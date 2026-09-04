# -*- coding: utf-8 -*-
"""The project's output colour space decides HDR, and silence is not no.

Nothing of Resolve is needed: a stand-in hands back the settings
dictionary and answers no other name, so a reading that stopped asking
for the whole of them is seen. In order the log output spaces the
cameras really deliver, where a version digit follows the marker; two
invented names burying a marker inside a longer word, where the word
boundary is decided; an ordinary SDR space, which says no; the spaces
carrying HDR in their name; the cases where nothing can be read, which
say nothing -- not no; and the reason, read back on a yes and on a no.
"""
import os
HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = os.environ.get("VPM_SCRIPT") or os.path.join(
    os.path.dirname(HERE), "videopodcast_magic.py")
import sys, time, importlib.util
spec = importlib.util.spec_from_file_location("vpm", SCRIPT)
vpm = importlib.util.module_from_spec(spec); sys.modules["vpm"] = vpm
spec.loader.exec_module(vpm)
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


class Project(object):
    """A Resolve project as far as this reading needs one.

    The real object answers the whole dictionary of settings to the
    empty name and one single value to any other name. Asked for
    anything else this one raises, so that a reader that stopped
    asking for the whole dictionary cannot be answered politely -- the
    asked list below is what makes that visible, because the reading
    catches what comes out of GetSetting.
    """

    def __init__(self, settings):
        self.settings = settings
        self.asked = []

    def GetSetting(self, key):
        self.asked.append(key)
        if key != "":
            raise LookupError("only the whole dictionary is served here")
        return self.settings


class Silent(object):
    """A project that will not answer at all."""

    def GetSetting(self, key):
        raise LookupError("this project answers nothing")


def space(name):
    """A project whose only output colour space is the given name."""
    return Project({"colorSpaceOutput": name})


print("A. The log output spaces the cameras really deliver")
got, why = vpm.hdr_from_project(space("Sony S-Gamut3.Cine/S-Log3"))
check("a Sony S-Log3 output space is read as HDR", got is True,
      "read back %r for 'Sony S-Gamut3.Cine/S-Log3', wanted True" % (got,))

check("the reason for a log output space names the setting and its value",
      why == "colorSpaceOutput = Sony S-Gamut3.Cine/S-Log3",
      "read back %r, wanted %r"
      % (why, "colorSpaceOutput = Sony S-Gamut3.Cine/S-Log3"))

got, why = vpm.hdr_from_project(space("ARRI LogC4"))
check("an ARRI LogC4 output space is read as HDR", got is True,
      "read back %r for 'ARRI LogC4', wanted True" % (got,))

got, why = vpm.hdr_from_project(space("Panasonic V-Log"))
check("a Panasonic V-Log output space is read as HDR", got is True,
      "read back %r for 'Panasonic V-Log', wanted True" % (got,))

print("\nB. A marker buried in a longer word is no marker")
got, why = vpm.hdr_from_project(space("Vlogger Wide Gamut"))
check("a marker at the start of a longer word is no log output space",
      got is False,
      "read back %r for 'Vlogger Wide Gamut', wanted False" % (got,))

got, why = vpm.hdr_from_project(space("Catalog Gamma Display"))
check("a marker at the end of a longer word is no log output space",
      got is False,
      "read back %r for 'Catalog Gamma Display', wanted False" % (got,))

print("\nC. An ordinary output space says no, and says what it read")
got, why = vpm.hdr_from_project(space("Rec.709 Gamma 2.4"))
check("an ordinary Rec.709 output space says no rather than nothing",
      got is False,
      "read back %r for 'Rec.709 Gamma 2.4', wanted False" % (got,))

check("the reason for an SDR output space names the setting and its value",
      why == "colorSpaceOutput = Rec.709 Gamma 2.4",
      "read back %r, wanted %r"
      % (why, "colorSpaceOutput = Rec.709 Gamma 2.4"))

print("\nD. The output spaces that carry HDR in their name")
got, why = vpm.hdr_from_project(space("Rec.2100 ST2084"))
check("a Rec.2100 ST2084 output space is read as HDR", got is True,
      "read back %r for 'Rec.2100 ST2084', wanted True" % (got,))

got, why = vpm.hdr_from_project(space("Rec.2100 HLG"))
check("a Rec.2100 HLG output space is read as HDR", got is True,
      "read back %r for 'Rec.2100 HLG', wanted True" % (got,))

got, why = vpm.hdr_from_project(space("Rec.2020"))
check("a Rec.2020 output space is read as HDR", got is True,
      "read back %r for 'Rec.2020', wanted True" % (got,))

print("\nE. Where nothing can be read, nothing is said -- and that is"
      " not a no")
empty = Project({"timelineFrameRate": "25", "superScale": "1"})
got, why = vpm.hdr_from_project(empty)
check("a project with no output colour space says nothing at all",
      got is None, "read back %r with the reason %r, wanted None"
      % (got, why))

check("the whole settings dictionary is asked for by the empty name",
      empty.asked == [""],
      "the reading asked for %r, wanted %r" % (empty.asked, [""]))

got, why = vpm.hdr_from_project(space("None"))
check("colour management switched off says nothing at all", got is None,
      "read back %r for 'None', wanted None" % (got,))

got, why = vpm.hdr_from_project(
    Project({"colorScienceMode": "DaVinci YRGB Color Managed"}))
check("a setting that names colour but no output is not read", got is None,
      "read back %r for 'colorScienceMode', wanted None" % (got,))

got, why = vpm.hdr_from_project(
    Project({"timelineOutputResolutionWidth": "1920"}))
check("a setting that names output but no colour is not read", got is None,
      "read back %r for 'timelineOutputResolutionWidth', wanted None"
      % (got,))

got, why = vpm.hdr_from_project(Silent())
check("a project that refuses to answer says nothing at all", got is None,
      "read back %r, wanted None" % (got,))

got, why = vpm.hdr_from_project(Project(""))
check("an answer that is no dictionary says nothing at all", got is None,
      "read back %r for an empty string of settings, wanted None" % (got,))

print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
