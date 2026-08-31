# -*- coding: utf-8 -*-
"""Where the speakers of a run come from, and how they reach it."""
import os
HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = os.environ.get("VPM_SCRIPT") or os.path.join(
    os.path.dirname(HERE), "videopodcast-magic.py")
import importlib.util, json, sys, tempfile, time
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


def values(**k):
    state = {"files": [], "clip_kinds": {}, "out_folder": "",
             "dry_run": False, "multitrack": False,
             "camera_audio_only": False, "rows": [], "cameras": [],
             "production": "", "in_point": "", "out_point": "", "cut": {},
             "wide_at_edges": True, "key": "", "preset": "",
             "done_folder": ""}
    state.update(k)
    return state


print("1. The separation travels in the assignment file")
rows = [{"blocks": ["/x/A.wav"], "speakers": "Host",
         "camera_choice": "CamA.mov"},
        {"blocks": ["/x/B.wav"], "speakers": "Guest",
         "camera_choice": "CamB.mov"}]
files = [("/x/A.wav", "audio"), ("/x/B.wav", "audio"),
         ("/x/CamA.mov", "video"), ("/x/CamB.mov", "video")]
cameras = [{"path": "/x/CamA.mov", "name": "CamA"},
           {"path": "/x/CamB.mov", "name": "CamB"}]
heard = {"source": "/x/room.wav", "names": {"SPEAKER_00": "Host"},
         "segments": [["SPEAKER_00", 1.0, 4.0]]}
_a, plan, _m = vpm.run_argv(values(
    multitrack=True, files=files, rows=rows, cameras=cameras),
    "/tmp/assign.json")
check("without a separation the key stays away",
      "speakers_of" not in (plan or {}), str(sorted(plan or {})))
_a, plan, _m = vpm.run_argv(values(
    multitrack=True, files=files, rows=rows, cameras=cameras,
    speakers_of=heard), "/tmp/assign.json")
check("with one it is in the plan", plan.get("speakers_of") == heard,
      str(plan.get("speakers_of")))

print("\n2. Reading it back out of a file")
D = tempfile.mkdtemp(prefix="vpmspeak_")
with open(os.path.join(D, "assign.json"), "w", encoding="utf-8") as f:
    json.dump({"tracks_of": [], "speakers_of": heard}, f)
with open(os.path.join(D, "project.json"), "w", encoding="utf-8") as f:
    json.dump({"files": [], "speakers": heard}, f)
with open(os.path.join(D, "nothing.json"), "w", encoding="utf-8") as f:
    json.dump({"files": []}, f)
check("out of an assignment file",
      vpm.read_separation_file(os.path.join(D, "assign.json")) == heard)
check("out of a project file",
      vpm.read_separation_file(os.path.join(D, "project.json")) == heard)
check("a file without one gives nothing",
      vpm.read_separation_file(os.path.join(D, "nothing.json")) == {})

print("\n3. Onto the axis of the run")
# The recording sits two seconds behind the reference camera, and the
# window starts ten seconds in.
tracks = [{"name": "Host", "blocks": ["/x/A.wav"], "a": 0.0, "b": 1.0},
          {"name": "Guest", "blocks": ["/x/B.wav"], "a": 0.0, "b": 1.0}]
position = {"/x/CamA.mov": (2.0, 1.0, {})}
given = {"source": "/x/CamA.mov",
         "names": {"SPEAKER_00": "Host", "SPEAKER_01": "Guest"},
         "segments": [["SPEAKER_00", 20.0, 30.0],
                      ["SPEAKER_01", 31.0, 40.0],
                      ["SPEAKER_00", 8.0, 15.0]]}
out, why_not = vpm.separation_on_axis(given, tracks, position, 10.0, 60.0)
check("it works", not why_not, why_not)
names = dict(out)
check("the names come along", sorted(names) == ["Guest", "Host"], str(out))
# 20 s in the file, widened by 0.2 s, minus the offset of 2 s, minus the
# window start of 10 s.
check("a section lands where it belongs",
      names["Host"][1] == (7.8, 18.2), str(names["Host"]))
check("what lies before the window is trimmed",
      names["Host"][0] == (0.0, 3.2), str(names["Host"][0]))

print("\n4. A recording that is not part of the run is said so")
_out, why_not = vpm.separation_on_axis(
    {"source": "/x/elsewhere.wav", "segments": [["A", 1.0, 2.0]]},
    tracks, position, 0.0, 60.0)
check("it names the file", "elsewhere.wav" in why_not, why_not)
_out, why_not = vpm.separation_on_axis({}, tracks, position, 0.0, 60.0)
check("and an empty one is refused too", bool(why_not), why_not)

print("\n5. One minimum edit duration, not two")
check("the switch and the constant agree",
      vpm.MIN_EDIT_DURATION_S == 3.0, str(vpm.MIN_EDIT_DURATION_S))
for name in ("camera_cut", "cut_statistics", "build_camera_cut",
             "camera_cut_detail", "split_shots_by_speaker"):
    import inspect
    default = inspect.signature(getattr(vpm, name)).parameters[
        "min_len"].default
    check("%s defaults to it" % name, default == vpm.MIN_EDIT_DURATION_S,
          str(default))
field = [f for f in vpm.CUT_FIELDS if f[0] == "min-edit-duration"][0]
check("and the field in the window shows the same",
      float(field[2]) == vpm.MIN_EDIT_DURATION_S, field[2])

print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
