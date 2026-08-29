# -*- coding: utf-8 -*-
"""The two functions that assemble a whole production at auphonic.com.

Measured before this test was written: `run_multitrack_production` had
46 of its 47 statements untouched by the suite, `run_single_production`
73 of 74. Both spend money and both are the last step before an episode
is delivered, so a mistake in them costs a production, not a run.

auphonic.com is never spoken to. `_curl_call` is the one place where
this program reaches the network, and it is replaced here by a stand-in
that answers from a table and writes down what it was asked. That makes
three things checkable that no live run makes checkable at all: what
exactly is sent, in what order, and what is *not* sent.

Every claim has its counter-check: the same run with an input that is
deliberately wrong, which has to be noticed.
"""
import io
import json
import os
import shutil
import sys
import tempfile
import wave
import zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = os.environ.get("VPM_SCRIPT") or os.path.join(
    os.path.dirname(HERE), "videopodcast-magic.py")
import importlib.util
os.environ["VPM_NO_UPDATE_CHECK"] = "1"
os.environ["VPM_NO_SPEAKER_SPLIT"] = "1"
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
spec = importlib.util.spec_from_file_location("vpm", SCRIPT)
vpm = importlib.util.module_from_spec(spec); sys.modules["vpm"] = vpm
spec.loader.exec_module(vpm)

error = []


def check(name, ok, extra=""):
    """One line per claim; the numbers travel into the FAIL line too."""
    print("  %-56s %s %s" % (name, "ok" if ok else "FAIL", extra))
    if not ok:
        error.append(name + ((" " + str(extra)) if extra else ""))


def raises(what, hint=""):
    """Return the error message of *what*, or "" if it did not raise."""
    try:
        what()
    except Exception as e:
        said = str(e)
        return said if (not hint or hint.lower() in said.lower()) else ""
    return ""


D = tempfile.mkdtemp(prefix="wholerun_")
RATE = 48000


def wav_bytes(seconds=0.3, channels=1):
    """A real WAV in memory: ffprobe has to be able to read it."""
    buffer = io.BytesIO()
    with wave.open(buffer, "wb") as w:
        w.setnchannels(channels)
        w.setsampwidth(2)
        w.setframerate(RATE)
        n = int(seconds * RATE)
        frame = b"\x00\x10" * channels
        w.writeframes(frame * n)
    return buffer.getvalue()


def wav_file(name, channels=1, seconds=0.3):
    path = os.path.join(D, name)
    with open(path, "wb") as f:
        f.write(wav_bytes(seconds, channels))
    return path


NAMES = ["Host", "Guest", "Third"]
TRACKS = [{"name": n, "axis": wav_file(n + ".wav")} for n in NAMES]
KEY = "not-a-real-key-0123456789"
TITLE = "Episode 12: Hosts & Guests"

# What the ZIP from auphonic.com holds. The names are theirs, not ours --
# the program is told nowhere what they will be called, so it matches by
# similarity, and this is the case where that works.
GOOD_ZIP = {"Episode_12_Hosts___Guests_Host.wav": wav_bytes(),
            "Episode_12_Hosts___Guests_Guest.wav": wav_bytes(),
            "Episode_12_Hosts___Guests_Third.wav": wav_bytes()}
# And the case where it cannot work: three files whose names have nothing
# to do with the speakers.
BAD_ZIP = {"aaa.wav": wav_bytes(), "bbb.wav": wav_bytes(),
           "ccc.wav": wav_bytes()}


def zip_bytes(entries):
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w") as z:
        for name, data in entries.items():
            z.writestr(name, data)
    return buffer.getvalue()


PRESET = {
    "uuid": "PRESETUUID", "preset_name": "Podcast Multitrack",
    "is_multitrack": True, "status": 3, "status_string": "Done",
    "algorithms": {"leveler": True, "denoise": True},
    "metadata": {"title": "from the preset", "artist": "somebody"},
    "multi_input_files": [
        {"type": "multitrack", "id": "PresetTrack",
         "algorithms": {"leveler": True, "backforeground": "auto"}}],
    "output_files": [{"format": "mp3", "ending": "mp3"}],
}

FORMATS = {"data": {
    "wav-24bit": {"string": "WAV 24 bit", "ending": "wav"},
    "mp3": {"string": "MP3", "ending": "mp3"},
    "tracks": {"string": "Multitrack files as ZIP", "ending": "wav.zip"}}}


