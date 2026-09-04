# -*- coding: utf-8 -*-
"""Nothing this program says is made before the language is settled.

The complaint about ffmpeg is the case that showed it: made at the top
of main() and shown much later, so a run with --lang de had its first
line in English and its second in German. Two parts, and the first is
the wider one: the shape -- nothing in main() that can reach T() is
called before the language is settled -- and then the case itself, a
run below the floor read in both directions, against a copy whose
floor no ffmpeg on this machine can reach.

The limit of the method: argparse's own words -- the usage line,
"unrecognized arguments" -- are English whatever the language, and no
T() carries them. They are not what this measures.
"""
import ast
import io
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time

import the_program

began = time.time()
done = 0
bad = []


def check(name, ok, extra=""):
    global done
    done += 1
    print("  %-58s %s %s" % (name, "ok" if ok else "FAIL", extra))
    if not ok:
        bad.append("%s [%s]" % (name, extra or "no numbers"))


SCRIPT = the_program.SCRIPT
m = the_program.load()
TREE = ast.parse(the_program.text())

# ------------------------------------------------------------- the shape
print("1. Nothing speaks before the language is settled")

# Only functions the program itself defines at its top level, and only
# calls made by bare name. A method called `set` or `split` on some
# object elsewhere carries the name of a function here otherwise, and
# the chain below then reports a way that does not exist.
MODULE = {}
for node in TREE.body:
    if isinstance(node, ast.FunctionDef):
        MODULE.setdefault(node.name, []).append(node)


def calls_in(node):
    """Every function of this program that piece of source calls."""
    out = []
    for bit in ast.walk(node):
        if isinstance(bit, ast.Call) and isinstance(bit.func, ast.Name) \
                and bit.func.id in MODULE:
            out.append((bit.func.id, bit.lineno))
    return out


EDGES = {}
for name, nodes in MODULE.items():
    EDGES[name] = [one for node in nodes for one in calls_in(node)]


def way_to_T(name, above=()):
    """The chain of calls from that function down to T(), or None.

    The chain and not a yes: a red line saying only that something
    speaks leaves the reader to find out through what.
    """
    if name in above or name not in EDGES:
        return None
    for called, line in EDGES[name]:
        if called in ("T", "TN"):
            return ["%s (line %d)" % (called, line)]
        rest = way_to_T(called, above + (name,))
        if rest:
            return ["%s (line %d)" % (called, line)] + rest
    return None


MAIN = [node for node in TREE.body
        if isinstance(node, ast.FunctionDef) and node.name == "main"]
BODY = MAIN[0].body if MAIN else []
settles = None
for i, one in enumerate(BODY):
    if any(isinstance(bit, ast.Call) and isinstance(bit.func, ast.Name)
           and bit.func.id == "set_language" for bit in ast.walk(one)):
        settles = i
        break
check("main settles the language before it does its work",
      settles is not None,
      "%d main() in the program, %d statements in it, %s set_language"
      % (len(MAIN), len(BODY),
         "statement %d calls" % settles if settles is not None
         else "none of them calls"))

# Everything above that statement. Where there is none, that is the
# whole of main(), and this check falls with the one above rather than
# passing over a program that never settles a language at all.
early = []
for one in BODY[:settles]:
    for called, line in calls_in(one):
        if called in ("T", "TN"):
            early.append("%s itself (line %d)" % (called, line))
            continue
        way = way_to_T(called)
        if way:
            early.append("%s (line %d) -> %s"
                         % (called, line, " -> ".join(way)))
check("nothing that can say a sentence is called before that",
      bool(MAIN) and not early,
      "%d call(s) in main() before the language is settled reach T(): %s"
      % (len(early), " | ".join(early[:2]) or "none"))

# --------------------------------------------------------------- the case
print("\n2. A run below the ffmpeg floor says so in the language asked for")

