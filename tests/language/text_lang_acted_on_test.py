# -*- coding: utf-8 -*-
"""--lang is acted on, not only accepted: two languages, two answers.

The program is really started, once with --lang de and once with
--lang en, on a file that is not there, and what it prints is held
apart: first that both runs answered, then that they differ. No wording
is held against anything, so it says the same on a German machine and
on an English one. That the switch is there and parses is read in
memory by text_only_texts_change.
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
import subprocess
import time
import the_program

began = time.time()
SCRIPT = the_program.SCRIPT

done = 0
error = []
def check(name, ok, extra=""):
    global done
    done += 1
    print("  %-54s %s %s" % (name, "ok" if ok else "FAIL", extra))
    if not ok:
        error.append(name)


print("1. The --lang switch, acted on")
# Arriving in the parser is not the same as being acted on. A run whose
# --lang goes nowhere falls back on the system's language, and on a
# machine set to German that looks exactly right -- which is why the
# program is really started here, once per language, on a file that is
# not there so nothing is read and nothing is written. The two runs
# only have to differ: no wording is held against anything, so this
# says the same on a German machine and on an English one. Both streams
# together, because the line that names a missing file goes to stderr
# and the banner above it is language-free.
GONE = "/tmp/vpm-no-such-recording.wav"
# The program looks for ffmpeg before it ever looks at --lang, and where
# it finds none it offers the package manager -- asked, and only where
# somebody is there to answer. A question about the language must not
# reach even that, so the run gets no console to be asked on, and a pip
# that can neither reach an index nor write outside a virtual
# environment.
#
# The pip half is kept although the program no longer fetches ffmpeg
# that way. It still fetches numpy and PySide6, and it asks first -- but
# this seal is what an unasked install would have run into, and it is
# not theory: an earlier version of these two runs put a wheel of
# ffmpeg binaries into the system Python. A seal is cheap; taking one
# away because the hole it covers is closed today is how the hole comes
# back.
SEALED = dict(os.environ, VPM_NO_UPDATE_CHECK="1",
              PIP_NO_INDEX="1", PIP_REQUIRE_VIRTUALENV="1", PIP_NO_INPUT="1")
SEALED.pop("VPM_INSTALL_TOOLS", None)
spoken, codes = {}, {}
for _code in ("de", "en"):
    try:
        _r = subprocess.run([sys.executable, SCRIPT, "--lang", _code, GONE],
                            capture_output=True, stdin=subprocess.DEVNULL,
                            timeout=300, env=SEALED)
        spoken[_code] = _r.stdout + _r.stderr
        codes[_code] = _r.returncode
    except subprocess.TimeoutExpired:
        spoken[_code], codes[_code] = b"", "timed out after 300 s"
# Asked before the judgement under it, and not folded into it: a
# machine on which the program cannot start at all prints the same
# thing twice, and that must read as "it did not run" and not as
# "--lang does nothing".
fell_over = b"Traceback" in spoken["de"] + spoken["en"]
check("the program answers on both runs",
        bool(spoken["de"]) and bool(spoken["en"])
        and codes["de"] == codes["en"] and not fell_over,
        "--lang de: %d characters, returned %s; --lang en: %d characters, "
        "returned %s; a traceback in them: %s"
        % (len(spoken["de"]), codes["de"], len(spoken["en"]), codes["en"],
           "yes" if fell_over else "no"))
apart = ""
for _a, _b in zip(spoken["de"].splitlines(), spoken["en"].splitlines()):
    if _a != _b:
        apart = "%s against %s" % (repr(_a[:36]), repr(_b[:36]))
        break
check("--lang is acted on, not only accepted",
        spoken["de"] != spoken["en"],
        "--lang de and --lang en print %d and %d characters; first line "
        "that differs: %s" % (len(spoken["de"]), len(spoken["en"]),
                              apart or "none -- the two runs are the same"))

print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + ", ".join(error) if error else "ALL OK")
sys.exit(1 if error else 0)
