# DaVinci Resolve

*Auf Deutsch: [resolve.de.md](resolve.de.md). Back to the [contents](README.md).*

## DaVinci Resolve

On tab **4. Output** the button **Create Resolve project** builds it:
files first, project afterwards. It creates the project, sets frame rate,
resolution and start timecode, imports the finished files and builds the
timelines; the run is written along to `<Production>_resolve_log.txt`.

The button works on the handover file and sends the camera-cut values from
the fields along, so the cut list is recomputed with what stands there now.
Where In point or Out point have changed since, it stops -- the audio in the
videos belongs to the old window.

Whether Resolve answers is asked by itself on the first look at tab
**3. Resolve cut**, in the background. That tab says the answer in one
line, and beside it stands the way to the **Settings ...** window, where
the check itself lives. In its box **Connection to Resolve** it names the
product and the version where it works, and where it does not, the two
paths it looked for and what can be in the way:

- Resolve is not running.
- External scripting stands at "None" instead of "Local", under
  Preferences > System > General.
- The free edition, which is reported to have kept external scripting to
  Studio since version 19.1. No official statement says so.

In that box, **Check again** asks once more, and so does opening the window.

| | Cut timeline | Multicam timeline |
|---|---|---|
| multitrack, several cameras | picture from the camera cut, audio in one piece | all cameras side by side |
| simple path, several cameras | — no speaker statistics, so none | all cameras side by side |
| one camera | the camera in one piece, the mix below | — would be pointless |

The simple path builds a project too. A camera cut it cannot deliver -- that
needs the speaker assignment from auphonic.com -- but it gives the timeline
with all cameras at their measured places, and Resolve makes the multicam clip
from it.

The frame rate is rounded to one Resolve knows -- ffprobe measures 29.994 or
30.001 for some files -- and the log says which. Timecodes are computed with
the whole-number rate, durations with the true one; drop frame is taken into
account.

**… Cut** -- the finished camera cut. V1 (`Camera cut`) carries the
picture pieces **without their audio**; below on A1 (`Audio-Full-Mix`) the
Full-Mix runs through in one piece, so the sound does not jump at the
cuts. The mix comes from the separate file, otherwise from the wide shot,
where it is the first audio track.

Which part of each camera file is used comes from the measured offset,
not from the timecode. Where one camera was not running, another steps
in, the wide shot first; the log says how often. No markers -- the cut is
made.

**… Multicam** -- all cameras side by side, one per video track, full
length, **uncut**, each at its measured place, track names = speakers (a
camera without a speaker is called `Wide`), speaker names as markers.
Video track 1 takes the camera whose first audio track is the Full-Mix,
usually the wide shot; on conversion it becomes angle 1.

**Exactly one audio track per camera, linked to its picture.** The
surplus audio is deleted after the insert and the audio tracks are named
like the video tracks. A camera that did not land is inserted separately,
and reported where even that fails.

### When the project already exists

It asks:

- **bring up to date** -- the two timelines this script builds (`… Cut` and
  `… Multicam`) are deleted and built again, the project settings brought up
  to date. **Everything else stays untouched:** media pool, your own
  timelines, everything from earlier runs.
- **leave it and put the new timelines alongside** -- the existing ones stay.
- **create a new project alongside** -- name with a suffix.
- **cancel.**

The interface asks in a dialog, the terminal with a number (on the command
line in advance, `--resolve-project update|keep|new|abort`).

Deletion is verified -- Resolve reports success even where nothing happened.
Where a timeline stays, the log says so and the new one gets an addition to
its name.

The multicam timeline is spared where it already fits -- same cameras, same
order. Whoever wants a new one deletes it in Resolve. No backup copy is kept:
one more run rebuilds it.

### Multicam audio: the four choices

On conversion Resolve asks under *Multicam Audio Options* where the sound
should come from (manual, chapter "Multicam Audio Options"):

| Setting | Effect |
|---|---|
| **Source Audio Channels** (default) | access to the single tracks and channels of every angle |
| **Reference Audio / Angle 1** | the *first pure audio angle* becomes the audio track for all angles; without one it is the first angle |
| **Adaptive Tracks** | all tracks and channels of an angle land in **one** adaptive track |
| **All Angles** | every audio track of every angle comes along -- four plus five makes nine |

*Source Audio Channels* is the right choice: only one audio track per
camera is left, and each angle then brings exactly the speaker in front of
it. The closing note in the log says so too.

### Clip colours

Every shot gets the colour of its angle, on both timelines. The colours
are sorted by distinguishability, and the wide shot gets `Tan`. More
angles than colours means the row repeats, and the log says so.

Each camera also gets a **colour group** -- see *Colour groups* further
down.

### The render job

Once the timelines stand, the script sets the render profile and queues the
job. In Resolve only "Render All" is left.

