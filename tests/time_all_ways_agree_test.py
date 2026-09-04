# -*- coding: utf-8 -*-
"""One moment, and every way to it has to land on the same second.

Three clocks run through this program and none of them says its name:

  programme time   zero is start_s of the handover file
  file time        zero is the start of that camera's file; the bridge
                   is offset -- "position in the file is programme time
                   minus this"
  window time      zero is the In point

No consumer writes down which clock it is standing in, so a repair in
one place can break another without anything looking wrong in between.
So this test checks no number of its own: it takes a moment it knows
the place of and walks it out to a wall clock time every way there is:

    start_s plus programme time                   (handover)
    start_tc plus programme time                  (handover, the other field)
    the cut entry that begins there               (cut list)
    the entry in _cameracut.edl                   (Resolve, as an EDL)
    the row in _cameracut.csv                     (the same, as a table)
    the row in _speakers.csv / .edl               (speech moments)
    the camera's own timecode plus (t - offset)   (file time, stored offset)
    the same with camera_offset()                 (file time, the player)
    recordFrame / fps out of build_cut_timeline   (Resolve, on the timeline)
    the camera timecode plus its startFrame       (Resolve, into the file)

All have to name the same time within one frame, and how many of them
could be walked at all is a judgement beside that one: a spread says
nothing about a way that gave no answer. Which moments those are is
said first and as a judgement of its own -- a shot on each of the three
cameras, both speakers heard -- because everything below it is counted
per moment, and a cut that quietly lost one would show as a smaller
count and not as a fault. It runs twice, wide open and
with a window set: applied twice a window moves everything under it, an
absolute In point applied again must move nothing more, a relative one
must move by one more In point, and "+0:10:00" must mean ten minutes
from the window start, not eighteen hours.

Then the five files of one run against each other, because where they
part company Resolve gets something other than the preview shows. Then
the cut cut_statistics() computes again, against the written one, and
with it the two name spaces: the cut list names a camera by the
camera's name, the player by the track name, and they agree only where
no camera carries a speaker.

After that the cases the material of a single ordinary run cannot
make, each one a place where two numbers that are one number here are
two everywhere else: a camera running slower than the Timeline, where
the frames of the file and the frames of the Timeline part company; a
measurement and a clock saying different things, where which of the
two placed a camera can be seen at all -- in every run above they
agree, and they have to, or no two ways could land on one instant;
one file whose path is written two ways, where a handover comparing
raw strings loses the measurement and puts the camera at the start of
the axis; and a rate
whose timecode counts faster than the pictures run, where the frame a
timecode names and the frame a second is are not the same frame. Last
the whole set once more at a second frame rate, read back the way a
stranger reads it -- from the handover alone, the files beside it found
by their stem: everything before that is written at 25 fps, and a frame
rate is where timecode arithmetic goes wrong.

The shared interview fixture carries real timecodes but the same
picture, so one file is checked against the axis, not three aligned.
Every judgement here is reached on every machine, and every one stands
on material the test writes itself: a section only one machine can run
makes the count this test prints mean a different thing on each of
them, and then no floor can hold it.

VPM_ONE_MOMENT_KEEP=1 leaves the written files in place for looking at.
"""
import os, sys, csv, json, re, shutil, subprocess, tempfile, time, types
import the_program

HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = the_program.SCRIPT
sys.path.insert(0, HERE)
from fixture_root import fixture

vpm = the_program.load()

error = []
began = time.time()
# Not "bad": that name is taken further down by the lists of entries
# that did not line up, and a counter under it would end this file in a
# traceback where a verdict should stand.
done = 0


def check(name, ok, extra=""):
    global done
    done += 1
    print("  %-58s %s %s" % (name, "ok" if ok else "FAIL", extra))
    if not ok:
        error.append(name)


# ---------------------------------------------------------------- material
FIX = fixture("interview")
WIDE = os.path.join(FIX, "WideCam_01011855_C001.mov")
MOD = os.path.join(FIX, "PresentersCam_01011855_C002.mov")
KAND = os.path.join(FIX, "GuestCam_01011858_C003.mov")
FPS = 25.0
FRAME = 1.0 / FPS
# What the run measured for itself. A camera stands where it was
# measured, so these are the places every way below has to arrive at.
# They are also what the fixture's own clocks say, and that is not a
# convenience: a run whose measurement disagreed with its clocks is one
# in which the sound really does sit against the wrong picture, and
# then no two ways could agree by any arithmetic. That the clocks say
# exactly this is a judgement of its own further down, so a fixture
# rebuilt to other times says so instead of turning every line here red
# without a reason. Where the two have to be told apart -- which of
# them the run went by -- a section of its own does it, on material
# built so that they disagree.
MEASURED = {WIDE: 0.0, MOD: 4.0, KAND: 17.48}

# Two ways out, and they are not the same news: a machine nobody set
# up, or a fixture that changed under everybody. One line each --
# run.sh lifts only the first SKIPPED line into the summary, so a
# reason spread over two lines arrives there halved.
missing = [os.path.basename(p) for p in (WIDE, MOD, KAND)
           if not os.path.exists(p)]
if missing:
    print("SKIPPED: no interview fixture under %s (%s) -- "
          "run tests/fixtures.sh" % (FIX, ", ".join(missing)))
    # The count on the way out as well: no way out of this file is
    # silent about how much it judged. The SKIPPED line stays the
    # verdict here -- nothing behind it may read as "all good".
    print("\n%d checks in %.2f s" % (done, time.time() - began))
    sys.exit(0)

stamp = {p: vpm.file_timecode(p, FPS) for p in (WIDE, MOD, KAND)}
blank = sorted(os.path.basename(p) for p, v in stamp.items() if v is None)
if blank:
    print("SKIPPED: the interview fixture is there but carries no "
          "timecode on %s, and every clock here is measured from one -- "
          "rebuild %s with tests/fixtures.sh (INTERVIEW_BUILD)"
          % (", ".join(blank), FIX))
    print("\n%d checks in %.2f s" % (done, time.time() - began))
    sys.exit(0)

ZERO = stamp[WIDE]              # the earliest camera is the zero of the axis
# The material's own clocks, held against the places above. Every way
# below walks from one of the two, and a fixture rebuilt to other times
# would part them without anything saying so: the spread reported then
# names no fault of the program's at all.
off_by = {os.path.basename(p): round(stamp[p] - ZERO - MEASURED[p], 4)
          for p in (WIDE, MOD, KAND)}
check("the fixture's clocks are the places this test was written for",
      not [v for v in off_by.values() if abs(v) > FRAME],
      "each camera's clock less the axis, less what this test measures "
      "for it: %s -- rebuild with tests/fixtures.sh" % (off_by,))


def stamp_of(cam):
    """A camera's timecode, asked of the same row the run asks.

    The rendered file first and the source behind it: not every ffmpeg
    carries a timecode track through a render, and asking the rendered
    file alone measures the ffmpeg rather than the program.
    """
    for path in (cam.get("file"), cam.get("source")):
        if not path:
            continue
        got = stamp.get(path)
        if got is None:
            got = vpm.file_timecode(path, FPS)
        if got is not None:
            return got
    return None
LENGTH = 60.0
KEEP = []


def stem_of(p):
    return os.path.splitext(os.path.basename(p))[0]


cameras = [{"video": p, "name": stem_of(p)} for p in (WIDE, MOD, KAND)]
tracks = [{"name": "Presenter", "camera": MOD},
          {"name": "Guest", "camera": KAND}]


def videos_at(rate):
    """The three cameras described at *rate*, and the reference clip.

    write_cut_list and write_handover both take the rate they write at
    from ref_clip[1]["fps"] and from nowhere else, so this is the whole
    of what it takes to ask the same questions at another frame rate.
    """
    tc = vpm.timecode_string(ZERO, rate)
    made = [(p, {"width": 1280, "height": 720, "fps": rate,
                 "duration": 120.0, "tc": tc if p == WIDE else None})
            for p in (WIDE, MOD, KAND)]
    return made, (WIDE, made[0][1])


ref_clip = videos_at(FPS)[1]    # the window's reference, at the usual rate

# The moments this test knows the place of. Chosen so that every shot
# falls inside the time all three cameras are rolling: a shot before
# that has no picture, which is another fault entirely.
SPEECH = [("Presenter", [(22.0, 34.0), (46.0, 58.0)]),
          ("Guest", [(36.0, 44.0)])]


def make_args(name, in_point=None, out_point=None):
    return types.SimpleNamespace(
        production=name, min_edit_duration=1.2, delay=0.3,
        wide_after=0.0, wide_length=5.0, wide_most=15.0, wide_latest=120.0,
        no_wide_edges=True, wide_shot=[WIDE],
        in_point=in_point, out_point=out_point,
        lufs=None, intro=None, outro=None, resolve=False)


