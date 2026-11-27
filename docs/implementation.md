# Implementation Notes (Python port)

The port is deliberately split into *data* and *engine*, mirroring Knuth's
separation between the cave tables and the simulation loop.

> **Status.** The port runs: `python -m advent --seed 7` plays a complete
> game in the terminal, and `python -m advent --gui` plays the same game in a
> tkinter window. `vocabulary.py` and `data.py` are verified against
> `advent.w` (all 140 locations, 740 travel instructions, 66 objects, 87
> notes, 14 remarks, 282 words, 13 messages match), and `rng.py`, `game.py`,
> `cli.py` and `__main__.py` implement the simulation, the terminal front end
> and the entry point. `scenes.py`, `art.py`, `session.py` and `gui.py` add the
> graphical front end. The test suite covers the vocabulary, the travel table,
> scripted games, the scene/art tables and the window bridge; a recorded
> 350-point walkthrough (`docs/walkthrough.md` and
> `tests/test_walkthrough.py`) is still to be written.

```text
advent/
  vocabulary.py   word types and meanings, the word table, default messages,
                  the fixed messages, and the enum classes (incl. Location)
  data.py         location texts/flags, travel table, object tables, notes,
                  remarks, hints, death/rank tables
  rng.py          Knuth's linear congruential generator
  game.py         the simulation: parser, actions, actors, clocks, scoring
  cli.py          terminal front end
  scenes.py       the scene/backdrop/prop table, item labels and exit labels
  art.py          procedural vector art: backdrops, props, item icons
  session.py      one Game in a worker thread, bridged by queues
  gui.py          tkinter window: canvas painter, object cards, verbs, exits
  __main__.py     python -m advent
tests/
  conftest.py           scripted console and fixtures
  test_vocabulary.py    words, enums, fixed and default messages
  test_travel.py        travel-table invariants and the quirky exits
  test_game.py          scripted games, death, closing, scoring
  test_scenes.py        scene/art coverage, labels, exit words, painters
  test_front_end.py     read-only engine views used by the GUI
  test_session.py       the worker-thread bridge
  test_gui.py           a real window (skipped without a display)
```

## Mapping from WEB to Python

