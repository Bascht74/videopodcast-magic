# -*- coding: utf-8 -*-
"""A stand-in for curl that answers the way auphonic.com does, and no more.

Put first on PATH under the name curl by source_live_asks_first, so the
live tests can be run without a network: to prove the starter's gate,
and to see each live check fall against a broken copy of the program.
Every call is written to VPM_STANDIN_LOG as its arguments and whether
the key named in VPM_STANDIN_WATCH came in its configuration; the key
itself is never written. A key containing VPM_STANDIN_REFUSED is turned
away with a 401, the way auphonic.com turns away one it does not know.

What it knows is the few calls the live tests make: the presets, one
preset by its uuid, a simple production with its settings changed and
started, its state, one download, the list of productions and a delete.
A production is finished the first time it is asked after, and the file
it hands back is twenty seconds long, with two channels only where the
mono fold was switched off. Anything else is a 404.
"""
import json
import os
import struct
import sys
import wave

args = sys.argv[1:]
conf = args[args.index("--config") + 1] if "--config" in args else ""
# "--config -" is the program's way since b28: the key comes on the
# input, and no file holds it.
said = (sys.stdin.read() if conf == "-" else
        open(conf, encoding="utf-8").read() if conf else "")
LOG = os.environ["VPM_STANDIN_LOG"]
with open(LOG, "a", encoding="utf-8") as log:
    log.write(json.dumps({"args": args, "key_in_config":
                          os.environ.get("VPM_STANDIN_WATCH", "\0") in said})
              + "\n")
STATE = LOG + ".state"
state = {"made": {}, "two": []}
if os.path.isfile(STATE):
    state = json.load(open(STATE, encoding="utf-8"))
url = ([a for a in args if a.startswith("http")] or [""])[-1]
method = args[args.index("-X") + 1] if "-X" in args else "GET"
forms = [args[i + 1] for i, a in enumerate(args) if a == "-F"]


def tone(path, channels):
    """Twenty seconds of silence-free sound, as a WAV."""
    with wave.open(path, "wb") as w:
        w.setnchannels(channels)
        w.setsampwidth(2)
        w.setframerate(8000)
        w.writeframes(struct.pack("<h", 3000) * channels * 8000 * 20)


def between(text, before, after):
    """The piece of text between two marks, or ""."""
    return text.split(before, 1)[1].split(after, 1)[0] if before in text \
        else ""


answer = {"status_code": 404, "error_message": "stand-in: not here"}
if os.environ.get("VPM_STANDIN_REFUSED", "\0") in said:
    answer = {"status_code": 401, "error_message": "stand-in: no such key"}
elif "-o" in args:
    uuid = between(url, "/download/", "/")
    tone(args[args.index("-o") + 1], 2 if uuid in state["two"] else 1)
    answer = None
elif url.endswith("/api/presets.json?minimal_data=1&limit=100"):
    answer = {"status_code": 200, "data": [
        {"preset_name": "Stand-in", "uuid": "standin0001",
         "is_multitrack": False}]}
elif "/api/preset/" in url:
    answer = {"status_code": 200,
              "data": {"uuid": between(url, "/api/preset/", ".json")}}
elif url.endswith("/api/simple/productions.json") and method == "POST":
    uuid = "standinprod%d" % len(state["made"])
    title = [f[6:] for f in forms if f.startswith("title=")]
    state["made"][uuid] = title[0] if title else ""
    answer = {"status_code": 200, "data": {"uuid": uuid}}
elif "/api/productions.json" in url:
    answer = {"status_code": 200, "data": [
        {"uuid": u, "metadata": {"title": t}}
        for u, t in state["made"].items()]}
elif "/api/production/" in url:
    uuid = between(url, "/api/production/", ".json")
    if uuid not in state["made"]:
        pass
    elif method == "DELETE":
        del state["made"][uuid]
        answer = None
    elif method == "POST":
        body = json.load(open(args[args.index("-d") + 1][1:],
                              encoding="utf-8"))
        if any(f.get("mono_mixdown") is False
               for f in body.get("output_files") or []):
            state["two"].append(uuid)
        answer = {"status_code": 200, "data": {"uuid": uuid}}
    elif method == "GET":
        answer = {"status_code": 200, "data": {
            "uuid": uuid, "status": 3, "status_string": "Done",
            "output_files": [{
                "format": "wav", "filename": "back.wav", "mono_mixdown":
                uuid not in state["two"],
                "download_url": "https://auphonic.com/download/%s/back.wav"
                                % uuid}]}}
json.dump(state, open(STATE, "w", encoding="utf-8"))
if answer is not None:
    sys.stdout.write(json.dumps(answer))
