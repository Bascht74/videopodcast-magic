# -*- coding: utf-8 -*-
"""Speech recognition: the words, their times and their punctuation.

What is checked: that punctuation is read the same way every time,
because the cut hangs on sentence ends and clause boundaries; that the
words survive the handover file unchanged; that each recogniser keeps
its own measured rules -- the filter without which Whisper writes words
into silence, and a correction of its own; and that the bundle a model
download is verified against reaches the connection.
"""
import os
HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = os.environ.get("VPM_SCRIPT") or os.path.join(
    os.path.dirname(HERE), "videopodcast_magic.py")
import importlib.util
import json
import subprocess
import sys
import tempfile
import time
import types
spec = importlib.util.spec_from_file_location("vpm", SCRIPT)
vpm = importlib.util.module_from_spec(spec); sys.modules["vpm"] = vpm
spec.loader.exec_module(vpm)

began = time.time()
done = 0
bad = []


def check(name, ok, extra=""):
    global done
    done += 1
    print("  %-58s %s %s" % (name, "ok" if ok else "FAIL", extra))
    if not ok:
        bad.append("%s [%s]" % (name, extra or "no numbers"))


print("1. What a word closes")
mark = vpm.word_mark("Versuch.")
check("a full stop ends a sentence", mark == "sentence",
      "'Versuch.' gave %r, wanted 'sentence'" % (mark,))
mark = vpm.word_mark("Erkennung?")
check("so does a question mark", mark == "sentence",
      "'Erkennung?' gave %r, wanted 'sentence'" % (mark,))
mark = vpm.word_mark("Halt!")
check("and an exclamation mark", mark == "sentence",
      "'Halt!' gave %r, wanted 'sentence'" % (mark,))
mark = vpm.word_mark("also...")
check("three dots as well", mark == "sentence",
      "'also...' gave %r, wanted 'sentence'" % (mark,))
mark = vpm.word_mark("Tag,")
check("a comma breaks a clause", mark == "clause",
      "'Tag,' gave %r, wanted 'clause'" % (mark,))
mark = vpm.word_mark('"fertig."')
check("a mark inside a closing quote still counts", mark == "sentence",
      "a full stop inside straight quotes gave %r, wanted 'sentence'"
      % (mark,))
mark = vpm.word_mark("»fertig.«")
check("and inside a German one too", mark == "sentence",
      "a full stop inside German quotes gave %r, wanted 'sentence'"
      % (mark,))
mark = vpm.word_mark("Tag")
check("a plain word closes nothing", mark == "",
      "'Tag' gave %r, wanted the empty string" % (mark,))
mark = vpm.word_mark("Video-")
check("a compound hyphen is not a boundary", mark == "",
      "'Video-' gave %r, wanted the empty string" % (mark,))
mark = vpm.word_mark("")
check("nothing at all is nothing", mark == "",
      "the empty word gave %r, wanted the empty string" % (mark,))

print("\n2. Sentences and clauses out of the words")
WORDS = [vpm.speech_word(*w) for w in (
    (0.0, 0.5, "Guten"), (0.5, 1.1, "Tag,"), (1.1, 1.3, "das"),
    (1.3, 1.8, "ist"), (1.8, 2.6, "ein"), (2.6, 3.0, "Versuch."),
    (3.0, 3.6, "Und"), (3.6, 4.4, "weiter"))]
ends = vpm.sentence_end_times(WORDS)
check("the sentence ends are the times of the marks", ends == [3.0],
      "%s over 8 words, wanted [3.0]" % (ends,))
breaks = vpm.clause_break_times(WORDS)
check("the clause boundaries as well", breaks == [1.1],
      "%s over 8 words, wanted [1.1]" % (breaks,))
starts = vpm.sentence_start_times(WORDS)
check("a sentence starts at its first word", starts == [0.0, 3.0],
      "%s, wanted [0.0, 3.0]" % (starts,))
