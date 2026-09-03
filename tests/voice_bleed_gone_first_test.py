# -*- coding: utf-8 -*-
"""#80: does the bleed get taken out before the speech detection?"""
import os
HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = os.environ.get("VPM_SCRIPT") or os.path.join(
    os.path.dirname(HERE), "videopodcast_magic.py")
import importlib.util, sys, time, wave
import numpy as np
sys.path.insert(0, os.path.dirname(
    os.path.abspath(__file__)))
from fixture_root import fixture

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
spec = importlib.util.spec_from_file_location("vpm", SCRIPT)
vpm = importlib.util.module_from_spec(spec); sys.modules["vpm"] = vpm
spec.loader.exec_module(vpm)

began = time.time()
done = 0
bad = []


def check(name, ok, extra=""):
    global done
    done += 1
    print("  %-58s %s %s" % (name, "ok" if ok else "FAIL", extra))
    if not ok:
        bad.append("%s [%s]" % (name, extra or "no numbers"))


D = fixture("speakergate")
os.makedirs(D, exist_ok=True)
RATE = 8000
LENGTH = 60.0
TURNS = {"Host": [(0, 10), (20, 30), (40, 50)],
         "Guest": [(10, 20), (30, 40), (50, 60)]}


def voice(turns, seed, length=LENGTH):
    """Speech-like noise in the given windows, silence in between."""
    rng = np.random.default_rng(seed)
    x = np.zeros(int(length * RATE))
    for a, b in turns:
        n = int((b - a) * RATE)
        # Amplitude wobbles like speech, so blocks differ from each other.
        env = 0.3 + 0.7 * np.abs(np.sin(np.linspace(0, 40, n)))
        x[int(a * RATE):int(a * RATE) + n] = rng.normal(0, 0.3, n) * env
    return x


def write(path, x):
    with wave.open(path, "wb") as f:
        f.setnchannels(1); f.setsampwidth(2); f.setframerate(RATE)
        f.writeframes((np.clip(x, -1, 1) * 32000).astype("<i2").tobytes())


def build(bleed_db):
    """Two microphones, each hearing the other speaker that much quieter."""
    host, guest = voice(TURNS["Host"], 1), voice(TURNS["Guest"], 2)
    g = 10.0 ** (-bleed_db / 20.0)
    noise = np.random.default_rng(3).normal(0, 0.0005, len(host))
    write(D + "/Host.wav", host + g * guest + noise)
    write(D + "/Guest.wav", guest + g * host + noise)
    return [("Host", D + "/Host.wav", 0.0), ("Guest", D + "/Guest.wav", 0.0)]


def speech_seconds(out):
    return {n: round(sum(b - a for a, b in segs), 1) for n, segs in out}


def wrong_share(out, turns=TURNS):
    """How much of a speaker's detected speech falls in the other's turn."""
    bad = total = 0.0
    for n, segs in out:
        mine = turns[n]
        for a, b in segs:
            total += b - a
            inside = sum(max(0.0, min(b, y) - max(a, x)) for x, y in mine)
            bad += (b - a) - inside
    return 100.0 * bad / (total or 1.0)


print("1. Six decibels of bleed -- less than the 3:1 rule asks for")
tracks = build(6.0)
plain = vpm.speakers_from_tracks(tracks, separate=False)
apart = vpm.speakers_from_tracks(tracks, separate=True)
print("   without separation:", speech_seconds(plain),
      " wrong %.0f %%" % wrong_share(plain))
print("   with separation:   ", speech_seconds(apart),
      " wrong %.0f %%" % wrong_share(apart))
# Without separation both microphones carry speech almost the whole time,
# so the noise floor sits at speech level and the threshold rejects it all.
plain_s = speech_seconds(plain)
check("without separation the result is unusable",
        abs(plain_s["Host"] - 30.0) > 10.0
        or abs(plain_s["Guest"] - 30.0) > 10.0 or wrong_share(plain) > 30.0,
        str(plain_s))
check("with separation almost nothing lands in the other turn",
        wrong_share(apart) < 5.0, "%.0f %%" % wrong_share(apart))
for n in ("Host", "Guest"):
    got = speech_seconds(apart)[n]
    check("%s keeps their own 30 s" % n, 24.0 <= got <= 33.0, str(got))

print("\n2. And the cut follows from it")
camera_of = {"Host": "CamHost", "Guest": "CamGuest"}
for name, out in (("without separation", plain), ("with separation", apart)):
    cut = vpm.build_camera_cut(out, LENGTH, camera_of, "Wide", 1.2, -0.3)
    share = {}
    for a, b, who in cut:
        share[who] = share.get(who, 0.0) + (b - a)
    print("   %-20s %2d shots | %s" % (name, len(cut), ", ".join(
        "%s %.0f %%" % (k, 100 * v / LENGTH) for k, v in sorted(share.items()))))
    if name == "without separation":
        check("without separation it stays on the wide shot",
                share.get("Wide", 0.0) > 0.8 * LENGTH,
                "%.0f s" % share.get("Wide", 0.0))
    else:
        check("with separation both cameras are used",
                share.get("CamHost", 0) > 10 and share.get("CamGuest", 0) > 10,
                str({k: round(v) for k, v in share.items()}))

