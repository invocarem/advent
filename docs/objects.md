# Objects

This is the object universe of the game: 66 numbered objects plus
`NOTHING` (0). The numbering is the C enum order from `advent.w`; it is
significant because objects are listed in a room in ascending number order,
and because a treasure's point value depends on whether it is below or above
the chest.

## How objects are stored

Each object `t` has:

| Field | Meaning |
| --- | --- |
| `name[t]` | inventory name, or 0 for things you cannot pick up |
| `base[t]` | 0 if movable; otherwise the lowest-numbered object of its immovable group |
| `place[t]` | a location code, or `inhand` (−1), or `limbo` (0) |
| `prop[t]` | current property value (see below) |
| `offset[t]` | where this object's notes start in the global note table |

Objects at a location are kept in a singly linked list: `first[loc]`, then
`link[first[loc]]`, and so on. `drop` pushes onto the front of a list,
`carry` removes from a list. Because the program creates objects from the
highest number down to the lowest, a room's list ends up in ascending object
order.

`prop` starts at **−1 for treasures** (meaning "not yet seen") and 0 for
everything else. When you first see a treasure, its property becomes 0 (or 1
for the rug and the chain, so that you must do something special to get full
credit). Objects print the message `note[prop + offset]`, so property values
choose among an object's descriptions.

## The object table

Places are the starting positions. `—` means the object starts in limbo.

| # | Object | Inventory name | Base | Starts at | Treasure |
| --- | --- | --- | --- | --- | --- |
| 0 | `NOTHING` | — | 0 | — | |
| 1 | `KEYS` | Set of keys | 0 | house | |
| 2 | `LAMP` | Brass lantern | 0 | house | |
| 3 | `GRATE` | — | GRATE | outside | |
| 4 | `GRATE_` | — | GRATE | inside | |
| 5 | `CAGE` | Wicker cage | 0 | cobbles | |
| 6 | `ROD` | Black rod | 0 | debris | |
| 7 | `ROD2` | Black rod | 0 | — | |
| 8 | `TREADS` | — | TREADS | spit | |
| 9 | `TREADS_` | — | TREADS | emist | |
| 10 | `BIRD` | Little bird in cage | 0 | bird | |
| 11 | `DOOR` | — | DOOR | immense | |
| 12 | `PILLOW` | Velvet pillow | 0 | soft | |
| 13 | `SNAKE` | — | SNAKE | hmk | |
| 14 | `CRYSTAL` | — | CRYSTAL | efiss | |
| 15 | `CRYSTAL_` | — | CRYSTAL | wfiss | |
| 16 | `TABLET` | — | TABLET | droom | |
| 17 | `CLAM` | Giant clam >GRUNT!< | 0 | shell | |
| 18 | `OYSTER` | Giant oyster >GROAN!< | 0 | — | |
| 19 | `MAG` | "Spelunker Today" | 0 | ante | |
| 20 | `DWARF` | — | DWARF | — | |
| 21 | `KNIFE` | — | 0 | — | |
| 22 | `FOOD` | Tasty food | 0 | house | |
| 23 | `BOTTLE` | Small bottle | 0 | house | |
| 24 | `WATER` | Water in the bottle | 0 | — | |
| 25 | `OIL` | Oil in the bottle | 0 | — | |
| 26 | `MIRROR` | — | MIRROR | mirror | |
| 27 | `MIRROR_` | — | MIRROR | — | |
| 28 | `PLANT` | — | PLANT | wpit | |
| 29 | `PLANT2` | — | PLANT2 | w2pit | |
| 30 | `PLANT2_` | — | PLANT2 | e2pit | |
| 31 | `STALACTITE` | — | STALACTITE | tite | |
| 32 | `SHADOW` | — | SHADOW | windoe | |
| 33 | `SHADOW_` | — | SHADOW | window | |
| 34 | `AXE` | Dwarf's axe | 0 | — | |
| 35 | `ART` | — | ART | oriental | |
| 36 | `PIRATE` | — | PIRATE | — | |
| 37 | `DRAGON` | — | DRAGON | scan1 | |
| 38 | `DRAGON_` | — | DRAGON | scan3 | |
| 39 | `BRIDGE` | — | BRIDGE | swside | |
| 40 | `BRIDGE_` | — | BRIDGE | neside | |
| 41 | `TROLL` | — | TROLL | swside | |
| 42 | `TROLL_` | — | TROLL | neside | |
| 43 | `TROLL2` | — | TROLL2 | — | |
| 44 | `TROLL2_` | — | TROLL2 | — | |
| 45 | `BEAR` | — | BEAR | barr | |
| 46 | `MESSAGE` | — | MESSAGE | — | |
| 47 | `GEYSER` | — | GEYSER | view | |
| 48 | `PONY` | — | PONY | pony | |
| 49 | `BATTERIES` | Batteries | 0 | — | |
| 50 | `MOSS` | — | MOSS | soft | |
| 51 | `GOLD` | Large gold nugget | 0 | nugget | 12 |
| 52 | `DIAMONDS` | Several diamonds | 0 | wfiss | 12 |
| 53 | `SILVER` | Bars of silver | 0 | ns | 12 |
| 54 | `JEWELS` | Precious jewelry | 0 | south | 12 |
| 55 | `COINS` | Rare coins | 0 | west | 12 |
| 56 | `CHEST` | Treasure chest | 0 | — | 14 |
| 57 | `EGGS` | Golden eggs | 0 | giant | 16 |
| 58 | `TRIDENT` | Jeweled trident | 0 | falls | 16 |
| 59 | `VASE` | Ming vase | 0 | oriental | 16 |
| 60 | `EMERALD` | Egg-sized emerald | 0 | proom | 16 |
| 61 | `PYRAMID` | Platinum pyramid | 0 | droom | 16 |
| 62 | `PEARL` | Glistening pearl | 0 | — | 16 |
| 63 | `RUG` | Persian rug | RUG (until the dragon dies) | scan1 | 16 |
| 64 | `RUG_` | — | RUG | scan3 | — |
| 65 | `SPICES` | Rare spices | 0 | chamber | 16 |
| 66 | `CHAIN` | Golden chain | CHAIN (until unlocked) | barr | 16 |

