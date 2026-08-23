# Changelog

All notable changes to this project are documented in this file. The
format is based on [Keep a Changelog][kac], and the numbers are given
out under [Semantic Versioning][semver]. English only, unlike the
manual: this is for whoever picks the script up from a repository.

Only the two releases of 2026-08-22 carry a date. The versions below
them were numbered after the fact, and no reliable release date for them
survives.

## [2.3.0-beta] - 2026-08-23

### Added

- The model for the speaker separation is fetched the first time a
  separation is asked for, so the one Python file is all anybody has to
  download. It comes from the same repository the program does, at the
  tag of the running version, and off the `main` branch where there is
  no such tag -- a program and its model are never a version apart.
  Every file is held against the SHA-256 sums that come with it, and
  one that does not match is not written. It lands in `models/` beside
  the program and is never fetched a second time.

- `L` plays forward and doubles the speed on every press, 1x to 8x; `K`
  stops and goes back to normal. The speed stands on the play button.
  `J` is absent: measured, Qt takes a negative rate and reports 0.00
  back, and swapping the whole media backend for one key is the wrong
  trade.
- Names a reading program can announce on the first and third sheets as
  well -- the file list, the production fields, the eight cut numbers
  as "caption, seconds", the four choices, the Resolve button.

### Changed

- Nothing is asked of auphonic.com unless somebody asks for it. A key
  that was remembered used to be checked at start-up, which meant a
  start spoke to a third party about a key it had only been asked to
  keep -- and a key that had expired or been mistyped greeted its owner
  with an error box every time. The presets are fetched when the list
  is opened, which is the moment they are wanted and the only moment
  they are needed.
- A key is measured before it is sent: whether there is one, and
  whether it was pasted with a line break, a space in the middle or a
  character that cannot be typed. Not its length or its character set
  -- what a real key looks like has never been measured here, and a
  guessed format would turn away a key that works.
- The tabs lost their numbers. Numbered tabs promise an order that does
  not exist -- one may jump, and the ticks behind the names already say
  what is finished.
- `Dry run (writes nothing)` is `Dry run` on the button; the
  explanation was in the tooltip anyway.
- The trim slider takes its colours from the scheme. Measured: its
  outline against the handle 2.94 before, 5.17 light and 6.03 dark now
  -- under the 3:1 that WCAG asks of a control. On dark it no longer
  draws a white band across the window.
- `warning` is `#985508` on light, measured at 5.77 against the sheet
  where it used to fall under 4.5. Dark keeps `#e2a355`: `#985508`
  there is 2.74.
- A switch between light and dark arrives while the program runs.
  Before, the scheme was read once at start and the way back to light
  was burned in.
- The type in the "one more speaker" row is made smaller only where
  the row would otherwise grow wider than the player leaves it.
  Smaller type is harder to read, and on a machine whose system font
  was turned up it undoes what somebody set it for.

### Removed

- `install.py`. The program brings what it needs by itself -- numpy and
  PySide6 at the first start, ffmpeg over the package manager, the
  separation and its model at the first separation -- so there is one
  file to fetch and one file to keep.

### Fixed

- `as a track` was clipped in the camera table. The macOS style reports
  a checkbox narrower than its own text, and the column took that
  number: 83 px offered for text that needs 87. The room now comes from
  the style rather than from a number somebody liked.

### Tests

- `release_test.py`, new: one version number named the same in the
  program, the changelog and both READMEs; the changelog in its shape;
  every picture there and used, in both languages; and the rule that
  the key never reaches a file. Four rules that used to be enforced by
  somebody remembering them.
- `auphonic_quiet_test.py`, new: what is turned away before it is sent,
  what gets through, that no timer fetches presets at start-up, and
  that the unasked fetch opens no box.
- `preview_shot.py` and `assignment_shot.py` used to look for a tab and
  return in silence where they found none -- the script then
  photographed the wrong sheet and still returned 0. They stop and say
  which sheets there are.
- `first_run.sh --then-install` does what the manual tells a stranger
  to do: fetch the one file and start it. It used to fetch the
  installer and run that.

### Documentation

- The screenshots showed a window that exists nowhere. Taken under
  `offscreen`, Qt draws them in the Fusion style: 46 of 63 palette
  entries differ from the Mac, and the menu bar sat inside the window
  instead of at the top of the screen. They are taken under `cocoa`
  now, with the window kept off the desktop -- real style, real
  palette, exact size, nothing in anybody's way. It needs a screen
  somebody is logged in to, so the run is started by hand.
- Twenty-five places in the manual named the numbered tabs, in each
  language. All of them pulled along, four captions rebuilt where the
  number was the only thing naming the sheet.
- `docs/notes/begriffe.md`, new: which German word this project uses
  for which thing, counted rather than felt -- Spur against Track
  stands 88 to 1. Written after Tooltip had been replaced by
  Kurzhinweis and put back: Tooltip is the ordinary German word too.
- The requirements chapter says what the program fetches for itself,
  when, and how much, in both languages. It described `install.py`,
  which is gone.
- The section on ffmpeg named `static-ffmpeg` as what happens where
  ffmpeg is missing. The package manager comes first and is asked
  about; `static-ffmpeg` is the way out where there is no manager.

