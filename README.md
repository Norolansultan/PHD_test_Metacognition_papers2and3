# Mediated Command Chain

**Experimental environment for a dissertation on situation awareness, metacognition, and
AI-mediated command.**

> [!IMPORTANT]
> This repository contains a research instrument specification, a deterministic simulation engine
> design, and measurement apparatus for human-subjects research. It is not an operational command
> system and must not be used as one. The scenarios, terrain, place names, and organisations are
> fictional. The studies involve deception (error injection) and therefore require ethics approval,
> preregistration, and a debriefing procedure before any data collection.

## Overview

The dissertation asks one question: **how does AI help people decide and understand in situations
where more happens than a person can take in — and can an organisation's shifting strategy be
steered through AI, without human contact, in a way the user does not notice while projecting
decisions?**

The framing rule that governs every document, every interface string, and every paper in this
project: **the question is when a person notices they have been steered, not how steering is made
unnoticeable.** The same experiment read the other way is a manipulation manual. Write from the
detection and protection side, always.

This repository specifies the environment that makes that question measurable: a deterministic
simulation whose AI channel answers strictly from what the organisation has observed, never from
what is true, and whose every response, probe, confidence rating, and injected error is
reconstructable from an append-only log.

## Study programme

| Paper | Collection | Participants | What it isolates |
|---|---|---|---|
| 1 — AI as channel | Study I, phase 1 | army, ~100 | Human-mediated vs AI-mediated situation picture |
| B — vertical steering | Study I, phase 2 | same participants | Who interprets a vague order: the commander or the AI on their behalf |
| A — horizontal influence | Study II | rescue (recommended) | Social information as opinion vs as model input |
| D — adaptive algorithm | no collection of its own | — | Validating real-time proxies against an offline gold standard |

**Every participant first completes a 200-item calibration battery** that establishes their
individual metacognitive baseline before they ever see the scenario. This is run as a separate
session on its own time. It is the only place individual-level metacognitive efficiency (M-ratio)
can be estimated, and without it Paper D has no anchor. See
[docs/measurement/calibration-battery.md](docs/measurement/calibration-battery.md).

**Target sample: ~100 participants.** Design for 80 usable, recruit 100–110 — remote collection
loses more than supervised collection does.

## Operating principles

| Principle | Project interpretation |
|---|---|
| Three layers, never two | World truth, organisational knowledge, and what the user is shown are separate. The AI answers from organisational knowledge only. |
| Detection, not concealment | Detection measures are built before the manipulation. Every participant's exposure is reconstructable and is disclosed at debrief. |
| Measurement wins | This is a research instrument that contains a simulation, not a simulation with measurement added. Where immersion and measurement conflict, measurement wins. |
| Determinism is a hard requirement | Same seed, same inputs, same log — byte for byte. Condition means are not comparable without it. |
| Compute, never generate | The engine computes and renders from templates. No generative reasoning on the participant path. |
| Conditions are configuration | Changing a condition must never require a code change or a rebuild. |
| The log is the study | If a variable is not in the logging schema, it does not exist. Add it to the schema before building the feature. |
| Terrain is apparatus | Forced branch points, visibility shadows, and two plausible routes are requirements; visual realism is second. |
| Engine before interface | The headless harness comes before the frontend. Developing the engine through a browser is ten times slower. |
| One domain first | Study I (army) ships first. Study II (rescue) is a content package, not a second system. |

## Repository structure

```text
.
├── engine/                 Pure Python library — no web, no HTTP, no LLM
│   ├── world.py            Immutable world state, tick simulation
│   ├── belief.py           Observations, BeliefState, ageing
│   ├── projection.py       What-if: copy state, run forward, return outcome
│   ├── intents.py          Question → parameters (closed intent set)
│   ├── render.py           Outcome → text (templates)
│   └── errors.py           Error injection
├── scenarios/              One YAML per scenario
├── probes/                 Probe bank and answer keys, YAML
├── api/                    FastAPI — a thin layer over the engine
├── web/                    Browser frontend
├── harness/                Headless runs, scripted participants, regression
├── analysis/               HMeta-d, derived variables, coding frame
└── docs/
    ├── adr/                Architecture decision records
    ├── architecture/       Information model, engine boundaries, reconciliation
    ├── studies/            Study I and Study II designs
    ├── measurement/        Calibration battery, probes, metacognitive states
    ├── scenarios/          Scenario and probe file formats, validator rules
    ├── implementation/     Build order, phases, effort, demo mode, environment
    ├── operations/         Open decisions, risks, ethics and framing
    └── testing/            Determinism, replay, regression, gates
```

