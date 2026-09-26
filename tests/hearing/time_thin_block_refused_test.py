# -*- coding: utf-8 -*-
"""A recording block too thin to place is refused, never laid out wrong.

The interview fixture's cameras hear the room, so its recordings are
placed by sound. A block of forty seconds holding one turn finds a place
nearly as good elsewhere, and a point or two agree with any of them. In
order: the rule on its own numbers; the run's way on thin blocks and on
a whole recording; the preview over the window's own set of files; and
the thin block as the head of its recording, placed by the whole.
"""
PLATFORM_BOUND = True
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
import time

from fixture_root import fixture

vpm = the_program.load()
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


F = fixture("interview")
WIDE = os.path.join(F, "WideCam_01011855_C001.mov")
HOSTS = os.path.join(F, "PresentersCam_01011855_C002.mov")
GUESTS = os.path.join(F, "GuestCam_01011858_C003.mov")
# One turn of its speaker in forty seconds, from second 0 of the
# programme; the third block, one turn from second 80.
THIN = os.path.join(F, "Presenter_REC00021.wav")
THIN_LATE = os.path.join(F, "Presenter_REC00023.wav")
# The whole programme, seven turns, from second 0.
WHOLE = os.path.join(F, "Guest_Take0021A_Timecode.wav")
# The wide shot rolls first: picture time is programme time on it.
FRAME = 0.04


def name_of(path):
    return os.path.basename(path)


# ------------------------------------------------------------ the rule
print("the rule on its own numbers")
enough = vpm.RECORDING_POINTS_ENOUGH
few = {"quality": 0.3, "next_best": 0.29, "points": enough - 1,
       "spread_ms": 0.0, "ppm": 0.0}
check("too few points under a match that does not stand out refuse it",
      vpm.sound_places_recording(few) is False,
      "%r from %d points, q %.2f against next %.2f, wanted False"
      % (vpm.sound_places_recording(few), few["points"], few["quality"],
         few["next_best"]))
borne = dict(few, points=enough)
check("as many as the floor asks for, on one line, place it",
      vpm.sound_places_recording(borne) is True,
      "%r from %d points, the floor %d, wanted True"
      % (vpm.sound_places_recording(borne), borne["points"], enough))
clear = {"quality": 0.8, "next_best": 0.05, "points": 1}
check("a match that stands clear places it on a single point",
      vpm.sound_places_recording(clear) is True,
      "%r from %d point, q %.2f against next %.2f, wanted True"
      % (vpm.sound_places_recording(clear), clear["points"],
         clear["quality"], clear["next_best"]))

# --------------------------------------------------------- the run's way
print("\nthe run's way")


def run_way(recording, camera):
    """As the run measures a recording: twenty points, 30 s apart.

    Where it lands, as the recording's second at the camera's first,
    whether it was refused, and how many points it rested on.
    """
    a, _b, st = vpm.align_audio_to_video(recording, camera, sample_points=20,
                                         distance_s=30.0, phase=False)
    print("   %-26s at %+8.3f s, match %.3f, next %.3f, %d points"
          % (name_of(recording), a, st.get("quality", 0.0),
             st.get("next_best", 0.0), st.get("points", 0)))
    return a, bool(st.get("unplaceable")), st.get("points", 0), st


# Against the camera that rolls four seconds late, the first block's
# second 4 is that camera's first; against the wide shot, the last
# block's second 0 is the wide shot's second 80. Before the rule both
# were laid out on one or two points, 96 and 15 s wrong.
a, refused, n, _st = run_way(THIN, HOSTS)
check("a block of one turn is refused, not laid out wrong",
      refused or abs(a - 4.0) <= FRAME,
      "%s at %+.3f s against +4.000, refused %r, %d points"
      % (name_of(THIN), a, refused, n))
a, refused, n, _st = run_way(THIN_LATE, WIDE)
check("and so is the last block, one turn from second 80",
      refused or abs(a + 80.0) <= FRAME,
      "%s at %+.3f s against -80.000, refused %r, %d points"
      % (name_of(THIN_LATE), a, refused, n))
# By its curve, not by the second try: that one would catch a whole
# recording the rule lost, and hide the loss.
a, refused, n, st = run_way(WHOLE, WIDE)
check("a whole recording is still placed by its curve, within a frame",
      not refused and not st.get("from_bands") and abs(a) <= FRAME,
      "%s at %+.3f s against 0, refused %r, by the bands %r, %d points"
      % (name_of(WHOLE), a, refused, bool(st.get("from_bands")), n))

# ------------------------------------------------------------ the preview
print("\nthe preview, over the files window_marks_take_spot opens")
PLAIN = os.path.join(F, "CoPresenter_REC00018.wav")
WINDOW = [THIN, PLAIN, WIDE, HOSTS, GUESTS]


def clock(p):
    try:
        return vpm.file_timecode(p, 25.0)
    except Exception:
        return None


def preview(paths):
    """Where the preview lays each file, by name; the phase way off,
    as in a window where nobody said the sound was mixed."""
    data, _text = vpm.measure_time_axis(paths, clock,
                                        phase_of=lambda p: False)
    axis = data.get("axis") or {}
    at = dict((name_of(p), axis.get(vpm.path_key(p))) for p in paths)
    print("   " + ", ".join("%s %s" % (n, "-" if t is None
                                       else "%.3f" % (t - start))
                             for n, t in sorted(at.items())))
    return at


start = clock(WIDE)
thin_at = preview(WINDOW)[name_of(THIN)]
check("the preview does not lay the thin block out wrong either",
      thin_at is None or abs(thin_at - start) <= FRAME,
      "%s at %s against %.3f, the wide shot's clock"
      % (name_of(THIN), thin_at, start))

# ------------------------------------------------- the head of the blocks
print("\nthe thin block heading the recording it belongs to")
ROW = [THIN, os.path.join(F, "Presenter_REC00022.wav"), THIN_LATE]
# The late camera first, so the joined curve is held against it and
# a place read the wrong way round shows.
data, _text = vpm.axis_with_blocks(ROW + [HOSTS, WIDE, GUESTS], clock,
                                   blocks={THIN: ROW},
                                   phase_of=lambda p: False)
laid = [(data.get("axis") or {}).get(vpm.path_key(p)) for p in ROW]
wanted = [start, start + 40.0, start + 80.0]
check("the preview places the blocks as one, where the run does",
      all(t is not None and abs(t - w) <= FRAME
          for t, w in zip(laid, wanted)),
      "at %s against %s" % (["-" if t is None else "%.3f" % (t - start)
                             for t in laid], ["0.000", "40.000", "80.000"]))

print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
