"""Layer 2 — organisational knowledge.

What blue knows, built from timestamped observations and never from truth
(ADR-001). This is the layer the AI channel and the frontend read.

Observations are records of a moment. They are never updated: a sighting at
T+300 stays what it was, and at T+900 it is ten minutes old.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from random import Random

from engine.world import WorldState, distance

DRIFT_RATE_M_PER_S = 1.2  # how fast an estimate decays without a fresh observation


@dataclass(frozen=True)
class Observation:
    id: str
    observer: str
    subject: str
    t_observed: int
    pos: tuple[float, float] | None
    pos_error: float  # metres, sensor accuracy
    attrs: dict
    confidence: float
    channel: str  # "drone_feed" | "radio_report" | "sigint" | "peer_report"


@dataclass(frozen=True)
class Estimate:
    subject: str
    pos: tuple[float, float] | None
    uncertainty_m: float
    age_s: int
    source: str
    channel: str
    confidence: float
    attrs: dict


@dataclass(frozen=True)
class Sensor:
    entity: str
    range_m: float
    pos_error_m: float
    interval_s: int


class BeliefState:
    """The organisation's picture. Append-only."""

    def __init__(self, observations: list[Observation] | None = None) -> None:
        self.observations: list[Observation] = list(observations or [])

    def add(self, obs: Observation) -> None:
        self.observations.append(obs)

    def for_subject(self, subject: str) -> list[Observation]:
        return [o for o in self.observations if o.subject == subject]

    def best_estimate(self, subject: str, t_now: int) -> Estimate | None:
        """Freshest observation, with uncertainty grown by its age.

        uncertainty = pos_error + drift_rate * age
        """
        obs = [o for o in self.observations if o.subject == subject and o.t_observed <= t_now]
        if not obs:
            return None
        o = max(obs, key=lambda x: (x.t_observed, x.id))
        age = t_now - o.t_observed
        return Estimate(
            subject=subject,
            pos=o.pos,
            uncertainty_m=o.pos_error + DRIFT_RATE_M_PER_S * age,
            age_s=age,
            source=o.observer,
            channel=o.channel,
            confidence=o.confidence,
            attrs=dict(o.attrs),
        )

    def known_subjects(self, t_now: int) -> list[str]:
        return sorted({o.subject for o in self.observations if o.t_observed <= t_now})


def line_of_sight(state: WorldState, a: tuple[float, float], b: tuple[float, float]) -> bool:
    """Forest blocks ground observation. Sampled along the segment."""
    d = distance(a, b)
    if d == 0:
        return True
    samples = max(2, int(d / (state.terrain.cell_m / 2)))
    for i in range(1, samples):
        f = i / samples
        p = (a[0] + (b[0] - a[0]) * f, a[1] + (b[1] - a[1]) * f)
        if state.terrain.at(p) == "forest":
            return False
    return True


def sense(
    state: WorldState, sensors: list[Sensor], rng: Random, seq: int
) -> list[Observation]:
    """Generate the observations this tick's sensors are entitled to make.

    Observations fall out of the simulation rather than being hand-authored
    (reconciliation D-05). A region no sensor covers stays empty by construction.
    """
    out: list[Observation] = []
    for s in sorted(sensors, key=lambda x: x.entity):
        if state.t % s.interval_s != 0:
            continue
        observer = state.entities.get(s.entity)
        if observer is None or observer.status == "destroyed":
            continue
        airborne = observer.endurance_s is not None
        if airborne and observer.endurance_s == 0:
            continue  # landed: no new observations, and uncertainty grows on its own
        for sid in sorted(state.entities):
            subject = state.entities[sid]
            if subject.id == observer.id or subject.side == observer.side:
                continue
            d = distance(observer.pos, subject.pos)
            if d > s.range_m:
                continue
            if not airborne and not line_of_sight(state, observer.pos, subject.pos):
                continue
            err = s.pos_error_m
            jx = rng.gauss(0.0, err / 2.0)
            jy = rng.gauss(0.0, err / 2.0)
            seq += 1
            out.append(
                Observation(
                    id=f"o{seq:05d}",
                    observer=observer.id,
                    subject=subject.id,
                    t_observed=state.t,
                    pos=(subject.pos[0] + jx, subject.pos[1] + jy),
                    pos_error=err,
                    attrs={"kind": subject.kind, "strength": round(subject.strength, 2)},
                    confidence=0.9 if airborne else 0.7,
                    channel="drone_feed" if airborne else "radio_report",
                )
            )
    return out
