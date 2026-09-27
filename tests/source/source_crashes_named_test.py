# -*- coding: utf-8 -*-
"""run.sh ends by naming the Python crash reports written while it ran.

A child that crashes after its parent has left reaches no test log, and
macOS keeps a report of it; so run.sh counts the new ones at its end.
The suite is started here on one cheap test, twice, with
VPM_CRASH_REPORTS pointed at a folder of made-up reports and never at
the real one. First a folder holding an old Python report, a new one,
a new one under Retired/ known only by its header, and a new one of
another program: the line counts and names the two new Python ones,
says the folder lies outside the repository, carries nothing out of
the reports, and the folder is left as it was. Then an empty folder:
the line says none.
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
import hashlib
import re
import shutil
import subprocess
import tempfile
import time

RUN = os.path.join(HERE, "run.sh")
# The cheapest test there is, as in source_resolve_recalled: the inner
# suite has something to do and is back in well under a second.
NAMED = "cut_rules_hold"
# Far above a suite of one on the slowest builder, and under run.sh's
# own 300 s, so a hang is red here with the number beside it.
WAIT = 240
DAY = 24 * 3600
# Written into every made-up report. The line may name a report, never
# say what is in it.
INSIDE = "only-inside-the-report-4711"
OPENS = re.compile(r"^crash reports: (\d+|none) ")

began = time.time()
done = 0
bad = []


def check(name, ok, extra=""):
    global done
    done += 1
    print("  %-58s %s %s" % (name, "ok" if ok else "FAIL", extra))
    if not ok:
        bad.append("%s [%s]" % (name, extra or "no numbers"))


# The words run.sh judges a run by; what the inner run printed is
# quoted, so it goes through this first.
LOUD = ("FAIL", "Traceback", "SKIPPED", "LEFT OUT", "Left out",
        "Error", "error", "Exception", "Interrupt")


def quiet(text):
    """Text out of another run, safe to print in a line of ours."""
    text = " ".join(str(text).split())
    for word in LOUD:
        text = text.replace(word, word[:2] + "-" + word[2:])
    return text


def bash():
    r"""Where bash is -- on Windows Git's, not the WSL stub in System32."""
    if sys.platform == "win32":
        for root in (os.environ.get("EXEPATH"),
                     os.path.join(os.environ.get("ProgramFiles", ""),
                                  "Git")):
            exe = os.path.join(root or "", "bin", "bash.exe")
            if root and os.path.isfile(exe):
                return exe
    return shutil.which("bash") or "bash"


BASH = bash()


def spelt(folder):
    """The folder in bash's own spelling (/c/Users/... on Windows)."""
    if sys.platform != "win32":
        return folder
    got = subprocess.run([BASH, "-c", 'cygpath -u "$0"', folder],
                         capture_output=True, text=True)
    return got.stdout.strip() if got.returncode == 0 and got.stdout.strip() \
        else folder


def report(folder, rel, bundle, age):
    """A made-up .ips: a header line and a body, its time moved by age."""
    path = os.path.join(folder, *rel.split("/"))
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        f.write('{"app_name":"x","bundleID":"%s"}\n' % bundle)
        f.write('{"path":"/tmp/%s"}\n' % INSIDE)
    when = time.time() + age
    os.utime(path, (when, when))


def held(folder):
    """Every file under the folder: its bytes' sum and its time."""
    found = {}
    for root, _, names in os.walk(folder):
        for name in names:
            path = os.path.join(root, name)
            with open(path, "rb") as f:
                digest = hashlib.sha256(f.read()).hexdigest()[:12]
            found[os.path.relpath(path, folder).replace(os.sep, "/")] = (
                digest, int(os.path.getmtime(path)))
    return found


def suite(folder):
    """The crash line of a run on NAMED, the reports read out of folder."""
    env = dict(os.environ, VPM_CRASH_REPORTS=spelt(folder))
    try:
        ran = subprocess.run([BASH, RUN, NAMED], cwd=HERE, env=env,
                             stdout=subprocess.PIPE,
                             stderr=subprocess.STDOUT, timeout=WAIT)
    except (OSError, subprocess.TimeoutExpired) as e:
        return [], type(e).__name__
    lines = ran.stdout.decode("utf-8", "replace").splitlines()
    return [one for one in lines if OPENS.match(one)], \
        "%d lines, returned %d" % (len(lines), ran.returncode)


# Old: a day before the run. New: a day after its start, so no clock
# between here and the inner run can put it on the wrong side.
full = tempfile.mkdtemp(prefix="vpm-crashes-")
empty = tempfile.mkdtemp(prefix="vpm-no-crashes-")
report(full, "Python-2026-01-01-000000.ips", "org.python.python", -DAY)
report(full, "Python-2099-01-01-000000.ips", "org.python.python", DAY)
report(full, "Retired/embedded-2099-01-01-000001.ips", "org.python.python",
       DAY)
report(full, "Finder-2099-01-01-000002.ips", "com.apple.finder", DAY)
before = held(full)

# ------------------------------------------------------------------ 1.
print("1. A folder with two new Python reports among older and others")
lines, how = suite(full)
check("a run with crash reports ends on one crash reports line",
      len(lines) == 1,
      "%d such lines (%s): %s" % (len(lines), how, quiet(" / ".join(lines))))
line = lines[0] if lines else ""
said = OPENS.match(line)
check("the line counts only new Python reports",
      said is not None and said.group(1) == "2",
      "wanted 2, the line says %s" % (said.group(1) if said else "nothing"))
named = sorted(re.findall(r"\S+\.ips", line))
check("the line names exactly the new Python reports",
      named == ["Python-2099-01-01-000000.ips",
                "Retired/embedded-2099-01-01-000001.ips"],
      "named: %s" % (quiet(", ".join(named)) or "none"))
check("the line says the folder lies outside the repository",
      "outside the repository" in line, "line: %s" % quiet(line))
check("the line carries nothing out of the reports",
      bool(line) and INSIDE not in line, "line: %s" % quiet(line))
after = held(full)
check("the run leaves the report folder as it found it",
      before == after,
      "%d files before, %d after, %d differ"
      % (len(before), len(after),
         len([k for k in set(before) | set(after)
              if before.get(k) != after.get(k)])))

# ------------------------------------------------------------------ 2.
print("\n2. An empty folder")
lines, how = suite(empty)
said = OPENS.match(lines[0]) if len(lines) == 1 else None
check("a run with no crash reports says none",
      said is not None and said.group(1) == "none",
      "%d such lines (%s): %s" % (len(lines), how, quiet(" / ".join(lines))))

shutil.rmtree(full, ignore_errors=True)
shutil.rmtree(empty, ignore_errors=True)
print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
