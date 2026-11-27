"""Procedural vector art for the graphical front end.

Everything here is drawn from primitives -- rectangles, ovals, polygons and
lines -- in a fixed logical canvas of 1000x600.  A front end supplies a
:class:`Painter` that scales those coordinates to real pixels; :mod:`advent.gui`
wraps a tkinter ``Canvas``, and the tests use a recording painter.  There are no
image files, no third-party libraries, and no network access: a scene is a pure
function of its :class:`advent.scenes.Scene`.

The style is deliberately flat and illustrative.  The engine's text remains
authoritative; these pictures are a reading of the room descriptions, not a
replacement for them.
"""

from __future__ import annotations

import math
import random
from collections.abc import Callable, Sequence
from typing import Protocol

LOGICAL_W = 1000.0
LOGICAL_H = 600.0

Point = tuple[float, float]


class Painter(Protocol):
    """The drawing operations the art needs.  Coordinates are logical units."""

    def rect(
        self,
        x0: float,
        y0: float,
        x1: float,
        y1: float,
        *,
        fill: str | None = None,
        outline: str | None = None,
        width: float = 1,
        stipple: str | None = None,
    ) -> None: ...

    def oval(
        self,
        x0: float,
        y0: float,
        x1: float,
        y1: float,
        *,
        fill: str | None = None,
        outline: str | None = None,
        width: float = 1,
        stipple: str | None = None,
    ) -> None: ...

    def polygon(
        self,
        points: Sequence[Point],
        *,
        fill: str | None = None,
        outline: str | None = None,
        width: float = 1,
        stipple: str | None = None,
        smooth: bool = False,
    ) -> None: ...

    def line(
        self,
        points: Sequence[Point],
        fill: str,
        *,
        width: float = 1,
        smooth: bool = False,
    ) -> None: ...

    def text(
        self,
        x: float,
        y: float,
        text: str,
        *,
        fill: str,
        size: float = 14,
        anchor: str = "center",
        bold: bool = False,
    ) -> None: ...


# ---------------------------------------------------------------------------
# Colours
# ---------------------------------------------------------------------------


def _rgb(color: str) -> tuple[int, int, int]:
    color = color.lstrip("#")
    if len(color) == 3:
        color = "".join(ch * 2 for ch in color)
    return int(color[0:2], 16), int(color[2:4], 16), int(color[4:6], 16)


def _hex(rgb: tuple[float, float, float]) -> str:
    r, g, b = (max(0, min(255, int(round(v)))) for v in rgb)
    return "#%02x%02x%02x" % (r, g, b)


def shade(color: str, factor: float) -> str:
    """Multiply a colour's brightness (``factor < 1`` darkens)."""
    return _hex(tuple(c * factor for c in _rgb(color)))


def mix(first: str, second: str, t: float) -> str:
    """Blend two colours; ``t=0`` is ``first``, ``t=1`` is ``second``."""
    a, b = _rgb(first), _rgb(second)
    return _hex(tuple(a[i] + (b[i] - a[i]) * t for i in range(3)))


def luminance(color: str) -> float:
    """Perceived brightness in ``0..1`` (used by the tests, and by shading)."""
    r, g, b = _rgb(color)
    return (0.2126 * r + 0.7152 * g + 0.0722 * b) / 255.0


# ---------------------------------------------------------------------------
# Palettes
# ---------------------------------------------------------------------------

_BASE: dict[str, str] = {
    "sky_top": "#15141f",
    "sky_bottom": "#2b293a",
    "sun": "#ffe9a8",
    "cloud": "#8d91a6",
    "distant": "#232232",
    "tree": "#243a2c",
    "tree_dark": "#1a2b21",
    "trunk": "#3a2a1e",
    "grass": "#3b5236",
    "grass_dark": "#2b3f2b",
    "dirt": "#4a3b2c",
    "rock": "#4a4458",
    "rock_dark": "#302c3c",
    "rock_light": "#6a6278",
    "floor": "#3d3849",
    "wall": "#443f54",
    "wall_dark": "#2d2938",
    "water": "#2f6f8f",
    "water_light": "#5fa8c4",
    "mist": "#cfd8e6",
    "glow": "#ffd27a",
    "warm": "#b06a3c",
    "accent": "#c9a227",
    "shadow": "#14121a",
    "lava": "#e2571e",
    "lava_light": "#ffb03a",
    "brick": "#8c4a38",
    "brick_dark": "#663226",
    "roof": "#3a2b33",
    "wood": "#6b4a2e",
    "metal": "#9aa3b0",
    "metal_dark": "#5d6570",
    "gold": "#e8c04a",
    "green": "#4f7a3a",
    "paper": "#e8dcc0",
    "blood": "#8f2f2f",
    "skin": "#c98f63",
    "bone": "#ded6c2",
}


def _pal(**overrides: str) -> dict[str, str]:
    palette = dict(_BASE)
    palette.update(overrides)
    return palette


PALETTES: dict[str, dict[str, str]] = {
    "cave": _pal(),
    "surface": _pal(
        sky_top="#6fa8dc",
        sky_bottom="#cfe3f2",
        sun="#ffe9a8",
        cloud="#ffffff",
        distant="#5d7f63",
        tree="#2f5d3a",
        tree_dark="#234a2d",
        trunk="#4a3524",
        grass="#6f9e4f",
        grass_dark="#567f3d",
        dirt="#8a6a48",
        rock="#7d7568",
        rock_dark="#5d564c",
        rock_light="#a29a8c",
        floor="#7a6a52",
        wall="#8c4a38",
        wall_dark="#6b3528",
        water="#4f93b5",
        water_light="#9fd3e6",
        mist="#e8eef4",
        glow="#ffe9a8",
        brick="#a9563f",
        brick_dark="#8c4634",
        roof="#5b3f33",
        wood="#7a5535",
        paper="#efe4c8",
    ),
    "house": _pal(
        sky_top="#4a6a86",
        sky_bottom="#cfe3f2",
        wall="#a9563f",
        wall_dark="#7d3c2d",
        rock="#8d8377",
        rock_dark="#6a6157",
        rock_light="#b3a898",
        floor="#7a5535",
        wood="#6b4a2e",
        brick="#a9563f",
        brick_dark="#8c4634",
        roof="#4b3428",
        glow="#ffe9a8",
        water="#4f93b5",
        water_light="#9fd3e6",
        metal="#8d949f",
        metal_dark="#5d6570",
    ),
    "warm": _pal(
        rock="#6a4030",
        rock_dark="#452a22",
        rock_light="#8f5b3e",
        wall="#6a4030",
        wall_dark="#452a22",
        floor="#4a2f26",
        warm="#d08040",
        glow="#ffd27a",
        mist="#e7d6c6",
    ),
    "water": _pal(
        rock="#3a4654",
        rock_dark="#242c36",
        rock_light="#5c6c7c",
        floor="#2d3742",
        wall="#3a4654",
        wall_dark="#242c36",
        water="#1f5a7a",
        water_light="#63b3cf",
        mist="#dbe9f2",
    ),
    "soft": _pal(
        rock="#6a4a5a",
        rock_dark="#46303c",
        rock_light="#8f6a7c",
        wall="#6a4a5a",
        wall_dark="#46303c",
        floor="#5a3c4a",
        warm="#c07a8a",
        glow="#ffd9c0",
        mist="#e8dbe4",
    ),
    "shrine": _pal(
        rock="#6d5030",
        rock_dark="#4a3520",
        rock_light="#96744a",
        wall="#6d5030",
        wall_dark="#4a3520",
        floor="#4a3520",
        warm="#d9a45a",
        glow="#ffd27a",
        accent="#b0703a",
    ),
    "volcano": _pal(
        sky_top="#2a1214",
        sky_bottom="#6a2a1a",
        distant="#3a1a16",
        rock="#3a2622",
        rock_dark="#241414",
        rock_light="#5c3a30",
        floor="#2a1a18",
        wall="#3a2622",
        wall_dark="#241414",
        lava="#e2571e",
        lava_light="#ffb03a",
        glow="#ff8a3a",
        mist="#6a4a42",
        tree="#2a1a16",
        tree_dark="#1a0e0c",
    ),
    "void": _pal(
        sky_top="#08070c",
        sky_bottom="#08070c",
        rock="#0c0a10",
        rock_dark="#06050a",
        rock_light="#181420",
        floor="#08070c",
        wall="#0c0a10",
        wall_dark="#06050a",
        mist="#2a2230",
        glow="#5a1418",
        lava="#5a1418",
        lava_light="#8a2a20",
    ),
}


def palette(name: str, dark: bool = False) -> dict[str, str]:
    """Return a palette, darkened when the room is unlit."""
    pal = PALETTES.get(name, PALETTES["cave"])
    if not dark:
        return pal
    return {key: shade(value, 0.3) for key, value in pal.items()}


# ---------------------------------------------------------------------------
# Generic shape helpers
# ---------------------------------------------------------------------------


def _vgrad(
    p: Painter,
    x0: float,
    y0: float,
    x1: float,
    y1: float,
    top: str,
    bottom: str,
    steps: int = 18,
) -> None:
    for i in range(steps):
        t0 = i / steps
        t1 = (i + 1) / steps
        p.rect(
            x0,
            y0 + (y1 - y0) * t0,
            x1,
            y0 + (y1 - y0) * t1 + 0.5,
            fill=mix(top, bottom, (t0 + t1) / 2),
            outline="",
        )


def _oval(
    p: Painter,
    cx: float,
    cy: float,
    rx: float,
    ry: float,
    fill: str | None,
    outline: str | None = None,
    width: float = 1,
    stipple: str | None = None,
) -> None:
    p.oval(cx - rx, cy - ry, cx + rx, cy + ry, fill=fill, outline=outline, width=width, stipple=stipple)


def _circle(
    p: Painter,
    cx: float,
    cy: float,
    r: float,
    fill: str | None,
    outline: str | None = None,
    width: float = 1,
) -> None:
    _oval(p, cx, cy, r, r, fill, outline, width)


def _poly(
    p: Painter,
    points: Sequence[Point],
    fill: str | None,
    outline: str | None = None,
    width: float = 1,
    smooth: bool = False,
) -> None:
    p.polygon(points, fill=fill, outline=outline, width=width, smooth=smooth)


def _roundrect(
    p: Painter,
    x0: float,
    y0: float,
    x1: float,
    y1: float,
    radius: float,
    fill: str | None,
    outline: str | None = None,
    width: float = 1,
) -> None:
    r = max(1.0, min(radius, (x1 - x0) / 2, (y1 - y0) / 2))
    points: list[Point] = [
        (x0 + r, y0),
        (x1 - r, y0),
        (x1, y0 + r),
        (x1, y1 - r),
        (x1 - r, y1),
        (x0 + r, y1),
        (x0, y1 - r),
        (x0, y0 + r),
    ]
    p.polygon(points, fill=fill, outline=outline, width=width, smooth=True)


def _glow(
    p: Painter,
    cx: float,
    cy: float,
    radius: float,
    color: str,
    base: str,
    steps: int = 7,
) -> None:
    for i in range(steps, 0, -1):
        t = i / steps
        _circle(p, cx, cy, radius * t, mix(base, color, 0.55 * (1.0 - t) + 0.08), "")


def _cloud(p: Painter, cx: float, cy: float, scale: float, color: str) -> None:
    for dx, dy, r in ((-40, 4, 26), (0, -12, 32), (38, 2, 24), (0, 12, 28), (-14, 14, 20), (16, 14, 22)):
        _oval(p, cx + dx * scale, cy + dy * scale, r * scale, r * scale * 0.8, color, "")


def _tree(
    p: Painter,
    x: float,
    base: float,
    height: float,
    pal: dict[str, str],
    rnd: random.Random,
) -> None:
    trunk = max(3.0, height * 0.055)
    p.rect(x - trunk / 2, base - height * 0.6, x + trunk / 2, base, fill=pal["trunk"], outline="")
    blobs = (
        (0.0, -0.72, 0.30),
        (-0.16, -0.55, 0.23),
        (0.17, -0.58, 0.24),
        (0.02, -0.92, 0.20),
        (-0.06, -0.40, 0.18),
    )
    for i, (dx, dy, r) in enumerate(blobs):
        colour = pal["tree"] if i % 2 == 0 else pal["tree_dark"]
        _oval(p, x + dx * height, base + dy * height, r * height, r * height * 0.88, colour, "")
    _oval(
        p,
        x - 0.08 * height,
        base - 0.78 * height,
        0.10 * height,
        0.08 * height,
        mix(pal["tree"], "#ffffff", 0.10),
        "",
    )


def _tree_band(
    p: Painter,
    pal: dict[str, str],
    rnd: random.Random,
    base_y: float,
    height: float,
) -> None:
    points: list[Point] = [(0.0, base_y)]
    x = 0.0
    while x < LOGICAL_W:
        width = rnd.uniform(46, 96)
        points.append((x, base_y - height * rnd.uniform(0.45, 0.95)))
        points.append((x + width * 0.5, base_y - height * rnd.uniform(0.75, 1.25)))
        points.append((x + width, base_y - height * rnd.uniform(0.4, 0.9)))
        x += width
    points.extend([(LOGICAL_W, base_y), (LOGICAL_W, base_y + 14), (0.0, base_y + 14)])
    _poly(p, points, pal["distant"])


def _mist(
    p: Painter,
    pal: dict[str, str],
    cx: float,
    cy: float,
    rx: float,
    ry: float,
    layers: int = 3,
) -> None:
    for i in range(layers):
        t = (i + 1) / (layers + 1)
        _oval(
            p,
            cx + (t - 0.5) * rx * 0.6,
            cy + (t - 0.5) * ry * 0.5,
            rx * (0.9 - 0.2 * i),
            ry * (0.9 - 0.2 * i),
            pal["mist"],
            "",
            stipple="gray25" if i % 2 else "gray12",
        )


def _speckle(
    p: Painter,
    rnd: random.Random,
    x0: float,
    y0: float,
    x1: float,
    y1: float,
    color: str,
    count: int,
    size: float = 3,
) -> None:
    for _ in range(count):
        x = rnd.uniform(x0, x1)
        y = rnd.uniform(y0, y1)
        p.rect(x, y, x + rnd.uniform(1, size), y + rnd.uniform(1, size * 0.7), fill=color, outline="")


def _bricks(
    p: Painter,
    pal: dict[str, str],
    x0: float,
    y0: float,
    x1: float,
    y1: float,
    rows: int,
    cols: int,
) -> None:
    row_h = (y1 - y0) / rows
    for row in range(rows):
        y = y0 + row * row_h
        p.line([(x0, y), (x1, y)], shade(pal["brick"], 0.72), width=1.5)
        offset = (row % 2) * ((x1 - x0) / cols / 2)
        for col in range(cols + 1):
            x = x0 + offset + col * (x1 - x0) / cols
            if x0 < x < x1:
                p.line([(x, y), (x, y + row_h)], shade(pal["brick"], 0.78), width=1.2)


