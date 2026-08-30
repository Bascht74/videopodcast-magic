# Speaker statistics, camera cut, EDL

*Auf Deutsch: [camera-cut.de.md](camera-cut.de.md). Back to the
[contents](README.md).*

## How the cut comes about

The cut needs two people, each with a name and a camera. One person is
enough as well, as long as a second camera is there that nobody is on.
Separate recordings give two people, and so do the voices told apart on
one recording whose **Speaker name** was answered with **several
speakers**; the **Multitrack** tick is no part of it. Both ways are in
[Speech recognition and speaker separation](speech.md). With that the
script knows who speaks when, and builds the cut from it:

* One speaker alone gets their camera, with a lead-in.
* A short "yes" does not: below **Speaks at least** the picture stays
  where it is.
* In silence the wide shot runs: the camera with no speaker assigned.
* After a long shot the wide shot drops in at a sentence boundary.

**When several speak at once**, a camera showing exactly those speakers
wins, one on both hosts, say. If none fits exactly, the smallest camera
carrying all the speakers does. If no camera covers them, the wide shot
takes over. The assignment says who is on which camera: two speakers on
one camera means it shows both.

**The name follows the cameras.** Between two cameras the picture is
switched; on one camera it is not. What comes out there is a first cut
at every change of speaker. The run puts `CAMERA CUT` over its section
with two cameras or more and `FIRST CUT BY SPEAKER` with one. The box in
the window carries those two names and a third: with one person named
and two cameras or more it is called **Cut with the wide shot**, because
their camera stands and only the wide shot breaks it up. Before anything
is separated the box is called **Camera cut**.

The output folder gets `_speakers.csv`, `_speakers.edl`, `_cameracut.csv`
and `_cameracut.edl`, whatever the cut is called. The heads are
`Speaker,Start TC,End TC,Time from start,Duration s` and
`Shot,Camera,Speaker,Start TC,End TC,Duration s`, the EDLs are titled
`Speakers` and `Camera cut`.

### Setting the knobs

The interface takes every value on the **Resolve cut** tab, in the box
**Camera cut**. One field per value, with the unit and a short line
beside it. The box is there once the cut has its people -- two of them,
or one with a second camera nobody is on; until then a line stands in
its place and says what is missing.

![The knobs for the camera cut](images/resolve-cut.png)

*Tab Resolve cut: the values on the left, the preview on the right.*

All eight fields take seconds, and the number in each line is the
default. An empty field means the default, a comma counts as the decimal
mark, and there is no upper limit. A negative value is only meant for
**Edit Change Delay**; the other fields take one but nothing good comes
of it.

Four fields shape the cut itself:

* **Minimum Edit Duration**: 3 s, this long a shot stands at least;
  higher makes the cut calmer (on the command line
  `--min-edit-duration`)
* **Speaks at least**: 1.5 s, below this the camera does not follow;
  higher and it follows less often (on the command line
  `--min-speech-to-switch`)
* **Edit Change Delay**: 0.3 s, this much later than the sound the
  picture cuts; a negative value makes the picture lead (on the
  command line `--edit-change-delay`)
* **Reaction cut earlier**: 1.5 s, after a question the answer is on
  screen this much earlier (on the command line `--reaction-lead`)

Four more shape the wide shot:

* **Wide shot after**: 70 s, from this hold time on, a look at the
  wide shot; smaller gives more wide shots, 0 turns it off (on the
  command line `--wide-after`). Measured over 87 minutes of interview
  with one guest holding the floor for 59 of them: at 40 seconds the
  picture leaves that guest 77 times, every 39 seconds; at 70 it
  leaves them 37 times, every 104. Both place the shot on a sentence
  boundary, so this is rhythm and not correctness.
* **Wide shot holds**: 5 s, the inserted wide shot stands at least
  this long (on the command line `--wide-length`)
* **Wide shot at most**: 15 s, and at most this long (on the command
  line `--wide-most`)
* **Wide shot at the latest**: 120 s, upper limit for one camera in
  one piece; smaller breaks it up sooner (on the command line
  `--wide-latest`)

Under them stand four selectors. They say what runs when the speech
does not say whom to show:

* **Long monologue**: **Alternating** (on the command line
  `--on-monologue`)
* **Several speak at once**: **Wide shot** (on the command line
  `--on-together`)
