# -*- coding: utf-8 -*-
"""A point outside a timecoded camera is named, never jumped past.

One window over a camera with a 10:00:00:00 timecode, 12 s long, the
In point a minute before it and the Out point ten hours past it. The
sections: the sheet comes up with both jump buttons live and the camera
in the preview player on its own clock; "to In point" and "to Out
point" each say no video file holds that point and leave the player
where it stood; an In point marked six seconds in is jumped to, silently.
"""
import json
import os
import subprocess
import sys
import tempfile
import time
import the_program

os.environ["QT_QPA_PLATFORM"] = "offscreen"
from PySide6 import QtCore, QtWidgets

began = time.time()
app = QtWidgets.QApplication(sys.argv[:1])
vpm = the_program.load()
vpm.set_language("en")
vpm.list_presets = lambda key: []
vpm.load_api_key = lambda: ""
vpm.update_offer = lambda *a, **k: None
vpm.run_argv = lambda values, assignment_file_path="": (None, None, [])

done = 0
bad = []


def check(name, ok, extra=""):
    global done
    done += 1
    print("  %-58s %s %s" % (name, "ok" if ok else "FAIL", extra))
    if not ok:
        bad.append("%s [%s]" % (name, extra or "no numbers"))


def material(folder):
    """A recording and a camera, both on a 10:00:00 clock, 12 s."""
    made = {n: os.path.join(folder, n) for n in ("Room_tc.wav", "A_tc.mov")}
    subprocess.run(
        ["ffmpeg", "-v", "error", "-f", "lavfi", "-i",
         "sine=frequency=300:duration=12", "-ar", "48000", "-ac", "1",
         "-c:a", "pcm_s16le", "-write_bext", "1", "-metadata",
         "time_reference=%d" % (36000 * 48000), "-y", made["Room_tc.wav"]],
        check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    subprocess.run(
        ["ffmpeg", "-v", "error", "-f", "lavfi", "-i",
         "testsrc=size=160x90:rate=25:duration=12", "-f", "lavfi",
         "-i", "sine=frequency=300:duration=12", "-c:a", "aac",
         "-c:v", "libx264", "-preset", "ultrafast", "-pix_fmt",
         "yuv420p", "-timecode", "10:00:00:00", "-shortest", "-y",
         made["A_tc.mov"]],
        check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return made


made = material(tempfile.mkdtemp(prefix="vpm_tcpoint_"))
project = os.path.join(tempfile.mkdtemp(prefix="vpm_tcpoint_p_"),
                       "videopodcast-magic_Point.json")
PAST, BEFORE = "20:00:00:00", "09:59:00:00"
with open(project, "w", encoding="utf-8") as f:
    json.dump({"format": vpm.FILE_FORMAT, "version": "test",
               "timeline": [], "preset": "", "production": "Point",
               "multitrack": False, "project_type": "cut",
               "in_point": BEFORE, "out_point": PAST,
               "out_folder": os.path.join(os.path.dirname(project),
                                          "Result"),
               "assignment": {
                   "audio:" + made["Room_tc.wav"]: ["Guest", "A_tc.mov"]},
               "files": [{"path": made["Room_tc.wav"], "kind": "audio"},
                         {"path": made["A_tc.mov"], "kind": "video"}]}, f)
os.makedirs(os.path.join(os.path.dirname(project), "Result"), exist_ok=True)
QtWidgets.QFileDialog.getOpenFileName = staticmethod(
    lambda *a, **k: (project, ""))
QtWidgets.QDialog.exec = lambda self: QtWidgets.QDialog.Accepted
QtWidgets.QMessageBox.exec = lambda self: QtWidgets.QMessageBox.Ok
_show = QtWidgets.QWidget.show


def offstage(self):
    """Shown for the layout, never on a screen."""
    self.setAttribute(QtCore.Qt.WA_DontShowOnScreen, True)
    _show(self)


QtWidgets.QWidget.show = offstage


def win():
    """The program's window."""
    for w in app.topLevelWidgets():
        if "Video Podcast Magic" in w.windowTitle():
            return w
    return None


def button(text):
    """The push button with that caption, or None."""
    for b in win().findChildren(QtWidgets.QPushButton):
        if b.text() == vpm.T(text):
            return b
    return None


def viewer():
    """The preview player: the one widget with a tick for assigned audio."""
    for w in win().findChildren(QtWidgets.QWidget):
        if hasattr(w, "track_checkbox") and hasattr(w, "jump_to"):
            return w
    return None


SENTENCE = vpm.T('%s is in none of the video files. Is there a timecode '
                 'that fits the material?')


def said():
    """What the visible label ending like the no-file sentence reads."""
    tail = SENTENCE.split("%s")[-1]
    for label in win().findChildren(QtWidgets.QLabel):
        if label.isVisible() and label.text().endswith(tail):
            return label.text()
    return ""


def judge():
    """Press the jump buttons over three points and read what each left."""
    to_in, to_out = button('to In point'), button('to Out point')
    mark_in = button('Mark In')
    live = [b is not None and b.isEnabled() for b in (to_in, to_out)]
    check("the sheet came up with both jump buttons live", all(live),
          "to In point %s, to Out point %s" % tuple(live))
    p = viewer()
    name = os.path.basename(getattr(p, "file_path", None) or "")
    clock = getattr(p, "tc0", None)
    check("the preview player holds the camera on its 10:00:00 clock",
          name == "A_tc.mov" and clock is not None
          and abs(clock - 36000.0) < 0.05,
          "holds %r, clock %r s against 36000" % (name, clock))
    if not all(live) or p is None or mark_in is None:
        return
    p.jump(3000)
    app.processEvents()
    to_in.click()
    app.processEvents()
    at, got = p.slider.value(), said()
    wanted = SENTENCE % vpm.T('In point')
    check("to In point before the camera starts says no file holds it",
          got == wanted, "reads %r, wanted %r" % (got, wanted))
    to_out.click()
    app.processEvents()
    after, got = p.slider.value(), said()
    wanted = SENTENCE % vpm.T('Out point')
    check("to Out point past the camera says no file holds it",
          got == wanted, "reads %r, wanted %r" % (got, wanted))
    check("a point no file holds leaves the player where it stood",
          at == 3000 and after == 3000,
          "at %d ms after In, %d ms after Out, 3000 before" % (at, after))
    p.jump(6000)
    app.processEvents()
    mark_in.click()
    p.jump(1000)
    app.processEvents()
    to_in.click()
    app.processEvents()
    at, got = p.slider.value(), said()
    check("to In point inside the camera lands there and says nothing",
          abs(at - 6000) <= 40 and got == "",
          "%r, at %d ms against 6000, sentence %r"
          % (p.cut_left.text(), at, got))


state = {"round": 0, "widths": None, "still": 0}


def to_sheet():
    """Bring the assignment sheet to the front."""
    for tw in win().findChildren(QtWidgets.QTabWidget):
        for k in range(tw.count()):
            if vpm.T('Assignment && time window')[:8].lower() \
                    in tw.tabText(k).lower():
                tw.setCurrentIndex(k)


def step():
    """Open the project, wait for the sheet to stand still, judge."""
    state["round"] += 1
    if state["round"] == 1:
        win().show()
        win().resize(1400, 900)
        for b in win().findChildren(QtWidgets.QPushButton):
            if b.text().strip().startswith(vpm.T('Open project ...')[:8]):
                b.click()
                break
    to_sheet()
    to_in = button('to In point')
    now = None if to_in is None or not to_in.isEnabled() else [
        w.width() for w in win().findChildren(QtWidgets.QPushButton)
        if w.isVisible()]
    # Settled: the button is live and the widths held for five turns.
    state["still"] = state["still"] + 1 if (
        now and now == state["widths"]) else 0
    state["widths"] = now
    if state["still"] < 5 and state["round"] < 240:
        QtCore.QTimer.singleShot(200, step)
        return
    try:
        judge()
    except Exception:
        import traceback
        traceback.print_exc()
        bad.append("the judging fell over")
    app.quit()


def deadline():
    """An outer brake only: the waiting inside is on the widths."""
    bad.append("the window never finished: 120 s gone, at turn %d"
               % state["round"])
    app.quit()


QtCore.QTimer.singleShot(300, step)
brake = QtCore.QTimer()
brake.setSingleShot(True)
brake.timeout.connect(deadline)
brake.start(120000)
try:
    vpm.gui()
except Exception:
    import traceback
    traceback.print_exc()
    bad.append("the window never came up: gui() fell over")
brake.stop()

print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
