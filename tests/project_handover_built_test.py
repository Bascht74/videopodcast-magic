# -*- coding: utf-8 -*-
"""The handover is built from data alone, without a window."""
import os
HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = os.environ.get("VPM_SCRIPT") or os.path.join(
    os.path.dirname(HERE), "videopodcast-magic.py")
import sys, importlib.util
spec = importlib.util.spec_from_file_location(
    "vpm", SCRIPT)
vpm = importlib.util.module_from_spec(spec); sys.modules["vpm"] = vpm
spec.loader.exec_module(vpm)

error = []
def check(name, ok, extra=""):
    print("  %-54s %s %s" % (name, "ok" if ok else "FAIL", extra))
    if not ok:
        error.append(name)

SEG = [("Guest", [(10.0, 60.0), (120.0, 200.0)]),
       ("Co-host", [(60.0, 120.0)])]
CAM = [{"track": "Wide", "file": "/x/Wide_C003.mov", "start_s": 61100.0},
       {"track": "Guest", "file": "/x/Guest_C009.mov", "start_s": 61500.0},
       {"track": "Hosts", "file": "/x/Host_C005.mov", "start_s": 61505.0}]
ASSIGN = {"Guest": "Guest_C009.mov", "Co-host": "Host_C005.mov"}

print("1. The zero point: audio comes before picture")
check("audio wins", vpm.choose_zero_point([61200.0, 61300.0],
                                           [61100.0]) == 61200.0)
check("without audio the picture",
        vpm.choose_zero_point([], [61100.0, 61500.0]) == 61100.0)
check("None is passed over",
        vpm.choose_zero_point([None, 61300.0], [61100.0]) == 61300.0)
check("only None is like empty",
        vpm.choose_zero_point([None], [None]) is None)
check("nothing at all -> None", vpm.choose_zero_point() is None)

print("\n2. The handover")
d, reason = vpm.build_handover(SEG, 300.0, ASSIGN, CAM,
                               audio_origin=[61200.0], camera_origin=[61100.0])
check("no reason", reason == "", reason)
check("length taken over", d["length_s"] == 300.0)
check("zero point from the audio", d["start_s"] == 61200.0)
check("two speakers", [s["name"] for s in d["speakers"]]
        == ["Guest", "Co-host"])
check("sections are lists, not tuples",
        d["speakers"][0]["sections"] == [[10.0, 60.0], [120.0, 200.0]])
by_track = {cam["track"]: cam["speakers"] for cam in d["cameras"]}
check("the wide shot gets nobody", by_track["Wide"] == [])
check("the guest at his camera", by_track["Guest"] == ["Guest"])
check("the co-host at the hosts camera",
        by_track["Hosts"] == ["Co-host"])
check("the order of the cameras stays",
        [cam["track"] for cam in d["cameras"]] == ["Wide", "Guest",
                                                   "Hosts"])

print("\n3. Two speakers on one camera")
d, _r = vpm.build_handover(
    SEG + [("Host", [(200.0, 260.0)])], 300.0,
    dict(ASSIGN, Host="Host_C005.mov"), CAM)
by_track = {cam["track"]: sorted(cam["speakers"])
            for cam in d["cameras"]}
check("both at the same camera",
        by_track["Hosts"] == ["Co-host", "Host"], str(by_track))
check("without an audio start the zero point stays empty",
        d["start_s"] is None)

print("\n4. When it does not work, it says why")
d, reason = vpm.build_handover([], 300.0, ASSIGN, CAM, places=["/a", "/b"])
check("no sections -> None", d is None)
check("the reason names both places", "/a and /b" in reason, reason[:70])
d, reason = vpm.build_handover(SEG, 0.0, ASSIGN, CAM, places=[])
check("length 0 counts as nothing too", d is None)
check("without a place still a sentence", "no folder" in reason, reason[:70])
d, reason = vpm.build_handover(SEG, 300.0, ASSIGN, [])
check("no cameras -> None", d is None)
check("the reason names Multitrack", "Multitrack" in reason, reason)

print("\n5. The time window carries on from there")
d, _r = vpm.build_handover(SEG, 300.0, ASSIGN, CAM, audio_origin=[61200.0])
w, _complaint = vpm.apply_time_window(dict(d), "17:01:00:00", "")
check("the zero point moves along", w["start_s"] == 61260.0, str(w["start_s"]))
# The In point sits 60 s behind the zero point, so early sections go.
check("sections move along and are trimmed",
        w["speakers"][0]["sections"] == [[60.0, 140.0]],
        str(w["speakers"][0]["sections"]))
