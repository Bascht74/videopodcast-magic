# What it needs

*Auf Deutsch: [requirements.de.md](requirements.de.md). Back to the
[contents](README.md).*

## Getting the program

One command installs it, and there is no second way in:

```
pip3 install git+https://github.com/Bascht74/videopodcast-magic
```

It leaves the command `videopodcast-magic` behind, callable out of any
folder. Everything the program needs in Python comes with it in that
one go: `PySide6` for the window, `numpy` for the measurements,
`certifi` for the authorities an https connection is checked against,
`faster-whisper` for the speech recognition on a system that brings
none. Nothing gets fetched behind anybody's back afterwards, and
nothing is missing when the window opens for the first time.

**That first command takes minutes, and the wait is those packages.**
Measured on 4 September 2026, on a Mac with an empty cache: five
minutes, 498 MB fetched and 1.4 GB on the disk afterwards. Nearly all
of it is the window -- `PySide6` alone is 443 MB of the download, in
two pieces of 332 and 111 MB, and 1.2 GB unpacked. On a fast line it
is over sooner; on a slow one it is not stuck, it is fetching the
piece of 332 MB.

**The newer version comes on the same address, and that one is
seconds:**

```
pip3 install -U git+https://github.com/Bascht74/videopodcast-magic
```

No package registry stands in between: the address is the repository
itself, and pip reads it afresh each time, compares the version there
with the one installed, and leaves everything alone where the two are
the same. Measured the same day: twelve seconds for a `-U` that found
nothing newer, and not one package touched.

Where `pip3 install` refuses and says the environment is externally
managed, this Python belongs to a package manager -- Homebrew's, or a
Linux distribution's -- which keeps pip out of what it maintains, and
the refusal names the way round it: `pipx install` on the same address
puts the program in an environment of its own and the command on the
path.

Two things have to be on the machine before that command, because pip
can bring neither:

* **Python 3.10 or newer, and its pip.** A pip that reads the project
  file stops below 3.10 and names the version it wanted. **The pip
  macOS brings with its own Python 3.9 reads nothing and says nothing
  is wrong**: measured on 4 September 2026, `/usr/bin/pip3` --
  pip 21.2.4 -- answered `Successfully installed UNKNOWN-0.0.0` and
  left behind an empty folder of that name. No module, no command, no
  error. **Reading `UNKNOWN` means the pip is the wrong one**, and the
  answer is to install Python 3.10 or newer and use its `pip3`.
* **`ffmpeg` and `ffprobe`.** They are not Python and no list pip
  reads can name them. [Where ffmpeg comes
  from](#where-ffmpeg-comes-from) says what the program does when they
  are missing.

Two more the program fetches later, and only when somebody wants what
they are for:

* The environment the speaker separation runs in, about 218 MB, the
  first time a separation is asked for.
* The model for the separation, about 33 MB, right after it.

And one it only asks after: the number of the newest version, from
github.com, a moment after the window is up. The program sends nothing
while it asks, and it fetches that version only when somebody says so.
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

3.10 or newer, and pip refuses the install below that. The floor is
what the interface needs: PySide6 does not build below 3.10. The
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

## Where ffmpeg comes from

**`ffmpeg` and `ffprobe` are the one thing pip cannot bring**, because
they are not Python and no list pip reads has a place for them. Every
other piece came with the install; these two have to be on the machine.

The program looks for them first on the search path, then next to
itself. When they are still missing it names the package
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

`requirements.txt` holds the Python packages under the same names pip
reads from `pyproject.toml`, for anyone who would rather have them in
a virtual environment before the install.

## What differs per platform

Day to day the program runs on macOS and Windows. On Linux it runs as
well, with two limits:

* The key cannot be stored (no Keychain, no Registry), so it has to
  come from `AUPHONIC_TOKEN` each time.
* The cache goes to `XDG_CACHE_HOME`.

## When something goes wrong

* **pip refuses and names a Python version.** This Python is older
  than 3.10. Install a newer one and give the same command to that
  one.
* **pip answers `Successfully installed UNKNOWN-0.0.0`.** Nothing was
  installed. This pip is too old to read the project file; on a Mac
  that is `/usr/bin/pip3`, which belongs to Python 3.9. Install
  Python 3.10 or newer and give the command to its `pip3`.
* **pip says the environment is externally managed.** This Python
  belongs to a package manager. `pipx install` on the same address is
  the way round it.
* **The install breaks off part way.** The last lines of pip say why.
  It is almost always the download of `PySide6`, the piece of 332 MB:
  give the same command again.
* **`videopodcast-magic` is not a known command afterwards.** pip put
  the command into a folder that is not on the search path. Put that
  folder on the path, or reach the program through Python instead:
  `python3 -m videopodcast_magic` needs no command of its own and
  takes the same switches.
* **`ffmpeg` is still not found after installing it.** The folder
  holding it is not on the search path. Put it there and start again.

That is everything the program needs. What the window then shows, tab
by tab, is in [The interface](interface.md).
