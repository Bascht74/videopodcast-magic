# -*- coding: utf-8 -*-
"""The speech recognition says its amounts the way the language does.

Four sections in the order they come: the words dropped for want of a
time, which take the thousands mark; the shares of the transcript
report, which take the decimal mark; the recognition's own report,
where both marks stand in one line and both languages are asked; and
the seconds a build took. The recogniser and the Swift compiler are
stand-ins in the last two, so nothing real is run and no wording is
held against anything -- what is judged is the shape of the number,
which is why these checks stand whether a catalogue carries the
sentence or not.
"""
import contextlib
import io
import os
import re
import shutil
import sys
import tempfile
import time

import the_program

began = time.time()
vpm = the_program.load()

done = 0
bad = []


def check(name, ok, extra=""):
    global done
    done += 1
    print("  %-58s %s %s" % (name, "ok" if ok else "FAIL", extra))
    if not ok:
        bad.append("%s [%s]" % (name, extra or "no numbers"))


def spoken(work):
    """Run work with the printing caught, and hand back what it said."""
    caught = io.StringIO()
    with contextlib.redirect_stdout(caught):
        work()
    said = caught.getvalue()
    for line in said.splitlines():
        print("      > %s" % line.rstrip())
    return said


def marks(text):
    """The separators the text printed between two digits, in order.

    Read out of the printed line rather than worked out, so the check
    holds no expectation the program could compute the same way. A
    thousands mark and a decimal mark both stand between two digits,
    and the order they come in is the order the number is written.
    """
    return [m.group(1) for m in re.finditer(r"\d([.,])\d", text or "")]


room = tempfile.mkdtemp(prefix="vpm_amounts_")
try:
    print("1. A count of words left out takes the thousands mark")
    # A word without a time is written with -1 and dropped; 1234 of
    # them, so the count is four digits and has a mark to carry. The
    # one good line keeps the reading from being empty.
    tsv = os.path.join(room, "words.tsv")
    with open(tsv, "w", encoding="utf-8") as f:
        f.write("".join("-1\t-1\tw\n" for _ in range(1234)))
        f.write("0.0\t0.1\tx\n")
    vpm.set_language("de")
    said = spoken(lambda: vpm.read_word_tsv(tsv))
    check("the words left out for want of a time carry the German "
          "thousands mark",
          "1.234" in said and "1234" not in said,
          "%r -- wanted %r in it and %r not"
          % (said.strip(), "1.234", "1234"))

    print("\n2. The shares of the transcript report take the decimal mark")
    # A thousand words a tenth of a second apart, and one speaker over
    # the first 25 seconds: 250 words to a voice and 750 in a gap, so
    # the shares are 25.0, 0.0 and 75.0 and none of them is a whole
    # number the decimal mark could hide in.
    words = [{"start": i * 0.1, "end": i * 0.1 + 0.05, "word": "w%d" % i}
             for i in range(1000)]
    segments = [("A", [(0.0, 25.0)])]
    vpm.set_language("de")
    said = spoken(lambda: vpm.write_transcript_files(
        room, "transcript", words, segments))
    check("the shares of the transcript report carry the German "
          "decimal mark",
          "25,0" in said and "25.0" not in said,
          "%r -- wanted %r in it and %r not"
          % (said.strip(), "25,0", "25.0"))

    print("\n3. The recognition's own report writes both marks")
    # The recogniser is a stand-in: it hands back 1234 words and
    # nothing else, so the line the run prints carries a four-digit
    # count and the seconds the run itself took, and no third number
    # from anywhere. It is stricter than the real one -- it cannot
    # answer with a word the real one would not have heard.
    heard = [{"start": i * 0.1, "end": i * 0.1 + 0.05, "word": "w"}
             for i in range(1234)]
    store = os.path.join(room, "store")

    def store_folder(sub=""):
        folder = os.path.join(store, sub)
        os.makedirs(folder, exist_ok=True)
        return folder

    def recognised(lang):
        """One run of the recognition in that language, as it printed it.

        A recording of its own per language, and its content differs
        and not only its name: the store is keyed on what a file holds,
        so two files alike would let the second run read the first
        one's words back and print the other sentence, which carries no
        seconds at all.
        """
        sound = os.path.join(room, "heard_%s.wav" % lang)
        with open(sound, "wb") as f:
            f.write(lang.encode("ascii") * 2048)
        vpm.set_language(lang)
        return spoken(lambda: vpm.words_at_hand(sound, "de-DE"))

    was_cache, was_macos = vpm.cache_folder, vpm.macos_words
    try:
        vpm.cache_folder = store_folder
        vpm.macos_words = lambda path, language="": [dict(w) for w in heard]
        german = recognised("de")
        english = recognised("en")
    finally:
        vpm.cache_folder, vpm.macos_words = was_cache, was_macos
    check("the recognition's report carries the German marks, "
          "thousands then decimal",
          marks(german) == [".", ","],
          "%r reads %s, wanted %s"
          % (german.strip(), marks(german), [".", ","]))
    check("the recognition's report carries the English marks, "
          "thousands then decimal",
          marks(english) == [",", "."],
          "%r reads %s, wanted %s"
          % (english.strip(), marks(english), [",", "."]))

    print("\n4. The seconds a build took take the decimal mark")
    # The compiler is a stand-in that writes the file it was asked for
    # and reports success. It is stricter than the real one: it
    # compiles nothing, so the only thing the run can print about it
    # is the time it waited.

    class Answer(object):
        returncode = 0
        stdout = b"swiftc 6.0"

    def compiler_stand_in(argv, **named):
        if "-o" in argv:
            with open(argv[argv.index("-o") + 1], "wb") as f:
                f.write(b"not really a program")
        return Answer()

    build = os.path.join(room, "build")

    def build_folder(sub=""):
        folder = os.path.join(build, sub)
        os.makedirs(folder, exist_ok=True)
        return folder

    was_cache = vpm.cache_folder
    was_swift, was_run = vpm.swift_compiler, vpm.subprocess.run
    try:
        vpm.cache_folder = build_folder
        vpm.swift_compiler = lambda: os.path.join(room, "swiftc")
        vpm.subprocess.run = compiler_stand_in
        vpm.set_language("de")
        said = spoken(vpm.recogniser_program)
    finally:
        vpm.cache_folder = was_cache
        vpm.swift_compiler, vpm.subprocess.run = was_swift, was_run
    # The line before it says the build has begun and carries no
    # number, so the last line is the one with the seconds in it.
    last = (said.strip().splitlines() or [""])[-1]
    check("the seconds the recogniser took to build carry the German "
          "decimal mark",
          marks(last) == [","],
          "%r reads %s, wanted %s" % (last.strip(), marks(last), [","]))
finally:
    vpm.set_language("en")
    shutil.rmtree(room, ignore_errors=True)

print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
