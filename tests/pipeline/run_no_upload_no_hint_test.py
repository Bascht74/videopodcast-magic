# -*- coding: utf-8 -*-
"""The run promises to save an upload only where it uploads.

Missing audio past half a minute is filled with silence, and the line
saying so added that an In or Out point saves the upload -- also in a
run with --without-auphonic, which uploads nothing. The sections: which
runs upload; what the line says with an upload, without one, and for a
short gap; and whether the run's own report asks the first before it
says the second.
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
from argparse import Namespace
import the_program

began = time.time()
vpm = the_program.load()
vpm.set_language("en")
done = 0
bad = []


def check(name, ok, extra=""):
    global done
    done += 1
    print("  %-58s %s %s" % (name, "ok" if ok else "FAIL", extra))
    if not ok:
        bad.append("%s [%s]" % (name, extra or "no numbers"))


print("\n1. Which runs upload")
said = vpm.run_uploads(Namespace(without_auphonic=False, auphonic_done=None))
check("a run with Auphonic uploads", said is True, "got %r" % said)
said = vpm.run_uploads(Namespace(without_auphonic=True, auphonic_done=None))
check("a run with --without-auphonic uploads nothing", said is False,
      "got %r" % said)
said = vpm.run_uploads(Namespace(without_auphonic=False,
                                 auphonic_done="/tmp/processed"))
check("a run handed processed tracks uploads nothing", said is False,
      "got %r" % said)

print("\n2. The line")
SAVES = vpm.T(' -- an In or Out point saves the upload')
FILLED = vpm.T('Missing audio %s filled with silence%s')
line = vpm.silence_sentence("up to 0:04:00", 240.0, True)
check("four minutes missing in an uploading run name the saving",
      SAVES in line, repr(line))
line = vpm.silence_sentence("up to 0:04:00", 240.0, False)
check("four minutes missing in a local run name no saving",
      SAVES not in line, repr(line))
check("a local run still says the silence was filled",
      line == FILLED % ("up to 0:04:00", ""),
      "%r, wanted %r" % (line, FILLED % ("up to 0:04:00", "")))
line = vpm.silence_sentence("up to 0:00:20", 20.0, True)
check("twenty seconds missing name no saving, upload or not",
      SAVES not in line, repr(line))

print("\n3. The run's own report")
HERE = os.path.dirname(os.path.abspath(the_program.SCRIPT))
RUN = open(os.path.join(HERE, "pipeline", "__init__.py"),
           encoding="utf-8").read()
# The call as it stands in the report, arguments and all, and not the
# line that defines it: a report that hands on a fixed True promises the
# saving to every run again.
call = re.search(r'(?<!def )silence_sentence\((?:[^()]|\([^()]*\))*\)', RUN)
check("the run's report asks whether this run uploads",
      bool(call) and "run_uploads(args)" in call.group(0),
      call.group(0) if call else "no call of silence_sentence in pipeline")

print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
