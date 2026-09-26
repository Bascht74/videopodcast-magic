# -*- coding: utf-8 -*-
"""A key nobody holds is turned away, and the reason is auphonic.com's own.

Against auphonic.com itself: the suite's stand-ins only ever say what
somebody guessed a refusal looks like. The made-up key is sent the way
the window sends one when presets are fetched; the answer has to be a
refusal and not a list, and a readable one, not a reply the program
cannot parse. Costs no credit; the key this machine keeps is not read.
"""
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import auphonic_ground as ground

ground.gate()

began = time.time()
done = 0
bad = []


def check(name, ok, extra=""):
    global done
    done += 1
    print("  %-58s %s %s" % (name, "ok" if ok else "FAIL", extra))
    if not ok:
        bad.append("%s [%s]" % (name, extra or "no numbers"))


vpm = ground.program()

print("1. A made-up key, sent the way the window sends one")
presets, said = None, ""
try:
    presets = vpm.list_presets(ground.REFUSED_KEY)
except RuntimeError as e:
    said = " ".join(str(e).split())
check("a key nobody holds gets no list of presets",
      presets is None, "%d presets came back" % len(presets or ()))
check("the refusal is auphonic.com's answer and not a broken reply",
      bool(said) and vpm.T('Response was not JSON: %s').split("%")[0]
      not in said, said[:200] or "nothing was said")

print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
