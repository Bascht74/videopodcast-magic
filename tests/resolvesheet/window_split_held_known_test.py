# -*- coding: utf-8 -*-
"""Resolve cut measures no speakers while a stored separation still holds.

way_ground's plain project on a copied recording, one window per case:
unchanged -- the separation comes back, the first look measures nothing;
file changed after opening -- measured; stored by other separation code
-- it comes back and is measured. The limit: no run, and no model here,
so a changed model mark is not among the cases."""
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


def project_for(vpm, work, out, case):
    """The plain project on a copy of its recording; hands back both paths.

    "code" writes another recipe mark into the stored separation, as
    other separation code would have stamped it.
    """
    source = ground.media(ground.HEARD_IN)
    copy = os.path.join(work, "rec", os.path.basename(source))
    os.makedirs(os.path.dirname(copy))
    shutil.copy2(source, copy)          # the mtime comes along
    path = ground.project_file(vpm, os.path.join(work, "project"), out)
    with open(path, encoding="utf-8") as f:
        d = json.loads(f.read().replace(json.dumps(source)[1:-1],
                                        json.dumps(copy)[1:-1]))
    if case == "code":
        d["speakers"]["recipe"] = "0" * 12
    with open(path, "w", encoding="utf-8") as f:
        json.dump(d, f, ensure_ascii=False, indent=1)
    return path, copy


def child(case):
    """One window, one case; prints what it saw as one RESULT line."""
    os.environ.pop("VPM_NO_SPEAKER_SPLIT", None)
    store = tempfile.mkdtemp(prefix="vpm_splitheld_store_")
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
    work = ground.own_folder("splitheld_" + case)
    out = os.path.join(work, "out")
    os.makedirs(out)
    os.makedirs(os.path.join(work, "project"))
    project, copy = project_for(vpm, work, out, case)
    seen = {"measures": [], "kept": None}
    step = {"n": 0, "last": None, "since": 0.0}

    def settled(w):
        """True once the sheet stood unchanged for 1.5 s, not measuring."""
        rs = w.resolve_sheet
        now = (bool(rs.state.get("speakers_measuring")),
               bool(rs.state.get("speakers_measured")), len(seen["measures"]))
        if now != step["last"]:
            step["last"], step["since"] = now, time.time()
        return not now[0] and time.time() - step["since"] > 1.5

    def answer(w):
        """Change the file where asked, open the tab, let it settle."""
        if w is None:
            return "the window"
        at = [k for k in range(w.tabs.count())
              if w.tabs.tabText(k).startswith(vpm.T('Resolve cut'))]
        if not at:
            return "the Resolve cut tab"
        rs = w.resolve_sheet
        if step["n"] == 0:
            seen["kept"] = sorted(rs.state.get("speakers_by") or {})
            if case == "file":
                t = os.stat(copy).st_mtime + 60
                os.utime(copy, (t, t))
            real = rs.speaker_measure

            def counted(*a, **k):
                """The sheet's measuring, counted and handed on."""
                seen["measures"].append(time.time())
                return real(*a, **k)
            rs.speaker_measure = counted
            w.tabs.setCurrentIndex(at[0])
            step["n"] = 1
            return "the look settling"
        return "" if settled(w) else "the look settling"

    keep = ground.window_answered_run(vpm, app, project, {}, answer,
                                      run=False)
    seen.update(why=keep["why"], unanswered=keep["unanswered"],
                measures=len(seen["measures"]),
                kept=[os.path.basename(p) for p in seen["kept"] or ()])
    print("RESULT " + json.dumps(seen))
    shutil.rmtree(work, ignore_errors=True)
    shutil.rmtree(store, ignore_errors=True)


if len(sys.argv) > 2 and sys.argv[1] == "--case":
    child(sys.argv[2])
    sys.exit(0)

if ground.missing():
    print("SKIPPED: " + ground.missing())
    stop()

# One window per case, each in a child: two windows in one process would
# share what gui() leaves behind. Each child waits on standstill.
work = tempfile.mkdtemp(prefix="vpm_splitheld_")
kids = {}
for case in ("same", "file", "code"):
    log = open(os.path.join(work, case + ".txt"), "w+", encoding="utf-8")
    kids[case] = (subprocess.Popen(
        [sys.executable, os.path.abspath(__file__), "--case", case],
        stdout=log, stderr=subprocess.STDOUT), log)
seen = {}
for case, (kid, log) in kids.items():
    try:
        kid.wait(timeout=240)
    except subprocess.TimeoutExpired:
        kid.kill()
        kid.wait()
    log.seek(0)
    said = log.read()
    log.close()
    rows = [x for x in said.splitlines() if x.startswith("RESULT ")]
    seen[case] = json.loads(rows[-1][7:]) if rows else {
        "why": "the child ended with %s and no result: %s"
        % (kid.returncode, " / ".join(said.strip().splitlines()[-3:])[-200:])}
shutil.rmtree(work, ignore_errors=True)
HEARD = [os.path.basename(ground.media(ground.HEARD_IN))]


def line(s):
    """The evidence for one case, for a failure line."""
    return ("measured %s time(s) on the first look; separations in the window %s; "
            "%s" % (s.get("measures"), s.get("kept"),
                    s.get("unanswered") or s.get("why") or "settled"))


same, changed, code = seen["same"], seen["file"], seen["code"]
print("1. Unchanged: file, measurement and code as stored")
check("unchanged: the stored separation comes back with the project",
      same.get("kept") == HEARD, line(same))
check("unchanged: the first look at Resolve cut measures no speakers",
      same.get("measures") == 0, line(same))

print("\n2. The recording changed after the project was opened")
check("file changed: the first look at Resolve cut measures the speakers",
      changed.get("measures") == 1, line(changed))

print("\n3. The separation was stored by other separation code")
check("code changed: the stored separation still comes back",
      code.get("kept") == HEARD, line(code))
check("code changed: the first look at Resolve cut measures the speakers",
      code.get("measures") == 1, line(code))
stop()
