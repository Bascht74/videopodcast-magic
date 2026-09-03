# -*- coding: utf-8 -*-
"""A Timecode is counted from the axis, not from the reference's clock.

The reference is the longest camera, and the longest camera need not be
one that carries a timecode. Every other file that does says on its own
what the reference's first frame reads, and the median of those answers
hangs the whole axis on the clock -- the same rule the preview's axis
follows, so a point marked in the player and the point the run makes of
it are the same moment. "The reference" is the control, "another file"
and "the direction" the conversion, "several clocks" the choice between
them, "nobody set a point" the window the interface fills in by itself,
"nothing at all" the refusal, and "what counts as a clock" the
gathering underneath.
"""
import os
HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = os.environ.get("VPM_SCRIPT") or os.path.join(
    os.path.dirname(HERE), "videopodcast_magic.py")
import contextlib, importlib.util, io, shutil, subprocess, sys, tempfile, time
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


# The window the measurement hands over: the stretch every camera saw.
SHARED_FROM, SHARED_TO = 5.0, 120.0
# The reference camera. It is the longest one and it carries no clock,
# which is the whole case this test is about. The second shape of it is
# the same camera with a clock, for the control.
REF_NAME = "WideCam.mov"
REFERENCE = (REF_NAME, {"fps": 25.0, "duration": 120.0})
REFERENCE_WITH_CLOCK = (REF_NAME, {"fps": 25.0, "duration": 120.0,
                                   "tc": "10:00:00:00"})
# Two cameras that do carry one. Both read 10:00:00:00 at their own
# first frame and they sit on opposite sides of the reference: file
# time = a + b * axis time, so the Guest camera's own zero falls on
# axis second 5 -- it started five seconds after the reference -- and
# the CoPresenter's on axis second -8, eight seconds before it. Each
# therefore says something different about the reference's first frame:
# 09:59:55:00 and 10:00:08:00.
GUEST = {"name": "GuestCam.mov", "tc": 36000.0, "a": -5.0, "b": 1.0}
COPRESENTER = {"name": "CoPresenterCam.mov", "tc": 36000.0, "a": 8.0,
               "b": 1.0}
# A third camera that agrees with the Guest camera, and one whose clock
# was never set right: it reads a whole hour late.
PRESENTER = {"name": "PresenterCam.mov", "tc": 36000.0, "a": -5.0, "b": 1.0}
STRAY = {"name": "StrayCam.mov", "tc": 39600.0, "a": 0.0, "b": 1.0}
# Three moments on the clock. 10:00:00:00 is 36000 s, so these are
# 36010, 36020 and 36070 seconds past midnight.
IN_TC, LATER_TC, OUT_TC = "10:00:10:00", "10:00:20:00", "10:01:10:00"


class Call(object):
    """What a call says about the window: an In point and an Out point."""

    def __init__(self, first="", last=""):
        self.in_point = first
        self.out_point = last


def window(first, last, reference, clocks=()):
    """The window that call comes to, and everything it said on the way."""
    told = io.StringIO()
    with contextlib.redirect_stdout(told):
        got = vpm.clip_to_time_window(Call(first, last), SHARED_FROM,
                                      SHARED_TO, reference, clocks)
    return got, " ".join(told.getvalue().split())


def hangs_on(names, reads):
    """The line the run prints when the axis hangs on somebody else's clock."""
    return " ".join((vpm.T(
        '    The reference camera carries no Timecode. The axis hangs on '
        'the clock of %s, and its first frame reads %s.')
        % (names, reads)).split())


def refusal(value_text, name):
    """What the run says when nothing on the axis knows the time of day."""
    return " ".join((vpm.T(
        '%r is a Timecode, but the time axis hangs on no clock: no file '
        'here carries one, the reference camera %s included. Then only a '
        'value from the window start works, such as +12:30.')
        % (value_text, name)).split())


