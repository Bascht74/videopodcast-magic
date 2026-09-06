# Inside the script

For the folder `videopodcast_magic/` and the text files in it. How the
program is put together, and how each step works. Not part of the
manual and English only: this is for whoever changes the program, not
for whoever uses it.

What was measured is in [What was measured](measurements.md): hit
rates, run times, distributions, comparisons.

---

## How the script is put together

`videopodcast_magic/__init__.py` is the way in and holds most of the
program -- 10 551 lines. Eleven pieces have moved out, and each sits
beside it in a folder of its own with an `__init__.py` in it: `ui/`
holds the window and everything it shows, asks or offers (12 841
lines); `cut/` who is on camera when, and what carries it out of here
(3 925); `resolve/` the project in DaVinci Resolve, timelines, colour,
render and markers (2 755); `speakers/` who is speaking, out of the
sound alone (2 060); `pipeline/` the chain the recordings run through
until the camera files are written (1 880); `preflight/` whether the
material fits together before the first long step, and the ffmpeg run
that shows its progress (1 507); `auphonic/` the sending to
auphonic.com and the fetching back -- the key, the presets, the
production, the waiting (1 226); `setup/` finding ffmpeg, offering the
way to get one, installing a missing module and keeping the key
(1 161); `speech/` what is said and when, and what is written down
from it (1 130); `desktop/` the picture and the shortcut the first
start lays down (657); `language/` a `.po` file per language, nothing
but texts in it, and the reader that looks one up (313). All counted
6.9.2026 with `wc -l`, and the figure of the day is that command, not
this paragraph. `models/` is a twelfth folder and the odd one out:
the speaker model lives there and no code at all, so `beside()` never
reaches for it. There is nothing to build.

**How a piece is joined on, and why it is not an import.** `beside()`
reads the piece out of the folder and hands the program in before the
file is read; the piece then binds by name what it takes, one line per
name, because `source_no_loose_ends` wants a visible origin for every
name in its own file. What is bound again while the program runs -- the
five sinks, `LANG`, `TOOL_TROUBLE` and the rest -- is reached through
`PROGRAM.` instead, and a name bent from outside is written through
into every piece that holds it. That last line is what keeps the suite
working: it bends 119 of the program's names, and a copy would part
from the original at the first assignment. It can be installed as well -- `pyproject.toml` makes a package
of that folder and puts a `videopodcast-magic` command on the path --
and nothing inside knows the difference: it is the same code either
way, and the name carries an underscore only because a hyphen cannot be
imported.

**A piece asks the program where the program is, never itself.** A
piece lies one folder deeper than the way in, so `__file__` in it names
that deeper folder. `find_required_tools` looks for an ffmpeg lying
beside the program and asks `PROGRAM.__file__` for the place; with the
piece's own `__file__` there it puts `videopodcast_magic/setup` on the
search path and answers "ffmpeg, ffprobe is missing." with both of them
lying beside the program -- measured 6.9.2026 on a copy that kept
`__file__`, against the same copy that asks the program.

**Where a piece is read decides what it can bind.** Most of them stand
at the end of the way in, after everything they take; `setup/` is read
at the top instead, because what stands under it wants ffmpeg or a
module that may not be installed yet -- and so it can bind only what is
above that line. `as_warn` is the one name it uses that is not, and it
goes through `PROGRAM.` for that reason and no other. `FFMPEG_FLOOR`
stays on the near side of the seam as well, and that one is measured:
`text_lang_settled_first` rewrites the floor line in the way in to put
a run under it, and reads no other file.

**Two pieces that need each other are read in the order that leaves one
name over.** `auphonic/` and `preflight/` are the pair: `choose_preset`
asks `check_preset` whether the chosen preset fits the run, and
`check_preset` reads that preset out of auphonic.com to answer. Read
`auphonic/` first and two names have to wait -- `check_preset` and
`report_findings`; read it after `preflight/` and one does --
`read_preset`. So it is read after, `preflight/` drops the binding line
and its one call site says `PROGRAM.read_preset(key, uuid)`. Counted
6.9.2026 out of the two files: 27 names cross that seam into
`auphonic/`, 26 of them bound at its head.

