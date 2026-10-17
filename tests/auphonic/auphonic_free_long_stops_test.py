# -*- coding: utf-8 -*-
"""A free account's Multitrack run past 21 min stops before anything goes up.

auphonic.com is never spoken to: `_curl_call` is replaced by a stand-in
answering /api/user.json and a production's creation, and ending the
run at any upload. Sections: the border -- past 21 minutes, on the free
plan, Multitrack only -- said as needing a paid plan, with Singletrack
and work without Auphonic as the way out; the stop before the upload,
past which a paying account and a free Singletrack run go on; the line
in the Auphonic box, red; and the preflight, which stops a run, only
warns a dry run, lets --anyway through and says the upload stops it
then, offers no --anyway without it, lets one recording through, and
counts the tracks of the window's plan as the run sends them -- a
recording set to "do not use" none, two rows of one name one, a
camera's own sound one -- and with no plan as the run names them: two
recordings of one guessed name or of one typed name one track, one
guess in two folders two. File lengths are stood in for.
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
import io
import json
import shutil
import tempfile
import time
import types
import wave
import the_program

began = time.time()

os.environ["VPM_NO_UPDATE_CHECK"] = "1"
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
vpm = the_program.load()
vpm.set_language("en")
vpm.load_api_key = lambda *a, **k: ""
vpm.show_progress = lambda text, share=None: None
T = vpm.T

done = 0
bad = []


def check(name, ok, extra=""):
    global done
    done += 1
    print("  %-62s %s %s" % (name, "ok" if ok else "FAIL", extra))
    if not ok:
        bad.append("%s [%s]" % (name, extra or "no numbers"))


KEY = "FAKEKEY-0000"
# The fields of /api/user.json the program reads, and the plan.
FREE_ACCOUNT = {"username": "testuser", "credits": 2.0,
                "is_paying_user": False}
PAID_ACCOUNT = dict(FREE_ACCOUNT, is_paying_user=True)


class Uploaded(Exception):
    """The run reached its upload."""


class Account(object):
    """Stands in for auphonic.com: answers the account, notes each call.

    An upload -- any call with a progress bar -- ends the run with
    Uploaded, having first written a mark into what the run prints.
    """

    def __init__(self, answer):
        self.answer = answer
        self.calls = []

    def __call__(self, key, arguments, output_binary=False, progress=False):
        self.calls.append([str(a) for a in arguments])
        if progress:
            print("<<the upload begins here>>")
            raise Uploaded()
        if any(str(a).endswith("/api/productions.json")
               for a in arguments):
            # A production is created, so a run that goes on reaches
            # its upload.
            return json.dumps({"status_code": 201,
                               "data": {"uuid": "PRODUCTION"}})
        return self.answer


def minutes(n):
    """How a number of whole minutes is said."""
    return T('%d min') % n


SAID = T('This Multitrack production is %s long. On the free plan '
         'auphonic.com takes one only up to about %s; a longer one needs '
         'a paid plan.')
WAY_OUT = T('For Singletrack, which the free plan takes at any length, set '
            'every track but one to "%s" -- where one track holds every '
            'voice. Or choose "%s" under Preset (--without-auphonic): the '
            'tracks are then mixed here.') % (
                vpm.label_of(vpm.IGNORE_AUDIO), vpm.label_of(vpm.PRESET_NONE))

# ---------------------------------------------------------- The border
print("The border, and how it is said")

FREE = {"hours": 2.0, "paying": False}
got = vpm.free_border_said(FREE, 21 * 60 + 1, True)
check("past 21 min a free Multitrack production is said to need a paid plan",
      bool(got) and got[0] == SAID % (minutes(22), minutes(21)),
      "21 min 1 s on the free plan: %r" % (got,))
check("the way out names Singletrack and work without Auphonic",
      bool(got) and got[1] == WAY_OUT, "advice %r" % ((got or ("", ""))[1],))
got = vpm.free_border_said(FREE, 21 * 60, True)
check("exactly 21 min on the free plan meets no border", got is None,
      "21 min on the free plan: %r" % (got,))
got = vpm.free_border_said(FREE, 22 * 60, False)
check("the border holds for Multitrack only, not Singletrack", got is None,
      "22 min Singletrack, free: %r" % (got,))
got = vpm.free_border_said(dict(FREE, paying=True), 22 * 60, True)
check("a paying account's Multitrack production may be longer", got is None,
      "22 min Multitrack, paid: %r" % (got,))
got = vpm.free_border_said(dict(FREE, paying=None), 22 * 60, True)
check("an account that names no plan meets no border", got is None,
      "22 min Multitrack, plan unknown: %r" % (got,))

# ------------------------------------------------- Before the upload
print("\nBefore the upload")

room = tempfile.mkdtemp(prefix="vpm_free_long_")
audio = os.path.join(room, "Presenter.wav")
with wave.open(audio, "wb") as w:
    w.setnchannels(1)
    w.setsampwidth(2)
    w.setframerate(48000)
    w.writeframes(b"\x00\x10" * 48000 * 3)
guest = os.path.join(room, "Guest.wav")
shutil.copyfile(audio, guest)
tracks = [{"name": "Guest", "axis": guest},
          {"name": "Presenter", "axis": audio}]


def run_said(account, single=False):
    """What a run of 25 min printed, how it ended, its calls.

    Multitrack with both tracks, or *single*: Singletrack with one.
    """
    stand_in = Account(json.dumps({"status_code": 200, "data": account}))
    vpm._curl_call = stand_in
    said = io.StringIO()
    old, sys.stdout = sys.stdout, said
    measure, vpm.media_seconds = vpm.media_seconds, lambda path: 25 * 60.0
    ended = ""
    try:
        if single:
            vpm.run_single_production(audio, "PRESETUUID", "Podcast", KEY,
                                      os.path.join(room, "back"))
        else:
            vpm.run_multitrack_production(KEY, "PRESETUUID", "Podcast",
                                          tracks, os.path.join(room, "back"))
    except Uploaded:
        ended = "uploaded"
    except Exception as why:
        ended = str(why)
    finally:
        sys.stdout = old
        vpm.media_seconds = measure
    return said.getvalue(), ended, stand_in.calls


text, ended, calls = run_said(FREE_ACCOUNT)
check("a free Multitrack run of 25 min stops before anything goes up",
      "<<the upload begins here>>" not in text and len(calls) == 1
      and calls[0][-1].endswith("/api/user.json"),
      "calls in order: %r; ended %r" % ([c[-1] for c in calls], ended))
check("the stop says the paid plan and the way out",
      ended == SAID % (minutes(25), minutes(21)) + " " + WAY_OUT,
      "ended with %r" % ended)
text, ended, calls = run_said(PAID_ACCOUNT)
check("a paying Multitrack run of 25 min goes on to auphonic.com",
      len(calls) >= 2 and "/api/preset/PRESETUUID" in calls[1][-1],
      "calls in order: %r; ended %r" % ([c[-1] for c in calls], ended))
text, ended, calls = run_said(FREE_ACCOUNT, single=True)
check("a free Singletrack run of 25 min goes on to its upload",
      ended == "uploaded" and "<<the upload begins here>>" in text,
      "calls in order: %r; ended %r" % ([c[-1] for c in calls], ended))

# ------------------------------------------------------------ The box
print("\nThe line in the Auphonic box")

from PySide6 import QtWidgets
app = QtWidgets.QApplication.instance() or QtWidgets.QApplication([])
holder = QtWidgets.QWidget()
layout = QtWidgets.QVBoxLayout(holder)
show = vpm.credit_row(layout)
line = holder.findChildren(QtWidgets.QLabel)[-1]
RED = vpm.COLOURS["error"]
show(FREE, True, 22 * 60)
check("the box names the paid plan and the way out past 21 min, in red",
      RED in line.styleSheet()
      and SAID % (minutes(22), minutes(21)) in line.text()
      and WAY_OUT in line.text(),
      "22 min: style %r, text %r" % (line.styleSheet(), line.text()))
show(FREE, True, 21 * 60)
check("a free Multitrack production of 21 min shows no border in the box",
      RED not in line.styleSheet() and WAY_OUT not in line.text(),
      "21 min: style %r, text %r" % (line.styleSheet(), line.text()))

# ------------------------------------------------------ The preflight
print("\nThe preflight")

LONG = {"Guest.wav": 25 * 60, "Presenter.wav": 15 * 60,
        "WideCam.mov": 15 * 60}
vpm.sample_count = lambda path: LONG.get(os.path.basename(path), 0) * vpm.SR
recordings = [guest, audio]
# A camera whose own sound the window makes a track; only its name and
# its length, stood in for above, are asked of it.
camera = os.path.join(room, "WideCam.mov")
shutil.copyfile(audio, camera)


def plan_of(name, *rows):
    """An assignment file holding *rows*, as the window writes the plan."""
    path = os.path.join(room, name + ".json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump({"tracks_of": list(rows), "cameras": []}, f)
    return path


def run_args(**changed):
    """A call as the run's parser leaves it, with the key handed over."""
    values = dict(without_auphonic=False, auphonic_done=None,
                  auphonic_key=KEY, in_point=None, out_point=None,
                  out=os.path.join(room, "out"), lufs=-16.0, anyway=False,
                  dry_run=False, no_preflight=False, preflight_again=False,
                  apart=(), together=(), no_follow_ups=False)
    values.update(changed)
    return types.SimpleNamespace(**values)


