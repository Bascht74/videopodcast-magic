# -*- coding: utf-8 -*-
"""Connecting to auphonic.com must not by itself arm a paid run.

The sections: a key lying only in the store, on the command line --
each of the three ways takes it, the one place a key is kept, and
none of them sends anything while no preset was named; then the window
with a stored key, where 'without Auphonic' stays chosen. main() is
stopped at a stand-in preflight, the service and the store are stood
in for, and the video way's sending is judged at its preset gate only.
"""
PLATFORM_BOUND = True
import io
import os
import shutil
import sys
import tempfile
import types
# tests/, where the helpers and state/ lie; this file may stand in a
# folder under it, or in one under that.
HERE = os.path.dirname(os.path.abspath(__file__))
while not os.path.isfile(os.path.join(HERE, "the_program.py")) \
        and os.path.dirname(HERE) != HERE:
    HERE = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import the_program
SCRIPT = the_program.SCRIPT
import sys, time
began = time.time()

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
# The material for the command line: empty files the parser and main()
# accept, never read, because the run stops at the preflight. The cache
# lies beside them, so main()'s tidying touches nothing of anybody's.
FOLDER = tempfile.mkdtemp(prefix="vpm_none_chosen_")
os.makedirs(os.path.join(FOLDER, "cache"))
os.environ["VPM_CACHE"] = os.path.join(FOLDER, "cache")
MATERIAL = {}
for name in ("one.wav", "host.wav", "guest.wav", "camera.mp4"):
    MATERIAL[name] = os.path.join(FOLDER, name)
    io.open(MATERIAL[name], "wb").close()
from PySide6 import QtWidgets, QtCore
app = QtWidgets.QApplication(sys.argv[:1])
vpm = the_program.load()
# Before the window comes up: all three names of the credential store
# go somewhere throwaway. Measured on 2.9.2026 -- this file is the one
# that wrote "not-a-real-key" into the real keychain. The reading below
# is stood in for, the writing was not, and starting the window saves
# what it read; on a Mac the two keychain names stood in the program
# where they were used, so nothing here could redirect them.
import key_store_apart                                      # noqa: E402
key_store_apart.apart(vpm)
vpm.list_presets = lambda key: [("Podcast_Multitrack", "u1", True),
                                ("Podcast_Zoom", "u2", False)]
vpm.load_api_key = lambda: "not-a-real-key"

done = 0
error = []
def check(name, ok, extra=""):
    global done
    done += 1
    print("  %-52s %s %s" % (name, "ok" if ok else "FAIL", extra))
    if not ok:
        error.append(name)

def win():
    for x in app.topLevelWidgets():
        if "Video Podcast Magic" in x.windowTitle():
            return x

def preset_box():
    """The preset list, wherever it currently hangs.

    A tab widget adopts a page only once that page is inserted, which
    happens when there are files. What matters here is what the list is
    set to, not where it hangs.
    """
    for b in app.allWidgets():
        if not isinstance(b, QtWidgets.QComboBox):
            continue
        for i in range(b.count()):
            if b.itemData(i) == vpm.PRESET_NONE:
                return b
    return None

def look():
    b = preset_box()
    if b is None:
        boxes = [w for w in app.allWidgets()
                 if isinstance(w, QtWidgets.QComboBox)]
        check("preset list found", False,
              "no list held PRESET_NONE: %d lists on screen, "
              "with %s entries" % (len(boxes),
                                   [w.count() for w in boxes][:10]))
        app.quit(); return
    # Opening the list is what asks the service: a start must not speak
    # to a third party about a key it was only asked to keep. So the
    # list is opened here, the way somebody would.
    b.showPopup()
    b.hidePopup()
    # The fetch runs in a thread, so the list is not full the moment the
    # popup closes. Waited for, not slept through: on a busy machine a
    # fixed pause is either too short or wasted.
    import time
    until = time.time() + 20.0
    while b.count() < 2 and time.time() < until:
        app.processEvents()
        time.sleep(0.02)
    print("     waited %.1f s for the list" % (20.0 - (until - time.time())))

    print("1. With a stored key, after the list has been opened once")
    print("     entries: %s" % [b.itemText(i) for i in range(b.count())])
    check("more than the placeholder is offered", b.count() > 1, str(b.count()))
    check("but 'without Auphonic' stays selected",
          b.currentData() == vpm.PRESET_NONE, repr(b.currentData()))

    print("\n2. Picking a preset still works and sticks")
    b.setCurrentIndex(1)
    check("a preset can be chosen", b.currentData() != vpm.PRESET_NONE,
          repr(b.currentData()))
    chosen = b.currentData()
    # a redraw of the list -- the mode changed, say -- keeps the choice
    for cb in app.allWidgets():
        if not isinstance(cb, QtWidgets.QCheckBox):
            continue
        if cb.text().startswith(vpm.T('Multitrack')[:9]):
            cb.setChecked(not cb.isChecked())
            cb.setChecked(not cb.isChecked())
            break
    app.processEvents()
    b2 = preset_box()
    check("and survives the list being rebuilt",
          b2.currentData() in (chosen, vpm.PRESET_NONE), repr(b2.currentData()))
    app.quit()

