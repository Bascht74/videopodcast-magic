# -*- coding: utf-8 -*-
"""The window's own preview, before any run, shows the cut the run builds.

way_ground's production in a window per path, offscreen: plain and
Multitrack. The preview is read before Start, the window's own run goes
through, its handover is read back. Per path: both there, the preview
beginning where the last camera rolls, and against the run's cut list
the number of shots, every cut on the run's frame, every camera.
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
import subprocess
import tempfile
import time
import the_program
import way_ground as ground

began = time.time()
done = 0
bad = []
# Where the run's Timeline begins on the clock: the guest camera rolls
# last, at 10:00:05:15, thirty labels a second (way_ground).
LAST_ROLLS = ground.FRAME_OF[ground.GUEST] / 30.0


def check(name, ok, extra=""):
    """One judgement: a line in the report, and a name in bad if it fell."""
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


def child(path):
    """One window on one path; prints the preview and the run as RESULT."""
    # The model and the words are stood in for; the store and Resolve's
    # interface are the child's own, so nothing outside answers.
    os.environ.pop("VPM_NO_SPEAKER_SPLIT", None)
    store = tempfile.mkdtemp(prefix="vpm_freshcut_store_")
    nowhere = os.path.join(store, "no-resolve-here")
    os.environ.update(VPM_CACHE=store, QT_QPA_PLATFORM="offscreen",
                      RESOLVE_SCRIPT_API=nowhere, RESOLVE_SCRIPT_LIB=os.path
                      .join(nowhere, "fusionscript.so"))
    from PySide6 import QtWidgets
    app = QtWidgets.QApplication(sys.argv[:1])
    vpm = the_program.load()
    vpm.set_language("en")
    vpm.list_presets = lambda key: []
    vpm.load_api_key = lambda: ""
    vpm.speaker_split_run = lambda *a, **k: ([], "")
    vpm.speaker_split_available = lambda deep=False: True
    vpm.SPEAKER_SPLIT_OFF = False
    vpm.words_at_hand = lambda *a, **k: []
    vpm.recognise_speech = lambda *a, **k: ([], "")
    work = ground.own_folder("freshcut_" + path)
    out = os.path.join(work, "out")
    os.makedirs(out)
    os.makedirs(os.path.join(work, "project"))
    project = (ground.project_file(vpm, os.path.join(work, "project"), out)
               if path == "plain" else ground.project_plain(
                   vpm, os.path.join(work, "project"), out, multitrack=True))
    seen = {"start": None, "cut": None}
    step = {"n": 0, "last": None, "since": 0.0}

    def look(w):
        """The preview now: its start on the clock, its cut, measuring."""
        st = w.resolve_sheet.state
        cut = [(a, b, who) for a, b, who
               in ((st.get("cut_numbers") or {}).get("cut") or [])]
        return ((st.get("cut_data") or {}).get("start_s"), cut,
                bool(st.get("speakers_measuring")))

    def answer(w):
        """Open Resolve cut, and keep the preview once it stood 1.5 s."""
        if w is None:
            return "the window"
        at = [k for k in range(w.tabs.count())
              if w.tabs.tabText(k).startswith(vpm.T('Resolve cut'))]
        if not at:
            return "the Resolve cut tab"
        if step["n"] == 0:
            w.tabs.setCurrentIndex(at[0])
            step["n"] = 1
            return "the preview settling"
        now = look(w)
        if now != step["last"]:
            step["last"], step["since"] = now, time.time()
        if now[2] or not now[1] or time.time() - step["since"] <= 1.5:
            return "the preview settling"
        seen["start"], seen["cut"] = now[0], now[1]
        return ""

    keep = ground.window_answered_run(vpm, app, project, {}, answer)
    made = ground.handover(out) or {}
    seen.update(why=keep["why"], unanswered=keep["unanswered"],
                ended=keep["ended"], run_start=made.get("start_s"),
                fps=made.get("fps"),
                run_cut=[(c.get("start"), c.get("end"), c.get("camera"))
                         for c in (made.get("cut") or [])])
    print("RESULT " + json.dumps(seen))
    shutil.rmtree(work, ignore_errors=True)
    shutil.rmtree(store, ignore_errors=True)


def frames(start, cut, fps):
    """A cut as (first frame, frame after, camera) on the clock."""
    return [(int(round((float(start) + a) * fps)),
             int(round((float(start) + b) * fps)), who)
            for a, b, who in cut or ()]


def both(s):
    """(preview, run) as frames on the clock, at the run's rate."""
    if s.get("start") is None or s.get("run_start") is None:
        return [], []
    fps = float(s.get("fps") or 30.0)
    return (frames(s["start"], s.get("cut"), fps),
            frames(s["run_start"], s.get("run_cut"), fps))


