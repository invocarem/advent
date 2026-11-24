# Reference: Vocabulary, Messages, Hints, Scoring

Everything in this file is a direct transcription of the tables in
`knuth/advent.w`. Words are shown in their truncated five-character form
when the original stores them that way (for example `upwar` is the stored
form of "upward"; typing `upwards` also works, because only five letters are
compared).

## The vocabulary

### Motion words

| Word(s) | Meaning |
| --- | --- |
| `north`, `n` | N |
| `south`, `s` | S |
| `east`, `e` | E |
| `west`, `w` | W |
| `ne` | NE |
| `se` | SE |
| `nw` | NW |
| `sw` | SW |
| `upwar`, `up`, `u`, `above`, `ascen` | U |
| `downw`, `down`, `d`, `desce` | D |
| `left` | L |
| `right` | R |
| `inwar`, `insid`, `in` | IN |
| `out`, `outsi`, `exit`, `leave` | OUT |
| `forwa`, `conti`, `onwar` | FORWARD |
| `back`, `retur`, `retre` | BACK |
| `over` | OVER |
| `acros` | ACROSS |
| `upstr` | UPSTREAM |
| `downs` | DOWNSTREAM |
| `enter` | ENTER |
| `crawl` | CRAWL |
| `jump` | JUMP |
| `climb` | CLIMB |
| `look`, `exami`, `touch`, `descr` | LOOK |
| `cross` | CROSS |
| `road`, `hill` | ROAD |
| `fores` | WOODS |
| `valle` | VALLEY |
| `build`, `house` | HOUSE |
| `gully` | GULLY |
| `strea` | STREAM |
| `depre` | DEPRESSION |
| `entra` | ENTRANCE |
| `cave` | CAVE |
| `rock` | ROCK |
| `slab`, `slabr` | SLAB |
| `bed` | BED |
| `passa`, `tunne` | PASSAGE |
| `caver` | CAVERN |
| `canyo` | CANYON |
| `awkwa` | AWKWARD |
| `secre` | SECRET |
| `bedqu` | BEDQUILT |
| `reser` | RESERVOIR |
| `giant` | GIANT |
| `orien` | ORIENTAL |
| `shell` | SHELL |
| `barre` | BARREN |
| `broke` | BROKEN |
| `debri` | DEBRIS |
| `view` | VIEW |
| `fork` | FORK |
| `pit` | PIT |
| `slit` | SLIT |
| `crack` | CRACK |
| `dome` | DOME |
| `hole` | HOLE |
| `wall` | WALL |
| `hall` | HALL |
| `room` | ROOM |
| `floor` | FLOOR |
| `stair` | STAIRS |
| `steps` | STEPS |
| `cobbl` | COBBLES |
| `surfa` | SURFACE |
| `dark` | DARK |
| `low` | LOW |
| `outdo` | OUTDOORS |
| `y2` | Y2 |
| `xyzzy` | XYZZY |
| `plugh` | PLUGH |
| `plove` | PLOVER |
| `main`, `offic` | OFFICE |
| `null`, `nowhe` | NOWHERE |

Note that there is no word for the west side chamber, the south side
chamber, or the Hall of the Mountain King: you reach them with directions
or with `hall`.

### Object words

