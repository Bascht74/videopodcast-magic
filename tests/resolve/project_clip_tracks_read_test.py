# -*- coding: utf-8 -*-
"""A media pool clip's audio tracks are counted from what Resolve reports.

source_channel_count against stand-in clips whose GetAudioMapping
answers in each shape the interface has been seen to take. In turn: the
documented answer, four channels embedded and one track used; the same
as JSON text; a list; the mapping as the outermost level; channels that
are not a whole number; and the answers that give no count -- a raise,
an empty list, broken JSON, something that is not a mapping, and a
mapping with no track in it.
The function is read only by --resolve-audio-tracks, which looks and
changes nothing.
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
import json
import time
import resolve_stand_in as stand

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


def count(mapping, **switches):
    """(tracks, channels) for a clip answering with this mapping."""
    clip = stand.Clip("/tmp/GuestCam_C003.mov", mapping=mapping, **switches)
    try:
        return vpm.source_channel_count(clip)
    except Exception as e:  # a raise is what it must never hand on
        return "raised", str(e)[:60]


MONO = {"channel_idx": [1], "mute": False, "type": "mono"}
DOCUMENTED = {"embedded_audio_channels": 4, "linked_audio": {},
              "track_mapping": {"1": MONO}}

print("1. Answers that give a count")
got = count(DOCUMENTED)
check("the documented answer gives one track of four channels",
      got == (1, 4), "got %r" % (got,))
got = count(json.dumps(DOCUMENTED))
check("the same answer as JSON text gives the same count",
      got == (1, 4), "got %r" % (got,))
got = count([MONO, MONO, MONO])
check("a list of tracks is counted, with no channel number",
      got == (3, None), "got %r" % (got,))
got = count({"1": MONO, "2": MONO})
check("a mapping that is the outermost level is counted",
      got == (2, None), "got %r" % (got,))
got = count({"embedded_audio_channels": "4", "track_mapping": {"1": MONO}})
check("channels that are not a whole number are not reported",
      got == (1, None), "got %r" % (got,))

print("\n2. Answers that give none")
got = count(DOCUMENTED, throw=["GetAudioMapping"])
check("a clip that raises gives no count", got == (None, None),
      "got %r" % (got,))
got = count([])
check("a clip that says nothing gives no count", got == (None, None),
      "got %r" % (got,))
got = count("{not json")
check("an answer that is not JSON gives no count", got == (None, None),
      "got %r" % (got,))
got = count(7)
check("an answer that is no mapping gives no count", got == (None, None),
      "got %r" % (got,))
got = count({"embedded_audio_channels": 2, "track_mapping": {}})
check("a mapping with no track keeps its channels and gives no count",
      got == (None, 2), "got %r" % (got,))

print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
