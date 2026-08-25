"""The first test written (ADR-003): the same seed produces the same log, byte for byte."""

from __future__ import annotations

import hashlib
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from harness.run import run

SCENARIO = "scenarios/fin-def-03.yaml"
PARTICIPANT = "harness/participants/synth_01.yaml"


def _digest(path: str) -> str:
    with open(path, "rb") as fh:
        return hashlib.sha256(fh.read()).hexdigest()


def test_two_runs_are_byte_identical(tmp_path):
    a = str(tmp_path / "a.jsonl")
    b = str(tmp_path / "b.jsonl")
    run(SCENARIO, PARTICIPANT, a)
    run(SCENARIO, PARTICIPANT, b)
    assert _digest(a) == _digest(b)


def test_engine_never_reads_the_wall_clock():
    """A wall-clock read inside the engine breaks reproducibility silently."""
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    offenders = []
    for name in sorted(os.listdir(os.path.join(root, "engine"))):
        if not name.endswith(".py"):
            continue
        src = open(os.path.join(root, "engine", name), encoding="utf-8").read()
        for needle in ("datetime.now", "time.time(", "random.random(", "random.seed("):
            if needle in src:
                offenders.append(f"{name}: {needle}")
    assert offenders == [], offenders
