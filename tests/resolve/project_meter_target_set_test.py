# -*- coding: utf-8 -*-
"""The loudness meter in Resolve aims at our level, or says how to set it.

set_loudness_target against stand-in projects whose settings list is
what Resolve hands out. In turn: the target found among the settings and
set; a target Resolve reads back otherwise reported as missed; a project
with no target setting told to set it by hand, at our level written with
a point even in German, which Resolve's field would not take back; and a
project that will not list its settings left untouched.
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
import the_program
import contextlib
import io
import time
import resolve_stand_in as stand

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


SCALE = "audioMeterLoudnessScale"
TARGET = "audioLoudnessTargetLevel"


def aim(p, lufs):
    """(what set_loudness_target returned, what it printed)."""
    out = io.StringIO()
    with contextlib.redirect_stdout(out):
        try:
            got = vpm.set_loudness_target(p, lufs)
        except Exception as e:  # a raise is what it must never hand on
            got = "raised: %s" % e
    return got, out.getvalue()


def sets(p):
    """Every SetSetting the program made on this project, as (key, value)."""
    return [c[1:] for c in p.calls if c[0] == "SetSetting"]


print("1. The target is found and set")
p = stand.Project(settings={SCALE: "LUFS", TARGET: "-23",
                            "timelineFrameRate": "25"})
got, said = aim(p, -16.0)
check("the meter target is set to our level",
      got is True and p.settings[TARGET] == "-16",
      "returned %r, %s now %r" % (got, TARGET, p.settings[TARGET]))

print("\n2. Resolve keeps a different value")
p = stand.Project(settings={TARGET: "-23"}, reads_back={TARGET: "-23"})
got, said = aim(p, -16.0)
line = [l for l in said.splitlines() if TARGET in l]
check("a target Resolve reads back otherwise is reported as missed",
      got is False and len(line) == 1 and "-23" in line[0]
      and "-16" in line[0],
      "returned %r, said %r" % (got, line))

print("\n3. No target among the settings")
p = stand.Project(settings={SCALE: "LUFS", "timelineFrameRate": "25"})
got, said = aim(p, -16.0)
check("a project without a target setting is told how to set it by hand",
      got is None and "-16" in said and not sets(p),
      "returned %r, set %r, said %r" % (got, sets(p), said.strip()[:90]))
vpm.set_language("de")
try:
    got, said = aim(stand.Project(settings={}), -14.5)
finally:
    vpm.set_language("en")
check("the level for the hand is written with a point in every language",
      "-14.5" in said and "-14,5" not in said,
      "said %r" % said.strip()[-70:])

print("\n4. Settings that cannot be listed")
p = stand.Project(settings={TARGET: "-23"}, throw=["GetSetting"])
got, said = aim(p, -16.0)
check("a project that will not list its settings is left untouched",
      got is None and not sets(p) and p.settings[TARGET] == "-23",
      "returned %r, set %r" % (got, sets(p)))

print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
