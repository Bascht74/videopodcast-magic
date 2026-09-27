# -*- coding: utf-8 -*-
"""The window and the run take each other's time axis out of one store.

The interview fixture, each section in a folder and a store of its own.
Window first: the window measures, and a dry run over the same files
takes that axis and puts every file where a run on an empty store puts
it. Run first: a dry run measures, and the window opened on the same
files shows the axis without measuring, every file where the window put
it when it measured itself. The window runs in a process of its own
(--window), its measuring steps counted. The limit: the run's side is
judged by its log, so a run that took the axis and said nothing passes
as one that measured.
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
import glob
import json
import re
import shutil
import subprocess
import tempfile
import time
import the_program

SCRIPT = the_program.SCRIPT
began = time.time()
done = 0
bad = []


def check(name, ok, extra=""):
    global done
    done += 1
    print("  %-58s %s %s" % (name, "ok" if ok else "FAIL", extra))
    if not ok:
        bad.append("%s [%s]" % (name, extra or "no numbers"))


def stop():
    """Count what there is and go; every path ends here."""
    print("\n%d checks in %.2f s" % (done, time.time() - began))
    print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
    sys.exit(1 if bad else 0)


PATIENCE = 150.0       # the builder is nine times slower than this machine
POLL = 0.05

# ------------------------------------------ the window, in its own process
if sys.argv[1:2] == ["--window"]:
    media = sys.argv[2]
    os.environ["QT_QPA_PLATFORM"] = "offscreen"
    os.environ["VPM_NO_UPDATE_CHECK"] = "1"
    os.environ["VPM_NO_SPEAKER_SPLIT"] = "1"
    from PySide6 import QtCore, QtWidgets
    app = QtWidgets.QApplication(sys.argv[:1])
    vpm = the_program.load()
    vpm.set_language("en")
    vpm.update_offer = lambda *a, **k: None
    vpm.list_presets = lambda key: []
    vpm.load_api_key = lambda: ""
    vpm.say_dialog = lambda *a, **k: False
    QtWidgets.QDialog.exec = lambda self: QtWidgets.QDialog.Accepted
    QtWidgets.QMessageBox.exec = lambda self: QtWidgets.QMessageBox.Ok
    # Every step that reads a recording against another, counted.
    measured = []
    for name in ("cameras_on_one_axis", "align_audio_to_video",
                 "join_audio_parts", "sound_places"):
        def counted(*a, _real=getattr(vpm, name), _name=name, **k):
            measured.append(_name)
            return _real(*a, **k)
        setattr(vpm, name, counted)
    files = sorted(glob.glob(os.path.join(media, "*.wav"))
                   + glob.glob(os.path.join(media, "*.mov")))
    QtWidgets.QFileDialog.getOpenFileNames = staticmethod(
        lambda *a, **k: (files, ""))
    answer = {"measured": None, "axis": {}, "why": ""}

    def shown():
        """The window's view as kept in the store, by file name."""
        for path in glob.glob(os.path.join(vpm.cache_folder("stages") or "",
                                           "axis_*.json")):
            try:
                with open(path, encoding="utf-8") as f:
                    kept = json.load(f).get("result") or {}
            except (OSError, ValueError):
                continue
            if kept.get("axis"):
                return dict((os.path.basename(k), v)
                            for k, v in kept["axis"].items())
        return {}

    def drive():
        add = None
        for b in app.allWidgets():
            if isinstance(b, QtWidgets.QPushButton) and b.text().replace(
                    "&", "").strip() == vpm.T('Add files ...'):
                add = b
        if add is None:
            answer["why"] = "no Add button"
        else:
            add.click()
            since = time.time()
            while time.time() - since < PATIENCE and not shown():
                app.processEvents()
                time.sleep(POLL)
            answer["axis"] = shown()
            answer["measured"] = len(measured)
            answer["why"] = "" if answer["axis"] else (
                "no axis kept after %.0f s" % PATIENCE)
        # The last line is the answer; everything above is the program.
        print(json.dumps(answer))
        app.quit()

    QtCore.QTimer.singleShot(2500, drive)
    QtCore.QTimer.singleShot(int(PATIENCE * 1000) + 30000, app.quit)
    sys.argv = ["videopodcast_magic.py"]
    vpm.gui()
    sys.exit(0)

