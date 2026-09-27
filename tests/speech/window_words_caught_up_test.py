# -*- coding: utf-8 -*-
"""The window writes its own transcript once the axis stands, and uses it.

The sections: where the words of a mix of two recordings land on the
window's axis; what is stored, so the same recordings are not heard
twice and a moved one is; one recording heard as it is, and the
separation's words taken as they are; the round -- not before the
axis, not while switched off -- with the preview saying "listening",
then carrying the words so the four settings open; its run told
where they are kept once they are there, for these recordings alone;
the prework bar always finished. A stand-in recogniser hears the mix.
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
import math
import struct
import tempfile
import time
import wave

os.environ["QT_QPA_PLATFORM"] = "offscreen"
# A store of its own, so words another test left behind cannot answer
# here in place of the stand-in below.
os.environ["VPM_CACHE"] = tempfile.mkdtemp(prefix="vpm-caught-up-store-")

from PySide6 import QtWidgets

began = time.time()
app = QtWidgets.QApplication(sys.argv[:1])
vpm = the_program.load()
# The cut box's greying reaches a name of the window: read it first.
vpm.window()
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


folder = tempfile.mkdtemp(prefix="vpm-caught-up-")
RATE = 48000


def recording(name, bursts, seconds):
    """A mono file, silent but for a tone at each (start, length)."""
    path = os.path.join(folder, name)
    frames = bytearray()
    for i in range(int(seconds * RATE)):
        t = i / float(RATE)
        loud = any(a <= t < a + n for a, n in bursts)
        frames += struct.pack(
            "<h", int(12000 * math.sin(2 * math.pi * 440 * t)) if loud else 0)
    with wave.open(path, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(RATE)
        w.writeframes(bytes(frames))
    return path


# A said at 0.5 s of its own time, B at 1.0 s of its own; B starts 2.5 s
# after A on the axis. So the words belong at 0.5 s and at 3.5 s.
A = recording("Presenter.wav", [(0.5, 0.3)], 3.0)
B = recording("Guest.wav", [(1.0, 0.3)], 3.0)
WANTED = [0.5, 3.5]

heard = []   # the file each call of the stand-in was handed


def onsets(path):
    """Where a tone begins in a 16-bit file, to 10 ms, read by hand."""
    with wave.open(path, "rb") as w:
        rate, width, count = (w.getframerate(), w.getsampwidth(),
                              w.getnframes())
        raw = w.readframes(count)
    assert width == 2, "the stand-in reads 16-bit sound only"  # material
    values = struct.unpack("<%dh" % (len(raw) // 2), raw)
    block = rate // 100
    out, on = [], False
    for k in range(0, len(values) - block, block):
        loud = max(abs(v) for v in values[k:k + block]) > 1000
        if loud and not on:
            out.append(round(k / float(rate), 2))
        on = loud
    return out


def stand_in(path, language=""):
    """The recogniser: a word wherever the file it is handed is loud."""
    heard.append(path)
    return [{"start": t, "end": t + 0.3, "word": "Hello?"}
            for t in onsets(path)]


vpm.macos_words = stand_in
vpm.whisper_words = lambda p, language="", install=True: None
vpm.SPEAKER_SPLIT_OFF = False
# The suite runs silent, and silent mode lets the window start no
# recogniser by itself; here the recogniser is stood in and asked.
vpm.listening_unasked = lambda: True


class Value(object):
    """What a row of the assignment answers with."""

    def __init__(self, v):
        self.v = v

    def get(self):
        return self.v


def lines(*paths):
    """Assignment rows for these recordings, each on a camera."""
    return [((p,), Value(os.path.basename(p)), Value("Cam.mov"))
            for p in paths]


def ground(offset_b=2.5):
    """The window's state with the axis standing: A at 10 s, B later."""
    return {"axis": {vpm.path_key(A): 10.0,
                     vpm.path_key(B): 10.0 + offset_b},
            "axis_clock": {}, "project_type": "", "speech_language": "en"}


PATIENCE = 30.0


