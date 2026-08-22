# The simple path

*Auf Deutsch: [simple-path.de.md](simple-path.de.md). Back to the [contents](README.md).*

## The simple path

The simple path is the run with the tick **Multitrack (one track per
speaker)** left off. It sits in the box **Production** on tab
**1. Files & production**, and a second time above the tables on tab
**2. Assignment & time window**.

Both paths write the same kind of file: MOV, picture copied over, audio
uncompressed, the `colr` box and the camera's QuickTime keys carried along.

What the simple path does just like multitrack:

- **Time window.** The buttons **Mark In** and **Mark Out** work here too
  (on the command line `--in-point` and `--out-point`), in the notations
  listed in [multitrack.md](multitrack.md), section "Time window". The
  audio is trimmed; the picture stays whole and keeps its timecode.
- **Preview player.** Same tab, same buttons.
- **Resolve project.** Several cameras give one timeline with all of them
  side by side, ready for multicam; one camera a straight one.

Camera cut, speaker statistics and cut forecast are missing: they need the
speaker assignment.

Audio only: the continuation files are joined and written. Audio and video:
the audio is aligned and laid into the video file. One video only: its own
audio, left and right kept apart.

### The recordings beside the mix

Without Multitrack all the audio goes into one track. Where several
recordings ran at the same time, each of them also goes into the video
as a track of its own, after the mix, on the same axis and of the same
length.

Whether they ran at the same time is read from the timecode rather than
guessed. Recordings that overlap were several microphones at once.
Blocks that follow one another are one recording and get no extra tracks.

The single tracks are as recorded: this path sends only the mix to
auphonic.com, so no de-bleed and no leveler on them. They cost about
520 MB per track and hour. Where the mix comes back from auphonic.com
with a different length than they have -- a jingle prepended on the free
tier -- they drop out by themselves and the run says so.

The script finds continuation files itself; the first numbered block is
enough. Only what joins seamlessly counts -- checked on the timecode,
otherwise on the block size. A later take with the same naming pattern is
not appended.

The offset is always measured, even where both sides carry timecode.
Where it is on both sides, the run ends by saying how far it lies from
the measured value.

### Blocks that carry a clock, not a counter

A recorder numbers its files and the next block is the next number. A
mixer often writes the date and the time of day instead:
`r_260808_185628.wav` and `r_260808_190128.wav`.

The clock is read and held against the length: the next block belongs
to the recording when it starts where the previous one ends, within two
seconds. Where every block carries the same clock -- the start of the
session, with the real index in a counter behind it -- the counter rule
applies as before.

### Putting blocks together by hand

Where the file names give the search nothing to go on, the recording
carries a selector **belongs to** in the file list on tab
**1. Files & production**. It puts this recording into another one, with
every block it has (on the command line `--together A B C`, in that
order, repeatable for several). Each name brings the blocks that already
belong to it.

The other direction: pick the block's row in the file list and press
**Remove** -- it then stays out of the recording it was found in (on the
command line `--apart`). Both are by hand, both beat the measurement, and
a file set apart stays out even of a group it was put into. Both are
stored in the project.

### Per video file

1. Which part of the audio has a counterpart in the picture? The rest falls
   away.
2. Align over envelopes against the camera's audio track.
3. Measure the clock drift and take it out, as far as the measurement
   carries; the picture is the reference.
4. Bring the audio to the start point and length of the picture, gaps
   filled with silence.
5. Reassemble: picture untouched (`-c:v copy`), the new audio as the first
   track, the camera track behind it, both named, timecode kept.
6. Measure again how far the new track lies against the camera track.

### Why MOV

The target is always MOV, for MP4 sources too; nothing is computed again.
MP4 would throw the track names away and has no uncompressed audio in the
standard. There is no `--container`.

### Further options on the command line

These options are not in the window.

- `--no-single-tracks` leaves the single recordings out of the video.
- `--no-camera-audio` leaves the camera's own track out of the new file.
- `--help` marks each switch with `[simple path only]` or
  `[multitrack only]`. Both markers stay English, even with `--lang de`.
