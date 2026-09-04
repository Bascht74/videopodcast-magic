# The test suite

238 tests against the program in `../videopodcast_magic/`. Every one of them stands
in the table at the end of this file, with the sentence that says what
holds when it is green.

```bash
bash run.sh              # all of them, several at a time
WORKERS=1 bash run.sh    # one after another, easier to read
bash run.sh voice_turns_found time_offset_found   # only those, named
python3 voice_turns_found_test.py                 # a single one, by hand
bash resolve.sh          # the ones that need a running DaVinci Resolve
```

`resolve.sh` runs what lies under `resolve/`. Those talk to a DaVinci
Resolve really running on this machine, so they are not in the suite and
not on the builder: without Resolve every one of them would be red for a
reason that is not a fault. They work in a project of their own, put the
project that was open back, and delete their own again. Their
counter-proofs live in `resolve/counterproof`, for the same reason: the
register reads the folder above, and a row there would belong to no test.
`run.sh` ends every run by naming them -- how many there are, that they
did not run here, and the command that starts them -- and where git says
something under `resolve/` or in `resolve.sh` has been worked on, the
line says that too. The count comes out of the folder, so a fifth test
is named without anybody editing a number. On the builder the line is
not printed at all.

A test started by hand runs in whatever language the machine is set to,
and on a German Mac that is German -- the program skips the `C` locale
on purpose and asks the system. Its English expectations then meet
German output and it goes red for the wrong reason. `run.sh` exports
`LANG=C LC_ALL=C LANGUAGE=en`, and all three are needed; a test started
on its own has to carry them:

```bash
LANG=C LC_ALL=C LANGUAGE=en python3 voice_turns_found_test.py
```

A test started by hand stays silent: every test that builds a player
sets `VPM_SILENT` itself, so it plays nothing at whoever is working
next to it, and `run.sh` sets the variable for the whole run anyway.
The program reads it with `bool()`, so any value silences the player,
`0` included, and `env -u VPM_SILENT` does not help -- the test would
set it again. Sound comes back with an empty value:
`VPM_SILENT= python3 cut_player_jump_lands_test.py`.

A test counts as green when it returns 0 and prints neither a traceback
nor `FAIL`. A test that finds nothing to work on prints `SKIPPED:` and is
counted apart -- the summary line then reads `green: 50 skipped: 1`, never
green for a test that checked nothing. A green test that left one
section out says so as well, and `run.sh` reports it as "left a piece
out" rather than folding it into the green count.

A test that crashes is given three goes before the run is called red,
and anything red beside the others is run once more alone. Either way
the summary names it as unsteady: green on a second go is not the same
as green. `TRIES=1` turns the retry off, `ALONE=0` the second run.

Needed: `python3`, `ffmpeg`, `ffprobe`, `numpy`, `PySide6` and
`pyspellchecker` (with its German and English word lists -- without it
`text_only_texts_change_test.py` turns red rather than skipping). The window tests run
offscreen (`QT_QPA_PLATFORM=offscreen`), so no display is required.

## Fixtures and temporary material

Every test builds its own material below `TMPDIR`. `run.sh` points that at
one folder per run and removes it at the end -- most tests do not clean up
after themselves, and a whole run is several gigabytes. `KEEP_TEMP=1 bash
run.sh` leaves it in place for looking at.

Six folders are shared and read-only, so `fixtures.sh` builds them once
before the tests fan out -- otherwise `files_hdr_complete_test.py` and
`files_foreign_untouched_test.py` would race for the same files. They
live under one root that carries the user id,
`/tmp/vpm-fixtures-<uid>`, so two users or two builder jobs on one
machine do not delete each other's material; `VPM_FIXTURES` moves the
root, and `fixture_root.py` tells the Python side where it is.

| Folder | Holds |
|---|---|
| `foreign` | everything that is not a camera file: text, an empty file, a truncated MP4, a folder |
| `hdrtest` | one file per HDR case: HDR10, HLG, no static metadata, the wrong curve, SDR |
| `playertest` | a minute of picture and sound, enough for a cut of five shots |
| `interview` | a whole small production: three recordings, three cameras, a project file |
| `mixer` | one file with eight channels, one case on each |
| `twovoices` | two synthetic voices taking turns, for the speaker separation. Spoken on a Mac and written back into `tests/material/twovoices/`, read from there everywhere else -- `say(1)` is macOS's alone |

