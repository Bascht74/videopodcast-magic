# -*- coding: utf-8 -*-
"""A run names the production and each camera as the window does.

One real run, started with the command line the window builds, on two
camera files of one name in two folders and a recording beside them.
The log names the second camera "(2)" in the plan, on the time axis and
where it is processed, and the handover is named after the production
field, not after the folder the material lies in. The preflight names
it so too: in the facts line for that camera and in the hint that the
two files may be one recording twice. Last the window's own check, run
in this process on the same files, says that hint with both apart too.
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
import shutil
import subprocess
import tempfile
import time
import the_program

SCRIPT = the_program.SCRIPT
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


def line_with(log, start):
    """The first line of *log* beginning with *start*, for a FAIL line."""
    return next((x for x in log.splitlines() if x.startswith(start)), "")


D = tempfile.mkdtemp(prefix="vpm_names_")
# Forty seconds of pink noise under a small picture: long enough for the
# alignment to find points. Two cards, one file name, as a recorder
# writes it on each.
REC = os.path.join(D, "Rec.wav")
subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i",
                "anoisesrc=color=pink:duration=40:sample_rate=48000",
                "-af", "tremolo=f=3:d=0.8", "-ac", "1", "-c:a", "pcm_s16le",
                REC], check=True)
CAMS = []
for card in ("CardA", "CardB"):
    os.makedirs(os.path.join(D, card))
    CAMS.append(os.path.join(D, card, "C0003.MP4"))
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i",
                    "smptebars=size=160x90:rate=25:duration=40", "-i", REC,
                    "-map", "0:v", "-map", "1:a", "-c:v", "libx264",
                    "-preset", "ultrafast", "-pix_fmt", "yuv420p",
                    "-c:a", "pcm_s16le", "-shortest", CAMS[-1]], check=True)
OUT = os.path.join(D, "out")
os.makedirs(OUT)
argv, _plan, _m = vpm.run_argv({
    "files": [(REC, "audio"), (CAMS[0], "video"), (CAMS[1], "video")],
    "clip_kinds": {}, "out_folder": OUT, "multitrack": False,
    "production": "Pilot", "cameras": [], "cut": {},
    "wide_at_edges": False, "key": ""})
ENV = dict(os.environ, LANG="C", LC_ALL="C", LANGUAGE="en", VPM_SILENT="1",
           VPM_NO_SPEAKER_SPLIT="1", VPM_NO_UPDATE_CHECK="1",
           QT_QPA_PLATFORM="offscreen")
p = subprocess.run(
    [sys.executable, SCRIPT] + list(argv or ["-"])[1:]
    + ["--no-metrics", "--no-speech-recognition", "--no-transcript-file"],
    capture_output=True, text=True, env=ENV)
log = (p.stdout or "") + (p.stderr or "")

print("1. The run")
check("the run goes through on the window's command line",
      p.returncode == 0,
      "returned %d, last line: %s" % (p.returncode, (log.replace(
          D, "<tmp>").strip().splitlines() or [""])[-1][-120:]))

print("\n2. The second camera, as the window names it")
PLAN = "    C0003.MP4 (2)  ->  "
check("the plan names the second camera as the window does",
      bool(line_with(log, PLAN)),
      "no line begins %r; the plan says %r" % (PLAN, next(
          (x for x in log.splitlines() if "->  C0003 2_" in x), "")))
AXIS = "  C0003.MP4 (2)        offset "
check("the time axis names it so too", bool(line_with(log, AXIS)),
      "no line begins %r; the axis says %r" % (
          AXIS, line_with(log, "  C0003.MP4")))
HEAD = vpm.T('\nPROCESSING: %s') % "C0003.MP4 (2)"
check("and it is processed under that name", HEAD + "\n" in log,
      "%r not in %d characters of log; it says %r" % (
          HEAD.strip(), len(log), line_with(log, "PROCESSING")))

print("\n3. The preflight, as the window names them")
FACTS = "    C0003.MP4 (2)     %s fps" % vpm.number_text(25, 3)
check("the preflight's facts line names the second camera so",
      bool(line_with(log, FACTS)),
      "no line begins %r; the preflight says %r" % (
          FACTS, [x for x in log.splitlines()
                  if x.startswith("    C0003.MP4")]))
TWINS = vpm.T('%s have the same size and running time -- possibly one '
              'recording twice.') % "C0003.MP4, C0003.MP4 (2)"
check("and the hint on one recording twice names both apart",
      TWINS in log, "%r not in the log; it says %r" % (
          TWINS, next((x for x in log.splitlines()
                       if "same size and running time" in x), "")))

print("\n4. The production, as the field names it")
made = sorted(n for n in os.listdir(OUT) if n.endswith("_resolve.json"))
check("the handover is named after the production field",
      made == ["Pilot_resolve.json"],
      "handover files %s, wanted ['Pilot_resolve.json']" % made)

print("\n5. The window's own check, on the same two cameras")


class Stub(object):
    """What the check touches of the window: a line, a plan, a field."""

    def __init__(self, value=None):
        self.value = value

    def get(self):
        return self.value

    def __getattr__(self, name):
        return lambda *a, **k: None


came = []
_fill, kick_off = vpm.make_preflight(
    {}, [(REC, "audio"), (CAMS[0], "video"), (CAMS[1], "video")], Stub(),
    Stub(), lambda _signal, findings: came.append(findings), Stub(), None,
    None, None, {}, set(), lambda: [], Stub(False), [], {})
kick_off()
waited = time.time()
while not came and time.time() - waited < 120:
    time.sleep(0.05)
said = [b.text for b in (came[0] if came else ())
        if b.field == vpm.T('Cameras')]
check("the window's check names both apart in the hint as well",
      TWINS.strip() in [x.strip() for x in said],
      "after %.1f s the window's check says %r, wanted %r" % (
          time.time() - waited, said, TWINS.strip()))

shutil.rmtree(D, ignore_errors=True)

print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
