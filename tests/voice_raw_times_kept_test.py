# -*- coding: utf-8 -*-
"""Local speaker separation: the arithmetic around the model.

The model itself is not run here -- it needs its own environment and
minutes of computing. Checked is everything around it, where the
mistakes would be: that segments are stored raw in the time of their
own file, that widening and moving them is arithmetic and not a second
measurement, that a changed way of working it out is not served out of
yesterday's store, that the worker keeps the rules that were measured,
and that the samples come back as wide as they were asked for --
narrow for the separation, which holds a whole episode in memory at
once.
"""
import os
import the_program
HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = the_program.SCRIPT
import ast
import json
import shutil
import subprocess
import sys
import tempfile
import time
vpm = the_program.load()

began = time.time()
done = 0
bad = []


def check(name, ok, extra=""):
    global done
    done += 1
    print("  %-58s %s %s" % (name, "ok" if ok else "FAIL", extra))
    if not ok:
        bad.append("%s [%s]" % (name, extra or "no numbers"))


RAW = [["SPEAKER_01", 10.0, 12.0], ["SPEAKER_00", 1.0, 4.0],
       ["SPEAKER_00", 4.1, 6.0], ["SPEAKER_01", 20.0, 21.0]]

print("1. The raw answer becomes speakers with their stretches")
grouped = vpm.speaker_segments_group(RAW)
check("one entry per voice", len(grouped) == 2, str(len(grouped)))
check("the one who spoke most stands first",
      grouped[0][0] == "SPEAKER_00", grouped[0][0])
check("the stretches are in order",
      grouped[0][1] == [(1.0, 4.0), (4.1, 6.0)], str(grouped[0][1]))
mixed = vpm.speaker_segments_group(RAW + [["X"], ["Y", "a", "b"]])
check("a broken row is left out, the rest stands", len(mixed) == 2,
      "%d voices against 2: %s" % (len(mixed), [v for v, _p in mixed]))
empty = vpm.speaker_segments_group([])
check("nothing at all is nothing", empty == [], "%r against []" % (empty,))

print("\n2. Widening the edges and closing the gaps")
polished = dict(vpm.speaker_segments_polish(grouped))
check("the two stretches 0.1 s apart became one",
      polished["SPEAKER_00"] == [(0.8, 6.2)], str(polished["SPEAKER_00"]))
check("a real pause is not closed",
      len(polished["SPEAKER_01"]) == 2, str(polished["SPEAKER_01"]))
at_zero = vpm.speaker_segments_polish([("A", [(0.05, 1.0)])])[0][1][0][0]
check("nothing moves before zero", at_zero == 0.0,
      "start %.3f s against 0.000 s, from a raw 0.05 s widened by %s s"
      % (at_zero, vpm.SPEAKER_MARGIN_S))
check("the edge is the measured 0.2 s", vpm.SPEAKER_MARGIN_S == 0.2,
      "SPEAKER_MARGIN_S %r s against 0.2 s" % (vpm.SPEAKER_MARGIN_S,))
check("the closing distance is the measured 0.75 s",
      vpm.SPEAKER_GAP_S == 0.75,
      "SPEAKER_GAP_S %r s against 0.75 s" % (vpm.SPEAKER_GAP_S,))
# Widening happens first, so a hole in the raw list has 0.4 s taken off
# it before the distance is measured. The middle one is the point of
# the three: 0.9 s raw is 0.5 s widened, which the old 0.25 s left
# standing and the measured 0.75 s closes.
holes = dict(vpm.speaker_segments_polish(
    [("A", [(10.0, 12.0), (12.5, 14.0)]),
     ("B", [(20.0, 22.0), (22.9, 24.0)]),
     ("C", [(30.0, 32.0), (33.5, 35.0)])]))
check("a hole of 0.5 s inside one speaker is closed",
      holes["A"] == [(9.8, 14.2)],
      "%s against [(9.8, 14.2)]" % (holes["A"],))
check("and one of 0.9 s, which the old distance left open",
      holes["B"] == [(19.8, 24.2)],
      "%s against [(19.8, 24.2)]" % (holes["B"],))
