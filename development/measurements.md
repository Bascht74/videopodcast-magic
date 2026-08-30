# What was measured

For `videopodcast-magic.py`. Each entry says where a number comes from:
what was measured, how, and what came out. Not part of the manual and
English only: this is for whoever changes the program, not for whoever
uses it.

How the program is built is in [Inside the script](internals.md).

---

## How long the speech recognition takes

macOS 26 brings the recognition with it: one hour of audio in a good
20 seconds, 0 MB to fetch. It needs the Command Line Developer Tools.
Otherwise faster-whisper with `large-v3-turbo`: 144 MB of packages and
a model of 1.5 GB. Without an NVIDIA graphics card it runs on the
processor. On a Mac that is not quite three times faster than the
recording is long. On an ordinary Windows machine it is 25 to 70
minutes for an episode of 72 minutes.

The recognition runs in a strand of its own beside the cameras. On the
Mac it costs 22 s per hour.

## What the word times are worth

Both recognisers report the beginning of a word about a tenth of a
second late, measured against the audio itself.

macOS almost never puts a gap between two words: 98 % of the word
pairs stand without a space, across sentence boundaries as well. Its
time grid is 60 ms. Whisper has room there.

## What the recognition gets wrong

Over one measured hour: the same recording over the mix 96 %
agreement, over the raw recording 75 %.

Invented words in the silence are a known fault of Whisper. One five
minute setup pause held 21 of them. The program switches the voice
activity detection on, and with it they are gone.

Names and anglicisms are the errors that remain, on both paths and
evenly spread over the length.

One hour of one recording lies behind these three figures. Whether
they hold for another room, other microphones and other voices was not
measured.

## How well the speakers are separated

Measured on 45,473 words over two whole interviews: 98.7 % right.
77 % of the errors lie in real overlap or within half a second of a
change of speaker. Real mix-ups in a quiet passage: 0.28 %. The raw
recording separates as well as the processed mix.

Widening the edges by 0.2 s and closing gaps under 0.25 s brings
4.2 points. At 0.5 s it tips over.

A given speaker count improves the recognition and quadruples the
picture time on the wrong person. The program passes one only when
somebody sets it by hand.

Two interviews out of one production. How many people spoke, in which
room and on which microphones is not part of the figure. The 98.7 %
therefore carries no further than material recorded the same way.

## What the separation costs

About 28 times real time on the graphics unit, one run at a time. Two
in parallel bring 12 % throughput, cost 1.75 times the wait for the
first result and 4.5 GB per process.

Different kinds of work do not slow each other down (0 %). From four
processors on, everything runs together.

The setup fetches about 218 MB into an environment of its own. The
model itself lies with the program.

All of this comes from one machine, and the machine is not named here.
What carries over are the ratios, not the absolute times: the gain
from running two, the memory per process.

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

Down to 5 dB the gate is exact, well below the 9.5 dB the 3:1 rule
asks for. Below that it does not fail all at once. At 4 dB no moment is
left in which exactly one person speaks, so most of the coupling can no
longer be measured. The separation then runs on half a model and is no
longer reliable. The log says how many of the pairs could be measured
at all.

Without the gate the failure below 6 dB is not "everybody speaks" but
"nobody speaks". Every track is loud the whole time, the noise floor
rises with it, and nothing exceeds the threshold any more.

## What the channel pairing was measured on

Built cases, with the delay put in on purpose:

| Case | at zero delay | read as |
| --- | --- | --- |
| X-Y, coincident | 1.00 | one pair |
| ORTF, 17 cm | 1.00 | one pair |
| pair at 30 cm | 1.00 | one pair |
| mono on both sides | 1.00 | one track |
| two clip-ons, 0.6 m | 0.16 | two microphones |
| two clip-ons, 1.2 m | 0.10 | two microphones |
| two clip-ons, 2.0 m | 0.10 | two microphones |

The absolute floor of -70 dBFS comes from a measurement as well: two
excerpts of one 32 channel recording judged the same pairs
differently. At -85 dBFS it was dither being compared.

On one mixer recording the first five minute block was the soundcheck
and gave one used channel pair. The second was the recording and gave
ten tracks. The program therefore judges the recording as a whole.

Measured on one 92 MB block of 32 channels: 2.0 s to read it in one
pass, 22.9 s to read it once per channel. The levels and the pairs
come out the same. A pair of 1.8 GB blocks drops from about fifteen
minutes to about ninety seconds.

ffmpeg's own channel conversion follows the equal-power law, measured
on a signal at -24.08 dBFS. One channel to two comes out at -27.09,
two channels to one at -21.07. Three decibels one way or the other,
inaudible in a single listen and wrong in every meter.

## Where the envelope alignment stops

Measured on one phone recording of monitor speakers against the
finished Logic mix of the same music. That is music with singing, not
a podcast, and so exactly what the envelope way was never built for.

`align_envelopes` finds nothing: a quality of 0.13 over the whole and
-0.18 in the window, against a threshold of `WEAK_MATCH = 0.05`. Below
that threshold nothing counts as a find. Material that belongs
together sits at 0.5 to 0.9 on the same figure.

Envelope cross-correlation asks where two recordings are loud at the
same time. For that something has to get loud and quiet again. A mixed
and limited song holds the same loudness for minutes, so there is
nothing to compare.

`phase_align` (`GCC-PHAT`) throws the loudness away and keeps only the
phase, which is what a re-recording through a room survives. First
try, with nothing to go on: offset **569.201 s = 9:29**, drift
**-29.1 ppm**. The video ends 11 s before the end of the audio.
Checked against what the recording was expected to hold: 8 to 11
minutes, with the video lying towards the end of the audio. Both fit,
and it is the only independent check there was: the material carried
no mark of its own to measure against.

The sharpness came out at 28.7 against 26.5 for the next best peak.
`PHASE_SHARP_ENOUGH = 8.0` comes from that one piece of material, so
it is a floor and not a measured threshold. The log prints the number,
so anybody can see how close it was.

The 12 ms left over are not an error. It is about 4 m from the
speakers to the phone, and sound needs 4 m / 343 m/s = 11.7 ms for
that. Whoever takes those 12 ms out moves the video wrong by the
travel time through the room.

