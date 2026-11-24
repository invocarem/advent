"""Vocabulary for the Adventure port.

This module is a transcription of the vocabulary section of ``advent.w``:
the word types, the meanings of motion/object/action words, the word table
itself, the fixed messages, and the per-action default messages.

Only the first five letters of a word are significant, exactly as in the
original, so the table is keyed by ``word[:5]``.
"""

from __future__ import annotations

from enum import IntEnum

# ---------------------------------------------------------------------------
# Word types
# ---------------------------------------------------------------------------


class WordType(IntEnum):
    NO_TYPE = 0
    MOTION = 1
    OBJECT = 2
    ACTION = 3
    MESSAGE = 4


# ---------------------------------------------------------------------------
# Motions
# ---------------------------------------------------------------------------


class Motion(IntEnum):
    N = 0
    S = 1
    E = 2
    W = 3
    NE = 4
    SE = 5
    NW = 6
    SW = 7
    U = 8
    D = 9
    L = 10
    R = 11
    IN = 12
    OUT = 13
    FORWARD = 14
    BACK = 15
    OVER = 16
    ACROSS = 17
    UPSTREAM = 18
    DOWNSTREAM = 19
    ENTER = 20
    CRAWL = 21
    JUMP = 22
    CLIMB = 23
    LOOK = 24
    CROSS = 25
    ROAD = 26
    WOODS = 27
    VALLEY = 28
    HOUSE = 29
    GULLY = 30
    STREAM = 31
    DEPRESSION = 32
    ENTRANCE = 33
    CAVE = 34
    ROCK = 35
    SLAB = 36
    BED = 37
    PASSAGE = 38
    CAVERN = 39
    CANYON = 40
    AWKWARD = 41
    SECRET = 42
    BEDQUILT = 43
    RESERVOIR = 44
    GIANT = 45
    ORIENTAL = 46
    SHELL = 47
    BARREN = 48
    BROKEN = 49
    DEBRIS = 50
    VIEW = 51
    FORK = 52
    PIT = 53
    SLIT = 54
    CRACK = 55
    DOME = 56
    HOLE = 57
    WALL = 58
    HALL = 59
    ROOM = 60
    FLOOR = 61
    STAIRS = 62
    STEPS = 63
    COBBLES = 64
    SURFACE = 65
    DARK = 66
    LOW = 67
    OUTDOORS = 68
    Y2 = 69
    XYZZY = 70
    PLUGH = 71
    PLOVER = 72
    OFFICE = 73
    NOWHERE = 74


# ---------------------------------------------------------------------------
# Objects
# ---------------------------------------------------------------------------


class Object(IntEnum):
    NOTHING = 0
    KEYS = 1
    LAMP = 2
    GRATE = 3
    GRATE_ = 4
    CAGE = 5
    ROD = 6
    ROD2 = 7
    TREADS = 8
    TREADS_ = 9
    BIRD = 10
    DOOR = 11
    PILLOW = 12
    SNAKE = 13
    CRYSTAL = 14
    CRYSTAL_ = 15
    TABLET = 16
    CLAM = 17
    OYSTER = 18
    MAG = 19
    DWARF = 20
    KNIFE = 21
    FOOD = 22
    BOTTLE = 23
    WATER = 24
    OIL = 25
    MIRROR = 26
    MIRROR_ = 27
    PLANT = 28
    PLANT2 = 29
    PLANT2_ = 30
    STALACTITE = 31
    SHADOW = 32
    SHADOW_ = 33
    AXE = 34
    ART = 35
    PIRATE = 36
    DRAGON = 37
    DRAGON_ = 38
    BRIDGE = 39
    BRIDGE_ = 40
    TROLL = 41
    TROLL_ = 42
    TROLL2 = 43
    TROLL2_ = 44
    BEAR = 45
    MESSAGE = 46
    GEYSER = 47
    PONY = 48
    BATTERIES = 49
    MOSS = 50
    GOLD = 51
    DIAMONDS = 52
    SILVER = 53
    JEWELS = 54
    COINS = 55
    CHEST = 56
    EGGS = 57
    TRIDENT = 58
    VASE = 59
    EMERALD = 60
    PYRAMID = 61
    PEARL = 62
    RUG = 63
    RUG_ = 64
    SPICES = 65
    CHAIN = 66


MIN_TREASURE = Object.GOLD
MAX_OBJ = Object.CHAIN


# ---------------------------------------------------------------------------
# Actions
# ---------------------------------------------------------------------------


