"""Scene descriptions for the graphical front end.

This module is pure data and small helpers: it says *what* a place looks like
(which backdrop, which painted props, which palette) and *what to call* every
object and exit.  It never imports tkinter and never touches the engine, so the
scene table can be tested headlessly and reused by another renderer.

The coordinates in :class:`Prop` are fractions of the logical canvas
(``0..1`` across and down); the painters in :mod:`advent.art` turn them into
vector shapes.  Nothing here changes the game: the engine's text is still the
source of truth, and every message it prints appears in the narration pane.
"""

from __future__ import annotations

from dataclasses import dataclass

from . import data as D
from .vocabulary import Location, Motion, Object


@dataclass(frozen=True)
class Prop:
    """One painted decoration in a scene."""

    kind: str
    x: float
    y: float
    scale: float = 1.0
    flip: bool = False


@dataclass(frozen=True)
class Scene:
    """The picture for one location."""

    backdrop: str
    props: tuple[Prop, ...] = ()
    palette: str = "cave"
    seed: int = 0


def _scene(
    backdrop: str,
    *props: Prop,
    palette: str = "cave",
    seed: int = 0,
) -> Scene:
    return Scene(backdrop, tuple(props), palette, seed)


def _p(kind: str, x: float, y: float, scale: float = 1.0, flip: bool = False) -> Prop:
    return Prop(kind, x, y, scale, flip)


# ---------------------------------------------------------------------------
# The picture for every location
# ---------------------------------------------------------------------------

