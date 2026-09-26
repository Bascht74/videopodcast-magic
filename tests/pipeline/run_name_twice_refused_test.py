# -*- coding: utf-8 -*-
"""A name on a recording and on a voice is refused at both doors alike.

On way_ground's production with the presenter's recorder added: its row
carries the name a separated voice carries, and merged, each of that
person's turns would count twice. In order: the window holds its
start back and says whose name it is; the command line returns 1, its
last line the same sentence, and leaves no handover behind.
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
import re
import shutil
import tempfile
import time
import the_program
import way_ground as ground

SCRIPT = the_program.SCRIPT
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


if ground.missing():
    print("SKIPPED: " + ground.missing())
    stop()

vpm = the_program.load()
vpm.set_language("en")
# The presenter's recorder, both blocks: the row way_ground leaves out.
PRESENTER = sorted(glob.glob(os.path.join(ground.MEDIA, "Presenter_*")))
# A precondition of the material, not a judgement about the program.
assert len(PRESENTER) == 2, PRESENTER
SAID = vpm.T('%s is on more than one speaker -- a name is a person, and '
             'every person needs their own.') % "Presenter"

print("1. The window")
source = ground.media(ground.HEARD_IN)
cam = dict((who, ground.media(c)) for who, c in ground.SEAT.items())
assign = [(PRESENTER, vpm.Value("Presenter"), vpm.Value(cam["Presenter"])),
          ([source], vpm.Value(""), vpm.Value(""))]
voices = [(vpm.voice_key(source, ground.LABEL[who]), vpm.Value(who),
           vpm.Value(cam[who])) for who in sorted(ground.LABEL)]
held = vpm.missing_conditions(
    PRESENTER + [source], ground.PRODUCTION, False, assign, [], voices,
    [source]).get(22)
check("the window holds the start back and names the name twice",
      held == SAID, "the sheet says %r against %r" % (held, SAID))

print("\n2. The command line")
work = tempfile.mkdtemp(prefix="vpm_twice_")
out = os.path.join(work, "out")
os.makedirs(out)
cache = os.path.join(work, "cache")
argv = ground.line(SCRIPT, ground.separation_file(vpm, work), out,
                   PRESENTER)
code, said, stuck = ground.line_run(argv, cache)
text = re.sub(r"\x1b\[[0-9;]*m", "", said).replace("\r", "\n")
lines = [x.strip() for x in text.splitlines() if x.strip()]
last = lines[-1] if lines else ""
WANT = vpm.T('Abort: %s') % SAID
check("the line with one name on a recording and a voice returns 1",
      code == 1 and not stuck,
      "returned %r against 1%s, last line %r"
      % (code, ", stuck" if stuck else "", last))
check("and its last line is the window's sentence",
      last == WANT, "last line %r against %r" % (last, WANT))
left = sorted(os.listdir(out))
check("and it leaves no handover behind", ground.handover(out) is None,
      "%d files in the output folder: %s" % (len(left), left[:6]))
shutil.rmtree(work, True)
stop()
