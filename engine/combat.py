"""Deterministic engagement and attrition.

The reference the supervisors gave is a constructive simulation in which the
situation changes continuously: units close, fire, take losses, and disappear.
A scripted world with units sliding along waypoints does not read as real to a
practitioner, and the white cell cannot portray a situation that never develops.

Everything here is deterministic. Damage is a closed-form function of range,
firepower and cover; the seeded generator is passed explicitly and used only for
the small dispersion that keeps identical pairings from producing identical
outcomes (ADR-003).
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from random import Random

from engine.belief import line_of_sight
from engine.world import Entity, WorldState, distance

# Weapon reach and effect by kind. PLANNING PLACEHOLDERS until the expert
# validation gate (build order step 5).
WEAPON = {
    "infantry_platoon": {"range_m": 900.0, "power": 0.0040},
    "mech_company": {"range_m": 2200.0, "power": 0.0110},
    "recon_troop": {"range_m": 1400.0, "power": 0.0050},
    "drone": {"range_m": 0.0, "power": 0.0},
}
COVER_FACTOR = {"forest": 0.35, "urban": 0.45, "track": 0.8, "road": 1.0,
                "open": 1.0, "water": 1.0}
# Attrition is calibrated so that a unit left in contact for the whole session is
# worn down but not annihilated: the participant's decision must still exist at
# the decision point. PLANNING PLACEHOLDER until the expert gate.
DESTROYED_AT = 0.12


@dataclass(frozen=True)
class Engagement:
    """One firing relationship in one tick. The white cell draws these."""

    shooter: str
    target: str
    range_m: float
    damage: float


def _effect(shooter: Entity, target: Entity, state: WorldState, rng: Random) -> float:
    w = WEAPON.get(shooter.kind)
    if not w or w["range_m"] <= 0.0:
        return 0.0
    d = distance(shooter.pos, target.pos)
    if d > w["range_m"]:
        return 0.0
    if not line_of_sight(state, shooter.pos, target.pos):
        return 0.0
    # Effect falls off with range and is reduced by the target's cover.
    falloff = 1.0 - (d / w["range_m"]) ** 2
    cover = COVER_FACTOR.get(state.terrain.at(target.pos), 1.0)
    dispersion = 0.85 + 0.30 * rng.random()
    return w["power"] * falloff * cover * shooter.strength * dispersion


def resolve(state: WorldState, rng: Random) -> tuple[WorldState, list[Engagement]]:
    """Resolve one tick of contact. Returns the new state and what happened.

    Both sides fire simultaneously: damage is computed against the state at the
    start of the tick, so the order units are iterated in cannot change the
    result.
    """
    live = {k: v for k, v in state.entities.items() if v.status != "destroyed"}
    damage: dict[str, float] = {k: 0.0 for k in live}
    engagements: list[Engagement] = []

    for sid in sorted(live):
        shooter = live[sid]
        for tid in sorted(live):
            target = live[tid]
            if target.side == shooter.side or target.side == "neutral":
                continue
            dmg = _effect(shooter, target, state, rng)
            if dmg <= 0.0:
                continue
            damage[tid] += dmg
            engagements.append(
                Engagement(sid, tid, round(distance(shooter.pos, target.pos), 1),
                           round(dmg, 4))
            )

    if not engagements:
        return state, []

    ents = dict(state.entities)
    for eid, dmg in damage.items():
        if dmg <= 0.0:
            continue
        e = ents[eid]
        strength = max(0.0, e.strength - dmg)
        if strength <= DESTROYED_AT:
            ents[eid] = replace(e, strength=0.0, status="destroyed", speed=0.0,
                                waypoint=None, route=())
        else:
            ents[eid] = replace(e, strength=strength,
                                status="engaged" if e.status != "blocked" else e.status)
    return replace(state, entities=ents), engagements
