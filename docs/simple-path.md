# The simple path

*Auf Deutsch: [simple-path.de.md](simple-path.de.md). Back to the
[contents](README.md).*

## The run without Multitrack

The simple path is the run with the tick **Multitrack (one track per
speaker)** left off. The tick sits on the **Assignment & time window**
tab, above the box **Processing at auphonic.com (optional)**.

The tick decides how the recordings are grouped, not which way the run
takes. With it, every person gets a track of their own, under their name
and tied to a camera. Without it, all the audio becomes one mix.
Everything after that is the same machine: one common time axis, one
writer.

Both paths write the same kind of file: MOV, picture copied over, audio
uncompressed, the `colr` box and the camera's QuickTime keys carried
along.

What the simple path does just like multitrack:

- **The same files.** Metrics, transcript, the four cut lists, the audio
  tracks as files in `auphonic-tracks/` and the handover for Resolve are
  written here as well.
- **Time window.** The buttons **Mark In** and **Mark Out** work here
  too (on the command line `--in-point` and `--out-point`). They take
  the notations listed in [Multitrack](multitrack.md), section "Time
  window". The point lies on the common time axis and means the same
  moment for every camera. The program trims the audio; the picture
  stays whole and keeps its timecode.
- **Preview player.** On the **Assignment & time window** tab, with the
  same buttons.
- **Loudness measured.** The sum is measured and the figure goes into the
  log, under `NORMALISE` as **Sum of tracks**, with LUFS, peak and range.
  The target comes from **Loudness** in the **Production** box (on the
  command line `--lufs`). With cameras in the material one gain moves
  every track by the same amount, so the speakers keep their balance.
  Without a target nothing is adjusted ([Preflight](preflight.md),
  section "Which loudness target holds").
- **Resolve project.** Several cameras give one timeline with all of them
  side by side, ready for multicam. One camera gives a straight timeline,
  or a cut one as soon as the speakers are told apart.

One track per speaker is not part of it. The mix reaches auphonic.com as
a single track, and without separate tracks the de-bleed has nothing to
take apart.

What comes out depends on the material:

- **Audio only.** This is the one case with a path of its own. The
  program joins the blocks into one file `<name>_joined.wav`, or sends a
  single recording on its own to auphonic.com. The target holds here as
  well, one gain per recording. The level between two of them then comes
  from the target, not from the recording.
- **Audio and video.** The program aligns the audio and lays it into the
  video file.
- **One video only.** The program takes its own audio, left and right
  kept apart.

### Telling the speakers apart on one track

One recording everybody is audible on is enough for the cut. The video
file carrying that sound has to be set to contribute it: in the file
list on the **Files & production** tab, in that file's row, put **Camera
audio** on **use the audio**. It then has a row in the assignment table.
Answer its **Speaker name** with **several speakers**, the one entry
that field offers to pick, and the voices on that one recording are told
apart ([Speech recognition and speaker separation](speech.md)). The
column **Speakers** says how far that got; the voices themselves come up
as indented rows under the recording.

The field never answers itself from a separation already stored. A
recording that was separated once, but that nobody answered for, shows
an empty field and no voice rows. Picking **several speakers** later
puts the voices there at once, with their names and cameras, without
computing anything again.

Where a row carries a name and is not on **several speakers**, the
column **Speakers** offers *Only one speaker -- separate the track?* as
a flat text button. A click sets the field to **several speakers**, and
the voices appear.