SCENES: dict[int, Scene] = {
    # -- above ground ------------------------------------------------------
    int(Location.ROAD): _scene(
        "road",
        _p("house", 0.64, 0.64, 1.0),
        _p("stream", 0.86, 0.87, 0.7),
        _p("trees", 0.12, 0.58, 0.9),
        palette="surface",
        seed=1,
    ),
    int(Location.HILL): _scene(
        "hill",
        _p("house_far", 0.79, 0.57, 0.7),
        _p("trees", 0.19, 0.55, 0.85),
        palette="surface",
        seed=2,
    ),
    int(Location.HOUSE): _scene(
        "house",
        _p("spring", 0.50, 0.79, 0.9),
        palette="house",
        seed=3,
    ),
    int(Location.VALLEY): _scene(
        "valley",
        _p("stream", 0.50, 0.87, 1.0),
        _p("trees", 0.13, 0.52, 0.9),
        _p("boulders", 0.82, 0.82, 0.6),
        palette="surface",
        seed=4,
    ),
    int(Location.FOREST): _scene(
        "forest",
        _p("trees", 0.32, 0.62, 0.95),
        _p("trees", 0.72, 0.58, 0.85),
        palette="surface",
        seed=5,
    ),
    int(Location.WOODS): _scene(
        "forest",
        _p("road", 0.86, 0.9, 0.8),
        _p("trees", 0.24, 0.62, 0.9),
        palette="surface",
        seed=6,
    ),
    int(Location.SLIT): _scene(
        "streambed",
        _p("slit", 0.5, 0.78, 0.9),
        _p("stream", 0.5, 0.9, 1.0),
        palette="surface",
        seed=7,
    ),
    int(Location.OUTSIDE): _scene(
        "depression",
        _p("dust", 0.5, 0.88, 0.7),
        palette="surface",
        seed=8,
    ),
    # -- the upper cave ----------------------------------------------------
    int(Location.INSIDE): _scene(
        "tunnel",
        _p("light_shaft", 0.5, 0.22, 0.8),
        _p("cobbles", 0.5, 0.9, 0.8),
        seed=9,
    ),
    int(Location.COBBLES): _scene(
        "crawl",
        _p("cobbles", 0.5, 0.88, 1.0),
        _p("light_shaft", 0.88, 0.32, 0.55),
        seed=10,
    ),
    int(Location.DEBRIS): _scene(
        "tunnel",
        _p("debris", 0.5, 0.86, 0.9),
        _p("note", 0.74, 0.5, 0.7),
        seed=11,
    ),
    int(Location.AWK): _scene(
        "canyon",
        _p("boulders", 0.5, 0.86, 0.5),
        seed=12,
    ),
    int(Location.BIRD): _scene(
        "cavern",
        _p("column", 0.78, 0.5, 0.9),
        _p("stalactite", 0.3, 0.28, 0.7),
        _p("mist", 0.5, 0.82, 0.7),
        palette="warm",
        seed=13,
    ),
    int(Location.SPIT): _scene(
        "tunnel",
        _p("pit", 0.5, 0.8, 0.7),
        _p("mist", 0.5, 0.7, 0.6),
        seed=14,
    ),
    int(Location.EMIST): _scene(
        "hall",
        _p("stairs", 0.82, 0.74, 0.9),
        _p("mist", 0.5, 0.68, 1.0),
        _p("dome", 0.3, 0.18, 0.7),
        seed=15,
    ),
    int(Location.NUGGET): _scene(
        "tunnel",
        _p("note", 0.6, 0.5, 0.7),
        _p("rubble", 0.38, 0.87, 0.5),
        seed=16,
    ),
    int(Location.EFISS): _scene(
        "hall",
        _p("mist", 0.5, 0.68, 1.0),
        _p("chasm_ledge", 0.5, 0.8, 0.9),
        seed=17,
    ),
    int(Location.WFISS): _scene(
        "hall",
        _p("mist", 0.5, 0.68, 1.0),
        _p("chasm_ledge", 0.5, 0.8, 0.9),
        seed=18,
    ),
    int(Location.WMIST): _scene(
        "hall",
        _p("mist", 0.5, 0.74, 1.0),
        _p("column", 0.2, 0.5, 0.8),
        seed=19,
    ),
    # -- the mazes ---------------------------------------------------------
    **{
        loc: _scene(
            "maze",
            _p("column", 0.18 + 0.06 * (loc % 4), 0.45, 0.7),
            _p("rubble", 0.5, 0.9, 0.5),
            seed=loc,
        )
        for loc in range(int(Location.LIKE1), int(Location.LIKE14) + 1)
    },
    int(Location.BRINK): _scene(
        "cavern",
        _p("pit", 0.5, 0.84, 1.0),
        _p("column", 0.76, 0.5, 1.0),
        palette="warm",
        seed=34,
    ),
    int(Location.ELONG): _scene(
        "hall",
        _p("stairs", 0.16, 0.8, 0.7),
        seed=35,
    ),
    int(Location.WLONG): _scene(
        "hall",
        _p("stalactite", 0.5, 0.3, 0.7),
        seed=36,
    ),
    **{
        loc: _scene(
            "maze",
            _p("column", 0.2 + 0.05 * ((loc - 37) % 5), 0.42, 0.65),
            _p("boulders", 0.7, 0.88, 0.5),
            seed=loc,
        )
        for loc in range(int(Location.DIFF0), int(Location.DIFF10) + 1)
    },
    int(Location.PONY): _scene(
        "deadend",
        _p("rubble", 0.5, 0.88, 0.7),
        seed=48,
    ),
    # -- Hall of the Mountain King and after -------------------------------
    int(Location.CROSS): _scene(
        "tunnel",
        _p("hole", 0.5, 0.8, 0.7),
        _p("column", 0.3, 0.5, 0.8),
        seed=49,
    ),
    int(Location.HMK): _scene(
        "cavern",
        _p("stalactite", 0.3, 0.24, 0.8),
        _p("stalactite", 0.7, 0.26, 0.7),
        _p("column", 0.8, 0.5, 0.9),
        seed=50,
    ),
    int(Location.WEST): _scene("tunnel", _p("boulders", 0.72, 0.86, 0.6), seed=51),
    int(Location.SOUTH): _scene("tunnel", _p("rubble", 0.4, 0.88, 0.5), seed=52),
    int(Location.NS): _scene("tunnel", _p("hole", 0.5, 0.8, 0.8), seed=53),
    int(Location.Y2): _scene(
        "cavern",
        _p("boulders", 0.74, 0.76, 0.9),
        _p("rubble", 0.3, 0.9, 0.6),
        seed=54,
    ),
    int(Location.JUMBLE): _scene(
        "canyon",
        _p("boulders", 0.5, 0.86, 1.0),
        _p("crack", 0.7, 0.5, 0.6),
        seed=55,
    ),
    int(Location.WINDOE): _scene(
        "chasm",
        _p("window", 0.5, 0.55, 1.0),
        _p("mist", 0.5, 0.8, 1.0),
        seed=56,
    ),
    int(Location.DIRTY): _scene(
        "tunnel",
        _p("debris", 0.5, 0.86, 0.8),
        _p("rubble", 0.3, 0.9, 0.5),
        seed=57,
    ),
    int(Location.CLEAN): _scene(
        "tunnel",
        _p("pit", 0.5, 0.82, 0.6),
        _p("boulders", 0.72, 0.9, 0.5),
        seed=58,
    ),
    int(Location.WET): _scene(
        "water",
        _p("stream", 0.5, 0.86, 1.0),
        _p("mist", 0.5, 0.7, 0.7),
        palette="water",
        seed=59,
    ),
    int(Location.DUSTY): _scene(
        "cavern",
        _p("hole", 0.5, 0.8, 0.9),
        _p("dust", 0.5, 0.9, 1.0),
        seed=60,
    ),
    int(Location.COMPLEX): _scene(
        "tunnel",
        _p("rubble", 0.4, 0.88, 0.6),
        _p("column", 0.76, 0.5, 0.8),
        seed=61,
    ),
    int(Location.SHELL): _scene(
        "shell",
        _p("rubble", 0.5, 0.9, 0.8),
        palette="warm",
        seed=62,
    ),
    int(Location.ARCH): _scene(
        "tunnel",
        _p("dome", 0.5, 0.18, 0.8),
        _p("rubble", 0.4, 0.9, 0.6),
        seed=63,
    ),
    int(Location.RAGGED): _scene("canyon", _p("boulders", 0.5, 0.9, 0.7), seed=64),
    int(Location.SAC): _scene("deadend", _p("rubble", 0.5, 0.9, 0.6), seed=65),
    int(Location.ANTE): _scene("tunnel", _p("column", 0.3, 0.5, 0.8), seed=66),
    int(Location.WITT): _scene(
        "maze",
        _p("boulders", 0.5, 0.86, 0.8),
        _p("rubble", 0.3, 0.9, 0.5),
        seed=67,
    ),
    int(Location.BEDQUILT): _scene(
        "hall",
        _p("hole", 0.3, 0.8, 0.6),
        _p("hole", 0.7, 0.82, 0.6),
        _p("stalactite", 0.5, 0.26, 0.7),
        seed=68,
    ),
    int(Location.CHEESE): _scene(
        "shell",
        _p("hole", 0.35, 0.5, 0.5),
        _p("hole", 0.6, 0.45, 0.4),
        _p("hole", 0.75, 0.62, 0.5),
        palette="warm",
        seed=69,
    ),
    int(Location.SOFT): _scene(
        "soft",
        _p("curtains", 0.5, 0.45, 1.0),
        palette="soft",
        seed=70,
    ),
    int(Location.E2PIT): _scene(
        "cavern",
        _p("pit", 0.35, 0.86, 0.9),
        _p("slab", 0.62, 0.72, 0.8),
        seed=71,
    ),
    int(Location.W2PIT): _scene(
        "cavern",
        _p("pit", 0.65, 0.86, 0.9),
        _p("hole", 0.72, 0.5, 0.7),
        seed=72,
    ),
    int(Location.EPIT): _scene(
        "cavern",
        _p("pit", 0.5, 0.9, 1.0),
        _p("oil_pool", 0.72, 0.88, 0.7),
        palette="water",
        seed=73,
    ),
    int(Location.WPIT): _scene(
        "cavern",
        _p("pit", 0.5, 0.9, 1.0),
        _p("hole", 0.72, 0.5, 0.7),
        seed=74,
    ),
    int(Location.NARROW): _scene("crawl", _p("rubble", 0.5, 0.9, 0.6), seed=75),
    int(Location.GIANT): _scene(
        "cavern",
        _p("column", 0.8, 0.5, 1.0),
        _p("stalactite", 0.25, 0.24, 0.9),
        seed=76,
    ),
    int(Location.BLOCK): _scene("deadend", _p("cavein", 0.5, 0.8, 1.0), seed=77),
    int(Location.IMMENSE): _scene(
        "hall",
        _p("column", 0.3, 0.5, 0.9),
        _p("column", 0.7, 0.5, 0.9),
        seed=78,
    ),
    int(Location.FALLS): _scene(
        "water",
        _p("waterfall", 0.5, 0.5, 1.0),
        _p("mist", 0.5, 0.86, 0.8),
        palette="water",
        seed=79,
    ),
    int(Location.STEEP): _scene(
        "cavern",
        _p("stairs", 0.5, 0.7, 1.0),
        _p("pit", 0.5, 0.9, 0.9),
        seed=80,
    ),
    int(Location.ABOVEP): _scene("canyon", _p("boulders", 0.5, 0.9, 0.6), seed=81),
    int(Location.SJUNC): _scene(
        "canyon",
        _p("boulders", 0.3, 0.9, 0.5),
        _p("crack", 0.7, 0.6, 0.5),
        seed=82,
    ),
    int(Location.TITE): _scene("cavern", _p("stalactite", 0.5, 0.3, 1.0), seed=83),
    int(Location.LOW): _scene("tunnel", _p("rubble", 0.5, 0.9, 0.7), seed=84),
    int(Location.CRAWL): _scene("crawl", _p("rubble", 0.5, 0.9, 0.6), seed=85),
    int(Location.WINDOW): _scene(
        "chasm",
        _p("window", 0.5, 0.55, 1.0),
        _p("mist", 0.5, 0.8, 1.0),
        seed=86,
    ),
    int(Location.ORIENTAL): _scene(
        "shrine",
        _p("mural", 0.5, 0.45, 1.0),
        palette="shrine",
        seed=87,
    ),
    int(Location.MISTY): _scene(
        "chasm",
        _p("mist", 0.5, 0.74, 1.0),
        _p("boulders", 0.5, 0.9, 0.6),
        seed=88,
    ),
    int(Location.ALCOVE): _scene("tunnel", _p("crack", 0.7, 0.6, 0.5), seed=89),
    int(Location.PROOM): _scene(
        "tunnel",
        _p("green_glow", 0.5, 0.5, 1.0),
        seed=90,
    ),
    int(Location.DROOM): _scene("tunnel", palette="void", seed=91),
    int(Location.SLAB): _scene("cavern", _p("slab", 0.5, 0.8, 1.0), seed=92),
    int(Location.ABOVER): _scene("canyon", _p("boulders", 0.5, 0.9, 0.6), seed=93),
    int(Location.MIRROR): _scene(
        "canyon",
        _p("mirror_lake", 0.5, 0.86, 1.0),
        _p("mist", 0.5, 0.7, 1.0),
        palette="water",
        seed=94,
    ),
    int(Location.RES): _scene(
        "water",
        _p("mist", 0.5, 0.7, 1.0),
        palette="water",
        seed=95,
    ),
    int(Location.SCAN1): _scene("canyon", _p("boulders", 0.6, 0.9, 0.6), seed=96),
    int(Location.SCAN2): _scene("canyon", _p("boulders", 0.4, 0.9, 0.6), seed=97),
    int(Location.SCAN3): _scene("canyon", _p("rubble", 0.6, 0.9, 0.6), seed=98),
    int(Location.SECRET): _scene("canyon", _p("crack", 0.5, 0.7, 0.7), seed=99),
    int(Location.WIDE): _scene("canyon", _p("boulders", 0.3, 0.9, 0.5), seed=100),
    int(Location.TIGHT): _scene("canyon", _p("boulders", 0.5, 0.86, 0.8), seed=101),
    int(Location.TALL): _scene("canyon", _p("crack", 0.7, 0.6, 0.5), seed=102),
    int(Location.BOULDERS): _scene(
        "deadend",
        _p("boulders", 0.5, 0.8, 1.0),
        seed=103,
    ),
    int(Location.SCORR): _scene("tunnel", _p("rubble", 0.5, 0.9, 0.6), seed=104),
    int(Location.SWSIDE): _scene("chasm", _p("mist", 0.5, 0.74, 1.0), seed=105),
    # -- dead ends ---------------------------------------------------------
    **{
        loc: _scene(
            "deadend",
            _p("rubble", 0.35 + 0.05 * (loc % 5), 0.9, 0.55),
            seed=loc,
        )
        for loc in range(int(Location.DEAD0), int(Location.DEAD11) + 1)
    },
    int(Location.NESIDE): _scene("chasm", _p("boulders", 0.5, 0.9, 0.6), seed=118),
    int(Location.CORR): _scene("tunnel", _p("rubble", 0.4, 0.9, 0.6), seed=119),
    int(Location.FORK): _scene(
        "canyon",
        _p("boulders", 0.5, 0.9, 0.6),
        _p("crack", 0.6, 0.6, 0.5),
        seed=120,
    ),
    int(Location.WARM): _scene(
        "tunnel",
        _p("warm_glow", 0.5, 0.4, 1.0),
        palette="warm",
        seed=121,
    ),
    int(Location.VIEW): _scene(
        "volcano",
        _p("volcano", 0.5, 0.58, 1.0),
        _p("lava", 0.5, 0.82, 1.0),
        palette="volcano",
        seed=122,
    ),
    int(Location.CHAMBER): _scene(
        "cavern",
        _p("boulders", 0.5, 0.86, 1.0),
        _p("warm_glow", 0.5, 0.5, 0.8),
        palette="warm",
        seed=123,
    ),
    int(Location.LIME): _scene(
        "tunnel",
        _p("stalactite", 0.3, 0.3, 0.6),
        _p("stalagmite", 0.7, 0.86, 0.7),
        seed=124,
    ),
    int(Location.FBARR): _scene("tunnel", _p("sign", 0.5, 0.55, 0.9), seed=125),
    int(Location.BARR): _scene(
        "shell",
        _p("dust", 0.5, 0.9, 1.0),
        palette="warm",
        seed=126,
    ),
    int(Location.NEEND): _scene(
        "cavern",
        _p("column", 0.8, 0.5, 1.0),
        _p("dust", 0.5, 0.9, 0.8),
        seed=127,
    ),
    int(Location.SWEND): _scene(
        "cavern",
        _p("pit", 0.5, 0.86, 0.9),
        _p("bones", 0.5, 0.9, 0.7),
        seed=128,
    ),
    # -- special, death, and forced-move locations -------------------------
    int(Location.CRACK): _scene("deadend", _p("crack", 0.5, 0.6, 1.0), seed=129),
    int(Location.NECK): _scene("void", palette="void", seed=130),
    int(Location.LOSE): _scene("void", palette="void", seed=131),
    int(Location.CANT): _scene("canyon", _p("dome", 0.5, 0.24, 0.9), seed=132),
    int(Location.CLIMB): _scene(
        "cavern",
        _p("hole", 0.5, 0.3, 0.6),
        _p("light_shaft", 0.5, 0.2, 0.7),
        seed=133,
    ),
    int(Location.CHECK): _scene("tunnel", seed=134),
    int(Location.SNAKED): _scene("tunnel", _p("rubble", 0.5, 0.9, 0.6), seed=135),
    int(Location.THRU): _scene("crawl", _p("rubble", 0.5, 0.9, 0.6), seed=136),
    int(Location.DUCK): _scene("crawl", _p("rubble", 0.5, 0.9, 0.6), seed=137),
    int(Location.SEWER): _scene(
        "sewer",
        _p("stream", 0.5, 0.88, 1.0),
        _p("sewer", 0.5, 0.7, 0.9),
        palette="surface",
        seed=138,
    ),
    int(Location.UPNOUT): _scene("cavern", _p("pit", 0.5, 0.86, 1.0), seed=139),
    int(Location.DIDIT): _scene(
        "cavern",
        _p("plant", 0.5, 0.5, 0.9),
        _p("light_shaft", 0.5, 0.2, 0.8),
        seed=140,
    ),
}

