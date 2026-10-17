# -*- coding: utf-8 -*-
"""An intro or outro without its file is named before Resolve is asked.

A handover written by hand into a folder of the test's own, handed to
build_resolve_project as a file the way --resolve-json hands it, with
a Resolve standing in that notes whether it was asked at all. In
order: an intro with no source and an outro whose source is empty --
each ends the build in 1 on the sentence naming it, and Resolve is
never asked -- and the same handover with both files named, which the
door lets through. The limit: a stand-in, not Resolve.
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
import the_program
import contextlib
import io
import json
import shutil
import tempfile
import time
import resolve_stand_in as stand

began = time.time()
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


WORK = tempfile.mkdtemp(prefix="edge_file_")
CAMERA = os.path.join(WORK, "WideCam_C001.mov")
INTRO = os.path.join(WORK, "Intro.mov")
OUTRO = os.path.join(WORK, "Outro.mov")
for made in (CAMERA, INTRO, OUTRO):
    open(made, "wb").close()
HANDOVER = {"format": vpm.FILE_FORMAT, "fps": 25.0,
            "start_tc": "01:00:00:00", "length_s": 60.0,
            "production": "Episode", "speakers": [],
            "cameras": [{"camera": "WideCam_C001", "track": "WideCam_C001",
                         "file": CAMERA, "source": CAMERA, "wide": True,
                         "offset": 0.0, "duration": 60.0, "fps": 25.0}],
            "cut": [{"start": 10.0, "end": 20.0, "camera": "WideCam_C001"}]}
# Every time the build reaches for Resolve, it is written down here.
ASKED = []


def reached():
    ASKED.append("connect_to_resolve")
    return stand.Resolve(stand.ProjectManager(names=["Episode"]))


vpm.connect_to_resolve = reached
NO_FILE = vpm.T("This handover names no file for the %s, so the timeline "
                "cannot be built from it. Please make the run again.")


def build(name, **edges):
    """One build from a handover file; (its code or exception, said)."""
    path = os.path.join(WORK, name + "_resolve.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(dict(HANDOVER, **edges), f)
    del ASKED[:]
    said = io.StringIO()
    try:
        with contextlib.redirect_stdout(said):
            code = vpm.build_resolve_project(path, "keep", log="")
    except Exception as e:
        code = "%s: %s" % (type(e).__name__, e)
    return code, said.getvalue()


print("1. An intro or an outro without its file")
code, said = build("no_intro", intro={"duration": 5.0, "has_audio": True})
named = NO_FILE % vpm.label_of(vpm.TYPE_INTRO)
check("an intro without its file is named before Resolve is asked",
      code == 1 and named in said and not ASKED,
      "the build ended in %r, the sentence %s, Resolve asked %d times"
      % (code, "said" if named in said else "not said", len(ASKED)))
code, said = build("empty_outro", outro={"source": "", "duration": 5.0,
                                         "has_audio": True})
named = NO_FILE % vpm.label_of(vpm.TYPE_OUTRO)
check("an outro whose file is empty is named before Resolve is asked",
      code == 1 and named in said and not ASKED,
      "the build ended in %r, the sentence %s, Resolve asked %d times"
      % (code, "said" if named in said else "not said", len(ASKED)))

print("\n2. Both with their files")
both = dict(HANDOVER, intro={"source": INTRO, "duration": 5.0},
            outro={"source": OUTRO, "duration": 5.0})
said = vpm.handover_complaint(both)
check("an intro and an outro with their files pass the door", said == "",
      "the door said %r" % said[:90])

shutil.rmtree(WORK, ignore_errors=True)
print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
