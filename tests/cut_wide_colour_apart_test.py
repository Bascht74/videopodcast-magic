# -*- coding: utf-8 -*-
"""Does the wide shot colour keep far enough from the speaker colours?"""
import os
HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = os.environ.get("VPM_SCRIPT") or os.path.join(
    os.path.dirname(HERE), "videopodcast_magic.py")
import math, sys, time, importlib.util
spec = importlib.util.spec_from_file_location(
    "vpm", SCRIPT)
vpm = importlib.util.module_from_spec(spec); sys.modules["vpm"] = vpm
spec.loader.exec_module(vpm)

# The list is called "error" and not "bad": every section below uses
# "bad" for the colours it found too close together.
began = time.time()
done = 0
error = []


def check(name, ok, extra=""):
    global done
    done += 1
    print("  %-58s %s %s" % (name, "ok" if ok else "FAIL", extra))
    if not ok:
        error.append("%s [%s]" % (name, extra or "no numbers"))

def lab(h):
    r, g, b = (int(h[i:i+2], 16) / 255.0 for i in (1, 3, 5))
    f0 = lambda c: c/12.92 if c <= 0.04045 else ((c+0.055)/1.055)**2.4
    r, g, b = f0(r), f0(g), f0(b)
    x = r*0.4124+g*0.3576+b*0.1805; y = r*0.2126+g*0.7152+b*0.0722
    z = r*0.0193+g*0.1192+b*0.9505
    f = lambda t: t**(1/3.) if t > 0.008856 else 7.787*t+16/116.
    fx, fy, fz = f(x/0.95047), f(y/1.0), f(z/1.08883)
    return (116*fy-16, 500*(fx-fy), 200*(fy-fz))

def de(a, b):
    return math.sqrt(sum((x-y)**2 for x, y in zip(lab(a), lab(b))))

# From here on two bars side by side are safely told apart. On a light
# ground the lower value holds: there the white background narrows the
# choice, and that has been so from the start.
MINIMUM = {"dark": 45.0, "light": 34.0}
GROUND = {"light": vpm.COLOURS["sheet"], "dark": vpm.COLOURS_DARK["sheet"]}

print("1. The wide shot against the first four speaker colours")
speaker = [f for f in vpm.CLIP_COLOURS if f != vpm.COLOUR_WIDE_SHOT][:4]
for mode in ("light", "dark"):
    vpm.ON_DARK[0] = (mode == "dark")
    wide = vpm.clip_colour_rgb(vpm.COLOUR_WIDE_SHOT)
    values = [(s, de(wide, vpm.clip_colour_rgb(s))) for s in speaker]
    bad = [(s, d) for s, d in values if d < MINIMUM[mode]]
    check("%-7s %s %s against %s" % (mode, vpm.COLOUR_WIDE_SHOT, wide,
                                     ", ".join(s for s in speaker)),
            not bad,
            "  ".join("%s %.1f" % (s, d) for s, d in values))

print("\n2. On dark clearly better than before")
old = min(de(vpm.CLIP_COLOURS_RGB["Tan"], vpm.CLIP_COLOURS_RGB[s])
          for s in speaker)
vpm.ON_DARK[0] = True
fresh = min(de(vpm.clip_colour_rgb(vpm.COLOUR_WIDE_SHOT),
               vpm.clip_colour_rgb(s))
          for s in speaker)
check("smallest distance on dark clearly larger", fresh > old + 10,
        "%.1f instead of %.1f" % (fresh, old))
vpm.ON_DARK[0] = False
light = min(de(vpm.clip_colour_rgb(vpm.COLOUR_WIDE_SHOT),
               vpm.clip_colour_rgb(s))
           for s in speaker)
check("on light no worse than before", light >= old - 0.01,
        "%.1f" % light)

print("\n3. Every colour stands out from the sheet")
for mode, ground in GROUND.items():
    vpm.ON_DARK[0] = (mode == "dark")
    bad = [(n, round(de(vpm.clip_colour_rgb(n), ground), 1))
                for n in vpm.CLIP_COLOURS
                if de(vpm.clip_colour_rgb(n), ground) < 30.0]
    check("%-7s all clip colours visible" % mode, not bad,
            str(bad))

print("\n4. The speaker colours among themselves")
for mode in ("light", "dark"):
    vpm.ON_DARK[0] = (mode == "dark")
    pairs = [(a, b, de(vpm.clip_colour_rgb(a), vpm.clip_colour_rgb(b)))
             for i, a in enumerate(speaker) for b in speaker[i+1:]]
    bad = [(a, b, round(d, 1)) for a, b, d in pairs if d < MINIMUM[mode]]
    check("%-7s speaker colours tellable apart" % mode, not bad,
            str(bad))

print("\n5. The assignment stays with the wide shot")
vpm.ON_DARK[0] = False
assigned, duplicate = vpm.colour_per_camera(
    [{"track": "Guest", "wide": False},
     {"track": "Hosts", "wide": False},
     {"track": "Wide", "wide": True}], list(vpm.CLIP_COLOURS))
print("   ", assigned)
check("Wide gets %s" % vpm.COLOUR_WIDE_SHOT,
        assigned["Wide"] == vpm.COLOUR_WIDE_SHOT, assigned["Wide"])
wide_given = list(assigned.values()).count(vpm.COLOUR_WIDE_SHOT)
check("no voice gets the same one", wide_given == 1,
        "%s given %d times, wanted once: %s"
        % (vpm.COLOUR_WIDE_SHOT, wide_given, assigned))
check("nothing twice", duplicate == 0,
        "%s colours given twice, wanted 0: %s" % (duplicate, assigned))

vpm.ON_DARK[0] = False
print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(error) if error else "ALL OK")
sys.exit(1 if error else 0)
