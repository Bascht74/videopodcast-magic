# -*- coding: utf-8 -*-
"""One production, and the two doors it can be started through.

The ground the whole-way tests stand on: the mixedcase fixture with its
numbers written down as values, a separation stored the way a run and
a project file carry it, a project file the window opens, the command
line a test writes itself, a child run with Resolve locked out, a
window run started with its own Start button, offscreen and in this
process, and one answered by hand first. What a test judges stays in
the test; this only builds.

Nothing in this file prints; run.sh would count a line against the test.
"""
import glob
import json
import os
import subprocess
import sys
import tempfile
import threading
import time

from fixture_root import fixture

# ---------------------------------------------------- the fixture's numbers
# Out of the table in fixtures.sh, as values and not computed: the
# camera, its rate, and the clock it starts on. The 29.97 clock is
# non-drop, thirty labels a second.
MEDIA = fixture("mixedcase")
WIDE, PRES, GUEST = ("WideCam_01011000_C001", "PresentersCam_01011000_C002",
                     "GuestCam_01011000_C003")
RATE = {WIDE: 25.0, PRES: 25.0, GUEST: 29.97}
CLOCK = {WIDE: "10:00:00:00", PRES: "10:00:03:00", GUEST: "10:00:05:15"}
# Where each camera rolls, in seconds of the programme (fixtures.sh).
ROLLS = {WIDE: 0.0, PRES: 3.0, GUEST: 5.5}
# Each camera at the frame its own clock names, at thirty labels a
# second: 10 h is 1080000, 3 s more 90, 5 s 15 frames 165.
FRAME_OF = {WIDE: 1080000, PRES: 1080090, GUEST: 1080165}
# Who speaks when, in seconds of the programme (fixtures.sh). The
# guest's recorder rolls at 0, so these are its own file's seconds too.
TURNS = {"Guest": [(1.0, 6.0), (14.0, 20.0), (29.0, 34.5), (43.0, 48.0),
                   (55.0, 59.5)],
         "Presenter": [(7.5, 12.5), (21.5, 27.5), (36.0, 41.5),
                       (49.5, 53.5)]}
# The camera each voice is set to, and the label the model gave it.
SEAT = {"Guest": GUEST, "Presenter": PRES}
LABEL = {"Guest": "SPEAKER_00", "Presenter": "SPEAKER_01"}
# The recording the separation was heard in: a recording, because the
# window hangs voices under a recording's row and nowhere else.
HEARD_IN = "Guest_Take0031A"
PRODUCTION = "Way"
# The wide edges are a rule with tests of their own. Off at both doors,
# so that every turn of the fixture lies inside a shot and is judged.
NO_EDGES = "--no-wide-edges"
# Nothing printed for this long and a run is stuck rather than slow.
STILL = 120.0


def media(name):
    """The fixture file of a camera or recording, by its stem or name."""
    hits = sorted(glob.glob(os.path.join(MEDIA, name + "*")))
    return hits[0] if hits else os.path.join(MEDIA, name)


def material():
    """(recordings, cameras) of this production, each sorted by name.

    One recording, the one the separation was heard in, and the three
    cameras. The presenter's recorder stays out: its row would carry
    the name a separated voice carries, and the window refuses one
    name on two speakers where the line folds them into one.
    """
    pictures = sorted(glob.glob(os.path.join(MEDIA, "*.mov")))
    sound = [p for p in [media(HEARD_IN)] if os.path.exists(p)]
    return sound, pictures


def missing():
    """Why the fixture cannot carry a run, or "" when it can."""
    sound, pictures = material()
    if len(sound) == 1 and len(pictures) == 3:
        return ""
    return ("no mixedcase fixture under %s (%d of 1 recording, %d of 3 "
            "cameras) -- run tests/fixtures.sh"
            % (MEDIA, len(sound), len(pictures)))


# ------------------------------------------------------ the stored voices
def separation(vpm):
    """The stored separation as a project file and a run carry it.

    Heard in HEARD_IN, named, and with the fingerprint of that file --
    written through the program's own writer, because the fingerprint
    is an input here and not a judgement.
    """
    source = media(HEARD_IN)
    segments = [(LABEL[who], list(TURNS[who])) for who in sorted(TURNS)]
    return vpm.speakers_for_project(
        source, segments, len(segments),
        dict((LABEL[who], who) for who in TURNS))


