"""The Adventure engine: a faithful port of ``advent.w``'s simulation.

The engine is UI-independent.  It never touches ``stdin``/``stdout``; it is
constructed with a :class:`Console` and emits exactly the text the original
``printf`` calls produce (including the one message that has no trailing
newline).

Structure follows Knuth's program section by section:

* :meth:`Game.play` -- the two nested loops (major cycles = moves, minor
  cycles = actions), @<Simulate an adventure@>.
* :meth:`Game._input_phase` -- the parser, @<Get user input@>, written as an
  explicit state machine instead of ``goto``.
* :meth:`Game._determine_next_location` -- the travel table,
  @<Determine the next location@>.
* Actions, actors, clocks, death and scoring live in their own methods named
  after the corresponding WEB sections.

``goto`` jumps that cross the major-cycle boundary are modelled with the
private exceptions below; they never escape :meth:`Game.play`.
"""

from __future__ import annotations

from typing import Protocol

from . import data as D
from .rng import Rng
from .vocabulary import (
    DEFAULT_MSG,
    LIGHTED,
    LIQUID,
    MAX_LOC,
    MAX_OBJ,
    MAX_PIRATE_LOC,
    MAX_SPEC,
    MESSAGES,
    MIN_FORCED_LOC,
    MIN_IN_CAVE,
    MIN_LOWER_LOC,
    MIN_TREASURE,
    CAVE_HINT,
    OK,
    Action,
    Location,
    Motion,
    Object,
    WordType,
    lookup,
)
from .vocabulary import OIL as OIL_FLAG

PITCH_DARK = "It is now pitch dark.  If you proceed you will most likely fall into a pit."

DWARVES_UPSET = (
    "The resulting ruckus has awakened the dwarves.  There are now several\n"
    "threatening little dwarves in the room with you!  Most of them throw\n"
    "knives at you!  All of them get you!"
)

ATTACK_MSG = ("it misses", "it gets you", "none of them hit you", "one of them gets you")

INCANTATION = ("fee", "fie", "foe", "foo", "fum")

# --------------------------------------------------------------------------
# Control flow: the original's goto labels
# --------------------------------------------------------------------------


class Console(Protocol):
    """Everything the engine needs from a front end."""

    def write(self, text: str) -> None:
        """Emit ``text`` exactly; add no newline of your own."""

    def read_line(self, prompt: str) -> str:
        """Write ``prompt``, then return one line of input (without the newline)."""


class EndOfInput(Exception):
    """The console reached end of file (the original would loop forever)."""


class _Quit(Exception):
    """``goto quit``."""


class _Death(Exception):
    """``goto death``."""


class _DwarvesUpset(Exception):
    """``goto dwarves_upset``."""


class _Commence(Exception):
    """``goto commence``: re-describe the current room."""


class _Motion(Exception):
    """``goto try_move`` with a motion word."""

    def __init__(self, mot: int) -> None:
        super().__init__(mot)
        self.mot = mot


# Parser states (the labels inside @<Get user input@>).
_CYCLE = "cycle"
_PRE_PARSE = "pre_parse"
_PARSE = "parse"
_BRANCH = "branch"
_SHIFT = "shift"
_INTRANSITIVE = "intransitive"
_TRANSITIVE = "transitive"
_SPEAKIT = "speakit"
_REPORT_DEFAULT = "report_default"
_GET_OBJECT = "get_object"
_CANT_SEE_IT = "cant_see_it"


def _streq(a: str, b: str) -> bool:
    """``streq``: the strings agree in their first five letters."""
    return a[:5] == b[:5]


