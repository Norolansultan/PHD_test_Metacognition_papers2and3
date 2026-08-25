"""Append-only JSONL event log (ADR-007).

Every row carries scenario time, wall time, session, participant, condition,
sequence, engine version, schema version, and seed. A session must be
reproducible from its log alone; tests/test_replay.py proves it.
"""

from __future__ import annotations

import json
from dataclasses import asdict, is_dataclass
from typing import Any

from engine.version import ENGINE_VERSION, SCHEMA_VERSION

EVENT_TYPES = (
    "session_start", "world_tick", "observation_created", "radio_message",
    "engagement", "unit_destroyed", "weather_change",
    "query", "answer", "probe_shown", "probe_answer", "confidence", "isa_load",
    "decision", "decision_revert", "freeze_start", "freeze_end", "screen_blanked",
    "focus_lost", "attribution_free", "attribution_forced", "debrief_shown",
    "session_end",
)


def _plain(o: Any) -> Any:
    if is_dataclass(o) and not isinstance(o, type):
        return {k: _plain(v) for k, v in asdict(o).items()}
    if isinstance(o, dict):
        return {str(k): _plain(v) for k, v in o.items()}
    if isinstance(o, (list, tuple)):
        return [_plain(v) for v in o]
    if isinstance(o, float):
        return round(o, 3)
    return o


class EventLog:
    def __init__(
        self, session: str, participant: str, condition: str, seed: int,
        wall_clock: str = "1970-01-01T00:00:00Z",
    ) -> None:
        self.session = session
        self.participant = participant
        self.condition = condition
        self.seed = seed
        self.wall_clock = wall_clock  # supplied, never read from the engine (ADR-003)
        self.seq = 0
        self.rows: list[dict] = []

    def write(self, t_scen: int, type_: str, **payload: Any) -> dict:
        if type_ not in EVENT_TYPES:
            raise ValueError(f"unknown event type: {type_}")
        self.seq += 1
        row = {
            "t_scen": t_scen,
            "t_wall": self.wall_clock,
            "session": self.session,
            "participant": self.participant,
            "condition": self.condition,
            "seq": self.seq,
            "type": type_,
            "engine_version": ENGINE_VERSION,
            "schema_version": SCHEMA_VERSION,
            "model_seed": self.seed,
        }
        row.update({k: _plain(v) for k, v in payload.items()})
        self.rows.append(row)
        return row

    def to_jsonl(self) -> str:
        return "\n".join(json.dumps(r, sort_keys=True, ensure_ascii=False) for r in self.rows)

    def save(self, path: str) -> None:
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(self.to_jsonl() + "\n")
