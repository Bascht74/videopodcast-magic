# -*- coding: utf-8 -*-
"""A file auphonic.com names is written inside the folder it is fetched to.

The name a finished production gives each output is the server's word,
and it is joined to a folder on this machine. auphonic.com is never
spoken to: `_curl_call` is replaced by a stand-in that writes what the
program asks for where it asks, so what is judged is the path. The
sections: the transcripts beside the result, the single result, and
the multitrack archive with what came beside it and the tracks in it.
A name is refused when no plain file name is left of it, and the run
says so.
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
import zipfile
import the_program

began = time.time()

os.environ["VPM_NO_UPDATE_CHECK"] = "1"
os.environ["VPM_NO_SPEAKER_SPLIT"] = "1"
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
vpm = the_program.load()
vpm.set_language("en")
# Nothing here needs a key from anywhere, and nothing may reach the
# store for one: all three names of it go somewhere throwaway.
import key_store_apart
key_store_apart.apart(vpm)
vpm.show_progress = lambda text, share=None: None

KEY = "FAKEKEY-0000"
done = 0
bad = []


def check(name, ok, extra=""):
    global done
    done += 1
    print("  %-64s %s %s" % (name, "ok" if ok else "FAIL", extra))
    if not ok:
        bad.append("%s [%s]" % (name, extra or "no numbers"))


def archive(entries):
    """A ZIP holding each entry name with a little sound-sized content."""
    held = io.BytesIO()
    with zipfile.ZipFile(held, "w") as zf:
        for entry in entries:
            zf.writestr(entry, b"\0" * 2000)
    return held.getvalue()


class Server(object):
    """Stands in for curl: writes each download where it is told to."""

    def __init__(self, zip_entries=()):
        self.fetched = []        # where each download was written
        self.zip_entries = list(zip_entries)

    def __call__(self, key, arguments, output_binary=False, progress=False):
        arguments = list(arguments)
        if "-o" not in arguments:
            # Only the single production creates something, and it is
            # asked for the id alone.
            return json.dumps({"status_code": 201, "data": {"uuid": "U"}})
        target = arguments[arguments.index("-o") + 1]
        url = arguments[-1]
        self.fetched.append(os.path.abspath(target))
        with open(target, "wb") as f:
            f.write(archive(self.zip_entries) if url.endswith(".zip")
                    else b"\0" * 2000)
        return b"" if output_binary else ""


def ground(tag):
    """A throwaway root with the folder the files are fetched to deep in it.

    Two levels between them, so a name climbing out with ../../ lands
    in the root and can be seen there.
    """
    root = tempfile.mkdtemp(prefix="vpm_names_%s_" % tag)
    folder = os.path.join(root, "a", "b", "out")
    os.makedirs(folder)
    return root, folder


def outside(root, folder):
    """Every file under *root* that is not under *folder*."""
    inner = os.path.abspath(folder) + os.sep
    found = []
    for where, _dirs, names in os.walk(root):
        for name in names:
            path = os.path.abspath(os.path.join(where, name))
            if not path.startswith(inner):
                found.append(os.path.relpath(path, root))
    return sorted(found)


def run(server, what):
    """Run *what* with the stand-in in place of curl; (result, log, error)."""
    old = vpm._curl_call
    vpm._curl_call = server
    said = io.StringIO()
    result, error = None, ""
    try:
        with contextlib.redirect_stdout(said):
            result = what()
    except Exception as why:
        error = str(why)
    finally:
        vpm._curl_call = old
    return result, said.getvalue(), error


def refusal(name):
    """The line the run says a name in: the program's own words for it."""
    return vpm.T('  auphonic.com named a file "%s" -- not a plain file '
                 'name, so it is not fetched') % name


def as_server_path(path):
    """An absolute path spelled the way a server spells one: slashes."""
    return path.replace(os.sep, "/")


# ------------------------------------------- 1. The transcripts beside it
print("1. The transcripts beside the result")

root, folder = ground("text")
absolute = as_server_path(os.path.join(root, "absolute.txt"))
refused = [".hidden.srt", "..\\..\\back.srt", "C:drive.srt"]
server = Server()
_, log, error = run(server, lambda: vpm.fetch_text_outputs(
    KEY, [{"filename": name, "download_url": "https://auphonic.com/dl/%d" % i}
          for i, name in enumerate(["../../escaped.txt", absolute,
                                    "fine.srt"] + refused)],
    folder))
written = sorted(os.path.relpath(p, root) for p in server.fetched)

inside = os.path.join(folder, "escaped.txt")
check("a name climbing out with ../ is fetched inside the folder",
      os.path.abspath(inside) in server.fetched,
      "written to %s" % (written,))
inside = os.path.join(folder, "absolute.txt")
check("an absolute name is fetched inside the folder",
      os.path.abspath(inside) in server.fetched,
      "written to %s" % (written,))