# ------------------------------------------------------- reading the files
EDL_ROW = re.compile(r"^(\d{3})\s+\S+\s+\S+\s+\S+\s+"
                     r"(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s*$")


def tc_clock(fps):
    """How many frames a timecode counts to the second at *fps*.

    Thirty at 29.97 and twenty-four at 23.976: a non-drop timecode
    labels the wall clock and counts whole frames under it, so a frame
    number out of one is turned back into seconds with the whole
    number, never with the true rate. Dividing by the true rate is out
    by about a minute per hour, and at 18:55 that is sixty-eight
    seconds -- every reading here would then name a moment no file
    mentions. Rounded here rather than looked up in the program, so the
    two do not agree by being the same call.
    """
    return float(int(round(float(fps))))


def read_edl(path, fps):
    """(start s, end s, clip name) per entry, in file order.

    *fps* has to be the rate the file was written at, or the timecode is
    out by up to a frame per frame number.
    """
    rate = float(fps)

    def at(tc):
        return vpm.timecode_to_frames(tc, rate) / tc_clock(rate)

    out, pending = [], None
    for line in open(path, encoding="utf-8"):
        m = EDL_ROW.match(line)
        if m:
            pending = (at(m.group(2)), at(m.group(3)))
            continue
        if line.startswith("* FROM CLIP NAME:") and pending:
            out.append((pending[0], pending[1], line.split(":", 1)[1].strip()))
            pending = None
    return out


