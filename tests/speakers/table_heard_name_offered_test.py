# -*- coding: utf-8 -*-
"""The table names a voice heard again as it was named, and Start is free.

A project with one recording separated and named, its prints stored,
and a second recording whose separation and prints lie in the store.
The window is opened offscreen and the second recording's separation
comes back on the window's own road -- answered with several speakers,
or separated anew. One window per case: voices just over the line --
the table shows the first recording's names and Start is free; just
under it -- no name is offered; a third recording's voice, apart from
all, carrying one of the names by hand -- not offered, Start held; the
second recording's other voice carrying it by hand -- not offered.
The prints are written by hand; real voices are voice_split_hears_two's.
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
import math
import shutil
import subprocess
import tempfile
import time
import wave

import the_program

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


# How long nothing may change before a child gives up, and how long the
# table has to stand unchanged before it is read. Standstill, not a
# deadline: the builder is about nine times slower than this machine.
PATIENCE = 60.0
SETTLED = 1.0
SEGMENTS = [("SPEAKER_00", [(0.0, 0.4)]), ("SPEAKER_01", [(0.5, 0.9)])]


def pair(similarity):
    """The second recording's prints, each at *similarity* to one voice
    of the first and at nought to the other: the labels the other way
    round, as the model numbers by speaking time and not by person."""
    rest = math.sqrt(1.0 - similarity ** 2)
    return {"SPEAKER_00": [0.0, similarity, rest, 0.0, 0.0],
            "SPEAKER_01": [similarity, 0.0, 0.0, rest, 0.0]}


def child(case):
    """One window, one case; prints what it saw as one RESULT line."""
    os.environ.pop("VPM_NO_SPEAKER_SPLIT", None)
    store = tempfile.mkdtemp(prefix="vpm_heard_offer_store_")
    folder = tempfile.mkdtemp(prefix="vpm_heard_offer_")
    nowhere = os.path.join(store, "no-resolve-here")
    os.environ.update(VPM_CACHE=store, QT_QPA_PLATFORM="offscreen",
                      RESOLVE_SCRIPT_API=nowhere, RESOLVE_SCRIPT_LIB=os.path
                      .join(nowhere, "fusionscript.so"))
    from PySide6 import QtCore, QtWidgets
    app = QtWidgets.QApplication(sys.argv[:1])
    vpm = the_program.load()
    vpm.set_language("en")
    line = vpm.SPEAKER_SAME_VOICE
    asked = []
    vpm.list_presets = lambda key: []
    vpm.load_api_key = lambda: ""
    vpm.speaker_split_run = lambda *a, **k: (asked.append(a), ([], ""))[1]
    vpm.speaker_split_available = lambda deep=False: True
    vpm.SPEAKER_SPLIT_OFF = False
    vpm.words_at_hand = lambda *a, **k: []
    vpm.recognise_speech = lambda *a, **k: ([], "")

    def recording(name, seconds):
        """A short wav of low noise, so the store has a file to key on."""
        path = os.path.join(folder, name)
        with wave.open(path, "wb") as w:
            w.setnchannels(1)
            w.setsampwidth(2)
            w.setframerate(16000)
            w.writeframes(bytes(bytearray((i * 7) % 5 for i in
                                          range(2 * 16000 * seconds))))
        return path

    first = recording("Room_A.wav", 1)
    second = recording("Room_B.wav", 2)
    third = recording("Room_C.wav", 3)
    prints = {first: {"SPEAKER_00": [1.0, 0.0, 0.0, 0.0, 0.0],
                      "SPEAKER_01": [0.0, 1.0, 0.0, 0.0, 0.0]},
              second: pair(line - 0.01 if case == "under" else line + 0.01),
              third: {"SPEAKER_00": [0.0, 0.0, 0.0, 0.0, 1.0]}}
    alone = [("SPEAKER_00", [(0.0, 0.4)])]
    for p in (first, second, third):
        key = vpm.speaker_cache_key(p, vpm.speaker_model_mark(), 0)
        vpm.speaker_cache_write(key, alone if p == third else SEGMENTS)
        vpm.speaker_voices_write(key, prints[p])
    block = vpm.speakers_for_project(
        first, SEGMENTS, 0, {"SPEAKER_00": "Presenter",
                             "SPEAKER_01": "Guest"})
    sound = [first, second]
    if case == "typed":
        # Typed by hand on a voice that lies apart from every other.
        block["more"] = [vpm.speakers_for_project(
            third, alone, 0, {"SPEAKER_00": "Guest"})]
        sound.append(third)
    if case == "again":
        # Typed by hand on the voice that sounds like the Presenter.
        block["more"] = [vpm.speakers_for_project(
            second, SEGMENTS, 0, {"SPEAKER_01": "Guest"})]
    assignment = dict(("several:" + os.path.abspath(p), True)
                      for p in sound if p != second or case == "again")
    project = os.path.join(folder, "project", "videopodcast-magic_Pilot.json")
    os.makedirs(os.path.dirname(project))
    with open(project, "w", encoding="utf-8") as f:
        json.dump({"format": vpm.FILE_FORMAT, "version": "test",
                   "timeline": [], "preset": "", "production": "Pilot",
                   "project_type": "cut", "multitrack": False,
                   "wide_at_edges": False,
                   "out_folder": os.path.join(folder, "out"),
                   "assignment": assignment, "speakers": block,
                   "speakers_source": first, "speakers_local": True,
                   "files": [{"path": p, "kind": "audio"} for p in sound]},
                  f, ensure_ascii=False, indent=1)

    hands, seen = {}, {"pending": None}
    real_make = vpm.make_speaker_split

    def make(*a):
        """The window's separation, built as ever; its handles kept."""
        got = real_make(*a)
        hands.update(state=a[1], voices=a[7], several=got[3], kick=got[0])
        return got
    vpm.make_speaker_split = make
    real_missing = vpm.missing_conditions

    def missing(*a, **k):
        """What the window's Start asks, kept as it answers."""
        out = real_missing(*a, **k)
        seen["pending"] = dict(out)
        return out
    vpm.missing_conditions = missing
    real_said = vpm.speaker_voices_said

    def said(*a, **k):
        """The last step of a separation come back, counted."""
        seen["back"] = seen.get("back", 0) + 1
        return real_said(*a, **k)
    vpm.speaker_voices_said = said
    QtWidgets.QFileDialog.getOpenFileName = staticmethod(
        lambda *a, **k: (project, ""))
    QtWidgets.QMessageBox.exec = lambda self: QtWidgets.QMessageBox.Ok
    result = {"why": "", "asked": 0}
    step = {"n": 0, "last": None, "since": time.time()}

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

    def rows(source):
        """The voice rows of *source* in the table: label -> the text of
        the name field in that row, found by the key the row carries."""
        out = {}
        views = win().findChildren(QtWidgets.QTreeView) if win() else ()
        for view in views:
            model = view.model()
            if not hasattr(model, "invisibleRootItem"):
                continue
            items = [model.invisibleRootItem()]
            while items:
                item = items.pop()
                items += [item.child(i, 0) for i in range(item.rowCount())
                          if item.child(i, 0) is not None]
                key = item.data(QtCore.Qt.UserRole + 2)
                if not isinstance(key, str) or not key:
                    continue
                there, label = vpm.voice_key_parts(key)
                field = view.indexWidget(
                    item.index().sibling(item.index().row(), 1))
                if vpm.path_key(there) == vpm.path_key(source) \
                        and isinstance(field, QtWidgets.QLineEdit):
                    out[label] = field.text()
        return out

    def give_up(why):
        """Stop waiting, and keep the reason for the red line."""
        result["why"] = why
        app.quit()

    def tick():
        """Open, answer the second recording, wait for the table."""
        try:
            now = (step["n"], json.dumps(rows(second)),
                   json.dumps(rows(first)), json.dumps(seen["pending"]))
            if now != step["last"]:
                step["last"], step["since"] = now, time.time()
            still = time.time() - step["since"]
            if still > PATIENCE:
                return give_up("nothing changed for %.0f s at step %d"
                               % (PATIENCE, step["n"]))
            if step["n"] == 0:
                if button(vpm.T("Open project")) is not None:
                    win().show()
                    button(vpm.T("Open project")).click()
                    step["n"] = 1
            elif step["n"] == 1:
                if len(rows(first)) == 2 and "several" in hands:
                    result["before"] = rows(second)
                    if case == "again":
                        # Separated anew, as voice_add starts it, with
                        # the count the store holds.
                        hands["state"]["speakers_source_chosen"] = second
                        hands["state"]["speakers_count"] = 0
                        hands["kick"](fresh=True)
                    else:
                        hands["several"](second, True)
                    step["n"] = 2
            elif step["n"] == 2:
                by = hands["state"].get("speakers_by") or {}
                if seen.get("back") \
                        and (by.get(second) or {}).get("segments") \
                        and len(rows(second)) == 2 \
                        and still > SETTLED:
                    start = button(vpm.T("Start"))
                    result.update(
                        names=rows(second), first=rows(first),
                        pending=dict((str(k), v) for k, v in
                                     (seen["pending"] or {}).items()),
                        start=bool(start and start.isEnabled()),
                        asked=len(asked), back=seen.get("back"))
                    return app.quit()
        except Exception as e:
            return give_up("%s: %s" % (type(e).__name__, e))
        QtCore.QTimer.singleShot(100, tick)

    QtCore.QTimer.singleShot(0, tick)
    sys.argv = ["videopodcast_magic.py"]
    vpm.gui()
    print("RESULT " + json.dumps(result))
    shutil.rmtree(folder, ignore_errors=True)
    shutil.rmtree(store, ignore_errors=True)