print("1. A clock on the reference camera is still the one taken")
got, said = window(IN_TC, OUT_TC, REFERENCE_WITH_CLOCK, [GUEST])
check("the reference camera's own clock beats every other",
      got == (10.0, 70.0), "%s, wanted (10.0, 70.0) -- %s" % (got, said[:80]))
check("and then nothing is said about hanging the axis on another clock",
      hangs_on(GUEST["name"], "09:59:55:00") not in said, said[:110])

print("\n2. Only another file carries one")
got, said = window(IN_TC, OUT_TC, REFERENCE, [GUEST])
check("a Timecode is counted from the axis the other clock hangs it on",
      got == (15.0, 75.0), "%s, wanted (15.0, 75.0) -- %s" % (got, said[:80]))
check("and the run names the clock and what it makes the first frame read",
      hangs_on(GUEST["name"], "09:59:55:00") in said, said[:130])

print("\n3. Which way the measured place points")
# The two cameras sit on opposite sides of the reference. A conversion
# that added the file's place instead of subtracting it would put the
# Guest camera's answer at 15.0 and the CoPresenter's at 28.0 -- one too
# early and one too late, so no single wrong constant gives both. The
# numbers come from a measured case: a camera built by cutting five
# seconds off the front of the reference's material was measured at
# a = -5.000, and measure_time_axis, which ties the preview's axis to
# the clock by its own road, put the reference's first frame at
# 09:59:55:00 -- the same second this arithmetic gives.
got, said = window(LATER_TC, OUT_TC, REFERENCE, [GUEST])
check("a camera that started after the reference lands 25 s in",
      got == (25.0, 75.0), "%s, wanted (25.0, 75.0) -- %s" % (got, said[:80]))
got, said = window(LATER_TC, OUT_TC, REFERENCE, [COPRESENTER])
check("and one that started before it lands 12 s in",
      got == (12.0, 62.0), "%s, wanted (12.0, 62.0) -- %s" % (got, said[:80]))

print("\n4. Several files carry a clock, and they disagree")
got, said = window(LATER_TC, OUT_TC, REFERENCE, [GUEST, COPRESENTER])
check("two clocks that disagree are settled at the middle answer",
      got == (12.0, 62.0), "%s, wanted (12.0, 62.0) -- %s" % (got, said[:80]))
check("and the run names both clocks it weighed",
      hangs_on("CoPresenterCam.mov, GuestCam.mov", "10:00:08:00") in said,
      said[:130])
got, said = window(LATER_TC, OUT_TC, REFERENCE, [GUEST, PRESENTER, STRAY])
check("one clock an hour out does not move the window",
      got == (25.0, 75.0), "%s, wanted (25.0, 75.0) -- %s" % (got, said[:80]))

print("\n5. The window the interface fills in when nobody set a point")
# Nobody marked anything: the interface puts the whole span of the
# material into the two fields as a Timecode and hands it to the run as
# though it had been typed. Under a reference without a clock that
# stopped the run before it started. 09:59:55:00 is the reference's own
# first frame and therefore axis second 0; the window keeps its own
# first frame instead.
got, said = window("09:59:55:00", "10:01:55:00", REFERENCE, [GUEST])
check("a window nobody set comes back as the measured window",
      got == (SHARED_FROM, SHARED_TO),
      "%s, wanted (%.1f, %.1f) -- %s"
      % (got, SHARED_FROM, SHARED_TO, said[:80]))

print("\n6. No file at all carries a clock")
got, said = window(IN_TC, OUT_TC, REFERENCE, [])
check("with no clock anywhere a Timecode is refused",
      got == (None, None), "%s, wanted (None, None) -- %s" % (got, said[:80]))
check("and the refusal says the axis hangs on no clock at all",
      refusal(IN_TC, REF_NAME) in said, said[:160])

