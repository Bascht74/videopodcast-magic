# -*- coding: utf-8 -*-
"""The check of a written camera file reads it once, not once per track.

Mix and camera track sit in one container, and a pass over a 36 GB file is
what a run pays for on a drive. Two containers are built here, one with
four audio tracks and one with two. In order: two tracks out of one
ffmpeg, the same samples as one call per track and in the order they were
asked for, one progress stream that never falls back, a track that is not
there named instead of reported as a bad match, and one track alone.
"""
import os
import the_program
HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = the_program.SCRIPT
import contextlib, io, subprocess, sys, tempfile, time
import numpy as np
vpm = the_program.load()
vpm.set_language("en")
WORK = tempfile.mkdtemp(prefix="checkread_")
RATE, SECONDS = 4000, 4.0
TONES = [300, 550, 800, 1100]
began = time.time()
done = 0
bad = []


def check(name, ok, extra=""):
    global done
    done += 1
    print("  %-58s %s %s" % (name, "ok" if ok else "FAIL", extra))
    if not ok:
        bad.append("%s [%s]" % (name, extra or "no numbers"))


def build(name, how_many):
    """A container with a small picture and one tone per audio track."""
    cmd = ["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i",
           "testsrc2=size=320x180:rate=15:duration=%d" % int(SECONDS)]
    for hz in TONES[:how_many]:
        cmd += ["-f", "lavfi", "-i", "sine=frequency=%d:duration=%d"
                ":sample_rate=48000" % (hz, int(SECONDS))]
    cmd += ["-map", "0:v"] + sum(
        [["-map", "%d:a" % (k + 1)] for k in range(how_many)], [])
    path = os.path.join(WORK, name)
    cmd += ["-c:v", "libx264", "-preset", "ultrafast", "-pix_fmt", "yuv420p",
            "-c:a", "pcm_s16le", path]
    subprocess.run(cmd, capture_output=True)
    return path


def one_call(path, stream):
    """The way it was done: one ffmpeg call for one track."""
    cmd = ["ffmpeg", "-v", "error", "-i", path]
    if stream is not None:
        cmd += ["-map", "0:a:%d" % stream]
    cmd += ["-ac", "1", "-ar", str(RATE), "-f", "f32le", "-"]
    p = subprocess.run(cmd, capture_output=True)
    return np.frombuffer(p.stdout, dtype=np.float32).astype(np.float64)


def top_hz(x):
    """The loudest frequency in a piece of sound, so a track can be named."""
    if len(x) < 2:
        return 0.0
    peak = np.abs(np.fft.rfft(x * np.hanning(len(x))))
    return float(np.fft.rfftfreq(len(x), 1.0 / RATE)[int(np.argmax(peak))])


def said(work):
    """Everything the program printed while work ran."""
    buffer = io.StringIO()
    with contextlib.redirect_stdout(buffer):
        work()
    return buffer.getvalue()


starts = []
real_popen = subprocess.Popen


def counting(cmd, *rest, **named):
    if isinstance(cmd, (list, tuple)) and cmd and "ffmpeg" in str(cmd[0]):
        starts.append(list(cmd))
    return real_popen(cmd, *rest, **named)


print("1. Two tracks out of one pass")
four = build("four.mov", 4)
size = os.path.getsize(four) if os.path.exists(four) else 0
check("the file with four audio tracks was built", size > 10000,
      "%d bytes at %s" % (size, four))
del starts[:]
subprocess.Popen = counting
try:
    both = vpm.decode_audio_tracks(four, RATE, SECONDS, "x", [0, 3])
finally:
    subprocess.Popen = real_popen
check("reading two tracks starts one ffmpeg, not one per track",
      len(starts) == 1, "%d started, wanted 1" % len(starts))
alone = [one_call(four, 0), one_call(four, 3)]
check("both tracks are as long as one call per track gives",
      [len(x) for x in both] == [len(x) for x in alone],
      "%s against %s" % ([len(x) for x in both], [len(x) for x in alone]))
equal = [a.tobytes() == b.tobytes() for a, b in zip(both, alone)]
check("and byte for byte the same as one call per track", all(equal),
      "%d of %d tracks equal over %d bytes"
      % (sum(equal), len(equal), len(both[0].tobytes())))
check("the track asked for first is the first one back",
      abs(top_hz(both[0]) - 300) < 25, "%.0f Hz, wanted 300" % top_hz(both[0]))
check("and the one asked for second is not the first again",
      abs(top_hz(both[1]) - 1100) < 25,
      "%.0f Hz, wanted 1100" % top_hz(both[1]))

print("\n2. One process, so one progress stream")
seen = []
vpm.decode_audio_tracks(four, RATE, SECONDS, "x", [0, 3], report=seen.append)
check("progress is reported before the end is announced", len(seen) >= 2,
      "%d reports, wanted at least 2" % len(seen))
falls = [(i, round(seen[i - 1], 3), round(seen[i], 3))
         for i in range(1, len(seen)) if seen[i] < seen[i - 1]]
check("and the bar never falls back to the start", not falls,
      "%d of %d steps fall back: %s" % (len(falls), max(1, len(seen) - 1),
                                        falls[:3]))


class Args(object):
    no_camera_audio = False
    dry_run = False


print("\n3. A track that is not in the file")
two = build("two.mov", 2)
size = os.path.getsize(two) if os.path.exists(two) else 0
check("the file with two audio tracks was built", size > 10000,
      "%d bytes at %s" % (size, two))
# Three tracks claimed against two in the file: the camera track is asked
# for at 0:a:3 and is not there.
items = [("Full-Mix", 0), ("Anna", 0), ("Bert", 0)]
try:
    spoke, alive = said(
        lambda: vpm.check_written_file(two, items, 1, Args(), 25.0)), "yes"
except Exception as e:
    spoke, alive = "", repr(e)
check("a missing track does not end the run in a traceback",
      alive == "yes", alive)
absent = vpm.T('  Check:           one of the two tracks is not in the '
               'written file, so nothing was measured.')
check("the missing track is named as missing", absent in spoke,
      "%d characters printed, ending %r" % (len(spoke), spoke[-70:]))
weak = vpm.T('  Check:           the two tracks cannot be compared '
             '(match %.2f, %.2f is the floor). This says nothing '
             'about the timing.') % (0.0, vpm.WEAK_MATCH)
check("and no bad match is reported in its place", weak not in spoke,
      "%d characters printed, ending %r" % (len(spoke), spoke[-70:]))

print("\n4. One track asked for alone")


def beside(mine, theirs):
    """Length and loudest tone of both, so a swapped track shows up."""
    return ("%d samples at %.0f Hz against %d at %.0f Hz"
            % (len(mine), top_hz(mine), len(theirs), top_hz(theirs)))


lone = vpm.decode_audio_long(four, RATE, SECONDS, "x", stream=2)
ref = one_call(four, 2)
check("one track alone is what one ffmpeg call gives",
      lone.tobytes() == ref.tobytes(), beside(lone, ref))
whole = vpm.decode_audio_long(four, RATE, SECONDS, "x")
ref = one_call(four, None)
check("and asking for no track at all is the file's own choice",
      whole.tobytes() == ref.tobytes(), beside(whole, ref))

print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
