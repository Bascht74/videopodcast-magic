# -*- coding: utf-8 -*-
"""The ffmpeg the program insists on: new enough, and only that.

One condition, not two. The floor is the oldest build measured to hand
a camera file's boxes through a copy unchanged; soxr is no part of it,
because a build without soxr takes the clock drift out in steps of
21 ppm instead of 0.21 -- coarser, and coarser is not broken.

The version is read off the line ffmpeg prints, so the reading is held
against lines real builds really write -- Homebrew, evermeet, Debian,
gyan, and one straight out of git that carries a commit where the
number should be. Then in order: the floor itself, what the decision
makes of a version above and below it, that both tools are asked and
the old one named, that a build without soxr still lets the run start,
that what brew is offered is the bottle and not the tap -- the tap has
no bottle at all, so that button would compile in the window's own
thread -- that installing and building again are different commands, and that the ways out -- --help, --version,
--update -- still answer while the gate is shut.
"""
import os
import the_program
HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = the_program.SCRIPT
import shutil, subprocess, sys, tempfile, time
m = the_program.load()
m.set_language("en")

began = time.time()
done = 0
bad = []


def check(name, ok, extra=""):
    global done
    done += 1
    print("  %-58s %s %s" % (name, "ok" if ok else "FAIL", extra))
    if not ok:
        bad.append("%s [%s]" % (name, extra or "no numbers"))


# ------------------------------------------------------- reading the line
# First lines as builds really print them. The expectation stands here as
# a value; nothing recomputes it.
LINES = [
    ("ffmpeg version 9.0.1 Copyright (c) 2000-2026 the FFmpeg developers",
     (9, 0, 1), "9.0.1"),
    ("ffmpeg version 8.0-tessus  https://evermeet.cx/ffmpeg/  Copyright",
     (8, 0, 0), "8.0-tessus"),
    ("ffprobe version 9.0.1 Copyright (c) 2007-2026 the FFmpeg developers",
     (9, 0, 1), "9.0.1"),
    ("ffmpeg version 5.1.2-0+deb12u1 Copyright (c) 2000-2022",
     (5, 1, 2), "5.1.2-0+deb12u1"),
    ("ffmpeg version 6.0-essentials_build-www.gyan.dev Copyright",
     (6, 0, 0), "6.0-essentials_build-www.gyan.dev"),
    ("ffmpeg version n7.1 Copyright (c) 2000-2024 the FFmpeg developers",
     (7, 1, 0), "n7.1"),
    ("ffmpeg version N-120722-g230fafe68a Copyright (c) 2000-2025",
     None, "N-120722-g230fafe68a"),
    ("ffmpeg version 2023-05-31-git-2d0f0f4 Copyright (c) 2000-2023",
     None, "2023-05-31-git-2d0f0f4"),
    ("", None, ""),
]
wrong = [(line[:40], m.version_from_line(line), (want, said))
         for line, want, said in LINES
         if m.version_from_line(line) != (want, said)]
check("every version line real builds write is read as it stands",
      not wrong, "%d of %d lines read wrongly: %s"
      % (len(wrong), len(LINES), wrong[:2] or "none"))

# A build with a commit where the number should be is not proof of
# anything, and a tool that answers nothing is not either.
check("a build with no number in it yields no version",
      m.version_from_line(
          "ffmpeg version N-120722-g230fafe68a Copyright")[0] is None,
      "read %r, wanted None"
      % (m.version_from_line("ffmpeg version N-120722-g230fafe68a "
                             "Copyright")[0],))

# ---------------------------------------------------------------- the floor
check("the floor is ffmpeg 8.1.2", m.FFMPEG_FLOOR == (8, 1, 2),
      "the program says %s, this test %s"
      % (m.version_text(m.FFMPEG_FLOOR), "8.1.2"))
check("8.1.1 is under the floor and 8.1.2 is not",
      (8, 1, 1) < m.FFMPEG_FLOOR <= (8, 1, 2),
      "floor %s" % m.version_text(m.FFMPEG_FLOOR))

# ------------------------------------------------- what the decision makes
# The two tools are asked by name, so they are driven by name here --
# no binary anywhere, which is the only way this can run on a machine
# that has one ffmpeg and no way to put another beside it.
real_version = m.tool_version
real_soxr = m.soxr_available
empty = tempfile.mkdtemp(prefix="vpm_noffmpeg_")
old_path = os.environ.get("PATH", "")


def decide(answers, soxr=True):
    """find_required_tools() with the tools answering what they are told.

    soxr is driven as well as the version, although the decision does
    not ask about it any more. That is the point: the check below is
    then a statement about the program and not about the ffmpeg of the
    machine underneath, which here has no soxr and elsewhere may.
    """
    m.tool_version = lambda tool: answers[tool]
    m.soxr_available = lambda: soxr
    try:
        return m.find_required_tools()
    finally:
        m.tool_version = real_version
        m.soxr_available = real_soxr


new = ((8, 1, 2), "8.1.2")
old = ((8, 0, 0), "8.0-tessus")
none = (None, "N-120722-g230fafe68a")

