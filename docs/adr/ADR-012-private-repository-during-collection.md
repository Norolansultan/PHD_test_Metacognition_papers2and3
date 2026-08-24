# ADR-012: Private Repository During Collection, DOI at Publication

- **Status**: proposed
- **Date**: 2026-08-24
- **Deciders**:
- **Tags**: ethics, contamination, publication

## Context

The target population is technically capable. Published injection proportions and probe answer keys before or during collection would contaminate the sample; one participant searching the repository is enough.

## Decision

The repository stays private for the duration of collection. Secrets live in environment secrets, never in the repository, and model credentials exist only in the backend. At publication the repository is made public with Zenodo archiving, a DOI, and a CITATION.cff.

## Consequences

### Positive
- Sample integrity is protected without giving up open publication.

### Negative
- Collaborators need explicit access, and pre-publication review of materials is harder.

### Neutral
- Scenario files are written to be publishable from the start, so publication is a visibility change rather than a rewrite.

## Links
- [Architecture](../architecture/README.md)
- [Reconciliation](../architecture/reconciliation.md)
