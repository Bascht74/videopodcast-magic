# -*- coding: utf-8 -*-
"""Checks: on reuse the tracks are switched over one at a time.

A production that already exists is recomputed: the uploaded files stay
where they are, and every track is brought to the preset through its
own URL -- the whole list sent to the production appends instead of
matching, and three tracks became six that way. In order: the reuse
comes through without an error, nothing is uploaded a second time, the
track list stays out of the production, each track is addressed once,
and the settings have arrived on all of them at the end. Auphonic is a
stand-in here; what is measured is which calls the program makes and
what it puts into them.
"""
import os
HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = os.environ.get("VPM_SCRIPT") or os.path.join(
    os.path.dirname(HERE), "videopodcast_magic.py")
import importlib.util, json, sys, copy, time

began = time.time()
done = 0
bad = []


def check(name, ok, extra=""):
    global done
    done += 1
    print("  %-58s %s %s" % (name, "ok" if ok else "FAIL", extra))
    if not ok:
        bad.append("%s [%s]" % (name, extra or "no numbers"))


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

# Caught rather than let through: a reuse that stops halfway is one of
# the judgements below, and every path has to reach the closing lines.
try:
    result = vpm.reuse_production(
        "secret", production(), request,
        {"preset_name": "Podcast_Multitrack"},
        [{"name": n, "axis": "/tmp/%s.wav" % n} for n in NAMES], list(NAMES),
        "/tmp", "base", 60, "rerun")
    stopped = ""
except Exception as why:
    result = None
    stopped = ("%s %s" % (type(why).__name__, " ".join(str(why).split())))[:110]

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

# What was called, read off the log of calls: the second upload, the
# bodies that went to the production itself, and the tracks that were
# addressed each on their own.
uploaded = [t for t, _b in world["calls"] if t.endswith("/upload.json")]
addressed = [t.rsplit("/", 1)[-1].split(".")[0] for t, b in world["calls"]
             if "/multi_input_files/" in t and b is not None]
to_production = [b for t, b in world["calls"]
                 if b is not None and "/multi_input_files/" not in t
                 and not t.endswith("/start.json")]
carry_list = [b for b in to_production if "multi_input_files" in b]
now = world["p"]["multi_input_files"]
right = [t["id"] for t in now if t.get("algorithms") == NEW]
off = [str(t["id"]) for t in now if t.get("algorithms") != NEW]

print("\n--- what it did ---")
check("the reuse comes through without an error",
      not stopped, "0 wanted, %d: %s" % (1 if stopped else 0,
                                         stopped or "none"))
check("nothing is uploaded a second time", not uploaded,
      "0 wanted, %d uploads out of %d calls" % (len(uploaded),
                                                len(world["calls"])))
check("the track list does not go to the production as a whole",
      not carry_list,
      "0 wanted, %d of %d bodies to the production carry it"
      % (len(carry_list), len(to_production)))
check("each track is addressed once through its own URL",
      sorted(addressed) == sorted(NAMES),
      "%d wanted (%s), %d addressed (%s)"
      % (len(NAMES), ", ".join(NAMES), len(addressed),
         ", ".join(addressed) or "none"))
check("every track carries the preset settings afterwards",
      len(right) == len(NAMES) and not off,
      "%d wanted, %d of %d carry them, off: %s"
      % (len(NAMES), len(right), len(now), ", ".join(off) or "none"))

print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
