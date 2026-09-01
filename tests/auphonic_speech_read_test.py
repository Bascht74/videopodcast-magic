# -*- coding: utf-8 -*-
"""What a production writes about the audio, and in which language.

Nothing here talks to auphonic.com. The language is the tag the run
carries: which ones the interface offers, which one the system
suggests, and how it reaches the command line. The fetching is held
against a stand-in that notes the address instead of opening it, so
what is checked is which files are asked for and which are left alone.
"""
import os
HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = os.environ.get("VPM_SCRIPT") or os.path.join(
    os.path.dirname(HERE), "videopodcast-magic.py")
import importlib.util, shutil, sys, tempfile, time

began = time.time()

spec = importlib.util.spec_from_file_location("vpm", SCRIPT)
vpm = importlib.util.module_from_spec(spec); sys.modules["vpm"] = vpm
spec.loader.exec_module(vpm)

done = 0
bad = []


def check(name, ok, extra=""):
    global done
    done += 1
    print("  %-52s %s %s" % (name, "ok" if ok else "FAIL", extra))
    if not ok:
        bad.append("%s [%s]" % (name, extra or "no numbers"))


print("1. The language the interface offers")
# A tag without a two letter code cannot be suggested: language_of_system
# reads the system's code and looks for the tag that carries it, so a
# language offered without one can never come up by itself.
codeless = [t for t, _n in vpm.SPOKEN_LANGUAGES if not vpm.SPEECH_CODES.get(t)]
check("every language offered is one the system can suggest",
      not codeless, "%d of %d without a two letter code: %s"
      % (len(codeless), len(vpm.SPOKEN_LANGUAGES), codeless))
tags = [t for t, _n in vpm.SPOKEN_LANGUAGES]
check("no tag appears twice", len(set(tags)) == len(tags),
      "%d tags, %d different" % (len(tags), len(set(tags))))
names = [n for _t, n in vpm.spoken_language_choices()]
out_of_order = [(a, b) for a, b in zip(names, names[1:])
                if a.lower() > b.lower()]
check("the list is sorted by name", not out_of_order,
      "%d pairs the wrong way round, first %s"
      % (len(out_of_order), out_of_order[:1] or "--"))
offered = [t for t, _n in vpm.spoken_language_choices()]
check("and German is in it", "ger" in offered,
      "%d languages offered: %s ..." % (len(offered), offered[:4]))

print("\n2. What the system suggests")
was = dict(os.environ)
try:
    for k in ("LANGUAGE", "LC_ALL", "LC_MESSAGES", "LANG"):
        os.environ.pop(k, None)
    os.environ["LANG"] = "de_DE.UTF-8"
    check("a German system suggests ger",
          vpm.language_of_system() == "ger",
          "de_DE.UTF-8 gave %r, wanted 'ger'" % vpm.language_of_system())
    os.environ["LANG"] = "en_GB.UTF-8"
    check("an English one suggests eng",
          vpm.language_of_system() == "eng",
          "en_GB.UTF-8 gave %r, wanted 'eng'" % vpm.language_of_system())
    os.environ["LANG"] = "es_ES.UTF-8"
    check("a Spanish one suggests spa -- not the interface language",
          vpm.language_of_system() == "spa",
          "es_ES.UTF-8 gave %r, wanted 'spa'" % vpm.language_of_system())
    os.environ["LANG"] = "xx_XX.UTF-8"
    check("an unknown one suggests nothing",
          vpm.language_of_system() == "",
          "xx_XX.UTF-8 gave %r, wanted ''" % vpm.language_of_system())
finally:
    os.environ.clear()
    os.environ.update(was)

print("\n3. The language goes to the command line")
argv, _plan, _msg = vpm.run_argv(
    {"files": [("/tmp/a.wav", "audio")], "speech_language": "ger"})
argv = argv or []
after = (argv[argv.index("--speech-language") + 1]
         if "--speech-language" in argv else None)
check("as it was typed", after == "ger",
      "--speech-language followed by %r, wanted 'ger', among %d words"
      % (after, len(argv)))
argv, _plan, _msg = vpm.run_argv(
    {"files": [("/tmp/a.wav", "audio")], "speech_language": "  "})
check("and left out when empty", "--speech-language" not in (argv or []),
      "%d switches, %d of them --speech-language"
      % (len(argv or []), (argv or []).count("--speech-language")))

print("\n4. Fetching what is text, leaving what is audio")
folder = tempfile.mkdtemp(prefix="vpm_text_")
asked = []
real = vpm._curl_call
files = [{"filename": "show.wav", "download_url": "u1"},
         {"filename": "show.json", "download_url": "u2"},
         {"filename": "show.srt", "download_url": "u3"},
         {"filename": "show.txt", "download_url": "u4"},
         {"filename": "show.mp3", "download_url": "u5"},
         {"filename": "nourl.srt"}]
try:
    vpm._curl_call = lambda key, arguments, **k: asked.append(arguments) or b""
    vpm.fetch_text_outputs("K", files, folder, skip=files[0])
finally:
    vpm._curl_call = real
got = [a[-1] for a in asked]
check("the three text files are fetched", sorted(got) == ["u2", "u3", "u4"],
      "%d fetched: %s, wanted u2 u3 u4" % (len(got), sorted(got)))
check("the audio is not fetched again",
      "u1" not in got and "u5" not in got,
      "u1 and u5 are the audio and must not be among the %d fetched: %s"
      % (len(got), sorted(got)))
check("and one without an address is passed over",
      "nourl" not in str(asked),
      "%d calls, none may name nourl.srt -- fetched to %s"
      % (len(asked), [os.path.basename(a[-2]) for a in asked]))
shutil.rmtree(folder, ignore_errors=True)

print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