print("\n7. What counts as a clock on the axis")
# The reference carries a clock here, so that only its being the
# reference keeps it out of the list. With a reference without one the
# check below would be held up by the missing clock and would pass
# however the gathering was written.
VIDEOS = [(REF_NAME, REFERENCE_WITH_CLOCK[1]),
          ("GuestCam.mov", {"fps": 25.0, "tc": "10:00:00:00"}),
          ("NoClockCam.mov", {"fps": 25.0}),
          ("NeverPlaced.mov", {"fps": 25.0, "tc": "10:00:00:00"})]
PLACES = {REF_NAME: (0.0, 1.0, {"points": 0}),
          "GuestCam.mov": (-5.0, 1.0, {"points": 30}),
          "NoClockCam.mov": (3.0, 1.0, {"points": 12})}
found = vpm.clocks_on_the_axis(VIDEOS, PLACES, [], REFERENCE_WITH_CLOCK)
names = [c["name"] for c in found]
check("a camera with a clock and a measured place is offered",
      "GuestCam.mov" in names,
      "got %s, wanted GuestCam.mov among them" % (names,))
check("a camera without a clock is not offered",
      "NoClockCam.mov" not in names,
      "got %s, wanted NoClockCam.mov left out" % (names,))
check("a camera the axis never placed is not offered either",
      "NeverPlaced.mov" not in names,
      "got %s, wanted NeverPlaced.mov left out" % (names,))
check("and the reference is not among them -- it is the axis itself",
      REF_NAME not in names, "got %s, wanted %s left out" % (names, REF_NAME))
guest = ([c for c in found if c["name"] == "GuestCam.mov"] or [{}])[0]
check("the place the file was measured at travels with its clock",
      (guest.get("a"), guest.get("b")) == (-5.0, 1.0),
      "a=%s b=%s, wanted a=-5.0 b=1.0" % (guest.get("a"), guest.get("b")))
check("and the clock itself arrives in seconds past midnight",
      guest.get("tc") == 36000.0, "%s, wanted 36000.0" % (guest.get("tc"),))

# A recorder writes its clock into the file rather than beside the
# pictures, and it is read off the first block of the recording.
FOLDER = tempfile.mkdtemp(prefix="vpm_clocks_")
WAV = os.path.join(FOLDER, "Guest_REC0001.wav")
made = ""
try:
    subprocess.run(["ffmpeg", "-v", "error", "-f", "lavfi",
                    "-i", "sine=frequency=440:duration=1",
                    "-ar", "48000", "-c:a", "pcm_s16le",
                    "-write_bext", "1",
                    "-metadata", "time_reference=%d" % (36000 * 48000),
                    WAV, "-y"], check=True)
except Exception as e:
    made = str(e)[:60]
# A precondition of the material, not a statement about the program:
# without the file the three checks under it would report the wrong
# thing.
check("the recording carrying a clock was built",
      not made and os.path.exists(WAV),
      made or "%s, %d bytes" % (os.path.basename(WAV),
                                os.path.getsize(WAV)
                                if os.path.exists(WAV) else 0))
TRACKS = [{"name": "Guest", "blocks": [WAV], "a": -5.0, "b": 1.0,
           "st": {"points": 21}}]
found = vpm.clocks_on_the_axis([(REF_NAME, REFERENCE[1])],
                               {REF_NAME: (0.0, 1.0, {"points": 0})},
                               TRACKS, REFERENCE)
names = [c["name"] for c in found]
check("a recording's own clock counts as well as a camera's",
      names == [os.path.basename(WAV)],
      "got %s, wanted [%r]" % (names, os.path.basename(WAV)))
check("and it is read off the file as 36000.0 s past midnight",
      bool(found) and found[0]["tc"] == 36000.0,
      "%s, wanted 36000.0" % (found[0]["tc"] if found else None,))
got, said = window(IN_TC, OUT_TC, REFERENCE, found)
check("a point counted through a recording lands where its clock says",
      got == (15.0, 75.0), "%s, wanted (15.0, 75.0) -- %s" % (got, said[:80]))
shutil.rmtree(FOLDER, ignore_errors=True)

print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
