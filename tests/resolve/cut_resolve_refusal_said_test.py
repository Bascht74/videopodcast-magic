# -*- coding: utf-8 -*-
"""What Resolve refuses on the cut timeline is said, and nothing laid on it.

build_cut_timeline and set_timeline_start against a stand-in media pool
and timeline. In turn: a shot before its camera rolled, and one whose
camera is not in the media pool, filled by the wide shot; a cut with
nothing in it; a timeline that took no picture, with no mix laid after
it; fewer shots taken than sent; a mix not in the media pool and one
refused, with A1 left unnamed; a mix out of a camera that rolled early,
trimmed by its head. Then the start timecode: none asked for, one that
raises, one moved elsewhere, and one neither taken nor read back.
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


WIDE, GUEST = "WideCam_C001", "GuestCam_C003"
MIX = "/tmp/Full-Mix.wav"
FPS = 25.0
# The guest's camera rolled five seconds into the programme; the wide
# shot at its start, sixty seconds long.
ROLLED = {WIDE: 0.0, GUEST: 5.0}


def cameras(wide_offset=0.0):
    return [{"camera": WIDE, "track": WIDE, "file": "/tmp/%s.mov" % WIDE,
             "source": "/tmp/%s.mov" % WIDE, "wide": True,
             "offset": wide_offset, "duration": 60.0, "fps": FPS},
            {"camera": GUEST, "track": GUEST, "file": "/tmp/%s.mov" % GUEST,
             "source": "/tmp/%s.mov" % GUEST, "offset": ROLLED[GUEST],
             "duration": 55.0, "fps": FPS}]


def build(cut, cams=None, without=(), mix=(MIX, "stored file"), **pool):
    """Build one cut timeline; return (timeline, project, what was said)."""
    cams = cams or cameras()
    p = stand.Project()
    for k, v in pool.items():
        setattr(p.pool, k, set(v) if k == "refuse_media" else v)
    tl = p.pool.CreateEmptyTimeline("Episode Cut")
    clips = dict((c["file"], stand.Clip(c["file"], frames=1500))
                 for c in cams if c["camera"] not in without)
    if MIX not in without:
        clips[MIX] = stand.Clip(MIX, frames=1500)
    d = {"fps": FPS, "cameras": cams, "start_tc": "01:00:00:00"}
    out = io.StringIO()
    with contextlib.redirect_stdout(out):
        vpm.build_cut_timeline(p.pool, tl, cut, cams, clips, d,
                               mix if mix[0] else None, 0)
    return tl, p, out.getvalue()


def on_v1(tl):
    return [x.GetName() for x in tl.GetItemListInTrack("video", 1)]


def lines_with(said, *words):
    return [l.strip() for l in said.splitlines()
            if all(w in l for w in words)]


THREE = [{"start": 10.0, "end": 20.0, "camera": GUEST},
         {"start": 20.0, "end": 30.0, "camera": WIDE},
         {"start": 30.0, "end": 40.0, "camera": GUEST}]

print("1. A shot its camera cannot give")
tl, p, said = build([{"start": 1.0, "end": 4.0, "camera": GUEST}])
check("a shot before its camera rolled is filled by the wide shot",
      on_v1(tl) == [WIDE + ".mov"], "V1 holds %r" % (on_v1(tl),))
tl, p, said = build(THREE, without=[GUEST])
check("a camera missing from the media pool is filled by another",
      on_v1(tl) == [WIDE + ".mov"] * 3, "V1 holds %r" % (on_v1(tl),))

print("\n2. Nothing to lay")
tl, p, said = build([{"start": 10.0, "end": 10.0, "camera": WIDE}])
check("a cut with nothing in it lays nothing and says so",
      p.pool.count("AppendToTimeline") == 0 and said.strip().endswith(
          vpm.T('  No cut left -- the Timeline stays empty.').strip()),
      "AppendToTimeline asked %d times, said %r"
      % (p.pool.count("AppendToTimeline"), said.strip()[-60:]))

print("\n3. Resolve takes less than it was sent")
tl, p, said = build(THREE, refuse_media=[1])
check("a timeline that took no picture gets no mix laid after it",
      on_v1(tl) == [] and p.pool.count("AppendToTimeline") == 1
      and "Full-Mix" not in said,
      "V1 holds %r, AppendToTimeline asked %d times"
      % (on_v1(tl), p.pool.count("AppendToTimeline")))
tl, p, said = build(THREE, takes=1)
short = lines_with(said, " 1 ", " 3 ")
check("fewer shots taken than sent is said with both numbers",
      len(on_v1(tl)) == 1 and len(short) == 1,
      "V1 holds %d, said %r" % (len(on_v1(tl)), short))

print("\n4. The mix")
tl, p, said = build(THREE, without=[MIX])
check("a mix not in the media pool lays nothing on A1",
      tl.GetItemListInTrack("audio", 1) == []
      and p.pool.count("AppendToTimeline") == 1
      and tl.GetTrackName("audio", 1) == "",
      "A1 holds %d, named %r, AppendToTimeline asked %d times"
      % (len(tl.GetItemListInTrack("audio", 1)), tl.GetTrackName("audio", 1),
         p.pool.count("AppendToTimeline")))
tl, p, said = build(THREE, refuse_media=[2])
check("a mix Resolve refuses leaves A1 unnamed",
      tl.GetItemListInTrack("audio", 1) == []
      and p.pool.count("AppendToTimeline") == 2
      and tl.GetTrackName("audio", 1) == "",
      "A1 holds %d, named %r" % (len(tl.GetItemListInTrack("audio", 1)),
                                 tl.GetTrackName("audio", 1)))
# The wide shot rolled two seconds before the programme and carries
# the mix: fifty frames at its head, and it ends at its own last frame.
early = cameras(wide_offset=-2.0)
tl, p, said = build(THREE, cams=early, mix=(early[0]["file"], "the wide"))
sent = p.pool.sent[-1][0] if p.pool.sent else {}
check("a mix out of a camera that rolled early is trimmed by its head",
      sent.get("startFrame") == 50 and sent.get("endFrame") == 1500
      and sent.get("mediaType") == 2,
      "sent startFrame %r, endFrame %r, mediaType %r, wanted 50, 1500, 2"
      % (sent.get("startFrame"), sent.get("endFrame"),
         sent.get("mediaType")))

print("\n5. The start timecode")
START = "01:00:00:00"


def start(tc, **switches):
    """(what set_timeline_start returned, said, the timeline)."""
    tl = stand.Timeline("Episode Cut", **switches)
    out = io.StringIO()
    with contextlib.redirect_stdout(out):
        got = vpm.set_timeline_start(tl, tc)
    return got, out.getvalue(), tl


got, said, tl = start("")
check("no start timecode asks nothing of Resolve",
      got is True and tl.count("SetStartTimecode") == 0,
      "returned %r, SetStartTimecode asked %d times"
      % (got, tl.count("SetStartTimecode")))
got, said, tl = start(START, throw=["SetStartTimecode"])
check("a start Resolve raises on is said and not counted as taken",
      got is False and len(lines_with(said, START, "refused by raising")) == 1,
      "returned %r, said %r" % (got, said.strip()))
got, said, tl = start(START, moves_start_to="00:59:59:00")
check("a start Resolve moves elsewhere is said with both timecodes",
      got is False and len(lines_with(said, START, "00:59:59:00")) == 1,
      "returned %r, said %r" % (got, said.strip()))
got, said, tl = start(START, refuse=["SetStartTimecode"],
                      throw=["GetStartTimecode"])
check("a start neither taken nor read back is said",
      got is False and len(lines_with(said, START)) == 1,
      "returned %r, said %r" % (got, said.strip()))

print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
