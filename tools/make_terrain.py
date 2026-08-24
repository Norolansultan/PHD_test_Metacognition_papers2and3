"""Generate the fictional terrain raster for fin-def-03.

Terrain is apparatus, not scenery (ADR-010). The layout is built to satisfy the
experimental-design gate in tests/test_terrain.py:

  - a forced branch point: two corridors from a common junction to the objective,
    symmetric in length so neither is choosable on distance alone
  - two routes with different risk profiles: the west corridor runs through open
    ground, the east corridor through forest
  - visibility shadows: the forest belts block ground line of sight
  - a lake between the corridors so the choice cannot be deferred by cutting across
  - distances that make time a real cost: ~9 km across

Geometry, in cells of 100 m:

      x=20 west road            x=41 KELO          x=62 east road
  y=30  +--------------------- northern lateral ---------------+
        |                        (junction 41,30)              |
        |   open ground              lake                 forest
  y=75  +--------------------- southern lateral ---------------+
                                  KELO
"""

from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from engine.terrain import write_png

OPEN, FOREST, WATER, ROAD, URBAN = 0, 1, 2, 3, 4

W, H = 90, 90  # 9 x 9 km at 100 m per cell

WEST_X, EAST_X, KELO_X = 20, 62, 41
NORTH_Y, SOUTH_Y = 30, 75


def build() -> list[list[int]]:
    g = [[OPEN for _ in range(W)] for _ in range(H)]

    # The eastern half is forested: the covered corridor and the shadows it casts.
    for y in range(NORTH_Y + 2, SOUTH_Y - 1):
        for x in range(48, 78):
            g[y][x] = FOREST
    # A forest belt across the north, so the approach is not observable end to end.
    for y in range(12, 22):
        for x in range(10, 80):
            g[y][x] = FOREST

    # The lake sits between the corridors: no cutting across, and the branch holds.
    for y in range(38, 66):
        for x in range(28, 54):
            if ((x - 41) / 13.0) ** 2 + ((y - 52) / 14.0) ** 2 <= 1.0:
                g[y][x] = WATER

    # Corridors and laterals.
    for y in range(NORTH_Y, SOUTH_Y + 1):
        g[y][WEST_X] = ROAD
        g[y][EAST_X] = ROAD
    for x in range(WEST_X, EAST_X + 1):
        g[NORTH_Y][x] = ROAD
        g[SOUTH_Y][x] = ROAD

    # KELO: the objective, on the southern lateral, equidistant from both corridors.
    for y in range(SOUTH_Y + 1, SOUTH_Y + 6):
        for x in range(KELO_X - 4, KELO_X + 5):
            g[y][x] = URBAN

    # A village on the eastern corridor, so the two are not visually identical.
    for y in range(58, 62):
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
