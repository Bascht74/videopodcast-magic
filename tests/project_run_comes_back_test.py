# -*- coding: utf-8 -*-
"""Opening a project takes up the handover its own run left behind.

The note printed after an open promises "Create Resolve project -- from
that run's handover file", and the button hung on a state nobody filled
while opening. Three projects over one material in one window: nothing
in the output folder, the handover of its own run, and one of an earlier
round over a single camera. Read off the search, the button, and the
preview, which has to show the run's speakers rather than work them out
again from the raw tracks -- and has to follow that file when it is
written again, which is what turning a number above does.

Last the sheet that reads the recordings itself, opened where no run
answered the question. That reading costs minutes on the graphics card,
so a reading that came to nothing must not be set going a second time
by the next look at the sheet.
"""
import os
import time

HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = os.environ.get("VPM_SCRIPT") or os.path.join(
    os.path.dirname(HERE), "videopodcast_magic.py")

import importlib.util
import json
import shutil
import subprocess
import sys
import tempfile
import wave

import numpy as np

os.environ["QT_QPA_PLATFORM"] = "offscreen"
from PySide6 import QtCore, QtWidgets

began = time.time()
app = QtWidgets.QApplication(sys.argv[:1])
spec = importlib.util.spec_from_file_location("vpm", SCRIPT)
vpm = importlib.util.module_from_spec(spec)
sys.modules["vpm"] = vpm
spec.loader.exec_module(vpm)
vpm.set_language("en")
vpm.list_presets = lambda key: []
vpm.load_api_key = lambda: ""
vpm.say_dialog = lambda *a, **k: True     # no dialog waits for anybody
# The builder has no Resolve, and this test is not about whether it is
# installed: the button is grey without it whatever the handover says.
vpm.resolve_installed = lambda: True

# Every reading of the recordings the window sets going, counted where
# it is set going: it runs in a thread of its own and costs minutes on
# the graphics card, so how often it is started is what the last
# section is about. The real reading follows it unchanged.
measurements = []
_really_measure = vpm.speaker_measure_loop


def counted_measure(tracks, bridge, bridge_emit):
    measurements.append(len(tracks))
    _really_measure(tracks, bridge, bridge_emit)


vpm.speaker_measure_loop = counted_measure

done = 0
bad = []


def check(name, ok, extra=""):
    global done
    done += 1
    print("  %-58s %s %s" % (name, "ok" if ok else "FAIL", extra))
    if not ok:
        bad.append("%s [%s]" % (name, extra or "no numbers"))


RATE, SEC = 48000, 4
folder = tempfile.mkdtemp(prefix="vpm_comesback_")
bare_folder = os.path.join(folder, "Bare")
run_folder = os.path.join(folder, "Run")
short_folder = os.path.join(folder, "Short")
for _d in (bare_folder, run_folder, short_folder):
    os.makedirs(_d, exist_ok=True)


def tone(name, hz=300.0):
    path = os.path.join(folder, name)
    t = np.arange(SEC * RATE) / float(RATE)
    with wave.open(path, "wb") as f:
        f.setnchannels(1)
        f.setsampwidth(2)
        f.setframerate(RATE)
        f.writeframes((0.4 * np.sin(2 * np.pi * hz * t) * 32767)
                      .astype("<i2").tobytes())
    return path


def clip(name, where=None):
    path = os.path.join(where or folder, name)
    subprocess.run(["ffmpeg", "-v", "error", "-f", "lavfi", "-i",
                    "testsrc=size=160x90:rate=25:duration=%d" % SEC,
                    "-f", "lavfi", "-i",
                    "sine=frequency=440:duration=%d" % SEC,
                    "-c:v", "libx264", "-preset", "ultrafast", "-pix_fmt",
                    "yuv420p", "-c:a", "aac", "-shortest", "-y", path],
                   check=True)
    return path


audio = tone("A_speaker.wav")
cams = [clip(n) for n in ("B_Presenter.mov", "C_Guest.mov", "D_WideCam.mov")]
# A rendered file in each output folder, so both projects print the same
# "PROJECT OPENED" note and the two readings differ in one thing only.
for where in (bare_folder, run_folder, short_folder):
    shutil.copy(cams[0], os.path.join(where, "Presenter.mov"))

# The run measured four minutes of it, in turns of twenty seconds. The
# window itself can measure nothing here: four seconds of a sine wave on
# one track is neither of these two people.
LENGTH = 240.0
TURNS = {"Presenter": [[float(a), float(a + 20)]
                       for a in range(0, int(LENGTH), 40)],
         "Guest": [[float(a), float(a + 20)]
                   for a in range(20, int(LENGTH), 40)]}
