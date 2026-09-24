# -*- coding: utf-8 -*-
"""A camera's own sound, taken for want of a recording, is its track.

Real runs with --without-auphonic over two short cameras made here,
each with a tone and a timecode of its own and the tone in one pattern
of bursts, so that the sound places them where their clocks do, as
project type "sync" so that no speech is recognised. Afterwards the
written camera files are asked, not the program: the track is found by
its name, a few seconds of it are decoded with ffmpeg and its tone
counted, and held against the tone counted the same way in the camera
the run was given. The sections: "use internal audio" on two cameras,
the plan built the way the window builds it; one camera on a bare
command line and no recording, where the camera's sound becomes the
mix; two cameras and --multitrack with no recording; and cameras with
no sound at all, where the run stops and says so.

The limit of the method: a tone is one frequency, so this says the
right camera's sound arrived, not that nothing else was mixed into it.
"""
import os
import the_program
HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = the_program.SCRIPT
import json
import re
import struct
import subprocess
import sys
import tempfile
import threading
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


def stop():
    """Nothing further can be asked, so count what there is and go."""
    print("\n%d checks in %.2f s" % (done, time.time() - began))
    print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
    sys.exit(1 if bad else 0)


# No output at all for this long, and the run is stuck rather than slow:
# the program writes a progress bar while it works, so silence is the
# sign of life, not a clock that a slower builder would outrun.
STILL = 120.0
STEP = 0.25


def run(argv):
    """Start the program and watch it: (code, last line, stuck, seconds)."""
    kid = subprocess.Popen(argv, stdout=subprocess.PIPE,
                           stderr=subprocess.STDOUT,
                           env=dict(os.environ, QT_QPA_PLATFORM="offscreen"))
    pieces = []

    def read():
        while True:
            try:
                piece = os.read(kid.stdout.fileno(), 65536)
            except OSError:
                break
            if not piece:
                break
            pieces.append(piece)

    reader = threading.Thread(target=read)
    reader.daemon = True
    reader.start()
    started, last, seen, stuck = time.time(), time.time(), 0, False
    while kid.poll() is None:
        time.sleep(STEP)
        if len(pieces) != seen:
            seen, last = len(pieces), time.time()
        if time.time() - last > STILL:
            stuck = True
            kid.kill()
            break
    took = time.time() - started
    reader.join(10)
    try:
        kid.stdout.close()
    except Exception:
        pass
    kid.wait()
    text = b"".join(pieces).decode("utf-8", "replace")
    text = re.sub(r"\x1b\[[0-9;]*m", "", text).replace("\r", "\n")
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    return kid.returncode, (lines[-1] if lines else ""), stuck, took


# One ffprobe or ffmpeg over a file of seconds takes a fraction of one
# here; this bound is only there so that a tool that never answers is
# named in the line, well before run.sh ends the whole test.
ASK = 120.0


def tool(argv):
    """What a tool wrote to stdout, or None if it did not end within ASK."""
    try:
        return subprocess.run(argv, stdout=subprocess.PIPE,
                              stderr=subprocess.DEVNULL,
                              timeout=ASK).stdout
    except subprocess.TimeoutExpired:
        return None


def tracks(path):
    """The audio tracks of a file by name: {name: index among the audio}.

    None if ffprobe did not answer.
    """
    out = tool(["ffprobe", "-v", "error", "-select_streams", "a",
                "-show_entries", "stream_tags=handler_name", "-of", "json",
                path])
    if out is None:
        return None
    try:
        streams = json.loads(out.decode("utf-8") or "{}")["streams"]
    except (ValueError, KeyError):
        return {}
    return {(s.get("tags") or {}).get("handler_name", ""): i
            for i, s in enumerate(streams)}