A finished folder carries a `.built` marker, and the marker may name the
recipe that wrote it: a folder built by an older `fixtures.sh` is then
built again rather than being taken for current. A build broken off half
way has no marker at all and is likewise built again. `bash fixtures.sh
force` rebuilds regardless.

## Environment

| Variable | Effect |
|---|---|
| `VPM_SCRIPT` | which copy of the program is tested, named by its own `__init__.py` (default: the one in the folder above) |
| `VPM_PYTHON` | which interpreter runs the suite (default: the version the program recommends, if it is installed) |
| `VPM_MEDIA` | folder with a project to open (default: the `interview` fixture) |
| `VPM_FIXTURES` | where the six shared folders live (default: `/tmp/vpm-fixtures-<uid>`) |
| `VPM_SHOTS` | where the window screenshots go (default: `tests/shots/`) |
| `WORKERS` | how many tests at once (default: processors + 1, at most 12) |
| `TRIES` | how many goes a crashed test gets before the run is red (default 3) |
| `ALONE` | whether a red test is run once more by itself (default 1) |
| `VPM_ORDER` | `reverse` turns the queue round, shortest first -- for asking what the order is worth, not for running the suite |
| `KEEP_TEMP` | keep the run's temporary folder and its cache |
| `VPM_CACHE` | where the program keeps what it computes between runs. `run.sh` points it at one folder per run and throws it away at the end, so a suite leaves nothing in the cache of whoever started it |
| `VPM_SILENT` | the player makes no sound (`run.sh` sets it, and every player test sets it for itself) |
| `VPM_NO_SPEAKER_SPLIT` | the speaker separation never starts by itself: setting it up fetches hundreds of megabytes and a run costs minutes on the graphics unit |
| `VPM_NO_UPDATE_CHECK` | do not look whether a newer version is out (`run.sh` sets it: a suite has no business on the network, and none swapping the file it is testing) |
| `VPM_INSTALL_TOOLS` | answer the ffmpeg question with yes before it is asked, so a run with nobody in front of it installs it over the package manager instead of stopping |

Five things need a folder holding `videopodcast-magic_Interview_2.json`
and the files it points at: `window_start_runs_test.py`,
`window_idle_bar_hidden_test.py`, `window_stages_named_test.py` and the
two screenshot scripts `preview_shot.py` and `assignment_shot.py`, which
`run.sh` does not collect. `text_no_german_left_test.py` uses the same
folder for one section and leaves that section out without it.
`fixtures.sh` builds a synthetic one, so they run from a fresh checkout.
Point `VPM_MEDIA` at real recordings to run them against those instead;
where neither is there they print `SKIPPED:` and are counted apart.

## The order of the queue

The long tests run first, or a slow one named late in the alphabet
starts last and its whole length is added to the end of the run.
`state/longest` holds how long each test took, and only
`builder_times.sh` writes it, from a green run on the builder. This Mac
has cores to spare and finishes in half a minute while the builder takes
minutes, so its numbers have no business deciding the order. A test the
file does not name goes first: unknown may be slow.

```bash
bash builder_times.sh    # fetch the newest green run on main, rewrite state/longest
```

## The ratchets

Four tests count things that are meant to go to zero and keep the count
in `state/`, one file each. A count may fall, never rise.

| Test | Keeps | Counts |
|---|---|---|
| `source_limits_hold_test.py` | `state/style_state.json` | German in comments and docstrings, narrating comments, lines over 79 characters, long comment blocks and docstrings, docstring heading defects, lazy plurals (`file(s)`), the largest function, functions over 300 lines, exceptions swallowed without a word |
| `source_no_loose_ends_test.py` | `state/consistency_state.json` | project keys nobody reads, and tests in this folder that pass no judgement at all |
| `text_only_texts_change_test.py` | `state/language_state.json` | uncoloured messages, German words in the source, English words left in German texts |
| `text_whole_sentences_test.py` | `state/catalogue_shape_state.json` | sentences glued together out of translated pieces |