class Action(IntEnum):
    ABSTAIN = 0
    TAKE = 1
    DROP = 2
    OPEN = 3
    CLOSE = 4
    ON = 5
    OFF = 6
    WAVE = 7
    CALM = 8
    GO = 9
    RELAX = 10
    POUR = 11
    EAT = 12
    DRINK = 13
    RUB = 14
    TOSS = 15
    WAKE = 16
    FEED = 17
    FILL = 18
    BREAK = 19
    BLAST = 20
    KILL = 21
    SAY = 22
    READ = 23
    FEEFIE = 24
    BRIEF = 25
    FIND = 26
    INVENTORY = 27
    SCORE = 28
    QUIT = 29


# ---------------------------------------------------------------------------
# Locations
# ---------------------------------------------------------------------------

_LOCATION_NAMES = [
    "INHAND",
    "LIMBO",
    "ROAD",
    "HILL",
    "HOUSE",
    "VALLEY",
    "FOREST",
    "WOODS",
    "SLIT",
    "OUTSIDE",
    "INSIDE",
    "COBBLES",
    "DEBRIS",
    "AWK",
    "BIRD",
    "SPIT",
    "EMIST",
    "NUGGET",
    "EFISS",
    "WFISS",
    "WMIST",
    *[f"LIKE{i}" for i in range(1, 15)],
    "BRINK",
    "ELONG",
    "WLONG",
    *[f"DIFF{i}" for i in range(11)],
    "PONY",
    "CROSS",
    "HMK",
    "WEST",
    "SOUTH",
    "NS",
    "Y2",
    "JUMBLE",
    "WINDOE",
    "DIRTY",
    "CLEAN",
    "WET",
    "DUSTY",
    "COMPLEX",
    "SHELL",
    "ARCH",
    "RAGGED",
    "SAC",
    "ANTE",
    "WITT",
    "BEDQUILT",
    "CHEESE",
    "SOFT",
    "E2PIT",
    "W2PIT",
    "EPIT",
    "WPIT",
    "NARROW",
    "GIANT",
    "BLOCK",
    "IMMENSE",
    "FALLS",
    "STEEP",
    "ABOVEP",
    "SJUNC",
    "TITE",
    "LOW",
    "CRAWL",
    "WINDOW",
    "ORIENTAL",
    "MISTY",
    "ALCOVE",
    "PROOM",
    "DROOM",
    "SLAB",
    "ABOVER",
    "MIRROR",
    "RES",
    "SCAN1",
    "SCAN2",
    "SCAN3",
    "SECRET",
    "WIDE",
    "TIGHT",
    "TALL",
    "BOULDERS",
    "SCORR",
    "SWSIDE",
    *[f"DEAD{i}" for i in range(12)],
    "NESIDE",
    "CORR",
    "FORK",
    "WARM",
    "VIEW",
    "CHAMBER",
    "LIME",
    "FBARR",
    "BARR",
    "NEEND",
    "SWEND",
    "CRACK",
    "NECK",
    "LOSE",
    "CANT",
    "CLIMB",
    "CHECK",
    "SNAKED",
    "THRU",
    "DUCK",
    "SEWER",
    "UPNOUT",
    "DIDIT",
    "PPASS",
    "PDROP",
    "TROLL",
]

Location = IntEnum("Location", {name: i - 1 for i, name in enumerate(_LOCATION_NAMES)})

INHAND = Location.INHAND
LIMBO = Location.LIMBO
MIN_IN_CAVE = Location.INSIDE
MIN_LOWER_LOC = Location.EMIST
MIN_FORCED_LOC = Location.CRACK
MAX_LOC = Location.DIDIT
MAX_SPEC = Location.TROLL
MAX_PIRATE_LOC = Location.DEAD2


# ---------------------------------------------------------------------------
# Location flags (bits of flags[loc])
# ---------------------------------------------------------------------------

LIGHTED = 1
OIL = 2
LIQUID = 4
CAVE_HINT = 8
BIRD_HINT = 16
SNAKE_HINT = 32
TWIST_HINT = 64
DARK_HINT = 128
WITT_HINT = 256


# ---------------------------------------------------------------------------
# The word table
# ---------------------------------------------------------------------------

_WORDS: list[tuple[str, WordType, int]] = []


def _w(word: str, wtype: WordType, meaning: int) -> None:
    _WORDS.append((word, wtype, meaning))


