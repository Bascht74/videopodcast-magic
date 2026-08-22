# Preflight

*Auf Deutsch: [preflight.de.md](preflight.de.md). Back to the [contents](README.md).*

## Preflight

Before the first long step the script looks the material over. The report
holds for both modes and stands at one place, before the switch; the bleed
falls away where there is only one track.

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

A stop halts the run before anything is written or uploaded. `--anyway` runs
regardless, `--no-preflight` skips the check entirely.

Only what changed is measured, and it is remembered **per file**, not per
selection: path, size and modification time identify it. Adding a camera
measures that camera alone; what shows only in comparison -- frame rates,
resolutions, tracks out of line -- comes from the remembered data and costs
nothing. The bleed counts for exactly that set of tracks. Disk space and
loudness target are found afresh every time, and `--preflight-again` measures
everything again.

### Variable frame rate

A camera does not have to write a frame every 1/30 second; it can put a
timestamp on every frame and let the spacing vary -- phones do that when the
light goes. The file still states a fixed nominal rate. Two cases matter, and
the report says which:

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

The yardstick is the 3:1 rule: with the other microphone three times as far
from the speaker as their own, the neighbouring voice is about 9.5 dB
quieter. That says something about the setup in the room, not about
post-production, and can only be changed next time -- so it does not halt the
run.

### Loudness by platform

`--lufs` sets the target as a number, `--platform` by purpose:

| Value | Target | What for |
|---|---|---|
| `podcast` | -16 LUFS | podcast directories, stereo |
| `podcast-mono` | -19 LUFS | podcast directories, mono |
| `youtube` | -14 LUFS | YouTube turns down only, never up |
| `broadcast` | -23 LUFS | EBU R128 |

The value holds for both: normalising the tracks, and the target level of the
loudness display in the Resolve project.

**The mix is two-channel, and so is the measurement.** The single tracks keep
the channels their source has ([Channels](channels.md)); every *mix* though,
the `Full-Mix` as much as one camera's mix, carries the same signal on both
channels and is measured that way. On one channel the same mix measures a good
three decibels quieter -- that is measured, not assumed -- so measure on one
and deliver on two and you are off by that much.

Normalising also puts the **loudness range** in the log, the distance between
quiet and loud passages. For speech 3 to 7 LU is usual; below 2 LU the log
says so plainly. Then something was squashed, and not by the limiter, which
only catches peaks and may take off 6 dB at most, but by the leveler in front
of it.
