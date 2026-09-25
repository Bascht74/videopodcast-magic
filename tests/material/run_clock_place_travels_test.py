# -*- coding: utf-8 -*-
"""Where its clock places a camera, its own sound and handover follow.

One real run, Sync only and --without-auphonic, over two cameras alone,
each a steady tone with an honest timecode, the second rolling 2.48 s
earlier; its tone breaks off once. In order: the run goes through and its
clock places the second camera, and its own lines say so, check
nothing and print no drift; in its written file its own sound breaks
off where its picture's sound does, within a frame; the handover says
the clock placed it and not the other, and the log that its sound
matched too weakly.
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
import the_program
import json
import re
import struct
import subprocess
import tempfile
import threading
import time

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


def stop():
    """Nothing further can be asked, so count what there is and go."""
    print("\n%d checks in %.2f s" % (done, time.time() - began))
    print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
    sys.exit(1 if bad else 0)


# No output for this long and the run is stuck rather than slow: it
# writes a progress bar while it works, so silence is the sign.
STILL = 120.0
STEP = 0.25
# A bound for one ffmpeg or ffprobe over seconds of material, so a tool
# that never answers is named in the line before run.sh ends the test.
ASK = 120.0


def run(argv):
    """Start the program and watch it: (code, what it said, stuck, seconds)."""
    kid = subprocess.Popen(argv, stdout=subprocess.PIPE,
                           stderr=subprocess.STDOUT,
                           env=dict(os.environ, QT_QPA_PLATFORM="offscreen"))
    pieces = []

    def read():
        """Collect what the program writes until it closes the pipe."""
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
    kid.wait()
    text = b"".join(pieces).decode("utf-8", "replace")
    # The mark in front of a warning is for the window, not for a line.
    text = re.sub(re.escape(vpm.MARK) + "[a-z]", "", text)
    text = re.sub(r"\x1b\[[0-9;]*m", "", text).replace("\r", "\n")
    return kid.returncode, text, stuck, took


def tool(argv):
    """What a tool wrote to stdout, or None if it did not end within ASK."""
    try:
        return subprocess.run(argv, stdout=subprocess.PIPE,
                              stderr=subprocess.DEVNULL,
                              timeout=ASK).stdout
    except subprocess.TimeoutExpired:
        return None


def tracks(path):
    """The audio tracks of a file by name, {name: index}; None: no answer."""
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


def breaks(path, index):
    """Where one track falls silent for under a second, in seconds.

    Decoded by ffmpeg, not the program, and read in blocks of 10 ms: a
    block under a tenth of the loudest is silent. A longer silence is
    the padding before a track begins and is not a break.
    """
    raw = tool(["ffmpeg", "-v", "error", "-i", path, "-map",
                "0:a:%d" % index, "-ac", "1", "-ar", "8000", "-f", "s16le",
                "-"])
    if not raw:
        return []
    s = struct.unpack("<%dh" % (len(raw) // 2), raw[:len(raw) // 2 * 2])
    level = [max(abs(x) for x in s[k:k + 80])
             for k in range(0, len(s) - 79, 80)]
    top, found, start = max(level or [0]), [], None
    for k, v in enumerate(level + [top]):
        if v < top * 0.1 and start is None:
            start = k
        elif v >= top * 0.1 and start is not None:
            if k - start < 100:
                found.append(start * 0.01)
            start = None
    return found


def make(path, sound, timecode):
    """A camera made with ffmpeg; a precondition, not a judgement."""
    made = subprocess.run(
        ["ffmpeg", "-v", "error", "-f", "lavfi", "-i",
         "testsrc=size=160x90:rate=25:duration=%g" % LENGTH, "-f", "lavfi",
         "-i", sound, "-c:v", "libx264", "-preset", "ultrafast", "-pix_fmt",
         "yuv420p", "-c:a", "aac", "-timecode", timecode, "-shortest",
         path, "-y"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
        timeout=ASK)
    assert made.returncode == 0 and os.path.exists(path), made.stdout
    return path


#------------------------------------------------------------- Material

HOME = tempfile.mkdtemp(prefix="vpm_clockplace_")
LENGTH = 2 * vpm.AXIS_MIN_WINDOW_S
FRAME = 1.0 / 25
# The presenter's tone breaks off here in its own time: a steady tone
# gives the sound nothing to place, and this mark shows where it went.
BREAK = 11.0
GUEST = make(os.path.join(HOME, "GuestCam_C003.mov"),
             "sine=frequency=220:duration=%g" % LENGTH, "18:55:06:12")
PRESENTER = make(
    os.path.join(HOME, "PresenterCam_C002.mov"),
    "aevalsrc='0.5*sin(2*PI*330*t)*(1-between(t,%g,%g))':s=48000:d=%g"
    % (BREAK, BREAK + 0.3, LENGTH), "18:55:04:00")
STEM = os.path.splitext(os.path.basename(PRESENTER))[0]
OTHER = os.path.splitext(os.path.basename(GUEST))[0]
OUT = os.path.join(HOME, "out")

#----------------------------------------------------------------- 1. Run

print("1. Two quiet cameras, Sync only, cameras alone")
code, said, stuck, took = run([sys.executable, SCRIPT, "--project-type",
                               "sync", "--without-auphonic", "--multitrack",
                               "--out", OUT, GUEST, PRESENTER])
lines = [line.strip() for line in said.splitlines() if line.strip()]
check("a run over two quiet cameras goes through",
      code == 0 and not stuck,
      "returned %r after %.1f s, stood still %s, last line %r"
      % (code, took, stuck, lines[-1] if lines else ""))
by_clock = re.escape(vpm.T('  %s: its sound matches by %s, under the floor '
                           'of %s -- placed by its clock alone').strip()
                     ).replace(re.escape("%s"), "(.*?)")
placed = [m.group(1) for m in (re.match(by_clock, x) for x in lines) if m]
check("its clock places the camera that rolled earlier",
      placed == [os.path.basename(PRESENTER)],
      "placed by the clock: %s, wanted [%r]"
      % (placed, os.path.basename(PRESENTER)))
# Each camera's lines come out in one piece under its own head.
head = vpm.T('\nPROCESSING: %s').strip() % os.path.basename(PRESENTER)
own_lines = []
if head in lines:
    for x in lines[lines.index(head) + 1:]:
        if x.startswith(vpm.T('\nPROCESSING: %s').strip() % ""):
            break
        own_lines.append(x)
by_timecode = vpm.T('  Offset:          %s   (from its timecode alone -- '
                    'its sound could not place it, so nothing is '
                    'checked)').strip().split("%s")[1].strip()
measuring = [x for x in own_lines
             if x.startswith(vpm.T('  Cross-check:     %s from the Full-Mix, '
                                   'deviation %s ms (%s of %s points)%s'
                                   ).strip().split("%s")[0].strip())
             or x.startswith(vpm.T('  Check:           %s against the camera '
                                   'track %s ms (match %s)%s'
                                   ).strip().split("%s")[0].strip())]
check("and its own lines say the clock placed it, and check nothing",
      any(x.endswith(by_timecode) for x in own_lines) and not measuring,
      "%d lines under %r, the clock's among them: %s; measuring: %s"
      % (len(own_lines), head, any(x.endswith(by_timecode)
                                   for x in own_lines), measuring))
drifting = [x for x in own_lines
            if x.startswith(vpm.T('  Clock drift:     %s ppm (+/- %s), '
                                  'residual spread %s ms, %s of %s points'
                                  ).strip().split("%s")[0].strip())
            or x.startswith(vpm.T('  Drift over the running time: %s s = '
                                  '%s frames  -->  %s'
                                  ).strip().split("%s")[0].strip())]
check("and no drift of its clock is printed, since none was measured",
      own_lines and not drifting,
      "%d lines under %r; drift lines among them: %s"
      % (len(own_lines), head, drifting))

#---------------------------------------------------- 2. Its written file

print("\n2. The camera's own sound in its written file")
WRITTEN = os.path.join(OUT, STEM + "_audio.mov")
have = tracks(WRITTEN) if os.path.exists(WRITTEN) else {}
ORIGINAL = vpm.build_argument_parser().get_default("name_camera")
own = breaks(WRITTEN, have[STEM]) if have and STEM in have else []
picture = breaks(WRITTEN, have[ORIGINAL]) if have and ORIGINAL in have else []
check("the own sound stands with its picture within a frame",
      len(own) == 1 and len(picture) == 1
      and abs(own[0] - picture[0]) <= FRAME,
      "breaks off at %s s in track %r, at %s s in %r, at most %.2f apart; "
      "tracks %s" % (own, STEM, picture, ORIGINAL, FRAME,
                     sorted(have) if have is not None else "no answer"))

#--------------------------------------------------------- 3. The handover

print("\n3. What the handover says")
found = [os.path.join(OUT, f) for f in sorted(os.listdir(OUT))
         if f.endswith("_resolve.json")] if os.path.isdir(OUT) else []
cameras = {}
if len(found) == 1:
    with open(found[0], encoding="utf-8") as f:
        cameras = {c.get("camera"): c.get("placed_by")
                   for c in json.load(f).get("cameras") or []}
check("and the handover says the clock placed it, and not the other",
      cameras.get(STEM) == "clock" and cameras.get(OTHER) == "measured",
      "placed_by %s, wanted %r clock and %r measured; handover files %s"
      % (cameras, STEM, OTHER, [os.path.basename(f) for f in found]))
weak = vpm.T('  The sound of %s matched too weakly to trust -- placed by '
             'the timecode alone.') % STEM
nothing = vpm.T('  Nothing was found in the sound for %s -- placed by the '
                'timecode alone.') % STEM
check("and the log says its sound matched too weakly, not that none was",
      weak.strip() in lines and nothing.strip() not in lines,
      "%r %s, %r %s, among the %d lines the run wrote"
      % (weak.strip(), "found" if weak.strip() in lines else "not found",
         nothing.strip(), "found" if nothing.strip() in lines
         else "not found", len(lines)))

stop()