def _arch(
    p: Painter,
    cx: float,
    base: float,
    width: float,
    height: float,
    fill: str | None,
    outline: str | None = None,
    line_width: float = 4,
    smooth: bool = True,
) -> None:
    points: list[Point] = [(cx - width / 2, base)]
    steps = 22
    for i in range(steps + 1):
        angle = math.pi * (1 - i / steps)
        points.append((cx + math.cos(angle) * width / 2, base - math.sin(angle) * height))
    points.append((cx + width / 2, base))
    _poly(p, points, fill, outline, line_width, smooth=smooth)


def _ripples(
    p: Painter,
    pal: dict[str, str],
    cx: float,
    cy: float,
    rx: float,
    ry: float,
    count: int,
) -> None:
    for i in range(count):
        t = (i + 1) / (count + 1)
        _oval(p, cx, cy + (t - 0.5) * ry, rx * (0.55 + 0.45 * t), ry * 0.10 * (0.5 + t), None, pal["water_light"], 2)


def _jagged(
    p: Painter,
    rnd: random.Random,
    start: Point,
    end: Point,
    rough: float,
    steps: int = 8,
) -> list[Point]:
    points: list[Point] = [start]
    for i in range(1, steps):
        t = i / steps
        x = start[0] + (end[0] - start[0]) * t
        y = start[1] + (end[1] - start[1]) * t
        points.append((x + rnd.uniform(-rough, rough), y + rnd.uniform(-rough, rough)))
    points.append(end)
    return points


# ---------------------------------------------------------------------------
# Backdrops: one function per kind of place
# ---------------------------------------------------------------------------


def _bd_road(p: Painter, pal: dict[str, str], rnd: random.Random) -> None:
    _vgrad(p, 0, 0, LOGICAL_W, 380, pal["sky_top"], pal["sky_bottom"])
    _glow(p, 806, 112, 100, pal["sun"], pal["sky_top"])
    _circle(p, 806, 112, 34, pal["sun"])
    _cloud(p, 210, 108, 1.0, pal["cloud"])
    _cloud(p, 470, 70, 0.7, pal["cloud"])
    _cloud(p, 648, 152, 0.55, pal["cloud"])
    _tree_band(p, pal, rnd, 374, 74)
    p.rect(0, 372, LOGICAL_W, LOGICAL_H, fill=pal["grass"], outline="")
    p.rect(0, 372, LOGICAL_W, 434, fill=pal["grass_dark"], outline="")
    _poly(p, [(428, 600), (578, 600), (532, 420), (480, 420)], pal["dirt"])
    p.line([(452, 600), (500, 420)], shade(pal["dirt"], 0.8), width=3)
    p.line([(556, 600), (514, 420)], shade(pal["dirt"], 0.8), width=3)
    _speckle(p, rnd, 0, 380, LOGICAL_W, 600, pal["grass_dark"], 90)
    for _ in range(30):
        x = rnd.uniform(0, LOGICAL_W)
        y = rnd.uniform(392, 592)
        p.line([(x, y), (x - 5, y - 13)], pal["grass_dark"], width=2)
        p.line([(x, y), (x + 6, y - 11)], pal["grass_dark"], width=2)


def _bd_forest(p: Painter, pal: dict[str, str], rnd: random.Random) -> None:
    _vgrad(p, 0, 0, LOGICAL_W, 270, pal["sky_top"], pal["sky_bottom"])
    _tree_band(p, pal, rnd, 330, 130)
    p.rect(0, 316, LOGICAL_W, LOGICAL_H, fill=pal["grass_dark"], outline="")
    for i in range(10):
        x = 40 + i * 106 + rnd.uniform(-28, 28)
        _tree(p, x, rnd.uniform(520, 588), rnd.uniform(230, 330), pal, rnd)
    _speckle(p, rnd, 0, 470, LOGICAL_W, 600, pal["grass"], 110)
    for _ in range(22):
        x = rnd.uniform(0, LOGICAL_W)
        y = rnd.uniform(500, 596)
        p.line([(x, y), (x - 9, y - 20)], pal["grass"], width=2, smooth=True)


def _bd_hill(p: Painter, pal: dict[str, str], rnd: random.Random) -> None:
    _vgrad(p, 0, 0, LOGICAL_W, 344, pal["sky_top"], pal["sky_bottom"])
    _glow(p, 210, 96, 96, pal["sun"], pal["sky_top"])
    _circle(p, 210, 96, 30, pal["sun"])
    _cloud(p, 640, 92, 0.8, pal["cloud"])
    _cloud(p, 830, 150, 0.55, pal["cloud"])
    _tree_band(p, pal, rnd, 346, 84)
    p.rect(0, 340, LOGICAL_W, LOGICAL_H, fill=pal["grass"], outline="")
    _poly(
        p,
        [(0, 528), (180, 434), (372, 402), (566, 430), (760, 470), (1000, 438), (1000, 600), (0, 600)],
        pal["grass_dark"],
    )
    p.line([(432, 600), (492, 486), (556, 432), (646, 414)], pal["dirt"], width=26, smooth=True)
    p.line([(432, 600), (492, 486), (556, 432), (646, 414)], shade(pal["dirt"], 0.82), width=2, smooth=True)
    _speckle(p, rnd, 0, 360, LOGICAL_W, 600, pal["grass_dark"], 100)


def _bd_valley(p: Painter, pal: dict[str, str], rnd: random.Random) -> None:
    _vgrad(p, 0, 0, LOGICAL_W, 330, pal["sky_top"], pal["sky_bottom"])
    _tree_band(p, pal, rnd, 330, 96)
    p.rect(0, 326, LOGICAL_W, LOGICAL_H, fill=pal["grass_dark"], outline="")
    _poly(p, [(0, 330), (300, 600), (0, 600)], pal["grass"])
    _poly(p, [(1000, 330), (700, 600), (1000, 600)], pal["grass"])
    _poly(p, [(300, 600), (700, 600), (620, 486), (380, 486)], pal["rock_dark"])
    _poly(p, [(360, 600), (640, 600), (590, 500), (410, 500)], pal["water"])
    _ripples(p, pal, 500, 560, 90, 40, 4)
    _speckle(p, rnd, 330, 500, 670, 600, pal["rock_light"], 40, 4)


def _bd_streambed(p: Painter, pal: dict[str, str], rnd: random.Random) -> None:
    _vgrad(p, 0, 0, LOGICAL_W, 168, pal["sky_top"], pal["sky_bottom"])
    _tree_band(p, pal, rnd, 172, 64)
    p.rect(0, 168, LOGICAL_W, LOGICAL_H, fill=pal["rock"], outline="")
    _poly(p, [(0, 168), (420, 600), (0, 600)], pal["rock_dark"])
    _poly(p, [(1000, 168), (580, 600), (1000, 600)], pal["rock_dark"])
    _poly(p, [(340, 600), (660, 600), (600, 320), (400, 320)], pal["water"])
    _poly(p, [(380, 600), (620, 600), (580, 340), (420, 340)], pal["water_light"])
    _ripples(p, pal, 500, 470, 80, 90, 5)
    for i in range(8):
        x = rnd.uniform(0, LOGICAL_W)
        y = rnd.uniform(200, 590)
        p.line(_jagged(p, rnd, (x, y), (x + rnd.uniform(-50, 50), y + rnd.uniform(10, 50)), 4), pal["rock_light"], width=2)
    _speckle(p, rnd, 0, 200, LOGICAL_W, 600, pal["rock_light"], 70, 4)


def _bd_depression(p: Painter, pal: dict[str, str], rnd: random.Random) -> None:
    _vgrad(p, 0, 0, LOGICAL_W, 208, pal["sky_top"], pal["sky_bottom"])
    _tree_band(p, pal, rnd, 212, 66)
    p.rect(0, 206, LOGICAL_W, LOGICAL_H, fill=pal["dirt"], outline="")
    p.rect(0, 206, LOGICAL_W, 300, fill=shade(pal["dirt"], 0.72), outline="")
    _poly(p, [(0, 206), (318, 600), (0, 600)], shade(pal["dirt"], 0.6))
    _poly(p, [(1000, 206), (682, 600), (1000, 600)], shade(pal["dirt"], 0.6))
    _poly(p, [(318, 600), (682, 600), (628, 468), (372, 468)], shade(pal["dirt"], 0.92))
    _speckle(p, rnd, 300, 470, 700, 600, shade(pal["dirt"], 0.55), 90, 4)
    for i in range(6):
        x = rnd.uniform(0, LOGICAL_W)
        p.line(_jagged(p, rnd, (x, 240), (x + rnd.uniform(-40, 40), 580), 6, 6), shade(pal["dirt"], 0.45), width=2)


def _bd_house(p: Painter, pal: dict[str, str], rnd: random.Random) -> None:
    p.rect(0, 0, LOGICAL_W, LOGICAL_H, fill=pal["wall"], outline="")
    _bricks(p, pal, 0, 0, LOGICAL_W, 470, 16, 22)
    # ceiling beams
    p.rect(0, 0, LOGICAL_W, 74, fill=pal["roof"], outline="")
    for x in range(40, int(LOGICAL_W), 150):
        p.rect(x, 0, x + 22, 74, fill=shade(pal["roof"], 0.75), outline="")
    # floor
    p.rect(0, 470, LOGICAL_W, LOGICAL_H, fill=pal["floor"], outline="")
    for y in range(486, 600, 26):
        p.line([(0, y), (LOGICAL_W, y)], shade(pal["floor"], 0.7), width=2)
    # window with daylight
    p.rect(724, 148, 924, 330, fill=pal["sky_bottom"], outline=pal["wood"], width=9)
    p.line([(824, 148), (824, 330)], pal["wood"], width=7)
    p.line([(724, 238), (924, 238)], pal["wood"], width=7)
    _poly(p, [(736, 330), (912, 330), (1000, 600), (540, 600)], pal["glow"], "", smooth=False)
    _oval(p, 824, 240, 80, 76, pal["glow"], "", stipple="gray12")
    # door
    p.rect(62, 214, 246, 470, fill=pal["wood"], outline=shade(pal["wood"], 0.6), width=8)
    for x in (100, 140, 180, 220):
        p.line([(x, 222), (x, 462)], shade(pal["wood"], 0.72), width=2)
    _circle(p, 218, 350, 5, pal["gold"])
    # stone sill under the spring (the pool itself is a prop)
    p.rect(360, 470, 640, 486, fill=pal["rock"], outline="")


def _bd_tunnel(p: Painter, pal: dict[str, str], rnd: random.Random) -> None:
    p.rect(0, 0, LOGICAL_W, LOGICAL_H, fill=pal["rock_dark"], outline="")
    _arch(p, 500, 520, 620, 420, pal["rock"], pal["rock_light"], 5)
    _arch(p, 500, 512, 380, 300, pal["rock_dark"], pal["rock_light"], 3)
    p.rect(0, 500, LOGICAL_W, LOGICAL_H, fill=pal["floor"], outline="")
    # jagged side walls
    left = _jagged(p, rnd, (0, 0), (300, 600), 24, 10)
    _poly(p, [(0, 0)] + left + [(0, 600)], pal["rock_dark"])
    right = _jagged(p, rnd, (1000, 0), (700, 600), 24, 10)
    _poly(p, [(1000, 0)] + right + [(1000, 600)], pal["rock_dark"])
    for i in range(10):
        x = rnd.uniform(60, 940)
        y = rnd.uniform(40, 460)
        p.line(_jagged(p, rnd, (x, y), (x + rnd.uniform(-70, 70), y + rnd.uniform(10, 70)), 6, 4), pal["rock_light"], width=2)
    _speckle(p, rnd, 0, 470, LOGICAL_W, 600, pal["rock_light"], 60, 3)


def _bd_crawl(p: Painter, pal: dict[str, str], rnd: random.Random) -> None:
    p.rect(0, 0, LOGICAL_W, LOGICAL_H, fill=pal["rock_dark"], outline="")
    # a low ceiling pressed down on the passage
    _poly(p, [(0, 0), (1000, 0), (1000, 210), (860, 250), (700, 196), (520, 250), (340, 200), (160, 252), (0, 214)], pal["rock"])
    for i in range(9):
        x = rnd.uniform(0, 1000)
        p.line(_jagged(p, rnd, (x, 0), (x + rnd.uniform(-40, 40), 230), 8, 5), pal["rock_light"], width=2)
    p.rect(0, 430, LOGICAL_W, LOGICAL_H, fill=pal["floor"], outline="")
    for i in range(26):
        x = rnd.uniform(0, LOGICAL_W)
        y = rnd.uniform(440, 596)
        _oval(p, x, y, rnd.uniform(12, 28), rnd.uniform(6, 13), pal["rock"], shade(pal["rock"], 0.7), 1)
    _poly(p, [(0, 430), (1000, 430), (1000, 470), (0, 470)], pal["rock_dark"])


def _bd_hall(p: Painter, pal: dict[str, str], rnd: random.Random) -> None:
    p.rect(0, 0, LOGICAL_W, LOGICAL_H, fill=pal["rock_dark"], outline="")
    for i, scale in enumerate((1.0, 0.78, 0.58, 0.40, 0.25)):
        _arch(
            p,
            500,
            540,
            900 * scale,
            470 * scale,
            mix(pal["rock_dark"], pal["rock"], 0.15 + i * 0.16),
            pal["rock_light"],
            3,
        )
    p.rect(0, 520, LOGICAL_W, LOGICAL_H, fill=pal["floor"], outline="")
    for i in range(9):
        t = i / 9
        p.line([(500 - 440 * t, 520), (500 + 440 * t, 520)], shade(pal["floor"], 0.7), width=2)
    _mist(p, pal, 500, 330, 420, 60, 3)
    _speckle(p, rnd, 0, 40, LOGICAL_W, 500, pal["rock_light"], 50, 3)


def _bd_cavern(p: Painter, pal: dict[str, str], rnd: random.Random) -> None:
    p.rect(0, 0, LOGICAL_W, LOGICAL_H, fill=pal["rock_dark"], outline="")
    _glow(p, 500, 340, 420, pal["rock"], pal["rock_dark"], 8)
    # ceiling stalactites
    for i in range(14):
        x = i * 76 + rnd.uniform(-20, 20)
        length = rnd.uniform(40, 130)
        _poly(p, [(x - 16, 0), (x + 16, 0), (x + rnd.uniform(-4, 4), length)], pal["rock"], "")
    # far wall shapes
    _poly(
        p,
        [(60, 520), (140, 250), (320, 180), (520, 240), (700, 170), (860, 260), (940, 520)],
        shade(pal["rock"], 0.85),
    )
    p.rect(0, 500, LOGICAL_W, LOGICAL_H, fill=pal["floor"], outline="")
    _speckle(p, rnd, 0, 500, LOGICAL_W, 600, pal["rock_light"], 70, 4)
    for i in range(7):
        x = rnd.uniform(80, 920)
        p.line(_jagged(p, rnd, (x, 120), (x + rnd.uniform(-50, 50), 500), 10, 6), pal["rock_light"], width=2)


