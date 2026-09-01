# -*- coding: utf-8 -*-
"""The render job handed to Resolve carries format, codec and settings.

Nothing is written to disk here: queue_render_job only calls methods on
the project object, so there is no rendered file to measure. What is
checked is the job as Resolve receives it -- which format and codec were
chosen, what the settings dictionary holds, and that a refusal leaves the
queue empty. The one thing that does touch the filesystem is the target
name: an existing delivery must not be rendered over.
"""
import os
HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = os.environ.get("VPM_SCRIPT") or os.path.join(
    os.path.dirname(HERE), "videopodcast-magic.py")
import importlib.util, sys, tempfile, io, contextlib, time
began = time.time()
spec = importlib.util.spec_from_file_location(
    "vpm", SCRIPT)
vpm = importlib.util.module_from_spec(spec); sys.modules["vpm"] = vpm
spec.loader.exec_module(vpm)

done = 0
bad = []


def check(name, ok, extra=""):
    global done
    done += 1
    print("  %-58s %s %s" % (name, "ok" if ok else "FAIL", extra))
    if not ok:
        bad.append("%s [%s]" % (name, extra or "no numbers"))


class TL(object):
    def GetName(self): return "Test Cut"


class P(object):
    """A Resolve project that writes down what was asked of it."""

    def __init__(self, formats, codecs, accepts=True, settings_ok=True,
                 job=True, mode_ok=True):
        self.formats, self.codecs, self.accepts = formats, codecs, accepts
        self.settings_ok, self.job, self.mode_ok = settings_ok, job, mode_ok
        self.applied = None; self.jobs = 0; self.mode = None
        self.fc = None; self.timeline = None; self.tries = 0

    def SetCurrentTimeline(self, tl): self.timeline = tl; return True

    def GetRenderFormats(self): return self.formats

    def GetRenderCodecs(self, f): return self.codecs.get(f, {})

    def SetCurrentRenderFormatAndCodec(self, f, c):
        self.fc = (f, c); return self.accepts

    # Resolve can refuse this, and a stand-in that never does would
    # let the silence that follows a refusal go unnoticed.
    def SetCurrentRenderMode(self, m): self.mode = m; return self.mode_ok

    def SetRenderSettings(self, e):
        self.tries += 1
        if not self.settings_ok:
            return False
        self.applied = e; return True

    def AddRenderJob(self):
        if not self.job:
            return ""
        self.jobs += 1; return "job1"


FORMATS = {"MP4": "mp4", "QuickTime": "mov", "MXF OP1A": "mxf"}
CODECS = {"mp4": {"H.264": "H264", "H.265": "H265",
                  "H.264 (NVIDIA)": "H264_NVIDIA"}}
WORK = tempfile.mkdtemp(prefix="render_")


def queue(folder, height=1080, width=1920, fps=30.0, name="Episode 12",
          **fake):
    """Queue one job against a fresh fake project and hand both back."""
    p = P(FORMATS, CODECS, **fake)
    camera = os.path.join(folder, "x.mov")
    d = {"height": height, "width": width, "fps": fps,
         "cameras": [{"file": camera, "source": camera}]}
    return p, vpm.queue_render_job(p, TL(), d, folder, name)


# --- the three sizes, each in its own folder so no name is taken -------
bitrates = {}
for height, width in ((1080, 1920), (2160, 3840), (720, 1280)):
    folder = os.path.join(WORK, "%dp" % height)
    os.makedirs(folder)
    print("\n== %dp30 SDR" % height)
    p, queued = queue(folder, height, width, 30.0)
    tag = "%dp:" % height
    s = p.applied or {}
    bitrates[height] = s.get("VideoQuality")
    want_rate = vpm.bitrate_for(height, 30.0, False)

    check("%s queue_render_job says it worked" % tag, queued is True,
          "returned %r" % (queued,))
    check("%s the job sits on the timeline it was given" % tag,
          isinstance(p.timeline, TL), "timeline %r" % (p.timeline,))
    check("%s MP4 wins over QuickTime and MXF" % tag,
          p.fc is not None and p.fc[0] == "mp4",
          "chose %r out of %r" % (p.fc, sorted(FORMATS)))
    check("%s SDR takes H.264, not H.265" % tag,
          p.fc is not None and p.fc[1] == "H264",
          "chose %r out of %r" % (p.fc, sorted(CODECS["mp4"].values())))
    check("%s one file, not one per clip" % tag, p.mode == 1,
          "SetCurrentRenderMode(%r), 1 is one file" % (p.mode,))
    check("%s exactly one job queued" % tag, p.jobs == 1,
          "AddRenderJob ran %d times" % p.jobs)
    check("%s the settings arrived" % tag, bool(s),
          "SetRenderSettings got %r" % (p.applied,))
    check("%s the whole timeline is rendered" % tag,
          s.get("SelectAllFrames") is True,
          "SelectAllFrames %r" % (s.get("SelectAllFrames"),))
    check("%s picture and sound are both exported" % tag,
          s.get("ExportVideo") is True and s.get("ExportAudio") is True,
          "video %r, audio %r" % (s.get("ExportVideo"),
                                  s.get("ExportAudio")))
    check("%s target folder is the one handed in" % tag,
          s.get("TargetDir") == folder,
          "TargetDir %r, wanted %r" % (s.get("TargetDir"), folder))
    check("%s the name is the one handed in" % tag,
          s.get("CustomName") == "Episode 12",
          "CustomName %r, wanted 'Episode 12'" % (s.get("CustomName"),))
    check("%s frame size comes from the material" % tag,
          s.get("FormatWidth") == width and s.get("FormatHeight") == height,
          "%r x %r, wanted %dx%d" % (s.get("FormatWidth"),
                                     s.get("FormatHeight"), width, height))
    check("%s frame rate comes from the material" % tag,
          s.get("FrameRate") == 30.0,
          "FrameRate %r, wanted 30.0" % (s.get("FrameRate"),))
    check("%s bitrate is the one the table gives" % tag,
          s.get("VideoQuality") == want_rate,
          "VideoQuality %r, bitrate_for(%d, 30.0, False) = %r"
          % (s.get("VideoQuality"), height, want_rate))
    check("%s sound is AAC at 16 bit" % tag,
          s.get("AudioCodec") == "aac" and s.get("AudioBitDepth") == 16,
          "codec %r, depth %r" % (s.get("AudioCodec"),
                                  s.get("AudioBitDepth")))
    check("%s sample rate is the one we work at" % tag,
          s.get("AudioSampleRate") == vpm.SR,
          "AudioSampleRate %r, vpm.SR is %r"
          % (s.get("AudioSampleRate"), vpm.SR))
    first_pair = (vpm.SDR_TAGS[0][0], vpm.SDR_TAGS[1][0])
    check("%s SDR is tagged, not left to the project" % tag,
          (s.get("ColorSpaceTag"), s.get("GammaTag")) == first_pair,
          "tagged %r, wanted %r"
          % ((s.get("ColorSpaceTag"), s.get("GammaTag")), first_pair))

