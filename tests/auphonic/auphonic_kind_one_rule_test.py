# -*- coding: utf-8 -*-
"""The preset list and the run ask one rule for the kind of preset.

Three ways, each asked of the window's preset list and of the run: two
recordings with a picture and the Multitrack tick off, the same without
a picture, and without a picture with the tick on. The list is the
window's own box, fed the account's two presets; the run is the time
base in this process, stopped where the time axis would be measured.
auphonic.com is stood in for where the piece looks it up.
"""
PLATFORM_BOUND = True
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
import io
import shutil
import subprocess
import tempfile
import time
import types

began = time.time()
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
vpm = the_program.load()
vpm.set_language("en")
from PySide6 import QtWidgets
app = QtWidgets.QApplication.instance() or QtWidgets.QApplication(
    sys.argv[:1])

done = 0
bad = []


def check(name, ok, extra=""):
    global done
    done += 1
    print("  %-58s %s %s" % (name, "ok" if ok else "FAIL", extra))
    if not ok:
        bad.append("%s [%s]" % (name, extra or "no numbers"))


PRESETS = [("Podcast_Single", "u1", False), ("Podcast_Multi", "u2", True)]
events, sent = [], []


class AxisReached(Exception):
    """Raised where the time axis would be measured: the run ends there."""


def offline(*_a, **_k):
    """The one road to auphonic.com, stood in for: it refuses."""
    events.append("curl")
    raise RuntimeError("auphonic.com is not asked in this test")


def single(audio, preset, _name, *_a, **_k):
    """One Singletrack production, written down; its result the upload."""
    sent.append(("single", preset))
    return audio


def multi(_key, preset, _title, tracks, *_a, **_k):
    """One Multitrack production, written down; the uploads come back."""
    sent.append(("multi %d" % len(tracks), preset))
    return dict((t["name"], t["axis"]) for t in tracks)


def axis(*_a, **_k):
    """The first step of the time axis: noted, and the run stops."""
    events.append("axis")
    raise AxisReached()


vpm._curl_call = offline
vpm.api_key_source = lambda *a, **k: ("FAKEKEY-0000", "store")
vpm.load_api_key = lambda *a, **k: ""
vpm.list_presets = lambda key: events.append("preset") or list(PRESETS)
vpm.check_preset = lambda *a, **k: []
vpm.run_single_production = single
vpm.run_multitrack_production = multi
vpm.verify_returned_tracks = lambda *a, **k: True
vpm.normalise_loudness = lambda *a, **k: (0.0, None)
vpm.align_cameras = axis

WORK = tempfile.mkdtemp(prefix="vpm_kind_")


def made(name, source):
    """A few seconds of material, written by ffmpeg; its path."""
    path = os.path.join(WORK, name)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i",
                    source, "-f", "lavfi", "-i",
                    "sine=frequency=330:duration=3", "-ar", "48000",
                    "-shortest", path] if name.endswith(".mp4") else
                   ["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i",
                    source, "-ar", "48000", path], check=True)
    return path


GUEST = made("Guest.wav", "sine=frequency=220:duration=3")
PRESENTER = made("Presenter.wav", "sine=frequency=440:duration=3")
CAMERA = made("WideCam.mp4", "smptebars=size=160x90:rate=25:duration=3")


kept = []


def boxes():
    """Every preset list the window code has built so far."""
    return [w for w in QtWidgets.QApplication.allWidgets()
            if type(w).__name__ == "PresetBox"]


