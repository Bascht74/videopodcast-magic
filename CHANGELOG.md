# Changelog

All notable changes to this project are documented in this file. The
format is based on [Keep a Changelog][kac], and the numbers are given
out under [Semantic Versioning][semver]. English only, unlike the
manual: this is for whoever picks the script up from a repository.

Only the two releases of 2026-08-22 carry a date. The versions below
them were numbered after the fact, and no reliable release date for them
survives.

## [Unreleased]

### Added

- A run can be broken off. The button stands beside Start while a run
  is going and can be pressed at any moment -- but the run stops only
  where stopping leaves nothing half written, so between the press and
  the end there is a wait, and the log says so rather than leaving the
  button looking broken. What was written before the break is whole;
  what comes after it is missing, and the run says which files are
  finished and that the folder holds a part of a run, not a result.
  Whatever ffmpeg was doing at that moment is ended with it -- a child
  nobody tells goes on writing long after the window says it stopped.

### Changed

- In the camera table nothing stands behind the answer any more,
  neither at Kind nor at Camera audio. Instead, where no speaker is
  assigned to a camera, the one entry **Content** is barred and says
  on itself why -- intro, outro and "ignore this video" stay open,
  because those are answers about the file and have nothing to do with
  who was assigned where. Greying the whole list took them away for no
  reason, and the sentence beside the field made the row too long to
  read.

### Fixed

- A shot could arrive under the "shortest shot" the window promises.
  The rule that merges shots below that number ran after the wide shot
  at the edges but not after the wide shots put into a long monologue,
  although it says itself it has to run after every step. Measured on a
  monologue of 240 s with the shortest shot at 8 s and the wide shot
  length left at 5: five shots of exactly 5.00 s reached the cut, three
  seconds under the number that was set. It only happened where
  somebody asked for a longer shortest shot than the wide shot lasts;
  the two defaults are the safe way round.
- Where no camera is a wide shot, the preview and the run reach for the
  same stand-in. They took different ones -- the preview the first of
  its own list, the run the reference clip -- and in a real shoot both
  are real cameras, so it showed as two different cuts rather than as a
  fault: three speakers on three cameras gave 15 shots in the run
  against 12 in the preview. It goes by name now, not by position, so
  two lists built in different places cannot drift apart again.

### Documentation

- Nineteen numbers in the manual say what they are: whether they are a
  default, which switch sets them, and what a larger or smaller value
  does. Two were wrong. The report of samples at the ceiling was said
  to appear from eight samples on, where the program says three -- and
  it was said to need the peak within 0.1 dB of full scale, a
  condition that does not exist: the constant for it is defined and
  used nowhere. Whoever looked for a channel with four samples at the
  ceiling would have found the manual and the program disagreeing, and
  had no way to tell which was right.

## [2.12.0-beta] - 2026-08-29

### Changed

- The window a run works out for itself is the stretch **every** camera
  saw, not the one any of them saw. It begins where the last camera
  came on and ends where the first one stopped, and the log names both
  of them. Wider than that, there is a stretch at the start where a cut
  to the camera that came on late finds no picture, and the episode
  comes out shorter than the window promised -- measured over the test
  interview: the beginning lay 12.567 s before one of three cameras
  began, and on the built material the window even began 0.180 s before
  its own zero. Whoever wants the wider stretch sets an In point of
  their own, which is untouched by this.
- The line beside the progress bar is shortened in the middle where it
  is too wide for its field, and carries the whole of itself as a
  tooltip. It holds a file name, so how wide it turns out is decided by
  the material: with a camera file of 29 characters the German stood
  20 px past its field while the English of the same moment fitted. A
  shorter wording would only have held until the next longer name.
- No In point or Out point while an intro, an outro or a file marked
  not to be used is in the player. The four buttons are greyed out and
  say why: such a file is set in front of the material or after it, not
  cut into it, so no point inside one is a boundary of the episode.
  Marking there put the window somewhere that had nothing to do with
  the interview -- an 18-second jingle in the player, and above it a
  window from 17:14 to 18:23.
- The line saying how much sound was cut off at the back says what it
  was cut back to. Two lines stand close together there, both saying
  "back", and their numbers were sixteen minutes apart: the first is
  the sound that has no picture, the second everything past the Out
  point. Both were right, and both were read as the same thing.

### Tests

- The cut itself is held against numbers now: 64 checks in a hundredth
  of a second over a conversation built for the purpose, so the right
  answer is known before the cut is computed. Whoever speaks is on
  their own camera -- 207 samples of 207 -- a silence goes to the wide
  shot, and every setting that is a number is read back out of the
  finished cut: the shortest shot, the delay to a speech boundary, how
  long before a wide shot comes and how long it holds, how late it may
  still arrive, how much of the whole it may take, and how early an
  answer appears. Each rule is also run switched off, and the readings
  were held against four deliberately broken copies of the program --
  all four came out red. That is how the fault above was found.
- The window a run works out had no test at all: the whole suite stayed
  green while the meaning of that window turned round, because nothing
  asked. The arithmetic stands on its own now and is held against
  numbers -- three cameras that do not begin together, one camera
  alone, cameras that do begin together, and two that never overlap.

## [2.11.1-beta] - 2026-08-28

### Added

- Where a camera's timecode and the measured alignment disagree by
  more than one frame, the log says so and names both numbers. The
  timecode still decides where the camera sits -- what changed is that
  the measurement is no longer dropped without a word. On the
  reference camera the two are the same number, so a camera standing
  in the wrong place had nowhere to show itself.

### Changed

- The window length in the preview player stands on a line of its own,
  under the In point and the Out point it spans. Beside them there was
  no room for it in German: the addition that says this file begins
  later than the window, or ends earlier, or lies outside it
  altogether, fitted in none of its three versions -- measured 16 to
  40 px too wide. Nobody had seen it, because the addition only
  appears where the material carries a timecode, and until now the
  test material carried none.
- The two players stop each other. Starting one pauses the other: two
  pictures running at once are two moments at once, and neither can be
  judged.
- An answer given in the window reaches the preview without a run.
  Which camera is the wide shot is an answer, not a measurement, and
  the file the preview reads can be older than it -- marking a camera,
  or giving a voice a camera, now moves the band underneath at once.

### Fixed

- The window could stop for good, and then nothing in it answered any
  more. It happened where a player was told to stop that had never
  started: what lies behind such a player is built at that moment, and
  building it waits for a lock that another player holds while it is
  starting up. Six places did that without asking -- on a jump, on the
  transport, on the picture that is not showing, and before a new file
  was loaded. They ask first now, and a player that is not playing has
  nothing to pause anyway. Found because two tests of this project
  stopped in the same place, one of them with a single window open;
  the suite went from three and a half minutes to twenty-six seconds
  with it, so the same waiting had been slowing down everything that
  opens a window.
- The Resolve project put the cameras where the alignment measurement
  had them, not where the preview had shown them. Two of three cameras
  stood 37 s and 78 s away from the cut that had just been approved --
  what landed on the timeline was not what had been judged. A camera's
  place in the handover file now comes from its own timecode, the same
  number the preview reads, and the measurement stands beside it under
  a name of its own.
- The timecode is read at the frame rate of the material, not at a
  fixed 30 frames. At 25 fps it was up to 0.160 s out -- four frames;
  at 30 fps nothing changes. The three places that turn the value back
  into characters follow it: the file list, the two lines that say the
  time window back, and the hint about a clock that was never set.
  Those two lines were printing at 30 already while the value they
  printed had been read at the material's own rate, and it was never
  noticed, because everywhere else a value read wrong and printed
  wrong the same way came out looking right again.
- A time window set by hand stopped the Resolve project from being
  made at all. The check before that step held the In point against
  the zero of the axis -- the earliest camera, which lies before any
  In point anybody sets -- so every window that did not begin at the
  first camera was turned away as belonging to older files. A run
  writes down the window it was made with now, and the check asks
  that.
- The handover file did not carry which speaker sits at which camera.
  Every camera therefore counted as the wide shot, and the whole
  episode fell together into one single shot.
- The camera table said **Wide shot** for a camera a speaker had been
  given: two columns of the same table, one naming the speaker and the
  next saying nobody sits there. Both tables are built before anybody
  is assigned, and the wide shot is derived from exactly that
  assignment. They are drawn again now the moment a voice is given a
  name or a camera -- the file list on the first tab with them, which
  went on calling every camera the wide shot.
- Speaker names and the answer **several speakers** stay in the
  project file and survive the window being closed. Saved at any
  moment other than the one the answer was picked in, a project came
  back with everybody called "Speaker 1" although the voices were
  right there.
- Switching the Kind of a file no longer makes the assignment sheet
  flash. Between the old table going and the new one arriving is a
  moment with nothing in it, and Qt painted it.

### Tests

- The suite reported green where it had checked nothing. A test that
  left out the part its machine cannot do, went on with the part it
  can and fell over that was written down as skipped -- the failure
  was neither shown nor counted, and skipping never reached the return
  code at all. The CI, for its part, did not write down which ffmpeg
  it ran against, did not hold the model against the checksums shipped
  beside it, and had no time limit on macOS.
- The gate test builds three windows at a time instead of six, and a
  child that has said nothing for a hundred seconds is killed, built
  once more on its own, and said out loud in the log. Six windows at
  once, each holding three players, walked into a lock inside Qt --
  at worst every second run, until the program stopped making the
  window for a picture while its players were starting up and stopped
  telling a player to pause that was not playing.
- Four new checks over the time axes: that a window shifts nothing
  against anything else, that In and Out points counted from the ends
  give a length that makes sense, that every camera sits where its own
  timecode puts it and not only the reference does, and that an answer
  given in the window reaches the cut without taking anybody's
  speakers away.

