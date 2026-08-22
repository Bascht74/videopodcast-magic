# Video Podcast Magic

*Auf Deutsch: [README.de.md](README.de.md)*

**Version 1.0.0-beta.** It does the work it was written for, every
week, on real material. It is called beta because it is not finished
being tested: the format of the project file may still change, and an
older file is refused with a clear message rather than half read.

`videopodcast-magic.py` -- put processed audio into video files as the
first audio track, and build from it everything the edit needs afterwards:
the cameras on one time axis, a first cut by speaker, and a DaVinci Resolve
project.

One Python file, about 24000 lines. No package, no build step.

## Getting started

```
python3 videopodcast-magic.py                          interface
python3 videopodcast-magic.py AUDIO.wav VIDEO.mov
python3 videopodcast-magic.py AUDIO.wav                join only
python3 videopodcast-magic.py AUDIO.wav *.mov --out Done
python3 videopodcast-magic.py VIDEO.mov                takes the camera sound
python3 videopodcast-magic.py --lang de|en             language of the messages
python3 videopodcast-magic.py --help                   all switches
```

Without arguments the interface opens. Files are told apart by extension;
the order does not matter. `--lang de` or `--lang en` fixes the language;
without it the system locale decides. Only `--help` stays English.

## What it needs

Python 3.10 or newer, `ffmpeg` and `ffprobe` on the search path, and two
packages -- `PySide6` for the window, `numpy` for the measurements. What is
missing is installed at start over pip. macOS and Windows are what this is
used on; Linux works with two limits.

The detail, including which Python is recommended and what differs per
platform, is in **[docs/requirements.md](docs/requirements.md)**.

## The manual

* **[What it needs](docs/requirements.md)** -- Python, ffmpeg, the two packages, and what differs per platform.
* **[The interface](docs/interface.md)** -- The window, tab by tab -- and what to do when there is no timecode.
* **[Preflight](docs/preflight.md)** -- What is checked before a run starts, and what each complaint means.
* **[Channels: one track or two?](docs/channels.md)** -- How a stereo pair is told apart from two separate microphones. Measured, not guessed.
* **[The simple path](docs/simple-path.md)** -- One audio file, one camera: the shortest way through.
* **[Processing at auphonic.com](docs/auphonic.md)** -- Levelling, de-bleed, transcription -- and where the key lives.
* **[Multitrack: several speakers, several cameras](docs/multitrack.md)** -- One track per speaker, several cameras, one time axis.
* **[Speaker statistics, camera cut, EDL](docs/camera-cut.md)** -- How the first cut is proposed, and the numbers it is judged by.
* **[DaVinci Resolve](docs/resolve.md)** -- The project that comes out: timelines, tracks, colour, render.
* **[All switches](docs/command-line.md)** -- Every command line switch, with what it does.
* **[Inside the script](docs/internals.md)** -- How the one file is put together, and where the German lives.

The whole contents: **[docs/README.md](docs/README.md)**.

## What the script does not do

It does not cut and it decides nothing. The camera cut is a suggestion. The
script makes sure that at the start of the real work everything is where it
belongs -- and says so when something does not fit, before an hour has gone
into the wrong edit.

## Licence

MIT -- see `LICENSE`. Use it, change it, pass it on; keep the copyright
notice with it. What the program leans on and under which terms is listed
in `THIRD-PARTY.md`.