def border_found(on_line=recordings, videos=0, **changed):
    """The finding check_account gives on the border, or None.

    *on_line*: the recordings on the command line, *videos* how many
    cameras beside them.
    """
    vpm._curl_call = Account(json.dumps({"status_code": 200,
                                         "data": FREE_ACCOUNT}))
    found = vpm.check_account(run_args(**changed),
                              vpm.group_recording_parts(on_line), videos)
    hit = [b for b in found if b.text == SAID % (minutes(25), minutes(21))]
    return hit[0] if hit else None, found


def stopped(found):
    """The findings that would stop the run."""
    return [(b.kind, b.text) for b in found if b.kind == "abort"]


hit, found = border_found()
check("the preflight stops a free Multitrack run of 25 min",
      hit is not None and hit.kind == "abort" and hit.advice == WAY_OUT,
      "said: %r" % ([(b.kind, b.text, b.advice) for b in found],))
hit, found = border_found(dry_run=True)
check("a dry run is warned of the border, not stopped",
      hit is not None and hit.kind == "warning",
      "said: %r" % ([(b.kind, b.text) for b in found],))
hit, found = border_found(on_line=[guest])
check("the preflight lets a free run of one 25 min recording through",
      not stopped(found), "stops on: %r" % (stopped(found),))
hit, found = border_found(assign=plan_of(
    "unused", {"audio": guest, "blocks": [guest], "speakers": "Guest",
               "camera": ""}))