With exactly one video file with sound and no audio recording beside it
nobody has to set anything: that sound is the only sound there is, so
the field sets itself and says why, greyed out. Add an audio recording
and it is a question again ([Multitrack](multitrack.md), section "Making
camera sound a track").

With one camera nothing is switched over: there is nothing to switch to.
What comes of it is a cut at every change of speaker, so Resolve gets one
section per person instead of one long take. Each section can be grouped,
coloured and given a framing of its own there, which on a 360 degree
camera is the whole point. The passages sit on that timeline as markers,
a colour per person, so it is visible who speaks where.

The log says `FIRST CUT BY SPEAKER` instead of `CAMERA CUT` as soon as
all the speakers sit on the same camera; the heading follows nothing
else. The box in the window is named by a rule of its own and does not
always agree with it. Speaking times, cut forecast, the settings of the
cut and the four cut lists come with it
([Speaker statistics, camera cut, EDL](camera-cut.md)).

One voice found is not a fault. What comes of it depends on how many
cameras there are:

- **One camera.** Nobody hands over and there is nothing to switch to,
  so there is no cut. Resolve gets the camera in one piece with the mix
  under it, and the passages are marked there too. The box in the
  window is called **First cut by speaker**.
- **Two cameras or more.** The program takes the first camera nobody is
  assigned to, calls it the wide shot and cuts it in. The box is called
  **Cut with the wide shot**. The log still says
  `FIRST CUT BY SPEAKER`, because all the speakers sit on the same
  camera.

With two speakers on cameras of their own it stays a camera cut, in the
log and in the window.

### What goes into the video beside the mix

Without Multitrack all the audio goes into one mix. The video file gets
two audio tracks and no more: track 1 the `Full-Mix`, track 2
`Camera Original`, the camera's own sound.

The single recordings are not in the video. They lie beside it in the
folder `auphonic-tracks/` as `final_<name>.wav`, with the timecode in
the name where the material carries one, in the bext chunk and as iXML
for Premiere and Media Composer.

With one recording the mix keeps that recording's channel count: a mono
recording gives `Full-Mix from 1 tracks, 1 channel` in the log, two
recordings give `Full-Mix from 2 tracks, 2 channels`. A stereo source
raises the number to two by itself.

The run reads from the timecode which recordings ran at the same time.
Recordings that overlap were several microphones at once. The program
calls each file of a split recording a block. Blocks that follow one
another are one recording.

The script finds continuation files itself; the first numbered block is
enough. Only what joins seamlessly counts, checked on the timecode,
otherwise on the block size. The program does not append a later take
with the same naming pattern.

The program always measures the offset, even when both sides carry
timecode. If timecode is on both sides, the run ends by saying how far it
lies from the measured value.

Where a recording reaches past the picture, that part is left out. The
log says it for each track, one line apiece:

```
    Rec: 0:00:04,000 at the front and 0:00:04,000 at the back have no picture and are left out
```

The line comes only where more than a quarter of a second falls away at
the front or at the back.

A video the run cannot place at all stays out. Where neither the shape of
the sound nor its phase finds the camera in the recording, and the file
carries no timecode fitting the rest of the material either, the run
names the file and goes on without it instead of laying it down where the
best of several bad numbers points. The line says what would help: a
timecode that fits the other recordings, set with another program. A file
whose timecode does fit is placed by that clock and never asked about its
sound; a single timecode among files that carry none is not a place.

### How the run reads a clock instead of a counter

Names with date and time of day count as blocks too:
`r_260808_185628.wav` and `r_260808_190128.wav`. A recorder numbers its
files; a mixer often writes the clock instead.

The next block belongs to the recording when it starts where the previous
one ends, within two seconds. If every block carries the same clock, the
counter rule applies as before. That clock is the start of the session,
and the real index sits in a counter behind it.

### Putting blocks together by hand

If the file names give the search nothing to go on, put the blocks
together by hand:

1. In the file list on the **Files & production** tab, expand the
   recording's row.
2. In the selector **belongs to**, choose the recording it belongs to.

![The blocks of one recording](images/blocks.png)

*The expanded row: the selector belongs to, set to a recording of its
own, and under it the three blocks with size and runtime.*

The recording goes into that one with every block it has. The program
offers the selector only when another recording is available to join. It
leaves the selector out on a recording that is itself joining into
another: a chain of joins is not on offer. To undo it, choose **a
recording of its own**.

On the command line `--together A B C` names them in that order and is
repeatable for several; each name brings the blocks that already belong
to it.

The other direction: pick the block's row in the file list and press
**Remove**. It then stays out of the recording it was found in (on the
command line `--apart`). Both beat the measurement. A file set apart
stays out even of a group it was put into. The project stores both.

### What comes back for each video file

Each video file comes back with the picture untouched (`-c:v copy`), the
new audio as the first track and the camera's own track behind it. The
program names both tracks and keeps the timecode.

The new track is always called `Full-Mix`. The camera's own is called
`Camera Original`; a camera bringing several of its own gets them
numbered `Camera Original 1`, `Camera Original 2` and so on.
`--name-camera` sets that second name.

### Why the target is always MOV

The target is always MOV, for MP4 sources too; the program copies picture
and audio instead of computing them again. MOV carries the track names
and the uncompressed audio, MP4 does neither, so `--container` does not
exist.

### When something goes wrong

- **The camera's row is missing from the assignment table.** Its sound
  is not in use yet: put **Camera audio** on **use the audio** in the
  file list.
- **The continuation files are missing from the recording.** The names
  give the search nothing to go on: put them together by hand with
  **belongs to**.
- **A file was taken into a recording it does not belong to.** Pick its
  row and press **Remove**; it stays out from then on.
- **A recording is missing from the video.** Only the mix and the
  camera's own sound go in. The recordings themselves are in
  `auphonic-tracks/`, one file each.
- **A video file is missing from the result.** The run could not place
  it: its sound has nothing in common with the rest of the material and
  it carries no timecode. Give it one that fits the other recordings,
  with another program, or set it to **ignore this video** in the column
  **Kind** of the file list so it does not take part. In the window the
  program proposes that by itself ([The interface](interface.md)).

The video now holds the finished mix and the camera's own sound, and the
recordings lie beside it as files. What auphonic.com does to the mix is
in [Processing at auphonic.com](auphonic.md).

### Further options on the command line

These options are not in the window.

- `--no-single-tracks` counts for the run entirely without picture: it
  decides there whether the blocks are kept singly. Where there is
  picture it changes nothing, because the video holds no single tracks.
- `--no-camera-audio` leaves the camera's own track out of the new file.
- `--help` puts `[simple path only]` or `[multitrack only]` on a switch
  that works on one path only. Both markers stay English, even with
  `--lang de`.
