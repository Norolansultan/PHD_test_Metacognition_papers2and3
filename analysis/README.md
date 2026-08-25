# Analysis

Not yet built. It belongs to build-order step 6 onward and depends on log files the harness already
produces, so it can be developed against synthetic data before the first participant (ADR-008).

Planned contents:

| File | Purpose |
|---|---|
| `derive.py` | Raw event stream to analysis table. A pure function: same log, same variables |
| `hmetad/` | HMeta-d fitting in R, regression variant for covariates |
| `power.R` | Parameter-recovery simulation — the sample-size figure for preregistration |
| `coding/` | Coding frame for the open Level-3 probe, and inter-rater agreement |

Derived variables are listed in [../docs/measurement/README.md](../docs/measurement/README.md).
Nothing is computed at collection time: every variable is derived from the log afterwards, so a
definition can change without re-collecting.
