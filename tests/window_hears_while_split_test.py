# -*- coding: utf-8 -*-
"""The words are written down while the speakers are being separated.

The recognition used to wait for the separation, because the recording
it wants was only named once the separation had stored its result. The
two use different machinery, so the shorter of them costs nothing
where it runs inside the longer.

The sections: both started on one road, words that come back before
any separation, and the window taking that road at all. Neither the
model nor a recogniser runs -- the separation is stood in for by one
that blocks until this test lets it go, so "while" is measured.
"""
import os
HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = os.environ.get("VPM_SCRIPT") or os.path.join(
    os.path.dirname(HERE), "videopodcast-magic.py")
import ast
import importlib.util
import shutil
import sys
import tempfile
import threading
import time
spec = importlib.util.spec_from_file_location("vpm", SCRIPT)
vpm = importlib.util.module_from_spec(spec); sys.modules["vpm"] = vpm
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


folder = tempfile.mkdtemp(prefix="vpm-while-split-")
# A store of its own, so a recognition another test left behind cannot
# answer here in place of the stand-in below.
os.environ["VPM_CACHE"] = tempfile.mkdtemp(prefix="vpm-while-split-store-")

SOURCE = os.path.join(folder, "Room.wav")
OTHER = os.path.join(folder, "Older.wav")
for path in (SOURCE, OTHER):
    with open(path, "wb") as f:
        f.write(b"0")

WORDS = [{"start": 1.0, "end": 1.4, "word": "Hallo"}]
LANGUAGE = "de-DE"

# How long a step may stand still before this is red. Never reached
# where the program works, so it costs nothing; the builder is about
# nine times slower than this machine, which is what makes it generous
# rather than tight.
PATIENCE = 30.0
LOOK_EVERY = 0.01


def stood_still(condition):
    """Wait for a condition; return how long it took, or None."""
    began_here = time.time()
    while time.time() - began_here < PATIENCE:
        if condition():
            return time.time() - began_here
        time.sleep(LOOK_EVERY)
    return None


split_entered = threading.Event()
split_may_finish = threading.Event()
split_came_back = threading.Event()
words_entered = threading.Event()
asked_for = []


def blocking_split(path, count=0, report=None, stopping=None):
    """The model, stood in for by one that will not finish on its own."""
    split_entered.set()
    split_may_finish.wait(PATIENCE)
    return [("SPEAKER_00", [(0.0, 4.0)])], ""


def listening(path, language=""):
    """The recogniser macOS brings, stood in for by one that notes."""
    asked_for.append((path, language))
    words_entered.set()
    return list(WORDS)


vpm.speaker_split_run = blocking_split
vpm.speaker_split_available = lambda deep=False: True
vpm.macos_words = listening
vpm.whisper_words = lambda p, language="", install=True: None


class Signal(object):
    """One of the window's signals, without Qt under it."""

    def __init__(self, name):
        self.name = name


class Bridge(object):
    """The window's signals, as much of them as this road touches."""

    def __init__(self):
        self.speakers_split_note = Signal("note")
        self.speakers_split = Signal("split")
        self.speakers_heard = Signal("heard")


bridge = Bridge()
told = []


def emit(signal, *values):
    """Stand in for bridge_emit: what the window would be told."""
    told.append((signal.name, values))
    if signal.name == "split":
        split_came_back.set()


print("1. Both are started, and the words do not wait")
state = {"speakers_run": 1}
split_run = {"busy": True, "stop": False}
vpm.speaker_split_begin(state, split_run, bridge, emit, SOURCE, 0, 1,
                        LANGUAGE)

took_split = stood_still(split_entered.is_set)
check("the separation is entered", took_split is not None,
      "it was still not entered after %.0f s" % PATIENCE
      if took_split is None else "after %.3f s" % took_split)

took_words = stood_still(words_entered.is_set)
still_running = not split_came_back.is_set()
check("the recognition is entered while the separation still blocks",
      took_words is not None and still_running,
      "the recogniser was %s and the separation had %s come back"
      % ("not entered after %.0f s" % PATIENCE if took_words is None
         else "entered after %.3f s" % took_words,
         "not" if still_running else "already"))

check("and it is asked for the recording being separated",
      asked_for == [(SOURCE, LANGUAGE)],
      "the recogniser was given %s, wanted [(%r, %r)]"
      % (asked_for, SOURCE, LANGUAGE))

heard = [v for name, v in told if name == "heard"]
check("its words reach the window on their own signal",
      heard == [((SOURCE, WORDS),)],
      "%d words came back on the heard signal, wanted 1: %s"
      % (len(heard), heard))

split_may_finish.set()
took_back = stood_still(split_came_back.is_set)
check("and the separation comes back after it, not before",
      took_back is not None,
      "it was still not back %.0f s after being let go" % PATIENCE
      if took_back is None else "after %.3f s" % took_back)

print("\n2. Words that come back before the separation does")
early = {"speakers_words_of": SOURCE}
woken = []
vpm.speech_words_done(early, (SOURCE, WORDS), lambda: woken.append(1))
check("words that arrive before any separation are kept",
      early.get("speakers_words") == WORDS and woken == [1],
      "the window holds %r and was woken %d times, wanted the words "
      "and once" % (early.get("speakers_words"), len(woken)))

stale = {"speakers_words_of": SOURCE}
vpm.speech_words_done(stale, (OTHER, WORDS), lambda: woken.append(1))
check("and words of a recording nobody asked about are dropped",
      stale.get("speakers_words") is None and len(woken) == 1,
      "the window holds %r and was woken %d times in all, wanted "
      "nothing and once" % (stale.get("speakers_words"), len(woken)))

print("\n3. The window takes that road")
tree = ast.parse(open(SCRIPT, encoding="utf-8").read())
kick = [n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)
        and n.name == "speaker_split_kick_off"]
calls = sorted(set(n.func.id for one in kick for n in ast.walk(one)
                   if isinstance(n, ast.Call)
                   and isinstance(n.func, ast.Name)))
check("the window starts the separation on the road that starts both",
      len(kick) == 1 and "speaker_split_begin" in calls,
      "%d functions are called speaker_split_kick_off and they call %s"
      % (len(kick), calls))

shutil.rmtree(os.environ["VPM_CACHE"], ignore_errors=True)
shutil.rmtree(folder, ignore_errors=True)
print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
