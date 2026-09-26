# -*- coding: utf-8 -*-
"""A hole or an overlap between timecoded blocks is said when they are joined.

Three blocks of ten seconds, each with its start written in the file the
way a recorder writes it: one at zero, one twenty seconds in, which
leaves a ten-second hole, and one nine seconds in, which overlaps the
first by a second. join_with_report joins the first with each of the
others, and what it prints is held to the program's own sentences: the
join by timecode, the hole with its length and place, the overlap as an
overlap and as several microphones at once.
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
import contextlib, io, subprocess, tempfile, time

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


D = tempfile.mkdtemp(prefix="vpm_blockgap_")
# One ffmpeg call writes the three blocks; the start of each is its
# sample count from midnight, as a recorder's bext chunk carries it.
STARTS = {"first": 0, "late": 20 * 48000, "early": 9 * 48000}
build = ["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i",
         "sine=frequency=440:duration=10:sample_rate=48000"]
for name, start in STARTS.items():
    build += ["-map", "0:a", "-c:a", "pcm_s16le", "-write_bext", "1",
              "-metadata", "time_reference=%d" % start,
              os.path.join(D, name + ".wav")]
subprocess.run(build, check=True)


def join(*names):
    """Join the blocks named; hands back what was printed."""
    said = io.StringIO()
    with contextlib.redirect_stdout(said):
        vpm.join_with_report([os.path.join(D, n + ".wav") for n in names],
                             os.path.join(D, "_".join(names) + "_joined.wav"))
    return said.getvalue()


def line(template, *values):
    """The program's sentence with these values, without its indent."""
    return (vpm.T(template) % values).strip()


print("A hole between two blocks")
said = join("first", "late")
told = (vpm.T('  %s blocks joined via timecode, start %s')
        % (vpm.number_text(2, 0), "\0")).split("\0")[0].strip()
check("blocks with timecode are joined by it, and it is said",
      told in said, "%r %s among %d lines"
      % (told, "said" if told in said else "not said", len(said.splitlines())))
gap = line('  Gap of %s at %s -- filled with silence',
           "0:00:10.000", "0:00:10.000")
check("a hole is named with its length and place", gap in said,
      "%r %s; the lines were %s"
      % (gap, "said" if gap in said else "not said",
         [x.strip() for x in said.splitlines()][:4]))

print("\nTwo blocks that overlap")
said = join("first", "early")
over = line('  Overlap of %s at %s -- both sound there',
            "0:00:01.000", "0:00:10.000")
check("an overlap is named as an overlap", over in said,
      "%r %s; the lines were %s"
      % (over, "said" if over in said else "not said",
         [x.strip() for x in said.splitlines()][:4]))
both = line('  They overlap -- several microphones at once, not blocks in '
            'a row.')
check("and as several microphones at once", both in said,
      "%r %s among %d lines"
      % (both, "said" if both in said else "not said", len(said.splitlines())))

print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
