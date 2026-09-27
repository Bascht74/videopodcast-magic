# Test durations, per release

What each test took on the builder, one section per release, so that a
change which makes the suite slower shows up as a number and not as a
feeling. `tests/state/longest` cannot do this: it holds only the newest
figures, and only for the queue.

**The rule.** At every release, after the green run and before the
word, `cd tests && bash builder_times.sh --record <version>`. It finds
the green run whose commit says that version, writes
`tests/state/longest` from its slowest job as before, and appends a
section here. Nothing in this file is written by hand. Skill `freigabe`
says why and when.

**What a section holds.** The run it was read from; the slowest job's
wall time, which is what a push waits for; the six jobs' wall times
and the sum of their test seconds, which is what the builder bills; the
15 longest tests; and every test in a folded block, which the next
release's change is reckoned against.

**The figure per test is a trimmed mean over the six system jobs**
(Linux, macOS and Windows, each on two versions of Python): the highest
and the lowest go, the four between are averaged, so no one machine's
bad minute decides it. A test that ran on fewer than six jobs -- set
aside on a platform, or platform-neutral and so run once, on the
neutral job -- takes the median of what there is instead, and the
table says "median of n".

**Change** is the trimmed mean against the previous section, in
seconds; "new" for a test that section did not have. **A test that grew
by more than 20 % and by at least 10 s is marked grown**, listed under
the table, and the release report names it.

## 3.0.0b24 -- 2026-09-25

Run 36190779960 on `runde-b24` at `f8da359`: suite #735 on runde-b24 -- separation off.

The slowest job, and what a push waits for: **Windows py3.10, 1067 s**.
The suite summed over the trimmed means: **2722 s** for 332 tests.

| job | wall s | tests summed s |
|---|---:|---:|
| Linux py3.10 | 597 | 2372 |
| Linux py3.14 | 519 | 2225 |
| macOS py3.10 | 708 | 2224 |
| macOS py3.14 | 606 | 2009 |
| Windows py3.10 | 1067 | 4009 |
| Windows py3.14 | 988 | 4013 |

The 15 longest by trimmed mean:

| test | Linux py3.10 | Linux py3.14 | macOS py3.10 | macOS py3.14 | Windows py3.10 | Windows py3.14 | trimmed | change |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| `window_captions_fit` | 149 | 139 | 138 | 139 | 257 | 276 | 171.0 | -- |
| `run_new_name_checked` | 72 | 63 | 59 | 46 | 106 | 105 | 74.8 | -- |
| `run_promise_is_written` | 53 | 49 | 42 | 38 | 158 | 146 | 72.5 | -- |
| `run_switch_changes_it` | 60 | 57 | 52 | 53 | 93 | 115 | 65.8 | -- |
| `sound_camera_own_used` | 44 | 40 | 35 | 34 | 121 | 132 | 60.0 | -- |
| `time_one_track_aligned` | 50 | 43 | 45 | 37 | 101 | 93 | 57.8 | -- |
| `sound_tracks_written` | 51 | 46 | 36 | 36 | 64 | 68 | 49.2 | -- |
| `project_errors_reach_run` | 36 | 30 | 23 | 23 | 82 | 113 | 42.8 | -- |
| `run_mute_camera_placed` | 31 | 29 | 21 | 19 | 85 | 88 | 41.5 | -- |
| `time_guess_refused` | 42 | 41 | 36 | 35 | 50 | 47 | 41.5 | -- |
| `run_done_tracks_used` | 32 | 31 | 23 | 25 | 73 | 92 | 40.2 | -- |
| `project_mixed_run_lands` | 28 | 30 | 22 | 22 | 91 | 79 | 39.8 | -- |
| `source_material_stays` | 32 | 33 | 29 | 25 | 63 | 66 | 39.2 | -- |
| `time_sound_stays_put` | 31 | 28 | 23 | 22 | 74 | 83 | 39.0 | -- |
| `time_tracks_alone` | 43 | 37 | 25 | 23 | 48 | 40 | 36.2 | -- |

Grown: no earlier section to compare with.

<details>
<summary>Every test, 332</summary>

