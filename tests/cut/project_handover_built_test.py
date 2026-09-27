# -*- coding: utf-8 -*-
"""The handover is built from data alone, without a window."""
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
import the_program
SCRIPT = the_program.SCRIPT
import contextlib, io, json, shutil, sys, tempfile, time
began = time.time()
vpm = the_program.load()

# The failures collect in "error", not in "bad": further down
# slider_numbers() hands the field it could not read back under
# that name, and a check reads it there.
done = 0
error = []


def check(name, ok, extra=""):
    global done
    done += 1
    print("  %-58s %s %s" % (name, "ok" if ok else "FAIL", extra))
    if not ok:
        error.append("%s [%s]" % (name, extra or "no numbers"))


def keys_of(d):
    """What came back, short enough to stand in a FAIL line.

    A handover and a project file are both too big to print, and on
    another machine the printed line is all there is. The keys say
    whether something came back at all and what shape it had; anything
    that is not a dict prints as itself.
    """
    return sorted(d) if isinstance(d, dict) else d


print("1. The zero point: audio comes before picture")
zero = vpm.choose_zero_point([61200.0, 61300.0], [61100.0])
check("audio wins", zero == 61200.0,
        "%r against 61200.0 -- 61100.0 would mean the camera won" % (zero,))
zero = vpm.choose_zero_point([], [61100.0, 61500.0])
check("without audio the picture", zero == 61100.0,
        "%r against 61100.0, the earliest of the two cameras" % (zero,))
zero = vpm.choose_zero_point([None, 61300.0], [61100.0])
check("None is passed over", zero == 61300.0,
        "%r against 61300.0 -- a None counted as 0.0 would win" % (zero,))
zero = vpm.choose_zero_point([None], [None])
check("only None is like empty", zero is None, "%r against None" % (zero,))
zero = vpm.choose_zero_point()
check("nothing at all -> None", zero is None, "%r against None" % (zero,))

print("\n2. The time window carries on from there")
# A handover as a run writes it, as far as the time window reads one:
# the speakers' sections and the zero point, here the audio's start.
d = {"speakers": [{"name": "Guest", "sections": [[10.0, 60.0],
                                                 [120.0, 200.0]]},
                  {"name": "Co-host", "sections": [[60.0, 120.0]]}],
     "cameras": [], "length_s": 300.0, "start_s": 61200.0}
w, _complaint = vpm.apply_time_window(dict(d), "17:01:00:00", "")
check("the zero point moves along", w["start_s"] == 61260.0,
        "%r against 61260.0, the zero point 60 s further on"
        % (w["start_s"],))
# The In point sits 60 s behind the zero point, so early sections go.
check("sections move along and are trimmed",
        w["speakers"][0]["sections"] == [[60.0, 140.0]],
        "%r against [[60.0, 140.0]]" % (w["speakers"][0]["sections"],))
check("the co-host moves just the same",
        w["speakers"][1]["sections"] == [[0.0, 60.0]],
        "%r against [[0.0, 60.0]]" % (w["speakers"][1]["sections"],))
# The label goes along on the clock it was written on. The run writes
# one, and for a drop-frame reference with the semicolon -- given here
# by hand. The In point is a whole second, so
# the digits follow start_s at any rate and only the separator can go.
d["start_tc"] = "17:00:00;00"
w, _complaint = vpm.apply_time_window(dict(d), "17:01:00:00", "")
check("a fresh start_tc keeps the semicolon",
        w.get("start_tc") == "17:01:00;00",
        "%r against '17:01:00;00'" % (w.get("start_tc"),))

print("\n3. The old zero point is gone from the program")
source = the_program.whole()
lines_in_source = source.count("\n") + 1
old_sums = source.count("zero = (min(audios) if audios else")
check("the old calculation is gone", old_sums == 0,
        "%d of the old zero-point lines against 0, in %d lines of %s"
        % (old_sums, lines_in_source, os.path.basename(SCRIPT)))