def listed(videos, tick):
    """The presets the window's box offers for two named recordings."""
    model = types.SimpleNamespace(
        assign_lines=[(None, vpm.Value("Guest"), vpm.Value(vpm.MIX_ONLY)),
                      (None, vpm.Value("Presenter"),
                       vpm.Value(vpm.MIX_ONLY))],
        files=[(GUEST, "audio"), (PRESENTER, "audio")]
        + [(v, "video") for v in videos],
        clip_kinds={}, multitrack=vpm.Value(tick))
    # The page and the button are kept: Qt deletes what Python lets go.
    kept.append((QtWidgets.QWidget(), QtWidgets.QPushButton()))
    holder, layout = [], QtWidgets.QVBoxLayout(kept[-1][0])
    bridge = types.SimpleNamespace(presets=types.SimpleNamespace(
        connect=holder.append))
    before = set(boxes())
    kept.append(vpm.make_auphonic_box(
        QtWidgets, {}, bridge, lambda *a: None, layout, lambda: None,
        lambda: None, kept[-1][1], vpm.Value(""), lambda: "",
        lambda *a: None, lambda: vpm.run_tracks_of(model)))
    holder[0](list(PRESETS), "", "FAKEKEY-0000")
    box = (set(boxes()) - before).pop()
    return [box.itemData(i) for i in range(1, box.count())
            if box.model().item(i).isEnabled()]


def run(videos, preset, *switches):
    """The time base on the two recordings: (return, events, sent)."""
    del events[:], sent[:]
    args = vpm.build_argument_parser().parse_args(
        [GUEST, PRESENTER] + videos + ["--auphonic-preset", preset,
                                       "--out", WORK] + list(switches))
    args.auphonic_key = "FAKEKEY-0000"
    plan = [{"audio": path, "blocks": [path], "speakers": name,
             "camera": ""}
            for path, name in ((GUEST, "Guest"), (PRESENTER, "Presenter"))]
    kept, sys.stdin = sys.stdin, io.StringIO("")
    try:
        code = vpm.build_common_timebase(args, plan, [], videos)
    except AxisReached:
        code = "axis"
    finally:
        sys.stdin = kept
    return code, list(events), list(sent)


try:
    print("Two recordings with a picture, the Multitrack tick off")
    offered = listed([CAMERA], False)
    check("the list offers the Multitrack preset for two on a picture",
          offered == ["Podcast_Multi"],
          "the list offers %s, wanted ['Podcast_Multi']" % offered)
    code, seen, up = run([CAMERA], "Podcast_Multi")
    check("the run takes it, and asks before the time axis",
          seen == ["preset", "axis"],
          "asked in this order: %s, wanted ['preset', 'axis']; returned %r"
          % (seen, code))
    code, seen, up = run([CAMERA], "Podcast_Single")
    check("a Singletrack preset stops the run before the time axis",
          code == 1 and "preset" in seen and "axis" not in seen,
          "returned %r against 1, asked in this order: %s, wanted the "
          "preset and no axis" % (code, seen))

    print("\nTwo recordings without a picture, the tick off")
    offered = listed([], False)
    check("the list offers the Singletrack preset for two joined alone",
          offered == ["Podcast_Single"],
          "the list offers %s, wanted ['Podcast_Single']" % offered)
    code, seen, up = run([], "Podcast_Single")
    check("the run sends each as a Singletrack production of that preset",
          code == 0 and up == [("single", "u1"), ("single", "u1")],
          "returned %r against 0, sent %s, wanted two ('single', 'u1')"
          % (code, up))
    code, seen, up = run([], "Podcast_Multi")
    check("a Multitrack preset stops the join before anything goes up",
          code == 1 and not up,
          "returned %r against 1, sent %s, wanted nothing" % (code, up))

    print("\nTwo recordings without a picture, the tick on")
    offered = listed([], True)
    check("the list offers the Multitrack preset for tracks on one axis",
          offered == ["Podcast_Multi"],
          "the list offers %s, wanted ['Podcast_Multi']" % offered)
    del sent[:]
    args = types.SimpleNamespace(auphonic_preset="Podcast_Multi", lufs=None,
                                 auphonic_wait=60, dry_run=False,
                                 auphonic_resume=None)
    code = vpm.send_to_auphonic(
        args, [{"name": "Guest", "axis": GUEST},
               {"name": "Presenter", "axis": PRESENTER}], WORK, WORK, 3.0)
    check("the run sends them as one Multitrack production",
          code is None and sent == [("multi 2", "u2")],
          "returned %r against None, sent %s, wanted [('multi 2', 'u2')]"
          % (code, sent))
except Exception as e:
    bad.append("the test ran into %s: %s" % (type(e).__name__, e))
finally:
    shutil.rmtree(WORK, True)

print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
