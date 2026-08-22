# -*- coding: utf-8 -*-
"""Checks: on reuse the tracks are switched over one at a time."""
import os
HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = os.environ.get("VPM_SCRIPT") or os.path.join(
    os.path.dirname(HERE), "videopodcast-magic.py")
import importlib.util, json, sys, copy

spec = importlib.util.spec_from_file_location(
    "vpm", SCRIPT)
vpm = importlib.util.module_from_spec(spec); sys.modules["vpm"] = vpm
spec.loader.exec_module(vpm)

UUID = "PresetTestProduction01"
OLD = {"filtering": True, "denoise": False, "gain": 0}
NEW = {"filtering": True, "denoise": True,
       "denoisemethod": "speech_isolation", "gain": 0, "deverbamount": 12}
NAMES = ["Guest", "Host", "Co-host"]

def production():
    return {"uuid": UUID, "status_string": "Done", "is_multitrack": True,
            "output_files": [{"format": "tracks", "filename": "x.zip"},
                             {"format": "stats", "filename": "x.json"},
                             {"format": "wav-24bit",
                              "filename": "x_master.wav"}],
            "multi_input_files": [
                {"id": n, "input_file": "axis_%s.wav" % n, "service": None,
                 "type": "multitrack", "offset": 0.0,
                 "algorithms": dict(OLD)} for n in NAMES]}

world = {"p": production(), "calls": []}

def fake_curl(key, arguments, output_binary=False, progress=False):
    target = [a for a in arguments if a.startswith("https://")][0]
    body = None
    if "-d" in arguments:
        file_path = arguments[arguments.index("-d") + 1][1:]
        body = json.load(open(file_path, encoding="utf-8"))
    world["calls"].append((target.replace(vpm.AUPHONIC, ""), body))
    if "/multi_input_files/" in target and body:
        sid = target.rsplit("/", 1)[-1].split(".")[0]
        for t in world["p"]["multi_input_files"]:
            if t["id"] == sid:
                t["algorithms"] = dict(body["algorithms"])
        return json.dumps({"status_code": 200}).encode()
    if target.endswith("/start.json"):
        return json.dumps({"status_code": 200}).encode()
    if body is not None:                       # change the production
        assert "multi_input_files" not in body, \
            "FAIL: the track list went to the production after all!"
        world["p"].update({k: v for k, v in body.items()
                           if k != "output_files"})
        return json.dumps({"status_code": 200, "data": world["p"]}).encode()
    return json.dumps({"data": copy.deepcopy(world["p"])}).encode()

vpm._curl_call = fake_curl
vpm.wait_for_production = lambda key, uuid, wait_s: copy.deepcopy(world["p"])
vpm.download_results = lambda key, p, names, folder, base: "FETCHED"

request = {"is_multitrack": True, "metadata": {"title": "Interview 2"},
           "output_files": [{"format": "tracks", "ending": "wav.zip"},
                            {"format": "stats", "ending": "json"},
                            {"format": "wav-24bit", "ending": "wav",
                             "mono_mixdown": True, "suffix": "_master"}],
           "multi_input_files": [{"type": "multitrack", "id": n,
                                  "algorithms": dict(NEW)} for n in NAMES]}

result = vpm.reuse_production(
    "secret", production(), request,
    {"preset_name": "Podcast_Multitrack"},
    [{"name": n, "axis": "/tmp/%s.wav" % n} for n in NAMES], list(NAMES),
    "/tmp", "base", 60, "rerun")

print("\n--- calls ---")
for target, body in world["calls"]:
    short = "" if body is None else json.dumps(body,
                                               ensure_ascii=False)[:70]
    print("  %-62s %s" % (target, short))
print("\nResult:", result)
print("Tracks at the end:", len(world["p"]["multi_input_files"]))
for t in world["p"]["multi_input_files"]:
    print("   %-14s denoise=%s deverbamount=%s"
          % (t["id"], t["algorithms"].get("denoise"),
             t["algorithms"].get("deverbamount")))
assert all(t["algorithms"] == NEW
           for t in world["p"]["multi_input_files"]), "not switched over!"
print("\nOK: all three tracks now carry the preset settings.")
