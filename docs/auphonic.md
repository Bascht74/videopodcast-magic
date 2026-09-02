# Processing at auphonic.com

*Auf Deutsch: [auphonic.de.md](auphonic.de.md). Back to the
[contents](README.md).*

## The key and the preset

The service at auphonic.com processes the assembled audio with a stored
preset and sends it back as an ordinary audio file. The access goes in
once, the preset belongs to the single production.

The key is in the Auphonic account settings, or in `AUPHONIC_TOKEN`.
Never in a file, never in the project file.

1. Open **Settings ...** in the footer; the window itself is described
   in [The interface](interface.md).
2. In the box **Access to auphonic.com** fill in the field **API Key:**
   (on the command line `--auphonic-api-key`).
3. Optional: tick **Save in Keychain**, which keeps the key in the
   Keychain (macOS) or in the Registry (Windows). On a Mac the keychain
   has to be unlocked for that, and the window says so where it is not.
4. Press **Connect**. It checks the key and fetches the presets.

![The box for the key](images/settings.png)

*The window that Settings ... opens: above the box for the key, below
the box for Resolve. The field is still empty.*

A key that auphonic.com does not accept opens no window. **Connect**
does not turn green, and under the field a line says what auphonic.com
replied, with a button beside it that opens the settings. That line
stands in the settings window and in the box on the **Assignment & time
window** tab alike. It names a missing key as well.

* On its way to auphonic.com the key never appears in the process list:
  curl reads it from a config file that only its owner can read. The
  program deletes that file afterwards, and overwrites it first if it
  cannot delete it. The key goes into that file escaped, so a quotation
  mark or a line break in it cannot add directives of its own.
* But `--auphonic-api-key KEY` puts it into the command line of this
  program, where `ps` and the shell history can see it. On the command
  line, prefer `AUPHONIC_TOKEN`.

Storing it in the macOS Keychain hands it to the `security` program over
that program's input, not as an argument, so the key does not stand in
the process list on that way either. The program reads it back to see
that it arrived. There is no second way round: handing it over as an
argument would put it where everybody on the machine can read it, so
where the Keychain does not take it, nothing is stored and a line says
why. The tick comes off again with it, so it never stands there green
over a key that is gone at the next start. The Windows Registry path has
no such question.

A locked keychain is looked at before anything is handed over. While it
is shut, the tick **Save in Keychain** is grey, and under it stands, in
the colour of a warning, **The keychain is locked. Unlock it and this
button wakes up.** Beside that line is **Open Keychain Access**, which
opens the program that unlocks it. Unlock it there and the tick comes
back by itself, within half a second -- and that waking is the sign the
unlock took, because nothing else reports it. The look itself asks
nothing and puts nothing on the screen.

On the **Assignment & time window** tab the box **Processing at
auphonic.com (optional)** holds what this run does: the preset under
**Preset:** (on the command line `--auphonic-preset`). The program
rebuilds the production from that preset.

The tick **Multitrack (one track per speaker)** is not in the Auphonic
box and needs no key. What it decides here is whether every person keeps
a track of their own: only separate tracks can auphonic.com work on one
by one and free of the bleed from the others. Where everybody stands in
one track there is nothing for the de-bleed to take apart.

The number of tracks decides the kind of production. A single track goes
up as an ordinary production, two or more as a multitrack production,
and the preset has to match: an ordinary preset for the one, a
multitrack preset for the others.

### The transcript is made here

None of the text comes from auphonic.com. The program listens to the
finished mix on this machine and writes down every word with the time it
was said. Three files land in the output folder, named after the
**Production name**:

* a json with times
* an srt for subtitles
* a txt to read

Where the voices have been told apart, the transcript carries their
names. Where they have not, it carries none: who said a sentence is then
not known, and a guessed name in a transcript is worse than a gap.

This costs the processor, not credit. It needs no key, no preset and no
upload, and a run without Auphonic writes the same three files. How many
words were heard and how many seconds the listening took stands in the
log; under the heading **TRANSCRIPT** stand the three paths.
`--no-transcript-file` leaves the files out -- the words are still heard,
and the cut still takes its sentence boundaries from them.

Which way the recognition takes on which machine, what it costs there
and what the text is used for is in [Speech recognition and speaker
separation](speech.md).

### Working without Auphonic

Every run can do without the service. The first entry of the preset
list, **work without Auphonic**, keeps this run here (on the command
line `--without-auphonic`). It is not a preset. The key stays in the
field, remembered and checked, only not passed on.

Everything then happens here: the program aligns the tracks on the
common axis, mixes them and distributes them over the cameras. Camera
cut and Resolve project come out as usual. Missing is only what the
service does: de-bleed, leveler, noise removal. The bleed stays in the
audio.

`--lufs` sets the target loudness; a lower number is quieter. The same
gain goes on every track, which keeps the balance between the speakers.
Without it, and with **Take from source files** in the window, nothing
is adjusted at all: the sound stays as it is in the source files.

The local speaker separation says who speaks when ([Speech recognition
and speaker separation](speech.md)). Without it, the program measures it
from the tracks and takes the bleed out of that measurement, not out of
the audio. The measurement and its lower limit stand in [Speaker
statistics, camera cut, EDL](camera-cut.md).

As long as the program has checked no key, the list holds this one
entry. Once the presets arrive, the choice jumps to the first of them. A
deliberate choice survives a rebuild of the list and goes into the
project file.

### When the production already exists

The program finds the production by name and asks what should happen to
it:

1. take the existing result: nothing computed, nothing uploaded
2. recompute with the chosen preset, the files stay where they are:
   costs no credit
3. upload everything again and recompute: costs credit
4. cancel

The upload alone spends credit. Answer 2 recomputes with the new preset
and uploads nothing, so preset after preset can be tried. The program
uploads only when asked to. Answer 1 appears only if everything needed
is there. If the tracks are named differently there, the program asks
whether to adopt those names.

On a recompute the program brings the track settings to the preset as
well. Further tracks there go into the mix, and a warning names them.

The program downloads everything, the single tracks and every further
output the preset itself makes: chapter marks, analyses, and a
transcript of its own where the preset produces one. All of that is paid
for with the production either way. It lands in `auphonic-tracks/` next
to the finished videos, later the `final_*.wav` too.

The program handles a later In point or Out point here, not at Auphonic.
It trims the returned tracks to the new window. If the length matches
neither the window nor the whole measured range, the files belong to
another run, and the message says so.

### When something goes wrong

* **Connect does not turn green.** The line under the field says what
  auphonic.com replied. The button beside it opens the settings;
  correct the key there.
* **The preset list holds only its first entry.** No key has been
  checked yet: press **Connect**.
* **The returned tracks fit neither the time window nor the whole
  measured range.** They belong to another run. Use the folder that
  belongs to this run, or let the audio go through auphonic.com again.
* **A run is about to cost credit that was not meant.** Only answer 3
  uploads, and only the upload costs. Answers 1 and 2 leave the files
  where they are.

The audio is now processed and lies in `auphonic-tracks/`. How the
tracks are spread over several speakers and several cameras stands in
[Multitrack: several speakers, several cameras](multitrack.md).

### Further options on the command line

The window does not offer these.

* `--auphonic-preset` without a name: the program lists the existing
  presets with numbers and asks for one, and a key without files lists
  them too.
* `--auphonic-resume result|rerun|adopt|upload|abort` answers the
  question about a production that already exists in advance. It
  reaches only a run that uploads several tracks; a single track has no
  per-track upload to take up again.
* `--auphonic-done FOLDER` fetches nothing and takes the tracks lying
  there, named after the speakers.
