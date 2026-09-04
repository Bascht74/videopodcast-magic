# -*- coding: utf-8 -*-
"""A multitrack run puts every voice on the camera the assignment names.

The voices are finer than the tracks: the two microphones stand in the
assignment as devices with no camera, and under the first camera's
sound a separation found three people -- two of them placed, the third
heard only in the room. In order: the run ends without an error and
without a traceback, the cut list, the list of speakers and the
handover for Resolve are all written, all three voices reach the cut
list, each of the two placed voices is cut to her or his own camera and
the third to the wide shot, a track with no camera of its own counts
for the speaking shares and still wins no shot, the handover's cut
shows the same three while they speak, and its table of cameras names
the same two and marks only the camera nobody sits on as the wide shot.

Nothing goes out: the run is given --without-auphonic and no key, so
there is nothing to send with. It is not asked of the log, because the
log cannot answer it -- a run that really reaches the service prints
neither its address nor a word about uploading.
"""
import os
import the_program
HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = the_program.SCRIPT
import csv, json, re, subprocess, sys, tempfile, time, wave
import numpy as np

# The same environment the suite gives every test, so a run by hand
# measures the same thing. The speaker separation stays off: this run
# is handed one in the assignment and must not fetch a second.
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
# The common window is LENGTH minus the latest camera start, so 36.5 s
# here. The alignment sets its sample points a couple of seconds apart
# and a window holding none of them is refused, so the length is not
# free: it has to hold five turns of five seconds with quiet between.
LENGTH = 40.0
# Where each camera's picture starts inside the recording.
LATE = {"CamOne": 0.0, "CamTwo": 2.0, "CamThree": 3.5}
# Turns with more than a second of quiet around each, and none shorter
# than MIN_EDIT_DURATION_S, under which a shot is merged into the next.
# Nothing before 3.5 s, where the common window begins. Vera and Wim
# have a microphone each; Xenia is the guest without one, heard only in
# the room.
TURNS = {"Vera": [(5, 10), (18, 23)],
         "Wim": [(11.5, 16.5), (24.5, 29.5)],
         "Xenia": [(31, 36.5)]}
# Who sits on which camera. This is what the assignment says, and what
# the cut list and the handover afterwards have to repeat.
ON = {"Vera": "CamOne", "Wim": "CamTwo"}
# Where the third one lands. Nothing points at CamThree -- no track and
# no voice -- so it is the wide shot of this run, and a voice with no
# camera of its own is shown there.
WIDE = "CamThree"
# What the two tracks are called in the assignment. Devices, not
# people: the run measures them and counts them for the speaking
# shares, and neither of them has a camera to be shown on.
DEVICES = ("Mic A", "Mic B")


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


D = tempfile.mkdtemp(prefix="vpmvoicecam_")
said = {n: voice(TURNS[n], i + 1) for i, n in enumerate(sorted(TURNS))}
room = said["Vera"] + said["Wim"] + said["Xenia"]
noise = np.random.default_rng(9).normal(0, 0.0004, int(LENGTH * RATE))
# Each microphone hears its own speaker and the room a fifth as loud.
# The room is what the cameras record, so the two lie on one axis.
write(D + "/Mic_A.wav", said["Vera"] + 0.2 * (room - said["Vera"]) + noise)
write(D + "/Mic_B.wav", said["Wim"] + 0.2 * (room - said["Wim"]) + noise)
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
                 the_program.text(), re.M)
