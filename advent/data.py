"""Static cave data for the Adventure port.

Everything in this module is a transcription of the "Cave data", "Cave
connections", and "Object data" sections of ``advent.w``:

* ``LOCATIONS``: the long/short description and flags of every real place.
* ``TRAVELS`` / ``START``: the flat instruction table.  Each instruction is
  ``(motion, condition, destination)``.  ``START[loc]`` is the index of the
  first instruction of ``loc``; ``START[loc + 1]`` is the end.
* ``REMARKS``: the messages printed by "stay put" destinations.
* ``OBJECTS`` / ``NOTES``: every object, its base, starting place, and the
  note table used for property-dependent descriptions.
* Hint, death, and ranking tables.
"""

from __future__ import annotations

from dataclasses import dataclass

from .vocabulary import (
    Action,
    BIRD_HINT,
    CAVE_HINT,
    DARK_HINT,
    LIGHTED,
    LIQUID,
    Location,
    MAX_OBJ,
    MAX_SPEC,
    MIN_TREASURE,
    Motion,
    Object,
    OIL,
    SNAKE_HINT,
    TWIST_HINT,
    WITT_HINT,
)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

FORCE = Motion.N  # any motion value; forced locations ignore the motion
TRAVEL_SIZE = 740
REM_SIZE = 15
HASH_PRIME = 1009
BUF_SIZE = 72
MAX_SCORE = 350
MAX_DEATHS = 3
N_HINTS = 8
TALLY = 15
CLOCK1 = 15
CLOCK2 = 30
INTERVAL = 5
INITIAL_LIMIT = 330
INSTRUCTIONS_LIMIT = 1000

CHEST_LOC = Location.DEAD2
MESSAGE_LOC = Location.PONY

IS_TREASURE = lambda t: int(t) >= int(MIN_TREASURE)  # noqa: E731


@dataclass(frozen=True)
class Instruction:
    mot: int
    cond: int
    dest: int


@dataclass(frozen=True)
class LocationInfo:
    long: str | None
    short: str | None
    flags: int


@dataclass(frozen=True)
class ObjectInfo:
    name: str | None
    base: int
    start: int
    offset: int


LOCATIONS: dict[int, LocationInfo] = {}
TRAVELS: list[Instruction] = []
START: dict[int, int] = {}
REMARKS: list[str] = []
OBJECTS: dict[int, ObjectInfo] = {}
NOTES: list[str | None] = []


# ---------------------------------------------------------------------------
# Builders
# ---------------------------------------------------------------------------


def make_loc(
    loc: Location, long_desc: str | None, short_desc: str | None, flags: int
) -> None:
    START[int(loc)] = len(TRAVELS)
    LOCATIONS[int(loc)] = LocationInfo(long_desc, short_desc, flags)


def inst(mot: int, cond: int, dest: int) -> None:
    TRAVELS.append(Instruction(int(mot), cond, int(dest)))


def ditto(mot: int) -> None:
    prev = TRAVELS[-1]
    TRAVELS.append(Instruction(int(mot), prev.cond, prev.dest))


def remark(text: str) -> int:
    REMARKS.append(text)
    return int(MAX_SPEC) + len(REMARKS)


def sayit() -> int:
    return int(MAX_SPEC) + len(REMARKS)


def holds(o: Object) -> int:
    return 100 + int(o)


def sees(o: Object) -> int:
    return 200 + int(o)


def prop_ne(o: Object, k: int) -> int:
    return 300 + int(o) + 100 * k


def new_obj(
    obj: Object,
    name: str | None,
    base: int,
    start: int,
    *notes: str | None,
) -> None:
    OBJECTS[int(obj)] = ObjectInfo(name, int(base), int(start), len(NOTES))
    NOTES.extend(notes)


# ---------------------------------------------------------------------------
# Locations and travel table (in source order)
# ---------------------------------------------------------------------------

make_loc(
    Location.ROAD,
    "You are standing at the end of a road before a small brick building.\n"
    "Around you is a forest.  A small stream flows out of the building and\n"
    "down a gully.",
    "You're at end of road again.",
    LIGHTED + LIQUID,
)
inst(Motion.W, 0, Location.HILL)
ditto(Motion.U)
ditto(Motion.ROAD)
inst(Motion.E, 0, Location.HOUSE)
ditto(Motion.IN)
ditto(Motion.HOUSE)
ditto(Motion.ENTER)
inst(Motion.S, 0, Location.VALLEY)
ditto(Motion.D)
ditto(Motion.GULLY)
ditto(Motion.STREAM)
ditto(Motion.DOWNSTREAM)
inst(Motion.N, 0, Location.FOREST)
ditto(Motion.WOODS)
inst(Motion.DEPRESSION, 0, Location.OUTSIDE)

make_loc(
    Location.HILL,
    "You have walked up a hill, still in the forest.  The road slopes back\n"
    "down the other side of the hill.  There is a building in the distance.",
    "You're at hill in road.",
    LIGHTED,
)
inst(Motion.ROAD, 0, Location.ROAD)
ditto(Motion.HOUSE)
ditto(Motion.FORWARD)
ditto(Motion.E)
ditto(Motion.D)
inst(Motion.WOODS, 0, Location.FOREST)
ditto(Motion.N)
ditto(Motion.S)

make_loc(
    Location.HOUSE,
    "You are inside a building, a well house for a large spring.",
    "You're inside building.",
    LIGHTED + LIQUID,
)
inst(Motion.ENTER, 0, Location.ROAD)
ditto(Motion.OUT)
ditto(Motion.OUTDOORS)
ditto(Motion.W)
inst(Motion.XYZZY, 0, Location.DEBRIS)
inst(Motion.PLUGH, 0, Location.Y2)
inst(Motion.DOWNSTREAM, 0, Location.SEWER)
ditto(Motion.STREAM)

make_loc(
    Location.VALLEY,
    "You are in a valley in the forest beside a stream tumbling along a\n"
    "rocky bed.",
    "You're in valley.",
    LIGHTED + LIQUID,
)
inst(Motion.UPSTREAM, 0, Location.ROAD)
ditto(Motion.HOUSE)
ditto(Motion.N)
inst(Motion.WOODS, 0, Location.FOREST)
ditto(Motion.E)
ditto(Motion.W)
ditto(Motion.U)
inst(Motion.DOWNSTREAM, 0, Location.SLIT)
ditto(Motion.S)
ditto(Motion.D)
inst(Motion.DEPRESSION, 0, Location.OUTSIDE)

make_loc(
    Location.FOREST,
    "You are in open forest, with a deep valley to one side.",
    "You're in forest.",
    LIGHTED,
)
inst(Motion.VALLEY, 0, Location.VALLEY)
ditto(Motion.E)
ditto(Motion.D)
inst(Motion.WOODS, 50, Location.FOREST)
ditto(Motion.FORWARD)
ditto(Motion.N)
inst(Motion.WOODS, 0, Location.WOODS)
inst(Motion.W, 0, Location.FOREST)
ditto(Motion.S)

make_loc(
    Location.WOODS,
    "You are in open forest near both a valley and a road.",
    LOCATIONS[int(Location.FOREST)].short,
    LIGHTED,
)
inst(Motion.ROAD, 0, Location.ROAD)
ditto(Motion.N)
inst(Motion.VALLEY, 0, Location.VALLEY)
ditto(Motion.E)
ditto(Motion.W)
ditto(Motion.D)
inst(Motion.WOODS, 0, Location.FOREST)
ditto(Motion.S)

make_loc(
    Location.SLIT,
    "At your feet all the water of the stream splashes into a 2-inch slit\n"
    "in the rock.  Downstream the streambed is bare rock.",
    "You're at slit in streambed.",
    LIGHTED + LIQUID,
)
inst(Motion.HOUSE, 0, Location.ROAD)
inst(Motion.UPSTREAM, 0, Location.VALLEY)
ditto(Motion.N)
inst(Motion.WOODS, 0, Location.FOREST)
ditto(Motion.E)
ditto(Motion.W)
inst(Motion.DOWNSTREAM, 0, Location.OUTSIDE)
ditto(Motion.ROCK)
ditto(Motion.BED)
ditto(Motion.S)
SLIT_RMK = remark("You don't fit through a two-inch slit!")
inst(Motion.SLIT, 0, SLIT_RMK)
ditto(Motion.STREAM)
ditto(Motion.D)

make_loc(
    Location.OUTSIDE,
    "You are in a 20-foot depression floored with bare dirt.  Set into the\n"
    "dirt is a strong steel grate mounted in concrete.  A dry streambed\n"
    "leads into the depression.",
    "You're outside grate.",
    LIGHTED + CAVE_HINT,
)
inst(Motion.WOODS, 0, Location.FOREST)
ditto(Motion.E)
ditto(Motion.W)
ditto(Motion.S)
inst(Motion.HOUSE, 0, Location.ROAD)
inst(Motion.UPSTREAM, 0, Location.SLIT)
ditto(Motion.GULLY)
ditto(Motion.N)
inst(Motion.ENTER, prop_ne(Object.GRATE, 0), Location.INSIDE)
ditto(Motion.ENTER)
ditto(Motion.IN)
ditto(Motion.D)
GRATE_RMK = remark("You can't go through a locked steel grate!")
inst(Motion.ENTER, 0, GRATE_RMK)

make_loc(
    Location.INSIDE,
    "You are in a small chamber beneath a 3x3 steel grate to the surface.\n"
    "A low crawl over cobbles leads inwards to the west.",
    "You're below the grate.",
    LIGHTED,
)
inst(Motion.OUT, prop_ne(Object.GRATE, 0), Location.OUTSIDE)
ditto(Motion.OUT)
ditto(Motion.U)
inst(Motion.OUT, 0, GRATE_RMK)
inst(Motion.CRAWL, 0, Location.COBBLES)
ditto(Motion.COBBLES)
ditto(Motion.IN)
ditto(Motion.W)
inst(Motion.PIT, 0, Location.SPIT)
inst(Motion.DEBRIS, 0, Location.DEBRIS)