check("the co-host moves just the same",
        w["speakers"][1]["sections"] == [[0.0, 60.0]],
        str(w["speakers"][1]["sections"]))

print("\n6. The interface really takes this way")
source = open(SCRIPT, encoding="utf-8").read()
check("off_speakers calls build_handover",
        "d, reason = build_handover(" in source)
check("the old calculation is gone",
        "zero = (min(audios) if audios else" not in source)

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
check("named directly", d is not None and found == real)
d, found = vpm.find_project_file(D)
check("pointed at the folder", d is not None and found == real)
d, found = vpm.find_project_file(os.path.join(D, "foreign.json"))
check("foreign json -> the right one next to it", found == real)
d, found = vpm.find_project_file(os.path.join(D, "text.txt"))
check("no json at all -> found anyway", found == real)
empty = tempfile.mkdtemp(prefix="projempty_")
d, found = vpm.find_project_file(empty)
check("empty folder -> (None, \"\")", d is None and found == "")
d, found = vpm.find_project_file("")
check("empty path -> (None, \"\")", d is None and found == "")
d, found = vpm.find_project_file("/doesnotexist/nor/this.json")
check("path into nothing -> no crash", d is None and found == "")
# A broken json must not hide the sound one
open(os.path.join(D, vpm.PROJECT_PREFIX + "0_broken.json"),
     "w").write("{ this is not json")
d, found = vpm.find_project_file(D)
check("broken json is skipped", found == real, found)

print("\n8. What of the project is still there")
present, missing = vpm.project_files(
    {"files": [{"path": real, "kind": "audio"},
                 {"path": "/gone/Guest.wav", "kind": "audio"},
                 {"path": "/gone/Wide.mov", "kind": "video"},
                 {"path": ""}, {}]})
check("only the one that exists stays", present == [(real, "audio")],
        str(present))
check("the missing ones are named",
        missing == ["Guest.wav", "Wide.mov"], str(missing))
check("empty entries drop out without disturbing",
        len(present)+len(missing) == 3)
present, missing = vpm.project_files({})
check("empty project -> empty twice", present == [] and missing == [])
present, missing = vpm.project_files(None)
check("None -> no crash", present == [] and missing == [])
shutil.rmtree(D, ignore_errors=True); shutil.rmtree(empty, ignore_errors=True)

print("\n9. The sliders as numbers -- one source for both ways")
nums, bad = vpm.slider_numbers({})
check("empty means the default", bad is None
        and nums["min-edit-duration"][1] == 3.0, str(nums["min-edit-duration"]))
nums, bad = vpm.slider_numbers({"min-edit-duration": "2,5"})
check("comma becomes point", nums["min-edit-duration"] == ("2.5", 2.5))
nums, bad = vpm.slider_numbers({"wide-after": "abc"})
check("a non-number is named", bad == "wide-after")
check("the fields before it are read already",
        "min-edit-duration" in nums and "wide-after" not in nums)
a1, s1 = vpm.slider_argv({"min-edit-duration": "2,5"})
check("slider_argv passes the text on, not the number",
        "--min-edit-duration" in a1
        and a1[a1.index("--min-edit-duration")+1] == "2.5")
a2, s2 = vpm.slider_argv({"wide-after": "abc"})
check("slider_argv reports the same field", s2 == "wide-after")
check("and stops there", "--wide-after" not in a2)

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
    check("contains %r" % piece, piece in t, "")
check("no leftover of the old formatting",
        "%(w)s" not in t and "%(l)s" not in t)

print("\n11. The heading says where the sections come from")
check("separated by voice", vpm.speech_heading(False) ==
        "Speakers, separated by voice")
check("self-measured",
        "self-measured from the tracks" in vpm.speech_heading(True))
check("with the total appended",
        vpm.speech_heading(False, "72 min") ==
        "Speakers, separated by voice -- 72 min")
check("an empty total appends nothing",
        vpm.speech_heading(False, "").endswith("by voice"))

print("\n12. The window's answer reaches the cut, and nobody loses "
      "their speakers")
# Cameras are compared by file, not by track: a run joins the speakers
# into the track name, and comparing by track made the episode one shot.


def sections_every(first, apart, holds, how_many):
    """Sections one after another, so the cut has something to do."""
    return [[round(first + i * apart, 1),
             round(first + i * apart + holds, 1)]
            for i in range(how_many)]


