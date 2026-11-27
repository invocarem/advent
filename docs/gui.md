# The graphical front end

`python -m advent --gui` opens Adventure in a window instead of a terminal.
The game underneath is unchanged: the same 140 locations, the same objects,
the same parser and the same scoring. The window is a second way to read and
drive that engine, not a new game.

```bash
python -m advent --gui
python -m advent --gui --seed 7     # reproducible run
```

The front end is written with **tkinter**, which ships with CPython, so the
"no third-party runtime dependencies" rule still holds. On Linux distributions
that split tkinter into a separate system package, install `python3-tk`.

## What is on screen

```text
┌───────────────────────────────────────────────────────────────────────┐
│ New game  Look  Inventory  Score  Help  Brief  Quit       Turn 3 · Carrying 2 │
├───────────────────────────────────────────────┬───────────────────────┤
│                                               │ IN THIS PLACE         │
│   the scene for the current location          │  [icon] Set of keys   │
│   (vector art, drawn in code)                 │  [icon] Brass lantern │
│   with the objects that are here              │  …                    │
│                                               │ YOU ARE CARRYING      │
│                                               │  [icon] [icon] …      │
│                                               │ Selected: Brass lantern│
│                                               │ Take Drop Open Close  │
│                                               │ Light Out Wave Rub …  │
├───────────────────────────────────────────────┴───────────────────────┤
│ Look  N  NE  E  SE  S  SW  W  NW  Up  Down  In  Out  Building  Stream … │
├───────────────────────────────────────────────────────────────────────┤
│ narration: every line the engine prints, in order                     │
├───────────────────────────────────────────────────────────────────────┤
│ *  [ command entry ]  Send   Yes  No                                  │
└───────────────────────────────────────────────────────────────────────┘
```

* **Scene.** The current location painted from shapes: the road and brick
  building at the start, the well house, the grate, the Hall of Mists, the
  mazes, the reservoir, the volcano overlook, and so on. In a dark room the
  palette is dimmed and the objects are hidden, just as the engine hides them.
* **Objects.** Everything the engine lists at the location appears both in the
  scene and in the *In this place* panel. Creatures and scenery (dragon, troll,
  bear, snake, pirate, dwarf, plant, stalactite, bridge, mirror, mural, …) are
  painted large in the scene; portable objects are laid out along the floor
  (the first eight are drawn, and the panel lists every object in the room and
  scrolls if needed). The bottle's icon changes with water, oil or empty; a lit
  lamp glows.
* **Verbs.** Click an object to select it, then press a verb. The button sends
  the ordinary command, e.g. `take keys`, `fill bottle`, `wave rod`.
  Double-clicking an object takes it; double-clicking an inventory item drops
  it.
* **Exits.** The buttons are the motions the travel table could accept from
  here. They are only suggestions: the engine still decides whether a move
  works, and the original wording for failures still appears in the narration.
  The list is a heuristic — it does not reproduce the engine's fall-through
  from a failed conditional exit (at the locked grate, for example, it offers
  *Enter* rather than *Down*), so the command line remains the complete
  interface. The *Look* button always runs `look`.
* **Carrying.** The panel follows the engine's `INVENTORY` filter: parts of
  multipart objects and the bear (a follower) are not listed as carried.
* **Narration.** All engine output is reproduced verbatim in the pane, with
  prompts, typed commands and system notes styled differently. Long room
  descriptions, hint offers, dwarf fights, the closing cave and the final
  score all appear there.
* **Command entry.** The original two-word parser is still available: type
  `take lamp`, `ne`, `unlock grate`, `say xyzzy`, `score`, `quit`, and so on.
  Up/Down recall previous commands.
* **Yes/No.** The engine's yes/no questions (instructions, hints, quitting)
  show *Yes* and *No* buttons; typing `y` or `n` works too. The object and exit
  buttons are disabled while such a question is open, so a compass `N` button
  cannot be mistaken for a "No" answer.

Keyboard shortcuts on the scene: arrow keys move N/S/E/W, Shift+Up and
Shift+Down move up and down. The scene must have focus (click it once). While a
yes/no question is open, the arrow keys are ignored and the entry gets focus,
so they cannot answer the question by accident.

## How the picture layer is organised

The graphics are split into a toolkit-free data layer and a drawing layer, so
that they can be tested without a display and reused by another renderer.

| Module | Role |
| --- | --- |
| `advent/scenes.py` | The scene for every location: backdrop kind, painted props, palette, deterministic seed. Also item labels, icon names, command words, actor slots, and exit labels. |
| `advent/art.py` | Procedural painters: 22 backdrops, 41 props and 52 item icons, all drawn from rectangles, ovals, polygons and lines in a logical 1000×600 canvas. |
| `advent/session.py` | Runs one `Game` in a worker thread, publishes a frozen `GameSnapshot` with every prompt, and exchanges output, prompts and answers through queues. No tkinter import. |
| `advent/gui.py` | The tkinter window: canvas painter, object cards, verb and exit buttons, narration, command entry, yes/no buttons. |

