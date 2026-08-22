# Speaker statistics, camera cut, EDL

*Auf Deutsch: [camera-cut.de.md](camera-cut.de.md). Back to the [contents](README.md).*

## Speaker statistics, camera cut, EDL

With multitrack the script knows who spoke when -- from auphonic.com, or
measured here (see below). Out of that it builds a camera cut: whoever speaks
alone gets their camera, with a lead-in; in silence the wide shot. Where a
shot stands for a long time, the wide shot is dropped into a speech pause.

**When several speak at once**, a camera showing exactly those speakers
wins -- one on both hosts, say; in conversation a two-shot beats the wide
shot. If none fits exactly, the smallest camera carrying all the speakers
does. Only
where no camera covers them does the wide shot take over. Who is on which
camera comes from the assignment: two speakers on one camera means it shows
both.

The output folder gets `_speakers.csv`, `_speakers.edl`, `_cameracut.csv`
and `_cameracut.edl`. The heads are
`Speaker,Start TC,End TC,Time from start,Duration s` and
`Shot,Camera,Start TC,End TC,Duration s`, the EDLs are titled `Speakers` and
`Camera cut`. Auphonic's own `<Production>_statistics.json` lies with
everything else from the service in `auphonic-tracks/`.

### The knobs

| Switch | Default | What for |
|---|---|---|
| `--min-edit-duration` | 3 s | this long a shot stands at least |
| `--edit-change-delay` | 0.3 s | this much later than the sound the picture cuts |
| `--wide-after` | 45 s | from this hold time on, a short look at the wide shot |
| `--wide-length` | 2.5 s | how long that wide shot holds at most |
| `--wide-min` | 1.5 s | and how short it never gets -- if need be it runs into the first words |
| `--wide-flow` | 6 s | how long it holds when the cut falls mid-speech |
| `--wide-latest` | 120 s | upper limit for one camera in one piece |
| `--no-wide-edges` | off | otherwise beginning and end stay wide |