def separation_file(vpm, folder, seat=None):
    """Write the file --speakers-from reads; hands back its path.

    *seat* is name -> camera stem, SEAT unless a test asks otherwise.
    """
    path = os.path.join(folder, "separation.json")
    voices = dict((who, media(cam)) for who, cam in (seat or SEAT).items())
    with open(path, "w", encoding="utf-8") as f:
        json.dump({"format": vpm.FILE_FORMAT, "created_by": "test",
                   "speakers_of": separation(vpm), "voices_of": voices},
                  f, ensure_ascii=False, indent=1)
    return path


def project_file(vpm, folder, out, seat=None):
    """Write the project file the window opens; hands back its path.

    The six files, the production's name, the plain path, no wide
    edges, and the same
    separation with its voices named and seated -- "several speakers"
    on the recording it was heard in, which is what brings the voices
    up as rows. Opening moves the file, so it lies in *folder* alone.

    "several:" is keyed as the window keys it, by the absolute path of
    the table's row: on Windows the fixture folder comes in with forward
    slashes and os.path.join adds a backslash, and a key spelt the raw
    way is never found, so the voices never come up.
    """
    sound, pictures = material()
    source = media(HEARD_IN)
    assignment = {"several:" + os.path.abspath(source): True}
    for who, cam in (seat or SEAT).items():
        assignment["voice:" + vpm.voice_key(source, LABEL[who])] = \
            media(cam)
    path = os.path.join(folder, "videopodcast-magic_%s.json" % PRODUCTION)
    with open(path, "w", encoding="utf-8") as f:
        json.dump({"format": vpm.FILE_FORMAT, "version": "test",
                   "timeline": [], "preset": "", "production": PRODUCTION,
                   "project_type": "cut", "multitrack": False,
                   "wide_at_edges": False, "out_folder": out, "assignment": assignment,
                   "speakers": separation(vpm), "speakers_source": source,
                   "speakers_local": True,
                   "files": [{"path": p, "kind": "audio"} for p in sound]
                   + [{"path": p, "kind": "video"} for p in pictures]},
                  f, ensure_ascii=False, indent=1)
    return path


# ------------------------------------------------------ the command line
def line(script, speakers_from, out, extra=()):
    """The command line a test writes itself, not the one a window builds.

    No speech recognition: in a child nothing can be stood in, and the
    recognition would fetch a model.
    """
    sound, pictures = material()
    return ([sys.executable, script, "--without-auphonic",
             "--no-speech-recognition", "--production", PRODUCTION,
             "--speakers-from", speakers_from, "--out", out, NO_EDGES]
            + list(extra) + sound + pictures)


def line_run(argv, cache):
    """Run a child with Resolve locked out; (code, what it said, stuck).

    No --resolve, and the scripting interface pointed at a folder that
    is not there: the owner's Resolve may be open on this machine. The
    store is the caller's own, so nothing stored elsewhere answers, and
    the separation stays off: in a child the model cannot be stood in.
    """
    nowhere = os.path.join(cache, "no-resolve-here")
    env = dict(os.environ, RESOLVE_SCRIPT_API=nowhere, VPM_CACHE=cache,
               RESOLVE_SCRIPT_LIB=os.path.join(nowhere, "fusionscript.so"),
               VPM_NO_SPEAKER_SPLIT="1")
    kid = subprocess.Popen(argv, stdout=subprocess.PIPE,
                           stderr=subprocess.STDOUT, env=env)
    pieces = []

    def read():
        """Keep what the child prints, so it never blocks on a pipe."""
        for piece in iter(lambda: kid.stdout.read1(65536), b""):
            pieces.append(piece)

    reader = threading.Thread(target=read)
    reader.daemon = True
    reader.start()
    last, seen, stuck = time.time(), 0, False
    while kid.poll() is None:
        time.sleep(0.25)
        if len(pieces) != seen:
            seen, last = len(pieces), time.time()
        if time.time() - last > STILL:
            stuck = True
            kid.kill()
            break
    kid.wait()
    reader.join(10)
    return (kid.returncode, b"".join(pieces).decode("utf-8", "replace"),
            stuck)


