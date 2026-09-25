# -*- coding: utf-8 -*-
"""Without auphonic.com the speaker tracks are brought to one level first.

One common gain keeps whatever balance came in, and without auphonic.com
no leveler ever set one: two voices recorded six decibels apart stayed
six apart. Three generated tracks -- two voices six decibels apart and
one with nothing on it -- go through the matching on its own, then
through the whole path without auphonic.com with the mixing stood in
for. The material as it starts; the matching: the voices land within a
decibel, the empty track stays, the log names every move; the path
hands matched tracks on; and the Auphonic chain never calls it, which
is asked of the source, since that chain cannot run here.
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
import ast, contextlib, io, subprocess, sys, tempfile, time, types
vpm = the_program.load()
vpm.set_language("en")
WORK = tempfile.mkdtemp(prefix="matched_")
began = time.time()
done = 0
bad = []


def check(name, ok, extra=""):
    global done
    done += 1
    print("  %-58s %s %s" % (name, "ok" if ok else "FAIL", extra))
    if not ok:
        bad.append("%s [%s]" % (name, extra or "no numbers"))


def track(name, hz, db):
    path = os.path.join(WORK, name)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "lavfi",
                    "-i", "sine=frequency=%d:duration=30" % hz,
                    "-af", "volume=%ddB" % db, "-ac", "1", "-ar", "48000",
                    "-c:a", "pcm_s24le", path], check=True)
    return path


def lufs(path):
    return vpm.measure_loudness(path)[0]


def said(v):
    return "not measurable" if v is None else "%.1f LUFS" % v


def gap_between(a, b):
    return None if a is None or b is None else abs(a - b)


loud = track("loud.wav", 220, -20)
quiet = track("quiet.wav", 330, -26)
empty = track("empty.wav", 440, -60)


def fresh():
    """The three tracks as the path without auphonic.com receives them."""
    return [{"name": "Presenter", "axis": loud, "ready": loud},
            {"name": "Guest", "axis": quiet, "ready": quiet},
            {"name": "CoPresenter", "axis": empty, "ready": empty}]


print("\n1. The material as it starts")
# The claims below rest on these two, so they are asked first: a red
# line further down then names the program and not the material.
start = dict((n, lufs(p)) for n, p in (("loud", loud), ("quiet", quiet),
                                        ("empty", empty)))
apart = gap_between(start["loud"], start["quiet"])
check("the two voices start about six decibels apart",
      apart is not None and 5.0 <= apart <= 7.0,
      "%s against %s" % (said(start["loud"]), said(start["quiet"])))
check("the third track reads as nothing, under the floor",
      start["empty"] is not None
      and start["empty"] <= vpm.SPEAKER_FLOOR_LUFS,
      "%s against a floor of %.1f LUFS"
      % (said(start["empty"]), vpm.SPEAKER_FLOOR_LUFS))

print("\n2. The matching on its own")
tracks = fresh()
log = io.StringIO()
with contextlib.redirect_stdout(log):
    moves = vpm.match_speakers(tracks, WORK)
log = log.getvalue()
after = dict((t["name"], lufs(t["ready"])) for t in tracks)
gap = gap_between(after["Presenter"], after["Guest"])
check("two voices six decibels apart come out under one apart",
      gap is not None and gap < 1.0,
      "%s against %s" % (said(after["Presenter"]), said(after["Guest"])))
check("a track with nothing on it is left as it is",
      tracks[2]["ready"] == empty and moves[2][2] == 0.0,
      "ready %s, gain %+.1f dB"
      % (os.path.basename(tracks[2]["ready"]), moves[2][2]))
# The log has to carry the figure the program itself handed back, on
# the line that names the voice.
named = {}
for name, _have, gain in moves[:2]:
    figure = vpm.number_text(gain, 1, plus=True)
    named[name] = any(name in line and figure in line
                      for line in log.splitlines())
check("the log says what each voice was moved by", all(named.values()),
      ", ".join("%s %s" % (n, "named" if ok else "missing")
                for n, ok in named.items()))

print("\n3. The path without auphonic.com hands matched tracks on")
received = {}


def stand_in(args, tracks, cameras, videos, tmpdir, gain, position, t0,
             ref_clip, t1, curve, segment_list=None):
    """In place of the mixing: keeps what it was handed, writes nothing."""
    received["tracks"] = list(tracks)
    return 0


vpm.distribute_tracks_to_cameras = stand_in
args = types.SimpleNamespace(dry_run=False, out=WORK, lufs=-16.0,
                             project_type="sync", production="Test")
tracks = fresh()
with contextlib.redirect_stdout(io.StringIO()):
    rc = vpm.finish_without_auphonic(args, tracks, [], [], WORK, {},
                                     0.0, 30.0, None)
handed = received.get("tracks") or []
check("the mixing is reached with the three tracks",
      rc == 0 and len(handed) == 3, "rc %s, %d track(s)" % (rc, len(handed)))
levels = dict((t["name"], lufs(t["ready"])) for t in handed)
gap = gap_between(levels.get("Presenter"), levels.get("Guest"))
check("the path hands the two voices on within a decibel",
      gap is not None and gap < 1.0,
      "%s against %s" % (said(levels.get("Presenter")),
                         said(levels.get("Guest"))))

print("\n4. The Auphonic chain never calls it")
# Asked of the source: that chain uploads, and cannot run here. Every
# call of the matching, by the piece and the function it stands in.
callers = {}
for where, body in the_program.pieces():
    for node in ast.parse(body, where).body:
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        for inner in ast.walk(node):
            if not isinstance(inner, ast.Call):
                continue
            func = inner.func
            called = (func.id if isinstance(func, ast.Name)
                      else func.attr if isinstance(func, ast.Attribute)
                      else "")
            if called == "match_speakers":
                callers.setdefault(where, []).append(node.name)
elsewhere = sorted((where, name) for where, names in callers.items()
                   for name in names if not where.startswith("cut/"))
check("no piece but the cut calls the matching, the chain included",
      not elsewhere, "callers outside cut/: %s" % (elsewhere or "none"))
check("in the cut it is the path without auphonic.com, once",
      callers.get("cut/__init__.py") == ["finish_without_auphonic"],
      "callers in cut/: %s" % (callers.get("cut/__init__.py") or "none"))

print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
