# -*- coding: utf-8 -*-
"""The window and the command line separate the same way.

The same folder has to give the same cut either way: both pick the same
recording, both refuse in the same places, the switches hold, the
segments lead to the same cut list, and what one way measured the other
reads out of the store instead of measuring it a second time.

The separation itself is a stand-in that answers out of a table and
notes that it was called. What is measured is which way asks for it,
not what a model hears. The store is this test's own, and it is emptied
before every check that is about a machine which has not separated this
recording before.
"""
import os
HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = os.environ.get("VPM_SCRIPT") or os.path.join(
    os.path.dirname(HERE), "videopodcast-magic.py")
import importlib.util
import shutil
import sys
import tempfile
import time
spec = importlib.util.spec_from_file_location("vpm", SCRIPT)
vpm = importlib.util.module_from_spec(spec); sys.modules["vpm"] = vpm
spec.loader.exec_module(vpm)

began = time.time()
done = 0
bad = []


def check(name, ok, extra=""):
    global done
    done += 1
    print("  %-58s %s %s" % (name, "ok" if ok else "FAIL", extra))
    if not ok:
        bad.append("%s [%s]" % (name, extra or "no numbers"))


folder = tempfile.mkdtemp(prefix="vpm-same-way-")
# A store of its own: the suite hands every test one cache folder, and
# a separation another test left there would answer here for a file
# this one never saw.
os.environ["VPM_CACHE"] = tempfile.mkdtemp(prefix="vpm-same-way-store-")


def made(name):
    path = os.path.join(folder, name)
    with open(path, "wb") as f:
        f.write(b"0")
    return path


RECORDER = made("recorder.wav")
SECOND = made("second.wav")
CAM_A = made("camA.mov")
CAM_B = made("camB.mov")
LENGTH = {CAM_A: 600.0, CAM_B: 1800.0}


class Args(object):
    """As much of the parsed command line as the separation reads."""

    def __init__(self, **over):
        self.speakers_local = None
        self.speakers_from = None
        self.speakers_count = 0
        self.no_speakers_local = False
        self.dry_run = False
        self._speakers_of = {}
        self._camera_audio = None
        self.__dict__.update(over)


def tracks_of(*paths):
    return [{"name": os.path.basename(p), "source": p, "blocks": [p],
             "a": 0.0, "b": 1.0} for p in paths]


print("1. Both ways pick the same recording")
window = vpm.speaker_source_pick([RECORDER], [CAM_A, CAM_B])
run = vpm.separation_source_of_run(Args(), tracks_of(RECORDER),
                                   [CAM_A, CAM_B])
check("one recording: the same file and the same reason",
      window == run and run[0] == RECORDER, str(run))

window = vpm.speaker_source_pick([RECORDER, SECOND], [CAM_A, CAM_B])
run = vpm.separation_source_of_run(Args(), tracks_of(RECORDER, SECOND),
                                   [CAM_A, CAM_B])
check("several microphones: neither way separates",
      window == run and not run[0], str(run))

window = vpm.speaker_source_pick([], [CAM_A, CAM_B], camera_audio=True,
                                 length_of=LENGTH.get)
saved = vpm.media_seconds
vpm.media_seconds = LENGTH.get
try:
    run = vpm.separation_source_of_run(
        Args(_camera_audio=folder), tracks_of(CAM_A, CAM_B), [CAM_A, CAM_B])
finally:
    vpm.media_seconds = saved
check("out of the cameras: the same, and the longer one",
      window == run and run[0] == CAM_B, str(run))

empty = vpm.separation_source_of_run(Args(), [], [])
check("nothing at all stays nothing", empty == ("", "nothing"),
      "%s, wanted ('', 'nothing')" % (empty,))

print("\n2. The run starts it by itself, and the switches still hold")
asked = []


def fake_run(path, count=0, **kw):
    asked.append((path, count))
    return [("SPEAKER_00", [(0.0, 4.0), (8.0, 12.0)]),
            ("SPEAKER_01", [(4.2, 7.8)])], ""


vpm.speaker_split_available = lambda deep=False: True
vpm.speaker_split_run = fake_run
vpm.media_seconds = lambda p: LENGTH.get(p, 20.0)
vpm.SPEAKER_SPLIT_OFF = False
TRACKS = tracks_of(RECORDER)


def forget_stored():
    """Empty this test's own store, and only ever its own.

    The checks below are about a machine that has not separated this
    recording before; section 5 is the one that leaves it filled.
    """
    kept = vpm.cache_folder("speakers") or ""
    for name in (os.listdir(kept) if kept else ()):
        os.unlink(os.path.join(kept, name))


def separate(args):
    del asked[:]
    forget_stored()
    return vpm.separation_for_run(args, TRACKS, {}, 0.0, 20.0,
                                  [CAM_A, CAM_B])

own, where_from = separate(Args())
check("with a source and no switch it separates",
      bool(own) and asked == [(RECORDER, 0)], str(asked))
check("and the log says where it came from", bool(where_from), where_from)

out, _w = separate(Args(no_speakers_local=True))
check("--no-speakers-local leaves it out", out == [] and asked == [],
      str(asked))