## [2.2.0-beta] - 2026-08-23

### Added

- A menu bar, with seventeen entries. On a Mac that is not a matter of
  taste: About, Settings and Help are expected in places the window has
  no say over, and Qt's minimal fallback carries none of them.
- Keys. The player had buttons for a frame back and forward, which is
  where anybody who edits reaches for the arrows and found nothing.
  Space plays and pauses, the arrows step a frame, with Shift a second
  and with Alt ten, I and O set the marks and Shift+I and Shift+O jump
  to them. They hang on the player rather than on the window, so a bare
  letter cannot fire while somebody is typing a name into a field.
  Everything else is on Ctrl or Command, where it cannot collide:
  Ctrl+O adds files, Ctrl+R starts, Ctrl+Shift+R is the dry run,
  Ctrl+1 to Ctrl+3 pick a sheet, Ctrl+, opens the settings.
- Seventeen controls carry a name a reading program can announce. There
  were none.
- `VPM_CACHE` points what the program keeps between runs somewhere else.
  The suite sets it, so a test run no longer leaves envelopes and
  measurements in the cache of whoever started it.

### Changed

- The reason a run cannot start stands in the window, in full. It used
  to be in the tooltip of the start button -- a tooltip cannot be
  reached with the keyboard and is not read out reliably, so the most
  important sentence in the window was the one hardest to get at.
- On the second sheet a file that does not fit is no longer red and
  nothing else: it now carries the same sentence the first sheet writes
  beside it. Colour alone carries nothing to whoever cannot tell red
  from black.
- The second sheet asked for 1800 pixels and now asks for 743, so it
  fits on a laptop. The recording name moved out of the "one more
  speaker" button into a chooser beside it.

### Fixed

- brew asked a second time despite NONINTERACTIVE. `--yes` is the
  switch that stops it; without it a run with nobody in front of it
  waited for an answer that never came.

### Tests

- `start_reason_test.py` held the old behaviour in place -- it checked
  that the footer points at the tooltip, which was the defect. It now
  checks that the footer names the reason itself.

### Documentation

- The manual has a chapter section on the menu and the keys, in both
  languages. There was none: a way of working the program that is
  nowhere written down does not exist for whoever reads.
- All five screenshots taken again, English and German. Four things
  changed on every one of them: the menu bar, the state line at the
  bottom, the text beside red rows on the second sheet, and the
  shrunken "one more speaker" row.

## [2.1.0-beta] - 2026-08-23

### Added

- The program looks whether a newer release is out, and offers to fetch
  it and start again. Looking needs no permission -- it asks github.com
  for a version number and sends nothing -- but nothing is ever fetched
  or replaced without being asked, and the question comes at the start,
  never during a run. What comes down has to be readable text, has to
  look like this program and has to compile before it replaces the file
  that works; the old one stays beside it as `.old`. `--no-update-check`
  switches the looking off and the answer is remembered.
- `install.py` fetches the newest release by default rather than the
  tip of the main branch. `--ref` takes a named version instead -- a
  tag for a particular release, or a branch. A release marked as a
  pre-release is never what the newest means.

### Changed

- ffmpeg comes from the package manager where there is one. It asks,
  and then does it: brew on a Mac, apt-get, dnf, zypper or pacman on
  Linux, each with the switch that stops it asking a second time. On
  Windows it offers to open ffmpeg.org. static-ffmpeg is what is left
  when none of that is there, and it now says what it brings: sixteen
  packages, and a binary loaded from a private repository without being
  held against anything. `VPM_INSTALL_TOOLS=1` answers yes in advance,
  for a run with nobody in front of it.
- A package that was half removed counted as installed. pip leaves a
  package's `__pycache__` folder behind when it uninstalls it, and
  Python reads that folder as a namespace package: the import goes
  through and the module is hollow. Only a module that names the file
  it was read from counts as there now.

### Fixed

- The message that ffmpeg was being installed came at every start, even
  though nothing was being installed: static-ffmpeg only puts its
  programs on the search path for the running process.

### Tests

- `update_test.py`, 24 checks: which version is newer, what counts as a
  newer release, that a no is remembered, that an error page and a file
  that does not compile are both refused, and that the old file is kept.
  Nothing in it touches the network.
- `first_run.sh` puts the machine back the way it was before the program
  ever ran -- the environment, the caches, the packages, what a package
  downloaded after pip was done with it, the keychain entry -- so a
  change to how the program installs itself can be watched from
  nothing. It is not part of the suite.
- The suite stops instead of going red where there is no ffmpeg.

## [2.0.0-beta] - 2026-08-23

### Added

- `install.py` brings the program and the separation model in one
  command, on macOS, Windows and Linux alike -- it is written in Python
  because Python is the one thing that has to be there anyway. Every
  file is held against the SHA-256 sums that travel with the model and
  is not written where it does not match. It reports ffmpeg rather than
  installing it, and hands over to the program at the end. `--check`
  holds an installation already there against the sums, `--to` puts it
  somewhere else, `--no-start` stops before the handover.