print("\n3. Twenty decibels -- lavaliers, well separated")
tracks = build(20.0)
apart = vpm.speakers_from_tracks(tracks, separate=True)
check("still right", wrong_share(apart) < 5.0, "%.0f %%" % wrong_share(apart))

print("\n4. Microphones side by side -- it says so instead of inventing")
tracks = build(0.5)
said = []
apart = vpm.speakers_from_tracks(tracks, separate=True, note=said.append)
check("a reason is given", any("separable" in t or "quieter" in t
                               or "exactly one" in t for t in said),
        "; ".join(said)[:70])

print("\n5. One track alone still works")
build(40.0)          # a clean recording, nothing from the other microphone
one = vpm.speakers_from_tracks([("Host", D + "/Host.wav", 0.0)])
check("segments found", len(one) == 1 and len(one[0][1]) >= 3,
        str(len(one[0][1])))

print("\n6. An offset moves the segments onto the common axis")
tracks = build(20.0)
moved = [(n, p, 100.0) for n, p, _o in tracks]
out = vpm.speakers_from_tracks(moved, separate=True)
first = min(a for _n, segs in out for a, _b in segs)
check("everything sits 100 s later", 99.0 <= first <= 102.0, str(first))

print("\n7. One person hardly speaks -- and is separated all the same")
# Each track is held against a percentile of its own blocks, silence
# included. A speaker who says little pushes that reference down into
# what the others bleed into their microphone, and then the bleed is
# measured against the bleed.
UNEVEN_LENGTH = 400.0
UNEVEN = {"Host": [(20, 22), (80, 82), (140, 143), (220, 222),
                   (300, 303), (360, 362)],                     # 14 s
          "Guest": [(30, 60), (95, 125), (150, 180), (230, 260),
                    (310, 340), (370, 390)]}                    # 170 s


def build_uneven(bleed_db):
    """The same two microphones, but one of the two says almost nothing."""
    host = voice(UNEVEN["Host"], 4, UNEVEN_LENGTH)
    guest = voice(UNEVEN["Guest"], 5, UNEVEN_LENGTH)
    g = 10.0 ** (-bleed_db / 20.0)
    noise = np.random.default_rng(6).normal(0, 0.0005, len(host))
    write(D + "/Few.wav", host + g * guest + noise)
    write(D + "/Many.wav", guest + g * host + noise)
    return [("Host", D + "/Few.wav", 0.0), ("Guest", D + "/Many.wav", 0.0)]


tracks = build_uneven(20.0)
said = []
apart = vpm.speakers_from_tracks(tracks, separate=True, note=said.append)
# The two texts the program uses, taken from the catalogue rather than
# written out, so the check does not hang on one language.
NOT_SEPARABLE = vpm.T('  Bleed not separable: %s').split('%s')[0]
AS_LOUD = vpm.T('the microphones hear each other almost as loudly '
                'as their own speaker')
refused = [t for t in said if t.startswith(NOT_SEPARABLE)]
print("   host speaks 14 s of 400 s = 3.5 %, microphones 20 dB apart")
print("   notes:", "; ".join(t.strip() for t in said)[:100] or "none")
print("   seconds:", speech_seconds(apart),
      " wrong %.1f %%" % wrong_share(apart, UNEVEN))
check("a speaker on a thirtieth of the recording is still separated",
        not refused, "; ".join(t.strip() for t in refused)[:90]
        or "no refusal")
check("no refusal calls microphones 20 dB apart almost equally loud",
        not [t for t in refused if AS_LOUD in t],
        "built 20.0 dB apart; %s"
        % ("; ".join(t.strip() for t in refused)[:80] or "no refusal"))
few = speech_seconds(apart)["Host"]
check("the one who speaks little keeps their own 14 s",
        8.0 <= few <= 40.0, "%.1f s against the 14.0 s built" % few)
off = wrong_share(apart, UNEVEN)
check("almost nothing of the quiet speaker lands in the other turn",
        off < 15.0, "%.1f %% against a limit of 15.0 %%" % off)
cut = vpm.build_camera_cut(apart, UNEVEN_LENGTH, camera_of, "Wide",
                           1.2, -0.3)
share = {}
for a, b, who in cut:
    share[who] = share.get(who, 0.0) + (b - a)
print("   cut: %2d shots | %s" % (len(cut), ", ".join(
    "%s %.0f s" % (k, v) for k, v in sorted(share.items()))))
check("the cut reaches both cameras although one of them speaks little",
        share.get("CamHost", 0.0) > 5.0 and share.get("CamGuest", 0.0) > 60.0,
        "%s against 5 s and 60 s"
        % str({k: round(v) for k, v in sorted(share.items())}))

print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
