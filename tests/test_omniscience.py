"""ADR-001 / reconciliation X-01.

Perturb opposing-force truth without touching a single observation. Every answer
about that force must be unchanged. If this test fails, the AI channel has become
omniscient and the study measures nothing.
"""

from __future__ import annotations

import os
import sys
from dataclasses import replace
from random import Random

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from engine.belief import BeliefState, sense
from engine.errors import Injector
from engine.intents import IntentParser
from engine.query import ConditionConfig, QueryEngine
from engine.scenario import load
from engine.world import step

QUERIES = [
    "where is the enemy",
    "what is the enemy strength",
    "where will the enemy be in 30 minutes",
    "how long until the enemy reaches kelo",
]


def _build(scenario, move_red_by: float):
    rng = Random(scenario.seed)
    belief = BeliefState()
    world = scenario.initial
    seq = 0
    for _ in range(20):
        for o in sense(world, scenario.sensors, rng, seq):
            seq += 1
            belief.add(o)
        world = step(world, rng)
    if move_red_by:
        red = world.entities["red_coy_x"]
        ents = dict(world.entities)
        ents["red_coy_x"] = replace(
            red, pos=(red.pos[0] + move_red_by, red.pos[1] + move_red_by)
        )
        world = replace(world, entities=ents)
    return world, belief


def test_perturbing_red_truth_does_not_change_any_answer():
    s = load("scenarios/fin-def-03.yaml", root=".")
    cfg = ConditionConfig()
    baseline_world, baseline_belief = _build(s, 0.0)
    moved_world, moved_belief = _build(s, 3000.0)

    # The observations must be identical: we perturbed truth after sensing.
    assert len(baseline_belief.observations) == len(moved_belief.observations)

    qe_a = QueryEngine(IntentParser(), Injector(s.injections),
                       s.order.true_reading, s.order.distorted_readings)
    qe_b = QueryEngine(IntentParser(), Injector(s.injections),
                       s.order.true_reading, s.order.distorted_readings)
    for q in QUERIES:
        a = qe_a.answer(q, baseline_belief, baseline_world, cfg)
        b = qe_b.answer(q, moved_belief, moved_world, cfg)
        assert a.text == b.text, f"answer to {q!r} changed when red truth moved"
