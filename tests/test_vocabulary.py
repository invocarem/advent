"""The vocabulary: word table, enums, fixed and default messages."""

from __future__ import annotations

import pytest

from advent.vocabulary import (
    DEFAULT_MSG,
    MESSAGES,
    MESSAGE_WORDS,
    WORDS,
    Action,
    Location,
    Motion,
    Object,
    WordType,
    lookup,
)


def test_only_five_letters_matter():
    assert lookup("northeast") == (WordType.MOTION, Motion.N)
    assert lookup("north") == (WordType.MOTION, Motion.N)
    assert lookup("NORTHEAST") == (WordType.MOTION, Motion.N)
    assert lookup("treasure") == (WordType.OBJECT, Object.CHEST)


def test_lookup_is_case_insensitive():
    assert lookup("LaMp") == (WordType.OBJECT, Object.LAMP)


def test_unknown_words():
    assert lookup("tickle") is None
    assert lookup("") is None


def test_word_count():
    # 283 entries in advent.w collapse to 282 distinct five-letter keys.
    assert len(WORDS) == 282


def test_there_is_no_woods_word():
    # advent.w deliberately omits "woods"; the motion is spelled "forest".
    assert lookup("woods") is None
    assert lookup("forest") == (WordType.MOTION, Motion.WOODS)


def test_enums_match_the_c_source():
    assert int(Location.INHAND) == -1
    assert int(Location.LIMBO) == 0
    assert int(Location.ROAD) == 1
    assert int(Location.TROLL) == 143
    assert int(Object.GOLD) == 51
    assert int(Object.CHAIN) == 66
    assert int(Motion.NOWHERE) == 74
    assert int(Action.QUIT) == 29


def test_fixed_messages():
    assert len(MESSAGES) == 13
    assert MESSAGES[0] == "Good try, but that is an old worn-out magic word."
    assert MESSAGES[12] == "I don't know how."
    # the three dynamite endings live at indices 5, 6 and 9
    assert "splashed across the" in MESSAGES[5]
    assert "river of molten lava" in MESSAGES[6]
    assert "friendly elves" in MESSAGES[9]


def test_message_word_indices():
    for word, index in MESSAGE_WORDS:
        assert lookup(word) == (WordType.MESSAGE, index)


@pytest.mark.parametrize(
    "alias, target",
    [
        (Action.CLOSE, Action.OPEN),
        (Action.OFF, Action.ON),
        (Action.POUR, Action.DROP),
        (Action.TOSS, Action.DROP),
        (Action.WAKE, Action.EAT),
        (Action.KILL, Action.EAT),
        (Action.INVENTORY, Action.FIND),
        (Action.QUIT, Action.SCORE),
    ],
)
def test_default_message_aliases(alias, target):
    assert DEFAULT_MSG[alias] == DEFAULT_MSG[target]


def test_actions_without_a_default():
    assert Action.ABSTAIN not in DEFAULT_MSG
    assert Action.SAY not in DEFAULT_MSG