print("\n4. Finding the project file, even after a wrong pick")
import os, json, shutil, tempfile
D = tempfile.mkdtemp(prefix="projfind_")
real = os.path.join(D, vpm.PROJECT_PREFIX + "Interview_2.json")
json.dump({"files": [{"path": real, "kind": "audio"}], "production": "P"},
          open(real, "w", encoding="utf-8"))
json.dump({"what": "something else"},
          open(os.path.join(D, "foreign.json"), "w"))
open(os.path.join(D, "text.txt"), "w").write("nothing")
d, found = vpm.find_project_file(real)
check("named directly", d is not None and found == real,
        "%s %r against a project at %r" % (keys_of(d), found, real))
d, found = vpm.find_project_file(D)
check("pointed at the folder", d is not None and found == real,
        "%s %r against a project at %r" % (keys_of(d), found, real))
d, found = vpm.find_project_file(os.path.join(D, "foreign.json"))
check("foreign json -> the right one next to it", found == real,
        "%r against %r" % (found, real))
d, found = vpm.find_project_file(os.path.join(D, "text.txt"))
check("no json at all -> found anyway", found == real,
        "%r against %r" % (found, real))
empty = tempfile.mkdtemp(prefix="projempty_")
d, found = vpm.find_project_file(empty)
check("empty folder -> (None, \"\")", d is None and found == "",
        "%s %r against None and '' for %r" % (keys_of(d), found, empty))
d, found = vpm.find_project_file("")
check("empty path -> (None, \"\")", d is None and found == "",
        "%s %r against None and ''" % (keys_of(d), found))
d, found = vpm.find_project_file("/doesnotexist/nor/this.json")
check("path into nothing -> no crash", d is None and found == "",
        "%s %r against None and ''" % (keys_of(d), found))
# A broken json must not hide the sound one
open(os.path.join(D, vpm.PROJECT_PREFIX + "0_broken.json"),
     "w").write("{ this is not json")
d, found = vpm.find_project_file(D)
check("broken json is skipped", found == real,
        "%r against %r" % (found, real))

print("\n5. What of the project is still there")
present, missing = vpm.project_files(
    {"files": [{"path": real, "kind": "audio"},
                 {"path": "/gone/Guest.wav", "kind": "audio"},
                 {"path": "/gone/Wide.mov", "kind": "video"},
                 {"path": ""}, {}]})
check("only the one that exists stays", present == [(real, "audio")],
        "%r against [(%r, 'audio')]" % (present, real))
check("the missing ones are named",
        missing == ["Guest.wav", "Wide.mov"],
        "%r against ['Guest.wav', 'Wide.mov']" % (missing,))
check("empty entries drop out without disturbing",
        len(present)+len(missing) == 3,
        "%d present + %d missing = %d against 3 of the 5 entries"
        % (len(present), len(missing), len(present)+len(missing)))
present, missing = vpm.project_files({})
check("empty project -> empty twice", present == [] and missing == [],
        "%r and %r against [] and []" % (present, missing))
present, missing = vpm.project_files(None)
check("None -> no crash", present == [] and missing == [],
        "%r and %r against [] and []" % (present, missing))
shutil.rmtree(D, ignore_errors=True); shutil.rmtree(empty, ignore_errors=True)

print("\n6. The sliders as numbers -- one source for both ways")
nums, bad = vpm.slider_numbers({})
check("empty means the default", bad is None
        and nums["min-edit-duration"][1] == 3.0,
        "bad %r and min-edit-duration %r against None and ('3.0', 3.0)"
        % (bad, nums.get("min-edit-duration")))
nums, bad = vpm.slider_numbers({"min-edit-duration": "2,5"})
check("comma becomes point", nums["min-edit-duration"] == ("2.5", 2.5),
        "%r against ('2.5', 2.5)" % (nums.get("min-edit-duration"),))
nums, bad = vpm.slider_numbers({"wide-after": "abc"})
check("a non-number is named", bad == "wide-after",
        "%r against 'wide-after'" % (bad,))
