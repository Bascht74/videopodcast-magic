# -*- coding: utf-8 -*-
"""While mixing, a track is named by its speaker, and only the mix as the mix.

The line shown while a track is mixed took the target's file name and
replaced "full" and the two prefixes wherever they stood, so a speaker
called Carefully was announced as CareFull-Mixy.

The sections: the file names the run gives its targets, taken out of
the run rather than written down here; the overall mix under its name;
three speakers whose names only look like the mix or its prefixes; and
whether the mixing call asks this rather than a replace of its own.
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
import inspect
import re
import time
import the_program

began = time.time()
vpm = the_program.load()
done = 0
bad = []


def check(name, ok, extra=""):
    global done
    done += 1
    print("  %-58s %s %s" % (name, "ok" if ok else "FAIL", extra))
    if not ok:
        bad.append("%s [%s]" % (name, extra or "no numbers"))


print("\n1. The names the run gives its targets")
# Out of pipeline, not spelt out here: a test that writes the file name
# down stays green the day the run calls it something else, and the mix
# is then announced as a file.
HERE = os.path.dirname(os.path.abspath(the_program.SCRIPT))
RUN = open(os.path.join(HERE, "pipeline", "__init__.py"),
           encoding="utf-8").read()
# Each pattern stays inside its own call: .*? once ran on past the
# speakers' call into the camera mix below it, and took that call's mix_
# for the speakers' prefix.
_mix = re.search(r'full_mix = mix_tracks\([^)]*?"(mix_\w+\.wav)"', RUN)
MIX_FILE = _mix.group(1) if _mix else ""
check("the run still names the file of its overall mix", bool(MIX_FILE),
      MIX_FILE or "no file name after full_mix = mix_tracks( in pipeline")
_one = re.search(r'single\[track\["name"\]\] = mix_tracks\([^)]*?"(\w+_)%s\.wav"',
                 RUN)
SPEAKER = _one.group(1) if _one else ""
check("the run still names its speakers' files", bool(SPEAKER),
      SPEAKER or "no speaker target built from the track's name in pipeline")

print("\n2. The overall mix")
said = vpm.mixing_label(os.path.join("work", MIX_FILE))
check("the overall mix is announced by the mix's own name",
      said == vpm.MIX_TRACK_NAME,
      "%r for %r, wanted %r" % (said, MIX_FILE, vpm.MIX_TRACK_NAME))

print("\n3. Speakers whose names only look like it")
said = vpm.mixing_label(os.path.join("work", SPEAKER + "Carefully.wav"))
check("a speaker whose name holds full keeps that name",
      said == "Carefully", "%r, wanted 'Carefully'" % said)
said = vpm.mixing_label(os.path.join("work", SPEAKER + "Remix_Anna.wav"))
check("a speaker whose name holds a prefix keeps all of it",
      said == "Remix_Anna", "%r, wanted 'Remix_Anna'" % said)
said = vpm.mixing_label(os.path.join("work", SPEAKER + "full.wav"))
check("a speaker called full is not announced as the mix",
      said == "full", "%r, wanted 'full'" % said)

print("\n4. The mixing call asks this")
# A right answer nobody asks repairs nothing: the line is made inside
# mix_tracks, and a replace of its own there would bring the fault back.
_body = inspect.getsource(vpm.mix_tracks)
check("the progress line of a mix is named by mixing_label",
      "mixing_label(target)" in _body,
      "mix_tracks %s mixing_label(target)"
      % ("calls" if "mixing_label(target)" in _body else "does not call"))

print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
