# -*- coding: utf-8 -*-
"""A run refuses a --new-name it cannot follow as given, and says why.

Dry runs on the interview fixture. In order: the fixture holds its
cameras; two cameras given one name, two names differing only in case,
and a name equal to another camera's stem are refused with both files
named; a name with a separator or drive colon is refused naming it, one
beginning with a dot and an empty one with the reason; a file that is
no camera of the run by name, one file given two names with both; names
beside assigned cameras, and for cameras alone, with the reason. Two
distinct names pass, alone and beside a --speakers-from file, read too.
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
SCRIPT = the_program.SCRIPT
import glob
import json
import shutil
import subprocess
import tempfile
import threading
import time

sys.path.insert(0, HERE)
from fixture_root import fixture

vpm = the_program.load()
vpm.set_language("en")

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
    shutil.rmtree(OUT, ignore_errors=True)
    shutil.rmtree(HELD, ignore_errors=True)
    print("\n%d checks in %.2f s" % (done, time.time() - began))
    print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
    sys.exit(1 if bad else 0)


# No output at all for this long, and the run is stuck rather than slow:
# standstill, not a deadline, so a builder nine times slower still passes.
STILL = 120.0
OUT = tempfile.mkdtemp(prefix="vpm_newname_")
HELD = tempfile.mkdtemp(prefix="vpm_newname_assign_")
ENV = dict(os.environ, LANG="C", LC_ALL="C", LANGUAGE="en",
           VPM_SILENT="1", VPM_NO_SPEAKER_SPLIT="1",
           VPM_NO_UPDATE_CHECK="1", QT_QPA_PLATFORM="offscreen")


def dry_run(names, files, extra=()):
    """A dry run with these --new-name pairs; (return code, output)."""
    # The fixture's microphones share no sound with its cameras: only the
    # phase way places them, and it is asked only for mixed sound.
    argv = [sys.executable, SCRIPT, "--without-auphonic", "--dry-run",
            "--sound", "mixed", "--out", OUT] + list(extra)
    for file, name in names:
        argv += ["--new-name", file, name]
    kid = subprocess.Popen(argv + files, stdout=subprocess.PIPE,
                           stderr=subprocess.STDOUT, env=ENV)
    pieces = []

    def read():
        for piece in iter(lambda: os.read(kid.stdout.fileno(), 65536), b""):
            pieces.append(piece)

    reader = threading.Thread(target=read, daemon=True)
    reader.start()
    last, seen, stood = time.time(), 0, ""
    while kid.poll() is None:
        time.sleep(0.1)
        if len(pieces) != seen:
            seen, last = len(pieces), time.time()
        if time.time() - last > STILL and not stood:
            stood = "; stood still %.0f s without output and was stopped" % (
                time.time() - last)
            kid.kill()
    kid.wait()
    reader.join(10)
    kid.stdout.close()
    return (kid.returncode, b"".join(pieces).decode("utf-8", "replace"),
            stood)


def aborts(said):
    """The refusal lines the run printed, for the failure line."""
    return [line.strip() for line in said.splitlines()
            if line.startswith(vpm.T('Abort: %s') % "")] or ["none"]


def refused(names, files, reason, extra=()):
    """The run's code, whether it said *reason*, and what it did say."""
    code, said, stood = dry_run(names, files, extra)
    line = vpm.T('Abort: %s') % reason
    return (code == 1 and line in said.splitlines(),
            "rc %s, wanted 1, with %r; the run said %s%s"
            % (code, line, aborts(said), stood))


MEDIA = fixture("interview")
SOUND = sorted(glob.glob(os.path.join(MEDIA, "Guest_*.wav")))[:1]
GUEST = os.path.join(MEDIA, "GuestCam_01011858_C003.mov")
HOST = os.path.join(MEDIA, "PresentersCam_01011855_C002.mov")
WIDE = os.path.join(MEDIA, "WideCam_01011855_C001.mov")
FILES = SOUND + [GUEST, HOST]
g, h = os.path.basename(GUEST), os.path.basename(HOST)

print("1. The fixture")
there = [p for p in (GUEST, HOST, WIDE) if os.path.exists(p)]
check("the fixture holds a recording and three cameras",
      len(SOUND) == 1 and len(there) == 3,
      "%d recording and %d of 3 cameras in the interview fixture -- "
      "'cd tests && bash fixtures.sh' builds them" % (len(SOUND), len(there)))
if len(SOUND) != 1 or len(there) != 3:
    stop()

print("\n2. Two cameras in one file")
ok, why = refused([(GUEST, "Same"), (HOST, "Same")], FILES,
                  vpm.T('Two cameras would be written as one file, %s: '
                        '%s and %s.') % ("Same_audio.mov", g, h))
check("two cameras given one name are refused, both named", ok, why)
ok, why = refused([(GUEST, "Same"), (HOST, "same")], FILES,
                  vpm.T('Two cameras would be written as one file, %s: '
                        '%s and %s.') % ("Same_audio.mov", g, h))
check("two names differing only in case are refused as one file", ok, why)
ok, why = refused([(GUEST, os.path.splitext(h)[0])], FILES,
                  vpm.T('Two cameras would be written as one file, %s: '
                        '%s and %s.')
                  % (os.path.splitext(h)[0] + "_audio.mov", g, h))
check("a name equal to another camera's stem is refused too", ok, why)

