# Multitrack: several speakers, several cameras

*Auf Deutsch: [multitrack.de.md](multitrack.de.md). Back to the
[contents](README.md).*

## What Multitrack does

Several people at a table, each with a microphone that hears everyone.
Taking that bleed out of the audio is the one thing only auphonic.com
does.

Multitrack is the way for one track per person. Everybody on one
recording stays one track. The speaker separation tells the voices in it
apart and gives the cut, not a track each
([Speech recognition and speaker separation](speech.md)).

Everything else runs locally. [Processing at auphonic.com](auphonic.md)
describes the way there (on the command line `--without-auphonic`). The
program then aligns the audio, mixes it, sets the loudness and builds the
camera cut. It leaves out de-bleed, leveler and noise removal.

Everything lands on one common time axis, clock drift and all. The
window comes from the cameras alone; the program fills gaps inside it
with silence. Rows with the same speaker name become one track. The
program lays them end to end by their timecode. A recording that was
stopped in between comes back in one piece.

### Setting the assignment

The **Assignment & time window** tab holds two tables on the left. The
upper one has a row per audio recording: **Audio recording**, **Speaker
name**, **belongs to**, Timecode, **Speakers**. The last column holds
the button **Separate speakers**, and once that recording is separated
the count of the speakers found stands there instead ([Speech
recognition and speaker separation](speech.md)). The selector **belongs
to** lists the cameras, then two special cases:

- **into the mix only**: in the Full-Mix, but nobody's first track. For
  someone heard but not seen.
- **ignore this audio**: out entirely, and the speaker name goes grey.
  For a recording whose video is still missing.

The lower table has a row per camera: **Camera**, **new file name**,
**gets audio from** and **Camera audio**. What a file is -- content,
intro, outro or ignored -- is asked in the file list now, in the column
**Kind**, with the material it is about. A click on a row fetches that
file into the player. Files that do not fit the measured time axis stand
in red, here as in the file list.

Under the tables the **Multitrack** tick sits a second time. It is the
same tick as under **Production**: click either one and both show it.
The count is the same on the command line (`--multitrack`).

Multitrack needs two input tracks. Three things count as a track:

- a recording of its own,
- a channel of a multichannel recorder,
- the audio of a video file whose **Camera audio** stands on **use the
  audio**.

The program counts the rows of the upper table, minus those on **ignore
this audio**. The camera cut does not need this field.

![The two tables of the assignment](images/assignment.png)

*Tab Assignment & time window: the recordings with their camera, the
cameras with the column Camera audio, and under both tables the
Multitrack tick and the box for auphonic.com.*

### Making camera sound a track

Whether a camera contributes its sound is asked at the file: in the file
list on the **Files & production** tab, in the column **Camera audio**.
It stands on **do not use the audio** until somebody says otherwise, at
every camera and however many there are. Nothing can measure that
answer -- two radio microphones recorded straight into the video track
look exactly like the camera's own microphone in the room, so only
whoever was there knows.

The same field stands in the camera table beside the player, on the same
value: change either and both show it. What is known up front is said
with the material; what is only heard later is changed where it can be
heard.

One case settles itself: exactly one video file with sound and no audio
recording beside it. That sound is then the only sound there is, and the
field stands on **use the audio**, greyed out, with the reason beside it.
It is derived, not stored -- an audio recording added takes it back to a
question ([The simple path](simple-path.md)).

Set to **use the audio**, the camera gets a row in the upper table, with
its speaker name. It counts like any other track: processed, in the
Full-Mix, counted in the speaking time for the camera cut, and the first
audio track of its own camera.

"Like any other track" includes the channels. The field only keeps the
audio; the same measurement as for a recorder file decides what it
becomes.

- **Two clip-on microphones on the two channels** give two rows with two
  speaker names. The program judges and cuts them like a two channel
  recorder file. That one camera is two input tracks.
- **A real stereo pair** stays one two channel track.

The selector **belongs to** sets which camera such a track belongs to;
the camera the audio came out of is only the preselection. A clip-on
microphone plugged into one camera does not mean that camera films the
person.

Where nobody sets the field and there is no audio recording either, there
is nothing to listen to: **Start** stays locked and says so underneath.
Synchronising is not part of this question -- the time axis is measured
over the envelope of every file, whatever the field says.

### What the program reads in the background

The program reads camera audio and the envelope as soon as the table
stands, up to four files at once. One bar under the tables shows it. On
long 4K files that takes minutes. Work carries on meanwhile. The program
starts the run only when the prework is done.

### Running several files at once

The run works in parallel too: several camera files at once. Each file's
report appears in one piece when it is finished, under one shared bar.

**Remove** takes a file out of the list: it leaves the queue, the
program forgets its envelope and deletes the audio already extracted.

Envelopes otherwise stay in the system cache folder
(`~/Library/Caches/videopodcast-magic/envelopes/`, on Windows
`%LOCALAPPDATA%`), keyed to the source file's path, size and change time.
At start the program clears out anything older than thirty days.

### Setting the time window

By default the window reaches as far as the cameras. To set the start:

1. On the **Assignment & time window** tab, click the row of the file.
   It goes into the **Preview player**.
2. Stop the picture where the window should begin.
3. Press **Mark In** (on the command line `--in-point`).

**Mark Out** sets the other boundary the same way (`--out-point`). **to
In point** and **to Out point** jump back to the two marks. The
**Resolve cut** tab repeats both as a line: In point, Out point,
Duration.

Both boundaries take these entries:

| Entry         | Meaning                      |
|---------------|------------------------------|
| `17:20:14`    | absolute, clock time         |
| `17:20:14:00` | absolute, with frames        |
| `+12:30`      | from the window start        |
| `90`          | the same, in seconds         |
| `-30`         | Out point: back from the end |

The buttons stay locked until the common time axis is there. After that
they hold for every file alike, including those without a timecode.

### What goes into the camera files

The first audio track of each camera file is the mix of exactly the
speakers in that picture: `Mix <A> + <B>`. With only one speaker it
carries their name. Then those speakers singly, then `Full-Mix (…)`,
last `Camera Original`. The program measures loudness over the sum and
applies it to every track alike, so their balance stays.

The program also writes the tracks as files, into `auphonic-tracks/` as
`final_<name>_<timecode>.wav`. The timecode is in the name and in the
bext chunk, and iXML comes along for Premiere and Media Composer.

### When something goes wrong

- **A row stands in red.** That file's sound does not line up with the
  others, so it gets no place on the common time axis. Pick **ignore
  this video** in the column **Kind** of the file list, or take the file
  out of the list with **Remove**.
- **Mark In and Mark Out stay locked.** The common time axis is not
  there yet. Wait for the bar under the tables.
- **Several cameras, no audio recording, and Start stays locked.** No
  camera is contributing its sound. Set **Camera audio** to **use the
  audio** at every camera that is to be heard; each one is then a track.
  They no longer become tracks by themselves: a camera recording a
  usable track cannot be told from one merely filming in the same room.
- **A speaker is missing from the Full-Mix.** That row has **ignore this
  audio** in the column **belongs to**.

The tracks are assigned, the window is set, and every camera file
carries its own mix. Next comes the question of who says what:
[Speech recognition and speaker separation](speech.md).

### Further options on the command line

These options are not in the window.

- `--parallel COUNT` sets how many camera files run at once: `0` is the
  default and decides for you, `1` takes one file after another. A
  higher count never runs more files than the list holds. The written
  files are byte-identical either way.
- `--lufs` sets the loudness the sum is brought to, default −16. The
  usual targets per platform are in [Preflight](preflight.md).
