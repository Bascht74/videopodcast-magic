# -*- coding: utf-8 -*-
"""After Start the preview shows the run's handover, not its own dry run.

The preview keeps its dry run of the window's line under a key of that
line; a run of the same line that ends later wrote the newer handover.
In order: the kept dry run shown before any run, a run of other numbers
leaving it standing, a run of the same line -- auphonic.com asked, as a
Start asks it -- putting the preview out of date and shown with the
finished run's label, "Create Resolve project" after it keeping the
run's, and a dry run of the same line afterwards taking the kept one
back. The window's run loop with main stood in for, without a window.
"""
PLATFORM_BOUND = True
import contextlib
import io
import json
import os
import queue
import shutil
import sys
import tempfile
import time
import types
# tests/, where the helpers and state/ lie; this file may stand in a
# folder under it, or in one under that.
HERE = os.path.dirname(os.path.abspath(__file__))
while not os.path.isfile(os.path.join(HERE, "the_program.py")) \
        and os.path.dirname(HERE) != HERE:
    HERE = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import the_program

WORK = tempfile.mkdtemp(prefix="vpm_runkept_")
os.environ["VPM_CACHE"] = os.path.join(WORK, "cache")
vpm = the_program.load()
vpm.set_language("en")
ui = vpm.window()

began = time.time()
done = 0
bad = []


def check(name, ok, extra=""):
    global done
    done += 1
    print("  %-58s %s %s" % (name, "ok" if ok else "FAIL", extra))
    if not ok:
        bad.append("%s [%s]" % (name, extra or "no numbers"))


A, B = [os.path.join(WORK, n) for n in ("A_Presenter.mov", "B_Guest.mov")]
for p in (A, B):
    open(p, "wb").close()


def handover(name, said):
    """A stand-in handover file carrying a word saying where it came from."""
    path = os.path.join(WORK, name)
    with open(path, "w", encoding="utf-8") as f:
        json.dump({"came_from": said, "cut": [], "speakers": [],
                   "cameras": []}, f)
    return path


RUN_FILE = handover("Episode_resolve.json", "the run of these numbers")
OTHER_FILE = handover("Other_resolve.json", "a run of other numbers")
# The preview's line goes without auphonic.com; Start's asks it.
PREVIEW = ["vpm", A, B, "--lufs", "-16", "--without-auphonic",
           "--min-edit-duration", "2.0"]
START = ["vpm", A, B, "--lufs", "-16", "--auphonic-preset", "Preset",
         "--min-edit-duration", "2.0"]
OTHER = ["vpm", A, B, "--lufs", "-16", "--auphonic-preset", "Preset",
         "--min-edit-duration", "2.5"]
KEY = vpm.handover_key(*vpm.line_words(PREVIEW))
vpm.stage_put(KEY, {"came_from": "the preview's dry run", "cut": [],
                    "speakers": [], "cameras": []})

state = {"handover_key": KEY, "results": [], "running": False,
         "dry_run": False}


def run(argv, writes):
    """One run through the window's loop; main says it wrote *writes*."""
    def main():
        """The run: says what it wrote, and ends well."""
        if writes:
            print(writes)
        return 0
    ui.main = main
    state["results"], state["running"] = [], True
    kept_argv = sys.argv[:]
    with contextlib.redirect_stdout(io.StringIO()):
        ui.gui_run_loop(list(argv), state,
                        ui.make_log_writer(state, queue.Queue()),
                        lambda *a: None,
                        types.SimpleNamespace(run_step=None),
                        lambda *a: None, [])
    sys.argv[:] = kept_argv


def shown():
    """What the preview reads now, by its word, and it marked as shown."""
    d = vpm.preview_handover(state)
    state["statistics"] = {"n": 1}
    return (d or {}).get("came_from")


def label():
    """The line the preview writes over the cut: what it stands on."""
    return vpm.cut_basis_line(state.get("cut_basis"), 2, 60.0)[0]


print("1. Before any run")
got = shown()
check("before any run the preview shows its kept dry run",
      got == "the preview's dry run",
      "read %r, wanted the preview's dry run" % got)

print("\n2. A run of other cut numbers")
run(OTHER, OTHER_FILE)
got = shown()
check("a run of other numbers leaves the kept dry run shown",
      got == "the preview's dry run",
      "read %r after a run of other numbers, wanted the preview's dry run"
      % got)

print("\n3. Start with the same numbers")
run(START, RUN_FILE)
stale = vpm.preview_out_of_date(state)
check("a run of the same line puts the preview out of date",
      stale is True, "answered %r with the dry run shown" % stale)
got = shown()
check("after a run of the same line the preview shows the run's",
      got == "the run of these numbers",
      "read %r, wanted the run of these numbers" % got)
check("the preview then says it stands on the finished run",
      label() == vpm.cut_basis_line("run", 2, 60.0)[0],
      "says %r, cut_basis %r" % (label(), state.get("cut_basis")))
stale = vpm.preview_out_of_date(state)
check("the run's handover once shown is not out of date again",
      stale is False, "answered %r, shown from %r"
      % (stale, state.get("preview_from")))

print("\n4. Create Resolve project after it")
run(["vpm", "--resolve-json", RUN_FILE, "--min-edit-duration", "2.0"],
    RUN_FILE)
got = shown()
check("Create Resolve project afterwards keeps the run's shown",
      got == "the run of these numbers",
      "read %r, wanted the run of these numbers" % got)

print("\n5. A dry run of the same line afterwards")
vpm.stage_put(KEY, {"came_from": "a later dry run", "cut": [],
                    "speakers": [], "cameras": []})
run(START + ["--dry-run"], None)
got = shown()
check("a dry run of the same line afterwards is shown again",
      got == "a later dry run", "read %r, wanted a later dry run" % got)

shutil.rmtree(WORK, ignore_errors=True)
print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
