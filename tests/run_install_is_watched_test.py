# -*- coding: utf-8 -*-
"""Installing ffmpeg shows what it is doing while it does it.

Before this the package manager ran in the window's own thread with
its output going nowhere anybody could see, so a minute of fetching
looked like a program that had hung.

Sections: what a watched command hands out, and when; that the process
is handed out so it can be reached; that a command which cannot start
says so instead of pretending a code; that without a sink nothing is
piped, which is what leaves a password prompt on the terminal; that a
test run installs nothing; that the manager's lines and the program's
own go the same way and carry their newline; that the job says
beforehand what it is, hands every line to the Output tab and into
the log, and ends by saying what has to happen next; that a job which
failed hands back a sentence instead of that promise; and that the
button in the ffmpeg box leads there rather than to a hidden run, ends
nothing while it goes, and falls back to the old way where there is no
window to show it in. Then the long silence in the middle of a build:
that the line a manager goes quiet under is told from the ones it
races past, that the sentence explaining the wait hangs on that line
and is said once, and that a dot keeps coming while nothing else does.
Last, that what has to happen afterwards is offered in a box rather
than laid down as the last of two hundred lines.

No package manager is ever really called. The command is replaced by a
harmless one that prints, waits and prints again -- so what is
measured is the plumbing, not the weather on a mirror. Windows has no
manager to watch and leaves the three sections about one out.

From the fifth section on, VPM_SILENT has to come off, or the manager
is never reached at all -- and that takes the guard off the fetch
beside it. So while it is off, the road out is shut at the socket,
where every road out ends, and the last check of the failed job says
how many addresses were opened all the same. The failed job itself is
driven onto Linux: only there does the program have a second door.
"""
import io
import os
import re
import shutil
import socket
import subprocess
import sys
import tempfile
import time
import the_program

os.environ["QT_QPA_PLATFORM"] = "offscreen"
from PySide6 import QtCore, QtGui, QtWidgets

app = QtWidgets.QApplication(sys.argv[:1])
vpm = the_program.load()
vpm.set_language("en")

began = time.time()
done = 0
bad = []
left_out = []


def check(name, ok, extra=""):
    global done
    done += 1
    print("  %-58s %s %s" % (name, "ok" if ok else "FAIL", extra))
    if not ok:
        bad.append("%s [%s]" % (name, extra or "no numbers"))


# Prints, waits, prints again, and puts one line on the error channel.
# The wait is what tells a stream from a collection: a line that
# arrives before the end can only have come out while it was running.
SLOW = [sys.executable, "-c",
        "import sys, time;"
        "print('first');sys.stdout.flush();"
        "sys.stderr.write('aside\\n');sys.stderr.flush();"
        "time.sleep(0.6);print('last')"]
NEVER = [os.path.join(os.path.dirname(os.path.abspath(__file__)),
                      "no such command at all")]

# Somewhere for a fetched build to land that is not the home folder of
# whoever ran the suite. Without VPM_SILENT the program is given a real
# one, and on the builder that is a hundred and fifty megabytes left
# behind by a test.
ROOM = tempfile.mkdtemp(prefix="vpm_toolsroom_")
outward = []


def no_fetch(url, where, say=None):
    """The one place in the program that opens a connection, replaced.

    Its own docstring asks for this: a test replaces this function and
    then measures what the program does with the answer, instead of
    measuring the weather on a mirror.
    """
    return "the test fetched nothing"


def shut(address):
    """No address is reached from here, and the attempt is written down.

    The two callers hand their arguments over differently -- connect
    arrives as a method with its socket first, create_connection with
    the address first and a timeout behind it -- so each has a line of
    its own below and only the address arrives here.
    """
    outward.append(address)
    raise OSError("this test opens no connection")


