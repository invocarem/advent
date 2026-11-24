# Gameplay

This is a complete description of how the game behaves, in the order the
program itself thinks about it: input, movement, sight, objects, actors,
hints, the clock, death, and score. Constants are given as they appear in
`knuth/advent.w`.

---

## 1. The command language

### One or two words

A command is one or two words separated by whitespace. Anything longer is
rejected with:

```text
 Please stick to 1- and 2-word commands.
```

An empty line gets:

```text
 Tell me to do something.
```

Words are lowercased, and **only the first five characters are used**.
`northeast` is read as `north`; the game only knows `ne` for the diagonal.
`xyzzy` is stored as `xyzzy`; longer words such as `treasure` become
`treas`. This is not a limit of the Python port — it is the original
behavior, and the game's own instructions warn about it.

### Four kinds of words

The vocabulary is a hash table of about 300 five-character strings. Each
entry has a type and a meaning:

| Type | Meaning | Example |
| --- | --- | --- |
| `motion` | a direction, a place, or a special travel verb | `north`, `enter`, `xyzzy`, `depression`, `back` |
| `object` | a thing | `lamp`, `grate`, `rod`, `bird` |
| `action` | a verb | `take`, `drop`, `unlock`, `wave`, `blast` |
| `message` | prints a fixed text | `help`, `info`, `tree`, `lost` |

### Parsing rules

The parser keeps a verb, an object, and a motion. The loop is:

1. A **motion word** immediately ends the action phase and starts a move.
   A motion overrides any verb or object already entered.
2. An **object word** sets the object. If a verb is already known, the
   action runs immediately; otherwise the game asks
   `What do you want to do with the <word>?` and keeps reading.
3. An **action word** sets the verb. If an object is already known, the
   action runs immediately; if not, the game asks `<Verb> what?` and keeps
   reading. (`Take` is capitalized as typed by the program: the first
   letter of your word is uppercased in the question.)
4. A **message word** prints its fixed text and ends the turn.

The two words may be given in either order: `take lamp` and `lamp take` are
the same command. If a word is unknown:

```text
Sorry, I don't know the word "tickle".
```

### Special cases

* `say <word>`: if a second word is present, it is re-parsed as a command,
  which is why `say plugh` and `say xyzzy` work as magic words. With one
  word, `say hello` echoes `Okay, "hello".` If you type just `say`, the game
  asks `Say what?`, and your next single word is echoed.
* `enter water` or `enter stream`: if there is water at your location you
  are told `Your feet are now wet.`, otherwise the game falls back to the
  default for `go`.
* `water plant`, `oil plant`, `water door`, `oil door`: the second word is
  treated as the verb `pour` when the named object is at your location.
* After you have typed `west` ten times, the game remarks once:
  `If you prefer, simply type W rather than WEST.`

### Answering questions

Hints, resurrection, and quitting ask yes/no questions. The prompt is
`** `, and the answer must start with `y` or `n`; anything else gets
` Please answer Yes or No.` and the question repeats.

---

## 2. Moving

### Major and minor cycles

The program alternates two kinds of turn:

* **Minor cycle** — you perform an action; you stay in the same place and
  are told the result.
* **Major cycle** — you give a motion; you move (or fail to move) and the
  game describes where you are.

After every command the dwarves get to move, the lamp burns one unit, and
the clocks may tick. `turns` counts every command you give, including
questions and the ones that fail.

### The travel table

Every location has a list of instructions:

```text
(motion, condition, destination)
```

To move, the game finds the first instruction whose motion matches your
word and whose condition is satisfied. Conditions are:

| Condition | Meaning |
| --- | --- |
| `0` | always true |
| `1..99` | true with that percentage probability |
| `100` | always true — and **forbidden to dwarves** (they may not use this exit) |
| `100+o` | you must be carrying object `o` |
| `200+o` | object `o` must be at your location |
| `300+o+100k` | property of object `o` must **not** be `k` |

A failed condition moves to the next instruction; consecutive instructions
with the same destination *and* the same condition are skipped together.
This is how messages like "You can't go through a locked steel grate!" are
reached only when the alternative fails.

The destination is either a location, a **pseudo-location** (special code),
or a **remark** (a message printed while you stay where you are). There are
fourteen remarks, reused by several exits.

