"""Greyscale-8 PNG read/write with no external dependencies.

The scenario format specifies terrain as a PNG plus a legend (docs/scenarios).
Pillow is not a dependency of the engine, so this module encodes and decodes the
narrow subset we author ourselves: 8-bit greyscale, no interlacing, filter type 0
on every row.
"""

from __future__ import annotations

import struct
import zlib
from dataclasses import dataclass


def _chunk(tag: bytes, data: bytes) -> bytes:
    return (
        struct.pack(">I", len(data))
        + tag
        + data
        + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)
    )


def write_png(path: str, rows: list[list[int]]) -> None:
    h = len(rows)
    w = len(rows[0])
    raw = b"".join(b"\x00" + bytes(r) for r in rows)
    png = b"\x89PNG\r\n\x1a\n"
    png += _chunk(b"IHDR", struct.pack(">IIBBBBB", w, h, 8, 0, 0, 0, 0))
    png += _chunk(b"IDAT", zlib.compress(raw, 9))
    png += _chunk(b"IEND", b"")
    with open(path, "wb") as fh:
        fh.write(png)


def read_png(path: str) -> list[list[int]]:
    with open(path, "rb") as fh:
        data = fh.read()
    if data[:8] != b"\x89PNG\r\n\x1a\n":
        raise ValueError(f"{path}: not a PNG")
    pos = 8
    w = h = 0
    idat = b""
    while pos < len(data):
        (length,) = struct.unpack(">I", data[pos : pos + 4])
        tag = data[pos + 4 : pos + 8]
        body = data[pos + 8 : pos + 8 + length]
        pos += 12 + length
        if tag == b"IHDR":
            w, h, depth, colour, _, _, interlace = struct.unpack(">IIBBBBB", body)
            if (depth, colour, interlace) != (8, 0, 0):
                raise ValueError(f"{path}: only 8-bit greyscale, non-interlaced")
        elif tag == b"IDAT":
            idat += body
        elif tag == b"IEND":
            break
    raw = zlib.decompress(idat)
    stride = w + 1
    rows = []
    for y in range(h):
        line = raw[y * stride : (y + 1) * stride]
        if line[0] != 0:
            raise ValueError(f"{path}: only filter type 0 is supported")
        rows.append(list(line[1:]))
    return rows


@dataclass(frozen=True)
class TerrainGrid:
    """A raster of terrain classes. Positions are continuous metres (D-11)."""

    cells: tuple[tuple[int, ...], ...]
    cell_m: float
    legend: dict[int, str]

    @property
    def width_m(self) -> float:
        return len(self.cells[0]) * self.cell_m

    @property
    def height_m(self) -> float:
        return len(self.cells) * self.cell_m

    def at(self, pos: tuple[float, float]) -> str:
        """Terrain class at a continuous position. Out of bounds reads as the edge."""
        x, y = pos
        cx = min(max(int(x // self.cell_m), 0), len(self.cells[0]) - 1)
        cy = min(max(int(y // self.cell_m), 0), len(self.cells) - 1)
        return self.legend[self.cells[cy][cx]]

    def cover_fraction(self, pos: tuple[float, float], radius_m: float = 300.0) -> float:
        """Share of forest cells within radius_m of a position.

        Exposure is a property of the surroundings, not of the cell under the
        unit's feet: a platoon on a road through open ground is observable, the
        same platoon on a road through forest is not.
        """
        r = max(1, int(radius_m // self.cell_m))
        cx = int(pos[0] // self.cell_m)
        cy = int(pos[1] // self.cell_m)
        total = forest = 0
        for dy in range(-r, r + 1):
            for dx in range(-r, r + 1):
                if dx * dx + dy * dy > r * r:
                    continue
                x, y = cx + dx, cy + dy
                if 0 <= y < len(self.cells) and 0 <= x < len(self.cells[0]):
                    total += 1
                    if self.legend[self.cells[y][x]] == "forest":
                        forest += 1
        return (forest / total) if total else 0.0

    @classmethod
    def load(cls, png_path: str, cell_m: float, legend: dict[int, str]) -> "TerrainGrid":
        rows = read_png(png_path)
        return cls(
            cells=tuple(tuple(r) for r in rows),
            cell_m=cell_m,
            legend={int(k): v for k, v in legend.items()},
        )