def settled(held):
    """Wait until the thread has left its words; how long, or None."""
    t0 = time.time()
    while time.time() - t0 < PATIENCE:
        if not held.get("busy"):
            return time.time() - t0
        time.sleep(0.01)
    return None


def starts(words_rows):
    return [round(float(r[0]), 2) for r in words_rows]


print("1. Two recordings, mixed on the axis")
state, bar = ground(), []
rows = lines(A, B)
begun = vpm.window_words_round(state, rows,
                               lambda text, share: bar.append(share))
held = state.get("window_words") or {}
listening = vpm.window_words_joined(state, {"speakers": []}, rows)
told_early = vpm.window_words_reference(state, rows)
check("the round starts the transcript once the axis stands", begun,
      "round answered %r, held %r" % (begun, sorted(held)))
check("while it is written the preview says so",
      vpm.words_missing_why(listening) == "listening",
      "read %r" % (vpm.words_missing_why(listening),))
check("while it is written its run is told of no transcript",
      told_early is None, "told of %d recordings"
      % len((told_early or {}).get("recordings") or ()))
took = settled(held)
check("the transcript comes back", took is not None,
      "still busy after %.0f s" % PATIENCE)
told = vpm.window_words_reference(state, rows) or {}
kept, _way = vpm.window_words_kept(
    [tuple(r) for r in told.get("recordings") or ()], told.get("language"))
check("its run is told where the words are kept, and finds them there",
      [round(w["start"], 2) for w in kept or ()] == WANTED,
      "told %d recordings, read back at %s" % (
          len(told.get("recordings") or ()),
          [round(w["start"], 2) for w in kept or ()]))
got = vpm.window_words_joined(state, {"speakers": []}, rows)
check("the words lie where they were said on the window's axis",
      starts(got.get("words") or []) == WANTED,
      "at %s, wanted %s" % (starts(got.get("words") or []), WANTED))
check("the recogniser heard one mix, not the recordings",
      len(heard) == 1 and heard[0] not in (A, B),
      "handed %s" % [os.path.basename(p) for p in heard])
check("and the mix is gone again afterwards",
      not any(os.path.exists(p) for p in heard),
      "left %s" % [os.path.basename(p) for p in heard
                   if os.path.exists(p)])
check("the prework bar is told the start and the end",
      len(bar) >= 2 and bar[0] < 1.0 and bar[-1] == 1.0,
      "shares %s" % bar)
fresh = vpm.window_words_round(state, rows)
check("the next look says the words have arrived, once",
      fresh and not vpm.window_words_round(state, rows),
      "first look %r" % (fresh,))
check("with them the preview reads the words as there",
      vpm.words_missing_why(got) is True,
      "read %r" % (vpm.words_missing_why(got),))

print("\n2. What is stored")
state = ground()
vpm.window_words_round(state, rows)
settled(state["window_words"])
got = vpm.window_words_joined(state, {"speakers": []}, rows)
check("the same recordings again are read back, not heard again",
      len(heard) == 1 and starts(got.get("words") or []) == WANTED,
      "%d hearings, words at %s" % (len(heard),
                                    starts(got.get("words") or [])))
state = ground(offset_b=3.0)
vpm.window_words_round(state, rows)
settled(state["window_words"])
got = vpm.window_words_joined(state, {"speakers": []}, rows)
check("a recording moved on the axis is heard again, at its new place",
      len(heard) == 2 and starts(got.get("words") or []) == [0.5, 4.0],
      "%d hearings, words at %s" % (len(heard),
                                    starts(got.get("words") or [])))
other = vpm.window_words_joined(dict(state, axis=ground()["axis"]),
                                {"speakers": []}, rows)
check("words heard for another placing are not put into this preview",
      "words" not in other,
      "carried words at %s" % starts(other.get("words") or []))
told = vpm.window_words_reference(dict(state, axis=ground()["axis"]), rows)
check("words heard for another placing are not named to its run",
      told is None, "told of %d recordings, placed at %s"
      % (len((told or {}).get("recordings") or ()),
         [r[1] for r in (told or {}).get("recordings") or ()]))

