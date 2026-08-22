# -*- coding: utf-8 -*-
"""Render profile: does it find format and codec, and what does it set?

A smoke test on purpose. What this builds is a render job for DaVinci
Resolve, and whether the job is right can only be seen by handing it to
Resolve and looking at the file that comes out. So this catches a crash
and a missing key, not a wrong setting -- and saying so here is better
than a check that pretends to know.
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
    def GetName(self): return "Test Cut"

class P(object):
    def __init__(self, formats, codecs, accepts=True):
        self.formats, self.codecs, self.accepts = formats, codecs, accepts
        self.applied = None; self.jobs = 0; self.mode = None
        self.fc = None
    def SetCurrentTimeline(self, tl): return True
    def GetRenderFormats(self): return self.formats
    def GetRenderCodecs(self, f): return self.codecs.get(f, {})
    def SetCurrentRenderFormatAndCodec(self, f, c):
        self.fc = (f, c); return self.accepts
    def SetCurrentRenderMode(self, m): self.mode = m; return True
    def SetRenderSettings(self, e): self.applied = e; return True
    def AddRenderJob(self): self.jobs += 1; return "job1"

FORMATS = {"MP4": "mp4", "QuickTime": "mov", "MXF OP1A": "mxf"}
CODECS = {"mp4": {"H.264": "H264", "H.265": "H265",
                  "H.264 (NVIDIA)": "H264_NVIDIA"}}

for height, width in ((1080, 1920), (2160, 3840), (720, 1280)):
    p = P(FORMATS, CODECS)
    d = {"height": height, "width": width, "fps": 30.0,
         "cameras": [{"file": "/tmp/x.mov", "source": "/tmp/x.mov"}]}
    print("\n== %dp" % height)
    vpm.queue_render_job(p, TL(), d, "/tmp", "Episode 12")
    print("   chosen:", p.fc, "| mode:", p.mode, "| jobs:", p.jobs)

print("\n== no MP4 on offer ==")
p = P({"QuickTime": "mov"}, {})
vpm.queue_render_job(p, TL(), {"height": 1080, "width": 1920, "fps": 25},
                     "/tmp", "X")
print("\n== the format is refused ==")
p = P(FORMATS, CODECS, accepts=False)
vpm.queue_render_job(p, TL(), {"height": 1080, "width": 1920, "fps": 25},
                     "/tmp", "X")
