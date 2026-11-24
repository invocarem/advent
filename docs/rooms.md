# Room Descriptions

Every location's text, exactly as the program prints it. `long` is shown
the first time you arrive and every fifth visit (unless you type `brief`,
which makes it first-visit only); `short` is used in between. `look`
always forces the long text. A room with no short text always shows its
long text. A room with no long text (only `check` has none) prints nothing.

Locations are listed with their numeric code and grouped by region, matching
[world.md](world.md).

---

## Above ground

### road (1)

> You are standing at the end of a road before a small brick building.
> Around you is a forest.  A small stream flows out of the building and
> down a gully.

*short:* You're at end of road again.

### hill (2)

> You have walked up a hill, still in the forest.  The road slopes back
> down the other side of the hill.  There is a building in the distance.

*short:* You're at hill in road.

### house (3)

> You are inside a building, a well house for a large spring.

*short:* You're inside building.

### valley (4)

> You are in a valley in the forest beside a stream tumbling along a
> rocky bed.

*short:* You're in valley.

### forest (5)

> You are in open forest, with a deep valley to one side.

*short:* You're in forest.

### woods (6)

> You are in open forest near both a valley and a road.

*short:* You're in forest.

### slit (7)

> At your feet all the water of the stream splashes into a 2-inch slit
> in the rock.  Downstream the streambed is bare rock.

*short:* You're at slit in streambed.

### outside (8)

> You are in a 20-foot depression floored with bare dirt.  Set into the
> dirt is a strong steel grate mounted in concrete.  A dry streambed
> leads into the depression.

*short:* You're outside grate.

---

## The upper cave

### inside (9)

> You are in a small chamber beneath a 3x3 steel grate to the surface.
> A low crawl over cobbles leads inwards to the west.

*short:* You're below the grate.

### cobbles (10)

> You are crawling over cobbles in a low passage.  There is a dim light
> at the east end of the passage.

*short:* You're in cobble crawl.

### debris (11)

> You are in a debris room filled with stuff washed in from the surface.
> A low wide passage with cobbles becomes plugged with mud and debris
> here, but an awkward canyon leads upward and west.  A note on the wall
> says "MAGIC WORD XYZZY".

*short:* You're in debris room.

### awk (12)

> You are in an awkward sloping east/west canyon.

*(no short form)*

### bird (13)

> You are in a splendid chamber thirty feet high.  The walls are frozen
> rivers of orange stone.  An awkward canyon and a good passage exit
> from east and west sides of the chamber.

*short:* You're in bird chamber.

### spit (14)

> At your feet is a small pit breathing traces of white mist.  An east
> passage ends here except for a small crack leading on.

*short:* You're at top of small pit.

---

## The Hall of Mists

### emist (15)

> You are at one end of a vast hall stretching forward out of sight to
> the west.  There are openings to either side.  Nearby, a wide stone
> staircase leads downward.  The hall is filled with wisps of white mist
> swaying to and fro almost as if alive.  A cold wind blows up the
> staircase.  There is a passage at the top of a dome behind you.

*short:* You're in Hall of Mists.

### nugget (18)

> This is a low room with a crude note on the wall.  The note says,
> "You won't get it up the steps".

*short:* You're in nugget of gold room.

### efiss (17)

> You are on the east bank of a fissure slicing clear across the hall.
> The mist is quite thick here, and the fissure is too wide to jump.

*short:* You're on east bank of fissure.

### wfiss (27)

> You are on the west side of the fissure in the Hall of Mists.

*(no short form)*

### wmist (41)

> You are at the west end of the Hall of Mists.  A low wide crawl
> continues west and another goes north.  To the south is a little
> passage 6 feet off the floor.

*short:* You're at west end of Hall of Mists.

### brink (57)

> You are on the brink of a thirty-foot pit with a massive orange column
> down one wall.  You could climb down here but you could not get back
> up.  The maze continues at this level.

*short:* You're at brink of pit.

### elong (60)

> You are at the east end of a very long hall apparently without side
> chambers.  To the east a low wide crawl slants up.  To the north a
> round two-foot hole slants down.

*short:* You're at east end of long hall.

### wlong (61)

