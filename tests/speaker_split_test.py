# -*- coding: utf-8 -*-
"""Local speaker separation: the arithmetic around the model.

The model itself is not run here -- it needs an environment of its own
and minutes of computing. What is checked is everything around it, and
that is where the mistakes would be: that the segments are stored raw
and in the time of their own file, that widening and moving them is
arithmetic rather than a second measurement, that a file which starts
minutes early does not smuggle speech into the episode, that two
speakers on one camera become one condition, and that the worker keeps
the three rules that were measured -- telemetry off first of all, the
waveform rather than the path, and no number of speakers unless
somebody asked for one.
"""
import os
HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = os.environ.get("VPM_SCRIPT") or os.path.join(
    os.path.dirname(HERE), "videopodcast-magic.py")
import ast
import importlib.util
import json
import sys
import tempfile
spec = importlib.util.spec_from_file_location("vpm", SCRIPT)
vpm = importlib.util.module_from_spec(spec); sys.modules["vpm"] = vpm
spec.loader.exec_module(vpm)

error = []


def check(name, ok, extra=""):
    print("  %-56s %s %s" % (name, "ok" if ok else "FAIL", extra))
    if not ok:
        error.append(name)


RAW = [["SPEAKER_01", 10.0, 12.0], ["SPEAKER_00", 1.0, 4.0],
       ["SPEAKER_00", 4.1, 6.0], ["SPEAKER_01", 20.0, 21.0]]

print("1. The raw answer becomes speakers with their stretches")
grouped = vpm.speaker_segments_group(RAW)
check("one entry per voice", len(grouped) == 2, str(len(grouped)))
check("the one who spoke most stands first",
      grouped[0][0] == "SPEAKER_00", grouped[0][0])
check("the stretches are in order",
      grouped[0][1] == [(1.0, 4.0), (4.1, 6.0)], str(grouped[0][1]))
check("a broken row is left out, the rest stands",
      len(vpm.speaker_segments_group(RAW + [["X"], ["Y", "a", "b"]])) == 2)
check("nothing at all is nothing", vpm.speaker_segments_group([]) == [])

print("\n2. Widening the edges and closing the gaps")
polished = dict(vpm.speaker_segments_polish(grouped))
check("the two stretches 0.1 s apart became one",
      polished["SPEAKER_00"] == [(0.8, 6.2)], str(polished["SPEAKER_00"]))
check("a real pause is not closed",
      len(polished["SPEAKER_01"]) == 2, str(polished["SPEAKER_01"]))
check("nothing moves before zero",
      vpm.speaker_segments_polish([("A", [(0.05, 1.0)])])[0][1][0][0] == 0.0)
check("the edge is the measured 0.2 s", vpm.SPEAKER_MARGIN_S == 0.2)
check("and the stored measurement is untouched",
      grouped[0][1] == [(1.0, 4.0), (4.1, 6.0)])

print("\n3. From the time of the file onto the common axis")
# A recording that started 924.6 s before the episode: everything it
# heard in that lead-in has to fall out, not be carried along.
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
check("moving a second time gives the same as moving once",
      vpm.speaker_segments_on_axis(grouped, 924.6)
      == vpm.speaker_segments_on_axis(grouped, 924.6))

print("\n4. Naming the voices")
names = dict(vpm.speaker_label_names(grouped))
check("whoever spoke most is the first one",
      names["SPEAKER_00"] == "Speaker 1", names["SPEAKER_00"])
check("a name given by hand stays",
      dict(vpm.speaker_label_names(
          grouped, {"SPEAKER_00": "Anna"}))["SPEAKER_00"] == "Anna")

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
check("one recording is the one",
      vpm.speaker_source_pick([one], [cam_a]) == (one, "one recording"))
check("several microphones: the tracks are the truth, so it stays out",
      vpm.speaker_source_pick([two_a, two_b], [cam_a])
      == ("", "several microphones"))
check("a choice made by hand comes first",
      vpm.speaker_source_pick([one], [cam_a], chosen=cam_a)[1] == "chosen")
check("without a recording the longest camera track is used",
      vpm.speaker_source_pick([], [cam_a, cam_b], [cam_a, cam_b],
                              length_of=os.path.getsize)
      == (cam_b, "camera track"))
