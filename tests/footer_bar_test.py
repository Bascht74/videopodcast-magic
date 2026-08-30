# -*- coding: utf-8 -*-
"""The one bar in the footer: does it come, rise, and go again?"""
import os
HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = os.environ.get("VPM_SCRIPT") or os.path.join(
    os.path.dirname(HERE), "videopodcast-magic.py")
import importlib.util, sys, tempfile
os.environ["QT_QPA_PLATFORM"] = "offscreen"
# A cache of its own, and an empty one. This test asks whether the bar
# comes, rises and goes -- and there is nothing to show where there is
# nothing to do. Once what was measured of these files is kept between
# runs, the second run over the same material is instant and the bar
# never appears: green on 31.8.2026 cold, red on the third warm run.
# The bar was right both times; the test was tied to slowness.
os.environ["VPM_CACHE"] = tempfile.mkdtemp(prefix="vpm_footer_cache_")
from PySide6 import QtWidgets, QtCore
app = QtWidgets.QApplication(sys.argv[:1])
spec = importlib.util.spec_from_file_location("vpm", SCRIPT)
vpm = importlib.util.module_from_spec(spec); sys.modules["vpm"] = vpm
spec.loader.exec_module(vpm)
vpm.list_presets = lambda key: [("Podcast_Multitrack", "u1", True)]
vpm.load_api_key = lambda: ""
sys.path.insert(0, HERE)
from fixture_project import fixture_project
PROJECT, MEDIA = fixture_project("footerbar")
if PROJECT is None:
    print("SKIPPED: no test project -- point VPM_MEDIA at a folder "
          "holding videopodcast-magic_Interview_2.json (looked in %s)" % MEDIA)
    sys.exit(0)
QtWidgets.QFileDialog.getOpenFileName = staticmethod(
    lambda *a, **k: (PROJECT, ""))

error = []
def check(name, ok, extra=""):
    print("  %-52s %s %s" % (name, "ok" if ok else "FAIL", extra))
    if not ok:
        error.append(name)

def win():
    for x in app.topLevelWidgets():
        if "Video Podcast Magic" in x.windowTitle():
            return x

def bar():
    """The footer bar: the only one that counts in thousandths.

    Told apart by its range, not by its size. Height and width are
    looks, and looks change; 0..1000 is what this bar is.
    """
    for w in win().findChildren(QtWidgets.QProgressBar):
        if w.maximum() == 1000:
            return w

seen = {"shown": 0, "values": [], "captions": set(), "hidden_again": False}
n = [0]

def watch():
    b = bar()
    if b is None:
        return
    if b.isVisible():
        seen["shown"] += 1
        seen["values"].append(b.value())
    elif seen["shown"]:
        seen["hidden_again"] = True

def step():
    i = n[0]; n[0] += 1
    try:
        if i == 0:
            win().show(); win().resize(1400, 900); app.processEvents()
        elif i == 1:
            b = bar()
            check("a bar is there", b is not None)
            check("and it is out of the way while nothing runs",
                  b is not None and not b.isVisible())
            clock = QtCore.QTimer(win())
            clock.timeout.connect(watch)
            clock.start(100)
            state["clock"] = clock
            button = None
            for w in win().findChildren(QtWidgets.QPushButton):
                if w.text().strip().startswith("Open project"):
                    button = w
            button.click()
        elif i >= 3 and (not vpm_busy() or i > 40):
            state["clock"].stop()
            values = seen["values"]
            check("the bar showed itself", seen["shown"] > 0, seen["shown"])
            check("it only ever went forwards",
                  all(b >= a for a, b in zip(values, values[1:])),
                  str(values[:14]))
            check("it got past the start", max(values or [0]) > 0,
                  max(values or [0]))
            check("it reached the end", max(values or [0]) >= 1000,
                  max(values or [0]))
            print("\n%s" % ("ALL OK" if not error
                            else "FAIL: " + ", ".join(error)))
            app.quit(); return
    except Exception:
        import traceback; traceback.print_exc(); app.quit(); return
    QtCore.QTimer.singleShot(1000, step)

state = {}

def vpm_busy():
    """Still working, as the window itself sees it."""
    b = bar()
    return b is not None and b.isVisible()

QtCore.QTimer.singleShot(600, step)
QtCore.QTimer.singleShot(120000, app.quit)
sys.argv = ["videopodcast-magic.py"]
vpm.gui()
sys.exit(1 if error else 0)
