# -*- coding: utf-8 -*-
"""A run main() stops returns 1, its last line naming what failed and why.

Each case is a bare command line in a process of its own: presets that
cannot be fetched (curl stood in for, fenced behind a proxy to nowhere),
a lone camera with no sound, a file of no known kind alone, a path that
is not there, two cameras with no recording and no --multitrack, the
last also naming the unknown file beside it as skipped, the two
Resolve switches in a child cut off from Resolve, which checks that
before main() and stops red, main() uncalled, where it is not, no
ffmpeg with the repair stood in for and refused, --multitrack over a
single recording, and the one-shot jobs: --update with the look
switched off, --hdr-check over a file that is not HDR. What they
return when they did their work is run_one_shots_return_0's.
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
SCRIPT = the_program.SCRIPT
import json
import re
import subprocess
import tempfile
import time

vpm = the_program.load()
vpm.set_language("en")

began = time.time()
done = 0
bad = []


def check(name, ok, extra=""):
    global done
    done += 1
    print("  %-58s %s %s" % (name, "ok" if ok else "FAIL", extra))
    if not ok:
        bad.append("%s [%s]" % (name, extra or "no numbers"))


# Each start here stops within a second, before any real work; this
# bound is only there so that one that never ends is named in its own
# line, well before run.sh ends the whole test.
ASK = 120.0


def run(argv, fence=None):
    """The program's way in, in its own process: (code, last line, all).

    The code is None if it did not end within ASK, and the last line
    then says so. `fence` replaces the variables it names in either case,
    and one set to None is taken away.
    """
    fence = fence or {}
    env = {k: v for k, v in os.environ.items() if k.lower() not in fence}
    env.update((k, v) for k, v in fence.items() if v is not None)
    env["QT_QPA_PLATFORM"] = "offscreen"
    try:
        kid = subprocess.run(argv, stdout=subprocess.PIPE,
                             stderr=subprocess.STDOUT, timeout=ASK, env=env)
    except subprocess.TimeoutExpired:
        return None, "no end within %.0f s" % ASK, ""
    text = kid.stdout.decode("utf-8", "replace")
    # Colour marks and a progress bar's carriage returns are not words.
    text = re.sub(r"\x1b\[[0-9;]*m", "", text).replace("\r", "\n")
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    return kid.returncode, (lines[-1] if lines else ""), "\n".join(lines)


print("1. The presets cannot be fetched")
HOME = tempfile.mkdtemp(prefix="vpm_stopwhy_")
# A reason no curl prints, so that a real curl answering in its place
# cannot pass for the stand-in; each call leaves a line in ASKED.
REASON = "no way out -- the stand-in answers in curl's place"
ASKED = os.path.join(HOME, "asked")
# Bent where list_presets looks the name up, not on the program's face.
CHILD = "\n".join([
    "import sys",
    "sys.path.insert(0, %r)" % HERE,
    "import the_program",
    "vpm = the_program.load()",
    "def cannot_get_through(*a, **k):",
    "    with open(%r, 'a') as f:" % ASKED,
    "        f.write('asked\\n')",
    "    raise RuntimeError(%r)" % REASON,
    "vpm.list_presets.__globals__['_curl_call'] = cannot_get_through",
    "sys.argv = ['videopodcast-magic'] + sys.argv[1:]",
    "sys.exit(vpm.main())"])
# The fence: a curl started past the stand-in reaches a proxy on a
# port nothing listens on, so the placeholder key never gets out.
NOWHERE = "http://127.0.0.1:9"
FENCE = {"https_proxy": NOWHERE, "http_proxy": NOWHERE,
         "all_proxy": NOWHERE, "no_proxy": None}
code, last, _said = run([sys.executable, "-c", CHILD,
                         "--auphonic-api-key", "not-a-real-key"], FENCE)
try:
    with open(ASKED, encoding="utf-8") as f:
        asked = len(f.read().splitlines())
except OSError:
    asked = 0
WANT = vpm.T('Presets could not be loaded: %s') % REASON
check("the preset list asks the stand-in, never the network", asked >= 1,
      "the stand-in was asked %d times against at least 1" % asked)
check("a preset list that cannot be fetched returns 1", code == 1,
      "returned %r against 1" % code)
check("and its last line says the presets failed, and why", last == WANT,
      "last line %r against %r" % (last, WANT))

print("\n2. A lone camera with no sound on it")
CAMERA = os.path.join(HOME, "Mute_C001.mp4")
made = subprocess.run(["ffmpeg", "-v", "error", "-f", "lavfi", "-i",
                       "testsrc=size=160x90:rate=25:duration=2",
                       "-c:v", "libx264", "-pix_fmt", "yuv420p", CAMERA,
                       "-y"], stdout=subprocess.PIPE,
                      stderr=subprocess.STDOUT, timeout=ASK)
# A precondition of the material, not a judgement about the program.
assert made.returncode == 0 and os.path.exists(CAMERA), made.stdout
code, last, _said = run([sys.executable, SCRIPT, "--without-auphonic",
                         "--out", os.path.join(HOME, "out"), CAMERA])
WANT = vpm.T('Camera audio not usable: %s') % (
    vpm.T('%s has no audio track.') % os.path.basename(CAMERA))
check("a lone camera without sound returns 1", code == 1,
      "returned %r against 1" % code)
check("and its last line names the file and says it has no sound",
      last == WANT, "last line %r against %r" % (last, WANT))

print("\n3. Files a run can do nothing with")
NOTES = os.path.join(HOME, "notes.txt")
with open(NOTES, "w") as f:
    f.write("not a recording\n")
CAMS = [os.path.join(HOME, "CamA_C001.mov"), os.path.join(HOME,
                                                         "CamB_C001.mov")]
build = ["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i",
         "testsrc=size=160x90:rate=25:duration=2", "-f", "lavfi", "-i",
         "sine=frequency=440:duration=2"]
for cam in CAMS:
    build += ["-map", "0:v", "-map", "1:a", "-c:v", "libx264", "-pix_fmt",
              "yuv420p", "-c:a", "pcm_s16le", cam]
made = subprocess.run(build, stdout=subprocess.PIPE,
                      stderr=subprocess.STDOUT, timeout=ASK)
# A precondition of the material, not a judgement about the program.
assert made.returncode == 0 and all(map(os.path.exists, CAMS)), made.stdout
code, last, _said = run([sys.executable, SCRIPT, "--without-auphonic",
                         "--out", os.path.join(HOME, "out3"), NOTES])
WANT = vpm.T('No audio file given.')
check("an unknown file alone returns 1 and says no audio came",
      code == 1 and last == WANT,
      "returned %r against 1, last line %r against %r" % (code, last, WANT))
GONE = os.path.join(HOME, "Gone_C001.wav")
code, last, _said = run([sys.executable, SCRIPT, "--without-auphonic",
                         "--out", os.path.join(HOME, "out3"), GONE])
WANT = vpm.T('Not found: %s') % GONE
check("a missing file returns 1 and names it",
      code == 1 and last == WANT,
      "returned %r against 1, last line %r against %r" % (code, last, WANT))
code, last, said = run([sys.executable, SCRIPT, "--without-auphonic",
                        "--out", os.path.join(HOME, "out3"), NOTES] + CAMS)
WANT = vpm.T('Several cameras but no audio file. Each camera would have its '
             'own audio --\nthat is what --multitrack is for. Otherwise '
             'one camera after another.').splitlines()[-1].strip()
check("two cameras without a recording and without Multitrack return 1 "
      "and say what --multitrack is for", code == 1 and last == WANT,
      "returned %r against 1, last line %r against %r" % (code, last, WANT))
SKIPPED = vpm.T('Unknown extension, skipped: %s') % "notes.txt"
check("an unknown file beside real ones is named as skipped",
      SKIPPED in said.splitlines(),
      "%r %s among %d lines" % (SKIPPED, "said" if SKIPPED in
                                said.splitlines() else "not said",
                                len(said.splitlines())))

print("\n4. Resolve out of reach, and main() saying so")
# The owner's Resolve may be running on this machine. So the child
# points the scripting interface at a folder that is not there, drops
# any path holding the module, nails connect_to_resolve, and checks all
# three before main() is called; where one does not hold it stops there.
RESOLVE_REASON = "no Resolve here -- the stand-in answers in its place"
HANDOVER = os.path.join(HOME, "Door_resolve.json")
with open(HANDOVER, "w", encoding="utf-8") as f:
    json.dump({"format": vpm.FILE_FORMAT, "fps": 25, "production": "Door",
               "cameras": [{"file": CAMS[0], "name": "CamA"}]}, f)
SHUT = "Resolve's scripting module is out of reach"
# One string, not lines joined: source_resolve_door_shut reads it as a
# child of its own and lets its switches through for the nail and the
# bolt standing above them, and for nothing else.
RESOLVE_CHILD = """import importlib.util, os, sys
os.environ["RESOLVE_SCRIPT_API"] = %r
os.environ["RESOLVE_SCRIPT_LIB"] = os.path.join(%r, "fusionscript.so")
MODULES = ("DaVinciResolveScript", "fusionscript")
sys.path[:] = [p for p in sys.path if not any(
    os.path.exists(os.path.join(p, m + e)) for m in MODULES
    for e in (".py", ".so", ".dll"))]
