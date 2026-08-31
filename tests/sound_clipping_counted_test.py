# -*- coding: utf-8 -*-
"""Clipping is counted per channel, and only where the format has a stop.

An integer format has a highest value, and samples sitting on it were
cut off. Float has no such stop, so a peak above 0 dBFS there is loud,
not damaged, and counting it would warn about nothing.

Sections: the material and the numpy under it; the count over integer
and float, loud and quiet; the channel that hit the stop, picked out of
a stereo pair; the run's length in samples and in milliseconds; and the
preflight, which raises one hint for that one channel, names it
counting from one, carries the count, and never a reason to stop.
"""
import os
import subprocess
import sys
import tempfile
import time

HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = os.environ.get("VPM_SCRIPT") or os.path.join(
    os.path.dirname(HERE), "videopodcast-magic.py")
os.environ["VPM_NO_UPDATE_CHECK"] = "1"
import importlib.util
spec = importlib.util.spec_from_file_location("vpm", SCRIPT)
vpm = importlib.util.module_from_spec(spec); sys.modules["vpm"] = vpm
spec.loader.exec_module(vpm)

began = time.time()
done = 0
bad = []


def check(name, ok, extra=""):
    global done
    done += 1
    print("  %-58s %s %s" % (name, "ok" if ok else "FAIL", extra))
    if not ok:
        bad.append("%s [%s]" % (name, extra or "no numbers"))


RATE = 48000
NOTHING = (0, 0, 0.0, 0.0)


def written(path):
    """A file ffmpeg really wrote, not one it opened and gave up on."""
    return os.path.exists(path) and os.path.getsize(path) > 1000


def sine(path, gain, codec):
    """Two seconds of a sine at a chosen gain, in a chosen format."""
    subprocess.run(
        ["ffmpeg", "-y", "-v", "error", "-f", "lavfi",
         "-i", "sine=frequency=440:duration=2:sample_rate=%d" % RATE,
         "-af", "volume=%s" % gain, "-c:a", codec, path],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return written(path)


def two_sided(path, left, right, codec):
    """One stereo file with a different gain on each side.

    The loud side is the right one on purpose: a count that always
    answers "channel one" then says the wrong thing instead of the
    right thing by accident.
    """
    one = "sine=frequency=440:duration=2:sample_rate=%d" % RATE
    subprocess.run(
        ["ffmpeg", "-y", "-v", "error", "-f", "lavfi", "-i", one,
         "-f", "lavfi", "-i", one, "-filter_complex",
         "[0:a]volume=%s[l];[1:a]volume=%s[r];[l][r]amerge=inputs=2[a]"
         % (left, right), "-map", "[a]", "-c:a", codec, path],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return written(path)


folder = tempfile.mkdtemp(prefix="vpm_clip_")
hot16 = os.path.join(folder, "hot16.wav")
hot24 = os.path.join(folder, "hot24.wav")
hot32 = os.path.join(folder, "hot32.wav")
calm = os.path.join(folder, "calm.wav")
sides = os.path.join(folder, "sides.wav")
made = 0
for path, gain, codec in ((hot16, "30dB", "pcm_s16le"),
                          (hot24, "30dB", "pcm_s24le"),
                          (hot32, "30dB", "pcm_f32le"),
                          (calm, "0.25", "pcm_s16le")):
    made += 1 if sine(path, gain, codec) else 0
made += 1 if two_sided(sides, "0.25", "30dB", "pcm_s16le") else 0

# Without numpy nothing is counted anywhere, and every "not counted"
# below would be green for that reason and not for its own. So it is
# asked first, and the red line says so rather than blaming a format.
check("numpy is there, or nothing at all could be counted",
      vpm.np is not None,
      "numpy %s" % ("loaded" if vpm.np is not None
                    else "missing -- pip install numpy"))
check("ffmpeg wrote every piece of material", made == 5,
      "%d of %d files written under %s" % (made, 5, folder))

a16 = vpm.clipping_facts(hot16)
a24 = vpm.clipping_facts(hot24)
a32 = vpm.clipping_facts(hot32)
quiet = vpm.clipping_facts(calm)
pair = vpm.clipping_facts(sides)
runs16, long16, ms16, _first = a16.get(0, NOTHING)
runs24, long24 = a24.get(0, NOTHING)[0], a24.get(0, NOTHING)[1]

check("16 bit against the stop is counted", runs16 >= 1,
      "%d runs on the first channel, wanted at least %d" % (runs16, 1))
check("24 bit counts exactly the same",
      runs24 >= 1 and (runs24, long24) == (runs16, long16),
      "24 bit %d runs / longest %d against 16 bit %d runs / longest %d"
      % (runs24, long24, runs16, long16))
# Float has no stop at full scale, so a peak above 0 dBFS is loud, not
# damaged, and a warning would be a warning about nothing.
check("32 bit float is not counted at all", a32 == {},
      "%d channels counted, wanted %d -- %s" % (len(a32), 0, a32))
check("and a quiet recording is left alone", quiet == {},
      "%d channels counted, wanted %d -- %s" % (len(quiet), 0, quiet))
check("only the channel that hit the stop is counted",
      sorted(pair) == [1],
      "channels counted %s, wanted [1] -- the loud side is the second"
      % (sorted(pair),))
# Three samples in a row is the whole threshold: one or two are
# rounding. A run reported as shorter than that was never a run.
check("a counted run is at least the three samples it takes",
      long16 >= 3, "longest run %d samples, wanted at least %d"
      % (long16, 3))
check("and its milliseconds are those samples at the file's own rate",
      abs(ms16 - long16 * 1000.0 / RATE) < 0.001,
      "%.4f ms reported, %.4f ms for %d samples at %d Hz"
      % (ms16, long16 * 1000.0 / RATE, long16, RATE))

if written(hot16) and written(sides):
    found, _rest = vpm.check_audio_file(hot16)
    hints = [b for b in found if b.kind == "hint"]
    aborts = [b for b in found if b.kind == "abort"]
    check("the preflight says so", len(hints) == 1,
          "%d hints for %d clipped channel, wanted %d"
          % (len(hints), 1, 1))
    check("as a hint, never a reason to stop", not aborts,
          "%d of %d findings would stop the run, wanted %d"
          % (len(aborts), len(found), 0))
    counted = vpm.group_text(runs16)
    check("and says how many, not just that it happened",
          bool(hints) and counted in hints[0].text,
          "looked for %s runs in: %s"
          % (counted, hints[0].text if hints else "no hint at all"))

    side_found, _rest = vpm.check_audio_file(sides)
    side_hints = [b for b in side_found if b.kind == "hint"]
    check("one clipped channel of two makes one hint, not two",
          len(side_hints) == 1,
          "%d hints for %d clipped channel of %d, wanted %d"
          % (len(side_hints), 1, 2, 1))
    # The user counts channels from one, the program keys them from
    # zero. The second channel is the loud one, so the hint says two.
    opening = vpm.T(
        'Channel %d is against the stop: %s times three samples or '
        'more in a row, the longest %s (%.1f ms), the first at %s.'
    ).split("%s")[0] % 2
    check("the hint counts channels from one, as a person does",
          bool(side_hints) and side_hints[0].text.startswith(opening),
          "wanted a hint opening on %s -- got %s"
          % (opening.strip(),
             side_hints[0].text[:60] if side_hints else "no hint at all"))
else:
    print("  LEFT OUT: the preflight, ffmpeg wrote no material to feed it")

print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