## [2.11.0-beta] - 2026-08-26

### Added

- One speaker is enough for a cut; it took two before. Where one
  person is named and two or more cameras are released, the box says
  **Cut with the wide shot**: their own camera stands and the wide one
  breaks it up. Measured: five minutes give 15 shots, 7 of them the
  wide one. With one camera it stays at "no cut" -- there is nowhere
  to cut to.
- The wide shot can be said out loud. **Kind** carries **Wide shot**
  as a value, in the file list and beside the player, and
  `--wide-shot` says the same on the command line. A camera marked
  that way takes no speaker: whoever stood on it is put aside and
  comes back the moment the mark falls. Where nobody marks one, the
  camera the program derives for itself shows **Wide shot** greyed
  out with the reason beside it, instead of doing it silently.
- The loudness of the finished episode is set in the window. Five
  entries in the **Production** box: the four targets, each with what
  it is the standard for, and **Take from source files**, which
  adjusts nothing. It starts at -16 LUFS, the last choice is
  remembered for the next new project, and a project file carrying
  its own value beats it. Until now nothing in the window was bound
  to the loudness at all, and every episode came out at -16 whatever
  it was for.

### Changed

- The assignment is a tree. A recording is a row with a triangle, and
  the voices found in it are the rows folded in under it. Folded up,
  the recording carries what disappears -- `on 2 cameras`, or
  `on 1 camera, 1 without`; folded open, its own cell stays empty. The
  assignment stands on exactly one level, never on two at once. A
  click on a voice row plays that voice at its longest passage.
- The name field no longer picks **several speakers** by itself. It
  used to jump there as soon as the separation found more than one
  voice; it carries a given answer now and nothing else. What was
  measured stays: picking **several speakers** puts the voices there
  at once, with the names and cameras they had, without computing
  anything again. Where one speaker is all there is, the offer stands
  beside it -- "Only one speaker -- separate the track?".
- Picking a camera for a voice makes that row the current one, so
  whoever picks hears what they are picking: opening the camera list
  and clicking into the name field both move the player.
- The **Question** rule is answered with **do not go early** where it
  used to say **off**: what does not happen, instead of a switch
  position. The stored value stays `off`, and command lines and
  project files are unchanged.
- The camera table on the assignment tab drops the hints and the red.
  The file list on the first tab still says all of it, at full length,
  where the files come in.
- The legend under the cut band says who is in the picture, not which
  file it came out of. A camera with one speaker carries that name,
  several speakers all of them joined with a plus, and the camera
  nobody is on is called **Wide shot**. It wraps instead of running
  off the edge of the window: the Resolve sheet fell from 1838 to
  1206 px, so on a 1512 px window there is nothing to scroll,
  sideways or downwards. Nothing was shortened or left out to get
  there.
- The speaker table has a lid. From the fourth speaker on it scrolls
  inside itself instead of stretching the whole sheet taller.
- A guessed speaker name counts where nobody typed one -- but only
  where it begins with a letter. `Kandidat_0008A.wav` gives
  `Kandidat`; `0008A.wav` gives nothing, the field stays empty and
  Multitrack refuses to start. With Multitrack the name becomes the
  label of that track at auphonic.com, where it is read by people who
  never saw the file, and a card number there looks like a fault
  rather than like a person.
- The log entry about the reaction cut says how many questions stood
  in the transcript, how many became a cut, and why the rest did not.

### Removed

- **`--platform` is gone with nothing in its place, and without
  `--lufs` nothing is adjusted any more.** It used to be -16 whatever
  the material was. This breaks a stored call: a command line that
  leaned on the default now comes out at the loudness of its source
  files, and `--lufs -16` is what asks for the old behaviour. In the
  window the same question is the **Loudness** list, and with **Take
  from source files** the file comes out byte for byte as it went in
  -- measured.

### Fixed

- The name field could not be typed into at all. Where it read
  "several speakers", the first keystroke tore down the very field
  that was being typed into, and the speaker was called `A`
  afterwards. The rebuild waits for the end of the typing now. The
  same corner had a second fault: with the caption showing, Qt wrote
  the letters into it instead of replacing it --
  `sevAnnaeral speakers`.
- The **Resolve cut** tab did not reach the run. In point, Out point,
  the eight cut numbers, the four choice fields and the wide-shot tick
  stayed lying in the window whenever neither Multitrack was ticked
  nor a separation had run: the run cut with the default values while
  the preview beside it stood on the numbers that had been typed in.
  They reach the run on every path now.
- An In point set afterwards moved everything except the cameras.
  Measured: the zero point and the speaker passages travelled with it,
  the camera offsets stayed where they were, and picture and sound
  stood 60 seconds apart. Now 0.0, and the counter-check without an In
  point comes out unchanged.
- Camera sound was unpacked at a fixed bit depth, in four places and
  wrong in both directions: a 24-bit camera squeezed into 16, a 16-bit
  camera blown up to 24. The depth follows the source now.
- Where there is no wide shot at all, its four numbers and its tick
  still did something. The program fell back on a camera somebody is
  sitting in front of, so "Wide shot after 40 s" broke one person's
  monologue with a look at somebody else's camera. Measured with
  three speakers on three cameras: 15 shots instead of 11 in the run,
  12 instead of 8 in the preview. They do nothing now, and the window
  greys them out with the reason underneath.
- The camera assignment was lost when a project was opened.
  Recordings that carried no typed name came back without a camera.
- The output tab kept the colours it had started with. Started light
  and put on dark, the running text stood at a contrast of 1.00 -- it
  was invisible; the other way round the same. The lines already
  written follow the appearance now.
- A camera whose speaker name is only guessed was played with the raw
  recording while its prepared track lay ready, and nothing said
  which of the two was heard. The guess counts here as well now.

### Documentation

- The manual was pulled through the day's work, both languages: the
  assignment as a tree instead of a voice table of its own, the
  **Separate speakers** button that is gone, **do not go early** in
  place of **off**, the cut that needs only one speaker,
  `--wide-shot`, the loudness field, and the `--platform` line, which
  was struck.

## [2.10.1-beta] - 2026-08-25

### Fixed

- No cut at all, and a message that named a file there was none of.
  A Zoom H4n writes a BWF time reference of 2304000 samples -- 48
  seconds, dated 1 January 2008, a clock that was never set. The
  program says so on the first tab ("this clock was not set") and then
  used that timecode anyway: the zero point became 48 s where the
  measured axis said 61128.6, an In point 62053 s into the day landed
  62005 s into a recording of 5217 s, the time window came back with a
  length of minus 56788 seconds and no complaint at all, and the
  preview said the file held no speaker statistics -- with no file
  anywhere in it. Measured on the real material, before and after:
  zero point 48.0 -> 61128.619, window -56788.399 -> 4140.767, cut
  none -> 218 shots.
- The under-five-seconds guard on the time window sat before the
  trimming, so a window outside the material passed it and the trimming
  then made the length negative. It sits behind now, and a window that
  cannot work says where it lies and how long the material runs.
- The rule about an unset clock was written down four times. It lives
  once now, in `clocks_apart`, and the hint on the first tab, the audio
  origin and the zero point all ask it. The hint comes out byte for
  byte as before.
- Where no cut comes out, the reason is given -- no speaker, no camera,
  no length, no voice with a camera, or no shot left standing after the
  rules.

## [2.10.0-beta] - 2026-08-25

### Changed

- The assignment tab carries one table where it carried two. A
  recording is a row, and the voices heard in it are rows directly
  underneath it. Where a recording shows voices, its own **belongs to**
  cell is empty: the assignment has exactly one level, and the rows
  below carry it. Two tables meant the same two columns twice, and a
  file could say "into every camera" while the voices under it said
  "into the mix only" -- two truths above each other.
- The button **Separate speakers** is gone. It is an answer in the name
  field now: type a name, or pick **several speakers**. One question --
  who is to be heard on this recording -- with answers instead of a
  field beside a button.
- Picked back is picked back: setting a name again hides the voice
  rows, and picking **several speakers** brings them straight back,
  with the names and cameras that were given and without computing
  anything. A separation costs three minutes on real material, and
  a mis-click must not undo it.
- The **Listen** button is gone; a click on the row does the same, and
  lands in the middle of that voice's longest passage.
- The voice row no longer prints how long somebody speaks and where
  their longest passage is. Both are still worked out -- the longest
  passage is where the click takes the player -- but the row stood at
  three times the width it needed. It had carried one number before
  that looked like a timestamp and was a sum; splitting it in two was
  right and answered the wrong question.
- **Kind** stands on both tabs, one value: what is known at import is
  said in the file list, what is only noticed while watching can be
  changed beside the player.
- Where a voice is set to **do not use**, its name field is greyed --
  a name without effect. The name is kept, and the row still plays, so
  the tool for deciding stays.
- The separation starts by itself only where there is exactly one
  candidate. With two cameras released it used to start on a guess --
  the longer of them -- and spend three minutes unasked.
- The line under the table said "who speaks when can be worked out on
  this machine" while the table already said "Separated: 4 speakers".
  It only speaks now where this machine does not do the separation at
  all.
- Before a run, the box says who gets no camera of their own.

### Fixed

- Closing the window saved nothing. The project was written after the
  time axis, after a separation, at "Not on this machine" and at Start
  -- and closing was none of those. Measured: two names typed, two
  cameras picked, window closed, file unmoved. A separation costs three
  minutes and the names are given by hand.
- The dry run did not write either, which is the trap with the longest
  fall: the same hand work stands before it.
- One German word: an intro or **Abspann** with two channels, not
  Nachspann. The selector had said Abspann all along.

### Documentation

- The pictures are stale and are taken again before the next release,
  not after every change: the interface moves several times a day now.

