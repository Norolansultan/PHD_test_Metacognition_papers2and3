"""Engagement: deterministic, symmetric, and confined to the presentation of truth."""

from __future__ import annotations

import os
import sys
from random import Random

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from engine.combat import resolve
from engine.scenario import load
from engine.tick import advance


def _run(seed_offset: int = 0):
    s = load("scenarios/fin-def-03.yaml", root=".")
    rng = Random(s.seed + seed_offset)
    w = s.initial
    engagements, destroyed = 0, []
    while w.t < s.duration_s:
        tr = advance(w, rng, s.weather_changes)
        w = tr.state
        engagements += len(tr.engagements)
        destroyed += tr.destroyed
    return w, engagements, destroyed


def test_the_situation_actually_develops():
    """A picture that never changes cannot be portrayed by a white cell."""
    w, engagements, _ = _run()
    assert engagements > 50, f"only {engagements} firing events in a 90 minute session"
    weakened = [e for e in w.entities.values() if e.strength < 0.95 and e.kind != "drone"]
    assert len(weakened) >= 3, "nothing took losses"


def test_nobody_is_annihilated_before_the_decision_point():
    """Attrition must leave the decision standing. The order arrives at 40 min."""
    s = load("scenarios/fin-def-03.yaml", root=".")
    rng = Random(s.seed)
    w = s.initial
    while w.t < s.order.issued_t:
        w = advance(w, rng, s.weather_changes).state
    for e in w.entities.values():
        if e.side == "blue":
            assert e.status != "destroyed", f"{e.id} was destroyed before the order arrived"
            assert e.strength > 0.4, f"{e.id} is at {e.strength:.2f} before the order arrived"


def test_engagement_is_deterministic():
    a = _run()
    b = _run()
    assert a[1] == b[1]
    assert {k: round(v.strength, 6) for k, v in a[0].entities.items()} == \
           {k: round(v.strength, 6) for k, v in b[0].entities.items()}


def test_fire_is_simultaneous_and_order_independent():
    """Damage is computed against the start-of-tick state, so iteration order
    cannot decide who wins."""
    s = load("scenarios/fin-def-03.yaml", root=".")
    rng = Random(s.seed)
    w = s.initial
    while w.t < 1500:
        w = advance(w, rng, s.weather_changes).state
    a, _ = resolve(w, Random(1))
    reversed_entities = dict(reversed(list(w.entities.items())))
    b, _ = resolve(w.__class__(**{**w.__dict__, "entities": reversed_entities}), Random(1))
    assert {k: round(v.strength, 6) for k, v in a.entities.items()} == \
           {k: round(v.strength, 6) for k, v in b.entities.items()}


def test_weather_changes_on_schedule():
    s = load("scenarios/fin-def-03.yaml", root=".")
    assert s.weather_changes, "a static sky is one more thing that reads as unreal"
    rng = Random(s.seed)
    w = s.initial
    seen = []
    while w.t < s.duration_s:
        tr = advance(w, rng, s.weather_changes)
        w = tr.state
        if tr.weather_changed:
            seen.append((w.t, w.weather.precipitation))
    assert len(seen) == len(s.weather_changes)
