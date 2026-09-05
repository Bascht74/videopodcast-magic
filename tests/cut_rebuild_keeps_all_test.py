# -*- coding: utf-8 -*-
"""Rebuilding the cut list keeps every setting the run was given.

The button builds a stand-in for the sliders out of the stored command
line, so a whole class of fault sits here: a switch the window wrote is
not read back and falls out without a word. First that a cut was built
at all, then the wide shot mark, the cut numbers, the reaction gap and
hold no field in the window carries, the loudness, the choices, the
tick for the edges, the file that puts a voice on its own camera, and
the time window. write_cut_list is wrapped, not replaced: the cut is
the real one, and the settings are read where the run reads them.
"""
import os
import the_program
HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = the_program.SCRIPT
import contextlib, io, json, sys, tempfile, time
vpm = the_program.load()
vpm.set_language("en")
WORK = tempfile.mkdtemp(prefix="rebuildkeeps_")
began = time.time()
done = 0
bad = []


def check(name, ok, extra=""):
    global done
    done += 1
    print("  %-58s %s %s" % (name, "ok" if ok else "FAIL", extra))
    if not ok:
        bad.append("%s [%s]" % (name, extra or "no numbers"))


# ------------------------------------------------------------ the ground
# Three cameras: nobody sits in front of Wide, so without a mark it is
# the wide shot. A and B take one speaker each and alternate every five
# seconds over the whole axis.
ZERO = 68100.0                                            # 18:55:00:00
a_speaks, b_speaks, at = [], [], 0.0
while at < 300.0:
    a_speaks.append([round(at, 3), round(at + 5.0, 3)])
    b_speaks.append([round(at + 5.0, 3), round(at + 10.0, 3)])
    at += 10.0
STALE = [{"start": 0.0, "end": 300.0, "camera": "Wide"}]
folder = os.path.join(WORK, "cut")
os.makedirs(folder)
video = {}
for who in ("Wide", "A", "B"):
    video[who] = os.path.join(folder, who + ".mov")
    with open(video[who], "w") as handle:
        handle.write("x")

# The values the run was given. Every one of them differs from the
# built-in default, so a setting that is not read back cannot come out
# right by accident.
CALL = ["--wide-shot", video["A"], "--wide-shot", video["B"],
        "--min-edit-duration", "4.5", "--min-speech-to-switch", "2.5",
        "--edit-change-delay", "0.9", "--reaction-lead", "5",
        "--wide-after", "40", "--wide-latest", "95",
        "--wide-length", "7", "--wide-most", "11",
        "--reaction-gap", "8", "--reaction-hold", "1.4",
        "--lufs", "-16",
        "--on-question", vpm.SHOT_LISTENER,
        "--on-monologue", vpm.SHOT_LISTENER,
        "--on-together", vpm.SHOT_HOLD,
        "--on-uncertain", vpm.SHOT_LISTENER]
UNMARKED = [x for x in CALL
            if x not in ("--wide-shot", video["A"], video["B"])]

# The real write_cut_list is wrapped, not replaced: the cut is built by
# the program, and the wrapper only keeps the settings object the
# button handed it, so the recovered values can be read where the run
# reads them.
seen = []
_real_write_cut_list = vpm.write_cut_list


def recorder(args, *a, **k):
    seen.append(args)
    return _real_write_cut_list(args, *a, **k)


vpm.write_cut_list = recorder


