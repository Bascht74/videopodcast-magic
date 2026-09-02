# -*- coding: utf-8 -*-
"""The preview shows the cut the run will really make.

Both ways end in camera_cut: the window through cut_statistics, the run
through write_cut_list -- and for a whole version the preview handed no
transcript along, so it showed a cut without the reaction cut while the
run made one with, each green on its own. Built from data and without a
window: the run writes the handover file, the preview reads it back and
is driven the way preview_compute drives it. First the material: that
the transcript moves the cut at all, and that the handover carries every
word of it. Then three cases, held against each other in that there is a
cut at all, in the number of shots, in the seconds and in the camera --
after a question, on a long monologue with the wide shot at the edges,
and with every camera taken. Then the transcript cut_statistics finds in
the handover itself where the caller sends none, and last the cut list
the written file carries, against both. Only the cut list is compared,
to the millisecond the handover writes; what the window rounds for its
own sentence is not.
"""
import collections
import contextlib
import io
import json
import os
import shutil
import sys
import tempfile
import time
import types

import importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = os.environ.get("VPM_SCRIPT") or os.path.join(
    os.path.dirname(HERE), "videopodcast-magic.py")

began = time.time()
spec = importlib.util.spec_from_file_location("vpm", SCRIPT)
vpm = importlib.util.module_from_spec(spec)
sys.modules["vpm"] = vpm
spec.loader.exec_module(vpm)
vpm.set_language("en")

done = 0
bad = []


def check(name, ok, extra=""):
    global done
    done += 1
    print("  %-58s %s %s" % (name, "ok" if ok else "FAIL", extra))
    if not ok:
        bad.append("%s [%s]" % (name, extra or "no numbers"))


ROOM = tempfile.mkdtemp(prefix="preview_is_the_run_")


def folder(name):
    """A folder of its own for one set of written files.

    One a run, and never the same one twice: two runs of one production
    into one folder would leave the second reading the first one's
    handover file, and the two ways would then agree by accident.
    """
    return tempfile.mkdtemp(prefix=name + "_", dir=ROOM)


def video(name):
    """A camera file's path. Nothing here is opened, so none is made."""
    return os.path.join(ROOM, name + ".mov")


# --------------------------------------------------------- the material
#
# Two speakers on two cameras and a free third one. The names of the
# cameras and of the speakers are the same on purpose: the cut list
# names a camera by the camera's name and the handover file by the track
# name, and where they differ the two lists cannot be laid on each other
# at all. That is a second question and time_all_ways_agree_test asks it.
LENGTH = 200.0
SPEECH = [("Presenter", [(0.0, 40.0), (50.0, 160.0), (190.0, 200.0)]),
          ("Guest", [(40.0, 50.0), (160.0, 190.0)])]
NAMES = ["Presenter", "Guest", "Wide"]
REF_CLIP = ("Presenter.mov", {"fps": 25.0, "tc": "10:00:00:00"})
TC_START = 36000.0


def said(first, last, closer):
    """Filler speech between two seconds, in sentences of six words."""
    out, t, n = [], first + 0.5, 0
    while t < last - 1.0:
        n += 1
        out.append(vpm.speech_word(t, t + 0.4,
                                   "wort" if n % 6 else closer))
        t += 0.6
    return out


# Presenter holds the floor longest, so he is the main speaker; the
# question is the guest's, and the answer is the Presenter's block that
# begins at 50 s. That is what a reaction cut needs, and without a
# question in the words this test cannot see the fault it exists for.
WORDS = (said(0.0, 40.0, "so.")
         + [vpm.speech_word(41.0, 41.4, "Und"),
            vpm.speech_word(41.6, 42.0, "dann"),
            vpm.speech_word(42.2, 42.8, "kam"),
            vpm.speech_word(43.0, 43.6, "das."),
            vpm.speech_word(44.0, 44.4, "Wie"),
            vpm.speech_word(44.6, 45.0, "hast"),
            vpm.speech_word(45.2, 45.6, "du"),
            vpm.speech_word(45.8, 46.2, "das"),
            vpm.speech_word(46.4, 46.8, "gemacht"),
            vpm.speech_word(47.0, 49.5, "eigentlich?")]
         + said(50.0, 160.0, "gut.")
         + said(160.0, 190.0, "genau.")
         + said(190.0, 200.0, "ende."))
