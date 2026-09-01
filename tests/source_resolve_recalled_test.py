# -*- coding: utf-8 -*-
"""The reminder about the Resolve tests reaches a person, not the builder.

Nothing under tests/resolve/ runs in the suite: those tests want a
DaVinci Resolve really running, and only a person starts them. So run.sh
says at the end how many there are and what to type, and says none of it
where CI is set -- an instruction no runner can follow is noise. The
suite is started from here twice, once plain and once with the two
variables GitHub sets; then the ending of the plain run is read, and
after it the ending of the other one.

The limit is that one cheap test is named rather than the whole folder,
so what is read is what run.sh prints around a run. The count is taken
out of the folder again here, by another route than the shell takes.
"""
import os
import re
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
RUN = os.path.join(HERE, "run.sh")
FOLDER = os.path.join(HERE, "resolve")
# One test is named, so the inner suite has something to do and still
# comes back in well under a second. Measured on 1.9.2026, three runs
# each: 0.26 to 0.33 s a run with this one against 0.64 to 0.80 s with
# source_numpy_comes_last, and state/longest says 1 s against 2 s on the
# builder. It stands in no machine's set-aside list in tests.yml, so the
# name is there on all six.
NAMED = "cut_rules_hold"
# A suite of one costs a fraction of a second here and the builder is
# some nine times slower, so a healthy run never comes near this. It is
# there because a run that hangs would otherwise hang the whole suite
# behind it, and running out of it is red with the number beside it.
WAIT = 600
# The line the block opens on, which is the line carrying the count, and
# the line that says what a person types. Two anchors and not one: the
# sharper form of the block names tests/resolve.sh among the files that
# were worked on, and a bare "resolve.sh" would take that for the way
# back.
OPENS = re.compile(r"^resolve:\s+(\d+)\b")
TYPED = "bash resolve.sh"

began = time.time()
done = 0
bad = []


def check(name, ok, extra=""):
    global done
    done += 1
    print("  %-58s %s %s" % (name, "ok" if ok else "FAIL", extra))
    if not ok:
        bad.append("%s [%s]" % (name, extra or "no numbers"))


# The words run.sh judges a whole run by -- and it looks for FAIL
# anywhere in a line, not only at its start. What another run printed is
# quoted here, so it goes through this first.
LOUD = ("FAIL", "Traceback", "SKIPPED", "LEFT OUT", "Left out",
        "Error", "error", "Exception", "Interrupt")


def quiet(text):
    """Text out of another run, safe to print in a line of ours."""
    text = " ".join(str(text).split())
    for word in LOUD:
        text = text.replace(word, word[:2] + "-" + word[2:])
    return text


def suite(builder):
    """The suite started on one test, plain or the way GitHub starts it.

    CI and GITHUB_ACTIONS are taken out for the plain run and not merely
    left alone: on the builder they are already set in this process, and
    a plain run there would be the builder run a second time. Returns
    the lines it printed, or None and the name of what went wrong.
    """
    env = dict(os.environ)
    env.pop("CI", None)
    env.pop("GITHUB_ACTIONS", None)
    if builder:
        env["CI"] = "true"
        env["GITHUB_ACTIONS"] = "true"
    try:
        ran = subprocess.run(["bash", RUN, NAMED], cwd=HERE, env=env,
                             stdout=subprocess.PIPE,
                             stderr=subprocess.STDOUT, timeout=WAIT)
    except (OSError, subprocess.TimeoutExpired) as e:
        return None, type(e).__name__
    return ran.stdout.decode("utf-8", "replace").splitlines(), ""


def summed(lines):
    """How many closing summaries a run printed. One, in a healthy run."""
    return len([one for one in (lines or ()) if one.startswith("green:")])


# ------------------------------------------------------------------ 1.
print("1. The suite started twice, once plain and once as the builder")
plain, plain_why = suite(False)
built, built_why = suite(True)
check("both runs of the suite reached their closing summary",
      summed(plain) == 1 and summed(built) == 1,
      "%d lines here with %d summary in them, %d lines as the builder "
      "with %d -- %s" % (len(plain or ()), summed(plain), len(built or ()),
                         summed(built),
                         quiet("plain %s, builder %s"
                               % (plain_why or "ran", built_why or "ran"))))

# ------------------------------------------------------------------ 2.
print("\n2. What the run here says about the tests it did not run")
mine = []
if os.path.isdir(FOLDER):
    mine = sorted(name for name in os.listdir(FOLDER)
                  if name.endswith("_test.py"))
opened = [OPENS.match(one) for one in (plain or ())]
opened = [one for one in opened if one]
check("a run here names the Resolve tests that did not run in it",
      len(opened) == 1,
      "%d lines open with resolve: in the %d the run printed, and "
      "resolve/ holds %d test files" % (len(opened), len(plain or ()),
                                        len(mine)))

named = int(opened[0].group(1)) if opened else -1
check("the run names as many Resolve tests as resolve/ holds files",
      named == len(mine),
      "the run says %d, the folder holds %d: %s"
      % (named, len(mine), quiet(", ".join(mine)) or "none"))

after = []
if opened:
    for at, one in enumerate(plain or ()):
        if OPENS.match(one):
            after = (plain or [])[at:]
            break
check("the run names the command that starts the Resolve tests",
      any(TYPED in one for one in after),
      "%r stands in %d of the %d lines from resolve: to the end"
      % (TYPED, len([one for one in after if TYPED in one]), len(after)))

# ------------------------------------------------------------------ 3.
print("\n3. What a run on the builder says about them")
loud = [one for one in (built or ())
        if OPENS.match(one) or TYPED in one]
check("a run on the builder says nothing about the Resolve tests",
      not loud and bool(built),
      "%d of %d lines name them: %s"
      % (len(loud), len(built or ()), quiet("; ".join(loud[:2])) or "none"))

print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