def tone(path, index=0):
    """The tone of one audio track, in Hz: upward zero crossings per second.

    Counted over two seconds from the fourth, folded to one channel, by
    ffmpeg and not by the program. 0 where there is nothing to count,
    None if ffmpeg did not answer.
    """
    raw = tool(["ffmpeg", "-v", "error", "-ss", "4", "-t", "2", "-i", path,
                "-map", "0:a:%d" % index, "-ac", "1", "-ar", "48000",
                "-f", "s16le", "-"])
    if raw is None:
        return None
    s = struct.unpack("<%dh" % (len(raw) // 2), raw[:len(raw) // 2 * 2])
    if len(s) < 24000:
        return 0.0
    ups = sum(1 for a, b in zip(s, s[1:]) if a < 0 <= b)
    return ups / (len(s) / 48000.0)


def carries(written, name, camera):
    """(is the named track the camera's tone, the line saying so)."""
    have = tracks(written) if os.path.exists(written) else {}
    if have is None:
        return False, "ffprobe gave no answer on %s within %.0f s" % (
            os.path.basename(written), ASK)
    if name not in have:
        return False, "%s holds no track %r, only %s" % (
            os.path.basename(written), name, sorted(have))
    got, want = tone(written, have[name]), SOURCE[camera] or 0.0
    if got is None:
        return False, "ffmpeg gave no answer on %s within %.0f s" % (
            os.path.basename(written), ASK)
    return (want > 0 and abs(got - want) <= NEAR,
            "track %r of %s at %.1f Hz, %s at %.1f Hz, at most %.1f apart"
            % (name, os.path.basename(written), got,
               os.path.basename(camera), want, NEAR))


# The two cameras' tones lie a hundred hertz apart, and one counted
# twice lands within a fraction of a hertz.
NEAR = 3.0
COMMON = ["--project-type", "sync", "--without-auphonic"]


def make(path, argv):
    """Material made here with ffmpeg; a precondition, not a judgement."""
    made = subprocess.run(["ffmpeg", "-v", "error"] + argv + [path, "-y"],
                          stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                          timeout=ASK)
    assert made.returncode == 0 and os.path.exists(path), made.stdout
    return path


HOME = tempfile.mkdtemp(prefix="vpm_camown_")
# Short, so that the runs cost little on a slow builder, and long enough
# that the two cameras share twice the stretch the program needs before
# it places anything on a common axis. The second rolls 2.48 s later,
# frames and all, so its place is not a whole number of seconds.
LENGTH = 2 * vpm.AXIS_MIN_WINDOW_S


# Each camera's tone sounds only in bursts, and the bursts are one pattern
# in the room's time, which each camera hears from its own start: of
# different lengths at uneven spacing, so no shift but the true one lays
# the two loudness curves over each other. A steady tone has no curve at
# all, and then the cameras are placed by a guess that numerical noise
# decides -- on the builders one that left under 8 s in common. The long
# burst holds the stretch the tone is counted over, in every file and on
# the axis.
LATE = 2.48
BURSTS = [(0.6, 1.3), (1.9, 2.1), (2.9, 3.2), (3.7, 8.9), (9.6, 10.0),
          (10.8, 11.9), (12.3, 12.45), (13.4, 14.3), (15.1, 15.35),
          (16.2, 17.8), (18.5, 18.65), (19.3, 20.3), (21.0, 21.4),
          (21.9, 22.2)]


def camera(name, hz, timecode, late):
    gate = "+".join("between(t+%g,%g,%g)" % (late, x, y) for x, y in BURSTS)
    return make(os.path.join(HOME, name), [
        "-f", "lavfi", "-i", "testsrc=size=160x90:rate=25:duration=%g"
        % LENGTH, "-f", "lavfi", "-i",
        "aevalsrc='0.5*sin(2*PI*%d*t)*(%s)':s=48000:d=%g" % (hz, gate, LENGTH),
        "-c:v", "libx264", "-preset", "ultrafast",
        "-pix_fmt", "yuv420p", "-c:a", "aac", "-timecode", timecode,
        "-shortest"])


PRESENTER = camera("PresenterCam_C002.mov", 330, "18:55:04:00", 0.0)
GUEST = camera("GuestCam_C003.mov", 220, "18:55:06:12", LATE)
# Each camera's tone, counted once by the same route as the written files.
SOURCE = {path: tone(path) for path in (GUEST, PRESENTER)}

print("1. \"Use internal audio\" on two cameras")
OUT = os.path.join(HOME, "internal")
os.makedirs(OUT)
PLAN = os.path.join(OUT, "plan.json")
# What the window holds with both cameras set to their own sound; the
# command line and the plan are built by the window's own builder.
argv, plan, messages = vpm.run_argv({
    "files": [(GUEST, "video"), (PRESENTER, "video")], "clip_kinds": {},
    "out_folder": OUT, "dry_run": False, "multitrack": True,
    "camera_audio_only": True, "project_type": "sync",
    "rows": [{"blocks": [GUEST], "speakers": "Guest",
              "camera_choice": os.path.basename(GUEST)},
             {"blocks": [PRESENTER], "speakers": "Presenter",
              "camera_choice": os.path.basename(PRESENTER)}],
    "cameras": [{"path": GUEST, "name": "Guest"},
                {"path": PRESENTER, "name": "Presenter"}],
    "production": "Internal", "in_point": "", "out_point": "", "cut": {},
    "wide_at_edges": True, "key": "", "preset": "", "done_folder": ""},
    PLAN)
with open(PLAN, "w", encoding="utf-8") as f:
    json.dump(plan or {}, f)
# No command line, and nothing is started: without its arguments the
# program would open its window and wait.
if argv is None:
    code, stuck, said = None, False, (
        "run_argv gave no command line, so nothing was started; it said %r"
        % [m[2] for m in messages])
else:
    code, last, stuck, took = run([sys.executable, SCRIPT] + argv[1:])
    said = ("returned %r after %.1f s, stood still %s, last line %r"
            % (code, took, stuck, last))
check("a run over cameras set to their own sound goes through",
      argv is not None and code == 0 and not stuck, said)
ok1, said1 = carries(os.path.join(OUT, "Guest_audio.mov"), "Guest", GUEST)
ok2, said2 = carries(os.path.join(OUT, "Presenter_audio.mov"), "Presenter",
                     PRESENTER)
check("each camera's file carries its own sound as its speaker",
      ok1 and ok2, "%s; %s" % (said1, said2))

print("\n2. One camera on the command line, no recording")
OUT = os.path.join(HOME, "single")
code, last, stuck, took = run([sys.executable, SCRIPT] + COMMON
                              + ["--out", OUT, PRESENTER])
check("a lone camera with sound and no recording goes through",
      code == 0 and not stuck,
      "returned %r after %.1f s, stood still %s, last line %r"
      % (code, took, stuck, last))
STEM = os.path.splitext(os.path.basename(PRESENTER))[0]
ok, said = carries(os.path.join(OUT, STEM + "_audio.mov"),
                   vpm.MIX_TRACK_NAME, PRESENTER)
check("its sound becomes the mix track of its file", ok, said)

print("\n3. Two cameras and --multitrack, no recording")
OUT = os.path.join(HOME, "multitrack")
code, last, stuck, took = run([sys.executable, SCRIPT] + COMMON
                              + ["--multitrack", "--out", OUT,
                                 GUEST, PRESENTER])
check("cameras alone with --multitrack go through",
      code == 0 and not stuck,
      "returned %r after %.1f s, stood still %s, last line %r"
      % (code, took, stuck, last))
STEM1 = os.path.splitext(os.path.basename(GUEST))[0]
STEM2 = os.path.splitext(os.path.basename(PRESENTER))[0]
ok1, said1 = carries(os.path.join(OUT, STEM1 + "_audio.mov"), STEM1, GUEST)
ok2, said2 = carries(os.path.join(OUT, STEM2 + "_audio.mov"), STEM2,
                     PRESENTER)
check("each camera's file carries its own sound under its name",
      ok1 and ok2, "%s; %s" % (said1, said2))

print("\n4. Cameras with no sound at all")
OUT = os.path.join(HOME, "mute")
os.makedirs(OUT)
MUTE = [make(os.path.join(OUT, "Mute_C00%d.mp4" % n), [
    "-f", "lavfi", "-i", "testsrc=size=160x90:rate=25:duration=2",
    "-c:v", "libx264", "-preset", "ultrafast", "-pix_fmt", "yuv420p"])
    for n in (1, 2)]
code, last, stuck, took = run([sys.executable, SCRIPT] + COMMON
                              + ["--multitrack", "--out",
                                 os.path.join(OUT, "out")] + MUTE)
WANT = vpm.T('No sound in the cameras -- nothing to work with.')
check("cameras without any sound stop the run, saying so",
      code == 1 and last == WANT,
      "returned %r against 1, last line %r against %r" % (code, last, WANT))

stop()
