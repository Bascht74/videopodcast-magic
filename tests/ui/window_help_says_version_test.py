# -*- coding: utf-8 -*-
"""The Help boxes name the version running and show its own release text.

About, What changed and the answer to "look for a newer version", each
opened offscreen with Qt's dialogs stood in for: a dialog's exec hands
it to the test instead of waiting, and the release text comes from the
test, not from github. In order: About names program, version and
Python; What changed asks for this version's text and shows its
English half in a window that scrolls, or says it could not be had;
the newest answer says so, names the version, shows the text with the
release page under it, or stays one line without a text.
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
import platform
import time
import the_program

os.environ["QT_QPA_PLATFORM"] = "offscreen"
os.environ.setdefault("VPM_SILENT", "1")
from PySide6 import QtCore, QtWidgets
from PySide6.QtCore import Qt

began = time.time()
app = QtWidgets.QApplication(sys.argv[:1])
vpm = the_program.load()
vpm.set_language("en")

done = 0
bad = []


def check(name, ok, extra=""):
    global done
    done += 1
    print("  %-58s %s %s" % (name, "ok" if ok else "FAIL", extra))
    if not ok:
        bad.append("%s [%s]" % (name, extra or "no numbers"))


# Every dialog that would wait for somebody is handed to the test.
shown, told = [], []
QtWidgets.QDialog.exec = lambda self: shown.append(self) or 1
QtWidgets.QMessageBox.exec = lambda self: shown.append(self) or 0
QtWidgets.QMessageBox.information = staticmethod(
    lambda parent, title, text, *a, **k: told.append((title, text)) or 0)

# A release text as github holds it: both halves, under their marks.
ENGLISH = "### Fixed\n\n* The cut band names the shot under the mouse."
GERMAN = "### Behoben\n\n* Das Schnittband nennt die Einstellung."
RELEASE = "%s\n\n%s\n\n---\n\n%s\n\n%s" % (
    vpm.upkeep.MARK_EN, ENGLISH, vpm.upkeep.MARK_DE, GERMAN)
PAGE = "https://example.invalid/releases/tag/v1"
asked = []
answers = {"v" + vpm.VERSION: RELEASE}
vpm.ui.release_text_of = lambda tag: asked.append(tag) or answers.get(tag, "")

window = QtWidgets.QWidget()
window.setAttribute(Qt.WA_DontShowOnScreen, True)


def last():
    """The last dialog handed over, and its labels and text fields."""
    box = shown[-1] if shown else None
    labels = [w.text() for w in box.findChildren(QtWidgets.QLabel)] \
        if box is not None else []
    fields = box.findChildren(QtWidgets.QPlainTextEdit) \
        if box is not None else []
    return box, labels, fields


print("1. About")
vpm.ui.about_show(window)
box = shown[-1] if shown else None
named = "%s %s" % (vpm.DISPLAY_NAME, vpm.VERSION)
check("the About box names the program and the version running",
      box is not None and box.text() == named,
      "%r against %r" % (box.text() if box else None, named))
python = vpm.T('Python %s on %s') % (platform.python_version(),
                                     platform.system())
check("the About box says which Python it runs on",
      box is not None and python in box.informativeText(),
      "looked for %r in %r" % (python, box.informativeText() if box else None))

print("\n2. What changed")
del shown[:]
vpm.ui.changes_shown(window)
box, labels, fields = last()
check("What changed asks for the text of the version running here",
      asked[:1] == ["v" + vpm.VERSION],
      "asked for %r, wanted %r first" % (asked, "v" + vpm.VERSION))
check("What changed shows the English half of the release text",
      len(fields) == 1 and fields[0].toPlainText() == ENGLISH,
      "%d text fields, the first %r against %r"
      % (len(fields), fields[0].toPlainText() if fields else None, ENGLISH))
check("the release text keeps its scroll bar however short it is",
      len(fields) == 1 and fields[0].verticalScrollBarPolicy()
      == Qt.ScrollBarAlwaysOn,
      "policy %s" % (fields[0].verticalScrollBarPolicy() if fields
                     else None))
check("What changed puts no heading and no link over its own text",
      box is not None and labels == [],
      "labels %r" % labels)
answers.clear()
del shown[:]
vpm.ui.changes_shown(window)
wanted = (vpm.T('What changed in this version'),
          vpm.T('The text for %s could not be fetched.') % vpm.VERSION)
check("without a release text What changed says it could not be had",
      shown == [] and told[-1:] == [wanted],
      "%d windows, told %r against %r" % (len(shown), told[-1:], wanted))

print("\n3. No newer version")
del shown[:]
del told[:]
vpm.ui.newest_shown(window, PAGE, RELEASE)
box, labels, fields = last()
said = vpm.T('No newer version found. This one is %s.') % vpm.VERSION
check("the newest answer says so and names the version over its text",
      labels[:1] == [said] and len(fields) == 1
      and fields[0].toPlainText() == ENGLISH,
      "labels %r, %d text fields" % (labels, len(fields)))
check("the newest answer puts the release page under its text",
      labels[1:] == [PAGE], "labels %r, wanted %r under it" % (labels, PAGE))
del shown[:]
vpm.ui.newest_shown(window, PAGE, "")
wanted = (vpm.T('Look for a newer version now'), said)
check("without a release text the newest answer is one line",
      shown == [] and told == [wanted],
      "%d windows, told %r against %r" % (len(shown), told, wanted))

print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