**The catalogues only travel because they are named.** setuptools packs
`.py` and nothing else, so `[tool.setuptools.package-data]` in
`pyproject.toml` names `"videopodcast_magic.language" = ["*.po"]`.
Before that line stood there the built wheel held not one `.po` file,
and nothing went red over it: it was found by looking inside the wheel,
which is the only place it shows. Both halves measured 5.9.2026 -- the
same package built without the line puts no `.po` into the wheel and
with it puts them in, and a copy of the program with every `.po`
deleted starts, still answers `languages()` with all nine codes, holds
an empty `CATALOGUE["de"]`, and says everything in English.

**It was a single file, on purpose, until 4.9.2026, and that day it
became a folder.** The catalogue was the first piece to move out and
the rest followed the same day. The large file is still large and
further cuts are to come, but the shape is now the one aimed at: a
folder with an `__init__.py` in it and no single program file left. One
thing follows from it, and it holds whatever the next cut does: **the
program is never copied out of its folder.** It reads its pieces out of
the folder it sits in, so the folder travels whole or the copy stops
during the import with a `FileNotFoundError` on `language/__init__.py`,
the reader beside it -- measured 5.9.2026 with the lone file copied out.
The `.po` files are the quieter half of the same rule: without them the
program starts and says everything in English, and nothing complains.

One rule holds inside it: everything that computes or decides sits as a
function at the top level and can be tested without a window. `gui()`
only builds the interface. So far:

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

`choose_zero_point` is four lines and was twice the cause of a misplaced
cut. Now the rule stands in one place and has test cases. The other way
round, the building blocks of the interface (`cell`, `table_build`,
`item`, `report`, `mark_red`) stay in `gui()`. They are called from
over a hundred places and decide nothing.

`run_argv` shows no dialogs. It returns a list of `(kind, title, text,
button)` in the order intended. `"error"` means show and abort,
`"question"` means ask and abort on no. So the order of the queries can
be tested: `run_command_built_test.py` goes through eighteen cases.

## How speech is detected without Auphonic

Recorders are turned up to different degrees, so the threshold sits
over each track's own noise floor and not at a fixed level.

Without the bleed taken out of the tracks, every microphone reports
speech at once, and no camera shows exactly those speakers. The cut
then stays on the wide shot for the whole recording.

## How the recogniser is built

The small Swift program is built once and kept in the cache until it
changes or the system is updated. The recognition takes its language
version from the system region.

## How the separation is run and stored

The segments are stored raw in file time, into the cache and into the
project file; the conversion happens where they are used.

pyannote 4 sends a trace to `otel.pyannote.ai` on every run. The
worker process switches that off first and does not run at all if it
cannot find the switch.

The waveform is handed over, not the file path: `torchcodec` cannot
load the ffmpeg libraries everywhere. The checksums of the model are
checked before every load.

## How the players reach a spot

Seeking is a request in Qt, not a command, so every spot is set again
until it holds. Every 120 ms, tolerance 350 ms, up to five seconds, and
always at a standstill. A `play` that does not arrive is repeated after
400 ms. When the output device changes, the player follows the new
device.

## How the progress bar counts

The run is split into weighted sections. Writing the camera files gets
the largest share, reading the plan the smallest. If a section reports
nothing, the bar creeps on slowly, only a little past what was last
reported. It stops short of the end rather than standing still.

## How the channels are measured

*When* both channels hear the same thing decides which two of them are
one stereo pair, not how alike they are. Level and correlation both
fail here: with bleed the two microphones are loud together most of the
time. Read as a pair, both speakers land in one track, and the camera
cut has nothing left to switch between.

The program judges the recording as a whole and not block by block. It
reads blocks one at a time because they do not all fit in memory at
once. A block is read in one pass and taken apart afterwards, rather
than decoded once per channel. A 32 channel recording used to go
through ffmpeg 32 times.