```text
test Linux_py3.10 Linux_py3.14 macOS_py3.10 macOS_py3.14 Windows_py3.10 Windows_py3.14 trimmed
window_captions_fit 149 139 138 139 257 276 171.0
run_new_name_checked 72 63 59 46 106 105 74.8
run_promise_is_written 53 49 42 38 158 146 72.5
run_switch_changes_it 60 57 52 53 93 115 65.8
sound_camera_own_used 44 40 35 34 121 132 60.0
time_one_track_aligned 50 43 45 37 101 93 57.8
sound_tracks_written 51 46 36 36 64 68 49.2
project_errors_reach_run 36 30 23 23 82 113 42.8
run_mute_camera_placed 31 29 21 19 85 88 41.5
time_guess_refused 42 41 36 35 50 47 41.5
run_done_tracks_used 32 31 23 25 73 92 40.2
project_mixed_run_lands 28 30 22 22 91 79 39.8
source_material_stays 32 33 29 25 63 66 39.2
time_sound_stays_put 31 28 23 22 74 83 39.0
time_tracks_alone 43 37 25 23 48 40 36.2
run_choice_kept 38 31 25 22 42 43 34.0
voice_both_splits_stand 27 28 41 27 39 38 33.0
time_drift_taken_out 26 23 35 22 49 47 32.8
run_stop_names_why 28 29 20 12 50 48 31.2
run_sync_only_no_cut 22 19 16 17 56 53 27.8
time_tracks_sit_together 20 20 36 19 37 32 27.0
text_no_german_left 25 26 22 20 36 34 26.8
table_lock_says_why 26 23 26 26 - - 26.0
run_log_within_reach 30 22 18 14 34 31 25.2
files_only_window_kept 19 18 14 15 40 39 22.8
window_all_come_up 16 15 26 16 30 30 22.0
window_speaker_cell_fits 21 20 17 30 27 20 22.0
cut_player_jump_lands 19 19 21 24 22 22 21.0
project_run_comes_back 18 18 23 18 22 21 19.8
run_simple_path_agrees 18 17 13 13 31 31 19.8
source_no_real_names 19 16 19 19 22 21 19.5
window_answers_arrive 17 16 17 15 21 23 17.8
run_no_drift_noughts 10 11 15 18 26 28 17.5
text_only_texts_change 15 13 13 18 20 20 16.5
source_no_loose_ends 16 16 14 9 24 19 16.2
time_offset_found 16 16 9 10 27 23 16.2
table_names_one_order 15 7 16 7 26 29 16.0
window_stages_named 13 11 13 17 19 19 15.5
table_row_per_voice - 12 25 15 16 15 15.0
table_tick_keeps_camera 13 12 19 11 18 17 15.0
run_outside_seen 14 14 8 8 23 26 14.8
sound_mix_hits_target 13 11 10 7 29 23 14.2
window_play_follows_tab 11 11 16 16 14 15 14.0
window_sheets_fit 11 11 18 17 - - 14.0
cut_player_prepared_used 11 11 12 15 14 15 13.0
window_grey_says_why 10 10 13 14 16 15 13.0
window_restart_carries 12 11 10 8 18 23 12.8
cut_own_mic_own_camera 6 7 12 16 16 15 12.5
text_languages_covered 12 10 7 12 16 16 12.5
window_offers_restart 11 12 13 10 15 14 12.5
run_clock_place_travels 8 7 8 9 24 25 12.2
table_pair_seats_apart 11 11 10 13 14 14 12.2
window_stands_still 9 10 20 11 14 14 12.2
window_marks_take_spot 10 10 13 28 12 13 12.0
cut_offer_needs_two 10 9 11 11 17 15 11.8
project_file_beats_last 9 9 13 14 15 11 11.8
project_settings_return 11 11 12 10 14 13 11.8
source_resolve_door_shut 10 12 14 9 13 12 11.8
window_menu_greys_along 11 9 11 12 13 14 11.8
run_stays_local 6 10 7 10 19 22 11.5
text_lang_settled_first 11 10 8 11 15 14 11.5
sound_delay_decides 9 11 18 16 9 8 11.2
table_pair_named_alike 10 9 12 6 15 14 11.2
time_clock_beats_guess 5 6 12 13 16 14 11.2
cut_voice_on_its_camera 7 7 7 8 22 33 11.0
cut_player_in_sync 9 9 11 11 12 12 10.8
time_reference_silent 10 9 7 7 17 17 10.8
voice_close_mics_mixed 5 4 7 11 20 20 10.8
window_prework_box_goes 7 6 7 9 19 19 10.5
window_handover_found 9 10 14 15 8 8 10.2
window_idle_bar_hidden 7 8 8 11 15 14 10.2
window_view_reaches_tabs 11 10 15 10 9 10 10.2
table_blocks_judged 7 9 10 9 12 12 10.0
text_german_arrives 7 7 13 6 13 14 10.0
sound_join_any_rate 5 8 4 2 24 21 9.5
window_reads_as_chosen 9 10 9 7 10 10 9.5
window_tc_point_named 8 8 10 8 12 12 9.5
run_own_sound_with_cam 6 8 10 6 14 13 9.2
sound_speakers_matched 6 6 7 7 19 17 9.2
window_dark_follows 6 7 10 8 12 12 9.2
run_ffmpeg_new_enough 9 8 7 7 13 12 9.0
run_overwrite_is_said 6 11 7 14 9 8 8.8
source_limits_hold 9 8 8 6 11 10 8.8
table_back_to_one_name 7 8 8 8 11 11 8.8
window_marks_come_back 7 8 8 10 10 9 8.8
source_reds_carry_value 7 9 7 8 10 10 8.5
table_audio_asked_for 8 7 8 8 9 9 8.2
sound_stereo_kept 4 3 10 7 11 14 8.0
window_axis_asks_again 8 7 7 7 11 10 8.0
window_handover_follows 4 6 8 14 9 9 8.0
files_project_first 5 6 8 7 10 10 7.8
run_only_newer_offered 7 8 6 5 9 9 7.5
sound_both_sides_alike 4 6 7 5 11 11 7.2
time_preview_fit_as_run 6 7 5 4 12 11 7.2
time_second_try_places 5 5 6 5 14 13 7.2
files_block_stays_apart 6 4 7 4 11 11 7.0
sound_peaks_limited 4 5 7 6 11 10 7.0
table_stereo_splits 6 5 7 6 10 9 7.0
run_switch_has_effect 6 5 7 4 9 9 6.8
source_imported_is_whole 6 6 6 3 10 9 6.8
table_row_per_channel 7 5 6 6 9 8 6.8
window_project_type_set 6 6 7 4 8 8 6.8
project_keeps_answers 6 6 7 5 8 7 6.5
table_sync_stem_shown 6 5 6 6 9 8 6.5
window_blocks_placed 6 6 6 6 9 8 6.5
files_colour_fair 4 4 7 3 10 10 6.2
files_probed_once 4 4 9 6 8 7 6.2
files_sync_one_recording 4 4 11 5 7 8 6.0
run_install_is_watched 6 5 8 6 6 6 6.0
sound_camera_judged_too 4 5 5 3 9 10 5.8
sound_any_count_judged 4 4 5 2 9 9 5.5
sound_one_pass_agrees 6 6 4 5 - - 5.5
run_ffmpeg_not_fetched 5 5 5 4 6 7 5.2
source_test_names_swept 5 6 4 2 6 7 5.2
auphonic_key_answer_fits 4 4 6 4 6 6 5.0
files_lengths_summed 4 4 3 2 9 9 5.0
window_title_follows 4 5 4 6 5 6 5.0
auphonic_none_chosen 5 4 4 4 6 6 4.8
files_old_file_refused 4 5 4 3 6 6 4.8
files_set_aside_skipped 5 4 3 2 7 8 4.8
run_threads_keep_order 5 4 5 4 5 5 4.8
sound_each_gets_a_track 3 3 4 3 9 9 4.8
table_sync_none_derived 4 4 5 4 6 7 4.8
time_which_way_is_said 5 5 4 2 6 5 4.8
window_point_named 3 4 6 2 6 6 4.8
cut_box_fits_the_picture 5 4 4 4 5 5 4.5
files_atom_travels 4 4 4 3 6 7 4.5
files_block_out_and_back 4 3 4 3 7 7 4.5
files_by_file_holds 4 4 4 3 6 6 4.5
sound_channels_split 3 4 4 3 9 7 4.5
source_checks_proved 4 5 4 3 5 5 4.5
source_resolve_recalled 6 4 5 4 - - 4.5
files_clock_links_blocks 2 2 4 2 9 9 4.2
files_mute_clip_intro 5 4 2 2 6 6 4.2
project_close_forgets 4 4 3 2 6 8 4.2
project_leaves_others 4 3 5 3 6 5 4.2
run_which_script 4 4 3 1 6 6 4.2
sound_clipping_counted 4 3 3 2 7 7 4.2
time_weak_at_its_clock 4 3 3 2 7 8 4.2
voice_bleed_gone_first 3 3 3 3 8 9 4.2
window_overwrite_asked 3 4 5 3 5 6 4.2
window_start_runs 4 4 4 4 5 5 4.2
cut_preview_is_the_run 2 2 4 2 9 8 4.0
files_colour_carried 3 2 4 3 7 6 4.0
files_data_track_kept 3 3 4 3 7 6 4.0
files_intro_proposed 4 4 2 2 6 6 4.0
text_whole_sentences 4 4 2 2 6 6 4.0
time_track_starts_late 2 3 3 3 7 7 4.0
voice_answer_kept 4 3 4 3 5 5 4.0
window_picture_returns 3 2 5 4 5 4 4.0
window_setup_kept_apart 3 3 5 2 5 5 4.0
window_sound_fault_named 3 3 5 3 5 5 4.0
run_metrics_add_up 3 3 3 2 7 6 3.8
sound_all_blocks_count 3 4 3 2 5 5 3.8
source_sections_named 4 4 3 3 5 4 3.8
table_notes_in_one_row 3 4 3 2 6 5 3.8
text_numbers_fit_reader 4 4 2 2 5 5 3.8
text_shown_catalogued 4 3 3 2 5 5 3.8
time_unheard_file_named 4 3 3 2 5 6 3.8
window_choices_refit 4 3 3 2 5 5 3.8
window_hears_while_split 4 4 2 2 5 5 3.8
files_twin_cameras_named 4 3 2 2 5 5 3.5
run_bar_never_falls 3 4 3 2 5 4 3.5
run_odd_clock_named 2 3 3 1 7 6 3.5
sound_bleed_reported 3 3 3 2 5 6 3.5
sound_check_reads_once 3 2 2 3 7 6 3.5
window_voice_audio_heard 4 3 3 3 5 4 3.5
cut_player_speeds_up 3 3 2 2 5 5 3.2
files_foreign_untouched 3 3 2 2 5 5 3.2
files_hdr_complete 3 3 2 2 5 5 3.2
run_command_built 4 3 2 1 5 4 3.2
source_names_stay_fresh 3 3 3 2 5 4 3.2
time_axis_keys_agree 3 3 2 2 5 5 3.2
time_axis_measured 3 3 2 1 5 5 3.2
time_measured_place_wins 3 2 2 1 6 6 3.2
window_no_full_screen 3 3 3 2 4 5 3.2
window_not_started_said 3 3 3 3 4 4 3.2
window_size_as_run 3 2 3 3 4 5 3.2
auphonic_key_by_pipe 3 3 2 3 3 3 3.0
auphonic_key_kept - - - - 3 3 3.0
run_bar_tracks_work 3 3 2 1 5 4 3.0
run_update_says_it_landed 3 2 2 3 4 4 3.0
time_bext_at_own_rate 3 3 2 2 4 4 3.0
time_clock_read_at_rate 3 2 2 2 5 5 3.0
voice_words_intact 2 2 - - 4 4 3.0
cut_note_moves_no_shot 3 3 1 2 3 3 2.8
cut_two_stay_two 2 3 2 2 4 4 2.8
files_cut_without_keys 3 2 2 2 4 4 2.8
files_line_counts_misfit 2 2 3 3 4 3 2.8
files_project_offered 3 2 2 2 4 4 2.8
run_space_has_margin 3 2 2 2 5 4 2.8
run_three_ways_agree 3 2 2 2 4 4 2.8
source_numpy_comes_last 3 3 1 1 4 4 2.8
table_no_place_not_wide 3 3 1 2 3 4 2.8
text_units_translated 3 2 2 2 4 4 2.8
time_all_ways_agree 3 2 2 2 4 4 2.8
voice_counts_grouped 2 2 3 2 4 4 2.8
voice_every_word_placed 3 2 2 1 4 4 2.8
voice_mhm_is_speech 3 2 2 2 4 5 2.8
voice_names_when_sure 2 2 3 2 4 4 2.8
voice_split_names_fault 2 2 3 1 4 4 2.8
voice_turns_found 2 2 2 1 5 5 2.8
window_cut_colours 3 2 1 2 4 4 2.8
window_foot_on_one_line 2 3 3 2 4 3 2.8
window_grey_opens_again 3 2 3 2 3 3 2.8
window_speakers_as_run 3 2 2 2 4 4 2.8
window_symbol_from_file 3 2 2 2 4 4 2.8
auphonic_may_be_skipped 3 2 1 1 4 4 2.5
auphonic_unsaved_said 3 2 2 2 4 3 2.5
cut_note_says_who_speaks 2 2 2 2 4 4 2.5
files_blocks_join_exact 3 1 2 1 4 4 2.5
files_curve_kept_once 3 2 2 1 4 3 2.5
project_handover_built 2 2 3 1 4 3 2.5
project_two_stay_two 3 2 2 1 3 3 2.5
project_two_timelines_go 3 2 2 1 3 3 2.5
run_shortcut_laid_once 2 2 1 2 5 4 2.5
run_way_back_offered 3 3 1 1 3 3 2.5
sound_block_gap_said 2 2 2 2 4 4 2.5
sound_join_order 2 2 2 2 4 4 2.5
sound_mix_says_the_name 3 2 1 2 3 3 2.5
table_one_entry_greyed 3 2 2 2 3 3 2.5
time_block_holds_on 3 2 2 1 3 3 2.5
time_clock_from_any_file 3 2 2 2 3 4 2.5
time_clock_track_first 2 2 2 2 4 4 2.5
time_fit_reports 3 2 1 2 3 3 2.5
voice_both_ways_agree 3 2 2 1 3 4 2.5
voice_split_mends_itself 3 2 2 2 4 3 2.5
window_amounts_grouped 3 2 2 2 4 3 2.5
window_note_names_kind 3 2 1 2 3 3 2.5
auphonic_preset_fits 2 2 1 2 3 3 2.2
auphonic_run_delivers 2 2 1 1 4 4 2.2
cut_amounts_grouped 2 2 2 1 3 3 2.2
cut_edl_says_drop_frame 2 1 2 2 3 3 2.2
cut_jingle_over_start 3 1 1 2 3 3 2.2
cut_list_rebuilt 3 2 1 1 3 3 2.2
cut_own_rate_counted 2 2 2 1 3 3 2.2
cut_rebuild_keeps_all 2 3 1 1 3 3 2.2
cut_right_camera 2 2 1 1 4 4 2.2
cut_speech_time_fits 2 2 1 1 4 4 2.2
cut_wide_not_on_speech 2 2 2 2 3 3 2.2
files_joined_by_hand 2 2 1 1 5 4 2.2
files_order_kept 3 2 1 1 3 3 2.2
files_split_found_again 2 2 2 1 3 3 2.2
project_amounts_grouped 2 2 2 1 3 3 2.2
project_every_offset 2 2 1 2 4 3 2.2
project_markers_placed 2 2 2 1 4 3 2.2
project_output_says_hdr 3 2 1 1 4 3 2.2
project_real_frame 2 2 2 1 3 4 2.2
project_sync_multicam 2 2 2 1 3 3 2.2
run_dry_reports_voices 3 2 1 1 3 3 2.2
run_dry_run_not_stopped 3 2 1 1 4 3 2.2
run_ffmpeg_offered 2 2 1 2 3 3 2.2
run_project_type_reaches 2 2 1 1 4 4 2.2
run_starter_arch_fits 3 2 1 1 3 3 2.2
table_recording_shown 2 1 2 2 4 3 2.2
text_tests_listed 2 3 1 2 2 3 2.2
time_point_pulled_back 2 2 2 1 3 3 2.2
time_window_is_shared 2 2 2 1 4 3 2.2
time_zero_at_in_point 2 2 2 1 3 3 2.2
voice_amounts_grouped 2 2 2 1 3 3 2.2
voice_questions_rank 3 2 1 1 3 4 2.2
voice_raw_times_kept 2 1 2 1 4 4 2.2
voice_tracks_read_once 3 2 1 1 3 3 2.2
window_clock_sound_said 2 2 1 1 5 4 2.2
window_note_reason_true 2 2 2 2 3 4 2.2
window_notes_break_up 2 2 2 2 3 4 2.2
window_zoom_stays_in 2 2 2 2 3 3 2.2
auphonic_key_out_of_view 2 2 1 1 3 3 2.0
auphonic_mono_not_stereo 2 2 1 1 3 3 2.0
auphonic_preset_checked 2 1 1 2 3 3 2.0
auphonic_speech_read 2 2 1 1 3 3 2.0
auphonic_stays_quiet 2 2 1 1 3 3 2.0
cut_all_shots_land 2 2 2 1 3 2 2.0
cut_no_wide_silences 3 2 1 1 4 2 2.0
cut_player_right_file 2 1 2 1 3 3 2.0
cut_rules_hold 2 2 1 1 4 3 2.0
cut_together_read_order 3 2 1 1 3 2 2.0
files_left_out_named 2 1 1 1 4 4 2.0
files_named_as_written 2 2 1 1 3 3 2.0
project_audio_counted 2 1 2 1 4 3 2.0
project_cameras_land 2 2 1 1 4 3 2.0
project_each_track_set 2 2 1 1 3 3 2.0
project_hdr_follows 3 1 1 1 3 3 2.0
project_mix_by_name 2 1 1 1 4 4 2.0
project_refusal_heeded 2 2 1 1 3 3 2.0
project_render_kept 2 2 1 1 3 3 2.0
project_render_queued 2 2 1 1 3 3 2.0
project_rerun_updates 3 2 1 1 3 2 2.0
project_same_offset 2 2 1 1 4 3 2.0
project_top_rate_wins 3 2 1 1 3 2 2.0
run_findings_reach_both 2 2 1 1 3 3 2.0
run_prework_listed 2 2 1 1 3 3 2.0
run_rate_way_said_right 2 2 1 1 3 3 2.0
sound_camera_counts 1 2 1 2 3 4 2.0
sound_hush_reason 2 2 1 1 3 3 2.0
sound_loudest_block 3 1 1 1 3 3 2.0
sound_silent_no_pair 2 1 1 2 3 3 2.0
table_camera_proposed 2 2 1 1 3 3 2.0
table_names_reach_camera 2 2 1 1 3 3 2.0
table_sync_keeps_stem 2 1 2 1 4 3 2.0
text_lists_match 2 2 1 1 4 3 2.0
time_drop_label_kept 3 2 1 1 3 2 2.0
time_over_midnight 2 2 1 1 3 3 2.0
voice_failed_read_named 2 2 1 1 4 3 2.0
voice_language_arrives 2 2 1 1 3 3 2.0
voice_name_is_one_person 2 2 1 1 4 3 2.0
voice_reason_reaches_log 2 2 1 1 3 3 2.0
voice_source_travels 2 1 1 2 3 3 2.0
window_run_handover_kept 2 2 1 1 3 3 2.0
cut_both_are_shown 2 1 1 1 3 3 1.8
cut_opening_wide_holds 2 1 1 1 3 3 1.8
cut_player_offset_used 2 2 1 1 3 2 1.8
project_grades_stay_off 2 2 1 1 3 2 1.8
project_tag_reason_fits 2 1 1 1 3 3 1.8
run_no_upload_no_hint 2 1 1 1 3 3 1.8
source_no_stale_places 2 2 1 1 2 3 1.8
text_release_ready 2 1 0 1 3 3 1.8
time_bad_point_dropped 2 2 1 1 3 2 1.8
time_length_is_in_to_out 2 1 1 1 3 3 1.8
voice_mic_reaches_cut 2 1 1 1 3 3 1.8
voice_note_translated 2 2 1 1 3 2 1.8
cut_colour_per_camera 2 1 1 1 3 2 1.5
cut_one_camera_marks 2 1 1 1 3 2 1.5
cut_wide_colour_apart 2 1 1 1 2 2 1.5
source_floor_needs_main 0 1 1 1 3 3 1.5
time_length_names_change 1 1 1 1 3 3 1.5
files_named_by_folder 1 2 1 1 - - 1.0
source_piece_list_holds 1 1 0 1 2 1 1.0
source_skills_resolve 0 0 0 1 1 1 0.5
text_index_targets_exist 0 0 0 1 1 1 0.5
text_skills_listed 0 1 0 0 1 1 0.5
source_needs_lists_agree 0 0 0 0 1 0 0.0
```

