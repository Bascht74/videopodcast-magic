# -*- coding: utf-8 -*-
"""A separation that cannot run mends itself once, or says the way back.

The window asked "can it run here" once, at its own start, and kept
that answer for the whole run: a machine on which the separation was
installed afterwards went on saying no until it was restarted. Nothing
called the deep ask, and nothing tried to put the separation back
although the program installs over pip already.

Sections: the attempt is made once and no second time; a test run
installs nothing; what is reported when the attempt worked and when it
did not; that every start measures again instead of reading an answer
from earlier in the run; and that what does not fit in the cell of a
row stands in the line under the table.

Nothing is installed and no interpreter is started: pip and the one
call that starts an interpreter are both answered from here, so what
is measured is what the program does with those answers.
"""
import contextlib
import io
import os
import shutil
import sys
import tempfile
import time
import the_program

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
# Nothing is installed while this runs. run.sh sets this for the whole
# suite; it is set here too, so a run started by hand installs nothing.
os.environ.setdefault("VPM_SILENT", "1")
HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = the_program.SCRIPT
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


class Driven(object):
    """pip and the call that starts an interpreter, answered from here.

    *imports* is the list of answers the import of pyannote gives, one
    per ask, and *mended* what pip reports back. Every ask is written
    down, so how often each was reached is a measurement and not a
    guess.
    """

    def __init__(self, imports, mended=False):
        self.imports, self.mended = list(imports), mended
        self.asked, self.installed, self.said = [], [], []

    def __enter__(self):
        self.was_run = vpm.subprocess.run
        self.was_pip = vpm.pip_repair
        vpm.subprocess.run = self.run
        vpm.pip_repair = self.pip
        vpm.forget_speaker_split()
        return self

    def run(self, command, *_a, **_k):
        self.asked.append(list(command))
        answer = type("Answer", (object,), {})()
        answer.returncode = 0 if (self.imports.pop(0)
                                  if self.imports else False) else 1
        answer.stderr, answer.stdout = b"ImportError: no pyannote here", b""
        return answer

    def pip(self, packages):
        self.installed.append(tuple(packages))
        return self.mended

    def note(self, text, _share):
        self.said.append(text)

    def __exit__(self, *_trouble):
        vpm.subprocess.run = self.was_run
        vpm.pip_repair = self.was_pip
        vpm.forget_speaker_split()


print("1. The attempt is made once, and no second time")

# Two recordings in a row on a machine with no way in: the import
# fails before and after the install, so the second call finds the
# same fault the first one found.
with Driven([False, False, False, False], mended=True) as driven:
    first = vpm.speaker_split_mend(driven.note)
    second = vpm.speaker_split_mend(driven.note)
check("a second recording does not start the same install again",
      len(driven.installed) == 1 and first is False and second is False,
      "pip was asked %d times with %s; the two answers were %r and %r"
      % (len(driven.installed), driven.installed, first, second))
check("and the window is told once that something is being put back",
      len(driven.said) == 1,
      "%d lines said: %s" % (len(driven.said), driven.said))


print("\n2. A test run installs nothing")

# The real pip_repair here, with the call that starts a process
# answered from this file: what is measured is whether it reaches that
# call at all.
started = []


def counted(command, *_a, **_k):
    started.append(list(command))
    answer = type("Answer", (object,), {})()
    answer.returncode, answer.stdout, answer.stderr = 0, b"", b""
    return answer


was_run = vpm.subprocess.run
fenced = tempfile.mkdtemp(prefix="vpm_mend_home_")
was_home = dict((name, os.environ.get(name))
                for name in ("HOME", "APPDATA", "XDG_CONFIG_HOME",
                             "VPM_SILENT"))
try:
    vpm.subprocess.run = counted
    silent_answer = vpm.pip_repair(vpm.SPEAKER_PACKAGES)
    silent_started = list(started)
    # The other direction, and the copy is what holds the program: a
    # run without the mark would install for real, so the three places
    # a setting could land point at a folder thrown away below.
    del started[:]
    for name in ("HOME", "APPDATA", "XDG_CONFIG_HOME"):
        os.environ[name] = fenced
    os.environ.pop("VPM_SILENT", None)
    # What it says goes to print, and a line of the program's between
    # two judgements is read as this test's own.
    with contextlib.redirect_stdout(io.StringIO()):
        loud_answer = vpm.pip_repair(vpm.SPEAKER_PACKAGES)
    loud_started = list(started)
finally:
    vpm.subprocess.run = was_run
    for name, what in was_home.items():
        if what is None:
            os.environ.pop(name, None)
        else:
            os.environ[name] = what
    shutil.rmtree(fenced, ignore_errors=True)

check("a run that marks itself silent starts no installer at all",
      silent_started == [] and silent_answer is False,
      "%d processes started (%s), and it answered %r"
      % (len(silent_started), silent_started[:1], silent_answer))
