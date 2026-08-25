"""Bake the white-cell display into a page that needs no server.

Runs a real session and records the control view every tick, then writes a
standalone HTML with the same CSS and the same rendering code the live display
uses. Nothing is re-implemented: the transport is swapped, the display is not.
"""

from __future__ import annotations

import base64
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from api.session import Session
from engine import scenario as scen
from engine.query import KELO, ROUTE_EAST, ROUTE_WEST

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# A scripted participant, so the log the white cell reads has a participant in it.
SCRIPT = [
    (600, "query", "where is the enemy"),
    (1320, "query", "what is the enemy strength"),
    (2160, "query", "where will the enemy be in 30 minutes"),
    (2520, "query", "what does the order mean for us"),
    (2880, "query", "compare the two routes"),
    (3000, "decide", None),
]


def build() -> dict:
    s = Session(participant="wc_demo", scenario_id="fin-def-03")
    sc = scen.load(os.path.join(ROOT, "scenarios/fin-def-03.yaml"), root=ROOT)
    with open(os.path.join(ROOT, "scenarios/terrain/valley_a.png"), "rb") as fh:
        png = base64.b64encode(fh.read()).decode("ascii")

    frames = [s.truth_view()]
    script = list(SCRIPT)
    while not s.finished:
        if s.freeze is not None:
            s.answer_probe(choice="C", text="Enemy continues west; the corridor is contested.",
                           confidence=3)
            s.answer_isa(4)
        while script and script[0][0] <= s.world.t:
            t, kind, arg = script.pop(0)
            if kind == "query":
                s.ask(arg)
            else:
                s.decide("move_west", "blue_1pl",
                         [[2850, 3050], [2850, 7550], [4150, 7550]])
        s.tick()
        frames.append(s.truth_view())

    return {
        "meta": {
            "terrain_png": png,
            "cell_m": sc.initial.terrain.cell_m,
            "legend": sc.initial.terrain.legend,
            "width_m": sc.initial.terrain.width_m,
            "duration_s": sc.duration_s,
            "routes": {"west": [list(p) for p in ROUTE_WEST],
                       "east": [list(p) for p in ROUTE_EAST]},
            "objective": list(KELO),
            "junction": [4150.0, 3050.0],
        },
        "frames": frames,
    }


def main() -> None:
    out = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, "logs", "white-cell.html")
    data = build()
    css = open(os.path.join(ROOT, "web", "control.css"), encoding="utf-8").read()
    js = open(os.path.join(ROOT, "web", "control.js"), encoding="utf-8").read()
    html = open(os.path.join(ROOT, "web", "control.html"), encoding="utf-8").read()

    body = html.split("<link rel=\"stylesheet\" href=\"control.css\">")[1]
    body = body.replace('<script src="control.js"></script>', "")
    payload = json.dumps(data, separators=(",", ":")).replace("</", "<\\/")

    page = (
        "<title>White Cell Display</title>\n"
        f"<style>{css}</style>\n"
        f"{body}\n"
        f"<script>window.REPLAY={payload};</script>\n"
        f"<script>{js}</script>\n"
    )
    with open(out, "w", encoding="utf-8") as fh:
        fh.write(page)
    print(f"wrote {out} ({len(page)//1024} KB, {len(data['frames'])} frames)")


if __name__ == "__main__":
    main()
