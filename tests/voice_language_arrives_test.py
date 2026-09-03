# -*- coding: utf-8 -*-
"""The language asked for reaches the recognition as a code it takes.

The Language field and --speech-language carry the three-letter tag
ffmpeg wants on the written audio track; both recognisers want the two
letters. Sections: the list the field offers and the code each tag
becomes, then the door into the recognition macOS brings with it, then
the door into faster-whisper.

Neither recogniser runs. Both are stood in for by something stricter
than the original: the stand-in refuses a code that is not in the table
written down here, where the macOS one looks the locale up, finds
nothing and falls back to the system without a word -- which is the
fault this is about. What faster-whisper does with a code it does not
know is read from its source, not measured: the package is not on this
machine.
"""
import os
HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = os.environ.get("VPM_SCRIPT") or os.path.join(
    os.path.dirname(HERE), "videopodcast_magic.py")
import importlib.util
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


vpm.set_language("en")

# What the field offers, and the code the recognition has to be handed
# for it. Written out rather than read out of the program: a table
# taken from the program would only agree with itself. It is also what
# the stand-ins accept, so a language added to the field without a code
# behind it cannot slip through here unnoticed.
WANTED = {
    "ger": "de", "eng": "en", "fra": "fr", "spa": "es", "ita": "it",
    "nld": "nl", "por": "pt", "pol": "pl", "rus": "ru", "swe": "sv",
    "dan": "da", "nor": "no", "fin": "fi", "ces": "cs", "tur": "tr",
    "ell": "el", "hun": "hu", "ron": "ro", "ukr": "uk", "cat": "ca",
    "ara": "ar", "heb": "he", "jpn": "ja", "zho": "zh", "kor": "ko",
}
TAKEN = set(WANTED.values())

# A tag that stands for no language at all, in the three-letter shape
# the field uses -- so what happens to it says something about the
# conversion and not about its length.
UNKNOWN = "qqq"

folder = tempfile.mkdtemp(prefix="vpm_language_")
audio = os.path.join(folder, "mix_full.wav")
open(audio, "wb").close()


#--------------------------------------------------- The macOS door

class Ran(object):
    """What subprocess.run gives back: the two fields macos_words reads."""

    def __init__(self, returncode, stdout):
        self.returncode = returncode
        self.stdout = stdout


class MacDoor(object):
    """Stand in for subprocess, and for the Swift recogniser behind it.

    Stricter than the real one on purpose. The Swift program looks the
    wanted locale up in supportedLocales and falls back to the current
    locale when nothing matches, so a code it cannot use disappears
    without a word. This one refuses it with a return code, and
    macos_words then comes back with nothing at all.

    An empty wish is not a refusal: the Swift program takes it as "work
    it out yourself", and so does this.
    """

    PIPE = subprocess.PIPE
    STDOUT = subprocess.STDOUT

    def __init__(self):
        self.asked = []

    def run(self, cmd, **_ignored):
        self.asked.append(list(cmd))
        if len(cmd) < 4:
            return Ran(2, b"ERR arguments")
        want = cmd[3]
        if want and want not in TAKEN:
            return Ran(1, ("ERR no locale for %s" % want).encode("utf-8"))
        with open(cmd[2], "w", encoding="utf-8") as f:
            f.write("0.000\t0.400\tHallo\n0.400\t0.900\tWelt.\n")
        return Ran(0, b"")


def heard_by_macos(tag):
    """Run macos_words against the stand-in; return (words, the calls)."""
    door = MacDoor()
    was_program, was_subprocess = vpm.recogniser_program, vpm.subprocess
    vpm.recogniser_program = lambda *a, **k: os.path.join(folder, "recog")
    vpm.subprocess = door
    try:
        words = vpm.macos_words(audio, tag)
    finally:
        vpm.recogniser_program = was_program
        vpm.subprocess = was_subprocess
    return words, door.asked


#--------------------------------------------- The faster-whisper door

class Word(object):
    """One word the way faster-whisper hands it out."""

    def __init__(self, start, end, word):
        self.start, self.end, self.word = start, end, word


class Piece(object):
    """One segment; its words are there because they were asked for."""

    def __init__(self, words):
        self.words = words


class WhisperDoor(object):
    """Stand in for faster_whisper.WhisperModel.

    transcribe refuses a language it does not know, as faster-whisper
    does -- that is read from its source, not measured here, because
    the package is not installed on this machine. The list it knows is
    longer than the one this refuses down to; this one takes only what
    the field offers, so a language added there without a code cannot
    pass unnoticed.

    None is not a refusal: it is how faster-whisper is told to work the
    language out itself.
    """

    asked = []

    def __init__(self, name, device=None, compute_type=None):
        self.name = name

    def transcribe(self, path, language=None, **_ignored):
        WhisperDoor.asked.append(language)
        if language is not None and language not in TAKEN:
            raise ValueError("invalid language %r" % language)
        return iter([Piece([Word(0.0, 0.4, "Hallo"),
                            Word(0.4, 0.9, "Welt.")])]), None


