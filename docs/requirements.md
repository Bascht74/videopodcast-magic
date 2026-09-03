# What it needs

*Auf Deutsch: [requirements.de.md](requirements.de.md). Back to the
[contents](README.md).*

## Getting the program

Two ways lead in, and the [README](../README.md#getting-it) holds the
command for each.

**Fetched**: take the one file `videopodcast_magic.py`, start it with
`python3`, and there is nothing else to install. Good for a first
look, for a machine you sit at once, and for a copy kept beside the
material it belongs to.

**Installed**: the command
`pip3 install git+https://github.com/Bascht74/videopodcast-magic` puts
the program into this Python and leaves the command
`videopodcast-magic` behind, callable out of any folder. The same
command with `-U` brings the newer version. Good where the program is
used every week.

Where `pip3 install` refuses and says the environment is externally
managed, this Python belongs to a package manager -- Homebrew's, or a
Linux distribution's -- and the refusal names `pipx`. That is the
right answer: `pipx` on the same address puts the program in an
environment of its own and the command on the path.

Either way Python 3.10 or newer has to be there first. That is the one
thing the program cannot bring.

Everything else the program fetches when it needs it, and says so
while it does:

* `numpy` and `PySide6` at the first start, over pip. `PySide6` is the
  big one: about 250 MB on Windows and Linux, about 440 MB on macOS.
* `ffmpeg` and `ffprobe` when they are missing -- over the package
  manager of this system, and only when that is allowed. On no other
  route. The section below says how.
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
then next to itself. When they are still missing it names the package
manager of this machine and asks before it runs it -- never unasked,
because a package manager writes outside the program, into what the
machine owner keeps:

* **macOS:** `brew`.
* **Linux:** `apt-get`, `dnf`, `zypper` or `pacman`, with `sudo` in
  front.
* **Windows:** Windows brings no package manager, so the program
  offers to open ffmpeg.org. The folder with `ffmpeg.exe` then goes
  into PATH, or the files next to the program.
* **When nothing gets installed:** the program stops and says what to
  do on this machine -- `brew install ffmpeg` on macOS, on Windows the
  build from ffmpeg.org and its folder into PATH, on Linux the package
  manager of the distribution. Answering the question with no ends the
  run the same way. The program brings no ffmpeg of its own: what it
  needs has to be on the machine, and whoever has not got it fetches
  it once, by hand.

A question needs somebody to answer it, so it is only put where the
run has a terminal in front of it. Started without one, the program
asks nothing and ends the way the last point above describes.

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
  `videopodcast_magic.py` instead.
* **`videopodcast-magic` is not a known command after the install.**
  pip put the command into a folder that is not on the search path.
  Put that folder on the path, or reach the program through Python
  instead: `python3 -m videopodcast_magic` needs no command of its own
  and takes the same switches.

That is everything the program needs. What the window then shows, tab
by tab, is in [The interface](interface.md).
