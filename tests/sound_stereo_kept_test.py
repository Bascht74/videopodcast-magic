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


def side_gap(x):
    """The widest difference between the two sides, -1 where there is one side.

    Only for the failure line: a folded track has no second column, and
    -1 beside the channel count says that rather than raising.
    """
    return (float(np.max(np.abs(x[:, 0] - x[:, 1]))) if x.shape[1] >= 2
            else -1.0)


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
kept_one, kept_two = vpm.kept_channels(mono), vpm.kept_channels(stereo)
kept_four = vpm.kept_channels(four)
check("kept_channels: one channel stays one", kept_one == 1,
      "kept %d, wanted 1, out of %d in the file"
      % (kept_one, vpm.channel_count(mono)))
check("kept_channels: two channels stay two", kept_two == 2,
      "kept %d, wanted 2, out of %d in the file"
      % (kept_two, vpm.channel_count(stereo)))
check("kept_channels: four channels are folded to one", kept_four == 1,
      "kept %d, wanted 1, out of %d in the file"
      % (kept_four, vpm.channel_count(four)))
wide_mixed = vpm.widest_track([mono, stereo, mono])
wide_monos = vpm.widest_track([mono, mono])
check("widest_track: one stereo among monos gives two", wide_mixed == 2,
      "%d over mono, stereo, mono, wanted 2" % wide_mixed)
check("widest_track: only monos give one", wide_monos == 1,
      "%d over mono, mono, wanted 1" % wide_monos)
same2, same1 = vpm.channel_filter(2, 2), vpm.channel_filter(1, 1)
widen, fold = vpm.channel_filter(1, 2), vpm.channel_filter(2, 1)
check("channel_filter keeps what already fits",
      same2 == "anull" and same1 == "anull",
      "two to two %r and one to one %r, wanted 'anull' twice"
      % (same2, same1))
check("channel_filter writes the pan out for one to two",
      widen == "pan=stereo|c0=c0|c1=c0",
      "%r against 'pan=stereo|c0=c0|c1=c0'" % widen)
check("and a half-and-half sum for two to one",
      fold == "pan=mono|c0=0.5*c0+0.5*c1",
      "%r against 'pan=mono|c0=0.5*c0+0.5*c1'" % fold)

#------------------------------------------------- one to two without a loss
widened = os.path.join(WORK, "widened.wav")
subprocess.run(["ffmpeg", "-v", "error", "-i", mono, "-af",
                vpm.channel_filter(1, 2), "-c:a", "pcm_s24le", "-y",
                widened], check=True)
gap = peak_db(read(widened)) - peak_db(read(mono))
check("one channel to two keeps the level", abs(gap) < 0.05,
      "%.2f dB off, at most 0.05" % gap)
plain = os.path.join(WORK, "plain.wav")
subprocess.run(["ffmpeg", "-v", "error", "-i", mono, "-ac", "2",
                "-c:a", "pcm_s24le", "-y", plain], check=True)
loss = peak_db(read(mono)) - peak_db(read(plain))
check("and ffmpeg's own conversion would not (that is why)", loss > 2.5,
      "%.2f dB lost, wanted more than 2.5" % loss)

#--------------------------------------------- and two to one likewise
both = write(os.path.join(WORK, "dual.wav"), [mid, mid])
narrowed = os.path.join(WORK, "narrowed.wav")
subprocess.run(["ffmpeg", "-v", "error", "-i", both, "-af",
                vpm.channel_filter(2, 1), "-c:a", "pcm_s24le", "-y",
                narrowed], check=True)
gap = peak_db(read(narrowed)) - peak_db(read(both))
check("two channels to one keeps the level", abs(gap) < 0.05,
      "%.2f dB off, at most 0.05" % gap)
# In float -- what a filter graph runs in -- ffmpeg's own conversion
# adds 3 dB here; writing integers it scales the matrix down so the sum
# cannot clip and the level comes out right. Same call, two answers.
plain1 = os.path.join(WORK, "plain1.wav")
subprocess.run(["ffmpeg", "-v", "error", "-i", both, "-ac", "1",
                "-c:a", "pcm_f32le", "-y", plain1], check=True)
rise = peak_db(read(plain1)) - peak_db(read(both))
check("and ffmpeg's own conversion would raise it in float (that is why)",
      rise > 2.5, "%.2f dB gained, wanted more than 2.5" % rise)
plain1i = os.path.join(WORK, "plain1i.wav")
subprocess.run(["ffmpeg", "-v", "error", "-i", both, "-ac", "1",
                "-c:a", "pcm_s24le", "-y", plain1i], check=True)
same = peak_db(read(plain1i)) - peak_db(read(both))
check("while in integers it would not -- the trap is the format",
      abs(same) < 0.05, "%.2f dB apart, at most 0.05" % same)

#---------------------------------------------------- place_track_on_axis
axis_stereo = vpm.place_track_on_axis(
    stereo, os.path.join(WORK, "axis_stereo.wav"), 0.0, 1.0, 0.0, 4.0)
