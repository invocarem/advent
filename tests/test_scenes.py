"""Tests for the picture layer: scene coverage, names, and painters."""

from __future__ import annotations

import math

import pytest

from advent import art, scenes
from advent.vocabulary import (
    Location,
    Motion,
    Object,
    WordType,
    lookup,
)


class RecordingPainter:
    """A painter that records what the art asks for, and validates it."""

    def __init__(self) -> None:
        self.ops = 0
        self.fills: list[str] = []
        self.colours: set[str] = set()
        self.bounds = [math.inf, math.inf, -math.inf, -math.inf]

    def _point(self, x: float, y: float) -> None:
        assert isinstance(x, (int, float)) and isinstance(y, (int, float))
        assert math.isfinite(x) and math.isfinite(y), (x, y)
        assert -2000 <= x <= 3000 and -2000 <= y <= 2000, (x, y)
        self.bounds[0] = min(self.bounds[0], x)
        self.bounds[1] = min(self.bounds[1], y)
        self.bounds[2] = max(self.bounds[2], x)
        self.bounds[3] = max(self.bounds[3], y)

    def _colour(self, colour: str | None) -> None:
        if colour:
            assert colour.startswith("#") and len(colour) == 7, colour
            int(colour[1:], 16)
            self.colours.add(colour.lower())

    def rect(self, x0, y0, x1, y1, *, fill=None, outline=None, width=1, stipple=None):
        self._point(x0, y0)
        self._point(x1, y1)
        self._colour(fill)
        self._colour(outline)
        if fill:
            self.fills.append(fill)
        self.ops += 1

    def oval(self, x0, y0, x1, y1, *, fill=None, outline=None, width=1, stipple=None):
        self._point(x0, y0)
        self._point(x1, y1)
        self._colour(fill)
        self._colour(outline)
        if fill:
            self.fills.append(fill)
        self.ops += 1

    def polygon(self, points, *, fill=None, outline=None, width=1, stipple=None, smooth=False):
        for x, y in points:
            self._point(x, y)
        self._colour(fill)
        self._colour(outline)
        if fill:
            self.fills.append(fill)
        self.ops += 1

    def line(self, points, fill, *, width=1, smooth=False):
        for x, y in points:
            self._point(x, y)
        self._colour(fill)
        self.ops += 1

    def text(self, x, y, text, *, fill, size=14, anchor="center", bold=False):
        self._point(x, y)
        self._colour(fill)
        assert text
        self.ops += 1

    @property
    def lightness(self) -> float:
        values = [art.luminance(colour) for colour in self.fills]
        assert values, "nothing was filled"
        return sum(values) / len(values)


ALL_LOCATIONS = range(int(Location.ROAD), int(Location.DIDIT) + 1)
ALL_OBJECTS = range(1, int(Object.CHAIN) + 1)


def test_every_location_has_a_scene() -> None:
    missing = [loc for loc in ALL_LOCATIONS if loc not in scenes.SCENES]
    assert not missing, missing
    assert int(Location.INHAND) in scenes.SCENES
    assert int(Location.LIMBO) in scenes.SCENES
    assert len(scenes.SCENES) == len(list(ALL_LOCATIONS)) + 2


def test_unknown_location_falls_back() -> None:
    assert scenes.scene_for(99999) is scenes.FALLBACK_SCENE


def test_scene_parts_are_known_and_in_range() -> None:
    for loc, scene in scenes.SCENES.items():
        assert scene.backdrop in art.BACKDROPS, (loc, scene.backdrop)
        assert scene.palette in art.PALETTES, (loc, scene.palette)
        for prop in scene.props:
            assert prop.kind in art.PROPS, (loc, prop.kind)
            assert 0.0 <= prop.x <= 1.0, (loc, prop)
            assert 0.0 <= prop.y <= 1.0, (loc, prop)
            assert prop.scale > 0, (loc, prop)


def test_scenes_are_deterministic() -> None:
    for loc in ALL_LOCATIONS:
        assert scenes.scene_for(loc) == scenes.scene_for(loc)


def test_every_object_has_a_label_icon_and_optional_word() -> None:
    for obj in ALL_OBJECTS:
        assert scenes.item_label(obj).strip(), obj
        kind = scenes.ITEM_ICONS[obj]
        assert kind in art.ICONS, (obj, kind)
        word = scenes.item_word(obj)
        if word is not None:
            meaning = lookup(word)
            assert meaning is not None, (obj, word)
            assert meaning[0] is WordType.OBJECT, (obj, word, meaning)


def test_actor_slots_are_real_objects() -> None:
    for obj, (x, y, scale) in scenes.ACTOR_SLOTS.items():
        assert obj in scenes.ITEM_ICONS, obj
        assert 0.0 <= x <= 1.0 and 0.0 <= y <= 1.0, (obj, x, y)
        assert scale > 0, (obj, scale)
        assert scenes.is_actor(obj)


def test_every_motion_has_a_working_exit_label() -> None:
    for motion in Motion:
        label, command = scenes.MOTION_LABELS[int(motion)]
        assert label.strip()
        meaning = lookup(command)
        assert meaning is not None, (motion, command)
        assert meaning[0] is WordType.MOTION, (motion, command, meaning)
        assert meaning[1] == int(motion), (motion, command, meaning)
        assert scenes.motion_label(int(motion)) == label
        assert scenes.motion_command(int(motion)) == command


def test_exit_order_covers_every_labelled_motion() -> None:
    assert set(scenes.EXIT_ORDER) == set(scenes.MOTION_LABELS)
    ordered = scenes.sorted_motions([int(Motion.S), int(Motion.N), int(Motion.CAVE)])
    assert ordered == [int(Motion.N), int(Motion.S), int(Motion.CAVE)]


def test_every_scene_paints() -> None:
    for loc in scenes.SCENES:
        painter = RecordingPainter()
        art.draw_scene(painter, scenes.scene_for(loc))
        assert painter.ops > 12, loc
        assert painter.colours, loc


def test_dark_scenes_are_darker() -> None:
    for loc in (
        int(Location.ROAD),
        int(Location.HOUSE),
        int(Location.EMIST),
        int(Location.GIANT),
        int(Location.VIEW),
    ):
        light = RecordingPainter()
        dark = RecordingPainter()
        scene = scenes.scene_for(loc)
        art.draw_scene(light, scene)
        art.draw_scene(dark, scene, dark=True)
        assert dark.lightness < light.lightness * 0.6, (loc, light.lightness, dark.lightness)


def test_every_object_paints() -> None:
    for obj in ALL_OBJECTS:
        painter = RecordingPainter()
        art.draw_item(painter, obj, 500.0, 300.0, 80.0)
        assert painter.ops >= 2, obj
        for size in (32.0, 260.0):
            painter = RecordingPainter()
            art.draw_item(painter, obj, 500.0, 300.0, size, state=2, lit=True)
            assert painter.ops >= 2, (obj, size)


def test_icon_and_prop_names_are_complete() -> None:
    referenced_icons = set(scenes.ITEM_ICONS.values())
    assert referenced_icons <= art.icon_names()
    assert set(scenes.SCENES.values()) and all(
        scene.backdrop in art.backdrop_names() for scene in scenes.SCENES.values()
    )
    assert all(
        prop.kind in art.prop_names()
        for scene in scenes.SCENES.values()
        for prop in scene.props
    )


@pytest.mark.parametrize("palette", sorted(art.PALETTES))
def test_palettes_have_the_base_keys(palette: str) -> None:
    from advent.art import _BASE

    assert set(_BASE) <= set(art.PALETTES[palette])
