# ADR-008: Headless Harness Before the Frontend

- **Status**: proposed
- **Date**: 2026-08-24
- **Deciders**:
- **Tags**: testing, delivery, tooling

## Context

Developing an engine through a browser is roughly ten times slower than developing it under a test runner, and it is the usual reason research software schedules slip.

## Decision

A headless harness runs whole scenarios with scripted participants defined in YAML and emits the same log file a real session does. It is built before any interface work. It provides regression tests, synthetic data for the analysis pipeline before the first participant, and a demonstration that requires no clicking.

## Consequences

### Positive
- The analysis pipeline and the power simulation can be built and tested before recruitment.

### Negative
- Scripted participants are not real ones; the harness proves plumbing, not validity.

### Neutral
- The harness doubles as the demonstration path used by supervisors.

## Links
- [Architecture](../architecture/README.md)
- [Reconciliation](../architecture/reconciliation.md)
