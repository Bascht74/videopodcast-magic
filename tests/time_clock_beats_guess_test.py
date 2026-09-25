# -*- coding: utf-8 -*-
"""A camera the sound cannot place and its clock can stands at its clock.

Cameras made here. Sections: two steady tones, the run and the preview
at the clock and saying why; a camera the sound places keeps its place;
a clockless reference, where a camera the sound placed lends its clock
and with none the camera is refused, run, preview and window alike;
two such tones, and a recording's clock, placing nothing the run
refuses, the window and the project file saying so; a failed
measurement, at its clock; a recording the cameras miss refusing
none; and the reference's clock first.
"""
import os
import the_program
import contextlib
import io
import re
import subprocess
import sys
import tempfile
import time

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


#------------------------------------------------------------- Material

HOME = tempfile.mkdtemp(prefix="vpm_clockwins_")
LENGTH = 2 * vpm.AXIS_MIN_WINDOW_S
# The guest rolls this much later in the room's time, frames and all.
LATE = 2.48
FRAME = 1.0 / 25
BURSTS = [(0.6, 1.3), (1.9, 2.1), (2.9, 3.2), (3.7, 8.9), (9.6, 10.0),
          (10.8, 11.9), (12.3, 12.45), (13.4, 14.3), (15.1, 15.35),
          (16.2, 17.8), (18.5, 18.65), (19.3, 20.3), (21.0, 21.4),
          (21.9, 22.2)]


