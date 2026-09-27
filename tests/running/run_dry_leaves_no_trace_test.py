# -*- coding: utf-8 -*-
"""A dry run works up to the handover and leaves out and TMPDIR as found.

The dry run runs every step up to the handover and keeps what it works
out in the program's store, never beside the result or in the temporary
folder. way_ground's production with its stored separation, both doors,
each in a child with a TMPDIR and a store of its own: --dry-run on the
command line into a folder already holding a file, and the window's Dry
run button once the preview stands. Per door: a handover in the store,
the output folder and the temporary folder each read before and after
-- name, bytes and time of every file.
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
import hashlib
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
# Still for this long after the dry run, and nothing more comes.
STILL = 3.0
QUIET = 60.0


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


def folder_read(folder):
    """Every file under the folder, by its path there: digest and mtime.

    The time goes along because a file written again with the same
    bytes was still written, and the run said nothing was.
    """
    seen = {}
    for root, _dirs, names in os.walk(folder):
        for name in names:
            path = os.path.join(root, name)
            try:
                with open(path, "rb") as f:
                    seen[os.path.relpath(path, folder)] = (hashlib.sha256(
                        f.read()).hexdigest(), os.stat(path).st_mtime_ns)
            except OSError:
                seen[os.path.relpath(path, folder)] = ("gone while read", 0)
    return seen


def difference(before, after):
    """What a run did to the folder, in words: empty where nothing."""
    said = ["came in: %s" % n for n in sorted(set(after) - set(before))]
    for name in sorted(before):
        if name not in after:
            said.append("gone: %s" % name)
        elif after[name][0] != before[name][0]:
            said.append("other bytes: %s" % name)
        elif after[name] != before[name]:
            said.append("written again, same bytes: %s" % name)
    return said


def settled(folders):
    """The folders read once they have stood still STILL s, or at QUIET."""
    last, since, first = None, time.time(), time.time()
    while True:
        now = [folder_read(f) for f in folders]
        if now != last:
            last, since = now, time.time()
        if time.time() - since >= STILL or time.time() - first > QUIET:
            return now
        time.sleep(0.2)


def handovers_in(store):
    """The names under *store* of every JSON shaped as a handover."""
    found = []
    for root, _dirs, names in os.walk(store):
        for name in names:
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
            if (isinstance(d, dict) and isinstance(d.get("cut"), list)
                    and d.get("start_s") is not None):
                found.append(os.path.relpath(path, store))
    return sorted(found)


def child_window(out, store):
    """The window's Dry run on the separation's project; RESULT printed.

    TMPDIR and VPM_CACHE come from the parent, set before Python began.
    """
    nowhere = os.path.join(store, "no-resolve-here")
    os.environ.update(QT_QPA_PLATFORM="offscreen",
                      RESOLVE_SCRIPT_API=nowhere, RESOLVE_SCRIPT_LIB=os.path
                      .join(nowhere, "fusionscript.so"))
    os.environ.pop("VPM_NO_SPEAKER_SPLIT", None)
    tmp = tempfile.gettempdir()
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
    folder = os.path.join(store, "..", "project_" + os.path.basename(store))
    os.makedirs(folder)
    path = ground.project_file(vpm, folder, out)
    seen = {"before": None}
    step = {"last": None, "since": 0.0}

    def answer(w):
        """Wait for the preview to stand 1.5 s, then read both folders."""
        if w is None:
            return "the window"
        at = [k for k in range(w.tabs.count())
              if w.tabs.tabText(k).startswith(vpm.T('Resolve cut'))]
        if not at:
            return "the Resolve cut tab"
        w.tabs.setCurrentIndex(at[0])
        st = w.resolve_sheet.state
        now = (bool((st.get("cut_numbers") or {}).get("cut")),
               bool(st.get("speakers_measuring")))
        if now != step["last"]:
            step["last"], step["since"] = now, time.time()
        if not now[0] or now[1] or time.time() - step["since"] <= 1.5:
            return "the preview settling"
        seen["before"] = [folder_read(out), folder_read(tmp)]
        return ""

    keep = ground.window_answered_run(vpm, app, path, {}, answer,
                                      press="Dry run")
    after = settled([out, tmp])
    before = seen["before"] or after
    print("RESULT " + json.dumps({
        "ended": keep["ended"], "why": keep["why"] or keep["unanswered"],
        "out": difference(before[0], after[0]),
        "tmp": difference(before[1], after[1]),
        "files": [len(before[0]), len(before[1])],
        "said": "".join(keep["log"])[-100:]}))
    shutil.rmtree(folder, ignore_errors=True)


if len(sys.argv) > 3 and sys.argv[1] == "--window":
    child_window(sys.argv[2], sys.argv[3])
    sys.exit(0)

if ground.missing():
    print("SKIPPED: " + ground.missing())
    stop()

vpm = the_program.load()
work = tempfile.mkdtemp(prefix="vpm_drytrace_")
doors = {}
for door in ("line", "window"):
    paths = dict((k, os.path.join(work, door + "_" + k))
                 for k in ("out", "tmp", "store"))
    for p in paths.values():
        os.makedirs(p)
    with open(os.path.join(paths["out"], "kept_from_before.txt"), "w") as f:
        f.write("a file the run has no business with\n")
    doors[door] = paths

print("1. --dry-run on the command line")
line = doors["line"]
speakers = ground.separation_file(vpm, work)
before = [folder_read(line["out"]), folder_read(line["tmp"])]
os.environ["TMPDIR"], kept = line["tmp"], os.environ.get("TMPDIR")
code, said, stuck = ground.line_run(
    ground.line(the_program.SCRIPT, speakers, line["out"], ["--dry-run"]),
    line["store"])
if kept is None:
    os.environ.pop("TMPDIR")
else:
    os.environ["TMPDIR"] = kept
after = settled([line["out"], line["tmp"]])
check("the command line's dry run came back with 0",
      code == 0 and not stuck,
      "return code %s%s, the last it said: %r"
      % (code, ", stuck" if stuck else "", said[-120:]))
found = handovers_in(line["store"])
check("the command line's dry run worked up to the handover",
      bool(found), "%d handovers in its store (%s); the last it said: %r"
      % (len(found), ", ".join(found) or "none", said.strip()[-90:]))
# A run that never came back has left nothing behind for no reason.
ran = "" if not stuck else "the dry run stood still and was stopped; "
gone = difference(before[0], after[0])
check("the command line's dry run leaves its output folder as it was",
      not ran and not gone, "%s%s (%d files before, %d after)"
      % (ran, "; ".join(gone) or "nothing", len(before[0]), len(after[0])))
gone = difference(before[1], after[1])
check("the command line's dry run leaves TMPDIR as it was",
      not ran and not gone, "%s%s (%d files before, %d after)"
      % (ran, "; ".join(gone[:6]) or "nothing", len(before[1]),
         len(after[1])))

print("\n2. The window's Dry run button")
win = doors["window"]
log = open(os.path.join(work, "window.txt"), "w+", encoding="utf-8")
kid = subprocess.Popen(
    [sys.executable, os.path.abspath(__file__), "--window", win["out"],
     win["store"]], stdout=log, stderr=subprocess.STDOUT,
    env=dict(os.environ, TMPDIR=win["tmp"], VPM_CACHE=win["store"]))
try:
    kid.wait(timeout=400)
except subprocess.TimeoutExpired:
    kid.kill()
    kid.wait()
log.seek(0)
text = log.read()
log.close()
rows = [x for x in text.splitlines() if x.startswith("RESULT ")]
seen = json.loads(rows[-1][7:]) if rows else {
    "why": "the child ended with %s and no result: %s"
    % (kid.returncode, " / ".join(text.strip().splitlines()[-3:])[-200:])}
check("the window's dry run was started and came to its end",
      bool(seen.get("ended")),
      "%s; the last it said: %r" % (seen.get("why") or "ran",
                                    seen.get("said")))
found = handovers_in(win["store"])
check("the window's dry run worked up to the handover",
      bool(found), "%d handovers in its store (%s); the last it said: %r"
      % (len(found), ", ".join(found) or "none",
         (seen.get("said") or "").strip()[-90:]))
# A dry run that never ran has left nothing behind for no reason.
ran = "" if seen.get("ended") else "the dry run never ran (%s); " % (
    seen.get("why") or "no reason given")
check("the window's dry run leaves the output folder as it was",
      not ran and not seen.get("out"), "%s%s (%s files before)"
      % (ran, "; ".join(seen.get("out") or []) or "nothing",
         (seen.get("files") or ["?"])[0]))
check("the window's dry run leaves TMPDIR as it was",
      not ran and not seen.get("tmp"), "%s%s (%s files before)"
      % (ran, "; ".join((seen.get("tmp") or [])[:6]) or "nothing",
         (seen.get("files") or ["?", "?"])[1]))
shutil.rmtree(work, ignore_errors=True)
stop()