make_loc(
    Location.COBBLES,
    "You are crawling over cobbles in a low passage.  There is a dim light\n"
    "at the east end of the passage.",
    "You're in cobble crawl.",
    LIGHTED,
)
inst(Motion.OUT, 0, Location.INSIDE)
ditto(Motion.SURFACE)
ditto(Motion.NOWHERE)
ditto(Motion.E)
inst(Motion.IN, 0, Location.DEBRIS)
ditto(Motion.DARK)
ditto(Motion.W)
ditto(Motion.DEBRIS)
inst(Motion.PIT, 0, Location.SPIT)

make_loc(
    Location.DEBRIS,
    "You are in a debris room filled with stuff washed in from the surface.\n"
    "A low wide passage with cobbles becomes plugged with mud and debris\n"
    "here, but an awkward canyon leads upward and west.  A note on the wall\n"
    'says "MAGIC WORD XYZZY".',
    "You're in debris room.",
    0,
)
inst(Motion.DEPRESSION, prop_ne(Object.GRATE, 0), Location.OUTSIDE)
inst(Motion.ENTRANCE, 0, Location.INSIDE)
inst(Motion.CRAWL, 0, Location.COBBLES)
ditto(Motion.COBBLES)
ditto(Motion.PASSAGE)
ditto(Motion.LOW)
ditto(Motion.E)
inst(Motion.CANYON, 0, Location.AWK)
ditto(Motion.IN)
ditto(Motion.U)
ditto(Motion.W)
inst(Motion.XYZZY, 0, Location.HOUSE)
inst(Motion.PIT, 0, Location.SPIT)

make_loc(
    Location.AWK,
    "You are in an awkward sloping east/west canyon.",
    None,
    0,
)
inst(Motion.DEPRESSION, prop_ne(Object.GRATE, 0), Location.OUTSIDE)
inst(Motion.ENTRANCE, 0, Location.INSIDE)
inst(Motion.D, 0, Location.DEBRIS)
ditto(Motion.E)
ditto(Motion.DEBRIS)
inst(Motion.IN, 0, Location.BIRD)
ditto(Motion.U)
ditto(Motion.W)
inst(Motion.PIT, 0, Location.SPIT)

make_loc(
    Location.BIRD,
    "You are in a splendid chamber thirty feet high.  The walls are frozen\n"
    "rivers of orange stone.  An awkward canyon and a good passage exit\n"
    "from east and west sides of the chamber.",
    "You're in bird chamber.",
    BIRD_HINT,
)
inst(Motion.DEPRESSION, prop_ne(Object.GRATE, 0), Location.OUTSIDE)
inst(Motion.ENTRANCE, 0, Location.INSIDE)
inst(Motion.DEBRIS, 0, Location.DEBRIS)
inst(Motion.CANYON, 0, Location.AWK)
ditto(Motion.E)
inst(Motion.PASSAGE, 0, Location.SPIT)
ditto(Motion.PIT)
ditto(Motion.W)

make_loc(
    Location.SPIT,
    "At your feet is a small pit breathing traces of white mist.  An east\n"
    "passage ends here except for a small crack leading on.",
    "You're at top of small pit.",
    0,
)
inst(Motion.DEPRESSION, prop_ne(Object.GRATE, 0), Location.OUTSIDE)
inst(Motion.ENTRANCE, 0, Location.INSIDE)
inst(Motion.DEBRIS, 0, Location.DEBRIS)
inst(Motion.PASSAGE, 0, Location.BIRD)
ditto(Motion.E)
inst(Motion.D, holds(Object.GOLD), Location.NECK)
ditto(Motion.PIT)
ditto(Motion.STEPS)
inst(Motion.D, 0, Location.EMIST)
inst(Motion.CRACK, 0, Location.CRACK)
ditto(Motion.W)

make_loc(
    Location.EMIST,
    "You are at one end of a vast hall stretching forward out of sight to\n"
    "the west.  There are openings to either side.  Nearby, a wide stone\n"
    "staircase leads downward.  The hall is filled with wisps of white mist\n"
    "swaying to and fro almost as if alive.  A cold wind blows up the\n"
    "staircase.  There is a passage at the top of a dome behind you.",
    "You're in Hall of Mists.",
    0,
)
inst(Motion.L, 0, Location.NUGGET)
ditto(Motion.S)
inst(Motion.FORWARD, 0, Location.EFISS)
ditto(Motion.HALL)
ditto(Motion.W)
inst(Motion.STAIRS, 0, Location.HMK)
ditto(Motion.D)
ditto(Motion.N)
inst(Motion.U, holds(Object.GOLD), Location.CANT)
ditto(Motion.PIT)
ditto(Motion.STEPS)
ditto(Motion.DOME)
ditto(Motion.PASSAGE)
ditto(Motion.E)
inst(Motion.U, 0, Location.SPIT)
inst(Motion.Y2, 0, Location.JUMBLE)

make_loc(
    Location.NUGGET,
    "This is a low room with a crude note on the wall.  The note says,\n"
    '"You won\'t get it up the steps".',
    "You're in nugget of gold room.",
    0,
)
inst(Motion.HALL, 0, Location.EMIST)
ditto(Motion.OUT)
ditto(Motion.N)

make_loc(
    Location.EFISS,
    "You are on the east bank of a fissure slicing clear across the hall.\n"
    "The mist is quite thick here, and the fissure is too wide to jump.",
    "You're on east bank of fissure.",
    0,
)
inst(Motion.HALL, 0, Location.EMIST)
ditto(Motion.E)
BRIDGE_RMK = remark(
    "I respectfully suggest you go across the bridge instead of jumping."
)
inst(Motion.JUMP, prop_ne(Object.CRYSTAL, 0), BRIDGE_RMK)
inst(Motion.FORWARD, prop_ne(Object.CRYSTAL, 1), Location.LOSE)
remark("There is no way across the fissure.")
inst(Motion.OVER, prop_ne(Object.CRYSTAL, 1), sayit())
ditto(Motion.ACROSS)
ditto(Motion.W)
ditto(Motion.CROSS)
inst(Motion.OVER, 0, Location.WFISS)

make_loc(
    Location.WFISS,
    "You are on the west side of the fissure in the Hall of Mists.",
    None,
    0,
)
inst(Motion.JUMP, prop_ne(Object.CRYSTAL, 0), BRIDGE_RMK)
inst(Motion.FORWARD, prop_ne(Object.CRYSTAL, 1), Location.LOSE)
inst(Motion.OVER, prop_ne(Object.CRYSTAL, 1), sayit())
ditto(Motion.ACROSS)
ditto(Motion.E)
ditto(Motion.CROSS)
inst(Motion.OVER, 0, Location.EFISS)
inst(Motion.N, 0, Location.THRU)
inst(Motion.W, 0, Location.WMIST)

make_loc(
    Location.WMIST,
    "You are at the west end of the Hall of Mists.  A low wide crawl\n"
    "continues west and another goes north.  To the south is a little\n"
    "passage 6 feet off the floor.",
    "You're at west end of Hall of Mists.",
    0,
)
inst(Motion.S, 0, Location.LIKE1)
ditto(Motion.U)
ditto(Motion.PASSAGE)
ditto(Motion.CLIMB)
inst(Motion.E, 0, Location.WFISS)
inst(Motion.N, 0, Location.DUCK)
inst(Motion.W, 0, Location.ELONG)
ditto(Motion.CRAWL)

ALL_ALIKE = "You are in a maze of twisty little passages, all alike."
DEAD_END = "Dead end."

make_loc(Location.LIKE1, ALL_ALIKE, None, TWIST_HINT)
inst(Motion.U, 0, Location.WMIST)
inst(Motion.N, 0, Location.LIKE1)
inst(Motion.E, 0, Location.LIKE2)
inst(Motion.S, 0, Location.LIKE4)
inst(Motion.W, 0, Location.LIKE11)

make_loc(Location.LIKE2, ALL_ALIKE, None, TWIST_HINT)
inst(Motion.W, 0, Location.LIKE1)
inst(Motion.S, 0, Location.LIKE3)
inst(Motion.E, 0, Location.LIKE4)

make_loc(Location.LIKE3, ALL_ALIKE, None, TWIST_HINT)
inst(Motion.E, 0, Location.LIKE2)
inst(Motion.D, 0, Location.DEAD5)
inst(Motion.S, 0, Location.LIKE6)
inst(Motion.N, 0, Location.DEAD9)

make_loc(Location.LIKE4, ALL_ALIKE, None, TWIST_HINT)
inst(Motion.W, 0, Location.LIKE1)
inst(Motion.N, 0, Location.LIKE2)
inst(Motion.E, 0, Location.DEAD3)
inst(Motion.S, 0, Location.DEAD4)
inst(Motion.U, 0, Location.LIKE14)
ditto(Motion.D)

make_loc(Location.LIKE5, ALL_ALIKE, None, TWIST_HINT)
inst(Motion.E, 0, Location.LIKE6)
inst(Motion.W, 0, Location.LIKE7)

make_loc(Location.LIKE6, ALL_ALIKE, None, TWIST_HINT)
inst(Motion.E, 0, Location.LIKE3)
inst(Motion.W, 0, Location.LIKE5)
inst(Motion.D, 0, Location.LIKE7)
inst(Motion.S, 0, Location.LIKE8)

make_loc(Location.LIKE7, ALL_ALIKE, None, TWIST_HINT)
inst(Motion.W, 0, Location.LIKE5)
inst(Motion.U, 0, Location.LIKE6)
inst(Motion.E, 0, Location.LIKE8)
inst(Motion.S, 0, Location.LIKE9)

make_loc(Location.LIKE8, ALL_ALIKE, None, TWIST_HINT)
inst(Motion.W, 0, Location.LIKE6)
inst(Motion.E, 0, Location.LIKE7)
inst(Motion.S, 0, Location.LIKE8)
inst(Motion.U, 0, Location.LIKE9)
inst(Motion.N, 0, Location.LIKE10)
inst(Motion.D, 0, Location.DEAD11)

make_loc(Location.LIKE9, ALL_ALIKE, None, TWIST_HINT)
inst(Motion.W, 0, Location.LIKE7)
inst(Motion.N, 0, Location.LIKE8)
inst(Motion.S, 0, Location.DEAD6)

make_loc(Location.LIKE10, ALL_ALIKE, None, TWIST_HINT)
inst(Motion.W, 0, Location.LIKE8)
inst(Motion.N, 0, Location.LIKE10)
inst(Motion.D, 0, Location.DEAD7)
inst(Motion.E, 0, Location.BRINK)

