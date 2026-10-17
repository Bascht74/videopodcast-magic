# -*- coding: utf-8 -*-
"""Each Singletrack production of a run goes up under a title of its own.

A second run finds a Singletrack production by its title alone, so two
tracks sharing one would take each other's result. send_to_auphonic in
this process against a stand-in for auphonic.com that keeps what it
was sent, as the real one keeps its productions. Sections: two tracks
of one run with one title -- two titles, no question on the first run,
and on a second with --auphonic-resume result each its own result;
then a lone track, with a title and without, which keeps the title it
always went up under, so a production sent before is still found.
"""
PLATFORM_BOUND = True
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
import io
import json
import shutil
import tempfile
import time
import types
import wave
import the_program

began = time.time()

os.environ["VPM_NO_UPDATE_CHECK"] = "1"
vpm = the_program.load()
vpm.set_language("en")
vpm.load_api_key = lambda: ""
vpm.show_progress = lambda text, share=None: None

done = 0
bad = []


def check(name, ok, extra=""):
    global done
    done += 1
    print("  %-58s %s %s" % (name, "ok" if ok else "FAIL", extra))
    if not ok:
        bad.append("%s [%s]" % (name, extra or "no numbers"))


KEY = "FAKEKEY-0000"
TITLE = "Episode 7"
ROOM = tempfile.mkdtemp(prefix="vpm_titles_apart_")


def wav_bytes(seconds):
    """A real WAV in memory, mono, 48 kHz."""
    buffer = io.BytesIO()
    with wave.open(buffer, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(48000)
        w.writeframes(b"\x00\x10" * int(48000 * seconds))
    return buffer.getvalue()


class Auphonic(object):
    """Stands in for auphonic.com: keeps each production it was sent.

    A production is made from the request a run sends, under the title
    in it. Listed newest first and ten a time from the offset asked
    for, as auphonic.com lists them, each finished at once, its result
    a file named after its uuid -- so the file a track hands back says
    which production it came from.
    """

    def __init__(self):
        self.made = []

    def titles(self):
        """The titles sent, oldest first."""
        return [p["metadata"]["title"] for p in reversed(self.made)]

    def __call__(self, key, arguments, output_binary=False, progress=False):
        arguments = [str(a) for a in arguments]
        url = next((a for a in arguments
                    if a.startswith("https://auphonic.com")), "")
        path = url.split("auphonic.com", 1)[-1]
        if "-o" in arguments:
            with open(arguments[arguments.index("-o") + 1], "wb") as f:
                f.write(wav_bytes(1.0))
            return b"" if output_binary else ""
        if path == "/api/user.json":
            answer = {"credits": 10.0, "is_paying_user": True}
        elif path.startswith("/api/productions.json?"):
            query = dict(part.split("=", 1) for part in
                         path.split("?", 1)[1].split("&") if "=" in part)
            start = int(query.get("offset") or 0)
            answer = self.made[start:start + 10]
        elif path == "/api/productions.json":
            # The request is read while the call is made: the program
            # deletes the file behind -d @ as soon as curl has returned.
            with open(arguments[arguments.index("-d") + 1][1:],
                      encoding="utf-8") as f:
                request = json.load(f)
            uuid = "U%d" % (len(self.made) + 1)
            answer = {"uuid": uuid, "status": 3, "status_string": "Done",
                      "creation_time": "2026-01-02T03:04:05",
                      "is_multitrack": False,
                      "metadata": {"title": (request.get("metadata")
                                             or {}).get("title")},
                      "output_files": [{
                          "filename": uuid + ".wav", "format": "wav",
                          "download_url": "https://auphonic.com/dl/%s.wav"
                          % uuid}]}
            self.made.insert(0, answer)
        elif path.startswith("/api/preset/"):
            # A preset read is answered with one: the run makes its
            # production from it.
            answer = {"uuid": "PRESETUUID", "preset_name": "Podcast",
                      "is_multitrack": False,
                      "output_files": [{"format": "wav", "ending": "wav"}]}
        elif path.startswith("/api/production/"):
            uuid = path.split("/")[3].split(".")[0]
            answer = next((p for p in self.made if p["uuid"] == uuid), {})
        else:
            answer = {}
        return json.dumps({"status_code": 200, "data": answer})


asked = []


def sink(possible, title):
    """Whoever sits at the window: notes the question, sends anew."""
    asked.append([k for k, _t in possible])
    return "upload"


vpm.ASK_SINK = sink
vpm.preset_for_run = lambda args, key, multitrack: ("PRESETUUID", "Podcast")
vpm.api_key_from_anywhere = lambda args: KEY
vpm.verify_returned_tracks = lambda *a, **k: True


def send(server, names, title, resume=None):
    """One run's tracks to the stand-in: {track: the file it got back}."""
    del asked[:]
    vpm._curl_call = server
    tracks = []
    for name in names:
        path = os.path.join(ROOM, "%s.wav" % name)
        with open(path, "wb") as f:
            f.write(wav_bytes(1.0))
        tracks.append({"name": name, "axis": path})
    args = types.SimpleNamespace(auphonic_resume=resume, auphonic_wait=60,
                                 dry_run=False)
    try:
        with contextlib.redirect_stdout(io.StringIO()):
            vpm.send_to_auphonic(args, tracks, tempfile.mkdtemp(dir=ROOM),
                                 ROOM, 1.0, title, together=False)
    except Exception as why:     # a fault is a finding here, not a crash
        bad.append("the run ran into %s: %s" % (type(why).__name__, why))
    return dict((t["name"], t.get("done") and os.path.basename(t["done"]))
                for t in tracks)


try:
    print("1. Two tracks of one run, one title")
    server = Auphonic()
    send(server, ["Guest", "Presenter"], TITLE)
    check("two tracks of one run go up under two titles",
          server.titles() == ["Episode 7 - Guest", "Episode 7 - Presenter"],
          "titles sent %r" % server.titles())
    check("the first run asks about no production of its own",
          asked == [], "asked %r" % asked)
    got = send(server, ["Guest", "Presenter"], TITLE, resume="result")
    check("a second run hands each track its own production's result",
          got == {"Guest": "U1.wav", "Presenter": "U2.wav"},
          "got back %r, wanted Guest U1.wav and Presenter U2.wav; %d "
          "productions" % (got, len(server.made)))

    print("\n2. A lone track keeps its title")
    server = Auphonic()
    send(server, ["Guest"], TITLE)
    check("a lone track with a title goes up under that title",
          server.titles() == ["Episode 7"],
          "titles sent %r" % server.titles())
    server = Auphonic()
    send(server, ["Guest"], "")
    check("a lone track without a title goes up under its name",
          server.titles() == ["Guest"], "titles sent %r" % server.titles())
except Exception as e:
    bad.append("the test ran into %s: %s" % (type(e).__name__, e))
finally:
    shutil.rmtree(ROOM, True)

print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
