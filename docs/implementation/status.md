# Build status

Tracked against [build-order.md](build-order.md). Updated when a step's definition of done is met.

| Step | State | Evidence |
|---|---|---|
| 0 · Phase 0 deliverables | **partial** | Feature register exists as terrain requirements; state-space document, echelon decision, CMO parameters and the power simulation are **not** done |
| 1 · `WorldState` + `step()` + determinism test | **done** | `tests/test_determinism.py` — two runs, same seed, byte-identical logs |
| 2 · `Observation` + `BeliefState` + ageing | **done** | `tests/test_belief.py` — ageing, supersession by existence, a landed platform stops observing |
| 3 · One scenario YAML and its loader | **done** | `scenarios/fin-def-03.yaml`, `engine/scenario.py` |
| 4 · `projection` and `whatif`, no model | **done** | `engine/projection.py`; route comparison with time and exposure |
| **5 · GATE — expert validation** | **BLOCKED** | Requires practitioner advisors. Nothing downstream is validated until this passes |
| 6 · Logging + replay + headless harness | **done** | `tests/test_replay.py` reproduces a session from its log alone |
| 7 · Intent parsing | **partial** | Rule tier and cache built; the model fallback waits for a real question corpus, per ADR-005 |
| 8 · Frontend | not started | The session viewer is a replay surface, not the participant interface |
| 9 · Freeze, blanking, probes, ISA | **partial** | Probe and ISA events are logged by the harness; blanking and freeze mechanics need the frontend |
| 10 · Error injection | **done** | `tests/test_injection.py`; `tests/test_exposure_route.py` covers the radio fallback |
| 11 · Demo mode | **done** for replay | `tools/make_viewer.py` produces the debug panel over real logs |
| 12-13 · Pilots | not started | Blocked by step 5 |

## What the gate at step 5 blocks

Every number the projection engine uses is a **planning placeholder**:

| Placeholder | Where | Replaced by |
|---|---|---|
| `SPEED_BY_TERRAIN`, `MOBILITY` | `engine/world.py` | CMO-derived movement rates |
| `SPEED_ASSUMPTION` | `engine/projection.py` | The planning figures a commander would actually use |
| `DRIFT_RATE_M_PER_S` | `engine/belief.py` | An estimate of how fast a position estimate decays in practice |
| Sensor ranges and errors | `scenarios/fin-def-03.yaml` | Real platform figures |
| Distortion magnitude | `scenarios/fin-def-03.yaml` | The calibration pilot |

Until the advisors have looked at the projections, the engine is correct but not credible, and
credibility is what the study rests on.

## Defects found and fixed while building

Recorded because they are the kind that would have survived into collection.

| # | Defect | Consequence had it survived |
|---|---|---|
| B-1 | Query normalisation left a trailing space from stripped punctuation, so the parse cache never hit | Two participants asking the same question in different punctuation would have received answers by different routes; the determinism claim would have been false |
| B-2 | No mobility difference between unit kinds: an infantry platoon moved as fast as a mechanised company | Movement times meaningless, and the route comparison with them |
| B-3 | `whatif_move` reported the horizon rather than the arrival time | Every option comparison would have shown the same number |
| B-4 | Exposure was measured from the cell under the unit, so a road through open ground read as covered | The risk half of the route trade-off would have been identically zero for both routes |
| B-5 | Units walked into the lake, because passability was checked at the current position rather than the next one | The lake would not have separated the corridors, and the forced branch would not have been forced |
| B-6 | The two corridors were not comparable in cost (89 min against 204 min) | The branch would have been choosable on distance alone, and exposure to the pulled channel would have been self-selected — the failure K-6 exists to prevent |

B-6 was found by the experimental-design gate in `tests/test_terrain.py`, which is the reason that
gate is a test rather than a paragraph.