class Unguarded(object):
    """VPM_SILENT off, and every road out shut in its place.

    The two belong together. VPM_SILENT is the one switch over two
    different things -- no package manager, and no network -- so a
    section that has to reach the manager takes the guard off the
    fetch as well. On 4.9.2026 that fetched a real ffmpeg on the Linux
    builder and turned the last section green in the wrong direction.

    Shut at the socket rather than at a list of the program's own
    functions: a list is one rebuild away from being the wrong list,
    and it goes wrong silently. What is left over is the second shape
    of going outside, an address handed to the desktop's own browser,
    and the program has one named door for that too.
    """

    def __enter__(self):
        self.was = (os.environ.pop("VPM_SILENT", None),
                    socket.socket.connect, socket.create_connection,
                    vpm.fetch_archive, vpm.tools_folder, vpm.open_page)
        socket.socket.connect = lambda one, address, *rest: shut(address)
        socket.create_connection = lambda address, *rest, **more: \
            shut(address)
        vpm.fetch_archive = no_fetch
        vpm.tools_folder = lambda make=False: ROOM
        vpm.open_page = lambda url: outward.append(url) or False
        return self

    def __exit__(self, *trouble):
        (was_silent, socket.socket.connect, socket.create_connection,
         vpm.fetch_archive, vpm.tools_folder, vpm.open_page) = self.was
        if was_silent is not None:
            os.environ["VPM_SILENT"] = was_silent


def waited(ready, sign, bound=90.0, still=20.0):
    """Turn the wheel until *ready*, and give up when *sign* stops moving.

    Standstill rather than a deadline: the builder is the slower
    machine and must not be punished for it, and a thing that hangs
    while there is still time left is caught this way and not by a
    clock.
    """
    started_at = last = time.time()
    mark = sign()
    while not ready():
        app.processEvents()
        now = sign()
        if now != mark:
            mark, last = now, time.time()
        if time.time() - last > still or time.time() - started_at > bound:
            return False
        time.sleep(0.01)
    return True


print("\n1. A watched command is heard while it runs")
lines = []
at = []


def note(text):
    lines.append(text)
    at.append(time.time())


code = vpm.run_watched(SLOW, None, note)
over = time.time()
check("a watched command hands back its exit code", code == 0,
      "code %r" % (code,))
check("both channels come out of the one stream, newline and all",
      sorted(x for x in lines if x in ("first\n", "aside\n", "last\n"))
      == ["aside\n", "first\n", "last\n"],
      "lines %r" % (lines[:6],))
check("the first line arrives before the command is over",
      bool(at) and over - at[0] > 0.4,
      "first line %.2f s before the end, the wait in it is 0.60 s"
      % ((over - at[0]) if at else -1.0))

print("\n2. It can be ended, and it says when it cannot start")
child = []
stopped = []


def kill_it(one):
    child.append(one)
    one.terminate()


code = vpm.run_watched(SLOW, None, stopped.append, kill_it)
check("the process is handed out to whoever asked", len(child) == 1,
      "%d processes handed over" % len(child))
check("ending it ends the run", code not in (0, None),
      "code %r after terminate" % (code,))
said = []
code = vpm.run_watched(NEVER, None, said.append)
check("a command that cannot start returns no exit code", code is None,
      "code %r for %s" % (code, os.path.basename(NEVER[0])))
check("and it says what went wrong", len(said) == 1 and said[0].strip(),
      "said %r" % (said[:2],))

print("\n3. Without a sink nothing is piped")
# The password prompt of sudo carries no newline. Behind a pipe it
# would sit in a buffer while the terminal waits, so a run nobody is
# watching keeps the descriptors it was started with.
quiet = []
vpm.run_watched([sys.executable, "-c", "pass"], None, None, quiet.append)
check("a command nobody watches keeps this run's descriptors",
      len(quiet) == 1 and quiet[0].stdout is None,
      "%d processes, stdout %r"
      % (len(quiet), quiet[0].stdout if quiet else "none"))

print("\n4. A test run installs nothing and asks nobody")
asked = []
was_command = vpm.package_manager_command
vpm.package_manager_command = lambda update=False: tuple(SLOW)
try:
    ran = vpm.install_over_package_manager(asked=True, say=asked.append)
