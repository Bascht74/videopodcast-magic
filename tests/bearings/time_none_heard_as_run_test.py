# -*- coding: utf-8 -*-
"""With no camera heard, the window lays every file where the run does.

The recordings are laid against each other as without a picture, and a
camera no sound reaches stands at its timecode against the recordings
the sound placed. Sections: a camera with no sound and a clock beside
recordings with clocks, the run's side read off its own function, and
one the run placed at a match no material here reaches, kept; that
camera with no clock, and with no recording's clock to set it against;
no picture, the longest starting after another, a short one fitting
nothing and a lone clock; and a dry run over the files of the first.
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
import contextlib
import io
import re
import shutil
import subprocess
import tempfile
import time
import types
import wave
import numpy as np

SCRIPT = the_program.SCRIPT
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

RATE = 48000
# A tenth of a millisecond: the run's own numbers, not a frame apart.
SAME = 0.0001
# The clocks: the presenter's recorder at ten o'clock, the camera ten
# seconds later, the guest's at thirty and the hiss at twenty.
AT = 36000.0
CAM_AFTER, GUEST_AFTER, HISS_AFTER = 10.0, 30.0, 20.0
WORK = tempfile.mkdtemp(prefix="vpm_noneheard_")


def turns(seconds, seed):
    """Speech-like turns: noise in irregular pieces with pauses between."""
    rng = np.random.default_rng(seed)
    x = np.zeros(int(seconds * RATE))
    t = 0.2
    while t < seconds - 1.0:
        long_s = float(rng.uniform(0.25, 0.9))
        k, i0 = int(long_s * RATE), int(t * RATE)
        x[i0:i0 + k] = rng.normal(0, 0.25, k) * np.hanning(k)
        t += long_s + float(rng.uniform(0.2, 1.1))
    return x


def write(name, x, clock=None):
    """A WAV of *x*, its bext saying *clock* seconds where one is given."""
    path = os.path.join(WORK, name)
    raw = (np.clip(x, -1, 1) * 32000).astype("<i2").tobytes()
    if clock is None:
        with wave.open(path, "wb") as f:
            f.setnchannels(1)
            f.setsampwidth(2)
            f.setframerate(RATE)
            f.writeframes(raw)
        return path
    subprocess.run(["ffmpeg", "-v", "error", "-f", "s16le", "-ar",
                    str(RATE), "-ac", "1", "-i", "pipe:0", "-c:a",
                    "pcm_s16le", "-write_bext", "1", "-metadata",
                    "time_reference=%d" % int(clock * RATE), "-y", path],
                   input=raw, check=True)
    return path


def camera(name, clock=None):
    """Two minutes of colour bars and no sound track, a timecode or none."""
    path = os.path.join(WORK, name)
    stamp = (["-timecode", "10:00:%02d:00" % int(clock - AT)]
             if clock is not None else [])
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i",
                    "smptebars=size=160x90:rate=25:duration=120", "-an",
                    "-t", "120"] + stamp + [
                        "-c:v", "libx264", "-preset", "ultrafast",
                        "-pix_fmt", "yuv420p", path], check=True)
    return path


room = turns(130, 1)
hiss = np.random.default_rng(5).normal(0, 0.001, 60 * RATE)
guest = (0.5 * room[int(GUEST_AFTER * RATE):int((GUEST_AFTER + 80) * RATE)]
         + np.random.default_rng(13).normal(0, 0.002, 80 * RATE))
PRES = write("Presenter_REC00001.wav", room, AT)
GUEST = write("Guest_REC00001.wav", guest, AT + GUEST_AFTER)
HISS = write("Hiss_REC00001.wav", hiss, AT + HISS_AFTER)
CAM = camera("WideCam_C001.mov", AT + CAM_AFTER)
CAM_BARE = camera("WideCam_C002.mov")
PRES_BARE = write("Presenter_REC00002.wav", room)
GUEST_BARE = write("Guest_REC00002.wav", guest)
# Ten seconds of other talk before the room's first: it starts before
# the longest. And four seconds of hiss, far shorter than the rest.
EARLY = write("CoPresenter_REC00001.wav", np.concatenate(
    [turns(10, 77), room[:70 * RATE]]))
SHORT = write("Sting_REC00001.wav", hiss[:4 * RATE])
# A precondition of the material, not a judgement: no sound track.
for p in (CAM, CAM_BARE):
    assert not vpm.video_facts(p)["audio"], p


def clock(p):
    """A file's own clock, as the window asks it."""
    try:
        return vpm.file_timecode(p, 25.0)
    except Exception:
        return None


