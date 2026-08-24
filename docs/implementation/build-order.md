# Build order

The order matters more than the estimate. Steps 1-6 are about half the work and all of the value.
**Step 5 is a gate:** if the projections are not credible, nothing built after them matters.

## Phase 0 — before any code (2-3 weeks)

| Deliverable | Why it precedes code |
|---|---|
| **State-space document**, 4-6 states × 4 columns | The third column determines the logging schema, which cannot be fixed retroactively |
| **Echelon decision** | Determines terrain, cell size, speeds, order wording, probe difficulty |
| **Feature register**: branch points, visibility shadows, routes | Terrain is designed decision-points-first |
| **CMO runs and the parameter table** | Engine numbers are not invented |
| **`hmetad` parameter-recovery simulation** | The only sample-size figure a reviewer accepts without argument |
| **Pilot date in the calendar** | Decide it now. If it slips twice, the problem is scope, not schedule |

## Build sequence

1. **`WorldState` + `step()` + the determinism test.** The first test written runs a scenario twice
   with the same seed and compares logs byte for byte.
2. **`Observation` + `BeliefState` + ageing.** The layer most projects forget, and the study's core.
3. **One scenario YAML and its loader.**
4. **`projection` and `whatif`** — no language model, parameters by hand.
5. **GATE — expert validation.** Run the projections past the practitioner advisors. If they do not
   survive an expert's look, no later work helps. This is the cheapest kill point in the project.
6. **Logging + replay + headless harness.** Replay is tested here, not at the end.
7. **Intent parsing** — rule-based first; the model fallback only once a corpus of real questions
   exists.
8. **Frontend:** map, messages, query.
9. **Freeze, blanking, probes, ISA.**
10. **Error injection**, both types.
11. **Demo mode.**
12. **Calibration pilot, 5-8 people:** probe difficulty into 65-85 %, distortion detection threshold.
13. **Full pilot, 3-5 people**, with the pilot data analysed all the way to a result.

## The harness comes before the frontend

`harness/` runs a whole scenario with no browser. A scripted participant is YAML:

```yaml
participant: synth_01
condition: ai_mediated
actions:
  - {at_t: 300,  type: query,        text: "where is the enemy"}
  - {at_t: 920,  type: probe_answer, ref: p_fin03_01, choice: B, confidence: 3}
  - {at_t: 1250, type: query,        text: "what does the order mean for us"}
  - {at_t: 1400, type: decision,     action: withdraw, axis: north}
```

It emits the same log file a real session does. That gives regression tests (change the model, run
50 scenarios, see what moved), synthetic data for building the analysis pipeline and the power
simulation before the first participant, and a demonstration for supervisors that needs no clicking.

Developing the engine through a browser is roughly ten times slower, and it is the usual reason this
kind of project runs late. See [ADR-008](../adr/ADR-008-headless-harness-before-frontend.md).

## Frontend requirements

| Requirement | Note |
|---|---|
| Canvas map, fictional terrain PNG plus legend | No map tile services, no 3D |
| **Draw from `BeliefState`, never `WorldState`** | The same rule as the AI. Uncertainty visible: fresh observations sharp, old ones faded or a growing circle |
| **Screen blanking during freezes** | Mandatory. Without it the participant reads the answer off the map |
| Acknowledgement under 300 ms | The engine computes rather than generates — do not squander the advantage |
| No login | `?pid=p117&scenario=fin-def-03` is enough |
| Fullscreen enforcement, focus-loss logging, minimum viewport | Remote collection specifics |

## Effort — and a discrepancy to settle

The dissertation plan estimates **4-6 months part-time** for engine, parsing, map, interface,
logging and freeze mechanics. Decomposed into the steps above with their definitions of done, the
bottom-up total is **roughly 20 person-weeks, about 5 months full-time** — which part-time is 9-10
months, not 4-6.

Neither figure is wrong; they cover different scopes. The 4-6 month figure holds if these are left
out:

| Left out | Consequence |
|---|---|
| The content validator | Parts drift apart over months — a failure this project has already seen once |
| The debrief view | The debrief obligation falls back on manual work |
| The calibration battery's runner | Paper D loses its anchor |
| The admin view | Monitoring during collection becomes reading log files |
| Automated tests (determinism, leakage, blanking) | The determinism claim cannot be demonstrated in the methods section |

**Recommendation: do not cut these.** Cut scenario count and map polish instead, and accept an 8-10
month part-time arc — or buy 2-3 months of full-time work for the middle of the build, which brings
calendar time back to 5-6 months. **Decide before fixing the pilot date**, because after that the
pilot date is the only indicator that scope has escaped.

## The first two weeks

1. **Echelon decision and Study II's domain.** Everything else depends on them.
2. **State-space document.** Write the third column precisely enough that a developer can implement
   it without asking.
3. **`hmetad` recovery simulation.** A day's work, and the figure goes into the preregistration
   verbatim.
4. **Contacts:** expert advisors for parameters and terrain realism, a second coder for the open
   probe.
5. **Feature register** before a single line of terrain is generated.
6. **Pilot date.**

Only then the first line of code — and that line is the engine's state model, not the interface.
