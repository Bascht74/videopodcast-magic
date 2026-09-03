"""Every file is measured once, not once per question.

Building the file list asks the same things about the same file over
and over -- length, timecode, channel count, frame rate -- and each
answer costs a process. Writing down what is spoken is the dearest of
those measurements by far. All of them are kept in memory and on disk,
keyed on size and modification time; this test counts the processes and
the recognitions.

In order: the same question twice, every measurement of its own, a file
rewritten under its old name, a caller who spoils what it was handed,
the warming pass before the window is drawn, what the store carries
from one run into the next, a file that cannot be measured, which must
not stop the rest, and a recording written down once: handed back and
read back word for word, by both ways, listened to afresh in another
language, by the other recogniser and after a rewrite, and a silence
that counts as an answer rather than a miss. Then the mix a run writes
into a folder of its own, which is known by what it holds and not by
its name, and two separations in the window, each keeping its own
words instead of sending the other back to the recogniser, and neither
started a second time while it is still being written down.
"""
import os
HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = os.environ.get("VPM_SCRIPT") or os.path.join(
    os.path.dirname(HERE), "videopodcast_magic.py")
import importlib.util, shutil, struct, subprocess, sys, tempfile, threading
import time, wave
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


folder = tempfile.mkdtemp(prefix="vpm_probe_")
# A cache of its own: the suite hands every test the same folder, so
# without this the counts below would depend on which test ran first.
os.environ["VPM_CACHE"] = tempfile.mkdtemp(prefix="vpm_probe_cache_")


def forget_kept():
    """Empty what was kept on disk, so a count means what it says."""
    kept = vpm.cache_folder("probes")
    for name in (os.listdir(kept) if kept and os.path.isdir(kept) else []):
        try:
            os.unlink(os.path.join(kept, name))
        except OSError:
            continue

def tone(name, seconds=1.0, rate=48000):
    path = os.path.join(folder, name)
    with wave.open(path, "wb") as f:
        f.setnchannels(1); f.setsampwidth(2); f.setframerate(rate)
        f.writeframes(b"".join(struct.pack("<h", (i % 400) * 40)
                               for i in range(int(rate * seconds))))
    return path

a, b, c = tone("a.wav"), tone("b.wav"), tone("c.wav")

# --------------------------------------------------------------- Counting
run_real = subprocess.run
count = {"n": 0}

def run_counted(cmd, *args, **kwargs):
    if cmd and str(cmd[0]).endswith("ffprobe"):
        count["n"] += 1
    return run_real(cmd, *args, **kwargs)

subprocess.run = run_counted

def probes(work):
    """Return how many ffprobe processes a piece of work costs."""
    before = count["n"]
    work()
    return count["n"] - before


def duration_of(path):
    """The length ffprobe reports for a file, or None."""
    return vpm.ffprobe_json(path).get("format", {}).get("duration")


def cold():
    """Forget everything that was measured, in memory and on disk."""
    vpm._PROBE.clear()
    forget_kept()

# ------------------------------------------------------- One file, asked twice
print("1. The same question twice")
# The first judgement is the ground under every count below: if ffprobe
# answers nothing, or the counter never sees the process it starts,
# every "costs nothing" further down is true and means nothing.
cold()
first = probes(lambda: vpm.ffprobe_json(a))
answer = duration_of(a)
again = probes(lambda: vpm.ffprobe_json(a))
check("ffprobe answers about the material at all", answer is not None,
      "duration %s s, wanted a number" % (answer,))
check("the first question about a file starts one ffprobe", first == 1,
      "%d processes, wanted 1" % first)
check("the same question a second time starts none", again == 0,
      "%d processes, wanted 0" % again)

print("\n2. Every measurement of its own")
# Each question cold, so that "no second process" is not read off a
# store the question before it filled.
for what, ask in (("the channel count", lambda: vpm.channel_count(a)),
                  ("the length in samples", lambda: vpm.sample_count(a)),
                  ("the timecode", lambda: vpm.file_timecode(a))):
    cold()
    once, twice = probes(ask), probes(ask)
    check("%s is measured on the first ask" % what, once == 1,
          "%d processes, wanted 1" % once)
    check("%s is not asked of ffprobe a second time" % what, twice == 0,
          "%d processes, wanted 0" % twice)

