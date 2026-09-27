# -*- coding: utf-8 -*-
"""The voice proposals count "+30" from where every camera runs, as the run.

No file carries a clock; the recorders roll first, the cameras later,
and one voice talks only before "+30" from every camera. Sections: the
window the proposals use; what they propose from it; a camera set to
"ignore this video" no longer counting. The limit: the axis is handed
in -- window_zero_as_run holds that zero to the run.
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
# Seconds on the axis: the recorders at 0, the wide camera at 10 for
# 140 s, the guest camera at 25 for 115 s -- every camera from 25 on.
WIDE_ROLLS, WIDE_RUNS = 10.0, 140.0
GUEST_ROLLS, GUEST_RUNS = 25.0, 115.0
IN, OUT = "+0:00:30", "+0:01:50"
# Where the window has to start on the axis: 30 s after every camera
# runs, and with the guest camera ignored, 30 s after the wide one.
EVERY_CAMERA_IN = 55.0
WIDE_ONLY_IN = 40.0
NEAR = 0.01
FOLDER = tempfile.mkdtemp(prefix="vpm_voicezero_")
REC = os.path.join(FOLDER, "Presenter_REC00021.wav")
PLAIN = os.path.join(FOLDER, "Guest_REC00022.wav")
WIDE = os.path.join(FOLDER, "WideCam_C001.mov")
GUEST = os.path.join(FOLDER, "GuestCam_C002.mov")
for path in (REC, PLAIN):
    with wave.open(path, "wb") as f:
        f.setnchannels(1)
        f.setsampwidth(2)
        f.setframerate(8000)
        f.writeframes(b"\x00\x00" * 8000)
for path, seconds in ((WIDE, WIDE_RUNS), (GUEST, GUEST_RUNS)):
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i",
                    "color=size=64x36:rate=25", "-t", str(seconds),
                    "-c:v", "libx264", "-preset", "ultrafast", path],
                   check=True)

# V2 talks from 31 to 54 on the axis only; V0 asks and V1 answers from
# 56 on. Each passage is one sentence, a second apart.
PARTS = {"V0": [], "V1": [], "V2": []}
WORDS = []
t = 31.0
while t < 54.0:
    PARTS["V2"].append((t, t + 0.8))
    WORDS.append(vpm.speech_word(t + 0.1, t + 0.6, "wort."))
    t += 1.1
t, k = 56.0, 0
while t < 148.0:
    who = "V0" if k % 2 == 0 else "V1"
    PARTS[who].append((t, t + 0.5))
    WORDS.append(vpm.speech_word(t + 0.1, t + 0.4,
                                 "wort?" if who == "V0" else "wort."))
    t += 1.0
    k += 1

# The proposals look the trimming up on the program when they call it,
# so a spy there reads where they put the window's start, on the axis.
seen = []
_real_window = vpm.apply_time_window


def window_spy(d, in_point, out_point):
    """The real trimming, with where it started noted down."""
    out = _real_window(d, in_point, out_point)
    seen.append((out[0].get("start_s"), out[1]))
    return out


vpm.apply_time_window = window_spy


def one_round(guest_kind):
    """One round of the proposals over fresh rows; the rows back."""
    state = {"speakers_local": [(n, PARTS[n]) for n in sorted(PARTS)],
             "speakers_source": REC, "speakers_words_by": {REC: WORDS},
             "axis": {vpm.path_key(REC): 0.0, vpm.path_key(PLAIN): 0.0,
                      vpm.path_key(WIDE): WIDE_ROLLS,
                      vpm.path_key(GUEST): GUEST_ROLLS},
             "clip_kinds": {WIDE: vpm.Value(vpm.TYPE_CONTENT),
                            GUEST: vpm.Value(guest_kind)}}
    assign = [((REC,), vpm.Value("Presenter"), vpm.Value(WIDE)),
              ((PLAIN,), vpm.Value("Guest"), vpm.Value(GUEST))]
    cameras = [(b, vpm.Value(""), vpm.Value(""), vpm.Value(""))
               for b in (WIDE, GUEST)]
    marks = vpm.voice_marks_of(state)
    rows = {}
    voices = []
    for i, label in enumerate(sorted(PARTS)):
        key = vpm.voice_key(REC, label)
        name, camera = vpm.Value(vpm.T('Speaker %d') % (i + 1)), \
            vpm.Value(WIDE)
        marks["name"][key], marks["camera"][key] = name.get(), camera.get()
        voices.append((key, name, camera))
        rows[label] = (name, camera)
    del seen[:]
    vpm.voice_suggest_round(state, voices, assign, cameras, IN, OUT)
    return rows


def said(rows):
    """Each voice's name and camera, in one line for a FAIL."""
    return ", ".join("%s %s on %s" % (n, rows[n][0].get(), "do not use"
                     if rows[n][1].get() == vpm.IGNORE_AUDIO else "camera")
                     for n in sorted(rows))


print("Both cameras count")
rows = one_round(vpm.TYPE_CONTENT)
start = seen[-1][0] if seen else None
check("the proposals' window starts 30 s after every camera runs",
      start is not None and abs(start - EVERY_CAMERA_IN) <= NEAR,
      "%d windows cut, the last from %s s on the axis, wanted %.1f s; "
      "complaint %r" % (len(seen), start, EVERY_CAMERA_IN,
                        seen[-1][1] if seen else None))
check("a voice heard only before that is proposed for do not use",
      rows["V2"][1].get() == vpm.IGNORE_AUDIO, said(rows))
check("the two talking inside it are named host and guest",
      rows["V0"][0].get() == vpm.T('Host')
      and rows["V1"][0].get() == vpm.T('Guest'), said(rows))

print("\nThe guest camera set to ignore this video")
rows = one_round(vpm.TYPE_IGNORED)
start = seen[-1][0] if seen else None
check("an ignored camera does not move where +30 counts from",
      start is not None and abs(start - WIDE_ONLY_IN) <= NEAR,
      "%d windows cut, the last from %s s on the axis, wanted %.1f s: "
      "the wide camera alone" % (len(seen), start, WIDE_ONLY_IN))

shutil.rmtree(FOLDER, ignore_errors=True)
print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
