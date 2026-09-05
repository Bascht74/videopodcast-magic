# -*- coding: utf-8 -*-
"""An update that went through says so, and offers the restart.

pip runs beside the window and writes into the Output tab, so the
window that asked keeps running the old version with nothing said. The
sections: that a box comes up by itself once pip is done, that it names
the version that arrived and is not the one ffmpeg's install puts up,
that the window's own way of running a long job is handed back
afterwards, and that the Update button leads to this road at all.

No pip is ever really started and nothing goes out: the look for a
newer version and pip itself are both replaced, and the one door to
the network is shut at the top of the file. What the box does with the
two buttons in it is not measured here -- that is the ffmpeg install's
test, and the box is the same box.
"""
import os
import sys
import time
import urllib.request

import the_program


def no_network(url, *rest, **more):
    """Refuse every look, so nothing here can depend on the weather."""
    raise IOError("this test asks github.com nothing")


urllib.request.urlopen = no_network

os.environ["QT_QPA_PLATFORM"] = "offscreen"
from PySide6 import QtWidgets

app = QtWidgets.QApplication(sys.argv[:1])
vpm = the_program.load()
vpm.set_language("en")

began = time.time()
done = 0
bad = []

# A version that cannot be the one running, and a folder shaped like
# the one a package manager installs into.
TAG = "v99.9.9"
OWNER = os.path.join("usr", "local", "lib", "python3.14", "site-packages")


def check(name, ok, extra=""):
    global done
    done += 1
    print("  %-58s %s %s" % (name, "ok" if ok else "FAIL", extra))
    if not ok:
        bad.append("%s [%s]" % (name, extra or "no numbers"))


def waited(ready, sign, bound=60.0, still=15.0):
    """Turn the wheel until *ready*, and give up when *sign* stops moving.

    Standstill rather than a deadline: the builder is the slower
    machine and must not be punished for being slow, while a thing
    that hangs with time still on the clock is caught all the same.
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


print("\n1. Once pip is done, the window says so by itself")
was_offer = vpm.restart_offer
was_pip = vpm.pip_update
was_sink = vpm.UPDATE_SINK
offers, jobs = [], []
window = QtWidgets.QWidget()


def hand_over(job):
    """The window's sink, stood in: keep the job rather than run it."""
    jobs.append(job)


try:
    vpm.restart_offer = lambda w, said: offers.append(said) or True
    vpm.pip_update = lambda tag, say: ""
    vpm.UPDATE_SINK = hand_over
    answer = vpm.update_watched(window, TAG, OWNER)
    sink_after = vpm.UPDATE_SINK
    if jobs:
        jobs[0](lambda text: None)
    arrived = waited(lambda: bool(offers),
                     lambda: (len(jobs), len(offers)))
finally:
    vpm.restart_offer = was_offer
    vpm.pip_update = was_pip
    vpm.UPDATE_SINK = was_sink
check("an update pip has finished with is not passed over in silence",
      answer == "" and len(jobs) == 1 and offers != [],
      "update_watched said %r, handed the window %d jobs and %d boxes "
      "came up in %s" % (answer, len(jobs), len(offers), arrived))
said = offers[0] if offers else ("", "", "")
check("the box that comes up then names the version that arrived",
      TAG in "\n".join(said),
      "the box said %r, wanted %s in it" % ("\n".join(said)[:70], TAG))
# The empty stand-in above would satisfy "says no ffmpeg" without a
# box ever standing there, so the box itself is part of the judgement.
check("and it is not the box that says ffmpeg is in place",
      offers != [] and tuple(said) != tuple(vpm.ffmpeg_in_place())
      and "ffmpeg" not in "\n".join(said).lower(),
      "the box said %r, and ffmpeg's says %r"
      % ("\n".join(said)[:60], "\n".join(vpm.ffmpeg_in_place())[:60]))
check("the window's way of running a long job is handed back after",
      sink_after is hand_over,
      "the sink afterwards was %r, wanted %r" % (sink_after, hand_over))

print("\n2. The Update button leads to that road and no other")
was_watched = vpm.update_watched
was_newer = vpm.newer_release
was_owner = vpm.installed_by_a_package_manager
was_exec = QtWidgets.QDialog.exec
was_warning = QtWidgets.QMessageBox.warning
taken, warned = [], []
# A warning is answered here rather than by a person. Left alone it
# waits for a click that never comes: the road that puts one up is the
# road a broken update takes, and a test that hangs there says nothing.
try:
    vpm.update_watched = lambda w, tag, owner: taken.append((tag, owner)) or ""
    vpm.newer_release = lambda asked=False: (TAG, "", "", "")
    vpm.installed_by_a_package_manager = lambda: OWNER
    QtWidgets.QDialog.exec = lambda self: QtWidgets.QDialog.Accepted
    QtWidgets.QMessageBox.warning = \
        lambda parent, title, text: warned.append(text)
    vpm.update_offer(window, asked=True)
finally:
    vpm.update_watched = was_watched
    vpm.newer_release = was_newer
    vpm.installed_by_a_package_manager = was_owner
    QtWidgets.QDialog.exec = was_exec
    QtWidgets.QMessageBox.warning = was_warning
check("pressing Update in the window leads to the watched update",
      taken == [(TAG, OWNER)],
      "%d updates started, %r, wanted one for %s -- and %d warnings: %r"
      % (len(taken), taken[:1], TAG, len(warned), warned[:1]))

print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
