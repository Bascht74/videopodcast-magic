# -*- coding: utf-8 -*-
"""The project's output colour space decides HDR, and silence is not no.

Nothing of Resolve is needed: a stand-in hands back the settings
dictionary and answers no other name, so a reading that stopped asking
for the whole of them is seen. In order the log output spaces the
cameras really deliver, where a version digit follows the marker; two
invented names burying a marker inside a longer word, where the word
boundary is decided; an ordinary SDR space, which says no; the spaces
carrying HDR in their name; the cases where nothing can be read, which
say nothing -- not no; the reason, read back on a yes and on a no;
which curve is read out of every output colour space Resolve offers;
two names Resolve really writes that a reading by word end missed; and
one odd spelling that both readers have to read alike, because they
read the same plain spelling of the same settings. The one door to a
Resolve that is really running is nailed shut first: every project here
is a stand-in, and a reading that asked for a real one would be news.
"""
import os
import the_program
HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = the_program.SCRIPT
import sys, time
vpm = the_program.load()
vpm.set_language("en")


# The one door to a Resolve that is really running, and it is nailed
# shut. Resolve may be up on this machine, and nothing here may reach
# it: a reading that asked for a real project instead of the stand-in
# it was handed gets this refusal out loud, and gets nothing to invent
# a project manager or a project out of.
def no_resolve(*_args, **_kwargs):
    raise RuntimeError("hdr_from_project asked for a Resolve")


vpm.connect_to_resolve = no_resolve

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

# --- every output colour space Resolve offers, and what catches it ---
# Written out as values: these are the names Resolve 21 carries, and a
# loop that worked them out would work them out as wrongly as the
# program does. PQ and HLG on one side, the spaces that are neither on
# the other -- and nothing may be caught by both.
PQ_NAMES = ("Rec.2100 ST2084", "Rec.2100 ST2084 (1000 nit)",
            "Rec.2100 ST2084 (Scene)", "Rec.2020 ST2084 1000 nits",
            "P3-D65 ST2084 (1000 nit)", "HDR PQ", "HDR Rec.2020 PQ",
            "HDR ST.2084")
HLG_NAMES = ("Rec.2100 HLG", "Rec.2100 HLG (Scene)", "HDR HLG",
             "HDR Rec.2020 HLG", "Rec.2020 HLG ARIB STD-B67")
NEITHER = ("Rec.709", "Rec.709 Gamma 2.4", "Rec.709 BT.1886",
           "Rec.2020", "Rec.2020 Gamma 2.4", "SDR Rec.709",
           "SDR Rec.2020", "P3-D65", "DCI-P3", "Rec.601")


class OneSetting:
    """A project that answers with one output colour space and nothing else."""

    def __init__(self, value):
        self.value = value

    def GetSetting(self, name):
        return {"colorSpaceOutput": self.value}


missed = [n for n in PQ_NAMES
          if vpm.hdr_kind_from_project(OneSetting(n))[0] != "pq"]
check("every PQ output colour space is read as PQ", not missed,
      "%d of %d not caught: %r" % (len(missed), len(PQ_NAMES), missed[:3]))
missed = [n for n in HLG_NAMES
          if vpm.hdr_kind_from_project(OneSetting(n))[0] != "hlg"]
check("every HLG output colour space is read as HLG", not missed,
      "%d of %d not caught: %r" % (len(missed), len(HLG_NAMES), missed[:3]))
wrong = [(n, vpm.hdr_kind_from_project(OneSetting(n))[0]) for n in NEITHER
         if vpm.hdr_kind_from_project(OneSetting(n))[0] is not None]
check("a space that is neither is read as neither", not wrong,
      "%d of %d taken for HDR: %r" % (len(wrong), len(NEITHER), wrong[:3]))

print("\nF. Two names Resolve really writes, and the word is not at the end")
kind, why = vpm.hdr_kind_from_project(
    OneSetting("HDR Rec.2020 PQ (P3-D65 limited)"))
check("a PQ output space limited to P3-D65 is read as PQ", kind == "pq",
      "read back %r for 'HDR Rec.2020 PQ (P3-D65 limited)', wanted 'pq'"
      % (kind,))

kind, why = vpm.hdr_kind_from_project(
    OneSetting("Rec.2100 Hybrid Log Gamma"))
check("an HLG output space written out in words is read as HLG",
      kind == "hlg",
      "read back %r for 'Rec.2100 Hybrid Log Gamma', wanted 'hlg'" % (kind,))

print("\nG. One odd spelling, and both readers read it alike")
# Dots and a blank inside the curve's name, and no second word -- no
# 2100, no HDR -- that either reader could fall back on: what they make
# of it is what they make of the one plain spelling both are handed.
ODD = "P3-D65 ST. 2084 (1000 nit)"
got, why = vpm.hdr_from_project(OneSetting(ODD))
kind, why = vpm.hdr_kind_from_project(OneSetting(ODD))
check("both readers read one odd spelling of ST 2084 as the same HDR",
      got is True and kind == "pq",
      "hdr_from_project read %r and hdr_kind_from_project %r for %r, "
      "wanted True and 'pq'" % (got, kind, ODD))

print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
