"""A thread-safe bridge between the engine and an interactive front end.

The engine is a blocking, line-oriented program: it writes text and then waits
for a line.  A windowed front end cannot block its own event loop waiting for
that, so :class:`EngineSession` runs one :class:`~advent.game.Game` in a worker
thread and exchanges messages through queues:

* the engine's output and prompts arrive as :class:`Event` objects in
  :attr:`EngineSession.events`;
* the front end calls :meth:`EngineSession.submit` with each answer.

This module has no GUI toolkit dependency, so the bridge is testable headlessly.
"""

from __future__ import annotations

import queue
import threading
from dataclasses import dataclass

from .game import Console, EndOfInput, Game
from .vocabulary import Object

WRITE = "write"
PROMPT = "prompt"
DONE = "done"


@dataclass(frozen=True)
class GameSnapshot:
    """A frozen view of the game, safe to read from another thread."""

    loc: int
    oldloc: int
    dark: bool
    here: tuple[int, ...]
    inventory: tuple[int, ...]
    motions: tuple[int, ...]
    turns: int
    bottle: int
    lamp: int


@dataclass(frozen=True)
class Event:
    """One message from the engine thread."""

    kind: str
    payload: str | None = None
    snapshot: GameSnapshot | None = None


class _SessionConsole:
    """The :class:`~advent.game.Console` the engine sees."""

    def __init__(self, session: "EngineSession") -> None:
        self.session = session

    def write(self, text: str) -> None:
        self.session.events.put(Event(WRITE, text))

    def read_line(self, prompt: str) -> str:
        self.session.events.put(Event(PROMPT, prompt, self.session.snapshot()))
        line = self.session._input.get()
        if line is None:
            raise EndOfInput
        return line


class EngineSession:
    """One game, running in its own thread."""

    def __init__(self, seed: int | None = None) -> None:
        self.seed = seed
        self.events: queue.Queue[Event] = queue.Queue()
        self._input: queue.Queue[str | None] = queue.Queue()
        self.game: Game | None = None
        self.finished = threading.Event()
        self._thread = threading.Thread(target=self._run, name="advent-engine", daemon=True)

    # -- lifecycle ---------------------------------------------------------

    def start(self) -> "EngineSession":
        self._thread.start()
        return self

    def _run(self) -> None:
        console: Console = _SessionConsole(self)
        try:
            # Build the game without its opening question, so that ``self.game``
            # is visible to the front end when that question is asked.
            game = Game(console, seed=self.seed, welcome=False)
            self.game = game
            game.welcome()
            game.play()
        except EndOfInput:
            pass
        finally:
            self.finished.set()
            self.events.put(Event(DONE, None, self.snapshot()))

    def snapshot(self) -> GameSnapshot | None:
        """Freeze the state a front end may draw, without mutating anything."""
        game = self.game
        if game is None:
            return None
        return GameSnapshot(
            loc=game.loc,
            oldloc=game.oldloc,
            dark=game.is_dark(),
            here=tuple(game.here_objects()),
            inventory=tuple(game.inventory()),
            motions=tuple(game.possible_motions()),
            turns=game.turns,
            bottle=game.prop[int(Object.BOTTLE)],
            lamp=game.prop[int(Object.LAMP)],
        )

    def stop(self) -> None:
        """Ask the engine to stop (it sees end of input and prints its score)."""
        self._input.put(None)

    def join(self, timeout: float | None = None) -> None:
        if self._thread.is_alive():
            self._thread.join(timeout)

    @property
    def running(self) -> bool:
        return self._thread.is_alive() and not self.finished.is_set()

    # -- traffic -----------------------------------------------------------

    def submit(self, line: str) -> None:
        """Answer the pending prompt with one line."""
        self._input.put(line)

    def drain(self) -> list[Event]:
        """Return every event queued so far, oldest first."""
        events: list[Event] = []
        while True:
            try:
                events.append(self.events.get_nowait())
            except queue.Empty:
                return events


__all__ = ["DONE", "PROMPT", "WRITE", "EngineSession", "Event", "GameSnapshot"]