def heard_by_whisper(tag):
    """Run whisper_words against the stand-in; return (words, the calls)."""
    WhisperDoor.asked = []
    module = types.ModuleType("faster_whisper")
    module.WhisperModel = WhisperDoor
    was_module = sys.modules.get("faster_whisper")
    was_certificates = vpm.use_certificates
    sys.modules["faster_whisper"] = module
    # The real one installs certifi where there is none, and a test
    # fetches nothing.
    vpm.use_certificates = lambda: None
    try:
        words = vpm.whisper_words(audio, tag, install=False)
    finally:
        vpm.use_certificates = was_certificates
        if was_module is None:
            del sys.modules["faster_whisper"]
        else:
            sys.modules["faster_whisper"] = was_module
    return words, list(WhisperDoor.asked)


print("1. The list the field offers, and the code each tag becomes")

offered = [tag for tag, _name in vpm.spoken_language_choices()]
missing = sorted(set(WANTED) - set(offered))
added = sorted(set(offered) - set(WANTED))
check("the field offers exactly the languages written down here",
      not missing and not added,
      "%d offered against %d here, gone: %s, new: %s"
      % (len(offered), len(WANTED), missing[:3], added[:3]))

wrong = ["%s -> %r, wanted %r" % (tag, vpm.speech_locale(tag), WANTED[tag])
         for tag in sorted(set(offered) & set(WANTED))
         if vpm.speech_locale(tag) != WANTED[tag]]
check("every language the field offers becomes a two-letter code",
      not wrong, "%d of %d wrong: %s"
      % (len(wrong), len(set(offered) & set(WANTED)), wrong[:3]))

check("a tag with padding or capitals still converts",
      vpm.speech_locale("  GER  ") == "de",
      "'  GER  ' -> %r, wanted 'de'" % vpm.speech_locale("  GER  "))


print("\n2. The door into the recognition macOS brings with it")

_words, calls = heard_by_macos("ger")
check("the macOS door is reached and the call recorded",
      len(calls) == 1 and len(calls[0]) == 4 and calls[0][1] == audio,
      "%d calls, first %s" % (len(calls), (calls[0] if calls else [])[:4]))

handed, empty = {}, []
for tag in sorted(set(offered) & set(WANTED)):
    words, calls = heard_by_macos(tag)
    handed[tag] = calls[0][3] if calls else None
    if words is None:
        empty.append(tag)
wrong = ["%s -> %r, wanted %r" % (tag, handed[tag], WANTED[tag])
         for tag in sorted(handed) if handed[tag] != WANTED[tag]]
check("the macOS recogniser is handed the code, not the tag",
      not wrong, "%d of %d wrong: %s" % (len(wrong), len(handed), wrong[:3]))
check("the macOS way brings words back for every language offered",
      not empty, "%d of %d came back with nothing: %s"
      % (len(empty), len(handed), empty[:3]))

_words, calls = heard_by_macos("")
check("not set reaches the macOS recogniser as nothing",
      bool(calls) and calls[0][3] == "",
      "asked '' -> %r, wanted ''" % (calls[0][3] if calls else None))

_words, calls = heard_by_macos("de")
check("a two-letter code reaches the macOS recogniser unchanged",
      bool(calls) and calls[0][3] == "de",
      "asked 'de' -> %r, wanted 'de'" % (calls[0][3] if calls else None))

_words, calls = heard_by_macos(UNKNOWN)
check("an unknown tag reaches the macOS recogniser as it stands",
      bool(calls) and calls[0][3] == UNKNOWN,
      "asked %r -> %r, wanted %r"
      % (UNKNOWN, (calls[0][3] if calls else None), UNKNOWN))


print("\n3. The door into faster-whisper")

_words, calls = heard_by_whisper("ger")
check("the faster-whisper door is reached and the call recorded",
      len(calls) == 1, "%d calls, first %r"
      % (len(calls), calls[0] if calls else None))

handed, empty = {}, []
for tag in sorted(set(offered) & set(WANTED)):
    words, calls = heard_by_whisper(tag)
    handed[tag] = calls[0] if calls else None
    if not words:
        empty.append(tag)
wrong = ["%s -> %r, wanted %r" % (tag, handed[tag], WANTED[tag])
         for tag in sorted(handed) if handed[tag] != WANTED[tag]]
check("faster-whisper is handed the code, not the tag",
      not wrong, "%d of %d wrong: %s" % (len(wrong), len(handed), wrong[:3]))
check("faster-whisper brings words back for every language offered",
      not empty, "%d of %d came back with nothing: %s"
      % (len(empty), len(handed), empty[:3]))

_words, calls = heard_by_whisper("")
check("not set reaches faster-whisper as no language at all",
      bool(calls) and calls[0] is None,
      "asked '' -> %r, wanted None" % (calls[0] if calls else "no call"))

_words, calls = heard_by_whisper("de")
check("a two-letter code reaches faster-whisper unchanged",
      bool(calls) and calls[0] == "de",
      "asked 'de' -> %r, wanted 'de'" % (calls[0] if calls else "no call"))

_words, calls = heard_by_whisper(UNKNOWN)
check("an unknown tag reaches faster-whisper as it stands",
      bool(calls) and calls[0] == UNKNOWN,
      "asked %r -> %r, wanted %r"
      % (UNKNOWN, (calls[0] if calls else "no call"), UNKNOWN))


try:
    os.unlink(audio)
    os.rmdir(folder)
except OSError:
    pass

print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
