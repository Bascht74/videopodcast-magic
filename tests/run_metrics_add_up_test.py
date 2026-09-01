# -*- coding: utf-8 -*-
"""The metrics CSV: does it hold what it should, and are the numbers right?

The file is what stays behind after a run, and the only place where before
and after stand side by side. The two tracks here are built at a known
level, so what the loudness rows must say is arithmetic, not opinion.

The shape of the file, the loudness rows, what was measured and only
that, gain and target and cut, speech time and colour. Every row is
asked for before its value is read: a row that is not there is a finding
of its own, and a number taken out of a row that is not there would end
the run instead of being reported.
"""
import os
HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = os.environ.get("VPM_SCRIPT") or os.path.join(
    os.path.dirname(HERE), "videopodcast-magic.py")
import importlib.util, csv, math, subprocess, sys, tempfile, time
began = time.time()
spec = importlib.util.spec_from_file_location("vpm", SCRIPT)
vpm = importlib.util.module_from_spec(spec); sys.modules["vpm"] = vpm
spec.loader.exec_module(vpm)
WORK = tempfile.mkdtemp(prefix="metrics_")
done = 0
bad = []


def check(name, ok, extra=""):
    global done
    done += 1
    print("  %-58s %s %s" % (name, "ok" if ok else "FAIL", extra))
    if not ok:
        bad.append("%s [%s]" % (name, extra or "no numbers"))


def track(name, hz, loud):
    path = os.path.join(WORK, name)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "lavfi",
                    "-i", "sine=frequency=%d:duration=20" % hz,
                    "-af", "volume=%g" % loud, "-ac", "1", "-ar", "48000",
                    "-c:a", "pcm_s24le", path], check=True)
    return path


# Both lifts are exact, so the difference between Before and After is known.
ANNA_LIFT = 20.0 * math.log10(0.5 / 0.05)
BERT_LIFT = 20.0 * math.log10(0.5 / 0.08)
tracks = [
    {"name": "Anna", "axis": track("a_raw.wav", 200, 0.05),
     "ready": track("a_ready.wav", 200, 0.5),
     "drift_ppm": -9.2, "offset_ms": 18.4, "residual_ms": 0.6},
    {"name": "Bert", "axis": track("b_raw.wav", 300, 0.08),
     "ready": track("b_ready.wav", 300, 0.5)},
]
cut = [(0.0, 12.0, "Anna"), (12.0, 15.0, "Wide"), (15.0, 40.0, "Bert")]
segments = [("Anna", [(0.0, 12.0)]), ("Bert", [(15.0, 40.0)])]


class Args(object):
    lufs = -16.0
    production = "Episode 12"
    no_metrics = False


colours = [("Camera 1", {"y": 124.0, "u": 129.8, "v": 125.4},
            (-13.1, 0.2, 0.5)),
           ("Camera 2", {"y": 150.2, "u": 129.4, "v": 124.4},
            (13.1, -0.2, -0.5))]
target = vpm.write_metrics_csv(os.path.join(WORK, "Episode12_metrics.csv"),
                               tracks, cut, segments, [], Args(), colours,
                               4.2)
print()
print("1. The file and its shape")
check("the file is there", os.path.exists(target),
      "wanted %s; the %d files in the folder are %s"
      % (os.path.basename(target), len(os.listdir(WORK)),
         sorted(os.listdir(WORK))))
with open(target, encoding="utf-8") as f:
    rows = list(csv.reader(f))
check("it has a header", rows and rows[0] == ["Area", "Metric", "Before",
                                              "After", "Unit"], str(rows[:1]))
check("every row has five columns", all(len(r) == 5 for r in rows),
      str([r for r in rows if len(r) != 5][:2]))
body = rows[1:]
check("and there is a body", len(body) > 20, str(len(body)))


def find(area, metric):
    for r in body:
        if r[0] == area and r[1] == metric:
            return r
    return None


def number(row, column):
    try:
        return float(row[column])
    except (TypeError, ValueError, IndexError):
        return None


def figure(area, metric, column=3):
    """One number out of the file, the row asked for before the value.

    A row that is not there answers None, and the check underneath then
    worked with that None: abs(None - 4.2) ends the run with a TypeError
    instead of a red line, no number is printed, and every check further
    down the file is lost with it. So being there is a judgement of its
    own and it stands first -- the red line then says the row is missing
    and which rows the file does carry, rather than naming a value that
    was never there to be wrong.
    """
    row = find(area, metric)
    got = number(row, column)
    here = [r[1] for r in body if r[0] == area]
    check("the %s row under %s carries a number" % (metric, area),
          got is not None,
          "row %s in column %d; the %d metrics under %s are %s"
          % (row, column, len(here), area, here))
    return got


