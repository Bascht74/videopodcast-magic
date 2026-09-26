# -*- coding: utf-8 -*-
"""Every word the window and the printed Auphonic lists show went through T().

The program speaks a made-up language: every text in full-width letters,
so a plain word of two letters or more never met T(); one letter is not
seen. The sections: the window as it starts, its menu bar and the Windows
key store; the file list's headings over an audio and a video file; the
settings window once its Resolve check found none; a production's status
block; the preset list, full and empty, from a stood-in account. Not
counted: names of files, presets and languages, LUFS, the log's path, what
Qt draws. Walked alone: the Windows store, the headings, Resolve's refusal.
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
import contextlib
import io
import re
import shutil
import struct
import subprocess
import tempfile
import time
import traceback
import types
import wave
import the_program

SCRIPT = the_program.SCRIPT

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
os.environ["VPM_NO_UPDATE_CHECK"] = "1"
os.environ.pop("AUPHONIC_TOKEN", None)

from PySide6 import QtWidgets, QtCore            # noqa: E402

app = QtWidgets.QApplication(sys.argv[:1])
vpm = the_program.load()
vpm.set_language("en")
sys.path.insert(0, HERE)
import key_store_apart                            # noqa: E402
key_store_apart.apart(vpm)

began = time.time()
done = 0
bad = []
reached = []


def check(name, ok, extra=""):
    """One judgement: one line, and a failure kept for the closing line."""
    global done
    done += 1
    print("  %-58s %s %s" % (name, "ok" if ok else "FAIL", extra))
    if not ok:
        bad.append("%s [%s]" % (name, extra or "no numbers"))


PATIENCE = 30.0
POLL = 0.02
# Words that are the same in every language: a unit of loudness.
SAME_EVERYWHERE = {"LUFS"}
PLAIN = re.compile(r"[A-Za-z]{2,}")
# What T() must leave as it is: a slot, a tag, an entity.
UNTOUCHED = re.compile(r"%(\([^)]*\))?[-#0 +]*\d*(\.\d+)?[sdifgeExXcr%]"
                       r"|<[^>]*>|&[a-z]+;")
WIDE = dict((c, chr(ord(c) + 0xFEE0)) for c in
            "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz")


def made_up(text):
    """The text in the made-up language: every letter full width."""
    out, last = [], 0
    for m in UNTOUCHED.finditer(text):
        out.append("".join(WIDE.get(c, c) for c in text[last:m.start()]))
        out.append(m.group(0))
        last = m.end()
    out.append("".join(WIDE.get(c, c) for c in text[last:]))
    return "".join(out)


class MadeUp(dict):
    """A catalogue that knows every text, in the made-up language."""

    def get(self, key, default=None):
        """Every text translated, whether any catalogue holds it or not."""
        return made_up(key) if isinstance(key, str) else default


vpm.language.CATALOGUE["en"] = MadeUp()

# The key store stood in for, so no real key is read or written, and the
# box built as on Windows: the one platform whose store had a raw name.
vpm._ask_key_store = lambda: ""
vpm.load_api_key = lambda: ""
vpm.store_api_key = lambda key: False
vpm.delete_api_key = lambda: False
vpm.key_store_locked = lambda: False
vpm.update_offer = lambda *a, **k: None
vpm.make_auphonic_box.__globals__["platform"] = types.SimpleNamespace(
    system=lambda: "Windows")
# A box that would wait for a click is answered at once.
QtWidgets.QDialog.exec = lambda self: QtWidgets.QDialog.Rejected

folder = tempfile.mkdtemp(prefix="vpm_shown_")
# Resolve's door nailed shut, and its interface looked for where none is:
# the refusal is the same on every machine and the one branch judged.
NO_API = os.path.join(folder, "no_interface")
NO_LIB = os.path.join(folder, "no_library.so")
vpm.resolve_module_paths = lambda: (NO_API, NO_LIB)


def no_resolve(*_args, **_kwargs):
    """A Resolve asked for; the answer is that none is there."""
    raise RuntimeError("text_shown_catalogued asked for a Resolve")


vpm.connect_to_resolve = no_resolve


def no_wire(*_args, **_kwargs):
    """auphonic.com asked; this test never goes outside."""
    raise RuntimeError("text_shown_catalogued asked auphonic.com")


# The account's answer stood in for, and the wire it would come down cut.
PRESETS = ["Podcast_Zoom", "Podcast_Studio"]
vpm.list_presets = lambda key: [(PRESETS[0], "u1", False),
                                (PRESETS[1], "u2", None)]
vpm._curl_call = no_wire
AUDIO = os.path.join(folder, "Guest_REC0001.wav")
VIDEO = os.path.join(folder, "WideCam_C0001.mov")
with wave.open(AUDIO, "wb") as f:
    f.setnchannels(1)
    f.setsampwidth(2)
    f.setframerate(48000)
    f.writeframes(struct.pack("<48000h", *([0] * 48000)))
subprocess.run(["ffmpeg", "-v", "error", "-f", "lavfi", "-i",
                "testsrc=size=160x90:rate=25:duration=1", "-f", "lavfi",
                "-i", "sine=frequency=300:duration=1", "-c:v", "libx264",
                "-preset", "ultrafast", "-pix_fmt", "yuv420p", "-c:a",
                "aac", "-shortest", "-y", VIDEO], check=True)
# Written as the reader has them: the files' names and every language's
# own name for itself, longest first so no name is cut by a shorter one.
OWN_NAMES = sorted([NO_API, NO_LIB, folder, os.path.basename(AUDIO),
                    os.path.basename(VIDEO)]
                   + [p for p in [vpm.log_path()] if p]
                   + list(vpm.language.LANGUAGE_NAMES.values()),
                   key=len, reverse=True)
QtWidgets.QFileDialog.getOpenFileNames = staticmethod(
    lambda *a, **k: ([AUDIO, VIDEO], ""))


def finish():
    """The one way out: the count, the verdict, the return code."""
    shutil.rmtree(folder, ignore_errors=True)
    if not reached:
        bad.append("the drive got to its end [it stopped before, "
                   "after %d checks]" % done)
    print("\n%d checks in %.2f s" % (done, time.time() - began))
    print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
    sys.exit(1 if bad else 0)


def drawn(text):
    """What ends up on the screen: & marks a key, && draws one &."""
    return str(text).replace("&&", "\x00").replace("&", "") \
                    .replace("\x00", "&")


def plain_words(where, text, found):
    """Note every word in plain letters, the reader's own names aside."""
    text = re.sub(r"<[^>]*>", " ", drawn(text or ""))
    for own in OWN_NAMES:
        text = text.replace(own, " ")
    for word in PLAIN.findall(text):
        if word not in SAME_EVERYWHERE:
            found.append("%s in %s %r" % (word, where, text[:60]))


