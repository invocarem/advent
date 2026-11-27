# Adventure — Colossal Cave (Python port)

A study port of Don Knuth's CWEB implementation of **Adventure** (Colossal
Cave): the ur-text adventure game written by Will Crowther in 1975–76,
greatly extended by Don Woods in 1977, and rewritten in literate form by
Knuth in September 1998 (revised March 1999).

The source of truth is [`knuth/advent.w`](knuth/advent.w). Knuth describes
his program as "entirely faithful to the behavior of Adventure Version 1.0",
with slightly edited messages and without Woods's prime-time cave-closing
machinery and binary obfuscation. This project ports that program to Python
one behaviour at a time, and documents the game completely in [`docs/`](docs/index.md).

The aim is **behavioural fidelity, not bug fidelity**: the same 140
locations, the same 740-instruction travel table, the same message texts
(including the one message with no trailing newline), the same object
numbering, and the same scoring quirks.

## Status

| Part | State |
| --- | --- |
| `advent/vocabulary.py` — word types, word table, fixed and default messages | **done** |
| `advent/data.py` — locations, travel table, objects, notes, remarks, hints, ranks | **done** |
| `advent/rng.py` — Knuth's generator | **done** |
| `advent/game.py` — parser, actions, actors, clocks, death, scoring | **done** |
| `advent/cli.py`, `advent/__main__.py` — front end and entry point | **done** |
| `advent/scenes.py`, `advent/art.py` — scene table and procedural vector art | **done** |
| `advent/session.py`, `advent/gui.py` — tkinter graphical front end | **done** |
| `tests/` — pytest suite | **done** |
| `tests/test_walkthrough.py`, `docs/walkthrough.md` — recorded 350-point game | **not written yet** |

Both data modules have been machine-diffed against `advent.w` and match
exactly: 140 locations (long/short text and flags), 740 travel instructions
(motion, condition, destination), 66 objects (name, base, start), 87 notes,
14 remarks, 13 fixed messages, the 28 action default messages, and 283 word
entries (282 distinct five-letter keys). The engine reproduces the original's
prompts, message texts, object lists and scoring; see
[docs/implementation.md](docs/implementation.md).

## Requirements

* **Python 3.10+** (developed and checked on 3.11)
* **No third-party runtime dependencies** — the game and both front ends are
  standard library only. The graphical front end uses **tkinter**; on Linux
  distributions that split it out, install `python3-tk`.
* `pytest` for the test suite: `pip install -r requirements.txt`

## Quick start

```bash
git clone <this-repo> && cd advent
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt

python -m advent                   # play in the terminal (seed from the clock)
python -m advent --seed 7          # reproducible run
python -m advent --gui             # play in a graphical window
python -m advent --gui --seed 7    # reproducible graphical run
python -m pytest -q                # run the test suite
```

Commands are one or two words (`take lamp`, `lamp take`), only the first five
letters of each word matter, and `help` / `info` / `score` / `quit` do what
you would expect.

## Graphical front end

`python -m advent --gui` opens the same game in a tkinter window. The current
location is drawn as a scene (the road and brick building, the well house, the
grate, the Hall of Mists, the mazes, the reservoir, the volcano overlook, …),
the objects in the room are pictures you can click, and the exit bar offers the
directions that could work from here. Selecting an object enables verbs that
send the original commands (`take keys`, `fill bottle`, `wave rod`), while the
command entry still accepts the full two-word vocabulary. Every line the engine
prints appears in the narration pane, including the final score.

The pictures are generated in code — no image files and no third-party
libraries — and the engine is untouched: all messages, rules, probabilities,
object numbering and scoring quirks are still the original ones. See
[docs/gui.md](docs/gui.md) for the layout, controls and how to add art.

## Layout

```text
knuth/advent.w   the original CWEB source (read-only reference)
advent/          the Python port
  vocabulary.py  enums, word table, default and fixed messages
  data.py        locations, travel table, objects, notes, remarks, hints, ranks
  rng.py         Knuth's 1021·x mod 2^20 generator
  game.py        the engine, UI-independent
  cli.py         terminal front end
  scenes.py      the scene for every location, item labels, exit labels
  art.py         procedural vector art (backdrops, props, item icons)
  session.py     engine thread + input/output queues for the GUI
  gui.py         tkinter graphical front end
  __main__.py    `python -m advent`
docs/            the documentation
tests/           pytest suite (vocabulary, travel table, scripted games,
                 scenes/art coverage, the session bridge, a GUI smoke test)
```

## Roadmap

Done:

1. `advent/rng.py` — Knuth's generator, seeded from the clock or `--seed`.
2. `advent/game.py` — the engine: input state machine, travel-table
   resolution, verbs, dwarves/pirate, hints, clocks, death, scoring.
3. `advent/cli.py` + `__main__.py` — console front end and entry point.
4. `tests/` — table tests plus scripted games.
5. `advent/scenes.py` + `advent/art.py` — a scene and procedural art for every
   location, and an icon for every object.
6. `advent/session.py` + `advent/gui.py` — tkinter graphical front end
   (`python -m advent --gui`), with clickable objects, verbs and exits.

Still open:

7. `tests/test_walkthrough.py` + `docs/walkthrough.md` — a recorded
   350-point game (with the seed it was recorded at).

## Documentation

| Document | What it covers |
| --- | --- |
| [docs/index.md](docs/index.md) | Overview, what is reproduced, and the deliberate differences. |
| [docs/gameplay.md](docs/gameplay.md) | How the game behaves: parser, movement, light, objects, dwarves, the pirate, hints, the closing cave, death, scoring. |
| [docs/world.md](docs/world.md) | The map and the complete travel table: every location, exit, condition, and remark. |
| [docs/rooms.md](docs/rooms.md) | The full text of every room description, long and short. |
| [docs/objects.md](docs/objects.md) | Every object: names, starting places, groups, property values, messages. |
| [docs/reference.md](docs/reference.md) | Vocabulary, default messages, hints, ranks, scoring tables, constants. |
| [docs/gui.md](docs/gui.md) | The graphical front end: layout, controls, the scene/art model, and how to add art. |
| [docs/implementation.md](docs/implementation.md) | How the port is organised and how it maps onto Knuth's WEB sections. |

## Deliberate differences from the original

* **Determinism is available.** `--seed` pins the linear congruential
  generator; without it the seed comes from the clock, as in the original.
* **No undefined behaviour.** A few places where the C original reads an
  array with `-1` (for example, saying an unknown word) are handled safely.
* **Input robustness.** EOF (Ctrl-D) ends the game cleanly instead of
  looping forever.
* **Output stream.** Messages go through a small console abstraction, so the
  same engine backs both the terminal and the tkinter front end; prompt
  strings and message text are preserved exactly.
* **A graphical front end.** `python -m advent --gui` draws each location and
  the objects in it as vector pictures, and offers clickable verbs and exits.
  The pictures are an interpretation of the room descriptions; the engine, its
  messages, rules and scoring are unchanged. The terminal remains the default.
* **Structure.** `goto`-based control flow is re-expressed as explicit state
  machines and exceptions, and the table data is kept apart from the engine.

## Copyright

Copyright 1998 by Donald R. Woods and Donald E. Knuth. The original program
and its text are theirs; this repository is a study port that reproduces the
game for educational purposes. Do not redistribute `knuth/advent.w` without
the authors' permission.
