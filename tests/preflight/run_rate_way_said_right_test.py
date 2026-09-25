# -*- coding: utf-8 -*-
"""A camera off its nominal rate is said to be off the way it really is.

The preflight tells a camera file that runs faster than its label from
one that runs slower, and both sentences hang on which way round it is:
more frames and shorter ones for the first, fewer and longer ones for
the second. Two made-up results stand in for the measurement, one a
little above the nominal rate and one as far below it, so what is
judged is the hint the program writes, not what a file would measure.
"""
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
import tempfile
import time
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


# An hour at 25 frames a second, and 36 frames more or fewer than that:
# 1.44 s off by the end, over the second the preflight lets pass.
NOMINAL = 25.0
HOUR = 3600.0
FASTER, SLOWER = 90036, 89964
# Never created: what the rest of the check reads off the disk is
# "nothing there".
WHERE = os.path.join(tempfile.mkdtemp(), "WideCam.mov")


def made_up(frames):
    """What inspect_frame_rate hands back, for a camera with `frames`."""
    return {"path": WHERE, "nominal": NOMINAL, "mean": frames / HOUR,
            "duration": HOUR, "videos": frames, "varies": False,
            "spread": 0.0, "offset_s": HOUR - frames / NOMINAL,
            "codec": "h264", "width": 1920, "height": 1080, "gaps": 0}


def hint_for(frames):
    """The one hint the preflight gives that camera, or None."""
    real = vpm.preflight.inspect_frame_rate
    vpm.preflight.inspect_frame_rate = lambda path: made_up(frames)
    try:
        found, _facts = vpm.preflight.check_camera_file(WHERE)
    except Exception as exc:                      # noqa: BLE001
        # Carried into the verdict, so the file still reaches its end.
        bad.append("the preflight read a made-up camera [%s: %s]"
                   % (type(exc).__name__, exc))
        return None
    finally:
        vpm.preflight.inspect_frame_rate = real
    hints = [f for f in found if f.kind == "hint"]
    return hints[0] if len(hints) == 1 else None


def fits(text, wording):
    """Whether `text` is `wording` with something in every %s."""
    pattern = "".join(".+?" if part == "%s" else re.escape(part)
                      for part in re.split(r"(%s)", wording))
    return re.fullmatch(pattern, text or "", re.S) is not None


MORE = vpm.T('%s fps, not the %s in the file -- %s more frames in '
             'the same length.')
FEWER = vpm.T('%s fps, not the %s in the file -- %s fewer frames in '
              'the same length.')
SHORTER = vpm.T('The frames stand a little shorter; the file is not any '
                'longer for it. Editing software leaves out about one '
                'frame every %s s, and picture and camera audio stay '
                'together.')
LONGER = vpm.T('The frames stand a little longer; the file is not any '
               'shorter for it. Editing software repeats about one '
               'frame every %s s, and picture and camera audio stay '
               'together.')

fast, slow = hint_for(FASTER), hint_for(SLOWER)
print("1. Both cameras are off by more than the preflight lets pass")
check("each of the two made-up cameras gets one hint",
      fast is not None and slow is not None,
      "a hint for the faster: %s, for the slower: %s -- %d and %d frames "
      "against %d an hour" % (fast is not None, slow is not None, FASTER,
                              SLOWER, int(NOMINAL * HOUR)))
fast_text, fast_why = (fast.text, fast.advice) if fast else ("", "")
slow_text, slow_why = (slow.text, slow.advice) if slow else ("", "")

print("\n2. Faster than the label")
check("a camera faster than its label is said to have more frames",
      fits(fast_text, MORE) and not fits(fast_text, FEWER),
      "%r for %d frames against %d" % (fast_text, FASTER,
                                       int(NOMINAL * HOUR)))
check("and its frames are said to stand shorter, some left out",
      fits(fast_why, SHORTER) and not fits(fast_why, LONGER),
      "%r" % fast_why[:70])

print("\n3. Slower than the label")
check("a camera slower than its label is said to have fewer frames",
      fits(slow_text, FEWER) and not fits(slow_text, MORE),
      "%r for %d frames against %d" % (slow_text, SLOWER,
                                       int(NOMINAL * HOUR)))
check("and its frames are said to stand longer, some repeated",
      fits(slow_why, LONGER) and not fits(slow_why, SHORTER),
      "%r" % slow_why[:70])

os.rmdir(os.path.dirname(WHERE))
print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
