# -*- coding: utf-8 -*-
"""The note beside a file with no place gives the reason that is true.

Sections: the decision, with the intro free and with it taken; the
reason, with a timecode that has nothing to be set against and with
none -- kept by the window as the measurement named it, and the first
no wider than the second. Each is read on both sheets, the file list
and the tree, out of one weak_marks_show call, and the answer reaches
it through the window's own axis_present. The limit: that answer is
laid here in the shape measure_time_axis gives, not measured.
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
import the_program

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
from PySide6 import QtWidgets, QtGui

app = QtWidgets.QApplication.instance() or QtWidgets.QApplication(sys.argv[:1])
vpm = the_program.load()
vpm.set_language("en")

began = time.time()
done = 0
bad = []


def check(name, ok, extra=""):
    global done
    done += 1
    print("  %-58s %s %s" % (name, "ok" if ok else "FAIL", extra))
    if not ok:
        bad.append("%s [%s]" % (name, extra or "no numbers"))


class Kind(object):
    """One Kind field of the window, as much of it as this road uses."""

    def __init__(self, value):
        self.value = value

    def get(self):
        return self.value


PATH = "/tmp/vpm no place/GuestCam_C003.mov"
OTHER = "/tmp/vpm no place/Jingle.mp4"
INTRO = vpm.label_of(vpm.TYPE_INTRO)
OUTRO = vpm.label_of(vpm.TYPE_OUTRO)
FREE = vpm.T('Left out; %s or %s is one click away.') % (INTRO, OUTRO)
TAKEN = (vpm.T('Left out, %s being taken already; %s is one click away.')
         % (INTRO, OUTRO))


def finding(lines):
    """The lines between the file's name and the decision, as one."""
    return " ".join(line.strip() for line in lines[1:-1])


# The finding of each sentence, asked for by its value.
NO_TC = finding((vpm.T('%s\n   does not fit the other files: sound not '
                       'recognised, no timecode.\n   %s')
                 % ("", "")).splitlines())
ALONE = finding((vpm.T('%s\n   does not fit the other files: sound not '
                       'recognised,\n   nothing to set its timecode '
                       'against.\n   %s') % ("", "")).splitlines())
metrics = QtGui.QFontMetrics(app.font())


def widest(lines):
    """How wide the note is drawn: the widest of its lines."""
    return max(metrics.horizontalAdvance(line) for line in lines)


class Player(object):
    """The player beside the axis, as much of it as axis_present asks."""

    def spot_s(self):
        return 0.0

    def spot(self, ms):
        pass

    def window_draw(self):
        pass


def arrived(state, show_weak, alone):
    """Hand the window's axis_present a measurement that placed nothing.

    In the shape measure_time_axis gives when no two files meet: PATH
    fits nothing, and *alone* names it where it carries a timecode with
    nothing to set it against. Everything round the axis is a stand-in.
    """
    came = []
    bridge = type("Bridge", (), {})()
    bridge.axis = type("Signal", (),
                       {"connect": lambda s, f: came.append(f)})()
    plan = type("Plan", (), {"begin": lambda *a: None,
                             "done": lambda *a: None})()
    nothing = lambda *a, **k: None
    vpm.make_time_axis(
        state=state, files=[], plan=plan, bridge=bridge,
        bridge_emit=nothing, assign_lines=[], blocks_of=nothing,
        real_tc=nothing, HOP=5.0, prework_busy=nothing, out_folder=None,
        production_var=None, commonest_folder=nothing,
        project_move=nothing, project_collect=nothing,
        settings_extend=nothing, axis_label=QtWidgets.QLabel(),
        player=Player(), video_kind_again={}, kind_answered=nothing,
        show_weak=show_weak, tc_column_show=nothing,
        player_follow_up=nothing, window_enable=nothing,
        window_position_show=nothing)
    came[0]({"axis": {}, "clock": {}, "absolute": False, "weak": [PATH],
             "unplaceable": [], "brief": [], "no_place": [PATH],
             "clock_alone": list(alone)}, "")


def notes(other_kind, alone=()):
    """What the tree row and the file list say about PATH, left out.

    With the window's field on a timecode alone beside them, as the
    measurement arriving left it.
    """
    tree = vpm.tree_build(["Recording", "Name", "belongs to", "Timecode",
                           "Speakers"])
    row = vpm.tree_row(tree, None, [os.path.basename(PATH)])
    kinds = vpm.ByFile()
    kinds[PATH] = Kind(vpm.TYPE_IGNORED)
    kinds[OTHER] = Kind(other_kind)
    state = {"file_rows": [(row, PATH, os.path.basename(PATH))],
             "clip_kinds": kinds}
    node = QtWidgets.QTreeWidgetItem([os.path.basename(PATH), "", ""])
    arrived(state, lambda: vpm.weak_marks_show(state, {PATH: node}), alone)
    return (row[0].text().splitlines(), node.text(2).splitlines(),
            sorted(state.get("clock_alone") or ()))


print("1. The decision: left out, and why")
on_tree, on_list, _kept = notes(vpm.TYPE_CONTENT)
check("a file left out with Intro free is not told Intro is taken",
      on_tree[-1].strip() == FREE and on_list[-1].strip() == FREE,
      "the tree says %r, the list %r, wanted %r"
      % (on_tree[-1].strip(), on_list[-1].strip(), FREE))
on_tree, on_list, _kept = notes(vpm.TYPE_INTRO)
check("a file left out with Intro held elsewhere is told so",
      on_tree[-1].strip() == TAKEN and on_list[-1].strip() == TAKEN,
      "the tree says %r, the list %r, wanted %r"
      % (on_tree[-1].strip(), on_list[-1].strip(), TAKEN))

print("\n2. The reason: no timecode, or nothing to set it against")
alone_tree, alone_list, kept = notes(vpm.TYPE_CONTENT, (PATH,))
check("the window keeps which file has a timecode alone, as measured",
      kept == [vpm.path_key(PATH)],
      "the field holds %r, wanted %r" % (kept, [vpm.path_key(PATH)]))
check("a timecode with nothing to set it against is said as that",
      finding(alone_tree) == ALONE and finding(alone_list) == ALONE,
      "the tree says %r, the list %r, wanted %r"
      % (finding(alone_tree), finding(alone_list), ALONE))
on_tree, on_list, _kept = notes(vpm.TYPE_CONTENT)
check("a file with no timecode at all is still told it has none",
      finding(on_tree) == NO_TC and finding(on_list) == NO_TC,
      "the tree says %r, the list %r, wanted %r"
      % (finding(on_tree), finding(on_list), NO_TC))
check("the note on a timecode alone is no wider than the one on none",
      widest(alone_tree) <= widest(on_tree),
      "widest line %d px in %d line(s), against %d px for no timecode"
      % (widest(alone_tree), len(alone_tree), widest(on_tree)))

print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