# ---------------------------------------------------------------- the runs
vpm = the_program.load()
vpm.set_language("en")
MEDIA = os.environ.get("VPM_MEDIA") or ""
SOURCES = sorted(glob.glob(os.path.join(MEDIA, "*.wav"))
                 + glob.glob(os.path.join(MEDIA, "*.mov")))
if len(SOURCES) < 3:
    print("SKIPPED: no interview material -- point VPM_MEDIA at the "
          "interview fixture (tests/fixtures.sh builds it; looked in %r)"
          % MEDIA)
    stop()

WORK = tempfile.mkdtemp(prefix="vpm_onestore_")
TAKEN = vpm.T('  Taken from the measurement kept on this machine: the '
              'same files and settings, so nothing is measured again.')


def folder(name):
    """The material in a folder of its own: the window writes beside it."""
    where = os.path.join(WORK, name)
    os.makedirs(where)
    for p in SOURCES:
        try:
            os.link(p, os.path.join(where, os.path.basename(p)))
        except OSError:
            shutil.copy2(p, where)
    return sorted(glob.glob(os.path.join(where, "*.*")))


def dry_run(files, store):
    """A dry run into *store*: its return code and its log."""
    got = subprocess.run(
        [sys.executable, SCRIPT, "--without-auphonic", "--dry-run",
         "--out", os.path.join(WORK, "out"), "--no-speech-recognition"]
        + files, capture_output=True, text=True, errors="replace",
        env=dict(os.environ, VPM_CACHE=store))
    return got.returncode, got.stdout + got.stderr


def window(files, store):
    """The window opened on *files* over *store*: what it said, or why not."""
    got = subprocess.run(
        [sys.executable, os.path.abspath(__file__), "--window",
         os.path.dirname(files[0])], capture_output=True, text=True,
        errors="replace", env=dict(os.environ, VPM_CACHE=store))
    try:
        return json.loads(got.stdout.strip().splitlines()[-1])
    except (ValueError, IndexError):
        return {"measured": None, "axis": {},
                "why": "return code %d, %r" % (got.returncode,
                                               (got.stdout + got.stderr)[-300:])}


def offsets(log):
    """Every file's place as the axis section says it, in its order."""
    return re.findall(r"^  (\S.*?) +offset (-?[0-9:.]+)", log, re.M)


def apart(one, other):
    """The largest difference in place between two views, in ms."""
    if not one or set(one) != set(other):
        return None
    return max(abs(one[k] - other[k]) for k in one) * 1000.0


try:
    print("window first")
    first = folder("first")
    seen = window(first, os.path.join(WORK, "store_a"))
    check("on an empty store the window measures the axis itself",
          bool(seen["measured"]) and len(seen["axis"]) >= 3,
          "%s measuring steps, %d places; %s"
          % (seen["measured"], len(seen["axis"]), seen["why"]))
    rc, took = dry_run(first, os.path.join(WORK, "store_a"))
    check("a dry run takes the axis the window measured",
          rc == 0 and TAKEN in took, "return code %d, taken line there: %s"
          % (rc, TAKEN in took))
    rc, own = dry_run(first, os.path.join(WORK, "store_c"))
    check("and puts every file where a run on an empty store puts it",
          offsets(took) == offsets(own) and bool(offsets(own)),
          "taken %s, measured %s" % (offsets(took), offsets(own)))

    print("\nrun first")
    second = folder("second")
    rc, log = dry_run(second, os.path.join(WORK, "store_b"))
    check("on an empty store the dry run measures the axis itself",
          rc == 0 and TAKEN not in log and bool(offsets(log)),
          "return code %d, taken line there: %s, %d places"
          % (rc, TAKEN in log, len(offsets(log))))
    shown = window(second, os.path.join(WORK, "store_b"))
    check("the window takes the run's axis and measures nothing",
          shown["measured"] == 0 and bool(shown["axis"]),
          "%s measuring steps, %d places; %s"
          % (shown["measured"], len(shown["axis"]), shown["why"]))
    gap = apart(shown["axis"], seen["axis"])
    check("and shows every file where it put it measuring itself",
          gap is not None and gap < 1.0,
          "%s ms apart at most; taken %s, measured %s"
          % (gap, sorted(shown["axis"].items()),
             sorted(seen["axis"].items())))
except Exception as e:
    # A crash ends the runs, not the count: it goes out through stop().
    bad.append("the runs crashed [%r]" % e)
    print("  the runs crashed: %r" % e)
finally:
    shutil.rmtree(WORK, ignore_errors=True)
stop()