The program writes both channel conversions out rather than leaving
them to ffmpeg. ffmpeg's own result depends on the output format.
Writing integers it scales the matrix down against clipping and the
level comes out right after all; writing floats it does not. The same
call is correct in one place and 3 dB out in the next. The script's own
conversion uses an equal-power law.

Only neighbours are compared: channel 1 against 2, 2 against 3, and so
on. A pair whose two channels do not sit side by side is not found.

A camera's two channels are judged like a two channel recorder file:
two clip-on microphones on them give two rows with two speaker names.
On the command line (`--multitrack`) the count works the same way as in
the window, and it is a count of input tracks rather than of files: a
recording of its own, a channel of a multichannel recorder, or the
audio of a camera whose **Camera audio** stands on **use the audio**.
The count is read from the assignment file: `cameras_as_tracks` counts
the rows of `tracks_of` that carry `own_audio`, `camera_audio` or
`from_camera`. A two channel file that was never split carries no extra
mark.

## Which way a camera's audio goes

A camera's audio takes one of two ways, and they behave differently.
This is written down because reading only one of them leads to the
wrong conclusion about the other.

What decides is the **Camera audio** field at the video file: in the
file list on **Files & production**, and again in the camera table
beside the player on **Assignment & time window**, on the same value
both times (`audio_use_value`, `audio_use_bind`). It stands on **do not
use the audio** until somebody says otherwise, and there the sound is
not material at all and takes neither way. Synchronising is not part of
the question: the time axis is measured over the envelope of every
file, whatever the field says.

| Way | What happens to more than two channels |
|---|---|
| **use the audio**, with Multitrack | `camera_audio_tracks` cuts it into tracks, by the same measurement as a recorder file |
| the simple path: one video, no audio recording | `extract_audio_from_video` keeps every channel, and the file goes on whole |

On the first way a camera is not automatically one track: two clip-on
microphones on one channel each are two people, while a real stereo
pair stays one two channel track. The audio is extracted with every
channel it has and folded afterwards, never before -- folding four
channels to one and then asking what is on them would always answer
"one voice".

On the second way the field has nothing to decide: one video with sound
and no audio recording beside it is the only sound there is, so
`audio_use_settled` returns it as used with that reason, greyed out and
never stored. The way has one track by definition, so nothing is cut
there. `kept_channels` answers 2 for two channels and 1 for anything
else, which means a four channel file is treated as mono. Nothing then
happens to it, and the four channels survive by accident rather than by
design.

## How the time axis is measured

The time axis is measured with sample points over the whole runtime, a
regression line through them, and the median instead of the mean. The
interface uses the same method in the background as the run itself.

The spread of a file is read at five spots over it, two seconds each,
from the packet timestamps in the container.

**Two ways lead to a place and either one is enough**, and
`cannot_be_placed` is the only reading of that: the timecode places a
file (`timecode_places_it` -- one on the file and one on something else
in the material), or the measurement does. Only where neither answers
is the file refused.

What decides whether a measurement answers is not the correlation.
Measured over 85 pairs that belong together and 293 that do not, the
correlation runs to 0.203 at worst for a true pair and 0.124 at best
for a false one, so no threshold separates them -- a steady mains hum
pushes it down without moving where the file belongs. `fit_places_it`
reads the two numbers the fit already produced and throws away:
how many sample points were set (`FIT_POINTS_ENOUGH`, 50) and how far
they scatter (`FIT_SPREAD_MS`, 15 ms). Those give 85 of 85 and 0 of
293. The camera-against-camera door in the window's measurement reads
it, as the run's does.

The window used to leave a file out where the run kept it, so the cut
band showed one camera fewer than the finished project. It asks the
same question now. A file the sound could not vouch for is still marked
-- `weak` -- but it keeps the place its clock gave it, and only
`no_place` bars anything. `weak_note` and `weak_colour` turn the two
apart: warning colour and "sound not recognised; placed by its
timecode" against error colour and "does not fit the other files".

