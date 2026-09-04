# -*- coding: utf-8 -*-
"""Importing the program gives the whole of it, whatever argv said.

pip puts a command on the path, and that command imports this file and
calls main() -- so what the module holds must not hang on sys.argv.
Three children load the file, each in a process of its own: one with
numpy out of reach and every process start recorded, one with a bare
command line, one with --version that afterwards calls main(). The
limit: this says what happens where numpy is shut away, not what
happens on a machine that really has none.
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
import the_program

HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = os.path.realpath(the_program.SCRIPT)

MARK = "WHOLE-REPORT"
# Reading the file costs a fifth of a second here and the builder is
# some nine times slower, so a healthy run never comes near this. A
# child that only imports gives no sign of life to watch, so this is a
# limit and not a standstill -- and reaching it is red, with the
# waiting time in the line.
PATIENCE = 180.0

# A second of silence at 48 kHz, read with the 5 ms box the program
# uses: 48000 // 240 = 200 readings, and a curve that never moves comes
# out flat, so every one of them is zero. Both numbers are arithmetic,
# not a value copied out of a run.
SAMPLES = 48000
HOP_MS = 5.0
RATE = 48000
READINGS = 200

CHILD = r'''# -*- coding: utf-8 -*-
"""Load the program the way an installed command does, and report."""
import importlib.util
import json
import os
import subprocess
import sys

SCRIPT = os.path.realpath(os.environ["VPM_WHOLE_SCRIPT"])
MARK = os.environ["VPM_WHOLE_MARK"]
started = []


def note_run(cmd, *rest, **named):
    """subprocess.run's place: it writes the command down and refuses."""
    started.append(" ".join(str(p) for p in cmd) if not isinstance(cmd, str)
                   else cmd)
    raise OSError("no process is started in this test")


class NoPopen:
    """subprocess.Popen's place. A class, because the program subclasses it."""

    def __init__(self, cmd, *rest, **named):
        note_run(cmd)


class NoNumpy:
    """A finder that shuts the door on numpy before anything can open it."""

    def find_spec(self, name, path=None, target=None):
        if name == "numpy" or name.startswith("numpy."):
            raise ImportError("numpy is out of reach in this test")
        return None


subprocess.run = note_run
subprocess.Popen = NoPopen
if os.environ.get("VPM_WHOLE_BLOCK"):
    sys.modules.pop("numpy", None)
    sys.meta_path.insert(0, NoNumpy())
switch = os.environ.get("VPM_WHOLE_ARGV") or ""
sys.argv = ["videopodcast_magic.py"] + ([switch] if switch else [])

out = {"loaded": False, "trouble": "", "started": started,
       "readings": -1, "widest": -1.0, "sum": "", "wrapped": ""}


def say(trouble):
    """One flat line naming what went wrong, with no line break in it."""
    return "%s: %s" % (type(trouble).__name__,
                       " ".join(str(trouble).split())[:110])