## [2.9.0-beta] - 2026-08-25

### Changed

- Whether a video file's audio is used is decided on the file sheet
  now, at every video, as a drop-down reading "do not use the audio"
  until somebody says otherwise. It sat on the assignment tab as a tick
  named "as a track", one tab after the question it answers.

  It cannot be measured, only asked. Two speakers on Rode microphones
  as their own files and two on DJI radio mics recorded straight into
  the video track look identical from outside -- two channels, 48 kHz,
  clean levels. Only whoever was in the room knows whether that is a
  usable recording or the camera's own microphone in a room.

  Once it is set, the audio goes through the same machinery as a
  recording that was read in: channels measured, the stereo verdict,
  silent channels dropped, cut into tracks. Not a second path that
  looks similar.
- The field stands on the assignment tab as well, showing the same
  value both ways -- because judging a track means listening to it, and
  the player is there. What is known up front is said on the file
  sheet; what is only noticed later can be changed beside the player.
- Exactly one video carrying sound and no audio recording beside it:
  the field sets itself, is greyed out, and carries its reason next to
  it. Derived, never stored, so adding a recording takes it away again
  with nothing left behind.

### Fixed

- Taking the last sound away left the Start button live and the reason
  line empty. A window that opened without sound refused correctly, but
  only by accident -- the button had never been enabled there.
  assignment_fresh() left early when there was nothing to show, and the
  check that greys the button sits at the far end of it. Twelve seconds
  were watched; it never corrected itself. Found by the test that was
  asked to write down the rule and refused, because the rule was wrong.
- The update box showed the newest release only. Somebody two versions
  behind saw one section and had to guess at the rest; the sections in
  between come down as well now, and the heading says what it means --
  what changed since the version that is running.
- A folder that cannot be read while looking for finished tracks now
  answers like an empty one instead of swallowing the error.

### Documentation

- `interface`, `multitrack` and `simple-path` follow the decision to
  the file sheet, both languages. Two things came out of writing them
  that the order had wrong: the field settles itself in four cases, not
  one -- no audio track in the file, a file set aside, a finished clip,
  and the single video with sound -- and the channel measurement never
  hung on the field at all; it runs for every multichannel video, and
  the field only decides whether the tracks become rows.
- Four places in the program still named the tick "as a track", the
  line beside the Multitrack tick among them. The pictures are stale
  and follow in the next version.

## [2.8.0-beta] - 2026-08-25

### Added

- Every recording carries its own **Separate speakers** button, in a
  fifth column of the assignment table. Until now one button sat in the
  player box on the right and the program picked the file itself. Which
  recording gets taken apart is now a choice.
- More than one recording no longer blocks the separation. It returned
  "several microphones" and hid the whole line, so somebody with two
  audio files -- one of them a stereo bed with quiet music -- had no
  separation at all. Nothing starts by itself there, which is right at
  a measured 28 times real time, but the button in the row starts it.
- A camera's audio can be a track where there is only one camera. The
  window built no camera row at all for a single video without an audio
  recording, so the tick did not exist and there was nothing to set.
- Exactly one video carrying sound and no audio recording beside it:
  the tick sits by itself, greyed out, with "the only sound there is"
  next to it. It is derived, never stored, so adding a recording makes
  it vanish with nothing left behind. Greyed out without a reason was
  the dead end taken out of the preset list on 24.8.

### Changed

- The state line "Separated: 4 speakers" stands in the row of the file
  it belongs to, where the button was. Not beside it: with both in one
  cell the name field shrinks from 210 to 86 px.
- "Not on this machine" moved with it, once, under the tick. It is the
  one question that belongs to the project rather than to a file.
- A click on a voice row plays it, not only the Listen button.

### Fixed

- Multitrack counted video files where it should have counted tracks.
  A single camera carrying two clip-on microphones holds two tracks,
  and it was turned away before anybody looked: `main()` refused
  cameras-only runs at fewer than two video files. The plan is built
  first now -- audio pulled, channels measured, tracks cut -- and
  counted afterwards. Measured on the same file: the old version exits
  1, the new one exits 0 and writes a .mov with four audio streams,
  every segment boundary inside the 0.4 s pause, largest deviation
  0.263 s.
- One track is a valid result, and two places still treated it as too
  few. They now say why Multitrack falls away and hand the measured
  tracks to the ordinary path, which since 2.7.0-beta separates
  speakers and cuts by them. Only "no sound in any camera" still stops.
- The channel split never ran for video files. `channels_arrived`
  handed on a list that held audio files alone, so a camera with two
  microphones stayed one row for good.
- Start is blocked, with the reason under the button, where no sound is
  left at all -- rather than a dialog, or an abort at the end.

### Documentation

- Four chapter pairs followed the button: interface, speech,
  simple-path and multitrack, both languages. Corrected with them:
  the line does not stay away when everybody has a microphone, a Mac
  starts by itself only with one recording, and with
  VPM_NO_SPEAKER_SPLIT the column is not built at all rather than
  shown empty and clickable.

## [2.7.1-beta] - 2026-08-25

### Fixed

- Captions were measured on Windows alone. Everywhere else they kept
  the width they were designed with, and on Linux that left the
  "+10 s" button of the preview player 9 px short of its own text.
  `caption_room` returned the designed number unchanged wherever
  `sys.platform` was not `win32`, although its own comment says a
  surcharge in pixels fits one font and misses the next. It measures
  on every system now, and it never returns less than the designed
  width, so nothing moves where the design fits: measured on macOS,
  not one of the 150 captions wants more than its base. "Sans Serif
  9.0" is not the same font file on macOS and on Ubuntu.
- The test suite ran green on every push and the CI did not, at every
  push since it was set up, always on that one button. A light that is
  always red is a light nobody looks at, and it hid a second fault:
  `start_button_test` replaces `threading.Thread` for the whole
  process, and the replacement could only `start()`. On Windows that
  is not enough -- subprocess reads a child's output in threads of its
  own and calls `join()` on them -- so the first time the window asked
  ffprobe for a timecode while opening a project, the test died. macOS
  and Linux wait with selectors and make no thread at all. All four
  runners are green for the first time.

### Documentation

- The manual's pictures were taken again, all ten that changed. They
  now show the voice row saying how long somebody speaks and where the
  longest passage is, the line beside the Multitrack tick, and the two
  renamed choices. `files`, `blocks` and `settings` came out
  byte-identical, which says the run is repeatable.

## [2.7.0-beta] - 2026-08-25

### Added

- The simple path tells speakers apart and cuts by them. Until now the
  separation ran on the multitrack path alone: `--speakers-local`,
  `--speakers-from`, `--speakers-count` and `--no-speakers-local` were
  refused everywhere else, the window wrote the assignment file only
  with Multitrack ticked, and the arithmetic that puts the voices on a
  camera's own time axis was reachable from the multitrack path only.
  One recording, or the audio of a single camera, is now enough. The
  cut list itself needed nothing: it had handled a single camera all
  along.
- A line beside the Multitrack tick says why it cannot be used yet --
  "One track only: tick 'as a track' at a camera for a second one", or
  that no camera audio is left to take. The tick stays clickable
  rather than going grey without a reason.

### Changed

- With one camera the result is called a first cut by speaker, not a
  camera cut. Between one camera there is nothing to switch to. What
  the run produces is a cut at every change of speaker, so Resolve
  gets one clip per person to group, grade and reframe -- which is
  what a 360 degree camera wants.
- Multitrack counts input tracks, not recordings. It said "at least
  two separate audio recordings" in four places, and what the program
  counts is rows in the assignment table: a recording of its own, a
  channel of a multichannel recorder, or the audio of a camera once
  "as a track" is ticked for it.
- The voice row said "0:59:08,376" where a timestamp was expected and
  meant the sum of that speaker's talking time. It now gives the
  duration and the position of the longest passage, each named as what
  it is.
- Only one voice found is no longer treated as a failure. There is no
  cut, because nobody hands over; the passages travel into the
  handover as markers and Resolve gets the camera in one piece.

### Fixed

- The camera cut hung on the Multitrack tick instead of on the
  question it answers. Four speakers told apart in a single recording,
  each with a camera, produced an empty Resolve tab and a line saying
  it could not be done -- while the cut itself had read those voices
  for two versions.
- The Resolve tab said the camera cut needed the speaker assignment
  from auphonic.com. That stopped being true in 2.0.0, when the
  separation moved onto this machine, and the line stood there another
  two versions sending people somewhere they no longer had to go.
- A recording with more than two channels was announced to
  auphonic.com as mono, because `kept_channels` answered 2 for two
  channels and 1 for anything else. The count is now reported as
  measured, with a warning that more than two channels go as one and
  should be cut into tracks first. What four ambisonic channels ought
  to become is a decision, not a default, so the fold itself is
  unchanged.
- With one camera not a single speaker marker was ever set. They lived
  on the multicam timeline, and with one camera none is built, so the
  run said the passages travelled as markers and set none. They sit on
  the cut timeline now, a colour per person -- which is what somebody
  reframing a 360 degree shot by hand needs to see.
- Fifteen switches carried `[multitrack only]` in `--help` although the
  simple path hands the whole of `args` to `write_cut_list` and uses
  them there: the cut sliders, the four `--wide-...` and the four
  `--on-...`. And `--suffix` carried `[simple path only]` although
  `finish_without_auphonic` names the mixed file with it on the other
  path.
- The preview box stayed "Camera cut -- preview" beside a box called
  "First cut by speaker". The two names were worked out in two places;
  now in one.

### Documentation

- Six chapters carried the old restriction that speaker separation and
  the cut need multitrack. Both languages.