groups = vpm.sentences_of(WORDS)
check("the unclosed tail is a sentence too", len(groups) == 2,
      "%d sentences out of 8 words, wanted 2: %s"
      % (len(groups), [[w["word"] for w in g] for g in groups]))
tail = [w["word"] for w in (groups[1] if len(groups) > 1 else [])]
check("and it keeps its words", tail == ["Und", "weiter"],
      "the second sentence holds %r, wanted ['Und', 'weiter']" % (tail,))
check("no words, no boundaries",
      vpm.sentence_end_times([]) == [] and vpm.sentences_of([]) == [],
      "sentence_end_times([]) gave %r and sentences_of([]) gave %r, "
      "both wanted []"
      % (vpm.sentence_end_times([]), vpm.sentences_of([])))

print("\n3. Through the handover file and back")
folder = tempfile.mkdtemp(prefix="vpm_speech_")
path = os.path.join(folder, "handover.json")
d = {"format": vpm.FILE_FORMAT, "words": vpm.words_for_handover(WORDS)}
with open(path, "w", encoding="utf-8") as f:
    json.dump(d, f, ensure_ascii=False)
back = vpm.words_from_handover(json.load(open(path, encoding="utf-8")))
check("every word comes back", len(back) == len(WORDS),
      "%d words read back out of %d written" % (len(back), len(WORDS)))
differ = [(i, back[i], WORDS[i])
          for i in range(min(len(back), len(WORDS))) if back[i] != WORDS[i]]
check("with the same times and the same punctuation", back == WORDS,
      "%d of %d rows differ%s"
      % (len(differ), len(WORDS),
         (", first row %d read back as %r, written as %r" % differ[0])
         if differ else ""))
empty = vpm.words_from_handover({"format": vpm.FILE_FORMAT})
check("a handover without words gives an empty list", empty == [],
      "a file with no words key gave %r, wanted []" % (empty,))
broken = vpm.words_from_handover({"words": [[0.0], None]})
check("and so does a broken row",
      broken == [],
      "the rows [[0.0], None] gave %r, wanted []" % (broken,))
names = list(vpm.write_handover.__code__.co_varnames[
    :vpm.write_handover.__code__.co_argcount])
check("the handover takes the words as a parameter", "words" in names,
      "'words' wanted among the %d parameters of write_handover: %s"
      % (len(names), names))

print("\n4. Reading what a recogniser wrote")
tsv = os.path.join(folder, "words.tsv")
with open(tsv, "w", encoding="utf-8") as f:
    f.write("1.500\t1.800\t ist\n0.000\t0.500\tGuten\n"
            "-1\t-1\tohne\n\nrubbish\n")
rows = vpm.read_word_tsv(tsv)
check("the leading space of a word goes",
      [w["word"] for w in rows] == ["Guten", "ist"],
      "5 lines gave %r, wanted ['Guten', 'ist']"
      % ([w["word"] for w in rows],))
check("and the words come back in time order",
      [w["start"] for w in rows] == [0.0, 1.5],
      "the starts came out %s, wanted [0.0, 1.5]"
      % ([w["start"] for w in rows],))
speech = os.path.join(folder, "speech.json")
with open(speech, "w", encoding="utf-8") as f:
    json.dump([{"speaker": "A", "text": "Guten Tag,",
                "timestamps": [["Guten", 0.0, 0.5, 0.9],
                               ["Tag,", 0.5, 1.1, 0.9]]}], f)
heard = vpm.read_speech_json(speech)
check("the word times from auphonic.com are read", heard == WORDS[:2],
      "%d words %s, wanted %s" % (len(heard), heard, WORDS[:2]))
by_name = vpm.read_words(speech)
check("read_words takes the json way for a json file",
      by_name == WORDS[:2],
      "the .json file gave %d words %s, wanted %s"
      % (len(by_name), by_name, WORDS[:2]))
by_tab = vpm.read_words(tsv)
check("and the tab separated way for the rest", by_tab == rows,
      "the .tsv file gave %d words %s, wanted the %d of read_word_tsv %s"
      % (len(by_tab), by_tab, len(rows), rows))

