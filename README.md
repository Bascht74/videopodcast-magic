# Video Podcast Magic

*Auf Deutsch: [README.de.md](README.de.md)*

![The main window: the files of one production](docs/images/files.png)

*The main window. What was found, what belongs together, and what does
not fit -- before anything is written.*

*Working on the program, or opening a pull request? [CONTRIBUTING.md](CONTRIBUTING.md) says how: the tests, the counter-proof every check owes, and what a pull request has to carry.*

**Version 3.0.0b0.** It does the work it was written for, every week, on
real material. The step to 3 is a break rather than a heap of new
features: the program is installed now, with pip3, and it is a command
called `videopodcast-magic`. Anything that still starts it as a file
has to be written once more. The format of the project file
may still change, and an older file is refused with a clear message
rather than half read.

`videopodcast-magic` -- put processed audio into video files as the
first audio track, and build from it everything the edit needs afterwards:
the cameras on one time axis, a first cut by speaker, and a DaVinci Resolve
project.

One Python file, about 40 000 lines. That one file is the whole
program, and there is nothing to build: pip makes a package of it and
puts the command on the path.

## Why this exists

Every episode began with the same hour of handwork. The recorder splits
a take at two gigabytes, so one interview arrives as three files. Sound
and picture do not start together, and by the end of the hour the lips
are off by a tenth of a second, because camera and recorder each run on
their own quartz. Then the good audio has to go into every camera file,
every speaker has to be told apart from the others, and somebody has to
decide which camera to be on while each of them talks.

None of that is editing. It is the work before the editing, it is the
same work every week, and a machine can measure it better than a person
can guess it -- so the machine does it, and the hour goes into the cut
instead.

It was written for one podcast and does that job every week. It does not
decide: the camera cut is a proposal, and the edit stays yours. The story
of one run, from the files on the disk to the finished Resolve project,
is in **[docs/overview.md](docs/overview.md)**.

## Getting it

One command, and there is no second way in:

```
pip3 install git+https://github.com/Bascht74/videopodcast-magic
videopodcast-magic
```

The newer version comes on the same address and takes the place of the
one installed:

```
pip3 install -U git+https://github.com/Bascht74/videopodcast-magic
```

**Wait for the first one. It takes minutes, and it is meant to.**
Everything the program needs in Python comes with it in that one go --
the window, the measurements, the certificates, the speech recognition
-- so nothing gets fetched behind your back later and nothing is
missing when the window first opens. Measured on 4 September 2026 on a
Mac: five minutes, 498 MB down the line, 1.4 GB on the disk. Nearly
all of it is the window: `PySide6` alone comes in a piece of 332 MB,
which is what a first install looks like when it seems to be hanging.
Every `-U` after that is seconds -- twelve, measured, where the version
had not moved -- because pip reads the repository, compares the version
and stops where it is already the one installed.

**Where `pip3 install` refuses**, saying the environment is externally
managed, this Python belongs to a package manager -- Homebrew's, or a
Linux distribution's -- which keeps pip out of what it maintains, and
the refusal names the way round it:
`pipx install git+https://github.com/Bascht74/videopodcast-magic` puts
the program in an environment of its own and the command on the path.

Two things pip cannot bring, because neither is Python: **Python
itself**, 3.10 or newer, and **`ffmpeg` with `ffprobe`**. For the two
tools the program looks on the search path, offers the package manager
of the machine and asks before it runs it, and otherwise says where to
fetch them.

**One trap, measured on 4 September 2026.** A pip that reads the
project file stops below Python 3.10 and says which version it wanted.
The pip macOS brings with its own Python 3.9 -- `/usr/bin/pip3` --
reads nothing: it answers `Successfully installed UNKNOWN-0.0.0` and
leaves an empty folder of that name, no command and no error. Reading
`UNKNOWN` means the pip is the wrong one; install Python 3.10 or newer
and use its `pip3`.

Later, and only when somebody wants what they are for, it fetches two
more: the environment the speaker separation runs in, and its model.

