# -*- coding: utf-8 -*-
"""How much of each speaker sits in the other microphone.

The 3:1 rule of thumb puts the neighbour about 10 dB down: a clip-on
microphone three times closer to its own speaker than to the next. The
material here is built with a known amount of bleed, so the figure the
report gives is either that amount or a fault.
"""
import os
HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = os.environ.get("VPM_SCRIPT") or os.path.join(
    os.path.dirname(HERE), "videopodcast-magic.py")
import importlib.util, re, sys, tempfile, wave
import numpy as np
spec = importlib.util.spec_from_file_location("vpm", SCRIPT)
vpm = importlib.util.module_from_spec(spec); sys.modules["vpm"] = vpm
spec.loader.exec_module(vpm)
# check_crosstalk decodes down to 16 kHz before it measures, so a higher
# rate only buys a resampling step; the voices here reach 570 Hz at most.
SR = 16000
# Five windows of at least 4 s each, and under twice one window the
# program refuses. 16 s holds eight whole turns, so no window cuts one
# in half; a half turn drags the reading down.
DURATION, TURN = 16, 2
WORK = tempfile.mkdtemp(prefix="bleed_")
bad, done = [], []


def check(what, ok, detail=""):
    print("  %-54s %s%s" % (what, "ok" if ok else "FAIL",
                            "" if ok else "   " + detail))
    done.append(what)
    if not ok:
        bad.append(what)


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
    print("%.0f dB of bleed" % -wanted)
    two = pair(wanted, os.path.join(WORK, "b%d" % int(-wanted)))
    if first_pair is None:
        first_pair = two
    findings = vpm.check_crosstalk(list(two))
    got = measured(findings)
    check("both directions are reported", len(got) == 2, str(got))
    for who, value in sorted(got.items()):
        check("  %s is %.0f dB down, as built" % (who, -wanted),
              abs(value - (-wanted)) <= 1.5, "%.1f dB" % value)
    kinds = set(f.kind for f in findings)
    if wanted <= -15.0:
        check("  that is far enough apart, so no warning",
              kinds == {"good"}, str(kinds))
    else:
        check("  6 dB is too close, and the report says so",
              "hint" in kinds or "abort" in kinds, str(kinds))

# One microphone out of the pair above; a new pair adds nothing.
print("\nOne microphone alone")
alone = vpm.check_crosstalk([first_pair[0]])
check("nothing to compare, nothing claimed", alone == [], str(alone))

print()
if bad:
    print("FAIL: %d of %d checks: %s"
          % (len(bad), len(done), "; ".join(bad)))
    sys.exit(1)
print("All good.")