If no instruction matches:

* `crawl` with no direction → `Which way?`
* `xyzzy` or `plugh` in the wrong place → `Nothing happens.`
* `find`/`inventory` used as a motion → the "I can only tell you what you
  see" message
* `in`/`out` → `I don't know in from out here.  Use compass points or name something in the general direction you want to go.`
* `forward`/`left`/`right` → `I am unsure how you are facing.  Use compass points or nearby objects.`
* other directions → `There is no way to go in that direction.`
* anything else → `I don't know how to apply that word here.`

### Magic words

| Word | Effect |
| --- | --- |
| `xyzzy` | From the building, teleports you to the debris room; from the debris room, to the building. It works from nowhere else. |
| `plugh` | From the building, to room Y2; from Y2, to the building. |
| `plover` | From Y2, to the Plover Room — **but if you carry the emerald, it is silently dropped first**. From the Plover Room, back to Y2. |
| `y2` | A motion word in its own right: from the Hall of Mists it goes to the jumble of rock, and elsewhere it behaves as a normal place word. |

The two magic words are written on the walls of the rooms that use them:
`MAGIC WORD XYZZY` in the debris room, and a large "Y2" on a rock in room
Y2. A hollow voice occasionally says `PLUGH` in room Y2.

### Special motion words

* `back` / `return` / `retreat`: try to undo your last move. The game looks
  for any instruction from your current location to the previous one, or
  through a one-step pseudo-location. If it cannot find one:
  `You can't get there from here.` If there is no remembered move:
  `Sorry, but I no longer seem to remember how you got here.`
* `look` / `examine` / `touch` / `describe`: print the full description of
  where you are. The first three looks in a row add
  `Sorry, but I am not allowed to give more detail.  I will repeat the long description of your location.`
  Looking is safe in the dark: it pretends it was not dark.
* `cave`: above ground you are told that no stream can run on the surface
  for long and that you should try the stream; inside, the game says
  `I need more detailed instructions to do that.`

### Forced moves

Some destinations are *pseudo-locations*: `crack`, `neck`, `lose`, `cant`,
`climb`, `check`, `snaked`, `thru`, `duck`, `sewer`, `upnout`, `didit`. They
are not places you can explore. Arriving at one prints its message and
immediately forces another move:

| Pseudo-location | Message | Ends up |
| --- | --- | --- |
| `crack` | The crack is far too small for you to follow. | small pit (`spit`) |
| `neck` | You are at the bottom of the pit with a broken neck. | death |
| `lose` | You didn't make it. | death |
| `cant` | The dome is unclimbable. | Hall of Mists |
| `climb` | You clamber up the plant and scurry through the hole at the top. | narrow corridor |
| `check` | (conditional) | west pit or Twopit Room |
| `snaked` | You can't get by the snake. | Hall of the Mountain King |
| `thru` | You have crawled through a very low wide passage parallel to and north of the Hall of Mists. | west end of Hall of Mists |
| `duck` | (same text as `thru`) | west side of the fissure |
| `sewer` | The stream flows out through a pair of 1-foot-diameter sewer pipes. It would be advisable to use the exit. | building |
| `upnout` | There is nothing here to climb. Use "up" or "out" to leave the pit. | west pit |
| `didit` | You have climbed up the plant and out of the pit. | Twopit Room |

Three more "destinations" are pure code:

* `ppass` — the tight Plover/alcove tunnel. It only lets you through if you
  are carrying nothing, or carrying exactly the emerald:
  `Something you're carrying won't fit through the tunnel with you. You'd best take inventory and drop something.`
* `pdrop` — used by the word `plover` when you carry the emerald: the
  emerald is quietly dropped, then the normal `plover` instruction runs.
* `troll` — crossing the troll bridge (see §6).

---

## 3. Seeing, light, and the lamp

A location is either lit (`lighted` flag) or dark. In a dark place you see
only:

```text
It is now pitch dark.  If you proceed you will most likely fall into a pit.
```

The lamp is a brass lantern found in the building. Its `prop` is 0 (off) or
1 (on). Turning it on sets `prop[LAMP]=1`; if you were in the dark, the room
is described again immediately. Turning it off in a dark place repeats the
pitch-dark warning.

### Lamp budget

