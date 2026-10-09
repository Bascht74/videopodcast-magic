# -*- coding: utf-8 -*-
"""A run whose auphonic.com step fails or brings a track back empty ends.

send_to_auphonic in this process, with the key, the preset, the
Multitrack production and the return check replaced where the piece
looks them up, so nothing leaves the machine. Sections: a production
that fails ends the run with 1 and says why; a track that came back
without a file ends it with 1 and names that track; and a dry run goes
on without holding anything against the window.
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
import types
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


WHY = "the stand-in production failed"
verified = []
vpm.api_key_from_anywhere = lambda args: "FAKEKEY-0000"
vpm.preset_for_run = lambda args, key, multitrack: ("PRESETUUID", "Podcast")
vpm.verify_returned_tracks = (lambda tracks, window, tmpdir:
                              verified.append(window) or True)


def send(production, dry_run=False):
    """send_to_auphonic for two tracks: (what it returned, what it said)."""
    del verified[:]
    vpm.run_multitrack_production = production
    args = types.SimpleNamespace(auphonic_wait=60, dry_run=dry_run,
                                 auphonic_resume=None)
    tracks = [{"name": "Guest", "axis": "/tmp/Guest.wav"},
              {"name": "Presenter", "axis": "/tmp/Presenter.wav"}]
    said = io.StringIO()
    with contextlib.redirect_stdout(said):
        got = vpm.send_to_auphonic(args, tracks, "/tmp", "/tmp", 10.0,
                                   "Episode 7", together=True)
    return got, said.getvalue()


def failing(*a, **k):
    raise RuntimeError(WHY)


print("1. The production fails")
got, said = send(failing)
check("a production that fails ends the run with 1",
      got == 1, "returned %r, wanted 1" % (got,))
failed = vpm.T('Processing failed: %s') % WHY
check("and says why it failed",
      failed in said, "%r said: %s" % (failed, failed in said))

print("\n2. A track comes back without a file")
got, said = send(lambda *a, **k: {"Guest": "/tmp/Guest_back.wav"})
check("a track that came back empty ends the run with 1",
      got == 1 and not verified,
      "returned %r, wanted 1; the return check ran %d times"
      % (got, len(verified)))
empty = vpm.T('\nEnded without a result: %s') % "Presenter"
check("and names the track that came back empty",
      empty in said, "%r said: %s" % (empty.strip(), empty in said))

print("\n3. A dry run")
got, said = send(lambda *a, **k: {}, dry_run=True)
check("a dry run goes on without a return check",
      got is None and not verified,
      "returned %r, wanted None; the return check ran %d times"
      % (got, len(verified)))

print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
