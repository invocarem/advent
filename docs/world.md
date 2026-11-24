# The World and the Travel Table

This document is the map of Colossal Cave as the program sees it: every
location code, its flags, and every travel instruction. The room texts
themselves are in [rooms.md](rooms.md); the objects are in
[objects.md](objects.md).

## Notation

* A location is shown as `name (code)`; the code is the value of the C
  `location` enum. Codes 1–140 are real places.
* **Exits** are written `motion → destination`, with synonyms separated by
  `/`. `(cond)` gives a travel condition:
  * `50%` — probabilistic exit (`condition 1..99`);
  * `carry X` — you must be carrying X;
  * `X here` — X must be at the location;
  * `X≠k` — property of X must not be k;
  * `no dwarf` — condition 100 (dwarves may not use it).
* **Flags**: `lighted`, `liquid` (water available), `oil`, and the hint
  flags `cave`, `bird`, `snake`, `twist`, `dark`, `witt`. A location with
  no `lighted` flag is dark unless your lamp is on.
* **Remarks** are messages printed while you stay put. An exit that ends in
  `remark N` prints remark N from
  [the list below](#the-complete-list-of-remarks) and leaves you where you
  are; a few exits quote the message inline instead.

## Region 1 — Above ground

The surface is a small loop: road, hill, valley, forest, woods, the slit in
the streambed, the depression with the locked grate, and the building.
The building is the "well house"; all treasures must end up here.

| Room | Flags | Exits |
| --- | --- | --- |
| `road` (1) | lighted, liquid | `w`/`up`/`road`→hill; `e`/`in`/`house`/`enter`→house; `s`/`down`/`gully`/`stream`/`downstream`→valley; `n`/`woods`→forest; `depression`→outside |
| `hill` (2) | lighted | `road`/`house`/`forward`/`e`/`d`→road; `woods`/`n`/`s`→forest |
| `house` (3) | lighted, liquid | `enter`/`out`/`outdoors`/`w`→road; `xyzzy`→debris; `plugh`→y2; `downstream`/`stream`→sewer |
| `valley` (4) | lighted, liquid | `upstream`/`house`/`n`→road; `woods`/`e`/`w`/`u`→forest; `downstream`/`s`/`d`→slit; `depression`→outside |
| `forest` (5) | lighted | `valley`/`e`/`d`→valley; `woods`(50%)/`forward`/`n`→forest; `woods`→woods; `w`/`s`→forest |
| `woods` (6) | lighted | `road`/`n`→road; `valley`/`e`/`w`/`d`→valley; `woods`/`s`→forest |
| `slit` (7) | lighted, liquid | `house`→road; `upstream`/`n`→valley; `woods`/`e`/`w`→forest; `downstream`/`rock`/`bed`/`s`→outside; `slit`/`stream`/`d`→*"You don't fit through a two-inch slit!"* |
| `outside` (8) | lighted, cave hint | `woods`/`e`/`w`/`s`→forest; `house`→road; `upstream`/`gully`/`n`→slit; `enter`(grate≠0)/`enter`/`in`/`d`→inside; `enter`→*"You can't go through a locked steel grate!"* |

The grate is the only way in: `enter` works only after the grate has been
unlocked (`prop[GRATE] != 0`). The hint flag here offers hint 2 after four
turns.

## Region 2 — The upper cave

The cave mouth leads down a crawl over cobbles to the debris room, then
through an awkward canyon and the bird chamber to the small pit at the top
of the Hall of Mists. The cage, rod, and bird are found here.

| Room | Flags | Exits |
| --- | --- | --- |
| `inside` (9) | lighted | `out`(grate≠0)/`out`/`u`→outside; `out`→remark 2; `crawl`/`cobbles`/`in`/`w`→cobbles; `pit`→spit; `debris`→debris |
| `cobbles` (10) | lighted | `out`/`surface`/`nowhere`/`e`→inside; `in`/`dark`/`w`/`debris`→debris; `pit`→spit |
| `debris` (11) | dark | `depression`(grate≠0)→outside; `entrance`→inside; `crawl`/`cobbles`/`passage`/`low`/`e`→cobbles; `canyon`/`in`/`u`/`w`→awk; `xyzzy`→house; `pit`→spit |
| `awk` (12) | dark | `depression`(grate≠0)→outside; `entrance`→inside; `d`/`e`/`debris`→debris; `in`/`u`/`w`→bird; `pit`→spit |
| `bird` (13) | dark, bird hint | `depression`(grate≠0)→outside; `entrance`→inside; `debris`→debris; `canyon`/`e`→awk; `passage`/`pit`/`w`→spit |
| `spit` (14) | dark | `depression`(grate≠0)→outside; `entrance`→inside; `debris`→debris; `passage`/`e`→bird; `down`(carry GOLD)/`pit`/`steps`→neck; `down`→emist; `crack`/`w`→crack |

The small pit is the gateway to the lower cave. Going down normally lands
you in the Hall of Mists (`emist`); going down with the gold nugget sends
you to `neck` and death, which is why the gold must leave by another route.
The `crack` pseudo-location prints a message and returns you to `spit`.

## Region 3 — The Hall of Mists

The great hall runs east–west, with the fissure and crystal bridge in the
middle, the Hall of the Mountain King below via the stairs, the gold nugget
room to the west, the crawl north to the fissure's west side, and the long
hall west of the west end.

| Room | Flags | Exits |
| --- | --- | --- |
| `emist` (15) | dark | `l`/`s`→nugget; `forward`/`hall`/`w`→efiss; `stairs`/`d`/`n`→hmk; `u`(carry GOLD)/`pit`/`steps`/`dome`/`passage`/`e`→cant; `u`→spit; `y2`→jumble |
| `nugget` (18) | dark | `hall`/`out`/`n`→emist |
| `efiss` (17) | dark | `hall`/`e`→emist; `jump`(crystal≠0)→remark 3; `forward`(crystal≠1)→lose; `over`(crystal≠1)/`across`/`w`/`cross`→remark 4; `over`→wfiss |
| `wfiss` (27) | dark | `jump`(crystal≠0)→remark 3; `forward`(crystal≠1)→lose; `over`(crystal≠1)/`across`/`e`/`cross`→remark 4; `over`→efiss; `n`→thru; `w`→wmist |
| `wmist` (41) | dark | `s`/`u`/`passage`/`climb`→like1; `e`→wfiss; `n`→duck; `w`/`crawl`→elong |
| `like1`–`like14` | dark, twist hint | see [the all-alike maze](#region-5--the-all-alike-maze) |
| `brink` (57) | dark | `d`/`climb`→bird; `w`→like10; `s`→dead8; `n`→like12; `e`→like13 |
| `elong` (60) | dark | `e`/`u`/`crawl`→wmist; `w`→wlong; `n`/`d`/`hole`→cross |
| `wlong` (61) | dark | `e`→elong; `n`→cross; `s`(no dwarf)→diff0 |
| `pony` (140) | dark | `n`/`out`→diff10 |
| `cross` (62) | dark | `w`→elong; `n`→dead0; `e`→west; `s`→wlong |

The `forward` quirk: at the fissure `forward` is supposed to be fatal, but
its condition (`crystal≠1`) fails once the bridge exists, so the skip rule
advances to the `over` instruction and `forward` carries you across. With no
bridge, `jump` and `forward` are fatal, while
`over`/`across`/`cross`/`w` print remark 4 ("There is no way across the
fissure."). With the bridge, `jump` prints remark 3 ("I respectfully suggest
you go across the bridge instead of jumping.").

## Region 4 — The Hall of the Mountain King and side chambers

A four-way chamber with the snake in it. North leads to the Y2 room and the
window on the pit; south and west lead to treasure chambers; southwest is a
35% secret passage to the canyon system (and always reachable once the
snake is gone); `secret` is a direct word to that canyon.

| Room | Flags | Exits |
| --- | --- | --- |
| `hmk` (19) | dark, snake hint | `stairs`/`u`/`e`→emist; `n`(snake gone)/`l`→ns; `s`(snake gone)/`r`→south; `w`(snake gone)/`forward`→west; `n`→snaked; `sw`(35%)→secret; `sw`(snake here)→snaked; `secret`→secret |
| `west` (30) | dark | `hall`/`out`/`e`→hmk; `w`/`u`→cross |
| `south` (29) | dark | `hall`/`out`/`n`→hmk |
| `ns` (28) | dark | `hall`/`out`/`s`→hmk; `n`/`y2`→y2; `d`/`hole`→dirty |
| `y2` (33) | dark | `plugh`→house; `s`→ns; `e`/`wall`/`broken`→jumble; `w`→windoe; `plover`(carry EMERALD)→pdrop; `plover`→proom |
| `jumble` (34) | dark | `d`/`y2`→y2; `u`→emist |
| `windoe` (35) | dark | `e`/`y2`→y2; `jump`→neck |

## Region 5 — The all-alike maze

Fourteen rooms with the same description. The exits are deliberately
inconsistent so that you can map the maze by trying directions; dropping
objects is the intended way to tell rooms apart. The only entrances are
`wmist` (via `like1`) and `brink` (via `like12`/`like13`); the only exits
are up from `like1` and down from `brink`.

| Room | Exits |
| --- | --- |
| `like1` (42) | `u`→wmist; `n`→like1; `e`→like2; `s`→like4; `w`→like11 |
| `like2` (43) | `w`→like1; `s`→like3; `e`→like4 |
| `like3` (44) | `e`→like2; `d`→dead5; `s`→like6; `n`→dead9 |
| `like4` (45) | `w`→like1; `n`→like2; `e`→dead3; `s`→dead4; `u`/`d`→like14 |
| `like5` (49) | `e`→like6; `w`→like7 |
| `like6` (50) | `e`→like3; `w`→like5; `d`→like7; `s`→like8 |
| `like7` (51) | `w`→like5; `u`→like6; `e`→like8; `s`→like9 |
| `like8` (52) | `w`→like6; `e`→like7; `s`→like8; `u`→like9; `n`→like10; `d`→dead11 |
| `like9` (53) | `w`→like7; `n`→like8; `s`→dead6 |
| `like10` (55) | `w`→like8; `n`→like10; `d`→dead7; `e`→brink |
| `like11` (80) | `n`→like1; `w`/`s`→like11; `e`→dead1 |
| `like12` (83) | `s`→brink; `e`→like13; `w`→dead10 |
| `like13` (84) | `n`→brink; `w`→like12; `nw`→dead2 |
| `like14` (87) | `u`/`d`→like4 |

`like14` is a two-way stub: up and down both return to `like4`.

## Region 6 — The all-different maze

Eleven rooms, each with a distinct description, laid out as an 11×11 Latin
square over the ten directions. Every room is reachable from every other
room in exactly one way per direction. The entrance is `diff0` (down from
the west end of the long hall, condition 100 — dwarves cannot follow you),
and `diff10` has a south exit to the vending-machine dead end.

| Room | Exits (N, S, E, W, NE, SE, NW, SW, U, D) |
| --- | --- |
| `diff0` (107) | diff9, diff1, diff7, diff8, diff3, diff4, diff6, diff2, diff5, **wlong** |
| `diff1` (131) | diff8, diff9, diff10, diff0, diff5, diff2, diff3, diff4, diff6, diff7 |
| `diff2` (132) | diff3, diff4, diff8, diff5, diff7, diff10, diff0, diff6, diff1, diff9 |
| `diff3` (133) | diff7, diff10, diff6, diff2, diff4, diff9, diff8, diff5, diff0, diff1 |
| `diff4` (134) | diff1, diff7, diff5, diff9, diff0, diff3, diff2, diff10, diff8, diff6 |
| `diff5` (135) | diff0, diff3, diff4, diff6, diff8, diff1, diff9, diff7, diff10, diff2 |
| `diff6` (136) | diff10, diff5, diff0, diff1, diff9, diff8, diff7, diff3, diff2, diff4 |
| `diff7` (137) | diff6, diff2, diff9, diff10, diff1, diff0, diff5, diff8, diff4, diff3 |
| `diff8` (138) | diff5, diff6, diff1, diff4, diff2, diff7, diff10, diff9, diff3, diff0 |
| `diff9` (139) | diff4, diff8, diff2, diff3, diff10, diff6, diff1, diff0, diff7, diff5 |
| `diff10` (112) | diff2, **pony**, diff3, diff7, diff6, diff5, diff4, diff1, diff9, diff8 |

The descriptions differ only in word order: "maze of twisty little
passages", "twisting maze of little passages", and so on — a mnemonic
device. The dead end `pony` has a vending machine.

## Region 7 — The Twopit Room and the west area

The Twopit Room has two pits; the east pit contains oil, and the west pit
contains the plant. Climbing the plant is the only way to the Giant Room and
the waterfall. West of the pits is the Slab Room, then the secret canyon
above it, then the mirror canyon and the reservoir.

| Room | Flags | Exits |
| --- | --- | --- |
| `bedquilt` (65) | dark | `e`→complex; `w`→cheese; `s`(80%)→remark 7; `slab`→slab; `u`(80%)→remark 7; `u`(50%)→abovep; `u`→dusty; `n`(60%)→remark 7; `n`(75%)→low; `n`→sjunc; `d`(80%)→remark 7; `d`→ante |
| `cheese` (66) | dark | `ne`→bedquilt; `w`→e2pit; `s`(80%)→remark 7; `canyon`→tall; `e`→soft; `nw`(50%)→remark 7; `oriental`→oriental |
| `soft` (96) | dark | `w`/`out`→cheese |
| `e2pit` (67) | dark | `e`→cheese; `w`/`across`→w2pit; `d`/`pit`→epit |
| `w2pit` (23) | dark | `e`/`across`→e2pit; `w`/`slab`→slab; `d`/`pit`→wpit; `hole`→*"It is too far up for you to reach."* |
| `epit` (24) | dark, liquid, **oil** | `u`/`out`→e2pit |
| `wpit` (25) | dark | `u`/`out`→w2pit; `climb`(plant≠4)→check; `climb`→climb |
| `slab` (68) | dark | `s`→w2pit; `u`/`climb`→abover; `n`→bedquilt |
| `abover` (69) | dark | `d`/`slab`→slab; `s`(dragon gone)→scan2; `s`→scan1; `n`→mirror; `reservoir`→res |
| `mirror` (109) | dark | `s`→abover; `n`/`reservoir`→res |
| `res` (113) | dark, liquid | `s`/`out`→mirror |
| `scan1` (119) | dark | `n`/`out`→abover; `e`/`forward`→*"The dragon looks rather nasty.  You'd best not try to get by."* |
| `scan2` (120) | dark | `n`→abover; `e`→secret |
| `scan3` (121) | dark | `e`/`out`→secret; `n`/`forward`→remark 11 |
| `secret` (74) | dark | `e`→hmk; `w`(dragon gone)→scan2; `w`→scan3; `d`→wide |
| `wide` (75) | dark | `s`→tight; `n`→tall |
| `tight` (76) | dark | `n`→wide |
| `tall` (77) | dark | `e`→wide; `w`→boulders; `n`/`crawl`→cheese |
| `boulders` (78) | dark | `s`→tall |

`scan1`/`scan2`/`scan3` are three views of the dragon's canyon; killing the
dragon merges them into `scan2`. `abover`'s south exit chooses `scan2` when
the dragon is dead (`prop[DRAGON] != 0`), otherwise `scan1`.

## Region 8 — The Giant Room and the waterfall

Reached by climbing the gigantic plant from the west pit. Contains the eggs,
the rusty door, and the trident; the only way on is through the door, which
must be oiled.

| Room | Flags | Exits |
| --- | --- | --- |
| `narrow` (88) | dark | `d`/`climb`/`e`→wpit; `jump`→neck; `w`/`giant`→giant |
| `giant` (92) | dark | `s`→narrow; `e`→block; `n`→immense |
| `block` (93) | dark | `s`/`giant`/`out`→giant |
| `immense` (94) | dark | `s`/`giant`/`passage`→giant; `n`(door≠0)/`enter`/`cavern`→falls; `n`→*"The door is extremely rusty and refuses to open."* |
| `falls` (95) | dark, liquid | `s`/`out`→immense; `giant`→giant; `w`→steep |
| `steep` (91) | dark | `n`/`cavern`/`passage`→falls; `d`/`climb`→low |

## Region 9 — The east area: Bedquilt, Oriental Room, misty cavern

The complex junction connects the long crawl, the Shell Room cavelet, the
anteroom to Witt's End, and Bedquilt. The Oriental Room and the misty
cavern lead to the alcove and the Plover Room.

| Room | Flags | Exits |
| --- | --- | --- |
| `dusty` (39) | dark | `e`/`passage`→dirty; `d`/`hole`/`floor`→complex; `bedquilt`→bedquilt |
| `dirty` (36) | dark | `e`/`crawl`→clean; `u`/`hole`→ns; `w`→dusty; `bedquilt`→bedquilt |
| `clean` (37) | dark | `w`/`crawl`→dirty; `d`/`pit`/`climb`→wet |
| `wet` (38) | dark, liquid | `climb`/`u`/`out`→clean; `slit`/`stream`/`d`/`upstream`/`downstream`→*"You don't fit through a two-inch slit!"* |
| `complex` (64) | dark | `u`/`climb`/`room`→dusty; `w`/`bedquilt`→bedquilt; `n`/`shell`→shell; `e`→ante |
| `shell` (103) | dark | `u`/`hall`→arch; `d`→ragged; `s`(carry CLAM)→remark 5; `s`(carry OYSTER)→remark 6; `s`→complex |
| `arch` (102) | dark | `d`/`shell`/`out`→shell |
| `ragged` (104) | dark | `u`/`shell`→shell; `d`→sac |
| `sac` (105) | dark | `u`/`out`→ragged; `shell`→shell |
| `ante` (106) | dark | `u`→complex; `w`→bedquilt; `e`→witt |
| `witt` (108) | dark, witt hint | `e`(95%)/`n`/`s`/`ne`/`se`/`sw`/`nw`/`u`/`d`→remark 7; `e`→ante; `w`→remark 8 |
| `low` (72) | dark | `bedquilt`→bedquilt; `sw`→scorr; `n`→crawl; `se`/`oriental`→oriental |
| `crawl` (73) | dark | `s`/`crawl`/`out`→low |
| `oriental` (97) | dark | `se`→cheese; `w`/`crawl`→low; `u`/`n`/`cavern`→misty |
| `misty` (98) | dark | `s`/`oriental`→oriental; `w`→alcove |
| `alcove` (99) | dark, dark hint | `nw`/`cavern`→misty; `e`/`passage`→ppass; `e`→proom |
| `proom` (100) | lighted, dark hint | `w`/`passage`/`out`→ppass; `w`→alcove; `plover`(carry EMERALD)→pdrop; `plover`→y2; `ne`/`dark`→droom |
| `droom` (101) | dark, dark hint | `s`/`plover`/`out`→proom |

The two `proom`/`alcove` `e`/`w` instructions that are marked "never
performed" exist so that `go back` can find a reverse direction through the
tight tunnel.

## Region 10 — The troll bridge and the hidden cave

The sloping corridor west of the low room leads up to the southwest side of
a chasm. The troll blocks it until paid (or chased by the bear). Across the
chasm is a hidden cave: a corridor, a fork, a warm junction, a volcano
view, a boulder chamber, a limestone passage, a barren room with the bear
and chain, and the two "repository" storage rooms.

| Room | Flags | Exits |
| --- | --- | --- |
| `scorr` (118) | dark | `d`→low; `u`→swside |
| `swside` (117) | dark | `sw`→scorr; `over`(troll here)/`across`/`cross`/`ne`→remark 12; `over`(bridge≠0)→remark 13; `over`→troll; `jump`(bridge≠0)→lose; `jump`→remark 3 |
| `dead0` (63) | dark | `s`/`out`→cross |
| `dead1` (81) | dark, twist hint | `w`/`out`→like11 |
| `dead2` (114) | dark | `se`→like13 |
| `dead3` (46) | dark, twist hint | `w`/`out`→like4 |
| `dead4` (47) | dark, twist hint | `e`/`out`→like4 |
| `dead5` (48) | dark, twist hint | `u`/`out`→like3 |
| `dead6` (54) | dark, twist hint | `w`/`out`→like9 |
| `dead7` (56) | dark, twist hint | `u`/`out`→like10 |
| `dead8` (58) | dark | `e`/`out`→brink |
| `dead9` (82) | dark, twist hint | `s`/`out`→like3 |
| `dead10` (85) | dark, twist hint | `e`/`out`→like12 |
| `dead11` (86) | dark, twist hint | `u`/`out`→like8 |
| `neside` (122) | dark | `ne`→corr; `over`(troll here)/`across`/`cross`/`sw`→remark 12; `over`→troll; `jump`→remark 3; `fork`→fork; `view`→view; `barren`→fbarr |
| `corr` (123) | dark | `w`→neside; `e`/`fork`→fork; `view`→view; `barren`→fbarr |
| `fork` (124) | dark | `w`→corr; `ne`/`l`→warm; `se`/`r`/`d`→lime; `view`→view; `barren`→fbarr |
| `warm` (125) | dark | `s`/`fork`→fork; `n`/`view`→view; `e`/`crawl`→chamber |
| `view` (126) | lighted | `s`/`passage`/`out`→warm; `fork`→fork; `d`/`jump`→*"Don't be ridiculous!"* |
| `chamber` (127) | dark | `w`/`out`/`crawl`→warm; `fork`→fork; `view`→view |
| `lime` (128) | dark | `n`/`u`/`fork`→fork; `s`/`d`/`barren`→fbarr; `view`→view |
| `fbarr` (129) | dark | `w`/`u`→lime; `fork`→fork; `e`/`in`/`barren`/`enter`→barr; `view`→view |
| `barr` (130) | dark | `w`/`out`→fbarr; `fork`→fork; `view`→view |
| `neend` (115) | lighted | `sw`→swend |
| `swend` (116) | lighted | `ne`→neend; `d`→remark 2 |

The `view`, `fork`, and `barren` shortcuts are one-way "long distance"
motions that work from every room in the hidden cave; `view` is the only
lit room there, thanks to the volcano.

## The special destinations

These are not rooms. They are values greater than `max_loc` that trigger
code or remarks.

| Name | Kind | Behavior |
| --- | --- | --- |
| `crack` | forced location | prints the crack message, returns you to `spit` |
| `neck` | forced location | broken neck; death |
| `lose` | forced location | "You didn't make it."; death |
| `cant` | forced location | "The dome is unclimbable."; returns to `emist` |
| `climb` | forced location | clamber up the plant; goes to `narrow` |
| `check` | forced location | if plant ≠ 2 → `upnout`, else `didit` |
| `snaked` | forced location | "You can't get by the snake."; back to `hmk` |
| `thru` | forced location | crawl parallel to the Hall of Mists; to `wmist` |
| `duck` | forced location | same text; to `wfiss` |
| `sewer` | forced location | sewer pipes; back to `house` |
| `upnout` | forced location | nothing to climb; back to `wpit` |
| `didit` | forced location | climbed out of the pit; to `w2pit` |
| `ppass` | special code | the plover-alcove tunnel |
| `pdrop` | special code | drop the emerald during plover transport |
| `troll` | special code | cross the troll bridge |

`forced_move(loc)` is true for every location code ≥ `crack`. Arriving at
one immediately triggers another move without asking for input.

## The complete list of remarks

Remarks are printed when a conditional exit fails or when a special
"stay put" destination is used. They are numbered from 1 in the order the
program defines them; there are fourteen of them.

1. `You don't fit through a two-inch slit!` (slit)
2. `You can't go through a locked steel grate!` (outside)
3. `I respectfully suggest you go across the bridge instead of jumping.` (both banks of the fissure)
4. `There is no way across the fissure.` (both banks of the fissure)
5. `You can't fit this five-foot clam through that little passage!` (shell)
6. `You can't fit this five-foot oyster through that little passage!` (shell)
7. `You have crawled around in some little holes and wound up back in the main passage.` (Witt's End)
8. `You have crawled around in some little holes and found your way blocked by a recent cave-in.  You are now back in the main passage.` (Witt's End, west)
9. `It is too far up for you to reach.` (west Twopit Room)
10. `The door is extremely rusty and refuses to open.` (immense passage)
11. `The dragon looks rather nasty.  You'd best not try to get by.` (dragon canyon)
12. `The troll refuses to let you cross.` (southwest and northeast chasms)
13. `There is no longer any way across the chasm.` (southwest chasm)
14. `Don't be ridiculous!` (breath-taking view, down/jump)