- The speaker separation model travels with the repository, in
  `models/speaker-diarization-community-1` -- five files, 33 MB, with
  their licence, model card and checksums beside them. It is read from
  a folder next to the program: no account, no token, no network.
- The program recognises speech itself. On macOS 26 it uses the
  recogniser the system brings, driven by a small Swift program built on
  first use -- 22 seconds for an hour of audio, nothing to install.
  Everywhere else it falls back to Whisper (`large-v3-turbo`, 1.5 GB,
  measured at six times real time on a processor). The words carry their
  punctuation, which is where sentence and clause boundaries come from.
- The program separates speakers itself, locally, without uploading
  anything. Measured against the individual microphones of two complete
  interviews: 98.7 per cent of 45 473 words land on the right person,
  and three quarters of the remaining errors sit where two people really
  do talk at once or where the speaker had just changed. The model
  travels with the program (`models/`, CC BY 4.0, checksummed before
  every use) and is never fetched at run time.
- A voice table under the assignment, one row per voice found, named
  "Speaker 1, 2 ..." until somebody names them, with a button to listen
  to each -- naming a voice without hearing it is guessing.
- Four choices on tab 3 decide what is shown when nobody is clearly
  speaking: the wide shot, the listener, alternating between them, or no
  change at all.
- The wide shot is placed by the language now. It enters on a sentence
  boundary, holds at least five seconds and leaves at the next sentence
  end; where that would run past fifteen seconds it leaves at the last
  clause break before it, never in the middle of a sentence. Measured,
  every inserted wide shot lands in the five-to-fifteen-second window it
  is meant for.
- The exact frame comes from the sound, not from the text: in a window
  around the target the quietest stretch is looked for. That lands in a
  real speech pause 97 to 99 times in a hundred, where the recogniser's
  word boundary manages 42 to 46 -- and it costs a fifth of a second for
  a whole episode.
- A reaction cut. When somebody asks a question and another answers, the
  picture goes to the answering person while the question is still
  running.

### Changed

- A speaker has to hold the floor for one and a half seconds before the
  picture follows. A short "mhm" used to switch the camera, and the
  minimum edit duration then held that camera for three seconds.
- Short shots are merged into the one that **follows**, not the one
  before. Measured over four runs, the time the wrong camera is shown
  falls from 326 to 99 seconds -- and it falls just as far when the
  input is the truth instead of a recognition, so this is a better rule
  and not a crutch.
- The wide shot answers uncertainty. Where the separation frays -- seven
  segment starts inside twelve seconds -- or produces a small mixed
  cluster that belongs to nobody, the wide shot is shown instead of
  guessing. Measured, that beats even the best possible guess, and the
  longest stretch showing the wrong person drops from eight seconds to
  2.3, which is below the minimum edit duration.
- `--wide-after` is 40 seconds instead of 45, `--wide-length` is the
  minimum hold of the wide shot instead of its length.
- One minimum edit duration. The window showed three seconds while the
  functions defaulted to 1.2, so every path without a slider cut
  differently from the interface.
- The opening wide shot survives a fragmented recognition. It used to
  end at the first four-second block of another voice; a mislabelled
  block ended it 88 seconds early.

### Removed

- **auphonic.com no longer supplies speaker data.** Its statistics knew
  0.6 pauses a minute where our own measurement finds 16, and in 66
  minutes the wide-shot search found no place at all on them. Levelling,
  de-bleed, noise removal and transcription are untouched.
- `--wide-min` and `--wide-flow`. With a five-second minimum hold they
  could no longer change anything.

### Fixed

- The preview died on every call with "Preview not possible: 'min-shot'"
  -- it read a key that does not exist.
- The time axis looked files up under the path handed to it. On macOS
  `/tmp` is a link to `/private/tmp`, so the same file carried two names
  and was not found.
- Four labels of the preview player reached the screen without going
  through the catalogue and stayed English in the German window.
- The row of "One more speaker in ..." buttons grew with every
  recording and pushed the preview player off the edge. The file name
  moved into a chooser; the row is now the same width whatever the
  material.

### Tests

- Eight new test files, 90 in total. Among them a test that speaks its
  own audio with `say` rather than shipping a file, and one that holds
  the preview's cut list against the run's.
- `first_run.sh` puts the machine back the way it was before the program
  ever ran -- the environment, the caches, the packages, the models, the
  keychain entry -- so a change to how the program installs itself can
  be watched from nothing. It is not part of the suite: `run.sh` picks
  up `*_test.py` and nothing else.

## [1.1.0-beta] - 2026-08-22

### Changed

- **Settings ...** moved into the footer. It sat beside the tabs, in
  the top right corner, where a button is not looked for. It now stands
  with the other buttons at the bottom right, flat and set apart,
  because it is not a step of the work.

### Fixed

- Two switched-off buttons now look switched off in the same way.
  **Start** kept its filled shape and its own colour while **Dry run
  (writes nothing)** went pale and flat, so one of the pair still looked
  pressable. Both now fade into the same muted blue -- filled for the
  main action, outlined for the dry run, so the rank is still readable.
  The label on a switched-off button was measured for contrast rather
  than guessed: 4.7 against its own background, where the old grey on
  grey gave 2.6.
