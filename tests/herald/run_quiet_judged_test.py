# -*- coding: utf-8 -*-
"""A quiet run reads as working while something moves, else as stuck.

In order: a child's processor time is read and rises while it works;
then the verdict over stand-in children -- a busy loop, a sleeping
process, a sleeper whose named file grows -- and over a word, the same
line again, a server's answer, a question open, this process busy;
then the line it becomes, and last the line beside the bar. The clock
is a stand-in, so five minutes pass in a second; the children are real.
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
import subprocess, tempfile, time
os.environ["QT_QPA_PLATFORM"] = "offscreen"
from PySide6 import QtCore, QtWidgets
app = QtWidgets.QApplication(sys.argv[:1])
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


FOLDER = tempfile.mkdtemp(prefix="vpm_quiet_")
children = []
clock = [1000.0]
BUSY = "print('ready', flush=True)\nwhile True: pass"
SLEEPY = "import time; print('ready', flush=True); time.sleep(600)"


def child(code, *more):
    """A stand-in child, started and waited for until it says it is up."""
    proc = subprocess.Popen([sys.executable, "-c", code] + list(more),
                            stdout=subprocess.PIPE)
    proc.stdout.readline()
    children.append(proc)
    return proc


def cpu_rose(proc, since, patience=10.0):
    """Wait until the child's time is past *since*, and say what it is."""
    until = time.time() + patience
    now = vpm.cpu_seconds(proc)
    while (now is None or since is None or now <= since) \
            and time.time() < until:
        time.sleep(0.02)
        now = vpm.cpu_seconds(proc)
    return now


def vitals(own=None):
    """A watch on the stand-in clock, begun now."""
    v = vpm.RunVitals(clock=lambda: clock[0], own=own or (lambda: 0.0))
    v.begin()
    return v


def minutes_pass(v, minutes, between=None):
    """Let whole minutes pass on the clock, the signs read after each."""
    for _ in range(minutes):
        if between:
            between()
        clock[0] += 60.0
        v.look()
    return v.verdict()


try:
    print("Reading a child")
    busy = child(BUSY)
    first = vpm.cpu_seconds(busy)
    later = cpu_rose(busy, first)
    check("a busy child's processor time can be read and rises",
          first is not None and later is not None and later > first,
          "read %r, then %r" % (first, later))

    print("\nJudging a quiet run")
    v = vitals()
    v.watch(busy)
    v.look()
    said = minutes_pass(v, 6, lambda: cpu_rose(busy, vpm.cpu_seconds(busy)))
    check("a busy child keeps a quiet run working, not stuck",
          said is not None and said[0] == "working",
          "after 6 minutes without a word: %r" % (said,))

    sleepy = child(SLEEPY)
    v = vitals()
    v.watch(sleepy)
    v.look()
    said = minutes_pass(v, 1)
    check("one quiet minute is no verdict yet", said is None,
          "after 1 minute: %r" % (said,))
    said = minutes_pass(v, 2)
    check("nothing growing is not called working", said is None,
          "after 3 minutes with a sleeping child: %r" % (said,))
    said = minutes_pass(v, 3)
    limit = int(vpm.herald.STUCK_AFTER_S // 60)
    check("a sleeping child with nothing growing is judged stuck",
          said is not None and said[0] == "stuck",
          "after 6 minutes: %r, the limit is %d min" % (said, limit))
    check("the stuck verdict counts the minutes since the last change",
          said is not None and said[1] == 6,
          "after 6 minutes: %r" % (said,))

    v.heard("a new line")
    said = v.verdict()
    check("a new line of output clears the verdict", said is None,
          "after a word: %r" % (said,))

    v = vitals()
    v.watch(sleepy)
    v.look()
    said = minutes_pass(v, 6, lambda: v.heard("the same line"))
    check("the same line again and again is no word",
          said is not None and said[0] == "stuck",
          "after 6 minutes of one line repeated: %r" % (said,))

    grows = os.path.join(FOLDER, "out.wav")
    with open(grows, "wb") as f:
        f.write(b"x")
    writer = child(SLEEPY, grows)

    def grow():
        with open(grows, "ab") as f:
            f.write(b"x" * 100)

    v = vitals()
    v.watch(writer)
    v.look()
    said = minutes_pass(v, 6, grow)
    check("a growing file on the child's command line keeps it working",
          said is not None and said[0] == "working",
          "after 6 minutes with %d bytes in the file: %r"
          % (os.path.getsize(grows), said))

    v = vitals()
    v.watch(sleepy)
    v.look()
    said = minutes_pass(v, 6, v.alive)
    check("an answer from the server counts as life",
          said is not None and said[0] == "working",
          "after 6 minutes of answers and no word: %r" % (said,))

    v = vitals()
    v.watch(sleepy)
    v.look()
    with v.asking():
        said = minutes_pass(v, 10)
    after = v.verdict()
    check("while a person is asked nothing is judged",
          said is None and after is None,
          "during 10 minutes of a question: %r, after it: %r"
          % (said, after))

    spent = [0.0]

    def work():
        spent[0] += 30.0

    v = vitals(own=lambda: spent[0])
    v.look()
    said = minutes_pass(v, 6, work)
    check("this process at half a core counts as life",
          said is not None and said[0] == "working",
          "after 6 minutes at 30 s a minute and no child: %r" % (said,))

    print("\nThe line")
    text, warn = vpm.vitals_line(("stuck", 5))
    check("the stuck line warns and names its minutes",
          warn and vpm.number_text(5, 0) in text,
          "warns %r, says %r" % (warn, text))
    text, warn = vpm.vitals_line(("working", 3))
    check("the working line does not warn",
          not warn and vpm.number_text(3, 0) in text,
          "warns %r, says %r" % (warn, text))

    print("\nBeside the bar")
    # The verdict goes into the log file too, and the log beside the
    # program is not this test's to write into.
    vpm.herald.log_aside = lambda text: None
    vpm.window()    # the bar's line is fitted by the window's own helper
    plan = vpm.ProgressPlan()
    plan.begin("run:cameras", "Writing the camera files")
    bar, line = QtWidgets.QProgressBar(), QtWidgets.QLabel()
    line.resize(900, 20)    # wide enough that nothing is shortened
    watch = vpm.RUN_VITALS
    watch.clock = lambda: clock[0]
    watch.own = lambda: 0.0
    watch.begin()
    watch.watch(sleepy)
    state = {"full_since": 0.0}
    for _ in range(7):
        vpm.total_paint(QtCore.Qt, plan, state, bar, line)
        clock[0] += 60.0
    vpm.total_paint(QtCore.Qt, plan, state, bar, line)
    wanted, _warn = vpm.vitals_line(watch.verdict())
    check("the line beside the bar says a quiet run is stuck",
          bool(wanted) and line.text() == wanted,
          "the line says %r, the verdict %r" % (line.text(), wanted))
    check("and says it in the warning colour",
          vpm.COLOURS["warning"] in line.styleSheet(),
          "style %r, warning is %s" % (line.styleSheet(),
                                       vpm.COLOURS["warning"]))
    watch.end()
except Exception:
    import traceback
    traceback.print_exc()
    bad.append("the test itself broke off")
finally:
    for proc in children:
        proc.kill()
        proc.wait()

print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