> You are at the west end of a very long featureless hall.  The hall
> joins up with a narrow north/south passage.

*short:* You're at west end of long hall.

### cross (62)

> You are at a crossover of a high N/S passage and a low E/W one.

*(no short form)*

### pony (140)

> Dead end.

*(no short form — the vending machine is here)*

---

## The all-alike maze

Every one of `like1` (42) through `like14` (87) prints:

> You are in a maze of twisty little passages, all alike.

*(no short form; the hint flag `twist` is set in all fourteen rooms)*

---

## The all-different maze

These eleven rooms differ only in the order of the words "maze",
"twisty"/"twisting", "little", and "passages". They are, in code order:

| Room | Text |
| --- | --- |
| `diff0` (107) | You are in a maze of twisty little passages, all different. |
| `diff1` (131) | You are in a maze of twisting little passages, all different. |
| `diff2` (132) | You are in a little maze of twisty passages, all different. |
| `diff3` (133) | You are in a twisting maze of little passages, all different. |
| `diff4` (134) | You are in a twisting little maze of passages, all different. |
| `diff5` (135) | You are in a twisty little maze of passages, all different. |
| `diff6` (136) | You are in a twisty maze of little passages, all different. |
| `diff7` (137) | You are in a little twisty maze of passages, all different. |
| `diff8` (138) | You are in a maze of little twisting passages, all different. |
| `diff9` (139) | You are in a maze of little twisty passages, all different. |
| `diff10` (112) | You are in a little maze of twisting passages, all different. |

---

## The Hall of the Mountain King and around

### hmk (19)

> You are in the Hall of the Mountain King, with passages off in all
> directions.

*short:* You're in Hall of Mt King.

### west (30)

> You are in the west side chamber of the Hall of the Mountain King.
> A passage continues west and up here.

*short:* You're in west side chamber.

### south (29)

> You are in the south side chamber.

*(no short form)*

### ns (28)

> You are in a low N/S passage at a hole in the floor.  The hole goes
> down to an E/W passage.

*short:* You're in N/S passage.

### y2 (33)

> You are in a large room, with a passage to the south, a passage to the
> west, and a wall of broken rock to the east.  There is a large "Y2" on
> a rock in the room's center.

*short:* You're at "Y2".

### jumble (34)

> You are in a jumble of rock, with cracks everywhere.

*(no short form)*

### windoe (35)

> You're at a low window overlooking a huge pit, which extends up out of
> sight.  A floor is indistinctly visible over 50 feet below.  Traces of
> white mist cover the floor of the pit, becoming thicker to the right.
> Marks in the dust around the window would seem to indicate that
> someone has been here recently.  Directly across the pit from you and
> 25 feet away there is a similar window looking into a lighted room.
> A shadowy figure can be seen there peering back at you.

*short:* You're at window on pit.

---

## Bedquilt, the pits, and the west area

### bedquilt (65)

> You are in Bedquilt, a long east/west passage with holes everywhere.
> To explore at random select north, south, up, or down.

*short:* You're in Bedquilt.

### cheese (66)

> You are in a room whose walls resemble Swiss cheese.  Obvious passages
> go west, east, NE, and NW.  Part of the room is occupied by a large
> bedrock block.

*short:* You're in Swiss cheese room.

### soft (96)

> You are in the Soft Room.  The walls are covered with heavy curtains,
> the floor with a thick pile carpet.  Moss covers the ceiling.

*short:* You're in Soft Room.

### e2pit (67)

> You are at the east end of the Twopit Room.  The floor here is
> littered with thin rock slabs, which make it easy to descend the pits.
> There is a path here bypassing the pits to connect passages from east
> and west.  There are holes all over, but the only big one is on the
> wall directly over the west pit where you can't get to it.

*short:* You're at east end of Twopit Room.

### w2pit (23)

> You are at the west end of the Twopit Room.  There is a large hole in
> the wall above the pit at this end of the room.

*short:* You're at west end of Twopit Room.

### epit (24)

> You are at the bottom of the eastern pit in the Twopit Room.  There is
> a small pool of oil in one corner of the pit.

*short:* You're in east pit.

### wpit (25)

> You are at the bottom of the western pit in the Twopit Room.  There is
> a large hole in the wall about 25 feet above you.

