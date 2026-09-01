"""The window shows its own length, and only content bounds an episode.

Three independent claims. The length counts from the In point to the
Out point and not from where the file starts; the older file-relative
arithmetic stands beside it to show how far the two differ. An intro,
an outro or an ignored file can carry no boundary, with a reason that
names the file, because a barred button without one reads as a fault;
an empty player bars nothing, and a file nobody has classified yet
counts as content. And where a Timecode is refused, the refusal names
the situation it is really in and says what does work instead, in the
language of the run: without a picture there is no reference camera to
name, and the message used to name one anyway."""
import os
HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = os.environ.get("VPM_SCRIPT") or os.path.join(
    os.path.dirname(HERE), "videopodcast-magic.py")
import contextlib
import io
import sys
import time
import importlib.util

began = time.time()
# No Qt here: the four functions this asks after live at module
# level, and building an application for them doubled the run.
spec = importlib.util.spec_from_file_location(
    "vpm", SCRIPT)
m = importlib.util.module_from_spec(spec); sys.modules["vpm"] = m
spec.loader.exec_module(m)

done = 0
bad = []


def check(name, ok, extra=""):
    global done
    done += 1
    print("  %-58s %s %s" % (name, "ok" if ok else "FAIL", extra))
    if not ok:
        bad.append("%s [%s]" % (name, extra or "no numbers"))


# Rebuild only the calculation, without the whole interface
def duration(in_point, out_point, fps=30.0):
    a, abs_a = m.parse_time_point(in_point, fps)
    b, abs_b = m.parse_time_point(out_point, fps)
    if a is None or b is None or abs_a != abs_b or b <= a:
        return ""
    return m.as_hms(b - a)


print("  the length runs from the In point to the Out point")
have = duration("17:02:16:17", "18:23:14:04")
check("two Timecodes give the stretch between them", have == "1:20:57.567",
      "17:02:16:17 to 18:23:14:04 wanted 1:20:57.567, got %s"
      % (have or "(empty)"))
have = duration("17:20:56:16", "18:17:06:15")
check("a second pair gives its own length, under the hour",
      have == "0:56:09.967",
      "17:20:56:16 to 18:17:06:15 wanted 0:56:09.967, got %s"
      % (have or "(empty)"))
have = duration("+0:00:10.000", "+0:01:10.000")
check("two points counted from the window start give their difference",
      have == "0:01:00.000",
      "+0:00:10.000 to +0:01:10.000 wanted 0:01:00.000, got %s"
      % (have or "(empty)"))
have = duration("", "18:00:00:00")
check("with no In point there is no length", have == "",
      "wanted an empty length, got %s" % (have or "(empty)"))
have = duration("18:00:00:00", "17:00:00:00")
check("an Out point before the In point gives no length", have == "",
      "18:00:00:00 to 17:00:00:00 wanted an empty length, got %s"
      % (have or "(empty)"))
# And the old way, which took the file as the yardstick:
tc0 = m.parse_timecode("17:06:35:20", 30.0)
old = (m.parse_timecode("18:23:14:04", 30.0) - tc0) - max(
    0.0, m.parse_timecode("17:02:16:17", 30.0) - tc0)
check("counting from the file start comes out shorter",
      m.as_hms(old) == "1:16:38.467",
      "wanted 1:16:38.467, got %s, against 1:20:57.567 from In to Out"
      % m.as_hms(old))
# ----------------------------------------------------------------------
# No boundary inside a jingle
#
# An intro is set in front of the material, not cut into it, so no point
# inside it can be a boundary of the episode.
print("\n  no boundary inside what is not on the axis")


def reason_for(name, kind):
    """Why the file in the player carries no boundary, or ""."""
    path = "/tmp/%s" % name
    return m.not_on_the_axis(path, {}, {"kind:" + path: kind})


said = reason_for("Interview_C002.mov", m.TYPE_CONTENT)
check("content is not barred from carrying a boundary", said == "",
      "wanted no reason, got %r" % said)
said = reason_for("WideCam_C003.mov", m.TYPE_WIDE)
check("the wide shot is not barred either", said == "",
      "wanted no reason, got %r" % said)
# A reason is as much part of this as the greying out: greyed out with
# nothing beside it reads as a fault in the program.
said = reason_for("Jingle.mp4", m.TYPE_INTRO)
check("an intro is barred, and the reason names the file",
      "Jingle.mp4" in said,
      "wanted a reason naming Jingle.mp4, got %r" % said)
said = reason_for("Abspann.mp4", m.TYPE_OUTRO)
check("an outro is barred, and the reason names the file",
      "Abspann.mp4" in said,
      "wanted a reason naming Abspann.mp4, got %r" % said)
said = reason_for("Fehlstart.mov", m.TYPE_IGNORED)
check("a file marked not to be used is barred too, and named",
      "Fehlstart.mov" in said,
      "wanted a reason naming Fehlstart.mov, got %r" % said)
# Nothing in the player bars nothing: the four buttons are then held by
# the axis alone, which is the older rule and still the one that counts.
said = m.not_on_the_axis(None, {}, {})
check("with no file in the player nothing is barred", said == "",
      "wanted no reason, got %r" % said)
said = m.not_on_the_axis("", {}, {})
check("and an empty path bars nothing either", said == "",
      "wanted no reason, got %r" % said)
# A file nobody has answered for counts as content, or opening a project
# would bar the buttons until every Kind has been looked at once.
said = m.not_on_the_axis("/tmp/unanswered.mov", {}, {})
check("a file nobody answered for counts as content", said == "",
      "wanted no reason, got %r" % said)

# ----------------------------------------------------------------------
# A Timecode that cannot be counted from
#
# Two situations, and one message for both named a reference camera on
# the path that has none: with no picture the file was printed as "?".


class Call(object):
    """The switches clip_to_time_window reads, and nothing else."""

    def __init__(self, in_point=None, out_point=None):
        self.in_point = in_point
        self.out_point = out_point


def refused(args, ref_clip):
    """What the run says when it will not take the point. One line."""
    out = io.StringIO()
    with contextlib.redirect_stdout(out):
        window = m.clip_to_time_window(args, 0.0, 600.0, ref_clip)
    return window, " ".join(out.getvalue().split())


print("\n  a Timecode where nothing can count it")
ABSOLUTE = Call(in_point="17:20:14")
window, said = refused(ABSOLUTE, None)
check("without a picture the point is refused", window == (None, None),
      str(window))
check("and no camera is named that is not there", "camera ?" not in said,
      said[:110])
check("the message says there is no picture", "no picture" in said,
      said[:110])
check("and it says what does work instead", "+12:30" in said, said[:110])

# The other direction: a camera that is there and carries no clock is
# still named, or nobody knows which file to look at.
window, said = refused(ABSOLUTE, ("/m/Camera1.mov", {"fps": 25.0}))
check("a camera without a timecode is refused too", window == (None, None),
      str(window))
check("and that message names the file", "Camera1.mov" in said, said[:110])

# A relative point needs no camera at all, so the same call goes through.
window, said = refused(Call(in_point="+00:10"), None)
check("a point counted from the window start goes through",
      window == (10.0, 600.0), str(window))
check("and the block that says so is translated",
      "In point" in said and said.count("In point") == 1, said[:110])
m.set_language("de")
_window, said = refused(Call(in_point="+00:10"), None)
m.set_language("en")
check("the German run says In-Punkt, not In point",
      "In-Punkt" in said and "In point" not in said, said[:110])

print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