`speaker_source_pick` follows the same rule rather than one of its
own. It leaves out only what has no place at all; a camera whose sound
was not recognised may be the source of the separation. Measured on
such a camera -- hum at 99.94 Hz sitting 51.7 dB over the speech -- two
speakers in 90 seconds of it.

## What the preflight remembers a file by

A measurement is filed under a fingerprint. The fingerprint is a sha1
over the measurement version and the language of the run. For every
file involved it also covers the absolute path, the size and the
modification time. The first sixteen hex digits of that hash name the
file in the preflight cache. A file that changed gets a different
fingerprint and is measured again; an unchanged one is read from the
cache.

The language belongs in the fingerprint because a stored finding holds
its text ready-made. Without it a run in one language would serve the
report of the last run in the other. The measurement version is raised
whenever a measurement starts to contain something new, which makes all
older entries stale at once. A cached entry written by a different
version of the program is ignored.

Every entry is written beside its place and then moved into it. A run
broken off halfway therefore leaves no half json to be read as a
measurement later.

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

## How many processors are used

Half of the processors this process **may** use, at most four, never
more than there are files. A container or a taskset can hold the
process to two of thirty-two. Counting all thirty-two would mean
threads taking turns. Python 3.13 and newer answer that question
directly (`os.process_cpu_count()`); below it the machine's count has
to do.

## How a production at auphonic.com is created and started

The simple interface Auphonic offers for a single file has no field for
speech recognition. A production with a transcript is created first and
started second. For a single track the file goes to
`/api/simple/productions.json` together with preset and title, and
`action=start` is left out, so the production waits. The program then
reads the production back from `/api/production/<id>.json` and adds the
recognition to its own output files. It posts all of it in one call to
the same address, and that call starts the production.

For multitrack the recognition is already part of the create request to
`/api/productions.json`. The tracks follow through
`/api/production/<id>/upload.json`, and
`/api/production/<id>/start.json` starts the run.

Speech recognition is switched on with an empty service id, so
Auphonic's own Whisper does the work. Shownotes stay off, and the
language stays empty if none is set. Three output files are asked for
beside the audio: `speech` as json, `subtitle` as srt, `transcript` as
txt.

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
again for the reader. On Windows the `chmod` only toggles the read-only
bit, and the protection there comes from the temporary directory. The
file holds one line, `header = "Authorization: bearer <key>"`, and the
key goes in escaped. Backslash and quotation mark get a backslash;
carriage return and line feed are dropped. curl reads this file as
configuration. Without that escaping a quotation mark or a line break
inside the key would start a directive of its own.

The file is removed in a `finally`, whatever happened. If it cannot be
removed it is overwritten with a single line first, so a file left
behind no longer holds the key. A failure to remove it never replaces
the real error.

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
rarely a whole one long, which is where the slack comes from. Two
blocks that really follow one another are never further apart than
that. Six digits for the date or eight, six for the time, and the
calendar has to accept them. `Take_991399_120000` is not a date and is
not read as one. Two names spelling the same moment cannot be told
apart, so neither of them is taken, and that is said as well. `260808`
and `20260808` are the same day.

The "belongs to" chooser, which joins by hand what the search did not
find, asks that same `_joins_seamlessly` before it offers a target.
`join_barred` returns the ones it rules out and the reason, and
`choices_shut` greys those entries instead of dropping them: the answer
to "why can I not pick this" has to stand on the entry it is about.
Only where both sides carry a timecode -- without one there is nothing
to check, and that is what the chooser is for. `BLOCK_GAP_MAX_S` is the
fence, half an hour, because a clock is set wrong by whole hours and
half of the smallest of those catches every one while still letting a
real pause through. Joined over a gap of 12:19:48 the difference went
into the file as silence: 40 seconds of sound came out as 5.95 GB.

## How the colour tagging survives the copy