def name_of(p):
    return os.path.basename(p)


def named(data, key):
    return sorted(name_of(p) for p in (data or {}).get(key) or ())


def figure(value):
    return "none" if value is None else "%+.4f" % value


def run_side(videos, recordings):
    """Where the run lays every file when no camera is heard.

    recordings_carry_cameras, the function build_common_timebase hands
    such material to, and each track as speakers_for_the_cut reads it:
    {path: start from the run's reference}, that reference, and what
    the run said -- or None for the places where it found none.
    """
    args = types.SimpleNamespace(project_type="sync", sound=None,
                                 sound_of=None)
    said = io.StringIO()
    folder = tempfile.mkdtemp(dir=WORK)
    with contextlib.redirect_stdout(said):
        got = vpm.recordings_carry_cameras(
            args, [{"audio": p, "blocks": [p]} for p in recordings],
            [(v, vpm.video_facts(v)) for v in videos], None, folder)
    if got is None:
        return None, None, said.getvalue()
    ref_clip, position, tracks = got
    out = dict((v, -a / b) for v, (a, b, _st) in position.items())
    for track in tracks:
        track["drift"] = vpm.drift_clear(track["b"], track.get("st"))
        out[track["blocks"][0]] = vpm.recordings_on_axis(
            [track], (0.0, 1.0))[0][2]
    return out, ref_clip[0], said.getvalue()


def window_side(paths, raw=None):
    """The window's axis over *paths*, the phase way off as for speech."""
    with contextlib.redirect_stdout(io.StringIO()):
        data, text = vpm.measure_time_axis(paths, clock,
                                           phase_of=lambda p: False,
                                           raw=raw)
    return data, text


def from_(data, p, base):
    """Where the window lays *p*, counted from *base*."""
    axis = (data or {}).get("axis") or {}
    k, b = vpm.path_key(p), vpm.path_key(base)
    return None if k not in axis or b not in axis else axis[k] - axis[b]


#---------------------------------- 1. A camera none hears, with a clock

print("1. A camera with no sound and a clock, beside recordings with clocks")
FILES = [CAM, PRES, GUEST, HISS]
run, ref, _said = run_side([CAM], [PRES, GUEST, HISS])
data, text = window_side(FILES)
print("   %s; weak %s, no place %s" % (text, named(data, "weak"),
                                       named(data, "no_place")))
for p in FILES:
    print("   %-28s run %s, window %s" % (
        name_of(p), figure((run or {}).get(p)), figure(from_(data, p, CAM))))
check("the run lays a camera none hears at its clock, as its reference",
      run is not None and ref == CAM
      and abs(run.get(PRES, 99.0) + CAM_AFTER) <= SAME,
      "reference %s, the presenter at %s from it, wanted %+.4f"
      % (name_of(ref or ""), figure((run or {}).get(PRES)), -CAM_AFTER))
check("and one its sound cannot place at that recording's own clock",
      run is not None
      and abs(run.get(HISS, 99.0) - (HISS_AFTER - CAM_AFTER)) <= SAME,
      "the hiss at %s from the camera, wanted %+.4f"
      % (figure((run or {}).get(HISS)), HISS_AFTER - CAM_AFTER))
apart = [(name_of(p), from_(data, p, CAM), r) for p, r in
         sorted((run or {}).items())
         if from_(data, p, CAM) is None or abs(from_(data, p, CAM) - r)
         > SAME]
check("the window lays every file where the run lays it, to 0.1 ms",
      run is not None and len(run) == len(FILES) and not apart,
      "; ".join("%s window %s run %+.4f" % (n, figure(w), r)
                for n, w, r in apart) or "the run placed %d of %d"
      % (len(run or {}), len(FILES)))
check("the window reads its marks at the run's reference camera",
      (data or {}).get("reference") == vpm.path_key(CAM),
      "reference %r, wanted %r" % (name_of((data or {}).get("reference")
                                           or ""), name_of(CAM)))
check("the camera and the recording its clock placed keep their place",
      named(data, "weak") == sorted(name_of(p) for p in (CAM, HISS))
      and named(data, "no_place") == [],
      "weak %s, no place %s, wanted %s and none"
      % (named(data, "weak"), named(data, "no_place"),
         sorted(name_of(p) for p in (CAM, HISS))))