class Auphonic(object):
    """Stands in for auphonic.com: answers from a table, notes it down.

    Everything a test wants to steer sits in an attribute, so a case
    with a broken answer is the same object with one field changed.
    """

    def __init__(self):
        self.calls = []          # (method, path), in the order they came
        self.arguments = []      # every argument list, as curl would see
        self.bodies = []         # the JSON that was posted
        self.downloads = []      # every file that was fetched
        self.preset = dict(PRESET)
        self.listed = []         # what /api/productions.json answers
        self.status = 3
        self.status_string = "Done"
        self.error_message = ""
        self.track_ids = None    # None: the ones that were asked for
        self.uploaded_ok = True
        self.outputs = None      # None: the usual ZIP and mixdown
        self.zip_entries = GOOD_ZIP
        self.create_answer = None
        self.broken_urls = set()
        self.uuid = "PRODUUID"
        self.pending = 0         # how often it answers "still running"

    # -- what a production looks like from outside --------------------
    def output_files(self):
        if self.outputs is not None:
            return self.outputs
        return [{"filename": "tracks.wav.zip", "format": "tracks",
                 "download_url": "https://auphonic.com/dl/tracks.zip"},
                {"filename": "Episode_master.wav", "format": "wav-24bit",
                 "download_url": "https://auphonic.com/dl/master.wav"}]

    def production(self):
        return {"uuid": self.uuid, "status": self.status,
                "status_string": self.status_string,
                "error_message": self.error_message,
                "metadata": {"title": TITLE},
                "multi_input_files": [
                    {"id": n, "input_file": (n + ".wav")
                     if self.uploaded_ok else None} for n in NAMES],
                "output_files": self.output_files()}

    def body_of(self, arguments):
        for i, a in enumerate(arguments):
            if a == "-d" and i + 1 < len(arguments):
                with open(arguments[i + 1][1:], encoding="utf-8") as f:
                    return json.load(f)
        return None

    def data_for(self, url):
        if url.endswith(".zip"):
            return zip_bytes(self.zip_entries)
        return wav_bytes(1.0)

    def __call__(self, key, arguments, output_binary=False, progress=False):
        arguments = list(arguments)
        self.arguments.append(arguments)
        url = next((a for a in arguments
                    if str(a).startswith("https://auphonic.com")), "")
        path = url.split("auphonic.com", 1)[-1]
        method = "POST" if "-X" in arguments else "GET"
        if "-o" in arguments:
            method = "GET"
            target = arguments[arguments.index("-o") + 1]
            if url in self.broken_urls:
                raise RuntimeError("server said no")
            self.calls.append(("GET", path))
            self.downloads.append(os.path.basename(target))
            with open(target, "wb") as f:
                f.write(self.data_for(url))
            return b"" if output_binary else ""
        self.calls.append((method, path))
        body = self.body_of(arguments)
        if body is not None:
            self.bodies.append((path, body))
        return json.dumps(self.answer(method, path, body))

    def answer(self, method, path, body):
        if path.startswith("/api/preset/"):
            return {"status_code": 200, "data": self.preset}
        if path.startswith("/api/info/output_files"):
            return FORMATS
        if path.startswith("/api/productions.json?"):
            return {"status_code": 200, "data": self.listed}
        if path == "/api/productions.json" and method == "POST":
            if self.create_answer is not None:
                return self.create_answer
            ids = self.track_ids
            if ids is None:
                ids = [t.get("id") for t in
                       (body or {}).get("multi_input_files") or []]
            return {"status_code": 201,
                    "data": dict(self.production(),
                                 multi_input_files=[{"id": i} for i in ids])}
        if path.startswith("/api/simple/productions.json"):
            if self.create_answer is not None:
                return self.create_answer
            return {"status_code": 201, "data": self.production()}
        if path.endswith("/upload.json"):
            return {"status_code": 200, "data": self.production()}
        if path.endswith("/start.json"):
            return {"status_code": 200, "data": self.production()}
        if method == "GET" and self.pending:
            self.pending -= 1
            return {"status_code": 200,
                    "data": dict(self.production(), status=1,
                                 status_string="Audio Processing")}
        return {"status_code": 200, "data": self.production()}


def with_server(server, what):
    """Run *what* with the stand-in in place of the network."""
    old = vpm._curl_call
    vpm._curl_call = server
    try:
        return what()
    finally:
        vpm._curl_call = old


