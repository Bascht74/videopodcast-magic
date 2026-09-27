# -*- coding: utf-8 -*-
"""What auphonic.com has left is said, and a production it cannot carry too.

auphonic.com is never spoken to: `_curl_call` is replaced by a stand-in
answering /api/user.json the way its API page shows it. Sections: the
account read, the verdict before an upload (the length needed counted in
whole minutes, rounded up, at least one), a run that says it before
anything goes up, and the line in the Auphonic box. The field names are
read off the API page, not measured against the service; the twenty
minutes a free Multitrack production may last are the pricing page's.
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
    """The lines credit_verdict gives: [(line, warning)]."""
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

# ------------------------------------------------ 2. The verdict before
print("\n2. The verdict before an upload")

HOUR = {"hours": 1.0, "paying": True}
lines = verdict(HOUR, 30 * 60, False)
check("credit that carries the production is said, not warned of",
      len(lines) == 1 and not lines[0][1],
      "1 h left for 30 min: %r" % (lines,))
lines = verdict(HOUR, 90 * 60, False)
check("credit shorter than the production is a warning",
      len(lines) == 1 and lines[0][1],
      "1 h left for 90 min: %r" % (lines,))
check("the warning names what is left and what is needed",
      bool(lines) and T('%d h %02d min') % (1, 0) in lines[0][0]
      and T('%d h %02d min') % (1, 30) in lines[0][0],
      "the line: %r" % (lines[0][0] if lines else "",))

ENOUGH = T('  Credit at auphonic.com: %s left, enough for the '
           '%s this production needs.')
lines = verdict(HOUR, 20, False)
check("a 20 s production is said to need 1 min, never 0 min",
      len(lines) == 1 and lines[0][0]
      == ENOUGH % (T('%d h %02d min') % (1, 0), T('%d min') % 1),
      "1 h left for 20 s: %r" % (lines,))
lines = verdict(HOUR, 90, False)
check("a production of 1 min 30 s is said to need 2 min, rounded up",
      len(lines) == 1 and lines[0][0]
      == ENOUGH % (T('%d h %02d min') % (1, 0), T('%d min') % 2),
      "1 h left for 90 s: %r" % (lines,))
lines = verdict({"hours": 30 / 3600.0, "paying": True}, 20, False)
check("30 s of credit does not carry a 20 s production charged as 1 min",
      len(lines) == 1 and lines[0][1],
      "30 s left for 20 s: %r" % (lines,))

FREE = {"hours": 2.0, "paying": False}
lines = verdict(FREE, 21 * 60, True)
check("a free account's Multitrack production over 20 min is warned of",
      len(lines) == 2 and lines[1][1],
      "21 min on the free plan: %r" % (lines,))
lines = verdict(FREE, 19 * 60, True)
check("a free account's Multitrack production under 20 min is not",
      not any(w for _, w in lines), "19 min on the free plan: %r" % (lines,))
lines = verdict(FREE, 21 * 60, False)
check("the twenty minutes hold for Multitrack only, not Singletrack",
      not any(w for _, w in lines), "21 min Singletrack, free: %r" % (lines,))
lines = verdict(dict(FREE, paying=True), 21 * 60, True)
check("a paying account's Multitrack production may be longer",
      not any(w for _, w in lines), "21 min Multitrack, paid: %r" % (lines,))
lines = verdict(None, 30 * 60, True)
check("an account that did not answer is said, and warns of nothing",
      len(lines) == 1 and not lines[0][1], "no answer: %r" % (lines,))

# ------------------------------------------------------- 3. In the run
print("\n3. A run says it before anything goes up")

room = tempfile.mkdtemp(prefix="vpm_credit_")
audio = os.path.join(room, "Presenter.wav")
with wave.open(audio, "wb") as w:
    w.setnchannels(1)
    w.setsampwidth(2)
    w.setframerate(48000)
    w.writeframes(b"\x00\x10" * 48000 * 3)


def run_said(account):
    """What a Singletrack run printed up to its upload, and the calls."""
    stand_in = Account(json.dumps({"status_code": 200, "data": account}))
    vpm._curl_call = stand_in
    said = io.StringIO()
    old, sys.stdout = sys.stdout, said
    try:
        vpm.run_single_production(audio, "PRESETUUID", "Podcast", KEY,
                                  os.path.join(room, "out"), 600, False)
    except Uploaded:
        pass
    except Exception as why:
        said.write("the run raised %s: %s\n" % (type(why).__name__, why))
    finally:
        sys.stdout = old
    return said.getvalue(), stand_in.calls


# Three seconds of sound are charged as a whole minute.
ONE = T('%d min') % 1
NONE_LEFT = T('%d min') % 0

# Three seconds of sound against a fiftieth of an hour, 72 s: enough.
text, calls = run_said(dict(PAID, credits=0.02))
mark = text.find("<<the upload begins here>>")
enough = text.find(ENOUGH % (ONE, ONE))
check("a run asks the account before its upload, not after",
      len(calls) == 2 and calls[0][-1].endswith("/api/user.json")
      and "-F" in calls[1],
      "calls in order: %r" % ([c[-1] if "-F" not in c else "upload"
                               for c in calls],))
check("a run says the credit before its upload",
      0 <= enough < mark, "credit line at %d, the upload at %d"
      % (enough, mark))

# Three seconds of sound against a ten-thousandth of an hour, 0.36 s.
text, _ = run_said(dict(PAID, credits=0.0001))
mark = text.find("<<the upload begins here>>")
short = text.find(T('  Credit at auphonic.com: %s left, and this '
                    'production needs %s -- not enough.')
                  % (NONE_LEFT, ONE))
check("a run whose credit is short says so before its upload",
      0 <= short < mark, "the short line at %d, the upload at %d"
      % (short, mark))

# ------------------------------------------------------- 4. The box
print("\n4. The line in the Auphonic box")

from PySide6 import QtWidgets
app = QtWidgets.QApplication.instance() or QtWidgets.QApplication([])
holder = QtWidgets.QWidget()
layout = QtWidgets.QVBoxLayout(holder)
show = vpm.credit_row(layout)
line = holder.findChildren(QtWidgets.QLabel)[-1]
WARN = vpm.COLOURS["warning"]

show(None, False)
check("the box shows no credit line before the account answered",
      line.isHidden(), "hidden %s, text %r" % (line.isHidden(), line.text()))
show({"hours": 2.5, "paying": True}, False)
check("the box shows what the account has left once it answered",
      not line.isHidden() and T('%d h %02d min') % (2, 30) in line.text(),
      "hidden %s, text %r" % (line.isHidden(), line.text()))
check("credit that is left is not in the warning colour",
      WARN not in line.styleSheet(), "style %r" % line.styleSheet())
show({"hours": 0.0, "paying": True}, False)
check("the box warns when no credit is left",
      WARN in line.styleSheet(), "style %r" % line.styleSheet())
show({"hours": 2.0, "paying": False}, True)
check("the box warns of the twenty minutes on a free plan for Multitrack",
      WARN in line.styleSheet()
      and T('%d min') % 20 in line.text(),
      "style %r, text %r" % (line.styleSheet(), line.text()))
show({"hours": 2.0, "paying": False}, False)
check("a free plan in Singletrack mode is said but not warned of",
      WARN not in line.styleSheet() and not line.isHidden(),
      "style %r, hidden %s" % (line.styleSheet(), line.isHidden()))

shutil.rmtree(room, ignore_errors=True)
print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
