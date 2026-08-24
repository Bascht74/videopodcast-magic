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

The report holds for both modes.

| Area | What | What follows |
|---|---|---|
| Picture | nominal rate against actual rate, spread of the frame spacing | see below |
| Picture | frame rates of the cameras against each other | which rate the timeline gets |
| Picture | multi-part cameras: gap between the blocks | where picture is missing |
| Sound | sample rate, bit depth, channels, length | 44.1 kHz is converted, and it says so |
| Sound | tracks much shorter than the longest | note |
| Sound | samples on the stop, per channel | note, integer formats only |
| Timecode | the clocks of the files against each other | note where a clock was not set |
| Room | bleed per pair of speakers, against the 3:1 rule | note for the *next* recording |
| System | free disk space against the estimated need | **stop** if it is short |
| Auphonic | preset algorithms, loudness target, track template | **stop** on a contradiction |
| Loudness | which target holds and where it comes from | -- |

A stop halts the run before anything is written or uploaded.

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
five windows over the shared time, each at a spot where exactly one
person is talking.

The yardstick is the 3:1 rule. With the other microphone three times as
far from the speaker as their own, the neighbouring voice is about 9.5 dB
quieter. That says something about the setup in the room. It also sets a
limit on what comes after: the less the microphones are separated, the
more cautiously De-Bleed at auphonic.com can work. It can only be changed
next time, so it does not halt the run.

One track alone leaves nothing to measure. The same holds for recordings
that overlap too little, and for a recording with no passage in which
exactly one person speaks. The report says so and the run goes on.

### Which loudness target holds

The target holds for both: normalising the tracks, and the target level of
the loudness display in the Resolve project. Without an entry it is
-16 LUFS.

**The mix is two-channel, and so is the measurement.** The single tracks
keep the channels their source has ([Channels](channels.md)). Every *mix*
though, the `Full-Mix` as much as one camera's mix, carries the same
signal on both channels, and the program measures it that way. On one
channel the same mix measures a good three decibels quieter; the
measurements behind that number are in
[What was measured](../development/measurements.md). Measure on one and
deliver on two and you are off by that much.

Normalising also puts the **loudness range** in the log, the distance
between quiet and loud passages. For speech 3 to 7 LU is usual; below
2 LU the log says so plainly. Then something was squashed by the leveler,
not by the limiter, which only catches peaks and takes off 6 dB at most.

### How the report counts the samples on the stop

The program counts, per channel, how many samples sit on the highest
value the format can hold. The hint names the channel, the count and the
peak level. It appears from eight samples on, and only when the peak
stands within 0.1 dB of full scale. The hint holds nothing up: an
overdriven recording is sometimes the only recording there is.

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

### When something goes wrong

- **Disk space short.** Free space on the target drive, or set another
  output folder in the strip under the file list. The temporary files of
  the run go into the system temp folder, somewhere else again.
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

`--lufs` sets the target loudness as a number (default -16, nearer to
zero is louder), `--platform` by purpose:

| Value | Target | What for |
|---|---|---|
| `podcast` | -16 LUFS | podcast directories, stereo |
| `podcast-mono` | -19 LUFS | podcast directories, mono |
| `youtube` | -14 LUFS | YouTube turns down only, never up |
| `broadcast` | -23 LUFS | EBU R128 |
