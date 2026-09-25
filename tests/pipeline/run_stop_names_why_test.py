# -*- coding: utf-8 -*-
"""A run main() stops returns 1, its last line naming what failed and why.

main() catches what goes wrong and says it in one line. Reached here
from a bare command line, the program in a process of its own: the
list of presets, with the place list_presets reaches curl through
replaced by a stand-in that counts its calls, and every curl fenced
off behind a proxy that goes nowhere; and a lone camera with no sound
on it, made here. For each: the return code, and the last line held
against the program's own sentence -- the reason, and the file.

The limit: --hdr-check and the two Resolve switches are not reached --
the first answers every way in from outside with its report, the others
lie past source_resolve_door_shut, which forbids them in any test.
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
    """The program's way in, in a process of its own: (code, last line).

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
        return None, "no end within %.0f s" % ASK
    text = kid.stdout.decode("utf-8", "replace")
    # Colour marks and a progress bar's carriage returns are not words.
    text = re.sub(r"\x1b\[[0-9;]*m", "", text).replace("\r", "\n")
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    return kid.returncode, (lines[-1] if lines else "")


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
code, last = run([sys.executable, "-c", CHILD,
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
code, last = run([sys.executable, SCRIPT, "--without-auphonic",
                  "--out", os.path.join(HOME, "out"), CAMERA])
WANT = vpm.T('Camera audio not usable: %s') % (
    vpm.T('%s has no audio track.') % os.path.basename(CAMERA))
check("a lone camera without sound returns 1", code == 1,
      "returned %r against 1" % code)
check("and its last line names the file and says it has no sound",
      last == WANT, "last line %r against %r" % (last, WANT))

print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