`looks_like_music()` decides none of this. Do not read it as if it
did. Settling it on the share of the syllable band, 2 to 8 Hz under
0.20, did not separate cleanly in the runs so far. A finished mix
landed at 26 %, speech at 31 to 32 %. The value goes in the log and
nowhere else.

One recording, one room, one phone. The offset is confirmed, the way
to it is not. Whether the phase way also beats the envelope on speech
has never been tried. It runs as a fallback, after the envelope has
already given up.

## What one bad point does to the drift

Measured in `tests/time_bad_point_dropped_test.py`, 19 checks, on a built series of
points: the true answer is known, so the error is known exactly too.

A single wrong point **at the start** moves the offset by 188.9 ms and
turns the drift from -64.07 ppm into +10.00 ppm. What changes is the
sign, not only the size. "The audio runs away" becomes "the video runs
away", and a correction made on that pulls the wrong way.

With `without_outliers()` the offset stays at 0.0 ms and the drift at
10.00 ppm, which is the true answer. What it does:

* The anchor is the median, not the line. The line is already bent,
  and measuring against it makes the good points look like the odd
  ones out.
* The scatter is the median absolute deviation, scaled by 1.4826 so
  that it means the same as a standard deviation on ordinary data.
* The limit is `max(3 * MAD, 20 ms)` (`OUTLIER_SIGMA`,
  `OUTLIER_FLOOR_S`). The 20 ms are a floor and not a measured
  threshold: four times HOP, which is as fine as the envelope resolves
  at all. Without it a very tight set of points throws away its own
  scatter.
* Six rounds (`OUTLIER_ROUNDS`), and never below three points. Two
  points fit a line perfectly, which would turn a broken measurement
  into a confident one.
* The log names every point dropped, with its time and how far out it
  lay. A run that cleans up in silence cannot be checked afterwards.

The edge is where it hurts, because a fitted line tips about its
centre of gravity. A point in the middle sits almost on the pivot and
moves nothing; a point at the edge has the longest lever. The test
tries all three places on their own: start, middle, end. The start is
the worst of them, because that is where an opening jingle lies.

The series is built, not recorded. This says what the cleaning does to
a known fault, not how often such a fault turns up in crosstalk points
that were really measured.

## What the loudness was measured at

| File | measured |
|---|---|
| mix on one channel | -29.4 LUFS |
| the same mix on both channels | -26.3 LUFS |
| after normalising, two channels | -16.0 LUFS |

Leaving it to the editing program would be an invisible trap. A mono
track panned to the middle of a stereo bus lands at 0, -3, -4.5 or
-6 dB, depending on the pan law.

## Clipping does not depend on the bit depth

The claim was that 24 bit material behaves differently at full scale
from 16 bit: more headroom, a different kind of clipping. It was
measured, and the claim was wrong.

`ffmpeg ... -af astats` over the same clipped source, written out
three times, once per format. The source is the same in all three, so
a difference can only be down to the format.

| Format | Flat factor | Peak count | Peak |
|---|---|---|---|
| 16 bit integer | 31.15 | 63,520 | 0.00 dBFS |
| 24 bit integer | 31.15 | 63,520 | 0.00 dBFS |
| **32 bit float** | 0 | none | **+5.94 dBFS** |

The first two rows are not close, they are identical. The same flat
factor to two decimal places, the same 63,520 samples sitting on the
maximum, the same peak.

The line runs between integer and float, not between 16 and 24 bit. An
integer format cannot go past full scale. There is a wall there, and
whatever stood above it was cut off as the file was written. Float
can, and 0 dBFS is only a mark on its scale. The +5.94 dBFS of the
third row are still in the file and can be pulled down afterwards.

So the clipping warning may only fire on integer formats. On float it
would point at material that nothing has happened to, and a warning
that does that teaches people to skip warnings.

Not measured: whether 24 bit material that a converter limited before
writing is still recognisable as clipped at all. A limiter leaves
rounded tops rather than flat ones, and neither figure in the table
would see them. Nor whether the recordings this program is aimed at
ever reach 0 dBFS in the first place. That decides whether the warning
has anything to fire on.

## What the camera cut was measured at

* **Merging a short shot forward instead of backward** -- the wrong
  picture time falls from 326 s to 99 s over four runs. With the truth
  as input it falls from 42 s to 7 s.
* **The heap of leftovers** -- over six sources 5 of 5 found, no false
  alarm. The largest heap holds 219 s.
* **Restlessness** -- the wrong picture time falls from 77 s to 49 s,
  the longest wrong stretch from 8.0 s to 2.3 s. On correct recognition
  it fires 0.0 s and 3.3 s.
* **Where the wide shot comes in** -- both directions; forward only
  halves the hit rate. From +/-4 s on, 100 % lie on punctuation. The
  dip in the audio hits the real pause in speech 97 to 99 %, the word
  boundary of the recognition 42 to 46 %.
* **Where the wide shot goes out** -- median 9.0 s, 100 % in the window
  5 to 15 s. No wide shot ends in the middle of a sentence.
* **The reaction cut** -- 25 to 40 cases per interview. 1 to 3 % of the
  picture time change owner, and no new cuts arise.

These are counts from interview recordings of one kind, and the
defaults come from them. Nothing here was measured on a different sort
of programme.

## The clip colours

The colours are sorted by distinguishability, so the first two lie as
far apart as possible. The wide shot gets "Tan" from that list, a warm
sand brown. On a dark background it sits too close to the orange of
the second camera (34.9 CIE76). The program shows a pale sage instead,
at least 52.9 from every speaker colour. In Resolve the clip is still
called Tan, so that graded projects do not shift.

## What the opening wide shot was measured on

A rebuilt case: the same 92 second opening, once as one block and once
chopped into 14 pieces. Before, 100.3 s against 5.3 s; afterwards,
100.3 s against 100.3 s. A single wrongly labelled block in it: before
5.3 s, afterwards 24.6 s.

A long, cleanly wrongly labelled stretch in the middle of the opening
still ends it too early. The program pulls blocks together by speaker,
and whoever holds such a stretch alone counts as the one taking over.
This is not measured against the real interviews.

## How big the PySide6 download really is

The source said 100 MB, in a comment justifying why pip's output stays
on screen during the install. Measured on 24.8.2026 from the wheel
sizes pypi.org reports for PySide6 6.11.2. The four wheels pip
actually fetches, per platform:

