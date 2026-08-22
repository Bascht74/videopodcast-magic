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
* **[Speaker statistics, camera cut, EDL](camera-cut.md)** -- How the first cut is proposed, and the numbers it is judged by.
* **[DaVinci Resolve](resolve.md)** -- The project that comes out: timelines, tracks, colour, render.
* **[All switches](command-line.md)** -- Every command line switch, with what it does.
* **[Inside the script](internals.md)** -- How the one file is put together, and where the German lives.

Two more documents that are not part of the manual:

* **[Overview](overview.md)** -- the same ground in a few pages, for
  anyone deciding whether this program is for them.
* **[Coding guidelines](coding_guidelines.md)** -- how the code is
  written, and why. For anyone changing it.