| Word(s) | Object |
| --- | --- |
| `key`, `keys` | KEYS |
| `lamp`, `lante`, `headl` | LAMP |
| `grate` | GRATE |
| `cage` | CAGE |
| `rod` | ROD (or ROD2 when that is the rod present) |
| `bird` | BIRD |
| `door` | DOOR |
| `pillo`, `velve` | PILLOW |
| `snake` | SNAKE |
| `fissu` | CRYSTAL |
| `table` | TABLET |
| `clam` | CLAM |
| `oyste` | OYSTER |
| `magaz`, `issue`, `spelu`, `"spel` | MAG |
| `dwarf`, `dwarv` | DWARF |
| `knife`, `knive` | KNIFE |
| `food`, `ratio` | FOOD |
| `bottl`, `jar` | BOTTLE |
| `water`, `h2o` | WATER |
| `oil` | OIL |
| `mirro` | MIRROR |
| `plant`, `beans` | PLANT |
| `stala` | STALACTITE |
| `shado`, `figur` | SHADOW |
| `axe` | AXE |
| `drawi` | ART |
| `pirat` | PIRATE |
| `drago` | DRAGON |
| `chasm` | BRIDGE |
| `troll` | TROLL |
| `bear` | BEAR |
| `messa` | MESSAGE |
| `volca`, `geyse` | GEYSER |
| `vendi`, `machi` | PONY |
| `batte` | BATTERIES |
| `moss`, `carpe` | MOSS |
| `gold`, `nugge` | GOLD |
| `diamo` | DIAMONDS |
| `silve`, `bars` | SILVER |
| `jewel` | JEWELS |
| `coins` | COINS |
| `chest`, `box`, `treas` | CHEST |
| `eggs`, `egg`, `nest` | EGGS |
| `tride` | TRIDENT |
| `ming`, `vase`, `shard`, `potte` | VASE |
| `emera` | EMERALD |
| `plati`, `pyram` | PYRAMID |
| `pearl` | PEARL |
| `persi`, `rug` | RUG |
| `spice` | SPICES |
| `chain` | CHAIN |

### Action words

| Word(s) | Action |
| --- | --- |
| `take`, `carry`, `keep`, `catch`, `captu`, `steal`, `get`, `tote` | TAKE |
| `drop`, `relea`, `free`, `disca`, `dump` | DROP |
| `open`, `unloc` | OPEN |
| `close`, `lock` | CLOSE |
| `light`, `on` | ON |
| `extin`, `off` | OFF |
| `wave`, `shake`, `swing` | WAVE |
| `calm`, `placa`, `tame` | CALM |
| `walk`, `run`, `trave`, `go`, `proce`, `explo`, `goto`, `follo`, `turn` | GO |
| `nothi` | RELAX |
| `pour` | POUR |
| `eat`, `devou` | EAT |
| `drink` | DRINK |
| `rub` | RUB |
| `throw`, `toss` | TOSS |
| `wake`, `distu` | WAKE |
| `feed` | FEED |
| `fill` | FILL |
| `break`, `smash`, `shatt` | BREAK |
| `blast`, `deton`, `ignit`, `blowu` | BLAST |
| `attac`, `kill`, `fight`, `hit`, `strik`, `slay` | KILL |
| `say`, `chant`, `sing`, `utter`, `mumbl` | SAY |
| `read`, `perus` | READ |
| `fee`, `fie`, `foe`, `foo`, `fum` | FEEFIE |
| `brief` | BRIEF |
| `find`, `where` | FIND |
| `inven` | INVENTORY |
| `score` | SCORE |
| `quit` | QUIT |

### Message words

Message words print a fixed text. The numbers are indices into the message
array.

| Word(s) | Index | Text |
| --- | --- | --- |
| `abra`, `abrac`, `opens`, `sesam`, `shaza`, `hocus`, `pocus` | 0 | Good try, but that is an old worn-out magic word. |
| `help`, `?` | 1 | *the long help text (see below)* |
| `tree`, `trees` | 2 | The trees of the forest are large hardwood oak and maple, with an occasional grove of pine or spruce.  There is quite a bit of undergrowth, largely birch and ash saplings plus nondescript bushes of various sorts.  This time of year visibility is quite restricted by all the leaves, but travel is quite easy if you detour around the spruce and berry bushes. |
| `dig`, `excav` | 3 | Digging without a shovel is quite impractical.  Even with a shovel progress is unlikely. |
| `lost` | 4 | I'm as confused as you are. |
| `mist` | 7 | Mist is a white vapor, usually water, seen from time to time in caverns.  It can be found anywhere but is frequently a sign of a deep pit leading down to water. |
| `fuck` | 8 | Watch it! |
| `stop` | 10 | I don't know the word "stop".  Use "quit" if you want to give up. |
| `info`, `infor` | 11 | *the long info text (see below)* |
| `swim` | 12 | I don't know how. |

