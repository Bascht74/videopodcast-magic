# -*- coding: utf-8 -*-
"""What Resolve refuses on the render page is said, and no job is faked.

queue_render_job against stand-in projects that raise or answer no at
one call each. In turn: a timeline that cannot be made current, a format
list, a codec list, a format and codec that raise, a one-file mode that
raises, a job that raises; HDR without H.265, HDR whose project names no
curve, tags no spelling of which is taken, and the line saying how to
check an HDR delivery; and a new project that cannot follow the
material, warned about while the material decides.
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


WORK = tempfile.mkdtemp(prefix="render_refused_")
SDR = {"height": 1080, "width": 1920, "fps": 25.0}
HDR = dict(SDR, hdr=True, hdr_reason="the material says so")
REFUSAL = "refused by raising"
H264_ONLY = {"mp4": {"H.264": "H264"}}


def queue(p, d=SDR, new=False):
    """(what queue_render_job returned, what it printed, the timeline)."""
    tl = p.pool.CreateEmptyTimeline("Episode Cut")
    out = io.StringIO()
    with contextlib.redirect_stdout(out):
        got = vpm.queue_render_job(p, tl, d, WORK, "Episode",
                                   project_is_new=new)
    return got, out.getvalue(), tl


def lines_with(said, word):
    return [l.strip() for l in said.splitlines() if word in l]


print("1. A refusal that stops the job")
p = stand.Project(throw=["GetRenderFormats"])
got, said, tl = queue(p)
check("a format list that raises stops the job with its reason",
      got is False and not p.jobs and len(lines_with(said, REFUSAL)) == 1,
      "returned %r, %d jobs, said %r"
      % (got, len(p.jobs), lines_with(said, REFUSAL)))
p = stand.Project(throw=["GetRenderCodecs"])
got, said, tl = queue(p)
check("a codec list that raises stops the job with its reason",
      got is False and not p.jobs and len(lines_with(said, REFUSAL)) == 1,
      "returned %r, %d jobs, said %r"
      % (got, len(p.jobs), lines_with(said, REFUSAL)))
p = stand.Project(throw=["SetCurrentRenderFormatAndCodec"])
got, said, tl = queue(p)
check("a format and codec that raise stop the job before its settings",
      got is False and p.count("SetRenderSettings") == 0
      and len(lines_with(said, REFUSAL)) == 1,
      "returned %r, settings sent %d times, said %r"
      % (got, p.count("SetRenderSettings"), lines_with(said, REFUSAL)))
p = stand.Project(throw=["AddRenderJob"])
got, said, tl = queue(p)
check("a job Resolve raises on is not reported as queued",
      got is False and not p.jobs and len(lines_with(said, REFUSAL)) == 1,
      "returned %r, %d jobs, said %r"
      % (got, len(p.jobs), lines_with(said, REFUSAL)))

print("\n2. A refusal the job goes on past")
p = stand.Project(throw=["SetCurrentTimeline"])
got, said, tl = queue(p)
check("a timeline that cannot be made current does not stop the job",
      got is True and len(p.jobs) == 1,
      "returned %r, %d jobs" % (got, len(p.jobs)))
p = stand.Project(throw=["SetCurrentRenderMode"])
got, said, tl = queue(p)
check("a one-file mode that raises is said and the job still queued",
      got is True and len(p.jobs) == 1
      and len(lines_with(said, REFUSAL)) == 1,
      "returned %r, %d jobs, said %r"
      % (got, len(p.jobs), lines_with(said, REFUSAL)))

print("\n3. HDR")
PQ = {"colorSpaceOutput": "Rec.2100 ST2084"}
p = stand.Project(settings=PQ, codecs=H264_ONLY)
got, said, tl = queue(p, HDR)
check("HDR without H.265 is rendered in H.264 and warned about",
      got is True and p.format_codec == ("mp4", "H264")
      and len(lines_with(said, "H.265")) == 1,
      "returned %r, chose %r, said %r"
      % (got, p.format_codec, lines_with(said, "H.265")))
p = stand.Project(settings={"colorSpaceOutput": "Rec.2100"})
got, said, tl = queue(p, HDR)
job = p.jobs[0] if p.jobs else {}
check("an HDR project that names no curve leaves the tags untouched",
      got is True and "ColorSpaceTag" not in job
      and job.get("EncodingProfile") == "Main10",
      "returned %r, job %r" % (got, sorted(job)))
p = stand.Project(settings=PQ, render_refuses=["ColorSpaceTag"])
got, said, tl = queue(p, HDR)
job = p.jobs[0] if p.jobs else {}
tagged = lines_with(said, "ST.2084")
check("tags no spelling of which is taken are left for the hand",
      got is True and "ColorSpaceTag" not in job
      and job.get("EncodingProfile") == "Main10" and len(tagged) == 1,
      "returned %r, job %r, said %r" % (got, sorted(job), tagged))
p = stand.Project(settings=PQ)
got, said, tl = queue(p, HDR)
target = os.path.join(WORK, "Episode.mp4")
told = lines_with(said, "--hdr-check")
check("an HDR delivery says how to check the finished file",
      got is True and len(told) == 1 and target in said,
      "said %r" % [l.replace(WORK, "<work>") for l in told])

print("\n4. A new project that cannot follow the material")
p = stand.Project(settings=PQ, accepts={"colorSpaceOutput": []})
got, said, tl = queue(p, SDR, new=True)
job = p.jobs[0] if p.jobs else {}
warned = lines_with(said, "Rec.2100 ST2084")
check("a new project left at HDR is warned about, the material decides",
      got is True and len(warned) == 1
      and job.get("ColorSpaceTag") == vpm.SDR_TAGS[0][0]
      and p.settings["colorSpaceOutput"] == "Rec.2100 ST2084",
      "returned %r, warned %r, tagged %r"
      % (got, warned, job.get("ColorSpaceTag")))

print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
