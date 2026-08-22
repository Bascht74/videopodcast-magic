# -*- coding: utf-8 -*-
"""The channel split is visible on the file page, and can be changed."""
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
SEC = 10
folder = tempfile.mkdtemp(prefix="vpm_rows_")


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
        on = int(r.uniform(0.5, 1.4) * RATE)
        env[t:t + on] = 1.0
        t += on + int(r.uniform(0.2, 0.7) * RATE)
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


a, b = voice(21), voice(22)
quiet = 10 ** (-12.0 / 20.0)
two_mics = write("A_two_mics.wav", [a + quiet * later(b, 2.9),
                                    b + quiet * later(a, 2.9)])
one_pair = write("B_one_pair.wav", [a + 0.4 * b, 0.4 * a + b])
single = write("C_single.wav", [a])
video = os.path.join(folder, "D_camera.mov")
subprocess.run(["ffmpeg", "-v", "error", "-f", "lavfi", "-i",
                "testsrc=size=160x90:rate=25:duration=%d" % SEC,
                "-f", "lavfi", "-i", "sine=frequency=300:duration=%d" % SEC,
                "-c:v", "libx264", "-preset", "ultrafast", "-pix_fmt",
                "yuv420p", "-c:a", "aac", "-shortest", "-y", video],
               check=True)
project = os.path.join(folder, "videopodcast-magic_Interview_2.json")
with open(project, "w", encoding="utf-8") as f:
    json.dump({"format": 3, "version": "test", "timeline": [], "call": [],
               "files": [{"path": two_mics, "kind": "audio"},
                         {"path": one_pair, "kind": "audio"},
                         {"path": single, "kind": "audio"},
                         {"path": video, "kind": "video"}],
               "out_folder": os.path.join(folder, "Ergebnis"),
               "production": "Rows", "multitrack": True,
               "assignment": {}, "preset": ""}, f)
os.makedirs(os.path.join(folder, "Ergebnis"), exist_ok=True)
QtWidgets.QFileDialog.getOpenFileName = staticmethod(
    lambda *a, **k: (project, ""))
QtWidgets.QDialog.exec = lambda self: QtWidgets.QDialog.Accepted


def win():
    for x in app.topLevelWidgets():
        if x.windowTitle().startswith("Video Podcast"):
            return x


def tree():
    for w in win().findChildren(QtWidgets.QTreeWidget):
        if w.columnCount() >= 3:
            return w


def rows_under(name):
    """The channel rows of one file, as (text, value, checkbox).

    One row per channel now, and the tick sits in the wide column inside
    a small widget beside its reason -- in the narrow one the word next
    to the box was cut off after its first letter.
    """
    out = []
    t = tree()

    def box_and_text(row):
        beside = t.itemWidget(row, 2)
        if beside is None:
            return row.text(2), None
        box = beside.findChild(QtWidgets.QCheckBox)
        said = [w.text() for w in beside.findChildren(QtWidgets.QLabel)]
        return (said[0] if said else ""), box

    def walk(node):
        for i in range(node.childCount()):
            kid = node.child(i)
            if kid.text(0).strip().startswith(os.path.basename(name)):
                for k in range(kid.childCount()):
                    row = kid.child(k)
                    if row.data(0, QtCore.Qt.UserRole + 2) == "channel":
                        said, box = box_and_text(row)
                        out.append((row.text(0).strip(), said, box))
            walk(kid)
    walk(t.invisibleRootItem())
    return out


n = [0]
waited = [0]

def step():
    i = n[0]; n[0] += 1
    try:
        if i == 0:
            win().show(); app.processEvents()
            for w in win().findChildren(QtWidgets.QPushButton):
                if w.text().strip().startswith("Open project"):
                    w.click()
        elif i == 1:
            # Both files, not just the first: they are measured in
            # parallel and the second can still be running.
            # What "ready" means, exactly: both files have their two
            # rows, neither still says it is measuring, and the first
            # channel of each carries the tick. Asking for a tick on
            # *every* row waits for something that never comes -- the
            # last channel has nothing after it to join to and gets
            # none, which is what this test checks further down. That
            # wait ran into its limit every single time and cost the
            # suite two minutes: it took as long as all the other
            # tests together.
            two_now = rows_under("A_two_mics.wav")
            pair_now = rows_under("B_one_pair.wav")
            said = [r[1] for r in two_now + pair_now]
            pending = (len(two_now) < 2 or len(pair_now) < 2
                       or vpm.T('measurement running ...') in said
                       or two_now[0][2] is None or pair_now[0][2] is None)
            if pending and waited[0] < 120:
                waited[0] += 1
                n[0] = 1
                QtCore.QTimer.singleShot(200, step)
                return
            two = rows_under("A_two_mics.wav")
            pair = rows_under("B_one_pair.wav")
            lone = rows_under("C_single.wav")
            cam = rows_under("D_camera.mov")
            print("   two mics:", [(r[0], r[1][:40]) for r in two])
            print("   one pair:", [(r[0], r[1][:40]) for r in pair])
            # One row per channel: two channels give two rows, and only
            # the first carries a tick -- the last channel has nothing
            # after it to join to.
            check("the two-microphone file gets a row per channel",
                  len(two) == 2, str(len(two)))
            check("and a tick to change it with",
                  two and two[0][2] is not None)
            check("only the first channel has one",
                  len(two) > 1 and two[1][2] is None, str(two[1:2]))
            check("the tick is off: two tracks",
                  two and two[0][2] is not None
                  and not two[0][2].isChecked())
            check("the stereo file gets a row per channel",
                  len(pair) == 2, str(len(pair)))
            check("and its tick is on",
                  pair and pair[0][2] is not None and pair[0][2].isChecked())
            check("the second channel says who it belongs to",
                  len(pair) > 1 and "1" in pair[1][1], str(pair[1:2]))
            check("a single channel file gets none", not lone, str(lone))
            check("a mono camera gets none too", not cam, str(cam))
            if two and two[0][2] is not None:
                two[0][2].setChecked(True)
                app.processEvents()
                QtCore.QTimer.singleShot(300, step)
                return
        elif i == 2:
            two = rows_under("A_two_mics.wav")
            check("what was set by hand says so",
                  two and two[0][1] == vpm.T(
                      'set by hand -- overrides the measurement'),
                  str(two and two[0][1]))
            check("and the tick stayed where it was put",
                  two and two[0][2] is not None and two[0][2].isChecked())
            print("\n%s" % ("ALL OK" if not error
                            else "FAIL: " + ", ".join(error)))
            app.quit(); return
    except Exception:
        import traceback; traceback.print_exc(); app.quit(); return
    QtCore.QTimer.singleShot(1200, step)

QtCore.QTimer.singleShot(700, step)
QtCore.QTimer.singleShot(180000, app.quit)
sys.argv = ["videopodcast-magic.py"]
vpm.gui()
shutil.rmtree(folder, ignore_errors=True)
sys.exit(1 if error else 0)