</details>

## 3.0.0b25 -- 2026-09-26

Run 36251871464 on `main` at `1ae49a2`: suite #781 on main -- separation off.

The slowest job, and what a push waits for: **Windows py3.14, 848 s**.
The suite summed over the trimmed means: **2394 s** for 354 tests.

| job | wall s | tests summed s |
|---|---:|---:|
| Linux py3.10 | 508 | 2106 |
| Linux py3.14 | 401 | 1574 |
| macOS py3.10 | 659 | 2060 |
| macOS py3.14 | 478 | 1306 |
| Neutral py3.14 | 64 | 170 |
| Windows py3.10 | 842 | 3217 |
| Windows py3.14 | 848 | 3347 |

The 15 longest by trimmed mean:

| test | Linux py3.10 | Linux py3.14 | macOS py3.10 | macOS py3.14 | Neutral py3.14 | Windows py3.10 | Windows py3.14 | trimmed | change |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| `run_switch_changes_it` | 39 | 28 | 46 | 37 | - | 75 | 80 | 49.2 | -16.5 |
| `source_material_stays` | 43 | 39 | 37 | 34 | - | 71 | 71 | 47.5 | +8.3 |
| `window_speaker_cell_fits` | 35 | 28 | 60 | 36 | - | 57 | 56 | 46.0 | +24.0 **grown** |
| `time_phase_only_mixed` | 45 | 34 | 24 | 18 | - | 88 | 77 | 45.0 | new |
| `run_promise_is_written` | 38 | 27 | 35 | 28 | - | 71 | 77 | 43.0 | -29.5 |
| `run_new_name_checked` | 45 | 30 | 30 | 22 | - | 54 | 57 | 39.8 | -35.0 |
| `table_lock_says_why` | 35 | 24 | 52 | - | - | - | - | 35.0 (median of 3) | +9.0 |
| `run_stop_names_why` | 37 | 20 | 28 | 14 | - | 51 | 44 | 32.2 | +1.1 |
| `run_simple_path_agrees` | 17 | 14 | 36 | 22 | - | 51 | 53 | 31.5 | +11.7 **grown** |
| `table_row_per_voice` | 25 | 32 | 31 | - | - | 30 | 33 | 31.0 (median of 5) | +16.0 **grown** |
| `voice_both_splits_stand` | 27 | 22 | 36 | 23 | - | 36 | 36 | 30.5 | -2.5 |
| `run_choice_kept` | 47 | 22 | 22 | 17 | - | 38 | 39 | 30.2 | -3.8 |
| `text_no_german_left` | 29 | 22 | 25 | 19 | - | 38 | 39 | 28.5 | +1.7 |
| `run_dry_leaves_out` | 25 | 21 | 19 | 19 | - | 46 | 50 | 27.8 | new |
| `run_no_drift_noughts` | 22 | 17 | 15 | 20 | - | 52 | 54 | 27.8 | +10.2 **grown** |

Grown by more than 20 % and at least 10 s: `run_simple_path_agrees` 19.8 -> 31.5 s, `table_row_per_voice` 15.0 -> 31.0 s, `run_no_drift_noughts` 17.5 -> 27.8 s, `window_speaker_cell_fits` 22.0 -> 46.0 s, `table_pair_seats_apart` 12.2 -> 26.8 s, `cut_player_prepared_used` 13.0 -> 27.0 s.

<details>
<summary>Every test, 354</summary>