check("the fields before it are read already",
        "min-edit-duration" in nums and "wide-after" not in nums,
        "%s read, against a list with min-edit-duration in it "
        "and wide-after not" % (sorted(nums),))
a1, s1 = vpm.slider_argv({"min-edit-duration": "2,5"})
check("slider_argv passes the text on, not the number",
        "--min-edit-duration" in a1
        and a1[a1.index("--min-edit-duration")+1] == "2.5",
        "%r against '--min-edit-duration', '2.5' in %d arguments"
        % (a1[:2], len(a1)))
a2, s2 = vpm.slider_argv({"wide-after": "abc"})
check("slider_argv reports the same field", s2 == "wide-after",
        "%r against 'wide-after'" % (s2,))
check("and stops there", "--wide-after" not in a2,
        "--wide-after %d times in the %d arguments, against 0"
        % (a2.count("--wide-after"), len(a2)))

print("\n7. The sentence under the preview")
METRICS = {"shots": 132, "median": 12.5, "shortest": 1.2,
           "longest_camera": 98.0, "in_frame": 83.4, "in_frame_s": 3010.0,
           "on_wide": 15.1, "on_wide_s": 545.0, "off_camera": 1.5,
           "off_camera_s": 54.0, "wides": 20}
COLOURS = {"heading": "#111", "warning": "#c00", "value": "#000",
           "quiet": "#888"}
t = vpm.metrics_sentence(METRICS, COLOURS, lambda s: "%.0f min" % (s/60.0))
for piece in ("132 shots", "median 12.5 s", "83.4 %", "50 min",
               "1.5 %", "#c00"):
    check("contains %r" % piece, piece in t,
            "found %d times in the %d characters: %s"
            % (t.count(piece), len(t), t))
check("no leftover of the old formatting",
        "%(w)s" not in t and "%(l)s" not in t,
        "%d of '%%(w)s' and %d of '%%(l)s' against 0 and 0"
        % (t.count("%(w)s"), t.count("%(l)s")))

print("\n8. The heading says where the sections come from")
head = vpm.speech_heading(False)
check("separated by voice", head == "Speakers, separated by voice",
        "%r against 'Speakers, separated by voice'" % (head,))
head = vpm.speech_heading(True)
check("self-measured", "self-measured from the tracks" in head,
        "looked for 'self-measured from the tracks' in %r" % (head,))
head = vpm.speech_heading(False, "72 min")
want = ("Speakers, separated by voice (72 min) -- "
        "talking at once counts twice")
check("with the total in it and the warning about talking at once",
        head == want, "%r against %r" % (head, want))
head = vpm.speech_heading(False, "")
check("an empty total appends nothing", head.endswith("by voice"),
        "%r against a heading ending in 'by voice'" % (head,))

print("\n9. The cut read off a run's handover")


def sections_every(first, apart, holds, how_many):
    """Sections one after another, so the cut has something to do."""
    return [[round(first + i * apart, 1),
             round(first + i * apart + holds, 1)]
            for i in range(how_many)]


# Shaped the way a run writes it -- the speakers joined into the track,
# the rendered file under "file", the camera it came from under
# "source".
RUN = {"length_s": 600.0, "start_s": 61200.0,
       "speakers": [
           {"name": "Presenter",
            "sections": sections_every(2.0, 30.0, 11.0, 20)},
           {"name": "CoPresenter",
            "sections": sections_every(14.0, 30.0, 8.0, 20)},
           {"name": "Guest",
            "sections": sections_every(23.0, 30.0, 6.0, 20)}],
       "cameras": [
           {"track": "Presenter + CoPresenter",
            "file": "/r/A001_video.mov", "source": "/cam/A001.MP4",
            "camera": "A001", "speakers": ["Presenter", "CoPresenter"],
            "wide_marked": False, "wide": False},
           {"track": "Guest", "file": "/r/B002_video.mov",
            "source": "/cam/B002.MP4", "camera": "B002",
            "speakers": ["Guest"], "wide_marked": False, "wide": False},
           {"track": "WideCam", "file": "/r/C003_video.mov",
            "source": "/cam/C003.MP4", "camera": "WideCam",
            "speakers": [], "wide_marked": False, "wide": True}]}