print("\n3. The answer belongs to this file as it stands")
cold()
value_before = duration_of(a)
stamp_before = vpm.file_stamp(a) or ()
tone("a.wav", 2.0)                      # same name, other contents
stamp_after = vpm.file_stamp(a) or ()
after = probes(lambda: vpm.ffprobe_json(a))
value_after = duration_of(a)
# The path is left out of both: it is the same one, and it would carry
# the temporary folder into every failure line.
check("rewriting a file changes what it is known by",
      tuple(stamp_before[1:]) != tuple(stamp_after[1:]),
      "mtime and size %s -> %s, wanted two different ones"
      % (stamp_before[1:], stamp_after[1:]))
check("a changed file is measured again", after == 1,
      "%d processes, wanted 1" % after)
check("a changed file answers with its new length",
      value_before != value_after,
      "%s s -> %s s, wanted two different ones" % (value_before, value_after))

print("\n4. A caller may keep what it got")
vpm._PROBE.clear()
d = vpm.ffprobe_json(a)
check("the description of a file comes back as a dictionary",
      isinstance(d.get("format"), dict),
      "format is %s, wanted a dict" % type(d.get("format")).__name__)
d["format"] = "spoilt"
next_one = vpm.ffprobe_json(a).get("format")
check("a caller who spoils it does not spoil the next one's",
      isinstance(next_one, dict),
      "format is %s after one caller spoilt it, wanted a dict"
      % type(next_one).__name__)

print("\n5. Warming up beforehand")
cold()
warm = probes(lambda: vpm.probe_warm([a, b, c]))
check("warming three files starts one ffprobe for each", warm == 3,
      "%d processes, wanted 3" % warm)
# One line per question, and each one warmed afresh. Chained with "or"
# the first answer is truthy and the other two questions are never
# asked; asked one after another on the same warm cache, the first
# question fills it for the other two and only it can ever fall.
for what, ask in (("the whole description", vpm.ffprobe_json),
                  ("the channel count", vpm.channel_count),
                  ("the length in samples", vpm.sample_count)):
    cold()
    vpm.probe_warm([a, b, c])
    cost = dict((p, probes(lambda p=p: ask(p))) for p in (a, b, c))
    check("%s costs nothing after warming" % what,
          set(cost.values()) == set([0]),
          "%s, wanted 0 for each"
          % dict((os.path.basename(p), n) for p, n in cost.items()))

print("\n6. What ffprobe said outlives the run")
# Asking again costs a process: cheap here, dear on a builder where
# starting processes is most of what a test spends its time on.
cold()
first = probes(lambda: vpm.ffprobe_json(a))
measured = duration_of(a)
vpm._PROBE.clear()                      # a later run, nothing remembered
second = probes(lambda: vpm.ffprobe_json(a))
stored = duration_of(a)
check("the run that measures starts one ffprobe", first == 1,
      "%d processes, wanted 1" % first)
check("a later run with no memory of it starts none", second == 0,
      "%d processes, wanted 0" % second)
check("what the store gives back is what was measured",
      measured is not None and stored == measured,
      "%s s measured, %s s out of the store" % (measured, stored))

# Changed on disk means measured again, not answered from the store.
with open(a, "r+b") as f:
    f.seek(0, 2)
    f.write(b"\0" * 64)
vpm._PROBE.clear()
again = probes(lambda: vpm.ffprobe_json(a))
check("a file changed on disk is measured again, store or no store",
      again == 1, "%d processes, wanted 1" % again)

# A half-written file is what a run broken off in the middle leaves.
# Whether one was kept at all comes first: with nothing in the store,
# "measured again" is true of any program and says nothing.
vpm._PROBE.clear()
stamp = vpm.file_stamp(a)
kept = vpm.probe_cache_path(("ffprobe",) + stamp) if stamp else None
there = bool(kept) and os.path.exists(kept)
check("the store did keep what was measured", there,
      "kept file %s, wanted one that exists"
      % (os.path.basename(kept) if kept else "not named"))
if there:
    open(kept, "wb").close()
empty = probes(lambda: vpm.ffprobe_json(a))
check("an empty kept file is measured again, not believed", empty == 1,
      "%d processes, wanted 1" % empty)

print("\n7. What cannot be measured must not stop anything")
missing = os.path.join(folder, "not-there.wav")
check("the file this asks about really is not there",
      not os.path.exists(missing),
      "%s is there: %s, wanted False"
      % (os.path.basename(missing), os.path.exists(missing)))
cold()
try:
    vpm.probe_warm([a, missing, b])
    threw = ""
except Exception as e:
    threw = "%s while warming" % type(e).__name__
