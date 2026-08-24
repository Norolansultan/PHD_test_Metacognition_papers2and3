"""A session must be reproducible from its log alone."""

from __future__ import annotations

import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from harness.replay import replay
from harness.run import run

SCENARIO = "scenarios/fin-def-03.yaml"


def _events(path):
    return [json.loads(line) for line in open(path, encoding="utf-8") if line.strip()]


def _comparable(rows):
    """Everything except the decision's optional world-move payload, which the
    log records as taken rather than as an instruction."""
    return [
        {k: v for k, v in r.items() if k != "seq"}
        for r in rows
        if r["type"] not in ("world_tick",)
    ]


def test_replay_reproduces_the_session(tmp_path):
    original = str(tmp_path / "orig.jsonl")
    again = str(tmp_path / "replay.jsonl")
    run(SCENARIO, "harness/participants/synth_01.yaml", original)
    replay(original, again)
    assert _comparable(_events(original)) == _comparable(_events(again))


def test_replay_of_the_non_asking_participant(tmp_path):
    original = str(tmp_path / "orig2.jsonl")
    again = str(tmp_path / "replay2.jsonl")
    run(SCENARIO, "harness/participants/synth_02_no_ask.yaml", original)
    replay(original, again)
    assert _comparable(_events(original)) == _comparable(_events(again))