`limit` is the lamp's remaining life, counted in commands:

* `330` if you declined the welcome instructions, `1000` if you asked for
  them.
* Every command with the lamp on costs 1.
* Accepting a hint adds `30 × (hint cost)` to the limit, if the limit is
  above 30.

Warnings and replacements:

* At `limit ≤ 30`, if fresh batteries are present and the lamp is present,
  the batteries are installed automatically:
  `Your lamp is getting dim.  I'm taking the liberty of replacing the batteries.`
  The limit is reset to **2500**.
* At `limit ≤ 30` with no usable batteries, a one-time warning explains
  whether you are out of spares, should find the vending machine, or should
  go back for the batteries.
* At `limit == 0` the lamp goes out: `Your lamp has run out of power.`
  (In the original this message has no trailing newline, and the port keeps
  that quirk.)
* Below zero while outside the cave, the game ends:
  `There's not much point in wandering around out here, and you can't explore the cave without a lamp.  So let's just call it a day.`

Fresh batteries come from a vending machine in the maze of twisty little
passages; drop coins there and get batteries. Used batteries can be
replaced only once (`prop[BATTERIES]` becomes 1).

### Falling in the dark

If it is dark and you were already in the dark on your previous command,
there is a 35% chance each turn that you fall and die:

```text
You fell into a pit and broke every bone in your body!
```

`look` is exempt. Death handling is described in §9.

---

## 4. Objects

### Movable and immovable

Every object has a *base*. `base[t] == 0` means the object can be carried.
`base[t] != 0` means it is part of an immovable group, and `base[t]` is the
lowest-numbered object of the group. Groups in the game:

| Group | Parts | Where |
| --- | --- | --- |
| grate | `GRATE`, `GRATE_` | outside / inside the cave mouth |
| steps | `TREADS`, `TREADS_` | small pit / Hall of Mists |
| crystal bridge | `CRYSTAL`, `CRYSTAL_` | east / west side of the fissure |
| door | `DOOR` | immense passage |
| snake | `SNAKE` | Hall of the Mountain King |
| plant | `PLANT` | west pit |
| beanstalk | `PLANT2`, `PLANT2_` | Twopit Room / east pit |
| stalactite | `STALACTITE` | top of stalactite |
| shadow | `SHADOW`, `SHADOW_` | east / west window |
| axe | `AXE` | dropped by a dwarf |
| drawing | `ART` | Oriental Room |
| pirate | `PIRATE` | limbo |
| dragon | `DRAGON`, `DRAGON_` | secret canyon (east/west) |
| rug | `RUG`, `RUG_` | dragon's room |
| bridge | `BRIDGE`, `BRIDGE_` | troll chasm (southwest/northeast) |
| troll | `TROLL`, `TROLL_` | troll chasm |
| absent troll | `TROLL2`, `TROLL2_` | limbo |
| bear | `BEAR` | barren room |
| message | `MESSAGE` | limbo until the pirate is seen |
| geyser | `GEYSER` | breath-taking view |
| vending machine | `PONY` | dead end off the Latin-square maze |
| moss | `MOSS` | Soft Room |
| mirror | `MIRROR`, `MIRROR_` | mirror canyon / limbo |
| golden chain | `CHAIN` | barren room |

Groups are used by `is_at_loc`: an exit that tests "is the snake here" is
true if any part of the snake group is at your location.

### Properties and messages

Each object has a `prop` value. Treasures start at `-1` ("not yet seen");
everything else starts at 0. When you first see a treasure its prop becomes
0 (or 1 for the rug and chain, a scoring hack), `tally` drops by one, and
the object's message for that property value is printed. Objects print
`note[prop + offset]`, so property values select different descriptions.

Examples:

* Bottle: 0 = bottle of water, 1 = empty, 2 = bottle of oil, −2 = the
  bottle was reset when the cave closed.
* Lamp: 0 = off, 1 = on.
* Vase: 0 = intact, 1 = resting on a velvet pillow, 2 = shattered.
* Plant: 0 tiny, 1 spurting, 2 twelve feet tall, 3 explosive growth,
  4 gigantic, 5 shrivelling (the program cycles 0 → 2 → 4 → 0 when you
  water it).
