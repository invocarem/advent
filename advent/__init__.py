"""Adventure -- Colossal Cave, ported from Don Knuth's ``advent.w``.

The game is a study port of Knuth's CWEB program.  Play it with
``python -m advent``; the engine itself is UI-independent and is driven
through a :class:`~advent.game.Console`.
"""

from __future__ import annotations

from .game import Console, EndOfInput, Game

__all__ = ["Console", "EndOfInput", "Game"]
