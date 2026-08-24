"""Live session state. The engine drives it; the API only exposes it.

The session owns the scenario clock, the belief layer, the injector, the query
engine and the log. Nothing here decides anything the engine has not already
decided; this module exists so that a browser can step the same run the harness
steps (ADR-002: FastAPI is a thin layer over the engine).
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from random import Random

from engine import scenario as scen
from engine.belief import BeliefState, sense
from engine.errors import Injector
from engine.eventlog import EventLog
from engine.intents import IntentParser
from engine.query import ConditionConfig, QueryEngine
from engine.world import TICK_S, step, with_route

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


@dataclass
class Freeze:
    """A freeze stops the scenario clock, blanks the display and refuses queries."""

    probe_ref: str
    open_l3: bool
    started_t: int


@dataclass
class Session:
    participant: str
    scenario_id: str
    condition: str = "ai_mediated"
    style: str = "plain"
    session_id: str = "s0001"

    def __post_init__(self) -> None:
        self.s = scen.load(os.path.join(ROOT, f"scenarios/{self.scenario_id}.yaml"), root=ROOT)
        self.cfg = ConditionConfig(channel=self.condition, style=self.style)
        self.rng = Random(self.s.seed)
        self.belief = BeliefState()
        self.injector = Injector(self.s.injections)
        self.qe = QueryEngine(IntentParser(), self.injector,
                              self.s.order.true_reading, self.s.order.distorted_readings)
        self.log = EventLog(self.session_id, self.participant, self.condition, self.s.seed)
        self.world = self.s.initial
        self.obs_seq = 0
        self.asked_order = False
        self.freeze: Freeze | None = None
        self.finished = False
        self.pending: list[dict] = []  # radio traffic the client has not shown yet
        self._probes = {p.t: p for p in self.s.probes}
        self._events: dict[int, list] = {}
        for ev in self.s.events:
            self._events.setdefault(ev.t, []).append(ev)
        self.log.write(0, "session_start", scenario=self.s.id,
                       scenario_version=self.s.version, echelon=self.s.echelon,
                       condition_config=self.cfg)
        self._tick_world_events()

    # ------------------------------------------------------------------ clock

    def tick(self) -> None:
        """Advance one tick. A freeze stops the clock entirely (docs/architecture)."""
        if self.freeze is not None or self.finished:
            return
        if self.world.t >= self.s.duration_s:
            if not self.finished:
                self.finished = True
                self.log.write(self.s.duration_s, "debrief_shown",
                               covers=[i.kind for i in self.s.injections])
                self.log.write(self.s.duration_s, "session_end",
                               observations=len(self.belief.observations))
            return
        self.world = step(self.world, self.rng, TICK_S)
        self._tick_world_events()

    def _tick_world_events(self) -> None:
        t = self.world.t
        for o in sense(self.world, self.s.sensors, self.rng, self.obs_seq):
            self.obs_seq += 1
            self.belief.add(o)
            self.log.write(t, "observation_created", observation=o)

        for ev in self._events.get(t, []):
            self._radio(ev.sender, ev.text)
            o = scen.observation_from_event(ev, self.obs_seq)
            if o is not None:
                self.obs_seq += 1
                self.belief.add(o)
                self.log.write(t, "observation_created", observation=o)

        if t == self.s.order.issued_t:
            self._radio("higher_hq", self.s.order.text, tag=self.s.order.ref)

        if t == self.s.order.fallback_at_t and not self.asked_order:
            inj = self.injector.active(t, "guidance_distortion")
            reading = (self.s.order.distorted_readings.get(inj.direction) if inj else None) \
                or self.s.order.true_reading
            self._radio("higher_hq", reading, tag="order_interpretation_fallback",
                        guidance_route="radio_fallback", injection=(inj.id if inj else None))

        if t in self._probes:
            pr = self._probes[t]
            self.freeze = Freeze(pr.ref, pr.open_l3, t)
            self.log.write(t, "freeze_start", ref=pr.ref, channels_locked=True)
            self.log.write(t, "screen_blanked", ref=pr.ref)
            self.log.write(t, "probe_shown", ref=pr.ref, open_l3=pr.open_l3)

    def _radio(self, sender: str, text: str, **extra) -> None:
        row = self.log.write(self.world.t, "radio_message", sender=sender, text=text, **extra)
        self.pending.append({"t": self.world.t, "sender": sender, "text": text,
                             "tag": extra.get("tag")})

    # ----------------------------------------------------------- participant

    def ask(self, text: str) -> dict:
        if self.freeze is not None:
            # The channel is provably unreachable during a freeze, and the refusal
            # is itself logged.
            self.log.write(self.world.t, "query", raw_text=text, refused="freeze")
            return {"refused": True,
                    "text": "The channel is unavailable while the display is blanked."}
        self.log.write(self.world.t, "query", raw_text=text)
        ans = self.qe.answer(text, self.belief, self.world, self.cfg)
        if ans.intent.name == "order_interpretation":
            self.asked_order = True
        self.log.write(self.world.t, "answer", intent=ans.intent.name,
                       params=ans.intent.params, parse_route=ans.intent.route,
                       text=ans.text, injection=ans.injection_id,
                       guidance_route=("query" if ans.intent.name == "order_interpretation"
                                       else None))
        return {"refused": False, "text": ans.text, "intent": ans.intent.name}

    def answer_probe(self, choice: str | None, text: str | None, confidence: int) -> None:
        if self.freeze is None:
            return
        self.log.write(self.world.t, "probe_answer", ref=self.freeze.probe_ref,
                       choice=choice, text=text)
        self.log.write(self.world.t, "confidence", ref=self.freeze.probe_ref, value=confidence)

    def answer_isa(self, value: int) -> None:
        self.log.write(self.world.t, "isa_load", value=value)
        if self.freeze is not None:
            self.log.write(self.world.t, "freeze_end", ref=self.freeze.probe_ref)
            self.freeze = None

    def decide(self, action: str, unit: str | None, route: list[list[float]] | None) -> None:
        self.log.write(self.world.t, "decision", action=action, unit=unit, route=route)
        if unit and route:
            self.world = with_route(self.world, unit,
                                    [(float(p[0]), float(p[1])) for p in route])

    def focus_lost(self, reason: str) -> None:
        self.log.write(self.world.t, "focus_lost", reason=reason,
                       during_freeze=self.freeze is not None)

    # ------------------------------------------------------------------ view

    def view(self) -> dict:
        """Everything the client may render. Belief layer only — never truth."""
        t = self.world.t
        beliefs = []
        for subject in self.belief.known_subjects(t):
            est = self.belief.best_estimate(subject, t)
            if est is None or est.pos is None:
                continue
            beliefs.append({
                "subject": subject, "pos": list(est.pos), "age_s": est.age_s,
                "uncertainty_m": round(est.uncertainty_m), "source": est.source,
                "channel": est.channel, "attrs": est.attrs,
            })
        own = {
            e.id: {"pos": list(e.pos), "status": e.status,
                   "endurance_s": e.endurance_s}
            for e in self.world.entities.values() if e.side == "blue"
        }
        pending, self.pending = self.pending, []
        return {
            "t": t, "duration_s": self.s.duration_s, "finished": self.finished,
            "own": own, "beliefs": beliefs, "radio": pending,
            "freeze": (None if self.freeze is None else
                       {"ref": self.freeze.probe_ref, "open_l3": self.freeze.open_l3}),
        }
