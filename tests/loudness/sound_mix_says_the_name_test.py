# -*- coding: utf-8 -*-
"""While mixing, each sum is named by speaker, mix or label -- never by file.

The line shown while a track is mixed took the target's file name and
replaced "full" and the two prefixes wherever they stood, so a speaker
called Carefully was announced as CareFull-Mixy.

The sections: the file names the run gives its targets, taken out of
the run rather than written down here; the overall mix under its name;
three speakers whose names only look like the mix or its prefixes;
whether the mixing call asks this rather than a replace of its own; and
every mixing call in the program, read out of its source, announced by
a name or a label of its own -- the dry run's sum said "levels".
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
import ast
import glob
import inspect
import re
import time
import the_program

began = time.time()
vpm = the_program.load()
done = 0
bad = []


def check(name, ok, extra=""):
    global done
    done += 1
    print("  %-58s %s %s" % (name, "ok" if ok else "FAIL", extra))
    if not ok:
        bad.append("%s [%s]" % (name, extra or "no numbers"))


print("\n1. The names the run gives its targets")
# Out of timebase, not spelt out here: a test that writes the file name
# down stays green the day the run calls it something else, and the mix
# is then announced as a file.
HERE = os.path.dirname(os.path.abspath(the_program.SCRIPT))
RUN = open(os.path.join(HERE, "timebase", "__init__.py"),
           encoding="utf-8").read()
# Each pattern stays inside its own call: .*? once ran on past the
# speakers' call into the camera mix below it, and took that call's mix_
# for the speakers' prefix.
_mix = re.search(r'full_mix = mix_tracks\([^)]*?"(mix_\w+\.wav)"', RUN)
MIX_FILE = _mix.group(1) if _mix else ""
check("the run still names the file of its overall mix", bool(MIX_FILE),
      MIX_FILE or "no file name after full_mix = mix_tracks( in timebase")
_one = re.search(r'single\[track\["name"\]\] = mix_tracks\([^)]*?"(\w+_)%s\.wav"',
                 RUN)
SPEAKER = _one.group(1) if _one else ""
check("the run still names its speakers' files", bool(SPEAKER),
      SPEAKER or "no speaker target built from the track's name in timebase")

print("\n2. The overall mix")
said = vpm.mixing_label(os.path.join("work", MIX_FILE))
check("the overall mix is announced by the mix's own name",
      said == vpm.MIX_TRACK_NAME,
      "%r for %r, wanted %r" % (said, MIX_FILE, vpm.MIX_TRACK_NAME))

print("\n3. Speakers whose names only look like it")
said = vpm.mixing_label(os.path.join("work", SPEAKER + "Carefully.wav"))
check("a speaker whose name holds full keeps that name",
      said == "Carefully", "%r, wanted 'Carefully'" % said)
said = vpm.mixing_label(os.path.join("work", SPEAKER + "Remix_Anna.wav"))
check("a speaker whose name holds a prefix keeps all of it",
      said == "Remix_Anna", "%r, wanted 'Remix_Anna'" % said)
said = vpm.mixing_label(os.path.join("work", SPEAKER + "full.wav"))
check("a speaker called full is not announced as the mix",
      said == "full", "%r, wanted 'full'" % said)

print("\n4. The mixing call asks this")
# A right answer nobody asks repairs nothing: the line is made inside
# mix_tracks, and a replace of its own there would bring the fault back.
_body = inspect.getsource(vpm.mix_tracks)
check("the progress line of a mix is named by mixing_label",
      "mixing_label(target)" in _body,
      "mix_tracks %s mixing_label(target)"
      % ("calls" if "mixing_label(target)" in _body else "does not call"))

print("\n5. Every mixing call in the program")
# Read, not run: a call nobody reaches in a test still prints its line
# in somebody's run. A target the label function turns into the name
# put into it is announced by that name; any other needs a label, or
# its file's stem stands in the line untranslated.
NAME = "Guest"
calls, stems = 0, []
for module in sorted(glob.glob(os.path.join(HERE, "*", "__init__.py"))
                     + [os.path.join(HERE, "__init__.py")]):
    tree = ast.parse(open(module, encoding="utf-8").read())
    for node in ast.walk(tree):
        if not (isinstance(node, ast.Call) and getattr(
                node.func, "id", getattr(node.func, "attr", "")) ==
                "mix_tracks"):
            continue
        calls += 1
        if any(k.arg == "label" for k in node.keywords):
            continue
        files = [c.value for c in ast.walk(node.args[1])
                 if isinstance(c, ast.Constant) and isinstance(c.value, str)
                 and c.value.endswith(".wav")] if len(node.args) > 1 else []
        file = (files[0] % NAME if "%s" in files[0] else files[0]) \
            if files else ""
        said = vpm.mixing_label(os.path.join("work", file))
        if said not in (NAME, vpm.MIX_TRACK_NAME):
            stems.append("%s:%d %r said as %r" % (
                os.path.basename(os.path.dirname(module)), node.lineno,
                file, said))
check("no mixing call in the program is announced by its file",
      calls > 0 and not stems,
      "%d calls read; %s" % (calls, "; ".join(stems) or "none by its file"))

# A label handed in has to reach the line: taken past, the call above
# would pass and the line say the file after all. ffmpeg and the reads
# of the files are stood in for, in memory, and put back.
shown = []
LOUD = vpm.loudness
kept = (LOUD.kept_channels, LOUD.sample_count, LOUD.bext_time_reference,
        LOUD.PROGRAM.run_ffmpeg_with_progress)
LOUD.kept_channels = lambda path: 1
LOUD.sample_count = lambda path: 48000
LOUD.bext_time_reference = lambda path: None
LOUD.PROGRAM.run_ffmpeg_with_progress = lambda cmd, s, text: shown.append(text)
try:
    vpm.mix_tracks(["a.wav", "b.wav"], os.path.join("work", "levels.wav"),
                   label="a label of its own")
finally:
    (LOUD.kept_channels, LOUD.sample_count, LOUD.bext_time_reference,
     LOUD.PROGRAM.run_ffmpeg_with_progress) = kept
check("a sum handed a label is announced by that label",
      shown == ["a label of its own"],
      "the line said %r, wanted 'a label of its own'" % shown)

print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
