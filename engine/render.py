"""Layer 3 — presentation. Templates only, never generated text (ADR-004).

Wording, hedging vocabulary and length are independent variables in this study.
The hedging register is per-condition configuration, not a model's choice.
"""

from __future__ import annotations

from engine.belief import Estimate
from engine.projection import ProjectionOutcome

HEDGE = {
    "plain": {
        "single_source": "Single source, uncorroborated.",
        "aged": "This observation is {mins} minutes old.",
        "no_data": "No information available on that.",
    },
    "cautious": {
        "single_source": "Single source, uncorroborated; treat with caution.",
        "aged": "This observation is {mins} minutes old and may have been overtaken.",
        "no_data": "No information available on that.",
    },
}


def _mins(seconds: int) -> int:
    return max(0, round(seconds / 60))


def _grid(pos: tuple[float, float] | None) -> str:
    if pos is None:
        return "unknown"
    return f"{int(pos[0] // 100):02d}-{int(pos[1] // 100):02d}"


def render_locate(est: Estimate | None, style: str, subject: str) -> str:
    h = HEDGE[style]
    if est is None:
        return h["no_data"]
    lines = [
        f"{subject}: last observed {_mins(est.age_s)} min ago, {est.source}.",
        f"Estimated position {_grid(est.pos)}, uncertainty {int(est.uncertainty_m)} m.",
    ]
    if est.confidence < 0.8:
        lines.append(h["single_source"])
    return "\n".join(lines)


def render_strength(est: Estimate | None, style: str, subject: str) -> str:
    h = HEDGE[style]
    if est is None:
        return h["no_data"]
    s = est.attrs.get("strength")
    kind = est.attrs.get("kind", "unknown type")
    return (
        f"{subject}: reported as {kind}, combat strength {s}.\n"
        + h["aged"].format(mins=_mins(est.age_s))
    )


def render_projection(out: ProjectionOutcome, style: str) -> str:
    h = HEDGE[style]
    if out.predicted_pos is None:
        return h["no_data"]
    line = (
        f"Projection over {_mins(out.horizon_s)} min: {out.subject} at "
        f"{_grid(out.predicted_pos)}"
    )
    if out.predicted_uncertainty_m:
        line += f", uncertainty {int(out.predicted_uncertainty_m)} m"
    line += "."
    if out.eta_s is not None:
        line += f"\nTime to reach that point: {_mins(out.eta_s)} min."
    if out.reachable is False:
        line += "\nThe move does not complete within the horizon."
    return line


def render_compare(rows: list[tuple[str, ProjectionOutcome]], style: str) -> str:
    out = ["Option comparison:"]
    for name, o in rows:
        eta = "not reached" if o.eta_s is None else f"{_mins(o.eta_s)} min"
        exp = "" if o.exposed_fraction is None else (
            f", {int(round(o.exposed_fraction * 100))} % of the route in open ground"
        )
        out.append(f"  {name}: arrival {eta}{exp}.")
    return "\n".join(out)


def render_order(interpretation: str, style: str) -> str:
    return f"Reading of the standing order for this sector:\n{interpretation}"


def render_unknown(style: str) -> str:
    return HEDGE[style]["no_data"]
