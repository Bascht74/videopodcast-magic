# The manual

*Auf Deutsch: [README.de.md](README.de.md). Back to the
[project](../README.md).*

Eleven chapters, in the order the program does things. Each one stands on
its own; nothing here has to be read from front to back.

## Contents

* **[What it needs](requirements.md)**: Python, ffmpeg, the two
  packages, and what differs per platform.
* **[The interface](interface.md)**: the window, tab by tab -- and what
  to do when there is no timecode.
* **[Preflight](preflight.md)**: what is checked before a run starts,
  and what each complaint means.
* **[Channels: one track or two?](channels.md)**: how a stereo pair is
  told apart from two separate microphones. Measured, not guessed.
* **[The simple path](simple-path.md)**: one audio file, one camera --
  the shortest way through.
* **[Processing at auphonic.com](auphonic.md)**: levelling, de-bleed,
  transcription -- and where the key lives.
* **[Multitrack: several speakers, several cameras](multitrack.md)**:
  one track per speaker, several cameras, one time axis.
* **[Speech recognition and speaker separation](speech.md)**: what is
  said and who says it, worked out on this machine.
* **[Speaker statistics, camera cut, EDL](camera-cut.md)**: how the
  first cut is proposed, and the numbers it is judged by.
* **[DaVinci Resolve](resolve.md)**: the project that comes out --
  timelines, tracks, colour, render.
* **[All switches](command-line.md)**: every command line switch, with
  what it does.

The [overview](overview.md) is not a chapter: it covers the same ground
in a few pages, for anyone deciding whether this program is for them.

## Index

Each entry names its chapter and the section in it. The section that
explains the word comes first.

* **3:1 rule**: `preflight`, "How the report measures bleed against the 3:1
  rule"
* **API key**: `auphonic`, "The key and the preset"; `interface`, "What
  Settings ... holds"
* **Apple Log**: `resolve`, "How Apple Log survives the rewrite"
* **as a track (tick)**: `multitrack`, "Making camera sound a track"
* **assignment**: see belongs to
* **belongs to (selector)**: `multitrack`, "Setting the assignment";
  `simple-path`, "Putting blocks together by hand"
* **bleed**: `preflight`, "How the report measures bleed against the 3:1
  rule"; `camera-cut`, "Measuring the speakers without Auphonic"
* **block**: `simple-path`, "What goes into the video beside the mix";
  `simple-path`, "Putting blocks together by hand"
* **camera audio**: `multitrack`, "Making camera sound a track";
  `simple-path`, "What comes back for each video file"
* **channel, used or not**: `channels`, "Which channels become tracks at
  all"
* **clip-on microphone**: `channels`, "One track or two"; `multitrack`,
  "Making camera sound a track"
* **clock drift**: `overview`, "What it takes off your hands";
  `command-line`, "What happens to audio and picture"
* **colour comparison**: `camera-cut`, "What the metrics and the colour
  comparison measure"
* **colour group**: `resolve`, "Grading a whole camera at once"
* **`colr`**: `resolve`, "Keeping the colour of the source"
* **credit**: `auphonic`, "When the production already exists"
* **cut band**: `camera-cut`, "Reading the cut band and the legend"
* **de-bleed**: `auphonic`, "Working without Auphonic"; `preflight`, "How
  the report measures bleed against the 3:1 rule"
* **drop frame**: `resolve`, "The button and the two timelines"
* **dry run**: `interface`, "The four tabs"
* **Edit Change Delay**: `camera-cut`, "Setting the knobs"
* **EDL**: `camera-cut`, "How the cut comes about"
* **envelope**: `interface`, "The four tabs"; `multitrack`, "Running several
  files at once"
* **faster-whisper**: `speech`, "How the program writes the text down"
* **ffmpeg**: `requirements`, "Where ffmpeg, PySide6 and numpy come from"
* **ffplay**: `interface`, "The four tabs"
* **follow-up file**: `simple-path`, "What goes into the video beside the
  mix"; `interface`, "The four tabs"
* **frame rate, variable**: `preflight`, "What the report says about a
  variable frame rate"
* **Full-Mix**: `multitrack`, "What goes into the camera files"; `resolve`,
  "The button and the two timelines"
* **handover file (`_resolve.json`)**: `camera-cut`, "What the project file
  keeps"
* **HDR**: `resolve`, "HDR: what has to be in the file"; `resolve`, "What
  the render job sets"
