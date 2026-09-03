# -*- coding: utf-8 -*-
"""Nothing the speech recogniser prints reaches the screen in its words.

The recogniser macOS brings with it writes one line about itself when
it is done. That line went straight into the progress bar of the run,
in its own keywords and in English whatever the run's language. The
sections: the timing line turned into a sentence of ours, in both
languages; a line nobody expected passed on as the fault it is; and the
same thing seen from outside, with the recogniser replaced by a
stand-in that writes exactly the line the real one writes.
"""
import os
import sys
import time
import io
import importlib.util
import contextlib

HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = os.environ.get("VPM_SCRIPT") or os.path.join(
    os.path.dirname(HERE), "videopodcast_magic.py")
spec = importlib.util.spec_from_file_location("vpm", SCRIPT)
vpm = importlib.util.module_from_spec(spec)
sys.modules["vpm"] = vpm
spec.loader.exec_module(vpm)

began = time.time()
done = 0
bad = []


def check(name, ok, extra=""):
    global done
    done += 1
    print("  %-58s %s %s" % (name, "ok" if ok else "FAIL", extra))
    if not ok:
        bad.append("%s [%s]" % (name, extra or "no numbers"))


# The line the recogniser really writes, from the format string in the
# Swift source of the program itself.
NOTE = "LOCALE de_DE SETUP 0.10 SECONDS 25.75"
# Its own keywords. None of them may reach a user.
KEYWORDS = ("LOCALE", "SETUP", "SECONDS")

print("1. The timing line becomes a sentence of ours")
vpm.set_language("en")
said = vpm.speech_note_said(NOTE)
left = [w for w in KEYWORDS if w in said]
check("the recogniser's own keywords do not reach the screen", not left,
      "%d of %d still in %r" % (len(left), len(KEYWORDS), said[:60]))
check("and the sentence is the one the catalogue holds",
      said == vpm.T('  Recognised in %s: ready in %s s, heard in %s s')
      % ("de-DE", "0.1", "25.8"),
      "%r against %r" % (said[:60], (vpm.T(
          '  Recognised in %s: ready in %s s, heard in %s s')
          % ("de-DE", "0.1", "25.8"))[:60]))
check("and the two times it measured are still in it",
      "0.1" in said and "25.8" in said,
      "%r -- wanted the 0.1 s of setup and the 25.75 s rounded to 25.8"
      % said[:70])

print("\n2. And it reads German in a German run")
vpm.set_language("de")
german = vpm.speech_note_said(NOTE)
vpm.set_language("en")
# The numbers go through the decimal mark too, so the German line
# carries commas. That is the whole point: the sentence was turned
# and the number was left English.
check("the German run gets the German sentence",
      german == vpm.CATALOGUE["de"][
          '  Recognised in %s: ready in %s s, heard in %s s']
      % ("de-DE", "0,1", "25,8"),
      "%r" % german[:70])
check("and German and English are not the same line",
      german != said, "%r against %r" % (german[:40], said[:40]))

print("\n3. A line nobody expected is passed on as a fault")
vpm.set_language("en")
odd = vpm.speech_note_said("ERR something went wrong")
check("an unexpected line goes out as the recogniser's complaint",
      odd == vpm.T('  The speech recognition reports: %s')
      % "ERR something went wrong",
      "%r" % odd[:70])

print("\n4. From outside: what the run prints while recognising")
here = None
try:
    import tempfile
    here = tempfile.mkdtemp(prefix="vpm_speechnote_")

    class Answer(object):
        returncode = 0
        stdout = (NOTE + "\n").encode("utf-8")

    def stand_in(argv, **named):
        """The recogniser, replaced: it writes its line and no words.

        At least as strict as the real one -- it writes nothing into
        the words file, so anything the run prints comes from the note
        and from nowhere else.
        """
        return Answer()

    was_program, was_run = vpm.recogniser_program, vpm.subprocess.run
    vpm.recogniser_program = lambda: os.path.join(here, "recogniser")
    vpm.subprocess.run = stand_in
    caught = io.StringIO()
    try:
        with contextlib.redirect_stdout(caught):
            words = vpm.macos_words(os.path.join(here, "sound.wav"), "de")
    finally:
        vpm.recogniser_program, vpm.subprocess.run = was_program, was_run
    printed = [l for l in caught.getvalue().splitlines() if l.strip()]
    raw = [l for l in printed if any(w in l for w in KEYWORDS)]
    check("the stand-in was reached and the run printed its line",
          len(printed) == 1 and words == [],
          "%d line(s) printed, %s word(s) read"
          % (len(printed), "no" if words is None else len(words)))
    check("and no line of the output carries the recogniser's keywords",
          not raw, "%d of %d lines: %s"
          % (len(raw), len(printed), (raw or [""])[0][:60]))
    check("and the line that was printed went through the catalogue",
          printed == [vpm.T(
              '  Recognised in %s: ready in %s s, heard in %s s')
              % ("de-DE", "0.1", "25.8")],
          "%r" % (printed or [""])[0][:70])
finally:
    if here:
        import shutil
        shutil.rmtree(here, ignore_errors=True)

print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