```text
test Linux_py3.10 Linux_py3.14 macOS_py3.10 macOS_py3.14 Neutral_py3.14 Windows_py3.10 Windows_py3.14 trimmed
run_switch_changes_it 39 28 46 37 - 75 80 49.2
source_material_stays 43 39 37 34 - 71 71 47.5
window_speaker_cell_fits 35 28 60 36 - 57 56 46.0
time_phase_only_mixed 45 34 24 18 - 88 77 45.0
run_promise_is_written 38 27 35 28 - 71 77 43.0
run_new_name_checked 45 30 30 22 - 54 57 39.8
table_lock_says_why 35 24 52 - - - - 35.0
run_stop_names_why 37 20 28 14 - 51 44 32.2
run_simple_path_agrees 17 14 36 22 - 51 53 31.5
table_row_per_voice 25 32 31 - - 30 33 31.0
voice_both_splits_stand 27 22 36 23 - 36 36 30.5
run_choice_kept 47 22 22 17 - 38 39 30.2
text_no_german_left 29 22 25 19 - 38 39 28.5
run_dry_leaves_out 25 21 19 19 - 46 50 27.8
run_no_drift_noughts 22 17 15 20 - 52 54 27.8
cut_player_prepared_used 24 20 31 16 - 33 39 27.0
table_pair_seats_apart 27 22 37 26 - 27 27 26.8
sound_camera_own_used 26 19 18 17 - 43 46 26.5
sound_tracks_written 24 18 19 19 - 43 46 26.2
window_all_come_up 18 14 28 19 - 35 36 25.0
time_one_track_aligned 26 19 16 14 - 38 42 24.8
files_only_window_kept 19 14 16 13 - 41 42 22.5
run_log_within_reach 27 18 16 12 - 29 31 22.5
time_guess_refused 22 15 15 13 - 36 37 22.0
project_errors_reach_run 17 19 11 9 - 40 59 21.8
run_done_tracks_used 19 15 16 11 - 35 38 21.2
time_tracks_alone 23 16 15 13 - 32 31 21.2
cut_player_jump_lands 20 18 20 20 - 22 25 20.5
project_mixed_run_lands 17 13 12 9 - 40 42 20.5
project_run_comes_back 20 18 21 17 - 24 21 20.0
table_names_one_order 16 11 21 8 - 39 31 19.8
run_mute_camera_placed 17 14 13 12 - 33 33 19.2
window_answers_arrive 17 15 17 23 - 22 21 19.2
time_sound_stays_put 15 14 14 15 - 32 33 19.0
table_tick_keeps_camera 17 17 28 14 - 20 19 18.2
window_grey_says_why 14 13 29 19 - 23 16 18.0
run_clock_place_travels 13 8 16 5 - 28 28 16.2
time_drift_taken_out 16 13 9 10 - 28 25 16.0
window_marks_take_spot 10 8 28 12 - 17 23 15.5
source_no_loose_ends - - - - 15 - - 15.0
time_tracks_sit_together 13 16 12 6 - 19 20 15.0
text_only_texts_change 18 12 11 10 - 18 19 14.8
time_offset_found 9 6 16 5 - 28 28 14.8
time_weak_as_run 14 11 10 7 - 39 23 14.5
window_offers_restart 17 14 14 10 - 14 16 14.5
project_settings_return 13 11 16 12 - 18 15 14.0
project_ticks_come_back 15 14 12 9 - 15 16 14.0
window_restart_carries 12 8 13 8 - 24 23 14.0
window_stands_still 15 10 19 7 - 16 14 13.8
cut_voice_on_its_camera 13 8 13 5 - 20 22 13.5
cut_own_mic_own_camera 12 9 14 6 - 18 20 13.2
sound_speakers_matched 7 3 10 4 - 31 40 13.0
run_stays_local 9 6 18 5 - 18 26 12.8
window_play_follows_tab 11 10 16 12 - 13 14 12.5
window_captions_fit 9 7 12 10 - 18 19 12.2
window_stages_named 11 10 10 9 - 20 18 12.2
sound_mix_hits_target 9 5 17 5 - 17 26 12.0
run_outside_seen 12 7 12 5 - 17 16 11.8
run_sync_only_no_cut 8 5 14 5 - 20 28 11.8
table_pair_named_alike 11 8 14 8 - 14 18 11.8
window_menu_greys_along 11 10 12 10 - 15 14 11.8
cut_offer_needs_two 10 7 13 9 - 14 14 11.5
time_clock_beats_guess 13 6 12 4 - 15 16 11.5
window_idle_bar_hidden 9 8 10 9 - 18 35 11.5
run_own_sound_with_cam 8 6 17 3 - 14 24 11.2
text_lang_settled_first 9 5 12 10 - 14 16 11.2
cut_player_in_sync 10 9 11 11 - 12 14 11.0
time_reference_silent 8 5 11 4 - 18 34 10.5
files_project_first 10 7 10 7 - 14 14 10.2
run_ffmpeg_new_enough 10 7 12 3 - 12 12 10.2
text_german_arrives 10 6 14 3 - 12 13 10.2
voice_close_mics_mixed 8 5 10 4 - 18 18 10.2
text_languages_covered 12 7 7 3 - 14 20 10.0
time_scatter_not_placed 9 8 9 6 - 14 14 10.0
window_project_type_set 10 7 17 9 - 11 10 10.0
window_sheets_fit 11 8 18 9 - - - 10.0
project_file_beats_last 10 8 8 8 - 13 22 9.8
run_names_as_window 9 9 8 6 - 24 13 9.8
run_one_shots_return_0 11 7 8 7 - 13 15 9.8
window_marks_come_back 9 8 17 9 - 10 11 9.8
window_reads_as_chosen 10 8 11 6 - 11 10 9.8
table_audio_asked_for 9 7 10 7 - 11 12 9.2
time_thin_block_refused 10 7 6 5 - 38 14 9.2
window_axis_asks_again 9 7 16 5 - 11 10 9.2
source_no_real_names - - - - 9 - - 9.0
table_blocks_judged 8 7 8 6 - 13 19 9.0
time_second_try_places 7 6 9 4 - 14 16 9.0
table_back_to_one_name 8 7 12 7 - 10 10 8.8
window_tc_point_named 8 7 9 7 - 11 13 8.8
window_view_reaches_tabs 8 7 10 5 - 10 10 8.8
time_preview_fit_as_run 9 6 9 3 - 10 10 8.5
files_block_stays_apart 8 6 6 4 - 13 20 8.2
window_prework_box_goes 6 6 9 6 - 12 12 8.2
source_limits_hold - - - - 8 - - 8.0
source_reds_carry_value - - - - 8 - - 8.0
source_resolve_door_shut - - - - 8 - - 8.0
window_dark_follows 8 7 8 6 - 9 9 8.0
window_exit_keeps_all 9 6 6 4 - 11 13 8.0
table_row_per_channel 7 5 9 5 - 10 18 7.8
sound_peaks_limited 8 4 7 3 - 11 12 7.5
run_overwrite_is_said 7 5 7 4 - 10 11 7.2
sound_stereo_kept 6 4 7 4 - 11 12 7.0
files_probed_once 5 3 8 6 - 9 8 6.8
run_only_newer_offered 8 6 5 4 - 8 9 6.8
project_keeps_answers 7 5 7 4 - 8 7 6.5
sound_delay_decides 6 4 5 3 - 10 11 6.2
table_stereo_splits 6 5 6 5 - 8 9 6.2
table_sync_stem_shown 6 5 6 5 - 8 8 6.2
run_install_is_watched 6 6 6 5 - 6 7 6.0
window_blocks_placed 6 5 7 5 - - 9 6.0
files_colour_fair 4 4 5 3 - 12 10 5.8
run_switch_has_effect 6 4 5 2 - 8 8 5.8
sound_both_sides_alike 5 4 4 4 - 10 10 5.8
source_imported_is_whole 6 4 6 2 - 7 7 5.8
window_handover_follows 6 4 5 4 - 8 8 5.8
window_handover_found 6 4 5 4 - 8 8 5.8
window_overwrite_asked 6 4 6 3 - 7 7 5.8
window_pair_said_apart 6 4 5 4 - 10 8 5.8
files_sync_one_recording 4 4 5 3 - 9 10 5.5
sound_camera_judged_too 5 4 4 3 - 10 9 5.5
sound_any_count_judged 5 3 3 4 - 9 9 5.2
window_point_named 6 4 4 4 - 7 7 5.2
window_tracks_seen_anew 5 4 5 4 - 9 7 5.2
auphonic_key_answer_fits 5 5 5 3 - 6 5 5.0
table_sync_none_derived 5 4 4 3 - 7 8 5.0
table_typed_name_stays 5 4 5 4 - 6 8 5.0
auphonic_none_chosen 5 4 4 3 - 6 6 4.8
files_lengths_summed 5 3 3 2 - 9 8 4.8
run_threads_keep_order 5 4 5 4 - 5 5 4.8
sound_each_gets_a_track 3 2 3 3 - 10 11 4.8
files_block_out_and_back 5 3 4 3 - 6 7 4.5
files_data_track_kept 4 4 3 2 - 7 7 4.5
sound_channels_split 4 2 5 2 - 8 7 4.5
sound_join_any_rate 4 3 3 2 - 9 8 4.5
time_weak_at_its_clock 4 3 4 2 - 7 7 4.5
cut_preview_is_the_run 2 2 4 3 - 8 8 4.2
files_set_aside_skipped 3 3 4 1 - 7 7 4.2
run_which_script 4 3 4 2 - 6 6 4.2
time_axis_measured 4 3 2 1 - 8 8 4.2
time_short_cam_as_run 4 3 4 3 - 6 6 4.2
voice_bleed_gone_first 5 3 3 1 - 6 9 4.2
window_title_follows 4 4 4 2 - 5 6 4.2
files_atom_travels 3 2 2 1 - 10 9 4.0
files_clock_links_blocks 3 2 4 2 - 7 8 4.0
sound_one_pass_agrees 7 4 4 4 - - - 4.0
source_checks_proved - - - - 4 - - 4.0
source_resolve_recalled 5 4 4 3 - - - 4.0
source_test_names_swept - - - - 4 - - 4.0
text_whole_sentences - - - - 4 - - 4.0
time_short_cam_found 4 3 3 3 - 7 6 4.0
cut_box_fits_the_picture 4 3 3 2 - 5 5 3.8
files_colour_carried 4 3 2 2 - 7 6 3.8
files_intro_proposed 5 3 2 2 - 6 5 3.8
files_mute_clip_intro 4 3 2 2 - 6 6 3.8
run_ffmpeg_not_fetched 4 3 3 1 - 5 6 3.8
table_notes_in_one_row 4 2 4 2 - 5 5 3.8
text_numbers_fit_reader 4 3 3 2 - 6 5 3.8
text_shown_catalogued 4 3 3 3 - 5 5 3.8
voice_answer_kept 4 3 4 3 - 4 5 3.8
window_choices_refit 3 3 4 3 - 5 6 3.8
window_sound_fault_named 4 2 4 2 - 5 5 3.8
files_by_file_holds 4 2 3 1 - 5 5 3.5
project_leaves_others 4 2 3 1 - 6 5 3.5
sound_bleed_reported 3 2 3 1 - 6 6 3.5
sound_check_reads_once 3 2 3 1 - 6 6 3.5
sound_clipping_counted 3 2 3 2 - 6 7 3.5
time_track_starts_late 2 2 4 2 - 6 7 3.5
files_twin_cameras_named 4 3 2 1 - 4 5 3.2
sound_all_blocks_count 4 2 2 1 - 6 5 3.2
source_numpy_comes_last 4 3 2 1 - 4 4 3.2
time_unheard_file_named 3 2 3 2 - 5 5 3.2
window_setup_kept_apart 3 2 3 1 - 5 5 3.2
window_size_as_run 3 2 3 2 - 5 6 3.2
window_start_runs 4 2 3 2 - 4 5 3.2
cut_player_speeds_up 3 3 2 2 - 4 5 3.0
files_foreign_untouched 3 2 2 1 - 6 5 3.0
files_hdr_complete 3 2 2 2 - 6 5 3.0
files_old_file_refused - - - - 3 - - 3.0
run_bar_tracks_work - - - - 3 - - 3.0
run_three_ways_agree 3 3 2 1 - 4 4 3.0
source_sections_named - - - - 3 - - 3.0
time_axis_keys_agree 3 2 2 1 - 5 5 3.0
time_which_way_is_said - - - - 3 - - 3.0
voice_mhm_is_speech 3 2 3 2 - 4 5 3.0
window_clock_sound_said 3 2 3 1 - 4 4 3.0
window_no_full_screen 4 2 2 1 - 4 4 3.0
window_picture_returns 3 1 2 2 - 5 5 3.0
cut_note_says_who_speaks 3 2 2 1 - 4 4 2.8
run_dry_run_not_stopped 3 1 2 2 - 4 4 2.8
run_metrics_add_up 3 2 2 1 - 4 4 2.8
sound_join_order 3 2 2 1 - 4 4 2.8
text_units_translated 3 2 2 1 - 4 5 2.8
time_bext_at_own_rate 3 2 2 1 - 4 4 2.8
time_measured_place_wins 3 2 2 1 - 5 4 2.8
voice_split_names_fault 3 2 3 2 - 3 3 2.8
window_hears_while_split 2 2 2 1 - 5 5 2.8
window_key_off_line 2 2 2 1 - 6 5 2.8
window_not_started_said 3 2 3 1 - 3 3 2.8
window_note_names_way 3 2 2 2 - 5 4 2.8
window_sound_sync_fixed 3 2 2 2 - 5 4 2.8
window_voice_audio_heard 3 2 2 2 - 4 4 2.8
auphonic_key_by_pipe 3 2 2 1 - 3 3 2.5
auphonic_key_kept - - - - - 2 3 2.5
auphonic_unsaved_said 3 1 2 1 - 4 4 2.5
cut_note_moves_no_shot 3 2 2 2 - 3 3 2.5
files_cut_without_keys 3 1 2 1 - 4 4 2.5
files_order_kept 3 2 1 1 - 4 4 2.5
run_ffmpeg_offered 3 2 2 1 - 3 3 2.5
run_odd_clock_named 2 2 2 2 - 4 5 2.5
run_shortcut_laid_once 2 2 2 2 - 4 4 2.5
run_update_says_it_landed 3 2 2 1 - 4 3 2.5
sound_block_gap_said 2 2 2 1 - 4 4 2.5
table_one_entry_greyed 3 2 2 2 - 3 3 2.5
voice_counts_grouped 3 2 2 1 - 3 3 2.5
voice_names_when_sure 3 1 2 1 - 4 4 2.5
voice_words_intact 2 2 - - - 3 3 2.5
window_amounts_grouped 3 2 2 1 - 4 3 2.5
window_foot_on_one_line 3 2 2 1 - 4 3 2.5
window_grey_opens_again 3 2 2 1 - 4 3 2.5
window_run_handover_kept 3 2 2 1 - 3 3 2.5
window_speakers_as_run 3 2 2 1 - 3 3 2.5
auphonic_key_out_of_view 2 2 1 1 - 4 4 2.2
auphonic_run_delivers 3 2 1 1 - 3 3 2.2
cut_no_wide_silences 2 2 2 0 - 3 3 2.2
cut_two_stay_two 2 2 2 1 - 3 4 2.2
files_split_found_again 3 2 1 0 - 3 3 2.2
project_audio_counted 2 2 1 1 - 5 4 2.2
project_handover_built 3 1 2 0 - 3 4 2.2
project_same_offset 3 1 2 1 - 3 3 2.2
run_project_type_reaches 3 1 2 1 - 5 3 2.2
run_space_has_margin 2 2 1 1 - 4 5 2.2
table_recording_shown 2 2 2 2 - 3 4 2.2
time_all_ways_agree 2 2 1 1 - 4 4 2.2
time_clock_track_first 2 2 1 1 - 4 4 2.2
voice_language_arrives 3 2 1 1 - 3 3 2.2
voice_raw_times_kept 2 2 2 1 - 3 4 2.2
voice_split_mends_itself 2 1 2 2 - 3 3 2.2
voice_turns_found 2 1 2 1 - 4 5 2.2
window_note_names_kind 3 2 1 0 - 3 3 2.2
window_note_reason_true 3 1 2 1 - 4 3 2.2
window_symbol_from_file 2 2 2 1 - 3 4 2.2
auphonic_preset_fits - - - - 2 - - 2.0
auphonic_stays_quiet - - - - 2 - - 2.0
cut_amounts_grouped - - - - 2 - - 2.0
cut_answer_brought_early - - - - 2 - - 2.0
cut_list_rebuilt 2 2 1 1 - 3 3 2.0
cut_rules_hold - - - - 2 - - 2.0
cut_short_edges_kept - - - - 2 - - 2.0
cut_wide_not_on_speech - - - - 2 - - 2.0
cut_window_cut_as_whole - - - - 2 - - 2.0
files_blocks_join_exact 2 2 1 1 - 3 3 2.0
files_left_out_named 3 1 1 0 - 3 3 2.0
files_line_counts_misfit 3 1 1 1 - 4 3 2.0
files_project_offered 2 2 1 1 - 3 3 2.0
project_every_offset 2 2 1 0 - 3 3 2.0
project_output_says_hdr - - - - 2 - - 2.0
project_real_frame - - - - 2 - - 2.0
project_two_stay_two 2 2 1 1 - 3 3 2.0
project_two_timelines_go - - - - 2 - - 2.0
run_bar_never_falls - - - - 2 - - 2.0
run_command_built - - - - 2 - - 2.0
run_no_upload_no_hint - - - - 2 - - 2.0
run_rate_way_said_right 2 2 1 0 - 3 3 2.0
run_starter_arch_fits 2 1 2 1 - 3 3 2.0
run_way_back_offered 3 1 1 1 - 4 3 2.0
sound_camera_counts 2 2 1 0 - 3 3 2.0
sound_loudest_block - - - - 2 - - 2.0
sound_silent_no_pair - - - - 2 - - 2.0
source_names_stay_fresh - - - - 2 - - 2.0
source_piece_list_holds - - - - 2 - - 2.0
table_names_reach_camera - - - - 2 - - 2.0
table_no_place_not_wide 2 1 2 1 - 3 3 2.0
table_sync_keeps_stem 3 1 1 1 - 3 4 2.0
text_lists_match - - - - 2 - - 2.0
text_tests_listed - - - - 2 - - 2.0
time_clock_from_any_file 3 1 1 0 - 3 3 2.0
time_clock_read_at_rate 2 1 1 1 - 5 4 2.0
time_length_is_in_to_out - - - - 2 - - 2.0
time_length_names_change - - - - 2 - - 2.0
time_zero_at_in_point - - - - 2 - - 2.0
voice_both_ways_agree 2 2 1 0 - 3 3 2.0
voice_failed_read_named 2 2 1 0 - 3 3 2.0
voice_questions_rank - - - - 2 - - 2.0
voice_source_travels 2 2 1 1 - 3 3 2.0
voice_tracks_read_once 2 1 2 1 - 3 3 2.0
window_cut_colours 2 1 2 1 - 3 3 2.0
window_notes_break_up 2 1 2 1 - 3 4 2.0
cut_player_right_file 2 1 1 1 - 3 3 1.8
cut_rebuild_keeps_all 2 1 1 0 - 3 3 1.8
files_curve_kept_once 2 1 1 1 - 4 3 1.8
files_joined_by_hand 2 1 1 1 - 3 3 1.8
project_close_forgets 2 1 1 1 - 3 3 1.8
project_mix_by_name 2 2 1 1 - 2 2 1.8
project_render_kept 2 1 2 1 - 2 3 1.8
run_dry_reports_voices 2 1 1 1 - 3 3 1.8
run_prework_listed 2 1 1 1 - 4 3 1.8
text_release_ready 2 1 1 0 - 3 3 1.8
voice_mic_reaches_cut 2 1 1 1 - 3 3 1.8
window_zoom_stays_in 2 1 1 1 - 3 3 1.8
files_named_by_folder 2 2 1 0 - - - 1.5
time_block_holds_on 1 1 1 0 - 2 2 1.2
auphonic_may_be_skipped - - - - 1 - - 1.0
auphonic_mono_not_stereo - - - - 1 - - 1.0
auphonic_preset_checked - - - - 1 - - 1.0
auphonic_speech_read - - - - 1 - - 1.0
cut_all_shots_land - - - - 1 - - 1.0
cut_both_are_shown - - - - 1 - - 1.0
cut_colour_per_camera - - - - 1 - - 1.0
cut_edl_says_drop_frame - - - - 1 - - 1.0
cut_jingle_over_start - - - - 1 - - 1.0
cut_one_camera_marks - - - - 1 - - 1.0
cut_opening_wide_holds - - - - 1 - - 1.0
cut_own_rate_counted - - - - 1 - - 1.0
cut_player_offset_used - - - - 1 - - 1.0
cut_right_camera - - - - 1 - - 1.0
cut_speech_time_fits - - - - 1 - - 1.0
cut_together_read_order - - - - 1 - - 1.0
cut_wide_colour_apart - - - - 1 - - 1.0
files_named_as_written - - - - 1 - - 1.0
project_amounts_grouped - - - - 1 - - 1.0
project_cameras_land - - - - 1 - - 1.0
project_each_track_set - - - - 1 - - 1.0
project_grades_stay_off - - - - 1 - - 1.0
project_hdr_follows - - - - 1 - - 1.0
project_markers_placed - - - - 1 - - 1.0
project_refusal_heeded - - - - 1 - - 1.0
project_render_queued - - - - 1 - - 1.0
project_rerun_updates - - - - 1 - - 1.0
project_sync_multicam - - - - 1 - - 1.0
project_tag_reason_fits - - - - 1 - - 1.0
project_top_rate_wins - - - - 1 - - 1.0
run_findings_reach_both - - - - 1 - - 1.0
sound_hush_reason - - - - 1 - - 1.0
sound_mix_says_the_name - - - - 1 - - 1.0
source_no_stale_places - - - - 1 - - 1.0
source_platform_declared - - - - 1 - - 1.0
source_skills_resolve - - - - 1 - - 1.0
table_camera_proposed - - - - 1 - - 1.0
time_bad_point_dropped - - - - 1 - - 1.0
time_drop_label_kept - - - - 1 - - 1.0
time_fit_reports - - - - 1 - - 1.0
time_over_midnight - - - - 1 - - 1.0
time_point_pulled_back - - - - 1 - - 1.0
time_window_is_shared - - - - 1 - - 1.0
voice_amounts_grouped - - - - 1 - - 1.0
voice_every_word_placed - - - - 1 - - 1.0
voice_name_is_one_person - - - - 1 - - 1.0
voice_note_translated - - - - 1 - - 1.0
voice_reason_reaches_log - - - - 1 - - 1.0
source_floor_needs_main - - - - 0 - - 0.0
source_needs_lists_agree - - - - 0 - - 0.0
source_pictures_seen - - - - 0 - - 0.0
text_index_targets_exist - - - - 0 - - 0.0
text_skills_listed - - - - 0 - - 0.0
```

