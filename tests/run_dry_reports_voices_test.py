# -*- coding: utf-8 -*-
"""A dry run hands on the separation it read back instead of nothing.

Reading a separation that is already on this machine costs nothing, so
a dry run may do it: what it must not do is measure. The sections are
a machine that has never separated this recording, one that has, and
one whose recording has been written since -- where there is nothing
to read back and the dry run measures nothing again.

The model is stood in for by a table, so what is counted is who asks
for it, not what a model hears.
"""
import os
import the_program
HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = the_program.SCRIPT
import io
import shutil
import sys
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
folder = tempfile.mkdtemp(prefix="vpm-dry-voices-")
# A store of its own: the suite hands every test one cache folder, and
# a separation another test left there would answer here for a file
# this one never saw.
os.environ["VPM_CACHE"] = tempfile.mkdtemp(prefix="vpm-dry-voices-store-")


def made(name):
    path = os.path.join(folder, name)
    with open(path, "wb") as f:
        f.write(b"0")
    return path


RECORDER = made("recorder.wav")
CAM = made("cam.mov")
TRACKS = [{"name": "recorder.wav", "source": RECORDER,
           "blocks": [RECORDER], "a": 0.0, "b": 1.0}]
asked = []


def fake_run(path, count=0, **kw):
    """Stand in for the model: a fixed answer, and note who asked."""
    asked.append((path, count))
    return [("SPEAKER_00", [(0.0, 4.0), (8.0, 12.0)]),
            ("SPEAKER_01", [(4.2, 7.8)])], ""


vpm.speaker_split_run = fake_run
vpm.speaker_split_available = lambda deep=False: True
vpm.media_seconds = lambda p: 20.0
vpm.SPEAKER_SPLIT_OFF = False


class Args(object):
    """As much of the parsed command line as the separation reads."""

    def __init__(self, **over):
        self.speakers_local = RECORDER
        self.speakers_from = None
        self.speakers_count = 0
        self.no_speakers_local = False
        self.dry_run = False
        self._speakers_of = {}
        self._camera_audio = None
        self.__dict__.update(over)


def separated(args):
    """What the separation handed back, and what it wrote to the log."""
    del asked[:]
    said = io.StringIO()
    kept, sys.stdout = sys.stdout, said
    try:
        out, _where = vpm.separation_for_run(args, TRACKS, {}, 0.0, 20.0,
                                             [CAM])
    finally:
        sys.stdout = kept
    return out, said.getvalue()


def forget_stored():
    """Empty this test's own store, and only ever its own."""
    kept = vpm.cache_folder("speakers") or ""
    for name in (os.listdir(kept) if kept else ()):
        os.unlink(os.path.join(kept, name))


print("1. A machine that has never separated this recording")
forget_stored()
nothing, log = separated(Args(dry_run=True))
check("with nothing stored a dry run measures nothing",
      asked == [], "the model was asked %d times %s, wanted none"
      % (len(asked), asked))
check("and hands nothing on either", nothing == [],
      "%d voices came back, wanted none" % len(nothing))
check("and the log says that is what happened",
      vpm.T('  (measuring only: nothing separated)') in log,
      "the log was %r" % log[-120:])

print("\n2. A machine that has separated it before")
real, _log = separated(Args())
check("a run without --dry-run measures it once",
      asked == [(RECORDER, 0)] and len(real) == 2,
      "the model was asked %d times %s and %d voices came back, "
      "wanted once and two" % (len(asked), asked, len(real)))

read_back, log = separated(Args(dry_run=True))
check("a dry run does not measure what is already stored",
      asked == [], "the model was asked %d times %s, wanted none"
      % (len(asked), asked))
check("and hands the stored voices on rather than nothing",
      read_back == real,
      "%d voices in the dry run against %d in the real one"
      % (len(read_back), len(real)))
check("and does not say it separated nothing",
      vpm.T('  (measuring only: nothing separated)') not in log,
      "the log was %r" % log[-120:])
check("and the list stands under the heading the real run gives it",
      vpm.as_head(vpm.T('\nSPEAKERS -- SEPARATED BY VOICE')) in log,
      "the log was %r" % log[-200:])
check("the log names one line per voice",
      log.count(" passage") == len(read_back),
      "%d lines with passages against %d voices"
      % (log.count(" passage"), len(read_back)))
check("and the first voice with the seconds it speaks",
      "SPEAKER_00" in log and "0:00:08.600 in 2 passages" in log,
      "the log was %r" % log[-200:])
check("and the second one, which speaks once, in the singular",
      "SPEAKER_01" in log and "0:00:04.000 in 1 passage\n" in log,
      "the log was %r" % log[-200:])

print("\n3. A recording written since it was separated")
os.utime(RECORDER, (2000, 2000))
stale, log = separated(Args(dry_run=True))
check("nothing stored fits it any more, so nothing is handed on",
      stale == [], "%d voices came back for a rewritten recording, "
      "wanted none" % len(stale))
check("and the dry run measures it no more than before",
      asked == [], "the model was asked %d times %s, wanted none"
      % (len(asked), asked))

shutil.rmtree(os.environ["VPM_CACHE"], ignore_errors=True)
shutil.rmtree(folder, ignore_errors=True)
print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
