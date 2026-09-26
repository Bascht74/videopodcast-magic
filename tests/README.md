# The test suite

361 tests against the program in `../videopodcast_magic/`. Every one of them stands
in the table at the end of this file, with the sentence that says what
holds when it is green.

```bash
bash run.sh              # all of them, several at a time
WORKERS=1 bash run.sh    # one after another, easier to read
bash run.sh voice_turns_found time_offset_found   # only those, named
python3 speakers/voice_turns_found_test.py        # a single one, by hand
bash resolve.sh          # the ones that need a running DaVinci Resolve
```

`resolve.sh` runs what lies under `resolve/live/`. Those talk to a DaVinci
Resolve really running on this machine, so they are not in the suite and
not on the builder: without Resolve every one of them would be red for a
reason that is not a fault. They work in a project of their own, put the
project that was open back, and delete their own again. Their
counter-proofs live in `resolve/live/counterproof`, for the same reason:
the register reads the suite's folders, and a row there would belong to
no test. The tests in `resolve/` itself are the suite's: they check the
piece `resolve/` and need no Resolve running.
`run.sh` ends every run by naming them -- how many there are, that they
did not run here, and the command that starts them -- and where git says
something under `resolve/live/` or in `resolve.sh` has been worked on, the
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
LANG=C LC_ALL=C LANGUAGE=en python3 speakers/voice_turns_found_test.py
```

A test started by hand stays silent: every test that builds a player
sets `VPM_SILENT` itself, so it plays nothing at whoever is working
next to it, and `run.sh` sets the variable for the whole run anyway.
The program reads it with `bool()`, so any value silences the player,
`0` included, and `env -u VPM_SILENT` does not help -- the test would
set it again. Sound comes back with an empty value:
`VPM_SILENT= python3 player/cut_player_jump_lands_test.py`.

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
| `mixedcase` | a production like the owner's case: three cameras without a speaker at 25 and 29.97 fps, one in 10 bit, a recording in two blocks |
| `mixer` | one file with eight channels, one case on each |
| `twovoices` | two synthetic voices taking turns, for the speaker separation. Spoken on a Mac and checked in under `tests/samples/twovoices/`, read from there everywhere else -- `say(1)` is macOS's alone |

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
| `VPM_FIXTURES` | where the seven shared folders live (default: `/tmp/vpm-fixtures-<uid>`) |
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

361 tests. The name is the one a red line carries, and beside it the
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
| `files_colour_fair` | Cameras are compared in colour like for like: one scale, each file once. |
| `files_curve_kept_once` | One file leaves one envelope, whatever name it was asked for. |
| `files_cut_without_keys` | A camera is cut to the window even where its key frames cannot be read. |
| `files_data_track_kept` | A camera's data track is carried over only where ffmpeg writes it whole. |
| `files_foreign_untouched` | Copying atoms over onto everything that is not a camera file. |
| `files_hdr_complete` | #65: Does a finished file carry everything that marks it as HDR? |
| `files_intro_proposed` | A jingle is proposed as the intro, not for "ignore this video". |
| `files_joined_by_hand` | Putting files into one recording by hand. |
| `files_left_out_named` | A file left out of a recording is named, with the reason. |
| `files_lengths_summed` | Does the preflight compare recordings instead of blocks? |
| `files_line_counts_misfit` | The line under the file list counts the rows the time axis marked. |
| `files_mute_clip_intro` | A mute clip is proposed as intro by a length that judges it alone. |
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
| `files_sync_one_recording` | Sync only takes one audio recording, and the second is refused. |
| `files_twin_cameras_named` | Two copies of one camera file are named once, as a note, never stopped. |

### `sound_` -- channels, tracks and loudness

| Test | Green means |
|---|---|
| `sound_all_blocks_count` | The channels are judged over the whole recording, not over one block. |
| `sound_any_count_judged` | One rule for any channel count: is this pair stereo or two tracks? |
| `sound_bleed_reported` | How much of each speaker sits in the other microphone. |
| `sound_block_gap_said` | A hole or an overlap between timecoded blocks is said when they are joined. |
| `sound_both_sides_alike` | The two channel mix: same signal on both sides, and the right loudness. |
| `sound_camera_counts` | A camera counts as a track once the assignment says so. |
| `sound_camera_judged_too` | A camera whose audio is in use is an audio file like any other. |
| `sound_camera_own_used` | A camera's own sound, taken for want of a recording, is its track. |
| `sound_channels_split` | A file with several channels becomes several tracks. |
| `sound_check_reads_once` | The check of a written camera file reads it once, not once per track. |
| `sound_clipping_counted` | Clipping is counted per channel, and only where the format has a stop. |
| `sound_delay_decides` | One pair of microphones, or two of them? |
| `sound_each_gets_a_track` | Without Multitrack: the mix, and the recordings beside it. |
| `sound_hush_reason` | A channel that carries nothing says which rule caught it. |
| `sound_join_any_rate` | Timecoded blocks in a row are joined whole at 44.1 and 96 kHz too. |
| `sound_join_order` | Audio blocks are joined in the order they were handed over. |
| `sound_loudest_block` | The facts of a recording come from its loudest block. |
| `sound_mix_hits_target` | Loudness: does the range come along, and does it still normalise? |
| `sound_mix_says_the_name` | While mixing, a track is named by its speaker, and only the mix as the mix. |
| `sound_one_pass_agrees` | Reading the channels: one pass has to say what one pass per channel said. |
| `sound_peaks_limited` | The limiter holds every peak at the ceiling and backs off where it must. |
| `sound_silent_no_pair` | A silent channel is never one side of a stereo track. |
| `sound_speakers_matched` | Without auphonic.com the speaker tracks are brought to one level first. |
| `sound_stereo_kept` | Stereo stays stereo: on the axis, in the single track, in the mix. |
| `sound_tracks_written` | Which audio tracks stand in a written camera file, counted and named. |

### `time_` -- the common time axis

| Test | Green means |
|---|---|
| `time_all_ways_agree` | One moment, and every way to it has to land on the same second. |
| `time_axis_keys_agree` | A measured time axis answers to the same name as a remembered one. |
| `time_axis_measured` | The common time axis, measured out of the sound and without a window. |
| `time_bad_point_dropped` | One sample point in the wrong place must not tip the whole line. |
| `time_bext_at_own_rate` | A bext stamp's samples are counted at the WAV's own sample rate. |
| `time_block_holds_on` | A recording made of blocks is placed as one recording. |
| `time_clock_beats_guess` | A camera the sound cannot place and its clock can stands at its clock. |
| `time_clock_from_any_file` | A Timecode is counted from the axis, not from the reference's clock. |
| `time_clock_read_at_rate` | What a file's clock says is read at that file's own rate. |
| `time_clock_track_first` | A file's clock is read off its track before the file's own level. |
| `time_drift_taken_out` | A returned track that runs away has to be straightened again. |
| `time_drop_label_kept` | A timecode written back stays on the clock it was read from. |
| `time_fit_reports` | The offset fit says how close it came and what it left unexplained. |
| `time_guess_refused` | A file nothing can place is refused, not laid down at a guess. |
| `time_length_is_in_to_out` | The window shows its own length, and only content bounds an episode. |
| `time_length_names_change` | The length line names the measured window only where it differs. |
| `time_measured_place_wins` | A camera stands where it was measured; its clock is the last resort. |
| `time_offset_found` | Sound path and a track's own offset are told apart out of the bleed. |
| `time_one_track_aligned` | The simple path: one recording into the video files. |
| `time_over_midnight` | Midnight is one night, not a day apart. |
| `time_phase_only_mixed` | The phase way places a recording only where its sound was said mixed. |
| `time_point_pulled_back` | A hand-set In or Out point never reaches past what every camera saw. |
| `time_preview_fit_as_run` | The preview places a camera its fit alone places, where the run does. |
| `time_reference_silent` | The camera everything else is measured against reports no measurement. |
| `time_scatter_not_placed` | A recording whose sample points scatter is not placed by them. |
| `time_second_try_places` | A steady tone no longer keeps a file off the time axis. |
| `time_short_cam_as_run` | The preview judges a short camera as the run does, stranger or not. |
| `time_short_cam_found` | A short camera is found anywhere in a long one, and a stranger is not. |
| `time_sound_stays_put` | Does a time window move the sound against the picture in Multitrack? |
| `time_thin_block_refused` | A recording block too thin to place is refused, never laid out wrong. |
| `time_track_starts_late` | A track that begins after the picture is placed where the file says. |
| `time_tracks_alone` | Multitrack without a picture: the tracks are laid against each other. |
| `time_tracks_sit_together` | Tracks put on the axis sit together, whatever offset they came with. |
| `time_unheard_file_named` | A file the axis cannot hear is named as not fitting, never left out. |
| `time_weak_as_run` | The preview lays a file its sound hardly places where the run lays it. |
| `time_weak_at_its_clock` | A camera the sound did not place stands at its clock, not at what failed. |
| `time_which_way_is_said` | The run says which way put a track on the axis, and how sure it is. |
| `time_window_is_shared` | The window is the stretch EVERY camera saw, not the one any saw. |
| `time_zero_at_in_point` | #66: Where does programme time start on the clock, and what hangs on it? |

### `voice_` -- who speaks, and where

| Test | Green means |
|---|---|
| `voice_amounts_grouped` | The speech recognition says its amounts the way the language does. |
| `voice_answer_kept` | The two proposals that fill a field nobody has answered. |
| `voice_bleed_gone_first` | #80: does the bleed get taken out before the speech detection? |
| `voice_both_splits_stand` | A second separation leaves the first its voices, names and cameras. |
| `voice_both_ways_agree` | The window and the command line separate the same way. |
| `voice_close_mics_mixed` | Microphones that hear each other are mixed and taken apart by voice. |
| `voice_counts_grouped` | The separation counts voices as the language does, project files not. |
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
| `voice_split_mends_itself` | A separation that cannot run mends itself once, or says the way back. |
| `voice_split_names_fault` | A separation that will not run says which fault it hit, not a story. |
| `voice_tracks_read_once` | The tracks of a run are read once, whatever the reading is used for. |
| `voice_turns_found` | Speech is found back where it was put, offset and all. |
| `voice_words_intact` | Speech recognition: the words, their times and their punctuation. |

### `cut_` -- the cut by speaker, and the player over it

| Test | Green means |
|---|---|
| `cut_all_shots_land` | Checks the cut timeline: lengths fit, no gaps, nothing drops out. |
| `cut_amounts_grouped` | The cut's report writes amounts as the language does, names not. |
| `cut_answer_brought_early` | The reaction cut lands where the picture changes, and is counted there. |
| `cut_both_are_shown` | Two talk at once: does the camera showing both come up? |
| `cut_box_fits_the_picture` | The picture keeps its shape, and the note under it keeps to two lines. |
| `cut_colour_per_camera` | Clip colours: one per angle, and the same one every time. |
| `cut_edl_says_drop_frame` | The EDL head says which clock the Timeline runs on, and so do its times. |
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
| `cut_rebuild_keeps_all` | Rebuilding the cut list keeps every setting the project file holds. |
| `cut_right_camera` | Is the cut true: the right camera, and every time rule kept? |
| `cut_rules_hold` | The cut rules: when the camera follows, and what it shows instead. |
| `cut_short_edges_kept` | A too long wide edge is shortened, to a third or the latest setting. |
| `cut_speech_time_fits` | The speech time the preview reports fits inside the timeline. |
| `cut_together_read_order` | Speakers heard in one shot are named in the order a person reads. |
| `cut_two_stay_two` | Two cameras never become one camera in the cut. |
| `cut_voice_on_its_camera` | A multitrack run puts every voice on the camera the assignment names. |
| `cut_wide_colour_apart` | Does the wide shot colour keep far enough from the speaker colours? |
| `cut_wide_not_on_speech` | No wide shot is put on the short answer the speech floor keeps. |
| `cut_window_cut_as_whole` | A window set by In and Out is cut as though it were the whole recording. |

### `project_` -- what DaVinci Resolve is handed

| Test | Green means |
|---|---|
| `project_amounts_grouped` | Resolve's report writes amounts as the language does, addresses not. |
| `project_audio_counted` | A camera's audio tracks are counted in its file, timecode not among them. |
| `project_cameras_land` | Every camera reaches the timeline on picture and sound tracks of its own. |
| `project_close_forgets` | Closing a project forgets the handovers remembered for its cameras. |
| `project_each_track_set` | Checks: on reuse the tracks are switched over one at a time. |
| `project_errors_reach_run` | A --resolve run whose Resolve build refused a track ends in 1, not 0. |
| `project_every_offset` | Every camera reaches the handover with its offset -- and only a camera. |
| `project_file_beats_last` | A project opened after another takes its answers from its own file. |
| `project_grades_stay_off` | Remote grades: off by default, and always set -- old projects too. |
| `project_handover_built` | The handover is built from data alone, without a window. |
| `project_hdr_follows` | The render job carries the codec, profile and tags of its range. |
| `project_keeps_answers` | The saved project holds what was answered, and nothing else. |
| `project_leaves_others` | Opening, starting or renaming a project leaves each project file its own. |
| `project_markers_placed` | Speaker markers land on the frame of each turn, one per frame. |
| `project_mix_by_name` | The mix is found by its own name, not by a word inside another one. |
| `project_mixed_run_lands` | A run on mixed rates hands Resolve what its material says, and it builds. |
| `project_output_says_hdr` | The project's output colour space decides HDR, and silence is not no. |
| `project_real_frame` | The frame of the project is one a camera really recorded. |
| `project_refusal_heeded` | What Resolve refuses is named, said again at the end, and the rest built. |
| `project_render_kept` | A render never writes over the delivery before it. |
| `project_render_queued` | The render job handed to Resolve carries format, codec and settings. |
| `project_rerun_updates` | #60 in a whole run: build twice, update on the second pass. |
| `project_run_comes_back` | Opening a project takes up the handover its own run left behind. |
| `project_same_offset` | Preview and Resolve put a camera at the same offset. |
| `project_settings_return` | What is typed into the window reaches the project file and comes back. |
| `project_sync_multicam` | A sync-only handover builds the multicam timeline alone, and says so. |
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
| `auphonic_preset_checked` | A preset is found by name or id, one of the wrong kind stops the upload. |
| `auphonic_preset_fits` | Preflight for the preset: does it hold what the run needs? |
| `auphonic_run_delivers` | The two functions that assemble a whole production at auphonic.com. |
| `auphonic_speech_read` | What a production writes about the audio, and in which language. |
| `auphonic_stays_quiet` | The program says nothing to auphonic.com unless somebody asks it to. |
| `auphonic_unsaved_said` | A key the store refuses takes its tick back and says so in the window. |

### `window_` -- the interface

| Test | Green means |
|---|---|
| `window_all_come_up` | The interface really builds itself -- in both languages. |
| `window_amounts_grouped` | The window says its amounts the way the language does. |
| `window_answers_arrive` | What the window is told is what the calculation gets. |
| `window_axis_asks_again` | A file added while the time axis is measured is measured too. |
| `window_blocks_placed` | The preview plays a recording in the block that holds the moment. |
| `window_captions_fit` | Does every visible caption fit the field that carries it? |
| `window_captions_langs1` | Does every visible caption fit its field, first slice of languages? |
| `window_captions_langs2` | Does every visible caption fit its field, second slice of languages? |
| `window_captions_langs3` | Does every visible caption fit its field, third slice of languages? |
| `window_captions_langs4` | Does every visible caption fit its field, fourth slice of languages? |
| `window_choices_refit` | The camera cut's drop-downs hold their longest entry in any font. |
| `window_clock_sound_said` | Until the sound is measured in, the line under the picture says so. |
| `window_cut_colours` | Every shot in the cut band stands at its time in its camera colour. |
| `window_dark_follows` | A desktop switched to dark leaves no light ground standing in the window. |
| `window_exit_keeps_all` | On Windows the window's end skips the teardown and keeps what it owes. |
| `window_foot_on_one_line` | The buttons in the footer stand on one line, and say why they are off. |
| `window_grey_opens_again` | Every setting greyed out opens again once its reason is gone. |
| `window_grey_says_why` | Why the start button is grey, and where that is said. |
| `window_handover_follows` | The Resolve button follows the handover over the cameras in the list. |
| `window_handover_found` | The Resolve button finds a handover where a run over the list put it. |
| `window_hears_while_split` | The words are written down while the speakers are being separated. |
| `window_idle_bar_hidden` | The one bar in the footer: does it come, rise, and go again? |
| `window_key_off_line` | The key stands on no command line: a window run's, a restart's, a typed one. |
| `window_marks_come_back` | A file that fits nothing is still marked after the project is reopened. |
| `window_marks_take_spot` | What Mark In and Mark Out set is where the player stands. |
| `window_menu_greys_along` | The five File entries that switch are as grey as the window. |
| `window_no_full_screen` | Nothing in the window takes the picture full screen any more. |
| `window_not_started_said` | A camera switched to before it began says so, and the moment is kept. |
| `window_note_names_kind` | A file with no place is told what became of it, not only what is wrong. |
| `window_note_names_way` | A weak file's note names the way that placed it, not another one. |
| `window_note_reason_true` | The note beside a file with no place gives the reason that is true. |
| `window_notes_break_up` | A note too long for its place breaks into lines, and its box gives. |
| `window_offers_restart` | The window offers to start again when another language is chosen. |
| `window_overwrite_asked` | A camera file already written is asked about before a run starts. |
| `window_pair_said_apart` | The window names the second of a pair '(2)' in its intro sentences. |
| `window_picture_returns` | A refused format does not outlive the attempt it was about. |
| `window_play_follows_tab` | The transport drives the player of the tab showing, or nothing. |
| `window_point_named` | A jump no file can make names the point in the window's language. |
| `window_prework_box_goes` | The box that shows the prework goes away once the prework is over. |
| `window_project_type_set` | The project type is chosen once, and the later tabs take its shape. |
| `window_reads_as_chosen` | The window is laid out the way the chosen language reads. |
| `window_restart_carries` | A restart carries the work over, or says plainly that it will not. |
| `window_run_handover_kept` | A run's handover that left a camera out comes back with the camera. |
| `window_setup_kept_apart` | What is set up once, and what is decided every time. |
| `window_sheets_fit` | The window fits its screen and its first three sheets fit the window. |
| `window_size_as_run` | The window's summary names the size the run really needs. |
| `window_sound_fault_named` | A refused sound track costs neither the picture nor the truth. |
| `window_sound_sync_fixed` | The In the sound field keeps one answer, and Sync only fixes it mixed. |
| `window_speaker_cell_fits` | Whatever is written into the Speakers cell can be read there. |
| `window_speaker_langs1` | Whatever is written into the Speakers cell can be read, first slice. |
| `window_speaker_langs2` | Whatever is written into the Speakers cell can be read, second slice. |
| `window_speaker_langs3` | Whatever is written into the Speakers cell can be read, third slice. |
| `window_speaker_langs4` | Whatever is written into the Speakers cell can be read, fourth slice. |
| `window_speakers_as_run` | The window's preview counts the same speakers as the run will. |
| `window_stages_named` | The footer bar during a run: stages, weights, and the end reached. |
| `window_stands_still` | Left alone, the window stops measuring and stops moving a Kind. |
| `window_start_runs` | The start button must build a command line and start a run. |
| `window_symbol_from_file` | The window's symbol is the picture in the file, and nowhere else. |
| `window_tc_point_named` | A point outside a timecoded camera is named, never jumped past. |
| `window_title_follows` | The title bar names the open project's file after a rename too. |
| `window_tracks_seen_anew` | The window looks for finished tracks again after a run and a reset. |
| `window_view_reaches_tabs` | The View menu reaches every tab that stands, by name and by key. |
| `window_voice_audio_heard` | A camera hears its voice; the wide shot, the one recording of every voice. |
| `window_zoom_stays_in` | Zoom on the cut band: in, out, and what a press then means. |

### `table_` -- the assignment table

| Test | Green means |
|---|---|
| `table_audio_asked_for` | #38 Stage 5c: what decides that a camera's sound is material. |
| `table_back_to_one_name` | Going back from several speakers to one name leaves a fresh layout. |
| `table_blocks_judged` | A recording of several blocks must not wait for ever to be judged. |
| `table_camera_proposed` | The suggestion finds the speaker's camera, and never freezes it. |
| `table_lock_says_why` | The sheet's reasons stand in grey inside the field they are about. |
| `table_names_one_order` | Two speakers on one camera stand in one order in its file and track. |
| `table_names_reach_camera` | A speaker's name reaches the camera row, typed or only suggested. |
| `table_no_place_not_wide` | A file that sits nowhere is not offered as the wide shot. |
| `table_notes_in_one_row` | Do all findings of a multi-part recording land in its row? |
| `table_one_entry_greyed` | The Kind field greys one entry, not the whole field. |
| `table_pair_named_alike` | Two cameras of one file name are named apart as the command line does. |
| `table_pair_seats_apart` | Two cameras of one file name each take their own speakers. |
| `table_recording_shown` | The chooser beside "One more speaker in" has to show which file. |
| `table_row_per_channel` | The channel split is visible on the file page, and can be changed. |
| `table_row_per_voice` | A separation stored in the project becomes rows -- once somebody says so. |
| `table_stereo_splits` | A stereo file with two people on it becomes two rows to assign. |
| `table_sync_keeps_stem` | Under Sync only every camera is offered its own file name. |
| `table_sync_none_derived` | Under Sync only no camera is worked out to be the wide shot. |
| `table_sync_stem_shown` | Under Sync only the camera table offers a camera its own file stem. |
| `table_tick_keeps_camera` | The Multitrack tick neither bars a camera choice nor clears one. |
| `table_typed_name_stays` | A name somebody typed stays as typed, even shaped like an offer. |

### `run_` -- a whole run: command line, threads, progress, log

| Test | Green means |
|---|---|
| `run_bar_never_falls` | The bar neither falls back nor stands still. |
| `run_bar_tracks_work` | The one bar: weights, creeping, never going backwards, and its line. |
| `run_choice_kept` | A choice made in one run is found by the next, and by nobody else. |
| `run_clock_place_travels` | Where its clock places a camera, its own sound and handover follow. |
| `run_command_built` | run_argv() builds the command line and the plan, or says why not. |
| `run_done_tracks_used` | Tracks already back from Auphonic go into the run, or the run says why not. |
| `run_dry_leaves_out` | A dry run leaves the output folder exactly as it found it. |
| `run_dry_reports_voices` | A dry run hands on the separation it read back instead of nothing. |
| `run_dry_run_not_stopped` | A dry run short of disk space is told so and goes on; a real run stops. |
| `run_ffmpeg_new_enough` | The ffmpeg the program insists on: new enough, and only that. |
| `run_ffmpeg_not_fetched` | The program fetches no ffmpeg of its own: it finds one, or says how. |
| `run_ffmpeg_offered` | Getting ffmpeg is offered on all three systems, and a test run gets none. |
| `run_findings_reach_both` | Every preflight finding reaches the log and the pane, not just a count. |
| `run_install_is_watched` | Installing ffmpeg shows what it is doing while it does it. |
| `run_log_within_reach` | The log of a run is where whoever started it can get at it. |
| `run_metrics_add_up` | The metrics CSV: does it hold what it should, and are the numbers right? |
| `run_mute_camera_placed` | A camera with no sound but a timecode is placed by it and handed over. |
| `run_names_as_window` | A run names the production and each camera as the window does. |
| `run_new_name_checked` | A run refuses a --new-name it cannot follow as given, and says why. |
| `run_no_drift_noughts` | A drift nobody measured says it was not measured, never noughts. |
| `run_no_upload_no_hint` | The run promises to save an upload only where it uploads. |
| `run_odd_clock_named` | A clock that was never set is found, and blocks group as recordings. |
| `run_one_shots_return_0` | A one-shot job that did its work returns 0 and says so last. |
| `run_only_newer_offered` | Keeping itself up to date must not surprise anybody or guess. |
| `run_outside_seen` | Every call to another program is in the log, and none in the output. |
| `run_overwrite_is_said` | A run that replaces a file says so, and marks one it did not make. |
| `run_own_sound_with_cam` | A camera's own sound stands where its camera stands, however placed. |
| `run_prework_listed` | Header line, prework, window suggestion and axis reuse all hold. |
| `run_project_type_reaches` | The project type reaches the run and says what sync leaves out. |
| `run_promise_is_written` | What the run promises as audio tracks is what it writes. |
| `run_rate_way_said_right` | A camera off its nominal rate is said to be off the way it really is. |
| `run_shortcut_laid_once` | One shortcut is laid on the first start, and never a second time. |
| `run_simple_path_agrees` | One simple-path run end to end: every promise kept, and it agrees. |
| `run_space_has_margin` | Room for the run is judged with a margin, and on both disks at once. |
| `run_starter_arch_fits` | The start asks for the architecture the installed packages fit. |
| `run_stays_local` | A whole multitrack run that finishes on this machine alone. |
| `run_stop_names_why` | A run main() stops returns 1, its last line naming what failed and why. |
| `run_switch_changes_it` | A switch that is taken changes the result, not only the parser. |
| `run_switch_has_effect` | A switch that is taken and does nothing is worse than no switch. |
| `run_sync_only_no_cut` | A Sync only run leaves no cut, no speaker and no transcript behind. |
| `run_threads_keep_order` | Doing several things at once: in order, complete, and honest about errors. |
| `run_three_ways_agree` | Window, project file and command line come to the same cut. |
| `run_update_says_it_landed` | An update that went through says so, and offers the restart. |
| `run_way_back_offered` | Going back to an earlier version is offered, and never into a dead end. |
| `run_which_script` | The log names the copy of the script that is running. |

### `text_` -- the texts: catalogue, manual, changelog

| Test | Green means |
|---|---|
| `text_german_arrives` | The German texts are a file of their own, and every way in brings them. |
| `text_index_targets_exist` | The index has to point at sections that are really there. |
| `text_lang_settled_first` | Nothing this program says is made before the language is settled. |
| `text_languages_covered` | No language answers fewer of the program's texts than it did before. |
| `text_lists_match` | Where the manual copies a list out of the program, it has to match. |
| `text_no_german_left` | Hunt down the last German word, and check the catalogue itself. |
| `text_numbers_fit_reader` | A number takes the language's form for a person, never for a machine. |
| `text_only_texts_change` | The language machinery: catalogue, detection, switch, log colours. |
| `text_release_ready` | What a release has to have, checked instead of remembered. |
| `text_shown_catalogued` | Every word the window and the printed Auphonic lists show went through T(). |
| `text_skills_listed` | Every copy of the skill table says what the skills themselves say. |
| `text_tests_listed` | README.md lists every test with the sentence that test stands for. |
| `text_units_translated` | A file's details say their units and headings in the reader's language. |
| `text_whole_sentences` | No sentence may be glued together out of translated pieces. |

### `source_` -- the source itself, held by ratchets

| Test | Green means |
|---|---|
| `source_checks_proved` | Which checks have been seen red, and which have not. |
| `source_floor_needs_main` | A ratchet writes no floor from a tree that is behind origin/main. |
| `source_imported_is_whole` | Importing the program gives the whole of it, whatever argv said. |
| `source_limits_hold` | Style check for comments and docstrings. |
| `source_material_stays` | A run of fixtures.sh leaves the checked-in material as it found it. |
| `source_names_stay_fresh` | A name the program writes on itself is held nowhere as a stale copy. |
| `source_needs_lists_agree` | requirements.txt and pyproject.toml name the same packages. |
| `source_no_loose_ends` | Looks for half-finished renames and other loose ends. |
| `source_no_real_names` | Nothing off a real production and nobody's name is in a shipped file. |
| `source_no_stale_places` | No docstring sends a reader to a place its own piece does not hold. |
| `source_numpy_comes_last` | The program loads without numpy, so --help and --version stay cheap. |
| `source_piece_list_holds` | Every folder the program reads out of is on pip's list, and no other. |
| `source_platform_declared` | Every test says whether its verdict can differ between systems. |
| `source_reds_carry_value` | A check that falls says what came out, not only that it fell. |
| `source_resolve_door_shut` | A test that calls at a door to Resolve has nailed it shut first. |
| `source_resolve_recalled` | The reminder about the Resolve tests reaches a person, not the builder. |
| `source_sections_named` | The program divides into named sections, and the ground uses none above. |
| `source_skills_resolve` | Every file, test and skill a skill names by name is really there. |
| `source_test_names_swept` | A name a test gives Resolve is swept, or excepted by name. |

### By folder -- the piece each test checks

A test lies in the folder named after the piece of the
program under `videopodcast_magic/` whose logic it checks;
`bash run.sh <name>` finds it there by its name alone.
`source/` is no piece: it holds the tests that read
the source, the texts and the documents as a whole.

| Folder | Tests |
|---|---|
| `auphonic/` | `auphonic_key_answer_fits`, `auphonic_key_out_of_view`, `auphonic_may_be_skipped`, `auphonic_mono_not_stereo`, `auphonic_none_chosen`, `auphonic_preset_checked`, `auphonic_run_delivers`, `auphonic_stays_quiet`, `auphonic_unsaved_said`, `project_each_track_set` |
| `bearings/` | `files_colour_fair`, `files_intro_proposed`, `files_mute_clip_intro`, `files_named_by_folder`, `run_prework_listed`, `sound_camera_counts`, `table_camera_proposed`, `time_axis_keys_agree`, `time_axis_measured`, `time_block_holds_on`, `time_clock_beats_guess`, `time_fit_reports`, `time_offset_found`, `time_preview_fit_as_run`, `time_short_cam_as_run`, `time_tracks_sit_together`, `time_unheard_file_named`, `time_weak_as_run`, `time_weak_at_its_clock`, `window_axis_asks_again`, `window_marks_come_back` |
| `colour/` | `files_hdr_complete`, `files_named_as_written` |
| `cut/` | `cut_answer_brought_early`, `cut_both_are_shown`, `cut_edl_says_drop_frame`, `cut_list_rebuilt`, `cut_no_wide_silences`, `cut_one_camera_marks`, `cut_opening_wide_holds`, `cut_preview_is_the_run`, `cut_rebuild_keeps_all`, `cut_right_camera`, `cut_rules_hold`, `cut_short_edges_kept`, `cut_speech_time_fits`, `cut_together_read_order`, `cut_voice_on_its_camera`, `cut_wide_not_on_speech`, `cut_window_cut_as_whole`, `project_errors_reach_run`, `project_every_offset`, `project_handover_built`, `project_real_frame`, `run_metrics_add_up`, `table_names_one_order`, `table_names_reach_camera`, `table_no_place_not_wide`, `table_sync_keeps_stem`, `table_sync_none_derived`, `time_measured_place_wins`, `time_zero_at_in_point`, `window_grey_opens_again` |
| `desktop/` | `run_shortcut_laid_once`, `run_starter_arch_fits` |
| `filelist/` | `files_block_out_and_back` |
| `filing/` | `files_by_file_holds` |
| `fittings/` | `table_recording_shown`, `window_choices_refit`, `window_foot_on_one_line`, `window_speaker_cell_fits`, `window_speaker_langs1`, `window_speaker_langs2`, `window_speaker_langs3`, `window_speaker_langs4` |
| `hearing/` | `files_curve_kept_once`, `sound_block_gap_said`, `sound_check_reads_once`, `sound_each_gets_a_track`, `sound_join_any_rate`, `sound_join_order`, `time_bad_point_dropped`, `time_guess_refused`, `time_phase_only_mixed`, `time_scatter_not_placed`, `time_second_try_places`, `time_short_cam_found`, `time_thin_block_refused`, `time_track_starts_late`, `time_which_way_is_said` |
| `herald/` | `run_bar_never_falls`, `run_bar_tracks_work`, `run_which_script`, `window_idle_bar_hidden`, `window_stages_named` |
| `language/` | `text_german_arrives`, `text_lang_settled_first`, `text_languages_covered`, `text_no_german_left`, `text_numbers_fit_reader`, `text_only_texts_change`, `text_shown_catalogued`, `text_whole_sentences`, `window_reads_as_chosen` |
| `livery/` | `window_dark_follows` |
| `logbook/` | `run_log_within_reach`, `run_outside_seen`, `window_exit_keeps_all` |
| `material/` | `files_block_stays_apart`, `files_blocks_join_exact`, `files_clock_links_blocks`, `files_cut_without_keys`, `files_joined_by_hand`, `files_left_out_named`, `files_old_file_refused`, `files_only_window_kept`, `files_order_kept`, `files_split_found_again`, `run_clock_place_travels`, `run_mute_camera_placed`, `run_threads_keep_order`, `sound_all_blocks_count`, `sound_any_count_judged`, `sound_both_sides_alike`, `sound_camera_judged_too`, `sound_channels_split`, `sound_clipping_counted`, `sound_delay_decides`, `sound_hush_reason`, `sound_loudest_block`, `sound_mix_hits_target`, `sound_mix_says_the_name`, `sound_one_pass_agrees`, `sound_peaks_limited`, `sound_silent_no_pair`, `sound_speakers_matched`, `sound_stereo_kept`, `table_blocks_judged`, `table_row_per_channel`, `table_stereo_splits`, `time_drift_taken_out` |
| `menus/` | `window_menu_greys_along`, `window_play_follows_tab`, `window_view_reaches_tabs` |
| `metadata/` | `files_atom_travels`, `files_colour_carried`, `files_data_track_kept`, `files_foreign_untouched`, `text_units_translated` |
| `orders/` | `run_command_built`, `run_project_type_reaches`, `run_switch_changes_it`, `run_switch_has_effect`, `run_three_ways_agree` |
| `pipeline/` | `run_done_tracks_used`, `run_names_as_window`, `run_new_name_checked`, `run_no_drift_noughts`, `run_no_upload_no_hint`, `run_one_shots_return_0`, `run_overwrite_is_said`, `run_own_sound_with_cam`, `run_promise_is_written`, `run_simple_path_agrees`, `run_stays_local`, `run_stop_names_why`, `run_sync_only_no_cut`, `sound_camera_own_used`, `sound_tracks_written`, `time_clock_from_any_file`, `time_length_names_change`, `time_one_track_aligned`, `time_point_pulled_back`, `time_reference_silent`, `time_sound_stays_put`, `time_tracks_alone`, `time_window_is_shared` |
| `player/` | `cut_box_fits_the_picture`, `cut_note_moves_no_shot`, `cut_note_says_who_speaks`, `cut_player_in_sync`, `cut_player_jump_lands`, `cut_player_right_file`, `cut_player_speeds_up`, `window_blocks_placed`, `window_clock_sound_said`, `window_cut_colours`, `window_no_full_screen`, `window_not_started_said`, `window_notes_break_up`, `window_picture_returns`, `window_sound_fault_named`, `window_tc_point_named`, `window_zoom_stays_in` |
| `preflight/` | `auphonic_preset_fits`, `files_lengths_summed`, `files_line_counts_misfit`, `files_set_aside_skipped`, `files_sync_one_recording`, `files_twin_cameras_named`, `run_dry_run_not_stopped`, `run_findings_reach_both`, `run_odd_clock_named`, `run_rate_way_said_right`, `run_space_has_margin`, `sound_bleed_reported`, `table_notes_in_one_row`, `window_size_as_run` |
| `prework/` | `window_prework_box_goes` |
| `project/` | `files_project_first`, `files_project_offered`, `project_close_forgets`, `project_keeps_answers`, `project_leaves_others`, `project_run_comes_back`, `project_settings_return`, `window_restart_carries` |
| `resolve/` | `cut_all_shots_land`, `cut_colour_per_camera`, `cut_jingle_over_start`, `cut_own_rate_counted`, `cut_wide_colour_apart`, `project_amounts_grouped`, `project_audio_counted`, `project_cameras_land`, `project_grades_stay_off`, `project_hdr_follows`, `project_markers_placed`, `project_mix_by_name`, `project_mixed_run_lands`, `project_output_says_hdr`, `project_refusal_heeded`, `project_render_kept`, `project_render_queued`, `project_rerun_updates`, `project_same_offset`, `project_sync_multicam`, `project_tag_reason_fits`, `project_top_rate_wins`, `project_two_stay_two`, `project_two_timelines_go` |
| `running/` | `run_dry_leaves_out`, `window_overwrite_asked`, `window_start_runs` |
| `setup/` | `auphonic_key_by_pipe`, `auphonic_key_kept`, `run_ffmpeg_new_enough`, `run_ffmpeg_not_fetched`, `run_ffmpeg_offered`, `run_install_is_watched` |
| `soundings/` | `files_probed_once` |
| `source/` | `source_checks_proved`, `source_floor_needs_main`, `source_imported_is_whole`, `source_limits_hold`, `source_material_stays`, `source_names_stay_fresh`, `source_needs_lists_agree`, `source_no_loose_ends`, `source_no_real_names`, `source_no_stale_places`, `source_numpy_comes_last`, `source_piece_list_holds`, `source_platform_declared`, `source_reds_carry_value`, `source_resolve_door_shut`, `source_resolve_recalled`, `source_sections_named`, `source_skills_resolve`, `source_test_names_swept`, `text_index_targets_exist`, `text_lists_match`, `text_release_ready`, `text_skills_listed`, `text_tests_listed` |
| `speakers/` | `cut_amounts_grouped`, `cut_own_mic_own_camera`, `run_dry_reports_voices`, `table_back_to_one_name`, `table_row_per_voice`, `voice_answer_kept`, `voice_bleed_gone_first`, `voice_both_splits_stand`, `voice_both_ways_agree`, `voice_close_mics_mixed`, `voice_counts_grouped`, `voice_failed_read_named`, `voice_mhm_is_speech`, `voice_mic_reaches_cut`, `voice_name_is_one_person`, `voice_names_when_sure`, `voice_questions_rank`, `voice_raw_times_kept`, `voice_reason_reaches_log`, `voice_source_travels`, `voice_split_hears_two`, `voice_split_mends_itself`, `voice_split_names_fault`, `voice_tracks_read_once`, `voice_turns_found`, `window_amounts_grouped`, `window_hears_while_split`, `window_note_names_kind`, `window_note_names_way`, `window_note_reason_true`, `window_speakers_as_run` |
| `speech/` | `voice_amounts_grouped`, `voice_every_word_placed`, `voice_language_arrives`, `voice_note_translated`, `voice_words_intact` |
| `stowage/` | `run_choice_kept` |
| `timecode/` | `time_all_ways_agree`, `time_bext_at_own_rate`, `time_clock_read_at_rate`, `time_clock_track_first`, `time_drop_label_kept`, `time_length_is_in_to_out`, `time_over_midnight` |
| `ui/` | `auphonic_speech_read`, `cut_offer_needs_two`, `cut_player_offset_used`, `cut_player_prepared_used`, `cut_two_stay_two`, `project_file_beats_last`, `table_audio_asked_for`, `table_lock_says_why`, `table_one_entry_greyed`, `table_pair_named_alike`, `table_pair_seats_apart`, `table_sync_stem_shown`, `table_tick_keeps_camera`, `table_typed_name_stays`, `window_all_come_up`, `window_answers_arrive`, `window_captions_fit`, `window_captions_langs1`, `window_captions_langs2`, `window_captions_langs3`, `window_captions_langs4`, `window_grey_says_why`, `window_handover_follows`, `window_handover_found`, `window_key_off_line`, `window_marks_take_spot`, `window_offers_restart`, `window_pair_said_apart`, `window_point_named`, `window_project_type_set`, `window_run_handover_kept`, `window_setup_kept_apart`, `window_sheets_fit`, `window_sound_sync_fixed`, `window_stands_still`, `window_symbol_from_file`, `window_title_follows`, `window_tracks_seen_anew`, `window_voice_audio_heard` |
| `upkeep/` | `run_only_newer_offered`, `run_update_says_it_landed`, `run_way_back_offered` |

### Under `resolve/live/` -- beside a running DaVinci Resolve

Not in the suite and not in the count above: `resolve.sh`
starts these by hand, one after another.

| Test | Green means |
|---|---|
| `project_clips_land_right` | Every camera and every shot lands on the track and frame the cut names. |
| `project_pool_takes_all` | Every file the run hands over is in the media pool and found again. |
| `project_run_puts_back` | A run that never tidied up leaves nothing, and what it remembers comes back. |
| `project_settings_arrive` | The project the run asks for is there, with the rate and size it named. |

<!-- overview ends -->