*short:* You're in west pit.

### narrow (88)

> You are in a long, narrow corridor stretching out of sight to the
> west.  At the eastern end is a hole through which you can see a
> profusion of leaves.

*short:* You're in narrow corridor.

### slab (68)

> You are in a large low circular chamber whose floor is an immense slab
> fallen from the ceiling (Slab Room).  There once were large passages
> to the east and west, but they are now filled with boulders.  Low
> small passages go north and south, and the south one quickly bends
> east around the boulders.

*short:* You're in Slab Room.

### abover (69)

> You are in a secret N/S canyon above a large room.

*(no short form)*

### mirror (109)

> You are in a north/south canyon about 25 feet across.  The floor is
> covered by white mist seeping in from the north.  The walls extend
> upward for well over 100 feet.  Suspended from some unseen point far
> above you, an enormous two-sided mirror is hanging parallel to and
> midway between the canyon walls.  (The mirror is obviously provided
> for the use of the dwarves, who as you know are extremely vain.)
> A small window can be seen in either wall, some fifty feet up.

*short:* You're in mirror canyon.

### res (113)

> You are at the edge of a large underground reservoir.  An opaque cloud
> of white mist fills the room and rises rapidly upward.  The lake is
> fed by a stream, which tumbles out of a hole in the wall about 10 feet
> overhead and splashes noisily into the water somewhere within the
> mist.  The only passage goes back toward the south.

*short:* You're at reservoir.

### scan1 (119), scan2 (120), scan3 (121)

All three print:

> You are in a secret canyon that exits to the north and east.

*(no short form)*

### secret (74)

> You are in a secret canyon, which here runs E/W.  It crosses over a
> very tight canyon 15 feet below.  If you go down you may not be able
> to get back up.

*short:* You're in secret E/W canyon above tight canyon.

### wide (75)

> You are at a wide place in a very tight N/S canyon.

*(no short form)*

### tight (76)

> The canyon here becomes too tight to go further south.

*(no short form)*

### tall (77)

> You are in a tall E/W canyon.  A low tight crawl goes 3 feet north and
> seems to open up.

*short:* You're in tall E/W canyon.

### boulders (78)

> The canyon runs into a mass of boulders --- dead end.

*(no short form)*

---

## The Giant Room and the waterfall

### giant (92)

> You are in the Giant Room.  The ceiling here is too high up for your
> lamp to show it.  Cavernous passages lead east, north, and south.  On
> the west wall is scrawled the inscription, "FEE FIE FOE FOO" [sic].

*short:* You're in Giant Room.

### block (93)

> The passage here is blocked by a recent cave-in.

*(no short form)*

### immense (94)

> You are at one end of an immense north/south passage.

*(no short form)*

### falls (95)

> You are in a magnificent cavern with a rushing stream, which cascades
> over a sparkling waterfall into a roaring whirlpool that disappears
> through a hole in the floor.  Passages exit to the south and west.

*short:* You're in cavern with waterfall.

### steep (91)

> You are at the top of a steep incline above a large room.  You could
> climb down here, but you would not be able to climb up.  There is a
> passage leading back to the north.

*short:* You're at steep incline above large room.

---

## The east area

### dirty (36)

> You are in a dirty broken passage.  To the east is a crawl.  To the
> west is a large passage.  Above you is a hole to another passage.

*short:* You're in dirty passage.

### clean (37)

> You are on the brink of a small clean climbable pit.  A crawl leads
> west.

*short:* You're by a clean pit.

### wet (38)

> You are in the bottom of a small pit with a little stream, which
> enters and exits through tiny slits.

*short:* You're in pit by stream.

### dusty (39)

> You are in a large room full of dusty rocks.  There is a big hole in
> the floor.  There are cracks everywhere, and a passage leading east.

*short:* You're in dusty rock room.

### complex (64)

> You are at a complex junction.  A low hands-and-knees passage from the
> north joins a higher crawl from the east to make a walking passage
> going west.  There is also a large room above.  The air is damp here.

*short:* You're at complex junction.

### shell (103)

