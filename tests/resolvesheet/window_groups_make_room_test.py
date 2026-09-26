# -*- coding: utf-8 -*-
"""The camera cut's groups shut the one opened longest ago to make room.

The three groups of the Resolve sheet are built the way the sheet builds
them, over a stand-in for the preview beneath them, in a sheet with room
for two open groups and not three. In order: the oldest is shut on the
first look, opening a shut one shuts the oldest and not it, a changed
value keeps its group open, one group stays open however short the room,
and a shut group names its values beside its header. The height needed
is asked of the program; which groups are open is written down here.
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
import shutil
import tempfile
import time
import the_program

os.environ["QT_QPA_PLATFORM"] = "offscreen"
# A press writes which groups are open; into a folder of this test's own,
# so no other test of the run finds it, and every build starts empty.
KEPT = tempfile.mkdtemp(prefix="vpm_groups_")
os.environ["VPM_SETTINGS"] = KEPT
from PySide6 import QtCore, QtWidgets

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


def build(room, changed=None):
    """A sheet *room* px high: the cut box, and 300 px of preview under it."""
    shutil.rmtree(KEPT, ignore_errors=True)
    vpm.forget_settings()
    sheet = QtWidgets.QScrollArea()
    sheet.setWidgetResizable(True)
    sheet.setFrameShape(QtWidgets.QFrame.NoFrame)
    inside = QtWidgets.QWidget()
    sheet.setWidget(inside)
    column = QtWidgets.QVBoxLayout(inside)
    box = QtWidgets.QGroupBox("cut")
    column.addWidget(box)
    into = QtWidgets.QVBoxLayout(box)
    loose = QtWidgets.QVBoxLayout()
    parts = {}
    values = vpm.cut_fields_build(loose, parts)
    preview = QtWidgets.QWidget()
    preview.setFixedHeight(300)
    column.addWidget(preview)
    for key, value in (changed or {}).items():
        values[key].set(value)
    groups = vpm.resolvesheet.CutGroups(sheet, into, loose, parts, values)
    sheet.setAttribute(QtCore.Qt.WA_DontShowOnScreen, True)
    sheet.resize(640, room)
    sheet.show()
    app.processEvents()
    return sheet, groups, values


def need_with(groups, keys):
    """The height the sheet asks for with just *keys* open."""
    for g in groups.groups:
        g.open_show(g.key in keys)
    return groups.room_needed()


def shown(groups):
    """The open groups as the sheet shows them, in the order of the plan."""
    return [g.key for g in groups.groups if g.is_open()]


# The room: any two groups open fit, all three do not.
_s, probe, _v = build(4000)
pair = max(need_with(probe, k) for k in (("wide", "special"),
                                         ("timing", "special"),
                                         ("timing", "wide")))
every = need_with(probe, ("timing", "wide", "special"))
# A precondition of the material, not a verdict: three must not fit.
assert every > pair + 2, (every, pair)
room = pair + 2

sheet, groups, values = build(room)
groups.first()
check("with room for two the group opened longest ago is shut",
      groups.opened == ["wide", "special"]
      and shown(groups) == ["wide", "special"],
      "open %s, shown %s, wanted wide and special; %d px of room, %d "
      "asked with all three" % (groups.opened, shown(groups), room, every))
groups.group_of["timing"].button.click()
app.processEvents()
check("opening a shut group shuts the oldest open one, not it",
      groups.opened == ["special", "timing"]
      and shown(groups) == ["timing", "special"],
      "open %s, shown %s after timing was opened, wanted special and "
      "timing" % (groups.opened, shown(groups)))
values["min-edit-duration"].set("2.5")
timing = groups.group_of["timing"]
timing.button.click()
app.processEvents()
beside = timing.said.text()
wanted = "%s 2.5\u00a0s" % vpm.T('Minimum Edit Duration')
check("a shut group names its values beside its header",
      wanted in beside and not timing.said.isHidden()
      and not timing.is_open(),
      "beside the shut header %r, wanted it to hold %r; shown %s, open %s"
      % (beside[:80], wanted, not timing.said.isHidden(), timing.is_open()))

_s2, changed, _v2 = build(60, {"min-edit-duration": "2.5"})
changed.first()
check("a group holding a changed value is the one left open",
      changed.opened == ["timing"] and shown(changed) == ["timing"],
      "open %s, shown %s in 60 px, wanted timing, whose Minimum Edit "
      "Duration was set to 2.5" % (changed.opened, shown(changed)))
_s3, short, _v3 = build(60)
short.first()
check("however short the room, one group stays open",
      short.opened == ["special"] and shown(short) == ["special"],
      "open %s, shown %s in 60 px, wanted the last of the plan, special"
      % (short.opened, shown(short)))

shutil.rmtree(KEPT, ignore_errors=True)
print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
