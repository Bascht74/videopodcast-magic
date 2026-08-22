# -*- coding: utf-8 -*-
"""The transcript from auphonic.com: asked for, and fetched.

Nothing here talks to auphonic.com. What is checked is the shape of the
request and what is done with the answer -- the two places where a
mistake would cost a whole production to find out.
"""
import os
HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = os.environ.get("VPM_SCRIPT") or os.path.join(
    os.path.dirname(HERE), "videopodcast-magic.py")
import importlib.util, shutil, sys, tempfile
spec = importlib.util.spec_from_file_location("vpm", SCRIPT)
vpm = importlib.util.module_from_spec(spec); sys.modules["vpm"] = vpm
spec.loader.exec_module(vpm)

error = []
def check(name, ok, extra=""):
    print("  %-52s %s %s" % (name, "ok" if ok else "FAIL", extra))
    if not ok:
        error.append(name)

print("1. What switches the recognition on")
block = vpm.transcript_block()
check("no service is named, so Auphonic uses its own",
      "uuid" not in block, str(block))
check("and no summary is asked for", block.get("shownotes") is False)
check("without a language it says nothing about one",
      "language" not in block, str(block))
check("with one it passes it on",
      vpm.transcript_block("de").get("language") == "de")

print("\n2. What is asked for as output")
want = vpm.transcript_outputs([])
kinds = sorted((f["format"], f["ending"]) for f in want)
check("three files: times, subtitles, reading",
      kinds == [("speech", "json"), ("subtitle", "srt"),
                ("transcript", "txt")], str(kinds))
again = vpm.transcript_outputs([{"format": "subtitle", "ending": "srt"}])
check("what is already there is not asked for twice",
      len(again) == 2, str(again))
check("and the rest still is",
      sorted(f["format"] for f in again) == ["speech", "transcript"])

print("\n3. Sending an output file back")
answer = {"format": "mp3", "ending": "mp3", "bitrate": "192",
          "size": 12345, "download_url": "https://x/y", "checksum": "abc",
          "filename": "out.mp3", "size_string": "12 MB"}
wish = vpm.output_file_wish(answer)
check("what may be asked for again is kept",
      wish == {"format": "mp3", "ending": "mp3", "bitrate": "192",
               "filename": "out.mp3"}, str(wish))
check("what only an answer can carry is dropped",
      not any(k in wish for k in ("size", "download_url", "checksum",
                                  "size_string")))

print("\n4. A multitrack request carries it all")
preset = {"preset_name": "P", "is_multitrack": True,
          "multi_input_files": [{"algorithms": {"denoise": True}}],
          "metadata": {"title": "old"}}
plain = vpm.build_multitrack_request(preset, "Show", ["A", "B"], "show")
check("without the switch nothing is added",
      "speech_recognition" not in plain, str(plain.get("speech_recognition")))
with_text = vpm.build_multitrack_request(preset, "Show", ["A", "B"], "show",
                                         None, True, "de")
check("with it the recognition is in the request",
      with_text.get("speech_recognition", {}).get("language") == "de")
formats = [f["format"] for f in with_text["output_files"]]
check("the single tracks are still asked for", "tracks" in formats,
      str(formats))
check("and the three text files as well",
      all(f in formats for f in ("speech", "subtitle", "transcript")),
      str(formats))
check("the tracks stay unchanged",
      [t["id"] for t in with_text["multi_input_files"]] == ["A", "B"])

print("\n5. From the interface to the command line")
base = {"files": [("/tmp/a.wav", "audio")], "out_folder": "/tmp/out",
        "key": "K", "preset": "P"}
argv, _plan, _msg = vpm.run_argv(dict(base, transcript=True))
check("the switch is passed on", "--transcript" in (argv or []), str(argv))
argv, _plan, _msg = vpm.run_argv(dict(base, transcript=False))
check("and left out when it is off", "--transcript" not in (argv or []))
argv, _plan, _msg = vpm.run_argv({"files": [("/tmp/a.wav", "audio")],
                                  "out_folder": "/tmp/out",
                                  "transcript": True})
check("without a key there is nobody to transcribe",
      "--transcript" not in (argv or []), str(argv))
