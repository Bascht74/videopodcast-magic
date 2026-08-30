# Speech recognition and speaker separation

*Auf Deutsch: [speech.de.md](speech.de.md). Back to the
[contents](README.md).*

## What runs on this machine

The program writes down what is spoken, and it tells the voices on a
recording apart. Both run on this machine, without an account and
without an upload, and before anything goes to auphonic.com.

### Separating the speakers

On the **Assignment & time window** tab every recording carries a
**Speaker name** and a column **Speakers**. A name typed into the name
field says the recording is that one person. The one entry that can be
picked instead, **several speakers**, says there are several, and the
program goes and works out who speaks when in that one recording.
While a run is going, the **Speakers** cell of that row offers **Break
off** and the other rows offer nothing: one recording is separated at
a time.

The field starts empty, with the name the file name suggests standing
in it in grey. Nothing else fills it in. A recording that carries a
separation nobody has answered for shows an empty field and no voices:
only an answer brings them up. It brings them up at once, with the
names and cameras they already had, and nothing is worked out twice --
so a wrong click costs no time.

Where a name stands in the field, the **Speakers** cell offers to think
again: **Only one speaker -- separate the track?**, or, where the
voices are already there, to show them. One click and they stand in
their rows. A field nobody has answered is offered nothing.

Once a recording has been separated, **Separated: 4 speakers** stands
in its **Speakers** cell. The program keeps one separation. Separating
a second recording puts its result in place of the first.

Under the recordings one line offers the separation, and only where
it is needed. A Mac works it out by itself and gets no line at all.
Anywhere else the line stands there the first time, with **Not on this
machine** beside it. The project keeps the answer: a project that has
said no is told so on that line and is not asked again.

On a Mac with one recording the separation starts by itself as soon as
the files are there. With more than one recording nothing starts on its
own; the answer **several speakers** in the row starts it.

Separation is the way for **one common recording** that everybody is
audible on. It does not need the tick **Multitrack (one track per
speaker)**: the column stands there on both paths, with a single camera
as well. If each person has their own microphone, the tracks are the
truth and nothing has to be separated. The separation says who speaks
when; it does not make one track per speaker out of one recording.

