"""End-to-end check: a real browser against a real server.

Drives the participant display through a query, a freeze with a probe, a
confidence rating and an ISA rating, then asserts the log contains what the
measurement documents require. Run with the API already serving on :8000.

    python3 -m uvicorn api.main:app --port 8000 &
    python3 tools/e2e_check.py
"""

from __future__ import annotations

import json
import os
import sys

from playwright.sync_api import sync_playwright

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CHROME = "/opt/pw-browsers/chromium-1194/chrome-linux/chrome"
PID = "e2e01"


def main() -> int:
    errors: list[str] = []
    latencies: list[float] = []
    with sync_playwright() as p:
        b = p.chromium.launch(executable_path=CHROME)
        pg = b.new_page(viewport={"width": 1280, "height": 820})
        pg.on("pageerror", lambda e: errors.append(f"pageerror: {e}"))
        pg.on("console", lambda m: (
            errors.append(m.text) if m.type == "error"
            else latencies.append(float(m.text.split()[2]))
            if m.text.startswith("answer in") else None))

        pg.goto(f"http://127.0.0.1:8010/?pid={PID}&scenario=fin-def-03")
        pg.click("#begin")
        pg.wait_for_selector("#app", state="visible")

        # Let a few observations accumulate before asking, so the answer is a
        # real one rather than the no-information response.
        for _ in range(6):
            pg.evaluate("fetch('/api/tick',{method:'POST',headers:{'Content-Type':"
                        "'application/json'},body:JSON.stringify({pid:'%s'})})" % PID)
        pg.wait_for_timeout(400)

        # Ask something, and time the acknowledgement.
        pg.fill("#q", "where is the enemy")
        pg.press("#q", "Enter")
        pg.wait_for_timeout(600)
        answer = pg.inner_text("#answer")
        print("answer:", answer.replace("\n", " / ")[:110])
        if "last observed" not in answer:
            errors.append(f"expected a located answer, got: {answer!r}")

        # Order a move: the decision must reach the log.
        pg.click("[data-move='west']")
        pg.wait_for_timeout(200)

        # Drive the clock to the first probe. One tick per second is too slow for
        # a check, so the tick endpoint is called directly.
        for _ in range(70):
            pg.evaluate("fetch('/api/tick',{method:'POST',headers:{'Content-Type':"
                        "'application/json'},body:JSON.stringify({pid:'%s'})})" % PID)
        pg.wait_for_timeout(1500)
        pg.wait_for_selector("#freeze", state="visible", timeout=8000)
        print("freeze visible:", pg.is_visible("#freeze"))

        # The channel must refuse while the display is blanked.
        refused = pg.evaluate(
            "fetch('/api/ask',{method:'POST',headers:{'Content-Type':'application/json'},"
            "body:JSON.stringify({pid:'%s',text:'where is the enemy'})})"
            ".then(r=>r.json()).then(j=>j.answer.refused)" % PID)
        print("query refused during freeze:", refused)
        if not refused:
            errors.append("the channel answered during a freeze")

        pg.click("[data-opt='C']")
        pg.click("[data-conf='3']")
        pg.click("[data-isa='4']")
        pg.click("#psubmit")
        pg.wait_for_timeout(400)
        if pg.is_visible("#freeze"):
            errors.append("the freeze did not close after the probe was answered")

        pg.screenshot(path=os.path.join(ROOT, "logs", "e2e.png"))
        pg.click("#finish")
        pg.wait_for_timeout(600)
        b.close()

    path = os.path.join(ROOT, "logs", f"{PID}.jsonl")
    rows = [json.loads(line) for line in open(path, encoding="utf-8") if line.strip()]
    types = {r["type"] for r in rows}
    required = {"session_start", "observation_created", "query", "answer", "decision",
                "freeze_start", "screen_blanked", "probe_shown", "probe_answer",
                "confidence", "isa_load", "freeze_end"}
    missing = required - types
    if missing:
        errors.append(f"log is missing event types: {sorted(missing)}")

    for r in rows:
        for field in ("engine_version", "schema_version", "model_seed", "t_scen", "seq"):
            if field not in r:
                errors.append(f"row {r.get('seq')} is missing {field}")
                break

    print(f"log: {len(rows)} events, {len(types)} distinct types")
    if latencies:
        print(f"answer latency: {max(latencies):.0f} ms (requirement: under 300 ms)")
        if max(latencies) > 300:
            errors.append(f"answer latency {max(latencies):.0f} ms exceeds 300 ms")
    print("ERRORS:", errors or "none")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
