"""Headless run: a whole scenario with a scripted participant, no browser (ADR-008).

Emits the same log a real session does. That gives regression tests, synthetic
data for the analysis pipeline before the first participant, and a demonstration
that needs no clicking.

    python3 -m harness.run --scenario scenarios/fin-def-03.yaml \
        --participant harness/participants/synth_01.yaml --out logs/synth_01.jsonl
"""

from __future__ import annotations

import argparse
import os
import sys
from random import Random

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import yaml

from engine import scenario as scen
from engine.belief import BeliefState, sense
from engine.errors import Injector
from engine.eventlog import EventLog
from engine.intents import IntentParser
from engine.query import ConditionConfig, QueryEngine
from engine.world import TICK_S, step, with_waypoint


def load_participant(path: str) -> dict:
    with open(path, encoding="utf-8") as fh:
        return yaml.safe_load(fh)


def run(scenario_path: str, participant_path: str, out_path: str, root: str = ".") -> EventLog:
    s = scen.load(scenario_path, root=root)
    p = load_participant(participant_path)
    cfg = ConditionConfig(
        channel=p.get("condition", "ai_mediated"),
        style=p.get("style", "plain"),
        social_info=p.get("social_info", "none"),
    )

    rng = Random(s.seed)
    belief = BeliefState()
    injector = Injector(s.injections)
    parser = IntentParser()
    qe = QueryEngine(parser, injector, s.order.true_reading, s.order.distorted_readings)

    log = EventLog(
        session=p.get("session", "s0001"),
        participant=p["participant"],
        condition=cfg.channel,
        seed=s.seed,
    )
    log.write(0, "session_start", scenario=s.id, scenario_version=s.version,
              echelon=s.echelon, condition_config=cfg, social_info=cfg.social_info)

    actions = sorted(p.get("actions", []), key=lambda a: (a["at_t"], a.get("type", "")))
    ai = 0
    obs_seq = 0
    asked_order = False
    world = s.initial
    probes_by_t = {pr.t: pr for pr in s.probes}
    events_by_t: dict[int, list] = {}
    for ev in s.events:
        events_by_t.setdefault(ev.t, []).append(ev)

    while world.t <= s.duration_s:
        t = world.t

        # 1. Sensors observe. Layer 1 -> layer 2, and the only route between them.
        for o in sense(world, s.sensors, rng, obs_seq):
            obs_seq += 1
            belief.add(o)
            log.write(t, "observation_created", observation=o)

        # 2. Scheduled radio traffic, and any observation it creates.
        for ev in events_by_t.get(t, []):
            log.write(t, "radio_message", sender=ev.sender, text=ev.text)
            o = scen.observation_from_event(ev, obs_seq)
            if o is not None:
                obs_seq += 1
                belief.add(o)
                log.write(t, "observation_created", observation=o)

        # 3. The vague order, identical in all conditions.
        if t == s.order.issued_t:
            log.write(t, "radio_message", sender="higher_hq", text=s.order.text,
                      tag=s.order.ref, identical_all_conditions=True)

        # 4. Radio fallback: exposure must not depend on whether they asked (X-02).
        if t == s.order.fallback_at_t and not asked_order:
            inj = injector.active(t, "guidance_distortion")
            reading = (s.order.distorted_readings.get(inj.direction)
                       if inj else None) or s.order.true_reading
            log.write(t, "radio_message", sender="higher_hq", text=reading,
                      tag="order_interpretation_fallback",
                      guidance_route="radio_fallback",
                      injection=(inj.id if inj else None))

        # 5. Probes.
        if t in probes_by_t:
            pr = probes_by_t[t]
            log.write(t, "probe_shown", ref=pr.ref, open_l3=pr.open_l3)

        # 6. The participant's scripted actions for this tick.
        while ai < len(actions) and actions[ai]["at_t"] <= t:
            a = actions[ai]
            ai += 1
            kind = a["type"]
            if kind == "query":
                log.write(t, "query", raw_text=a["text"])
                ans = qe.answer(a["text"], belief, world, cfg)
                if ans.intent.name == "order_interpretation":
                    asked_order = True
                log.write(t, "answer", intent=ans.intent.name, params=ans.intent.params,
                          parse_route=ans.intent.route, text=ans.text,
                          injection=ans.injection_id,
                          guidance_route=("query" if ans.intent.name == "order_interpretation"
                                          else None))
            elif kind == "probe_answer":
                log.write(t, "probe_answer", ref=a["ref"], choice=a.get("choice"),
                          text=a.get("text"))
                log.write(t, "confidence", ref=a["ref"], value=a.get("confidence"))
            elif kind == "isa":
                log.write(t, "isa_load", value=a["value"])
            elif kind == "decision":
                log.write(t, "decision", action=a["action"], axis=a.get("axis"),
                          unit=a.get("unit"))
                if a.get("unit") and a.get("target"):
                    world = with_waypoint(world, a["unit"],
                                          (float(a["target"][0]), float(a["target"][1])))
            elif kind == "decision_revert":
                log.write(t, "decision_revert", reverts=a.get("reverts"))

        # 7. Advance the world.
        if world.t >= s.duration_s:
            break
        world = step(world, rng, TICK_S)
        if world.t % 60 == 0:
            log.write(world.t, "world_tick",
                      entities={k: v.pos for k, v in sorted(world.entities.items())})

    log.write(s.duration_s, "debrief_shown",
              covers=[i.kind for i in s.injections])
    log.write(s.duration_s, "session_end", observations=len(belief.observations))

    os.makedirs(os.path.dirname(out_path) or ".", exist_ok=True)
    log.save(out_path)
    return log


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--scenario", required=True)
    ap.add_argument("--participant", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--root", default=".")
    a = ap.parse_args()
    log = run(a.scenario, a.participant, a.out, a.root)
    print(f"{a.out}: {len(log.rows)} events")


if __name__ == "__main__":
    main()
