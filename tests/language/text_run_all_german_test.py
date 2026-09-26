# -*- coding: utf-8 -*-
"""The program run in German says no English sentence.

The strongest check against a line that never went through T(), because
it needs no list: the program is started twice on the interview
material -- the simple path and multitrack -- and what it prints is
read for English function words. Without that material the test says
SKIPPED and names what would bring it back. The catalogue and the
documents are read by text_no_german_left.
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
import subprocess
import time
from fixture_root import fixture
import the_program

began = time.time()
SCRIPT = the_program.SCRIPT
done = 0
bad = []


def check(what, ok, detail=""):
    global done
    done += 1
    print("  %-56s %s%s" % (what, "ok" if ok else "FAIL",
                            "" if ok else "   " + detail))
    if not ok:
        bad.append(what)


print("1. The program run in German, read back")
skipped = ""
# The strongest check, because it needs no list: a line that never went
# through T() stays English, and English function words give it away.
media = os.environ.get("VPM_MEDIA") or fixture("interview")
job = sorted(f for f in (os.listdir(media) if os.path.isdir(media) else [])
             if f.lower().endswith((".wav", ".mov")))
if len(job) < 2:
    # The machine's doing again: run.sh builds this folder and points
    # VPM_MEDIA at it, so under the suite the section runs.
    skipped = ("no material under %s (%d files of the right "
               "kind, two are needed)" % (media, len(job)))
else:
    # Two runs, so both paths are read: the simple one and multitrack.
    out = ""
    for extra in ([], ["--multitrack", "--without-auphonic"]):
        out += subprocess.run(
            [sys.executable, SCRIPT] + [os.path.join(media, f) for f in job]
            + ["--lang", "de", "--dry-run", "--no-preflight",
               "--no-metrics"] + extra,
            capture_output=True, text=True, timeout=900,
            env=dict(os.environ, LANG="C", LC_ALL="C")).stdout
    check("the German run says something at all", len(out) > 2000,
          "%d characters" % len(out))
    # Words that are English and not also German, and not a term the
    # German text uses as it stands. A hyphen counts as a letter on
    # both sides, because a word glued to one belongs to a name and
    # not to a sentence: the switch --with-libsoxr, the switch
    # --without-auphonic, the cut rule wide-after. Measured 4.9.2026,
    # so the price is known: of the 4877 lines of the English manual
    # this pattern catches, eight fall out of its reach that way, and
    # all eight are names. The limit is the other side of that -- an
    # English line whose only word from the list is glued to a hyphen
    # now goes through.
    ENGLISH = re.compile(r"(?<![A-Za-z-])(the|and|with|from|into|"
                         r"which|would|there|their|because|"
                         r"before|after|between|through|without)"
                         r"(?![A-Za-z-])")
    left = []
    for line in out.splitlines():
        # Paths and file names carry English words and are not text.
        bare = re.sub(r"[^\s]*[/\\][^\s]*", "", line)
        m = ENGLISH.search(bare)
        if m:
            left.append((m.group(0), bare.strip()[:60]))
    check("and no English sentence is left in it", not left, str(left[:3]))

print("\n%d checks in %.2f s" % (done, time.time() - began))
# A run.sh run builds the material and points VPM_MEDIA at it, so this
# line only stands where the test was started without it.
if skipped:
    print("SKIPPED: %s -- run it through run.sh, which builds the "
          "interview material, or point VPM_MEDIA at a folder with two "
          "recordings" % skipped)
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