# ------------------------------------------------------------ the window
def window_run(vpm, app, project, keep):
    """Open *project* in the window, press Start, wait for the run's end.

    The real button and the real gui_run_loop: the loop is wrapped, not
    replaced, so the line it was handed and what it wrote are kept in
    *keep* ("argv", "log", "ended", "why"). Waited on the loop coming
    back, with a standstill limit on the log; every question answered
    yes, since offscreen nobody would.
    """
    from PySide6 import QtCore, QtWidgets
    QtWidgets.QFileDialog.getOpenFileName = staticmethod(
        lambda *a, **k: (project, ""))
    QtWidgets.QDialog.exec = lambda self: QtWidgets.QDialog.Accepted
    QtWidgets.QMessageBox.exec = lambda self: QtWidgets.QMessageBox.Ok
    real = vpm.gui_run_loop
    keep.update(argv=None, log=[], ended=False, why="")

    def loop(argv, state, write, *rest):
        """The window's own run loop, with what passes through it kept."""
        keep["argv"] = list(argv)

        def kept(text):
            """Keep a piece of the log, and hand it on to the window."""
            keep["log"].append(text)
            return write(text)

        try:
            return real(argv, state, kept, *rest)
        finally:
            keep["ended"] = True

    vpm.gui_run_loop = loop
    step, since = [0], [time.time(), 0]

    def win():
        """The program's window, once it stands."""
        for x in app.topLevelWidgets():
            if vpm.DISPLAY_NAME in x.windowTitle():
                return x

    def button(text):
        """The window's button whose text begins with *text*."""
        for w in (win().findChildren(QtWidgets.QPushButton)
                  if win() else ()):
            if w.text().strip().startswith(text):
                return w

    def not_ready():
        """The reason the window gives for holding Start, on one line."""
        for w in win().findChildren(QtWidgets.QWidget) if win() else ():
            if w.toolTip().startswith(vpm.T("Not ready yet:")):
                return w.toolTip().replace("\n", " / ")[:240]
        return "no reason shown"

    def give_up(why):
        """Stop waiting, and keep the reason for the red line."""
        keep["why"] = why
        app.quit()

    def tick():
        """One step of the plan: open, wait for Start, press, wait."""
        try:
            if step[0] == 0:
                if button(vpm.T("Open project")) is None:
                    if time.time() - since[0] > 60:
                        return give_up("the window never showed its "
                                       "Open project button in 60 s")
                    return QtCore.QTimer.singleShot(50, tick)
                win().show()
                button(vpm.T("Open project")).click()
                step[0], since[0] = 1, time.time()
            elif step[0] == 1:
                k = button(vpm.T("Start"))
                if k is None or not k.isEnabled():
                    if time.time() - since[0] > 90:
                        return give_up("Start was not ready after 90 s: %s"
                                       % not_ready())
                    return QtCore.QTimer.singleShot(100, tick)
                k.click()
                step[0], since[0] = 2, time.time()
                since[1] = 0
            elif step[0] == 2:
                if keep["ended"]:
                    # The loop is back; let the window take its last
                    # signals before it goes.
                    step[0] = 3
                    return QtCore.QTimer.singleShot(300, tick)
                if keep["argv"] is None and time.time() - since[0] > 30:
                    return give_up("Start was pressed and no run began "
                                   "in 30 s")
                if len(keep["log"]) != since[1]:
                    since[0], since[1] = time.time(), len(keep["log"])
                elif time.time() - since[0] > STILL:
                    return give_up("the run stood still for %.0f s" % STILL)
            else:
                return app.quit()
        except Exception as e:
            return give_up("%s: %s" % (type(e).__name__, e))
        QtCore.QTimer.singleShot(100, tick)

    QtCore.QTimer.singleShot(0, tick)
    sys.argv = ["videopodcast_magic.py"]
    vpm.gui()
    vpm.gui_run_loop = real
    return keep


# ------------------------------------------- the window, answered by hand
def recordings():
    """All three recordings of the production: the guest's, two blocks."""
    return [media(n) for n in ("Guest_Take0031A", "Presenter_REC00031",
                               "Presenter_REC00032")]


