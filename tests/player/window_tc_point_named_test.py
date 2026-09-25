# -*- coding: utf-8 -*-
"""A point outside a timecoded camera is named, never jumped past.

Two cameras, 12 s each, on 10:00:00:00 and 11:00:00:00; the In point a
minute before the first, the Out point ten hours past both. Sections:
the sheet comes up with both jump buttons live, the first camera in the
player on its clock; "to In point" and "to Out point" say no file holds
the point and leave the player where it stood; an In point six seconds
in is jumped to, silently; one five seconds into the second camera,
pressed for from the first, names it, loads it, says 5 s while it opens
and lands there with its recording.
"""
import json
import os
import subprocess
import sys
import tempfile
import time
# tests/, where the helpers and state/ lie; this file may stand in a
# folder under it, or in one under that.
HERE = os.path.dirname(os.path.abspath(__file__))
while not os.path.isfile(os.path.join(HERE, "the_program.py")) \
        and os.path.dirname(HERE) != HERE:
    HERE = os.path.dirname(HERE)
sys.path.insert(0, HERE)
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
    """Two recordings and two cameras, 12 s each, a pair per clock.

    Room and A on 10:00:00 hear a tone, Host and B on 11:00:00 a noise:
    the same sound in both pairs would measure A and B as one moment,
    an hour against their clocks. Each camera has a recording on it,
    so neither is the free wide shot the player would take first, and
    A comes first by name.
    """
    made = {n: os.path.join(folder, n) for n in (
        "Room_tc.wav", "A_tc.mov", "Host_tc.wav", "B_tc.mov")}
    for wav, mov, hours, sound in (
            ("Room_tc.wav", "A_tc.mov", 10, "sine=frequency=300:duration=12"),
            ("Host_tc.wav", "B_tc.mov", 11,
             "anoisesrc=color=pink:seed=7:sample_rate=48000:duration=12")):
        subprocess.run(
            ["ffmpeg", "-v", "error", "-f", "lavfi", "-i", sound,
             "-ar", "48000", "-ac", "1",
             "-c:a", "pcm_s16le", "-write_bext", "1", "-metadata",
             "time_reference=%d" % (hours * 3600 * 48000), "-y", made[wav]],
            check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        subprocess.run(
            ["ffmpeg", "-v", "error", "-f", "lavfi", "-i",
             "testsrc=size=160x90:rate=25:duration=12", "-f", "lavfi",
             "-i", sound, "-c:a", "aac", "-ac", "1",
             "-c:v", "libx264", "-preset", "ultrafast", "-pix_fmt",
             "yuv420p", "-timecode", "%02d:00:00:00" % hours, "-shortest",
             "-y", made[mov]],
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
                   "audio:" + made["Room_tc.wav"]: ["Guest", "A_tc.mov"],
                   "audio:" + made["Host_tc.wav"]: ["Presenter",
                                                    "B_tc.mov"]},
               "files": [{"path": made["Room_tc.wav"], "kind": "audio"},
                         {"path": made["Host_tc.wav"], "kind": "audio"},
                         {"path": made["A_tc.mov"], "kind": "video"},
                         {"path": made["B_tc.mov"], "kind": "video"}]}, f)
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


NOW_IN = vpm.T('%s is in %s -- the file is now in the player.')


def shown(text):
    """Whether a visible label reads exactly *text*."""
    return any(label.isVisible() and label.text() == text
               for label in win().findChildren(QtWidgets.QLabel))


def stands(p, name, ms):
    """Wait until *name* is open, its length known, at *ms* for a second.

    On a standstill, not the clock: loading and seeking each move the
    file, the length or the position, and five seconds of none of them
    moving is given up; sixty in all is the outer bound. Returns
    whether it stood there, what it last read, and the seconds waited.
    """
    began_at = moved = time.monotonic()
    seen, there_since = None, None
    while True:
        app.processEvents()
        now = time.monotonic()
        here = (os.path.basename(getattr(p, "file_path", None) or ""),
                p.player.duration(), p.player.position(), p.slider.value())
        if here[0] == name and here[1] > 0 and all(
                abs(v - ms) <= 40 for v in here[2:]):
            there_since = there_since or now
            if now - there_since >= 1.0:
                return True, here, now - began_at
        else:
            there_since = None
        if here != seen:
            seen, moved = here, now
        elif now - moved > 5.0 or now - began_at > 60.0:
            return False, here, now - began_at
        time.sleep(0.02)


def heard(p, name, ms):
    """Wait until the recording *name* sits at *ms* under the picture.

    The same standstill as above, over the recording and where it is.
    Returns whether it got there, what it last read, the seconds waited.
    """
    began_at = moved = time.monotonic()
    seen = None
    while True:
        app.processEvents()
        now = time.monotonic()
        here = (os.path.basename(p.track_path or ""), p.track.position())
        if here[0] == name and abs(here[1] - ms) <= 40:
            return True, here, now - began_at
        if here != seen:
            seen, moved = here, now
        elif now - moved > 5.0 or now - began_at > 60.0:
            return False, here, now - began_at
        time.sleep(0.02)


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
    p.load(made["B_tc.mov"], 5.0)
    marked_at = stands(p, "B_tc.mov", 5000)
    mark_in.click()
    app.processEvents()
    p.load(made["A_tc.mov"], 3.0)
    back = stands(p, "A_tc.mov", 3000)
    wanted = vpm.T('In point %s') % "11:00:05:00"
    check("the In point marked in the second camera reads its clock",
          p.cut_left.text() == wanted,
          "reads %r, wanted %r; B stood %r after %.1f s"
          % (p.cut_left.text(), wanted, marked_at[1], marked_at[2]))
    check("the first camera is back at 3 s with its length known",
          back[0], "read (file, length, position, slider) %r after %.1f s"
          % (back[1], back[2]))
    to_in.click()
    # Read before any event: the second file is still opening here.
    early = p.spot_s()
    landed = stands(p, "B_tc.mov", 5000)
    name = os.path.basename(getattr(p, "file_path", None) or "")
    wanted = NOW_IN % (vpm.T('In point'), "B_tc.mov")
    check("to In point in the second camera names it and loads it",
          name == "B_tc.mov" and shown(wanted),
          "player holds %r, sentence %r shown: %s"
          % (name, wanted, shown(wanted)))
    check("while it opens, the second camera reports 5 s in, not 0",
          abs(early - 5.0) <= 0.04, "reported %.3f s" % early)
    check("to In point in the second camera lands 5 s in and stays",
          landed[0], "read (file, length, position, slider) %r against "
          "5000 ms, after %.1f s" % (landed[1], landed[2]))
    sound = heard(p, "Host_tc.wav", 5000)
    check("the second camera's recording is placed 5 s in with it",
          sound[0], "read (recording, position) %r against 5000 ms, "
          "after %.1f s" % (sound[1], sound[2]))


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
