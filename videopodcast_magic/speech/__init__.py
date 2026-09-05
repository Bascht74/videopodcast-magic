# -*- coding: utf-8 -*-
"""What is said and when, and what is written down from it.

A piece of the program, read out of the folder beside it by beside().
It cannot import the file it was cut out of, because that file is
still being read while this one is; the program is handed in instead,
and every name this piece uses out of it is bound below, by name, so
that nothing in here comes from nowhere.
"""

# The program itself. beside() puts it here before this file is read,
# and the line under that binds it to a name of this file's own.
PROGRAM = PROGRAM

# What the program has and this piece uses, bound once so that the
# recognition reads as it did in the one file. Not one of them is a
# name the program rebinds while it runs, so none of them has to stay
# PROGRAM.something the way a few of the window's do.
T = PROGRAM.T
TN = PROGRAM.TN
VERSION = PROGRAM.VERSION
_pip_install = PROGRAM._pip_install
cache_folder = PROGRAM.cache_folder
decimal_text = PROGRAM.decimal_text
file_content_mark = PROGRAM.file_content_mark
group_text = PROGRAM.group_text
hashlib = PROGRAM.hashlib
json = PROGRAM.json
os = PROGRAM.os
outside_work = PROGRAM.outside_work
platform = PROGRAM.platform
re = PROGRAM.re
speech_locale = PROGRAM.speech_locale
subprocess = PROGRAM.subprocess
sys = PROGRAM.sys
tempfile = PROGRAM.tempfile
threading = PROGRAM.threading
time = PROGRAM.time
use_certificates = PROGRAM.use_certificates


# =====================================================================
#  Speech recognition
#  ------------------
#  What is said, and when. A word with a start and an end is what
#  every sentence rule below rests on: where a sentence ends, where a
#  clause breaks, where a cut may fall without cutting into a word.
#
#  Two ways lead there and both come out in the same form: the
#  recognition macOS brings with it, and faster-whisper for every
#  other machine. Measured over five hours of interview: 22 seconds
#  per hour of audio for the first, six times real time for the
#  second on a processor.
# =====================================================================

# One recognised word is {"start": seconds, "end": seconds,
# "word": text}. The word keeps the punctuation it was written with,
# because that is the only place a sentence end can be read from.

# Sentence ends and clause boundaries, counted over five hours of
# German speech: 8.4 sentence ends and 17.2 clause boundaries per
# minute. Semicolon, colon and dash did not occur once -- a clause
# boundary is a comma in practice; the others are listed because they
# cost nothing.
SENTENCE_MARKS = ".!?"
CLAUSE_MARKS = ",;:–—"
# Punctuation may stand inside a closing quote or bracket, so those
# come off before the last character is looked at.
CLOSING_MARKS = "\"')]}“”„’»«"

# turbo and not large-v3: over the same twenty minutes large-v3 costs
# five and a half times as long, agrees with macOS no better (95.2
# against 95.4 %) and has the worse word times. The 3 GB buy computing
# time, not accuracy. distil-large-v3 is out because it is English
# only, and small saves a fifth of the time for two points.
WHISPER_MODEL = "large-v3-turbo"

# Both recognisers report a word as beginning about a tenth of a
# second after the sound does -- measured against the audio itself, at
# entries after at least half a second of silence, where the beginning
# is not in doubt: macOS +0.09 to +0.14 s, Whisper +0.065 to +0.115 s.
# Neither stretches at the other end: both stop hearing 0.04 to 0.10 s
# before the sound dies away.
#
# There is no shared axis to pull the two onto, because neither of
# them is the truth. Each gets its own correction, and only where the
# correction buys something.

# Whisper scatters two to five times less than macOS, so a fixed
# correction lands: word boundaries within 0.1 s of the sound go from
# 33-54 % to 53-63 %.
WHISPER_START_S = -0.090
WHISPER_END_S = 0.060

# macOS gets none, and that is a decision rather than an omission: its
# scatter is wider than the offset, so a correction would move noise
# and little else -- 25-33 % within 0.1 s becomes 24-39 %. What looks
# like a stretched word end is a refused gap between two words, and no
# offset repairs that.
MACOS_START_S = 0.0
MACOS_END_S = 0.0


