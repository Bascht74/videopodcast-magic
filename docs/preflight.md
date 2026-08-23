# Preflight

*Auf Deutsch: [preflight.de.md](preflight.de.md). Back to the [contents](README.md).*

## Preflight

The script looks the material over before the first long step. On tab
**Files & production** this happens by itself, and again after every
change to the file list. One sentence under the list says what was found,
and each row carries a mark. Hovering over the mark, or opening the row,
shows what stands behind it.

The report holds for both modes and stands at one place, before the
switch. The bleed falls away where there is only one track.

| | What | What follows |
|---|---|---|
| Picture | nominal rate against actual rate, spread of the frame spacing | see below |
| | frame rates of the cameras against each other | which rate the timeline gets |
| | multi-part cameras: gap between the blocks | where picture is missing |
| Sound | sample rate, bit depth, channels, length | 44.1 kHz is converted, and it says so |
| | tracks much shorter than the longest | note |
| Room | bleed per pair of speakers, against the 3:1 rule | note for the *next* recording |
| System | free disk space against the estimated need | **stop** where it is short |
| Auphonic | preset algorithms, loudness target, track template | **stop** on a contradiction |
| Loudness | which target holds and where it comes from | -- |

A stop halts the run before anything is written or uploaded.

Only what changed is measured, and it is remembered **per file**, not per
selection. Adding a camera measures that camera alone. Frame rates,
resolutions and tracks out of line show only in comparison and come from
the remembered data. The bleed counts for exactly that set of tracks.
Disk space and loudness target are found afresh every time.

### Variable frame rate

A camera need not write a frame every 1/30 second. It can put a timestamp
on every frame and let the spacing vary; phones do that when the light
goes. The file still states a fixed nominal rate. The report says which of
two cases it is:

- **Evenly off.** The file says 30, in truth it is a constant 29.98 -- clock
  drift as in the audio. The audio is pulled onto the picture during
  alignment anyway, so the report only mentions it.
- **Unevenly.** The frame spacing changes mid-recording, and the audio
  *cannot* catch that. Where the sample points spread during alignment too,
  only converting to a fixed frame rate helps.

The check reads the container only -- nothing is decoded, so it costs no
time. Only what is not a whole frame duration, or what wanders over the
file, counts as spread.

### Bleed and the 3:1 rule

Where several speakers sit in one room, every voice stands quietly in the
other microphones too. The report measures how much quieter, at five windows
over the shared time, each where exactly one person is talking.

The yardstick is the 3:1 rule: with the other microphone three times as
far from the speaker as their own, the neighbouring voice is about 9.5 dB
quieter. That says something about the setup in the room, not about
post-production. It can only be changed next time, so it does not halt
the run.

### Loudness

The target holds for both: normalising the tracks, and the target level of
the loudness display in the Resolve project. Without an entry it is
-16 LUFS.

**The mix is two-channel, and so is the measurement.** The single tracks
keep the channels their source has ([Channels](channels.md)). Every *mix*
though, the `Full-Mix` as much as one camera's mix, carries the same
signal on both channels and is measured that way. On one channel the same
mix measures a good three decibels quieter. Measure on one and deliver on
two and you are off by that much.

Normalising also puts the **loudness range** in the log, the distance
between quiet and loud passages. For speech 3 to 7 LU is usual; below
2 LU the log says so plainly. Then something was squashed by the leveler,
not by the limiter, which only catches peaks and takes off 6 dB at
most.

### Further options on the command line

The window does not offer these.

`--anyway` runs despite a stop, `--no-preflight` skips the check entirely,
`--preflight-again` measures everything again instead of only what changed.

`--lufs` sets the target loudness as a number, `--platform` by purpose:

| Value | Target | What for |
|---|---|---|
| `podcast` | -16 LUFS | podcast directories, stereo |
| `podcast-mono` | -19 LUFS | podcast directories, mono |
| `youtube` | -14 LUFS | YouTube turns down only, never up |
| `broadcast` | -23 LUFS | EBU R128 |