HEAD = [sys.executable, "-m", "pip", "install", "-U"]
check("without that mark pip is asked once, with -U and the packages last",
      len(loud_started) == 1 and loud_started[0][:len(HEAD)] == HEAD
      and loud_started[0][len(HEAD):] == list(vpm.SPEAKER_PACKAGES),
      "%d processes started; the first was %s, wanted %s and %s after it"
      % (len(loud_started), loud_started[:1], HEAD,
         list(vpm.SPEAKER_PACKAGES)))

# What the repair names has to be what this project really installs.
# Read out of pyproject.toml rather than written down again: a package
# renamed there and not here would put back something nobody ships.
DEPENDS = io.open(os.path.join(os.path.dirname(HERE), "pyproject.toml"),
                  encoding="utf-8").read().split("dependencies = [")[1]
DEPENDS = DEPENDS.split("]")[0]
missing = [one for one in vpm.SPEAKER_PACKAGES
           if ('"%s"' % one) not in DEPENDS]
check("and every package it names is one this project depends on",
      not missing,
      "%d of %d named nowhere in the project's own list: %s"
      % (len(missing), len(vpm.SPEAKER_PACKAGES), missing))


print("\n3. What is reported when it worked, and when it did not")

# The separation itself is answered from here as well: what is being
# measured is whether the job goes on to it at all, and a real one
# would fetch a model and spend minutes on the graphics unit.
reached = []


def instead(source, count=0, report=None, stopping=None):
    reached.append(source)
    return [("A", [(0.0, 1.0)])], ""


was_cached = vpm.speaker_split_cached
answers = []
try:
    vpm.speaker_split_cached = instead
    # It cannot run, pip puts it back, and the ask after the install
    # goes through: that is the second answer in the list.
    with Driven([False, True], mended=True) as driven:
        vpm.speaker_split_work("/tmp/no such recording.wav", 0,
                               driven.note, lambda: False, answers.append)
    del reached[:]
    with Driven([False, False], mended=False) as driven:
        vpm.speaker_split_work("/tmp/no such recording.wav", 0,
                               driven.note, lambda: False, answers.append)
    after_failure = list(reached)
finally:
    vpm.speaker_split_cached = was_cached

worked, failed = answers[0][3], answers[1][3]
check("an install that worked leaves nothing to report",
      worked == "",
      "it reported %r, wanted nothing at all" % (worked,))
check("and the separation itself is then reached",
      len(answers[0][2]) == 1,
      "%d voices came back, wanted 1 -- the job stopped before the "
      "separation although the install went through"
      % (len(answers[0][2]),))
check("an install that did not work stops short of the separation",
      after_failure == [] and failed != "",
      "the separation was reached %d times and %d characters were "
      "reported" % (len(after_failure), len(failed)))


print("\n4. Every start measures again")

with Driven([True]) as driven:
    # A no kept from earlier in the run, and an import that would
    # answer yes if it were asked.
    vpm._SPEAKER_READY = False
    answers = []
    was_cached = vpm.speaker_split_cached
    try:
        vpm.speaker_split_cached = instead
        vpm.speaker_split_work("/tmp/no such recording.wav", 0,
                               driven.note, lambda: False, answers.append)
    finally:
        vpm.speaker_split_cached = was_cached
    stale = answers[0][3]
    asks = len(driven.asked)
check("a no kept from earlier in the run does not survive the next start",
      stale == "" and asks == 1,
      "it reported %r after %d asks of the interpreter, wanted nothing "
      "after one" % (stale, asks))


print("\n5. What does not fit in the cell stands under the table")

from PySide6 import QtWidgets

app = QtWidgets.QApplication.instance() or QtWidgets.QApplication([])
line = QtWidgets.QWidget()
words = QtWidgets.QLabel("")
never = QtWidgets.QPushButton("")
with Driven([False]):
    NOTE = (os.path.abspath("/tmp/no such recording.wav"),
            vpm.speaker_split_trouble(), vpm.COLOURS["error"])
UNDER = vpm.speaker_split_missing()
# The suite switches the separation off outright, and a switched-off
# separation says nothing at all. This section is about the line the
# window shows while it is on.
was_off = vpm.SPEAKER_SPLIT_OFF
try:
    vpm.SPEAKER_SPLIT_OFF = False
    vpm.split_line_write(line, words, never, True, False, True, NOTE)
    shown, hidden = words.text(), line.isHidden()
    red = vpm.COLOURS["error"] in words.styleSheet()
    # The same line once the fault is gone, on a machine nobody has
    # answered for yet: the project's own question, in its own colour.
    vpm.split_line_write(line, words, never, None, False, True, None)
    after, still_red = words.text(), vpm.COLOURS["error"] in words.styleSheet()
finally:
    vpm.SPEAKER_SPLIT_OFF = was_off

check("the line under the table carries what did not fit in the cell",
      shown == UNDER and not hidden and red,
      "it showed %r (wanted %r), hidden %r, in the fault colour %r"
      % (shown[:60], UNDER[:60], hidden, red))
check("and it asks the project's own question again once that is over",
      after and UNDER not in after and not still_red,
      "it now shows %r, in the fault colour %r"
      % (after[:70], still_red))

print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