- The opening line is no longer written in warning colour. "No files or
  project opened yet" is where everybody starts, not a fault, and it now
  stands in quiet type. The warning colour is kept for the case where
  something really is missing. The quiet grey was darkened a shade so it
  still reads on the footer: measured against the desktop's #efefef it
  went from 4.0 to 4.5.

## [1.0.0-beta] - 2026-08-22

### Changed

- The terms are DaVinci Resolve's now, not our own. Looked up in
  Resolve's manual rather than assumed: `Cut in` and `Cut out` become
  **In point** and **Out point** (the manual has `In point` 171 times
  and `Cut in` not once), the two buttons that set them become **Mark
  In** and **Mark Out**, and `Minimum shot length` becomes **Minimum
  Edit Duration**. The German side follows Resolve's German window: „In
  markieren", „Out markieren", „Mindestschnittdauer", and the wide shot
  is „Weitwinkel". The switches are `--in-point`, `--out-point` and
  `--min-edit-duration`; the keys in the project file are `in_point`
  and `out_point`, so the file format counts up to **3**. An older
  project file is refused with a clear message rather than half read.
- A stereo pair now has to prove itself twice. Measured on a 32 channel
  drum recording: the share of what two channels hear together said
  "stereo" eight times and was wrong every time, because in one room
  every microphone hears the same drum. Two more legs decide now -- the
  spacing that comes out of the same measurement has to be under 0.3 m,
  and the pair has to stand out from the pairs beside it.
- In a project the script creates itself, the colour space follows the
  material. A project made a minute ago carries whatever that machine
  defaults to; measured, one starts at Rec.709 and the next at Rec.2100
  ST2084. HDR material now gets an HDR output space, SDR material
  Rec.709, and SDR is no longer delivered wrapped in HDR. A project
  somebody set up is never touched, and automatic colour management is
  never switched off.

### Fixed

- The Resolve part crashed after reporting two cameras with the same
  file name: two clips on one track cannot be put in an order.
- The same collision made the self check report a camera as not
  inserted although its clip was there.
- The footer bar stood at 170 pixels however wide the window was.
- The run bar of a fresh run could open at full.

### Tests

- The suite runs in a fifth of the time. Four tests waited on the clock
  instead of on a condition -- `channel_rows` spent 121 of its 123
  seconds waiting for a tick that never comes. 112 seconds became 33,
  and one test that had quietly stopped checking anything is checking
  again.

## Before 1.0

What follows is the record from before the first release, counted as
0.x. Nothing in it was rewritten -- the versions are the ones that
really happened, in the order they happened, and only their numbers were
brought into this scheme. The program was written for one podcast then
and never handed to anybody.

The record starts at 0.1.0. Everything before that was built without a
changelog, and reconstructing it after the fact would mean guessing at
dates and wording. What the older versions did is in the manual, which
describes the program as it stands rather than how it got there.

## 0.11.1

### Fixed

- The footer bar could open a run at nine tenths and then fall back.
  When a project is opened the measuring fills the bar, and it is left
  full for a moment so the end is seen. A run started inside that moment
  had its stages added to the plan that was already finished, and the
  finished steps went on counting. The old plan is cleared before the
  run's stages are announced, and the bar itself is put to nothing at
  the same moment -- a widget goes on showing the figure it was last
  given until the next redraw, so clearing the plan alone still left the
  old 100 per cent standing for a tick. Found by run_bar_test.py, which
  only saw it when the machine was loaded enough to reach the start
  button inside that moment.

## 0.11.0

Seven findings from a review of the Resolve and render part. Each is
read from the source; none is confirmed against a running Resolve.

### Changed

- The test doubles in `cut_timeline_test.py` and `intro_test.py` can
  report what landed on a track, which is what the timeline report in
  the program asks them for.
- Ready for a public repository: the one-off cleanup script moved out of
  the tree, the preset fixtures carry no personal name, and
  `.gitignore` also holds back `zu_loeschen/`, `_to_delete/` and stray
  media files.

### Fixed

- A camera without a rendered file lost its measured offset. The offsets
  are kept under the rendered name, and the missing key fell back to
  0.0, which put that camera at the start of the axis instead of where
  it was measured. The source path is tried too now, and what stays
  unknown is named in the log.
- Width and height were each taken as their own maximum. A landscape and
  a portrait camera together produced a square frame that neither had.
  The largest frame a camera really recorded is used.
- Where the earliest camera starts before cut in, the timeline start
  moves back. The "For checking" report kept measuring against the old
  start, so every distance it printed was wrong by that much.
- The Full-Mix fallback takes a camera's audio. That audio begins where
  the camera began, not at cut in, so it ran against the picture by the
  camera's offset. The head is trimmed off now.
- A project the program has just created carries Resolve's factory
  Rec.709, and that beat the material: HDR sources would have been
  delivered as eight bit SDR without a word. On a project of our own
  making the material now wins, with a line saying where the output
  colour space is set by hand. A project somebody else set up still
  wins.
- The render target came from the production name alone, so a second run
  wrote over the first delivery. The name counts up and says so.
