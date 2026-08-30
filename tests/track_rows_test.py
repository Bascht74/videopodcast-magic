# -*- coding: utf-8 -*-
"""A stereo file with two people on it becomes two tracks everywhere."""
import os
HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = os.environ.get("VPM_SCRIPT") or os.path.join(
    os.path.dirname(HERE), "videopodcast-magic.py")
import importlib.util, json, shutil, subprocess, sys, tempfile, wave
import numpy as np
os.environ["QT_QPA_PLATFORM"] = "offscreen"
from PySide6 import QtCore, QtWidgets
app = QtWidgets.QApplication(sys.argv[:1])
spec = importlib.util.spec_from_file_location("vpm", SCRIPT)
vpm = importlib.util.module_from_spec(spec); sys.modules["vpm"] = vpm
spec.loader.exec_module(vpm)
vpm.list_presets = lambda key: []
vpm.load_api_key = lambda: ""

error = []
def check(name, ok, extra=""):
    print("  %-52s %s %s" % (name, "ok" if ok else "FAIL", extra))
    if not ok:
        error.append(name)

RATE = 48000
SEC = 8
folder = tempfile.mkdtemp(prefix="vpm_tracks_")


def voice(seed):
    r = np.random.default_rng(seed)
    n = SEC * RATE
    x = r.standard_normal(n)
    f = np.fft.rfftfreq(n, 1.0 / RATE)
    X = np.fft.rfft(x)
    X[(f < 120) | (f > 5000)] = 0
    x = np.fft.irfft(X, n)
    env = np.zeros(n)
    t = 0
    while t < n:
        on = int(r.uniform(0.4, 1.2) * RATE)
        env[t:t + on] = 1.0
        t += on + int(r.uniform(0.2, 0.6) * RATE)
    k = np.hanning(int(0.05 * RATE))
    x = x * np.convolve(env, k / k.sum(), mode="same")
    return x / (np.abs(x).max() + 1e-9)


def later(x, ms):
    n = int(round(ms * RATE / 1000.0))
    return np.concatenate((np.zeros(n), x))[:len(x)]


def write(name, rows):
    path = os.path.join(folder, name)
    n = min(len(r) for r in rows)
    both = np.empty(len(rows) * n)
    for i, r in enumerate(rows):
        both[i::len(rows)] = r[:n]
    both = both / max(1e-9, np.abs(both).max()) * 0.7
    with wave.open(path, "wb") as f:
        f.setnchannels(len(rows)); f.setsampwidth(2); f.setframerate(RATE)
        f.writeframes(np.clip(both * 32767, -32768, 32767)
                      .astype("<i2").tobytes())
    return path


a, b, c = voice(31), voice(32), voice(33)
quiet = 10 ** (-12.0 / 20.0)
pair = write("A_pair.wav", [a + quiet * later(b, 2.9),
                            b + quiet * later(a, 2.9)])
solo = write("B_solo.wav", [c])
video = os.path.join(folder, "C_camera.mov")
subprocess.run(["ffmpeg", "-v", "error", "-f", "lavfi", "-i",
                "testsrc=size=160x90:rate=25:duration=%d" % SEC,
                "-f", "lavfi", "-i", "sine=frequency=300:duration=%d" % SEC,
                "-c:v", "libx264", "-preset", "ultrafast", "-pix_fmt",
                "yuv420p", "-c:a", "aac", "-shortest", "-y", video],
               check=True)
project = os.path.join(folder, "videopodcast-magic_Interview_2.json")
with open(project, "w", encoding="utf-8") as f:
    json.dump({"format": 3, "version": "test", "timeline": [], "call": [],
               "files": [{"path": pair, "kind": "audio"},
                         {"path": solo, "kind": "audio"},
                         {"path": video, "kind": "video"}],
               "out_folder": os.path.join(folder, "Ergebnis"),
               "production": "Tracks", "multitrack": True,
               "assignment": {}, "preset": ""}, f)
os.makedirs(os.path.join(folder, "Ergebnis"), exist_ok=True)
QtWidgets.QFileDialog.getOpenFileName = staticmethod(
    lambda *a, **k: (project, ""))
QtWidgets.QDialog.exec = lambda self: QtWidgets.QDialog.Accepted


def win():
    for x in app.topLevelWidgets():
        if "Video Podcast Magic" in x.windowTitle():
            return x


def audio_rows():
    """The first column of the upper assignment tree, its top rows only.

    The assignment is a QTreeView over a model, and the tree is found the
    way the table was: the visible one whose fourth column is headed
    "Timecode". Children of a row are voices inside one recording, not
    recordings, so only the top level is read. Nothing found means no
    rows -- the caller waits for the window to fill and gives up loudly.
    """
    for t in win().findChildren(QtWidgets.QTreeView):
        m = t.model()
        if not t.isVisible() or m is None or m.columnCount() < 4:
            continue
        if m.headerData(3, QtCore.Qt.Horizontal) != "Timecode":
            continue
        return [m.index(r, 0).data() or ""
                for r in range(m.rowCount())]
    return []