With `-c:v copy` ffmpeg rewrites the `colr` box from its own values and
replaces what it does not know. Transfer function 21 (Apple Log) comes
back out as an 18. Without `-movflags +write_colr` it writes no `colr`
box at all, and the values live only in the bitstream, where Resolve
does not look. So the script reads the box out of the source itself,
not through ffprobe. ffprobe reports names instead of numbers, and a
wrong name for what it does not know. The script passes the numbers on
explicitly (`-color_primaries`, `-color_trc`, `-colorspace`,
`-color_range`), forces the write and checks afterwards: log line
**Colour**.

ffmpeg throws the QuickTime keys of the container away
(`com.apple.quicktime.model`, `com.apple.quicktime.software`,
`com.blackmagic-design.camera.*`) without `-map_metadata 0 -movflags
+use_metadata_tags`. The script sets both.

## What makes a file count as HDR

Ungraded, Log looks flat and is easily taken for harmless SDR. It
carries the camera's full dynamic range all the same, and it bands in
eight bit.

The search through the QuickTime keys runs on word markers, not on
"log": that syllable hides in too many harmless words.

## How the `logs` atom is carried over

The atom sits in the picture description itself,
`moov/trak/mdia/minf/stbl/stsd/hvc1`.

ffmpeg cannot keep the atom. Its MOV *demuxer* does not know the box
type and never reads it in. Its *muxer* writes only `colr`, `pasp`,
`gama`, `btrt` and the codec's own box into a picture entry. There is
no switch for it.

So the script adds the atom itself after writing, byte for byte from
the source. That works only because ffmpeg puts `moov` at the end of
the file. Growing it there moves no media data, and the chunk offsets
in `stco`/`co64` stay valid. It keeps its hands off when

- `moov` is not the last box at the end of the file (as with
  `-movflags faststart`),
- a 64 bit box is in the chain,
- the picture entries are of different kinds, `hvc1` against `avc1`,
- the atom is over 64 KiB,
- or the atom is already there.

Afterwards it reads back:

- the top level boxes at the same offsets,
- `moov` grown and still ending at the end of the file,
- the chain down to the picture description readable again,
- every box inside its parent,
- the atom there.

On any mismatch the old `moov` comes back byte for byte.

## What stands in the project file

| Key | What |
|---|---|
| `format`, `version` | the naming (currently 3) and the version that wrote it |
| `files` | the list, each entry `{"path": ..., "kind": ...}` |
| `production`, `out_folder` | name and where it goes |
| `multitrack` | the tick, and with it the later tabs |
| `in_point`, `out_point` | the time window |
| `camera_cut`, `wide_at_edges` | every value of the camera cut |
| `assignment` | what is remembered per row and per file, each key by its prefix: `audio:` speaker name and camera, `video:` the name of the new video file, `own:` whether **Camera audio** is in use, `ownname:` the name that camera's track carries, `kind:` content, intro, outro or ignored, `voice:` the camera a separated voice sits on -- and `player_file`, `player_spot`, where the player stood |
| `preset` | the chosen Auphonic preset, or `no-auphonic` |
| `transcript`, `speech_language` | the transcript tick and the language tag |
| `apart`, `together` | blocks taken out by hand, and put together by hand |
| `channels` | the stereo ticks, per file and channel |
| `timeline`, `timeline_absolute` | the measured position of every file, and how fast its recorder ran |
| `call` | the command line of the last run |

The `assignment` cannot be guessed. `own:` holds only what somebody set
themselves; a **Camera audio** field that settled itself is derived
again at every start and leaves nothing behind. The `timeline` saves the
measurement at the next start.

Each `timeline` entry carries `path`, `mtime`, `size`, `start_s` and
`clock`. `clock` is the `b` of "recorder time = a + b * axis time", the
same figure the run takes out before it rewrites a track; it rides along
with the position because measuring it again costs the same minutes, and
a file that changed is caught by `mtime` and `size` anyway. It is not a
new format: an entry written before `clock` existed reads back as 1.0,
so an older project file opens and the axis in it still holds. The
format number stays 3.

