# -*- coding: utf-8 -*-
"""Stereo stays stereo: on the axis, in the single track, in the mix.

Every step that folds a stereo track to one channel throws the two
microphones away for good, so each step is measured rather than
trusted: the channel count, and whether the sides still differ. Levels
too -- ffmpeg's own mono to stereo conversion loses 3 dB, inaudible in
one listen and wrong in every meter.
"""
import os
HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = os.environ.get("VPM_SCRIPT") or os.path.join(
    os.path.dirname(HERE), "videopodcast-magic.py")
import importlib.util, struct, subprocess, sys, tempfile, time
import numpy as np
spec = importlib.util.spec_from_file_location("vpm", SCRIPT)
vpm = importlib.util.module_from_spec(spec); sys.modules["vpm"] = vpm
spec.loader.exec_module(vpm)
SR = vpm.SR
WORK = tempfile.mkdtemp(prefix="stereomix_")
DURATION = 6.0
n = int(DURATION * SR)
began = time.time()
done = 0
bad = []


def write(path, columns):
    """Write float columns as a 16 bit wav, one column per channel."""
    x = np.stack(columns, axis=1) if len(columns) > 1 else \
        np.asarray(columns[0]).reshape(-1, 1)
    ch = x.shape[1]
    b = (np.clip(x, -1, 1) * 32767).astype("<i2").tobytes()
    with open(path, "wb") as f:
        f.write(b"RIFF" + struct.pack("<I", 36 + len(b)) + b"WAVE")
        f.write(b"fmt " + struct.pack("<IHHIIHH", 16, 1, ch, SR,
                                      SR * 2 * ch, 2 * ch, 16))
        f.write(b"data" + struct.pack("<I", len(b)) + b)
    return path


def read(path):
    """Read a file back as one column per channel."""
    ch = vpm.channel_count(path)
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", path,
                          "-f", "f32le", "-ac", str(ch), "-ar", str(SR), "-"],
                         capture_output=True, check=True).stdout
    return np.frombuffer(raw, dtype="<f4").reshape(-1, ch)


def peak_db(x):
    top = float(np.max(np.abs(x))) if x.size else 0.0
    return 20.0 * np.log10(top) if top > 0 else -120.0


def check(name, ok, extra=""):
    global done
    done += 1
    print("  %-58s %s %s" % (name, "ok" if ok else "FAIL", extra))
    if not ok:
        bad.append("%s [%s]" % (name, extra or "no numbers"))


t = np.arange(n) / float(SR)
left = 0.5 * np.sin(2 * np.pi * 1000 * t)
right = 0.25 * np.sin(2 * np.pi * 400 * t)
mid = 0.4 * np.sin(2 * np.pi * 700 * t)

stereo = write(os.path.join(WORK, "stereo.wav"), [left, right])
mono = write(os.path.join(WORK, "mono.wav"), [mid])
four = write(os.path.join(WORK, "four.wav"), [left, right, mid, mid * 0.5])

#--------------------------------------------------------------- the helpers
check("kept_channels: one channel stays one",
      vpm.kept_channels(mono) == 1)
check("kept_channels: two channels stay two",
      vpm.kept_channels(stereo) == 2)
check("kept_channels: four channels are folded to one",
      vpm.kept_channels(four) == 1,
      "got %d" % vpm.kept_channels(four))
check("widest_track: one stereo among monos gives two",
      vpm.widest_track([mono, stereo, mono]) == 2)
check("widest_track: only monos give one",
      vpm.widest_track([mono, mono]) == 1)
check("channel_filter keeps what already fits",
      vpm.channel_filter(2, 2) == "anull"
      and vpm.channel_filter(1, 1) == "anull")
check("channel_filter writes the pan out for one to two",
      vpm.channel_filter(1, 2) == "pan=stereo|c0=c0|c1=c0")
check("and a half-and-half sum for two to one",
      vpm.channel_filter(2, 1) == "pan=mono|c0=0.5*c0+0.5*c1")

#------------------------------------------------- one to two without a loss
widened = os.path.join(WORK, "widened.wav")
subprocess.run(["ffmpeg", "-v", "error", "-i", mono, "-af",
                vpm.channel_filter(1, 2), "-c:a", "pcm_s24le", "-y",
                widened], check=True)
gap = peak_db(read(widened)) - peak_db(read(mono))
check("one channel to two keeps the level", abs(gap) < 0.05,
      "%.2f dB off" % gap)
plain = os.path.join(WORK, "plain.wav")
subprocess.run(["ffmpeg", "-v", "error", "-i", mono, "-ac", "2",
                "-c:a", "pcm_s24le", "-y", plain], check=True)
loss = peak_db(read(mono)) - peak_db(read(plain))
check("and ffmpeg's own conversion would not (that is why)", loss > 2.5,
      "only %.2f dB" % loss)

#--------------------------------------------- and two to one likewise
both = write(os.path.join(WORK, "dual.wav"), [mid, mid])
narrowed = os.path.join(WORK, "narrowed.wav")
subprocess.run(["ffmpeg", "-v", "error", "-i", both, "-af",
                vpm.channel_filter(2, 1), "-c:a", "pcm_s24le", "-y",
                narrowed], check=True)