print("\n5. The correction each recogniser gets on its own")
check("Whisper pulls the start forward and lets the end run",
      vpm.WHISPER_START_S == -0.090 and vpm.WHISPER_END_S == 0.060,
      "start %s end %s, wanted -0.09 and 0.06"
      % (vpm.WHISPER_START_S, vpm.WHISPER_END_S))
check("macOS gets none: its scatter is wider than its offset",
      vpm.MACOS_START_S == 0.0 and vpm.MACOS_END_S == 0.0,
      "start %s end %s, wanted 0.0 and 0.0"
      % (vpm.MACOS_START_S, vpm.MACOS_END_S))
moved = vpm.corrected_words(WORDS[:1], vpm.WHISPER_START_S,
                            vpm.WHISPER_END_S)
moved_start = moved[0]["start"] if moved else None
moved_end = moved[0]["end"] if moved else None
check("the two edges move apart, not together",
      moved_start == 0.0 and moved_end == 0.56,
      "the word 0.0-0.5 became %s-%s, wanted 0.0-0.56"
      % (moved_start, moved_end))
floored = vpm.corrected_words(WORDS[1:2], -10.0, -10.0)
floored_start = floored[0]["start"] if floored else None
check("nothing lands before the recording began", floored_start == 0.0,
      "the start 0.5 shifted by -10.0 s gave %s, wanted 0.0"
      % (floored_start,))
squeezed = vpm.corrected_words(WORDS[1:2], 0.0, -10.0)
squeezed_end = squeezed[0]["end"] if squeezed else None
check("and no word ends before it begins", squeezed_end == 0.5,
      "the word 0.5-1.1 with the end shifted by -10.0 s ends at %s, "
      "wanted its own start 0.5" % (squeezed_end,))
unmoved = vpm.corrected_words(WORDS, 0, 0)
changed = [(a, b) for a, b in zip(unmoved, WORDS) if a != b]
check("no correction, no change", unmoved == WORDS,
      "a correction of 0/0 gave %d words out of %d, %d of them changed%s"
      % (len(unmoved), len(WORDS), len(changed),
         (", first %r against %r" % changed[0]) if changed else ""))

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
      "the model asked for was %r, wanted 'large-v3-turbo'"
      % (seen.get("model"),))
check("the voice activity filter is on", seen.get("vad_filter") is True,
      "vad_filter went in as %r, wanted True" % (seen.get("vad_filter"),))
check("the word times are asked for",
      seen.get("word_timestamps") is True,
      "word_timestamps went in as %r, wanted True"
      % (seen.get("word_timestamps"),))
check("the language goes in without the country",
      seen.get("language") == "de",
      "'de-DE' went in and %r came out, wanted 'de'"
      % (seen.get("language"),))
WHISPER_WANT = [vpm.speech_word(0.91, 1.46, "Tag,")]
check("the words come back with Whisper's own correction",
      out == WHISPER_WANT,
      "1.0-1.4 ' Tag,' came back as %s, wanted %s" % (out, WHISPER_WANT))
want = "float32" if (sys.platform == "darwin"
                     and vpm.platform.machine() == "arm64") else "int8"
check("the arithmetic fits the machine: %s" % want,
      seen.get("arithmetic") == want,
      "compute_type went in as %r, wanted %r on %s/%s"
      % (seen.get("arithmetic"), want, sys.platform,
         vpm.platform.machine()))
del sys.modules["faster_whisper"]

print("\n7. Certificates")
bundle = vpm.certificate_file()
check("a certificate bundle is found", bool(bundle),
      "certificate_file() gave %r, wanted a path" % (bundle,))
