"""The query path: parse, execute, inject, render.

    intent  = parse_intent(query)              # cache -> rules -> (llm) -> failed
    result  = execute(intent, belief, world)   # computation, never a model
    result  = maybe_inject_error(result, cfg)  # presentation layer only
    return    render(result, cfg.style)        # template, never a model

The discipline that makes the study interpretable: `world` is read for terrain,
physics, and own-side entities only. Non-own entities enter through
ProjectionInput built from BeliefState (ADR-001, reconciliation X-01).
"""

from __future__ import annotations

from dataclasses import dataclass

from engine.belief import BeliefState
from engine.errors import Injector
from engine.intents import Intent, IntentParser
from engine.projection import (
    ProjectionOutcome,
    belief_input,
    project_subject,
    whatif_move,
    whatif_route,
)
from engine import render as R
from engine.world import WorldState

KELO = (4150.0, 7550.0)
# The forced branch: two routes to the same objective, joined by the northern
# lateral, separated by the lake. West is short, fast and exposed; east is long,
# slow and covered. Neither dominates, so neither is choosable on the available
# information without asking (ADR-010, docs/studies/study-i-army.md).
ROUTE_WEST = [(2850.0, 3050.0), (2850.0, 7550.0), KELO]
ROUTE_EAST = [(7050.0, 3050.0), (7050.0, 7550.0), KELO]
DIRECTION_VECTOR = {"north": (0.0, -1.0), "south": (0.0, 1.0),
                    "east": (1.0, 0.0), "west": (-1.0, 0.0)}


@dataclass(frozen=True)
class ConditionConfig:
    channel: str = "ai_mediated"  # "ai_mediated" | "human_mediated"
    style: str = "plain"  # hedging register
    social_info: str = "none"  # Study II: none | raw_peer | peer_in_projection


@dataclass(frozen=True)
class Answer:
    text: str
    intent: Intent
    injection_id: str | None
    outcome: ProjectionOutcome | None = None


class QueryEngine:
    def __init__(
        self,
        parser: IntentParser,
        injector: Injector,
        order_true_reading: str,
        order_distorted_readings: dict[str, str],
    ) -> None:
        self.parser = parser
        self.injector = injector
        self.order_true_reading = order_true_reading
        self.order_distorted_readings = order_distorted_readings

    def answer(
        self, query: str, belief: BeliefState, world: WorldState, cfg: ConditionConfig
    ) -> Answer:
        intent = self.parser.parse(query)
        t = world.t
        override, inj_id = self.injector.param_override(t)

        if intent.name == "locate":
            subj = intent.params["subject"]
            est = belief.best_estimate(subj, t)
            return Answer(R.render_locate(est, cfg.style, subj), intent, None)

        if intent.name == "strength":
            subj = intent.params["subject"]
            est = belief.best_estimate(subj, t)
            return Answer(R.render_strength(est, cfg.style, subj), intent, None)

        if intent.name == "peer_status":
            subj = intent.params["peer_id"]
            est = belief.best_estimate(subj, t)
            return Answer(R.render_locate(est, cfg.style, subj), intent, None)

        if intent.name in ("project", "eta"):
            subj = intent.params["subject"]
            pi = belief_input(belief, subj, t, override)
            if pi is None:
                return Answer(R.render_unknown(cfg.style), intent, None)
            horizon = int(intent.params.get("horizon_s", 1800))
            out = project_subject(pi, KELO, horizon)
            return Answer(R.render_projection(out, cfg.style), intent, inj_id, out)

        if intent.name == "whatif":
            unit = intent.params["unit"]
            if unit not in world.entities:
                return Answer(R.render_unknown(cfg.style), intent, None)
            dx, dy = DIRECTION_VECTOR[intent.params.get("dir", "north")]
            base = world.entities[unit].pos
            target = (base[0] + dx * 2500.0, base[1] + dy * 2500.0)
            out = whatif_move(world, unit, target, int(intent.params.get("horizon_s", 1800)))
            return Answer(R.render_projection(out, cfg.style), intent, None, out)

        if intent.name == "compare_options":
            horizon = int(intent.params.get("horizon_s", 1800))
            unit = "blue_1pl" if "blue_1pl" in world.entities else next(iter(world.entities))
            rows = [
                ("west road corridor", whatif_route(world, unit, ROUTE_WEST)),
                ("east forest track", whatif_route(world, unit, ROUTE_EAST)),
            ]
            return Answer(R.render_compare(rows, cfg.style), intent, None)

        if intent.name == "order_interpretation":
            inj = self.injector.active(t, "guidance_distortion")
            if inj is not None and inj.direction in self.order_distorted_readings:
                text = self.order_distorted_readings[inj.direction]
                return Answer(R.render_order(text, cfg.style), intent, inj.id)
            return Answer(R.render_order(self.order_true_reading, cfg.style), intent, None)

        return Answer(R.render_unknown(cfg.style), intent, None)
