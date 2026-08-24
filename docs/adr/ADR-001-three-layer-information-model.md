# ADR-001: Three-Layer Information Model

- **Status**: proposed
- **Date**: 2026-08-24
- **Deciders**:
- **Tags**: information-model, validity, core

## Context

The study manipulates how a situation picture is mediated. If the AI channel can read simulation truth directly, it is omniscient, and the manipulated variable is no longer mediation. An earlier draft of this plan defined only two layers and let the projection engine run against world state, which is exactly that failure.

## Decision

Three layers are separate: world truth, organisational knowledge (`BeliefState` built from timestamped `Observation` records), and what is presented. The AI channel and the frontend read layer 2 only. World state is passed into the query path for terrain, physics, and own-side state; every non-own entity enters a projection through a `ProjectionInput` constructed from beliefs. A test perturbs opposing-force truth without changing any observation and asserts that projections are unchanged.

## Consequences

### Positive
- The channel's answers are interpretable as mediation. Staleness, sensor coverage, and peer reports become modelled consequences rather than scripted content.

### Negative
- Every feature that touches information must decide which layer it reads from, which is slower to build than reading truth.

### Neutral
- The layering does not by itself make the scenario realistic; that is a separate validation gate.

## Links
- [Architecture](../architecture/README.md)
- [Reconciliation](../architecture/reconciliation.md)