The numbers stand in those files and not here, where they would go
stale. Several of them are at zero, and that is what makes them worth
having: a German word or a `(s)` plural that creeps back into the source
turns the suite red the same day. **Do not delete `state/`**: a missing
count is treated as "no baseline yet" and seeded from the current
source, which would quietly disarm the ratchet.

The bigger counters are held on places rather than on plain numbers --
`ratchet.py` says why. A count alone lets one fault be swapped for
another: shorten a long line here, write a new one there, and the number
has not moved.

## The counter-proof register

A check nobody has ever seen fail is not known to check anything. So
every check owes a counter-proof: break the thing it is about in a copy
outside the repository, run the test against that, keep the red line.
`state/counterproof` holds one line per test -- what was broken and the
red line word for word -- and a census row for every test that has not
had one yet.

`source_checks_proved_test.py` is the ratchet over the rest: a new test with no
row turns the suite red at once, and the census may shrink but never
grow. Its closing line says how many have their proof and how many are
still owed, so the figure is read out of the run rather than out of
here.

A row hangs on a fingerprint over the wording of the test's judgements,
not on the file name, so a renamed test keeps its row and a test whose
checks were reworded loses it -- a counter-proof from yesterday says
nothing about a check rewritten today.

## What these tests cannot do

Three of them -- `project_render_queued`, `project_hdr_follows`,
`project_cameras_land` -- build something for DaVinci Resolve and hold a
stand-in project up to it. They check what was handed over: the format,
the codec, the profile, which track each camera landed on. Whether
Resolve then delivers what it was told is not visible from here, and
only Resolve could say. Each of the three says so in its docstring.

The stand-in is the risk in all three. One that is more generous than
the real thing keeps every check over it green while nothing works: a
media pool that invents each track it is asked for, a timeline with no
way to delete one. `development/test_guidelines.md`, section 5, says
what to hold a stand-in to.

## Back to a first run

`first_run.sh` takes off the machine everything the program puts on it:
the environment the separation runs in, the packages it installs by
itself, what it stores between runs, the models in the Hugging Face
store, pip's download store, the auphonic key in the keychain. The next
start is then a first start.

```bash
bash first_run.sh              # say what would go, delete nothing
bash first_run.sh --for-real   # delete it, after one question
```

It is not part of the suite -- `run.sh` picks up `*_test.py` and nothing
else -- and it is not run in passing. It belongs to a change in how the
program installs or caches: then it is run once, a real project is
opened, and the first run is watched putting it all back.

Two things it leaves alone on purpose. `models/` beside the program: the
separation model travels with the program rather than being fetched, so
removing it does not test an install, it breaks the program. And the
project folders, whose results are nobody's to delete but their owner's.

`--without-torch`, `--without-modules` and the other `--without-` names
leave a group standing. That matters for `torch`: the environment is
built with `--system-site-packages`, so a torch already in the
interpreter makes it fetch 58 MB instead of 218 -- but other work on the
same machine may need it.

## Every test, and what green means

The table below is written by `overview.py` out of the tests themselves,
and `text_tests_listed_test.py` holds it against the folder. Change a
test and write the table back:

```bash
python3 overview.py            # into README.md
python3 overview.py --show     # to the screen, changing nothing
```

The name is the one `run.sh` prints and the one a red line carries. The
sentence beside it is the first line of the test's docstring, which says
what holds about the program when the test is green -- so a red run can
be placed without opening the file. The twelve prefixes say where the
fault would sit, not what the material is about;
`development/test_guidelines.md`, section 3, has the reasoning.

<!-- overview begins -- written by overview.py, not by hand -->

238 tests. The name is the one a red line carries, and beside it the
first line of that test's docstring: what holds about the program when
it is green.

### `files_` -- the material: what is read, what is written, what is left