finally:
    vpm.package_manager_command = was_command
check("under VPM_SILENT nothing is installed",
      bool(os.environ.get("VPM_SILENT")) and ran is False and not asked,
      "VPM_SILENT %r, answer %r, %d lines"
      % (os.environ.get("VPM_SILENT"), ran, len(asked)))

print("\n5. The line and the manager's output go the same way")
if sys.platform == "win32":
    # Windows has no manager to run: that branch offers a download page
    # instead, and there is nothing to watch. The two sections below
    # would measure nothing there.
    left_out.append("no package manager on Windows")
    print("LEFT OUT: sections 5 to 7 -- Windows installs from a page, "
          "there is no manager to watch")
else:
    heard = []
    with Unguarded():
        vpm.package_manager_command = lambda update=False: tuple(SLOW)
        try:
            ran = vpm.install_over_package_manager(asked=True,
                                                   say=heard.append)
        finally:
            vpm.package_manager_command = was_command
    check("the install reports that it worked", ran is True,
          "answer %r, %d lines" % (ran, len(heard)))
    check("the program's own line went to the sink",
          any(vpm.T('  Installing it: %s').split("%s")[0].strip() in x
              for x in heard),
          "lines %r" % (heard[:3],))
    check("and so did the command's output",
          "first\n" in heard and "last\n" in heard,
          "lines %r" % (heard[:6],))
    check("every line carries the newline the pane breaks on",
          bool(heard) and all(x.endswith("\n") for x in heard),
          "%d of %d lines end in a newline"
          % (len([x for x in heard if x.endswith("\n")]), len(heard)))

    print("\n6. The whole job, with its lines going where somebody sees")
    shown = []
    log_here = os.path.join(tempfile.mkdtemp(prefix="vpm_watched_"),
                            "videopodcast-magic.log")
    was_log = vpm.log_path
    with Unguarded():
        vpm.package_manager_command = lambda update=False: tuple(SLOW)
        vpm.log_path = lambda: log_here
        del vpm._LOG_ASIDE[:]
        try:
            trouble = vpm.install_job(False, shown.append)
        finally:
            vpm.package_manager_command = was_command
            vpm.log_path = was_log
            del vpm._LOG_ASIDE[:]
    whole = "".join(shown)
    check("a job that worked reports no trouble", trouble == "",
          "trouble %r, %d lines" % (trouble, len(shown)))
    check("it says beforehand what pressing the button meant",
          vpm.T('This takes a few minutes -- a package manager may '
                'build from source. What it says appears here.') in whole,
          "%d characters, first of them %r" % (len(whole), whole[:70]))
    # find, not index: a notice that is not there at all has to come
    # back as a number and not as a raised error, or the checks behind
    # this one say nothing.
    notice_at = whole.find(vpm.T(
        'This takes a few minutes -- a package manager may build from '
        'source. What it says appears here.'))
    first_at = whole.find("first")
    check("the announcement stands before the command's first line",
          notice_at >= 0 and first_at > notice_at,
          "notice at %d, the command's first line at %d"
          % (notice_at, first_at))
    check("what the command said goes to the window", "last\n" in shown,
          "%d lines, %r" % (len(shown), shown[-3:]))
    check("and the last word says what has to happen now",
          vpm.T('Start the program again to pick it up.') in whole,
          "%r among %d characters"
          % (vpm.T('Start the program again to pick it up.'), len(whole)))
    kept = (io.open(log_here, encoding="utf-8").read()
            if os.path.isfile(log_here) else "")
    # The pane is gone when the window goes, and the file is where
    # somebody is sent afterwards -- so the two have to agree.
    check("the same lines stand in the log beside it",
          "first" in kept and "last" in kept
          and vpm.T('Start the program again to pick it up.') in kept,
          "%d characters in %s" % (len(kept), os.path.basename(log_here)))

    print("\n7. A job that failed hands back what to do about it")
    # Driven onto Linux, and that is the point of the section rather
    # than a detail of it: there the manager is the first of two doors
    # and a built ffmpeg is the second, so an install has only failed
    # when both have. A Mac has no second door, and the section would
    # measure the easier half of the case and pass it off as the whole.
    failed = []
    was_where = (vpm.sys.platform, vpm.platform.machine)
    with Unguarded():
        vpm.package_manager_command = lambda update=False: (
            sys.executable, "-c", "raise SystemExit(3)")
        vpm.sys.platform = "linux"
        vpm.platform.machine = lambda: "x86_64"
        try:
            trouble = vpm.install_job(False, failed.append)
        finally:
            vpm.package_manager_command = was_command
            vpm.sys.platform, vpm.platform.machine = was_where
    check("an install that failed comes back with a sentence, not silence",
          trouble.startswith(vpm.T(
              'Nothing runs until that is put right. This way: %s')
              .split("%s")[0]),
          "trouble %r" % (trouble[:80],))
    check("and it does not claim the program can be started again",
          vpm.T('Start the program again to pick it up.')
          not in "".join(failed),
          "%d lines, %r" % (len(failed), "".join(failed)[-60:]))
    # The three sections above are the only ones without VPM_SILENT,
    # and this is what says so afterwards. It is counted at the socket
    # and not at a list of functions, so a road that grows a second
    # door tomorrow lands here loudly instead of downloading.
    check("no section of this test opens a connection to the network",
          not outward,
          "%d addresses opened, wanted 0: %s -- the package manager is "
          "not the only door out of install_ffmpeg"
          % (len(outward), outward[:2]))

