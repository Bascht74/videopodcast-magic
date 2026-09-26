# -*- coding: utf-8 -*-
"""Stop can be pressed in every phase a run goes through.

In order: while a start waits for the camera audio, Stop is there, and
pressing it calls that start off without stopping the camera audio;
then while the Resolve-only run goes, Stop is there. The window around
the run start is stood in for -- the buttons are real, the rest takes
every call -- and no run thread is started.
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
import the_program
SCRIPT = the_program.SCRIPT
import threading, time
os.environ["QT_QPA_PLATFORM"] = "offscreen"
from PySide6 import QtCore, QtWidgets
app = QtWidgets.QApplication(sys.argv[:1])
vpm = the_program.load()
vpm.set_language("en")
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
    """Takes every call and every name, and answers with itself."""

    def __getattr__(self, name):
        return self

    def __call__(self, *rest, **named):
        return self


class HeldThread(object):
    """A run thread that never runs: only the buttons are asked about."""

    def __init__(self, *rest, **named):
        pass

    def start(self):
        pass


def window_for(state):
    """The window as far as the run start reaches into it."""
    window = Anything()
    sheet = Anything()
    buttons = {}
    for name in ("start_run", "preview_button"):
        buttons[name] = QtWidgets.QPushButton(name)
    sheet.__dict__["only_resolve"] = QtWidgets.QPushButton("resolve")
    window.__dict__.update(buttons)
    window.__dict__["output_sheet"] = sheet
    window.__dict__["break_off"] = vpm.break_off_button(
        QtWidgets, state, lambda text: None)
    return window


def run_start(state, busy):
    """Both starts, made over the stood-in window."""
    window = window_for(state)
    model = Anything()
    model.__dict__.update(files=[("/tmp/vpm_stop/WideCam.mov", "video")],
                          cut={})
    start, only_resolve_start = vpm.make_run_start(
        QtCore, window, state, model, Anything(), Anything(), Anything(),
        Anything(), Anything(), {}, {}, [], {"threads": 1},
        threading.Lock(), lambda: busy, Anything(), Anything(),
        lambda: True, [])
    return window, start, only_resolve_start


def shown(button):
    """Whether a button stands in the row and can be pressed."""
    return not button.isHidden() and button.isEnabled()


real_thread = threading.Thread
threading.Thread = HeldThread
try:
    print("A start waiting for the camera audio")
    state = {"running": False, "waiting": False, "confirmed": True,
             "own_cameras": True}
    window, start, _only = run_start(state, busy=True)
    start(False)
    check("Stop can be pressed while a start waits for camera audio",
          state.get("waiting") and shown(window.break_off),
          "waiting %r, Stop hidden %r, enabled %r"
          % (state.get("waiting"), window.break_off.isHidden(),
             window.break_off.isEnabled()))
    window.break_off.click()
    until = time.time() + 10.0
    while state.get("waiting") and time.time() < until:
        app.processEvents()
        time.sleep(0.02)
    check("pressing Stop there calls the waiting start off",
          not state.get("waiting") and window.start_run.isEnabled()
          and window.break_off.isHidden(),
          "waiting %r, Start enabled %r, Stop hidden %r"
          % (state.get("waiting"), window.start_run.isEnabled(),
             window.break_off.isHidden()))
    check("and leaves the camera audio running",
          not vpm.RUN_STOP["wanted"],
          "a stop was asked for: %r" % (vpm.RUN_STOP["wanted"],))

    print("\nThe Resolve-only run")
    state = {"running": False, "resolve_json": "/tmp/vpm_stop/x_resolve.json"}
    window, _start, only_resolve_start = run_start(state, busy=False)
    only_resolve_start()
    check("Stop can be pressed while the Resolve-only run goes",
          state.get("running") and shown(window.break_off),
          "running %r, Stop hidden %r, enabled %r"
          % (state.get("running"), window.break_off.isHidden(),
             window.break_off.isEnabled()))
except Exception:
    import traceback
    traceback.print_exc()
    bad.append("the test itself broke off")
finally:
    threading.Thread = real_thread

print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