* **Recognition uncertain**: **Wide shot** (on the command line
  `--on-uncertain`)
* **Question**: **Answering speaker** (on the command line
  `--on-question`)

The first three take the same four values: **Wide shot**, **Listener**,
**Alternating** and **No camera change**. **Question** takes **do not go
early**, **Answering speaker** and **Listener**; **do not go early**
means no early camera change, the picture follows the sound here as it
does everywhere else.

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

* **Long monologue**: one person holds the floor past **Wide shot
  after**. **Alternating** remembers what the last break showed.
* **Several speak at once**: and no camera shows exactly them.
* **Recognition uncertain**: the recognition frays over a passage, or
  a name is left with nothing but scraps.
* **Question**: the picture goes to the answer before it starts. Only
  after a question that is not the main speaker's, when somebody else
  takes over at once and keeps the floor.

**Listener** means whoever speaks next, and only if somebody on that
camera was heard in the last 20 seconds; otherwise the wide shot. The
20 seconds are fixed; no field and no switch sets them.

**Listener** and **Alternating** show a person the program only knows
was audible shortly before. It does not see the picture. Set **Wide
shot** wherever a wrong face on screen costs more than a still one.

Two speakers on one camera count as one for these rules: a change of
speaker between them does not change the picture.

### What the preview and the speaker box show

The box **Camera cut -- preview** carries the length in its title and
one line of numbers below it:

* shots
* median hold time
* shortest shot
* longest a camera holds
* the speech time, split into own camera, wide shot and a camera
  without the speaker

The last figure stands in the warning colour.

The box **Speaker** shows, per speaker:

* the speech time and its share
* the number of blocks and their average length
* a row for silence

The heading names the source: **Speakers, separated by voice** or
**Speakers, self-measured from the tracks**. With two speaking at once
the time counts twice, for silence it does not. The rows therefore add
up to more than the running time.

The program computes both from the handover file
`<Production>_resolve.json` of the last run, on every change and always
for the chosen window. Writing and uploading belong to the run, not to
the preview.

With no speakers known the box says so and offers the button **Measure
speakers now**; if the computation fails, the reason stands in its
place. Speakers that turn up later start the preview by themselves.

### Reading the cut band and the legend

In the box **Camera cut -- preview** sits the **cut band**, in place of
the position rail: the computed cut over the full length, one bar per
shot in the colour of its camera. The scale carries minutes over the
whole thing and seconds once zoomed in. Hovering names camera, from-to
and duration; clicking sets the spot for the player. Below it the
**legend**: one entry per camera in the cut, a square in its colour and
then how often, who, the share and the time --
`129 × Candidate  50 %  (29:48 min)`.

**An entry is named after the people, not after the file.** A file name
says nothing that is not known already; the assignment does. So an
entry carries:

* the speaker on that camera, by name;
* every name joined with a plus where several share one camera --
  `41 × Speaker 1 + Speaker 2  14 %  (9:37 min)`; none is dropped and
  none is shortened;
* **Wide shot** for the camera serving as that;
* the camera's short name where nobody is assigned to it and it is not
  the wide shot, because calling it the wide shot would be a claim and
  not a reading;
* the camera beside the name where two of them come out with the same
  one -- one speaker filmed twice -- or the bars could not be told
  apart.

The legend wraps. On a narrow window it stands on two lines instead of
one, and nothing is shortened or left out to make it fit: a line breaks
between two entries and at a plus, never inside a name and never inside
a number.

These are the colours of the clips in Resolve, with one exception: the
wide shot is shown in a pale sage. In Resolve that clip is still called
Tan. Brown, Chocolate, Cocoa, Navy and Teal are lightened on dark, Beige
is darkened on light.

The band can be zoomed. **+** shows half as much around the current
position, **−** twice as much, and the third button the whole length
again; the mouse wheel over the band does the same, as do the keys plus,
minus and 0. Zoom in to see and hear whether a cut sits in a pause or in
the middle of a word. While playing, the section follows the position,
so it does not run out of the picture.

### How the preview players choose file and sound

Two players show the material, and both pick their file themselves.

On the **Assignment & time window** tab the order is:

1. a file **containing In point and Out point**, or the jump buttons go
   nowhere
2. failing that, one with at least one of the boundaries
3. among equals the camera with **no speaker** assigned
4. among those the longest
5. never a file set to "ignore this video", never intro or outro