print("\n8. The button in the box leads to the watched install")
# The box is answered here rather than by a person: exec returns at
# once and the button it reports pressed is the one that gets ffmpeg.
was_exec = QtWidgets.QMessageBox.exec
was_clicked = QtWidgets.QMessageBox.clickedButton
was_install = vpm.install_watched
was_manager = vpm.install_over_package_manager
was_trouble = vpm.TOOL_TROUBLE
led = []
quit_asked = []


class NoQuit(object):
    """Stands in for the application, so nothing really ends here."""

    def quit(self):
        quit_asked.append(True)


try:
    QtWidgets.QMessageBox.exec = lambda self: 0
    QtWidgets.QMessageBox.clickedButton = lambda self: self.buttons()[0]
    vpm.install_watched = lambda w, a, update: (led.append(update), True)[1]
    vpm.package_manager_command = lambda update=False: tuple(SLOW)
    vpm.TOOL_TROUBLE = ("missing", "ffmpeg is missing.")
    vpm.tools_offer(QtWidgets.QWidget(), NoQuit())
finally:
    QtWidgets.QMessageBox.exec = was_exec
    QtWidgets.QMessageBox.clickedButton = was_clicked
    vpm.install_watched = was_install
    vpm.package_manager_command = was_command
    vpm.TOOL_TROUBLE = was_trouble
check("pressing the button in the box opens the watched install",
      led == [False], "%r handed over" % (led,))
check("and nothing is ended while that install is still going",
      quit_asked == [], "%d requests to quit" % len(quit_asked))

# And where there is no window to show it in, the old way: the install
# runs as it ran before, and the run ends behind it.
was_sink = vpm.UPDATE_SINK
plain = []
del led[:]
try:
    QtWidgets.QMessageBox.exec = lambda self: 0
    QtWidgets.QMessageBox.clickedButton = lambda self: self.buttons()[0]
    vpm.UPDATE_SINK = None
    vpm.install_over_package_manager = lambda **k: plain.append(k) or False
    vpm.package_manager_command = lambda update=False: tuple(SLOW)
    vpm.TOOL_TROUBLE = ("missing", "ffmpeg is missing.")
    vpm.tools_offer(QtWidgets.QWidget(), NoQuit())