# ------------------------------------------ a stored key, command line
# Invented, and the only key this section knows. The store is
# replaced, so the real one is never read.
KEY = "FAKEKEY-0000"
vpm.RUN_KEY = ""
window_store = vpm.load_api_key
vpm.load_api_key = lambda: KEY
seen = []
sent = []


def stand_in_preflight(args, audio_paths, video_paths, project_type=None):
    """Stops the run where the preflight would, and keeps what it saw."""
    seen.append(args)
    return 1


def upload_stand_in(*a, **k):
    """Every way to auphonic.com: counted, and nothing goes."""
    sent.append(a)
    raise RuntimeError("an upload was started")


def run_with(*words):
    """main() on this command line, up to the stand-in preflight."""
    del seen[:]
    sys.argv = [SCRIPT] + list(words)
    try:
        vpm.main()
    except SystemExit:
        pass
    return seen[0] if seen else types.SimpleNamespace()


def carried(args):
    """The key and its origin as the run carries them, asked nothing.

    Not api_key_source: it reads the store again for a run that took no
    key, and so would repair the very fault asked about.
    """
    return (getattr(args, "auphonic_key", None),
            getattr(args, "auphonic_key_from", None))


kept_calls = dict((n, getattr(vpm, n)) for n in (
    "run_preflight", "run_single_production", "run_multitrack_production",
    "_curl_call", "normalise_loudness", "channel_count"))
vpm.run_preflight = stand_in_preflight
vpm.run_single_production = upload_stand_in
vpm.run_multitrack_production = upload_stand_in
vpm._curl_call = upload_stand_in
vpm.normalise_loudness = lambda *a, **k: (0.0, None)
vpm.channel_count = lambda path: 1
kept_stdin = sys.stdin
sys.stdin = io.StringIO("")     # nobody at the keyboard to pick a preset

print("A key only in the store counts on every way")
alone = run_with(MATERIAL["one.wav"])
check("one recording without a picture takes the stored key",
      carried(alone) == (KEY, "store"),
      "key and origin %r, wanted the stored one from 'store'"
      % (carried(alone),))
several = run_with("--multitrack", MATERIAL["host.wav"], MATERIAL["guest.wav"])
check("several recordings on one axis take the stored key",
      carried(several) == (KEY, "store"),
      "key and origin %r, wanted the stored one from 'store'"
      % (carried(several),))
pictured = run_with(MATERIAL["camera.mp4"], MATERIAL["one.wav"])
check("a run with a picture takes the stored key",
      carried(pictured) == (KEY, "store"),
      "key and origin %r, wanted the stored one from 'store'"
      % (carried(pictured),))
stop = vpm.check_mode_fits_input(
    [MATERIAL["host.wav"], MATERIAL["guest.wav"]], several) \
    if getattr(several, "multitrack", False) else "the run never got here"
check("and multitrack does not stop for want of a key",
      stop is None, "it said %r" % (str(stop)[:60],))
local = run_with("--without-auphonic", MATERIAL["one.wav"])
check("--without-auphonic leaves the stored key where it lies",
      getattr(local, "auphonic_key", "") is None,
      "the run carries %r" % (getattr(local, "auphonic_key", "no run"),))

print("\n... and with no preset named, none of the three sends anything")
said = ""
try:
    code = vpm.join_only(alone, [{"name": "one", "source": MATERIAL["one.wav"],
                                  "blocks": [MATERIAL["one.wav"]]}], FOLDER)
except Exception as e:
    code, said = "raised", str(e)
check("one recording without a picture sends nothing without a preset",
      not sent and code != 0,
      "%d uploads started, the way ended on %r %r"
      % (len(sent), code, said[:60]))
del sent[:]
tracks = [{"name": "host", "axis": MATERIAL["host.wav"]},
          {"name": "guest", "axis": MATERIAL["guest.wav"]}]
code = vpm.send_to_auphonic(several, tracks, FOLDER, FOLDER, 10.0)
check("several recordings on one axis send nothing without a preset",
      not sent and code == 1,
      "%d uploads started, the way returned %r" % (len(sent), code))
del sent[:]
try:
    chosen = vpm.choose_preset(KEY, pictured.auphonic_preset, False)
except Exception as e:
    chosen = "refused: %s" % str(e)[:40]
check("a run with a picture gets no preset it was not given",
      not sent and str(chosen).startswith("refused"),
      "%d uploads started, choose_preset gave %r" % (len(sent), chosen))

sys.stdin = kept_stdin
for name, call in kept_calls.items():
    setattr(vpm, name, call)
vpm.load_api_key = window_store
shutil.rmtree(FOLDER, True)
print()

QtCore.QTimer.singleShot(2500, look)
QtCore.QTimer.singleShot(40000, app.quit)
vpm.gui()
print("\n%d checks in %.2f s" % (done, time.time() - began))
print("\n%s" % ("All good." if not error else "FAIL: " + ", ".join(error)))
sys.exit(1 if error else 0)