gap = peak_db(read(narrowed)) - peak_db(read(both))
check("two channels to one keeps the level", abs(gap) < 0.05,
      "%.2f dB off" % gap)
# In float -- what a filter graph runs in -- ffmpeg's own conversion
# adds 3 dB here; writing integers it scales the matrix down so the sum
# cannot clip and the level comes out right. Same call, two answers.
plain1 = os.path.join(WORK, "plain1.wav")
subprocess.run(["ffmpeg", "-v", "error", "-i", both, "-ac", "1",
                "-c:a", "pcm_f32le", "-y", plain1], check=True)
rise = peak_db(read(plain1)) - peak_db(read(both))
check("and ffmpeg's own conversion would raise it in float (that is why)",
      rise > 2.5, "only %.2f dB" % rise)
plain1i = os.path.join(WORK, "plain1i.wav")
subprocess.run(["ffmpeg", "-v", "error", "-i", both, "-ac", "1",
                "-c:a", "pcm_s24le", "-y", plain1i], check=True)
same = peak_db(read(plain1i)) - peak_db(read(both))
check("while in integers it would not -- the trap is the format",
      abs(same) < 0.05, "%.2f dB" % same)

#---------------------------------------------------- place_track_on_axis
axis_stereo = vpm.place_track_on_axis(
    stereo, os.path.join(WORK, "axis_stereo.wav"), 0.0, 1.0, 0.0, 4.0)
x = read(axis_stereo)
check("on the axis a stereo track keeps two channels", x.shape[1] == 2,
      "got %d" % x.shape[1])
check("and the two sides still differ",
      x.shape[1] == 2 and float(np.max(np.abs(x[:, 0] - x[:, 1]))) > 0.05)
check("the window is the length asked for",
      abs(x.shape[0] - int(4.0 * SR)) <= 1)
axis_mono = vpm.place_track_on_axis(
    mono, os.path.join(WORK, "axis_mono.wav"), 0.0, 1.0, 0.0, 4.0)
check("on the axis a mono track stays mono",
      read(axis_mono).shape[1] == 1)
axis_four = vpm.place_track_on_axis(
    four, os.path.join(WORK, "axis_four.wav"), 0.0, 1.0, 0.0, 4.0)
check("a four channel file is folded, not passed on",
      read(axis_four).shape[1] == 1)

#------------------------------------------------------------- mix_tracks
mix = vpm.mix_tracks([axis_mono, axis_stereo],
                     os.path.join(WORK, "mix.wav"), channels=2)
m = read(mix)
check("a mix holding a stereo track has two channels", m.shape[1] == 2)
check("and the sides of the stereo track survive it",
      m.shape[1] == 2 and float(np.max(np.abs(m[:, 0] - m[:, 1]))) > 0.05)

only_mono = vpm.mix_tracks([axis_mono], os.path.join(WORK, "onlymono.wav"),
                           channels=2)
gap = peak_db(read(only_mono)) - peak_db(read(axis_mono))
check("a mono track alone in a two channel mix keeps its level",
      abs(gap) < 0.05, "%.2f dB off" % gap)

single = vpm.mix_tracks([axis_stereo],
                        os.path.join(WORK, "single_stereo.wav"))
check("a single stereo track is not folded on its own line",
      read(single).shape[1] == 2)
check("a single mono track needs no pass at all",
      vpm.mix_tracks([axis_mono], os.path.join(WORK, "single_mono.wav"))
      == axis_mono)

#----------------------------------------------------- the limiter curve
curve, gone = vpm.limiter_curve(mix, WORK, 12.0)
check("a two channel sum gives a two channel curve",
      curve is not None and vpm.channel_count(curve) == 2,
      "" if curve is None else "%d channels" % vpm.channel_count(curve))
if curve:
    with_curve = vpm.mix_tracks([axis_mono],
                                os.path.join(WORK, "curved.wav"),
                                0.0, curve)
    c = read(with_curve)
    check("a mono track under a two channel curve stays mono",
          c.shape[1] == 1, "got %d" % c.shape[1])
    quiet = peak_db(read(axis_mono)) - peak_db(c)
    # The curve only takes away; more than the limiter itself found
    # would mean a channel conversion crept in.
    check("and loses no more than the limiter asked for",
          -0.05 <= quiet <= gone + 0.05,
          "%.2f dB against at most %.2f" % (quiet, gone))

#-------------------------------------------------- what auphonic is asked for
def formats(_key, find, avoid=()):
    return {"format": "wav", "ending": "wav"}


old = vpm.find_output_format
vpm.find_output_format = formats
try:
    check("the yardstick is one channel while everything is mono",
          vpm.master_output_format("x", False)["mono_mixdown"] is True)
    check("and two as soon as one track is stereo",
          vpm.master_output_format("x", True)["mono_mixdown"] is False)
finally:
    vpm.find_output_format = old

print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