make_loc(Location.LIKE11, ALL_ALIKE, None, TWIST_HINT)
inst(Motion.N, 0, Location.LIKE1)
inst(Motion.W, 0, Location.LIKE11)
ditto(Motion.S)
inst(Motion.E, 0, Location.DEAD1)

make_loc(Location.LIKE12, ALL_ALIKE, None, TWIST_HINT)
inst(Motion.S, 0, Location.BRINK)
inst(Motion.E, 0, Location.LIKE13)
inst(Motion.W, 0, Location.DEAD10)

make_loc(Location.LIKE13, ALL_ALIKE, None, TWIST_HINT)
inst(Motion.N, 0, Location.BRINK)
inst(Motion.W, 0, Location.LIKE12)
inst(Motion.NW, 0, Location.DEAD2)

make_loc(Location.LIKE14, ALL_ALIKE, None, TWIST_HINT)
inst(Motion.U, 0, Location.LIKE4)
ditto(Motion.D)

make_loc(
    Location.BRINK,
    "You are on the brink of a thirty-foot pit with a massive orange column\n"
    "down one wall.  You could climb down here but you could not get back\n"
    "up.  The maze continues at this level.",
    "You're at brink of pit.",
    0,
)
inst(Motion.D, 0, Location.BIRD)
ditto(Motion.CLIMB)
inst(Motion.W, 0, Location.LIKE10)
inst(Motion.S, 0, Location.DEAD8)
inst(Motion.N, 0, Location.LIKE12)
inst(Motion.E, 0, Location.LIKE13)

make_loc(
    Location.ELONG,
    "You are at the east end of a very long hall apparently without side\n"
    "chambers.  To the east a low wide crawl slants up.  To the north a\n"
    "round two-foot hole slants down.",
    "You're at east end of long hall.",
    0,
)
inst(Motion.E, 0, Location.WMIST)
ditto(Motion.U)
ditto(Motion.CRAWL)
inst(Motion.W, 0, Location.WLONG)
inst(Motion.N, 0, Location.CROSS)
ditto(Motion.D)
ditto(Motion.HOLE)

make_loc(
    Location.WLONG,
    "You are at the west end of a very long featureless hall.  The hall\n"
    "joins up with a narrow north/south passage.",
    "You're at west end of long hall.",
    0,
)
inst(Motion.E, 0, Location.ELONG)
inst(Motion.N, 0, Location.CROSS)
inst(Motion.S, 100, Location.DIFF0)

TWIST_DESC = [
    "You are in a maze of twisty little passages, all different.",
    "You are in a maze of twisting little passages, all different.",
    "You are in a little maze of twisty passages, all different.",
    "You are in a twisting maze of little passages, all different.",
    "You are in a twisting little maze of passages, all different.",
    "You are in a twisty little maze of passages, all different.",
    "You are in a twisty maze of little passages, all different.",
    "You are in a little twisty maze of passages, all different.",
    "You are in a maze of little twisting passages, all different.",
    "You are in a maze of little twisty passages, all different.",
    "You are in a little maze of twisting passages, all different.",
]


def twist(
    loc: Location,
    desc: str,
    n: Location,
    s: Location,
    e: Location,
    w: Location,
    ne: Location,
    se: Location,
    nw: Location,
    sw: Location,
    u: Location,
    d: Location,
) -> None:
    make_loc(loc, desc, None, 0)
    inst(Motion.N, 0, n)
    inst(Motion.S, 0, s)
    inst(Motion.E, 0, e)
    inst(Motion.W, 0, w)
    inst(Motion.NE, 0, ne)
    inst(Motion.SE, 0, se)
    inst(Motion.NW, 0, nw)
    inst(Motion.SW, 0, sw)
    inst(Motion.U, 0, u)
    inst(Motion.D, 0, d)


twist(
    Location.DIFF0, TWIST_DESC[0],
    Location.DIFF9, Location.DIFF1, Location.DIFF7, Location.DIFF8,
    Location.DIFF3, Location.DIFF4, Location.DIFF6, Location.DIFF2,
    Location.DIFF5, Location.WLONG,
)
twist(
    Location.DIFF1, TWIST_DESC[1],
    Location.DIFF8, Location.DIFF9, Location.DIFF10, Location.DIFF0,
    Location.DIFF5, Location.DIFF2, Location.DIFF3, Location.DIFF4,
    Location.DIFF6, Location.DIFF7,
)
twist(
    Location.DIFF2, TWIST_DESC[2],
    Location.DIFF3, Location.DIFF4, Location.DIFF8, Location.DIFF5,
    Location.DIFF7, Location.DIFF10, Location.DIFF0, Location.DIFF6,
    Location.DIFF1, Location.DIFF9,
)
twist(
    Location.DIFF3, TWIST_DESC[3],
    Location.DIFF7, Location.DIFF10, Location.DIFF6, Location.DIFF2,
    Location.DIFF4, Location.DIFF9, Location.DIFF8, Location.DIFF5,
    Location.DIFF0, Location.DIFF1,
)
twist(
    Location.DIFF4, TWIST_DESC[4],
    Location.DIFF1, Location.DIFF7, Location.DIFF5, Location.DIFF9,
    Location.DIFF0, Location.DIFF3, Location.DIFF2, Location.DIFF10,
    Location.DIFF8, Location.DIFF6,
)
twist(
    Location.DIFF5, TWIST_DESC[5],
    Location.DIFF0, Location.DIFF3, Location.DIFF4, Location.DIFF6,
    Location.DIFF8, Location.DIFF1, Location.DIFF9, Location.DIFF7,
    Location.DIFF10, Location.DIFF2,
)
twist(
    Location.DIFF6, TWIST_DESC[6],
    Location.DIFF10, Location.DIFF5, Location.DIFF0, Location.DIFF1,
    Location.DIFF9, Location.DIFF8, Location.DIFF7, Location.DIFF3,
    Location.DIFF2, Location.DIFF4,
)
twist(
    Location.DIFF7, TWIST_DESC[7],
    Location.DIFF6, Location.DIFF2, Location.DIFF9, Location.DIFF10,
    Location.DIFF1, Location.DIFF0, Location.DIFF5, Location.DIFF8,
    Location.DIFF4, Location.DIFF3,
)
twist(
    Location.DIFF8, TWIST_DESC[8],
    Location.DIFF5, Location.DIFF6, Location.DIFF1, Location.DIFF4,
    Location.DIFF2, Location.DIFF7, Location.DIFF10, Location.DIFF9,
    Location.DIFF3, Location.DIFF0,
)
twist(
    Location.DIFF9, TWIST_DESC[9],
    Location.DIFF4, Location.DIFF8, Location.DIFF2, Location.DIFF3,
    Location.DIFF10, Location.DIFF6, Location.DIFF1, Location.DIFF0,
    Location.DIFF7, Location.DIFF5,
)
twist(
    Location.DIFF10, TWIST_DESC[10],
    Location.DIFF2, Location.PONY, Location.DIFF3, Location.DIFF7,
    Location.DIFF6, Location.DIFF5, Location.DIFF4, Location.DIFF1,
    Location.DIFF9, Location.DIFF8,
)

make_loc(Location.PONY, DEAD_END, None, 0)
inst(Motion.N, 0, Location.DIFF10)
ditto(Motion.OUT)

make_loc(
    Location.CROSS,
    "You are at a crossover of a high N/S passage and a low E/W one.",
    None,
    0,
)
inst(Motion.W, 0, Location.ELONG)
inst(Motion.N, 0, Location.DEAD0)
inst(Motion.E, 0, Location.WEST)
inst(Motion.S, 0, Location.WLONG)

make_loc(
    Location.HMK,
    "You are in the Hall of the Mountain King, with passages off in all\n"
    "directions.",
    "You're in Hall of Mt King.",
    SNAKE_HINT,
)
inst(Motion.STAIRS, 0, Location.EMIST)
ditto(Motion.U)
ditto(Motion.E)
inst(Motion.N, prop_ne(Object.SNAKE, 0), Location.NS)
ditto(Motion.L)
inst(Motion.S, prop_ne(Object.SNAKE, 0), Location.SOUTH)
ditto(Motion.R)
inst(Motion.W, prop_ne(Object.SNAKE, 0), Location.WEST)
ditto(Motion.FORWARD)
inst(Motion.N, 0, Location.SNAKED)
inst(Motion.SW, 35, Location.SECRET)
inst(Motion.SW, sees(Object.SNAKE), Location.SNAKED)
inst(Motion.SECRET, 0, Location.SECRET)

make_loc(
    Location.WEST,
    "You are in the west side chamber of the Hall of the Mountain King.\n"
    "A passage continues west and up here.",
    "You're in west side chamber.",
    0,
)
inst(Motion.HALL, 0, Location.HMK)
ditto(Motion.OUT)
ditto(Motion.E)
inst(Motion.W, 0, Location.CROSS)
ditto(Motion.U)

make_loc(Location.SOUTH, "You are in the south side chamber.", None, 0)
inst(Motion.HALL, 0, Location.HMK)
ditto(Motion.OUT)
ditto(Motion.N)

make_loc(
    Location.NS,
    "You are in a low N/S passage at a hole in the floor.  The hole goes\n"
    "down to an E/W passage.",
    "You're in N/S passage.",
    0,
)
inst(Motion.HALL, 0, Location.HMK)
ditto(Motion.OUT)
ditto(Motion.S)
inst(Motion.N, 0, Location.Y2)
ditto(Motion.Y2)
inst(Motion.D, 0, Location.DIRTY)
ditto(Motion.HOLE)

make_loc(
    Location.Y2,
    "You are in a large room, with a passage to the south, a passage to the\n"
    'west, and a wall of broken rock to the east.  There is a large "Y2" on\n'
    "a rock in the room's center.",
    'You\'re at "Y2".',
    0,
)
inst(Motion.PLUGH, 0, Location.HOUSE)
inst(Motion.S, 0, Location.NS)
inst(Motion.E, 0, Location.JUMBLE)
ditto(Motion.WALL)
ditto(Motion.BROKEN)
inst(Motion.W, 0, Location.WINDOE)
inst(Motion.PLOVER, holds(Object.EMERALD), Location.PDROP)
inst(Motion.PLOVER, 0, Location.PROOM)

