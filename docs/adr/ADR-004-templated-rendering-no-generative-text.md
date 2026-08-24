# ADR-004: Templated Rendering, No Generative Text on the Participant Path

- **Status**: proposed
- **Date**: 2026-08-24
- **Deciders**:
- **Tags**: validity, rendering, llm

## Context

Wording, hedging vocabulary, and answer length are independent variables in this study. A language model that writes the answer varies all three between participants.

## Decision

Answers are rendered from templates. The hedging register is per-condition configuration. No generative reasoning appears anywhere on the participant path; the model's only permitted role is parsing (ADR-005).

## Consequences

### Positive
- Two participants asking the same question receive identical text, so the condition comparison is clean.

### Negative
- Answers read more mechanically than a generated equivalent would.

### Neutral
- Template authoring becomes content work with its own review.

## Links
- [Architecture](../architecture/README.md)
- [Reconciliation](../architecture/reconciliation.md)
