# -*- coding: utf-8 -*-
"""A preset is found by name or id, one of the wrong kind stops the upload.

choose_preset in this process, with the account's list and the preset
check replaced where the piece looks them up, and the one road to
auphonic.com replaced by a stand-in that raises, so any call shows in a
failure line. A preset is found by its name and by its id in any case;
a Singletrack one in a Multitrack run is refused before anything goes
up; without a terminal no preset is a stop that names the way out; and
a preset the check finds unfit stops the run.
"""
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
import contextlib, io, time

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


PIECE = vpm.choose_preset.__globals__
NO_WAY = "the stand-in curl was called"


def no_way(*a, **k):
    """The stand-in for every call that would go out: it refuses."""
    raise RuntimeError(NO_WAY)


PIECE["_curl_call"] = no_way
PIECE["list_presets"] = lambda key: [("Single A", "u1", False),
                                     ("Multi B", "u2", True)]
FINDINGS = []
PIECE["check_preset"] = lambda *a, **k: list(FINDINGS)
Finding = vpm.report_findings.__globals__["Finding"]


def choose(wanted, multitrack=True):
    """choose_preset with no terminal: (what it returned, or its error)."""
    was = sys.stdin
    sys.stdin = io.StringIO("")
    try:
        with contextlib.redirect_stdout(io.StringIO()):
            return vpm.choose_preset("not-a-key", wanted, multitrack), ""
    except Exception as e:
        return None, "%s: %s" % (type(e).__name__, e)
    finally:
        sys.stdin = was


print("Found, or refused")
by_name, why_name = choose("multi b")
by_id, why_id = choose("U2")
check("a preset is found by its name and by its id, in any case",
      by_name == ("u2", "Multi B") and by_id == ("u2", "Multi B"),
      "'multi b' gave %s%s, 'U2' gave %s%s, wanted ('u2', 'Multi B')"
      % (by_name, " " + why_name if why_name else "",
         by_id, " " + why_id if why_id else ""))
got, why = choose("Single A")
want = "RuntimeError: " + vpm.T('%r is a Singletrack preset, and a '
                                'Multitrack one is needed.') % "Single A"
check("a Singletrack preset in a Multitrack run is refused before "
      "anything goes up", got is None and why == want,
      "got %s, %r against %r" % (got, why, want))

print("\nNo preset, and no terminal to ask at")
got, why = choose(None)
want = "RuntimeError: " + vpm.T('No preset given, no input possible. Choose '
                                'one of the above with --auphonic-preset '
                                'NAME.')
check("without a terminal, no preset means a stop with the way out",
      got is None and why == want, "got %s, %r against %r" % (got, why, want))

print("\nA preset that does not fit")
FINDINGS.append(Finding("abort", "Preset", "no track template"))
got, why = choose("Multi B")
want = "RuntimeError: " + vpm.T('preset does not fit the run')
check("a preset that does not fit the run stops it",
      got is None and why == want, "got %s, %r against %r" % (got, why, want))

print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
