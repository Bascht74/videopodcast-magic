# -*- coding: utf-8 -*-
"""The preview, the dry run's handover and the run cut the same shots.

way_ground's production, per case two offscreen windows in children:
one keeps the preview once it stands and presses Dry run, one Start.
The dry run's handover is any JSON in its own store (VPM_CACHE), or the
result one wraps, with a cut list and a start; the run's lies in out. Cases:
plain, Multitrack, Multitrack with In and Out, a stored separation, one
name on two recordings set to two cameras. Per case: preview and run
there, the run on the preview's frames and cameras, a dry-run handover
there, and it on the preview's frames and cameras too.
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
CASES = ("plain", "multitrack", "marks", "separation", "two_cameras")
# In from where every camera runs, Out back from where the first stops.
MARKS = {"in_point": "+0:00:10", "out_point": "-0:00:10"}


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


def project(vpm, case, folder, out):
    """The project file of *case*, written into *folder*."""
    if case == "two_cameras":
        # The presenter's two recordings under one name, each set to a
        # camera of its own: one person, two cameras.
        seat = {"Guest_Take0031A": ("Guest", ground.GUEST),
                "Presenter_REC00031": ("Presenter", ground.PRES),
                "Presenter_REC00032": ("Presenter", ground.WIDE)}
        return ground.project_plain(vpm, folder, out, extra={
            "assignment": dict(("audio:" + ground.media(rec), [
                who, os.path.basename(ground.media(cam))])
                for rec, (who, cam) in seat.items())})
    if case in ("plain", "multitrack", "marks"):
        return ground.project_plain(
            vpm, folder, out, multitrack=case != "plain",
            extra=MARKS if case == "marks" else None)
    return ground.project_file(vpm, folder, out)


def handovers_in(store):
    """Every JSON under *store* shaped as a handover: a cut and a start.

    Newest first; each as (its name under the store, its start, fps,
    its cut as (start, end, camera)). Nothing else is asked of the
    store, so it may keep the dry run's work in any shape it likes.
    """
    found = []
    for root, _dirs, names in os.walk(store):
        for name in names:
            if not name.endswith(".json"):
                continue
            path = os.path.join(root, name)
            try:
                with open(path, encoding="utf-8") as f:
                    d = json.load(f)
            except (OSError, ValueError):
                continue
            # The store keeps each entry in an envelope; its result is
            # what the stage worked out.
            if isinstance(d, dict) and isinstance(d.get("result"), dict):
                d = d["result"]
            if not (isinstance(d, dict) and isinstance(d.get("cut"), list)
                    and d.get("start_s") is not None):
                continue
            found.append((os.path.getmtime(path),
                          os.path.relpath(path, store), d.get("start_s"),
                          d.get("fps"), [(c.get("start"), c.get("end"),
                                          c.get("camera"))
                                         for c in d["cut"]]))
    return [x[1:] for x in sorted(found, reverse=True)]


def child(case, press):
    """One window on *case*; the preview and what *press* left, as RESULT."""
    # The model and the words are stood in for; the store and Resolve's
    # interface are the child's own, so nothing outside answers.
    os.environ.pop("VPM_NO_SPEAKER_SPLIT", None)
    store = tempfile.mkdtemp(prefix="vpm_threecuts_store_")
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
    work = ground.own_folder("threecuts_%s_%s" % (case, press[0]))
    out = os.path.join(work, "out")
    os.makedirs(out)
    os.makedirs(os.path.join(work, "project"))
    path = project(vpm, case, os.path.join(work, "project"), out)
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
        # Why the window holds its buttons, if it does, for the red line.
        seen["held"] = [x.toolTip().replace("\n", " / ")[:200]
                        for x in w.findChildren(QtWidgets.QWidget)
                        if x.toolTip().startswith(vpm.T("Not ready yet:"))
                        ][:1]
        return ""

    keep = ground.window_answered_run(vpm, app, path, {}, answer,
                                      press=press)
    seen.update(why=keep["why"], unanswered=keep["unanswered"],
                ended=keep["ended"])
    if press == "Start":
        made = ground.handover(out) or {}
        seen.update(run_start=made.get("start_s"), fps=made.get("fps"),
                    run_cut=[(c.get("start"), c.get("end"), c.get("camera"))
                             for c in (made.get("cut") or [])])
    else:
        found = handovers_in(store)
        stored = []
        for root, _dirs, names in os.walk(store):
            stored += names
        seen.update(stored=len(stored), dry=found[0] if found else None,
                    dry_count=len(found),
                    dry_said=[x for x in keep["log"] if x.strip()][-1:])
    print("RESULT " + json.dumps(seen))
    shutil.rmtree(work, ignore_errors=True)
    shutil.rmtree(store, ignore_errors=True)


def frames(start, cut, fps):
    """A cut as (first frame, frame after, camera) on the clock."""
    return [(int(round((float(start) + a) * fps)),
             int(round((float(start) + b) * fps)), who)
            for a, b, who in cut or ()]


def preview_of(s):
    """The preview as frames on the clock, at the run's rate."""
    if s["dry"].get("start") is None:
        return []
    return frames(s["dry"]["start"], s["dry"].get("cut"), rate(s))


