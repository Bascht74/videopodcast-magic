# -*- coding: utf-8 -*-
"""A preset not named is picked by the number typed, or the run stops.

choose_preset in this process at a terminal that is stood in for: what
is typed is read from a list, the account's presets and the preset
check are replaced where the piece looks them up, and the one road to
auphonic.com raises, so any call shows in a failure line. Sections: a
number picks a preset of the run's kind; a number out of range is asked
again; nothing typed cancels; a name the account does not know is said
and then asked for; and an account with no preset of the run's kind, or
none at all, stops the run naming what there is.
"""
PLATFORM_BOUND = False
import os
import sys
# tests/, where the helpers and state/ lie; this file may stand in a
# folder under it, or in one under that.
HERE = os.path.dirname(os.path.abspath(__file__))
while not os.path.isfile(os.path.join(HERE, "the_program.py")) \
        and os.path.dirname(HERE) != HERE:
    HERE = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import contextlib
import io
import time
import the_program

began = time.time()
vpm = the_program.load()
vpm.set_language("en")

done = 0
bad = []


def check(name, ok, extra=""):
    global done
    done += 1
    print("  %-62s %s %s" % (name, "ok" if ok else "FAIL", extra))
    if not ok:
        bad.append("%s [%s]" % (name, extra or "no numbers"))


PIECE = vpm.choose_preset.__globals__


def no_way(*a, **k):
    """The stand-in for every call that would go out: it refuses."""
    raise RuntimeError("the stand-in curl was called")


PIECE["_curl_call"] = no_way
PIECE["check_preset"] = lambda *a, **k: []
ACCOUNT = [("Multi A", "u1", True), ("Single C", "u3", False),
           ("Multi B", "u2", True)]


class Terminal(io.StringIO):
    """A terminal somebody types *lines* into."""

    def isatty(self):
        return True


def choose(wanted, typed, account=ACCOUNT, multitrack=True):
    """choose_preset at a terminal: (returned, error, everything said)."""
    PIECE["list_presets"] = lambda key: list(account)
    was = sys.stdin
    sys.stdin = Terminal("".join(line + "\n" for line in typed))
    said = io.StringIO()
    try:
        with contextlib.redirect_stdout(said):
            got, error = vpm.choose_preset("not-a-key", wanted,
                                           multitrack), ""
    except Exception as why:     # a stop is one of the judgements below
        got, error = None, "%s: %s" % (type(why).__name__, why)
    finally:
        sys.stdin = was
    return got, error, said.getvalue()


print("1. Picked by number")
got, error, said = choose(None, ["2"])
check("the number typed picks that preset of the run's kind",
      got == ("u2", "Multi B"),
      "typed 2, got %r, wanted ('u2', 'Multi B'); %s" % (got, error or "-"))
got, error, said = choose(None, ["3", "1"])
again = vpm.T('  Please give a number between 1 and %d.') % 2
check("a number past the list is asked again, naming the two there are",
      got == ("u1", "Multi A") and again in said,
      "typed 3 then 1, got %r; %r said: %s; %s"
      % (got, again.strip(), again in said, error or "-"))

print("\n2. Nothing typed")
got, error, said = choose(None, [""])
check("nothing typed cancels the run",
      got is None and error == "RuntimeError: " + vpm.T('cancelled'),
      "got %r, raised %r" % (got, error or "nothing"))

print("\n3. A name the account does not know")
got, error, said = choose("Nope", ["1"])
unknown = vpm.T('No preset is called %r.') % "Nope"
check("an unknown name is said, and then a number is asked for",
      unknown in said and got == ("u1", "Multi A"),
      "%r said: %s; got %r; %s"
      % (unknown, unknown in said, got, error or "-"))

print("\n4. No preset of the run's kind")
got, error, said = choose("Single C", [],
                          account=[("Single C", "u3", False)])
want = "RuntimeError: " + vpm.T('No Multitrack preset in the account. '
                                'Only these: %s') % "Single C"
check("no preset of the run's kind stops the run, naming the rest",
      got is None and error == want,
      "got %r, raised %r, wanted %r" % (got, error or "nothing", want))
got, error, said = choose(None, [], account=[])
want = "RuntimeError: " + vpm.T('No presets stored in the account. One can '
                                'be created in the web interface.')
check("no preset at all stops the run, saying where to make one",
      got is None and error == want,
      "got %r, raised %r, wanted %r" % (got, error or "nothing", want))

print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