names = sorted(os.path.basename(p) for p in server.fetched)
check("a name with no plain file name left is not fetched at all",
      names == ["absolute.txt", "escaped.txt", "fine.srt"],
      "fetched %s" % (names,))
unsaid = [name for name in refused if refusal(name) not in log]
check("every name not fetched is named in the log", not unsaid,
      "%d of %d refused names missing from the log: %s"
      % (len(unsaid), len(refused), unsaid))
strays = outside(root, folder)
check("nothing of the transcripts is written outside the folder",
      not strays and not error,
      "outside: %s, error: %s" % (strays, error or "none"))
shutil.rmtree(root, ignore_errors=True)

# ----------------------------------------------- 2. The single result
print("\n2. The single result")

vpm.kept_channels = lambda audio: 1
vpm.channel_count = lambda audio: 1
vpm.wishes_then_start = lambda key, uuid, stereo=False: None
OUTPUTS = []
vpm.wait_for_production = lambda key, uuid, wait_s: {
    "output_files": list(OUTPUTS)}
spoken = tempfile.mkdtemp(prefix="vpm_names_audio_")
audio = os.path.join(spoken, "Episode.wav")
with open(audio, "wb") as f:
    f.write(b"\0" * 2000)

root, folder = ground("single")
OUTPUTS[:] = [{"filename": "../../result.wav",
               "download_url": "https://auphonic.com/dl/result.wav"}]
server = Server()
came, log, error = run(server, lambda: vpm.run_single_production(
    audio, "PRESETUUID", "Podcast", KEY, folder, 60))
check("a result climbing out with ../ is fetched inside the folder",
      came == os.path.join(folder, "result.wav")
      and not outside(root, folder),
      "came back %s, outside: %s, error: %s"
      % (came and os.path.relpath(came, root), outside(root, folder),
         error or "none"))
shutil.rmtree(root, ignore_errors=True)

root, folder = ground("single_refused")
OUTPUTS[:] = [{"filename": "C:result.wav",
               "download_url": "https://auphonic.com/dl/result.wav"}]
server = Server()
came, log, error = run(server, lambda: vpm.run_single_production(
    audio, "PRESETUUID", "Podcast", KEY, folder, 60))
check("a result with no plain file name stops the run, fetching nothing",
      bool(error) and not server.fetched and refusal("C:result.wav") in log,
      "error: %s, fetched %d, named in the log: %s"
      % (error or "none", len(server.fetched),
         refusal("C:result.wav") in log))
shutil.rmtree(root, ignore_errors=True)
shutil.rmtree(spoken, ignore_errors=True)

# ------------------------------------------- 3. The multitrack archive
print("\n3. The multitrack archive")

root, folder = ground("tracks")
tracks = vpm.tracks_folder(folder, create=False)
production = {"output_files": [
    {"filename": "../../tracks.zip",
     "download_url": "https://auphonic.com/dl/tracks.zip"},
    {"filename": "../../chapters.txt",
     "download_url": "https://auphonic.com/dl/chapters.txt"}]}
server = Server(["../../Guest.wav", "Presenter.wav"])
came, log, error = run(server, lambda: vpm.download_results(
    KEY, production, ["Guest", "Presenter"], folder, "Episode"))
came = came or {}
written = sorted(os.path.relpath(p, root) for p in server.fetched)
check("an archive named with ../ is fetched inside the tracks folder",
      os.path.abspath(os.path.join(tracks, "tracks.zip")) in server.fetched,
      "written to %s, error: %s" % (written, error or "none"))
check("an extra output named with ../ is fetched inside the tracks folder",
      os.path.abspath(os.path.join(tracks, "chapters.txt"))
      in server.fetched,
      "written to %s" % (written,))
guest = came.get("Guest") or ""
check("a track whose entry climbs out is handed back where it was written",
      os.path.isfile(guest) and os.path.abspath(guest).startswith(
          os.path.abspath(tracks) + os.sep),
      "Guest -> %s, there: %s"
      % (guest and os.path.relpath(guest, root), os.path.isfile(guest)))
strays = outside(root, folder)
check("nothing of the archive is written outside the folder", not strays,
      "outside: %s" % (strays,))
shutil.rmtree(root, ignore_errors=True)

root, folder = ground("tracks_refused")
production = {"output_files": [
    {"filename": ".hidden.zip",
     "download_url": "https://auphonic.com/dl/tracks.zip"}]}
server = Server(["Guest.wav"])
came, log, error = run(server, lambda: vpm.download_results(
    KEY, production, ["Guest"], folder, "Episode"))
check("an archive with no plain file name stops the run, fetching nothing",
      bool(error) and not server.fetched and refusal(".hidden.zip") in log,
      "error: %s, fetched %d, named in the log: %s"
      % (error or "none", len(server.fetched),
         refusal(".hidden.zip") in log))
shutil.rmtree(root, ignore_errors=True)

print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