def without_waiting(what):
    """Run *what* with the pause between two polls taken out.

    The wait for a production is a poll loop with a second between the
    tries. A test must not spend that second, and it must not skip the
    loop either -- that is where a run sits for minutes, and a mistake
    in it means the finished episode is never fetched. So the clock is
    taken away and the condition stays.
    """
    slept = []
    old = vpm.time.sleep
    vpm.time.sleep = lambda s: slept.append(s)
    try:
        return what(), slept
    finally:
        vpm.time.sleep = old


def fresh(tag):
    """A server and an empty output folder for one case."""
    folder = os.path.join(D, tag)
    shutil.rmtree(folder, ignore_errors=True)
    os.makedirs(folder)
    return Auphonic(), folder


def multitrack(server, folder, **rest):
    return with_server(server, lambda: vpm.run_multitrack_production(
        KEY, "PRESETUUID", TITLE, TRACKS, folder,
        rest.pop("wait_s", 600), rest.pop("dry_run", False), **rest))


def single(server, folder, audio, **rest):
    return with_server(server, lambda: vpm.run_single_production(
        audio, "PRESETUUID", "Podcast", KEY, folder,
        rest.pop("wait_s", 600), rest.pop("dry_run", False), **rest))


print("1. A dry run reaches auphonic.com not at all")
server, folder = fresh("dry")
done = multitrack(server, folder, dry_run=True)
check("multitrack dry run: no call whatsoever", not server.calls,
      "%d calls: %s" % (len(server.calls), server.calls[:3]))
check("multitrack dry run: nothing came back", done == {}, repr(done))
mono = wav_file("single_mono.wav")
server, folder = fresh("drysingle")
done = single(server, folder, mono, dry_run=True)
check("single dry run: no call whatsoever", not server.calls,
      "%d calls: %s" % (len(server.calls), server.calls[:3]))
check("single dry run: nothing came back", done is None, repr(done))
# The counter-check to all four: without dry_run the very same call does
# speak, so the silence above is the switch and not a broken stand-in.
server, folder = fresh("wet")
result = multitrack(server, folder)
check("without dry run it does speak", len(server.calls) > 4,
      "%d calls" % len(server.calls))

print("\n2. What a new production is made of")
paths = [p for _m, p in server.calls]
create = next((b for p, b in server.bodies
               if p == "/api/productions.json"), {})
check("asked for as multitrack", create.get("is_multitrack") is True,
      repr(create.get("is_multitrack")))
sent_ids = [t.get("id") for t in create.get("multi_input_files") or []]
check("one track per speaker, by name", sent_ids == NAMES, repr(sent_ids))
kinds = [(f.get("format"), f.get("ending"))
         for f in create.get("output_files") or []]
check("the single tracks are asked for",
      ("tracks", "wav.zip") in kinds, repr(kinds))
check("the mixdown is asked for as the yardstick",
      any(k[0] == "wav-24bit" for k in kinds), repr(kinds))
master = next((f for f in create.get("output_files") or []
               if f.get("format") == "wav-24bit"), {})
check("mono tracks: the yardstick is folded to one channel",
      master.get("mono_mixdown") is True, repr(master))
check("the title of this episode, not the preset's",
      (create.get("metadata") or {}).get("title") == TITLE,
      repr((create.get("metadata") or {}).get("title")))
check("the file names come from the title",
      create.get("output_basename") == vpm.safe_filename(TITLE),
      repr(create.get("output_basename")))
check("the preset's own identity is not sent back",
      "uuid" not in create and "preset_name" not in create,
      repr(sorted(k for k in create if k in ("uuid", "preset_name"))))
check("the preset's track settings reached every track",
      all((t.get("algorithms") or {}).get("backforeground") == "auto"
          for t in create.get("multi_input_files") or []),
      repr(sent_ids))

print("\n3. The order of the calls, and what it costs to get it wrong")
check("the production exists before anything is uploaded",
      paths.index("/api/productions.json")
      < paths.index("/api/production/PRODUUID/upload.json"),
      str(paths))
check("nothing is started before the tracks are up",
      paths.index("/api/production/PRODUUID/upload.json")
      < paths.index("/api/production/PRODUUID/start.json"),
      str(paths))
check("the result is only fetched after the start",
      paths.index("/api/production/PRODUUID/start.json")
      < max(i for i, p in enumerate(paths) if p.startswith("/dl/")),
      str(paths))
upload = next(a for a in server.arguments
              if any("upload.json" in str(x) for x in a))
