# -*- coding: utf-8 -*-
"""A whole multitrack run that finishes on this machine alone.

Measure the time axis, take the bleed out of the speech detection, mix,
cut by speaker, write the files and the handover for Resolve -- all of
it here, with nothing leaving the house. The run is started with
--without-auphonic and a made-up key, and the test holds the program to
that: the log has to say what is missing, and a stand-in curl on the
search path sees nothing sent to auphonic.com. Windows starts no such
stand-in; there no key is given and that judgement is left out.
"""
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
import json, subprocess, sys, tempfile, time
import local_ground

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
vpm = the_program.load()

began = time.time()
done = 0
bad = []


def check(name, ok, extra=""):
    global done
    done += 1
    print("  %-58s %s %s" % (name, "ok" if ok else "FAIL", extra))
    if not ok:
        bad.append("%s [%s]" % (name, extra or "no numbers"))


# Its own folder under the run's TMPDIR, not the shared fixture root. The
# leaf keeps its name: the program names what it writes after the folder
# it was pointed at, and the checks below look for those names.
D = os.path.join(tempfile.mkdtemp(prefix="vpm_run_"), "localrun")
os.makedirs(D)
ASSIGN = local_ground.build(D, vpm.FILE_FORMAT)
TURNS, CAM_LATE = local_ground.TURNS, local_ground.CAM_LATE
ENV = dict(os.environ, LANG="C", LC_ALL="C")
curl_calls, WATCHED = local_ground.watched_curl(os.path.join(D, "bin"), ENV)
# A made-up key where the stand-in watches, so that --without-auphonic
# has something to hold back; without the stand-in no key is given.
KEY = ["--auphonic-api-key", "not-a-key-only-a-test"] if WATCHED else []
if WATCHED:
    ENV["AUPHONIC_TOKEN"] = KEY[1]

OUT = D + "/out"
print("1. The run goes through, and nothing leaves the house")
p = subprocess.run(
    [sys.executable, SCRIPT, "--multitrack", "--without-auphonic"] + KEY
    + ["--assign", ASSIGN, "--out", OUT, "--no-metrics",
       "--no-speech-recognition", "--no-transcript-file",
       "--no-wide-edges", D + "/Host.wav", D + "/Guest.wav",
       D + "/CamHost.mov", D + "/CamGuest.mov"],
    capture_output=True, text=True, timeout=900, env=ENV)
out = (p.stdout or "") + (p.stderr or "")
check("return code 0", p.returncode == 0, str(p.returncode))
check("no traceback", "Traceback" not in out,
        out[out.find("Traceback"):][:90])
said = out.count("WITHOUT AUPHONIC.COM")
check("it says what is missing", said > 0,
        "%d mentions of WITHOUT AUPHONIC.COM in %d characters of log, "
        "wanted at least 1" % (said, len(out)))
if WATCHED:
    # The address only: the rest of a call is a file of this machine.
    reached = [w for c in curl_calls() if "auphonic.com" in c
               for w in c.split() if "://" in w]
    check("nothing reached auphonic.com although a key was given",
          not reached, "%d calls to curl, %d of them to auphonic.com: %s"
          % (len(curl_calls()), len(reached), reached[:1]))
else:
    print("LEFT OUT: the stand-in curl is a #!/bin/sh file and this "
          "machine starts none of those, so no key was given and nothing "
          "watched whether the run reached auphonic.com.")
measured = out.count("Bleed measured")
apart = out.count("Bleed not separable")
check("the bleed was measured", measured > 0,
        "%d mentions of Bleed measured and %d of Bleed not separable in %d "
        "characters of log, wanted at least 1" % (measured, apart, len(out)))

print("\n2. The files are there")
made = sorted(os.listdir(OUT)) if os.path.isdir(OUT) else []
for tail in ("_speakers.csv", "_cameracut.csv", "_resolve.json"):
    check("WA%s written" % tail, os.path.exists(OUT + "/WA" + tail),
          "wanted WA%s; the %d files in out are %s" % (tail, len(made), made))
