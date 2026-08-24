# ADR-009: Separate Calibration Battery of 200 Items

- **Status**: proposed
- **Date**: 2026-08-24
- **Deciders**:
- **Tags**: measurement, metacognition, paper-d

## Context

Individual-level metacognitive efficiency requires hundreds of trials; a scenario task never produces them. The implementation guide does not mention a battery at all, and without one there is no gold standard against which Paper D's real-time proxies can be validated.

## Decision

Every participant completes a 200-item calibration battery in a separate session on its own time, before the scenario session. Binary or few-choice items with known ground truth, a confidence rating after each, difficulty targeted at 65-85 percent accuracy. Each study carries its own battery; there is no shared anchor across studies.

## Consequences

### Positive
- Individual M-ratio becomes estimable, Paper D gets its anchor, and no time is taken from the scenario session.

### Negative
- A second session per participant raises the recruitment cost and the attrition risk.

### Neutral
- Battery difficulty must be piloted; items outside the target accuracy band are replaced.

## Links
- [Architecture](../architecture/README.md)
- [Reconciliation](../architecture/reconciliation.md)
