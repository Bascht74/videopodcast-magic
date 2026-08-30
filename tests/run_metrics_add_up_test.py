# -*- coding: utf-8 -*-
"""The metrics CSV: does it hold what it should, and are the numbers right?

The file is what stays behind after a run, and the only place where before
and after stand side by side. The two tracks here are built at a known
level, so what the loudness rows must say is arithmetic, not opinion.
"""
import os
HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = os.environ.get("VPM_SCRIPT") or os.path.join(
    os.path.dirname(HERE), "videopodcast-magic.py")
import importlib.util, csv, math, subprocess, sys, tempfile
spec = importlib.util.spec_from_file_location("vpm", SCRIPT)
vpm = importlib.util.module_from_spec(spec); sys.modules["vpm"] = vpm
spec.loader.exec_module(vpm)
WORK = tempfile.mkdtemp(prefix="metrics_")
bad = []


def check(what, ok, detail=""):
    print("  %-54s %s%s" % (what, "ok" if ok else "FAIL",
                            "" if ok else "   " + detail))
    if not ok:
        bad.append(what)


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
check("the file is there", os.path.exists(target))
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


print("\n2. The loudness rows say what was measured")
for who, lift in (("Anna", ANNA_LIFT), ("Bert", BERT_LIFT)):
    row = find("Audio %s" % who, "Loudness")
    check("%s has a loudness row" % who, row is not None)
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
    peak = find("Audio %s" % who, "Peak")
    check("%s: the peak rose by the same amount" % who,
          peak is not None
          and abs((number(peak, 3) - number(peak, 2)) - lift) < 0.3,
          str(peak))

print("\n3. What was measured, and only that")
row = find("Audio Anna", "Clock drift")
check("Anna's clock drift is in there", row is not None and "-9.2" in row[2],
      str(row))
row = find("Audio Anna", "Offset")
check("and her offset, before and after", row is not None
      and abs(number(row, 2) - 18.4) < 0.01
      and abs(number(row, 3) - 0.6) < 0.01, str(row))
check("Bert has no drift row -- nothing was measured for him",
      find("Audio Bert", "Clock drift") is None)
check("nor an offset row", find("Audio Bert", "Offset") is None)

print("\n4. Gain, target and cut")
check("the gain that went on every track",
      abs(number(find("Audio", "Gain on every track"), 3) - 4.2) < 0.01)
check("the loudness target", abs(number(find("Audio", "Loudness target"), 3)
                                 + 16.0) < 0.01)
check("three shots", number(find("Cut", "Shots"), 3) == 3)
check("median hold time is the middle one of 12, 3 and 25",
      abs(number(find("Cut", "Median hold time"), 3) - 12.0) < 0.01,
      str(find("Cut", "Median hold time")))
check("the shortest is 3 s", abs(number(find("Cut", "shortest"), 3) - 3.0)
      < 0.01)
check("the longest is 25 s", abs(number(find("Cut", "longest"), 3) - 25.0)
      < 0.01)
shares = [number(r, 3) for r in body
          if r[0] == "Cut" and r[1].startswith("Share")]
check("three shares", len(shares) == 3, str(shares))
check("and they add up to a hundred", abs(sum(shares) - 100.0) < 0.1,
      str(sum(shares)))
check("Bert holds the longest, so his share is the biggest",
      max(shares) == number(find("Cut", "Share Bert"), 3), str(shares))

print("\n5. Speech time and colour")
check("Anna speaks for twelve seconds",
      abs(number(find("Speech time", "Anna"), 3) - 12.0) < 0.01)
check("Bert for twenty-five",
      abs(number(find("Speech time", "Bert"), 3) - 25.0) < 0.01)
check("both cameras have a brightness",
      number(find("Colour Camera 1", "Brightness"), 3) == 124.0
      and number(find("Colour Camera 2", "Brightness"), 3) == 150.2)
check("and their distance to the mean is equal and opposite",
      abs(number(find("Colour Camera 1", "Distance to mean"), 3)
          + number(find("Colour Camera 2", "Distance to mean"), 3)) < 0.01)

print()
if bad:
    print("FAIL: %d of the checks" % len(bad))
    sys.exit(1)
print("All good.")