x = read(axis_stereo)
check("on the axis a stereo track keeps two channels", x.shape[1] == 2,
      "%d channels, wanted 2" % x.shape[1])
check("and the two sides still differ",
      x.shape[1] == 2 and side_gap(x) > 0.05,
      "%d channels, sides apart by %.4f, wanted 2 channels apart by more "
      "than 0.05" % (x.shape[1], side_gap(x)))
check("the window is the length asked for",
      abs(x.shape[0] - int(4.0 * SR)) <= 1,
      "%d samples against the %d asked for, at most 1 apart"
      % (x.shape[0], int(4.0 * SR)))
axis_mono = vpm.place_track_on_axis(
    mono, os.path.join(WORK, "axis_mono.wav"), 0.0, 1.0, 0.0, 4.0)
on_axis_mono = read(axis_mono)
check("on the axis a mono track stays mono", on_axis_mono.shape[1] == 1,
      "%d channels, wanted 1, out of %d in the source"
      % (on_axis_mono.shape[1], vpm.channel_count(mono)))
axis_four = vpm.place_track_on_axis(
    four, os.path.join(WORK, "axis_four.wav"), 0.0, 1.0, 0.0, 4.0)
on_axis_four = read(axis_four)
check("a four channel file is folded, not passed on",
      on_axis_four.shape[1] == 1,
      "%d channels, wanted 1, out of %d in the source"
      % (on_axis_four.shape[1], vpm.channel_count(four)))

#------------------------------------------------------------- mix_tracks
mix = vpm.mix_tracks([axis_mono, axis_stereo],
                     os.path.join(WORK, "mix.wav"), channels=2)
m = read(mix)
check("a mix holding a stereo track has two channels", m.shape[1] == 2,
      "%d channels, wanted 2" % m.shape[1])
check("and the sides of the stereo track survive it",
      m.shape[1] == 2 and side_gap(m) > 0.05,
      "%d channels, sides apart by %.4f, wanted 2 channels apart by more "
      "than 0.05" % (m.shape[1], side_gap(m)))

only_mono = vpm.mix_tracks([axis_mono], os.path.join(WORK, "onlymono.wav"),
                           channels=2)
gap = peak_db(read(only_mono)) - peak_db(on_axis_mono)
check("a mono track alone in a two channel mix keeps its level",
      abs(gap) < 0.05, "%.2f dB off, at most 0.05" % gap)

single = vpm.mix_tracks([axis_stereo],
                        os.path.join(WORK, "single_stereo.wav"))
alone = read(single)
check("a single stereo track is not folded on its own line",
      alone.shape[1] == 2, "%d channels, wanted 2" % alone.shape[1])
handed_back = vpm.mix_tracks([axis_mono],
                             os.path.join(WORK, "single_mono.wav"))
check("a single mono track needs no pass at all", handed_back == axis_mono,
      "handed back %s, wanted the source itself %s"
      % (handed_back, axis_mono))

#----------------------------------------------------- the limiter curve
curve, gone = vpm.limiter_curve(mix, WORK, 12.0)
check("a two channel sum gives a two channel curve",
      curve is not None and vpm.channel_count(curve) == 2,
      "no curve at all, wanted one of 2 channels" if curve is None
      else "%d channels, wanted 2" % vpm.channel_count(curve))
if curve:
    with_curve = vpm.mix_tracks([axis_mono],
                                os.path.join(WORK, "curved.wav"),
                                0.0, curve)
    c = read(with_curve)
    check("a mono track under a two channel curve stays mono",
          c.shape[1] == 1, "%d channels, wanted 1" % c.shape[1])
    quiet = peak_db(on_axis_mono) - peak_db(c)
    # The curve only takes away; more than the limiter itself found
    # would mean a channel conversion crept in.
    check("and loses no more than the limiter asked for",
          -0.05 <= quiet <= gone + 0.05,
          "%.2f dB quieter, wanted between -0.05 and %.2f"
          % (quiet, gone + 0.05))

#-------------------------------------------------- what auphonic is asked for
def formats(_key, find, avoid=()):
    return {"format": "wav", "ending": "wav"}


old = vpm.find_output_format
vpm.find_output_format = formats
try:
    all_mono = vpm.master_output_format("x", False)
    one_stereo = vpm.master_output_format("x", True)
    check("the yardstick is one channel while everything is mono",
          bool(all_mono) and all_mono.get("mono_mixdown") is True,
          "mono_mixdown %r, wanted True; the entry was %r"
          % ((all_mono or {}).get("mono_mixdown"), all_mono))
    check("and two as soon as one track is stereo",
          bool(one_stereo) and one_stereo.get("mono_mixdown") is False,
          "mono_mixdown %r, wanted False; the entry was %r"
          % ((one_stereo or {}).get("mono_mixdown"), one_stereo))
finally:
    vpm.find_output_format = old

print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
