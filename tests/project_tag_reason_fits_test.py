# -*- coding: utf-8 -*-
"""The Tagging line names a reason only where it explains its own tags.

Four fake Resolve projects are held up to queue_render_job() and the
Tagging line is read out of the log: an SDR delivery, an SDR delivery in
an HDR project of our own making, an HDR delivery, and an HDR delivery
whose project names no curve. Each of the first three is asked for its
tags first and for the bracket after; the fourth applies no tags and
prints no tag line at all. Nothing reaches the disk.
"""
import os
HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = os.environ.get("VPM_SCRIPT") or os.path.join(
    os.path.dirname(HERE), "videopodcast_magic.py")
import importlib.util, sys, re, io, time, shutil, tempfile, contextlib
spec = importlib.util.spec_from_file_location("vpm", SCRIPT)
vpm = importlib.util.module_from_spec(spec); sys.modules["vpm"] = vpm
spec.loader.exec_module(vpm)

# The line being read is a user-visible one, so it is read in the
# language the source is written in, whatever LANG says on this machine.
vpm.set_language("en")

began = time.time()
done = 0
bad = []

# An empty folder of our own: free_render_name() renames around a file
# that is already there, and then the log names another target.
WORK = tempfile.mkdtemp(prefix="tagreason_")


def check(name, ok, extra=""):
    global done
    done += 1
    print("  %-54s %s %s" % (name, "ok" if ok else "FAIL", extra))
    if not ok:
        bad.append("%s [%s]" % (name, extra or "no numbers"))


class TL(object):
    def GetName(self): return "T"


class P(object):
    """A Resolve project that answers only what it was given.

    GetSetting("") hands over every setting, GetSetting(name) one of
    them -- the real one does not answer a name it does not carry with
    the whole dictionary. SetSetting is here and refuses: a project
    under automatic colour management does not take the dropdown
    names, and without the method the program's attempt would vanish
    into a swallowed exception instead.
    """

    def __init__(self, project=None):
        self.project = dict(project or {})
        self.fc = None; self.settings = None; self.jobs = 0
        self.ok = None

    def SetCurrentTimeline(self, tl): return True
    def GetSetting(self, k):
        return self.project if k == "" else self.project.get(k, "")
    def SetSetting(self, k, v): return False
    def GetRenderFormats(self): return {"MP4": "mp4", "QuickTime": "mov"}
    def GetRenderCodecs(self, f):
        return {"H.264": "H264", "H.265": "H265"}
    def SetCurrentRenderFormatAndCodec(self, f, c):
        self.fc = (f, c); return True
    def SetCurrentRenderMode(self, m): return True
    def SetRenderSettings(self, e): self.settings = e; return True
    def AddRenderJob(self): self.jobs += 1; return "j"


BASE = {"cameras": [{"file": "/tmp/x.mov"}]}
# The tag line, and only it: the "Same as Project" message stands under
# the same label and carries no pair of tags.
TAG_LINE = re.compile(r"^ {4}Tagging {2,}(\S+) / (\S+)(.*)$")


def run(title, d, project=None, project_is_new=False):
    """Queue one job against a fresh fake project, keeping its log."""
    p = P(project)
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        p.ok = vpm.queue_render_job(p, TL(), d, WORK, "Episode 1",
                                    project_is_new)
    p.log = buf.getvalue()
    p.tag_line = ""
    p.tags = None
    p.rest = ""
    for line in p.log.splitlines():
        hit = TAG_LINE.match(line)
        if hit:
            p.tag_line = line
            p.tags = (hit.group(1), hit.group(2))
            p.rest = hit.group(3)
            break
    print("\n== %s\n     %s" % (title, p.tag_line or "(no tag line)"))
    return p


sdr = run("SDR delivery, the project says nothing",
          dict(BASE, height=1080, width=1920, fps=30.0, hdr=False))
# Our own fresh project stands at PQ and will not be steered, so the
# material decides and the delivery stays SDR -- while the project still
# names a curve. That is the pairing the bracket used to be borrowed
# from.
in_hdr = run("SDR delivery inside an HDR project of our own",
             dict(BASE, height=1080, width=1920, fps=30.0, hdr=False),
             project={"colorSpaceOutput": "Rec.2100 ST2084"},
             project_is_new=True)
hdr = run("HDR delivery, the project outputs PQ",
          dict(BASE, height=2160, width=3840, fps=30.0, hdr=True,
               hdr_reason="Transfer function 16 (PQ) in Wide.mov"),
          project={"colorSpaceOutput": "Rec.2100 ST2084"})
no_curve = run("HDR delivery, the project names no curve",
               dict(BASE, height=2160, width=3840, fps=30.0, hdr=True,
                    hdr_reason="Transfer function 16 (PQ) in Wide.mov"))

SDR_709 = ("Rec.709", "Rec.709")
HDR_PQ = ("Rec.2020", "ST.2084")
WHY = "colorSpaceOutput = Rec.2100 ST2084"

print("\n-- the SDR delivery")
check("an SDR delivery tags Rec.709 and says so",
      sdr.tags == SDR_709,
      "wanted %r, got %r in %r" % (SDR_709, sdr.tags, sdr.tag_line))
check("an SDR delivery names no reason beside its tags",
      sdr.rest.strip() == "",
      "wanted nothing after the tags, got %r in %r"
      % (sdr.rest.strip(), sdr.tag_line))

print("\n-- the SDR delivery inside an HDR project")
check("an SDR delivery in an HDR project still tags Rec.709",
      in_hdr.tags == SDR_709,
      "wanted %r, got %r in %r" % (SDR_709, in_hdr.tags, in_hdr.tag_line))
check("an SDR delivery borrows no reason from its project",
      in_hdr.rest.strip() == "",
      "wanted nothing after the tags, got %r in %r"
      % (in_hdr.rest.strip(), in_hdr.tag_line))

print("\n-- the HDR delivery")
check("an HDR delivery tags Rec.2020 and ST.2084",
      hdr.tags == HDR_PQ,
      "wanted %r, got %r in %r" % (HDR_PQ, hdr.tags, hdr.tag_line))
check("an HDR delivery names the project setting as its reason",
      hdr.rest.strip() == "(%s)" % WHY,
      "wanted %r, got %r in %r"
      % ("(%s)" % WHY, hdr.rest.strip(), hdr.tag_line))

print("\n-- the HDR delivery whose project names no curve")
applied = (no_curve.settings or {}).get("ColorSpaceTag")
check("an HDR delivery without a curve applies no tags",
      "ColorSpaceTag" not in (no_curve.settings or {}),
      "wanted no ColorSpaceTag, got %r in %d setting(s)"
      % (applied, len(no_curve.settings or {})))
check("an HDR delivery without a curve prints no tag line",
      no_curve.tag_line == "",
      "wanted no line matching 'Tagging x / y', got %r"
      % (no_curve.tag_line,))

shutil.rmtree(WORK, ignore_errors=True)

print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
