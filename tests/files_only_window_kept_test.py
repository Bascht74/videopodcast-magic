# -*- coding: utf-8 -*-
"""A time window shortens the cameras and leaves every frame where it was.

Two runs go through on the same material, one without a window and one
with. "Whole cameras" holds the first to what it always wrote, "only
the window" measures what the second delivers, "the timecode" that the
head cut off moved it, "the recorded moment" holds the delivered
picture against the source camera, "the handover" describes the
delivered file, and "what it wrote" is the line the log owes the user.
"""
import os
HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = os.environ.get("VPM_SCRIPT") or os.path.join(
    os.path.dirname(HERE), "videopodcast-magic.py")
import hashlib, importlib.util, json, subprocess, sys, tempfile, time, wave
import numpy as np
spec = importlib.util.spec_from_file_location("vpm", SCRIPT)
vpm = importlib.util.module_from_spec(spec); sys.modules["vpm"] = vpm
spec.loader.exec_module(vpm)

# The same environment the suite gives every test, so a run by hand
# measures the same thing. Speaker separation is off: it fetches a
# machine-learning environment and is not the question here.
os.environ.setdefault("VPM_NO_SPEAKER_SPLIT", "1")
ENV = dict(os.environ, LANG="C", LC_ALL="C", LANGUAGE="en",
           VPM_SILENT="1", VPM_NO_UPDATE_CHECK="1",
           QT_QPA_PLATFORM="offscreen")
D = tempfile.mkdtemp(prefix="onlywindow_")

began = time.time()
done = 0
bad = []


def check(name, ok, extra=""):
    global done
    done += 1
    print("  %-58s %s %s" % (name, "ok" if ok else "FAIL", extra))
    if not ok:
        bad.append("%s [%s]" % (name, extra or "no numbers"))


def tail(text, n=2):
    rows = [x.strip() for x in text.splitlines() if x.strip()]
    return (" | ".join(rows[-n:]))[:100]


#------------------------------------------------------------- Material

RATE = 48000
FPS = 25
# 45 s, and not less: the run stops below a common window of 30 s, and
# the common window here is LENGTH minus the latest camera start.
LENGTH = 45.0
# Where each camera's picture starts inside the recording. The three
# differ and none of them is zero, so one head cut of the same size for
# all of them would show up at once.
LATE = {"CamHost": 0.0, "CamGuest": 4.0, "CamWide": 7.0}
CAM_LEN = dict((cam, LENGTH - late) for cam, late in LATE.items())
COMMON = max(LATE.values())        # where the common window begins
# The window, counted from the start of the common window. The tenths
# are what makes the key frames matter: the In point less the margin
# then falls between two of them and the copy has to go back.
WIN_IN, WIN_OUT = 10.4, 25.4
# What the program keeps beyond the window at each end, the spacing of
# the key frames the copy has to start on, and how far the cut has to go
# back to reach one. The material below is built to that spacing, so
# what the run may cut back to is known here as a value.
MARGIN, GOP, SNAP = 1.0, 1.0, 0.4
# How long a delivered camera is, and the wall clock its first frame
# carries. Every camera lands on the same moment, because they were all
# rolling by the time the window begins.
WANT_S = WIN_OUT - WIN_IN + 2 * MARGIN + SNAP
WANT_TC = "10:00:16:00"
TURNS = {"Host": [(5, 11), (18, 24), (31, 37)],
         "Guest": [(12.5, 17), (25.5, 30)]}
# Where the pictures are compared, in programme time. None of them falls
# on a frame boundary, so a reading cannot land on either neighbour.
WHEN = [0.5, 4.1, 9.3, 13.5]


def voice(turns, seed):
    rng = np.random.default_rng(seed)
    x = np.zeros(int(LENGTH * RATE))
    for a, b in turns:
        n = int((b - a) * RATE)
        env = 0.3 + 0.7 * np.abs(np.sin(np.linspace(0, 50, n)))
        x[int(a * RATE):int(a * RATE) + n] = rng.normal(0, 0.25, n) * env
    return x


def write(path, x):
    with wave.open(path, "wb") as f:
        f.setnchannels(1); f.setsampwidth(2); f.setframerate(RATE)
        f.writeframes((np.clip(x, -1, 1) * 32000).astype("<i2").tobytes())


host, guest = voice(TURNS["Host"], 1), voice(TURNS["Guest"], 2)
bleed = 10 ** (-8.0 / 20)            # under the 3:1 rule on purpose
noise = np.random.default_rng(9).normal(0, 0.0004, len(host))
write(D + "/Host.wav", host + bleed * guest + noise)
write(D + "/Guest.wav", guest + bleed * host + noise)
write(D + "/room.wav", 0.6 * host + 0.6 * guest + noise)