`--min-edit-duration` also takes care of short interjections ("mhm", "yes
exactly"): too brief a look at the other camera falls back into the shot
before it.

In multitrack every value can be typed into the interface, in the box "Camera
cut" on tab **3. Resolve cut** -- the rhythm on the left, the wide shot on the
right, below it the tick "Wide shot for greeting at the start and farewell at
the end" (the counterpart to `--no-wide-edges`).

### Preview and speaker statistics

On the right the box "Camera cut -- preview" carries the length in its title
and one line of numbers below it: shots, median hold time, shortest shot,
longest a camera holds, and the speech time split into own camera, wide shot
and a camera without the speaker. The last figure stands in the warning
colour.

On the left, under the knobs, the box "Speaker": per speaker the speech time,
the share, the number of blocks and their average length, plus a row of
silence. Where two speak at once the time counts twice, for silence it does
not, so the rows add up to more than the running time. The heading names the
source -- "Speaker statistics from auphonic.com" or "Speakers, self-measured
from the tracks".

Both come out of the handover file of the last run, recomputed on every change
and always for the chosen window; nothing is written or uploaded. Without
statistics the box says so and offers the button "Measure speakers now"; where
the computation fails, the reason stands in its place. Results that turn up
later -- in `Ergebnis/auphonic-tracks/` too -- start the preview by
themselves.

### Cut band and legend

In the preview box, under the player, sits the **cut band**, in place of the
position rail: the computed cut over the full length, one bar per shot in the
colour of its camera, and a scale whose ticks are as far apart as the
length allows: minutes over the whole thing, seconds once zoomed in. That
shows the rhythm without rendering anything. Hovering names camera, from-to and
duration; clicking sets the spot for the player. Below it the **legend**: per
camera a dot of colour and `62 × Candidate  77 %  (48:19 min)`.

These are the colours of the clips in Resolve, with one exception. The wide
shot gets "Tan" there, a warm sand brown that on a dark background sits too
close to the orange of the second camera (34.9 CIE76); shown instead is a
pale sage, at least 52.9 from every speaker colour. In Resolve the clip is
still called Tan, so that graded projects do not shift. The same way Brown,
Chocolate, Cocoa, Navy and Teal are lightened on dark, Beige darkened on
light.

The band can be zoomed. **+** shows half as much around the current
position, **−** twice as much, and the third button the whole length
again; the mouse wheel over the band does the same, as do the keys plus,
minus and 0. Zoomed in, it can be seen and heard whether a cut sits in a
pause or in the middle of a word. While playing, the section follows the
position, so it does not run out of the picture.

### The preview players

Two players show the material, and both pick their file themselves.

**On tab 2. Assignment & time window** the order is:

1. a file **containing In point and Out point**, or the jump buttons go nowhere
2. failing that, one with at least one of the boundaries
3. among equals the camera with **no speaker** assigned, because the wide
   shot shows the most
4. among those the longest
5. never a file set to "ignore this video", never intro or outro

Which file was last in the player is kept in the project file and taken
again -- as long as it covers the boundaries as well as the best
alternative. Whether a boundary lies in a file cannot be decided without a
timecode or a measured time axis; until then nothing is claimed, and once
the axis is there the player looks again. **to In point** and
**to Out point** fetch their file themselves; where there is none at all, a
line says why nothing happened.

With **hear assigned audio** the picture runs with the sound belonging to that
camera: the **processed track** from auphonic.com (`final_<Name>_<TC>.wav`),
at -16 LUFS and with a BWF timecode; failing that the **raw recording** of the
assigned speaker; with no speaker assigned -- the wide shot -- the
**Full-Mix**, if it is there. Raw recordings sit 16 to 36 dB below the
processed sound, and the interface cannot make them louder. The tooltip says
what is running and in which version.

**On tab 3. Resolve cut** the player in the preview box always shows
something: where there is a cut it plays the cut and switches camera at every
edge, otherwise the file with no speaker assigned. Nothing is rendered. The
sound comes from one file throughout, preferably the **Full-Mix**, which is at
delivery level and goes into the cut timeline too. Where it is not there yet,
the camera file carrying the mix as its first audio track is used -- the same
choice as for angle 1 of the multicam clip, and noticeably quieter.

`start_s` is the wall clock time at which programme time is zero: the
earliest audio start actually known, own timecode or measured position --
the speaker segments count from the start of the material that went to
auphonic.com. Failing that the earliest camera timecode; failing that
nothing, because nothing is guessed. In point and Out point move the zero
point along. The spot in each camera file is programme time minus offset,
the same offset the cut timeline is built with.

Seeking is a request in Qt, not a command, so every spot is set again until it
holds; how often, and for how long, is in [Inside the script](internals.md).
`VPM_PLAYER_DEBUG=1` puts clock, position and wanted value of all three
players under the picture, and every attempt on the console.

### Speakers without Auphonic

With `--without-auphonic` the run stays local, and who speaks when is measured
from the tracks; in the log that section is headed `SPEAKERS -- MEASURED
HERE`. Each track is cut into blocks of 100 milliseconds and measured against
its own noise floor, the quietest fifth of its blocks; 10 dB above that counts
as speech, because a fixed threshold is no good with recorders turned up to
different degrees. Pauses under 0.35 seconds are not speaker changes, passages
under 0.4 seconds do not count.

Before that the **bleed is taken out of the measurement**, not out of the
audio: where exactly one person speaks -- that one at most 10 dB below their
own speech level, the others at least 6 dB below theirs -- the script measures
how loudly that voice arrives in the other microphones and computes each
speaker's own share back out of every track. The coupling is measured, not
assumed, so it also works with microphones standing closer than the 3:1 rule
wants; for a pair without at least three such moments, nothing is subtracted.
Where it cannot be undone -- microphones side by side, tracks too much alike
-- the levels stay as measured, and the log says why and names the worst pair.
Without the step every microphone reports speech at once, no camera shows
exactly those speakers, and the cut stays on the wide shot for the whole
recording.

Down to 5 dB of separation the detection is exact, well below the 9.5 dB the
3:1 rule asks for; the measurements behind that number are in
[Inside the script](internals.md).

The log says how strong the bleed was, and under it the speech time and the
number of passages per speaker. Where nothing was audible, there is no camera
cut.

The button **Measure speakers now** does the same in the interface, before the
first run: coarser than auphonic.com, but enough to set the cut up. As soon as
the statistics are there they take precedence, and the heading above the table
says which source applies.

### One camera for everybody

With several speakers on one camera the cut has nothing to switch
between, and the whole recording would be a single shot. It is cut
anyway, at the change of speaker: every shot comes from the same clip and
carries the name of whoever is talking. Nothing about the picture changes
-- but Resolve gets a track already separated at the right places, and
there each piece can be grouped, coloured and zoomed into, so the wide
shot becomes the speaker.

The cut list says so too: `_cameracut.csv` has a Speaker column, and
where one camera shows everybody the EDL carries the speaker name.

### Project file

`videopodcast-magic_<Production>.json` in the output folder. It holds
everything set by hand that cannot be guessed again: the file list, the
production name and the output folder, the time window, every value of the
camera cut, who belongs to which camera, the Auphonic preset, the stereo ticks
and the measured position of every file. The API key is **not** in there.

On opening, the format of the file is checked; a file in another format is
refused. Older project files can no longer be opened.

The file appears as soon as the time axis is measured -- then still next to
the material, because there is no output folder yet; where one is chosen
later, or the production renamed, **it moves along**. There is always exactly
one, or you open the wrong state. "Open project ..." at the top left brings it
back; point at the wrong file and `videopodcast-magic*.json` in the same
folder is searched. Beside it lies the handover file
`<Production>_resolve.json` -- the preview computes from it, and the Resolve
part builds from it.

### How the wide shot is placed

A wide shot does not come by the clock. What is looked for is the spot where a
cut is unobtrusive anyway: a long speech pause, if possible shortly before
someone else comes in, and not too far from where the wide shot was wanted.
The rhythm follows the sound and not a beat, and it stays reproducible:
nothing is rolled for.

`--wide-latest` is the rip cord: where no pause turns up, the cut happens
anyway. It then falls mid-speech, so the wide shot holds for `--wide-flow`
instead of `--wide-length`; where the room to the next cut is short, it is
brought forward rather than shortened.

## Metrics and colour comparison

At the end of every run `<Production>_metrics.csv` appears. The log is
overwritten by the next run, this file is not -- over a few months it shows
what a single run hides: a recorder going slow, a camera looking increasingly
unlike the rest, bleed rising with a new setup.

It is built as `Area,Metric,Before,After,Unit` -- comma separated, with a full
stop as the decimal mark, and `Area` and `Metric` in English whatever the
language, so two runs stay comparable. Before is the track as it came in,
after as it goes out, both measured the same way.

On a German system the comma costs one step: Excel opens a file by double
click with the semicolon and puts the whole row in one column. The way in
is `Data > From Text/CSV`, where separator and the language of the numbers
are set by hand. LibreOffice asks for both by itself.

| Area | What is in it |
|---|---|
| `Audio <Name>` | loudness, peak, loudness range, clock drift in ppm, offset and residual |
| `Audio` | gain on every track, loudness target |
| `Cut` | shots, median, shortest, longest, share per camera |
| `Speech time` | seconds per speaker |
| `Colour <Name>` | brightness per camera, distance to the mean, colour position |

**The colour comparison** measures brightness and colour position at five
spots in each camera file, compared not against a target but against the mean
of all cameras: what counts is the distance *between* the cameras, because
that is what shows when switching. From about twelve steps a warning comes
with it. Both measurements together take a few minutes on long recordings
-- the loudness measurement runs through each track twice. `--no-metrics`
leaves it out.
