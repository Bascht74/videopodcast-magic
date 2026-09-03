# -*- coding: utf-8 -*-
"""Do all findings of a multi-part recording land in its row?

A recording that arrived in three blocks is one row with the blocks
under it. A finding about the third block belongs to that row, not to a
row of its own and not to the general notes.
"""
import os
HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = os.environ.get("VPM_SCRIPT") or os.path.join(
    os.path.dirname(HERE), "videopodcast_magic.py")
import gc, importlib.util, shutil, sys, tempfile, time, wave
import numpy as np
os.environ["QT_QPA_PLATFORM"] = "offscreen"
from PySide6 import QtCore, QtWidgets
app = QtWidgets.QApplication(sys.argv[:1])
spec = importlib.util.spec_from_file_location("vpm", SCRIPT)
vpm = importlib.util.module_from_spec(spec); sys.modules["vpm"] = vpm
spec.loader.exec_module(vpm)
vpm.list_presets = lambda key: []
vpm.load_api_key = lambda: ""

began = time.time()
done = 0
bad = []


def check(name, ok, extra=""):
    global done
    done += 1
    print("  %-58s %s %s" % (name, "ok" if ok else "FAIL", extra))
    if not ok:
        bad.append("%s [%s]" % (name, extra or "no numbers"))


RATE, SEC = 48000, 3
# A folder of its own for every run. A fixed path was worse than it
# looks: the program writes its project file beside the material when it
# quits, and from the next run on that file is offered on the way in --
# a question the run has nobody to answer, and the test stood at it.
folder = tempfile.mkdtemp(prefix="vpm_findingrow_")


def block(name):
    """One block of a recording: three seconds of a tone."""
    path = os.path.join(folder, name)
    t = np.arange(RATE * SEC) / float(RATE)
    with wave.open(path, "wb") as f:
        f.setnchannels(1); f.setsampwidth(2); f.setframerate(RATE)
        f.writeframes((0.4 * np.sin(2 * np.pi * 300.0 * t) * 32767)
                      .astype("<i2").tobytes())
    return path


names = [block("Host_REC%05d.wav" % (5 + i)) for i in range(3)]
names.append(block("Guest_REC00005.wav"))
head, third = os.path.abspath(names[0]), os.path.abspath(names[2])
QtWidgets.QFileDialog.getOpenFileNames = staticmethod(
    lambda *a, **k: (names, ""))


def win():
    for x in app.topLevelWidgets():
        if "Video Podcast Magic" in x.windowTitle():
            return x


def tree():
    w = win()
    kids = w.findChildren(QtWidgets.QTreeWidget) if w else []
    return kids[0] if kids else None


def button(t):
    for w in win().findChildren(QtWidgets.QPushButton):
        if w.text().strip().startswith(t):
            return w


def rows(node=None, depth=0):
    """Every row of the list as (depth, name, sign, text, row)."""
    out = []
    node = node if node is not None else tree().invisibleRootItem()
    for k in range(node.childCount()):
        c = node.child(k)
        out.append((depth, c.text(0).strip(), c.text(1), c.text(2), c))
        out += rows(c, depth + 1)
    return out


def chain_row():
    """The row of the recording that arrived in three blocks."""
    for r in rows() if tree() else []:
        if r[0] == 1 and r[1].startswith("Host_REC00005"):
            return r


def bridge():
    """The object the measuring thread reports its findings through.

    It is built inside gui() and hangs on nothing, so there is no way in
    from outside but to look for it.
    """
    for o in gc.get_objects():
        try:
            if type(o).__name__ == "Bridge" and hasattr(o, "preflight"):
                return o
        except Exception:
            pass


def measured():
    """Whether the program's own check is through.

    Its findings are written into the same rows as ours and they clear
    what stood there, so ours have to go in afterwards. While it runs
    the line under the list says so.
    """
    if win() is None or tree() is None or chain_row() is None:
        return False
    if bridge() is None:
        return False
    return not any(w.text() == vpm.T('checking ...')
                   for w in win().findChildren(QtWidgets.QLabel))


findings = [
    vpm.Finding("good", "a", "all good", "", head),
    vpm.Finding("hint", "", "note on the first block", "", head),
    vpm.Finding("good", "c", "all good", "", third),
    vpm.Finding("hint", "", "note on the third block", "", third),
    vpm.Finding("hint", "Overall", "holds for all")]

