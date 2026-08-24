"""The experimental-design gate (ADR-010, docs/scenarios V-09).

Checked before the realism gate. Where they conflict, this one wins and the
deviation is reported.
"""

from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from engine.projection import whatif_route
from engine.query import ROUTE_EAST, ROUTE_WEST
from engine.scenario import load

MAX_TIME_DIFFERENCE = 0.35   # routes must be comparable in cost
MIN_RISK_DIFFERENCE = 0.20   # and must differ in risk


def _routes():
    s = load("scenarios/fin-def-03.yaml", root=".")
    w = whatif_route(s.initial, "blue_1pl", ROUTE_WEST)
    e = whatif_route(s.initial, "blue_1pl", ROUTE_EAST)
    return w, e


def test_the_branch_is_forced_neither_route_is_cheaper():
    w, e = _routes()
    assert w.reachable and e.reachable
    diff = abs(w.eta_s - e.eta_s) / max(w.eta_s, e.eta_s)
    assert diff <= MAX_TIME_DIFFERENCE, (
        f"routes differ by {diff:.0%} in time: the branch is choosable on cost alone"
    )


def test_the_two_routes_differ_in_risk():
    w, e = _routes()
    diff = abs(w.exposed_fraction - e.exposed_fraction)
    assert diff >= MIN_RISK_DIFFERENCE, (
        f"routes differ by only {diff:.0%} in exposure: the choice carries no risk trade-off"
    )


def test_visibility_shadows_exist():
    """Ground observation must be blocked somewhere, or nothing is unobservable."""
    s = load("scenarios/fin-def-03.yaml", root=".")
    t = s.initial.terrain
    forest = sum(
        1
        for row in t.cells
        for c in row
        if t.legend[c] == "forest"
    )
    total = len(t.cells) * len(t.cells[0])
    assert 0.10 <= forest / total <= 0.50, f"forest cover {forest / total:.0%} is implausible"


def test_the_map_is_large_enough_for_time_to_cost_something():
    s = load("scenarios/fin-def-03.yaml", root=".")
    assert s.initial.terrain.width_m >= 5000