def project_plain(vpm, folder, out, multitrack=True, extra=None):
    """A project file with all six files and no answers; hands back its path.

    No separation, no assignment: what the run gets is what a test then
    sets in the window by hand. *extra* is laid over the fields.
    """
    _sound, pictures = material()
    d = {"format": vpm.FILE_FORMAT, "version": "test", "timeline": [],
         "preset": "", "production": PRODUCTION, "project_type": "cut",
         "multitrack": multitrack, "wide_at_edges": False,
         "out_folder": out, "assignment": {},
         "files": [{"path": p, "kind": "audio"} for p in recordings()]
         + [{"path": p, "kind": "video"} for p in pictures]}
    d.update(extra or {})
    path = os.path.join(folder, "videopodcast-magic_%s.json" % PRODUCTION)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(d, f, ensure_ascii=False, indent=1)
    return path


def window_answered_run(vpm, app, project, keep, answer, run=True,
                        press="Start"):
    """As window_run, answered by hand before *press* ("Start", "Dry run").

    *answer(window)* is called every 100 ms once *project* is open (with
    None, none is), and hands back "" when its answers stand or what it
    still waits for; after 60 s the button is pressed regardless. With
    *run* False the loop is not entered: its line is kept, nothing
    written. *keep* gets "argv", "log", "ended", "why", "unanswered"
    (what never stood, or "") and "answered" (s it took, None if never).
    """
    from PySide6 import QtCore, QtWidgets
    QtWidgets.QFileDialog.getOpenFileName = staticmethod(
        lambda *a, **k: (project, ""))
    QtWidgets.QDialog.exec = lambda self: QtWidgets.QDialog.Accepted
    QtWidgets.QMessageBox.exec = lambda self: QtWidgets.QMessageBox.Ok
    real = vpm.gui_run_loop
    keep.update(argv=None, log=[], ended=False, why="", answered=None,
                unanswered="")

    def loop(argv, state, write, *rest):
        """The window's own run loop, or only its line, kept."""
        keep["argv"] = list(argv)

        def kept(text):
            """Keep a piece of the log, and hand it on to the window."""
            keep["log"].append(text)
            return write(text)

        try:
            return real(argv, state, kept, *rest) if run else 0
        finally:
            keep["ended"] = True

    vpm.gui_run_loop = loop
    step, since, waits = [0], [time.time(), 0], [""]

    def win():
        """The program's window, once it stands."""
        for x in app.topLevelWidgets():
            if vpm.DISPLAY_NAME in x.windowTitle():
                return x

    def button(text):
        """The window's button whose text begins with *text*."""
        for w in (win().findChildren(QtWidgets.QPushButton)
                  if win() else ()):
            if w.text().strip().startswith(text):
                return w

    def give_up(why):
        """Stop waiting, and keep the reason for the red line."""
        keep["why"] = why
        app.quit()

    def tick():
        """One step: open, answer, wait for Start, press, wait."""
        try:
            if step[0] == 0:
                if button(vpm.T("Open project")) is None:
                    if time.time() - since[0] > 60:
                        return give_up("the window never showed its "
                                       "Open project button in 60 s")
                    return QtCore.QTimer.singleShot(50, tick)
                win().show()
                win().resize(1400, 900)
                if project:
                    button(vpm.T("Open project")).click()
                step[0], since[0] = 1, time.time()
            elif step[0] == 1:
                # Answers that never stand go on to Start all the same,
                # so the run is judged and says what it got instead.
                waits[0] = answer(win())
                if waits[0] and time.time() - since[0] <= 60:
                    return QtCore.QTimer.singleShot(100, tick)
                keep["answered"] = (None if waits[0]
                                    else time.time() - since[0])
                keep["unanswered"] = waits[0]
                step[0], since[0] = 2, time.time()
            elif step[0] == 2:
                k = button(vpm.T(press))
                if k is None or not k.isEnabled():
                    if time.time() - since[0] > 90:
                        return give_up("%s was not ready after 90 s"
                                       % press)
                    return QtCore.QTimer.singleShot(100, tick)
                k.click()
                step[0], since[0], since[1] = 3, time.time(), 0
            elif step[0] == 3:
                if keep["ended"]:
                    step[0] = 4
                    return QtCore.QTimer.singleShot(300, tick)
                if keep["argv"] is None and time.time() - since[0] > 30:
                    return give_up("%s was pressed and no run began "
                                   "in 30 s" % press)
                if len(keep["log"]) != since[1]:
                    since[0], since[1] = time.time(), len(keep["log"])
                elif time.time() - since[0] > STILL:
                    return give_up("the run stood still for %.0f s" % STILL)
            else:
                return app.quit()
        except Exception as e:
            return give_up("%s: %s" % (type(e).__name__, e))
        QtCore.QTimer.singleShot(100, tick)

    QtCore.QTimer.singleShot(0, tick)
    sys.argv = ["videopodcast_magic.py"]
    vpm.gui()
    vpm.gui_run_loop = real
    return keep


