"""Generate the fictional terrain raster for fin-def-03.

Terrain is apparatus, not scenery (ADR-010). The layout exists to satisfy the
experimental-design gate in tests/test_terrain.py.

The two corridors are deliberately ASYMMETRIC, and the asymmetry is the point:

  west  short, fast, and fully exposed   — a road across open ground
  east  long, slow, and covered          — a track under forest

Neither option dominates. The fast route is the exposed one, so the choice cannot
be made on time alone and cannot be made on safety alone: it is a trade-off, and
the risk half of it is only visible if the participant asks. That is what makes
the branch forced (docs/architecture/reconciliation.md K-6).

Geometry, in cells of 100 m:

        x=28 west road          x=41 KELO           x=70 east track
  y=30  +---------------- northern lateral (road) --------------+
        |     open ground          lake             forest      |
  y=75  +---------------- southern lateral (road) --------------+
                             KELO
"""

from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from engine.terrain import write_png

OPEN, FOREST, WATER, ROAD, URBAN, TRACK = 0, 1, 2, 3, 4, 5

W, H = 90, 90  # 9 x 9 km at 100 m per cell

WEST_X, EAST_X, KELO_X = 28, 70, 41
NORTH_Y, SOUTH_Y = 30, 75


def build() -> list[list[int]]:
    g = [[OPEN for _ in range(W)] for _ in range(H)]

    # Forest covering the eastern third: the covered corridor and its shadows.
    for y in range(NORTH_Y - 6, SOUTH_Y + 5):
        for x in range(58, 82):
            g[y][x] = FOREST
    # A forest belt across the north, so the approach is not observable end to end.
    for y in range(12, 22):
        for x in range(10, 82):
            g[y][x] = FOREST

    # The lake: no cutting between the corridors, so the branch holds.
    for y in range(38, 68):
        for x in range(31, 56):
            if ((x - 43) / 12.5) ** 2 + ((y - 53) / 15.0) ** 2 <= 1.0:
                g[y][x] = WATER

    # West corridor: road, through open ground. Fast and seen.
    for y in range(NORTH_Y, SOUTH_Y + 1):
        g[y][WEST_X] = ROAD
    # East corridor: track, under forest. Slow and unseen.
    for y in range(NORTH_Y, SOUTH_Y + 1):
        g[y][EAST_X] = TRACK

    # Laterals joining the two, both road.
    for x in range(WEST_X, EAST_X + 1):
        g[NORTH_Y][x] = ROAD
        g[SOUTH_Y][x] = ROAD

    # KELO: the objective, on the southern lateral.
    for y in range(SOUTH_Y + 1, SOUTH_Y + 6):
        for x in range(KELO_X - 4, KELO_X + 5):
            g[y][x] = URBAN

    # A village on the eastern track, so the corridors are not visually identical.
    for y in range(60, 64):
        for x in range(EAST_X + 1, EAST_X + 6):
            g[y][x] = URBAN

    return g


if __name__ == "__main__":
    out = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "scenarios", "terrain", "valley_a.png",
    )
    write_png(out, build())
    print(f"wrote {out} ({W}x{H} cells, {W/10:.0f}x{H/10:.0f} km)")