The messages at indices 5, 6, and 9 are not reachable from the vocabulary;
they are the three dynamite endings:

| Index | Text | Bonus |
| --- | --- | --- |
| 5 | There is a loud explosion and you are suddenly splashed across the walls of the room. | 25 |
| 6 | There is a loud explosion and a twenty-foot hole appears in the far wall, burying the snakes in the rubble.  A river of molten lava pours in through the hole, destroying everything in its path, including you! | 30 |
| 9 | There is a loud explosion, and a twenty-foot hole appears in the far wall, burying the dwarves in the rubble.  You march through the hole and find yourself in the main office, where a cheering band of friendly elves carry the conquering adventurer off into the sunset. | 45 |

#### Help text (index 1)

```text
I know of places, actions, and things.  Most of my vocabulary
describes places and is used to move you there.  To move, try words
like forest, building, downstream, enter, east, west, north, south,
up, or down.  I know about a few special objects, like a black rod
hidden in the cave.  These objects can be manipulated using some of
the action words that I know.  Usually you will need to give both the
object and action words (in either order), but sometimes I can infer
the object from the verb alone.  Some objects also imply verbs; in
particular, "inventory" implies "take inventory", which causes me to
give you a list of what you're carrying.  The objects have side
effects; for instance, the rod scares the bird.  Usually people having
trouble moving just need to try a few more words.  Usually people
trying unsuccessfully to manipulate an object are attempting something
beyond their (or my!) capabilities and should try a completely
different tack.  To speed the game you can sometimes move long
distances with a single word.  For example, "building" usually gets
you to the building from anywhere above ground except when lost in the
forest.  Also, note that cave passages turn a lot, and that leaving a
room to the north does not guarantee entering the next from the south.
Good luck!
```

#### Info text (index 11)

```text
If you want to end your adventure early, say "quit".  To get full
credit for a treasure, you must have left it safely in the building,
though you get partial credit just for locating it.  You lose points
for getting killed, or for quitting, though the former costs you more.
There are also points based on how much (if any) of the cave you've
managed to explore; in particular, there is a large bonus just for
getting in (to distinguish the beginners from the rest of the pack),
and there are other ways to determine whether you've been through some
of the more harrowing sections.  If you think you've found all the
treasures, just keep exploring for a while.  If nothing interesting
happens, you haven't found them all yet.  If something interesting
DOES happen, it means you're getting a bonus and have an opportunity
to garner many more points in the master's section.
I may occasionally offer hints if you seem to be having trouble.
If I do, I'll warn you in advance how much it will affect your score
to accept the hints.  Finally, to save paper, you may specify "brief",
which tells me never to repeat the full description of a place
unless you explicitly ask me to.
```

## Default messages for actions

When an action has no special case for the object involved, the game prints
the action's default message (or, for `ABSTAIN`, nothing at all).

| Action | Default message |
| --- | --- |
| `TAKE` | You are already carrying it! |
| `DROP` | You aren't carrying it! |
| `OPEN` | I don't know how to lock or unlock such a thing. |
| `CLOSE` | *(same as OPEN)* |
| `ON` | You have no source of light. |
| `OFF` | *(same as ON)* |
| `WAVE` | Nothing happens. |
| `CALM` | I'm game.  Would you care to explain how? |
| `GO` | Where? |
| `RELAX` | OK. |
| `POUR` | *(same as DROP)* |
| `EAT` | Don't be ridiculous! |
| `DRINK` | You have taken a drink from the stream.  The water tastes strongly of minerals, but is not unpleasant.  It is extremely cold. |
| `RUB` | Rubbing the electric lamp is not particularly rewarding.  Anyway, nothing exciting happens. |
| `TOSS` | *(same as DROP)* |
| `WAKE` | *(same as EAT)* |
| `FEED` | There is nothing here to eat. |
| `FILL` | You can't fill that. |
| `BREAK` | It is beyond your power to do that. |
| `BLAST` | Blasting requires dynamite. |
| `KILL` | *(same as EAT)* |
| `READ` | I'm afraid I don't understand. |
| `FEEFIE` | I don't know how. |
| `BRIEF` | On what? |
| `FIND` | I can only tell you what you see as you move about and manipulate things.  I cannot tell you where remote things are. |
| `INVENTORY` | *(same as FIND)* |
| `SCORE` | Eh? |
| `QUIT` | *(same as SCORE)* |

