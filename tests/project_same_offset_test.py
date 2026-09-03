# -*- coding: utf-8 -*-
"""Preview and Resolve put a camera at the same offset.

Both start from the place the run wrote into the handover, and from
there the two go different ways: the player asks camera_offset and
keys on the track name, the Resolve build works out a startFrame from
cam["offset"] and keys on the camera's own name, counted at that
camera's rate rather than the Timeline's. So the two are held against
each other where they can really come apart -- across the two name
spaces, and across two rates.

The sections: the two name spaces; one shot per camera through both
routes; a camera running slower than the Timeline; the stored place
taken as it stands rather than worked out again; and the other shape
camera_offset is given, a preview that has no places yet.

The material makes the clocks and the stored places disagree on
purpose: with the two agreeing, a route that quietly went back to the
clocks would answer the same and nothing here could see it.
"""
import os
HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = os.environ.get("VPM_SCRIPT") or os.path.join(
    os.path.dirname(HERE), "videopodcast_magic.py")
import importlib.util, io, json, struct, sys, tempfile, time
import contextlib
began = time.time()
spec = importlib.util.spec_from_file_location("vpm", SCRIPT)
vpm = importlib.util.module_from_spec(spec); sys.modules["vpm"] = vpm
spec.loader.exec_module(vpm)
WORK = tempfile.mkdtemp(prefix="sameoffset_")
done = 0
bad = []


def check(name, ok, extra=""):
    global done
    done += 1
    print("  %-58s %s %s" % (name, "ok" if ok else "FAIL", extra))
    if not ok:
        bad.append("%s [%s]" % (name, extra or "no numbers"))


class Args(object):
    production = "Test"
    resolve = False
    lufs = -16.0
    intro = None
    outro = None


def stamped(path, seconds):
    """Write a file that carries *seconds* in a bext chunk."""
    body = (b"\0" * 338 + struct.pack("<Q", int(round(seconds * vpm.SR)))
            + b"\0" * 8)
    with open(path, "wb") as f:
        f.write(b"RIFF" + struct.pack("<I", 4 + 8 + len(body)) + b"WAVE")
        f.write(b"bext" + struct.pack("<I", len(body)) + body)
    return path


class FakeClip(object):
    def __init__(self, name):
        self.name = name


class FakeItem(object):
    def __init__(self, frames):
        self.frames = frames

    def GetDuration(self):
        return self.frames


class FakePool(object):
    """Takes what build_cut_timeline sends and keeps it."""

    def __init__(self):
        self.sent = []

    def AppendToTimeline(self, item):
        self.sent.extend(item)
        return [FakeItem(x.get("endFrame", 0) - x.get("startFrame", 0))
                for x in item]


class FakeTimeline(object):
    def __init__(self, pool):
        self.pool = pool

    def SetStartTimecode(self, tc):
        return True

    def SetTrackName(self, *a):
        return True

    def GetItemListInTrack(self, kind, i):
        if kind != "video":
            return []
        return [FakeItem(x.get("endFrame", 0) - x.get("startFrame", 0))
                for x in self.pool.sent if x.get("mediaType") == 1]


ZERO = 68100.0                                # 18:55:00:00, the wide shot
FPS = 30.0
# Per camera: the clock its file carries, and what the alignment
# measured. None of the two agree anywhere -- the run places a camera
# by the measurement, and a route that fell back on the clock would
# have to answer 0.0, 4.0 and 17.4 instead.
NIGHT = [("WideCam", 68100.0, 0.0),
         ("PresenterCam", 68104.0, -33.34),
         ("GuestCam", 68117.4, -60.11)]
SPEAKER_OF = {"PresenterCam": "Presenter", "GuestCam": "Guest"}
# One shot per camera, each late enough that every camera was already
# running: a shot before a camera came in is refused by the build and
# taken by another one, which is a different claim from this one.
CUT = [(40.0, 70.0, "WideCam"), (70.0, 100.0, "PresenterCam"),
       (100.0, 130.0, "GuestCam")]

