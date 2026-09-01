# -*- coding: utf-8 -*-
"""A speaker with her own microphone is in the cut beside a separation.

The owner's sentence, walked end to end: everybody is in the cut unless
somebody said "do not use". Anna has a microphone of her own and a
camera of her own; beside her a room recording was taken apart by voice,
and the two people it holds have no microphone. Until 31.8.2026 the
separation pushed Anna out -- the moment any recording was taken apart,
every track went with it, and she was heard in the mix and seen nowhere.

In order: the run ends without an error and without a traceback, the
speaker list and the cut list are both written, all three names stand in
the speaker list, Anna's passages reach it with the seconds she spoke,
the cut list puts her on her own camera and nobody else there, the
separated voice with a camera is on hers, the one without is on the wide
shot, and all three cameras carry shots instead of two.

Nothing goes out: the run is given --without-auphonic and no key, so
there is nothing to send with.
"""
import os
HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = os.environ.get("VPM_SCRIPT") or os.path.join(
    os.path.dirname(HERE), "videopodcast-magic.py")
import csv, json, re, subprocess, sys, tempfile, time, wave
import numpy as np

# The same environment the suite gives every test, so a run by hand
# measures the same thing. The speaker separation stays off: this run is
# handed one in the assignment and must not fetch a second.
ENV = dict(os.environ, LANG="C", LC_ALL="C", LANGUAGE="en",
           VPM_SILENT="1", VPM_NO_UPDATE_CHECK="1",
           VPM_NO_SPEAKER_SPLIT="1", QT_QPA_PLATFORM="offscreen")

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
# The common window is LENGTH minus the latest camera start. The
# alignment sets its sample points a couple of seconds apart and refuses
# a window holding none of them, so the length is not free: it has to
# hold five turns of five seconds with quiet between.
LENGTH = 40.0
# Where each camera's picture starts inside the recording.
LATE = {"CamOne": 0.0, "CamTwo": 2.0, "CamThree": 3.5}
# Turns with more than a second of quiet around each, none shorter than
# MIN_EDIT_DURATION_S, and nothing before 3.5 s where the common window
# begins. Anna speaks into a microphone of her own; Bea and Cid are only
# in the room recording, and the separation handed over is what tells
# them apart.
TURNS = {"Anna": [(5.0, 10.0), (18.0, 23.0)],
         "Bea": [(11.5, 16.5), (24.5, 29.5)],
         "Cid": [(31.0, 36.5)]}
MINE = "Anna"
# Anna's camera comes off her track in the assignment, Bea's off the
# voices of the separation. Nothing points at CamThree, so that is the
# wide shot of this run and Cid is shown there.
ON = {"Anna": "CamOne", "Bea": "CamTwo"}
WIDE = "CamThree"
# What the cut has to hold when everybody is in it. Written out rather
# than counted from ON and WIDE: a number the test works out for itself
# is worked out the way the program does it, and then agrees with a
# wrong answer.
CAMERAS_WANTED = 3
NAMES_WANTED = 3


def voice(turns, seed):
    """Speech-like noise in bursts: an envelope is what alignment reads."""
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


D = tempfile.mkdtemp(prefix="vpmownmic_")
said = {n: voice(TURNS[n], i + 1) for i, n in enumerate(sorted(TURNS))}
room = said["Anna"] + said["Bea"] + said["Cid"]
noise = np.random.default_rng(9).normal(0, 0.0004, int(LENGTH * RATE))
# Anna's microphone hears her and the room a fifth as loud; the room
# recording hears everybody. The cameras record the room, so the two
# recordings and the three pictures lie on one axis.
write(D + "/Mic_Anna.wav", said[MINE] + 0.2 * (room - said[MINE]) + noise)
write(D + "/room.wav", 0.6 * room + noise)

# One ffmpeg call for all three cameras, because a process start is what
# the Windows builder charges for. Colour bars at ultrafast: the run
# never decodes a video frame, it reads the packet times and copies the
# picture through, so the picture only has to exist. The -ss in front of
# each output is an output option and cuts that file alone.
build = ["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i",
         "smptebars=size=320x180:rate=25:duration=%.1f" % LENGTH,
         "-i", D + "/room.wav"]
for cam in sorted(LATE):
    build += ["-ss", "%.2f" % LATE[cam],
              "-map", "0:v", "-map", "1:a", "-c:v", "libx264",
              "-preset", "ultrafast", "-pix_fmt", "yuv420p",
              "-c:a", "pcm_s16le", "-shortest", D + "/" + cam + ".mov"]
subprocess.run(build, check=True)

# The file format number is read out of the program rather than the
# program imported for it: importing 35000 lines to learn one integer
# costs a second and pulls a window toolkit in with it. A plan with the
# wrong number is refused before anything is measured.
form = re.search(r"^FILE_FORMAT = (\d+)",
                 open(SCRIPT, encoding="utf-8").read(), re.M)