sent_files = [x.split("=@", 1) for x in upload if "=@" in str(x)]
check("one file per track went up, each the right one",
      sent_files == [[t["name"], t["axis"]] for t in TRACKS],
      repr(sent_files))

print("\n4. The key stays out of everything curl is handed")
in_argv = [a for a in server.arguments
           if any(KEY in str(x) for x in a)]
check("the key is in no argument list", not in_argv, repr(in_argv[:1]))
# The counter-check: the same search does find a key that is there, so a
# green line above is a measurement and not a search that never matches.
check("and the search would have found one",
      bool([a for a in [["-H", "bearer " + KEY]]
            if any(KEY in str(x) for x in a)]))

print("\n5. What came back is on the disc and belongs to the right voice")
check("one file per speaker", sorted(result) == sorted(NAMES),
      repr(sorted(result)))
check("every file is really there",
      all(os.path.exists(p) for p in result.values()),
      repr([p for p in result.values() if not os.path.exists(p)]))
sizes = [os.path.getsize(p) for p in result.values()]
check("and none of them is empty", all(s > 1000 for s in sizes),
      repr(sizes))
check("each speaker got the file bearing that name",
      all(name.lower() in os.path.basename(p).lower()
          for name, p in result.items()),
      repr({n: os.path.basename(p) for n, p in result.items()}))
cache = vpm.tracks_folder(folder, create=False)
check("the mixdown lies beside them as the yardstick",
      os.path.exists(os.path.join(cache, "Episode_master.wav")),
      repr(sorted(os.listdir(cache))))
check("the archive was removed once unpacked",
      not os.path.exists(os.path.join(cache, "tracks.wav.zip")),
      repr(sorted(os.listdir(cache))))

print("\n6. The counter-checks: every one of these has to be noticed")
server, folder = fresh("notmulti")
server.preset = dict(PRESET, is_multitrack=False)
said = raises(lambda: multitrack(server, folder), "not a Multitrack")
check("a preset that is not multitrack stops the run", bool(said), said[:60])
check("and nothing was uploaded for it",
      not any("upload" in p for _m, p in server.calls),
      str(server.calls))

server, folder = fresh("othertracks")
server.track_ids = ["Host", "Guest"]
said = raises(lambda: multitrack(server, folder), "different tracks")
check("tracks created other than asked for stop the run",
      bool(said), said[:60])
check("and nothing was uploaded for them",
      not any("upload" in p for _m, p in server.calls),
      str(server.calls))

server, folder = fresh("nofile")
server.uploaded_ok = False
said = raises(lambda: multitrack(server, folder), "no file")
check("a track that got no file stops the run", bool(said), said[:60])
check("and nothing was started for it",
      not any("start" in p for _m, p in server.calls),
      str(server.calls))

server, folder = fresh("rejected")
server.create_answer = {"status_code": 400,
                        "error_message": "preset does not exist"}
said = raises(lambda: multitrack(server, folder), "400")
check("a refusal from auphonic.com stops the run", bool(said), said[:60])

server, folder = fresh("nouuid")
server.create_answer = {"status_code": 201, "data": {}}
said = raises(lambda: multitrack(server, folder), "production id")
check("an answer without a production id stops the run",
      bool(said), said[:60])

server, folder = fresh("nozip")
server.outputs = [{"filename": "Episode_master.wav", "format": "wav-24bit",
                   "download_url": "https://auphonic.com/dl/master.wav"}]
said = raises(lambda: multitrack(server, folder), "no ZIP")
check("a production without the tracks stops the run", bool(said),
      said[:60])

server, folder = fresh("failed")
server.status = 2
server.error_message = "the audio was unusable"
said = raises(lambda: multitrack(server, folder), "unusable")
check("an error at auphonic.com is passed on with its reason",
      bool(said), said[:60])

server, folder = fresh("toolong")
said = raises(lambda: multitrack(server, folder, wait_s=0), "Time limit")
check("the time limit ends the wait and names the production",
      bool(said) and "PRODUUID" in said, said[:70])

server, folder = fresh("badzip")
server.zip_entries = BAD_ZIP
result = multitrack(server, folder)
check("an archive with foreign names matches nobody",
      result == {}, repr(result))

print("\n7. What is paid for is fetched, and fetched once")
server, folder = fresh("extras")
twice = {"filename": "transcript.txt", "format": "txt",
         "download_url": "https://auphonic.com/dl/transcript.txt"}
server.outputs = server.output_files() + [twice, dict(twice)]
result = multitrack(server, folder)
check("the extra output came along", "transcript.txt" in server.downloads,
      repr(server.downloads))
