# -*- coding: utf-8 -*-
"""Set-aside files: checked yes, compared no, counted no.

A file that does not take part -- an ignored take, an intro, a colour
chart -- is still measured, so its row is not the only one without a
mark; but it stays out of everything that compares files, and what is
found about it does not count towards the balance line.

The sections: the resolution hint a colour chart makes and loses; that
the set-aside file keeps findings of its own and they all carry the
mark; that a file taking part carries none; that a finding born of the
comparison never carries it; the same for sound, where a short
recording earns a hint only while it takes part; and the balance line,
which a marked finding leaves alone.
"""
import os
import the_program
HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = the_program.SCRIPT
import sys, subprocess, tempfile, time
vpm = the_program.load()

began = time.time()
done = 0
bad = []


def check(name, ok, extra=""):
    global done
    done += 1
    print("  %-58s %s %s" % (name, "ok" if ok else "FAIL", extra))
    if not ok:
        bad.append("%s [%s]" % (name, extra or "no numbers"))


# Its own folder under the run's TMPDIR, which the run throws away: a
# fixed path collides the moment two tests run beside each other.
D = tempfile.mkdtemp(prefix="vpm_set_aside_")


def video(name, size, duration=2):
    p = os.path.join(D, name)
    subprocess.run(["ffmpeg", "-v", "error", "-f", "lavfi",
                    "-i", "testsrc=size=%s:rate=30:duration=%d"
                    % (size, duration),
                    "-c:v", "libx264", "-pix_fmt", "yuv420p", p, "-y"],
                   check=True)
    return p


def sine(name, seconds, hertz):
    # Names without a trailing number on purpose: a trailing number makes
    # the program read the files as blocks of one recording, and then
    # there is nothing left to compare.
    p = os.path.join(D, name)
    subprocess.run(["ffmpeg", "-v", "error", "-f", "lavfi",
                    "-i", "sine=frequency=%d:duration=%d" % (hertz, seconds),
                    p, "-y"], check=True)
    return p


# Two cameras of the same size, plus a colour chart of a quite different one.
cam1 = video("Camera1.mov", "640x360")
cam2 = video("Camera2.mov", "640x360")
chart = video("Colourchart.mov", "320x180")
SIZE_FIELD = vpm.T('Resolutions')

print("1. Without set aside: the colour chart makes a resolution hint")
findings = vpm.collect_findings([], [cam1, cam2, chart], fresh=True)
res = [x for x in findings if x.field == SIZE_FIELD]
check("the odd-sized file makes a hint about resolutions", len(res) == 1,
      "%d such hints among %d findings" % (len(res), len(findings)))

print("\n2. With set aside: no resolution hint any more")
findings = vpm.collect_findings([], [cam1, cam2, chart], fresh=True,
                                set_aside=[chart])
res = [x for x in findings if x.field == SIZE_FIELD]
check("set aside, that file makes no hint about resolutions", not res,
      "%d such hints among %d findings" % (len(res), len(findings)))

print("\n3. The colour chart still has findings of its own")
its = [x for x in findings if x.file == os.path.abspath(chart)]
check("a set-aside file is measured all the same", len(its) >= 1,
      "%d findings about it, %d in all" % (len(its), len(findings)))
unmarked = [x.field for x in its if not x.set_aside]
check("every finding about a set-aside file carries the mark",
      its and not unmarked,
      "%d of %d without the mark: %s" % (len(unmarked), len(its), unmarked))

print("\n4. The cameras are not set aside")
mine = [x for x in findings if x.file == os.path.abspath(cam1)]
check("a file that takes part is measured too", len(mine) >= 1,
      "%d findings about it, %d in all" % (len(mine), len(findings)))
marked = [x.field for x in mine if x.set_aside]
check("no finding about a file that takes part carries the mark",
      mine and not marked,
      "%d of %d marked: %s" % (len(marked), len(mine), marked))

print("\n5. Findings across files are never set aside")
# One camera set aside, and the two left over still differ in size: so
# there is a finding out of the comparison to ask about at all.
findings = vpm.collect_findings([], [cam1, cam2, chart], fresh=True,
                                set_aside=[cam2])
across = [x for x in findings if not x.file]
check("a comparison still speaks while one file is set aside",
      len(across) >= 1,
      "%d findings across files, %d in all" % (len(across), len(findings)))
marked = [x.field for x in across if x.set_aside]
check("no finding across files carries the mark",
      across and not marked,
      "%d of %d marked: %s" % (len(marked), len(across), marked))

print("\n6. Sound: a short recording is compared only while it takes part")
long1 = sine("Anna.wav", 6, 300)
long2 = sine("Ben.wav", 6, 400)
short = sine("Cara.wav", 2, 500)


def about_short(**how):
    got = vpm.collect_findings([long1, long2, short], [], fresh=True,
                               crosstalk=False, **how)
    return [x for x in got if x.file == os.path.abspath(short)]


alone = vpm.collect_findings([short], [], fresh=True, crosstalk=False)
check("a short recording alone earns findings of its own", len(alone) >= 1,
      "%d findings alone" % len(alone))
beside = about_short()
check("beside longer ones it earns a hint from the comparison",
      len(beside) > len(alone),
      "%d findings beside them against %d alone"
      % (len(beside), len(alone)))
aside = about_short(set_aside=[short])
check("set aside it earns no hint from the comparison",
      len(aside) == len(alone),
      "%d findings set aside against %d alone" % (len(aside), len(alone)))
unmarked = [x.field for x in aside if not x.set_aside]
check("every finding about the set-aside recording is marked",
      aside and not unmarked,
      "%d of %d without the mark: %s"
      % (len(unmarked), len(aside), unmarked))

print("\n7. The balance line counts no finding that was set aside")
# Two findings alike but for the mark, held against the same line with
# no finding at all: what the mark is worth is the difference.
note = vpm.Finding("hint", "X", "a note about something")
put_by = vpm.Finding("hint", "X", "a note about something")
put_by.set_aside = True
quiet = vpm.preflight_sentence([], 0, 0, 2)
counted = vpm.preflight_sentence([note], 0, 0, 2)
left_out = vpm.preflight_sentence([put_by], 0, 0, 2)
check("a hint that takes part changes the balance line",
      counted != quiet,
      "%r against %r without it" % (counted[0][-40:], quiet[0][-40:]))
check("a hint about a set-aside file leaves the balance alone",
      left_out == quiet,
      "%r against %r without it" % (left_out[0][-40:], quiet[0][-40:]))

print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
