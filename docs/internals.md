# Inside the script

*Auf Deutsch: [internals.de.md](internals.de.md). Back to the [contents](README.md).*

## How the script is put together

The core is a single file, on purpose: copy, call, done, no installation.
Inside it one rule holds: **decisions belong outside, windows inside.**
Everything that computes or decides sits as a function at the top level and
can be tested without a window; `gui()` only builds the interface. So far:

| Function | what it decides |
|---|---|
| `run_argv` | the whole command line, checks and queries included |
| `slider_numbers` | the cut sliders as numbers, defaults filled in |
| `slider_argv` | the same sliders as switches |
| `build_handover` | the handover, with a sentence for every no |
| `choose_zero_point` | where programme time starts: audio first, picture as stand-in |
| `find_project_file` | the project file for whatever was pointed at |
| `format_complaint` | whether a stored file may be read at all |
| `project_files` | what of the project is still there and what is missing |
| `metrics_sentence` | the line under the preview: where speech time lands |
| `speech_heading` | sections from auphonic.com or measured here |
| `assignment_rows` | the rows of the upper table, camera audio included |
| `preselected_camera` | which camera an audio track is preset to |
| `camera_output_name` | the name of the new video file, without a duplicate |
| `measure_time_axis` | how the files lie against each other and against the clock |
| `axis_still_valid` | whether a measured axis still holds for these files |
| `pending_prework` | what envelopes and audio are still to fetch |
| `window_suggestion` | In point and Out point from what the cameras offer |
| `recordings_text` | the heading of the audio group |
| `hdr_findings` | whether a finished file passes as HDR |
| `copy_mov_atoms` | carry the `logs` atom over and read it back |

`choose_zero_point` is four lines and was twice the cause of a misplaced cut
-- now the rule stands in one place and has test cases. The other way round,
the building blocks of the interface -- `cell`, `table_build`, `item`,
`report`, `mark_red` -- stay in `gui()`: they are called from over a hundred
places and decide nothing.

`run_argv` shows no dialogs. It returns a list of `(kind, title, text,
button)` in the order intended -- `"error"` means show and abort, `"question"`
means ask and abort on no. So the order of the queries can be tested:
`argv_test.py` goes through eighteen cases.

## How speech is detected without Auphonic

Recorders are turned up to different degrees, so the threshold sits
over each track's own noise floor and not at a fixed level.

Without the bleed taken out of the tracks, every microphone reports
speech at once, no camera shows exactly those speakers, and the cut
stays on the wide shot for the whole recording.

## How far down the speaker gate still works

Measured on three real microphone tracks, remixed to a separation we
choose. Ground truth is therefore exact: 720 blocks in which somebody
speaks, and the count of how many of them the detection gets right.

| Separation | With the gate | Without it |
|---|---|---|
| 14 dB | all 720 right, nothing invented | 720 right, 36 invented |
| 10 dB | all 720 right | 528 right, 192 missed |
| 8 dB | all 720 right | 462 right, 258 missed |
| 6 dB | all 720 right | 77 right, 643 missed |
| **5 dB** | **all 720 right** | 30 right, 690 missed |
| 4 dB | 510 right, 480 invented, 210 missed | 30 right, 690 missed |

Down to 5 dB the gate is exact -- well below the 9.5 dB the 3:1 rule
asks for. Below that it does not fail all at once: at 4 dB no moment is
left in which exactly one person speaks, so most of the coupling can no
longer be measured. The separation then runs on half a model, which is
still better than none but no longer reliable. The log says how many of
the pairs could be measured at all.

Without the gate the failure below 6 dB is not "everybody speaks" but
"nobody speaks": every track is loud the whole time, the noise floor
rises with it, and nothing exceeds the threshold any more.

## How the players reach a spot

Seeking is a request in Qt, not a command, so every spot is set again until
it holds: every 120 ms, tolerance 350 ms, up to five seconds, and always at
a standstill. A `play` that does not arrive is repeated after 400 ms; when
the output device changes, the player follows the new device.

## How the progress bar counts

The run is split into weighted sections. Writing the camera files gets
the largest share, reading the plan the smallest. Where a section
reports nothing, the bar creeps on slowly, only a little past what was
last reported, and stops short of the end rather than standing still.

## How the channels are measured

Which two channels are one stereo pair is decided by *when* both hear
the same thing, not by how alike they are. Measured on built cases with
the delay put in on purpose:

| Case | at zero delay | read as |
| --- | --- | --- |
| X-Y, coincident | 1.00 | one pair |
| ORTF, 17 cm | 1.00 | one pair |
| pair at 30 cm | 1.00 | one pair |
| mono on both sides | 1.00 | one track |
| two clip-ons, 0.6 m | 0.16 | two microphones |
| two clip-ons, 1.2 m | 0.10 | two microphones |
| two clip-ons, 2.0 m | 0.10 | two microphones |

