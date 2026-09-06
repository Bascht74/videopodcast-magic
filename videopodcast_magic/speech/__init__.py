# -*- coding: utf-8 -*-
"""What is said and when, and what is written down from it.

A piece of the program, read in by beside(): it cannot import the file
it was cut out of, so the program is handed in and bound below by name.
"""

# Put here by beside() before this file is read.
PROGRAM = PROGRAM

# What this piece uses out of the program, bound once. Not one is a
# name the program rebinds while it runs, so none has to stay
# PROGRAM.something the way a few of the window's do.
SPEECH_CODES = PROGRAM.SPEECH_CODES
T = PROGRAM.T
TN = PROGRAM.TN
VERSION = PROGRAM.VERSION
_pip_install = PROGRAM._pip_install
cache_folder = PROGRAM.cache_folder
certificate_file = PROGRAM.certificate_file
hashlib = PROGRAM.hashlib
json = PROGRAM.json
number_text = PROGRAM.number_text
os = PROGRAM.os
outside_work = PROGRAM.outside_work
platform = PROGRAM.platform
re = PROGRAM.re
subprocess = PROGRAM.subprocess
sys = PROGRAM.sys
tempfile = PROGRAM.tempfile
threading = PROGRAM.threading
time = PROGRAM.time


# =====================================================================
#  Speech recognition
#  ------------------

# One recognised word is {"start": seconds, "end": seconds,
# "word": text}. The word keeps the punctuation it was written with,
# because that is the only place a sentence end can be read from.

# Counted over five hours of German speech: 8.4 sentence ends and 17.2
# clause boundaries a minute. Semicolon, colon and dash never occurred
# -- a clause boundary is a comma; the rest are listed and cost nothing.
SENTENCE_MARKS = ".!?"
CLAUSE_MARKS = ",;:–—"
# Punctuation may stand inside a closing quote or bracket, so those
# come off before the last character is looked at.
CLOSING_MARKS = "\"')]}“”„’»«"

# turbo and not large-v3: large-v3 costs five and a half times as long,
# agrees with macOS no better (95.2 against 95.4 %) and times words
# worse. distil-large-v3 is English only; small costs two points.
WHISPER_MODEL = "large-v3-turbo"

# Both recognisers hear a word begin about a tenth of a second late --
# macOS +0.09 to +0.14 s, Whisper +0.065 to +0.115 s -- and stop 0.04
# to 0.10 s early. Neither is the truth, so each gets its own figure.

# Whisper scatters two to five times less than macOS, so a fixed
# correction lands: word boundaries within 0.1 s of the sound go from
# 33-54 % to 53-63 %.
WHISPER_START_S = -0.090
WHISPER_END_S = 0.060

# macOS gets none by decision, not omission: its scatter is wider than
# the offset, so a correction moves noise -- 25-33 % within 0.1 s
# becomes 24-39 %, and a refused gap is not a stretched word end.
MACOS_START_S = 0.0
MACOS_END_S = 0.0


def word_mark(text):
    """Say what a word closes: a sentence, a clause, or nothing.

    The mark sits on the word, so that word's end is the boundary's
    time. A trailing hyphen ends nothing; in German it breaks a compound.
    """
    stripped = (text or "").strip().rstrip(CLOSING_MARKS)
    if not stripped:
        return ""
    if stripped[-1] in SENTENCE_MARKS:
        return "sentence"
    if stripped[-1] in CLAUSE_MARKS:
        return "clause"
    return ""


def speech_word(start, end, text):
    """Build one word of the inner form, times rounded to the ms."""
    return {"start": round(float(start), 3),
            "end": round(float(end), 3),
            "word": (text or "").strip()}


def sentences_of(words):
    """Group words into sentences: one list of words per sentence.

    A sentence ends on the word carrying the mark; what follows the
    last mark is a sentence too, or the last minutes would be lost.
    """
    out, current = [], []
    for w in words:
        current.append(w)
        if word_mark(w.get("word")) == "sentence":
            out.append(current)
            current = []
    if current:
        out.append(current)
    return out


def sentence_end_times(words):
    """The times sentences end: the end of the word with the mark."""
    return [w["end"] for w in words
            if word_mark(w.get("word")) == "sentence"]


def clause_break_times(words):
    """The times clauses break, mostly commas."""
    return [w["end"] for w in words
            if word_mark(w.get("word")) == "clause"]


def sentence_start_times(words):
    """The times sentences begin: the start of their first word."""
    return [group[0]["start"] for group in sentences_of(words) if group]