</details>

## 3.0.0b26 -- 2026-09-26

Run 36271092456 on `runde-b26` at `4ccd052`: suite #783 on runde-b26 -- separation off.

The slowest job, and what a push waits for: **Windows py3.14, 949 s**.
The suite summed over the trimmed means: **2876 s** for 384 tests.

| job | wall s | tests summed s |
|---|---:|---:|
| Linux py3.10 | 545 | 2310 |
| Linux py3.14 | 506 | 2110 |
| macOS py3.10 | 811 | 2560 |
| macOS py3.14 | 748 | 2269 |
| Neutral py3.14 | 88 | 273 |
| Windows py3.10 | 829 | 3137 |
| Windows py3.14 | 949 | 3693 |

The 15 longest by trimmed mean:

| test | Linux py3.10 | Linux py3.14 | macOS py3.10 | macOS py3.14 | Neutral py3.14 | Windows py3.10 | Windows py3.14 | trimmed | change |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| `source_material_stays` | 51 | 52 | 49 | 43 | - | 57 | 82 | 52.2 | +4.8 |
| `time_phase_only_mixed` | 52 | 49 | 48 | 36 | - | 54 | 70 | 50.8 | +5.8 |
| `run_new_name_checked` | 50 | 43 | 48 | 46 | - | 54 | 72 | 49.5 | +9.7 |
| `run_switch_changes_it` | 39 | 38 | 52 | 41 | - | 66 | 74 | 49.5 | +0.3 |
| `run_promise_is_written` | 39 | 36 | 43 | 35 | - | 74 | 81 | 48.0 | +5.0 |
| `window_speaker_cell_fits` | 46 | 44 | 47 | 44 | - | 54 | 70 | 47.8 | +1.8 |
| `run_choice_kept` | 45 | 36 | 52 | 24 | - | 41 | 54 | 43.5 | +13.3 **grown** |
| `time_guess_refused` | 33 | 28 | 41 | 23 | - | 46 | 61 | 37.0 | +15.0 **grown** |
| `time_tracks_alone` | 31 | 28 | 41 | 31 | - | 41 | 50 | 36.0 | +14.8 **grown** |
| `run_done_tracks_used` | 28 | 26 | 24 | 32 | - | 50 | 64 | 34.0 | +12.8 **grown** |
| `table_seats_reach_run` | 28 | 25 | 26 | 27 | - | 49 | 69 | 32.5 | new |
| `cut_player_prepared_used` | 29 | 29 | 25 | 23 | - | 40 | 52 | 30.8 | +3.8 |
| `project_errors_reach_run` | 27 | 27 | 21 | 22 | - | 44 | 50 | 30.0 | +8.2 |
| `sound_camera_own_used` | 27 | 25 | 25 | 17 | - | 40 | 48 | 29.2 | +2.8 |
| `sound_tracks_written` | 29 | 25 | 24 | 15 | - | 38 | 52 | 29.0 | +2.8 |

