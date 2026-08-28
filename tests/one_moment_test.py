# -*- coding: utf-8 -*-
"""One moment, and every way to it has to land on the same second.

Three clocks run through this program and none of them says its name:

  programme time   zero is start_s of the handover file
  file time        zero is the start of that camera's file; the bridge
                   is offset -- "position in the file is programme time
                   minus this"
  window time      zero is the In point

Every consumer worked its own conversion out for itself: the player,
the band under it, the cut list, the handover file, the Resolve build,
the EDL and the CSV. None of them wrote down which clock it was
standing in. That is why a repair in one place could break another,
three times in a row on one day, without anything looking wrong in
between.

So this test does not check a number. It takes a moment it knows the
place of -- the start of a shot, and the start of a speech section --
and walks it out to an absolute wall clock time over every way that
exists:

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

All of them have to name the same wall clock time, within one frame.
Where two do not, both numbers and both ways are printed -- a test that
only says "red" does not help the next time.

And the whole of it twice: once with the window wide open, once with an
In point and an Out point set. The third clock is where the expensive
mistakes were made, and the worst of them moved every speech section by
215.600 s because the window was applied twice. So four things are held
about it:

  * with a window set, all the ways still land on one frame;
  * the window moves nothing against anything else -- for one real
    moment the position in the camera file is the same before and after
    it is set. What a window changes is what falls away, not what slides
    where;
  * applying an absolute In point a second time moves nothing more, and
    a relative one moves by exactly one more In point and never two;
  * "+0:10:00" means ten minutes from the window start and "-0:05:00"
    five minutes back from its end -- not eighteen hours, and not zero.

The second half holds the five files one run writes against each other:
_resolve.json, _cameracut.edl, _cameracut.csv, _speakers.edl and
_speakers.csv. The same cuts, the same times, the same length, written
five ways. Where they part company, Resolve gets something other than
the preview shows, and no Resolve is needed to see it.

The third: the preview does not read the cut out of the handover file,
it computes it again with cut_statistics(). Two computations of one
thing drift. So the recomputed cut is held against the written one --
and with it the two name spaces, because the cut list names cameras by
the camera's name while the player keys on the track name, and they are
the same string only where no camera carries a speaker. A consumer that
confuses them loses every shot without a word.

The material is built here, out of the shared interview fixture, whose
three cameras carry real timecodes (Totale 18:55:00:00, Moderatoren
18:55:04:00, Kandidat 18:55:17:12) but all the same test picture. So
what is checked here is the conversion of one file against the axis --
not the alignment of three, which cannot be measured off equal
pictures. The offsets are therefore not measured but read off the
timecodes, which is what the program does too.

VPM_ONE_MOMENT_KEEP=1 leaves the written files in place for looking at.
"""
import os, sys, csv, json, re, shutil, subprocess, tempfile, types
import importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = os.environ.get("VPM_SCRIPT") or os.path.join(
    os.path.dirname(HERE), "videopodcast-magic.py")
sys.path.insert(0, HERE)
from fixture_root import fixture

spec = importlib.util.spec_from_file_location("vpm", SCRIPT)
vpm = importlib.util.module_from_spec(spec)
sys.modules["vpm"] = vpm
spec.loader.exec_module(vpm)

error = []


def check(name, ok, extra=""):
    print("  %-58s %s %s" % (name, "ok" if ok else "FAIL", extra))
    if not ok:
        error.append(name)


# ---------------------------------------------------------------- material
FIX = fixture("interview")
WIDE = os.path.join(FIX, "Totale_08141855_C003.mov")
MOD = os.path.join(FIX, "Moderatoren_08141855_C005.mov")
KAND = os.path.join(FIX, "Kandidat_08141858_C009.mov")
FPS = 25.0
FRAME = 1.0 / FPS

if not all(os.path.exists(p) for p in (WIDE, MOD, KAND)):
    print("SKIPPED: no interview fixture -- run tests/fixtures.sh")
    sys.exit(0)

stamp = {p: vpm.file_timecode(p, FPS) for p in (WIDE, MOD, KAND)}
if any(v is None for v in stamp.values()):
    print("SKIPPED: the fixture cameras carry no timecode -- rebuild the")
    print("  interview folder with tests/fixtures.sh (INTERVIEW_BUILD)")
    sys.exit(0)

ZERO = stamp[WIDE]              # the earliest camera is the zero of the axis
ZERO_TC = vpm.timecode_string(ZERO, FPS)
LENGTH = 60.0
KEEP = []


