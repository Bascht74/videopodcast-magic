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
spec = importlib.util.spec_from_file_location("vpm", SCRIPT)
vpm = importlib.util.module_from_spec(spec); sys.modules["vpm"] = vpm
spec.loader.exec_module(vpm)

error = []
checked = [0]


def check(name, ok, extra=""):
    checked[0] += 1
    print("  %-56s %s %s" % (name, "ok" if ok else "FAIL", extra))
    if not ok:
        error.append(name)


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
      all(w.get("speaker") for w in put))
check("the first sentence is Anna's",
      [w["speaker"] for w in put[:6]] == ["Anna"] * 6)
check("the second is Bert's",
      [w["speaker"] for w in put[6:8]] == ["Bert"] * 2)
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
check("one voice in six is outvoted",
      [w["speaker"] for w in after] == ["Anna"] * 6)
for i, w in enumerate(MIXED):
    w["speaker"] = "Bert" if i >= 4 else "Anna"
after = vpm.sentence_speakers(MIXED)
check("two in six are not -- the words stand",
      [w["speaker"] for w in after]
      == ["Anna", "Anna", "Anna", "Anna", "Bert", "Bert"])
check("the limit is the measured fifth",
      abs(vpm.SENTENCE_MINORITY_SHARE - 0.2) < 1e-9,
      str(vpm.SENTENCE_MINORITY_SHARE))

print("\n5. Without a separation nobody is named")
put = vpm.words_with_speakers(SAID, [])
check("no word gets a name", not any(w.get("speaker") for w in put))
check("and the reading file has no colon in it",
      ":" not in vpm.transcript_file_text(put))

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
          all(os.path.exists(p) and os.path.getsize(p) for p in written))

    with open(written[0], encoding="utf-8") as f:
        passages = json.load(f)
    check("the json is a list of passages", isinstance(passages, list))
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
          "ANNA: Guten Tag" in srt)
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
          "\n\nBert: Und weiter." in text)
    check("and carries no times", "-->" not in text and "00:00" not in text)
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
check("every word is in exactly one subtitle",
      " ".join(t for _a, _b, _n, t in cues)
      == " ".join(w["word"] for w in long_words))

print("\n8. Nothing in, nothing written")
folder = tempfile.mkdtemp(prefix="vpm-transcript-")
try:
    check("no words means no files",
          vpm.write_transcript_files(folder, "Leer", [], SEGMENTS) == []
          and not os.listdir(folder))
finally:
    shutil.rmtree(folder, ignore_errors=True)

print("\n%d checks, %d failed" % (checked[0], len(error)))
sys.exit(1 if error else 0)
