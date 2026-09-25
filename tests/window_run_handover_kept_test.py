# -*- coding: utf-8 -*-
"""A run's handover that left a camera out comes back with the camera.

The run refuses a camera it cannot place, so its handover names two of
the three cameras in the list. Taking one out and putting it back must
not lose it: no search finds it, since it names these cameras less one.
In order: the run's handover taken up, a camera out, the camera back,
one naming a camera the list does not hold never given back to it, and
none given back from a folder the search no longer looks in.
The window's own functions, the run loop included, without a window.
"""
import io
import json
import os
import queue
import shutil
import sys
import tempfile
import time
import types
import contextlib
import the_program

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


folder = tempfile.mkdtemp(prefix="vpm_kept_")
out = os.path.join(folder, "Run")
os.makedirs(out)
A, B, C = [os.path.join(folder, n) for n in
           ("A_Presenter.mov", "B_Guest.mov", "C_WideCam.mov")]
for p in (A, B, C):
    open(p, "wb").close()
HANDOVER = os.path.join(out, "Episode_resolve.json")
with open(HANDOVER, "w", encoding="utf-8") as f:
    json.dump({"format": vpm.FILE_FORMAT, "created_by": "test",
               "production": "Episode", "fps": 25, "length_s": 60.0,
               "cameras": [{"source": A, "file": A, "track": "Presenter"},
                           {"source": B, "file": B, "track": "Guest"}],
               "cut": [], "speakers": [], "audio_files": {}, "words": []},
              f)

said = []
state = {"out_folder": vpm.Value(out), "project_from": "",
         "resolve_button_check": lambda: said.append(1),
         "results": [], "running": True, "dry_run": False}


def run_writes(handover):
    """One run through the window's loop, its command line saying *handover*.

    main stands in for the run and prints the path, as the run prints
    what it wrote; the loop keeps an existing path as a result.
    """
    def main():
        """The run: says what it wrote, and ends well."""
        print(handover)
        return 0
    ui.main = main
    state["results"], state["running"] = [], True
    kept_argv = sys.argv[:]
    with contextlib.redirect_stdout(io.StringIO()):
        ui.gui_run_loop(["vpm"], state,
                        ui.make_log_writer(state, queue.Queue()),
                        lambda *a: None,
                        types.SimpleNamespace(run_step=None),
                        lambda *a: None, [])
    sys.argv[:] = kept_argv


def taken():
    """The handover the button offers now, by file name, or None."""
    js = state.get("resolve_json")
    return os.path.basename(js) if js else None


print("1. A run over three cameras that wrote a handover over two")
ui.handover_follows(state, [A, B, C])
run_writes(HANDOVER)
check("the run's own handover is taken up though it names two",
      taken() == "Episode_resolve.json",
      "the button offers %r, wanted 'Episode_resolve.json'" % taken())

print("\n2. A camera the handover names taken out")
ui.handover_follows(state, [A, C])
check("a camera taken out drops the run's handover",
      taken() is None, "the button offers %r, wanted None" % taken())

print("\n3. The camera put back")
ui.handover_follows(state, [A, B, C])
check("the camera put back brings the run's handover back",
      taken() == "Episode_resolve.json",
      "the button offers %r, wanted 'Episode_resolve.json'" % taken())

print("\n4. A list the remembered handover names more than")
ui.handover_follows(state, [A])
run_writes(HANDOVER)
ui.handover_follows(state, [A, C])
ui.handover_follows(state, [A])
check("a handover naming a camera not in the list stays away",
      taken() is None,
      "the button offers %r for A alone, wanted None" % taken())

print("\n5. Another output folder, as a new production has")
ui.handover_follows(state, [A, B, C])
ui.handover_follows(state, [A, B])
elsewhere = os.path.join(folder, "Next")
os.makedirs(elsewhere)
state["out_folder"], state["resolve_json"] = vpm.Value(elsewhere), None
ui.handover_follows(state, [])
ui.handover_follows(state, [A, B, C])
check("a handover from a folder no longer searched stays away",
      taken() is None,
      "the button offers %r with the output folder moved, wanted None"
      % taken())

shutil.rmtree(folder, ignore_errors=True)
print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