# Anna's track carries her camera, so the cut knows where she sits
# without any voice of the separation naming her. The room recording is
# a track with no camera: the people in it are on screen through their
# voices, and the recording itself is only in the mix. The separation
# was made on that recording and found Bea and Cid in it -- Anna is not
# in it, and that is the whole case.
plan = {"format": int(form.group(1)) if form else 3, "created_by": "test",
        "production": "MT",
        "tracks_of": [{"audio": D + "/Mic_Anna.wav",
                       "blocks": [D + "/Mic_Anna.wav"],
                       "speakers": MINE,
                       "camera": D + "/CamOne.mov", "camera_audio": False},
                      {"audio": D + "/room.wav",
                       "blocks": [D + "/room.wav"],
                       "speakers": "Room",
                       "camera": "", "camera_audio": False}],
        "cameras": [{"video": D + "/" + cam + ".mov", "name": cam}
                    for cam in sorted(LATE)],
        "speakers_of": {"source": D + "/room.wav", "names": {},
                        "segments": [[n, a, b] for n in ("Bea", "Cid")
                                     for a, b in TURNS[n]]},
        "voices_of": {"Bea": D + "/CamTwo.mov"}}
with open(D + "/assign.json", "w", encoding="utf-8") as f:
    json.dump(plan, f)


#--------------------------------------------------------------- The run

OUT = D + "/out"
# Started the way a person starts it. --no-wide-edges keeps the wide
# shot out of the first and last shot, so every shot in the list belongs
# to whoever is speaking in it.
call = [sys.executable, SCRIPT, "--multitrack", "--without-auphonic",
        "--assign", D + "/assign.json", "--out", OUT, "--no-metrics",
        "--no-speech-recognition", "--no-transcript-file",
        "--no-wide-edges", D + "/Mic_Anna.wav", D + "/room.wav"] \
    + [D + "/" + cam + ".mov" for cam in sorted(LATE)]
rc, out = 1, ""
try:
    p = subprocess.run(call, capture_output=True, text=True, timeout=900,
                       env=ENV)
    rc, out = p.returncode, (p.stdout or "") + (p.stderr or "")
except subprocess.TimeoutExpired as e:
    out = "the run was still going after 900 s: %s" % tail(
        (e.stdout or b"").decode("utf-8", "replace"))

print("1. The run goes through")
check("the run ends without an error", rc == 0,
      "%d, ends: %s" % (rc, tail(out)))
fell = out.find("Traceback")
# The end of it, on one line: the head of a traceback is a path, and a
# judgement that runs over three lines loses two of them in every report
# that keeps only the line saying FAIL.
check("and it prints no traceback", fell < 0,
      tail(out[fell:]) if fell >= 0 else "")

WHO = OUT + "/MT_speakers.csv"
CUT = OUT + "/MT_cameracut.csv"
there = sorted(os.listdir(OUT)) if os.path.isdir(OUT) else "no folder"
check("the speaker list was written", os.path.exists(WHO), str(there))
check("the cut list was written", os.path.exists(CUT), str(there))

print("\n2. The speaker list holds the microphone beside the separation")
rows = []
if os.path.exists(WHO):
    with open(WHO, encoding="utf-8", newline="") as f:
        # Speaker, Start TC, End TC, Time from start, Duration s
        rows = [(r[0], float(r[4])) for r in list(csv.reader(f))[1:]]
named = sorted({n for n, _s in rows})
print("   ", len(rows), "passages by", named)
check("all three speakers stand in the speaker list",
      len(named) == NAMES_WANTED and named == sorted(TURNS),
      "%d names %s, wanted %d %s"
      % (len(named), named, NAMES_WANTED, sorted(TURNS)))
# Her own line, and not only a name in a list: the fault this is about
# did not shorten her, it deleted her. The seconds are held loosely --
# the detection finds the edges of a burst, not the number in TURNS.
hers = [s for n, s in rows if n == MINE]
wanted = sum(b - a for a, b in TURNS[MINE])
check("and the microphone's own passages are in it with their seconds",
      len(hers) == len(TURNS[MINE]) and abs(sum(hers) - wanted) < 2.0,
      "%d passages of %.2f s, wanted %d of about %.2f s"
      % (len(hers), sum(hers), len(TURNS[MINE]), wanted))

print("\n3. The cut list seats every one of them")
shots = []
if os.path.exists(CUT):
    with open(CUT, encoding="utf-8", newline="") as f:
        # Shot, Camera, Speaker, Start TC, End TC, Duration s
        shots = [(r[1], r[2]) for r in list(csv.reader(f))[1:]]
print("   ", len(shots), "shots:", shots)


def seated(who):
    """Which cameras the cut list puts one name on, and in how many shots."""
    mine = [cam for cam, name in shots if name == who]
    return sorted(set(mine)), len(mine)


# A judgement per person, and the person written out rather than built
# from the data: the register reads the wording as it stands in the
# source, so one name holding three people would go in as a single row
# -- and a row that has seen one of the cases it names counts as done
# while the other two were never tried.
where, count = seated(MINE)
check("Anna is cut to her own camera and to no other",
      count > 0 and where == [ON[MINE]], "%d shots, on %s -- wanted %s"
      % (count, where or "nothing", ON[MINE]))
where, count = seated("Bea")
check("the separated voice with a camera is cut to hers",
      count > 0 and where == [ON["Bea"]], "%d shots, on %s -- wanted %s"
      % (count, where or "nothing", ON["Bea"]))
where, count = seated("Cid")
check("and the separated voice without one to the wide shot",
      count > 0 and where == [WIDE], "%d shots, on %s -- wanted %s"
      % (count, where or "nothing", WIDE))
shown = sorted({cam for cam, _who in shots})
check("all three cameras carry shots, not two",
      len(shown) == CAMERAS_WANTED, "%d cameras %s, wanted %d"
      % (len(shown), shown, CAMERAS_WANTED))

print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