# The two microphones are the tracks and carry no camera, so they are
# measured and counted but have no picture to win. The separation was
# made on the first camera's sound and found three voices; voices_of
# says where two of them sit, and Xenia is left out of it on purpose.
plan = {"format": int(form.group(1)) if form else 3, "created_by": "test",
        "production": "MT",
        "tracks_of": [{"audio": D + "/Mic_%s.wav" % k,
                       "blocks": [D + "/Mic_%s.wav" % k],
                       "speakers": name,
                       "camera": "", "camera_audio": False}
                      for k, name in zip(("A", "B"), DEVICES)],
        "cameras": [{"video": D + "/" + cam + ".mov", "name": cam}
                    for cam in sorted(LATE)],
        "speakers_of": {"source": D + "/CamOne.mov", "names": {},
                        "segments": [[n, a, b] for n in sorted(TURNS)
                                     for a, b in TURNS[n]]},
        "voices_of": {who: D + "/" + cam + ".mov"
                      for who, cam in ON.items()}}
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
# The end of it, on one line: the head of a traceback is a path, and a
# judgement that runs over three lines loses two of them in every report
# that keeps only the line saying FAIL.
check("and it prints no traceback", fell < 0,
      tail(out[fell:]) if fell >= 0 else "")

CUT = OUT + "/MT_cameracut.csv"
SAID = OUT + "/MT_speakers.csv"
JS = OUT + "/MT_resolve.json"
there = sorted(os.listdir(OUT)) if os.path.isdir(OUT) else "no folder"
check("the cut list was written", os.path.exists(CUT), str(there))
check("the list of speakers was written", os.path.exists(SAID), str(there))
check("the handover for Resolve was written", os.path.exists(JS),
      str(there))

print("\n2. The cut list puts every voice where the assignment put it")
shots = []
if os.path.exists(CUT):
    with open(CUT, encoding="utf-8", newline="") as f:
        # Shot, Camera, Speaker, Start TC, End TC, Duration s
        shots = [(row[1], row[2]) for row in list(csv.reader(f))[1:]]
print("   ", len(shots), "shots:", shots)


def voices_in(cell):
    """The names in one Speaker cell of the cut list, devices included."""
    return [n for n in str(cell or "").split(" + ") if n]


heard = {n for _cam, cell in shots for n in voices_in(cell)}
check("all three voices of the assignment reach the cut list",
      set(TURNS) <= heard, "found %s, wanted %s among them"
      % (sorted(heard), sorted(TURNS)))


def seated(who):
    """Which cameras the cut list puts one voice on, and in how many shots."""
    mine = [cam for cam, cell in shots if who in voices_in(cell)]
    return sorted(set(mine)), len(mine)


# The fault this is about did not lose a voice, it lost the seating: the
# run knew the three and put them all on one camera. A judgement per
# voice, and the voice written out rather than built from the data: the
# register reads the wording as it stands in the source, so one name
# holding two voices would go in as a single row -- and a row that has
# seen only one of the cases it names counts as done while half of it
# was never tried. The camera goes into the evidence, where it belongs.
where, count = seated("Vera")
check("Vera is cut to her own camera and to no other",
      where == [ON["Vera"]], "%d shots, on %s -- wanted %s"
      % (count, where or "nothing", ON["Vera"]))
where, count = seated("Wim")
check("Wim is cut to his own camera and to no other",
      where == [ON["Wim"]], "%d shots, on %s -- wanted %s"
      % (count, where or "nothing", ON["Wim"]))
where, count = seated("Xenia")
elsewhere = [cam for cam in where if cam != WIDE]
check("the voice with no camera of its own is on the wide shot",
      count > 0 and not elsewhere,
      "%d shots of hers, not on %s: %s"
      % (count, WIDE, elsewhere or "none"))

print("\n3. A track with no camera counts, and takes nothing from anybody")
# The two devices are in the cut and must stay in it: the owner's rule
# is that every speaker is taken into account. What they must not do is
# decide the picture, because there is nothing to cut to.
spoke = {}
if os.path.exists(SAID):
    with open(SAID, encoding="utf-8", newline="") as f:
        # Speaker, Start TC, End TC, Time from start, Duration s
        for row in list(csv.reader(f))[1:]:
            spoke.setdefault(row[0], []).append(float(row[4]))
print("   ", {n: "%.1f s in %d" % (sum(v), len(v))
              for n, v in sorted(spoke.items())})
check("Mic A counts for the shares though it has no camera",
      bool(spoke.get("Mic A")), "%.1f s in %d passages, against Vera's %.1f s"
      % (sum(spoke.get("Mic A") or [0]), len(spoke.get("Mic A") or []),
         sum(spoke.get("Vera") or [0])))