# The engine also uses negative pseudo-locations (in hand, limbo).
SCENES[int(Location.INHAND)] = Scene("void", (), "void", 0)
SCENES[int(Location.LIMBO)] = Scene("void", (), "void", 0)

FALLBACK_SCENE = Scene("tunnel", (), "cave", 0)


def scene_for(loc: int) -> Scene:
    """The scene for a location, with a safe fallback for odd engine states."""
    return SCENES.get(loc, FALLBACK_SCENE)


# ---------------------------------------------------------------------------
# Names and icons for objects
# ---------------------------------------------------------------------------

#: Every object's display name.  The engine leaves several objects unnamed
#: because their notes describe them; the picture layer still needs a label.
ITEM_LABELS: dict[int, str] = {
    int(Object.KEYS): "Set of keys",
    int(Object.LAMP): "Brass lantern",
    int(Object.GRATE): "Steel grate",
    int(Object.GRATE_): "Steel grate",
    int(Object.CAGE): "Wicker cage",
    int(Object.ROD): "Black rod",
    int(Object.ROD2): "Black rod",
    int(Object.TREADS): "Stone steps",
    int(Object.TREADS_): "Stone steps",
    int(Object.BIRD): "Little bird",
    int(Object.DOOR): "Door",
    int(Object.PILLOW): "Velvet pillow",
    int(Object.SNAKE): "Snake",
    int(Object.CRYSTAL): "Crystal bridge",
    int(Object.CRYSTAL_): "Crystal bridge",
    int(Object.TABLET): "Stone tablet",
    int(Object.CLAM): "Giant clam",
    int(Object.OYSTER): "Giant oyster",
    int(Object.MAG): "Spelunker Today",
    int(Object.DWARF): "Little dwarf",
    int(Object.KNIFE): "Dwarf's knife",
    int(Object.FOOD): "Tasty food",
    int(Object.BOTTLE): "Small bottle",
    int(Object.WATER): "Water in the bottle",
    int(Object.OIL): "Oil in the bottle",
    int(Object.MIRROR): "Mirror",
    int(Object.MIRROR_): "Mirror",
    int(Object.PLANT): "Beanstalk",
    int(Object.PLANT2): "Beanstalk",
    int(Object.PLANT2_): "Beanstalk",
    int(Object.STALACTITE): "Stalactite",
    int(Object.SHADOW): "Shadowy figure",
    int(Object.SHADOW_): "Shadowy figure",
    int(Object.AXE): "Dwarf's axe",
    int(Object.ART): "Cave drawings",
    int(Object.PIRATE): "Pirate",
    int(Object.DRAGON): "Dragon",
    int(Object.DRAGON_): "Dragon",
    int(Object.BRIDGE): "Bridge",
    int(Object.BRIDGE_): "Bridge",
    int(Object.TROLL): "Troll",
    int(Object.TROLL_): "Troll",
    int(Object.TROLL2): "Troll",
    int(Object.TROLL2_): "Troll",
    int(Object.BEAR): "Bear",
    int(Object.MESSAGE): "Message",
    int(Object.GEYSER): "Geyser",
    int(Object.PONY): "Vending machine",
    int(Object.BATTERIES): "Batteries",
    int(Object.MOSS): "Moss",
    int(Object.GOLD): "Gold nugget",
    int(Object.DIAMONDS): "Diamonds",
    int(Object.SILVER): "Silver bars",
    int(Object.JEWELS): "Jewelry",
    int(Object.COINS): "Coins",
    int(Object.CHEST): "Treasure chest",
    int(Object.EGGS): "Golden eggs",
    int(Object.TRIDENT): "Jeweled trident",
    int(Object.VASE): "Ming vase",
    int(Object.EMERALD): "Emerald",
    int(Object.PYRAMID): "Platinum pyramid",
    int(Object.PEARL): "Pearl",
    int(Object.RUG): "Persian rug",
    int(Object.RUG_): "Persian rug",
    int(Object.SPICES): "Rare spices",
    int(Object.CHAIN): "Golden chain",
}

