# Multitrack: several speakers, several cameras

*Auf Deutsch: [multitrack.de.md](multitrack.de.md). Back to the
[contents](README.md).*

## What Multitrack does

Several people at a table, each with a microphone that hears everyone.
Taking that bleed out of the audio is the one thing only auphonic.com
does.

Multitrack is the tick for one track per person. Everybody on one
recording stays one track. The speaker separation tells the voices in it
apart and gives the cut, not a track each
([Speech recognition and speaker separation](speech.md)).

The tick decides how the recordings are grouped, and nothing else: with
it every person gets a track of their own, with a name and a camera;
without it they all run into the Full-Mix together. The common time
axis, the camera cut and the files that come out are the same with the
tick and without it. Who ends up in the cut does not hang on where they
came in by either: a recording of one person, the sound of a camera, a
channel of a recorder and a voice a separation found all count alike,
and only **do not use** keeps somebody out.

Everything else runs locally. [Processing at auphonic.com](auphonic.md)
describes the way there (on the command line `--without-auphonic`). The
program then aligns the audio, mixes it, sets the loudness and builds the
camera cut. It leaves out de-bleed, leveler and noise removal. Where the
microphones hear each other too well for the tracks to say who is
speaking, the separation takes that question off them and listens to all
of them at once ([Speech recognition and speaker
separation](speech.md)).

Everything lands on one common time axis, clock drift and all. The
window comes from the cameras alone, and where there is no camera at all
from the tracks themselves; the program fills gaps inside it with
silence. Rows with the same speaker name become one track. The
program lays them end to end by their timecode. A recording that was
stopped in between comes back in one piece.

### Setting the assignment

The **Assignment & time window** tab holds two tables on the left. The
upper one has a row per audio recording: **Audio recording**, **Speaker
name**, **belongs to**, Timecode, **Speakers**. A name typed into
**Speaker name** says the recording is that one person; the one entry
that can be picked instead, **several speakers**, says there are
several, and the voices found then hang under that row as indented rows
of their own. Only an answer given shows them: a recording whose
separation is stored already and that nobody has answered for keeps an
empty field and no voice rows. Nothing measured is lost -- the voices
stay in the project and in the cache folder, and picking **several
speakers** later brings them up at once, with their names and cameras
and without computing again. The last column says how far that got and
offers **Break off** while it runs ([Speech recognition and speaker
separation](speech.md)). Nothing there starts a separation: a name
typed over **several speakers** hides the voice rows again and keeps
what was worked out, and what brings them back is the answer in the
field. The selector **belongs to** lists the cameras, then two special
cases:

- **no camera of its own**: in the Full-Mix, but nobody's first track.
  For someone heard but not seen.
- **do not use**: out entirely, and the speaker name goes grey. For a
  recording whose video is still missing.

The selector is there with the **Multitrack** tick and without it: which
camera a recording belongs to is the same question either way, and the
camera cut asks it whether the tick is set or not. Clicking the tick
therefore takes nothing away -- a camera picked by hand stays picked.
Only where a recording shows its voices as rows of their own does the
selector give way: the rows below carry the cameras then, and the
recording's own cell says so in grey.

**Speaker name** starts empty, with the name guessed from the file name
beside it in grey. Type nothing and the guess counts -- but only if it
begins with a letter, in any alphabet, not just in a to z. A guess like
`0008A` does not, the field stays empty, and with Multitrack **Start**
stays locked until a name is there: the name becomes that track's label
at auphonic.com, read there by people who never saw the file. A typed
name counts as typed.

A name belongs to one person, so it stands on the sheet once. Type one
that is there already and the field goes red -- on both levels, whether
the other bearer is a recording or a voice under one.

What follows from that is two different things. Two recordings of one
name are a question and not a refusal: the line under the table names it
and says **occurs more than once. These recordings are merged into one
track and placed in sequence by their timecode -- correct if recording
was stopped in between**, which is exactly what that grouping is for. A
voice cannot be merged with anything -- it is one person inside one
separation -- so a voice carrying a name somebody else has locks
**Start**, and the line under the button names it and says **is on more
than one speaker -- a name is a person, and every person needs their
own**.

The lower table has a row per camera: **Camera**, **new file name**,
**gets audio from**, **Kind** and **Camera audio**. The last two stand
in the file list as well, on the same value, and they stand here a
second time because the player is here: that a clip is in truth an
outro is noticed while watching it. A click on a row fetches that file
into the player.

