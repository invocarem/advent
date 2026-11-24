"""The travel table, and the engine's quirky destination rules."""

from __future__ import annotations

import pytest

from advent.data import LOCATIONS, MAX_SPEC, REMARKS, START, TRAVELS
from advent.vocabulary import (
    INHAND,
    MAX_LOC,
    MAX_OBJ,
    MIN_FORCED_LOC,
    Action,
    Location,
    Motion,
    Object,
)


def test_table_sizes():
    assert len(TRAVELS) == 740
    assert len(LOCATIONS) == 140
    assert len(REMARKS) == 14


def test_start_sentinel_covers_every_real_location():
    # start[ppass] is the end of didit's instruction list (advent.w line 2108).
    assert START[int(Location.DIDIT) + 1] == len(TRAVELS)
    for loc in range(1, int(MAX_LOC) + 1):
        assert loc in START
        assert START[loc] <= START[loc + 1]


def test_every_destination_is_valid():
    specials = {int(Location.PPASS), int(Location.PDROP), int(Location.TROLL)}
    for inst in TRAVELS:
        assert 0 <= inst.dest <= MAX_SPEC + len(REMARKS)
        if inst.dest > MAX_SPEC:
            assert inst.dest - MAX_SPEC - 1 < len(REMARKS)
        elif inst.dest > MAX_LOC:
            assert inst.dest in specials


def test_conditions_are_well_formed():
    for inst in TRAVELS:
        assert inst.cond >= 0
        if inst.cond > 300:  # "property of object o must not be k"
            assert inst.cond % 100 <= int(MAX_OBJ)


def test_every_real_location_has_instructions():
    for loc in range(1, int(MAX_LOC) + 1):
        assert START[loc] < START[loc + 1]


def test_forced_locations_are_pseudo_rooms():
    assert int(Location.CRACK) == int(MIN_FORCED_LOC)
    for loc in range(int(MIN_FORCED_LOC), int(MAX_LOC) + 1):
        # every forced location begins with a FORCE instruction (FORCE == N)
        assert TRAVELS[START[loc]].mot == int(Motion.N)


# ---------------------------------------------------------------------------
# Destination rules, driven through the engine
# ---------------------------------------------------------------------------


@pytest.fixture
def game(make_game):
    return make_game(["n"])


def next_loc(game, loc, mot):
    game.loc = int(loc)
    game._determine_next_location(int(mot))
    return game.newloc


def test_fissure_without_the_bridge(game):
    game.prop[int(Object.CRYSTAL)] = 0
    assert next_loc(game, Location.EFISS, Motion.JUMP) == int(Location.LOSE)
    assert next_loc(game, Location.EFISS, Motion.FORWARD) == int(Location.LOSE)
    assert next_loc(game, Location.EFISS, Motion.OVER) == int(Location.EFISS)


def test_fissure_with_the_bridge(game):
    game.prop[int(Object.CRYSTAL)] = 1
    # `jump` only scolds you ...
    assert next_loc(game, Location.EFISS, Motion.JUMP) == int(Location.EFISS)
    # ... but `forward` falls through to the `over` instruction and crosses.
    assert next_loc(game, Location.EFISS, Motion.FORWARD) == int(Location.WFISS)
    assert next_loc(game, Location.EFISS, Motion.OVER) == int(Location.WFISS)


def test_plover_alcove_passage(game):
    assert next_loc(game, Location.ALCOVE, Motion.E) == int(Location.PROOM)
    game._carry(int(Object.EMERALD))
    assert next_loc(game, Location.ALCOVE, Motion.E) == int(Location.PROOM)
    game._carry(int(Object.LAMP))
    assert next_loc(game, Location.ALCOVE, Motion.E) == int(Location.ALCOVE)


def test_troll_bridge_needs_a_payment(game):
    assert next_loc(game, Location.SWSIDE, Motion.OVER) == int(Location.SWSIDE)
    game.prop[int(Object.TROLL)] = 0
    game._destroy(int(Object.TROLL))
    game._destroy(int(Object.TROLL_))
    game._drop(int(Object.TROLL2), int(Location.SWSIDE))
    game._drop(int(Object.TROLL2_), int(Location.NESIDE))
    assert next_loc(game, Location.SWSIDE, Motion.OVER) == int(Location.NESIDE)
    assert game.prop[int(Object.TROLL)] == 1


def test_a_remark_leaves_you_where_you_are(game):
    # The slit refuses to let you through: a remark, and you stay.
    assert next_loc(game, Location.SLIT, Motion.D) == int(Location.SLIT)


def test_inapplicable_motion(game):
    game.verb = Action.ABSTAIN
    game.console.output.clear()
    assert next_loc(game, Location.ROAD, Motion.CRAWL) == int(Location.ROAD)
    assert game.console.text == "Which way?\n"


# ---------------------------------------------------------------------------
# The initial object layout
# ---------------------------------------------------------------------------


def test_objects_start_where_the_table_says(make_game):
    game = make_game()
    assert game.place[int(Object.KEYS)] == int(Location.HOUSE)
    assert game.place[int(Object.CAGE)] == int(Location.COBBLES)
    assert game.place[int(Object.ROD)] == int(Location.DEBRIS)
    assert game.place[int(Object.GOLD)] == int(Location.NUGGET)
    assert game.place[int(Object.PEARL)] == int(Location.LIMBO)
    assert game.holding == 0
    assert game.place[int(Object.BOTTLE)] != INHAND


def test_treasure_properties_start_unseen(make_game):
    game = make_game()
    for t in range(int(Object.GOLD), int(MAX_OBJ) + 1):
        assert game.prop[t] == -1
    assert game.prop[int(Object.LAMP)] == 0


def test_room_lists_are_in_ascending_object_order(make_game):
    game = make_game()
    t = game.first[int(Location.HOUSE)]
    listed = []
    while t:
        listed.append(t)
        t = game.link[t]
    assert listed == sorted(listed)
    assert listed == [int(Object.KEYS), int(Object.LAMP), int(Object.FOOD), int(Object.BOTTLE)]