- `development/measurements.md` gains "Why one recording does not
  become four tracks": the measurement behind not building per-speaker
  tracks by muting the others. De-Bleed has nothing to correlate when
  only one track is non-zero at a time, and only 34.3 % of segment
  boundaries fall in a real speech pause against 97-99 % for the audio
  dip.

## [2.6.1-beta] - 2026-08-24

### Fixed

- Saving the key in the Keychain hung the window, and it had never
  worked. Two faults sat on top of each other, both measured at the
  window that had stopped responding. "security" asks for the word on
  the terminal rather than on the input it is handed, because it opens
  /dev/tty: started from a shell, the question landed in that shell
  behind the window, where nobody looks, and Sebastian's console sat at
  "password data for new item:" while the window waited for good. It
  now runs without a controlling terminal, so it cannot ask and reads
  the input instead. And the key is sent twice, because "security" asks
  once for the word and once to retype it. Sending it once left the
  second answer empty and stored an empty string while still returning
  0, so the read-back failed and every save since this was written fell
  through to the argument form -- which puts the key in the process
  list, the one thing that branch exists to avoid. The safe path had
  never once been taken.
- Connect could sit at "checking ..." for good. No call to auphonic.com
  had a time limit of any kind. The short calls give up after sixty
  seconds and fifteen on the connection; the long ones, where an upload
  may take as long as it takes, limit only the connection.

## [2.6.0-beta] - 2026-08-24

### Added

- The window can be run on Windows and Linux, and now somebody checks
  that. A workflow runs the whole suite on Linux, Windows and macOS at
  every push, on Python 3.14.7 and on 3.10. Until now every one of the
  98 tests had only ever run on one Mac, and the lower bound of 3.10
  was a claim rather than a measurement. It is measured now.
- Three checks for faults that only the eye had caught: a caption wider
  than the field carrying it, in both languages; an English word left
  on the German side of the catalogue where the same catalogue
  translates it elsewhere; a sentence glued together from translated
  fragments, which is how German ends up with the wrong article.
- Five checks that hold a list in the manual against a table in the
  source. All thirteen untruths found in the manual on 24 August were
  questions of truth, and every documentation test until now asked
  about form.
- A test that runs the speaker separation for real, on speech this
  machine generates itself, so the interface of a dependency cannot
  change under us unnoticed again.
- An index of 79 keywords in both READMEs, and a test that keeps every
  entry pointing at a section that exists. The style pass of 24 August
  renamed 103 of 164 headings on its own, and an index would have
  rotted in silence.
- Every chapter of the manual carries a picture now, four of them
  newly taken. One needed an eight-channel fixture that did not exist,
  and one is a terminal showing the call and the start of a run,
  because the picture run can only grab our own window.
- A roadmap, in both languages, saying what comes next and what this
  program will not become.

### Changed

- The box that said "no newer version found" now shows what is in the
  version that is running. The release text comes down with the same
  answer that was asked for the version number and used to be thrown
  away.

### Fixed

- A stereo recording made with a coincident pair was not recognised as
  stereo. The gate that decides which places are loud enough to measure
  hung on the peak of the whole file, and a handful of samples at full
  scale -- 0.0000 per cent of them -- pinned that peak at 0 dBFS while
  99 per cent of the windows sat below -33 dBFS. Of 120 places, 119
  were dropped as too quiet and none for the reason the message gave.
  The gate now hangs on the ninth decile of the window levels. Measured
  on the recording that showed it: the share in the zero window went
  from nothing at all to 0.939 against a threshold of 0.50, and the
  spacing to 0.0 m, which is what a coincident pair is.
- Every Windows clone carried a broken speaker model. Git for Windows
  rewrites line endings while checking out, the model is held against a
  SHA-256 sum, and one changed line was enough for the program to
  declare its own model damaged.
- 62 captions did not fit their field on Windows, the worst short by
  136 px. At a nominally identical font the text runs 1.89 times wider
  there than on macOS, and five fixed pixel widths measured for the Mac
  font caused all 62. The fields now compute their width. Nothing
  changed on the Mac, where the layout is measured, balanced and held
  in eleven manual pictures.
- The speaker separation stopped with an AttributeError on the newest
  pyannote. Version 4 hands back a different object and keeps the
  annotation in a field of it. The worker now asks the object what it
  is, so both versions run, and where neither shape fits it names the
  class it got.
- The ratchets counted offences instead of holding them. Swap one for
  another and the count stays and the test stays green. They now hold
  the findings themselves, keyed on the function they sit in.
- A run against a snapshot could pull a ratchet down for good. The
  suite is meant to be run against snapshots, so this had been open
  every time anybody followed the instructions.
- The player menu killed the window on a Qt without multimedia.

### Documentation

- The manual went through a style pass, and the complaint behind it was
  measured before it was acted on: against the DaVinci Resolve manual,
  903,627 words of running text, and against GIMP, LibreOffice,
  Kdenlive and man ffmpeg. Appended dashes fell from 199 to 38, "Where"
  as a condition from 51 to 0, fronted clauses from 105 to 26. Nothing
  was cut to get there: the manual came out longer, 28,993 words to
  29,962.
- Thirteen places where the manual said something the program does not
  do are corrected, and the command line table now matches the parser
  switch for switch, 68 against 68.
- Eleven chapters gained a section on what to do when it goes wrong.
  None of the four style guides asks for one.

## [2.5.0-beta] - 2026-08-24

### Added

- Clipping is counted per channel and named in the preflight, with the
  number of samples sitting on the stop. It used to be invisible here,
  and actively so. The master is measured as a sum, and a limiter pulls
  it under -1 dBTP. A lapel microphone against the stop all evening
  therefore came out looking clean. Only integer formats are counted.
  Measured on one overdriven source written three ways: 16 bit and 24
  bit come out identical, 120,720 samples on the top, 0.00 dBFS. The 32
  bit float copy peaks at +11.94 dBFS with nothing clipped at all. The
  line is integer against float, not 16 against 24 bit: an integer
  format has a stop at full scale and float has none. It is a note,
  never a reason to stop. An overdriven recording is sometimes the only
  recording there is.
- A second way to find the offset between a recording and a video, by
  phase, tried only if the first one came back empty. The way over the
  envelopes lives on speech pauses, and music has none. On a concert
  recording it returned 0.13 and -0.18, which is nothing. Phase found
  the offset on the same material: 9:29, to within 12 ms. Those 12 ms
  are the sound travelling four metres from the monitors to the
  telephone that recorded them. Both numbers go into the log either
  way, so a failure says how close it came.
- The log and the command line say which copy of the script is running.
  Several runnable copies of one version are the normal case here.
  There is the snapshot the tests run against, the `.old` an update
  leaves behind, and the download in the Downloads folder. They share
  one log file, and without the path there is no telling later why one
  run came out different from another.

### Changed

- A recording that crosses midnight is one night, not a day apart. A
  timecode counts from midnight and starts over there. The file after
  midnight therefore overlapped nothing and was reported as a clock
  that had never been set. Nothing is added to any timecode: the values
  are brought onto one axis where they are compared. That happens only
  if it actually puts the file among the others. A recorder left at
  00:00:00 is still reported for what it is.
- A channel that carries nothing says which of the two rules caught it,
  and by how much. One line said "below the noise floor" for both, and
  for one of them that was simply wrong. A channel 45 dB under the
  loudest can sit 40 dB above its own noise floor. The rule itself
  stood twice, word for word, in two functions; now it stands once.
- A failed offset measurement says how close it came. It names how many
  seconds of the recording had one voice alone, and how sharp the best
  of them was against what was needed. "No pair measurable" hid two
  different recording faults with two different remedies behind one
  sentence.
- `--together` keeps the order it was given. Its own help promises
  "these files are one recording, in this order". One of the two paths
  through the program sorted that row by name anyway. The same switch
  therefore gave two different answers, depending on how it was
  reached.
- The pair fit hands back what it could not explain, and the line
  prints it next to the number of points. It was worked out on every
  run and thrown away. Three points fit three unknowns exactly, so a
  residual of nothing there means nothing.

### Fixed

- The player menu no longer stops the window from being built on a Qt
  without multimedia. The stand-in player has no play, pause or nudge,
  the menu bound them directly, and the whole window died on the way
  up. It has them now, and the menu greys out: there is nothing behind
  those entries, and saying so is better than pretending.

### Documentation

- Thirteen places where the manual said something the program does not
  do. The menu bar has four menus and the manual said three,
  `--speakers-local` had a different default from the one printed,
  `--no-transcript-file` was missing from the full list of switches,
  the preflight compares the timecodes and no chapter mentioned it, and
  static-ffmpeg arrives even when the question is answered with no.
  Each one was checked against the source and carries a line number. A
  manual that says something untrue is worse than one that says
  nothing.
- Eleven chapters gained a section **When something goes wrong**. None
  of the four style guides asks for one. It names the action, not the
  message text: what somebody does when it jams there. `overview` has
  none on purpose, because it is the page for deciding whether the
  program is for you, and it has no switch block for the section to sit
  in front of.
- The command line chapter was checked switch by switch against
  `build_argument_parser`. Both tables now hold 68 rows against 68
  switches and the sets match in both directions. Three switches named
  no default although the chapter promises defaults in brackets, and
  two descriptions were incomplete: `--on-monologue` fires only on a
  shot that has held past `--wide-after`, and `--on-together` only
  where no camera shows exactly those speakers.
- The preflight chapter says what the clipping count is. It names
  channel, count and peak level, holds nothing up, and counts in
  integer formats only. The measurement behind that is in
  `development/measurements.md`.