## How a spot for the wide shot is scored

Each candidate gets a weighted sum of three criteria:

- length of the pause, capped at 2 s, x3,
- closeness to the next entry of another speaker, ramp over 6 s, x4,
- distance from the wanted spot, x1.5, negative.

## How a heap of leftovers is found

Mean segment length under 1.5 s and a share under 10 % of the
recognised speech time.

## How restlessness is found

At least 7 camera changes in a sliding 12 second window.

## Where the wide shot comes in

The wide shot comes in at the first of these that is found, in both
directions:

1. a sentence beginning within +/-2 s,
2. a clause break within +/-2 s,
3. a sentence beginning within +/-5 s,
4. a clause break within +/-5 s.

The exact spot comes out of the audio. In a window of +/-0.5 s around
the target the script takes the dip. The threshold is
p5 + 0.30 * (p95 - p5) of the 10 ms levels in that window itself, and
the dip is chosen by width - 0.5 * distance. A fixed dB threshold fails
on quiet material.

## Where the wide shot goes out

At least 5 s, then to the end of the sentence; beyond that the last
clause break at or under 15 s.

## How the level curve is measured

ffmpeg rectifies the signal and samples it down to 100 Hz: two seconds
for one hour of audio, cached afterwards.

## Cutting when all speakers sit on one camera

With several speakers on one camera the cut has nothing to switch
between. The program cuts anyway, at the change of speaker.

## What the key figures compare

What counts is the distance between the cameras, so the figures are
measured against the mean of all cameras and not against a target.

## Where the preview takes its offsets from

A handover file carries `offset` per camera. A preview without a
handover file works from `start_s` per camera. The speaker segments
are stored raw in the time of their source file and converted where
they are used.

The offset is not the whole of it: **Measure speakers now** applies the
clock speed as well. The run takes it out by rewriting the audio; here
the level curve is resampled instead -- `clock_on_axis` stretches the
100 Hz curve by `b` before the tracks are laid on one grid -- which is
the same correction at the resolution the levels are read with. The
speed comes out of the axis, is kept in `state["axis_clock"]`, and is
read per file by `audio_clock_of`, which answers 1.0 where nothing is
stored.

Measured over an hour: without it the preview's edit points ran about
143 ms away from the run's, three to four frames; with it they stay
inside one frame. Which camera the cut goes to never changed -- the
gap was always far under the shortest shot.

## What the line on the third tab stands on

`state["cut_basis"]` is set on every pass of the preview, before
anything is computed: `"run"` where this window's own handover file was
read, `"auphonic"` where that run went over auphonic.com
(`state["run_auphonic"]`, held when **Start** is pressed, so turning the
preset box afterwards cannot change the answer), otherwise `"measured"`.
`cut_basis_line` turns it into the sentence and the colour -- warning
for `"measured"`, good for the other two.

The line stands whenever there are numbers. It gives way to who is still
unmeasured (`tracks_left`) and to the reason a measurement failed
(`measure_failed`); the button beside it comes and goes on `tracks_left`
alone. Before this it was overwritten 400 ms after the measurement, when
the preview timer next ran and hid the whole row.

## How a separation reaches the run

The assignment file carries `speakers_of` with the source, the names
and the segments in the time of the source file. The run knows from
the alignment where this file lies on the axis and computes
`(t - a) / b`.

Files are looked up over the real path: `/tmp` on macOS is a link to
`/private/tmp`.

## Where the minimum edit duration stands

The minimum edit duration stands at one place in the source, and
interface, switch and function defaults read that same value: 3.0 s.

## How the script talks to Resolve

The check runs in the background on the first look at the tab. A run
that ends by building a project should not find out at the end that
Resolve was never running.

Reports say that external scripting has been kept to the Studio edition
since version 19.1. There is no official statement. This is why the
program measures whether scripting answers instead of going by the
edition it finds.

