# -*- coding: utf-8 -*-
"""Where Linux has no secret-tool, it is offered, and then the key is kept.

Sections, as the test prints them: the package each Linux manager
installs it from, and the advice where there is none; the command
line answered yes -- asked once, the manager run, the key stored; the
command line answered no -- nothing run, and what to type said; no
terminal, where nobody is asked; a manager that says it worked and
brings no secret-tool, which is not taken for it; a test run, which
asks nobody; the window's box answered with its button -- the command
named, the manager run, the key stored, the tick back -- and answered
Later, with the tick off and the key's line saying what to type. The
piece is told it runs on Linux; the manager and secret-tool are #!
stand-ins on PATH, so a Windows runner sets this test aside. No real
package manager and no real keyring is reached.
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
import builtins
import contextlib
import getpass
import io
import json
import shutil
import stat
import tempfile
import time
import traceback
import the_program

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
os.environ["VPM_NO_UPDATE_CHECK"] = "1"

from PySide6 import QtWidgets, QtCore            # noqa: E402

app = QtWidgets.QApplication(sys.argv[:1])
vpm = the_program.load()
vpm.set_language("en")
# All three names of the store go somewhere throwaway first.
import key_store_apart                            # noqa: E402
key_store_apart.apart(vpm)

began = time.time()
done = 0
bad = []
reached = []


def check(name, ok, extra=""):
    global done
    done += 1
    print("  %-58s %s %s" % (name, "ok" if ok else "FAIL", extra))
    if not ok:
        bad.append("%s [%s]" % (name, extra or "no numbers"))


def finish():
    """The one way out: the count, the verdict, the return code."""
    if not reached:
        bad.append("the drive got to its end [it stopped before, "
                   "after %d checks]" % done)
    print("\n%d checks in %.2f s" % (done, time.time() - began))
    print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
    sys.exit(1 if bad else 0)


# Invented, and the only key this file knows.
KEY = "FAKEKEY-0000"
PATIENCE = 30.0
POLL = 0.02
WORK = tempfile.mkdtemp()
MANAGERS = os.path.join(WORK, "managers")
TOOLS = os.path.join(WORK, "tools")
os.makedirs(MANAGERS)
os.makedirs(TOOLS)
SECRET = os.path.join(TOOLS, "secret-tool")
INSTALL = ["install", "-y", "libsecret-tools"]

# ------------------------------------------------ the stand-in secret-tool
# As strict as the real one where it matters here: an entry is found only
# under the attributes it was stored under, and a lookup of nothing
# answers 1 with nothing printed.
SECRET_TEXT = r'''#!%s
import json, os, sys
kept_file = %r
words = sys.argv[1:]
what = words.pop(0) if words else ""
if what == "store":
    if not words or not words[0].startswith("--label="):
        sys.exit(2)
    words.pop(0)
if len(words) %% 2 or what not in ("store", "lookup", "clear"):
    sys.exit(2)
place = json.dumps(sorted(zip(words[0::2], words[1::2])))
kept = json.load(open(kept_file)) if os.path.exists(kept_file) else {}
if what == "store":
    kept[place] = sys.stdin.buffer.read().decode("utf-8")
elif what == "clear":
    kept.pop(place, None)
else:
    if place not in kept:
        sys.exit(1)
    sys.stdout.write(kept[place])
json.dump(kept, open(kept_file, "w"))
''' % (sys.executable, os.path.join(WORK, "kept.json"))

# ------------------------------------------------ the stand-in apt-get
# Writes down every argument list it is started with. Told "install" it
# lays the stand-in secret-tool down, as the package would; "lie" says
# it worked and lays nothing down; anything else fails.
MANAGER_TEXT = r'''#!%s
import json, os, stat, sys
work = %r
with open(os.path.join(work, "manager.log"), "a") as f:
    f.write(json.dumps(sys.argv[1:]) + "\n")
plan = open(os.path.join(work, "manager_plan")).read().strip()
if plan == "install":
    with open(%r, "w") as f:
        f.write(%r)
    os.chmod(%r, 0o755)
    print("Setting up libsecret-tools")
    sys.exit(0)
sys.exit(0 if plan == "lie" else 100)
''' % (sys.executable, WORK, SECRET, SECRET_TEXT, SECRET)
with open(os.path.join(MANAGERS, "apt-get"), "w") as f:
    f.write(MANAGER_TEXT)
os.chmod(os.path.join(MANAGERS, "apt-get"), 0o755)


def fresh(plan):
    """No secret-tool, nothing kept, the manager told how to answer."""
    for name in ("manager.log", "kept.json"):
        if os.path.exists(os.path.join(WORK, name)):
            os.remove(os.path.join(WORK, name))
    if os.path.exists(SECRET):
        os.remove(SECRET)
    with open(os.path.join(WORK, "manager_plan"), "w") as f:
        f.write(plan)


def manager_calls():
    """Every argument list the stand-in manager was started with."""
    where = os.path.join(WORK, "manager.log")
    if not os.path.exists(where):
        return []
    return [json.loads(line) for line in open(where)]


def kept_key():
    """What the stand-in keyring holds under the moved names, or None."""
    where = os.path.join(WORK, "kept.json")
    if not os.path.exists(where):
        return None
    place = json.dumps(sorted([["service", vpm.KEY_SERVICE],
                               ["account", vpm.KEY_ACCOUNT]]))
    return json.load(open(where)).get(place)


# --------------------------------------------- the piece, told it is Linux
class Seen(object):
    """A module as the piece sees it, with some names answered otherwise."""

    def __init__(self, real, **answers):
        self._real, self._answers = real, answers

    def __getattr__(self, name):
        if name in self._answers:
            return self._answers[name]
        return getattr(self._real, name)


class Terminal(object):
    """A standard input somebody sits at, or nobody."""

    def __init__(self, there):
        self.there = there

    def isatty(self):
        return self.there


class OnlyTool(object):
    """A search path holding one manager and nothing else, sudo neither."""

    def __init__(self, tool):
        self.tool = tool

    def which(self, name, *rest, **more):
        return "/usr/bin/" + name if name == self.tool else None


piece = vpm.setup
saved = dict((n, piece.__dict__[n]) for n in ("sys", "shutil",
                                               "INSTALL_TOOLS"))
saved_path = os.environ.get("PATH", "")
saved_silent = os.environ.get("VPM_SILENT")
saved_input = builtins.input
saved_prompt = getpass.getpass
questions = []
answer = [""]


def asked(prompt=""):
    questions.append(prompt)
    return answer[0]


def linux(there):
    """The piece on Linux with this terminal, and only the stand-ins."""
    piece.__dict__["sys"] = Seen(sys, platform="linux",
                                 stdin=Terminal(there))
    piece.__dict__["INSTALL_TOOLS"] = False
    os.environ["PATH"] = MANAGERS + os.pathsep + TOOLS


def home():
    """Everything back the way the program had it."""
    for name, what in saved.items():
        piece.__dict__[name] = what
    os.environ["PATH"] = saved_path
    if saved_silent is None:
        os.environ.pop("VPM_SILENT", None)
    else:
        os.environ["VPM_SILENT"] = saved_silent


def switch(there, reply, silent=False):
    """--store-auphonic-key on Linux: (code, what it said, questions)."""
    del questions[:]
    answer[0] = reply
    out = io.StringIO()
    linux(there)
    if not silent:
        # The offer is never made in a test run, so the section that
        # measures it takes the mark off -- only the stand-ins are on
        # PATH, and nothing of this opens a connection.
        os.environ.pop("VPM_SILENT", None)
    try:
        with contextlib.redirect_stdout(out):
            code = piece.store_key_from_terminal()
    finally:
        home()
    return code, out.getvalue(), list(questions)


builtins.input = asked
getpass.getpass = lambda *a, **k: KEY
try:
    print("1. The package each manager installs secret-tool from")
    got = {}
    for tool in ("apt-get", "dnf", "zypper", "pacman"):
        piece.__dict__["shutil"] = OnlyTool(tool)
        piece.__dict__["sys"] = Seen(sys, platform="linux")
        got[tool] = list(piece.secret_tool_command())
        home()
    check("apt-get is asked for libsecret-tools",
          got["apt-get"] == ["apt-get", "install", "-y", "libsecret-tools"],
          "it would run %r" % (got["apt-get"],))
    check("dnf is asked for libsecret",
          got["dnf"] == ["dnf", "install", "-y", "libsecret"],
          "it would run %r" % (got["dnf"],))
    check("zypper is asked for secret-tool",
          got["zypper"] == ["zypper", "--non-interactive", "install",
                            "secret-tool"],
          "it would run %r" % (got["zypper"],))
    check("pacman is asked for libsecret",
          got["pacman"] == ["pacman", "-S", "--noconfirm", "libsecret"],
          "it would run %r" % (got["pacman"],))
    piece.__dict__["shutil"] = OnlyTool("nothing")
    piece.__dict__["sys"] = Seen(sys, platform="linux")
    bare = (piece.secret_tool_command(), piece.secret_tool_by_hand())
    home()
    check("with no manager the advice names the packages instead",
          bare[0] == () and "libsecret-tools" in bare[1],
          "command %r, advice %r" % (bare[0], bare[1]))

    print("\n2. The command line, answered yes")
    fresh("install")
    code, out, asks = switch(True, "y")
    check("the terminal is asked once whether to install it",
          len(asks) == 1,
          "%d question(s): %r" % (len(asks), asks))
    check("and on yes the manager is run for libsecret-tools",
          manager_calls() == [INSTALL],
          "the manager was started with %r" % (manager_calls(),))
    check("then the key is stored, and the switch ends with 0",
          code == 0 and kept_key() == KEY,
          "returned %r, the keyring holds %s" % (
              code, "nothing" if kept_key() is None
              else "%d characters, wanted %d" % (len(kept_key()), len(KEY))))

    print("\n3. The command line, answered no")
    fresh("install")
    code, out, asks = switch(True, "n")
    check("answered no, the manager is not started",
          len(asks) == 1 and manager_calls() == [],
          "%d question(s), the manager started %d time(s)"
          % (len(asks), len(manager_calls())))
    by_hand = vpm.T('This machine has no secret-tool, which keeps the key '
                    'in the desktop\'s keyring, so nothing was stored. By '
                    'hand: %s') % "apt-get install -y libsecret-tools"
    check("and it ends with 1, saying what to type by hand",
          code == 1 and by_hand in out,
          "returned %r, printed %r" % (code, out.replace(KEY, "<key>")[-200:]))

    print("\n4. No terminal to answer in")
    fresh("install")
    code, out, asks = switch(False, "y")
    check("with no terminal nobody is asked and nothing is installed",
          asks == [] and manager_calls() == [] and code == 1,
          "%d question(s), the manager started %d time(s), returned %r"
          % (len(asks), len(manager_calls()), code))

    print("\n5. A manager that says it worked and brings nothing")
    fresh("lie")
    del questions[:]
    linux(True)
    os.environ.pop("VPM_SILENT", None)
    try:
        with contextlib.redirect_stdout(io.StringIO()):
            came = piece.install_secret_tool(asked=True)
    finally:
        home()
    check("a manager's word is not taken for secret-tool being there",
          len(manager_calls()) == 1 and came is False,
          "the manager started %d time(s), install_secret_tool answered %r"
          % (len(manager_calls()), came))

    print("\n6. A test run")
    fresh("install")
    os.environ["VPM_SILENT"] = "1"
    code, out, asks = switch(True, "y", silent=True)
    check("a test run asks nobody and installs nothing",
          asks == [] and manager_calls() == [],
          "%d question(s), the manager started %d time(s)"
          % (len(asks), len(manager_calls())))
except Exception as exc:                          # noqa: BLE001
    traceback.print_exc()
    bad.append("the command line sections ran [%s: %s]"
               % (type(exc).__name__, exc))
finally:
    home()
    builtins.input = saved_input
    getpass.getpass = saved_prompt

# ------------------------------------------------------------ the window
vpm.update_offer = lambda *a, **k: None
vpm.key_store_locked = lambda: False
vpm.list_presets = lambda key: [("Podcast_Single", "u2", False)]


def box_answered(self, *_args):
    """A dialog that would wait is turned down at once."""
    return QtWidgets.QDialog.Rejected


QtWidgets.QDialog.exec = box_answered


class Box(object):
    """The offer's box: what it says written down, one button pressed."""
    made = []
    press = [""]

    def __init__(self, parent):
        self.title, self.text, self.buttons = "", "", []
        self.pressed = None
        Box.made.append(self)

    def setWindowTitle(self, text):
        self.title = text

    def setText(self, text):
        self.text = text

    def setInformativeText(self, text):
        pass

    def addButton(self, text, role):
        self.buttons.append(text)
        return text

    def exec(self):
        for b in self.buttons:
            if b.startswith(Box.press[0]):
                self.pressed = b
        return 0

    def clickedButton(self):
        return self.pressed


