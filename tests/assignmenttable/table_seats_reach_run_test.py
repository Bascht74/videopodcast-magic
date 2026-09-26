# -*- coding: utf-8 -*-
"""The camera a voice is set on in the table is its camera in the run.

way_ground's production, all three recordings, the tick on, each voice
set crosswise to a camera the table does not propose. A real run per
door: the line with an --assign order written as values, the window
answered in its own choosers and started. Per door: a handover, each
camera carrying exactly the speaker set on it. Then both doors lay the
same tracks into each camera file and cut the same shots. The limit:
multitrack only, where the table's camera travels to the run.
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
import json
import shutil
import tempfile
import time
import the_program
import way_ground as ground

SCRIPT = the_program.SCRIPT
began = time.time()
done = 0
bad = []


def check(name, ok, extra=""):
    global done
    done += 1
    print("  %-58s %s %s" % (name, "ok" if ok else "FAIL", extra))
    if not ok:
        bad.append("%s [%s]" % (name, extra or "no numbers"))


def stop():
    """Nothing further can be asked, so count what there is and go."""
    print("\n%d checks in %.2f s" % (done, time.time() - began))
    print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
    sys.exit(1 if bad else 0)


if ground.missing():
    print("SKIPPED: " + ground.missing())
    stop()

STORE = tempfile.mkdtemp(prefix="vpm_way_store_")
os.environ["VPM_CACHE"] = STORE
os.environ["QT_QPA_PLATFORM"] = "offscreen"
from PySide6 import QtWidgets
app = QtWidgets.QApplication(sys.argv[:1])
vpm = the_program.load()
vpm.set_language("en")
vpm.list_presets = lambda key: []
vpm.load_api_key = lambda: ""
# Nothing is written down from speech: that would fetch a model, and
# no judgement here is about words.
vpm.words_at_hand = lambda *a, **k: []
vpm.recognise_speech = lambda *a, **k: ([], "")

# Crosswise: the table proposes each voice's own camera by its name,
# so an answer that arrives cannot have come from the proposal.
ROW_OF = {"Guest": "Guest_Take0031A.wav", "Presenter": "Presenter_REC00031.wav"}
SET_ON = {"Guest": ground.PRES, "Presenter": ground.GUEST}
# Who each camera carries once the run is done: the truth.
CARRIES = {ground.PRES: ["Guest"], ground.GUEST: ["Presenter"],
           ground.WIDE: []}
AS_THE_WINDOW = ["--lufs", "-16", "--speech-language", "eng"]


def order(folder):
    """The --assign order a person writes by hand, as values."""
    rec = ground.recordings()
    _sound, pictures = ground.material()
    plan = {"format": vpm.FILE_FORMAT, "created_by": "test",
            "production": ground.PRODUCTION,
            "tracks_of": [
                {"audio": rec[0], "blocks": [rec[0]], "speakers": "Guest",
                 "camera": ground.media(SET_ON["Guest"]),
                 "camera_audio": False},
                {"audio": rec[1], "blocks": rec[1:], "speakers": "Presenter",
                 "camera": ground.media(SET_ON["Presenter"]),
                 "camera_audio": False}],
            "cameras": [{"video": p, "name": os.path.splitext(
                os.path.basename(p))[0]} for p in pictures]}
    path = os.path.join(folder, "assign.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(plan, f, ensure_ascii=False, indent=1)
    return path


def carried(d):
    """Camera stem -> the speakers its handover entry names."""
    return dict((os.path.splitext(os.path.basename(c.get("source") or ""))
                 [0], sorted(c.get("speakers") or []))
                for c in (d or {}).get("cameras") or [])


def tracks(d):
    """Camera stem -> the tracks laid into its file."""
    return dict((os.path.splitext(os.path.basename(c.get("source") or ""))
                 [0], c.get("audio_tracks"))
                for c in (d or {}).get("cameras") or [])


def shots(d):
    """The shots of a handover as (start, end, camera stem)."""
    stem = dict((c.get("camera"), os.path.splitext(os.path.basename(
        c.get("source") or ""))[0]) for c in (d or {}).get("cameras") or [])
    return [(e.get("start"), e.get("end"), stem.get(e.get("camera")))
            for e in (d or {}).get("cut") or []]


proposed = {}


def answer(window):
    """Set each row's camera crosswise, one at a time; "" once all stand.

    What the table proposed before anything was set is kept, for the
    red line. One choice per call: an answer rebuilds the table.
    """
    boxes = ground.fields(window, vpm.T("belongs to"))
    rows = dict((who, next((b for k, b in boxes.items()
                            if k.startswith(ROW_OF[who])), None))
                for who in ROW_OF)
    if None in rows.values():
        return "the rows of %s" % sorted(ROW_OF.values())
    for who, box in sorted(rows.items()):
        proposed.setdefault(who, os.path.basename(str(box.currentData())))
        want = ground.media(SET_ON[who])
        if box.currentData() != want:
            box.setCurrentIndex(box.findData(want))
            return "%s set on %s" % (who, SET_ON[who])
    return ""


WORK = ground.own_folder("seats")
OUT_LINE = os.path.join(WORK, "line")
OUT_WINDOW = os.path.join(WORK, "window")
os.makedirs(OUT_WINDOW)
os.makedirs(os.path.join(WORK, "project"))
_sound, PICTURES = ground.material()

print("1. The command line, with an order written by hand")
code, said, stuck = ground.line_run(
    [sys.executable, SCRIPT, "--without-auphonic", "--multitrack",
     "--assign", order(WORK), "--no-speech-recognition", "--out", OUT_LINE,
     ground.NO_EDGES] + AS_THE_WINDOW + ground.recordings() + PICTURES,
    STORE)
by_line = ground.handover(OUT_LINE)
tail = [x.strip() for x in said.replace(WORK, "<work>").splitlines()
        if x.strip()][-3:]
check("the line's run came back with 0 and wrote its handover",
      not stuck and code == 0 and by_line is not None,
      "return code %s%s, handover %s -- the log ends: %s"
      % (code, " after standing still" if stuck else "",
         "there" if by_line else "missing", " / ".join(tail)[-240:]))
check("at the line, each camera carries the speaker its order sets",
      carried(by_line) == CARRIES,
      "%s, wanted %s" % (carried(by_line), CARRIES))

print("\n2. The window, answered in its own table and started")
PROJECT = ground.project_plain(vpm, os.path.join(WORK, "project"),
                               OUT_WINDOW)
kept = ground.window_answered_run(vpm, app, PROJECT, {}, answer)
by_window = ground.handover(OUT_WINDOW)
check("the window's Start ran a run to its end, with a handover",
      kept["ended"] and not kept["why"] and by_window is not None,
      "loop %s, %s, handover %s"
      % ("came back" if kept["ended"] else "never came back",
         kept["why"] or "nothing given up",
         "there" if by_window else "missing"))
check("from the window, each camera carries the speaker set on it",
      carried(by_window) == CARRIES,
      "%s, wanted %s; the table had proposed %s; answers %s"
      % (carried(by_window), CARRIES, proposed,
         ("never stood: " + kept["unanswered"]) if kept["unanswered"]
         else "stood"))

print("\n3. The two doors against each other")
check("both doors lay the same tracks into each camera file",
      bool(tracks(by_line)) and tracks(by_line) == tracks(by_window),
      "line %s -- window %s" % (tracks(by_line), tracks(by_window)))
check("both doors cut the same shots to the same cameras",
      bool(shots(by_line)) and shots(by_line) == shots(by_window),
      "line %s -- window %s" % (shots(by_line), shots(by_window)))

shutil.rmtree(WORK, ignore_errors=True)
shutil.rmtree(STORE, ignore_errors=True)
stop()