out, _w = separate(Args(dry_run=True))
check("--dry-run computes nothing", out == [] and asked == [], str(asked))

out, _w = separate(Args(speakers_local=SECOND))
check("--speakers-local names exactly that file",
      asked == [(os.path.abspath(SECOND), 0)], str(asked))

vpm.SPEAKER_SPLIT_OFF = True
out, _w = separate(Args())
check("switched off it never starts by itself", asked == [], str(asked))
out, _w = separate(Args(speakers_local=RECORDER))
check("but a named file still starts it, like the button",
      asked == [(os.path.abspath(RECORDER), 0)], str(asked))
vpm.SPEAKER_SPLIT_OFF = False

print("\n3. A no in the window reaches the run")


def window_argv(**over):
    state = {"files": [], "clip_kinds": {}, "out_folder": "",
             "dry_run": False, "multitrack": True,
             "camera_audio_only": False, "production": "P",
             "in_point": "", "out_point": "", "cut": {},
             "wide_at_edges": True, "key": "k", "preset": "p",
             "done_folder": "",
             "rows": [{"blocks": ["/x/a.wav"], "speakers": "A",
                       "camera_choice": "G.mov"},
                      {"blocks": ["/x/b.wav"], "speakers": "B",
                       "camera_choice": "H.mov"}],
             "cameras": [{"path": "/x/G.mov", "name": "Cam1"},
                         {"path": "/x/H.mov", "name": "Cam2"}]}
    state.update(over)
    return vpm.run_argv(state, "/x/assign.json")[0] or []


said_no = window_argv(speakers_wanted=False)
check("the window sends its no as a switch",
      "--no-speakers-local" in said_no,
      "%d arguments, the switches among them %s"
      % (len(said_no), [x for x in said_no if x.startswith("--")]))
said_yes = window_argv(speakers_wanted=True)
check("a yes sends nothing -- the run separates as the window does",
      "--no-speakers-local" not in said_yes,
      "%d arguments, the switches among them %s"
      % (len(said_yes), [x for x in said_yes if x.startswith("--")]))
said_nothing = window_argv()
check("and an unanswered question sends nothing either",
      "--no-speakers-local" not in said_nothing,
      "%d arguments, the switches among them %s"
      % (len(said_nothing), [x for x in said_nothing if x.startswith("--")]))

print("\n4. The same segments, the same cut list")
handed = {"source": RECORDER,
          "segments": [[label, a, b]
                       for label, parts in fake_run(RECORDER)[0]
                       for a, b in parts]}
by_window, _w = vpm.separation_for_run(
    Args(_speakers_of=handed), TRACKS, {}, 0.0, 20.0, [CAM_A, CAM_B])
by_run, _w = separate(Args())
check("both ways end with the same speaker segments",
      by_window == by_run, "%s / %s" % (by_window, by_run))

CAMERA_OF = {"SPEAKER_00": "camA.mov", "SPEAKER_01": "camB.mov"}
cut_window = vpm.build_camera_cut(by_window, 20.0, CAMERA_OF, "camA.mov")
cut_run = vpm.build_camera_cut(by_run, 20.0, CAMERA_OF, "camA.mov")
check("and with the same cut list", cut_window == cut_run,
      "%d shots" % len(cut_run))

print("\n5. What one way measured, the other reads")
forget_stored()
del asked[:]
heard = []
vpm.speaker_split_work(RECORDER, 0, lambda t, s: None, lambda: False,
                       lambda r: heard.append(r))
check("the window's road measures the recording once",
      asked == [(RECORDER, 0)] and bool(heard and heard[0][2]),
      "the model was asked %d times %s and %d voices came back, "
      "wanted once and more than none"
      % (len(asked), asked, len(heard[0][2]) if heard else 0))

del asked[:]
by_store, _w = vpm.separation_for_run(Args(), TRACKS, {}, 0.0, 20.0,
                                      [CAM_A, CAM_B])
check("and the run reads it back instead of measuring again",
      asked == [] and bool(by_store),
      "the model was asked %d times %s and %d voices came back, "
      "wanted none and more than none"
      % (len(asked), asked, len(by_store)))

# The one thing a store must never do: answer for a recording that is
# not the one it was filled from.
os.utime(RECORDER, (2000, 2000))
del asked[:]
by_fresh, _w = vpm.separation_for_run(Args(), TRACKS, {}, 0.0, 20.0,
                                      [CAM_A, CAM_B])
check("a recording written since is measured again, not read back",
      asked == [(RECORDER, 0)] and bool(by_fresh),
      "the model was asked %d times %s and %d voices came back, "
      "wanted once and more than none"
      % (len(asked), asked, len(by_fresh)))

del asked[:]
back = []
vpm.speaker_split_work(RECORDER, 0, lambda t, s: None, lambda: False,
                       lambda r: back.append(r))
check("and what the run measured, the window reads back",
      asked == [] and bool(back and back[0][2]),
      "the model was asked %d times %s and %d voices came back, "
      "wanted none and more than none"
      % (len(asked), asked, len(back[0][2]) if back else 0))

shutil.rmtree(os.environ["VPM_CACHE"], ignore_errors=True)
shutil.rmtree(folder, ignore_errors=True)
print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
