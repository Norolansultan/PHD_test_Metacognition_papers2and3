# Architecture

## Authority order

When two documents disagree, this is the order that settles it:

1. Ethics approval, the preregistration, and the framing rule
2. The measurement requirements in [docs/measurement](../measurement/README.md)
3. The architecture decision records in [docs/adr](../adr/README.md)
4. This document
5. Everything else

## The one principle

Three things are separate, and it is tempting to merge them:

| Layer | What it is | Who may read it |
|---|---|---|
| **1 · World truth** | What is actually happening in the simulation | The engine's `step()`; the researcher's tooling. **Never the AI channel. Never the frontend.** |
| **2 · Organisational knowledge** | What the commander, the other units, and the staff have observed and reported | The AI channel; the frontend; the human-mediated summary |
| **3 · Presented** | What this participant sees or is answered, in this condition | The participant |

**The AI always answers from layer 2, never from layer 1.** If the AI can read truth directly it is
omniscient, and the study is no longer about a mediated situation picture. This single rule
determines the data model, and it is the most important sentence in this repository.

## Data model

### World truth

```python
@dataclass(frozen=True)
class Entity:
    id: str
    side: str              # "blue" | "red" | "neutral"
    kind: str              # "infantry_platoon" | "drone" | "vehicle" | ...
    pos: tuple[float, float]
    heading: float
    speed: float
    strength: float        # 0.0-1.0
    supply: float
    status: str            # "moving" | "engaged" | "static" | "destroyed"

@dataclass(frozen=True)
class WorldState:
    t: int                 # scenario time, seconds
    entities: dict[str, Entity]
    terrain: TerrainGrid
    weather: Weather
    seed: int
```

Immutable. `step(state) -> WorldState` returns a new state, so a what-if is a copy run forward and
the original is untouched.

### Organisational knowledge

This is the layer most projects forget to build, and it is the study's core.

```python
@dataclass(frozen=True)
class Observation:
    id: str
    observer: str          # "drone_01" | "1st_platoon" | "adjacent_bn"
    subject: str           # id of the observed entity
    t_observed: int
    pos: tuple[float, float] | None
    pos_error: float       # metres, sensor accuracy
    attrs: dict            # strength, kind, heading, whatever was seen
    confidence: float      # 0.0-1.0
    channel: str           # "drone_feed" | "radio_report" | "sigint"

class BeliefState:
    """What 'blue' knows. Built from observations, never from truth."""
    observations: list[Observation]

    def best_estimate(self, subject: str, t_now: int) -> Estimate | None:
        """Freshest observation, extrapolated, with ageing uncertainty."""
```

**Observations never update.** They are records of a moment. A drone sighting at T+300 stays exactly
what it was; at T+900 it is ten minutes old.

**Ageing is an explicit function**, not a rendering convention:

```
uncertainty = pos_error + drift_rate * (t_now - t_observed)
```

Fresh sensor data is precise; old data is a guess. That is what makes drone feeds realistic and it
is what makes staleness measurable.

### Why this answers the research questions

| Question | How the model answers it |
|---|---|
| Where is the adjacent company? | From their last report, not their true position. A twenty-minute-old report answers as a twenty-minute-old report. |
| What happens when the drone lands? | No new observations arrive and uncertainty grows on its own. Scarcity is modelled, not scripted. |
| Human-mediated vs AI-mediated | The same `BeliefState`; only the assembler differs. Exactly the isolation Paper 1 requires. |
| Peer decisions (Paper A) | Observations whose `observer` is another commander and whose `subject` is that commander's own unit. |

### Presented

Rendering is a template, never a language model. Wording, hedging vocabulary, and length are
independent variables in this study; if a model chooses them, they vary between participants and the
manipulation is contaminated.

```
{subject}: last observed {age} ago, {source}.
Estimated position {pos}, uncertainty {uncertainty} m.
{projection_sentence}
```

The level of hedging is per-condition configuration, not a model's choice.

## The query path

Three stages, strictly separated:

```python
def answer(query: str, belief: BeliefState, world: WorldState,
           cfg: ConditionConfig) -> Answer:
    intent  = parse_intent(query)              # cache → rules → LLM fallback
    result  = execute(intent, belief, world)   # computation, never a model
    result  = maybe_inject_error(result, cfg)  # presentation-layer only
    return render(result, cfg.style)           # template, never a model
```