# One ffmpeg call for all three cameras, because a process start is what
# the Windows builder charges for. The -ss in front of each output is an
# output option and cuts that file alone, so picture and sound of each
# camera begin its own LATE in. testsrc2 moves, so no two frames of one
# camera look alike and a picture can be told from its neighbour.
build = ["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i",
         "testsrc2=size=320x180:rate=%d:duration=%.1f" % (FPS, LENGTH),
         "-i", D + "/room.wav"]
for cam, late in sorted(LATE.items()):
    build += ["-ss", "%.2f" % late,
              "-map", "0:v", "-map", "1:a", "-c:v", "libx264",
              "-preset", "ultrafast", "-pix_fmt", "yuv420p",
              # A key frame on every whole second, so what the copy may
              # start on is a value here and not a second calculation.
              "-force_key_frames", "expr:eq(mod(n,%d),0)" % int(FPS * GOP),
              "-c:a", "pcm_s16le", "-shortest",
              "-timecode", "10:00:%02d:00" % int(late),
              D + "/" + cam + ".mov"]
subprocess.run(build, check=True)

# The material has to carry the key frames the expectations rest on.
# That says nothing about the program, so it is an assert, not a check.
for cam in LATE:
    got = subprocess.run(
        ["ffprobe", "-v", "error", "-select_streams", "v:0", "-skip_frame",
         "nokey", "-show_entries", "frame=pts_time", "-of", "csv=p=0",
         "-read_intervals", "%+6", D + "/" + cam + ".mov"],
        capture_output=True, text=True).stdout
    marks = [round(float(x.strip().rstrip(",")), 3)
             for x in got.splitlines() if x.strip().rstrip(",")]
    assert marks[:5] == [0.0, 1.0, 2.0, 3.0, 4.0], (cam, marks[:5])

plan = {"format": vpm.FILE_FORMAT, "created_by": "test", "production": "OW",
        "tracks_of": [
            {"audio": D + "/Host.wav", "blocks": [D + "/Host.wav"],
             "speakers": "Host", "camera": D + "/CamHost.mov",
             "camera_audio": False},
            {"audio": D + "/Guest.wav", "blocks": [D + "/Guest.wav"],
             "speakers": "Guest", "camera": D + "/CamGuest.mov",
             "camera_audio": False}],
        "cameras": [{"video": D + "/" + c + ".mov", "name": c}
                    for c in sorted(LATE)]}
with open(D + "/assign.json", "w", encoding="utf-8") as f:
    json.dump(plan, f)


def run(out, *extra):
    """One Multitrack run on this material, and what it printed."""
    p = subprocess.run(
        [sys.executable, SCRIPT, "--multitrack", "--without-auphonic",
         "--no-speech-recognition", "--no-transcript-file",
         "--assign", D + "/assign.json", "--out", out, "--no-metrics",
         "--no-wide-edges"] + [str(x) for x in extra]
        + [D + "/Host.wav", D + "/Guest.wav"]
        + [D + "/" + c + ".mov" for c in sorted(LATE)],
        capture_output=True, text=True, timeout=1800, env=ENV)
    return p.returncode, (p.stdout or "") + (p.stderr or "")


#-------------------------------------------------------------- The runs

rc1, log1 = run(D + "/plain")
rc2, log2 = run(D + "/window", "--in-point", "+%.1f" % WIN_IN,
                "--out-point", "+%.1f" % WIN_OUT)


def handover(folder):
    path = os.path.join(D, folder, "OW_resolve.json")
    if not os.path.exists(path):
        return {}
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def by_camera(over):
    return {c["camera"]: c for c in (over.get("cameras") or [])}


plain_over, window_over = handover("plain"), handover("window")
plain_told, window_told = by_camera(plain_over), by_camera(window_over)