The project file keeps which file was last in the player and takes it
again, as long as it covers the boundaries as well as the best
alternative. Without a timecode or a measured time axis the program
claims nothing about the boundaries; once the axis is there, the player
looks again. **to In point** and **to Out point** fetch their file
themselves; if there is none at all, a line says why nothing
happened.

With **hear assigned audio** the picture runs with the sound belonging to
that camera:

* the **processed track** from auphonic.com (`final_<Name>_<TC>.wav`), at
  the target chosen under **Loudness**, or that of the preset where
  nothing was chosen, and with a BWF timecode
* failing that the **raw recording** of the assigned speaker
* for the wide shot, the camera with no speaker assigned, the
  **Full-Mix**, if it is there

Raw recordings sit 16 to 36 dB below the processed sound, and the
interface cannot make them louder. The tooltip says what is running and
in which version.

On the **Resolve cut** tab the player in the preview box always shows
something: if there is a cut it plays the cut and switches camera at
every edge, otherwise the file with no speaker assigned.

The sound comes from one file throughout, preferably the **Full-Mix**,
which is at delivery level and goes into the cut timeline too. As long
as it is not there, the program takes the camera file carrying the mix
as its first audio track -- the same choice as for angle 1 of the
multicam clip, and noticeably quieter.

`start_s` is the wall clock time at which programme time is zero. It is
the earliest audio start actually known, own timecode or measured
position; failing that the earliest camera timecode; failing that
nothing. In point and Out point move the zero point along. The spot in
each camera file is programme time minus offset, the same offset the cut
timeline is built with.

The program sets every spot again until it holds;
[Inside the script](../development/internals.md) names how often and
for how long.

### Measuring the speakers without Auphonic

Without Auphonic the run stays local, and the script measures from the
tracks who speaks when. The way there is in [Processing at
auphonic.com](auphonic.md) (on the command line `--without-auphonic`).
In the log that section is headed `SPEAKERS -- MEASURED HERE`.

How the script reads the tracks:

* It cuts each track into blocks of 100 milliseconds.
* It measures each block against that track's own noise floor, the
  quietest fifth of its blocks; 10 dB above that counts as speech.
* Pauses under 0.35 seconds are not speaker changes.
* Passages under 0.2 seconds do not count. Measured on 31 minutes
  of three-microphone material: below that the passages that come
  back average two tenths of a second, which is breath rather than
  speech. Above it, at four tenths, a short "mhm" was dropped and
  the reply read as a pause -- 21 pauses over two seconds in that
  half hour were never pauses at all.

Before that the script takes the **bleed out of the measurement**, not
out of the audio. It looks for the moments where exactly one person
speaks: that one at most 10 dB below their own speech level, the others
at least 6 dB below theirs. There it measures how loudly that voice
arrives in the other microphones, and it takes each speaker's own share
back out of every track. None of these values can be set; there is no
field and no switch for them.

It also works with microphones standing closer than the 3:1 rule wants.
For a pair without at least three such moments it subtracts nothing.
With microphones side by side, or tracks too much alike, it cannot be
undone: the levels stay as measured, and the log says why and names the
worst pair.

Down to 5 dB of separation the detection is exact, well below the 9.5 dB
the 3:1 rule asks for; the measurements behind that number are in
[What was measured](../development/measurements.md).

The log says how strong the bleed was, and under it the speech time and
the number of passages per speaker. If nothing was audible, there is
no camera cut.

The button **Measure speakers now** does the same in the interface,
before the first run: coarser than the separation by voice, but enough
to set the cut up. Speakers separated by voice take precedence as soon
as they are there, and the heading above the table says which applies.

### Cutting when one camera shows everybody

With several speakers on one camera the program cuts at the change of
speaker: every shot comes from the same clip, so it shows the same
framing, and carries the name of whoever is talking. Resolve gets a
track already separated at the right places, and there each piece can be
grouped, coloured and zoomed into, so the wide shot becomes the speaker.

The cut list says so too: with one camera for everybody the EDL carries
the speaker name in place of the camera name. The Speaker column of
`_cameracut.csv` is there in any case.

**A single voice on one camera gives no cut.** Nobody hands over, so
there is nothing to cut at, and neither a cut list nor an EDL is
written. The passages go into the handover file, and Resolve sets them
as markers on the timeline it builds, the one camera in one piece with
the mix below.