check("a hole of 1.5 s stays a change of speaker",
      holes["C"] == [(29.8, 32.2), (33.3, 35.2)],
      "%s against [(29.8, 32.2), (33.3, 35.2)]" % (holes["C"],))
check("and the stored measurement is untouched",
      grouped[0][1] == [(1.0, 4.0), (4.1, 6.0)],
      "%s against [(1.0, 4.0), (4.1, 6.0)]" % (grouped[0][1],))

print("\n3. From the time of the file onto the common axis")
# Whatever a recording heard before the episode began has to fall out,
# not be carried along.
moved = vpm.speaker_segments_on_axis(grouped, 924.6)
check("the offset is added on",
      moved[0][1][0] == (925.6, 928.6), str(moved[0][1][0]))
lead = vpm.speaker_segments_on_axis(grouped, 0.0, 5.0, 21.0)
check("what lies before the In point falls out",
      dict(lead)["SPEAKER_00"] == [(0.0, 1.0)], str(dict(lead)))
check("and what is left is counted from the In point",
      dict(lead)["SPEAKER_01"] == [(5.0, 7.0), (15.0, 16.0)],
      str(dict(lead)["SPEAKER_01"]))
gone = vpm.speaker_segments_on_axis(grouped, 0.0, 100.0, 200.0)
check("a voice with nothing left in the window is left out",
      gone == [], str(gone))
twice = vpm.speaker_segments_on_axis(
    vpm.speaker_segments_on_axis(grouped, 900.0), 24.6)
check("moving a second time gives the same as moving once",
      twice == moved, "%s against %s" % (twice, moved))

print("\n4. Naming the voices")
names = dict(vpm.speaker_label_names(grouped))
check("whoever spoke most is the first one",
      names["SPEAKER_00"] == "Speaker 1", names["SPEAKER_00"])
given = dict(vpm.speaker_label_names(grouped, {"SPEAKER_00": "Anna"}))
check("a name given by hand stays", given["SPEAKER_00"] == "Anna",
      "%r against 'Anna'" % (given["SPEAKER_00"],))

print("\n5. Everything counts per camera, not per speaker")
per = dict(vpm.segments_per_camera(
    grouped, {"Anna": "A.mov", "Bert": "A.mov"},
    {"SPEAKER_00": "Anna", "SPEAKER_01": "Bert"}))
check("two speakers on one camera are one series",
      list(per) == ["A.mov"], str(list(per)))
check("and what either of them did counts",
      per["A.mov"] == [(1.0, 4.0), (4.1, 6.0), (10.0, 12.0), (20.0, 21.0)],
      str(per["A.mov"]))
touching = vpm.segments_per_camera(
    [("a", [(0.0, 5.0)]), ("b", [(4.0, 9.0)])],
    {"a": "A.mov", "b": "A.mov"})
check("overlapping stretches of the two are merged",
      touching == [("A.mov", [(0.0, 9.0)])], str(touching))
two = vpm.segments_per_camera(
    grouped, {"Anna": "A.mov", "Bert": "B.mov"},
    {"SPEAKER_00": "Anna", "SPEAKER_01": "Bert"})
check("two cameras stay two", len(two) == 2, str(len(two)))
left_out = vpm.segments_per_camera(
    grouped, {"Anna": vpm.IGNORE_AUDIO, "Bert": "B.mov"},
    {"SPEAKER_00": "Anna", "SPEAKER_01": "Bert"})
check("a track left out contributes nothing",
      [c for c, _p in left_out] == ["B.mov"], str(left_out))

print("\n6. Which file the separation listens to")
folder = tempfile.mkdtemp(prefix="vpm_split_")


def touch(name, size=1000):
    p = os.path.join(folder, name)
    with open(p, "wb") as f:
        f.write(b"\0" * size)
    return p


one = touch("Zoom.wav")
two_a, two_b = touch("Anna.wav"), touch("Bert.wav")
cam_a, cam_b = touch("A.mov", 2000), touch("B.mov", 4000)


def told(v):
    """A picked (path, why) with this run's temporary folder as ".../".

    The same shortening on the wanted side, so a path from anywhere
    else keeps its full name and still shows up as different.
    """
    return repr(v).replace(folder + os.sep, ".../").replace(folder, "...")


