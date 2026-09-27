# -*- coding: utf-8 -*-
"""A cut slider moved in the window works out the cut again, and only that.

The axis, who speaks when and the handover stand on the files and the
assignment; a slider moves none of them. way_ground's project with its
stored separation, offscreen, in this process: the preview left to
stand, then the program's functions of each stage counted while the
shortest shot is moved and the preview stands again. Sections: the
ground (the preview stood; every earlier stage has a watched function
still there), then the cut worked out again, the axis, the speakers and
the handover not. The limit: a stage is watched by its function names.
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
import tempfile
import time
import the_program
import way_ground as ground

began = time.time()
done = 0
bad = []
# The functions of each stage, run's and window's alike: counted from
# the moment the slider moves. A name the program no longer has is
# left out and said; a stage with none left is red.
STAGES = {
    "cut": ("camera_cut",),
    "axis": ("measure_time_axis", "axis_with_blocks",
             "build_common_timebase"),
    "speakers": ("speakers_from_tracks", "speaker_measure_loop",
                 "speakers_for_the_cut", "speakers_all_on_window_axis",
                 "speakers_window_all"),
    "handover": ("build_handover", "handover_of", "write_handover"),
}


def check(name, ok, extra=""):
    """One judgement: a line in the report, and a name in bad if it fell."""
    global done
    done += 1
    print("  %-58s %s %s" % (name, "ok" if ok else "FAIL", extra))
    if not ok:
        bad.append("%s [%s]" % (name, extra or "no numbers"))


def stop():
    """Nothing further can be asked, so count what there is and go."""
    print("\n%d checks in %.2f s" % (done, time.time() - began))
    print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
    sys.exit(1 if bad else 0)


if ground.missing():
    print("SKIPPED: " + ground.missing())
    stop()

# The model and the words are stood in for; the store and Resolve's
# interface are this test's own, so nothing outside answers.
os.environ.pop("VPM_NO_SPEAKER_SPLIT", None)
STORE = tempfile.mkdtemp(prefix="vpm_slider_store_")
NOWHERE = os.path.join(STORE, "no-resolve-here")
os.environ.update(VPM_CACHE=STORE, QT_QPA_PLATFORM="offscreen",
                  RESOLVE_SCRIPT_API=NOWHERE, RESOLVE_SCRIPT_LIB=os.path
                  .join(NOWHERE, "fusionscript.so"))
from PySide6 import QtWidgets
app = QtWidgets.QApplication(sys.argv[:1])
vpm = the_program.load()
vpm.set_language("en")
vpm.list_presets = lambda key: []
vpm.load_api_key = lambda: ""
vpm.speaker_split_run = lambda *a, **k: ([], "")
vpm.speaker_split_available = lambda deep=False: True
vpm.SPEAKER_SPLIT_OFF = False
vpm.words_at_hand = lambda *a, **k: []
vpm.recognise_speech = lambda *a, **k: ([], "")

WORK = ground.own_folder("slider")
OUT = os.path.join(WORK, "out")
os.makedirs(OUT)
os.makedirs(os.path.join(WORK, "project"))
PROJECT = ground.project_file(vpm, os.path.join(WORK, "project"), OUT)
counts = {}
watched = dict((stage, [n for n in names if callable(getattr(vpm, n, None))])
               for stage, names in STAGES.items())
seen = {"n": 0, "last": None, "since": 0.0, "before": None, "moved": None}


def counted(name, real):
    """*real*, counting its calls under *name* once counting is on."""
    def wrapper(*a, **k):
        """Count, then hand on."""
        if seen["moved"] is not None:
            counts[name] = counts.get(name, 0) + 1
        return real(*a, **k)
    return wrapper


# Bent on the program: a name bent there is written through into every
# piece that holds it.
for names in watched.values():
    for name in names:
        setattr(vpm, name, counted(name, getattr(vpm, name)))


def look(w):
    """The preview now: its cut, and whether speakers are being measured."""
    st = w.resolve_sheet.state
    return (id(st.get("cut_numbers")),
            len((st.get("cut_numbers") or {}).get("cut") or []),
            bool(st.get("speakers_measuring")))


def standing(w):
    """Whether the preview has a cut and has not moved for 1.5 s."""
    now = look(w)
    if now != seen["last"]:
        seen["last"], seen["since"] = now, time.time()
    return now[1] > 0 and not now[2] and time.time() - seen["since"] > 1.5


def answer(w):
    """Let the preview stand, move the slider, let it stand again."""
    if w is None:
        return "the window"
    at = [k for k in range(w.tabs.count())
          if w.tabs.tabText(k).startswith(vpm.T('Resolve cut'))]
    if not at:
        return "the Resolve cut tab"
    if seen["n"] == 0:
        w.tabs.setCurrentIndex(at[0])
        seen["n"] = 1
        return "the preview standing"
    if seen["n"] == 1:
        if not standing(w):
            return "the preview standing"
        seen["before"] = look(w)
        var = w.resolve_sheet.cut_var["min-edit-duration"]
        was = float(var.get())
        seen["moved"] = (was, was + 0.5)
        seen["n"] = 2
        var.set(str(was + 0.5))
        return "the preview working the cut out again"
    if not counts.get("camera_cut") or not standing(w):
        return "the preview working the cut out again"
    return ""


keep = ground.window_answered_run(vpm, app, PROJECT, {}, answer, run=False)
shutil.rmtree(WORK, ignore_errors=True)
shutil.rmtree(STORE, ignore_errors=True)


def stage_line(stage):
    """The calls counted in *stage* after the slider moved, by name."""
    if seen["moved"] is None:
        return "the slider never moved, so nothing was counted"
    return "%s; shortest shot %s s" % (", ".join(
        "%s %d" % (n, counts.get(n, 0)) for n in watched[stage])
        or "no function of this stage watched",
        " -> ".join("%.1f" % x for x in seen["moved"]))


def calls(stage):
    """How many calls *stage* had after the slider moved; None if it never.

    A slider that never moved counted nothing, and nothing is no answer.
    """
    if seen["moved"] is None:
        return None
    return sum(counts.get(n, 0) for n in watched[stage])


print("The ground")
check("the preview stands before the slider moves",
      seen["before"] is not None and seen["before"][1] > 0,
      "%s shots before the slider moved; %s" % (
          seen["before"][1] if seen["before"] else "no",
          keep["unanswered"] or keep["why"] or "stood"))
gone = ["%s: none of %s" % (stage, ", ".join(STAGES[stage]))
        for stage in ("axis", "speakers", "handover") if not watched[stage]]
check("every earlier stage still has a function this test watches",
      not gone, "; ".join(gone) or ", ".join(
          "%s %d of %d" % (stage, len(watched[stage]), len(STAGES[stage]))
          for stage in ("axis", "speakers", "handover")))

print("\nAfter the slider moved")
check("a slider change works the cut out again", (calls("cut") or 0) > 0,
      stage_line("cut"))
check("a slider change measures no time axis again", calls("axis") == 0,
      stage_line("axis"))
check("a slider change leaves who speaks when as it stood",
      calls("speakers") == 0, stage_line("speakers"))
check("a slider change builds no handover again", calls("handover") == 0,
      stage_line("handover"))
stop()
