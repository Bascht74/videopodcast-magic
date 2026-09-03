# -*- coding: utf-8 -*-
"""The handover is built from data alone, without a window."""
import os
HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = os.environ.get("VPM_SCRIPT") or os.path.join(
    os.path.dirname(HERE), "videopodcast-magic.py")
import contextlib, importlib.util, io, json, shutil, sys, tempfile, time
began = time.time()
spec = importlib.util.spec_from_file_location(
    "vpm", SCRIPT)
vpm = importlib.util.module_from_spec(spec); sys.modules["vpm"] = vpm
spec.loader.exec_module(vpm)

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

SEG = [("Guest", [(10.0, 60.0), (120.0, 200.0)]),
       ("Co-host", [(60.0, 120.0)])]
CAM = [{"track": "Wide", "file": "/x/Wide_C003.mov", "start_s": 61100.0},
       {"track": "Guest", "file": "/x/Guest_C009.mov", "start_s": 61500.0},
       {"track": "Hosts", "file": "/x/Host_C005.mov", "start_s": 61505.0}]
ASSIGN = {"Guest": "Guest_C009.mov", "Co-host": "Host_C005.mov"}

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

print("\n2. The handover")
d, reason = vpm.build_handover(SEG, 300.0, ASSIGN, CAM,
                               audio_origin=[61200.0], camera_origin=[61100.0])
check("no reason", reason == "", reason)
check("length taken over", d["length_s"] == 300.0,
        "%r against 300.0" % (d["length_s"],))
check("zero point from the audio", d["start_s"] == 61200.0,
        "%r against 61200.0, the audio start -- 61100.0 is the camera"
        % (d["start_s"],))
names = [s["name"] for s in d["speakers"]]
check("two speakers", names == ["Guest", "Co-host"],
        "%s against ['Guest', 'Co-host']" % (names,))
check("sections are lists, not tuples",
        d["speakers"][0]["sections"] == [[10.0, 60.0], [120.0, 200.0]],
        "%r against [[10.0, 60.0], [120.0, 200.0]]"
        % (d["speakers"][0]["sections"],))
by_track = {cam["track"]: cam["speakers"] for cam in d["cameras"]}
check("the wide shot gets nobody", by_track["Wide"] == [],
        "Wide %r against []" % (by_track["Wide"],))
check("the guest at his camera", by_track["Guest"] == ["Guest"],
        "Guest %r against ['Guest']" % (by_track["Guest"],))
check("the co-host at the hosts camera",
        by_track["Hosts"] == ["Co-host"],
        "Hosts %r against ['Co-host']" % (by_track["Hosts"],))
tracks = [cam["track"] for cam in d["cameras"]]
check("the order of the cameras stays",
        tracks == ["Wide", "Guest", "Hosts"],
        "%s against ['Wide', 'Guest', 'Hosts']" % (tracks,))

print("\n3. Two speakers on one camera")
d, _r = vpm.build_handover(
    SEG + [("Host", [(200.0, 260.0)])], 300.0,
    dict(ASSIGN, Host="Host_C005.mov"), CAM)
by_track = {cam["track"]: sorted(cam["speakers"])
            for cam in d["cameras"]}
check("both at the same camera",
        by_track["Hosts"] == ["Co-host", "Host"],
        "Hosts %r against ['Co-host', 'Host'] -- all of it %s"
        % (by_track["Hosts"], by_track))
check("without an audio start the zero point stays empty",
        d["start_s"] is None, "%r against None" % (d["start_s"],))

print("\n4. When it does not work, it says why")
d, reason = vpm.build_handover([], 300.0, ASSIGN, CAM, places=["/a", "/b"])
check("no sections -> None", d is None,
        "%s against None" % (keys_of(d),))
check("the reason names both places", "/a and /b" in reason,
        "looked for '/a and /b' in: %s" % reason)
d, reason = vpm.build_handover(SEG, 0.0, ASSIGN, CAM, places=[])
check("length 0 counts as nothing too", d is None,
        "%s against None" % (keys_of(d),))
check("without a place still a sentence", "no folder" in reason,
        "looked for 'no folder' in: %s" % reason)
d, reason = vpm.build_handover(SEG, 300.0, ASSIGN, [])
check("no cameras -> None", d is None,
        "%s against None" % (keys_of(d),))
check("the reason names Multitrack", "Multitrack" in reason, reason)

print("\n5. The time window carries on from there")
d, _r = vpm.build_handover(SEG, 300.0, ASSIGN, CAM, audio_origin=[61200.0])
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

print("\n6. The interface really takes this way")
source = open(SCRIPT, encoding="utf-8").read()
lines_in_source = source.count("\n") + 1
calls = source.count("d, reason = build_handover(")
check("off_speakers calls build_handover", calls > 0,
        "found %d times in the %d lines of %s"
        % (calls, lines_in_source, os.path.basename(SCRIPT)))