The word "multicam" does not appear once in the README that comes with
Resolve's scripting interface. The words "transition", "dissolve" and
"fade" do not appear once in that documentation either. The dissolve is
therefore pulled by hand. The intro and outro clips lie over the
content instead of beside it, so that one drag on the upper corner is
enough.

## How the timelines are built

The cameras started at different times. Which part of each camera file
lands in the cut therefore comes from the measured offset, not from the
timecode.

A timeline destined to become a multicam clip has to look like this:
full length, uncut, one camera per video track. Each camera sits at its
measured place.

Conversion turns every audio track into an angle. The Full-Mix and the
camera microphone would become angles without picture, and SmartSwitch
would hear every speaker on every camera. The surplus audio is
therefore deleted after the insert.

Remote grades glue the **Clip** level together with the source file, so
a single cut can no longer be corrected on its own. The colour group
does the same work without giving up the clip level. The script sets
local versions on every run because a project from an earlier run would
otherwise still have remote grades on.

## Which frame rate counts where

Four rates have to be kept apart, and confusing two of them put every
shot of a mixed-rate cut in the wrong place -- twice, on two different
pairs.

`timeline_frame_rate` says what the timeline runs at: the highest `fps`
among the videos, with intro and outro dropped by path and a file set to
"ignore this video" never in the list to begin with. Where nothing is
left the reference clip decides, as before. It stands in for
`ref_clip[1]["fps"]` in `write_handover`, in `write_cut_list` and in the
timecode of the stored tracks. The reference clip still decides the time
axis, and the log still names it as the longest running time -- that is
a different question from the rate. Upwards Resolve repeats frames,
downwards it throws every fifth one away, so taking the highest loses no
picture.

`resolve_timeline_rate` puts that answer onto a rate Resolve offers a
timeline for. `RESOLVE_FRAME_RATES` holds the nineteen it has, read off
Resolve's own list, and nothing else is a project rate: measured on
21.0.4.5, 15 and 240 are refused, 16 and 120 are the two ends. So the
next rate **up** is taken, never the nearest -- upwards costs repeated
frames, downwards thrown-away ones -- and above 120 there is nothing
higher, which is the one place it goes down instead.

`known_frame_rate` answers which of those nineteen a reading means, or
`None`. The fence is relative (`FRAME_RATE_TOLERANCE`, one per cent),
because one frame at 120 is a fifth of one at 24: a container names its
rate to within a millionth, an averaged reading strays a few
ten-thousandths, and the nearest foreign rate lies four times further
out than that.

`own_frame_rate` is the rate a file's own frames are counted at, and it
is not the same question. Where the reading means one of Resolve's
rates, that is the answer; where it means none of them, **the reading
itself is**, and it is not moved to the nearest. A 15 fps file counts
fifteen frames to the second in its length, its timecode and its cut.
Rounding a foreign rate here was the fault behind the whole change: one
function answered both questions, so a 15 file had its timecode counted
at 16 frames to the second. `frames_to_timecode` and `timecode_to_frames`
go through `own_frame_rate` for that reason.

Nothing is refused for its rate. The file is read, placed and cut like
any other; only the timeline gets a rate Resolve has. Measured on
21.0.4.5, a 15 file in a 30 timeline sits within half a source frame at
every shot, with no gaps and the length exact; alone it gets a 16
timeline and keeps its length to the millisecond. `video_summary` puts
the note on the **Video** line of the file list where
`known_frame_rate` is `None`, and the time-base step says the same at
the file while it reads it.

`startFrame` and `endFrame` of an appended clip are frames of the source
file, counted at that file's own rate. Measured against Resolve
21.0.4.5: three clips at 24, 25 and 30 frames, each given
`startFrame=240`, answered `GetSourceStartTime` with 10.000, 9.600 and
8.000 seconds. `write_handover` therefore writes an `fps` into every
camera entry of the handover file, and `build_cut_timeline` carries one
rate per camera and counts the in point at that rate. Against the
timeline's rate a 24 camera in a 30 timeline showed a quarter of the
elapsed time too late, and its shots came out a quarter too long.
Measured over the round trip -- the cut list read back out of Resolve
and held against what went in -- six shots gave sixteen complaints
before and none after. The head cut of the Full-Mix runs at the rate of
the camera file it comes from for the same reason. The `offset` of a
camera goes the same way: `camera_place` reads the timecode of that
file, so it is handed that file's rate and no longer the reference
clip's.

