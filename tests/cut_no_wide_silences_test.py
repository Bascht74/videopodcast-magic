# -*- coding: utf-8 -*-
"""Without a wide shot the settings that steer it are silenced in the cut.

Every camera carrying a speaker and none marked means there is no wide
shot, and then the interval, the tick for the edges and a rule standing
on the wide shot are replaced before a shot is laid out. In order: which
cameras count as the wide shot and what the run says, each replacement
read off the finished cut, and the same readings with a free camera
there, where none may happen. The cut comes out of the run itself. The
"Long monologue" rule is replaced too but cannot be read here: with the
interval at zero, nothing asks it.
"""
import contextlib
import importlib.util
import io
import os
import shutil
import sys
import tempfile
import time

HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = os.environ.get("VPM_SCRIPT") or os.path.join(
    os.path.dirname(HERE), "videopodcast_magic.py")
spec = importlib.util.spec_from_file_location("vpm", SCRIPT)
vpm = importlib.util.module_from_spec(spec); sys.modules["vpm"] = vpm
spec.loader.exec_module(vpm)
vpm.set_language("en")

began = time.time()
done = 0
bad = []


def check(name, ok, extra=""):
    global done
    done += 1
    print("  %-58s %s %s" % (name, "ok" if ok else "FAIL", extra))
    if not ok:
        bad.append("%s [%s]" % (name, extra or "no numbers"))


# Six cameras to draw on. Nothing is read out of them -- the cut works
# on the speaker blocks below -- but the run turns every camera into an
# absolute path and compares it with the marks, so the files exist.
W = tempfile.mkdtemp(prefix="vpmnowide_")
PATH = {}
for _name in ("CamA", "CamB", "CamC", "CamD", "CamW", "CamX"):
    PATH[_name] = os.path.join(W, _name + ".mov")
    with open(PATH[_name], "w") as _f:
        _f.write("x")

LENGTH = 300.0
# Dirk is on CamA and says one thing all evening. Where there is no wide
# shot the cut falls back on a stand-in, and that stand-in is the first
# camera by name -- so somebody has to sit in front of CamA, and nobody
# whose picture is asked after below may sit there, or holding the
# picture and going to the stand-in would look alike.
ON = {"Anna": "CamB", "Bert": "CamC", "Cleo": "CamD", "Dirk": "CamA"}
# Anna holds the floor from 60 to 160 with only breaths in it: a hundred
# seconds against a wide shot interval of forty. Bert opens the round at
# 30 and Cleo closes it at 250, which is what the edge rule needs. From
# 170 to 180 Bert and Cleo speak at once and no camera shows those two,
# so the "Several speak at once" rule decides -- and the shot before it
# is Bert's.
SPEECH = [("Anna", [(0.0, 25.0), (60.0, 90.0), (92.0, 120.0),
                    (122.0, 160.0), (200.0, 240.0)]),
          ("Bert", [(30.0, 40.0), (160.0, 170.0), (170.0, 180.0)]),
          ("Cleo", [(170.0, 190.0), (250.0, 260.0)]),
          ("Dirk", [(190.0, 198.0)])]
# The same four, with seven changes of camera between 200 and 206: that
# is what the program calls a frayed recognition, and there the
# "Recognition uncertain" rule decides. Bert has the floor up to 200, so
# holding shows his camera and the stand-in would show Dirk's.
FRAY = [("Anna", [(0.0, 60.0), (200.0, 201.0), (202.0, 203.0),
                  (204.0, 205.0), (260.0, 300.0)]),
        ("Bert", [(100.0, 160.0), (190.0, 200.0), (201.0, 202.0),
                  (203.0, 204.0), (205.0, 206.0)]),
        ("Cleo", [(206.0, 207.0), (220.0, 250.0)]),
        ("Dirk", [(70.0, 78.0)])]
# One word a second, every fifth ending a sentence. Without a transcript
# the interval finds no boundary to put the wide shot on, and then a
# monologue stands unbroken whether there is a wide shot or not.
WORDS = [vpm.speech_word(t, t + 0.8, "wort" + ("." if t % 5 == 4 else ""))
         for t in range(int(LENGTH))]
