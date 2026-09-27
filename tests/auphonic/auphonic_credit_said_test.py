# -*- coding: utf-8 -*-
"""The account's plan and credit are said, first, in the log and the box.

auphonic.com is never spoken to: `_curl_call` is replaced by a stand-in
answering /api/user.json the way its API page shows it. Sections: the
account read; the lines before an upload -- the plan, the credit in
whole minutes, what a production needs rounded up to at least one, a
hint where the credit is short, and a warning with a note beside it
where a free account's Multitrack production is longer than the 21
minutes auphonic.com took, none on the border itself; a run that
says it before anything goes up and goes on; the line in the Auphonic
box, red where the production needs more, plain without a preset; the
box in the window, fed the length of the rows, shown once the account
answered, preset or not; and the check before the run, which says the
same lines first, asks once, and stops nothing. File lengths are stood
in for from the window on.
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
vpm.load_api_key = lambda: ""
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
# The example on auphonic.com/help/api/query.html, shortened to what the
# program reads and the fields beside it: 2.873 hours, a paying user.
PAID = {"username": "testuser", "credits": 2.87309201310154,
        "onetime_credits": 1.0, "recurring_credits": 1.87309201310154,
        "recharge_recurring_credits": 2.0, "is_paying_user": True}


class Account(object):
    """Stands in for auphonic.com: answers the account, notes each call.

    An upload -- any call with a progress bar -- ends the run with
    Uploaded, having first written a mark into what the run prints, so
    the order of the two can be read off the text.
    """

    def __init__(self, answer):
        self.answer = answer
        self.calls = []

    def __call__(self, key, arguments, output_binary=False, progress=False):
        self.calls.append([str(a) for a in arguments])
        if progress:
            print("<<the upload begins here>>")
            raise Uploaded()
        if isinstance(self.answer, Exception):
            raise self.answer
        return self.answer


class Uploaded(Exception):
    """The run reached its upload."""


def asked(answer):
    """What account_credit makes of *answer*, and the calls it made."""
    stand_in = Account(answer)
    vpm._curl_call = stand_in
    try:
        got = vpm.account_credit(KEY)
    except Exception as why:     # a fault is a finding here, not a crash
        got = "raised %s" % type(why).__name__
    return got, stand_in.calls


def verdict(account, seconds, multitrack):
    """The lines credit_verdict gives, as the run prints them."""
    return vpm.credit_verdict(account, seconds, multitrack)


# ------------------------------------------------------ 1. The account
print("1. The account read")

got, calls = asked(json.dumps({"status_code": 200, "data": PAID}))
check("the account is asked at /api/user.json and nothing is sent",
      len(calls) == 1 and calls[0] == ["https://auphonic.com/api/user.json"],
      "calls: %r" % (calls,))
check("the credit is read in hours, the one-time and recurring together",
      isinstance(got, dict)
      and abs((got["hours"] or 0) - 2.87309201310154) < 1e-9,
      "read %r, the answer said 2.87309201310154" % (got,))
check("a paying account is read as paying",
      isinstance(got, dict) and got["paying"] is True,
      "read %r" % (got,))

free = dict(PAID, is_paying_user=False, credits=0.5)
got, _ = asked(json.dumps({"status_code": 200, "data": free}))
check("a free account is read as free",
      isinstance(got, dict) and got["paying"] is False,
      "read %r" % (got,))

got, _ = asked(json.dumps({"status_code": 401, "error_message": "no"}))
check("a refused key gives no account, and no fault", got is None,
      "read %r" % (got,))
got, _ = asked("<html>not json</html>")
check("an answer that is not JSON gives no account, and no fault",
      got is None, "read %r" % (got,))
got, _ = asked(RuntimeError("curl: (6) could not resolve host"))
check("a call that fails gives no account, and no fault", got is None,
      "read %r" % (got,))

# ------------------------------------------------ 2. The lines before
print("\n2. The lines before an upload")


def minutes(n):
    """How a number of whole minutes is said."""
    return T('%d min') % n


def warned(lines):
    """The lines among *lines* marked as a warning."""
    return [one for one in lines if vpm.split_kind(one)[0] == "warning"]


PAYING = T('  Account at auphonic.com: paying.')
FREE_SAID = T('  Account at auphonic.com: free.')
UNKNOWN = T('  Account at auphonic.com: not known.')
ENOUGH = T('  Credit at auphonic.com: %s left, enough for the '
           '%s this production needs.')
SHORT = T('  Credit at auphonic.com: %s left, and this '
          'production needs %s -- not enough.')
TRIES = T('  Note: the run tries anyway. auphonic.com decides whether the '
          'production starts, and says so if it does not.')
WARN = T('  Warning: this Multitrack production is %s long, and on the '
         'free plan auphonic.com takes one only up to about %s.')
WHY = T('  Note: auphonic.com refuses a longer one at the start and charges '
        'nothing for it. The run tries anyway; if auphonic.com refuses, its '
        'own message follows.')

HOUR = {"hours": 1.0, "paying": True}
lines = verdict(HOUR, 30 * 60, False)
check("a paying account is said as paying, first",
      lines[:1] == [PAYING], "lines: %r" % (lines,))
check("credit that carries the production is said with what it needs",
      lines[1:] == [ENOUGH % (minutes(60), minutes(30))],
      "1 h left for 30 min: %r" % (lines,))
lines = verdict({"hours": 1.65, "paying": True}, 30 * 60, False)
check("credit is said in whole minutes, 1.65 h as 99 min",
      len(lines) == 2 and lines[1] == ENOUGH % (minutes(99), minutes(30)),
      "1.65 h left for 30 min: %r" % (lines,))
lines = verdict(HOUR, 90 * 60, False)
check("credit shorter than the production is said with what it needs",
      len(lines) >= 2 and lines[1] == SHORT % (minutes(60), minutes(90)),
      "1 h left for 90 min: %r" % (lines,))
check("short credit gives the hint that the run tries anyway",
      lines[2:] == [TRIES], "1 h left for 90 min: %r" % (lines,))
check("short credit is no warning",
      not warned(lines), "%d of %d lines marked a warning: %r"
      % (len(warned(lines)), len(lines), warned(lines)))

lines = verdict(HOUR, 20, False)
check("a 20 s production is said to need 1 min, never 0 min",
      lines[1:] == [ENOUGH % (minutes(60), minutes(1))],
      "1 h left for 20 s: %r" % (lines,))
lines = verdict(HOUR, 90, False)
check("a production of 1 min 30 s is said to need 2 min, rounded up",
      lines[1:] == [ENOUGH % (minutes(60), minutes(2))],
      "1 h left for 90 s: %r" % (lines,))
lines = verdict({"hours": 30 / 3600.0, "paying": True}, 20, False)
check("30 s of credit does not carry a 20 s production charged as 1 min",
      lines[1:] == [SHORT % (minutes(0), minutes(1)), TRIES],
      "30 s left for 20 s: %r" % (lines,))

FREE = {"hours": 2.0, "paying": False}
lines = verdict(FREE, 21 * 60 + 1, True)
check("a free account is said as free, first",
      lines[:1] == [FREE_SAID], "lines: %r" % (lines,))
check("a free Multitrack production past 21 min gets the border warning",
      lines[-2:] == [vpm.as_warn(WARN % (minutes(22), minutes(21))), WHY],
      "21 min 1 s on the free plan: %r" % (lines,))
check("the border line is marked a warning, and only that line",
      warned(lines) == [vpm.as_warn(WARN % (minutes(22), minutes(21)))],
      "%d of %d lines marked a warning: %r"
      % (len(warned(lines)), len(lines), warned(lines)))
lines = verdict(FREE, 21 * 60, True)
check("a free Multitrack production of exactly 21 min gets none",
      len(lines) == 2 and not warned(lines),
      "21 min on the free plan: %r" % (lines,))
lines = verdict(FREE, 22 * 60, False)
check("the border holds for Multitrack only, not Singletrack",
      len(lines) == 2, "22 min Singletrack, free: %r" % (lines,))
lines = verdict(dict(FREE, paying=True), 22 * 60, True)
check("a paying account's Multitrack production may be longer",
      len(lines) == 2, "22 min Multitrack, paid: %r" % (lines,))
lines = verdict(None, 30 * 60, True)
check("an account that did not answer is said as not known",
      lines == [UNKNOWN, T('  Credit at auphonic.com: not known -- the '
                           'account did not answer.')],
      "no answer: %r" % (lines,))
lines = verdict({"hours": 1.0, "paying": None}, 30 * 60, True)
check("an account that names no plan is said as not known",
      lines[:1] == [UNKNOWN], "no plan: %r" % (lines,))

# ------------------------------------------------------- 3. In the run
print("\n3. A run says it before anything goes up, and goes on")

room = tempfile.mkdtemp(prefix="vpm_credit_")
audio = os.path.join(room, "Presenter.wav")
with wave.open(audio, "wb") as w:
    w.setnchannels(1)
    w.setsampwidth(2)
    w.setframerate(48000)
    w.writeframes(b"\x00\x10" * 48000 * 3)


def said_by(step, account):
    """What *step* printed, run against *account*, and the calls."""
    stand_in = Account(json.dumps({"status_code": 200, "data": account}))
    vpm._curl_call = stand_in
    said = io.StringIO()
    old, sys.stdout = sys.stdout, said
    try:
        step()
    except Uploaded:
        pass
    except Exception as why:
        said.write("the run raised %s: %s\n" % (type(why).__name__, why))
    finally:
        sys.stdout = old
    return said.getvalue(), stand_in.calls


def run_said(account):
    """What a Singletrack run printed up to its upload, and the calls."""
    return said_by(lambda: vpm.run_single_production(
        audio, "PRESETUUID", "Podcast", KEY, os.path.join(room, "out"), 600,
        False), account)


# Three seconds of sound are charged as a whole minute.
ONE = minutes(1)

# Three seconds of sound against a fiftieth of an hour, 72 s: enough.
text, calls = run_said(dict(PAID, credits=0.02))
mark = text.find("<<the upload begins here>>")
enough = text.find(ENOUGH % (ONE, ONE))
check("a run asks the account before its upload, not after",
      len(calls) == 2 and calls[0][-1].endswith("/api/user.json")
      and "-F" in calls[1],
      "calls in order: %r" % ([c[-1] if "-F" not in c else "upload"
                               for c in calls],))
plan = text.find(PAYING)
check("a run says the account's plan before its upload",
      0 <= plan < mark, "plan line at %d, the upload at %d" % (plan, mark))
check("a run says the credit before its upload",
      0 <= enough < mark, "credit line at %d, the upload at %d"
      % (enough, mark))

# Three seconds of sound against a ten-thousandth of an hour, 0.36 s.
text, _ = run_said(dict(PAID, credits=0.0001))
mark = text.find("<<the upload begins here>>")
short = text.find(SHORT % (minutes(0), ONE))
check("a run whose credit is short says so before its upload",
      0 <= short < mark, "the short line at %d, the upload at %d"
      % (short, mark))
check("a run whose credit is short goes on to its upload",
      mark >= 0 and "the run raised" not in text,
      "upload at %d; %r" % (mark, text[-200:]))
check("nothing a run says about the account is a warning",
      not warned(text[:mark].splitlines()), "%r"
      % (warned(text[:mark].splitlines()),))

# A free account, two tracks of 25 minutes by the measure the run asks:
# the files are short, their length is stood in for.
tracks = [{"name": "Guest", "axis": audio},
          {"name": "Presenter", "axis": audio}]
measure, vpm.media_seconds = vpm.media_seconds, lambda path: 25 * 60.0
text, calls = said_by(lambda: vpm.run_multitrack_production(
    KEY, "PRESETUUID", "Podcast", tracks, os.path.join(room, "back")),
    dict(PAID, credits=2.0, is_paying_user=False))
vpm.media_seconds = measure
border = text.find(vpm.as_warn(WARN % (minutes(25), minutes(21))))
check("a free Multitrack run of 25 min gives the border warning",
      border >= 0 and text.find(WHY) > border, "%r" % text[:500])
check("and goes on to auphonic.com after it",
      len(calls) >= 2 and "/api/preset/PRESETUUID" in calls[1][-1],
      "calls in order: %r" % ([c[-1] for c in calls],))

# ------------------------------------------------------- 4. The box
print("\n4. The line in the Auphonic box")

from PySide6 import QtWidgets
app = QtWidgets.QApplication.instance() or QtWidgets.QApplication([])
holder = QtWidgets.QWidget()
layout = QtWidgets.QVBoxLayout(holder)
show = vpm.credit_row(layout)
line = holder.findChildren(QtWidgets.QLabel)[-1]
RED = vpm.COLOURS["error"]

show(None, False)
check("the box shows no credit line before the account answered",
      line.isHidden(), "hidden %s, text %r" % (line.isHidden(), line.text()))
show({"hours": 2.5, "paying": True}, False, 40 * 60)
check("the box shows what the account has left once it answered",
      not line.isHidden() and minutes(150) in line.text(),
      "hidden %s, text %r" % (line.isHidden(), line.text()))
check("credit that carries the production is not red",
      RED not in line.styleSheet(), "150 min for 40: style %r"
      % line.styleSheet())
show({"hours": 0.5, "paying": True}, False, 40 * 60)
check("the box is red when the production needs more than is left",
      RED in line.styleSheet(), "30 min for 40: style %r"
      % line.styleSheet())
show({"hours": 0.0, "paying": True}, False)
check("the box is red when no credit is left",
      RED in line.styleSheet(), "style %r" % line.styleSheet())
FREE_LINE = T('On the free plan auphonic.com takes a Multitrack production '
              'only up to about %s.') % minutes(21)
show({"hours": 2.0, "paying": False}, True, 22 * 60)
check("the box names the free Multitrack border past 21 min, in red",
      RED in line.styleSheet() and FREE_LINE in line.text(),
      "22 min: style %r, text %r" % (line.styleSheet(), line.text()))
show({"hours": 2.0, "paying": False}, True, 21 * 60)
check("a free Multitrack production of 21 min shows no border",
      RED not in line.styleSheet() and FREE_LINE not in line.text(),
      "21 min: style %r, text %r" % (line.styleSheet(), line.text()))
show({"hours": 2.0, "paying": False}, False, 40 * 60)
check("a free plan in Singletrack mode is said, and not red",
      RED not in line.styleSheet() and not line.isHidden()
      and T('%s -- free plan') % "" in line.text(),
      "style %r, text %r" % (line.styleSheet(), line.text()))
show({"hours": 2.5, "paying": True}, False, 40 * 60)
check("the box names a paying plan as paying",
      T('%s -- paying plan') % "" in line.text(),
      "text %r" % line.text())
show({"hours": 0.0, "paying": True}, False, None)
check("without a preset the box says what is left, and is not red",
      not line.isHidden() and minutes(0) in line.text()
      and RED not in line.styleSheet(),
      "no credit, no preset: hidden %s, style %r, text %r"
      % (line.isHidden(), line.styleSheet(), line.text()))

# ------------------------------------------------- 5. In the window
print("\n5. The box in the window, fed the rows")

vpm.api_key_source = lambda *a, **k: ("", "")
vpm.load_api_key = lambda *a, **k: ""
vpm._curl_call = Account(RuntimeError("auphonic.com is not asked here"))
LONG = {"Guest.wav": 25 * 60, "Presenter.wav": 15 * 60}
vpm.sample_count = lambda path: LONG.get(os.path.basename(path), 0) * vpm.SR
model = types.SimpleNamespace(
    assign_lines=[([os.path.join(room, n)], vpm.Value(n[:-4]),
                   vpm.Value(vpm.MIX_ONLY)) for n in sorted(LONG)],
    files=[(os.path.join(room, n), "audio") for n in sorted(LONG)],
    clip_kinds={})
check("one Multitrack production lasts as long as its longest track",
      vpm.run_tracks_of(model)[1:] == (True, 25 * 60.0),
      "two tracks of 25 and 15 min: %r" % (vpm.run_tracks_of(model),))
alone = types.SimpleNamespace(assign_lines=model.assign_lines, files=[],
                              clip_kinds={})
check("Singletrack productions add up",
      vpm.run_seconds_of(alone, False) == 40 * 60.0,
      "25 and 15 min apart: %r" % (vpm.run_seconds_of(alone, False),))

page, multi = QtWidgets.QWidget(), QtWidgets.QPushButton()
page_layout = QtWidgets.QVBoxLayout(page)
arrived = []
bridge = types.SimpleNamespace(presets=types.SimpleNamespace(
    connect=arrived.append))
state = {"account": {"hours": 20 / 60.0, "paying": True}}
built = vpm.make_auphonic_box(
    QtWidgets, state, bridge, lambda *a: None, page_layout, lambda: None,
    lambda: None, multi, vpm.Value(""), lambda: "", lambda *a: None,
    lambda: vpm.run_tracks_of(model))
credit = [w for w in page.findChildren(QtWidgets.QLabel)
          if w.wordWrap() and not w.text().startswith(T('Preset:'))]
credit = credit[-1] if credit else QtWidgets.QLabel()
# The key connected, and the account holds no preset yet.
arrived[0]([], "", KEY)
check("the window shows the credit once connected, before any preset",
      not credit.isHidden() and minutes(20) in credit.text(),
      "no preset in the account: hidden %s, text %r"
      % (credit.isHidden(), credit.text()))
arrived[0]([("Podcast_Multi", "u2", True)], "", KEY)
box = [w for w in page.findChildren(QtWidgets.QComboBox)
       if w.count() and w.itemData(0) == vpm.PRESET_NONE][0]
box.setCurrentIndex(0)
check("the window shows the credit with \"work without Auphonic\" chosen",
      not credit.isHidden() and minutes(20) in credit.text(),
      "hidden %s, text %r" % (credit.isHidden(), credit.text()))
check("and it is not red then, though the rows need more",
      RED not in credit.styleSheet(), "20 min for 25, no preset: style %r"
      % credit.styleSheet())
box.setCurrentIndex(1)
check("the window shows the credit once a preset is chosen",
      not credit.isHidden() and minutes(20) in credit.text(),
      "hidden %s, text %r" % (credit.isHidden(), credit.text()))
check("it is red when the rows need more than is left",
      RED in credit.styleSheet(), "20 min for 25: style %r"
      % credit.styleSheet())
state["account"] = {"hours": 30 / 60.0, "paying": True}
built[6]()
check("and not red when the credit carries them",
      RED not in credit.styleSheet() and not credit.isHidden(),
      "30 min for 25: style %r, hidden %s"
      % (credit.styleSheet(), credit.isHidden()))

# --------------------------------------------- 6. Before the run
print("\n6. The check before the run says the account first")

# Two recordings of 25 and 15 minutes by the stood-in measure above;
# the files themselves are three seconds, so the check stays short.
guest = os.path.join(room, "Guest.wav")
shutil.copyfile(audio, guest)
recordings = [guest, audio]


def run_args(**changed):
    """A call as the run's parser leaves it, with the key handed over."""
    values = dict(without_auphonic=False, auphonic_done=None,
                  auphonic_key=KEY, in_point=None, out_point=None,
                  out=os.path.join(room, "out"), lufs=-16.0, anyway=False,
                  dry_run=True, no_preflight=False, preflight_again=False,
                  apart=(), together=(), no_follow_ups=False)
    values.update(changed)
    return types.SimpleNamespace(**values)