Box.AcceptRole, Box.RejectRole = 0, 1


class Widgets(object):
    QMessageBox = Box


def drawn(text):
    """What ends up on the screen: & marks a key, && draws one &."""
    return str(text).replace("&&", "\x00").replace("&", "") \
                    .replace("\x00", "&")


def among(kind):
    return [w for w in app.allWidgets() if isinstance(w, kind)]


def key_field():
    for w in among(QtWidgets.QLineEdit):
        if w.echoMode() == QtWidgets.QLineEdit.Password:
            return w
    return None


def keep_box():
    said = {vpm.T('Save in Keychain'), vpm.T('Save in Registry'),
            vpm.T('Keep it saved')}
    for b in among(QtWidgets.QCheckBox):
        if drawn(b.text()).strip() in said:
            return b
    return None


def notes():
    return [w for w in among(QtWidgets.QLabel)
            if w.objectName() in ("key_note", "key_note_settings")]


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


def ticked(tick, press):
    """The tick set by hand on Linux with no secret-tool, *press* pressed.

    The install runs where the window runs it, handed to the Output
    tab's sink -- here one that runs the job at once, as the window's
    thread would, and keeps its lines. The piece stays on Linux
    afterwards, so the store the window goes back to is the stand-in;
    home() ends that.
    """
    lines = []
    was_sink, was_widgets = vpm.UPDATE_SINK, vpm._qt_widgets

    def sink(job):
        trouble = job(lines.append)
        if trouble:
            lines.append(trouble)

    Box.made, Box.press[0] = [], press
    linux(True)
    os.environ.pop("VPM_SILENT", None)
    vpm.UPDATE_SINK, vpm._qt_widgets = sink, (lambda: Widgets)
    try:
        tick.click()
    finally:
        vpm.UPDATE_SINK, vpm._qt_widgets = was_sink, was_widgets
        if saved_silent is not None:
            os.environ["VPM_SILENT"] = saved_silent
    return lines


