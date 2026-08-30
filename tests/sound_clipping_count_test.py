# -*- coding: utf-8 -*-
"""Clipping is counted per channel, and only where the format has a stop.

An integer format has a highest value, and samples sitting on it were
cut off. Float has no such stop, so a peak above 0 dBFS there is loud,
not damaged, and counting it would warn about nothing.
"""
import os
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = os.environ.get("VPM_SCRIPT") or os.path.join(
    os.path.dirname(HERE), "videopodcast-magic.py")
os.environ["VPM_NO_UPDATE_CHECK"] = "1"
import importlib.util
spec = importlib.util.spec_from_file_location("vpm", SCRIPT)
vpm = importlib.util.module_from_spec(spec); sys.modules["vpm"] = vpm
spec.loader.exec_module(vpm)

error = []
def check(name, ok, extra=""):
    print("  %-52s %s %s" % (name, "ok" if ok else "FAIL", extra))
    if not ok:
        error.append(name)


def sine(path, gain, codec):
    """One second of a sine at a chosen gain, in a chosen format."""
    subprocess.run(
        ["ffmpeg", "-y", "-v", "error", "-f", "lavfi",
         "-i", "sine=frequency=440:duration=2:sample_rate=48000",
         "-af", "volume=%s" % gain, "-c:a", codec, path],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return os.path.exists(path) and os.path.getsize(path) > 1000


have_ffmpeg = True
folder = tempfile.mkdtemp(prefix="vpm_clip_")
hot16 = os.path.join(folder, "hot16.wav")
hot24 = os.path.join(folder, "hot24.wav")
hot32 = os.path.join(folder, "hot32.wav")
calm = os.path.join(folder, "calm.wav")
for path, gain, codec in ((hot16, "30dB", "pcm_s16le"),
                          (hot24, "30dB", "pcm_s24le"),
                          (hot32, "30dB", "pcm_f32le"),
                          (calm, "0.25", "pcm_s16le")):
    if not sine(path, gain, codec):
        have_ffmpeg = False
if not have_ffmpeg:
    print("  (no ffmpeg -- skipped)")
else:
    a16 = vpm.clipping_facts(hot16)
    a24 = vpm.clipping_facts(hot24)
    a32 = vpm.clipping_facts(hot32)
    quiet = vpm.clipping_facts(calm)
    check("16 bit against the stop is counted", bool(a16), str(a16))
    check("24 bit counts exactly the same",
          bool(a24) and a24[0][1] == a16[0][1],
          "%s vs %s" % (a24.get(0), a16.get(0)))
    # Float has no stop at full scale, so a peak above 0 dBFS is loud,
    # not damaged, and a warning would be a warning about nothing.
    check("32 bit float is not counted at all", a32 == {}, str(a32))
    check("and a quiet recording is left alone", quiet == {}, str(quiet))
    found, _ = vpm.check_audio_file(hot16)
    hints = [b for b in found if b.kind == "hint"]
    check("the preflight says so", len(hints) == 1,
          hints[0].text if hints else "nothing")
    check("as a hint, never a reason to stop",
          all(b.kind != "abort" for b in found))
    check("and says how many, not just that it happened",
          bool(hints) and any(c.isdigit() for c in hints[0].text))

print()
if error:
    print("FAIL: %d of the checks" % len(error))
    sys.exit(1)
print("All good.")
