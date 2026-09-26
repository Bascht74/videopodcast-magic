# -*- coding: utf-8 -*-
"""The project type reaches the run and says what sync leaves out.

One switch, --project-type, and three doors it has to pass. The parser
takes cut and sync, answers cut on its own and refuses any other word.
main() turns sync into the three switches the pipeline already reads --
no local speaker split, no speech recognition, no transcript file --
and leaves them alone for a cut. And run_argv puts the window's choice
on the line: only the two words the parser takes, and nothing while the
window has not asked. main() is stopped at a stand-in preflight, so
nothing is measured: what is judged is the namespace as the preflight
and everything after it read it, not a run.
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
import shutil
import tempfile
import time

# The material: a file name the parser and main() accept. Nothing
# reads it, because the run is stopped at the preflight below. The
# cache stands beside it, so the tidying main() does on its way in
# touches nothing of the person's own.
FOLDER = tempfile.mkdtemp(prefix="vpm_project_type_")
SOUND = os.path.join(FOLDER, "recorder.wav")
io.open(SOUND, "wb").close()
os.makedirs(os.path.join(FOLDER, "cache"))
os.environ["VPM_CACHE"] = os.path.join(FOLDER, "cache")

import the_program

began = time.time()
SCRIPT = the_program.SCRIPT

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


def parsed(*words):
    """The namespace, or the exit code argparse leaves with."""
    kept = sys.stderr
    sys.stderr = io.StringIO()
    try:
        return vpm.build_argument_parser().parse_args(list(words) + [SOUND])
    except SystemExit as e:
        return e.code
    finally:
        sys.stderr = kept


print("1. The parser: cut and sync, cut by itself, other words refused")
plain = parsed()
check("without the switch the run is a cut",
      getattr(plain, "project_type", None) == "cut",
      "project_type is %r, wanted 'cut'"
      % (getattr(plain, "project_type", plain),))
chosen = parsed("--project-type", "sync")
check("--project-type sync is taken",
      getattr(chosen, "project_type", None) == "sync",
      "project_type is %r, wanted 'sync'"
      % (getattr(chosen, "project_type", chosen),))
other = parsed("--project-type", "both")
check("a word other than cut or sync is refused",
      other == 2, "parse_args gave %r, wanted the exit code 2"
      % (other if isinstance(other, int)
         else "a namespace with project_type=%r"
         % getattr(other, "project_type", None),))

print("\n2. main(): sync sets three switches, cut leaves them as typed")
seen = []


def stand_in_preflight(args, audio_paths, video_paths):
    """Stops the run where the preflight would, and keeps what it saw.

    The three parameters and no more, as the program's own preflight
    has them: a stand-in taking anything would hide a call the real
    one refuses.
    """
    seen.append(args)
    return 1


vpm.run_preflight = stand_in_preflight


def run_with(*words):
    """main() on this command line, up to the preflight.

    main() leaves through sys.exit on some paths; the code is handed
    back so that a run refused before the preflight is a red line, not
    a traceback.
    """
    del seen[:]
    sys.argv = [SCRIPT] + list(words) + [SOUND]
    try:
        return vpm.main()
    except SystemExit as e:
        return e.code


code = run_with("--project-type", "sync")
check("the run stops at the stand-in preflight",
      code == 1 and len(seen) == 1,
      "main() returned %r and the preflight was reached %d times, "
      "wanted 1 and once" % (code, len(seen)))
args = seen[0] if seen else None
check("sync switches the local speaker split off",
      getattr(args, "no_speakers_local", None) is True,
      "no_speakers_local is %r, wanted True"
      % (getattr(args, "no_speakers_local", None),))
check("sync switches speech recognition off",
      getattr(args, "no_speech_recognition", None) is True,
      "no_speech_recognition is %r, wanted True"
      % (getattr(args, "no_speech_recognition", None),))
check("sync writes no transcript file",
      getattr(args, "no_transcript_file", None) is True,
      "no_transcript_file is %r, wanted True"
      % (getattr(args, "no_transcript_file", None),))
code = run_with("--project-type", "cut")
args = seen[0] if seen else None
three = [getattr(args, name, None)
         for name in ("no_speakers_local", "no_speech_recognition",
                      "no_transcript_file")]
check("a cut leaves the three switches as typed",
      code == 1 and three == [False, False, False],
      "main() returned %r and the three are %r, wanted 1 and "
      "[False, False, False]" % (code, three))

print("\n3. run_argv: the window's choice goes on the line, nothing "
      "when unset")


def line_with(**more):
    """The command line the window would build, cut switches and all."""
    values = {"files": [(SOUND, "audio")], "clip_kinds": {},
              "multitrack": False, "key": "", "preset": ""}
    values.update(more)
    argv, _plan, _messages = vpm.run_argv(values, "")
    return argv or []


def after(argv, switch):
    """The word behind a switch, or None where the switch is not there."""
    if switch not in argv or argv.index(switch) + 1 >= len(argv):
        return None
    return argv[argv.index(switch) + 1]


line = line_with(project_type="sync")
check("sync stands on the line",
      after(line, "--project-type") == "sync",
      "--project-type carries %r, wanted 'sync'; %d words on the line"
      % (after(line, "--project-type"), len(line)))
line = line_with(project_type="cut")
check("cut stands on the line too",
      after(line, "--project-type") == "cut",
      "--project-type carries %r, wanted 'cut'; %d words on the line"
      % (after(line, "--project-type"), len(line)))
line = line_with(project_type="")
check("an unset type puts nothing on the line",
      "--project-type" not in line,
      "--project-type stands %d times on the line, carrying %r, wanted 0"
      % (line.count("--project-type"), after(line, "--project-type")))
line = line_with(project_type="both")
check("a word the parser would refuse stays off the line",
      "--project-type" not in line,
      "--project-type stands %d times on the line, carrying %r, wanted 0"
      % (line.count("--project-type"), after(line, "--project-type")))

shutil.rmtree(FOLDER, True)
print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
