# -*- coding: utf-8 -*-
"""No wide shot is put on the short answer the speech floor keeps.

An "mhm" under the floor is thrown away before the pause search runs,
and the break rule then aims at the hole it left: a wide shot over
somebody answering. The material is a guest holding the floor for a
quarter of an hour with an "mhm" in every twenty-fifth breath, cut
twice: once at the floor the program uses, once at the old four
tenths. It holds because the floor keeps the answer, not because the
cut avoids speech -- an answer under the floor can still be covered,
so this says nothing about a floor lower than the one in use.
"""
import inspect
import os
import sys
import time
HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = os.environ.get("VPM_SCRIPT") or os.path.join(
    os.path.dirname(HERE), "videopodcast-magic.py")
import importlib.util
spec = importlib.util.spec_from_file_location("vpm", SCRIPT)
vpm = importlib.util.module_from_spec(spec); sys.modules["vpm"] = vpm
spec.loader.exec_module(vpm)

began = time.time()
done = 0
bad = []


def check(name, ok, extra=""):
    global done
    done += 1
    print("  %-58s %s %s" % (name, "ok" if ok else "FAIL", extra))
    if not ok:
        bad.append("%s [%s]" % (name, extra or "no numbers"))


GUEST, HOST = "Guest", "Host"
GUEST_CAM, HOST_CAM, WIDE = "guest.mov", "host.mov", "wide.mov"
LENGTH = 900.0
TURN, BREATH = 4.0, 0.5
# Long enough to survive the floor the program uses and short enough to
# fall under the old one, which is what the whole case turns on.
ANSWER = 0.30
EVERY = 25.0
# The floor before this one. A number, not a constant read out of the
# program: read from there, both sides of the comparison would move
# together and the test would be green about nothing.
OLD_FLOOR = 0.4
# How long a breath may be and still be closed over. Taken from the
# measurement itself so a second copy cannot go stale.
CLOSED = inspect.signature(vpm.speakers_from_tracks).parameters["gap"].default


def monologue():
    """A guest holding the floor, with an "mhm" in every 25th breath."""
    guest, answers, at = [], [], 0.0
    while at + TURN <= LENGTH:
        ends = at + TURN
        guest.append((round(at, 2), round(ends, 2)))
        if ends // EVERY != (ends - TURN - BREATH) // EVERY:
            said = ends + (BREATH - ANSWER) / 2.0
            answers.append((round(said, 2), round(said + ANSWER, 2)))
        at = ends + BREATH
    return guest, answers


def with_floor(parts, floor):
    """Breaths closed over first, then what is still short thrown away."""
    joined = []
    for a, b in parts:
        if joined and a - joined[-1][1] <= CLOSED:
            joined[-1][1] = max(joined[-1][1], b)
        else:
            joined.append([a, b])
    return ([(a, b) for a, b in joined if b - a >= floor],
            [(a, b) for a, b in joined if b - a < floor])


def cut_at(floor):
    """The cut at that floor: shots, what the break rule added, and hits."""
    kept, thrown = with_floor(ANSWERS, floor)
    common = dict(tracks=[(GUEST, GUEST_BLOCKS), (HOST, kept)],
                  length=LENGTH, camera_of={GUEST: GUEST_CAM, HOST: HOST_CAM},
                  wide_shot=WIDE, rules=vpm.cut_rules())
    plain = vpm.camera_cut(after=0, **common)
    whole = vpm.camera_cut(after=vpm.WIDE_AFTER_S, **common)
    stood = set(round(a, 3) for a, _b, _w in plain)
    added = [(a, b) for a, b, who in whole
             if who == WIDE and round(a, 3) not in stood]
    return dict(kept=len(kept), thrown=len(thrown), added=len(added),
                on_speech=[(a, s) for a, b in added
                           for s, _e in thrown if a <= s < b])


GUEST_BLOCKS, ANSWERS = monologue()
NOW = cut_at(vpm.SPEECH_MIN_LEN_S)
THEN = cut_at(OLD_FLOOR)

print("1. What the two floors leave of the short answers")
# The material has to carry the fault before the cut can be asked
# anything about it: at the old floor the answers have to be gone, and
# at today's they have to be there.
check("the material holds short answers to be thrown away at all",
      len(ANSWERS) >= 20,
      "%d answers of %.2f s in %.0f s" % (len(ANSWERS), ANSWER, LENGTH))
check("the floor the program uses keeps every one of them",
      NOW["thrown"] == 0 and NOW["kept"] == len(ANSWERS),
      "%d kept, %d thrown away of %d"
      % (NOW["kept"], NOW["thrown"], len(ANSWERS)))
check("at a floor of four tenths the same answers are thrown away",
      THEN["thrown"] == len(ANSWERS),
      "%d thrown away of %d at %.2f s"
      % (THEN["thrown"], len(ANSWERS), OLD_FLOOR))

print("\n2. Where the break rule puts the wide shot")
check("the break rule does break the monologue up at both floors",
      NOW["added"] > 0 and THEN["added"] > 0,
      "%d wide shots put in at the floor in use, %d at %.2f s"
      % (NOW["added"], THEN["added"], OLD_FLOOR))
check("at four tenths a wide shot lands on somebody answering",
      len(THEN["on_speech"]) >= 1,
      "%d of %d inserted wide shots sit on a thrown-away answer"
      % (len(THEN["on_speech"]), THEN["added"]))
check("at the floor the program uses none of them does",
      len(NOW["on_speech"]) == 0,
      "%d of %d inserted wide shots sit on a thrown-away answer, "
      "wanted 0" % (len(NOW["on_speech"]), NOW["added"]))

print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
