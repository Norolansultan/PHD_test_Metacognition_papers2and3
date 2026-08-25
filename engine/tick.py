"""One advance of the world: movement, contact, weather.

The harness and the API both drive the same function, so the run a scripted
participant produces and the run a live participant produces cannot diverge.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from random import Random

from engine.combat import Engagement, resolve
from engine.world import TICK_S, WorldState, step


@dataclass(frozen=True)
class TickResult:
    state: WorldState
    engagements: list[Engagement]
    weather_changed: bool
    destroyed: list[str]


def advance(state: WorldState, rng: Random, weather_changes: list, dt: int = TICK_S) -> TickResult:
    before = {k: v.status for k, v in state.entities.items()}
    s = step(state, rng, dt)

    changed = False
    for wc in weather_changes:
        if wc.t == s.t:
            s = replace(s, weather=wc.weather)
            changed = True

    s, engagements = resolve(s, rng)
    destroyed = [k for k, v in s.entities.items()
                 if v.status == "destroyed" and before.get(k) != "destroyed"]
    return TickResult(s, engagements, changed, destroyed)
