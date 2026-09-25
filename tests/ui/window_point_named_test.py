# -*- coding: utf-8 -*-
"""A jump no file can make names the point in the window's language.

One German window over a project whose points lie on a recording's
clock, far past the one camera, and that camera has no timecode. The
sections: the catalogue has a German word for each point; the sheet
comes up with both jump buttons live; "to In point" and "to Out point"
each leave the sentence saying no video file holds that point, opened by
the German word. Offscreen, in Qt's own style.
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
import json
import subprocess
import tempfile
import time
import the_program

os.environ["QT_QPA_PLATFORM"] = "offscreen"
from PySide6 import QtCore, QtWidgets

began = time.time()
app = QtWidgets.QApplication(sys.argv[:1])
vpm = the_program.load()
vpm.set_language("en")
english = (vpm.T('In point'), vpm.T('Out point'))
vpm.set_language("de")
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
    """A recording on a 10:00:00 clock and a camera with none, 12 s."""
    made = {n: os.path.join(folder, n) for n in ("Room_tc.wav", "A_cam.mov")}
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
         "yuv420p", "-shortest", "-y", made["A_cam.mov"]],
        check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return made


made = material(tempfile.mkdtemp(prefix="vpm_point_"))
project = os.path.join(tempfile.mkdtemp(prefix="vpm_point_p_"),
                       "videopodcast-magic_Point.json")
# Both points ten hours past the recording's clock: no file holds them.
with open(project, "w", encoding="utf-8") as f:
    json.dump({"format": vpm.FILE_FORMAT, "version": "test",
               "timeline": [], "preset": "", "production": "Point",
               "multitrack": False, "project_type": "cut",
               "in_point": "20:00:00:00", "out_point": "20:00:05:00",
               "out_folder": os.path.join(os.path.dirname(project),
                                          "Result"),
               "assignment": {
                   "audio:" + made["Room_tc.wav"]: ["Guest", "A_cam.mov"]},
               "files": [{"path": made["Room_tc.wav"], "kind": "audio"},
                         {"path": made["A_cam.mov"], "kind": "video"}]}, f)
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
    """Press both jump buttons and read the sentence each leaves."""
    words = (vpm.T('In point'), vpm.T('Out point'))
    check("the German catalogue has a word of its own for each point",
          words[0] != english[0] and words[1] != english[1],
          "de %r and %r, en %r and %r" % (words + english))
    to_in, to_out = button('to In point'), button('to Out point')
    live = [b is not None and b.isEnabled() for b in (to_in, to_out)]
    check("the sheet came up with both jump buttons live", all(live),
          "to In point %s, to Out point %s" % tuple(live))
    if not all(live):
        return
    to_in.click()
    app.processEvents()
    got = said()
    check("to In point says no file holds the In point, in German",
          got == SENTENCE % words[0],
          "reads %r, wanted %r" % (got, SENTENCE % words[0]))
    to_out.click()
    app.processEvents()
    got = said()
    check("to Out point says no file holds the Out point, in German",
          got == SENTENCE % words[1],
          "reads %r, wanted %r" % (got, SENTENCE % words[1]))


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
    judge()
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
