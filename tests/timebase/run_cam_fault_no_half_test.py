# -*- coding: utf-8 -*-
"""A camera that cannot be written is named, and leaves no piece behind.

Whole runs over a copy of the mixedcase fixture. The sections: the disk
fills while one camera is written, command line; one camera's file is
gone when its turn comes, command line; the disk fills, in the window.
Each: the camera named with the reason, the run not counted as done;
where the disk filled, no cut-short file left under the camera's name.
The limit: the full disk is a stand-in for ffmpeg, not a full disk.
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
import re
import shutil
import tempfile
import time
import types
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

STORE = tempfile.mkdtemp(prefix="vpm_camfault_store_")
os.environ["VPM_CACHE"] = STORE
os.environ["QT_QPA_PLATFORM"] = "offscreen"
from PySide6 import QtWidgets
app = QtWidgets.QApplication(sys.argv[:1])
vpm = the_program.load()
vpm.set_language("en")
vpm.list_presets = lambda key: []
vpm.load_api_key = lambda: ""
vpm.words_at_hand = lambda *a, **k: []
vpm.recognise_speech = lambda *a, **k: ([], "")

# What ffmpeg says when the disk is full, and a stand-in for it: the
# camera's file begun and cut short, then that line and a failure.
FULL = "av_interleaved_write_frame(): No space left on device"
CHILD = """import os, sys, types
sys.path.insert(0, %r)
import the_program
vpm = the_program.load()
FAULT, VICTIM, OUT, RECORD = sys.argv[1:5]
del sys.argv[1:5]
real = vpm.run_ffmpeg_with_progress
place = real.__globals__
sub = place["subprocess"]
fake = types.ModuleType("subprocess")
fake.__dict__.update(sub.__dict__)
def same(path):
    return os.path.normcase(os.path.abspath(str(path)))
def Popen(cmd, *a, **k):
    out = str(cmd[-1])
    if (FAULT == "full" and same(out).startswith(same(OUT))
            and out.endswith(".mov") and same(VICTIM) in map(same, cmd)):
        with open(out, "wb") as f:
            f.write(bytes(65536))
        with open(RECORD, "a") as f:
            f.write(out + "\\n")
        cmd = [sys.executable, "-c",
               "import sys; sys.stderr.write(%%r); sys.exit(1)" %% (%r + "\\n")]
    return sub.Popen(cmd, *a, **k)
fake.Popen = Popen
place["subprocess"] = fake
def gone(cmd, duration, text):
    if (FAULT == "vanish" and os.path.basename(str(cmd[-1])).startswith(
            "mix_full") and os.path.exists(VICTIM)):
        os.remove(VICTIM)
    return real(cmd, duration, text)
vpm.run_ffmpeg_with_progress = gone
sys.argv = ["videopodcast-magic"] + sys.argv[1:]
sys.exit(vpm.main())
""" % (HERE, FULL)


def said_under(text, camera):
    """What the run said under one camera's heading, up to the next one."""
    text = re.sub(r"\x1b\[[0-9;]*m", "", text)
    head = vpm.T('\nPROCESSING: %s').strip()
    at = text.find(head % camera)
    if at < 0:
        return ""
    rest = text[at + len(head % camera):]
    ends = rest.find(head.split("%s")[0])
    return rest if ends < 0 else rest[:ends]


def same(path):
    """A path spelt one way, whatever slashes and case it came in."""
    return os.path.normcase(os.path.abspath(str(path)))


def left_of(record):
    """The cut-short files the stand-in began that are still there.

    (what is left, with sizes; how many the stand-in began).
    """
    try:
        with open(record, encoding="utf-8") as f:
            begun = f.read().splitlines()
    except OSError:
        begun = []
    return (["%s (%d bytes)" % (os.path.basename(p), os.path.getsize(p))
             for p in begun if os.path.exists(p)], len(begun))


def line(fault, out, record):
    """The command line of a child run with *fault* planted in it."""
    whole = ground.line(STARTER, SEPARATION, out)
    return whole[:2] + [fault, PRES, out, record] + whole[2:]