`SAY` has no default message: with no word it asks `Say what?`, and with a
word it echoes `Okay, "<word>".`

## Hints

| # | Prompt | Cost | Threshold | Hint |
| --- | --- | --- | --- | --- |
| 0 | Welcome to Adventure!!  Would you like instructions? | 5 | — | The long welcome/instructions text (same as the `help` text plus the credits paragraph). |
| 1 | Hmmm, this looks like a clue, which means it'll cost you 10 points to read it.  Should I go ahead and read it anyway? | 10 | — | It says, "There is something strange about this place, such that one of the words I've always known now has a new effect." |
| 2 | Are you trying to get into the cave? | 2 | 4 | The grate is very solid and has a hardened steel lock.  You cannot enter without a key, and there are no keys in sight.  I would recommend looking elsewhere for the keys. |
| 3 | Are you trying to catch the bird? | 2 | 5 | Something seems to be frightening the bird just now and you cannot catch it no matter what you try.  Perhaps you might try later. |
| 4 | Are you trying to deal somehow with the snake? | 2 | 8 | You can't kill the snake, or drive it away, or avoid it, or anything like that.  There is a way to get by, but you don't have the necessary resources right now. |
| 5 | Do you need help getting out of the maze? | 4 | 75 | You can make the passages look less alike by dropping things. |
| 6 | Are you trying to explore beyond the Plover Room? | 5 | 25 | There is a way to explore that region without having to worry about falling into a pit.  None of the objects available is immediately useful for discovering the secret. |
| 7 | Do you need help getting out of here? | 3 | 20 | Don't go west. |

Hint 0's text is the welcome message printed at startup when you accept
instructions:

```text
Somewhere nearby is Colossal Cave, where others have found fortunes in
treasure and gold, though it is rumored that some who enter are never
seen again.  Magic is said to work in the cave.  I will be your eyes
and hands.  Direct me with commands of one or two words.  I should
warn you that I look at only the first five letters of each word, so
you'll have to enter "NORTHEAST" as "NE" to distinguish it from
"NORTH".  Should you get stuck, type "HELP" for some general hints.
For information on how to end your adventure, etc., type "INFO".
                        -  -  -
The first adventure program was developed by Willie Crowther.
Most of the features of the current program were added by Don Woods;
all of its bugs were added by Don Knuth.
```