# A precondition of the material, not a statement about the program:
# without a question mark in it the reaction cut never runs.
assert any(w["word"].endswith("?") for w in WORDS)


def settings(name, **over):
    """The run's settings, the same fields the command line carries."""
    made = dict(production=name, min_edit_duration=3.0, delay=0.3,
                wide_after=0.0, wide_length=5.0, wide_most=15.0,
                wide_latest=120.0, no_wide_edges=True, wide_shot=[],
                min_speech_to_switch=1.5, reaction_lead=1.5,
                reaction_gap=3.0, reaction_hold=0.7,
                on_question=vpm.SHOT_ANSWER, on_monologue="alternate",
                on_together="wide", on_uncertain="wide",
                on_silence="wide", silence_hold=1.0,
                in_point=None, out_point=None, lufs=None, intro=None,
                outro=None, resolve=False)
    made.update(over)
    return types.SimpleNamespace(**made)


def parts(names, assigned):
    """The three lists the run is handed: tracks, cameras, videos."""
    return ([{"name": who, "camera": video(cam)} for who, cam in assigned],
            [{"name": n, "video": video(n)} for n in names],
            [(video(n), {"fps": 25.0, "width": 1920, "height": 1080,
                         "duration": LENGTH}) for n in names])


def shots(cut):
    """One cut as (start, end, camera), to the millisecond.

    A thousandth is what the handover file itself writes, and a frame at
    25 is forty of them -- so this rounds away nothing anybody could see.
    """
    return [(round(float(a), 3), round(float(b), 3), str(n))
            for a, b, n in (cut or ())]


def the_run(args, tracks, cameras, videos, words=None):
    """What the run makes: the cut, and the handover file it leaves.

    The program's own printing goes into the bin -- it is one heading
    and three lines a case, and the judgements have to stay readable.
    """
    words = WORDS if words is None else words
    where = folder(args.production)
    with contextlib.redirect_stdout(io.StringIO()):
        cut, segs = vpm.write_cut_list(args, SPEECH, tracks, cameras,
                                       videos, where, TC_START, REF_CLIP,
                                       LENGTH, words=words)
        vpm.write_handover(args, tracks, cameras, videos, where, TC_START,
                           REF_CLIP, results=[], cut=cut, segment_list=segs,
                           length=LENGTH, words=words)
    js = os.path.join(where, vpm.safe_filename(args.production)
                      + "_resolve.json")
    with open(js, encoding="utf-8") as f:
        return shots(cut), json.load(f)


def the_preview(args, d, hand_the_words=True):
    """What the window shows, driven the way preview_compute drives it.

    The same three steps in the same order: the window is applied to the
    handover, the words are read out of it, and the numbers come from
    cut_statistics. *hand_the_words* off is the older shape of that call,
    which left the transcript to cut_statistics to find.
    """
    d, complaint = vpm.apply_time_window(d, "", "")
    if complaint:
        return None, complaint
    from_the_file = vpm.words_from_handover(d)
    picked = {switch.replace("-", "_"): getattr(args,
                                                switch.replace("-", "_"))
              for switch, _c, _d, _v, _s, _l in vpm.CUT_CHOICES}
    if hand_the_words:
        picked["words"] = from_the_file
    numbers = vpm.cut_statistics(
        d, args.min_edit_duration, args.delay, args.wide_after,
        args.wide_length, args.wide_latest, not args.no_wide_edges,
        vpm.cut_rules(min_speech=args.min_speech_to_switch,
                      reaction_lead=args.reaction_lead,
                      wide_holds=args.wide_length,
                      silence_hold=args.silence_hold,
                      wide_most=args.wide_most, **picked))
    if not numbers:
        return None, vpm.why_no_cut(d)
    return shots(numbers["cut"]), ""


def first_time_apart(here, there, one_name="the run", two_name="the preview"):
    """The first shot whose start or end differs, as a sentence."""
    for i, (one, two) in enumerate(zip(here, there), 1):
        if one[0] != two[0] or one[1] != two[1]:
            return ("shot %d runs %.3f-%.3f s in %s and %.3f-%.3f s in %s"
                    % (i, one[0], one[1], one_name, two[0], two[1], two_name))
    if len(here) == len(there):
        return "all %d shots stand at the same seconds" % len(here)
    return ("the %d shots they share stand at the same seconds, but %s has "
            "%d of them and %s %d"
            % (min(len(here), len(there)), one_name, len(here), two_name,
               len(there)))


