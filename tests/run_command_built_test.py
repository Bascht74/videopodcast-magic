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
    os.path.dirname(HERE), "videopodcast_magic.py")
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

# Six judgements are called "rejected" and three "gets through", once per
# section. So every failure line starts with the number of the section it
# belongs to, or a red run names a check that stands seven times.

SLIDER_SWITCHES = set(
    ["--" + k for k, _b, _v, _e, _kk, _l in vpm.CUT_FIELDS]
    + ["--" + k for k, _b, _v, _e, _kk, _l in vpm.CUT_CHOICES])


def shown(argv):
    """The command line for a failure line, the cut switches folded up.

    Every built line carries the same twelve cut switches with their
    values, so writing them out buries the part a check is about. They
    are counted instead. Only for printing -- no check reads this.
    """
    if not argv:
        return repr(argv)
    rest = []
    folded = 0
    skip = False
    for word in argv:
        if skip:
            skip = False
            continue
        if word in SLIDER_SWITCHES:
            folded += 1
            skip = True
            continue
        rest.append(word)
    return "%s (+ %d cut switches)" % (" ".join(rest), folded)


def brief(value):
    """A dict by its keys, anything else the way it is written.

    repr() and not str(): an empty plan, an empty title and a missing
    one all print as nothing, and that is the case these checks mean.
    """
    if isinstance(value, dict):
        return "{%s}" % ", ".join(sorted(value))
    return repr(value)

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
check("program name first", a[0] == "videopodcast_magic.py",
        "1. a[0] is %r, wanted 'videopodcast_magic.py'" % (a[0],))
check("both files there", a[1:3] == ["/x/a.wav", "/x/G.mov"],
        "1. a[1:3] is %s, wanted ['/x/a.wav', '/x/G.mov']" % (a[1:3],))
check("--out behind them", a[3:5] == ["--out", "/out"],
        "1. a[3:5] is %s, wanted ['--out', '/out']" % (a[3:5],))
check("no plan", plan is None,
        "1. plan is %s, wanted None" % brief(plan))
check("no message", m == [],
        "1. %d messages, titles %s, wanted 0"
        % (len(m), [x[1] for x in m]))

print("\n2. Intro, outro and ignoring")
a, _p, _m = vpm.run_argv(values(
    files=[("/x/G.mov", "video"), ("/x/J.mp4", "video"),
             ("/x/O.mp4", "video"), ("/x/away.mov", "video")],
    clip_kinds={"/x/J.mp4": vpm.TYPE_INTRO, "/x/O.mp4": vpm.TYPE_OUTRO,
         "/x/away.mov": vpm.TYPE_IGNORED}))
print("   ", a)
check("only the content file in the list", a[1:2] == ["/x/G.mov"],
        "2. a[1:2] is %s, wanted ['/x/G.mov']" % (a[1:2],))
check("--intro and --outro sorted",
        a[2:6] == ["--intro", "/x/J.mp4", "--outro", "/x/O.mp4"],
        "2. a[2:6] is %s, wanted "
        "['--intro', '/x/J.mp4', '--outro', '/x/O.mp4']" % (a[2:6],))
check("the ignored one is missing", "/x/away.mov" not in a,
        "2. the files on the line are %s, wanted /x/away.mov not among them"
        % ([x for x in a if x.startswith("/x/")],))

print("\n2b. Two files marked as the intro is refused, not silently halved")
# Both would be written into the same --intro and the folder listing would
# decide which one survives. So the run stops and names the two.
a, _p, m = vpm.run_argv(values(
    files=[("/x/G.mov", "video"), ("/x/J.mp4", "video"),
             ("/x/K.mp4", "video")],
    clip_kinds={"/x/J.mp4": vpm.TYPE_INTRO, "/x/K.mp4": vpm.TYPE_INTRO}))
check("rejected", a is None,
        "2b. J.mp4 and K.mp4 both intro gave %s, wanted None" % shown(a))