night = os.path.join(WORK, "night")
os.makedirs(night)
n_cameras, n_videos, n_results, n_offsets, n_tracks = [], [], [], {}, []
for name, tc, measured in NIGHT:
    src = os.path.join(WORK, name + "_source.mov")
    open(src, "w").write("x")
    rendered = stamped(os.path.join(WORK, name + ".wav"), tc)
    n_cameras.append({"name": name, "video": src})
    n_videos.append((src, {"fps": FPS, "width": 1920, "height": 1080,
                           "duration": 300.0,
                           "tc": vpm.timecode_string(tc, FPS)}))
    n_results.append(rendered)
    n_offsets[os.path.abspath(rendered)] = measured
    if name in SPEAKER_OF:
        n_tracks.append({"name": SPEAKER_OF[name], "camera": src})

with contextlib.redirect_stdout(io.StringIO()):
    vpm.write_handover(Args(), n_tracks, n_cameras, n_videos, night, ZERO,
                       (n_cameras[0]["video"], n_videos[0][1]), n_results,
                       list(CUT), None, 130.0, None, None, n_offsets)
written = json.load(io.open(os.path.join(night, "Test_resolve.json"),
                            encoding="utf-8"))
a_frame = 1.0 / max(1.0, float(written["fps_measured"]))
track_of = {cam["camera"]: cam["track"] for cam in written["cameras"]}
place_of = {cam["camera"]: float(cam["offset"])
            for cam in written["cameras"]}
rate_of = {cam["camera"]: float(cam["fps"]) for cam in written["cameras"]}

print("The two name spaces")
# Where every track name is its camera's name the check below is true
# whatever either side does, so the material is asked first.
check("the two name spaces really differ here",
      sorted(track_of) != sorted(track_of.values()),
      "cameras %s against tracks %s"
      % (sorted(track_of), sorted(track_of.values())))
for_player = vpm.camera_offset(written["cameras"], written["start_s"],
                               written["fps_measured"])
check("the player has a place for every camera Resolve is given",
      sorted(for_player) == sorted(track_of.values()),
      "the player answers to %s, the handover names the tracks %s"
      % (sorted(for_player), sorted(track_of.values())))


def build(handover):
    """Run the Resolve build over *handover* and hand back what landed.

    Keyed by the camera the clip belongs to, with the position in that
    camera's own file in seconds -- which is the number the player
    works out its own way.
    """
    pool = FakePool()
    clips = {cam["file"]: FakeClip(cam["camera"])
             for cam in handover["cameras"]}
    with contextlib.redirect_stdout(io.StringIO()):
        vpm.build_cut_timeline(pool, FakeTimeline(pool), handover["cut"],
                               handover["cameras"], clips, handover)
    out = {}
    for x in pool.sent:
        if x.get("mediaType") != 1:
            continue
        cam = next(c for c in handover["cameras"]
                   if c["file"] == x["mediaPoolItem"].name
                   or c["camera"] == x["mediaPoolItem"].name)
        out[cam["camera"]] = float(x["startFrame"]) / float(cam["fps"])
    return out


print("\nOne shot per camera, walked both ways")
in_resolve = build(written)
# Which camera a shot landed on is not a detail here: where the build
# refuses a shot it puts another camera in its place without a word,
# and the two numbers compared below would then belong to two cameras.
check("every shot landed on the camera the cut names",
      sorted(in_resolve) == sorted(n for _a, _b, n in CUT),
      "the build placed shots on %s, the cut names %s"
      % (sorted(in_resolve), sorted(n for _a, _b, n in CUT)))


def both_ways(camera, at):
    """The place in that camera's file, worked out each way."""
    player = at - for_player.get(track_of[camera], 1e9)
    return player, in_resolve.get(camera)


player_wide, resolve_wide = both_ways("WideCam", 40.0)
check("the wide shot sits in the same place in the player and in Resolve",
      resolve_wide is not None and abs(player_wide - resolve_wide) <= a_frame,
      "the player says %.4f s into the file, Resolve %s"
      % (player_wide, "nothing" if resolve_wide is None
         else "%.4f s" % resolve_wide))