- Media pool clips were found again by file name. Two cameras both
  writing C0001.MP4 landed on one clip, and the second camera showed the
  first one's picture. The import uses the real path Resolve reports;
  on the timeline, where only a name exists, a collision is reported.

## 0.10.0

### Changed

- The manual describes the settings window, the preset under the
  assignment table, the plus in a channel pair's name, the tick as an
  offer, and which Python versions this is for. Both halves.
- `CLAUDE.md`: what a session needs to know at its start -- where the
  state lives, how the tests run, and the rules that do not bend.
- The shared test fixtures no longer live at fixed paths under `/tmp`.
  Each was preceded by an `rm -rf` on a path anybody can write to, so on
  a shared machine or a CI with two jobs the second run deleted the
  first one's material. The root carries the user id now, and
  `VPM_FIXTURES` overrides it. `tests/fixture_root.py` says the same
  thing to the Python side.
- The channel rows say "unused input -- ignored" rather than "stays
  out", "measurement running ..." rather than "being looked at", and
  "below the noise floor" rather than "practically silent". The
  uncertain case says "uncertain", which is what it means.
- The suite ends by reminding whoever started it not to sit and watch.

## 0.9.0

Two reviews went over everything 0.7.0 and 0.8.0 changed. What they
found is below; every fix has a test.

### Fixed

- Taking a stereo pair apart freed a channel, the proposal was rerun
  over it, and the freed channel was joined to its *other* neighbour.
  One click, two changes, the second one unasked. Now the measurement
  proposes once and a tick corrects that proposal: taking one apart
  takes exactly that one apart, putting one together frees both its
  neighbours.
- The tick used to read "with Channel 5 one stereo track" beside a
  measurement saying they are two microphones. It says "join with
  Channel 5" now -- an offer, not a claim.
- On resume, an output whose channel count the answer gives as empty was
  read as "not mono" and sent again. auphonic.com appends rather than
  replaces, so that is a second render and a second bill. An output that
  is configured but not rendered yet is now found by its own suffix,
  since it has no file name to read one from.
- An ffmpeg that died half way through reading the channels was taken
  for one that had finished: the return code was never looked at. The
  half-read judgement was then stored under the file's size and time and
  would never have been measured again.
- The channel read held the whole recording twice at the moment of
  joining the chunks -- the doubling the chunked read exists to avoid.
  Each channel is now joined and its chunks dropped one at a time.
- A transfer broken off by an error left curl running and downloading,
  and left an open handle on a deleted file.
- The API key went into curl's config file unescaped. A key containing a
  quotation mark or a line break could have added directives of its own.
  Where the file cannot be deleted afterwards it is overwritten.
- Removing the last audio file left the block map standing, so the work
  for the removed recording was queued again and again.
- The Resolve verdict was written into a box that lives in the settings
  window: invisible to anybody who had not opened it. The Resolve tab
  now says whether Resolve answers and offers the way to the settings,
  and the check runs again every time that window is opened rather than
  once per session.
- "not measured -- nothing is running for it" was shown in the ordinary
  case, because the work is registered a moment after the row is drawn.
  The row says "being looked at ..." again.
- Four containers were declared twice in `gui()`, so the first four were
  dead; and `plan` -- the one progress bar -- was shadowed inside
  `start()` by the assignment plan.
- `blocks_facts_from` raised on hand-made facts whose three lists are of
  different lengths, and choked on a non-dict.

## 0.8.0

### Changed

- The floor is Python 3.10, because PySide6 does not build below that
  and the window could not open there whatever the command line did.
- The suite runs on **3.14.7**, the version this is used on daily. It
  used to run on 3.11 while the program ran on 3.14 -- proving something
  about a Python nobody uses.
- `--version`, the log header and every run say which Python is running
  and name the recommended one where they differ:
  `Python 3.11.15  (recommended version 3.14.7)`.
- Pools are sized with `os.process_cpu_count()` where it exists (3.13
  and up): it says how many processors this *process* may use, not how
  many the machine has. In a container held to two of thirty-two, the
  old number meant thirty threads taking turns.
- `consistency_test.py` reported `__annotate__` and `__classdict__` as
  names without an origin. Both are put there by the 3.14 compiler, not
  by anybody writing code.
- Two sorts of setting stood in one box on the first sheet: the key for
  auphonic.com, entered once in a lifetime, and the preset, chosen for
  every production. Choosing a preset therefore meant paging back from
  the table where the decision is actually made.
- **Settings ...**, top right of the tab bar, opens a window holding the
  key, the tick that stores it, **Connect**, and the Resolve check. The
  Resolve box has left the third tab; the check itself still runs by
  itself on the first look at that tab, since a run that ends by
  building a project should not find out at the end that Resolve was
  never running.
- The preset and **Fetch transcript** now stand under the assignment
  table, right below the Multitrack tick. The whole "what should this
  run do" is in one place.
- The first tab holds files, production name, spoken language and output
  folder. Nothing else.
- `settings_window_test.py` holds all three to it.

### Fixed

