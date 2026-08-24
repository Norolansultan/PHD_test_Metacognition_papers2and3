# Risks

## Risks the architecture answers

| Risk | Answer |
|---|---|
| The AI reads world truth | Three-layer model plus the omniscience test in CI ([ADR-001](../adr/ADR-001-three-layer-information-model.md)) |
| A mid-collection model fix invalidates everything before it | Engine and schema versions on every log row ([ADR-007](../adr/ADR-007-append-only-log-with-engine-and-schema-versions.md)) |
| Parse variation eats determinism | Three-tier parser with a cache; rule coverage target ≥ 80 % in the pilot; route logged |
| Content parts drift apart over months | Validator V-01 to V-17 on every build, failing the build |
| Losing a session to a technical fault | Append-only queue, dual write, replay, interrupted sessions analysable to the point of interruption |
| Feature creep — a helpful new notification | V-05 and V-09 as automated tests. Helpful notifications are forbidden by default |
| Self-selected exposure to pulled guidance | Forced branch, radio fallback, route as covariate |
| Building the interface first and running late | The harness precedes the frontend ([ADR-008](../adr/ADR-008-headless-harness-before-frontend.md)) |

## Risks the architecture does not answer

| Risk | Reality |
|---|---|
| **Probe difficulty misses 65-85 %** | Sensitivity becomes incomputable. The pilot must replace items; this is a gate, not tuning |
| **Distortion magnitude too small or too large** | Too small does not separate from human dispersion; too large is detected as inconsistency. Three magnitudes, 5-8 people each. This is the pilot's most important job |
| **Reactivity produced the result** | Sparse-probe group (n ≈ 20) plus proxy weighting. Reported as a limitation regardless |
| **Recruiting ~100 officers, twice each** | The battery is a second session. Schedule both at recruitment; a battery-only participant is a partial record, not a loss |
| **Expert availability** | The longest lead time in the project. Parameters, terrain realism, and the order's vagueness need the same people. Book them together |
| **A second screen or second device** | Cannot be prevented. Measured and reported |
| **Ethics committee and MPKK** | Detection-and-protection framing, preregistration, and the debrief view as software rather than paperwork |
| **CMO's land-warfare model is rejected** | Confirm before parameters are frozen; fallback is expert derivation reported as a limitation |