def corrected_words(words, start_by, end_by):
    """Move word starts and word ends by their own correction.

    The two edges are wrong differently, so one shift for both would
    undo itself. Nothing moves before zero, none ends before it begins.
    """
    if not start_by and not end_by:
        return list(words)
    out = []
    for w in words:
        start = max(0.0, w["start"] + start_by)
        out.append(speech_word(start, max(start, w["end"] + end_by),
                               w["word"]))
    return out


#------------------------------------------------------- Who said it

# A word goes to whoever covers most of it. Measured over 45473 words:
# 95 to 98 % touch one speaker, 1 to 5 % two, 0.4 % fall in a gap.
# Edges widen in speaker_segments_polish; widening twice moves them.

# The majority decides only where a sentence is nearly of one voice:
# on every sentence it gains almost nothing (98.71 -> 98.78 %), below
# a fifth 98.89 %, at a tenth 98.86 %, at a third 98.83 %.
SENTENCE_MINORITY_SHARE = 0.2


def words_by_speaker(words, segments, tally=None):
    """Give every word the speaker whose segments cover most of it.

    A word touching nobody goes to the nearest segment; where two
    cover it equally, the one speaking more wins -- the order
    *segments*, [(name, [(from, to), ...])], arrives in. *tally* counts
    clear, shared and gap words. No segments, no "speaker" on a word.
    """
    out = [dict(w) for w in sorted(words or (),
                                   key=lambda w: (w["start"], w["end"]))]
    if tally is not None:
        tally.update({"clear": 0, "shared": 0, "gap": 0})
    if not out or not segments:
        return out
    covered_by = [0.0] * len(out)
    touching = [0] * len(out)
    nearest = [None] * len(out)
    nearest_name = [""] * len(out)
    for name, parts in segments:
        parts = sorted(parts)
        i = 0
        for k, w in enumerate(out):
            # The words are in time order, so a stretch that ends
            # before this word ends before every later one too.
            while i < len(parts) and parts[i][1] < w["start"]:
                i += 1
            covered, j = 0.0, i
            while j < len(parts) and parts[j][0] < w["end"]:
                covered += (min(parts[j][1], w["end"])
                            - max(parts[j][0], w["start"]))
                j += 1
            if covered > 0:
                touching[k] += 1
                if covered > covered_by[k]:
                    covered_by[k] = covered
                    out[k]["speaker"] = name
                continue
            gap = None
            if i < len(parts):
                gap = max(0.0, parts[i][0] - w["end"])
            if i > 0:
                back = max(0.0, w["start"] - parts[i - 1][1])
                gap = back if gap is None else min(gap, back)
            if gap is not None and (nearest[k] is None or gap < nearest[k]):
                nearest[k], nearest_name[k] = gap, name
    for k, w in enumerate(out):
        if not touching[k] and nearest_name[k]:
            w["speaker"] = nearest_name[k]
    if tally is not None:
        tally["clear"] = sum(1 for n in touching if n == 1)
        tally["shared"] = sum(1 for n in touching if n > 1)
        tally["gap"] = sum(1 for n in touching if not n)
    return out


def sentence_speakers(words, limit=SENTENCE_MINORITY_SHARE):
    """Let a sentence agree on one speaker where it is nearly of one.

    A sentence more divided than *limit* keeps its single words: it is
    usually two sentences of two people, and the words know better.
    """
    out = []
    for group in sentences_of(words):
        count = {}
        for w in group:
            if w.get("speaker"):
                count[w["speaker"]] = count.get(w["speaker"], 0) + 1
        if count:
            total = sum(count.values())
            name, most = max(count.items(), key=lambda x: x[1])
            if (total - most) / float(total) < limit:
                group = [dict(w, speaker=name) for w in group]
        out.extend(group)
    return out


def words_with_speakers(words, segments, tally=None,
                        limit=SENTENCE_MINORITY_SHARE):
    """Say who spoke each word: covered most, then agreed per sentence."""
    return sentence_speakers(words_by_speaker(words, segments, tally), limit)


def speech_passages(words):
    """Group the words into passages: one voice, speaking on."""
    out = []
    for w in words or ():
        who = w.get("speaker") or ""
        if not out or out[-1]["speaker"] != who:
            out.append({"speaker": who, "start": w["start"],
                        "end": w["end"], "words": [w]})
        else:
            out[-1]["end"] = max(out[-1]["end"], w["end"])
            out[-1]["words"].append(w)
    return out


#------------------------------------------------------ The three files

# What a subtitle may hold. 42 characters a line and two lines is the
# limit the timed text style guides give for Latin script, and seven
# seconds is the longest a subtitle stands there.
SUBTITLE_LINE_CHARS = 42
SUBTITLE_LINES = 2
SUBTITLE_LONGEST_S = 7.0