before = vpm.cut_statistics(RUN)
check("and it stays a cut, not one shot over the whole episode",
        before["shots"] > 1,
        "%s shots against more than 1" % (before["shots"],))
# A camera marked as the wide shot keeps "wide_marked" in the handover,
# with people at it; the cut holds the mark for the wide shot.
MARKED = dict(RUN, cameras=[dict(RUN["cameras"][0], wide_marked=True,
                                 wide=True)] + RUN["cameras"][1:])
said = vpm.cut_statistics(MARKED)
check("and the cut holds it for the wide shot",
        said["wide_shots"] == ["Presenter + CoPresenter"],
        "%r against ['Presenter + CoPresenter']" % (said["wide_shots"],))

print("\n10. Two names at one camera stand in one order")
# The names at a camera are read: joined with a plus they are the
# legend under the cut band and the track name in Resolve, and that
# name is a key -- the clips of a camera and its place on the timeline
# are looked up by it. The run's builder gathers them in two goes: the
# recordings with a camera first, then the voices a separation found
# under one of them. Presenter is the recording and CoPresenter the
# voice, so gathered in that order the list comes out back to front --
# measured so on 2.9.2026.
RUN_WORK = tempfile.mkdtemp(prefix="handover_order_")
ONE_CAM = os.path.join(RUN_WORK, "A001.MP4")
open(ONE_CAM, "w").write("x")
VOICE_FILE = os.path.join(RUN_WORK, "assign.json")
with open(VOICE_FILE, "w", encoding="utf-8") as f:
    json.dump({"voices_of": {"CoPresenter": ONE_CAM}}, f)


class RunArgs(object):
    production = "Order"
    resolve = False
    lufs = -16.0
    intro = None
    outro = None
    assign = VOICE_FILE


said = io.StringIO()
with contextlib.redirect_stdout(said):
    vpm.write_handover(
        RunArgs(), [{"name": "Presenter", "camera": ONE_CAM}],
        [{"name": "A001", "video": ONE_CAM}],
        [(ONE_CAM, {"fps": 30.0, "width": 1920, "height": 1080,
                    "duration": 100.0, "tc": "10:00:00:00"})],
        RUN_WORK, 0.0, (ONE_CAM, {"fps": 30.0, "tc": "10:00:00:00"}))
written = json.load(io.open(os.path.join(RUN_WORK, "Order_resolve.json"),
                            encoding="utf-8"))
one = (written.get("cameras") or [{}])[0]
check("the run's builder sorts them too, though it gathers the "
        "recording before the voice",
        one.get("speakers") == ["CoPresenter", "Presenter"],
        "%r against ['CoPresenter', 'Presenter'] -- gathered as they "
        "arrive it is ['Presenter', 'CoPresenter']"
        % (one.get("speakers"),))
check("so the track name Resolve is keyed on reads the same either way",
        one.get("track") == "CoPresenter + Presenter",
        "%r against 'CoPresenter + Presenter'" % (one.get("track"),))
shutil.rmtree(RUN_WORK, ignore_errors=True)

print("\n11. Sync only: the handover knows nobody, whatever was assigned")
# The same material as 10 -- a recording with a camera, a voice under
# it -- but the run only synchronises. Then no name reaches the
# handover: the camera is plain and no wide shot, its track keeps the
# file's name, and the file says which kind of run it came from. A run
# that never learned the switch is a cut.
SYNC_WORK = tempfile.mkdtemp(prefix="handover_sync_")
SYNC_CAM = os.path.join(SYNC_WORK, "A001.MP4")
open(SYNC_CAM, "w").write("x")
SYNC_VOICES = os.path.join(SYNC_WORK, "assign.json")
with open(SYNC_VOICES, "w", encoding="utf-8") as f:
    json.dump({"voices_of": {"CoPresenter": SYNC_CAM}}, f)