#: Which icon painter draws each object (see ``advent.art.ICONS``).
ITEM_ICONS: dict[int, str] = {
    int(Object.KEYS): "keys",
    int(Object.LAMP): "lamp",
    int(Object.GRATE): "grate",
    int(Object.GRATE_): "grate",
    int(Object.CAGE): "cage",
    int(Object.ROD): "rod",
    int(Object.ROD2): "rod",
    int(Object.TREADS): "treads",
    int(Object.TREADS_): "treads",
    int(Object.BIRD): "bird",
    int(Object.DOOR): "door",
    int(Object.PILLOW): "pillow",
    int(Object.SNAKE): "snake",
    int(Object.CRYSTAL): "crystal",
    int(Object.CRYSTAL_): "crystal",
    int(Object.TABLET): "tablet",
    int(Object.CLAM): "clam",
    int(Object.OYSTER): "oyster",
    int(Object.MAG): "magazine",
    int(Object.DWARF): "dwarf",
    int(Object.KNIFE): "knife",
    int(Object.FOOD): "food",
    int(Object.BOTTLE): "bottle",
    int(Object.WATER): "water",
    int(Object.OIL): "oil",
    int(Object.MIRROR): "mirror",
    int(Object.MIRROR_): "mirror",
    int(Object.PLANT): "plant",
    int(Object.PLANT2): "plant",
    int(Object.PLANT2_): "plant",
    int(Object.STALACTITE): "stalactite",
    int(Object.SHADOW): "shadow",
    int(Object.SHADOW_): "shadow",
    int(Object.AXE): "axe",
    int(Object.ART): "mural",
    int(Object.PIRATE): "pirate",
    int(Object.DRAGON): "dragon",
    int(Object.DRAGON_): "dragon",
    int(Object.BRIDGE): "bridge",
    int(Object.BRIDGE_): "bridge",
    int(Object.TROLL): "troll",
    int(Object.TROLL_): "troll",
    int(Object.TROLL2): "troll",
    int(Object.TROLL2_): "troll",
    int(Object.BEAR): "bear",
    int(Object.MESSAGE): "message",
    int(Object.GEYSER): "geyser",
    int(Object.PONY): "vending",
    int(Object.BATTERIES): "batteries",
    int(Object.MOSS): "moss",
    int(Object.GOLD): "gold",
    int(Object.DIAMONDS): "diamonds",
    int(Object.SILVER): "silver",
    int(Object.JEWELS): "jewels",
    int(Object.COINS): "coins",
    int(Object.CHEST): "chest",
    int(Object.EGGS): "eggs",
    int(Object.TRIDENT): "trident",
    int(Object.VASE): "vase",
    int(Object.EMERALD): "emerald",
    int(Object.PYRAMID): "pyramid",
    int(Object.PEARL): "pearl",
    int(Object.RUG): "rug",
    int(Object.RUG_): "rug",
    int(Object.SPICES): "spices",
    int(Object.CHAIN): "chain",
}

