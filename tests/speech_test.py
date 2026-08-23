# -*- coding: utf-8 -*-
"""Speech recognition: the words, their times and their punctuation.

Three things are checked here. That a word's punctuation is read the
same way every time -- sentence ends and clause boundaries are what
the cut hangs on later. That the words survive the handover file
unchanged. And that the two recognisers keep the rules that were
measured: the voice activity filter on Whisper, without which it
writes words into silence, and the correction each recogniser gets on
its own -- one for both would be a shared axis, and neither of them
is the truth.

The macOS part runs the real recogniser on a file this test speaks
itself, so it needs neither network nor material.
"""
import os
HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = os.environ.get("VPM_SCRIPT") or os.path.join(
    os.path.dirname(HERE), "videopodcast-magic.py")
import importlib.util
import json
import subprocess
import sys
import tempfile
import types
spec = importlib.util.spec_from_file_location("vpm", SCRIPT)
vpm = importlib.util.module_from_spec(spec); sys.modules["vpm"] = vpm
spec.loader.exec_module(vpm)

error = []
checked = [0]


def check(name, ok, extra=""):
    checked[0] += 1
    print("  %-54s %s %s" % (name, "ok" if ok else "FAIL", extra))
    if not ok:
        error.append(name)


print("1. What a word closes")
check("a full stop ends a sentence", vpm.word_mark("Versuch.") == "sentence")
check("so does a question mark", vpm.word_mark("Erkennung?") == "sentence")
check("and an exclamation mark", vpm.word_mark("Halt!") == "sentence")
check("three dots as well", vpm.word_mark("also...") == "sentence")
check("a comma breaks a clause", vpm.word_mark("Tag,") == "clause")
check("a mark inside a closing quote still counts",
      vpm.word_mark('"fertig."') == "sentence")
check("and inside a German one too", vpm.word_mark("»fertig.«") == "sentence")
check("a plain word closes nothing", vpm.word_mark("Tag") == "")
check("a compound hyphen is not a boundary", vpm.word_mark("Video-") == "")
check("nothing at all is nothing", vpm.word_mark("") == "")

print("\n2. Sentences and clauses out of the words")
WORDS = [vpm.speech_word(*w) for w in (
    (0.0, 0.5, "Guten"), (0.5, 1.1, "Tag,"), (1.1, 1.3, "das"),
    (1.3, 1.8, "ist"), (1.8, 2.6, "ein"), (2.6, 3.0, "Versuch."),
    (3.0, 3.6, "Und"), (3.6, 4.4, "weiter"))]
check("the sentence ends are the times of the marks",
      vpm.sentence_end_times(WORDS) == [3.0],
      str(vpm.sentence_end_times(WORDS)))
check("the clause boundaries as well",
      vpm.clause_break_times(WORDS) == [1.1])
check("a sentence starts at its first word",
      vpm.sentence_start_times(WORDS) == [0.0, 3.0],
      str(vpm.sentence_start_times(WORDS)))
check("the unclosed tail is a sentence too",
      len(vpm.sentences_of(WORDS)) == 2)
check("and it keeps its words",
      [w["word"] for w in vpm.sentences_of(WORDS)[1]] == ["Und", "weiter"])
check("no words, no boundaries",
      vpm.sentence_end_times([]) == [] and vpm.sentences_of([]) == [])

print("\n3. Through the handover file and back")
folder = tempfile.mkdtemp(prefix="vpm_speech_")
path = os.path.join(folder, "handover.json")
d = {"format": vpm.FILE_FORMAT, "words": vpm.words_for_handover(WORDS)}
with open(path, "w", encoding="utf-8") as f:
    json.dump(d, f, ensure_ascii=False)
back = vpm.words_from_handover(json.load(open(path, encoding="utf-8")))
check("every word comes back", len(back) == len(WORDS))
check("with the same times and the same punctuation", back == WORDS,
      str(back[:2]))
check("a handover without words gives an empty list",
      vpm.words_from_handover({"format": vpm.FILE_FORMAT}) == [])
check("and so does a broken row",
      vpm.words_from_handover({"words": [[0.0], None]}) == [])
check("the handover takes the words as a parameter",
      "words" in vpm.write_handover.__code__.co_varnames)

print("\n4. Reading what a recogniser wrote")
tsv = os.path.join(folder, "words.tsv")
with open(tsv, "w", encoding="utf-8") as f:
    f.write("1.500\t1.800\t ist\n0.000\t0.500\tGuten\n"
            "-1\t-1\tohne\n\nrubbish\n")
rows = vpm.read_word_tsv(tsv)
check("the leading space of a word goes",
      [w["word"] for w in rows] == ["Guten", "ist"], str(rows))
check("and the words come back in time order",
      [w["start"] for w in rows] == [0.0, 1.5])