def _bd_maze(p: Painter, pal: dict[str, str], rnd: random.Random) -> None:
    p.rect(0, 0, LOGICAL_W, LOGICAL_H, fill=pal["rock_dark"], outline="")
    path = [
        (0, 570),
        (250, 570),
        (300, 440),
        (500, 440),
        (560, 300),
        (760, 300),
        (820, 160),
        (1000, 160),
        (1000, 600),
        (0, 600),
    ]
    _poly(p, path, pal["floor"])
    p.line(path[:8], pal["rock_light"], width=7, smooth=True)
    # a branch and a dead-looking alcove
    _poly(p, [(300, 440), (380, 360), (520, 360), (560, 300)], pal["floor"])
    p.line([(300, 440), (380, 360), (520, 360), (560, 300)], pal["rock_light"], width=5, smooth=True)
    # rough wall texture
    for i in range(12):
        x = rnd.uniform(0, 1000)
        y = rnd.uniform(0, 600)
        p.line(_jagged(p, rnd, (x, y), (x + rnd.uniform(-90, 90), y + rnd.uniform(-40, 40)), 8, 5), pal["rock"], width=3)
    _speckle(p, rnd, 0, 0, 1000, 600, pal["rock"], 90, 3)


def _bd_canyon(p: Painter, pal: dict[str, str], rnd: random.Random) -> None:
    p.rect(0, 0, LOGICAL_W, LOGICAL_H, fill=pal["rock_dark"], outline="")
    _vgrad(p, 0, 0, LOGICAL_W, 120, pal["sky_top"], pal["sky_bottom"])
    left = [(0, 0)] + _jagged(p, rnd, (0, 120), (330, 600), 30, 9) + [(0, 600)]
    right = [(1000, 0)] + _jagged(p, rnd, (1000, 120), (670, 600), 30, 9) + [(1000, 600)]
    _poly(p, left, pal["rock"])
    _poly(p, right, pal["rock"])
    _poly(p, [(330, 600), (670, 600), (600, 470), (400, 470)], pal["floor"])
    for i in range(8):
        y = 150 + i * 52
        p.line([(0, y), (250 - i * 20, y + 40)], shade(pal["rock"], 0.8), width=3)
        p.line([(1000, y), (750 + i * 20, y + 40)], shade(pal["rock"], 0.8), width=3)
    _speckle(p, rnd, 0, 120, LOGICAL_W, 600, pal["rock_light"], 70, 4)


def _bd_water(p: Painter, pal: dict[str, str], rnd: random.Random) -> None:
    p.rect(0, 0, LOGICAL_W, LOGICAL_H, fill=pal["rock_dark"], outline="")
    _arch(p, 500, 300, 900, 300, pal["rock"], pal["rock_light"], 4)
    _vgrad(p, 0, 260, LOGICAL_W, LOGICAL_H, pal["water_light"], pal["water"], 22)
    for i in range(12):
        y = 300 + i * 24
        p.line([(0, y), (LOGICAL_W, y)], shade(pal["water"], 0.85), width=2)
    _ripples(p, pal, 500, 430, 320, 120, 5)
    _mist(p, pal, 500, 290, 360, 34, 3)
    _speckle(p, rnd, 0, 0, LOGICAL_W, 250, pal["rock_light"], 50, 4)
    for i in range(6):
        x = rnd.uniform(80, 920)
        p.line([(x, 300), (x + rnd.uniform(-20, 20), 590)], pal["water_light"], width=2)


def _bd_chasm(p: Painter, pal: dict[str, str], rnd: random.Random) -> None:
    p.rect(0, 0, LOGICAL_W, LOGICAL_H, fill=pal["rock_dark"], outline="")
    _poly(p, [(0, 0), (1000, 0), (1000, 300), (800, 260), (620, 300), (400, 250), (200, 300), (0, 260)], pal["rock"])
    _vgrad(p, 0, 260, LOGICAL_W, 500, pal["mist"], pal["rock_dark"], 18)
    _mist(p, pal, 500, 380, 420, 70, 4)
    _poly(p, [(0, 470), (1000, 470), (1000, 600), (0, 600)], pal["floor"])
    p.line([(0, 470), (1000, 470)], pal["rock_light"], width=4)
    for i in range(7):
        x = rnd.uniform(0, 1000)
        p.line(_jagged(p, rnd, (x, 40), (x + rnd.uniform(-60, 60), 280), 10, 5), pal["rock_light"], width=2)
    _speckle(p, rnd, 0, 480, 1000, 600, pal["rock_light"], 50, 3)


def _bd_volcano(p: Painter, pal: dict[str, str], rnd: random.Random) -> None:
    _vgrad(p, 0, 0, LOGICAL_W, 300, pal["sky_top"], pal["sky_bottom"])
    _glow(p, 500, 300, 320, pal["lava_light"], pal["sky_bottom"], 8)
    _poly(
        p,
        [(220, 380), (400, 300), (600, 300), (780, 380), (880, 600), (120, 600)],
        shade(pal["rock"], 0.9),
    )
    _poly(p, [(400, 300), (500, 350), (600, 300), (560, 250), (440, 250)], pal["lava"])
    _poly(p, [(470, 350), (530, 350), (520, 470), (560, 560), (440, 560), (480, 470)], pal["lava_light"])
    _poly(p, [(0, 500), (1000, 500), (1000, 600), (0, 600)], pal["rock_dark"])
    _poly(p, [(0, 500), (1000, 500), (1000, 520), (0, 520)], pal["lava"])
    for i in range(8):
        x = rnd.uniform(100, 900)
        p.line([(x, 520), (x + rnd.uniform(-20, 20), 600)], pal["lava_light"], width=3)
    _speckle(p, rnd, 0, 0, 1000, 260, shade(pal["sky_bottom"], 0.7), 90, 3)


def _bd_deadend(p: Painter, pal: dict[str, str], rnd: random.Random) -> None:
    p.rect(0, 0, LOGICAL_W, LOGICAL_H, fill=pal["rock_dark"], outline="")
    _poly(
        p,
        [(0, 0), (1000, 0), (1000, 460), (860, 500), (700, 440), (540, 500), (380, 440), (200, 500), (0, 460)],
        pal["rock"],
    )
    p.rect(0, 480, LOGICAL_W, LOGICAL_H, fill=pal["floor"], outline="")
    for i in range(9):
        x = rnd.uniform(0, 1000)
        p.line(_jagged(p, rnd, (x, 60), (x + rnd.uniform(-60, 60), 460), 10, 6), pal["rock_light"], width=2)
    _speckle(p, rnd, 0, 480, 1000, 600, pal["rock_light"], 50, 3)


def _bd_shrine(p: Painter, pal: dict[str, str], rnd: random.Random) -> None:
    p.rect(0, 0, LOGICAL_W, LOGICAL_H, fill=pal["wall"], outline="")
    for i in range(7):
        y = i * 70
        p.rect(0, y, LOGICAL_W, y + 30, fill=shade(pal["wall"], 0.86), outline="")
    p.rect(0, 470, LOGICAL_W, LOGICAL_H, fill=pal["floor"], outline="")
    _speckle(p, rnd, 0, 0, LOGICAL_W, 470, shade(pal["wall"], 0.7), 90, 3)
    _speckle(p, rnd, 0, 480, LOGICAL_W, 600, shade(pal["floor"], 0.75), 60, 3)


def _bd_soft(p: Painter, pal: dict[str, str], rnd: random.Random) -> None:
    p.rect(0, 0, LOGICAL_W, LOGICAL_H, fill=pal["wall"], outline="")
    for x in range(0, int(LOGICAL_W), 64):
        p.rect(x, 0, x + 30, 470, fill=shade(pal["wall"], 0.85), outline="")
        p.line([(x + 30, 0), (x + 30, 470)], shade(pal["wall"], 0.7), width=2)
    p.rect(0, 470, LOGICAL_W, LOGICAL_H, fill=pal["floor"], outline="")
    for x in range(30, int(LOGICAL_W), 90):
        p.line([(x, 480), (x, 596)], shade(pal["floor"], 0.7), width=2)
    _oval(p, 500, 540, 300, 46, shade(pal["floor"], 0.8), pal["accent"], 2)


def _bd_shell(p: Painter, pal: dict[str, str], rnd: random.Random) -> None:
    p.rect(0, 0, LOGICAL_W, LOGICAL_H, fill=pal["wall"], outline="")
    bands = 9
    for i in range(bands):
        y = i * (600 / bands)
        p.rect(0, y, LOGICAL_W, y + 600 / bands, fill=shade(pal["wall"], 0.7 + 0.05 * (i % 3)), outline="")
    for _ in range(18):
        x = rnd.uniform(0, LOGICAL_W)
        y = rnd.uniform(0, 470)
        _oval(p, x, y, rnd.uniform(14, 46), rnd.uniform(10, 30), shade(pal["wall"], 0.4), "", stipple="gray25")
    p.rect(0, 470, LOGICAL_W, LOGICAL_H, fill=pal["floor"], outline="")
    _speckle(p, rnd, 0, 480, LOGICAL_W, 600, shade(pal["floor"], 0.7), 70, 3)


def _bd_void(p: Painter, pal: dict[str, str], rnd: random.Random) -> None:
    p.rect(0, 0, LOGICAL_W, LOGICAL_H, fill="#07060a", outline="")
    _glow(p, 500, 430, 340, pal["glow"], "#07060a", 9)
    for i in range(9):
        x = rnd.uniform(120, 880)
        p.line(
            _jagged(p, rnd, (x, rnd.uniform(60, 220)), (x + rnd.uniform(-60, 60), rnd.uniform(380, 560)), 12, 5),
            shade(pal["glow"], 0.6),
            width=2,
        )


def _bd_sewer(p: Painter, pal: dict[str, str], rnd: random.Random) -> None:
    _vgrad(p, 0, 0, LOGICAL_W, 300, pal["sky_top"], pal["sky_bottom"])
    _tree_band(p, pal, rnd, 300, 70)
    p.rect(0, 296, LOGICAL_W, LOGICAL_H, fill=pal["grass"], outline="")
    _poly(p, [(0, 520), (1000, 520), (1000, 600), (0, 600)], pal["water"])
    _ripples(p, pal, 500, 560, 400, 40, 4)
    p.rect(300, 300, 700, 540, fill=shade(pal["rock"], 0.8), outline="")
    for cx in (390, 610):
        _circle(p, cx, 420, 74, shade(pal["rock"], 0.55), pal["rock_light"], 6)
        _circle(p, cx, 420, 54, "#0b0d10")
        _oval(p, cx, 470, 52, 18, pal["water"], "")
    _speckle(p, rnd, 0, 310, 1000, 600, pal["grass_dark"], 60, 3)


BACKDROPS: dict[str, Callable[[Painter, dict[str, str], random.Random], None]] = {
    "road": _bd_road,
    "forest": _bd_forest,
    "hill": _bd_hill,
    "valley": _bd_valley,
    "streambed": _bd_streambed,
    "depression": _bd_depression,
    "house": _bd_house,
    "tunnel": _bd_tunnel,
    "crawl": _bd_crawl,
    "hall": _bd_hall,
    "cavern": _bd_cavern,
    "maze": _bd_maze,
    "canyon": _bd_canyon,
    "water": _bd_water,
    "chasm": _bd_chasm,
    "volcano": _bd_volcano,
    "deadend": _bd_deadend,
    "shrine": _bd_shrine,
    "soft": _bd_soft,
    "shell": _bd_shell,
    "void": _bd_void,
    "sewer": _bd_sewer,
}

# ---------------------------------------------------------------------------
# Item icons: one small painting per object
# ---------------------------------------------------------------------------

IconPainter = Callable[[Painter, float, float, float, int | None], None]

_INK = "#1b1a22"


def _gem(
    p: Painter,
    cx: float,
    cy: float,
    rx: float,
    ry: float,
    fill: str,
    outline: str = _INK,
) -> None:
    _poly(
        p,
        [
            (cx, cy - ry),
            (cx + rx, cy - ry * 0.25),
            (cx + rx * 0.55, cy + ry),
            (cx - rx * 0.55, cy + ry),
            (cx - rx, cy - ry * 0.25),
        ],
        fill,
        outline,
        max(1.0, rx * 0.12),
    )
    _poly(
        p,
        [(cx, cy - ry), (cx + rx * 0.25, cy - ry * 0.15), (cx, cy + ry * 0.5), (cx - rx * 0.2, cy - ry * 0.15)],
        mix(fill, "#ffffff", 0.42),
        "",
    )


def _icon_keys(p: Painter, cx: float, cy: float, s: float, state: int | None = None) -> None:
    w = max(1.5, s * 0.07)
    _circle(p, cx - s * 0.26, cy - s * 0.10, s * 0.16, None, "#c9c3b2", w)
    p.line([(cx - s * 0.10, cy - s * 0.10), (cx + s * 0.32, cy - s * 0.10)], fill="#d9b64a", width=w)
    p.line([(cx + s * 0.32, cy - s * 0.10), (cx + s * 0.32, cy + s * 0.10)], fill="#d9b64a", width=w)
    p.line([(cx + s * 0.19, cy - s * 0.10), (cx + s * 0.19, cy + s * 0.05)], fill="#d9b64a", width=w)
    p.line([(cx + s * 0.10, cy - s * 0.10), (cx + s * 0.10, cy + s * 0.01)], fill="#d9b64a", width=w)
    _circle(p, cx - s * 0.36, cy - s * 0.24, s * 0.10, None, "#c9c3b2", w)


def _icon_lamp(p: Painter, cx: float, cy: float, s: float, state: int | None = None) -> None:
    lit = bool(state)
    if lit:
        _glow(p, cx, cy, s * 0.62, "#ffd27a", "#2a2630", 5)
    brass, dark = "#c9a23c", "#6b4f16"
    p.line(
        [(cx - s * 0.20, cy - s * 0.16), (cx, cy - s * 0.44), (cx + s * 0.20, cy - s * 0.16)],
        fill=brass,
        width=max(2, s * 0.06),
        smooth=True,
    )
    p.rect(cx - s * 0.22, cy - s * 0.20, cx + s * 0.22, cy - s * 0.08, fill=brass, outline=dark, width=2)
    _poly(
        p,
        [
            (cx - s * 0.20, cy - s * 0.08),
            (cx + s * 0.20, cy - s * 0.08),
            (cx + s * 0.15, cy + s * 0.24),
            (cx - s * 0.15, cy + s * 0.24),
        ],
        "#ffe6a0" if lit else "#7a7f8a",
        dark,
        2,
    )
    p.rect(cx - s * 0.24, cy + s * 0.24, cx + s * 0.24, cy + s * 0.34, fill=brass, outline=dark, width=2)
    if lit:
        _poly(
            p,
            [(cx, cy + s * 0.16), (cx + s * 0.06, cy + s * 0.04), (cx, cy - s * 0.02), (cx - s * 0.06, cy + s * 0.04)],
            "#ffb03a",
            "",
        )


