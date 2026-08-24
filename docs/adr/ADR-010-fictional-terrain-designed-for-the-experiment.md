# ADR-010: Fictional Terrain Designed for the Experiment

- **Status**: proposed
- **Date**: 2026-08-24
- **Deciders**:
- **Tags**: terrain, validity, opsec

## Context

Real terrain raises operational-security questions, cannot be shaped to the design, and cannot be published as an appendix. It also contributes prior local knowledge that varies between participants in a way nothing controls.

## Decision

Terrain is fictional, supplied as a raster with a legend, with continuous positions in metres sampled against it. It must contain a forced branch point (two equally plausible directions with insufficient information to choose), visibility shadows, two routes with different risk profiles, and distances that make time a real cost. The experimental-design gate is checked before the realism gate; where they conflict, the experimental gate wins and the deviation is reported.

## Consequences

### Positive
- Exposure to the pulled channel can be guaranteed, information scarcity is structural, and scenarios are publishable.

### Negative
- Terrain logic is asserted rather than inherited from real ground, so an expert realism review is required.

### Neutral
- Terrain is baked to hashed assets; nothing is generated at run time.

## Links
- [Architecture](../architecture/README.md)
- [Reconciliation](../architecture/reconciliation.md)
