# -*- coding: utf-8 -*-
"""A Stop met inside a run's step ends the run, not only that step.

Each step below catches its own failures and goes on; Stop must pass
them. In order: the separation mix (real ffmpeg, no half mix left), the
auphonic.com downloads and format lookup, the preset check, a join's
loudness, a multitrack send's preset and production, a parallel step,
the bleed check and its cross-check, the cut's speaker reading.
"""
PLATFORM_BOUND = True
import os
import sys
# tests/, where the helpers and state/ lie; this file may stand in a
# folder under it, or in one under that.
HERE = os.path.dirname(os.path.abspath(__file__))
while not os.path.isfile(os.path.join(HERE, "the_program.py")) \
        and os.path.dirname(HERE) != HERE:
    HERE = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import shutil
import subprocess
import tempfile
import time
import types
import zipfile
import the_program

began = time.time()
done = 0
bad = []


def check(name, ok, extra=""):
    global done
    done += 1
    print("  %-58s %s %s" % (name, "ok" if ok else "FAIL", extra))
    if not ok:
        bad.append("%s [%s]" % (name, extra or "no numbers"))


vpm = the_program.load()
vpm.set_language("en")
WORK = tempfile.mkdtemp(prefix="vpm_passes_")
AT = "the step Stop was pressed in"


def outcome(call):
    """What *call* did: 'Stopped', 'returned ...' or 'raised ...'."""
    try:
        got = call()
    except vpm.Stopped:
        return "Stopped"
    except Exception as e:
        return "raised %s: %s" % (type(e).__name__, str(e)[:80])
    return "returned %r" % (got,)


def stopping(*a, **k):
    """A call Stop ends: what _curl_call and the ffmpeg step raise then."""
    raise vpm.Stopped(AT)


def tone(name):
    """One second of sound, written by ffmpeg; its path."""
    path = os.path.join(WORK, name)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i",
                    "sine=frequency=440:duration=1", "-ar", "48000", path],
                   check=True)
    return path


