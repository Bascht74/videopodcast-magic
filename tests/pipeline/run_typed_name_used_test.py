# -*- coding: utf-8 -*-
"""A name typed for a recording is the name its run works under.

On way_ground's production without Multitrack, all three recordings.
The window: the presenter's recording typed "Host", a dry run; its plan
carries the name, its log lists the recording and lays its track under
that name, and the untyped recording keeps what its file proposes. The
line: the name given on the second block names the whole recording,
without it the file names it. Refused, not dropped: a file that is no
recording of the run, the switch beside --assign, an empty name, two.
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
import re
import shutil
import tempfile
import time
import the_program
import way_ground as ground

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
    """Nothing further can be asked, so count what there is and go."""
    print("\n%d checks in %.2f s" % (done, time.time() - began))
    print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
    sys.exit(1 if bad else 0)


if ground.missing():
    print("SKIPPED: " + ground.missing())
    stop()

STORE = tempfile.mkdtemp(prefix="vpm_way_store_")
os.environ["VPM_CACHE"] = STORE
os.environ["QT_QPA_PLATFORM"] = "offscreen"
from PySide6 import QtWidgets
app = QtWidgets.QApplication(sys.argv[:1])
vpm = the_program.load()
vpm.set_language("en")
vpm.list_presets = lambda key: []
vpm.load_api_key = lambda: ""

# A name no file of the fixture proposes, so arriving it was typed.
TYPED = "Host"
REC = ground.recordings()
_sound, PICTURES = ground.material()
WORK = ground.own_folder("typed")


def plan_line(said, name, recording):
    """The plan's line listing *recording* under *name*, or ""."""
    wanted = r"^\s*%s\s+%s\b" % (re.escape(name),
                                 re.escape(os.path.basename(recording)))
    return next((x.strip() for x in said.splitlines()
                 if re.match(wanted, x)), "")


def tracks_named(said):
    """Every name a "Track N:" line of the plan gives, in order."""
    return re.findall(r"^\s*Track \d+: (.+?)\s*$", said, re.M)


def dry_line(extra, files=None):
    """A dry run from the line; (code, what it said, stuck)."""
    return ground.line_run(
        [sys.executable, SCRIPT, "--without-auphonic", "--dry-run",
         "--no-speech-recognition", "--production", ground.PRODUCTION,
         "--out", os.path.join(WORK, "line"), ground.NO_EDGES]
        + list(extra) + (REC + PICTURES if files is None else files), STORE)


def last_line(said):
    """The run's last line that says something."""
    lines = [x.strip() for x in said.splitlines() if x.strip()]
    return lines[-1] if lines else ""


def typed(window):
    """Type the name into the presenter's row; "" once it stands."""
    rows = ground.fields(window, vpm.T("Speaker name"))
    box = next((b for k, b in rows.items()
                if k.startswith(os.path.basename(REC[1]))), None)
    if box is None:
        return "the presenter's row among %s" % sorted(rows)
    edit = box.lineEdit() if hasattr(box, "lineEdit") else box
    if edit.text() != TYPED:
        edit.setText(TYPED)
        edit.editingFinished.emit()
        return "the name typed"
    return ""


print("1. The window, the presenter's recording typed, a dry run")
os.makedirs(os.path.join(WORK, "project"))
PROJECT = ground.project_plain(vpm, os.path.join(WORK, "project"),
                               os.path.join(WORK, "window"),
                               multitrack=False)
kept = ground.window_answered_run(vpm, app, PROJECT, {}, typed,
                                  press="Dry run")
said = "".join(kept["log"])
argv = kept["argv"] or []
check("the window's dry run ran to its end, the name typed",
      kept["ended"] and not kept["why"] and not kept["unanswered"]
      and "--dry-run" in argv,
      "loop %s, %s, answers %s, --dry-run %s"
      % ("came back" if kept["ended"] else "never came back",
         kept["why"] or "nothing given up",
         kept["unanswered"] or "stood",
         "on the line" if "--dry-run" in argv else "missing"))
