# -*- coding: utf-8 -*-
"""A file left out of a recording is named, with the reason.

Two ways of being left out: a file named by hand that cannot be
used, and a second name for the same moment that nothing joins.
Both went by without a word.
"""
import os
HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = os.environ.get("VPM_SCRIPT") or os.path.join(
    os.path.dirname(HERE), "videopodcast-magic.py")
import importlib.util, struct, sys, tempfile, wave
import numpy as np
spec = importlib.util.spec_from_file_location("vpm", SCRIPT)
vpm = importlib.util.module_from_spec(spec); sys.modules["vpm"] = vpm
spec.loader.exec_module(vpm)
WORK = tempfile.mkdtemp(prefix="whynotjoined_")
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


def long_silence(name, seconds):
    """A file of this length without the bytes -- only the length is read."""
    path = os.path.join(WORK, name)
    n = int(seconds * vpm.SR)
    with open(path, "wb") as f:
        f.write(b"RIFF" + struct.pack("<I", 36 + n * 2) + b"WAVE"
                + b"fmt " + struct.pack("<IHHIIHH", 16, 1, 1, vpm.SR,
                                        vpm.SR * 2, 2, 16)
                + b"data" + struct.pack("<I", n * 2))
        f.seek(n * 2 - 1, 1)
        f.write(b"\x00")
    return path


print("A file named by hand that cannot be used is said out loud")
solo = tone("r_260809_000030.wav", 300.0)
other = tone("x_260809_010000.wav", 300.0)
rows = vpm.group_recording_parts(
    [solo, other], together=[[solo, os.path.join(WORK, "nope.wav")]])
said = " ".join(why for _row, discarded in rows
                for _name, why in discarded) + " " + " ".join(
    name for _row, discarded in rows for name, _why in discarded)
check("the missing file is named", "nope.wav" in said, said[:160])

print("\nTwo file names for the same moment say why nothing was joined")
# Five minutes apart, so the trailing number cannot pass for a counter
# and only the clock rule could join the two.
long_silence("v_260808_140000.wav", 300.0)
long_silence("v_20260808_140000.wav", 300.0)
after = long_silence("v_260808_140500.wav", 300.0)
row, discarded = vpm.find_continuation_files(after)
check("neither of the two is taken", len(row) == 1, str(len(row)))
check("and the reason is given", bool(discarded), str(discarded))
check("naming both files",
      len([1 for name, _why in discarded if name.startswith("v_")]) >= 2,
      str(discarded))

print()
if bad:
    print("FAIL: %d of the checks" % len(bad))
    sys.exit(1)
print("all checks passed")
