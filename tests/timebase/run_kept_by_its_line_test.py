# -*- coding: utf-8 -*-
"""A dry run's handover is kept under what decides it, and nothing else.

The key a dry run keeps its handover under, handover_key over
line_words, is what the window's preview looks its cut up by. Sections:
what leaves the key alone -- --dry-run, the switches about auphonic.com
(preset, returned folder), the plan file's own path, the plan read off
its file or handed in; what moves it -- a cut number and an In point
(E-533), the plan, a file the line names; and what the cut stage alone
decides, words_but_the_cut.
In memory, over small files of the test's own and a store of its own.
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
import json
import shutil
import tempfile
import time
import the_program

WORK = tempfile.mkdtemp(prefix="vpm_linekey_")
os.environ["VPM_CACHE"] = os.path.join(WORK, "cache")
vpm = the_program.load()
vpm.set_language("en")

began = time.time()
done = 0
bad = []


def check(name, ok, extra=""):
    global done
    done += 1
    print("  %-58s %s %s" % (name, "ok" if ok else "FAIL", extra))
    if not ok:
        bad.append("%s [%s]" % (name, extra or "no numbers"))


def made(name, text):
    """A small file of the test's own, by name; its path."""
    path = os.path.join(WORK, name)
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)
    return path


AUDIO = made("Guest_Take0031A.wav", "a recording stood in for")
CAMERA = made("GuestCam_01011858_C003.mov", "a camera stood in for")
PLAN = {"production": "Way", "tracks_of": [
    {"audio": AUDIO, "speakers": "Guest", "camera": CAMERA}]}
PLAN_FILE = made("vpm_assign_one.json", json.dumps(PLAN))
OTHER_PLAN_FILE = made("vpm_assign_two.json", json.dumps(PLAN, indent=1))
LINE = ["videopodcast_magic.py", AUDIO, CAMERA, "--out", WORK,
        "--multitrack", "--assign", PLAN_FILE, "--in-point", "+0:00:10",
        "--min-edit-duration", "3.0", "--on-question", "answer"]


def key(argv, plan=None):
    """The key a dry run of *argv* keeps its handover under."""
    return vpm.handover_key(*vpm.line_words(argv, plan))


def swapped(argv, old, new):
    """*argv* with the word after *old* set to *new*."""
    out = list(argv)
    out[out.index(old) + 1] = new
    return out


BASE = key(LINE)

print("What leaves the key alone")
dry = LINE + ["--dry-run", "--without-auphonic"]
check("--dry-run and --without-auphonic leave the key as it was",
      key(dry) == BASE, "%s against %s" % (key(dry), BASE))
sent = LINE + ["--auphonic-preset", "Podcast", "--auphonic-done", WORK]
check("a preset and a folder from auphonic.com leave the key alone",
      key(sent) == BASE, "%s against %s" % (key(sent), BASE))
moved = swapped(LINE, "--assign", OTHER_PLAN_FILE)
check("the same plan in another file keys alike",
      key(moved) == BASE, "%s against %s" % (key(moved), BASE))
handed = swapped(LINE, "--assign", "<not written yet>")
check("the window's plan handed in keys as the run's file does",
      key(handed, json.loads(json.dumps(PLAN))) == BASE,
      "%s against %s" % (key(handed, PLAN), BASE))

print("\nWhat moves it")
cut = swapped(LINE, "--min-edit-duration", "3.5")
check("a cut number moves the key", key(cut) != BASE,
      "3.0 s and 3.5 s both keyed %s" % BASE)
marked = swapped(LINE, "--in-point", "+0:00:20")
check("an In point moves the key", key(marked) != BASE,
      "+0:00:10 and +0:00:20 both keyed %s" % BASE)
renamed = json.loads(json.dumps(PLAN))
renamed["tracks_of"][0]["speakers"] = "Presenter"
check("another plan moves the key",
      key(handed, renamed) != BASE, "Guest and Presenter both keyed %s"
      % BASE)
later = os.stat(CAMERA).st_mtime + 60
os.utime(CAMERA, (later, later))
check("a file the line names, changed, moves the key", key(LINE) != BASE,
      "the camera a minute later still keyed %s" % BASE)

print("\nWhat the cut stage alone decides")
kept = vpm.words_but_the_cut(vpm.line_words(LINE)[0])
# By name alone in the evidence: the folder is this run's own.
shown = [os.path.basename(w) for w in kept]
check("the cut's numbers are left out of what the handover stands on",
      "--min-edit-duration" not in kept and "--on-question" not in kept
      and "3.0" not in kept and "answer" not in kept, str(shown))
check("an In point stays in what the handover stands on",
      kept[kept.index("--in-point") + 1] == "+0:00:10"
      if "--in-point" in kept else False, str(shown))

shutil.rmtree(WORK, ignore_errors=True)
print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
