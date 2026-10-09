# -*- coding: utf-8 -*-
"""Our own new project is brought to the material's colour, or says not.

project_colour_to_material against stand-in projects that take only
some names for the output colour space, as Resolve takes only the names
of one namespace at a time. In turn: SDR material bringing an HDR
project to Rec.709 through whichever name is taken; HDR material
bringing an SDR project to PQ; a name Resolve takes but reads back as
the other range not counted; a spelling that raises passed over; HDR10+
switched off for SDR, left alone for HDR, and one that raises undoing
nothing; a project that will not list its settings, or lists none, left
alone; and the render log of a new project naming the space it was
brought to.
"""
PLATFORM_BOUND = False
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
import contextlib
import io
import tempfile
import time
import resolve_stand_in as stand

began = time.time()
vpm = the_program.load()
vpm.set_language("en")

done = 0
bad = []


def check(name, ok, extra=""):
    global done
    done += 1
    print("  %-58s %s %s" % (name, "ok" if ok else "FAIL", extra))
    if not ok:
        bad.append("%s [%s]" % (name, extra or "no numbers"))


OUT = "colorSpaceOutput"
PLUS = "hdr10PlusControlsOn"
# The internal names, which Resolve takes with automatic colour
# management off; the dropdown's names are refused then.
INTERNAL = ["Rec.709 Gamma 2.4", "Rec.2100 ST2084", "Rec.2100 HLG"]
WORK = tempfile.mkdtemp(prefix="output_space_")


def project(now, **more):
    """A project standing at `now`, taking only the internal names."""
    settings = {OUT: now, PLUS: more.pop("plus", "0")}
    return stand.Project(settings=settings, accepts={OUT: INTERNAL}, **more)


def tried(p):
    return [c[2] for c in p.calls if c[0] == "SetSetting" and c[1] == OUT]


print("1. SDR material, HDR project")
p = project("Rec.2100 ST2084")
stands, missed = vpm.project_colour_to_material(p, False)
check("SDR material brings the project to Rec.709",
      p.settings[OUT] == "Rec.709 Gamma 2.4" and OUT in stands
      and "Rec.709 Gamma 2.4" in stands and missed == "",
      "output now %r, returned (%r, %r) after trying %r"
      % (p.settings[OUT], stands, missed, tried(p)))

print("\n2. HDR material, SDR project")
p = project("Rec.709 Gamma 2.4")
stands, missed = vpm.project_colour_to_material(p, True)
check("HDR material brings the project to PQ",
      p.settings[OUT] == "Rec.2100 ST2084" and "ST2084" in stands
      and missed == "",
      "output now %r, returned (%r, %r) after trying %r"
      % (p.settings[OUT], stands, missed, tried(p)))

print("\n3. Taken, and read back as the other range")
# Resolve takes every HDR name and still reads back Rec.709.
p = stand.Project(settings={OUT: "Rec.709 Gamma 2.4"},
                  reads_back={OUT: "Rec.709 Gamma 2.4"})
stands, missed = vpm.project_colour_to_material(p, True)
check("a name taken but read back as SDR is not counted as HDR",
      stands == "" and missed == "%s = Rec.709 Gamma 2.4" % OUT
      and len(tried(p)) == 4,
      "returned (%r, %r) after trying %r" % (stands, missed, tried(p)))

print("\n4. A spelling that raises")
p = project("Rec.2100 HLG")
real_set = p.SetSetting


def set_raising_first(key, value):
    """The first spelling raises, as an unknown name has in Resolve."""
    if value == "SDR Rec.709":
        raise RuntimeError("stand-in does not know this name")
    return real_set(key, value)


p.SetSetting = set_raising_first
stands, missed = vpm.project_colour_to_material(p, False)
check("a spelling that raises is passed over for the next one",
      p.settings[OUT] == "Rec.709 Gamma 2.4" and missed == "",
      "output now %r, returned (%r, %r)" % (p.settings[OUT], stands, missed))

print("\n5. HDR10+")
p = project("Rec.2100 ST2084", plus="1")
vpm.project_colour_to_material(p, False)
check("HDR10+ is switched off when the material is SDR",
      p.settings[PLUS] == "0", "%s now %r" % (PLUS, p.settings[PLUS]))
p = project("Rec.709 Gamma 2.4", plus="1")
vpm.project_colour_to_material(p, True)
check("HDR10+ is left as it stands when the material is HDR",
      p.settings[PLUS] == "1"
      and not [c for c in p.calls if c[0] == "SetSetting" and c[1] == PLUS],
      "%s now %r" % (PLUS, p.settings[PLUS]))

p = project("Rec.2100 ST2084", plus="1")
real_plus = p.SetSetting


def plus_raising(key, value):
    """HDR10+ raises, as a key this Resolve does not know would."""
    if key == PLUS:
        raise RuntimeError("stand-in has no HDR10+")
    return real_plus(key, value)


p.SetSetting = plus_raising
got = vpm.project_colour_to_material(p, False)
check("HDR10+ that raises does not undo the colour space already set",
      p.settings[OUT] == "Rec.709 Gamma 2.4" and got[1] == ""
      and "Rec.709 Gamma 2.4" in got[0],
      "output now %r, returned %r" % (p.settings[OUT], got))

print("\n6. Settings that cannot be listed")
p = project("Rec.2100 ST2084", throw=["GetSetting"])
got = vpm.project_colour_to_material(p, False)
check("a project that will not list its settings is left alone",
      got == ("", "") and not tried(p),
      "returned %r, tried %r" % (got, tried(p)))
p = project("Rec.2100 ST2084")
p.GetSetting = lambda key="": "Rec.2100 ST2084" if key == OUT else []
got = vpm.project_colour_to_material(p, False)
check("a project that answers no list is left alone too",
      got == ("", "") and not tried(p),
      "returned %r, tried %r" % (got, tried(p)))

print("\n7. In the render job")
p = project("Rec.2100 ST2084")
tl = p.pool.CreateEmptyTimeline("Episode Cut")
out = io.StringIO()
with contextlib.redirect_stdout(out):
    vpm.queue_render_job(p, tl, {"height": 1080, "width": 1920, "fps": 25.0},
                         WORK, "Episode", project_is_new=True)
named = [l.strip() for l in out.getvalue().splitlines()
         if "Rec.709 Gamma 2.4" in l and OUT in l]
check("a new project brought along names its colour space in the log",
      p.settings[OUT] == "Rec.709 Gamma 2.4" and len(named) == 1,
      "output now %r, said %r" % (p.settings[OUT], named))

print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