SPEAKERS = ["Presenter", "Guest"]
HANDOVER = os.path.join(run_folder, "Episode_resolve.json")


def a_camera(source, name, speakers, wide):
    return {"file": source, "source": source, "camera": name,
            "track": name, "speakers": speakers, "audio_tracks": [],
            "offset": 0.0, "duration": LENGTH, "fps": 25.0,
            "wide_marked": wide, "wide": wide}


with open(HANDOVER, "w", encoding="utf-8") as f:
    json.dump({"format": vpm.FILE_FORMAT, "created_by": "test",
               "production": "Episode", "fps": 25, "fps_measured": 25.0,
               "drop_frame": False, "width": 160, "height": 90,
               "start_tc": None, "start_s": 0.0, "length_s": LENGTH,
               "cameras": [a_camera(cams[0], "Presenter", ["Presenter"],
                                    False),
                           a_camera(cams[1], "Guest", ["Guest"], False),
                           a_camera(cams[2], "WideCam", [], True)],
               "cut": [{"start": 0.0, "end": LENGTH, "camera": "WideCam"}],
               "speakers": [{"name": n, "sections": TURNS[n]}
                            for n in SPEAKERS],
               "audio_files": {}, "words": []}, f)


# The handover of an earlier round over the same material, one camera
# of the three. A cut out of it is not the cut of this project, and it
# looks exactly like a fresh one.
SHORT_HANDOVER = os.path.join(short_folder, "Earlier_resolve.json")
with open(SHORT_HANDOVER, "w", encoding="utf-8") as f:
    json.dump({"format": vpm.FILE_FORMAT, "created_by": "an earlier run",
               "production": "Earlier", "fps": 25, "fps_measured": 25.0,
               "drop_frame": False, "width": 160, "height": 90,
               "start_tc": None, "start_s": 0.0, "length_s": LENGTH,
               "cameras": [a_camera(cams[0], "Presenter", ["Presenter"],
                                    False)],
               "cut": [{"start": 0.0, "end": LENGTH, "camera": "Presenter"}],
               "speakers": [{"name": "Presenter",
                             "sections": TURNS["Presenter"]}],
               "audio_files": {}, "words": []}, f)


def project_file(name, target):
    """One project over this material, writing into that output folder."""
    path = os.path.join(folder, "videopodcast-magic_%s.json" % name)
    with open(path, "w", encoding="utf-8") as f:
        json.dump({"format": vpm.FILE_FORMAT, "version": "test",
                   "timeline": [], "call": [],
                   "files": [{"path": audio, "kind": "audio"}]
                            + [{"path": p, "kind": "video"} for p in cams],
                   "out_folder": target, "production": name,
                   "multitrack": True, "assignment": {}, "preset": ""}, f)
    return path


BARE = project_file("Bare", bare_folder)
WITH_RUN = project_file("Run", run_folder)
SHORT = project_file("Short", short_folder)
wanted = [BARE]
QtWidgets.QFileDialog.getOpenFileName = staticmethod(
    lambda *a, **k: (wanted[0], ""))
QtWidgets.QDialog.exec = lambda self: QtWidgets.QDialog.Accepted


def win():
    for x in app.topLevelWidgets():
        if "Video Podcast Magic" in x.windowTitle():
            return x


def button(word):
    for w in win().findChildren(QtWidgets.QPushButton):
        if w.text().strip().startswith(word):
            return w


def tab_bar():
    """The bar of sheets, found by the one tab that is always there."""
    for tw in win().findChildren(QtWidgets.QTabWidget):
        if tw.count() and tw.tabText(0).startswith(
                vpm.T('Files && production')):
            return tw


def resolve_button():
    return button(vpm.T('Create Resolve project'))


def enabled():
    """Whether that button can be pressed, or None where it is not there."""
    b = resolve_button()
    return None if b is None else b.isEnabled()


HEADS = {"run": vpm.speech_heading("run"),
         "tracks": vpm.speech_heading(True),
         "voices": vpm.speech_heading(False)}


def speech_head():
    """Which of the three sources the speech table says it shows."""
    for w in win().findChildren(QtWidgets.QLabel):
        for key, text in HEADS.items():
            if w.text().startswith(text):
                return key
    return "no heading"