| platform | download | of which addons |
| --- | ---: | ---: |
| Windows amd64 | 246.9 MB | 168.2 MB |
| Linux x86_64 | 256.0 MB | 175.1 MB |
| macOS universal2 | 443.9 MB | 332.0 MB |

macOS is the outlier because its wheel is `universal2`: it carries both
processor architectures in one file. A second way checked the macOS
figure: fetching the wheels with `pip download PySide6` on this
machine and adding up the bytes. That gives 443,896,377, the same
number. Unpacked it is 1.2 GiB in `site-packages/PySide6`, plus
1.4 MB for `shiboken6`.

The old number was out by a factor of two to four, depending on the
platform. It matters only for the one sentence it was written for:
whether a silent install looks like a hang. At 6 MB per second, even
the smallest of the three is forty seconds of nothing happening.

**A unit trap, and it caught this measurement first time round.** `du`
and `ls -lh` report MiB and call them M; pypi.org and every download
figure people quote are MB. The macOS download is 423.3 MiB and
443.9 MB, and those are the same number of bytes. Written as "423 MB"
it contradicted the manual, which said 440. A size quoted for somebody
comparing it against a download is MB.

**What was not measured:** how much of the addons the program actually
needs. It imports QtWidgets, QtGui, QtCore, QtMultimedia and
QtMultimediaWidgets. Whether those live in essentials alone was not
checked. If they do, the download would be about a third of the
figures above. The unpacked size was measured on macOS only.

## Why one recording does not become four tracks

Could the program build one audio track per speaker out of a single
recording -- each speaker's own segments kept, the rest of the track
silenced -- so that one recording could be run as an Auphonic
Multitrack production? Measured on 24 and 25.8.2026 on one real
interview. The answer is no.

The material is one room recording from a Zoom,
`Gesamtaudio-016_Zoom.wav`: 5216.71 s = 1:26:56, 48 kHz, stereo, one
signal that holds everybody. The separation is the cached pyannote run,
so these are the numbers the program itself would cut the tracks from.

| what | measured |
|---|---|
| labels | 4, over 1257 raw segments |
| the loudest of them | 68.0 % of the speaking time, 736 segments |
| the quietest | 219 s in 181 segments, mean 1.21 s |
| two at once, raw | 98.0 s = 1.88 % of the recording, 189 events |
| two at once, polished | 224.5 s = 4.30 % |
| three at once | never |
| nobody speaking | 12.15 % of the recording |
| four gated tracks | 652 audible blocks, 1304 fade edges |
| the same, unpolished | 2514 edges |

Polished is the program's own `speaker_segments_polish`: edges widened
by `SPEAKER_MARGIN_S` = 0.2 s, gaps up to `SPEAKER_GAP_S` = 0.25 s
closed. It more than doubles the overlap. That is no fault of the step
-- a picture cut wants the wider edge -- but it is the shape the audio
tracks would inherit. Per speaker, the quiet participants have 19 to
32 % of their own speaking time overlapped by somebody else.

* **De-Bleed has nothing to correlate.** Auphonic's crosstalk removal
  looks for the same signal on two tracks while somebody is speaking.
  In synthesised tracks exactly one track is non-zero at any instant,
  so there is no correlation to find. In the 1.88 to 4.30 % where two
  tracks are non-zero together they are bit-identical at zero delay,
  which is the same sample twice and not bleed.
* **The boundaries are not cut points.** Only 34.3 % of the 2501
  segment boundaries fall into a real pause in the speech, and the
  median distance from a boundary to the nearest pause is 0.20 s. The
  dip in the audio hits a real pause 97 to 99 % on the same material.
  `docs/notes/pyannote4.md` says it already: whoever takes a segment
  boundary for a cut point has the number against him. A track that
  starts in the middle of a word sounds worse than no track, and there
  would be 1304 places to do it.
* **The fourth label is not a person.** 219 s in 181 segments, mean
  1.21 s: 4.2 % of the recording, 4.7 % of the speaking time added up
  over the four labels. The program's own `stray_labels` rule calls
  that a heap and not a speaker. The smallest voice that is a person
  reaches 57.3 % precision.
* **The project refused this input once already, for this reason.**
  `docs/notes/debleed_and_cleanup.md` says the Zoom room track "does
  not belong in the multitrack production as a track -- it contains
  every speaker, and Remove Mic Bleed then cannot tell what belongs to
  whom". Building four tracks out of it does not change what is in it.
* **The cheaper way is already there.** A singletrack production of the
  same recording gets the same Auphonic algorithms -- leveler, denoise,
  loudness -- over the whole file, for a quarter of the cost, and cuts
  nothing.

The cost of the way not taken: about 87 minutes of reading and writing
per track, four times about 1 GB of WAV, to arrive at four tracks that
De-Bleed cannot use.

**What the same numbers do support.** The separation is good enough to
say who is speaking and where the speaker changes, which is what the
camera cut has always used it for and what the figures further up were
measured for. It is only not good enough to be used as a knife on the
audio itself. A tenth of a second out moves a picture cut, and nobody
sees it; the same tenth of a second cuts a word in half, and everybody
hears it.

Measured are all the counts, times and shares above: they come from the
separation of that one file and can be counted again from the cache.
Extrapolated are the two cost figures, from the size of the file and
the decode rate measured on this machine -- no four tracks were ever
written. One recording, one room, four voices; how the shares fall in
another room was not measured. The first reason does not depend on the
material at all: it follows from tracks that are zero wherever their
person is not speaking, whatever was recorded.

## Two clocks in the timecode, and why they do not reach this machine

Measured on 25.8.2026 against v2.10.1-beta, offscreen, on the real
module.

The program turns seconds into a timecode two ways. `timecode_string`
(line 1084) builds `HH:MM:SS` from `int(seconds)` and only the frames
from the rate; the Resolve side goes through the frame count and the
timecode clock, which at the 1000/1001 rates runs slower than the wall
clock. Measured, path A against path B:

| fps | 1 min | 1 hour | 1.5 hours | difference |
|---|---|---|---|---|
| 25 | identical | identical | identical | 0 |
| 30 | identical | identical | identical | 0 |
| 29.97 | 00:01:00:00 / 00:00:59:28 | 01:00:00:00 / 00:59:56:12 | 01:30:00:00 / 01:29:54:18 | up to 5.4 s |
| 23.976 | -- | 01:00:00:00 / 00:59:56:10 | 01:30:00:00 / 01:29:54:14 | up to 5.4 s |
| 59.94 | -- | 01:00:00:00 / 00:59:56:24 | 01:30:00:00 / 01:29:54:36 | up to 5.4 s |

**It cannot reach Sebastian's material, and not for the reason one
would guess.** His cameras measure 29.9936, 29.9935 and 30.0010 -- none
of them a 1000/1001 rate. `write_cut_list` really does hand the raw
measured rate to `timecode_string`, not the snapped one. But the
seconds field comes out of `int(seconds)` and does not depend on the
rate at all: over 90 minutes at 540000 sample points,
`timecode_string(t, 29.9936)` and `timecode_string(t, 30.0)` differ in
the seconds field **zero times** -- only 33878 single-frame differences
in the frames field, and those do not accumulate. `nearest_known_frame_
rate` answers 30.0 for all three of his rates, and the Resolve handover
writes that, at which the two clocks are one clock.

**Verdict: a tidying job for whoever else uses the program, not a fault
here.** Written down so nobody measures it a third time.

**And the load-bearing warning, measured:** today a timecode survives
every trip through the program -- `timecode_string` to `parse_timecode`
and back, and the handover's `start_tc`, written on one path and read
on the other -- with an error under half a frame at every rate, 29.97
included. It survives **because both directions share the same wrong
assumption.** Changing one direction alone breaks the handover origin,
the displays in the window and `--head`/`--tail`. The scope is 27
`timecode_string` call sites, 20 `parse_timecode` and 17
`file_timecode`, each needing a decision about which clock it sits on.

## Why the Resolve sheet was wider than the window

Measured on 25.8.2026, offscreen, with the Mac font
`.AppleSystemUIFont` forced to 13 px. Offscreen reckons at 96 dpi where
the screen has 72, so every width below comes out about 4 % more
generous than it will be on a real Mac; the heights are exact to the
pixel. **Every width here is a lower bound. On a real Mac each of them
falls out larger.**

| | Sheet | Window needed |
|---|---|---|
| as it was | 1838 px | 1864 px |
| legend hidden (as a yardstick only) | 1283 | 1309 |
| legend wrapping, everything still there | 1283 | 1309 |

The two lower rows carry the answer: they are the same number. Letting
the legend wrap costs the sheet exactly what throwing the legend away
costs it, which is nothing.

Where the 1838 comes from: 744 (cut column) + 16 (gap) + 1058
(preview) + 20 (margin).

The legend line on its own is 1038 px at three cameras -- texts of 340,
316 and 274, three colour squares of 12, three spacers of 14. Those
parts account for 1008 of the 1038; the remaining 30 px were not broken
out. The widest row on the left is "Recognition uncertain" at 693 px:
caption 145 + drop-down 150 + explanatory text 368, which likewise
accounts for 663 of the 693.

**What is not the cause. Each of these was measured, not argued away:**

* The statistics line wraps, and sets a floor of 88 px.
* The fixed minimum widths do not bind. The largest of them is the
  video picture at 320 px.
* The 50:50 split of the two columns is not it either. Set to `0`/`1`
  and measured again at six window widths, **every number came out
  identical**.

And one thing that would be worse rather than better:
`ScrollBarAlwaysOff` on the horizontal. The content stays 1271 px wide,
so 287 px of it become **unreachable** instead of scrollable.

Sebastian's MacBook is 1512 x 982 points, of which 1512 x 890 are
available. Vertically the same run reported 16 px of air at three
speakers, and a speaker table growing by 30 px per speaker with nothing
holding it, which puts the threshold at four speakers and a window
904 px high.

The width is what was being chased here. One machine, one font size,
three cameras -- and the camera names are what the length of the legend
is made of, so other names give another number. Nothing was measured on
a window that was actually on screen; the offscreen figures are the
floor under the real ones, not the real ones.

## What one speaker with two cameras still cuts

Five minutes, one speaker, two cameras: **15 shots, 7 of them wide.**
The same speaker on one camera: **1 shot.**

So the cut has work to do without a second voice. Two cameras on one
person alternate; one camera on one person is the single long take it
has to be.

What the numbers do not say: this is five minutes of one recording, and
it is a count, not a verdict. That 15 shots exist says nothing about
whether they fall in the right places, and nothing about how the same
rate looks over a full hour.

## What an In point does to the camera offsets

Measured on 25.8.2026 on a written handover: zero point 10.0 s, In
point `00:01:10:00`, so a removed head of 60 s.

Before, the camera offsets `{Wide: -5.0, Anna: 0.0, Bert: 12.5,
Cam4: -33.25}` stayed exactly as they were while the zero point, the
sections and the words all moved by 60. The distance between picture
and sound was then **60.0 s per camera**. Afterwards the offsets are
`{-65.0, -60.0, -47.5, -93.25}` and the distance is **0.0 s**.

The counter-test is a run without an In point: identical before and
after. Whoever sets no window is untouched by the change.

One handover, four cameras, one In point a minute in. The offsets
themselves are not the measurement -- the 60.0 s against 0.0 s is. The
size of the error is the length of the removed head, so a longer head
would show a larger number and mean the same fault.

## What depth the camera sound is unpacked at

Hard-wired in four places, and wrong in both directions. Measured on
25.8.2026 as the size in bytes of the unpacked WAV:

| Source | was written as | is written as | bytes |
|---|---|---|---|
| 24 bit camera | `pcm_s16le` / 16 | `pcm_s24le` / 24 | 576114 -> 864138 |
| 16 bit camera | `pcm_s24le` / 24 | `pcm_s16le` / 16 | 864748 -> 576724 |

Floating point is capped at 24 bit. Ordinary camera sound is AAC and
AAC probes as `sample_fmt fltp`, so unpacking it as float cost a third
more room for nothing that was ever in the file: **384092 bytes as
float against 288102 as 24 bit, for the same two seconds** -- out of a
lossy encoder that never had 32 bits of anything to give.

