# -*- coding: utf-8 -*-
"""What came back from reading the AudioRecorder project.

Six things were built out of that comparison, and each one is here with
the case it was built for:

* the run says which copy of the script it is (several runnable copies
  of one version are the normal case here, and they share a log file),
* clipping is counted per channel -- and only where an integer format
  gives it a stop to count against,
* a failed measurement says how close it came instead of "not
  measurable",
* a channel that carries nothing says which of the two rules caught it,
  and by how much,
* the fit hands back what it could not explain instead of dropping it,
* a recording that crosses midnight is one night, not a day apart.

The clipping numbers here were measured, not assumed: the same
overdriven sine written three ways gives 120,720 samples on the stop in
16 bit and the same 120,720 in 24 bit, while the 32 bit float copy
peaks at +11.94 dBFS with nothing clipped at all. The line is integer
against float, not 16 against 24 bit.
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


print("1. The log says which copy of the script is running")
where = vpm.running_from()
check("an absolute path", os.path.isabs(where), where[:40])
check("and it is the file that was loaded",
      os.path.samefile(where, SCRIPT))

print("2. Clipping is counted, and only where there is a stop")
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
    # This is the whole point of the check. Float has no stop at full
    # scale, so a peak above 0 dBFS is loud, not damaged, and warning
    # about it would be warning about nothing.
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

print("3. A failed measurement says how close it came")
# Both branches carry their number now. Without it the two faults --
# everybody talking at once against bleed too weak to read -- look the
# same in the log, and they need different remedies.
check("three is the floor for a fit, and it is named",
      vpm.ENOUGH_WINDOWS == 3, str(vpm.ENOUGH_WINDOWS))
check("so is the sharpness a second has to reach",
      vpm.SHARP_ENOUGH == 10.0, str(vpm.SHARP_ENOUGH))
text = vpm.T('only %d seconds where %s speaks alone, %d needed') % (
    1, "Anna", vpm.ENOUGH_WINDOWS)
check("the thin-material line carries both numbers",
      "1" in text and "3" in text, text)
text = vpm.T('bleed too indistinct: %d of %d seconds usable, sharpest '
             '%.1f of %.0f needed') % (1, 9, 4.2, vpm.SHARP_ENOUGH)
check("and so does the indistinct-bleed line",
      "4.2" in text and "10" in text, text)

print("4. A channel that carries nothing says which rule caught it")
silent, why = vpm.channel_hush([-3.0, -60.0, -6.0])
check("45 dB under the loudest counts as unplugged",
      silent == [False, True, False], str(silent))
check("and the reason is the relative one",
      why[1][0] == "under" and abs(why[1][1] - 57.0) < 0.01, str(why[1]))
line = vpm.hush_reason(2, why)
check("the line names the gap, not a noise floor",
      "57" in line and "noise" not in line, line)
silent, why = vpm.channel_hush([-75.0, -71.0])
check("all quiet is judged on the relative rule alone",
      silent == [False, False], str(silent))
# The absolute rule only gets a turn where the relative one does not
# fire first: 31 dB down is not an unplugged input, but -71 dBFS is
# still nothing but the converter talking to itself.
silent, why = vpm.channel_hush([-40.0, -71.0])
check("a channel under -70 dBFS is converter noise",
      silent == [False, True] and why[1][0] == "quiet", str(why[1]))
check("and that line says the level",
      "-71" in vpm.hush_reason(2, why), vpm.hush_reason(2, why))
# It used to stand twice, word for word, in two functions 400 lines
# apart. Now it stands once and both call it.
source = open(SCRIPT, encoding="utf-8").read()
check("one rule, not the same rule typed twice",
      source.count("def channel_hush(") == 1
      and source.count("silent, why = channel_hush(level)") == 2,
      "%d definitions, %d callers"
      % (source.count("def channel_hush("),
         source.count("silent, why = channel_hush(level)")))

print("5. The fit hands back what it could not explain")
points = [(float(t), 10.0 + 0.0 * t) for t in range(8)]
m = {(0, 1): points, (1, 0): [(t, -v) for t, v in points]}
found = vpm.solve_pair_offsets(m, 0, 1)
check("five values come back now, not four",
      found is not None and len(found) == 5, str(found and len(found)))
check("a line that fits exactly leaves nothing over",
      found is not None and found[4] < 1e-6, "%.2e" % found[4])
noisy = list(points)
noisy[3] = (3.0, 40.0)
m = {(0, 1): noisy, (1, 0): [(t, -v) for t, v in points]}
found2 = vpm.solve_pair_offsets(m, 0, 1)
check("and a point out of line shows up in it",
      found2 is not None and found2[4] > 1.0, "%.2f ms" % found2[4])

print("6. Midnight is one night, not a day apart")
DAY = 24 * 3600
check("a value moves onto the axis of its neighbour",
      vpm.unwrap_day(600, 85800) == 600 + DAY)
check("and back the other way",
      vpm.unwrap_day(85800, 600) == 85800 - DAY)
check("nothing moves inside the same day",
      vpm.unwrap_day(3600, 3000) == 3600)
check("no timecode, nothing to do", vpm.unwrap_day(None, 5) is None)

cameras = [{"tc": 23 * 3600 + 50 * 60, "duration": 1800,
            "name": "CamA", "path": "a"},
           {"tc": 23 * 3600 + 50 * 60, "duration": 1800,
            "name": "CamB", "path": "b"},
           {"tc": 23 * 3600 + 52 * 60, "duration": 1700,
            "name": "CamC", "path": "c"}]

def about(tc, duration=900):
    return vpm.timecode_comparison(
        cameras + [{"tc": tc, "duration": duration,
                    "name": "Rec", "path": "d"}])

found = about(10 * 60)
check("a recording after midnight is not an unset clock",
      len(found) == 1 and found[0].field == vpm.T('Midnight'),
      "; ".join(b.text[:40] for b in found))
check("the same evening says nothing at all",
      about(23 * 3600 + 55 * 60) == [])
found = about(3 * 3600)
# The unwrap is only kept where it puts the file among the others. At
# 03:00 against cameras at 23:50 it does not, so the move is taken back
# and the old finding stands -- which is the right one.
check("a clock set to the wrong hour is still an unset clock",
      len(found) == 1 and "Timecode" in found[0].text,
      "; ".join(b.text[:40] for b in found))
found = about(0)
check("and 00:00:00 stays the unset clock it has always been",
      len(found) == 1 and "Timecode" in found[0].text,
      "; ".join(b.text[:40] for b in found))
check("a camera that restarts over midnight has no gap",
      vpm.unwrap_day(5.0, 86395.0 + 5.0) - (86395.0 + 5.0) == 0.0
      or abs(vpm.unwrap_day(5.0, 86390.0) - 86390.0 - 15.0) < 0.001)

print("7. --together keeps the order it was given")
paths = [os.path.join(folder, x)
         for x in ("Zulu.wav", "Alpha.wav", "Mike.wav")]
for p in paths:
    open(p, "wb").close()
out, _ = vpm.collect_with_continuations(
    paths, True, together=[paths])
check("the hand-forced row is not sorted by name",
      [os.path.basename(x) for x in out]
      == ["Zulu.wav", "Alpha.wav", "Mike.wav"],
      str([os.path.basename(x) for x in out]))
loose = os.path.join(folder, "Bravo.wav")
open(loose, "wb").close()
out, _ = vpm.collect_with_continuations(
    paths + [loose], True, together=[paths])
check("and it lands where its first-named member would",
      [os.path.basename(x) for x in out]
      == ["Zulu.wav", "Alpha.wav", "Mike.wav", "Bravo.wav"],
      str([os.path.basename(x) for x in out]))
out, _ = vpm.collect_with_continuations(paths + [loose], True)
check("without --together everything sorts by name",
      [os.path.basename(x) for x in out]
      == ["Alpha.wav", "Bravo.wav", "Mike.wav", "Zulu.wav"],
      str([os.path.basename(x) for x in out]))

print()
if error:
    print("FAIL: %d of the checks" % len(error))
    sys.exit(1)
print("All good.")