# What the four wide shot settings are set to for every run below.
CALL = ["--wide-after", "40", "--wide-latest", "120",
        "--wide-length", "5", "--wide-most", "15"]
NO_WIDE = vpm.T('  Every camera carries a speaker, so there is no wide '
                'shot: the four wide shot settings and the tick for the '
                'edges do nothing here.')
COUNTED = vpm.T('  %d wide shots: the cut uses %s.')
AT_EDGES = vpm.T('  Wide shot at the edges: until %s and from %s') \
    % (vpm.as_hms(40.0), vpm.as_hms(250.0))


def a_run(cameras, speech=SPEECH, marked=()):
    """Build the cut the way a run builds it. Returns (cut, log).

    Through write_cut_list, which is where the switch sits: the point is
    what came out of the caller, not what the function it calls returns.
    """
    call = list(CALL)
    for one in marked:
        call += ["--wide-shot", PATH[one]]
    args = vpm.build_argument_parser().parse_args(call)
    # The one field the parser has no switch for; the run fills it in
    # from the folder name before it gets here.
    args.production = "Nowide"
    folder = tempfile.mkdtemp(prefix="out_", dir=W)
    written = io.StringIO()
    with contextlib.redirect_stdout(written):
        cut, _segments = vpm.write_cut_list(
            args, speech,
            [{"name": who, "camera": PATH[cam]} for who, cam in ON.items()],
            [{"video": PATH[n], "name": n} for n in cameras],
            [(PATH[n], {"width": 1280, "height": 720, "fps": 25.0,
                        "duration": LENGTH, "tc": "10:00:00:00"})
             for n in cameras],
            folder, 0.0,
            (PATH[cameras[0]], {"fps": 25.0, "tc": "10:00:00:00"}),
            LENGTH, words=WORDS, sound_source="")
    return [tuple(x) for x in cut], written.getvalue()


def shown_at(cut, when):
    """Which camera the cut shows at that second."""
    for a, b, who in cut:
        if a <= when < b:
            return who
    return "nothing"


def longest_on(cut, who):
    """The longest single shot that camera holds."""
    return max([b - a for a, b, name in cut if name == who] or [0.0])


def cameras_of(cut):
    """Every camera the cut uses, once each."""
    return sorted(set(name for _a, _b, name in cut))


FOUR = ("CamA", "CamB", "CamC", "CamD")
none_cut, none_log = a_run(FOUR)
wide_cut, wide_log = a_run(FOUR + ("CamW",))

print("1. WHICH CAMERAS COUNT AS THE WIDE SHOT")
check("the material gives a cut with and without a free camera",
      len(none_cut) > 0 and len(wide_cut) > 0,
      "%d shots with every camera taken, %d with one free"
      % (len(none_cut), len(wide_cut)))
check("with every camera carrying a speaker the run says there is none",
      none_log.count(NO_WIDE) == 1,
      "the sentence stands %d times in the log, wanted 1"
      % none_log.count(NO_WIDE))
check("a camera nobody is assigned to ends that state",
      wide_log.count(NO_WIDE) == 0,
      "the sentence stands %d times in the log, wanted 0"
      % wide_log.count(NO_WIDE))
check("and it is the camera the cut falls back on",
      "CamW" in cameras_of(wide_cut),
      "the cut uses %s, wanted CamW among them" % (cameras_of(wide_cut),))

# A mark beats the derivation: Cleo sits in front of CamD and it is the
# wide shot all the same, which no camera with a speaker on it would
# otherwise be.
marked_cut, marked_log = a_run(FOUR, marked=("CamD",))
check("a mark makes a camera the wide shot although a speaker sits on it",
      marked_log.count(NO_WIDE) == 0,
      "the sentence stands %d times in the log, wanted 0"
      % marked_log.count(NO_WIDE))
check("and the cut then holds the opening on the marked camera",
      shown_at(marked_cut, 35.0) == "CamD",
      "at 35.0 s the cut shows %s, wanted CamD -- the stand-in would be "
      "CamA and the speaker's own camera CamC"
      % shown_at(marked_cut, 35.0))

