"""Reconciliation X-02: exposure must not depend on whether the participant asked.

A participant who never asks for an interpretation still meets it, through the
radio fallback, and the route is logged as a covariate.
"""

from __future__ import annotations

import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from harness.run import run

SCENARIO = "scenarios/fin-def-03.yaml"


def _rows(path):
    return [json.loads(line) for line in open(path, encoding="utf-8") if line.strip()]


def test_the_asker_is_exposed_by_query(tmp_path):
    out = str(tmp_path / "asker.jsonl")
    run(SCENARIO, "harness/participants/synth_01.yaml", out)
    routes = [r.get("guidance_route") for r in _rows(out) if r.get("guidance_route")]
    assert routes == ["query"]


def test_the_non_asker_is_exposed_by_radio_fallback(tmp_path):
    out = str(tmp_path / "silent.jsonl")
    run(SCENARIO, "harness/participants/synth_02_no_ask.yaml", out)
    rows = _rows(out)
    routes = [r.get("guidance_route") for r in rows if r.get("guidance_route")]
    assert routes == ["radio_fallback"]
    fb = next(r for r in rows if r.get("guidance_route") == "radio_fallback")
    assert fb["injection"] == "inj_gd_01", "the fallback must carry the distortion too"


def test_the_fallback_does_not_fire_for_someone_who_asked(tmp_path):
    out = str(tmp_path / "asker2.jsonl")
    run(SCENARIO, "harness/participants/synth_01.yaml", out)
    tags = [r.get("tag") for r in _rows(out)]
    assert "order_interpretation_fallback" not in tags