Hints 2–7 are only offered while you are in a location with the matching
hint flag, after the threshold number of turns, and only if the extra
conditions in [gameplay.md](gameplay.md#7-hints) hold. Accepting a hint
adds `30 × cost` to the lamp limit if the limit is above 30.

## Death and resurrection texts

| Death | Question | Answer text |
| --- | --- | --- |
| 1 | Oh dear, you seem to have gotten yourself killed.  I might be able to help you out, but I've never really done this before.  Do you want me to try to reincarnate you? | All right.  But don't blame me if something goes wr......<br>                 --- POOF!! ---<br>You are engulfed in a cloud of orange smoke.  Coughing and gasping,<br>you emerge from the smoke and find.... |
| 2 | You clumsy oaf, you've done it again!  I don't know how long I can keep this up.  Do you want me to try reincarnating you again? | Okay, now where did I put my resurrection kit?....  >POOF!<<br>Everything disappears in a dense cloud of orange smoke. |
| 3 | Now you've really done it!  I'm out of orange smoke!  You don't expect me to do a decent reincarnation without any orange smoke, do you? | Okay, if you're so smart, do it yourself!  I'm leaving! |

The "OK." printed after either answer is the value of `default_msg[RELAX]`.

## Scoring and ranks

```text
Getting well into cave    25
Each treasure < chest     12  (5 treasures = 60)
Treasure chest            14
Each treasure > chest     16  (9 treasures = 144)
Each unused death         10  (3 = 30)
Not quitting               4
Reaching Witt's End        1
Getting to closing        25
Various bonuses        25/30/45 (max 45)
Round out the total        2
                        ----
                         350
```

The scoring function in the program:

```text
score = 2
      + 25 if dflag
      + for each treasure with prop >= 0:
            2, plus (10 / 12 / 14) if delivered intact to the house
      + 10 * (3 - deaths)
      + 4 if you did not quit
      + 1 if the magazine is at Witt's End
      + 25 if the cave is closing
      + bonus (0, 10, 25, 30, or 45)
      - hint costs
```

Ranks (the score must be at least the value shown):

| Score | Message |
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

The final report:

```text
You scored %d point(s) out of a possible 350, using %d turn(s).
<rank message>
To achieve the next higher rating, you need %d more point(s).
```

For the grandmaster rank the last line becomes:

```text
To achieve the next higher rating would be a neat trick!
Congratulations!!
```

## Program constants

| Constant | Value | Meaning |
| --- | --- | --- |
| `hash_prime` | 1009 | size of the word hash table |
| `travel_size` | 740 | maximum travel instructions |
| `rem_size` | 15 | number of remarks |
| `buf_size` | 72 | input buffer |
| `max_obj` | 66 (`CHAIN`) | highest object number |
| `min_treasure` | 51 (`GOLD`) | first treasure |
| `max_loc` | `didit` | highest real location |
| `min_in_cave` | `inside` | first underground location |
| `min_lower_loc` | `emist` | first "deep" location (activates dwarves) |
| `min_forced_loc` | `crack` | first pseudo-location |
| `max_spec` | `troll` | last special destination |
| `max_pirate_loc` | `dead2` | pirate/dwarf roaming limit |
| `nd` | 5 | number of dwarves |
| `max_deaths` | 3 | lives |
| `max_score` | 350 | perfect score |
| `tally` (initial) | 15 | unseen treasures |
| `clock1` | 15 | turns until the cave starts closing |
| `clock2` | 30 | turns until the cave is fully closed (15 after panic) |
| `limit` | 330 / 1000 | lamp life without / with instructions |
| `interval` | 5 | full description every 5th visit (10000 in brief mode) |
| `holding` limit | 7 | maximum carried objects |
| `pct(35)` | — | chance of falling in the dark |
| knife hit chance | `95*(dflag-2)/1000` | per thrown knife |
| dwarf axe hit chance | `ran(3) < 2` | 2/3 when throwing the axe |
| pirate warning | `pct(20)` | faint rustling noises |
| pirate/secret exits | 35% / 50% / 60% / 75% / 80% / 95% | see the travel table |

## The dwarves' starting positions

`dloc[0..5]` = `dead2` (the pirate), `hmk`, `wfiss`, `y2`, `like3`,
`complex`.

`dflag`:

| Value | Meaning |
| --- | --- |
| 0 | dormant; you have not reached the Hall of Mists or deeper |
| 1 | you have been deep, but no dwarf has been met |
| 2 | a dwarf has been met (the axe was thrown); dwarves start moving |
| 3 | a knife has been thrown (and missed) |
| 4 | knives hit with probability 0.095 |
| 5 | knives hit with probability 0.190 |
| 6 | knives hit with probability 0.285 |
| n | knives hit with probability 0.095·(n−2) |

## Remarks

The fourteen "stay put" messages are listed in
[world.md](world.md#the-complete-list-of-remarks).