- The channel rows of a recording are drawn from the measurement over
  all its blocks, and the row hangs on the first block. Each finished
  block asked for a redraw of its own row -- which only the first block
  has. The last block to finish therefore redrew nothing, and a
  recording of two blocks said "being looked at ..." for as long as the
  window stayed open, while the work was long done and the bar had gone.
  Reproduced, then fixed: every finished block now redraws the row of
  the recording it belongs to. `blocks_rows_test.py` holds it there.
- A row waiting for a measurement that nobody started said the same as
  one that is being measured. Now it says which of the two it is.
- Where the channel count of a file cannot be determined, the run says
  so instead of swallowing it -- that silence was what made the state
  above so hard to read.
- Ticking a channel pair the measurement already found, or unticking one
  it did not, no longer counts as "set by hand". Only a real override is
  remembered, so clicking through the rows no longer leaves every one of
  them claiming to have been set by hand.

## 0.7.0

### Changed

- The channel measurement is eleven times faster. Every channel was read
  by decoding the whole file again: a 32 channel recording went through
  ffmpeg 32 times. It is one pass now, taken apart afterwards. Measured
  on one 92 MB block of 32 channels: 22.9 s before, 2.0 s after -- 4.0
  MB/s to 46.2 MB/s -- with the same levels, the same silent channels
  and the same pair numbers to six decimals. A pair of 1.8 GB blocks
  drops from about fifteen minutes to about ninety seconds.
- `channel_read_test.py` reads the same file both ways and compares
  sample by sample, so it stays that way.

### Fixed

- On a Mac the API key no longer travels to `security` as an argument
  where it does not have to: it goes over the input first and is read
  back to see whether that worked. Only if the wrong key comes back does
  the old way follow. An argument stands in the process list, which
  every auditing agent on a managed machine writes to a log.

## 0.6.0

Four reviews went over the program from four sides -- what happens to
the API key, what a stranger meets on a fresh machine, whether the
newest code is right, and whether the manual still describes the
program. What they found is below.

### Changed

- The manual no longer claims the key is never in the process list. On
  the way to auphonic.com it is not, but `--auphonic-api-key` puts it in
  this program's own command line, and storing it in the macOS Keychain
  hands it to `security` as an argument. Both are now said plainly, with
  `AUPHONIC_TOKEN` named as the way round the first.
- The manual says which Python versions run, and what Linux costs.
- The temporary file holding a curl answer is removed even when the call
  is interrupted, and a failed removal no longer replaces the real
  error.
- A pair is written with a plus, not an ampersand: `Channel 1+2` on
  screen and `_Channel1+2.wav` on disk. Measured: both are legal file
  names everywhere, but an unquoted ampersand splits the command in two
  in every shell, and in a web address it separates parameters. The old
  spelling is not recognised any more and does not need to be -- the cut
  pieces live in a temporary folder that goes when the program does.

### Fixed

- `blocks_facts` gave back the last block's pair judgement instead of
  the loudest block's: the inner loop reused the name of the list it was
  filling. A recording whose second block is the run-out or pure silence
  was therefore judged on that, and the answer even depended on the
  order the blocks arrived in. It also grew the cached measurement of
  the block it read. The combining half is now `blocks_facts_from`,
  which can be held against made-up numbers without building gigabytes
  of audio.
- A recording of several blocks never came apart into tracks: the
  regrouping still looked for the `_ch` in the names from before 0.4.0,
  while the pieces are called `_Channel1` now. Two 32-channel blocks
  stayed one row with one speaker name, and the run folded all channels
  into one voice.
- `--together` promised "in this order" and then sorted the blocks by
  name again. Without a timecode that is the one case where name order
  is meaningless -- it is exactly why the switch exists.
- A tick joining two channels to a stereo track is no longer honoured
  where one of the two is an unused input. The interface never offers
  the tick there, but a tick made earlier outlives the measurement it
  was made under.
- A file named in `--together` that is not on disk was reported only
  when one of its partners ended up in a recording of its own.
- Two file names spelling the same moment ("260808" and "20260808") drop
  both, which was right and silent. It is now said.
- Intro and outro survived the opening of another project, because the
  file marks are the one per-file store that was not cleared. With the
  0.5.0 guard against two intros, that stopped the run with a message
  naming a file that was not even in the list.
- `--help` and `--version` answer without numpy and without ffmpeg. They
  used to fetch twenty megabytes and look for ffmpeg first, and on a
  machine without either they failed instead of answering.
- Starting the interface without PySide6 printed one line and died
  silently: the console went into the log file before Qt was resolved,
  so a hundred megabyte download happened behind a silent terminal. Qt
  is resolved first now.
- When pip fails, the last lines of its output are printed. The advice
  underneath was the same command that had just failed, with no hint
  why.
- pip no longer inherits `AUPHONIC_TOKEN`. It runs code from the
  packages it installs, and any of them could have read the key out of
  the environment.
- Below Python 3.7 the program says so and stops, instead of failing
  later on a keyword argument.
- Where ffmpeg is missing, the advice names the machine this is: brew on
  a Mac, the package manager on Linux, ffmpeg.org on Windows. Linux used
  to get the other two.
- Installing past the system package manager is said out loud when it
  happens, with the virtual environment named as the way round it.
