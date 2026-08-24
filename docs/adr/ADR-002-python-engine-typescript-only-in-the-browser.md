# ADR-002: Python Engine, TypeScript Only in the Browser

- **Status**: proposed
- **Date**: 2026-08-24
- **Deciders**:
- **Tags**: language, engine, tooling

## Context

The engine must be deterministic, testable without a browser, re-runnable years later, and adjacent to the analysis stack (HMeta-d in R, embeddings for the open probe). An earlier draft chose TypeScript everywhere for single-language simplicity.

## Decision

`engine/` is a pure Python library with no web, HTTP, or language-model dependencies, tested with pytest. FastAPI is a thin boundary over it. TypeScript is used only for the browser frontend.

## Consequences

### Positive
- Determinism is provable in a test harness; the analysis pipeline shares the engine's language; the engine outlives the interface.

### Negative
- Two languages in the repository and a serialisation boundary between them.

### Neutral
- Interface technology stays replaceable, which was the intent either way.

## Links
- [Architecture](../architecture/README.md)
- [Reconciliation](../architecture/reconciliation.md)