def _icon_grate(p: Painter, cx: float, cy: float, s: float, state: int | None = None) -> None:
    p.rect(cx - s * 0.40, cy - s * 0.22, cx + s * 0.40, cy + s * 0.22, fill="#4a4f57", outline="#1b1a22", width=2)
    for i in range(5):
        x = cx - s * 0.30 + i * s * 0.15
        p.line([(x, cy - s * 0.18), (x, cy + s * 0.18)], fill="#aeb6c1", width=max(2, s * 0.035))
    for dx in (-0.36, 0.36):
        for dy in (-0.17, 0.17):
            _circle(p, cx + s * dx, cy + s * dy, max(1.5, s * 0.03), "#c9d0d8")


def _icon_cage(p: Painter, cx: float, cy: float, s: float, state: int | None = None) -> None:
    w = max(1.5, s * 0.04)
    p.rect(cx - s * 0.34, cy + s * 0.22, cx + s * 0.34, cy + s * 0.32, fill="#9a7444", outline="#4a3218", width=2)
    _arch(p, cx, cy + s * 0.22, s * 0.68, s * 0.66, None, "#c9a23c", w)
    for dx in (-0.24, -0.08, 0.08, 0.24):
        p.line([(cx + s * dx, cy - s * 0.40), (cx + s * dx, cy + s * 0.22)], fill="#c9a23c", width=w)
    _circle(p, cx, cy - s * 0.44, s * 0.06, "#c9a23c")


def _icon_rod(p: Painter, cx: float, cy: float, s: float, state: int | None = None) -> None:
    p.line(
        [(cx - s * 0.34, cy + s * 0.28), (cx + s * 0.28, cy - s * 0.30)],
        fill="#15141a",
        width=max(3, s * 0.10),
    )
    p.line(
        [(cx - s * 0.34, cy + s * 0.28), (cx - s * 0.22, cy + s * 0.18)],
        fill="#c9c3b2",
        width=max(3, s * 0.10),
    )
    _circle(p, cx + s * 0.30, cy - s * 0.32, s * 0.07, "#c9c3b2")
    _circle(p, cx + s * 0.30, cy - s * 0.32, s * 0.03, "#6b6b73")


def _icon_treads(p: Painter, cx: float, cy: float, s: float, state: int | None = None) -> None:
    for i in range(4):
        y = cy + s * 0.30 - i * s * 0.17
        half = s * (0.34 - i * 0.05)
        p.rect(cx - half, y - s * 0.09, cx + half, y, fill="#8d8377", outline="#3a342c", width=2)
        p.line([(cx - half, y - s * 0.09), (cx + half, y - s * 0.09)], fill="#c3b8a6", width=2)


def _icon_bird(p: Painter, cx: float, cy: float, s: float, state: int | None = None) -> None:
    body = "#6fa8dc"
    p.oval(cx - s * 0.26, cy - s * 0.16, cx + s * 0.24, cy + s * 0.20, fill=body, outline=_INK, width=2)
    _circle(p, cx + s * 0.20, cy - s * 0.22, s * 0.16, body, _INK, 2)
    _poly(
        p,
        [(cx + s * 0.34, cy - s * 0.26), (cx + s * 0.48, cy - s * 0.20), (cx + s * 0.34, cy - s * 0.15)],
        "#e8a33c",
        _INK,
        1,
    )
    _circle(p, cx + s * 0.24, cy - s * 0.26, max(1.2, s * 0.025), _INK)
    _poly(
        p,
        [(cx - s * 0.20, cy - s * 0.10), (cx - s * 0.02, cy - s * 0.28), (cx + s * 0.06, cy - s * 0.02)],
        shade(body, 0.8),
        _INK,
        1,
    )
    p.line([(cx - s * 0.06, cy + s * 0.18), (cx - s * 0.06, cy + s * 0.30)], fill="#e8a33c", width=2)
    p.line([(cx + s * 0.04, cy + s * 0.18), (cx + s * 0.04, cy + s * 0.30)], fill="#e8a33c", width=2)


def _icon_door(p: Painter, cx: float, cy: float, s: float, state: int | None = None) -> None:
    p.rect(cx - s * 0.28, cy - s * 0.38, cx + s * 0.28, cy + s * 0.38, fill="#6b4a2e", outline="#2a1c10", width=3)
    for x in (-0.16, 0.0, 0.16):
        p.line([(cx + s * x, cy - s * 0.34), (cx + s * x, cy + s * 0.34)], fill="#4a3218", width=2)
    p.line([(cx - s * 0.28, cy - s * 0.20), (cx + s * 0.28, cy - s * 0.20)], fill="#9aa3b0", width=4)
    p.line([(cx - s * 0.28, cy + s * 0.20), (cx + s * 0.28, cy + s * 0.20)], fill="#9aa3b0", width=4)
    _circle(p, cx + s * 0.18, cy, s * 0.04, "#e8c04a")


def _icon_pillow(p: Painter, cx: float, cy: float, s: float, state: int | None = None) -> None:
    _roundrect(p, cx - s * 0.38, cy - s * 0.24, cx + s * 0.38, cy + s * 0.24, s * 0.16, "#8f5f8f", _INK, 2)
    _oval(p, cx, cy, s * 0.10, s * 0.06, "#c9a2c9", "")
    p.line([(cx - s * 0.30, cy - s * 0.16), (cx + s * 0.30, cy - s * 0.16)], fill="#c9a2c9", width=2, smooth=True)


def _icon_snake(p: Painter, cx: float, cy: float, s: float, state: int | None = None) -> None:
    green = "#5f8f3a"
    p.line(
        [
            (cx - s * 0.36, cy + s * 0.24),
            (cx - s * 0.10, cy + s * 0.36),
            (cx + s * 0.28, cy + s * 0.22),
            (cx + s * 0.30, cy - s * 0.02),
            (cx + s * 0.02, cy - s * 0.10),
            (cx - s * 0.22, cy + s * 0.04),
        ],
        fill=green,
        width=max(3, s * 0.12),
        smooth=True,
    )
    _circle(p, cx - s * 0.30, cy + s * 0.20, s * 0.13, green, _INK, 2)
    _circle(p, cx - s * 0.34, cy + s * 0.16, max(1.2, s * 0.025), "#e8c04a")
    p.line([(cx - s * 0.40, cy + s * 0.26), (cx - s * 0.46, cy + s * 0.32)], fill="#d94a3a", width=2)


def _icon_crystal(p: Painter, cx: float, cy: float, s: float, state: int | None = None) -> None:
    for i, dx in enumerate((-0.30, 0.0, 0.30)):
        _gem(p, cx + s * dx, cy + s * (0.02 - 0.06 * (i % 2)), s * 0.16, s * 0.34, "#9fd3e6")
    p.line([(cx - s * 0.42, cy + s * 0.30), (cx + s * 0.42, cy + s * 0.30)], fill="#5fa8c4", width=4)


def _icon_tablet(p: Painter, cx: float, cy: float, s: float, state: int | None = None) -> None:
    _roundrect(p, cx - s * 0.30, cy - s * 0.38, cx + s * 0.30, cy + s * 0.38, s * 0.06, "#8d8377", "#3a342c", 2)
    for i in range(5):
        y = cy - s * 0.24 + i * s * 0.12
        p.line([(cx - s * 0.20, y), (cx + s * 0.20, y)], fill="#4a4038", width=2)
    p.line([(cx - s * 0.14, cy + s * 0.28), (cx + s * 0.16, cy + s * 0.28)], fill="#4a4038", width=2)


def _icon_clam(p: Painter, cx: float, cy: float, s: float, state: int | None = None) -> None:
    shell = "#d8c0a0"
    _poly(
        p,
        [
            (cx, cy + s * 0.30),
            (cx - s * 0.36, cy + s * 0.02),
            (cx - s * 0.28, cy - s * 0.28),
            (cx, cy - s * 0.36),
            (cx + s * 0.28, cy - s * 0.28),
            (cx + s * 0.36, cy + s * 0.02),
        ],
        shell,
        "#6b5a44",
        2,
    )
    for dx in (-0.22, -0.08, 0.08, 0.22):
        p.line([(cx, cy + s * 0.28), (cx + s * dx, cy - s * 0.30)], fill="#a8906e", width=2)
    _circle(p, cx, cy + s * 0.02, s * 0.05, "#f4f0e2")


def _icon_oyster(p: Painter, cx: float, cy: float, s: float, state: int | None = None) -> None:
    _oval(p, cx, cy, s * 0.38, s * 0.30, "#8d8377", "#3a342c", 2)
    _oval(p, cx, cy, s * 0.26, s * 0.20, "#6b6157", "")
    _circle(p, cx + s * 0.04, cy - s * 0.02, s * 0.12, "#f4f0e2", "#a8a090", 1)
    _circle(p, cx - s * 0.01, cy - s * 0.07, s * 0.04, "#ffffff")


def _icon_magazine(p: Painter, cx: float, cy: float, s: float, state: int | None = None) -> None:
    p.rect(cx - s * 0.26, cy - s * 0.36, cx + s * 0.26, cy + s * 0.36, fill="#e8dcc0", outline=_INK, width=2)
    p.rect(cx - s * 0.26, cy - s * 0.36, cx + s * 0.26, cy - s * 0.20, fill="#b04030", outline="")
    for i in range(4):
        y = cy - s * 0.10 + i * s * 0.10
        p.line([(cx - s * 0.18, y), (cx + s * 0.18, y)], fill="#6b6157", width=2)
    p.text(cx, cy - s * 0.28, "TODAY", fill="#ffffff", size=max(6, s * 0.12), bold=True)


def _icon_knife(p: Painter, cx: float, cy: float, s: float, state: int | None = None) -> None:
    _poly(
        p,
        [(cx - s * 0.40, cy + s * 0.10), (cx + s * 0.16, cy - s * 0.28), (cx + s * 0.22, cy - s * 0.16), (cx - s * 0.34, cy + s * 0.22)],
        "#c9d0d8",
        _INK,
        2,
    )
    p.line([(cx - s * 0.40, cy + s * 0.10), (cx - s * 0.20, cy + s * 0.28)], fill="#4a3218", width=max(3, s * 0.12))
    p.line([(cx - s * 0.44, cy + s * 0.24), (cx - s * 0.30, cy + s * 0.36)], fill="#9aa3b0", width=3)


def _icon_food(p: Painter, cx: float, cy: float, s: float, state: int | None = None) -> None:
    p.line([(cx - s * 0.36, cy + s * 0.30), (cx - s * 0.08, cy + s * 0.06)], fill="#e8dcc0", width=max(3, s * 0.10))
    _circle(p, cx - s * 0.38, cy + s * 0.32, s * 0.07, "#e8dcc0", "#a8a090", 1)
    _oval(p, cx + s * 0.06, cy - s * 0.06, s * 0.28, s * 0.22, "#a05a2a", _INK, 2)
    _oval(p, cx + s * 0.02, cy - s * 0.12, s * 0.12, s * 0.08, "#c07a3a", "")


def _icon_bottle(p: Painter, cx: float, cy: float, s: float, state: int | None = None) -> None:
    liquid = {0: "#5fa8c4", 2: "#c9a23c"}.get(state if state is not None else 0, None)
    glass = "#c9d8d8"
    p.rect(cx - s * 0.10, cy - s * 0.38, cx + s * 0.10, cy - s * 0.20, fill=glass, outline=_INK, width=2)
    p.rect(cx - s * 0.12, cy - s * 0.44, cx + s * 0.12, cy - s * 0.36, fill="#8a6a2a", outline=_INK, width=1)
    _roundrect(p, cx - s * 0.24, cy - s * 0.22, cx + s * 0.24, cy + s * 0.34, s * 0.12, glass, _INK, 2)
    if liquid:
        _roundrect(p, cx - s * 0.19, cy - s * 0.02, cx + s * 0.19, cy + s * 0.29, s * 0.08, liquid, "")
        p.line([(cx - s * 0.15, cy + s * 0.01), (cx - s * 0.15, cy + s * 0.26)], fill=mix(liquid, "#ffffff", 0.5), width=3)
    else:
        p.line([(cx - s * 0.12, cy + s * 0.24), (cx + s * 0.12, cy + s * 0.24)], fill="#8d8377", width=2)


def _droplet(p: Painter, cx: float, cy: float, s: float, fill: str) -> None:
    _poly(
        p,
        [
            (cx, cy - s * 0.36),
            (cx + s * 0.24, cy + s * 0.04),
            (cx + s * 0.16, cy + s * 0.28),
            (cx, cy + s * 0.36),
            (cx - s * 0.16, cy + s * 0.28),
            (cx - s * 0.24, cy + s * 0.04),
        ],
        fill,
        _INK,
        2,
        smooth=True,
    )
    _circle(p, cx - s * 0.06, cy + s * 0.10, s * 0.05, mix(fill, "#ffffff", 0.6))


def _icon_water(p: Painter, cx: float, cy: float, s: float, state: int | None = None) -> None:
    _droplet(p, cx, cy, s, "#5fa8c4")


def _icon_oil(p: Painter, cx: float, cy: float, s: float, state: int | None = None) -> None:
    _droplet(p, cx, cy, s, "#b8912f")


def _icon_mirror(p: Painter, cx: float, cy: float, s: float, state: int | None = None) -> None:
    _oval(p, cx, cy, s * 0.30, s * 0.40, "#c9a23c", _INK, 3)
    _oval(p, cx, cy, s * 0.22, s * 0.32, "#9fd3e6", "#6b8a9a", 2)
    p.line([(cx - s * 0.10, cy - s * 0.16), (cx + s * 0.04, cy - s * 0.26)], fill="#ffffff", width=3, smooth=True)
    p.line([(cx - s * 0.14, cy - s * 0.04), (cx - s * 0.02, cy - s * 0.14)], fill="#e8f4fa", width=2, smooth=True)


def _icon_plant(p: Painter, cx: float, cy: float, s: float, state: int | None = None) -> None:
    stem = "#4f7a3a"
    p.line(
        [(cx, cy + s * 0.44), (cx - s * 0.06, cy + s * 0.10), (cx + s * 0.06, cy - s * 0.16), (cx, cy - s * 0.44)],
        fill=stem,
        width=max(3, s * 0.08),
        smooth=True,
    )
    for i, (dx, dy, flip) in enumerate(((-0.24, 0.24, -1), (0.26, 0.08, 1), (-0.22, -0.10, -1), (0.22, -0.26, 1))):
        _oval(p, cx + s * dx, cy + s * dy, s * 0.16, s * 0.09, "#5f8f3a" if i % 2 == 0 else "#3f6a2a", _INK, 1)
    for dy in (-0.34, 0.0, 0.30):
        _oval(p, cx + s * 0.10, cy + s * dy, s * 0.05, s * 0.07, "#c9a23c", _INK, 1)


def _icon_stalactite(p: Painter, cx: float, cy: float, s: float, state: int | None = None) -> None:
    _poly(
        p,
        [(cx - s * 0.16, cy - s * 0.44), (cx + s * 0.16, cy - s * 0.44), (cx + s * 0.04, cy + s * 0.10), (cx, cy + s * 0.30), (cx - s * 0.04, cy + s * 0.10)],
        "#8d8377",
        _INK,
        2,
    )
    p.line([(cx - s * 0.08, cy - s * 0.36), (cx - s * 0.02, cy + s * 0.16)], fill="#c3b8a6", width=2)


