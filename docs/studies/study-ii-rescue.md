# Study II — rescue, paper A

Horizontal influence: what happens when other commanders' decisions are fed into a projection as
model input rather than presented as opinion.

**A separate collection, a separate sample, its own baseline, and its own
[200-item calibration battery](../measurement/calibration-battery.md).**

## Conditions

| Condition | What the participant receives | What it isolates |
|---|---|---|
| **No social information** | Radio net, own units, projection engine | Baseline: interpretation made alone |
| **Peer decisions raw** | The same, plus a list or timeline of other sector commanders' choices | Social information **as opinion** — assessable, rejectable |
| **Peer decisions as projection input** | The same, but peers' choices enter the model as input and appear only in its output | Social information **as model input** — it does not look like an opinion |

**Hypothesis:** social information embedded in a projection bypasses critical evaluation, because it
is presented as an input to a model rather than as someone's view.

The same mechanism as Paper B, in the horizontal direction. The synthesis chapter's contribution is
the comparison: **does vertical steering bypass critical evaluation more easily than horizontal
steering, when both are embedded in a projection?**

Peer decisions are `Observation` records whose `observer` is another commander and whose `subject`
is that commander's own unit. One mechanism, not a separate content system — see
[reconciliation D-07](../architecture/reconciliation.md).

Theory: informational versus normative influence, information cascades (Bikhchandani et al. 1992;
Çelen & Kariv 2004), the Judge–Advisor System, Schöbel et al. 2016, Logg et al. 2019. Nearest
comparison: *Drivers and influence of social conformity on decision making in human–AI teams*
(Sci Rep 2026).

## The incident

A late-summer wildland fire. The participant commands **sector BRAVO**, roughly 4 × 4 km inside a
30 × 30 km incident area. The protected object is a small industrial site about a kilometre behind
the main line; losing it is the failure condition. The main line runs along an esker ridge, and the
road on that ridge is both the supply route and the escape route.

Neighbouring sectors work 5-15 km away. **That distance is designed:** copying their solution is a
genuine inferential leap, not an observation.

## Roles

| Role | Who | Visible as |
|---|---|---|
| Incident commander | scripted | Radio |
| Operations chief | scripted | Assigns the sector task |
| **Sector commander BRAVO** | **the participant** | — |
| Strike teams A, B, C | agents | Under command: position, water, task, exposure |
| Engine, tender, dozer | agents | Under command |
| Neighbouring sectors | agents | Radio, map, **the source for conditions 2 and 3** |
| Unmanned aircraft | agents | Coverage windows, observations |

Cognitive styles — methodical, analytical, aggressive, follower — drive how each neighbour's
decisions develop and how coherent they look. That is the content of conditions 2 and 3.

## Physics

These are the rescue domain's projection parameters, validated by the same expert gate as the army
parameters.

| Quantity | Planning assumption |
|---|---|
| Movement, road / off-road | 40-60 km/h · 3-4 km/h plus setup time |
| Fire spread | Head fire 0.3-2 km/h by fuel, wind and slope; faster in the open and in a wind-driven run |
| Water | Consumed per task; resupply tied to a trafficable road |
| Repositioning within the sector | 5-15 min — a real cost, but a payable one |
| Crossing a sector boundary | Effectively an irreversible commitment |

In 88 minutes the fire moves 0.5-3 km: a large fraction of a 4 km sector, under 10 % of a 30 km area.
That is why there are two scales, and why the threat feels like it is developing.

## Terrain requirements

| Feature | Role |
|---|---|
| Esker ridge with a road along the crest | The line's anchor, observation north, the supply route |
| The industrial site, south-central | **The objective.** Loss is the failure condition |
| Prepared fallback line, 400 m to the rear | The conservative option |
| Northern open approach | The expected main run, fast |
| Eastern covered approach | Smoulders and creeps — until the wind turns |
| **South-western rear ground** | Assumed safe because the peat is wet. **This is where the shift bites** |
| **Forced branch point** | Two equally plausible directions to commit a strike team, with insufficient information to choose without a projection |
| **Visibility shadows** | The eastern development and the rear ground are unobservable without reconnaissance |

