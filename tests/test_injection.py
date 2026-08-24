"""Error injection is presentation-layer only, and the two kinds never co-occur."""

from __future__ import annotations

import os
import sys
from random import Random

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest

from engine.belief import BeliefState, sense
from engine.errors import Injection, Injector
from engine.intents import IntentParser
from engine.query import ConditionConfig, QueryEngine
from engine.scenario import load
from engine.world import step


def test_a_scenario_may_not_arm_both_kinds():
    with pytest.raises(ValueError):
        Injector([
            Injection("a", "projection_error", 0, param="red_speed", factor=0.6),
            Injection("b", "guidance_distortion", 0, direction="north"),
        ])


def test_distortion_changes_only_the_interpretation_not_the_world():
    s = load("scenarios/fin-def-03.yaml", root=".")
    rng = Random(s.seed)
    belief = BeliefState()
    world = s.initial
    seq = 0
    while world.t < s.order.issued_t + 120:
        for o in sense(world, s.sensors, rng, seq):
            seq += 1
            belief.add(o)
        world = step(world, rng)

    clean = QueryEngine(IntentParser(), Injector([]), s.order.true_reading,
                        s.order.distorted_readings)
    armed = QueryEngine(IntentParser(), Injector(s.injections), s.order.true_reading,
                        s.order.distorted_readings)
    cfg = ConditionConfig()

    a = clean.answer("what does the order mean for us", belief, world, cfg)
    b = armed.answer("what does the order mean for us", belief, world, cfg)
    assert a.injection_id is None and b.injection_id == "inj_gd_01"
    assert a.text != b.text

    # Everything that is not the interpretation is untouched.
    for q in ("where is the enemy", "what is the enemy strength"):
        assert clean.answer(q, belief, world, cfg).text == armed.answer(q, belief, world, cfg).text


def test_every_answer_carries_an_injection_field():
    s = load("scenarios/fin-def-03.yaml", root=".")
    qe = QueryEngine(IntentParser(), Injector(s.injections), s.order.true_reading,
                     s.order.distorted_readings)
    a = qe.answer("where is the enemy", BeliefState(), s.initial, ConditionConfig())
    assert hasattr(a, "injection_id")
