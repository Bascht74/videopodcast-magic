# -*- coding: utf-8 -*-
"""A voice heard again may carry its name, and the table offers it.

Two recordings of the same two people, each separated, their voice
prints stored beside the separations. In order: the window lets a name
stand on a voice and on its own voice in the other recording, and holds
its start where the names are crossed or a recording's row carries the
name too; the net under the window's run line says the same; the
command line reads the prints out of the store and says the same; and
the table offers a new recording's voices the names already given,
never one that would clash. The prints are written out here by hand;
what the real model makes of real voices is voice_split_hears_two's.
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
import shutil
import tempfile
import time
import wave

import the_program

began = time.time()
vpm = the_program.load()
vpm.set_language("en")
done = 0
bad = []


def check(name, ok, extra=""):
    global done
    done += 1
    print("  %-58s %s %s" % (name, "ok" if ok else "FAIL", extra))
    if not ok:
        bad.append("%s [%s]" % (name, extra or "no numbers"))


folder = tempfile.mkdtemp(prefix="vpm_heard_named_")


def recording(name, seconds):
    """A short silent wav, so the store has a file to key on."""
    path = os.path.join(folder, name)
    with wave.open(path, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(16000)
        w.writeframes(b"\0\0" * 16000 * seconds)
    return path


def keep(path, segments, prints):
    """Store a separation and its prints the way the program does."""
    key = vpm.speaker_cache_key(path, vpm.speaker_model_mark(), 0)
    vpm.speaker_cache_write(key, segments)
    vpm.speaker_voices_write(key, prints)


# Presenter and Guest in both recordings; the model numbered them the
# other way round in the second, as it numbers by speaking time.
FIRST = recording("Room_A.wav", 1)
SECOND = recording("Room_B.wav", 2)
SEGMENTS = [("SPEAKER_00", [(0.0, 0.4)]), ("SPEAKER_01", [(0.5, 0.9)])]
PRINTS = {FIRST: {"SPEAKER_00": [1.0, 0.0, 0.0, 0.0],
                  "SPEAKER_01": [0.0, 1.0, 0.0, 0.0]},
          SECOND: {"SPEAKER_00": [0.1, 0.9, 0.3, 0.0],
                   "SPEAKER_01": [0.95, 0.05, 0.2, 0.1]}}
for p in (FIRST, SECOND):
    keep(p, SEGMENTS, PRINTS[p])
MATCHED = [(FIRST, "SPEAKER_00", "Presenter"), (FIRST, "SPEAKER_01", "Guest"),
           (SECOND, "SPEAKER_01", "Presenter"), (SECOND, "SPEAKER_00", "Guest")]
CROSSED = [(FIRST, "SPEAKER_00", "Presenter"), (FIRST, "SPEAKER_01", "Guest"),
           (SECOND, "SPEAKER_00", "Presenter"), (SECOND, "SPEAKER_01", "Guest")]


def voice_rows(named):
    """The window's voice rows, each name carrying its print as voices_build
    hangs it on."""
    rows = []
    for source, label, name in named:
        value = vpm.Value(name)
        value.heard = PRINTS[source][label]
        rows.append((vpm.voice_key(source, label), value, vpm.Value("Cam")))
    return rows


def held(voices, assign=()):
    """What the window's start says on the assignment tab, or None."""
    return vpm.missing_conditions([FIRST, SECOND], "Pilot", False,
                                  list(assign), [], voices,
                                  [FIRST, SECOND]).get(22)


#------------------------------------------------------------ the window

print("The window")
said = held(voice_rows(MATCHED))
check("a voice heard again may carry its name, and Start is free",
      said is None, "the sheet says %r, wanted nothing" % (said,))
said = held(voice_rows(CROSSED))
want = vpm.names_clash_said(["Guest", "Presenter"])
check("names crossed over two different voices still hold Start",
      said == want, "the sheet says %r, wanted %r" % (said, want))
FOURTH = recording("Room_D.wav", 1)
said = held(voice_rows(MATCHED),
            [([FOURTH], vpm.Value("Guest"), vpm.Value("Cam"))])
