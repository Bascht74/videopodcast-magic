# -*- coding: utf-8 -*-
"""Opening Resolve cut asks Resolve and shows the cut by voice, on both paths.

way_ground's production opened in a window of its own per path, offscreen:
plain -- one recording, the stored separation -- and Multitrack -- three
recordings, ticked. Per path: the tab is there, the first look asks Resolve
and says its answer, the preview shows each turn on its voice's camera, a
second look measures nothing again. The limit: the run is not started.
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
# Programme second 0 on the clock: the wide camera rolls there, at
# 10:00:00:00, thirty labels a second (way_ground).
ORIGIN = ground.FRAME_OF[ground.WIDE] / 30.0 - ground.ROLLS[ground.WIDE]


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
    """One window on one path; prints what it saw as one RESULT line."""
    # The model and the words are stood in for; the store and Resolve's
    # interface are the child's own, so nothing outside answers.
    os.environ.pop("VPM_NO_SPEAKER_SPLIT", None)
    store = tempfile.mkdtemp(prefix="vpm_cuttab_store_")
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
    work = ground.own_folder("cuttab_" + path)
    out = os.path.join(work, "out")
    os.makedirs(out)
    os.makedirs(os.path.join(work, "project"))
    project = (ground.project_file(vpm, os.path.join(work, "project"), out)
               if path == "plain" else ground.project_plain(
                   vpm, os.path.join(work, "project"), out, multitrack=True))
    seen = {"tab": False, "said_before": None, "said": None, "kicks": [],
            "measures": [], "cut": [], "zero": None}
    step = {"n": 0, "at": None, "last": None, "since": 0.0}
    answer_text = vpm.T('Resolve does not answer -- see Settings')

    def look(w):
        """What the sheet shows now: answer, cut, zero, measuring."""
        rs = w.resolve_sheet
        said = any(x.text() == answer_text and x.isVisibleTo(rs)
                   for x in rs.findChildren(QtWidgets.QLabel))
        cut = []
        for x in rs.findChildren(QtWidgets.QWidget):
            if hasattr(x, "cut") and hasattr(x, "audio_offset"):
                cut = [(a, b, who) for a, b, who in (x.cut or [])]
        zero = (rs.state.get("cut_data") or {}).get("start_s")
        return said, cut, zero, bool(rs.state.get("speakers_measuring"))

    def counted(rs, name, into):
        """Wrap the sheet's own *name*, counting each call into *into*."""
        real = getattr(rs, name)

        def wrapped(*a, **k):
            """The sheet's call, counted and handed on."""
            into.append(time.time())
            return real(*a, **k)
        setattr(rs, name, wrapped)

    def settled(w):
        """True once the sheet stood unchanged for 1.5 s, not measuring."""
        now = look(w)
        if now != step["last"]:
            step["last"], step["since"] = now, time.time()
        return not now[3] and time.time() - step["since"] > 1.5

    def answer(w):
        """Open the tab, let it settle, look away and back, settle again."""
        if w is None:
            return "the window"
        at = [k for k in range(w.tabs.count())
              if w.tabs.tabText(k).startswith(vpm.T('Resolve cut'))]
        if not at:
            return "the Resolve cut tab"
        if step["n"] == 0:
            seen["tab"], seen["said_before"] = True, look(w)[0]
            counted(w.resolve_sheet, "resolve_check_run_kick_off",
                    seen["kicks"])
            counted(w.resolve_sheet, "speaker_measure", seen["measures"])
            w.tabs.setCurrentIndex(at[0])
            step["n"] = 1
            return "the first look settling"
        if not settled(w):
            return "the look settling"
        if step["n"] == 1:
            seen["said"], seen["cut"], seen["zero"], _m = look(w)
            seen["first"] = [len(seen["kicks"]), len(seen["measures"])]
            w.tabs.setCurrentIndex(0)
            w.tabs.setCurrentIndex(at[0])
            step["n"], step["last"] = 2, None
            return "the second look settling"
        return ""

    keep = ground.window_answered_run(vpm, app, project, {}, answer,
                                      run=False)
    seen.update(why=keep["why"], unanswered=keep["unanswered"],
                kicks=len(seen["kicks"]), measures=len(seen["measures"]))
    print("RESULT " + json.dumps(seen))
    shutil.rmtree(work, ignore_errors=True)
    shutil.rmtree(store, ignore_errors=True)