check("and it says which two", m and "J.mp4" in m[0][2] and "K.mp4" in m[0][2],
        "2b. first message %s, wanted both J.mp4 and K.mp4 named in its text"
        % (m[:1],))
a, _p, m = vpm.run_argv(values(
    files=[("/x/G.mov", "video"), ("/x/J.mp4", "video"),
             ("/x/K.mp4", "video")],
    clip_kinds={"/x/J.mp4": vpm.TYPE_OUTRO, "/x/K.mp4": vpm.TYPE_OUTRO}))
check("the same for the outro", a is None,
        "2b. J.mp4 and K.mp4 both outro gave %s, wanted None" % shown(a))
a, _p, m = vpm.run_argv(values(
    files=[("/x/J.mp4", "video"), ("/x/K.mp4", "video")],
    clip_kinds={"/x/J.mp4": vpm.TYPE_INTRO, "/x/K.mp4": vpm.TYPE_OUTRO}))
check("one of each is fine", a is not None and "--intro" in a,
        "2b. one intro and one outro gave %s, wanted a line carrying --intro"
        % shown(a))

print("\n3. Dry run")
a, _p, _m = vpm.run_argv(values(dry_run=True))
check("--dry-run there", "--dry-run" in a,
        "3. wanted --dry-run on the line, the line is %s" % shown(a))

print("\n4. Multitrack needs at least two recordings")
a, plan, m = vpm.run_argv(values(multitrack=True, key="k", preset="p",
    rows=[{"blocks": ["/x/a.wav"], "speakers": "A",
           "camera_choice": "G.mov"}]))
check("rejected", a is None,
        "4. 1 row where 2 are needed gave %s, wanted None" % shown(a))
check("error named", m and m[0][0] == "error" and "at least two"
        in m[0][2],
        "4. first message %s, wanted one of kind error saying "
        "'at least two'" % (m[:1],))

print("\n5. Names missing")
a, _p, m = vpm.run_argv(values(multitrack=True, key="k", preset="p", rows=[
    {"blocks": ["/x/a.wav"], "speakers": "A", "camera_choice": "G.mov"},
    {"blocks": ["/x/b.wav"], "speakers": " ", "camera_choice": "H.mov"}]))
check("rejected", a is None,
        "5. 2 rows, one of them nameless, gave %s, wanted None" % shown(a))
check("speaker names", m[-1][1] == "Speaker names",
        "5. last title is %r, wanted 'Speaker names'" % (m[-1][1],))

print("\n6. Every row the same name -> only one speaker")
a, _p, m = vpm.run_argv(values(multitrack=True, key="k", preset="p", rows=[
    {"blocks": ["/x/a.wav"], "speakers": "A", "camera_choice": "G.mov"},
    {"blocks": ["/x/b.wav"], "speakers": "A", "camera_choice": "H.mov"}]))
check("rejected", a is None,
        "6. 2 rows both named A gave %s, wanted None" % shown(a))
check("only one speaker", m[-1][1] == "Only one speaker",
        "6. last title is %r, wanted 'Only one speaker'" % (m[-1][1],))

print("\n7. Duplicate name among several -> a question, not an error")
a, plan, m = vpm.run_argv(values(multitrack=True, key="k", preset="p", rows=[
    {"blocks": ["/x/a.wav"], "speakers": "A", "camera_choice": "G.mov"},
    {"blocks": ["/x/b.wav"], "speakers": "A", "camera_choice": "G.mov"},
    {"blocks": ["/x/c.wav"], "speakers": "B", "camera_choice": "H.mov"}],
    cameras=[{"path": "/x/G.mov", "name": "Cam1"},
             {"path": "/x/H.mov", "name": "Cam2"}]))
check("gets through", a is not None,
        "7. rows named A, A, B gave %s, wanted a line" % shown(a))
check("one question", [x[0] for x in m] == ["question"],
        "7. the messages are %s, wanted ['question']"
        % ([x[0] for x in m],))
