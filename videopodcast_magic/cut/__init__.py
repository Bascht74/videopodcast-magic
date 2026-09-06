# -*- coding: utf-8 -*-
"""The cut: who is on camera when, and what carries it out of here.

A piece of the program, read in by beside(): it cannot import the file
it was cut out of, so the program is handed in and bound below by name.
"""

# Put here by beside() before this file is read.
PROGRAM = PROGRAM

# What this piece uses out of the program, bound once. GUI_RUNNING,
# choices_shut and distribute_tracks_to_cameras stay below.

ByFile = PROGRAM.ByFile
CAMERA_TYPES = PROGRAM.CAMERA_TYPES
CATALOGUE = PROGRAM.CATALOGUE
CLIP_COLOURS = PROGRAM.CLIP_COLOURS
CLOSING_MARKS = PROGRAM.CLOSING_MARKS
COLOURS = PROGRAM.COLOURS
CUT_CHOICES = PROGRAM.CUT_CHOICES
FILE_FORMAT = PROGRAM.FILE_FORMAT
FileSet = PROGRAM.FileSet
IGNORE_AUDIO = PROGRAM.IGNORE_AUDIO
MICROPHONES_APART_DB = PROGRAM.MICROPHONES_APART_DB
MIN_EDIT_DURATION_S = PROGRAM.MIN_EDIT_DURATION_S
MIX_ONLY = PROGRAM.MIX_ONLY
PROJECT_PREFIX = PROGRAM.PROJECT_PREFIX
SHOT_ALTERNATE = PROGRAM.SHOT_ALTERNATE
SHOT_ANSWER = PROGRAM.SHOT_ANSWER
SHOT_HOLD = PROGRAM.SHOT_HOLD
SHOT_HOLD_BRIEF = PROGRAM.SHOT_HOLD_BRIEF
SHOT_LISTENER = PROGRAM.SHOT_LISTENER
SHOT_NAMES = PROGRAM.SHOT_NAMES
SHOT_OFF = PROGRAM.SHOT_OFF
SHOT_WIDE = PROGRAM.SHOT_WIDE
SILENCE_HOLD_S = PROGRAM.SILENCE_HOLD_S
SPEAKER_SPLIT_OFF = PROGRAM.SPEAKER_SPLIT_OFF
SPEAKER_SPLIT_SPEED = PROGRAM.SPEAKER_SPLIT_SPEED
SR = PROGRAM.SR
T = PROGRAM.T
TN = PROGRAM.TN
TYPE_CONTENT = PROGRAM.TYPE_CONTENT
TYPE_WIDE = PROGRAM.TYPE_WIDE
VERSION = PROGRAM.VERSION
_intro_outro_entry = PROGRAM._intro_outro_entry
_xml_escape = PROGRAM._xml_escape
as_bad = PROGRAM.as_bad
as_head = PROGRAM.as_head
as_hms = PROGRAM.as_hms
as_warn = PROGRAM.as_warn
audio_start_of = PROGRAM.audio_start_of
bisect = PROGRAM.bisect
build_resolve_project = PROGRAM.build_resolve_project
camera_output_name = PROGRAM.camera_output_name
camera_start_of = PROGRAM.camera_start_of
clause_break_times = PROGRAM.clause_break_times
clip_colour_rgb = PROGRAM.clip_colour_rgb
clocks_apart = PROGRAM.clocks_apart
colour_per_camera = PROGRAM.colour_per_camera
cut_log_heading = PROGRAM.cut_log_heading
decode_audio = PROGRAM.decode_audio
ffprobe_json = PROGRAM.ffprobe_json
file_fingerprint = PROGRAM.file_fingerprint
file_timecode = PROGRAM.file_timecode
find_pauses = PROGRAM.find_pauses
frames_to_timecode = PROGRAM.frames_to_timecode
hdr_from_sources = PROGRAM.hdr_from_sources
how_many_processors = PROGRAM.how_many_processors
is_drop_frame = PROGRAM.is_drop_frame
json = PROGRAM.json
math = PROGRAM.math
measure_loudness = PROGRAM.measure_loudness
media_seconds = PROGRAM.media_seconds
microphones_apart_db = PROGRAM.microphones_apart_db
mix_width = PROGRAM.mix_width
normalise_loudness = PROGRAM.normalise_loudness
number_text = PROGRAM.number_text
os = PROGRAM.os
own_frame_rate = PROGRAM.own_frame_rate
parallel_map = PROGRAM.parallel_map
parse_time_point = PROGRAM.parse_time_point
path_key = PROGRAM.path_key
picture_rate = PROGRAM.picture_rate
re = PROGRAM.re
resolve_timeline_rate = PROGRAM.resolve_timeline_rate
safe_filename = PROGRAM.safe_filename
sample_count = PROGRAM.sample_count
seconds_to_frames = PROGRAM.seconds_to_frames
segments_per_camera = PROGRAM.segments_per_camera
sentence_start_times = PROGRAM.sentence_start_times
sentences_of = PROGRAM.sentences_of
show_progress = PROGRAM.show_progress
speaker_mix_file = PROGRAM.speaker_mix_file
speaker_segments_group = PROGRAM.speaker_segments_group
speaker_segments_polish = PROGRAM.speaker_segments_polish
speaker_source_pick = PROGRAM.speaker_source_pick
speaker_split_available = PROGRAM.speaker_split_available
speaker_split_cached = PROGRAM.speaker_split_cached
speaker_split_missing = PROGRAM.speaker_split_missing
speaker_split_stored = PROGRAM.speaker_split_stored
speakers_on_window_axis = PROGRAM.speakers_on_window_axis
speech_word = PROGRAM.speech_word
speech_words_kick_off = PROGRAM.speech_words_kick_off
step_begin = PROGRAM.step_begin
struct = PROGRAM.struct
subprocess = PROGRAM.subprocess
time = PROGRAM.time
timecode_string = PROGRAM.timecode_string
timecode_to_frames = PROGRAM.timecode_to_frames
timeline_frame_rate = PROGRAM.timeline_frame_rate
trouble_log = PROGRAM.trouble_log
voice_key_parts = PROGRAM.voice_key_parts
voice_lines_here = PROGRAM.voice_lines_here
voices_in_use = PROGRAM.voices_in_use
voices_merged = PROGRAM.voices_merged
widest_frame = PROGRAM.widest_frame
words_for_handover = PROGRAM.words_for_handover
words_from_handover = PROGRAM.words_from_handover
words_of_recording = PROGRAM.words_of_recording


# numpy is the one name the program still has to fetch: it binds the
# real module on the first sum, which a copy taken up there would miss.
class LateNumpy:
    """Stands in for the program's numpy until a sum wants it."""

    def __getattr__(self, name):
        global np
        got = getattr(PROGRAM.np, name)
        np = PROGRAM.np
        return got


np = LateNumpy()

# A speaker has to hold the floor this long before the camera follows.
# Half a second of "yes" would drag it onto the wrong person for seconds.
MIN_SPEECH_TO_SWITCH_S = 1.5

# A label that is not a person: segments shorter than this on average,
# and less than this share of the recognised speech. Total duration
# does not work -- the largest such heap outruns a host.
STRAY_MEAN_S = 1.5
STRAY_SHARE = 0.10

# Restlessness: this many entries inside this window mean the
# recognition is fraying, not that people talk fast.
UNREST_STARTS = 7
UNREST_WINDOW_S = 12.0

# The listener earns the picture only where somebody on that camera was
# heard within this stretch, or it goes to someone silent for minutes.
LISTENER_MEMORY_S = 20.0

# Where a cut may sit: sentence beginning first, clause break second,
# near before far. Beyond four seconds nothing changes, so five is free.
# Both directions -- forwards only finds half as many.
BOUNDARY_NEAR_S = 2.0
BOUNDARY_FAR_S = 5.0

# The exact point comes from the sound, not the text: the dip lands in
# a real speech pause far more often than a word boundary does.
DIP_NEAR_S = 0.5
DIP_FAR_S = 1.0
DIP_STEP_S = 0.010
# A share of the window's own dynamic range. A fixed level in dB misses
# on quiet material, where the whole file spans twenty dB.
DIP_LEVEL_SHARE = 0.30

def merged_spans(spans, join=0.0):
    """Merge overlapping spans; *join* closes gaps up to that long."""
    out = []
    for a, b in sorted(spans):
        if out and a - out[-1][1] <= join:
            out[-1][1] = max(out[-1][1], b)
        else:
            out.append([a, b])
    return [(a, b) for a, b in out]

def span_finder(spans):
    """Return a function saying whether a time falls inside a span.

    The starts are sorted once and searched by halving: the caller asks
    this for every block of the cut against every camera.
    """
    ordered = merged_spans(spans)
    starts = [a for a, _b in ordered]

    def inside(t):
        i = bisect.bisect_right(starts, t) - 1
        return i >= 0 and t < ordered[i][1]
    return inside

def stray_labels(tracks, mean_s=STRAY_MEAN_S, share=STRAY_SHARE):
    """Return the labels that are a leftover heap rather than a person.

    Small heaps of very short segments with little total time mark where
    the recognition did not know; the largest is never one.
    """
    total = sum(b - a for _n, segs in tracks for a, b in segs)
    if total <= 0 or len(tracks) < 2:
        return set()
    held = {n: sum(b - a for a, b in segs) for n, segs in tracks}
    biggest = max(held, key=held.get)
    out = set()
    for name, segs in tracks:
        if name == biggest or not segs:
            continue
        if held[name] / total >= share:
            continue
        if held[name] / len(segs) < mean_s:
            out.add(name)
    return out

def unrest_spans(tracks, camera_of, starts_needed=UNREST_STARTS,
                 window=UNREST_WINDOW_S):
    """Return the stretches where the speaker recognition frays.

    Counted per camera: two people on one camera taking turns are one
    picture, so what is counted is how often the picture would change.
    """
    need = max(2, int(starts_needed))
    starts, last = [], None
    for a, camera in sorted(
            (a, cam) for cam, segs
            in segments_per_camera(tracks, camera_of) for a, _b in segs):
        if camera != last:
            starts.append(a)
            last = camera
    out = []
    for i in range(len(starts) - need + 1):
        if starts[i + need - 1] - starts[i] <= window:
            out.append((starts[i], starts[i + need - 1]))
    return merged_spans(out)

def next_speaker_camera(t, per_camera, not_this,
                        memory=LISTENER_MEMORY_S):
    """Return the camera of whoever speaks next, if they are there.

    "There" means somebody on that camera was audible within the last
    *memory* seconds; otherwise it shows a person looking at a phone.
    """
    best, when = None, None
    for camera, segs in per_camera:
        if camera == not_this:
            continue
        for a, _b in segs:
            if a >= t and (when is None or a < when):
                best, when = camera, a
            if a >= t:
                break
    if best is None:
        return None
    for camera, segs in per_camera:
        if camera != best:
            continue
        if any(b > t - memory and a <= t for a, b in segs):
            return best
    return None

def boundary_near(target, sentences, clauses, near=BOUNDARY_NEAR_S,
                  far=BOUNDARY_FAR_S):
    """Return the sentence or clause boundary a cut should aim at.

    Four steps: a sentence beginning close by, a clause break close by,
    then the same two further out. Most clause breaks carry no pause.
    """
    for times, radius in ((sentences, near), (clauses, near),
                          (sentences, far), (clauses, far)):
        best = None
        for t in times or ():
            if abs(t - target) <= radius and (
                    best is None or abs(t - target) < abs(best - target)):
                best = t
        if best is not None:
            return best
    return None

def sound_dip(levels, step, target, radius=DIP_NEAR_S,
              share=DIP_LEVEL_SHARE):
    """Return the middle of the quietest stretch around *target*.

    Among the stretches under the threshold the widest wins, less half
    its distance: width alone picks a far one, nearness a narrow one.
    """
    if not levels or step <= 0 or radius <= 0:
        return None
    first = max(0, int((target - radius) / step))
    last = min(len(levels), int((target + radius) / step) + 1)
    window = levels[first:last]
    if len(window) < 3:
        return None
    ordered = sorted(window)
    low = ordered[int(0.05 * (len(ordered) - 1))]
    high = ordered[int(0.95 * (len(ordered) - 1))]
    if high <= low:
        return None
    limit = low + share * (high - low)
    best, score, i = None, None, 0
    while i < len(window):
        if window[i] > limit:
            i += 1
            continue
        j = i
        while j < len(window) and window[j] <= limit:
            j += 1
        middle = (first + (i + j) / 2.0) * step
        value = (j - i) * step - 0.5 * abs(middle - target)
        if score is None or value > score:
            best, score = middle, value
        i = j
    return best

def cut_point(target, sentences=(), clauses=(), levels=(),
              step=DIP_STEP_S):
    """Return where a cut aimed at *target* should really sit.

    The text says roughly where -- a sentence beginning or a clause
    break -- and the sound exactly where; without either, unchanged.
    """
    aim = boundary_near(target, sentences, clauses)
    if aim is None:
        aim = target
    for radius in (DIP_NEAR_S, DIP_FAR_S):
        found = sound_dip(levels, step, aim, radius)
        if found is not None:
            return found
    return aim

def wide_shot_length(start, room, sentences=(), clauses=(), holds=5.0,
                     most=15.0):
    """Return how long an inserted wide shot stands.

    At least *holds* seconds, then to the end of the sentence. Past
    *most* the last clause break below it ends the shot instead.
    """
    room = max(0.0, room)
    if room <= 0:
        return 0.0
    floor_t = start + min(holds, room)
    ceiling = start + min(max(holds, most), room)
    for t in sorted(sentences or ()):
        if t >= floor_t:
            if t <= ceiling:
                return t - start
            break
    breaks = [t for t in (clauses or ()) if floor_t <= t <= ceiling]
    if breaks:
        return max(breaks) - start
    return min(holds, room)

_LEVELS = {}