def astray(seen):
    """(turns judged, those not on their voice's camera) in the preview."""
    cut, zero, judged, off = seen.get("cut") or [], seen.get("zero"), 0, []
    if not cut or zero is None:
        return 0, ["no cut or no zero drawn"]
    for who in sorted(ground.TURNS):
        for a, b in ground.TURNS[who]:
            t = ORIGIN + (a + b) / 2.0 - float(zero)
            shown = [c for s, e, c in cut if s <= t < e]
            if not shown:
                continue
            judged += 1
            if os.path.splitext(shown[0])[0] != ground.SEAT[who]:
                off.append("%s %.1f-%.1f on %s" % (who, a, b, shown[0]))
    return judged, off


if len(sys.argv) > 2 and sys.argv[1] == "--path":
    child(sys.argv[2])
    sys.exit(0)

if ground.missing():
    print("SKIPPED: " + ground.missing())
    stop()

# Both windows at once, each in a child: two windows in one process
# would share what gui() leaves behind. Each child waits on standstill.
work = tempfile.mkdtemp(prefix="vpm_cuttab_")
kids = {}
for path in ("plain", "multi"):
    log = open(os.path.join(work, path + ".txt"), "w+", encoding="utf-8")
    kids[path] = (subprocess.Popen(
        [sys.executable, os.path.abspath(__file__), "--path", path],
        stdout=log, stderr=subprocess.STDOUT), log)
seen = {}
for path, (kid, log) in kids.items():
    try:
        kid.wait(timeout=240)
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


def tab_line(s):
    """The evidence for the tab being offered, for a failure line."""
    return "tab %s, %s" % ("there" if s.get("tab") else "missing",
                           s.get("unanswered") or s.get("why") or "no wait")


def ask_line(s):
    """The evidence for the Resolve question, for a failure line."""
    return ("before the look said %s, after %s; asked %s time(s) on the "
            "first look" % (s.get("said_before"), s.get("said"),
                            (s.get("first") or ["-"])[0]))


def voice_line(s):
    """The evidence for the preview's cameras, for a failure line."""
    judged, off = astray(s)
    return ("%d turns judged, %d astray: %s -- zero %s, %d shots"
            % (judged, len(off), off[:3], s.get("zero"),
               len(s.get("cut") or [])))


def again_line(s):
    """The evidence for the second look, for a failure line."""
    return ("measured %s time(s) after the first look, %s after the second"
            % ((s.get("first") or ["-", "-"])[1], s.get("measures")))


# At least eight turns judged: the guest's first ends before the run's
# Timeline begins, so a preview that starts there judges the other eight.
plain, multi = seen["plain"], seen["multi"]
print("1. Plain: one recording, its stored separation")
check("plain: the window offers Resolve cut once the project is open",
      plain.get("tab") is True, tab_line(plain))
check("plain: the first look at Resolve cut asks Resolve and says so",
      plain.get("said_before") is False and plain.get("said") is True
      and (plain.get("first") or [0])[0] == 1, ask_line(plain))
check("plain: the preview shows each turn on its voice's camera",
      astray(plain)[0] >= 8 and not astray(plain)[1], voice_line(plain))
check("plain: a second look at the tab measures nothing again",
      bool(plain.get("first"))
      and plain.get("measures") == plain["first"][1], again_line(plain))

print("\n2. Multitrack: three recordings, the tick set")
check("Multitrack: the window offers Resolve cut once the project is open",
      multi.get("tab") is True, tab_line(multi))
check("Multitrack: the first look at Resolve cut asks Resolve and says so",
      multi.get("said_before") is False and multi.get("said") is True
      and (multi.get("first") or [0])[0] == 1, ask_line(multi))
check("Multitrack: the preview shows each turn on its voice's camera",
      astray(multi)[0] >= 8 and not astray(multi)[1], voice_line(multi))
check("Multitrack: a second look at the tab measures nothing again",
      bool(multi.get("first"))
      and multi.get("measures") == multi["first"][1], again_line(multi))
stop()
