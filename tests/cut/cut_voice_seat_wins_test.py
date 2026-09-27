# -*- coding: utf-8 -*-
"""A person on two cameras sits on the voice's camera, in every answer.

Vera's microphone is assigned to one camera, and the separation under
another camera's sound assigns her voice to a second: the owner's rule
is that the voice's own assignment wins, one rule everywhere, and the
log says so. In order: the run goes through and writes its files, the
log names the person and the camera that wins, the cut list, the
handover's table of cameras and the handover's cut put her on the
voice's camera only, the camera she left is judged alike by the cut
and the handover, and the preview of that handover and the cut list
rebuilt from it by the button show her where the run did.
"""
PLATFORM_BOUND = True
import os
import sys
# tests/, where the helpers and state/ lie; this file may stand in a
# folder under it, or in one under that.
HERE = os.path.dirname(os.path.abspath(__file__))
while not os.path.isfile(os.path.join(HERE, "the_program.py")) \
        and os.path.dirname(HERE) != HERE:
    HERE = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import the_program
SCRIPT = the_program.SCRIPT
import contextlib, csv, io, json, re, subprocess, tempfile, time, wave
import numpy as np

# The same environment the suite gives every test. The speaker
# separation stays off: the run is handed one in the assignment.
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
# Long enough for five turns of five seconds after the latest camera
# start, with quiet between: the alignment refuses a thinner window.
LENGTH = 40.0
LATE = {"CamOne": 0.0, "CamTwo": 2.0, "CamThree": 3.5}
TURNS = {"Vera": [(5, 10), (18, 23)],
         "Wim": [(11.5, 16.5), (24.5, 29.5)],
         "Xenia": [(31, 36.5)]}
# Vera twice: her microphone's track says CamThree, her voice CamOne.
# The voice is the one that counts.
TRACK_SAYS = "CamThree"
VOICE_SAYS = {"Vera": "CamOne", "Wim": "CamTwo"}


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


D = tempfile.mkdtemp(prefix="vpmvoiceseat_")
said = {n: voice(TURNS[n], i + 1) for i, n in enumerate(sorted(TURNS))}
room = said["Vera"] + said["Wim"] + said["Xenia"]
noise = np.random.default_rng(9).normal(0, 0.0004, int(LENGTH * RATE))
write(D + "/Mic_A.wav", said["Vera"] + 0.2 * (room - said["Vera"]) + noise)
write(D + "/Mic_B.wav", said["Wim"] + 0.2 * (room - said["Wim"]) + noise)
write(D + "/room.wav", 0.6 * room + noise)

# One ffmpeg call for the three cameras; the run copies the picture
# through, so colour bars at ultrafast are enough.
build = ["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i",
         "smptebars=size=320x180:rate=25:duration=%.1f" % LENGTH,
         "-i", D + "/room.wav"]
for cam in sorted(LATE):
    build += ["-ss", "%.2f" % LATE[cam],
              "-map", "0:v", "-map", "1:a", "-c:v", "libx264",
              "-preset", "ultrafast", "-pix_fmt", "yuv420p",
              "-c:a", "pcm_s16le", "-shortest", D + "/" + cam + ".mov"]
subprocess.run(build, check=True)

form = re.search(r"^FILE_FORMAT = (\d+)", the_program.text(), re.M)
# Mic A is Vera's and assigned to CamThree; Mic B is a device with no
# camera. The separation under CamOne's sound heard all three, and
# voices_of seats Vera on CamOne -- the second camera for one person.
plan = {"format": int(form.group(1)) if form else 3, "created_by": "test",
        "production": "MT",
        "tracks_of": [{"audio": D + "/Mic_A.wav", "blocks": [D + "/Mic_A.wav"],
                       "speakers": "Vera",
                       "camera": D + "/" + TRACK_SAYS + ".mov",
                       "camera_audio": False},
                      {"audio": D + "/Mic_B.wav", "blocks": [D + "/Mic_B.wav"],
                       "speakers": "Mic B", "camera": "",
                       "camera_audio": False}],
        "cameras": [{"video": D + "/" + cam + ".mov", "name": cam}
                    for cam in sorted(LATE)],
        "speakers_of": {"source": D + "/CamOne.mov", "names": {},
                        "segments": [[n, a, b] for n in sorted(TURNS)
                                     for a, b in TURNS[n]]},
        "voices_of": {who: D + "/" + cam + ".mov"
                      for who, cam in VOICE_SAYS.items()}}
with open(D + "/assign.json", "w", encoding="utf-8") as f:
    json.dump(plan, f)


#--------------------------------------------------------------- The run

OUT = D + "/out"
call = [sys.executable, SCRIPT, "--multitrack", "--without-auphonic",
        "--assign", D + "/assign.json", "--out", OUT, "--no-metrics",
        "--no-speech-recognition", "--no-transcript-file",
        "--no-wide-edges", D + "/Mic_A.wav", D + "/Mic_B.wav"] \
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
check("and it prints no traceback", fell < 0,
      tail(out[fell:]) if fell >= 0 else "")
CUT = OUT + "/MT_cameracut.csv"
JS = OUT + "/MT_resolve.json"
there = sorted(os.listdir(OUT)) if os.path.isdir(OUT) else "no folder"
check("the cut list was written", os.path.exists(CUT), str(there))
check("the handover for Resolve was written", os.path.exists(JS),
      str(there))