**Rule:** `engine/` knows nothing about HTTP, the browser, or any language model. It runs under
pytest and produces the same result every time. Everything else is replaceable.

## Documentation index

| Document | Contents |
|---|---|
| [docs/architecture/README.md](docs/architecture/README.md) | The three-layer information model, data model, engine boundaries |
| [docs/architecture/reconciliation.md](docs/architecture/reconciliation.md) | **Every point where the implementation guide and the prior plan differ, with a verdict** |
| [docs/adr/README.md](docs/adr/README.md) | Decisions that cannot be reversed without losing data |
| [docs/studies/study-i-army.md](docs/studies/study-i-army.md) | Papers 1 and B: two phases, the vague order, forced question |
| [docs/studies/study-ii-rescue.md](docs/studies/study-ii-rescue.md) | Paper A: three conditions, the incident, precedent validity |
| [docs/measurement/README.md](docs/measurement/README.md) | Sensitivity, calibration, efficiency; probes; detection battery; states |
| [docs/measurement/calibration-battery.md](docs/measurement/calibration-battery.md) | The 200-item baseline battery |
| [docs/scenarios/README.md](docs/scenarios/README.md) | Scenario YAML, probe YAML, validator rules |
| [docs/implementation/build-order.md](docs/implementation/build-order.md) | The order the parts are built in, and the gate at step 5 |
| [docs/implementation/environment.md](docs/implementation/environment.md) | Demo mode, Codespaces, repository visibility, secrets |
| [docs/testing/README.md](docs/testing/README.md) | Determinism, replay, regression, leakage, blanking |
| [docs/operations/open-decisions.md](docs/operations/open-decisions.md) | Decisions that block work, and who makes them |
| [docs/operations/risks.md](docs/operations/risks.md) | Risks the architecture answers, and those it does not |
| [docs/operations/ethics-and-framing.md](docs/operations/ethics-and-framing.md) | The framing rule as a build rule; debrief; disclosure |

## Getting started

```bash
make setup      # PyYAML, FastAPI, pytest
make test       # 28 tests, including determinism, replay and the omniscience test
make terrain    # regenerate the fictional terrain raster
make run        # run the scenario headless with two scripted participants
make viewer     # build the data for the session viewer
make api        # serve the participant display on :8000
make e2e        # drive a real browser against it and check the log
make demo       # all of the above, from a clean checkout
```

The engine has no web dependencies and no language-model dependency. `make test` is the whole
verification surface at this stage, and the first test written was the determinism test.

## What is built

Build-order steps 1-4 and 6 are done; step 5 is a gate that needs practitioner advisors, and nothing
downstream of it is validated until it passes. Progress and the defects found while building are in
[docs/implementation/status.md](docs/implementation/status.md).

| Component | State |
|---|---|
| `engine/world.py` — immutable state, deterministic tick | done |
| `engine/belief.py` — observations, ageing, sensor coverage, line of sight | done |
| `engine/projection.py` — what-if, route comparison with time and exposure | done |
| `engine/intents.py` — closed intent set, normalise → cache → rules | done (model fallback deferred) |
| `engine/errors.py`, `engine/query.py` — injection and the query path | done |
| `engine/eventlog.py` — append-only JSONL with engine and schema versions | done |
| `harness/run.py`, `harness/replay.py` — headless runs and replay from log | done |
| `scenarios/`, `probes/` — one scenario, two probes, fictional terrain | done |
| `api/` — FastAPI over the engine, session state, freeze semantics | done |
| `web/` — participant display: belief-layer map, query, freeze and blanking | done |
| `tools/e2e_check.py` — a real browser against a real server | done |

## Status

Specification complete against the August 2026 dissertation plan and the implementation guide, and
the engine runs. **Seven decisions remain open**, two of which block content work: the army echelon
and the domain for Study II. See
[docs/operations/open-decisions.md](docs/operations/open-decisions.md).
