# Reconciliation: implementation guide against the prior plan

The implementation guide (August 2026) and the prior build plan disagree in twenty-eight places.
This document lists every one of them with a verdict, so that no disagreement is settled silently
in code.

Three verdicts are used:

- **ADOPT GUIDE** — the guide is right and the plan was wrong or vague. The plan has been changed.
- **KEEP PLAN** — the plan is better or covers something the guide does not. Kept, and flagged here
  so the difference is a decision rather than an oversight.
- **SYNTHESIS** — neither is complete; a third position is specified.

One defect in the prior plan is recorded in D-01. It is the exact mistake the guide warns about,
and it would have made the results uninterpretable.

---

## A. Where the guide is right

### D-01 · The AI could read world truth — a defect in the prior plan · ADOPT GUIDE

The prior plan defined two layers, ground truth and perceived, and specified that the truth layer
must be unreachable **in the participant's build**. It then defined the projection engine as taking
a request and running the model against world state. That is the omniscient-AI failure the guide
names in §13: the channel would have answered from truth while the interface merely hid truth from
the screen. The manipulated variable would not have been mediation at all.

The guide's three-layer model is correct and is now the architecture: world truth, organisational
knowledge (`BeliefState`, built from timestamped `Observation` records), and what is presented.
The AI answers from layer 2. See [README.md](README.md).

### D-02 · Python engine, not TypeScript · ADOPT GUIDE

The plan chose TypeScript for a single language across engine, build tooling and interface. The
guide specifies a pure Python `engine/` under pytest, FastAPI at the boundary, and a separate
frontend. The guide wins on two grounds the plan underweighted: the analysis side is R and Python
(HMeta-d, embeddings for the open probe), and a research engine that must be re-run years later is
better served by the scientific stack than by a Node toolchain. See
[ADR-002](../adr/ADR-002-python-engine-typescript-only-in-the-browser.md).

### D-03 · Immutable world state · ADOPT GUIDE

`step(state) -> WorldState` returning a new state makes what-if trivial: copy, run forward, discard.
The plan left mutability unspecified, which invites in-place simulation and a projection that
corrupts the run it is projecting from.

### D-04 · Observations are records, not updates · ADOPT GUIDE

The plan carried a temporally indexed corpus with `valid_from` and `superseded_by`. The guide's
model is simpler and truer: observations never update, and `best_estimate` picks the freshest and
extrapolates. `superseded_by` disappears — a newer observation supersedes an older one by existing.

### D-05 · Sensors generate observations · ADOPT GUIDE

The plan hand-authored corpus entries and their query paths. The guide declares sensors in the
scenario (`range_m`, `pos_error_m`, `interval_s`) and lets observations fall out of the simulation.
This is a large content-work saving and it removes a whole class of inconsistency between what a
sensor could have seen and what the corpus says it saw.

**Consequence for Study II:** the "information-sparse sector" is no longer a hand-written emptiness
that a well-meaning contributor can fill in. It is a region no sensor has covered, and it stays
empty by construction.

### D-06 · Drone endurance models information scarcity · ADOPT GUIDE

The plan scripted a drone as grounded between two scenario points. The guide gives it endurance and
coverage, so scarcity is a modelled consequence rather than a scripted event — and uncertainty grows
on its own while the drone is down.

### D-07 · Peer decisions are observations · ADOPT GUIDE

Paper A's peer content is `Observation` records whose `observer` is another commander and whose
`subject` is that commander's own unit. The plan had a separate peer-arc table that had to be kept
consistent with everything else by hand. One mechanism replaces two.

### D-08 · Explicit ageing function · ADOPT GUIDE

`uncertainty = pos_error + drift_rate * (t_now - t_observed)` is the whole staleness model in one
line, and it makes "how old is this" a computed answer rather than a rendering convention.

### D-09 · Closed intent set · ADOPT GUIDE

Nine intents beat the plan's WHO × WHAT × WHEN slot grammar: they are enumerable, testable, and each
one names a research construct. `order_interpretation` in particular is the exact point where Paper
B's manipulation lives, and the plan had no equivalent.

### D-10 · One YAML per scenario, probes in a shared bank · ADOPT GUIDE

The plan compiled everything into a single content pack. Per-scenario files are readable by a
supervisor without programming, publishable as an appendix, and let the same probe serve several
scenarios.