| Test | Green means |
|---|---|
| `files_atom_travels` | Atoms lost by ffmpeg's copy are put back into the new file. |
| `files_block_out_and_back` | Taking one block out of a recording, and putting it back. |
| `files_block_stays_apart` | A block taken out of a recording by hand stays out. |
| `files_blocks_join_exact` | Blocks join only where the file names match letter for letter. |
| `files_by_file_holds` | The dictionary of files finds one file under any of its names. |
| `files_clock_links_blocks` | Blocks that carry a clock in the name instead of a counter. |
| `files_colour_carried` | Colour tags, metadata keys and named audio tracks reach the result. |
| `files_curve_kept_once` | One file leaves one envelope, whatever name it was asked for. |
| `files_cut_without_keys` | A camera is cut to the window even where its key frames cannot be read. |
| `files_data_track_kept` | A camera's data track is carried over only where ffmpeg writes it whole. |
| `files_foreign_untouched` | Copying atoms over onto everything that is not a camera file. |
| `files_hdr_complete` | #65: Does a finished file carry everything that marks it as HDR? |
| `files_intro_proposed` | A jingle is proposed as the intro, not for "ignore this video". |
| `files_joined_by_hand` | Putting files into one recording by hand. |
| `files_left_out_named` | A file left out of a recording is named, with the reason. |
| `files_lengths_summed` | Does the preflight compare recordings instead of blocks? |
| `files_named_as_written` | Curve and camera are named from the file's words, not from a likeness. |
| `files_named_by_folder` | Which folder name is a production, and which one says nothing. |
| `files_old_file_refused` | The format check: an older file is reported, not read. |
| `files_only_window_kept` | A time window shortens the cameras and leaves every frame where it was. |
| `files_order_kept` | Files put together by hand keep the order they were named in. |
| `files_probed_once` | Every file is measured once, not once per question. |
| `files_project_first` | The project is offered before the material is measured; closing stops it. |
| `files_project_offered` | A project file lying with the material is offered, not read behind a back. |
| `files_set_aside_skipped` | Set-aside files: checked yes, compared no, counted no. |
| `files_split_found_again` | Split blocks are found again by the names they carry today. |

### `sound_` -- channels, tracks and loudness

| Test | Green means |
|---|---|
| `sound_all_blocks_count` | The channels are judged over the whole recording, not over one block. |
| `sound_any_count_judged` | One rule for any channel count: is this pair stereo or two tracks? |
| `sound_bleed_reported` | How much of each speaker sits in the other microphone. |
| `sound_both_sides_alike` | The two channel mix: same signal on both sides, and the right loudness. |
| `sound_camera_counts` | A camera counts as a track once the assignment says so. |
| `sound_camera_judged_too` | A camera whose audio is in use is an audio file like any other. |
| `sound_channels_split` | A file with several channels becomes several tracks. |
| `sound_check_reads_once` | The check of a written camera file reads it once, not once per track. |
| `sound_clipping_counted` | Clipping is counted per channel, and only where the format has a stop. |
| `sound_delay_decides` | One pair of microphones, or two of them? |
| `sound_each_gets_a_track` | Without Multitrack: the mix, and the recordings beside it. |
| `sound_hush_reason` | A channel that carries nothing says which rule caught it. |
| `sound_join_order` | Audio blocks are joined in the order they were handed over. |
| `sound_loudest_block` | The facts of a recording come from its loudest block. |
| `sound_mix_hits_target` | Loudness: does the range come along, and does it still normalise? |
| `sound_one_pass_agrees` | Reading the channels: one pass has to say what one pass per channel said. |
| `sound_silent_no_pair` | A silent channel is never one side of a stereo track. |
| `sound_stereo_kept` | Stereo stays stereo: on the axis, in the single track, in the mix. |
| `sound_tracks_written` | Which audio tracks stand in a written camera file, counted and named. |

### `time_` -- the common time axis