- The manual, the changelog and the developer documents went through a
  style pass. It came out of a complaint that the writing was too
  narrative, and the complaint was measured before it was acted on:
  against the DaVinci Resolve manual (903,627 words of running text),
  against GIMP, LibreOffice, Kdenlive and `man ffmpeg`, and against the
  Google, Microsoft, Diataxis and plain-language guides. Three separate
  faults came out of it, and they are not the same thing. Sixty-three
  of ninety-seven English headings named a thing instead of an action.
  A hundred German sentences opened with a subordinate clause carrying
  no conjunction, against two that had one. Forty-four appended dashes,
  nine of which said the main clause over again. The counts afterwards:
  appended dashes 199 to 38, `Where` as a condition 51 to 0, fronted
  clauses 105 to 26, lines over 79 characters 22 to 0.
- Nothing was cut to get there. The manual came out **longer**, 28,993
  words to 29,962, and every measured number, reason and limit was
  checked back one by one. The single number that changed is the pair
  spacing in `channels`, which said 35 cm and is measured at 30. Two
  proposals in three that would have cost information were refused and
  written down with what would have gone, so the next round does not
  open the same places again.
- The rules behind that pass are rules 26 to 32 in the working notes,
  each one countable. Rule 32 is the one that took two attempts to get
  right: repeat nothing the sentence before already implies. Its test
  looks back at that one sentence, not at the chapter. "Nothing is
  uploaded on its own" repeats what "trying presets costs nothing"
  already says. "The program uploads only when asked to" does not,
  because it says *when* instead of *not*.
- `development/measurements.md` gained what was measured on 23 and
  24 August: that clipping does not depend on the bit depth, that the
  envelope alignment stops where the music has no pauses, what one bad
  sample point does to the drift line, and how big the PySide6
  download really is. Each of them says what was **not** measured as
  well.

## [2.4.0-beta] - 2026-08-23

### Added

- `--update-check` takes back a `--no-update-check`. Without it a no
  could not be undone, and on 23.8.2026 that caught its own author. The
  switch had been given once in passing, the program never looked
  again, and nothing anywhere said why. A no that cannot be taken back
  is a trap.
- The update dialog has a tick, **Do not ask again**. It stops the
  program looking by itself; asking from the menu still works, and the
  tooltip says so. It is remembered whichever button is pressed.
  Somebody who ticks it and then updates still means it for next time.

### Changed

- The update dialog shows what changed, in the dialog. It used to give
  an address and leave it at that. Whoever has to open a browser to
  find out what they are installing will mostly not, and will say yes
  without knowing. The release text comes down with the same answer
  that is asked for the version number, so it costs nothing.
- That dialog is one of its own rather than a QMessageBox. The box
  hides the text behind a "Show Details" button of its own making,
  which it does not translate. It gives that text four lines to be read
  in. It is 680 by 560 now, the frame stands whether the text needs to
  scroll or not, and the button says **Update**.
- Asking from the menu is answered even if the program was told to
  stop looking by itself. The no was about looking unasked, not about
  refusing an answer to somebody who asks. `VPM_NO_UPDATE_CHECK` still
  holds against both: that one is set by whoever runs the machine.

### Fixed

- The German tooltip on the tick named a menu entry that does not
  exist. It said "Nach einer neueren Fassung sehen"; the menu says
  "Jetzt nach einer neueren Fassung sehen". It pointed at the way out
  of the trap and got the name wrong.
- The settings sheet said the key goes into "Schluesselbund" with no
  article. The sentence put the place in as a placeholder, and the
  three possible places need three different German articles. Rebuilt
  so that none is needed.

### Documentation

- The manual describes keeping itself up to date. It names what is
  asked of github.com and when, and what is sent (nothing). Also what
  is checked before anything replaces anything, and how to undo it. It
  was a whole ability nobody had written down.
- Both switches were missing from the command-line chapter entirely.
- Undoing an update is written as an action. "The old one stays beside
  it" is not enough. `put_new_self` copies the running version to
  `.old` and replaces the original, so the way back is to put the file
  back under its own name.

## [2.3.0-beta] - 2026-08-23

### Added

- The model for the speaker separation is fetched the first time a
  separation is asked for. The one Python file is then all anybody has
  to download. It comes from the same repository the program does. The
  tag is that of the running version, or the `main` branch if there is
  no such tag. Every file is held against the SHA-256 sums that come
  with it, and one that does not match is not written. It lands in
  `models/` beside the program and is never fetched a second time.

- `L` plays forward and doubles the speed on every press, 1x to 8x; `K`
  stops and goes back to normal. The speed stands on the play button.
  `J` is absent. Measured, Qt takes a negative rate and reports 0.00
  back, and swapping the whole media backend for one key is the wrong
  trade.
- Names a reading program can announce on the first and third sheets as
  well. They cover the file list, the production fields, the eight cut
  numbers as "caption, seconds", the four choices and the Resolve
  button.

### Changed

- Nothing is asked of auphonic.com unless somebody asks for it. A key
  that was remembered used to be checked at start-up. That meant a
  start spoke to a third party about a key it had only been asked to
  keep. A key that had expired or been mistyped greeted its owner
  with an error box every time. The presets are fetched when the list
  is opened, which is the moment they are wanted and the only moment
  they are needed.
- A key is measured before it is sent. The measurement asks whether
  there is one at all. It also asks whether it was pasted with a line
  break, a space in the middle or a character that cannot be typed.
  Not its length or its character set: what a real key looks like has
  never been measured here. A guessed format would turn away a key that
  works.
- The tabs lost their numbers. Numbered tabs promise an order that does
  not exist. One may jump, and the ticks behind the names already say
  what is finished.
- `Dry run (writes nothing)` is `Dry run` on the button; the
  explanation was in the tooltip anyway.
- The trim slider takes its colours from the scheme. Measured: its
  outline against the handle 2.94 before, 5.17 light and 6.03 dark now.
  The 2.94 was under the 3:1 that WCAG asks of a control. On dark it no
  longer draws a white band across the window.
- `warning` is `#985508` on light, measured at 5.77 against the sheet.
  The old colour fell under 4.5 there. Dark keeps `#e2a355`: `#985508`
  there is 2.74.
- A switch between light and dark arrives while the program runs.
  Before, the scheme was read once at start and the way back to light
  was burned in.
- The type in the "one more speaker" row is made smaller only if the
  row would otherwise grow wider than the player leaves it.
  Smaller type is harder to read, and on a machine whose system font
  was turned up it undoes what somebody set it for.

### Removed

- `install.py`. The program brings what it needs by itself: numpy and
  PySide6 at the first start, ffmpeg over the package manager. The
  separation and its model come at the first separation. There is one
  file to fetch and one file to keep.

### Fixed

- `as a track` was clipped in the camera table. The macOS style reports
  a checkbox narrower than its own text, and the column took that
  number: 83 px offered for text that needs 87. The room now comes from
  the style rather than from a number somebody liked.

### Tests

- `release_test.py`, new: one version number named the same in the
  program, the changelog and both READMEs. Also the changelog in its
  shape, every picture there and used in both languages, and the rule
  that the key never reaches a file. Four rules that used to be
  enforced by somebody remembering them.
- `auphonic_quiet_test.py`, new: what is turned away before it is sent,
  and what gets through. Also that no timer fetches presets at
  start-up, and that the unasked fetch opens no box.
- `preview_shot.py` and `assignment_shot.py` used to look for a tab and
  return in silence if they found none. The script then photographed
  the wrong sheet and still returned 0. They stop and say which sheets
  there are.
- `first_run.sh --then-install` does what the manual tells a stranger
  to do: fetch the one file and start it. It used to fetch the
  installer and run that.

### Documentation

- The screenshots showed a window that exists nowhere. Qt draws them in
  the Fusion style under `offscreen`. Of 63 palette entries 46 differ
  from the Mac, and the menu bar sat inside the window instead of at
  the top of the screen. They are taken under `cocoa` now, with the
  window kept off the desktop: real style, real palette, exact size,
  nothing in anybody's way. It needs a screen
  somebody is logged in to, so the run is started by hand.
- Twenty-five places in the manual named the numbered tabs, in each
  language. All of them pulled along, four captions rebuilt where the
  number was the only thing naming the sheet.
- `docs/notes/begriffe.md`, new: which German word this project uses
  for which thing, counted rather than felt. Spur against Track
  stands 88 to 1. Written after Tooltip had been replaced by
  Kurzhinweis and put back: Tooltip is the ordinary German word too.
- The requirements chapter says what the program fetches for itself,
  when, and how much, in both languages. It described `install.py`,
  which is gone.
- The section on ffmpeg named `static-ffmpeg` as what happens if
  ffmpeg is missing. The package manager comes first and is asked
  about; `static-ffmpeg` is the way out if there is no manager.

## [2.2.0-beta] - 2026-08-23

### Added

- A menu bar, with seventeen entries. On a Mac that is not a matter of
  taste. About, Settings and Help are expected in places the window has
  no say over, and Qt's minimal fallback carries none of them.
- Keys. The player had buttons for a frame back and forward, which is
  where anybody who edits reaches for the arrows and found nothing.
  Space plays and pauses, and the arrows step a frame, with Shift a
  second and with Alt ten. I and O set the marks, Shift+I and Shift+O
  jump to them. They hang on the player rather than on the window, so a
  bare letter cannot fire while somebody is typing a name into a field.
  Everything else is on Ctrl or Command, where it cannot collide:
  Ctrl+O adds files, Ctrl+R starts, Ctrl+Shift+R is the dry run.
  Ctrl+1 to Ctrl+3 pick a sheet, and Ctrl+, opens the settings.
- Seventeen controls carry a name a reading program can announce. There
  were none.
- `VPM_CACHE` points what the program keeps between runs somewhere else.
  The suite sets it, so a test run no longer leaves envelopes and
  measurements in the cache of whoever started it.