HDR or SDR is decided by the material and the project, not by taste. First the
`colr` box of the camera files is read. HDR is:

- **PQ or HLG** (transfer function 16 or 18), the two HDR display curves,
- **Log** (Apple Log is 21 in the file) -- a recording curve, not a
  display curve. **Log is HDR.**
- **BT.2020** as colour space or as matrix.

Where a camera writes nothing usable into `colr`, its QuickTime keys are
read as well; most cameras note the curve there. The search runs on word
markers (`apple log`, `s-log`, `v-log`, `logc`, …), not on "log". Where
the project settings say otherwise, the project wins.

| | SDR | HDR |
|---|---|---|
| Codec | H.264, eight bit | H.265, ten bit (profile Main10) |
| 2160p | 45,000 kbit/s | 56,000 kbit/s |
| 1440p | 16,000 | 20,000 |
| 1080p | 8,000 | 10,000 |
| 720p | 5,000 | 6,500 |

At high frame rates -- 48, 50, 60 -- the higher values apply: 68,000 and
85,000 kbit/s at 2160p, correspondingly below. They are YouTube's upload
recommendation, each the upper end of the range given there.

A warning goes into the log where this Resolve offers no H.265, and another
where it will not take the profile Main10, which is then set without.

HDR also has to be tagged, or the file carries none however cleanly it was
graded. The curve comes from the project's output colour space: PQ gets
Rec.2020 / ST.2084, HLG gets Rec.2020 / HLG. Naming no HDR curve there leaves
the render on "Same as Project".

Fixed are: one file instead of one per clip, target the output folder, file
name the production name, `.mp4`, audio AAC at 48 kHz, 16 bit, two channels.
Resolve's scripting interface has no key for the audio bitrate; the log
notes that 384 kbit/s would be the recommendation for stereo. For HDR it
names the check too: `videopodcast-magic.py --hdr-check <file>`.

### Intro and outro

In the camera table on tab **2. Assignment & time window** every row has a
column **Kind**: *Content*, *Intro*, *Outro* or *ignore this video*. Intro
and outro are optional. A file that is not content is not aligned, not
processed and not copied -- it is a finished clip and only goes into the
timeline (on the command line `--intro FILE` and `--outro FILE`). Both land
on the **second** video and audio track, over the content (`Intro / Outro`
and `Audio Intro / Outro`).

There is one intro and one outro. Setting a second file to the same kind puts
the first one back to content. A run that still sees two of a kind stops and
names them.

**Nothing is shortened.** Both clips keep their full length, and the content
is not trimmed either. Only where they lie shifts, and that follows the
**sound**, not the file length:

- **Intro**: the *end of its audible sound* meets the first word. That means
  the jingle, not the file. The threshold is 40 dB below the loudest point of
  the file itself.
- **Outro**: the *start of its sound* meets the end of the last word.
- Where the words lie comes from the speaker statistics.
- A clip without sound uses its end for the intro, its start for the outro.

You pull the dissolve yourself, and that is why the clips lie *over* the
content instead of beside it: one drag on the upper corner is enough.
Resolve's scripting interface knows no transitions.

### Colour

The colour of the source is kept unchanged. The script reads the `colr`
box out of the source itself, passes the numbers on explicitly, forces the
write and checks afterwards: log line **Colour**.

iPhone recordings from the Blackmagic Camera App carry "unspecified" as
their curve in `colr`; Resolve goes by the QuickTime keys of the container
(`com.apple.quicktime.model`, `com.apple.quicktime.software`,
`com.blackmagic-design.camera.*`). The script carries them along and
counts afterwards whether every key arrived (log line **Camera data**).

#### The logs atom

The picture description holds a small atom `logs` naming the recording
curve, for instance `com.apple.apple-wide-gamut.apple-log`. **That** is
what Resolve recognises Apple Log by; the `colr` box says nothing about
it. ffmpeg cannot keep the atom, so the script adds it itself after
writing, byte for byte from the source, and reads back afterwards whether
the file is still sound.

The log then says under **Camera atoms** whether the atom was added and which
curve it names, and in the file list the curve stands in the **Colour** row --
with a plain name where one is known (Apple Log, Apple Log 2), otherwise with
the identifier as it stands.

### Colour groups

The script creates one **colour group** per camera and puts all clips of
that camera into it, so a camera is graded once instead of once per cut.
The node editor on the Color page has four modes for this:

| Mode | acts on |
|---|---|
| **Group Pre-Clip** | "affect every clip in the group simultaneously" -- the whole camera |
| **Clip** | "only affect the specific clip that's selected" -- this one cut |
| **Group Post-Clip** | the whole group again, but computed after the clip |
| **Timeline** | every clip of the timeline |

