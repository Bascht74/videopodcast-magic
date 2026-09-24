# -*- coding: utf-8 -*-
"""A run of fixtures.sh leaves the checked-in material as it found it.

fixtures.sh builds the shared folders into a fresh VPM_FIXTURES. The
material it may read lies beside it, under tests/material, and a run
must never write there: a changed file in the working tree turns up in
whatever pull request comes next. In order: the script runs through on
a fresh folder, every file under material carries the bytes it had
before the run and none appeared or vanished, and what lies there is
what HEAD holds, so a change made before the run counts too. That last
section asks git and is left out where there is none; a copy refreshed
by hand and on purpose shows there until it is committed.

VPM_FIXTURES_SH names the script to run; without it, the one beside
this test. The material held is always the folder beside that script.
On Windows the first bash on the search path is the WSL stub, which
only says how to install a distribution; Git's bash is taken there,
and the fresh folder is handed to it in its own spelling.
"""
import hashlib
import os
import shutil
import subprocess
import sys
import tempfile
import time

HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = os.path.abspath(os.environ.get("VPM_FIXTURES_SH")
                        or os.path.join(HERE, "fixtures.sh"))
MATERIAL = os.path.join(os.path.dirname(SCRIPT), "material")
# Under run.sh's own 300 s, so a slow machine learns that the build
# never came and not merely that the whole run is over.
PATIENCE = 240

began = time.time()
done = 0
bad = []


def check(name, ok, extra=""):
    global done
    done += 1
    print("  %-58s %s %s" % (name, "ok" if ok else "FAIL", extra))
    if not ok:
        bad.append("%s [%s]" % (name, extra or "no numbers"))


def sums():
    """Every file under material: its path, its sha256, its bytes."""
    found = {}
    for folder, _, names in os.walk(MATERIAL):
        for name in names:
            path = os.path.join(folder, name)
            with open(path, "rb") as f:
                data = f.read()
            rel = os.path.relpath(path, MATERIAL).replace(os.sep, "/")
            found[rel] = (hashlib.sha256(data).hexdigest(), len(data))
    return found


def git(*words):
    """git's answer out of the material's folder, or None without git."""
    try:
        got = subprocess.run(["git", "-C", MATERIAL] + list(words),
                             capture_output=True, text=True)
    except OSError:
        return None
    return got


def bash():
    r"""Where bash is -- on Windows Git's, not the WSL stub in System32.

    C:\Windows\System32\bash.exe stands first on the search path and
    answers every call with the line to install a distribution, so
    shutil.which() alone hands the script to a shell that runs nothing.
    Git's bash sets EXEPATH to its root when it is the shell running
    the suite; otherwise the usual install folder is tried.
    """
    if sys.platform == "win32":
        for root in (os.environ.get("EXEPATH"),
                     os.path.join(os.environ.get("ProgramFiles", ""),
                                  "Git")):
            exe = os.path.join(root or "", "bin", "bash.exe")
            if root and os.path.isfile(exe):
                return exe
    return shutil.which("bash")


BASH = bash()
for tool, found in (("bash", BASH), ("ffmpeg", shutil.which("ffmpeg"))):
    if not found:
        print("SKIPPED: no %s on the search path -- fixtures.sh cannot "
              "build without it; install it and run again" % tool)
        print("\n%d checks in %.2f s" % (done, time.time() - began))
        print("Good as far as it went -- nothing ran.")
        sys.exit(0)

before = sums()
fix = tempfile.mkdtemp(prefix="vpm-material-stays-")
fix_for_bash = fix
if sys.platform == "win32":
    # The folder in bash's own spelling (/c/Users/...), so the script's
    # mkdir, cp and rm see one path and not a mixed one.
    posix = subprocess.run([BASH, "-c", 'cygpath -u "$0"', fix],
                           capture_output=True, text=True)
    if posix.returncode == 0 and posix.stdout.strip():
        fix_for_bash = posix.stdout.strip()
env = dict(os.environ, VPM_FIXTURES=fix_for_bash)
env.pop("VPM_FIXTURES_SH", None)
returned = None
tail = ""
try:
    try:
        run = subprocess.run([BASH, SCRIPT], env=env, cwd=fix,
                             capture_output=True, text=True,
                             timeout=PATIENCE)
        returned = run.returncode
        tail = " / ".join((run.stdout + run.stderr).strip()
                          .splitlines()[-3:])
    except subprocess.TimeoutExpired:
        tail = "did not finish within %d s" % PATIENCE
finally:
    shutil.rmtree(fix, ignore_errors=True)

# --- the script ran through ---
check("fixtures.sh runs through on a fresh folder", returned == 0,
      "returned %s; last lines: %s" % (returned, tail))

# --- the bytes it found are the bytes it left ---
after = sums()
moved = []
for rel in sorted(set(before) | set(after)):
    if before.get(rel) != after.get(rel):
        was = before.get(rel)
        now = after.get(rel)
        moved.append("%s: %s -> %s" % (
            rel,
            "absent" if was is None else "%s/%d bytes" % (was[0][:8], was[1]),
            "gone" if now is None else "%s/%d bytes" % (now[0][:8], now[1])))
check("a run leaves every file under material with the bytes it found",
      not moved,
      "%d of %d files moved -- %s" % (len(moved), len(after),
                                      "; ".join(moved) or "none"))

# --- and they are what HEAD holds ---
# git itself is asked, not the bytes of HEAD: on the Windows builder
# core.autocrlf rewrites truth.txt on checkout, and git knows that a
# rewritten line ending is not a change while a byte comparison does not.
inside = git("rev-parse", "--show-prefix")
head = git("rev-parse", "--verify", "-q", "HEAD")
if inside is None or inside.returncode != 0:
    print("  LEFT OUT: no git around %s -- the comparison against HEAD "
          "asks the repository, and a folder cannot answer it" % MATERIAL)
elif head.returncode != 0:
    # A fresh 'git init' has an index and no HEAD, and 'git diff HEAD'
    # then answers nothing at all -- which would read as no change.
    print("  LEFT OUT: no commit around %s -- there is no HEAD to hold "
          "the material against yet" % MATERIAL)
else:
    prefix = inside.stdout.strip()
    changed = git("diff", "--name-only", "HEAD", "--", ".").stdout.split()
    loose = git("ls-files", "--others", "--exclude-standard",
                "--", ".").stdout.split()
    told = []
    for rel in changed:
        # git names the file from the top of the repository.
        short = rel[len(prefix):] if rel.startswith(prefix) else rel
        now = after.get(short)
        held = git("cat-file", "-s", "HEAD:" + rel)
        told.append("%s: %s bytes in the tree, %s in HEAD" % (
            short, "gone" if now is None else now[1],
            held.stdout.strip() if held.returncode == 0 else "absent"))
    for rel in loose:
        told.append("%s: %d bytes in the tree, absent in HEAD"
                    % (rel, after.get(rel, (None, 0))[1]))
    check("after the run every file under material is what HEAD holds",
          not told,
          "%d of %d files differ from HEAD -- %s" % (
              len(told), len(after), "; ".join(told) or "none"))

print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