Level and correlation both fail here: with bleed the two microphones
are loud together most of the time. Read as a pair, both speakers land
in one track, and the camera cut has nothing left to switch between.

The absolute floor of -70 dBFS comes from a measurement as well -- two
excerpts of one 32 channel recording judged the same pairs differently,
because at -85 dBFS it was dither being compared.

The recording is judged as a whole and not block by block. On one mixer
recording the first five minute block was the soundcheck and gave one
used channel pair; the second was the recording and gave ten tracks.
Blocks are read one at a time because they do not all fit in memory at
once.

A block is read in one pass and taken apart afterwards, rather than
decoded once per channel: a 32 channel recording used to go through
ffmpeg 32 times. Measured on one 92 MB block of 32 channels, 2.0 s
instead of 22.9 s, with the same levels and the same pairs; a pair of
1.8 GB blocks drops from about fifteen minutes to about ninety seconds.

Both channel conversions are written out rather than left to ffmpeg,
and that matters more than it looks: ffmpeg's own result depends on the
output format. Writing integers it scales the matrix down against
clipping and the level comes out right after all, writing floats it
does not. The same call is correct in one place and 3 dB out in the
next. Its own conversion uses an equal-power law: measured on a signal
at -24.08 dBFS, one channel to two comes out at -27.09 and two channels
to one at -21.07. Three decibels one way or the other, inaudible in a
single listen and wrong in every meter.

Only neighbours are compared: channel 1 against 2, 2 against 3, and so
on. A pair whose two channels do not sit side by side is not found.

A camera's two channels are judged like a two channel recorder file:
two clip-on microphones on them give two rows with two speaker names.
On the command line (`--multitrack`) two separate recordings are
counted the same way as in the window, and the assignment file is what
the count is read from. A two channel file that was never split carries
no extra mark.

## How the time axis is measured

The time axis is measured with sample points over the whole runtime, a
regression line through them, and the median instead of the mean. The
interface uses the same method in the background as the run itself.

The spread of a file is read at five spots over it, two seconds each,
from the packet timestamps in the container.

## What the preflight remembers a file by

A measurement is filed under a fingerprint. The fingerprint is a sha1
over the measurement version, the language of the run and, for every
file involved, its absolute path, its size and its modification time;
the first sixteen hex digits of that hash name the file in the
preflight cache. A file that changed gets a different fingerprint and
is measured again, an unchanged one is read from the cache.

The language belongs in the fingerprint because a stored finding holds
its text ready-made: without it a run in one language would serve the
report of the last run in the other. The measurement version is raised
whenever a measurement starts to contain something new, which makes all
older entries stale at once. A cached entry written by a different
version of the program is ignored.

Every entry is written beside its place and then moved into it, so a
run broken off halfway leaves no half json to be read as a measurement
later.

## The order of work per video file

Per video file the run works in this order:

1. Which part of the audio has a counterpart in the picture? The rest
   falls away.
2. Align over envelopes against the camera's audio track.
3. Measure the clock drift and take it out, as far as the measurement
   carries; the picture is the reference.
4. Bring the audio to the start point and length of the picture, gaps
   filled with silence.
5. Reassemble: picture untouched (`-c:v copy`), the new audio as the
   first track, the camera track behind it, both named, timecode kept.
6. Measure again how far the new track lies against the camera track.

## What the loudness was measured at

| File | measured |
|---|---|
| mix on one channel | -29.4 LUFS |
| the same mix on both channels | -26.3 LUFS |
| after normalising, two channels | -16.0 LUFS |

Leaving it to the editing program would be an invisible trap: a mono
track panned to the middle of a stereo bus lands at 0, -3, -4.5 or -6 dB
depending on the pan law.

## How many processors are used

Half of the processors this process **may** use, at most four, never
more than there are files. May use, not has: a container or a taskset
can hold the process to two of thirty-two, and counting all thirty-two
would mean threads taking turns. Python 3.13 and newer answer that
question directly (`os.process_cpu_count()`); below it the machine's
count has to do.

## How a production at auphonic.com is created and started

The simple interface Auphonic offers for a single file has no field for
speech recognition. A production with a transcript is created first and
started second. For a single track the file goes to
`/api/simple/productions.json` together with preset and title, and
`action=start` is left out, so the production waits. The program then
reads the production back from `/api/production/<id>.json`, adds the
recognition to its own output files and posts all of it in one call to
the same address -- that call starts the production.

For multitrack the recognition is already part of the create request to
`/api/productions.json`; the tracks follow through
`/api/production/<id>/upload.json` and
`/api/production/<id>/start.json` starts the run.

