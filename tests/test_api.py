"""API layer: the freeze must be provably closed, and the view must never carry truth."""

from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from api.session import Session


def _run_to(s: Session, t: int, answer_freezes: bool = True) -> None:
    """Advance to t.

    A freeze stops the clock, so it has to be answered to get past it — which is
    the point of a freeze, and the reason this helper exists at all.
    """
    guard = 0
    while s.world.t < t and not s.finished:
        if s.freeze is not None:
            if not answer_freezes:
                return
            s.answer_probe(choice="C", text="-", confidence=3)
            s.answer_isa(3)
        s.tick()
        guard += 1
        assert guard < 10000, f"the clock is not advancing (stuck at {s.world.t})"


def test_the_view_never_contains_opposing_force_truth():
    """The client cannot render what it is never sent (ADR-001)."""
    s = Session(participant="t1", scenario_id="fin-def-03")
    _run_to(s, 1500)
    v = s.view()
    assert set(v["own"]) == {"blue_1pl", "blue_2pl", "blue_drone_a"}
    for b in v["beliefs"]:
        assert b["age_s"] >= 0 and b["uncertainty_m"] > 0
    blob = repr(v)
    assert "red_coy_x" not in v["own"]
    # Whatever red appears in the view arrives as a belief with an age, never a
    # position without one.
    for b in v["beliefs"]:
        assert "age_s" in b and "uncertainty_m" in b
    assert "waypoint" not in blob and "strength=" not in blob


def test_the_channel_refuses_during_a_freeze_and_the_clock_stops():
    s = Session(participant="t2", scenario_id="fin-def-03")
    _run_to(s, 1800, answer_freezes=False)
    assert s.freeze is not None, "the first probe should have opened a freeze"
    frozen_t = s.world.t

    r = s.ask("where is the enemy")
    assert r["refused"] is True

    for _ in range(10):
        s.tick()
    assert s.world.t == frozen_t, "the scenario clock must stop during a freeze"

    s.answer_probe(choice="C", text=None, confidence=3)
    s.answer_isa(4)
    assert s.freeze is None
    s.tick()
    assert s.world.t > frozen_t

    types = [r["type"] for r in s.log.rows]
    for needed in ("freeze_start", "screen_blanked", "probe_shown", "probe_answer",
                   "confidence", "isa_load", "freeze_end"):
        assert needed in types, f"{needed} was not logged"

    refusals = [r for r in s.log.rows if r["type"] == "query" and r.get("refused")]
    assert refusals, "a query refused during a freeze must still be logged"


def test_focus_loss_is_recorded_with_whether_it_happened_during_a_freeze():
    s = Session(participant="t3", scenario_id="fin-def-03")
    _run_to(s, 1800, answer_freezes=False)
    s.focus_lost("left_fullscreen")
    row = next(r for r in s.log.rows if r["type"] == "focus_lost")
    assert row["during_freeze"] is True


def test_asking_for_the_interpretation_suppresses_the_radio_fallback():
    s = Session(participant="t4", scenario_id="fin-def-03")
    _run_to(s, s.s.order.issued_t + 60)
    s.ask("what does the order mean for us")
    _run_to(s, s.s.order.fallback_at_t + 120)
    tags = [r.get("tag") for r in s.log.rows]
    assert "order_interpretation_fallback" not in tags
    routes = [r.get("guidance_route") for r in s.log.rows if r.get("guidance_route")]
    assert routes == ["query"]
