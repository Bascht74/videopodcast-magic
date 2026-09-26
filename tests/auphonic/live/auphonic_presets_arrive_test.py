# -*- coding: utf-8 -*-
"""The key this machine keeps is taken, and the presets come back readable.

Against auphonic.com itself, not a stand-in: the suite has never asked
it. In order -- the list of presets the program fetches with the key it
keeps, every entry with a name and a uuid, and one preset read in full
by the uuid the list gave. Costs no credit; nothing is made.

The limit is that what an account holds is the owner's: an account with
no preset at all leaves the reading of one out and says so.
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
key, origin = ground.the_key(vpm)

print("1. The list of presets, asked with the key from the %s" % origin)
presets, why = None, ""
try:
    presets = vpm.list_presets(key)
except RuntimeError as e:
    why = " ".join(str(e).split())[:200]
check("auphonic.com answers the kept key with a list of presets",
      presets is not None, why or "%d presets" % len(presets or ()))
presets = presets or []
no_uuid = [i for i, (name, uuid, mark) in enumerate(presets) if not uuid]
check("every preset in the list carries a uuid",
      not no_uuid, "%d of %d without one, at places %s"
      % (len(no_uuid), len(presets), no_uuid[:5]))
unnamed = [i for i, (name, uuid, mark) in enumerate(presets)
           if name == vpm.T('unnamed')]
check("every preset in the list carries a name",
      not unnamed, "%d of %d without one, at places %s"
      % (len(unnamed), len(presets), unnamed[:5]))
kinds = [mark for name, uuid, mark in presets]
print("      of %d presets: %d multitrack, %d single-track, %d unclassified"
      % (len(kinds), kinds.count(True), kinds.count(False), kinds.count(None)))

print("\n2. One preset read in full by the uuid the list gave")
if not presets:
    print("LEFT OUT: the account holds no preset, so none can be read -- "
          "create one at auphonic.com")
else:
    uuid = presets[0][1]
    full, why = None, ""
    try:
        full = vpm.read_preset(key, uuid)
    except RuntimeError as e:
        why = " ".join(str(e).split())[:200]
    check("the preset read in full is the one the list named",
          bool(full) and full.get("uuid") == uuid,
          why or "asked for %s, came back %s"
          % (uuid, (full or {}).get("uuid")))

print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