* Bear: 0 ferocious, 1 gentle (fed), 2 contented (chain unlocked),
  3 dead (bridge collapse).
* Dragon: 0 alive, 1 killed by hand, 2 dead.
* Troll: 0 present, 1 paid/crossed, 2 gone.

### Taking and carrying

* You may carry at most **7** objects (counting the bird and cage as two,
  and the water or oil inside the bottle as one). The eighth gives:
  `You can't carry anything more.  You'll have to drop something first.`
* Immovable objects answer with `You can't be serious!`, or with a
  specialized line: the chain is still locked, the bear is still chained to
  the wall, the plant's roots are too deep.
* Taking the bird takes the cage too, and vice versa, when the bird is in
  the cage. A bird on the ground cannot be caught while you carry the rod
  (`The bird was unafraid when you entered, but as you approach it becomes disturbed and you cannot catch it.`),
  and without the cage you can catch it but not carry it.
* Taking water or oil requires a bottle; with an empty bottle you
  automatically switch to `fill`.
* Taking the bottle also takes its contents; dropping it leaves the liquid
  behind (the liquid is destroyed).

### The bottle

`prop[BOTTLE]`: 0 = water, 1 = empty, 2 = oil. Water and oil exist only as
contents of the bottle or as features of a location (`liquid` and `oil`
flags). You can:

* `fill` the bottle at any place with water or oil (the oil pool is at the
  bottom of the east pit);
* `pour` water or oil: on the plant in the west pit, or on the rusty iron
  door in the immense passage. Water on the door rusts it shut; oil frees
  it. Pouring elsewhere just empties the bottle and wets the ground.
* `drink`: drinks from the bottle if it holds water; otherwise, if you are
  at a water location, you drink from the stream (`The water tastes strongly of minerals, but is not unpleasant.  It is extremely cold.`).
* `fill vase` (anywhere with liquid) shatters the vase: a nasty surprise.

### The treasures

There are fifteen treasures, in object order:

| # | Object | Name | Where found |
| --- | --- | --- | --- |
| 1 | `GOLD` | Large gold nugget | nugget of gold room |
| 2 | `DIAMONDS` | Several diamonds | west side of fissure |
| 3 | `SILVER` | Bars of silver | low N/S passage |
| 4 | `JEWELS` | Precious jewelry | south side chamber |
| 5 | `COINS` | Rare coins | west side chamber |
| 6 | `CHEST` | Treasure chest | pirate's chest (in a maze) |
| 7 | `EGGS` | Golden eggs | Giant Room |
| 8 | `TRIDENT` | Jeweled trident | cavern with waterfall |
| 9 | `VASE` | Ming vase | Oriental Room |
| 10 | `EMERALD` | Egg-sized emerald | Plover Room |
| 11 | `PYRAMID` | Platinum pyramid | Dark-Room |
| 12 | `PEARL` | Glistening pearl | inside the clam (appears in the cul-de-sac) |
| 13 | `RUG` | Persian rug | under the dragon |
| 14 | `SPICES` | Rare spices | chamber of boulders |
| 15 | `CHAIN` | Golden chain | barren room |

Objects below the chest in number are worth 12 points each when delivered;
the chest is worth 14; objects above the chest are worth 16 each. See §10.

The gold nugget is too heavy to carry up the stairs from the Hall of Mists
(`You won't get it up the steps`), so it must leave by the crack route or
the plant route.

---

## 5. Dwarves and the pirate

### `dflag` — how angry the dwarves are

Five dwarves roam the cave. They are dormant until you reach the Hall of
Mists or deeper (`loc >= emist`), at which point `dflag` becomes 1 — this
also earns the "well into cave" 25 points.

* `dflag == 1`: each turn there is a 5% chance the dwarves wake up. When
  that happens, 0–2 dwarves are silently killed, any dwarf in your room is
  moved to the gold nugget room, and one dwarf runs by and throws an axe at
  you (it misses). The axe lands in your room and is a usable weapon.
* `dflag >= 2`: every turn each living dwarf takes a random step. A dwarf
  who has seen you follows you. Dwarves never enter the all-different maze
  (`condition 100` exits are closed to them) and never go past `dead2`.