**About the model.** The separation reads it from a folder beside the
program -- no account, no token, and after the one download no network.
The program fetches it from its own repository, holds every file
against its checksum, and puts it there. It fetches the model only the
first time.

## Getting started

```
videopodcast-magic                          interface
videopodcast-magic AUDIO.wav VIDEO.mov
videopodcast-magic AUDIO.wav                join only
videopodcast-magic AUDIO.wav *.mov --out Done
videopodcast-magic VIDEO.mov                takes the camera sound
videopodcast-magic --lang de|en             language of the messages
videopodcast-magic --help                   all switches
```

Where pip put the command somewhere the search path does not reach,
`python3 -m videopodcast_magic` stands in place of the command in every
one of those lines and takes the same switches.

Without arguments the interface opens. Files are told apart by extension;
the order does not matter. `--lang de` or `--lang en` fixes the language;
without it the system locale decides. Only `--help` stays English.

![The assignment tab](docs/images/assignment.png)

*Which recording belongs to which camera, and what becomes of each
camera.*

## What it needs

Python 3.10 or newer, and `ffmpeg` and `ffprobe` on the search path.
That is the whole list: everything else is a Python package, every one
of them stands on the list pip reads, and the install brings them all.
ffmpeg is the exception it cannot help being, since it is not Python
-- the program brings none of its own, offers the system's package
manager and asks first, and otherwise says where to get it. macOS and
Windows are what this is used on; Linux works with two limits.

The detail, including which Python is recommended and what differs per
platform, is in **[docs/requirements.md](docs/requirements.md)**.

## The manual

* **[What it needs](docs/requirements.md)**: the one command that
  installs it, Python, ffmpeg, and what differs per platform.
* **[The interface](docs/interface.md)**: the window, tab by tab -- and
  what to do when there is no timecode.
* **[Preflight](docs/preflight.md)**: what is checked before a run
  starts, and what each complaint means.
* **[Channels: one track or two?](docs/channels.md)**: how a stereo pair
  is told apart from two separate microphones. Measured, not guessed.
* **[The simple path](docs/simple-path.md)**: one audio file, one camera
  -- the shortest way through.
* **[Processing at auphonic.com](docs/auphonic.md)**: levelling,
  de-bleed, transcription -- and where the key lives.
* **[Multitrack: several speakers, several cameras](docs/multitrack.md)**:
  one track per speaker, several cameras, one time axis.
* **[Speech recognition and speaker separation](docs/speech.md)**: what
  is said and who says it, worked out on this machine.
* **[Speaker statistics, camera cut, EDL](docs/camera-cut.md)**: how the
  first cut is proposed, and the numbers it is judged by.
* **[DaVinci Resolve](docs/resolve.md)**: the project that comes out --
  timelines, tracks, colour, render.
* **[All switches](docs/command-line.md)**: every command line switch,
  with what it does.

The whole contents: **[docs/README.md](docs/README.md)**.

## Further information and technical detail

Beside the manual stand the documents for whoever changes the program
rather than uses it. They are English only.

**[Inside the script](development/internals.md)** says how the one
file is put together and how each step works. **[What was
measured](development/measurements.md)** holds the evidence behind
the numbers: hit rates, run times, distributions, comparisons.
**[Coding guidelines](development/coding_guidelines.md)** says how
the code is written, and why. All three are in `development/`.

**[CHANGELOG.md](CHANGELOG.md)** says what changed in each version, from
0.1.0. **[THIRD-PARTY.md](THIRD-PARTY.md)** lists what the program leans
on at run time and under which terms, the speaker model included.
**[CLAUDE.md](CLAUDE.md)** holds the project rules, the ones that are
not negotiable among them; Claude Code reads it by itself at the start
of a session.

## What the script does not do

It does not cut and it decides nothing. The camera cut is a suggestion. The
script makes sure that at the start of the real work everything is where it
belongs -- and says so when something does not fit, before an hour has gone
into the wrong edit.

## Licence

MIT -- see `LICENSE`. Use it, change it, pass it on; keep the copyright
notice with it. What the program leans on and under which terms is listed
in `THIRD-PARTY.md`.
