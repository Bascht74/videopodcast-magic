# The manual

*Auf Deutsch: [README.de.md](README.de.md). Back to the
[project](../README.md).*

Eleven chapters, in the order the program does things. Each one stands on
its own; nothing here has to be read from front to back.

## Contents

* **[What it needs](requirements.md)**: the one command that installs
  it, Python, ffmpeg, and what differs per platform.
* **[The interface](interface.md)**: the window, tab by tab -- and how
  the common time axis is measured.
* **[Preflight](preflight.md)**: what is checked before a run starts,
  and what each complaint means.
* **[Channels: one track or two?](channels.md)**: how a stereo pair is
  told apart from two separate microphones. Measured, not guessed.
* **[The simple path](simple-path.md)**: one audio file, one camera --
  the shortest way through.
* **[Processing at auphonic.com](auphonic.md)**: levelling, de-bleed,
  noise removal -- and where the key lives.
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

* **360 degree camera**: `resolve`, "One camera"; `simple-path`, "Telling
  the speakers apart on one track"
* **3:1 rule**: `preflight`, "How the report measures bleed against the 3:1
  rule"
* **API key**: `auphonic`, "The key and the preset"; `interface`, "What
  Settings ... holds"
* **Apple Log**: `resolve`, "How Apple Log survives the rewrite"
* **assignment**: see belongs to
* **belongs to (selector)**: `multitrack`, "Setting the assignment";
  `simple-path`, "Putting blocks together by hand"
* **bleed**: `preflight`, "How the report measures bleed against the 3:1
  rule"; `camera-cut`, "Measuring the speakers without Auphonic"
* **block**: `simple-path`, "What goes into the video beside the mix";
  `simple-path`, "Putting blocks together by hand"
* **camera audio**: `multitrack`, "Making camera sound a track";
  `simple-path`, "What comes back for each video file";
  `interface`, "The four tabs"
* **camera, only one**: `resolve`, "One camera"; `camera-cut`, "Cutting when
  one camera shows everybody"
* **channel, used or not**: `channels`, "Which channels become tracks at
  all"
* **clip-on microphone**: `channels`, "One track or two"; `multitrack`,
  "Making camera sound a track"
* **clock drift**: `overview`, "What it takes off your hands";
  `command-line`, "What happens to audio and picture"; `interface`,
  "The four tabs"
* **colour comparison**: `camera-cut`, "What the metrics and the colour
  comparison measure"
* **colour group**: `resolve`, "Grading a whole camera at once"
* **`colr`**: `resolve`, "Keeping the colour of the source"
* **credit**: `auphonic`, "When the production already exists"
* **cut band**: `camera-cut`, "Reading the cut band and the legend"
* **cut basis (the line under the preview)**: `interface`, "The four
  tabs"
* **Cut with the wide shot (box)**: `camera-cut`, "How the cut comes about"
* **de-bleed**: `auphonic`, "Working without Auphonic"; `preflight`, "How
  the report measures bleed against the 3:1 rule"
* **drop frame**: `resolve`, "The button and the two timelines"
* **dry run**: `interface`, "The four tabs"; `speech`, "What the dry run
  shows of the speakers"
* **Edit Change Delay**: `camera-cut`, "Setting the knobs"
* **EDL**: `camera-cut`, "How the cut comes about"
* **envelope**: `interface`, "The four tabs"; `multitrack`, "Running several
  files at once"
* **faster-whisper**: `speech`, "How the program writes the text down"
* **ffmpeg**: `requirements`, "Where ffmpeg comes from"
* **ffplay**: `interface`, "The four tabs"
* **First cut by speaker (box)**: `camera-cut`, "How the cut comes about";
  `interface`, "The four tabs"
* **follow-up file**: `simple-path`, "What goes into the video beside the
  mix"; `interface`, "The four tabs"
* **frame rate, mixed**: `resolve`, "Cameras that run at different
  speeds"; `preflight`, "What is checked"
* **frame rate, variable**: `preflight`, "What the report says about a
  variable frame rate"
* **Full-Mix**: `multitrack`, "What goes into the camera files"; `resolve`,
  "The button and the two timelines"; `simple-path`, "What comes back for
  each video file"
* **GENERAL NOTES (row in the file list)**: `preflight`, "What is checked"
* **handover file (`_resolve.json`)**: `camera-cut`, "What the project file
  keeps"
* **HDR**: `resolve`, "HDR: what has to be in the file"; `resolve`, "What
  the render job sets"
* **`--hdr-check`**: `resolve`, "HDR: what has to be in the file"
* **ignore this video**: `interface`, "How the time axis is measured";
  `multitrack`, "When something goes wrong"; `simple-path`, "When
  something goes wrong"
* **In point**: `multitrack`, "Setting the time window"; `interface`, "The
  four tabs"