check("and it was fetched once, not twice",
      server.downloads.count("transcript.txt") == 1,
      "%d times" % server.downloads.count("transcript.txt"))
check("the tracks are there all the same", sorted(result) == sorted(NAMES),
      repr(sorted(result)))

server, folder = fresh("brokenextra")
server.outputs = server.output_files() + [twice]
server.broken_urls = {twice["download_url"]}
result = multitrack(server, folder)
check("an extra that will not come does not lose the tracks",
      sorted(result) == sorted(NAMES), repr(sorted(result)))

print("\n8. A stereo track keeps its two channels")
stereo_axis = wav_file("Stereo.wav", channels=2)
server, folder = fresh("stereo")
with_server(server, lambda: vpm.run_multitrack_production(
    KEY, "PRESETUUID", TITLE,
    TRACKS[:2] + [{"name": "Third", "axis": stereo_axis}], folder))
create = next(b for p, b in server.bodies if p == "/api/productions.json")
master = next((f for f in create.get("output_files") or []
               if f.get("format") == "wav-24bit"), {})
check("one stereo track: the yardstick keeps two channels",
      master.get("mono_mixdown") is False, repr(master))

print("\n9. The single file: created and started in one call")
server, folder = fresh("simple")
got = single(server, folder, mono)
create = next(a for a in server.arguments
              if any("simple/productions" in str(x) for x in a))
check("mono without transcript starts straight away",
      "action=start" in create, repr(create))
check("no second call was needed",
      len([p for _m, p in server.calls
           if p == "/api/production/PRODUUID.json" and _m == "POST"]) == 0,
      str(server.calls))
check("the file itself went up",
      "input_file=@" + mono in create, repr(create))
check("the result lies in the folder that was named",
      got and os.path.dirname(got) == folder, repr(got))
check("and it is a real file", got and os.path.getsize(got) > 1000,
      repr(got and os.path.getsize(got)))

print("\n10. Stereo and transcript need the second call")
stereo = wav_file("single_stereo.wav", channels=2)
# The preset folds its mixdown to one channel. That is the state the
# clearing has to be visible against -- an output without the key at all
# would let a program that does nothing pass.
FOLDED = [{"filename": "Episode.wav", "format": "wav",
           "mono_mixdown": True,
           "download_url": "https://auphonic.com/dl/Episode.wav"}]
server, folder = fresh("simplestereo")
server.outputs = [dict(f) for f in FOLDED]
single(server, folder, stereo)
create = next(a for a in server.arguments
              if any("simple/productions" in str(x) for x in a))
check("stereo is not started before the settings are in",
      "action=start" not in create, repr(create))
posted = [b for p, b in server.bodies
          if p == "/api/production/PRODUUID.json"]
check("the settings call starts it",
      bool(posted) and posted[-1].get("action") == "start",
      repr(posted[-1].get("action") if posted else None))
wished = (posted[-1].get("output_files") or []) if posted else []
check("the preset's own output is sent back with it",
      len(wished) == 1 and wished[0].get("format") == "wav", repr(wished))
check("and the fold to one channel is cleared",
      bool(wished) and wished[0].get("mono_mixdown") is False,
      repr(wished))

# The other direction: a mono recording with a transcript goes through
# the same call, and there the fold stays exactly as the preset set it.
server, folder = fresh("simplefold")
server.outputs = [dict(f) for f in FOLDED]
single(server, folder, mono, transcript=True)
posted = [b for p, b in server.bodies
          if p == "/api/production/PRODUUID.json"]
kept = [f for f in ((posted[-1].get("output_files") or []) if posted else [])
        if f.get("format") == "wav"]
check("mono: the fold the preset asked for is left alone",
      bool(kept) and kept[0].get("mono_mixdown") is True, repr(kept))

server, folder = fresh("simpletranscript")
server.outputs = [
    {"filename": "Episode.wav", "format": "wav",
     "download_url": "https://auphonic.com/dl/Episode.wav"},
    {"filename": "Episode.srt", "format": "srt",
     "download_url": "https://auphonic.com/dl/Episode.srt"}]
single(server, folder, mono, transcript=True, language="de")
posted = [b for p, b in server.bodies
          if p == "/api/production/PRODUUID.json"]
check("a transcript is asked for in the second call",
      bool(posted) and "speech_recognition" in posted[-1],
      repr(sorted(posted[-1]) if posted else None))
