#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Does the program still come up, and does the window still build?

    cd tests && LANG=C LC_ALL=C LANGUAGE=en VPM_FIXTURES=/tmp/vpm-fixtures-<you> \\
      python3 ../development/probe.py

One line and a return code: `load() ok, gui() ok, N top-level widgets`
and rc=0, or the exception that stopped it and rc=1. Nothing else.

**This is how a refusal from the seam is read: by running it.** Six
kinds of name cannot be bound at a piece's head, and
`development/internals.md` lists them; four of the six answer the
identical `AttributeError: 'Program' object has no attribute '<name>'`,
one is not an error at all, and one is *accepted* and quietly keeps a
stale copy. **None of that can be seen in the source.** Between a block
that moved house and a program that still starts there is no argument,
only this run.

**It builds the window, and that is not decoration.** A head line can be
fine for the loader and wrong for the window: what `ui/` and the six
pieces read out of it hold is on the programme only after `take_from(ui)`
has run, which is after the whole window has been read. A probe that
only called `load()` was green through a fault that `gui()` catches in
two seconds.

Run it after **every** step that moves a block or writes a head line,
not once at the end. A block that goes in whole and then refuses costs
the bisection.

**What it does not do is stand in for the suite.** Measured 7.9.2026
while the table toolbox was moved: the probe was green through a head
line nobody read (`source_no_loose_ends` red) and through a five-line
comment that pushed the `long_blocks` ratchet from 7 to 8. The probe
says the program runs. Only `bash run.sh` says the program is right.

`gui()` enters the Qt loop and does not come back on its own, so a timer
shuts it again once the window stands. Two and a half seconds is the
wait, measured against a builder nine times slower than this machine
only in that it is generous here and never reached in a healthy run.
"""
import os
import sys

# python3 puts this script's own folder on the path, not the one it was
# started from. The tests folder is where the_program lives.
sys.path.insert(0, os.getcwd())

os.environ["QT_QPA_PLATFORM"] = "offscreen"
os.environ.setdefault("VPM_SILENT", "1")
os.environ.setdefault("VPM_NO_SPEAKER_SPLIT", "1")
os.environ.setdefault("VPM_NO_UPDATE_CHECK", "1")

try:
    import the_program
except ImportError:
    print("probe FAIL  no the_program here -- run it from the tests folder")
    sys.exit(1)
from PySide6 import QtCore, QtWidgets

app = QtWidgets.QApplication(sys.argv[:1])
try:
    vpm = the_program.load()
except Exception as e:
    print("load() FAIL  %s: %s" % (type(e).__name__, e))
    sys.exit(1)

stood = []


def look():
    stood.append(len(app.topLevelWidgets()))
    app.quit()


QtCore.QTimer.singleShot(2500, look)
QtCore.QTimer.singleShot(60000, app.quit)
try:
    vpm.gui()
except Exception as e:
    print("gui()  FAIL  %s: %s" % (type(e).__name__, e))
    sys.exit(1)
if not stood or not stood[0]:
    print("gui()  FAIL  no window stood after 2.5 s")
    sys.exit(1)
print("load() ok, gui() ok, %d top-level widgets" % stood[0])
sys.exit(0)