def widget_words(widgets):
    """The plain words on these widgets, Qt's own scroll arrows aside."""
    found = []
    for w in widgets:
        if isinstance(w.parent(), QtWidgets.QTabBar):
            continue
        kind = type(w).__name__
        for ask in ("text", "toolTip", "title", "placeholderText",
                    "windowTitle", "accessibleName",
                    "accessibleDescription"):
            f = getattr(w, ask, None)
            if callable(f):
                try:
                    plain_words(kind + "." + ask, f(), found)
                except TypeError:
                    pass
        if isinstance(w, QtWidgets.QTabWidget):
            for i in range(w.count()):
                plain_words("tab", w.tabText(i), found)
                plain_words("tab tip", w.tabToolTip(i), found)
        if isinstance(w, QtWidgets.QComboBox):
            for i in range(w.count()):
                plain_words("choice", w.itemText(i), found)
        if isinstance(w, QtWidgets.QTreeWidget):
            head = w.headerItem()
            for c in range(head.columnCount()):
                plain_words("column", head.text(c), found)
    return found


def menu_words():
    """The plain words on the menu bar's entries, their tips included."""
    found = []
    for m in among(QtWidgets.QMenuBar) + among(QtWidgets.QMenu):
        for a in m.actions():
            plain_words("menu entry", a.text(), found)
            plain_words("menu entry tip", a.toolTip(), found)
    return found


def entries():
    """How many entries with a caption the menu bar's menus hold."""
    return sum(1 for m in among(QtWidgets.QMenu) for a in m.actions()
               if a.text())


def heading_words(tree):
    """The plain words on the file list's headings, tips included."""
    found = []
    root = tree.invisibleRootItem()
    for i in range(root.childCount()):
        for c in range(tree.columnCount()):
            plain_words("heading", root.child(i).text(c), found)
            plain_words("heading tip", root.child(i).toolTip(c), found)
    return found


def said(found):
    """A FAIL line's evidence: how many, and the first three by place."""
    return "%d plain word(s): %s" % (len(found), "; ".join(found[:3]))


def among(kind):
    """Every widget of this kind the application holds."""
    return [w for w in app.allWidgets() if isinstance(w, kind)]


def button(caption):
    """The button with this caption in the made-up language, or None.

    Written by the test's own hand, never asked of T(): a T() that
    skipped the catalogue would otherwise find its own plain caption.
    """
    for b in among(QtWidgets.QPushButton):
        if drawn(b.text()).strip() == made_up(caption):
            return b
    return None


def file_list():
    """The file list: the one tree with five columns, or None."""
    for t in among(QtWidgets.QTreeWidget):
        if t.columnCount() == 5:
            return t
    return None


def groups():
    """The kinds the file list shows a heading for, top down."""
    t = file_list()
    root = t.invisibleRootItem() if t else None
    return [root.child(i).data(0, QtCore.Qt.UserRole + 1)
            for i in range(root.childCount())] if root else []


def settings_window():
    """The settings window while it is on screen, or None."""
    for d in among(QtWidgets.QDialog):
        if d.isVisible() and d.windowTitle() == made_up('Settings'):
            return d
    return None