* A dwarf who was already in your room (or who walks in) is threatening.
  If a knife has been thrown before, he may throw again:
  `There is a threatening little dwarf in the room with you!`
  or `There are N threatening little dwarves in the room with you!`
  followed by the knife throw. The chance to hit is `9.5% × (dflag − 2)`
  per knife, so `dflag` 3 = 9.5%, 4 = 19%, 5 = 28.5%, and so on.
* A dwarf who has seen you and came from the direction you are trying to
  go blocks you: `A little dwarf with a big knife blocks your way.`
* Throwing the axe at a dwarf hits with probability 2/3. A hit kills him
  (`You killed a little dwarf.  The body vanishes in a cloud of greasy black smoke.`
  for the first one). The axe stays where you are and can be reused.
* Feeding a dwarf is a bad idea: `You fool, dwarves eat only coal!  Now you've made him REALLY mad!`
  (this increments `dflag`).

### The pirate

The pirate is `dwarf[0]`. He starts at the chest's hiding place (`dead2`, in
the all-different maze) and walks like a dwarf, but he is after your
treasures:

* If you are carrying any treasure (except the platinum pyramid when you
  are in the Plover Room or Dark-Room, which is "too easy"), and you are not
  at `dead2`, and the chest has not been found, the pirate pounces:
  `Out from the shadows behind you pounces a bearded pirate!  "Har, har," he chortles, "I'll just take all this booty and hide it away with me chest deep in the maze!"  He snatches your treasure and vanishes into the gloom.`
  He takes every treasure in the room and every treasure you carry, and
  hides them all in the chest.
* Before he is spotted, the chest is in limbo and you get occasional
  `There are faint rustling noises from the darkness behind you.` warnings
  (20% chance when he moves).
* You spot him when you have seen every treasure except the chest
  (`tally == lost_treasures + 1`), there is no treasure in your current
  room, you have a working lamp with you, and he has not been spotted yet.
  He then announces `"Shiver me timbers!"` and vanishes, leaving the chest
  and a message in the maze:
  `This is not the maze where the pirate leaves his treasure chest.`
  (written in the dust at the dead end `pony`).
* Once the chest has been found (`prop[CHEST] >= 0`) the pirate stops
  robbing you.
* Two treasures can be permanently lost: if you drop the bird into the
  dragon's room (or kill the bird) while the snake is still in the Hall of
  the Mountain King, the snake can never be driven away, so the jewels are
  unreachable; and if the bear falls into the chasm, the spices and chain
  are lost. These count in `lost_treasures`, which lets the lamp be cut to
  35 turns once nothing more can be found.

---

## 6. Set pieces

### The grate

The steel grate at the cave mouth is locked (`prop[GRATE] == 0`). With the
keys you can `unlock grate`; from outside, `enter` then takes you in.
Once the cave starts closing, the grate is locked again and cannot be
unlocked; `panic` mode gives you 15 more turns.

### The fissure and the crystal bridge

The Hall of Mists is split by a fissure. At either side you can `wave rod`
(the black rod with the rusty star, found in the debris room). Each wave
toggles the crystal bridge (`prop[CRYSTAL]`): 0 → 1 creates it, 1 → 0 makes
it vanish. Waving the rod anywhere else gives the default wave message.
Crossing without the bridge is fatal (`You didn't make it.`). Waving fails
once the cave is closing.

### The snake

A green snake blocks the three side passages of the Hall of the Mountain
King. You cannot attack it, and going that way gives `You can't get by the
snake.` The way past is to drop the caged bird: the bird attacks the snake
and drives it away, after which the side chambers (silver, coins, jewels)
are open. If the bird is dead or lost, those treasures are unreachable.
Trying to cross while the snake is present, with the bird in hand, is a hint
situation (see §7).

### The dragon and the rug

The dragon guards the Persian rug in a secret canyon. Fighting it:

```text
With what?  Your bare hands?
```

Answer `yes` (or `y`) and the dragon dies:

```text
Congratulations!  You have just vanquished a dragon with your bare hands! (Unbelievable, isn't it?)
```

The rug becomes a normal treasure, the two canyon branches join (`scan2`
replaces `scan1` and `scan3`), and you are moved there. The dragon's body is
visible from the west branch. Throwing the axe at the dragon only bounces
off. Attacking a dead dragon gives
`For crying out loud, the poor thing is already dead!`

### The troll bridge

