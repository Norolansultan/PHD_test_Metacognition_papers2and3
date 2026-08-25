"""Replay a session from its log alone (ADR-007, build order step 6).

A log that cannot reproduce its session cannot be fixed later; it means
re-collecting. This is tested at the start of the project, not at the end.
"""

from __future__ import annotations

import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import yaml

from harness.run import run


def participant_spec_from_log(path: str) -> dict:
    rows = [json.loads(line) for line in open(path, encoding="utf-8") if line.strip()]
    start = next(r for r in rows if r["type"] == "session_start")
    spec = {
        "participant": start["participant"],
        "session": start["session"],
        "condition": start["condition"],
        "style": start.get("condition_config", {}).get("style", "plain"),
        "social_info": start.get("social_info", "none"),
        "actions": [],
    }
    pending_confidence: dict[str, dict] = {}
    for r in rows:
        t = r["t_scen"]
        if r["type"] == "query":
            spec["actions"].append({"at_t": t, "type": "query", "text": r["raw_text"]})
        elif r["type"] == "probe_answer":
            a = {"at_t": t, "type": "probe_answer", "ref": r["ref"]}
            if r.get("choice") is not None:
                a["choice"] = r["choice"]
            if r.get("text") is not None:
                a["text"] = r["text"]
            spec["actions"].append(a)
            pending_confidence[r["ref"]] = a
        elif r["type"] == "confidence":
            a = pending_confidence.get(r["ref"])
            if a is not None:
                a["confidence"] = r["value"]
        elif r["type"] == "isa_load":
            spec["actions"].append({"at_t": t, "type": "isa", "value": r["value"]})
        elif r["type"] == "decision":
            a = {"at_t": t, "type": "decision", "action": r["action"]}
            for k in ("axis", "unit", "route", "target"):
                if r.get(k) is not None:
                    a[k] = r[k]
            spec["actions"].append(a)
    return spec


def scenario_from_log(path: str) -> str:
    rows = [json.loads(line) for line in open(path, encoding="utf-8") if line.strip()]
    start = next(r for r in rows if r["type"] == "session_start")
    return f"scenarios/{start['scenario']}.yaml"


def replay(log_path: str, out_path: str, root: str = ".") -> str:
    spec = participant_spec_from_log(log_path)
    tmp = out_path + ".participant.yaml"
    with open(tmp, "w", encoding="utf-8") as fh:
        yaml.safe_dump(spec, fh, sort_keys=False, allow_unicode=True)
    run(scenario_from_log(log_path), tmp, out_path, root)
    os.remove(tmp)
    return out_path


if __name__ == "__main__":
    src, dst = sys.argv[1], sys.argv[2]
    replay(src, dst)
    print(f"replayed {src} -> {dst}")