try:
    spec = importlib.util.spec_from_file_location("vpm", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["vpm"] = mod
    spec.loader.exec_module(mod)
    out["loaded"] = True
except BaseException as trouble:
    out["trouble"] = say(trouble)

if out["loaded"] and not os.environ.get("VPM_WHOLE_BLOCK"):
    try:
        import numpy
        flat = numpy.ones(int(os.environ["VPM_WHOLE_SAMPLES"]),
                          dtype=numpy.float32)
        got = mod.envelope(flat, float(os.environ["VPM_WHOLE_HOP"]),
                           int(os.environ["VPM_WHOLE_RATE"]))
        out["readings"] = len(got)
        out["widest"] = float(max(abs(v) for v in got)) if len(got) else -1.0
        out["sum"] = "%.9f" % float(sum(got))
    except BaseException as trouble:
        out["trouble"] = say(trouble)

if out["loaded"] and os.environ.get("VPM_WHOLE_MAIN"):
    try:
        mod.main()
    except SystemExit:
        pass
    except BaseException as trouble:
        out["trouble"] = say(trouble)
    out["wrapped"] = "%s %s" % (subprocess.run is mod.run_outside,
                                subprocess.Popen is mod.popen_outside)

sys.stdout.write("\n%s %s\n" % (MARK, json.dumps(out)))
sys.stdout.flush()
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


def as_text(raw):
    """Whatever a child left behind, as text."""
    if isinstance(raw, bytes):
        return raw.decode("utf-8", "replace")
    return raw or ""


def tail(text, how_many=2):
    """The last non-empty lines of some output, flattened and cut short."""
    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
    return " / ".join(lines[-how_many:])[:150] if lines else "(nothing)"


work = tempfile.mkdtemp(prefix="imported_whole_")
child = os.path.join(work, "load_like_a_command.py")
with open(child, "w", encoding="utf-8") as f:
    f.write(CHILD)


def load(switch="", block=False, call_main=False):
    """Run the child once and hand back what it reported, and how long."""
    env = dict(os.environ)
    env["VPM_WHOLE_SCRIPT"] = SCRIPT
    env["VPM_WHOLE_MARK"] = MARK
    env["VPM_WHOLE_SAMPLES"] = str(SAMPLES)
    env["VPM_WHOLE_HOP"] = str(HOP_MS)
    env["VPM_WHOLE_RATE"] = str(RATE)
    env["VPM_WHOLE_ARGV"] = switch
    env["VPM_WHOLE_BLOCK"] = "1" if block else ""
    env["VPM_WHOLE_MAIN"] = "1" if call_main else ""
    # Three locks against an install, because one of these tests once
    # wrote a package into somebody's system Python: the stand-in above
    # refuses to start any process, the question is answered in advance
    # so nothing waits on a person, and pip is given no place to fetch
    # from.
    env["VPM_INSTALL_TOOLS"] = "1"
    env["PIP_NO_INDEX"] = "1"
    env["PIP_NO_INPUT"] = "1"
    env["QT_QPA_PLATFORM"] = "offscreen"
    env["VPM_SILENT"] = "1"
    env["VPM_NO_SPEAKER_SPLIT"] = "1"
    env["VPM_NO_UPDATE_CHECK"] = "1"
    env.pop("VPM_SCRIPT", None)
    env.pop("VPM_COUNT_STARTS", None)
    started_at = time.time()
    said = ""
    went_wrong = ""
    code = -1
    slow = False
    try:
        ran = subprocess.run([sys.executable, child], env=env, cwd=work,
                             capture_output=True, text=True, timeout=PATIENCE)
        code, said, went_wrong = ran.returncode, ran.stdout, ran.stderr
    except subprocess.TimeoutExpired as late:
        slow = True
        said, went_wrong = as_text(late.stdout), as_text(late.stderr)
    report = {}
    for line in said.splitlines():
        if line.startswith(MARK + " "):
            try:
                report = json.loads(line[len(MARK) + 1:])
            except ValueError:
                report = {}
    waited = time.time() - started_at
    if not report:
        report = {"loaded": False, "started": [], "readings": -1,
                  "widest": -1.0, "sum": "", "wrapped": "",
                  "trouble": "no report: the child ended %d after %.2f s%s, "
                             "last words: %s"
                             % (code, waited,
                                " of a %.1f s wait" % PATIENCE if slow else "",
                                tail(went_wrong))}
    report["waited"] = waited
    return report


shut = load(block=True)
bare = load()
version = load(switch="--version", call_main=True)


def why(report):
    """The one sentence that says how a child got on."""
    if not report.get("loaded"):
        return "it was not read to the end -- %s" % (report.get("trouble")
                                                     or "(nothing said)")
    return ("read in %.2f s, %d readings, widest %.9f, sum %s%s"
            % (report.get("waited") or 0.0, report.get("readings"),
               report.get("widest"), report.get("sum") or "-",
               (" -- %s" % report["trouble"]) if report.get("trouble") else ""))


print("1. The file is read with a bare command line and numpy shut away")

check("the file is read to the end with a bare command line and no numpy",
      bool(shut.get("loaded")), why(shut))

opened = shut.get("started") or []
check("and nothing is installed on the way in",
      not opened,
      "%d processes started, the first is %s"
      % (len(opened), (opened[0][:90] if opened else "none")))


print("\n2. A calculation after such an import gives numbers")

widest = bare.get("widest")
check("a calculation after an import with a bare command line computes",
      bare.get("readings") == READINGS and 0 <= widest < 1e-9,
      "%d readings against %d, widest %.9f against 0 -- %s"
      % (bare.get("readings"), READINGS, bare.get("widest"), why(bare)))

same = (version.get("readings") == bare.get("readings")
        and version.get("sum") == bare.get("sum")
        and bare.get("readings") == READINGS)
check("and the same after an import with --version in the command line",
      same,
      "with --version %d readings and sum %s, with none %d and %s -- %s"
      % (version.get("readings"), version.get("sum") or "-",
         bare.get("readings"), bare.get("sum") or "-", why(version)))


print("\n3. And a run reached through main() logs its calls outside")

check("main() puts the log in front of every call to another program",
      version.get("wrapped") == "True True",
      "run and Popen replaced: %s, wanted True True"
      % (version.get("wrapped") or "(main was never reached)"))

shutil.rmtree(work, ignore_errors=True)

print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