def speech_names():
    """The speakers the speech table lists, silence left out."""
    for t in win().findChildren(QtWidgets.QTableWidget):
        return [t.item(r, 0).text() for r in range(t.rowCount())
                if t.item(r, 0) is not None
                and t.item(r, 0).text() != vpm.T('Silence')]
    return []


def cut_sheet():
    """The Resolve sheet, found by its name in the bar of sheets."""
    tw = tab_bar()
    if tw is None:
        return None
    for i in range(tw.count()):
        if tw.tabText(i).startswith(vpm.T('Resolve cut')):
            return tw.widget(i)
    return None


def sheets_offered():
    """The sheets the bar holds, for a failure line."""
    tw = tab_bar()
    return [] if tw is None else [tw.tabText(i) for i in range(tw.count())]


def sheet_says():
    """Everything the Resolve sheet has in words, as a person reads it.

    Read off the whole sheet rather than off one label picked out
    beforehand: what used to name that label -- the button it stood
    beside -- is gone, and its tooltip is wording like any other and
    moves when somebody rewrites it. The sentences looked for below
    all go through T() and are the program's own.
    """
    sheet = cut_sheet()
    if sheet is None:
        return []
    return [w.text().strip() for w in sheet.findChildren(QtWidgets.QLabel)
            if w.text().strip()]


def measure_note():
    """What the sheet says, short enough for a failure line.

    The sheet also carries the paragraph that explains the settings,
    which is longer than a whole failure line may be and carries line
    breaks a register row cannot hold. So: the short lines only, the
    last of them, which is where the one about the speakers sits.
    """
    said = [" ".join(x.split()) for x in sheet_says()]
    short = [x for x in said if len(x) < 70]
    return "%d lines on the sheet, the last short ones %s" % (len(said),
                                                              short[-6:])


def open_cut_sheet():
    """Click on the Resolve sheet, the way a person does."""
    tw, sheet = tab_bar(), cut_sheet()
    if tw is None or sheet is None:
        return False
    tw.setCurrentWidget(sheet)
    app.processEvents()
    return True


def look_away_and_back():
    """Off the Resolve sheet and onto it again, as a person would."""
    tw = tab_bar()
    if tw is None:
        return False
    tw.setCurrentIndex(0)
    app.processEvents()
    return open_cut_sheet()


def cut_cameras():
    """The cameras the preview's cut switches between."""
    for w in win().findChildren(QtWidgets.QWidget):
        if hasattr(w, "audio_offset") and hasattr(w, "cut"):
            return sorted({who for _a, _b, who in (getattr(w, "cut", None)
                                                   or [])})
    return []


def taken():
    """The handover this open brought back, or "" if none did."""
    return (found[-1][1] or "") if found else ""


def looked_in():
    """The folders this open searched, as the window named them."""
    return list(found[-1][0]) if found else []


def named(path):
    """Whether the title bar names this project file."""
    return os.path.basename(path) in win().windowTitle()


def ground():
    """One line naming everything a judgement below rests on."""
    return ("the title %r, the button is %s, the open searched %s and "
            "brought back %r"
            % (win().windowTitle(),
               {True: "usable", False: "grey", None: "not there"}[enabled()],
               [os.path.basename(p) for p in looked_in()] or "nowhere",
               os.path.basename(taken()) or "no handover"))


# Read off the search itself, never off a variable set by hand: what is
# wanted is that opening a project asks this question, in that folder,
# and takes the answer.
found = []
_really_find = vpm.find_handover_file


def _watched(*places, **kw):
    got = _really_find(*places, **kw)
    found.append((tuple(places), got))
    return got


vpm.find_handover_file = _watched

n = [0]
seen = [-1]
still = [0]
patience = [0]
sign = [None]
over = set()
same = {}


def life():
    """A sign that moves only because the window is working.

    The line about the speakers is in it because the last section
    waits for a reading to come back, and that reading moves nothing
    else here: without it a step would stand still while the window
    was working the whole time.
    """
    w = win()
    tw = tab_bar() if w is not None else None
    return (w.windowTitle() if w is not None else None,
            tw.count() if tw is not None else -1,
            enabled() if w is not None else None,
            measure_note() if w is not None else None)


class NotYet(Exception):
    """The window has not caught up; wait and ask again."""


def needed(what, thing):
    if thing is None or thing is False:
        raise NotYet(what)
    return thing