> You're in a large room carved out of sedimentary rock.  The floor
> and walls are littered with bits of shells embedded in the stone.
> A shallow passage proceeds downward, and a somewhat steeper one
> leads up.  A low hands-and-knees passage enters from the south.

*short:* You're in Shell Room.

### arch (102)

> You are in an arched hall.  A coral passage once continued up and east
> from here, but is now blocked by debris.  The air smells of sea water.

*short:* You're in arched hall.

### ragged (104)

> You are in a long sloping corridor with ragged sharp walls.

*(no short form)*

### sac (105)

> You are in a cul-de-sac about eight feet across.

*(no short form)*

### ante (106)

> You are in an anteroom leading to a large passage to the east.  Small
> passages go west and up.  The remnants of recent digging are evident.
> A sign in midair here says "CAVE UNDER CONSTRUCTION BEYOND THIS POINT.
> PROCEED AT OWN RISK.  [WITT CONSTRUCTION COMPANY]"

*short:* You're in anteroom.

### witt (108)

> You are at Witt's End.  Passages lead off in "all" directions.

*short:* You're at Witt's End.

### low (72)

> You are in a large low room.  Crawls lead north, SE, and SW.

*(no short form)*

### crawl (73)

> Dead end crawl.

*(no short form)*

### window (110)

> You're at a low window overlooking a huge pit, which extends up out of
> sight.  A floor is indistinctly visible over 50 feet below.  Traces of
> white mist cover the floor of the pit, becoming thicker to the left.
> Marks in the dust around the window would seem to indicate that
> someone has been here recently.  Directly across the pit from you and
> 25 feet away there is a similar window looking into a lighted room.
> A shadowy figure can be seen there peering back at you.

*short:* You're at window on pit.

### oriental (97)

> This is the Oriental Room.  Ancient oriental cave drawings cover the
> walls.  A gently sloping passage leads upward to the north, another
> passage leads SE, and a hands-and-knees crawl leads west.

*short:* You're in Oriental Room.

### misty (98)

> You are following a wide path around the outer edge of a large cavern.
> Far below, through a heavy white mist, strange splashing noises can be
> heard.  The mist rises up through a fissure in the ceiling.  The path
> exits to the south and west.

*short:* You're in misty cavern.

### alcove (99)

> You are in an alcove.  A small NW path seems to widen after a short
> distance.  An extremely tight tunnel leads east.  It looks like a very
> tight squeeze.  An eerie light can be seen at the other end.

*short:* You're in alcove.

### proom (100)

> You're in a small chamber lit by an eerie green light.  An extremely
> narrow tunnel exits to the west.  A dark corridor leads NE.

*short:* You're in Plover Room.

### droom (101)

> You're in the Dark-Room.  A corridor leading south is the only exit.

*short:* You're in Dark-Room.

---

## The troll bridge and the hidden cave

### scorr (118)

> You are in a long winding corridor sloping out of sight in both
> directions.

*short:* You're in sloping corridor.

### swside (117)

> You are on one side of a large, deep chasm.  A heavy white mist rising
> up from below obscures all view of the far side.  A SW path leads away
> from the chasm into a winding corridor.

*short:* You're on SW side of chasm.

### dead0 (63) … dead11 (86)

All twelve print:

> Dead end.

*(no short form)*

### neside (122)

> You are on the far side of the chasm.  A NE path leads away from the
> chasm on this side.

*short:* You're on NE side of chasm.

### corr (123)

> You're in a long east/west corridor.  A faint rumbling noise can be
> heard in the distance.

*short:* You're in corridor.

### fork (124)

> The path forks here.  The left fork leads northeast.  A dull rumbling
> seems to get louder in that direction.  The right fork leads southeast
> down a gentle slope.  The main corridor enters from the west.

*short:* You're at fork in path.

### warm (125)

> The walls are quite warm here.  From the north can be heard a steady
> roar, so loud that the entire cave seems to be trembling.  Another
> passage leads south, and a low crawl goes east.

*short:* You're at junction with warm walls.

### view (126)

