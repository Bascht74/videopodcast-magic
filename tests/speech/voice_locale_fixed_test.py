# -*- coding: utf-8 -*-
"""A language is heard in the same locale every time, whatever the list.

The recognition macOS brings with it lists the locales it offers in a
different order on every call, and English came out as en_NZ, en_GB or
en_IN on the same file. Sections: the choice over a given list and a
given region -- the machine's region, the fixed locale, the first by
name, a whole locale asked for, a language not offered -- then the
door, where the chosen locale is what the recogniser is handed.

Nothing is recognised: the list is written out here, and the
recogniser is stood in for by something that only answers.
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
import shutil
import subprocess
import tempfile
import time
vpm = the_program.load()

began = time.time()
done = 0
bad = []


def check(name, ok, extra=""):
    global done
    done += 1
    print("  %-58s %s %s" % (name, "ok" if ok else "FAIL", extra))
    if not ok:
        bad.append("%s [%s]" % (name, extra or "no numbers"))


vpm.set_language("en")

# Three orders the English locales really came in, one call after the
# other, on a Mac whose region is Germany -- shortened to what matters.
ORDERS = (
    ["fr_FR", "en_NZ", "de_DE", "en_GB", "en_US", "en_IN", "de_CH"],
    ["en_GB", "de_CH", "en_US", "en_IN", "fr_FR", "de_DE", "en_NZ"],
    ["en_IN", "de_DE", "en_NZ", "fr_FR", "de_CH", "en_US", "en_GB"],
)
choose = vpm.speech_locale_choice


print("\n1. The choice over a given list")

got = [choose("en", order, "DE") for order in ORDERS]
check("English is en_US whichever order the list comes in",
      got == ["en_US", "en_US", "en_US"],
      "three orders gave %s, wanted en_US each time" % got)

got = [choose("de", ORDERS[1], "CH"), choose("en", ORDERS[2], "GB")]
check("the machine's region comes before the fixed locale",
      got == ["de_CH", "en_GB"],
      "German on a Swiss Mac and English on a British one gave %s, "
      "wanted ['de_CH', 'en_GB']" % got)

without_us = (["en_NZ", "en_GB", "en_IN", "de_DE"],
              ["en_IN", "de_DE", "en_GB", "en_NZ"])

got = [choose("en", order, "DE") for order in without_us]
check("with neither, the first by name, whatever the list's order",
      got == ["en_GB", "en_GB"],
      "region DE gave %s, wanted en_GB (before en_IN, en_NZ) each time"
      % got)

got = choose("en-GB", ORDERS[0], "DE")
check("a whole locale asked for is taken as it stands",
      got == "en_GB", "'en-GB' gave %r, wanted 'en_GB'" % got)

got = choose("nl", ORDERS[2], "DE")
check("a language the machine does not offer gives no locale",
      got == "", "Dutch gave %r out of a list without it, wanted ''" % got)

got = choose("no", ["nb_NO", "da_DK", "sv_SE"], "DE")
check("Norwegian is heard as Bokmal, the locale macOS names it by",
      got == "nb_NO", "'no' gave %r, wanted 'nb_NO'" % got)


print("\n2. The door into the recognition macOS brings with it")


class Ran(object):
    """What subprocess.run gives back: the two fields macos_words reads."""

    def __init__(self, returncode, stdout):
        self.returncode = returncode
        self.stdout = stdout


class MacDoor(object):
    """Stand in for subprocess, and for the Swift recogniser behind it.

    Asked for its list it answers with the region and one of the orders
    above; asked to listen, it takes only an exact locale off that list
    -- stricter than the real one, which falls back to the machine's
    own language without a word.
    """

    PIPE = subprocess.PIPE
    STDOUT = subprocess.STDOUT

    def __init__(self, order):
        self.order = order
        self.handed = []

    def run(self, cmd, **_ignored):
        if list(cmd[1:]) == ["--locales"]:
            return Ran(0, ("REGION DE\n" + "\n".join(self.order) + "\n")
                       .encode("utf-8"))
        self.handed.append(cmd[3] if len(cmd) > 3 else None)
        if cmd[3] not in self.order:
            return Ran(1, ("ERR no locale %s" % cmd[3]).encode("utf-8"))
        with open(cmd[2], "w", encoding="utf-8") as f:
            f.write("0.000\t0.400\tGood\n0.400\t0.900\tmorning.\n")
        return Ran(0, b"")


folder = tempfile.mkdtemp(prefix="vpm_locale_")
audio = os.path.join(folder, "mix_full.wav")
open(audio, "wb").close()
handed, heard = [], []
was_program, was_subprocess = vpm.recogniser_program, vpm.subprocess
try:
    for n, order in enumerate(ORDERS):
        door = MacDoor(order)
        # A program of its own each time, so the list one call was
        # given is not the one the next call reads back.
        vpm.recogniser_program = (
            lambda *a, n=n, **k: os.path.join(folder, "recog%d" % n))
        vpm.subprocess = door
        words = vpm.macos_words(audio, "eng")
        handed += door.handed
        heard.append(len(words or []))
finally:
    vpm.recogniser_program = was_program
    vpm.subprocess = was_subprocess
    shutil.rmtree(folder, ignore_errors=True)

check("the recogniser is handed the fixed locale, not the code",
      handed == ["en_US", "en_US", "en_US"] and heard == [2, 2, 2],
      "'eng' over three orders was handed %s and heard %s words, "
      "wanted en_US and 2 each time" % (handed, heard))


print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