def _icon_shadow(p: Painter, cx: float, cy: float, s: float, state: int | None = None) -> None:
    _oval(p, cx, cy - s * 0.28, s * 0.14, s * 0.16, "#14121a", "")
    _poly(
        p,
        [(cx - s * 0.24, cy + s * 0.40), (cx - s * 0.16, cy - s * 0.06), (cx, cy - s * 0.16), (cx + s * 0.16, cy - s * 0.06), (cx + s * 0.24, cy + s * 0.40)],
        "#14121a",
        "",
        smooth=True,
    )
    _circle(p, cx - s * 0.06, cy - s * 0.30, max(1.2, s * 0.025), "#9fd3e6")
    _circle(p, cx + s * 0.06, cy - s * 0.30, max(1.2, s * 0.025), "#9fd3e6")


def _icon_axe(p: Painter, cx: float, cy: float, s: float, state: int | None = None) -> None:
    p.line([(cx - s * 0.32, cy + s * 0.36), (cx + s * 0.16, cy - s * 0.20)], fill="#6b4a2e", width=max(3, s * 0.10))
    _poly(
        p,
        [(cx + s * 0.06, cy - s * 0.30), (cx + s * 0.36, cy - s * 0.36), (cx + s * 0.40, cy - s * 0.08), (cx + s * 0.12, cy - s * 0.02)],
        "#c9d0d8",
        _INK,
        2,
    )


def _icon_mural(p: Painter, cx: float, cy: float, s: float, state: int | None = None) -> None:
    p.rect(cx - s * 0.42, cy - s * 0.32, cx + s * 0.42, cy + s * 0.32, fill="#8a5f38", outline="#4a3218", width=2)
    ink = "#d9a45a"
    for i in range(3):
        x = cx - s * 0.24 + i * s * 0.24
        _circle(p, x, cy - s * 0.10, s * 0.05, ink)
        p.line([(x, cy - s * 0.05), (x, cy + s * 0.12)], fill=ink, width=2)
        p.line([(x - s * 0.07, cy + s * 0.02), (x + s * 0.07, cy + s * 0.04)], fill=ink, width=2)
        p.line([(x, cy + s * 0.12), (x - s * 0.06, cy + s * 0.22)], fill=ink, width=2)
        p.line([(x, cy + s * 0.12), (x + s * 0.06, cy + s * 0.22)], fill=ink, width=2)
    _oval(p, cx + s * 0.24, cy + s * 0.18, s * 0.08, s * 0.05, ink, "")


def _icon_pirate(p: Painter, cx: float, cy: float, s: float, state: int | None = None) -> None:
    skin = "#c98f63"
    p.line([(cx - s * 0.16, cy + s * 0.42), (cx - s * 0.10, cy + s * 0.06)], fill="#2a2a3a", width=max(3, s * 0.09))
    p.line([(cx + s * 0.16, cy + s * 0.42), (cx + s * 0.10, cy + s * 0.06)], fill="#2a2a3a", width=max(3, s * 0.09))
    p.rect(cx - s * 0.20, cy - s * 0.14, cx + s * 0.20, cy + s * 0.10, fill="#b04030", outline=_INK, width=2)
    for i in range(3):
        p.line([(cx - s * 0.20 + i * s * 0.14, cy - s * 0.12), (cx - s * 0.20 + i * s * 0.14, cy + s * 0.08)], fill="#e8dcc0", width=2)
    _circle(p, cx, cy - s * 0.26, s * 0.16, skin, _INK, 2)
    p.rect(cx - s * 0.18, cy - s * 0.40, cx + s * 0.18, cy - s * 0.32, fill="#b04030", outline=_INK, width=1)
    _poly(p, [(cx - s * 0.12, cy - s * 0.22), (cx + s * 0.12, cy - s * 0.22), (cx, cy - s * 0.08)], "#2a2a3a", "")
    _circle(p, cx - s * 0.06, cy - s * 0.28, max(1.2, s * 0.02), _INK)
    _circle(p, cx + s * 0.06, cy - s * 0.28, max(1.2, s * 0.02), _INK)
    _poly(
        p,
        [(cx + s * 0.22, cy - s * 0.02), (cx + s * 0.44, cy - s * 0.16), (cx + s * 0.44, cy - s * 0.08), (cx + s * 0.24, cy + s * 0.06)],
        "#c9d0d8",
        _INK,
        1,
    )


def _icon_dragon(p: Painter, cx: float, cy: float, s: float, state: int | None = None) -> None:
    green, dark = "#4f8f3a", "#2f5a24"
    # tail
    p.line(
        [(cx - s * 0.42, cy + s * 0.34), (cx - s * 0.18, cy + s * 0.10), (cx - s * 0.06, cy + s * 0.20)],
        fill=green,
        width=max(3, s * 0.10),
        smooth=True,
    )
    # wings
    _poly(
        p,
        [(cx - s * 0.06, cy - s * 0.04), (cx - s * 0.34, cy - s * 0.34), (cx - s * 0.30, cy + s * 0.06)],
        dark,
        _INK,
        1,
    )
    _poly(
        p,
        [(cx + s * 0.06, cy - s * 0.04), (cx + s * 0.34, cy - s * 0.34), (cx + s * 0.30, cy + s * 0.06)],
        dark,
        _INK,
        1,
    )
    # body and neck
    _oval(p, cx, cy + s * 0.10, s * 0.24, s * 0.20, green, _INK, 2)
    p.line([(cx + s * 0.10, cy - s * 0.02), (cx + s * 0.18, cy - s * 0.30)], fill=green, width=max(4, s * 0.12))
    _oval(p, cx + s * 0.22, cy - s * 0.34, s * 0.15, s * 0.11, green, _INK, 2)
    _circle(p, cx + s * 0.28, cy - s * 0.38, max(1.5, s * 0.028), "#e8c04a")
    _circle(p, cx + s * 0.28, cy - s * 0.38, max(0.8, s * 0.012), _INK)
    _poly(
        p,
        [(cx + s * 0.34, cy - s * 0.34), (cx + s * 0.48, cy - s * 0.30), (cx + s * 0.34, cy - s * 0.26)],
        "#b04030",
        "",
    )
    # legs
    for dx in (-0.12, 0.10):
        p.line([(cx + s * dx, cy + s * 0.22), (cx + s * (dx - 0.04), cy + s * 0.40)], fill=dark, width=max(3, s * 0.08))


def _icon_bridge(p: Painter, cx: float, cy: float, s: float, state: int | None = None) -> None:
    _arch(p, cx, cy + s * 0.24, s * 0.86, s * 0.42, None, "#8d8377", max(3, s * 0.08))
    p.rect(cx - s * 0.44, cy + s * 0.20, cx + s * 0.44, cy + s * 0.28, fill="#6b6157", outline=_INK, width=1)
    for dx in (-0.30, -0.10, 0.10, 0.30):
        p.line([(cx + s * dx, cy + s * 0.24), (cx + s * dx, cy - s * 0.10)], fill="#a89a86", width=2)


def _icon_troll(p: Painter, cx: float, cy: float, s: float, state: int | None = None) -> None:
    body = "#6b7a4a"
    p.rect(cx - s * 0.22, cy - s * 0.10, cx + s * 0.22, cy + s * 0.28, fill=body, outline=_INK, width=2)
    _circle(p, cx, cy - s * 0.28, s * 0.18, body, _INK, 2)
    _circle(p, cx - s * 0.06, cy - s * 0.30, max(1.5, s * 0.03), "#e8c04a")
    _circle(p, cx + s * 0.06, cy - s * 0.30, max(1.5, s * 0.03), "#e8c04a")
    p.line([(cx - s * 0.16, cy + s * 0.26), (cx - s * 0.22, cy + s * 0.44)], fill=body, width=max(4, s * 0.10))
    p.line([(cx + s * 0.16, cy + s * 0.26), (cx + s * 0.22, cy + s * 0.44)], fill=body, width=max(4, s * 0.10))
    p.line([(cx + s * 0.20, cy - s * 0.06), (cx + s * 0.42, cy - s * 0.26)], fill="#6b4a2e", width=max(4, s * 0.11))
    _oval(p, cx + s * 0.44, cy - s * 0.30, s * 0.10, s * 0.14, "#8d8377", _INK, 2)


def _icon_bear(p: Painter, cx: float, cy: float, s: float, state: int | None = None) -> None:
    fur = "#6b4a2e"
    _oval(p, cx - s * 0.02, cy + s * 0.08, s * 0.34, s * 0.24, fur, _INK, 2)
    _circle(p, cx + s * 0.26, cy - s * 0.18, s * 0.18, fur, _INK, 2)
    _circle(p, cx + s * 0.16, cy - s * 0.32, s * 0.07, fur, _INK, 1)
    _circle(p, cx + s * 0.36, cy - s * 0.32, s * 0.07, fur, _INK, 1)
    _circle(p, cx + s * 0.32, cy - s * 0.20, max(1.5, s * 0.028), _INK)
    _circle(p, cx + s * 0.38, cy - s * 0.12, s * 0.06, "#c98f63", _INK, 1)
    for dx in (-0.24, -0.04, 0.14):
        p.line([(cx + s * dx, cy + s * 0.28), (cx + s * dx, cy + s * 0.44)], fill=fur, width=max(4, s * 0.10))


def _icon_message(p: Painter, cx: float, cy: float, s: float, state: int | None = None) -> None:
    p.rect(cx - s * 0.30, cy - s * 0.26, cx + s * 0.30, cy + s * 0.26, fill="#e8dcc0", outline="#8a7a5a", width=2)
    _circle(p, cx - s * 0.30, cy - s * 0.26, s * 0.06, "#c9b89a")
    _circle(p, cx - s * 0.30, cy + s * 0.26, s * 0.06, "#c9b89a")
    for i in range(4):
        y = cy - s * 0.16 + i * s * 0.11
        p.line([(cx - s * 0.20, y), (cx + s * 0.20, y)], fill="#6b6157", width=2)


def _icon_geyser(p: Painter, cx: float, cy: float, s: float, state: int | None = None) -> None:
    _poly(
        p,
        [(cx - s * 0.34, cy + s * 0.34), (cx - s * 0.14, cy + s * 0.04), (cx + s * 0.14, cy + s * 0.04), (cx + s * 0.34, cy + s * 0.34)],
        "#8d8377",
        _INK,
        2,
    )
    for dx, top in ((-0.14, -0.34), (0.0, -0.46), (0.14, -0.32)):
        p.line([(cx + s * dx, cy + s * 0.02), (cx + s * dx * 1.4, cy + s * top)], fill="#9fd3e6", width=max(2, s * 0.05), smooth=True)
    _circle(p, cx, cy + s * 0.06, s * 0.05, "#5fa8c4")


def _icon_vending(p: Painter, cx: float, cy: float, s: float, state: int | None = None) -> None:
    p.rect(cx - s * 0.28, cy - s * 0.40, cx + s * 0.28, cy + s * 0.40, fill="#4a6a8a", outline=_INK, width=2)
    p.rect(cx - s * 0.20, cy - s * 0.32, cx + s * 0.06, cy - s * 0.02, fill="#9fd3e6", outline="#2a3a4a", width=1)
    for i in range(3):
        p.rect(cx - s * 0.18, cy + s * 0.04 + i * s * 0.10, cx + s * 0.02, cy + s * 0.10 + i * s * 0.10, fill="#c9a23c", outline="")
    p.rect(cx + s * 0.10, cy + s * 0.08, cx + s * 0.22, cy + s * 0.20, fill="#1b1a22", outline="")
    _circle(p, cx + s * 0.16, cy - s * 0.18, s * 0.04, "#e8c04a")


def _icon_batteries(p: Painter, cx: float, cy: float, s: float, state: int | None = None) -> None:
    for i, dx in enumerate((-0.14, 0.14)):
        p.rect(cx + s * dx - s * 0.09, cy - s * 0.26, cx + s * dx + s * 0.09, cy + s * 0.30, fill="#2a2a3a", outline=_INK, width=2)
        p.rect(cx + s * dx - s * 0.09, cy - s * 0.26, cx + s * dx + s * 0.09, cy - s * 0.16, fill="#c9a23c", outline="")
        p.rect(cx + s * dx - s * 0.03, cy - s * 0.32, cx + s * dx + s * 0.03, cy - s * 0.26, fill="#9aa3b0", outline="")


def _icon_moss(p: Painter, cx: float, cy: float, s: float, state: int | None = None) -> None:
    for dx, dy, r in ((-0.18, 0.10, 0.20), (0.06, 0.04, 0.24), (0.24, 0.14, 0.16), (-0.02, 0.24, 0.18)):
        _oval(p, cx + s * dx, cy + s * dy, s * r, s * r * 0.7, "#3f6a2a" if dx < 0 else "#4f7a3a", "")
    _speckle(p, random.Random(7), cx - s * 0.3, cy - s * 0.05, cx + s * 0.3, cy + s * 0.3, "#6fa84a", 18, 2)


def _icon_gold(p: Painter, cx: float, cy: float, s: float, state: int | None = None) -> None:
    _poly(
        p,
        [
            (cx - s * 0.34, cy + s * 0.10),
            (cx - s * 0.20, cy - s * 0.24),
            (cx + s * 0.10, cy - s * 0.30),
            (cx + s * 0.34, cy - s * 0.06),
            (cx + s * 0.24, cy + s * 0.24),
            (cx - s * 0.16, cy + s * 0.28),
        ],
        "#e8c04a",
        "#8a6a1a",
        2,
        smooth=True,
    )
    _poly(
        p,
        [(cx - s * 0.16, cy - s * 0.16), (cx + s * 0.06, cy - s * 0.22), (cx + s * 0.02, cy - s * 0.06)],
        "#fff0a8",
        "",
    )
    _circle(p, cx + s * 0.14, cy + s * 0.08, s * 0.05, "#fff0a8")


def _icon_diamonds(p: Painter, cx: float, cy: float, s: float, state: int | None = None) -> None:
    _gem(p, cx - s * 0.16, cy + s * 0.06, s * 0.16, s * 0.24, "#bfe6f5")
    _gem(p, cx + s * 0.14, cy - s * 0.04, s * 0.14, s * 0.22, "#e8f4fa")
    _gem(p, cx + s * 0.02, cy + s * 0.18, s * 0.12, s * 0.18, "#9fd3e6")


def _icon_silver(p: Painter, cx: float, cy: float, s: float, state: int | None = None) -> None:
    for i, dy in enumerate((0.18, 0.02, -0.14)):
        x = cx - s * 0.30 + (i % 2) * s * 0.10
        p.rect(x, cy + s * dy, x + s * 0.44, cy + s * (dy + 0.12), fill="#c9d0d8", outline="#5d6570", width=2)
        p.line([(x + s * 0.06, cy + s * (dy + 0.04)), (x + s * 0.38, cy + s * (dy + 0.04))], fill="#eef2f6", width=2)


