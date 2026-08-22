# Multitrack: several speakers, several cameras

*Auf Deutsch: [multitrack.de.md](multitrack.de.md). Back to the [contents](README.md).*

## Multitrack: several speakers, several cameras

Several people at a table, each with a microphone that hears everyone.
Taking that bleed out of the audio is the one thing only auphonic.com
does. `--without-auphonic` does the rest locally: aligned, mixed, loudness
set, camera cut included, but no de-bleed, no leveler, no noise removal.

Before that everything goes onto one common time axis, clock drift and
all. The window comes from the cameras alone; where audio is missing
inside it, silence goes there. Rows with the same speaker name become one
track, laid end to end by timecode. That is right for a recording that was
stopped in between.

### The assignment

Tab "2. Assignment & time window" holds two tables on the left. The upper
one has a row per audio recording: file, speaker name, where it belongs,
timecode. The selector lists the cameras, then two special cases:

- **into the mix only** — in the Full-Mix, but nobody's first track. For
  someone heard but not seen.
- **ignore this audio** — out entirely, and the speaker name goes grey.
  For a recording whose video is still missing.

The lower table has a row per camera: kind (content, intro, outro, ignore
this video), the new file name, which audio it gets, the tick for its own
audio. A click on a row fetches that file into the player. Files that do
not fit the measured time axis stand in red, here as in the file list.

Above the tables the **Multitrack** tick sits a second time. It is the
same tick as under Production and the same value -- click either one and
both show it. Multitrack wants two separate recordings, and a camera
counts as one as soon as **as a track** is ticked for it. On the command
line the count works the same way and reads the assignment file for it.

### Without separate audio recordings

With only cameras — at least two — their own sound becomes the tracks, one
per camera. Otherwise a single camera can still contribute its sound: the
tick **as a track** in the column "own audio". It then has a row in the
upper table with its speaker name and counts like any other track —
processed, in the Full-Mix, in the speaker statistics, and the first audio
track of its own camera. Without Multitrack the run would have nothing to
put into cameras-only material and would stop.

"Like any other track" includes the channels. The tick says no more than
"do not throw this audio away"; what it becomes is decided by the same
measurement as for a recorder file. A camera whose two channels carry two
clip-on microphones — a DJI Osmo does that — gives two rows with two
speaker names, judged and cut exactly as a two channel recorder file
would be. A camera carrying a real stereo pair keeps it as one two
channel track. On the command line the same thing happens without an
interface: `videopodcast-magic.py Osmo.mov Wide.mov --multitrack` reads
the Osmo as two speakers and the wide shot as one, and still writes one
file per camera.

Which camera such a track belongs to is a separate question, and the
selector answers it: a clip-on microphone plugged into one camera does
not mean the person is filmed by that camera. The camera the audio came
out of is the preselection, nothing more.

### Prework in the background

Pulling the camera audio out and reading the envelope takes minutes on
long 4K files. Both start as soon as the table stands, up to four at once,
shown as one bar under the tables. Work carries on meanwhile; pressing
Start too early only costs a short wait.

### Several files at once

The run works in parallel too: several camera files at once. Each file's
report appears in one piece when it is finished, under one shared bar.
`--parallel COUNT` sets the number: `0`, the default, decides for you, `1`
takes one file after another. The written files are byte-identical either
way.

Take a file out of the list and it leaves the queue, its envelope is
forgotten and the audio already extracted is deleted. Envelopes otherwise
stay in the system cache folder
(`~/Library/Caches/videopodcast-magic/envelopes/`, on Windows
`%LOCALAPPDATA%`), keyed to the source file's path, size and change time.
Anything older than thirty days is cleared out at start.

### Time window

By default the window reaches as far as the cameras. In point and Out point
narrow it:

| Entry         | Meaning                      |
|---------------|------------------------------|
| `17:20:14`    | absolute, clock time         |
| `17:20:14:00` | absolute, with frames        |
| `+12:30`      | from the window start        |
| `90`          | the same, in seconds         |
| `-30`         | Out point: back from the end |

On the command line `--in-point` and `--out-point`. In the interface both
come out of the player: stop where it should begin, press "Mark In". Four
buttons sit under the picture: "Mark In" and "Mark Out" set the boundaries,
"to In point" and "to Out point" jump back to them. Tab "3. Resolve cut"
repeats both as a line: In point, Out point, Duration.

Until the common time axis is there the buttons stay locked. After that
they hold for every file alike, including those without a timecode.

### What goes into the camera files

The first audio track of each camera file is the mix of exactly the
speakers in that picture — `Mix <A> + <B>`, or with only one their name.
Then those speakers singly, then `Full-Mix (…)`, last `Camera Original`.
Loudness is measured over the sum and applied to every track alike, so
their balance stays (`--lufs`, default −16).

The tracks are also written as files, into `auphonic-tracks/` as
`final_<name>_<timecode>.wav` — timecode in the name and in the bext
chunk, plus iXML for Premiere and Media Composer.