### D-11 · Continuous positions over a raster · ADOPT GUIDE

The plan spent a section choosing between square and hex cells. The guide uses continuous float
positions in metres with terrain sampled from a raster, which makes the question moot and the
distances honest.

### D-12 · Headless harness before the frontend · ADOPT GUIDE

The plan sequenced tests after features. The guide makes the harness a prerequisite: scripted
participants in YAML produce the same log file a real session does. This gives regression tests,
synthetic data for the analysis pipeline before the first participant, and a demo that needs no
clicking.

### D-13 · Demo mode with a debug panel · ADOPT GUIDE

Not in the plan at all. A demo without a debug panel shows a supervisor one arbitrary condition and
tells them nothing. With the panel — active condition, what the model computed, which injection is
live, which observations the answer was built from — the demo becomes an argument.

### D-14 · Codespaces, private repository, DOI on publication · ADOPT GUIDE

Not in the plan. The repository must be **private during collection**: the target population is
technically capable, and published injection rates and answer keys would contaminate the sample.
Public at publication with Zenodo, DOI, and `CITATION.cff`.

### D-15 · `injection_id` on every answer · ADOPT GUIDE

Stronger than the plan's flag-plus-spec-id: every answer carries the id or `null`, so exposure
reconstruction never depends on joining two streams.

### D-16 · Replay tested at the start · ADOPT GUIDE

The plan had replay as a phase-3 deliverable. The guide is right that it must be proven early —
retrofitting replay onto a log format that cannot support it means re-collecting.

### D-17 · Expert validation as a gate at step 5 · ADOPT GUIDE

The guide places expert review of the projections before logging, parsing, or any interface. It is
the cheapest possible kill point: if the projections do not survive an expert's look, nothing built
after them matters.

---

## B. Where the prior plan is better or covers what the guide omits

These are kept. Each is a deliberate addition to the guide, not an oversight in it.

### D-18 · Parser determinism · KEEP PLAN

The guide allows `parse_intent` to be "LLM or rule-based". A language model is not deterministic,
and identical questions from two participants must produce identical answers. The plan's three-tier
parser is kept: normalise → **cache keyed by normalised text** → rule-based slot parser → LLM
fallback at temperature 0, whose result is written to the cache → fixed clarification request.

What is promised in the methods section: identical question text yields identical parameters and an
identical answer for every participant, for the whole collection. What is not promised: two
differently worded questions may parse differently. The parse route is logged and parse variation is
reported.

### D-19 · The calibration battery · KEEP PLAN — and now fixed at 200 items

The guide does not mention it at all. It is the only place individual-level M-ratio can be
estimated; a scenario task never yields enough trials. Without it there is no anchor for Paper D's
proxy validation, and Paper D has no data collection of its own.

**Now specified: 200 items per participant**, run as a separate session on its own time. See
[../measurement/calibration-battery.md](../measurement/calibration-battery.md).

### D-20 · Reactivity control · KEEP PLAN

Asking for confidence is itself a cognitive-forcing intervention. Not in the guide. A sparse-probe
group (n ≈ 20, two or three probes for the whole session), **not crossed** with the main design plus
proxy weighting in high-tempo passages.

### D-21 · The detection battery · KEEP PLAN

A channel manipulation without a detection measure is half a study, and the guide has the log event
types (`attribution_free`, `attribution_forced`) but no specification. The order is a build
requirement: free attribution before any source is named, then forced recognition, then behavioural
shift — one-way, no going back.

### D-22 · State-space document before code · KEEP PLAN

Four to six metacognitive states × four columns. The third column — online proxy plus the log fields
that make it computable — determines the logging schema, and a logging schema cannot be fixed
retroactively. This is a blocking deliverable, not a design note.

### D-23 · Freeze semantics · KEEP PLAN

The guide has `freeze_start`, `freeze_end` and `screen_blanked` events and requires blanking. It does
not say that the scenario clock stops and that querying is refused during a freeze. Both are kept,
and a refused query during a freeze is itself logged.

### D-24 · The drift measure · KEEP PLAN

