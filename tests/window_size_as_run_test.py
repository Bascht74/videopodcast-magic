# -*- coding: utf-8 -*-
"""The window's summary names the size the run really needs.

"One reckoning" holds the summary's size against the preflight's for the
same call, "the time window" does it again with a window and watches the
number come down, and "the summary itself" reads the line out of the
window the Start button opens. Free space is read twice and can differ
by a byte, so only the size is compared.
"""
import os
HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = os.environ.get("VPM_SCRIPT") or os.path.join(
    os.path.dirname(HERE), "videopodcast_magic.py")
import collections, importlib.util, json, re, sys, time
os.environ["QT_QPA_PLATFORM"] = "offscreen"
from PySide6 import QtWidgets, QtCore
app = QtWidgets.QApplication(sys.argv[:1])
spec = importlib.util.spec_from_file_location("vpm", SCRIPT)
vpm = importlib.util.module_from_spec(spec); sys.modules["vpm"] = vpm
spec.loader.exec_module(vpm)
vpm.set_language("en")
vpm.list_presets = lambda key: [("Podcast_Multitrack", "u1", True)]
vpm.load_api_key = lambda: ""
sys.path.insert(0, HERE)
from fixture_project import fixture_project

began = time.time()
done = 0
bad = []


def check(name, ok, extra=""):
    global done
    done += 1
    print("  %-58s %s %s" % (name, "ok" if ok else "FAIL", extra))
    if not ok:
        bad.append("%s [%s]" % (name, extra or "no numbers"))


def stop():
    """Every way out passes the count and the return code."""
    print("\n%d checks in %.2f s" % (done, time.time() - began))
    print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
    sys.exit(1 if bad else 0)


# The window, as the two timecodes a call carries and as the length they
# come to. The cameras of the fixture run two minutes from 18:55, so this
# is a small part of every one of them.
IN_POINT, OUT_POINT = "18:56:00:00", "18:56:05:00"
WINDOW_S = 5.0

PROJECT, MEDIA = fixture_project("sizeasrun")
if PROJECT is None:
    # Not a pass: run.sh reads the marker and counts this as skipped.
    print("SKIPPED: no test project -- point VPM_MEDIA at a folder "
          "holding videopodcast-magic_Interview_2.json (looked in %s)" % MEDIA)
    stop()
with open(PROJECT, encoding="utf-8") as f:
    plan = json.load(f)
plan["in_point"], plan["out_point"] = IN_POINT, OUT_POINT
with open(PROJECT, "w", encoding="utf-8") as f:
    json.dump(plan, f, indent=1)
TARGET = plan["out_folder"]
AUDIO = [e["path"] for e in plan["files"] if e["kind"] == "audio"]
VIDEO = [e["path"] for e in plan["files"] if e["kind"] == "video"]

Usage = collections.namedtuple("Usage", "total used free")
FREE_MB = 1e9
real_usage = vpm.shutil.disk_usage
real_one_disk = vpm.on_one_disk
real_size = vpm.as_data_size


def sizes(text):
    """The megabyte figures a sentence carries, in the order they stand.

    While these two are asked, as_data_size hands back the bare number
    in a marker instead of a rounded phrase, so the two sentences can be
    compared without either side being read back through the rounding.
    """
    return [float(x) for x in re.findall(r"<([0-9.]+)>", text)]


def summary_size(window=True):
    """What the summary before the run says the run writes, in MB."""
    lines = vpm.space_summary_lines(
        TARGET, AUDIO, VIDEO, True,
        IN_POINT if window else "", OUT_POINT if window else "")
    got = sizes(lines[0])
    return got[0] if got else None


def preflight_size(window=True):
    """What the preflight says the same call needs, in MB.

    The temporary files are told to live on another disk, so what is
    left is what lands in the target folder -- which is what the summary
    is about.
    """
    found = vpm.check_disk_space(TARGET, AUDIO, VIDEO, True,
                                 WINDOW_S if window else None)
    got = sizes(found[0].text) if found else []
    # "free %s, about %s needed": the second figure is the estimate.
    return got[1] if len(got) > 1 else None


vpm.shutil.disk_usage = lambda _p: Usage(0, 0, FREE_MB * 1e6)
vpm.on_one_disk = lambda _a, _b: False
vpm.as_data_size = lambda mb: "<%.6f>" % mb
try:
    open_summary, open_preflight = summary_size(False), preflight_size(False)
    cut_summary, cut_preflight = summary_size(True), preflight_size(True)