def camera(name, hz, timecode, late=None):
    """A camera made with ffmpeg: a steady tone, or bursts heard from *late*.

    With no *timecode* the file carries none. A precondition of the
    material, not a judgement, hence the assert.
    """
    if late is None:
        sound = "sine=frequency=%d:duration=%g" % (hz, LENGTH)
    else:
        gate = "+".join("between(t+%g,%g,%g)" % (late, x, y)
                        for x, y in BURSTS)
        sound = ("aevalsrc='0.5*sin(2*PI*%d*t)*(%s)':s=48000:d=%g"
                 % (hz, gate, LENGTH))
    path = os.path.join(HOME, name)
    made = subprocess.run(
        ["ffmpeg", "-v", "error", "-f", "lavfi", "-i",
         "testsrc=size=160x90:rate=25:duration=%g" % LENGTH,
         "-f", "lavfi", "-i", sound, "-c:v", "libx264", "-preset",
         "ultrafast", "-pix_fmt", "yuv420p", "-c:a", "aac"]
        + (["-timecode", timecode] if timecode else [])
        + ["-shortest", path, "-y"],
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    assert made.returncode == 0 and os.path.exists(path), made.stdout
    return path


def aligned(paths):
    """align_cameras over *paths*: (reference, position, what it printed)."""
    said = io.StringIO()
    with contextlib.redirect_stdout(said):
        ref, position = vpm.align_cameras(
            [(p, vpm.video_facts(p)) for p in paths])
    # The mark in front of a warning is for the window, not for a line.
    plain = re.sub(re.escape(vpm.MARK) + "[a-z]", "", said.getvalue())
    return ref[0], position, re.sub(r"\x1b\[[0-9;]*m", "", plain)


def figure(value):
    """A number for a failure line, or the word for its absence."""
    return "none" if value is None else "%.3f" % value


# The guest first: of two cameras of one length the first is the
# reference, so the presenter's offset is the one measured.
GUEST = camera("GuestCam_C003.mov", 220, "18:55:06:12")
PRESENTER = camera("PresenterCam_C002.mov", 330, "18:55:04:00")

#------------------------------------------- 1. Steady tones, in the run

print("1. Steady tones: the sound has nothing to place them by")
ref, position, said = aligned([GUEST, PRESENTER])
# The guess of the curve, asked the run's own way, so a line can show
# how far the clock's place lies from it.
guess = vpm.align_envelopes(vpm.envelope_heard(GUEST),
                            vpm.envelope_heard(PRESENTER),
                            sample_points=20, distance_s=30.0, warn=False)
check("the steady tones match under the floor between two cameras",
      guess[2].get("quality", 1.0) < vpm.CAMERA_MATCH_ENOUGH,
      "quality %.3f against a floor of %.2f"
      % (guess[2].get("quality", 1.0), vpm.CAMERA_MATCH_ENOUGH))
a = position.get(PRESENTER, (None,))[0]
check("the camera stands at its clock's offset within a frame",
      ref == GUEST and a is not None and abs(a - LATE) <= FRAME,
      "reference %s, offset %s against the clock's %.2f, the curve's guess "
      "%.3f" % (os.path.basename(ref), figure(a), LATE, guess[0]))
st = position.get(PRESENTER, (0, 0, {}))[2]
check("and its verdict says the clock alone placed it",
      bool(st.get("by_clock_only")) and position[PRESENTER][1] == 1.0,
      "verdict %r, factor %r" % (sorted(k for k in st if st[k]),
                                 position.get(PRESENTER, (0, None))[1]))
line = re.escape(vpm.T('  %s: its sound matches by %s, under the floor of '
                       '%s -- placed by its clock alone')).replace(
    re.escape("%s"), "(.*?)")
why = re.search(line, said)
check("the log says the sound fell under its floor and the clock placed it",
      bool(why) and why.group(1) == os.path.basename(PRESENTER),
      "no such line in %r" % said if not why else "names %r" % why.group(1))

#----------------------------------------- 2. Steady tones, in the preview

print("\n2. The same two cameras in the preview's axis")
facts = dict((p, vpm.video_facts(p)) for p in (GUEST, PRESENTER))
data, text = vpm.measure_time_axis(
    [GUEST, PRESENTER], tc_of=lambda p: vpm.timecode_seconds(facts[p]))
axis = (data or {}).get("axis") or {}
kg, kp = vpm.path_key(GUEST), vpm.path_key(PRESENTER)
gap = axis[kg] - axis[kp] if kg in axis and kp in axis else None
check("the preview lays it at its clock too, 2.48 s before the guest",
      gap is not None and abs(gap - LATE) <= FRAME,
      "guest less presenter %s against %.2f -- %r"
      % (figure(gap), LATE, text))

#-------------------------------- 3. Bursts, and a clock that disagrees

print("\n3. Bursts the sound can place, and a clock set wrong")
# The clock says 5.00 s; the sound, heard from each camera's start, 2.48.
LIAR = camera("GuestCam_C005.mov", 220, "18:55:09:00", LATE)
HEARD = camera("PresenterCam_C004.mov", 330, "18:55:04:00", 0.0)
ref, position, said = aligned([LIAR, HEARD])
a, _b, st = position.get(HEARD, (None, None, {}))
check("a camera the sound places keeps the sound's offset, not its clock's",
      ref == LIAR and a is not None and abs(a - LATE) <= FRAME,
      "reference %s, offset %s against the sound's %.2f and the clock's "
      "5.00, quality %s" % (os.path.basename(ref), figure(a), LATE,
                            figure(st.get("quality"))))
check("and nothing says the clock placed it",
      not st.get("by_clock_only") and not re.search(line, said),
      "verdict %r, log %r" % (sorted(k for k in st if st[k] is True), said))

#------------------------------- 4. Three cameras, the reference clockless

print("\n4. A reference with no clock, and a camera the sound placed with one")
# The wide camera rolls a second after the presenter's, so the sound lays
# the presenter's at +1.00; the clocks put the guest's 2.48 s after it.
WIDE = camera("WideCam_C006.mov", 440, None, 1.0)
AFTER_WIDE = 1.0 - LATE
ref, position, said = aligned([WIDE, HEARD, GUEST])
a_heard = position.get(HEARD, (None,))[0]
a = position.get(GUEST, (None,))[0]
check("a camera with a steady tone stands at its clock set against one "
      "the sound placed",
      ref == WIDE and a is not None and abs(a - AFTER_WIDE) <= FRAME,
      "reference %s, offset %s against %.2f, the presenter's by sound %s, "
      "log %r" % (os.path.basename(ref), figure(a), AFTER_WIDE,
                  figure(a_heard), said))
st = position.get(GUEST, (0, 0, {}))[2]
why = re.search(line, said)
check("and verdict and log say its clock alone placed it",
      bool(st.get("by_clock_only")) and bool(why)
      and why.group(1) == os.path.basename(GUEST),
      "verdict %r, log %r" % (sorted(k for k in st if st[k]), said))
data, text = vpm.measure_time_axis(
    [WIDE, HEARD, GUEST],
    tc_of=lambda p: vpm.timecode_seconds(vpm.video_facts(p)))
axis = (data or {}).get("axis") or {}
kw, kg = vpm.path_key(WIDE), vpm.path_key(GUEST)
gap = axis[kg] - axis[kw] if kw in axis and kg in axis else None
check("the preview lays it there too, 1.48 s after the wide camera",
      gap is not None and abs(gap + AFTER_WIDE) <= FRAME,
      "guest less wide %s against %.2f -- %r"
      % (figure(gap), -AFTER_WIDE, text))
ref, position, said = aligned([WIDE, GUEST])
unset = vpm.no_base_message(os.path.basename(GUEST))
check("with no clock on a camera the sound placed, it is refused",
      ref == WIDE and GUEST not in position,
      "reference %s, on the axis %s"
      % (os.path.basename(ref), sorted(map(os.path.basename, position))))
no_clock = vpm.no_place_message(os.path.basename(GUEST))
check("and the refusal says that, not that it carries no timecode",
      unset in said and no_clock not in said, "log %r" % said)
# The window's proposal, from the preview's measurement of the same two.
data, _text = vpm.measure_time_axis(
    [WIDE, GUEST], tc_of=lambda p: vpm.timecode_seconds(vpm.video_facts(p)))
kinds = dict((p, vpm.Value(vpm.TYPE_CONTENT)) for p in (WIDE, GUEST))
shown = io.StringIO()
with contextlib.redirect_stdout(shown):
    vpm.kind_proposal_say(kinds, data)
check("the window gives the run's reason, not a missing timecode",
      unset in shown.getvalue() and no_clock not in shown.getvalue(),
      "guest set to %s, window %r" % (kinds[GUEST].get(), shown.getvalue()))

#------------------------ 5. Two steady tones beside a clockless reference

print("\n5. Two steady tones with clocks, and no clock the sound placed")
ref, position, said = aligned([WIDE, GUEST, PRESENTER])
tones = [os.path.basename(p) for p in (GUEST, PRESENTER)]
refused = sorted(os.path.basename(p) for p in (GUEST, PRESENTER)
                 if p not in position)
check("the run refuses both for want of a clock the sound placed",
      ref == WIDE and refused == tones
      and all(vpm.no_base_message(n) in said for n in tones),
      "reference %s, refused %s, log %r"
      % (os.path.basename(ref), refused, said))
data, text = vpm.measure_time_axis(
    [WIDE, GUEST, PRESENTER],
    tc_of=lambda p: vpm.timecode_seconds(vpm.video_facts(p)))
nowhere = sorted(map(os.path.basename, (data or {}).get("no_place") or ()))
alone = sorted(map(os.path.basename, (data or {}).get("clock_alone") or ()))
# path_key settles case and separator on Windows; the names follow suit.
laid = sorted(os.path.basename(k) for k in (data or {}).get("axis") or {})
check("the preview refuses the same two, marked as the run's reason",
      nowhere == tones and alone == tones
      and not set(map(os.path.normcase, tones)) & set(laid),
      "no place %s, clock alone %s, on the axis %s -- %r"
      % (nowhere, alone, laid, text))
# Picked by hand, so the proposal passes them by and the fact moves
# them: the first to the intro, the second out, the intro being taken.
kinds = dict((p, vpm.Value(vpm.TYPE_CONTENT))
             for p in (WIDE, GUEST, PRESENTER))
kinds[GUEST].chosen_by_hand = kinds[PRESENTER].chosen_by_hand = True
shown = io.StringIO()
with contextlib.redirect_stdout(shown):
    vpm.kind_proposal_say(kinds, data)
set_off = vpm.T('%s fits nothing in the material, and no camera the sound '
                'placed carries a timecode to set its own against, so it '
                'cannot be cut into the episode: set to Intro.') % tones[0]
check("set to Intro, it is told its clock has nothing to be set against",
      kinds[GUEST].get() == vpm.TYPE_INTRO and set_off in shown.getvalue(),
      "guest set to %s, window %r" % (kinds[GUEST].get(), shown.getvalue()))
left = vpm.T('%s fits nothing in the material, and no camera the sound '
             'placed carries a timecode to set its own against; the intro '
             'is taken: left out.') % tones[1]
check("left out behind it, the second is told the same",
      kinds[PRESENTER].get() == vpm.TYPE_IGNORED
      and left in shown.getvalue(),
      "presenter set to %s, window %r"
      % (kinds[PRESENTER].get(), shown.getvalue()))

#------------------------- 6. A recording's clock beside the same reference

print("\n6. A recorder with a clock beside a reference without one")
RECORDER = os.path.join(HOME, "Room_REC0001.wav")
made = subprocess.run(
    ["ffmpeg", "-v", "error", "-i", WIDE, "-vn", "-c:a", "pcm_s16le",
     "-write_bext", "1", "-metadata", "time_reference=%d"
     % int(vpm.parse_timecode("18:55:00:00", 25.0) * 48000),
     RECORDER, "-y"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
# A precondition of the material, not a judgement, hence the assert.
assert made.returncode == 0 and os.path.exists(RECORDER), made.stdout
data, text = vpm.measure_time_axis([RECORDER, WIDE, GUEST],
                                   tc_of=lambda p: vpm.file_timecode(p))
axis = (data or {}).get("axis") or {}
nowhere = [os.path.basename(p) for p in (data or {}).get("no_place") or ()]
check("a recording's clock places no camera the run refuses",
      vpm.path_key(GUEST) not in axis and nowhere == tones[:1]
      and vpm.path_key(RECORDER) in axis and bool(data.get("absolute")),
      "guest at %s, no place %s, the recorder at %s, tied %s -- %r"
      % (axis.get(vpm.path_key(GUEST)), nowhere,
         axis.get(vpm.path_key(RECORDER)), data.get("absolute"), text))
# Through the project file: a reopened project gives the same reason.
marks = dict((k, list((data or {}).get(k) or []))
             for k in ("weak", "no_place", "brief", "clock_alone"))
entries = vpm.timeline_entries(axis, (data or {}).get("clock") or {}, marks)
back = vpm.axis_still_valid({"timeline": entries}, [RECORDER, WIDE, GUEST])
kept = sorted(map(os.path.basename, (back or {}).get("clock_alone") or ()))
check("the project file keeps that its clock has nothing to be set against",
      kept == tones[:1],
      "came back %s, wanted %s; stored off the axis %r"
      % (kept, tones[:1], [(os.path.basename(e["path"]), e.get("fit"),
                            e.get("clock_alone"))
                           for e in entries if "start_s" not in e]))

#--------------------------------------------- 7. A measurement that fails

print("\n7. A camera whose measurement fails outright")
# A stand-in: a curve the run reads has ten values at least, so what
# fails here is the arithmetic, and no file can be made to cause that.
real = vpm.align_envelopes


def refusing(env_a, env_b, *args, **named):
    """The real alignment, failing for the presenter's camera."""
    if named.get("warn") == os.path.basename(HEARD):
        raise RuntimeError(vpm.T('too little audio to align'))
    return real(env_a, env_b, *args, **named)


vpm.align_envelopes = refusing
try:
    ref, position, said = aligned([LIAR, HEARD])
    data, text = vpm.measure_time_axis(
        [LIAR, HEARD], tc_of=lambda p: vpm.timecode_seconds(
            vpm.video_facts(p)))
finally:
    vpm.align_envelopes = real
a, _b, st = position.get(HEARD, (None, None, {}))
told = vpm.T('  %s cannot be classified: %s -- placed by its clock '
             'alone') % (os.path.basename(HEARD),
                         vpm.T('too little audio to align'))
check("a camera whose measurement fails stands at its clock, 5.00 s in",
      ref == LIAR and a is not None and abs(a - 5.0) <= FRAME
      and bool(st.get("by_clock_only")) and told in said,
      "reference %s, offset %s against the clock's 5.00, verdict %r, "
      "log %r" % (os.path.basename(ref), figure(a),
                  sorted(k for k in st if st[k]), said))
axis = (data or {}).get("axis") or {}
kl, kh = vpm.path_key(LIAR), vpm.path_key(HEARD)
gap = axis[kh] - axis[kl] if kl in axis and kh in axis else None
check("the preview lays the unmeasured one 5.00 s in as well",
      gap is not None and abs(gap + 5.0) <= FRAME,
      "presenter less guest %s against -5.00 -- %r" % (figure(gap), text))

#------------------------ 8. A sound recording the cameras do not fit

print("\n8. Two cameras the sound places, beside a recording they miss")
FOREIGN = os.path.join(HOME, "Music_long.wav")
# Seeded: anoisesrc draws a new seed every run, and which camera then
# lands under the floor against the noise changed with it.
made = subprocess.run(
    ["ffmpeg", "-v", "error", "-f", "lavfi", "-i",
     "anoisesrc=d=%g:c=pink:a=0.3:seed=8808" % (LENGTH * 1.5),
     "-ar", "48000",
     "-c:a", "pcm_s16le", FOREIGN, "-y"],
    stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
# A precondition of the material, not a judgement, hence the assert.
assert made.returncode == 0 and os.path.exists(FOREIGN), made.stdout
data, text = vpm.measure_time_axis([FOREIGN, LIAR, HEARD],
                                   tc_of=lambda p: vpm.file_timecode(p))
kinds = dict((p, vpm.Value(vpm.TYPE_CONTENT)) for p in (LIAR, HEARD))
shown = io.StringIO()
with contextlib.redirect_stdout(shown):
    vpm.kind_proposal_say(kinds, data)
nowhere = sorted(map(os.path.basename, (data or {}).get("no_place") or ()))
weak = sorted(map(os.path.basename, (data or {}).get("weak") or ()))
check("the preview refuses no camera the run places by sound",
      nowhere == [] and all(v.get() == vpm.TYPE_CONTENT
                            for v in kinds.values()),
      "weak %s, no place %s, kinds %s -- %r, window %r"
      % (weak, nowhere, sorted((os.path.basename(p), v.get())
                               for p, v in kinds.items()),
         text, shown.getvalue()))

#------------------------------- 9. Two clocks the sound placed, in order

print("\n9. The reference's clock before a later camera's, which is wrong")
# The liar's clock is 2.52 s off what the sound says; set against it,
# the guest would stand 0.04 s after the presenter, not 2.48 s before.
ref, position, said = aligned([HEARD, LIAR, GUEST])
a = position.get(GUEST, (None,))[0]
check("the run sets the camera against the reference's clock first",
      ref == HEARD and a is not None and abs(a + LATE) <= FRAME,
      "reference %s, offset %s against %.2f, the liar's by sound %s"
      % (os.path.basename(ref), figure(a), -LATE,
         figure(position.get(LIAR, (None,))[0])))
data, text = vpm.measure_time_axis(
    [HEARD, LIAR, GUEST],
    tc_of=lambda p: vpm.timecode_seconds(vpm.video_facts(p)))
axis = (data or {}).get("axis") or {}
kh, kg = vpm.path_key(HEARD), vpm.path_key(GUEST)
gap = axis[kg] - axis[kh] if kh in axis and kg in axis else None
check("and so does the preview, 2.48 s after the presenter",
      gap is not None and abs(gap - LATE) <= FRAME,
      "guest less presenter %s against %.2f -- %r"
      % (figure(gap), LATE, text))

print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