def _build_motions() -> None:
    for word, meaning in (
        ("north", Motion.N),
        ("n", Motion.N),
        ("south", Motion.S),
        ("s", Motion.S),
        ("east", Motion.E),
        ("e", Motion.E),
        ("west", Motion.W),
        ("w", Motion.W),
        ("ne", Motion.NE),
        ("se", Motion.SE),
        ("nw", Motion.NW),
        ("sw", Motion.SW),
        ("upwar", Motion.U),
        ("up", Motion.U),
        ("u", Motion.U),
        ("above", Motion.U),
        ("ascen", Motion.U),
        ("downw", Motion.D),
        ("down", Motion.D),
        ("d", Motion.D),
        ("desce", Motion.D),
        ("left", Motion.L),
        ("right", Motion.R),
        ("inwar", Motion.IN),
        ("insid", Motion.IN),
        ("in", Motion.IN),
        ("out", Motion.OUT),
        ("outsi", Motion.OUT),
        ("exit", Motion.OUT),
        ("leave", Motion.OUT),
        ("forwa", Motion.FORWARD),
        ("conti", Motion.FORWARD),
        ("onwar", Motion.FORWARD),
        ("back", Motion.BACK),
        ("retur", Motion.BACK),
        ("retre", Motion.BACK),
        ("over", Motion.OVER),
        ("acros", Motion.ACROSS),
        ("upstr", Motion.UPSTREAM),
        ("downs", Motion.DOWNSTREAM),
        ("enter", Motion.ENTER),
        ("crawl", Motion.CRAWL),
        ("jump", Motion.JUMP),
        ("climb", Motion.CLIMB),
        ("look", Motion.LOOK),
        ("exami", Motion.LOOK),
        ("touch", Motion.LOOK),
        ("descr", Motion.LOOK),
        ("cross", Motion.CROSS),
        ("road", Motion.ROAD),
        ("hill", Motion.ROAD),
        ("fores", Motion.WOODS),
        ("valle", Motion.VALLEY),
        ("build", Motion.HOUSE),
        ("house", Motion.HOUSE),
        ("gully", Motion.GULLY),
        ("strea", Motion.STREAM),
        ("depre", Motion.DEPRESSION),
        ("entra", Motion.ENTRANCE),
        ("cave", Motion.CAVE),
        ("rock", Motion.ROCK),
        ("slab", Motion.SLAB),
        ("slabr", Motion.SLAB),
        ("bed", Motion.BED),
        ("passa", Motion.PASSAGE),
        ("tunne", Motion.PASSAGE),
        ("caver", Motion.CAVERN),
        ("canyo", Motion.CANYON),
        ("awkwa", Motion.AWKWARD),
        ("secre", Motion.SECRET),
        ("bedqu", Motion.BEDQUILT),
        ("reser", Motion.RESERVOIR),
        ("giant", Motion.GIANT),
        ("orien", Motion.ORIENTAL),
        ("shell", Motion.SHELL),
        ("barre", Motion.BARREN),
        ("broke", Motion.BROKEN),
        ("debri", Motion.DEBRIS),
        ("view", Motion.VIEW),
        ("fork", Motion.FORK),
        ("pit", Motion.PIT),
        ("slit", Motion.SLIT),
        ("crack", Motion.CRACK),
        ("dome", Motion.DOME),
        ("hole", Motion.HOLE),
        ("wall", Motion.WALL),
        ("hall", Motion.HALL),
        ("room", Motion.ROOM),
        ("floor", Motion.FLOOR),
        ("stair", Motion.STAIRS),
        ("steps", Motion.STEPS),
        ("cobbl", Motion.COBBLES),
        ("surfa", Motion.SURFACE),
        ("dark", Motion.DARK),
        ("low", Motion.LOW),
        ("outdo", Motion.OUTDOORS),
        ("y2", Motion.Y2),
        ("xyzzy", Motion.XYZZY),
        ("plugh", Motion.PLUGH),
        ("plove", Motion.PLOVER),
        ("main", Motion.OFFICE),
        ("offic", Motion.OFFICE),
        ("null", Motion.NOWHERE),
        ("nowhe", Motion.NOWHERE),
    ):
        _w(word, WordType.MOTION, meaning)