* **input track**: `multitrack`, "Setting the assignment"; `interface`, "The
  four tabs"
* **intro**: `resolve`, "Setting intro and outro"; `multitrack`, "Setting
  the assignment"
* **Keychain**: `auphonic`, "The key and the preset"; `requirements`, "What
  differs per platform"
* **keys**: `interface`, "Reaching everything by menu or key"
* **Kind (column)**: `interface`, "The four tabs"; `camera-cut`, "How the
  program places the wide shot"
* **legend**: `camera-cut`, "Reading the cut band and the legend"
* **leveler**: `preflight`, "Which loudness target holds"; `auphonic`,
  "Working without Auphonic"
* **log (`videopodcast-magic.log`)**: `interface`, "The four tabs"
* **loudness range**: `preflight`, "Which loudness target holds"
* **loudness target (LUFS)**: `interface`, "The four tabs"; `preflight`,
  "Which loudness target holds";
  `command-line`, "Basics"
* **marker**: `resolve`, "One camera"; `resolve`, "The button and the two
  timelines"
* **marks ✓ ! ✕**: `interface`, "The four tabs"; `preflight`, "What is
  checked"
* **metrics (`_metrics.csv`)**: `camera-cut`, "What the metrics and the
  colour comparison measure"
* **Minimum Edit Duration**: `camera-cut`, "Setting the knobs"
* **model (speaker separation)**: `requirements`, "Getting the program";
  `speech`, "Separating the speakers"
* **mono fold**: `channels`, "Stereo stays stereo"
* **MOV**: `simple-path`, "Why the target is always MOV"
* **multicam clip**: `resolve`, "When Resolve is to cut for itself";
  `resolve`, "Choosing the multicam audio"
* **Nobody speaks**: `camera-cut`, "Setting the knobs"; `camera-cut`,
  "When the speech does not say whom to show"
* **Node Sizing**: `resolve`, "Setting position and zoom for a whole camera"
* **offset**: `camera-cut`, "How the preview players choose file and sound";
  `simple-path`, "What goes into the video beside the mix"; `resolve`,
  "Where each camera sits"
* **Out point**: see In point
* **outro**: `resolve`, "Setting intro and outro"
* **package manager**: `requirements`, "Where ffmpeg comes from"
* **pip, pipx (installing)**: `requirements`, "Getting the program"
* **`placed_by` (handover file)**: `resolve`, "Where each camera sits"
* **player, preview**: `interface`, "The four tabs"; `camera-cut`, "How the
  preview players choose file and sound"; `camera-cut`, "What the picture
  says"
* **preflight**: `preflight`, "What is checked"
* **preset**: `auphonic`, "The key and the preset"; `preflight`, "What is
  checked"
* **project file**: `camera-cut`, "What the project file keeps";
  `interface`, "How the time axis is measured"
* **PySide6**: `requirements`, "Getting the program"
* **raw recording (level)**: `camera-cut`, "How the preview players choose
  file and sound"
* **reaction cut**: `camera-cut`, "Setting the knobs"
* **read back**: `speech`, "What is kept, and what is worked out again"
* **Remove (button)**: `simple-path`, "Putting blocks together by hand";
  `multitrack`, "Running several files at once"
* **render job**: `resolve`, "What the render job sets"
* **samples on the stop**: `preflight`, "How the report counts the samples
  on the stop"
* **sentence boundary**: `camera-cut`, "How the program places the wide
  shot"; `speech`, "What the text is for"
* **Settings ...**: `interface`, "What Settings ... holds"
* **Short gap up to**: `camera-cut`, "Setting the knobs"
* **Source Audio Channels**: `resolve`, "Choosing the multicam audio"
* **speaker name**: `multitrack`, "Setting the assignment"; `speech`,
  "Naming the voices"
* **speaker separation**: `speech`, "Separating the speakers";
  `simple-path`, "Telling the speakers apart on one track"
* **Speaks at least**: `camera-cut`, "Setting the knobs"
* **stages of a run (bar beside Start)**: `interface`, "The four tabs"
* **`start_s`**: `camera-cut`, "How the preview players choose file and
  sound"
* **stereo track**: `channels`, "Stereo stays stereo"; `preflight`, "Which
  loudness target holds"
* **time axis**: `interface`, "How the time axis is measured";
  `multitrack`, "What Multitrack does"
* **time window**: `multitrack`, "Setting the time window"; `multitrack`,
  "How much of each camera is written"
* **timecode, virtual**: `interface`, "How the time axis is measured"
* **transcript**: `speech`, "How the program writes the text down";
  `auphonic`, "The transcript is made here"
* **update**: `interface`, "Keeping itself up to date"
* **voice**: `speech`, "Naming the voices"
* **wide shot**: `camera-cut`, "How the program places the wide shot";
  `camera-cut`, "How the cut comes about"; `camera-cut`, "What the picture
  says"
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