- `requirements.txt` and `requirements-dev.txt`.
- On resume, a mixdown of one channel is no longer taken for the
  two-channel one a stereo run needs. Where the answer says nothing
  about the channel count, both still count as present -- an upload sent
  twice is billed twice.
- `--lufs` was marked "multitrack only" in the help text and is read by
  the simple path too.

### Tests

- `review_fixes_test.py`, one block per defect. 78 in all.
- `split_tracks_test.py` used the pre-0.4.0 piece names, which is why it
  did not catch the regrouping defect. It builds its names with
  `split_target` now.

## 0.5.0

### Changed

- The list of home-directory folder names that say nothing about a
  production ("Desktop", "Downloads") held German entries beside the
  English ones. macOS and Windows keep the English name on disk whatever
  the system language, and Linux writes the names it chose into
  `user-dirs.dirs` -- which is now read, instead of one language being
  guessed at.
- The metrics CSV stays comma separated. The manual says what that costs
  on a German system and which way in avoids it.
- A pass over every comment and docstring against the house rule "short
  and to the point": storytelling, self-justification and anecdotes from
  particular recordings are gone, the reasons and the measured numbers
  stay. 99 places, 51 lines fewer, no code touched -- proved by
  comparing the syntax tree with docstrings stripped.

### Fixed

- The reason the start button is grey stands in the footer beside it. It
  was in the tooltip alone, and a disabled Qt button shows no tooltip at
  all -- the text hung on a wrapper around it, where nobody looks.
- A missing production name marks its field red, like a duplicate
  speaker name or a duplicate output name does in its row.