def _icon_jewels(p: Painter, cx: float, cy: float, s: float, state: int | None = None) -> None:
    p.line(
        [(cx - s * 0.36, cy - s * 0.10), (cx - s * 0.10, cy + s * 0.10), (cx + s * 0.18, cy - s * 0.06), (cx + s * 0.38, cy + s * 0.04)],
        fill="#c9a23c",
        width=max(2, s * 0.04),
        smooth=True,
    )
    for i, (dx, dy, fill) in enumerate(((-0.24, 0.0, "#d94a8a"), (-0.02, 0.10, "#5fa8c4"), (0.24, -0.02, "#5f8f3a"))):
        _gem(p, cx + s * dx, cy + s * dy, s * 0.08, s * 0.12, fill)
    _circle(p, cx + s * 0.40, cy + s * 0.04, s * 0.04, "#e8c04a")


def _icon_coins(p: Painter, cx: float, cy: float, s: float, state: int | None = None) -> None:
    for i in range(4):
        y = cy + s * 0.26 - i * s * 0.10
        _oval(p, cx - s * 0.06, y, s * 0.24, s * 0.08, "#e8c04a", "#8a6a1a", 2)
    _oval(p, cx - s * 0.06, cy - s * 0.14, s * 0.24, s * 0.08, "#fff0a8", "#8a6a1a", 2)
    _circle(p, cx - s * 0.06, cy - s * 0.14, s * 0.04, "#c9a23c")


def _icon_chest(p: Painter, cx: float, cy: float, s: float, state: int | None = None) -> None:
    p.rect(cx - s * 0.32, cy - s * 0.02, cx + s * 0.32, cy + s * 0.30, fill="#8a5a2a", outline="#3a2410", width=2)
    _arch(p, cx, cy - s * 0.02, s * 0.64, s * 0.24, "#a06a34", "#3a2410", 2, smooth=False)
    for dx in (-0.18, 0.18):
        p.rect(cx + s * dx - s * 0.04, cy - s * 0.24, cx + s * dx + s * 0.04, cy + s * 0.30, fill="#c9a23c", outline="")
    p.rect(cx - s * 0.05, cy + s * 0.06, cx + s * 0.05, cy + s * 0.16, fill="#e8c04a", outline="#8a6a1a", width=1)


def _icon_eggs(p: Painter, cx: float, cy: float, s: float, state: int | None = None) -> None:
    _oval(p, cx, cy + s * 0.18, s * 0.36, s * 0.16, "#8a6a48", "#4a3218", 2)
    for dx in (-0.16, 0.0, 0.16):
        _oval(p, cx + s * dx, cy + s * 0.02, s * 0.10, s * 0.14, "#e8c04a", "#8a6a1a", 1)
        _circle(p, cx + s * dx - s * 0.03, cy - s * 0.04, s * 0.03, "#fff0a8")


def _icon_trident(p: Painter, cx: float, cy: float, s: float, state: int | None = None) -> None:
    p.line([(cx, cy + s * 0.42), (cx, cy - s * 0.10)], fill="#c9a23c", width=max(3, s * 0.08))
    p.line([(cx - s * 0.20, cy - s * 0.08), (cx + s * 0.20, cy - s * 0.08)], fill="#e8c04a", width=max(2, s * 0.05))
    for dx in (-0.20, 0.0, 0.20):
        p.line([(cx + s * dx, cy - s * 0.08), (cx + s * dx, cy - s * 0.38)], fill="#e8c04a", width=max(2, s * 0.05))
        _poly(
            p,
            [(cx + s * dx - s * 0.04, cy - s * 0.38), (cx + s * dx, cy - s * 0.50), (cx + s * dx + s * 0.04, cy - s * 0.38)],
            "#e8c04a",
            "#8a6a1a",
            1,
        )
    _gem(p, cx, cy + s * 0.10, s * 0.06, s * 0.08, "#5fa8c4")


def _icon_vase(p: Painter, cx: float, cy: float, s: float, state: int | None = None) -> None:
    _poly(
        p,
        [
            (cx - s * 0.12, cy - s * 0.36),
            (cx + s * 0.12, cy - s * 0.36),
            (cx + s * 0.10, cy - s * 0.16),
            (cx + s * 0.26, cy + s * 0.10),
            (cx + s * 0.16, cy + s * 0.36),
            (cx - s * 0.16, cy + s * 0.36),
            (cx - s * 0.26, cy + s * 0.10),
            (cx - s * 0.10, cy - s * 0.16),
        ],
        "#7fa8c4",
        _INK,
        2,
        smooth=True,
    )
    p.line([(cx - s * 0.18, cy + s * 0.14), (cx + s * 0.18, cy + s * 0.14)], fill="#e8f4fa", width=2)
    _oval(p, cx, cy + s * 0.02, s * 0.10, s * 0.08, "#e8f4fa", "")


def _icon_emerald(p: Painter, cx: float, cy: float, s: float, state: int | None = None) -> None:
    _gem(p, cx, cy, s * 0.30, s * 0.36, "#3fa06a")


def _icon_pyramid(p: Painter, cx: float, cy: float, s: float, state: int | None = None) -> None:
    _poly(
        p,
        [(cx, cy - s * 0.40), (cx + s * 0.38, cy + s * 0.34), (cx - s * 0.38, cy + s * 0.34)],
        "#d9dde2",
        "#5d6570",
        2,
    )
    _poly(
        p,
        [(cx, cy - s * 0.40), (cx + s * 0.10, cy + s * 0.34), (cx - s * 0.38, cy + s * 0.34)],
        "#aeb6c1",
        "",
    )
    _poly(p, [(cx, cy - s * 0.40), (cx + s * 0.04, cy - s * 0.10), (cx - s * 0.04, cy - s * 0.10)], "#ffffff", "")


def _icon_pearl(p: Painter, cx: float, cy: float, s: float, state: int | None = None) -> None:
    _circle(p, cx, cy, s * 0.30, "#f4f0e2", "#a8a090", 2)
    _circle(p, cx - s * 0.10, cy - s * 0.10, s * 0.09, "#ffffff")
    _circle(p, cx + s * 0.10, cy + s * 0.08, s * 0.05, "#e8e4d6")


def _icon_rug(p: Painter, cx: float, cy: float, s: float, state: int | None = None) -> None:
    _poly(
        p,
        [(cx - s * 0.44, cy - s * 0.24), (cx + s * 0.44, cy - s * 0.24), (cx + s * 0.36, cy + s * 0.24), (cx - s * 0.36, cy + s * 0.24)],
        "#a03a3a",
        "#4a1414",
        2,
    )
    _poly(
        p,
        [(cx - s * 0.30, cy - s * 0.16), (cx + s * 0.30, cy - s * 0.16), (cx + s * 0.24, cy + s * 0.16), (cx - s * 0.24, cy + s * 0.16)],
        "#3a4a8a",
        "",
    )
    _gem(p, cx, cy, s * 0.08, s * 0.10, "#e8c04a")
    for dx in (-0.40, 0.40):
        p.line([(cx + s * dx, cy - s * 0.24), (cx + s * dx * 0.9, cy + s * 0.24)], fill="#e8dcc0", width=2)


def _icon_spices(p: Painter, cx: float, cy: float, s: float, state: int | None = None) -> None:
    _poly(
        p,
        [(cx - s * 0.32, cy + s * 0.02), (cx + s * 0.32, cy + s * 0.02), (cx + s * 0.20, cy + s * 0.32), (cx - s * 0.20, cy + s * 0.32)],
        "#b8912f",
        "#6b4f16",
        2,
    )
    for dx, colour in ((-0.14, "#c96a2a"), (0.02, "#d9a45a"), (0.16, "#8f5f2a")):
        _oval(p, cx + s * dx, cy - s * 0.04, s * 0.13, s * 0.10, colour, "")
    _circle(p, cx - s * 0.02, cy - s * 0.14, s * 0.03, "#e8dcc0")


def _icon_chain(p: Painter, cx: float, cy: float, s: float, state: int | None = None) -> None:
    for i in range(5):
        x = cx - s * 0.34 + i * s * 0.16
        y = cy + (s * 0.10 if i % 2 else -s * 0.06)
        _oval(p, x, y, s * 0.11, s * 0.16, None, "#e8c04a", max(2, s * 0.05))
    _circle(p, cx + s * 0.38, cy + s * 0.04, s * 0.05, "#e8c04a")


def _icon_dwarf(p: Painter, cx: float, cy: float, s: float, state: int | None = None) -> None:
    skin, tunic = "#c98f63", "#6b4a8a"
    p.line([(cx - s * 0.10, cy + s * 0.42), (cx - s * 0.06, cy + s * 0.10)], fill="#3a2a1e", width=max(3, s * 0.09))
    p.line([(cx + s * 0.10, cy + s * 0.42), (cx + s * 0.06, cy + s * 0.10)], fill="#3a2a1e", width=max(3, s * 0.09))
    _roundrect(p, cx - s * 0.18, cy - s * 0.12, cx + s * 0.18, cy + s * 0.16, s * 0.08, tunic, _INK, 2)
    _circle(p, cx, cy - s * 0.26, s * 0.15, skin, _INK, 2)
    _poly(
        p,
        [(cx - s * 0.14, cy - s * 0.18), (cx + s * 0.14, cy - s * 0.18), (cx, cy + s * 0.04)],
        "#d9d2c2",
        "",
    )
    p.rect(cx - s * 0.17, cy - s * 0.40, cx + s * 0.17, cy - s * 0.33, fill="#4a6a3a", outline=_INK, width=1)
    _circle(p, cx - s * 0.05, cy - s * 0.28, max(1.2, s * 0.02), _INK)
    _circle(p, cx + s * 0.05, cy - s * 0.28, max(1.2, s * 0.02), _INK)
    _poly(
        p,
        [(cx + s * 0.16, cy + s * 0.02), (cx + s * 0.38, cy - s * 0.10), (cx + s * 0.36, cy - s * 0.02), (cx + s * 0.18, cy + s * 0.08)],
        "#c9d0d8",
        _INK,
        1,
    )


ICONS: dict[str, IconPainter] = {
    "keys": _icon_keys,
    "lamp": _icon_lamp,
    "grate": _icon_grate,
    "cage": _icon_cage,
    "rod": _icon_rod,
    "treads": _icon_treads,
    "bird": _icon_bird,
    "door": _icon_door,
    "pillow": _icon_pillow,
    "snake": _icon_snake,
    "crystal": _icon_crystal,
    "tablet": _icon_tablet,
    "clam": _icon_clam,
    "oyster": _icon_oyster,
    "magazine": _icon_magazine,
    "dwarf": _icon_dwarf,
    "knife": _icon_knife,
    "food": _icon_food,
    "bottle": _icon_bottle,
    "water": _icon_water,
    "oil": _icon_oil,
    "mirror": _icon_mirror,
    "plant": _icon_plant,
    "stalactite": _icon_stalactite,
    "shadow": _icon_shadow,
    "axe": _icon_axe,
    "mural": _icon_mural,
    "pirate": _icon_pirate,
    "dragon": _icon_dragon,
    "bridge": _icon_bridge,
    "troll": _icon_troll,
    "bear": _icon_bear,
    "message": _icon_message,
    "geyser": _icon_geyser,
    "vending": _icon_vending,
    "batteries": _icon_batteries,
    "moss": _icon_moss,
    "gold": _icon_gold,
    "diamonds": _icon_diamonds,
    "silver": _icon_silver,
    "jewels": _icon_jewels,
    "coins": _icon_coins,
    "chest": _icon_chest,
    "eggs": _icon_eggs,
    "trident": _icon_trident,
    "vase": _icon_vase,
    "emerald": _icon_emerald,
    "pyramid": _icon_pyramid,
    "pearl": _icon_pearl,
    "rug": _icon_rug,
    "spices": _icon_spices,
    "chain": _icon_chain,
}

# ---------------------------------------------------------------------------
# Scene props: bigger decorations placed by a scene
# ---------------------------------------------------------------------------


def _prop_house(p: Painter, pal: dict[str, str], prop: "Prop") -> None:
    cx, base = prop.x * LOGICAL_W, prop.y * LOGICAL_H
    s = prop.scale
    w, h = 200 * s, 132 * s
    x0, x1, y0 = cx - w / 2, cx + w / 2, base - h
    _oval(p, cx, base + 4 * s, w * 0.55, 11 * s, pal["shadow"], "", stipple="gray50")
    p.rect(x0, y0, x1, base, fill=pal["brick"], outline=pal["brick_dark"], width=3)
    _bricks(p, pal, x0, y0, x1, base, 6, 7)
    _poly(
        p,
        [(x0 - 18 * s, y0 + 5 * s), (cx, y0 - 70 * s), (x1 + 18 * s, y0 + 5 * s)],
        pal["roof"],
        shade(pal["roof"], 0.65),
        3,
    )
    p.rect(cx + 42 * s, y0 - 58 * s, cx + 62 * s, y0 - 6 * s, fill=pal["brick_dark"], outline="")
    p.rect(cx + 38 * s, y0 - 64 * s, cx + 66 * s, y0 - 54 * s, fill=shade(pal["roof"], 0.8), outline="")
    # door
    p.rect(cx - 20 * s, base - 64 * s, cx + 20 * s, base, fill=pal["wood"], outline=shade(pal["wood"], 0.55), width=2)
    _circle(p, cx + 13 * s, base - 32 * s, 2.5 * s, pal["gold"])
    # lit windows
    for wx in (cx - w * 0.30, cx + w * 0.30):
        p.rect(wx - 15 * s, y0 + 26 * s, wx + 15 * s, y0 + 54 * s, fill=pal["glow"], outline=pal["wood"], width=2)
        p.line([(wx, y0 + 26 * s), (wx, y0 + 54 * s)], pal["wood"], width=2)
    # water trough at the foot of the wall
    _oval(p, cx - w * 0.36, base + 2 * s, 26 * s, 7 * s, pal["water"], pal["water_light"], 1)


def _prop_house_far(p: Painter, pal: dict[str, str], prop: "Prop") -> None:
    cx, base = prop.x * LOGICAL_W, prop.y * LOGICAL_H
    s = prop.scale
    w, h = 96 * s, 70 * s
    p.rect(cx - w / 2, base - h, cx + w / 2, base, fill=shade(pal["brick"], 0.82), outline="")
    _poly(
        p,
        [(cx - w / 2 - 8 * s, base - h + 3 * s), (cx, base - h - 34 * s), (cx + w / 2 + 8 * s, base - h + 3 * s)],
        shade(pal["roof"], 0.8),
        "",
    )
    for wx in (cx - w * 0.22, cx + w * 0.22):
        p.rect(wx - 6 * s, base - h * 0.62, wx + 6 * s, base - h * 0.34, fill=pal["glow"], outline="")