player_mod, resolve_mod = both_ways("PresenterCam", 70.0)
check("and so does the presenters' camera, whose track carries a name "
      "of its own",
      resolve_mod is not None and abs(player_mod - resolve_mod) <= a_frame,
      "the player says %.4f s into the file, Resolve %s"
      % (player_mod, "nothing" if resolve_mod is None
         else "%.4f s" % resolve_mod))
player_guest, resolve_guest = both_ways("GuestCam", 100.0)
check("and so does the guest's camera, the furthest from the axis",
      resolve_guest is not None
      and abs(player_guest - resolve_guest) <= a_frame,
      "the player says %.4f s into the file, Resolve %s"
      % (player_guest, "nothing" if resolve_guest is None
         else "%.4f s" % resolve_guest))

print("\nA camera running slower than the Timeline")
# startFrame is counted in the camera's own frames and the player works
# in seconds, so as long as every rate is the Timeline's rate the two
# can be wrong in the same way and still agree. 24 in a 30 Timeline.
OWN_FPS = 24.0
slower = json.loads(json.dumps(written))
for cam in slower["cameras"]:
    if cam["camera"] == "GuestCam":
        cam["fps"] = OWN_FPS
check("the Timeline keeps its rate while a camera on it runs slower",
      abs(float(slower["fps_measured"]) - FPS) < 1e-6
      and abs(rate_of["GuestCam"] - FPS) < 1e-6,
      "the Timeline runs at %s and the camera was at %.4f before it was "
      "slowed to %.1f"
      % (slower["fps_measured"], rate_of["GuestCam"], OWN_FPS))
slow_resolve = build(slower)
check("a camera at another rate still lands where the player puts it",
      slow_resolve.get("GuestCam") is not None
      and abs(player_guest - slow_resolve["GuestCam"]) <= a_frame,
      "the player says %.4f s into the file, Resolve %s"
      % (player_guest, "nothing" if slow_resolve.get("GuestCam") is None
         else "%.4f s" % slow_resolve["GuestCam"]))

print("\nThe stored place, taken as it stands")
# Which of the three ways found a camera's place was settled when the
# handover was written, and working it out again here is how the player
# and Resolve came apart. The clocks in this material say 0.0, 4.0 and
# 17.4 against the axis; the stored places say something else entirely,
# so a route that went back to the clocks cannot pass this.
stored = {track_of[name]: round(m, 4) for name, _tc, m in NIGHT}
check("the player takes the stored place as it stands, whatever the "
      "clocks say",
      for_player == stored,
      "the player says %s, the handover stored %s, the clocks would give %s"
      % (for_player, stored,
         {track_of[n]: round(tc - ZERO, 4) for n, tc, _m in NIGHT}))

print("\nThe other shape: a preview that has no places yet")
# The preview built from the speaker statistics carries no offset at
# all, only each camera's own start time. Then the origin is where
# programme time begins, and without one the earliest camera.
raw = [{"track": "WideCam", "start_s": 68100.0},
       {"track": "Presenter", "start_s": 68104.0},
       {"track": "Guest", "start_s": 68117.4}]
WANT = {"WideCam": 0.0, "Presenter": 4.0, "Guest": 17.4}


def apart(got):
    """How far the worst of the three answers is from what it should be."""
    if sorted(got) != sorted(WANT):
        return 1e9
    return max(abs(got[k] - WANT[k]) for k in WANT)


told = vpm.camera_offset(raw, ZERO, FPS)
check("with no places stored, the cameras' own start times are used",
      apart(told) <= a_frame,
      "%s against the 0.0, 4.0 and 17.4 the start times give -- %.4f s "
      "out at the worst" % (told, apart(told)))
guessed = vpm.camera_offset(raw, None, FPS)
check("and with no origin either, the earliest camera is the zero",
      apart(guessed) <= a_frame,
      "%s against the same three, counted from the earliest camera -- "
      "%.4f s out at the worst" % (guessed, apart(guessed)))

print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
