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
