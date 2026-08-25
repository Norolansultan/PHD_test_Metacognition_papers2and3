# The white cell display

The people portraying the situation need a different display from the one the
participant sees. They need layer 1: what is actually happening, what blue believes,
and the gap between the two. That gap is what they are portraying.

`web/control.html` is that display. It is served on a separate route, reads a separate
endpoint, and the participant bundle references neither — asserted in `tests/test_api.py`.

```
make api                       # serve on :8000
open localhost:8000/control.html?pid=wc001
```

## What it shows

| Element | Why |
|---|---|
| **Symbols by side and role** — friendly rectangles, hostile diamonds, role marks inside | A coloured dot tells a practitioner nothing. The frame and the fill are the first thing they read |
| **Strength bar under each symbol** | Attrition is the situation. It has to be visible without opening a panel |
| **Plotted course**, with heading and speed at the symbol | Where a unit is going matters more than where it is |
| **Weapon reach and sensor reach rings** | Contact is about to happen when the rings touch. That is the cue the white cell acts on |
| **Fire lines for the current tick**, with the impact marked | Makes the moment of contact legible at a glance |
| **Blue's believed picture**, dashed, with its age and uncertainty | **The point of the whole display.** Where the participant thinks the enemy is, next to where it is |
| **Message log** with closing ranges | Reads as a contact report, and it fills continuously |
| **Weather with visibility**, changing on schedule | A static sky is one more thing that reads as unreal |
| **Time acceleration** ×1 … ×30 and pause | 90 scenario minutes are not watched in real time |
| **Kilometre grid, scale bar, objective** | Gives the eye something to measure against |

## What made the earlier map read as unreal

The map the supervisors saw was a survey sheet with a fixed operational overlay drawn on
it: contours, place names, a line, a fallback line, seven neighbouring sector circles.
Nothing in it moved, nothing had a state, and nothing could be portrayed from it. Four
specific things were missing, and all four are now in the engine rather than in the
drawing:

1. **Nothing changed.** Units slid along waypoints and never met. The engine now resolves
   contact every tick, deterministically: units fire, take losses, slow down when engaged,
   and are destroyed at 12 % strength.
2. **Nothing had a state worth showing.** There was no strength, no heading, no speed, no
   status. There is now, and the display reads it rather than being told it.
3. **The sky was fixed.** Weather now changes on a schedule declared in the scenario.
4. **The believed picture was not drawn at all.** It is the one thing a white cell most
   needs, because it is what the participant is acting on.

## Calibration

Attrition is tuned so that a unit left in contact for the whole session is worn down but
not annihilated: the participant's decision must still exist when the order arrives at
40 minutes. `tests/test_combat.py` asserts both — that the situation develops, and that
nothing blue is destroyed before the decision point.

Every combat number in `engine/combat.py` is a **planning placeholder** until the expert
validation gate (build order step 5), like every other parameter in the model.

## Determinism

Contact is resolved against the state at the start of the tick, so the order units are
iterated in cannot decide who wins. Two runs with the same seed and the same participant
actions produce byte-identical logs — including every engagement, its range and its
damage. `tests/test_combat.py::test_engagement_is_deterministic` and
`tests/test_determinism.py` cover it.

This matters more than it looks: without it, two participants making the same decisions
would see different outcomes, and the condition comparison would be measuring the
simulation's noise.