| Test | Green means |
|---|---|
| `time_all_ways_agree` | One moment, and every way to it has to land on the same second. |
| `time_axis_keys_agree` | A measured time axis answers to the same name as a remembered one. |
| `time_axis_measured` | The common time axis, measured out of the sound and without a window. |
| `time_bad_point_dropped` | One sample point in the wrong place must not tip the whole line. |
| `time_block_holds_on` | A recording made of blocks is placed as one recording. |
| `time_clock_from_any_file` | A Timecode is counted from the axis, not from the reference's clock. |
| `time_clock_read_at_rate` | What a file's clock says is read at that file's own rate. |
| `time_clock_track_first` | A file's clock is read off its track before the file's own level. |
| `time_drift_taken_out` | A returned track that runs away has to be straightened again. |
| `time_fit_reports` | The offset fit says how close it came and what it left unexplained. |
| `time_guess_refused` | A file nothing can place is refused, not laid down at a guess. |
| `time_length_is_in_to_out` | The window shows its own length, and only content bounds an episode. |
| `time_length_names_change` | The length line names the measured window only where it differs. |
| `time_measured_place_wins` | A camera stands where it was measured; its clock is the last resort. |
| `time_offset_found` | Sound path and a track's own offset are told apart out of the bleed. |
| `time_one_track_aligned` | The simple path: one recording into the video files. |
| `time_over_midnight` | Midnight is one night, not a day apart. |
| `time_point_pulled_back` | A hand-set In or Out point never reaches past what every camera saw. |
| `time_reference_silent` | The camera everything else is measured against reports no measurement. |
| `time_second_try_places` | A steady tone no longer keeps a file off the time axis. |
| `time_sound_stays_put` | Does a time window move the sound against the picture in Multitrack? |
| `time_track_starts_late` | A track that begins after the picture is placed where the file says. |
| `time_tracks_alone` | Multitrack without a picture: the tracks are laid against each other. |
| `time_tracks_sit_together` | Tracks put on the axis sit together, whatever offset they came with. |
| `time_which_way_is_said` | The run says which way put a track on the axis, and how sure it is. |
| `time_window_is_shared` | The window is the stretch EVERY camera saw, not the one any saw. |
| `time_zero_at_in_point` | #66: Where does programme time start on the clock, and what hangs on it? |

### `voice_` -- who speaks, and where

| Test | Green means |
|---|---|
| `voice_answer_kept` | The two proposals that fill a field nobody has answered. |
| `voice_bleed_gone_first` | #80: does the bleed get taken out before the speech detection? |
| `voice_both_splits_stand` | A second separation leaves the first its voices, names and cameras. |
| `voice_both_ways_agree` | The window and the command line separate the same way. |
| `voice_close_mics_mixed` | Microphones that hear each other are mixed and taken apart by voice. |
| `voice_every_word_placed` | The words on the speakers, and the three files that come of it. |
| `voice_failed_read_named` | A reading that fails costs its tracks the cut, and the log says so. |
| `voice_language_arrives` | The language asked for reaches the recognition as a code it takes. |
| `voice_mhm_is_speech` | A short reaction is speech, not a hole in the conversation. |
| `voice_mic_reaches_cut` | Every track is in the cut by its own microphone, or the log names it. |
| `voice_name_is_one_person` | A name that comes twice is one person in the cut, not two. |
| `voice_names_when_sure` | Where the names of the voices could come from, instead of by hand. |
| `voice_note_translated` | Nothing the speech recogniser prints reaches the screen in its words. |
| `voice_questions_rank` | Who is asking the questions, as a proposal and never as a verdict. |
| `voice_raw_times_kept` | Local speaker separation: the arithmetic around the model. |
| `voice_reason_reaches_log` | Why the separation cannot run reaches the log, and not a guess. |
| `voice_source_travels` | Where the speakers of a run come from, and how they reach it. |
| `voice_split_hears_two` | Let the speaker separation really run, on two voices we spoke. |
| `voice_split_names_fault` | A separation that will not run says which fault it hit, not a story. |
| `voice_tracks_read_once` | The tracks of a run are read once, whatever the reading is used for. |
| `voice_turns_found` | Speech is found back where it was put, offset and all. |
| `voice_words_intact` | Speech recognition: the words, their times and their punctuation. |

### `cut_` -- the cut by speaker, and the player over it