def facts(folder, cam):
    """Running time, size, timecode and first-frame kind of a delivery."""
    made = os.path.join(D, folder, cam + ".mov")
    if not os.path.exists(made):
        return {"seconds": 0.0, "bytes": 0, "tc": "", "key": "no file"}
    d = json.loads(subprocess.run(
        ["ffprobe", "-v", "error", "-print_format", "json", "-show_format",
         "-show_streams", made], capture_output=True, text=True).stdout
        or "{}")
    stamps = [(s.get("tags") or {}).get("timecode") for s in d.get("streams", [])
              if (s.get("tags") or {}).get("timecode")]
    # The packet flags, not the decoded frame: a file that starts
    # between two key frames answers "frame=key_frame" with nothing at
    # all, and an empty answer looks the same as a failed call. The
    # flags say it outright -- K for a key frame, D for one to discard.
    first = subprocess.run(
        ["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
         "packet=flags", "-of", "csv=p=0", "-read_intervals", "%+#1",
         made], capture_output=True, text=True).stdout.splitlines()
    return {"seconds": float((d.get("format") or {}).get("duration") or 0.0),
            "bytes": int((d.get("format") or {}).get("size") or 0),
            "tc": (stamps or [""])[0],
            "flags": (first or ["no answer"])[0].strip().rstrip(",")}


plain_facts = dict((c, facts("plain", c)) for c in LATE)
window_facts = dict((c, facts("window", c)) for c in LATE)


def delivered_frames(folder, told):
    """A picture per camera and programme time, out of what was written.

    One ffmpeg call for the lot: a process start is what the Windows
    builder charges for, and one call per picture would be a dozen.
    """
    want, call, out = [], ["ffmpeg", "-v", "error", "-y"], {}
    for cam in sorted(LATE):
        made = os.path.join(D, folder, cam + ".mov")
        if cam not in told or not os.path.exists(made):
            continue
        for t in WHEN:
            call += ["-ss", "%.6f" % (t - told[cam]["offset"]), "-i", made]
            want.append((cam, t))
    for i, (cam, t) in enumerate(want):
        png = os.path.join(D, "made_%s_%d.png" % (folder, i))
        call += ["-map", "%d:v" % i, "-frames:v", "1", "-f", "image2", png]
        out[(cam, t)] = png
    if want:
        subprocess.run(call, capture_output=True)
    return dict((k, hashlib.sha256(open(p, "rb").read()).hexdigest()[:16])
                for k, p in out.items() if os.path.exists(p))


def recorded_frames(zero, tag):
    """The same moments taken from the source cameras themselves.

    *zero* is where programme time 0 lies in the recording, so the
    camera saw that moment at *zero* minus its own start. This is the
    one reading in the file that does not come through the program.
    """
    want, call, out = [], ["ffmpeg", "-v", "error", "-y"], {}
    for cam in sorted(LATE):
        for t in WHEN:
            call += ["-ss", "%.6f" % (zero + t - LATE[cam]),
                     "-i", D + "/" + cam + ".mov"]
            want.append((cam, t))
    for i, (cam, t) in enumerate(want):
        png = os.path.join(D, "shot_%s_%d.png" % (tag, i))
        call += ["-map", "%d:v" % i, "-frames:v", "1", "-f", "image2", png]
        out[(cam, t)] = png
    subprocess.run(call, capture_output=True)
    return dict((k, hashlib.sha256(open(p, "rb").read()).hexdigest()[:16])
                for k, p in out.items() if os.path.exists(p))


plain_seen = delivered_frames("plain", plain_told)
window_seen = delivered_frames("window", window_told)
plain_want = recorded_frames(COMMON, "plain")
window_want = recorded_frames(COMMON + WIN_IN, "window")


def missed(seen, want):
    """Which camera and moment does not show the recorded picture."""
    return ["%s at %.1f s" % (cam, t) for (cam, t), h in sorted(want.items())
            if seen.get((cam, t)) != h]


#------------------------------------------------------------ The answers

print("1. Both runs go through with nothing leaving the house")
check("the run without a window returns 0", rc1 == 0,
      "%d, %s" % (rc1, tail(log1)))
check("the run with a window returns 0", rc2 == 0,
      "%d, %s" % (rc2, tail(log2)))
check("neither run shows a traceback",
      "Traceback" not in log1 and "Traceback" not in log2,
      "%d in the run without a window, %d in the one with"
      % (log1.count("Traceback"), log2.count("Traceback")))
check("nothing was uploaded in either run",
      not any("auphonic.com/api" in x or "Uploading" in x
              for x in (log1, log2)),
      "%d mentions of auphonic.com/api and %d of Uploading in %d "
      "characters of log, wanted none"
      % (log1.count("auphonic.com/api") + log2.count("auphonic.com/api"),
         log1.count("Uploading") + log2.count("Uploading"),
         len(log1) + len(log2)))

print("\n2. Without a window the cameras come out whole")
short = ["%s %.3f s of %.1f" % (c, plain_facts[c]["seconds"], CAM_LEN[c])
         for c in sorted(LATE)
         if abs(plain_facts[c]["seconds"] - CAM_LEN[c]) > 0.06]
