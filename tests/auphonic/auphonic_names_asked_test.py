# -*- coding: utf-8 -*-
"""Track names that differ at auphonic.com are adopted only when asked.

A Multitrack production of this title already exists, and its tracks
carry other names than ours. Sections: adopted, where every name moves
over by position -- the tracks, the request and the calls -- and
nothing goes up; stopped, where nothing at all is sent; uploaded anew,
where our names go up once; and a production with a different number
of tracks, which offers no adopting. auphonic.com is a stand-in that
answers from a table and notes each call; what is judged is which calls
the program makes and under which names.
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


UUID = "NamesAskedProduction01"
OURS = ["Guest", "Presenter"]
THERE = ["Track1", "Track2"]
SETTINGS = {"denoise": True, "gain": 0}


def production(names):
    """A finished Multitrack production holding *names*, every file there."""
    return {"uuid": UUID, "status": 3, "status_string": "Done",
            "is_multitrack": True,
            "output_files": [
                {"format": "tracks", "filename": "x.zip",
                 "download_url": "https://auphonic.com/dl/x.zip"},
                {"format": "wav-24bit", "filename": "x_master.wav",
                 "download_url": "https://auphonic.com/dl/x_master.wav"}],
            "multi_input_files": [
                {"id": n, "input_file": "%s.wav" % n, "type": "multitrack",
                 "algorithms": {"denoise": False, "gain": 0}}
                for n in names]}


world = {"p": None, "calls": []}


def fake_curl(key, arguments, output_binary=False, progress=False):
    """auphonic.com from a table: notes (path, body, form fields) per call."""
    arguments = [str(a) for a in arguments]
    target = [a for a in arguments if a.startswith("https://")][0]
    body = None
    if "-d" in arguments:
        with open(arguments[arguments.index("-d") + 1][1:],
                  encoding="utf-8") as f:
            body = json.load(f)
    fields = [arguments[i + 1].split("=@")[0]
              for i, a in enumerate(arguments) if a == "-F"]
    world["calls"].append((target.replace(vpm.AUPHONIC, ""), body, fields))
    if target.endswith("/upload.json"):
        return json.dumps({"status_code": 200, "data": {
            "multi_input_files": [{"id": n, "input_file": n + ".wav"}
                                  for n in fields]}})
    if "/multi_input_files/" in target or target.endswith("/start.json"):
        return json.dumps({"status_code": 200})
    if body is not None:
        return json.dumps({"status_code": 200, "data": world["p"]})
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


def reuse(there, carry_on=None, said=()):
    """One reuse against a production holding *there*.

    Returns (tracks, names, request, error) as they stand afterwards.
    """
    world["p"] = production(there)
    world["calls"] = []
    del fetched[:], offered[:], answers[:]
    answers.extend(said)
    tracks = [{"name": n, "axis": "/tmp/%s.wav" % n} for n in OURS]
    names = list(OURS)
    request = {"is_multitrack": True, "metadata": {"title": "Episode 7"},
               "output_files": [{"format": "tracks", "ending": "wav.zip"}],
               "multi_input_files": [{"type": "multitrack", "id": n,
                                      "algorithms": dict(SETTINGS)}
                                     for n in OURS]}
    try:
        with contextlib.redirect_stdout(io.StringIO()):
            vpm.reuse_production("FAKEKEY-0000", copy.deepcopy(world["p"]),
                                 request, {"preset_name": "Podcast"}, tracks,
                                 names, "/tmp", "base", 60, carry_on)
        error = ""
    except Exception as why:     # a stop is one of the judgements below
        error = "%s: %s" % (type(why).__name__, " ".join(str(why).split()))
    return tracks, names, request, error


def uploads():
    """The form fields of every upload call, one list per call."""
    return [f for t, _b, f in world["calls"] if t.endswith("/upload.json")]


def sent():
    """Every call that changes something at auphonic.com."""
    return [t for t, b, f in world["calls"] if b is not None or f
            or t.endswith("/start.json")]


# ------------------------------------------------------------ 1. Adopted
print("1. Their names adopted, by --auphonic-resume adopt")

tracks, names, request, error = reuse(THERE, carry_on="adopt")
check("adopting their names asks nothing and stops nothing",
      not offered and not error, "asked %r; %s" % (offered, error or "-"))
check("the tracks take their names by position",
      [t["name"] for t in tracks] == THERE and names == THERE,
      "tracks %r, names %r, wanted %r"
      % ([t["name"] for t in tracks], names, THERE))
check("the request to auphonic.com carries their names too",
      [e["id"] for e in request["multi_input_files"]] == THERE,
      "request ids %r, wanted %r"
      % ([e["id"] for e in request["multi_input_files"]], THERE))
addressed = [t.rsplit("/", 1)[-1].split(".")[0] for t, b, _f
             in world["calls"] if "/multi_input_files/" in t]
check("each track is set under its name there",
      sorted(addressed) == THERE,
      "addressed %r, wanted %r" % (addressed, THERE))
check("adopting uploads nothing", not uploads(),
      "%d uploads: %r" % (len(uploads()), uploads()))
check("the result is fetched under their names",
      fetched == [THERE], "fetched under %r, wanted %r" % (fetched, [THERE]))

# ------------------------------------------------------------ 2. Stopped
print("\n2. Stopped at the question about the names")

tracks, names, request, error = reuse(THERE, said=["rerun", "abort"])
check("the names question offers adopt, upload and stop",
      offered[1:] == [["adopt", "upload", "abort"]],
      "offered %r" % offered)
check("stopping there ends the run naming that nothing went up",
      error == "RuntimeError: " + " ".join(vpm.T(
          'Stopped. Nothing was uploaded and nothing computed.').split()),
      "raised %r" % (error or "nothing"))
check("and nothing at all is sent to auphonic.com", not sent(),
      "%d calls that change something: %r" % (len(sent()), sent()))
check("and our names stay ours",
      [t["name"] for t in tracks] == OURS,
      "tracks %r, wanted %r" % ([t["name"] for t in tracks], OURS))

# ------------------------------------------------------- 3. Uploaded anew
print("\n3. Our names kept, everything uploaded again")

tracks, names, request, error = reuse(THERE, said=["rerun", "upload"])
check("keeping our names uploads every track once, under our names",
      uploads() == [OURS] and not error,
      "uploads %r, wanted [%r]; %s" % (uploads(), OURS, error or "-"))
check("and the production is started once",
      [t for t in sent() if t.endswith("/start.json")]
      == ["/api/production/%s/start.json" % UUID],
      "calls that change something: %r" % sent())

# ------------------------------------------------- 4. A different count
print("\n4. Three tracks there, two here")

tracks, names, request, error = reuse(THERE + ["Track3"],
                                      said=["rerun", "abort"])
check("a different number of tracks offers no adopting",
      offered[1:] == [["upload", "abort"]], "offered %r" % offered)

print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
