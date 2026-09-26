# -*- coding: utf-8 -*-
"""A camera's clock drift goes out by the recordings' rule, and one bound.

camera_drift is asked with made-up measurements, since a real camera
lands on a clear drift only by chance. In order: what is taken out --
a short camera, a drift of a few milliseconds over the whole file --
then what stays in, each with its reason on the line: a drift too
large to be a clock, one inside its own uncertainty, one --no-drift
keeps; last, that the camera path asks camera_drift and nothing else.
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
import ast, re, time, types
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


def asked(ppm, error, seconds, fps=25.0, no_drift=False):
    """camera_drift over a drift of *ppm* measured to +/- *error*."""
    b = 1.0 + ppm * 1e-6
    st = {"ppm": ppm, "ppm_error": error, "points": 40, "candidates": 40}
    return vpm.camera_drift(types.SimpleNamespace(no_drift=no_drift), b, st,
                            {"duration": seconds, "fps": fps})


def pattern(text):
    """A T() text as a regular expression, each %s a group of its own."""
    parts = re.split(r"%s", text)
    return re.compile(".*".join(re.escape(p) for p in parts) + "$")


RUNNING = vpm.T('  Drift over the running time: %s s = %s frames  -->  %s')
TAKEN = vpm.T('is actively taken out')
TOO_LARGE = pattern(RUNNING % ("%s", "%s", vpm.T(
    'is left in: %s ppm or more is rather a measuring error')))
UNCLEAR = pattern(RUNNING % ("%s", "%s", vpm.T(
    'is left in: not %s times its uncertainty')))
PLAIN = RUNNING.split("%s")[-2] + vpm.T('is left in')

#-------------------------------------------------------- 1. Taken out

print("1. A clear drift is taken out, however short or small")
# 400 ppm over 90 s is 36 ms, past both old floors: only the length
# stood in its way.
drift, line = asked(400.0, 5.0, 90.0)
check("a camera under 120 s with a clear drift has it taken out",
      drift and line.endswith(TAKEN), "90 s, 400 +/- 5 ppm: %r" % line)
# 10 ppm over 600 s is 6 ms: under 10 ms and under half a frame.
drift, line = asked(10.0, 1.0, 600.0)
check("a clear drift of 6 ms over the whole file is taken out",
      drift and line.endswith(TAKEN), "600 s, 10 +/- 1 ppm: %r" % line)

#----------------------------------------------------------- 2. Left in

print("\n2. What stays in says why")
drift, line = asked(600.0, 5.0, 3600.0)
check("a clear drift of 600 ppm is left in, as a measuring error",
      not drift and bool(TOO_LARGE.match(line)),
      "3600 s, 600 +/- 5 ppm: drift %r, %r" % (drift, line))
drift, line = asked(50.0, 20.0, 3600.0)
check("a drift inside three times its uncertainty is left in",
      not drift and bool(UNCLEAR.match(line)),
      "3600 s, 50 +/- 20 ppm: drift %r, %r" % (drift, line))
drift, line = asked(400.0, 5.0, 90.0, no_drift=True)
check("--no-drift leaves a clear drift in",
      not drift and line.endswith(PLAIN),
      "90 s, 400 +/- 5 ppm, --no-drift: drift %r, %r" % (drift, line))

#------------------------------------------------ 3. The one place asked

print("\n3. The camera path asks camera_drift and nothing else")
# Every assignment to drift inside distribute_tracks_to_cameras, as the
# name of the function its value comes from.
sources = []
for where, body in the_program.pieces():
    for node in ast.walk(ast.parse(body, where)):
        if not (isinstance(node, ast.FunctionDef)
                and node.name == "distribute_tracks_to_cameras"):
            continue
        for st in ast.walk(node):
            if not isinstance(st, ast.Assign):
                continue
            for target in st.targets:
                names = (target.elts if isinstance(target, ast.Tuple)
                         else [target])
                if any(isinstance(n, ast.Name) and n.id == "drift"
                       for n in names):
                    call = st.value
                    sources.append(call.func.id if isinstance(call, ast.Call)
                                   and isinstance(call.func, ast.Name)
                                   else ast.dump(call)[:80])
check("a camera's drift is settled by camera_drift alone",
      sources == ["camera_drift"],
      "drift is assigned from %s" % sources)

print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
