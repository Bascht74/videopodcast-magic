# -*- coding: utf-8 -*-
"""A relative mark means in the window what it means in the run.

No file carries a clock; a recorder rolls first, the cameras later.
Sections: the axis; Mark In and Mark Out, counted from where every
camera runs; the preview cut there; "to In point" back to that picture;
an Out point counted back from where the first camera stops, in the
preview, the player, the window's length and a run; an In point counted
back, refused by the player as by the run; the run cutting at the same
pictures; its handover, not cut again. The limit: one camera in the
player.
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
from let_go import clean_up

SCRIPT = the_program.SCRIPT

os.environ["QT_QPA_PLATFORM"] = "offscreen"
os.environ["VPM_SILENT"] = "1"
os.environ["VPM_NO_UPDATE_CHECK"] = "1"
os.environ["VPM_NO_SPEAKER_SPLIT"] = "1"

import glob
import json
import re
import subprocess
import tempfile
import time
import wave

import numpy as np
from PySide6 import QtCore, QtWidgets

app = QtWidgets.QApplication(sys.argv[:1])
vpm = the_program.load()
vpm.list_presets = lambda key: []
vpm.load_api_key = lambda: ""
vpm.update_offer = lambda *a, **k: None
vpm.set_language("en")

POLL = 200
STILL = 100
WINDOW = (1400, 950)

began = time.time()
done = 0
bad = []


def check(name, ok, extra=""):
    global done
    done += 1
    print("  %-58s %s %s" % (name, "ok" if ok else "FAIL", extra))
    if not ok:
        bad.append("%s [%s]" % (name, extra or "no numbers"))


# ------------------------------------------------------------ the material
# Seconds of the events: the recorders roll at 0, the wide camera at 10,
# the guest camera at 25 -- so every camera runs from 25 on, and the
# earliest file of all is 25 seconds earlier than that.
RATE = 8000
LENGTH = 150.0
WIDE_ROLLS, GUEST_ROLLS, GUEST_STOPS = 10.0, 25.0, 140.0
EVERY_CAMERA = 25.0
# Where the player is put in the wide camera's file for the two marks,
# and what the marks then have to say: seconds after EVERY_CAMERA.
IN_AT, OUT_AT = 45.0, 115.0
IN_SAYS, OUT_SAYS = 30.0, 100.0
# An Out point typed counted back from the end: from where the guest
# camera stops, in the wide camera's seconds -- not from its own end.
FROM_END = "-0:00:20"
FROM_END_AT = GUEST_STOPS - 20.0 - WIDE_ROLLS
AWAY_AT = 5.0
FRAME = 1.0 / 25
NEAR = 0.02
SPLIT = "Presenter_REC00021.wav"
PLAIN = "Guest_REC00022.wav"
WIDE = "WideCam_C001.mov"
GUEST = "GuestCam_C002.mov"
SEGMENTS = [["V0", 1.0, 20.0], ["V1", 21.0, 40.0], ["V0", 41.0, 70.0],
            ["V1", 71.0, 100.0], ["V0", 101.0, 130.0], ["V1", 131.0, 148.0]]


def turns(seconds, seed):
    """Speech-like turns: noise in irregular pieces with pauses between."""
    rng = np.random.default_rng(seed)
    n = int(seconds * RATE)
    x = np.zeros(n)
    t = 0.2
    while t < seconds - 1.0:
        long_s = float(rng.uniform(0.3, 3.0))
        k, i0 = int(long_s * RATE), int(t * RATE)
        k = min(k, n - i0)
        if k > 2:
            x[i0:i0 + k] = rng.normal(0, 0.25, k) * np.hanning(k)
        t += long_s + float(rng.uniform(0.2, 2.5))
    return x


def write(path, x):
    with wave.open(path, "wb") as f:
        f.setnchannels(1)
        f.setsampwidth(2)
        f.setframerate(RATE)
        f.writeframes((np.clip(x, -1, 1) * 32000).astype("<i2").tobytes())


FOLDER = tempfile.mkdtemp(prefix="vpm_zero_")
D = os.path.join(FOLDER, "Zero")
os.makedirs(D)
one, other = turns(LENGTH, 5), turns(LENGTH, 6)
other = other * (np.abs(one) < 1e-6)
rng = np.random.default_rng(1)
mix = 0.5 * one + 0.5 * other + rng.normal(0, 0.004, len(one))
write(os.path.join(D, SPLIT), one + 0.15 * other
      + rng.normal(0, 0.003, len(one)))
write(os.path.join(D, PLAIN), other + 0.15 * one
      + rng.normal(0, 0.003, len(one)))
write(os.path.join(FOLDER, "w.wav"), mix[int(WIDE_ROLLS * RATE):])
write(os.path.join(FOLDER, "g.wav"),
      mix[int(GUEST_ROLLS * RATE):int(GUEST_STOPS * RATE)])
# A tiny picture at 25 frames, and no timecode anywhere.
command = ["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i",
           "color=size=64x36:rate=25",
           "-i", os.path.join(FOLDER, "w.wav"),
           "-i", os.path.join(FOLDER, "g.wav")]
for name, n in ((WIDE, 1), (GUEST, 2)):
    command += ["-map", "0:v", "-map", "%d:a" % n, "-shortest", "-c:v",
                "libx264", "-preset", "ultrafast", "-c:a", "pcm_s16le",
                os.path.join(D, name)]
subprocess.run(command, check=True)
HERE_IS = dict((n, os.path.join(D, n)) for n in (SPLIT, PLAIN, WIDE, GUEST))


def own_project():
    """The project file the window opens: the four files and two voices."""
    assignment = {"voice:V0": HERE_IS[WIDE], "voice:V1": HERE_IS[GUEST],
                  "several:" + HERE_IS[SPLIT]: True}
    st = os.stat(HERE_IS[SPLIT])
    d = {"format": vpm.FILE_FORMAT, "version": "test", "timeline": [],
         "files": [{"path": HERE_IS[n],
                    "kind": "video" if n.endswith(".mov") else "audio"}
                   for n in (SPLIT, PLAIN, WIDE, GUEST)],
         "out_folder": os.path.join(FOLDER, "Result"),
         "production": "Zero", "multitrack": True,
         "assignment": assignment, "preset": "",
         "speakers": {"source": os.path.abspath(HERE_IS[SPLIT]),
                      "mtime": int(st.st_mtime), "size": st.st_size,
                      "model": vpm.SPEAKER_MODEL_NAME, "model_mark": "",
                      "num_speakers": 2,
                      "names": {"V0": "Host", "V1": "Guest"},
                      "segments": SEGMENTS}}
    os.makedirs(d["out_folder"], exist_ok=True)
    path = os.path.join(FOLDER, "videopodcast-magic_Zero.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(d, f, indent=1)
    return path


PROJECT = own_project()
QtWidgets.QFileDialog.getOpenFileName = staticmethod(
    lambda *a, **k: (PROJECT, ""))
QtWidgets.QDialog.exec = lambda self: QtWidgets.QDialog.Accepted
QtWidgets.QMessageBox.exec = lambda self: QtWidgets.QMessageBox.Ok
_show = QtWidgets.QWidget.show


def offstage(self):
    self.setAttribute(QtCore.Qt.WA_DontShowOnScreen, True)
    _show(self)


QtWidgets.QWidget.show = offstage
QtWidgets.QDialog.show = offstage

# The preview looks the trimming up in the module when it calls it, so
# a spy here reads where it put the window's start, on the axis.
seen = []
_real_window = vpm.apply_time_window


def window_spy(d, in_point, out_point):
    out = _real_window(d, in_point, out_point)
    seen.append({"in": in_point, "out": out_point, "complaint": out[1],
                 "start": out[0].get("start_s"),
                 "length": out[0].get("length_s")})
    return out


vpm.apply_time_window = window_spy


# ------------------------------------------------------- reading the window
def drawn(text):
    return str(text).replace("&&", "\x00").replace("&", "") \
                    .replace("\x00", "&")


def window_of():
    for x in app.topLevelWidgets():
        if "Video Podcast Magic" in x.windowTitle():
            return x
    return None


def button_named(text):
    top = window_of()
    for b in ([] if top is None else top.findChildren(QtWidgets.QPushButton)):
        if drawn(b.text()).strip() == text:
            return b
    return None


def preview_player():
    """The player the mark buttons sit in, found from the button."""
    b = None
    for x in app.allWidgets():
        if isinstance(x, QtWidgets.QPushButton) \
                and drawn(x.text()).strip() == drawn(vpm.T('Mark In')):
            b = x
    up = None if b is None else b.parentWidget()
    while up is not None and not hasattr(up, "spot_s"):
        up = up.parentWidget()
    return up


def mark_seconds(text):
    """Read "+H:MM:SS.mmm" by hand, not by the program."""
    m = re.match(r"^\+(\d+):(\d\d):(\d\d)(?:[.,](\d+))?$", (text or "").strip())
    if not m:
        return None
    frac = float("0." + m.group(4)) if m.group(4) else 0.0
    return int(m.group(1)) * 3600 + int(m.group(2)) * 60 \
        + int(m.group(3)) + frac


def timeline():
    """Where the project file puts each file on the axis, by name."""
    try:
        with open(PROJECT, encoding="utf-8") as f:
            d = json.load(f)
    except (OSError, ValueError):
        return {}
    return dict((os.path.basename(e.get("path") or ""), e.get("start_s"))
                for e in d.get("timeline") or ())


def fields():
    """The two marks as the window holds them: the lines under the player."""
    p = preview_player()
    said = {}
    for caption, key in (('In point %s', "in"), ('Out point %s', "out")):
        head = drawn(vpm.T(caption)).replace("%s", "").strip()
        for x in ([] if p is None else p.findChildren(QtWidgets.QLabel)):
            text = drawn(x.text()).strip()
            if text.startswith(head):
                said[key] = text[len(head):].strip()
    return said.get("in", ""), said.get("out", "")


# ------------------------------------------------------------- the driver
plan = []
at = [0]
polls = [0]
still = [0]
sign = [None]
mark = [0]
kept = {}


def alive():
    p = preview_player()
    try:
        where = round(p.spot_s(), 3)
    except AttributeError:
        where = None
    return (len(seen), where, fields(), len(timeline()))


def step(say, do, then, until=None, watch=False):
    plan.append({"say": say, "do": do, "then": then, "watch": watch,
                 "until": until or (lambda: True), "begun": False})


def drive():
    if at[0] >= len(plan):
        app.quit()
        return
    job = plan[at[0]]
    if not job["begun"]:
        job["begun"] = True
        polls[0] = still[0] = 0
        sign[0] = alive()
        mark[0] = len(seen)
        try:
            job["do"]()
        except Exception:
            import traceback
            traceback.print_exc()
            check("every step was answered", False,
                  "%s -- the answer could not be given" % job["say"])
        QtCore.QTimer.singleShot(150, drive)
        return
    fresh = seen[mark[0]:]
    try:
        settled = ((not job["watch"]) or bool(fresh)) and job["until"]()
    except Exception:
        settled = False
    if not settled:
        now = alive()
        still[0] = 0 if now != sign[0] else still[0] + 1
        sign[0] = now
        polls[0] += 1
        if still[0] < STILL:
            QtCore.QTimer.singleShot(POLL, drive)
            return
        print("\n%s" % job["say"])
        check("every step was answered", False,
              "%s -- nothing moved for %.1f s of %.1f s waited"
              % (job["say"], still[0] * POLL / 1000.0,
                 polls[0] * POLL / 1000.0))
    else:
        print("\n%s" % job["say"])
    try:
        job["then"](fresh[-1] if fresh else None)
    except Exception:
        import traceback
        traceback.print_exc()
        check("every step was answered", False,
              "%s -- the reading could not be taken" % job["say"])
    at[0] += 1
    QtCore.QTimer.singleShot(50, drive)


def open_project():
    for b in window_of().findChildren(QtWidgets.QPushButton):
        if drawn(b.text()).strip().startswith(vpm.T('Open project ...')[:8]):
            b.click()
            return


def to_assignment():
    top = window_of()
    for bar in top.findChildren(QtWidgets.QTabWidget):
        for k in range(bar.count()):
            if drawn(vpm.T('Assignment')).lower() \
                    in drawn(bar.tabText(k)).lower():
                bar.setCurrentIndex(k)
    app.processEvents()


def player_ready():
    p = preview_player()
    try:
        return bool(p is not None and p.player.duration() > 0)
    except AttributeError:
        return False


def axis_there():
    return all(timeline().get(n) is not None for n in (WIDE, GUEST))


def ground(_fresh):
    t = timeline()
    wide, guest = t.get(WIDE), t.get(GUEST)
    check("the window puts the guest camera 15 s after the wide one",
          wide is not None and guest is not None
          and abs((guest - wide) - (GUEST_ROLLS - WIDE_ROLLS)) <= FRAME,
          "wide at %s s, guest at %s s on the axis, %.1f s apart wanted"
          % (wide, guest, GUEST_ROLLS - WIDE_ROLLS))
    check("and the earliest recorder 10 s before the wide camera",
          wide is not None and t.get(SPLIT) is not None
          and abs((wide - t[SPLIT]) - WIDE_ROLLS) <= FRAME,
          "recorder at %s s, wide at %s s, %.1f s apart wanted"
          % (t.get(SPLIT), wide, WIDE_ROLLS))


def load_wide():
    preview_player().load(HERE_IS[WIDE], 0.0)


def wide_loaded():
    p = preview_player()
    return (player_ready() and os.path.basename(
        getattr(p, "file_path", "") or "") == WIDE)


def move_to(seconds):
    def do():
        p = preview_player()
        p.slider.setValue(int(seconds * 1000))
        p.released()
        app.processEvents()
    return do


def stands_at(seconds):
    def ok():
        try:
            return abs(preview_player().spot_s() - seconds) <= NEAR
        except AttributeError:
            return False
    return ok


def press(caption):
    def do():
        button_named(drawn(vpm.T(caption))).click()
    return do


def in_marked(fresh):
    said = fields()[0]
    kept["in"] = said
    got = mark_seconds(said)
    check("Mark In counts from where every camera runs, as the run does",
          got is not None and abs(got - IN_SAYS) <= FRAME,
          "%r is %s s, wanted %.1f s: the wide camera's %.1f s less the "
          "%.1f s before the guest camera rolls" % (
              said, got, IN_SAYS, IN_AT, GUEST_ROLLS - WIDE_ROLLS))
    start = None if fresh is None else fresh["start"]
    # From the earliest recorder's place on the axis, not the handover's
    # start: the preview's handover itself begins where every camera runs.
    origin = timeline().get(SPLIT)
    wanted = WIDE_ROLLS + IN_AT
    check("the preview cuts at the picture Mark In was pressed on",
          start is not None and origin is not None
          and abs((start - origin) - wanted) <= FRAME,
          "the preview's window starts %s s after the earliest recording, "
          "wanted %.1f s; complaint %r" % (
              None if start is None or origin is None
              else round(start - origin, 3), wanted,
              None if fresh is None else fresh["complaint"]))


def out_marked(_fresh):
    said = fields()[1]
    kept["out"] = said
    got = mark_seconds(said)
    check("Mark Out counts from the same point as Mark In",
          got is not None and abs(got - OUT_SAYS) <= FRAME,
          "%r is %s s, wanted %.1f s" % (said, got, OUT_SAYS))


def back_at_in(_fresh):
    p = preview_player()
    where = None if p is None else p.spot_s()
    check("to In point goes back to the picture Mark In was pressed on",
          where is not None and abs(where - IN_AT) <= FRAME,
          "the player stands at %s s of %s, wanted %.1f s" % (
              None if where is None else round(where, 3),
              os.path.basename(getattr(p, "file_path", "") or ""), IN_AT))


def type_from_end():
    window_of().assignment_sheet.model.out_point.set(FROM_END)


def from_end_previewed(fresh):
    start = None if fresh is None else fresh["start"]
    # From the earliest recorder's place, as for Mark In above.
    origin = timeline().get(SPLIT)
    length = None if fresh is None else fresh["length"]
    ends = (None if None in (start, origin, length)
            else round(start - origin + length, 3))
    wanted = GUEST_STOPS - 20.0
    check("the preview counts an Out point back from the first stop",
          ends is not None and abs(ends - wanted) <= FRAME,
          "the preview's window ends %s s after the earliest recording, "
          "wanted %.1f s; complaint %r" % (
              ends, wanted, None if fresh is None else fresh["complaint"]))


def at_from_end(_fresh):
    p = preview_player()
    where = None if p is None else p.spot_s()
    check("to Out point goes where the run puts that Out point",
          where is not None and abs(where - FROM_END_AT) <= FRAME,
          "the player stands at %s s of %s, wanted %.1f s" % (
              None if where is None else round(where, 3),
              os.path.basename(getattr(p, "file_path", "") or ""),
              FROM_END_AT))


def length_said(_fresh):
    text = drawn(window_of().resolve_sheet.window_info_label.text())
    m = re.search(r"(\d+):(\d\d):(\d\d)[.,](\d+)\s*$", text)
    got = None if not m else (int(m.group(1)) * 3600 + int(m.group(2)) * 60
                              + int(m.group(3)) + float("0." + m.group(4)))
    wanted = FROM_END_AT - IN_AT
    check("the window's length counts an Out point back from the first stop",
          got is not None and abs(got - wanted) <= FRAME,
          "the line says %r, wanted a length of %.1f s" % (text, wanted))


# Not the Out point's value: "to In point" going there would stand still.
IN_FROM_END = "-0:00:40"
REFUSED = vpm.T('%r counts from the end -- that only works for Out point.') \
    % IN_FROM_END


def type_in_from_end():
    window_of().assignment_sheet.model.in_point.set(IN_FROM_END)


def in_from_end_refused(_fresh):
    p = preview_player()
    said = "" if p is None else drawn(p.cut_middle.text())
    check("the player refuses an In point counted from the end, as the run",
          said == drawn(REFUSED),
          "under the rail %r, wanted %r" % (said, drawn(REFUSED)))


def in_from_end_not_jumped(_fresh):
    p = preview_player()
    where = None if p is None else p.spot_s()
    said = drawn(window_of().assignment_sheet.window_label.text())
    check("and to In point stays where it was and says why",
          where is not None and abs(where - FROM_END_AT) <= FRAME
          and said == drawn(REFUSED),
          "the player stands at %s s, wanted %.1f s; the sheet says %r"
          % (None if where is None else round(where, 3), FROM_END_AT, said))


def start():
    top = window_of()
    if top is None:
        check("every step was answered", False, "no window came up")
        app.quit()
        return
    top.resize(*WINDOW)
    app.processEvents()
    drive()


step("1. the project is opened", open_project, lambda _f: None,
     until=lambda: preview_player() is not None)
step("1b. the player goes where the marks are made", to_assignment,
     lambda _f: None, until=player_ready)
step("1c. the time axis is measured", lambda: None, ground,
     until=axis_there)
step("2. the wide camera is in the player", load_wide, lambda _f: None,
     until=wide_loaded)
step("2b. the player is moved to the In point", move_to(IN_AT),
     lambda _f: None, until=stands_at(IN_AT))
step("2c. Mark In is pressed", press('Mark In'), in_marked, watch=True)
step("3. the player is moved to the Out point", move_to(OUT_AT),
     lambda _f: None, until=stands_at(OUT_AT))
step("3b. Mark Out is pressed", press('Mark Out'), out_marked, watch=True)
step("4. the player is moved away", move_to(AWAY_AT), lambda _f: None,
     until=stands_at(AWAY_AT))
step("4b. to In point is pressed", press('to In point'), back_at_in,
     until=stands_at(IN_AT))
step("5. an Out point is typed counted back from the end", type_from_end,
     from_end_previewed, watch=True,
     until=lambda: bool(seen) and seen[-1]["out"] == FROM_END)
step("5b. to Out point is pressed", press('to Out point'), at_from_end,
     until=stands_at(FROM_END_AT))
step("5c. the Resolve tab names the window's length", lambda: None,
     length_said)
step("5d. an In point is typed counted back from the end", type_in_from_end,
     in_from_end_refused,
     until=lambda: drawn(preview_player().cut_middle.text())
     == drawn(REFUSED))
step("5e. to In point is pressed", press('to In point'),
     in_from_end_not_jumped)

QtCore.QTimer.singleShot(1200, start)
QtCore.QTimer.singleShot(420000, app.quit)
sys.argv = ["videopodcast_magic.py"]
vpm.gui()
if not plan or not plan[-1]["begun"]:
    check("every step was run", False,
          "%d of %d" % (sum(1 for j in plan if j["begun"]), len(plan)))


# ------------------------------------------------------------- the run
def run(out, out_point):
    """One run fed the window's In point and *out_point*; its log."""
    p = subprocess.run(
        [sys.executable, SCRIPT, "--without-auphonic", "--no-metrics",
         "--no-speech-recognition", "--no-transcript-file",
         "--in-point", kept.get("in") or "+0:00:00", "--out-point",
         out_point, "--out", out]
        + [HERE_IS[n] for n in (WIDE, GUEST, SPLIT, PLAIN)],
        capture_output=True, text=True, env=dict(os.environ))
    said = (p.stdout or "") + (p.stderr or "")
    check("the run ends green", p.returncode == 0 and "Traceback" not in said,
          "return code %d, Out point %s, %s" % (
              p.returncode, out_point, said[said.find("Traceback"):][:80]))
    return said


