# Testing and evidence

Ordinary unit testing is not enough. This instrument has to prove six things a normal application
never has to prove.

| Test | How | Why |
|---|---|---|
| **Determinism** | Run the engine headless 100× with the same seed and inputs; compare log hashes | Condition means are not comparable without it. **This is the first test written** |
| **Replay** | Reconstruct a session from its log alone and compare | A log format that cannot replay cannot be fixed later; it means re-collecting |
| **Omniscience** | Perturb opposing-force truth without touching any observation; assert every projection is unchanged | If it fails, the AI is reading world truth and the results are uninterpretable ([ADR-001](../adr/ADR-001-three-layer-information-model.md)) |
| **Parse stability** | Run the pilot question corpus 3×; the same text must yield the same parameters | The determinism claim in the methods section ([ADR-005](../adr/ADR-005-closed-intent-set-with-cached-parsing.md)) |
| **Leakage** | Build the participant bundle, run headless, grep network traffic and the global object for world-truth, injection, and peer-content identifiers | Manipulation integrity |
| **Blanking** | Fullscreen and focus tests on three browsers | The most critical mechanism in remote collection |

Plus:

| Check | Note |
|---|---|
| **Golden run** | A stored input sequence and its expected event stream in version control; CI compares. Catches a content change that silently altered another decision point |
| **Zero-input run** | Run with no participant input at all. Every decision point must produce a non-decision, a state change, and a log entry. No window may close silently |
| **Injection exclusivity** | No trial carries both injection flags |
| **Log coverage** | Every proxy named in the state-space document is computable from a harness run's log |
| **Validator** | Rules V-01 to V-17 on every build ([scenario formats](../scenarios/README.md)) |

## Usability checks that cannot be automated

- Staleness is distinguishable at a glance: can a participant tell a five-minute-old answer from a
  thirty-minute-old one?
- Nothing in the interface anticipates a probe or a freeze.
- The debrief is comprehensible to someone who has just been deceived.

## Evidence for the methods section

Each of these produces something a reviewer will ask for:

| Claim in the paper | Evidence |
|---|---|
| "Responses were identical across participants" | Determinism and parse-stability test output |
| "The channel had no access to ground truth" | Omniscience test |
| "Probes were not anticipated" | Validator rule V-05 plus the usability check |
| "Probe difficulty was within the band" | Pilot accuracy distribution |
| "Exposure was reconstructable" | Replay of a sample session with injections |