def account_said(account, **changed):
    """The findings check_account gives, and the calls it made."""
    stand_in = Account(account if isinstance(account, Exception)
                       else json.dumps({"status_code": 200,
                                        "data": account}))
    vpm._curl_call = stand_in
    chains = vpm.group_recording_parts(recordings)
    try:
        found = vpm.check_account(run_args(**changed), chains, 0)
    except Exception as why:     # a fault is a finding here, not a crash
        found = [vpm.Finding("abort", "raised", "%s: %s"
                             % (type(why).__name__, why))]
    return found, stand_in.calls


FREE_ACCOUNT = dict(PAID, credits=2.0, is_paying_user=False)
found, calls = account_said(FREE_ACCOUNT)
texts = [b.text for b in found]
check("the check asks the account once, and nothing else",
      len(calls) == 1 and calls[0][-1].endswith("/api/user.json"),
      "calls: %r" % (calls,))
check("the check says a free account first",
      texts[:1] == [FREE_SAID.strip()], "said: %r" % (texts,))
check("the check says the credit against the 25 min of the rows",
      texts[1:2] == [ENOUGH.strip() % (minutes(120), minutes(25))],
      "said: %r" % (texts,))
check("a free Multitrack run of 25 min gets the border warning in the check",
      texts[-2:] == [WARN.strip() % (minutes(25), minutes(21)), WHY.strip()]
      and [b.kind for b in found][-2:] == ["warning", "good"],
      "said: %r" % ([(b.kind, b.text) for b in found],))
