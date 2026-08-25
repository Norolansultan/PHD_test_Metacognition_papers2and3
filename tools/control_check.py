"""Check the white-cell control display in a real browser.

Runs the situation forward at acceleration and asserts that it actually develops:
units move, contact happens, strengths fall, the log fills.
"""

from __future__ import annotations

import os
import sys

from playwright.sync_api import sync_playwright

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CHROME = "/opt/pw-browsers/chromium-1194/chrome-linux/chrome"
PORT = os.environ.get("PORT", "8020")


def main() -> int:
    errors: list[str] = []
    with sync_playwright() as p:
        b = p.chromium.launch(executable_path=CHROME)
        pg = b.new_page(viewport={"width": 1500, "height": 900})
        pg.on("pageerror", lambda e: errors.append(f"pageerror: {e}"))
        pg.on("console", lambda m: errors.append(m.text) if m.type == "error" else None)

        pg.goto(f"http://127.0.0.1:{PORT}/control.html?pid=wc_check")
        pg.wait_for_timeout(1500)

        first = pg.evaluate("() => truth.entities.map(e => "
                            "({id:e.id, pos:e.pos.slice(), s:e.strength}))")
        pg.click("[data-x='30']")
        pg.wait_for_timeout(9000)
        later = pg.evaluate("() => truth.entities.map(e => "
                            "({id:e.id, pos:e.pos.slice(), s:e.strength}))")
        t = pg.evaluate("() => truth.t")

        moved = sum(1 for a, c in zip(first, later)
                    if abs(a["pos"][0] - c["pos"][0]) + abs(a["pos"][1] - c["pos"][1]) > 50)
        weakened = sum(1 for a, c in zip(first, later) if c["s"] < a["s"] - 0.001)
        log_lines = pg.eval_on_selector_all("#log div", "els => els.length")
        engagements = pg.eval_on_selector_all("#log .engagement", "els => els.length")

        print(f"scenario time reached: {t // 60} min")
        print(f"units that moved: {moved} / {len(first)}")
        print(f"units that took losses: {weakened}")
        print(f"log lines: {log_lines}, of which engagements: {engagements}")
        print("weather:", pg.inner_text("#met"))

        if moved < 2:
            errors.append("the situation is not moving")
        if weakened < 1:
            errors.append("nothing is taking losses: the picture does not develop")
        if engagements < 1:
            errors.append("no engagements reached the log")

        pg.screenshot(path=os.path.join(ROOT, "logs", "control.png"))
        b.close()

    print("ERRORS:", errors or "none")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