The setup fetches about 218 MB the first time, the model about 33 MB
after it. [What it needs](requirements.md#getting-the-program) says
where the model comes from, and the measurements behind the 218 MB are
in [What was measured](../development/measurements.md).

Over the whole file the separation hears the run-up before the show as
well. The conversion cuts to the time window, but the number of
speakers in the table is the one of the uncut run. A conversation in
the run-up puts one voice more in the table than the episode holds.

One voice in the table and one camera means no cut: nobody hands over,
and there is nowhere else the picture could go. The passages go into
the handover file, and the run carries on to the end. With a second
camera there is somewhere to go: that one camera stands and the wide
shot breaks it up. Measured on 25.8.2026, five minutes on two cameras
gave 15 shots, 7 of them the wide one; the same five minutes on one
camera gave 1.

### Naming the voices

The voices have no table of their own. They hang under the recording
they were heard in, as indented rows of the same list: the first column
says **Voice**, so that the step down can be seen at all, and beside it
stand the **Speaker name** and the camera under **belongs to**. The
names are filled in as Speaker 1, Speaker 2 and so on by speaking time,
the longest first. No time is written in the row: which recording it is
stands in the row above, and how long somebody speaks is nothing anyone
decides here.

Once the words are written down, those names become a proposal that
says something. Who asks the questions and who answers can be read out
of the speech: the program counts, for every voice inside the time
window, how many of its sentences end in a question mark, and proposes
**Guest** for the one who asks least and talks longest, **Host** for
the others. It proposes only over a name it made up itself -- a name
somebody typed is never touched, not even one that reads like the
program's own.

The same counting says when a voice is not a speaker. One that gathers
too few sentences inside the time window is proposed for **do not use**,
with a line in the log saying which and why. That happens where a
separation splits somebody in two, or where a voice belongs to the
minutes before the interview began. Move the In point and the proposal
follows at once: widen the window and the voice comes back to its
camera and takes its name from the new ranking.

**Do not use** on a voice means it is not there. No camera, no track,
no speaker at auphonic.com, no line in the transcript and none in the
speaking shares; where it spoke, nobody is speaking, and the picture
stays on whoever it was on until the next voice that counts. What was
separated is kept in the project file all the same, so switching the
voice back on costs no computing.

The writing down costs about half a minute for an hour and a half of
recording. It runs once, in the background, after a separation exists
-- the long computation somebody either started or was asked about --
and never on merely adding files. It installs nothing and downloads
nothing: it takes the recognition macOS brings with it, and the other
way only where a run has already put it there.

A recording that shows voices comes up open, with a triangle in front
of it that folds it away. Open, its own **belongs to** stays empty and
the rows underneath carry the assignment; folded away, it says there
what folding takes off the screen -- the cameras: **on 2 cameras**, and
**on 1 camera, 1 without** where a voice has none yet. The number of
voices is not repeated there, because the **Speakers** cell of the same
row already says it. The assignment always stands on one level, never
on two. Recordings that show no voices are a flat list, without
triangles.

1. Answer the **Speaker name** of the recording with **several
   speakers**, the one entry that field offers to pick. On a Mac with
   one recording the separation has already run, and the answer only
   brings the voices onto the screen.
2. Click the row of a voice. The player on the right opens the
   recording where that voice speaks longest and plays at once.
   Clicking is how a voice is heard; there is no button for it.
3. Overwrite the **Speaker name** in that row with the name of the
   person.
4. If a voice is missing, press **One more speaker in `<file>`**
   under the recordings. The button goes through the same recording
   again, with one speaker more than the last run found. Then back to
   step 2. With more than one recording the name moves off the button
   into a chooser beside it.

A given count sharpens the separation. A wrong count quadruples the
picture time on the wrong person. Set it only when the number is known.
The measurements are in [What was
measured](../development/measurements.md).

![The voices of one recording](images/voices.png)

*Tab Assignment & time window: the voices under the recording they
were heard in.*

### When the program separates again

The program works the separation out again only when the source file is
exchanged, when it changes, or when somebody sets a speaker count by
hand. A moved time window, a new In point, a changed offset or a
renamed speaker carry on with the separation already there. The
separation from the window travels with the run, and the program only
converts it onto that time axis.

A speaker count set by hand belongs to the recording it was set for.
The button in another row drops it and counts afresh.

### Where the speakers came from

The log says it. Two marks to search for: `SPEAKERS -- SEPARATED BY
VOICE` and `SPEAKERS -- MEASURED HERE`. The separation on this machine
counts first. The measurement under the second mark needs a track per
person. If the separation does not fit the run, the log says why and
the run carries on -- with the measurement from the tracks, or without
a cut by speaker.

### How the program writes the text down

Recognition takes one of two ways, and the difference shows on the clock
alone.

* **macOS 26 brings it along.** Recognition sits in the operating
  system; an hour of audio in a good 20 seconds. It asks for the
  Command Line Developer Tools.
* **Everywhere else faster-whisper.** The program fetches 144 MB of
  packages and a model of 1.5 GB the first time. On an ordinary Windows
  machine recognition is the most expensive step of the whole chain.

The measurements behind these times are in [What was
measured](../development/measurements.md).

The program looks for the way it has and says in the log which one it
took. Recognition takes the language setting of the run. If that is
empty, macOS works with the system language and Whisper guesses it from
the audio. The run writes the text down alongside the camera cut, not
ahead of it.

Recognition runs on the finished mix, not on the single tracks. A quiet
recording can be enough for the speaker separation and still not carry
the text.

### What the text is for

The text gives the sentence and clause boundaries for the camera cut,
described in [Speaker statistics, camera cut, EDL](camera-cut.md).
Without recognition the program still cuts, only without sentence
boundaries; the same chapter says what the wide shot does then.

### When something goes wrong

* **The row says the separation is not set up.** It fetches what it
  needs on the first run. If that fails, the run carries on: with a
  track per person the speakers come from the tracks, otherwise the cut
  stays out.
* **The separation breaks off with a message.** The log says what
  happened. With a track per person the program measures the tracks
  instead and the cut still comes; on one common recording there is
  none.
* **On a Mac recognition takes the slow way.** The Command Line
  Developer Tools are missing. `xcode-select --install` fetches them;
  after that the run takes the fast way.

The voices now have names, and the program has written the text down.
What the cut makes of both is in [Speaker statistics, camera cut,
EDL](camera-cut.md).

### Further options on the command line

These options are not in the window.

* `--speakers-local <FILE>` takes that recording apart by voice on this
  machine and cuts by the result.
* `--speakers-from <FILE>` takes a finished separation out of a project
  or assignment file instead of working one out.
* `--speakers-count <NUMBER>` says how many people are to be found;
  without it the program works the count out.
* `--no-speakers-local` takes no recording apart by voice in this run,
  whatever else asks for it.
* `--no-speech-recognition` leaves the text out.
* `VPM_NO_SPEAKER_SPLIT=1` in front of the call: no column
  **Speakers**, no button, and the separation never starts by itself.
