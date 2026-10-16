# -*- coding: utf-8 -*-
"""A cut Timeline Resolve leaves without picture or sound ends the run red.

The project build, with build_cut_timeline real, against the Resolve
stand-in, for one camera cut into three shots and a stored mix. In
turn: a cut Resolve takes whole ends in 0; then no picture taken, fewer
shots taken than sent, no mix in the media pool and a mix refused --
each ends the build in 1 and is named again among the closing lines,
with the Timeline's name. Then the window: a refused mix leaves it
saying errors, with what Resolve refused above that line, and a cut
taken whole leaves it saying done. The limit: a stand-in, not Resolve.
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
import contextlib
import io
import re
import time
import types
import resolve_stand_in as stand

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


WIDE = "WideCam_C001"
CAMERA = "/tmp/%s.mov" % WIDE
MIX = "/tmp/Full-Mix.wav"
NAME = "Episode"
CUT_TIMELINE = "%s Cut" % NAME
HANDOVER = {"fps": 25.0, "start_tc": "01:00:00:00", "in_point": "01:00:00:00",
            "length_s": 60.0, "production": NAME, "speakers": [],
            "cameras": [{"camera": WIDE, "track": WIDE, "file": CAMERA,
                         "source": CAMERA, "wide": True, "offset": 0.0,
                         "duration": 60.0, "fps": 25.0}],
            "cut": [{"start": 10.0, "end": 20.0, "camera": WIDE},
                    {"start": 20.0, "end": 30.0, "camera": WIDE},
                    {"start": 30.0, "end": 40.0, "camera": WIDE}]}

# Everything around the cut Timeline is stubbed out; the layer that
# lays it -- build_cut_timeline -- and the closing lines are real.
WITHOUT = set()
vpm.apply_project_settings = lambda p, d: None
vpm.set_loudness_target = lambda p, x: None
vpm.set_remote_grades = lambda p, on=False: None
vpm.import_media = lambda mp, paths: dict(
    (p, stand.Clip(p, frames=1500)) for p in paths if p not in WITHOUT)
vpm.mix_file_from_handover = lambda d: (MIX, "stored file")
vpm.colour_clips_by_camera = lambda *a, **k: None
vpm.create_colour_groups = lambda *a, **k: None
vpm.queue_render_job = lambda *a, **k: None
vpm.lead_in_offset = lambda *a, **k: 0
CURRENT = {}
vpm.connect_to_resolve = lambda: stand.Resolve(CURRENT["pm"])


def build(without=(), **pool):
    """One build into an existing project kept as it is.

    Returns (the build's code or the exception, everything printed).
    """
    pm = stand.ProjectManager(names=[NAME])
    for k, v in pool.items():
        setattr(pm.projects[NAME].pool, k,
                set(v) if k == "refuse_media" else v)
    CURRENT["pm"] = pm
    WITHOUT.clear()
    WITHOUT.update(without)
    said = io.StringIO()
    try:
        with contextlib.redirect_stdout(said):
            code = vpm.build_resolve_project(dict(HANDOVER), "keep", log="")
    except Exception as e:
        code = e
    return code, said.getvalue()


def clean(line):
    """A printed line without the program's colour marks, for a FAIL line."""
    line = re.sub(re.escape(vpm.MARK) + ".", "", line)
    return "".join(c for c in line if c >= " ").strip()


def closing(said):
    """The lines under "this project is not complete", cleaned."""
    head = clean(vpm.T('  Caution: this project is not complete -- what '
                       'Resolve refused:'))
    rows = [clean(x) for x in said.splitlines() if clean(x)]
    return rows[rows.index(head) + 1:] if head in rows else []


def named(said, *words):
    """The closing lines naming the cut Timeline and every one of words."""
    return [x for x in closing(said)
            if '"%s"' % CUT_TIMELINE in x and all(w in x for w in words)]


print("1. A cut Resolve takes whole")
code, said = build()
check("a cut Resolve takes whole ends the build in 0",
      code == 0 and not closing(said),
      "the build ended in %r, the closing lines %r" % (code, closing(said)))

print("\n2. What Resolve refuses of the cut")
code, said = build(refuse_media=[1])
check("a cut Resolve took no picture of ends the build in 1",
      code == 1 and len(named(said, "no picture")) == 1,
      "the build ended in %r, the closing lines %r" % (code, closing(said)))
code, said = build(takes=1)
check("fewer shots taken than sent ends the build in 1",
      code == 1 and len(named(said, " 1 of 3 ")) == 1,
      "the build ended in %r, the closing lines %r" % (code, closing(said)))
code, said = build(without=[MIX])
check("a mix not in the media pool ends the build in 1",
      code == 1 and len(named(said, "Full-Mix", "media pool")) == 1,
      "the build ended in %r, the closing lines %r" % (code, closing(said)))
code, said = build(refuse_media=[2])
check("a mix Resolve refuses ends the build in 1",
      code == 1 and len(named(said, "refused the Full-Mix")) == 1,
      "the build ended in %r, the closing lines %r" % (code, closing(said)))

print("\n3. What the window says")
# The window's own run loop, with main standing in for the command
# line's switch, which returns the build's code as it is: that switch
# may not stand in a test (source_resolve_door_shut).
ERRORS = clean(vpm.T('\nFinished with errors.\n'))
DONE = clean(vpm.run_done_text(False).strip().splitlines()[0])


def window_says(**refusal):
    """Every line the window writes after one build, cleaned."""
    def main():
        code, said = build(**refusal)
        sys.stdout.write(said)
        return code if isinstance(code, int) else 1
    vpm.main = main
    written = []
    state = {"dry_run": False, "results": [], "running": True}
    with contextlib.redirect_stdout(io.StringIO()):
        vpm.window().gui_run_loop(
            ["vpm"], state, written.append, lambda *a: None,
            types.SimpleNamespace(run_step=None), lambda *a: None, [])
    return [clean(x) for x in "".join(written).splitlines() if clean(x)]


rows = window_says(refuse_media=[2])
refused_at = [i for i, x in enumerate(rows)
              if "refused the Full-Mix" in x and '"%s"' % CUT_TIMELINE in x]
check("a refused mix leaves the window saying errors, and why",
      rows[-1:] == [ERRORS] and len(refused_at) == 2,
      "the last lines %r against %r, the refusal written at %r"
      % (rows[-3:], ERRORS, refused_at))
rows = window_says()
check("a cut taken whole leaves the window saying done",
      DONE in rows[-3:] and ERRORS not in rows,
      "the last lines %r against %r" % (rows[-3:], DONE))

print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
