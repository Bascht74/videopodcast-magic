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
While a run is going, the **Speakers** cell of that row offers **Stop**
and the other rows offer nothing: one recording is separated at a time.

The field starts empty, with the name the file name suggests standing
in it in grey. Nothing else fills it in. A recording that carries a
separation nobody has answered for shows an empty field and no voices:
only an answer brings them up. It brings them up at once, with the
names and cameras they already had, and nothing is worked out twice --
so a wrong click costs no time.

Thinking again goes through the same field, and only through it. Where
a name stands, **several speakers** hands that recording to the
separation; where the voices stand, a name typed over the answer hides
them again and throws nothing away. The **Speakers** cell is a report
and not a question: nothing in it starts a separation.

Once a recording has been separated, **Separated: 4 speakers** stands
in its **Speakers** cell. Every recording carries its own: separating a
second one takes nothing from the first, both cells say their own
number, and both sets of voices stay in their rows. The project file
keeps them all.

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
as well. Where a person has a microphone of their own and the
microphones can be told apart, that track is the truth and there is
nothing to separate; where they hear each other too well for that, a run
without auphonic.com joins them and separates them together ("When the
microphones hear each other" below). The separation says who speaks
when; it does not make one track per speaker out of one recording.

Where there is no separate recording, the separation listens to the
sound of a camera. A camera whose sound fits the others too badly to be
placed by it is still allowed there, as long as its timecode puts it
among them; only a file with no place at all stays out. What a
separation needs is a place on the common time axis, and a clock gives
that place as well as a recognised sound does -- how good the camera's
own sound is decides nothing here.

**Which way somebody came in by makes no difference.** Everybody who is
heard is in the cut: a recording of one person, a camera's own sound
with one person on it, a recording several people share, and every voice
a separation found on one of them. They count together, not against
each other, and a separation on one recording takes nobody off the
others. Only **do not use** keeps somebody out, at the recording or at
the voice. Measured on two voices out of one separated recording and a
third person on a microphone of their own, each with a camera: all three
speak in the cut, and the picture goes to all three cameras.

What the separation runs on came with the installation; nothing has to
be set up for it. The one thing still fetched is the model itself,
about 33 MB, the first time a separation is asked for, and that happens
without a question. [What it needs](requirements.md#getting-the-program)
says where the model comes from.

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

### When the microphones hear each other

Two people sitting close together are on each other's microphones. Every
track then carries the neighbour as well, and a separation run over each
track on its own finds somebody in every passage of every one of them:
they all look as if they had talked almost throughout, and who really
spoke is no longer in the answer.

Where that is the case, the program stops asking the microphones one at
a time. It adds the aligned recordings into a single recording, lets the
separation listen to that one, and gives every voice it finds the name of
the microphone it belongs to. That name is the whole point: a voice out
of a joined recording would otherwise be Speaker 1, a name with nobody
behind it, and a name with nobody behind it has no camera -- the cut
would stand on the wide shot from beginning to end.

**Too well** is measured, not assumed. Every recording is held against
every other, in both directions, in the passages where one person is
speaking; where the smallest of those distances is under 20 dB, the
microphones are joined. They go in as they were recorded. Making them
equally loud first would flatten the very difference the naming lives
on, because the recording levels here are as large as the bleed.

Measured, the tracks on their own name 37.5 per cent of the speech
right, the joined recording 97.6. On material where who speaks when is
known to the millisecond, the speech under the right name went from 72.5
to 92.7 per cent, and the time the picture stands on the same camera as
a run through auphonic.com from 46 to 96.5 per cent.

**Only on a run without auphonic.com.** The de-bleed there takes the
neighbours out of the tracks, and afterwards each track answers better
on its own than any joining of them could. A run that uploads, and a run
pointed at tracks that have already been processed, go the way they
always went: one voice per track, measured from the microphones.

**And only where the run works the separation out itself.** A separation
the window has already made travels with the run and is used as it
stands. Answer **several speakers** on one recording in the window, and
that one recording is what the cut is built from; nothing is joined.
Where the window separated nothing -- the usual case with a microphone
per person, where every row carries a name -- the run decides, and it is
the run that joins them. On the command line it decides as well, unless
`--speakers-from` or `--speakers-local` hands it something.

The log says which of the two happened. In place of the recording's
name, the block **SEPARATING THE SPEAKERS** then says that the
microphones hear each other too well to say who is speaking, and how
many of them are being listened to at once. Under **SPEAKERS --
SEPARATED BY VOICE** the voices come **From the separation in this
run**, and one line per voice says which microphone it belongs to and
how many dB it stands **ahead of the next microphone, the recording
level taken out**.

That number decides, and one dB of it is enough. Each microphone's own
level is taken out of the reckoning first: a recorder turned up louder
than its neighbour would otherwise collect the voices of the whole room.
A voice that no microphone is far enough ahead of keeps its label and
gets no camera, and two voices pointing at the same microphone cancel
each other out, because one microphone is one person. More voices than
microphones -- somebody in the room without one, or a voice out of the
run-up -- and not one of them is placed. Where in the end no voice can
be given a microphone, the log says that the tracks are measured
instead, and the cut is the one it always was: one voice per track.

### Naming the voices

The voices have no table of their own. They hang under the recording
they were heard in, as indented rows of the same list: the first column
says **Voice**, so that the step down can be seen at all, and beside it
stand the **Speaker name** and the camera under **belongs to**. The
names are filled in as Speaker 1, Speaker 2 and so on by speaking time,
the longest first. The counting does not start over at each recording:
a name the program makes up takes the first number nobody has, across
every separation and across the rows of the assignment table above.
Where Speaker 1 and Speaker 2 are taken, the next voice is Speaker 3. A
name given by hand is never renumbered, and a number that comes free is
filled again. No time is written in the row: which recording it is
stands in the row above, and how long somebody speaks is nothing anyone
decides here.

**No two speakers may carry the same name.** A name is a person, and the
cut puts a person on one camera; two of one name arrive there as one
person, and that one camera then stands twice at different places in the
same cut. So a name that is already on somebody else turns its field red
while it is being typed, and the hint on it says so. Where the second
one is a voice, **Start** waits until it has a name of its own: a voice
is one person in one separation and cannot be merged with anything. Two
recordings of one name are a question and not a refusal -- they are
meant to become a single track, laid end to end by their timecode
([Multitrack](multitrack.md)).

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
of it that folds it away. Its own **belongs to** says in grey **the
voices below carry the cameras**, and the rows underneath carry
the assignment; fold them away and it says there
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

### What is kept, and what is worked out again

Both the separation and the written-down words are kept on this
machine, outside the project. A recording that was taken apart once, or
listened to once, is read back the next time instead of being worked
out again -- also in another project, also after the program was
closed, also days later. That is why a second start on the same
material is suddenly quick.

**Read back is not an estimate.** It is what the first computation
produced, kept as it stood: the same passages to the same thousandth of
a second, the same words at the same points. Nothing is worked out a
second time, so nothing can come out differently.

The log says which of the two happened. Where a separation was read
back, the line **Separated once already: read back, not measured
again.** stands under the heading; where one has to be measured, a line
saying how much computing the recording is about to cost stands there
instead. For the words the line ends in **read back** in place of the
seconds the recognition took.

**For the words, what the file holds decides** -- not its name and not
its time. A recording renamed, moved into another folder or copied to
another disk is the same recording and is not listened to again. A file
written afresh under the same name, in the same second, with other
sound in it, is listened to again: the program compares what is inside,
not the label on it. Reading a file through for that costs about a
third of a second per gigabyte, against half a minute for an hour and a
half on a Mac, and the many minutes it takes where faster-whisper does
the work. The language and the way are part of it as well: the same
recording in German and in English gives different words, and the two
recognisers do not write the same ones either.

**For the separation, the recording as it lies decides** -- its place,
its size and when it was last changed -- together with the model, a
speaker count set by hand, and the way the program works the answer out:
a version that changes that measures afresh instead of handing back what
an older reckoning wrote. So the separation is worked out again when
the source file is exchanged, when it changes, when it is renamed or
moved, or when somebody sets a count. A moved time window, a new In
point, a changed offset or a renamed speaker carry on with the
separation already there. The separation from the window travels with
the run, and the program only converts it onto that time axis.

A speaker count set by hand belongs to the recording it was set for.
The button in another row drops it and counts afresh.

Both lie in the system cache folder, beside the envelopes
(`~/Library/Caches/videopodcast-magic/`, on Windows `%LOCALAPPDATA%`),
in `words/` and `speakers/`. A recording joined out of several
microphones lies in `speakers/` as well, under a name made out of the
recordings it holds, so the same material finds it again instead of
building it twice. It all stays there. Throwing it away breaks nothing;
it only means the computing happens once more.

### Where the speakers came from

The log says it. Two marks to search for: `SPEAKERS -- SEPARATED BY
VOICE` and `SPEAKERS -- MEASURED HERE`. Both stand in one log where both
apply, one under the other: the first says where the separations came
from and how many voices they hold together, the second names the tracks
no separation covers. Under them comes one line per speaker, with the
speech time and the number of passages, and that list is the whole cast
of the cut.

The measurement under the second mark needs a track per person, and it
reads every track, including those a separation already speaks for: the
bleed is taken out by holding the microphones against each other, so a
track left out of the reading would hear its neighbour and count that as
speech. If a separation cannot be used, the log says why and the run
carries on with what the tracks say.

Where the microphones were joined, the second mark stays away. The
joined recording speaks for every track, so no track is measured a
second time and nobody stands in the cut twice: everybody in it is a
voice. Where no voice could be given a microphone it is the other way
round -- the voices are let go and every track is measured, exactly as
it was before.

### What the dry run shows of the speakers

**Dry run** writes no result and leaves the measuring undone, with the
one exception at the end of this section. Where the separation of a
recording is already on this machine, it shows the cut it would make:
the block names the recording, says the passages were read back, and
counts the voices up.

```
SEPARATING THE SPEAKERS
  In recorder.wav, on this machine.
  Separated once already: read back, not measured again.

  SPEAKER_00  0:00:08.600 in 2 passages
  SPEAKER_01  0:00:04.000 in 1 passages
```

The voices carry the labels the separation gave them, because nobody
has named them: a run started on the command line has no window to take
names from. A separation taken out of a project or an assignment file
is listed the same way, under the names that stand in it.

Where nothing is stored, the dry run stops at that point. It says how
much computing the separation would cost, then **(measuring only:
nothing separated)**, and no voices follow. That is the whole
difference: only a measurement that would really have to be made is
left undone. Reading a separation back costs nothing, so it happens and
the result is shown.

The list stands here or nowhere. A full run says who speaks how long
further down, under the two marks above; a dry run ends before that, so
it counts the voices up at the place it reaches.

One thing it does do. Where the microphones are joined, that is decided
before the separation is asked for at all, so the dry run does that
part: it measures how far the microphones stand apart, writes the joined
recording beside the separations and stops after it. What it leaves
undone is the separation itself.

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

On the macOS way the recognition reports on itself afterwards, in the
progress line and in the log: **Recognised in de-DE: ready in 0.1 s,
heard in 25.8 s** -- which language it settled on, how long it took to
be ready, how long the listening itself took. That is what makes a
later run comparable to this one. The line is in the language of the
run; it used to be handed on in the recognition's own keywords, English
in the middle of a German run. Anything else the recognition says is a
fault, and it comes out as one.

Recognition runs on the finished mix, not on the single tracks. A quiet
recording can be enough for the speaker separation and still not carry
the text.

A recording listened to once is not listened to again, whatever the
cost was. What is kept and what is worked out afresh stands above,
under "What is kept, and what is worked out again". The window and the
run listen to different things -- the window to the recording, the run
to the mix it made of it -- so each of the two pays once.

### What the text is for

The text gives the sentence and clause boundaries for the camera cut,
described in [Speaker statistics, camera cut, EDL](camera-cut.md).
Without recognition the program still cuts, only without sentence
boundaries; the same chapter says what the wide shot does then.

### When something goes wrong

* **The row says the separation is not installed here.** Something has
  gone missing out of the installation. The message names the command
  that puts it back -- the same one that installed the program, with
  `-U` -- and it is one command for everything, not for the separation
  alone. Until then the run carries on without it: with a track per
  person the speakers come from the tracks, otherwise the cut stays
  out.
* **The separation breaks off with a message.** The log says what
  happened. With a track per person those tracks are measured as they
  always are and the cut still comes, one speaker per track; on one
  common recording there is none.
* **Start stays locked and a name field is red.** Two speakers carry the
  same name. The line under **Start** says which name it is; give the
  voice in its row a name of its own.
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