make_loc(
    Location.JUMBLE,
    "You are in a jumble of rock, with cracks everywhere.",
    None,
    0,
)
inst(Motion.D, 0, Location.Y2)
ditto(Motion.Y2)
inst(Motion.U, 0, Location.EMIST)

make_loc(
    Location.WINDOE,
    "You're at a low window overlooking a huge pit, which extends up out of\n"
    "sight.  A floor is indistinctly visible over 50 feet below.  Traces of\n"
    "white mist cover the floor of the pit, becoming thicker to the right.\n"
    "Marks in the dust around the window would seem to indicate that\n"
    "someone has been here recently.  Directly across the pit from you and\n"
    "25 feet away there is a similar window looking into a lighted room.\n"
    "A shadowy figure can be seen there peering back at you.",
    "You're at window on pit.",
    0,
)
inst(Motion.E, 0, Location.Y2)
ditto(Motion.Y2)
inst(Motion.JUMP, 0, Location.NECK)

make_loc(
    Location.DIRTY,
    "You are in a dirty broken passage.  To the east is a crawl.  To the\n"
    "west is a large passage.  Above you is a hole to another passage.",
    "You're in dirty passage.",
    0,
)
inst(Motion.E, 0, Location.CLEAN)
ditto(Motion.CRAWL)
inst(Motion.U, 0, Location.NS)
ditto(Motion.HOLE)
inst(Motion.W, 0, Location.DUSTY)
inst(Motion.BEDQUILT, 0, Location.BEDQUILT)

make_loc(
    Location.CLEAN,
    "You are on the brink of a small clean climbable pit.  A crawl leads\n"
    "west.",
    "You're by a clean pit.",
    0,
)
inst(Motion.W, 0, Location.DIRTY)
ditto(Motion.CRAWL)
inst(Motion.D, 0, Location.WET)
ditto(Motion.PIT)
ditto(Motion.CLIMB)

make_loc(
    Location.WET,
    "You are in the bottom of a small pit with a little stream, which\n"
    "enters and exits through tiny slits.",
    "You're in pit by stream.",
    LIQUID,
)
inst(Motion.CLIMB, 0, Location.CLEAN)
ditto(Motion.U)
ditto(Motion.OUT)
inst(Motion.SLIT, 0, SLIT_RMK)
ditto(Motion.STREAM)
ditto(Motion.D)
ditto(Motion.UPSTREAM)
ditto(Motion.DOWNSTREAM)

make_loc(
    Location.DUSTY,
    "You are in a large room full of dusty rocks.  There is a big hole in\n"
    "the floor.  There are cracks everywhere, and a passage leading east.",
    "You're in dusty rock room.",
    0,
)
inst(Motion.E, 0, Location.DIRTY)
ditto(Motion.PASSAGE)
inst(Motion.D, 0, Location.COMPLEX)
ditto(Motion.HOLE)
ditto(Motion.FLOOR)
inst(Motion.BEDQUILT, 0, Location.BEDQUILT)

make_loc(
    Location.COMPLEX,
    "You are at a complex junction.  A low hands-and-knees passage from the\n"
    "north joins a higher crawl from the east to make a walking passage\n"
    "going west.  There is also a large room above.  The air is damp here.",
    "You're at complex junction.",
    0,
)
inst(Motion.U, 0, Location.DUSTY)
ditto(Motion.CLIMB)
ditto(Motion.ROOM)
inst(Motion.W, 0, Location.BEDQUILT)
ditto(Motion.BEDQUILT)
inst(Motion.N, 0, Location.SHELL)
ditto(Motion.SHELL)
inst(Motion.E, 0, Location.ANTE)

make_loc(
    Location.SHELL,
    "You're in a large room carved out of sedimentary rock.  The floor\n"
    "and walls are littered with bits of shells embedded in the stone.\n"
    "A shallow passage proceeds downward, and a somewhat steeper one\n"
    "leads up.  A low hands-and-knees passage enters from the south.",
    "You're in Shell Room.",
    0,
)
inst(Motion.U, 0, Location.ARCH)
ditto(Motion.HALL)
inst(Motion.D, 0, Location.RAGGED)
remark("You can't fit this five-foot clam through that little passage!")
inst(Motion.S, holds(Object.CLAM), sayit())
remark("You can't fit this five-foot oyster through that little passage!")
inst(Motion.S, holds(Object.OYSTER), sayit())
inst(Motion.S, 0, Location.COMPLEX)

make_loc(
    Location.ARCH,
    "You are in an arched hall.  A coral passage once continued up and east\n"
    "from here, but is now blocked by debris.  The air smells of sea water.",
    "You're in arched hall.",
    0,
)
inst(Motion.D, 0, Location.SHELL)
ditto(Motion.SHELL)
ditto(Motion.OUT)

make_loc(
    Location.RAGGED,
    "You are in a long sloping corridor with ragged sharp walls.",
    None,
    0,
)
inst(Motion.U, 0, Location.SHELL)
ditto(Motion.SHELL)
inst(Motion.D, 0, Location.SAC)

make_loc(Location.SAC, "You are in a cul-de-sac about eight feet across.", None, 0)
inst(Motion.U, 0, Location.RAGGED)
ditto(Motion.OUT)
inst(Motion.SHELL, 0, Location.SHELL)

make_loc(
    Location.ANTE,
    "You are in an anteroom leading to a large passage to the east.  Small\n"
    "passages go west and up.  The remnants of recent digging are evident.\n"
    'A sign in midair here says "CAVE UNDER CONSTRUCTION BEYOND THIS POINT.\n'
    'PROCEED AT OWN RISK.  [WITT CONSTRUCTION COMPANY]"',
    "You're in anteroom.",
    0,
)
inst(Motion.U, 0, Location.COMPLEX)
inst(Motion.W, 0, Location.BEDQUILT)
inst(Motion.E, 0, Location.WITT)

make_loc(
    Location.WITT,
    "You are at Witt's End.  Passages lead off in \"all\" directions.",
    "You're at Witt's End.",
    WITT_HINT,
)
remark(
    "You have crawled around in some little holes and wound up back in the\n"
    "main passage."
)
LOOP_RMK = sayit()
inst(Motion.E, 95, LOOP_RMK)
ditto(Motion.N)
ditto(Motion.S)
ditto(Motion.NE)
ditto(Motion.SE)
ditto(Motion.SW)
ditto(Motion.NW)
ditto(Motion.U)
ditto(Motion.D)
inst(Motion.E, 0, Location.ANTE)
remark(
    "You have crawled around in some little holes and found your way\n"
    "blocked by a recent cave-in.  You are now back in the main passage."
)
inst(Motion.W, 0, sayit())

make_loc(
    Location.BEDQUILT,
    "You are in Bedquilt, a long east/west passage with holes everywhere.\n"
    "To explore at random select north, south, up, or down.",
    "You're in Bedquilt.",
    0,
)
inst(Motion.E, 0, Location.COMPLEX)
inst(Motion.W, 0, Location.CHEESE)
inst(Motion.S, 80, LOOP_RMK)
inst(Motion.SLAB, 0, Location.SLAB)
inst(Motion.U, 80, LOOP_RMK)
inst(Motion.U, 50, Location.ABOVEP)
inst(Motion.U, 0, Location.DUSTY)
inst(Motion.N, 60, LOOP_RMK)
inst(Motion.N, 75, Location.LOW)
inst(Motion.N, 0, Location.SJUNC)
inst(Motion.D, 80, LOOP_RMK)
inst(Motion.D, 0, Location.ANTE)

make_loc(
    Location.CHEESE,
    "You are in a room whose walls resemble Swiss cheese.  Obvious passages\n"
    "go west, east, NE, and NW.  Part of the room is occupied by a large\n"
    "bedrock block.",
    "You're in Swiss cheese room.",
    0,
)
inst(Motion.NE, 0, Location.BEDQUILT)
inst(Motion.W, 0, Location.E2PIT)
inst(Motion.S, 80, LOOP_RMK)
inst(Motion.CANYON, 0, Location.TALL)
inst(Motion.E, 0, Location.SOFT)
inst(Motion.NW, 50, LOOP_RMK)
inst(Motion.ORIENTAL, 0, Location.ORIENTAL)

make_loc(
    Location.SOFT,
    "You are in the Soft Room.  The walls are covered with heavy curtains,\n"
    "the floor with a thick pile carpet.  Moss covers the ceiling.",
    "You're in Soft Room.",
    0,
)
inst(Motion.W, 0, Location.CHEESE)
ditto(Motion.OUT)

make_loc(
    Location.E2PIT,
    "You are at the east end of the Twopit Room.  The floor here is\n"
    "littered with thin rock slabs, which make it easy to descend the pits.\n"
    "There is a path here bypassing the pits to connect passages from east\n"
    "and west.  There are holes all over, but the only big one is on the\n"
    "wall directly over the west pit where you can't get to it.",
    "You're at east end of Twopit Room.",
    0,
)
inst(Motion.E, 0, Location.CHEESE)
inst(Motion.W, 0, Location.W2PIT)
ditto(Motion.ACROSS)
inst(Motion.D, 0, Location.EPIT)
ditto(Motion.PIT)

make_loc(
    Location.W2PIT,
    "You are at the west end of the Twopit Room.  There is a large hole in\n"
    "the wall above the pit at this end of the room.",
    "You're at west end of Twopit Room.",
    0,
)
inst(Motion.E, 0, Location.E2PIT)
ditto(Motion.ACROSS)
inst(Motion.W, 0, Location.SLAB)
ditto(Motion.SLAB)
inst(Motion.D, 0, Location.WPIT)
ditto(Motion.PIT)
remark("It is too far up for you to reach.")
inst(Motion.HOLE, 0, sayit())

make_loc(
    Location.EPIT,
    "You are at the bottom of the eastern pit in the Twopit Room.  There is\n"
    "a small pool of oil in one corner of the pit.",
    "You're in east pit.",
    LIQUID + OIL,
)
inst(Motion.U, 0, Location.E2PIT)
ditto(Motion.OUT)