def there_line(s):
    """The evidence for preview and run both being there."""
    return ("preview %s shots from %s; the run ended %s and wrote %d shots"
            " from %s; %s" % (len(s.get("cut") or []), s.get("start"),
                              s.get("ended"), len(s.get("run_cut") or []),
                              s.get("run_start"), s.get("unanswered")
                              or s.get("why") or "no wait"))


def start_line(s):
    """The evidence for where the preview begins."""
    return "the preview begins at %s s on the clock, wanted %.3f s" % (
        s.get("start"), LAST_ROLLS)


def count_line(s):
    """The evidence for the number of shots."""
    preview, run = both(s)
    return "%d shots in the preview, %d in the run" % (len(preview), len(run))


def frame_line(s):
    """The first shot whose frames differ, or that none does."""
    preview, run = both(s)
    for i, (p, r) in enumerate(zip(preview, run), 1):
        if p[:2] != r[:2]:
            return ("shot %d: frames %d-%d in the preview, %d-%d in the run"
                    % (i, p[0], p[1], r[0], r[1]))
    return "%d shots against %d, the shared ones on the same frames" % (
        len(preview), len(run))


def camera_line(s):
    """The first shot on another camera, or that none is."""
    preview, run = both(s)
    for i, (p, r) in enumerate(zip(preview, run), 1):
        if p[2] != r[2]:
            return "shot %d: %s in the preview, %s in the run" % (i, p[2],
                                                                   r[2])
    return "%d shots against %d, the shared ones on the same camera" % (
        len(preview), len(run))


def same_frames(s):
    """Whether every shot of the preview starts and ends on the run's."""
    preview, run = both(s)
    return bool(run) and [p[:2] for p in preview] == [r[:2] for r in run]


def same_cameras(s):
    """Whether every shot of the preview shows the run's camera."""
    preview, run = both(s)
    return bool(run) and [p[2] for p in preview] == [r[2] for r in run]


if len(sys.argv) > 2 and sys.argv[1] == "--path":
    child(sys.argv[2])
    sys.exit(0)

if ground.missing():
    print("SKIPPED: " + ground.missing())
    stop()

# Both windows at once, each in a child: two windows in one process
# would share what gui() leaves behind. Each child waits on standstill.
work = tempfile.mkdtemp(prefix="vpm_freshcut_")
kids = {}
for path in ("plain", "multi"):
    log = open(os.path.join(work, path + ".txt"), "w+", encoding="utf-8")
    kids[path] = (subprocess.Popen(
        [sys.executable, os.path.abspath(__file__), "--path", path],
        stdout=log, stderr=subprocess.STDOUT), log)
seen = {}
for path, (kid, log) in kids.items():
    try:
        kid.wait(timeout=400)
    except subprocess.TimeoutExpired:
        kid.kill()
        kid.wait()
    log.seek(0)
    said = log.read()
    log.close()
    rows = [x for x in said.splitlines() if x.startswith("RESULT ")]
    seen[path] = json.loads(rows[-1][7:]) if rows else {
        "why": "the child ended with %s and no result: %s"
        % (kid.returncode, " / ".join(said.strip().splitlines()[-3:])[-200:])}
shutil.rmtree(work, ignore_errors=True)

plain, multi = seen["plain"], seen["multi"]
print("1. Plain: one recording, its stored separation")
check("plain: a preview before Start, and the run's cut list after",
      bool(plain.get("cut")) and bool(plain.get("run_cut")),
      there_line(plain))
check("plain: the preview begins where the last camera rolls",
      plain.get("start") is not None
      and abs(float(plain["start"]) - LAST_ROLLS) < 0.001, start_line(plain))
check("plain: the preview has as many shots as the run",
      bool(plain.get("run_cut"))
      and len(plain.get("cut") or []) == len(plain["run_cut"]),
      count_line(plain))
check("plain: every cut of the preview on the run's frame",
      same_frames(plain), frame_line(plain))
check("plain: every shot of the preview on the run's camera",
      same_cameras(plain), camera_line(plain))

print("\n2. Multitrack: three recordings, the tick set")
check("Multitrack: a preview before Start, and the run's cut list after",
      bool(multi.get("cut")) and bool(multi.get("run_cut")),
      there_line(multi))
check("Multitrack: the preview begins where the last camera rolls",
      multi.get("start") is not None
      and abs(float(multi["start"]) - LAST_ROLLS) < 0.001, start_line(multi))
check("Multitrack: the preview has as many shots as the run",
      bool(multi.get("run_cut"))
      and len(multi.get("cut") or []) == len(multi["run_cut"]),
      count_line(multi))
check("Multitrack: every cut of the preview on the run's frame",
      same_frames(multi), frame_line(multi))
check("Multitrack: every shot of the preview on the run's camera",
      same_cameras(multi), camera_line(multi))
stop()
