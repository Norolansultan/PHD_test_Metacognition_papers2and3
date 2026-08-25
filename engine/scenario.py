"""Scenario loading. One YAML per scenario, no code (docs/scenarios)."""

from __future__ import annotations

import os
from dataclasses import dataclass

import yaml

from engine.belief import Observation, Sensor
from engine.errors import Injection
from engine.terrain import TerrainGrid
from engine.world import Entity, Weather, WorldState


@dataclass(frozen=True)
class RadioEvent:
    t: int
    sender: str
    text: str
    creates_observation: dict | None = None


@dataclass(frozen=True)
class ProbeRef:
    t: int
    ref: str
    open_l3: bool = False


@dataclass(frozen=True)
class Order:
    ref: str
    issued_t: int
    text: str
    true_reading: str
    distorted_readings: dict
    fallback_at_t: int
    required_by_order: str | None = None


@dataclass(frozen=True)
class WeatherChange:
    t: int
    weather: Weather


@dataclass(frozen=True)
class Scenario:
    id: str
    version: int
    seed: int
    duration_s: int
    domain: str
    echelon: str
    initial: WorldState
    sensors: list[Sensor]
    events: list[RadioEvent]
    probes: list[ProbeRef]
    injections: list[Injection]
    order: Order
    weather_changes: list[WeatherChange]


def _tuple(v) -> tuple[float, float]:
    return (float(v[0]), float(v[1]))


def load(path: str, root: str | None = None) -> Scenario:
    root = root or os.path.dirname(os.path.dirname(os.path.abspath(path)))
    with open(path, encoding="utf-8") as fh:
        d = yaml.safe_load(fh)

    terrain = TerrainGrid.load(
        os.path.join(root, d["terrain"]["file"]),
        float(d["terrain"]["cell_m"]),
        d["terrain"]["legend"],
    )
    ents: dict[str, Entity] = {}
    for e in d["entities"]:
        ents[e["id"]] = Entity(
            id=e["id"],
            side=e["side"],
            kind=e["kind"],
            pos=_tuple(e["pos"]),
            strength=float(e.get("strength", 1.0)),
            supply=float(e.get("supply", 1.0)),
            status="moving" if (e.get("waypoint") or e.get("route")) else "static",
            waypoint=(_tuple(e["waypoint"]) if e.get("waypoint")
                      else _tuple(e["route"][0]) if e.get("route") else None),
            route=(tuple(_tuple(p) for p in e["route"][1:]) if e.get("route") else ()),
            endurance_s=e.get("endurance_s"),
        )
    w = d.get("weather", {})
    def _weather(src: dict) -> Weather:
        return Weather(
            wind_dir_deg=float(src.get("wind_dir_deg", 0)),
            wind_ms=float(src.get("wind_ms", 3)),
            visibility_m=float(src.get("visibility_m", 8000)),
            temp_c=float(src.get("temp_c", 4)),
            precipitation=str(src.get("precipitation", "none")),
        )

    initial = WorldState(
        t=0, entities=ents, terrain=terrain, weather=_weather(w), seed=int(d["seed"]),
    )
    weather_changes = [WeatherChange(int(c["t"]), _weather(c))
                       for c in d.get("weather_changes", [])]
    sensors = [
        Sensor(s["entity"], float(s["range_m"]), float(s["pos_error_m"]), int(s["interval_s"]))
        for s in d.get("sensors", [])
    ]
    events = [
        RadioEvent(int(e["t"]), e.get("from", "unknown"), e.get("text", ""),
                   e.get("creates_observation"))
        for e in d.get("events", [])
        if e.get("type") == "radio_message"
    ]
    probes = [ProbeRef(int(p["t"]), p["ref"], bool(p.get("open_l3", False)))
              for p in d.get("probes", [])]
    injections = [
        Injection(
            id=i["id"], kind=i["type"], after_t=int(i["after_t"]),
            param=i.get("param"), factor=i.get("factor"),
            direction=i.get("direction"), magnitude=i.get("magnitude"),
        )
        for i in d.get("injections", [])
    ]
    o = d["order"]
    order = Order(
        ref=o["ref"], issued_t=int(o["issued_t"]), text=o["text"],
        true_reading=o["true_reading"].strip(),
        distorted_readings={k: v.strip() for k, v in (o.get("distorted_readings") or {}).items()},
        fallback_at_t=int(o.get("fallback_at_t", o["issued_t"] + 600)),
        required_by_order=o.get("required_by_order"),
    )
    return Scenario(
        id=d["id"], version=int(d["version"]), seed=int(d["seed"]),
        duration_s=int(d["duration_s"]), domain=d["domain"],
        echelon=d.get("echelon", "unspecified"), initial=initial, sensors=sensors,
        events=events, probes=probes, injections=injections, order=order,
        weather_changes=weather_changes,
    )


def observation_from_event(ev: RadioEvent, seq: int) -> Observation | None:
    co = ev.creates_observation
    if not co:
        return None
    return Observation(
        id=f"e{seq:05d}", observer=ev.sender, subject=co["subject"], t_observed=ev.t,
        pos=_tuple(co["pos"]) if co.get("pos") else None,
        pos_error=float(co.get("pos_error", 500)), attrs=co.get("attrs", {}),
        confidence=float(co.get("confidence", 0.6)), channel="radio_report",
    )
