# -*- coding: utf-8 -*-
"""The start button must still build a command line after the rebuild."""
import os
HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = os.environ.get("VPM_SCRIPT") or os.path.join(
    os.path.dirname(HERE), "videopodcast-magic.py")
import sys, time, importlib.util
os.environ["QT_QPA_PLATFORM"] = "offscreen"
from PySide6 import QtWidgets, QtCore
app = QtWidgets.QApplication(sys.argv[:1])
spec = importlib.util.spec_from_file_location(
    "vpm", SCRIPT)
vpm = importlib.util.module_from_spec(spec); sys.modules["vpm"] = vpm
spec.loader.exec_module(vpm)
vpm.list_presets = lambda key: [("Podcast_Multitrack", "u1", True)]
vpm.load_api_key = lambda: ""
sys.path.insert(0, HERE)
from fixture_project import fixture_project
PROJECT, D = fixture_project("startbutton")
if PROJECT is None:
    # Not a pass: run.sh reads the marker and counts this as skipped.
    print("SKIPPED: no test project -- point VPM_MEDIA at a folder "
          "holding videopodcast-magic_Interview_2.json (looked in %s)" % D)
    sys.exit(0)
QtWidgets.QFileDialog.getOpenFileName = staticmethod(
    lambda *a, **k: (PROJECT, ""))

# Accept every dialog at once -- offscreen nobody would answer them.
QtWidgets.QDialog.exec = lambda self: QtWidgets.QDialog.Accepted
QtWidgets.QMessageBox.exec = lambda self: QtWidgets.QMessageBox.Ok

seen = {}
import subprocess
import threading
real = threading.Thread


def fake_thread(target=None, args=(), daemon=None, **rest):
    """Hold back the program's own threads, let subprocess keep its.

    On Windows subprocess reads a child's output in threads of its own
    (`Popen._readerthread`), and this stub swallowed those too: it has
    no join, so CPython tripped over it as soon as the window asked
    ffprobe something while it was opening a project. On macOS and
    Linux the same call goes through selectors and no thread is made,
    which is why it stayed hidden until 25.8.2026. Those threads are
    not ours to hold back.
    """
    if isinstance(getattr(target, "__self__", None), subprocess.Popen):
        return real(target=target, args=args, daemon=daemon, **rest)

    class T(object):
        daemon = False

        def start(self_):
            # Measuring the files starts threads with an argument list of
            # their own, so what is kept here is the last list started,
            # and the run is the one that comes after the click.
            if args:
                seen["argv"] = list(args[0])

        def join(self_, timeout=None):
            pass

        def is_alive(self_):
            return False

    return T()


threading.Thread = fake_thread

error = []
def check(name, ok, extra=""):
    print("  %-48s %s %s" % (name, "ok" if ok else "FAIL", extra))
    if not ok: error.append(name)

def win():
    for x in app.topLevelWidgets():
        if "Video Podcast Magic" in x.windowTitle():
            return x
def button(text):
    for w in win().findChildren(QtWidgets.QPushButton):
        if w.text().strip().startswith(text):
            return w

n = [0]
waited = [0]
tries = [0]
since = [0.0, 0.0]
was = [None]
clicked = [False]
def carry_on():
    i = n[0]; n[0] += 1
    try:
        if i == 0:
            # Waited for rather than slept past: the window is built in
            # the first turns of the event loop, and how long that takes
            # depends on the machine.
            if (win() is None or button("Open project") is None) \
                    and tries[0] < 500:
                tries[0] += 1
                n[0] = 0
                QtCore.QTimer.singleShot(20, carry_on)
                return
            win().show(); app.processEvents()
        elif i == 1:
            button("Open project").click()
        elif i == 2:
            k = button("Dry run")
            # Waited for rather than slept past: opening the project
            # measures files, and how long that takes depends on the
            # machine and on what else the suite is running at the time.
            if not since[0]:
                since[0] = time.time()
            waited[0] = int(time.time() - since[0])
            if k is not None and not k.isEnabled() and waited[0] < 60:
                n[0] = 2
                QtCore.QTimer.singleShot(100, carry_on)
                return
            print("   dry-run button:", bool(k),
                  k.isEnabled() if k else "-", "after %d s" % waited[0])
            if k is not None and not k.isEnabled():
                # A disabled button without its reason is the hardest
                # kind of failure to chase. The interface knows why.
                for w in win().findChildren(QtWidgets.QWidget):
                    tip = w.toolTip()
                    if tip.startswith(vpm.T('Not ready yet:')):
                        print("   " + tip.replace("\n", "\n   "))
                        break
            if k and k.isEnabled():
                # Measuring the files starts threads carrying arguments
                # too, so the run is known by the argument list being a
                # new one, not by there being one at all.
                was[0] = seen.get("argv")
                clicked[0] = True
                k.click()
        elif i == 3:
            # Waited for rather than slept past: the click returns
            # before the thread it starts has its arguments in.
            if not since[1]:
                since[1] = time.time()
            if (clicked[0] and seen.get("argv") is was[0]
                    and time.time() - since[1] < 10):
                n[0] = 3
                QtCore.QTimer.singleShot(20, carry_on)
                return
        elif i == 4:
            argv = seen.get("argv")
            print("   argv:", " ".join(argv[:14]) if argv else None)
            check("a run was started", bool(argv))
            if argv:
                check("program name first",
                        argv[0].endswith("videopodcast-magic.py"))
                check("--dry-run there", "--dry-run" in argv)
                check("files there",
                        any(x.endswith(".mov") or x.endswith(".wav")
                            for x in argv))
            print("\n%s" % ("ALL OK" if not error
                            else "FAIL: " + ", ".join(error)))
            app.quit(); return
    except Exception:
        import traceback; traceback.print_exc(); app.quit(); return
    QtCore.QTimer.singleShot(50, carry_on)

QtCore.QTimer.singleShot(0, carry_on)
QtCore.QTimer.singleShot(150000, app.quit)
sys.argv = ["videopodcast-magic.py"]
vpm.gui()
threading.Thread = real
sys.exit(1 if error else 0)