if len(sys.argv) > 2 and sys.argv[1] == "--case":
    child(sys.argv[2])
    sys.exit(0)

# One window per case, each in a child: two windows in one process would
# share what gui() leaves behind. Each child waits on standstill.
CASES = ("over", "under", "typed", "again")
work = tempfile.mkdtemp(prefix="vpm_heard_offer_kids_")
kids = {}
for case in CASES:
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
    found = [x for x in said.splitlines() if x.startswith("RESULT ")]
    seen[case] = json.loads(found[-1][7:]) if found else {
        "why": "the child ended with %s and no result: %s"
        % (kid.returncode, " / ".join(said.strip().splitlines()[-3:])[-200:])}
shutil.rmtree(work, ignore_errors=True)
vpm = the_program.load()
vpm.set_language("en")
CLASH = vpm.names_clash_said(["Guest"])
FIRST = {"SPEAKER_00": "Presenter", "SPEAKER_01": "Guest"}
LENT = ("Presenter", "Guest")


def line(case):
    """The evidence for one case, for a failure line."""
    s = seen[case]
    return ("%s: second recording %s, first %s, Start %s, held %s%s"
            % (case, s.get("names"), s.get("first"),
               "free" if s.get("start") else "held", s.get("pending"),
               "; " + s["why"] if s.get("why") else ""))


