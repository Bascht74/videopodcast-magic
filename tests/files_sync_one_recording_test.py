# -*- coding: utf-8 -*-
"""Sync only takes one audio recording, and the second is refused.

A sync project copies one recording onto every camera, so a second
recording is a reason to stop, found in the preflight and nowhere
later. A recording is a chain of blocks, not a file, and a camera using
its own sound is a track, not a recording. Which chain is the second is
decided as the list orders chains: by the name of the block that heads
it, never by the order the files were handed in -- the window and the
command line hand them in differently and have to agree. The sections:
two recordings in sync, the blocks of one recorder, cut by speaker and
the call without the keyword, a camera with its own sound, the command
line stopping, and the window -- state to check, mark to row, sentence
under the list.
"""
import os
import the_program
HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = the_program.SCRIPT
import sys, subprocess, tempfile, time

os.environ["QT_QPA_PLATFORM"] = "offscreen"
from PySide6 import QtGui, QtWidgets
from PySide6.QtCore import Qt

app = QtWidgets.QApplication(sys.argv[:1])
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


# Its own folder under the run's TMPDIR, which the run throws away.
D = tempfile.mkdtemp(prefix="vpm_sync_one_")


def sine(name, seconds, hertz):
    p = os.path.join(D, name)
    subprocess.run(["ffmpeg", "-v", "error", "-f", "lavfi",
                    "-i", "sine=frequency=%d:duration=%d" % (hertz, seconds),
                    p, "-y"], check=True)
    return p


def camera(name, hertz, seconds=2):
    """A camera file with sound of its own in it."""
    p = os.path.join(D, name)
    subprocess.run(["ffmpeg", "-v", "error", "-f", "lavfi",
                    "-i", "testsrc=size=640x360:rate=30:duration=%d" % seconds,
                    "-f", "lavfi",
                    "-i", "sine=frequency=%d:duration=%d" % (hertz, seconds),
                    "-c:v", "libx264", "-pix_fmt", "yuv420p", "-c:a", "aac",
                    "-shortest", p, "-y"], check=True)
    return p


def stops(findings):
    return [x for x in findings if x.kind == "abort"]


def named(findings):
    return [os.path.basename(x.file) for x in stops(findings)]


SENTENCE = vpm.T('Sync only takes one audio recording; this is one more: %s')

# Names without a trailing number on purpose: with one, the program
# reads them as blocks of one recording -- that case is section 2.
anna = sine("Anna.wav", 3, 300)
ben = sine("Ben.wav", 3, 400)

print("1. Two recordings in a sync project")
found = vpm.collect_findings([anna, ben], [], fresh=True, crosstalk=False,
                             project_type="sync")
check("two recordings in sync make exactly one reason to stop",
      len(stops(found)) == 1,
      "%d reasons to stop among %d findings: %s"
      % (len(stops(found)), len(found), named(found)))
check("the reason stands on the second recording",
      named(found) == ["Ben.wav"], "on %s, wanted ['Ben.wav']" % named(found))
texts = [x.text for x in stops(found)]
check("the sentence names the second recording",
      texts == [SENTENCE % "Ben.wav"],
      "%r against %r" % (texts, [SENTENCE % "Ben.wav"]))
turned = vpm.collect_findings([ben, anna], [], fresh=True, crosstalk=False,
                              project_type="sync")
check("which one is second goes by file name, not by the order handed in",
      named(turned) == ["Ben.wav"],
      "handed in as Ben, Anna: on %s, wanted ['Ben.wav']" % named(turned))

print("\n2. A recorder's blocks are one recording")
block1 = sine("Presenter_REC00001.wav", 3, 500)
block2 = sine("Presenter_REC00002.wav", 3, 500)
chains = vpm.group_recording_parts([block1, block2])
check("two numbered blocks of one size are read as one recording",
      len(chains) == 1,
      "%d recordings from 2 blocks: %s"
      % (len(chains), [[os.path.basename(x) for x in r] for r, _d in chains]))
found = vpm.collect_findings([block1, block2], [], fresh=True,
                             crosstalk=False, project_type="sync")
check("two blocks of one recorder are no reason to stop",
      not stops(found),
      "%d reasons to stop among %d findings: %s"
      % (len(stops(found)), len(found), named(found)))
found = vpm.collect_findings([anna, block1, block2], [], fresh=True,
                             crosstalk=False, project_type="sync")
texts = [x.text for x in stops(found)]
check("a recording in blocks is named by its first block and the count",
      texts == [SENTENCE % "Presenter_REC00001.wav +1"],
      "%r against %r" % (texts, [SENTENCE % "Presenter_REC00001.wav +1"]))

print("\n3. Cut by speaker, and the call that does not say")
found = vpm.collect_findings([anna, ben], [], fresh=True, crosstalk=False,
                             project_type="cut")
check("cut by speaker takes two recordings as before", not stops(found),
      "%d reasons to stop among %d findings: %s"
      % (len(stops(found)), len(found), named(found)))
found = vpm.collect_findings([anna, ben], [], fresh=True, crosstalk=False)
check("a call without the keyword is a cut", not stops(found),
      "%d reasons to stop among %d findings: %s"
      % (len(stops(found)), len(found), named(found)))

