# -*- coding: utf-8 -*-
"""run_argv() builds the command line and the plan, or says why not.

Three independent claims. The command line is the one that would be
written by hand; the plan beside it carries what no switch can, the
cameras and the tracks; and what cannot be run is refused with a title
a person can read, while a merely doubtful case becomes a question.
The last sections hold gui() to calling this and keeping no assembly
of its own, since two builders of one command line drift apart."""
import os
HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = os.environ.get("VPM_SCRIPT") or os.path.join(
    os.path.dirname(HERE), "videopodcast-magic.py")
import sys, importlib.util, time
began = time.time()
spec = importlib.util.spec_from_file_location(
    "vpm", SCRIPT)
vpm = importlib.util.module_from_spec(spec); sys.modules["vpm"] = vpm
spec.loader.exec_module(vpm)

done = 0
# The list is called error and not bad because section 17 already gives
# that name to what slider_argv hands back as its second answer.
error = []


def check(name, ok, extra=""):
    global done
    done += 1
    print("  %-58s %s %s" % (name, "ok" if ok else "FAIL", extra))
    if not ok:
        error.append("%s [%s]" % (name, extra or "no numbers"))

def values(**k):
    state = {"files": [], "clip_kinds": {}, "out_folder": "",
             "dry_run": False, "multitrack": False,
             "camera_audio_only": False, "rows": [], "cameras": [],
             "production": "", "in_point": "", "out_point": "", "cut": {},
             "wide_at_edges": True, "key": "", "preset": "",
             "done_folder": ""}
    state.update(k)
    return state

print("1. The simple way: files, folder, nothing else")
a, plan, m = vpm.run_argv(values(
    files=[("/x/a.wav", "audio"), ("/x/G.mov", "video")],
    out_folder="/out"))
print("   ", a)
check("program name first", a[0] == "videopodcast-magic.py")
check("both files there", a[1:3] == ["/x/a.wav", "/x/G.mov"])
check("--out behind them", a[3:5] == ["--out", "/out"])
check("no plan", plan is None)
check("no message", m == [])

print("\n2. Intro, outro and ignoring")
a, _p, _m = vpm.run_argv(values(
    files=[("/x/G.mov", "video"), ("/x/J.mp4", "video"),
             ("/x/O.mp4", "video"), ("/x/away.mov", "video")],
    clip_kinds={"/x/J.mp4": vpm.TYPE_INTRO, "/x/O.mp4": vpm.TYPE_OUTRO,
         "/x/away.mov": vpm.TYPE_IGNORED}))
print("   ", a)
check("only the content file in the list", a[1:2] == ["/x/G.mov"])
check("--intro and --outro sorted",
        a[2:6] == ["--intro", "/x/J.mp4", "--outro", "/x/O.mp4"], str(a[2:6]))
check("the ignored one is missing", "/x/away.mov" not in a)

print("\n2b. Two files marked as the intro is refused, not silently halved")
# Both would be written into the same --intro and the folder listing would
# decide which one survives. So the run stops and names the two.
a, _p, m = vpm.run_argv(values(
    files=[("/x/G.mov", "video"), ("/x/J.mp4", "video"),
             ("/x/K.mp4", "video")],
    clip_kinds={"/x/J.mp4": vpm.TYPE_INTRO, "/x/K.mp4": vpm.TYPE_INTRO}))
check("rejected", a is None, str(a))
check("and it says which two", m and "J.mp4" in m[0][2] and "K.mp4" in m[0][2],
        str(m[:1]))
a, _p, m = vpm.run_argv(values(
    files=[("/x/G.mov", "video"), ("/x/J.mp4", "video"),
             ("/x/K.mp4", "video")],
    clip_kinds={"/x/J.mp4": vpm.TYPE_OUTRO, "/x/K.mp4": vpm.TYPE_OUTRO}))
check("the same for the outro", a is None, str(a))
a, _p, m = vpm.run_argv(values(
    files=[("/x/J.mp4", "video"), ("/x/K.mp4", "video")],
    clip_kinds={"/x/J.mp4": vpm.TYPE_INTRO, "/x/K.mp4": vpm.TYPE_OUTRO}))
check("one of each is fine", a is not None and "--intro" in a, str(a))

print("\n3. Dry run")
a, _p, _m = vpm.run_argv(values(dry_run=True))
check("--dry-run there", "--dry-run" in a)

print("\n4. Multitrack needs at least two recordings")
a, plan, m = vpm.run_argv(values(multitrack=True, key="k", preset="p",
    rows=[{"blocks": ["/x/a.wav"], "speakers": "A",
           "camera_choice": "G.mov"}]))
check("rejected", a is None)
check("error named", m and m[0][0] == "error" and "at least two"
        in m[0][2], str(m[:1]))