check("nothing the check says about the account stops the run",
      not [b for b in found if b.kind == "abort"],
      "kinds: %r" % ([b.kind for b in found],))
found, _ = account_said(dict(PAID, credits=2.0))
check("the check says a paying account as paying",
      [b.text for b in found][:1] == [PAYING.strip()],
      "said: %r" % ([b.text for b in found],))
found, _ = account_said(dict(PAID, credits=0.2))
check("the check says credit short of the rows, and that the run tries",
      [b.text for b in found][1:] == [SHORT.strip() % (minutes(12),
                                                         minutes(25)),
                                      TRIES.strip()],
      "12 min for 25: %r" % ([b.text for b in found],))
NOT_ASKED = T('Account at auphonic.com: not known -- it could not be '
              'asked. The run goes on.')
found, calls = account_said(RuntimeError("curl: (6) no network"))
check("an account that cannot be asked is one line: not known",
      [b.text for b in found] == [NOT_ASKED]
      and found[0].kind != "abort",
      "said: %r" % ([(b.kind, b.text) for b in found],))
found, calls = account_said(FREE_ACCOUNT, auphonic_key=None)
check("without a key the check says not known and asks nothing",
      [b.text for b in found] == [NOT_ASKED] and not calls,
      "said %r, calls %r" % ([b.text for b in found], calls))
found, calls = account_said(FREE_ACCOUNT, without_auphonic=True)
check("a run without auphonic.com says nothing about the account",
      not found and not calls,
      "said %r, calls %r" % ([b.text for b in found], calls))

text, calls = said_by(lambda: said_by.__setattr__(
    "returned", vpm.run_preflight(run_args(), recordings, [])),
    FREE_ACCOUNT)
marked = [one for one in text.splitlines()
          if WARN.strip() % (minutes(25), minutes(21)) in one]
check("the check before a run marks the border warning, and does not stop",
      [vpm.split_kind(one)[0] for one in marked] == ["warning"]
      and getattr(said_by, "returned", None) == 0,
      "returned %r; %r" % (getattr(said_by, "returned", None),
                            text[-600:]))

shutil.rmtree(room, ignore_errors=True)
print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