### Changed

- The reason a run cannot start stands in the window, in full. It used
  to be in the tooltip of the start button. A tooltip cannot be
  reached with the keyboard and is not read out reliably. The most
  important sentence in the window was therefore the one hardest to get
  at.
- On the second sheet a file that does not fit is no longer red and
  nothing else. It now carries the same sentence the first sheet writes
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

- `start_reason_test.py` held the old behaviour in place. It checked
  that the footer points at the tooltip, which was the defect. It now
  checks that the footer names the reason itself.

### Documentation

- The manual has a chapter section on the menu and the keys, in both
  languages. There was none: a way of working the program that is
  nowhere written down does not exist for whoever reads.
- All five screenshots taken again, English and German. Four things
  changed on every one of them: the menu bar and the state line at the
  bottom. Then the text beside red rows on the second sheet, and the
  shrunken "one more speaker" row.

## [2.1.0-beta] - 2026-08-23

### Added

- The program looks whether a newer release is out, and offers to fetch
  it and start again. Looking needs no permission: it asks github.com
  for a version number and sends nothing. But nothing is ever fetched
  or replaced without being asked, and the question comes at the start,
  never during a run. What comes down has to be readable text, has to
  look like this program and has to compile before it replaces the file
  that works. The old one stays beside it as `.old`. `--no-update-check`
  switches the looking off and the answer is remembered.
- `install.py` fetches the newest release by default rather than the
  tip of the main branch. `--ref` takes a named version instead: a
  tag for a particular release, or a branch. A release marked as a
  pre-release is never what the newest means.

### Changed

- ffmpeg comes from the package manager if there is one. It asks, and
  then does it: brew on a Mac, apt-get, dnf, zypper or pacman on Linux.
  Each comes with the switch that stops it asking a second time. On
  Windows it offers to open ffmpeg.org. static-ffmpeg is what is left
  when none of that is there. It now says what it brings: sixteen
  packages, and a binary loaded from a private repository without being
  held against anything. `VPM_INSTALL_TOOLS=1` answers yes in advance,
  for a run with nobody in front of it.
- A package that was half removed counted as installed. pip leaves a
  package's `__pycache__` folder behind when it uninstalls it, and
  Python reads that folder as a namespace package. The import goes
  through and the module is hollow. Only a module that names the file
  it was read from counts as there now.

### Fixed

- The message that ffmpeg was being installed came at every start, even
  though nothing was being installed. static-ffmpeg only puts its
  programs on the search path for the running process.

### Tests

- `update_test.py`, 24 checks: which version is newer, what counts as a
  newer release, and that a no is remembered. Then that an error page
  and a file that does not compile are both refused, and that the old
  file is kept. Nothing in it touches the network.
- `first_run.sh` puts the machine back the way it was before the program
  ever ran. That covers the environment, the caches, the packages, what
  a package downloaded after pip was done with it, and the keychain
  entry. A change to how the program installs itself can then be
  watched from nothing. It is not part of the suite.
- The suite stops instead of going red if there is no ffmpeg.

## [2.0.0-beta] - 2026-08-23

### Added

- `install.py` brings the program and the separation model in one
  command, on macOS, Windows and Linux alike. It is written in Python
  because Python is the one thing that has to be there anyway. Every
  file is held against the SHA-256 sums that travel with the model and
  is not written if it does not match. It reports ffmpeg rather than
  installing it, and hands over to the program at the end. `--check`
  holds an installation already there against the sums, `--to` puts it
  somewhere else, `--no-start` stops before the handover.
- The speaker separation model travels with the repository, in
  `models/speaker-diarization-community-1`: five files, 33 MB, with
  their licence, model card and checksums beside them. It is read from
  a folder next to the program: no account, no token, no network.
- The program recognises speech itself. On macOS 26 it uses the
  recogniser the system brings, driven by a small Swift program built
  on first use. That takes 22 seconds for an hour of audio, with
  nothing to install. Everywhere else it falls back to Whisper
  (`large-v3-turbo`, 1.5 GB, measured at six times real time on a
  processor). The words carry their punctuation, which is where
  sentence and clause boundaries come from.
- The program separates speakers itself, locally, without uploading
  anything. Measured against the individual microphones of two complete
  interviews: 98.7 per cent of 45 473 words land on the right person.
  Three quarters of the remaining errors sit where two people really
  do talk at once, or where the speaker had just changed. The model
  travels with the program (`models/`, CC BY 4.0, checksummed before
  every use) and is never fetched at run time.
- A voice table under the assignment, one row per voice found. It is
  named "Speaker 1, 2 ..." until somebody names them, and each row has
  a button to listen. Naming a voice without hearing it is guessing.
- Four choices on tab 3 decide what is shown when nobody is clearly
  speaking. They are the wide shot, the listener, alternating between
  them, or no change at all.
- The wide shot is placed by the language now. It enters on a sentence
  boundary, holds at least five seconds and leaves at the next sentence
  end. If that would run past fifteen seconds it leaves at the last
  clause break before it, never in the middle of a sentence. Measured,
  every inserted wide shot lands in the five-to-fifteen-second window it
  is meant for.
- The exact frame comes from the sound, not from the text: in a window
  around the target the quietest stretch is looked for. That lands in a
  real speech pause 97 to 99 times in a hundred, where the recogniser's
  word boundary manages 42 to 46. It costs a fifth of a second for a
  whole episode.
- A reaction cut. When somebody asks a question and another answers, the
  picture goes to the answering person while the question is still
  running.

### Changed

- A speaker has to hold the floor for one and a half seconds before the
  picture follows. A short "mhm" used to switch the camera, and the
  minimum edit duration then held that camera for three seconds.
- Short shots are merged into the one that **follows**, not the one
  before. Measured over four runs, the time the wrong camera is shown
  falls from 326 to 99 seconds. It falls just as far when the input is
  the truth instead of a recognition, so this is a better rule and not
  a crutch.
- The wide shot answers uncertainty. The separation frays when seven
  segment starts sit inside twelve seconds, or it produces a small
  mixed cluster that belongs to nobody. In both cases the wide shot is
  shown instead of guessing. Measured, that beats even the best
  possible guess. The longest stretch showing the wrong person drops
  from eight seconds to 2.3, which is below the minimum edit duration.
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
  0.6 pauses a minute, our own measurement finds 16. In 66 minutes the
  wide-shot search found no place at all on them. Levelling,
  de-bleed, noise removal and transcription are untouched.
- `--wide-min` and `--wide-flow`. With a five-second minimum hold they
  could no longer change anything.

### Fixed

- The preview died on every call with "Preview not possible: 'min-shot'".
  It read a key that does not exist.
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
  own audio with `say` rather than shipping a file. Another holds the
  preview's cut list against the run's.
- `first_run.sh` puts the machine back the way it was before the program
  ever ran. That covers the environment, the caches, the packages, the
  models and the keychain entry. A change to how the program installs
  itself can then be watched from nothing. It is not part of the suite:
  `run.sh` picks up `*_test.py` and nothing else.

## [1.1.0-beta] - 2026-08-22

### Changed

- **Settings ...** moved into the footer. It sat beside the tabs, in
  the top right corner, where a button is not looked for. It now stands
  with the other buttons at the bottom right, flat and set apart,
  because it is not a step of the work.

### Fixed

- Two switched-off buttons now look switched off in the same way.
  **Start** kept its filled shape and its own colour while **Dry run
  (writes nothing)** went pale and flat. One of the pair therefore
  still looked pressable. Both now fade into the same muted blue:
  filled for the main action, outlined for the dry run, so the rank is
  still readable. The label on a switched-off button was measured for
  contrast rather than guessed: 4.7 against its own background. The old
  grey on grey gave 2.6.
- The opening line is no longer written in warning colour. "No files or
  project opened yet" is where everybody starts, not a fault, and it now
  stands in quiet type. The warning colour is kept for the case where
  something really is missing. The quiet grey was darkened a shade so it
  still reads on the footer. Measured against the desktop's #efefef it
  went from 4.0 to 4.5.

## [1.0.0-beta] - 2026-08-22

### Changed

- The terms are DaVinci Resolve's now, not our own. Looked up in
  Resolve's manual rather than assumed. `Cut in` and `Cut out` become
  **In point** and **Out point**; the manual has `In point` 171 times
  and `Cut in` not once. The two buttons that set them become **Mark
  In** and **Mark Out**, and `Minimum shot length` becomes **Minimum
  Edit Duration**. The German side follows Resolve's German window: „In
  markieren", „Out markieren", „Mindestschnittdauer", and the wide shot
  is „Weitwinkel". The switches are `--in-point`, `--out-point` and
  `--min-edit-duration`; the keys in the project file are `in_point`
  and `out_point`, so the file format counts up to **3**. An older
  project file is refused with a clear message rather than half read.
- A stereo pair now has to prove itself twice. Measured on a 32 channel
  drum recording: the share of what two channels hear together said
  "stereo" eight times and was wrong every time. In one room every
  microphone hears the same drum. Two more legs decide now. The spacing
  that comes out of the same measurement has to be under 0.3 m. The
  pair also has to stand out from the pairs beside it.
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
  instead of on a condition. `channel_rows` spent 121 of its 123
  seconds waiting for a tick that never comes. 112 seconds became 33,
  and one test that had quietly stopped checking anything is checking
  again.

## Before 1.0

What follows is the record from before the first release, counted as
0.x. Nothing in it was rewritten. The versions are the ones that
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
  the same moment. A widget goes on showing the figure it was last
  given until the next redraw. Clearing the plan alone therefore still
  left the old 100 per cent standing for a tick. Found by
  run_bar_test.py, which only saw it when the machine was loaded enough
  to reach the start button inside that moment.

