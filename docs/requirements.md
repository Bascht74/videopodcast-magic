# What it needs

*Auf Deutsch: [requirements.de.md](requirements.de.md). Back to the [contents](README.md).*

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

`ffmpeg` and `ffprobe` are needed: first on the search path, then next to
the script; where both are missing the script fetches `static-ffmpeg`. The
interface needs `PySide6` (Qt), the measurements `numpy`. What is missing
is installed at start over pip -- only Python has to be there already.
`requirements.txt` holds the two packages for anyone who would rather
install them beforehand or into a virtual environment.

## Platforms

Platforms: macOS and Windows are the ones this is used on. Linux works,
with two limits -- the key cannot be stored (no Keychain, no Registry), so
it has to come from `AUPHONIC_TOKEN` each time, and the cache goes to
`XDG_CACHE_HOME`. Where a package manager marks the Python installation as
externally managed, install the two packages yourself, in a virtual
environment or with your distribution's packages.