def _build_objects() -> None:
    for word, meaning in (
        ("key", Object.KEYS),
        ("keys", Object.KEYS),
        ("lamp", Object.LAMP),
        ("lante", Object.LAMP),
        ("headl", Object.LAMP),
        ("grate", Object.GRATE),
        ("cage", Object.CAGE),
        ("rod", Object.ROD),
        ("bird", Object.BIRD),
        ("door", Object.DOOR),
        ("pillo", Object.PILLOW),
        ("velve", Object.PILLOW),
        ("snake", Object.SNAKE),
        ("fissu", Object.CRYSTAL),
        ("table", Object.TABLET),
        ("clam", Object.CLAM),
        ("oyste", Object.OYSTER),
        ("magaz", Object.MAG),
        ("issue", Object.MAG),
        ("spelu", Object.MAG),
        ('"spel', Object.MAG),
        ("dwarf", Object.DWARF),
        ("dwarv", Object.DWARF),
        ("knife", Object.KNIFE),
        ("knive", Object.KNIFE),
        ("food", Object.FOOD),
        ("ratio", Object.FOOD),
        ("bottl", Object.BOTTLE),
        ("jar", Object.BOTTLE),
        ("water", Object.WATER),
        ("h2o", Object.WATER),
        ("oil", Object.OIL),
        ("mirro", Object.MIRROR),
        ("plant", Object.PLANT),
        ("beans", Object.PLANT),
        ("stala", Object.STALACTITE),
        ("shado", Object.SHADOW),
        ("figur", Object.SHADOW),
        ("axe", Object.AXE),
        ("drawi", Object.ART),
        ("pirat", Object.PIRATE),
        ("drago", Object.DRAGON),
        ("chasm", Object.BRIDGE),
        ("troll", Object.TROLL),
        ("bear", Object.BEAR),
        ("messa", Object.MESSAGE),
        ("volca", Object.GEYSER),
        ("geyse", Object.GEYSER),
        ("vendi", Object.PONY),
        ("machi", Object.PONY),
        ("batte", Object.BATTERIES),
        ("moss", Object.MOSS),
        ("carpe", Object.MOSS),
        ("gold", Object.GOLD),
        ("nugge", Object.GOLD),
        ("diamo", Object.DIAMONDS),
        ("silve", Object.SILVER),
        ("bars", Object.SILVER),
        ("jewel", Object.JEWELS),
        ("coins", Object.COINS),
        ("chest", Object.CHEST),
        ("box", Object.CHEST),
        ("treas", Object.CHEST),
        ("eggs", Object.EGGS),
        ("egg", Object.EGGS),
        ("nest", Object.EGGS),
        ("tride", Object.TRIDENT),
        ("ming", Object.VASE),
        ("vase", Object.VASE),
        ("shard", Object.VASE),
        ("potte", Object.VASE),
        ("emera", Object.EMERALD),
        ("plati", Object.PYRAMID),
        ("pyram", Object.PYRAMID),
        ("pearl", Object.PEARL),
        ("persi", Object.RUG),
        ("rug", Object.RUG),
        ("spice", Object.SPICES),
        ("chain", Object.CHAIN),
    ):
        _w(word, WordType.OBJECT, meaning)


def _build_actions() -> None:
    for word, meaning in (
        ("take", Action.TAKE),
        ("carry", Action.TAKE),
        ("keep", Action.TAKE),
        ("catch", Action.TAKE),
        ("captu", Action.TAKE),
        ("steal", Action.TAKE),
        ("get", Action.TAKE),
        ("tote", Action.TAKE),
        ("drop", Action.DROP),
        ("relea", Action.DROP),
        ("free", Action.DROP),
        ("disca", Action.DROP),
        ("dump", Action.DROP),
        ("open", Action.OPEN),
        ("unloc", Action.OPEN),
        ("close", Action.CLOSE),
        ("lock", Action.CLOSE),
        ("light", Action.ON),
        ("on", Action.ON),
        ("extin", Action.OFF),
        ("off", Action.OFF),
        ("wave", Action.WAVE),
        ("shake", Action.WAVE),
        ("swing", Action.WAVE),
        ("calm", Action.CALM),
        ("placa", Action.CALM),
        ("tame", Action.CALM),
        ("walk", Action.GO),
        ("run", Action.GO),
        ("trave", Action.GO),
        ("go", Action.GO),
        ("proce", Action.GO),
        ("explo", Action.GO),
        ("goto", Action.GO),
        ("follo", Action.GO),
        ("turn", Action.GO),
        ("nothi", Action.RELAX),
        ("pour", Action.POUR),
        ("eat", Action.EAT),
        ("devou", Action.EAT),
        ("drink", Action.DRINK),
        ("rub", Action.RUB),
        ("throw", Action.TOSS),
        ("toss", Action.TOSS),
        ("wake", Action.WAKE),
        ("distu", Action.WAKE),
        ("feed", Action.FEED),
        ("fill", Action.FILL),
        ("break", Action.BREAK),
        ("smash", Action.BREAK),
        ("shatt", Action.BREAK),
        ("blast", Action.BLAST),
        ("deton", Action.BLAST),
        ("ignit", Action.BLAST),
        ("blowu", Action.BLAST),
        ("attac", Action.KILL),
        ("kill", Action.KILL),
        ("fight", Action.KILL),
        ("hit", Action.KILL),
        ("strik", Action.KILL),
        ("slay", Action.KILL),
        ("say", Action.SAY),
        ("chant", Action.SAY),
        ("sing", Action.SAY),
        ("utter", Action.SAY),
        ("mumbl", Action.SAY),
        ("read", Action.READ),
        ("perus", Action.READ),
        ("fee", Action.FEEFIE),
        ("fie", Action.FEEFIE),
        ("foe", Action.FEEFIE),
        ("foo", Action.FEEFIE),
        ("fum", Action.FEEFIE),
        ("brief", Action.BRIEF),
        ("find", Action.FIND),
        ("where", Action.FIND),
        ("inven", Action.INVENTORY),
        ("score", Action.SCORE),
        ("quit", Action.QUIT),
    ):
        _w(word, WordType.ACTION, meaning)