**With a second camera a single voice does give a cut.** Nobody is on
that camera, so the speaker's camera stands and the wide shot breaks it
up; the box is then called **Cut with the wide shot**. Five minutes on
two cameras gave 15 shots, 7 of them wide, against 1 shot on a single
camera.

### What the project file keeps

`videopodcast-magic_<Production>.json` in the output folder holds
everything set by hand that cannot be guessed again. That is the file
list, the production name and the output folder, the time window, every
value of the camera cut, who belongs to which camera, the Auphonic
preset, the stereo ticks and the measured position of every file; the
API key is **not** in there.

On opening, the program checks the format of the file and refuses a file
in another format. It can no longer open older project files.

The file appears as soon as the program has measured the time axis, then
still next to the material, because there is no output folder yet. If
one is chosen later, or the production renamed, **it moves along**.
There is always exactly one.

**Open project ...** on the drop area brings it back, as long as no
files are in the list; point at the wrong file and the program searches
the same folder for `videopodcast-magic*.json`. Beside it lies the
handover file `<Production>_resolve.json`. The preview computes from it,
and the Resolve part builds from it.

### How the program places the wide shot

A wide shot does not come by the clock. It enters on a sentence
boundary near the wanted spot, and the exact point comes from the sound:
the dip in the level around that boundary. Both are measured, so the
same material gives the same cut.

It stands at least **Wide shot holds**, then runs to the end of the
sentence. If that end lies beyond **Wide shot at most**, the last clause
break before it ends the shot.

`--wide-latest` is the rip cord: with no sentence boundary the cut
happens anyway. Without a transcript the wide shot goes to the longest
speech pause nearby and stands the set minimum.

### What the metrics and the colour comparison measure

At the end of every Multitrack run `<Production>_metrics.csv` appears;
the log is
overwritten by the next run, this file is not. Over months it shows what
a single run hides: a recorder going slow, a camera drifting away from
the rest, bleed rising with a new setup.

The columns are `Area,Metric,Before,After,Unit`, comma separated, with a
full stop as the decimal mark. `Area` and `Metric` stay English whatever
the language, so two runs stay comparable. Before is the track as it came
in, after as it goes out, both measured the same way.

On a German system the comma costs one step: Excel opens a file by double
click with the semicolon and puts the whole row in one column. The way in
is `Data > From Text/CSV`; there, set separator and the language of the
numbers by hand. LibreOffice asks for both by itself.

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
measurements together take a few minutes on long recordings: the
loudness measurement runs through each track twice.

### When something goes wrong

* **The Speaker box says no speakers are known.** Press **Measure
  speakers now**. The reason stands in place of the table if the
  computation fails.
* **No cut comes out.** Nothing was audible on the tracks, or the
  separation found a single voice and there is only one camera. The log
  says so, under `SPEAKERS -- MEASURED HERE` or
  `SPEAKERS -- SEPARATED BY VOICE`.
* **No box for the cut on the Resolve cut tab.** Nobody carries a name
  and a camera, or one person does and there is no second camera. On
  the **Assignment & time window** tab give each voice a name and a
  camera.
* **The picture stands still although the speaker changes.** Both
  speakers sit on one camera, or the block is shorter than **Speaks at
  least**.
* **The preview shows much time on a camera without the speaker.**
  Check who is assigned to which camera on the **Assignment & time
  window** tab.
* **The player is very quiet.** The Full-Mix is not there yet, so a
  camera file carries the sound. The interface cannot make it louder.
* **The cut is restless.** Raise **Minimum Edit Duration** or **Speaks
  at least**.

The cut now stands: a shot list, two EDLs and a preview to check it in.
What Resolve makes of it is in [DaVinci Resolve](resolve.md).

### Further options on the command line

These have no counterpart in the window.

* `--reaction-gap` how soon the answer has to follow the question for
  the reaction cut to fire (3 s); larger and it fires more often
* `--reaction-hold` how much of the ten seconds after the question the
  answering speaker has to hold, as a share between 0 and 1 (0.7);
  higher and it fires less often
* `--no-metrics` leaves out the metrics file and the colour comparison
  (Multitrack only; a run without Multitrack writes neither anyway)
* `VPM_PLAYER_DEBUG=1` in front of the call puts clock, position and
  wanted value of all three players under the picture, and every attempt
  on the console
