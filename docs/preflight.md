# Preflight

*Auf Deutsch: [preflight.de.md](preflight.de.md). Back to the
[contents](README.md).*

## What is checked

The program looks the material over before the first long step. It calls
that the preflight. On the **Files & production** tab this happens by
itself, and again after every change to the file list. One sentence under
the list says what was found, and each row carries a mark
([The interface](interface.md)). Hovering over the mark, or opening the
row, shows what stands behind it.

![The file list with the marks from the preflight](images/files.png)

*A tick on every row, and beside four of them the remark that the file
does not fit the rest. The one note, about bleed, stands under GENERAL
NOTES and in the sentence below the list.*

The report holds for both modes.

| Area | What | What follows |
|---|---|---|
| Picture | nominal rate against actual rate, spread of the frame spacing | see below |
| Picture | frame rates of the cameras against each other | the timeline gets the highest of them |
| Picture | multi-part cameras: gap between the blocks | where picture is missing |
| Sound | sample rate, bit depth, channels, length | brought to 48 kHz, and it says so |
| Sound | tracks much shorter than the longest | note |
| Sound | samples on the stop, per channel | note, integer formats only |
| Timecode | the clocks of the files against each other | note where a clock was not set |
| Room | bleed per pair of speakers, against the 3:1 rule | note for the *next* recording |
| System | free disk space against the estimated need | note where it is tight, **stop** where it is short |
| Auphonic | preset algorithms, loudness target, track template | **stop** on a contradiction |
| Loudness | which target holds and where it comes from | -- |

A stop halts the run before anything is written or uploaded.