print("\n6. The run, fed the two marks the window wrote")
OUT = os.path.join(FOLDER, "run")
log = run(OUT, kept.get("out") or "+0:00:00")


def run_point(which, log):
    """The run's In or Out point, in the wide camera's seconds, off its log."""
    head = vpm.T('    In point   %s\n    Out point  %s').split(
        "\n")[which].split("%s")[0].strip()
    for line in log.splitlines():
        if line.strip().startswith(head):
            m = re.search(r"(\d+):(\d\d):(\d\d)[.,](\d+)", line)
            if m:
                return (int(m.group(1)) * 3600 + int(m.group(2)) * 60
                        + int(m.group(3)) + float("0." + m.group(4)))
    return None


# The wide camera is the longest and so the run's reference: its log
# names the window in that camera's own seconds.
ran_in = run_point(0, log)
ran_out = run_point(1, log)
check("the run cuts at the picture Mark In was pressed on",
      ran_in is not None and abs(ran_in - IN_AT) <= FRAME,
      "the run's In point at %s s of %s, the player stood at %.1f s"
      % (ran_in, WIDE, IN_AT))
check("and at the picture Mark Out was pressed on",
      ran_out is not None and abs(ran_out - OUT_AT) <= FRAME,
      "the run's Out point at %s s of %s, the player stood at %.1f s"
      % (ran_out, WIDE, OUT_AT))

print("\n7. The run, fed the Out point counted back from the end")
from_end_out = run_point(1, run(os.path.join(FOLDER, "from_end"), FROM_END))
check("and the run counts it back from the first stop too",
      from_end_out is not None and abs(from_end_out - FROM_END_AT) <= FRAME,
      "the run's Out point at %s s of %s, wanted %.1f s"
      % (from_end_out, WIDE, FROM_END_AT))

print("\n8. The Resolve tab's preview, over the run's handover")
handover = sorted(glob.glob(os.path.join(OUT, "*_resolve.json")))
d = {}
if handover:
    with open(handover[0], encoding="utf-8") as f:
        d = json.load(f)
again, complaint = _real_window(d, kept.get("in") or "",
                                kept.get("out") or "")
check("the preview does not cut the run's handover a second time",
      bool(d) and not complaint
      and again.get("length_s") == d.get("length_s"),
      "%d handover files; length %s s against the run's %s s, "
      "complaint %r" % (len(handover), again.get("length_s"),
                        d.get("length_s"), complaint))

clean_up(FOLDER)
print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
