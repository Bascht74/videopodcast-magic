# -*- coding: utf-8 -*-
"""The render job carries the codec, profile and tags of its range.

Nothing reaches the disk here. queue_render_job() writes no file; it
sets values on a Resolve project and queues a job, and this test holds
a fake project up to it and reads back what was handed over: format and
codec, the ten bit profile, the bitrate, the picture, the colour tags.
Whether Resolve then delivers what it was told is not visible from
here.
"""
import os
HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = os.environ.get("VPM_SCRIPT") or os.path.join(
    os.path.dirname(HERE), "videopodcast_magic.py")
import importlib.util, sys, tempfile, time
began = time.time()
spec = importlib.util.spec_from_file_location(
    "vpm", SCRIPT)
vpm = importlib.util.module_from_spec(spec); sys.modules["vpm"] = vpm
spec.loader.exec_module(vpm)

# An empty folder of our own: free_render_name() renames around a file
# that is already there, and then the target name is not the one asked
# for.
WORK = tempfile.mkdtemp(prefix="renderhdr_")
done = 0
bad = []


def check(name, ok, extra=""):
    global done
    done += 1
    print("  %-58s %s %s" % (name, "ok" if ok else "FAIL", extra))
    if not ok:
        bad.append("%s [%s]" % (name, extra or "no numbers"))


class TL(object):
    def GetName(self): return "T"


class P(object):
    def __init__(self, project=None, profile_ok=True, formats=None):
        self.project = project or {}
        self.profile_ok = profile_ok
        self.formats = ({"MP4": "mp4", "QuickTime": "mov"}
                        if formats is None else formats)
        self.fc = None; self.settings = None; self.jobs = 0
        self.ok = None
    def SetCurrentTimeline(self, tl): return True
    def GetSetting(self, k): return self.project
    def GetRenderFormats(self): return self.formats
    def GetRenderCodecs(self, f):
        return {"H.264": "H264", "H.265": "H265",
                "H.265 (NVIDIA)": "H265_NV"}
    def SetCurrentRenderFormatAndCodec(self, f, c):
        self.fc = (f, c); return True
    def SetCurrentRenderMode(self, m): return True
    def SetRenderSettings(self, e):
        # A Resolve that does not know the profile name rejects the whole
        # dictionary. It is the name it does not know, not the key.
        if e.get("EncodingProfile") == "Main10" and not self.profile_ok:
            return False
        self.settings = e; return True
    def AddRenderJob(self): self.jobs += 1; return "j"


def run(title, d, project=None, profile_ok=True, formats=None):
    """Queue one job against a fresh fake project and hand it back."""
    print("\n== %s" % title)
    p = P(project, profile_ok, formats)
    p.ok = vpm.queue_render_job(p, TL(), d, WORK, "Episode 1")
    return p


def verdict(title, p, codec, profile, bitrate, picture, tags):
    """Hold one queued job against what its range asks for."""
    s = p.settings or {}
    check("%s: queued" % title, p.ok is True and p.jobs == 1,
          "returned %r, %d job(s)" % (p.ok, p.jobs))
    check("%s: format and codec" % title, p.fc == ("mp4", codec),
          "wanted ('mp4', %r), got %r" % (codec, p.fc))
    check("%s: encoding profile" % title,
          s.get("EncodingProfile") == profile,
          "wanted %r, got %r" % (profile, s.get("EncodingProfile")))
    check("%s: bitrate" % title, s.get("VideoQuality") == bitrate,
          "wanted %r kbit/s, got %r" % (bitrate, s.get("VideoQuality")))
    got = (s.get("FormatWidth"), s.get("FormatHeight"), s.get("FrameRate"))
    check("%s: picture and frame rate" % title, got == picture,
          "wanted %r, got %r" % (picture, got))
    seen = ((s.get("ColorSpaceTag"), s.get("GammaTag"))
            if "ColorSpaceTag" in s else None)
    check("%s: colour tagging" % title, seen == tags,
          "wanted %r, got %r" % (tags, seen))
    return seen


BASE = {"cameras": [{"file": "/tmp/x.mov"}]}
SDR_709 = ("Rec.709", "Rec.709")
HDR_PQ = ("Rec.2020", "ST.2084")

sdr_1080 = run("SDR 1080p30",
               dict(BASE, height=1080, width=1920, fps=30.0, hdr=False))
sdr_2160 = run("SDR 2160p60",
               dict(BASE, height=2160, width=3840, fps=60.0, hdr=False))
hdr_2160 = run("HDR 2160p30",
               dict(BASE, height=2160, width=3840, fps=30.0, hdr=True,
                    hdr_reason="Transfer function 18 (HLG) in Wide.mov"))
hdr_hfr = run("HDR 2160p60",
              dict(BASE, height=2160, width=3840, fps=59.94, hdr=True))
refused = run("HDR, but Resolve will not take Main10",
              dict(BASE, height=2160, width=3840, fps=30.0, hdr=True),
              profile_ok=False)