print("\n3. One recording")
state = ground()
one = lines(B)
vpm.window_words_round(state, one)
settled(state["window_words"])
got = vpm.window_words_joined(state, {"speakers": []}, one)
check("one recording is heard as it is, not mixed",
      heard[-1] == B, "handed %s" % os.path.basename(heard[-1]))
check("and its words stay in its own time, the axis starting with it",
      starts(got.get("words") or []) == [1.0],
      "at %s" % starts(got.get("words") or []))
state = ground()
state["speakers_words_by"] = {A: [{"start": 2.0, "end": 2.4,
                                   "word": "Hi."}]}
count = len(heard)
vpm.window_words_round(state, lines(A))
got = vpm.window_words_joined(state, {"speakers": []}, lines(A))
check("the separation's words of that recording are taken as they are",
      len(heard) == count and starts(got.get("words") or []) == [2.0],
      "%d more hearings, words at %s"
      % (len(heard) - count, starts(got.get("words") or [])))
state = ground()
state["speakers_words_now"] = {A}
count = len(heard)
answer = vpm.window_words_round(state, lines(A))
check("and waited for while the separation writes them",
      not answer and not (state.get("window_words") or {}).get("busy")
      and len(heard) == count,
      "round answered %r, held %r, %d more hearings"
      % (answer, state.get("window_words"), len(heard) - count))

print("\n4. When it does not start")
state = ground()
state["axis"] = {}
check("not before the time axis stands",
      not vpm.window_words_round(state, rows)
      and not state.get("window_words"),
      "held %r" % (state.get("window_words"),))
state = ground()
state["axis_running"] = True
check("not while the axis is still being measured",
      not vpm.window_words_round(state, rows)
      and not state.get("window_words"),
      "held %r" % (state.get("window_words"),))
state = ground()
state["project_type"] = "sync"
check("not for a project that only synchronises",
      not vpm.window_words_round(state, rows)
      and not state.get("window_words"),
      "held %r" % (state.get("window_words"),))
vpm.SPEAKER_SPLIT_OFF = True
state = ground()
check("not where nothing may compute unasked",
      not vpm.window_words_round(state, rows)
      and not state.get("window_words"),
      "held %r" % (state.get("window_words"),))
vpm.SPEAKER_SPLIT_OFF = False

print("\n5. A recogniser that fails")


def breaks(path, language=""):
    raise RuntimeError("stand-in broke")


vpm.macos_words = breaks
state, bar = ground(), []
vpm.window_words_round(state, lines(A, B, recording("Third.wav", [], 1.0)),
                       lambda text, share: bar.append(share))
settled(state["window_words"])
check("the prework bar is finished even when the recognition fails",
      bar and bar[-1] == 1.0, "shares %s" % bar)
vpm.macos_words = stand_in

print("\n6. The four settings, greyed and opened")
holder = QtWidgets.QWidget()
into = QtWidgets.QVBoxLayout(holder)
parts = {}
vpm.cut_fields_build(into, parts)
note = vpm.question_note_build(vpm.label, QUIET)
into.addWidget(note)
FOUR = ["on-question", "reaction-lead", "wide-after", "wide-most"]
vpm.words_settings_grey(parts, note, "yet", True, QUIET)
yet_said = note.text()
vpm.words_settings_grey(parts, note, "listening", True, QUIET)
check("while it is written the four are grey, with a sentence of its own",
      [k for k in FOUR if not parts[k][1].isEnabled()] == FOUR
      and note.text() not in ("", yet_said) and QUIET in note.styleSheet(),
      "grey %s, note %r" % ([k for k in FOUR if not parts[k][1].isEnabled()],
                            note.text()[-60:]))
state = ground()
vpm.window_words_round(state, rows)
settled(state["window_words"])
d = vpm.window_words_joined(state, {"speakers": []}, rows)
vpm.words_settings_grey(parts, note, vpm.words_missing_why(d), True, QUIET)
check("with the window's own words the four open",
      [k for k in FOUR if parts[k][1].isEnabled()] == FOUR,
      "open %s" % [k for k in FOUR if parts[k][1].isEnabled()])

print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