def stem_of(p):
    return os.path.splitext(os.path.basename(p))[0]


cameras = [{"video": p, "name": stem_of(p)} for p in (WIDE, MOD, KAND)]
videos = [(p, {"width": 1280, "height": 720, "fps": FPS, "duration": 120.0,
               "tc": ZERO_TC if p == WIDE else None})
          for p in (WIDE, MOD, KAND)]
tracks = [{"name": "Moderator", "camera": MOD},
          {"name": "Kandidat", "camera": KAND}]
ref_clip = (WIDE, videos[0][1])

# The moments this test knows the place of, as wall clock times. Chosen
# so that every shot falls inside the time all three cameras are
# rolling: the Kandidat camera starts 17.48 s after the axis begins, and
# a shot before that has no picture at all -- which is a different fault
# from a wrong conversion and must not stand in for it here.
SPEECH = [("Moderator", [(22.0, 34.0), (46.0, 58.0)]),
          ("Kandidat", [(36.0, 44.0)])]


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


def read_edl(path, fps):
    """(start s, end s, clip name) per entry, in file order.

    *fps* has to be the rate the file was written at: a timecode read at
    the wrong rate is out by up to a frame per frame number, which is
    exactly the mistake this test exists to catch.
    """
    rate = float(fps)

    def at(tc):
        return vpm.timecode_to_frames(tc, rate) / rate

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
                 in_point=None, out_point=None, mix=None):
        self.name = name
        self.dir = tempfile.mkdtemp(prefix="onemoment_")
        KEEP.append(self.dir)
        self.args = make_args(name, in_point, out_point)
        print("\nTHE RUN %r%s" % (name, (" with In point %s, Out point %s"
                                         % (in_point, out_point))
                                  if in_point or out_point else ""))
        self.cut, self.segs = vpm.write_cut_list(
            self.args, speech, tracks, cameras, videos, self.dir,
            tc_start, ref_clip, length)
        vpm.write_handover(
            self.args, tracks, cameras, videos, self.dir, tc_start, ref_clip,
            results=[WIDE, MOD, KAND], cut=self.cut, segment_list=self.segs,
            length=length, track_names={}, single_files=dict(mix or {}),
            offsets={p: 0.0 for p in (WIDE, MOD, KAND)}, words=())
        self.stem = os.path.join(self.dir, vpm.safe_filename(name))
        self.files = {
            "handover": self.stem + "_resolve.json",
            "cameracut.edl": self.stem + "_cameracut.edl",
            "cameracut.csv": self.stem + "_cameracut.csv",
            "speakers.edl": self.stem + "_speakers.edl",
            "speakers.csv": self.stem + "_speakers.csv"}
        gone = [n for n, p in self.files.items() if not os.path.exists(p)]
        if gone:
            print("FAIL: the run %r wrote no %s" % (name, ", ".join(gone)))
            sys.exit(1)
        self.d = json.load(open(self.files["handover"], encoding="utf-8"))
        d = self.d
        self.fps = vpm.nearest_known_frame_rate(d.get("fps") or FPS)
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
        return vpm.timecode_to_frames(tc, self.fps) / float(self.fps)

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
        # the build took every one of them, which is exact and shows a
        # shifted recordFrame as a wrong number. Where it dropped a shot
        # the positions no longer line up, and pairing them anyway would
        # blame the wrong entry -- then each is looked for by the place it
        # landed on, and an entry that has none is said to be out of reach
        # rather than given a number belonging to its neighbour.
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
        tc = stamp.get(cam.get("file") or cam.get("source"))
        if tc is None:
            return None
        return tc + (t - offset)

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
    not be walked at all, which is said rather than passed over.

    *tag* is what the failing line says at the bottom of the run, where
    run.sh reads it: "9 ways on one frame" five times over says nothing
    about which moment came apart.
    """
    print("\n%s" % heading)
    gone = [n for n, v in ways if v is None]
    have = [(n, v) for n, v in ways if v is not None]
    for n in gone:
        print("      not reachable: %s" % n)
    if len(have) < 2:
        check("%s: at least two ways lead there" % tag, False,
              "%d of %d" % (len(have), len(ways)))
        return
    # The whole spread, not neighbour against neighbour: three ways a
    # frame apart each are two frames apart at the ends, and the pair
    # that matters is the outer one.
    low = min(v for _n, v in have)
    high = max(v for _n, v in have)
    ok = (high - low) <= FRAME * 1.001
    # Grouped only for the report, so a divergence names both sides.
    # Ways a single frame apart go into one line: that is rounding, not
    # a disagreement, and three lines a frame apart would read like one.
    groups = {}
    for n, v in sorted(have, key=lambda x: x[1]):
        near = [k for k in groups if abs(k - v) <= FRAME * 1.001]
        groups.setdefault(near[0] if near else v, []).append((n, v))
    check("%s: %d ways, all on one frame" % (tag, len(have)), ok,
          "" if ok else "%.3f s apart, %d different answers"
          % (high - low, len(groups)))
    for key in sorted(groups):
        names = groups[key]
        print("      %s  (%s)"
              % (vpm.timecode_string(names[0][1], FPS),
                 ", ".join("%s = %.3f" % (n, v) for n, v in names)))
    return ok


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
             (stamp.get(r.by_camera[camera]["file"]) or 0.0)
             + float(x["startFrame"]) / r.fps_r),
        ]
        agree("%s: the shot on %s at %.3f s" % (r.name, camera, t),
              "%s: the shot on %s that begins at %.3f s programme time"
              % (r.name, camera, t), ways)

    # And a speech moment, which is where the speaker files can be reached.
    for s in d["speakers"]:
        if not s["sections"]:
            continue
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
        agree("%s: %s starts speaking at %.3f s" % (r.name, name, t),
              "%s: %s starts speaking at %.3f s programme time -- on %s"
              % (r.name, name, t, on_screen), ways)

    print("\n  THE BRIDGE BETWEEN THE AXES")
    for c in d["cameras"]:
        got = stamp.get(c["file"])
        check("  %s: timecode - start_s == offset" % c["camera"],
              got is not None
              and abs((got - r.start_s) - float(c["offset"])) <= r.frame,
              "" if got is None else
              "%.4f vs %.4f" % (got - r.start_s, c["offset"]))
        check("  %s: camera_offset() says the same" % c["camera"],
              abs(r.player_offset.get(c["track"], 1e9)
                  - float(c["offset"])) <= r.frame,
              "%.4f vs %.4f" % (r.player_offset.get(c["track"], 0.0),
                                c["offset"]))


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

    # The CSV is the finer of the two: it splits a shot again where the
    # speaker changes inside it. So it is the camera changes that have to
    # line up, not the row count.
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
    # "Time from start" is the window column: it counts from the axis, not
    # from midnight, and that is the one place the two clocks meet in a
    # file. With an In point set it counts from the In point, which is
    # what start_s then is.
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
    last = max(x["recordFrame"] + (x["endFrame"] - x["startFrame"])
               for x in r.placed)
    check("the Resolve timeline ends where the EDL ends",
          abs(float(last) / r.fps_r - r.cut_edl[-1][1]) <= r.frame,
          "%.3f vs %.3f" % (float(last) / r.fps_r, r.cut_edl[-1][1]))
    check("the Timeline was given the handover's own start timecode",
          r.timeline.start_tc == d["start_tc"],
          "%r vs %r" % (r.timeline.start_tc, d["start_tc"]))


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
# In the night "+0:10:00" came out as eighteen hours and "-0:05:00" as
# zero, because the sign was read off after the colons were counted. So
# the four notations are read here one by one, before anything uses them.
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
    print("\nFAIL: " + ", ".join(error))
    sys.exit(1)
# The run measures the speech on the trimmed material, so the sections
# count from the In point. The same real moments, on the new axis.
WINDOW_SPEECH = [(n, [(max(0.0, a - NEW0), min(NEW1 - NEW0, b - NEW0))
                      for a, b in segs if b > NEW0 and a < NEW1])
                 for n, segs in SPEECH]
win_run = Run("Onemomentwin", ZERO + NEW0, WINDOW_SPEECH, NEW1 - NEW0,
              in_point=IN_TEXT, out_point=OUT_TEXT)

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
# The point of a window is that something falls away, not that something
# slides. So one real wall clock moment is taken and asked of both runs:
# where in this camera's file does it sit? The two answers have to be
# the same number, or the sound runs against the wrong picture as soon
# as somebody sets an In point.
check("the window moved the axis by the In point",
      abs((win_run.start_s - open_run.start_s) - NEW0) <= FRAME,
      "%.3f vs %.3f" % (win_run.start_s - open_run.start_s, NEW0))
check("and shortened the material by the head and the tail",
      abs(float(win_run.d["length_s"])
          - (float(open_run.d["length_s"]) - NEW0
             - (LENGTH - NEW1))) <= FRAME,
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
# This is the mistake that cost the night: the window was applied once
# where the speakers were read and once again below, and every section
# moved by 215.600 s. An absolute In point cannot do that -- after the
# first application start_s IS the In point, so the second finds nothing
# to remove. A relative one is a different promise: "ten seconds from
# where the window now starts", so it moves ten seconds each time and
# never twenty. Both are held, because a defect could break either.
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
# By ten seconds, once. This is the check the night needed: a window
# applied twice leaves start_s right and moves everything under it by
# twice as much, so a test that only asks whether the second application
# changes anything sees nothing wrong.
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
# The windowed handover goes to the player and the band, never to
# timeline_origin: apply_time_window moves start_s and leaves start_tc
# where it was, so the two no longer name one instant. Held here so that
# nobody hands this dict to the Resolve build without noticing.
check("apply_time_window leaves start_tc behind -- so a windowed "
      "handover must not reach timeline_origin",
      abs(open_run.clock(once["start_tc"]) - float(once["start_s"])) > FRAME,
      "start_tc %s, start_s %.3f" % (once["start_tc"], once["start_s"]))
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
# cameras[].camera. The player, the band and camera_offset key on
# cameras[].track, which is the speakers' names joined where anybody is
# assigned and the camera's own name only where nobody is. The two are
# the same string only in a production where no camera carries a
# speaker -- and a consumer that takes one for the other finds no file,
# drops every shot and says nothing at all. So both directions are held.
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
check("camera_offset() is keyed on tracks, not on camera names",
      set(open_run.player_offset) == set(track_names),
      str(sorted(open_run.player_offset)))
# What the window does with them: files_per_track is built on tracks and
# the cut it feeds the player comes from cut_statistics, which is also
# on tracks. Fed the handover's own cut instead, nothing would match.
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
# The mix is the third thing the window touches: the player runs it under
# the cut, and audio_for_cut works its offset out as "timecode of the
# mix minus start_s", the same rule as for a camera. That function is
# nested inside gui() and closes over prepared_tracks(), so it cannot be
# called from here at all -- what can be checked is the ground it stands
# on: a mix stamped the way the run stamps it reads back as start_s, so
# its offset is zero, and the Resolve build lays it down at the axis.
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
if made.returncode or not os.path.exists(MIXFILE):
    print("  no Full-Mix could be built (%s) -- the mix checks are left out"
          % (made.stderr.decode("utf-8", "replace")[:120] or "ffmpeg failed"))
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
    if mix_run.audio:
        at = float(mix_run.audio[0]["recordFrame"]) / mix_run.fps_r
        check("and laid it down at start_s, in one piece",
              abs(at - mix_run.start_s) <= mix_run.frame
              and not mix_run.audio[0].get("startFrame"),
              "%.3f vs %.3f, startFrame %s"
              % (at, mix_run.start_s, mix_run.audio[0].get("startFrame")))

# ------------------------------------------- a real run, where one is on disk
REAL = os.environ.get("VPM_ONE_MOMENT_REAL",
                      "/Volumes/VIDEOS/Video_Podcast/Testinterview/Ausgabe")
real_json = None
if os.path.isdir(REAL):
    real_json = next((os.path.join(REAL, f) for f in sorted(os.listdir(REAL))
                      if f.endswith("_resolve.json")), None)
print("\n" + "=" * 66)
print("A REAL RUN, IF ONE IS ON THIS MACHINE")
print("=" * 66)
if not real_json:
    # Not a skip: everything above stands on its own. This only adds a
    # second frame rate and a run nobody built for a test.
    print("  none here (%s) -- the fixture runs above checked the same"
          % REAL)
else:
    rd = json.load(open(real_json, encoding="utf-8"))
    rstem = real_json[:-len("_resolve.json")]
    rfps = vpm.nearest_known_frame_rate(rd.get("fps") or 30.0)
    rframe = 1.0 / rfps
    rstart = float(rd["start_s"])

    def rclock(tc):
        return vpm.timecode_to_frames(tc, rfps) / float(rfps)

    print("  %s at %g fps" % (os.path.basename(real_json), rfps))
    check("  start_tc and start_s are the same instant",
          abs(rclock(rd["start_tc"]) - rstart) <= rframe,
          "%.3f vs %.3f" % (rclock(rd["start_tc"]), rstart))
    if os.path.exists(rstem + "_cameracut.edl"):
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
    if os.path.exists(rstem + "_speakers.csv") \
            and os.path.exists(rstem + "_speakers.edl"):
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

print()
if error:
    print("FAIL: " + ", ".join(error))
    sys.exit(1)
print("All good.")
