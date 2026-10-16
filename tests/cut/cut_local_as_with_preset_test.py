# -*- coding: utf-8 -*-
"""Without auphonic.com one recording's voices are cut as with a preset.

What the hint under the preset list promises: "work without Auphonic"
costs the sound its de-bleed, leveler and noise removal and the cut
nothing, also where one recording holds everybody. In order: the run
without auphonic.com writes its cut list, each voice on its camera
there; the run on the tracks auphonic.com hands back writes one too;
and the two are the same, shot for shot. Each run has a store of its
own, so the second measures afresh. Nothing goes out: no key, and
--auphonic-done hands in what an upload would have brought back.
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
import csv, json, re, shutil, subprocess, tempfile, time, wave
import numpy as np

# The environment the suite gives every test, so a run by hand measures
# the same thing. The separation stays off: it is handed over in the
# assignment, as the window hands it, and no second one is fetched.
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
# Long enough for five turns of five seconds with quiet between, inside
# the window the three cameras share: it begins where the last one does.
LENGTH = 40.0
LATE = {"GuestCam_C001": 0.0, "PresentersCam_C002": 2.0,
        "WideCam_C003": 3.5}
# Both people speak into the one recording and nowhere else; none of
# the turns is shorter than MIN_EDIT_DURATION_S or overlaps another.
TURNS = {"Guest": [(5.0, 10.0), (18.0, 23.0), (31.0, 36.5)],
         "Presenter": [(11.5, 16.5), (24.5, 29.5)]}
# The voices' cameras, as the table under the recording sets them.
# Nobody sits on the third, so it is the wide shot.
ON = {"Guest": "GuestCam_C001", "Presenter": "PresentersCam_C002"}


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


D = tempfile.mkdtemp(prefix="vpmlocalcut_")
ROOM = D + "/Room_REC00031.wav"
noise = np.random.default_rng(9).normal(0, 0.0004, int(LENGTH * RATE))
write(ROOM, 0.6 * (voice(TURNS["Guest"], 1) + voice(TURNS["Presenter"], 2))
      + noise)

# One ffmpeg call for the three cameras; each records the room, so the
# recording and the pictures lie on one axis. The -ss in front of each
# output is an output option and cuts that file alone.
build = ["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i",
         "smptebars=size=320x180:rate=25:duration=%.1f" % LENGTH,
         "-i", ROOM]
for cam in sorted(LATE):
    build += ["-ss", "%.2f" % LATE[cam],
              "-map", "0:v", "-map", "1:a", "-c:v", "libx264",
              "-preset", "ultrafast", "-pix_fmt", "yuv420p",
              "-c:a", "pcm_s16le", "-shortest", D + "/" + cam + ".mov"]
subprocess.run(build, check=True)

# The file format number read out of the program, not imported for it.
form = re.search(r"^FILE_FORMAT = (\d+)", the_program.text(), re.M)
# One recording with no camera of its own, and under it the separation
# the window made and the camera it gave each voice.
plan = {"format": int(form.group(1)) if form else 3, "created_by": "test",
        "production": "MT",
        "tracks_of": [{"audio": ROOM, "blocks": [ROOM], "speakers": "Room",
                       "camera": "", "camera_audio": False}],
        "cameras": [{"video": D + "/" + cam + ".mov", "name": cam}
                    for cam in sorted(LATE)],
        "speakers_of": {"source": ROOM, "names": {},
                        "segments": [[n, a, b] for n in sorted(TURNS)
                                     for a, b in TURNS[n]]},
        "voices_of": dict((n, D + "/" + cam + ".mov")
                          for n, cam in ON.items())}
with open(D + "/assign.json", "w", encoding="utf-8") as f:
    json.dump(plan, f)
# What auphonic.com hands back: the track under the recording's name.
# The sound does not decide the cut, so it is the recording itself.
os.makedirs(D + "/returned")
shutil.copyfile(ROOM, D + "/returned/Room.wav")


def run(name, *switches):
    """One run as a person starts it: (return code, output, cut rows).

    A store of its own, so nothing one run measured reaches the other.
    The rows are the cut list's camera, speaker, start and end.
    """
    out = D + "/out_" + name
    env = dict(ENV, VPM_CACHE=D + "/cache_" + name)
    call = [sys.executable, SCRIPT] + list(switches) + [
        "--assign", D + "/assign.json", "--out", out, "--no-metrics",
        "--no-speech-recognition", "--no-transcript-file",
        "--no-wide-edges", ROOM] \
        + [D + "/" + c + ".mov" for c in sorted(LATE)]
    rc, said = 1, ""
    try:
        p = subprocess.run(call, capture_output=True, text=True,
                           timeout=900, env=env)
        rc, said = p.returncode, (p.stdout or "") + (p.stderr or "")
    except subprocess.TimeoutExpired as e:
        said = "the run was still going after 900 s: %s" % tail(
            (e.stdout or b"").decode("utf-8", "replace"))
    rows = None
    if os.path.exists(out + "/MT_cameracut.csv"):
        with open(out + "/MT_cameracut.csv", encoding="utf-8",
                  newline="") as f:
            # Shot, Camera, Speaker, Start TC, End TC, Duration s
            rows = [tuple(r[1:5]) for r in list(csv.reader(f))[1:]]
    return rc, said, rows


def ended(rc, said, rows):
    """The words for how a run ended; its last lines where one went wrong."""
    fell = said.find("Traceback")
    whole = rc == 0 and fell < 0 and rows is not None
    return "returned %d, %s, cut list %s%s" % (
        rc, "traceback" if fell >= 0 else "no traceback",
        "%d rows" % len(rows) if rows is not None else "missing",
        "" if whole else "; ends: " + tail(said[fell:] if fell >= 0
                                           else said))


#--------------------------------------------------------------- The runs

print("1. Without auphonic.com")
rc, said, local = run("local", "--without-auphonic")
check("the run without auphonic.com ends and writes its cut list",
      rc == 0 and "Traceback" not in said and local is not None,
      ended(rc, said, local))
local = local or []
print("   ", len(local), "shots:", [(c, s) for c, s, _a, _b in local])


def seated(who):
    """The cameras the cut list shows one name on, and in how many shots."""
    mine = [c for c, s, _a, _b in local if s == who]
    return sorted(set(mine)), len(mine)


g_where, g_count = seated("Guest")
p_where, p_count = seated("Presenter")
check("without auphonic.com one recording's voices reach their cameras",
      g_count > 0 and g_where == [ON["Guest"]]
      and p_count > 0 and p_where == [ON["Presenter"]],
      "Guest %d shots on %s, Presenter %d on %s -- wanted %s and %s"
      % (g_count, g_where or "nothing", p_count, p_where or "nothing",
         ON["Guest"], ON["Presenter"]))

print("\n2. On the tracks auphonic.com returns")
rc, said, returned = run("returned", "--auphonic-preset", "Stand-in preset",
                         "--auphonic-done", D + "/returned")
check("the run on what auphonic.com returns writes its cut list too",
      rc == 0 and "Traceback" not in said and returned is not None,
      ended(rc, said, returned))
returned = returned or []
apart = [i + 1 for i in range(max(len(local), len(returned)))
         if local[i:i + 1] != returned[i:i + 1]]
check("and without auphonic.com the cut is that one, shot for shot",
      bool(local) and not apart,
      "%d shots against %d, apart from shot %s: %s against %s"
      % (len(local), len(returned), apart[0] if apart else "-",
         local[apart[0] - 1:apart[0]] if apart else "-",
         returned[apart[0] - 1:apart[0]] if apart else "-"))

shutil.rmtree(D, ignore_errors=True)
print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