| Test | Green means |
|---|---|
| `cut_all_shots_land` | Checks the cut timeline: lengths fit, no gaps, nothing drops out. |
| `cut_both_are_shown` | Two talk at once: does the camera showing both come up? |
| `cut_box_fits_the_picture` | The picture keeps its shape, and the note under it keeps to two lines. |
| `cut_colour_per_camera` | Clip colours: one per angle, and the same one every time. |
| `cut_jingle_over_start` | Intro and outro: where they sit, and how far the content moves. |
| `cut_list_rebuilt` | The cut list is built again unless the window really moved. |
| `cut_no_wide_silences` | Without a wide shot the settings that steer it are silenced in the cut. |
| `cut_note_moves_no_shot` | A name held on the picture moves nothing in the cut. |
| `cut_note_says_who_speaks` | The picture says who speaks and which camera runs, in the shot's colour. |
| `cut_offer_needs_two` | When a camera cut is offered, and what the box over it is called. |
| `cut_one_camera_marks` | One camera for everybody: the cut still marks the speaker changes. |
| `cut_opening_wide_holds` | The opening wide shot must not depend on how finely a source cuts. |
| `cut_own_mic_own_camera` | A speaker with her own microphone is in the cut beside a separation. |
| `cut_own_rate_counted` | Every shot of the cut counts its frames in the rate of its own camera. |
| `cut_player_in_sync` | Does the sound in the cut player belong to the picture on screen? |
| `cut_player_jump_lands` | Does the cut player really jump where it is told to? |
| `cut_player_offset_used` | #63: The player has to take the measured offset, not zero. |
| `cut_player_prepared_used` | Which recording a camera is heard with in the preview. |
| `cut_player_right_file` | #62: The player takes the file that holds the In point and the Out point. |
| `cut_player_speeds_up` | The cut player runs forward faster on every press, and says how fast. |
| `cut_preview_is_the_run` | The preview shows the cut the run will really make. |
| `cut_rebuild_keeps_all` | Rebuilding the cut list keeps every setting the run was given. |
| `cut_right_camera` | Is the cut true: the right camera, and every time rule kept? |
| `cut_rules_hold` | The cut rules: when the camera follows, and what it shows instead. |
| `cut_speech_time_fits` | The speech time the preview reports fits inside the timeline. |
| `cut_two_stay_two` | Two cameras never become one camera in the cut. |
| `cut_voice_on_its_camera` | A multitrack run puts every voice on the camera the assignment names. |
| `cut_wide_colour_apart` | Does the wide shot colour keep far enough from the speaker colours? |
| `cut_wide_not_on_speech` | No wide shot is put on the short answer the speech floor keeps. |

### `project_` -- what DaVinci Resolve is handed

| Test | Green means |
|---|---|
| `project_cameras_land` | Every camera reaches the timeline on picture and sound tracks of its own. |
| `project_each_track_set` | Checks: on reuse the tracks are switched over one at a time. |
| `project_every_offset` | Every camera reaches the handover with its offset -- and only a camera. |
| `project_file_beats_last` | A project opened after another takes its answers from its own file. |
| `project_grades_stay_off` | Remote grades: off by default, and always set -- old projects too. |
| `project_handover_built` | The handover is built from data alone, without a window. |
| `project_hdr_follows` | The render job carries the codec, profile and tags of its range. |
| `project_keeps_answers` | The saved project holds what was answered, and nothing else. |
| `project_output_says_hdr` | The project's output colour space decides HDR, and silence is not no. |
| `project_real_frame` | The frame of the project is one a camera really recorded. |
| `project_render_kept` | A render never writes over the delivery before it. |
| `project_render_queued` | The render job handed to Resolve carries format, codec and settings. |
| `project_rerun_updates` | #60 in a whole run: build twice, update on the second pass. |
| `project_run_comes_back` | Opening a project takes up the handover its own run left behind. |
| `project_same_offset` | Preview and Resolve put a camera at the same offset. |
| `project_settings_return` | What is typed into the window reaches the project file and comes back. |
| `project_tag_reason_fits` | The Tagging line names a reason only where it explains its own tags. |
| `project_top_rate_wins` | The Timeline gets the highest rate in the material, not the longest one's. |
| `project_two_stay_two` | Two cameras whose files share a name stay two cameras. |
| `project_two_timelines_go` | #60: update a project -- the two timelines go, nothing else. |

### `auphonic_` -- the way out to auphonic.com and back