single = vpm.speaker_source_pick([one], [cam_a])
check("one recording is the one", single == (one, "one recording"),
      "%s against %s" % (told(single), told((one, "one recording"))))
mics = vpm.speaker_source_pick([two_a, two_b], [cam_a])
check("several microphones: the tracks are the truth, so it stays out",
      mics == ("", "several microphones"),
      "%s against %s" % (told(mics), told(("", "several microphones"))))
picked = vpm.speaker_source_pick([one], [cam_a], chosen=cam_a)
check("a choice made by hand comes first", picked[1] == "chosen",
      "%s against a why of 'chosen'" % told(picked))
longest = vpm.speaker_source_pick([], [cam_a, cam_b], [cam_a, cam_b],
                                  length_of=os.path.getsize)
check("without a recording the longest camera track is used",
      longest == (cam_b, "camera track"),
      "%s against %s, A.mov %d bytes and B.mov %d bytes"
      % (told(longest), told((cam_b, "camera track")),
         os.path.getsize(cam_a), os.path.getsize(cam_b)))
all_tracks = vpm.speaker_source_pick([], [cam_a, cam_b], camera_audio=True,
                                     length_of=os.path.getsize)
check("cameras that are all tracks count as well",
      all_tracks[1] == "camera track",
      "%s against a why of 'camera track'" % told(all_tracks))
nowhere = vpm.speaker_source_pick([one], [], placeless=[one])
check("a recording the measurement placed nowhere is not listened to",
      nowhere == ("", "nothing"),
      "%s against %s" % (told(nowhere), told(("", "nothing"))))
anyway = vpm.speaker_source_pick([one], [], placeless=[])
check("but one that has a place is, whatever its sound scored",
      anyway == (one, "one recording"),
      "%s against %s" % (told(anyway), told((one, "one recording"))))
# What the window hands over is a call, not a value this can read back,
# so the program's own text is the only place the answer stands.
program = the_program.text()
check("the window hands over what nothing could place, not what "
      "sounded weak",
      'placeless=state.get("no_place")' in program
      and 'weak=state.get("weak")' not in program,
      "no_place handed over: %r, weak handed over: %r"
      % ('placeless=state.get("no_place")' in program,
         'weak=state.get("weak")' in program))
nothing = vpm.speaker_source_pick([], [])
check("nothing at all says so", nothing[1] == "nothing",
      "%s against a why of 'nothing'" % told(nothing))
check("the mix from auphonic.com is not offered",
      vpm.SPEAKER_SOURCE_MIX_ALLOWED is False,
      "SPEAKER_SOURCE_MIX_ALLOWED %r against False"
      % (vpm.SPEAKER_SOURCE_MIX_ALLOWED,))

print("\n7. What is measured again, and what is not")
key = vpm.speaker_cache_key(one, "model1", 0)
again = vpm.speaker_cache_key(one, "model1", 0)
check("the same file and model give the same name", key == again,
      "%r twice against %r" % (again, key))
other_model = vpm.speaker_cache_key(one, "model2", 0)
check("another model is another measurement", key != other_model,
      "model1 %r, model2 %r, wanted two different ones"
      % (key, other_model))
three = vpm.speaker_cache_key(one, "model1", 3)
check("a number of speakers set by hand is another measurement",
      key != three,
      "no number %r, three speakers %r, wanted two different ones"
      % (key, three))
other_file = vpm.speaker_cache_key(two_a, "model1", 0)
check("another file is another measurement", key != other_file,
      "Zoom.wav %r, Anna.wav %r, wanted two different ones"
      % (key, other_file))
os.utime(one, (1000, 1000))
early = vpm.speaker_cache_key(one, "model1", 0)
os.utime(one, (2000, 2000))
later = vpm.speaker_cache_key(one, "model1", 0)
check("a changed file is measured again", early != later,
      "mtime 1000 %r, mtime 2000 %r, wanted two different ones"
      % (early, later))