The "Treasure" column is the full delivery value: 12 points for objects
1–55 (five of them: gold, diamonds, silver, jewels, coins), 14 for the chest,
and 16 for everything numbered above the chest. `RUG_` is a duplicate half
of the rug and never scores; its property stays −1.

## Object notes

These are the exact texts printed when an object is described. `prop` values
are listed with their note; a blank means no message.

### Movable tools and containers

**KEYS** (`prop 0`): There are some keys on the ground here.

**LAMP**: `0` There is a shiny brass lamp nearby. / `1` There is a lamp
shining nearby.

**CAGE** (`0`): There is a small wicker cage discarded nearby.

**ROD** (`0`): A three-foot black rod with a rusty star on an end lies
nearby.

**ROD2** (`0`): A three-foot black rod with a rusty mark on an end lies
nearby.

**BIRD**: `0` A cheerful little bird is sitting here singing. / `1` There is
a little bird in the cage.

**PILLOW** (`0`): A small velvet pillow lies on the floor.

**CLAM** (`0`): There is an enormous clam here with its shell tightly
closed.

**OYSTER**: `0` There is an enormous oyster here with its shell tightly
closed. / `1` Interesting.  There seems to be something written on the
underside of the oyster.

**MAG** (`0`): There are a few recent issues of "Spelunker Today" magazine
here.

**FOOD** (`0`): There is food here.

**BOTTLE**: `0` There is a bottle of water here. / `1` There is an empty
bottle here. / `2` There is a bottle of oil here.

**AXE**: `0` There is a little axe here. / `1` There is a little axe lying
beside the bear.

**BATTERIES**: `0` There are fresh batteries here. / `1` Some worn-out
batteries have been discarded nearby.

### Immovable scenery

**GRATE**: `0` The grate is locked. / `1` The grate is open.

**TREADS**: `0` Rough stone steps lead down the pit. / `1` Rough stone steps
lead up the dome. (Property 1 is used only when the treads are seen from the
Hall of Mists; the treads themselves never change property.)

**DOOR**: `0` The way north is barred by a massive, rusty, iron door. /
`1` The way north leads through a massive, rusty, iron door.

**SNAKE**: `0` A huge green fierce snake bars the way! / `1` *(none — the
snake is gone)*

**CRYSTAL**: `0` *(none)* / `1` A crystal bridge now spans the fissure. /
`2` The crystal bridge has vanished!

**TABLET** (`0`): A massive stone tablet embedded in the wall reads:
"CONGRATULATIONS ON BRINGING LIGHT INTO THE DARK-ROOM!"

**DWARF**: *(none)*

**MIRROR / MIRROR_**: *(none)*

**PLANT**: `0` There is a tiny little plant in the pit, murmuring "Water,
water, ..." / `1` The plant spurts into furious growth for a few seconds. /
`2` There is a 12-foot-tall beanstalk stretching up out of the pit,
bellowing "Water!!  Water!!" / `3` The plant grows explosively, almost
filling the bottom of the pit. / `4` There is a gigantic beanstalk
stretching all the way up to the hole. / `5` You've over-watered the plant!
It's shriveling up!  It's, it's...

**PLANT2**: `0` *(none)* / `1` The top of a 12-foot-tall beanstalk is poking
out of the west pit. / `2` There is a huge beanstalk growing out of the west
pit up to the hole.

**STALACTITE**: *(none)*

**SHADOW / SHADOW_** (`0`): The shadowy figure seems to be trying to attract
your attention.

**ART**: *(none)*

**PIRATE**: *(none)*