ap = vpm.build_argument_parser()
check("the command line knows it",
      ap.parse_args(["x.wav", "--transcript"]).transcript is True)

print("\n6. The tag of the audio track is not the recognition language")
check("ISO 639-2/B becomes the two letter code",
      vpm.speech_language_code("ger") == "de",
      vpm.speech_language_code("ger"))
check("the other spelling too", vpm.speech_language_code("deu") == "de")
check("English as well", vpm.speech_language_code("eng") == "en")
check("upper case does not matter",
      vpm.speech_language_code("GER") == "de")
check("a two letter code is passed through",
      vpm.speech_language_code("de") == "de")
check("with a country as well",
      vpm.speech_language_code("de-DE") == "de-DE")
check("nothing stays nothing", vpm.speech_language_code("") == "")
check("an unknown code is not guessed at",
      vpm.speech_language_code("xyz") == "",
      repr(vpm.speech_language_code("xyz")))

print("\n6b. The list of languages the interface offers")
check("every language offered can also be recognised",
      all(vpm.speech_language_code(tag) for tag, _n in
          vpm.SPOKEN_LANGUAGES),
      str([t for t, _n in vpm.SPOKEN_LANGUAGES
           if not vpm.speech_language_code(t)]))
check("no tag appears twice",
      len({t for t, _n in vpm.SPOKEN_LANGUAGES})
      == len(vpm.SPOKEN_LANGUAGES))
names = [n for _t, n in vpm.spoken_language_choices()]
check("the list is sorted by name",
      names == sorted(names, key=str.lower), str(names[:4]))
check("and German is in it",
      "ger" in [t for t, _n in vpm.spoken_language_choices()])
was = dict(os.environ)
try:
    for k in ("LANGUAGE", "LC_ALL", "LC_MESSAGES", "LANG"):
        os.environ.pop(k, None)
    os.environ["LANG"] = "de_DE.UTF-8"
    check("a German system suggests ger",
          vpm.language_of_system() == "ger", vpm.language_of_system())
    os.environ["LANG"] = "en_GB.UTF-8"
    check("an English one suggests eng",
          vpm.language_of_system() == "eng", vpm.language_of_system())
    os.environ["LANG"] = "es_ES.UTF-8"
    check("a Spanish one suggests spa -- not the interface language",
          vpm.language_of_system() == "spa", vpm.language_of_system())
    os.environ["LANG"] = "xx_XX.UTF-8"
    check("an unknown one suggests nothing",
          vpm.language_of_system() == "", repr(vpm.language_of_system()))

finally:
    os.environ.clear()
    os.environ.update(was)

print("\n7. The language goes to the command line")
argv, _plan, _msg = vpm.run_argv(
    {"files": [("/tmp/a.wav", "audio")], "speech_language": "ger"})
check("as it was typed", "--speech-language" in (argv or [])
      and argv[argv.index("--speech-language") + 1] == "ger", str(argv))
argv, _plan, _msg = vpm.run_argv(
    {"files": [("/tmp/a.wav", "audio")], "speech_language": "  "})
check("and left out when empty", "--speech-language" not in (argv or []))

print("\n8. Fetching what is text, leaving what is audio")
folder = tempfile.mkdtemp(prefix="vpm_text_")
asked = []
real = vpm._curl_call
vpm._curl_call = lambda key, arguments, **k: asked.append(arguments) or b""
files = [{"filename": "show.wav", "download_url": "u1"},
         {"filename": "show.json", "download_url": "u2"},
         {"filename": "show.srt", "download_url": "u3"},
         {"filename": "show.txt", "download_url": "u4"},
         {"filename": "show.mp3", "download_url": "u5"},
         {"filename": "nourl.srt"}]
vpm.fetch_text_outputs("K", files, folder, skip=files[0])
vpm._curl_call = real
got = [a[-1] for a in asked]
check("the three text files are fetched",
      sorted(got) == ["u2", "u3", "u4"], str(got))
check("the audio is not fetched again", "u1" not in got and "u5" not in got)
check("and one without an address is passed over", "nourl" not in str(asked))
shutil.rmtree(folder, ignore_errors=True)

print()
if error:
    print("FAIL: " + ", ".join(error))
    sys.exit(1)
print("All good.")
