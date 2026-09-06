# -*- coding: utf-8 -*-
"""A choice made in one run is found by the next, and by nobody else.

The first thing this program keeps between two starts is the language
of its window. The sections: the choice comes back after a restart and
lies where it was asked to; the order --lang, kept choice, system holds;
a broken file costs the choice and nothing more; an entry this version
does not know survives a write; a test run refuses a place rather than
write into somebody's home, and a run that only reads builds nothing at
all; and none of it needs Qt.

The restart is a real one -- a second interpreter, not set_language()
called twice in this process. A store that only works while the module
stays loaded is what this test exists to rule out.
"""
import os
import the_program
SCRIPT = the_program.SCRIPT
import json
import shutil
import subprocess
import sys
import tempfile
import time

vpm = the_program.load()
vpm.set_language("de")
GERMAN = vpm.T('The check for new versions is switched off here.')
vpm.set_language("en")
ENGLISH = vpm.T('The check for new versions is switched off here.')

began = time.time()
done = 0
bad = []


def check(name, ok, extra=""):
    global done
    done += 1
    print("  %-58s %s %s" % (name, "ok" if ok else "FAIL", extra))
    if not ok:
        bad.append("%s [%s]" % (name, extra or "no numbers"))


FOLDER = tempfile.mkdtemp(prefix="vpm_choice_")
STORE = os.path.join(FOLDER, "store")
os.makedirs(STORE)
FILE = os.path.join(STORE, "videopodcast-magic", "settings.json")

# The system says French in every run below, and it is neither the
# language written into the file nor the one the untranslated source is
# in -- so none of the three answers can be mistaken for another.
# VPM_SETTINGS keeps the test out of the settings of whoever started it.
ENV = dict(os.environ, LANG="fr_FR.UTF-8", LC_ALL="fr_FR.UTF-8",
           LANGUAGE="fr", VPM_SILENT="1", VPM_NO_UPDATE_CHECK="1",
           VPM_SETTINGS=STORE)
LOAD = ("import importlib.util, sys\n"
        "spec = importlib.util.spec_from_file_location('vpm', %r)\n"
        "m = importlib.util.module_from_spec(spec)\n"
        "sys.modules['vpm'] = m\n"
        "spec.loader.exec_module(m)\n" % SCRIPT)


def started(code, env=None):
    """A fresh interpreter with the program in it, and what it printed."""
    said = subprocess.run([sys.executable, "-c", LOAD + code],
                          env=env or ENV, capture_output=True, text=True)
    if said.returncode:
        return "died: " + (said.stderr.strip().splitlines() or [""])[-1][:70]
    return (said.stdout.strip().splitlines() or [""])[-1]


def asked(env=None):
    """The language a fresh start of the program speaks."""
    return started("print(m.LANG)", env)


def update_line(*args, **kw):
    """What --update says. Translated, so it shows the language chosen."""
    said = subprocess.run([sys.executable, SCRIPT, "--update"] + list(args),
                          env=kw.get("env") or ENV,
                          capture_output=True, text=True)
    return (said.stdout.strip().splitlines() or [""])[-1]


# ----------------------------------------------- it survives a restart
wrote = started("print(m.keep_setting('language', 'de'))")
after = asked()
check("a language written in one run is spoken by the next",
      after == "de", "the write said %s, the next run said %s"
      % (wrote, after))
check("the settings file lands where VPM_SETTINGS points",
      os.path.exists(FILE), "no settings.json under the folder named; it "
      "holds %s" % (os.listdir(os.path.dirname(FILE))
                    if os.path.isdir(os.path.dirname(FILE)) else "nothing"))
check("the file is a readable dictionary naming the language",
      json.loads(open(FILE).read()).get("language") == "de",
      open(FILE).read().replace("\n", " ")[:60])

# ------------------------------------ --lang, then the kept choice, then
# the system. --update needs no network with VPM_NO_UPDATE_CHECK set and
# says one translated line, which is enough to see which of the three
# won: German is in the file, French is the system, English is neither.
EMPTY = dict(ENV, VPM_SETTINGS=os.path.join(FOLDER, "nothing"))
got = asked(EMPTY)
check("with nothing written, the system's language is spoken",
      got == "fr", "the system said fr_FR, the program said %s" % got)
