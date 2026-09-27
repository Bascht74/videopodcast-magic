# -*- coding: utf-8 -*-
"""run.sh reads red from a check's verdict, never from its name.

verdict.sh's said_red, which run.sh asks of every test's output, is put
lines written the way a check prints them and answers red or green for
each. In order: a check line whose verdict is ok is green whatever its
name or numbers say; one whose verdict is FAIL is red at every width in
use; ok in a name does not hide a FAIL verdict; FAIL on any other line
is red; a traceback is red; and a whole green output is green. A name
longer than its width with the word in it past column 55 is misread --
the closing FAIL: line and the return code still answer for that test.
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
import subprocess
import tempfile
import time

began = time.time()
done = 0
bad = []


def check(name, ok, extra=""):
    global done
    done += 1
    print("  %-58s %s %s" % (name, "ok" if ok else "FAIL", extra))
    if not ok:
        bad.append("%s [%s]" % (name, extra or "no numbers"))


def line(width, name, verdict, numbers=""):
    """A check line as a test prints it, at the given width."""
    return ("  %-" + str(width) + "s %s %s") % (name, verdict, numbers)


def bash():
    r"""Where bash is -- on Windows Git's, not the WSL stub in System32.

    C:\Windows\System32\bash.exe stands first on the search path and
    answers every call with the line to install a distribution; Git's
    bash sets EXEPATH to its root when it runs the suite. As
    source_material_stays finds it.
    """
    if sys.platform == "win32":
        for root in (os.environ.get("EXEPATH"),
                     os.path.join(os.environ.get("ProgramFiles", ""),
                                  "Git")):
            exe = os.path.join(root or "", "bin", "bash.exe")
            if root and os.path.isfile(exe):
                return exe
    return shutil.which("bash") or "bash"


# The outputs put to it, each a whole test's worth or one line of one.
CASES = {
    "ok_named_fail": line(58, "run.sh reads a FAIL line as red", "ok"),
    "ok_quotes_red": line(58, "an ok line may quote a red one", "ok",
                          "the line said: x  FAIL y"),
    "ok_width_52": line(52, "a FAIL named at the narrowest width", "ok"),
    "red_58": line(58, "a check that fell", "FAIL", "3 against 4"),
    "red_52": line(52, "a check that fell, narrow", "FAIL", "3 against 4"),
    "red_long": line(58, "a check whose name runs on well past the "
                         "fifty-eight columns it is given", "FAIL", "1 of 2"),
    "red_ok_in_name": line(58, "a key that is ok stays in its store",
                           "FAIL", "gone"),
    "red_closing": "\n0 checks in 0.01 s\nFAIL: a check that fell [3]",
    "red_run_sh": "FAIL the test judged anything at all -- 0 judgements "
                  "against 4 last time",
    "red_odd_line": "  the window never got as far as the checks   FAIL",
    "red_traceback": "Traceback (most recent call last):\n"
                     "  File \"x.py\", line 1, in <module>\n"
                     "ZeroDivisionError: division by zero",
    "green_whole": "1. The first part\n"
                   + line(58, "a camera is placed", "ok", "0.00 s off") + "\n"
                   + line(58, "and it is named", "ok", "Guest") + "\n"
                   + "\n2 checks in 0.40 s\nALL OK",
}

D = tempfile.mkdtemp(prefix="readsred_")
said = {}
try:
    for key, text in CASES.items():
        with open(os.path.join(D, key), "w", encoding="utf-8",
                  newline="\n") as f:
            f.write(text + "\n")
    # One bash for every case: on Windows a process is what a run pays.
    # The name is cut here, not in bash: Windows hands the paths over
    # with backslashes, and a bash pattern for both was read wrongly.
    script = ('. "$1"; shift; for f in "$@"; do '
              'if said_red "$(< "$f")"; then echo "$f red"; '
              'else echo "$f green"; fi; done')
    ran = subprocess.run(
        [bash(), "-c", script, "_", "verdict.sh"]
        + [os.path.join(D, key) for key in sorted(CASES)],
        cwd=HERE,
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=120)
    heard = ran.stdout.decode("utf-8", "replace")
    for one in heard.splitlines():
        parts = one.rsplit(" ", 1)
        if len(parts) == 2:
            parts[0] = re.split(r"[\\\\/]", parts[0])[-1]
        if len(parts) == 2 and parts[0] in CASES:
            said[parts[0]] = parts[1]
    if not said:
        print("  bash said nothing readable, return code %d: %s"
              % (ran.returncode, " / ".join(heard.strip().splitlines()[-3:])
                 [-200:]))
except (OSError, subprocess.TimeoutExpired) as e:
    said = {}
    print("  bash could not be asked: %s" % type(e).__name__)
finally:
    shutil.rmtree(D, ignore_errors=True)


def answers(*keys):
    """What said_red answered for each key, 'none' where it was silent."""
    return ", ".join("%s %s" % (k, said.get(k, "none")) for k in keys)


def all_are(colour, *keys):
    return all(said.get(k) == colour for k in keys)


check("an ok verdict is green, whatever the check's name says",
      all_are("green", "ok_named_fail", "ok_quotes_red", "ok_width_52"),
      answers("ok_named_fail", "ok_quotes_red", "ok_width_52"))
check("a check line whose verdict is FAIL is red, at any width",
      all_are("red", "red_58", "red_52", "red_long"),
      answers("red_58", "red_52", "red_long"))
check("a check with ok in its name and FAIL as its verdict is red",
      all_are("red", "red_ok_in_name"), answers("red_ok_in_name"))
check("FAIL on a line that is no check line is red",
      all_are("red", "red_closing", "red_run_sh", "red_odd_line"),
      answers("red_closing", "red_run_sh", "red_odd_line"))
check("a traceback is red", all_are("red", "red_traceback"),
      answers("red_traceback"))
check("a whole green output is green", all_are("green", "green_whole"),
      answers("green_whole"))

print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
