# ADR-006: Error Injection in the Presentation Layer, Two Mutually Exclusive Types

- **Status**: proposed
- **Date**: 2026-08-24
- **Deciders**:
- **Tags**: manipulation, ethics, logging

## Context

The study needs two distinct failures: a model that is wrong (reliability) and an interpretation that drifts from the order actually given (integrity). Confounding them makes neither interpretable.

## Decision

Injection never modifies world truth; it modifies only what the computation returns. `projection_error` runs the model with a wrong parameter; `guidance_distortion` returns an interpretation that differs from the order's meaning. The two never occur in the same trial. Proportions are approximately 55 percent clean, 20 percent projection error, 20 percent distortion, 0 percent both. Every answer carries an injection id or null. Distortion direction is systematic within a scenario and balanced across scenarios.

## Consequences

### Positive
- Exposure is exactly reconstructable for debriefing and for ethics review; the two constructs stay separable.

### Negative
- Injection magnitude must be calibrated in a pilot, and an uncalibrated magnitude wastes the cell.

### Neutral
- Distortion reaches only participants who ask for an interpretation unless a radio fallback delivers it; that fallback is specified separately.

## Links
- [Architecture](../architecture/README.md)
- [Reconciliation](../architecture/reconciliation.md)
