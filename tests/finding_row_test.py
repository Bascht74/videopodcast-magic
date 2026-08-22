"""Do all findings of a multi-part recording land in its row?"""
import os
HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = os.environ.get("VPM_SCRIPT") or os.path.join(
    os.path.dirname(HERE), "videopodcast-magic.py")
import sys, importlib.util, subprocess
os.environ["QT_QPA_PLATFORM"] = "offscreen"
from PySide6 import QtWidgets, QtCore
app = QtWidgets.QApplication(sys.argv[:1])
spec = importlib.util.spec_from_file_location(
    "vpm", SCRIPT)
vpm = importlib.util.module_from_spec(spec); sys.modules["vpm"] = vpm
spec.loader.exec_module(vpm)

D = "/tmp/findingtest"; os.makedirs(D, exist_ok=True)
names = []
for stem, n in (("Host", 3), ("Guest", 1)):
    for i in range(n):
        p = "%s/%s_REC%05d.wav" % (D, stem, 5 + i)
        if not os.path.exists(p):
            subprocess.run(["ffmpeg","-v","error","-y","-f","lavfi","-i",
                            "sine=frequency=300:duration=3","-ar","48000",
                            "-ac","1",p], check=True)
        names.append(p)
vpm.list_presets = lambda key: []
vpm.load_api_key = lambda: ""
QtWidgets.QFileDialog.getOpenFileNames = staticmethod(
    lambda *a, **k: (names, ""))

def win():
    for x in app.topLevelWidgets():
        if x.windowTitle().startswith("Video Podcast"): return x
def button(t):
    for w in win().findChildren(QtWidgets.QPushButton):
        if w.text().strip().startswith(t): return w

n=[0]
def carry_on():
    i=n[0]; n[0]+=1
    if i==0:
        win().show(); app.processEvents()
    elif i==1:
        (button("... or add files") or button("Add files")).click()
    elif i==3:
        tw = win().findChildren(QtWidgets.QTreeWidget)[0]
        # Feed findings in by hand: one on the first block, one on the third
        head = os.path.abspath(names[0]); third = os.path.abspath(names[2])
        Finding = vpm.Finding
        findings = [
            Finding("good", "a", "all good", "", head),
            Finding("hint", "", "note on the first block", "", head),
            Finding("good", "c", "all good", "", third),
            Finding("hint", "", "note on the third block", "", third),
            Finding("hint", "Overall", "holds for all")]
        for lab in win().findChildren(QtWidgets.QLabel):
            pass
        # call preflight_fill_in through the bridge signal
        for kind in win().findChildren(QtCore.QObject):
            pass
        vpm_gui_bridge[0].preflight.emit(findings)
        app.processEvents()
    elif i==4:
        tw = win().findChildren(QtWidgets.QTreeWidget)[0]
        found = []
        def run(it, depth=0):
            for k in range(it.childCount()):
                c = it.child(k)
                found.append((depth, c.text(0).strip(), c.text(1), c.text(2)))
                run(c, depth+1)
        run(tw.invisibleRootItem())
        for t, a, b, c in found:
            print("  %s[%s] %s | %s" % ("  "*t, a, b, c[:60]))
        chain = [g for g in found if g[1].startswith("Host_REC00005")]
        assert chain, "chain row missing"
        assert chain[0][2] == "!", "sign is %r instead of !" % chain[0][2]
        chain_notes = [g for g in found if g[1] == "Note"
                       and "block" in g[3]]
        print("\n  note rows of the chain:", len(chain_notes))
        for g in chain_notes:
            print("   ", g[3])
        assert len(chain_notes) == 2, ("both notes of the chain must be "
                                       "there, found %d" % len(chain_notes))
        print("\nall good"); app.quit(); return
    QtCore.QTimer.singleShot(1500, carry_on)

# we reach the bridge through a monkeypatch of the signal
vpm_gui_bridge = []
_old = vpm.make_drop_area
QtCore.QTimer.singleShot(1200, carry_on)
QtCore.QTimer.singleShot(40000, app.quit)
sys.argv=["videopodcast-magic.py"]
# collect the bridge: the object hangs as a child on the QApplication tree
_old_gui = vpm.gui
def gui_with_access():
    import types
    return _old_gui()
vpm.gui = gui_with_access
# simpler: search all QObjects once the interface stands
def collect_with_continuations():
    import gc
    for o in gc.get_objects():
        try:
            if type(o).__name__ == "Bridge" and hasattr(o, "preflight"):
                vpm_gui_bridge.append(o); return
        except Exception:
            pass
    QtCore.QTimer.singleShot(200, collect_with_continuations)
QtCore.QTimer.singleShot(800, collect_with_continuations)
vpm.gui()