two_cut, two_log = a_run(FOUR + ("CamW", "CamX"))
back_cut, back_log = a_run(FOUR + ("CamX", "CamW"))
check("two free cameras are counted, and the one used is named",
      two_log.count(COUNTED % (2, "CamW")) == 1,
      "%r stands %d times in the log, wanted 1"
      % (COUNTED % (2, "CamW"), two_log.count(COUNTED % (2, "CamW"))))
check("with a single wide shot nothing is counted out loud",
      wide_log.count(COUNTED % (1, "CamW")) == 0,
      "%r stands %d times in the log, wanted 0"
      % (COUNTED % (1, "CamW"), wide_log.count(COUNTED % (1, "CamW"))))
check("of two the cut takes the first and shows the other nowhere",
      "CamW" in cameras_of(two_cut) and "CamX" not in cameras_of(two_cut),
      "the cut uses %s, wanted CamW among them and no CamX"
      % (cameras_of(two_cut),))
check("listed the other way round it takes the other one",
      "CamX" in cameras_of(back_cut) and "CamW" not in cameras_of(back_cut),
      "the cut uses %s, wanted CamX among them and no CamW"
      % (cameras_of(back_cut),))

print("\n2. WITH NONE OF THEM, NOTHING THE SETTINGS ASK FOR HAPPENS")
check("a shot runs past the wide shot interval unbroken",
      longest_on(none_cut, "CamB") > 80.0,
      "longest shot on CamB %.2f s against an interval of 40 s, wanted "
      "more than 80" % longest_on(none_cut, "CamB"))
check("the opening stays with the speaker, not with a stand-in",
      shown_at(none_cut, 35.0) == "CamC",
      "at 35.0 s the cut shows %s, wanted CamC -- Bert is heard there and "
      "the stand-in would be CamA" % shown_at(none_cut, 35.0))
check("and the run announces no wide shot at the edges",
      none_log.count(AT_EDGES) == 0,
      "%r stands %d times in the log, wanted 0"
      % (AT_EDGES, none_log.count(AT_EDGES)))
check("two speaking at once hold the picture where it was",
      shown_at(none_cut, 175.0) == "CamC",
      "at 175.0 s the cut shows %s, wanted CamC -- Bert had the shot "
      "before it and the stand-in would be CamA"
      % shown_at(none_cut, 175.0))

fray_none_cut, _fray_none_log = a_run(FOUR, FRAY)
fray_wide_cut, _fray_wide_log = a_run(FOUR + ("CamW",), FRAY)
check("the fraying stretch is one the cut calls uncertain",
      vpm.unrest_spans(FRAY, ON) == [(200.0, 206.0)],
      "the cut calls %s uncertain, wanted [(200.0, 206.0)]"
      % (vpm.unrest_spans(FRAY, ON),))
check("a frayed stretch holds the picture where it was",
      shown_at(fray_none_cut, 203.0) == "CamC",
      "at 203.0 s the cut shows %s, wanted CamC -- Bert had the floor "
      "until 200.0 and the stand-in would be CamA"
      % shown_at(fray_none_cut, 203.0))

print("\n3. WITH ONE OF THEM, ALL OF IT HAPPENS AGAIN")
check("with a wide shot the same long shot is broken up",
      longest_on(wide_cut, "CamB") <= 40.0 + 1e-6,
      "longest shot on CamB %.2f s against an interval of 40 s, wanted no "
      "more" % longest_on(wide_cut, "CamB"))
check("with a wide shot the opening is held on it",
      shown_at(wide_cut, 35.0) == "CamW",
      "at 35.0 s the cut shows %s, wanted CamW" % shown_at(wide_cut, 35.0))
check("and the run announces the edges it held",
      wide_log.count(AT_EDGES) == 1,
      "%r stands %d times in the log, wanted 1"
      % (AT_EDGES, wide_log.count(AT_EDGES)))
check("with a wide shot two speaking at once go to it",
      shown_at(wide_cut, 175.0) == "CamW",
      "at 175.0 s the cut shows %s, wanted CamW" % shown_at(wide_cut, 175.0))
check("with a wide shot a frayed stretch goes to it",
      shown_at(fray_wide_cut, 203.0) == "CamW",
      "at 203.0 s the cut shows %s, wanted CamW"
      % shown_at(fray_wide_cut, 203.0))

shutil.rmtree(W, ignore_errors=True)
print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