check("Mic B counts for the shares though it has no camera",
      bool(spoke.get("Mic B")), "%.1f s in %d passages, against Wim's %.1f s"
      % (sum(spoke.get("Mic B") or [0]), len(spoke.get("Mic B") or []),
         sum(spoke.get("Wim") or [0])))
# Mic A is heard in the same shots as Vera, because it is her
# microphone. The picture there is hers: it speaks the longer of the
# two and still has nothing to show.
took = []
for cam, cell in shots:
    names = voices_in(cell)
    if not set(names) & set(DEVICES):
        continue
    for name in names:
        if name in ON and cam != ON[name]:
            took.append("%s on %s instead of %s" % (cell, cam, ON[name]))
per_voice = {}
for cam, cell in shots:
    for name in voices_in(cell):
        per_voice.setdefault(name, {})
        per_voice[name][cam] = per_voice[name].get(cam, 0) + 1
check("a track with no camera wins no shot from one that has",
      not took, "%d of %d shots taken away: %s -- shots per voice %s"
      % (len(took), len(shots), sorted(set(took)) or "none", per_voice))

print("\n4. And the handover shows the same picture")
handover = {}
if os.path.exists(JS):
    with open(JS, encoding="utf-8") as f:
        handover = json.load(f)
shown = [(x.get("start"), x.get("end"), x.get("camera"))
         for x in (handover.get("cut") or [])]


def picture_at(t):
    """Which camera the handover shows at that moment."""
    for a, b, cam in shown:
        if a <= t < b:
            return cam
    return "nothing"


# The handover carries its own list of who speaks when. Held against its
# own cut, so this asks the file alone: in Resolve, is the picture during
# a voice that voice's camera?
picture = {}
for entry in (handover.get("speakers") or []):
    for a, b in (entry.get("sections") or []):
        picture.setdefault(entry.get("name"), set()).add(
            picture_at((a + b) / 2.0))
print("   ", {k: sorted(v) for k, v in picture.items()})
check("the handover shows Vera's camera while she speaks",
      picture.get("Vera") == {ON["Vera"]}, "it shows %s, wanted %s"
      % (sorted(picture.get("Vera") or ["nothing"]), ON["Vera"]))
check("the handover shows Wim's camera while he speaks",
      picture.get("Wim") == {ON["Wim"]}, "it shows %s, wanted %s"
      % (sorted(picture.get("Wim") or ["nothing"]), ON["Wim"]))
check("and the voice without one on the wide shot there too",
      picture.get("Xenia") == {WIDE},
      "it shows %s, wanted %s"
      % (sorted(picture.get("Xenia") or ["nothing"]), WIDE))

# The other half of the handover, and not the same question: beside the
# cut it carries a table of cameras, and Resolve reads a camera's colour
# and its mix source off that. Until 31.8.2026 the table was built from
# the tracks alone, so a camera the cut filled with a person came over
# as having nobody on it -- marked as the wide shot, and keyed on the
# timeline by the camera's name instead of the person's.
sits = {cam.get("camera"): sorted(cam.get("speakers") or [])
        for cam in (handover.get("cameras") or [])}
print("   ", sits)
check("the handover names Vera on her camera, not only in its cut",
      sits.get(ON["Vera"]) == ["Vera"], "%s carries %s"
      % (ON["Vera"], sits.get(ON["Vera"], "-- no such camera in the table")))
check("the handover names Wim on his camera, not only in its cut",
      sits.get(ON["Wim"]) == ["Wim"], "%s carries %s"
      % (ON["Wim"], sits.get(ON["Wim"], "-- no such camera in the table")))
marked = sorted(cam.get("camera") for cam in (handover.get("cameras") or [])
                if cam.get("wide"))
check("only the camera nobody sits on counts as the wide shot",
      marked == [WIDE], "marked wide: %s -- wanted only %s"
      % (marked or "none", WIDE))

print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
