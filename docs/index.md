# Adventure — Colossal Cave

A faithful Python re-creation of Don Knuth's CWEB version of **Adventure**
(Colossal Cave), the ur-text adventure game written by Will Crowther in
1975–76 and greatly extended by Don Woods in 1977.

The original source used here is [`knuth/advent.w`](../knuth/advent.w)
(CWEB, September 1998, revised March 1999). Knuth describes his program as
"entirely faithful to the behavior of Adventure Version 1.0", with slightly
edited messages and without Woods's prime-time cave-closing machinery and
binary obfuscation. This project ports that program to Python, one behavior
at a time, and documents the game completely.

> Copyright 1998 by Donald R. Woods and Donald E. Knuth. The original
> program and its text are theirs; this repository is a study port that
> reproduces the game for educational purposes. Do not redistribute the
> original `advent.w` without the authors' permission.

## The game in one paragraph

You are a lone adventurer at the end of a road in a forest, facing a small
brick building. Somewhere underground is Colossal Cave, a sprawling
natural cave system full of treasures, magic words, a lamp that runs down,
a thieving pirate, five knife-throwing dwarves, a troll who demands a toll,
a dragon, a bear, and — eventually — a cave that closes behind you. Your job
is to collect **fifteen treasures**, get them safely into the building, and
score as close to **350 points** as you can. You interact by typing one- or
two-word commands such as `take lamp`, `west`, `unlock grate`, or
`say xyzzy`.

## Documentation map

| Document | What it covers |
| --- | --- |
| [gameplay.md](gameplay.md) | How the game works: the two-word parser, movement, light, objects, dwarves, the pirate, hints, the closing cave, death, and scoring. |
| [world.md](world.md) | The map and the complete travel table: every location, every exit, every condition. |
| [rooms.md](rooms.md) | The full text of every room description, short and long. |
| [objects.md](objects.md) | Every object: names, starting places, movable/immovable groups, property values, and the messages tied to them. |
| [reference.md](reference.md) | The complete vocabulary (motions, objects, actions, magic words), default messages, hints, ranks, and scoring tables. |
| [walkthrough.md](walkthrough.md) | A full solution, including the 350-point "master's section" ending. |
| [implementation.md](implementation.md) | How the Python port is organized and how it maps onto Knuth's WEB sections. |

## Quick start (CLI)

```bash
python -m advent            # play, random seed from the clock
python -m advent --seed 7   # deterministic run (handy for scripted games)
```

Inside the game:

```text
* help          # general hints
* info          # how scoring and quitting work
* in            # enter the building, then the grate
* take lamp
* on
* west
* score
* quit
```

Words are case-insensitive, and only the first five letters matter, so
`northeast` is read as `north`; use `ne` for the diagonal. Commands are at
most two words, in either order (`take lamp` = `lamp take`).

## What is reproduced

* The complete 140-location cave, including the two mazes, the "all alike"
  twisty passages, the "all different" Latin-square maze, Witt's End,
  Bedquilt, the troll bridge, the hidden cave, and the two storage rooms.
* The complete ~300-word vocabulary, including `xyzzy`, `plugh`, `plover`,
  `y2`, the `fee fie foe foo` incantation, and all the odd synonyms.
* The travel table with probabilistic exits, conditional exits
  (carrying/locating an object, object property tests), forced moves, and
  the pseudo-locations that implement special effects.
* All object behavior: the bottle (water/oil), lamp and batteries, bird and
  cage, snake, dragon and rug, troll and bridge, bear/chain/axe, plant and
  beanstalk, vase and pillow, clam/oyster/pearl, vending machine, pirate
  and chest, and all fifteen treasures.
* The five dwarves and the pirate, including their random walks, the
  "little dwarf with a big knife", knife throws, and the escalating
  `dflag` anger level.
* The lamp budget, the dim-lamp warnings, battery replacement, and death
  from darkness.
* The eight hints, with their thresholds, costs, and score penalties.
* The closing of the cave (two clocks), the panic message, the storage-room
  finale, and the three dynamite endings.
* Death and resurrection (three lives), the scoring formula, the nine
  adventurer ranks, and the exact end-of-game report.

## Deliberate differences

The port aims to be behaviorally identical, not bug-identical. The small,
documented deviations are:

* **Determinism is available.** `--seed` pins the linear congruential
  generator; without it the seed comes from the clock, as in the original.
* **No undefined behavior.** A few places where the C original reads an
  array with `-1` (for example, saying an unknown word) are handled safely.
* **Input robustness.** EOF (Ctrl-D) ends the game cleanly instead of
  looping forever.
* **Output stream.** Messages are emitted through a small console
  abstraction so the same engine can later back a web or GUI front end.
  Prompt strings (`* `, `** `) and all message text are preserved exactly,
  including the original's occasional missing trailing newline.
* **Structure.** `goto`-based control flow is re-expressed as explicit
  state machines and exceptions; the game logic and table data are kept
  apart (`advent/data.py` vs. `advent/game.py`).

Everything else — including the exact wording of every message, the
probability constants, the object numbering, the order in which objects are
listed in a room, and the scoring quirks — follows `advent.w`.

## Repository layout

```text
README.md             project overview, status, and roadmap
knuth/advent.w        the original CWEB source (read-only reference)
docs/                 this documentation
advent/               the Python port
  vocabulary.py       enums (incl. Location), word table, default messages,
                      fixed messages
  data.py             location texts/flags, travel table, objects, notes,
                      remarks, hints, death/rank tables
  rng.py              Knuth's 1021·x mod 2^20 generator
  game.py             the engine (UI-independent)
  cli.py              terminal front end
  __main__.py         `python -m advent`
tests/                pytest suite (vocabulary, travel table, scripted games)
```

> **Status.** The game runs. `advent.w`'s tables are transcribed and
> machine-verified, the engine and CLI are complete, and the test suite
> passes. Still missing: a recorded 350-point walkthrough
> (`walkthrough.md` and `tests/test_walkthrough.py`). See
> [implementation.md](implementation.md).

## A note on the source's style

Knuth's program is a table-driven simulation: a list of instructions
`(motion, condition, destination)` per location, object lists threaded
through locations, and a main loop that alternates "major cycles" (you
move) with "minor cycles" (you act). The documentation below uses the same
vocabulary — location codes, motion words, properties, `dflag`, `tally`,
`clock1`/`clock2` — so that the docs can be read side by side with
`advent.w`.