#: A word that the parser maps back to the object, or ``None`` when the
#: original vocabulary has no word for it (only a couple of scenery parts).
ITEM_WORDS: dict[int, str | None] = {
    int(Object.KEYS): "keys",
    int(Object.LAMP): "lamp",
    int(Object.GRATE): "grate",
    int(Object.GRATE_): "grate",
    int(Object.CAGE): "cage",
    int(Object.ROD): "rod",
    int(Object.ROD2): "rod",
    int(Object.TREADS): None,
    int(Object.TREADS_): None,
    int(Object.BIRD): "bird",
    int(Object.DOOR): "door",
    int(Object.PILLOW): "pillow",
    int(Object.SNAKE): "snake",
    int(Object.CRYSTAL): "fissure",
    int(Object.CRYSTAL_): "fissure",
    int(Object.TABLET): "tablet",
    int(Object.CLAM): "clam",
    int(Object.OYSTER): "oyster",
    int(Object.MAG): "magazine",
    int(Object.DWARF): "dwarf",
    int(Object.KNIFE): "knife",
    int(Object.FOOD): "food",
    int(Object.BOTTLE): "bottle",
    int(Object.WATER): "water",
    int(Object.OIL): "oil",
    int(Object.MIRROR): "mirror",
    int(Object.MIRROR_): "mirror",
    int(Object.PLANT): "plant",
    int(Object.PLANT2): "plant",
    int(Object.PLANT2_): "plant",
    int(Object.STALACTITE): "stalactite",
    int(Object.SHADOW): "shadow",
    int(Object.SHADOW_): "shadow",
    int(Object.AXE): "axe",
    int(Object.ART): "drawing",
    int(Object.PIRATE): "pirate",
    int(Object.DRAGON): "dragon",
    int(Object.DRAGON_): "dragon",
    int(Object.BRIDGE): "chasm",
    int(Object.BRIDGE_): "chasm",
    int(Object.TROLL): "troll",
    int(Object.TROLL_): "troll",
    int(Object.TROLL2): "troll",
    int(Object.TROLL2_): "troll",
    int(Object.BEAR): "bear",
    int(Object.MESSAGE): "message",
    int(Object.GEYSER): "geyser",
    int(Object.PONY): "machine",
    int(Object.BATTERIES): "batteries",
    int(Object.MOSS): "moss",
    int(Object.GOLD): "gold",
    int(Object.DIAMONDS): "diamonds",
    int(Object.SILVER): "silver",
    int(Object.JEWELS): "jewelry",
    int(Object.COINS): "coins",
    int(Object.CHEST): "chest",
    int(Object.EGGS): "eggs",
    int(Object.TRIDENT): "trident",
    int(Object.VASE): "vase",
    int(Object.EMERALD): "emerald",
    int(Object.PYRAMID): "pyramid",
    int(Object.PEARL): "pearl",
    int(Object.RUG): "rug",
    int(Object.RUG_): "rug",
    int(Object.SPICES): "spices",
    int(Object.CHAIN): "chain",
}


