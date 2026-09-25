# -*- coding: utf-8 -*-
"""Tracks already back from Auphonic go into the run, or the run says why not.

The material of run_stays_local, and a folder of returned tracks beside
it: the recordings with their highs taken off, which tells a processed
track from a raw one whatever the gain, and the finished mixdown. First
the tracks that fit: each speaker matched to the file of its name, the
processed one written, the mixdown setting the loudness. Then a folder
holding a track two minutes long, which belongs to another run and has
to stop this one with its reason, not by a crash. That nothing is
written then is not asked: three nets stand in front of it, and no one
break reaches it.
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
import re, shutil, subprocess, tempfile, time
import numpy as np
import local_ground

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


def tail(text, n=2):
    """The last n lines a run printed, joined, for a FAIL line."""
    rows = [x.strip() for x in text.splitlines() if x.strip()]
    return (" | ".join(rows[-n:]))[:100]


def high_share(path):
    """How much of a file's energy lies above 3 kHz, from 0 to 1."""
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", path, "-f", "f32le",
                          "-ac", "1", "-ar", "48000", "-"],
                         capture_output=True).stdout
    x = np.frombuffer(raw, "<f4").astype(float)
    if not len(x):
        return -1.0
    power = np.abs(np.fft.rfft(x)) ** 2
    hz = np.fft.rfftfreq(len(x), 1 / 48000.0)
    return float(power[hz >= 3000].sum() / max(power.sum(), 1e-30))


def number_after(text, template):
    """The first number after the fixed part of a template, or None."""
    lead = template.split("%s")[0].strip()
    for line in text.splitlines():
        if lead in line:
            found = re.search(r"-?\d+(\.\d+)?", line.split(lead, 1)[1])
            return float(found.group(0)) if found else None
    return None


# The leaf keeps its name: the program names what it writes after the
# folder it was pointed at. Its own folder under the run's TMPDIR.
D = os.path.join(tempfile.mkdtemp(prefix="vpm_run_"), "donerun")
os.makedirs(D)
ASSIGN = local_ground.build(D, vpm.FILE_FORMAT)
# A made-up key and a curl that goes nowhere: a copy with the finished
# folder ignored reaches for the upload, and must meet neither the
# keychain nor auphonic.com.
ENV = dict(os.environ, LANG="C", LC_ALL="C", LANGUAGE="en",
           VPM_SILENT="1", VPM_NO_UPDATE_CHECK="1",
           AUPHONIC_TOKEN="not-a-key-only-a-test")
local_ground.watched_curl(os.path.join(D, "bin"), ENV)

DONE = os.path.join(D, "done")
OTHER = os.path.join(D, "other")
os.makedirs(DONE)
os.makedirs(OTHER)
for name in ("Host", "Guest"):
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", D + "/%s.wav" % name,
                    "-af", "lowpass=f=1000,lowpass=f=1000,volume=-6dB",
                    "-c:a", "pcm_s24le", DONE + "/%s.wav" % name], check=True)
# The mixdown is the raw sum 10 dB down, so its loudness is neither the
# --lufs asked for nor the sum of the returned tracks.
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", D + "/Host.wav",
                "-i", D + "/Guest.wav", "-filter_complex",
                "amix=inputs=2:normalize=0,volume=-10dB", "-c:a", "pcm_s24le",
                DONE + "/WA_master.wav"], check=True)
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", DONE + "/Host.wav",
                "-af", "apad=whole_dur=120", "-c:a", "pcm_s24le",
                OTHER + "/Host.wav"], check=True)
shutil.copy(DONE + "/Guest.wav", OTHER + "/Guest.wav")
RAW, PROCESSED = high_share(D + "/Host.wav"), high_share(DONE + "/Host.wav")
# A precondition of the material, not a judgement about the program:
# without the highs apart, the two kinds of track cannot be told apart.
assert RAW > 0.5 and 0 <= PROCESSED < 0.001, (RAW, PROCESSED)


def run(folder, out, *extra):
    """One run with the finished folder given: (code, what it printed)."""
    p = subprocess.run(
        [sys.executable, SCRIPT, "--multitrack", "--auphonic-done", folder,
         "--assign", ASSIGN, "--out", out, "--no-metrics",
         "--no-speech-recognition", "--no-transcript-file",
         "--no-wide-edges"] + list(extra)
        + [D + "/Host.wav", D + "/Guest.wav", D + "/CamHost.mov",
           D + "/CamGuest.mov"],
        capture_output=True, text=True, timeout=900, env=ENV)
    return p.returncode, (p.stdout or "") + (p.stderr or "")


print("1. The returned tracks fit, and the mixdown lies beside them")
OUT = os.path.join(D, "out")
code, said = run(DONE, OUT, "--lufs", "-16")
check("a finished folder with the right tracks runs through", code == 0,
      "returned %d against 0, ends: %s" % (code, tail(said)))
matched = vpm.T('    %-20s <- %s  (%s, name similarity %s)').split("  (")[0]
missing = [name for name in ("Host", "Guest")
           if matched % (name, name + ".wav") not in said]
check("every speaker is matched to the file of its name", not missing,
      "no line matching %s to its own file" % (", ".join(missing) or "-"))
WRITTEN = os.path.join(OUT, "auphonic-tracks", "final_Host.wav")
share = high_share(WRITTEN) if os.path.exists(WRITTEN) else -1.0
check("the processed track is what the run writes, not the raw one",
      0 <= share < 0.01,
      "final_Host.wav has %.5f of its energy above 3 kHz; the processed "
      "track %.5f, the raw one %.3f" % (share, PROCESSED, RAW))
HAVE = vpm.T('  Mixdown from auphonic.com: %s LUFS, peak %s dBTP (%s)')
lines = [line.strip() for line in said.splitlines()
         if HAVE.split("%s")[0].strip() in line]
check("the mixdown from auphonic.com is measured",
      len(lines) == 1 and "WA_master.wav" in lines[0],
      "%d lines naming the mixdown: %s" % (len(lines), lines[:1]))
master = number_after(said, HAVE)
target = number_after(said, vpm.T('  Target:            %s LUFS  ->  %s dB '
                                  'on every track'))
check("and its loudness becomes the target",
      master is not None and target == master,
      "target %r LUFS against the mixdown's %r, with --lufs -16 asked for"
      % (target, master))

print("\n2. A track from another run")
OUT2 = os.path.join(D, "other_out")
code, said = run(OTHER, OUT2)
# A child that dies on a traceback returns 1 as well; that is no stop.
crashed = "Traceback (most recent call last)" in said
check("a track of the wrong length stops the run with 1, not a crash",
      code == 1 and not crashed,
      "returned %d against 1%s, ends: %s"
      % (code, ", after a traceback" if crashed else "", tail(said)))
why = vpm.T('    %-20s <- %s  BUT %s -- neither the time window (%s) nor the'
            '\n    %-20s    whole measured range (%s). This belongs to '
            'another run.').rsplit("(%s). ", 1)[1]
named = vpm.T('\n  Not usable: %s').strip() % "Host"
check("and names it as from another run", why in said and named in said,
      "%r %s, %r %s" % (why, "said" if why in said else "not said",
                        named, "said" if named in said else "not said"))

print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