print("\n2. The loudness rows say what was measured")
for who, lift in (("Anna", ANNA_LIFT), ("Bert", BERT_LIFT)):
    row = find("Audio %s" % who, "Loudness")
    mine = [r[1] for r in body if r[0] == "Audio %s" % who]
    check("%s has a loudness row" % who, row is not None,
          "row %s; the %d metrics under Audio %s are %s"
          % (row, len(mine), who, mine))
    if not row:
        continue
    before, after = number(row, 2), number(row, 3)
    check("%s: both figures are numbers" % who,
          before is not None and after is not None, str(row))
    if before is None or after is None:
        continue
    check("%s: the rise is the %.1f dB it was given" % (who, lift),
          abs((after - before) - lift) < 0.3,
          "%.1f dB measured" % (after - before))
    check("%s: the unit is LUFS" % who, row[4] == "LUFS", row[4])
    peak_was = figure("Audio %s" % who, "Peak", 2)
    peak_now = figure("Audio %s" % who, "Peak", 3)
    check("%s: the peak rose by the same amount" % who,
          peak_was is not None and peak_now is not None
          and abs((peak_now - peak_was) - lift) < 0.3,
          "%s dB against the %.1f dB it was given"
          % ("no number" if None in (peak_was, peak_now)
             else "%.1f" % (peak_now - peak_was), lift))

print("\n3. What was measured, and only that")
row = find("Audio Anna", "Clock drift")
check("Anna's clock drift is in there", row is not None and "-9.2" in row[2],
      str(row))
was = figure("Audio Anna", "Offset", 2)
now = figure("Audio Anna", "Offset", 3)
check("and her offset, before and after",
      was is not None and now is not None
      and abs(was - 18.4) < 0.01 and abs(now - 0.6) < 0.01,
      "%s ms and %s ms, wanted 18.4 ms and 0.6 ms" % (was, now))
drift = find("Audio Bert", "Clock drift")
check("Bert has no drift row -- nothing was measured for him",
      drift is None, "row %s, wanted none" % (drift,))
shift = find("Audio Bert", "Offset")
check("nor an offset row", shift is None, "row %s, wanted none" % (shift,))

print("\n4. Gain, target and cut")
gain = figure("Audio", "Gain on every track")
check("the gain that went on every track",
      gain is not None and abs(gain - 4.2) < 0.01,
      "gain %s dB, wanted 4.2 dB" % (gain,))
aim = figure("Audio", "Loudness target")
check("the loudness target", aim is not None and abs(aim + 16.0) < 0.01,
      "target %s LUFS, wanted -16.0 LUFS" % (aim,))
shots = figure("Cut", "Shots")
check("three shots", shots == 3, "%s shots, wanted 3" % (shots,))
middle = figure("Cut", "Median hold time")
check("median hold time is the middle one of 12, 3 and 25",
      middle is not None and abs(middle - 12.0) < 0.01,
      "%s s, wanted 12.0 s" % (middle,))
shortest = figure("Cut", "shortest")
check("the shortest is 3 s",
      shortest is not None and abs(shortest - 3.0) < 0.01,
      "shortest %s s, wanted 3.0 s" % (shortest,))
longest = figure("Cut", "longest")
check("the longest is 25 s",
      longest is not None and abs(longest - 25.0) < 0.01,
      "longest %s s, wanted 25.0 s" % (longest,))
shares = [number(r, 3) for r in body
          if r[0] == "Cut" and r[1].startswith("Share")]
check("three shares", len(shares) == 3, str(shares))
check("and every share is a number", bool(shares) and None not in shares,
      "%d of the %d share rows carry no number: %s"
      % (shares.count(None), len(shares), shares))
check("and they add up to a hundred",
      bool(shares) and None not in shares
      and abs(sum(shares) - 100.0) < 0.1,
      "%s, wanted 100.0" % (sum(s for s in shares if s is not None),))
his = figure("Cut", "Share Bert")
check("Bert holds the longest, so his share is the biggest",
      bool(shares) and None not in shares and his is not None
      and max(shares) == his,
      "Bert's share %s against the biggest of %s" % (his, shares))

print("\n5. Speech time and colour")
anna = figure("Speech time", "Anna")
check("Anna speaks for twelve seconds",
      anna is not None and abs(anna - 12.0) < 0.01,
      "%s s, wanted 12.0 s" % (anna,))
bert = figure("Speech time", "Bert")
check("Bert for twenty-five", bert is not None and abs(bert - 25.0) < 0.01,
      "%s s, wanted 25.0 s" % (bert,))
one = figure("Colour Camera 1", "Brightness")
two = figure("Colour Camera 2", "Brightness")
check("both cameras have a brightness", one == 124.0 and two == 150.2,
      "Camera 1 %s and Camera 2 %s, wanted 124.0 and 150.2" % (one, two))
off_one = figure("Colour Camera 1", "Distance to mean")
off_two = figure("Colour Camera 2", "Distance to mean")
check("and their distance to the mean is equal and opposite",
      off_one is not None and off_two is not None
      and abs(off_one + off_two) < 0.01,
      "%s and %s, which add to %s; wanted 0.0"
      % (off_one, off_two,
         None if None in (off_one, off_two) else off_one + off_two))

print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