kind, says = decide({"ffmpeg": new, "ffprobe": new})
check("a pair at the floor lets the run start", kind == "",
      "said %r, %r -- wanted nothing" % (kind, says))

kind, says = decide({"ffmpeg": old, "ffprobe": new})
check("one old tool stops the run", kind == "old",
      "said %r, wanted 'old'" % kind)
check("and the sentence names the old one and not its neighbour",
      "ffmpeg 8.0-tessus" in says and "ffprobe" not in says, says)
check("and the sentence says what is needed",
      m.version_text(m.FFMPEG_FLOOR) in says, says)

kind, says = decide({"ffmpeg": new, "ffprobe": old})
check("the other one being old stops the run just as well",
      kind == "old" and "ffprobe 8.0-tessus" in says,
      "said %r, %r" % (kind, says))

kind, says = decide({"ffmpeg": none, "ffprobe": new})
check("a version that cannot be read is not a version above the floor",
      kind == "old" and "N-120722-g230fafe68a" in says,
      "said %r, %r" % (kind, says))

# ------------------------------------------------------------- soxr
# Not a second condition, and this is where that is pinned down. soxr
# is what the fine clock correction is made of: without it the drift
# comes out in steps of 21 ppm instead of 0.21, a hundred times
# coarser. Coarser is not broken, though, and Homebrew offers no build
# that has soxr -- so such a build runs, and rate_filter_chain says
# once what it costs. Anybody putting the refusal back finds this red.
kind, says = decide({"ffmpeg": new, "ffprobe": new}, soxr=False)
check("an ffmpeg at the floor built without soxr still lets the run start",
      kind == "", "said %r, %r -- wanted nothing, because a coarser clock "
      "correction is a note and not a reason to refuse" % (kind, says))

# ----------------------------------------- what brew is offered, exactly
# Measured on 4.9.2026: homebrew/core builds ffmpeg without soxr, and
# the ffmpeg on this machine comes from the tap homebrew-ffmpeg/ffmpeg,
# where libsoxr is optional and has to be asked for by name. A plain
# "brew install ffmpeg" therefore installs exactly what the program
# complains about a moment later. Driven, not read off this machine, so
# the judgement is the same on a builder that has no brew.
class OnlyBrew:
    """A search path with brew on it and nothing else."""

    @staticmethod
    def which(name):
        return "/opt/homebrew/bin/brew" if name == "brew" else None


was_shutil, was_platform = m.shutil, m.sys.platform
try:
    m.shutil = OnlyBrew()
    m.sys.platform = "darwin"
    mac_install = m.package_manager_command()
    mac_again = m.package_manager_command(update=True)
finally:
    m.shutil, m.sys.platform = was_shutil, was_platform
# Written out twice rather than looped: a check whose wording is worked
# out at run time cannot be found in state/counterproof, which reads
# the wording out of the source.
# What the button mends is the version. The tap that carries soxr has
# no bottle at all -- measured 4.9.2026, brew info answers with none --
# so offering it would compile in the window's own thread, minutes to
# an hour, for a want that is a note and not a refusal.
WRONG = ("it offers %r -- the tap has no bottle, so this button would "
         "compile in the window's own thread")
check("the brew command to install ffmpeg offers the bottle, not the tap",
      "ffmpeg" in mac_install and "homebrew-ffmpeg/ffmpeg/ffmpeg"
      not in mac_install, WRONG % (" ".join(mac_install),))
check("the brew command to build it again offers the bottle, not the tap",
      "ffmpeg" in mac_again and "homebrew-ffmpeg/ffmpeg/ffmpeg"
      not in mac_again, WRONG % (" ".join(mac_again),))
check("installing and building it again are different brew commands",
      mac_install != mac_again,
      "both are %r -- told to install what is already there brew answers "
      "'already installed' and does nothing" % (" ".join(mac_install),))

# --------------------------------- the window offers what the console does
# Two places build the command -- tools_repaired for the console,
# tools_offer for the box on the window -- and they were found saying
# different things: the box offered "install" for a build that is there
# and only made wrong, which a manager answers "already installed" to.
# The box is driven through a stand-in rather than a screen: it records
# what it was given and clicks nothing, so no manager is ever started.
class Button:
    def __init__(self, text):
        self.written = text


class Box:
    """A message box that keeps what it was shown and presses nothing."""

    def __init__(self, parent):
        self.buttons, self.shown, self.title, self.under = [], "", "", ""
        Box.made.append(self)

    def setWindowTitle(self, text):
        self.title = text

    def setText(self, text):
        self.shown = text

    def setInformativeText(self, text):
        self.under = text

    def addButton(self, text, role):
        self.buttons.append(Button(text))
        return self.buttons[-1]

    def exec(self):
        return 0

    def clickedButton(self):
        return None


Box.AcceptRole = 0
Box.RejectRole = 1
Box.made = []


class Widgets:
    QMessageBox = Box


class Application:
    def __init__(self):
        self.quit_asked = 0

    def quit(self):
        self.quit_asked += 1