make_loc(
    Location.WPIT,
    "You are at the bottom of the western pit in the Twopit Room.  There is\n"
    "a large hole in the wall about 25 feet above you.",
    "You're in west pit.",
    0,
)
inst(Motion.U, 0, Location.W2PIT)
ditto(Motion.OUT)
inst(Motion.CLIMB, prop_ne(Object.PLANT, 4), Location.CHECK)
inst(Motion.CLIMB, 0, Location.CLIMB)

make_loc(
    Location.NARROW,
    "You are in a long, narrow corridor stretching out of sight to the\n"
    "west.  At the eastern end is a hole through which you can see a\n"
    "profusion of leaves.",
    "You're in narrow corridor.",
    0,
)
inst(Motion.D, 0, Location.WPIT)
ditto(Motion.CLIMB)
ditto(Motion.E)
inst(Motion.JUMP, 0, Location.NECK)
inst(Motion.W, 0, Location.GIANT)
ditto(Motion.GIANT)

make_loc(
    Location.GIANT,
    "You are in the Giant Room.  The ceiling here is too high up for your\n"
    "lamp to show it.  Cavernous passages lead east, north, and south.  On\n"
    'the west wall is scrawled the inscription, "FEE FIE FOE FOO" [sic].',
    "You're in Giant Room.",
    0,
)
inst(Motion.S, 0, Location.NARROW)
inst(Motion.E, 0, Location.BLOCK)
inst(Motion.N, 0, Location.IMMENSE)

make_loc(Location.BLOCK, "The passage here is blocked by a recent cave-in.", None, 0)
inst(Motion.S, 0, Location.GIANT)
ditto(Motion.GIANT)
ditto(Motion.OUT)

make_loc(
    Location.IMMENSE,
    "You are at one end of an immense north/south passage.",
    None,
    0,
)
inst(Motion.S, 0, Location.GIANT)
ditto(Motion.GIANT)
ditto(Motion.PASSAGE)
inst(Motion.N, prop_ne(Object.DOOR, 0), Location.FALLS)
ditto(Motion.ENTER)
ditto(Motion.CAVERN)
remark("The door is extremely rusty and refuses to open.")
inst(Motion.N, 0, sayit())

make_loc(
    Location.FALLS,
    "You are in a magnificent cavern with a rushing stream, which cascades\n"
    "over a sparkling waterfall into a roaring whirlpool that disappears\n"
    "through a hole in the floor.  Passages exit to the south and west.",
    "You're in cavern with waterfall.",
    LIQUID,
)
inst(Motion.S, 0, Location.IMMENSE)
ditto(Motion.OUT)
inst(Motion.GIANT, 0, Location.GIANT)
inst(Motion.W, 0, Location.STEEP)

make_loc(
    Location.STEEP,
    "You are at the top of a steep incline above a large room.  You could\n"
    "climb down here, but you would not be able to climb up.  There is a\n"
    "passage leading back to the north.",
    "You're at steep incline above large room.",
    0,
)
inst(Motion.N, 0, Location.FALLS)
ditto(Motion.CAVERN)
ditto(Motion.PASSAGE)
inst(Motion.D, 0, Location.LOW)
ditto(Motion.CLIMB)

make_loc(
    Location.ABOVEP,
    "You are in a secret N/S canyon above a sizable passage.",
    None,
    0,
)
inst(Motion.N, 0, Location.SJUNC)
inst(Motion.D, 0, Location.BEDQUILT)
ditto(Motion.PASSAGE)
inst(Motion.S, 0, Location.TITE)

make_loc(
    Location.SJUNC,
    "You are in a secret canyon at a junction of three canyons, bearing\n"
    "north, south, and SE.  The north one is as tall as the other two\n"
    "combined.",
    "You're at junction of three secret canyons.",
    0,
)
inst(Motion.SE, 0, Location.BEDQUILT)
inst(Motion.S, 0, Location.ABOVEP)
inst(Motion.N, 0, Location.WINDOW)

make_loc(
    Location.TITE,
    "A large stalactite extends from the roof and almost reaches the floor\n"
    "below.  You could climb down it, and jump from it to the floor, but\n"
    "having done so you would be unable to reach it to climb back up.",
    "You're on top of stalactite.",
    0,
)
inst(Motion.N, 0, Location.ABOVEP)
inst(Motion.D, 40, Location.LIKE6)
ditto(Motion.JUMP)
ditto(Motion.CLIMB)
inst(Motion.D, 50, Location.LIKE9)
inst(Motion.D, 0, Location.LIKE4)

make_loc(
    Location.LOW,
    "You are in a large low room.  Crawls lead north, SE, and SW.",
    None,
    0,
)
inst(Motion.BEDQUILT, 0, Location.BEDQUILT)
inst(Motion.SW, 0, Location.SCORR)
inst(Motion.N, 0, Location.CRAWL)
inst(Motion.SE, 0, Location.ORIENTAL)
ditto(Motion.ORIENTAL)

make_loc(Location.CRAWL, "Dead end crawl.", None, 0)
inst(Motion.S, 0, Location.LOW)
ditto(Motion.CRAWL)
ditto(Motion.OUT)

make_loc(
    Location.WINDOW,
    "You're at a low window overlooking a huge pit, which extends up out of\n"
    "sight.  A floor is indistinctly visible over 50 feet below.  Traces of\n"
    "white mist cover the floor of the pit, becoming thicker to the left.\n"
    "Marks in the dust around the window would seem to indicate that\n"
    "someone has been here recently.  Directly across the pit from you and\n"
    "25 feet away there is a similar window looking into a lighted room.\n"
    "A shadowy figure can be seen there peering back at you.",
    LOCATIONS[int(Location.WINDOE)].short,
    0,
)
inst(Motion.W, 0, Location.SJUNC)
inst(Motion.JUMP, 0, Location.NECK)

make_loc(
    Location.ORIENTAL,
    "This is the Oriental Room.  Ancient oriental cave drawings cover the\n"
    "walls.  A gently sloping passage leads upward to the north, another\n"
    "passage leads SE, and a hands-and-knees crawl leads west.",
    "You're in Oriental Room.",
    0,
)
inst(Motion.SE, 0, Location.CHEESE)
inst(Motion.W, 0, Location.LOW)
ditto(Motion.CRAWL)
inst(Motion.U, 0, Location.MISTY)
ditto(Motion.N)
ditto(Motion.CAVERN)

make_loc(
    Location.MISTY,
    "You are following a wide path around the outer edge of a large cavern.\n"
    "Far below, through a heavy white mist, strange splashing noises can be\n"
    "heard.  The mist rises up through a fissure in the ceiling.  The path\n"
    "exits to the south and west.",
    "You're in misty cavern.",
    0,
)
inst(Motion.S, 0, Location.ORIENTAL)
ditto(Motion.ORIENTAL)
inst(Motion.W, 0, Location.ALCOVE)

make_loc(
    Location.ALCOVE,
    "You are in an alcove.  A small NW path seems to widen after a short\n"
    "distance.  An extremely tight tunnel leads east.  It looks like a very\n"
    "tight squeeze.  An eerie light can be seen at the other end.",
    "You're in alcove.",
    DARK_HINT,
)
inst(Motion.NW, 0, Location.MISTY)
ditto(Motion.CAVERN)
inst(Motion.E, 0, Location.PPASS)
ditto(Motion.PASSAGE)
inst(Motion.E, 0, Location.PROOM)

make_loc(
    Location.PROOM,
    "You're in a small chamber lit by an eerie green light.  An extremely\n"
    "narrow tunnel exits to the west.  A dark corridor leads NE.",
    "You're in Plover Room.",
    LIGHTED + DARK_HINT,
)
inst(Motion.W, 0, Location.PPASS)
ditto(Motion.PASSAGE)
ditto(Motion.OUT)
inst(Motion.W, 0, Location.ALCOVE)
inst(Motion.PLOVER, holds(Object.EMERALD), Location.PDROP)
inst(Motion.PLOVER, 0, Location.Y2)
inst(Motion.NE, 0, Location.DROOM)
ditto(Motion.DARK)

make_loc(
    Location.DROOM,
    "You're in the Dark-Room.  A corridor leading south is the only exit.",
    "You're in Dark-Room.",
    DARK_HINT,
)
inst(Motion.S, 0, Location.PROOM)
ditto(Motion.PLOVER)
ditto(Motion.OUT)

make_loc(
    Location.SLAB,
    "You are in a large low circular chamber whose floor is an immense slab\n"
    "fallen from the ceiling (Slab Room).  There once were large passages\n"
    "to the east and west, but they are now filled with boulders.  Low\n"
    "small passages go north and south, and the south one quickly bends\n"
    "east around the boulders.",
    "You're in Slab Room.",
    0,
)
inst(Motion.S, 0, Location.W2PIT)
inst(Motion.U, 0, Location.ABOVER)
ditto(Motion.CLIMB)
inst(Motion.N, 0, Location.BEDQUILT)

make_loc(
    Location.ABOVER,
    "You are in a secret N/S canyon above a large room.",
    None,
    0,
)
inst(Motion.D, 0, Location.SLAB)
ditto(Motion.SLAB)
inst(Motion.S, prop_ne(Object.DRAGON, 0), Location.SCAN2)
inst(Motion.S, 0, Location.SCAN1)
inst(Motion.N, 0, Location.MIRROR)
inst(Motion.RESERVOIR, 0, Location.RES)

make_loc(
    Location.MIRROR,
    "You are in a north/south canyon about 25 feet across.  The floor is\n"
    "covered by white mist seeping in from the north.  The walls extend\n"
    "upward for well over 100 feet.  Suspended from some unseen point far\n"
    "above you, an enormous two-sided mirror is hanging parallel to and\n"
    "midway between the canyon walls.  (The mirror is obviously provided\n"
    "for the use of the dwarves, who as you know are extremely vain.)\n"
    "A small window can be seen in either wall, some fifty feet up.",
    "You're in mirror canyon.",
    0,
)
inst(Motion.S, 0, Location.ABOVER)
inst(Motion.N, 0, Location.RES)
ditto(Motion.RESERVOIR)

make_loc(
    Location.RES,
    "You are at the edge of a large underground reservoir.  An opaque cloud\n"
    "of white mist fills the room and rises rapidly upward.  The lake is\n"
    "fed by a stream, which tumbles out of a hole in the wall about 10 feet\n"
    "overhead and splashes noisily into the water somewhere within the\n"
    "mist.  The only passage goes back toward the south.",
    "You're at reservoir.",
    LIQUID,
)
inst(Motion.S, 0, Location.MIRROR)
ditto(Motion.OUT)