Where the cameras do not all run at the same speed, the note names the
rate the timeline will get: the highest of them. Nothing has to be
converted beforehand -- every camera keeps its own rate, and the cut is
counted in it ([Resolve](resolve.md), "Cameras that run at different
speeds").

A timecode from the other side of midnight counts as one night, not as a
day apart. For files really recorded on different days, the measured
offset is the one to trust.

The program measures only what changed, and remembers it **per file**,
not per selection. It measures a newly added camera alone. Frame rates,
resolutions and tracks out of line show only in comparison and come from
the remembered data. The bleed counts for exactly that set of tracks. The
program finds disk space and loudness target afresh every time.

### What the report says about a variable frame rate

A camera need not write a frame every 1/30 second. It can put a timestamp
on every frame and let the spacing vary; phones do that when the light
goes. The file still states a fixed nominal rate. The report says which of
two cases it is:

- **Evenly off.** The file says 30, in truth it is a constant 29.98. That
  is clock drift, as in the audio. The audio is pulled onto the picture
  during alignment anyway, so the report only mentions it.
- **Unevenly.** The frame spacing changes mid-recording, and the audio
  *cannot* catch that. If the sample points spread during alignment too,
  only converting to a fixed frame rate helps.

The program reads the container only and decodes nothing. Only what is
not a whole frame duration, or what wanders over the file, counts as
spread.

### How the report measures bleed against the 3:1 rule

With several speakers in one room, every voice stands quietly in the
other microphones too. The report measures how much quieter. It takes
five windows over the shared time, twenty seconds each, and measures
inside them where exactly one person is talking. Five and twenty are
fixed; no switch sets them. On short material the windows get shorter
rather than the measurement being given up.

The yardstick is the 3:1 rule. With the other microphone three times as
far from the speaker as their own, the neighbouring voice is about 9.5 dB
quieter. That mark is fixed too, and no switch moves it: the further a
pair falls below it, the more of the neighbour is left in the track.
That says something about the setup in the room. It also sets a
limit on what comes after: the less the microphones are separated, the
more cautiously De-Bleed at auphonic.com can work. It can only be changed
next time, so it does not halt the run.

One track alone leaves nothing to measure. The same holds for recordings
that overlap too little, and for a recording with no passage in which
exactly one person speaks. The report says so and the run goes on.

### How much room the report wants

Before the first long step the report holds the free space against what
the run will write. That estimate is a rough one and says so: it counts
every camera as copied and given fresh audio tracks, adds the processed
tracks and the mix, and rounds upward throughout.

A time window makes the cameras shorter, and the estimate goes with it:
each camera counts with its own share of the window, so a short camera
gives up far less of itself than a long one ([Multitrack](multitrack.md),
"How much of each camera is written"). That only happens where an In
point and an Out point both stand and both count the same way -- both as
clock time, or both as a distance. One mark alone, or an Out point
counted back from the end, leaves the estimate at the whole material.
The run then writes less than the report asked for, never more.

A rough estimate cleared by a hair is not room enough. So the report
wants **15 percent more than it estimated itself** before it calls the
space good. In between -- the numbers do add up, but only just -- it
gives a note and lets the run go on; below the estimate it stops the run
as before. That margin is fixed and no switch moves it.

The report looks at both drives. What the run delivers goes into the
output folder, but the intermediate files of the run go into the system
temp folder, which is somewhere else again. Where the two sit on the
same drive, the same space is needed twice, and the report counts it
twice. On separate drives nothing changes.

### Which loudness target holds

The target holds for both: normalising the tracks, and the target level of
the loudness display in the Resolve project. It comes from **Loudness** in
the **Production** box on the first page of the window, or from `--lufs`
on the command line. The window offers five entries:

- **-16 LUFS (Podcast directories, stereo)**
- **-19 LUFS (Podcast directories, mono)**
- **-14 LUFS (YouTube -- turns down only, never up)**
- **-23 LUFS (EBU R128, broadcast)**
- **Take from source files**

A new project starts on -16 LUFS. The window remembers the entry last
chosen and starts the next new project on it, and a loaded project file
beats that memory: a project saved at -23 LUFS opens at -23 LUFS, even
where the machine had remembered **Take from source files**.

**Without a target nothing is adjusted.** No `--lufs` on the command
line, or **Take from source files** in the window, and the sound leaves
exactly as it came in: no gain on any track and no limiter. auphonic.com
goes on doing what its preset says. The sum is measured all the same and
the measurement goes into the log, under `Not adjusted:` -- taken from
the source files, no gain on any track and no limiter. The preflight says
the same in its Loudness row: taken from the source files, no `--lufs`
given, nothing is adjusted. In the Resolve project the loudness display
still needs a scale, so it is set to -16 LUFS, and the line above it in
the log says that this is only what the meter measures against.

**Every run is measured and adjusted the same way.** A run without
Multitrack ([The simple path](simple-path.md)) applies the target just as
any other does, and so does a run with no picture at all, where the
blocks of a recording are joined into one file. The log gives `Target:`
and `Result:`; without a target nothing is adjusted.

One path is the exception: Multitrack with no picture at all, where the
tracks are laid against each other. Nothing is levelled there -- a gain
per track would pull the voices out of the balance that path exists to
keep -- and the run says so in one line
([Multitrack](multitrack.md)).

**The mix is two-channel, and so is the measurement.** The single tracks
keep the channels their source has ([Channels](channels.md)). Every *mix*
though, the `Full-Mix` as much as one camera's mix, carries the same
signal on both channels, and the program measures it that way. One
recording on its own is the exception: there is nothing to mix, so a mono
recording stays on one channel and a stereo one on two. On one channel
the same mix measures a good three decibels quieter; the measurements
behind that number are in
[What was measured](../development/measurements.md). Measure on one and
deliver on two and you are off by that much.

Normalising also puts the **loudness range** in the log, the distance
between quiet and loud passages. For speech 3 to 7 LU is usual; below
2 LU the log says so plainly, and the lower it goes the flatter the
result. Then something was squashed by the leveler, not by the limiter,
which only catches peaks and takes off 6 dB at most. Those three
figures are fixed; no switch sets them, and the leveler is set at
auphonic.com.

### How the report counts the samples on the stop

The program counts, per channel, how many samples sit on the highest
value the format can hold. Three in a row make one event; one or two are
rounding and are not reported. That three is fixed and no switch sets
it. The hint names the channel, how many such runs there are, the
longest of them in samples and in milliseconds, and where the first one
sits. The hint holds nothing up: an overdriven recording is sometimes
the only recording there is.

The program counts in integer formats only. An integer format has a stop
at full scale, and nothing above it ever reached the file. Float has no
stop, and 0 dBFS there is a mark on the scale, not a wall. Both 16 and
24 bit come out identical at the stop;
[What was measured](../development/measurements.md) has the same clipped
source written in all three formats.

Without the count a clipped channel stays invisible. The program
measures the master as a sum, and the limiter pulls it under -1 dBTP. A
lapel microphone that stood against the stop all evening therefore comes
out looking clean.

### When a very short file is proposed as the intro

While the material is being looked over, the window also measures where
the files sit relative to each other ([The interface](interface.md)). A
file that fits nothing there is proposed for **ignore this video** in
the column **Kind**. That is right for a camera whose microphone heard
nothing of the room, and wrong for a jingle: a jingle fits nothing
because it is not a camera, and it is meant to be used rather than left
out.

Length tells the two apart. Of the files that fit nothing and that no
timecode places either, the shortest is proposed as **Intro** -- but
only where it is at most a tenth as long as the middle of the rest of
the material. The yardstick is the shoot itself, not a length written
down: a jingle is orders below what it sits among, while a file that
belongs to the shoot and merely fits nothing is about as long as
everything else.

**Intro** means the file is put at the front and never measured
([DaVinci Resolve](resolve.md)), and there is one of those. So the
proposal falls on one file only, the shortest of them, and on none at
all where an intro already stands somewhere in the list.

It is a proposal like the others. It fills only a **Kind** that still
carries the program's own answer, never one somebody picked, and a file
that a later measurement can place again gets its old entry back. A
timecode settles the matter before any of this, as long as one other
file carries one too: the file then has a place, and nothing is proposed
for it.

### When something goes wrong

- **A very short file suddenly stands on Intro.** It fits nothing in the
  material and is far shorter than everything around it, so the program
  takes it for a jingle. Pick a **Kind** by hand and that settles the
  row for good.
- **Disk space short, or only just enough.** Free space on the target
  drive, or set another output folder in the strip under the file list.
  The temporary files of the run go into the system temp folder: where
  that sits on the same drive as the output folder, the run needs the
  space twice, and an output folder on another drive is worth as much as
  clearing space. Where only a stretch of the recording is wanted
  anyway, a narrower In point and Out point is worth more than either:
  the cameras are then written for that window alone.
- **The preset masters to a different loudness.** Set `--lufs` to the
  value of the preset, or change the loudness target of the preset at
  auphonic.com. Both at once does not work: the tracks come back at one
  value and the mix goes to the other.
- **The multitrack preset holds no track.** Create one track in the
  preset at auphonic.com. The first preset track sets the processing for
  all tracks; without it they come back as they were uploaded.
- **A channel stands against the stop.** If the same voice was recorded
  a second time, on a camera for instance, use that recording instead.
  There is nothing to repair here, so record the next session at a lower
  level.

The material is now checked, and every complaint is either dealt with or
knowingly accepted. The report names the channels of every file.
[Channels: one track or two?](channels.md) settles whether a file with
more than one channel becomes one track or two.

### Further options on the command line

The window does not offer these.

`--anyway` runs despite a stop, `--no-preflight` skips the check entirely,
`--preflight-again` measures everything again instead of only what changed.