# The way the answer is worked out belongs in the key as much as the
# file does. Eight minutes of computing is the sort of result nobody
# repeats to check, so a changed reckoning that quietly handed back
# yesterday's answer would never be noticed.
kept_mix = vpm.speaker_mix_file
# Read again here rather than reusing the one from the top: the file's
# date was moved in between, so that one differs for a second reason
# and would have said yes whatever the reckoning did.
today = vpm.speaker_cache_key(one, "model1", 0)
stored_key = vpm.speaker_cache_key(one, vpm.speaker_model_mark(), 0)
vpm.speaker_cache_write(stored_key, grouped)
check("a separation stored under this reckoning is read back",
      vpm.speaker_split_stored(one) == grouped,
      "%s against %s" % (vpm.speaker_split_stored(one), grouped))


def another_mix(paths, made_of, folder=""):
    """A different way of making the mix, so the reckoning has moved."""
    return ""


vpm.speaker_mix_file = another_mix
del vpm._SPEAKER_RECIPE[:]
moved = vpm.speaker_cache_key(one, "model1", 0)
check("a changed reckoning is another measurement", today != moved,
      "the reckoning of today %r, a changed one %r, wanted two "
      "different ones" % (today, moved))
check("and the answer stored under the old one is not read back",
      vpm.speaker_split_stored(one) == [],
      "%d voices came back, wanted 0"
      % len(vpm.speaker_split_stored(one)))
vpm.speaker_mix_file = kept_mix
del vpm._SPEAKER_RECIPE[:]
check("while the old reckoning still finds it",
      vpm.speaker_split_stored(one) == grouped,
      "%s against %s" % (vpm.speaker_split_stored(one), grouped))
if vpm.speaker_cache_file(stored_key):
    try:
        os.remove(vpm.speaker_cache_file(stored_key))
    except OSError:
        pass

print("\n8. Through the project file and back")
d = {}
d["speakers"] = vpm.speakers_for_project(one, grouped, 0,
                                         {"SPEAKER_00": "Anna"})
d = json.loads(json.dumps(d))
source, back, called = vpm.speakers_from_project(d)
check("the source comes back", source == os.path.abspath(one), source)
check("the segments come back unchanged", back == grouped, str(back))
check("the names come back", called == {"SPEAKER_00": "Anna"}, str(called))
check("they are stored raw, without the widened edges",
      d["speakers"]["segments"][0][1] == 1.0,
      str(d["speakers"]["segments"][0]))
stale = vpm.speakers_from_project(d, fingerprint=lambda p: [p, 7, 7])[1]
check("a changed source is not carried on wrongly", stale == [],
      "%r against [], for a source of 7 bytes at mtime 7 against the "
      "stored %d bytes at mtime %d"
      % (stale, d["speakers"]["size"], d["speakers"]["mtime"]))
unstored = vpm.speakers_from_project({})[1]
check("nothing stored is nothing read", unstored == [],
      "%r against []" % (unstored,))

print("\n9. The three rules of the worker process")
try:
    worker = ast.parse(vpm.SPEAKER_SPLIT_WORKER)
    compile(vpm.SPEAKER_SPLIT_WORKER, "worker", "exec")
    broken = ""
except SyntaxError as e:
    worker, broken = None, "line %s: %s" % (e.lineno, e.msg)
check("the worker is a program in its own right", not broken, broken)
if worker is None:
    print("\n%d checks in %.2f s" % (done, time.time() - began))
    print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
    sys.exit(1 if bad else 0)
body = [n for n in worker.body if isinstance(n, ast.FunctionDef)]
first = [n for n in body if n.name == "main"][0].body[0]
check("the first thing main does is switch the telemetry off",
      isinstance(first, ast.If)
      and "hush" in ast.dump(first.test), ast.dump(first.test)[:60])
reports = [v.value for n in ast.walk(first) if isinstance(n, ast.Dict)
           for v in n.values if isinstance(v, ast.Constant)]
check("and without that switch it refuses to run",
      "telemetry" in ast.dump(first),
      "'telemetry' found %d times in that branch, wanted at least 1; "
      "it reports %s"
      % (ast.dump(first).count("telemetry"), reports))
