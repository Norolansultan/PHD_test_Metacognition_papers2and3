"""FastAPI: a thin layer over the engine (ADR-002).

No identifier scheme, no login: ?pid=p117&scenario=fin-def-03 is enough
(docs/implementation/environment.md).
"""

from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from api.session import Session

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
app = FastAPI(title="mediated command chain")
SESSIONS: dict[str, Session] = {}


class StartBody(BaseModel):
    pid: str
    scenario: str = "fin-def-03"
    condition: str = "ai_mediated"
    style: str = "plain"


class AskBody(BaseModel):
    pid: str
    text: str


class ProbeBody(BaseModel):
    pid: str
    choice: str | None = None
    text: str | None = None
    confidence: int = 3


class IsaBody(BaseModel):
    pid: str
    value: int


class DecideBody(BaseModel):
    pid: str
    action: str
    unit: str | None = None
    route: list[list[float]] | None = None


class FocusBody(BaseModel):
    pid: str
    reason: str


class TickNBody(BaseModel):
    pid: str
    n: int = 1
    truth: bool = False


def _s(pid: str) -> Session:
    return SESSIONS[pid]


@app.post("/api/start")
def start(b: StartBody) -> dict:
    SESSIONS[b.pid] = Session(participant=b.pid, scenario_id=b.scenario,
                              condition=b.condition, style=b.style, session_id=f"s_{b.pid}")
    return _s(b.pid).view()


@app.post("/api/tick")
def tick(b: StartBody) -> dict:
    s = _s(b.pid)
    s.tick()
    return s.view()


@app.post("/api/ask")
def ask(b: AskBody) -> dict:
    s = _s(b.pid)
    return {"answer": s.ask(b.text), "view": s.view()}


@app.post("/api/probe")
def probe(b: ProbeBody) -> dict:
    s = _s(b.pid)
    s.answer_probe(b.choice, b.text, b.confidence)
    return s.view()


@app.post("/api/isa")
def isa(b: IsaBody) -> dict:
    s = _s(b.pid)
    s.answer_isa(b.value)
    return s.view()


@app.post("/api/decide")
def decide(b: DecideBody) -> dict:
    s = _s(b.pid)
    s.decide(b.action, b.unit, b.route)
    return s.view()


@app.post("/api/focus_lost")
def focus_lost(b: FocusBody) -> dict:
    s = _s(b.pid)
    s.focus_lost(b.reason)
    return {"ok": True}


@app.post("/api/finish")
def finish(b: StartBody) -> dict:
    s = _s(b.pid)
    path = os.path.join(ROOT, "logs", f"{b.pid}.jsonl")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    s.log.save(path)
    return {"saved": path, "events": len(s.log.rows)}


@app.post("/api/truth")
def truth(b: StartBody) -> dict:
    """WHITE CELL ONLY (see Session.truth_view). Never called by web/app.js."""
    return _s(b.pid).truth_view()


@app.post("/api/tick_n")
def tick_n(b: TickNBody) -> dict:
    """Advance several ticks at once, for the white cell's time acceleration."""
    s = _s(b.pid)
    for _ in range(max(1, min(120, b.n))):
        s.tick()
    return s.truth_view() if b.truth else s.view()


@app.get("/api/scenario/{scenario_id}")
def scenario_meta(scenario_id: str) -> dict:
    import base64

    from engine import scenario as scen

    s = scen.load(os.path.join(ROOT, f"scenarios/{scenario_id}.yaml"), root=ROOT)
    with open(os.path.join(ROOT, "scenarios/terrain/valley_a.png"), "rb") as fh:
        png = base64.b64encode(fh.read()).decode("ascii")
    from engine.query import KELO, ROUTE_EAST, ROUTE_WEST

    return {"terrain_png": png, "cell_m": s.initial.terrain.cell_m,
            "legend": s.initial.terrain.legend, "duration_s": s.duration_s,
            "width_m": s.initial.terrain.width_m,
            "routes": {"west": [list(p) for p in ROUTE_WEST],
                       "east": [list(p) for p in ROUTE_EAST]},
            "objective": list(KELO),
            "junction": [4150.0, 3050.0]}


app.mount("/", StaticFiles(directory=os.path.join(ROOT, "web"), html=True), name="web")
