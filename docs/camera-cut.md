# Speaker statistics, camera cut, EDL

*Auf Deutsch: [camera-cut.de.md](camera-cut.de.md). Back to the [contents](README.md).*

## Speaker statistics, camera cut, EDL

With multitrack the script knows who spoke when: separated by voice on
this machine, or measured from the tracks against each other -- both in
[Speech recognition and speaker separation](speech.md). Out of that it
builds the camera cut:

* Whoever speaks alone gets their camera, with a lead-in.
* A short "yes" does not: below **Speaks at least** the picture stays
  where it is.
* In silence the wide shot runs.
* Where a shot stands for a long time, the wide shot drops in at a
  sentence boundary.

**When several speak at once**, a camera showing exactly those speakers
wins -- one on both hosts, say. If none fits exactly, the smallest camera
carrying all the speakers does. Only where no camera covers them does the
wide shot take over. Who is on which camera comes from the assignment:
two speakers on one camera means it shows both.

The output folder gets `_speakers.csv`, `_speakers.edl`, `_cameracut.csv`
and `_cameracut.edl`. The heads are
`Speaker,Start TC,End TC,Time from start,Duration s` and
`Shot,Camera,Start TC,End TC,Duration s`, the EDLs are titled `Speakers`
and `Camera cut`.

### The knobs

In multitrack every value can be typed into the interface: on tab
**3. Resolve cut**, in the box **Camera cut**, one field per value, with
the unit and a short line beside it.

![The knobs for the camera cut](images/resolve-cut.png)

*Tab 3: the values on the left, the preview on the right.*

Four fields shape the cut itself:

* **Minimum Edit Duration** -- 3 s, this long a shot stands at least
  (on the command line `--min-edit-duration`)
* **Speaks at least** -- 1.5 s, below this the camera does not follow
  (on the command line `--min-speech-to-switch`)
* **Edit Change Delay** -- 0.3 s, this much later than the sound the
  picture cuts (on the command line `--edit-change-delay`)
* **Reaction cut earlier** -- 1.5 s, after a question the answer is on
  screen this much earlier (on the command line `--reaction-lead`)

Four more shape the wide shot:

* **Wide shot after** -- 40 s, from this hold time on, a look at the
  wide shot (on the command line `--wide-after`)
* **Wide shot holds** -- 5 s, the inserted wide shot stands at least
  this long (on the command line `--wide-length`)
* **Wide shot at most** -- 15 s, and at most this long (on the command
  line `--wide-most`)
* **Wide shot at the latest** -- 120 s, upper limit for one camera in
  one piece (on the command line `--wide-latest`)

Under them stand four selectors. They say what is shown where the
speech does not say whom to show:

* **Long monologue** -- **Alternating** (on the command line
  `--on-monologue`)
* **Several speak at once** -- **Wide shot** (on the command line
  `--on-together`)
* **Recognition uncertain** -- **Wide shot** (on the command line
  `--on-uncertain`)
* **Question** -- **Answering speaker** (on the command line
  `--on-question`)

The first three also take **Listener**, **Alternating** and **No camera
change**; **Question** takes **off** and **Listener** as well.

Under the fields the tick **Wide shot for greeting at the start and
farewell at the end** keeps beginning and end on the wide shot (on the
command line `--no-wide-edges` switches it off). The opening wide shot
holds until the floor is really handed over, not until the first longer
block from somebody else.

