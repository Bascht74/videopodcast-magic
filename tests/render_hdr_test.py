# -*- coding: utf-8 -*-
"""Render profile: HDR against SDR, frame rate, project setting.

A smoke test on purpose, for the same reason as render_test.py: whether
the HDR flags are right shows in Resolve and in the written file, not
here. This one catches a crash and a missing key.
"""
import os
HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = os.environ.get("VPM_SCRIPT") or os.path.join(
    os.path.dirname(HERE), "videopodcast-magic.py")
import importlib.util, sys
spec = importlib.util.spec_from_file_location(
    "vpm", SCRIPT)
vpm = importlib.util.module_from_spec(spec); sys.modules["vpm"] = vpm
spec.loader.exec_module(vpm)

class TL(object):
    def GetName(self): return "T"
class P(object):
    def __init__(self, project=None, profile_ok=True):
        self.project = project or {}
        self.profile_ok = profile_ok
        self.fc = None; self.settings = None; self.jobs = 0
    def SetCurrentTimeline(self, tl): return True
    def GetSetting(self, k): return self.project
    def GetRenderFormats(self): return {"MP4": "mp4", "QuickTime": "mov"}
    def GetRenderCodecs(self, f):
        return {"H.264": "H264", "H.265": "H265",
                "H.265 (NVIDIA)": "H265_NV"}
    def SetCurrentRenderFormatAndCodec(self, f, c):
        self.fc = (f, c); return True
    def SetCurrentRenderMode(self, m): return True
    def SetRenderSettings(self, e):
        if "EncodingProfile" in e and not self.profile_ok:
            return False
        self.settings = e; return True
    def AddRenderJob(self): self.jobs += 1; return "j"

def run(title, d, project=None, profile_ok=True):
    print("\n== %s" % title)
    p = P(project, profile_ok)
    vpm.queue_render_job(p, TL(), d, "/tmp", "Episode 1")
    print("   Codec:", p.fc, "| profile:",
          (p.settings or {}).get("EncodingProfile", "-"))

BASE = {"cameras": [{"file": "/tmp/x.mov"}]}
run("SDR 1080p30", dict(BASE, height=1080, width=1920, fps=30.0, hdr=False))
run("SDR 2160p60", dict(BASE, height=2160, width=3840, fps=60.0, hdr=False))
run("HDR 2160p30", dict(BASE, height=2160, width=3840, fps=30.0, hdr=True,
                        hdr_reason="Transfer function 18 (HLG) in Wide.mov"))
run("HDR 2160p60", dict(BASE, height=2160, width=3840, fps=59.94, hdr=True))
run("HDR, but Resolve will not take Main10",
    dict(BASE, height=2160, width=3840, fps=30.0, hdr=True),
    profile_ok=False)
run("Material SDR, but the project is HDR",
    dict(BASE, height=2160, width=3840, fps=30.0, hdr=False),
    project={"colorSpaceOutput": "Rec.2100 ST2084"})
run("Material HDR, but the project is Rec.709",
    dict(BASE, height=1080, width=1920, fps=25.0, hdr=True,
         hdr_reason="BT.2020 in G.mov"),
    project={"colorSpaceOutput": "Rec.709 Gamma 2.4"})