> You are on the edge of a breath-taking view.  Far below you is an
> active volcano, from which great gouts of molten lava come surging
> out, cascading back down into the depths.  The glowing rock fills the
> farthest reaches of the cavern with a blood-red glare, giving every-
> thing an eerie, macabre appearance.  The air is filled with flickering
> sparks of ash and a heavy smell of brimstone.  The walls are hot to
> the touch, and the thundering of the volcano drowns out all other
> sounds.  Embedded in the jagged roof far overhead are myriad twisted
> formations, composed of pure white alabaster, which scatter the murky
> light into sinister apparitions upon the walls.  To one side is a deep
> gorge, filled with a bizarre chaos of tortured rock that seems to have
> been crafted by the Devil himself.  An immense river of fire crashes
> out from the depths of the volcano, burns its way through the gorge,
> and plummets into a bottomless pit far off to your left.  To the
> right, an immense geyser of blistering steam erupts continuously
> from a barren island in the center of a sulfurous lake, which bubbles
> ominously.  The far right wall is aflame with an incandescence of its
> own, which lends an additional infernal splendor to the already
> hellish scene.  A dark, foreboding passage exits to the south.

*short:* You're at breath-taking view.

### chamber (127)

> You are in a small chamber filled with large boulders.  The walls are
> very warm, causing the air in the room to be almost stifling from the
> heat.  The only exit is a crawl heading west, through which a low
> rumbling noise is coming.

*short:* You're in chamber of boulders.

### lime (128)

> You are walking along a gently sloping north/south passage lined with
> oddly shaped limestone formations.

*short:* You're in limestone passage.

### fbarr (129)

> You are standing at the entrance to a large, barren room.  A sign
> posted above the entrance reads:  "CAUTION!  BEAR IN ROOM!"

*short:* You're in front of barren room.

### barr (130)

> You are inside a barren room.  The center of the room is completely
> empty except for some dust.  Marks in the dust lead away toward the
> far end of the room.  The only exit is the way you came in.

*short:* You're in barren room.

### neend (115)

> You are at the northeast end of an immense room, even larger than the
> Giant Room.  It appears to be a repository for the "Adventure"
> program.  Massive torches far overhead bathe the room with smoky
> yellow light.  Scattered about you can be seen a pile of bottles (all
> of them empty), a nursery of young beanstalks murmuring quietly, a bed
> of oysters, a bundle of black rods with rusty stars on their ends, and
> a collection of brass lanterns.  Off to one side a great many dwarves
> are sleeping on the floor, snoring loudly.  A sign nearby reads:  "DO
> NOT DISTURB THE DWARVES!"  An immense mirror is hanging against one
> wall, and stretches to the other end of the room, where various other
> sundry objects can be glimpsed dimly in the distance.

*short:* You're at NE end.

### swend (116)

> You are at the southwest end of the repository.  To one side is a pit
> full of fierce green snakes.  On the other side is a row of small
> wicker cages, each of which contains a little sulking bird.  In one
> corner is a bundle of black rods with rusty marks on their ends.
> A large number of velvet pillows are scattered about on the floor.
> A vast mirror stretches off to the northeast.  At your feet is a
> large steel grate, next to which is a sign that reads, "TREASURE
> VAULT.  KEYS IN MAIN OFFICE."

*short:* You're at SW end.

---

## Pseudo-locations

These are not rooms you can stay in. Arriving prints the text and forces
another move (see [world.md](world.md#the-special-destinations)).

| Code | Text |
| --- | --- |
| `crack` (16) | The crack is far too small for you to follow. |
| `neck` (20) | You are at the bottom of the pit with a broken neck. |
| `lose` (21) | You didn't make it. |
| `cant` (22) | The dome is unclimbable. |
| `climb` (26) | You clamber up the plant and scurry through the hole at the top. |
| `check` (31) | *(no text)* |
| `snaked` (32) | You can't get by the snake. |
| `thru` (40) | You have crawled through a very low wide passage parallel to and north of the Hall of Mists. |
| `duck` (59) | You have crawled through a very low wide passage parallel to and north of the Hall of Mists. |
| `sewer` (79) | The stream flows out through a pair of 1-foot-diameter sewer pipes. It would be advisable to use the exit. |
| `upnout` (89) | There is nothing here to climb.  Use "up" or "out" to leave the pit. |
| `didit` (90) | You have climbed up the plant and out of the pit. |