**new file name** is what will come out of that camera. It is a
proposal until somebody types over it, and it is built from the
production name, the camera and the speakers in front of it. **gets
audio from** beside it names those same speakers. A camera nobody is
assigned to says **the mix of all tracks** there, and the wide shot
says **no speaker -- this is the wide shot** -- or names whoever was
assigned to it before and has been moved to **no camera of its own**.

**A name that is only suggested counts in both.** The name field of a
recording starts empty with the guess from the file name standing in it
in grey, and that guess is what the run works with, so it belongs in
the camera's file name and in **gets audio from** as well. It used to
be missing from both while the run had it, and the camera then went to
Resolve under a file name with nobody in it. Typing the name over
changes nothing about that -- it was already the name that counted.

A file the measurement can place nowhere is not marked in this table.
Every note about a file stands in the file list, where the files are
chosen and where it is read before anybody gets this far. Here only the
**Kind** shows what became of it: **Content** and **Wide shot** are
barred, and the program's own answer stands in the field -- **Intro**,
or **ignore this video** where nothing at all could be measured of the
file ([The interface](interface.md)).

Under the tables the **Multitrack** tick sits a second time. It is the
same tick as under **Production**: click either one and both show it.
The count is the same on the command line (`--multitrack`).

Multitrack needs two input tracks. Three things count as a track:

- a recording of its own,
- a channel of a multichannel recorder,
- the audio of a video file whose **Camera audio** stands on **use the
  audio**.

The program counts the rows of the upper table, minus those on **do not
use**. The camera cut does not need this field.

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

**A clock time works even where the longest camera carries no clock.**
It is the longest camera the window is counted in, and it need not be
the one that knows the time of day: the axis is hung on the clocks of
the other files, and the run says which ones it took and what they make
the first frame of that camera read. Only where not one file on the axis
carries a clock does a clock time have nothing to be converted through;
the run says so and stops, and then only a value from the window start
works -- `+12:30`, `90`, `-30`.

### How much of each camera is written

The window decides what ends up in the output folder. As soon as one of
the two marks stands, every camera is written for that stretch only and
no longer for the whole shoot. Five minutes out of a real interview left
6.09 GB in the folder where the same run used to leave 83.57 GB.

Without a mark nothing is cut away. Every camera then comes out at its
full length, exactly as before.

Each written camera carries a second more than the window at either end,
and at the front the program goes back from there to the key frame
before it. That margin is a run-up and not an oversight. The run checks
its own cameras and calls one misplaced from a single frame onward, so a
second is twenty times the error it will tolerate; and a picture that
begins between two key frames starts up to 400 milliseconds away from
its own sound. The margin buys both, and what it costs is a second of
picture at either end.

The cut is untouched by this. The same shots stand at the same moments
as before, to the millisecond, and the sound in the written files is the
sound that was there.

Every camera reports a line **Time window**: how much of it was written,
and from which point of the recording. After the list of written files
one line names what the cameras carry against how much was recorded.
Where the key frames of a camera cannot be read, the program says so and
leaves that camera's start where it is.

In the same block each camera reports its offset and its clock drift.
One of them reports no drift: **Clock drift: nothing measured -- this
is the reference the others are held against**. It is the longest
camera, the one all the others were measured against, so there is
nothing about it that a measurement produced. It used to print a row of
noughts there -- nought ppm, nought of nought points -- which reads
like a measurement and was none.

Wanting more than the window holds means moving **Mark In** and **Mark
Out** apart and running again. There is no separate switch for it.

### What goes into the camera files

The first audio track of each camera file is the mix of exactly the
speakers in that picture: `Mix <A> + <B>`. With only one speaker it
carries their name. Then those speakers singly, then `Full-Mix (…)`,
last `Camera Original`. The program measures loudness over the sum and
applies it to every track alike, so their balance stays. Which target it
uses comes from **Loudness** in the **Production** box, or from `--lufs`;
without either, the sound is taken from the source files and nothing is
adjusted ([Preflight](preflight.md)).

The program also writes the tracks as files, into `auphonic-tracks/` as
`final_<name>_<timecode>.wav`. The timecode is in the name and in the
bext chunk, and iXML comes along for Premiere and Media Composer.

