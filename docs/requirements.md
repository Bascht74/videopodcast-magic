# What it needs

*Auf Deutsch: [requirements.de.md](requirements.de.md). Back to the [contents](README.md).*

## Getting the program

One file, and nothing else to install: `videopodcast-magic.py` is
fetched and started. The command is in the
[README](../README.md#getting-it). Python 3.10 or newer has to be
there first -- that is the one thing the program cannot bring.

Everything else the program fetches when it needs it, and says so
while it does:

* `numpy` and `PySide6` at the first start, over pip.
* `ffmpeg` and `ffprobe` where they are missing, over the package
  manager. The section below says how.
* The environment the speaker separation runs in, about 218 MB, the
  first time a separation is asked for.
* The model for the separation, about 33 MB, right after it.

**The model.** Telling voices apart needs a trained model. The program
fetches it from its own repository into the folder `models/` beside
the program and holds every file against its SHA-256 checksum; a file
that does not match is not written. The separation then reads it from
there, without an account, a token or a network. Where the folder is
already there, nothing is fetched again.

## Python

Python: 3.10 or newer, and the program says so and stops below that. The
floor is what the interface needs -- PySide6 does not build below 3.10, so
the command line alone could go lower but the window could not. The test
suite runs on 3.14.7, the version this is used on daily. `--version`, the
header of the log and the first line of every run say which Python is
running, and name the recommended one where it is another:
`Python 3.11.15  (recommended version 3.14.7)`. `--help` and `--version`
need neither package and answer on any of them.

## ffmpeg, PySide6, numpy

`ffmpeg` and `ffprobe` are needed: first on the search path, then next
to the program. Where both are missing the program names the package
manager of this machine and asks before it runs it -- `brew` on macOS,
`apt-get`, `dnf`, `zypper` or `pacman` on Linux, on Linux with `sudo`
in front. On Windows there is no manager to ask, so it offers to open
ffmpeg.org; the folder with `ffmpeg.exe` then goes into PATH, or the
files next to the program. Only where there is no package manager is
`static-ffmpeg` fetched, a build inside this Python.

The interface needs `PySide6` (Qt), the measurements `numpy`. What is
missing is installed at start over pip -- only Python has to be there
already. `requirements.txt` holds the two packages for anyone who would
rather install them beforehand or into a virtual environment.

## Platforms

Platforms: macOS and Windows are the ones this is used on. Linux works,
with two limits -- the key cannot be stored (no Keychain, no Registry), so
it has to come from `AUPHONIC_TOKEN` each time, and the cache goes to
`XDG_CACHE_HOME`. Where a package manager marks the Python installation as
externally managed, install the two packages yourself, in a virtual
environment or with your distribution's packages.