check('a recording set to "do not use" is no track to the preflight',
      not stopped(found), "both recordings on the line, one in the plan; "
      "stops on: %r" % (stopped(found),))
hit, found = border_found(assign=plan_of(
    "onename", {"audio": guest, "blocks": [guest], "speakers": "Guest",
                "camera": ""},
    {"audio": audio, "blocks": [audio], "speakers": "Guest", "camera": ""}))
check("two recordings of one name are one track to the preflight",
      not stopped(found), "both named Guest in the plan; stops on: %r"
      % (stopped(found),))
hit, found = border_found(on_line=[guest], videos=1, assign=plan_of(
    "camera", {"audio": guest, "blocks": [guest], "speakers": "Guest",
               "camera": ""},
    {"audio": camera, "blocks": [camera], "speakers": "Presenter",
     "camera": camera, "camera_audio": True, "from_camera": camera}))
check("a camera's own sound is a track to the preflight",
      hit is not None and hit.kind == "abort",
      "one recording on the line, the camera's sound beside it in the "
      "plan; said: %r" % ([(b.kind, b.text) for b in found],))
# No plan: the run names each recording itself -- a name typed with
# --speaker-name, else the file name's guess, alike only within one
# folder -- and joins those of one name into one track.
first = os.path.join(room, "Presenter A.wav")
second = os.path.join(room, "Presenter B.wav")
apart = os.path.join(room, "elsewhere", "Presenter A.wav")
os.makedirs(os.path.dirname(apart))
for path in (first, second, apart):
    shutil.copyfile(audio, path)
LONG.update({"Presenter A.wav": 25 * 60, "Presenter B.wav": 15 * 60})
hit, found = border_found(on_line=[first, second])
check("two recordings of one guessed name are one track to it",
      not stopped(found), "Presenter A.wav and Presenter B.wav in one "
      "folder, no plan; stops on: %r" % (stopped(found),))
hit, found = border_found(speaker_name=[(guest, "Guest"), (audio, "Guest")])
check("two recordings given one name on the line are one track",
      not stopped(found), "both named Guest by --speaker-name, no plan; "
      "stops on: %r" % (stopped(found),))
hit, found = border_found(on_line=[first, apart])
check("one guessed name in two folders is two tracks to it",
      hit is not None and hit.kind == "abort",
      "Presenter A.wav in two folders, no plan; said: %r"
      % ([(b.kind, b.text) for b in found],))


def preflight_returns(**changed):
    """What run_preflight returns for a free account, and what it said."""
    vpm._curl_call = Account(json.dumps({"status_code": 200,
                                         "data": FREE_ACCOUNT}))
    said = io.StringIO()
    old, sys.stdout = sys.stdout, said
    try:
        back = vpm.run_preflight(run_args(**changed), recordings, [])
    except Exception as why:
        back = "raised %s: %s" % (type(why).__name__, why)
    finally:
        sys.stdout = old
    return back, said.getvalue()


def last_line(text):
    """The report's last line, which says whether the run stops."""
    lines = vpm.strip_marks(text).strip().splitlines()
    return lines[-1].strip() if lines else ""


back, text = preflight_returns()
check("the run stops at the preflight", back == 1,
      "returned %r, wanted 1; last line %r" % (back, last_line(text)))
check("past the border the last line offers no --anyway",
      last_line(text) == T('\nStopped before the first long step.').strip(),
      "last line %r" % last_line(text))
back, text = preflight_returns(anyway=True)
check("--anyway passes the preflight", back == 0,
      "returned %r, wanted 0; last line %r" % (back, last_line(text)))
check("with --anyway the last line says the upload stops it",
      last_line(text) == T('    --anyway is set: it runs despite the points '
                           'above, but stops before the upload -- '
                           'auphonic.com would refuse this production.'
                           ).strip(), "last line %r" % last_line(text))

shutil.rmtree(room, ignore_errors=True)
print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
