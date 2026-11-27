"""Tests for the read-only views the front ends use."""

from __future__ import annotations

from collections.abc import Iterable

import pytest

from advent import data as D
from advent.game import Console, Game
from advent.vocabulary import Location, Motion, Object


class Answers:
    """A minimal scripted console (the GUI bridge is tested separately)."""

    def __init__(self, answers: Iterable[str] = ("n",)) -> None:
        self.answers = list(answers)
        self.output: list[str] = []

    def write(self, text: str) -> None:
        self.output.append(text)

    def read_line(self, prompt: str) -> str:
        self.output.append(prompt)
        return self.answers.pop(0) if self.answers else ""


def make_game(answers: Iterable[str] = ("n",)) -> Game:
    return Game(Answers(answers), seed=7)


def test_possible_motions_does_not_touch_the_game() -> None:
    game = make_game()
    before = (
        game.rng.rx,
        game.loc,
        game.newloc,
        list(game.place),
        list(game.prop),
        list(game.first),
        game.holding,
    )
    motions = game.possible_motions()
    after = (
        game.rng.rx,
        game.loc,
        game.newloc,
        list(game.place),
        list(game.prop),
        list(game.first),
        game.holding,
    )
    assert before == after
    assert motions
    assert len(motions) == len(set(motions))
    assert int(Motion.HOUSE) in motions
    assert int(Motion.NOWHERE) not in motions


def test_possible_motions_respects_object_conditions() -> None:
    game = make_game()
    game.loc = int(Location.OUTSIDE)  # the grate is locked until unlocked
    locked = game.possible_motions()
    assert int(Motion.D) not in locked
    game.prop[int(Object.GRATE)] = 1  # the engine's "unlocked" property
    unlocked = game.possible_motions()
    assert int(Motion.D) in unlocked


def test_here_objects_and_inventory() -> None:
    game = make_game()
    game.loc = int(Location.HOUSE)
    here = game.here_objects()
    assert here == sorted(here)
    assert int(Object.KEYS) in here
    assert int(Object.LAMP) in here
    assert int(Object.FOOD) in here
    assert int(Object.BOTTLE) in here
    assert game.inventory() == []

    game._carry(int(Object.LAMP))
    assert int(Object.LAMP) not in game.here_objects()
    assert game.inventory() == [int(Object.LAMP)]
    game._carry(int(Object.KEYS))
    assert game.inventory() == [int(Object.KEYS), int(Object.LAMP)]


def test_here_objects_includes_multipart_parts() -> None:
    game = make_game()
    game.loc = int(Location.INSIDE)
    assert int(Object.GRATE_) in game.here_objects()


def test_inventory_matches_the_engines_inventory_filter() -> None:
    game = make_game()
    game.loc = int(Location.HOUSE)
    game._carry(int(Object.KEYS))
    game._carry(int(Object.GRATE_))  # a part of the grate group
    game._carry(int(Object.BEAR))  # a follower, not an inventory item
    inventory = game.inventory()
    assert int(Object.KEYS) in inventory
    assert int(Object.GRATE_) not in inventory
    assert int(Object.BEAR) not in inventory


def test_possible_motions_at_a_forced_location() -> None:
    game = make_game()
    game.loc = int(Location.CRACK)
    before = game.rng.rx
    motions = game.possible_motions()
    assert motions
    assert game.rng.rx == before


def test_is_dark_tracks_the_lamp() -> None:
    game = make_game()
    assert not game.is_dark()  # the road is lit
    game.loc = int(Location.DEBRIS)
    assert game.is_dark()
    game._carry(int(Object.LAMP))
    game.prop[int(Object.LAMP)] = 0
    assert game.is_dark()
    game.prop[int(Object.LAMP)] = 1
    assert not game.is_dark()


def test_welcome_can_be_deferred_for_front_ends() -> None:
    console = Answers(["n"])
    game = Game(console, seed=7, welcome=False)
    assert console.output == []
    assert game.limit == 0
    assert game.loc == int(Location.ROAD)
    assert game.here_objects() == []

    game.welcome()
    assert console.output, "the welcome question was not asked"
    assert any(entry.rstrip().endswith("**") for entry in console.output)
    assert game.limit == D.INITIAL_LIMIT

    console = Answers(["y"])
    game = Game(console, seed=7, welcome=False)
    game.welcome()
    assert game.limit == D.INSTRUCTIONS_LIMIT


def test_cli_has_a_gui_flag() -> None:
    from advent.cli import build_parser

    args = build_parser().parse_args(["--gui", "--seed", "3"])
    assert args.gui is True
    assert args.seed == 3
    assert build_parser().parse_args([]).gui is False


def test_cli_dispatches_to_the_gui(monkeypatch) -> None:
    pytest.importorskip("tkinter")
    import advent.cli as cli
    import advent.gui as gui

    seen: dict[str, int | None] = {}

    def fake_run(seed: int | None = None) -> int:
        seen["seed"] = seed
        return 0

    monkeypatch.setattr(gui, "run", fake_run)
    assert cli.main(["--gui", "--seed", "5"]) == 0
    assert seen["seed"] == 5


def test_views_are_safe_outside_real_locations() -> None:
    game = make_game()
    for loc in (int(Location.INHAND), int(Location.LIMBO)):
        game.loc = loc
        assert game.here_objects() == []
        assert game.possible_motions() == []
        assert game.is_dark() is False
    assert game.inventory() == []


def test_console_protocol_is_satisfied_by_the_scripted_console() -> None:
    console: Console = Answers(["n"])
    assert console.read_line("* ") == "n"
