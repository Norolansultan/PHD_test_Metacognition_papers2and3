# ADR-007: Append-Only Log with Engine and Schema Versions

- **Status**: proposed
- **Date**: 2026-08-24
- **Deciders**:
- **Tags**: logging, analysis, reproducibility

## Context

Both the model and the log format will change during a multi-month collection. Without version stamps, a mid-collection change invalidates everything collected before it.

## Decision

One append-only JSONL stream. Every row carries scenario time, wall time, session, participant, condition, sequence, engine version, schema version, and seed. Replay from the log is tested at the start of the project. Local and server writes are duplicated so a network drop cannot swallow a session.

## Consequences

### Positive
- A model change costs part of the data instead of all of it; sessions are reproducible; analysis reads one time-ordered stream.

### Negative
- Log rows are larger, and every new measure requires a schema change before the feature is built.

### Neutral
- Derived variables are computed from the raw stream by script, so a variable definition can change after collection.

## Links
- [Architecture](../architecture/README.md)
- [Reconciliation](../architecture/reconciliation.md)
