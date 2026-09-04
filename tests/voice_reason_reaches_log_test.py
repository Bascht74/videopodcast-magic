# -*- coding: utf-8 -*-
"""Why the separation cannot run reaches the log, and not a guess.

The answer used to be a returncode and nothing else, and everything the
failed import wrote went to the null device -- so a program that was
installed, and whose import fell over a library beside it, was reported
as not installed.

Sections: what is kept from a failed import, what is kept from one that
worked, and what is kept when the interpreter cannot be started at all;
then the whole job, which puts one short line in the cell of the sheet
and the reason itself in the log beside it.

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

print("\n2. The cell says one line, the log says why")
SHORT = vpm.T('Speaker separation not available. The log says why.')
here = tempfile.mkdtemp(prefix="vpm_split_log_")
log_here = os.path.join(here, "videopodcast-magic.log")
was_log = vpm.log_path
answers = []
try:
    vpm.log_path = lambda: log_here
    del vpm._LOG_ASIDE[:]
    with Answered(1, FELL_OVER):
        vpm.speaker_split_work("/tmp/no such recording.wav", 0,
                               lambda *_a: None, lambda: False,
                               answers.append)
    del vpm._LOG_ASIDE[:]
    kept = (io.open(log_here, encoding="utf-8").read()
            if os.path.isfile(log_here) else "")
    # A second time with nothing said, so the way back is all there is.
    del vpm._LOG_ASIDE[:]
    quiet_log = os.path.join(here, "quiet.log")
    vpm.log_path = lambda: quiet_log
    with Answered(1, b""):
        vpm.speaker_split_work("/tmp/no such recording.wav", 0,
                               lambda *_a: None, lambda: False,
                               answers.append)
    del vpm._LOG_ASIDE[:]
    silent = (io.open(quiet_log, encoding="utf-8").read()
              if os.path.isfile(quiet_log) else "")
finally:
    vpm.log_path = was_log
    del vpm._LOG_ASIDE[:]
    shutil.rmtree(here, ignore_errors=True)

trouble = answers[0][3] if answers else "no answer at all"
check("the cell gets one short line and not the reason",
      trouble == SHORT and LAST not in trouble,
      "cell says %r, wanted %r" % (trouble, SHORT))
check("and the reason itself stands in the log",
      LAST in kept,
      "%d characters of log, %r among them"
      % (len(kept), kept.strip()[-70:]))
check("where the import said nothing, the way back is logged instead",
      vpm.speaker_split_missing()[:40] in silent,
      "%d characters of log, %r among them"
      % (len(silent), silent.strip()[-70:]))

print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
