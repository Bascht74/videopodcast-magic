# -*- coding: utf-8 -*-
"""The words on the speakers, and the three files that come of it.

The rule is measured, so the measured rule stands here: a word goes to
whoever covers most of it, a word in a gap to the nearest voice, and a
sentence agrees on one voice while the others hold under a fifth of
it. The three files are the ones auphonic.com delivers, so our json
goes through their reader and back against the words that went in.
"""
import os
HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = os.environ.get("VPM_SCRIPT") or os.path.join(
    os.path.dirname(HERE), "videopodcast-magic.py")
import importlib.util
import json
import shutil
import sys
import tempfile
import time
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


def words(*rows):
    return [vpm.speech_word(*r) for r in rows]


SEGMENTS = [("Anna", [(0.0, 3.1), (9.0, 9.6)]),
            ("Bert", [(3.15, 4.5)])]

print("1. A word goes to whoever covers most of it")
SAID = words((0.0, 0.5, "Guten"), (0.5, 1.1, "Tag,"), (1.1, 1.3, "das"),
             (1.3, 1.8, "ist"), (1.8, 2.6, "ein"), (2.6, 3.0, "Versuch."),
             (3.2, 3.6, "Und"), (3.6, 4.4, "weiter."),
             (9.0, 9.4, "Danke."))
tally = {}
put = vpm.words_by_speaker(SAID, SEGMENTS, tally)
check("every word carries a name",
      all(w.get("speaker") for w in put),
      "%d of %d words named"
      % (len([w for w in put if w.get("speaker")]), len(put)))
first_six = [w["speaker"] for w in put[:6]]
check("the first sentence is Anna's",
      first_six == ["Anna"] * 6,
      "%s against six times Anna" % (first_six,))
next_two = [w["speaker"] for w in put[6:8]]
check("the second is Bert's",
      next_two == ["Bert"] * 2,
      "%s against two times Bert" % (next_two,))
check("all nine words touch exactly one voice",
      (tally["clear"], tally["shared"], tally["gap"]) == (9, 0, 0),
      str(tally))

print("\n2. Where two voices touch the same word, the longer one wins")
OVER = words((3.0, 3.4, "kurz"))
put = vpm.words_by_speaker(OVER, SEGMENTS, tally)
check("0.1 s of Anna against 0.25 s of Bert goes to Bert",
      put[0]["speaker"] == "Bert", put[0].get("speaker"))
check("and it is counted as shared",
      (tally["clear"], tally["shared"], tally["gap"]) == (0, 1, 0),
      str(tally))

print("\n3. A word in a gap goes to the nearest voice")
tally = {}
put = vpm.words_by_speaker(words((6.0, 6.2, "hm")), SEGMENTS, tally)
check("1.5 s to Bert beats 2.8 s to Anna", put[0]["speaker"] == "Bert",
      put[0].get("speaker"))
check("and it is counted as a gap", tally["gap"] == 1, str(tally))
put = vpm.words_by_speaker(words((20.0, 20.2, "so")), SEGMENTS)
check("behind everything the last voice takes it",
      put[0]["speaker"] == "Anna", put[0].get("speaker"))

print("\n4. The majority of a sentence, and its limit")
# One voice in six holds a sixth, under the fifth, so the sentence
# agrees on the majority.
MIXED = words((0.0, 0.4, "Eins"), (0.4, 0.8, "zwei"), (0.8, 1.2, "drei"),
              (1.2, 1.6, "vier"), (1.6, 2.0, "fuenf"),
              (2.0, 2.4, "sechs."))
for i, w in enumerate(MIXED):
    w["speaker"] = "Bert" if i == 2 else "Anna"
after = vpm.sentence_speakers(MIXED)
voices = [w["speaker"] for w in after]
check("one voice in six is outvoted",
      voices == ["Anna"] * 6,
      "%s against six times Anna" % (voices,))
for i, w in enumerate(MIXED):
    w["speaker"] = "Bert" if i >= 4 else "Anna"
after = vpm.sentence_speakers(MIXED)
voices = [w["speaker"] for w in after]
check("two in six are not -- the words stand",
      voices == ["Anna", "Anna", "Anna", "Anna", "Bert", "Bert"],
      "%s against four times Anna and two times Bert" % (voices,))
check("the limit is the measured fifth",
      abs(vpm.SENTENCE_MINORITY_SHARE - 0.2) < 1e-9,
      str(vpm.SENTENCE_MINORITY_SHARE))

print("\n5. Without a separation nobody is named")
put = vpm.words_with_speakers(SAID, [])
check("no word gets a name", not any(w.get("speaker") for w in put),
      "%d of %d words named, wanted none"
      % (len([w for w in put if w.get("speaker")]), len(put)))