pairs = [[e.get("audio"), e.get("speakers")]
         for e in (kept["plan"] or {}).get("tracks_of") or ()]


def same_file(one, other):
    """One file however it is spelt: on Windows the fixture folder comes
    in with forward slashes and the window hands back backslashes."""
    return bool(one and other) and (
        os.path.normcase(os.path.abspath(one))
        == os.path.normcase(os.path.abspath(other)))


check("the window's plan hands the typed name over with its file",
      any(same_file(p, REC[1]) and n == TYPED for p, n in pairs),
      "plan rows %s, wanted %s among them" % (pairs, [REC[1], TYPED]))
check("the window's run lists that recording under the typed name",
      bool(plan_line(said, TYPED, REC[1])),
      "no plan line '%s  %s'; the file's name gives %r"
      % (TYPED, os.path.basename(REC[1]),
         plan_line(said, "Presenter", REC[1])))
named = tracks_named(said)
check("and lays the camera files' track under the typed name",
      TYPED in named and "Presenter" not in named,
      "the tracks are named %s" % sorted(set(named)))
check("the recording nobody typed for keeps what its file proposes",
      bool(plan_line(said, "Guest", REC[0])),
      "no plan line 'Guest  %s' in %d lines of log"
      % (os.path.basename(REC[0]), len(said.splitlines())))

print("\n2. The line")
code, said, stuck = dry_line(["--speaker-name", REC[2], TYPED])
check("the line names a whole recording by its second block",
      code == 0 and not stuck and bool(plan_line(said, TYPED, REC[1])),
      "return code %s, no plan line '%s  %s'; the last line %r"
      % (code, TYPED, os.path.basename(REC[1]), last_line(said)[-160:]))
code, said, stuck = dry_line([])
check("without the switch the line names it after its file",
      code == 0 and not stuck and bool(plan_line(said, "Presenter", REC[1])),
      "return code %s, no plan line 'Presenter  %s'; tracks %s"
      % (code, os.path.basename(REC[1]), sorted(set(tracks_named(said)))))

print("\n3. Refused rather than dropped")
code, said, stuck = dry_line(["--speaker-name", PICTURES[0], TYPED])
wanted = vpm.T('--speaker-name names %s, which is not one of the '
               'recordings of this run.') % os.path.basename(PICTURES[0])
check("a name for a file that is no recording of the run is refused",
      code == 1 and wanted in last_line(said),
      "return code %s, the last line %r" % (code, last_line(said)[-160:]))
ORDER = os.path.join(WORK, "assign.json")
with open(ORDER, "w") as f:
    f.write('{"format": %d, "tracks_of": []}' % vpm.FILE_FORMAT)
code, said, stuck = dry_line(["--assign", ORDER, "--speaker-name", REC[0],
                              TYPED])
wanted = vpm.T('The assignment file names the recordings here, so '
               '--speaker-name would be dropped; give the names there or '
               'leave --speaker-name out.')
check("beside --assign the name is refused rather than dropped",
      code == 1 and wanted in last_line(said),
      "return code %s, the last line %r" % (code, last_line(said)[-160:]))
code, said, stuck = dry_line(["--speaker-name", REC[0], " "])
wanted = vpm.T('The speaker name for %s is empty; give a name or leave '
               '--speaker-name out.') % os.path.basename(REC[0])
check("an empty name is refused, and says so",
      code == 1 and wanted in last_line(said),
      "return code %s, the last line %r" % (code, last_line(said)[-160:]))
code, said, stuck = dry_line(["--speaker-name", REC[1], TYPED,
                              "--speaker-name", REC[1], "Guest"])
wanted = vpm.T('--speaker-name gives %s two names, "%s" and "%s"; give '
               'each recording one.') % (os.path.basename(REC[1]), TYPED,
                                         "Guest")
check("one recording given two names is refused, both names said",
      code == 1 and wanted in last_line(said),
      "return code %s, the last line %r" % (code, last_line(said)[-160:]))

shutil.rmtree(WORK, ignore_errors=True)
shutil.rmtree(STORE, ignore_errors=True)
stop()