print("\n5. Names missing")
a, _p, m = vpm.run_argv(values(multitrack=True, key="k", preset="p", rows=[
    {"blocks": ["/x/a.wav"], "speakers": "A", "camera_choice": "G.mov"},
    {"blocks": ["/x/b.wav"], "speakers": " ", "camera_choice": "H.mov"}]))
check("rejected", a is None)
check("speaker names", m[-1][1] == "Speaker names", str(m[-1][1]))

print("\n6. Every row the same name -> only one speaker")
a, _p, m = vpm.run_argv(values(multitrack=True, key="k", preset="p", rows=[
    {"blocks": ["/x/a.wav"], "speakers": "A", "camera_choice": "G.mov"},
    {"blocks": ["/x/b.wav"], "speakers": "A", "camera_choice": "H.mov"}]))
check("rejected", a is None)
check("only one speaker", m[-1][1] == "Only one speaker", str(m[-1][1]))

print("\n7. Duplicate name among several -> a question, not an error")
a, plan, m = vpm.run_argv(values(multitrack=True, key="k", preset="p", rows=[
    {"blocks": ["/x/a.wav"], "speakers": "A", "camera_choice": "G.mov"},
    {"blocks": ["/x/b.wav"], "speakers": "A", "camera_choice": "G.mov"},
    {"blocks": ["/x/c.wav"], "speakers": "B", "camera_choice": "H.mov"}],
    cameras=[{"path": "/x/G.mov", "name": "Cam1"},
             {"path": "/x/H.mov", "name": "Cam2"}]))
check("gets through", a is not None)
check("one question", [x[0] for x in m] == ["question"],
        str([x[0] for x in m]))
check("title is right", m[0][1] == "Names used more than once")
check("button labelled", m[0][3] == "Merge them")

print("\n8. Ignored rows do not count")
a, _p, m = vpm.run_argv(values(multitrack=True, key="k", preset="p", rows=[
    {"blocks": ["/x/a.wav"], "speakers": "A", "camera_choice": "G.mov"},
    {"blocks": ["/x/b.wav"], "speakers": "B", "camera_choice": "H.mov"},
    {"blocks": ["/x/c.wav"], "speakers": "C",
     "camera_choice": vpm.IGNORE_AUDIO}],
    cameras=[{"path": "/x/G.mov", "name": "Cam1"},
             {"path": "/x/H.mov", "name": "Cam2"}]))
check("gets through", a is not None)
check("only two tracks in the plan", len(_p["tracks_of"]) == 2,
        str(len(_p["tracks_of"])))
check("the ignored one is missing",
        "C" not in [x["speakers"] for x in _p["tracks_of"]])

print("\n9. The full multitrack run")
a, plan, m = vpm.run_argv(values(
    files=[("/x/a.wav", "audio"), ("/x/b.wav", "audio"),
             ("/x/G.mov", "video"), ("/x/H.mov", "video")],
    out_folder="/out", multitrack=True, key="secret", preset="Preset 1",
    done_folder="/out/auphonic-tracks", production="Interview",
    in_point="17:00:00:00", out_point="18:00:00:00", wide_at_edges=False,
    cut={"min-edit-duration": "1,5"},
    rows=[{"blocks": ["/x/a.wav"], "speakers": "A", "camera_choice": "G.mov"},
          {"blocks": ["/x/b.wav"], "speakers": "B", "camera_choice": "H.mov"}],
    cameras=[{"path": "/x/G.mov", "name": "Cam1"},
             {"path": "/x/H.mov", "name": "Cam2"}]), "/tmp/assignment.json")
print("   ", " ".join(a))
check("--multitrack there", "--multitrack" in a)
check("--assign with path",
        a[a.index("--assign") + 1] == "/tmp/assignment.json")
check("--in-point", a[a.index("--in-point") + 1] == "17:00:00:00")
check("--out-point", a[a.index("--out-point") + 1] == "18:00:00:00")
check("comma becomes a point",
        a[a.index("--min-edit-duration") + 1] == "1.5")
check("defaults for the other sliders",
        all("--" + k in a for k, _b, _v, _e, _kk, _l in vpm.CUT_FIELDS))
check("--no-wide-edges", "--no-wide-edges" in a)
check("key and preset",
        a[a.index("--auphonic-api-key") + 1] == "secret"
        and a[a.index("--auphonic-preset") + 1] == "Preset 1")
check("--auphonic-done",
        a[a.index("--auphonic-done") + 1] == "/out/auphonic-tracks")
check("plan carries the production", plan["production"] == "Interview")
check("plan carries two cameras", len(plan["cameras"]) == 2)
check("camera resolved for the track",
        plan["tracks_of"][0]["camera"] == "/x/G.mov",
        plan["tracks_of"][0]["camera"])

print("\n10. No number in the slider field")
a, _p, m = vpm.run_argv(values(multitrack=True, key="k", preset="p",
    cut={"min-edit-duration": "lots"},
    rows=[{"blocks": ["/x/a.wav"], "speakers": "A", "camera_choice": "G.mov"},
          {"blocks": ["/x/b.wav"], "speakers": "B", "camera_choice": "H.mov"}],
    cameras=[{"path": "/x/G.mov", "name": "G"},
             {"path": "/x/H.mov", "name": "H"}]))
