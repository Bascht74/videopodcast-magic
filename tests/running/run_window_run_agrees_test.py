# -*- coding: utf-8 -*-
"""A run started in the window writes what the same line writes.

On way_ground's production, a real run through each door: the line the
test writes, with the answers the window's fields give beside it, then
the window's own Start, offscreen and not a dry run. Then the doors
against each other: the same files by name, the same handover but for
the folder, every camera file with the same streams and tags, every
sound track byte for byte. The limit: the plain path, not multitrack;
cut lists and EDLs are cut_stored_voices_used's, the metrics nobody's.
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
import hashlib
import json
import shutil
import subprocess
import tempfile
import time
import the_program
import way_ground as ground

SCRIPT = the_program.SCRIPT
began = time.time()
done = 0
bad = []


def check(name, ok, extra=""):
    global done
    done += 1
    print("  %-58s %s %s" % (name, "ok" if ok else "FAIL", extra))
    if not ok:
        bad.append("%s [%s]" % (name, extra or "no numbers"))


def stop():
    """Nothing further can be asked, so count what there is and go."""
    print("\n%d checks in %.2f s" % (done, time.time() - began))
    print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
    sys.exit(1 if bad else 0)


if ground.missing():
    print("SKIPPED: " + ground.missing())
    stop()

STORE = tempfile.mkdtemp(prefix="vpm_way_store_")
os.environ["VPM_CACHE"] = STORE
os.environ["QT_QPA_PLATFORM"] = "offscreen"
from PySide6 import QtWidgets
app = QtWidgets.QApplication(sys.argv[:1])
vpm = the_program.load()
vpm.set_language("en")
vpm.list_presets = lambda key: []
vpm.load_api_key = lambda: ""
# Nothing is written down from speech: that would fetch a model, and
# no judgement here is about words.
vpm.words_at_hand = lambda *a, **k: []
vpm.recognise_speech = lambda *a, **k: ([], "")

# What a fresh window's fields send beside the project file: its
# loudness field and its speech language. The line is given the same,
# so that a difference below is the door's and not the answers'.
AS_THE_WINDOW = ["--lufs", "-16", "--speech-language", "eng"]


def without_folder(d, out):
    """A handover as text, with its own output folder taken out."""
    text = json.dumps(d, sort_keys=True, ensure_ascii=False)
    return text.replace(json.dumps(out)[1:-1], "<out>")


def streams(path):
    """A camera file's streams: tags and a hash of each, copied not decoded."""
    tags = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries",
         "format_tags:stream_tags", "-of", "compact", path],
        stdout=subprocess.PIPE).stdout.decode("utf-8", "replace")
    sums = subprocess.run(
        ["ffmpeg", "-v", "error", "-i", path, "-map", "0", "-c", "copy",
         "-f", "streamhash", "-hash", "md5", "-"],
        stdout=subprocess.PIPE).stdout.decode("utf-8", "replace")
    return tags.split() + sums.split()


def sums(out, names):
    """The md5 of each named file under *out*."""
    return dict((n, hashlib.md5(open(os.path.join(out, n), "rb").read())
                 .hexdigest()) for n in names)


WORK = ground.own_folder("agrees")
OUT_LINE = os.path.join(WORK, "line")
OUT_WINDOW = os.path.join(WORK, "window")
os.makedirs(OUT_WINDOW)
os.makedirs(os.path.join(WORK, "project"))

print("1. The command line, as a test writes it")
code, said, stuck = ground.line_run(
    ground.line(SCRIPT, ground.separation_file(vpm, WORK), OUT_LINE,
                AS_THE_WINDOW), STORE)
by_line = ground.handover(OUT_LINE)
tail = [x.strip() for x in said.replace(WORK, "<work>").splitlines()
        if x.strip()][-3:]
check("the line's run came back with 0 and wrote its handover",
      not stuck and code == 0 and by_line is not None,
      "return code %s%s, handover %s -- the log ends: %s"
      % (code, " after standing still" if stuck else "",
         "there" if by_line else "missing", " / ".join(tail)[-240:]))

print("\n2. The window, opened on the same production and started")
PROJECT = ground.project_file(vpm, os.path.join(WORK, "project"), OUT_WINDOW)
kept = ground.window_run(vpm, app, PROJECT, {})
by_window = ground.handover(OUT_WINDOW)
check("the window's Start ran a run to its end, with a handover",
      kept["ended"] and not kept["why"] and by_window is not None,
      "loop %s, %s, handover %s, dry run %s"
      % ("came back" if kept["ended"] else "never came back",
         kept["why"] or "nothing given up",
         "there" if by_window else "missing",
         "--dry-run" in (kept["argv"] or [])))

print("\n3. The two doors against each other")
ours = ground.written_names(OUT_LINE)
theirs = ground.written_names(OUT_WINDOW)
check("the window writes the same files as the line",
      len(ours) >= 8 and ours == theirs,
      "line %d files, window %d; only the line: %s; only the window: %s"
      % (len(ours), len(theirs), sorted(set(ours) - set(theirs)),
         sorted(set(theirs) - set(ours))))
keys = sorted(k for k in set(by_line or {}) | set(by_window or {})
              if without_folder((by_line or {}).get(k), OUT_LINE)
              != without_folder((by_window or {}).get(k), OUT_WINDOW))
check("the window's handover is the line's but for the folder",
      by_line is not None and by_window is not None and not keys,
      "%d keys differ: %s" % (len(keys), "; ".join(
          "%s line %s / window %s"
          % (k, without_folder((by_line or {}).get(k), OUT_LINE)[:70],
             without_folder((by_window or {}).get(k), OUT_WINDOW)[:70])
          for k in keys)[:600]))
films = [n for n in ours if n.lower().endswith(".mov") and n in theirs]
apart = [n for n in films if streams(os.path.join(OUT_LINE, n))
         != streams(os.path.join(OUT_WINDOW, n))]
check("every camera file carries the line's streams and tags",
      len(films) == 3 and not apart,
      "%d camera files in both, %d apart: %s%s"
      % (len(films), len(apart), apart,
         "" if not apart else " -- line %s / window %s"
         % ([x for x in streams(os.path.join(OUT_LINE, apart[0]))
             if x not in streams(os.path.join(OUT_WINDOW, apart[0]))],
            [x for x in streams(os.path.join(OUT_WINDOW, apart[0]))
             if x not in streams(os.path.join(OUT_LINE, apart[0]))])))
tracks = [n for n in ours if n.lower().endswith(".wav") and n in theirs]
line_sums, window_sums = sums(OUT_LINE, tracks), sums(OUT_WINDOW, tracks)
check("every sound track is the line's, byte for byte",
      len(tracks) >= 2 and line_sums == window_sums,
      "%d tracks in both, apart: %s"
      % (len(tracks), sorted(n for n in tracks
                             if line_sums[n] != window_sums[n])))

shutil.rmtree(WORK, ignore_errors=True)
shutil.rmtree(STORE, ignore_errors=True)
stop()