def rate(s):
    """The run's frame rate, 30 where it wrote none."""
    return float(s["run"].get("fps") or 30.0)


def run_of(s):
    """The run's cut list as frames on the clock."""
    if s["run"].get("run_start") is None:
        return []
    return frames(s["run"]["run_start"], s["run"].get("run_cut"), rate(s))


def dry_of(s):
    """The dry run's handover cut as frames on the clock."""
    found = s["dry"].get("dry")
    if not found:
        return []
    _name, start, _fps, cut = found
    return frames(start, cut, rate(s)) if start is not None else []


def first_apart(one, other, names):
    """(the same, evidence): the first shot where two cuts part."""
    for i, (p, r) in enumerate(zip(one, other), 1):
        if p != r:
            return False, ("shot %d: %d-%d %s in the %s, %d-%d %s in the %s"
                           % (i, p[0], p[1], p[2], names[0], r[0], r[1],
                              r[2], names[1]))
    if len(one) != len(other) or not one:
        return False, "%d shots in the %s, %d in the %s" % (
            len(one), names[0], len(other), names[1])
    return True, "%d shots, each on the same frames and camera" % len(one)


def there_line(s):
    """The evidence for preview and run both being there."""
    return ("preview %d shots from %s (%s); the run ended %s and wrote %d "
            "shots from %s (%s)" % (
                len(s["dry"].get("cut") or []), s["dry"].get("start"),
                s["dry"].get("unanswered") or s["dry"].get("why")
                or "stood", s["run"].get("ended"),
                len(s["run"].get("run_cut") or []), s["run"].get("run_start"),
                "; ".join([s["run"].get("why") or "ran"]
                          + (s["run"].get("held") or []))))


def dry_line(s):
    """The evidence for the dry run's handover being there."""
    d = s["dry"]
    found = d.get("dry")
    if found:
        return "%s in the dry run's store, %d shots from %s" % (
            found[0], len(found[3] or []), found[1])
    return ("no handover with a cut list in the dry run's store: %s files "
            "there, the dry run ended %s, the last it said %r%s" % (
                d.get("stored"), d.get("ended"),
                "".join(d.get("dry_said") or [])[-80:],
                "; " + d["why"] if d.get("why") else ""))


if len(sys.argv) > 3 and sys.argv[1] == "--case":
    child(sys.argv[2], sys.argv[3])
    sys.exit(0)

if ground.missing():
    print("SKIPPED: " + ground.missing())
    stop()