nameless = vpm.transcript_file_text(put)
check("and the reading file has no colon in it",
      ":" not in nameless,
      "%d colons in %d characters, beginning %s"
      % (nameless.count(":"), len(nameless), repr(nameless[:40])))

print("\n6. The three files, and the json round trip")
folder = tempfile.mkdtemp(prefix="vpm-transcript-")
try:
    written = vpm.write_transcript_files(folder, "Episode", SAID, SEGMENTS)
    check("three files are written", len(written) == 3, str(written))
    check("they are named like the ones auphonic.com delivers",
          [os.path.basename(p) for p in written]
          == ["Episode.json", "Episode.srt", "Episode.txt"],
          str([os.path.basename(p) for p in written]))
    check("all three really exist",
          all(os.path.exists(p) and os.path.getsize(p) for p in written),
          "sizes in bytes %s, -1 where the file is missing"
          % ([os.path.getsize(p) if os.path.exists(p) else -1
              for p in written],))

    with open(written[0], encoding="utf-8") as f:
        passages = json.load(f)
    check("the json is a list of passages", isinstance(passages, list),
          "a %s: %.50s" % (type(passages).__name__, passages))
    check("each passage carries its speaker",
          [p.get("speaker") for p in passages] == ["Anna", "Bert", "Anna"],
          str([p.get("speaker") for p in passages]))
    check("and its running text",
          passages[0].get("text") == "Guten Tag, das ist ein Versuch.",
          str(passages[0].get("text")))
    back = vpm.read_speech_json(written[0])
    check("the reader for auphonic.com reads our own json",
          [(w["start"], w["end"], w["word"]) for w in back]
          == [(w["start"], w["end"], w["word"]) for w in SAID],
          "%d words back" % len(back))

    srt = open(written[1], encoding="utf-8").read()
    check("the subtitles are numbered from one",
          srt.startswith("1\n00:00:00,000 --> 00:00:03,000\n"), repr(srt[:40]))
    check("the name stands in capitals with a colon",
          "ANNA: Guten Tag" in srt,
          "'ANNA: Guten Tag' %d x, the file begins %s"
          % (srt.count("ANNA: Guten Tag"), repr(srt[:64])))
    check("and only where the voice changes",
          srt.count("ANNA:") == 2 and srt.count("BERT:") == 1,
          "%d/%d" % (srt.count("ANNA:"), srt.count("BERT:")))
    check("no subtitle line is longer than the guide allows",
          all(len(line) <= vpm.SUBTITLE_LINE_CHARS
              for line in srt.splitlines() if "-->" not in line),
          str(max([len(x) for x in srt.splitlines()] or [0])))

    text = open(written[2], encoding="utf-8").read()
    check("the reading file names the voices",
          text.startswith("Anna: Guten Tag"), repr(text[:20]))
    check("it shows the change of voice as a paragraph",
          "\n\nBert: Und weiter." in text,
          "%d blank lines, the file reads %s"
          % (text.count("\n\n"), repr(text[:90])))
    check("and carries no times", "-->" not in text and "00:00" not in text,
          "%d arrows and %d clock stamps in %d characters"
          % (text.count("-->"), text.count("00:00"), len(text)))
finally:
    shutil.rmtree(folder, ignore_errors=True)

print("\n7. A long turn is cut into readable subtitles")
long_words = words(*[(i * 0.4, i * 0.4 + 0.35, "Wort%d" % i)
                     for i in range(60)])
cues = vpm.subtitle_cues(vpm.words_by_speaker(
    long_words, [("Anna", [(0.0, 30.0)])]))
check("no subtitle stands longer than seven seconds",
      all(b - a <= vpm.SUBTITLE_LONGEST_S + 1e-6 for a, b, _n, _t in cues),
      str(max((b - a for a, b, _n, _t in cues), default=0)))
check("and none holds more than two lines' worth",
      all(len(t) <= vpm.SUBTITLE_LINE_CHARS * vpm.SUBTITLE_LINES
          for _a, _b, _n, t in cues),
      str(max((len(t) for _a, _b, _n, t in cues), default=0)))
in_cues = " ".join(t for _a, _b, _n, t in cues)
went_in = " ".join(w["word"] for w in long_words)
check("every word is in exactly one subtitle", in_cues == went_in,
      "%d words over %d subtitles against %d words in"
      % (len(in_cues.split()), len(cues), len(went_in.split())))

print("\n8. Nothing in, nothing written")
folder = tempfile.mkdtemp(prefix="vpm-transcript-")
try:
    made = vpm.write_transcript_files(folder, "Leer", [], SEGMENTS)
    left = os.listdir(folder)
    check("no words means no files", made == [] and not left,
          "%d files reported and %d left in the folder %s, wanted none"
          % (len(made), len(left), left))
finally:
    shutil.rmtree(folder, ignore_errors=True)

print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
