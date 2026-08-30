# -*- coding: utf-8 -*-
"""The two proposals that fill a field nobody has answered.

The names of the voices, and the voice that hardly speaks being set to
"do not use". Both are proposals: they write into a field that still
carries what the program put there, and they never touch an answer.

Three things are checked, and the third is the one that matters.

The window decides. Measured on a real interview of 31.8.2026: the
separation found four voices where three people sat, and over the whole
recording the fourth looks like a speaker -- 217 s, 4.6 per cent, a
longest passage of 11.1 s. Inside the time window it is 29 s. So the
material here is built the same way round: a voice that talks through a
long run-up and says almost nothing after the In point. Without the
window it is ranked and named; with the window it falls out and is
proposed for "do not use". A check that passed both ways would be
saying nothing.

Nothing is set over an answer. A name somebody typed, a camera somebody
picked, and a name typed back to exactly the stand-in the program hands
out: all three stay. The last one is why the mark decides and not the
text -- "Speaker 2" written by a person looks exactly like "Speaker 2"
written by the program.

And the footer: the three buttons of one row stand equally high. Held
against each other and never against a pixel count, because the system
font decides how tall a button is and a number written down here would
be wrong on the next machine.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = os.environ.get("VPM_SCRIPT") or os.path.join(
    os.path.dirname(HERE), "videopodcast-magic.py")
import importlib.util
import tempfile

os.environ["QT_QPA_PLATFORM"] = "offscreen"
os.environ["VPM_CACHE"] = tempfile.mkdtemp(prefix="vpm_voiceprop_cache_")
spec = importlib.util.spec_from_file_location("vpm", SCRIPT)
vpm = importlib.util.module_from_spec(spec)
sys.modules["vpm"] = vpm
spec.loader.exec_module(vpm)

bad = []


def check(what, ok, detail=""):
    print("  %-56s %s%s" % (what, "ok" if ok else "FAIL",
                            "" if ok else "   " + detail))
    if not ok:
        bad.append(what)


# --------------------------------------------------------------- material
# Three people talking in turn from second 1000 on, and a fourth voice
# that only speaks in the run-up before the In point. The fourth gets
# enough turns to be ranked over the whole recording -- otherwise the
# window would have nothing to prove.
PEOPLE = ["SPEAKER_00", "SPEAKER_01", "SPEAKER_02"]
IN_POINT = 995.0


def material():
    """The passages and the words, the way the program stores them."""
    parts = {n: [] for n in PEOPLE + ["SPEAKER_03"]}
    t = 5.0
    for _ in range(30):
        parts["SPEAKER_03"].append((t, t + 5.0))
        t += 6.0
    t = 1000.0
    for _ in range(40):
        for n in PEOPLE:
            parts[n].append((t, t + 5.0))
            t += 6.0
    # The one asking is SPEAKER_00: every one of its sentences ends on a
    # question mark, and who_asks counts questions per sentence.
    words = []
    for n in sorted(parts):
        for a, _b in parts[n]:
            for j in range(5):
                mark = "?" if (n == "SPEAKER_00" and j == 4) else (
                    "." if j == 4 else "")
                words.append(vpm.speech_word(a + 0.2 + j * 0.5,
                                             a + 0.4 + j * 0.5,
                                             "wort" + mark))
    words.sort(key=lambda w: w["start"])
    return [(n, parts[n]) for n in sorted(parts)], words


TRACKS, WORDS = material()
LABELS = [n for n, _p in TRACKS]


def proposals(in_point):
    """What the two proposals say for that In point."""
    order = vpm.voice_window_order(TRACKS, WORDS, 0.0, 0.0, in_point, "")
    return vpm.voice_proposals(order, LABELS)


print("The window decides")
whole_named, whole_silent = proposals("")
cut_named, cut_silent = proposals("+%d" % IN_POINT)
check("over the whole recording the fourth voice is ranked",
      "SPEAKER_03" in whole_named and "SPEAKER_03" not in whole_silent,
      "%s %s" % (whole_named, whole_silent))
check("inside the window it is the one proposed for do not use",
      cut_silent == ["SPEAKER_03"], str(cut_silent))
check("and the three who talk are named",
      sorted(cut_named) == PEOPLE, str(cut_named))
check("the one asking most is not the guest",
      cut_named.get("SPEAKER_00") != vpm.T('Guest'), str(cut_named))
check("exactly one of them is the guest",
      sorted(cut_named.values()).count(vpm.T('Guest')) == 1,
      str(cut_named))
check("nothing at all is said where nothing was recognised",
      vpm.voice_proposals(
          vpm.voice_window_order(TRACKS, [], 0.0, 0.0), LABELS) == ({}, []))
check("nor where the window has been narrowed to a minute",
      vpm.voice_window_order(TRACKS, WORDS, 0.0, 0.0,
                             "+1000", "+1060") == [])


# ------------------------------------------------------- filling the fields
def rows(labels):
    """Voice rows the way the window keeps them, with a fresh state."""
    state = {}
    lines = []
    for i, label in enumerate(labels):
        name_value = vpm.Value(vpm.T('Speaker %d') % (i + 1))
        camera_value = vpm.Value("A.mov")
        marks = vpm.voice_marks_of(state)
        marks["name"].setdefault(label, name_value.get())
        marks["camera"].setdefault(label, camera_value.get())
        lines.append((label, name_value, camera_value))
    return state, lines


def apply(state, lines, in_point):
    """One round of the proposals over those rows."""
    named, silent = proposals(in_point)
    return vpm.voice_proposal_apply(lines, named, silent,
                                    vpm.voice_marks_of(state))


print("\nWhat is filled in and what is left alone")
state, lines = rows(LABELS)
apply(state, lines, "+%d" % IN_POINT)
by_label = {k: (nv, cv) for k, nv, cv in lines}
check("a stand-in name is replaced by the proposal",
      not vpm.is_stand_in_name(by_label["SPEAKER_00"][0].get()),
      by_label["SPEAKER_00"][0].get())
check("the voice that hardly speaks goes to do not use",
      by_label["SPEAKER_03"][1].get() == vpm.IGNORE_AUDIO,
      by_label["SPEAKER_03"][1].get())
check("the others keep their camera",
      by_label["SPEAKER_00"][1].get() == "A.mov")

# The window widens again: the proposal has to be taken back, or a
# moved In point would only ever switch voices off.
apply(state, lines, "")
check("a wider window brings the fourth voice back to its camera",
      by_label["SPEAKER_03"][1].get() == "A.mov",
      by_label["SPEAKER_03"][1].get())
check("and its name follows the new ranking",
      not vpm.is_stand_in_name(by_label["SPEAKER_03"][0].get()),
      by_label["SPEAKER_03"][0].get())
apply(state, lines, "+%d" % IN_POINT)
check("and back again when the window narrows",
      by_label["SPEAKER_03"][1].get() == vpm.IGNORE_AUDIO
      and vpm.is_stand_in_name(by_label["SPEAKER_03"][0].get()),
      "%s / %s" % (by_label["SPEAKER_03"][0].get(),
                   by_label["SPEAKER_03"][1].get()))

print("\nNothing is set over an answer")
state, lines = rows(LABELS)
marks = vpm.voice_marks_of(state)
by_label = {k: (nv, cv) for k, nv, cv in lines}
by_label["SPEAKER_00"][0].set("Sebastian")
marks["typed"].add("SPEAKER_00")
by_label["SPEAKER_03"][1].set("B.mov")
marks["typed"].add("SPEAKER_03")
# Typed back to exactly the name the program hands out. The text says
# nothing; the mark says somebody was here.
by_label["SPEAKER_01"][0].set(vpm.T('Speaker %d') % 2)
marks["typed"].add("SPEAKER_01")
apply(state, lines, "+%d" % IN_POINT)
check("a name somebody typed stays",
      by_label["SPEAKER_00"][0].get() == "Sebastian")
check("a camera somebody picked stays, even on a silent voice",
      by_label["SPEAKER_03"][1].get() == "B.mov")
check("a stand-in typed by a person is an answer too",
      by_label["SPEAKER_01"][0].get() == vpm.T('Speaker %d') % 2,
      by_label["SPEAKER_01"][0].get())
check("the row nobody touched is still filled",
      not vpm.is_stand_in_name(by_label["SPEAKER_02"][0].get()),
      by_label["SPEAKER_02"][0].get())

print("\nWhat the row remembers")
from PySide6 import QtWidgets, QtCore
app = QtWidgets.QApplication(sys.argv[:1])
state = {}
name_value, camera_value = vpm.Value("Speaker 1"), vpm.Value("A.mov")
field = vpm.field_bind(QtWidgets.QLineEdit(), name_value)
box = QtWidgets.QComboBox()
box.addItems(["A.mov", "B.mov"])
vpm.voice_row_marks(state, "SPEAKER_00", name_value, camera_value,
                    field, box)
name_value.set("Gast")
check("the program writing a name is not an answer",
      "SPEAKER_00" not in vpm.voice_marks_of(state)["typed"])
field.setText("Anna")
check("nor is the field following the value",
      "SPEAKER_00" not in vpm.voice_marks_of(state)["typed"])
field.textEdited.emit("Anna")
check("a person typing is",
      "SPEAKER_00" in vpm.voice_marks_of(state)["typed"])
check("and what the row was born with is kept",
      vpm.voice_marks_of(state)["camera"]["SPEAKER_00"] == "A.mov")


# --------------------------------------------------------------- the footer
# Held against each other, never against a pixel count. A hidden button
# has no geometry, so it is made visible for the reading.
print("\nThe three buttons of the footer row")
vpm.list_presets = lambda key: [("Podcast_Multitrack", "u1", True)]
vpm.load_api_key = lambda: ""
WANTED = {vpm.T('Start'), vpm.T('Dry run'), vpm.T('Settings ...'),
          vpm.T('Break off')}
step = [0]


def window():
    for x in app.topLevelWidgets():
        if "Video Podcast Magic" in x.windowTitle():
            return x


def footer_buttons(w):
    return [b for b in w.findChildren(QtWidgets.QPushButton)
            if b.text() in WANTED]


def look():
    i = step[0]
    step[0] += 1
    w = window()
    if w is None:
        return
    if i == 0:
        w.show()
        w.resize(1600, 1000)
    elif i == 1:
        for b in footer_buttons(w):
            b.setVisible(True)
    elif i == 2:
        edges = {}
        for b in footer_buttons(w):
            y = b.mapTo(w, QtCore.QPoint(0, 0)).y()
            edges[b.text()] = (y, y + b.height())
        print("    " + "  ".join("%s %d..%d" % (n, a, b)
                                 for n, (a, b) in sorted(edges.items())))
        check("all four buttons were found", len(edges) == len(WANTED),
              str(sorted(edges)))
        check("their top edges agree",
              len(set(a for a, _b in edges.values())) == 1, str(edges))
        check("and their bottom edges too",
              len(set(b for _a, b in edges.values())) == 1, str(edges))
        app.quit()
    elif i > 3:
        app.quit()


clock = QtCore.QTimer()
clock.timeout.connect(look)
clock.start(500)
QtCore.QTimer.singleShot(30000, app.quit)
vpm.gui()

print("\n%s" % ("FAIL: %d of them" % len(bad) if bad else "All good."))
sys.exit(1 if bad else 0)
