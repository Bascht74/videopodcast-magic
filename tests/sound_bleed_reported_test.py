# -*- coding: utf-8 -*-
"""How much of each speaker sits in the other microphone.

The 3:1 rule of thumb puts the neighbour about 10 dB down: a clip-on
microphone three times closer to its own speaker than to the next. The
material is built with a known amount of bleed and read back out of the
written files first, so a figure that comes out wrong belongs to the
program and not to the material.

Three pairs in turn, two comfortably apart and one too close. Of each:
that the files really carry the bleed they were built with, that both
directions appear in the report, that each figure is the one built in,
and that the wide pairs are called good where the close one draws a
warning. Then one microphone on its own, which has nothing to compare
and says nothing.

The report's figures are medians over a few windows, so they are held to
a tolerance rather than read off exactly.
"""
import os
HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = os.environ.get("VPM_SCRIPT") or os.path.join(
    os.path.dirname(HERE), "videopodcast_magic.py")
import importlib.util, re, sys, tempfile, time, wave
import numpy as np
spec = importlib.util.spec_from_file_location("vpm", SCRIPT)
vpm = importlib.util.module_from_spec(spec); sys.modules["vpm"] = vpm
spec.loader.exec_module(vpm)
# The report is read as text below, so the language it is written in has
# to be settled here rather than left to whatever the machine says.
vpm.set_language("en")
# check_crosstalk decodes down to 16 kHz before it measures, so a higher
# rate only buys a resampling step; the voices here reach 570 Hz at most.
SR = 16000
# Five windows of at least 4 s each, and under twice one window the
# program refuses. 16 s holds eight whole turns, so no window cuts one
# in half; a half turn drags the reading down.
DURATION, TURN = 16, 2
# What the material may be out by, and what the report may be out by.
# The material is arithmetic and should sit on the number; the report is
# a median over a few windows and is allowed a wider margin.
BUILT_SLACK, REPORT_SLACK = 1.0, 1.5
WORK = tempfile.mkdtemp(prefix="bleed_")
began = time.time()
done = 0
bad = []


def check(name, ok, extra=""):
    global done
    done += 1
    print("  %-58s %s %s" % (name, "ok" if ok else "FAIL", extra))
    if not ok:
        bad.append("%s [%s]" % (name, extra or "no numbers"))


def voice(seconds, base_hz):
    """A speech-like signal: a fundamental under a changing envelope."""
    t = np.arange(int(seconds * SR)) / float(SR)
    swell = 0.5 + 0.5 * np.sin(2 * np.pi * 3.1 * t)
    return swell * (np.sin(2 * np.pi * base_hz * t)
                    + 0.5 * np.sin(2 * np.pi * 2 * base_hz * t)
                    + 0.3 * np.sin(2 * np.pi * 3 * base_hz * t)) / 1.8


# The same two turns every time, so they are built once, not per pair.
TURN_A, TURN_B = voice(TURN, 130), voice(TURN, 190)


def write(path, x):
    with wave.open(path, "w") as f:
        f.setnchannels(1)
        f.setsampwidth(2)
        f.setframerate(SR)
        f.writeframes(
            np.clip(x * 20000, -32000, 32000).astype("<i2").tobytes())
    return path


