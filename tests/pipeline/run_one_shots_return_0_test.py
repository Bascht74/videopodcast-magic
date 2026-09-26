# -*- coding: utf-8 -*-
"""A one-shot job that did its work returns 0 and says so last.

Each case is a bare command line in a process of its own, answered
without a run: --update with nothing newer to fetch (the look stood in
for, and fenced behind a proxy to nowhere), the preset list of an
account (curl stood in for, fenced the same way), and --hdr-check over
a file tagged as HDR. Where one of them fails, main() returning 1 is
run_stop_names_why's; this holds the other half, which a script reads.
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
import re
import subprocess
import tempfile
import time
from fixture_root import fixture

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


# Each start here ends within seconds; the bound only names one that
# never ends in its own line, well before run.sh ends the whole test.
ASK = 120.0
# A port nothing listens on: whatever gets past a stand-in reaches no
# server, and the switch that keeps the look off is taken away where
# the look itself is what is asked.
NOWHERE = "http://127.0.0.1:9"
FENCE = {"https_proxy": NOWHERE, "http_proxy": NOWHERE,
         "all_proxy": NOWHERE, "no_proxy": None}


def run(argv, fence=None):
    """The program's way in, in its own process: (code, last line, all).

    The code is None if it did not end within ASK. `fence` replaces the
    variables it names, in lower case for either spelling, and one set
    to None is taken away.
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
    text = re.sub(r"\x1b\[[0-9;]*m", "", text).replace("\r", "\n")
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    return kid.returncode, (lines[-1] if lines else ""), "\n".join(lines)


def times_asked(path):
    """How many lines a stand-in left in `path`."""
    try:
        with open(path, encoding="utf-8") as f:
            return len(f.read().splitlines())
    except OSError:
        return 0


HOME = tempfile.mkdtemp(prefix="vpm_oneshot_")

print("1. --update with nothing newer to fetch")
LOOKED = os.path.join(HOME, "looked")
# The newest release is the one running: nothing to fetch, and the job
# is done. Bent where newer_release looks it up, and the switch that
# keeps the look off in a test run is lifted for this child alone.
UPDATE_CHILD = "\n".join([
    "import io, json, sys, urllib.request",
    "sys.path.insert(0, %r)" % HERE,
    "import the_program",
    "vpm = the_program.load()",
    "def the_same_release(*a, **k):",
    "    with open(%r, 'a') as f:" % LOOKED,
    "        f.write('asked\\n')",
    "    return io.BytesIO(json.dumps({'tag_name': vpm.VERSION,",
    "        'html_url': '', 'body': ''}).encode('utf-8'))",
    "urllib.request.urlopen = the_same_release",
    "sys.argv = ['videopodcast-magic', '--update']",
    "sys.exit(vpm.main())"])
code, last, _said = run([sys.executable, "-c", UPDATE_CHILD],
                        dict(FENCE, vpm_no_update_check=None))
looked = times_asked(LOOKED)
WANT = vpm.T('No newer version found. This one is %s.') % vpm.VERSION
check("--update looks through the stand-in, never the network",
      looked >= 1, "the stand-in was asked %d times against at least 1"
      % looked)
check("--update with nothing newer returns 0", code == 0,
      "returned %r against 0, last line %r" % (code, last))
check("and its last line says this version is the newest",
      last == WANT, "last line %r against %r" % (last, WANT))

print("\n2. The presets of an account")
ASKED = os.path.join(HOME, "asked")
PRESET = "Standin Singletrack preset"
# One ordinary preset, answered where list_presets asks curl.
PRESET_CHILD = "\n".join([
    "import json, sys",
    "sys.path.insert(0, %r)" % HERE,
    "import the_program",
    "vpm = the_program.load()",
    "def one_preset(*a, **k):",
    "    with open(%r, 'a') as f:" % ASKED,
    "        f.write('asked\\n')",
    "    return json.dumps({'status_code': 200, 'data': [{",
    "        'preset_name': %r, 'uuid': 'u1', 'is_multitrack': False}]})"
    % PRESET,
    "vpm.list_presets.__globals__['_curl_call'] = one_preset",
    "sys.argv = ['videopodcast-magic'] + sys.argv[1:]",
    "sys.exit(vpm.main())"])
code, last, _said = run([sys.executable, "-c", PRESET_CHILD,
                         "--auphonic-api-key", "not-a-real-key"], FENCE)
asked = times_asked(ASKED)
WANT = "1  %s" % PRESET
check("the fetched presets come from the stand-in, never the "
      "network", asked >= 1,
      "the stand-in was asked %d times against at least 1" % asked)
check("a preset list that was fetched returns 0", code == 0,
      "returned %r against 0, last line %r" % (code, last))
check("and its last line is the account's preset, numbered",
      last == WANT, "last line %r against %r" % (last, WANT))

print("\n3. --hdr-check over a file tagged as HDR")
HDR = os.path.join(fixture("hdrtest"), "hdr10.mp4")
if os.path.exists(HDR):
    code, last, _said = run([sys.executable, SCRIPT, "--hdr-check", HDR])
    WANT = vpm.T('The file is tagged as HDR.')
    check("--hdr-check over an HDR10 file returns 0", code == 0,
          "returned %r against 0, last line %r" % (code, last))
    check("and its last line says the file is tagged as HDR",
          last == WANT, "last line %r against %r" % (last, WANT))
else:
    print("SKIPPED: no %s -- run tests/fixtures.sh, which builds the "
          "HDR files under hdrtest" % HDR)

print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