class SyncArgs(RunArgs):
    production = "Sync"
    assign = SYNC_VOICES
    project_type = "sync"


said = io.StringIO()
with contextlib.redirect_stdout(said):
    vpm.write_handover(
        SyncArgs(), [{"name": "Presenter", "camera": SYNC_CAM}],
        [{"name": "A001", "video": SYNC_CAM}],
        [(SYNC_CAM, {"fps": 30.0, "width": 1920, "height": 1080,
                     "duration": 100.0, "tc": "10:00:00:00"})],
        SYNC_WORK, 0.0, (SYNC_CAM, {"fps": 30.0, "tc": "10:00:00:00"}))
synced = json.load(io.open(os.path.join(SYNC_WORK, "Sync_resolve.json"),
                           encoding="utf-8"))
plain = (synced.get("cameras") or [{}])[0]
check("the handover of a sync run says so",
        synced.get("project_type") == "sync",
        "project_type is %r" % (synced.get("project_type"),))
check("and its camera carries nobody and is no wide shot, though a "
        "recording and a voice were assigned to it",
        plain.get("speakers") == [] and plain.get("wide") is False,
        "speakers %r, wide %r -- the cut run above puts "
        "['CoPresenter', 'Presenter'] here"
        % (plain.get("speakers"), plain.get("wide")))
check("so its track keeps the file's name",
        plain.get("track") == "A001",
        "%r against 'A001'" % (plain.get("track"),))
check("and a run that never learned the switch hands over a cut",
        written.get("project_type") == "cut",
        "project_type is %r in the handover of section 10"
        % (written.get("project_type"),))
shutil.rmtree(SYNC_WORK, ignore_errors=True)

print("\n12. The track carries the camera's name, not the file's")
# What the run gave the camera as its name -- the window's field, or
# --new-name on the line -- reaches the handover as the track, under a
# cut with nobody on it and under Sync only alike. Where nothing was
# given the run has already put the file's stem into that name, which
# is why sections 10 and 11 see A001: the same rule, not another.
NAME_WORK = tempfile.mkdtemp(prefix="handover_named_")
NAME_CAM = os.path.join(NAME_WORK, "A001.MP4")
open(NAME_CAM, "w").write("x")


class NamedArgs(RunArgs):
    production = "Named"
    assign = ""


class NamedSyncArgs(NamedArgs):
    production = "NamedSync"
    project_type = "sync"


track_under = {}
for made in (NamedArgs(), NamedSyncArgs()):
    said = io.StringIO()
    with contextlib.redirect_stdout(said):
        vpm.write_handover(
            made, [], [{"name": "Presenter", "video": NAME_CAM}],
            [(NAME_CAM, {"fps": 30.0, "width": 1920, "height": 1080,
                         "duration": 100.0, "tc": "10:00:00:00"})],
            NAME_WORK, 0.0, (NAME_CAM, {"fps": 30.0, "tc": "10:00:00:00"}))
    hand = json.load(io.open(os.path.join(
        NAME_WORK, made.production + "_resolve.json"), encoding="utf-8"))
    track_under[made.production] = [c.get("track")
                                    for c in hand.get("cameras") or []]
check("a camera given a name is handed over under that name",
        track_under.get("Named") == ["Presenter"],
        "%r against ['Presenter'] -- the file is A001.MP4, so A001 here "
        "means the stem won" % (track_under.get("Named"),))
check("and under Sync only just the same",
        track_under.get("NamedSync") == ["Presenter"],
        "%r against ['Presenter'] -- the cut run beside it says %r"
        % (track_under.get("NamedSync"), track_under.get("Named")))
shutil.rmtree(NAME_WORK, ignore_errors=True)

print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(error) if error else "ALL OK")
sys.exit(1 if error else 0)