# How wide the file for reading is set. Long enough for a sentence,
# narrow enough to read in a terminal beside something else.
TRANSCRIPT_WIDTH = 76


def wrapped_lines(text, width):
    """Break a text into lines of at most *width*, on the spaces.

    A single word longer than the line stays whole: breaking it would
    make it unreadable, and one long line is the smaller trouble.
    """
    lines, line = [], ""
    for word in (text or "").split():
        if line and len(line) + 1 + len(word) > width:
            lines.append(line)
            line = word
        else:
            line = word if not line else line + " " + word
    if line:
        lines.append(line)
    return lines or [""]


def srt_time(seconds):
    """A time as SubRip writes it: hours, minutes, seconds, comma, ms."""
    ms = int(round(max(0.0, float(seconds)) * 1000))
    return "%02d:%02d:%02d,%03d" % (ms // 3600000, ms // 60000 % 60,
                                    ms // 1000 % 60, ms % 1000)


def subtitle_cues(words, line_chars=SUBTITLE_LINE_CHARS,
                  lines=SUBTITLE_LINES, longest=SUBTITLE_LONGEST_S):
    """Cut the words into subtitles: (from, to, speaker, text).

    A subtitle never holds two speakers, never outlives *longest* and
    never grows past *lines* lines. Inside that it ends on a full
    stop, so a subtitle carries a whole thought where it fits.
    """
    room = max(1, int(line_chars) * max(1, int(lines)))
    out = []
    for passage in speech_passages(words):
        current = []
        for w in passage["words"]:
            text = " ".join(x["word"] for x in current + [w])
            too_long = current and (
                len(text) > room
                or w["end"] - current[0]["start"] > longest)
            if too_long:
                out.append((current[0]["start"], current[-1]["end"],
                            passage["speaker"],
                            " ".join(x["word"] for x in current)))
                current = []
            current.append(w)
            if word_mark(w["word"]) == "sentence":
                out.append((current[0]["start"], current[-1]["end"],
                            passage["speaker"],
                            " ".join(x["word"] for x in current)))
                current = []
        if current:
            out.append((current[0]["start"], current[-1]["end"],
                        passage["speaker"],
                        " ".join(x["word"] for x in current)))
    return out


def subtitle_file_text(cues, line_chars=SUBTITLE_LINE_CHARS):
    """The subtitles as a SubRip file.

    The speaker's name stands in capitals with a colon, only where the
    speaker changes -- on every one it would take the sentence's room.
    """
    parts, last = [], None
    for i, (a, b, who, text) in enumerate(cues or (), 1):
        if who and who != last:
            text = "%s: %s" % (who.upper(), text)
        last = who
        parts.append("%d\n%s --> %s\n%s\n"
                     % (i, srt_time(a), srt_time(b),
                        "\n".join(wrapped_lines(text, line_chars))))
    return "\n".join(parts)


def transcript_passages_json(words):
    """The passages in the shape auphonic.com writes beside a file.

    One entry per passage, with speaker, running text and a row per
    word. The fourth column of a row is confidence and stays empty:
    neither recogniser here reports one.
    """
    out = []
    for passage in speech_passages(words):
        entry = {"start": round(passage["start"], 3),
                 "end": round(passage["end"], 3),
                 "text": " ".join(w["word"] for w in passage["words"]),
                 "timestamps": [[w["word"], w["start"], w["end"], None]
                                for w in passage["words"]]}
        if passage["speaker"]:
            entry["speaker"] = passage["speaker"]
        out.append(entry)
    return out


def transcript_file_text(words, width=TRANSCRIPT_WIDTH):
    """The transcript for reading: a paragraph a voice, no times."""
    parts = []
    for passage in speech_passages(words):
        text = " ".join(w["word"] for w in passage["words"])
        if passage["speaker"]:
            text = "%s: %s" % (passage["speaker"], text)
        parts.append("\n".join(wrapped_lines(text, width)))
    return "\n\n".join(parts) + ("\n" if parts else "")


def write_transcript_files(folder, base, words, segments=()):
    """Write the transcript beside the run: json, srt and txt.

    The three formats and their names are the ones auphonic.com
    delivers, so whatever reads a transcript need not tell the two
    origins apart. Without speaker segments the files carry no names:
    a guess is worse than a gap. Returns the files written.
    """
    tally = {}
    said = words_with_speakers(words, segments, tally)
    if not said:
        return []
    total = len(said)
    if segments:
        print(T('  %s words: %s %% to one voice, %s %% to two, '
                '%s %% in a gap')
              % (number_text(total, 0),
                 number_text(100.0 * tally["clear"] / total, 1),
                 number_text(100.0 * tally["shared"] / total, 1),
                 number_text(100.0 * tally["gap"] / total, 1)))
    else:
        print(T('  %s words, without names -- nobody was separated')
              % number_text(total, 0))
    stem = os.path.join(folder, base)
    written = []
    for ending, content in (
            # Written in one piece, not laid out over lines: an hour of
            # speech is around twelve thousand words, and a word set out
            # as six lines would make a file nobody opens twice.
            ("json", json.dumps(transcript_passages_json(said),
                                ensure_ascii=False)),
            ("srt", subtitle_file_text(subtitle_cues(said))),
            ("txt", transcript_file_text(said))):
        target = stem + "." + ending
        try:
            with open(target, "w", encoding="utf-8") as f:
                f.write(content)
        except OSError as e:
            print(T('  %s could not be written: %s')
                  % (os.path.basename(target), e))
            continue
        written.append(target)
    return written


#--------------------------------------------------------------- Reading

def words_for_handover(words):
    """The words as the handover file carries them: start, end, word.

    An hour of speech is around twelve thousand words. As objects with
    three named keys the list alone would be a megabyte of key names,
    so the three values stand in a row and the reader names them again.
    """
    return [[w["start"], w["end"], w["word"]] for w in words]


def words_from_handover(d):
    """Read the words back out of a parsed handover file."""
    out = []
    for row in ((d or {}).get("words") or ()):
        try:
            out.append(speech_word(row[0], row[1], row[2]))
        except (TypeError, ValueError, IndexError, KeyError):
            continue
    return out


def read_word_tsv(path):
    """Read the recogniser's own output: start, end and word a line.

    A word without a time is written with -1 and skipped here; how
    many were skipped is said out loud rather than passed over.
    """
    out, timeless = [], 0
    with open(path, encoding="utf-8", errors="replace") as f:
        for line in f:
            parts = line.rstrip("\n").split("\t")
            if len(parts) < 3 or not parts[2].strip():
                continue
            try:
                start, end = float(parts[0]), float(parts[1])
            except ValueError:
                continue
            if start < 0 or end < 0:
                timeless += 1
                continue
            out.append(speech_word(start, end, parts[2]))
    if timeless:
        print(TN(timeless,
                 '  %s word came back without a time and was left out.',
                 '  %s words came back without a time and were left '
                 'out.') % number_text(timeless, 0))
    out.sort(key=lambda w: (w["start"], w["end"]))
    return out


def read_speech_json(path):
    """Read the word times written beside a transcript.

    The file is a list of passages; each carries the speaker, the
    running text and one entry per word -- word, start, end, confidence.
    """
    with open(path, encoding="utf-8", errors="replace") as f:
        d = json.load(f)
    if isinstance(d, dict):
        return words_from_handover(d)
    out = []
    for passage in (d or ()):
        for entry in (passage or {}).get("timestamps") or ():
            try:
                out.append(speech_word(entry[1], entry[2], entry[0]))
            except (TypeError, ValueError, IndexError):
                continue
    out.sort(key=lambda w: (w["start"], w["end"]))
    return out


def read_words(path):
    """Read word times from whichever kind of file this is.

    Three kinds turn up: the recogniser's tab separated lines, the
    json auphonic.com delivers, and this program's own handover file.
    """
    if os.path.splitext(path)[1].lower() == ".json":
        return read_speech_json(path)
    return read_word_tsv(path)


#------------------------------------------------ The recognition of macOS

# Compiled once and kept: audio in, one line per word out. Without
# -parse-as-library a single file with @main does not build, and the
# locale must come from supportedLocales -- de-DE, de-AT, de-CH exist.
SPEECH_SWIFT = r'''import Foundation
import Speech
import AVFoundation

@main struct Recogniser {
  static func pick(_ want: String) async -> Locale? {
    if want.isEmpty { return nil }
    let all = await SpeechTranscriber.supportedLocales
    let asked = want.replacingOccurrences(of: "_", with: "-")
    for l in all where l.identifier
        .replacingOccurrences(of: "_", with: "-")
        .lowercased() == asked.lowercased() { return l }
    let head = asked.split(separator: "-")[0].lowercased()
    let same = all.filter {
      ($0.language.languageCode?.identifier ?? "").lowercased()
        == head }
    let here = Locale.current.region?.identifier ?? ""
    for l in same where (l.region?.identifier ?? "") == here {
      return l
    }
    return same.first
  }
  static func main() async {
    let t0 = Date()
    let args = CommandLine.arguments
    if args.count > 1 && args[1] == "--locales" {
      for l in await SpeechTranscriber.supportedLocales {
        print(l.identifier)
      }
      exit(0)
    }
    guard args.count > 2 else { print("ERR arguments"); exit(2) }
    let want = args.count > 3 ? args[3] : ""
    let loc = await pick(want) ?? Locale.current
    let tr = SpeechTranscriber(locale: loc, transcriptionOptions: [],
                               reportingOptions: [],
                               attributeOptions: [.audioTimeRange])
    do {
      let url = URL(fileURLWithPath: args[1])
      let file = try AVAudioFile(forReading: url)
      if let ask = try await AssetInventory.assetInstallationRequest(
            supporting: [tr]) {
        try await ask.downloadAndInstall()
      }
      let analyzer = SpeechAnalyzer(modules: [tr])
      let collector = Task { () -> String in
        var s = ""
        for try await r in tr.results {
          let a = r.text
          for run in a.runs {
            let w = String(a[run.range].characters)
            if let t = run.audioTimeRange {
              s += String(format: "%.3f\t%.3f\t%@\n",
                          t.start.seconds, t.end.seconds, w)
            } else { s += "-1\t-1\t" + w + "\n" }
          }
        }
        return s
      }
      let t1 = Date()
      _ = try await analyzer.analyzeSequence(from: file)
      try await analyzer.finalizeAndFinishThroughEndOfInput()
      let text = try await collector.value
      try text.write(to: URL(fileURLWithPath: args[2]),
                     atomically: true, encoding: .utf8)
      print(String(format: "LOCALE %@ SETUP %.2f SECONDS %.2f",
                   loc.identifier, t1.timeIntervalSince(t0),
                   Date().timeIntervalSince(t1)))
    } catch { print("ERR", error); exit(4) }
  }
}
'''


def swift_compiler():
    """Return the Swift compiler, or None where there is none.

    /usr/bin/swiftc is only a stub: without the command line developer
    tools behind it, calling it opens a dialogue. xcode-select answers
    the same question without opening anything, so it is asked first.
    """
    if sys.platform != "darwin" or not os.path.exists("/usr/bin/swiftc"):
        return None
    try:
        p = subprocess.run(["/usr/bin/xcode-select", "-p"],
                           stdout=subprocess.DEVNULL,
                           stderr=subprocess.DEVNULL)
    except OSError:
        return None
    return "/usr/bin/swiftc" if p.returncode == 0 else None


def recogniser_names():
    """Where the built recogniser goes, and where a failed build says so.

    Both names carry a hash of the source and the compiler version, so
    a changed program or a system update starts over. Returns (binary,
    note), or (None, None) where there is no compiler.
    """
    compiler = swift_compiler()
    folder = cache_folder("speech")
    if not compiler or not folder:
        return None, None
    try:
        p = subprocess.run([compiler, "--version"],
                           stdout=subprocess.PIPE,
                           stderr=subprocess.STDOUT)
        version = (p.stdout or b"").decode("utf-8", "replace")
    except OSError:
        return None, None
    mark = hashlib.sha1(
        (SPEECH_SWIFT + version).encode("utf-8")).hexdigest()[:12]
    binary = os.path.join(folder, "recogniser_" + mark)
    return binary, binary + ".refused"


def recogniser_program(build=True):
    """Return the compiled recogniser, building it once if need be.

    Building costs about a second, so the result is kept -- and so is a
    refusal: an older macOS has the compiler but not the recognition,
    and without the note it would try again for ever.
    """
    binary, refused = recogniser_names()
    if not binary:
        return None
    if os.path.exists(binary):
        return binary
    if not build or os.path.exists(refused):
        return None
    print(T('  Building the speech recogniser ...'))
    started = time.time()
    folder = os.path.dirname(binary)
    # Two runs at once must not write each other's files, so both the
    # source and the result get a name of their own and only the
    # finished binary is moved to the name everybody looks for.
    handle, source = tempfile.mkstemp(suffix=".swift", dir=folder)
    os.close(handle)
    out = source[:-6] + ".bin"
    try:
        with open(source, "w", encoding="utf-8") as f:
            f.write(SPEECH_SWIFT)
        p = subprocess.run([swift_compiler(), "-O", "-parse-as-library",
                            source, "-o", out],
                           stdout=subprocess.PIPE,
                           stderr=subprocess.STDOUT)
        note = (p.stdout or b"").decode("utf-8", "replace").strip()
    except OSError as e:
        print(T('  The Swift compiler reports: %s') % e)
        return None
    finally:
        try:
            os.unlink(source)
        except OSError:
            pass
    if p.returncode != 0 or not os.path.exists(out):
        print(T('  The Swift compiler reports: %s')
              % (note.splitlines() or [""])[-1])
        try:
            with open(refused, "w", encoding="utf-8") as f:
                f.write(note)
        except OSError:
            pass
        return None
    os.replace(out, binary)
    print(T('  The speech recogniser is built (%s s).')
          % number_text(time.time() - started))
    return binary


SPEECH_TIMING = re.compile(
    r"^LOCALE\s+(\S+)\s+SETUP\s+([0-9.]+)\s+SECONDS\s+([0-9.]+)$")


def speech_note_said(note):
    """Put what the recogniser printed into words of our own.

    It writes one line about itself -- locale, time to get ready, time
    spent listening -- and that line is English in its own keywords.
    Anything else it says is a fault and goes out as one.
    """
    found = SPEECH_TIMING.match(str(note or "").strip())
    if found:
        # Through number_text, or a German run reads "0.1 s" -- the
        # catalogue turns the sentence and left the number English.
        return T('  Recognised in %s: ready in %s s, heard in %s s') \
            % (found.group(1).replace("_", "-"),
               number_text(float(found.group(2))),
               number_text(float(found.group(3))))
    return T('  The speech recognition reports: %s') % note


def macos_recognition_ready():
    """Say whether the recognition macOS brings with it can be used."""
    binary, refused = recogniser_names()
    if not binary:
        return False
    return os.path.exists(binary) or not os.path.exists(refused)


def speech_locale(language):
    """The recogniser's code for the tag the interface carries.

    The Language field and --speech-language hold what ffmpeg wants on
    the audio track: three letters. Both recognisers want the two-letter
    code. "ger" matched no locale and was dropped without a word, so the
    machine's own language decided and the field did nothing -- asked
    for "eng" on a German Mac, the recognition ran in de_DE.
    """
    tag = (language or "").strip()
    return SPEECH_CODES.get(tag.lower(), tag)


def macos_words(audio_path, language=""):
    """Let the recognition macOS brings with it write the words.

    None where this way does not exist: an older macOS, no developer
    tools, another system. [] means it ran and heard nothing.
    """
    program = recogniser_program()
    if not program:
        return None
    language = speech_locale(language)
    handle, out = tempfile.mkstemp(suffix=".tsv", prefix="vpm_words_")
    os.close(handle)
    try:
        p = subprocess.run([program, audio_path, out,
                            language or ""],
                           stdout=subprocess.PIPE,
                           stderr=subprocess.STDOUT)
        note = (p.stdout or b"").decode("utf-8", "replace").strip()
        if p.returncode != 0:
            print(T('  The speech recognition reports: %s')
                  % (note.splitlines() or [""])[-1])
            return None
        # What it was asked to do and what it did: which locale it
        # settled on and how long it took, so a slow run later can be
        # held against this one.
        if note:
            print(speech_note_said(note))
        return corrected_words(read_word_tsv(out),
                               MACOS_START_S, MACOS_END_S)
    except OSError as e:
        print(T('  The speech recognition reports: %s') % e)
        return None
    finally:
        try:
            os.unlink(out)
        except OSError:
            pass


#--------------------------------------------------------------- Whisper

def whisper_arithmetic():
    """Pick what faster-whisper computes in.

    Measured on Apple Silicon: float32 runs 2.3 times faster than int8,
    because that path goes through Accelerate. On x86 the usual order
    holds and int8 is faster; that has not been measured here.
    """
    if sys.platform == "darwin" and platform.machine() == "arm64":
        return "float32"
    return "int8"


def use_certificates():
    """Point the libraries that fetch on their own at the bundle.

    They read these two variables and nothing else; without them the
    model download fails on a Python that has no certificates.
    """
    bundle = certificate_file()
    if not bundle:
        print(T('  No certificate bundle found -- an HTTPS download '
                'may fail.'))
        return None
    os.environ.setdefault("SSL_CERT_FILE", bundle)
    os.environ.setdefault("REQUESTS_CA_BUNDLE", bundle)
    return bundle


def whisper_words(audio_path, language="", install=True):
    """Recognise with faster-whisper where macOS cannot.

    The voice activity filter is not optional: without it the
    recognition writes words into silence, twenty-one of them into a
    five minute pause. Returns the words with Whisper's own correction
    applied, or None where the package is not there.
    """
    import importlib
    try:
        module = importlib.import_module("faster_whisper")
    except ImportError:
        if not install:
            return None
        print(T('%s is missing -- installing it. The first time takes '
                'a few minutes.') % "faster-whisper")
        if not _pip_install("faster-whisper"):
            return None
        importlib.invalidate_caches()
        try:
            module = importlib.import_module("faster_whisper")
        except ImportError:
            return None
    # The model is fetched over HTTPS on first use, and that is where
    # a Python without certificates fails.
    use_certificates()
    try:
        # CTranslate2 knows cpu and cuda only -- mps and metal are
        # unknown names, not refused ones. "auto" is the graphics unit
        # on an NVIDIA card and the processor everywhere else.
        model = module.WhisperModel(WHISPER_MODEL, device="auto",
                                    compute_type=whisper_arithmetic())
        pieces, _info = model.transcribe(
            audio_path, language=speech_locale(language).split("-")[0] or None,
            word_timestamps=True, vad_filter=True)
        out = []
        # transcribe hands back a generator: nothing is computed until
        # the pieces are walked, so the clock has to run over the walk.
        with outside_work(WHISPER_MODEL, os.path.basename(audio_path)):
            for piece in pieces:
                # words is None unless word_timestamps was asked for,
                # and it was: without the times there is nothing to use.
                for w in (piece.words or ()):
                    out.append(speech_word(w.start, w.end, w.word))
    except Exception as e:
        print(T('  The speech recognition reports: %s') % e)
        return None
    out.sort(key=lambda w: (w["start"], w["end"]))
    return corrected_words(out, WHISPER_START_S, WHISPER_END_S)


#------------------------------------------------------------- Storage

# The two ways, in the order the recognition tries them: what the
# window and the run both call "macos" first, then Whisper.
WORD_WAYS = (("macos", "macOS"), ("whisper", WHISPER_MODEL))


def words_cache_key(mark, language, way):
    """The name a written-down recording lives under.

    What the recording holds decides, not where it lies: the run mixes
    into a new folder every time, so a key on the path never meets
    itself. Language and way belong in it: both change the words.
    """
    if not mark:
        return ""
    parts = [mark, (language or "").lower(), way or ""]
    return hashlib.sha1(
        "\n".join(parts).encode("utf-8")).hexdigest()[:16]


def words_cache_file(key):
    """Where a written-down recording lives, or None."""
    folder = cache_folder("words")
    return os.path.join(folder, key + ".json") if folder and key else None


def words_cache_read(mark, language, way):
    """The words stored under this mark, or None to listen again.

    An empty list is an answer, not a miss: a recording nobody spoke
    in was listened to and gave nothing.
    """
    file_path = words_cache_file(words_cache_key(mark, language, way))
    if not file_path or not os.path.exists(file_path):
        return None
    try:
        with open(file_path, encoding="utf-8") as f:
            d = json.load(f)
    except (OSError, ValueError):
        return None
    words = d.get("words")
    return words if isinstance(words, list) else None


def words_cache_write(mark, language, way, words):
    """Store what was heard so the next start need not listen again."""
    file_path = words_cache_file(words_cache_key(mark, language, way))
    if not file_path:
        return
    d = {"when": time.time(), "version": VERSION,
         "language": language or "", "way": way or "",
         "words": list(words or ())}
    try:
        fd, beside = tempfile.mkstemp(dir=os.path.dirname(file_path),
                                      prefix=".vpm_", suffix=".json")
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(d, f, ensure_ascii=False)
        os.replace(beside, file_path)
    except OSError as e:
        # The words are there either way; only the next start pays for
        # them again. Said out loud, because a store that quietly never
        # stores looks exactly like one that works.
        print(T('  %s could not be written: %s') % (file_path, e))


def words_stored(mark, language, ways):
    """Words already written down here, and the way they came from.

    The ways are asked in the order the recognition itself would take
    them, so a stored answer is the one that machine would give anyway.
    The mark comes in rather than being made here: reading once per way
    would double the cost. Returns (words, way), (None, "") for none.
    """
    for way in ways:
        words = words_cache_read(mark, language, way)
        if words is not None:
            return words, way
    return None, ""


# How much is read at a time when marking a file by its content. A
# larger block buys nothing: the hashing sets the pace, not the disk.
CONTENT_BLOCK = 1 << 20


def file_content_mark(file_path):
    """Return what a file holds, as one string over size and content.

    For a file whose name says nothing: a mix is written into a fresh
    folder on every run, so path and time can never meet themselves,
    and a modification time cannot tell two writes inside one second
    apart either. Costs about a third of a second per gigabyte, read
    or cached. "" where the file cannot be read.
    """
    mark = hashlib.sha1()
    try:
        with open(file_path, "rb") as f:
            mark.update(b"%d\n" % os.fstat(f.fileno()).st_size)
            for block in iter(lambda: f.read(CONTENT_BLOCK), b""):
                mark.update(block)
    except OSError:
        return ""
    return mark.hexdigest()


def recognise_speech(audio_path, language="", way=""):
    """Write down what is spoken in a file, with a time per word.

    macOS needs nothing installed and takes 22 seconds an hour of
    audio; faster-whisper needs 144 MB of packages and a 1.5 GB model
    and about six times real time on a processor. The first that works
    wins unless a way is named. (None, "") means neither exists here.
    """
    started = time.time()
    mark = file_content_mark(audio_path)
    words, took = words_stored(
        mark, language,
        [name for wanted, name in WORD_WAYS if way in ("", wanted)])
    if words is not None:
        print(T('  Speech recognition (%s): %s words, read back')
              % (took, number_text(len(words), 0)))
        return words, took
    took = ""
    if way in ("", "macos"):
        words = macos_words(audio_path, language)
        took = "macOS" if words is not None else ""
    if words is None and way in ("", "whisper"):
        words = whisper_words(audio_path, language)
        took = WHISPER_MODEL if words is not None else ""
    if words is None:
        print(T('  No speech recognition on this machine: macOS 26 '
                'brings one, otherwise faster-whisper is installed.'))
        return None, ""
    words_cache_write(mark, language, took, words)
    print(T('  Speech recognition (%s): %s words in %s s')
          % (took, number_text(len(words), 0),
             number_text(time.time() - started)))
    return words, took


def words_at_hand(audio_path, language=""):
    """Write the words down with what the machine already has.

    A run may install faster-whisper and fetch a 1.5 GB model: somebody
    started it and is watching. The window may not -- nobody asked for
    a download by adding files to a list. So macOS first, faster-whisper
    only where a run already installed it. [] where nothing can listen.
    """
    started = time.time()
    mark = file_content_mark(audio_path)
    words, took = words_stored(mark, language,
                               [name for _wanted, name in WORD_WAYS])
    if words is not None:
        print(T('  Speech recognition (%s): %s words, read back')
              % (took, number_text(len(words), 0)))
        return words
    words = macos_words(audio_path, language)
    took = "macOS"
    if words is None:
        words = whisper_words(audio_path, language, install=False)
        took = WHISPER_MODEL
    if words is None:
        return []
    words_cache_write(mark, language, took, words)
    print(T('  Speech recognition (%s): %s words in %s s')
          % (took, number_text(len(words), 0),
             number_text(time.time() - started)))
    return words


def speech_words_work(source, language, done):
    """One recognition of one recording, in a thread of its own."""
    try:
        words = words_at_hand(source, language)
    except Exception as e:
        print(T('  The speech recognition reports: %s') % str(e)[:140])
        words = []
    done((source, words))


def speech_words_kick_off(state, language="", done=None, source=""):
    """Write down what is said in the recording being separated.

    Beside the separation, not behind it: different machinery, and the
    recognition is over long before the separation is. *source* names
    the recording and carries the separation's consent; without it the
    one in front is meant. Installs nothing -- words_at_hand says why.
    """
    source = source or state.get("speakers_source") or ""
    listening = state.setdefault("speakers_words_now", set())
    # A recording still being written down is not started again: a
    # second separation moves what the window waits for, and without
    # this the round after it would set the same recogniser going twice.
    if (not source or not done or source in listening
            or state.get("speakers_words_of") == source):
        return
    listening.add(source)
    state["speakers_words_of"] = source
    state["speakers_words"] = []
    threading.Thread(target=speech_words_work,
                     args=(source, language, done), daemon=True).start()


def speech_words_done(state, result, wake):
    """The words came back; keep them where they still belong.

    Every recording keeps its own, so a second separation does not
    throw away what was heard in the first. In front stand the words of
    the recording that was asked about, not of the one being separated.
    """
    source, words = result
    state.setdefault("speakers_words_by", {})[source] = list(words or ())
    (state.get("speakers_words_now") or set()).discard(source)
    if source != (state.get("speakers_words_of") or ""):
        return
    state["speakers_words"] = words or []
    wake()


def words_forgotten(state):
    """Forget what was written down in the recordings just let go.

    Carried over, the next production would be built on what was said
    in the last one's.
    """
    for name in ("speakers_words", "speakers_words_of",
                 "speakers_words_by", "speakers_words_now"):
        state.pop(name, None)


def words_of_recording(state, source):
    """What was written down in that recording, None where nothing was.

    The recording on the sheet is not always the one being listened
    to: a second separation asks for its own words while the first is
    still what the preview is built from.
    """
    if not source:
        return None
    by = state.get("speakers_words_by") or {}
    if source in by:
        return by[source]
    if source == (state.get("speakers_words_of") or ""):
        return state.get("speakers_words") or []
    return None
