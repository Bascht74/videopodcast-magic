# -*- coding: utf-8 -*-
"""Cameras alone carry the sound, the cut and the handover, on both paths.

No recorder: two cameras made here, each hearing its own person loud and
the other faint, turns of irregular length. The sections: Multitrack in
the window, both cameras set to their own sound, the window's own Start
-- the run done, each camera file and the handover carrying its
speaker's track, the cut following the turns, the log naming the
speakers read off the tracks; then one camera alone on a plain command
line -- its sound said and used as the mix, the whole cut on it, and the
sound files the handover names still there after the run.
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
import json
import re
import shutil
import subprocess
import tempfile
import time
import the_program
import way_ground as ground

SCRIPT = the_program.SCRIPT
began = time.time()
done = 0
bad = []


def check(name, ok, extra=""):
    global done
    done += 1
    print("  %-58s %s %s" % (name, "ok" if ok else "FAIL", extra))
    if not ok:
        bad.append("%s [%s]" % (name, extra or "no numbers"))


def stop():
    """Nothing further can be asked, so count what there is and go."""
    print("\n%d checks in %.2f s" % (done, time.time() - began))
    print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
    sys.exit(1 if bad else 0)


STORE = tempfile.mkdtemp(prefix="vpm_camcut_store_")
os.environ["VPM_CACHE"] = STORE
os.environ["QT_QPA_PLATFORM"] = "offscreen"
from PySide6 import QtWidgets
app = QtWidgets.QApplication(sys.argv[:1])
vpm = the_program.load()
vpm.set_language("en")
vpm.list_presets = lambda key: []
vpm.load_api_key = lambda: ""
vpm.words_at_hand = lambda *a, **k: []
vpm.recognise_speech = lambda *a, **k: ([], "")

# Who speaks when, in seconds of the room; irregular, so that no stretch
# of the sound repeats and places a camera twice.
TURNS = {"Guest": [(1.0, 5.5), (12.5, 18.5), (24.0, 29.5)],
         "Presenter": [(6.5, 11.5), (19.5, 23.0)]}
# The guest's camera rolls with the room, the presenter's 2 s later, and
# the handover counts from where both have picture: the room's second 2.
# So the middle of each turn, in the handover's seconds:
MIDDLES = {"Guest": [1.25, 13.5, 24.75], "Presenter": [7.0, 19.25]}
CAMERA = {"Guest": "GuestCam_C001", "Presenter": "PresenterCam_C002"}
ROLLS = {"Guest": 0.0, "Presenter": 2.0}
CLOCK = {"Guest": "10:00:00:00", "Presenter": "10:00:02:00"}
LENGTH = 30.0
# One noise per person, the same in both cameras: the faint one in the
# other camera is the same voice, as bleed is.
SEED = {"Guest": 7101, "Presenter": 7202}
# Bounded so that a tool that never answers is named in the line.
ASK = 120.0


def voice(who, level):
    """One person as ffmpeg's noise shaped like speech, on while talking."""
    on = "+".join("between(t,%g,%g)" % t for t in TURNS[who])
    return ("anoisesrc=c=white:r=48000:d=%g:a=0.9:seed=%d,highpass=f=120,"
            "lowpass=f=4600,tremolo=f=5.5:d=0.55,volume=eval=frame:"
            "volume='%s',volume=%g" % (LENGTH, SEED[who], on, level))


