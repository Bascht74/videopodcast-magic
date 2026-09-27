# -*- coding: utf-8 -*-
"""A recording set to the finished mix in the window is the run's one too.

In order: the In the sound field offers it, keeps it and asks the list
again when it comes or goes; Sync only leaves it standing; the line
carries it as --finished-mix, out of the files and the plan, and the
parser reads those blocks; two are refused; it is placed as mixed sound
on both sides; the table shows its row on no speaker and no camera; the
window's check stops it without a picture, as the run's does; and one
camera beside it keeps its sound, since the run counts no recording.
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
import tempfile
import time
import types
import wave
import the_program

os.environ["QT_QPA_PLATFORM"] = "offscreen"

from PySide6 import QtWidgets

began = time.time()
app = QtWidgets.QApplication(sys.argv[:1])
vpm = the_program.load()
vpm.set_language("en")

QUIET = vpm.COLOURS["quiet"]
done = 0
bad = []


def check(name, ok, extra=""):
    global done
    done += 1
    print("  %-58s %s %s" % (name, "ok" if ok else "FAIL", extra))
    if not ok:
        bad.append("%s [%s]" % (name, extra or "no numbers"))


# Paths only; nothing is opened, every step here works on names.
D = "/tmp/vpm_finished_field"
TALK = D + "/Presenter_REC0001.wav"
MIX = D + "/ZOOM0004_LR.wav"
MIX2 = D + "/ZOOM0004_LR_0002.wav"
CAM = D + "/WideCam_C0001.MP4"
asked, again = [], []
state = {"project_type": "cut", "sound_holds": vpm.ByFile(),
         "axis_sound_again": lambda: asked.append(1)}

print("1. The field")
_c1, talk = vpm.sound_cell_for(TALK, state, QUIET)
_c2, mix = vpm.sound_cell_for(MIX, state, QUIET, lambda: again.append(1))
check("the field offers the finished mix",
      mix.findData(vpm.SOUND_FINISHED) >= 0,
      "entries %r" % [mix.itemData(i) for i in range(mix.count())])
mix.setCurrentIndex(mix.findData(vpm.SOUND_FINISHED))
check("picking it keeps it for that recording alone",
      state["sound_holds"].get(MIX) == vpm.SOUND_FINISHED
      and state["sound_holds"].get(TALK) is None,
      "kept %r and %r -- wanted finished-mix and none"
      % (state["sound_holds"].get(MIX), state["sound_holds"].get(TALK)))
check("and the list is asked again once", len(again) == 1,
      "asked %d times, wanted once" % len(again))
mix.setCurrentIndex(mix.findData(vpm.SOUND_MIXED))
check("taking it back asks the list again too", len(again) == 2,
      "asked %d times in all, wanted twice" % len(again))
mix.setCurrentIndex(mix.findData(vpm.SOUND_SPEECH))
check("mixed to speech leaves the list alone", len(again) == 2,
      "asked %d times in all, wanted twice" % len(again))
mix.setCurrentIndex(mix.findData(vpm.SOUND_FINISHED))

print("\n2. Sync only")
state["project_type"] = "sync"
vpm.sound_cells_follow(state)
check("under Sync only the finished mix stays and can be changed",
      mix.currentData() == vpm.SOUND_FINISHED and mix.isEnabled(),
      "shows %r, enabled %s -- wanted finished-mix and open"
      % (mix.currentData(), mix.isEnabled()))
state["project_type"] = "cut"
vpm.sound_cells_follow(state)

print("\n3. The line")
values = {"files": [(TALK, "audio"), (MIX, "audio"), (MIX2, "audio"),
                    (CAM, "video")],
          "clip_kinds": {CAM: vpm.TYPE_CONTENT},
          "sound": {MIX: vpm.SOUND_FINISHED},
          "rows": [{"blocks": [TALK], "speakers": "Presenter",
                    "camera_choice": CAM},
                   {"blocks": [MIX, MIX2], "speakers": "",
                    "camera_choice": vpm.IGNORE_AUDIO}],
          "cameras": [{"path": CAM, "name": ""}],
          "project_type": "cut", "wide_at_edges": True}
argv, plan, messages = vpm.run_argv(values)
words = list(argv or [])
given = [words[i + 1] for i, w in enumerate(words[:-1])
         if w == "--finished-mix"]
check("the line carries the finished mix with its blocks",
      given == [MIX, MIX2], "carries %r -- wanted both blocks" % given)
args = vpm.build_argument_parser().parse_args(words[1:])
check("the parser reads those blocks and no recording of them",
      args.finished_mix == [MIX, MIX2]
      and not set(args.files) & {MIX, MIX2},
      "finished %r, files %r" % (args.finished_mix, args.files))
# Where the row still says a camera: the rule stands in the line, not
# in what the table happened to write.
row_said = dict(values, rows=[dict(values["rows"][0]),
                              dict(values["rows"][1], camera_choice=CAM)])
_a, plan2, _m = vpm.run_argv(row_said)
entries = [e.get("audio") for e in (plan2 or {}).get("tracks_of") or ()]
check("its row is in no plan, whatever camera it names",
      entries == [TALK], "the plan's tracks are %r -- wanted the talk "
      "alone" % entries)

print("\n4. Two of them")
two = dict(values, sound={MIX: vpm.SOUND_FINISHED,
                          TALK: vpm.SOUND_FINISHED})
argv2, _p, said = vpm.run_argv(two)
titles = [m[1] for m in said if m[0] == "error"]
check("two finished mixes stop the start",
      argv2 is None and vpm.T('Two finished mixes') in titles,
      "line %r, errors %r" % (argv2 and list(argv2)[:3], titles))

print("\n5. Placed as mixed sound")
check("the window places it with the phase way, as the run does",
      vpm.phase_way_on([MIX, MIX2], "cut", vpm.SOUND_SPEECH,
                       {MIX: vpm.SOUND_FINISHED}),
      "the phase way is off for a finished mix")

print("\n6. Its row in the table")
table = vpm.ui.assignmentsheet.assignmenttable
tree = vpm.tree_build(["a", "b", "c", "d"])
lines, rows = [], []
node = vpm.tree_row(tree, None, [os.path.basename(MIX)])
shown = table.finished_row_shown(node, [MIX, MIX2], "ZOOM0004", "ZOOM0004",
                                 state, lines, rows)
check("the table shows the finished mix as no speaker on no camera",
      shown and len(lines) == 1 and lines[0][2].get() == vpm.IGNORE_AUDIO
      and node[2].text() == vpm.T('the finished mix -- no speaker, '
                                  'no camera'),
      "shown %s, lines %r, cell %r"
      % (shown, [(r[0], c.get()) for r, _n, c in lines], node[2].text()))
node2 = vpm.tree_row(tree, None, [os.path.basename(TALK)])
check("a recording of speech is left to the table",
      not table.finished_row_shown(node2, [TALK], "Presenter", "Presenter",
                                   state, lines, rows) and len(lines) == 1,
      "%d lines" % len(lines))

print("\n7. The window's check")
# Real files this time, two seconds each: the check asks ffprobe. No
# video beside them, so the run's preflight would stop.
R = tempfile.mkdtemp()
talk_file, mix_file = R + "/Presenter_REC0001.wav", R + "/ZOOM0004_LR.wav"
for path, channels in ((talk_file, 1), (mix_file, 2)):
    with wave.open(path, "wb") as f:
        f.setnchannels(channels); f.setsampwidth(2); f.setframerate(48000)
        f.writeframes(b"\x10\x00" * channels * 96000)
got = []


class Plan:
    """The progress plan, which this check does not watch."""

    def begin(self, *_a):
        """Nothing to show."""

    def done(self, *_a):
        """Nothing to show."""

    def drop(self, *_a):
        """Nothing to show."""


look = {"sound_holds": vpm.ByFile({mix_file: vpm.SOUND_FINISHED})}
_fill, kick = vpm.make_preflight(
    look, [(talk_file, "audio"), (mix_file, "audio")], Plan(),
    types.SimpleNamespace(preflight="preflight"),
    lambda _signal, findings: got.append(findings),
    QtWidgets.QLabel(), None, None, None, {}, set(), lambda: [],
    [([talk_file], vpm.SpeakerName("", "Presenter"), vpm.Value("")),
     ([mix_file], vpm.SpeakerName("", "ZOOM0004"),
      vpm.Value(vpm.IGNORE_AUDIO))], {})
kick()
waited = time.time()
while not got and time.time() - waited < 120:
    time.sleep(0.05)
HOMELESS = vpm.T('the finished mix takes the place of the mix in the '
                 'camera files, and without a video file there are none.')
said = [(b.kind, b.text) for b in (got[0] if got else ())
        if b.text == HOMELESS]
check("the window's check stops a finished mix with no picture",
      said == [("abort", HOMELESS)],
      "%s after %.1f s: %r" % ("answered" if got else "no answer",
                               time.time() - waited, said))

print("\n8. One camera beside it")
only = [(MIX, "audio"), (CAM, "video")]
kinds = {CAM: vpm.Value(vpm.TYPE_CONTENT)}
used, forced = vpm.cameras_using_audio(only, kinds, {}, None, state)
check("one camera and the finished mix: the camera's sound is used",
      used == [CAM] and forced == [CAM],
      "used %r, by rule %r -- wanted the camera twice" % (used, forced))

print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
