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
are loud together most of the time.

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

## How the time axis is measured

The time axis is measured with sample points over the whole runtime, a
regression line through them, and the median instead of the mean. The
interface uses the same method in the background as the run itself.

The spread of a file is read at five spots over it, two seconds each,
from the packet timestamps in the container.

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

## How the transcription is asked for

The simple interface Auphonic offers for a single file has no field for
speech recognition. The production is therefore created first, then told
to recognise, then started. Its own output files are read and sent back
along with the new ones, so the audio the preset asks for does not fall
away.

On a recompute the track settings are brought to the preset as well,
each through its own address (`.../multi_input_files/<Name>.json`).

## Track names, and why the target is MOV

MOV keeps a track name of its own; MP4 throws it away and writes
"SoundHandler" regardless, so the tracks could not be told apart. MP4
also has no PCM in the standard.

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

## Where the preview takes its offsets from

A handover file carries `offset` per camera, a preview from the speaker
statistics a `start_s` per camera, and both are read.

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