## The wind shift

The wind veers about 60° and freshens. The eastern covered approach aligns with the new wind, runs,
and **hooks around the eastern end of the line** toward the supply route and the rear ground. Fire
does not appear behind the line — it goes around it.

In the earlier design this invalidated both the guidance and the precedents. The guidance
manipulation is gone, but **invalidating the precedents matters more now**: it is the only way to
have both valid and stale social information inside one session.

| Condition | What the shift does to it |
|---|---|
| 1 | Only their own interpretation goes stale |
| 2 | Peer decisions carry timestamps. A careful reader notices they were made under the old wind; a copier does not. **The timestamp is the cue that separates them.** |
| 3 | Peers' choices arrive as model input. The timestamp is not visible in the same way, because the result is presented as the model's. **This is the hypothesis, and the whole reason the condition exists.** |

Timing is fixed and identical for everyone regardless of prior actions. Matched timing is the
condition for every group comparison.

## Decision points and precedent validity

The scenario is continuous. A decision point is a moment when pressure focuses, not a moment when
the world starts. **Precedent validity is a within-subject factor and therefore free**: the same
participant meets apt, misleading, absent, and invalidated precedents.

| # | Situation | Precedent | What it measures |
|---|---|---|---|
| 1 | Sector task, first commitment | absent | Baseline |
| 2 | Pressure to commit the reserve | apt | Following a good example |
| 3 | Opportunity window, neighbours audibly committing to direct attack | **misleading** — their flank has a road as an escape route, BRAVO's does not | Conformity under tempo |
| 4 | Strike team C reports degraded visibility in the east | absent | A weak signal against an established picture |
| 5 | **Forced branch:** two equally plausible directions | apt | Guaranteeing exposure; asking behaviour |
| 6 | A neighbour's reporting cycle goes quiet | absent | Noticing an absence |
| 7 | The eastern development becomes retrievable | apt | Belief revision against confirmation pressure |
| 8 | **The wind shift** | **invalidated** | Detection; the frame changing |
| 9 | Exposure undeniable, rear ground threatened | apt | Acting on stale or on current information |
| 10 | Committing into poorly observed rear ground | absent | **Recognising one's own ignorance.** The projection returns almost nothing, by design |
| 11 | Short window to check the run; neighbours visibly attacking | **misleading** — stale rationale | Opportunity and conformity |
| 12 | Late information makes an earlier commitment look wrong | apt | Error detection, sunk cost |
| 13 | Handover, free text | absent | Situation-awareness capture at closure |

Point 10 is the design's best feature and the easiest to lose during implementation. Under the
sensor model it stays empty by construction — no sensor has covered that ground — but a test asserts
it anyway.

**Window expiry:** units continue on their last orders, the radio states what is now happening, and a
non-decision is logged with the rule that fired. A non-decision is a finding, not a missing value.
The visible per-decision countdown is **removed** — it belonged to a time-pressure manipulation that
no longer exists. The scenario clock runs in the header and time remaining is logged.

## Open: error injection in Study II

The two injection types are *projection wrong* and *guidance distorted*. The second has no direct
horizontal counterpart, because there is no vertical order.

**Proposal requiring a decision:** the horizontal counterpart is a projection whose result is skewed
by peer consensus — the model is right, the peer set fed into it is wrong, and the output still looks
like the model's. That would test the hypothesis directly and would parallel Paper B's drift
structurally.

**Alternative:** restrict Study II to projection error and leave the skew inside the scenario
(misleading precedents at points 3 and 11). Safer ethically and simpler to build, but it loses the
direct parallel to Paper B.

**Decide before writing content**, because it determines both the log flags and the debrief text.
See [open decisions](../operations/open-decisions.md).