What these figures are is a check that the depth written is the depth
asked for, and nothing was listened to. They say the copy is as deep as
the original and no deeper. They do not say what a listener would hear
if it were not, and the float row says only what the room costs, not
what the extra bits would have held.

## The window that never came back: two players and one lock

Since the Resolve tab really shows a cut, the window it opens holds
three media players, and each of them decodes pictures in fifteen
threads of its own. The gate test builds six such windows at once, and
that is where it showed: **runs that never ended.** Not slow -- stopped,
in a lock inside Qt, with the machine idle at 1 % of one core.

Measured on 28.8.2026, every figure from the same test on the same
machine, the whole test from start to report:

| what stood in the program | runs that never ended |
|---|---|
| as it came out of the night | **2 of 4** |
| the picture's window made before any player has a file | 1 of 8 |
| ... and a player only stopped while it is running | 1 of 14 |

The two places were read off the stopped process itself, not guessed.
The first stood in `QWidget::createWinId` -- the window for the picture
was being made at the moment the players were starting up. The second
stood in `QMediaPlayer::pause`: one player stops the other when it
starts, and told to stop while it is still starting up, the media
player connects its own objects at that moment and waits for a lock
another thread holds.

Both are now avoided rather than survived: the picture's windows are
made while nothing has a file, and the other player is asked -- on the
Python side, because asking Qt is the thing that blocks -- whether it
is running at all before it is told to stop.

**And it is not the six windows.** The same stack turned up in
`window_stages_named_test`, which opens **one** window and starts a dry run --
stopped for good in `QMediaPlayer::pause`, 15 minutes into a limit of
15. That moved the finding: the load only makes it likelier, and what
it is about is pausing a player that has not started. Every place that
paused without asking now asks first, six of them: on a jump, on the
transport, on the surface that is not showing, and before a new file
is loaded. A player that is not playing has nothing to pause, so
nothing is lost by asking.

**What is left is not repaired.** One run in thirty still stopped, and
the third stack would be a third place: this is six windows at once on
a machine that has fourteen cores, and a build machine has fewer. So
the test builds three at a time now, and whoever is watching sits
outside the child: after 100 seconds without a word the parent kills
it, builds that one case again on its own, and prints a line saying it
did -- a repeat nobody sees is a green that was bought.

**A watchdog inside the child was tried first and does not work.** Not
a timer, which was expected -- the event loop is held. But not a thread
either: where this stops, Qt holds the interpreter's lock while it
waits, so no Python in that process runs at all. A thread whose whole
task was to sleep 100 seconds and print one line never printed it. That
is worth knowing beyond this test: in a window that has stopped, no
part of the program can report it. Only something outside can.

The previous version passed this test in three seconds. That is not
health: its Resolve tab loaded nothing at all, so no player ever
started, and there was nothing for the lock to be held by. The test got
harder because the program got further.

## Where a sound starts counting as speech

`speakers_from_tracks` throws away every block of sound shorter than
0.4 s before anything else looks at it. `find_pauses` reads exactly that
segmentation and `insert_wide_shots` reads `find_pauses`, so a short
"mhm" is not a quiet moment in the cut -- it is not there at all, and
the stretch it sits in reads as silence. The number has stood since the
first version and had never been measured. On 24.8.2026 it was read off
the source and noted as "with an honest 0.1 s, 22 pauses of 1.5 s and
over remain instead of the 64 the 0.4 s reading reports" -- read, not
measured, and on a different interview.

Measured on 29.8.2026 on the Testinterview: one hour and 27 minutes,
three cameras, four voices. The threshold was not changed.

**Two readings, and they are not the same material read twice.** Every
table below says which one it comes from.

* **The voices.** The 1257 speech blocks the separation of this very
  production found, out of its project file. Real speech, and every
  block carries a name. This production ran through the separation, and
  the separation has no such threshold, so nothing here was thrown away
  in the real run: the 0 s row is the cut Sebastian has. The other rows
  are what the same hour becomes when a threshold is put in front of
  it, applied the way `speakers_from_tracks` applies it -- gaps up to
  0.35 s closed first, then what is still shorter thrown away.
* **The tracks.** The sound of the camera files themselves, decoded at
  8000 Hz and put through `speakers_from_tracks` itself. That is the
  path the threshold really stands in.

### How many pauses the threshold invents

On the voices. A pause is false when a block the threshold threw away
lies inside it -- somebody is speaking there.

| threshold | blocks kept | thrown away | speech lost | pauses from 1.5 s | of them false |
|---|---|---|---|---|---|
| 0 s | 822 | 0 | 0.0 s | 69 | 0 |
| 0.05 s | 795 | 27 | 0.6 s | 68 | 8 |
| 0.1 s | 782 | 40 | 1.5 s | 66 | 10 |
| 0.2 s | 770 | 52 | 3.4 s | 66 | 13 |
| 0.3 s | 748 | 74 | 8.9 s | 70 | 21 |
| **0.4 s** | **697** | **125** | **26.9 s** | **74** | **27** |
| 0.6 s | 651 | 171 | 48.2 s | 81 | 38 |
| 1.0 s | 599 | 223 | 90.6 s | 97 | 63 |

**27 of the 74 pauses the program believes in at 0.4 s are not pauses.**
Of the 125 blocks it throws away, 64 fall while somebody else is
speaking -- that is the short answer thrown in, not a false start. Their
median is 0.25 s and the longest is 0.39 s.

On the tracks the same movement is much larger, because the level
detector cuts speech into far more pieces than the separation does:

| threshold | blocks | pauses from 1.5 s |
|---|---|---|
| 0.05 s | 4829 | 199 |
| 0.1 s | 3827 | 305 |
| 0.2 s | 3010 | 412 |
| 0.3 s | 2565 | 489 |
| **0.4 s** | **2275** | **527** |
| 0.6 s | 1558 | 582 |

The direction of the note from 24.8.2026 holds: an honest lower
threshold leaves fewer pauses, not more. The size does not. There it
was two thirds of the pauses; here it is 42 % on the tracks and 11 % on
the voices.

### What it does to the cut

On the voices, with the settings of this production: shortest shot
3.0 s, minimum speaking time 1.5 s, wide shot after 40 s for 5 s, long
monologue alternating. No transcript, so `insert_wide_shots` had only
the pause list to go on -- which is the case the threshold decides.

