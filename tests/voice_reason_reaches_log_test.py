# -*- coding: utf-8 -*-
"""Why the separation cannot run reaches the log, and not a guess.

The answer used to be a returncode and nothing else, and everything the
failed import wrote went to the null device -- so a program that was
installed, and whose import fell over a library beside it, was reported
as not installed. Then the log cut what it was handed at 200
characters, which is the width of a cell in the window and not the
width of a file.

Sections: what is kept from a failed import, what is kept from one that
worked, and what is kept when the interpreter cannot be started at all;
then the whole job, which puts the reason in the cell of the sheet, the
way back under it, and all of both in the log.

No interpreter is really asked. The one call that starts one is replaced
by an answer written here, so what is measured is what the program does
with that answer.
"""
import io
import os
import shutil
import sys
import tempfile
import time
import the_program

# Nothing is installed while this runs. run.sh sets it for the whole
# suite; set here as well, so a run started by hand installs nothing.
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


# What a failed import really writes: frames nobody can act on, and one
# last line that names the fault. This one is the fault of 4.9.2026, on
# a machine where pyannote was installed and imported anyway.
FELL_OVER = (b"Traceback (most recent call last):\n"
             b'  File "<string>", line 1, in <module>\n'
             b"    import pyannote.audio\n"
             b"ImportError: Can't determine version for bottleneck\n")
LAST = "ImportError: Can't determine version for bottleneck"


class Answered(object):
    """The one call that starts an interpreter, answered from here."""

    def __init__(self, code, said=b"", trouble=None):
        self.code, self.said, self.trouble = code, said, trouble

    def __enter__(self):
        self.was = vpm.subprocess.run
        vpm.subprocess.run = self.run
        vpm.forget_speaker_split()
        return self

    def run(self, *_a, **_k):
        if self.trouble is not None:
            raise self.trouble
        answer = type("Answer", (object,), {})()
        answer.returncode, answer.stderr, answer.stdout = \
            self.code, self.said, b""
        return answer

    def __exit__(self, *_trouble):
        vpm.subprocess.run = self.was
        vpm.forget_speaker_split()


print("\n1. What is kept from an import that failed")
with Answered(1, FELL_OVER):
    there = vpm.speaker_split_available()
    why = vpm.speaker_split_why()
check("the line that names the fault is kept, the frames are not",
      there is False and why == LAST,
      "available %r, kept %r, wanted %r" % (there, why, LAST))

# With something on the error channel all the same: an import that
# works can still print a warning there, and a warning is not a reason.
with Answered(0, b"DeprecationWarning: torchaudio is deprecated\n"):
    ready = vpm.speaker_split_available()
    quiet = vpm.speaker_split_why()
check("an import that worked leaves no reason behind",
      ready is True and quiet == "",
      "available %r, kept %r, wanted ''" % (ready, quiet))

with Answered(0, trouble=OSError("no such interpreter")):
    gone = vpm.speaker_split_available()
    said = vpm.speaker_split_why()
check("an interpreter that cannot be started is a reason too",
      gone is False and "no such interpreter" in said,
      "available %r, kept %r" % (gone, said))

print("\n2. The cell, the line under it, and the log")

# The fault of 6.9.2026, on a machine where the separation was
# installed: numpy would not load, and the one line that says why is
# longer than the 200 characters the log used to keep of it.
LONG_FALL = (b"Traceback (most recent call last):\n"
             b"ImportError: numpy._core.multiarray failed to import\n"
             b"Original error was: dlopen(/tmp/pyroom/numpy/_core/"
             b"_multiarray_umath.cpython-314-darwin.so, 0x0002): tried:"
             b" '/tmp/pyroom/numpy/_core/_multiarray_umath.so' (no such"
             b" file), '/tmp/elsewhere/_multiarray_umath.so' (no such"
             b" file), '/tmp/third/_multiarray_umath.so' (no such file)\n")
LONG_LAST = LONG_FALL.decode("utf-8").strip().splitlines()[-1]

here = tempfile.mkdtemp(prefix="vpm_split_log_")
was_log = vpm.log_path
answers = []


def worked_through(said, name):
    """One whole job against that answer, and the log it wrote."""
    where = os.path.join(here, name)
    del vpm._LOG_ASIDE[:]
    vpm.log_path = lambda: where
    with Answered(1, said):
        vpm.speaker_split_work("/tmp/no such recording.wav", 0,
                               lambda *_a: None, lambda: False,
                               answers.append)
    del vpm._LOG_ASIDE[:]
    return (io.open(where, encoding="utf-8").read()
            if os.path.isfile(where) else "")


try:
    kept = worked_through(FELL_OVER, "fell.log")
    # A second time with nothing said, so the way back is all there is.
    silent = worked_through(b"", "quiet.log")
    # And a third with a reason longer than a cell has room for.
    whole = worked_through(LONG_FALL, "long.log")
finally:
    vpm.log_path = was_log
    del vpm._LOG_ASIDE[:]
    shutil.rmtree(here, ignore_errors=True)

trouble = answers[0][3] if answers else "no answer at all"
first, _sep, rest = trouble.partition("\n")
WANTED = vpm.T('The speaker separation reports: %s') % LAST
check("the cell gets the reason and not a pointer to a log file",
      first == WANTED,
      "cell says %r, wanted %r" % (first, WANTED))
check("the way back stands under it, whole, for the line beneath the table",
      rest == vpm.speaker_split_missing(),
      "under it stands %r, wanted %r"
      % (rest, vpm.speaker_split_missing()))
check("and the reason itself stands in the log",
      LAST in kept,
      "%d characters of log, %r among them"
      % (len(kept), kept.strip()[-70:]))
check("where the import said nothing, the way back is logged instead",
      vpm.speaker_split_missing()[:40] in silent,
      "%d characters of log, %r among them"
      % (len(silent), silent.strip()[-70:]))
check("a reason wider than a cell reaches the log uncut",
      LONG_LAST in whole,
      "%d characters of reason against %d of log, which ends %r"
      % (len(LONG_LAST), len(whole), whole.strip()[-40:]))

print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
