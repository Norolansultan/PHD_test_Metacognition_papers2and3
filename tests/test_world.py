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


def test_a_unit_can_be_ordered_along_a_corridor():
    """A single waypoint runs into the lake; a corridor has to be a route.

    Without this, neither branch of the forced choice is executable, and the
    decision the study measures cannot be carried out.
    """
    from engine.world import with_route

    s = load("scenarios/fin-def-03.yaml", root=".")
    rng = Random(s.seed)
    west = [(2850.0, 3050.0), (2850.0, 7550.0), (4150.0, 7550.0)]
    world = with_route(s.initial, "blue_1pl", west)
    while world.t < s.duration_s:
        world = step(world, rng)
        assert world.entities["blue_1pl"].status != "blocked"
    end = world.entities["blue_1pl"].pos
    assert abs(end[0] - 4150.0) < 60 and abs(end[1] - 7550.0) < 60, (
        f"the platoon did not reach KELO by the western corridor: {end}"
    )