check("cameras that are all tracks count as well",
      vpm.speaker_source_pick([], [cam_a, cam_b], camera_audio=True,
                              length_of=os.path.getsize)[1]
      == "camera track")
check("a file the measurement called unfit is not listened to",
      vpm.speaker_source_pick([one], [], weak=[one]) == ("", "nothing"))
check("nothing at all says so", vpm.speaker_source_pick([], []) [1]
      == "nothing")
check("the mix from auphonic.com is not offered",
      vpm.SPEAKER_SOURCE_MIX_ALLOWED is False)

print("\n7. What is measured again, and what is not")
key = vpm.speaker_cache_key(one, "model1", 0)
check("the same file and model give the same name",
      key == vpm.speaker_cache_key(one, "model1", 0))
check("another model is another measurement",
      key != vpm.speaker_cache_key(one, "model2", 0))
check("a number of speakers set by hand is another measurement",
      key != vpm.speaker_cache_key(one, "model1", 3))
check("another file is another measurement",
      key != vpm.speaker_cache_key(two_a, "model1", 0))
os.utime(one, (1000, 1000))
early = vpm.speaker_cache_key(one, "model1", 0)
os.utime(one, (2000, 2000))
check("a changed file is measured again",
      early != vpm.speaker_cache_key(one, "model1", 0))

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
check("a changed source is not carried on wrongly",
      vpm.speakers_from_project(
          d, fingerprint=lambda p: [p, 7, 7])[1] == [])
check("nothing stored is nothing read", vpm.speakers_from_project({}) [1]
      == [])

print("\n9. The three rules of the worker process")
worker = ast.parse(vpm.SPEAKER_SPLIT_WORKER)
body = [n for n in worker.body if isinstance(n, ast.FunctionDef)]
first = [n for n in body if n.name == "main"][0].body[0]
check("the first thing main does is switch the telemetry off",
      isinstance(first, ast.If)
      and "hush" in ast.dump(first.test), ast.dump(first.test)[:60])
check("and without that switch it refuses to run",
      "telemetry" in ast.dump(first))
check("the waveform goes in, not the path",
      '"waveform"' in vpm.SPEAKER_SPLIT_WORKER
      and "16000" not in vpm.SPEAKER_SPLIT_WORKER)
check("mono 16 kHz is what the parent decodes to",
      vpm.SPEAKER_SPLIT_RATE == 16000)
check("a number of speakers is passed only when it was asked for",
      'if int(head.get("speakers") or 0) > 0:' in vpm.SPEAKER_SPLIT_WORKER)
check("the model comes out of a folder, never off a server",
      'Pipeline.from_pretrained(head["model"])' in vpm.SPEAKER_SPLIT_WORKER)
check("the worker is a program in its own right",
      compile(vpm.SPEAKER_SPLIT_WORKER, "worker", "exec") is not None)

print("\n10. The model that travels with the program")
model = vpm.speaker_model_folder()
if not model:
    print("  (no model folder beside the program -- not checked here)")
else:
    check("every weight matches its checksum",
          vpm.speaker_model_checked(model) == "",
          vpm.speaker_model_checked(model))
    check("the model has a mark of its own",
          len(vpm.speaker_model_mark(model)) == 12,
          vpm.speaker_model_mark(model))
    sums = vpm.read_checksums(os.path.join(model, "SHA256SUMS.txt"))
    check("the checksum file names more than one file", len(sums) > 1,
          str(len(sums)))
    check("and every name in it is a file that is there",
          all(os.path.exists(os.path.join(model, n)) for n in sums))

print("\n11. One separation at a time")
check("there is room for exactly one",
      vpm.SPEAKER_SPLIT_TURN.acquire(blocking=False)
      and not vpm.SPEAKER_SPLIT_TURN.acquire(blocking=False))
vpm.SPEAKER_SPLIT_TURN.release()
check("from four processors up everything runs at once",
      vpm.SPEAKER_SPLIT_TOGETHER_CORES == 4)

print("\n%s" % ("ALL OK" if not error else "FAIL: " + ", ".join(error)))
sys.exit(1 if error else 0)