def camera(folder, who, other, seed):
    """A camera hearing *who* loud and *other* faint over a quiet room."""
    wav = os.path.join(folder, who + ".wav")
    mov = os.path.join(folder, CAMERA[who] + ".mov")
    for argv in (["-filter_complex", "%s[a];%s[b];anoisesrc=c=pink:r=48000:"
                  "d=%g:a=0.9:seed=%d,volume=0.004[r];[a][b][r]amix="
                  "inputs=3:normalize=0" % (voice(who, 0.3),
                                            voice(other, 0.06), LENGTH,
                                            seed),
                  "-ac", "1", "-c:a", "pcm_s16le", wav],
                 ["-f", "lavfi", "-i", "testsrc=size=160x90:rate=25:"
                  "duration=%g" % (LENGTH - ROLLS[who]), "-ss",
                  str(ROLLS[who]), "-i", wav, "-map", "0:v", "-map", "1:a",
                  "-c:v", "libx264", "-preset", "ultrafast", "-pix_fmt",
                  "yuv420p", "-c:a", "aac", "-timecode", CLOCK[who],
                  "-shortest", mov]):
        made = subprocess.run(["ffmpeg", "-v", "error", "-y"] + argv,
                              stdout=subprocess.PIPE,
                              stderr=subprocess.STDOUT, timeout=ASK)
        # A precondition of the material, not a judgement.
        assert made.returncode == 0, made.stdout
    os.remove(wav)
    return mov


def track_names(path):
    """The names of a file's audio tracks, in order; None if unanswered."""
    try:
        out = subprocess.run(
            ["ffprobe", "-v", "error", "-select_streams", "a",
             "-show_entries", "stream_tags=handler_name", "-of", "json",
             path], stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
            timeout=ASK).stdout
        return [(s.get("tags") or {}).get("handler_name", "")
                for s in json.loads(out or b"{}").get("streams", [])]
    except (subprocess.TimeoutExpired, ValueError):
        return None


def handover(out, production):
    """The handover a run wrote, or {} where there is none."""
    try:
        with open(os.path.join(out, "%s_resolve.json" % production),
                  encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError):
        return {}


def shot_at(cut, second):
    """The camera the cut shows at *second*, or "" where none does."""
    for shot in cut:
        if shot["start"] <= second < shot["end"]:
            return shot["camera"]
    return ""