# The fixed messages, in the order of the C ``message[]`` array.
MESSAGES: list[str] = [
    "Good try, but that is an old worn-out magic word.",
    "I know of places, actions, and things.  Most of my vocabulary\n"
    "describes places and is used to move you there.  To move, try words\n"
    "like forest, building, downstream, enter, east, west, north, south,\n"
    "up, or down.  I know about a few special objects, like a black rod\n"
    "hidden in the cave.  These objects can be manipulated using some of\n"
    "the action words that I know.  Usually you will need to give both the\n"
    "object and action words (in either order), but sometimes I can infer\n"
    "the object from the verb alone.  Some objects also imply verbs; in\n"
    'particular, "inventory" implies "take inventory", which causes me to\n'
    "give you a list of what you're carrying.  The objects have side\n"
    "effects; for instance, the rod scares the bird.  Usually people having\n"
    "trouble moving just need to try a few more words.  Usually people\n"
    "trying unsuccessfully to manipulate an object are attempting something\n"
    "beyond their (or my!) capabilities and should try a completely\n"
    "different tack.  To speed the game you can sometimes move long\n"
    "distances with a single word.  For example, \"building\" usually gets\n"
    "you to the building from anywhere above ground except when lost in the\n"
    "forest.  Also, note that cave passages turn a lot, and that leaving a\n"
    "room to the north does not guarantee entering the next from the south.\n"
    "Good luck!",
    "The trees of the forest are large hardwood oak and maple, with an\n"
    "occasional grove of pine or spruce.  There is quite a bit of under-\n"
    "growth, largely birch and ash saplings plus nondescript bushes of\n"
    "various sorts.  This time of year visibility is quite restricted by\n"
    "all the leaves, but travel is quite easy if you detour around the\n"
    "spruce and berry bushes.",
    "Digging without a shovel is quite impractical.  Even with a shovel\n"
    "progress is unlikely.",
    "I'm as confused as you are.",
    "There is a loud explosion and you are suddenly splashed across the\n"
    "walls of the room.",
    "There is a loud explosion and a twenty-foot hole appears in the far\n"
    "wall, burying the snakes in the rubble.  A river of molten lava pours\n"
    "in through the hole, destroying everything in its path, including you!",
    "Mist is a white vapor, usually water, seen from time to time in\n"
    "caverns.  It can be found anywhere but is frequently a sign of a deep\n"
    "pit leading down to water.",
    "Watch it!",
    "There is a loud explosion, and a twenty-foot hole appears in the far\n"
    "wall, burying the dwarves in the rubble.  You march through the hole\n"
    "and find yourself in the main office, where a cheering band of\n"
    "friendly elves carry the conquering adventurer off into the sunset.",
    'I don\'t know the word "stop".  Use "quit" if you want to give up.',
    "If you want to end your adventure early, say \"quit\".  To get full\n"
    "credit for a treasure, you must have left it safely in the building,\n"
    "though you get partial credit just for locating it.  You lose points\n"
    "for getting killed, or for quitting, though the former costs you more.\n"
    "There are also points based on how much (if any) of the cave you've\n"
    "managed to explore; in particular, there is a large bonus just for\n"
    "getting in (to distinguish the beginners from the rest of the pack),\n"
    "and there are other ways to determine whether you've been through some\n"
    "of the more harrowing sections.  If you think you've found all the\n"
    "treasures, just keep exploring for a while.  If nothing interesting\n"
    "happens, you haven't found them all yet.  If something interesting\n"
    "DOES happen, it means you're getting a bonus and have an opportunity\n"
    "to garner many more points in the master's section.\n"
    "I may occasionally offer hints if you seem to be having trouble.\n"
    "If I do, I'll warn you in advance how much it will affect your score\n"
    "to accept the hints.  Finally, to save paper, you may specify \"brief\",\n"
    "which tells me never to repeat the full description of a place\n"
    "unless you explicitly ask me to.",
    "I don't know how.",
]

