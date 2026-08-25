"""Error injection — presentation layer only (ADR-006).

Injection never modifies world truth. It modifies only what the computation
returns. The two kinds never occur in the same trial, and every answer carries an
injection id or None.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Injection:
    id: str
    kind: str  # "projection_error" | "guidance_distortion"
    after_t: int
    param: str | None = None
    factor: float | None = None
    direction: str | None = None
    magnitude: str | None = None


class Injector:
    def __init__(self, injections: list[Injection]) -> None:
        kinds = {i.kind for i in injections}
        if {"projection_error", "guidance_distortion"} <= kinds:
            raise ValueError(
                "a scenario may not arm both injection kinds: they must never "
                "co-occur in a trial (ADR-006)"
            )
        self.injections = sorted(injections, key=lambda i: (i.after_t, i.id))

    def active(self, t: int, kind: str) -> Injection | None:
        for inj in self.injections:
            if inj.kind == kind and t >= inj.after_t:
                return inj
        return None

    def param_override(self, t: int) -> tuple[dict, str | None]:
        """Parameters the projection should be run with, and the injection id."""
        inj = self.active(t, "projection_error")
        if inj is None or inj.param is None or inj.factor is None:
            return {}, None
        return {inj.param: inj.factor}, inj.id
