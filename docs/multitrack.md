# Multitrack: several speakers, several cameras

*Auf Deutsch: [multitrack.de.md](multitrack.de.md). Back to the [contents](README.md).*

## Multitrack: several speakers, several cameras

Several people at a table, each with a microphone that hears everyone.
Taking that bleed out of the audio is the one thing only auphonic.com
does.

Everything else runs locally. In the box **Processing at auphonic.com
(optional)** on tab **2. Assignment & time window** pick **work without
Auphonic** in the selector **Preset:** (on the command line
`--without-auphonic`). The run is then aligned, mixed, loudness set,
camera cut included, but no de-bleed, no leveler, no noise removal.

Everything lands on one common time axis, clock drift and all. The
window comes from the cameras alone; where audio is missing inside it,
silence goes there. Rows with the same speaker name become one track,
laid end to end by timecode. A recording that was stopped in between
comes back in one piece.

### The assignment

Tab **2. Assignment & time window** holds two tables on the left. The
upper one has a row per audio recording: **Audio recording**, **Speaker
name**, **belongs to**, Timecode. The selector **belongs to** lists the
cameras, then two special cases:

- **into the mix only** — in the Full-Mix, but nobody's first track. For
  someone heard but not seen.
- **ignore this audio** — out entirely, and the speaker name goes grey.
  For a recording whose video is still missing.

The lower table has a row per camera: **Kind** (**Content**, **Intro**,
**Outro**, **ignore this video**), **new file name**, **gets audio
from**, and **own audio** with the tick **as a track**. A click on a row
fetches that file into the player. Files that do not fit the measured
time axis stand in red, here as in the file list.

Above the tables the **Multitrack** tick sits a second time. It is the
same tick as under **Production**: click either one and both show it.
Multitrack wants two separate recordings, and a camera counts as one as
soon as **as a track** is ticked for it. The count is the same on the
command line (`--multitrack`).

### Without separate audio recordings

With only cameras — at least two — their own sound becomes the tracks,
one per camera. Without Multitrack the run has nothing to put into
cameras-only material and stops.

A single camera can contribute its sound as well: the tick **as a track**
in the column **own audio**. It then has a row in the upper table with
its speaker name and counts like any other track — processed, in the
Full-Mix, in the speaker statistics, and the first audio track of its own
camera.

"Like any other track" includes the channels. The tick says no more than:
do not throw this audio away. What the audio becomes is decided by the
same measurement as for a recorder file.

- **Two clip-on microphones on the two channels** give two rows with two
  speaker names, judged and cut like a two channel recorder file.
- **A real stereo pair** stays one two channel track.

Which camera such a track belongs to is set in the selector **belongs
to**; the camera the audio came out of is only the preselection. A
clip-on microphone plugged into one camera does not mean that camera
films the person.

### Prework in the background

Camera audio and envelope are read as soon as the table stands, up to
four files at once, shown as one bar under the tables. On long 4K files
that takes minutes. Work carries on meanwhile; pressing **Start** too
early only costs a short wait.

### Several files at once

The run works in parallel too: several camera files at once. Each file's
report appears in one piece when it is finished, under one shared bar.

**Remove** takes a file out of the list: it leaves the queue, its
envelope is forgotten and the audio already extracted is deleted.

Envelopes otherwise stay in the system cache folder
(`~/Library/Caches/videopodcast-magic/envelopes/`, on Windows
`%LOCALAPPDATA%`), keyed to the source file's path, size and change time.
Anything older than thirty days is cleared out at start.

### Time window

By default the window reaches as far as the cameras. In the **Preview
player** on tab **2. Assignment & time window** four buttons sit under
the picture: **Mark In** and **Mark Out** set the boundaries, **to In
point** and **to Out point** jump back to them. Stop where it should
begin, press **Mark In** (on the command line `--in-point` and
`--out-point`). Tab **3. Resolve cut** repeats both as a line: In point,
Out point, Duration.

Both boundaries take these entries:

| Entry         | Meaning                      |
|---------------|------------------------------|
| `17:20:14`    | absolute, clock time         |
| `17:20:14:00` | absolute, with frames        |
| `+12:30`      | from the window start        |
| `90`          | the same, in seconds         |
| `-30`         | Out point: back from the end |

Until the common time axis is there the buttons stay locked. After that
they hold for every file alike, including those without a timecode.

### What goes into the camera files

The first audio track of each camera file is the mix of exactly the
speakers in that picture — `Mix <A> + <B>`, or with only one their name.
Then those speakers singly, then `Full-Mix (…)`, last `Camera Original`.
Loudness is measured over the sum and applied to every track alike, so
their balance stays.

The tracks are also written as files, into `auphonic-tracks/` as
`final_<name>_<timecode>.wav` — timecode in the name and in the bext
chunk, plus iXML for Premiere and Media Composer.

### Further options on the command line

These options are not in the window.

- `--parallel COUNT` sets how many camera files run at once: `0`, the
  default, decides for you, `1` takes one file after another. The written
  files are byte-identical either way.
- `--lufs` sets the loudness the sum is brought to, default −16.