print("\n3. A name that is no plain file name")
ok, why = refused([(GUEST, "a/../../Esc")], FILES,
                  vpm.T('The new name "%s" for %s holds "%s", a folder or '
                        'drive separator; give a plain file name.')
                  % ("a/../../Esc", g, "/"))
check("a name with a folder separator is refused, and names it", ok, why)
ok, why = refused([(GUEST, "D:Esc")], FILES,
                  vpm.T('The new name "%s" for %s holds "%s", a folder or '
                        'drive separator; give a plain file name.')
                  % ("D:Esc", g, ":"))
check("a name with a drive colon is refused, and names it", ok, why)
ok, why = refused([(GUEST, "..")], FILES,
                  vpm.T('The new name "%s" for %s begins with a dot, which '
                        'makes a hidden file or a folder; give a plain file '
                        'name.') % ("..", g))
check("a name beginning with a dot is refused, and says so", ok, why)
ok, why = refused([(GUEST, "  ")], FILES,
                  vpm.T('The new name for %s is empty; give a plain file '
                        'name or leave --new-name out.') % g)
check("an empty name is refused, and says so", ok, why)

print("\n4. A file that is no camera of the run")
ok, why = refused([(WIDE, "Wide")], FILES,
                  vpm.T('--new-name names %s, which is not one of the '
                        'camera files of this run.') % os.path.basename(WIDE))
check("a file that is no camera of the run is refused by name", ok, why)

print("\n5. One file given two names")
ok, why = refused([(GUEST, "Guest"), (GUEST, "Presenter")], FILES,
                  vpm.T('--new-name gives %s two names, "%s" and "%s"; '
                        'give each file one.') % (g, "Guest", "Presenter"))
check("one file given two names is refused, both names said", ok, why)

print("\n6. Names that come from elsewhere")
# Two recordings, so that without the refusal the multitrack run would
# go through with the assignment's names and the line would be missing.
TWO = SOUND + sorted(glob.glob(os.path.join(MEDIA, "Presenter_*.wav")))[:1]
ASSIGN = os.path.join(HELD, "assign.json")
with open(ASSIGN, "w", encoding="utf-8") as f:
    json.dump({"format": vpm.FILE_FORMAT, "created_by": "test",
               "production": "P",
               "tracks_of": [{"audio": a, "blocks": [a], "speakers": who,
                              "camera": cam, "camera_audio": False}
                             for a, who, cam in zip(TWO, ("Guest",
                                                          "Presenter"),
                                                    (GUEST, HOST))],
               "cameras": [{"video": GUEST, "name": "GCam"},
                           {"video": HOST, "name": "HCam"}]}, f)
ok, why = refused([(GUEST, "Guest")], TWO + [GUEST, HOST],
                  vpm.T('The assignment file names the cameras here, so '
                        '--new-name would be dropped; give the names there '
                        'or leave --new-name out.'),
                  ["--multitrack", "--assign", ASSIGN])
check("names beside assigned cameras are refused, saying why",
      ok, why)
ok, why = refused([(GUEST, "Guest")], [GUEST, HOST],
                  vpm.T('With cameras only, each file is named after the '
                        'tracks taken from its sound, so --new-name would be '
                        'dropped; leave --new-name out.'), ["--multitrack"])
check("names for cameras alone, named by tracks, are refused", ok, why)

print("\n7. Two distinct names")
code, said, stood = dry_run([(GUEST, "Guest"), (HOST, "Presenter")], FILES)
planned = [line.split() for line in said.splitlines() if "  ->  " in line]
wanted = [[g, "->", "Guest_audio.mov"], [h, "->", "Presenter_audio.mov"]]
check("two distinct names still pass into the plan",
      code == 0 and all(w in planned for w in wanted),
      "rc %s, wanted 0; planned %s, wanted %s among them; refusals %s%s"
      % (code, planned[-3:], wanted, aborts(said), stood))

print("\n8. Beside a separation file")
# It carries voices and the camera each sits on, and no camera names:
# the window sends it beside --new-name, and neither pushes out the other.
VOICES = os.path.join(HELD, "voices.json")
with open(VOICES, "w", encoding="utf-8") as f:
    json.dump({"format": vpm.FILE_FORMAT, "created_by": "test",
               "speakers_of": {"source": SOUND[0],
                               "segments": [["A", 0.0, 5.0],
                                            ["B", 5.0, 10.0]],
                               "names": {"A": "Guest", "B": "Presenter"}},
               "voices_of": {"Guest": GUEST, "Presenter": HOST}}, f)
code, said, stood = dry_run([(GUEST, "Guest"), (HOST, "Presenter")], FILES,
                            ["--speakers-from", VOICES])
planned = [line.split() for line in said.splitlines() if "  ->  " in line]
check("names beside a separation file are not refused, and kept",
      code == 0 and all(w in planned for w in wanted),
      "rc %s, wanted 0; planned %s, wanted %s among them; refusals %s%s"
      % (code, planned[-3:], wanted, aborts(said), stood))
lines = [line.strip() for line in said.splitlines()]
head = vpm.T('\nSPEAKERS -- SEPARATED BY VOICE').strip()
after = lines[lines.index(head) + 1:] if head in lines else []
voices = sorted(line.split()[0] for line in after[:after.index("")]
                if line) if "" in after else []
check("and the separation it names is read beside them",
      voices == ["Guest", "Presenter"],
      "voices read %s, wanted ['Guest', 'Presenter']; %s" % (
          voices, "the voices head was printed" if head in lines
          else "no voices head in the output"))

stop()