WORK = ground.own_folder("camcut")
try:
    PICTURES = {"Guest": camera(WORK, "Guest", "Presenter", 7303),
                "Presenter": camera(WORK, "Presenter", "Guest", 7404)}

    print("1. Multitrack in the window, the cameras' own sound")
    OUT = os.path.join(WORK, "window")
    os.makedirs(OUT)
    os.makedirs(os.path.join(WORK, "project"))
    project = os.path.join(WORK, "project", "videopodcast-magic_Own.json")
    # Each camera's Camera audio on "use internal audio", and its row
    # named for the person it hears loud: what a user sets in the window.
    assignment = {}
    for who, path in PICTURES.items():
        assignment["own:" + os.path.abspath(path)] = True
        assignment["ownname:" + os.path.abspath(path)] = who
    with open(project, "w", encoding="utf-8") as f:
        json.dump({"format": vpm.FILE_FORMAT, "version": "test",
                   "timeline": [], "preset": "", "production": "Own",
                   "project_type": "cut", "multitrack": True,
                   "wide_at_edges": False, "out_folder": OUT,
                   "assignment": assignment,
                   "files": [{"path": p, "kind": "video"}
                             for p in PICTURES.values()]}, f)
    kept = ground.window_run(vpm, app, project, {})
    text = "".join(kept["log"])
    finished = vpm.run_done_text(False).strip()
    errors = vpm.T('\nFinished with errors.\n').strip()
    check("cameras alone with their own sound run through the window",
          finished in text and errors not in text,
          "'%s' %s, '%s' %s; loop %s, %s"
          % (finished[:40], "said" if finished in text else "not said",
             errors, "said" if errors in text else "not said",
             "back" if kept["ended"] else "never back",
             kept["why"] or "nothing given up"))
    have = dict((who, track_names(os.path.join(
        OUT, CAMERA[who] + "_audio.mov"))) for who in PICTURES)
    check("each camera file carries its speaker's track and the Full-Mix",
          all((have[who] or [])[:2] == [who, vpm.MIX_TRACK_NAME]
              for who in PICTURES),
          "tracks %s against speaker then %s"
          % (have, vpm.MIX_TRACK_NAME))
    given = handover(OUT, "Own")
    tracks_of = dict((c.get("camera"), c.get("track"))
                     for c in given.get("cameras", []))
    check("the handover gives each camera its own speaker's track",
          all(tracks_of.get(CAMERA[who]) == who for who in PICTURES),
          "camera -> track %s against %s" % (tracks_of, CAMERA))
    shown = dict((who, [shot_at(given.get("cut", []), s)
                        for s in MIDDLES[who]]) for who in MIDDLES)
    check("the cut shows each turn on the camera of the one who speaks",
          all(set(shown[who]) == {CAMERA[who]} for who in MIDDLES),
          "at the turns' middles %s, shown %s; the cut %s"
          % (MIDDLES, shown, [(s["start"], s["end"], s["camera"])
                               for s in given.get("cut", [])]))
    READ = vpm.T('  From the tracks themselves, one voice per track: %s.'
                 ).strip() % "Guest, Presenter"
    check("the log says the speakers were read off the cameras' tracks",
          READ in text, "'%s' %s" % (READ, "said" if READ in text
                                     else "not said"))

    print("\n2. One camera alone on the command line, the plain path")
    OUT = os.path.join(WORK, "line")
    code, said, stuck = ground.line_run(
        [sys.executable, SCRIPT, "--without-auphonic",
         "--no-speech-recognition", "--project-type", "cut",
         "--production", "Lone", "--out", OUT, PICTURES["Presenter"]],
        os.path.join(WORK, "cache"))
    said = re.sub(r"\x1b\[[0-9;]*m", "", said)
    tail = " / ".join(x.strip() for x in said.replace(OUT, "<out>").replace(
        os.path.realpath(tempfile.gettempdir()), "<tmp>").replace(
        tempfile.gettempdir(), "<tmp>").splitlines() if x.strip())[-200:]
    check("a lone camera with its sound and no recording runs through",
          code == 0 and not stuck,
          "returned %r, stood still %s; it ended: %s" % (code, stuck, tail))
    HEAD = vpm.T('NO AUDIO FILE -- USING THE CAMERA AUDIO')
    FROM = vpm.T('  from %s, %s').strip().split(",")[0] % (
        CAMERA["Presenter"] + ".mov")
    check("the log says the camera's own sound is used, and whose",
          HEAD in said and FROM in said,
          "'%s' %s, '%s' %s" % (HEAD, "said" if HEAD in said else
                                "not said", FROM, "said" if FROM in said
                                else "not said"))
    given = handover(OUT, "Lone")
    cams = [(c.get("camera"), c.get("audio_tracks"))
            for c in given.get("cameras", [])]
    cut = [(s["start"], s["end"], s["camera"]) for s in given.get("cut", [])]
    WHOLE = LENGTH - ROLLS["Presenter"]
    check("the lone camera carries the Full-Mix and the whole cut",
          cams == [(CAMERA["Presenter"], [vpm.MIX_TRACK_NAME])]
          and {c for _a, _b, c in cut} == {CAMERA["Presenter"]}
          and cut[0][0] == 0.0 and cut[-1][1] == WHOLE
          and all(a[1] == b[0] for a, b in zip(cut, cut[1:])),
          "cameras %s against %s; cut %s against that camera from 0 to "
          "%.1f s without a gap"
          % (cams, [(CAMERA["Presenter"], [vpm.MIX_TRACK_NAME])], cut,
             WHOLE))
    sound = sorted((given.get("audio_files") or {}).items())
    gone = [name for name, path in sound if not os.path.isfile(path)]
    check("the sound files the handover names are there after the run",
          sound and not gone, "%d named, missing: %s"
          % (len(sound), gone or "none"))
except Exception:
    import traceback
    traceback.print_exc()
    bad.append("the test itself broke off")

shutil.rmtree(WORK, ignore_errors=True)
shutil.rmtree(STORE, ignore_errors=True)
stop()
