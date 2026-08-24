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

MAX_ROUTE_S = 5400           # a route must be completable inside the session
MIN_RISK_DIFFERENCE = 0.20   # the two routes must differ in risk


def _routes():
    s = load("scenarios/fin-def-03.yaml", root=".")
    w = whatif_route(s.initial, "blue_1pl", ROUTE_WEST)
    e = whatif_route(s.initial, "blue_1pl", ROUTE_EAST)
    return w, e


def test_both_routes_fit_inside_the_session():
    w, e = _routes()
    assert w.reachable and e.reachable
    for name, o in (("west", w), ("east", e)):
        assert o.eta_s <= MAX_ROUTE_S, (
            f"{name} route takes {o.eta_s // 60} min, longer than the {MAX_ROUTE_S // 60} "
            "minute session: a decision the participant cannot execute is not a decision"
        )


def test_neither_route_dominates_the_other():
    """The branch is forced by a trade-off, not by symmetry.

    An earlier version required the two routes to cost the same. That is one way
    to force the choice, but a weaker one: it makes the corridors interchangeable
    and the decision arbitrary. Requiring that the faster route is also the more
    exposed one is the stronger criterion, because it is the trade-off a commander
    actually faces, and it cannot be resolved without knowing the risk.
    """
    w, e = _routes()
    faster = "west" if w.eta_s < e.eta_s else "east"
    safer = "west" if w.exposed_fraction < e.exposed_fraction else "east"
    assert faster != safer, (
        f"the {faster} route is both faster and safer: it dominates, so the "
        "branch is choosable without asking anything"
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