finally:
    vpm.shutil.disk_usage = real_usage
    vpm.on_one_disk = real_one_disk
    vpm.as_data_size = real_size

print("1. One reckoning, not two")
check("the preflight reaches a size at all", open_preflight is not None,
      "%r cameras and %r recordings gave %r"
      % (len(VIDEO), len(AUDIO), open_preflight))
check("the summary names the size the preflight counts",
      open_summary is not None and open_preflight is not None
      and abs(open_summary - open_preflight) < 0.001,
      "the summary says %r MB, the preflight %r MB"
      % (open_summary, open_preflight))

print("\n2. And with a time window")
check("the summary names it with a time window too",
      cut_summary is not None and cut_preflight is not None
      and abs(cut_summary - cut_preflight) < 0.001,
      "over %.1f s the summary says %r MB, the preflight %r MB"
      % (WINDOW_S, cut_summary, cut_preflight))
check("a time window brings the summary's size down",
      cut_summary is not None and open_summary is not None
      and cut_summary < open_summary / 2.0,
      "%r MB over a window of %.1f s against %r MB over the whole shoot"
      % (cut_summary, WINDOW_S, open_summary))

print("\n3. The summary the Start button opens")
QtWidgets.QFileDialog.getOpenFileName = staticmethod(
    lambda *a, **k: (PROJECT, ""))
QtWidgets.QDialog.exec = lambda self: QtWidgets.QDialog.Accepted
QtWidgets.QMessageBox.exec = lambda self: QtWidgets.QMessageBox.Ok
seen = {}


def say_dialog(QtWidgets_, window, title, text, do_text="", no_text=""):
    """Catch the summary instead of showing it, and answer Cancel."""
    if title == vpm.T('This is what happens next'):
        seen["summary"] = text
    return False


vpm.say_dialog = say_dialog
import subprocess, threading
real_thread = threading.Thread


def fake_thread(target=None, args=(), daemon=None, **rest):
    """Hold back the program's own threads, let subprocess keep its."""
    if isinstance(getattr(target, "__self__", None), subprocess.Popen):
        return real_thread(target=target, args=args, daemon=daemon, **rest)

    class Held(object):
        daemon = False

        def start(self_):
            pass

        def join(self_, timeout=None):
            pass

        def is_alive(self_):
            return False

    return Held()


threading.Thread = fake_thread


def win():
    for x in app.topLevelWidgets():
        if "Video Podcast Magic" in x.windowTitle():
            return x


def button(text):
    where = win()
    for b in (where.findChildren(QtWidgets.QPushButton) if where else []):
        if b.text().strip().startswith(text):
            return b


step = [0]
tries = [0]
since = [0.0]
waited = [0.0]


def carry_on():
    """Open the project, then press Start and let the summary come up."""
    i = step[0]; step[0] += 1
    try:
        if i == 0:
            # Waited for, not slept past: how long the window takes to
            # build depends on the machine.
            if (win() is None or button(vpm.T('Open project')) is None) \
                    and tries[0] < 500:
                tries[0] += 1
                step[0] = 0
                QtCore.QTimer.singleShot(20, carry_on)
                return
            win().show(); app.processEvents()
        elif i == 1:
            button(vpm.T('Open project')).click()
        elif i == 2:
            k = button(vpm.T('Start'))
            if not since[0]:
                since[0] = time.time()
            waited[0] = time.time() - since[0]
            if k is not None and not k.isEnabled() and waited[0] < 120:
                step[0] = 2
                QtCore.QTimer.singleShot(100, carry_on)
                return
            if k is not None and k.isEnabled():
                k.click()
        elif i == 3:
            app.quit(); return
    except Exception:
        import traceback; traceback.print_exc(); app.quit(); return
    QtCore.QTimer.singleShot(50, carry_on)


QtCore.QTimer.singleShot(0, carry_on)
QtCore.QTimer.singleShot(300000, app.quit)
sys.argv = ["videopodcast_magic.py"]
vpm.gui()
threading.Thread = real_thread

shown = seen.get("summary") or ""
check("the summary came up when Start was pressed", bool(shown),
      "%d characters of summary after %.0f s of waiting"
      % (len(shown), waited[0]))
want = vpm.space_summary_lines(TARGET, AUDIO, VIDEO, True,
                               IN_POINT, OUT_POINT)[0]
check("and the line it shows is the one reckoning",
      want in shown,
      "wanted %r, and the summary reads %r" % (want[:70], shown[-160:]))

vpm.shutil.rmtree(os.path.dirname(PROJECT), ignore_errors=True)
stop()
