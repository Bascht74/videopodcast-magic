# -*- coding: utf-8 -*-
"""A command-line run goes up to auphonic.com under its production's name.

A run finds a production again by its title alone; one title every run
shared found last week's production for this week's recordings. main()
in this process, on material in episode folders; auphonic.com stood in
where the tracks go up, noting the title and ending the run there.
Sections: two weeks without a picture, one recording, two weeks with a
picture, a name given with --production, and the window's own line,
whose production name stays the title it was.
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
import subprocess
import tempfile
import time
import the_program

began = time.time()
os.environ["VPM_NO_UPDATE_CHECK"] = "1"
vpm = the_program.load()
vpm.set_language("en")

done = 0
bad = []


def check(name, ok, extra=""):
    global done
    done += 1
    print("  %-58s %s %s" % (name, "ok" if ok else "FAIL", extra))
    if not ok:
        bad.append("%s [%s]" % (name, extra or "no numbers"))


KEY = "FAKEKEY-0000"
sent = []
called = []


class Handed(Exception):
    """Raised where the tracks would go up: the title is noted, no more."""


def multi(_key, _preset, title, *_a, **_k):
    """One Multitrack production: its title noted, and the run ends."""
    sent.append(title)
    raise Handed("the stand-in ends the run here")


def single(_audio, _preset, _presetname, _key, _folder, _wait, _dry, title,
           *_a, **_k):
    """One Singletrack production: its title noted, and the run ends."""
    sent.append(title)
    raise Handed("the stand-in ends the run here")


def offline(_key, arguments, *_a, **_k):
    """The one road to auphonic.com: a paying account, nothing else."""
    called.append(" ".join(str(a) for a in arguments))
    if any(str(a).endswith("/api/user.json") for a in arguments):
        return json.dumps({"status_code": 200, "data": {
            "credits": 10.0, "is_paying_user": True}})
    raise RuntimeError("auphonic.com is not asked for that in this test")


vpm._curl_call = offline
vpm.load_api_key = lambda *a, **k: KEY
vpm.preset_for_run = lambda args, key, multitrack: ("PRESETUUID", "Podcast")
vpm.run_multitrack_production = multi
vpm.run_single_production = single

ROOM = tempfile.mkdtemp(prefix="vpm_title_window_")
TALK = os.path.join(HERE, "samples", "twovoices", "talk.wav")


def made(path, *args):
    """A file written by ffmpeg out of the checked-in talk; its path."""
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", TALK]
                   + list(args) + [path], check=True)
    return path


def week(name, files):
    """An episode folder holding copies of *files*; their paths there."""
    folder = os.path.join(ROOM, "Shows", name)
    os.makedirs(folder, exist_ok=True)
    return [shutil.copy(f, folder) for f in files]


def run(argv):
    """main() on this command line: the titles that went up, and its log."""
    del sent[:]
    sys.argv = ["videopodcast-magic"] + list(argv)
    log = io.StringIO()
    kept, sys.stdin = sys.stdin, io.StringIO("")
    try:
        with contextlib.redirect_stdout(log):
            vpm.main()
    except SystemExit:
        pass
    except Exception as why:     # a fault is a finding here, not a crash
        bad.append("the run ran into %s: %s" % (type(why).__name__, why))
    finally:
        sys.stdin = kept
    return list(sent), log.getvalue()


def line(argv, preset="Podcast_Multi"):
    """The line typed for a run of *argv*, beside its own out folder."""
    out = os.path.join(os.path.dirname(argv[0]), "out")
    return list(argv) + ["--auphonic-preset", preset, "--out", out,
                         "--lufs", "source", "--no-metrics",
                         "--no-speech-recognition", "--no-transcript-file"]


try:
    # Two recordings of one talk, the second a quarter second late, so
    # the two find each other on an axis; a small picture carries the
    # first.
    GUEST = made(os.path.join(ROOM, "Guest.wav"), "-ar", "48000", "-ac", "1")
    PRESENTER = made(os.path.join(ROOM, "Presenter.wav"), "-af",
                     "adelay=250", "-ar", "48000", "-ac", "1")
    CAMERA = os.path.join(ROOM, "WideCam.mp4")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i",
                    "smptebars=size=160x90:rate=25", "-i", GUEST,
                    "-shortest", "-c:v", "libx264", "-preset", "ultrafast",
                    "-pix_fmt", "yuv420p", "-c:a", "aac", "-ar", "48000",
                    CAMERA], check=True)

    print("1. Two weeks, two recordings, no picture")
    titles = []
    for name in ("Episode_41", "Episode_42"):
        titles += run(line(week(name, [GUEST, PRESENTER])))[0]
    check("two weeks without a picture go up under their folders' names",
          titles == ["Episode_41", "Episode_42"],
          "titles sent %r, wanted ['Episode_41', 'Episode_42']" % titles)

    print("\n2. One recording, no picture")
    titles, _log = run(line(week("Episode_43", [GUEST]), "Podcast_Single"))
    check("a lone recording goes up under its folder's name, not its own",
          titles == ["Episode_43"],
          "titles sent %r, wanted ['Episode_43']" % titles)

    print("\n3. Two weeks with a picture")
    titles = []
    for name in ("Episode_44", "Episode_45"):
        titles += run(line(week(name, [GUEST, PRESENTER, CAMERA])))[0]
    check("two weeks with a picture go up under their folders' names",
          titles == ["Episode_44", "Episode_45"],
          "titles sent %r, wanted ['Episode_44', 'Episode_45']" % titles)

    print("\n4. A name given on the line")
    titles, _log = run(line(week("Episode_46", [GUEST, PRESENTER]))
                       + ["--production", "Pilot rerun"])
    check("a name given with --production is the title",
          titles == ["Pilot rerun"],
          "titles sent %r, wanted ['Pilot rerun']" % titles)

    print("\n5. The window's own line")
    files = week("Episode_47", [GUEST, PRESENTER])
    ASSIGN = os.path.join(ROOM, "assign.json")
    argv, plan, _m = vpm.run_argv({
        "files": [(f, "audio") for f in files], "clip_kinds": {},
        "out_folder": os.path.join(ROOM, "out47"), "multitrack": True,
        "production": "Pilot", "cameras": [], "cut": {},
        "wide_at_edges": False, "key": KEY, "preset": "Podcast_Multi"},
        ASSIGN)
    with open(ASSIGN, "w", encoding="utf-8") as f:
        json.dump(plan or {}, f)
    titles, _log = run(list(argv or ["-"])[1:])
    check("the window's production name stays the title, not the folder",
          titles == ["Pilot"], "titles sent %r, wanted ['Pilot']" % titles)
except Exception as e:
    bad.append("the test ran into %s: %s" % (type(e).__name__, e))
finally:
    shutil.rmtree(ROOM, True)

print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
