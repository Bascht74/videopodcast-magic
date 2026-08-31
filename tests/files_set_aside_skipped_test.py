# -*- coding: utf-8 -*-
"""Set-aside files: checked yes, compared no, counted no."""
import os
HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = os.environ.get("VPM_SCRIPT") or os.path.join(
    os.path.dirname(HERE), "videopodcast-magic.py")
import sys, subprocess, shutil, time, importlib.util
sys.path.insert(0, os.path.dirname(
    os.path.abspath(__file__)))
from fixture_root import fixture
spec = importlib.util.spec_from_file_location(
    "vpm", SCRIPT)
vpm = importlib.util.module_from_spec(spec); sys.modules["vpm"] = vpm
spec.loader.exec_module(vpm)

began = time.time()
done = 0
error = []
def check(name, ok, extra=""):
    global done
    done += 1
    print("  %-58s %s %s" % (name, "ok" if ok else "FAIL", extra))
    if not ok:
        error.append("%s [%s]" % (name, extra or "no numbers"))

D = fixture("setaside"); shutil.rmtree(D, ignore_errors=True); os.makedirs(D)
def video(name, size, duration=2):
    p = os.path.join(D, name)
    subprocess.run(["ffmpeg", "-v", "error", "-f", "lavfi",
                    "-i", "testsrc=size=%s:rate=30:duration=%d"
                    % (size, duration),
                    "-c:v", "libx264", "-pix_fmt", "yuv420p", p, "-y"],
                   check=True)
    return p

# Two cameras of the same size, plus a colour chart of a quite different one.
cam1 = video("Camera1.mov", "640x360")
cam2 = video("Camera2.mov", "640x360")
chart = video("Colourchart.mov", "320x180")

print("1. Without set aside: the colour chart makes a resolution hint")
findings = vpm.collect_findings([], [cam1, cam2, chart], fresh=True)
res = [x for x in findings if x.field == "Resolutions"]
check("hint about differing resolutions there", bool(res),
        res[0].text[:60] if res else "-")

print("\n2. With set aside: no resolution hint any more")
findings = vpm.collect_findings([], [cam1, cam2, chart], fresh=True,
                         set_aside=[chart])
res = [x for x in findings if x.field == "Resolutions"]
check("no resolution hint", not res, res[0].text[:60] if res else "")

print("\n3. The colour chart still has findings of its own")
its_findings = [x for x in findings if x.file == os.path.abspath(chart)]
check("findings about the colour chart there", bool(its_findings),
        "%d" % len(its_findings))
check("all marked as set aside",
        all(x.set_aside for x in its_findings),
        str([x.field for x in its_findings if not x.set_aside]))

print("\n4. The cameras are not set aside")
its_findings = [x for x in findings if x.file == os.path.abspath(cam1)]
check("findings about Camera1 there", bool(its_findings),
        "%d" % len(its_findings))
check("none set aside", not any(x.set_aside for x in its_findings))

print("\n5. Findings across files are never set aside")
across = [x for x in findings if not x.file]
check("none set aside", not any(x.set_aside for x in across),
        "%d across files" % len(across))

print("\n6. Audio: an ignored track stays out of the comparison")
audio = []
for i, loud in enumerate((0.9, 0.9, 0.05)):
    p = os.path.join(D, "Track%d.wav" % i)
    subprocess.run(["ffmpeg", "-v", "error", "-f", "lavfi",
                    "-i", "sine=frequency=%d:duration=3" % (300 + i * 100),
                    "-af", "volume=%f" % loud, p, "-y"], check=True)
    audio.append(p)
findings1 = vpm.collect_findings(audio, [], fresh=True, crosstalk=False)
findings2 = vpm.collect_findings(audio, [], fresh=True, crosstalk=False,
                         set_aside=[audio[2]])
across1 = [x.field for x in findings1 if not x.file]
across2 = [x.field for x in findings2 if not x.file]
print("    across files without/with set aside:", across1, "/", across2)
its_findings = [x for x in findings2 if x.file == os.path.abspath(audio[2])]
check("the ignored track has findings of its own", bool(its_findings))
check("and they are set aside", all(x.set_aside for x in its_findings))

print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(error) if error else "ALL OK")
sys.exit(1 if error else 0)
