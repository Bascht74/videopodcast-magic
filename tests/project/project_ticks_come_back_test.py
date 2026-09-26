# -*- coding: utf-8 -*-
"""An opened project shows its two ticks as saved, in English and German.

The project file says Multitrack on and the wide shot at the edges off
-- each the other way round from what a fresh window holds, so a tick
that was never restored cannot pass for one that was. The same file is
opened by two windows, one started under LANGUAGE=en and one under
LANGUAGE=de, and each reports both ticks once nothing has moved them for
a while. The sections: the English window against the file, the German
window really German, and the German ticks against the English ones.
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
import time
import json
import wave
import shutil
import struct
import random
import tempfile
import subprocess
import the_program

MARK = "TICKS "
# How long the ticks must stand still before they are read, and how
# long a child may take in all. A timer that moved one after the
# opening moves it well inside the first; the second is never reached.
STILL = 1.5
PATIENCE = 90.0


def child():
    """One window: open the project, wait for standstill, report both ticks."""
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    from PySide6 import QtWidgets, QtCore
    app = QtWidgets.QApplication(sys.argv[:1])
    vpm = the_program.load()
    import key_store_apart
    key_store_apart.apart(vpm)
    vpm.update_offer = lambda *a, **k: None
    vpm.load_api_key = lambda: ""
    path = os.environ["VPM_TICKS_PROJECT"]
    QtWidgets.QFileDialog.getOpenFileName = staticmethod(
        lambda *a, **k: (path, ""))
    QtWidgets.QDialog.exec = lambda self: QtWidgets.QDialog.Accepted
    QtWidgets.QMessageBox.exec = lambda self: QtWidgets.QMessageBox.Ok
    shown = QtWidgets.QWidget.show

    def offstage(self):
        """Shown to Qt, kept off the desktop."""
        self.setAttribute(QtCore.Qt.WA_DontShowOnScreen, True)
        shown(self)

    QtWidgets.QWidget.show = offstage
    labels = {"multi": vpm.T('Multitrack (one track per speaker)'),
              "wide": vpm.T('Wide shot for greeting at the start and '
                            'farewell at the end')}
    moved = [time.time(), 0]

    def box(which):
        """The tick box whose label starts as *which* reads here."""
        for w in app.allWidgets():
            if isinstance(w, QtWidgets.QCheckBox) \
                    and w.text().startswith(labels[which]):
                return w
        return None

    def drive():
        """Open the project, wait until the ticks stand still, report."""
        said = {"texts": labels}
        found = {k: box(k) for k in labels}
        opener = None
        for w in app.allWidgets():
            for a in w.actions():
                if a.text().replace("&", "") \
                        == vpm.T('Open project ...').replace("&", ""):
                    opener = a
        if opener is None or None in found.values():
            said["error"] = "no opener or no box: %r" % sorted(
                k for k, v in found.items() if v is None)
            print(MARK + json.dumps(said))
            app.quit()
            return
        for b in found.values():
            b.toggled.connect(lambda *_: moved.__setitem__(0, time.time()))
            b.toggled.connect(
                lambda *_: moved.__setitem__(1, moved[1] + 1))
        opener.trigger()
        moved[0] = time.time()
        began_here = time.time()
        while time.time() - moved[0] < STILL \
                and time.time() - began_here < PATIENCE - 20:
            app.processEvents()
            time.sleep(0.02)
        said.update({k: b.isChecked() for k, b in found.items()})
        said["toggles"] = moved[1]
        said["still"] = round(time.time() - moved[0], 2)
        print(MARK + json.dumps(said))
        app.quit()

    QtCore.QTimer.singleShot(1500, drive)
    QtCore.QTimer.singleShot(int(PATIENCE * 1000) - 10000, app.quit)
    sys.argv = ["videopodcast_magic.py"]
    vpm.gui()
    sys.exit(0)


if os.environ.get("VPM_TICKS_PROJECT"):
    child()

began = time.time()
done = 0
bad = []


def check(name, ok, extra=""):
    global done
    done += 1
    print("  %-58s %s %s" % (name, "ok" if ok else "FAIL", extra))
    if not ok:
        bad.append("%s [%s]" % (name, extra or "no numbers"))


FOLDER = tempfile.mkdtemp(prefix="vpm_ticks_")


def a_recording(name, seed):
    """Three seconds of noise, written the way a recorder writes."""
    path = os.path.join(FOLDER, name)
    rng = random.Random(seed)
    with wave.open(path, "wb") as f:
        f.setnchannels(1)
        f.setsampwidth(2)
        f.setframerate(48000)
        f.writeframes(b"".join(struct.pack("<h", rng.randint(-6000, 6000))
                               for _ in range(3 * 48000)))
    return path


def a_window(language, project):
    """Start one window under *language*; hand back what it reported."""
    env = dict(os.environ, VPM_TICKS_PROJECT=project,
               QT_QPA_PLATFORM="offscreen", VPM_SILENT="1",
               VPM_NO_SPEAKER_SPLIT="1", VPM_NO_UPDATE_CHECK="1",
               LANG="C", LC_ALL="C", LANGUAGE=language)
    process = subprocess.Popen(
        [sys.executable, os.path.abspath(__file__)], cwd=HERE, env=env,
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    try:
        out, _ = process.communicate(timeout=PATIENCE)
    except subprocess.TimeoutExpired:
        process.kill()
        out = process.communicate()[0] + "\n(stopped after %.0f s)" % PATIENCE
    said = [x for x in out.split("\n") if x.startswith(MARK)]
    if not said:
        for x in out.split("\n")[-15:]:
            print("  | %s" % x)
        return {"error": "no report"}
    return json.loads(said[-1][len(MARK):])


try:
    out_folder = os.path.join(FOLDER, "Result")
    os.makedirs(out_folder)
    recordings = [a_recording("Presenter_REC0001.wav", 1),
                  a_recording("Guest_REC0002.wav", 2)]
    project = os.path.join(FOLDER, "videopodcast-magic_Ticks.json")
    with open(project, "w", encoding="utf-8") as f:
        json.dump({"format": 3, "version": "test", "timeline": [],
                   "preset": "", "production": "Ticks", "call": [],
                   "multitrack": True, "wide_at_edges": False,
                   "project_type": "cut", "out_folder": out_folder,
                   "assignment": {}, "camera_cut": {},
                   "files": [{"path": p, "kind": "audio"}
                             for p in recordings]}, f)
    en = a_window("en", project)
    de = a_window("de", project)
finally:
    shutil.rmtree(FOLDER, ignore_errors=True)


def ticks(d):
    """Both ticks one window reported, in words, for a failure line."""
    return "Multitrack %s, wide shot at the edges %s (%s toggle(s), %s)" % (
        d.get("multi"), d.get("wide"), d.get("toggles"),
        d.get("error") or "still for %s s" % d.get("still"))


print("1. The English window against the file")
check("the English window shows the Multitrack tick the file saved",
      en.get("multi") is True, ticks(en) + ", the file says True")
check("the English window leaves the wide-shot tick off as saved",
      en.get("wide") is False, ticks(en) + ", the file says False")

print("\n2. The German window")
check("the second window really speaks German",
      de.get("texts") and de.get("texts") != en.get("texts"),
      "the Multitrack box reads %r there and %r in English"
      % ((de.get("texts") or {}).get("multi"),
         (en.get("texts") or {}).get("multi")))
check("the German window shows the same two ticks as the English",
      (de.get("multi"), de.get("wide")) == (True, False)
      and (de.get("multi"), de.get("wide"))
      == (en.get("multi"), en.get("wide")),
      "German: %s; English: %s" % (ticks(de), ticks(en)))

print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