# No material built here gets the run's curve that low, so the guest's
# measurement goes in as the run keeps it, its match set to 0.10.
kept = {}
window_side(FILES, kept)
low = kept.get("against", {}).get(vpm.path_key(GUEST)) or [0.0, 1.0, {}]
low[2] = dict(low[2], quality=0.10)
data, text = window_side(FILES, kept)
check("a recording the run placed at a match of 0.10 is not named",
      name_of(GUEST) not in named(data, "weak")
      and from_(data, GUEST, CAM) is not None,
      "weak %s, the guest at %s from the camera, kept %s"
      % (named(data, "weak"), figure(from_(data, GUEST, CAM)),
         "yes" if "against" in kept else "no"))

#------------------------------------- 2. With no clock to stand at

print("\n2. That camera with no clock, and with nothing to set its clock by")
run, _ref, said = run_side([CAM_BARE], [PRES, GUEST])
data, text = window_side([CAM_BARE, PRES, GUEST])
print("   %s; no place %s" % (text, named(data, "no_place")))
check("a camera none hears with no clock has no place, as in the run",
      run is None and named(data, "no_place") == [name_of(CAM_BARE)]
      and named(data, "clock_alone") == [],
      "the run %s; no place %s, clock alone %s"
      % ("places nothing" if run is None else "places %d" % len(run),
         named(data, "no_place"), named(data, "clock_alone")))
run, _ref, said = run_side([CAM], [PRES_BARE, GUEST_BARE])
data, text = window_side([CAM, PRES_BARE, GUEST_BARE])
print("   %s; clock alone %s" % (text, named(data, "clock_alone")))
check("one whose clock nothing the sound placed can meet is a clock alone",
      run is None and named(data, "no_place") == [name_of(CAM)]
      and named(data, "clock_alone") == [name_of(CAM)],
      "the run %s; no place %s, clock alone %s"
      % ("places nothing" if run is None else "places %d" % len(run),
         named(data, "no_place"), named(data, "clock_alone")))

#--------------------------------------------------- 3. With no picture

print("\n3. No picture: the longest starts later, a sting, a lone clock")
data, text = window_side([PRES_BARE, EARLY, SHORT, HISS])
print("   %s; no place %s, brief %s, clock alone %s"
      % (text, named(data, "no_place"), named(data, "brief"),
         named(data, "clock_alone")))
check("with no picture the axis counts from the earliest, not the longest",
      from_(data, EARLY, EARLY) == 0.0
      and min(((data or {}).get("axis") or {"": 1.0}).values()) == 0.0
      and abs((from_(data, PRES_BARE, EARLY) or 99.0) - 10.0) < 0.01,
      "the earliest at %s, the longest %s after it, wanted +10.0"
      % (figure(min(((data or {}).get("axis") or {"": None}).values())),
         figure(from_(data, PRES_BARE, EARLY))))
check("a short one that fits nothing is named far shorter",
      named(data, "brief") == [name_of(SHORT)],
      "brief %s, no place %s, wanted [%r]"
      % (named(data, "brief"), named(data, "no_place"), name_of(SHORT)))
check("one with a clock nothing placed carries is a clock alone",
      named(data, "clock_alone") == [name_of(HISS)]
      and name_of(HISS) in named(data, "no_place"),
      "clock alone %s, no place %s, wanted [%r] in both"
      % (named(data, "clock_alone"), named(data, "no_place"),
         name_of(HISS)))

#--------------------------------------------------------- 4. The run

print("\n4. A dry run over the files of the first section")
try:
    answer = subprocess.run(
        [sys.executable, SCRIPT, "--project-type", "sync",
         "--without-auphonic", "--dry-run", "--no-preflight", "--out",
         os.path.join(WORK, "out")] + FILES,
        capture_output=True, text=True, timeout=240,
        env=dict(os.environ, QT_QPA_PLATFORM="offscreen"))
    code, said = answer.returncode, answer.stdout + answer.stderr
except subprocess.TimeoutExpired:
    code, said = -1, ""
said = re.sub(re.escape(vpm.MARK) + "[a-z]", "", said)
lines = [x.strip() for x in re.sub(r"\x1b\[[0-9;]*m", "", said)
         .replace("\r", "\n").splitlines() if x.strip()]
check("a run over a camera none hears goes through",
      code == 0, "returned %r after %d lines, the last %r"
      % (code, len(lines), lines[-1] if lines else ""))
by_clock = (vpm.T('  %s gives no sound to measure -- placed by its clock '
                  'alone, and nothing was found to check it against')
            % name_of(CAM)).strip()
check("and stands the camera at its clock against the recordings",
      by_clock in lines, "%d lines, wanted one saying %r"
      % (len(lines), by_clock))

shutil.rmtree(WORK, ignore_errors=True)
print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
