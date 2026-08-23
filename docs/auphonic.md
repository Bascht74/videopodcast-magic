# Processing at auphonic.com

*Auf Deutsch: [auphonic.de.md](auphonic.de.md). Back to the [contents](README.md).*

## Processing at auphonic.com

The assembled audio is processed at auphonic.com with a stored preset and
comes back as an ordinary audio file. The access is entered once, the
preset belongs to the single production.

The key is in the Auphonic account settings, or in `AUPHONIC_TOKEN`. In the
interface it stands behind **Settings ...** in the footer, with the tick
**Save in Keychain** that keeps it in the Keychain (macOS) or in the
Registry (Windows); the window itself is described in
[The interface](interface.md). Never in a file, never in the project file.

In the box **Access to auphonic.com** the key goes into the field
**API Key:**; **Connect** checks it and fetches the presets (on the command
line `--auphonic-api-key`).

Two things about the key are worth knowing rather than assuming:

* On its way to auphonic.com it never appears in the process list: curl reads
  it from a config file that only its owner can read and that is deleted
  afterwards -- overwritten first where it cannot be deleted, and the key goes
  in escaped, so a quotation mark or a line break in it cannot add directives
  of its own.
* But `--auphonic-api-key KEY` puts it into the command line of this program,
  where `ps` and the shell history can see it -- on the command line, prefer
  `AUPHONIC_TOKEN`.

Storing it in the macOS Keychain hands it to the `security` program over that
program's input, not as an argument, and reads it back to see that it arrived;
only where the wrong key comes back does the argument form follow, which has
the weakness of the command line. The Windows Registry path does not have it.

On tab **2. Assignment & time window** the box **Processing at
auphonic.com (optional)** holds what this run does. It stands under the
assignment table, right below the tick **Multitrack (one track per
speaker)**.

* the preset under **Preset:** (on the command line `--auphonic-preset`)
* the tick **Fetch transcript** beside it

The production is rebuilt from the preset.

### Fetch transcript

With **Fetch transcript** auphonic.com writes down what is said (on the
command line `--transcript`). Three files come back beside the audio:

* a json with times
* an srt for subtitles
* a txt to read

Auphonic's own Whisper does the work: no account anywhere else, no extra
fee, a longer production. With multitrack the transcript carries the
speaker names.

### Working without Auphonic

Multitrack no longer needs the service. The first entry of the preset
list, **work without Auphonic**, keeps this run here (on the command line
`--without-auphonic`). It is not a preset but the statement that this run
does not go there; the key stays in the field, remembered and checked,
only not passed on. The Multitrack tick sits above the Auphonic box and
needs no key.

Everything then happens here: the tracks are aligned on the common axis,
mixed, brought to the target loudness (`--lufs`, -16 by default) and
distributed over the cameras. Camera cut and Resolve project come out as
usual. Missing is only what the service does: de-bleed, leveler, noise
removal. The bleed stays in the audio.

Who speaks when comes from the local speaker separation
([Speech recognition and speaker separation](speech.md)); without it, it is
measured from the tracks, and the bleed is taken out of that measurement,
not out of the audio. How it is measured, and how far down it still works,
stands in [Speaker statistics, camera cut, EDL](camera-cut.md).

Without multitrack there are no separate tracks and therefore no camera cut,
with the service or without. The audio is then joined and laid into the
video as recorded; only Auphonic sets the loudness.

While no key is checked, the list holds this one entry. Once the presets
arrive, the choice jumps to the first of them. A deliberate choice
survives a rebuild of the list and goes into the project file.

### A production that already exists

Where a production of that name is already there, it asks:

1. take the existing result -- nothing computed, nothing paid
2. recompute with the chosen preset, the files stay where they are -- costs
   no credit
3. upload everything again and recompute -- costs credit
4. cancel

Only the upload costs credit -- presets can be tried out without paying; on
its own the script never uploads. Entry 1 appears only where everything
needed is there. Where the tracks are named differently there, it asks
whether to take those names -- that costs nothing either.

On a recompute the track settings are brought to the preset as well. Further
tracks there go into the mix, and a warning names them.

Everything is downloaded: the single tracks and every further output of the
preset -- chapter marks, transcript, analyses. All of it lands in
`auphonic-tracks/` next to the finished videos, later the `final_*.wav` too.

Setting In point and Out point afterwards costs no second run at
Auphonic. The tracks are trimmed to the new window. Where the length
matches neither the window nor the whole measured range, the files belong
to another run, and the message says so.

### Further options on the command line

The window does not offer these.

* `--auphonic-preset` without a name: the existing presets are listed with
  numbers and asked for, and a key without files lists them too.
* `--auphonic-resume result|rerun|adopt|upload|abort` answers the question
  about a production that already exists in advance.
* `--auphonic-done FOLDER` fetches nothing and takes the tracks lying there,
  named after the speakers.