check("without a window every camera keeps its whole running time",
      not short, "; ".join(short) or "3 of 3 whole, %s"
      % [round(plain_facts[c]["seconds"], 2) for c in sorted(LATE)])
kept = ["%s says %s, wanted %s"
        % (c, plain_facts[c]["tc"], "10:00:%02d:00" % int(LATE[c]))
        for c in sorted(LATE)
        if plain_facts[c]["tc"] != "10:00:%02d:00" % int(LATE[c])]
check("without a window the timecode stays the camera's own",
      not kept, "; ".join(kept) or "3 of 3 unchanged")

print("\n3. With a window only the window is written")
off_length = ["%s %.3f s, wanted %.1f"
              % (c, window_facts[c]["seconds"], WANT_S)
              for c in sorted(LATE)
              if abs(window_facts[c]["seconds"] - WANT_S) > 0.06]
check("with a window every camera holds the window and a second at each end",
      not off_length,
      "; ".join(off_length) or "3 of 3 at %.1f s" % WANT_S)
# Half, not merely "smaller": with the trim taken out the two files
# still differ by about a kilobyte in seventy megabytes, and a check
# that "smaller" satisfies would have called that a saving.
not_smaller = ["%s %d bytes against %d"
               % (c, window_facts[c]["bytes"], plain_facts[c]["bytes"])
               for c in sorted(LATE)
               if window_facts[c]["bytes"] * 2 >= plain_facts[c]["bytes"]]
check("with a window every camera file is under half the size",
      not not_smaller,
      "; ".join(not_smaller) or "together %d bytes against %d"
      % (sum(window_facts[c]["bytes"] for c in LATE),
         sum(plain_facts[c]["bytes"] for c in LATE)))
not_key = ["%s begins on a packet flagged %s" % (c, window_facts[c]["flags"])
           for c in sorted(LATE)
           if not window_facts[c]["flags"].startswith("K")
           or "D" in window_facts[c]["flags"]]
check("the delivered picture begins on a key frame",
      not not_key, "; ".join(not_key)
      or "3 of 3 flagged %s" % window_facts["CamHost"]["flags"])

print("\n4. The timecode moved with the head that was cut off")
wrong_tc = ["%s says %s" % (c, window_facts[c]["tc"]) for c in sorted(LATE)
            if window_facts[c]["tc"] != WANT_TC]
check("the timecode moved on by what was cut off the front",
      not wrong_tc, "; ".join(wrong_tc) or "3 of 3 say %s" % WANT_TC)

print("\n5. The delivered picture is the moment it was recorded")
check("without a window the camera shows the recorded moment",
      bool(plain_want) and not missed(plain_seen, plain_want),
      "%d of %d moments read, wrong: %s"
      % (len(plain_seen), len(plain_want),
         missed(plain_seen, plain_want) or "none"))
check("with a window the camera shows the recorded moment",
      bool(window_want) and not missed(window_seen, window_want),
      "%d of %d moments read, wrong: %s"
      % (len(window_seen), len(window_want),
         missed(window_seen, window_want) or "none"))

print("\n6. The handover describes what was delivered")
off_place = ["%s says %.4f, wanted %.4f"
             % (c, window_told[c]["offset"], -(MARGIN + SNAP))
             for c in sorted(LATE)
             if c not in window_told
             or abs(window_told[c]["offset"] + MARGIN + SNAP) > 0.06]
check("the handover puts every camera just before the In point",
      bool(window_told) and not off_place,
      "; ".join(off_place) or "3 of 3 at %.1f s" % -(MARGIN + SNAP))
off_dur = ["%s says %.3f, the file is %.3f"
           % (c, window_told[c]["duration"], window_facts[c]["seconds"])
           for c in sorted(LATE)
           if c not in window_told
           or abs(window_told[c]["duration"]
                  - window_facts[c]["seconds"]) > 0.06]
check("the handover says the delivered length, not the recording's",
      bool(window_told) and not off_dur,
      "; ".join(off_dur) or "3 of 3 agree with the file")

print("\n7. The run says what it wrote")
said = vpm.T('  The cameras carry the time window and a second at each end: '
             '%s written for %s of the %s recorded.').split("%s")[0]
check("the run with a window says what the cameras carry",
      said in log2, "%r is not in %d characters of log -- %s"
      % (said[:40], len(log2), tail(log2)))
check("the run without a window says nothing of the sort",
      said not in log1, "%r stands in %d characters of log all the same"
      % (said[:40], len(log1)))

print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