| Test | Green means |
|---|---|
| `auphonic_key_answer_fits` | What comes back is said about the key that went out, not another. |
| `auphonic_key_by_pipe` | The macOS key store is reached without a leak and without a prompt. |
| `auphonic_key_kept` | The Windows way to the key store, walked for real. |
| `auphonic_key_out_of_view` | Nobody else can read the key: not in the process list, not left behind. |
| `auphonic_may_be_skipped` | The entry "work without Auphonic" instead of a tick of its own. |
| `auphonic_mono_not_stereo` | A mono master does not stand in for the stereo one. |
| `auphonic_none_chosen` | Connecting to auphonic.com must not by itself arm a paid run. |
| `auphonic_preset_fits` | Preflight for the preset: does it hold what the run needs? |
| `auphonic_run_delivers` | The two functions that assemble a whole production at auphonic.com. |
| `auphonic_speech_read` | What a production writes about the audio, and in which language. |
| `auphonic_stays_quiet` | The program says nothing to auphonic.com unless somebody asks it to. |

### `window_` -- the interface

| Test | Green means |
|---|---|
| `window_all_come_up` | The interface really builds itself -- in both languages. |
| `window_answers_arrive` | What the window is told is what the calculation gets. |
| `window_axis_asks_again` | A file added while the time axis is measured is measured too. |
| `window_captions_fit` | Does every visible caption fit the field that carries it? |
| `window_cut_colours` | Every shot in the cut band stands at its time in its camera colour. |
| `window_foot_on_one_line` | The buttons in the footer stand on one line, and say why they are off. |
| `window_grey_opens_again` | Every setting greyed out opens again once its reason is gone. |
| `window_grey_says_why` | Why the start button is grey, and where that is said. |
| `window_hears_while_split` | The words are written down while the speakers are being separated. |
| `window_idle_bar_hidden` | The one bar in the footer: does it come, rise, and go again? |
| `window_marks_take_spot` | What Mark In and Mark Out set is where the player stands. |
| `window_menu_greys_along` | The five File entries that switch are as grey as the window. |
| `window_no_full_screen` | Nothing in the window takes the picture full screen any more. |
| `window_notes_break_up` | A note too long for its place breaks into lines, and its box gives. |
| `window_picture_returns` | A refused format does not outlive the attempt it was about. |
| `window_play_follows_tab` | The transport drives the player of the tab showing, or nothing. |
| `window_prework_box_goes` | The box that shows the prework goes away once the prework is over. |
| `window_setup_kept_apart` | What is set up once, and what is decided every time. |
| `window_size_as_run` | The window's summary names the size the run really needs. |
| `window_speaker_cell_fits` | Whatever is written into the Speakers cell can be read there. |
| `window_speakers_as_run` | The window's preview counts the same speakers as the run will. |
| `window_stages_named` | The footer bar during a run: stages, weights, and the end reached. |
| `window_stands_still` | Left alone, the window stops measuring and stops moving a Kind. |
| `window_start_runs` | The start button must build a command line and start a run. |
| `window_view_reaches_tabs` | The View menu reaches every tab that stands, by name and by key. |
| `window_zoom_stays_in` | Zoom on the cut band: in, out, and what a press then means. |

### `table_` -- the assignment table

| Test | Green means |
|---|---|
| `table_audio_asked_for` | #38 Stage 5c: what decides that a camera's sound is material. |
| `table_blocks_judged` | A recording of several blocks must not wait for ever to be judged. |
| `table_camera_proposed` | The suggestion finds the speaker's camera, and never freezes it. |
| `table_names_reach_camera` | A speaker's name reaches the camera row, typed or only suggested. |
| `table_no_place_not_wide` | A file that sits nowhere is not offered as the wide shot. |
| `table_notes_in_one_row` | Do all findings of a multi-part recording land in its row? |
| `table_one_entry_greyed` | The Kind field greys one entry, not the whole field. |
| `table_recording_shown` | The chooser beside "One more speaker in" has to show which file. |
| `table_row_per_channel` | The channel split is visible on the file page, and can be changed. |
| `table_row_per_voice` | A separation stored in the project becomes rows -- once somebody says so. |
| `table_stereo_splits` | A stereo file with two people on it becomes two rows to assign. |
| `table_tick_keeps_camera` | The Multitrack tick neither bars a camera choice nor clears one. |