def item_label(obj: int) -> str:
    """The label for an object, falling back to the engine's own name."""
    label = ITEM_LABELS.get(obj)
    if label:
        return label
    name = D.OBJECTS[obj].name if obj in D.OBJECTS else None
    return name or "Something"


def item_word(obj: int) -> str | None:
    """The command word for an object, or ``None`` if the vocabulary lacks one."""
    return ITEM_WORDS.get(obj)


#: Objects that are part of the scenery or are creatures.  They are painted
#: large in the scene at ``(x, y, scale)`` instead of in the small item row.
ACTOR_SLOTS: dict[int, tuple[float, float, float]] = {
    int(Object.GRATE): (0.5, 0.78, 0.7),
    int(Object.GRATE_): (0.5, 0.78, 0.7),
    int(Object.TREADS): (0.5, 0.72, 0.8),
    int(Object.TREADS_): (0.5, 0.72, 0.8),
    int(Object.SNAKE): (0.5, 0.82, 0.45),
    int(Object.DOOR): (0.76, 0.62, 0.6),
    int(Object.CRYSTAL): (0.5, 0.82, 0.9),
    int(Object.CRYSTAL_): (0.5, 0.82, 0.9),
    int(Object.TABLET): (0.5, 0.55, 0.6),
    int(Object.DWARF): (0.36, 0.74, 0.5),
    int(Object.MIRROR): (0.5, 0.72, 0.9),
    int(Object.MIRROR_): (0.5, 0.72, 0.9),
    int(Object.PLANT): (0.5, 0.52, 0.95),
    int(Object.PLANT2): (0.5, 0.52, 0.95),
    int(Object.PLANT2_): (0.5, 0.52, 0.95),
    int(Object.STALACTITE): (0.5, 0.3, 0.9),
    int(Object.SHADOW): (0.5, 0.62, 0.85),
    int(Object.SHADOW_): (0.5, 0.62, 0.85),
    int(Object.ART): (0.5, 0.45, 0.95),
    int(Object.PIRATE): (0.64, 0.62, 0.85),
    int(Object.DRAGON): (0.5, 0.62, 0.95),
    int(Object.DRAGON_): (0.5, 0.62, 0.95),
    int(Object.BRIDGE): (0.5, 0.82, 0.9),
    int(Object.BRIDGE_): (0.5, 0.82, 0.9),
    int(Object.TROLL): (0.56, 0.62, 0.9),
    int(Object.TROLL_): (0.56, 0.62, 0.9),
    int(Object.TROLL2): (0.56, 0.62, 0.9),
    int(Object.TROLL2_): (0.56, 0.62, 0.9),
    int(Object.BEAR): (0.62, 0.66, 0.8),
    int(Object.MESSAGE): (0.5, 0.6, 0.7),
    int(Object.GEYSER): (0.5, 0.6, 0.8),
    int(Object.PONY): (0.7, 0.7, 0.75),
    int(Object.MOSS): (0.4, 0.82, 0.5),
}