| `advent.w` section | Python |
| --- | --- |
| `@* The vocabulary`, `new_word`, `lookup` | `vocabulary.py`: a plain `dict[str, Entry]` keyed by the first five letters. The C hash table is an implementation detail; a dict has exactly the same lookup semantics (`streq` compares five characters). |
| `@<Type definitions@>` enums | `enum.IntEnum` classes `Motion`, `Action`, `Object`, `Location`, `WordType`. |
| `@* Cave data`, `@<Build the travel table@>` | `data.py`: `LOCATIONS` (name, long/short text, flags) and `TRAVELS` (a flat list of `Instruction(mot, cond, dest)`), plus `START` indices. Keeping a flat list preserves the C behavior where the condition-advance loop can look at the next location's instructions. |
| `@* Data structures for objects` | `data.py`: `OBJECTS` (name, base, start, notes) and the note table; `game.py` keeps the mutable `place`, `prop`, `first`, `link`, `base`, `holding`. |
| `@<Subroutines@>` (`drop`, `carry`, `is_at_loc`, `yes`, `listen`, `ran`, `dwarf`, `offer`, `score`) | methods on `Game`; `ran` in `rng.py`. |
| `@* The main control loop` | `Game.play()`: an outer loop (major cycles) containing an inner loop (minor cycles). |
| `@<Get user input...@>` | `Game._input_phase()`: an explicit state machine with the same labels (`cycle`, `pre_parse`, `parse`, `branch`, `intransitive`, `transitive`, `speakit`, `report_default`, `get_object`, `cant_see_it`). |
| `goto try_move`, `goto quit`, `goto death`, `goto commence`, `goto dwarves_upset` | Python exceptions `_Motion`, `_Quit`, `_Death`, `_Commence`, `_DwarvesUpset`, caught by the loop that owns the corresponding label. |
| `printf` | `Console.write(text)`; `printf("%s\n", s)` becomes `self._line(s)` (the engine's tiny helper around `Console.write`). |

## The console abstraction

The engine never touches `stdin`/`stdout`. It is constructed with a
`Console`:

```python
class Console(Protocol):
    def write(self, text: str) -> None: ...      # exact text, no newline added
    def read_line(self, prompt: str) -> str: ...  # write prompt, read one line
```

`advent/cli.py` implements it with `sys.stdin.readline()` / `sys.stdout`
(so prompts are flushed before blocking); `tests/conftest.py` implements it
with a scripted list of answers and an output buffer. This keeps the engine
usable from any front end and makes scripted games testable.

## The graphical front end

`python -m advent --gui` starts `advent/gui.py`, which uses the same engine
through a different console implementation:

| Module | Role |
| --- | --- |
| `scenes.py` | The scene for every location (`Scene(backdrop, props, palette, seed)`), plus labels, icon names, command words, actor slots and exit labels. No tkinter import. |
| `art.py` | Procedural painters for 22 backdrops, 41 props and 52 item icons, all from `rect`/`oval`/`polygon`/`line`/`text` in a logical 1000×600 canvas. A `Painter` protocol separates the art from tkinter; the tests supply a recording painter. |
| `session.py` | Runs one `Game` in a worker thread. Output and prompts arrive as `Event`s on a queue, each prompt carrying a frozen `GameSnapshot`; `submit(line)` answers the pending prompt. No tkinter import. |
| `gui.py` | The window: a `CanvasPainter` over a tkinter `Canvas`, object cards, verb and exit buttons, a narration pane, a command entry, and Yes/No buttons. |

The engine gained four read-only views used only by front ends:
`here_objects()`, `inventory()`, `is_dark()` and `possible_motions()`.
The last one is deliberately not a call to the movement routine: that routine
consumes the random generator for percentage exits and prints failure
messages, so asking "which buttons should I draw?" would perturb the game.
`possible_motions()` evaluates object and property conditions, treats
percentage conditions as possible, and writes nothing.

The constructor normally asks the welcome question before returning. A window
must paint the opening scene before that question is answered, so the
constructor accepts `welcome=False`; `game.welcome()` then asks the question
and fixes the turn limit. The terminal front end uses the default single-step
construction and is unchanged.

The window never reads the live `Game` from its own thread. `EngineSession`
publishes a frozen `GameSnapshot` (location, light, objects here, inventory,
possible motions, turns, bottle and lamp state) with every prompt and with the
final event; the window paints only from that snapshot. This keeps the engine
thread the sole owner of the mutable object lists, even if a window resize or a
selection happens while a command is being processed.

The art is not a new source of game data: it only interprets the room text.
Every message, object placement, probability and score still comes from
`game.py` and `data.py`. See [gui.md](gui.md) for the screen layout, controls,
the scene model, and how to add a backdrop, prop or icon.

## Control flow

Knuth's program is a `goto`-heavy multistate simulation. Two mechanisms
replace the gotos:

1. **State machines** for the two big dispatch sections:
   * the input/action phase (`cycle → pre_parse → parse → branch →
     intransitive/transitive → report_default/get_object/cant_see_it`);
   * the movement phase (find instruction, test condition, skip equal
     instructions, handle special destinations).
2. **Exceptions** for the long jumps that cross the major-cycle boundary:
   * `_Motion(mot)` — `goto try_move`;
   * `_Commence` — `goto commence` (re-describe the current room);
   * `_Death` — `goto death` (resurrection flow);
   * `_DwarvesUpset` — `goto dwarves_upset` (prints and then ends the game);
   * `_Quit` — `goto quit` (the `give_up` path just sets `gave_up` and
     raises this too).

The outer loop is:

```text
while True:
    check interference with newloc
    loc = newloc
    move dwarves and pirate
    while True:                      # "commence"
        describe state
        while True:                  # minor cycles
            motion = input phase
            if motion: break
        handle special motions -> newloc
    oldoldloc, oldloc = oldloc, loc
    determine next location -> newloc
```

with the death handler re-entering at `commence` after a resurrection.

## Faithfulness decisions

* **Object order.** Objects are created from the highest number down, and
  `drop` pushes onto the front of a location list, so lists are in ascending
  object order. The Python data keeps that exact creation order.
* **Notes.** The note table and each object's `offset` are reproduced
  exactly, including shared offsets (two-part objects) and empty notes.
* **Travel-table quirks.** The "skip instructions with the same destination
  and condition" rule is implemented literally, which reproduces oddities
  such as `forward` crossing the fissure when the crystal bridge exists
  (its own instruction fails and the skip lands on the `over` instruction).
* **Random numbers.** `rng.py` is `rx = (1021*rx) & 0xfffff; return
  (range*rx) >> 20`, seeded from the clock or `--seed`. Every call site
  (including the "kick" `k = ran(0)` each turn) is in the same order as the
  original, so a fixed seed reproduces a complete game.
* **Prompts and text.** `* ` and `** ` prompts, the two-space sentence
  spacing, and the one message without a trailing newline (`Your lamp has
  run out of power.`) are preserved.
* **Undefined behavior.** `hash_table[k]` with `k == -1` (saying an unknown
  word) is treated as "no such word" and echoes, which is what the original
  intends; `incantation[k]` with an out-of-range index cannot happen because
  `FEEFIE` is only reachable from the five incantation words.
* **Input.** Lines are truncated to 71 characters (the C buffer is 72
  bytes including the NUL). EOF raises `EndOfInput`, which the CLI treats as
  `quit`.

## Deterministic testing

`Game(console, seed=...)` accepts an integer seed; `python -m advent --seed N`
passes one through. The suite in `tests/` uses a scripted console
(`tests/conftest.py`) and covers three levels:

* `test_vocabulary.py` — five-letter lookup, the enum values, and the fixed
  and default messages;
* `test_travel.py` — table invariants (sizes, the `start[ppass]` sentinel,
  destination and condition encodings) plus the quirky exits driven through
  the engine: the fissure, the plover-alcove passage, the troll bridge;
* `test_game.py` — scripted games (welcome, building, grate, magic words,
  `look`, `say`), death and resurrection, the closing cave, and the scoring
  formula.
* `test_scenes.py` — every location has a scene; every object has a label,
  icon and (where the vocabulary has one) a command word; every exit command
  parses back to its motion; every scene and icon paints; dark scenes are
  darker; palettes are complete.
* `test_front_end.py` — the read-only engine views, including that
  `possible_motions()` leaves the random generator and object lists untouched.
* `test_session.py` — the worker-thread bridge: starting, answering prompts,
  quitting and stopping.
* `test_gui.py` — a real tkinter canvas draws every scene and icon, and a real
  window plays a few moves. These tests skip when tkinter has no display.

Because the game is random, scripted games are only meaningful with a fixed
seed. A full 350-point walkthrough has not been recorded yet; when it is, it
belongs in `tests/test_walkthrough.py` together with
[walkthrough.md](walkthrough.md), which must name the seed it was recorded
with.

## What is intentionally *not* modeled

* Woods's prime-time closing logic (Knuth removed it).
* The binary obfuscation of the original FORTRAN version.
* The FORTRAN program's encryption of messages.
* Persistence; the port is stateless between runs, like the original.
* Photorealistic or hand-drawn artwork: the graphical front end generates its
  pictures procedurally from the room descriptions.
