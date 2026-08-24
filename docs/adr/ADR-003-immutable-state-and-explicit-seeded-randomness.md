# ADR-003: Immutable State and Explicit Seeded Randomness

- **Status**: proposed
- **Date**: 2026-08-24
- **Deciders**:
- **Tags**: determinism, engine, testing

## Context

Condition means are not comparable unless every participant's world evolves identically for identical inputs. Hidden global randomness and wall-clock reads are the usual causes of drift.

## Decision

`WorldState` is frozen and `step(state)` returns a new state. One `Random(seed)` instance is passed explicitly; the global random module is never used. No wall-clock reads inside the engine. Dictionary iteration order is fixed where it matters. The first test written runs a scenario twice and compares logs byte for byte.

## Consequences

### Positive
- What-if projection is a state copy run forward, with no risk of corrupting the live run. Regression testing becomes a byte comparison.

### Negative
- Copying state costs memory and some care about hot paths.

### Neutral
- Determinism is a property of the engine, not of the interface, and must be re-checked whenever a dependency is added.

## Links
- [Architecture](../architecture/README.md)
- [Reconciliation](../architecture/reconciliation.md)
