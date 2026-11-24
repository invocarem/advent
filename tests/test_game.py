"""Scripted games: the parser, the actions, and the end-of-game report."""

from __future__ import annotations

import pytest

from advent.game import _Death, _DwarvesUpset, _Motion, _Quit
from advent.vocabulary import INHAND, Action, Location, Motion, Object


# ---------------------------------------------------------------------------
# The opening moves
# ---------------------------------------------------------------------------


def test_quitting_on_the_first_turn_scores_32(scripted):
    _, text = scripted(["n", "quit", "y"])
    assert "Do you really want to quit now?" in text
    assert "You scored 32 points out of a possible 350, using 1 turn." in text
    assert "You are obviously a rank amateur.  Better luck next time." in text
    assert "To achieve the next higher rating, you need 4 more points." in text


def test_instructions_are_offered_and_extend_the_lamp(scripted):
    game, text = scripted(["y"])
    assert text.startswith("Welcome to Adventure!!  Would you like instructions?")
    assert "Somewhere nearby is Colossal Cave" in text
    assert game.hinted[0] is True
    assert game.limit == 1000

    game, _ = scripted(["n"])
    assert game.hinted[0] is False
    assert game.limit == 330


def test_the_building_and_its_contents(scripted):
    game, text = scripted(["n", "in", "take lamp", "take keys", "inventory", "quit", "y"])
    assert "You are inside a building, a well house for a large spring." in text
    assert "There is a shiny brass lamp nearby." in text
    assert "You are currently holding the following:" in text
    assert " Set of keys" in text
    assert " Brass lantern" in text
    assert game.loc == int(Location.HOUSE)
    assert game.place[int(Object.LAMP)] == INHAND


def test_two_word_commands_work_in_either_order(scripted):
    for words in (["take lamp"], ["lamp take"]):
        game, _ = scripted(["n", "in", *words, "quit", "y"])
        assert game.place[int(Object.LAMP)] == INHAND
        assert game.holding == 1


def test_unlocking_the_grate(scripted):
    game, text = scripted(
        ["n", "in", "take keys", "out", "s", "s", "s", "unlock grate", "enter", "quit", "y"]
    )
    assert "You are in a 20-foot depression floored with bare dirt." in text
    assert "The grate is locked." in text
    assert "The grate is now unlocked." in text
    assert "You are in a small chamber beneath a 3x3 steel grate" in text
    assert game.loc == int(Location.INSIDE)


def test_taking_something_you_already_have(scripted):
    _, text = scripted(["n", "in", "take lamp", "take lamp", "quit", "y"])
    assert "You are already carrying it!" in text


def test_unknown_word_is_reported(scripted):
    _, text = scripted(["n", "tickle", "quit", "y"])
    assert 'Sorry, I don\'t know the word "tickle".' in text


def test_three_word_command_is_rejected(scripted):
    _, text = scripted(["n", "take the lamp", "quit", "y"])
    assert " Please stick to 1- and 2-word commands." in text


def test_magic_words_teleport(scripted):
    game, _ = scripted(["n", "in", "plugh", "quit", "y"])
    assert game.loc == int(Location.Y2)
    game, _ = scripted(["n", "in", "xyzzy", "quit", "y"])
    assert game.loc == int(Location.DEBRIS)


def test_say_echoes_and_say_magic_word_moves_you(scripted):
    _, text = scripted(["n", "say hello", "quit", "y"])
    assert 'Okay, "hello".' in text
    game, _ = scripted(["n", "in", "say plugh", "quit", "y"])
    assert game.loc == int(Location.Y2)


def test_look_repeats_the_long_description(scripted):
    _, text = scripted(["n", "in", "look", "quit", "y"])
    assert "Sorry, but I am not allowed to give more detail." in text
    assert text.count("You are inside a building") == 2


# ---------------------------------------------------------------------------
# Death, resurrection and the closing cave
# ---------------------------------------------------------------------------


def test_death_then_resurrection_returns_you_to_the_building(make_game):
    game = make_game(["n", "y"])
    game.oldoldloc = int(Location.AWK)
    game.loc = int(Location.LIMBO)
    with pytest.raises(_Death):
        game._report_state()
    game._death()
    assert game.death_count == 1
    assert game.loc == int(Location.HOUSE)
    assert game.oldloc == int(Location.HOUSE)


