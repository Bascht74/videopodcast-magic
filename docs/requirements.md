# What it needs

*Auf Deutsch: [requirements.de.md](requirements.de.md). Back to the
[contents](README.md).*

## Getting the program

One file, and nothing else to install: fetch `videopodcast-magic.py`
and start it. The command is in the [README](../README.md#getting-it).
Python 3.10 or newer has to be there first. That is the one thing the
program cannot bring.

Everything else the program fetches when it needs it, and says so
while it does:

* `numpy` and `PySide6` at the first start, over pip. `PySide6` is the
  big one: about 250 MB on Windows and Linux, about 440 MB on macOS.
* `ffmpeg` and `ffprobe` when they are missing, over the package
  manager. The section below says how.
* The environment the speaker separation runs in, about 218 MB, the
  first time a separation is asked for.
* The model for the separation, about 33 MB, right after it.
* The number of the newest version, from github.com, a moment after
  the window is up. The program sends nothing while it asks, and it
  fetches that version only when somebody says so.
  [The interface](interface.md#keeping-itself-up-to-date) says what
  happens then.

**The model.** Telling the voices on a recording apart is the speaker
separation, and it needs a trained model. The program fetches it from
its own repository into the folder `models/` beside the program. It
holds every file against its SHA-256 checksum and writes only what
matches.

The separation then reads the model from that folder, without an
account, a token or a network. The program fetches it only the first
time.

## Which Python the program needs

3.10 or newer, and the program says so and stops below that. The floor
is what the interface needs: PySide6 does not build below 3.10. The
test suite runs on 3.14.7, the version this is used on daily. It
covers 3.14.7 only; anything between it and 3.10 is not measured.

`--version`, the header of the log and the first line of every run say
which Python is running. They name the recommended one when it is
another: `Python 3.11.15  (recommended version 3.14.7)`. `--help` and
`--version` answer without `numpy`, `PySide6` and `ffmpeg`.

![A run in the terminal](images/terminal.png)

*The first line names version and Python, below it stands the path of
the running file. This Python is the recommended one, so no bracket
follows.*

## Where ffmpeg, PySide6 and numpy come from

The program looks for `ffmpeg` and `ffprobe` first on the search path,
then next to itself. When both are missing it names the package
manager of this machine and asks before it runs it:

* **macOS:** `brew`.
* **Linux:** `apt-get`, `dnf`, `zypper` or `pacman`, with `sudo` in
  front.
* **Windows:** Windows brings no package manager, so the program
  offers to open ffmpeg.org. The folder with `ffmpeg.exe` then goes
  into PATH, or the files next to the program.
* **When nothing gets installed:** `static-ffmpeg` is the last
  resort, a build inside this Python. The program fetches it when this
  machine has no package manager, and when the one it has does not
  deliver. Answering the question with no counts as that. It pulls
  sixteen packages in behind it, and its 50 MB build comes from a
  private repository, checked against nothing.

The interface needs `PySide6` (Qt), the measurements `numpy`. The
program installs what is missing at start over pip. Only Python has to
be there already. `requirements.txt` holds the two packages for anyone
who would rather install them beforehand or into a virtual
environment.

When a package manager marks the Python installation as externally
managed, the program installs the two packages around it and says so.
To stay out of the manager's way, install the two packages yourself
beforehand, in a virtual environment or with your distribution's
packages.

## What differs per platform

Day to day the program runs on macOS and Windows. On Linux it runs as
well, with two limits:

* The key cannot be stored (no Keychain, no Registry), so it has to
  come from `AUPHONIC_TOKEN` each time.
* The cache goes to `XDG_CACHE_HOME`.

## When something goes wrong

* **The program stops and names the Python version.** This Python is
  older than 3.10. Install a newer one and start again.
* **pip cannot install `numpy` or `PySide6`.** The last lines of pip
  say why. Install both yourself with `pip install numpy PySide6`,
  best into a virtual environment.
* **`ffmpeg` is still not found after the install.** The folder with
  `ffmpeg` is not on the search path. Put the two files next to
  `videopodcast-magic.py` instead.

That is everything the program needs. What the window then shows, tab
by tab, is in [The interface](interface.md).
