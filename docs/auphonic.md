# Processing at auphonic.com

*Auf Deutsch: [auphonic.de.md](auphonic.de.md). Back to the [contents](README.md).*

## Processing at auphonic.com

With `--auphonic-api-key KEY` the assembled audio goes up, is processed
there with a stored preset, waited for, fetched and then used like any other
audio file.

The key is in the Auphonic account settings, or in `AUPHONIC_TOKEN`. In the
interface it stands behind **Settings ...**, top right of the tab bar, with
the tick **Save in Keychain** that keeps it in the Keychain (macOS) or in the
Registry (Windows); the window itself is described in
[The interface](interface.md). Never in a file, never in the project file.

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

The preset comes from `--auphonic-preset`; without it the existing ones are
listed with numbers and asked for, and a key without files lists them too.
In the interface the list stands under the assignment table, in the box
**Processing at auphonic.com (optional)** right below the Multitrack tick,
with **Fetch transcript** beside it: what this run is to do, in one place.
The production is rebuilt from the preset.

### Fetch transcript

With **Fetch transcript** auphonic.com writes down what is said and
delivers three files beside the audio: a json with times, an srt for
subtitles and a txt to read. Auphonic's own Whisper does the work, so no
account anywhere else is needed and there is no extra fee -- the
production only takes longer. With multitrack the transcript carries the
speaker names.

### Working without Auphonic

Multitrack no longer needs the service: `--without-auphonic` on the command
line, in the interface the first entry of the preset list, **work without
Auphonic**. It is not a preset but the statement that this run does not go
there; the key stays in the field, remembered and checked, only not passed
on. The Multitrack tick sits above the Auphonic box and needs no key.

Everything then happens here: the tracks are aligned on the common axis,
mixed, brought to the target loudness (`--lufs`, -16 by default) and
distributed over the cameras; camera cut and Resolve project come out as
usual. Only what the service does is missing: de-bleed, leveler, noise
removal. The bleed stays in the audio.

Who speaks when is measured from the tracks, and the bleed is taken out of
that measurement, not out of the audio. How it is measured, and how far down
it still works, stands in
[Speaker statistics, camera cut, EDL](camera-cut.md).

Without multitrack there are no separate tracks and therefore no camera cut,
with the service or without. The audio is then joined and laid into the
video as recorded; only Auphonic sets the loudness.

While no key is checked, the list holds this one entry. Once the presets
arrive, the choice jumps to the first of them; the placeholder alone does
not count as a choice. A deliberate choice survives a rebuild of the list
and goes into the project file.

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
whether to take those names -- that costs nothing either. On the command
line: `--auphonic-resume result|rerun|adopt|upload|abort`.

On a recompute the track settings are brought to the preset as well. Further
tracks there go into the mix, and a warning names them.

The speaker statistics are always requested, even where the preset does not
provide for them -- without them there is no camera cut.

Everything is downloaded: the single tracks, the statistics as
`<Production>_statistics.json` and every further output of the preset --
chapter marks, transcript, analyses. All of it lands in `auphonic-tracks/`
next to the finished videos, later the `final_*.wav` too.

`--auphonic-done FOLDER` fetches nothing and takes the tracks lying there,
named after the speakers. The statistics are looked for in that folder and
in its `auphonic-tracks/`.

Set In point and Out point afterwards and the tracks are longer than the new
window. They are trimmed and the times in the statistics shifted by the same
amount, so the camera cut still fits -- with no second run at Auphonic.
Where the length matches neither the window nor the whole measured range,
the files belong to another run, and the message says so.