def first_camera_apart(here, there, one_name="the run",
                       two_name="the preview"):
    """The first shot showing another camera, as a sentence."""
    for i, (one, two) in enumerate(zip(here, there), 1):
        if one[2] != two[2]:
            return ("shot %d shows %r in %s and %r in %s"
                    % (i, one[2], one_name, two[2], two_name))
    if len(here) == len(there):
        return "all %d shots name the same camera" % len(here)
    return ("the %d shots they share name the same camera, but %s has %d of "
            "them and %s %d"
            % (min(len(here), len(there)), one_name, len(here), two_name,
               len(there)))


def how_apart(here, there, one_name="the run", two_name="the preview"):
    """Where two cuts part company: the seconds first, then the cameras."""
    if here == there:
        return ("all %d shots stand at the same seconds and name the same "
                "camera" % len(here))
    if ([(a, b) for a, b, _n in here] != [(a, b) for a, b, _n in there]
            or len(here) != len(there)):
        return first_time_apart(here, there, one_name, two_name)
    return first_camera_apart(here, there, one_name, two_name)


Verdict = collections.namedtuple("Verdict", "ok why")


def both_ways(args, names, assigned):
    """One case: the run's cut against the preview's, as four verdicts.

    In this order: that both ways produced a cut at all, then the number
    of shots, the seconds, the camera. The judging is left to the caller
    because a check is named by the sentence in its first argument, and
    a sentence put together while the test runs -- "%s: the same number
    of shots" % tag -- stands nowhere in the source. The register of
    counter-proofs reads those first arguments out of the file, so a
    name it cannot see is a check nobody can prove.
    """
    tracks, cameras, videos = parts(names, assigned)
    try:
        run, d = the_run(args, tracks, cameras, videos)
        preview, why = the_preview(args, d)
    except Exception as e:
        return (Verdict(False, "%s came back instead: %s"
                        % (type(e).__name__, str(e)[:90])),
                Verdict(False, "nothing to count"),
                Verdict(False, "nothing to compare"),
                Verdict(False, "nothing to compare"))
    made = Verdict(bool(run) and bool(preview),
                   "the run made %d shots, the preview %s"
                   % (len(run), "%d" % len(preview) if preview
                      else "none -- %s" % (why or "no reason given")))
    if not run or not preview:
        return (made,
                Verdict(False, "%d shots against %d"
                        % (len(run), len(preview or []))),
                Verdict(False, "one of the two lists is empty"),
                Verdict(False, "one of the two lists is empty"))
    return (made,
            Verdict(len(run) == len(preview),
                    "%d shots in the run, %d in the preview"
                    % (len(run), len(preview))),
            Verdict([(a, b) for a, b, _n in run]
                    == [(a, b) for a, b, _n in preview],
                    first_time_apart(run, preview)),
            Verdict([n for _a, _b, n in run] == [n for _a, _b, n in preview],
                    first_camera_apart(run, preview)))


ONE = settings("One", wide_shot=[video("Wide")])
TWO = settings("Two", wide_shot=[video("Wide")], wide_after=40.0,
               no_wide_edges=False)
THREE = settings("Three")
WITH_A_SPEAKER = [("Presenter", "Presenter"), ("Guest", "Guest")]

print("1. The material, before anything is held against anything")
# Two cuts of the same run, one with the transcript and one without. If
# they were the same the whole test would be green over words that do
# nothing, and the fault it exists for would walk straight through it.
_tracks, _cameras, _videos = parts(NAMES, WITH_A_SPEAKER)
try:
    with_words, handover = the_run(ONE, _tracks, _cameras, _videos)
    without_words, _ = the_run(settings("Silent", wide_shot=[video("Wide")]),
                               _tracks, _cameras, _videos, words=())
    carried = vpm.words_from_handover(handover)
    trouble = ""
except Exception as e:
    with_words, without_words, carried = [], [], []
    trouble = "%s came back instead: %s" % (type(e).__name__, str(e)[:90])
