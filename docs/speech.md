# Speech recognition and speaker separation

*Auf Deutsch: [speech.de.md](speech.de.md). Back to the
[contents](README.md).*

## What runs on this machine

The program writes down what is spoken, and it tells the voices on a
recording apart. Both run on this machine, without an account and
without an upload, and before anything goes to auphonic.com.

### Separating the speakers

On the **Assignment & time window** tab the assignment table has a
column **Speakers**. Every recording carries a button **Separate
speakers** in its own row, and that button takes that one recording
apart. While a run is going its button says **Break off** and the other
rows carry none: one recording is separated at a time.

Once a recording has been separated, **Separated: 4 speakers** stands
in that cell instead of the button. The program keeps one separation.
Separating a second recording puts its result in place of the first.

Under the tables one line says whether this machine works the
separation out at all. On a machine that is not a Mac, **Not on this
machine** stands beside it the first time. The project keeps the
answer: a project that has said no does not ask again, and the buttons
in the rows go with it.

On a Mac with one recording the separation starts by itself as soon as
the files are there. With more than one recording nothing starts on its
own; the button in the row starts it.

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

One voice in the table means no cut: nobody hands over, so there is
nothing to cut at. The passages go into the handover file, and the run
carries on to the end.

### Naming the voices

On the same tab a table stands under the assignment tables: **Voice**,
**Speaker name**, **belongs to**, **Listen**. It has one row per voice
found, filled in as Speaker 1, Speaker 2 and so on by speaking time,
the longest first. The **Voice** cell names the recording, how long
that voice speaks in it, and where its longest passage begins.

1. Press **Separate speakers** in the row of the recording. On a Mac
   with one recording it has already run.
2. Press a row of the voice table, or **Listen** in it. Both play the
   longest stretch that voice speaks.
3. Overwrite **Speaker name** with the name of the person.
4. If a voice is missing, press **One more speaker in `<file>`**
   under the table. The button goes through the same recording again,
   with one speaker more than the last run found. Then back to step 2.
   With more than one recording the name moves off the button into a
   chooser beside it.

A given count sharpens the separation. A wrong count quadruples the
picture time on the wrong person. Set it only when the number is known.
The measurements are in [What was
measured](../development/measurements.md).

![The voices of one recording](images/voices.png)

*Tab Assignment & time window: the voice table under the assignment
tables.*

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