def fields(window, said):
    """The window's fields a screen reader calls *said*, by the row named.

    A table cell's field carries "<column> -- <row>" as its name; the
    row after the dashes is the key. Found afresh on every call: an
    answer rebuilds the table, and the old fields are gone.
    """
    from PySide6 import QtWidgets
    out = {}
    for w in window.findChildren(QtWidgets.QWidget) if window else ():
        name = w.accessibleName() or ""
        if name.startswith(said + " -- "):
            out[name.split(" -- ", 1)[1].strip()] = w
    return out


# ----------------------------------------------------------- the results
def handover(out):
    """The run's handover in *out*, read, or None."""
    hits = sorted(glob.glob(os.path.join(out, "*_resolve.json")))
    if not hits:
        return None
    with open(hits[0], encoding="utf-8") as f:
        return json.load(f)


def cut_files(out):
    """The two EDLs and the cut CSVs in *out*, by name, as text.

    The folder's own path is taken out, so two doors writing into two
    folders can be held against each other line by line.
    """
    found = {}
    for pattern in ("*.edl", "*_cameracut.csv", "*_speakers.csv"):
        for p in sorted(glob.glob(os.path.join(out, pattern))):
            with open(p, encoding="utf-8", errors="replace") as f:
                found[os.path.basename(p)] = f.read().replace(out, "<out>")
    return found


def written_names(out):
    """Every file under *out* by its path inside it, sorted; [] if none."""
    found = []
    for root, _dirs, names in os.walk(out):
        found += [os.path.relpath(os.path.join(root, n), out)
                  .replace(os.sep, "/") for n in names]
    return sorted(found)


def own_folder(tag):
    """A folder of this test's own under the run's TMPDIR."""
    return tempfile.mkdtemp(prefix="vpm_way_%s_" % tag)


# ------------------------------------------- Resolve, stood in, no door
class Item(object):
    """One thing lying on a track: where, and which frames of its file."""

    def __init__(self, name, frame, first=None, after=None):
        self.name, self.frame, self.first, self.after = \
            name, frame, first, after

    def GetName(self):
        """The clip's file name, as Resolve names an item."""
        return self.name

    def GetDuration(self):
        """How many frames of its file it shows."""
        if self.first is None or self.after is None:
            return 0
        return self.after - self.first


class Clip(object):
    """A media pool clip: its file name, and the audio it brings along."""

    def __init__(self, path):
        self.name = os.path.basename(path)
        probe = subprocess.run(
            ["ffprobe", "-v", "error", "-show_entries", "stream=codec_type",
             "-of", "csv=p=0", path], stdout=subprocess.PIPE)
        self.channels = probe.stdout.decode().split().count("audio")

    def GetClipProperty(self):
        """The one property the import reads: its audio channels."""
        return {"Audio Ch": str(self.channels)}