def is_actor(obj: int) -> bool:
    return obj in ACTOR_SLOTS


# ---------------------------------------------------------------------------
# Exit labels
# ---------------------------------------------------------------------------

#: ``motion -> (button label, command word)``.  The command word must be one
#: the original vocabulary accepts (the test suite checks every one).
MOTION_LABELS: dict[int, tuple[str, str]] = {
    int(Motion.N): ("N", "n"),
    int(Motion.S): ("S", "s"),
    int(Motion.E): ("E", "e"),
    int(Motion.W): ("W", "w"),
    int(Motion.NE): ("NE", "ne"),
    int(Motion.SE): ("SE", "se"),
    int(Motion.NW): ("NW", "nw"),
    int(Motion.SW): ("SW", "sw"),
    int(Motion.U): ("Up", "up"),
    int(Motion.D): ("Down", "down"),
    int(Motion.L): ("Left", "left"),
    int(Motion.R): ("Right", "right"),
    int(Motion.IN): ("In", "in"),
    int(Motion.OUT): ("Out", "out"),
    int(Motion.FORWARD): ("Forward", "forward"),
    int(Motion.BACK): ("Back", "back"),
    int(Motion.OVER): ("Over", "over"),
    int(Motion.ACROSS): ("Across", "across"),
    int(Motion.UPSTREAM): ("Upstream", "upstream"),
    int(Motion.DOWNSTREAM): ("Downstream", "downstream"),
    int(Motion.ENTER): ("Enter", "enter"),
    int(Motion.CRAWL): ("Crawl", "crawl"),
    int(Motion.JUMP): ("Jump", "jump"),
    int(Motion.CLIMB): ("Climb", "climb"),
    int(Motion.LOOK): ("Look", "look"),
    int(Motion.CROSS): ("Cross", "cross"),
    int(Motion.ROAD): ("Road", "road"),
    int(Motion.WOODS): ("Forest", "forest"),
    int(Motion.VALLEY): ("Valley", "valley"),
    int(Motion.HOUSE): ("Building", "building"),
    int(Motion.GULLY): ("Gully", "gully"),
    int(Motion.STREAM): ("Stream", "stream"),
    int(Motion.DEPRESSION): ("Depression", "depression"),
    int(Motion.ENTRANCE): ("Entrance", "entrance"),
    int(Motion.CAVE): ("Cave", "cave"),
    int(Motion.ROCK): ("Rock", "rock"),
    int(Motion.SLAB): ("Slab", "slab"),
    int(Motion.BED): ("Bed", "bed"),
    int(Motion.PASSAGE): ("Passage", "passage"),
    int(Motion.CAVERN): ("Cavern", "cavern"),
    int(Motion.CANYON): ("Canyon", "canyon"),
    int(Motion.AWKWARD): ("Awkward Canyon", "awkward"),
    int(Motion.SECRET): ("Secret Canyon", "secret"),
    int(Motion.BEDQUILT): ("Bedquilt", "bedquilt"),
    int(Motion.RESERVOIR): ("Reservoir", "reservoir"),
    int(Motion.GIANT): ("Giant Room", "giant"),
    int(Motion.ORIENTAL): ("Oriental Room", "oriental"),
    int(Motion.SHELL): ("Shell Room", "shell"),
    int(Motion.BARREN): ("Barren Room", "barren"),
    int(Motion.BROKEN): ("Broken Rock", "broken"),
    int(Motion.DEBRIS): ("Debris Room", "debris"),
    int(Motion.VIEW): ("View", "view"),
    int(Motion.FORK): ("Fork", "fork"),
    int(Motion.PIT): ("Pit", "pit"),
    int(Motion.SLIT): ("Slit", "slit"),
    int(Motion.CRACK): ("Crack", "crack"),
    int(Motion.DOME): ("Dome", "dome"),
    int(Motion.HOLE): ("Hole", "hole"),
    int(Motion.WALL): ("Wall", "wall"),
    int(Motion.HALL): ("Hall", "hall"),
    int(Motion.ROOM): ("Room", "room"),
    int(Motion.FLOOR): ("Floor", "floor"),
    int(Motion.STAIRS): ("Stairs", "stairs"),
    int(Motion.STEPS): ("Steps", "steps"),
    int(Motion.COBBLES): ("Cobbles", "cobbles"),
    int(Motion.SURFACE): ("Surface", "surface"),
    int(Motion.DARK): ("Dark", "dark"),
    int(Motion.LOW): ("Low Room", "low"),
    int(Motion.OUTDOORS): ("Outdoors", "outdoors"),
    int(Motion.Y2): ("Y2", "y2"),
    int(Motion.XYZZY): ("XYZY", "xyzzy"),
    int(Motion.PLUGH): ("PLUGH", "plugh"),
    int(Motion.PLOVER): ("PLOVER", "plover"),
    int(Motion.OFFICE): ("Office", "office"),
    int(Motion.NOWHERE): ("Nowhere", "nowhere"),
}

