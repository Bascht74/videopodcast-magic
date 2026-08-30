# -*- coding: utf-8 -*-
"""Audio blocks are joined in the order they were handed over.

One of the defects an adversarial review turned up. The two file names
below run against the alphabet on purpose: sorted rather than taken as
handed over, the joined file comes back the other way round.
"""
import os
HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = os.environ.get("VPM_SCRIPT") or os.path.join(
    os.path.dirname(HERE), "videopodcast-magic.py")
import importlib.util, subprocess, sys, tempfile, wave
import numpy as np
spec = importlib.util.spec_from_file_location("vpm", SCRIPT)
vpm = importlib.util.module_from_spec(spec); sys.modules["vpm"] = vpm
spec.loader.exec_module(vpm)
WORK = tempfile.mkdtemp(prefix="joinorder_")
bad = []
RATE = 48000


def check(what, ok, detail=""):
    print("  %-58s %s%s" % (what, "ok" if ok else "FAIL",
                            "" if ok else "   " + detail))
    if not ok:
        bad.append(what)


def tone(name, hz, seconds=1.0):
    path = os.path.join(WORK, name)
    t = np.arange(int(seconds * RATE)) / float(RATE)
    x = (0.5 * np.sin(2 * np.pi * hz * t) * 32767).astype("<i2")
    with wave.open(path, "wb") as f:
        f.setnchannels(1); f.setsampwidth(2); f.setframerate(RATE)
        f.writeframes(x.tobytes())
    return path


first = tone("zz_first.wav", 440.0)
second = tone("aa_second.wav", 1500.0)
target = os.path.join(WORK, "joined.wav")
vpm.join_audio_parts([first, second], target)


def loudest_hz(path, from_s, to_s):
    """The strongest frequency in this stretch, read through ffmpeg.

    Python's wave module refuses the joined file, 24 bit extensible.
    """
    out = subprocess.run(
        ["ffmpeg", "-v", "error", "-ss", "%.3f" % from_s, "-t",
         "%.3f" % (to_s - from_s), "-i", path, "-ac", "1", "-ar",
         str(RATE), "-f", "s16le", "-"], check=True,
        capture_output=True).stdout
    x = np.frombuffer(out, "<i2").astype(float)
    spectrum = np.abs(np.fft.rfft(x * np.hanning(len(x))))
    return np.fft.rfftfreq(len(x), 1.0 / RATE)[int(np.argmax(spectrum))]


a = loudest_hz(target, 0.1, 0.9)
b = loudest_hz(target, 1.1, 1.9)
check("the first named file is first", abs(a - 440.0) < 20.0, "%.0f Hz" % a)
check("the second one second", abs(b - 1500.0) < 20.0, "%.0f Hz" % b)

print()
if bad:
    print("FAIL: %d of the checks" % len(bad))
    sys.exit(1)
print("all checks passed")