rest = probes(lambda: [vpm.ffprobe_json(a), vpm.ffprobe_json(b)])
check("a missing file does not stop the others being warmed",
      threw == "" and rest == 0,
      threw or "%d processes for the two good files afterwards, wanted 0"
      % rest)
try:
    got = vpm.ffprobe_json(missing)
    threw = ""
except Exception as e:
    got, threw = None, "%s while asking" % type(e).__name__
check("asking about a missing file answers instead of throwing",
      threw == "" and isinstance(got, dict),
      threw or "answer is %s, wanted a dict" % type(got).__name__)

print("\n8. A recording is written down once")
# Listening is a measurement like the others and by far the dearest:
# 27.0 s for 87 minutes of audio, and until there was a store it was
# paid again on every start. The recognisers are stood in for here, so
# what is counted is how often the program asks for one at all.
said = tempfile.mkdtemp(prefix="vpm_words_")
real_macos, real_whisper = vpm.macos_words, vpm.whisper_words
heard = {"macos": 0, "whisper": 0}
wrote = {"last": []}
mute = set()


def recording(name, seconds=0.2):
    """A file to listen to, with a sound of its own.

    The store knows a recording by what is in it, so two of these have
    to differ in more than their names or they really are one
    recording and one entry answers for both.
    """
    path = os.path.join(said, name)
    with wave.open(path, "wb") as f:
        f.setnchannels(1); f.setsampwidth(2); f.setframerate(8000)
        f.writeframes(struct.pack("<h", sum(ord(c) for c in name) % 3000 + 1)
                      * int(8000 * seconds))
    return path


def stood_in(way, path, language):
    """Stand in for a recogniser: count the run, name way and language."""
    # The real ones answer None where there is nothing to listen to, and
    # a stand-in that invented words for a missing file would let a
    # broken key through.
    if not os.path.exists(path):
        return None
    heard[way] += 1
    if path in mute:
        wrote["last"] = []              # it listened and heard nobody
        return []
    # Where the file lies is part of it: two runs write their mix under
    # the same name, and a stand-in that answered both alike could not
    # tell a stored answer from a fresh one.
    whose = "%s/%s" % (os.path.basename(os.path.dirname(path)),
                       os.path.basename(path))
    raw = [vpm.speech_word(i * 0.5, i * 0.5 + 0.3, "%s-%s-%s-%d"
                           % (way, (language or "none").lower(), whose, i))
           for i in range(3)]
    # Through the program's own correction, so the words carry the shape
    # the rest of it expects rather than one this test invented.
    shift = ((vpm.MACOS_START_S, vpm.MACOS_END_S) if way == "macos"
             else (vpm.WHISPER_START_S, vpm.WHISPER_END_S))
    wrote["last"] = vpm.corrected_words(raw, shift[0], shift[1])
    return wrote["last"]


vpm.macos_words = lambda path, language="": stood_in("macos", path, language)
vpm.whisper_words = (lambda path, language="", install=True:
                     stood_in("whisper", path, language))


def listens(work):
    """What a piece of work returned, and how many recogniser runs it cost."""
    before = heard["macos"] + heard["whisper"]
    got = work()
    return got, heard["macos"] + heard["whisper"] - before


def first_word(words):
    """The first word of a transcript, for the failure line."""
    return words[0]["word"] if words else "none"


def alike(one, other):
    """How many words of two transcripts stand in the same place unchanged."""
    return sum(1 for x, y in zip(one or (), other or ()) if x == y)


talk = recording("talk.wav")
(spoken, _way), first_runs = listens(
    lambda: vpm.recognise_speech(talk, "eng"))
said_words = list(wrote["last"])
(read_back, _way), again_runs = listens(
    lambda: vpm.recognise_speech(talk, "eng"))
check("the first listen to a recording runs the recogniser once",
      first_runs == 1, "%d recogniser runs, wanted 1" % first_runs)
check("the words the recogniser wrote are the ones handed back",
      len(said_words) == 3 and spoken == said_words,
      "%d words written down, %d handed back, %d of them alike, wanted 3"
      % (len(said_words), len(spoken or ()), alike(spoken, said_words)))
check("the same recording in the same language is not listened to twice",
      again_runs == 0,
      "%d recogniser runs the second time, wanted 0" % again_runs)
check("what is read back is word for word what was heard",
      read_back == spoken,
      "%d words heard, %d read back, %d of them alike"
      % (len(spoken or ()), len(read_back or ()), alike(spoken, read_back)))