want = vpm.names_clash_said(["Guest"])
check("a recording's row with a heard-again voice's name still holds",
      said == want, "the sheet says %r, wanted %r" % (said, want))
bare = voice_rows(MATCHED)
for _k, value, _c in bare:
    value.heard = None
said = held(bare)
want = vpm.names_clash_said(["Guest", "Presenter"])
check("voices without a stored print never share a name",
      said == want, "the sheet says %r, wanted %r" % (said, want))


def net(named):
    """The error titles run_argv answers the window's voices with."""
    values = {"files": [], "rows": [], "cameras": [], "clip_kinds": {},
              "voices": [{"name": v.get(), "camera": "Cam", "key": k,
                          "heard": v.heard}
                         for k, v, _c in voice_rows(named)]}
    return [m[1] for m in vpm.run_argv(values)[2] if m[0] == "error"]


titles = net(MATCHED)
check("the net under the run line lets a heard-again voice's name by",
      titles == [], "error titles %s, wanted none" % titles)
titles = net(CROSSED)
check("and still stops names crossed over two different voices",
      titles == ["One name for two voices"],
      "error titles %s, wanted ['One name for two voices']" % titles)

#------------------------------------------------------ the command line

print("\nThe command line")


class Args(object):
    """The parsed line, as far as voices_clashing_of_run reads it."""
    assign = ""
    speakers_from = ""
    project_type = "cut"


def line(names_second):
    """The clash on a command line handed both separations, stored prints."""
    args = Args()
    given = vpm.speakers_for_project(FIRST, SEGMENTS, 0, {
        "SPEAKER_00": "Presenter", "SPEAKER_01": "Guest"})
    given["more"] = [vpm.speakers_for_project(SECOND, SEGMENTS, 0,
                                              names_second)]
    args._speakers_of = given
    return vpm.voices_clashing_of_run(args, [])


clash = line({"SPEAKER_01": "Presenter", "SPEAKER_00": "Guest"})
check("the command line lets a heard-again voice's name by", clash == [],
      "clashing %s, wanted none" % clash)
clash = line({"SPEAKER_00": "Presenter", "SPEAKER_01": "Guest"})
check("and refuses names crossed over two different voices",
      clash == ["Guest", "Presenter"],
      "clashing %s, wanted ['Guest', 'Presenter']" % clash)

#------------------------------------------------------------ the offer

print("\nThe offer")
named = voice_rows(MATCHED[:2])
lent = vpm.voice_names_known(SECOND, PRINTS[SECOND], named,
                             ["Presenter", "Guest"])
check("a new recording's voices are offered the names already given",
      lent == {"SPEAKER_00": "Guest", "SPEAKER_01": "Presenter"},
      "offered %s, wanted SPEAKER_00 Guest and SPEAKER_01 Presenter"
      % lent)
lent = vpm.voice_names_known(SECOND, PRINTS[SECOND], named,
                             ["Presenter", "Guest", "Guest"])
check("a name a recording's row carries too is not offered",
      lent == {"SPEAKER_01": "Presenter"},
      "offered %s, wanted SPEAKER_01 Presenter alone" % lent)
got = dict(vpm.speaker_label_names(
    SEGMENTS, {}, ["Speaker 1", "Speaker 2"], {"SPEAKER_00": "Speaker 2"}))
check("an offered stand-in name is kept, not counted on past",
      got.get("SPEAKER_00") == "Speaker 2",
      "named %s, wanted SPEAKER_00 as Speaker 2" % got)
state = {"speakers_by": vpm.ByFile(
    [(FIRST, {"segments": SEGMENTS, "count": 0,
              "names": {"SPEAKER_01": "Speaker 1"}}),
     (SECOND, {"segments": SEGMENTS, "count": 0,
               "names": {"SPEAKER_00": "Speaker 1"}})])}
kept = vpm.voices_lent(state, SECOND, PRINTS[SECOND],
                       {"SPEAKER_00": "Speaker 1"})
check("and a rebuilt table keeps it where its own voice carries it",
      kept == set(["SPEAKER_00"]),
      "kept %s, wanted SPEAKER_00" % sorted(kept))

shutil.rmtree(folder, ignore_errors=True)
print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