| threshold | shots | wide shots | put in by the break rule | of those on speech | any wide shot on speech |
|---|---|---|---|---|---|
| 0 s | 338 | 121 | 74 | 0 | 0 |
| 0.05 s | 338 | 123 | 76 | 0 | 8 |
| 0.1 s | 338 | 123 | 76 | 0 | 12 |
| 0.2 s | 338 | 123 | 76 | 0 | 13 |
| 0.3 s | 338 | 124 | 77 | 1 | 17 |
| **0.4 s** | **336** | **125** | **78** | **6** | **22** |
| 0.6 s | 336 | 125 | 78 | 9 | 31 |
| 1.0 s | 342 | 128 | 80 | 15 | 49 |

**This is the number that counts. Six times in this hour the break rule
puts a wide shot on top of somebody who is speaking**, and it does so
because the threshold hid them. It is not a near miss: the wide shot
begins and the sound arrives within a third of a second.

| the wide shot starts | who is speaking there | how long |
|---|---|---|
| 649.2 s | Moderator at 649.8 s | 0.25 s |
| 1782.6 s | Kandidat at 1782.9 s | 0.39 s |
| 2367.4 s | Moderator at 2367.1 s | 0.32 s |
| 3924.8 s | Kandidat at 3925.0 s | 0.35 s |
| 4602.1 s | Moderator at 4606.7 s | 0.30 s |
| 4781.7 s | Kandidat at 4782.0 s | 0.37 s |

At 0.2 s and below the column is empty: **not one inserted wide shot
lands on a thrown-away block any more.** The last column falls more
slowly, because it also counts the long wide shots that stand over
silence anyway; those are a smaller fault, since nothing was cut there
on the strength of a wrong pause.

### What a lower threshold costs

The number of shots does not move. 3.86 to 3.93 shots a minute over
every threshold from 0 s to 1.0 s, and 338 shots at 0.1 s against 336
at 0.4 s. **The cut does not become restless.** The shortest shot of
3.0 s and the minimum speaking time of 1.5 s absorb the extra blocks
before they can reach the picture.

The segmentation does grow, on the tracks, and that is the price. Going
from 0.4 s to 0.2 s adds 32 % more blocks, from 0.2 s to 0.1 s another
27 %, and from 0.1 s to 0.05 s another 26 %. The blocks that come in
last are the marginal ones. Every block was measured against its own
track's noise floor, and the detector lets through what stands 10 dB
above it:

| block length | the hosts' camera | the candidate's camera | the wide camera |
|---|---|---|---|
| 0.1 to 0.2 s | 431 blocks, 11.5 dB | 783 blocks, 10.8 dB | 312 blocks, 11.6 dB |
| 0.2 to 0.4 s | 372 blocks, 12.9 dB | 461 blocks, 12.2 dB | 339 blocks, 13.6 dB |
| 0.4 to 1.0 s | 745 blocks, 13.6 dB | 533 blocks, 12.6 dB | 703 blocks, 14.5 dB |
| over 1.0 s | 794 blocks, 14.4 dB | 200 blocks, 14.1 dB | 874 blocks, 16.6 dB |

The figure is the median level over that track's noise floor. The whole
usable range is small -- on the candidate's camera the speech level
itself stands only 11.0 dB over the floor -- and the band from 0.1 to
0.2 s
sits at the bar: its lowest tenth is at 10.2 dB against a bar of 10.0.
**Below 0.2 s the blocks that come in are the ones that only just got
over the threshold of loudness, so a lower length threshold is buying
them by the thousand.** From 0.4 s down to 0.2 s the blocks that arrive
are 2 to 3 dB over the bar, which is the same place the blocks over
0.4 s sit.

### What was not measured

* **Whether the short blocks are speech.** They were not listened to,
  and the check against the separation could not be made: the
  separation ran on the recorder file and the blocks here come off the
  cameras, and the two time axes could not be brought together. The
  cross-correlation of the two speech indicators has no peak at all --
  the best shift agrees on 4805 blocks of 0.1 s and the best shift
  elsewhere on 4790, a ratio of 1.00. With one voice holding 64.6 % of
  the hour, any shift agrees about that well. So the levels above are
  what stands in place of a truth, and they say how loud a block is,
  not what it is.
* **The tracks path was not read for who speaks.** On this material it
  cannot be: the program's own bleed measurement reports the candidate
  only 1.7 dB quieter in the moderators' camera than in his own, well
  under the 5 dB where the separation starts to slip. Three cameras in
  one room with their built-in microphones are not three tracks. The
  block counts and pause counts from the tracks stand; who those blocks
  belong to does not.
* **With a transcript.** Every run here had no words and no dip levels,
  so the break rule fell back on the pause list. With a transcript the
  break goes to a sentence boundary and the pause list matters less. How
  much less was not measured.
* **Any other recording.** One interview, one room, one set of settings.
  The note from 24.8.2026 came from another interview and gave a much
  larger figure for the same movement, which is a reason to expect the
  size to travel badly even where the direction does not.
* **The built fixtures say nothing here.** `interview` under the
  fixtures folder holds continuous sine tones, not speech: one tone per
  microphone for the whole two minutes. There are no short blocks in it
  to keep or throw away.

### What the numbers say

0.2 s. It takes every inserted wide shot off the back of somebody
speaking (6 to 0), halves the false pauses (27 to 13), and costs 32 %
more blocks on the tracks. Going further down to 0.1 s buys almost
nothing on top of that -- 13 false pauses become 10 -- and costs another
27 % in blocks, all of them from the band that only just clears the
loudness bar. The decision is not made here.

## Whether the questions tell the moderator from the candidate

Sebastian asked on 29.8.2026 whether the recognition could be run over
ordinary tracks, the questions and the speaking time counted, and
"candidate" and "moderator" set from that. This is what came out.
Measured on 29.8.2026 on four episodes out of two productions.

### What there was to measure on

