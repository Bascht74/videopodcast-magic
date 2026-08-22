# -*- coding: utf-8 -*-
"""How much of each speaker sits in the other microphone.

The 3:1 rule of thumb says a clip-on microphone should be three times
closer to its own speaker than to the next one, which puts the neighbour
about 10 dB down. The preflight measures that so it can be said before the
run rather than heard after it.

The material here is built with a known amount of bleed, so the figure the
report gives is either that amount or a fault.
"""
import os
HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = os.environ.get("VPM_SCRIPT") or os.path.join(
    os.path.dirname(HERE), "videopodcast-magic.py")
import importlib.util, math, random, re, struct, sys, tempfile, wave
spec = importlib.util.spec_from_file_location("vpm", SCRIPT)
vpm = importlib.util.module_from_spec(spec); sys.modules["vpm"] = vpm
spec.loader.exec_module(vpm)
SR = 48000
WORK = tempfile.mkdtemp(prefix="bleed_")
random.seed(7)
bad = []


def check(what, ok, detail=""):
    print("  %-54s %s%s" % (what, "ok" if ok else "FAIL",
                            "" if ok else "   " + detail))
    if not ok:
        bad.append(what)


def voice(seconds, base_hz):
    """A speech-like signal: a fundamental under a changing envelope."""
    n = int(seconds * SR)
    x = [0.0] * n
    for i in range(n):
        t = i / float(SR)
        swell = 0.5 + 0.5 * math.sin(2 * math.pi * 3.1 * t)
        x[i] = swell * (math.sin(2 * math.pi * base_hz * t)
                        + 0.5 * math.sin(2 * math.pi * 2 * base_hz * t)
                        + 0.3 * math.sin(2 * math.pi * 3 * base_hz * t)) / 1.8
    return x


def write(path, x):
    with wave.open(path, "w") as f:
        f.setnchannels(1)
        f.setsampwidth(2)
        f.setframerate(SR)
        f.writeframes(b"".join(
            struct.pack("<h", max(-32000, min(32000, int(v * 20000))))
            for v in x))
    return path


def pair(bleed_db, folder):
    """Two microphones, each hearing the other this much quieter."""
    duration, block = 60, 5
    a = [0.0] * (duration * SR)
    b = [0.0] * (duration * SR)
    quieter = 10 ** (bleed_db / 20.0)
    for k in range(duration // block):
        piece = voice(block, 130 if k % 2 == 0 else 190)
        start = k * block * SR
        for i, v in enumerate(piece):
            if k % 2 == 0:                       # A is talking
                a[start + i] = v
                b[start + i] = v * quieter
            else:                                # B is talking
                b[start + i] = v
                a[start + i] = v * quieter
    # A little noise, so nothing is digitally silent.
    for x in (a, b):
        for i in range(len(x)):
            x[i] += random.uniform(-1, 1) * 0.0005
    os.makedirs(folder, exist_ok=True)
    return (write(os.path.join(folder, "Anna.wav"), a),
            write(os.path.join(folder, "Bert.wav"), b))


NUMBER = re.compile(r"(-?\d+(?:\.\d+)?)\s*dB")


def measured(findings):
    """Return {who: how many dB down} out of the report.

    Only the rows about one speaker in another's microphone. The report
    also carries a summary line, and that one counts comparisons rather
    than decibels.
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
for wanted in (-15.0, -25.0, -6.0):
    print("%.0f dB of bleed" % -wanted)
    two = pair(wanted, os.path.join(WORK, "b%d" % int(-wanted)))
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

print("\nOne microphone alone")
one = pair(-15.0, os.path.join(WORK, "single"))[0]
check("nothing to compare, nothing claimed",
      vpm.check_crosstalk([one]) == [], str(vpm.check_crosstalk([one])))

print()
if bad:
    print("FAIL: %d of the checks" % len(bad))
    sys.exit(1)
print("All good.")