print("\n== the bitrate follows the frame size")
check("more pixels get more bitrate",
      (bitrates.get(2160) or 0) > (bitrates.get(1080) or 0)
      > (bitrates.get(720) or 0),
      "2160p %r, 1080p %r, 720p %r"
      % (bitrates.get(2160), bitrates.get(1080), bitrates.get(720)))

# --- a delivery that is already there is not rendered over ------------
print("\n== the earlier delivery stays")
folder = os.path.join(WORK, "again")
os.makedirs(folder)
open(os.path.join(folder, "Episode 12.mp4"), "w").write("x")
p, queued = queue(folder, 1080, 1920, 30.0)
taken = (p.applied or {}).get("CustomName")
check("a taken name gives way to the next one", taken == "Episode 12_2",
      "CustomName %r although 'Episode 12.mp4' lies in the folder" % (taken,))
check("and the job is queued all the same", queued is True and p.jobs == 1,
      "returned %r, %d jobs" % (queued, p.jobs))

# --- the ways it gives up ---------------------------------------------
print("\n== no MP4 on offer")
p = P({"QuickTime": "mov"}, {})
queued = vpm.queue_render_job(p, TL(), {"height": 1080, "width": 1920,
                                        "fps": 25}, WORK, "X")
check("without MP4 it says no", queued is False, "returned %r" % (queued,))
check("and nothing was queued", p.jobs == 0 and p.applied is None,
      "%d jobs, settings %r" % (p.jobs, p.applied))

print("\n== no codec that fits")
p = P(FORMATS, {"mp4": {"DNxHR HQ": "DNxHR"}})
queued = vpm.queue_render_job(p, TL(), {"height": 1080, "width": 1920,
                                        "fps": 25}, WORK, "X")
check("without H.264 it says no", queued is False,
      "returned %r" % (queued,))
check("and nothing was queued", p.jobs == 0 and p.applied is None,
      "%d jobs, settings %r" % (p.jobs, p.applied))

print("\n== one file per delivery is refused")
buf = io.StringIO()
with contextlib.redirect_stdout(buf):
    p, queued = queue(WORK, name="Y", mode_ok=False)
said = buf.getvalue()
spoke = [l.strip() for l in said.splitlines() if "one file per clip" in l]
check("a refused one-file mode is said out loud", bool(spoke),
      "said %r" % (spoke[0] if spoke else
                   "nothing about it in %d lines" % len(said.splitlines()),))
check("and the delivery is queued all the same", queued is not False
      and p.jobs == 1, "returned %r, %d jobs" % (queued, p.jobs))

print("\n== the format is refused")
p, queued = queue(WORK, name="X", accepts=False)
check("a refused format says no", queued is False, "returned %r" % (queued,))
check("a refused format queues nothing", p.jobs == 0,
      "AddRenderJob ran %d times after the refusal" % p.jobs)
check("and no settings were sent after it", p.applied is None
      and p.tries == 0,
      "SetRenderSettings ran %d times, got %r" % (p.tries, p.applied))

print("\n== the settings are refused")
p, queued = queue(WORK, name="X", settings_ok=False)
check("refused settings say no", queued is False, "returned %r" % (queued,))
check("refused settings queue nothing", p.jobs == 0,
      "AddRenderJob ran %d times after the refusal" % p.jobs)
check("every spelling was tried before giving up", p.tries > 1,
      "SetRenderSettings ran %d times, one try per spelling" % p.tries)

print("\n== Resolve makes no job of it")
p, queued = queue(WORK, name="X", job=False)
check("no job means no", queued is False, "returned %r" % (queued,))

print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
