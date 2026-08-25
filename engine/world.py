"""Layer 1 — world truth.

Only the engine's step() and the researcher's tooling read this. Never the query
path's answer for a non-own entity, never the frontend (ADR-001).

State is immutable: step(state) returns a new state, which makes a what-if a copy
run forward with no risk to the live run (ADR-003).
"""

from __future__ import annotations

import math
from dataclasses import dataclass, replace
from random import Random

from engine.terrain import TerrainGrid

TICK_S = 30  # scenario seconds per step

# Movement speed in m/s by terrain class, for a ground unit.
SPEED_BY_TERRAIN = {
    "road": 11.0,
    "track": 4.5,
    "open": 4.0,
    "urban": 3.0,
    "forest": 1.6,
    "water": 0.0,
}
AIR_SPEED = 25.0

# Mobility multiplier by kind. PLACEHOLDER values: these are planning assumptions
# until the expert-validation gate (build order step 5) replaces them with figures
# derived from CMO runs.
MOBILITY = {
    "infantry_platoon": 0.30,
    "mech_company": 0.55,
    "recon_troop": 0.80,
}

# A unit in contact does not move at march speed. This is what makes a covering
# force worth something, and it is why the picture keeps developing instead of
# resolving in the first ten minutes.
CONTACT_SPEED_FACTOR = 0.22


@dataclass(frozen=True)
class Entity:
    id: str
    side: str  # "blue" | "red" | "neutral"
    kind: str  # "infantry_platoon" | "drone" | "mech_company" | ...
    pos: tuple[float, float]
    heading: float = 0.0
    speed: float = 0.0
    strength: float = 1.0
    supply: float = 1.0
    status: str = "static"  # "moving" | "engaged" | "static" | "destroyed"
    waypoint: tuple[float, float] | None = None
    route: tuple[tuple[float, float], ...] = ()  # legs still to run after waypoint
    endurance_s: int | None = None  # air only; None means not an air platform


@dataclass(frozen=True)
class Weather:
    wind_dir_deg: float = 0.0
    wind_ms: float = 3.0
    visibility_m: float = 8000.0
    temp_c: float = 4.0
    precipitation: str = "none"  # "none" | "rain" | "snow"

    def label(self) -> str:
        sky = {"none": "clear", "rain": "rain", "snow": "snow"}[self.precipitation]
        return (f"{sky} · {self.temp_c:.0f} °C · wind {self.wind_ms:.0f} m/s "
                f"from {self.wind_dir_deg:.0f}°")


@dataclass(frozen=True)
class WorldState:
    t: int  # scenario time, seconds
    entities: dict[str, Entity]
    terrain: TerrainGrid
    weather: Weather
    seed: int


def distance(a: tuple[float, float], b: tuple[float, float]) -> float:
    return math.hypot(b[0] - a[0], b[1] - a[1])


def terrain_speed(entity: Entity, terrain: TerrainGrid, pos: tuple[float, float]) -> float:
    if entity.endurance_s is not None:
        return AIR_SPEED
    return SPEED_BY_TERRAIN[terrain.at(pos)] * MOBILITY.get(entity.kind, 1.0)


def _advance(e: Entity, terrain: TerrainGrid, dt: int) -> Entity:
    """Move one entity toward its waypoint. Pure, deterministic."""
    if e.status == "destroyed" or e.waypoint is None:
        return e
    d = distance(e.pos, e.waypoint)
    if d < 1.0:
        # Leg complete. Take the next one, or stop.
        if e.route:
            return replace(e, waypoint=e.route[0], route=e.route[1:], status="moving")
        return replace(e, waypoint=None, status="static", speed=0.0)
    v = terrain_speed(e, terrain, e.pos)
    if e.status == "engaged":
        v *= CONTACT_SPEED_FACTOR
    if v <= 0.0:
        # Standing in impassable terrain: hold rather than swim.
        return replace(e, status="blocked", speed=0.0)
    stepd = min(v * dt, d)
    if stepd <= 0.0:
        return replace(e, speed=0.0)
    ux = (e.waypoint[0] - e.pos[0]) / d
    uy = (e.waypoint[1] - e.pos[1]) / d
    npos = (e.pos[0] + ux * stepd, e.pos[1] + uy * stepd)
    if terrain_speed(e, terrain, npos) <= 0.0:
        # The next step would enter impassable ground. Hold at the edge: a unit
        # does not walk into a lake, and routing around it is the commander's
        # problem, which is exactly what the branch point is for.
        return replace(e, status="blocked", speed=0.0)
    return replace(
        e,
        pos=npos,
        heading=math.degrees(math.atan2(ux, -uy)) % 360.0,
        speed=v,
        status="moving",
    )


def step(state: WorldState, rng: Random, dt: int = TICK_S) -> WorldState:
    """Advance the world by dt seconds and return a new state.

    rng is passed explicitly and is never the global random module (ADR-003).
    Entities are iterated in sorted key order so the result does not depend on
    dictionary insertion order.
    """
    ents: dict[str, Entity] = {}
    for eid in sorted(state.entities):
        e = state.entities[eid]
        e = _advance(e, state.terrain, dt)
        if e.endurance_s is not None and e.status != "destroyed":
            remaining = max(0, e.endurance_s - dt)
            e = replace(e, endurance_s=remaining)
            if remaining == 0 and e.status != "static":
                # Out of endurance: the platform lands and stops observing.
                e = replace(e, status="static", speed=0.0, waypoint=None)
        ents[eid] = e
    return WorldState(
        t=state.t + dt,
        entities=ents,
        terrain=state.terrain,
        weather=state.weather,
        seed=state.seed,
    )


def with_waypoint(state: WorldState, eid: str, wp: tuple[float, float]) -> WorldState:
    return with_route(state, eid, [wp])


def with_route(state: WorldState, eid: str, legs: list[tuple[float, float]]) -> WorldState:
    """Order a unit along a sequence of waypoints.

    A single waypoint is a straight line, and a straight line to the objective
    runs into the lake. A corridor is a route, so ordering one has to be a route
    as well, or neither branch is executable.
    """
    if not legs:
        return state
    e = state.entities[eid]
    ents = dict(state.entities)
    ents[eid] = replace(e, waypoint=tuple(legs[0]),
                        route=tuple(tuple(x) for x in legs[1:]), status="moving")
    return replace(state, entities=ents)