Paper B's dependent variable is the distance between what the participant did and **what the original
radio order would have required in their situation**, compared against the non-projection group's own
interpretation distribution. The guide has the distortion mechanism but not the measure.
`required_by_order(order, world_state) -> ActionSet` must be a computable function; where it cannot be
written for a decision point, that point yields no drift data, and it is better to learn that while
writing content than during analysis.

### D-25 · Injection proportions · KEEP PLAN

The guide states the two types are never in the same trial. The plan's proportions are kept:
~55 % clean, ~20 % projection error, ~20 % guidance distortion, 0 % both. Distortion direction stays
systematic within a scenario and is balanced across scenarios; a direction that varies mid-scenario
reveals the manipulation through its structure rather than its content.

### D-26 · Terrain as apparatus · KEEP PLAN

The guide specifies fictional terrain as a PNG plus legend. It does not say what the terrain must
contain. Kept: a forced branch point (two equally plausible directions and insufficient information
to choose), visibility shadows, two routes with different risk profiles, and distances that make
time a real cost. The experimental-design gate is checked before the realism gate, and where they
conflict the experimental gate wins.

### D-27 · Two version fields, not one · KEEP PLAN

The guide requires `engine_version` on every log row. The plan also requires `schema_version`. Both
are kept: the engine version identifies the model that produced an answer, the schema version
identifies the shape of the log row. A mid-collection change to either one is survivable only if
both are recorded.

### D-28 · What the guide leaves out entirely · KEEP PLAN

Remote-collection mechanics (fullscreen enforcement, focus-loss logging, minimum viewport);
condition immutability enforced so that no code path can change the channel mid-session; probe
placement rules; the ethics framing rule and the debrief view as software; the power simulation and
preregistration; parameter sourcing from CMO runs; the content validator; and the open-decisions
register. All retained.

---

## C. Ambiguities in the guide that needed a ruling

### X-01 · `execute(intent, belief, world)` hands the engine the truth handle · SYNTHESIS

The guide's principle is that the AI answers from layer 2, but its own function signature passes
`world` alongside `belief`. Discipline cannot be enforced by a signature that grants the access it
forbids.

**Ruling:** `world` is passed for terrain, physics, and own-side state only — the things the
organisation genuinely knows. Every non-own entity enters a projection through a `ProjectionInput`
constructed from `BeliefState`, carrying the estimate and its uncertainty. A test perturbs red truth
without changing any observation and asserts that every projection's output is unchanged. If that
test ever fails, the channel has become omniscient.

### X-02 · Guidance distortion only reaches participants who ask for it · SYNTHESIS

Distortion is delivered through the `order_interpretation` intent. A participant who never asks for
an interpretation is never exposed — which reintroduces the self-selection problem the forced
question was built to solve.

**Ruling:** the radio fallback delivers the interpretation, distorted or not, at time T if no query
has arrived. Exposure route (`query` or `radio_fallback`) is logged and is a covariate in every
phase-2 model. Participants exposed by fallback are not the same group as those who asked, even
though the content is identical.

### X-03 · Hand-written answer keys · SYNTHESIS

The guide writes `correct: C` into the probe file. The plan required probe ground truth to be
computed from world state, because a hand-written key silently drifts when the model changes.

**Ruling:** keep the hand-written key, and make it an assertion rather than a source. The validator
runs the scenario headless and re-derives the answer; a mismatch fails the build. This catches both
a wrong key and a model change that invalidated a key — which neither approach catches alone.

### X-04 · What the human-mediated condition actually is · SYNTHESIS

The guide says the two conditions differ only in who assembles the same `BeliefState`. It does not
say what the human-mediated assembly looks like.

**Ruling:** the human-mediated arm receives a written situation summary produced by a scripted staff
role from exactly the same `BeliefState`, on a fixed cycle, with the same template vocabulary for
uncertainty. It is push rather than pull, and it cannot be queried. Any content difference between
the arms is a confound; the difference must be who assembles and when, never what is available.

### X-05 · No metacognitive baseline in the guide · RESOLVED BY DECISION

Now resolved: 200 items per participant, separate session. See D-19.

---

## Change record

| Date | Change |
|---|---|
| 2026-08 | Prior plan rewritten against the August 2026 dissertation plan |
| 2026-08 | Reconciled against the implementation guide; this document created; D-01 recorded as a defect in the prior plan; calibration battery fixed at 200 items; sample fixed at ~100 participants |