old_sums = source.count("zero = (min(audios) if audios else")
check("the old calculation is gone", old_sums == 0,
        "%d of the old zero-point lines against 0, in %d lines of %s"
        % (old_sums, lines_in_source, os.path.basename(SCRIPT)))

print("\n7. Finding the project file, even after a wrong pick")
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

print("\n8. What of the project is still there")
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

print("\n9. The sliders as numbers -- one source for both ways")
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

print("\n10. The sentence under the preview")
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

print("\n11. The heading says where the sections come from")
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

print("\n12. The window's answer reaches the cut, and nobody loses "
      "their speakers")
# Cameras are compared by file, not by track: a run joins the speakers
# into the track name, and comparing by track made the episode one shot.


def sections_every(first, apart, holds, how_many):
    """Sections one after another, so the cut has something to do."""
    return [[round(first + i * apart, 1),
             round(first + i * apart + holds, 1)]
            for i in range(how_many)]


# Shaped the way a run writes it -- the speakers joined into the track,
# the rendered file under "file", the camera it came from under
# "source" -- but with the two names deliberately left in the order
# they were handed in rather than sorted, so that the sorting the
# window does to them is visible here and not hidden by the material.
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
# What the window holds: file names, as the choice fields show them.
ON = {"Presenter": "A001.MP4", "CoPresenter": "A001.MP4",
      "Guest": "B002.MP4"}

before = vpm.cut_statistics(RUN)
fresh = vpm.wide_marks_applied(RUN, ["C003.MP4"], ON, False)
who_at = {cam["track"]: cam["speakers"] for cam in fresh["cameras"]}
check("the two on one camera keep their names",
        who_at["Presenter + CoPresenter"] == ["CoPresenter", "Presenter"],
        "%r against ['CoPresenter', 'Presenter'] -- all of it %s"
        % (who_at["Presenter + CoPresenter"], who_at))
check("the single speaker keeps his", who_at["Guest"] == ["Guest"],
        "Guest %r against ['Guest'] -- all of it %s"
        % (who_at["Guest"], who_at))
check("the camera nobody sits at stays empty",
        who_at["WideCam"] == [],
        "WideCam %r against [] -- all of it %s" % (who_at["WideCam"], who_at))
check("only the free camera counts as the wide shot",
        [cam["wide"] for cam in fresh["cameras"]] == [False, False, True],
        "%s against [False, False, True] for %s"
        % ([cam["wide"] for cam in fresh["cameras"]],
           [cam["track"] for cam in fresh["cameras"]]))

after = vpm.cut_statistics(fresh)
check("the number of shots survives the window's answer",
        after["shots"] == before["shots"],
        "%s shots before against %s after" % (before["shots"],
                                              after["shots"]))
check("and it stays a cut, not one shot over the whole episode",
        after["shots"] > 1, "%s shots against more than 1" % (after["shots"],))
check("the wide shot is still the one nobody sits at",
        after["wide"] == "WideCam", "%r against 'WideCam'" % (after["wide"],))

# A mark in the Kind field is an answer, not a derivation. Marking a
# camera somebody sits at is what tells the two apart.
marked = vpm.wide_marks_applied(RUN, ["A001.MP4"], ON, True)
check("the marked camera carries wide_marked",
        [cam.get("wide_marked") for cam in marked["cameras"]]
        == [True, False, False],
        "%s against [True, False, False] for %s"
        % ([cam.get("wide_marked") for cam in marked["cameras"]],
           [cam["track"] for cam in marked["cameras"]]))
said = vpm.cut_statistics(marked)
check("and the cut holds it for the wide shot",
        said["wide_shots"] == ["Presenter + CoPresenter"],
        "%r against ['Presenter + CoPresenter']" % (said["wide_shots"],))
check("so the mark beats the derivation",
        said["wide"] != before["wide"],
        "%r with the mark against %r without it -- they must differ"
        % (said["wide"], before["wide"]))

# An empty assignment says nothing, not "nobody": the sheet may not be
# built yet, and the file's own answer would be wiped every time.
for nothing, called in (({}, "{}"), (None, "None")):
    kept = vpm.wide_marks_applied(RUN, ["C003.MP4"], nothing, False)
    at = {cam["track"]: cam["speakers"] for cam in kept["cameras"]}
    check("nothing answered yet (%s) -> the file's answer stands" % called,
            at["Presenter + CoPresenter"] == ["Presenter", "CoPresenter"]
            and at["Guest"] == ["Guest"] and at["WideCam"] == [],
            "%s against {'Presenter + CoPresenter': ['Presenter', "
            "'CoPresenter'], 'Guest': ['Guest'], 'WideCam': []}" % (at,))
    check("and the cut stays what it was (%s)" % called,
            vpm.cut_statistics(kept)["shots"] == before["shots"],
            "%s shots before against %s after"
            % (before["shots"], vpm.cut_statistics(kept)["shots"]))

