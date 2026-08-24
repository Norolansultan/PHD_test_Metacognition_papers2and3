"""Build the self-contained session viewer.

Demo mode as specified in docs/implementation/environment.md: the debug panel
shows the active condition, what the model computed, which injection is live, and
which observations the answer was built from. Without that panel a demonstration
shows one arbitrary condition and tells the viewer nothing.

The page is a viewer over real harness logs, not a second implementation of the
engine. Everything it displays was produced by engine/ under pytest.
"""

from __future__ import annotations

import base64
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from engine.query import ROUTE_EAST, ROUTE_WEST
from engine.scenario import load

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def collect() -> dict:
    s = load(os.path.join(ROOT, "scenarios/fin-def-03.yaml"), root=ROOT)
    with open(os.path.join(ROOT, "scenarios/terrain/valley_a.png"), "rb") as fh:
        png = base64.b64encode(fh.read()).decode("ascii")
    sessions = {}
    for name, path in (
        ("p117 — asks for an interpretation", "logs/synth_01.jsonl"),
        ("p118 — never asks, met by radio fallback", "logs/synth_02.jsonl"),
    ):
        rows = [
            json.loads(line)
            for line in open(os.path.join(ROOT, path), encoding="utf-8")
            if line.strip()
        ]
        sessions[name] = rows
    return {
        "terrain_png": png,
        "cell_m": s.initial.terrain.cell_m,
        "legend": s.initial.terrain.legend,
        "duration_s": s.duration_s,
        "scenario": s.id,
        "echelon": s.echelon,
        "order": {"t": s.order.issued_t, "text": s.order.text,
                  "fallback_t": s.order.fallback_at_t},
        "routes": {"west": ROUTE_WEST, "east": ROUTE_EAST},
        "sessions": sessions,
    }


if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, "logs", "viewer-data.json")
    data = collect()
    with open(out, "w", encoding="utf-8") as fh:
        json.dump(data, fh, separators=(",", ":"))
    print(f"wrote {out} ({os.path.getsize(out) // 1024} KB)")
