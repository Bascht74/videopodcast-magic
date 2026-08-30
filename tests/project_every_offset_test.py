# -*- coding: utf-8 -*-
"""Every camera reaches the handover with the offset measured for it.

The offsets are kept under the rendered file. A camera without one had
no key, and 0.0 as a fallback put it at the start of the axis.
"""
import os
HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = os.environ.get("VPM_SCRIPT") or os.path.join(
    os.path.dirname(HERE), "videopodcast-magic.py")
import importlib.util, io, json, sys, tempfile
import contextlib
spec = importlib.util.spec_from_file_location("vpm", SCRIPT)
vpm = importlib.util.module_from_spec(spec); sys.modules["vpm"] = vpm
spec.loader.exec_module(vpm)
# Not a prefix carrying the word this file looks for below: the
# hand-over prints its own path, and a check reads everything printed.
WORK = tempfile.mkdtemp(prefix="everycamera_")
bad = []


def check(what, ok, detail=""):
    print("  %-58s %s%s" % (what, "ok" if ok else "FAIL",
                            "" if ok else "   " + detail))
    if not ok:
        bad.append(what)


def spoken(call, *a, **k):
    """Run something and hand back what it printed."""
    said = io.StringIO()
    with contextlib.redirect_stdout(said):
        out = call(*a, **k)
    return out, said.getvalue()


class Args(object):
    production = "Test"
    resolve = False
    lufs = -16.0
    intro = None
    outro = None


hand = os.path.join(WORK, "hand")
os.makedirs(hand)
wide = os.path.join(WORK, "W.mov")
guest = os.path.join(WORK, "G.mov")
for f in (wide, guest):
    open(f, "w").write("x")
rendered = os.path.join(WORK, "Wide.wav")
open(rendered, "w").write("x")

cameras = [{"name": "Wide", "video": wide}, {"name": "Guest", "video": guest}]
videos = [(wide, {"fps": 30.0, "width": 1920, "height": 1080,
                  "duration": 100.0, "tc": "10:00:00:00"}),
          (guest, {"fps": 30.0, "width": 1080, "height": 1920,
                   "duration": 100.0, "tc": "10:00:00:00"})]
# Wide has a render, Guest has none. Both were measured.
offsets = {rendered: -12.5, os.path.abspath(guest): -7.25}
out, said = spoken(vpm.write_handover, Args(), [], cameras, videos, hand,
                   0.0, (wide, videos[0][1]), [rendered], None, None,
                   0.0, None, None, offsets)
written = json.load(io.open(os.path.join(hand, "Test_resolve.json"),
                            encoding="utf-8"))
by_camera = dict((c["camera"], c) for c in written["cameras"])
check("the camera with a render keeps its offset",
      by_camera["Wide"]["offset"] == -12.5,
      str(by_camera["Wide"]["offset"]))
check("the camera without one is found by its source",
      by_camera["Guest"]["offset"] == -7.25,
      str(by_camera["Guest"]["offset"]))
check("nothing to complain about", "offset" not in said.lower(),
      said.strip()[:60])

# And where nothing was measured for a camera, it is said out loud.
out, said = spoken(vpm.write_handover, Args(), [], cameras, videos, hand,
                   0.0, (wide, videos[0][1]), [rendered], None, None,
                   0.0, None, None, {rendered: -12.5})
check("an unmeasured camera is named", "Guest" in said, repr(said[:70]))

# A landscape and a portrait camera give a frame one of them has.
check("the handover frame is a real one",
      (written["width"], written["height"]) in ((1920, 1080), (1080, 1920)),
      "%sx%s" % (written["width"], written["height"]))

print("\n%s" % ("ALL OK" if not bad else "FAIL: " + ", ".join(bad)))
sys.exit(1 if bad else 0)
