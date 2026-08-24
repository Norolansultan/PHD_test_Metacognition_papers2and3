# Measurement apparatus

Metacognition is the primary measure. Endsley's levels are measurement instruments here, not the
plot.

## Three things that must not be merged

| Concept | Measures | Estimator |
|---|---|---|
| **Sensitivity** | Does confidence discriminate correct from incorrect | meta-d′, AUROC2 |
| **Calibration** | Is the level systematically wrong | Brier, over/under-confidence |
| **Efficiency** | Sensitivity relative to performance | M-ratio |

AI can raise accuracy and destroy sensitivity at the same time. That is invisible in accuracy and
invisible in mean confidence; it appears only when these three are separated.

## Baseline first

Every participant completes a **200-item calibration battery** in a separate session before the
scenario. Sample target: **approximately 100 participants** — design for 80 usable, recruit 100-110,
because remote collection loses more than supervised collection. See
[calibration-battery.md](calibration-battery.md).

## Scenario probes

Many small probes, not a few large ones. Binary or few-choice, ground truth known, a 1-4 confidence
rating after each — never one rating per freeze.

| | Count | Sufficient for |
|---|---|---|
| Calibration battery, separate session | 200 | Individual M-ratio, Paper D anchor |
| Scenario, per participant | **15-25** | Load curve, within-session development |
| Scenario, per condition pooled | 600-1000 | Group-level condition comparison |

**Why 15-25 and not 2.** Read literally, "50-80 probes per condition" is a condition total, which at
40 participants per condition would be two probes each — contradicting the instruction to use many
small probes. Building to the stricter reading (a probe every 3-4 minutes in a 60-90 minute scenario)
satisfies both readings, produces a load curve, and makes within-condition development analysable.

**Placement rule.** Probes may fall inside decision windows, but never in the last 60 seconds of one
and never within 30 seconds of a projection answer. The first would compete with the moment of
commitment; the second would contaminate the feeling-of-rightness rating and the reading time.

**Difficulty 65-85 %** is a requirement, not a preference. Probes outside the band are replaced after
piloting.

## Rating types

| When | Rating | What it tells you |
|---|---|---|
| Before | Feeling of knowing / judgment of solvability | Whether the participant judges the item solvable |
| Immediately after answering | **Feeling of rightness** | Predicts how long thinking continues. A fluent AI answer raises it regardless of content — this is the direct measure of the fluency illusion |
| After | Retrospective confidence | The standard input to meta-d′ |
| At the end | Global self-assessment | Global versus local metacognition |

## The open Level-3 probe

Closed probes cannot measure the **uniqueness** of projections, because the answer space is given.
One open probe: *what do you expect to happen in the next 30 minutes, and why* — 30-60 seconds.

There are **three freezes**. An ISA load probe sits in every one; the open probe sits in two or three
depending on what the time budget survives in piloting. Closed probes are distributed through the
scenario rather than clustered in freezes.

| Derived measure | Computation |
|---|---|
| **Dispersion** | How much Level-3 answers vary between participants, by condition — semantic distance over embeddings |
| **Coverage** | How many distinct threats or developments the whole sample identified |
| **Lone observations** | How many participants identified something nobody else did |

Uniformity **with better accuracy** means AI reduced noise. Uniformity **with the same accuracy**
means distributed redundancy has been lost — and in a chain of command that is a safety finding, not
a null result.

**Resource condition:** this requires a coding frame and a second coder (Cohen's kappa). Settle it
before collection; a coding frame cannot be retrofitted to data collected without one.

## Cognitive load

- **ISA probe (1-5) in every freeze.** Two seconds, and it produces a load curve across the session.
- **NASA-TLX only afterwards**, as an anchor. Never mid-session.

The most interesting analysis, and the one closest to CATCH's centre: **at what load level does
metacognitive efficiency collapse.** That inflection is what an adaptive system would be tuned to,
which makes this an input to Paper D rather than a by-product.

## Detection measures

A channel manipulation without a detection measure is half a study. Three parts, in this order, with
no way back:

1. **Free attribution** — *what influenced your decision* — before any source is named
2. **Forced recognition** — a list of factors, rate the influence of each
3. **Behavioural shift** — independent of 1 and 2

The order is a build requirement: the questionnaire is one-way, earlier answers are not reachable
again, and the list in step 2 must not be visible during step 1. If it leaks, free attribution is
ruined and cannot be collected again.

**The most interesting cell: large shift, zero attribution.** The participant changed what they did
and does not name the channel as an influence.

## Reactivity — a serious caveat

Asking for confidence is itself a cognitive-forcing intervention: it compels metacognitive
inspection that would not otherwise occur. This is reported as a limitation regardless of what is
done about it.

Both mitigations, not one:

1. **A sparse-probe group, n ≈ 20, not crossed with the main design.** Two or three probes for the
   whole session, used only to check whether their query rate, verification behaviour, and decision
   latency differ from the densely probed participants. Crossing it would halve the cells.
2. **Proxy weighting in high-tempo passages**, where a probe would disturb the most.

## Metacognitive states

Defined **relatively** — as a departure from the person's own baseline (which the 200-item battery
supplies) or as a percentile in the sample. The taxonomy then transfers between studies even when
the numbers do not.