check("title is right", m[0][1] == "Names used more than once",
        "7. first title is %r, wanted 'Names used more than once'"
        % (m[0][1],))
check("button labelled", m[0][3] == "Merge them",
        "7. button is %r, wanted 'Merge them'" % (m[0][3],))

print("\n8. Ignored rows do not count")
a, _p, m = vpm.run_argv(values(multitrack=True, key="k", preset="p", rows=[
    {"blocks": ["/x/a.wav"], "speakers": "A", "camera_choice": "G.mov"},
    {"blocks": ["/x/b.wav"], "speakers": "B", "camera_choice": "H.mov"},
    {"blocks": ["/x/c.wav"], "speakers": "C",
     "camera_choice": vpm.IGNORE_AUDIO}],
    cameras=[{"path": "/x/G.mov", "name": "Cam1"},
             {"path": "/x/H.mov", "name": "Cam2"}]))
check("gets through", a is not None,
        "8. 2 rows and 1 set aside gave %s, wanted a line" % shown(a))
check("only two tracks in the plan", len(_p["tracks_of"]) == 2,
        "8. %d tracks in the plan, wanted 2" % len(_p["tracks_of"]))
check("the ignored one is missing",
        "C" not in [x["speakers"] for x in _p["tracks_of"]],
        "8. the plan names %s, wanted C not among them"
        % ([x["speakers"] for x in _p["tracks_of"]],))

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
check("--multitrack there", "--multitrack" in a,
        "9. wanted --multitrack on the line, the line is %s" % shown(a))
check("--assign with path",
        a[a.index("--assign") + 1] == "/tmp/assignment.json",
        "9. --assign carries %r, wanted '/tmp/assignment.json'"
        % (a[a.index("--assign") + 1],))
check("--in-point", a[a.index("--in-point") + 1] == "17:00:00:00",
        "9. --in-point carries %r, wanted '17:00:00:00'"
        % (a[a.index("--in-point") + 1],))
check("--out-point", a[a.index("--out-point") + 1] == "18:00:00:00",
        "9. --out-point carries %r, wanted '18:00:00:00'"
        % (a[a.index("--out-point") + 1],))
check("comma becomes a point",
        a[a.index("--min-edit-duration") + 1] == "1.5",
        "9. --min-edit-duration carries %r out of '1,5', wanted '1.5'"
        % (a[a.index("--min-edit-duration") + 1],))
check("defaults for the other sliders",
        all("--" + k in a for k, _b, _v, _e, _kk, _l in vpm.CUT_FIELDS),
        "9. %d of %d cut numbers on the line, missing %s"
        % (len([1 for k, _b, _v, _e, _kk, _l in vpm.CUT_FIELDS
                if "--" + k in a]), len(vpm.CUT_FIELDS),
           [k for k, _b, _v, _e, _kk, _l in vpm.CUT_FIELDS
            if "--" + k not in a] or "none"))
check("--no-wide-edges", "--no-wide-edges" in a,
        "9. wanted --no-wide-edges on the line, the line is %s" % shown(a))
check("key and preset",
        a[a.index("--auphonic-api-key") + 1] == "secret"
        and a[a.index("--auphonic-preset") + 1] == "Preset 1",
        "9. key %r and preset %r, wanted 'secret' and 'Preset 1'"
        % (a[a.index("--auphonic-api-key") + 1],
           a[a.index("--auphonic-preset") + 1]))
check("--auphonic-done",
        a[a.index("--auphonic-done") + 1] == "/out/auphonic-tracks",
        "9. --auphonic-done carries %r, wanted '/out/auphonic-tracks'"
        % (a[a.index("--auphonic-done") + 1],))
check("plan carries the production", plan["production"] == "Interview",
        "9. plan production is %r, wanted 'Interview'" % (plan["production"],))
