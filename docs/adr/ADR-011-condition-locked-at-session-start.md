# ADR-011: Condition Locked at Session Start

- **Status**: proposed
- **Date**: 2026-08-24
- **Deciders**:
- **Tags**: design, integrity, implementation

## Context

The mediation channel is constant within a participant because an organisation does not change its mediation channel mid-battle. That makes the phase-1 and phase-2 manipulations entangled, which is accepted and named as an AI-mediated versus human-mediated command chain.

## Decision

The condition is assigned at session start, written to the first log row, and immutable. No code path, researcher control, or URL parameter may change the channel mid-session outside demonstration mode.

## Consequences

### Positive
- The construct stays whole and the log is unambiguous about what each participant experienced.

### Negative
- A misassigned condition cannot be corrected mid-session; the session must be discarded.

### Neutral
- Demonstration mode may set the condition freely because it collects no data.

## Links
- [Architecture](../architecture/README.md)
- [Reconciliation](../architecture/reconciliation.md)