make_loc(
    Location.SCAN1,
    "You are in a secret canyon that exits to the north and east.",
    None,
    0,
)
inst(Motion.N, 0, Location.ABOVER)
ditto(Motion.OUT)
DRAGON_RMK = remark(
    "The dragon looks rather nasty.  You'd best not try to get by."
)
inst(Motion.E, 0, DRAGON_RMK)
ditto(Motion.FORWARD)

make_loc(Location.SCAN2, LOCATIONS[int(Location.SCAN1)].long, None, 0)
inst(Motion.N, 0, Location.ABOVER)
inst(Motion.E, 0, Location.SECRET)

make_loc(Location.SCAN3, LOCATIONS[int(Location.SCAN1)].long, None, 0)
inst(Motion.E, 0, Location.SECRET)
ditto(Motion.OUT)
inst(Motion.N, 0, DRAGON_RMK)
ditto(Motion.FORWARD)

make_loc(
    Location.SECRET,
    "You are in a secret canyon, which here runs E/W.  It crosses over a\n"
    "very tight canyon 15 feet below.  If you go down you may not be able\n"
    "to get back up.",
    "You're in secret E/W canyon above tight canyon.",
    0,
)
inst(Motion.E, 0, Location.HMK)
inst(Motion.W, prop_ne(Object.DRAGON, 0), Location.SCAN2)
inst(Motion.W, 0, Location.SCAN3)
inst(Motion.D, 0, Location.WIDE)

make_loc(
    Location.WIDE,
    "You are at a wide place in a very tight N/S canyon.",
    None,
    0,
)
inst(Motion.S, 0, Location.TIGHT)
inst(Motion.N, 0, Location.TALL)

make_loc(
    Location.TIGHT,
    "The canyon here becomes too tight to go further south.",
    None,
    0,
)
inst(Motion.N, 0, Location.WIDE)

make_loc(
    Location.TALL,
    "You are in a tall E/W canyon.  A low tight crawl goes 3 feet north and\n"
    "seems to open up.",
    "You're in tall E/W canyon.",
    0,
)
inst(Motion.E, 0, Location.WIDE)
inst(Motion.W, 0, Location.BOULDERS)
inst(Motion.N, 0, Location.CHEESE)
ditto(Motion.CRAWL)

make_loc(
    Location.BOULDERS,
    "The canyon runs into a mass of boulders --- dead end.",
    None,
    0,
)
inst(Motion.S, 0, Location.TALL)

make_loc(
    Location.SCORR,
    "You are in a long winding corridor sloping out of sight in both\n"
    "directions.",
    "You're in sloping corridor.",
    0,
)
inst(Motion.D, 0, Location.LOW)
inst(Motion.U, 0, Location.SWSIDE)

make_loc(
    Location.SWSIDE,
    "You are on one side of a large, deep chasm.  A heavy white mist rising\n"
    "up from below obscures all view of the far side.  A SW path leads away\n"
    "from the chasm into a winding corridor.",
    "You're on SW side of chasm.",
    0,
)
inst(Motion.SW, 0, Location.SCORR)
remark("The troll refuses to let you cross.")
TROLL_RMK = sayit()
inst(Motion.OVER, sees(Object.TROLL), TROLL_RMK)
ditto(Motion.ACROSS)
ditto(Motion.CROSS)
ditto(Motion.NE)
remark("There is no longer any way across the chasm.")
inst(Motion.OVER, prop_ne(Object.BRIDGE, 0), sayit())
inst(Motion.OVER, 0, Location.TROLL)
inst(Motion.JUMP, prop_ne(Object.BRIDGE, 0), Location.LOSE)
inst(Motion.JUMP, 0, BRIDGE_RMK)

make_loc(Location.DEAD0, DEAD_END, None, 0)
inst(Motion.S, 0, Location.CROSS)
ditto(Motion.OUT)

make_loc(Location.DEAD1, DEAD_END, None, TWIST_HINT)
inst(Motion.W, 0, Location.LIKE11)
ditto(Motion.OUT)

make_loc(Location.DEAD2, DEAD_END, None, 0)
inst(Motion.SE, 0, Location.LIKE13)

make_loc(Location.DEAD3, DEAD_END, None, TWIST_HINT)
inst(Motion.W, 0, Location.LIKE4)
ditto(Motion.OUT)

make_loc(Location.DEAD4, DEAD_END, None, TWIST_HINT)
inst(Motion.E, 0, Location.LIKE4)
ditto(Motion.OUT)

make_loc(Location.DEAD5, DEAD_END, None, TWIST_HINT)
inst(Motion.U, 0, Location.LIKE3)
ditto(Motion.OUT)

make_loc(Location.DEAD6, DEAD_END, None, TWIST_HINT)
inst(Motion.W, 0, Location.LIKE9)
ditto(Motion.OUT)

make_loc(Location.DEAD7, DEAD_END, None, TWIST_HINT)
inst(Motion.U, 0, Location.LIKE10)
ditto(Motion.OUT)

make_loc(Location.DEAD8, DEAD_END, None, 0)
inst(Motion.E, 0, Location.BRINK)
ditto(Motion.OUT)

make_loc(Location.DEAD9, DEAD_END, None, TWIST_HINT)
inst(Motion.S, 0, Location.LIKE3)
ditto(Motion.OUT)

make_loc(Location.DEAD10, DEAD_END, None, TWIST_HINT)
inst(Motion.E, 0, Location.LIKE12)
ditto(Motion.OUT)

make_loc(Location.DEAD11, DEAD_END, None, TWIST_HINT)
inst(Motion.U, 0, Location.LIKE8)
ditto(Motion.OUT)

make_loc(
    Location.NESIDE,
    "You are on the far side of the chasm.  A NE path leads away from the\n"
    "chasm on this side.",
    "You're on NE side of chasm.",
    0,
)
inst(Motion.NE, 0, Location.CORR)
inst(Motion.OVER, sees(Object.TROLL), TROLL_RMK)
ditto(Motion.ACROSS)
ditto(Motion.CROSS)
ditto(Motion.SW)
inst(Motion.OVER, 0, Location.TROLL)
inst(Motion.JUMP, 0, BRIDGE_RMK)
inst(Motion.FORK, 0, Location.FORK)
inst(Motion.VIEW, 0, Location.VIEW)
inst(Motion.BARREN, 0, Location.FBARR)

make_loc(
    Location.CORR,
    "You're in a long east/west corridor.  A faint rumbling noise can be\n"
    "heard in the distance.",
    "You're in corridor.",
    0,
)
inst(Motion.W, 0, Location.NESIDE)
inst(Motion.E, 0, Location.FORK)
ditto(Motion.FORK)
inst(Motion.VIEW, 0, Location.VIEW)
inst(Motion.BARREN, 0, Location.FBARR)

make_loc(
    Location.FORK,
    "The path forks here.  The left fork leads northeast.  A dull rumbling\n"
    "seems to get louder in that direction.  The right fork leads southeast\n"
    "down a gentle slope.  The main corridor enters from the west.",
    "You're at fork in path.",
    0,
)
inst(Motion.W, 0, Location.CORR)
inst(Motion.NE, 0, Location.WARM)
ditto(Motion.L)
inst(Motion.SE, 0, Location.LIME)
ditto(Motion.R)
ditto(Motion.D)
inst(Motion.VIEW, 0, Location.VIEW)
inst(Motion.BARREN, 0, Location.FBARR)

make_loc(
    Location.WARM,
    "The walls are quite warm here.  From the north can be heard a steady\n"
    "roar, so loud that the entire cave seems to be trembling.  Another\n"
    "passage leads south, and a low crawl goes east.",
    "You're at junction with warm walls.",
    0,
)
inst(Motion.S, 0, Location.FORK)
ditto(Motion.FORK)
inst(Motion.N, 0, Location.VIEW)
ditto(Motion.VIEW)
inst(Motion.E, 0, Location.CHAMBER)
ditto(Motion.CRAWL)

make_loc(
    Location.VIEW,
    "You are on the edge of a breath-taking view.  Far below you is an\n"
    "active volcano, from which great gouts of molten lava come surging\n"
    "out, cascading back down into the depths.  The glowing rock fills the\n"
    "farthest reaches of the cavern with a blood-red glare, giving every-\n"
    "thing an eerie, macabre appearance.  The air is filled with flickering\n"
    "sparks of ash and a heavy smell of brimstone.  The walls are hot to\n"
    "the touch, and the thundering of the volcano drowns out all other\n"
    "sounds.  Embedded in the jagged roof far overhead are myriad twisted\n"
    "formations, composed of pure white alabaster, which scatter the murky\n"
    "light into sinister apparitions upon the walls.  To one side is a deep\n"
    "gorge, filled with a bizarre chaos of tortured rock that seems to have\n"
    "been crafted by the Devil himself.  An immense river of fire crashes\n"
    "out from the depths of the volcano, burns its way through the gorge,\n"
    "and plummets into a bottomless pit far off to your left.  To the\n"
    "right, an immense geyser of blistering steam erupts continuously\n"
    "from a barren island in the center of a sulfurous lake, which bubbles\n"
    "ominously.  The far right wall is aflame with an incandescence of its\n"
    "own, which lends an additional infernal splendor to the already\n"
    "hellish scene.  A dark, foreboding passage exits to the south.",
    "You're at breath-taking view.",
    LIGHTED,
)
inst(Motion.S, 0, Location.WARM)
ditto(Motion.PASSAGE)
ditto(Motion.OUT)
inst(Motion.FORK, 0, Location.FORK)
remark("Don't be ridiculous!")
inst(Motion.D, 0, sayit())
ditto(Motion.JUMP)

make_loc(
    Location.CHAMBER,
    "You are in a small chamber filled with large boulders.  The walls are\n"
    "very warm, causing the air in the room to be almost stifling from the\n"
    "heat.  The only exit is a crawl heading west, through which a low\n"
    "rumbling noise is coming.",
    "You're in chamber of boulders.",
    0,
)
inst(Motion.W, 0, Location.WARM)
ditto(Motion.OUT)
ditto(Motion.CRAWL)
inst(Motion.FORK, 0, Location.FORK)
inst(Motion.VIEW, 0, Location.VIEW)

