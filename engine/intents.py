"""Question to parameters. Closed intent set (ADR-005).

Three tiers: normalise, cache, rule-based parser. The model fallback is a stub
here and is only built once a corpus of real questions exists (build order step 7).
An unmatched question returns UNKNOWN and is logged verbatim — that is data, not
a bug.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

INTENTS = (
    "locate",
    "strength",
    "eta",
    "project",
    "whatif",
    "compare_options",
    "peer_status",
    "order_interpretation",
    "unknown",
)


@dataclass(frozen=True)
class Intent:
    name: str
    params: dict = field(default_factory=dict)
    route: str = "rule"  # "cache" | "rule" | "llm" | "failed"


_SYNONYM = {
    "enemy": "red_coy_x",
    "hostile": "red_coy_x",
    "opfor": "red_coy_x",
    "red": "red_coy_x",
    "1st platoon": "blue_1pl",
    "first platoon": "blue_1pl",
    "1 pl": "blue_1pl",
    "2nd platoon": "blue_2pl",
    "second platoon": "blue_2pl",
    "2 pl": "blue_2pl",
    "drone": "blue_drone_a",
    "uav": "blue_drone_a",
    "adjacent": "adjacent_bn",
    "neighbour": "adjacent_bn",
    "neighbor": "adjacent_bn",
}

_DIRECTION = {"north": (0, -1), "south": (0, 1), "east": (1, 0), "west": (-1, 0)}


def normalise(text: str) -> str:
    t = text.lower().strip()
    t = re.sub(r"[^\w\s]", " ", t)
    t = re.sub(r"\s+", " ", t)
    return t.strip()


def _subject(t: str) -> str | None:
    for phrase in sorted(_SYNONYM, key=len, reverse=True):
        if phrase in t:
            return _SYNONYM[phrase]
    return None


def _horizon(t: str, default: int = 1800) -> int:
    m = re.search(r"(\d+)\s*(min|minute|minutes)", t)
    if m:
        return int(m.group(1)) * 60
    m = re.search(r"(\d+)\s*(h|hour|hours)", t)
    if m:
        return int(m.group(1)) * 3600
    return default


class IntentParser:
    """Deterministic by construction: the cache is keyed by normalised text, so
    identical wording yields identical parameters for every participant."""

    def __init__(self) -> None:
        self._cache: dict[str, Intent] = {}

    def parse(self, text: str) -> Intent:
        key = normalise(text)
        if key in self._cache:
            hit = self._cache[key]
            return Intent(hit.name, dict(hit.params), route="cache")
        intent = self._rules(key)
        self._cache[key] = intent
        return intent

    def _rules(self, t: str) -> Intent:
        subj = _subject(t)

        if re.search(r"\b(order|command|withdraw|kelo)\b", t) and re.search(
            r"\b(mean|means|meaning|interpret|for us|do)\b", t
        ):
            return Intent("order_interpretation", {"order_ref": "vague_order"})

        if re.search(r"\bwhat happens if\b|\bwhat if\b|\bif i move\b|\bshould i move\b", t):
            direction = next((d for d in _DIRECTION if d in t), None)
            return Intent(
                "whatif",
                {
                    "unit": subj or "blue_1pl",
                    "dir": direction or "north",
                    "horizon_s": _horizon(t),
                },
            )

        if re.search(r"\bcompare\b|\bwhich route\b|\bwhich option\b|\beast or west\b", t):
            return Intent("compare_options", {"options": ["west_road", "east_track"],
                                              "horizon_s": _horizon(t)})

        if re.search(r"\bhow long\b|\beta\b|\bhow soon\b|\bwhen will\b", t):
            return Intent("eta", {"subject": subj or "red_coy_x", "target_area": "kelo"})

        if re.search(r"\bwhere will\b|\bproject\b|\bin \d+ minutes\b|\bnext \d+\b", t):
            return Intent("project", {"subject": subj or "red_coy_x",
                                      "horizon_s": _horizon(t)})

        if re.search(r"\bstrength\b|\bhow strong\b|\bhow many\b|\bcombat power\b", t):
            return Intent("strength", {"subject": subj or "red_coy_x"})

        if subj == "adjacent_bn" or re.search(r"\bpeer\b|\badjacent\b|\bflank unit\b", t):
            return Intent("peer_status", {"peer_id": "adjacent_bn"})

        if re.search(r"\bwhere\b|\blocate\b|\bposition\b|\bcontact\b", t):
            return Intent("locate", {"subject": subj or "red_coy_x"})

        return Intent("unknown", {}, route="failed")