sys.path.insert(0, %r)
import the_program
vpm = the_program.load()
def refuse(*a, **k):
    raise RuntimeError(%r)
vpm.connect_to_resolve = refuse
near = [m for m in MODULES if importlib.util.find_spec(m) is not None]
there = [p for p in vpm.resolve_module_paths() if os.path.exists(p)]
loose = [f.__name__ for f in (vpm.build_resolve_project,
                              vpm.print_audio_track_mapping)
         if f.__globals__.get("connect_to_resolve") is not refuse]
if near or there or loose:
    print("Resolve within reach, main() not called:", near, there, loose)
    sys.exit(3)
print(%r)
sys.argv = ["videopodcast-magic"] + {
    "json": ["--resolve-json", %r],
    "tracks": ["--resolve-audio-tracks"]}[sys.argv[1]]
sys.exit(vpm.main())
""" % (os.path.join(HOME, "nowhere"), os.path.join(HOME, "nowhere"), HERE,
       RESOLVE_REASON, SHUT, HANDOVER)
code, last, said = run([sys.executable, "-c", RESOLVE_CHILD, "json"])
bolted = SHUT in said.splitlines()
check("the child finds Resolve out of reach before main() is called",
      bolted, "%r %s, returned %r, last line %r"
      % (SHUT, "said" if bolted else "not said", code, last))
if bolted:
    WANT = vpm.T('Resolve part stopped: %s') % RESOLVE_REASON
    check("a Resolve build that cannot connect returns 1", code == 1,
          "returned %r against 1" % code)
    check("and its last line says the Resolve part stopped, and why",
          last == WANT, "last line %r against %r" % (last, WANT))
    code, last, said = run([sys.executable, "-c", RESOLVE_CHILD, "tracks"])
    WANT = vpm.T('Stopped: %s') % RESOLVE_REASON
    check("a look at Resolve's tracks that cannot connect returns 1",
          code == 1 and SHUT in said.splitlines(),
          "returned %r against 1, %r %s" % (code, SHUT, "said" if SHUT in
                                            said.splitlines() else
                                            "not said"))
    check("and its last line says it stopped, and why", last == WANT,
          "last line %r against %r" % (last, WANT))
else:
    print("   main() was not called: the checks on the two Resolve "
          "switches wait for a child that cannot reach Resolve")

print("\n5. No ffmpeg, and the repair not made")
# Both bent where main() and tools_repaired look them up: the search
# answers missing, and the repair leaves a line in MENDED and fails,
# so no installer and no download is ever reached.
MENDED = os.path.join(HOME, "mended")
TOOLLESS = "\n".join([
    "import sys",
    "sys.path.insert(0, %r)" % HERE,
    "import the_program",
    "vpm = the_program.load()",
    "vpm.find_required_tools = lambda: ('missing', %r)"
    % vpm.T('ffmpeg and ffprobe are missing.'),
    "def not_mended(*a, **k):",
    "    with open(%r, 'a') as f:" % MENDED,
    "        f.write('asked\\n')",
    "    return False",
    "vpm.tools_repaired.__globals__['install_ffmpeg'] = not_mended",
    "sys.argv = ['videopodcast-magic'] + sys.argv[1:]",
    "sys.exit(vpm.main())"])
code, last, _said = run([sys.executable, "-c", TOOLLESS,
                         "--without-auphonic", NOTES])
try:
    with open(MENDED, encoding="utf-8") as f:
        mended = len(f.read().splitlines())
except OSError:
    mended = 0
WANT = (vpm.T('Nothing runs until that is put right. This way: %s')
        % vpm.how_to_get_ffmpeg(False)).splitlines()[-1].strip()
check("the repair asks the stand-in, never an installer", mended >= 1,
      "the stand-in was asked %d times against at least 1" % mended)
check("a run with no ffmpeg that is not repaired returns 1", code == 1,
      "returned %r against 1" % code)
check("and its last line says nothing runs until that is put right",
      last == WANT, "last line %r against %r" % (last, WANT))

print("\n6. Multitrack over a single recording")
ALONE = os.path.join(HOME, "Presenter_REC0001.wav")
made = subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i",
                       "sine=frequency=440:duration=2", "-c:a", "pcm_s16le",
                       ALONE], stdout=subprocess.PIPE,
                      stderr=subprocess.STDOUT, timeout=ASK)
# A precondition of the material, not a judgement about the program.
assert made.returncode == 0 and os.path.exists(ALONE), made.stdout
code, last, _said = run([sys.executable, SCRIPT, "--multitrack",
                         "--without-auphonic", "--out",
                         os.path.join(HOME, "out6"), ALONE])
WANT = (vpm.T('MULTITRACK NOT POSSIBLE\n  At least two input tracks are '
              'needed, and only %s was found.\n  A track is a recording of '
              'its own, a channel of a multichannel\n  recorder, or the '
              'audio of a camera -- that counts as soon as its\n  Camera '
              'audio says "use internal audio". Without two of them '
              'there\n  '
              'is nothing to decouple, and the same file runs through as an\n'
              '  ordinary production.')
        % vpm.number_text(1, 0)).splitlines()[-1].strip()
check("multitrack over one recording returns 1", code == 1,
      "returned %r against 1, last line %r" % (code, last))
check("and its last line says it would run as an ordinary production",
      last == WANT, "last line %r against %r" % (last, WANT))

print("\n7. The one-shot jobs that cannot do theirs")
# The look for new versions switched off is the fault here, so --update
# is refused before anything could leave; the proxies to nowhere stand
# behind it. Named as the program reads it: the fence's lower case
# would take the switch away. The lone camera of section 2 is SDR.
code, last, _said = run([sys.executable, SCRIPT, "--update"],
                        dict(FENCE, VPM_NO_UPDATE_CHECK="1"))
WANT = vpm.T('The check for new versions is switched off here.')
check("an --update that cannot look returns 1", code == 1,
      "returned %r against 1, last line %r" % (code, last))
check("and its last line says the look is switched off", last == WANT,
      "last line %r against %r" % (last, WANT))
code, last, _said = run([sys.executable, SCRIPT, "--hdr-check", CAMERA])
WANT = vpm.T('The file is NOT recognised as HDR.')
check("an --hdr-check over a file that is not HDR returns 1", code == 1,
      "returned %r against 1, last line %r" % (code, last))
check("and its last line says the file is not recognised as HDR",
      last == WANT, "last line %r against %r" % (last, WANT))

print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