make_loc(
    Location.LIME,
    "You are walking along a gently sloping north/south passage lined with\n"
    "oddly shaped limestone formations.",
    "You're in limestone passage.",
    0,
)
inst(Motion.N, 0, Location.FORK)
ditto(Motion.U)
ditto(Motion.FORK)
inst(Motion.S, 0, Location.FBARR)
ditto(Motion.D)
ditto(Motion.BARREN)
inst(Motion.VIEW, 0, Location.VIEW)

make_loc(
    Location.FBARR,
    "You are standing at the entrance to a large, barren room.  A sign\n"
    'posted above the entrance reads:  "CAUTION!  BEAR IN ROOM!"',
    "You're in front of barren room.",
    0,
)
inst(Motion.W, 0, Location.LIME)
ditto(Motion.U)
inst(Motion.FORK, 0, Location.FORK)
inst(Motion.E, 0, Location.BARR)
ditto(Motion.IN)
ditto(Motion.BARREN)
ditto(Motion.ENTER)
inst(Motion.VIEW, 0, Location.VIEW)

make_loc(
    Location.BARR,
    "You are inside a barren room.  The center of the room is completely\n"
    "empty except for some dust.  Marks in the dust lead away toward the\n"
    "far end of the room.  The only exit is the way you came in.",
    "You're in barren room.",
    0,
)
inst(Motion.W, 0, Location.FBARR)
ditto(Motion.OUT)
inst(Motion.FORK, 0, Location.FORK)
inst(Motion.VIEW, 0, Location.VIEW)

make_loc(
    Location.NEEND,
    "You are at the northeast end of an immense room, even larger than the\n"
    "Giant Room.  It appears to be a repository for the \"Adventure\"\n"
    "program.  Massive torches far overhead bathe the room with smoky\n"
    "yellow light.  Scattered about you can be seen a pile of bottles (all\n"
    "of them empty), a nursery of young beanstalks murmuring quietly, a bed\n"
    "of oysters, a bundle of black rods with rusty stars on their ends, and\n"
    "a collection of brass lanterns.  Off to one side a great many dwarves\n"
    "are sleeping on the floor, snoring loudly.  A sign nearby reads:  \"DO\n"
    "NOT DISTURB THE DWARVES!\"  An immense mirror is hanging against one\n"
    "wall, and stretches to the other end of the room, where various other\n"
    "sundry objects can be glimpsed dimly in the distance.",
    "You're at NE end.",
    LIGHTED,
)
inst(Motion.SW, 0, Location.SWEND)

make_loc(
    Location.SWEND,
    "You are at the southwest end of the repository.  To one side is a pit\n"
    "full of fierce green snakes.  On the other side is a row of small\n"
    "wicker cages, each of which contains a little sulking bird.  In one\n"
    "corner is a bundle of black rods with rusty marks on their ends.\n"
    "A large number of velvet pillows are scattered about on the floor.\n"
    "A vast mirror stretches off to the northeast.  At your feet is a\n"
    "large steel grate, next to which is a sign that reads, \"TREASURE\n"
    "VAULT.  KEYS IN MAIN OFFICE.\"",
    "You're at SW end.",
    LIGHTED,
)
inst(Motion.NE, 0, Location.NEEND)
inst(Motion.D, 0, GRATE_RMK)

make_loc(Location.CRACK, "The crack is far too small for you to follow.", None, 0)
inst(FORCE, 0, Location.SPIT)

make_loc(Location.NECK, "You are at the bottom of the pit with a broken neck.", None, 0)
inst(FORCE, 0, Location.LIMBO)

make_loc(Location.LOSE, "You didn't make it.", None, 0)
inst(FORCE, 0, Location.LIMBO)

make_loc(Location.CANT, "The dome is unclimbable.", None, 0)
inst(FORCE, 0, Location.EMIST)

make_loc(
    Location.CLIMB,
    "You clamber up the plant and scurry through the hole at the top.",
    None,
    0,
)
inst(FORCE, 0, Location.NARROW)

make_loc(Location.CHECK, None, None, 0)
inst(FORCE, prop_ne(Object.PLANT, 2), Location.UPNOUT)
inst(FORCE, 0, Location.DIDIT)

make_loc(Location.SNAKED, "You can't get by the snake.", None, 0)
inst(FORCE, 0, Location.HMK)

make_loc(
    Location.THRU,
    "You have crawled through a very low wide passage parallel to and north\n"
    "of the Hall of Mists.",
    None,
    0,
)
inst(FORCE, 0, Location.WMIST)

make_loc(Location.DUCK, LOCATIONS[int(Location.THRU)].long, None, 0)
inst(FORCE, 0, Location.WFISS)

make_loc(
    Location.SEWER,
    "The stream flows out through a pair of 1-foot-diameter sewer pipes.\n"
    "It would be advisable to use the exit.",
    None,
    0,
)
inst(FORCE, 0, Location.HOUSE)

make_loc(
    Location.UPNOUT,
    'There is nothing here to climb.  Use "up" or "out" to leave the pit.',
    None,
    0,
)
inst(FORCE, 0, Location.WPIT)

make_loc(
    Location.DIDIT,
    "You have climbed up the plant and out of the pit.",
    None,
    0,
)
inst(FORCE, 0, Location.W2PIT)

# The travel table ends here; ppass/pdrop/troll are special destinations.
START[int(Location.DIDIT) + 1] = len(TRAVELS)
assert len(TRAVELS) <= TRAVEL_SIZE

# ---------------------------------------------------------------------------
# Object data
# ---------------------------------------------------------------------------

new_obj(Object.RUG_, None, Object.RUG, Location.SCAN3)
new_obj(
    Object.RUG, "Persian rug", Object.RUG, Location.SCAN1,
    "There is a Persian rug spread out on the floor!",
    "The dragon is sprawled out on a Persian rug!!",
)
new_obj(Object.TROLL2_, None, Object.TROLL2, Location.LIMBO)
new_obj(
    Object.TROLL2, None, Object.TROLL2, Location.LIMBO,
    "The troll is nowhere to be seen.",
)
new_obj(Object.TROLL_, None, Object.TROLL, Location.NESIDE)
new_obj(
    Object.TROLL, None, Object.TROLL, Location.SWSIDE,
    "A burly troll stands by the bridge and insists you throw him a\n"
    "treasure before you may cross.",
    "The troll steps out from beneath the bridge and blocks your way.",
    None,
)
new_obj(Object.BRIDGE_, None, Object.BRIDGE, Location.NESIDE)
new_obj(
    Object.BRIDGE, None, Object.BRIDGE, Location.SWSIDE,
    "A rickety wooden bridge extends across the chasm, vanishing into the\n"
    'mist.  A sign posted on the bridge reads, "STOP!  PAY TROLL!"',
    "The wreckage of a bridge (and a dead bear) can be seen at the bottom\n"
    "of the chasm.",
)
new_obj(Object.DRAGON_, None, Object.DRAGON, Location.SCAN3)
new_obj(
    Object.DRAGON, None, Object.DRAGON, Location.SCAN1,
    "A huge green fierce dragon bars the way!",
    "Congratulations!  You have just vanquished a dragon with your bare\n"
    "hands! (Unbelievable, isn't it?)",
    "The body of a huge green dead dragon is lying off to one side.",
)
new_obj(Object.SHADOW_, None, Object.SHADOW, Location.WINDOW)
new_obj(
    Object.SHADOW, None, Object.SHADOW, Location.WINDOE,
    "The shadowy figure seems to be trying to attract your attention.",
)
new_obj(Object.PLANT2_, None, Object.PLANT2, Location.E2PIT)
new_obj(
    Object.PLANT2, None, Object.PLANT2, Location.W2PIT,
    None,
    "The top of a 12-foot-tall beanstalk is poking out of the west pit.",
    "There is a huge beanstalk growing out of the west pit up to the hole.",
)
new_obj(Object.CRYSTAL_, None, Object.CRYSTAL, Location.WFISS)
new_obj(
    Object.CRYSTAL, None, Object.CRYSTAL, Location.EFISS,
    None,
    "A crystal bridge now spans the fissure.",
    "The crystal bridge has vanished!",
)
new_obj(Object.TREADS_, None, Object.TREADS, Location.EMIST)
new_obj(
    Object.TREADS, None, Object.TREADS, Location.SPIT,
    "Rough stone steps lead down the pit.",
    "Rough stone steps lead up the dome.",
)
new_obj(Object.GRATE_, None, Object.GRATE, Location.INSIDE)
new_obj(
    Object.GRATE, None, Object.GRATE, Location.OUTSIDE,
    "The grate is locked.",
    "The grate is open.",
)
new_obj(Object.MIRROR_, None, Object.MIRROR, Location.LIMBO)