`frames_of_the_file` turns a length in timeline frames into source
frames: the most that fit and never one more. Not every length is
reachable, because a 24 clip covers timeline frames of a 30 timeline in
steps of 1.25, so about one cut in five ends one timeline frame short.
The overrun was measured too and dropped: it closes that frame but moves
every following shot, and the moves accumulate over an hour into
seconds. One frame is the floor -- no picture at all is worse than one
frame too many.

`recordFrame` is the one number that really counts in timeline frames.
`build_camera_timeline` sends nothing else, which is why the multicam
timeline was right the whole time: measured, all three cameras placed at
+3.000 s kept their true running time in a 30 timeline.

The written camera files stay out of all of it. `write_camera_file`
copies the picture and takes the timecode from `info["fps"]`, the rate
of that file. Measured with ffprobe over eighteen written files: the
frame rate is the source's in every one, and where the head cut is not a
whole second the frame part of the timecode is the one that file's own
rate gives.

## German and English: what lives where

The whole source is English: names, messages, comments. German exists
only as translation strings, in `language/de.po` in the program's own
folder, keyed by the English text. That file is PO and holds no code at
all: one entry per message, `msgid` the English wording the program is
written in and `msgstr` what is said instead, so that a translator can
work in it without reading the program -- 1 531 entries, counted
5.9.2026.

`texts_of_language("de")` -- the project's own reader in
`language/__init__.py`, not `gettext` and not `polib`, and nothing is
compiled -- reads it out of the folder the program sits in, not by
import name: a program loaded from an absolute path, which is how every
test loads it, leaves its own folder off the search path.
What comes back is put into `CATALOGUE`, keyed by the language code.
`T()` looks a text up there; a missing entry shows English rather than
a gap.

`--lang de` or `--lang en` fixes the language of a run. Without the
switch `system_locale()` decides, from `LANGUAGE`, `LC_ALL`,
`LC_MESSAGES`, `LANG`, on macOS `AppleLocale`, on Windows
`GetUserDefaultLocaleName`. A run speaks one language. `--help` is the
exception: the help stays English, because those texts do not go
through `T()`.

Nothing a machine reads is translated: file names, folder names, track
names, the keys in the project and handover files, the column heads of
the CSV files. The keys are English (`speakers`, `cameras`, `length_s`,
`start_s`, `timeline`, `offset`), and the files carry `"format": 3`.
`format_complaint()` turns down anything older instead of reading a new
meaning into old names.

Numbers are split. On screen they follow the language (25,000 against
25.000, 1.2 s against 1,2 s; `group_text`, `decimal_text`), into files
they always go English. The CSV files are comma separated with a full
stop as the decimal mark, in every language: two runs have to stay
comparable.

A further language is one file and one line: copy `language/de.po` to a
name carrying the new two-letter code, translate every `msgstr` and
leave every `msgid` as it stands -- it is the key -- and name that code
where the catalogue is filled at the end of the program --
`CATALOGUE["xx"] = texts_of_language("xx")`. `--lang` offers it
afterwards, and a system set to it picks it up by itself.

**A language file may be incomplete, and it still works.** Measured
4.9.2026: an entry that is not there falls back to the English source
text, and a language stands in `languages()` by nothing more than
having an entry in `CATALOGUE`. So a file with a fifth of its lines
translated is a usable language and can be filled in later; nothing
has to be finished before it is added.

The test suite is English throughout. `source_limits_hold_test.py` watches the
source: German comments, narrating comments, text lines over 79
characters, over-long blocks, docstring headings without a full stop.
Every counter is at zero.