# The preview has no rendered file: "file" names the camera itself.
PREVIEW = dict(RUN, cameras=[
    {"track": cam["track"], "file": "/cam/%s.MP4" % cam["camera"],
     "speakers": cam["speakers"], "start_s": 61100.0,
     "wide_marked": False, "wide": not cam["speakers"]}
    for cam in RUN["cameras"]])
seen = vpm.wide_marks_applied(PREVIEW, ["C003.MP4"], ON, False)
at = {cam["track"]: cam["speakers"] for cam in seen["cameras"]}
check("without a source the file answers",
        at["Presenter + CoPresenter"] == ["CoPresenter", "Presenter"]
        and at["Guest"] == ["Guest"],
        "%s against ['CoPresenter', 'Presenter'] and ['Guest']" % (at,))

print("\n13. Cameras whose file is not there yet")
# The preview is built from data alone, so a camera whose file has not
# been written yet still belongs in it. Two cameras here have nobody
# sitting at them, one with a file and one without: both are the wide
# shot, which is how one sees that the file decides nothing. And the
# empty path has to stay empty -- a path invented here is one the cut
# would later hand to Resolve, which imports whatever it is given.
NOT_YET = [{"track": "WideCam", "file": "", "start_s": 61100.0},
           {"track": "Spare", "file": "/cam/D004.MP4", "start_s": 61100.0},
           {"track": "Presenter", "file": "/cam/A001.MP4",
            "start_s": 61100.0},
           {"track": "Guest", "file": "/cam/B002.MP4", "start_s": 61100.0},
           {"track": "Ghost", "start_s": 61100.0}]   # no file field at all
LOTS = [("Presenter", sections_every(2.0, 30.0, 11.0, 20)),
        ("Guest", sections_every(23.0, 30.0, 6.0, 20))]
AT = {"Presenter": "A001.MP4", "Guest": "B002.MP4"}
d, reason = vpm.build_handover(LOTS, 600.0, AT, NOT_YET,
                               audio_origin=[61200.0])
check("a camera without a file does not stop the preview",
        d is not None and reason == "",
        "%s and reason %r against a handover and ''"
        % (keys_of(d), reason))
paths = [cam["file"] for cam in (d or {}).get("cameras") or []]
check("the paths come through as they were given, empty and missing too",
        paths == ["", "/cam/D004.MP4", "/cam/A001.MP4", "/cam/B002.MP4",
                  None],
        "%r against ['', '/cam/D004.MP4', '/cam/A001.MP4', "
        "'/cam/B002.MP4', None]" % (paths,))
sits_at = {cam["track"]: cam["speakers"]
           for cam in (d or {}).get("cameras") or []}
check("the cameras that do have a file keep their speakers",
        sits_at.get("Presenter") == ["Presenter"]
        and sits_at.get("Guest") == ["Guest"],
        "%s against Presenter ['Presenter'] and Guest ['Guest']" % (sits_at,))
free = [cam["wide"] for cam in (d or {}).get("cameras") or []]
check("the file plays no part in who is the wide shot",
        free == [True, True, False, False, True],
        "%s against [True, True, False, False, True] for %s -- WideCam has "
        "no file and Spare has one, and neither has a speaker"
        % (free, [cam["track"] for cam in (d or {}).get("cameras") or []]))
numbers = vpm.cut_statistics(d) or {}
check("the preview still cuts with a camera that has no file",
        numbers.get("shots", 0) > 1,
        "%s shots against more than 1, over %d cameras"
        % (numbers.get("shots"), len(paths)))

print("\n14. Two names at one camera stand in one order, whoever built it")
# The names at a camera are read: joined with a plus they are the
# legend under the cut band and the track name in Resolve, and that
# name is a key -- the clips of a camera and its place on the timeline
# are looked up by it. Two builders make the list. Measured on
# 2.9.2026 they ordered it differently: the preview sorted, the run put
# the recordings' names before the voices'. Both are handed material
# whose given order is the reverse of the sorted one, or a sorted list
# could not be told from one that came out as it went in.
BACK_TO_FRONT = {"Presenter": "Host_C005.mov",
                 "CoPresenter": "Host_C005.mov"}
d, _r = vpm.build_handover(
    [("Presenter", [(0.0, 10.0)]), ("CoPresenter", [(10.0, 20.0)])],
    300.0, BACK_TO_FRONT, CAM)
at_camera = {cam["track"]: cam["speakers"] for cam in d["cameras"]}
check("the preview builder sorts the two names, whatever order they "
        "were assigned in",
        at_camera["Hosts"] == ["CoPresenter", "Presenter"],
        "%r against ['CoPresenter', 'Presenter'] -- the assignment names "
        "them the other way round, all of it %s"
        % (at_camera["Hosts"], at_camera))

# And the run's builder, which gathers them in two goes: the recordings
# with a camera first, then the voices a separation found under one of
# them. Presenter is the recording and CoPresenter the voice, so
# gathered in that order the list comes out back to front.
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

print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(error) if error else "ALL OK")
sys.exit(1 if error else 0)