The troll guards a chasm. `cross`/`over`/`across` while the troll is present
gives `The troll refuses to let you cross.` The way past is to `throw` a
treasure to the troll; he catches it and disappears, leaving the bridge
crossable. If you throw the bear into the troll's room, the bear chases the
troll away — and the bridge becomes crossable without paying.

Crossing the bridge with the bear in tow is fatal: the bridge buckles under
his weight, you fall, and the bear dies at the far side (which permanently
loses the spices and chain if they are still over there). Crossing is
handled by a special pseudo-location so that dwarves never cross.

### The door

The massive iron door in the immense passage is rusty. `pour oil` frees it;
`pour water` rusts it solid. With `prop[DOOR] == 1` you can walk north into
the cavern with the waterfall.

### The clam and the oyster

The giant clam in the Shell Room is too big to carry through the little
passage south. Opening it requires the jeweled trident (from the waterfall
cavern) and that you are not holding the clam. `open clam` reveals a pearl,
which rolls into the cul-de-sac (`sac`), and the clam becomes an oyster
(`prop[CLAM]` destroyed, `OYSTER` dropped in its place). The pearl is then
reachable. The oyster itself can be opened again, but contains nothing.

### The plant

The tiny plant in the west pit can be watered (twice) to become a beanstalk:
first 12 feet tall (`The plant spurts into furious growth for a few seconds.`),
then gigantic (`There is a gigantic beanstalk stretching all the way up to the hole.`).
A third watering resets it to a tiny plant. Climbing:

* gigantic plant (`prop == 4`) → the narrow corridor;
* 12-foot plant (`prop == 2`) → back up to the Twopit Room;
* otherwise → `There is nothing here to climb.  Use "up" or "out" to leave the pit.`

This is the only way to reach the Giant Room, the waterfall, the trident,
and the spices.

### The vase and the pillow

The Ming vase shatters if dropped anywhere except onto the velvet pillow in
the Soft Room. Dropping it on the pillow sets `prop[VASE]=0` (intact, worth
full value). Dropping it elsewhere prints `The Ming vase drops with a
delicate crash.` and makes it worthless. Breaking it, or filling it with
liquid, shatters it. (A shattered vase still counts as "seen" for `tally`.)

### The bear and the chain

The bear in the barren room is chained to the wall. Feed it the tasty food
and it becomes gentle. Then `unlock chain` with the keys frees it; the
chain becomes a treasure (`prop[CHAIN]=0`). If you unlock the chain while
the bear is still ferocious, you can't get past him. Throwing the axe at the
bear makes the axe stick near the bear and become unreachable until the bear
is fed.

### The vending machine

In a dead end off the all-different maze stands a vending machine. Drop the
coins there: `There are fresh batteries here.` (the coins are destroyed).

### The plover-alcove passage

The tight tunnel between the alcove and the Plover Room only passes if you
carry nothing, or exactly the emerald. This is why the emerald must be
carried through alone, and why the Plover Room is dark and mysterious on
your first visit: you arrive without a lamp. Saying `plover` at Y2 while
carrying the emerald silently drops it first, so the tunnel trip is always
possible.

### The two mazes

* **All-alike maze**: 14 locations described as
  `You are in a maze of twisty little passages, all alike.` The exits are
  irregular, so you must drop objects to mark rooms. Hints suggest exactly
  this. The only ways out are up to the west end of the Hall of Mists and
  down from the brink of the pit.
* **All-different maze**: eleven rooms, each described differently, whose
  exits form an 11×11 Latin square over the ten directions (N, S, E, W, NE,
  SE, NW, SW, U, D). `diff0` goes down to the long hall; `diff10` goes south
  to the vending machine dead end. Dwarves are forbidden here (condition
  100 on the entrance).

### Witt's End

`You are at Witt's End.  Passages lead off in "all" directions.` Almost every
direction loops you back with a message, and going west gives a cave-in
message that also returns you to the main passage. Dropping the magazine
there is proof of your visit and worth 1 point.

---

## 7. Hints

The game offers eight hints. Each has a counter, a threshold, a cost, and a
prompt. Hints 2–7 are tied to location flags, and the counter resets when
you leave the relevant place. Accepting a hint costs points and usually
extends the lamp.