* **`--hdr-check`**: `resolve`, "HDR: what has to be in the file"
* **In point**: `multitrack`, "Setting the time window"; `interface`, "The
  four tabs"
* **intro**: `resolve`, "Setting intro and outro"; `multitrack`, "Setting
  the assignment"
* **Keychain**: `auphonic`, "The key and the preset"; `requirements`, "What
  differs per platform"
* **keys**: `interface`, "Reaching everything by menu or key"
* **legend**: `camera-cut`, "Reading the cut band and the legend"
* **leveler**: `preflight`, "Which loudness target holds"; `auphonic`,
  "Working without Auphonic"
* **log (`videopodcast-magic.log`)**: `interface`, "The four tabs"
* **loudness range**: `preflight`, "Which loudness target holds"
* **loudness target (LUFS)**: `preflight`, "Which loudness target holds";
  `command-line`, "Basics"
* **marks ✓ ! ✕**: `interface`, "The four tabs"; `preflight`, "What is
  checked"
* **Measure speakers now (button)**: `camera-cut`, "Measuring the speakers
  without Auphonic"
* **metrics (`_metrics.csv`)**: `camera-cut`, "What the metrics and the
  colour comparison measure"
* **Minimum Edit Duration**: `camera-cut`, "Setting the knobs"
* **model (speaker separation)**: `requirements`, "Getting the program";
  `speech`, "Separating the speakers"
* **mono fold**: `channels`, "Stereo stays stereo"
* **MOV**: `simple-path`, "Why the target is always MOV"
* **multicam clip**: `resolve`, "When Resolve is to cut for itself";
  `resolve`, "Choosing the multicam audio"
* **Node Sizing**: `resolve`, "Setting position and zoom for a whole camera"
* **offset**: `camera-cut`, "How the preview players choose file and sound";
  `simple-path`, "What goes into the video beside the mix"
* **Out point**: see In point
* **outro**: `resolve`, "Setting intro and outro"
* **package manager**: `requirements`, "Where ffmpeg, PySide6 and numpy come
  from"
* **player, preview**: `interface`, "The four tabs"; `camera-cut`, "How the
  preview players choose file and sound"
* **preflight**: `preflight`, "What is checked"
* **preset**: `auphonic`, "The key and the preset"; `preflight`, "What is
  checked"
* **project file**: `camera-cut`, "What the project file keeps";
  `interface`, "How the time axis is built without timecode"
* **PySide6**: `requirements`, "Where ffmpeg, PySide6 and numpy come from"
* **raw recording (level)**: `camera-cut`, "How the preview players choose
  file and sound"
* **reaction cut**: `camera-cut`, "Setting the knobs"
* **Remove (button)**: `simple-path`, "Putting blocks together by hand";
  `multitrack`, "Running several files at once"
* **render job**: `resolve`, "What the render job sets"
* **samples on the stop**: `preflight`, "How the report counts the samples
  on the stop"
* **sentence boundary**: `camera-cut`, "How the program places the wide
  shot"; `speech`, "What the text is for"
* **Settings ...**: `interface`, "What Settings ... holds"
* **Source Audio Channels**: `resolve`, "Choosing the multicam audio"
* **speaker name**: `multitrack`, "Setting the assignment"; `speech`,
  "Naming the voices"
* **speaker separation**: `speech`, "Separating the speakers"
* **Speaks at least**: `camera-cut`, "Setting the knobs"
* **`start_s`**: `camera-cut`, "How the preview players choose file and
  sound"
* **static-ffmpeg**: `requirements`, "Where ffmpeg, PySide6 and numpy come
  from"
* **stereo track**: `channels`, "Stereo stays stereo"; `preflight`, "Which
  loudness target holds"
* **time axis**: `interface`, "How the time axis is built without timecode";
  `multitrack`, "What Multitrack does"
* **time window**: `multitrack`, "Setting the time window"
* **timecode, virtual**: `interface`, "How the time axis is built without
  timecode"
* **transcript**: `auphonic`, "Fetch transcript"; `speech`, "How the program
  writes the text down"
* **update**: `interface`, "Keeping itself up to date"
* **voice**: `speech`, "Naming the voices"
* **wide shot**: `camera-cut`, "How the program places the wide shot";
  `camera-cut`, "How the cut comes about"
* **working without Auphonic**: `auphonic`, "Working without Auphonic"

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