check("in the language that was chosen",
      bool(posted) and (posted[-1].get("speech_recognition")
                        or {}).get("language") == "de",
      repr(posted[-1].get("speech_recognition") if posted else None))
check("the subtitles landed beside the audio",
      os.path.exists(os.path.join(folder, "Episode.srt")),
      repr(sorted(os.listdir(folder))))

print("\n11. The counter-checks for the single file")
server, folder = fresh("simplebad")
server.create_answer = {"status_code": 402,
                        "error_message": "no credit left"}
said = raises(lambda: single(server, folder, mono), "402")
check("a refusal stops the run and says why", bool(said), said[:60])
check("and nothing was downloaded", not server.downloads,
      repr(server.downloads))

server, folder = fresh("simplenouuid")
server.create_answer = {"status_code": 201, "data": {}}
said = raises(lambda: single(server, folder, mono), "production id")
check("an answer without a production id stops the run",
      bool(said), said[:60])

server, folder = fresh("simpleempty")
server.data_for = lambda url: b"RIFF short"
said = raises(lambda: single(server, folder, mono), "bytes")
check("a download that is too small stops the run", bool(said), said[:60])

server, folder = fresh("simplenone")
server.outputs = []
said = raises(lambda: single(server, folder, mono), "no output file")
check("a production without a result stops the run", bool(said), said[:60])

server, folder = fresh("simplenourl")
server.outputs = [{"filename": "Episode.wav", "format": "wav"}]
said = raises(lambda: single(server, folder, mono), "no download address")
check("a result without an address stops the run", bool(said), said[:60])

server, folder = fresh("simplefailed")
server.status = 2
server.error_message = "input file broken"
said = raises(lambda: single(server, folder, mono), "broken")
check("an error at auphonic.com is passed on with its reason",
      bool(said), said[:60])

server, folder = fresh("simpletime")
said = raises(lambda: single(server, folder, mono, wait_s=0), "Time limit")
check("the time limit ends the wait and says where to look",
      bool(said) and "PRODUUID" in said, said[:70])

print("\n12. A production that is not finished yet is waited for")
server, folder = fresh("waiting")
server.pending = 2
(result, slept) = without_waiting(lambda: multitrack(server, folder))
asked = [p for m, p in server.calls
         if m == "GET" and p == "/api/production/PRODUUID.json"]
check("it asked again instead of giving up", len(asked) == 3,
      "%d times" % len(asked))
check("it paused between the tries", len(slept) >= 5,
      "%d pauses of %s" % (len(slept), sorted(set(slept))))
check("and the tracks came back all the same",
      sorted(result) == sorted(NAMES), repr(sorted(result)))

server, folder = fresh("waitingsingle")
server.pending = 1
(got, slept) = without_waiting(lambda: single(server, folder, mono))
asked = [p for m, p in server.calls
         if m == "GET" and p == "/api/production/PRODUUID.json"]
check("the single file is waited for too", len(asked) == 2,
      "%d times" % len(asked))
check("and its result came back", bool(got) and os.path.exists(got),
      repr(got))

# The counter-check: one that never finishes must not be waited for for
# ever. Without the pause the loop is bounded by the time limit alone,
# so the limit is what has to end it.
server, folder = fresh("never")
server.pending = 10 ** 6
said = raises(lambda: without_waiting(
    lambda: multitrack(server, folder, wait_s=0)), "Time limit")
check("one that never finishes ends at the time limit", bool(said),
      said[:60])

print("\n13. Lossless before lossy, whatever order they arrive in")
server, folder = fresh("pick")
server.outputs = [
    {"filename": "Episode.mp3", "format": "mp3",
     "download_url": "https://auphonic.com/dl/Episode.mp3"},
    {"filename": "Episode.wav", "format": "wav",
     "download_url": "https://auphonic.com/dl/Episode.wav"}]
got = single(server, folder, mono)
check("the WAV is taken, not the MP3",
      got and got.endswith("Episode.wav"), repr(got))
server, folder = fresh("pickonly")
server.outputs = [
    {"filename": "Episode.mp3", "format": "mp3",
     "download_url": "https://auphonic.com/dl/Episode.mp3"}]
got = single(server, folder, mono)
check("with only an MP3 that one is taken",
      got and got.endswith("Episode.mp3"), repr(got))

shutil.rmtree(D, ignore_errors=True)
print()
if error:
    print("FAIL: " + ", ".join(error))
    sys.exit(1)
print("All good.")