# Another language of the same recording: other words, so the entry of
# the first one must not answer for it.
(german, _way), other_runs = listens(
    lambda: vpm.recognise_speech(talk, "ger"))
check("another language is listened to afresh", other_runs == 1,
      "%d recogniser runs for the second language, wanted 1" % other_runs)
check("the other language gets words of its own",
      bool(german) and german != spoken,
      "first word %s against %s, wanted two different ones"
      % (first_word(german), first_word(spoken)))

# And the other recogniser: two machines do not write the same words.
(whispered, whisper_way), whisper_runs = listens(
    lambda: vpm.recognise_speech(talk, "eng", way="whisper"))
check("the other recogniser is not answered out of the first one's store",
      whisper_runs == 1,
      "%d recogniser runs for the second way, wanted 1" % whisper_runs)
check("the other recogniser's own words come back",
      bool(whispered) and whispered != spoken,
      "way %s, first word %s against the first way's %s, wanted two "
      "different ones"
      % (whisper_way, first_word(whispered), first_word(spoken)))

# The one that proves the store never answers out of date: same name,
# other recording.
changed = recording("changed.wav", 0.2)
listens(lambda: vpm.recognise_speech(changed, "eng"))
mark_before = vpm.file_content_mark(changed)
recording("changed.wav", 0.5)           # same name, another recording
mark_after = vpm.file_content_mark(changed)
_answer, rewritten_runs = listens(lambda: vpm.recognise_speech(changed, "eng"))
check("rewriting a recording changes the mark it is known by",
      bool(mark_before) and mark_before != mark_after,
      "mark %s -> %s, wanted two different ones"
      % (mark_before[:12] or "none", mark_after[:12] or "none"))
check("a recording rewritten under its own name is listened to again",
      rewritten_runs == 1,
      "%d recogniser runs after the rewrite, wanted 1" % rewritten_runs)

# Nobody spoke: that is an answer, and asking again costs the same 27 s
# as any other recording.
quiet = recording("quiet.wav")
mute.add(quiet)
(nothing, _way), quiet_runs = listens(
    lambda: vpm.recognise_speech(quiet, "eng"))
_again, quiet_again = listens(lambda: vpm.recognise_speech(quiet, "eng"))
check("a recording nobody spoke in gives an empty answer, not a refusal",
      nothing == [] and quiet_runs == 1,
      "words %s after %d recogniser runs, wanted [] after 1"
      % (nothing, quiet_runs))
check("a recording nobody spoke in is not listened to a second time",
      quiet_again == 0,
      "%d recogniser runs the second time, wanted 0" % quiet_again)

# The run writes it down, the window reads it: one store, not two.
both = recording("both.wav")
(by_run, _way), _cost = listens(lambda: vpm.recognise_speech(both, "eng"))
by_window, window_runs = listens(lambda: vpm.words_at_hand(both, "eng"))
check("the window's way reads what the run's way wrote",
      window_runs == 0 and by_window == by_run,
      "%d recogniser runs and %d of %d words alike, wanted 0 runs and %d alike"
      % (window_runs, alike(by_window, by_run), len(by_window or ()),
         len(by_run or ())))

print("\n9. The mix the run writes into a folder of its own")
# A run mixes into a fresh temporary folder, so the file handed to the
# recogniser never carries the same name twice. What decides whether it
# has been written down before is therefore what is in it.
folders = [tempfile.mkdtemp(prefix="vpm_mt_") for _ in range(3)]


def mix_into(where, hum=1):
    """The mix of a run, in a folder of its own, as the run writes it."""
    path = os.path.join(where, "mix_full.wav")
    with wave.open(path, "wb") as f:
        f.setnchannels(1); f.setsampwidth(2); f.setframerate(8000)
        f.writeframes(struct.pack("<h", hum) * 1600)
    return path


mix_one, mix_two = mix_into(folders[0]), mix_into(folders[1])
other_mix = mix_into(folders[2], hum=9)
check("the two runs really wrote to two different places",
      mix_one != mix_two, "%s against %s" % (mix_one, mix_two))
(said_once, _way), first_mix_runs = listens(
    lambda: vpm.recognise_speech(mix_one, "eng"))
(said_again, _way), second_mix_runs = listens(
    lambda: vpm.recognise_speech(mix_two, "eng"))
check("the first run's mix is listened to once", first_mix_runs == 1,
      "%d recogniser runs, wanted 1" % first_mix_runs)
