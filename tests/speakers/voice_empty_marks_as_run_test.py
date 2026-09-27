# -*- coding: utf-8 -*-
"""With In or Out empty, the voice proposals hear only what every camera sees.

The recorders roll first, the three cameras one after another, the
first camera stops while the talking goes on. One voice talks only
before every camera runs, one only after the first camera stops.
Sections: both marks empty; In empty with an Out; Out empty with an
In. The limit: the axis is handed in, and the stretch itself is the
run's (camera_window) -- this holds the proposals to it.
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

import shutil
import subprocess
import tempfile
import time
import wave

os.environ["QT_QPA_PLATFORM"] = "offscreen"
vpm = the_program.load()
vpm.set_language("en")

began = time.time()
done = 0
bad = []


def check(name, ok, extra=""):
    global done
    done += 1
    print("  %-58s %s %s" % (name, "ok" if ok else "FAIL", extra))
    if not ok:
        bad.append("%s [%s]" % (name, extra or "no numbers"))


# ------------------------------------------------------------ the material
# Seconds on the axis: the recorders at 0; the wide camera rolls at 0
# for 150 s, the guest camera at 30 for 140, the presenter camera at 55
# for 130. Every camera runs from 55 to 150, where the wide one stops.
CAMERAS = (("WideCam_C001.mov", 0.0, 150.0),
           ("GuestCam_C002.mov", 30.0, 140.0),
           ("PresenterCam_C003.mov", 55.0, 130.0))
FOLDER = tempfile.mkdtemp(prefix="vpm_voiceempty_")
REC = os.path.join(FOLDER, "Presenter_REC00021.wav")
PLAIN = os.path.join(FOLDER, "Guest_REC00022.wav")
for path in (REC, PLAIN):
    with wave.open(path, "wb") as f:
        f.setnchannels(1)
        f.setsampwidth(2)
        f.setframerate(8000)
        f.writeframes(b"\x00\x00" * 8000)
CAMS = []
for name, _rolls, seconds in CAMERAS:
    path = os.path.join(FOLDER, name)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i",
                    "color=size=64x36:rate=25", "-t", str(seconds),
                    "-c:v", "libx264", "-preset", "ultrafast", path],
                   check=True)
    CAMS.append(path)

# EARLY talks from 1 to 54 on the axis only, LATE from 151 to 199 only;
# V0 asks and V1 answers from 56 to 149. One sentence a second.
PARTS = {"EARLY": [], "LATE": [], "V0": [], "V1": []}
WORDS = []
for who, t, until in (("EARLY", 1.0, 54.0), ("LATE", 151.0, 199.0)):
    while t < until:
        PARTS[who].append((t, t + 0.8))
        WORDS.append(vpm.speech_word(t + 0.1, t + 0.6, "wort."))
        t += 1.1
t, k = 56.0, 0
while t < 149.0:
    who = "V0" if k % 2 == 0 else "V1"
    PARTS[who].append((t, t + 0.5))
    WORDS.append(vpm.speech_word(t + 0.1, t + 0.4,
                                 "wort?" if who == "V0" else "wort."))
    t += 1.0
    k += 1


def one_round(in_point, out_point):
    """One round of the proposals over fresh rows; the rows back."""
    axis = {vpm.path_key(REC): 0.0, vpm.path_key(PLAIN): 0.0}
    for path, (_name, rolls, _seconds) in zip(CAMS, CAMERAS):
        axis[vpm.path_key(path)] = rolls
    state = {"speakers_local": [(n, PARTS[n]) for n in sorted(PARTS)],
             "speakers_source": REC, "speakers_words_by": {REC: WORDS},
             "axis": axis,
             "clip_kinds": {p: vpm.Value(vpm.TYPE_CONTENT) for p in CAMS}}
    assign = [((REC,), vpm.Value("Presenter"), vpm.Value(CAMS[0])),
              ((PLAIN,), vpm.Value("Guest"), vpm.Value(CAMS[1]))]
    cameras = [(b, vpm.Value(""), vpm.Value(""), vpm.Value(""))
               for b in CAMS]
    marks = vpm.voice_marks_of(state)
    rows = {}
    voices = []
    for i, label in enumerate(sorted(PARTS)):
        key = vpm.voice_key(REC, label)
        name, camera = vpm.Value(vpm.T('Speaker %d') % (i + 1)), \
            vpm.Value(CAMS[0])
        marks["name"][key], marks["camera"][key] = name.get(), camera.get()
        voices.append((key, name, camera))
        rows[label] = (name, camera)
    vpm.voice_suggest_round(state, voices, assign, cameras,
                            in_point, out_point)
    return rows


def unused(rows, label):
    """Whether the proposals set this voice to do not use."""
    return rows[label][1].get() == vpm.IGNORE_AUDIO


def said(rows):
    """Each voice's name and camera, in one line for a FAIL."""
    return ", ".join("%s %s on %s" % (n, rows[n][0].get(), "do not use"
                     if unused(rows, n) else "camera") for n in sorted(rows))


print("Both marks empty")
rows = one_round("", "")
check("a voice heard only before every camera runs is not used",
      unused(rows, "EARLY"), said(rows) + "; every camera from 55 s")
check("a voice heard only after the first camera stops is not used",
      unused(rows, "LATE"), said(rows) + "; the first camera stops at 150 s")
check("the two talking where every camera runs are host and guest",
      rows["V0"][0].get() == vpm.T('Host')
      and rows["V1"][0].get() == vpm.T('Guest')
      and not unused(rows, "V0") and not unused(rows, "V1"), said(rows))

print("\nIn point empty, Out point +0:01:00")
rows = one_round("", "+0:01:00")
check("an empty In point starts the proposals where every camera runs",
      unused(rows, "EARLY"), said(rows) + "; every camera from 55 s")

print("\nIn point +0:00:05, Out point empty")
rows = one_round("+0:00:05", "")
check("an empty Out point ends the proposals where a camera stops",
      unused(rows, "LATE"), said(rows) + "; the first camera stops at 150 s")

shutil.rmtree(FOLDER, ignore_errors=True)
print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