## 0.11.0

Seven findings from a review of the Resolve and render part. Each is
read from the source; none is confirmed against a running Resolve.

### Changed

- The test doubles in `cut_timeline_test.py` and `intro_test.py` can
  report what landed on a track. That is what the timeline report in
  the program asks them for.
- Ready for a public repository: the one-off cleanup script moved out of
  the tree, and the preset fixtures carry no personal name.
  `.gitignore` also holds back `zu_loeschen/`, `_to_delete/` and stray
  media files.

### Fixed

- A camera without a rendered file lost its measured offset. The offsets
  are kept under the rendered name, and the missing key fell back to
  0.0. That put the camera at the start of the axis instead of where
  it was measured. The source path is tried too now, and what stays
  unknown is named in the log.
- Width and height were each taken as their own maximum. A landscape and
  a portrait camera together produced a square frame that neither had.
  The largest frame a camera really recorded is used.
- If the earliest camera starts before cut in, the timeline start
  moves back. The "For checking" report kept measuring against the old
  start, so every distance it printed was wrong by that much.
- The Full-Mix fallback takes a camera's audio. That audio begins where
  the camera began, not at cut in, so it ran against the picture by the
  camera's offset. The head is trimmed off now.
- A project the program has just created carries Resolve's factory
  Rec.709, and that beat the material. HDR sources would have been
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
  assignment table, and the plus in a channel pair's name. Also the
  tick as an offer, and which Python versions this is for. Both halves.
- `CLAUDE.md`, what a session needs to know at its start: where the
  state lives, how the tests run, and the rules that do not bend.
- The shared test fixtures no longer live at fixed paths under `/tmp`.
  Each was preceded by an `rm -rf` on a path anybody can write to. On a
  shared machine or a CI with two jobs the second run therefore deleted
  the first one's material. The root carries the user id now, and
  `VPM_FIXTURES` overrides it. `tests/fixture_root.py` says the same
  thing to the Python side.
- The channel rows say "unused input -- ignored" rather than "stays
  out", and "measurement running ..." rather than "being looked at".
  The third change puts "below the noise floor" in place of
  "practically silent". The uncertain case says "uncertain", which is
  what it means.
- The suite ends by reminding whoever started it not to sit and watch.

## 0.9.0

Two reviews went over everything 0.7.0 and 0.8.0 changed. What they
found is below; every fix has a test.

### Fixed

- Taking a stereo pair apart freed a channel, the proposal was rerun
  over it, and the freed channel was joined to its *other* neighbour.
  One click, two changes, the second one unasked. Now the measurement
  proposes once and a tick corrects that proposal. Taking one apart
  takes exactly that one apart, putting one together frees both its
  neighbours.
- The tick used to read "with Channel 5 one stereo track" beside a
  measurement saying they are two microphones. It says "join with
  Channel 5" now: an offer, not a claim.
- On resume, an output whose channel count the answer gives as empty was
  read as "not mono" and sent again. auphonic.com appends rather than
  replaces, so that is a second render and a second bill. An output that
  is configured but not rendered yet is now found by its own suffix. It
  has no file name to read one from.
- An ffmpeg that died half way through reading the channels was taken
  for one that had finished: the return code was never looked at. The
  half-read judgement was then stored under the file's size and time and
  would never have been measured again.
- The channel read held the whole recording twice at the moment of
  joining the chunks: the doubling the chunked read exists to avoid.
  Each channel is now joined and its chunks dropped one at a time.
- A transfer broken off by an error left curl running and downloading,
  and left an open handle on a deleted file.
- The API key went into curl's config file unescaped. A key containing a
  quotation mark or a line break could have added directives of its own.
  If the file cannot be deleted afterwards it is overwritten.
- Removing the last audio file left the block map standing, so the work
  for the removed recording was queued again and again.
- The Resolve verdict was written into a box that lives in the settings
  window: invisible to anybody who had not opened it. The Resolve tab
  now says whether Resolve answers and offers the way to the settings.
  The check runs again every time that window is opened, rather than
  once per session.
- "not measured -- nothing is running for it" was shown in the ordinary
  case, because the work is registered a moment after the row is drawn.
  The row says "being looked at ..." again.
- Four containers were declared twice in `gui()`, so the first four were
  dead. `plan`, the one progress bar, was shadowed inside `start()` by
  the assignment plan.
- `blocks_facts_from` raised on hand-made facts whose three lists are of
  different lengths, and choked on a non-dict.

## 0.8.0

### Changed

- The floor is Python 3.10, because PySide6 does not build below that
  and the window could not open there whatever the command line did.
- The suite runs on **3.14.7**, the version this is used on daily. It
  used to run on 3.11 while the program ran on 3.14, proving something
  about a Python nobody uses.
- `--version`, the log header and every run say which Python is running
  and name the recommended one if they differ:
  `Python 3.11.15  (recommended version 3.14.7)`.
- Pools are sized with `os.process_cpu_count()` if it exists (3.13 and
  up). It says how many processors this *process* may use, not how
  many the machine has. In a container held to two of thirty-two, the
  old number meant thirty threads taking turns.
- `consistency_test.py` reported `__annotate__` and `__classdict__` as
  names without an origin. Both are put there by the 3.14 compiler, not
  by anybody writing code.
- Two sorts of setting stood in one box on the first sheet. One is the
  key for auphonic.com, entered once in a lifetime; the other the
  preset, chosen for every production. Choosing a preset therefore
  meant paging back from the table where the decision is actually made.
- **Settings ...**, top right of the tab bar, opens a window holding the
  key, the tick that stores it, **Connect**, and the Resolve check. The
  Resolve box has left the third tab. The check itself still runs by
  itself on the first look at that tab. A run that ends by building a
  project should not find out at the end that Resolve was never
  running.
- The preset and **Fetch transcript** now stand under the assignment
  table, right below the Multitrack tick. The whole "what should this
  run do" is in one place.
- The first tab holds files, production name, spoken language and output
  folder. Nothing else.
- `settings_window_test.py` holds all three to it.

### Fixed

- The channel rows of a recording are drawn from the measurement over
  all its blocks, and the row hangs on the first block. Each finished
  block asked for a redraw of its own row, which only the first block
  has. The last block to finish therefore redrew nothing. A recording
  of two blocks said "being looked at ..." for as long as the window
  stayed open. The work was long done and the bar had gone.
  Reproduced, then fixed: every finished block now redraws the row of
  the recording it belongs to. `blocks_rows_test.py` holds it there.
- A row waiting for a measurement that nobody started said the same as
  one that is being measured. Now it says which of the two it is.
- If the channel count of a file cannot be determined, the run says
  so instead of swallowing it. That silence was what made the state
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
  on one 92 MB block of 32 channels: 22.9 s before, 2.0 s after, 4.0
  MB/s to 46.2 MB/s. It came out with the same levels, the same silent
  channels and the same pair numbers to six decimals. A pair of 1.8 GB
  blocks drops from about fifteen minutes to about ninety seconds.
- `channel_read_test.py` reads the same file both ways and compares
  sample by sample, so it stays that way.

### Fixed

- On a Mac the API key no longer travels to `security` as an argument
  where it does not have to. It goes over the input first and is read
  back to see whether that worked. Only if the wrong key comes back does
  the old way follow. An argument stands in the process list, which
  every auditing agent on a managed machine writes to a log.

## 0.6.0

Four reviews went over the program from four sides. They asked what
happens to the API key, and what a stranger meets on a fresh machine.
Then whether the newest code is right, and whether the manual still
describes the program. What they found is below.

### Changed

- The manual no longer claims the key is never in the process list. On
  the way to auphonic.com it is not. But `--auphonic-api-key` puts it in
  this program's own command line, and storing it in the macOS Keychain
  hands it to `security` as an argument. Both are now said plainly, with
  `AUPHONIC_TOKEN` named as the way round the first.
- The manual says which Python versions run, and what Linux costs.
- The temporary file holding a curl answer is removed even when the call
  is interrupted, and a failed removal no longer replaces the real
  error.
- A pair is written with a plus, not an ampersand: `Channel 1+2` on
  screen and `_Channel1+2.wav` on disk. Measured: both are legal file
  names everywhere. But an unquoted ampersand splits the command in two
  in every shell, and in a web address it separates parameters. The old
  spelling is not recognised any more and does not need to be. The cut
  pieces live in a temporary folder that goes when the program does.

### Fixed

- `blocks_facts` gave back the last block's pair judgement instead of
  the loudest block's: the inner loop reused the name of the list it was
  filling. A recording whose second block is the run-out or pure silence
  was therefore judged on that. The answer even depended on the order
  the blocks arrived in. It also grew the cached measurement of
  the block it read. The combining half is now `blocks_facts_from`,
  which can be held against made-up numbers without building gigabytes
  of audio.
- A recording of several blocks never came apart into tracks. The
  regrouping still looked for the `_ch` in the names from before 0.4.0,
  while the pieces are called `_Channel1` now. Two 32-channel blocks
  stayed one row with one speaker name, and the run folded all channels
  into one voice.
- `--together` promised "in this order" and then sorted the blocks by
  name again. Without a timecode that is the one case where name order
  is meaningless. It is exactly why the switch exists.
- A tick joining two channels to a stereo track is no longer honoured
  if one of the two is an unused input. The interface never offers
  the tick there, but a tick made earlier outlives the measurement it
  was made under.
- A file named in `--together` and not on disk went unreported, unless
  one of its partners ended up in a recording of its own.
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
  silently. The console went into the log file before Qt was resolved,
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
- If ffmpeg is missing, the advice names the machine this is: brew on
  a Mac, the package manager on Linux, ffmpeg.org on Windows. Linux used
  to get the other two.