check("the same mix under another name is not listened to again",
      second_mix_runs == 0,
      "%d recogniser runs for the second run, wanted 0" % second_mix_runs)
check("and the second run gets the first run's words",
      said_again == said_once,
      "%d of %d words alike, wanted all %d"
      % (alike(said_again, said_once), len(said_again or ()),
         len(said_once or ())))
_other, other_runs = listens(lambda: vpm.recognise_speech(other_mix, "eng"))
check("another mix is listened to rather than answered from the first",
      other_runs == 1,
      "%d recogniser runs for a different mix, wanted 1" % other_runs)

# A modification time counts in whole seconds, so a file rewritten
# inside one second looks untouched by it. The mark reads the file.
clock = recording("clock.wav", 0.2)
listens(lambda: vpm.recognise_speech(clock, "eng"))
was = os.stat(clock)
with open(clock, "r+b") as f:
    f.seek(80); f.write(b"\x7f\x03" * 64)
os.utime(clock, (was.st_atime, was.st_mtime))
now = os.stat(clock)
_after, clock_runs = listens(lambda: vpm.recognise_speech(clock, "eng"))
check("a recording rewritten inside one second looks untouched by name",
      now.st_size == was.st_size and int(now.st_mtime) == int(was.st_mtime),
      "size %d -> %d, mtime %d -> %d, wanted both unchanged"
      % (was.st_size, now.st_size, int(was.st_mtime), int(now.st_mtime)))
check("and it is listened to again all the same", clock_runs == 1,
      "%d recogniser runs after the silent rewrite, wanted 1" % clock_runs)

# Reading the recording is what the mark costs, and there are two ways
# to ask about. Once per listening, not once per way.
real_mark = vpm.file_content_mark
marked = []


def counted_mark(file_path):
    """Mark a file and note that it was read for it."""
    marked.append(file_path)
    return real_mark(file_path)


vpm.file_content_mark = counted_mark
fresh = recording("fresh.wav", 0.2)
listens(lambda: vpm.recognise_speech(fresh, "eng"))
made_fresh = len(marked)
del marked[:]
listens(lambda: vpm.recognise_speech(fresh, "eng"))
made_again = len(marked)
vpm.file_content_mark = real_mark
check("a recording is read once to be marked, not once per way",
      made_fresh == 1, "%d readings while listening, wanted 1" % made_fresh)
check("and reading it back costs one reading too", made_again == 1,
      "%d readings while reading back, wanted 1" % made_again)

print("\n10. A second separation leaves the first one's words alone")
# The window listens to the recording it is separating while the sheet
# still shows the one before it. With one place for the words the two
# took it from each other and both were listened to twice.
one, two = recording("split_one.wav", 0.2), recording("split_two.wav", 0.3)
never = recording("split_none.wav", 0.4)
window = {"speakers_source": one, "axis": {},
          "speakers_local": [("SPEAKER_00", [(0.0, 4.0)]),
                             ("SPEAKER_01", [(5.0, 9.0)])]}
back = []


def came_back(result):
    """The signal the window connects: keep the words, note what came."""
    vpm.speech_words_done(window, result, lambda: None)
    back.append(result)


def words_arrive(wanted, still=5.0):
    """Wait until that many recognitions are back, or nothing moves.

    On standstill and not on a deadline: what says the recognition is
    working is that another answer arrived, and the builder is about
    nine times slower than this machine.
    """
    seen, quiet = len(back), 0.0
    while len(back) < wanted and quiet < still:
        time.sleep(0.01)
        quiet = 0.0 if len(back) != seen else quiet + 0.01
        seen = len(back)
    return len(back)


split_before = heard["macos"] + heard["whisper"]
vpm.speech_words_kick_off(window, "eng", came_back, one)
check("the recording being separated is listened to", words_arrive(1) == 1,
      "%d answers came back, wanted 1" % len(back))
vpm.speech_words_kick_off(window, "eng", came_back, two)
check("and so is a second one started beside it", words_arrive(2) == 2,
      "%d answers came back in all, wanted 2" % len(back))
heard_of = dict(back)
still_there = vpm.words_of_recording(window, one)
its_own = vpm.words_of_recording(window, two)
check("the first recording keeps its words while the second is separated",
      bool(still_there) and still_there == heard_of.get(one),
      "%d words stand under the first recording, %d came back for it"
      % (len(still_there or ()), len(heard_of.get(one) or ())))