class Game:
    """One game of Adventure."""

    def __init__(self, console: Console, seed: int | None = None) -> None:
        self.console = console
        self.rng = Rng(seed)

        # --- objects (@<Data structures for objects@>) --------------------
        self.place = [int(Location.LIMBO)] * (MAX_OBJ + 1)
        self.prop = [0] * (MAX_OBJ + 1)
        self.link = [0] * (MAX_OBJ + 1)
        self.base = [0] * (MAX_OBJ + 2)  # base[max_obj+1] == NOTHING
        self.name: list[str | None] = [None] * (MAX_OBJ + 1)
        self.offset = [0] * (MAX_OBJ + 1)
        self.first = [0] * (MAX_LOC + 1)
        self.holding = 0

        # --- locations and turn counters ---------------------------------
        self.visits = [0] * (MAX_LOC + 1)
        self.turns = 0
        self.west_count = 0
        self.look_count = 0
        self.interval = D.INTERVAL
        self.was_dark = False

        # --- parser registers --------------------------------------------
        self.mot = int(Motion.N)
        self.verb = Action.ABSTAIN
        self.oldverb = Action.ABSTAIN
        self.obj = int(Object.NOTHING)
        self.oldobj = int(Object.NOTHING)
        self.word1 = ""
        self.word2 = ""
        self.command: tuple[WordType, int] | None = None
        self.k = 0
        self.foobar = 0

        # --- treasures, lamp, clocks -------------------------------------
        self.tally = D.TALLY
        self.lost_treasures = 0
        self.limit = 0  # set below, after the welcome message
        self.warned = False
        self.clock1 = D.CLOCK1
        self.clock2 = D.CLOCK2
        self.panic = D.INITIAL_PANIC
        self.closed = D.INITIAL_CLOSED

        # --- dwarves and the pirate --------------------------------------
        self.dflag = 0
        self.dkill = 0
        self.dloc = [int(x) for x in D.INITIAL_DLOC]
        self.odloc = [int(Location.LIMBO)] * (D.ND + 1)
        self.dseen = [False] * (D.ND + 1)
        self.dtotal = 0
        self.attack = 0
        self.stick = 0
        self.knife_loc = int(D.INITIAL_KNIFE_LOC)

        # --- death, hints, score -----------------------------------------
        self.death_count = 0
        self.gave_up = False
        self.bonus = 0
        self.hinted = [False] * D.N_HINTS
        self.hint_count = [0] * D.N_HINTS

        # --- positions ----------------------------------------------------
        self.oldoldloc = int(Location.ROAD)
        self.oldloc = int(Location.ROAD)
        self.loc = int(Location.ROAD)
        self.newloc = int(Location.ROAD)

        self._build_objects()
        self._offer(0)  # welcome message, and maybe instructions
        self.limit = D.INSTRUCTIONS_LIMIT if self.hinted[0] else D.INITIAL_LIMIT

    # ------------------------------------------------------------------
    # Output helpers
    # ------------------------------------------------------------------

    def _write(self, text: str) -> None:
        self.console.write(text)

    def _line(self, text: str) -> None:
        self.console.write(text + "\n")

    def _report(self, text: str | None) -> str:
        """``report(m)``: print and end the minor cycle."""
        if text is not None:
            self._line(text)
        return _CYCLE

    def _report_default_of(self, verb: Action) -> str:
        """``default_to(v)``: print the default message for ``v``."""
        msg = DEFAULT_MSG.get(verb)
        return self._report(msg)

    # ------------------------------------------------------------------
    # Low-level input (@* Low-level input@>)
    # ------------------------------------------------------------------

    def _listen(self) -> tuple[str, str]:
        """``listen``: read one or two lowercased words."""
        while True:
            line = self.console.read_line("* ")[: D.BUF_SIZE - 1]
            words = line.split()
            if not words:
                self._line(" Tell me to do something.")
                continue
            if len(words) == 1:
                return words[0].lower(), ""
            if len(words) == 2:
                return words[0].lower(), words[1].lower()
            self._line(" Please stick to 1- and 2-word commands.")

    def _yes(self, question: str, yes: str | None, no: str | None) -> bool:
        """``yes``: ask a yes/no question until the answer starts with y or n."""
        while True:
            answer = self.console.read_line(question + "\n** ")
            first = answer[:1].lower()
            if first == "y":
                if yes is not None:
                    self._line(yes)
                return True
            if first == "n":
                if no is not None:
                    self._line(no)
                return False
            self._line(" Please answer Yes or No.")

    # ------------------------------------------------------------------
    # Object bookkeeping (@<Subroutines@>)
    # ------------------------------------------------------------------

    def _build_objects(self) -> None:
        """@<Build the object tables@>: highest number first, so lists ascend."""
        for t, info in D.OBJECTS.items():
            self.name[t] = info.name
            self.base[t] = info.base
            self.offset[t] = info.offset
            self.prop[t] = -1 if t >= int(MIN_TREASURE) else 0
            self._drop(t, info.start)

    def _toting(self, t: int) -> bool:
        return self.place[t] < 0

    def _here(self, t: int) -> bool:
        return self._toting(t) or self.place[t] == self.loc

    def _is_at_loc(self, t: int) -> bool:
        """``is_at_loc``: is any part of the (possibly multipart) object here?"""
        if self.base[t] == 0:
            return self.place[t] == self.loc
        tt = t
        while self.base[tt] == t:
            if self.place[tt] == self.loc:
                return True
            tt += 1
        return False

    def _drop(self, t: int, loc: int) -> None:
        """``drop(t,l)``: put object ``t`` at ``loc``."""
        if self._toting(t):
            self.holding -= 1
        self.place[t] = loc
        if loc < 0:
            self.holding += 1
        elif loc > 0:
            self.link[t] = self.first[loc]
            self.first[loc] = t

    def _carry(self, t: int) -> None:
        """``carry(t)``: pick object ``t`` up."""
        loc = self.place[t]
        if loc >= int(Location.LIMBO):
            self.place[t] = int(Location.INHAND)
            self.holding += 1
            if loc > int(Location.LIMBO):
                r, s = 0, self.first[loc]
                while s != t:
                    r, s = s, self.link[s]
                if r == 0:
                    self.first[loc] = self.link[s]
                else:
                    self.link[r] = self.link[s]

    def _move(self, t: int, loc: int) -> None:
        """``move(t,l)``: carry then drop."""
        self._carry(t)
        self._drop(t, loc)

    def _destroy(self, t: int) -> None:
        """``destroy(t)``: move to limbo."""
        self._move(t, int(Location.LIMBO))

    # ------------------------------------------------------------------
    # Derived tests
    # ------------------------------------------------------------------

    def _flags(self, loc: int) -> int:
        return D.LOCATIONS[loc].flags

    def _dark(self) -> bool:
        return (self._flags(self.loc) & LIGHTED) == 0 and (
            self.prop[int(Object.LAMP)] == 0 or not self._here(int(Object.LAMP))
        )

    def _water_here(self) -> bool:
        return (self._flags(self.loc) & (LIQUID | OIL_FLAG)) == LIQUID

    def _oil_here(self) -> bool:
        return (self._flags(self.loc) & (LIQUID | OIL_FLAG)) == LIQUID + OIL_FLAG

    def _no_liquid_here(self) -> bool:
        return (self._flags(self.loc) & LIQUID) == 0

    def _bottle_empty(self) -> bool:
        return self.prop[int(Object.BOTTLE)] == 1 or self.prop[int(Object.BOTTLE)] < 0

    def _object_in_bottle(self) -> bool:
        obj = self.obj
        return (obj == Object.WATER and self.prop[int(Object.BOTTLE)] == 0) or (
            obj == Object.OIL and self.prop[int(Object.BOTTLE)] == 2
        )

    def _forced_move(self, loc: int) -> bool:
        return loc >= int(MIN_FORCED_LOC)

    def _closing(self) -> bool:
        return self.clock1 < 0

    def _dwarf(self) -> bool:
        """``dwarf()``: is a live dwarf in the room?"""
        if self.dflag < 2:
            return False
        return any(self.dloc[j] == self.loc for j in range(1, D.ND + 1))

    def _is_treasure(self, t: int) -> bool:
        return t >= int(MIN_TREASURE)

    def _too_easy(self, i: int) -> bool:
        return i == Object.PYRAMID and self.loc in (Location.PROOM, Location.DROOM)

    def _note(self, index: int) -> str | None:
        if 0 <= index < len(D.NOTES):
            return D.NOTES[index]
        return None

    # ------------------------------------------------------------------
    # Hints (@<Subroutines@>, @<Check if a hint applies@>)
    # ------------------------------------------------------------------

    def _offer(self, j: int) -> None:
        if j > 1:
            if not self._yes(D.HINT_PROMPT[j], " I am prepared to give you a hint,", OK):
                return
            self._write(" but it will cost you %d points.  " % D.HINT_COST[j])
            self.hinted[j] = self._yes("Do you want the hint?", D.HINT[j], OK)
        else:
            self.hinted[j] = self._yes(D.HINT_PROMPT[j], D.HINT[j], OK)
        if self.hinted[j] and self.limit > 30:
            self.limit += 30 * D.HINT_COST[j]

    def _hint_applies(self, j: int) -> bool | None:
        """The per-hint conditions; ``None`` means ``continue`` (keep counting)."""
        if j == 2:
            return self.prop[int(Object.GRATE)] == 0 and not self._here(int(Object.KEYS))
        if j == 3:
            if (
                self._here(int(Object.BIRD))
                and self.oldobj == Object.BIRD
                and self._toting(int(Object.ROD))
            ):
                return True
            return None
        if j == 4:
            return self._here(int(Object.SNAKE)) and not self._here(int(Object.BIRD))
        if j == 5:
            return (
                self.first[self.loc] == 0
                and self.first[self.oldloc] == 0
                and self.first[self.oldoldloc] == 0
                and self.holding > 1
            )
        if j == 6:
            return (
                self.prop[int(Object.EMERALD)] != -1
                and self.prop[int(Object.PYRAMID)] == -1
            )
        return True  # j == 7

    def _offer_hints(self) -> None:
        k = int(CAVE_HINT)  # then doubling for hints 3..7
        for j in range(2, 8):
            if not self.hinted[j]:
                if (self._flags(self.loc) & k) == 0:
                    self.hint_count[j] = 0
                else:
                    self.hint_count[j] += 1
                    if self.hint_count[j] >= D.HINT_THRESH[j]:
                        verdict = self._hint_applies(j)
                        if verdict is True:
                            self._offer(j)
                            self.hint_count[j] = 0
                        elif verdict is False:
                            self.hint_count[j] = 0
            k += k

    # ------------------------------------------------------------------
    # Scoring (@* Scoring@>)
    # ------------------------------------------------------------------

    def _score(self) -> int:
        s = 2
        if self.dflag:
            s += 25
        for k in range(int(MIN_TREASURE), MAX_OBJ + 1):
            if self.prop[k] >= 0:
                s += 2
                if self.place[k] == Location.HOUSE and self.prop[k] == 0:
                    s += 10 if k < Object.CHEST else (12 if k == Object.CHEST else 14)
        s += 10 * (D.MAX_DEATHS - self.death_count)
        if not self.gave_up:
            s += 4
        if self.place[int(Object.MAG)] == Location.WITT:
            s += 1
        if self._closing():
            s += 25
        s += self.bonus
        for j in range(D.N_HINTS):
            if self.hinted[j]:
                s -= D.HINT_COST[j]
        return s

    def _print_score(self) -> None:
        k = self._score()
        self._line(
            "You scored %d point%s out of a possible %d, using %d turn%s."
            % (k, "" if k == 1 else "s", D.MAX_SCORE, self.turns, "" if self.turns == 1 else "s")
        )
        j = 0
        while j < len(D.CLASS_SCORE) - 1 and D.CLASS_SCORE[j] < k:
            j += 1
        self._write(D.CLASS_MESSAGE[j] + "\nTo achieve the next higher rating")
        if j < D.HIGHEST_CLASS:
            self._line(
                ", you need %d more point%s."
                % (D.CLASS_SCORE[j] + 1 - k, "" if D.CLASS_SCORE[j] == k else "s")
            )
        else:
            self._line(" would be a neat trick!\nCongratulations!!")

    # ------------------------------------------------------------------
    # The main loop (@<Simulate an adventure@>)
    # ------------------------------------------------------------------

    def play(self) -> None:
        """Run the game until the player quits, dies for the last time, or hits EOF."""
        try:
            self._run()
        except _DwarvesUpset:
            self._line(DWARVES_UPSET)
        except (_Quit, EndOfInput):
            pass
        self._print_score()

    def _run(self) -> None:
        while True:  # major cycles
            self._check_interference()
            self.loc = self.newloc
            try:
                self._move_actors()
            except _Death:
                self._death()
            while True:  # "commence": report, then minor cycles
                try:
                    forced = self._report_state()
                    if forced:
                        mot = self.mot
                    else:
                        try:
                            mot = self._input_phase()
                        except _Motion as jump:
                            mot = jump.mot
                    outcome = self._handle_special_motions(mot)
                    if outcome is None:  # stay put / looked / asked about the cave
                        break
                    skip_oldloc, mot = outcome
                    if not skip_oldloc:
                        self.oldoldloc = self.oldloc
                        self.oldloc = self.loc
                    self._determine_next_location(mot)
                    break
                except _Commence:
                    continue
                except _Death:
                    self._death()
                    continue

    def _check_interference(self) -> None:
        """@<Check for interference with the proposed move to newloc@>."""
        if self._closing() and self.newloc < int(MIN_IN_CAVE) and self.newloc != int(Location.LIMBO):
            self._panic()
            self.newloc = self.loc
        elif self.newloc != self.loc and self.loc <= MAX_PIRATE_LOC:
            for j in range(1, D.ND + 1):
                if self.odloc[j] == self.newloc and self.dseen[j]:
                    self._line("A little dwarf with a big knife blocks your way.")
                    self.newloc = self.loc
                    break

    def _report_state(self) -> bool:
        """@<Report the current state@>; True means a forced move follows."""
        if self.loc == int(Location.LIMBO):
            raise _Death
        if self._dark() and not self._forced_move(self.loc):
            if self.was_dark and self.rng.pct(35):
                self._line("You fell into a pit and broke every bone in your body!")
                self.oldoldloc = self.loc
                raise _Death
            text: str | None = PITCH_DARK
        elif (
            D.LOCATIONS[self.loc].short is None
            or self.visits[self.loc] % self.interval == 0
        ):
            text = D.LOCATIONS[self.loc].long
        else:
            text = D.LOCATIONS[self.loc].short
        if self._toting(int(Object.BEAR)):
            self._line("You are being followed by a very large, tame bear.")
        if text:
            self._line("\n" + text)
        if self._forced_move(self.loc):
            return True
        if self.loc == Location.Y2 and self.rng.pct(25) and not self._closing():
            self._line('A hollow voice says "PLUGH".')
        if not self._dark():
            self._describe_objects()
        return False

    def _describe_objects(self) -> None:
        """@<Describe the objects at this location@>."""
        self.visits[self.loc] += 1
        t = self.first[self.loc]
        while t:
            tt = self.base[t] if self.base[t] else t
            if self.prop[tt] < 0:
                if not self.closed:
                    self.prop[tt] = 1 if tt in (Object.RUG, Object.CHAIN) else 0
                    self.tally -= 1
                    if self.tally == self.lost_treasures and self.tally > 0 and self.limit > 35:
                        self.limit = 35
                t = self.link[t]
                continue
            if not (tt == Object.TREADS and self._toting(int(Object.GOLD))):
                extra = 1 if (tt == Object.TREADS and self.loc == Location.EMIST) else 0
                note = self._note(self.prop[tt] + self.offset[tt] + extra)
                if note:
                    self._line(note)
            t = self.link[t]

    # ------------------------------------------------------------------
    # Parser (@<Get user input@>)
    # ------------------------------------------------------------------

    def _input_phase(self) -> int:
        """Run minor cycles until a motion word ends the action phase."""
        state = _CYCLE
        while True:
            if state == _CYCLE:
                # Entering a minor cycle: forget the previous command, but
                # remember its object (@<Get user input@>).
                self.verb = Action.ABSTAIN
                self.oldverb = Action.ABSTAIN
                self.oldobj = self.obj
                self.obj = int(Object.NOTHING)
                self._offer_hints()
                self.was_dark = self._dark()
                self.k = self.rng.ran(0)  # kick the generator
                if self.closed:
                    if self.prop[int(Object.OYSTER)] < 0 and self._toting(int(Object.OYSTER)):
                        self._line(D.NOTES[self.offset[int(Object.OYSTER)] + 1])
                    for j in range(1, MAX_OBJ + 1):
                        if self._toting(j) and self.prop[j] < 0:
                            self.prop[j] = -1 - self.prop[j]
                self.word1, self.word2 = self._listen()
                state = _PRE_PARSE

            elif state == _PRE_PARSE:
                self.turns += 1
                if self.verb == Action.SAY:
                    if self.word2:
                        self.verb = Action.ABSTAIN
                    else:
                        state = _TRANSITIVE
                        continue
                self.foobar = -self.foobar if self.foobar > 0 else 0
                self._check_clocks_and_lamp()
                state = self._pre_parse_specials()

            elif state == _PARSE:
                if _streq(self.word1, "west"):
                    self.west_count += 1
                    if self.west_count == 10:
                        self._line(" If you prefer, simply type W rather than WEST.")
                self.command = lookup(self.word1)
                if self.command is None:
                    self._line('Sorry, I don\'t know the word "%s".' % self.word1)
                    state = _CYCLE
                    continue
                state = _BRANCH

            elif state == _SHIFT:
                self.word1, self.word2 = self.word2, ""
                state = _PARSE

            elif state == _BRANCH:
                wtype, meaning = self.command  # type: ignore[misc]
                if wtype is WordType.MOTION:
                    raise _Motion(int(meaning))
                if wtype is WordType.OBJECT:
                    self.obj = int(meaning)
                    nxt = self._make_sure_obj_meaningful()
                    if nxt is not None:
                        state = nxt
                        continue
                    if self.word2:
                        state = _SHIFT
                        continue
                    if self.verb:
                        state = _TRANSITIVE
                        continue
                    self._line("What do you want to do with the %s?" % self.word1)
                    state = _CYCLE
                elif wtype is WordType.ACTION:
                    self.verb = Action(meaning)
                    if self.verb == Action.SAY:
                        self.obj = 1 if self.word2 else int(Object.NOTHING)
                    elif self.word2:
                        state = _SHIFT
                        continue
                    state = _TRANSITIVE if self.obj else _INTRANSITIVE
                else:  # MESSAGE
                    state = _SPEAKIT

            elif state == _INTRANSITIVE:
                state = self._do_intransitive()

            elif state == _TRANSITIVE:
                state = self._do_transitive()

            elif state == _SPEAKIT:
                self._line(MESSAGES[self.command[1]])  # type: ignore[index]
                state = _CYCLE

            elif state == _REPORT_DEFAULT:
                state = self._report_default_of(self.verb)

            elif state == _GET_OBJECT:
                self.word1 = self.word1[:1].upper() + self.word1[1:]
                self._line(self.word1 + " what?")
                state = _CYCLE

            elif state == _CANT_SEE_IT:
                if self.verb in (Action.FIND, Action.INVENTORY) and not self.word2:
                    state = _TRANSITIVE
                    continue
                self._line("I see no %s here." % self.word1)
                state = _CYCLE

    def _pre_parse_specials(self) -> str:
        """@<Handle special cases of input@> and @<Handle additional special cases@>."""
        if _streq(self.word1, "enter"):
            if _streq(self.word2, "water") or _streq(self.word2, "strea"):
                if self._water_here():
                    return self._report("Your feet are now wet.")
                return self._report_default_of(Action.GO)
            if self.word2:
                return _SHIFT
        if (
            (_streq(self.word1, "water") or _streq(self.word1, "oil"))
            and (_streq(self.word2, "plant") or _streq(self.word2, "door"))
        ):
            target = lookup(self.word2)
            if target is not None and self.loc == self.place[int(target[1])]:
                self.word2 = "pour"
        return _PARSE

    def _make_sure_obj_meaningful(self) -> str | None:
        """@<Make sure obj is meaningful at the current location@>."""
        if self._toting(self.obj) or self._is_at_loc(self.obj):
            return None
        obj = self.obj
        if obj == Object.GRATE:
            if self.loc < int(MIN_IN_CAVE):
                if self.loc in (Location.ROAD, Location.VALLEY, Location.SLIT):
                    raise _Motion(int(Motion.DEPRESSION))
                if self.loc in (
                    Location.COBBLES,
                    Location.DEBRIS,
                    Location.AWK,
                    Location.BIRD,
                    Location.SPIT,
                ):
                    raise _Motion(int(Motion.ENTRANCE))
            return _CANT_SEE_IT
        if obj == Object.DWARF:
            return None if (self.dflag >= 2 and self._dwarf()) else _CANT_SEE_IT
        if obj == Object.PLANT:
            if self._is_at_loc(int(Object.PLANT2)) and self.prop[int(Object.PLANT2)]:
                self.obj = int(Object.PLANT2)
                return None
            return _CANT_SEE_IT
        if obj == Object.KNIFE:
            if self.loc != self.knife_loc:
                return _CANT_SEE_IT
            self.knife_loc = -1
            return self._report("The dwarves' knives vanish as they strike the walls of the cave.")
        if obj == Object.ROD:
            if not self._here(int(Object.ROD2)):
                return _CANT_SEE_IT
            self.obj = int(Object.ROD2)
            return None
        if obj in (Object.WATER, Object.OIL):
            if self._here(int(Object.BOTTLE)) and self._object_in_bottle():
                return None
            if (obj == Object.WATER and self._water_here()) or (
                obj == Object.OIL and self._oil_here()
            ):
                return None
        return _CANT_SEE_IT

    # ------------------------------------------------------------------
    # Intransitive verbs
    # ------------------------------------------------------------------

    def _do_intransitive(self) -> str:
        self.k = 0
        verb = self.verb
        if verb in (Action.GO, Action.RELAX):
            return _REPORT_DEFAULT
        if verb in (
            Action.ON,
            Action.OFF,
            Action.POUR,
            Action.FILL,
            Action.DRINK,
            Action.BLAST,
            Action.KILL,
        ):
            return _TRANSITIVE
        if verb == Action.TAKE:
            first = self.first[self.loc]
            if first == 0 or self.link[first] or self._dwarf():
                return _GET_OBJECT
            self.obj = first
            return _TRANSITIVE
        if verb == Action.EAT:
            if not self._here(int(Object.FOOD)):
                return _GET_OBJECT
            self.obj = int(Object.FOOD)
            return _TRANSITIVE
        if verb in (Action.OPEN, Action.CLOSE):
            obj = 0
            if self.place[int(Object.GRATE)] == self.loc or self.place[int(Object.GRATE_)] == self.loc:
                obj = int(Object.GRATE)
            elif self.place[int(Object.DOOR)] == self.loc:
                obj = int(Object.DOOR)
            elif self._here(int(Object.CLAM)):
                obj = int(Object.CLAM)
            elif self._here(int(Object.OYSTER)):
                obj = int(Object.OYSTER)
            if self._here(int(Object.CHAIN)):
                if obj:
                    return _GET_OBJECT
                obj = int(Object.CHAIN)
            if obj:
                self.obj = obj
                return _TRANSITIVE
            return self._report("There is nothing here with a lock!")
        if verb == Action.READ:
            if self._dark():
                return _GET_OBJECT
            obj = 0
            if self._here(int(Object.MAG)):
                obj = int(Object.MAG)
            if self._here(int(Object.TABLET)):
                if obj:
                    return _GET_OBJECT
                obj = int(Object.TABLET)
            if self._here(int(Object.MESSAGE)):
                if obj:
                    return _GET_OBJECT
                obj = int(Object.MESSAGE)
            if self.closed and self._toting(int(Object.OYSTER)):
                obj = int(Object.OYSTER)
            if obj:
                self.obj = obj
                return _TRANSITIVE
            return _GET_OBJECT
        if verb == Action.INVENTORY:
            for t in range(1, MAX_OBJ + 1):
                if (
                    self._toting(t)
                    and (self.base[t] == 0 or self.base[t] == t)
                    and t != Object.BEAR
                ):
                    if self.k == 0:
                        self.k = 1
                        self._line("You are currently holding the following:")
                    self._line(" %s" % (self.name[t] or ""))
            if self._toting(int(Object.BEAR)):
                return self._report("You are being followed by a very large, tame bear.")
            if self.k == 0:
                return self._report("You're not carrying anything.")
            return _CYCLE
        if verb == Action.BRIEF:
            self.interval = 10000
            self.look_count = 3
            return self._report(
                "Okay, from now on I'll only describe a place in full the first time\n"
                'you come to it.  To get the full description, say "LOOK".'
            )
        if verb == Action.SCORE:
            self._line(
                "If you were to quit now, you would score %d\nout of a possible %d."
                % (self._score() - 4, D.MAX_SCORE)
            )
            if not self._yes("Do you indeed wish to quit now?", OK, OK):
                return _CYCLE
            self.gave_up = True
            raise _Quit
        if verb == Action.QUIT:
            if not self._yes("Do you really want to quit now?", OK, OK):
                return _CYCLE
            self.gave_up = True
            raise _Quit
        if verb == Action.FEEFIE:
            while not _streq(self.word1, INCANTATION[self.k]):
                self.k += 1
            if self.foobar == -self.k:
                return self._proceed_foobarically()
            if self.foobar == 0:
                return self._report(DEFAULT_MSG[Action.WAVE])
            return self._report("What's the matter, can't you read?  Now you'd best start over.")
        return _GET_OBJECT

    def _proceed_foobarically(self) -> str:
        self.foobar = self.k + 1
        if self.foobar != 4:
            return self._report(DEFAULT_MSG[Action.RELAX])
        self.foobar = 0
        if self.place[int(Object.EGGS)] == Location.GIANT or (
            self._toting(int(Object.EGGS)) and self.loc == Location.GIANT
        ):
            return self._report(DEFAULT_MSG[Action.WAVE])
        if (
            self.place[int(Object.EGGS)] == Location.LIMBO
            and self.place[int(Object.TROLL)] == Location.LIMBO
            and self.prop[int(Object.TROLL)] == 0
        ):
            self.prop[int(Object.TROLL)] = 1
        k = 0 if self.loc == Location.GIANT else (1 if self._here(int(Object.EGGS)) else 2)
        self._move(int(Object.EGGS), int(Location.GIANT))
        return self._report(self._note(self.offset[int(Object.EGGS)] + k))

    # ------------------------------------------------------------------
    # Transitive verbs
    # ------------------------------------------------------------------

    def _do_transitive(self) -> str:
        self.k = 0
        verb = self.verb
        obj = self.obj

        if verb == Action.SAY:
            if self.word2:
                self.word1 = self.word2
            found = lookup(self.word1)
            if found is not None:
                wtype, meaning = found
                if (meaning == Action.FEEFIE and wtype is WordType.ACTION) or meaning in (
                    Motion.XYZZY,
                    Motion.PLUGH,
                    Motion.PLOVER,
                ):
                    self.word2 = ""
                    self.obj = int(Object.NOTHING)
                    self.command = found
                    return _BRANCH
            self._line('Okay, "%s".' % self.word1)
            return _CYCLE

        if verb == Action.EAT:
            if obj == Object.FOOD:
                self._destroy(int(Object.FOOD))
                return self._report("Thank you, it was delicious!")
            if obj in (
                Object.BIRD,
                Object.SNAKE,
                Object.CLAM,
                Object.OYSTER,
                Object.DWARF,
                Object.DRAGON,
                Object.TROLL,
                Object.BEAR,
            ):
                return self._report("I think I just lost my appetite.")
            return _REPORT_DEFAULT

        if verb == Action.WAVE:
            if (
                obj != Object.ROD
                or self.loc not in (Location.EFISS, Location.WFISS)
                or not self._toting(obj)
                or self._closing()
            ):
                if self._toting(obj) or (obj == Object.ROD and self._toting(int(Object.ROD2))):
                    return _REPORT_DEFAULT
                return self._report_default_of(Action.DROP)
            self.prop[int(Object.CRYSTAL)] = 1 - self.prop[int(Object.CRYSTAL)]
            return self._report(
                self._note(self.offset[int(Object.CRYSTAL)] + 2 - self.prop[int(Object.CRYSTAL)])
            )

        if verb == Action.BLAST:
            if self.closed and self.prop[int(Object.ROD2)] >= 0:
                if self._here(int(Object.ROD2)):
                    self.bonus = 25
                elif self.loc == Location.NEEND:
                    self.bonus = 30
                else:
                    self.bonus = 45
                self._line(MESSAGES[self.bonus // 5])
                raise _Quit
            return _REPORT_DEFAULT

        if verb == Action.RUB:
            if obj == Object.LAMP:
                return _REPORT_DEFAULT
            return self._report("Peculiar.  Nothing unexpected happens.")

        if verb in (Action.FIND, Action.INVENTORY):
            if self._toting(obj):
                return self._report_default_of(Action.TAKE)
            if self.closed:
                return self._report("I daresay whatever you want is around here somewhere.")
            if (
                self._is_at_loc(obj)
                or (self._object_in_bottle() and self.place[int(Object.BOTTLE)] == self.loc)
                or (obj == Object.WATER and self._water_here())
                or (obj == Object.OIL and self._oil_here())
                or (obj == Object.DWARF and self._dwarf())
            ):
                return self._report("I believe what you want is right here with you.")
            return _REPORT_DEFAULT

        if verb == Action.BREAK:
            if obj == Object.VASE and self.prop[int(Object.VASE)] == 0:
                if self._toting(int(Object.VASE)):
                    self._drop(int(Object.VASE), self.loc)
                self._line("You have taken the vase and hurled it delicately to the ground.")
                return self._smash_vase()
            if obj != Object.MIRROR:
                return _REPORT_DEFAULT
            if self.closed:
                self._write(
                    "You strike the mirror a resounding blow, whereupon it shatters into a\n"
                    "myriad tiny fragments."
                )
                raise _DwarvesUpset
            return self._report("It is too far up for you to reach.")

        if verb == Action.WAKE:
            if self.closed and obj == Object.DWARF:
                self._line(
                    "You prod the nearest dwarf, who wakes up grumpily, takes one look at\n"
                    "you, curses, and grabs for his axe."
                )
                raise _DwarvesUpset
            return _REPORT_DEFAULT

        if verb == Action.ON:
            if not self._here(int(Object.LAMP)):
                return _REPORT_DEFAULT
            if self.limit < 0:
                return self._report("Your lamp has run out of power.")
            self.prop[int(Object.LAMP)] = 1
            self._line("Your lamp is now on.")
            if self.was_dark:
                raise _Commence
            return _CYCLE

        if verb == Action.OFF:
            if not self._here(int(Object.LAMP)):
                return _REPORT_DEFAULT
            self.prop[int(Object.LAMP)] = 0
            self._line("Your lamp is now off.")
            if self._dark():
                self._line(PITCH_DARK)
            return _CYCLE

        if verb == Action.DRINK:
            if obj == Object.NOTHING:
                if not self._water_here() and not (
                    self._here(int(Object.BOTTLE)) and self.prop[int(Object.BOTTLE)] == 0
                ):
                    return _GET_OBJECT
            elif obj != Object.WATER:
                return self._report_default_of(Action.EAT)
            if not (self._here(int(Object.BOTTLE)) and self.prop[int(Object.BOTTLE)] == 0):
                return _REPORT_DEFAULT
            self.prop[int(Object.BOTTLE)] = 1
            self.place[int(Object.WATER)] = int(Location.LIMBO)
            return self._report("The bottle of water is now empty.")

        if verb == Action.POUR:
            if obj in (Object.NOTHING, Object.BOTTLE):
                if self.prop[int(Object.BOTTLE)] == 0:
                    obj = int(Object.WATER)
                elif self.prop[int(Object.BOTTLE)] == 2:
                    obj = int(Object.OIL)
                else:
                    obj = int(Object.NOTHING)
                if obj == Object.NOTHING:
                    return _GET_OBJECT
                self.obj = obj
            if not self._toting(obj):
                return _REPORT_DEFAULT
            if obj not in (Object.WATER, Object.OIL):
                return self._report("You can't pour that.")
            self.prop[int(Object.BOTTLE)] = 1
            self.place[obj] = int(Location.LIMBO)
            if self.loc == self.place[int(Object.PLANT)]:
                return self._water_the_plant(obj)
            if self.loc == self.place[int(Object.DOOR)]:
                return self._pour_on_door(obj)
            return self._report("Your bottle is empty and the ground is wet.")

        if verb == Action.FILL:
            if obj == Object.VASE:
                return self._fill_the_vase()
            if not self._here(int(Object.BOTTLE)):
                if obj == Object.NOTHING:
                    return _GET_OBJECT
                return _REPORT_DEFAULT
            if obj not in (Object.NOTHING, Object.BOTTLE):
                return _REPORT_DEFAULT
            if not self._bottle_empty():
                return self._report("Your bottle is already full.")
            if self._no_liquid_here():
                return self._report("There is nothing here with which to fill the bottle.")
            self.prop[int(Object.BOTTLE)] = self._flags(self.loc) & OIL_FLAG
            if self._toting(int(Object.BOTTLE)):
                self.place[
                    int(Object.OIL) if self.prop[int(Object.BOTTLE)] else int(Object.WATER)
                ] = int(Location.INHAND)
            self._line(
                "Your bottle is now full of %s."
                % ("oil" if self.prop[int(Object.BOTTLE)] else "water")
            )
            return _CYCLE

        if verb == Action.TAKE:
            if self._toting(obj):
                return _REPORT_DEFAULT
            if self.base[obj]:
                if obj == Object.CHAIN and self.prop[int(Object.BEAR)]:
                    return self._report("The chain is still locked.")
                if obj == Object.BEAR and self.prop[int(Object.BEAR)] == 1:
                    return self._report("The bear is still chained to the wall.")
                if obj == Object.PLANT and self.prop[int(Object.PLANT)] <= 0:
                    return self._report(
                        "The plant has exceptionally deep roots and cannot be pulled free."
                    )
                return self._report("You can't be serious!")
            if obj in (Object.WATER, Object.OIL):
                if self._here(int(Object.BOTTLE)) and self._object_in_bottle():
                    self.obj = obj = int(Object.BOTTLE)
                else:
                    self.obj = obj = int(Object.BOTTLE)
                    if self._toting(int(Object.BOTTLE)):
                        self.oldverb = self.verb
                        self.verb = Action.FILL
                        return _TRANSITIVE
                    return self._report("You have nothing in which to carry it.")
            if self.holding >= 7:
                return self._report(
                    "You can't carry anything more.  You'll have to drop something first."
                )
            if obj == Object.BIRD and self.prop[int(Object.BIRD)] == 0:
                if self._toting(int(Object.ROD)):
                    return self._report(
                        "The bird was unafraid when you entered, but as you approach it becomes\n"
                        "disturbed and you cannot catch it."
                    )
                if self._toting(int(Object.CAGE)):
                    self.prop[int(Object.BIRD)] = 1
                else:
                    return self._report("You can catch the bird, but you cannot carry it.")
            if obj == Object.BIRD or (obj == Object.CAGE and self.prop[int(Object.BIRD)]):
                self._carry(int(Object.BIRD) + int(Object.CAGE) - obj)
            self._carry(obj)
            if obj == Object.BOTTLE and not self._bottle_empty():
                self.place[
                    int(Object.OIL) if self.prop[int(Object.BOTTLE)] else int(Object.WATER)
                ] = int(Location.INHAND)
            return self._report_default_of(Action.RELAX)

        if verb == Action.DROP:
            if obj == Object.ROD and self._toting(int(Object.ROD2)) and not self._toting(
                int(Object.ROD)
            ):
                self.obj = obj = int(Object.ROD2)
            if not self._toting(obj):
                return _REPORT_DEFAULT
            if obj == Object.COINS and self._here(int(Object.PONY)):
                self._destroy(int(Object.COINS))
                self._drop(int(Object.BATTERIES), self.loc)
                self.prop[int(Object.BATTERIES)] = 0
                return self._report(self._note(self.offset[int(Object.BATTERIES)]))
            if obj == Object.BIRD:
                if self._here(int(Object.SNAKE)):
                    self._line(
                        "The little bird attacks the green snake, and in an astounding flurry\n"
                        "drives the snake away."
                    )
                    self.k = 1
                    if self.closed:
                        raise _DwarvesUpset
                    self._destroy(int(Object.SNAKE))
                    self.prop[int(Object.SNAKE)] = 1
                elif self._is_at_loc(int(Object.DRAGON)) and self.prop[int(Object.DRAGON)] == 0:
                    self._destroy(int(Object.BIRD))
                    self.prop[int(Object.BIRD)] = 0
                    if self.place[int(Object.SNAKE)] == Location.HMK:
                        self.lost_treasures += 1
                    return self._report(
                        "The little bird attacks the green dragon, and in an astounding flurry\n"
                        "gets burnt to a cinder.  The ashes blow away."
                    )
            if obj == Object.VASE and self.loc != Location.SOFT:
                self.prop[int(Object.VASE)] = (
                    0 if self.place[int(Object.PILLOW)] == self.loc else 2
                )
                self._line(
                    self._note(self.offset[int(Object.VASE)] + 1 + self.prop[int(Object.VASE)])
                )
                self.k = 1
                if self.prop[int(Object.VASE)]:
                    self.base[int(Object.VASE)] = int(Object.VASE)
            if obj == Object.BEAR and self._is_at_loc(int(Object.TROLL)):
                self._line(
                    "The bear lumbers toward the troll, who lets out a startled shriek and\n"
                    "scurries away.  The bear soon gives up the pursuit and wanders back."
                )
                self.k = 1
                self._destroy(int(Object.TROLL))
                self._destroy(int(Object.TROLL_))
                self._drop(int(Object.TROLL2), int(Location.SWSIDE))
                self._drop(int(Object.TROLL2_), int(Location.NESIDE))
                self.prop[int(Object.TROLL)] = 2
                self._move(int(Object.BRIDGE), int(Location.SWSIDE))
                self._move(int(Object.BRIDGE_), int(Location.NESIDE))
            if self._object_in_bottle():
                self.obj = obj = int(Object.BOTTLE)
            if obj == Object.BOTTLE and not self._bottle_empty():
                self.place[
                    int(Object.OIL) if self.prop[int(Object.BOTTLE)] else int(Object.WATER)
                ] = int(Location.LIMBO)
            if obj == Object.BIRD:
                self.prop[int(Object.BIRD)] = 0
            elif obj == Object.CAGE and self.prop[int(Object.BIRD)]:
                self._drop(int(Object.BIRD), self.loc)
            self._drop(obj, self.loc)
            if self.k:
                return _CYCLE
            return self._report_default_of(Action.RELAX)

        if verb == Action.TOSS:
            if obj == Object.ROD and self._toting(int(Object.ROD2)) and not self._toting(
                int(Object.ROD)
            ):
                self.obj = obj = int(Object.ROD2)
            if not self._toting(obj):
                return _REPORT_DEFAULT
            if self._is_treasure(obj) and self._is_at_loc(int(Object.TROLL)):
                self._drop(obj, int(Location.LIMBO))
                self._destroy(int(Object.TROLL))
                self._destroy(int(Object.TROLL_))
                self._drop(int(Object.TROLL2), int(Location.SWSIDE))
                self._drop(int(Object.TROLL2_), int(Location.NESIDE))
                self._move(int(Object.BRIDGE), int(Location.SWSIDE))
                self._move(int(Object.BRIDGE_), int(Location.NESIDE))
                return self._report("The troll catches your treasure and scurries away out of sight.")
            if obj == Object.FOOD and self._here(int(Object.BEAR)):
                self.obj = obj = int(Object.BEAR)
                self.oldverb = self.verb
                self.verb = Action.FEED
                return _TRANSITIVE
            if obj != Object.AXE:
                self.oldverb = self.verb
                self.verb = Action.DROP
                return _TRANSITIVE
            if self._dwarf():
                j = 1
                while self.dloc[j] != self.loc:
                    j += 1
                if self.rng.ran(3) < 2:
                    self.dloc[j] = int(Location.LIMBO)
                    self.dseen[j] = False
                    self.dkill += 1
                    if self.dkill == 1:
                        self._line(
                            "You killed a little dwarf.  The body vanishes in a cloud of greasy\n"
                            "black smoke."
                        )
                    else:
                        self._line("You killed a little dwarf.")
                else:
                    self._line("You attack a little dwarf, but he dodges out of the way.")
                self._drop(int(Object.AXE), self.loc)
                raise _Motion(int(Motion.NOWHERE))
            if self._is_at_loc(int(Object.DRAGON)) and self.prop[int(Object.DRAGON)] == 0:
                self._line("The axe bounces harmlessly off the dragon's thick scales.")
            elif self._is_at_loc(int(Object.TROLL)):
                self._line(
                    "The troll deftly catches the axe, examines it carefully, and tosses it\n"
                    'back, declaring, "Good workmanship, but it\'s not valuable enough."'
                )
            elif self._here(int(Object.BEAR)) and self.prop[int(Object.BEAR)] == 0:
                self._drop(int(Object.AXE), self.loc)
                self.prop[int(Object.AXE)] = 1
                self.base[int(Object.AXE)] = int(Object.AXE)
                if self.place[int(Object.BEAR)] == self.loc:
                    self._move(int(Object.BEAR), self.loc)
                return self._report(
                    "The axe misses and lands near the bear where you can't get at it."
                )
            else:
                self.obj = int(Object.NOTHING)
                self.oldverb = self.verb
                self.verb = Action.KILL
                return _TRANSITIVE
            self._drop(int(Object.AXE), self.loc)
            raise _Motion(int(Motion.NOWHERE))

        if verb == Action.KILL:
            if obj == Object.NOTHING:
                obj = self._unique_target()
                if obj is None:
                    return _GET_OBJECT
                self.obj = obj
            if obj == Object.NOTHING:
                return self._report("There is nothing here to attack.")
            if obj == Object.BIRD:
                if self.closed:
                    return self._report("Oh, leave the poor unhappy bird alone.")
                self._destroy(int(Object.BIRD))
                self.prop[int(Object.BIRD)] = 0
                if self.place[int(Object.SNAKE)] == Location.HMK:
                    self.lost_treasures += 1
                return self._report("The little bird is now dead.  Its body disappears.")
            if obj == Object.DRAGON:
                if self.prop[int(Object.DRAGON)] == 0:
                    return self._kill_dragon()
                return self._report("For crying out loud, the poor thing is already dead!")
            if obj in (Object.CLAM, Object.OYSTER):
                return self._report("The shell is very strong and impervious to attack.")
            if obj == Object.SNAKE:
                return self._report(
                    "Attacking the snake both doesn't work and is very dangerous."
                )
            if obj == Object.DWARF:
                if self.closed:
                    raise _DwarvesUpset
                return self._report("With what?  Your bare hands?")
            if obj == Object.TROLL:
                return self._report(
                    "Trolls are close relatives with the rocks and have skin as tough as\n"
                    "a rhinoceros hide.  The troll fends off your blows effortlessly."
                )
            if obj == Object.BEAR:
                if self.prop[int(Object.BEAR)] == 0:
                    return self._report("With what?  Your bare hands?  Against HIS bear hands?")
                if self.prop[int(Object.BEAR)] == 3:
                    return self._report("For crying out loud, the poor thing is already dead!")
                return self._report("The bear is confused; he only wants to be your friend.")
            return _REPORT_DEFAULT

        if verb == Action.FEED:
            if obj == Object.BIRD:
                return self._report(
                    "It's not hungry (it's merely pinin' for the fjords).  Besides, you\n"
                    "have no bird seed."
                )
            if obj == Object.TROLL:
                return self._report(
                    "Gluttony is not one of the troll's vices.  Avarice, however, is."
                )
            if obj == Object.DRAGON:
                if self.prop[int(Object.DRAGON)]:
                    return self._report_default_of(Action.EAT)
                return self._report("There's nothing here it wants to eat (except perhaps you).")
            if obj == Object.SNAKE:
                if self.closed or not self._here(int(Object.BIRD)):
                    return self._report("There's nothing here it wants to eat (except perhaps you).")
                self._destroy(int(Object.BIRD))
                self.prop[int(Object.BIRD)] = 0
                self.lost_treasures += 1
                return self._report("The snake has now devoured your bird.")
            if obj == Object.BEAR:
                if not self._here(int(Object.FOOD)):
                    if self.prop[int(Object.BEAR)] == 0:
                        return self._report(
                            "There's nothing here it wants to eat (except perhaps you)."
                        )
                    if self.prop[int(Object.BEAR)] == 3:
                        self.verb = Action.EAT
                    return _REPORT_DEFAULT
                self._destroy(int(Object.FOOD))
                self.prop[int(Object.BEAR)] = 1
                self.prop[int(Object.AXE)] = 0
                self.base[int(Object.AXE)] = 0
                return self._report(
                    "The bear eagerly wolfs down your food, after which he seems to calm\n"
                    "down considerably and even becomes rather friendly."
                )
            if obj == Object.DWARF:
                if not self._here(int(Object.FOOD)):
                    return _REPORT_DEFAULT
                self.dflag += 1
                return self._report(
                    "You fool, dwarves eat only coal!  Now you've made him REALLY mad!"
                )
            return self._report(DEFAULT_MSG[Action.CALM])

        if verb in (Action.OPEN, Action.CLOSE):
            if obj in (Object.OYSTER, Object.CLAM):
                return self._open_clam_or_oyster(obj)
            if obj in (Object.GRATE, Object.CHAIN):
                if not self._here(int(Object.KEYS)):
                    return self._report("You have no keys!")
                return self._open_grate_or_chain(obj)
            if obj == Object.KEYS:
                return self._report("You can't lock or unlock the keys.")
            if obj == Object.CAGE:
                return self._report("It has no lock.")
            if obj == Object.DOOR:
                if self.prop[int(Object.DOOR)]:
                    return self._report_default_of(Action.RELAX)
                return self._report("The door is extremely rusty and refuses to open.")
            return _REPORT_DEFAULT

        if verb == Action.READ:
            if self._dark():
                return _CANT_SEE_IT
            if obj == Object.MAG:
                return self._report("I'm afraid the magazine is written in dwarvish.")
            if obj == Object.TABLET:
                return self._report('"CONGRATULATIONS ON BRINGING LIGHT INTO THE DARK-ROOM!"')
            if obj == Object.MESSAGE:
                return self._report(
                    '"This is not the maze where the pirate hides his treasure chest."'
                )
            if obj == Object.OYSTER:
                if self.hinted[1]:
                    if self._toting(int(Object.OYSTER)):
                        return self._report("It says the same thing it did before.")
                elif self.closed and self._toting(int(Object.OYSTER)):
                    self._offer(1)
                    return _CYCLE
            return _REPORT_DEFAULT

        return _REPORT_DEFAULT

    # --- action helpers ---------------------------------------------------

    def _smash_vase(self) -> str:
        self.prop[int(Object.VASE)] = 2
        self.base[int(Object.VASE)] = int(Object.VASE)
        return _CYCLE

    def _unique_target(self) -> int | None:
        """@<See if there's a unique object to attack@>; None means ask."""
        k = 0
        obj = int(Object.NOTHING)
        if self._dwarf():
            k, obj = k + 1, int(Object.DWARF)
        if self._here(int(Object.SNAKE)):
            k, obj = k + 1, int(Object.SNAKE)
        if self._is_at_loc(int(Object.DRAGON)) and self.prop[int(Object.DRAGON)] == 0:
            k, obj = k + 1, int(Object.DRAGON)
        if self._is_at_loc(int(Object.TROLL)):
            k, obj = k + 1, int(Object.TROLL)
        if self._here(int(Object.BEAR)) and self.prop[int(Object.BEAR)] == 0:
            k, obj = k + 1, int(Object.BEAR)
        if k == 0:
            if self._here(int(Object.BIRD)) and self.oldverb != Action.TOSS:
                k, obj = k + 1, int(Object.BIRD)
            if self._here(int(Object.CLAM)) or self._here(int(Object.OYSTER)):
                k, obj = k + 1, int(Object.CLAM)
        if k > 1:
            return None
        return obj

    def _kill_dragon(self) -> str:
        """@<Fun stuff for dragon@>."""
        self._line("With what?  Your bare hands?")
        self.verb = Action.ABSTAIN
        self.obj = int(Object.NOTHING)
        self.word1, self.word2 = self._listen()
        if not (_streq(self.word1, "yes") or _streq(self.word1, "y")):
            # goto pre_parse: reprocess what was just typed
            self.turns += 1
            self.foobar = -self.foobar if self.foobar > 0 else 0
            self._check_clocks_and_lamp()
            return self._pre_parse_specials()
        self._line(self._note(self.offset[int(Object.DRAGON)] + 1))
        self.prop[int(Object.DRAGON)] = 2
        self.prop[int(Object.RUG)] = 0
        self.base[int(Object.RUG)] = 0
        self.base[int(Object.DRAGON_)] = int(Object.DRAGON_)
        self._destroy(int(Object.DRAGON_))
        self.base[int(Object.RUG_)] = int(Object.RUG_)
        self._destroy(int(Object.RUG_))
        for t in range(1, MAX_OBJ + 1):
            if self.place[t] in (Location.SCAN1, Location.SCAN3):
                self._move(t, int(Location.SCAN2))
        self.loc = int(Location.SCAN2)
        raise _Motion(int(Motion.NOWHERE))

    def _water_the_plant(self, obj: int) -> str:
        if obj != Object.WATER:
            return self._report(
                'The plant indignantly shakes the oil off its leaves and asks, "Water?"'
            )
        self._line(self._note(self.prop[int(Object.PLANT)] + 1 + self.offset[int(Object.PLANT)]))
        self.prop[int(Object.PLANT)] += 2
        if self.prop[int(Object.PLANT)] > 4:
            self.prop[int(Object.PLANT)] = 0
        self.prop[int(Object.PLANT2)] = self.prop[int(Object.PLANT)] >> 1
        raise _Motion(int(Motion.NOWHERE))

    def _pour_on_door(self, obj: int) -> str:
        if obj == Object.WATER:
            self.prop[int(Object.DOOR)] = 0
            return self._report("The hinges are quite thoroughly rusted now and won't budge.")
        self.prop[int(Object.DOOR)] = 1
        return self._report("The oil has freed up the hinges so that the door will now open.")

    def _fill_the_vase(self) -> str:
        if self._no_liquid_here():
            return self._report("There is nothing here with which to fill the vase.\n")
        if not self._toting(int(Object.VASE)):
            return self._report_default_of(Action.DROP)
        self._line("The sudden change in temperature has delicately shattered the vase.")
        return self._smash_vase()

    def _open_clam_or_oyster(self, obj: int) -> str:
        name = "clam" if obj == Object.CLAM else "oyster"
        if self.verb == Action.CLOSE:
            return self._report("What?")
        if not self._toting(int(Object.TRIDENT)):
            self._write("You don't have anything strong enough to open the %s" % name)
            return self._report(".")
        if self._toting(obj):
            self._write("I advise you to put down the %s before opening it.  " % name)
            return self._report(">STRAIN!<" if obj == Object.CLAM else ">WRENCH!<")
        if obj == Object.CLAM:
            self._destroy(int(Object.CLAM))
            self._drop(int(Object.OYSTER), self.loc)
            self._drop(int(Object.PEARL), int(Location.SAC))
            return self._report(
                "A glistening pearl falls out of the clam and rolls away.  Goodness,\n"
                "this must really be an oyster.  (I never was very good at identifying\n"
                "bivalves.)  Whatever it is, it has now snapped shut again."
            )
        return self._report(
            "The oyster creaks open, revealing nothing but oyster inside.\n"
            "It promptly snaps shut again."
        )

    def _open_grate_or_chain(self, obj: int) -> str:
        if obj == Object.CHAIN:
            if self.verb == Action.OPEN:
                if self.prop[int(Object.CHAIN)] == 0:
                    return self._report("It was already unlocked.")
                if self.prop[int(Object.BEAR)] == 0:
                    return self._report(
                        "There is no way to get past the bear to unlock the chain, which is\n"
                        "probably just as well."
                    )
                self.prop[int(Object.CHAIN)] = 0
                self.base[int(Object.CHAIN)] = 0
                if self.prop[int(Object.BEAR)] == 3:
                    self.base[int(Object.BEAR)] = int(Object.BEAR)
                else:
                    self.prop[int(Object.BEAR)] = 2
                    self.base[int(Object.BEAR)] = 0
                return self._report("The chain is now unlocked.")
            if self.loc != Location.BARR:
                return self._report("There is nothing here to which the chain can be locked.")
            if self.prop[int(Object.CHAIN)]:
                return self._report("It was already locked.")
            self.prop[int(Object.CHAIN)] = 2
            self.base[int(Object.CHAIN)] = int(Object.CHAIN)
            if self._toting(int(Object.CHAIN)):
                self._drop(int(Object.CHAIN), self.loc)
            return self._report("The chain is now locked.")
        if self._closing():
            self._panic()
            return _CYCLE
        was = self.prop[int(Object.GRATE)]
        self.prop[int(Object.GRATE)] = 1 if self.verb == Action.OPEN else 0
        return self._report(
            {
                0: "It was already locked.",
                1: "The grate is now locked.",
                2: "The grate is now unlocked.",
                3: "It was already unlocked.",
            }[was + 2 * self.prop[int(Object.GRATE)]]
        )

    # ------------------------------------------------------------------
    # Special motions (@<Handle special motion words@>)
    # ------------------------------------------------------------------

    def _handle_special_motions(self, mot: int) -> tuple[bool, int] | None:
        """Returns None to stay put, else (skip_oldloc_update, motion)."""
        self.newloc = self.loc
        if mot == Motion.NOWHERE:
            return None
        if mot == Motion.BACK:
            target = self.oldoldloc if self._forced_move(self.oldloc) else self.oldloc
            self.oldoldloc = self.oldloc
            self.oldloc = self.loc
            if target == self.loc:
                self._line("Sorry, but I no longer seem to remember how you got here.")
                return None
            found = None
            via = None
            for q in range(D.START[self.loc], D.START[self.loc + 1]):
                dest = D.TRAVELS[q].dest
                if dest == target:
                    found = q
                    break
                if (
                    dest <= MAX_LOC
                    and self._forced_move(dest)
                    and D.TRAVELS[D.START[dest]].dest == target
                ):
                    via = q
            if found is None:
                if via is None:
                    self._line("You can't get there from here.")
                    return None
                found = via
            return (True, D.TRAVELS[found].mot)
        if mot == Motion.LOOK:
            self.look_count += 1
            if self.look_count <= 3:
                self._line(
                    "Sorry, but I am not allowed to give more detail.  I will repeat the\n"
                    "long description of your location."
                )
            self.was_dark = False
            self.visits[self.loc] = 0
            return None
        if mot == Motion.CAVE:
            if self.loc < int(MIN_IN_CAVE):
                self._line(
                    "I can't see where the cave is, but hereabouts no stream can run on\n"
                    "the surface for long.  I would try the stream."
                )
            else:
                self._line("I need more detailed instructions to do that.")
            return None
        return (False, mot)

    def _determine_next_location(self, mot: int) -> None:
        """@<Determine the next location, newloc@>."""
        start, end = D.START[self.loc], D.START[self.loc + 1]
        forced = self._forced_move(self.loc)
        q = start
        while q < end and not (forced or D.TRAVELS[q].mot == mot):
            q += 1
        if q == end:
            self._inapplicable_motion(mot)
            self.newloc = self.loc
            return
        while True:
            t = D.TRAVELS[q]
            j = t.cond
            if j > 300:
                ok = self.prop[j % 100] != (j - 300) // 100
            elif j <= 100:
                ok = j == 0 or self.rng.pct(j)
            else:
                ok = self._toting(j % 100) or (j >= 200 and self._is_at_loc(j % 100))
            if ok:
                if t.dest == Location.PDROP:
                    self._drop(int(Object.EMERALD), self.loc)
                    q = self._skip_dups(q)
                    continue
                break
            q = self._skip_dups(q)
            if q >= len(D.TRAVELS):
                self.newloc = self.loc
                return
        dest = D.TRAVELS[q].dest
        if dest <= MAX_LOC:
            self.newloc = dest
            return
        if dest > MAX_SPEC:
            self._line(D.REMARKS[dest - MAX_SPEC - 1])
            self.newloc = self.loc
            return
        if dest == Location.PPASS:
            if self.holding == 0 or (
                self._toting(int(Object.EMERALD)) and self.holding == 1
            ):
                self.newloc = int(Location.ALCOVE) + int(Location.PROOM) - self.loc
                return
            self._line(
                "Something you're carrying won't fit through the tunnel with you.\n"
                "You'd best take inventory and drop something."
            )
            self.newloc = self.loc
            return
        if dest == Location.TROLL:
            self._cross_troll_bridge()
            return
        self.newloc = self.loc

    def _skip_dups(self, q: int) -> int:
        """``no_good``: skip instructions with the same destination and condition."""
        qq = q
        q += 1
        while (
            q < len(D.TRAVELS)
            and D.TRAVELS[q].dest == D.TRAVELS[qq].dest
            and D.TRAVELS[q].cond == D.TRAVELS[qq].cond
        ):
            q += 1
        return q

    def _inapplicable_motion(self, mot: int) -> None:
        """@<Report on inapplicable motion@>."""
        if mot == Motion.CRAWL:
            self._write("Which way?")
        elif mot in (Motion.XYZZY, Motion.PLUGH):
            self._write(DEFAULT_MSG[Action.WAVE])
        elif self.verb in (Action.FIND, Action.INVENTORY):
            self._write(DEFAULT_MSG[Action.FIND])
        elif mot <= Motion.FORWARD:
            if mot in (Motion.IN, Motion.OUT):
                self._write(
                    "I don't know in from out here.  Use compass points or name something\n"
                    "in the general direction you want to go."
                )
            elif mot in (Motion.FORWARD, Motion.L, Motion.R):
                self._write("I am unsure how you are facing.  Use compass points or nearby objects.")
            else:
                self._write("There is no way to go in that direction.")
        else:
            self._write("I don't know how to apply that word here.")
        self._write("\n")

    def _cross_troll_bridge(self) -> None:
        """@<Cross troll bridge if possible@>."""
        if self.prop[int(Object.TROLL)] == 1:
            self._move(int(Object.TROLL), int(Location.SWSIDE))
            self._move(int(Object.TROLL_), int(Location.NESIDE))
            self.prop[int(Object.TROLL)] = 0
            self._destroy(int(Object.TROLL2))
            self._destroy(int(Object.TROLL2_))
            self._move(int(Object.BRIDGE), int(Location.SWSIDE))
            self._move(int(Object.BRIDGE_), int(Location.NESIDE))
            self._line(self._note(self.offset[int(Object.TROLL)] + 1))
            self.newloc = self.loc
            return
        self.newloc = int(Location.NESIDE) + int(Location.SWSIDE) - self.loc
        if self.prop[int(Object.TROLL)] == 0:
            self.prop[int(Object.TROLL)] = 1
        if not self._toting(int(Object.BEAR)):
            return
        self._line(
            "Just as you reach the other side, the bridge buckles beneath the\n"
            "weight of the bear, who was still following you around.  You\n"
            "scrabble desperately for support, but as the bridge collapses you\n"
            "stumble back and fall into the chasm."
        )
        self.prop[int(Object.BRIDGE)] = 1
        self.prop[int(Object.TROLL)] = 2
        self._drop(int(Object.BEAR), self.newloc)
        self.base[int(Object.BEAR)] = int(Object.BEAR)
        self.prop[int(Object.BEAR)] = 3
        if self.prop[int(Object.SPICES)] < 0 and self.place[int(Object.SPICES)] >= Location.NESIDE:
            self.lost_treasures += 1
        if self.prop[int(Object.CHAIN)] < 0 and self.place[int(Object.CHAIN)] >= Location.NESIDE:
            self.lost_treasures += 1
        self.oldoldloc = self.newloc
        raise _Death

    # ------------------------------------------------------------------
    # Dwarves and the pirate (@* Dwarf stuff@>)
    # ------------------------------------------------------------------

    def _move_actors(self) -> None:
        """@<Possibly move dwarves and the pirate@>."""
        if self.loc > MAX_PIRATE_LOC or self.loc == Location.LIMBO:
            return
        if self.dflag == 0:
            if self.loc >= int(MIN_LOWER_LOC):
                self.dflag = 1
        elif self.dflag == 1:
            if self.loc >= int(MIN_LOWER_LOC) and self.rng.pct(5):
                self._advance_dflag()
        else:
            self._move_dwarves()

    def _advance_dflag(self) -> None:
        """@<Advance dflag to 2@>."""
        self.dflag = 2
        for _ in range(2):
            if self.rng.pct(50):
                self.dloc[1 + self.rng.ran(D.ND)] = int(Location.LIMBO)
        for j in range(1, D.ND + 1):
            if self.dloc[j] == self.loc:
                self.dloc[j] = int(Location.NUGGET)
            self.odloc[j] = self.dloc[j]
        self._line(
            "A little dwarf just walked around a corner, saw you, threw a little\n"
            "axe at you, cursed, and ran away.  (The axe missed.)"
        )
        self._drop(int(Object.AXE), self.loc)

    def _move_dwarves(self) -> None:
        """@<Move dwarves and the pirate@>."""
        self.dtotal = self.attack = self.stick = 0
        for j in range(0, D.ND + 1):
            if self.dloc[j] == Location.LIMBO:
                continue
            ploc: list[int] = []
            for q in range(D.START[self.dloc[j]], D.START[self.dloc[j] + 1]):
                dest = D.TRAVELS[q].dest
                if (
                    dest >= int(MIN_LOWER_LOC)
                    and dest != self.odloc[j]
                    and dest != self.dloc[j]
                    and (not ploc or dest != ploc[-1])
                    and len(ploc) < 19
                    and D.TRAVELS[q].cond != 100
                    and dest <= (MAX_PIRATE_LOC if j == 0 else int(MIN_FORCED_LOC) - 1)
                ):
                    ploc.append(dest)
            if not ploc:
                ploc = [self.odloc[j]]
            self.odloc[j] = self.dloc[j]
            self.dloc[j] = ploc[self.rng.ran(len(ploc))]
            self.dseen[j] = (
                self.dloc[j] == self.loc
                or self.odloc[j] == self.loc
                or (self.dseen[j] and self.loc >= int(MIN_LOWER_LOC))
            )
            if self.dseen[j]:
                self._follow(j)
        if self.dtotal:
            self._attack()

    def _follow(self, j: int) -> None:
        """@<Make dwarf j follow@>."""
        self.dloc[j] = self.loc
        if j == 0:
            self._pirate_track()
            return
        self.dtotal += 1
        if self.odloc[j] == self.dloc[j]:
            self.attack += 1
            if self.knife_loc >= 0:
                self.knife_loc = self.loc
            if self.rng.ran(1000) < 95 * (self.dflag - 2):
                self.stick += 1

    def _attack(self) -> None:
        """@<Make the threatening dwarves attack@>."""
        if self.dtotal == 1:
            self._write("There is a threatening little dwarf")
        else:
            self._write("There are %d threatening little dwarves" % self.dtotal)
        self._write(" in the room with you!\n")
        if not self.attack:
            return
        if self.dflag == 2:
            self.dflag = 3
        if self.attack == 1:
            self.k = 0
            self._write("One sharp nasty knife is thrown")
        else:
            self.k = 2
            self._write(" %d of them throw knives" % self.attack)
        self._write(" at you --- ")
        if self.stick <= 1:
            self._write(ATTACK_MSG[self.k + self.stick] + "!\n")
        else:
            self._write("%d of them get you!\n" % self.stick)
        if self.stick:
            self.oldoldloc = self.loc
            raise _Death

    def _pirate_track(self) -> None:
        """@<Make the pirate track you@>."""
        if self.loc == MAX_PIRATE_LOC or self.prop[int(Object.CHEST)] >= 0:
            return
        k = 0
        for i in range(int(MIN_TREASURE), MAX_OBJ + 1):
            if not self._too_easy(i) and self._toting(i):
                k = -1
                break
            if self._here(i):
                k = 1
        if k < 0:
            self._take_booty()
        elif (
            self.tally == self.lost_treasures + 1
            and k == 0
            and self.place[int(Object.MESSAGE)] == Location.LIMBO
            and self.prop[int(Object.LAMP)]
            and self._here(int(Object.LAMP))
        ):
            self._spot_pirate()
        elif self.odloc[0] != self.dloc[0] and self.rng.pct(20):
            self._line("There are faint rustling noises from the darkness behind you.")

    def _take_booty(self) -> None:
        """@<Take booty and hide it in the chest@>."""
        self._line(
            'Out from the shadows behind you pounces a bearded pirate!  "Har, har,"\n'
            'he chortles, "I\'ll just take all this booty and hide it away with me\n'
            'chest deep in the maze!"  He snatches your treasure and vanishes into\n'
            "the gloom."
        )
        for i in range(int(MIN_TREASURE), MAX_OBJ + 1):
            if not self._too_easy(i):
                if self.base[i] == 0 and self.place[i] == self.loc:
                    self._carry(i)
                if self._toting(i):
                    self._drop(i, int(D.CHEST_LOC))
        if self.place[int(Object.MESSAGE)] == Location.LIMBO:
            self._move(int(Object.CHEST), int(D.CHEST_LOC))
            self._move(int(Object.MESSAGE), int(D.MESSAGE_LOC))
        self.dloc[0] = self.odloc[0] = int(D.CHEST_LOC)
        self.dseen[0] = False

    def _spot_pirate(self) -> None:
        """@<Let the pirate be spotted@>."""
        self._line(
            "There are faint rustling noises from the darkness behind you.  As you\n"
            "turn toward them, the beam of your lamp falls across a bearded pirate.\n"
            'He is carrying a large chest.  "Shiver me timbers!" he cries, "I\'ve\n'
            "been spotted!  I'd best hie meself off to the maze to hide me chest!\"\n"
            "With that, he vanishes into the gloom."
        )
        self._move(int(Object.CHEST), int(D.CHEST_LOC))
        self._move(int(Object.MESSAGE), int(D.MESSAGE_LOC))
        self.dloc[0] = self.odloc[0] = int(D.CHEST_LOC)
        self.dseen[0] = False

    # ------------------------------------------------------------------
    # Clocks, lamp, closing (@* Closing the cave@>, @* Death@>)
    # ------------------------------------------------------------------

    def _check_clocks_and_lamp(self) -> None:
        """@<Check the clocks and the lamp@>."""
        if self.tally == 0 and self.loc >= int(MIN_LOWER_LOC) and self.loc != Location.Y2:
            self.clock1 -= 1
        if self.clock1 == 0:
            self._warn_closing()
        else:
            if self.clock1 < 0:
                self.clock2 -= 1
            if self.clock2 == 0:
                self._close_cave()
            else:
                self._check_lamp()

    def _check_lamp(self) -> None:
        """@<Check the lamp@>."""
        if self.prop[int(Object.LAMP)] == 1:
            self.limit -= 1
        if (
            self.limit <= 30
            and self._here(int(Object.BATTERIES))
            and self.prop[int(Object.BATTERIES)] == 0
            and self._here(int(Object.LAMP))
        ):
            self._line(
                "Your lamp is getting dim.  I'm taking the liberty of replacing\n"
                "the batteries."
            )
            self.prop[int(Object.BATTERIES)] = 1
            if self._toting(int(Object.BATTERIES)):
                self._drop(int(Object.BATTERIES), self.loc)
            self.limit = 2500
        elif self.limit == 0:
            self.limit = -1
            self.prop[int(Object.LAMP)] = 0
            if self._here(int(Object.LAMP)):
                self._write("Your lamp has run out of power.")
        elif self.limit < 0 and self.loc < int(MIN_IN_CAVE):
            self._line(
                "There's not much point in wandering around out here, and you can't\n"
                "explore the cave without a lamp.  So let's just call it a day."
            )
            self.gave_up = True
            raise _Quit
        elif self.limit <= 30 and not self.warned and self._here(int(Object.LAMP)):
            self._write("Your lamp is getting dim")
            if self.prop[int(Object.BATTERIES)] == 1:
                self._write(", and you're out of spare batteries.  You'd\nbest start wrapping this up.\n")
            elif self.place[int(Object.BATTERIES)] == Location.LIMBO:
                self._write(
                    ".  You'd best start wrapping this up, unless\n"
                    "you can find some fresh batteries.  I seem to recall that there's\n"
                    "a vending machine in the maze.  Bring some coins with you.\n"
                )
            else:
                self._write(".  You'd best go back for those batteries.\n")
            self.warned = True

    def _warn_closing(self) -> None:
        """@<Warn that the cave is closing@>."""
        self._line(
            'A sepulchral voice, reverberating through the cave, says, "Cave\n'
            'closing soon.  All adventurers exit immediately through main office."'
        )
        self.clock1 = -1
        self.prop[int(Object.GRATE)] = 0
        self.prop[int(Object.CRYSTAL)] = 0
        for j in range(0, D.ND + 1):
            self.dseen[j] = False
            self.dloc[j] = int(Location.LIMBO)
        self._destroy(int(Object.TROLL))
        self._destroy(int(Object.TROLL_))
        self._move(int(Object.TROLL2), int(Location.SWSIDE))
        self._move(int(Object.TROLL2_), int(Location.NESIDE))
        self._move(int(Object.BRIDGE), int(Location.SWSIDE))
        self._move(int(Object.BRIDGE_), int(Location.NESIDE))
        if self.prop[int(Object.BEAR)] != 3:
            self._destroy(int(Object.BEAR))
        self.prop[int(Object.CHAIN)] = 0
        self.base[int(Object.CHAIN)] = 0
        self.prop[int(Object.AXE)] = 0
        self.base[int(Object.AXE)] = 0

    def _close_cave(self) -> None:
        """@<Close the cave@>."""
        self._line(
            'The sepulchral voice intones, "The cave is now closed."  As the echoes\n'
            "fade, there is a blinding flash of light (and a small puff of orange\n"
            "smoke). . . .    Then your eyes refocus; you look around and find..."
        )
        self._move(int(Object.BOTTLE), int(Location.NEEND))
        self.prop[int(Object.BOTTLE)] = -2
        self._move(int(Object.PLANT), int(Location.NEEND))
        self.prop[int(Object.PLANT)] = -1
        self._move(int(Object.OYSTER), int(Location.NEEND))
        self.prop[int(Object.OYSTER)] = -1
        self._move(int(Object.LAMP), int(Location.NEEND))
        self.prop[int(Object.LAMP)] = -1
        self._move(int(Object.ROD), int(Location.NEEND))
        self.prop[int(Object.ROD)] = -1
        self._move(int(Object.DWARF), int(Location.NEEND))
        self.prop[int(Object.DWARF)] = -1
        self._move(int(Object.MIRROR), int(Location.NEEND))
        self.prop[int(Object.MIRROR)] = -1
        self.loc = self.oldloc = int(Location.NEEND)
        self._move(int(Object.GRATE), int(Location.SWEND))
        self._move(int(Object.SNAKE), int(Location.SWEND))
        self.prop[int(Object.SNAKE)] = -2
        self._move(int(Object.BIRD), int(Location.SWEND))
        self.prop[int(Object.BIRD)] = -2
        self._move(int(Object.CAGE), int(Location.SWEND))
        self.prop[int(Object.CAGE)] = -1
        self._move(int(Object.ROD2), int(Location.SWEND))
        self.prop[int(Object.ROD2)] = -1
        self._move(int(Object.PILLOW), int(Location.SWEND))
        self.prop[int(Object.PILLOW)] = -1
        self._move(int(Object.MIRROR_), int(Location.SWEND))
        self.place[int(Object.WATER)] = int(Location.LIMBO)
        self.place[int(Object.OIL)] = int(Location.LIMBO)
        for j in range(1, MAX_OBJ + 1):
            if self._toting(j):
                self._destroy(j)
        self.closed = True
        self.bonus = 10
        raise _Motion(int(Motion.NOWHERE))

    def _panic(self) -> None:
        """@<Panic at closing time@>."""
        if not self.panic:
            self.clock2 = 15
            self.panic = True
        self._line(
            "A mysterious recorded voice groans into life and announces:\n"
            '"This exit is closed.  Please leave via main office."'
        )

    def _death(self) -> None:
        """@<Deal with death and resurrection@>."""
        self.death_count += 1
        if self._closing():
            self._line(
                "It looks as though you're dead.  Well, seeing as how it's so close\n"
                "to closing time anyway, let's just call it a day."
            )
            raise _Quit
        i = 2 * self.death_count - 2
        if not self._yes(D.DEATH_WISHES[i], D.DEATH_WISHES[i + 1], OK) or (
            self.death_count == D.MAX_DEATHS
        ):
            raise _Quit
        if self._toting(int(Object.LAMP)):
            self.prop[int(Object.LAMP)] = 0
        self.place[int(Object.WATER)] = int(Location.LIMBO)
        self.place[int(Object.OIL)] = int(Location.LIMBO)
        for j in range(MAX_OBJ, 0, -1):
            if self._toting(j):
                self._drop(
                    j, int(Location.ROAD) if j == Object.LAMP else self.oldoldloc
                )
        self.loc = self.oldloc = int(Location.HOUSE)