class Timeline(object):
    """Keeps what it is told, and refuses a track that was never made.

    As project_mixed_run_lands' own: a new Resolve Timeline brings one
    video and one audio track, and a deleted track renumbers those above.
    """

    def __init__(self, name):
        self.name = name
        self.tracks = {"video": [[]], "audio": [[]]}
        self.names = {"video": {}, "audio": {}}
        self.starts = []

    def GetName(self):
        """Its name."""
        return self.name

    def GetTrackCount(self, kind):
        """How many tracks of that kind there are."""
        return len(self.tracks[kind])

    def AddTrack(self, kind):
        """One more track of that kind, always granted."""
        self.tracks[kind].append([])
        return True

    def DeleteTrack(self, kind, i):
        """Take track *i* away; those above move down one."""
        if not 1 <= i <= len(self.tracks[kind]):
            return False
        del self.tracks[kind][i - 1]
        names = self.names[kind]
        self.names[kind] = dict((j - (j > i), n) for j, n in names.items()
                                if j != i)
        return True

    def GetItemListInTrack(self, kind, i):
        """What lies on track *i*, nothing for a track not there."""
        if not 1 <= i <= len(self.tracks[kind]):
            return []
        return list(self.tracks[kind][i - 1])

    def SetTrackName(self, kind, i, name):
        """Name track *i*; refused for a track not there."""
        if not 1 <= i <= len(self.tracks[kind]):
            return False
        self.names[kind][i] = name
        return True

    def GetTrackName(self, kind, i):
        """The name track *i* was given."""
        return self.names[kind].get(i, "")

    def SetStartTimecode(self, tc):
        """Keep every start set, the last one counting."""
        self.starts.append(tc)
        return True

    def GetStartTimecode(self):
        """The last start set, or Resolve's own default."""
        return self.starts[-1] if self.starts else "01:00:00:00"

    def SetClipsLinked(self, items, state):
        """Linking changes nothing that is looked at here."""
        return True

    def DeleteClips(self, items):
        """Take the items off every track."""
        for kind in self.tracks:
            self.tracks[kind] = [[p for p in t if p not in items]
                                 for t in self.tracks[kind]]
        return True


class Pool(object):
    """Resolve's insert: picture and sound on one track number unless told.

    Where a track is missing or its sound would land on taken tracks,
    the whole entry is refused without a word, as Resolve does.
    """

    def __init__(self, tl):
        self.tl = tl

    def AppendToTimeline(self, entries):
        """Lay what fits, keep its frames, and drop the rest silently."""
        out = []
        for e in entries:
            clip, i, kind = e["mediaPoolItem"], e["trackIndex"], \
                e.get("mediaType")
            room = range(i, i + max(1, clip.channels))
            picture = 1 <= i <= self.tl.GetTrackCount("video")
            sound = (i >= 1 and room[-1] <= self.tl.GetTrackCount("audio")
                     and not any(self.tl.GetItemListInTrack("audio", t)
                                 for t in room))
            if not {1: picture, 2: sound}.get(kind, picture and sound):
                continue
            # One item per track, as Resolve lays them: picture and each
            # sound track are apart, and deleting one leaves the others.
            def item():
                return Item(clip.name, e["recordFrame"], e.get("startFrame"),
                            e.get("endFrame"))
            if kind != 2:
                self.tl.tracks["video"][i - 1].append(item())
            if kind != 1:
                for t in room:
                    self.tl.tracks["audio"][t - 1].append(item())
            out.append(item())
        return out


def lay(vpm, d):
    """Build both Timelines out of a handover, on the stand-in.

    The cut Timeline as the import builds it, lead-in and all, but
    without the mix; then the camera Timeline. Returns (cut Timeline,
    camera Timeline, what broke or ""). What they print is kept out.
    """
    import io
    import traceback
    cameras = d.get("cameras") or []
    clips = dict((c["file"], Clip(c["file"])) for c in cameras
                 if c.get("file"))
    cut_tl = Timeline("%s Cut" % PRODUCTION)
    cam_tl = Timeline("%s Multicam" % PRODUCTION)
    d["_refused"] = []
    kept, sys.stdout = sys.stdout, io.StringIO()
    try:
        fps, origin = vpm.timeline_origin(d)
        pool = Pool(cut_tl)
        lead_in = vpm.lead_in_offset(pool, cut_tl, d, clips, fps, origin)
        vpm.build_cut_timeline(pool, cut_tl, d.get("cut") or [], cameras,
                               clips, d, None, lead_in)
        vpm.build_camera_timeline(Pool(cam_tl), cam_tl,
                                  vpm.cameras_in_track_order(cameras),
                                  clips, d)
        broke = ""
    except Exception as e:
        where = traceback.extract_tb(sys.exc_info()[2])[-1]
        broke = "%s: %s, in %s line %d" % (type(e).__name__, e, where.name,
                                           where.lineno)
    finally:
        sys.stdout = kept
    return cut_tl, cam_tl, broke