def word_mark(text):
    """Say what a word closes: a sentence, a clause, or nothing.

    The mark sits on the word, so the end of that word is the time of
    the boundary. A trailing hyphen does not count: in German it
    breaks a compound and ends nothing.
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

    A sentence ends on the word carrying the mark. What follows the
    last mark is a sentence as well -- the recognition does not always
    close the final one, and dropping it would lose the last minutes
    of an episode.
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

    The two edges are wrong by different amounts and in different
    directions, so one shift for both would put back at the end what
    it took off at the start. Nothing moves before zero, and no word
    ends before it begins.
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

# A word goes to whoever covers most of it. Measured over 45473 words
# of two whole interviews against the clip-on microphones: 95 to 98 %
# of the words touch exactly one speaker, 1 to 5 % touch two, and
# under 0.4 % fall into a gap between two segments.
#
# The edges of the segments are widened where the segments are made
# (speaker_segments_polish), not here -- widening twice would move the
# boundaries a second time.

# The majority of a sentence decides only where the sentence is nearly
# of one voice. Measured: applied to every sentence the majority gains
# almost nothing (98.71 -> 98.78 %), because it repairs as much in the
# clean sentences as it breaks in the mixed ones. Below a fifth it
# gains 98.89 %; at a tenth 98.86 %, at a third 98.83 %.
SENTENCE_MINORITY_SHARE = 0.2


def words_by_speaker(words, segments, tally=None):
    """Give every word the speaker whose segments cover most of it.

    A word that touches nobody goes to the nearest segment: inside a
    gap there is no duration to weigh, and the neighbour is a fifth of
    a second away in the median. Where two speakers cover the same
    word equally the one who speaks more in the whole recording wins,
    which is the order *segments* arrives in.

    *segments* is [(name, [(from, to), ...])], the stretches of one
    speaker sorted and without overlaps among themselves. *tally*, a
    dict, is filled with how many words were clear, shared and in a
    gap. Returns the words in time order, each with a "speaker";
    without segments they come back without one.
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
    usually two sentences of two people, and then the words know
    better than the sentence.
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
    never grows past what *lines* lines can hold. Inside that it ends
    on a full stop, so a subtitle carries a whole thought wherever the
    thought is short enough.
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

    The name of the speaker stands in capitals with a colon, and only
    where the speaker changes: that is how a subtitle names who is
    talking, and repeating the name on every subtitle would take the
    room the sentence needs.
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

    One entry per passage with its speaker, its running text and one
    row per word. The fourth column of a row is how sure the
    recognition was; neither recogniser here reports that, so it
    stays empty rather than being filled with a number nobody
    measured.
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
    who said it is then not known, and a guess in a transcript is
    worse than a gap.

    Returns the files written.
    """
    tally = {}
    said = words_with_speakers(words, segments, tally)
    if not said:
        return []
    total = len(said)
    if segments:
        print(T('  %s words: %.1f %% to one voice, %.1f %% to two, '
                '%.1f %% in a gap')
              % (group_text(total), 100.0 * tally["clear"] / total,
                 100.0 * tally["shared"] / total,
                 100.0 * tally["gap"] / total))
    else:
        print(T('  %s words, without names -- nobody was separated')
              % group_text(total))
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

    An hour of speech is around twelve thousand words. Written as
    objects with three named keys each, the list alone would be a
    megabyte of key names, so the three values stand in a row and the
    reader names them again.
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
                 '  %d word came back without a time and was left out.',
                 '  %d words came back without a time and were left '
                 'out.') % timeless)
    out.sort(key=lambda w: (w["start"], w["end"]))
    return out


def read_speech_json(path):
    """Read the word times written beside a transcript.

    The file is a list of passages; each carries the speaker, the
    running text and one entry per word -- the word itself, its start,
    its end and how sure the recognition was.
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
    json auphonic.com delivers, and the handover file this program
    writes itself.
    """
    if os.path.splitext(path)[1].lower() == ".json":
        return read_speech_json(path)
    return read_word_tsv(path)


#------------------------------------------------ The recognition of macOS

# The way into the recognition macOS brings with it is Swift, so this
# is compiled once and kept. It takes the audio file, the file to
# write and the wanted language, and writes one line per word:
# start, end and the word with its punctuation.
#
# Two things it must not be without: -parse-as-library, or a single
# file with @main does not build at all, and the locale is looked up
# in supportedLocales rather than assembled from the language code --
# de-DE, de-AT and de-CH all exist and only the system knows which
# ones are installed.
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

    /usr/bin/swiftc is only a stub: without the command line
    developer tools behind it, calling it opens a dialogue asking for
    them. xcode-select answers the same question without opening
    anything, so it is asked first.
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

    Both names carry a hash of the source and of the compiler
    version, so a changed program or a system update starts over and
    an unchanged one does not. Returns (binary, note) or (None, None)
    where there is no compiler at all.
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

    Building costs about a second and would otherwise cost it on
    every run, so the result is kept -- and so is a refusal. An older
    macOS has the compiler but not the recognition, and without the
    note it would try again, and say so again, for ever.
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
    print(T('  The speech recogniser is built (%.1f s).')
          % (time.time() - started))
    return binary


SPEECH_TIMING = re.compile(
    r"^LOCALE\s+(\S+)\s+SETUP\s+([0-9.]+)\s+SECONDS\s+([0-9.]+)$")


def speech_note_said(note):
    """Put what the recogniser printed into words of our own.

    It writes one line about itself: the locale, how long it took to
    get ready, how long it listened. Handed on unchanged that line
    stood in the progress bar in its own keywords -- "LOCALE de_DE
    SETUP 0.10 SECONDS 25.75" -- English in a German run. Anything
    else it says is a fault and goes out as one.
    """
    found = SPEECH_TIMING.match(str(note or "").strip())
    if found:
        # Through decimal_text, or a German run reads "0.1 s" -- the
        # catalogue turns the sentence and left the number English.
        return T('  Recognised in %s: ready in %s s, heard in %s s') \
            % (found.group(1).replace("_", "-"),
               decimal_text("%.1f" % float(found.group(2))),
               decimal_text("%.1f" % float(found.group(3))))
    return T('  The speech recognition reports: %s') % note


def macos_recognition_ready():
    """Say whether the recognition macOS brings with it can be used."""
    binary, refused = recogniser_names()
    if not binary:
        return False
    return os.path.exists(binary) or not os.path.exists(refused)


def macos_words(audio_path, language=""):
    """Let the recognition macOS brings with it write the words.

    Returns the words, or None where this way does not exist -- an
    older macOS, no developer tools, another system. An empty list
    means it ran and heard nothing, which is a different answer.
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

    Measured on Apple Silicon: float32 runs 2.3 times faster than
    int8, because that path goes through Accelerate while int8 goes
    through a general ARM matrix multiplication. On x86 the usual
    order holds and int8 is the faster one; that has not been
    measured here.
    """
    if sys.platform == "darwin" and platform.machine() == "arm64":
        return "float32"
    return "int8"


def whisper_words(audio_path, language="", install=True):
    """Recognise with faster-whisper where macOS cannot.

    large-v3-turbo: large-v3 costs five and a half times the time for
    the same result and worse word times. The voice activity filter
    is not optional -- without it the recognition writes
    words into silence, twenty-one of them into a five minute pause.

    Returns the words with Whisper's own correction applied, or None
    where the package is not there.
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
        # CTranslate2 knows two devices, cpu and cuda -- mps and metal
        # are not refused, they are unknown names. "auto" therefore
        # means the graphics unit only on a machine with an NVIDIA
        # card, and the processor everywhere else.
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
    into a folder of its own every time, so a key on the path would
    never meet itself. The language and the way belong in it as well:
    the same recording in another language gives other words, and the
    two recognisers do not write the same ones either.
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
    them, so a stored answer is the one that machine would have given
    anyway. The mark comes in rather than being made here: reading the
    recording once per way would double what the store costs. Returns
    (words, way), (None, "") for nothing stored.
    """
    for way in ways:
        words = words_cache_read(mark, language, way)
        if words is not None:
            return words, way
    return None, ""


def recognise_speech(audio_path, language="", way=""):
    """Write down what is spoken in a file, with a time per word.

    The way macOS brings with it needs nothing installed and takes 22
    seconds for an hour of audio; faster-whisper needs 144 MB of
    packages and a 1.5 GB model and takes about six times real time
    on a processor. The first one that works wins, unless a way was
    named.

    Returns (words, the way it took). (None, "") means neither way
    exists on this machine.
    """
    started = time.time()
    mark = file_content_mark(audio_path)
    words, took = words_stored(
        mark, language,
        [name for wanted, name in WORD_WAYS if way in ("", wanted)])
    if words is not None:
        print(T('  Speech recognition (%s): %s words, read back')
              % (took, group_text(len(words))))
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
    print(T('  Speech recognition (%s): %s words in %.1f s')
          % (took, group_text(len(words)), time.time() - started))
    return words, took


def words_at_hand(audio_path, language=""):
    """Write the words down with what the machine already has.

    The run may install faster-whisper and fetch a model of 1.5 GB,
    because somebody started the run and is watching it. The window
    may not: nobody asked for a download by adding files to a list.
    So this takes the recognition macOS brings with it, and
    faster-whisper only where the package is already installed -- and
    it is only ever installed because a run put it there, which is the
    same run that fetched the model.

    Returns the words, [] where this machine cannot listen.
    """
    started = time.time()
    mark = file_content_mark(audio_path)
    words, took = words_stored(mark, language,
                               [name for _wanted, name in WORD_WAYS])
    if words is not None:
        print(T('  Speech recognition (%s): %s words, read back')
              % (took, group_text(len(words))))
        return words
    words = macos_words(audio_path, language)
    took = "macOS"
    if words is None:
        words = whisper_words(audio_path, language, install=False)
        took = WHISPER_MODEL
    if words is None:
        return []
    words_cache_write(mark, language, took, words)
    print(T('  Speech recognition (%s): %s words in %.1f s')
          % (took, group_text(len(words)), time.time() - started))
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

    Beside the separation, not behind it: the two use different
    machinery and the recognition is over long before the separation
    is. It inherits the separation's consent from its start, which is
    where *source* names the recording before anything is stored under
    it. Without *source* the recording in front is meant. On its own
    it installs nothing and fetches nothing -- words_at_hand says why.
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
    throw away what was heard in the first. In front stand the words
    of the recording that was asked about, not of the one being
    separated: they may arrive before its separation does.
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
