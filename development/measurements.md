# What was measured

For `videopodcast-magic.py`. Where the numbers come from: what was
measured, how, and what came out. Not part of the manual and English
only: this is for whoever changes the program, not for whoever uses it.

How the program is built is in [Inside the script](internals.md).

---

## How long the speech recognition takes

macOS 26 brings the recognition with it: one hour of audio in a good
20 seconds, 0 MB to fetch, the Command Line Developer Tools required.
Otherwise faster-whisper with `large-v3-turbo`: 144 MB of packages and
a model of 1.5 GB. Without an NVIDIA graphics card it runs on the
processor -- on a Mac not quite three times faster than the recording
is long, on an ordinary Windows machine 25 to 70 minutes for an
episode of 72 minutes.

The recognition runs in a strand of its own beside the cameras. On the
Mac it costs 22 s per hour.

## What the word times are worth

Both recognisers report the beginning of a word about a tenth of a
second late, measured against the audio itself.

macOS almost never puts a gap between two words: 98 % of the word
pairs stand without a space, across sentence boundaries as well, and
its time grid is 60 ms. Whisper has room there.

## What the recognition gets wrong

Over one measured hour: the same recording over the mix 96 %
agreement, over the raw recording 75 %.

Invented words in the silence are a known fault of Whisper -- 21 words
in a five minute setup pause. The voice activity detection is switched
on, and with it they are gone.

Names and anglicisms are the errors that remain, on both paths and
evenly spread over the length.

One hour of one recording lies behind these three figures. Whether
they hold for another room, other microphones and other voices was not
measured.

## How well the speakers are separated

Measured on 45,473 words over two whole interviews: 98.7 % right.
77 % of the errors lie in real overlap or within half a second of a
change of speaker; real mix-ups in a quiet passage 0.28 %. The raw
recording separates as well as the processed mix.

Widening the edges by 0.2 s and closing gaps under 0.25 s brings
4.2 points. At 0.5 s it tips over.

A given speaker count improves the recognition and quadruples the
picture time on the wrong person. It is given only where somebody sets
it by hand.

Two interviews out of one production. How many people spoke, in which
room and on which microphones is not part of the figure, so the 98.7 %
carries no further than material recorded the same way.

## What the separation costs

About 28 times real time on the graphics unit, one run at a time. Two
in parallel bring 12 % throughput, cost 1.75 times the wait for the
first result and 4.5 GB per process.

Different kinds of work do not slow each other down (0 %). From four
processors on, everything runs together.

The setup fetches about 218 MB into an environment of its own. The
model itself lies with the program.

All of this comes from one machine, and the machine is not named here.
What carries over are the ratios -- the gain from running two, the
memory per process -- not the absolute times.

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
excerpts of one 32 channel recording judged the same pairs differently,
because at -85 dBFS it was dither being compared.

On one mixer recording the first five minute block was the soundcheck
and gave one used channel pair; the second was the recording and gave
ten tracks. That is why the recording is judged as a whole.

Reading a block in one pass instead of once per channel, measured on
one 92 MB block of 32 channels: 2.0 s instead of 22.9 s, with the same
levels and the same pairs. A pair of 1.8 GB blocks drops from about
fifteen minutes to about ninety seconds.

The equal-power law of ffmpeg's own channel conversion, measured on a
signal at -24.08 dBFS: one channel to two comes out at -27.09, two
channels to one at -21.07. Three decibels one way or the other,
inaudible in a single listen and wrong in every meter.

## Where the envelope alignment stops

Measured on one phone recording of monitor speakers against the
finished Logic mix of the same music -- music with singing, not a
podcast, and so exactly what the envelope way was never built for.

`align_envelopes` finds nothing: a quality of 0.13 over the whole and
-0.18 in the window, against a threshold of `WEAK_MATCH = 0.05`. Below
that it is not a find, it is a shrug. Material that belongs together
sits at 0.5 to 0.9 on the same figure.

The reason is in the method. Envelope cross-correlation asks where two
recordings are loud at the same time, and for that something has to
get loud and quiet again. A mixed and limited song holds the same
loudness for minutes. There is nothing to compare.

`phase_align` (`GCC-PHAT`) throws the loudness away and keeps only the
phase, which is what a re-recording through a room survives. First
try, with nothing to go on: offset **569.201 s = 9:29**, drift
**-29.1 ppm**, the video ending 11 s before the end of the audio. That
was checked against what the recording was expected to hold -- 8 to 11
minutes, and the video lying towards the end of the audio -- and both
fit. It is the only independent check there was: the material carried
no mark of its own to measure against.

The sharpness came out at 28.7 against 26.5 for the next best peak.
`PHASE_SHARP_ENOUGH = 8.0` is set from that one piece of material, so
it is a floor and not a measured threshold, and the log prints the
number so anybody can see how close it was.