### Multitrack with no camera at all

Sometimes there is no picture: several microphones on one table, and
nothing filming. A run with the tick and no video file used to be turned
away for want of a time axis. It now builds the axis out of the tracks
themselves -- they are laid against each other instead of against a
camera.

The longest recording is the reference, for the same reason the longest
camera is: it overlaps most with the others. Every other track is
measured against it, offset and clock drift in one go, and the log names
the reference with its running time and each track with what was found.
A track that cannot be placed is named and stays out.

The window holds everything any track heard. A recording switched on
late gets silence in front of it, one switched off early silence behind,
and the log says how much of each and on which track. A silent edge
costs less than a recording cut short.

What comes out is one file per voice in the output folder, called
`<Speaker name>_aligned.wav`: all of the same length, all beginning at
the same moment, which is what the processing of the sound wants. With
no output folder set they land beside the first recording. With a key
the same tracks go up to auphonic.com as **one** multitrack production
as well, and what comes back is held against what went up; without a
key, or with `--without-auphonic`, they stay on this machine.

In point and Out point hold here too (`--in-point`, `--out-point`), but
only as a value counting from the start of the window -- `+12:30`, `90`,
`-30`. A clock time has nothing to be converted through, because there
is no camera whose timecode the axis hangs on, and the run says so and
stops.

**A loudness target does nothing to the sound on this path.** A gain per
track would pull the voices out of the very balance this path exists to
keep, so the tracks leave as they were recorded and the loudness is set
where they are mixed. Given `--lufs` and no key, the run says that in
one line; given a key, the value is still held against what the preset
masters to ([Preflight](preflight.md)).

### When something goes wrong

- **Multitrack, no picture, and the run stops straight away.** Once the
  blocks are grouped only one track is left, and Multitrack means one
  track per voice. Rather than glue two people into one file the run
  stops before it joins anything. Where two people were taken for one
  recording, `--apart` keeps a block out of the grouping.
- **Only one track found a place.** The others could not be measured
  against the reference, and one track on its own has nothing left to
  lie against. The lines above name each one and why it was dropped.
- **A row is marked, and the mark is not red.** Under the name stands
  **sound not recognised; placed by its timecode**. Nothing has to be
  done: the sound of that file was not recognised, its clock places it
  among the others to the frame, and one of the two ways to a place is
  enough. The file lies on the axis and goes into the run.
- **A row stands in red.** That file has no place at all: nothing in its
  sound matches the rest of the material, and no timecode places it
  among the others either. Pick **ignore this video** in the column
  **Kind** of the file list, or take the file out of the list with
  **Remove**.
- **A row went to ignore this video by itself.** That file has no place
  at all: nothing in its sound matches the rest of the material, and it
  carries no timecode either. The program proposes leaving it out
  rather than laying it down at a guess, and the log names the file.
  Give it a timecode that fits the other recordings -- another program
  has to set that -- or let the proposal stand. An answer given by hand
  settles the row for good; a file that can be placed again gets its old
  **Kind** back ([The interface](interface.md)).
- **Mark In and Mark Out stay locked.** The common time axis is not
  there yet. Wait for the bar under the tables.
- **Several cameras, no audio recording, and Start stays locked.** No
  camera is contributing its sound. Set **Camera audio** to **use the
  audio** at every camera that is to be heard; each one is then a track.
  They no longer become tracks by themselves: a camera recording a
  usable track cannot be told from one merely filming in the same room.
- **A voice carries a name somebody else has, and Start stays locked.**
  A name is a person, and the cut puts a person on one camera; the same
  name twice would be one person in two places. Give the voice a name of
  its own, in its indented row under the recording. Two **recordings**
  of one name are another matter -- those are joined into one track on
  purpose and only want confirming, so what has to change is the
  indented row, not the recording's.
- **A speaker is missing from the Full-Mix.** That row has **do not
  use** in the column **belongs to**.

The tracks are assigned, the window is set, and every camera file
carries its own mix. Next comes the question of who says what:
[Speech recognition and speaker separation](speech.md).

### Further options on the command line

This option is not in the window.

- `--parallel COUNT` sets how many camera files run at once: `0` is the
  default and decides for you, `1` takes one file after another. A
  higher count never runs more files than the list holds. The written
  files are byte-identical either way.