# Shaped the way a run writes it: the speakers joined into the track,
# the rendered file under "file", the camera it came from under "source".
RUN = {"length_s": 600.0, "start_s": 61200.0,
       "speakers": [
           {"name": "Moderator",
            "sections": sections_every(2.0, 30.0, 11.0, 20)},
           {"name": "Moderatorin",
            "sections": sections_every(14.0, 30.0, 8.0, 20)},
           {"name": "Gast",
            "sections": sections_every(23.0, 30.0, 6.0, 20)}],
       "cameras": [
           {"track": "Moderator + Moderatorin",
            "file": "/r/A001_video.mov", "source": "/cam/A001.MP4",
            "camera": "A001", "speakers": ["Moderator", "Moderatorin"],
            "wide_marked": False, "wide": False},
           {"track": "Gast", "file": "/r/B002_video.mov",
            "source": "/cam/B002.MP4", "camera": "B002",
            "speakers": ["Gast"], "wide_marked": False, "wide": False},
           {"track": "Totale", "file": "/r/C003_video.mov",
            "source": "/cam/C003.MP4", "camera": "Totale",
            "speakers": [], "wide_marked": False, "wide": True}]}
# What the window holds: file names, as the choice fields show them.
ON = {"Moderator": "A001.MP4", "Moderatorin": "A001.MP4",
      "Gast": "B002.MP4"}

before = vpm.cut_statistics(RUN)
fresh = vpm.wide_marks_applied(RUN, ["C003.MP4"], ON, False)
who_at = {cam["track"]: cam["speakers"] for cam in fresh["cameras"]}
check("the two on one camera keep their names",
        who_at["Moderator + Moderatorin"] == ["Moderator", "Moderatorin"],
        str(who_at))
check("the single speaker keeps his", who_at["Gast"] == ["Gast"],
        str(who_at))
check("the camera nobody sits at stays empty",
        who_at["Totale"] == [], str(who_at))
check("only the free camera counts as the wide shot",
        [cam["wide"] for cam in fresh["cameras"]] == [False, False, True],
        str([cam["wide"] for cam in fresh["cameras"]]))

after = vpm.cut_statistics(fresh)
check("the number of shots survives the window's answer",
        after["shots"] == before["shots"],
        "%s -> %s" % (before["shots"], after["shots"]))
check("and it stays a cut, not one shot over the whole episode",
        after["shots"] > 1, str(after["shots"]))
check("the wide shot is still the one nobody sits at",
        after["wide"] == "Totale", str(after["wide"]))

# A mark in the Kind field is an answer, not a derivation. Marking a
# camera somebody sits at is what tells the two apart.
marked = vpm.wide_marks_applied(RUN, ["A001.MP4"], ON, True)
check("the marked camera carries wide_marked",
        [cam.get("wide_marked") for cam in marked["cameras"]]
        == [True, False, False],
        str([cam.get("wide_marked") for cam in marked["cameras"]]))
said = vpm.cut_statistics(marked)
check("and the cut holds it for the wide shot",
        said["wide_shots"] == ["Moderator + Moderatorin"],
        str(said["wide_shots"]))
check("so the mark beats the derivation",
        said["wide"] != before["wide"],
        "%s vs %s" % (said["wide"], before["wide"]))

# An empty assignment says nothing, not "nobody": the sheet may not be
# built yet, and the file's own answer would be wiped every time.
for nothing, called in (({}, "{}"), (None, "None")):
    kept = vpm.wide_marks_applied(RUN, ["C003.MP4"], nothing, False)
    at = {cam["track"]: cam["speakers"] for cam in kept["cameras"]}
    check("nothing answered yet (%s) -> the file's answer stands" % called,
            at["Moderator + Moderatorin"] == ["Moderator", "Moderatorin"]
            and at["Gast"] == ["Gast"] and at["Totale"] == [], str(at))
    check("and the cut stays what it was (%s)" % called,
            vpm.cut_statistics(kept)["shots"] == before["shots"],
            "%s -> %s" % (before["shots"],
                          vpm.cut_statistics(kept)["shots"]))

# The preview has no rendered file: "file" names the camera itself.
PREVIEW = dict(RUN, cameras=[
    {"track": cam["track"], "file": "/cam/%s.MP4" % cam["camera"],
     "speakers": cam["speakers"], "start_s": 61100.0,
     "wide_marked": False, "wide": not cam["speakers"]}
    for cam in RUN["cameras"]])
seen = vpm.wide_marks_applied(PREVIEW, ["C003.MP4"], ON, False)
at = {cam["track"]: cam["speakers"] for cam in seen["cameras"]}
check("without a source the file answers",
        at["Moderator + Moderatorin"] == ["Moderator", "Moderatorin"]
        and at["Gast"] == ["Gast"], str(at))

print("\n%s" % ("all good" if not error
                else "FAIL: %s" % ", ".join(error)))
sys.exit(1 if error else 0)
