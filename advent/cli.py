"""Terminal front end for the Adventure port.

The engine is UI-independent; this module supplies the :class:`Console` it
needs and the ``python -m advent`` command line.
"""

from __future__ import annotations

import argparse
import sys
from collections.abc import Sequence

from .game import EndOfInput, Game


class TerminalConsole:
    """A :class:`~advent.game.Console` backed by stdin/stdout."""

    def write(self, text: str) -> None:
        sys.stdout.write(text)
        sys.stdout.flush()

    def read_line(self, prompt: str) -> str:
        sys.stdout.write(prompt)
        sys.stdout.flush()
        line = sys.stdin.readline()
        if not line:
            raise EndOfInput
        return line.rstrip("\r\n")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="python -m advent",
        description="Adventure (Colossal Cave), a faithful port of Knuth's advent.w.",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=None,
        metavar="N",
        help="seed the random number generator (default: from the clock)",
    )
    parser.add_argument(
        "--gui",
        action="store_true",
        help="play in a graphical window instead of the terminal (needs tkinter)",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.gui:
        try:
            from .gui import run as run_gui
        except ImportError as exc:
            print("The graphical front end needs tkinter: %s" % exc, file=sys.stderr)
            return 2
        return run_gui(seed=args.seed)
    game = Game(TerminalConsole(), seed=args.seed)
    try:
        game.play()
    except KeyboardInterrupt:
        # Ctrl-C: the engine stops wherever it was; just end the line nicely.
        print()
        return 130
    return 0
