# -*- coding: utf-8 -*-
"""A recording at any sample rate lands on the axis whole and in its place.

Four recordings of one conversation at 16, 44.1, 48 and 96 kHz, each
begun at another moment of it, and three 48 kHz cameras begun later.
With the cameras the run comes back with 0, every recording and the
Full-Mix get a track beside them, each as long as the common window and
beginning where it does, and every track in a camera file sits on that
camera's own sound. Without them the run comes back with 0, and every
track is as long as all heard and begins with the earliest recording --
each place read by cross correlation against the conversation itself.
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
import glob, shutil, subprocess, tempfile, time
import numpy as np
import the_program

SCRIPT = the_program.SCRIPT
ENV = dict(os.environ, LANG="C", LC_ALL="C", LANGUAGE="en", VPM_SILENT="1",
           VPM_NO_UPDATE_CHECK="1", VPM_NO_SPEAKER_SPLIT="1",
           QT_QPA_PLATFORM="offscreen")

began = time.time()
done = 0
bad = []


def check(name, ok, extra=""):
    global done
    done += 1
    print("  %-58s %s %s" % (name, "ok" if ok else "FAIL", extra))
    if not ok:
        bad.append("%s [%s]" % (name, extra or "no numbers"))


#------------------------------------------------------------- Material

# Two synthetic voices taking turns, checked in: speech, so the sound
# places it, and 31.452 s long.
TALK = os.path.join(HERE, "samples", "twovoices", "talk.wav")
# Each recording at a rate of its own and begun this far into the
# conversation. 48 kHz is the working rate and stands beside the others,
# so a repair that moves it is caught too.
RECORDINGS = {"Presenter": (16000, 0.0), "Guest": (44100, 0.25),
              "CoPresenter": (96000, 0.5), "Room": (48000, 0.1)}
# Where each camera's picture begins in the conversation; 34 s each.
CAMERAS = {"Cam1": 0.6, "Cam2": 0.9, "Cam3": 0.4}
CAM_LEN = 34.0
# The common window runs from the latest camera start, 0.9 s, to the
# earliest camera end, 0.4 + 34 s: that is where every track begins
# in the conversation, and how long each one is.
WINDOW_AT, WINDOW_LEN = 0.9, 33.5
# Without a picture the window is everything any recording heard: from
# the earliest start, 0.0 s, to the end of the conversation.
HEARD_AT, HEARD_LEN = 0.0, 31.452
# Read at 8 kHz, a step is 0.125 ms. A length may differ by rounding a
# sample at either end, a place by the resampler's filter.
LONG_BY, OFF_BY = 0.005, 0.002
READ_RATE = 8000


def run(out, files):
    """One run over *files* into *out*: its return code and its log.

    The work folder is cut out of the log: a red line carries what was
    said, not the path of a temporary folder with somebody's name in it.
    """
    p = subprocess.run(
        [sys.executable, SCRIPT, "--without-auphonic",
         "--no-speech-recognition", "--no-transcript-file", "--no-metrics",
         "--out", out] + files, capture_output=True, text=True,
        errors="replace", timeout=1800, env=ENV)
    return p.returncode, ((p.stdout or "") + (p.stderr or "")).replace(
        D, "<work>")


def heard(path, stream=0):
    """One audio stream of a file, mono at READ_RATE, or None."""
    p = subprocess.run(["ffmpeg", "-v", "error", "-i", path, "-map",
                        "0:a:%d" % stream, "-ac", "1", "-ar", str(READ_RATE),
                        "-f", "f32le", "-"], capture_output=True)
    x = np.frombuffer(p.stdout, "<f4").astype(float)
    return x if p.returncode == 0 and len(x) else None


def begins_at(reference, track):
    """Where in *reference* the first sample of *track* was taken, in s."""
    n = 1 << int(np.ceil(np.log2(len(reference) + len(track))))
    c = np.fft.irfft(np.fft.rfft(reference, n)
                     * np.conj(np.fft.rfft(track, n)), n)
    k = int(np.argmax(np.abs(c)))
    return (k - n if k > n // 2 else k) / float(READ_RATE)


def streams(path):
    """How many audio streams a file carries."""
    p = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "a",
                        "-show_entries", "stream=index", "-of", "csv=p=0",
                        path], capture_output=True, text=True)
    return len(p.stdout.split())


def tail(log, n=2):
    rows = [x.strip() for x in log.splitlines() if x.strip()]
    return " | ".join(rows[-n:])[-160:]


def rate_of(name):
    return "%g kHz" % (RECORDINGS[name][0] / 1000.0) \
        if name in RECORDINGS else "mix"


D = None
try:
    D = tempfile.mkdtemp(prefix="vpm_ownrate_")
    MEDIA = os.path.join(D, "media")
    os.makedirs(MEDIA)
    # One ffmpeg for every file, because a process start is what the
    # Windows builder charges for: each output carries its own filter.
    build = ["ffmpeg", "-v", "error", "-y", "-i", TALK, "-f", "lavfi", "-i",
             "smptebars=size=160x90:rate=25:duration=%g" % CAM_LEN]
    for name, (rate, at) in sorted(RECORDINGS.items()):
        build += ["-map", "0:a", "-af",
                  "aresample=%d,atrim=start=%g,asetpts=N/SR/TB" % (rate, at),
                  "-c:a", "pcm_s24le", os.path.join(MEDIA, name + ".wav")]
    for cam, at in sorted(CAMERAS.items()):
        build += ["-map", "1:v", "-map", "0:a", "-af",
                  "aresample=48000,atrim=start=%g,asetpts=N/SR/TB,"
                  "apad=whole_dur=%g" % (at, CAM_LEN),
                  "-c:v", "libx264", "-preset", "ultrafast", "-pix_fmt",
                  "yuv420p", "-c:a", "pcm_s16le", "-t", "%g" % CAM_LEN,
                  os.path.join(MEDIA, cam + ".mov")]
    subprocess.run(build, check=True)

    talk = heard(TALK)
    recordings = [os.path.join(MEDIA, n + ".wav")
                  for n in sorted(RECORDINGS)]
    cameras = [os.path.join(MEDIA, c + ".mov") for c in sorted(CAMERAS)]

    #--------------------------------------------------------- With a picture
    print("With the cameras")
    out = os.path.join(D, "with")
    rc, log = run(out, recordings + cameras)
    check("the run with the cameras comes back with 0",
          rc == 0 and "Traceback" not in log,
          "return code %d, the last it said: %r" % (rc, tail(log)))
    WANT = sorted(["final_%s.wav" % n for n in RECORDINGS]
                  + ["final_Full-Mix.wav"])
    beside = os.path.join(out, "auphonic-tracks")
    made = sorted(os.path.basename(p)
                  for p in glob.glob(os.path.join(beside, "final_*.wav")))
    check("every recording and the Full-Mix get a track beside them",
          made == WANT, "wanted %s, found %s" % (WANT, made))
    lengths, places = [], []
    for f in made:
        name = f[len("final_"):-len(".wav")]
        x = heard(os.path.join(beside, f))
        if x is None:
            lengths.append((name, rate_of(name), "unreadable"))
            continue
        lengths.append((name, rate_of(name),
                        round(len(x) / float(READ_RATE), 3)))
        places.append((name, rate_of(name), round(begins_at(talk, x), 4)))
    wrong = [t for t in lengths if not isinstance(t[2], float)
             or abs(t[2] - WINDOW_LEN) > LONG_BY]
    check("every track beside the cameras is as long as the window",
          bool(lengths) and not wrong,
          "%d of %d off, wanted %.3f s: %s"
          % (len(wrong), len(lengths), WINDOW_LEN, wrong or lengths))
    wrong = [t for t in places if abs(t[2] - WINDOW_AT) > OFF_BY]
    check("every track beside the cameras begins where the window does",
          bool(places) and not wrong,
          "%d of %d off, wanted %.3f s into the conversation: %s"
          % (len(wrong), len(places), WINDOW_AT, wrong or places))
    # A camera file carries the Full-Mix, every recording, and last the
    # camera's own sound, which was cut with the picture: each track has to
    # begin where that one does.
    seated = []
    for cam in sorted(CAMERAS):
        path = os.path.join(out, cam + "_audio.mov")
        n = streams(path) if os.path.exists(path) else 0
        own = heard(path, n - 1) if n > 1 else None
        if own is None:
            seated.append((cam, "%d audio streams" % n))
            continue
        for k in range(n - 1):
            x = heard(path, k)
            seated.append((cam, k + 1, None if x is None
                           else round(begins_at(own, x) * 1000.0, 1)))
    wrong = [t for t in seated if len(t) < 3 or t[2] is None
             or abs(t[2]) > OFF_BY * 1000.0]
    check("every track in a camera file sits on that camera's own sound",
          len(seated) == len(CAMERAS) * (len(RECORDINGS) + 1) and not wrong,
          "%d of %d off by more than %.0f ms (camera, track, ms): %s"
          % (len(wrong), len(seated), OFF_BY * 1000.0, wrong or seated))

    #------------------------------------------------------ Without a picture
    print("\nWithout the cameras")
    out = os.path.join(D, "without")
    rc, log = run(out, recordings)
    check("the run without the cameras comes back with 0",
          rc == 0 and "Traceback" not in log,
          "return code %d, the last it said: %r" % (rc, tail(log)))
    lengths, places = [], []
    for name in sorted(RECORDINGS):
        x = heard(os.path.join(out, name + "_aligned.wav"))
        if x is None:
            lengths.append((name, rate_of(name), "missing"))
            continue
        lengths.append((name, rate_of(name),
                        round(len(x) / float(READ_RATE), 3)))
        places.append((name, rate_of(name), round(begins_at(talk, x), 4)))
    wrong = [t for t in lengths if not isinstance(t[2], float)
             or abs(t[2] - HEARD_LEN) > LONG_BY]
    check("without the cameras every track is as long as all heard",
          not wrong, "%d of %d off, wanted %.3f s: %s"
          % (len(wrong), len(lengths), HEARD_LEN, wrong or lengths))
    wrong = [t for t in places if abs(t[2] - HEARD_AT) > OFF_BY]
    check("without the cameras every track begins with the earliest",
          bool(places) and not wrong,
          "%d of %d off, wanted %.3f s into the conversation: %s"
          % (len(wrong), len(places), HEARD_AT, wrong or places))

except Exception as e:
    # A crash ends the runs, not the count: it goes out below.
    bad.append("the runs crashed [%r]" % e)
    print("  the runs crashed: %r" % e)
finally:
    if D:
        shutil.rmtree(D, ignore_errors=True)
print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
