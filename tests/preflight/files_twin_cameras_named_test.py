# -*- coding: utf-8 -*-
"""Two copies of one camera file are named once, as a note, never stopped.

One recording added twice looks like two cameras to everything after
the preflight, so the preflight says it once. Three real files through
collect_findings: a recording, a byte copy of it, and a second
recording in a codec that writes every frame at one size, so that size
and length agree as well; then two such recordings over two MiB that
differ only towards the end. The limit: only the first and last MiB are
compared, so recordings that differ only between them are named too.
"""
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
import shutil, subprocess, tempfile, time
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
D = tempfile.mkdtemp(prefix="vpm_twin_cameras_")


def video(name, *parts):
    """*parts* one after the other in DNxHR, written as *name* in D.

    Each part is a picture source and its seconds. DNxHR gives every
    frame the same number of bytes, so two different pictures of one
    length come out at one size.
    """
    p = os.path.join(D, name)
    graph = "".join("%s=size=256x144:rate=30:duration=%d[p%d];"
                    % (source, seconds, i)
                    for i, (source, seconds) in enumerate(parts))
    graph += "".join("[p%d]" % i for i in range(len(parts)))
    subprocess.run(["ffmpeg", "-v", "error", "-filter_complex",
                    graph + "concat=n=%d:v=1" % len(parts),
                    "-c:v", "dnxhd", "-profile:v", "dnxhr_lb",
                    "-pix_fmt", "yuv422p", p, "-y"], check=True)
    return p


# Names without a trailing number: that would make them blocks of one
# recording. The copy is made by copying, so its bytes are the same.
guest = video("Guest.mov", ("testsrc", 2))
presenter = os.path.join(D, "Presenter.mov")
shutil.copyfile(guest, presenter)
wide = video("WideCam.mov", ("smptebars", 2))
FIELD = vpm.T('Cameras')

print("1. Two copies of one recording beside a second recording")
findings = vpm.collect_findings([], [guest, presenter, wide], fresh=True)
twins = [x for x in findings if x.field == FIELD]
check("the two copies are named in one hint",
      len(twins) == 1 and twins[0].kind == "hint"
      and "Guest.mov" in twins[0].text and "Presenter.mov" in twins[0].text,
      "%d such findings: %s" % (len(twins), [(x.kind, x.text) for x in twins]))
# Of one size, or the check below would hold for the size alone; the
# sizes stand in the line either way.
sizes = (os.path.getsize(guest), os.path.getsize(wide))
check("and a recording alike only in size and length is not in it",
      bool(twins) and "WideCam.mov" not in twins[0].text
      and sizes[0] == sizes[1],
      "%r, sizes %d and %d bytes"
      % (twins[0].text if twins else "no such finding at all",
         sizes[0], sizes[1]))
stops = [(x.field, x.text) for x in findings if x.kind == "abort"]
check("nothing about the material stops the run", not stops,
      "%d reasons to stop: %s" % (len(stops), stops))

print("\n2. Two recordings over two MiB, alike until past the first")
# Six seconds of one picture, then six of one each: the first MiB is the
# same in both, and only the last one tells them apart.
os.makedirs(os.path.join(D, "second"))
early = video(os.path.join("second", "Guest.mov"),
              ("testsrc", 6), ("testsrc", 6))
late = video(os.path.join("second", "Presenter.mov"),
             ("testsrc", 6), ("smptebars", 6))
with open(early, "rb") as a, open(late, "rb") as b:
    first_alike = a.read(1 << 20) == b.read(1 << 20)
sizes = (os.path.getsize(early), os.path.getsize(late))
findings = vpm.collect_findings([], [early, late], fresh=True)
twins = [x.text for x in findings if x.field == FIELD]
check("recordings that differ only towards the end are not named",
      not twins and first_alike and sizes[0] == sizes[1] > 2 << 20,
      "%d such findings: %s; first MiB alike %s, sizes %d and %d bytes"
      % (len(twins), twins, first_alike, sizes[0], sizes[1]))

shutil.rmtree(D, ignore_errors=True)
print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