check("rejected", a is None)
check("says which value", "'lots'" in m[-1][2], m[-1][2])

print("\n11. Two cameras, one target name")
a, _p, m = vpm.run_argv(values(multitrack=True, key="k", preset="p",
    rows=[{"blocks": ["/x/a.wav"], "speakers": "A", "camera_choice": "G.mov"},
          {"blocks": ["/x/b.wav"], "speakers": "B", "camera_choice": "H.mov"}],
    cameras=[{"path": "/x/G.mov", "name": "same"},
             {"path": "/x/H.mov", "name": "same"}]))
check("rejected", a is None)
check("file names", m[-1][1] == "File names", str(m[-1][1]))

print("\n12. Key without a preset")
a, _p, m = vpm.run_argv(values(key="secret"))
check("rejected", a is None)
check("preset missing", m[-1][1] == "Preset missing")

print("\n13. Multitrack without a key runs locally")
a, plan, m = vpm.run_argv(values(multitrack=True,
    rows=[{"blocks": ["/x/a.wav"], "speakers": "A", "camera_choice": "G.mov"},
          {"blocks": ["/x/b.wav"], "speakers": "B", "camera_choice": "H.mov"}],
    cameras=[{"path": "/x/G.mov", "name": "G"},
             {"path": "/x/H.mov", "name": "H"}]))
check("not rejected", a is not None, str(m))
check("--without-auphonic is there", "--without-auphonic" in (a or []))
check("nothing goes to auphonic.com",
        "--auphonic-api-key" not in (a or []))
check("the assignment is still written", plan is not None)

print("\n14. Camera audio only: question first, tracks as camera")
a, plan, m = vpm.run_argv(values(multitrack=True, key="k", preset="p",
    camera_audio_only=True,
    files=[("/x/G.mov", "video"), ("/x/H.mov", "video")],
    rows=[{"blocks": ["/x/G.mov"], "speakers": "A", "camera_choice": "G.mov"},
          {"blocks": ["/x/H.mov"], "speakers": "B", "camera_choice": "H.mov"}],
    cameras=[{"path": "/x/G.mov", "name": "G"},
             {"path": "/x/H.mov", "name": "H"}]))
check("the question comes first", m and m[0][1] == "Cameras only", str(m[:1]))
check("gets through", a is not None)
check("every track is its own camera",
        all(x["camera_audio"] for x in plan["tracks_of"]))
check("camera points at the audio file",
        plan["tracks_of"][0]["camera"].endswith("G.mov"),
        plan["tracks_of"][0]["camera"])

print("\n15. An own-audio row carries its finished file along")
a, plan, m = vpm.run_argv(values(multitrack=True, key="k", preset="p",
    files=[("/x/G.mov", "video"), ("/x/H.mov", "video")],
    rows=[{"blocks": ["/x/G.mov"], "speakers": "A", "camera_choice": "G.mov",
             "own_audio": True, "audio_done": "/tmp/done.wav"},
          {"blocks": ["/x/b.wav"], "speakers": "B", "camera_choice": "H.mov"}],
    cameras=[{"path": "/x/G.mov", "name": "G"},
             {"path": "/x/H.mov", "name": "H"}]))
check("audio_done taken over",
        plan["tracks_of"][0].get("audio_done") == "/tmp/done.wav",
        str(plan["tracks_of"][0].get("audio_done")))
check("the other row without", "audio_done" not in plan["tracks_of"][1])

print("\n16. The interface really calls run_argv")
import inspect
source = inspect.getsource(vpm.gui)
check("call present", "run_argv(values, assign_file)" in source)
check("no argv tinkering left in gui()",
        'argv += ["--auphonic-api-key"' not in source
        and '"--multitrack", "--assign"' not in source
        and 'argv += ["--" + key' not in source)
check("the key is still thrown out when saving",
        'if part == "--auphonic-api-key":' in source)

print("\n17. slider_argv on its own")
t, bad = vpm.slider_argv({})
check("empty values -> all defaults", bad is None
        and len(t) == 2 * (len(vpm.CUT_FIELDS) + len(vpm.CUT_CHOICES)),
        "%d" % len(t))
t, bad = vpm.slider_argv({"wide-after": "60"})
check("a set value gets through", t[t.index("--wide-after") + 1] == "60")
t, bad = vpm.slider_argv({"wide-after": "6,5"})
check("comma becomes point", t[t.index("--wide-after") + 1] == "6.5")
t, bad = vpm.slider_argv({"wide-after": "soon"})
check("a non-number is reported", bad == "wide-after", str(bad))
check("and the same list is shared with only_resolve_start_run",
        "slider_argv(values)" in source)

print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(error) if error else "ALL OK")
sys.exit(1 if error else 0)