said = update_line()
check("a run without --lang keeps the language that was written",
      said == GERMAN, "wanted %r, got %r" % (GERMAN[:40], said[:40]))
said = update_line("--lang", "en")
check("--lang on the command line beats the written choice",
      said == ENGLISH, "wanted %r, got %r" % (ENGLISH[:40], said[:40]))
check("--lang did not overwrite what was written",
      json.loads(open(FILE).read()).get("language") == "de",
      open(FILE).read().replace("\n", " ")[:60])

# ------------------------------------- a broken file costs the choice only
# Written out one by one and not looped: a computed name would leave one
# row in the register standing for five judgements at once.


def wrote_and_asked(blob):
    """Lay that file down and ask the next start what it speaks."""
    with open(FILE, "wb") as f:
        f.write(blob)
    return asked()


got = wrote_and_asked(b"")
check("an empty settings file costs the choice and no more",
      got == "fr", "wanted the system's fr, got %s" % got)
got = wrote_and_asked(b'{"language": "d')
check("half a line of JSON costs the choice and no more",
      got == "fr", "wanted the system's fr, got %s" % got)
got = wrote_and_asked(b'["de"]')
check("a list instead of a dictionary costs the choice and no more",
      got == "fr", "wanted the system's fr, got %s" % got)
got = wrote_and_asked(b'{"language": "kl"}')
check("a language with no texts falls through to the system",
      got == "fr", "wanted the system's fr, got %s" % got)
got = wrote_and_asked(b'{"language": {"a": 1}}')
check("an entry that is not text falls through to the system",
      got == "fr", "wanted the system's fr, got %s" % got)

# --------------------------------- room for more than the one setting
open(FILE, "w").write('{"language": "de", "later": {"a": 1}}')
started("m.keep_setting('language', 'fr')")
kept = json.loads(open(FILE).read())
check("an entry this version does not know survives a write",
      kept.get("later") == {"a": 1} and kept.get("language") == "fr",
      repr(kept)[:60])

# ------------------------------------------ a test run stays out of the way
# No VPM_SETTINGS, because that is the whole of what is asked here.
# But the fall-back place is somebody's own home, and a counter-proof
# for the next two checks takes the guard out -- so the run wrote
# "zh" into the real settings of whoever earned the row, and the
# window spoke Chinese at the next start. Measured 6.9.2026. HOME,
# APPDATA and XDG_CONFIG_HOME are what settings_folder falls back
# through; pointed at a throwaway they leave the question untouched
# and give a broken guard nowhere real to land.
NOWHERE = os.path.join(FOLDER, "not-a-home")
BLIND = dict(os.environ, LANG="C", LC_ALL="C", LANGUAGE="en",
             VPM_SILENT="1", VPM_NO_UPDATE_CHECK="1",
             HOME=NOWHERE, APPDATA=NOWHERE, XDG_CONFIG_HOME=NOWHERE)
BLIND.pop("VPM_SETTINGS", None)
lines = subprocess.run(
    [sys.executable, "-c", LOAD + "print(m.settings_file())\n"
     "print(m.keep_setting('language', 'zh'))\n"],
    env=BLIND, capture_output=True, text=True).stdout.strip().splitlines()
# Only the last parts of what it answered: the whole path names the
# home folder of whoever runs this, and a failure line travels.
place = (lines[:1] or [""])[0]
check("a silent run with no folder named refuses a place",
      place == "None", "wanted None, got ...%s" % place[-40:])
check("a silent run with no folder named refuses the write",
      lines[1:2] == ["False"], "wanted False, got %s"
      % ((lines[1:2] or ["nothing"])[0])[:20])

# Only a write builds anything: whoever never chooses a language must
# not find an empty folder for having started the program.
LOOKED = os.path.join(FOLDER, "looked")
os.makedirs(LOOKED)
started("m.settings()", dict(ENV, VPM_SETTINGS=LOOKED))
check("reading builds no folder, only writing does",
      os.listdir(LOOKED) == [], repr(os.listdir(LOOKED)))

# ------------------------------------------ the window is not needed for it
said = started("m.keep_setting('language', 'pt')\n"
               "m.settings()\n"
               "print([k for k in sys.modules if 'PySide' in k])")
check("reading and writing a setting loads no Qt", said == "[]", said[:60])

shutil.rmtree(FOLDER, ignore_errors=True)
print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