def press(call, window=None, on_camera=None, heard=None):
    """Put the call in the project file and press "Rebuild cut list".

    *on_camera* says which track names the handover gives each camera,
    *heard* who was heard when. Returns (the reason it refused or None,
    the rebuilt cut, the settings the cut was built from, what the
    button printed).
    """
    cams = []
    for who, speaks in (on_camera
                        or (("Wide", []), ("A", ["A"]), ("B", ["B"]))):
        cams.append({"camera": who, "source": video[who],
                     "file": video[who], "track": who,
                     "speakers": speaks, "offset": 0.0})
    d = {"production": "Test", "start_s": ZERO, "fps": 30,
         "fps_measured": 30.0, "start_tc": "18:55:00:00",
         "length_s": 300.0,
         "in_point": (window or (None, None))[0],
         "out_point": (window or (None, None))[1],
         "speakers": [{"name": n, "sections": s} for n, s in
                      (heard or (("A", a_speaks), ("B", b_speaks)))],
         "cameras": cams, "cut": list(STALE)}
    with open(os.path.join(folder, "videopodcast-magic_Test.json"),
              "w", encoding="utf-8") as f:
        json.dump({"production": "Test", "call": call}, f)
    path = os.path.join(folder, "Test_resolve.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(d, f)
    del seen[:]
    said = io.StringIO()
    kept, sys.argv[1:] = sys.argv[1:], []
    try:
        with contextlib.redirect_stdout(said):
            reason = vpm.refresh_cut_list(d, path)
    finally:
        sys.argv[1:] = kept
    return (reason, d.get("cut") or [], seen[-1] if seen else None,
            said.getvalue())


def cameras_in(cut):
    return sorted({shot["camera"] for shot in cut})


def opens(cut):
    """The camera of the first shot, or None where no cut was built.

    None rather than an exception: a cut that stayed empty is what the
    first judgement is about, and the ones under it should still be
    printed instead of the run ending in a traceback.
    """
    return cut[0]["camera"] if cut else None


def shown_at(cut, second):
    """Which camera the cut shows at that second, or None."""
    for shot in cut:
        if shot["start"] <= second < shot["end"]:
            return shot["camera"]
    return None


# The window heard a second voice inside one recording and put it on a
# camera of its own. Only the assignment file says so: the handover
# gives camera B no track, so without that file Ben belongs nowhere and
# the cut falls back to the wide shot for him. BEN_SPEAKS is a second
# inside one of his stretches, far from both wide shot edges.
VOICE_APART = (("Wide", []), ("A", ["A"]), ("B", []))
BEN_HEARD = (("A", a_speaks), ("Ben", b_speaks))
BEN_SPEAKS = 157.5


def a_plan(name):
    """An assignment file as the window writes it, naming Ben's camera."""
    path = os.path.join(folder, name)
    with open(path, "w", encoding="utf-8") as f:
        json.dump({"format": vpm.FILE_FORMAT, "created_by": "test",
                   "voices_of": {"Ben": video["B"]}}, f)
    return path


try:
    plain_r, plain_cut, _plain_set, _plain_log = press(UNMARKED)
    full_r, full_cut, settings, full_log = press(CALL)
    off_r, off_cut, off_set, _off_log = press(UNMARKED + ["--no-wide-edges"])
    quiet_call = list(CALL)
    quiet_call[quiet_call.index("--lufs"):
               quiet_call.index("--lufs") + 2] = []
    quiet_r, _quiet_cut, quiet_set, _quiet_log = press(quiet_call)
    moved_r, _moved_cut, _moved_set, _moved_log = press(
        CALL + ["--in-point", "19:00:00:00"],
        window=("18:55:30:00", "18:59:00:00"))
    assign_r, assign_cut, _assign_set, _assign_log = press(
        UNMARKED + ["--multitrack", "--assign", a_plan("assign.json")],
        on_camera=VOICE_APART, heard=BEN_HEARD)
    from_r, from_cut, _from_set, _from_log = press(
        UNMARKED + ["--speakers-from", a_plan("speakers_from.json")],
        on_camera=VOICE_APART, heard=BEN_HEARD)
finally:
    vpm.write_cut_list = _real_write_cut_list

# The four runs that should build a cut have to have built one, or every
# judgement below is about an empty list.
check("the button builds a cut from every call it was given",
      bool(plain_cut) and bool(full_cut) and bool(off_cut)
      and settings is not None and off_set is not None
      and quiet_set is not None,
      "shots %d/%d/%d, settings %s, refusals %r/%r/%r/%r"
      % (len(plain_cut), len(full_cut), len(off_cut),
         "/".join("none" if s is None else "there"
                  for s in (settings, off_set, quiet_set)),
         plain_r, full_r, off_r, quiet_r))

# ------------------------------------------------------- the wide shot mark
check("without the mark the camera nobody sits on opens the cut",
      opens(plain_cut) == "Wide",
      "%r against 'Wide' asked for, cameras %s"
      % (opens(plain_cut), cameras_in(plain_cut)))
check("with the mark the marked camera opens the cut",
      opens(full_cut) == "A",
      "%r against 'A' asked for, cameras %s"
      % (opens(full_cut), cameras_in(full_cut)))
check("and the unmarked camera is no wide shot any more",
      "Wide" not in cameras_in(full_cut),
      "cameras %s against wanted without 'Wide'" % cameras_in(full_cut))
check("both marks come back, not only the first",
      vpm.marked_wide_shots(settings)
      == {vpm.path_key(video["A"]), vpm.path_key(video["B"])},
      "%d marks %s against 2 asked for"
      % (len(vpm.marked_wide_shots(settings)),
         sorted(os.path.basename(p)
                for p in vpm.marked_wide_shots(settings))))
check("and the rebuild says it has two wide shots, not one",
      (vpm.T('  %s wide shots: the cut uses %s.')
       % (vpm.group_text(2), "A")) in full_log,
      "wanted the line for 2 wide shots, cut cameras %s"
      % cameras_in(full_cut))

# ------------------------------------------------------------ the cut numbers
# Some of them write_cut_list reads straight off the settings, the rest
# through rules_from_settings; each is read here where the run reads it,
# so a number that arrives but is never passed on still shows up.
rules = vpm.rules_from_settings(settings)
min_edit = getattr(settings, "min_edit_duration", None)
check("the minimum edit duration comes back as it was given",
      min_edit == 4.5, "%r against 4.5 s asked for" % min_edit)
min_speech = rules.get("min_speech")
check("how long somebody must speak comes back as it was given",
      min_speech == 2.5, "%r against 2.5 s asked for" % min_speech)
delay = getattr(settings, "delay", None)
check("the edit change delay comes back as it was given",
      delay == 0.9, "%r against 0.9 s asked for" % delay)
lead = rules.get("reaction_lead")
check("the answer lead comes back as it was given",
      lead == 5.0, "%r against 5.0 s asked for" % lead)
after = getattr(settings, "wide_after", None)
check("when the wide shot starts comes back as it was given",
      after == 40.0, "%r against 40.0 s asked for" % after)
latest = getattr(settings, "wide_latest", None)
check("the latest wide shot comes back as it was given",
      latest == 95.0, "%r against 95.0 s asked for" % latest)
holds = rules.get("wide_holds")
check("the shortest wide shot comes back as it was given",
      holds == 7.0, "%r against 7.0 s asked for" % holds)
most = rules.get("wide_most")
check("the longest wide shot comes back as it was given",
      most == 11.0, "%r against 11.0 s asked for" % most)

# ------------------------------- the two numbers the window has no field for
gap = rules.get("reaction_gap")
check("the reaction gap comes back as it was given, not the default",
      gap == 8.0, "%r against 8.0 s asked for" % gap)
hold = rules.get("reaction_hold")
check("the reaction hold comes back as it was given, not the default",
      hold == 1.4, "%r against 1.4 s asked for" % hold)

# ---------------------------------------------------------------- loudness
loud = getattr(settings, "lufs", None)
check("the loudness comes back as it was given",
      loud == -16.0, "%r against -16.0 LUFS asked for" % loud)
quiet = getattr(quiet_set, "lufs", 0.0)
check("no loudness in the call stays no loudness",
      quiet is None, "%r against None asked for" % quiet)

# ------------------------------------------------------- the four choices
question = rules.get("on_question")
check("the choice after a question comes back as it was set",
      question == vpm.SHOT_LISTENER,
      "%r against %r asked for" % (question, vpm.SHOT_LISTENER))
monologue = rules.get("on_monologue")
check("the choice for a long monologue comes back as it was set",
      monologue == vpm.SHOT_LISTENER,
      "%r against %r asked for" % (monologue, vpm.SHOT_LISTENER))
together = rules.get("on_together")
check("the choice for several speaking at once comes back as it was set",
      together == vpm.SHOT_HOLD,
      "%r against %r asked for" % (together, vpm.SHOT_HOLD))
uncertain = rules.get("on_uncertain")
check("the choice where recognition frays comes back as it was set",
      uncertain == vpm.SHOT_LISTENER,
      "%r against %r asked for" % (uncertain, vpm.SHOT_LISTENER))

# ---------------------------------------------------------------- the tick
check("the tick against the wide shot edges reaches the cut",
      "Wide" not in cameras_in(off_cut),
      "cameras %s against wanted without 'Wide', tick read as %r"
      % (cameras_in(off_cut), getattr(off_set, "no_wide_edges", None)))

# ------------------------------------------- the file that places a voice
check("a voice --assign placed is on its camera after the rebuild",
      shown_at(assign_cut, BEN_SPEAKS) == "B",
      "%r at %.1f s against 'B' asked for, %d shots on %s"
      % (shown_at(assign_cut, BEN_SPEAKS), BEN_SPEAKS, len(assign_cut),
         cameras_in(assign_cut)))
check("a voice --speakers-from placed is on its camera too",
      shown_at(from_cut, BEN_SPEAKS) == "B",
      "%r at %.1f s against 'B' asked for, %d shots on %s"
      % (shown_at(from_cut, BEN_SPEAKS), BEN_SPEAKS, len(from_cut),
         cameras_in(from_cut)))

# --------------------------------------------------------- the time window
check("the In point in the stored call is still read back",
      "19:00:00:00" in (moved_r or ""),
      "refused with %r, wanted the In point 19:00:00:00 named"
      % (moved_r or ""))

print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