check("the transcript moves the cut, so dropping it has to show",
      bool(with_words) and with_words != without_words,
      trouble or "%d shots with the words and %d without; %s"
      % (len(with_words), len(without_words),
         first_time_apart(with_words, without_words,
                          "the cut with the words", "the cut without")))
check("the handover file hands every word of the transcript on",
      len(carried) == len(WORDS) and carried[:1] == WORDS[:1]
      and carried[-1:] == WORDS[-1:],
      trouble or "%d of %d words came back; the first %r against %r, the "
      "last %r against %r" % (len(carried), len(WORDS),
                              (carried[:1] or [{}])[0].get("word"),
                              WORDS[0]["word"],
                              (carried[-1:] or [{}])[0].get("word"),
                              WORDS[-1]["word"]))

print("\n2. After a question, where the picture goes to the answer early")
made, counted, timed, shown = both_ways(ONE, NAMES, WITH_A_SPEAKER)
check("after a question: both ways produce a cut", made.ok, made.why)
check("after a question: the same number of shots", counted.ok, counted.why)
check("after a question: every shot at the same second", timed.ok, timed.why)
check("after a question: every shot on the same camera", shown.ok, shown.why)

print("\n3. On a long monologue, with the wide shot at the edges")
made, counted, timed, shown = both_ways(TWO, NAMES, WITH_A_SPEAKER)
check("on a long monologue: both ways produce a cut", made.ok, made.why)
check("on a long monologue: the same number of shots", counted.ok, counted.why)
check("on a long monologue: every shot at the same second",
      timed.ok, timed.why)
check("on a long monologue: every shot on the same camera",
      shown.ok, shown.why)

print("\n4. With every camera taken, where there is no wide shot at all")
made, counted, timed, shown = both_ways(THREE, NAMES[:2], WITH_A_SPEAKER)
check("with every camera taken: both ways produce a cut", made.ok, made.why)
check("with every camera taken: the same number of shots",
      counted.ok, counted.why)
check("with every camera taken: every shot at the same second",
      timed.ok, timed.why)
check("with every camera taken: every shot on the same camera",
      shown.ok, shown.why)

print("\n5. The transcript the preview takes out of the handover itself")
# The window hands the words along; before it did, the cut still had
# them, because cut_statistics reads them out of the handover where the
# caller sends none. That second way is what kept the preview honest,
# so it is checked as its own claim rather than assumed.
try:
    _run, _d = the_run(settings("Four", wide_shot=[video("Wide")]),
                       *parts(NAMES, WITH_A_SPEAKER))
    _found, _why = the_preview(ONE, _d, hand_the_words=False)
except Exception as e:
    _run, _found, _why = None, None, "%s: %s" % (type(e).__name__,
                                                 str(e)[:90])
check("the preview takes the transcript out of the handover itself",
      bool(_run) and _found == _run,
      "the run made %d shots, the preview without a handed transcript %s"
      % (len(_run or []),
         ("%d -- %s" % (len(_found), how_apart(_run, _found)))
         if _found else "none -- %s" % (_why or "no reason given")))

print("\n6. The cut list the handover file itself carries")
# The two above are the cut in memory against the preview. What lands
# in Resolve is neither: it is the list written into the file, and a
# window showing a cut the file does not carry shows a film nobody will
# see. So the file is read back and held against both.
try:
    _made, _file = the_run(ONE, *parts(NAMES, WITH_A_SPEAKER))
    _carried = shots([(c["start"], c["end"], c["camera"])
                      for c in (_file.get("cut") or [])])
    _shown, _no = the_preview(ONE, _file)
except Exception as e:
    _made, _carried, _shown, _no = None, [], None, "%s: %s" % (
        type(e).__name__, str(e)[:90])
check("the handover file carries the cut the run made",
      bool(_made) and _carried == _made,
      "the run made %d shots, the file carries %d -- %s"
      % (len(_made or []), len(_carried),
         how_apart(_made or [], _carried, "the run", "the file")))
check("and the preview shows the cut the handover file carries",
      bool(_carried) and _shown == _carried,
      "the file carries %d shots, the preview shows %s"
      % (len(_carried),
         ("%d -- %s" % (len(_shown), how_apart(_carried, _shown, "the file",
                                               "the preview")))
         if _shown else "none -- %s" % (_no or "no reason given")))

shutil.rmtree(ROOM, ignore_errors=True)
print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