Speech recognition is switched on with an empty service id, so
Auphonic's own Whisper does the work, shownotes stay off, and the
language stays empty where none is set. Three output files are asked
for beside the audio: `speech` as json, `subtitle` as srt, `transcript`
as txt.

When the production is done, everything is downloaded into
`auphonic-tracks/`: the ZIP with the single tracks and every further
output file the production carries.

On the simple path every output the preset would fold to mono is
switched off: what a preset folds cannot be unfolded afterwards.

On a recompute the track settings are brought to the preset as well,
each through its own address (`.../multi_input_files/<Name>.json`).

## How the key reaches curl

The key reaches curl through a temporary config file. `mkstemp` creates
that file readable by its owner alone, and a `chmod` to `0600` says so
again for the reader; on Windows the `chmod` only toggles the read-only
bit, and the protection there comes from the temporary directory. The
file holds one line, `header = "Authorization: bearer <key>"`, and the
key goes in escaped: backslash and quotation mark get a backslash,
carriage return and line feed are dropped. Without that escaping a
quotation mark or a line break inside the key would start a directive
of its own, because curl reads this file as configuration. The file is
removed in a `finally`, whatever happened; where it cannot be removed
it is overwritten with a single line first, so a file left behind no
longer holds the key. A failure to remove it never replaces the real
error.

## Track names and the MOV target

The target is MOV for every run, MP4 sources included. MOV keeps a
track name of its own; MP4 throws it away and writes "SoundHandler"
regardless, so the tracks could not be told apart. MP4 also has no PCM
in the standard. Nothing is computed again: the picture is copied over
(`-c:v copy`) and the audio is written uncompressed. There is no
`--container`.

## How a file name with a clock in it is read

Blocks whose names carry a time of day are joined when one follows the
other within two seconds. Recorders write whole seconds and a block is
rarely a whole one long, which is where the slack comes from; two
blocks that really follow one another are never further apart than
that. Six digits for the date or eight, six for the time, and the
calendar has to accept them -- `Take_991399_120000` is not a date and
is not read as one. Two names spelling the same moment -- `260808` and
`20260808` are the same day -- cannot be told apart, so neither of them
is taken, and that is said as well.

## How the colour tagging survives the copy

With `-c:v copy` ffmpeg rewrites the `colr` box from its own values and
replaces what it does not know: transfer function 21 (Apple Log) comes
back out as an 18. Without `-movflags +write_colr` it writes no `colr`
box at all, and the values live only in the bitstream, where Resolve
does not look. So the script reads the box out of the source itself --
not through ffprobe, which reports names instead of numbers and a wrong
name for what it does not know -- passes the numbers on explicitly
(`-color_primaries`, `-color_trc`, `-colorspace`, `-color_range`),
forces the write and checks afterwards: log line **Colour**.

The QuickTime keys of the container (`com.apple.quicktime.model`,
`com.apple.quicktime.software`, `com.blackmagic-design.camera.*`) ffmpeg
throws away without `-map_metadata 0 -movflags +use_metadata_tags`. The
script sets both.

## What makes a file count as HDR

Ungraded, Log looks flat and is easily taken for harmless SDR. It
carries the camera's full dynamic range all the same, and it bands in
eight bit.

The search through the QuickTime keys runs on word markers, not on
"log": that syllable hides in too many harmless words.

## How the `logs` atom is carried over

The atom sits in the picture description itself,
`moov/trak/mdia/minf/stbl/stsd/hvc1`.

ffmpeg cannot keep the atom: its MOV *demuxer* does not know the box
type and never reads it in, and its *muxer* writes only `colr`, `pasp`,
`gama`, `btrt` and the codec's own box into a picture entry. There is no
switch for it.

So the script adds the atom itself after writing, byte for byte from the
source. That works only because ffmpeg puts `moov` at the end of the
file: growing it there moves no media data, and the chunk offsets in
`stco`/`co64` stay valid. It keeps its hands off when

- `moov` is not the last box at the end of the file (as with
  `-movflags faststart`),
- a 64 bit box is in the chain,
- the picture entries are of different kinds, `hvc1` against `avc1`,
- the atom is over 64 KiB,
- or the atom is already there.

Afterwards it reads back: the top level boxes at the same offsets,
`moov` grown and still ending at the end of the file, the chain down to
the picture description readable again, every box inside its parent, the
atom there. On any mismatch the old `moov` comes back byte for byte.

## What stands in the project file