| # | Trigger flag | Threshold | Cost | Question |
| --- | --- | --- | --- | --- |
| 0 | start of game | 0 | 5 | Welcome to Adventure!!  Would you like instructions? |
| 1 | reading the oyster after closing | 0 | 10 | Hmmm, this looks like a clue... Should I go ahead and read it anyway? |
| 2 | `cave_hint` (outside grate) | 4 | 2 | Are you trying to get into the cave? |
| 3 | `bird_hint` (bird chamber) | 5 | 2 | Are you trying to catch the bird? |
| 4 | `snake_hint` (Hall of the Mountain King) | 8 | 2 | Are you trying to deal somehow with the snake? |
| 5 | `twist_hint` (mazes) | 75 | 4 | Do you need help getting out of the maze? |
| 6 | `dark_hint` (alcove / Plover / Dark-Room) | 25 | 5 | Are you trying to explore beyond the Plover Room? |
| 7 | `witt_hint` (Witt's End) | 20 | 3 | Do you need help getting out of here? |

The extra conditions:

* Hint 2 is only offered if the grate is locked and you are not carrying
  the keys.
* Hint 3 is only offered if the bird is here, you were just asking about the
  bird, and you carry the rod.
* Hint 4 needs the snake present and no bird present.
* Hint 5 needs the current, previous, and previous-previous rooms all empty
  of objects and you carrying more than one object.
* Hint 6 needs the emerald not in its original place and the pyramid still
  unseen.
* Hint 7 is always offered at Witt's End.

Accepting hint 0 gives you the long instructions and a 1000-turn lamp;
declining gives a 330-turn lamp. Hint 1 is the only one that costs 10 and is
offered by `read oyster` after the cave closes.

---

## 8. The cave closes

`tally` starts at 15 and drops each time you see a new treasure. Once
`tally == 0` (all fifteen seen), `clock1` starts counting down, one tick per
command while you are inside the cave and not at Y2. `clock1` starts at 15.

* When `clock1` reaches 0:

  ```text
  A sepulchral voice, reverberating through the cave, says, "Cave
  closing soon.  All adventurers exit immediately through main office."
  ```

  At this moment: the grate locks, the crystal bridge vanishes, all dwarves
  and the pirate vanish, the troll and the bridge are replaced by the
  "absent troll", the bear is removed unless dead, and the chain and axe
  are reset to movable. `closing` is now true.
* From then on, trying to leave the cave (any exit to a location above
  ground) triggers panic: `clock2` is set to 15 and you get
  `A mysterious recorded voice groans into life and announces: "This exit is closed.  Please leave via main office."`
  You cannot unlock the grate, create the bridge, or be resurrected.
* When `clock2` reaches 0, the cave closes:

  ```text
  The sepulchral voice intones, "The cave is now closed."  As the echoes
  fade, there is a blinding flash of light (and a small puff of orange
  smoke). . . .    Then your eyes refocus; you look around and find...
  ```

  You are transported to the two-part storage room (`neend` and `swend`),
  the objects are rearranged, everything you carried is destroyed, and
  `bonus` is set to 10. The long descriptions of the storage room are the
  final puzzle's clues: a pile of empty bottles, young beanstalks, oysters,
  rods with stars, lanterns, sleeping dwarves, and a mirror at the northeast
  end; a grate, snakes, caged birds, rods with marks, and pillows at the
  southwest end.
* Once closed, picking up a treasure resets its property from `-1` to `0`
  on the next turn, so it can be described again. Reading the oyster gives
  hint 1.
* `blast` while the cave is closed and the "rod with a rusty mark" has a
  nonnegative property value ends the game with one of three explosions,
  worth 25, 30, or 45 bonus points:
  * carrying or standing with the marked rod: `There is a loud explosion and you are suddenly splashed across the walls of the room.` (25)
  * at the northeast end: `There is a loud explosion and a twenty-foot hole appears in the far wall, burying the snakes in the rubble.  A river of molten lava pours in through the hole, destroying everything in its path, including you!` (30)
  * at the southwest end without the marked rod: `There is a loud explosion, and a twenty-foot hole appears in the far wall, burying the dwarves in the rubble.  You march through the hole and find yourself in the main office, where a cheering band of friendly elves carry the conquering adventurer off into the sunset.` (45)

---

## 9. Death and resurrection

You may die three times. On death:

1. `death_count` increases.
2. If the cave is closing, the game simply ends:
   `It looks as though you're dead.  Well, seeing as how it's so close to closing time anyway, let's just call it a day.`
3. Otherwise you are asked whether to be reincarnated, with one of three
   pairs of messages (increasingly exasperated). On the third death the game
   asks, then ends regardless.
4. If you accept, all objects you carry are dropped at your last safe
   location (the lamp is turned off and left at the road), you are placed
   inside the building, and the game continues. You cannot `back` into the
   cave.

Death sources: falling in the dark (35% when already in the dark), falling
off the bridge, jumping the fissure, jumping into the pit at the windows,
jumping off the stalactite, jumping down at the breath-taking view
(`Don't be ridiculous!` — that one is a message, not death), and dwarf
knives. The message `The resulting ruckus has awakened the dwarves...`
(disturbing dwarves after closing, breaking the mirror, waking a dwarf)
ends the game immediately with no resurrection.

Each unused death is worth 10 points.

---

## 10. Scoring

The score is computed at the end (and previewed by `score`, which shows
`score() - 4` and asks whether you want to quit).

| Objective | Points | Maximum |
| --- | --- | --- |
| Getting well into the cave (`dflag != 0`) | 25 | 25 |
| Each treasure below the chest, delivered intact | 12 | 60 |
| The chest itself, delivered | 14 | 14 |
| Each treasure above the chest, delivered intact | 16 | 144 |
| Each unused death | 10 | 30 |
| Not quitting | 4 | 4 |
| Reaching Witt's End (magazine there) | 1 | 1 |
| Reaching the closing of the cave | 25 | 25 |
| Additional bonuses (the dynamite ending) | 25/30/45 | 45 |
| Rounding | 2 | 2 |
| **Total** | | **350** |

Details:

* A treasure scores 2 points just for having been seen.
* A treasure scores full value only if `prop >= 0`, it is in the building,
  and its property is exactly 0 (so the rug must have its dragon removed and
  the chain must have been unlocked; a shattered vase scores only 2).
* Hints subtract their cost from the final score.
* Quitting (`quit` or the `score` prompt) forfeits the 4 "not quitting"
  points and ends the game.
* The worst possible score is −3; 1 is possible but rare.

### Ranks

| Score at least | Rank |
| --- | --- |
| 35 | You are obviously a rank amateur.  Better luck next time. |
| 100 | Your score qualifies you as a novice class adventurer. |
| 130 | You have achieved the rating "Experienced Adventurer". |
| 200 | You may now consider yourself a "Seasoned Adventurer". |
| 250 | You have reached "Junior Master" status. |
| 300 | Your score puts you in Master Adventurer Class C. |
| 330 | Your score puts you in Master Adventurer Class B. |
| 349 | Your score puts you in Master Adventurer Class A. |
| 9999 | All of Adventuredom gives tribute to you, Adventure Grandmaster! |

The final report is:

```text
You scored 350 points out of a possible 350, using 336 turns.
All of Adventuredom gives tribute to you, Adventure Grandmaster!
To achieve the next higher rating would be a neat trick!
Congratulations!!
```

The "next higher rating" line is omitted only for the grandmaster class;
for every other class it tells you how many more points are needed.

---

## 11. Odds and ends

* `brief`: from then on, full descriptions are shown only the first time
  (and every 10000th visit); `look` still works, with the three-look
  limitation.
* `inventory`: lists everything you carry, one object per line. It also
  reports the bear following you, if you are being followed.
* `find <object>`: tells you whether the object is with you, at your
  location, in the bottle, or a feature of the place; otherwise the default
  message.
* `score`: shows what you would score if you quit now (excluding the 4
  points for not quitting) and asks whether to quit.
* `quit`: asks `Do you really want to quit now?` and ends the game.
* The bear follows you after you feed it. It is shown in the room
  description as `You are being followed by a very large, tame bear.` and
  cannot be dropped into the troll's room without consequences.
* Objects are listed in a fixed order (by object number) in each room, not
  in the order you dropped them.
* The `magazine` must be dropped at Witt's End for the 1-point visit bonus;
  `place[MAG] == witt` is checked at the end.
