# -*- coding: utf-8 -*-
"""The preview's own run says nothing, and a Start stops it, not waits.

The preview is a dry run in a thread of the window's; its lines would
land in the log beside a run somebody started. way_ground's project
with its stored separation, offscreen, in this process, its output read
from the start: the preview's run stood and kept its handover, then a
moved In point sets a second one going, held in a real ffmpeg child of
SLOW_S s, the In point moves again and Start is pressed. Sections: the
ground; nothing of it written out; Start stopping it -- the child ended,
Start's run begun early yet after it, nothing kept, the stop taken back.
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
# Every dry run says this last; the preview's run is a dry run.
SAID_LAST = vpm.T('\n  (measuring only: nothing written)').strip()
# The second preview's run is held this long in its levels mix, by a
# real child the run's own stop has to reach.
SLOW_S = 120

WORK = ground.own_folder("quiet")
OUT = os.path.join(WORK, "out")
os.makedirs(OUT)
os.makedirs(os.path.join(WORK, "project"))
PROJECT = ground.project_file(vpm, os.path.join(WORK, "project"), OUT)
seen = {"n": 0, "ran": None, "pressed_while": False, "at_start": None,
        "heard_before_start": None, "slow": "", "slow_took": None,
        "pressed_at": None, "began_at": None, "keys": [], "told": {}}
real_loop = vpm.gui_run_loop
real_mix = vpm.timebase.mix_tracks


def loop(argv, state, *rest):
    """The window's run loop: how things stood the moment it began."""
    seen["began_at"] = time.time()
    seen["at_start"] = bool(state.get("preview_running"))
    seen["heard_before_start"] = "".join(HEARD.text)
    return real_loop(argv, state, *rest)


def mix_slowly(*a, **k):
    """The levels mix, once held SLOW_S s by a child the stop can end."""
    if seen["slow"] == "wanted":
        seen["slow"], began_here = "going", time.time()
        try:
            vpm.run_ffmpeg_with_progress(
                ["ffmpeg", "-v", "error", "-re", "-f", "lavfi", "-i",
                 "anullsrc=r=8000:cl=mono", "-t", str(SLOW_S), "-f",
                 "null", os.path.join(STORE, "held")], SLOW_S, "held")
            seen["slow"] = "ran out"
        except vpm.Stopped:
            seen["slow"] = "stopped"
            raise
        finally:
            seen["slow_took"] = time.time() - began_here
    return real_mix(*a, **k)


vpm.gui_run_loop = loop
vpm.timebase.mix_tracks = mix_slowly


def runs_watched(st):
    """The preview's runs, with the key each stands for and what it told."""
    real = st["preview_run"]

    def run(request, done):
        """Keep the key, and the stop as it stood when the run told."""
        seen["keys"].append(request["key"])

        def told(result):
            """Keep what the run handed back, then hand it on."""
            seen["told"][request["key"]] = (
                result, vpm.RUN_STOP["wanted"])
            return done(result)

        return real(request, told)

    st["preview_run"] = run


def answer(w):
    """A preview's run stands; a second is held; settings move; press."""
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
        runs_watched(st)
        seen["slow"] = "wanted"
        w.assignment_sheet.model.in_point.set("+0:00:02")
        seen["n"] = 2
        return "the second preview's run held"
    if not (st.get("preview_running") and seen["slow"] == "going"):
        return "the second preview's run held"
    # Its settings change again: the run going is for the old ones.
    w.assignment_sheet.model.in_point.set("+0:00:03")
    seen["pressed_while"], seen["pressed_at"] = True, time.time()
    return ""


keep = ground.window_answered_run(vpm, app, PROJECT, {}, answer)
sys.stdout = HEARD.inner
held_key = seen["keys"][0] if seen["keys"] else None
kept_after = vpm.stage_get(held_key) if held_key else None
shutil.rmtree(WORK, ignore_errors=True)
shutil.rmtree(STORE, ignore_errors=True)

print("The ground")
check("the preview's run ended and its cut stood", bool(seen["ran"]),
      "kept under %s; %s" % (seen["ran"], keep["unanswered"] or keep["why"]
                             or "stood"))
check("Start came while a second preview's run went",
      seen["pressed_while"] and seen["at_start"] is not None,
      "pressed while it went: %s; the run began: %s; %s"
      % (seen["pressed_while"], seen["at_start"] is not None,
         keep["unanswered"] or keep["why"] or "stood"))

print("\nNothing of it written out")
before = seen["heard_before_start"] or ""
check("no line of the preview's runs reached the output",
      bool(seen["ran"]) and SAID_LAST not in before,
      "%d characters written before Start's run, %r among them: %s"
      % (len(before), SAID_LAST, SAID_LAST in before))

print("\nA Start stops it")
check("the held preview's child was ended by Start's stop",
      seen["slow"] == "stopped",
      "the held step %s after %s s of %d s"
      % (seen["slow"] or "never began", "%.1f" % seen["slow_took"]
         if seen["slow_took"] is not None else "-", SLOW_S))
waited = (seen["began_at"] - seen["pressed_at"]
          if seen["began_at"] and seen["pressed_at"] else None)
check("Start's run began before the held preview's could end",
      waited is not None and waited < SLOW_S,
      "Start's run began %s s after the press, the held step lasts %d s"
      % ("%.1f" % waited if waited is not None else "never", SLOW_S))
check("and its run begins only once the preview's run has ended",
      seen["at_start"] is False,
      "a preview's run still going when Start's run began: %s"
      % seen["at_start"])
told, standing = seen["told"].get(held_key, (None, None))
check("the stopped run tells the tab that nothing ran",
      told == (None, 0, ""),
      "it handed back %r" % (told,))
check("nothing was kept for the stopped run's settings",
      held_key is not None and kept_after is None,
      "key %s; kept under it: %s"
      % (held_key and held_key[:12], "nothing" if kept_after is None
         else "a handover of %d keys" % len(kept_after)))
check("the preview's stop is taken back once its run ended",
      told is not None and standing is False,
      "the run's stop still wanted when it told: %s" % standing)
stop()
