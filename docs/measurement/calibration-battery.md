# The 200-item calibration battery

**Every participant completes a 200-item battery before they ever see the scenario.** It runs as a
separate session, on its own time, and it establishes that participant's metacognitive baseline.

This is the only place individual-level metacognitive efficiency can be estimated. A scenario task
never produces enough trials, and without an individual anchor Paper D — the validation of
real-time behavioural proxies against an offline gold standard — has nothing to validate against.
See [ADR-009](../adr/ADR-009-separate-calibration-battery-of-200-items.md).

## Specification

| Property | Value | Why |
|---|---|---|
| Items per participant | **200** | Enough for a stable individual M-ratio; short enough for one sitting |
| Format | Binary or few-choice, ground truth known | Type-2 sensitivity requires a correct/incorrect classification |
| Confidence | Rating after **every** item, 1-4 | Per-item, never per-block |
| Target accuracy | **65-85 %** | A hard requirement, not a preference: with no errors, sensitivity cannot be computed at all |
| Duration | 30-45 min | ~10 s per item plus instruction and practice |
| Timing | Separate session, before the scenario session | Keeps the scenario session inside a bearable length |
| Domain | One battery per study | Different participants, no shared anchor across studies |

## Session A — the battery

| # | Block | Duration | Notes |
|---|---|---|---|
| 1 | Consent, identifier from URL parameter | 5 min | No login |
| 2 | Instructions and practice items | 5 min | Confidence scale trained to a demonstrated criterion |
| 3 | **200 items, confidence after each** | 30-45 min | Breaks permitted between blocks of 50 |

## What is estimated from it

| Quantity | Estimator | Used by |
|---|---|---|
| Type-2 sensitivity | meta-d′, AUROC2 | Individual baseline, covariate |
| Calibration | Brier score, over/under-confidence | Individual baseline |
| **Metacognitive efficiency** | **M-ratio (meta-d′/d′)** | **Paper D's gold standard** |

Estimation uses HMeta-d via the `hmetad` package in R. Individual differences and covariates go
**inside the model** using the regression variant, not as a post-hoc correlation — hierarchical
shrinkage would attenuate the relationship and make a real effect invisible.

## Difficulty calibration is a gate

An item bank whose accuracy sits outside 65-85 % cannot produce a sensitivity estimate. Items are
piloted, and those outside the band are replaced before collection. This is a build gate, not a
tuning preference.

## Why the battery is separate, and what it costs

Running 200 items inside the scenario session would add 30-45 minutes to an already long sitting and
would contaminate the scenario with a long metacognitive-monitoring warm-up.

The cost is a second session per participant: higher recruitment friction and an attrition point
between the two sessions. Mitigations: schedule both at recruitment, make the battery the first of
the two, and treat a participant who completes only the battery as a partial record rather than a
loss — their baseline still contributes to the item-bank calibration.

## Relationship to the scenario probes

| | Calibration battery | Scenario probes |
|---|---|---|
| Items | 200 per participant | 15-25 per participant |
| Purpose | Individual baseline, Paper D anchor | Condition comparison, load curve |
| Level | Individual | Group |
| Pooled per condition | — | 600-1000 trials |

Individual meta-d′ comes **only** from the battery. The scenario yields group-level condition
comparisons and the within-session load curve, and it is not asked to do more than that.