new_obj(
    Object.CHAIN, "Golden chain", Object.CHAIN, Location.BARR,
    "There is a golden chain lying in a heap on the floor!",
    "The bear is locked to the wall with a golden chain!",
    "There is a golden chain locked to the wall!",
)
new_obj(
    Object.SPICES, "Rare spices", 0, Location.CHAMBER,
    "There are rare spices here!",
)
new_obj(
    Object.PEARL, "Glistening pearl", 0, Location.LIMBO,
    "Off to one side lies a glistening pearl!",
)
new_obj(
    Object.PYRAMID, "Platinum pyramid", 0, Location.DROOM,
    "There is a platinum pyramid here, 8 inches on a side!",
)
new_obj(
    Object.EMERALD, "Egg-sized emerald", 0, Location.PROOM,
    "There is an emerald here the size of a plover's egg!",
)
new_obj(
    Object.VASE, "Ming vase", 0, Location.ORIENTAL,
    "There is a delicate, precious, Ming vase here!",
    "The vase is now resting, delicately, on a velvet pillow.",
    "The floor is littered with worthless shards of pottery.",
    "The Ming vase drops with a delicate crash.",
)
new_obj(
    Object.TRIDENT, "Jeweled trident", 0, Location.FALLS,
    "There is a jewel-encrusted trident here!",
)
new_obj(
    Object.EGGS, "Golden eggs", 0, Location.GIANT,
    "There is a large nest here, full of golden eggs!",
    "The nest of golden eggs has vanished!",
    "Done!",
)
new_obj(
    Object.CHEST, "Treasure chest", 0, Location.LIMBO,
    "The pirate's treasure chest is here!",
)
new_obj(Object.COINS, "Rare coins", 0, Location.WEST, "There are many coins here!")
new_obj(Object.JEWELS, "Precious jewelry", 0, Location.SOUTH, "There is precious jewelry here!")
new_obj(Object.SILVER, "Bars of silver", 0, Location.NS, "There are bars of silver here!")
new_obj(Object.DIAMONDS, "Several diamonds", 0, Location.WFISS, "There are diamonds here!")
new_obj(
    Object.GOLD, "Large gold nugget", 0, Location.NUGGET,
    "There is a large sparkling nugget of gold here!",
)
new_obj(Object.MOSS, None, Object.MOSS, Location.SOFT, None)
new_obj(
    Object.BATTERIES, "Batteries", 0, Location.LIMBO,
    "There are fresh batteries here.",
    "Some worn-out batteries have been discarded nearby.",
)
new_obj(
    Object.PONY, None, Object.PONY, Location.PONY,
    "There is a massive vending machine here.  The instructions on it read:\n"
    '"Drop coins here to receive fresh batteries."',
)
new_obj(Object.GEYSER, None, Object.GEYSER, Location.VIEW, None)
new_obj(
    Object.MESSAGE, None, Object.MESSAGE, Location.LIMBO,
    "There is a message scrawled in the dust in a flowery script, reading:\n"
    '"This is not the maze where the pirate leaves his treasure chest."',
)
new_obj(
    Object.BEAR, None, Object.BEAR, Location.BARR,
    "There is a ferocious cave bear eying you from the far end of the room!",
    "There is a gentle cave bear sitting placidly in one corner.",
    "There is a contented-looking bear wandering about nearby.",
    None,
)
new_obj(Object.PIRATE, None, Object.PIRATE, Location.LIMBO, None)
new_obj(Object.ART, None, Object.ART, Location.ORIENTAL, None)
new_obj(
    Object.AXE, "Dwarf's axe", 0, Location.LIMBO,
    "There is a little axe here.",
    "There is a little axe lying beside the bear.",
)
new_obj(Object.STALACTITE, None, Object.STALACTITE, Location.TITE, None)
new_obj(
    Object.PLANT, None, Object.PLANT, Location.WPIT,
    'There is a tiny little plant in the pit, murmuring "Water, water, ..."',
    "The plant spurts into furious growth for a few seconds.",
    "There is a 12-foot-tall beanstalk stretching up out of the pit,\n"
    'bellowing "Water!!  Water!!"',
    "The plant grows explosively, almost filling the bottom of the pit.",
    "There is a gigantic beanstalk stretching all the way up to the hole.",
    "You've over-watered the plant!  It's shriveling up!  It's, it's...",
)
new_obj(Object.MIRROR, None, Object.MIRROR, Location.MIRROR, None)
new_obj(Object.OIL, "Oil in the bottle", 0, Location.LIMBO)
new_obj(Object.WATER, "Water in the bottle", 0, Location.LIMBO)
new_obj(
    Object.BOTTLE, "Small bottle", 0, Location.HOUSE,
    "There is a bottle of water here.",
    "There is an empty bottle here.",
    "There is a bottle of oil here.",
)
new_obj(Object.FOOD, "Tasty food", 0, Location.HOUSE, "There is food here.")
new_obj(Object.KNIFE, None, 0, Location.LIMBO)
new_obj(Object.DWARF, None, Object.DWARF, Location.LIMBO)
new_obj(
    Object.MAG, '"Spelunker Today"', 0, Location.ANTE,
    'There are a few recent issues of "Spelunker Today" magazine here.',
)
new_obj(
    Object.OYSTER, "Giant oyster >GROAN!<", 0, Location.LIMBO,
    "There is an enormous oyster here with its shell tightly closed.",
    "Interesting.  There seems to be something written on the underside of\n"
    "the oyster.",
)
new_obj(
    Object.CLAM, "Giant clam >GRUNT!<", 0, Location.SHELL,
    "There is an enormous clam here with its shell tightly closed.",
)
new_obj(
    Object.TABLET, None, Object.TABLET, Location.DROOM,
    "A massive stone tablet embedded in the wall reads:\n"
    '"CONGRATULATIONS ON BRINGING LIGHT INTO THE DARK-ROOM!"',
)
new_obj(
    Object.SNAKE, None, Object.SNAKE, Location.HMK,
    "A huge green fierce snake bars the way!",
    None,
)
new_obj(
    Object.PILLOW, "Velvet pillow", 0, Location.SOFT,
    "A small velvet pillow lies on the floor.",
)
new_obj(
    Object.DOOR, None, Object.DOOR, Location.IMMENSE,
    "The way north is barred by a massive, rusty, iron door.",
    "The way north leads through a massive, rusty, iron door.",
)
new_obj(
    Object.BIRD, "Little bird in cage", 0, Location.BIRD,
    "A cheerful little bird is sitting here singing.",
    "There is a little bird in the cage.",
)
new_obj(
    Object.ROD2, "Black rod", 0, Location.LIMBO,
    "A three-foot black rod with a rusty mark on an end lies nearby.",
)
new_obj(
    Object.ROD, "Black rod", 0, Location.DEBRIS,
    "A three-foot black rod with a rusty star on an end lies nearby.",
)
new_obj(
    Object.CAGE, "Wicker cage", 0, Location.COBBLES,
    "There is a small wicker cage discarded nearby.",
)
new_obj(
    Object.LAMP, "Brass lantern", 0, Location.HOUSE,
    "There is a shiny brass lamp nearby.",
    "There is a lamp shining nearby.",
)
new_obj(
    Object.KEYS, "Set of keys", 0, Location.HOUSE,
    "There are some keys on the ground here.",
)

# ---------------------------------------------------------------------------
# Hints
# ---------------------------------------------------------------------------

HINT_THRESH = [0, 0, 4, 5, 8, 75, 25, 20]
HINT_COST = [5, 10, 2, 2, 2, 4, 5, 3]
HINT_PROMPT = [
    "Welcome to Adventure!!  Would you like instructions?",
    "Hmmm, this looks like a clue, which means it'll cost you 10 points to\n"
    "read it.  Should I go ahead and read it anyway?",
    "Are you trying to get into the cave?",
    "Are you trying to catch the bird?",
    "Are you trying to deal somehow with the snake?",
    "Do you need help getting out of the maze?",
    "Are you trying to explore beyond the Plover Room?",
    "Do you need help getting out of here?",
]
HINT = [
    "Somewhere nearby is Colossal Cave, where others have found fortunes in\n"
    "treasure and gold, though it is rumored that some who enter are never\n"
    "seen again.  Magic is said to work in the cave.  I will be your eyes\n"
    "and hands.  Direct me with commands of one or two words.  I should\n"
    'warn you that I look at only the first five letters of each word, so\n'
    'you\'ll have to enter "NORTHEAST" as "NE" to distinguish it from\n'
    '"NORTH".  Should you get stuck, type "HELP" for some general hints.\n'
    'For information on how to end your adventure, etc., type "INFO".\n'
    "                        -  -  -\n"
    "The first adventure program was developed by Willie Crowther.\n"
    "Most of the features of the current program were added by Don Woods;\n"
    "all of its bugs were added by Don Knuth.",
    'It says, "There is something strange about this place, such that one\n'
    'of the words I\'ve always known now has a new effect."',
    "The grate is very solid and has a hardened steel lock.  You cannot\n"
    "enter without a key, and there are no keys in sight.  I would recommend\n"
    "looking elsewhere for the keys.",
    "Something seems to be frightening the bird just now and you cannot\n"
    "catch it no matter what you try.  Perhaps you might try later.",
    "You can't kill the snake, or drive it away, or avoid it, or anything\n"
    "like that.  There is a way to get by, but you don't have the necessary\n"
    "resources right now.",
    "You can make the passages look less alike by dropping things.",
    "There is a way to explore that region without having to worry about\n"
    "falling into a pit.  None of the objects available is immediately\n"
    "useful for discovering the secret.",
    "Don't go west.",
]

# ---------------------------------------------------------------------------
# Death, ranking
# ---------------------------------------------------------------------------

DEATH_WISHES = [
    "Oh dear, you seem to have gotten yourself killed.  I might be able to\n"
    "help you out, but I've never really done this before.  Do you want me\n"
    "to try to reincarnate you?",
    "All right.  But don't blame me if something goes wr......\n"
    "                 --- POOF!! ---\n"
    "You are engulfed in a cloud of orange smoke.  Coughing and gasping,\n"
    "you emerge from the smoke and find....",
    "You clumsy oaf, you've done it again!  I don't know how long I can\n"
    "keep this up.  Do you want me to try reincarnating you again?",
    "Okay, now where did I put my resurrection kit?....  >POOF!<\n"
    "Everything disappears in a dense cloud of orange smoke.",
    "Now you've really done it!  I'm out of orange smoke!  You don't expect\n"
    "me to do a decent reincarnation without any orange smoke, do you?",
    "Okay, if you're so smart, do it yourself!  I'm leaving!",
]

CLASS_SCORE = [35, 100, 130, 200, 250, 300, 330, 349, 9999]
CLASS_MESSAGE = [
    "You are obviously a rank amateur.  Better luck next time.",
    "Your score qualifies you as a novice class adventurer.",
    'You have achieved the rating "Experienced Adventurer".',
    'You may now consider yourself a "Seasoned Adventurer".',
    'You have reached "Junior Master" status.',
    "Your score puts you in Master Adventurer Class C.",
    "Your score puts you in Master Adventurer Class B.",
    "Your score puts you in Master Adventurer Class A.",
    "All of Adventuredom gives tribute to you, Adventure Grandmaster!",
]
HIGHEST_CLASS = 8

# Dwarves and the pirate.
ND = 5
INITIAL_DLOC = [
    Location.DEAD2,     # the pirate
    Location.HMK,
    Location.WFISS,
    Location.Y2,
    Location.LIKE3,
    Location.COMPLEX,
]

INITIAL_KNIFE_LOC = Location.LIMBO
INITIAL_PANIC = False
INITIAL_CLOSED = False