was_qt, was_trouble = m._qt_widgets, m.TOOL_TROUBLE
boxes = {}
try:
    m._qt_widgets = lambda: Widgets
    m.shutil, m.sys.platform = OnlyBrew(), "darwin"
    for kind, sentence in (("missing", "ffmpeg, ffprobe is missing."),
                           ("old", "Here: ffmpeg 8.0-tessus.")):
        m.TOOL_TROUBLE = (kind, sentence)
        Box.made = []
        app = Application()
        m.tools_offer(None, app)
        boxes[kind] = (Box.made[-1] if Box.made else Box(None), app)
finally:
    m._qt_widgets, m.TOOL_TROUBLE = was_qt, was_trouble
    m.shutil, m.sys.platform = was_shutil, was_platform


def offered(kind):
    """The command the box's Get-it button holds, or ""."""
    for button in boxes[kind][0].buttons:
        if ":" in button.written:
            return button.written.split(":", 1)[1].strip()
    return ""


check("the box offers installing where there is no ffmpeg at all",
      offered("missing") == " ".join(mac_install),
      "the box offers %r, the console %r"
      % (offered("missing"), " ".join(mac_install)))
check("the box offers building it again where one is there but too old",
      offered("old") == " ".join(mac_again),
      "the box offers %r, the console %r"
      % (offered("old"), " ".join(mac_again)))
# Two claims, so two checks: a conjunction only one half of which has
# ever been seen red says nothing about the other half.
SAID = ["ffmpeg, ffprobe is missing.", "Here: ffmpeg 8.0-tessus."]
check("the box shows the complaint itself, not a wording of its own",
      [box.shown for box, _a in boxes.values()] == SAID,
      "shown %r, wanted %r"
      % ([b.shown[:34] for b, _a in boxes.values()],
         [s[:34] for s in SAID]))
check("and the run ends behind the box, whatever was answered",
      [app.quit_asked for _b, app in boxes.values()] == [1, 1],
      "quit asked %r -- what the start looked for has changed under it, "
      "so a window left standing would go on with the old answer"
      % ([a.quit_asked for _b, a in boxes.values()],))

# Nothing on the path at all: the older complaint, and it must still work.
os.environ["PATH"] = empty
try:
    kind, says = m.find_required_tools()
finally:
    os.environ["PATH"] = old_path
check("with neither tool anywhere the complaint is that they are missing",
      kind == "missing" and "ffmpeg" in says and "ffprobe" in says,
      "said %r, %r" % (kind, says))

# --------------------------------------------------- install against lift
install = m.package_manager_command()
lift = m.package_manager_command(update=True)
if not install:
    print("LEFT OUT: no package manager on this machine, so the two "
          "commands cannot be compared -- install one, or run this "
          "where brew, apt-get, dnf, zypper or pacman is on PATH.")
else:
    check("lifting an ffmpeg that is there is a different command "
          "from installing one", install != lift or "pacman" in install,
          "install %r, lift %r -- told to install what is already "
          "there, a manager answers 'already installed' and does nothing"
          % (" ".join(install), " ".join(lift)))

# ------------------------------------------------------- the ways out
env = dict(os.environ)
env.update({"LANG": "C", "LC_ALL": "C", "LANGUAGE": "en",
            "VPM_SILENT": "1", "VPM_NO_UPDATE_CHECK": "1",
            # An empty folder and nothing else, so the child finds no
            # ffmpeg at all -- the shut gate in its harshest form. In
            # front of the real path it would not be shut: the real
            # ffmpeg is still reachable behind it, and the two checks
            # below would then answer about a gate that never closed.
            # Python itself is started by its full path and needs none.
            "PATH": empty})


def started(*more):
    """Run the program with those arguments. (return code, first lines)."""
    p = subprocess.run([sys.executable, SCRIPT] + list(more),
                       capture_output=True, env=env, stdin=subprocess.DEVNULL)
    text = (p.stdout or b"").decode("utf-8", "replace")
    return p.returncode, " ".join(text.split())[:150]


code, text = started("--version")
check("--version still answers while the gate is shut",
      code == 0 and m.VERSION in text,
      "return code %d, said %r, wanted the version %s in it"
      % (code, text[:60], m.VERSION))

code, text = started("--help")
check("--help still answers while the gate is shut",
      code == 0 and "usage" in text.lower(),
      "return code %d, said %r" % (code, text[:60]))

# --update is the way out of a broken installation, so it must not fail
# on the very thing it repairs. VPM_NO_UPDATE_CHECK is in the
# environment above, so it reaches its own refusal and says so instead
# of fetching anything -- which is proof enough that it got past the
# gate, and costs no network.
SWITCHED_OFF = m.T('The check for new versions is switched off here.')
code, text = started("--update")
check("--update still answers while the gate is shut",
      SWITCHED_OFF in text,
      "return code %d, said %r, wanted %r -- an --update stopped by the "
      "gate cannot repair the installation the gate is complaining about"
      % (code, text[:80], SWITCHED_OFF))

shutil.rmtree(empty, ignore_errors=True)
print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
