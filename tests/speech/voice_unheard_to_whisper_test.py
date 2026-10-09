# -*- coding: utf-8 -*-
"""A language macOS does not offer goes to Whisper, not the system's.

Asked for a language its list lacks, the recognition macOS brings with
it heard in the machine's own language and wrote those words down.
Sections: the language missing from the list -- nothing handed to
macOS, one line naming the language, Whisper taking the run -- then a
list that never came, where the code still goes on as before.

The recogniser is stood in for by something that does what the real
one does with a locale it does not know: it hears in the system's.
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
import the_program
SCRIPT = the_program.SCRIPT
import contextlib
import io
import shutil
import subprocess
import tempfile
import time
vpm = the_program.load()

began = time.time()
done = 0
bad = []


def check(name, ok, extra=""):
    global done
    done += 1
    print("  %-58s %s %s" % (name, "ok" if ok else "FAIL", extra))
    if not ok:
        bad.append("%s [%s]" % (name, extra or "no numbers"))


vpm.set_language("en")

# What this Mac offers in the stand-in: no Dutch among it.
OFFERED = ["en_US", "de_DE", "fr_FR"]


class Ran(object):
    """What subprocess.run gives back: the two fields macos_words reads."""

    def __init__(self, returncode, stdout):
        self.returncode = returncode
        self.stdout = stdout


class MacDoor(object):
    """Stand in for subprocess, and for the Swift recogniser behind it.

    Like the real one, it hears a locale it does not know in the
    machine's own, de_DE, and says so in its line. *listed* False
    makes its list fail, as a recogniser that will not say.
    """

    PIPE = subprocess.PIPE
    STDOUT = subprocess.STDOUT

    def __init__(self, listed=True):
        self.listed = listed
        self.handed = []

    def run(self, cmd, **_ignored):
        if list(cmd[1:]) == ["--locales"]:
            if not self.listed:
                return Ran(1, b"ERR no list")
            return Ran(0, ("REGION DE\n" + "\n".join(OFFERED) + "\n")
                       .encode("utf-8"))
        self.handed.append(cmd[3])
        heard_in = cmd[3] if cmd[3] in OFFERED else "de_DE"
        with open(cmd[2], "w", encoding="utf-8") as f:
            f.write("0.000\t0.400\tHallo\n0.400\t0.900\tWelt.\n")
        return Ran(0, ("LOCALE %s SETUP 0.10 SECONDS 0.20" % heard_in)
                   .encode("utf-8"))


folder = tempfile.mkdtemp(prefix="vpm_unheard_")
audio = os.path.join(folder, "mix_full.wav")
with open(audio, "wb") as f:
    f.write(b"\0" * 64)
calls = [0]


def through_door(door, work):
    """Run *work* with the recogniser stood in for; return what it printed."""
    was = (vpm.recogniser_program, vpm.subprocess)
    calls[0] += 1
    # A program of its own each time, so no list is read back from the
    # call before.
    vpm.recogniser_program = (
        lambda *a, **k: os.path.join(folder, "recog%d" % calls[0]))
    vpm.subprocess = door
    caught = io.StringIO()
    try:
        with contextlib.redirect_stdout(caught):
            result = work()
    finally:
        vpm.recogniser_program, vpm.subprocess = was
    return result, [l for l in caught.getvalue().splitlines() if l.strip()]


print("\n1. A language the list lacks")

door = MacDoor()
words, said = through_door(door, lambda: vpm.macos_words(audio, "nld"))
check("a language macOS does not list is not handed to macOS",
      words is None and door.handed == [],
      "Dutch was handed %s and came back with %s, wanted nothing handed "
      "and None" % (door.handed, None if words is None else
                    "%d words" % len(words)))

vpm.set_language("de")
door = MacDoor()
_words, said = through_door(door, lambda: vpm.macos_words(audio, "nld"))
wanted = vpm.T('  macOS hears no %s here, Whisper takes it') % vpm.T("Dutch")
check("one line says why, naming the language in the run's own",
      said == [wanted], "printed %r, wanted [%r]" % (said, wanted))
vpm.set_language("en")

was = (vpm.whisper_words, vpm.words_stored, vpm.words_cache_write)
vpm.whisper_words = lambda path, language="", install=True: [
    vpm.speech_word(0.0, 0.5, "Hallo")]
vpm.words_stored = lambda *a, **k: (None, "")
vpm.words_cache_write = lambda *a, **k: None
try:
    door = MacDoor()
    (words, took), _said = through_door(
        door, lambda: vpm.recognise_speech(audio, "nld"))
finally:
    vpm.whisper_words, vpm.words_stored, vpm.words_cache_write = was
check("and the run's recognition takes Whisper for it",
      took == vpm.WHISPER_MODEL and len(words or []) == 1,
      "the way was %r with %s words, wanted %r with 1"
      % (took, len(words or []), vpm.WHISPER_MODEL))


print("\n2. A list that never came")

door = MacDoor(listed=False)
words, _said = through_door(door, lambda: vpm.macos_words(audio, "nld"))
check("without a list the code still goes on to macOS",
      door.handed == ["nl"] and len(words or []) == 2,
      "Dutch was handed %s and heard %s words, wanted ['nl'] and 2"
      % (door.handed, len(words or [])))

shutil.rmtree(folder, ignore_errors=True)

print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