| State | Signature |
|---|---|
| Calibrated control | high sensitivity, small bias, verification proportional to uncertainty |
| **Delegated projection** | high confidence, no verification, answer equals the AI's |
| **Fluency illusion** | high feeling of rightness, short acceptance latency, no own what-ifs, justifies in the AI's words |
| Collapsed monitoring | confidence distribution flattens, sensitivity → 0, load-driven |
| Unproductive doubt | low confidence even when correct, excess verification |
| **Productive conflict** | low feeling of rightness, active checking, hypothesis change |
| Socially induced certainty | confidence proportional to peer consensus (Study II only) |

**Transitions matter more than states.** The log yields a trajectory, not snapshots. The success
measure for an adaptive system is how often it moves a user from delegated projection or fluency
illusion into productive conflict.

### The state-space document comes before the code

Four to six states × four columns: definition | offline detection | **online proxy and the log
fields it needs** | what the AI should do. The fourth column may be a guess. **The third determines
the logging schema, and a logging schema cannot be fixed retroactively** — which makes this a
blocking deliverable, not a design note.

## Paper D proxies

meta-d′ is computed after the fact and cannot drive a real-time system. So the expensive gold
standard is collected offline (the battery) and cheap behavioural proxies online in the same
session — and validating the proxies against the gold standard **is** writing the algorithm.

| Proxy | Log fields that make it computable |
|---|---|
| Verification behaviour | `verification` events, source referenced, interval since the projection |
| Query diversity | variation in `params` across successive projections |
| Hypothesis rejection | whether an alternative to the AI's proposal was tested |
| **Acceptance latency** | latency to next action plus confidence. Short latency with high confidence is the warning sign |
| Decision reversal | `decision_revert` and its timing |
| Confidence-verification decoupling | derived: the correlation collapses |

**Transfer rule: features transfer, coefficients do not.** The model is fitted per regime. That
yields a claim which is itself a contribution — an adaptive system needs either regime detection or
separate calibration per workspace; one generic metacognition model cannot be fielded. The claim is
empirically supportable **only if two regimes are collected**.

## Session structure

**Session A — calibration battery.** See [calibration-battery.md](calibration-battery.md).

**Session B — scenario**

| # | Block | Duration | Notes |
|---|---|---|---|
| 1 | Consent, same identifier | 5 min | Condition assigned and locked here (ADR-011) |
| 2 | Interface training | 10-12 min | Map, query field, confidence rating, freeze mechanics. **Freeze timings are never mentioned** |
| 3 | Practice scenario | 8 min | Different terrain, `practice = true` |
| 4 | **Scenario** | 60-90 min | 15-25 probes, 3 freezes (ISA + open L3) |
| 5 | **Detection battery** | 8 min | One-way: free attribution → forced recognition |
| 6 | NASA-TLX, background | 5 min | TLX only here |
| 7 | **Debrief** | 5 min | What was manipulated, and how their decisions related to the order |

Session B totals roughly 1 h 45 min to 2 h 15 min. In remote collection that is the ceiling.

**The order is binding.** Debrief is last because it reveals the manipulation and would spoil every
measure before it.

## Sample size and preregistration

- **Approximately 100 participants.** Design for 80 usable, recruit 100-110.
- The defensible number comes from **a parameter-recovery simulation with `hmetad`** using the
  expected values. A day's work, and the only figure a reviewer accepts without argument.
- 100 participants gives main effects reliably and an interaction only if it is large. **Do not build
  either paper's headline claim on an interaction.**
- **Preregister** (OSF or AsPredicted). It is free, a day's work, and it matters most precisely where
  deception and error injection are involved — the place a reviewer would otherwise suspect
  post-hoc fitting. The recovery simulation goes in verbatim.