The 12 ms left over are not an error. It is about 4 m from the
speakers to the phone, and sound needs 4 m / 343 m/s = 11.7 ms for
that. Whoever takes those 12 ms out moves the video wrong by the
travel time through the room.

`looks_like_music()` decides none of this and must not be read as if
it did. Settling it on the share of the syllable band, 2 to 8 Hz under
0.20, did not separate cleanly in the runs so far: a finished mix
landed at 26 %, speech at 31 to 32 %. The value goes in the log and
nowhere else.

One recording, one room, one phone. The offset is confirmed, the way
to it is not, and whether the phase way also beats the envelope on
speech has never been tried -- it runs as a fallback, after the
envelope has already given up.

## What one bad point does to the drift

Measured in `tests/outliers_test.py`, 19 checks, on a built series of
points: the true answer is known, so the error is known exactly too.

A single wrong point **at the start** moves the offset by 188.9 ms and
turns the drift from -64.07 ppm into +10.00 ppm -- not the size of it,
the sign. "The audio runs away" becomes "the video runs away", and a
correction made on that pulls the wrong way.

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
* Every point dropped is named in the log with its time and how far
  out it lay. A run that cleans up in silence cannot be checked
  afterwards.

The edge is where it hurts, because a fitted line tips about its
centre of gravity: a point in the middle sits almost on the pivot and
moves nothing, a point at the edge has the longest lever. The test
tries all three places on their own -- start, middle, end -- and the
start is the worst of them, because that is where an opening jingle
lies.

The series is built, not recorded. This says what the cleaning does to
a known fault, not how often such a fault turns up in crosstalk points
that were really measured.

## What the loudness was measured at

| File | measured |
|---|---|
| mix on one channel | -29.4 LUFS |
| the same mix on both channels | -26.3 LUFS |
| after normalising, two channels | -16.0 LUFS |

Leaving it to the editing program would be an invisible trap: a mono
track panned to the middle of a stereo bus lands at 0, -3, -4.5 or -6 dB
depending on the pan law.

## Clipping does not depend on the bit depth

The claim was that 24 bit material behaves differently at full scale
from 16 bit -- more headroom, a different kind of clipping. It was
doubted rather than argued about, and then measured. The claim was
wrong.

`ffmpeg ... -af astats` over the same clipped source, written out
three times, once per format. That it is the same source is the whole
point: only then can a difference be down to the format.

| Format | Flat factor | Peak count | Peak |
|---|---|---|---|
| 16 bit integer | 31.15 | 63,520 | 0.00 dBFS |
| 24 bit integer | 31.15 | 63,520 | 0.00 dBFS |
| **32 bit float** | 0 | none | **+5.94 dBFS** |

The first two rows are not close, they are identical: the same flat
factor to two decimal places, the same 63,520 samples sitting on the
maximum, the same peak. That settles it.

The line runs between integer and float, not between 16 and 24 bit. An
integer format cannot go past full scale -- there is a wall there, and
whatever stood above it was cut off as the file was written. Float
can, and 0 dBFS is only a mark on its scale: the +5.94 dBFS of the
third row are still in the file and can be pulled down afterwards.

So the clipping warning may only fire on integer formats. On float it
would point at material that nothing has happened to, and a warning
that does that teaches people to skip warnings.

Not measured: whether 24 bit material that a converter limited before
writing is still recognisable as clipped at all -- a limiter leaves
rounded tops rather than flat ones, and neither figure in the table
would see them. Nor whether the recordings this program is aimed at
ever reach 0 dBFS in the first place, which decides whether the
warning has anything to fire on.

## What the camera cut was measured at

* **Merging a short shot forward instead of backward** -- the wrong
  picture time falls from 326 s to 99 s over four runs, and from 42 s
  to 7 s with the truth as input.
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
  5 to 15 s, and no wide shot ends in the middle of a sentence.
* **The reaction cut** -- 25 to 40 cases per interview. 1 to 3 % of the
  picture time change owner, and no new cuts arise.

These are counts from interview recordings of one kind, and they are
what the defaults were derived from. Nothing here was measured on a
different sort of programme.

## The clip colours

The colours are sorted by distinguishability, so the first two lie as
far apart as possible. The wide shot gets "Tan" from that list, a warm
sand brown that on a dark background sits too close to the orange of
the second camera (34.9 CIE76); shown instead is a pale sage, at least
52.9 from every speaker colour. In Resolve the clip is still called
Tan, so that graded projects do not shift.

## What the opening wide shot was measured on

A rebuilt case: the same 92 second opening, once as one block and once
chopped into 14 pieces. Before, 100.3 s against 5.3 s; afterwards,
100.3 s against 100.3 s. A single wrongly labelled block in it: before
5.3 s, afterwards 24.6 s.

A long, cleanly wrongly labelled stretch in the middle of the opening
still ends it too early. Blocks are pulled together by speaker, and
whoever holds such a stretch alone counts as the one taking over. This
is not measured against the real interviews.