for name in ("CamHost_audio.mov", "CamGuest_audio.mov"):
    check("%s written" % name, os.path.exists(OUT + "/" + name),
          "wanted %s; the %d files in out are %s" % (name, len(made), made))
tracks = (sorted(os.listdir(OUT + "/auphonic-tracks"))
          if os.path.isdir(OUT + "/auphonic-tracks") else [])
check("the mix is there",
        os.path.exists(OUT + "/auphonic-tracks/final_Full-Mix.wav"),
        "wanted final_Full-Mix.wav; the %d files in auphonic-tracks are %s"
        % (len(tracks), tracks))


def rows_of(name):
    """The rows under a written table's head; none where it is missing."""
    path = os.path.join(OUT, name)
    if not os.path.exists(path):
        return []
    return open(path, encoding="utf-8").read().splitlines()[1:]


print("\n3. The speakers were told apart")
rows = rows_of("WA_speakers.csv")
found = {}
for line in rows:
    part = line.split(",")
    found[part[0]] = found.get(part[0], 0.0) + float(part[4])
print("   ", {k: round(v) for k, v in found.items()})
check("both speakers appear", set(found) == {"Host", "Guest"}, str(set(found)))
# 15 s of Host and 10 s of Guest are in the material.
check("Host about 15 s", 12 <= found.get("Host", 0) <= 18,
        str(round(found.get("Host", 0))))
check("Guest about 10 s", 7 <= found.get("Guest", 0) <= 13,
        str(round(found.get("Guest", 0))))
# Durations alone let a lot through. What the separation is for is that
# no microphone reports its neighbour, so how much of each speaker's
# reported speech falls in the other one's turns is measured. The csv
# counts from the common start, CAM_LATE into the material.
NEXT_TO = {"Host": "Guest", "Guest": "Host"}
foreign = {"Host": 0.0, "Guest": 0.0}
for line in rows:
    part = line.split(",")
    hour, minute, second = part[3].split(":")
    a = int(hour) * 3600 + int(minute) * 60 + float(second)
    b = a + float(part[4])
    for c, d in TURNS.get(NEXT_TO.get(part[0], ""), []):
        foreign[part[0]] = foreign.get(part[0], 0.0) + max(
            0.0, min(b, d - CAM_LATE) - max(a, c - CAM_LATE))
print("   ", {k: round(v, 1) for k, v in foreign.items()}, "of the other's turns")
check("neither track claims the other's turns",
        max(foreign.values()) <= 1.5,
        str({k: round(v, 1) for k, v in foreign.items()}))

print("\n4. And the cut alternates")
cut = rows_of("WA_cameracut.csv")
cameras = [line.split(",")[1] for line in cut]
print("   ", len(cut), "shots:", cameras)
check("more than two shots", len(cut) > 2, str(len(cut)))
check("both cameras are used", set(cameras) == {"CamHost", "CamGuest"},
        str(set(cameras)))

print("\n5. The handover holds the same cut")
# Missing, it reads as empty: the checks below then name what is absent.
d = (json.load(open(OUT + "/WA_resolve.json", encoding="utf-8"))
     if os.path.exists(OUT + "/WA_resolve.json") else {})
check("format stamped", d.get("format") == vpm.FILE_FORMAT,
        "%r in the file, wanted %r" % (d.get("format"), vpm.FILE_FORMAT))
# Not 0 against 0: an empty cut in both would agree and say nothing.
check("cut in the file", 0 < len(d.get("cut") or []) == len(cut),
        "%d/%d" % (len(d.get("cut") or []), len(cut)))
# The track name is the speaker; the camera name stands beside it.
check("both cameras in the file",
        {cam.get("camera") for cam in (d.get("cameras") or [])}
        == {"CamHost", "CamGuest"},
        str([cam.get("camera") for cam in (d.get("cameras") or [])]))

print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
