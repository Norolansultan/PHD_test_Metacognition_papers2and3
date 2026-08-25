"""Layer 2 behaviour: observations are records, ageing is explicit, forest blocks sight."""

from __future__ import annotations

import os
import sys
from random import Random

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from engine.belief import DRIFT_RATE_M_PER_S, BeliefState, Observation, Sensor, sense
from engine.scenario import load
from engine.world import step


def _obs(t: int, err: float = 50.0) -> Observation:
    return Observation(f"o{t}", "blue_drone_a", "red_coy_x", t, (1000.0, 1000.0), err,
                       {"kind": "mech_company"}, 0.9, "drone_feed")


def test_uncertainty_grows_with_age():
    b = BeliefState([_obs(300)])
    fresh = b.best_estimate("red_coy_x", 300)
    old = b.best_estimate("red_coy_x", 900)
    assert fresh.uncertainty_m == 50.0
    assert old.uncertainty_m == 50.0 + DRIFT_RATE_M_PER_S * 600
    assert old.age_s == 600


def test_newer_observation_supersedes_by_existing():
    b = BeliefState([_obs(300), _obs(900, err=200.0)])
    est = b.best_estimate("red_coy_x", 1200)
    assert est.age_s == 300 and est.uncertainty_m == 200.0 + DRIFT_RATE_M_PER_S * 300


def test_nothing_is_known_before_it_was_observed():
    b = BeliefState([_obs(900)])
    assert b.best_estimate("red_coy_x", 600) is None


def test_a_landed_platform_stops_producing_observations():
    s = load("scenarios/fin-def-03.yaml", root=".")
    rng = Random(s.seed)
    world = s.initial
    counts = {"airborne": 0, "landed": 0}
    seq = 0
    while world.t < s.duration_s:
        drone = world.entities["blue_drone_a"]
        made = sense(world, [x for x in s.sensors if x.entity == "blue_drone_a"], rng, seq)
        seq += len(made)
        counts["airborne" if drone.endurance_s else "landed"] += len(made)
        world = step(world, rng)
    assert counts["airborne"] > 0
    assert counts["landed"] == 0