vpm = the_program.load()
vpm.set_language("en")

print("\n2. The log says which camera wins")
wanted = vpm.T('  %s is on two cameras: %s by the track, %s by the voice. '
               'The voice wins, so the cut shows %s on %s only.') % (
    "Vera", TRACK_SAYS, VOICE_SAYS["Vera"], "Vera", VOICE_SAYS["Vera"])
lines = [x.rstrip() for x in out.splitlines()]
check("the log names the person on two cameras and the voice's camera",
      lines.count(wanted.rstrip()) == 1,
      "stands %d times, wanted once: %r" % (lines.count(wanted.rstrip()),
                                            wanted.strip()[:70]))

print("\n3. The cut list and the handover seat her once")
shots = []
if os.path.exists(CUT):
    with open(CUT, encoding="utf-8", newline="") as f:
        # Shot, Camera, Speaker, Start TC, End TC, Duration s
        shots = [(row[1], row[2]) for row in list(csv.reader(f))[1:]]
print("   ", len(shots), "shots:", shots)
vera_on = sorted({cam for cam, cell in shots if "Vera" in cell.split(" + ")})
check("the cut list shows Vera on the voice's camera and no other",
      vera_on == [VOICE_SAYS["Vera"]], "on %s, wanted %s"
      % (vera_on or "nothing", VOICE_SAYS["Vera"]))

handover = {}
if os.path.exists(JS):
    with open(JS, encoding="utf-8") as f:
        handover = json.load(f)
sits = {cam.get("camera"): sorted(cam.get("speakers") or [])
        for cam in (handover.get("cameras") or [])}
print("   ", sits)
holding = sorted(c for c, names in sits.items() if "Vera" in names)
check("the handover's table names Vera under the voice's camera only",
      holding == [VOICE_SAYS["Vera"]], "under %s, wanted %s"
      % (holding or "none", VOICE_SAYS["Vera"]))
shown = [(x.get("start"), x.get("end"), x.get("camera"))
         for x in (handover.get("cut") or [])]


def picture_at(cut, t):
    """Which camera a cut of (start, end, camera) shows at that moment."""
    for a, b, cam in cut:
        if a <= t < b:
            return cam
    return "nothing"


sections = {e.get("name"): e.get("sections") or []
            for e in (handover.get("speakers") or [])}
in_cut = sorted({picture_at(shown, (a + b) / 2.0)
                 for a, b in sections.get("Vera", [])})
check("the handover's cut shows the voice's camera while Vera speaks",
      in_cut == [VOICE_SAYS["Vera"]], "it shows %s, wanted %s"
      % (in_cut or "nothing", VOICE_SAYS["Vera"]))

# The camera she left: whatever the rule makes of it, the cut list and
# the handover have to make the same. Where nobody speaks the cut list
# shows its wide shot; the handover marks its own.
quiet_on = sorted({cam for cam, cell in shots if not cell.strip()})
marked = sorted(cam.get("camera") for cam in (handover.get("cameras") or [])
                if cam.get("wide"))
check("the cut list's wide shot is the one the handover marks",
      quiet_on == marked,
      "the cut list shows the quiet on %s, the handover marks %s"
      % (quiet_on or "nothing", marked or "none"))

print("\n4. The preview and the rebuilt cut agree with the run")
# The preview names a camera by its track, and two cameras can carry
# one track name: each track is turned back into every camera it names.
cameras_of = {}
for cam in (handover.get("cameras") or []):
    cameras_of.setdefault(cam.get("track"), []).append(cam.get("camera"))
# Without the edges, as the run was started: the opening is Vera's.
numbers = vpm.cut_statistics(handover, edge=False) if handover else None
seen = sorted({c for a, b in sections.get("Vera", [])
               for c in cameras_of.get(picture_at(
                   (numbers or {}).get("cut") or [], (a + b) / 2.0),
                   ["nothing"])})
check("the preview shows the voice's camera while Vera speaks",
      seen == [VOICE_SAYS["Vera"]], "it shows %s, wanted %s"
      % (seen or "nothing", VOICE_SAYS["Vera"]))

# The button: a project file beside the handover, and the command line
# emptied, because a value typed there beats the file's.
with open(OUT + "/videopodcast-magic_MT.json", "w", encoding="utf-8") as f:
    json.dump({"production": "MT", "wide_at_edges": False}, f)
# The button needs a clock and this material carries none, so the
# copy gets one at zero; its cut is emptied, so only a rebuilt one counts.
again = json.loads(json.dumps(handover))
if again.get("start_s") is None:
    again["start_s"] = 0.0
again["cut"] = []
kept, sys.argv[1:] = sys.argv[1:], []
try:
    with contextlib.redirect_stdout(io.StringIO()):
        reason = vpm.refresh_cut_list(again, JS) if handover else "no file"
finally:
    sys.argv[1:] = kept
rebuilt = [(x.get("start"), x.get("end"), x.get("camera"))
           for x in (again.get("cut") or [])]
there_now = sorted({picture_at(rebuilt, (a + b) / 2.0)
                    for a, b in sections.get("Vera", [])})
check("the rebuilt cut list shows the voice's camera while Vera speaks",
      not reason and there_now == [VOICE_SAYS["Vera"]],
      "it shows %s, wanted %s; the button said %r"
      % (there_now or "nothing", VOICE_SAYS["Vera"], reason))

print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