| Key | What |
|---|---|
| `format`, `version` | the naming (currently 3) and the version that wrote it |
| `files` | the list, each entry `{"path": ..., "kind": ...}` |
| `production`, `out_folder` | name and where it goes |
| `multitrack` | the tick, and with it the later tabs |
| `in_point`, `out_point` | the time window |
| `camera_cut`, `wide_at_edges` | every value of the camera cut |
| `assignment` | who belongs to which camera, what the new files are called, "own audio", and the last file in the player (`player_file`, `player_spot`) |
| `preset` | the chosen Auphonic preset, or `no-auphonic` |
| `transcript`, `speech_language` | the transcript tick and the language tag |
| `apart`, `together` | blocks taken out by hand, and put together by hand |
| `channels` | the stereo ticks, per file and channel |
| `timeline`, `timeline_absolute` | the measured position of every file |
| `call` | the command line of the last run |

The `assignment` cannot be guessed. The `timeline` saves the measurement
at the next start.

## How a spot for the wide shot is scored

Each candidate gets a weighted sum of three criteria -- length of the
pause (capped at 2 s, x3), closeness to the next entry of another
speaker (ramp over 6 s, x4), distance from the wanted spot (x1.5,
negative).

## Cutting when all speakers sit on one camera

With several speakers on one camera the cut has nothing to switch
between. It is cut anyway, at the change of speaker.

## What the key figures compare

What counts is the distance between the cameras, so the figures are
measured against the mean of all cameras and not against a target.

## The clip colours

The colours are sorted by distinguishability, so the first two lie as
far apart as possible. The wide shot gets "Tan" from that list, a warm
sand brown that on a dark background sits too close to the orange of
the second camera (34.9 CIE76); shown instead is a pale sage, at least
52.9 from every speaker colour. In Resolve the clip is still called
Tan, so that graded projects do not shift.

## Where the preview takes its offsets from

A handover file carries `offset` per camera, a preview from the speaker
statistics a `start_s` per camera, and both are read. The speaker
segments count from the start of the material that went to
auphonic.com.

## How the script talks to Resolve

The check runs in the background on the first look at the tab. A run
that ends by building a project should not find out at the end that
Resolve was never running.

That external scripting has been kept to the Studio edition since
version 19.1 is reported, not stated officially. This is why the
program measures whether scripting answers instead of going by the
edition it finds.

The word "multicam" does not appear once in the README that comes with
Resolve's scripting interface. The words "transition", "dissolve" and
"fade" do not appear once in that documentation either. The dissolve is
therefore pulled by hand, and the intro and outro clips lie over the
content instead of beside it, so that one drag on the upper corner is
enough.

## How the timelines are built

The cameras started at different times. Which part of each camera file
lands in the cut therefore comes from the measured offset, not from the
timecode.

Full length, uncut, one camera per video track, each at its measured
place: that is how a timeline destined to become a multicam clip has to
look.

Conversion turns every audio track into an angle. The Full-Mix and the
camera microphone would become angles without picture, and SmartSwitch
would hear every speaker on every camera. The surplus audio is
therefore deleted after the insert.

Remote grades glue the **Clip** level together with the source file, so
a single cut can no longer be corrected on its own. The colour group
does the same work without giving up the clip level. The script sets
local versions on every run because a project from an earlier run would
otherwise still have remote grades on.

## German and English: what lives where

The whole source is English -- names, messages, comments. German exists only
as translation strings, in `CATALOGUE["de"]` at the end of the file, keyed by
the English text. `T()` looks them up; a missing entry shows English rather
than a gap.

`--lang de` or `--lang en` fixes the language of a run; without the switch
`system_locale()` decides, from `LANGUAGE`, `LC_ALL`, `LC_MESSAGES`, `LANG`,
on macOS `AppleLocale`, on Windows `GetUserDefaultLocaleName`. A run speaks
one language. `--help` is the exception: the help stays English, because those
texts do not go through `T()`.

Nothing a machine reads is translated -- file names, folder names, track
names, the keys in the project and handover files, the column heads of the CSV
files. The keys are English (`speakers`, `cameras`, `length_s`, `start_s`,
`timeline`, `offset`), the files carry `"format": 3`, and `format_complaint()`
turns down anything older instead of reading a new meaning into old names.

Numbers are split: on screen they follow the language (25,000 against 25.000,
1.2 s against 1,2 s -- `group_text`, `decimal_text`), into files they always
go English. The CSV files are comma separated with a full stop as the decimal
mark, in every language: two runs have to stay comparable.

A further language costs no code: copy the `CATALOGUE["de"]` block, give it
the new two-letter code, translate the right-hand sides. `--lang` offers it
afterwards, and a system set to it picks it up by itself.

The test suite is English throughout, and `style_test.py` watches the source:
German comments, narrating comments, text lines over 79 characters, over-long
blocks, docstring headings without a full stop. Every counter is at zero.