WORK = ground.own_folder("camfault")
try:
    # A copy, because one section takes a camera away mid-run.
    ground.MEDIA = os.path.join(WORK, "media")
    shutil.copytree(ground.fixture("mixedcase"), ground.MEDIA)
    PRES = ground.media(ground.PRES)
    CAMERA = os.path.basename(PRES)
    SEPARATION = ground.separation_file(vpm, WORK)
    STARTER = os.path.join(WORK, "child.py")
    with open(STARTER, "w", encoding="utf-8") as f:
        f.write(CHILD)
    ERROR = vpm.T('  Error while writing: %s').strip() % ""

    print("1. The disk fills while one camera is written, command line")
    OUT = os.path.join(WORK, "full")
    RECORD = os.path.join(WORK, "begun1")
    code, text, stuck = ground.line_run(line("full", OUT, RECORD),
                                        os.path.join(WORK, "cache1"))
    under = said_under(text, CAMERA)
    check("a camera the full disk broke off is named with the reason",
          ERROR in under and FULL in under,
          "'%s' %s and '%s' %s under %s; returned %r, stood still %s"
          % (ERROR, "said" if ERROR in under else "not said", FULL,
             "said" if FULL in under else "not said", CAMERA, code, stuck))
    check("a run that lost a camera to a full disk returns 1", code == 1,
          "returned %r against 1, stood still %s" % (code, stuck))
    left, begun = left_of(RECORD)
    check("no cut-short file is left under a camera the disk broke off",
          begun and not left, "the stand-in began %d, left: %s"
          % (begun, left or "nothing"))

    print("\n2. One camera's file is gone when its turn comes, command line")
    OUT = os.path.join(WORK, "gone")
    code, text, stuck = ground.line_run(
        line("vanish", OUT, os.path.join(WORK, "begun2")),
        os.path.join(WORK, "cache2"))
    under = said_under(text, CAMERA)
    MISSING = os.strerror(2)
    check("a camera whose file went mid-run is named with the reason",
          ERROR in under and MISSING in under,
          "'%s' %s and '%s' %s under %s; returned %r, stood still %s"
          % (ERROR, "said" if ERROR in under else "not said", MISSING,
             "said" if MISSING in under else "not said", CAMERA, code,
             stuck))
    check("a run that lost a camera's file mid-run returns 1", code == 1,
          "returned %r against 1, stood still %s" % (code, stuck))

    print("\n3. The disk fills while one camera is written, the window")
    # The copy of section 2 lost its camera; the window gets a fresh one.
    shutil.rmtree(ground.MEDIA)
    shutil.copytree(ground.fixture("mixedcase"), ground.MEDIA)
    OUT = os.path.join(WORK, "window")
    os.makedirs(OUT)
    os.makedirs(os.path.join(WORK, "project"))
    RECORD = os.path.join(WORK, "begun3")
    place = vpm.run_ffmpeg_with_progress.__globals__
    sub = place["subprocess"]
    fake = types.ModuleType("subprocess")
    fake.__dict__.update(sub.__dict__)

    def Popen(cmd, *a, **k):
        """ffmpeg, but the disk is full for the one camera's file."""
        out = str(cmd[-1])
        if (same(out).startswith(same(OUT)) and out.endswith(".mov")
                and same(PRES) in map(same, cmd)):
            with open(out, "wb") as f:
                f.write(bytes(65536))
            with open(RECORD, "a") as f:
                f.write(out + "\n")
            cmd = [sys.executable, "-c", "import sys; sys.stderr.write(%r); "
                   "sys.exit(1)" % (FULL + "\n")]
        return sub.Popen(cmd, *a, **k)

    fake.Popen = Popen
    place["subprocess"] = fake
    try:
        kept = ground.window_run(vpm, app, ground.project_file(
            vpm, os.path.join(WORK, "project"), OUT), {})
    finally:
        place["subprocess"] = sub
    text = "".join(kept["log"])
    under = said_under(text, CAMERA)
    check("the window names a camera the full disk broke off, and why",
          ERROR in under and FULL in under,
          "'%s' %s and '%s' %s under %s; loop %s, %s"
          % (ERROR, "said" if ERROR in under else "not said", FULL,
             "said" if FULL in under else "not said", CAMERA,
             "back" if kept["ended"] else "never back",
             kept["why"] or "nothing given up"))
    errors = vpm.T('\nFinished with errors.\n').strip()
    finished = vpm.run_done_text(False).strip()
    check("a window run that lost a camera finishes with errors, not done",
          errors in text and finished not in text,
          "'%s' %s, '%s' %s" % (errors, "said" if errors in text else
                                "missing", finished[:40], "said" if
                                finished in text else "not said"))
    left, begun = left_of(RECORD)
    check("the window's result folder keeps no cut-short camera file",
          begun and not left, "the stand-in began %d, left: %s"
          % (begun, left or "nothing"))
except Exception:
    import traceback
    traceback.print_exc()
    bad.append("the test itself broke off")

shutil.rmtree(WORK, ignore_errors=True)
shutil.rmtree(STORE, ignore_errors=True)
stop()
