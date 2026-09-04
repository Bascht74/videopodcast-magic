# -*- coding: utf-8 -*-
"""A separation that will not run says which fault it hit, not a story.

The worker switches pyannote's telemetry off before anything else, and
refuses to run where it cannot. That refusal used to swallow every
other fault with it: a dependency taken out by hand made "import
pyannote.audio" die, and the window answered with a sentence about
data protection that had nothing to do with it.

The sections: what the worker's own switch reports for the three cases
it can meet; what the run makes of each of those answers; and that the
question "can it run here" is answered by really importing rather than
by a note an earlier run left behind. Nothing here imports pyannote
for real -- the package is driven, so the judgement is the same on a
machine that has none.
"""
import os
import the_program
HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = the_program.SCRIPT
import json
import shutil
import subprocess
import sys
import tempfile
import time
import types

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
os.environ.setdefault("VPM_NO_SPEAKER_SPLIT", "1")
m = the_program.load()
m.set_language("en")

began = time.time()
done = 0
bad = []


def check(name, ok, extra=""):
    global done
    done += 1
    print("  %-58s %s %s" % (name, "ok" if ok else "FAIL", extra))
    if not ok:
        bad.append("%s [%s]" % (name, extra or "no numbers"))


#--------------------------------------------- 1. The worker's own switch

# The worker is a source text the program carries, so it is run here
# rather than read: what matters is what hush() answers, and only
# running it says that.
WORKER = {}
exec(compile(m.SPEAKER_SPLIT_WORKER, "worker", "exec"), WORKER)
hush = WORKER["hush"]

thrown = []


THREE = ("pyannote", "pyannote.audio", "pyannote.audio.telemetry")


def with_modules(**modules):
    """Run hush() with those names standing in for pyannote's.

    None in sys.modules is how a name is made unimportable without
    touching the disc: the import machinery stops at it and raises.
    Without that the real package would answer on a machine that has
    one, and the first case below would measure nothing.
    """
    was = dict((name, sys.modules.get(name, "not there")) for name in THREE)
    try:
        for name in THREE:
            sys.modules[name] = None
        for name, mod in modules.items():
            sys.modules[name.replace("_", ".")] = mod
        return hush()
    finally:
        for name, mod in was.items():
            if mod == "not there":
                sys.modules.pop(name, None)
            else:
                sys.modules[name] = mod


def a_module(with_switch):
    out = types.ModuleType("stand-in")
    if with_switch:
        out.set_telemetry_metrics = lambda on: thrown.append(on)
    return out


print("1. What the worker's own switch reports")

# Nothing under that name at all: the import fails, and that is not a
# question of telemetry.
missing = with_modules()
check("a pyannote that will not load is reported by its own error",
      missing != "telemetry" and "Error" in missing,
      "it said %r, wanted the import error itself -- a package that "
      "cannot be loaded is not a package refusing to be quiet"
      % (missing[:90],))

# It loads, and there is no such switch in this version: then the
# refusal stands and the word is the truth.
no_switch = with_modules(pyannote=a_module(False),
                         pyannote_audio=a_module(False))
check("a pyannote with no such switch is still refused as telemetry",
      no_switch == "telemetry",
      "it said %r, wanted 'telemetry' -- this program sends nothing by "
      "itself, and a separation is not worth breaking that for"
      % (no_switch,))

del thrown[:]
quiet = with_modules(pyannote=a_module(False),
                     pyannote_audio=a_module(True))
check("a pyannote that can be quietened reports nothing to report",
      quiet == "" and thrown == [False],
      "it said %r and threw the switch %r times with %r"
      % (quiet, len(thrown), thrown))


#------------------------------------------- 2. What the run makes of it

print("\n2. What the run makes of each of those answers")

WORK = tempfile.mkdtemp(prefix="vpm_faultworker_")


def worker_saying(what, name):
    """A stand-in worker that answers with that and stops."""
    where = os.path.join(WORK, name)
    with open(where, "w", encoding="utf-8") as f:
        f.write("import json, sys\n"
                "print(json.dumps({'error': %r}))\n"
                "sys.exit(3)\n" % what)
    return where


import numpy as np

wave = np.zeros(16, dtype=np.float32)
head = json.dumps({"model": WORK, "sample_rate": 16000,
                   "samples": 16, "speakers": 0})
try:
    _segments, said_telemetry = m._speaker_split_talk(
        sys.executable, worker_saying("telemetry", "w_tele.py"),
        head, wave, dict(os.environ), None, None)
    _segments, said_import = m._speaker_split_talk(
        sys.executable,
        worker_saying("ImportError: cannot import name 'resnet50'",
                      "w_import.py"),
        head, wave, dict(os.environ), None, None)
finally:
    shutil.rmtree(WORK, ignore_errors=True)

TELEMETRY = m.T('pyannote sends a trace home on every run and this '
                'version offers no way to switch it off, so the '
                'separation was not started.')
REPORTS = m.T('The speaker separation reports: %s').split("%s")[0]

check("the telemetry refusal keeps its own sentence",
      said_telemetry == TELEMETRY,
      "it said %r, wanted the sentence about the trace" % (said_telemetry,))
check("any other refusal is handed on word for word",
      REPORTS in said_import and "resnet50" in said_import,
      "it said %r, wanted %r and the name it died at in it"
      % (said_import[:110], REPORTS))


#--------------------------------- 3. The question is answered by asking

print("\n3. Whether it can run here is measured, not remembered")

was_python, was_ready = m.speaker_python, m._SPEAKER_READY
nowhere = os.path.join(WORK, "no such python at all")
try:
    m.speaker_python = lambda: nowhere
    m._SPEAKER_READY = True
    kept = m.speaker_split_available()
    asked_again = m.speaker_split_available(deep=True)
finally:
    m.speaker_python, m._SPEAKER_READY = was_python, was_ready

check("the answer from earlier in this run is not measured again",
      kept is True,
      "it answered %r -- importing pyannote takes seconds, so it is "
      "asked once" % (kept,))
check("and asking deeply throws that answer away and measures",
      asked_again is False,
      "it answered %r with no interpreter to ask -- a note left behind "
      "by an earlier run says what was true then, not what is true now"
      % (asked_again,))

print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