check("plan carries two cameras", len(plan["cameras"]) == 2,
        "9. %d cameras in the plan, named %s, wanted 2"
        % (len(plan["cameras"]), [c["name"] for c in plan["cameras"]]))
check("camera resolved for the track",
        plan["tracks_of"][0]["camera"] == "/x/G.mov",
        "9. track 1 camera is %r, wanted '/x/G.mov'"
        % (plan["tracks_of"][0]["camera"],))

print("\n10. No number in the slider field")
a, _p, m = vpm.run_argv(values(multitrack=True, key="k", preset="p",
    cut={"min-edit-duration": "lots"},
    rows=[{"blocks": ["/x/a.wav"], "speakers": "A", "camera_choice": "G.mov"},
          {"blocks": ["/x/b.wav"], "speakers": "B", "camera_choice": "H.mov"}],
    cameras=[{"path": "/x/G.mov", "name": "G"},
             {"path": "/x/H.mov", "name": "H"}]))
check("rejected", a is None,
        "10. min-edit-duration 'lots' gave %s, wanted None" % shown(a))
check("says which value", "'lots'" in m[-1][2],
        "10. last text is %r, wanted 'lots' named in it" % (m[-1][2],))

print("\n11. Two cameras, one target name")
a, _p, m = vpm.run_argv(values(multitrack=True, key="k", preset="p",
    rows=[{"blocks": ["/x/a.wav"], "speakers": "A", "camera_choice": "G.mov"},
          {"blocks": ["/x/b.wav"], "speakers": "B", "camera_choice": "H.mov"}],
    cameras=[{"path": "/x/G.mov", "name": "same"},
             {"path": "/x/H.mov", "name": "same"}]))
check("rejected", a is None,
        "11. both cameras named 'same' gave %s, wanted None" % shown(a))
check("file names", m[-1][1] == "File names",
        "11. last title is %r, wanted 'File names'" % (m[-1][1],))

print("\n12. Key without a preset")
a, _p, m = vpm.run_argv(values(key="secret"))
check("rejected", a is None,
        "12. a key and no preset gave %s, wanted None" % shown(a))
check("preset missing", m[-1][1] == "Preset missing",
        "12. last title is %r, wanted 'Preset missing'" % (m[-1][1],))

print("\n13. Multitrack without a key runs locally")
a, plan, m = vpm.run_argv(values(multitrack=True,
    rows=[{"blocks": ["/x/a.wav"], "speakers": "A", "camera_choice": "G.mov"},
          {"blocks": ["/x/b.wav"], "speakers": "B", "camera_choice": "H.mov"}],
    cameras=[{"path": "/x/G.mov", "name": "G"},
             {"path": "/x/H.mov", "name": "H"}]))
check("not rejected", a is not None,
        "13. two rows and no key gave %s, wanted a line; the messages "
        "are %s" % (shown(a), [x[1] for x in m]))
check("--without-auphonic is there", "--without-auphonic" in (a or []),
        "13. wanted --without-auphonic on the line, the line is %s" % shown(a))
check("nothing goes to auphonic.com",
        "--auphonic-api-key" not in (a or []),
        "13. wanted no --auphonic-api-key on the line, the line is %s"
        % shown(a))
check("the assignment is still written", plan is not None,
        "13. plan is %s, wanted an assignment" % brief(plan))

print("\n14. Camera audio only: question first, tracks as camera")
a, plan, m = vpm.run_argv(values(multitrack=True, key="k", preset="p",
    camera_audio_only=True,
    files=[("/x/G.mov", "video"), ("/x/H.mov", "video")],
    rows=[{"blocks": ["/x/G.mov"], "speakers": "A", "camera_choice": "G.mov"},
          {"blocks": ["/x/H.mov"], "speakers": "B", "camera_choice": "H.mov"}],
    cameras=[{"path": "/x/G.mov", "name": "G"},
             {"path": "/x/H.mov", "name": "H"}]))