They are computed in that order. So: the basic correction of a camera in
**Group Pre-Clip**, and where a single cut falls out of line, pull it back in
**Clip**. Further clips join the group by right-click > Group > name > Assign
to Group.

### Local grades, not remote grades

The script sets **local versions**, explicitly on every run. Remote grades
("Use local version for new clips" off) would tie all clips of the same
source file to one correction, so a single cut could no longer be
corrected on its own. There is no switch to turn them back on.

The setting only affects clips that come into a timeline **afterwards**:
`--resolve-project update` rebuilds both timelines and settles it. With
`keep` the clips already there hang on to their remote grade, and the log
names the way out -- Color page, right-click a thumbnail > **Copy Remote
Grades to Local** (takes the correction along) or **Use Local Grades**.
What the setting is called inside Resolve is picked out of the list of all
project settings and read back.

### HDR: what has to be in the file

An HDR picture is not enough -- it has to say so as well. Three numbers from
ITU-T H.273 decide whether a player or YouTube treats the file as HDR; without
them everything shows as SDR, and the effort with Apple Log is lost.

| Feature | HDR10 (PQ) | HLG | Required |
|---|---|---|---|
| Primaries | **9** (BT.2020) | **9** | yes |
| Curve | **16** (SMPTE ST 2084) | **18** (HLG) | yes |
| Matrix | **9** (BT.2020, non-constant) | **9** | yes |
| Bit depth | 10 (or 12) | 10 | yes |
| Codec | HEVC **Main 10** | same | with HEVC |
| `colr` atom in the container | present | present | yes |
| Mastering display (ST 2086) | values of the reference monitor | none | no |
| MaxCLL / MaxFALL | e.g. 1000 / 400 | none | no |

Two traps: **the 14 is not an HDR curve** -- it is called "BT.2020 10 bit" and
is SDR in the wide gamut. And **tagging changes no pixels**: a PQ tag on a
Rec.709 grade turns it into wrongly labelled SDR. The static metadata is only
a recommendation; without it YouTube applies default values (a Sony BVM-X300),
and with HLG it falls away entirely.

**What the script does.** Building the render job, it reads the output colour
space from the project settings. Where that names PQ or HLG it sets
`ColorSpaceTag`, `GammaTag` and `EncodingProfile` = `Main10`; which spelling
this Resolve version takes is documented nowhere, so several are tried and the
accepted one goes into the log. Otherwise it stays at "Same as Project", and
the log names the place to look: Project Settings > Color Management > Output
Color Space.

**Looking at the finished file:**

```
videopodcast-magic.py --hdr-check Production.mp4
```

That checks every point of the table, says for each what would have to be
done, and changes nothing. Return value 0 means the file passes as HDR.

"Embed HDR10 Metadata" and the HDR10+ analysis the script cannot switch on
remotely -- Resolve's scripting interface has no key for it. By hand:
Color Management > HDR10+, Color page > Analyze All Shots, Deliver > Embed
HDR10 Metadata.

### Framing

Position and zoom go through the same group as the colour, but only in one
place. The **Sizing** palette (Color page, bottom middle, between "Key" and
"Stereo") has five modes:

| Mode | acts |
|---|---|
| Edit Sizing | like the inspector on the Edit page, per clip |
| Input Sizing | before the node tree, per clip |
| **Node Sizing** | **in the node tree, on the selected node** |
| Output Sizing | for the whole timeline |
| Reference Sizing | only for the still comparison |

A group shares the node tree, not the clip settings; it carries Node Sizing
along, Edit and Input Sizing not. So: click a clip of that camera, switch the
node editor from "Clip" to **Group Pre-Clip**, set the Sizing palette to
**Node Sizing**, adjust -- it holds retroactively for every clip of that
camera in both timelines. What is changed on the media pool clip, by contrast,
takes hold only for clips that come into a timeline *afterwards*.

Inferred from the manual (chapters 142 and 152), not copied from it: that Node
Sizing in the Group-Pre-Clip tree acts on the whole group is not stated there.

### When Resolve is to cut for itself

That needs a multicam clip, and the script cannot create one: the
scripting interface has no multicam. So by hand:

1. Media pool, right-click on "... Multicam"
2. **Convert Timeline to Multicam Clip** > **Use Source Audio Channels**

On the audio, see the four choices above. The track name becomes the name of
the angle (manual, chapter 49) -- which is why the video tracks are named
after the speakers. Converting is a one-way operation, and there is no backup
copy.

### Further options on the command line

The window has no equivalent for these.

- `--resolve` builds the project as part of a whole run, straight after the
  files.
- `--resolve-json FILE` catches up the Resolve part alone; everything
  needed is in `Production_resolve.json`. That is what the button
  **Create Resolve project** runs.
- `--resolve-audio-tracks` only looks: for the open project it prints the
  channel mapping of every clip and the tracks of every timeline.