def read_csv(path):
    with open(path, encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


# ----------------------------------------------- the Resolve build, no Resolve
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
        self.start_tc = None

    def SetStartTimecode(self, tc):
        self.start_tc = tc
        return True

    def SetTrackName(self, *a):
        return True

    def GetItemListInTrack(self, kind, i):
        if kind != "video":
            return []
        return [FakeItem(x.get("endFrame", 0) - x.get("startFrame", 0))
                for x in self.pool.sent if x.get("mediaType") == 1]


# ------------------------------------------------------------------- a run
class Run(object):
    """One whole run: the five files it wrote and everything read back."""

    def __init__(self, name, tc_start, speech, length,
                 in_point=None, out_point=None, mix=None, rate=FPS,
                 offsets=None):
        self.name = name
        self.dir = tempfile.mkdtemp(prefix="onemoment_")
        KEEP.append(self.dir)
        self.args = make_args(name, in_point, out_point)
        print("\nTHE RUN %r%s" % (name, (" with In point %s, Out point %s"
                                         % (in_point, out_point))
                                  if in_point or out_point else ""))
        vids, ref = videos_at(rate)
        self.cut, self.segs = vpm.write_cut_list(
            self.args, speech, tracks, cameras, vids, self.dir,
            tc_start, ref, length)
        vpm.write_handover(
            self.args, tracks, cameras, vids, self.dir, tc_start, ref,
            results=[WIDE, MOD, KAND], cut=self.cut, segment_list=self.segs,
            length=length, track_names={}, single_files=dict(mix or {}),
            offsets=dict(MEASURED if offsets is None else offsets),
            words=())
        self.stem = os.path.join(self.dir, vpm.safe_filename(name))
        self.files = {
            "handover": self.stem + "_resolve.json",
            "cameracut.edl": self.stem + "_cameracut.edl",
            "cameracut.csv": self.stem + "_cameracut.csv",
            "speakers.edl": self.stem + "_speakers.edl",
            "speakers.csv": self.stem + "_speakers.csv"}
        gone = [n for n, p in self.files.items() if not os.path.exists(p)]
        if gone:
            error.append("the run %r wrote no %s" % (name, ", ".join(gone)))
            print("\n%d checks in %.2f s" % (done, time.time() - began))
            print("FAIL: " + ", ".join(error))
            sys.exit(1)
        self.d = json.load(open(self.files["handover"], encoding="utf-8"))
        d = self.d
        self.fps = vpm.resolve_timeline_rate(d.get("fps") or FPS)
        self.frame = 1.0 / self.fps
        self.start_s = float(d["start_s"])
        self.by_camera = {c["camera"]: c for c in d["cameras"]}
        self.track_of = {c["camera"]: c["track"] for c in d["cameras"]}
        self.cut_edl = read_edl(self.files["cameracut.edl"], self.fps)
        self.spk_edl = read_edl(self.files["speakers.edl"], self.fps)
        self.cut_csv = read_csv(self.files["cameracut.csv"])
        self.spk_csv = read_csv(self.files["speakers.csv"])
        self.mix = mix
        self._build()
        # What the player would use. The same call the window makes.
        self.player_offset = vpm.camera_offset(
            [c for c in d["cameras"] if c.get("file")], d.get("start_s"),
            max(1.0, float(d.get("fps_measured") or d.get("fps") or FPS)))

    def clock(self, tc):
        """A timecode as seconds since midnight, as the program counts."""
        return vpm.timecode_to_frames(tc, self.fps) / tc_clock(self.fps)

    # -- the Resolve build ------------------------------------------------
    def _build(self):
        d = self.d
        self.pool = FakePool()
        self.timeline = FakeTimeline(self.pool)
        clips = {c["file"]: FakeClip(c["camera"]) for c in d["cameras"]}
        mix_entry = None
        if self.mix:
            path = list(self.mix.values())[0]
            clips[path] = FakeClip("Full-Mix")
            mix_entry = (path, "the stored Full-Mix")
        print("  the Resolve build (no Resolve: a stand-in media pool)")
        vpm.build_cut_timeline(self.pool, self.timeline, d["cut"],
                               d["cameras"], clips, d, mix=mix_entry)
        self.fps_r, self.origin = vpm.timeline_origin(d)
        self.placed = [x for x in self.pool.sent if x.get("mediaType") == 1]
        self.audio = [x for x in self.pool.sent if x.get("mediaType") == 2]
        # Which placed clip belongs to which cut entry: by position while
        # the build took all of them, and where it dropped a shot by the
        # place each landed on, so none is blamed for its neighbour.
        if len(self.placed) == len(d["cut"]):
            self._pairs = list(zip([float(e["start"]) for e in d["cut"]],
                                   self.placed))
        else:
            print("  (the build dropped %d of %d shots -- the rest are"
                  % (len(d["cut"]) - len(self.placed), len(d["cut"])))
            print("   looked for by where they landed, not by their place)")
            self._pairs = sorted(
                (float(x["recordFrame"] - self.origin) / self.fps_r, x)
                for x in self.placed)

    def resolve_at(self, t):
        """The clip the build put at programme time *t*, or nothing."""
        if not self._pairs:
            return None
        got = min(self._pairs, key=lambda p: abs(p[0] - t))
        return got[1] if abs(got[0] - t) <= self.frame * 1.5 else None

    # -- one way each ------------------------------------------------------
    def file_position(self, camera, t, offset):
        """Absolute clock over the camera's file: timecode plus position."""
        cam = self.by_camera.get(camera)
        if cam is None or offset is None:
            return None
        tc = stamp_of(cam)
        if tc is None:
            return None
        return tc + (t - offset)

    def own_rate(self, camera):
        """The rate this camera's own frames are counted at.

        startFrame and endFrame are frames of the file and of nothing
        else, so a way that divides them by the Timeline's rate is right
        only for as long as the two rates are the same number.
        """
        cam = self.by_camera.get(camera)
        return float((cam or {}).get("fps") or self.fps_r)

    def in_file(self, camera, t):
        """Where in this camera's file programme time *t* sits."""
        cam = self.by_camera.get(camera)
        return None if cam is None else t - float(cam["offset"])

    def edl_row_at(self, rows, t_abs, name=None):
        for a, _b, who in rows:
            if abs(a - t_abs) <= self.frame and (name is None or who == name):
                return a
        return None

    def csv_row_at(self, rows, key, t_abs):
        for r in rows:
            if abs(self.clock(r[key]) - t_abs) <= self.frame:
                return self.clock(r[key])
        return None


# ------------------------------------------------------------- the moment
def agree(tag, heading, ways):
    """Every way has to name the same wall clock time, within a frame.

    *ways* is a list of (name, seconds or None). None means the way could
    not be walked at all, which is said rather than passed over -- the
    names that led nowhere come back from here, because the caller is
    where they become a judgement. *tag* is what the failing line says
    where run.sh reads it, so that five failures do not read alike.
    """
    print("\n%s" % heading)
    gone = [n for n, v in ways if v is None]
    have = [(n, v) for n, v in ways if v is not None]
    for n in gone:
        print("      not reachable: %s" % n)
    # The whole spread, not neighbour against neighbour: three ways a
    # frame apart each are two frames apart at the ends. Where fewer
    # than two were reachable there is no spread to measure and the line
    # falls on the count instead -- there used to be a judgement of its
    # own for that, and it could not fall: two of the nine ways below are
    # the same expression written twice, so two of them are always there.
    low = min([v for _n, v in have] or [0.0])
    high = max([v for _n, v in have] or [0.0])
    ok = len(have) >= 2 and (high - low) <= FRAME * 1.001
    # Grouped only for the report, so a divergence names both sides.
    # A single frame apart is rounding, not a disagreement.
    groups = {}
    for n, v in sorted(have, key=lambda x: x[1]):
        near = [k for k in groups if abs(k - v) <= FRAME * 1.001]
        groups.setdefault(near[0] if near else v, []).append((n, v))
    # The line that fails carries its own evidence: a build machine's log
    # keeps only the lines that say FAIL, and numbers left behind on a
    # machine nobody here can run cannot be read.
    check("%s: %d ways, all on one frame" % (tag, len(have)), ok,
          "" if ok else "%.3f s apart, %d different answers: %s"
          % (high - low, len(groups),
             " | ".join("%s = %.3f" % (n, v)
                        for n, v in sorted(have, key=lambda x: x[1]))))
    for key in sorted(groups):
        names = groups[key]
        print("      %s  (%s)"
              % (vpm.timecode_string(names[0][1], FPS),
                 ", ".join("%s = %.3f" % (n, v) for n, v in names)))
    return [(tag, n) for n in gone]


def walk_every_way(r):
    """Take every moment this run knows and walk it out every way."""
    d = r.d
    # One shot start per camera, so a camera with a zero offset cannot
    # hide a sign error on the others.
    seen, moments = set(), []
    for e in d["cut"]:
        if e["camera"] in seen:
            continue
        seen.add(e["camera"])
        moments.append(e)
    heard = [s for s in d["speakers"] if s["sections"]]
    # Before the loops, and as a judgement rather than a comment: how
    # many judgements follow hangs on these two numbers, and a count
    # that quietly moved with the material is exactly what left this
    # test with one number here and another on six builders. Three
    # cameras and two speakers are what the material above sets up, so
    # every run walks the same five moments out.
    check("%s: three cameras in the cut, both speakers heard" % r.name,
          len(moments) == 3 and len(heard) == 2,
          "%d cameras and %d speakers with sections, against 3 and 2"
          % (len(moments), len(heard)))

    # What could not be walked at all is collected and judged once at
    # the end. A way that leads nowhere is not a small disagreement, it
    # is a file with no row for this moment -- and the line above it
    # cannot say so: it measures how far the answers lie apart, and a
    # way that gave no answer is not in that spread. Measured: a zero
    # moved by 125 frames left four of the five files five seconds
    # wrong, and the count of ways fell from nine to seven without a
    # word.
    lost = []

    for e in moments:
        t = float(e["start"])
        camera = e["camera"]
        x = r.resolve_at(t)
        ways = [
            ("handover start_s + t", r.start_s + t),
            ("handover start_tc + t", r.clock(d["start_tc"]) + t),
            ("cut entry", r.start_s + t),
            ("cameracut.edl", r.edl_row_at(r.cut_edl, r.start_s + t)),
            ("cameracut.csv",
             r.csv_row_at(r.cut_csv, "Start TC", r.start_s + t)),
            ("file time, stored offset",
             r.file_position(camera, t, r.by_camera[camera].get("offset"))),
            ("file time, camera_offset()",
             r.file_position(camera, t,
                             r.player_offset.get(r.track_of[camera]))),
            ("Resolve recordFrame",
             None if x is None else float(x["recordFrame"]) / r.fps_r),
            ("Resolve startFrame in the file",
             None if x is None else
             (stamp_of(r.by_camera[camera]) or 0.0)
             + float(x["startFrame"]) / r.own_rate(camera)),
        ]
        lost += agree("%s: the shot on %s at %.3f s" % (r.name, camera, t),
                      "%s: the shot on %s that begins at %.3f s programme "
                      "time" % (r.name, camera, t), ways)

    # And a speech moment, which is where the speaker files can be reached.
    for s in heard:
        name, t = s["name"], float(s["sections"][0][0])
        shot = next((e for e in d["cut"] if e["start"] <= t < e["end"]), None)
        on_screen = shot["camera"] if shot else None
        x = r.resolve_at(float(shot["start"])) if shot else None
        ways = [
            ("handover start_s + t", r.start_s + t),
            ("speakers.edl", r.edl_row_at(r.spk_edl, r.start_s + t, name)),
            ("speakers.csv",
             r.csv_row_at(r.spk_csv, "Start TC", r.start_s + t)),
            ("file time, stored offset",
             r.file_position(on_screen, t,
                             r.by_camera[on_screen].get("offset"))
             if on_screen else None),
            ("file time, camera_offset()",
             r.file_position(on_screen, t,
                             r.player_offset.get(r.track_of[on_screen]))
             if on_screen else None),
            ("Resolve recordFrame of that shot",
             None if x is None else
             (float(x["recordFrame"]) / r.fps_r) + (t - float(shot["start"]))),
        ]
        lost += agree("%s: %s starts speaking at %.3f s" % (r.name, name, t),
                      "%s: %s starts speaking at %.3f s programme time "
                      "-- on %s" % (r.name, name, t, on_screen), ways)

    check("every way to every one of those moments could be walked",
          not lost, "%d of them led nowhere: %s"
          % (len(lost), "; ".join("%s -- %s" % p for p in lost[:3])))

    print("\n  THE BRIDGE BETWEEN THE AXES")
    # Written out one camera at a time rather than looped: a name put
    # together out of the camera makes one line in state/counterproof
    # stand for three judgements, and that row cannot say which of the
    # three was ever seen red.

    def bridge(camera):
        """(the clock against the axis, the stored place, the player's)."""
        c = r.by_camera.get(camera)
        if c is None:
            return None, None, None
        got = stamp_of(c)
        return (None if got is None else got - r.start_s,
                float(c["offset"]), r.player_offset.get(c["track"]))

    def one_instant(a, b):
        return a is not None and b is not None and abs(a - b) <= r.frame

    clock, stored, played = bridge(stem_of(WIDE))
    check("  the wide shot's clock and its stored place are one instant",
          one_instant(clock, stored),
          "%s: the clock sits %s s from the axis, the handover says %s"
          % (r.name, clock, stored))
    check("  and the player puts the wide shot in that same place",
          one_instant(played, stored),
          "%s: the player says %s, the handover %s"
          % (r.name, played, stored))
    clock, stored, played = bridge(stem_of(MOD))
    check("  the presenters' clock and its stored place are one instant",
          one_instant(clock, stored),
          "%s: the clock sits %s s from the axis, the handover says %s"
          % (r.name, clock, stored))
    check("  and the player puts the presenters' camera in that place",
          one_instant(played, stored),
          "%s: the player says %s, the handover %s"
          % (r.name, played, stored))
    clock, stored, played = bridge(stem_of(KAND))
    check("  the guest's clock and its stored place are one instant",
          one_instant(clock, stored),
          "%s: the clock sits %s s from the axis, the handover says %s"
          % (r.name, clock, stored))
    check("  and the player puts the guest's camera in that place",
          one_instant(played, stored),
          "%s: the player says %s, the handover %s"
          % (r.name, played, stored))


def five_files(r):
    """The five files of one run, held against each other."""
    d = r.d
    check("cameracut.edl has one entry per cut entry",
          len(r.cut_edl) == len(d["cut"]),
          "%d vs %d" % (len(r.cut_edl), len(d["cut"])))
    bad = [(i, a, r.start_s + e["start"])
           for i, ((a, _b, _n), e) in enumerate(zip(r.cut_edl, d["cut"]))
           if abs(a - (r.start_s + e["start"])) > r.frame]
    check("every cameracut.edl entry begins where the cut does", not bad,
          "" if not bad else "entry %d: %.3f vs %.3f" % bad[0])
    bad = [(i, b, r.start_s + e["end"])
           for i, ((_a, b, _n), e) in enumerate(zip(r.cut_edl, d["cut"]))
           if abs(b - (r.start_s + e["end"])) > r.frame]
    check("and ends where the cut does", not bad,
          "" if not bad else "entry %d: %.3f vs %.3f" % bad[0])

    # The CSV is the finer of the two: it splits a shot where the speaker
    # changes inside it, so the camera changes line up, not the rows.
    edges = []
    for row in r.cut_csv:
        if not edges or edges[-1][2] != row["Camera"]:
            edges.append([r.clock(row["Start TC"]), r.clock(row["End TC"]),
                          row["Camera"]])
        else:
            edges[-1][1] = r.clock(row["End TC"])
    check("cameracut.csv holds at least as many rows as the EDL",
          len(r.cut_csv) >= len(r.cut_edl),
          "%d vs %d" % (len(r.cut_csv), len(r.cut_edl)))
    check("its camera changes are the EDL's entries",
          len(edges) == len(r.cut_edl),
          "%d vs %d" % (len(edges), len(r.cut_edl)))
    bad = [(i, e[0], a) for i, (e, (a, _b, _n))
           in enumerate(zip(edges, r.cut_edl)) if abs(e[0] - a) > r.frame]
    check("and they begin at the same time", not bad,
          "" if not bad else "change %d: %.3f vs %.3f" % bad[0])
    holes = [(i, edges[i][1], edges[i + 1][0]) for i in range(len(edges) - 1)
             if abs(edges[i][1] - edges[i + 1][0]) > r.frame]
    check("no gap and no overlap between the shots", not holes,
          "" if not holes else "after shot %d: %.3f then %.3f" % holes[0])

    # The speaker side. Sorted the same way the writer sorts them.
    lines = sorted((a, b, s["name"]) for s in d["speakers"]
                   for a, b in s["sections"])
    check("speakers.edl has one entry per speech section",
          len(r.spk_edl) == len(lines),
          "%d vs %d" % (len(r.spk_edl), len(lines)))
    check("speakers.csv has one row per speech section",
          len(r.spk_csv) == len(lines),
          "%d vs %d" % (len(r.spk_csv), len(lines)))
    bad = [(i, a, r.start_s + s[0]) for i, ((a, _b, _n), s)
           in enumerate(zip(r.spk_edl, lines))
           if abs(a - (r.start_s + s[0])) > r.frame]
    check("every speakers.edl entry sits where the handover says", not bad,
          "" if not bad else "entry %d: %.3f vs %.3f" % bad[0])
    bad = [(i, r.clock(row["Start TC"]), a) for i, (row, (a, _b, _n))
           in enumerate(zip(r.spk_csv, r.spk_edl))
           if abs(r.clock(row["Start TC"]) - a) > r.frame]
    check("speakers.csv and speakers.edl say the same times", not bad,
          "" if not bad else "row %d: %.3f vs %.3f" % bad[0])
    bad = [(i, row["Speaker"], n) for i, (row, (_a, _b, n))
           in enumerate(zip(r.spk_csv, r.spk_edl)) if row["Speaker"] != n]
    check("and the same names", not bad,
          "" if not bad else "row %d: %r vs %r" % bad[0])
    # "Time from start" is the window column: it counts from the axis and
    # not from midnight, the one place the two clocks meet in a file.
    bad = []
    for row in r.spk_csv:
        h, m, s = row["Time from start"].split(":")
        from_start = int(h) * 3600 + int(m) * 60 + float(s)
        if abs((r.clock(row["Start TC"]) - r.start_s) - from_start) > r.frame:
            bad.append((row["Speaker"],
                        r.clock(row["Start TC"]) - r.start_s, from_start))
    check("speakers.csv: 'Time from start' is the TC minus start_s", not bad,
          "" if not bad else "%s: %.3f vs %.3f" % bad[0])

    check("the cut runs to the length the handover states",
          abs(r.cut_edl[-1][1] - (r.start_s + float(d["length_s"])))
          <= r.frame,
          "%.3f vs %.3f" % (r.cut_edl[-1][1],
                            r.start_s + float(d["length_s"])))
    check("the cut begins at start_s",
          abs(r.cut_edl[0][0] - r.start_s) <= r.frame,
          "%.3f vs %.3f" % (r.cut_edl[0][0], r.start_s))
    # The empty list has an answer here too: a build that placed nothing
    # is a fault this line has to report, not one it may die on. max()
    # over nothing throws, and the traceback would end the file before
    # the counting line and take every judgement after it with it.
    last = max([x["recordFrame"] + (x["endFrame"] - x["startFrame"])
                for x in r.placed] or [0])
    check("the Resolve timeline ends where the EDL ends",
          abs(float(last) / r.fps_r - r.cut_edl[-1][1]) <= r.frame,
          "%.3f vs %.3f" % (float(last) / r.fps_r, r.cut_edl[-1][1]))
    check("the Timeline was given the handover's own start timecode",
          r.timeline.start_tc == d["start_tc"],
          "%r vs %r" % (r.timeline.start_tc, d["start_tc"]))
    # The paper and the Timeline on the same frame, and asked as frames:
    # everything above allows a frame either way, because a second read
    # off a timecode and a second computed from the axis are rounded in
    # different places. Between these two there is nothing to round --
    # the EDL is written as a frame number and Resolve is handed one --
    # so a whole frame between them is a disagreement and not the
    # method. It is where a rounding put in one of the two and not in
    # the other shows up, and that difference is exactly one frame.
    clock = tc_clock(r.fps)
    apart = [(i, int(round(a * clock)), x["recordFrame"])
             for i, ((a, _b, _n), x) in enumerate(zip(r.cut_edl, r.placed))
             if int(round(a * clock)) != x["recordFrame"]]
    check("every cameracut.edl entry names the frame Resolve is handed",
          not apart and len(r.cut_edl) == len(r.placed),
          "%d entries against %d clips%s"
          % (len(r.cut_edl), len(r.placed),
             "" if not apart else "; entry %d on frame %d, its clip on %d"
             % apart[0]))


def preview_cut(r):
    """The cut the window computes again, against the one on disk."""
    d = r.d
    numbers = vpm.cut_statistics(
        d, min_len=r.args.min_edit_duration, delay=r.args.delay,
        after=r.args.wide_after, holds=r.args.wide_length,
        at_latest=r.args.wide_latest, edge=not r.args.no_wide_edges,
        rules=vpm.rules_from_settings(r.args))
    if not numbers:
        check("cut_statistics returned a cut", False, "it returned nothing")
        return
    again = numbers["cut"]
    check("the preview finds the same number of shots",
          len(again) == len(d["cut"]),
          "%d vs %d" % (len(again), len(d["cut"])))
    bad = [(i, a, e["start"]) for i, ((a, _b, _w), e)
           in enumerate(zip(again, d["cut"])) if abs(a - e["start"]) > r.frame]
    check("at the same times", not bad,
          "" if not bad else "shot %d: %.3f vs %.3f" % bad[0])
    bad = [(i, w, r.track_of.get(e["camera"])) for i, ((_a, _b, w), e)
           in enumerate(zip(again, d["cut"]))
           if w != r.track_of.get(e["camera"])]
    check("and on the same cameras, through the camera-to-track map", not bad,
          "" if not bad else "shot %d: %r vs %r" % bad[0])


# ============================================================== run one
print("=" * 66)
print("THE WINDOW WIDE OPEN")
print("=" * 66)
open_run = Run("Onemoment", ZERO, SPEECH, LENGTH)
# Everything below looks a camera up in this dict by its track name, so
# it is asked here and not among the two name spaces further down: a
# key missing there kills the run before the judgement is reached.
# And asked as "every track is a key", not as "these keys and no
# others": the player, the band and audio_for_cut all read the dict
# with .get(track) and never over its keys, so an extra key under the
# camera's name breaks nothing -- and the earlier form of this check
# went red on exactly that harmless addition.
no_key = sorted({c["track"] for c in open_run.d["cameras"]}
                - set(open_run.player_offset))
check("camera_offset() answers to every track name", not no_key,
      "%d of %d tracks have no key: %s -- the keys are %s"
      % (len(no_key), len(open_run.d["cameras"]), no_key,
         sorted(open_run.player_offset)))

print("\n" + "=" * 66)
print("A KNOWN MOMENT, WALKED OUT EVERY WAY")
print("=" * 66)
walk_every_way(open_run)

print("\n" + "=" * 66)
print("THE FIVE FILES OF ONE RUN, HELD AGAINST EACH OTHER")
print("=" * 66)
five_files(open_run)

print("\n" + "=" * 66)
print("THE PREVIEW'S OWN CUT AGAINST THE WRITTEN ONE")
print("=" * 66)
preview_cut(open_run)

# ============================================== the third clock: the window
print("\n" + "=" * 66)
print("THE WINDOW: WHAT THE FOUR NOTATIONS MEAN")
print("=" * 66)
# Read the sign after counting the colons and "+0:10:00" becomes
# eighteen hours, so the four notations are read one by one first.
for text, want_value, want_absolute in [
        ("+0:10:00", 600.0, False),
        ("0:10:00", 600.0, True),         # no sign: a wall clock time
        ("-0:05:00", -300.0, False),
        ("90", 90.0, False)]:
    value, absolute = vpm.parse_time_point(text, FPS)
    check("  %-10r means %+.1f s, %s" % (
              text, want_value,
              "a wall clock time" if want_absolute else "from the window"),
          value is not None and abs(value - want_value) < 1e-6
          and absolute is want_absolute,
          "got %s, absolute=%s" % (value, absolute))

# And the same four through the run's own converter, which is what turns
# them into a window on the reference camera.
for text, out_text, want0, want1 in [
        ("+0:00:10", "-0:00:05", 10.0, 55.0),
        (vpm.timecode_string(ZERO + 10.0, FPS), "", 10.0, LENGTH),
        ("", "-0:00:05", 0.0, 55.0)]:
    got0, got1 = vpm.clip_to_time_window(
        make_args("x", text or None, out_text or None), 0.0, LENGTH, ref_clip)
    check("  clip_to_time_window(%r, %r) -> %.1f .. %.1f"
          % (text, out_text, want0, want1),
          got0 is not None and abs(got0 - want0) < 1e-6
          and abs(got1 - want1) < 1e-6, "got %s .. %s" % (got0, got1))

print("\n" + "=" * 66)
print("THE SAME RUN AGAIN, WITH A WINDOW SET")
print("=" * 66)
IN_TEXT, OUT_TEXT = "+0:00:10", "-0:00:05"
NEW0, NEW1 = vpm.clip_to_time_window(
    make_args("x", IN_TEXT, OUT_TEXT), 0.0, LENGTH, ref_clip)
if NEW0 is None or NEW1 is None:
    # Without a window there is no windowed run, and going on would end
    # in a stack trace with no summing-up line for run.sh to show.
    check("the window %r .. %r can be read at all" % (IN_TEXT, OUT_TEXT),
          False, "clip_to_time_window returned nothing")
    print("\n%d checks in %.2f s" % (done, time.time() - began))
    print("FAIL: " + ", ".join(error))
    sys.exit(1)
# The run measures the speech on the trimmed material, so the sections
# count from the In point. The same real moments, on the new axis.
WINDOW_SPEECH = [(n, [(max(0.0, a - NEW0), min(NEW1 - NEW0, b - NEW0))
                      for a, b in segs if b > NEW0 and a < NEW1])
                 for n, segs in SPEECH]
# The measurement moves with the window. A run measures on the trimmed
# material, so what it finds is one In point smaller than what the open
# run found: the camera's picture has not moved, the axis under it has.
# Handing the open run's numbers to the windowed one would be handing
# it a measurement of material it never saw.
win_run = Run("Onemomentwin", ZERO + NEW0, WINDOW_SPEECH, NEW1 - NEW0,
              in_point=IN_TEXT, out_point=OUT_TEXT,
              offsets={p: m - NEW0 for p, m in MEASURED.items()})

print("\n" + "=" * 66)
print("THE SAME MOMENTS AGAIN, WITH THE WINDOW SET")
print("=" * 66)
walk_every_way(win_run)

print("\n" + "=" * 66)
print("THE FIVE FILES OF THE WINDOWED RUN")
print("=" * 66)
five_files(win_run)
preview_cut(win_run)

print("\n" + "=" * 66)
print("THE WINDOW MOVES NOTHING AGAINST ANYTHING ELSE")
print("=" * 66)
# A window makes something fall away, it does not make things slide. So
# one real moment is asked of both runs: the two answers must be the
# same, or sound runs against the wrong picture.
# Both of these used to hold one run against the other -- the windowed
# start_s less the open one, the windowed length less the open one --
# and everything the program got equally wrong in both runs cancelled
# out. Measured: a constant half second added in write_handover turned
# 44 judgements here red and left these two green. So they are held
# against numbers of this file's own: the timecode the fixture carries
# and the window that was asked for.
check("the window moved the axis by the In point",
      abs(win_run.start_s - (ZERO + NEW0)) <= FRAME,
      "%.3f vs %.3f" % (win_run.start_s, ZERO + NEW0))
check("and shortened the material by the head and the tail",
      abs(float(win_run.d["length_s"]) - (NEW1 - NEW0)) <= FRAME,
      "%.3f vs %.3f" % (win_run.d["length_s"], NEW1 - NEW0))
for real in (ZERO + 22.0, ZERO + 36.0, ZERO + 50.0):
    for camera in open_run.by_camera:
        was = open_run.in_file(camera, real - open_run.start_s)
        now = win_run.in_file(camera, real - win_run.start_s)
        check("  %s sits in the same place in %s"
              % (vpm.timecode_string(real, FPS), camera.split("_")[0]),
              was is not None and now is not None and abs(was - now) <= FRAME,
              "%.4f vs %.4f" % (was or -1, now or -1))
    # And the same for the player's own numbers, which do not come from
    # the stored offset at all but off the timecode.
    for camera, track in open_run.track_of.items():
        was = (real - open_run.start_s) - open_run.player_offset[track]
        now = (real - win_run.start_s) - win_run.player_offset[track]
        check("  the player puts it in the same place on %s"
              % camera.split("_")[0], abs(was - now) <= FRAME,
              "%.4f vs %.4f" % (was, now))

print("\n" + "=" * 66)
print("APPLYING THE WINDOW A SECOND TIME")
print("=" * 66)
# A window applied twice moves every section by double. An absolute In
# point cannot: after the first application start_s IS the In point. A
# relative one promises "from where the window now starts" and moves
# once more, never twice. Both are held.
base = json.load(open(open_run.files["handover"], encoding="utf-8"))


def section_starts(x):
    return [round(a, 3) for s in x["speakers"] for a, _b in s["sections"]]


ABS_IN = vpm.timecode_string(ZERO + 10.0, FPS)
once, c1 = vpm.apply_time_window(base, ABS_IN, "")
twice, c2 = vpm.apply_time_window(once, ABS_IN, "")
check("an absolute In point is read without complaint", not (c1 or c2),
      "%r %r" % (c1, c2))
check("an absolute In point moved the axis by ten seconds",
      abs((float(once["start_s"]) - float(base["start_s"])) - 10.0) <= FRAME,
      "%.3f" % (float(once["start_s"]) - float(base["start_s"])))
# By ten seconds, once: applied twice a window leaves start_s right and
# moves everything under it double, so asking only whether the second
# application changes anything sees nothing wrong.
want = [round(a - 10.0, 3) for a in section_starts(base) if a >= 10.0]
check("every speech section moved by the In point, once",
      section_starts(once) == want,
      "%s vs %s" % (section_starts(once)[:4], want[:4]))
check("every camera offset moved by the In point, once",
      [c.get("offset") for c in once["cameras"]]
      == [round(float(c["offset"]) - 10.0, 4) for c in base["cameras"]],
      "%s vs %s" % ([c.get("offset") for c in once["cameras"]],
                    [round(float(c["offset"]) - 10.0, 4)
                     for c in base["cameras"]]))
check("and the material is ten seconds shorter",
      abs((float(base["length_s"]) - float(once["length_s"])) - 10.0)
      <= FRAME,
      "%.3f" % (float(base["length_s"]) - float(once["length_s"])))
check("applying it a second time moves the axis no further",
      abs(float(twice["start_s"]) - float(once["start_s"])) <= FRAME,
      "%.3f vs %.3f" % (twice["start_s"], once["start_s"]))
check("and moves no speech section",
      section_starts(twice) == section_starts(once),
      "%s vs %s" % (section_starts(twice)[:3], section_starts(once)[:3]))
check("and moves no camera offset",
      [c.get("offset") for c in twice["cameras"]]
      == [c.get("offset") for c in once["cameras"]],
      "%s vs %s" % ([c.get("offset") for c in twice["cameras"]],
                    [c.get("offset") for c in once["cameras"]]))
# The relative one: one In point further, and never two.
r_once, _ = vpm.apply_time_window(base, "+0:00:10", "")
r_twice, _ = vpm.apply_time_window(r_once, "+0:00:10", "")
step = float(r_twice["start_s"]) - float(r_once["start_s"])
check("a relative In point applied twice moves by one In point, not two",
      abs(step - 10.0) <= FRAME, "%.3f s the second time" % step)
# apply_time_window moves start_s to the In point, and start_tc goes
# with it: Resolve reads start_tc and nothing else, so a handover
# trimmed after it was written used to put every frame the removed head
# out of place. The wide judgement stays beside the narrow one on
# purpose -- it allows either answer and refuses a third, so it holds
# whichever of the two the program settles on, while the one under it
# says which of the two that is today.
head = float(once["start_s"]) - float(base["start_s"])
gap = open_run.clock(once["start_tc"]) - float(once["start_s"])
check("a window puts start_tc where start_s now is, or leaves it at "
      "the untrimmed start -- never a third place",
      abs(gap) <= FRAME or abs(gap + head) <= FRAME,
      "start_tc %s sits %.3f s from start_s %.3f -- %.3f (moved along) "
      "and %.3f (left behind) are the two right answers"
      % (once["start_tc"], gap, float(once["start_s"]), 0.0, -head))
check("and a handover trimmed after it was written names one instant "
      "in both fields, as a run with a window does",
      abs(gap) <= FRAME,
      "start_tc %s sits %.3f s from start_s %.3f, wanted 0.000 -- left "
      "at the untrimmed start it would sit %.3f s away"
      % (once["start_tc"], gap, float(once["start_s"]), -head))
check("the run's own windowed handover has the two agreeing",
      abs(win_run.clock(win_run.d["start_tc"]) - win_run.start_s)
      <= win_run.frame,
      "%.3f vs %.3f" % (win_run.clock(win_run.d["start_tc"]),
                        win_run.start_s))
check("and it wrote down the window it was made with",
      win_run.d.get("in_point") == IN_TEXT
      and win_run.d.get("out_point") == OUT_TEXT,
      "%r %r" % (win_run.d.get("in_point"), win_run.d.get("out_point")))

print("\n" + "=" * 66)
print("THE TWO NAME SPACES FOR ONE CAMERA")
print("=" * 66)
# The cut list, the EDL, the CSV and the Resolve build name a camera by
# cameras[].camera; the player, the band and camera_offset key on
# cameras[].track. They agree only where no camera carries a speaker,
# and a consumer that confuses them drops every shot without a word.
d = open_run.d
names = [c["camera"] for c in d["cameras"]]
track_names = [c["track"] for c in d["cameras"]]
check("every camera name is unique", len(set(names)) == len(names),
      str(names))
check("every track name is unique",
      len(set(track_names)) == len(track_names), str(track_names))
check("the two name spaces really differ here (a camera carries a "
      "speaker)", set(names) != set(track_names),
      "%s vs %s" % (names, track_names))
check("every cut entry names a camera the handover knows",
      all(e["camera"] in open_run.by_camera for e in d["cut"]),
      str(sorted({e["camera"] for e in d["cut"]} - set(names))))
check("no cut entry names a track by mistake",
      not ({e["camera"] for e in d["cut"]} & (set(track_names) - set(names))),
      str({e["camera"] for e in d["cut"]} & set(track_names)))
# That camera_offset keys on tracks and not on camera names is asked
# right after the run is built, above: by the time the two name spaces
# are compared here, a missing key has long since stopped the run.
# files_per_track is built on tracks, and so is the cut cut_statistics
# feeds the player. Fed the handover's own cut instead, nothing matches.
in_cut = {e["camera"] for e in d["cut"]}
lost = in_cut - set(track_names)
check("feeding the handover's cut to the player loses every camera "
      "that carries a speaker", bool(lost),
      "%d of %d cameras would vanish: %s"
      % (len(lost), len(in_cut), sorted(lost)))
check("and what survives is only the camera nobody is assigned to",
      (in_cut - lost) == {c["camera"] for c in d["cameras"]
                          if not c.get("speakers")},
      str(sorted(in_cut - lost)))

print("\n" + "=" * 66)
print("THE FULL-MIX ON THE AXIS")
print("=" * 66)
# The player runs the mix under the cut, and audio_for_cut works its
# offset out as "timecode of the mix minus start_s". It is nested inside
# gui(), so only the ground it stands on can be checked.
MIXDIR = tempfile.mkdtemp(prefix="onemoment_mix_")
KEEP.append(MIXDIR)
MIXFILE = os.path.join(MIXDIR, "final_Full-Mix.wav")
made = subprocess.run(
    ["ffmpeg", "-v", "error", "-f", "lavfi",
     "-i", "sine=frequency=440:duration=%g" % LENGTH,
     "-ar", str(vpm.SR), "-ac", "1",
     # Exactly what the run writes: bext with the axis zero in samples.
     "-write_bext", "1", "-metadata",
     "time_reference=%d" % int(round(ZERO * vpm.SR)),
     "-y", MIXFILE], capture_output=True)
left_out = []
if made.returncode or not os.path.exists(MIXFILE):
    # Not the SKIPPED marker: that counts the whole test as skipped and
    # the suite allows one. Written down instead, and read out at the end.
    said = " ".join(made.stderr.decode("utf-8", "replace").split())
    left_out.append(
        "the Full-Mix on the axis -- this ffmpeg wrote no bext stamp (%s)"
        % (said[:120] or "ffmpeg failed"))
    print("  LEFT OUT: %s" % left_out[-1])
else:
    got = vpm.file_timecode(MIXFILE, FPS)
    check("a mix stamped the way the run stamps it reads back as start_s",
          got is not None and abs(got - ZERO) <= FRAME,
          "%.3f vs %.3f" % (got if got is not None else -1, ZERO))
    check("so its offset against programme time is zero",
          got is not None and abs((got - ZERO) - 0.0) <= FRAME,
          "%.4f" % ((got - ZERO) if got is not None else -1))
    mix_run = Run("Onemomentmix", ZERO, SPEECH, LENGTH,
                  mix={"Full-Mix": MIXFILE})
    check("the handover names the mix",
          mix_run.d.get("audio_files", {}).get("Full-Mix") == MIXFILE,
          str(mix_run.d.get("audio_files")))
    check("the Resolve build put the mix on the timeline",
          len(mix_run.audio) == 1, "%d audio clips" % len(mix_run.audio))
    # Judged whether the mix arrived or not: under an "if" this line
    # disappears exactly when it has something to say, and the count
    # printed at the end then means one thing on a good day and another
    # on a bad one.
    laid = mix_run.audio[0] if mix_run.audio else {}
    at = float(laid.get("recordFrame", -1)) / mix_run.fps_r
    check("and laid it down at start_s, in one piece",
          bool(mix_run.audio) and abs(at - mix_run.start_s) <= mix_run.frame
          and not laid.get("startFrame"),
          "%.3f vs %.3f, startFrame %s"
          % (at, mix_run.start_s, laid.get("startFrame")))

print("\n" + "=" * 66)
print("A CAMERA THAT RUNS AT ANOTHER RATE THAN THE TIMELINE")
print("=" * 66)
# startFrame and endFrame are frames of the camera's file; recordFrame
# is a frame of the Timeline. In every run above the two rates are the
# same number, so all three can be counted at either rate and nothing
# moves -- three ways of being wrong that no material running at one
# rate can show, and that every way walked above therefore walks past.
# So the run's own handover is taken, one camera in it is set to a
# slower rate, and one shot is put on that camera through the same
# build. Its own handover and not a made-up one, because a dict written
# here would be a guess at the shape the program writes. One shot,
# because a second would begin where the first stopped short of its
# place, and that carry is a different claim from this one.
#
# 24 in a 25 Timeline, and not the wide shot: the wide shot stands in
# for every camera that cannot cover a moment, so a shot refused there
# is silently taken by nobody. This camera's timecode holds no frames
# (18:55:04:00), so read at 24 it names the same instant as read at 25
# -- with the twelve frames the guest's camera carries it would not,
# and the section would be measuring the test's own arithmetic.
OWN_FPS = 24.0
SLOWER = stem_of(MOD)
foreign = json.loads(json.dumps(open_run.d))
for c in foreign["cameras"]:
    if c["camera"] == SLOWER:
        c["fps"] = OWN_FPS
foreign["cut"] = [{"start": 10.0, "end": 30.0, "camera": SLOWER}]
f_pool = FakePool()
vpm.build_cut_timeline(f_pool, FakeTimeline(f_pool), foreign["cut"],
                       foreign["cameras"],
                       {c["file"]: FakeClip(c["camera"])
                        for c in foreign["cameras"]}, foreign)
f_placed = [x for x in f_pool.sent if x.get("mediaType") == 1]
f_fps, f_origin = vpm.timeline_origin(foreign)
f_cam = next(c for c in foreign["cameras"] if c["camera"] == SLOWER)
# Both halves of the setup, as judgements: everything under them is a
# statement about two rates, and if the two ever became one number
# again the four lines below would go on passing and prove nothing.
check("the Timeline keeps its rate while a camera on it runs slower",
      abs(f_fps - FPS) < 1e-6 and abs(float(f_cam["fps"]) - OWN_FPS) < 1e-6,
      "Timeline %g fps, camera %g fps, and they must differ"
      % (f_fps, f_cam["fps"]))
check("and that camera came in four seconds after the axis begins",
      abs(float(f_cam["offset"]) - 4.0) <= FRAME,
      "offset %.4f s, against the 4.0 the material sets up"
      % float(f_cam["offset"]))
check("the one shot on it reached the Timeline", len(f_placed) == 1,
      "%d clips placed, against 1" % len(f_placed))
# Nothing conditional under that: a section that judges four times here
# and once there makes the count this test prints mean two things.
f_shot = f_placed[0] if f_placed else {"startFrame": -1, "endFrame": -1,
                                       "recordFrame": -1}
# 10.0 s into the programme, less the 4.0 s this camera was not yet
# running, is 6.0 s into its file -- at 24 that is frame 144. Counted at
# the Timeline's rate it would be 150, and the shot would show a quarter
# of a second of the wrong moment.
check("the shot begins on the file's own frame, counted at the "
      "camera's rate", f_shot["startFrame"] == 144,
      "startFrame %d, against 144 -- at the Timeline's rate it is 150"
      % f_shot["startFrame"])
# The shot is 20.0 s long: 500 frames of the Timeline, 480 of the
# camera. Counted at the Timeline's rate it would take 500 of the
# camera's frames and run a second past the shot after it.
check("and is as long as the cut says, counted at the camera's rate",
      f_shot["endFrame"] - f_shot["startFrame"] == 480,
      "%d frames long, against 480 -- at the Timeline's rate it is 500"
      % (f_shot["endFrame"] - f_shot["startFrame"]))
# Where it sits is the Timeline's business and nobody else's: 10.0 s
# after frame zero, and at 25 that is 250 frames.
check("and sits on the Timeline where the cut puts it, counted at the "
      "Timeline's rate", f_shot["recordFrame"] - f_origin == 250,
      "%d frames after frame zero, against 250"
      % (f_shot["recordFrame"] - f_origin))

print("\n" + "=" * 66)
print("WHICH OF THE TWO PUT A CAMERA WHERE IT IS")
print("=" * 66)
# A camera stands where it was measured, and its clock is what is left
# where nothing was. Every run above is built so the two say the same
# thing -- they have to, or no two ways to a moment could land on one
# instant -- and that is exactly the material in which "the measurement
# decided" and "the clock decided" cannot be told apart. So three short
# handovers here, each one written from a material in which the two
# disagree, and each read for the place, for the word the file carries
# saying who put it there, and for what the run kept beside it.
#
# Three shifts apart from each other and from anything the clocks could
# give back (0.0, 4.0 and 17.48 against the axis), so a measurement
# that never arrived cannot pass for one that did.
ODD = {WIDE: 7.5, MOD: -3.25, KAND: 11.0}


def handover_from(name, tc_start, offsets):
    """Write one handover and read it back. No judgement here."""
    folder = tempfile.mkdtemp(prefix="onemoment_who_")
    KEEP.append(folder)
    vpm.write_handover(
        make_args(name), tracks, cameras, videos_at(FPS)[0], folder,
        tc_start, ref_clip, results=[WIDE, MOD, KAND], cut=open_run.cut,
        segment_list=open_run.segs, length=LENGTH, track_names={},
        single_files={}, offsets=dict(offsets), words=())
    path = os.path.join(folder, vpm.safe_filename(name) + "_resolve.json")
    got = (json.load(open(path, encoding="utf-8"))
           if os.path.exists(path) else {"cameras": []})
    return path, got


def off_from(written, want):
    """The cameras whose offset is not *want*, as (name, got, wanted)."""
    return [(c["camera"], float(c["offset"]), want.get(c["camera"]))
            for c in written["cameras"]
            if abs(float(c["offset"]) - want.get(c["camera"], 1e9)) > FRAME]


ODDFILE, odd_d = handover_from("Onemomentodd", ZERO, ODD)
want = {stem_of(p): v for p, v in ODD.items()}
bad = off_from(odd_d, want)
check("where the measurement and the clock disagree, the measurement "
      "is the place", not bad and len(odd_d["cameras"]) == 3,
      "%d cameras of 3%s" % (len(odd_d["cameras"]), "" if not bad else
                             "; %s: offset %.4f, measured %.4f" % bad[0]))
# And the file says so out loud, so that anybody asking afterwards why
# a camera sits where it does is not left to guess between the two.
wrong_word = [(c["camera"], c.get("placed_by")) for c in odd_d["cameras"]
              if c.get("placed_by") != "measured"]
check("and every camera says the measurement is what placed it",
      not wrong_word and len(odd_d["cameras"]) == 3,
      "%d cameras of 3%s" % (len(odd_d["cameras"]), "" if not wrong_word
                             else "; %s says %r" % wrong_word[0]))

# Nothing measured at all: then the clock is all there is, and a camera
# put there is one nobody checked -- so the word has to say "clock" and
# no shift may be claimed beside it. A 0.0 there reads exactly like a
# camera the alignment found on the axis.
NOTHINGFILE, none_d = handover_from("Onemomentnone", ZERO, {})
by_clock = {stem_of(p): stamp[p] - ZERO for p in (WIDE, MOD, KAND)}
bad = off_from(none_d, by_clock)
check("with nothing measured, every camera stands where its clock says",
      not bad and len(none_d["cameras"]) == 3,
      "%d cameras of 3%s" % (len(none_d["cameras"]), "" if not bad else
                             "; %s: offset %.4f, the clock says %.4f"
                             % bad[0]))
wrong_word = [(c["camera"], c.get("placed_by")) for c in none_d["cameras"]
              if c.get("placed_by") != "clock"]
check("and every camera says the clock is what placed it",
      not wrong_word and len(none_d["cameras"]) == 3,
      "%d cameras of 3%s" % (len(none_d["cameras"]), "" if not wrong_word
                             else "; %s says %r" % wrong_word[0]))
claimed = [(c["camera"], c.get("sound_against_picture"))
           for c in none_d["cameras"]
           if c.get("sound_against_picture") is not None]
check("and none of them claims a shift against the picture",
      not claimed and len(none_d["cameras"]) == 3,
      "%d cameras of 3%s" % (len(none_d["cameras"]), "" if not claimed
                             else "; %s carries %r" % claimed[0]))

# And with no zero point there is no axis to read a clock against, so
# the measurement is the whole of the answer. The alternative is not
# "roughly right": it is every camera at the start of the axis, sound
# against the wrong picture, and nothing in the file looking wrong.
BLINDFILE, blind_d = handover_from("Onemomentblind", None, ODD)
check("a run with no zero writes a handover all the same",
      os.path.exists(BLINDFILE) and len(blind_d["cameras"]) == 3,
      "%d cameras in %s" % (len(blind_d["cameras"]),
                            os.path.basename(BLINDFILE)))
bad = off_from(blind_d, want)
check("with no zero point to go by, every camera still stands where "
      "the run measured it", not bad and len(blind_d["cameras"]) == 3,
      "%d cameras of 3%s" % (len(blind_d["cameras"]), "" if not bad else
                             "; %s: offset %.4f, measured %.4f" % bad[0]))
# And the measurement travels under a name of its own beside it, so
# nobody downstream reads a place out of it.
bad = [(c["camera"], c.get("sound_against_picture"), want.get(c["camera"]))
       for c in blind_d["cameras"]
       if abs(float(c.get("sound_against_picture") or 1e9)
              - want.get(c["camera"], 0.0)) > 1e-6]
check("and the measurement is handed on under its own name as well",
      not bad and len(blind_d["cameras"]) == 3,
      "%d cameras of 3%s" % (len(blind_d["cameras"]), "" if not bad else
                             "; %s: sound_against_picture %s, measured %.4f"
                             % bad[0]))

print("\n" + "=" * 66)
print("ONE FILE WHOSE PATH IS WRITTEN TWO WAYS")
print("=" * 66)
# What the run measured, how long it delivered and what it called the
# audio tracks are all kept under the file they belong to, and the
# caller writes that path in the shape it reached him in. A folder and
# straight back out again is one shape; a path carrying no drive letter
# is another, and that is the shape a run on Windows hands over.
# Compared as raw strings the two miss each other, and a missed
# measurement is 0.0 -- the camera at the start of the axis with
# seconds measured for it. The row with no timecode again, because
# there the measurement is the whole of the answer.


def other_shape(p):
    """The same file, its folder written by way of a step and back."""
    return os.path.join(os.path.dirname(p), os.curdir, os.path.basename(p))


SHAPEDIR = tempfile.mkdtemp(prefix="onemoment_shape_")
KEEP.append(SHAPEDIR)
# Three values apart from each other and from anything the material
# could give back: the delivered lengths are neither the 120 s the
# files carry nor the 60 s of the run, so a fallback cannot pass for a
# find.
DELIVERED = {WIDE: 41.5, MOD: 42.25, KAND: 43.0}
NAMED = {WIDE: ["Room"], MOD: ["Presenter"], KAND: ["Guest", "Presenter"]}
vpm.write_handover(
    make_args("Onemomentshape"), tracks, cameras, videos_at(FPS)[0],
    SHAPEDIR, None, ref_clip, results=[WIDE, MOD, KAND],
    cut=open_run.cut, segment_list=open_run.segs, length=LENGTH,
    track_names={other_shape(p): n for p, n in NAMED.items()},
    single_files={},
    offsets={other_shape(p): s for p, s in ODD.items()},
    lengths={other_shape(p): s for p, s in DELIVERED.items()}, words=())
SHAPEFILE = os.path.join(
    SHAPEDIR, vpm.safe_filename("Onemomentshape") + "_resolve.json")
shaped = (json.load(open(SHAPEFILE, encoding="utf-8"))
          if os.path.exists(SHAPEFILE) else {"cameras": []})
check("a handover is written from paths in the other shape too",
      os.path.exists(SHAPEFILE) and len(shaped["cameras"]) == 3,
      "%d cameras in %s" % (len(shaped["cameras"]),
                            os.path.basename(SHAPEFILE)))
# The shifts of the section above, not the places the runs use: with
# no zero point a missed measurement writes 0.0, and one camera really
# is measured at 0.0 up there -- so that camera alone could not tell a
# find from a fallback.
want_shift = {stem_of(p): v for p, v in ODD.items()}
bad = [(c["camera"], c["offset"], want_shift.get(c["camera"]))
       for c in shaped["cameras"]
       if abs(float(c["offset"]) - want_shift.get(c["camera"], 1e9)) > FRAME]
check("the measured shift is found however the path was written",
      not bad and len(shaped["cameras"]) == 3,
      "%s: offset %.4f, measured %.4f" % bad[0] if bad
      else "%d cameras of 3" % len(shaped["cameras"]))
want_len = {stem_of(p): v for p, v in DELIVERED.items()}
bad = [(c["camera"], c["duration"], want_len.get(c["camera"]))
       for c in shaped["cameras"]
       if abs(float(c["duration"]) - want_len.get(c["camera"], 1e9)) > 1e-6]
check("and so is the length the run delivered under it",
      not bad and len(shaped["cameras"]) == 3,
      "%s: duration %.3f, delivered %.3f" % bad[0] if bad
      else "%d cameras of 3" % len(shaped["cameras"]))
want_names = {stem_of(p): v for p, v in NAMED.items()}
bad = [(c["camera"], c.get("audio_tracks"), want_names.get(c["camera"]))
       for c in shaped["cameras"]
       if list(c.get("audio_tracks") or ()) != want_names.get(c["camera"])]
check("and the names of the audio tracks it wrote",
      not bad and len(shaped["cameras"]) == 3,
      "%s: audio_tracks %s, handed in %s" % bad[0] if bad
      else "%d cameras of 3" % len(shaped["cameras"]))

print("\n" + "=" * 66)
print("A RATE WHOSE TIMECODE COUNTS FASTER THAN THE MATERIAL RUNS")
print("=" * 66)
# At 25 and at 30 a timecode counts as many frames to the second as the
# material runs, and then "the frame this timecode names" and "the
# frame this second is" are one number: either may stand in for the
# other anywhere, and a cut list that counted its zero the second way
# would write exactly the same files. At 29.97 they part company -- the
# timecode still counts thirty to the second while the pictures run
# 29.97 -- and at 18:55 the two are 68 seconds apart. So this is the
# one rate at which the paper can be seen to count from the frame the
# start timecode names rather than from the raw second, and the one at
# which the paper and the Timeline can be caught naming different
# frames. Asked in frames and not in seconds, because seconds are what
# the two clocks disagree about.
DRIFT_FPS = 29.97
drift = Run("Onemomentdrift", ZERO, SPEECH, LENGTH, rate=DRIFT_FPS)
d_clock = tc_clock(drift.fps)
check("  the rate really is one whose timecode outruns its pictures",
      abs(drift.fps - DRIFT_FPS) < 1e-6 and abs(d_clock - drift.fps) > 1e-6,
      "%g fps, and a timecode on it counts %g frames to the second"
      % (drift.fps, d_clock))
d_zero = vpm.timecode_to_frames(drift.d["start_tc"], drift.fps)
d_first = int(round(drift.cut_edl[0][0] * d_clock)) if drift.cut_edl else -1
check("  the cut list counts from the frame the start timecode names, "
      "not from the second behind it", d_first == d_zero,
      "first entry on frame %d, start_tc on frame %d, %d apart"
      % (d_first, d_zero, d_first - d_zero))
# ------------------------------------------------- and at a second frame rate
# Everything above is written at 25 fps. A frame rate is where timecode
# arithmetic goes wrong -- the same instant gets a different frame
# number, and a rate read out of the wrong place is out by a frame per
# frame -- so the whole set of files is written once more at 30 and read
# back the way a stranger reads it: from the handover alone, the files
# beside it found by their stem, at the rate the handover itself states.
#
# These eight questions used to be put to a real production under
# /Volumes, where one happened to be lying. That made the section judge
# eight times on the one machine that had it and not at all on the six
# builders, and no floor in state/checks can hold a count that depends
# on which machine is asking: 122 here, 114 there, red on all six for a
# fault that was in the test. Material only one machine has cannot carry
# a judgement -- so the run this section reads is one it writes itself,
# and the four "if it is there" branches under it are gone with it.
OTHER_FPS = 30.0
print("\n" + "=" * 66)
print("THE SAME QUESTIONS AT A SECOND FRAME RATE")
print("=" * 66)
rate_run = Run("Onemomentrate", ZERO, SPEECH, LENGTH, rate=OTHER_FPS)
rd = json.load(open(rate_run.files["handover"], encoding="utf-8"))
rstem = rate_run.files["handover"][:-len("_resolve.json")]
rfps = vpm.resolve_timeline_rate(rd.get("fps") or OTHER_FPS)
rframe = 1.0 / rfps
rstart = float(rd["start_s"])


def rclock(tc):
    return vpm.timecode_to_frames(tc, rfps) / tc_clock(rfps)


print("  %s at %g fps" % (os.path.basename(rate_run.files["handover"]), rfps))
# First of the eight, because they all rest on it: if the rate never
# reached the handover, the questions below are the ones already asked
# at 25 fps, they are all green, and the section proves nothing twice.
check("  the handover really is at the other frame rate",
      abs(rfps - OTHER_FPS) < 1e-6 and abs(rfps - FPS) > 1e-6,
      "%g fps, against %g everywhere above" % (rfps, FPS))
check("  start_tc and start_s are the same instant",
      abs(rclock(rd["start_tc"]) - rstart) <= rframe,
      "%.3f vs %.3f" % (rclock(rd["start_tc"]), rstart))
redl = read_edl(rstem + "_cameracut.edl", rfps)
check("  cameracut.edl has one entry per cut entry",
      len(redl) == len(rd["cut"]),
      "%d vs %d" % (len(redl), len(rd["cut"])))
bad = [(i, a, rstart + e["start"]) for i, ((a, _b, _n), e)
       in enumerate(zip(redl, rd["cut"]))
       if abs(a - (rstart + e["start"])) > rframe]
check("  and every one begins where the cut does", not bad,
      "" if not bad else "entry %d: %.3f vs %.3f" % bad[0])
bad = [(i, n, e["camera"]) for i, ((_a, _b, n), e)
       in enumerate(zip(redl, rd["cut"])) if n != e["camera"]]
check("  and names the same camera", not bad,
      "" if not bad else "entry %d: %r vs %r" % bad[0])
rows = read_csv(rstem + "_speakers.csv")
ents = read_edl(rstem + "_speakers.edl", rfps)
check("  speakers.csv and .edl have the same number of entries",
      len(rows) == len(ents), "%d vs %d" % (len(rows), len(ents)))
bad = [(i, rclock(row["Start TC"]), a) for i, (row, (a, _b, _n))
       in enumerate(zip(rows, ents))
       if abs(rclock(row["Start TC"]) - a) > rframe]
check("  and the same times", not bad,
      "" if not bad else "row %d: %.3f vs %.3f" % bad[0])
lines = sorted((a, b, s["name"]) for s in rd["speakers"]
               for a, b in s["sections"])
check("  as many as the handover holds sections",
      len(lines) == len(ents), "%d vs %d" % (len(lines), len(ents)))
bad = [(i, a, rstart + s[0]) for i, ((a, _b, _n), s)
       in enumerate(zip(ents, lines))
       if abs(a - (rstart + s[0])) > rframe]
check("  and every one sits where the handover says", not bad,
      "" if not bad else "entry %d: %.3f vs %.3f" % bad[0])

if not os.environ.get("VPM_ONE_MOMENT_KEEP"):
    for folder in KEEP:
        shutil.rmtree(folder, ignore_errors=True)
else:
    print("\n  kept: %s" % ", ".join(KEEP))

print("\n%d checks in %.2f s" % (done, time.time() - began))
if error:
    print("FAIL: " + ", ".join(error))
    sys.exit(1)
# "All good." belongs to a whole run. Where a part fell away it is
# named again here, so the last line of the test cannot read as more
# than was done.
print("All good." if not left_out else
      "Good as far as it went -- left out: %s" % "; ".join(left_out))
