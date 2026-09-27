# -*- coding: utf-8 -*-
"""Every release carries each system's known-good package list, checked.

In order: every bound suite job in tests.yml keeps its pip freeze after
a green suite, under its system and Python; both of publish.yml's suite
calls install the separation, and it takes the three py3.14 lists, sums
them into SHA256SUMS.txt before the tag and attaches them in the command
that makes the release; release.yml asks each hangs, is in the manifest
with its sum, and is name==version lines; the manual in both languages
says to install with it. Read as text: the workflows run on the builder.
"""
PLATFORM_BOUND = False
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
import time

began = time.time()
ROOT = os.path.dirname(HERE)
FLOWS = os.path.join(ROOT, ".github", "workflows")
SYSTEMS = ("macos", "windows", "linux")

done = 0
bad = []


def check(name, ok, extra=""):
    global done
    done += 1
    print("  %-58s %s %s" % (name, "ok" if ok else "FAIL", extra))
    if not ok:
        bad.append("%s [%s]" % (name, extra or "no numbers"))


def read(*path):
    try:
        with open(os.path.join(ROOT, *path), encoding="utf-8") as f:
            return f.read()
    except OSError as e:
        return "<unreadable: %s>" % e


def job(text, name):
    """The lines of one job, from its key to the next job's key."""
    m = re.search(r"^  %s:\n(.*?)(?=^  [A-Za-z_][\w-]*:\n|\Z)" % name,
                  text, re.S | re.M)
    return m.group(1) if m else ""


def steps(block):
    """The steps of a job, each from its dash to the next one's."""
    return re.split(r"^      - ", block, flags=re.M)[1:]


def first_line(s):
    return s.split("\n", 1)[0].strip()


def condition(step):
    m = re.search(r"^        if: (.*)$", step, re.M)
    return m.group(1) if m else ""


tests_yml = read(".github", "workflows", "tests.yml")
publish_yml = read(".github", "workflows", "publish.yml")
release_yml = read(".github", "workflows", "release.yml")

print("tests.yml: the suite writes down what it stood on")
suite = steps(job(tests_yml, "suite"))
freeze = [s for s in suite if "python -m pip freeze" in s]
upload = [s for s in suite if first_line(s).startswith(
    "uses: actions/upload-artifact")]
run_at = [i for i, s in enumerate(suite)
          if 'name: "Run: the test suite"' in s]
freeze_at = [i for i, s in enumerate(suite) if "python -m pip freeze" in s]
check("a suite step writes pip freeze", len(freeze) == 1,
      "%d steps of %d name pip freeze" % (len(freeze), len(suite)))
check("and it comes after the suite has run",
      bool(run_at and freeze_at and freeze_at[0] > run_at[0]),
      "suite at step %s, freeze at step %s" % (run_at, freeze_at))
f_if = condition(freeze[0]) if freeze else ""
check("and only after a green one", "success()" in f_if,
      "if: %s" % (f_if or "none"))
check("and on every bound job: no system or Python left out",
      bool(freeze) and not re.search(r"matrix\.(label|os|python)", f_if),
      "if: %s" % (f_if or "none"))
u_name = re.search(r"^          name: (.*)$", upload[0], re.M) \
    if upload else None
u_name = u_name.group(1) if u_name else ""
check("the list is kept under its system and its Python",
      "${{ matrix.label }}" in u_name and "${{ matrix.python }}" in u_name,
      "artifact name: %s" % (u_name or "no upload step"))
u_if = condition(upload[0]) if upload else ""
check("and kept only where it was written", bool(u_if) and u_if == f_if,
      "upload if: %s | freeze if: %s" % (u_if or "none", f_if or "none"))

print("\npublish.yml: collected, summed and attached")
calls = {n: job(publish_yml, n) for n in ("tests", "languages")}
check("the long way's suite installs the separation",
      "speaker_split: true" in calls["tests"],
      "tests job: %d lines" % calls["tests"].count("\n"))
check("the short way's suite installs it too",
      "speaker_split: true" in calls["languages"],
      "languages job: %d lines" % calls["languages"].count("\n"))
pub = steps(job(publish_yml, "publish"))
pub_names = [first_line(s) for s in pub]
down = [s for s in pub if "actions/download-artifact" in s]
d_pat = re.search(r"pattern: (\S+)", down[0]) if down else None
d_pat = d_pat.group(1) if d_pat else ""
check("the publish job takes the py3.14 lists of this run",
      d_pat == "freeze-*-py3.14",
      "pattern: %s" % (d_pat or "no download step"))
made = [s for s in pub if "gh release create" in s]
command = re.search(r"gh release create(.*?); then", made[0], re.S) \
    if made else None
command = command.group(1) if command else ""
sums = re.search(r"shasum -a 256 ([^>]*)>> SHA256SUMS\.txt", "".join(pub))
sums = sums.group(1) if sums else ""
summed = " ".join(sums.split()) or "none"
attached = " ".join(command.split()[-6:]) or "no gh release create"
check("constraints-macos.txt goes into SHA256SUMS.txt",
      "constraints-macos.txt" in sums, "summed: %s" % summed)
check("constraints-windows.txt goes into SHA256SUMS.txt",
      "constraints-windows.txt" in sums, "summed: %s" % summed)
check("constraints-linux.txt goes into SHA256SUMS.txt",
      "constraints-linux.txt" in sums, "summed: %s" % summed)
check("constraints-macos.txt hangs on the release as it is made",
      "/tmp/constraints-macos.txt" in command, "attached: %s" % attached)
check("constraints-windows.txt hangs on the release as it is made",
      "/tmp/constraints-windows.txt" in command, "attached: %s" % attached)
check("constraints-linux.txt hangs on the release as it is made",
      "/tmp/constraints-linux.txt" in command, "attached: %s" % attached)
at = [i for i, n in enumerate(pub_names) if n.startswith('name: "6.')]
lists_at = [i for i, s in enumerate(pub) if "constraints-$sys.txt" in s]
check("the lists are made before the tag is set",
      bool(at and lists_at and lists_at[0] < at[0]),
      "lists at step %s, tag at step %s" % (lists_at, at))

print("\nrelease.yml: asked as they hang")
contract = "".join(steps(job(release_yml, "contract")))
section = contract.split('echo "5. And the known-good package lists', 1)
section = section[1] if len(section) == 2 else ""
loop = re.search(r"for sys in ([a-z ]+); do", section)
loop = loop.group(1).split() if loop else []
check("each of the three systems is asked about",
      sorted(loop) == sorted(SYSTEMS), "asked: %s" % (loop or "none"))
check("that its list hangs on the release",
      '*,"$name",*) ok=1' in section, "%d lines in the section"
      % section.count("\n"))
check("that the manifest names it with the sum of what came down",
      "$NF == n" in section and '"$want" = "$got"' in section,
      "%d lines in the section" % section.count("\n"))
check("that it is name==version lines and nothing else",
      "and it is a list pip3 -c takes" in section
      and "==[^+[:space:];]+$" in section,
      "%d lines in the section" % section.count("\n"))

print("\nthe manual says how to use it")
# A paragraph may break a line anywhere, inside a command as well.
english = " ".join(read("docs", "requirements.md").split())
german = " ".join(read("docs", "requirements.de.md").split())
check("requirements.md says to install with -c",
      "pip3 install -c constraints-macos.txt" in english,
      "%d characters read" % len(english))
check("requirements.de.md says to install with -c",
      "pip3 install -c constraints-macos.txt" in german,
      "%d characters read" % len(german))

print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