finally:
    QtWidgets.QMessageBox.exec = was_exec
    QtWidgets.QMessageBox.clickedButton = was_clicked
    vpm.UPDATE_SINK = was_sink
    vpm.install_over_package_manager = was_manager
    vpm.package_manager_command = was_command
    vpm.TOOL_TROUBLE = was_trouble
check("with no window to show it in the old way is still taken",
      len(plain) == 1 and quit_asked == [True],
      "%d installs run the old way, %d requests to quit"
      % (len(plain), len(quit_asked)))

print("\n9. The line a package manager goes quiet under is known")
check("a build command is what a manager says before it goes quiet",
      vpm.build_begins("==> ./configure --enable-shared --cc=clang"),
      "read %r as the start of a build: %r"
      % ("==> ./configure",
         vpm.build_begins("==> ./configure --enable-shared --cc=clang")))
check("fetching is not taken for the start of a build",
      not vpm.build_begins("==> Fetching downloads for: ffmpeg"),
      "read %r as a build: %r"
      % ("==> Fetching downloads for: ffmpeg",
         vpm.build_begins("==> Fetching downloads for: ffmpeg")))
check("nor is a bottle that is poured in seconds",
      not vpm.build_begins("==> Pouring ffmpeg--9.0.1.bottle.tar.gz"),
      "read %r as a build: %r"
      % ("==> Pouring ffmpeg--9.0.1.bottle.tar.gz",
         vpm.build_begins("==> Pouring ffmpeg--9.0.1.bottle.tar.gz")))

print("\n10. A build that says nothing still moves, and says why")
# A stand-in for a manager that compiles: it names what it is about to
# build and then goes quiet, which is what brew does -- the build's own
# output goes into a log file and nothing is printed until it is over.
BUILDING = [sys.executable, "-c",
            "import sys, time;"
            "print('==> Fetching downloads for: ffmpeg');"
            "print('==> ./configure --enable-shared');sys.stdout.flush();"
            "time.sleep(1.2);print('==> make install')"]
saw = []
PATIENCE = vpm.T('Now it is being compiled, and that is the long part: '
                 'minutes on a fast machine and a good deal longer on an '
                 'older one. Nothing is stuck -- a dot appears every few '
                 'seconds for as long as it works.')


def heard(text):
    """The window's line sink, the way install_job builds it."""
    saw.append(text if text.endswith("\n") else text + "\n")


eye, halt = vpm.sign_of_life(heard, saw.append, every=0.25)
vpm.run_watched(BUILDING, None, eye)
halt()
stream = "".join(saw)
at_build = stream.find("==> ./configure")
at_note = stream.find(PATIENCE)
check("the patience sentence stands under the build line, not above it",
      at_build >= 0 and at_note > at_build,
      "build line at %d, sentence at %d" % (at_build, at_note))
check("it is said once, however many build steps follow",
      stream.count(PATIENCE) == 1 and stream.count("==> ") == 3,
      "%d sentences for %d lines beginning ==> "
      % (stream.count(PATIENCE), stream.count("==> ")))
check("something moves while the manager says nothing",
      saw.count(".") >= 2,
      "%d dots in %.1f s of silence, wanted 2 or more"
      % (saw.count("."), 1.2))
last_dot = max([i for i, x in enumerate(saw) if x == "."] or [-1])
check("the row of dots ends before the next line the manager says",
      last_dot >= 0 and saw[last_dot + 1:last_dot + 2] == ["\n"],
      "after the last dot at %d came %r"
      % (last_dot, saw[last_dot + 1:last_dot + 2]))
check("what the manager said arrives beside the dots",
      "==> make install\n" in saw,
      "%d pieces, the last of them %r" % (len(saw), saw[-2:]))