def deadline():
    """The whole pass has taken 240 s: red, and it says where.

    An outer brake and nothing else -- the waiting inside the pass is
    on standstill, not on this clock. It is set where it is because
    there is no timeout(1) on the machine this was written on and a
    window that never comes must not hold the suite: 11 s here, and
    the builder runs about nine times slower, worst measured 12.6.
    """
    def fired():
        if "the pass" in over:
            return          # the pass is over; this timer is only late
        bad.append("the pass never finished: 240 s gone, still at step %d"
                   % n[0])
        app.quit()
    return fired


def settled():
    """Wait until the tab count has stopped moving."""
    tw = needed("the tab bar", tab_bar())
    if tw.count() != seen[0]:
        seen[0], still[0] = tw.count(), 0
    else:
        still[0] += 1
    if still[0] < 5:
        raise NotYet("the tabs to stop arriving, %d of them for %d rounds"
                     % (tw.count(), still[0]))
    return tw


def step():
    i = n[0]
    print("   step %d" % i, flush=True)
    try:
        if i == 0:
            needed("the window", win()).show()
            win().resize(1400, 900)
            app.processEvents()
            same["window"] = win()
            wanted[0] = BARE
            needed("the Open project button",
                   button(vpm.T('Open project ...'))).click()
        elif i == 1:
            if not named(BARE):
                raise NotYet("the first project in the title bar, which "
                             "reads %r" % win().windowTitle())
            settled()
            print("1. A project whose output folder holds no handover")
            check("the button that builds the Resolve project is on the "
                  "window before anything is read off it",
                  resolve_button() is not None, ground())
            check("opening a project looks for a handover in that "
                  "project's own output folder",
                  os.path.abspath(bare_folder) in
                  [os.path.abspath(p) for p in looked_in() if p],
                  "%d searches, the last one in %s, wanted %s"
                  % (len(found), looked_in() or "nowhere", bare_folder))
            check("a project whose output folder holds no handover leaves "
                  "Create Resolve project grey",
                  enabled() is False, ground())
            check("no handover is taken out of the output folder of "
                  "another project",
                  taken() == "",
                  "the open brought back %r while %s lies in the other "
                  "output folder -- %s"
                  % (taken(), os.path.basename(HANDOVER), ground()))
            wanted[0] = WITH_RUN
            seen[0], still[0] = -1, 0
            needed("the Open project button",
                   button(vpm.T('Open project ...'))).click()
        elif i == 2:
            if not named(WITH_RUN):
                raise NotYet("the second project in the title bar, which "
                             "reads %r" % win().windowTitle())
            settled()
            print("\n2. A project whose output folder holds the handover "
                  "of its run")
            check("opening another project searches that project's own "
                  "output folder and not the one before it",
                  os.path.abspath(run_folder) in
                  [os.path.abspath(p) for p in looked_in() if p]
                  and os.path.abspath(bare_folder) not in
                  [os.path.abspath(p) for p in looked_in() if p],
                  "searched %s, wanted %s and not %s; the window is %s the "
                  "one the first project was opened in -- %s"
                  % (looked_in() or "nowhere", run_folder, bare_folder,
                     "still" if win() is same["window"] else "not",
                     ground()))
            check("the handover an open brings back is the one lying in "
                  "that project's own output folder",
                  bool(taken()) and
                  os.path.abspath(taken()) == os.path.abspath(HANDOVER),
                  "the open brought back %r, wanted %r"
                  % (taken() or "nothing", HANDOVER))
            check("a project whose output folder holds a handover makes "
                  "Create Resolve project usable",
                  enabled() is True, ground())
        elif i == 3:
            if speech_head() == "no heading":
                raise NotYet("the preview to say what it stands on, %s"
                             % ground())
            print("\n3. And the preview stands on that run")
            check("the speech table says the speakers come from the run",
                  speech_head() == "run",
                  "the heading is %r, wanted %r"
                  % (speech_head(), "run"))
            check("the speech table lists the run's speakers and not the "
                  "recordings the window could measure",
                  speech_names() == SPEAKERS,
                  "the table lists %s, wanted %s" % (speech_names(),
                                                     SPEAKERS))
            from_run = vpm.cut_basis_line("run", len(SPEAKERS), LENGTH)[0]
            check("the line on the cut sheet says the cut stands on the "
                  "finished run", from_run in sheet_says(),
                  "%r not among the %s" % (from_run, measure_note()))
            check("the cut in the preview runs on the cameras the handover "
                  "names",
                  bool(cut_cameras())
                  and not set(cut_cameras()) - {"Presenter", "Guest",
                                                "WideCam"},
                  "the cut runs on %s" % (cut_cameras() or "nothing"))
            same["cut"] = cut_cameras()
            # What "Create Resolve project" does when a number above is
            # turned: the cut is worked out again and written back under
            # the same name. Here only the Presenter speaks afterwards,
            # so the new cut is plainly another one.
            with open(HANDOVER, encoding="utf-8") as f:
                again = json.load(f)
            again["speakers"] = [{"name": "Presenter",
                                  "sections": [[0.0, LENGTH]]}]
            with open(HANDOVER, "w", encoding="utf-8") as f:
                json.dump(again, f)
        elif i == 4:
            # Waited for, but the waiting must not swallow the verdict:
            # once the rounds are spent the check below says what never
            # arrived, in a line the register can hold.
            same["rounds"] = same.get("rounds", 0) + 1
            if cut_cameras() == same["cut"] and same["rounds"] < 40:
                raise NotYet("the rewritten handover to reach the preview, "
                             "which still runs on %s after %d rounds"
                             % (cut_cameras() or "nothing", same["rounds"]))
            print("\n4. The handover rewritten under the same name")
            check("a handover written again under the same name reaches "
                  "the preview by itself",
                  cut_cameras() == ["Presenter", "WideCam"],
                  "after %d rounds of 400 ms the cut runs on %s, before it "
                  "ran on %s, wanted ['Presenter', 'WideCam']"
                  % (same["rounds"], cut_cameras() or "nothing",
                     same["cut"]))
            wanted[0] = SHORT
            seen[0], still[0] = -1, 0
            needed("the Open project button",
                   button(vpm.T('Open project ...'))).click()
        elif i == 5:
            if not named(SHORT):
                raise NotYet("the third project in the title bar, which "
                             "reads %r" % win().windowTitle())
            settled()
            print("\n5. A handover of an earlier round, one camera of three")
            check("a handover naming fewer cameras than the project holds "
                  "is passed over",
                  taken() == "",
                  "the open brought back %r while %s lies in that very "
                  "output folder -- %s"
                  % (taken(), os.path.basename(SHORT_HANDOVER), ground()))
            check("and Create Resolve project is grey again once such a "
                  "project is opened", enabled() is False, ground())
            # No run answered the question for this project, so opening
            # the Resolve sheet is what sets the reading of the
            # recordings going. Four seconds of an unbroken sine wave
            # is nobody talking, so it comes back with a complaint --
            # which is the state the two judgements below are about.
            if not open_cut_sheet():
                raise NotYet("the Resolve sheet, the window offers %s"
                             % sheets_offered())
        elif i == 6:
            working = vpm.T('working out who speaks when ...')
            if working in sheet_says():
                raise NotYet("the reading to come back, the sheet still "
                             "says %r after %d set going"
                             % (working, len(measurements)))
            print("\n6. The cut sheet where no run answered the question")
            came_to_nothing = vpm.T('Nothing was audible in the tracks.')
            check("a reading that comes to nothing says so on the cut sheet",
                  came_to_nothing in sheet_says(),
                  "%r not among the %s, after %d readings were set going"
                  % (came_to_nothing, measure_note(), len(measurements)))
            came_back = look_away_and_back()
            check("and a reading that failed is not set going a second time",
                  came_back and len(measurements) == 1,
                  "%d readings after looking away and back, wanted 1; the "
                  "sheet %s and there are %s"
                  % (len(measurements),
                     "was opened again" if came_back else "never came back",
                     measure_note()))
        else:
            over.add("the pass")
            app.quit()
            return
        n[0] += 1
        patience[0] = 0
        QtCore.QTimer.singleShot(400, step)
    except NotYet as why:
        moved = life()
        if moved != sign[0]:
            sign[0], patience[0] = moved, 0
        patience[0] += 1
        if patience[0] > 60:
            bad.append("step %d waited for %s: 60 rounds of 400 ms with "
                       "the window at %r not moving at all, and it never "
                       "came" % (i, why, sign[0]))
            over.add("the pass")
            app.quit()
            return
        QtCore.QTimer.singleShot(400, step)
    except Exception:
        import traceback
        traceback.print_exc()
        bad.append("step %d fell over" % i)
        over.add("the pass")
        app.quit()


QtCore.QTimer.singleShot(500, step)
QtCore.QTimer.singleShot(240000, deadline())
# A window that falls over while it is being built takes the event loop
# with it, and the closing lines below are the only place that counts.
try:
    vpm.gui()
except Exception:
    import traceback
    traceback.print_exc()
    bad.append("the window never came up: gui() fell over")

shutil.rmtree(folder, ignore_errors=True)
print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