### `run_` -- a whole run: command line, threads, progress, log

| Test | Green means |
|---|---|
| `run_bar_never_falls` | The bar neither falls back nor stands still. |
| `run_bar_tracks_work` | The one bar: weights, creeping, and never going backwards. |
| `run_choice_kept` | A choice made in one run is found by the next, and by nobody else. |
| `run_command_built` | run_argv() builds the command line and the plan, or says why not. |
| `run_dry_reports_voices` | A dry run hands on the separation it read back instead of nothing. |
| `run_ffmpeg_new_enough` | The ffmpeg the program insists on: new enough, and only that. |
| `run_ffmpeg_not_fetched` | The program fetches no ffmpeg of its own: it finds one, or says how. |
| `run_ffmpeg_offered` | Getting ffmpeg is offered on all three systems, and a test run gets none. |
| `run_findings_reach_both` | Every preflight finding reaches the log and the pane, not just a count. |
| `run_install_is_watched` | Installing ffmpeg shows what it is doing while it does it. |
| `run_log_within_reach` | The log of a run is where whoever started it can get at it. |
| `run_metrics_add_up` | The metrics CSV: does it hold what it should, and are the numbers right? |
| `run_odd_clock_named` | A clock that was never set is found, and blocks group as recordings. |
| `run_only_newer_offered` | Keeping itself up to date must not surprise anybody or guess. |
| `run_outside_seen` | Every call to another program is in the log, and none in the output. |
| `run_prework_listed` | Header line, prework, window suggestion and axis reuse all hold. |
| `run_promise_is_written` | What the run promises as audio tracks is what it writes. |
| `run_simple_path_agrees` | One simple-path run end to end: every promise kept, and it agrees. |
| `run_space_has_margin` | Room for the run is judged with a margin, and on both disks at once. |
| `run_stays_local` | A whole multitrack run that finishes on this machine alone. |
| `run_switch_changes_it` | A switch that is taken changes the result, not only the parser. |
| `run_switch_has_effect` | A switch that is taken and does nothing is worse than no switch. |
| `run_threads_keep_order` | Doing several things at once: in order, complete, and honest about errors. |
| `run_three_ways_agree` | Window, project file and command line come to the same cut. |
| `run_which_script` | The log names the copy of the script that is running. |

### `text_` -- the texts: catalogue, manual, changelog

| Test | Green means |
|---|---|
| `text_german_arrives` | The German texts are a file of their own, and every way in brings them. |
| `text_index_targets_exist` | The index has to point at sections that are really there. |
| `text_lang_settled_first` | Nothing this program says is made before the language is settled. |
| `text_lists_match` | Where the manual copies a list out of the program, it has to match. |
| `text_no_german_left` | Hunt down the last German word, and check the catalogue itself. |
| `text_only_texts_change` | The language machinery: catalogue, detection, switch, log colours. |
| `text_release_ready` | What a release has to have, checked instead of remembered. |
| `text_tests_listed` | README.md lists every test with the sentence that test stands for. |
| `text_whole_sentences` | No sentence may be glued together out of translated pieces. |

### `source_` -- the source itself, held by ratchets

| Test | Green means |
|---|---|
| `source_checks_proved` | Which checks have been seen red, and which have not. |
| `source_imported_is_whole` | Importing the program gives the whole of it, whatever argv said. |
| `source_limits_hold` | Style check for comments and docstrings. |
| `source_no_loose_ends` | Looks for half-finished renames and other loose ends. |
| `source_no_real_names` | Nothing off a real production and nobody's name is in a shipped file. |
| `source_numpy_comes_last` | The program loads without numpy, so --help and --version stay cheap. |
| `source_reds_carry_value` | A check that falls says what came out, not only that it fell. |
| `source_resolve_door_shut` | A test that calls at a door to Resolve has nailed it shut first. |
| `source_resolve_recalled` | The reminder about the Resolve tests reaches a person, not the builder. |
| `source_sections_named` | The program divides into named sections, and the ground uses none above. |
| `source_skills_resolve` | Every file, test and skill a skill names by name is really there. |
| `source_test_names_swept` | A name a test gives Resolve is swept, or excepted by name. |

<!-- overview ends -->
