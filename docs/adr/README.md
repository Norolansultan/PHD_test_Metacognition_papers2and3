# Architecture Decision Records

Decisions that cannot be reversed once collection starts without losing data. Each record states
what was decided, why, and what it costs.

| ADR | Decision | Status |
|---|---|---|
| [001](ADR-001-three-layer-information-model.md) | Three-layer information model | proposed |
| [002](ADR-002-python-engine-typescript-only-in-the-browser.md) | Python engine, TypeScript only in the browser | proposed |
| [003](ADR-003-immutable-state-and-explicit-seeded-randomness.md) | Immutable state and explicit seeded randomness | proposed |
| [004](ADR-004-templated-rendering-no-generative-text.md) | Templated rendering, no generative text on the participant path | proposed |
| [005](ADR-005-closed-intent-set-with-cached-parsing.md) | Closed intent set with cached three-tier parsing | proposed |
| [006](ADR-006-error-injection-in-the-presentation-layer.md) | Error injection in the presentation layer, two mutually exclusive types | proposed |
| [007](ADR-007-append-only-log-with-engine-and-schema-versions.md) | Append-only log with engine and schema versions | proposed |
| [008](ADR-008-headless-harness-before-frontend.md) | Headless harness before the frontend | proposed |
| [009](ADR-009-separate-calibration-battery-of-200-items.md) | Separate calibration battery of 200 items | proposed |
| [010](ADR-010-fictional-terrain-designed-for-the-experiment.md) | Fictional terrain designed for the experiment | proposed |
| [011](ADR-011-condition-locked-at-session-start.md) | Condition locked at session start | proposed |
| [012](ADR-012-private-repository-during-collection.md) | Private repository during collection, DOI at publication | proposed |

## The three that cost the data if they are wrong

1. **ADR-001.** If the AI reads world truth, the results are uninterpretable. This was a real defect
   in an earlier draft of this plan — see [reconciliation D-01](../architecture/reconciliation.md).
2. **ADR-007.** A logging schema without a version stamp means the first mid-collection model fix
   invalidates everything collected before it.
3. **ADR-008.** Building the frontend before the harness is the usual reason this kind of project
   runs late.