- The reason named pages that no longer exist ("2.1 Production", "2.3
  Resolve cut"). The names are now read off the tabs themselves, so they
  cannot drift apart again.
- The Resolve tab no longer carries a tick. Nothing on it can keep a run
  from starting, so the tick was there whatever happened.
- Two files set to intro (or to outro) both went into the same switch
  and the last one silently won. The second choice now frees the first,
  and a run that still sees two of a kind stops and names them.

### Tests

- `folder_name_test.py` and `start_reason_test.py`, and a section in
  `argv_test.py` for the doubled intro. 77 in all.

## 0.4.0

### Added

- A stereo track stays stereo the whole way: onto the time axis, through
  the loudness measurement, into its own audio track on the camera file,
  and into the mix. The rule is "keep what the source has" instead of
  folding everything to one channel.
- At auphonic.com the finished mixdown is asked for in two channels as
  soon as one track is stereo, and on the simple path the mono fold is
  switched off for every output the preset asks for.
- Without Multitrack, recordings that ran at the same time now also go
  into the video as tracks of their own, after the mix. Whether they ran
  at the same time is read from the timecode, not guessed.
  `--no-single-tracks` leaves them out.
- A camera ticked "as a track" is an audio candidate like any other: its
  channels are judged and cut by the same rule as a recorder file, so a
  camera carrying two clip-on microphones gives two tracks with two
  speaker names.
- The same on the command line: `Osmo.mov Wide.mov --multitrack` reads a
  two microphone camera as two speakers without an interface, and still
  writes one file per camera.
- Camera tracks get the full camera selector. A microphone plugged into
  one camera may belong to a person another camera is filming.
- A camera counts towards Multitrack as soon as it is ticked as a track,
  on the command line as well as in the interface.
- Blocks whose names carry a date and a time instead of a counter are
  joined into one recording when the next one starts where the previous
  one ends.
- `--together FILE ...` and the "belongs to" selector put files into one
  recording by hand, the counterpart to `--apart`.
- Channel count and sample rate have to match before two blocks are
  joined.
- The channels of a recording are judged over all its blocks, not over
  the first one. On a 32 channel mixer recording the first five minute
  block was the soundcheck and read as one used channel pair; the second
  was the show and read as ten tracks.
- An absolute floor for a channel that carries anything: under -70 dBFS
  there is only the converter's noise, and a pair judged on noise
  answers differently every time it is measured.

### Changed

- Every neighbour is judged, not every second one. On a mixer, channels
  2 and 3 can be the stereo pair just as well as 1 and 2; fixed pairs
  asked the wrong question and got a confident wrong answer.
- One row per channel in the file list, with a tick that says "this one
  and the next are one stereo track". Ticking channel 2 takes the tick
  away from channel 3 -- a channel can belong to only one pair. Where
  two neighbours both look like a pair, the left one wins.
- The tick and the reason behind it moved into the wide column. In the
  narrow one, where the file marks live, the word beside the box was cut
  off after its first letter.
- Tracks are named after their channels -- `Channel 1`, `Channel 2+3` --
  and so are the files they are cut into, closed up and with a
  fingerprint of the source folder in between:
  `Mixer_3f9a1c02_Channel1+2.wav`, instead of `_cha` and `_chef`.
  "Channel" stays English in every language -- it is the word on the
  recorder and on the mixer.
- The hint under a file with more than two channels said they would be
  mixed into one track. They have not been since 0.1.0; it now says what
  actually happens.
- `--min-shot` from 1.2 s to 3 s. Interview cutting practice asks for
  three to five seconds; a camera that changes faster than the viewer
  can settle on a face reads as nervous. SmartSwitch calls the same
  thing 1.00, which is where the old 1.2 came from.
- The Multitrack tick moved from the settings sheet to under the
  assignment table, because what it needs is decided in that table.
- With cameras only and no audio file, the interface offers the
  Multitrack tick instead of stopping the run afterwards.
- Channel conversions are written out rather than left to ffmpeg, in
  both directions. Its own uses an equal-power law -- measured on a
  signal at -24.08 dBFS, one channel to two comes out at -27.09 and two
  channels to one at -21.07 -- and the second of those depends on the
  output format.

### Fixed

- A production with a transcript did not start when the preset already
  carried the transcript output formats. The run then waited for it
  until the time limit.
- The check report cleared the channel rows out of the file list when it
  came back: the stereo tick and everything beside it disappeared, and
  only a later rebuild brought them back. Finding lines now carry a mark
  of their own instead of sharing one with every other extra row.
- A track cut out of a multichannel file lost the recording time. Those
  files are exactly the ones that carry it, and everything after the cut
  asks the piece rather than the file it came from, so a real pause
  between two blocks was swallowed instead of being filled with silence
  and reported.
- Two files with the same name on two cards wrote over each other's
  tracks, silently, because a piece that is already there is not written
  again. The name of a piece now carries a fingerprint of where its
  source lies.
- Above 26 channels the channel letters ran together: channels 1 and 2
  gave "ab", and so did channel 28. On a 32 channel mixer recording one
  track therefore held another one's audio.
- A camera with more than two channels was folded to mono before anybody
  looked at what was on it, so four microphones on four channels became
  one voice. The audio is now extracted with every channel it has and
  folded only if nothing has to be cut out of it.
- Where a recording is made of blocks, the pair judgement took the
  answer of the loudest block even when that block had one of the two
  channels silent -- which is no answer at all. It now takes the loudest
  block that actually measured the pair.
- Changing the stereo tick dropped the cut tracks of one block only. The
  other blocks kept their old cut, and the rows then held block one's
  channel 1 next to block two's channels 1 and 2.
- Continuation blocks that were found rather than selected were never
  measured or cut, so a multi-part multichannel recording was cut from
  its first block alone.
- The block-size rule never saw the block it was judging: on the first
  step forward it compared a block with itself and always said yes, so a
  short finished take in front of the real recording was glued onto it.
  Which answer came out depended on which block was selected.
- Two files carrying the same recording time were laid end to end
  instead of on top of each other. Two recorders started together write
  exactly the same number, and those recordings run at the same time.
- Two by-hand groups could both claim the same block, and it was then
  decoded and mixed into two productions. The first group to claim it
  keeps it, and the second is told.
- A file named with `--together` that is not on disk was accepted into
  the recording and then vanished without a word. It is refused, and the
  refusal is reported.
- Two names spelling the same moment -- "260808" and "20260808" are the
  same day -- put one file into two recordings, and which grouping came
  out depended on the folder listing.
- On a case-sensitive disc, `REC0002.wav` and `rec0002.wav` collapsed
  into one entry and the folder listing decided which one was used.
- A counter that reads as a time of day -- `260808_000001` -- made the
  clock rule fire, find nothing and stop, instead of handing back to the
  counter rule. Three blocks of one recording stayed three recordings.

### Tests

- 75 tests, all of them checking something. The five that only printed
  their result -- colours, metrics, dualmono, crosstalk, intro -- now
  measure it. The three that cannot be checked outside Resolve --
  render, render_hdr, multicam -- say so in their docstring.
- New: stereo_mix, beside_mix, camera_track_mode, camera_channels,
  blocks_facts, clock_blocks, together, german_hunt.
- `german_hunt_test.py` reads seven ways for German where only English
  belongs, including the running program: the job is driven twice in
  German and the output searched for English function words.

## 0.3.0

### Added

- A single continuation file can be taken out of a recording by hand and
  stays out, even though the search would find it in the folder again.
  Added later it is a recording of its own; only removing the whole
  recording and adding it again joins it up as before.

## 0.2.0

### Changed

- The camera cut is built even with one camera, so Resolve can group,
  colour and zoom the clips.

## 0.1.0

### Changed

- The pipeline works in tracks instead of files. A multichannel recorder
  file is cut into its tracks, each with its own row in the assignment,
  its own name and its own camera.

[kac]: https://keepachangelog.com/en/1.1.0/
[semver]: https://semver.org/spec/v2.0.0.html
[2.2.0-beta]: https://github.com/Bascht74/videopodcast-magic/compare/v2.1.0-beta...v2.2.0-beta
[2.1.0-beta]: https://github.com/Bascht74/videopodcast-magic/compare/v2.0.0-beta...v2.1.0-beta
[2.0.0-beta]: https://github.com/Bascht74/videopodcast-magic/compare/v1.1.0-beta...v2.0.0-beta
[1.1.0-beta]: https://github.com/Bascht74/videopodcast-magic/compare/v1.0.0-beta...v1.1.0-beta
[1.0.0-beta]: https://github.com/Bascht74/videopodcast-magic/releases/tag/v1.0.0-beta
