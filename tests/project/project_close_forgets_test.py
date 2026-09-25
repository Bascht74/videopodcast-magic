# -*- coding: utf-8 -*-
"""Closing a project forgets the handovers remembered for its cameras.

The window remembers, per list of cameras, the handover its button
offered, so a camera taken out and put back brings it back. Closing the
project has to take that memory along: left standing, the next
production over the same cameras in the same folder was handed the
closed one's handover. In order: the memory at work inside one
production, then the project closed and the same cameras and folder
taken up again. The window's own functions without a window; what
closing touches besides the state stands in and takes every call.
"""
import os
import sys
# tests/, where the helpers and state/ lie; this file may stand in a
# folder under it, or in one under that.
HERE = os.path.dirname(os.path.abspath(__file__))
while not os.path.isfile(os.path.join(HERE, "the_program.py")) \
        and os.path.dirname(HERE) != HERE:
    HERE = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import inspect
import json
import shutil
import tempfile
import time
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


class Anything(object):
    """Every widget and helper closing touches besides the state: any call."""

    def __getattr__(self, name):
        """Any attribute, and it is this again."""
        return self

    def __call__(self, *args, **kwargs):
        """Any call, and it answers this again."""
        return self

    def __getitem__(self, key):
        """Any entry, and it is this again."""
        return self

    def __setitem__(self, key, value):
        """Any entry set, and nothing kept."""


folder = tempfile.mkdtemp(prefix="vpm_close_")
out = os.path.join(folder, "Run")
os.makedirs(out)
A, B, C = [os.path.join(folder, n) for n in
           ("A_Presenter.mov", "B_Guest.mov", "C_WideCam.mov")]
for p in (A, B, C):
    open(p, "wb").close()
# The run's handover names two of the three: a search over all three
# passes it over, so only the memory can hand it back.
HANDOVER = os.path.join(out, "Episode_resolve.json")
with open(HANDOVER, "w", encoding="utf-8") as f:
    json.dump({"format": vpm.FILE_FORMAT, "created_by": "test",
               "production": "Episode", "fps": 25, "length_s": 60.0,
               "cameras": [{"source": A, "file": A, "track": "Presenter"},
                           {"source": B, "file": B, "track": "Guest"}],
               "cut": [], "speakers": [], "audio_files": {}, "words": []},
              f)

state = {"out_folder": vpm.Value(out), "project_from": "",
         "resolve_button_check": lambda: None,
         "results": [], "running": False, "dry_run": False}
files = []
# Closing as the window wires it, with the state and the output folder
# real and everything else a stand-in.
wiring = {name: Anything() for name in
          inspect.signature(vpm.make_project_file).parameters}
wiring.update(state=state, files=files, out_folder=state["out_folder"])
_write, project_close, _open = vpm.make_project_file(**wiring)


def taken():
    """The handover the button offers now, by file name, or None."""
    js = state.get("resolve_json")
    return os.path.basename(js) if js else None


try:
    print("1. One production: a camera out and back brings the handover")
    ui.handover_follows(state, [A, B, C])
    # As the run hands its handover to the window.
    state["resolve_json"] = HANDOVER
    ui.handover_follows(state, [A, C])
    ui.handover_follows(state, [A, B, C])
    check("within one production the remembered handover comes back",
          taken() == "Episode_resolve.json",
          "the button offers %r, wanted 'Episode_resolve.json'" % taken())

    print("\n2. The project closed, the same cameras and folder again")
    project_close()
    # The emptied file list, as the window rebuilds it after closing.
    ui.handover_follows(state, [])
    state["out_folder"].set(out)
    ui.handover_follows(state, [A, B, C])
    check("a new production is not handed the closed one's handover",
          taken() is None,
          "the button offers %r for the same three cameras in %s after "
          "closing, wanted None" % (taken(), os.path.basename(out)))
except Exception:
    import traceback
    traceback.print_exc()
    bad.append("crash")
finally:
    shutil.rmtree(folder, ignore_errors=True)

print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