check("the waveform goes in, not the path",
      '"waveform"' in vpm.SPEAKER_SPLIT_WORKER
      and "16000" not in vpm.SPEAKER_SPLIT_WORKER,
      '"waveform" found %d times and "16000" %d times in the worker, '
      "wanted at least 1 and 0"
      % (vpm.SPEAKER_SPLIT_WORKER.count('"waveform"'),
         vpm.SPEAKER_SPLIT_WORKER.count("16000")))
check("mono 16 kHz is what the parent decodes to",
      vpm.SPEAKER_SPLIT_RATE == 16000,
      "SPEAKER_SPLIT_RATE %r against 16000" % (vpm.SPEAKER_SPLIT_RATE,))
WANT_ASKED = 'if int(head.get("speakers") or 0) > 0:'
WANT_MODEL = 'Pipeline.from_pretrained(head["model"])'
asked = [ln.strip() for ln in vpm.SPEAKER_SPLIT_WORKER.splitlines()
         if 'head.get("speakers")' in ln]
check("a number of speakers is passed only when it was asked for",
      WANT_ASKED in vpm.SPEAKER_SPLIT_WORKER,
      "the worker says %s, wanted [%r]" % (asked, WANT_ASKED))
loads = [ln.strip() for ln in vpm.SPEAKER_SPLIT_WORKER.splitlines()
         if "from_pretrained" in ln]
check("the model comes out of a folder, never off a server",
      WANT_MODEL in vpm.SPEAKER_SPLIT_WORKER,
      "the worker says %s, wanted [%r]" % (loads, WANT_MODEL))

print("\n10. How wide the samples come back")
# The separation holds the whole episode in memory at once, so the
# width of that block is the largest the program ever asks for: on an
# 87 minute interview it was 1095 MB in float32 against 1428 MB in
# float64. Every other caller wants the wide form and must keep it.
tone_folder = tempfile.mkdtemp(prefix="vpm_dtype_")
tone = os.path.join(tone_folder, "tone.wav")
# ffmpeg builds the material here; a failure of it says nothing about
# the program, so it stops the run outright instead of being judged.
subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i",
                "sine=frequency=440:duration=0.2", "-ac", "1",
                "-ar", str(vpm.SPEAKER_SPLIT_RATE), tone], check=True)
wide = vpm.decode_audio(tone, vpm.SPEAKER_SPLIT_RATE)
narrow = vpm.decode_audio(tone, vpm.SPEAKER_SPLIT_RATE,
                          dtype=vpm.np.float32)
check("the test tone decodes to samples at all", len(wide) > 0,
      "%d samples out of 0.2 s at %d Hz, wanted more than 0"
      % (len(wide), vpm.SPEAKER_SPLIT_RATE))
check("without a dtype the samples stay float64",
      wide.dtype == vpm.np.float64,
      "%s at %d bytes a sample against float64 at 8"
      % (wide.dtype.name, wide.itemsize))
check("asked for float32 the samples come back float32",
      narrow.dtype == vpm.np.float32,
      "%s at %d bytes a sample against float32 at 4"
      % (narrow.dtype.name, narrow.itemsize))


def dtype_told(x):
    """Name a dtype for the report -- None is nothing, not float64.

    numpy answers np.dtype(None) with float64, which would print the
    default where the argument was missing and send whoever reads the
    line after the wrong thing.
    """
    if x is None:
        return "none given"
    try:
        return vpm.np.dtype(x).name
    except TypeError:
        return repr(x)


asked, handed = [], []


def decode_recorder(path, rate=vpm.SR, ss=None, duration=None,
                    stream=None, dtype=None):
    """The decoder's own signature, and its one habit: it obeys dtype.

    A stand-in that always answered float32 would leave the check on
    what the worker gets green however wide a copy the program makes
    of it afterwards.
    """
    asked.append(dtype)
    return vpm.np.zeros(8, dtype=vpm.np.float32).astype(
        dtype or vpm.np.float64)


def talk_recorder(python, worker, head, wave, environment, report,
                  stopping):
    """Where the waveform leaves for the worker process."""
    handed.append(wave)
    return [], ""