def sound_levels(path, step=DIP_STEP_S):
    """Return the loudness of every ten milliseconds of a recording.

    ffmpeg does the work: down to 8000 Hz, rectified, resampled to one
    value per step. Kept while the program runs, because the preview
    asks again on every keystroke. An empty list means the file could
    not be read, and every caller falls back to the boundary in the text.
    """
    if not path or step <= 0:
        return []
    try:
        key = (os.path.abspath(path), os.path.getmtime(path),
               os.path.getsize(path), round(step, 4))
    except OSError:
        return []
    if key in _LEVELS:
        return _LEVELS[key]
    rate = int(round(1.0 / step))
    try:
        p = subprocess.run(
            ["ffmpeg", "-v", "error", "-i", path, "-map", "a:0", "-af",
             "aresample=8000,aeval=abs(val(0)):c=same,aresample=%d" % rate,
             "-ac", "1", "-f", "s16le", "-"], capture_output=True)
    except OSError:
        return []
    data = p.stdout or b""
    if p.returncode or len(data) < 4:
        _LEVELS[key] = []
        return []
    out = list(struct.unpack("<%dh" % (len(data) // 2),
                             data[:len(data) // 2 * 2]))
    _LEVELS[key] = out
    return out

def sound_levels_for(d):
    """Return the level envelope belonging to a handover file.

    Only a recording as long as the programme itself can be used: the
    stored single tracks start where it starts, or every dip is wrong.
    """
    files = (d or {}).get("audio_files") or {}
    length = float((d or {}).get("length_s") or 0.0)
    if not files or length <= 0:
        return []
    for name in sorted(files, key=lambda n: (n != "Full-Mix", n)):
        path = files[name]
        if not path or not os.path.exists(path):
            continue
        try:
            seconds = sample_count(path) / float(SR)
        except Exception:
            continue
        if abs(seconds - length) > 2.0:
            continue
        return sound_levels(path)
    return []

# How many sentences a track must carry before its share of questions
# says anything. Under twenty it is arithmetic on nothing.
ROLE_MIN_SENTENCES = 20

def who_asks(tracks, words):
    """Rank the speakers by who does the asking -- a proposal, never more.

    The guest asks fewest questions per sentence and speaks longest, and
    that order holds; the distance varies too much for a threshold. It
    takes one voice per track, and holds the tracks against each other
    first to see that it has one. [(name, sentences, questions, speech_s)].
    """
    if not words or not tracks or len(tracks) < 2:
        return []
    # Counting per track means nothing where two of them carry the same
    # speech: the questions go to the loudest recorder, not to the asker.
    if not one_voice_each(tracks):
        return []
    held = {name: sum(b - a for a, b in segs) for name, segs in tracks}

    def talking_at(t):
        for name, segs in tracks:
            for a, b in segs:
                if a <= t < b:
                    return name
        return None

    said = {name: [0, 0] for name in held}
    for group in sentences_of(words):
        who = talking_at((group[0]["start"] + group[-1]["end"]) / 2.0)
        if who is None or who not in said:
            continue
        said[who][0] += 1
        text = (group[-1].get("word") or "").strip().rstrip(CLOSING_MARKS)
        if text.endswith("?"):
            said[who][1] += 1
    # Nothing is claimed about a track that hardly said anything.
    enough = [n for n in said if said[n][0] >= ROLE_MIN_SENTENCES]
    if len(enough) < 2:
        return []
    # Most questions per sentence first; the shorter speaking time
    # breaks a tie, because the one asking is the one talking less.
    return sorted(
        [(n, said[n][0], said[n][1], held[n]) for n in enough],
        key=lambda r: (-(r[2] / float(r[1])), r[3]))

def roles_report(order, tracks=()):
    """The proposal in words, or why there is none.

    Silence has one reason worth a line: the tracks carry each other's
    speech. Every other says nothing a person could act on.
    """
    if not order:
        if not one_voice_each(tracks):
            return [T('  Who asks -- not said here: two of the tracks carry '
                      'the same speech, so the questions would go to '
                      'whichever recorder was turned up loudest.')]
        return []
    out = [as_head(T('\nWHO ASKS -- a proposal, and nothing is set from it'))]
    for name, sentences, questions, held in order:
        out.append(T('  %-20s %s speaking, %s of %s sentences a question')
                   % (name, as_hms(held), number_text(questions, 0),
                      number_text(sentences, 0)))
    out.append(T('  The order carries, the distance between them does not: '
                 'measured over four episodes it never turned round, while '
                 'the distance between first and last changed fourfold. It '
                 'takes one voice per track; where two of them carry the '
                 'same speech nothing is said at all.'))
    return out

def is_stand_in_name(name):
    """Report whether this is a name the program made up itself.

    Either the separation's SPEAKER_00 upwards or the numbered stand-in
    the window puts in the field, in whatever language it was in.
    """
    text = (name or "").strip()
    if re.match(r"^SPEAKER_\d+$", text):
        return True
    forms = ["Speaker %d"] + [c.get("Speaker %d") for c in CATALOGUE.values()]
    for form in forms:
        if form and re.match(
                "^" + re.escape(form).replace("%d", r"\d+") + "$", text):
            return True
    return False

def voice_role_names(order):
    """Propose a name for each voice out of the ranking of who asks.

    The one who answers asks fewest questions and speaks longest, so the
    last of the ranking is the guest and the rest are named after asking.
    Too few sentences and a voice never reaches the ranking.
    """
    if len(order or ()) < 2:
        return {}
    asking = [row[0] for row in order[:-1]]
    out = {order[-1][0]: T('Guest')}
    for i, name in enumerate(asking):
        out[name] = T('Host') if len(asking) == 1 else T('Host %d') % (i + 1)
    return out

def voice_names_report(order):
    """The proposed names in words, or nothing where there is nothing."""
    named = dict((n, v) for n, v in voice_role_names(order).items()
                 if is_stand_in_name(n))
    if not named:
        return []
    out = [as_head(T('\nWHAT THE VOICES COULD BE CALLED -- a proposal'))]
    for row in order:
        if row[0] in named:
            out.append(T('  %-20s could be called %s')
                       % (row[0], named[row[0]]))
    out.append(T('  Only for voices still carrying the name the program gave '
                 'them; one somebody typed is never touched. The roles are '
                 'read off who asks and who answers, which holds for a '
                 'conversation with one guest and is a proposal, not a '
                 'setting.'))
    return out

def voice_window_order(tracks, words, offset, origin,
                       in_point="", out_point="", fps=30.0):
    """Who does the asking, worked out inside the time window alone.

    *tracks* are the voices on the shared axis, *words* the recognition
    in its own time, *offset* what moves them onto it. The window goes
    through apply_time_window, so preview and this can never disagree.
    """
    if not tracks or not words:
        return []
    length = max((b for _n, parts in tracks for _a, b in parts), default=0.0)
    if length <= 0:
        return []
    handover = {
        "speakers": [{"name": name, "sections": [list(p) for p in parts]}
                     for name, parts in tracks],
        "words": [[w["start"] + offset, w["end"] + offset, w["word"]]
                  for w in words],
        "length_s": length, "start_s": origin, "fps": fps}
    cut, complaint = apply_time_window(handover, in_point, out_point)
    if complaint:
        return []
    return who_asks(
        [(s["name"], s["sections"]) for s in cut["speakers"]],
        [speech_word(a, b, text) for a, b, text in cut["words"]])

def voice_proposals(order, labels):
    """The two proposals that follow from that ranking.

    A name for every voice that reached the ranking, "do not use" for
    every one that did not -- hardly speaking inside the window is the
    whole rule. Returns ({label: name}, [labels that hardly speak]).
    """
    if not order:
        return {}, []
    ranked = set(row[0] for row in order)
    return (voice_role_names(order),
            [label for label in labels if label not in ranked])

def voice_marks_of(state):
    """What the window remembers about its voice rows.

    Made on first use and kept over a rebuild of the table: the rows go
    and come again, and a mark going with them would overwrite an answer.
    """
    marks = state.get("voice_marks")
    if marks is None:
        marks = {"typed": set(), "said": {}, "name": {}, "camera": {}}
        state["voice_marks"] = marks
    return marks

def voice_row_marks(state, key, name_value, camera_value, field, box):
    """Note what a voice row was born with, and who answers in it.

    Only textEdited and activated say a person answered; they never fire
    for the program. *key* is recording and label together, because
    every separation calls its first voice SPEAKER_00.
    """
    marks = voice_marks_of(state)
    marks["name"].setdefault(key, name_value.get())
    marks["camera"].setdefault(key, camera_value.get())
    # The field itself, so a name already on somebody else can be
    # marked in it. Written over on every rebuild, never kept.
    marks.setdefault("field", {})[key] = field
    field.textEdited.connect(lambda *_: marks["typed"].add(key))
    box.activated.connect(lambda *_: marks["typed"].add(key))

def voice_proposal_apply(voice_lines, named, silent, marks, source=""):
    """Fill the fields that still carry what the program put there.

    A field belongs to the program while it holds what the row was born
    with or the last proposal, and stops the moment somebody answers --
    typing the stand-in back by hand counts. *source* keeps out the rows
    of other recordings; returns the labels that changed.
    """
    typed = marks.get("typed") or set()
    said = marks.setdefault("said", {})
    born = marks.get("name") or {}
    first = marks.get("camera") or {}
    moved = []
    for key, name_value, camera_value in voice_lines_here(voice_lines,
                                                          source):
        label = voice_key_parts(key)[1]
        if key in typed:
            continue
        text = name_value.get().strip()
        if not (is_stand_in_name(text) or text == said.get(key)):
            continue
        want = named.get(label) or born.get(key) or text
        # Never onto a name somebody else already carries: a proposal
        # making two voices one person is worse than none.
        if want in set(nv.get().strip()
                       for k, nv, _c in voice_lines if k != key):
            want = text
        if want != text:
            if named.get(label):
                said[key] = want
            else:
                said.pop(key, None)
            name_value.set(want)
            moved.append(label)
        picked, was = camera_value.get(), first.get(key)
        if label in silent:
            if picked == was and picked != IGNORE_AUDIO:
                camera_value.set(IGNORE_AUDIO)
                print(T('  %s hardly speaks inside the time window -- '
                        'proposed: do not use.') % label)
                moved.append(label)
        elif picked == IGNORE_AUDIO and was not in (None, IGNORE_AUDIO):
            camera_value.set(was)
            moved.append(label)
    return moved

def voice_axis_offset(state, assign_lines):
    """Where the separated recording lies on the shared axis.

    The separation and the words are both stored in the raw time of
    that one recording, so both have the same distance to travel.
    """
    axis = state.get("axis") or {}
    starts = [audio_start_of(row[0], axis) or 0.0
              for row, _nv, cv in assign_lines
              if cv.get() != IGNORE_AUDIO and os.path.exists(row[0])]
    source = state.get("speakers_source") or ""
    return (audio_start_of(source, axis) or 0.0) - min(starts or [0.0])

def voice_suggest_round(state, voice_lines, assign_lines, camera_lines,
                        in_point, out_point, language="", heard=None):
    """One round of the proposals, on the wait the preview runs on.

    A moved In point, a renamed voice and a changed camera all reach it
    and none costs a measurement. A voice set to "do not use" by hand
    stays out of the ranking for good; one the program put there does not.
    """
    if not (state.get("speakers_local") and state.get("speakers_source")):
        return []
    spoken = words_of_recording(state, state.get("speakers_source") or "")
    if spoken is None:
        speech_words_kick_off(state, language, heard)
        return []
    marks = voice_marks_of(state)
    # Of this recording's rows, in this recording's labels: another
    # recording's SPEAKER_00 says nothing about these passages.
    source = state.get("speakers_source") or ""
    by_hand = set(voice_key_parts(k)[1]
                  for k, _nv, cv in voice_lines_here(voice_lines, source)
                  if cv.get() == IGNORE_AUDIO and k in marks["typed"])
    offset = voice_axis_offset(state, assign_lines)
    tracks, length = speakers_on_window_axis(
        voices_in_use(state["speakers_local"], by_hand), offset)
    if not tracks:
        return []
    origin = choose_zero_point(
        [audio_start_of(row[0], state.get("axis") or {})
         for row, _nv, cv in assign_lines
         if cv.get() != IGNORE_AUDIO and os.path.exists(row[0])],
        [camera_start_of(b) for b, _n, _own, _flag in camera_lines], length)
    order = voice_window_order(tracks, spoken, offset, origin,
                               in_point, out_point)
    named, silent = voice_proposals(order, [k for k, _p in tracks])
    return voice_proposal_apply(voice_lines, named, silent, marks, source)

# When two microphones can still be told apart: the share of the shorter
# one's speech that also falls inside the longer one. Above what talking
# at once produces, below what two clip-ons in one room share.
VOICE_TRACK_TOGETHER = 0.40

# How far the best microphone must be ahead of the second, as a share of
# the voice's own speech. Between the distance a right match keeps and
# the one a wrong match -- off the axis, no microphone -- ever reaches.
VOICE_TRACK_MARGIN = 0.40

# Under this much speech a voice says nothing about a microphone: below
# it the distance between the microphones collapses.
VOICE_MIN_SPEECH_S = 20.0

# How far the best microphone must stand ahead of the second once the
# recording level is out, in dB. Over a full interview the three margins
# were 6.0, 6.6 and 8.4 dB, so this refuses only a coin toss.
VOICE_LEVEL_MARGIN_DB = 1.0

def shared_seconds(one, other):
    """How long both of these lists of passages are running at once."""
    out, j = 0.0, 0
    other = sorted(other)
    for a, b in sorted(one):
        while j < len(other) and other[j][1] <= a:
            j += 1
        k = j
        while k < len(other) and other[k][0] < b:
            out += max(0.0, min(b, other[k][1]) - max(a, other[k][0]))
            k += 1
    return out

def one_voice_each(tracks):
    """Whether these lists of passages can be one voice apiece.

    Where clip-on microphones hear each other, every track carries the
    whole conversation and per-track counting lands on the loudest
    recorder. Measured as the shorter one's share inside the longer.
    """
    rows = list(tracks or ())
    for i, (_name, one) in enumerate(rows):
        for _other, two in rows[i + 1:]:
            floor = min(sum(b - a for a, b in one),
                        sum(b - a for a, b in two))
            if shared_seconds(one, two) > VOICE_TRACK_TOGETHER * floor:
                return False
    return True

def which_microphone(voices, tracks):
    """Match each separated voice to the microphone it was speaking into.

    Both are [(name, [(a, b), ...])] on one axis; returns [(voice,
    track, share, distance)] or []. A voice under a track's own name
    would claim it twice. Clip-ons are held against each other first.
    """
    own = set(name for name, _segs in tracks or ())
    voices = [(name, segs) for name, segs in voices or ()
              if name not in own]
    if len(voices) < 2 or len(tracks or ()) < 2:
        return []
    held = {name: sum(b - a for a, b in segs) for name, segs in tracks}
    if min(held.values()) <= 0:
        return []
    if not one_voice_each(tracks):
        return []
    picked = []
    for name, segs in voices:
        spoken = sum(b - a for a, b in segs)
        if spoken < VOICE_MIN_SPEECH_S:
            continue
        share = sorted(((shared_seconds(segs, t) / spoken, m)
                        for m, t in tracks), reverse=True)
        if share[0][0] - share[1][0] < VOICE_TRACK_MARGIN:
            continue
        picked.append((name, share[0][1], share[0][0],
                       share[0][0] - share[1][0]))
    # One microphone, one person: where two voices point at the same
    # one, neither is the answer -- one person cut in two, or two on
    # one microphone, and both mean this cannot name them.
    twice = set(t for i, (_, t, _s, _d) in enumerate(picked)
                for _n, u, _s2, _d2 in picked[i + 1:] if t == u)
    return [row for row in picked if row[1] not in twice]

def voices_by_level(voices, names, level, block=0.1, begin=0.0,
                    margin=VOICE_LEVEL_MARGIN_DB):
    """Name each separated voice after the microphone it spoke into.

    The voice says *when*, the microphones *who*. *level* is
    [microphone][block], *begin* where block zero sits. Not the loudest:
    a speaker stood louder in his neighbour's (-47.2 dB) than his own
    (-47.4 dB), 11 dB apart. Each microphone's mean out fixes that.
    """
    rows = [(name, list(segs)) for name, segs in (voices or ()) if segs]
    names = list(names or ())
    if len(rows) < 2 or len(names) < 2 or len(rows) > len(names):
        return []
    level = np.asarray(level, dtype=np.float64)
    if level.ndim != 2 or level.shape[0] != len(names) or not level.shape[1]:
        return []
    # Each microphone's own noise floor is the bottom of its column, or
    # a digitally silent track would drag its mean to minus infinity.
    floor = []
    for row in level:
        present = row[row > 0]
        floor.append(float(np.percentile(present, 20)) if len(present)
                     else 1e-7)
    table = []
    for _name, segs in rows:
        wanted = np.zeros(level.shape[1], dtype=bool)
        for a, b in segs:
            i = max(0, int(round((a - begin) / block)))
            j = min(level.shape[1], int(round((b - begin) / block)))
            if j > i:
                wanted[i:j] = True
        if not wanted.any():
            return []
        table.append([20.0 * math.log10(max(float(np.median(level[m][wanted])),
                                            floor[m], 1e-12))
                      for m in range(len(names))])
    # One number per microphone out of its own column: after this a
    # recorder turned up louder shifts nothing, only distance is left.
    middle = [sum(row[m] for row in table) / float(len(table))
              for m in range(len(names))]
    picked = []
    for (name, _segs), row in zip(rows, table):
        order = sorted(((row[m] - middle[m], names[m])
                        for m in range(len(names))), reverse=True)
        ahead = order[0][0] - order[1][0]
        if ahead >= margin:
            picked.append((name, order[0][1], round(order[0][0], 2),
                           round(ahead, 2)))
    # One microphone, one person -- which_microphone's rule. Where two
    # voices land on one, saying nothing beats naming an episode wrongly.
    twice = set(t for i, (_n, t, _l, _d) in enumerate(picked)
                for _n2, u, _l2, _d2 in picked[i + 1:] if t == u)
    return [row for row in picked if row[1] not in twice]

def microphones_report(rows):
    """The proposal in words, or nothing where there is nothing to say."""
    if not rows:
        return []
    out = [as_head(T('\nWHICH MICROPHONE -- a proposal, and nothing is set '
                     'from it'))]
    for voice, track, share, distance in rows:
        out.append(T('  %-20s sounds like %-20s %s %% of it inside that '
                     'track, %s points ahead of the next')
                   % (voice, track, number_text(round(100 * share), 0),
                      number_text(round(100 * distance), 0)))
    out.append(T('  It holds under one assumption: one microphone per '
                 'person, and each of them carrying only that person. '
                 'Where the tracks overlap too much to be told apart, or '
                 'two voices point at the same microphone, nothing is said '
                 'at all rather than something uncertain.'))
    return out

def reaction_cuts(tracks, words, camera_of, gap=3.0, holds=0.7,
                  over=10.0, tally=None, ends=None):
    """Return {when the answer begins: who answers} for every question.

    *ends* takes {answer begins: question ended}; the lead counts from
    the second. The picture goes to whoever answers, but only where the
    asker is not the main speaker, somebody starts within *gap* and holds
    *holds* of the next *over*, and the two are not on one camera.
    """
    out = {}
    stopped = {} if ends is None else ends
    counted = {} if tally is None else tally
    for key in ("questions", "used", "no_asker", "asked_by_main",
                "no_answer", "did_not_hold", "same_camera"):
        counted.setdefault(key, 0)
    if not words or not tracks:
        return out
    held = {n: sum(b - a for a, b in segs) for n, segs in tracks}
    if len(held) < 2:
        return out
    main = max(held, key=held.get)
    entries = sorted((a, n) for n, segs in tracks for a, _b in segs)

    def talking_at(t):
        for name, segs in tracks:
            for a, b in segs:
                if a <= t < b:
                    return name
        return None

    for group in sentences_of(words):
        last = group[-1]
        text = (last.get("word") or "").strip().rstrip(CLOSING_MARKS)
        if not text.endswith("?"):
            continue
        counted["questions"] += 1
        end = last["end"]
        asker = talking_at((group[0]["start"] + end) / 2.0)
        if asker is None:
            counted["no_asker"] += 1
            continue
        if asker == main:
            counted["asked_by_main"] += 1
            continue
        answer = None
        for a, n in entries:
            if a < end:
                continue
            if a > end + gap:
                break
            if n != asker:
                answer = (a, n)
                break
        if not answer:
            counted["no_answer"] += 1
            continue
        when, who = answer
        spoken = sum(max(0.0, min(b, when + over) - max(a, when))
                     for n, segs in tracks if n == who for a, b in segs)
        if over > 0 and spoken < holds * over:
            counted["did_not_hold"] += 1
            continue
        if camera_of.get(who) and camera_of.get(who) == camera_of.get(asker):
            counted["same_camera"] += 1
            continue
        out[when] = who
        stopped[when] = end
        counted["used"] += 1
    return out

def question_report(rules):
    """What the reaction cut found and what it let go, in one or two lines.

    A rule that quietly does nothing looks like a rule that is broken.
    A question is dropped without a transcript, where the main speaker
    asked it, where asker and answerer share a camera, or where nobody
    took over in time; the numbers say which. "" where it is switched off.
    """
    if (rules.get("on_question") or SHOT_OFF) == SHOT_OFF:
        return ""
    if not rules.get("words"):
        return T('  Question: no transcript, so no question was found and '
                 'no reaction cut\n            happened. The words are '
                 'written down from the finished mix during\n            '
                 'the run; without them the setting does nothing.')
    counted = rules.get("question_tally") or {}
    out = [T('  Question: %s in the transcript, %s became a reaction cut.')
           % (number_text(counted.get("questions") or 0, 0),
              number_text(counted.get("used") or 0, 0))]
    reasons = ((counted.get("asked_by_main"),
                T('the main speaker asked')),
               (counted.get("same_camera"),
                T('asker and answerer on one camera')),
               (counted.get("no_answer"),
                T('nobody answered in time')),
               (counted.get("did_not_hold"),
                T('the answer did not keep the floor')),
               (counted.get("no_asker"),
                T('nobody was speaking at the question')))
    named = ["%d %s" % (int(n), why) for n, why in reasons if n]
    if named:
        out.append(T('  Not used:  %s.') % ", ".join(named))
    return "\n".join(out)

def cut_rules(**over):
    """Return the settings the cut rules read, with their defaults.

    One dict rather than a dozen parameters: the same seven rules are
    read in three places, and a keyword overrides one of them.
    """
    out = {"min_speech": MIN_SPEECH_TO_SWITCH_S,
           "on_monologue": SHOT_ALTERNATE,
           "on_together": SHOT_WIDE,
           "on_uncertain": SHOT_WIDE,
           # The wide shot, as it always was. A setting that moves the
           # cut of every project already made belongs to whoever cuts.
           "on_silence": SHOT_WIDE,
           "silence_hold": SILENCE_HOLD_S,
           "on_question": SHOT_ANSWER,
           "reaction_lead": 1.5,
           "reaction_gap": 3.0,
           "reaction_hold": 0.7,
           "reaction_over": 10.0,
           # None means: whatever the caller passed as the wide shot
           # length. Two ways of saying it would let preview and run part.
           "wide_holds": None,
           "wide_most": 15.0,
           "words": (),
           "levels": (),
           "level_step": DIP_STEP_S}
    out.update(over)
    return out

def rules_from_settings(args):
    """Read the cut rules out of the command line settings.

    The choices come out of CUT_CHOICES rather than being named again
    here: two lists of the same names drift apart.
    """
    picked = {}
    for switch, _caption, default_value, _values, _k, _l in CUT_CHOICES:
        field = switch.replace("-", "_")
        picked[field] = getattr(args, field, None) or default_value
    return cut_rules(
        min_speech=float(getattr(args, "min_speech_to_switch",
                                 MIN_SPEECH_TO_SWITCH_S)),
        reaction_lead=float(getattr(args, "reaction_lead", 1.5)),
        reaction_gap=float(getattr(args, "reaction_gap", 3.0)),
        reaction_hold=float(getattr(args, "reaction_hold", 0.7)),
        wide_holds=float(getattr(args, "wide_length", 5.0)),
        wide_most=float(getattr(args, "wide_most", 15.0)),
        silence_hold=float(getattr(args, "silence_hold", SILENCE_HOLD_S)),
        **picked)

def rules_from_cut_box(number, chosen):
    """Read the cut rules out of what the cut box in the window holds.

    *number* is {switch: number} over CUT_FIELDS, *chosen* {switch:
    value} over CUT_CHOICES. Beside rules_from_settings: a rule the
    window offers and the run does not is a cut nobody can make.
    """
    return cut_rules(
        min_speech=number["min-speech-to-switch"],
        reaction_lead=number["reaction-lead"],
        wide_holds=number["wide-length"],
        wide_most=number["wide-most"],
        silence_hold=number["silence-hold"],
        **{k.replace("-", "_"): chosen[k]
           for k, _c, _d, _v, _s, _l in CUT_CHOICES})

# How long one camera may hold before the picture looks away. It sets
# how restless the cut feels, not whether it is right.
WIDE_AFTER_S = 70.0

def insert_wide_shots(cut, tracks, wide_shot, after, duration, min_len,
                      at_latest, camera_of=None, rules=None):
    """Break up long shots by leaving the speaker for a while.

    A shot holding longer than *after* opens at a sentence boundary
    nearby, the point from the sound; what shows is the "Long monologue"
    choice. It stands *duration* seconds at least; *at_latest* forces.
    """
    rules = rules or cut_rules()
    words = rules.get("words") or ()
    sentences = sentence_start_times(words) if words else []
    clauses = clause_break_times(words) if words else []
    levels = rules.get("levels") or ()
    step = rules.get("level_step") or DIP_STEP_S
    holds = float(rules.get("wide_holds") or duration)
    most = float(rules.get("wide_most") or 15.0)
    show = rules.get("on_monologue") or SHOT_WIDE
    if show == SHOT_HOLD:
        return list(cut)
    per_camera = segments_per_camera(tracks, camera_of or {})
    pauses, _entries = find_pauses(tracks)

    def picture(t, who, shown):
        """Return which camera the break shows, and remember it."""
        listener = (next_speaker_camera(t, per_camera, who)
                    if show in (SHOT_LISTENER, SHOT_ALTERNATE) else None)
        if show == SHOT_LISTENER:
            choice = listener or wide_shot
        elif show == SHOT_ALTERNATE:
            # Alternating needs a memory: without it the same camera
            # comes up again by chance and it is not alternation.
            turns = [wide_shot] + ([listener] if listener else [])
            choice = turns[len(shown) % len(turns)]
        else:
            choice = wide_shot
        shown.append(choice)
        return choice

    def split_up(a, b, who, shown, depth=0):
        if depth > 12 or b - a <= after:
            return [(a, b, who)]
        first, last = a + min_len, b - min_len - holds
        if last <= first:
            return [(a, b, who)]
        wanted = a + min(after, (b - a) / 2.0)
        t = None
        if sentences or clauses:
            aim = cut_point(wanted, sentences, clauses, levels, step)
            if first <= aim <= last:
                t = aim
        if t is None:
            # No usable boundary: the longest pause nearby, else the clock.
            points = [(p[0] + min(0.3, (p[1] - p[0]) / 2.0), p[1] - p[0])
                      for p in pauses if p[0] >= a and p[1] <= b]
            points = [(x, g) for x, g in points if first <= x <= last]
            if not points and b - a > at_latest:
                parts = int((b - a) // at_latest) + 1
                stride = (b - a) / parts
                points = [(a + stride * i, 0.0) for i in range(1, parts)]
                points = [(x, g) for x, g in points if first <= x <= last]
            if not points:
                return [(a, b, who)]
            t = max(points, key=lambda xg: (
                3.0 * min(xg[1], 2.0)
                - abs(xg[0] - wanted) / max(1.0, after) * 1.5))[0]
            t = cut_point(t, (), (), levels, step)
            t = min(max(t, first), last)
        length = wide_shot_length(t, b - min_len - t, sentences, clauses,
                                  holds, most)
        if length <= 0:
            return [(a, b, who)]
        seen = picture(t, who, shown)
        if seen == who:
            return [(a, b, who)]
        return (split_up(a, t, who, shown, depth + 1)
                + [(t, t + length, seen)]
                + split_up(t + length, b, who, shown, depth + 1))

    result = []
    for a, b, who in cut:
        if who == wide_shot or b - a <= after:
            result.append((a, b, who))
        else:
            result += split_up(a, b, who, [])
    return merge_adjacent(result)

def merge_adjacent(cut):
    """Merge two identical consecutive shots into one."""
    extra = []
    for a, b, who in cut:
        if extra and extra[-1][2] == who:
            extra[-1] = (extra[-1][0], b, who)
        else:
            extra.append((a, b, who))
    return [tuple(x) for x in extra]

# How long somebody may pause and still hold the floor: below this a
# gap is a breath, above it the next person may come in.
FLOOR_HOLD_GAP_S = 2.0

def floor_handovers(tracks, main_speaker, min_len_speech,
                    gap=FLOOR_HOLD_GAP_S):
    """Return where somebody other than the main speaker holds the floor.

    A single speech block only says the source drew a boundary there.
    The blocks of one person are chained across short gaps, and a chain
    counts where its speaker holds most of it. [(from, to), ...].
    """
    own = {}
    for n, segs in tracks:
        own.setdefault(n, []).extend(segs)
    out = []
    for n, segs in own.items():
        if n == main_speaker:
            continue
        chains = []
        for a, b in sorted(segs):
            if chains and a - chains[-1][1] <= gap:
                chains[-1][1] = max(chains[-1][1], b)
                chains[-1][2] += b - a
            else:
                chains.append([a, b, b - a])
        for a, b, spoke in chains:
            spoke = min(spoke, b - a)
            if spoke < min_len_speech:
                continue
            rivals = sum(max(0.0, min(b, y) - max(a, x))
                         for other_name, parts in own.items()
                         if other_name != n for x, y in parts)
            if rivals >= spoke:
                continue
            out.append((a, b))
    return sorted(out)

def wide_shot_at_edges(cut, tracks, wide_shot, min_len_speech=4.0,
                   faint=False):
    """Hold the wide shot while the round is introduced and closed.

    Someone introduces the participants at the start and says goodbye at
    the end; both belong in the wide frame. The opening ends where the
    floor first changes hands away from the main speaker, and the same
    rule runs backwards. A voice the separation never hears cannot end it.
    """
    if not cut:
        return cut
    speech_time = {n: sum(b - a for a, b in segs) for n, segs in tracks}
    if len(speech_time) < 2:
        return cut
    main_speaker = max(speech_time, key=speech_time.get)
    other = floor_handovers(tracks, main_speaker, min_len_speech)
    if not other:
        return cut
    begin, end = cut[0][0], cut[-1][1]
    until, from_s = other[0][1], other[-1][0]
    if until - begin > (end - begin) / 3.0 or end - from_s > (end - begin) / 3.0:
        # A third would no longer be a greeting but a conversation.
        if not faint:
            print(T('  Wide shot at the edges: skipped -- the first or '
                    'last announcement\n  would be too long for a greeting.'))
        return cut
    out = []
    for a, b, who in cut:
        if b <= until or a >= from_s:
            out.append((a, b, wide_shot))
        elif a < until < b:
            out += [(a, until, wide_shot), (until, b, who)]
        elif a < from_s < b:
            out += [(a, from_s, who), (from_s, b, wide_shot)]
        else:
            out.append((a, b, who))
    if not faint:
        print(T('  Wide shot at the edges: until %s and from %s') % (as_hms(until - begin),
                                                      as_hms(from_s - begin)))
    return merge_adjacent(out)

def metrics_sentence(numbers, colours, minutes_fn):
    """Build the summary line under the preview.

    How much speech time lands on the speaker's own camera, how much on
    the wide shot, how much on the wrong one -- the last in warning red.
    """
    return (T("<span style='color:%(t)s'><b>%(n)d shots</b>, median "
              '%(med).1f s, shortest %(short).1f s, longest camera '
              '%(long).0f s</span>. Speech time: <b>%(own).1f %%</b> on '
              'their own camera (%(own_t)s), %(wide).1f %% on the wide '
              "shot (%(wide_t)s), <span style='color:%(warn)s'>at "
              "%(off).1f %% (%(off_t)s) the speaker's camera is not "
              'active</span>')
            % {"t": colours["heading"], "warn": colours["warning"],
               "n": numbers["shots"], "med": numbers["median"],
               "short": numbers["shortest"], "long": numbers["longest_camera"],
               "own": numbers["in_frame"], "own_t": minutes_fn(numbers["in_frame_s"]),
               "wide": numbers["on_wide"], "wide_t": minutes_fn(numbers["on_wide_s"]),
               "off": numbers["off_camera"],
               "off_t": minutes_fn(numbers["off_camera_s"])})

def speech_heading(own_measure_measured, total_sum=""):
    """Return the heading for the speech segment table.

    Three answers, not two. Levels measured against each other are
    coarser than voices taken apart, and both are coarser than a finished
    run, which had the tracks on one axis and de-bled. Whoever judges the
    preview needs to know which of the three they see.
    """
    if own_measure_measured == "run":
        source_text = T('Speakers, as the run measured them')
    elif own_measure_measured:
        source_text = T('Speakers, self-measured from the tracks')
    else:
        source_text = T('Speakers, separated by voice')
    if not total_sum:
        return source_text
    return T('%s (%s) -- talking at once counts twice') % (
        source_text, total_sum)

def warn_box(QtWidgets, parent, title, text):
    """Show a warning, and write it down before it is clicked away.

    A box is gone as soon as somebody presses the button. One place does
    both, so a new warning cannot be shown without being kept.
    """
    trouble_log("%s -- %s" % (title, text))
    QtWidgets.QMessageBox.warning(parent, title, text)

def label_say(widget, text, colour):
    """Put one line into a label, in the colour that grades it."""
    widget.setText(text)
    widget.setStyleSheet("color: %s" % colour)
    if colour == COLOURS["error"]:
        trouble_log(text)

def cut_basis_line(basis, speakers, length):
    """Say what the cut on the third tab stands on, and in what colour.

    Three answers, and not worth the same: the recordings as they lie,
    a finished run on one axis, and with auphonic.com de-bled as well.
    """
    if basis == "auphonic":
        text = T('from the processed Auphonic tracks -- %s speakers, %s')
    elif basis == "run":
        text = T('from the finished run -- %s speakers, %s')
    else:
        text = T('measured from the recordings -- %s speakers, %s')
    return (text % (number_text(speakers, 0), as_hms(length)),
            COLOURS["good" if basis in ("run", "auphonic") else "warning"])

def project_opened_note(target):
    """The note in the log after a project was opened, and what to do next."""
    return T('PROJECT OPENED\n  All entries are back, nothing has been '
             'computed in this session.\n  The output folder holds the '
             'files of the last run:\n  %s\n\n  Three ways from here:\n   '
             ' • below "Open result folder" -- look at the files from '
             'that run,\n    • below "Create Resolve project" -- from '
             "that run's handover file,\n      without computing "
             'anything again,\n    • above "Start" -- compute '
             'everything again and overwrite the files.\n') % target

def projects_beside(paths, deep=40):
    """The project files lying with this material, newest first.

    Looked for in the folders the material is in and one level below,
    since the project file goes into the output folder. Not deeper: a
    search over the whole disk would stand in the way of adding a file.
    Gives (path, when) pairs, each path once.
    """
    folders = []
    for one in paths:
        folder = os.path.dirname(os.path.abspath(one))
        if folder not in folders:
            folders.append(folder)
    look = list(folders)
    for folder in folders:
        # Counted by folders, not by names: a recording folder holds
        # hundreds of files, the output folder anywhere among them.
        count = 0
        try:
            names = sorted(os.listdir(folder))
        except OSError:
            continue
        for name in names:
            full = os.path.join(folder, name)
            if full in look or not os.path.isdir(full):
                continue
            look.append(full)
            count += 1
            if count >= deep:
                break
    found = {}
    for folder in look:
        # One attempt for the whole folder, not one per file: a folder
        # nobody can read holds no project file anybody can open.
        try:
            for name in os.listdir(folder):
                if (name.startswith(PROJECT_PREFIX)
                        and name.lower().endswith(".json")):
                    full = os.path.join(folder, name)
                    found[full] = os.path.getmtime(full)
        except OSError:
            continue
    return sorted(found.items(), key=lambda pair: -pair[1])

def when_written(when):
    """When a file was written, short enough to stand in a list."""
    return time.strftime("%Y-%m-%d %H:%M", time.localtime(when))

def project_offer(QtWidgets, window, state, paths, ask, load):
    """Offer a project file lying with the material; never load it silently.

    Asked once per file found; the project is opened whole or not at
    all, and once one is open nothing more is offered. Returns whether
    one was opened -- the caller must not then rebuild the list.
    """
    if state.get("project_from"):
        return False
    seen = state.setdefault("projects_offered", set())
    found = [(one, when) for one, when in projects_beside(paths)
             if one not in seen]
    if not found:
        return False
    seen.update(one for one, _ in found)
    whole = T('Everything comes back from it: names, separation, assignment, '
              'types, the time window. The list of files is replaced by the '
              'one the project holds.')
    if len(found) == 1:
        one, when = found[0]
        if ask(T('Project found'),
               T('A project file lies with this material:\n\n  %s\n  '
                 'written %s\n\n%s')
               % (os.path.basename(one), when_written(when), whole),
               T('Open the project')):
            load(one)
            return True
        return False
    lines = ["%s   (%s)" % (os.path.basename(one), when_written(when))
             for one, when in found]
    picked, chosen = QtWidgets.QInputDialog.getItem(
        window, T('Project found'),
        T('Several project files lie with this material. Which one?\n\n%s')
        % whole, lines, 0, False)
    if chosen and picked in lines:
        load(found[lines.index(picked)][0])
        return True
    return False

def find_project_file(file_path):
    """Find the project file for whatever was pointed at.

    Pointing at the folder, or at the wrong file in it, should not
    produce an error, so the neighbourhood is searched too. A project
    file is a dict containing "files" -- the name alone is not enough,
    since plenty of files end in json. Returns (contents, path).
    """
    if not file_path:
        return None, ""
    folder = file_path if os.path.isdir(file_path) else os.path.dirname(file_path)
    attempts = [] if os.path.isdir(file_path) else [file_path]
    try:
        attempts += sorted(os.path.join(folder, n) for n in os.listdir(folder)
                           if n.startswith(PROJECT_PREFIX)
                           and n.lower().endswith(".json"))
    except OSError:
        pass
    for attempt in attempts:
        try:
            with open(attempt, encoding="utf-8") as f:
                loaded = json.load(f)
        except (OSError, ValueError):
            continue
        if isinstance(loaded, dict) and "files" in loaded:
            return loaded, attempt
    return None, ""

def project_files(d):
    """Split the project's file list into what is still there and what is not.

    Returns ([(path, kind), ...], [missing names]). Vanished files are named
    rather than silently dropped.
    """
    present, missing = [], []
    for entry in ((d or {}).get("files") or []):
        file_path = entry.get("path")
        if not file_path:
            continue
        if os.path.exists(file_path):
            present.append((file_path, entry.get("kind") or "audio"))
        else:
            missing.append(os.path.basename(file_path))
    return present, missing

def choose_zero_point(audio_origin=(), camera_origin=(), length=0.0):
    """Return where programme time starts on the clock.

    Speaker segments count from the audio recordings, not the cameras.
    Nothing is guessed: without a known audio start the earliest camera
    applies, and without that, None. A clock never set is no origin.
    """
    audio_files = [float(t) for t in audio_origin if t is not None]
    videos = [float(t) for t in camera_origin if t is not None]
    if length and (audio_files or videos):
        apart = clocks_apart(
            [(t, length, ("audio", i)) for i, t in enumerate(audio_files)]
            + [(t, length, ("camera", i))
               for i, t in enumerate(videos)])[0]
        audio_files = [t for i, t in enumerate(audio_files)
                       if ("audio", i) not in apart]
        # The cameras are the fallback, and where every one stands alone
        # there is no shared time to be had; the earliest start is left.
        videos = [t for i, t in enumerate(videos)
                  if ("camera", i) not in apart] or videos
    if audio_files:
        return min(audio_files)
    return min(videos) if videos else None

def cameras_frame_rate(cameras):
    """The rate the cut has to be read at, measured on a camera.

    The frames of a timecode are frames, so one read at the wrong rate
    lands whole frames out and the picture runs ahead of the sound on
    every camera whose timecode has a frame part. Cameras ending :00 are
    exact either way, which is how this sits unseen.
    """
    for cam in cameras or ():
        path = cam.get("file") or ""
        if path and os.path.exists(path):
            rate = picture_rate(ffprobe_json(path))
            if rate:
                return float(rate)
    return 0.0

def build_handover(segment_list, length, assignment, cameras, audio_origin=(),
                    camera_origin=(), places=()):
    """Build the handover from segments and the assignment.

    No window, no file: parsed segments and the assignment go in, the
    handover the run writes comes out. *cameras* are dicts of track,
    file, start_s and wide_marked. (handover, "") or (None, reason).
    """
    if not segment_list or not length or length <= 0:
        return None, (T('No speakers known yet -- nothing measured, '
                        'nothing separated, and no handover file of an '
                        'earlier run in %s or its subfolders.')
                      % (T(' and ').join([x for x in places if x])
                         or T('no folder')))
    if not cameras:
        return None, (T('No cameras assigned yet -- switch Multitrack on '
                        'to do that.'))
    out = []
    for cam in cameras:
        short = os.path.basename(cam.get("file") or "")
        # The camera audio arrives through the assignment already, and
        # sorted, because write_handover builds the same list by name.
        who = sorted(n for n, target in assignment.items() if target == short)
        out.append({"track": cam.get("track"), "file": cam.get("file"),
                     "speakers": who,
                     "start_s": cam.get("start_s"),
                     "wide_marked": bool(cam.get("wide_marked")),
                     "wide": bool(cam.get("wide_marked")) or not who})
    return ({"speakers": [{"name": n,
                           "sections": [list(x) for x in segs]}
                          for n, segs in segment_list],
             "cameras": out, "length_s": length,
             "fps": cameras_frame_rate(cameras),
             "start_s": choose_zero_point(audio_origin, camera_origin,
                                          length)}, "")

def apply_time_window(d, in_point, out_point):
    """Apply the In point and the Out point to an already written handover.

    The speaker times count from the start of the window in force at the
    time; start_s says where that was, so a new setting converts without
    measuring again. With a complaint the handover comes back untrimmed.
    """
    if not (in_point or "").strip() and not (out_point or "").strip():
        return d, ""
    length = float(d.get("length_s") or 0.0)
    origin = d.get("start_s")
    fps = max(1.0, float(d.get("fps") or 30.0))

    def compute(value_text, from_the_end):
        value, absolute = parse_time_point(value_text, fps)
        if value is None:
            return None
        if absolute:
            if origin is None:
                return None
            return value - float(origin)
        if value < 0 and not from_the_end:
            raise ValueError(value_text)
        return (length + value) if value < 0 else value

    try:
        from_s = compute(in_point, False) if (in_point or "").strip() else 0.0
        until = compute(out_point, True) if (out_point or "").strip() else length
    except ValueError as e:
        # The same rule as in the run: a negative value counts from the end
        # and only works for Out point. Anything else is not a time at all.
        text = str(e)
        if text == (in_point or "").strip():
            return d, T('%r counts from the end -- that only works '
                        'for Out point.') % text
        return d, T('In point or Out point cannot be read here.')
    if from_s is None or until is None:
        return d, T('In point or Out point cannot be read here.')
    # Trimmed to the material first, judged afterwards: the other way
    # round, a window past the end of the material passes as a positive
    # length and trimming turns it negative, with an empty complaint.
    asked_from, asked_until = from_s, until
    from_s, until = max(0.0, from_s), min(length, until)
    if length > 0 and (asked_from >= length or asked_until <= 0):
        return d, (T('The time window lies outside the material: In '
                     'point at %s, Out point at %s, and the material '
                     'runs %s.')
                   % (as_hms(asked_from), as_hms(asked_until),
                      as_hms(length)))
    if until - from_s < 5:
        return d, T('Out point lies less than 5 seconds after In point.')
    fresh = dict(d)
    fresh["length_s"] = round(until - from_s, 3)
    # The origin moves along: start_s is where programme time starts on
    # the clock, and after trimming that is In point, not the old value.
    if origin is not None:
        fresh["start_s"] = round(float(origin) + from_s, 3)
        # And the timecode with it. Resolve places by this field alone,
        # so one standing still puts every frame out by the removed head.
        if d.get("start_tc"):
            fresh["start_tc"] = timecode_string(fresh["start_s"], fps)
    fresh["speakers"] = [
        {"name": s.get("name"),
         "sections": [[max(0.0, a - from_s), min(until, b) - from_s]
                        for a, b in (s.get("sections") or [])
                        if b > from_s and a < until]}
        for s in (d.get("speakers") or [])]
    # The words move with them, or every sentence boundary sits as far
    # out as the removed head is long, and the cut points follow.
    if d.get("words"):
        fresh["words"] = [[a - from_s, b - from_s, text]
                          for a, b, text in d["words"]
                          if b > from_s and a < until]
    # And so do the cameras. A camera's offset counts against programme
    # time, and that now starts at In point; left standing, picture and
    # sound sit the removed head apart. A start_s of its own is right.
    if d.get("cameras"):
        fresh["cameras"] = [
            dict(cam, offset=round(float(cam["offset"]) - from_s, 4))
            if cam.get("offset") is not None else cam
            for cam in d["cameras"]]
    return fresh, ""

def as_minutes(seconds):
    """Format seconds as "3:34 min", short enough to sit inside a sentence.

    Only ever shown on screen, never written into a file, so it may be
    translated.
    """
    s = int(round(max(0.0, seconds)))
    return T("%s:%02d min") % (number_text(s // 60, 0), s % 60)

def speaker_statistics(d):
    """Return who speaks how much and how often.

    Same source as the cut: the handover file or the Auphonic statistics.
    Without them a share of wide shot cannot be judged.
    """
    out, total = [], 0.0
    for speaker in (d.get("speakers") or []):
        segs = [tuple(x) for x in (speaker.get("sections") or [])]
        total_sum = sum(b - a for a, b in segs)
        total += total_sum
        out.append({"name": speaker.get("name") or T('Track'), "seconds": total_sum,
                     "blocks": len(segs),
                     "mean": (total_sum / len(segs)) if segs else 0.0,
                     "longest_one": max((b - a for a, b in segs), default=0.0)})
    for e in out:
        e["share"] = 100.0 * e["seconds"] / (total or 1.0)
    out.sort(key=lambda e: -e["seconds"])
    # Silence: whatever is left when the speech blocks of all speakers
    # are laid on top of each other, so two at once count once here.
    every = sorted((a, b) for speaker in (d.get("speakers") or [])
                  for a, b in (speaker.get("sections") or []))
    merged = []
    for a, b in every:
        if merged and a <= merged[-1][1]:
            merged[-1][1] = max(merged[-1][1], b)
        else:
            merged.append([a, b])
    spoken = sum(b - a for a, b in merged)
    length = float(d.get("length_s") or 0.0) or (merged[-1][1]
                                                 if merged else 0.0)
    return out, total, max(0.0, length - spoken), length

def coupling_matrix(power, speech, faint=6.0, loud=10.0, at_least=3):
    """Return how loudly each voice arrives in the other microphones.

    ``c[i][j]`` is the power gain with which speaker j appears in
    microphone i, measured where j speaks alone; the diagonal is 1. No
    such moment leaves the entry 0. *power* is [track][block] on an axis.
    """
    n = len(power)
    c = np.eye(n)
    for j in range(n):
        # j speaks, everyone else is quiet against their own speech level.
        alone = power[j] > (speech[j] * (10 ** (-loud / 20.0))) ** 2
        for other in range(n):
            if other != j:
                alone &= power[other] < (speech[other]
                                         * (10 ** (-faint / 20.0))) ** 2
        blocks = np.where(alone)[0]
        if len(blocks) < at_least:
            continue
        for i in range(n):
            if i == j:
                continue
            own = power[j][blocks]
            c[i][j] = float(np.median(power[i][blocks] / np.maximum(own,
                                                                    1e-20)))
    return c

def unmix_levels(power, c, at_most=30.0):
    """Take the bleed out of the measured levels.

    What a microphone hears is its own speaker plus a share of every
    other: ``observed = c @ own``, solved once for all blocks. Returns
    (own, reason). Too strong a coupling to invert leaves the levels
    unchanged: better an unseparated measurement than an invented one.
    """
    if len(power) < 2:
        return power, ""
    highest = float(max(c[i][j] for i in range(len(c))
                        for j in range(len(c)) if i != j) if len(c) > 1
                    else 0.0)
    if highest >= 0.9:
        return power, T('the microphones hear each other almost as loudly '
                        'as their own speaker')
    try:
        if float(np.linalg.cond(c)) > at_most:
            return power, T('the tracks are too much alike to separate')
        own = np.linalg.solve(c, power)
    except np.linalg.LinAlgError as e:
        return power, str(e)
    return np.maximum(own, 0.0), ""

# The shortest sound that still counts as speech: below this a block is
# dropped before the pause search, so a short reaction reads as a pause.
# The floor is where passages stop being "mhm" and start being breath.
SPEECH_MIN_LEN_S = 0.2

def clock_on_axis(curve, clock):
    """Stretch a level curve from a recorder's own clock onto the axis.

    No two recorders run at exactly the same speed, so an hour on one is
    not an hour on the next. The run rewrites the audio; here the level
    curve is resampled. *clock* is the b of "recorder = a + b * axis".
    """
    if not len(curve) or abs(clock - 1.0) <= 1e-7:
        return curve
    long_enough = int(round(len(curve) / clock))
    if long_enough < 2:
        return curve
    return np.interp(np.arange(long_enough) * clock,
                     np.arange(len(curve)), curve)

def speakers_from_tracks(tracks, block=0.1, rate=8000, over_db=10.0,
                        gap=0.35, min_len=SPEECH_MIN_LEN_S,
                        report=None, separate=True,
                        note=None, grid=None):
    """Derive speech segments from the separate tracks.

    Each block is measured against the track's own noise floor, because
    recorders are set to different gains. With *separate* the bleed is
    taken out first; without it a neighbour's voice counts as that
    neighbour speaking. *tracks* is [(name, path, offset[, clock])];
    *grid* takes the levels as read, so no track is opened twice."""
    names, levels, shifts = [], [], []
    # Read a handful at a time, not all at once: an hour of audio is a
    # couple of hundred megabytes per track.
    step = max(2, min(4, how_many_processors()))
    read = {}
    for i, entry in enumerate(tracks):
        name, file_path, offset = entry[0], entry[1], entry[2]
        clock = float(entry[3]) if len(entry) > 3 else 1.0
        if i % step == 0:
            read = {}
            group = tracks[i:i + step]
            for entry, x in zip(group, parallel_map(
                    group, lambda t: decode_audio(t[1], rate=rate))):
                read[entry[1]] = x
        if report:
            report(T('Measuring %s (%s of %s)')
                   % (name, number_text(i + 1, 0),
                      number_text(len(tracks), 0)))
        x = read.pop(file_path, None)
        if x is None:
            x = decode_audio(file_path, rate=rate)
        nb = max(1, int(block * rate))
        count = len(x) // nb
        names.append(name)
        shifts.append(int(round(offset / block)))
        if count < 2:
            levels.append(np.zeros(0))
            continue
        levels.append(clock_on_axis(np.sqrt(
            (x[:count * nb].reshape(count, nb).astype(np.float64) ** 2
             ).mean(axis=1)), clock))

    # One grid for all: louder than another only means something on one axis.
    begin = min(shifts) if shifts else 0
    end = max((s + len(v) for s, v in zip(shifts, levels)), default=0)
    width = max(0, end - begin)
    level = np.zeros((len(levels), width))
    for i, (s, v) in enumerate(zip(shifts, levels)):
        if len(v):
            level[i][s - begin:s - begin + len(v)] = v
    # The reference has to land inside the speaking: the 90th percentile
    # does so above a tenth of the blocks, the 99th above a hundredth.
    # Below that it lands on the bleed and refuses the split untruly.
    speech = np.array([float(np.percentile(v[v > 0], 99))
                       if len(v) and len(v[v > 0]) else 0.0 for v in levels])
    if grid is not None:
        grid.append({"names": list(names), "level": level.copy(),
                     "block": block, "begin": begin * block})

    power = level ** 2
    reason = ""
    if separate and len(levels) > 1 and width:
        c = coupling_matrix(power, speech)
        power, reason = unmix_levels(power, c)
        if note:
            # c is a ratio of powers, so ten times the logarithm -- the
            # same figure the 3:1 check reports for amplitudes.
            far = [(10.0 * math.log10(1.0 / max(c[i][j], 1e-9)), names[j],
                    names[i]) for i in range(len(c)) for j in range(len(c))
                   if i != j and c[i][j] > 0]
            if reason:
                note(T('  Bleed not separable: %s') % reason)
            elif far:
                worst = min(far)
                note(T('  Bleed measured, %s in %s only %s dB quieter '
                       '-- taken out of the speech detection')
                     % (worst[1], worst[2],
                        number_text(worst[0], 1)))
                # Where a pair offers no moment of one voice alone, its
                # entry stays 0 and that bleed is left in: half a model
                # beats none, but silence here would look measured.
                pairs = len(c) * (len(c) - 1)
                if len(far) < pairs:
                    note(T('  Caution: only %s of %s pairs measurable. For '
                           'the rest no moment was found where exactly one '
                           'person speaks, so their bleed stays in -- the '
                           'speaker detection is unreliable here.')
                         % (number_text(len(far), 0), number_text(pairs, 0)))
            else:
                note(T('  No moment found where exactly one person speaks '
                       '-- the bleed stays in the speech detection.'))
    level = np.sqrt(power)

    out = []
    for i, name in enumerate(names):
        row = level[i]
        present = row[row > 0]
        if not len(present):
            out.append((name, []))
            continue
        # Noise floor: the lowest fifth of the blocks; above it is speech.
        floor = float(np.percentile(present, 20))
        threshold = max(floor * (10.0 ** (over_db / 20.0)),
                       float(np.percentile(present, 90)) * 0.08)
        loud = row > threshold
        segments, first = [], None
        for j, on in enumerate(loud):
            if on and first is None:
                first = j
            elif not on and first is not None:
                segments.append([first * block, j * block])
                first = None
        if first is not None:
            segments.append([first * block, len(row) * block])
        # Short pauses inside a sentence are not speaker changes.
        joined = []
        for a, b in segments:
            if joined and a - joined[-1][1] <= gap:
                joined[-1][1] = b
            else:
                joined.append([a, b])
        shift = begin * block
        out.append((name, [(round(a + shift, 2), round(b + shift, 2))
                            for a, b in joined if b - a >= min_len]))
    return out

def camera_cut(tracks, length, camera_of, wide_shot,
               min_len=MIN_EDIT_DURATION_S, delay=0.3, *,
               after, holds, at_latest, edge, rules=None, faint=True):
    """Build the whole camera cut, in the order the rules apply.

    The preview and the run both come through here. Two copies of this
    order drift apart, and then the same material yields a different cut
    depending on which produced it. The four wide shot settings are named
    at every call and have no starting value; *delay* keeps its 0.3 s.
    """
    rules = rules or cut_rules()
    cut = build_camera_cut(tracks, length, camera_of, wide_shot,
                           min_len, -delay, rules)
    if edge:
        cut = wide_shot_at_edges(cut, tracks, wide_shot, faint=faint)
        cut = merge_short_shots(cut, min_len)
    if after > 0:
        cut = insert_wide_shots(cut, tracks, wide_shot, after, holds,
                                min_len, at_latest, camera_of, rules)
        # And again after them, which is what merge_short_shots asks
        # for: an inserted wide shot may be shorter than the shortest.
        cut = merge_short_shots(cut, min_len)
    return cut

def camera_short_name(track):
    """The camera's own name out of its track name.

    The take and the camera number tell two files apart and say nothing
    about the camera, so they go. Where nothing is left the track name
    stays whole -- a camera named only by a number keeps that name.
    """
    parts = [t for t in str(track or "").split("_") if t.strip()]
    left_over = [t for t in parts
                 if not re.fullmatch(r"\d+", t)
                 and not re.fullmatch(r"[A-Za-z]\d{3,}", t)]
    return left_over[-1] if left_over else str(track or "")

def wide_shots_of(cameras, taken, marked=()):
    """Which cameras are the wide shot, in the order they stand in.

    One answer for the whole program: preview, run and window all ask
    here, or the window shows a cut the run does not make. A mark beats
    the derivation; without one, the cameras nobody is assigned to.
    """
    marked = [c for c in cameras if c in set(marked or ())]
    if marked:
        return marked
    return [c for c in cameras if c not in set(taken or ())]

def marked_wide_shots(args):
    """The video files marked as the wide shot, as absolute paths.

    One switch may stand several times: several wide shots are allowed,
    and the window can mark as many as it likes.
    """
    return FileSet(p for p in (getattr(args, "wide_shot", None) or ()) if p)

# The four numbers, the tick and the value in three of the choice
# fields: everything in the cut box that says what the wide shot does.
WIDE_FIELDS = ("wide-after", "wide-length", "wide-most", "wide-latest")
WIDE_CHOICES = ("on-monologue", "on-together", "on-uncertain")
# The two that belong to a question. They need the words: without a
# transcript no question is found, and then they change nothing.
QUESTION_SETTINGS = ("reaction-lead", "on-question")
# And two of the wide shot's: both place themselves on a sentence
# boundary, which only a transcript knows. Over 200 s of monologue,
# "after 40" gives what "after 90" does (measurements.md).
WIDE_NEEDS_WORDS = ("wide-after", "wide-most")

def wide_note_build(label_of_text, quiet):
    """The line under the wide shot settings that says why they are grey.

    The same pattern the start button follows: a greyed control without
    a reason is a dead end. Named, so a reading program can announce it.
    """
    note = label_of_text("", quiet)
    note.setWordWrap(True)
    note.setVisible(False)
    note.setObjectName("wide_note")
    note.setAccessibleName(T('Why the wide shot settings are grey'))
    return note

def question_note_build(label_of_text, quiet):
    """The line under the question settings that says why they are grey.

    Same pattern as the wide shot's: a greyed control without a reason
    is a dead end, and a tooltip is neither reachable nor read out.
    """
    note = label_of_text("", quiet)
    note.setWordWrap(True)
    note.setVisible(False)
    note.setObjectName("question_note")
    note.setAccessibleName(T('Why the question settings are grey'))
    return note

def wide_settings_grey(parts, tick, note, there, quiet, words_there):
    """Grey the wide shot settings where there is no wide shot.

    Five settings and a value in three drop-downs are about the wide shot
    and nothing else, and with every camera carrying a speaker there is
    none. The reason stands under them: a tooltip is not read out.
    """
    why = T('No camera is free of speakers, so there is no wide shot: '
            'the four wide shot settings and the tick for the edges do '
            'nothing. Give a camera the Kind "Wide shot", or leave one '
            'without a speaker.')
    for api_key in WIDE_FIELDS:
        # Two of them need the words too, and the greying that runs last
        # writes the widget. So each asks both facts.
        open_it = there and (words_there or api_key not in WIDE_NEEDS_WORDS)
        for w in parts.get(api_key, (None, None)):
            if w is not None:
                w.setEnabled(open_it)
    tick.setEnabled(there)
    for api_key in WIDE_CHOICES:
        _line, box = parts.get(api_key, (None, None))
        if box is not None:
            PROGRAM.choices_shut(box, () if there else (SHOT_WIDE,),
                                 why, quiet)
    note.setText("" if there else why)
    note.setVisible(not there)

def words_settings_grey(parts, note, there, wide_there, quiet):
    """Grey the settings that need a transcript, with the reason.

    Four of them: the two of the question, which without words find no
    question at all, and two of the wide shot, which place themselves on
    a sentence boundary. *wide_there* keeps the wide shot's own greying:
    a control is open only where both say so.
    """
    why = T('No transcript yet. Without one no question is found and no '
            'sentence boundary is known, so these four settings do '
            'nothing. A run writes it, and from then on they work.')
    for api_key in QUESTION_SETTINGS:
        for w in parts.get(api_key, (None, None)):
            if w is not None:
                w.setEnabled(there)
    for api_key in WIDE_NEEDS_WORDS:
        for w in parts.get(api_key, (None, None)):
            if w is not None:
                w.setEnabled(there and wide_there)
    note.setText("" if there else why)
    note.setVisible(not there)

def wide_cameras_of(files, kinds, remembered, taken, placeless=()):
    """The wide shots among these files, and whether anybody said so.

    *files* are the window's (path, kind) pairs, *kinds* the
    {path: Value} it holds, *remembered* the fallback for a file no table
    has a value for, *placeless* the paths placed nowhere. Returns
    (file names, marked).
    """
    videos = sorted([p for p, a in files if a == "video"],
                    key=lambda x: os.path.basename(x).lower())
    lost = set(path_key(p) for p in (placeless or ()))

    def kind_of(path):
        return (kinds[path].get() if path in kinds
                else remembered.get("kind:" + path) or TYPE_CONTENT)

    def a_camera(path):
        """A camera the derivation may take: one with a place on the axis.

        A file that sits on no axis cannot be the one the cut falls back
        on. A mark comes through either way: dropped here it would fall
        out of the marked list too, and the caller would say a wide shot
        was marked while handing back a derived one.
        """
        kind = kind_of(path)
        return kind in CAMERA_TYPES and (
            kind == TYPE_WIDE or path_key(path) not in lost)

    marked = [os.path.basename(p) for p in videos if kind_of(p) == TYPE_WIDE]
    return (wide_shots_of([os.path.basename(p) for p in videos
                           if a_camera(p)], taken, marked),
            bool(marked))

def wide_bar_of(targets, wides, said, aside):
    """What a wide shot mark bars, and where what it displaces is kept.

    A camera somebody marked takes no speakers, and its entry stays in
    every list, greyed, with the reason on it. Only a mark bars a camera,
    never the derivation -- a derived wide shot displaces nothing.
    """
    barred = set(wides) if said else set()
    return {"barred": barred,
            "why": T('marked as the wide shot -- it takes no speakers'),
            "pickable": [t for t in targets if t not in barred],
            "aside": aside, "pushed": {}}

def camera_after_a_mark(api_key, old_camera, wide, who):
    """The camera a row is preselected to, once the marks are in.

    Whoever was on a camera that is now the wide shot goes to "no camera
    of its own" -- name, sound, mix and transcript all stay. The camera
    is set aside and handed back the moment the mark goes, and kept out
    of "remembered", which is written back from the table.
    """
    aside, barred = wide["aside"], wide["barred"]
    kept = aside.get(api_key)
    was = old_camera if old_camera not in (None, MIX_ONLY) else kept
    if was in barred:
        # Held for as long as the mark stands, or a second rebuild
        # would lose what the first one set aside.
        aside[api_key] = was
        wide["pushed"].setdefault(was, []).append(who)
        return None
    if kept:
        # The mark is gone. The camera comes back where nothing else was
        # chosen meanwhile; where something was, that is the newer answer.
        aside.pop(api_key, None)
        if old_camera in (None, MIX_ONLY):
            return kept
    return old_camera

def speaker_names_of(values):
    """The names a set of speaker fields really works under.

    A field with nothing in it and nothing suggested has no name and
    drops out here: the answers are read out to people, and the camera's
    file name is built out of them.
    """
    return [name for name in (v.get() for v in values or ())
            if name]

def camera_gets_from(short, wide, names):
    """What the camera table says this camera gets its audio from.

    A wide shot takes no speakers, so the question has an answer of its
    own here -- one that says why. Any assigned before the mark are named.
    """
    if short in wide["barred"]:
        if wide["pushed"].get(short):
            return T('this is the wide shot -- %s moved to "no camera '
                     'of its own"') % ", ".join(wide["pushed"][short])
        return T('no speaker -- this is the wide shot')
    return (", ".join(v.get() or "?" for v in names)
            if names else T('the mix of all tracks'))

def camera_name_suggestion(production, camera, values):
    """The file name a camera is offered, out of the speakers on it.

    A speaker whose name is only suggested belongs in the camera's
    file name too, and that name travels to Resolve.
    """
    return camera_output_name(production, camera,
                              speaker_names_of(values) or ["Audio-Full-Mix"])

def cameras_with_a_speaker(assign_rows, voice_rows, voiced=()):
    """Which cameras a speaker is assigned to, by file name.

    The same reading off the assignment that off_speakers makes: voices
    under a recording carry the camera, and the recording does not.
    """
    voiced = set(voiced or ())
    taken = set()
    for row, name_value, camera_value in assign_rows:
        if os.path.abspath(row[0]) in voiced:
            continue
        if name_value.get() and camera_value.get() not in (
                MIX_ONLY, IGNORE_AUDIO):
            taken.add(camera_value.get())
    for _label, name_value, camera_value in voice_rows:
        if name_value.get().strip() and camera_value.get() not in (
                MIX_ONLY, IGNORE_AUDIO):
            taken.add(camera_value.get())
    return taken

def kind_on_show(kind, short, wides, said):
    """What the Kind field shows, why, and whether it is derived.

    A mark is shown as it stands; where several are marked, the ones
    after the first are told which the cut uses. A camera nobody is
    assigned to is the wide shot, with a reason. (value, reason, derived).
    """
    second = bool(wides) and len(wides) > 1 and wides[0] != short
    if kind == TYPE_WIDE:
        return kind, (T('the cut uses %s') % wides[0] if second else ""), False
    # chosen_by_hand is not asked here, where wide_shot_barred does: a
    # place on the axis is a measurement, an assignment is an answer.
    if kind == TYPE_CONTENT and not said and short in wides:
        if second:
            return TYPE_WIDE, T('no speaker is assigned to it, but the '
                                'cut uses %s') % wides[0], True
        return TYPE_WIDE, T('because no speaker is assigned to it'), True
    return kind, "", False

def without_a_wide_shot(after, edge, rules):
    """Silence the wide shot settings where there is no wide shot.

    Four numbers, one tick and one value in three of the choice fields
    all say what the wide shot does, and where there is none they have
    nothing to say -- without this they said it to the first camera. The
    window greys the same settings. Returns (after, edge, rules).
    """
    rules = dict(rules or {})
    for api_key in ("on_monologue", "on_together", "on_uncertain"):
        if rules.get(api_key) == SHOT_WIDE:
            rules[api_key] = SHOT_HOLD
    return 0.0, False, rules

def legend_names(cameras, wide_shot=None):
    """What each camera is called in the legend under the cut band.

    Returns {track: name}. Who is in the picture is what the reader does
    not know, so a camera is called after the people on it, joined with a
    plus and never shortened. Two alike get the camera beside the name.
    """
    # *wide_shot* takes one track name or several: two cameras nobody is
    # assigned to are two wide shots, as are two somebody marked. The cut
    # uses the first -- see wide_shots_of for why one and not a majority.
    marked = ([wide_shot] if isinstance(wide_shot, str)
              else list(wide_shot or []))
    wides = [cam.get("track") for cam in cameras
             if cam.get("track") in marked]
    out, short = {}, {}
    for cam in cameras:
        track = cam.get("track")
        short[track] = camera_short_name(track)
        who = [n for n in (cam.get("speakers") or []) if n]
        if who:
            out[track] = " + ".join(who)
        elif track in wides:
            out[track] = (T(SHOT_NAMES[SHOT_WIDE]) if len(wides) < 2
                          else T('Wide shot %d') % (wides.index(track) + 1))
        else:
            out[track] = short[track]
    same = {}
    for track, name in out.items():
        same.setdefault(name, []).append(track)
    for name, tracks in same.items():
        if len(tracks) < 2:
            continue
        beside = ["%s (%s)" % (name, short[t]) for t in tracks]
        for track, both in zip(tracks, beside):
            out[track] = (both if len(set(beside)) == len(tracks)
                          else "%s (%s)" % (name, track))
    return out

def legend_markup(numbers):
    """The legend under the cut band, as one piece of rich text.

    One wrapping label, not a row of widgets: a row cannot get narrower
    than the sum of its parts, and with camera names in it the sheet
    needs a horizontal scroll bar on any screen. The colour square rides
    in the text. Spaces are hard except between two cameras and two people.
    """
    names = (numbers or {}).get("names") or {}
    colours = (numbers or {}).get("colours") or {}

    def hard(text):
        """A piece that may not be broken: its spaces are hard ones."""
        return _xml_escape(text).replace(" ", "&nbsp;")

    entries = []
    for track, part, sec, how_often in (numbers or {}).get("shares") or []:
        who = str(names.get(track) or track)
        entries.append(
            '<span style="color: %s">■</span>&nbsp;%s%s%s'
            % (colours.get(track, "#888888"), hard("%d × " % how_often),
               " + ".join(hard(x) for x in who.split(" + ")),
               hard("  %.0f %%  (%s)" % (part, as_minutes(sec)))))
    return "&nbsp;&nbsp; ".join(entries)

def wide_marks_applied(d, wide_names, speakers_on=None, marked=False):
    """Say the wide shot in a handover the way the window says it now.

    The preview reads the handover for what a run measured, but which
    camera is the wide shot is an answer and the window may have a newer
    one. A camera is recognised by its file, never by its track name.
    """
    if not d or not d.get("cameras") or not (wide_names or speakers_on):
        return d

    def stem_of(name):
        stem = os.path.splitext(os.path.basename(str(name or "")))[0]
        return stem[:-6] if stem.endswith("_audio") else stem

    want = set(stem_of(n) for n in wide_names or ())
    fresh = []
    for c in d.get("cameras") or ():
        # A run's handover names the render "file" and the camera "source".
        stem = stem_of(c.get("source") or c.get("file") or c.get("camera"))
        who = c.get("speakers") or []
        if speakers_on:
            # Who sits in front of this camera. An empty assignment says
            # nothing rather than "nobody", or the file's own answer goes.
            who = sorted(n for n, cam in speakers_on.items()
                         if stem_of(cam) == stem)
        here = stem in want
        # Both answers, the way write_handover writes them: the cut goes
        # by "wide_marked", the colour and the mix source by "wide".
        fresh.append(dict(c, speakers=who,
                          wide_marked=bool(marked) and here,
                          wide=(bool(marked) and here) or not who))
    return dict(d, cameras=fresh)

def speech_on_cameras(tracks, cut, camera_of, wide_shot, step=0.1):
    """Where speech lands, counted along the programme's own clock.

    Once per tenth of a second of the timeline, not once per speaker:
    two people talking at once are one moment. Counted per speaker it
    reported 181 minutes on a timeline 83 minutes long. Three counts,
    in steps.
    """
    end = max([b for _a, b, _w in cut] + [0.0])
    steps = int(round(end / step))
    seen, anyone = {}, bytearray(steps)
    for name, segs in tracks:
        cam = camera_of.get(name)
        # Every speaker counts as speech, camera or none: counting only
        # those with one read 0.0 %, which looks quiet and is the loudest.
        mark = seen.setdefault(cam, bytearray(steps)) if cam else None
        for a, b in segs:
            for k in range(max(0, int(round(a / step))),
                           min(steps, int(round(b / step)))):
                anyone[k] = 1
                if mark is not None:
                    mark[k] = 1
    in_frame = on_wide = off_camera = 0
    for a, b, shown in cut:
        mark = seen.get(shown)
        for k in range(max(0, int(round(a / step))),
                       min(steps, int(round(b / step)))):
            if not anyone[k]:
                continue
            if mark is not None and mark[k]:
                in_frame += 1
            elif shown == wide_shot:
                on_wide += 1
            else:
                off_camera += 1
    return in_frame, on_wide, off_camera

def stand_in_camera(names):
    """What stands in front of a silence where no camera is a wide shot.

    Not a wide shot, and it must not act as one: everything the wide
    shot settings ask for is switched off wherever this is used.

    All that matters here is that the preview and the run reach for the
    same camera -- and they did not. The preview took the first of its
    own list, the run took the reference clip, and in a real shoot both
    are real cameras, so it showed as two different cuts rather than as
    a fault. Found 25.8.2026, and only reachable at all since a camera
    with a speaker stopped counting as a wide shot.

    By name, not by position: the two lists are built in different
    places and nothing says they are sorted alike, so a rule that hangs
    on the order would let them drift again on the day one of them is
    built differently.
    """
    return sorted(n for n in names if n)[:1] or ["Wide"]


def cut_statistics(d, min_len=MIN_EDIT_DURATION_S, delay=0.3,
                   after=WIDE_AFTER_S,
                       holds=5.0, at_latest=120.0, edge=True,
                       rules=None):
    """Compute the camera cut without writing anything.

    *d* is a parsed handover file. Returns how many shots, how long they
    stand, and how much speech lands on a camera the speaker is not in.
    """
    tracks = [(s["name"], [tuple(x) for x in (s.get("sections") or [])])
              for s in (d.get("speakers") or [])]
    cameras = d.get("cameras") or []
    if not tracks or not cameras:
        return None
    camera_of = {}
    for cam in cameras:
        for n in (cam.get("speakers") or []):
            camera_of[n] = cam.get("track")
    wides = wide_shots_of([cam.get("track") for cam in cameras],
                          set(camera_of.values()),
                          [cam.get("track") for cam in cameras
                           if cam.get("wide_marked")])
    wide_shot = wides[0] if wides else stand_in_camera(
        [cam.get("track") for cam in cameras])[0]
    length = float(d.get("length_s") or 0.0)
    if length <= 0:
        length = max((b for _, segs in tracks for _, b in segs), default=0.0)
    if length <= 0:
        return None

    # What was said and the sound itself come out of the handover file:
    # the caller sets the numbers, not the material.
    rules = dict(rules or cut_rules())
    if not rules.get("words"):
        rules["words"] = words_from_handover(d)
    if not rules.get("levels"):
        rules["levels"] = sound_levels_for(d)
    if not wides:
        after, edge, rules = without_a_wide_shot(after, edge, rules)
    cut = camera_cut(tracks, length, camera_of, wide_shot, min_len, delay,
                     after=after, holds=holds, at_latest=at_latest,
                     edge=edge, rules=rules)
    # The same step the run takes, out of the same function: without it
    # the preview shows one shot where the run makes hundreds.
    cut, _detail = cut_split_where_one_camera(cut, tracks, camera_of, min_len)
    if not cut:
        return None

    blocks = sorted(b - a for _, segs in tracks for a, b in segs)
    takes = sorted(b - a for a, b, _ in cut)
    share, how_often = {}, {}
    for a, b, who in cut:
        share[who] = share.get(who, 0.0) + (b - a)
        how_often[who] = how_often.get(who, 0) + 1
    total = sum(share.values()) or 1.0

    # How much speech time runs past the wrong camera? Checked in tenth of
    # a second steps -- finer would be effort without insight.
    step = 0.1
    in_frame, on_wide_shot, off_camera = speech_on_cameras(
        tracks, cut, camera_of, wide_shot, step)
    speech_time = (in_frame + off_camera + on_wide_shot) or 1
    # The same colour assignment as in Resolve, so band and clips look alike.
    colour_cameras = [{"track": cam.get("track"),
                       "wide": cam.get("track") in set(wides)}
                    for cam in cameras]
    assigned, _duplicate = colour_per_camera(colour_cameras, list(CLIP_COLOURS))
    return {
        "cut": cut,
        "colours": {track: clip_colour_rgb(name) for track, name in assigned.items()},
        "shots": len(cut),
        "median": takes[len(takes) // 2],
        "shortest": takes[0],
        "longest": takes[-1],
        "longest_camera": max((b - a for a, b, who in cut if who != wide_shot),
                               default=0.0),
        "wides": sum(1 for _, _, who in cut if who == wide_shot),
        "shares": [(who, 100.0 * v / total, v, how_often.get(who, 0)) for who, v in
                    sorted(share.items(), key=lambda x: -x[1])],
        # The one the cut uses, and all of them. With none at all the
        # first entry is empty: something has to stand before the silence.
        "wide": wide_shot if wides else "",
        "wide_shots": list(wides),
        # What each camera is called where somebody reads it. Here and
        # not in the window: a second answer to the question drifts.
        "names": legend_names(cameras, wides),
        "in_frame": 100.0 * in_frame / speech_time,
        "on_wide": 100.0 * on_wide_shot / speech_time,
        "off_camera": 100.0 * off_camera / speech_time,
        "in_frame_s": in_frame * step,
        "on_wide_s": on_wide_shot * step,
        "off_camera_s": off_camera * step,
        "speech_time_s": speech_time * step,
        "shortest_block": blocks[0] if blocks else 0.0,
    }

def why_no_cut(d):
    """Say why these statistics produce no camera cut.

    cut_statistics answers None for four different reasons, and what
    somebody can do differs, so each gets its own sentence.
    """
    tracks = d.get("speakers") or []
    if not tracks:
        return T('No speaker is known here -- without who speaks when '
                 'there is nothing to cut between.')
    if not (d.get("cameras") or []):
        return T('No camera is assigned, so there is nothing to cut '
                 'between.')
    length = float(d.get("length_s") or 0.0)
    if length <= 0:
        length = max((b for s in tracks
                      for _a, b in (s.get("sections") or [])), default=0.0)
    if length <= 0:
        return T('The programme is %s long here -- nothing can be laid '
                 'out in that. In point and Out point are what set it.') \
            % as_hms(float(d.get("length_s") or 0.0))
    if not any(cam.get("speakers") for cam in d["cameras"]):
        return T('No voice has a camera yet -- with that every shot '
                 'would be the same one.')
    return T('The cut rules leave no shot standing in these %s. A '
             'shorter shortest shot, or less wide shot, gives one '
             'again.') % as_hms(length)

def build_camera_cut(tracks, length, camera_of, wide_shot,
                     min_len=MIN_EDIT_DURATION_S, lead_in=-0.3,
                     rules=None):
    """Return the camera cut as [(from, to, camera)], without speakers."""
    return [(a, b, who) for a, b, who, _speaking
            in camera_cut_detail(tracks, length, camera_of, wide_shot,
                                 min_len, lead_in, rules)]

def camera_cut_detail(tracks, length, camera_of, wide_shot,
                      min_len=MIN_EDIT_DURATION_S, lead_in=-0.3,
                      rules=None):
    """Turn speaker segments into a camera cut list.

    Returns [(from, to, camera, speakers)]; *speakers* is who talks in
    that shot, empty during silence. Whoever speaks alone gets their
    camera; several prefer one showing exactly them. Judged per camera.
    """
    rules = rules or cut_rules()
    long = [(n, list(segs)) for n, segs in tracks]
    edges = sorted({t for _, segs in long for s in segs for t in s}
                    | {0.0, length})
    # The assignment already says which camera shows whom, and how many.
    coverage = {}
    for name, camera in (camera_of or {}).items():
        if camera:
            coverage.setdefault(camera, set()).add(name)

    def common_camera(active):
        """Return the camera showing exactly these speakers, or all of them.

        Exact match first. Otherwise the smallest camera containing them
        all: a three-shot beats the wide shot when only two speak.
        """
        wanted_name = set(active)
        for camera, who in coverage.items():
            if who == wanted_name:
                return camera
        matching = [(len(who), camera) for camera, who in coverage.items()
                   if wanted_name <= who]
        return min(matching)[1] if matching else None

    def on_a_camera(names):
        """Those of these speakers who have a camera to be shown on.

        A voice without one counts everywhere else -- for the speaking
        shares and among who is heard -- but cannot decide the picture.
        """
        return [n for n in names if (camera_of or {}).get(n)]

    per_camera = segments_per_camera(long, camera_of or {})
    words = rules.get("words") or ()
    sentences = sentence_start_times(words) if words else []
    clauses = clause_break_times(words) if words else []
    levels = rules.get("levels") or ()
    step = rules.get("level_step") or DIP_STEP_S
    # Too short to move the camera, judged per camera: what counts is
    # that one of the people on it was speaking, not which of them.
    min_speech = float(rules.get("min_speech") or 0.0)
    hold_gap = float(rules.get("silence_hold") or 0.0)
    too_short = {}
    for camera, segs in per_camera:
        too_short[camera] = span_finder(
            [(a, b) for a, b in segs if b - a < min_speech])
    stray = stray_labels(long)
    restless = span_finder(unrest_spans(long, camera_of or {}))
    turns = []

    def silence_picture(gap):
        """Return what to show where nobody speaks at all.

        A breath mid-sentence and the end of a thought are the same
        thing here; only the length tells them apart, and *gap* is whole.
        """
        want = rules.get("on_silence") or SHOT_WIDE
        if want == SHOT_HOLD:
            return None
        if want == SHOT_HOLD_BRIEF and gap <= hold_gap:
            return None
        return wide_shot

    def unsure_picture(t, active):
        """Return what to show where the cut does not know whom."""
        want = rules.get("on_uncertain") or SHOT_WIDE
        if want == SHOT_HOLD:
            return None
        if want in (SHOT_LISTENER, SHOT_ALTERNATE):
            here = {camera_of.get(n) for n in on_a_camera(active)}
            listener = next_speaker_camera(
                t, per_camera, next(iter(here)) if len(here) == 1 else None)
            if want == SHOT_LISTENER:
                return listener or wide_shot
            row = [wide_shot] + ([listener] if listener else [])
            choice = row[len(turns) % len(row)]
            turns.append(choice)
            return choice
        return wide_shot

    def together_picture(t, active):
        """Return what to show where several speak and no camera fits."""
        want = rules.get("on_together") or SHOT_WIDE
        if want == SHOT_HOLD:
            return None
        if want == SHOT_LISTENER:
            return next_speaker_camera(t, per_camera, None) or wide_shot
        if want == SHOT_ALTERNATE:
            row = sorted({camera_of.get(n) for n in active
                          if camera_of.get(n)}) or [wide_shot]
            choice = row[len(turns) % len(row)]
            turns.append(choice)
            return choice
        return wide_shot

    raw = []
    for a, b in zip(edges, edges[1:]):
        if b - a <= 1e-6:
            continue
        middle = (a + b) / 2.0
        active = [n for n, segs in long for s0, s1 in segs if s0 <= middle < s1]
        heap = [n for n in active if n in stray]
        strong = [n for n in active if n not in stray
                  and not too_short.get(camera_of.get(n), lambda _t: False)(
                      middle)]
        shown = on_a_camera(strong)
        if not active:
            who = silence_picture(b - a)
        elif restless(middle) or (heap and not strong):
            who = unsure_picture(middle, active)
        elif not strong:
            who = None               # nobody held the floor long enough
        elif not shown:
            who = wide_shot          # heard, but nothing to cut to
        elif len(shown) == 1:
            who = camera_of.get(shown[0]) or wide_shot
        else:
            who = common_camera(shown) or together_picture(middle, shown)
        raw.append([a, b, who, tuple(sorted(active))])

    # "Hold" means the picture does not change, so the block takes the
    # camera of the one before it -- or of the one after, at the start.
    for i in range(len(raw)):
        if raw[i][2] is None:
            raw[i][2] = raw[i - 1][2] if i else None
    for i in range(len(raw) - 1, -1, -1):
        if raw[i][2] is None:
            raw[i][2] = raw[i + 1][2] if i + 1 < len(raw) else wide_shot

    # Lead-in: switch to the coming camera shortly before the entry. A
    # negative value makes it a lag, as Resolve's Edit Change Delay does;
    # both edges of a shot move together, or shifting would shorten it.
    answers, asked_until = {}, {}
    if (rules.get("on_question") or SHOT_OFF) != SHOT_OFF and words:
        answers = reaction_cuts(
            long, words, camera_of or {},
            float(rules.get("reaction_gap") or 3.0),
            float(rules.get("reaction_hold") or 0.0),
            float(rules.get("reaction_over") or 0.0),
            # Counted into the caller's own rules, so whoever built them
            # can say what became of the questions; one built here cannot.
            tally=rules.setdefault("question_tally", {}),
            ends=asked_until)
    lead = float(rules.get("reaction_lead") or 0.0)
    if (lead_in or answers) and raw:
        limits = [r[0] for r in raw] + [raw[-1][1]]
        end = limits[-1]
        brought = []
        for i in range(1, len(raw)):
            if raw[i][2] == raw[i - 1][2]:
                continue
            who = answers.get(round(raw[i][0], 6))
            if who is None:
                for when in answers:
                    if abs(when - raw[i][0]) < 1e-6:
                        who = answers[when]
                        break
            early = (who is not None and lead > 0
                     and raw[i][2] == (camera_of or {}).get(who))
            if early and (rules.get("on_question") == SHOT_LISTENER
                          and not next_speaker_camera(
                              raw[i][0] - lead, per_camera, raw[i - 1][2])):
                early = False
            if early:
                # Zero is where the asker stops: the pause belongs to
                # the question, and the delay is not added twice.
                zero = asked_until.get(raw[i][0], raw[i][0])
                limits[i] = min(end, max(0.0, cut_point(
                    zero - lead, (), (), levels, step)))
                brought.append(i)
            elif lead_in:
                limits[i] = min(end, limits[i] - lead_in)
        # A reaction cut reaches back over the pause after the question,
        # and the wide shot in it goes too, or the edge would push back.
        for i in brought:
            for j in range(i - 1, 0, -1):
                if limits[j] <= limits[i]:
                    break
                limits[j] = limits[i]
        # No edge may end up before the previous one.
        for i in range(1, len(limits)):
            if limits[i] < limits[i - 1]:
                limits[i] = limits[i - 1]
        for i in range(len(raw)):
            raw[i][0], raw[i][1] = limits[i], limits[i + 1]
        raw = [r for r in raw if r[1] - r[0] > 1e-6]

    # A short silence between two identical shots is not noticeable.
    extra = []
    for r in raw:
        if extra and extra[-1][2] == r[2]:
            extra[-1][1] = r[1]
            voices_joined(extra[-1], r)
        else:
            extra.append(list(r))

    return [tuple(r) for r in merge_short_shots(extra, min_len)]

def voices_joined(keeper, swallowed):
    """Add the swallowed shot's voices to the shot that stays.

    Both halves are still audible in the joined shot, so both belong to
    its name -- and that name is read: the Speaker column of the cut list
    and the clip name in the EDL. A row without voices is left alone.
    """
    if len(keeper) > 3 and len(swallowed) > 3:
        keeper[3] = tuple(sorted(set(keeper[3]) | set(swallowed[3])))

def shot_key(row):
    """What makes two neighbouring shots the same shot: the camera."""
    return row[2]

def split_shots_by_speaker(cut, tracks, min_len=MIN_EDIT_DURATION_S):
    """Cut every shot again where the speech changes hands.

    For the case where one camera shows everybody: the cut is then one
    long shot, and Resolve gets a single clip that cannot be grouped,
    coloured or zoomed per speaker. The picture does not change, only the
    boundaries. Pieces shorter than *min_len* are merged back.
    """
    if not cut:
        return []
    edges = sorted({t for _n, segs in tracks for s in segs for t in s})
    key = lambda r: (r[2], r[3])
    out = []
    for a, b, who in cut:
        # Merged inside this shot, not across it: a piece pulled over a
        # camera edge would move the picture as well as the name.
        pieces = []
        inside = [t for t in edges if a < t < b]
        for x, y in zip([a] + inside, inside + [b]):
            if y - x <= 1e-6:
                continue
            middle = (x + y) / 2.0
            talking = tuple(sorted(
                n for n, segs in tracks
                for s0, s1 in segs if s0 <= middle < s1))
            if pieces and pieces[-1][3] == talking:
                pieces[-1][1] = y
            else:
                pieces.append([x, y, who, talking])
        out += merge_short_shots(pieces, min_len, key)
    joined = []
    for r in out:
        if joined and key(joined[-1]) == key(r):
            joined[-1][1] = r[1]
        else:
            joined.append(list(r))
    return [tuple(r) for r in joined]

def cut_split_where_one_camera(cut, tracks, camera_of, min_len):
    """Cut again at every change of speaker where one camera serves all.

    With one camera the cut is one long shot that says nothing; cutting
    again leaves the picture as it is and gives Resolve a clip per
    speaker. *detail* carries the speakers per shot and is always there.
    Run and preview both pass here, or the two drift apart.
    """
    detail = split_shots_by_speaker(cut, tracks, min_len) if cut else []
    if cut and one_camera_only(camera_of) and len(detail) > len(cut):
        return [(a, b, who) for a, b, who, _speaking in detail], detail
    return cut, detail

def one_camera_only(camera_of):
    """Report whether every speaker sits on the same camera.

    Then the camera says nothing about who is talking, and the cut has
    to come from the speech instead.
    """
    seen = {c for c in (camera_of or {}).values() if c}
    return len(seen) <= 1

def merge_short_shots(cut, min_len, key=shot_key):
    """Merge shots below the minimum duration into the following one.

    Same rule as Resolve's Minimum Edit Duration, run again after every
    other step, which can leave short remnants. Forwards, not backwards:
    merging back gives the time to whoever has just finished, forward to
    whoever is about to speak. *key* says when two are the same shot.
    """
    if min_len <= 0 or not cut:
        return list(cut)
    extra = [list(x) for x in cut]
    i = 0
    while i < len(extra) and len(extra) > 1:
        if extra[i][1] - extra[i][0] >= min_len:
            i += 1
            continue
        if i + 1 < len(extra):
            extra[i + 1][0] = extra[i][0]
            voices_joined(extra[i + 1], extra[i])
            del extra[i]
        else:
            extra[i - 1][1] = extra[i][1]
            voices_joined(extra[i - 1], extra[i])
            del extra[i]
            i -= 1
        # The neighbours may now be the same shot, and two of those in a
        # row would leave a cut where the picture does not change.
        j = max(0, i - 1)
        while j + 1 < len(extra) and key(extra[j]) == key(extra[j + 1]):
            extra[j][1] = extra[j + 1][1]
            voices_joined(extra[j], extra[j + 1])
            del extra[j + 1]
        i = max(0, i - 1)
    return extra

def timeline_timecode(seconds, zero, fps):
    """The timecode a moment of programme time carries on the Timeline.

    Frame zero of the Timeline, then the frames since it -- the two steps
    build_cut_timeline takes, or the paper and the Timeline name frames
    one apart wherever the zero does not sit on a whole one.
    """
    return frames_to_timecode(zero + seconds_to_frames(seconds, fps), fps)

def write_edl(file_path, title, segments, zero, fps):
    """Write segments as an EDL; Resolve imports it as timeline markers."""
    with open(file_path, "w", encoding="utf-8") as f:
        f.write("TITLE: %s\nFCM: NON-DROP FRAME\n\n" % title)
        for i, (a, b, name) in enumerate(segments, 1):
            t0 = timeline_timecode(a, zero, fps)
            t1 = timeline_timecode(b, zero, fps)
            f.write("%03d  AX       A     C        %s %s %s %s\n"
                    % (i, t0, t1, t0, t1))
            f.write("* FROM CLIP NAME: %s\n\n" % name)

def csv_line(values):
    """One row of a CSV file: comma separated, quoted where it matters.

    Comma and full stop, in every language. These files are read by other
    programs and compared across months; a separator that follows the
    language of the run would make two runs incomparable.
    """
    out = []
    for x in values:
        x = str(x)
        if any(c in x for c in ',";\r\n'):
            x = '"%s"' % x.replace('"', '""')
        out.append(x)
    return ",".join(out) + "\n"


def write_metrics_csv(file_path, tracks, cut, segment_list, cameras,
                         args, colours=None, gain=0.0):
    """Write the per-episode metrics as CSV, before against after.

    The log is overwritten on the next run; this file is not. Over a few
    months it shows what a single run hides: a recorder drifting, a
    camera unlike the rest, crosstalk rising. Area and Metric stay English.
    """
    lines = []

    def line(area, what, before_value="", after="", unit=""):
        lines.append((area, what, before_value, after, unit))

    def number(x, spots=1):
        # A full stop, always: the file is read by other programs, and
        # what they see must not depend on the language of the run.
        return "" if x is None else "%.*f" % (spots, x)

    # --- audio per track
    for track in tracks:
        before = track.get("axis") or track.get("audio")
        after = track.get("ready")
        i0 = p0 = l0 = i1 = p1 = l1 = None
        if before and os.path.exists(before):
            i0, p0, l0 = measure_loudness(before, None, T('Before: %s') % track["name"])
        if after and os.path.exists(after):
            i1, p1, l1 = measure_loudness(after, None, T('After: %s') % track["name"])
        line('Audio ' + track["name"], 'Loudness', number(i0), number(i1), "LUFS")
        line('Audio ' + track["name"], 'Peak', number(p0), number(p1), "dBTP")
        line('Audio ' + track["name"], 'Loudness range', number(l0), number(l1), "LU")
        if track.get("drift_ppm") is not None:
            line('Audio ' + track["name"], 'Clock drift', number(track["drift_ppm"], 2),
                  "0", "ppm")
        if track.get("offset_ms") is not None:
            line('Audio ' + track["name"], 'Offset', number(track["offset_ms"], 2),
                  number(track.get("residual_ms"), 2), "ms")
    line('Audio', 'Gain on every track', "", number(gain, 2), "dB")
    # Empty where nothing was adjusted, or the column claims a target.
    line('Audio', 'Loudness target', "", number(getattr(args, "lufs", None)),
          "LUFS")

    # --- the cut
    if cut:
        lengths = sorted(b - a for a, b, _n in cut)
        total = sum(lengths)
        line('Cut', 'Shots', "", "%d" % len(cut), "")
        line('Cut', 'Median hold time', "",
              number(lengths[len(lengths) // 2], 2), "s")
        line('Cut', 'shortest', "", number(lengths[0], 2), "s")
        line('Cut', 'longest', "", number(lengths[-1], 2), "s")
        per_camera = {}
        for a, b, n in cut:
            per_camera[n] = per_camera.get(n, 0.0) + (b - a)
        for n in sorted(per_camera, key=lambda x: -per_camera[x]):
            line('Cut', "Share %s" % n, "",
                  number(100.0 * per_camera[n] / total if total else 0), "%")

    # --- Speech time
    for name, segs in (segment_list or []):
        line('Speech time', name, "", number(sum(b - a for a, b in segs), 1), "s")

    # --- Colour
    for name, values, (dy, du, dv) in (colours or []):
        line('Colour ' + name, "Brightness", "", number(values.get("y")), "")
        line('Colour ' + name, 'Distance to mean', "", number(dy), "")
        line('Colour ' + name, "Colour position U / V", "",
              "%s / %s" % (number(du), number(dv)), "")

    try:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(csv_line(("Area", "Metric", "Before", "After",
                              "Unit")))
            for r in lines:
                f.write(csv_line(r))
    except OSError as e:
        print(T('  Metrics not writable: %s') % e)
        return None
    return file_path

def read_separation_file(file_path):
    """Read a stored separation out of a project or assignment file.

    Returns the dict with source, segments and names, or {}.
    """
    try:
        with open(file_path, encoding="utf-8") as f:
            d = json.load(f)
    except (OSError, ValueError) as e:
        print(T('  %s cannot be read: %s') % (os.path.basename(file_path), e))
        return {}
    if not isinstance(d, dict):
        return {}
    for key in ("speakers_of", "speakers"):
        entry = d.get(key)
        if isinstance(entry, dict) and entry.get("segments"):
            return entry
    return d if d.get("segments") else {}

def voices_of_file(file_path):
    """Which camera each voice belongs to, out of a handed-over file.

    Only the interface knows this. Missing is the ordinary case and
    means every voice goes to the camera the run is built around.
    """
    try:
        with open(file_path, encoding="utf-8") as f:
            d = json.load(f)
    except (OSError, ValueError):
        return {}
    got = d.get("voices_of") if isinstance(d, dict) else None
    return dict(got) if isinstance(got, dict) else {}

def separation_on_axis(given, tracks, position, t0, t1):
    """Put every separation handed over onto the axis of this run.

    The one in front and the ones under "more", each with the offset of
    its own recording -- which recording a voice was heard in makes no
    difference to the cut. Voices of one name are folded together.
    Returns (segments, "") or ([], why not).
    """
    out, trouble = one_separation_on_axis(given, tracks, position, t0, t1)
    why = [trouble] if trouble else []
    for one in ((given or {}).get("more") or ()):
        more, trouble = one_separation_on_axis(one, tracks, position, t0, t1)
        out += more
        if trouble:
            why.append(trouble)
    if not out:
        return [], "; ".join(why) or T('no recording named')
    return voices_merged(out), ""

def one_separation_on_axis(given, tracks, position, t0, t1):
    """Put one stored separation onto the axis of this run.

    The segments are kept raw, in the time of the file they were measured
    in; where it sits is known, so this is arithmetic and no measurement.
    Returns (segments, "") or ([], why not).
    """
    if not (given or {}).get("source"):
        return [], T('no recording named')
    # Looked up by the real path: /tmp is a link to /private/tmp on
    # macOS, and the same file then carries two names.
    source = os.path.realpath(given["source"])
    where = ByFile()
    for track in tracks:
        blocks = track.get("blocks") or [track.get("source")]
        if blocks and blocks[0]:
            where[os.path.realpath(blocks[0])] = (track["a"], track["b"])
    for v, place in (position or {}).items():
        where[os.path.realpath(v)] = (place[0], place[1])
    if source not in where:
        return [], T('%s is not part of this run') % os.path.basename(source)
    a, b = where[source]
    if not b:
        return [], T('%s has no place on the axis') % os.path.basename(source)
    named = dict((given or {}).get("names") or {})
    out = []
    for label, parts in speaker_segments_polish(
            speaker_segments_group((given or {}).get("segments") or [])):
        kept = []
        for x, y in parts:
            x, y = (x - a) / b - t0, (y - a) / b - t0
            x, y = max(0.0, x), min(y, t1 - t0)
            if y > x:
                kept.append((round(x, 3), round(y, 3)))
        if kept:
            out.append((named.get(label) or label, kept))
    if not out:
        return [], T('nothing of it falls inside the window')
    return out, ""

def microphones_apart_of_run(args, tracks):
    """How far apart the microphones of this run stand, in dB.

    Every recording against every other, both ways round, so it is the
    dearest question in this corner: asked once a run, the answer kept on
    *args*, None where there is nothing to compare. Two blocks of one
    recorder share no time, so the question goes to whole recordings.
    """
    if hasattr(args, "_microphones_apart"):
        return args._microphones_apart
    whole = []
    for track in tracks or ():
        p = track.get("source") or (track.get("blocks") or [""])[0]
        if p and p not in whole and os.path.exists(p):
            whole.append(p)
    apart = microphones_apart_db(whole) if len(whole) > 1 else None
    args._microphones_apart = apart
    return apart

def separation_source_of_run(args, tracks, video_paths, mixable=False,
                             window=()):
    """Which recording a run without a window takes apart by voice.

    The same rule the window follows, on the same function. Which cameras
    were ticked by hand is not on the command line, so all are offered.
    With *mixable* microphones that hear each other too well are added
    into one file, which becomes the source; *window* names it.
    """
    from_cameras = bool(getattr(args, "_camera_audio", None))
    recordings, of_track = [], {}
    for track in tracks or ():
        for p in (track.get("blocks") or [track.get("source")]):
            if p and p not in recordings:
                recordings.append(p)
                of_track[p] = track

    def mix(chosen):
        """Add up the tracks these recordings were aligned into."""
        picked, made_of, seen = [], [], set()
        for p in chosen:
            track = of_track.get(p)
            if track is None or id(track) in seen or not track.get("axis"):
                continue
            seen.add(id(track))
            picked.append(track["axis"])
            made_of.append("%s|%s|%.6f|%.9f"
                           % (path_key(p), file_fingerprint(p),
                              float(track.get("a") or 0.0),
                              float(track.get("b") or 1.0)))
        return speaker_mix_file(picked, made_of + [str(x) for x in window])

    apart = (microphones_apart_of_run(args, tracks)
             if mixable and not from_cameras else None)
    return speaker_source_pick([] if from_cameras else recordings,
                               video_paths or (),
                               camera_audio=from_cameras,
                               apart_db=apart,
                               mix=mix if mixable else None)

def voices_reported(segments):
    """Say who speaks how long, and in how many passages."""
    for name, segs in segments:
        print(TN(len(segs), '  %-20s %s in %s passage',
                 '  %-20s %s in %s passages')
              % (name, as_hms(sum(b - a for a, b in segs)),
                 number_text(len(segs), 0)))

def separation_for_run(args, tracks, position, t0, t1, video_paths=()):
    """Work out who speaks when, before the audio is processed.

    Four ways in, in order: handed over in the assignment file, named
    with --speakers-from, named with --speakers-local, or the one this
    run picks. Where the microphones hear each other too well, all are
    mixed instead. Returns (segments, where from) or ([], "").
    """
    given = getattr(args, "_speakers_of", None) or {}
    where_from = T('the interface') if given else ""
    if not given and getattr(args, "speakers_from", None):
        given = read_separation_file(args.speakers_from)
        where_from = os.path.basename(args.speakers_from)
    source, why, dropped = "", "", None
    if (getattr(args, "_speakers_of", None)
            and not SPEAKER_SPLIT_OFF
            and not getattr(args, "no_speakers_local", False)
            and not getattr(args, "speakers_local", None)
            and not getattr(args, "_camera_audio", None)
            and bool(getattr(args, "without_auphonic", False))
            and not getattr(args, "auphonic_done", None)):
        # The window picks its source without knowing how far the
        # microphones stand apart, so it takes one recording: below
        # MICROPHONES_APART_DB that names 37.5 % right against 97.6 %.
        apart = microphones_apart_of_run(args, tracks)
        if apart is not None and apart < MICROPHONES_APART_DB:
            source, why = separation_source_of_run(
                args, tracks, video_paths, mixable=True, window=(t0, t1))
            if source and why == "microphones mixed":
                dropped = apart
            else:
                # No mix came back, so what the window found still stands.
                source, why = "", ""
    if not given and not source and not getattr(args, "no_speakers_local",
                                                False):
        if getattr(args, "speakers_local", None):
            source = os.path.abspath(args.speakers_local)
        elif not SPEAKER_SPLIT_OFF:
            # Only where the recordings stay raw -- after auphonic.com
            # the bleed is already out of them.
            source, why = separation_source_of_run(
                args, tracks, video_paths,
                mixable=bool(getattr(args, "without_auphonic", False))
                and not getattr(args, "auphonic_done", None),
                window=(t0, t1))
    if source:
        print(as_head(T('\nSEPARATING THE SPEAKERS')))
        if dropped is not None:
            # Somebody is about to wait three minutes longer than the
            # window promised, and this is the only place to say why.
            print(as_warn(
                T('  What the window took apart is dropped: it listened '
                  'to one recording, and the microphones hear each other '
                  'so well that none of them stands out -- %s dB against '
                  'the %s dB one of them alone needs to say who is '
                  'speaking.')
                % (number_text(dropped, 1),
                   number_text(MICROPHONES_APART_DB, 1))))
        if why == "microphones mixed":
            args._speakers_mixed = True
            print(T('  The microphones hear each other too well to say who '
                    'is speaking, so the separation listens to all %s of '
                    'them at once, on this machine.')
                  % number_text(len(tracks), 0))
        else:
            print(T('  In %s, on this machine.') % os.path.basename(source))
        count = int(getattr(args, "speakers_count", 0) or 0)
        stored = speaker_split_stored(source, count)
        if stored:
            print(T('  Separated once already: read back, not measured '
                    'again.'))
        else:
            how_long = media_seconds(source)
            if how_long:
                print(T('  About %s of computing for %s of audio.')
                      % (as_hms(how_long / SPEAKER_SPLIT_SPEED),
                         as_hms(how_long)))
            if not speaker_split_available():
                print("  " + speaker_split_missing())
        # A separation already on this machine costs nothing to read, so
        # a dry run hands it on. Only a measurement is left undone.
        if getattr(args, "dry_run", False) and not stored:
            print(T('  (measuring only: nothing separated)'))
            return [], ""
        if not stored and not speaker_split_available():
            print("  %s" % speaker_split_missing())
            return [], ""
        segments, trouble = speaker_split_cached(
            source, count,
            report=lambda text, share: show_progress(text, share))
        print()
        if trouble:
            print("  %s" % trouble)
            return [], ""
        given = {"source": source,
                 "segments": [[label, a, b] for label, parts in segments
                              for a, b in parts]}
        where_from = T('the separation in this run')
    if not given:
        return [], ""
    # Which recordings were taken apart. Their tracks reach the cut
    # through their voices, the rest through speakers_for_the_cut.
    args._separated = separation_sources(given)
    if getattr(args, "_speakers_mixed", False):
        # The mix was written onto the axis over this window, so a moment
        # in it is a moment of the cut. Placing takes t0 off; -t0 undoes it.
        position = dict(position or {})
        position[source] = (-t0, 1.0)
    out, why_not = separation_on_axis(given, tracks, position, t0, t1)
    if not out:
        print(as_warn(T('  The speaker separation is not used: %s.')
                      % why_not))
        if getattr(args, "_speakers_mixed", False):
            # Whatever went wrong, the tracks are there and everybody is
            # on one. A mix that says nothing would empty the cut.
            args._speakers_mixed = False
            args._separated = []
        return [], ""
    if getattr(args, "_speakers_mixed", False):
        # The mix is made of every track, so every track is spoken for.
        # Without this everybody would stand in the cut twice.
        args._separated += [p for track in (tracks or ())
                            for p in (track.get("blocks")
                                      or [track.get("source")]) if p]
    if getattr(args, "dry_run", False):
        # A dry run stops before the cut is built, so what the voices
        # amount to is said here or nowhere.
        print(as_head(T('\nSPEAKERS -- SEPARATED BY VOICE')))
        voices_reported(out)
    return out, where_from

def separation_sources(given):
    """Every recording the separations handed over were made of."""
    given = given or {}
    return [one["source"] for one in [given] + list(given.get("more") or ())
            if (one or {}).get("source") and (one or {}).get("segments")]

def separated_already(track, separated=()):
    """Whether a separation was made of this very recording.

    Then the people in it are in the cut as its voices, and measuring the
    track as well would put them there twice. That is the only thing that
    keeps a track out of the measurement: one with no camera of its own
    is measured like any other and counts for the speaking shares.
    """
    apart = set(path_key(p) for p in separated or () if p)
    mine = list(track.get("blocks") or []) + [
        track.get("source") or "", track.get("from_camera") or ""]
    return any(path_key(p) in apart for p in mine if p)

def speakers_for_the_cut(args, tracks):
    """Say who speaks when, and put the origin in the log.

    Everybody is in it, whichever way they came in: the voices a
    separation found, and every track no separation covers, measured from
    its own microphone. Only "do not use" keeps somebody out. Whoever is
    not in it is named in the log instead of going quietly missing.
    """
    voices, where_from = getattr(args, "_speakers", None) or ([], "")
    left = [t for t in tracks
            if not separated_already(t, getattr(args, "_separated", None))]
    mics, box = [], []
    if left or (where_from and len(tracks) > 1):
        # One reading for both uses, over every track: a track left out
        # would hear its neighbour and count that as speech.
        try:
            mics = speakers_from_tracks(
                [(track["name"], track.get("ready") or track["axis"], 0.0)
                 for track in tracks], note=print, grid=box)
        except Exception as e:
            print(as_warn(T('  The tracks were not measured, so %s is in '
                            'the mix and not in the cut: %s')
                          % (", ".join(t["name"] for t in left) or "-",
                             str(e)[:140])))
            left = []
    named = []
    if voices and getattr(args, "_speakers_mixed", False):
        voices, named = name_voices_by_microphone(voices, box)
        if not voices:
            left = list(tracks)
            for line in named:
                print(line)
            named = []
    if voices:
        print(as_head(T('\nSPEAKERS -- SEPARATED BY VOICE')))
        print(TN(len(voices), '  From %s: %s voice.', '  From %s: %s voices.')
              % (where_from, number_text(len(voices), 0)))
        for line in named:
            print(line)
    if left:
        print(as_head(T('\nSPEAKERS -- MEASURED HERE')))
        print(T('  From the tracks themselves, one voice per track: %s.')
              % ", ".join(t["name"] for t in left))
        keep = set(t["name"] for t in left)
        voices = list(voices) + [(n, s) for n, s in mics if n in keep]
    segments = voices_merged(voices)
    voices_reported(segments)
    # A run that quietly holds fewer speakers than the sheet did costs
    # hours to find, so whoever is missing is named here.
    in_cut = set(name for name, _segs in segments)
    absent = [t["name"] for t in tracks if t["name"] not in in_cut]
    if absent:
        print(T('  Not in the cut: %s -- a separation speaks for the '
                'recording, or it was not measured.') % ", ".join(absent))
    if not any(segs for _, segs in segments):
        print(T('  Nothing was audible in the tracks -- no camera cut from '
                'this.'))
    if where_from and len(tracks) > 1:
        for line in name_the_voices(segments, mics):
            print(line)
    return segments

def name_voices_by_microphone(voices, box):
    """Give the voices of a mixed separation the names of the microphones.

    A voice out of a mix is SPEAKER_00, a name with no camera behind it,
    so the cut would stand on the wide shot throughout -- this is no
    proposal like the one below. *box* holds the levels
    speakers_from_tracks read, so the tracks are opened once.
    """
    grid = (box or [None])[0]
    rows = voices_by_level(voices, grid["names"], grid["level"],
                           grid["block"], grid["begin"]) if grid else []
    if not rows:
        # Nothing that could be hung on a camera, so the voices are let
        # go and the tracks answer -- worse, but everybody is somewhere.
        return [], [T('  Which voice belongs to which microphone could '
                      'not be told, so the tracks are measured instead.')]
    called = dict((voice, track) for voice, track, _level, _ahead in rows)
    lines = [T('  %-20s is %-20s %s dB ahead of the next microphone, '
               'the recording level taken out')
             % (voice, track, number_text(ahead, 1))
             for voice, track, _l, ahead in rows]
    return ([(called.get(name, name), segs) for name, segs in voices or ()],
            lines)

def name_the_voices(segments, mics):
    """What the microphones say about voices that came out unnamed.

    Only worth saying where the two are different things: a separation
    named the voices SPEAKER_00 upwards, and beside it there are tracks a
    person has named. The measurement comes in rather than being made
    here -- the one the cut is built from, not a second reading.
    """
    return microphones_report(which_microphone(segments, mics))

def finish_without_auphonic(args, tracks, cameras, videos, tmpdir, position,
                            t0, t1, ref_clip):
    """Finish a multitrack run without auphonic.com.

    The tracks are aligned and equally long, which is everything the mix
    and the cameras need. What is missing is what only auphonic.com does:
    de-bleeding, leveler, noise removal. Who speaks when is measured from
    the tracks -- and there the bleed comes out of the *measurement*.
    """
    step_begin("loudness")
    print(as_head(T('\nWITHOUT AUPHONIC.COM')))
    print(T('  The tracks are used as recorded: aligned, mixed and brought to '
            'the\n  target loudness. No de-bleed, no leveler, no noise '
            'removal -- for\n  those the run needs auphonic.com.'))
    for track in tracks:
        track["ready"] = track["axis"]
    if args.dry_run:
        print(T('\n  (measuring only: nothing written)'))
        return 0
    step_begin("speakers")
    segment_list = speakers_for_the_cut(args, tracks)
    folder = os.path.abspath(args.out) if args.out else os.path.dirname(
        os.path.abspath(videos[0][0]))
    gain, curve = normalise_loudness(tracks, args.lufs, tmpdir, None,
                                     channels=mix_width(tracks))
    return PROGRAM.distribute_tracks_to_cameras(
        args, tracks, cameras, videos, tmpdir, gain, position, t0,
        ref_clip, t1, curve, segment_list=segment_list)

def camera_place(files, zero, measured, fps=30.0):
    """Where a camera's picture sits, and what put it there.

    "Position in the file is programme time minus this." Returns the
    place and "measured", "clock" or "nowhere"; a clock only where
    nothing was measured. *files* are asked in turn, rendered first --
    not every ffmpeg carries a timecode. *fps*: 30 not 25 is 0.08 s out.
    """
    if measured is not None:
        return float(measured), "measured"
    if isinstance(files, str):
        files = (files,)
    for file in files:
        if zero is None or not file:
            continue
        try:
            stamp = file_timecode(file, max(1.0, float(fps or 30.0)))
        except Exception:
            stamp = None
        if stamp is not None:
            return float(stamp) - float(zero), "clock"
    return 0.0, "nowhere"

def write_handover(args, tracks, cameras, videos, folder, tc_start,
                      ref_clip, results=None, cut=None, segment_list=None,
                      length=0.0, track_names=None, single_files=None,
                      offsets=None, lengths=None, words=(), unplaceable=()):
    """Write everything Resolve needs: the handover file and instructions.

    The Resolve scripting interface has no multicam: the word does not
    appear once in the bundled README (version 21), and the manual lists
    the conversion only as a menu command. Project, import, timeline,
    track names and markers can be driven; the last step stays manual.
    """
    if not cameras:
        return
    fps = timeline_frame_rate(args, videos, ref_clip)
    stem = os.path.join(folder, safe_filename(args.production or 'Production'))
    # The written file carries the ending the run hangs on; the camera
    # is known here under its name without it, so both are keys.
    tail = getattr(args, "suffix", "") or "_audio"
    done = {}
    for p in (results or []):
        made = os.path.splitext(os.path.basename(p))[0]
        done[made] = os.path.abspath(p)
        if made.endswith(tail):
            done[made[:-len(tail)]] = os.path.abspath(p)

    resolutions, rates = set(), set()
    for _, e in videos:
        if e.get("width"):
            resolutions.add((e["width"], e["height"]))
        rates.add(round(float(e.get("fps") or 0), 3))
    # The fallback for the offset is 0.0 -- the start of the axis.
    takes = ByFile((v, e.get("duration") or 0.0) for v, e in videos)
    rate_of = ByFile((v, e.get("fps") or 0.0) for v, e in videos)
    # Kept under the rendered file, shaped here: the caller may not be a run.
    measured = ByFile(offsets or {})
    delivered = ByFile(lengths or {})
    named = ByFile(track_names or {})
    speaker_of = ByFile()
    for track in tracks:
        if track.get("camera"):
            speaker_of.setdefault(track["camera"],
                                    []).append(track["name"])
    # And the voices told apart under one recording, which have no track
    # of their own -- else a camera filled with a person counts as wide.
    for name, where in voices_of_file(
            getattr(args, "assign", "")
            or getattr(args, "speakers_from", "") or "").items():
        speaker_of.setdefault(where, []).append(name)

    #----------------------------------------------------- Handover file
    marked_wide = marked_wide_shots(args)
    _hdr_flag = hdr_from_sources([cam["video"] for cam in cameras])
    items = []
    unmeasured = []
    by_clock = []
    left_out = []
    nowhere = FileSet(unplaceable or ())
    for cam in cameras:
        v = os.path.abspath(cam["video"])
        if v in nowhere:
            # Refused by the run, so no camera of this episode. Handed
            # over it becomes the wide shot: nobody is assigned to it.
            left_out.append(cam["name"])
            continue
        # Sorted, like build_handover's: gathered as they arrive, the same
        # two people come out as one name here and another there.
        who = sorted(speaker_of.get(v) or [])
        file = done.get(cam["name"], "")
        # The offsets are kept under the rendered file. A camera without a
        # render has no such key, and 0.0 as a fallback would put it at the
        # start of the axis -- so the source is tried and gaps are said.
        shift = measured.get(file) if file else None
        if shift is None:
            shift = measured.get(v)
        # A 0.0 here would be a lie nothing can read back: it looks like
        # a camera measured at the start of the axis.
        where, how = camera_place((file, v), tc_start, shift,
                                   rate_of.get(v) or fps)
        if how == "clock":
            by_clock.append(cam["name"])
        elif how == "nowhere":
            unmeasured.append(cam["name"])
        elif how == "measured" and tc_start is not None:
            # Both numbers where they disagree -- a clock quietly ignored
            # is how a camera nineteen hours out slips through. The word
            # matters: no clock at all is not a clock reading zero.
            clock, said = camera_place((file, v), tc_start, None,
                                        rate_of.get(v) or fps)
            if said == "clock" and abs(clock - where) > 1.0 / max(
                    1.0, float(fps)):
                print(T('  %s: the measurement puts it at %s s, the '
                        'timecode at %s s -- the measurement is used.')
                      % (cam["name"], number_text(where, 3, plus=True),
                         number_text(clock, 3, plus=True)))
        items.append({
            "file": file,
            "source": v,
            "camera": cam["name"],
            # The track name is a key further along, so it has to be
            # unique: one word for every camera without a speaker puts
            # two on one key, and the second takes the first's place.
            "track": (" + ".join(who) if who else cam["name"]),
            "speakers": who,
            "audio_tracks": (named.get(file, []) if file else []),
            # Where this camera sits: position in the file is programme
            # time minus this, at this camera's own rate.
            "offset": round(where, 4),
            # Which of the three answered: "measured", "clock" or
            # "nowhere". Read back by anybody asking why it sits there.
            "placed_by": how,
            # Not the camera's place but where the shared sound sits
            # against the picture, sign turned round -- hence the name.
            "sound_against_picture": (round(shift, 4)
                                       if shift is not None else None),
            # How long the delivered file is, not the recording: the cut
            # timeline drops every shot running past what this says.
            "duration": round((delivered.get(file) if file else None)
                              or takes.get(v, 0.0), 3),
            # This camera's own rate, not the Timeline's: Resolve counts
            # startFrame and endFrame in frames of the file.
            "fps": own_frame_rate(rate_of.get(v) or fps),
            # Two answers to two questions: "wide" is nobody assigned,
            # "wide_marked" is what somebody said, and the cut goes by it.
            "wide_marked": v in marked_wide,
            "wide": v in marked_wide or not who})
    if left_out:
        print(as_warn(T('  Not handed over: the run could not place %s, so '
                        'it is no camera of this episode.')
                      % ", ".join(left_out)))
    if by_clock:
        print(as_warn(T('  Nothing was found in the sound for %s -- placed '
                        'by the timecode alone.') % ", ".join(by_clock)))
    if unmeasured:
        print(as_warn(T('  No measured offset for %s -- placed at the '
                        'start of the axis.') % ", ".join(unmeasured)))
    handover = {
        "format": FILE_FORMAT,
        "created_by": "videopodcast-magic %s" % VERSION,
        "production": args.production or 'Production',
        "fps": resolve_timeline_rate(fps),
        "fps_measured": round(fps, 4),
        "drop_frame": is_drop_frame(ref_clip[1].get("tc") if ref_clip else None),
        "width": widest_frame(resolutions)[0],
        "height": widest_frame(resolutions)[1],
        "start_tc": (timecode_string(tc_start,
                                     resolve_timeline_rate(fps))
                     if tc_start is not None else None),
        "start_s": tc_start,
        # The window this run was made with. Without it the check before
        # the Resolve step holds the In point against start_s -- the zero
        # of the axis, earlier than any In point somebody sets.
        "in_point": getattr(args, "in_point", None) or None,
        "out_point": getattr(args, "out_point", None) or None,
        "length_s": round(length, 3),
        # None travels as null: the Resolve side has to be able to tell
        # "not adjusted" from "adjusted to -16".
        "lufs": getattr(args, "lufs", None),
        # How the render job decides between HDR and SDR: from the colr
        # box of the camera files. A Resolve project wins later.
        "hdr": _hdr_flag[0],
        "hdr_reason": _hdr_flag[1],
        # Intro and outro are finished clips: they are not aligned, not
        # processed and not copied -- they only go into the timeline.
        "intro": _intro_outro_entry(getattr(args, "intro", None)),
        "outro": _intro_outro_entry(getattr(args, "outro", None)),
        "cameras": items,
        "cut": [{"start": round(a, 3), "end": round(b, 3), "camera": n}
                    for a, b, n in (cut or [])],
        "speakers": [{"name": n,
                      "sections": [[round(a, 3), round(b, 3)]
                                     for a, b in segs]}
                     for n, segs in (segment_list or [])],
        # The stored single tracks: the cut timeline's audio comes from
        # them, whatever order the audio tracks sit in in the cameras.
        "audio_files": dict(single_files or {}),
        # What was said and when: three values a word, because at twelve
        # thousand words an hour the key names would be half the file.
        "words": words_for_handover(words or []),
    }
    js = stem + "_resolve.json"
    # Beside it, then moved into place: a run that dies while writing
    # would leave a fragment, and the next run skips one without a word.
    try:
        with open(js + ".new", "w", encoding="utf-8") as f:
            json.dump(handover, f, ensure_ascii=False, indent=1)
        os.replace(js + ".new", js)
    except OSError as e:
        try:
            os.unlink(js + ".new")
        except OSError:
            pass
        print(T('\n  Could not write %s: %s') % (js, e))
        js = None

    # -------------------------------------------------------- instructions
    #
    # Keep it short: the Resolve part says everything needed itself.
    stem_p = safe_filename(args.production or 'Production')
    lines = [as_head(T('FOR RESOLVE')), ""]
    if not js:
        lines.append(T('  The handover file could not be written.'))
    else:
        lines.append("  %s" % os.path.basename(js))
        lines.append("")
        # What gets built depends on the material: promise no second one.
        has_cut = bool(cut)
        several = len(cameras) > 1
        lines.append(T('  This produces the project, the import and %s:')
                      % (T('two Timelines') if has_cut and several
                         else T('one Timeline')))
        if has_cut:
            lines.append(T('    %-26s picture from the camera cut, audio '
                           'in one piece')
                          % (stem_p + ' Cut'))
        elif not several:
            lines.append(T('    %-26s the camera in one piece, the mix below')
                          % (stem_p + ' Cut'))
        if several:
            lines.append(T('    %-26s all cameras side by side -- becomes '
                           'the multicam clip') % (stem_p + " Multicam"))
        if not getattr(args, "resolve", False):
            lines.append("")
            lines.append(T('  Create it with "Create Resolve project" in '
                           'the interface. Resolve must be running.'))

    print("\n" + "\n".join(lines))
    if js:
        print("")
        for p in (js, stem + "_speakers.csv", stem + "_speakers.edl",
                  stem + "_cameracut.csv",
                  stem + "_cameracut.edl"):
            if os.path.exists(p):
                print("  %s" % p)
    if js and getattr(args, "resolve", False):
        try:
            build_resolve_project(handover, args.resolve_project,
                          log=stem + "_resolve_log.txt",
                          )
        except Exception as e:
            print(T('\n  Resolve part stopped: %s') % e)
            print(T('  %s is ready -- with --resolve-json it can be done '
                    'later.') % os.path.basename(js))

def write_cut_list(args, segment_list, tracks, cameras, videos, folder,
                           tc_start, ref_clip, length, words=(),
                           sound_source=""):
    """Write the speaker list, markers and camera cut.

    Returns (camera cut, speaker segments) so the Resolve handover uses
    the same result instead of recomputing it. *segment_list* says who
    speaks when. *words* and *sound_source* say where the cut points
    come from -- the text roughly, the sound exactly.
    """
    fps = max(1.0, resolve_timeline_rate(
        timeline_frame_rate(args, videos, ref_clip)))
    if not any(segs for _, segs in (segment_list or ())):
        print(as_head(T('\nSPEAKERS\n  Nobody was heard -- no camera '
                        'cut from this.')))
        return [], []
    length = length or max((b for _n, segs in segment_list
                            for _a, b in segs), default=0.0)
    # Frame zero of the Timeline, read back out of the start timecode --
    # the same step timeline_origin takes, and it has to be the same.
    zero = timecode_to_frames(
        timecode_string(tc_start if tc_start is not None else 0.0, fps), fps)

    # Who belongs to which camera, and which is the wide shot? Through
    # path_key, or two shapes of one path count as two cameras.
    output_name = {path_key(cam["video"]): cam["name"] for cam in cameras}
    camera_of = {}
    taken = set()
    for track in tracks:
        if track.get("camera"):
            v = os.path.abspath(track["camera"])
            camera_of[track["name"]] = output_name.get(path_key(v),
                                                     os.path.basename(v))
            taken.add(path_key(track["camera"]))
    # And the voices told apart under a recording: without this every
    # one lands on the camera of its recording, one for everybody.
    strangers = []
    for who, where in voices_of_file(
            getattr(args, "assign", "")
            or getattr(args, "speakers_from", "") or "").items():
        v = os.path.abspath(where)
        if path_key(v) not in output_name:
            strangers.append((who, os.path.basename(v)))
        camera_of[who] = output_name.get(path_key(v), os.path.basename(v))
        taken.add(path_key(where))
    # A name whose file is no camera of this run would reach the cut list
    # as a camera invented from the file name, with nothing behind it.
    for who, name in sorted(strangers):
        print(as_bad(T('  %s is placed on %s, which is no camera of this '
                       'run -- the cut names it all the same.')
                     % (who, name)))
    marked_wide = marked_wide_shots(args)

    def camera_name_of(video):
        return output_name.get(path_key(video), os.path.basename(video))

    wides = wide_shots_of(
        [camera_name_of(v) for v, _ in videos],
        set(camera_name_of(v) for v, _ in videos
            if path_key(v) in taken),
        [camera_name_of(v) for v, _ in videos
         if path_key(v) in marked_wide])
    wide_shot = wides[0] if wides else stand_in_camera(
        [camera_name_of(v) for v, _ in videos])[0]

    stem = os.path.join(folder, safe_filename(args.production or 'Production'))
    lines = sorted((a, b, n) for n, segs in segment_list for a, b in segs)
    with open(stem + "_speakers.csv", "w", encoding="utf-8") as f:
        f.write(csv_line(("Speaker", "Start TC", "End TC",
                          "Time from start", "Duration s")))
        for a, b, n in lines:
            f.write(csv_line((n, timeline_timecode(a, zero, fps),
                              timeline_timecode(b, zero, fps),
                              as_hms(a, "."), "%.2f" % (b - a))))
    write_edl(stem + "_speakers.edl", "Speakers", lines, zero, fps)

    # With one camera nothing changes hands, so the word would be wrong:
    # what comes of it is a first cut at every change of speaker.
    alone = one_camera_only(camera_of)
    # The same case distinction the cut box makes, out of the same
    # function: two readings of one question drift apart, and this one
    # had -- the log still called a two-camera case a cut by speaker.
    print(as_head(cut_log_heading(list(camera_of.items()), len(cameras))))
    # The interface shows the whole cut as a band; a closing line is enough.
    rules = rules_from_settings(args)
    rules["words"] = list(words or ())
    rules["levels"] = sound_levels(sound_source) if sound_source else []
    edges_on = not getattr(args, "no_wide_edges", False)
    wide_after = args.wide_after
    if not wides:
        wide_after, edges_on, rules = without_a_wide_shot(
            wide_after, edges_on, rules)
        print(T('  Every camera carries a speaker, so there is no wide '
                'shot: the four wide shot settings and the tick for the '
                'edges do nothing here.'))
    elif len(wides) > 1:
        # Several are allowed. Which one the cut uses is not a thing to
        # work out from a majority, so it is said instead.
        print(T('  %s wide shots: the cut uses %s.')
              % (number_text(len(wides), 0), wides[0]))
    cut = camera_cut(
        segment_list, length, camera_of, wide_shot,
        args.min_edit_duration, getattr(args, "delay", 0.3),
        after=wide_after, holds=args.wide_length,
        at_latest=getattr(args, "wide_latest", 120.0), edge=edges_on,
        rules=rules, faint=PROGRAM.GUI_RUNNING)
    # What became of the questions. An omitted reaction cut that says
    # nothing looks like a broken setting; the answer is a number here.
    _said = question_report(rules)
    if _said:
        print(_said)
    before_value = len(cut)
    if wide_after > 0 and not PROGRAM.GUI_RUNNING:
        before_value = len(camera_cut(
            segment_list, length, camera_of, wide_shot,
            args.min_edit_duration, getattr(args, "delay", 0.3),
            after=0.0, holds=args.wide_length,
            at_latest=getattr(args, "wide_latest", 120.0), edge=edges_on,
            rules=rules))
    if wide_after > 0 and len(cut) > before_value and not PROGRAM.GUI_RUNNING:
        print(T('  %sx away from the speaker because a shot ran '
                'longer than %s s')
              % (number_text((len(cut) - before_value) // 2, 0),
                 number_text(wide_after, 0)))
    was = len(cut)
    cut, detail = cut_split_where_one_camera(cut, segment_list, camera_of,
                                              args.min_edit_duration)
    if len(cut) > was:
        print(T('  One camera for everybody: cut into %s shots at the '
                'change of speaker, so Resolve can group them.')
              % number_text(len(cut), 0))
    with open(stem + "_cameracut.csv", "w", encoding="utf-8") as f:
        f.write(csv_line(("Shot", "Camera", "Speaker", "Start TC",
                          "End TC", "Duration s")))
        for i, (a, b, n, speaking) in enumerate(detail, 1):
            f.write(csv_line((i, n, " + ".join(speaking),
                              timeline_timecode(a, zero, fps),
                              timeline_timecode(b, zero, fps),
                              "%.2f" % (b - a))))
    write_edl(stem + "_cameracut.edl", "Camera cut",
              [(a, b, " + ".join(speaking) or n)
               for a, b, n, speaking in detail] if alone else cut,
              zero, fps)

    # The numbers are in the interface and the files; the outcome is enough.
    print(T('  %s speakers, %s shots, shortest %s s')
          % (number_text(len(segment_list), 0), number_text(len(cut), 0),
             number_text(min((b - a) for a, b, _ in cut)
                         if cut else 0)))
    return cut, segment_list
