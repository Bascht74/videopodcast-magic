# -*- coding: utf-8 -*-
"""Every camera reaches the handover with its offset -- and only a camera.

The offsets are kept under the rendered file. A camera without one had
no key, and 0.0 as a fallback put it at the start of the axis. A file
the run refused altogether is not handed over at all: it has no place
on the axis, and nobody is assigned to it, which is what the handover
reads as the wide shot.
"""
import os
HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = os.environ.get("VPM_SCRIPT") or os.path.join(
    os.path.dirname(HERE), "videopodcast-magic.py")
import importlib.util, io, json, sys, tempfile, time
import contextlib
began = time.time()
spec = importlib.util.spec_from_file_location("vpm", SCRIPT)
vpm = importlib.util.module_from_spec(spec); sys.modules["vpm"] = vpm
spec.loader.exec_module(vpm)
# Not a prefix carrying the word this file looks for below: the
# hand-over prints its own path, and a check reads everything printed.
WORK = tempfile.mkdtemp(prefix="everycamera_")
done = 0
bad = []


def check(name, ok, extra=""):
    global done
    done += 1
    print("  %-58s %s %s" % (name, "ok" if ok else "FAIL", extra))
    if not ok:
        bad.append("%s [%s]" % (name, extra or "no numbers"))


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

# A file the run refused: no render, and no offset under either name.
# Handing it over would make it the wide shot, because "wide" is true for
# whoever has no speaker -- and nobody is assigned to a file that fits
# nowhere. A real run handed over an 18-second jingle that way, with an
# empty file name and "wide": true.
jingle = os.path.join(WORK, "Jingle.mov")
open(jingle, "w").write("x")
three = cameras + [{"name": "Jingle", "video": jingle}]
more = videos + [(jingle, {"fps": 30.0, "width": 1920, "height": 1080,
                           "duration": 18.0, "tc": None})]
out, said = spoken(vpm.write_handover, Args(), [], three, more, hand,
                   0.0, (wide, videos[0][1]), [rendered], None, None,
                   0.0, None, None, offsets, unplaceable=[jingle])
after = json.load(io.open(os.path.join(hand, "Test_resolve.json"),
                          encoding="utf-8"))
names = [c["camera"] for c in after["cameras"]]
check("a file the run could not place is no camera in the handover",
      "Jingle" not in names, "the handover names %s" % names)
check("and it reaches no entry marked as the wide shot",
      not [c for c in after["cameras"]
           if c["camera"] == "Jingle" and c.get("wide")],
      "wide flags: %s" % [(c["camera"], c.get("wide"))
                          for c in after["cameras"]])
check("the run says which file it left out and why",
      "Jingle" in said and "place" in said.lower(), repr(said[:90]))
check("the two it could place are still there",
      sorted(names) == ["Guest", "Wide"], "handed over: %s" % sorted(names))

print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
