# -*- coding: utf-8 -*-
"""Without Multitrack: the mix, and the recordings beside it.

Several microphones running at once are mixed into one track on the simple
path. Until now that was all the video got, and the separation was gone.
Now each recording also goes in on its own -- but only where they really
did run at the same time. Blocks laid end to end are one recording, and a
track per block would be silence with one block in it.
"""
import os
HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = os.environ.get("VPM_SCRIPT") or os.path.join(
    os.path.dirname(HERE), "videopodcast-magic.py")
import importlib.util, subprocess, sys, tempfile
import numpy as np
spec = importlib.util.spec_from_file_location("vpm", SCRIPT)
vpm = importlib.util.module_from_spec(spec); sys.modules["vpm"] = vpm
spec.loader.exec_module(vpm)
SR = vpm.SR
WORK = tempfile.mkdtemp(prefix="beside_")
bad = []


def check(what, ok, detail=""):
    print("%-58s %s%s" % (what, "ok" if ok else "FAIL",
                          "" if ok else "   " + detail))
    if not ok:
        bad.append(what)


def tone(name, hz, seconds, start_sample):
    """A wav carrying a timecode, so the join can place it."""
    path = os.path.join(WORK, name)
    subprocess.run(
        ["ffmpeg", "-v", "error", "-f", "lavfi", "-i",
         "sine=frequency=%d:sample_rate=%d:duration=%.3f" % (hz, SR, seconds),
         "-af", "volume=0.3", "-c:a", "pcm_s24le", "-write_bext", "1",
         "-metadata", "time_reference=%d" % start_sample, "-y", path],
        check=True)
    return path


#------------------------------------------------ two microphones at once
a = tone("Moderator_01.wav", 500, 4.0, 48000)
b = tone("Guest_01.wav", 900, 4.0, 48000 + 4800)     # 100 ms later
check("the timecode is written and read back",
      vpm.bext_time_reference(a) == 48000,
      "%s" % vpm.bext_time_reference(a))

mix, info = vpm.join_audio_parts([a, b], os.path.join(WORK, "joined.wav"),
                                 keep_parts=True)
check("the join finds the timecode", bool(info.get("tc")))
check("and sees that they overlap", bool(info.get("side_by_side")))
check("one single track per recording", len(info.get("parts") or []) == 2,
      "%d" % len(info.get("parts") or []))
for name, path in info.get("parts") or []:
    check("  %s is there and as long as the mix" % name,
          os.path.exists(path)
          and vpm.sample_count(path) == vpm.sample_count(mix),
          "%d against %d" % (vpm.sample_count(path) if os.path.exists(path)
                             else -1, vpm.sample_count(mix)))
names = [n for n, _p in info.get("parts") or []]
check("the names come from the files", names == ["Moderator", "Guest"],
      "%s" % names)


def peak_at(path, hz):
    """How much of one frequency is in a file, 0 to 1."""
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", path, "-f", "f32le",
                          "-ac", "1", "-ar", str(SR), "-"],
                         capture_output=True, check=True).stdout
    x = np.frombuffer(raw, dtype="<f4")
    spectrum = np.abs(np.fft.rfft(x * np.hanning(len(x))))
    k = int(round(hz * len(x) / float(SR)))
    return float(spectrum[k]) / (float(np.max(spectrum)) or 1.0)


first = dict(info["parts"])["Moderator"]
second = dict(info["parts"])["Guest"]
check("the first single track holds its own tone",
      peak_at(first, 500) > 0.9 and peak_at(first, 900) < 0.05,
      "%.2f / %.2f" % (peak_at(first, 500), peak_at(first, 900)))
check("the second holds the other one",
      peak_at(second, 900) > 0.9 and peak_at(second, 500) < 0.05,
      "%.2f / %.2f" % (peak_at(second, 900), peak_at(second, 500)))
check("the mix holds both",
      peak_at(mix, 500) > 0.5 and peak_at(mix, 900) > 0.5,
      "%.2f / %.2f" % (peak_at(mix, 500), peak_at(mix, 900)))

#-------------------------------------------------- blocks one after another
c = tone("Rec_01.wav", 500, 3.0, 48000)
d = tone("Rec_02.wav", 500, 3.0, 48000 + 3 * SR)
_m2, info2 = vpm.join_audio_parts([c, d], os.path.join(WORK, "joined2.wav"),
                                  keep_parts=True)
check("blocks in a row are not seen as overlapping",
      not info2.get("side_by_side"))
check("and get no single tracks", not info2.get("parts"))

#------------------------------------- two recorders started together
# Both write the same TimeReference, and both recordings run at the same
# time. Laying them end to end would be the worst answer of all.
same1 = tone("Together_A_01.wav", 500, 4.0, 48000)
same2 = tone("Together_B_01.wav", 900, 4.0, 48000)
mix2, info2 = vpm.join_audio_parts([same1, same2],
                                   os.path.join(WORK, "same.wav"),
                                   keep_parts=True)
check("the same timecode is still read as a timecode", bool(info2.get("tc")))
check("and they are placed on top of each other, not in a row",
      abs(vpm.sample_count(mix2) / float(SR) - 4.0) < 0.01,
      "%.2f s" % (vpm.sample_count(mix2) / float(SR)))
check("each still gets a track of its own",
      len(info2.get("parts") or []) == 2, str(info2.get("parts")))

#------------------------------------------------------------ the switch off
_m3, info3 = vpm.join_audio_parts([a, b], os.path.join(WORK, "joined3.wav"),
                                  keep_parts=False)
check("without keep_parts nothing extra is written", not info3.get("parts"))
check("but the mix is the same length",
      vpm.sample_count(_m3) == vpm.sample_count(mix),
      "%d against %d" % (vpm.sample_count(_m3), vpm.sample_count(mix)))

print()
if bad:
    print("FAIL: %d of the checks" % len(bad))
    sys.exit(1)
print("all checks passed")