Grown by more than 20 % and at least 10 s: `run_done_tracks_used` 21.2 -> 34.0 s, `time_guess_refused` 22.0 -> 37.0 s, `run_choice_kept` 30.2 -> 43.5 s, `time_tracks_alone` 21.2 -> 36.0 s.

<details>
<summary>Every test, 384</summary>

```text
test Linux_py3.10 Linux_py3.14 macOS_py3.10 macOS_py3.14 Neutral_py3.14 Windows_py3.10 Windows_py3.14 trimmed
source_material_stays 51 52 49 43 - 57 82 52.2
time_phase_only_mixed 52 49 48 36 - 54 70 50.8
run_new_name_checked 50 43 48 46 - 54 72 49.5
run_switch_changes_it 39 38 52 41 - 66 74 49.5
run_promise_is_written 39 36 43 35 - 74 81 48.0
window_speaker_cell_fits 46 44 47 44 - 54 70 47.8
run_choice_kept 45 36 52 24 - 41 54 43.5
time_guess_refused 33 28 41 23 - 46 61 37.0
time_tracks_alone 31 28 41 31 - 41 50 36.0
run_done_tracks_used 28 26 24 32 - 50 64 34.0
table_seats_reach_run 28 25 26 27 - 49 69 32.5
cut_player_prepared_used 29 29 25 23 - 40 52 30.8
project_errors_reach_run 27 27 21 22 - 44 50 30.0
sound_camera_own_used 27 25 25 17 - 40 48 29.2
sound_tracks_written 29 25 24 15 - 38 52 29.0
run_stop_names_why 30 24 28 16 - 30 37 28.0
run_simple_path_agrees 24 22 19 23 - 42 48 27.8
run_dry_leaves_out 26 24 20 23 - 36 45 27.2
voice_both_splits_stand 22 21 41 36 - 25 26 27.2
run_log_within_reach 25 22 33 25 - 27 31 27.0
time_one_track_aligned 25 23 27 22 - 33 40 27.0
run_mute_camera_placed 18 16 23 20 - 42 43 25.8
time_sound_stays_put 14 14 27 21 - 39 35 24.2
time_weak_as_run 14 16 28 23 - 30 38 24.2
window_all_come_up 19 16 29 20 - 28 36 24.0
table_lock_says_why 21 19 26 30 - - - 23.5
run_window_run_agrees 20 19 19 16 - 33 46 22.8
table_pair_seats_apart 21 21 24 24 - 23 23 22.8
project_run_comes_back 20 20 32 25 - 22 23 22.5
run_no_drift_noughts 19 18 18 18 - 35 43 22.5
cut_stored_voices_used 20 18 17 15 - 30 34 21.2
project_run_lands_whole 19 18 16 15 - 31 37 21.0
files_only_window_kept 17 16 22 16 - 26 34 20.2
cut_player_jump_lands 19 19 20 19 - 20 21 19.5
table_row_per_voice 19 22 17 14 - 30 20 19.5
cut_own_mic_own_camera 10 10 18 21 - 28 35 19.2
table_tick_keeps_camera 15 16 23 23 - 17 21 19.2
files_project_first 11 12 18 25 - 21 22 18.2
time_tracks_sit_together 11 11 24 17 - 22 23 18.2
source_no_loose_ends - - - - 18 - - 18.0
window_answers_arrive 17 17 41 - - 18 20 18.0
window_captions_fit 10 10 18 19 - 22 23 17.2
window_restart_carries 10 10 19 14 - 24 25 16.8
source_live_asks_first 17 16 18 15 - - - 16.5
project_mixed_run_lands 14 13 15 10 - 23 27 16.2
source_line_loads_no_qt 16 15 13 11 - 20 34 16.0
window_marks_take_spot 12 13 15 13 - 25 21 15.5
window_tc_point_named 15 12 18 23 - 14 14 15.2
table_names_one_order 10 10 16 12 - 31 22 15.0
table_blocks_judged 13 13 18 22 - 13 15 14.8
window_stages_named 12 12 14 14 - 19 23 14.8
files_block_stays_apart 6 4 20 18 - 14 22 14.5
run_sync_only_no_cut 11 11 15 14 - 18 21 14.5
time_drift_taken_out 14 12 11 13 - 34 18 14.2
source_no_real_names - - - - 14 - - 14.0
window_offers_restart 13 12 14 17 - 14 15 14.0
cut_offer_needs_two 10 9 14 19 - 14 16 13.5
table_pair_named_alike 10 10 14 17 - 14 16 13.5
time_colour_own_camera 12 12 11 9 - 19 29 13.5
window_idle_bar_hidden 10 8 15 16 - 13 16 13.5
cut_voice_on_its_camera 8 10 13 13 - 17 23 13.2
run_clock_place_travels 11 10 12 12 - 21 18 13.2
text_languages_covered 12 10 20 12 - 11 18 13.2
text_run_all_german 12 11 10 8 - 20 27 13.2
project_file_beats_last 11 9 13 14 - 15 14 13.0
time_scatter_not_placed 3 10 9 19 - 15 18 13.0
voice_close_mics_mixed 11 11 15 13 - 13 19 13.0
window_exit_keeps_all 16 11 17 12 - 12 12 13.0
project_settings_return 12 12 12 14 - 13 15 12.8
window_play_follows_tab 11 10 12 14 - 14 17 12.8
text_german_arrives 17 9 16 8 - 11 14 12.5
window_sheets_fit 11 9 18 14 - - - 12.5
cut_player_in_sync 10 9 15 14 - 13 12 12.2
time_offset_found 10 10 14 9 - 17 15 12.2
project_ticks_come_back 12 11 11 13 - 12 13 12.0
source_limits_hold - - - - 12 - - 12.0
text_only_texts_change - - - - 12 - - 12.0
time_reference_silent 9 8 13 9 - 16 25 11.8
text_lang_settled_first 11 8 11 13 - 11 14 11.5
run_outside_seen 10 9 10 11 - 14 16 11.2
window_grey_says_why 11 10 9 12 - 12 12 11.2
source_resolve_door_shut - - - - 11 - - 11.0
window_menu_greys_along 10 10 10 11 - 13 17 11.0
window_stands_still 10 8 10 12 - 12 13 11.0
table_row_per_channel 8 7 14 12 - 17 9 10.8
sound_mix_hits_target 9 7 9 10 - 14 15 10.5
table_audio_asked_for 8 8 13 10 - 11 13 10.5
window_dark_follows 10 11 13 11 - 8 10 10.5
files_added_alike 10 9 9 7 - 13 18 10.2
run_own_sound_with_cam 7 7 7 7 - 26 20 10.2
source_reds_carry_value - - - - 10 - - 10.0
run_ffmpeg_new_enough 11 9 6 9 - 10 13 9.8
run_names_as_window 8 7 9 10 - 12 15 9.8
sound_speakers_matched 8 8 9 7 - 13 17 9.5
table_back_to_one_name 8 8 11 11 - 9 10 9.5
window_reads_as_chosen 9 8 10 11 - 9 10 9.5
files_colour_fair 7 6 11 7 - 12 14 9.2
run_stays_local 8 7 7 9 - 16 13 9.2
window_prework_box_goes 7 6 12 9 - 10 11 9.2
time_clock_beats_guess 6 5 9 10 - 11 12 9.0
run_one_shots_return_0 10 8 6 8 - 9 11 8.8
window_marks_come_back 9 8 6 10 - 8 10 8.8
time_lost_end_named 8 8 7 5 - 11 19 8.5
window_blocks_placed 9 9 10 8 - 7 8 8.5
window_view_reaches_tabs 8 8 8 9 - 9 10 8.5
table_stereo_splits 8 7 15 10 - 7 8 8.2
window_axis_asks_again 8 7 7 8 - 10 10 8.2
run_only_newer_offered 8 7 10 5 - 7 10 8.0
sound_stereo_kept 5 5 7 10 - 10 14 8.0
source_names_said_once - - - - 8 - - 8.0
text_no_german_left - - - - 8 - - 8.0
window_project_type_set 7 6 8 10 - 8 9 8.0
sound_both_sides_alike 6 5 8 8 - 9 12 7.8
run_overwrite_is_said 8 5 6 7 - 8 10 7.2
run_unreadable_named 6 6 7 5 - 10 11 7.2
window_handover_follows 6 5 9 7 - 8 8 7.2
window_handover_found 6 5 9 7 - 7 10 7.2
run_switch_has_effect 8 7 6 5 - 7 9 7.0
sound_camera_judged_too 4 4 11 5 - 8 12 7.0
source_checks_proved - - - - 7 - - 7.0
voice_bleed_gone_first 6 6 13 10 - 5 6 7.0
files_sync_one_recording 5 5 7 7 - 8 10 6.8
project_keeps_answers 7 6 7 5 - 7 9 6.8
sound_peaks_limited 6 6 4 6 - 9 12 6.8
time_preview_fit_as_run 5 6 5 6 - 10 11 6.8
table_sync_stem_shown 6 6 7 6 - 7 8 6.5
auphonic_none_chosen 5 5 7 6 - 7 7 6.2
files_probed_once 4 4 7 7 - 7 8 6.2
run_install_is_watched 6 6 7 7 - 6 6 6.2
sound_delay_decides 5 5 5 6 - 9 10 6.2
source_imported_is_whole 6 5 6 5 - 8 10 6.2
files_old_file_refused - - - - 6 - - 6.0
sound_one_pass_agrees 6 6 6 5 - - - 6.0
source_test_names_swept - - - - 6 - - 6.0
time_second_try_places 5 5 6 7 - 6 9 6.0
window_pair_said_apart 6 4 7 5 - 6 7 6.0
table_sync_none_derived 5 5 7 5 - 6 9 5.8
window_title_follows 5 4 6 6 - 6 7 5.8
run_name_twice_refused 6 5 5 4 - 6 8 5.5
sound_any_count_judged 4 3 7 4 - 7 10 5.5
source_resolve_recalled 6 4 6 5 - - - 5.5
table_typed_name_stays 4 4 7 5 - 6 7 5.5
time_thin_block_refused 4 3 5 7 - 6 8 5.5
time_weak_at_its_clock 5 4 4 4 - 9 9 5.5
window_overwrite_asked 6 5 5 6 - 5 7 5.5
run_assign_file_gone 5 5 5 5 - 6 7 5.2
run_ffmpeg_not_fetched 6 5 5 4 - 5 6 5.2
run_threads_keep_order 5 4 5 5 - 6 6 5.2
window_point_named 6 5 4 3 - 6 6 5.2
files_block_out_and_back 5 4 4 4 - 7 7 5.0
source_frozen_name_holds - - - - 5 - - 5.0
time_axis_measured 3 3 6 4 - 7 8 5.0
time_camera_drift_clear - - - - 5 - - 5.0
time_which_way_is_said - - - - 5 - - 5.0
auphonic_key_answer_fits 5 4 4 4 - 6 6 4.8
files_by_file_holds 5 5 3 4 - 5 6 4.8
project_leaves_others 5 4 4 4 - 6 6 4.8
run_long_names_keep_end 5 3 4 3 - 7 8 4.8
sound_each_gets_a_track 4 3 3 5 - 7 9 4.8
text_lang_acted_on 5 4 5 4 - 5 7 4.8
text_shown_catalogued 4 4 3 5 - 5 6 4.5
time_track_starts_late 4 3 4 4 - 6 8 4.5
voice_answer_kept 5 4 4 3 - 5 6 4.5
files_atom_travels 4 4 4 3 - 5 6 4.2
files_clock_links_blocks 3 2 3 3 - 8 9 4.2
files_intro_proposed 4 4 3 4 - 5 7 4.2
run_which_script 5 4 3 2 - 5 7 4.2
sound_join_any_rate 4 3 4 3 - 6 6 4.2
time_unheard_file_named 4 4 3 3 - 6 6 4.2
window_tracks_seen_anew 5 4 4 4 - 4 6 4.2
window_words_caught_up 3 5 3 3 - 6 12 4.2
files_colour_carried 3 3 4 2 - 6 6 4.0
sound_channels_split 3 3 3 4 - 6 8 4.0
text_numbers_fit_reader 4 3 2 4 - 5 5 4.0
text_whole_sentences - - - - 4 - - 4.0
window_choices_refit 4 4 3 4 - 4 5 4.0
window_size_as_run 4 3 4 4 - 4 5 4.0
window_sound_fault_named 4 4 4 4 - 4 5 4.0
cut_box_fits_the_picture 4 3 2 4 - 5 4 3.8
cut_preview_is_the_run 2 2 3 3 - 7 8 3.8
files_data_track_kept 3 3 3 2 - 6 8 3.8
files_hdr_complete 3 3 3 3 - 6 6 3.8
files_lengths_summed 3 3 4 3 - 5 9 3.8
files_mute_clip_intro 4 3 3 2 - 5 6 3.8
files_twin_cameras_named 4 3 2 3 - 5 5 3.8
sound_clipping_counted 4 3 3 2 - 5 6 3.8
table_notes_in_one_row 3 3 3 5 - 8 4 3.8
window_no_full_screen 4 3 2 3 - 5 5 3.8
files_foreign_untouched 3 3 3 3 - 5 7 3.5
files_set_aside_skipped 3 3 2 3 - 5 5 3.5
time_measured_place_wins 4 2 3 3 - 4 5 3.5
time_short_cam_found 3 4 2 3 - 4 6 3.5
voice_names_when_sure 3 4 3 3 - 4 5 3.5
window_hears_while_split 4 3 3 3 - 4 5 3.5
window_start_runs 3 2 4 3 - 4 4 3.5
window_stop_always 3 4 3 3 - 4 8 3.5
auphonic_unsaved_said 3 3 3 3 - 4 4 3.2
run_metrics_add_up 3 3 2 2 - 5 5 3.2
run_odd_clock_named 3 2 2 2 - 6 6 3.2
sound_all_blocks_count 3 3 3 3 - 4 5 3.2
sound_bleed_reported 4 3 2 2 - 4 5 3.2
sound_check_reads_once 3 2 3 2 - 5 6 3.2
text_units_translated 3 2 2 3 - 5 5 3.2
voice_mhm_is_speech 3 3 2 2 - 5 5 3.2
window_clock_sound_said 3 3 2 3 - 5 4 3.2
window_groups_make_room 3 3 3 2 - 4 7 3.2
window_not_started_said 3 3 3 3 - 4 4 3.2
window_picture_returns 2 2 3 5 - 3 5 3.2
window_setup_kept_apart 3 3 4 3 - 3 4 3.2
auphonic_key_by_pipe 2 2 4 3 - 3 4 3.0
auphonic_key_kept - - - - - 3 3 3.0
cut_note_moves_no_shot 3 2 3 3 - 3 3 3.0
cut_player_speeds_up 4 2 2 3 - 3 4 3.0
files_curve_kept_once 3 3 3 1 - 3 4 3.0
run_bar_never_falls - - - - 3 - - 3.0
run_bar_tracks_work - - - - 3 - - 3.0
run_command_built - - - - 3 - - 3.0
run_quiet_judged 3 2 3 3 - 3 3 3.0
run_three_ways_agree 3 3 3 3 - 3 4 3.0
run_update_says_it_landed 3 3 3 2 - 4 3 3.0
sound_block_gap_said 3 3 3 3 - 3 4 3.0
source_names_stay_fresh - - - - 3 - - 3.0
source_numpy_comes_last 3 2 3 2 - 4 4 3.0
source_sections_named - - - - 3 - - 3.0
text_tests_listed - - - - 3 - - 3.0
time_axis_keys_agree 3 3 2 2 - 4 5 3.0
time_bext_at_own_rate 3 3 2 2 - 5 4 3.0
time_clock_read_at_rate 3 2 2 3 - 4 4 3.0
time_short_cam_as_run 3 3 2 1 - 4 5 3.0
voice_both_ways_agree 3 3 3 1 - 3 3 3.0
voice_counts_grouped 3 3 3 2 - 3 4 3.0
voice_cue_fits_two_lines - - - - 3 - - 3.0
voice_raw_times_kept 3 3 2 2 - 4 4 3.0
voice_words_intact 3 2 - - - 3 3 3.0
window_foot_on_one_line 3 2 3 2 - 4 4 3.0
window_key_off_line 3 3 2 3 - 3 5 3.0
window_voice_audio_heard 3 2 2 3 - 6 4 3.0
auphonic_key_typed 3 3 2 2 - 3 4 2.8
auphonic_run_delivers 2 2 3 3 - 3 4 2.8
auphonic_speech_read 3 2 2 3 - 3 4 2.8
cut_note_says_who_speaks 2 2 3 3 - 3 4 2.8
cut_player_offset_used 3 3 2 1 - 3 4 2.8
cut_two_stay_two 3 2 3 2 - 3 4 2.8
files_joined_by_hand 3 2 3 2 - 3 4 2.8
files_line_counts_misfit 2 2 4 2 - 3 4 2.8
project_audio_counted 2 3 2 2 - 4 4 2.8
project_refusal_heeded 3 3 2 1 - 3 3 2.8
run_shortcut_laid_once 3 2 2 1 - 4 4 2.8
sound_join_order 3 2 3 1 - 3 4 2.8
table_one_entry_greyed 2 2 3 3 - 4 3 2.8
time_all_ways_agree 3 3 2 1 - 3 5 2.8
voice_language_arrives 3 3 2 1 - 3 3 2.8
window_amounts_grouped 3 2 3 2 - 3 4 2.8
window_block_misfit_kept 3 3 2 2 - 3 5 2.8
window_grey_opens_again 3 3 2 2 - 3 3 2.8
window_speakers_as_run 3 3 2 2 - 3 3 2.8
auphonic_key_out_of_view 3 2 2 2 - 3 3 2.5
auphonic_key_reg_shut 2 2 3 1 - 3 4 2.5
files_blocks_join_exact 2 3 2 1 - 3 3 2.5
files_cut_without_keys 3 2 2 2 - 3 3 2.5
files_left_out_named 2 2 3 2 - 3 3 2.5
project_close_forgets 3 2 2 1 - 3 3 2.5
project_every_offset 2 2 2 1 - 4 4 2.5
run_ffmpeg_offered 3 1 2 2 - 3 3 2.5
run_project_type_reaches 3 2 2 1 - 3 4 2.5
run_space_has_margin 2 2 2 2 - 4 4 2.5
sound_far_block_left_out 3 2 1 2 - 3 4 2.5
table_no_place_not_wide 3 2 2 3 - 2 4 2.5
table_recording_shown 3 2 2 2 - 3 3 2.5
table_sync_keeps_stem 2 2 2 2 - 4 4 2.5
time_clock_track_first 3 2 2 2 - 3 4 2.5
voice_split_mends_itself 3 2 2 2 - 3 3 2.5
voice_split_names_fault 3 2 2 2 - 4 3 2.5
voice_turns_found 3 2 2 2 - 3 5 2.5
window_note_names_kind 3 2 1 2 - 3 4 2.5
window_note_names_way 2 3 2 2 - 3 4 2.5
window_note_reason_true 2 2 2 2 - 4 4 2.5
window_run_handover_kept 3 2 2 1 - 3 3 2.5
window_symbol_from_file 2 3 2 1 - 4 3 2.5
cut_list_rebuilt 3 1 2 1 - 3 3 2.2
cut_no_wide_silences 3 1 2 1 - 3 3 2.2
cut_player_right_file 2 2 1 2 - 3 3 2.2
cut_rebuild_keeps_all 2 2 2 2 - 3 3 2.2
files_order_kept 2 2 2 2 - 4 3 2.2
files_project_offered 2 2 2 2 - 3 4 2.2
files_split_found_again 2 2 2 1 - 3 3 2.2
project_same_offset 2 2 2 2 - 3 4 2.2
project_two_stay_two 2 2 2 2 - 3 4 2.2
run_dry_reports_voices 3 2 2 2 - 2 3 2.2
run_dry_run_not_stopped 2 1 2 2 - 3 4 2.2
run_prework_listed 3 1 2 1 - 3 4 2.2
run_way_back_offered 2 2 2 2 - 4 3 2.2
sound_camera_counts 2 2 2 1 - 3 3 2.2
time_clock_from_any_file 2 2 2 2 - 3 3 2.2
voice_mic_reaches_cut 2 2 1 2 - 3 4 2.2
voice_source_travels 2 2 2 1 - 3 3 2.2
window_cut_colours 2 2 2 2 - 3 4 2.2
window_notes_break_up 2 2 2 2 - 3 4 2.2
window_sound_sync_fixed 2 2 1 2 - 3 4 2.2
window_zoom_stays_in 2 2 2 2 - 3 3 2.2
auphonic_key_in_keyring 3 2 2 2 - - - 2.0
auphonic_may_be_skipped - - - - 2 - - 2.0
auphonic_mono_not_stereo - - - - 2 - - 2.0
cut_all_shots_land - - - - 2 - - 2.0
cut_amounts_grouped - - - - 2 - - 2.0
cut_both_are_shown - - - - 2 - - 2.0
cut_colour_per_camera - - - - 2 - - 2.0
cut_edges_said_as_cut - - - - 2 - - 2.0
cut_edl_says_drop_frame - - - - 2 - - 2.0
cut_jingle_over_start - - - - 2 - - 2.0
cut_one_camera_marks - - - - 2 - - 2.0
cut_opening_wide_holds - - - - 2 - - 2.0
cut_own_rate_counted - - - - 2 - - 2.0
cut_right_camera - - - - 2 - - 2.0
cut_rules_hold - - - - 2 - - 2.0
cut_short_edges_kept - - - - 2 - - 2.0
cut_speech_time_fits - - - - 2 - - 2.0
cut_together_read_order - - - - 2 - - 2.0
cut_wide_colour_apart - - - - 2 - - 2.0
cut_wide_not_on_speech - - - - 2 - - 2.0
files_named_as_written - - - - 2 - - 2.0
project_amounts_grouped - - - - 2 - - 2.0
project_cameras_land - - - - 2 - - 2.0
project_each_track_set - - - - 2 - - 2.0
project_grades_stay_off - - - - 2 - - 2.0
project_handover_built 2 1 1 2 - 3 4 2.0
project_hdr_follows - - - - 2 - - 2.0
project_markers_placed - - - - 2 - - 2.0
project_output_says_hdr - - - - 2 - - 2.0
project_real_frame - - - - 2 - - 2.0
project_rerun_updates - - - - 2 - - 2.0
project_sync_multicam - - - - 2 - - 2.0
project_tag_reason_fits - - - - 2 - - 2.0
project_top_rate_wins - - - - 2 - - 2.0
run_findings_reach_both 1 2 3 1 - 2 3 2.0
run_rate_way_said_right 2 2 2 1 - 2 3 2.0
run_starter_arch_fits 2 2 2 2 - 2 3 2.0
sound_hush_reason - - - - 2 - - 2.0
sound_loudest_block - - - - 2 - - 2.0
sound_mix_says_the_name - - - - 2 - - 2.0
sound_silent_no_pair - - - - 2 - - 2.0
source_no_stale_places - - - - 2 - - 2.0
source_piece_list_holds - - - - 2 - - 2.0
source_platform_declared - - - - 2 - - 2.0
table_camera_proposed - - - - 2 - - 2.0
table_names_reach_camera 2 2 1 1 - 3 3 2.0
text_lists_match - - - - 2 - - 2.0
time_bad_point_dropped - - - - 2 - - 2.0
time_block_holds_on 2 2 2 2 - 2 3 2.0
time_drop_label_kept - - - - 2 - - 2.0
time_fit_reports - - - - 2 - - 2.0
time_length_names_change - - - - 2 - - 2.0
time_over_midnight - - - - 2 - - 2.0
time_point_pulled_back - - - - 2 - - 2.0
time_window_is_shared - - - - 2 - - 2.0
time_zero_at_in_point - - - - 2 - - 2.0
voice_amounts_grouped - - - - 2 - - 2.0
voice_every_word_placed - - - - 2 - - 2.0
voice_failed_read_named 2 2 2 1 - 2 3 2.0
voice_name_is_one_person - - - - 2 - - 2.0
voice_note_translated - - - - 2 - - 2.0
voice_questions_rank - - - - 2 - - 2.0
voice_reason_reaches_log - - - - 2 - - 2.0
voice_tracks_read_once 2 2 1 1 - 3 3 2.0
project_render_kept 2 1 2 1 - 2 3 1.8
files_named_by_folder 2 1 2 1 - - - 1.5
project_mix_by_name 1 1 3 1 - 2 2 1.5
auphonic_preset_checked - - - - 1 - - 1.0
auphonic_preset_fits - - - - 1 - - 1.0
auphonic_stays_quiet - - - - 1 - - 1.0
cut_answer_brought_early - - - - 1 - - 1.0
cut_window_cut_as_whole - - - - 1 - - 1.0
project_render_queued - - - - 1 - - 1.0
project_two_timelines_go - - - - 1 - - 1.0
run_no_upload_no_hint - - - - 1 - - 1.0
source_pictures_seen - - - - 1 - - 1.0
text_release_ready - - - - 1 - - 1.0
time_length_is_in_to_out - - - - 1 - - 1.0
text_release_has_program 0 0 1 0 - 1 11 0.5
source_floor_needs_main - - - - 0 - - 0.0
source_needs_lists_agree - - - - 0 - - 0.0
source_skills_resolve - - - - 0 - - 0.0
text_index_targets_exist - - - - 0 - - 0.0
text_skills_listed - - - - 0 - - 0.0
```

</details>
