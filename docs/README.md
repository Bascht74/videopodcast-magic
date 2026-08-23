# The manual

*Auf Deutsch: [README.de.md](README.de.md). Back to the
[project](../README.md).*

Eleven chapters, in the order the program does things. Each one stands on
its own; nothing here has to be read from front to back.

## Contents

* **[What it needs](requirements.md)** -- Python, ffmpeg, the two packages, and what differs per platform.
* **[The interface](interface.md)** -- The window, tab by tab -- and what to do when there is no timecode.
* **[Preflight](preflight.md)** -- What is checked before a run starts, and what each complaint means.
* **[Channels: one track or two?](channels.md)** -- How a stereo pair is told apart from two separate microphones. Measured, not guessed.
* **[The simple path](simple-path.md)** -- One audio file, one camera: the shortest way through.
* **[Processing at auphonic.com](auphonic.md)** -- Levelling, de-bleed, transcription -- and where the key lives.
* **[Multitrack: several speakers, several cameras](multitrack.md)** -- One track per speaker, several cameras, one time axis.
* **[Speech recognition and speaker separation](speech.md)** -- What is said and who says it, worked out on this machine.
* **[Speaker statistics, camera cut, EDL](camera-cut.md)** -- How the first cut is proposed, and the numbers it is judged by.
* **[DaVinci Resolve](resolve.md)** -- The project that comes out: timelines, tracks, colour, render.
* **[All switches](command-line.md)** -- Every command line switch, with what it does.

The [overview](overview.md) is not a chapter: it covers the same ground
in a few pages, for anyone deciding whether this program is for them.

## Further information and technical detail

Beside the manual stand the documents for whoever changes the program
rather than uses it. They are English only.

They are in `development/`, next to this folder. [Inside the
script](../development/internals.md) says how the one file is put
together and how each step works. [What was
measured](../development/measurements.md) holds the evidence behind the
numbers: hit rates, run times, distributions, comparisons. [Coding
guidelines](../development/coding_guidelines.md) says how the code is
written, and why.

[CHANGELOG.md](../CHANGELOG.md) says what changed in each version, from
0.1.0. [THIRD-PARTY.md](../THIRD-PARTY.md) lists what the program leans
on at run time and under which terms, the speaker model included.
[CLAUDE.md](../CLAUDE.md) holds the project rules, the ones that are not
negotiable among them; Claude Code reads it by itself at the start of a
session.
