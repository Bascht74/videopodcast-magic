# -*- coding: utf-8 -*-
"""The command line runs without Qt: no PySide6 module is ever loaded.

Four command lines, each in a child of its own that counts the PySide6
modules in sys.modules as it exits: --help, --version, --hdr-check over
a camera file of the interview fixture, and --dry-run over that fixture
into a folder of its own. In order: that main() ran to its end in all
four, that each left Qt out, and window() as the control that the count
sees Qt at all. A piece that takes Qt at its head is the fault this finds.
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
import subprocess
import tempfile
import time
from fixture_root import fixture

# A dry run over the interview fixture takes seconds here and the
# builder is some nine times slower; a child that never ends is named
# in its own line well before run.sh ends the whole test.
PATIENCE = 240.0

# The child: the program loaded the way every test loads it, a hook
# that writes the PySide6 modules down as the process exits -- after a
# return, a sys.exit out of argparse, or a traceback alike -- and then
# either main() on the given command line or, for the control, window().
CHILD = r'''# -*- coding: utf-8 -*-
"""Run the program once and write down, at exit, what of Qt it loaded."""
import atexit
import json
import sys

REPORT, TESTS = sys.argv[1], sys.argv[2]
LINE = sys.argv[3:]
seen = {"end": "(main() never reached its end)"}


def written():
    """The PySide6 modules standing now, and how the run ended."""
    seen["qt"] = sorted(m for m in sys.modules
                        if m.split(".")[0] == "PySide6")
    with open(REPORT, "w", encoding="utf-8") as f:
        json.dump(seen, f)


atexit.register(written)
sys.path.insert(0, TESTS)
import the_program
vpm = the_program.load()
if LINE == ["window()"]:
    vpm.window()
    seen["end"] = "window() returned"
else:
    sys.argv = ["videopodcast-magic"] + LINE
    try:
        seen["end"] = "main() returned %r" % (vpm.main(),)
    except SystemExit as done:
        seen["end"] = "main() exited %r" % (done.code,)
'''

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


WORK = tempfile.mkdtemp(prefix="vpm_no_qt_")
CHILD_FILE = os.path.join(WORK, "count_qt.py")
with open(CHILD_FILE, "w", encoding="utf-8") as f:
    f.write(CHILD)


def counted(tag, line):
    """One child on this line: (how it ended, the PySide6 modules).

    The modules are None where no report came back; the first part then
    says why, with the child's last words.
    """
    report = os.path.join(WORK, tag + ".json")
    env = dict(os.environ)
    env["QT_QPA_PLATFORM"] = "offscreen"
    try:
        kid = subprocess.run([sys.executable, CHILD_FILE, report, HERE]
                             + line, cwd=WORK, env=env, timeout=PATIENCE,
                             stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    except subprocess.TimeoutExpired:
        return "no end within %.0f s" % PATIENCE, None
    try:
        with open(report, encoding="utf-8") as f:
            seen = json.load(f)
    except (OSError, ValueError):
        words = kid.stdout.decode("utf-8", "replace").strip().splitlines()
        return ("no report, exit %d, last words %r"
                % (kid.returncode, words[-1:] or "(none)")), None
    return seen.get("end", "?"), seen.get("qt")


# The fixture is read, never written: the dry run is handed links to
# it in a folder of its own, and its output goes into another.
SOURCE = fixture("interview")
if not os.path.isdir(SOURCE):
    print("SKIPPED: no %s -- run tests/fixtures.sh, which builds the "
          "interview fixture" % SOURCE)
    stop()
OWN = os.path.join(WORK, "material")
OUT = os.path.join(WORK, "out")
os.makedirs(OWN)
os.makedirs(OUT)
MATERIAL = []
for path in sorted(glob.glob(os.path.join(SOURCE, "*.wav"))
                   + glob.glob(os.path.join(SOURCE, "*.mov"))):
    link = os.path.join(OWN, os.path.basename(path))
    os.symlink(path, link)
    MATERIAL.append(link)
CAMERA = sorted(p for p in MATERIAL if p.endswith(".mov"))[:1]

print("1. The four command lines run to their end")
LINES = [("help", ["--help"]), ("version", ["--version"]),
         ("hdr", ["--hdr-check"] + CAMERA),
         ("dry", ["--dry-run", "--out", OUT] + MATERIAL)]
got = {}
for tag, line in LINES:
    got[tag] = counted(tag, line)
    print("     %-8s %s, %s PySide6 module(s)" % (
        tag, got[tag][0], "no report of" if got[tag][1] is None
        else len(got[tag][1])))
ended = [t for t, (end, _qt) in got.items() if not end.startswith("main()")
         or end.startswith("main() never")]
check("each of the four lines ran main() to its end",
      bool(CAMERA) and not ended,
      "%d camera file(s) in the fixture; not ended: %s" % (
          len(CAMERA), "; ".join("%s: %s" % (t, got[t][0]) for t in ended)
          or "none"))


def none_of_qt(tag):
    """The PySide6 modules one line left, in words for its check."""
    qt = got[tag][1]
    if qt is None:
        return False, "no count came back: %s" % got[tag][0]
    return not qt, "%d PySide6 module(s) against 0, first %s" % (
        len(qt), qt[:3] or "none")


print("\n2. None of them loads Qt")
ok, why = none_of_qt("help")
check("--help loads no PySide6 module", ok, why)
ok, why = none_of_qt("version")
check("--version loads no PySide6 module", ok, why)
ok, why = none_of_qt("hdr")
check("--hdr-check over a camera file loads no PySide6 module", ok, why)
ok, why = none_of_qt("dry")
check("a --dry-run over the interview loads no PySide6 module", ok, why)

print("\n3. The control: the window does load it")
end, qt = counted("window", ["window()"])
check("window() loads PySide6, so the count can see Qt",
      bool(qt) and end == "window() returned",
      "%s PySide6 module(s) against at least 1, the child: %s"
      % ("no report of" if qt is None else len(qt), end))

stop()