def _prop_trees(p: Painter, pal: dict[str, str], prop: "Prop") -> None:
    cx, base = prop.x * LOGICAL_W, prop.y * LOGICAL_H
    s = prop.scale
    rnd = random.Random(int(cx) + int(base))
    _tree(p, cx - 42 * s, base + 24 * s, 210 * s, pal, rnd)
    _tree(p, cx + 30 * s, base + 36 * s, 250 * s, pal, rnd)
    _tree(p, cx + 4 * s, base - 6 * s, 170 * s, pal, rnd)


def _prop_road(p: Painter, pal: dict[str, str], prop: "Prop") -> None:
    cx, cy = prop.x * LOGICAL_W, prop.y * LOGICAL_H
    s = prop.scale
    _poly(
        p,
        [(cx - 74 * s, cy + 70 * s), (cx + 74 * s, cy + 70 * s), (cx + 26 * s, cy - 46 * s), (cx - 26 * s, cy - 46 * s)],
        pal["dirt"],
        shade(pal["dirt"], 0.8),
        2,
    )
    p.line([(cx - 60 * s, cy + 60 * s), (cx - 22 * s, cy - 36 * s)], shade(pal["dirt"], 0.86), width=2)
    p.line([(cx + 60 * s, cy + 60 * s), (cx + 22 * s, cy - 36 * s)], shade(pal["dirt"], 0.86), width=2)


def _prop_stream(p: Painter, pal: dict[str, str], prop: "Prop") -> None:
    cx, cy = prop.x * LOGICAL_W, prop.y * LOGICAL_H
    s = prop.scale
    w, h = 165 * s, 34 * s
    _poly(
        p,
        [(cx - w, cy), (cx + w, cy), (cx + w * 0.72, cy + h * 2.4), (cx - w * 0.72, cy + h * 2.4)],
        pal["water"],
        pal["water_light"],
        2,
    )
    for i in range(4):
        t = (i + 1) / 5
        _oval(p, cx, cy + h * (0.5 + t * 1.2), w * (0.5 + t * 0.3), h * 0.22, None, pal["water_light"], 2)
    p.line([(cx - w, cy), (cx - w * 0.72, cy + h * 2.4)], fill=shade(pal["water"], 0.6), width=4)
    p.line([(cx + w, cy), (cx + w * 0.72, cy + h * 2.4)], fill=shade(pal["water"], 0.6), width=4)
    for dx in (-0.5, 0.1, 0.55):
        _oval(p, cx + w * dx, cy + h * 2.5, 18 * s, 8 * s, pal["rock_light"], pal["rock_dark"], 1)


def _prop_spring(p: Painter, pal: dict[str, str], prop: "Prop") -> None:
    cx, cy = prop.x * LOGICAL_W, prop.y * LOGICAL_H
    s = prop.scale
    _oval(p, cx, cy, 118 * s, 36 * s, pal["rock"], pal["rock_light"], 3)
    _oval(p, cx, cy, 96 * s, 26 * s, pal["water"], "")
    _ripples(p, pal, cx, cy, 80 * s, 20 * s, 4)
    _circle(p, cx - 30 * s, cy - 8 * s, 5 * s, pal["water_light"])


def _prop_grate(p: Painter, pal: dict[str, str], prop: "Prop") -> None:
    _icon_grate(p, prop.x * LOGICAL_W, prop.y * LOGICAL_H, 180 * prop.scale)


def _prop_stairs(p: Painter, pal: dict[str, str], prop: "Prop") -> None:
    _icon_treads(p, prop.x * LOGICAL_W, prop.y * LOGICAL_H, 190 * prop.scale)


def _prop_stalactite(p: Painter, pal: dict[str, str], prop: "Prop") -> None:
    _icon_stalactite(p, prop.x * LOGICAL_W, prop.y * LOGICAL_H, 200 * prop.scale)


def _prop_stalagmite(p: Painter, pal: dict[str, str], prop: "Prop") -> None:
    cx, cy = prop.x * LOGICAL_W, prop.y * LOGICAL_H
    s = prop.scale
    _poly(
        p,
        [(cx - 30 * s, cy + 70 * s), (cx + 30 * s, cy + 70 * s), (cx + 9 * s, cy - 70 * s), (cx - 9 * s, cy - 70 * s)],
        pal["rock_light"],
        pal["rock_dark"],
        2,
    )
    p.line([(cx - 12 * s, cy + 54 * s), (cx - 3 * s, cy - 40 * s)], fill=shade(pal["rock_light"], 1.15), width=3)


def _prop_column(p: Painter, pal: dict[str, str], prop: "Prop") -> None:
    cx, _ = prop.x * LOGICAL_W, prop.y * LOGICAL_H
    s = prop.scale
    w = 38 * s
    p.rect(cx - w, -10, cx + w, 560, fill=pal["warm"], outline=shade(pal["warm"], 0.65), width=3)
    for i in range(7):
        y = 40 + i * 78
        p.line([(cx - w * 0.7, y), (cx + w * 0.7, y + 18)], fill=shade(pal["warm"], 0.8), width=3)
    p.line([(cx - w * 0.45, 20), (cx - w * 0.30, 540)], fill=mix(pal["warm"], "#ffffff", 0.25), width=5)


def _prop_pit(p: Painter, pal: dict[str, str], prop: "Prop") -> None:
    cx, cy = prop.x * LOGICAL_W, prop.y * LOGICAL_H
    s = prop.scale
    _oval(p, cx, cy, 104 * s, 30 * s, pal["rock_dark"], pal["rock_light"], 3)
    _oval(p, cx, cy + 4 * s, 78 * s, 18 * s, "#08070c", "")
    _oval(p, cx, cy + 8 * s, 48 * s, 9 * s, "#14121a", "")
    p.line([(cx - 96 * s, cy - 4 * s), (cx - 40 * s, cy + 2 * s)], fill=pal["rock_light"], width=2)


def _prop_slit(p: Painter, pal: dict[str, str], prop: "Prop") -> None:
    cx, cy = prop.x * LOGICAL_W, prop.y * LOGICAL_H
    s = prop.scale
    p.rect(cx - 5 * s, cy - 48 * s, cx + 5 * s, cy + 34 * s, fill="#08070c", outline=pal["rock_light"], width=2)
    for i in range(4):
        x = cx + (i - 1.5) * 16 * s
        p.line([(cx + (i - 1.5) * 4 * s, cy - 20 * s), (x, cy - 48 * s)], fill=pal["water_light"], width=2)
    _oval(p, cx, cy + 36 * s, 30 * s, 8 * s, pal["water"], "")


def _prop_crack(p: Painter, pal: dict[str, str], prop: "Prop") -> None:
    cx, cy = prop.x * LOGICAL_W, prop.y * LOGICAL_H
    s = prop.scale
    points = [(cx - 40 * s, cy - 90 * s), (cx - 8 * s, cy - 30 * s), (cx + 18 * s, cy + 8 * s), (cx - 4 * s, cy + 40 * s), (cx + 24 * s, cy + 96 * s)]
    p.line(points, fill="#08070c", width=max(3, 9 * s), smooth=True)
    p.line([(x + 4 * s, y) for x, y in points], fill=pal["rock_light"], width=2, smooth=True)


def _prop_hole(p: Painter, pal: dict[str, str], prop: "Prop") -> None:
    cx, cy = prop.x * LOGICAL_W, prop.y * LOGICAL_H
    s = prop.scale
    _oval(p, cx, cy, 72 * s, 24 * s, pal["rock_dark"], pal["rock_light"], 3)
    _oval(p, cx, cy + 3 * s, 52 * s, 15 * s, "#08070c", "")


def _prop_boulders(p: Painter, pal: dict[str, str], prop: "Prop") -> None:
    cx, cy = prop.x * LOGICAL_W, prop.y * LOGICAL_H
    s = prop.scale
    rnd = random.Random(int(cx * 3 + cy))
    for dx, dy, r in ((-0.42, 0.06, 0.30), (0.05, -0.04, 0.38), (0.46, 0.10, 0.26), (-0.05, 0.24, 0.30)):
        rx, ry = r * 90 * s, r * 58 * s
        x, y = cx + dx * 130 * s, cy + dy * 90 * s
        points = [
            (x - rx, y),
            (x - rx * 0.5, y - ry),
            (x + rx * 0.4, y - ry * 0.9),
            (x + rx, y + ry * 0.1),
            (x + rx * 0.5, y + ry),
            (x - rx * 0.4, y + ry * 0.9),
        ]
        points = [(px + rnd.uniform(-4, 4), py + rnd.uniform(-4, 4)) for px, py in points]
        _poly(p, points, pal["rock"], pal["rock_dark"], 2, smooth=True)
        p.line([(x - rx * 0.4, y - ry * 0.4), (x + rx * 0.1, y - ry * 0.5)], fill=pal["rock_light"], width=2)


def _prop_mist(p: Painter, pal: dict[str, str], prop: "Prop") -> None:
    _mist(p, pal, prop.x * LOGICAL_W, prop.y * LOGICAL_H, 190 * prop.scale, 34 * prop.scale, 3)


def _prop_waterfall(p: Painter, pal: dict[str, str], prop: "Prop") -> None:
    cx, cy = prop.x * LOGICAL_W, prop.y * LOGICAL_H
    s = prop.scale
    p.rect(cx - 44 * s, cy - 190 * s, cx + 44 * s, cy + 120 * s, fill=pal["water_light"], outline="", stipple="gray50")
    for dx in (-30, -10, 10, 30):
        p.line(
            [(cx + dx * s, cy - 180 * s), (cx + dx * s * 0.8, cy + 108 * s)],
            fill=mix(pal["water_light"], "#ffffff", 0.6),
            width=max(2, 4 * s),
        )
    _oval(p, cx, cy + 122 * s, 100 * s, 24 * s, pal["water"], "")
    _mist(p, pal, cx, cy + 110 * s, 120 * s, 20 * s, 2)


def _prop_oil_pool(p: Painter, pal: dict[str, str], prop: "Prop") -> None:
    cx, cy = prop.x * LOGICAL_W, prop.y * LOGICAL_H
    s = prop.scale
    _oval(p, cx, cy, 64 * s, 20 * s, "#1b2a1b", "#3a5a2a", 2)
    _oval(p, cx, cy, 48 * s, 13 * s, "#3a5a2a", "")
    p.line([(cx - 36 * s, cy - 2 * s), (cx + 34 * s, cy + 3 * s)], fill="#8fd3a0", width=2, smooth=True)
    p.line([(cx - 20 * s, cy + 6 * s), (cx + 22 * s, cy + 1 * s)], fill="#b8e0c0", width=2, smooth=True)


def _prop_plant(p: Painter, pal: dict[str, str], prop: "Prop") -> None:
    _icon_plant(p, prop.x * LOGICAL_W, prop.y * LOGICAL_H, 260 * prop.scale)


def _prop_window(p: Painter, pal: dict[str, str], prop: "Prop") -> None:
    cx, cy = prop.x * LOGICAL_W, prop.y * LOGICAL_H
    s = prop.scale
    w, h = 116 * s, 74 * s
    p.rect(cx - w, cy - h, cx + w, cy + h, fill="#0b0d10", outline=pal["rock_light"], width=7)
    _mist(p, pal, cx, cy + h * 0.4, w * 0.8, h * 0.4, 2)
    p.line([(cx - w * 0.7, cy + h * 0.8), (cx + w * 0.7, cy + h * 0.8)], fill=pal["rock"], width=4)
    _oval(p, cx + w * 0.2, cy - h * 0.2, w * 0.18, h * 0.1, pal["rock"], "")


def _prop_mural(p: Painter, pal: dict[str, str], prop: "Prop") -> None:
    _icon_mural(p, prop.x * LOGICAL_W, prop.y * LOGICAL_H, 260 * prop.scale)


def _prop_curtains(p: Painter, pal: dict[str, str], prop: "Prop") -> None:
    cx, cy = prop.x * LOGICAL_W, prop.y * LOGICAL_H
    s = prop.scale
    for dx, w in ((-110, 34), (-40, 40), (32, 36), (104, 30)):
        x = cx + dx * s
        _roundrect(p, x - w * s, cy - 220 * s, x + w * s, cy + 190 * s, 14 * s, pal["warm"], shade(pal["warm"], 0.6), 2)
        p.line([(x, cy - 210 * s), (x + 6 * s, cy + 180 * s)], fill=shade(pal["warm"], 0.75), width=3, smooth=True)
    p.rect(cx - 170 * s, cy - 240 * s, cx + 150 * s, cy - 214 * s, fill=shade(pal["warm"], 0.5), outline="")


def _prop_slab(p: Painter, pal: dict[str, str], prop: "Prop") -> None:
    cx, cy = prop.x * LOGICAL_W, prop.y * LOGICAL_H
    s = prop.scale
    _oval(p, cx, cy, 220 * s, 62 * s, pal["rock"], pal["rock_light"], 4)
    _oval(p, cx, cy - 6 * s, 196 * s, 50 * s, shade(pal["rock"], 1.1), "")
    for dx in (-90, -20, 60):
        p.line(
            [(cx + dx * s, cy - 34 * s), (cx + (dx + 26) * s, cy + 8 * s), (cx + (dx + 4) * s, cy + 34 * s)],
            fill=pal["rock_dark"],
            width=2,
            smooth=True,
        )


def _prop_sign(p: Painter, pal: dict[str, str], prop: "Prop") -> None:
    cx, cy = prop.x * LOGICAL_W, prop.y * LOGICAL_H
    s = prop.scale
    p.rect(cx - 7 * s, cy, cx + 7 * s, cy + 150 * s, fill=pal["wood"], outline=shade(pal["wood"], 0.6), width=2)
    p.rect(cx - 92 * s, cy - 54 * s, cx + 92 * s, cy + 20 * s, fill="#a87a4a", outline="#3a2410", width=4)
    p.text(cx, cy - 34 * s, "CAUTION", fill="#2a1a10", size=22 * s, bold=True)
    p.text(cx, cy - 4 * s, "BARREN", fill="#2a1a10", size=16 * s, bold=True)


def _prop_note(p: Painter, pal: dict[str, str], prop: "Prop") -> None:
    cx, cy = prop.x * LOGICAL_W, prop.y * LOGICAL_H
    s = prop.scale
    _poly(
        p,
        [(cx - 34 * s, cy - 44 * s), (cx + 32 * s, cy - 48 * s), (cx + 36 * s, cy + 40 * s), (cx - 30 * s, cy + 44 * s)],
        "#e8dcc0",
        "#8a7a5a",
        2,
    )
    for i in range(5):
        y = cy - 30 * s + i * 14 * s
        p.line([(cx - 22 * s, y), (cx + 24 * s, y - 2 * s)], fill="#6b6157", width=2)
    _circle(p, cx, cy - 46 * s, 3 * s, "#8a7a5a")


def _prop_cobbles(p: Painter, pal: dict[str, str], prop: "Prop") -> None:
    cx, cy = prop.x * LOGICAL_W, prop.y * LOGICAL_H
    s = prop.scale
    rnd = random.Random(int(cx) + 11)
    for i in range(22):
        x = cx + rnd.uniform(-210, 210) * s
        y = cy + rnd.uniform(-26, 30) * s
        _oval(
            p,
            x,
            y,
            rnd.uniform(10, 22) * s,
            rnd.uniform(5, 11) * s,
            pal["rock_light"] if i % 3 else pal["rock"],
            pal["rock_dark"],
            1,
        )


