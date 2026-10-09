# -*- coding: utf-8 -*-
"""A production found again is sent nothing that auphonic.com holds.

A Multitrack production of this title already exists under our track
names. Sections: its finished result is taken, and nothing is uploaded,
changed or started; a rerun where the mixdown is missing asks for that
output file alone, and a track whose settings are already right is not
sent again; and stopping at the first question sends nothing at all.
auphonic.com is a stand-in that answers from a table and notes each
call; what is judged is which calls the program makes and what goes
into them.
"""
PLATFORM_BOUND = False
import os
import sys
# tests/, where the helpers and state/ lie; this file may stand in a
# folder under it, or in one under that.
HERE = os.path.dirname(os.path.abspath(__file__))
while not os.path.isfile(os.path.join(HERE, "the_program.py")) \
        and os.path.dirname(HERE) != HERE:
    HERE = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import contextlib
import copy
import io
import json
import time
import the_program

began = time.time()
vpm = the_program.load()
vpm.set_language("en")

done = 0
bad = []


def check(name, ok, extra=""):
    global done
    done += 1
    print("  %-62s %s %s" % (name, "ok" if ok else "FAIL", extra))
    if not ok:
        bad.append("%s [%s]" % (name, extra or "no numbers"))


UUID = "NoResendProduction01"
OURS = ["Guest", "Presenter"]
OLD = {"denoise": False, "gain": 0}
NEW = {"denoise": True, "gain": 0}
TRACKS_OUT = {"format": "tracks", "ending": "wav.zip"}
MASTER_OUT = {"format": "wav-24bit", "ending": "wav", "mono_mixdown": True,
              "suffix": "_master"}


def production(with_master=True, settings=None):
    """A finished Multitrack production of our tracks, every file there.

    *settings* gives a track's settings by name; the rest carry OLD.
    """
    outputs = [{"format": "tracks", "filename": "x.zip",
                "download_url": "https://auphonic.com/dl/x.zip"}]
    if with_master:
        outputs.append({"format": "wav-24bit", "filename": "x_master.wav",
                        "download_url": "https://auphonic.com/dl/x_master.wav"})
    return {"uuid": UUID, "status": 3, "status_string": "Done",
            "is_multitrack": True, "output_files": outputs,
            "multi_input_files": [
                {"id": n, "input_file": "%s.wav" % n, "type": "multitrack",
                 "algorithms": dict((settings or {}).get(n, OLD))}
                for n in OURS]}


world = {"p": None, "calls": []}


def fake_curl(key, arguments, output_binary=False, progress=False):
    """auphonic.com from a table: notes (path, body, uploaded) per call."""
    arguments = [str(a) for a in arguments]
    target = [a for a in arguments if a.startswith("https://")][0]
    body = None
    if "-d" in arguments:
        with open(arguments[arguments.index("-d") + 1][1:],
                  encoding="utf-8") as f:
            body = json.load(f)
    world["calls"].append((target.replace(vpm.AUPHONIC, ""), body,
                           "-F" in arguments))
    if "/multi_input_files/" in target or target.endswith("/start.json"):
        return json.dumps({"status_code": 200})
    return json.dumps({"status_code": 200,
                       "data": copy.deepcopy(world["p"])})


fetched = []
vpm._curl_call = fake_curl
vpm.wait_for_production = lambda key, uuid, wait_s: copy.deepcopy(world["p"])
vpm.download_results = (lambda key, p, names, folder, base:
                        fetched.append(list(names)) or {})

offered = []
answers = []


def sink(possible, title):
    """Whoever sits at the window: notes what is offered, says the next."""
    offered.append([k for k, _t in possible])
    return answers.pop(0)


vpm.ASK_SINK = sink


def reuse(existing, said):
    """One reuse of *existing*, answering *said*: the error, or ""."""
    world["p"] = existing
    world["calls"] = []
    del fetched[:], offered[:], answers[:]
    answers.extend(said)
    request = {"is_multitrack": True, "metadata": {"title": "Episode 7"},
               "output_files": [dict(TRACKS_OUT), dict(MASTER_OUT)],
               "multi_input_files": [{"type": "multitrack", "id": n,
                                      "algorithms": dict(NEW)}
                                     for n in OURS]}
    try:
        with contextlib.redirect_stdout(io.StringIO()):
            vpm.reuse_production("FAKEKEY-0000", copy.deepcopy(existing),
                                 request, {"preset_name": "Podcast"},
                                 [{"name": n, "axis": "/tmp/%s.wav" % n}
                                  for n in OURS], list(OURS), "/tmp",
                                 "base", 60, None)
        return ""
    except Exception as why:     # a stop is one of the judgements below
        return "%s: %s" % (type(why).__name__, " ".join(str(why).split()))


def sent():
    """Every call that changes something at auphonic.com, by its path."""
    return [t for t, b, up in world["calls"] if b is not None or up
            or t.endswith("/start.json")]


# ------------------------------------------------------ 1. Result taken
print("1. The finished result is taken")

error = reuse(production(), ["result"])
check("taking the result sends nothing to auphonic.com",
      not sent() and not error,
      "%d calls that change something: %r; %s"
      % (len(sent()), sent(), error or "-"))
check("and fetches that production's result",
      fetched == [OURS], "fetched under %r, wanted [%r]" % (fetched, OURS))

# ------------------------------------------------------------- 2. Rerun
print("\n2. A rerun with the mixdown missing there")

error = reuse(production(with_master=False, settings={"Guest": NEW}),
              ["rerun"])
check("a result without the mixdown is not offered to be taken",
      offered[:1] == [["rerun", "upload", "abort"]],
      "offered %r" % offered)
changes = [b for t, b, _u in world["calls"]
           if t == "/api/production/%s.json" % UUID and b is not None]
asked_for = [c.get("output_files") for c in changes]
check("a rerun asks for the missing output file alone",
      asked_for == [[MASTER_OUT]] and not error,
      "output files sent %r, wanted [[%r]]; %s"
      % (asked_for, MASTER_OUT, error or "-"))
addressed = [t.rsplit("/", 1)[-1].split(".")[0] for t, b, _u
             in world["calls"] if "/multi_input_files/" in t]
check("a track whose settings are already right is not sent again",
      addressed == ["Presenter"],
      "tracks sent %r, wanted ['Presenter']" % addressed)

# ------------------------------------------------------------ 3. Stopped
print("\n3. Stopped at the first question")

error = reuse(production(), ["abort"])
check("stopping at the first question ends the run",
      error.startswith("RuntimeError: " + " ".join(vpm.T(
          'Stopped. Choose another production name -- then a new '
          'production\n  is created -- or pick one of the other '
          'options.').split())),
      "raised %r" % (error or "nothing"))
check("and nothing is sent to auphonic.com", not sent(),
      "%d calls that change something: %r" % (len(sent()), sent()))

print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