def test_the_third_death_ends_the_game(make_game):
    game = make_game(["n", "y", "y", "y"])
    for i in range(3):
        game.loc = int(Location.LIMBO)
        with pytest.raises(_Death):
            game._report_state()
        if i < 2:
            game._death()
        else:
            with pytest.raises(_Quit):
                game._death()
    assert game.death_count == 3
    assert game._score() == 6  # 2 base + 4 for not giving up


def test_closing_warning_locks_the_grate(make_game):
    game = make_game()
    game.tally = 0
    game.clock1 = 1
    game.loc = int(Location.EMIST)
    game._check_clocks_and_lamp()
    assert game.clock1 == -1
    assert game._closing() is True
    assert game.prop[int(Object.GRATE)] == 0


def test_closing_moves_everything_to_the_storage_rooms(make_game):
    game = make_game()
    game.tally = 0
    game.clock1 = -1
    game.clock2 = 1
    game.loc = int(Location.EMIST)
    game.prop[int(Object.ROD2)] = 0
    with pytest.raises(_Motion) as jump:
        game._check_clocks_and_lamp()
    assert jump.value.mot == int(Motion.NOWHERE)  # stay_put
    assert game.closed is True
    assert game.loc == int(Location.NEEND)
    assert game.bonus == 10
    assert game.place[int(Object.ROD2)] == int(Location.SWEND)
    assert game.place[int(Object.LAMP)] == int(Location.NEEND)
    assert game.place[int(Object.GRATE)] == int(Location.SWEND)
    assert all(game.place[t] >= 0 for t in range(1, 67))


# ---------------------------------------------------------------------------
# Scoring
# ---------------------------------------------------------------------------


def test_score_counts_treasures_delivered_to_the_building(make_game):
    game = make_game()
    game.dflag = 1
    game.place[int(Object.GOLD)] = int(Location.HOUSE)
    game.prop[int(Object.GOLD)] = 0
    game.place[int(Object.MAG)] = int(Location.WITT)
    # 2 base + 25 deep + (2 seen + 10 delivered) + 30 deaths + 4 + 1 Witt's End
    assert game._score() == 74


def test_hints_cost_points(make_game):
    game = make_game(["y"])  # accepted the instructions, which cost 5 points
    assert game._score() == 2 + 30 + 4 - 5


def test_treasures_are_worth_more_above_the_chest(make_game):
    game = make_game()
    game.place[int(Object.CHAIN)] = int(Location.HOUSE)  # above the chest
    game.prop[int(Object.CHAIN)] = 0
    game.place[int(Object.COINS)] = int(Location.HOUSE)  # below the chest
    game.prop[int(Object.COINS)] = 0
    # 2 base + 2*(2 seen) + 10 (coins) + 14 (chain) + 30 deaths + 4
    assert game._score() == 64


# ---------------------------------------------------------------------------
# Individual actions, driven straight at the action dispatcher
# ---------------------------------------------------------------------------


def act(game, verb, obj, word1="", word2=""):
    """Run one transitive action and return the next parser state."""
    game.verb = verb
    game.obj = int(obj)
    game.word1 = word1
    game.word2 = word2
    game.console.output.clear()
    return game._do_transitive()


def test_taking_the_bird_with_the_rod_scares_it(make_game):
    game = make_game()
    game.loc = int(Location.BIRD)
    game._carry(int(Object.ROD))
    game._carry(int(Object.CAGE))
    game.prop[int(Object.BIRD)] = 0
    act(game, Action.TAKE, Object.BIRD)
    assert "disturbed and you cannot catch it" in game.console.text


def test_catching_the_bird_needs_the_cage(make_game):
    game = make_game()
    game.loc = int(Location.BIRD)
    game.prop[int(Object.BIRD)] = 0
    act(game, Action.TAKE, Object.BIRD)
    assert "You can catch the bird, but you cannot carry it." in game.console.text