**DRAGON**: `0` A huge green fierce dragon bars the way! / `1`
Congratulations!  You have just vanquished a dragon with your bare hands!
(Unbelievable, isn't it?) / `2` The body of a huge green dead dragon is
lying off to one side.

**BRIDGE**: `0` A rickety wooden bridge extends across the chasm, vanishing
into the mist.  A sign posted on the bridge reads, "STOP!  PAY TROLL!" /
`1` The wreckage of a bridge (and a dead bear) can be seen at the bottom of
the chasm.

**TROLL**: `0` A burly troll stands by the bridge and insists you throw him a
treasure before you may cross. / `1` The troll steps out from beneath the
bridge and blocks your way. / `2` *(none)*

**TROLL2** (`0`): The troll is nowhere to be seen.

**BEAR**: `0` There is a ferocious cave bear eying you from the far end of
the room! / `1` There is a gentle cave bear sitting placidly in one corner. /
`2` There is a contented-looking bear wandering about nearby. / `3`
*(none — the bear is dead)*

**MESSAGE** (`0`): There is a message scrawled in the dust in a flowery
script, reading: "This is not the maze where the pirate leaves his treasure
chest."

**GEYSER**: *(none)*

**PONY** (`0`): There is a massive vending machine here.  The instructions on
it read: "Drop coins here to receive fresh batteries."

**MOSS**: *(none)*

**RUG**: `0` There is a Persian rug spread out on the floor! / `1` The dragon
is sprawled out on a Persian rug!!

**CHAIN**: `0` There is a golden chain lying in a heap on the floor! / `1`
The bear is locked to the wall with a golden chain! / `2` There is a golden
chain locked to the wall!

### Treasures

**GOLD** (`0`): There is a large sparkling nugget of gold here!

**DIAMONDS** (`0`): There are diamonds here!

**SILVER** (`0`): There are bars of silver here!

**JEWELS** (`0`): There is precious jewelry here!

**COINS** (`0`): There are many coins here!

**CHEST** (`0`): The pirate's treasure chest is here!

**EGGS**: `0` There is a large nest here, full of golden eggs! / `1` The nest
of golden eggs has vanished! / `2` Done!

**TRIDENT** (`0`): There is a jewel-encrusted trident here!

**VASE**: `0` There is a delicate, precious, Ming vase here! / `1` The vase
is now resting, delicately, on a velvet pillow. / `2` The floor is littered
with worthless shards of pottery. / `3` The Ming vase drops with a delicate
crash.

**EMERALD** (`0`): There is an emerald here the size of a plover's egg!

**PYRAMID** (`0`): There is a platinum pyramid here, 8 inches on a side!

**PEARL** (`0`): Off to one side lies a glistening pearl!

**SPICES** (`0`): There are rare spices here!

## Property cheat sheet

| Object | prop values |
| --- | --- |
| `BOTTLE` | 0 water, 1 empty, 2 oil, −2 reset by closing |
| `LAMP` | 0 off, 1 on |
| `GRATE` | 0 locked, 1 open |
| `DOOR` | 0 rusty shut, 1 oiled |
| `SNAKE` | 0 present, 1 driven away |
| `CRYSTAL` | 0 no bridge, 1 bridge, 2 vanished |
| `BIRD` | 0 free, 1 caged |
| `PLANT` | 0 tiny, 1 spurting, 2 tall, 3 exploding, 4 gigantic, 5 over-watered |
| `PLANT2` | 0 nothing, 1 top visible, 2 huge |
| `AXE` | 0 loose, 1 stuck by the bear |
| `DRAGON` | 0 alive, 1 killed bare-handed, 2 dead |
| `BRIDGE` | 0 intact, 1 collapsed |
| `TROLL` | 0 present, 1 paid, 2 gone |
| `BEAR` | 0 ferocious, 1 gentle, 2 contented, 3 dead |
| `VASE` | 0 intact, 1 on pillow, 2 shattered, 3 crashed |
| `EGGS` | 0 present, 1 vanished, 2 "Done!" |
| `RUG` | 1 dragon on it (initial), 0 free |
| `CHAIN` | 0 loose, 1 locking the bear, 2 locked to the wall |
| `BATTERIES` | 0 fresh, 1 used |
| `TREASURES` | −1 unseen, 0 seen, other values mean broken/hidden |

## Objects that are not really objects

* `WATER` and `OIL` are virtual objects: they exist only when inside the
  bottle (`place == inhand`) or as a location feature. `fill`, `pour`,
  `drink`, `take water`, and `drop water` all special-case them.
* `KNIFE` is only ever a marker for where dwarves have thrown knives; any
  attempt to refer to it makes it vanish:
  `The dwarves' knives vanish as they strike the walls of the cave.`
* `DWARF` is a stand-in used when a dwarf is present, so that commands like
  `kill dwarf` work.
* `PIRATE`, `MIRROR_`, `TROLL2`, and `TROLL2_` exist only to make the
  two-ended groups work; they never appear in inventories.