# Every window in a child: two in one process would share what gui()
# leaves behind. Each child waits on standstill; five at a time.
work = tempfile.mkdtemp(prefix="vpm_threecuts_")
orders = [(case, press) for case in CASES for press in ("Dry run", "Start")]
seen = dict((case, {}) for case in CASES)
running = []
while orders or running:
    while orders and len(running) < 5:
        case, press = orders.pop(0)
        log = open(os.path.join(work, "%s_%s.txt" % (case, press[0])), "w+",
                   encoding="utf-8")
        running.append((case, press, log, subprocess.Popen(
            [sys.executable, os.path.abspath(__file__), "--case", case,
             press], stdout=log, stderr=subprocess.STDOUT)))
    case, press, log, kid = running.pop(0)
    try:
        kid.wait(timeout=400)
    except subprocess.TimeoutExpired:
        kid.kill()
        kid.wait()
    log.seek(0)
    said = log.read()
    log.close()
    rows = [x for x in said.splitlines() if x.startswith("RESULT ")]
    seen[case]["dry" if press == "Dry run" else "run"] = (
        json.loads(rows[-1][7:]) if rows else {
            "why": "the child ended with %s and no result: %s"
            % (kid.returncode,
               " / ".join(said.strip().splitlines()[-3:])[-200:])})
shutil.rmtree(work, ignore_errors=True)


def both_there(s):
    """Whether the preview and the run's cut list are both there."""
    return bool(preview_of(s)) and bool(run_of(s))


s = seen["plain"]
print("1. Plain: three recordings, no answers")
check("plain: a preview before the dry run, and the run's cut list",
      both_there(s), there_line(s))
ok, why = first_apart(preview_of(s), run_of(s), ("preview", "run"))
check("plain: the run cuts every shot the preview shows", ok, why)
check("plain: the dry run leaves a handover with a cut list",
      bool(dry_of(s)), dry_line(s))
ok, why = first_apart(preview_of(s), dry_of(s), ("preview", "dry run"))
check("plain: the dry run's handover cuts every shot of the preview",
      ok, why)

s = seen["multitrack"]
print("\n2. Multitrack: three recordings, the tick set")
check("Multitrack: a preview before the dry run, and the run's cut list",
      both_there(s), there_line(s))
ok, why = first_apart(preview_of(s), run_of(s), ("preview", "run"))
check("Multitrack: the run cuts every shot the preview shows", ok, why)
check("Multitrack: the dry run leaves a handover with a cut list",
      bool(dry_of(s)), dry_line(s))
ok, why = first_apart(preview_of(s), dry_of(s), ("preview", "dry run"))
check("Multitrack: the dry run's handover cuts every shot of the preview",
      ok, why)

s = seen["marks"]
print("\n3. Multitrack with In and Out")
check("In and Out: a preview before the dry run, and the run's cut list",
      both_there(s), there_line(s))
ok, why = first_apart(preview_of(s), run_of(s), ("preview", "run"))
check("In and Out: the run cuts every shot the preview shows", ok, why)
check("In and Out: the dry run leaves a handover with a cut list",
      bool(dry_of(s)), dry_line(s))
ok, why = first_apart(preview_of(s), dry_of(s), ("preview", "dry run"))
check("In and Out: the dry run's handover cuts every shot of the preview",
      ok, why)

s = seen["separation"]
print("\n4. A stored separation, one recording")
check("separation: a preview before the dry run, and the run's cut list",
      both_there(s), there_line(s))
ok, why = first_apart(preview_of(s), run_of(s), ("preview", "run"))
check("separation: the run cuts every shot the preview shows", ok, why)
check("separation: the dry run leaves a handover with a cut list",
      bool(dry_of(s)), dry_line(s))
ok, why = first_apart(preview_of(s), dry_of(s), ("preview", "dry run"))
check("separation: the dry run's handover cuts every shot of the preview",
      ok, why)

s = seen["two_cameras"]
print("\n5. The presenter's name on two cameras")
check("two cameras: a preview before the dry run, and the run's cut list",
      both_there(s), there_line(s))
ok, why = first_apart(preview_of(s), run_of(s), ("preview", "run"))
check("two cameras: the run cuts every shot the preview shows", ok, why)
check("two cameras: the dry run leaves a handover with a cut list",
      bool(dry_of(s)), dry_line(s))
ok, why = first_apart(preview_of(s), dry_of(s), ("preview", "dry run"))
check("two cameras: the dry run's handover cuts every shot of the preview",
      ok, why)
stop()