Four recordings hold one track per person: Freiensteinau 1 and 2, and
Steinau 1 and 2. Nothing else does. Two folders that look like more
turned out to be the same material again -- the Testinterview run is
the Freiensteinau 1 recording (its separation gives the candidate
83.5 % against 85.7 %, on the same three file names), and the twenty
minute Auphonic file is a slice of Freiensteinau 2 (1805 of its 2928
five word runs stand in that episode's transcript). They are used
below as a second reading, not as a third and fourth episode.

**The transcripts carry punctuation.** The recognition macOS brings
with it writes the mark on the word, so the question mark is there to
count: `Wie geht das?` arrives as one row with the mark. No fallback
to question words was needed, though it was counted alongside and is
in the table. One track of 66.6 minutes costs 19.4 s, one of 176.7
minutes 56.9 s.

A question is what the program itself calls a question: the last word
of a sentence, closing marks stripped, ends in `?` -- the same rule
`answer_moments` uses, so these figures and the reaction cut count the
same things.

### The four episodes, speaker by speaker

Speaking time is the span of the words with holes under 0.6 s closed.
For Freiensteinau it can be checked against the program's own
separation, which never saw the same input: 3479.5 s here against
3434.6 s in `Interview_BGM_Freiensteinau_speakers.edl` for the
candidate, 447.4 against 432.6 for the moderator.

| episode | speaker | words | sentences | questions | of sentences | opens with a question word | speech | share |
|---|---|---|---|---|---|---|---|---|
| Freiensteinau 1 | Kandidat | 10353 | 582 | 13 | **2.2 %** | 5.7 % | 3479.5 s | 85.0 % |
| | Moderator | 397 | 36 | 8 | **22.2 %** | 19.4 % | 166.1 s | 4.1 % |
| | Moderatorin | 1124 | 94 | 30 | **31.9 %** | 30.9 % | 447.4 s | 10.9 % |
| Freiensteinau 2 | Kandidat | 7544 | 368 | 10 | **2.7 %** | 3.0 % | 3059.9 s | 80.2 % |
| | Moderator | 368 | 30 | 9 | **30.0 %** | 23.3 % | 156.5 s | 4.1 % |
| | Moderatorin | 1492 | 126 | 49 | **38.9 %** | 37.3 % | 598.6 s | 15.7 % |
| Steinau 1 | Kandidat | 11400 | 791 | 46 | **5.8 %** | 4.8 % | 5622.5 s | 60.1 % |
| | Moderator | 6399 | 737 | 94 | **12.8 %** | 7.5 % | 2634.4 s | 28.2 % |
| | Moderatorin | 2659 | 299 | 43 | **14.4 %** | 7.4 % | 1095.7 s | 11.7 % |
| Steinau 2 | Kandidat | 9647 | 787 | 64 | **8.1 %** | 6.4 % | 3314.2 s | 73.0 % |
| | Moderator | 1659 | 113 | 28 | **24.8 %** | 11.5 % | 688.8 s | 15.2 % |
| | Moderatorin | 1360 | 150 | 49 | **32.7 %** | 18.7 % | 535.4 s | 11.8 % |

The direction never turns. In all four the candidate asks the fewest
questions per sentence and speaks the longest, and no moderator ever
speaks more than the candidate.

A second recogniser says the same on the twenty minutes of
Freiensteinau 2 that went through auphonic.com: 26 of the
moderator's 44 sentences carry a question mark (59.1 %) and 0 of the
candidate's 117 (0.0 %), with the share 18.6 % against 81.4 %. Same
order, different size -- the absolute rate belongs to the recogniser,
the ranking does not.

### How far apart the roles stand

The candidate against the nearer of the two moderators, which is the
distance that has to hold:

| episode | questions per sentence | speaking share | questions per 10 min of own speech |
|---|---|---|---|
| Freiensteinau 1 | 2.2 % vs 22.2 % -- **20.0 points, 10.0x** | 85.0 % vs 10.9 % -- 7.8x | 2.24 vs 28.89 -- 12.9x |
| Freiensteinau 2 | 2.7 % vs 30.0 % -- **27.3 points, 11.0x** | 80.2 % vs 15.7 % -- 5.1x | 1.96 vs 34.50 -- 17.6x |
| Steinau 1 | 5.8 % vs 12.8 % -- **6.9 points, 2.2x** | 60.1 % vs 28.2 % -- 2.1x | 4.91 vs 21.41 -- 4.4x |
| Steinau 2 | 8.1 % vs 24.8 % -- **16.6 points, 3.1x** | 73.0 % vs 15.2 % -- 4.8x | 11.59 vs 24.39 -- 2.1x |

**This is the number that decides it.** Between the two productions
the distance falls by a factor of four or five on every measure. A bar
drawn where Freiensteinau puts it -- a moderator asks from 20 % of his
sentences up -- calls every speaker in Steinau 1 a candidate. The
ranking survives the change of production; a threshold does not.

The question word at the start of a sentence is the weaker of the two
readings and would not do on its own: in Steinau 1 it puts the
candidate at 4.8 % against the moderator's 7.5 %, 2.7 points apart
where the question mark gives 6.9.

### The swap after a question is the share again, not the question

The third measure was meant to be the shape of an interview itself:
A asks, B then talks for a while. Counted as "somebody else holds more
than half of the next 20 s, and more of it than the asker", against
the same count after every sentence that is *not* a question:

| episode | speaker | after a question | after a statement | difference |
|---|---|---|---|---|
| Freiensteinau 1 | Kandidat | 0.0 % (n=13) | 9.7 % (n=569) | -9.7 |
| | Moderator | 87.5 % (n=8) | 89.3 % (n=28) | **-1.8** |
| | Moderatorin | 96.7 % (n=30) | 53.1 % (n=64) | +43.5 |
| Freiensteinau 2 | Kandidat | 20.0 % (n=10) | 15.4 % (n=358) | +4.6 |
| | Moderator | 100.0 % (n=9) | 71.4 % (n=21) | +28.6 |
| | Moderatorin | 91.8 % (n=49) | 54.5 % (n=77) | +37.3 |
| Steinau 1 | Kandidat | 6.5 % (n=46) | 12.3 % (n=745) | -5.8 |
| | Moderator | 57.4 % (n=94) | 56.0 % (n=643) | **+1.5** |
| | Moderatorin | 62.8 % (n=43) | 44.1 % (n=256) | +18.7 |
| Steinau 2 | Kandidat | 6.2 % (n=64) | 8.6 % (n=723) | -2.3 |
| | Moderator | 53.6 % (n=28) | 56.5 % (n=85) | **-2.9** |
| | Moderatorin | 55.1 % (n=49) | 47.5 % (n=101) | +7.6 |

The gap between candidate and moderator is the largest of all three
measures -- 47 to 88 points, and never smaller than 47. But the
right-hand column says what it is made of: for four of the eight
moderator rows the question changes nothing at all (-2.9 to +1.5
points). **Whoever speaks little hands over after everything he says,
question or not.** The measure separates the roles beautifully and
tells us nothing the speaking share did not already say. It is not a
third leg.

### How much of an episode it takes

The transcript of the first N minutes only, and the question: from
which minute on is the ranking right and right for the rest of the
episode? A speaker is ranked once he has ten sentences.

| episode | by questions | by speaking share |
|---|---|---|
| Freiensteinau 1 | 9 min | 2 min |
| Freiensteinau 2 | 7 min | 2 min |
| Steinau 1 | **6 min** | **23 min** |
| Steinau 2 | 2 min | 1 min |

The share settles first three times out of four, and the one time it
does not it is far the slower: Steinau 1 opens with a long setup in
which the moderator does the talking, and the share points at the
wrong person for 23 minutes. The questions are right there from minute
six. So the two do not merely agree -- **the questions cover the case
the share gets wrong**, which is what a second leg is for.

### What the raw lavaliers cost

Sebastian's condition was a track with one voice on it. Whether a
track has one voice is not a matter of how it was recorded but of what
comes back off it, and the two productions are not alike. Counted as
shared runs of five words between the transcripts of two tracks of the
same episode:

| episode | tracks | shared five word runs |
|---|---|---|
| Freiensteinau 1, after auphonic.com | Kandidat / Moderator | 0 of 10198 -- **0.0 %** |
| Freiensteinau 1, as uploaded | Kandidat / Moderator | 0 of 10412 -- **0.0 %** |
| Steinau 1 | Kandidat / Moderator | 11900 of 16605 -- **71.7 %** |
| Steinau 2 | Kandidat / Moderatorin | 7594 of 12531 -- **60.6 %** |

In Steinau every track holds the whole conversation: the moderator's
own recognition returned 19300 words where the candidate's returned
16884. Counting questions on those tracks as they stand gives the
moderator's questions to whoever has the hottest recorder gain.

So they had to be taken apart first. The tracks were brought onto one
axis by matching five word runs -- 11783 matches for Steinau 1, a
straight line through them, and 90 % of the matches within 64 ms of it
-- and every word then went to its own track only where that track's
level over that word led the others. **Every track's level is referred
to its own loudest tenth of a per cent before the comparison.** Without
that step the candidate's 8 to 11 dB hotter recorder takes the whole
episode: it put a question of the moderator's -- who thought of tiling
the swimming pool -- in the candidate's mouth.

That gate was checked against a truth, not trusted. The three clean
Freiensteinau 1 tracks were mixed into each other at -11.5 dB, the
depth measured on Steinau, which reproduced the fault exactly -- all
three mixes then recognised about 11700 words, the whole conversation,
as Steinau does. Recognised again and taken apart by the same gate:

| | words judged | right |
|---|---|---|
| gate over the mixed tracks | 11370 | **99.79 %** |
| the same, candidate's track lifted 8 dB | 11370 | 99.79 % |
| the same without the normalising step | 11435 | 99.32 % |

and the rates it gives back against the rates the clean tracks give:
candidate 2.9 % against 2.2 %, moderator 25.7 % against 22.2 %,
moderatorin 34.5 % against 31.9 %. **The gate costs under a point on
the candidate's rate**, which is well inside the distance the roles
stand apart.

The reservation is the margin it decides on. Over the words it kept,
the winning track led by 5.9 dB in the checked case and by only 1.3 dB
in Steinau 1 and 3.7 dB in Steinau 2. The Steinau figures are made
much closer to the gate's limit than the figures the 99.79 % was
measured at.

### What was not measured

* **No episode where it is the other way round.** None was found: in
  none of the four does a candidate lead on questions or a moderator
  lead on speaking time. That is not the same as saying there is none.
  Two productions, one room each, both the same format -- a candidate
  before an election, two moderators asking. A panel, two candidates,
  a guest who interviews the host: none of that is in this material,
  and none of these figures says what would happen there.
* **The near miss that is in the material.** Steinau 1 comes within
  6.9 points on the questions and within a factor of 2.1 on the share.
  Nothing was measured that says a fifth episode could not close that
  gap altogether.
* **Whether the Steinau split is right.** Its numbers rest on the gate
  above, not on the program's own separation, and there is no
  separation output for Steinau to check them against. The 99.79 % was
  measured on a mix built for the purpose, at a margin four times
  wider than the one Steinau 1 offers.
* **Who is who in Steinau 2.** The moderator's track is `REC00018`
  plus `REC00019`, named after the recorder and not after a person.
  That they are the moderator's is taken from the file dates matching
  Steinau 1's `Moderator.wav`, not from anybody saying so.
* **The recognition on a track full of bleed.** It is visibly worse --
  it hears compound words that do not exist and mangles ordinary ones --
  and a question mark is
  put there by the recogniser, not by the speaker. How much of the
  candidate's 5.8 % and 8.1 % is his and how much is the recognition
  was not separated.
* **The first minutes of a raw recording are not the episode.** Steinau
  1 runs 151.7 minutes, of which the interview is roughly the first
  125; the rest is packing up. The setup chatter is counted in
  everything above, and it is what makes the share need 23 minutes.
* **Nothing was listened to.** Every figure comes off a transcript.

### What the numbers say

The question mark carries. It sorts the roles the right way round in
four episodes out of four, it is the only one of the three measures
that adds anything the speaking share does not already give, and it is
right from minute six in the one episode where the share is wrong for
twenty-three.

What it will not carry is a fixed bar. The distance between the roles
is 20 to 27 points in one production and 6.9 in the other, and a bar
set on the first misreads the second completely.

So the shape a proposal can take is a ranking over the speakers of one
episode -- fewest questions per sentence, most speaking time -- offered
as a name to overwrite, never as a fact. Ten minutes of transcript is
enough for the ranking to settle in three of the four; the fourth
needs twenty-three because of what stands in front of it. Four
episodes out of two productions is enough to say the direction holds;
it is not enough to put a number on how often the ranking would be
wrong. The decision is not made here.
