# ADR-005: Closed Intent Set with Cached Three-Tier Parsing

- **Status**: proposed
- **Date**: 2026-08-24
- **Deciders**:
- **Tags**: llm, determinism, query

## Context

Free text input is required, but a language model is not deterministic and identical questions must yield identical answers. The implementation guide allows parsing to be rule-based or model-based without resolving the tension.

## Decision

A closed set of nine intents. Parsing runs normalise, then a cache keyed by normalised text, then a rule-based slot parser, then a temperature-zero model fallback whose result is written to the cache, then a fixed clarification request. Both raw text and parsed intent are logged with the parse route. An `unknown` result is data, not a bug.

## Consequences

### Positive
- Identical question text yields an identical answer for every participant for the whole collection, and that claim is defensible in the methods section.

### Negative
- Two differently worded questions may still parse differently; parse variation must be reported rather than hidden.

### Neutral
- The rule parser's coverage becomes a measurable build target (at least 80 percent of piloted questions).

## Links
- [Architecture](../architecture/README.md)
- [Reconciliation](../architecture/reconciliation.md)