### Scenes

A scene is a small frozen dataclass:

```python
Scene(backdrop="road", props=(Prop("house", 0.64, 0.64),), palette="surface", seed=1)
```

* `backdrop` names a painter in `art.BACKDROPS` (`road`, `forest`, `house`,
  `tunnel`, `crawl`, `hall`, `cavern`, `maze`, `canyon`, `water`, `chasm`,
  `volcano`, `deadend`, `shrine`, `soft`, `shell`, `void`, `sewer`, …).
* `props` are decorations placed at fractional coordinates: trees, stream,
  stairs, pit, crack, mist, waterfall, oil pool, sign, mural, curtains,
  light shaft, and so on.
* `palette` selects one of `art.PALETTES` (`surface`, `house`, `cave`, `warm`,
  `water`, `soft`, `shrine`, `volcano`, `void`); a dark room is the same
  palette multiplied down and overlaid with a vignette.
* `seed` drives the small random details (rock cracks, speckles) so a room
  looks the same every time you visit it.

All 140 locations, plus the engine's `in hand` and `limbo` pseudo-locations,
have a scene. `scenes.scene_for(loc)` falls back to a plain tunnel if a future
engine ever reports an unknown location.

### Icons

`scenes.ITEM_ICONS` maps every one of the 66 objects to an icon painter;
`scenes.ITEM_LABELS` gives names to the objects the engine leaves unnamed
because its notes describe them (grate, door, plant, mirror, dragon, …).
`scenes.ITEM_WORDS` maps an object to a word the original parser accepts, so a
button can send a command for it. A few scenery parts (the two treads objects)
have no vocabulary word; their verb buttons are disabled rather than sending
an unknown word.

`scenes.ACTOR_SLOTS` says which objects are painted large in the scene instead
of in the item row. Everything else the engine lists at the location is laid
out in up to two rows along the floor, in the engine's own list order.

### The engine stays authoritative

The engine gained four small read-only views for front ends:

* `here_objects()` — the objects in the current room, in list order;
* `inventory()` — the objects being carried;
* `is_dark()` — the engine's lighting test;
* `possible_motions()` — the motion words worth offering from here.

`possible_motions()` deliberately does **not** call the movement routine: that
routine consumes the random generator for percentage exits and prints failure
messages, which would change the game just by drawing buttons. It evaluates
object and property conditions, treats percentage conditions as possible, and
writes nothing. A test asserts that it leaves the generator, object lists and
player state untouched.

The engine's constructor normally asks the welcome question before returning.
A front end needs a fully built game *before* that question so it can paint the
opening scene, so `Game(..., welcome=False)` builds the state and a separate
`game.welcome()` asks the question. The terminal front end keeps the original
single-step construction.

## Faithfulness

* All message text, prompts, object names and room descriptions come from the
  engine unchanged and appear in the narration pane.
* The pictures are an interpretation of the room descriptions. Where a room
  says "a splendid chamber thirty feet high" or "the walls are frozen rivers
  of orange stone", the scene uses an orange-stone palette and tall columns;
  it does not claim to be an authoritative illustration.
* The exit buttons are a convenience layer. They list motions that *could*
  apply; the engine may still refuse the move, with its original message.
* No game rule, probability, object placement or scoring detail is changed by
  the front end.

## Adding art

To give a location a new look, edit its entry in `scenes.SCENES`:

```python
int(Location.HALL): _scene(
    "hall",
    _p("stairs", 0.82, 0.74, 0.9),
    _p("mist", 0.5, 0.68, 1.0),
    seed=15,
),
```

To add a new prop, write a painter in `art.py` with the signature
`(painter, palette, prop)` and register it in `art.PROPS`. To add a new item
icon, write `(painter, cx, cy, size, state)` and register it in `art.ICONS`,
then point the object at it in `scenes.ITEM_ICONS`. The tests check that every
backdrop, prop, palette and icon named by the scene table exists.

The drawing API is intentionally tiny — `rect`, `oval`, `polygon`, `line`,
`text` — with logical coordinates. `gui.CanvasPainter` scales them to the
window; the tests use a recording painter that checks coordinates and colours.

## Tests

* `tests/test_scenes.py` — every location has a scene; every object has a
  label, icon and (where the vocabulary has one) a command word; every exit
  command parses back to its motion; every scene and icon paints; dark scenes
  are darker; palettes are complete.
* `tests/test_front_end.py` — the read-only engine views, and that
  `possible_motions()` does not consume the random generator or mutate state.
* `tests/test_session.py` — the worker-thread bridge, including starting,
  answering prompts, quitting and stopping.
* `tests/test_gui.py` — a real tkinter window: every scene and icon is drawn on
  a canvas, then the window plays a few moves. These skip when tkinter has no
  display.

> **A tkinter/pytest quirk.** On Windows, creating and destroying a Tk root
> during pytest collection can leave Tcl unable to read its own library files
> later in the same process. The GUI tests therefore create their root lazily
> inside each test, and suspend pytest's file-descriptor capture while the
> window exists.