def resolve_heads(d):
    """What the settings window's Resolve check says in its head line."""
    labels = d.findChildren(QtWidgets.QLabel) if d else []
    return [drawn(w.text()) for w in labels
            if drawn(w.text()).startswith(made_up('Resolve answers'))
            or drawn(w.text()) == made_up('checking ...')]


def waited_for(condition, why):
    """Wait on a condition, never on the clock; None when it never came."""
    began_here = time.time()
    while time.time() - began_here < PATIENCE:
        app.processEvents()
        if condition():
            return time.time() - began_here
        time.sleep(POLL)
    print("      gave up after %.1f s waiting for %s" % (PATIENCE, why))
    return None


def drive():
    """Walk the sections in order, one check after another."""
    print("1. The window as it starts, its menu bar, the Windows key store")
    took = waited_for(lambda: button('Add files ...') is not None,
                      "the Add files button in the made-up language")
    check("the window came up, speaking the made-up language",
          took is not None,
          "a button saying %r after %s s, patience %.0f s"
          % (made_up('Add files ...'), "%.2f" % took if took else took,
             PATIENCE))
    if took is None:
        return
    ticks = [drawn(b.text()) for b in among(QtWidgets.QCheckBox)]
    check("the key-store tick is the Windows one",
          made_up('Save in Registry') in ticks,
          "wanted %r among %d ticks, first %s"
          % (made_up('Save in Registry'), len(ticks), ticks[:3]))
    found = widget_words(app.allWidgets())
    check("every word on the window as it starts went through T()",
          not found, said(found))
    found = menu_words() if entries() else ["(no menu entry to read)"]
    check("every entry of the menu bar went through T()",
          not found, "%d entries; %s" % (entries(), said(found)))

    print("\n2. The headings of the file list")
    button('Add files ...').click()
    took = waited_for(lambda: sorted(groups()) == ["audio", "video"],
                      "an AUDIO and a VIDEO heading")
    check("the file list holds an audio and a video heading",
          took is not None, "the headings are for %s" % groups())
    found = heading_words(file_list()) if file_list() \
        else ["(no file list to read)"]
    check("every word on the file list's headings went through T()",
          not found, said(found))

    print("\n3. The settings window")
    way = button('Settings ...')
    if way is not None:
        way.click()
    took = waited_for(lambda: settings_window() is not None,
                      "the settings window")
    check("the settings window opened",
          took is not None, "button found %s, window titled %r seen %s"
          % (way is not None, made_up('Settings'), took is not None))
    d = settings_window()
    refused = made_up('Resolve answers%s') % made_up(' not.')
    took = waited_for(lambda: refused in resolve_heads(d),
                      "the Resolve check's answer") if d else None
    check("the Resolve check in it has answered that none is there",
          took is not None, "wanted %r, its head says %s"
          % (refused, resolve_heads(d)))
    found = widget_words([d] + d.findChildren(QtWidgets.QWidget)) \
        if d else ["(no settings window to read)"]
    check("every word in the settings window went through T()",
          not found, said(found))
    if d:
        d.close()

    print("\n4. The status block of a production")
    names = ["1_2", "3.zip", "4.wav", "5.mp4"]
    production = {"status_string": "7",
                  "creation_time": "2026-01-01T10:00:00",
                  "multi_input_files": [{"id": "8", "input_file": "1_2"},
                                        {"id": "9", "input_file": None}],
                  "output_files": [{"filename": n, "download_url": "u"}
                                   for n in names[1:]]}
    out = io.StringIO()
    with contextlib.redirect_stdout(out):
        vpm.print_production(production)
        vpm.print_production({"status_string": "7"})
    text = out.getvalue()
    for n in names:
        text = text.replace(n, " ")
    found = []
    plain_words("status block", text, found)
    check("every word of a production's status block went through T()",
          not found and bool(text.strip()), said(found))

    print("\n5. The preset list --list-presets prints")
    out = io.StringIO()
    with contextlib.redirect_stdout(out):
        vpm.print_presets("not-a-real-key", False)
        vpm.list_presets = lambda key: []
        vpm.print_presets("not-a-real-key", False)
    text = out.getvalue()
    listed = all(n in text for n in PRESETS)
    for n in PRESETS:
        text = text.replace(n, " ")
    found = []
    plain_words("preset list", text, found)
    check("every word of the preset list went through T()",
          not found and listed, "the stand-in's names printed %s; %s"
          % (listed, said(found)))
    reached.append(True)


def drive_and_quit():
    """Every way out of the drive ends the window and reaches finish()."""
    try:
        drive()
    except Exception as exc:                      # noqa: BLE001
        traceback.print_exc()
        bad.append("the drive ran without an error [%s: %s]"
                   % (type(exc).__name__, exc))
    finally:
        app.quit()


QtCore.QTimer.singleShot(0, drive_and_quit)
sys.argv = ["videopodcast_magic.py"]
try:
    vpm.gui()
except Exception as exc:                          # noqa: BLE001
    traceback.print_exc()
    bad.append("the window was built [%s: %s]" % (type(exc).__name__, exc))
finish()