print("\n4. A camera with its own sound is a track, not a recording")
cam1 = camera("WideCam_C001.mov", 600)
cam2 = camera("GuestCam_C002.mov", 700)
found = vpm.collect_findings([anna], [cam1, cam2], fresh=True,
                             crosstalk=False, project_type="sync")
check("one recording beside two cameras with sound is no reason to stop",
      not stops(found),
      "%d reasons to stop among %d findings: %s"
      % (len(stops(found)), len(found), named(found)))

print("\n5. The command line stops at the second recording")


class Call(object):
    """What the preflight sees of a call; the project type comes beside it."""

    def __init__(self):
        self.no_preflight = False
        self.preflight_again = True
        self.multitrack = False
        self.apart = ()
        self.together = ()
        self.in_point = ""
        self.out_point = ""
        self.fps = 25.0
        self.out = D
        self.dry_run = True
        self.anyway = False


def preflight_verdict(project_type):
    """1 to stop, 0 to go on -- with the machine's own checks replaced."""
    keep = (vpm.check_disk_space, vpm.check_loudness_target)
    vpm.check_disk_space = lambda *a, **k: []
    vpm.check_loudness_target = lambda *a, **k: []
    try:
        # As main() calls it: the project type as a keyword beside the call.
        return vpm.run_preflight(Call(), [anna, ben], [],
                                 project_type=project_type)
    finally:
        vpm.check_disk_space, vpm.check_loudness_target = keep


verdict = preflight_verdict("sync")
check("a sync call with two recordings is stopped before the long steps",
      verdict == 1, "run_preflight answered %r, wanted 1" % verdict)
verdict = preflight_verdict("cut")
check("a cut call with two recordings goes on", verdict == 0,
      "run_preflight answered %r, wanted 0" % verdict)

print("\n6. The window: state to check, mark to row, sentence under the list")


class Plan(object):
    def begin(self, *a):
        pass

    def done(self, *a):
        pass

    def drop(self, *a):
        pass


class Bridge(object):
    preflight = "preflight"


class Tick(object):
    def __init__(self, value):
        self.value = value

    def get(self):
        return self.value


def window_findings(state):
    """What the window's background check hands back for this state."""
    files = [(anna, "audio"), (ben, "audio")]
    seen = []
    _fill_in, kick_off = vpm.make_preflight(
        state, files, Plan(), Bridge(), lambda _s, found: seen.append(found),
        QtWidgets.QLabel(), lambda *a: None, lambda *a: None, lambda *a: None,
        vpm.ByFile(), set(), lambda: [], Tick(False), [], {})
    kick_off()
    # On a condition, never on the clock: the answer arrives from a
    # thread, and a slow machine gets a standstill bound, not a deadline.
    waited = 0.0
    while not seen and waited < 60.0:
        time.sleep(0.05)
        waited += 0.05
    return seen[0] if seen else None, waited


found, waited = window_findings({"project_type": "sync"})
check("the window's check answers at all", found is not None,
      "%s after %.1f s" % ("answered" if found is not None
                           else "nothing came back", waited))
check("the window's sync reaches the check in the background",
      found is not None and named(found) == ["Ben.wav"],
      "reasons to stop on %s, wanted ['Ben.wav']"
      % (named(found) if found is not None else "nothing"))
found, waited = window_findings({})
check("a window with no project type set checks as a cut",
      found is not None and not stops(found),
      "reasons to stop on %s, wanted none"
      % (named(found) if found is not None else "nothing"))

# The real rows and the real mark: the list widget, one row per
# recording, and the findings written into it the way the window does.
state = {"project_type": "sync", "audio_recordings": 2}
sheet = QtWidgets.QVBoxLayout()
(items, preflight_line, _stripes, _marks, _MARKS, _word, set_mark,
 item) = vpm.make_file_list(Qt, QtGui, QtWidgets, sheet, state)
lines_node = vpm.ByFile()
for p in (anna, ben):
    lines_node[p] = item(items, os.path.basename(p), D, "audio",
                         files_for_it=[p])
fill_in, _kick_off = vpm.make_preflight(
    state, [(anna, "audio"), (ben, "audio")], Plan(), Bridge(),
    lambda *a: None, preflight_line, set_mark, lambda *a: None,
    lambda *a: None, lines_node, set(), lambda: [], Tick(False), [], {})
found = vpm.collect_findings([anna, ben], [], fresh=True, crosstalk=False,
                             project_type="sync")
fill_in(found)
# The glyph itself, not the table it comes out of: the cross is what
# the manual shows, and held against the table the check would stay
# green with the table changed under it.
CROSS = "\u2715"
mark_ben = lines_node[ben].text(1)
mark_anna = lines_node[anna].text(1)
check("the second recording's row carries the stop mark",
      mark_ben == CROSS, "%r on Ben.wav, wanted %r" % (mark_ben, CROSS))
check("the first recording's row carries no stop mark",
      mark_anna != CROSS and mark_anna != "",
      "%r on Anna.wav, must be a mark other than %r" % (mark_anna, CROSS))
line = preflight_line.text()
check("the line under the list says why", line.endswith(SENTENCE % "Ben.wav"),
      "%r" % line[-90:])
colour = preflight_line.styleSheet()
check("the line under the list is written in the error colour",
      vpm.COLOURS["error"] in colour,
      "%r, wanted %r in it" % (colour, vpm.COLOURS["error"]))

print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