def test_waving_the_rod_toggles_the_crystal_bridge(make_game):
    game = make_game()
    game.loc = int(Location.EFISS)
    game._carry(int(Object.ROD))
    game.prop[int(Object.CRYSTAL)] = 0
    act(game, Action.WAVE, Object.ROD)
    assert game.prop[int(Object.CRYSTAL)] == 1
    assert "A crystal bridge now spans the fissure." in game.console.text
    act(game, Action.WAVE, Object.ROD)
    assert game.prop[int(Object.CRYSTAL)] == 0
    assert "The crystal bridge has vanished!" in game.console.text


def test_the_vase_survives_only_the_pillow(make_game):
    game = make_game()
    # Dropping it in the Soft Room simply leaves it there, intact.
    game.loc = int(Location.SOFT)
    game._carry(int(Object.VASE))
    game.prop[int(Object.VASE)] = 0
    act(game, Action.DROP, Object.VASE)
    assert game.prop[int(Object.VASE)] == 0
    assert "OK." in game.console.text

    # Anywhere else it shatters and becomes immovable.
    game.loc = int(Location.COBBLES)
    game._carry(int(Object.VASE))
    act(game, Action.DROP, Object.VASE)
    assert game.prop[int(Object.VASE)] == 2
    assert game.base[int(Object.VASE)] == int(Object.VASE)
    assert "The Ming vase drops with a delicate crash." in game.console.text


def test_the_vase_rests_on_the_pillow_if_the_pillow_travels(make_game):
    # advent.w only prints the "resting on a velvet pillow" note when the
    # pillow is at the place where the vase is dropped.
    game = make_game()
    game.loc = int(Location.COBBLES)
    game._move(int(Object.PILLOW), int(Location.COBBLES))
    game._carry(int(Object.VASE))
    game.prop[int(Object.VASE)] = 0
    act(game, Action.DROP, Object.VASE)
    assert game.prop[int(Object.VASE)] == 0
    assert "The vase is now resting, delicately, on a velvet pillow." in game.console.text


def test_opening_the_clam_needs_the_trident(make_game):
    game = make_game()
    game.loc = int(Location.SHELL)
    act(game, Action.OPEN, Object.CLAM)
    assert "You don't have anything strong enough to open the clam." in game.console.text

    game._carry(int(Object.TRIDENT))
    act(game, Action.OPEN, Object.CLAM)
    assert game.place[int(Object.OYSTER)] == int(Location.SHELL)
    assert game.place[int(Object.PEARL)] == int(Location.SAC)


def test_throwing_a_treasure_to_the_troll_clears_the_bridge(make_game):
    game = make_game()
    game.loc = int(Location.SWSIDE)
    game._carry(int(Object.GOLD))
    act(game, Action.TOSS, Object.GOLD)
    assert game.place[int(Object.GOLD)] == int(Location.LIMBO)
    assert game.place[int(Object.TROLL)] == int(Location.LIMBO)
    assert "The troll catches your treasure and scurries away out of sight." in game.console.text


def test_feeding_the_bear_makes_it_friendly(make_game):
    game = make_game()
    game.loc = int(Location.BARR)
    game._carry(int(Object.FOOD))
    game.prop[int(Object.AXE)] = 1
    game.base[int(Object.AXE)] = int(Object.AXE)
    act(game, Action.FEED, Object.BEAR)
    assert game.prop[int(Object.BEAR)] == 1
    assert game.place[int(Object.FOOD)] == int(Location.LIMBO)
    assert game.prop[int(Object.AXE)] == 0
    assert game.base[int(Object.AXE)] == 0


def test_breaking_the_mirror_after_closing_upsets_the_dwarves(make_game):
    game = make_game()
    game.loc = int(Location.MIRROR)
    game.closed = True
    with pytest.raises(_DwarvesUpset):
        act(game, Action.BREAK, Object.MIRROR)


def test_fee_fie_foe_foo_moves_the_eggs(make_game):
    game = make_game()
    game.loc = int(Location.GIANT)
    game.place[int(Object.EGGS)] = int(Location.LIMBO)
    for i, word in enumerate(["fee", "fie", "foe", "foo"]):
        game.foobar = -i if i else 0
        game.verb = Action.FEEFIE
        game.k = 0
        game.word1 = word
        game.console.output.clear()
        assert game._do_intransitive() == "cycle"
    assert game.place[int(Object.EGGS)] == int(Location.GIANT)