if bundle:
    # What goes to the context is a bundle written here, three
    # certificates out of the real one and nothing else. Holding the
    # store against the real bundle proves nothing: section 6 put
    # SSL_CERT_FILE into the environment, OpenSSL reads that by itself,
    # and a context that was handed no bundle at all then comes back
    # with exactly the same authorities as one that was handed the file
    # -- 121 of them, measured on 2.9.2026.
    END = "-----END CERTIFICATE-----"
    with open(bundle, encoding="utf-8", errors="replace") as f:
        pems = f.read().split(END)
    # certifi is third-party material, not the program: below three
    # certificates the slice would be short and the count would say
    # nothing. A precondition of the material, hence a bare assert.
    assert len(pems) - 1 >= 3, "the bundle holds %d certificates" % (
        len(pems) - 1,)
    three = os.path.join(folder, "three_certificates.pem")
    with open(three, "w", encoding="utf-8") as f:
        f.write(END.join(pems[:3]) + END + "\n")
    real_certificate_file = vpm.certificate_file
    vpm.certificate_file = lambda: three
    try:
        stats = vpm.https_context().cert_store_stats()
    finally:
        vpm.certificate_file = real_certificate_file
    check("the context is loaded out of the bundle, not the machine",
          stats["x509_ca"] == 3,
          "%d certificate authorities in the store, wanted the 3 in the "
          "bundle handed over; the whole bundle holds %d, the store says %s"
          % (stats["x509_ca"], len(pems) - 1, stats))
    pointed = vpm.use_certificates()
    check("the libraries that fetch on their own are pointed at it",
          pointed == bundle
          and os.environ.get("SSL_CERT_FILE") == bundle,
          "use_certificates() gave %r and SSL_CERT_FILE is %r, "
          "both wanted %r"
          % (pointed, os.environ.get("SSL_CERT_FILE"), bundle))

# The real recogniser runs on a file this test speaks itself, so this
# part needs neither network nor material.
print("\n8. The recognition macOS brings with it")
if not vpm.macos_recognition_ready():
    # run.sh reads a line beginning LEFT OUT, keeps the test green and
    # repeats it, so the section is named instead of the count simply
    # falling short of what a machine with the recogniser reached.
    print("  LEFT OUT: no recogniser on this machine -- "
          "the rest is for macOS 26")
else:
    program = vpm.recogniser_program()
    check("the recogniser is built and kept", bool(program),
          "recogniser_program() gave %r, wanted a path" % (program,))
    again = vpm.recogniser_program()
    check("built again it is the same file", again == program,
          "the second call gave %r, the first %r" % (again, program))
    spoken = os.path.join(folder, "spoken.aiff")
    said = subprocess.run(
        ["say", "-v", "Anna", "-o", spoken,
         "Guten Tag, das ist ein Versuch."],
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    if said.returncode != 0 or not os.path.exists(spoken):
        print("  LEFT OUT: no German voice installed -- "
              "nothing to recognise")
    else:
        words, way = vpm.recognise_speech(spoken, "de")
        check("the way it took is the one macOS brings", way == "macOS",
              "the way was %r, wanted 'macOS'" % (way,))
        said_words = [w["word"] for w in (words or [])]
        check("it heard the sentence", len(words or []) >= 5,
              "%d words out of a sentence of 6, wanted at least 5: %s"
              % (len(said_words), said_words))
        outside = [w for w in (words or [])
                   if not (0 <= w["start"] <= w["end"])]
        check("every word has a time inside the file", not outside,
              "%d of %d words break 0 <= start <= end%s"
              % (len(outside), len(said_words),
                 (", first %r" % (outside[0],)) if outside else ""))
        sentence_ends = vpm.sentence_end_times(words)
        check("the punctuation comes with it", len(sentence_ends) == 1,
              "%d sentence ends %s out of %d words, wanted 1"
              % (len(sentence_ends), sentence_ends, len(said_words)))
        clause_breaks = vpm.clause_break_times(words)
        check("and the comma too", len(clause_breaks) == 1,
              "%d clause breaks %s out of %d words, wanted 1"
              % (len(clause_breaks), clause_breaks, len(said_words)))

print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