check("the second recording gets words of its own",
      bool(its_own) and its_own != still_there,
      "first word %s against %s, wanted two different ones"
      % (first_word(its_own), first_word(still_there)))
check("a recording nobody listened to has no words to hand out",
      vpm.words_of_recording(window, never) is None,
      "%r came back for a recording never asked about, wanted None"
      % (vpm.words_of_recording(window, never),))

# The round the preview runs on. This is where the first recording used
# to be sent back to the recogniser while the second was separated.
waited_on = window.get("speakers_words_of")
vpm.voice_suggest_round(window, [], [], [], "", "", "eng", came_back)
check("a round while the second is separated sends nobody to listen",
      window.get("speakers_words_of") == waited_on,
      "the window now waits on %s, wanted it still on %s"
      % (os.path.basename(window.get("speakers_words_of") or "none"),
         os.path.basename(waited_on or "none")))
window["speakers_source"] = never
vpm.voice_suggest_round(window, [], [], [], "", "", "eng", came_back)
check("and a round for a recording nobody heard does ask for it",
      words_arrive(3) == 3,
      "%d answers came back in all, wanted 3" % len(back))
split_runs = heard["macos"] + heard["whisper"] - split_before
check("three recordings cost three recognitions, none of them twice",
      split_runs == 3,
      "%d recogniser runs for three recordings, wanted 3" % split_runs)

# A recording is still being written down when the next separation
# starts. On Windows that is a quarter of an hour, and a round in
# between must not set the same recogniser going a second time.
holding = threading.Event()
started = []
real_at_hand = vpm.words_at_hand


def slow_words(audio_path, language=""):
    """Stand in for the whole road: note the start, then wait."""
    started.append(audio_path)
    holding.wait(30.0)
    return [vpm.speech_word(0.0, 0.4, "held")]


def starts_settle(still=0.4):
    """Wait until no further recognition begins, and say how many did."""
    seen, quiet = len(started), 0.0
    while quiet < still:
        time.sleep(0.01)
        quiet = 0.0 if len(started) != seen else quiet + 0.01
        seen = len(started)
    return len(started)


vpm.words_at_hand = slow_words
slow = {"speakers_source": one, "axis": {},
        "speakers_local": window["speakers_local"]}
vpm.speech_words_kick_off(slow, "eng", lambda r: None, one)
vpm.speech_words_kick_off(slow, "eng", lambda r: None, two)
both_begun = starts_settle()
check("both separations really have a recognition running",
      both_begun == 2 and sorted(started) == sorted([one, two]),
      "%d recognitions began, on %s"
      % (both_begun, [os.path.basename(p) for p in started]))
vpm.voice_suggest_round(slow, [], [], [], "", "", "eng", lambda r: None)
starts_settle()
begun_for_one = len([p for p in started if p == one])
holding.set()
vpm.words_at_hand = real_at_hand
check("a recording still being written down is not started a second time",
      begun_for_one == 1,
      "the recogniser was started %d times for the one recording, wanted 1"
      % begun_for_one)

print("\n11. What the store lets go of again")
# Kept by fingerprint, so a folder of material seen once leaves an entry
# behind per file -- and every entry is refused after an update, which
# is why they have to go by age rather than wait to be read again.
vpm.cache_write("a" * 16, {"findings": []})
vpm.cache_write("b" * 16, {"findings": []})
stale, fresh = vpm.cache_path("a" * 16), vpm.cache_path("b" * 16)
os.utime(stale, (time.time() - 40 * 86400,) * 2)
vpm.clean_preflight_cache()
check("a measurement untouched for longer than the limit is let go",
      not os.path.exists(stale),
      "%s is still there" % os.path.basename(stale))
check("and one from this month is kept", os.path.exists(fresh),
      "%s went with it" % os.path.basename(fresh))
kept_preflight = vpm.cache_folder("preflight")
if kept_preflight:                      # inside this test's own cache
    shutil.rmtree(kept_preflight, ignore_errors=True)

vpm.macos_words, vpm.whisper_words = real_macos, real_whisper
for one_folder in folders:
    shutil.rmtree(one_folder, ignore_errors=True)
shutil.rmtree(said, ignore_errors=True)
kept_words = vpm.cache_folder("words")
if kept_words:                          # inside this test's own cache
    shutil.rmtree(kept_words, ignore_errors=True)

subprocess.run = run_real
shutil.rmtree(folder, ignore_errors=True)

print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
