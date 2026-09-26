# -*- coding: utf-8 -*-
"""A long file name in the preflight keeps its end, cut in the middle.

A name cut at the end loses its extension and the "(2)" that tells two
cameras of one name apart. The rule first, on names alone: one that
fits stands whole, a long one keeps both ends, a wide letter counts two
columns. Then every place that names a file: the facts line of a camera
and of a recording, a camera without picture, a file that could not be
read, the short recording, the second recording in sync, the unset
clock, a block with no timecode and a gap between two, and the camera
colour comparison.
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
import contextlib, io, shutil, subprocess, tempfile, time
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


# Its own folder under the run's TMPDIR, which the run throws away.
D = tempfile.mkdtemp(prefix="vpm_long_names_")
# The shape a cinema camera writes, a role put in front of it: long
# enough for both columns, and the end is what tells takes apart.
CAM = "WideCam_A001C003_260926_R2EJ.mov"
REC = "Presenter_Lavalier_260926_001.WAV"
ELLIPSIS = "…"


def made(name, *source):
    """Write *name* under D from an ffmpeg source, two seconds of it."""
    p = os.path.join(D, name)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    subprocess.run(["ffmpeg", "-v", "error", "-f", "lavfi", "-i",
                    source[0] + ":duration=2"] + list(source[1:])
                   + [p, "-y"], check=True)
    return p


def says(field, whole):
    """Both names for a FAIL line: what was shown, and what it stands for."""
    return "shown %r for %r" % (field, whole)


print("1. The rule, on names alone")
check("a name that fits its column stands whole",
      vpm.name_to_fit("Guest.mov", 24) == "Guest.mov",
      says(vpm.name_to_fit("Guest.mov", 24), "Guest.mov"))
cut = vpm.name_to_fit(CAM, 24)
check("a long name is cut in the middle and keeps its extension",
      cut.startswith("WideCam") and cut.endswith(".mov")
      and ELLIPSIS in cut and len(cut) <= 24,
      says(cut, CAM) + ", %d letters in a column of 24" % len(cut))
# Every letter but the extension is a wide one, so the columns can be
# counted here without asking any table.
WIDE = "ゲ" * 20 + ".mov"
cut = vpm.name_to_fit(WIDE, 24)
columns = 2 * cut.count("ゲ") + len(cut) - cut.count("ゲ")
check("a wide letter takes two of the column's places",
      columns <= 24 and cut.endswith(".mov"),
      says(cut, WIDE) + ", %d columns in a column of 24" % columns)

print("\n2. The two cameras of one long name, through the check")
first = made(os.path.join("cardA", CAM), "testsrc=size=160x90:rate=25")
second = made(os.path.join("cardB", CAM), "smptebars=size=160x90:rate=25")
labels = vpm.camera_labels([first, second])
findings = vpm.collect_findings([], [first, second], fresh=True,
                                crosstalk=False, labels=labels)
facts = dict((b.file, b.field) for b in findings if b.kind == "good")
one, two = facts.get(first, ""), facts.get(second, "")
check("a long camera name keeps its extension in the facts line",
      one.endswith(".mov") and ELLIPSIS in one,
      says(one, labels.get(first)))
check("the second of two long same-named cameras keeps its (2)",
      two.endswith("(2)") and one != two,
      says(two, labels.get(second)) + ", the first " + says(one, CAM))

print("\n3. The other places that name a file")
blind = made(os.path.join("cardC", CAM), "sine=frequency=440")
got = [b.field for b in vpm.check_camera_file(blind)[0]]
check("a camera with no picture keeps its extension in the note",
      bool(got) and got[0].endswith(".mov") and ELLIPSIS in got[0],
      says(got[0] if got else "no finding", CAM))


def unreadable(_path):
    """A measurement that cannot read the file, as a broken one."""
    raise OSError("stands in for a file that cannot be read")


got = [b.field for b in vpm.measure_cached(first, "long_names",
                                           unreadable, fresh=True)[0]]
check("a file that cannot be read keeps its extension in the note",
      bool(got) and got[0].endswith(".mov") and ELLIPSIS in got[0],
      says(got[0] if got else "no finding", CAM))
voice = made(os.path.join("rec", REC), "sine=frequency=220")
got = [b.field for b in vpm.check_audio_file(voice)[0]
       if b.kind == "good"]
check("a long recording keeps its extension in the facts line",
      bool(got) and got[0].endswith(".WAV") and ELLIPSIS in got[0],
      says(got[0] if got else "no finding", REC))
got = [b.field for b in vpm.compare_audio_tracks(
    [{"name": REC, "duration": 10.0, "path": voice},
     {"name": "Guest.wav", "duration": 100.0, "path": ""}])]
check("a short recording keeps its extension in the note",
      bool(got) and got[0].endswith(".WAV") and ELLIPSIS in got[0],
      says(got[0] if got else "no finding", REC))
got = [b.field for b in vpm.one_recording_only(
    [([os.path.join(D, "Guest.wav")], []), ([voice], [])])]
check("the recording past the first in sync keeps its extension",
      bool(got) and got[0].endswith(".WAV") and ELLIPSIS in got[0],
      says(got[0] if got else "no finding", REC))
# Two files an hour into the day and one at ten: the third overlaps
# neither, so its clock was never set.
got = [b.field for b in vpm.timecode_comparison(
    [{"name": "Guest.wav", "tc": 3600.0, "duration": 60.0},
     {"name": "Presenter.wav", "tc": 3610.0, "duration": 60.0},
     {"name": CAM, "tc": 36000.0, "duration": 60.0, "nominal": 25.0}])]
check("a file with an unset clock keeps its extension in the note",
      bool(got) and got[0].endswith(".mov") and ELLIPSIS in got[0],
      says(got[0] if got else "no finding", CAM))
# Two blocks of one camera with no timecode: the note names the part of
# the name they share, and its end is what tells two cameras apart.
BLOCK = "WideCam_A001C003_260926_R2EJ_%04d.mov"
blocks = [os.path.join(D, "cardD", BLOCK % n) for n in (1, 2)]
os.makedirs(os.path.dirname(blocks[0]))
for p in blocks:
    shutil.copyfile(first, p)
got = [b.field for b in vpm.find_camera_gaps(blocks)]
check("a block with no timecode keeps the end of its shared name",
      bool(got) and got[0].endswith("R2EJ_") and ELLIPSIS in got[0],
      says(got[0] if got else "no finding", BLOCK % 1))
# The same two blocks with a clock: the second starts eight seconds
# after the first two-second block ended, so the camera stopped.
timed = [made(os.path.join("cardE", BLOCK % n),
              "testsrc=size=160x90:rate=25", "-timecode", start)
         for n, start in ((1, "01:00:00:00"), (2, "01:00:10:00"))]
# Only the note on the gap counts, not the one on a missing clock.
blind_clock = vpm.T('multi-part, no timecode -- gaps in between cannot '
                    'be detected.')
got = [b.field for b in vpm.find_camera_gaps(timed)
       if b.text != blind_clock]
check("a gap between blocks keeps the end of their shared name",
      bool(got) and got[0].endswith("R2EJ_") and ELLIPSIS in got[0],
      says(got[0] if got else "no note on a gap", BLOCK % 1))
said = io.StringIO()
with contextlib.redirect_stdout(said):
    vpm.report_picture_comparison([{"file": first, "track": labels[first]},
                                   {"file": second,
                                    "track": labels[second]}])
rows = [x for x in said.getvalue().splitlines() if x.startswith("  Wide")]
check("the colour comparison keeps both long cameras' ends",
      len(rows) == 2 and rows[0].split()[0].endswith(".mov")
      and rows[1].split()[1] == "(2)",
      "%d rows for %r and %r: %r" % (len(rows), labels[first],
                                     labels[second], rows))

shutil.rmtree(D, ignore_errors=True)
print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