MESSAGE_WORDS: list[tuple[str, int]] = [
    ("abra", 0),
    ("abrac", 0),
    ("opens", 0),
    ("sesam", 0),
    ("shaza", 0),
    ("hocus", 0),
    ("pocus", 0),
    ("help", 1),
    ("?", 1),
    ("tree", 2),
    ("trees", 2),
    ("dig", 3),
    ("excav", 3),
    ("lost", 4),
    ("mist", 7),
    ("fuck", 8),
    ("stop", 10),
    ("info", 11),
    ("infor", 11),
    ("swim", 12),
]


def _build_messages() -> None:
    for word, index in MESSAGE_WORDS:
        _w(word, WordType.MESSAGE, index)


_build_motions()
_build_objects()
_build_actions()
_build_messages()

WORDS: dict[str, tuple[WordType, int]] = {}
for _word, _type, _meaning in _WORDS:
    WORDS.setdefault(_word[:5], (_type, _meaning))


def lookup(word: str) -> tuple[WordType, int] | None:
    """Return (type, meaning) for a word, or None if unknown.

    The original truncates the word to five characters and compares five
    characters, so ``northeast`` is ``north``.
    """
    return WORDS.get(word[:5].lower())


# ---------------------------------------------------------------------------
# Default messages for actions
# ---------------------------------------------------------------------------

_DRINK_STREAM = (
    "You have taken a drink from the stream.  The water tastes strongly of\n"
    "minerals, but is not unpleasant.  It is extremely cold."
)

DEFAULT_MSG: dict[Action, str] = {
    Action.TAKE: "You are already carrying it!",
    Action.DROP: "You aren't carrying it!",
    Action.OPEN: "I don't know how to lock or unlock such a thing.",
    Action.ON: "You have no source of light.",
    Action.WAVE: "Nothing happens.",
    Action.CALM: "I'm game.  Would you care to explain how?",
    Action.GO: "Where?",
    Action.RELAX: "OK.",
    Action.EAT: "Don't be ridiculous!",
    Action.DRINK: _DRINK_STREAM,
    Action.RUB: (
        "Rubbing the electric lamp is not particularly rewarding.  Anyway,\n"
        "nothing exciting happens."
    ),
    Action.FEED: "There is nothing here to eat.",
    Action.FILL: "You can't fill that.",
    Action.BREAK: "It is beyond your power to do that.",
    Action.BLAST: "Blasting requires dynamite.",
    Action.READ: "I'm afraid I don't understand.",
    Action.FEEFIE: "I don't know how.",
    Action.BRIEF: "On what?",
    Action.FIND: (
        "I can only tell you what you see as you move about and manipulate\n"
        "things.  I cannot tell you where remote things are."
    ),
    Action.SCORE: "Eh?",
}

# Actions whose default is an alias of another action's default.
DEFAULT_MSG[Action.CLOSE] = DEFAULT_MSG[Action.OPEN]
DEFAULT_MSG[Action.OFF] = DEFAULT_MSG[Action.ON]
DEFAULT_MSG[Action.POUR] = DEFAULT_MSG[Action.DROP]
DEFAULT_MSG[Action.TOSS] = DEFAULT_MSG[Action.DROP]
DEFAULT_MSG[Action.WAKE] = DEFAULT_MSG[Action.EAT]
DEFAULT_MSG[Action.KILL] = DEFAULT_MSG[Action.EAT]
DEFAULT_MSG[Action.INVENTORY] = DEFAULT_MSG[Action.FIND]
DEFAULT_MSG[Action.QUIT] = DEFAULT_MSG[Action.SCORE]

# The C code uses ``ok`` for the default of RELAX in yes/no answers.
OK = DEFAULT_MSG[Action.RELAX]
