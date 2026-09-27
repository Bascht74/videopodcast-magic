# -*- coding: utf-8 -*-
"""The preview's own run says nothing, and a Start waits until it ends.

The preview is a dry run in a thread of the window's; its lines would
land in the log beside a run somebody started. way_ground's project
with its stored separation, offscreen, in this process, its output read
from the start: the preview's run stood and kept its handover, then
Start is pressed while a second preview's run -- set going by a moved
In point -- still goes. Sections: the ground (the preview's run ended
and stood; Start came while one went); nothing of it written out; Start
saying it waits, and its run beginning only once the preview's ended.
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


class Heard(object):
    """The process's output, handed on and kept, until told to stop."""

    def __init__(self, inner):
        """Pass on to *inner*, keeping a copy while listening."""
        self.inner, self.text, self.on = inner, [], True

    def write(self, text):
        """Keep, then hand on."""
        if self.on:
            self.text.append(str(text))
        return self.inner.write(text)

    def __getattr__(self, name):
        """Everything else is the real output's."""
        return getattr(self.inner, name)


HEARD = Heard(sys.stdout)
sys.stdout = HEARD
# The store and Resolve's interface are this test's own.
os.environ.pop("VPM_NO_SPEAKER_SPLIT", None)
STORE = tempfile.mkdtemp(prefix="vpm_quiet_store_")
NOWHERE = os.path.join(STORE, "no-resolve-here")
os.environ.update(VPM_CACHE=STORE, QT_QPA_PLATFORM="offscreen",
                  RESOLVE_SCRIPT_API=NOWHERE, RESOLVE_SCRIPT_LIB=os.path
                  .join(NOWHERE, "fusionscript.so"))
from PySide6 import QtCore, QtWidgets
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
# Every dry run says this last; the preview's run is a dry run.
SAID_LAST = vpm.T('\n  (measuring only: nothing written)').strip()
WAITS = vpm.T('Preview running ...')

WORK = ground.own_folder("quiet")
OUT = os.path.join(WORK, "out")
os.makedirs(OUT)
os.makedirs(os.path.join(WORK, "project"))
PROJECT = ground.project_file(vpm, os.path.join(WORK, "project"), OUT)
seen = {"n": 0, "ran": None, "pressed_while": False, "button": [],
        "at_start": None, "heard_before_start": None}
real_loop = vpm.gui_run_loop


def loop(argv, state, *rest):
    """The window's run loop: how things stood the moment it began."""
    seen["at_start"] = bool(state.get("preview_running"))
    seen["heard_before_start"] = "".join(HEARD.text)
    return real_loop(argv, state, *rest)


vpm.gui_run_loop = loop


def button_text(w):
    """What the Start button says, kept every tenth of a second."""
    if w is not None:
        seen["button"].append(w.start_run.text())


def answer(w):
    """Let a preview's run stand, move the In point, press on its run."""
    if w is None:
        return "the window"
    st = w.resolve_sheet.state
    at = [k for k in range(w.tabs.count())
          if w.tabs.tabText(k).startswith(vpm.T('Resolve cut'))]
    if not at:
        return "the Resolve cut tab"
    if seen["n"] == 0:
        w.tabs.setCurrentIndex(at[0])
        seen["n"] = 1
    if seen["n"] == 1:
        if not (st.get("cut_numbers") and st.get("preview_ran")
                and not st.get("preview_running")):
            return "the preview's run standing"
        seen["ran"] = st.get("preview_ran")
        watch = QtCore.QTimer(w)
        watch.timeout.connect(lambda: button_text(w))
        watch.start(100)
        seen["watch"] = watch
        w.assignment_sheet.model.in_point.set("+0:00:02")
        seen["n"] = 2
        return "the second preview's run going"
    if not st.get("preview_running"):
        return "the second preview's run going"
    seen["pressed_while"] = True
    return ""


keep = ground.window_answered_run(vpm, app, PROJECT, {}, answer)
sys.stdout = HEARD.inner
shutil.rmtree(WORK, ignore_errors=True)
shutil.rmtree(STORE, ignore_errors=True)

print("The ground")
check("the preview's run ended and its cut stood", bool(seen["ran"]),
      "kept under %s; %s" % (seen["ran"], keep["unanswered"] or keep["why"]
                             or "stood"))
check("Start came while a second preview's run went",
      seen["pressed_while"] and seen["at_start"] is not None,
      "pressed while it went: %s; the run began: %s"
      % (seen["pressed_while"], seen["at_start"] is not None))

print("\nNothing of it written out")
before = seen["heard_before_start"] or ""
check("no line of the preview's runs reached the output",
      bool(seen["ran"]) and SAID_LAST not in before,
      "%d characters written before Start's run, %r among them: %s"
      % (len(before), SAID_LAST, SAID_LAST in before))

print("\nA Start waits for it")
check("the Start button says it waits for the preview's run",
      WAITS in seen["button"],
      "the button said %s" % sorted(set(seen["button"])))
check("and its run begins only once the preview's run has ended",
      seen["at_start"] is False,
      "a preview's run still going when Start's run began: %s"
      % seen["at_start"])
stop()
