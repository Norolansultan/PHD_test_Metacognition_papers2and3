# Study I — army, papers 1 and B

One continuous scenario, no artificial phasing. **The phase boundary arises from when the order
arrives.** This is the first content package to be built.

## Structure

| | Phase 1 — paper 1 | Phase 2 — paper B |
|---|---|---|
| Situation | The attack begins, the situation develops | Radio order: withdraw, move to area X |
| Information | Bottom-up situation reports from own units only | The same, plus the order from above |
| Manipulation | Human-mediated vs AI-mediated **situation picture** | Who interprets the vague order — the commander or the AI on their behalf |
| Group 1 | Human-mediated picture | Left to their own interpretation |
| Group 2 | AI-mediated picture | Sees the interpretation sharpen in projections **they request themselves** |

**The channel is constant within a participant for the whole session.** An organisation does not
change its mediation channel mid-battle. The manipulated variable is therefore not "the channel of
this message" but **an AI-mediated versus a human-mediated chain of command** — a whole construct,
and a better answer to the core question than a per-message channel would be. See
[ADR-011](../adr/ADR-011-condition-locked-at-session-start.md).

### What the human-mediated arm actually is

Both arms are served from the same `BeliefState`. The human-mediated arm receives a written
situation summary produced by a scripted staff role, on a fixed cycle, using the same uncertainty
vocabulary as the templates. It is push rather than pull and cannot be queried.

Any content difference between the arms is a confound. What differs is **who assembles and when**,
never what is available.

## The radio order

**The same vague order for everyone. It does not repeat.**

That single choice removes three confounds the earlier design carried: pushed versus pulled
guidance, different timing for different participants, and different content across conditions. It
is also ecologically accurate — a real order is often vague, and a commander's work is to interpret
it into their own situation. **That interpretive work is exactly what an AI can take over
unnoticed.**

Writing requirements:

- **Vagueness is designed and measured.** Piloting confirms that unaided interpretation disperses
  enough to be measurable but not without bound. Too precise leaves no interpretive room; too vague
  produces random dispersion.
- **`required_by_order(order, world_state) -> ActionSet` must be writable** for every decision point
  where drift is measured. Where it cannot be written, that point yields no drift data — better
  learned while writing content than during analysis.
- The original order lives in world truth, unmodified. It is the only thing drift is measured
  against.

## Drift — the dependent variable

```
drift(participant) = distance( decision , action the order required in this situation )
reference          = the non-projection group's own distribution of interpretations
```

Without the non-projection group there is no drift measure: human interpretation disperses anyway,
and against no reference distribution any deviation would look like drift.

## The forced question

Pulled guidance is the strongest form of the question, because self-retrieved information is
experienced as one's own reasoning in a way given information is not. Its cost is self-selected
exposure. Three remedies, all of them built:

1. **A branch point in the scenario.** The situation branches so that there is no way forward
   without asking something: two equally plausible directions and insufficient information to
   choose. This is a terrain requirement, not an interface feature — see
   [ADR-010](../adr/ADR-010-fictional-terrain-designed-for-the-experiment.md).
2. **Radio fallback.** If no query has arrived by time T, the same guidance arrives by radio,
   **including the distorted interpretation when one is active**. Logged as
   `guidance_route: query | radio_fallback`.
3. **Asking behaviour is itself a measure** — a metacognitive control decision, collected regardless.

**Analysis consequence:** exposure route is a covariate in every phase-2 model. Participants exposed
by fallback are not the same group as those who asked, even though the content is identical.

## Order and its limits

- **Phase 1 always first, no counterbalancing.** The baseline must not leak knowledge of the
  guidance. Reported as a limitation.
- **A learning effect into phase 2** exists and is stated — but it is ecologically correct: a real
  user does not meet the system for the first time during a crisis.
- **Scenario length 60-90 minutes**, one session. The phase boundary falls near the midpoint so that
  both phases yield probes and at least one freeze.
- **The calibration battery runs separately and beforehand.** Session structure is in
  [docs/measurement](../measurement/README.md).

## What the platform must provide

| Requirement | Reference |
|---|---|
| Channel locked at session start, no path to change it | [ADR-011](../adr/ADR-011-condition-locked-at-session-start.md) |
| Original order in world truth; `required_by_order` computable | [Architecture](../architecture/README.md) |
| Error injection, two mutually exclusive types, ~20 % / ~20 % / 0 % | [ADR-006](../adr/ADR-006-error-injection-in-the-presentation-layer.md) |
| Free text query, acknowledgement under 300 ms | [Architecture](../architecture/README.md) |
| Forced branch in terrain plus radio fallback | [ADR-010](../adr/ADR-010-fictional-terrain-designed-for-the-experiment.md) |
| 15-25 probes, confidence after each, ISA in every freeze | [Measurement](../measurement/README.md) |
| Open Level-3 probe in two or three freezes | [Measurement](../measurement/README.md) |
| One-way detection battery after the session | [Measurement](../measurement/README.md) |
| Screen blanking that survives remote collection | [Implementation](../implementation/build-order.md) |
| Debrief view | [Ethics](../operations/ethics-and-framing.md) |

## Open: echelon

The dissertation plan does not name the echelon, and it is a **blocking** decision: terrain scale,
cell size, movement speeds, order wording, unit types, and the whole probe bank's difficulty follow
from it.

| Option | Consequence |
|---|---|
| **Company commander** | Smaller terrain (~10 × 10 km), shorter movements, denser decision points, easier recruitment to 100 |
| **Battalion commander** | Matches the earlier Paper 1 design on KESI at MPKK, larger terrain (~30 × 30 km), fewer but heavier decisions, harder recruitment |

Pick one. Mixing echelons produces variance that 100 participants cannot model. If recruitment comes
from course cohorts, the cohort's level decides it for you — establish that first.