check("the question comes first", m and m[0][1] == "Cameras only",
        "14. the first of %d messages is %s, wanted the title "
        "'Cameras only'" % (len(m), m[:1]))
check("gets through", a is not None,
        "14. camera audio only gave %s, wanted a line" % shown(a))
check("every track is its own camera",
        all(x["camera_audio"] for x in plan["tracks_of"]),
        "14. camera_audio over %d tracks is %s, wanted all of them true"
        % (len(plan["tracks_of"]),
           [x["camera_audio"] for x in plan["tracks_of"]]))
check("camera points at the audio file",
        plan["tracks_of"][0]["camera"].endswith("G.mov"),
        "14. track 1 camera is %r, wanted a path ending in G.mov"
        % (plan["tracks_of"][0]["camera"],))

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
        "15. track 1 audio_done is %r, wanted '/tmp/done.wav'"
        % (plan["tracks_of"][0].get("audio_done"),))
check("the other row without", "audio_done" not in plan["tracks_of"][1],
        "15. track 2 carries %s, wanted no audio_done among them"
        % (sorted(plan["tracks_of"][1]),))

print("\n16. The interface really calls run_argv")
import inspect
source = inspect.getsource(vpm.gui)
check("call present", "run_argv(values, assign_file)" in source,
        "16. gui() names run_argv in %s, wanted one reading "
        "run_argv(values, assign_file)"
        % ([l.strip() for l in source.splitlines() if "run_argv(" in l]
           or "no line at all",))
# Written out once for the failure line, and once more in the check itself:
# a list read by both would be logic deciding what is tested.
tinkering = ['argv += ["--auphonic-api-key"', '"--multitrack", "--assign"',
             'argv += ["--" + key']
check("no argv tinkering left in gui()",
        'argv += ["--auphonic-api-key"' not in source
        and '"--multitrack", "--assign"' not in source
        and 'argv += ["--" + key' not in source,
        "16. gui() still carries %s of the 3 fragments, wanted none"
        % ([t for t in tinkering if t in source],))
check("the key is still thrown out when saving",
        'if part == "--auphonic-api-key":' in source,
        "16. gui() names --auphonic-api-key in %s, wanted one reading "
        "if part == \"--auphonic-api-key\":"
        % ([l.strip() for l in source.splitlines()
            if "--auphonic-api-key" in l] or "no line at all",))

print("\n17. slider_argv on its own")
t, bad = vpm.slider_argv({})
check("empty values -> all defaults", bad is None
        and len(t) == 2 * (len(vpm.CUT_FIELDS) + len(vpm.CUT_CHOICES)),
        "17. %d words for %d numbers and %d choices, wanted %d; "
        "the field reported as no number is %r"
        % (len(t), len(vpm.CUT_FIELDS), len(vpm.CUT_CHOICES),
           2 * (len(vpm.CUT_FIELDS) + len(vpm.CUT_CHOICES)), bad))
t, bad = vpm.slider_argv({"wide-after": "60"})
check("a set value gets through", t[t.index("--wide-after") + 1] == "60",
        "17. --wide-after carries %r, wanted '60'"
        % (t[t.index("--wide-after") + 1],))
t, bad = vpm.slider_argv({"wide-after": "6,5"})
check("comma becomes point", t[t.index("--wide-after") + 1] == "6.5",
        "17. --wide-after carries %r out of '6,5', wanted '6.5'"
        % (t[t.index("--wide-after") + 1],))
t, bad = vpm.slider_argv({"wide-after": "soon"})
check("a non-number is reported", bad == "wide-after",
        "17. reported %r, wanted 'wide-after'" % (bad,))
check("and the same list is shared with only_resolve_start_run",
        "slider_argv(values)" in source,
        "17. gui() calls slider_argv(values) %d times, wanted at least 1"
        % source.count("slider_argv(values)"))

print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(error) if error else "ALL OK")
sys.exit(1 if error else 0)
