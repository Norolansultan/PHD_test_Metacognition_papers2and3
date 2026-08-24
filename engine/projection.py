"""What-if projection.

The hard rule (ADR-001, reconciliation X-01): world state is used for terrain,
physics, and own-side entities only. Every non-own entity enters a projection
through a ProjectionInput built from BeliefState, carrying the estimate and its
uncertainty. tests/test_omniscience.py enforces it.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from random import Random

from engine.belief import BeliefState
from engine.world import Entity, WorldState, distance, step, terrain_speed


@dataclass(frozen=True)
class ProjectionInput:
    """A non-own entity as the organisation believes it to be."""

    subject: str
    pos: tuple[float, float] | None
    uncertainty_m: float
    age_s: int
    kind: str
    speed_assumption: float  # m/s, the planning assumption for this kind


@dataclass(frozen=True)
class ProjectionOutcome:
    horizon_s: int
    subject: str | None
    predicted_pos: tuple[float, float] | None
    predicted_uncertainty_m: float | None
    eta_s: int | None
    reachable: bool | None
    exposed_fraction: float | None = None  # share of the route in open ground
    notes: tuple[str, ...] = ()


# Planning assumptions per kind, in m/s. Sourced parameters replace these at the
# expert-validation gate (build order step 5).
SPEED_ASSUMPTION = {
    "mech_company": 2.5,
    "infantry_platoon": 1.0,
    "drone": 25.0,
}


def belief_input(
    belief: BeliefState, subject: str, t_now: int, param_override: dict | None = None
) -> ProjectionInput | None:
    est = belief.best_estimate(subject, t_now)
    if est is None:
        return None
    kind = str(est.attrs.get("kind", "mech_company"))
    speed = SPEED_ASSUMPTION.get(kind, 5.0)
    if param_override and "red_speed" in param_override:
        speed = speed * float(param_override["red_speed"])
    return ProjectionInput(
        subject=subject,
        pos=est.pos,
        uncertainty_m=est.uncertainty_m,
        age_s=est.age_s,
        kind=kind,
        speed_assumption=speed,
    )


def project_subject(
    pi: ProjectionInput, toward: tuple[float, float], horizon_s: int
) -> ProjectionOutcome:
    """Straight-line advance of a believed entity toward a point."""
    if pi.pos is None:
        return ProjectionOutcome(horizon_s, pi.subject, None, None, None, None,
                                 ("no position in the record",))
    d = distance(pi.pos, toward)
    travelled = min(pi.speed_assumption * horizon_s, d)
    if d == 0:
        npos = pi.pos
    else:
        ux, uy = (toward[0] - pi.pos[0]) / d, (toward[1] - pi.pos[1]) / d
        npos = (pi.pos[0] + ux * travelled, pi.pos[1] + uy * travelled)
    eta = int(d / pi.speed_assumption) if pi.speed_assumption > 0 else None
    return ProjectionOutcome(
        horizon_s=horizon_s,
        subject=pi.subject,
        predicted_pos=npos,
        predicted_uncertainty_m=pi.uncertainty_m + 1.2 * horizon_s,
        eta_s=eta,
        reachable=travelled >= d,
    )


def whatif_move(
    state: WorldState, unit_id: str, target: tuple[float, float], horizon_s: int
) -> ProjectionOutcome:
    """Own-side move. Own units may be read from world state: the organisation
    knows where its own units are and what it ordered them to do."""
    e = state.entities[unit_id]
    if e.side != "blue":
        raise ValueError("whatif_move is for own-side units only")
    sim = replace(state, entities={unit_id: replace(e, waypoint=target, status="moving")})
    rng = Random(state.seed)
    t_end = state.t + horizon_s
    arrived_at: int | None = None
    while sim.t < t_end:
        sim = step(sim, rng)
        if arrived_at is None and distance(sim.entities[unit_id].pos, target) <= 1.0:
            arrived_at = sim.t - state.t
            break
    moved = sim.entities[unit_id]
    d_remaining = distance(moved.pos, target)
    if arrived_at is None:
        # Not there yet: extrapolate the remaining leg at the local speed.
        v = terrain_speed(e, state.terrain, moved.pos)
        eta = None if v <= 0 else int(horizon_s + d_remaining / v)
    else:
        eta = arrived_at
    return ProjectionOutcome(
        horizon_s=horizon_s,
        subject=unit_id,
        predicted_pos=moved.pos,
        predicted_uncertainty_m=0.0,
        eta_s=eta,
        reachable=arrived_at is not None,
    )


def whatif_route(
    state: WorldState, unit_id: str, waypoints: list[tuple[float, float]], cap_s: int = 14400
) -> ProjectionOutcome:
    """Run an own-side unit through a sequence of waypoints.

    Returns the time to complete the route and the fraction of it spent in open
    ground, which is the risk half of the route comparison. The cap exists so an
    unreachable route terminates rather than looping.
    """
    e = state.entities[unit_id]
    if e.side != "blue":
        raise ValueError("whatif_route is for own-side units only")
    sim = replace(state, entities={unit_id: replace(e, waypoint=waypoints[0], status="moving")})
    rng = Random(state.seed)
    leg = 0
    ticks = 0
    open_ticks = 0
    while sim.t - state.t < cap_s:
        sim = step(sim, rng)
        ticks += 1
        u = sim.entities[unit_id]
        if state.terrain.cover_fraction(u.pos) < 0.25:
            open_ticks += 1
        if distance(u.pos, waypoints[leg]) <= 1.0:
            leg += 1
            if leg >= len(waypoints):
                break
            sim = replace(
                sim,
                entities={unit_id: replace(sim.entities[unit_id],
                                           waypoint=waypoints[leg], status="moving")},
            )
    done = leg >= len(waypoints)
    return ProjectionOutcome(
        horizon_s=sim.t - state.t,
        subject=unit_id,
        predicted_pos=sim.entities[unit_id].pos,
        predicted_uncertainty_m=0.0,
        eta_s=(sim.t - state.t) if done else None,
        reachable=done,
        exposed_fraction=(open_ticks / ticks) if ticks else None,
    )