try:
    print("Separation mix, Stop asked while ffmpeg adds the tracks")
    A, B = tone("A.wav"), tone("B.wav")
    MIXES = os.path.join(WORK, "mixes")
    os.makedirs(MIXES)
    vpm.RUN_STOP["wanted"], vpm.RUN_STOP["at"] = True, AT
    try:
        got = outcome(lambda: vpm.speakers.speaker_mix_file(
            [A, B], ["passes"], folder=MIXES))
    finally:
        vpm.RUN_STOP["wanted"], vpm.RUN_STOP["at"] = False, ""
        # The step's bar ends its line only when nobody stopped it.
        print("")
    check("Stop in the separation mix ends the run, not only the mix",
          got == "Stopped", "the mix %s, wanted Stopped" % got)
    left = sorted(os.listdir(MIXES))
    check("no mix, whole or half, is left when Stop ends the mix",
          not left, "left in the mix folder: %s" % (left,))

    print("\nauphonic.com, Stop while a file comes down")
    au = vpm.auphonic
    real_curl = au._curl_call
    au._curl_call = stopping
    try:
        got = outcome(lambda: au.fetch_text_outputs(
            "key", [{"filename": "words.srt", "download_url": "u"}], WORK))
        check("Stop while a transcript comes down ends the run",
              got == "Stopped", "the fetch %s, wanted Stopped" % got)
        got = outcome(lambda: au.find_output_format("key", "wav"))
        check("Stop while the output formats are asked ends the run",
              got == "Stopped", "the lookup %s, wanted Stopped" % got)
        # The ZIP of the tracks comes down whole, empty; Stop meets the
        # extra output after it.
        au._curl_call = lambda key, argv, **k: (
            stopping() if argv[-1] == "extra"
            else zipfile.ZipFile(argv[1], "w").close())
        got = outcome(lambda: au.download_results(
            "key", {"output_files": [
                {"filename": "tracks.zip", "download_url": "zip"},
                {"filename": "chapters.txt", "download_url": "extra"}]},
            [], WORK, "base"))
        check("Stop while an extra output comes down ends the run",
              got == "Stopped", "the download %s, wanted Stopped" % got)
    finally:
        au._curl_call = real_curl

    print("\nThe preset, Stop while it is read")
    real_read = vpm.read_preset
    vpm.read_preset = stopping
    try:
        got = outcome(lambda: vpm.preflight.check_preset(
            "key", "uuid", "Preset", -16.0, True))
    finally:
        vpm.read_preset = real_read
    check("Stop while the preset is read ends the run, not the check",
          got == "Stopped", "the preset check %s, wanted Stopped" % got)

    print("\nA join without picture, Stop while the loudness is measured")
    tb = vpm.timebase
    real_loud = tb.normalise_loudness
    tb.normalise_loudness = stopping
    try:
        got = outcome(lambda: tb.join_only(
            types.SimpleNamespace(out=WORK, lufs=-16.0, auphonic_key=None,
                                  dry_run=False),
            [{"name": "Guest", "source": A, "blocks": [A]}], WORK))
    finally:
        tb.normalise_loudness = real_loud
    check("Stop while a join's loudness is measured ends the run",
          got == "Stopped", "the join %s, wanted Stopped" % got)

    print("\nA multitrack send, Stop at the preset and at the production")
    kept = (tb.api_key_from_anywhere, tb.choose_preset,
            tb.run_multitrack_production)
    tb.api_key_from_anywhere = lambda args: "key"
    tb.choose_preset = stopping
    line = types.SimpleNamespace(auphonic_preset="", lufs=-16.0,
                                 auphonic_wait=60, dry_run=False,
                                 auphonic_resume=None)
    # Two tracks on one axis: the send makes them one Multitrack
    # production, the way the Stop below is met in.
    pair = [{"name": "Guest", "axis": A}, {"name": "Presenter", "axis": B}]
    try:
        got = outcome(lambda: tb.send_to_auphonic(
            line, pair, WORK, WORK, 1.0))
        check("Stop while the send's preset is chosen ends the run",
              got == "Stopped", "the send %s, wanted Stopped" % got)
        tb.choose_preset = lambda *a, **k: ("uuid", "Preset")
        tb.run_multitrack_production = stopping
        got = outcome(lambda: tb.send_to_auphonic(
            line, pair, WORK, WORK, 1.0))
        check("Stop while the production is waited for ends the run",
              got == "Stopped", "the send %s, wanted Stopped" % got)
    finally:
        (tb.api_key_from_anywhere, tb.choose_preset,
         tb.run_multitrack_production) = kept

    print("\nA parallel step, Stop asked before its items are worked")
    vpm.RUN_STOP["wanted"], vpm.RUN_STOP["at"] = True, AT
    try:
        got = outcome(lambda: vpm.workbench.parallel_map([1, 2, 3],
                                                         lambda x: x))
    finally:
        vpm.RUN_STOP["wanted"], vpm.RUN_STOP["at"] = False, ""
    check("Stop in a parallel step ends the run, not a list with gaps",
          got == "Stopped", "the parallel step %s, wanted Stopped" % got)

    print("\nThe bleed check, Stop while it measures and cross-checks")
    bg = vpm.bearings
    kept = (bg.measure_offsets_by_crosstalk, bg.solve_pair_offsets,
            bg.place_track_on_axis)
    pair = [{"name": n, "source": p, "axis": p, "a": 0.0, "b": 1.0}
            for n, p in (("A", A), ("B", B))]
    calls = []

    def second_stops(tracks):
        """The first measurement comes back empty, the cross-check stops."""
        calls.append(1)
        if len(calls) > 1:
            raise vpm.Stopped(AT)
        return {}, []

    try:
        bg.measure_offsets_by_crosstalk = stopping
        got = outcome(lambda: bg.verify_alignment(pair, 0.0, 1.0))
        check("Stop while the bleed is measured ends the run",
              got == "Stopped", "the bleed check %s, wanted Stopped" % got)
        # One pair 5 ms apart, so a track is moved and then cross-checked.
        bg.measure_offsets_by_crosstalk = second_stops
        bg.solve_pair_offsets = lambda m, i, j: (1.0, 5.0, 0.0, 10, 0.1)
        bg.place_track_on_axis = lambda *a, **k: None
        got = outcome(lambda: bg.verify_alignment(pair, 0.0, 1.0))
        check("Stop while the bleed is cross-checked ends the run",
              got == "Stopped" and len(calls) == 2,
              "the cross-check %s after %d measurements, wanted Stopped "
              "after 2" % (got, len(calls)))
    finally:
        (bg.measure_offsets_by_crosstalk, bg.solve_pair_offsets,
         bg.place_track_on_axis) = kept

    print("\nThe cut's speakers, Stop while the tracks are read")
    sp = vpm.speakers
    real_read = sp.speakers_from_tracks
    sp.speakers_from_tracks = stopping
    try:
        got = outcome(lambda: sp.speakers_for_the_cut(
            types.SimpleNamespace(), pair))
    finally:
        sp.speakers_from_tracks = real_read
    check("Stop while the cut's speakers are read ends the run",
          got == "Stopped", "the speaker reading %s, wanted Stopped" % got)
except Exception:
    import traceback
    traceback.print_exc()
    bad.append("the test itself broke off")
finally:
    shutil.rmtree(WORK, ignore_errors=True)

print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