print("1. The windows")
came = [c for c in CASES if not seen[c].get("why")
        and seen[c].get("first") == FIRST
        and len(seen[c].get("names") or {}) == 2
        and seen[c].get("asked") == 0 and seen[c].get("back") == 1]
check("every window took the stored separation back into its table",
      came == list(CASES),
      "came back in %s of %s; %s" % (came, list(CASES), " | ".join(
          line(c) + ", model asked %s times, came back %s times"
          % (seen[c].get("asked"), seen[c].get("back"))
          for c in CASES if c not in came)))

print("\n2. Just over the line")
over = seen["over"]
check("a voice heard again shows its first recording's name in the table",
      over.get("names") == {"SPEAKER_00": "Guest",
                            "SPEAKER_01": "Presenter"},
      "wanted SPEAKER_00 Guest and SPEAKER_01 Presenter; " + line("over"))
check("and Start is free, nothing held on the assignment tab",
      over.get("start") is True and "22" not in (over.get("pending") or {}),
      line("over"))

print("\n3. Just under the line")
under = seen["under"]
check("voices just under the line are offered no name from the first",
      len(under.get("names") or {}) == 2 and not set(
          (under.get("names") or {}).values()) & set(LENT),
      "wanted neither Presenter nor Guest; " + line("under"))

print("\n4. A name typed by hand on another voice")
typed = seen["typed"]
check("a name typed on a voice apart from both is not offered",
      (typed.get("names") or {}).get("SPEAKER_01") == "Presenter"
      and (typed.get("names") or {}).get("SPEAKER_00") not in LENT,
      "wanted SPEAKER_01 Presenter and SPEAKER_00 neither; "
      + line("typed"))
check("and Start stays held on that name",
      typed.get("start") is False
      and (typed.get("pending") or {}).get("22") == CLASH,
      "wanted held with %r; %s" % (CLASH, line("typed")))
again = seen["again"]
check("a name the recording's other voice carries is not offered twice",
      (again.get("before") or {}).get("SPEAKER_01") == "Guest"
      and (again.get("names") or {}).get("SPEAKER_01") == "Guest"
      and (again.get("names") or {}).get("SPEAKER_00") not in LENT,
      "wanted SPEAKER_01 Guest as typed before (%s) and SPEAKER_00 neither;"
      " %s" % (again.get("before"), line("again")))
stop()