**`world` is passed for terrain, physics, and own-side state only.** Every non-own entity enters a
projection through a `ProjectionInput` built from `BeliefState`. A test perturbs red truth without
touching any observation and asserts that every projection is unchanged; if it fails, the channel
has become omniscient. See [reconciliation.md](reconciliation.md) X-01.

### Intents

A fixed, closed set:

| Intent | Parameters | Source |
|---|---|---|
| `locate` | subject | BeliefState |
| `strength` | subject | BeliefState |
| `eta` | subject, target_area | BeliefState + model |
| `project` | horizon_s, assumptions | model |
| `whatif` | action, horizon_s | model, copied state |
| `compare_options` | options[] | model |
| `peer_status` | peer_id | BeliefState |
| `order_interpretation` | order_ref | **Paper B's manipulation point** |
| `unknown` | — | fixed response |

Both the raw text and the parsed intent are logged. An `unknown` is data, not a bug: it names a
question that was not anticipated.

## Error injection

A separate layer that **never modifies world truth** — only what the computation returns.

| Kind | Mechanism | What it exposes |
|---|---|---|
| `projection_error` | the model is run with a wrong parameter (e.g. red speed × 0.6) | Delegated projection — a reliability question |
| `guidance_distortion` | `order_interpretation` returns a reading that differs from what the order meant | Command-chain drift — an integrity question |

Never both in the same trial. Proportions: ~55 % clean, ~20 % projection error, ~20 % guidance
distortion, 0 % both. Every answer carries `injection_id` or `null`.

**Command-chain drift is the most important cell in the dissertation.** The participant follows an
order that was never given. They break nothing, they can justify the decision coherently, and the
chain of command has drifted without anyone noticing.

## Logging

One append-only JSONL stream. No relational model — analysis is easier when everything is in one
time-ordered stream.

```json
{"t_scen": 1247, "t_wall": "2027-03-04T10:22:31Z", "session": "s0042",
 "participant": "p117", "condition": "ai_mediated", "seq": 88,
 "type": "query",
 "raw_text": "what happens if I move 2nd platoon north",
 "intent": "whatif", "params": {"unit": "blue_2pl", "dir": "north", "horizon_s": 1800},
 "engine_version": "0.4.2", "schema_version": "3", "model_seed": 88421,
 "injection": null, "parse_route": "rule", "latency_ms": 180}
```

Mandatory on every row: scenario time, wall time, session, participant, condition, sequence number,
**engine version**, **schema version**, seed.

Event types: `session_start`, `world_tick`, `observation_created`, `radio_message`, `query`,
`answer`, `probe_shown`, `probe_answer`, `confidence`, `isa_load`, `decision`, `decision_revert`,
`freeze_start`, `freeze_end`, `screen_blanked`, `focus_lost`, `attribution_free`,
`attribution_forced`, `debrief_shown`, `session_end`.

Three things that are not optional:

1. **Engine version on every row.** Adjust the model halfway through collection and you lose part of
   the data if the version is logged; you lose all of it if it is not.
2. **Replay.** A session must be reproducible from its log. Test this at the start, not at the end.
3. **Dual write.** Local file and server. A network drop must not swallow a session.

## Determinism

- One `Random(seed)` instance, passed explicitly. Never the global `random` module.
- No `datetime.now()` in the engine — everything is scenario time.
- Dictionary iteration order fixed where order matters.
- **First test written:** run the same scenario twice with the same seed and compare the logs byte
  for byte.

## Freeze semantics

During a freeze the scenario clock stops, the screen is blanked, and the query path refuses to
answer — a refused query is itself logged. Blanking is mandatory: without it the participant reads
the answer off the map and the probe measures the map, not their situation awareness.

## Domain neutrality

The engine knows nothing about fire or enemies. A threat is an interface:

```python
class ThreatModel(Protocol):
    def state_at(self, t: int) -> ThreatState: ...
    def exposure_for(self, unit: Entity, t: int) -> float: ...
```

Study I (army) and Study II (rescue) are content packages over the same engine. Building this
interface in phase 1 costs a day; omitting it costs a second project later.