to_hdr = run("Material SDR, but the project is HDR",
             dict(BASE, height=2160, width=3840, fps=30.0, hdr=False),
             project={"colorSpaceOutput": "Rec.2100 ST2084"})
to_sdr = run("Material HDR, but the project is Rec.709",
             dict(BASE, height=1080, width=1920, fps=25.0, hdr=True,
                  hdr_reason="BT.2020 in G.mov"),
             project={"colorSpaceOutput": "Rec.709 Gamma 2.4"})
no_mp4 = run("No MP4 on offer",
             dict(BASE, height=1080, width=1920, fps=30.0, hdr=False),
             formats={"QuickTime": "mov"})

print("\n-- what was handed to Resolve")
# A fake project names no HDR curve unless it was given one, so the
# three plain HDR jobs stay at "Same as Project" and carry no tag.
used = [
    verdict("SDR 1080p30", sdr_1080, "H264", None, 8000,
            (1920, 1080, 30.0), SDR_709),
    verdict("SDR 2160p60", sdr_2160, "H264", None, 68000,
            (3840, 2160, 60.0), SDR_709),
    verdict("HDR 2160p30", hdr_2160, "H265", "Main10", 56000,
            (3840, 2160, 30.0), None),
    verdict("HDR 2160p60", hdr_hfr, "H265", "Main10", 85000,
            (3840, 2160, 59.94), None),
    verdict("HDR, Main10 refused", refused, "H265", None, 56000,
            (3840, 2160, 30.0), None),
    verdict("project HDR beats SDR material", to_hdr, "H265", "Main10",
            56000, (3840, 2160, 30.0), HDR_PQ),
    verdict("project SDR beats HDR material", to_sdr, "H264", None, 8000,
            (1920, 1080, 25.0), SDR_709),
]

print("\n-- the give-up path")
check("no MP4 on offer: nothing is queued",
      no_mp4.ok is False and no_mp4.jobs == 0 and no_mp4.settings is None,
      "returned %r, %d job(s), settings %r"
      % (no_mp4.ok, no_mp4.jobs, no_mp4.settings))

print("\n-- across all seven jobs")
every = [("SDR 1080p30", sdr_1080), ("SDR 2160p60", sdr_2160),
         ("HDR 2160p30", hdr_2160), ("HDR 2160p60", hdr_hfr),
         ("HDR, Main10 refused", refused),
         ("project HDR beats SDR material", to_hdr),
         ("project SDR beats HDR material", to_sdr)]
off_rate = ["%s: %r" % (t, (p.settings or {}).get("AudioSampleRate"))
            for t, p in every
            if (p.settings or {}).get("AudioSampleRate") != vpm.SR]
check("audio at the sample rate of the mix", not off_rate,
      "vpm.SR = %r, off: %s" % (vpm.SR, "; ".join(off_rate) or "none"))
off_target = ["%s: %r / %r" % (t, (p.settings or {}).get("TargetDir"),
                               (p.settings or {}).get("CustomName"))
              for t, p in every
              if (p.settings or {}).get("TargetDir") != WORK
              or (p.settings or {}).get("CustomName") != "Episode 1"]
check("target folder and name as asked for", not off_target,
      "wanted %r / 'Episode 1', off: %s"
      % (WORK, "; ".join(off_target) or "none"))

offered = set()
for clear, curves in list(vpm.HDR_TAGS.values()) + [vpm.SDR_TAGS]:
    for space in clear:
        for gamma in curves:
            offered.add((space, gamma))
taken = set(t for t in used if t)
check("every tag used is a spelling the tables offer",
      taken <= offered, "used %s, not offered: %s"
      % (sorted(taken), sorted(taken - offered) or "none"))

print("\n-- the bitrate, without restating the table")
TABLE = [(1080, 30.0, False, 8000), (2160, 60.0, False, 68000),
         (2160, 30.0, True, 56000), (2160, 59.94, True, 85000)]
off_table = ["%dp%g hdr=%s: %r instead of %d"
             % (h, f, hd, vpm.bitrate_for(h, f, hd), b)
             for h, f, hd, b in TABLE if vpm.bitrate_for(h, f, hd) != b]
check("bitrate_for holds the numbers checked above", not off_table,
      "; ".join(off_table) or "all four agree")
hdr_60 = (hdr_hfr.settings or {}).get("VideoQuality")
sdr_60 = (sdr_2160.settings or {}).get("VideoQuality")
hdr_30 = (hdr_2160.settings or {}).get("VideoQuality")
check("HDR gets more than SDR at 2160p60",
      isinstance(hdr_60, int) and isinstance(sdr_60, int)
      and hdr_60 > sdr_60,
      "HDR %r against SDR %r" % (hdr_60, sdr_60))
check("60 fps gets more than 30 fps in HDR 2160p",
      isinstance(hdr_60, int) and isinstance(hdr_30, int)
      and hdr_60 > hdr_30,
      "60 fps %r against 30 fps %r" % (hdr_60, hdr_30))

print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