- Installing past the system package manager is said out loud when it
  happens, with the virtual environment named as the way round it.
- `requirements.txt` and `requirements-dev.txt`.
- On resume, a mixdown of one channel is no longer taken for the
  two-channel one a stereo run needs. If the answer says nothing
  about the channel count, both still count as present. An upload sent
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
  the system language. Linux writes the names it chose into
  `user-dirs.dirs`, which is now read instead of one language being
  guessed at.
- The metrics CSV stays comma separated. The manual says what that costs
  on a German system and which way in avoids it.
- A pass over every comment and docstring against the house rule "short
  and to the point". Storytelling, self-justification and anecdotes from
  particular recordings are gone; the reasons and the measured numbers
  stay. 99 places, 51 lines fewer, no code touched. Proved by comparing
  the syntax tree with docstrings stripped.

### Fixed

- The reason the start button is grey stands in the footer beside it. It
  was in the tooltip alone, and a disabled Qt button shows no tooltip at
  all. The text hung on a wrapper around it, where nobody looks.
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
  the loudness measurement. Then into its own audio track on the camera
  file, and into the mix. The rule is "keep what the source has" instead
  of folding everything to one channel.
- At auphonic.com the finished mixdown is asked for in two channels as
  soon as one track is stereo. On the simple path the mono fold is
  switched off for every output the preset asks for.
- Without Multitrack, recordings that ran at the same time now also go
  into the video as tracks of their own, after the mix. Whether they ran
  at the same time is read from the timecode, not guessed.
  `--no-single-tracks` leaves them out.
- A camera ticked "as a track" is an audio candidate like any other. Its
  channels are judged and cut by the same rule as a recorder file. A
  camera carrying two clip-on microphones therefore gives two tracks
  with two speaker names.
- The same on the command line. `Osmo.mov Wide.mov --multitrack` reads a
  two microphone camera as two speakers without an interface, and still
  writes one file per camera.
- Camera tracks get the full camera selector. A microphone plugged into
  one camera may belong to a person another camera is filming.
- A camera counts towards Multitrack as soon as it is ticked as a track,
  on the command line as well as in the interface.
- Blocks whose names carry a date and a time instead of a counter are
  joined into one recording. That happens when the next one starts where
  the previous one ends.
- `--together FILE ...` and the "belongs to" selector put files into one
  recording by hand, the counterpart to `--apart`.
- Channel count and sample rate have to match before two blocks are
  joined.
- The channels of a recording are judged over all its blocks, not over
  the first one. On a 32 channel mixer recording the first five minute
  block was the soundcheck and read as one used channel pair. The second
  was the show and read as ten tracks.
- An absolute floor for a channel that carries anything: under -70 dBFS
  there is only the converter's noise. A pair judged on noise answers
  differently every time it is measured.

### Changed

- Every neighbour is judged, not every second one. On a mixer, channels
  2 and 3 can be the stereo pair just as well as 1 and 2. Fixed pairs
  asked the wrong question and got a confident wrong answer.
- One row per channel in the file list, with a tick that says "this one
  and the next are one stereo track". Ticking channel 2 takes the tick
  away from channel 3. A channel can belong to only one pair. If two
  neighbours both look like a pair, the left one wins.
- The tick and the reason behind it moved into the wide column. In the
  narrow one, where the file marks live, the word beside the box was cut
  off after its first letter.
- Tracks are named after their channels: `Channel 1`, `Channel 2+3`. So
  are the files they are cut into, closed up and with a fingerprint of
  the source folder in between. That gives
  `Mixer_3f9a1c02_Channel1+2.wav`, instead of `_cha` and `_chef`.
  "Channel" stays English in every language. It is the word on the
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
  both directions. Its own uses an equal-power law. Measured on a
  signal at -24.08 dBFS, one channel to two comes out at -27.09 and two
  channels to one at -21.07. The second of those depends on the
  output format.

### Fixed

- A production with a transcript did not start when the preset already
  carried the transcript output formats. The run then waited for it
  until the time limit.
- The check report cleared the channel rows out of the file list when it
  came back. The stereo tick and everything beside it disappeared, and
  only a later rebuild brought them back. Finding lines now carry a mark
  of their own instead of sharing one with every other extra row.
- A track cut out of a multichannel file lost the recording time. Those
  files are exactly the ones that carry it, and everything after the cut
  asks the piece rather than the file it came from. A real pause between
  two blocks was therefore swallowed instead of being filled with
  silence and reported.
- Two files with the same name on two cards wrote over each other's
  tracks, silently. A piece that is already there is not written
  again. The name of a piece now carries a fingerprint of where its
  source lies.
- Above 26 channels the channel letters ran together: channels 1 and 2
  gave "ab", and so did channel 28. On a 32 channel mixer recording one
  track therefore held another one's audio.
- A camera with more than two channels was folded to mono before anybody
  looked at what was on it. Four microphones on four channels became
  one voice. The audio is now extracted with every channel it has and
  folded only if nothing has to be cut out of it.
- If a recording is made of blocks, the pair judgement took the answer
  of the loudest block. It did so even when that block had one of the
  two channels silent, which is no answer at all. It now takes the
  loudest block that actually measured the pair.
- Changing the stereo tick dropped the cut tracks of one block only. The
  other blocks kept their old cut, and the rows then held block one's
  channel 1 next to block two's channels 1 and 2.
- Continuation blocks that were found rather than selected were never
  measured or cut. A multi-part multichannel recording was cut from
  its first block alone.
- The block-size rule never saw the block it was judging. On the first
  step forward it compared a block with itself and always said yes. A
  short finished take in front of the real recording was therefore
  glued onto it. Which answer came out depended on which block was
  selected.
- Two files carrying the same recording time were laid end to end
  instead of on top of each other. Two recorders started together write
  exactly the same number, and those recordings run at the same time.
- Two by-hand groups could both claim the same block, and it was then
  decoded and mixed into two productions. The first group to claim it
  keeps it, and the second is told.
- A file named with `--together` that is not on disk was accepted into
  the recording and then vanished without a word. It is refused, and the
  refusal is reported.
- "260808" and "20260808" are the same day. Two names spelling the same
  moment put one file into two recordings, and which grouping came out
  depended on the folder listing.
- On a case-sensitive disc, `REC0002.wav` and `rec0002.wav` collapsed
  into one entry and the folder listing decided which one was used.
- A counter that reads as a time of day, `260808_000001`, made the
  clock rule fire, find nothing and stop. It did not hand back to the
  counter rule. Three blocks of one recording stayed three recordings.

### Tests

- 75 tests, all of them checking something. The five that only printed
  their result (colours, metrics, dualmono, crosstalk, intro) now
  measure it. The three that cannot be checked outside Resolve
  (render, render_hdr, multicam) say so in their docstring.
- New: stereo_mix, beside_mix, camera_track_mode, camera_channels,
  blocks_facts, clock_blocks, together, german_hunt.
- `german_hunt_test.py` reads seven ways for German where only English
  belongs, including the running program. The job is driven twice in
  German and the output searched for English function words.

## 0.3.0

### Added

- A single continuation file can be taken out of a recording by hand. It
  stays out even though the search would find it in the folder again.
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
[2.12.0-beta]: https://github.com/Bascht74/videopodcast-magic/compare/v2.11.1-beta...v2.12.0-beta
[2.11.1-beta]: https://github.com/Bascht74/videopodcast-magic/compare/v2.11.0-beta...v2.11.1-beta
[2.11.0-beta]: https://github.com/Bascht74/videopodcast-magic/compare/v2.10.1-beta...v2.11.0-beta
[2.10.1-beta]: https://github.com/Bascht74/videopodcast-magic/compare/v2.10.0-beta...v2.10.1-beta
[2.10.0-beta]: https://github.com/Bascht74/videopodcast-magic/compare/v2.9.0-beta...v2.10.0-beta
[2.9.0-beta]: https://github.com/Bascht74/videopodcast-magic/compare/v2.8.0-beta...v2.9.0-beta
[2.8.0-beta]: https://github.com/Bascht74/videopodcast-magic/compare/v2.7.1-beta...v2.8.0-beta
[2.7.1-beta]: https://github.com/Bascht74/videopodcast-magic/compare/v2.7.0-beta...v2.7.1-beta
[2.7.0-beta]: https://github.com/Bascht74/videopodcast-magic/compare/v2.6.1-beta...v2.7.0-beta
[2.6.1-beta]: https://github.com/Bascht74/videopodcast-magic/compare/v2.6.0-beta...v2.6.1-beta
[2.6.0-beta]: https://github.com/Bascht74/videopodcast-magic/compare/v2.5.0-beta...v2.6.0-beta
[2.5.0-beta]: https://github.com/Bascht74/videopodcast-magic/compare/v2.4.0-beta...v2.5.0-beta
[2.4.0-beta]: https://github.com/Bascht74/videopodcast-magic/compare/v2.3.0-beta...v2.4.0-beta
[2.3.0-beta]: https://github.com/Bascht74/videopodcast-magic/compare/v2.2.0-beta...v2.3.0-beta
[2.2.0-beta]: https://github.com/Bascht74/videopodcast-magic/compare/v2.1.0-beta...v2.2.0-beta
[2.1.0-beta]: https://github.com/Bascht74/videopodcast-magic/compare/v2.0.0-beta...v2.1.0-beta
[2.0.0-beta]: https://github.com/Bascht74/videopodcast-magic/compare/v1.1.0-beta...v2.0.0-beta
[1.1.0-beta]: https://github.com/Bascht74/videopodcast-magic/compare/v1.0.0-beta...v1.1.0-beta
[1.0.0-beta]: https://github.com/Bascht74/videopodcast-magic/releases/tag/v1.0.0-beta