# The wording is taken out of the catalogue and never written down
# here: a literal ties the judgement to one translation of the day.
SAYS = 'Here: %s. Needed: %s or newer.'
m.set_language("de")
GERMAN = [bit for bit in m.T(SAYS).split("%s") if bit.strip()]
m.set_language("en")
ENGLISH = [bit for bit in m.T(SAYS).split("%s") if bit.strip()]
check("the sentence both runs are read by is translated at all",
      GERMAN != ENGLISH,
      "German %r against English %r -- with the two the same, both "
      "judgements below are true whatever the program does"
      % (" ".join(GERMAN)[:40], " ".join(ENGLISH)[:40]))

# A copy, because nothing on the command line puts a run below the
# floor: this machine's ffmpeg is at it or above it, and there is no
# switch that lowers it. models/ stays behind -- 33 MB of speaker model
# that a run stopped at the gate never opens.
work = tempfile.mkdtemp()
copy = os.path.join(work, "videopodcast_magic")
shutil.copytree(os.path.dirname(SCRIPT), copy,
                ignore=shutil.ignore_patterns("models", "__pycache__",
                                              "*.log"))
INSIDE = os.path.join(copy, "__init__.py")
OUT_OF_REACH = (99, 0, 0)
LIFTED = "FFMPEG_FLOOR = (99, 0, 0)"
whole = io.open(INSIDE, encoding="utf-8").read()
raised = re.sub(r"^FFMPEG_FLOOR = \(.*\)$", LIFTED, whole, count=1,
                flags=re.M)
io.open(INSIDE, "w", encoding="utf-8").write(raised)
check("the copy's floor is out of reach of every ffmpeg there is",
      raised != whole and m.FFMPEG_FLOOR < OUT_OF_REACH,
      "the floor line was %sreplaced in the copy, and the program's own "
      "floor is %s, which has to stay under %s"
      % ("" if raised != whole else "not ",
         m.version_text(m.FFMPEG_FLOOR), m.version_text(OUT_OF_REACH)))

# The floor of the copy, as the sentence writes it. Both languages put
# the number in the same place, so it finds the line whatever language
# the line came out in -- and a banner printed in front of it one day
# does not turn this into a judgement about banners.
MARK = m.version_text(OUT_OF_REACH)
absent = os.path.join(work, "no-such-recording.wav")
# VPM_SILENT: nothing is installed and nothing fetched, so the run
# stops at the complaint. LANGUAGE=en so that the run which asks for
# nothing is an English one wherever this is started.
BASE = dict(os.environ, LANG="C", LC_ALL="C", LANGUAGE="en",
            VPM_SILENT="1", VPM_NO_UPDATE_CHECK="1")


def complaint(*more):
    """The line that run made about the floor, and the head of its output."""
    ran = subprocess.run(
        [sys.executable, INSIDE, absent, "--dry-run"] + list(more),
        capture_output=True, text=True, timeout=300, env=BASE,
        stdin=subprocess.DEVNULL)
    said = ran.stdout + ran.stderr
    for line in said.split("\n"):
        if MARK in line:
            return line.strip(), said
    return "", said


german, said = complaint("--lang", "de")
missing = [bit for bit in GERMAN if bit not in german]
check("a run that asked for German is told in German that ffmpeg is old",
      bool(german) and not missing,
      "the line is %r; %d of %d pieces of the German wording missing: %s"
      % (german[:70] or ("nothing said about %s, output began %r"
                         % (MARK, " ".join(said.split())[:60])),
         len(missing), len(GERMAN), missing[:2] or "none"))

english, said = complaint()
missing = [bit for bit in ENGLISH if bit not in english]
check("and a run that asked for nothing is told in the machine's language",
      bool(english) and not missing,
      "the line is %r; %d of %d pieces of the English wording missing: %s"
      % (english[:70] or ("nothing said about %s, output began %r"
                          % (MARK, " ".join(said.split())[:60])),
         len(missing), len(ENGLISH), missing[:2] or "none"))

shutil.rmtree(work, ignore_errors=True)
print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