def _prop_volcano(p: Painter, pal: dict[str, str], prop: "Prop") -> None:
    cx, cy = prop.x * LOGICAL_W, prop.y * LOGICAL_H
    s = prop.scale
    _glow(p, cx, cy - 40 * s, 190 * s, pal["lava_light"], pal["sky_bottom"], 8)
    _poly(
        p,
        [(cx - 260 * s, cy + 120 * s), (cx - 70 * s, cy - 60 * s), (cx + 70 * s, cy - 60 * s), (cx + 260 * s, cy + 120 * s)],
        shade(pal["rock"], 0.95),
        pal["rock_dark"],
        2,
    )
    _poly(p, [(cx - 70 * s, cy - 60 * s), (cx, cy - 20 * s), (cx + 70 * s, cy - 60 * s), (cx + 34 * s, cy - 90 * s), (cx - 34 * s, cy - 90 * s)], pal["lava"])
    p.line([(cx - 20 * s, cy - 20 * s), (cx - 40 * s, cy + 110 * s)], fill=pal["lava_light"], width=max(3, 8 * s), smooth=True)
    p.line([(cx + 26 * s, cy - 24 * s), (cx + 60 * s, cy + 100 * s)], fill=pal["lava"], width=max(3, 6 * s), smooth=True)


def _prop_mirror_lake(p: Painter, pal: dict[str, str], prop: "Prop") -> None:
    cx, cy = prop.x * LOGICAL_W, prop.y * LOGICAL_H
    s = prop.scale
    _oval(p, cx, cy, 250 * s, 44 * s, pal["water"], pal["water_light"], 3)
    for i in range(6):
        t = (i + 1) / 7
        _oval(p, cx, cy - 30 * s + t * 60 * s, 210 * s * (1 - t * 0.4), 5 * s, None, pal["water_light"], 2)
    _oval(p, cx, cy - 6 * s, 90 * s, 10 * s, pal["mist"], "", stipple="gray25")


def _prop_dust(p: Painter, pal: dict[str, str], prop: "Prop") -> None:
    cx, cy = prop.x * LOGICAL_W, prop.y * LOGICAL_H
    s = prop.scale
    rnd = random.Random(int(cx) + 5)
    _speckle(p, rnd, cx - 260 * s, cy - 40 * s, cx + 260 * s, cy + 40 * s, pal["rock_light"], 90, 4)


def _prop_sewer(p: Painter, pal: dict[str, str], prop: "Prop") -> None:
    cx, cy = prop.x * LOGICAL_W, prop.y * LOGICAL_H
    s = prop.scale
    p.rect(cx - 220 * s, cy - 90 * s, cx + 220 * s, cy + 120 * s, fill=shade(pal["rock"], 0.8), outline="")
    for dx in (-100, 100):
        _circle(p, cx + dx * s, cy + 10 * s, 78 * s, shade(pal["rock"], 0.55), pal["rock_light"], 6)
        _circle(p, cx + dx * s, cy + 10 * s, 58 * s, "#0b0d10")
        _oval(p, cx + dx * s, cy + 56 * s, 54 * s, 18 * s, pal["water"], "")


def _prop_dome(p: Painter, pal: dict[str, str], prop: "Prop") -> None:
    cx, cy = prop.x * LOGICAL_W, prop.y * LOGICAL_H
    s = prop.scale
    _arch(p, cx, cy + 120 * s, 420 * s, 220 * s, shade(pal["rock"], 0.8), pal["rock_light"], 4)
    for dx in (-140, -60, 20, 100):
        p.line(
            [(cx + dx * s, cy + 110 * s), (cx + dx * 0.4 * s, cy - 70 * s)],
            fill=pal["rock_light"],
            width=3,
            smooth=True,
        )


def _prop_debris(p: Painter, pal: dict[str, str], prop: "Prop") -> None:
    cx, cy = prop.x * LOGICAL_W, prop.y * LOGICAL_H
    s = prop.scale
    rnd = random.Random(int(cx) + 23)
    for i in range(7):
        x = cx + rnd.uniform(-170, 170) * s
        y = cy + rnd.uniform(-24, 26) * s
        if i % 2:
            p.rect(x - 30 * s, y - 5 * s, x + 30 * s, y + 5 * s, fill=pal["wood"], outline=shade(pal["wood"], 0.6), width=1)
        else:
            _oval(p, x, y, 20 * s, 12 * s, pal["rock"], pal["rock_dark"], 1)
    _speckle(p, rnd, cx - 200 * s, cy - 30 * s, cx + 200 * s, cy + 34 * s, pal["rock_light"], 40, 3)


def _prop_lava(p: Painter, pal: dict[str, str], prop: "Prop") -> None:
    cx, cy = prop.x * LOGICAL_W, prop.y * LOGICAL_H
    s = prop.scale
    _poly(
        p,
        [(cx - 360 * s, cy + 40 * s), (cx - 120 * s, cy - 10 * s), (cx + 160 * s, cy + 6 * s), (cx + 380 * s, cy + 44 * s), (cx + 380 * s, cy + 80 * s), (cx - 360 * s, cy + 80 * s)],
        pal["lava"],
        "",
    )
    for i in range(5):
        x = cx - 260 * s + i * 130 * s
        p.line([(x, cy + 30 * s), (x + 60 * s, cy + 46 * s)], fill=pal["lava_light"], width=3, smooth=True)


def _prop_bones(p: Painter, pal: dict[str, str], prop: "Prop") -> None:
    cx, cy = prop.x * LOGICAL_W, prop.y * LOGICAL_H
    s = prop.scale
    _circle(p, cx, cy - 8 * s, 16 * s, pal["bone"], "#6b6157", 2)
    _circle(p, cx - 6 * s, cy - 10 * s, 4 * s, "#2a2620")
    _circle(p, cx + 6 * s, cy - 10 * s, 4 * s, "#2a2620")
    p.line([(cx - 4 * s, cy + 2 * s), (cx + 4 * s, cy + 2 * s)], fill="#2a2620", width=2)
    for dx, dy in ((-40, 16), (34, 20), (10, 30)):
        p.line([(cx + dx * s, cy + dy * s), (cx + (dx + 26) * s, cy + (dy - 4) * s)], fill=pal["bone"], width=max(2, 5 * s))
        _circle(p, cx + (dx + 26) * s, cy + (dy - 4) * s, 3 * s, pal["bone"])


def _prop_cavein(p: Painter, pal: dict[str, str], prop: "Prop") -> None:
    cx, cy = prop.x * LOGICAL_W, prop.y * LOGICAL_H
    s = prop.scale
    rnd = random.Random(int(cx) + 31)
    _poly(p, [(cx - 260 * s, cy + 140 * s), (cx - 240 * s, cy - 120 * s), (cx + 240 * s, cy - 140 * s), (cx + 260 * s, cy + 140 * s)], pal["rock_dark"], "")
    for i in range(12):
        x = cx + rnd.uniform(-230, 230) * s
        y = cy + rnd.uniform(-110, 130) * s
        r = rnd.uniform(22, 52) * s
        _oval(p, x, y, r, r * 0.7, pal["rock"] if i % 2 else pal["rock_light"], pal["rock_dark"], 2)
    _speckle(p, rnd, cx - 240 * s, cy - 120 * s, cx + 240 * s, cy + 130 * s, pal["rock_light"], 50, 4)


def _prop_green_glow(p: Painter, pal: dict[str, str], prop: "Prop") -> None:
    cx, cy = prop.x * LOGICAL_W, prop.y * LOGICAL_H
    s = prop.scale
    _glow(p, cx, cy, 300 * s, "#5fd36a", pal["rock_dark"], 8)
    _oval(p, cx, cy, 220 * s, 150 * s, "#5fd36a", "", stipple="gray12")
    for i in range(7):
        x = cx + (i - 3) * 54 * s
        p.line([(x, cy + 120 * s), (x + 8 * s, cy - 100 * s)], fill="#8fe89a", width=2, smooth=True)


def _prop_light_shaft(p: Painter, pal: dict[str, str], prop: "Prop") -> None:
    cx, cy = prop.x * LOGICAL_W, prop.y * LOGICAL_H
    s = prop.scale
    _poly(p, [(cx - 70 * s, 0), (cx + 70 * s, 0), (cx + 190 * s, cy + 210 * s), (cx - 190 * s, cy + 210 * s)], pal["glow"], "", smooth=False)
    _oval(p, cx, cy + 200 * s, 190 * s, 40 * s, pal["glow"], "", stipple="gray12")
    _oval(p, cx, 8, 70 * s, 18 * s, mix(pal["glow"], "#ffffff", 0.5), "")


def _prop_warm_glow(p: Painter, pal: dict[str, str], prop: "Prop") -> None:
    cx, cy = prop.x * LOGICAL_W, prop.y * LOGICAL_H
    s = prop.scale
    _glow(p, cx, cy, 320 * s, pal["lava_light"], pal["rock_dark"], 8)
    _oval(p, cx, cy, 240 * s, 150 * s, pal["lava"], "", stipple="gray12")
    for i in range(6):
        y = cy - 80 * s + i * 34 * s
        p.line([(cx - 220 * s, y), (cx + 220 * s, y + 8 * s)], fill=pal["lava_light"], width=2, smooth=True)


def _prop_rubble(p: Painter, pal: dict[str, str], prop: "Prop") -> None:
    cx, cy = prop.x * LOGICAL_W, prop.y * LOGICAL_H
    s = prop.scale
    for dx, dy, r in ((-46, 6, 16), (-12, -2, 22), (26, 8, 18), (54, 2, 12), (6, 18, 14)):
        _oval(p, cx + dx * s, cy + dy * s, r * s, r * 0.6 * s, pal["rock"], pal["rock_dark"], 1)


def _prop_chasm_ledge(p: Painter, pal: dict[str, str], prop: "Prop") -> None:
    cx, cy = prop.x * LOGICAL_W, prop.y * LOGICAL_H
    s = prop.scale
    _poly(
        p,
        [(cx - 420 * s, cy + 60 * s), (cx + 420 * s, cy + 60 * s), (cx + 320 * s, cy - 20 * s), (cx - 320 * s, cy - 20 * s)],
        pal["rock"],
        pal["rock_light"],
        3,
    )
    _poly(
        p,
        [(cx - 300 * s, cy - 18 * s), (cx + 300 * s, cy - 18 * s), (cx + 250 * s, cy + 22 * s), (cx - 250 * s, cy + 22 * s)],
        "#08070c",
        "",
    )
    _mist(p, pal, cx, cy - 6 * s, 260 * s, 16 * s, 2)


PROPS: dict[str, Callable[[Painter, dict[str, str], "Prop"], None]] = {
    "house": _prop_house,
    "house_far": _prop_house_far,
    "trees": _prop_trees,
    "road": _prop_road,
    "stream": _prop_stream,
    "spring": _prop_spring,
    "grate": _prop_grate,
    "stairs": _prop_stairs,
    "stalactite": _prop_stalactite,
    "stalagmite": _prop_stalagmite,
    "column": _prop_column,
    "pit": _prop_pit,
    "slit": _prop_slit,
    "crack": _prop_crack,
    "hole": _prop_hole,
    "boulders": _prop_boulders,
    "mist": _prop_mist,
    "waterfall": _prop_waterfall,
    "oil_pool": _prop_oil_pool,
    "plant": _prop_plant,
    "window": _prop_window,
    "mural": _prop_mural,
    "curtains": _prop_curtains,
    "slab": _prop_slab,
    "sign": _prop_sign,
    "note": _prop_note,
    "cobbles": _prop_cobbles,
    "volcano": _prop_volcano,
    "mirror_lake": _prop_mirror_lake,
    "dust": _prop_dust,
    "sewer": _prop_sewer,
    "dome": _prop_dome,
    "debris": _prop_debris,
    "lava": _prop_lava,
    "bones": _prop_bones,
    "cavein": _prop_cavein,
    "green_glow": _prop_green_glow,
    "light_shaft": _prop_light_shaft,
    "warm_glow": _prop_warm_glow,
    "rubble": _prop_rubble,
    "chasm_ledge": _prop_chasm_ledge,
}


# ---------------------------------------------------------------------------
# Public drawing entry points
# ---------------------------------------------------------------------------


def draw_scene(p: Painter, scene: "Scene", dark: bool = False) -> None:
    """Paint a whole scene (backdrop, props, and a vignette when dark)."""
    pal = palette(scene.palette, dark)
    rnd = random.Random(scene.seed * 7919 + 13)
    backdrop = BACKDROPS.get(scene.backdrop)
    if backdrop is not None:
        backdrop(p, pal, rnd)
    for prop in scene.props:
        painter = PROPS.get(prop.kind)
        if painter is not None:
            painter(p, pal, prop)
    if dark:
        p.rect(0, 0, LOGICAL_W, LOGICAL_H, fill="#000000", outline="", stipple="gray12")
        for x0, y0, x1, y1 in (
            (0, 0, LOGICAL_W, 80),
            (0, LOGICAL_H - 80, LOGICAL_W, LOGICAL_H),
            (0, 0, 80, LOGICAL_H),
            (LOGICAL_W - 80, 0, LOGICAL_W, LOGICAL_H),
        ):
            p.rect(x0, y0, x1, y1, fill="#000000", outline="", stipple="gray50")


def draw_item(
    p: Painter,
    obj: int,
    cx: float,
    cy: float,
    size: float,
    state: int | None = None,
    lit: bool = False,
) -> None:
    """Paint one object's icon; ``state`` carries bottle/lamp state."""
    from .scenes import ITEM_ICONS  # local imports keep art usable on its own
    from .vocabulary import Object

    painter = ICONS.get(ITEM_ICONS.get(obj, ""))
    if painter is None:
        return
    _oval(p, cx, cy + size * 0.44, size * 0.36, size * 0.09, "#000000", "", stipple="gray50")
    if obj == int(Object.LAMP):
        state = 1 if lit else 0
    painter(p, cx, cy, size, state)


def draw_icon(p: Painter, kind: str, cx: float, cy: float, size: float, state: int | None = None) -> None:
    """Paint a named icon (used by props and tests)."""
    painter = ICONS.get(kind)
    if painter is not None:
        painter(p, cx, cy, size, state)


def backdrop_names() -> frozenset[str]:
    return frozenset(BACKDROPS)


def prop_names() -> frozenset[str]:
    return frozenset(PROPS)


def icon_names() -> frozenset[str]:
    return frozenset(ICONS)


__all__ = [
    "BACKDROPS",
    "ICONS",
    "LOGICAL_H",
    "LOGICAL_W",
    "PALETTES",
    "PROPS",
    "Painter",
    "backdrop_names",
    "draw_icon",
    "draw_item",
    "draw_scene",
    "icon_names",
    "luminance",
    "mix",
    "palette",
    "prop_names",
    "shade",
]