#: Preferred order for exit buttons.
EXIT_ORDER: tuple[int, ...] = (
    int(Motion.N),
    int(Motion.NE),
    int(Motion.E),
    int(Motion.SE),
    int(Motion.S),
    int(Motion.SW),
    int(Motion.W),
    int(Motion.NW),
    int(Motion.U),
    int(Motion.D),
    int(Motion.L),
    int(Motion.R),
    int(Motion.IN),
    int(Motion.OUT),
    int(Motion.ENTER),
    int(Motion.UPSTREAM),
    int(Motion.DOWNSTREAM),
    int(Motion.FORWARD),
    int(Motion.BACK),
    int(Motion.OVER),
    int(Motion.ACROSS),
    int(Motion.CROSS),
    int(Motion.JUMP),
    int(Motion.CLIMB),
    int(Motion.CRAWL),
    int(Motion.LOOK),
    int(Motion.ROAD),
    int(Motion.WOODS),
    int(Motion.VALLEY),
    int(Motion.HOUSE),
    int(Motion.GULLY),
    int(Motion.STREAM),
    int(Motion.DEPRESSION),
    int(Motion.ENTRANCE),
    int(Motion.CAVE),
    int(Motion.ROCK),
    int(Motion.SLAB),
    int(Motion.BED),
    int(Motion.PASSAGE),
    int(Motion.CAVERN),
    int(Motion.CANYON),
    int(Motion.AWKWARD),
    int(Motion.SECRET),
    int(Motion.BEDQUILT),
    int(Motion.RESERVOIR),
    int(Motion.GIANT),
    int(Motion.ORIENTAL),
    int(Motion.SHELL),
    int(Motion.BARREN),
    int(Motion.BROKEN),
    int(Motion.DEBRIS),
    int(Motion.VIEW),
    int(Motion.FORK),
    int(Motion.PIT),
    int(Motion.SLIT),
    int(Motion.CRACK),
    int(Motion.DOME),
    int(Motion.HOLE),
    int(Motion.WALL),
    int(Motion.HALL),
    int(Motion.ROOM),
    int(Motion.FLOOR),
    int(Motion.STAIRS),
    int(Motion.STEPS),
    int(Motion.COBBLES),
    int(Motion.SURFACE),
    int(Motion.DARK),
    int(Motion.LOW),
    int(Motion.OUTDOORS),
    int(Motion.Y2),
    int(Motion.XYZZY),
    int(Motion.PLUGH),
    int(Motion.PLOVER),
    int(Motion.OFFICE),
    int(Motion.NOWHERE),
)


def motion_label(mot: int) -> str:
    """A short button label for a motion."""
    entry = MOTION_LABELS.get(mot)
    if entry:
        return entry[0]
    try:
        return Motion(mot).name.replace("_", " ").title()
    except ValueError:
        return "Go"


def motion_command(mot: int) -> str:
    """The word to type for a motion (always one the parser accepts)."""
    entry = MOTION_LABELS.get(mot)
    if entry:
        return entry[1]
    return Motion(mot).name.lower()


def sorted_motions(motions: list[int]) -> list[int]:
    """Order motions for the exit bar: compass points first, then the rest."""
    rank = {mot: i for i, mot in enumerate(EXIT_ORDER)}
    return sorted(motions, key=lambda mot: (rank.get(mot, len(rank)), mot))


__all__ = [
    "ACTOR_SLOTS",
    "EXIT_ORDER",
    "FALLBACK_SCENE",
    "ITEM_ICONS",
    "ITEM_LABELS",
    "ITEM_WORDS",
    "MOTION_LABELS",
    "Prop",
    "SCENES",
    "Scene",
    "is_actor",
    "item_label",
    "item_word",
    "motion_command",
    "motion_label",
    "scene_for",
    "sorted_motions",
]