print("\n11. The restart is offered in a box, not lost in the pane")
# The box is answered here rather than by a person, and the program is
# not really started again: what is measured is which button leads
# where, and that the box comes up at all.
was_exec = QtWidgets.QMessageBox.exec
was_clicked = QtWidgets.QMessageBox.clickedButton
was_warning = QtWidgets.QMessageBox.warning
was_again = vpm.start_again
was_job = vpm.install_job
was_offer = vpm.restart_offer
was_sink_two = vpm.UPDATE_SINK
was_log = vpm.log_path
boxes, warned, restarts, offers, jobs = [], [], [], [], []
window = QtWidgets.QWidget()
log_aside_here = os.path.join(tempfile.mkdtemp(prefix="vpm_restart_"),
                              "videopodcast-magic.log")
try:
    QtWidgets.QMessageBox.exec = lambda self: boxes.append(self.text()) or 0
    QtWidgets.QMessageBox.warning = \
        lambda parent, title, text: warned.append(text)
    vpm.start_again = lambda: restarts.append(True)
    vpm.log_path = lambda: log_aside_here
    del vpm._LOG_ASIDE[:]
    with Unguarded():
        QtWidgets.QMessageBox.clickedButton = lambda self: self.buttons()[0]
        took = vpm.restart_offer(window)
        QtWidgets.QMessageBox.clickedButton = lambda self: self.buttons()[1]
        later = vpm.restart_offer(window)
    silent = vpm.restart_offer(window)
finally:
    QtWidgets.QMessageBox.exec = was_exec
    QtWidgets.QMessageBox.clickedButton = was_clicked
    QtWidgets.QMessageBox.warning = was_warning
    vpm.start_again = was_again
    vpm.log_path = was_log
    del vpm._LOG_ASIDE[:]
check("a box is what says ffmpeg arrived",
      boxes[:1] == [vpm.T('ffmpeg is in place.')],
      "%d boxes, the first saying %r" % (len(boxes), boxes[:1]))
check("the button in it starts the program again",
      took is True and restarts == [True],
      "answer %r, %d restarts asked for" % (took, len(restarts)))
check("answering Later starts nothing",
      later is False and len(restarts) == 1,
      "answer %r, %d restarts asked for" % (later, len(restarts)))
check("a restart that did not work says so in a box, not in a line",
      len(warned) == 1 and vpm.T('Starting again did not work. Close '
                                 'the window and start the program the '
                                 'way you did before.') in warned,
      "%d warnings, %r" % (len(warned), warned[:1]))
check("a test run is offered no box",
      silent is False and len(boxes) == 2,
      "under VPM_SILENT %r the answer was %r and %d boxes stood"
      % (os.environ.get("VPM_SILENT"), silent, len(boxes)))

try:
    vpm.restart_offer = lambda w: offers.append(True) or True
    ticker = vpm.restart_when_done(window, ["the install went wrong"])
    waited(lambda: not ticker.isActive(),
           lambda: (ticker.isActive(), len(offers)), bound=20.0, still=5.0)
    check("an install that ended badly offers no restart",
          offers == [] and not ticker.isActive(),
          "%d boxes offered, the timer still turning: %r"
          % (len(offers), ticker.isActive()))
    vpm.install_job = lambda update, say: ""
    vpm.UPDATE_SINK = lambda job: jobs.append(job)
    armed = vpm.install_watched(QtWidgets.QWidget(), None, False)
    jobs[0](lambda text: None)
    waited(lambda: bool(offers),
           lambda: (len(jobs), len(offers)), bound=20.0, still=5.0)
    check("the box comes up by itself once the install has ended",
          armed is True and offers == [True],
          "%d jobs handed to the sink, answer %r, %d boxes offered"
          % (len(jobs), armed, len(offers)))
finally:
    vpm.restart_offer = was_offer
    vpm.install_job = was_job
    vpm.UPDATE_SINK = was_sink_two
    shutil.rmtree(os.path.dirname(log_aside_here), ignore_errors=True)

shutil.rmtree(ROOM, ignore_errors=True)

print("\n%d checks in %.2f s" % (done, time.time() - began))
if left_out:
    print("Good as far as it went -- 8 of 11 sections: %s"
          % "; ".join(left_out))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