def drive():
    print("\n7. The window, the box answered with its button")
    took = waited_for(lambda: key_field() and keep_box(),
                      "the key field and the tick")
    field, tick = key_field(), keep_box()
    if took is None:
        # The ground under the two sections, not a judgement of its own.
        bad.append("the window came up with its key field and tick "
                   "[field %s, tick %s]" % (field is not None,
                                            tick is not None))
        return
    if tick.isChecked():
        tick.click()
    field.setText(KEY)
    app.processEvents()
    fresh("install")
    get_it = vpm.T('Get it: %s').split("%s")[0]
    lines = ticked(tick, get_it)
    offered = [(b.title, b.buttons) for b in Box.made]
    check("a tick with no secret-tool offers it in a box, command named",
          len(offered) == 1 and offered[0][0] == "secret-tool"
          and vpm.T('Get it: %s') % "apt-get install -y libsecret-tools"
          in offered[0][1],
          "%d box(es): %r" % (len(offered), offered))
    check("the button runs the manager for libsecret-tools",
          manager_calls() == [INSTALL],
          "the manager was started with %r" % (manager_calls(),))
    # The key is stored again from the window's own thread, once the
    # timer sees the job ended; so this waits on the tick.
    came = waited_for(lambda: tick.isChecked(), "the tick to come back")
    check("once it is there the key is stored and the tick comes back",
          came is not None and kept_key() == KEY,
          "tick %s after %s s, the keyring holds %s; the job said %r"
          % ("on" if tick.isChecked() else "off",
             "%.2f" % came if came else came,
             "nothing" if kept_key() is None else
             "%d characters" % len(kept_key()),
             [x.strip()[:50] for x in lines][-3:]))
    home()

    print("\n8. The window, the box answered Later")
    tick.click()             # off again: the key leaves the store
    app.processEvents()
    fresh("install")
    ticked(tick, vpm.T('Later'))
    app.processEvents()
    home()
    said = [(w.objectName(), drawn(w.text()), w.isHidden())
            for w in notes()]
    want = vpm.T('The key was not saved: %s') % (
        vpm.T('This machine has no secret-tool, which keeps the key in '
              'the desktop\'s keyring, so nothing was stored. By hand: '
              '%s') % "apt-get install -y libsecret-tools")
    shown = sorted(n for n, t, h in said if t == want and not h)
    check("answered Later, nothing is installed and the tick stays off",
          manager_calls() == [] and not tick.isChecked()
          and len(Box.made) == 1,
          "%d box(es), the manager started %d time(s), tick %s"
          % (len(Box.made), len(manager_calls()),
             "on" if tick.isChecked() else "off"))
    check("and the key's line says what to type by hand",
          shown == ["key_note", "key_note_settings"],
          "shown in %s of %d lines; they say %s"
          % (shown, len(said), [t[:60] for _n, t, _h in said]))
    reached.append(True)


def drive_and_quit():
    try:
        drive()
    except Exception as exc:                      # noqa: BLE001
        traceback.print_exc()
        bad.append("the drive ran without an error [%s: %s]"
                   % (type(exc).__name__, exc))
    finally:
        home()
        app.quit()


QtCore.QTimer.singleShot(0, drive_and_quit)
sys.argv = ["videopodcast_magic.py"]
try:
    vpm.gui()
except Exception as exc:                          # noqa: BLE001
    traceback.print_exc()
    bad.append("the window was built [%s: %s]" % (type(exc).__name__, exc))
finally:
    home()
    shutil.rmtree(WORK, ignore_errors=True)
finish()
