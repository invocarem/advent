"""Shared helpers for the Adventure test suite."""

from __future__ import annotations

from collections.abc import Iterable

import pytest

from advent.game import EndOfInput, Game


class ScriptedConsole:
    """A :class:`advent.game.Console` that replays a fixed list of answers."""

    def __init__(self, answers: Iterable[str] = ()) -> None:
        self.answers = list(answers)
        self.output: list[str] = []

    def write(self, text: str) -> None:
        self.output.append(text)

    def read_line(self, prompt: str) -> str:
        self.output.append(prompt)
        if not self.answers:
            raise EndOfInput
        return self.answers.pop(0)

    @property
    def text(self) -> str:
        return "".join(self.output)


@pytest.fixture
def make_game():
    """Factory for a game driven by scripted answers: ``make_game([...])``."""

    def _make(answers: Iterable[str] = ("n",), seed: int = 7) -> Game:
        return Game(ScriptedConsole(answers), seed=seed)

    return _make


@pytest.fixture
def scripted():
    """Play a whole scripted game: ``game, output = scripted([...])``."""

    def _run(answers: Iterable[str], seed: int = 7) -> tuple[Game, str]:
        console = ScriptedConsole(answers)
        game = Game(console, seed=seed)
        game.play()
        return game, console.text

    return _run