NOTE = vpm.T('Note')    # what a hint is headed with in the list
n, waited, stuck, got_there = [0], [0], [], []
PATIENCE = 400          # 400 x 25 ms: ten seconds for any one step


def ready(i):
    """Whether step *i* can read what it needs."""
    if i == 0:
        return win() is not None
    return measured()


def how_it_stands():
    """What was there when the chain gave up.

    Written down at that moment, not afterwards: quitting lets a dialog
    go that was holding the way, and the run then reads as though
    nothing had been in it.
    """
    return ("window %s, list %s, row %s, bridge %s, line %s"
            % ("up" if win() else "never up",
               "there" if tree() else "missing",
               "there" if tree() and chain_row() else "missing",
               "found" if bridge() else "missing",
               "still says %r" % vpm.T('checking ...')
               if win() and any(w.text() == vpm.T('checking ...')
                                for w in win().findChildren(
                                    QtWidgets.QLabel))
               else "has spoken"))


def step():
    i = n[0]
    if not ready(i):
        if waited[0] < PATIENCE:
            waited[0] += 1
            QtCore.QTimer.singleShot(25, step)
            return
        stuck.append((i, how_it_stands()))
        app.quit(); return
    waited[0] = 0
    n[0] += 1
    # Said before the step runs and flushed at once: a test killed in a
    # Qt thread leaves no Python frame behind, so the last line that got
    # out is all there is to place the crash by.
    print("   step %d" % i, flush=True)
    try:
        if i == 0:
            win().show(); app.processEvents()
            (button(vpm.T('... or add files ...'))
             or button(vpm.T('Add files ...'))).click()
        elif i == 1:
            bridge().preflight.emit(findings)
            app.processEvents()
        elif i == 2:
            for d, a, sign, text, _ in rows():
                print("  %s[%s] %s | %s" % ("  " * d, a, sign, text[:60]))
            chain = chain_row()
            check("the recording stands as one row", chain is not None,
                  str([r[1] for r in rows() if r[0] == 1]))
            if chain is None:
                app.quit(); return
            check("and its sign says there is something to read",
                  chain[2] == "!", "sign is %r" % chain[2])
            mine = [r[3] for r in rows(chain[4], 0)
                    if r[1] == NOTE and "block" in r[3]]
            check("the note on the first block is in that row",
                  any("first block" in t for t in mine), str(mine))
            check("the note on the third block is in that row",
                  any("third block" in t for t in mine), str(mine))
            elsewhere = [(r[1], r[3]) for r in rows()
                         if r[1] == NOTE and "block" in r[3]
                         and r[4].parent() is not chain[4]]
            check("and neither of them lands anywhere else",
                  not elsewhere, str(elsewhere))
            general = [r[3] for r in rows() if r[1] == "Overall"]
            check("what belongs to no file stands in the general notes",
                  general == ["holds for all"], str(general))
            got_there.append(True)
            app.quit(); return
    except Exception:
        import traceback; traceback.print_exc(); app.quit(); return
    QtCore.QTimer.singleShot(25, step)


QtCore.QTimer.singleShot(0, step)
# The brake, not the verdict. Without the lines at the end a run that
# never got to the checks would end with 0, and the suite would read a
# test that checked nothing as one that passed.
QtCore.QTimer.singleShot(45000, app.quit)
sys.argv = ["videopodcast_magic.py"]
vpm.gui()

if not got_there:
    if stuck:
        print("\nFAIL: the checks never ran -- step %d of 3 waited ten "
              "seconds for its turn and %s" % (stuck[0][0], stuck[0][1]))
    else:
        # Nothing was polled: the chain arms the next step only when the
        # step before it comes back, so a step that stayed inside --
        # in a dialog waiting for an answer nobody is there to give --
        # stops it without ever waiting.
        print("\nFAIL: the checks never ran -- step %d of 3 never came "
              "back; when the window closed: %s"
              % (n[0] - 1, how_it_stands()))
    bad.append("the checks never ran")

for top in app.topLevelWidgets():
    top.close()
app.processEvents()
shutil.rmtree(folder, ignore_errors=True)
# Named, not turned red: a folder still held is worth knowing about, and
# a test red on every Windows run gets switched off, not read.
if os.path.exists(folder):
    print("  the folder stayed: %s" % folder)
print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