def tab(word):
    for tw in win().findChildren(QtWidgets.QTabWidget):
        for k in range(tw.count()):
            if word.lower() in tw.tabText(k).lower():
                tw.setCurrentIndex(k)
                app.processEvents()
                return True
    return False


n = [0]
waited = [0]

def step():
    i = n[0]; n[0] += 1
    try:
        if i == 0:
            win().show(); win().resize(1400, 900); app.processEvents()
            for w in win().findChildren(QtWidgets.QPushButton):
                if w.text().strip().startswith("Open project"):
                    w.click()
        elif i == 1:
            tab("Assignment")
            rows = audio_rows()
            if len(rows) < 3 and waited[0] < 120:
                waited[0] += 1
                n[0] = 1
                QtCore.QTimer.singleShot(1000, step)
                return
            print("   rows:", rows)
            check("the stereo file became two rows, the mono one stays one",
                  len(rows) == 3, str(len(rows)))
            cut = [r for r in rows if "_Channel" in r]
            check("both come from the stereo file", len(cut) == 2, str(cut))
            check("and they are different channels",
                  len(set(cut)) == 2, str(cut))
            check("the mono file is untouched",
                  any(r.startswith("B_solo") for r in rows), str(rows))
            k = None
            for w in win().findChildren(QtWidgets.QPushButton):
                if w.text().strip().startswith("Dry run"):
                    k = w
            check("and a run can be started -- multitrack is possible now",
                  bool(k and k.isEnabled()),
                  "" if k is None else str(k.isEnabled()))
            print("\n%s" % ("ALL OK" if not error
                            else "FAIL: " + ", ".join(error)))
            app.quit(); return
    except Exception:
        import traceback; traceback.print_exc(); app.quit(); return
    QtCore.QTimer.singleShot(1200, step)

QtCore.QTimer.singleShot(700, step)
QtCore.QTimer.singleShot(200000, app.quit)
def let_go_of(what):
    """Make every player let go of what it has open in there.

    A player holds the file it has open. Under macOS and Linux the
    folder can be deleted anyway, under Windows it cannot -- and with
    ignore_errors nobody hears of it: the folder simply stays behind on
    every run. Every player under every window is asked, and by what it
    has open rather than by which player it is, so that a second holder
    cannot slip through. Returns the names that were let go.

    A player that never started is not stopped. What lies behind stop()
    is built on first use, and building it waits for a lock another
    player holds while it is starting up -- the window then never comes
    back. playbackState only reads what is already noted.
    """
    what = os.path.realpath(what)
    let_go = []
    for top in app.topLevelWidgets():
        for x in top.findChildren(QtCore.QObject):
            if not (hasattr(x, "setSource") and hasattr(x, "source")):
                continue
            where = x.source()
            if not isinstance(where, QtCore.QUrl):
                continue
            where = where.toLocalFile()
            if not where:
                continue
            held = os.path.realpath(where)
            if held != what and not held.startswith(what + os.sep):
                continue
            state = getattr(x, "playbackState", None)
            state = state() if state is not None else None
            if state is not None and state != type(state).StoppedState:
                x.stop()
            x.setSource(QtCore.QUrl())
            let_go.append(os.path.basename(where))
    app.processEvents()
    return sorted(let_go)


def clean_up(what):
    """Close the window, then delete the folder, waiting for the grip.

    gui() comes back with the window still standing, so the folder used
    to go while players still held files in it. Let go, close, delete --
    in that order. And no ignore_errors: it would swallow the one thing
    that can go wrong here, a folder that stays because something still
    holds it.

    Letting go returns before the file is free. The media backend closes
    the handle in a thread of its own, so setSource() comes back while
    the system still has the file open. Under macOS and Linux that never
    shows, because a held file can be deleted there anyway. On Windows
    it does: measured on the build machine, five of these tests left
    four to seven files behind on the first attempt. So what is waited
    for is the handle, not a number of milliseconds -- delete, run the
    event loop, delete again, up to ten seconds. Ten because it is far
    above a thread closing a file, and still short enough that a folder
    which will never go does not hold the suite.

    What is left after that is a finding, not a failure: it is named,
    with how long it was waited on, and it does not turn the test red.
    A test that is red on one system on every run gets switched off
    rather than looked at, and then it says nothing at all.
    """
    print("  let go of %s" % (", ".join(let_go_of(what)) or "nothing"))
    for top in app.topLevelWidgets():
        top.close()
    app.processEvents()
    clock = QtCore.QElapsedTimer()
    clock.start()
    while True:
        left = []
        try:
            shutil.rmtree(what)
        except OSError:
            for here, _, files in os.walk(what):
                left += [os.path.join(here, f) for f in files]
            left = left or ([what] if os.path.exists(what) else [])
        if not left or clock.elapsed() > 10000:
            break
        app.processEvents()
        QtCore.QThread.msleep(50)
    if left:
        print("  the folder stayed: %d still held after %.1f s, first %s"
              % (len(left), clock.elapsed() / 1000.0, left[0]))
    else:
        print("  the folder went away with the window, after %.1f s"
              % (clock.elapsed() / 1000.0))


sys.argv = ["videopodcast-magic.py"]
vpm.gui()
clean_up(folder)
sys.exit(1 if error else 0)