speech = os.path.join(folder, "speech.json")
with open(speech, "w", encoding="utf-8") as f:
    json.dump([{"speaker": "A", "text": "Guten Tag,",
                "timestamps": [["Guten", 0.0, 0.5, 0.9],
                               ["Tag,", 0.5, 1.1, 0.9]]}], f)
check("the word times from auphonic.com are read",
      vpm.read_speech_json(speech) == WORDS[:2],
      str(vpm.read_speech_json(speech)))
check("read_words takes the json way for a json file",
      vpm.read_words(speech) == WORDS[:2])
check("and the tab separated way for the rest",
      vpm.read_words(tsv) == rows)

print("\n5. The correction each recogniser gets on its own")
check("Whisper pulls the start forward and lets the end run",
      vpm.WHISPER_START_S == -0.090 and vpm.WHISPER_END_S == 0.060,
      "%s %s" % (vpm.WHISPER_START_S, vpm.WHISPER_END_S))
check("macOS gets none: its scatter is wider than its offset",
      vpm.MACOS_START_S == 0.0 and vpm.MACOS_END_S == 0.0)
moved = vpm.corrected_words(WORDS[:1], vpm.WHISPER_START_S,
                            vpm.WHISPER_END_S)
check("the two edges move apart, not together",
      moved[0]["start"] == 0.0 and moved[0]["end"] == 0.56, str(moved))
check("nothing lands before the recording began",
      vpm.corrected_words(WORDS[1:2], -10.0, -10.0)[0]["start"] == 0.0)
check("and no word ends before it begins",
      vpm.corrected_words(WORDS[1:2], 0.0, -10.0)[0]["end"] == 0.5)
check("no correction, no change",
      vpm.corrected_words(WORDS, 0, 0) == WORDS)

print("\n6. What Whisper is asked for")
seen = {}


class FakeModel(object):
    def __init__(self, name, device=None, compute_type=None):
        seen["model"] = name
        seen["device"] = device
        seen["arithmetic"] = compute_type

    def transcribe(self, path, **rest):
        seen.update(rest)
        word = types.SimpleNamespace(start=1.0, end=1.4, word=" Tag,")
        return [types.SimpleNamespace(words=[word])], None


fake = types.ModuleType("faster_whisper")
fake.WhisperModel = FakeModel
sys.modules["faster_whisper"] = fake
out = vpm.whisper_words("/nowhere.wav", "de-DE")
check("the model is large-v3-turbo", seen.get("model") == "large-v3-turbo",
      str(seen.get("model")))
check("the voice activity filter is on", seen.get("vad_filter") is True)
check("the word times are asked for",
      seen.get("word_timestamps") is True)
check("the language goes in without the country",
      seen.get("language") == "de", str(seen.get("language")))
check("the words come back with Whisper's own correction",
      out == [vpm.speech_word(0.91, 1.46, "Tag,")], str(out))
want = "float32" if (sys.platform == "darwin"
                     and vpm.platform.machine() == "arm64") else "int8"
check("the arithmetic fits the machine: %s" % want,
      seen.get("arithmetic") == want, str(seen.get("arithmetic")))
del sys.modules["faster_whisper"]

print("\n7. Certificates")
bundle = vpm.certificate_file()
check("a certificate bundle is found", bool(bundle), str(bundle))
if bundle:
    context = vpm.https_context()
    check("and the context has certificates in it",
          context.cert_store_stats()["x509_ca"] > 0,
          str(context.cert_store_stats()))
    check("the libraries that fetch on their own are pointed at it",
          vpm.use_certificates() == bundle
          and os.environ.get("SSL_CERT_FILE") == bundle)

print("\n8. The recognition macOS brings with it")
if not vpm.macos_recognition_ready():
    print("  no recogniser on this machine -- the rest is for macOS 26")
else:
    program = vpm.recogniser_program()
    check("the recogniser is built and kept", bool(program), str(program))
    check("built again it is the same file",
          vpm.recogniser_program() == program)
    spoken = os.path.join(folder, "spoken.aiff")
    said = subprocess.run(
        ["say", "-v", "Anna", "-o", spoken,
         "Guten Tag, das ist ein Versuch."],
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    if said.returncode != 0 or not os.path.exists(spoken):
        print("  no German voice installed -- nothing to recognise")
    else:
        words, way = vpm.recognise_speech(spoken, "de")
        check("the way it took is the one macOS brings", way == "macOS")
        check("it heard the sentence", len(words or []) >= 5,
              str([w["word"] for w in (words or [])]))
        check("every word has a time inside the file",
              all(0 <= w["start"] <= w["end"] for w in words or []))
        check("the punctuation comes with it",
              len(vpm.sentence_end_times(words)) == 1,
              str(vpm.sentence_end_times(words)))
        check("and the comma too",
              len(vpm.clause_break_times(words)) == 1)

print("\n%d checks, %d failed" % (checked[0], len(error)))
sys.exit(1 if error else 0)