def pair(bleed_db, folder):
    """Two microphones, each hearing the other this much quieter."""
    n, step = DURATION * SR, TURN * SR
    a, b = np.zeros(n), np.zeros(n)
    quieter = 10 ** (bleed_db / 20.0)
    for k in range(DURATION // TURN):
        start = k * step
        piece = TURN_A if k % 2 == 0 else TURN_B
        if k % 2 == 0:
            a[start:start + step] = piece
            b[start:start + step] = piece * quieter
        else:
            b[start:start + step] = piece
            a[start:start + step] = piece * quieter
    # A little noise, so nothing is digitally silent.
    rng = np.random.default_rng(7)
    a += rng.uniform(-1, 1, n) * 0.0005
    b += rng.uniform(-1, 1, n) * 0.0005
    os.makedirs(folder, exist_ok=True)
    return (write(os.path.join(folder, "Anna.wav"), a),
            write(os.path.join(folder, "Bert.wav"), b))


def bleed_in(paths):
    """How many dB down each voice sits in the other file, both ways.

    Read back out of the written files, so what is measured is what the
    program will be handed -- and by a different route than the program
    takes: the plain level over the one turn where a speaker has the
    floor, against the level of the other file over the same stretch.
    No windows, no speech detection, no median.
    """
    signal = []
    for p in paths:
        with wave.open(p) as f:
            raw = f.readframes(f.getnframes())
        signal.append(np.frombuffer(raw, dtype="<i2").astype(np.float64))
    out = []
    for k in (0, 1):
        # Turn 0 belongs to the first speaker, turn 1 to the second:
        # loud in their own file, the built-in bleed in the other's.
        turn = slice(k * TURN * SR, (k + 1) * TURN * SR)
        own = float(np.sqrt(np.mean(signal[k][turn] ** 2)))
        other = float(np.sqrt(np.mean(signal[1 - k][turn] ** 2)))
        out.append(20.0 * float(np.log10(own / other)))
    return out


NUMBER = re.compile(r"(-?\d+(?:\.\d+)?)\s*dB")


def measured(findings):
    """Return {who: how many dB down} out of the report.

    Only the rows about one speaker in another's microphone; the
    summary line counts comparisons rather than decibels.
    """
    out = {}
    for f in findings:
        if "'s microphone" not in f.text:
            continue
        m = NUMBER.search(f.text)
        who = f.text.split(" in ")[0].strip().split(": ")[-1]
        if m:
            out[who] = float(m.group(1))
    return out


print()
first_pair = None
for wanted in (-15.0, -25.0, -6.0):
    # How far down the neighbour should sit, said the way the report
    # says it: a positive number of decibels.
    down = -wanted
    print("%.0f dB of bleed" % down)
    two = pair(wanted, os.path.join(WORK, "b%d" % int(down)))
    if first_pair is None:
        first_pair = two
    # Before the program is asked anything: the material is what it
    # says it is. Otherwise a wrong figure below reads as the program's
    # fault when the fault is in the two files handed to it.
    holds = bleed_in(two)
    check("  the files really carry %.0f dB of bleed" % down,
          max(abs(v - down) for v in holds) <= BUILT_SLACK,
          "wanted %.1f dB down, the files hold %.1f and %.1f dB down, "
          "at most %.1f dB out" % (down, holds[0], holds[1], BUILT_SLACK))
    findings = vpm.check_crosstalk(list(two))
    got = measured(findings)
    check("both directions are reported", len(got) == 2,
          "at %.0f dB: wanted 2 rows about a microphone, got %d of %d "
          "findings %s" % (down, len(got), len(findings),
                           sorted(got.items())))
    for who, value in sorted(got.items()):
        check("  %s is %.0f dB down, as built" % (who, down),
              abs(value - down) <= REPORT_SLACK,
              "wanted %.1f dB, the report says %.1f dB, at most %.1f dB out"
              % (down, value, REPORT_SLACK))
    kinds = set(f.kind for f in findings)
    if wanted <= -15.0:
        check("  that is far enough apart, so no warning",
              kinds == {"good"},
              "at %.0f dB: wanted ['good'] and nothing else, found %s"
              % (down, sorted(kinds)))
    else:
        check("  6 dB is too close, and the report says so",
              "hint" in kinds or "abort" in kinds,
              "at %.0f dB: wanted a hint or an abort among them, found %s"
              % (down, sorted(kinds)))

# One microphone out of the pair above; a new pair adds nothing.
print("\nOne microphone alone")
alone = vpm.check_crosstalk([first_pair[0]])
check("nothing to compare, nothing claimed", alone == [],
      "wanted 0 findings from 1 file, got %d: %s"
      % (len(alone), [f.text for f in alone]))

print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