real = (vpm.speaker_model_folder, vpm.speaker_model_checked,
        vpm.speaker_venv_python, vpm.speaker_worker_file,
        vpm.decode_audio, vpm._speaker_split_talk)
# The four things the run wants in place before it decodes anything.
vpm.speaker_model_folder = lambda: tone_folder
vpm.speaker_model_checked = lambda folder="": ""
vpm.speaker_venv_python = lambda folder="": os.path.join(tone_folder,
                                                         "python")
vpm.speaker_worker_file = lambda: os.path.join(tone_folder, "worker.py")
vpm.decode_audio = decode_recorder
vpm._speaker_split_talk = talk_recorder
try:
    _segments, why = vpm.speaker_split_run(tone)
finally:
    (vpm.speaker_model_folder, vpm.speaker_model_checked,
     vpm.speaker_venv_python, vpm.speaker_worker_file,
     vpm.decode_audio, vpm._speaker_split_talk) = real
last_asked = dtype_told(asked[-1]) if asked else "not called at all"
check("the separation asks the decoder for float32",
      len(asked) == 1 and last_asked == "float32",
      "the decoder was called %d times, the last for %s, wanted 1 time "
      "for float32; the separation answered %r"
      % (len(asked), last_asked, why))
last_handed = handed[-1].dtype.name if handed else "nothing at all"
check("and the wave the worker gets is still the narrow one",
      len(handed) == 1 and last_handed == "float32",
      "the worker was handed %d waves, the last %s at %d bytes a "
      "sample, wanted 1 wave of float32 at 4"
      % (len(handed), last_handed,
         handed[-1].itemsize if handed else 0))
shutil.rmtree(tone_folder, ignore_errors=True)

print("\n11. The model that travels with the program")
model = vpm.speaker_model_folder()
SHIPPED = os.path.join(os.path.dirname(HERE), "models",
                       vpm.SPEAKER_MODEL_NAME)
if not model and os.path.isfile(os.path.join(SHIPPED, "config.yaml")):
    # A suite is often run against a snapshot of the program in a
    # temporary folder. The model is data and does not travel with a
    # copy of the script, so the checkout's own is read instead --
    # without this the whole section fell away and said so to nobody.
    model = SHIPPED
    print("  the script under test stands alone in %s,"
          % os.path.dirname(SCRIPT))
    print("  so the model read here is the checkout's own")
# Red rather than passed over: the model ships with the program, every
# checkout carries it, and a machine that has none has a broken one.
check("the model is where a checkout puts it", bool(model),
      os.path.basename(model) if model else
      "no config.yaml beside %s and none in %s" % (SCRIPT, SHIPPED))
if model:
    check("every weight matches its checksum",
          vpm.speaker_model_checked(model) == "",
          vpm.speaker_model_checked(model))
    check("the model has a mark of its own",
          len(vpm.speaker_model_mark(model)) == 12,
          vpm.speaker_model_mark(model))
    sums = vpm.read_checksums(os.path.join(model, "SHA256SUMS.txt"))
    check("the checksum file names more than one file", len(sums) > 1,
          str(len(sums)))
    missing = [n for n in sorted(sums)
               if not os.path.exists(os.path.join(model, n))]
    check("and every name in it is a file that is there", not missing,
          "%d of %d names have no file: %s"
          % (len(missing), len(sums), missing))

print("\n12. One separation at a time")
first_go = vpm.SPEAKER_SPLIT_TURN.acquire(blocking=False)
second_go = first_go and vpm.SPEAKER_SPLIT_TURN.acquire(blocking=False)
check("there is room for exactly one", first_go and not second_go,
      "first go %s, second go %s, wanted True and False"
      % (first_go, second_go))
if second_go:
    vpm.SPEAKER_SPLIT_TURN.release()
if first_go:
    vpm.SPEAKER_SPLIT_TURN.release()
check("from four processors up everything runs at once",
      vpm.SPEAKER_SPLIT_TOGETHER_CORES == 4,
      "SPEAKER_SPLIT_TOGETHER_CORES %r against 4"
      % (vpm.SPEAKER_SPLIT_TOGETHER_CORES,))

print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