**Speaks at least** takes care of short interjections ("mhm", "yes
exactly"). A shot that still comes out too short falls into the one
that follows, not into the one before.

### When the speech does not say whom to show

Four cases, and what each of the four selectors decides:

* **Long monologue** -- one person holds the floor past **Wide shot
  after**. **Alternating** remembers what the last break showed.
* **Several speak at once** -- and no camera shows exactly them.
* **Recognition uncertain** -- the recognition frays over a passage, or
  a name is left with nothing but scraps.
* **Question** -- the picture goes to the answer before it starts. Only
  after a question that is not the main speaker's, when somebody else
  takes over at once and keeps the floor.

**Listener** means whoever speaks next, and only where somebody on that
camera was heard in the last 20 seconds. Otherwise the wide shot.

**Listener** and **Alternating** show a person the program only knows
was audible shortly before. Whether they are watching, it does not know
-- it does not see the picture. The wide shot is the honest one.

Two speakers on one camera count as one for these rules: a change of
speaker between them does not change the picture.

### Preview and speakers

On the right the box **Camera cut -- preview** carries the length in its
title and one line of numbers below it: shots, median hold time, shortest
shot, longest a camera holds, and the speech time split into own camera,
wide shot and a camera without the speaker. The last figure stands in the
warning colour.

On the left, under the knobs, the box **Speaker**: per speaker the speech
time, the share, the number of blocks and their average length, plus a
row of silence. The heading names the source -- **Speakers, separated by
voice** or **Speakers, self-measured from the tracks**. Where two
speak at once the time counts twice, for silence it does not, so the rows
add up to more than the running time.

Both come out of the handover file of the last run, recomputed on every
change and always for the chosen window. Nothing is written or uploaded.

Where no speakers are known the box says so and offers the button
**Measure speakers now**; where the computation fails, the reason stands
in its place. Speakers that turn up later start the preview by
themselves.

### Cut band and legend

In the preview box, under the player, sits the **cut band**, in place of
the position rail: the computed cut over the full length, one bar per
shot in the colour of its camera. The scale carries minutes over the
whole thing and seconds once zoomed in. Hovering names camera, from-to
and duration; clicking sets the spot for the player. Below it the
**legend**: per camera a dot of colour and
`62 × Candidate  77 %  (48:19 min)`.

These are the colours of the clips in Resolve, with one exception: the
wide shot is shown in a pale sage. In Resolve that clip is still called
Tan. Brown, Chocolate, Cocoa, Navy and Teal are lightened on dark, Beige
is darkened on light.

The band can be zoomed. **+** shows half as much around the current
position, **−** twice as much, and the third button the whole length
again; the mouse wheel over the band does the same, as do the keys plus,
minus and 0. Zoomed in, it can be seen and heard whether a cut sits in a
pause or in the middle of a word. While playing, the section follows the
position, so it does not run out of the picture.

### The preview players

Two players show the material, and both pick their file themselves.

**On tab 2. Assignment & time window** the order is:

1. a file **containing In point and Out point**, or the jump buttons go
   nowhere
2. failing that, one with at least one of the boundaries
3. among equals the camera with **no speaker** assigned
4. among those the longest
5. never a file set to "ignore this video", never intro or outro

The project file keeps which file was last in the player and takes it
again -- as long as it covers the boundaries as well as the best
alternative. Without a timecode or a measured time axis nothing is
claimed about the boundaries; once the axis is there, the player looks
again. **to In point** and **to Out point** fetch their file themselves;
where there is none at all, a line says why nothing happened.

With **hear assigned audio** the picture runs with the sound belonging to
that camera:

* the **processed track** from auphonic.com (`final_<Name>_<TC>.wav`), at
  -16 LUFS and with a BWF timecode
* failing that the **raw recording** of the assigned speaker
* with no speaker assigned -- the wide shot -- the **Full-Mix**, if it is
  there

Raw recordings sit 16 to 36 dB below the processed sound, and the
interface cannot make them louder. The tooltip says what is running and
in which version.

**On tab 3. Resolve cut** the player in the preview box always shows
something: where there is a cut it plays the cut and switches camera at
every edge, otherwise the file with no speaker assigned. Nothing is
rendered.

The sound comes from one file throughout, preferably the **Full-Mix**,
which is at delivery level and goes into the cut timeline too. Where it
is not there yet, the camera file carrying the mix as its first audio
track is used -- the same choice as for angle 1 of the multicam clip, and
noticeably quieter.

`start_s` is the wall clock time at which programme time is zero: the
earliest audio start actually known, own timecode or measured position;
failing that the earliest camera timecode; failing that nothing. In point
and Out point move the zero point along. The spot in each camera file is
programme time minus offset, the same offset the cut timeline is built
with.

Every spot is set again until it holds; how often, and for how long, is
in [Inside the script](../development/internals.md).

### Speakers without Auphonic

On tab **2. Assignment & time window**, in the box **Processing at
auphonic.com (optional)**, the preset list carries the entry **work
without Auphonic** (on the command line `--without-auphonic`). The run
then stays local, and who speaks when is measured from the tracks. In the
log that section is headed `SPEAKERS -- MEASURED HERE`.

How the tracks are read:

* Each track is cut into blocks of 100 milliseconds.
* Each block is measured against that track's own noise floor, the
  quietest fifth of its blocks; 10 dB above that counts as speech.
* Pauses under 0.35 seconds are not speaker changes.
* Passages under 0.4 seconds do not count.

Before that the **bleed is taken out of the measurement**, not out of the
audio. Where exactly one person speaks -- that one at most 10 dB below
their own speech level, the others at least 6 dB below theirs -- the
script measures how loudly that voice arrives in the other microphones
and takes each speaker's own share back out of every track.

The coupling is measured, not assumed, so it also works with microphones
standing closer than the 3:1 rule wants. For a pair without at least
three such moments, nothing is subtracted. Where it cannot be undone --
microphones side by side, tracks too much alike -- the levels stay as
measured, and the log says why and names the worst pair.

Down to 5 dB of separation the detection is exact, well below the 9.5 dB
the 3:1 rule asks for; the measurements behind that number are in
[What was measured](../development/measurements.md).

The log says how strong the bleed was, and under it the speech time and
the number of passages per speaker. Where nothing was audible, there is
no camera cut.

The button **Measure speakers now** does the same in the interface,
before the first run: coarser than the separation by voice, but enough
to set the cut up. Speakers separated by voice take precedence as soon
as they are there, and the heading above the table says which applies.

### One camera for everybody

With several speakers on one camera the cut is made at the change of
speaker: every shot comes from the same clip and carries the name of
whoever is talking. Nothing about the picture changes. Resolve gets a
track already separated at the right places, and there each piece can be
grouped, coloured and zoomed into, so the wide shot becomes the speaker.

The cut list says so too: `_cameracut.csv` has a Speaker column, and
where one camera shows everybody the EDL carries the speaker name.

### Project file

`videopodcast-magic_<Production>.json` in the output folder holds
everything set by hand that cannot be guessed again: the file list, the
production name and the output folder, the time window, every value of
the camera cut, who belongs to which camera, the Auphonic preset, the
stereo ticks and the measured position of every file. The API key is
**not** in there.

On opening, the format of the file is checked; a file in another format
is refused. Older project files can no longer be opened.

The file appears as soon as the time axis is measured -- then still next
to the material, because there is no output folder yet. Where one is
chosen later, or the production renamed, **it moves along**. There is
always exactly one.

**Open project ...** at the top left brings it back; point at the wrong
file and `videopodcast-magic*.json` in the same folder is searched.
Beside it lies the handover file `<Production>_resolve.json` -- the
preview computes from it, and the Resolve part builds from it.

### How the wide shot is placed

A wide shot does not come by the clock. It enters on a sentence
boundary near the spot where it was wanted, and the exact point comes
from the sound: the dip in the level around that boundary. Nothing is
rolled for -- the same material gives the same cut.

It stands at least **Wide shot holds**, then runs to the end of the
sentence. Where that end lies beyond **Wide shot at most**, the last
clause break before it ends the shot. It never ends mid-sentence.

`--wide-latest` is the rip cord: where no sentence boundary turns up,
the cut happens anyway. Without a transcript the wide shot goes to the
longest speech pause nearby and stands the set minimum.

## Metrics and colour comparison

At the end of every run `<Production>_metrics.csv` appears; the log is
overwritten by the next run, this file is not. Over months it shows what
a single run hides: a recorder going slow, a camera drifting away from
the rest, bleed rising with a new setup.

It is built as `Area,Metric,Before,After,Unit` -- comma separated, with a
full stop as the decimal mark. `Area` and `Metric` stay English whatever
the language, so two runs stay comparable. Before is the track as it came
in, after as it goes out, both measured the same way.

On a German system the comma costs one step: Excel opens a file by double
click with the semicolon and puts the whole row in one column. The way in
is `Data > From Text/CSV`, where separator and the language of the
numbers are set by hand. LibreOffice asks for both by itself.

| Area | What is in it |
|---|---|
| `Audio <Name>` | loudness, peak, loudness range, clock drift in ppm, offset and residual |
| `Audio` | gain on every track, loudness target |
| `Cut` | shots, median, shortest, longest, share per camera |
| `Speech time` | seconds per speaker |
| `Colour <Name>` | brightness per camera, distance to the mean, colour position |

**The colour comparison** measures brightness and colour position at five
spots in each camera file, against the mean of all cameras rather than
against a target. From about twelve steps a warning comes with it. Both
measurements together take a few minutes on long recordings -- the
loudness measurement runs through each track twice.

## Further options on the command line

These have no counterpart in the window.

* `--reaction-gap` how soon the answer has to follow the question for
  the reaction cut to fire (3 s)
* `--reaction-hold` how much of the ten seconds after the question the
  answering speaker has to hold, as a share between 0 and 1 (0.7)
* `--no-metrics` leaves out the metrics file and the colour comparison
* `VPM_PLAYER_DEBUG=1` in front of the call puts clock, position and
  wanted value of all three players under the picture, and every attempt
  on the console
