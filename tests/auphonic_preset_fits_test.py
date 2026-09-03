# -*- coding: utf-8 -*-
"""Preflight for the preset: does it hold what the run needs?"""
import os
HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = os.environ.get("VPM_SCRIPT") or os.path.join(
    os.path.dirname(HERE), "videopodcast_magic.py")
import importlib.util, sys, time
began = time.time()

spec = importlib.util.spec_from_file_location(
    "vpm", SCRIPT)
vpm = importlib.util.module_from_spec(spec); sys.modules["vpm"] = vpm
spec.loader.exec_module(vpm)

CASES = {
 "fits": {"algorithms": {"loudnesstarget": -16, "leveler": True,
                         "denoise": True, "crossgate": True,
                         "filtering": "autoeq"},
          "multi_input_files": [{"id": "Speaker",
                                 "algorithms": {"denoise": True,
                                                "filtering": "autoeq"}}]},
 "other loudness": {"algorithms": {"loudnesstarget": -23, "leveler": True},
                    "multi_input_files": [{"id": "A",
                                           "algorithms": {"denoise": True}}]},
 "no track template": {"algorithms": {"loudnesstarget": -16},
                       "multi_input_files": []},
 "empty track template": {"algorithms": {"loudnesstarget": -16},
                          "multi_input_files": [{"id": "A",
                                                 "algorithms": {}}]},
}
# What each case has to lead to. The run asks for -16 LUFS and multitrack.
WANTED = {
    # Everything the run needs is in the preset: nothing to say.
    "fits": False,
    # -23 instead of -16 is the wrong loudness, and only noticed at the end.
    "other loudness": True,
    # Without a track in the preset our tracks come back unprocessed.
    "no track template": True,
    # A track that is switched off may be intended, so it is only said.
    "empty track template": False,
}

done = 0
error = []
def check(name, ok, extra=""):
    global done
    done += 1
    print("  %-52s %s %s" % (name, "ok" if ok else "FAIL", extra))
    if not ok:
        error.append(name)

verdict = {}
for name, p in CASES.items():
    vpm.read_preset = lambda key, uuid, _p=p: _p
    print("== %s" % name)
    findings = vpm.check_preset("key", "uuid", "Podcast_Multitrack",
                                -16.0, True)
    stop = vpm.report_findings(findings, "does the preset fit the run?",
                               False)
    verdict[name] = bool(stop)
    print("  -> stop: %s\n" % stop)

print("Does it stop where it has to?")
for name, wanted in WANTED.items():
    check("%-22s -> %s" % (name, "stop" if wanted else "go"),
          verdict.get(name) is wanted,
          "" if verdict.get(name) is wanted else "got %s" % verdict.get(name))
check("every case was tried", set(verdict) == set(WANTED),
      str(sorted(set(WANTED) ^ set(verdict))))

print("\n%d checks in %.2f s" % (done, time.time() - began))
if error:
    print("FAIL: " + ", ".join(error))
    sys.exit(1)
print("All good.")
