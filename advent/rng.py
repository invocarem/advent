"""Knuth's random number generator (``advent.w``, @* Random numbers).

The original is a linear congruential generator::

    rx = (1021*rx) & 0xfffff;      /* multiply by 1021, modulo 2**20 */
    return (range*rx) >> 20;

Each run is different: the seed comes from the clock, with the low bit
forced on so that the sequence can never degenerate to zero.  Pass an
explicit seed to make a run reproducible.
"""

from __future__ import annotations

import time

MASK = 0xFFFFF  # 2**20 - 1


class Rng:
    """The generator behind the ``ran`` and ``pct`` macros."""

    def __init__(self, seed: int | None = None) -> None:
        if seed is None:
            seed = int(time.time())
        self.rx = (seed & MASK) | 1

    def ran(self, range_: int) -> int:
        """A uniform integer in ``0 .. range_ - 1`` (``range_ == 0`` still advances)."""
        self.rx = (1021 * self.rx) & MASK
        return (range_ * self.rx) >> 20

    def pct(self, r: int) -> bool:
        """True with probability ``r`` percent (``pct`` in the original)."""
        return self.ran(100) < r
