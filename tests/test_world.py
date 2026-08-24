"""World invariants."""

from __future__ import annotations

import os
import sys
from random import Random

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from engine.scenario import load
from engine.world import step


def test_no_entity_ever_stands_in_impassable_terrain():
    s = load("scenarios/fin-def-03.yaml", root=".")
    rng = Random(s.seed)
    world = s.initial
    while world.t < s.duration_s:
        world = step(world, rng)
        for e in world.entities.values():
            if e.endurance_s is not None:
                continue  # air platforms overfly water
            assert world.terrain.at(e.pos) != "water", (
                f"{e.id} is in the lake at t={world.t}"
            )


def test_state_is_immutable_between_steps():
    s = load("scenarios/fin-def-03.yaml", root=".")
    rng = Random(s.seed)
    before = s.initial
    positions = {k: v.pos for k, v in before.entities.items()}
    after = step(before, rng)
    assert {k: v.pos for k, v in before.entities.items()} == positions
    assert after is not before


def test_units_move_at_different_speeds_by_kind():
    """A mech company and an infantry platoon do not cover ground alike."""
    from engine.world import MOBILITY

    assert MOBILITY["infantry_platoon"] < MOBILITY["mech_company"]
