# -*- coding: utf-8 -*-
"""A short mono file goes through a real production and comes back as audio.

Against auphonic.com itself, and it spends credit: twenty seconds of
tone through the account's first single-track preset, or the one
VPM_LIVE_PRESET names. In order -- the program uploads and starts in one
call, waits, and fetches the result; the result is a file of about the
length sent; and the production, found again by its title, is deleted.
The title has the tests' own shape, so a run killed half way is cleared
by the sweep auphonic.sh makes at both ends.

A step that throws is a failed judgement and not a traceback, so the
closing count is reached whatever happens.
"""
import os
import shutil
import sys
import tempfile
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import auphonic_ground as ground

ground.gate(spends=True)

began = time.time()
done = 0
bad = []
SECONDS = 20


def check(name, ok, extra=""):
    global done
    done += 1
    print("  %-58s %s %s" % (name, "ok" if ok else "FAIL", extra))
    if not ok:
        bad.append("%s [%s]" % (name, extra or "no numbers"))


def said(e):
    """An exception as one short line."""
    return " ".join(str(e).split())[:200]


vpm = ground.program()
key, origin = ground.the_key(vpm)
preset = ground.a_preset(vpm, key, multitrack=False)
folder = tempfile.mkdtemp(prefix="vpm_auphonic_live_")
title = ground.a_test_title("mono")
try:
    audio = ground.tone(os.path.join(folder, "tone.wav"), SECONDS, 1)

    print("1. Upload, start, wait and fetch, the way a run does")
    result, why = None, ""
    try:
        result = vpm.run_single_production(
            audio, preset, "the account's preset", key,
            os.path.join(folder, "back"), wait_s=900, title=title)
    except RuntimeError as e:
        why = said(e)
    check("the production comes back with a file",
          bool(result) and os.path.isfile(result),
          why or "the program returned %r"
          % (os.path.basename(result) if result else result,))

    print("\n2. What came back")
    length = None
    if result and os.path.isfile(result):
        try:
            length = ground.measured(result)[0]
        except (OSError, ValueError) as e:
            why = said(e)
    check("the file that came back is about as long as the one sent",
          length is not None and abs(length - SECONDS) < 1.5,
          "%s s back against %d s sent%s"
          % (length, SECONDS, (" -- " + why) if length is None else ""))

    print("\n3. The production is taken away again")
    found, why = None, ""
    try:
        found = vpm.find_production_by_title(key, title)
    except RuntimeError as e:
        why = said(e)
    check("the production stands at auphonic.com under the title given",
          bool(found) and bool(found.get("uuid")),
          why or "%s under %s among the last 50"
          % ((found or {}).get("uuid") or "none", title))
    if found and found.get("uuid"):
        gone, why = False, ""
        try:
            gone = ground.delete(vpm, key, found["uuid"])
        except RuntimeError as e:
            why = said(e)
        check("the tests' own production can be deleted again", gone,
              why or "auphonic.com said %s to deleting %s"
              % ("yes" if gone else "no", found["uuid"]))
finally:
    shutil.rmtree(folder, ignore_errors=True)

print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
