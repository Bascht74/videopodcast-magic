# -*- coding: utf-8 -*-
"""A second Singletrack run finds its production by title, not paying again.

auphonic.com is never spoken to: `_curl_call` is replaced by a stand-in
that answers from a table and notes every call, an upload being any
call that sends a file. Sections: a finished production of the same
title is asked about, and taking its result uploads nothing and fetches
it; the answers offered are the result, a new upload and stop, and an
unfinished one offers no result; a new upload goes up, stop ends the
run before anything does; a production that is no match -- a Multitrack
one of that title, or another title -- is passed over unasked, while a
Singletrack one with an intro in its list is asked about; and the
run hands the --auphonic-resume answer on to a Singletrack run. The
limit: auphonic.com's list is stood in for as a list of the fields the
program reads, never measured against the real one here.
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
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
vpm = the_program.load()
vpm.set_language("en")
vpm.load_api_key = lambda: ""
vpm.show_progress = lambda text, share=None: None

done = 0
bad = []


def check(name, ok, extra=""):
    global done
    done += 1
    print("  %-62s %s %s" % (name, "ok" if ok else "FAIL", extra))
    if not ok:
        bad.append("%s [%s]" % (name, extra or "no numbers"))


KEY = "FAKEKEY-0000"
TITLE = "Episode 7"
ROOM = tempfile.mkdtemp(prefix="vpm_single_reused_")


def wav_bytes(seconds):
    """A real WAV in memory, mono, 48 kHz."""
    buffer = io.BytesIO()
    with wave.open(buffer, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(48000)
        w.writeframes(b"\x00\x10" * int(48000 * seconds))
    return buffer.getvalue()


AUDIO = os.path.join(ROOM, "Presenter.wav")
with open(AUDIO, "wb") as f:
    f.write(wav_bytes(1.0))


def production(title=TITLE, status=3, multitrack=False, uuid="OLDUUID",
               intro=False):
    """A production as auphonic.com lists it, in the fields read here.

    One being computed again still lists the files of its last result,
    so an unfinished one carries them too: only its status says it is
    not done.
    """
    p = {"uuid": uuid, "status": status,
         "status_string": "Done" if status == 3 else "Audio Processing",
         "creation_time": "2026-01-02T03:04:05",
         "metadata": {"title": title},
         "output_files": [{"filename": "Episode_7.wav", "format": "wav",
                           "download_url": "https://auphonic.com/dl/%s.wav"
                           % uuid}]}
    if multitrack:
        p["is_multitrack"] = True
        p["multi_input_files"] = [{"id": "Guest"}, {"id": "Presenter"}]
    if intro:
        # A Singletrack production with an intro lists it too, by type.
        p["is_multitrack"] = False
        p["multi_input_files"] = [{"type": "intro", "id": "Jingle"}]
    return p


class Auphonic(object):
    """Stands in for auphonic.com: answers from a table, notes each call."""

    def __init__(self, listed):
        self.listed = listed
        self.calls = []
        self.downloads = []

    def uploads(self):
        """The calls that sent a file: those that cost credit."""
        return [c for c in self.calls if any("=@" in a for a in c)]

    def __call__(self, key, arguments, output_binary=False, progress=False):
        arguments = [str(a) for a in arguments]
        self.calls.append(arguments)
        url = next((a for a in arguments
                    if a.startswith("https://auphonic.com")), "")
        path = url.split("auphonic.com", 1)[-1]
        if "-o" in arguments:
            target = arguments[arguments.index("-o") + 1]
            self.downloads.append(path)
            with open(target, "wb") as f:
                f.write(wav_bytes(1.0))
            return b"" if output_binary else ""
        if path == "/api/user.json":
            answer = {"credits": 10.0, "is_paying_user": True}
        elif path.startswith("/api/productions.json?"):
            answer = self.listed
        elif path.startswith("/api/simple/productions.json"):
            answer = production(uuid="NEWUUID")
        elif path.startswith("/api/production/"):
            uuid = path.split("/")[3].split(".")[0]
            answer = production(uuid=uuid)
        else:
            answer = {}
        return json.dumps({"status_code": 200, "data": answer})


asked = []


def sink(possible, title):
    """Whoever sits at the window: notes the answers offered, says one."""
    asked.append([k for k, _t in possible])
    return sink.answer


sink.answer = "result"
vpm.ASK_SINK = sink


def run(listed, carry_on=None, answer="result"):
    """One Singletrack run against *listed*: (result, stand-in, error)."""
    del asked[:]
    sink.answer = answer
    server = Auphonic(listed)
    vpm._curl_call = server
    out = tempfile.mkdtemp(dir=ROOM)
    said = io.StringIO()
    old, sys.stdout = sys.stdout, said
    try:
        got, error = vpm.run_single_production(
            AUDIO, "PRESETUUID", "Podcast", KEY, out, 600, False, TITLE,
            carry_on), ""
    except Exception as why:     # a fault is a finding here, not a crash
        got, error = None, "%s: %s" % (type(why).__name__, why)
    finally:
        sys.stdout = old
    return got, server, error


def where(server):
    """The calls in order, an upload named as one, for a FAIL line."""
    return ["upload" if any("=@" in a for a in c) else c[-1]
            for c in server.calls]


# ------------------------------------------------- 1. Found and taken
print("1. A finished production of the same title is taken")

got, server, error = run([production()])
check("a finished production of the same title is asked about once",
      asked == [["result", "upload", "abort"]],
      "asked %r; %s" % (asked, error))
check("taking its result uploads nothing",
      not server.uploads() and not error,
      "%d uploads; calls %r; %s" % (len(server.uploads()), where(server),
                                    error))
check("taking its result fetches the production's own audio",
      server.downloads == ["/dl/OLDUUID.wav"] and bool(got)
      and os.path.isfile(got),
      "fetched %r, handed back %r; %s"
      % (server.downloads, got and os.path.basename(got), error))

got, server, error = run([production()], carry_on="result", answer="abort")
check("--auphonic-resume result takes it without asking",
      not asked and not server.uploads() and bool(got),
      "asked %r, %d uploads, handed back %r; %s"
      % (asked, len(server.uploads()), got and os.path.basename(got), error))

# ------------------------------------------- 2. What is offered, what not
print("\n2. What is offered, and what each answer does")

got, server, error = run([production(status=4)], answer="upload")
check("an unfinished production offers no result, only upload or stop",
      asked == [["upload", "abort"]], "asked %r; %s" % (asked, error))

got, server, error = run([production()], answer="upload")
check("a new upload goes up, once",
      len(server.uploads()) == 1 and not error,
      "%d uploads; calls %r; %s" % (len(server.uploads()), where(server),
                                    error))
check("and its own production is fetched, not the old one",
      server.downloads == ["/dl/NEWUUID.wav"],
      "fetched %r; %s" % (server.downloads, error))

got, server, error = run([production()], answer="abort")
check("stop ends the run before anything goes up",
      not server.uploads() and not server.downloads and "Stopped" in error,
      "%d uploads, fetched %r, raised %r"
      % (len(server.uploads()), server.downloads, error))

# ------------------------------------------------ 3. Not a match
print("\n3. A production that is no match is passed over")

got, server, error = run([production(multitrack=True)])
check("a Multitrack production of the same title is passed over unasked",
      not asked and len(server.uploads()) == 1,
      "asked %r, %d uploads; %s" % (asked, len(server.uploads()), error))
got, server, error = run([production(intro=True)])
check("a Singletrack production with an intro is asked about",
      asked == [["result", "upload", "abort"]] and not server.uploads(),
      "asked %r, %d uploads; %s" % (asked, len(server.uploads()), error))
got, server, error = run([production(title="Episode 8")])
check("a production of another title is passed over unasked",
      not asked and len(server.uploads()) == 1,
      "asked %r, %d uploads; %s" % (asked, len(server.uploads()), error))

# ------------------------------------------------ 4. From the run
print("\n4. The run hands the answer on")

handed = []
vpm.run_single_production = (
    lambda audio, preset, name, key, folder, wait, dry, title, carry_on=None:
    handed.append(carry_on) or audio)
vpm.preset_for_run = lambda args, key, multitrack: ("PRESETUUID", "Podcast")
vpm.api_key_from_anywhere = lambda args: KEY
vpm.verify_returned_tracks = lambda *a, **k: True
args = types.SimpleNamespace(auphonic_resume="result", auphonic_wait=600,
                             dry_run=False)
try:
    stop = vpm.send_to_auphonic(args, [{"name": "Presenter", "axis": AUDIO}],
                                ROOM, ROOM, 1.0, TITLE, together=False)
except Exception as why:         # a fault is a finding here, not a crash
    stop = "%s: %s" % (type(why).__name__, why)
check("--auphonic-resume reaches a Singletrack run",
      handed == ["result"], "handed %r, the run returned %r"
      % (handed, stop))

shutil.rmtree(ROOM, ignore_errors=True)
print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
