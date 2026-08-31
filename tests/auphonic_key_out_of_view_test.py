# -*- coding: utf-8 -*-
"""Nobody else can read the key: not in the process list, not left behind.

Every call to auphonic.com goes through _curl_call, and no test watched
it. curl is never started: the place that starts a process is stood in
for and reads what it was handed -- the arguments, the environment, and
the file behind --config while it still exists, because the program
removes it the moment curl is back. The sections: the quiet call, the
two ways one can go wrong, the transfer with a bar, what is left lying
about, and the project file. The key store is stood in for too, the key
is plainly invented, and no line prints it -- only where it stood.
"""
import io
import json
import os
import stat
import subprocess
import sys
import tempfile
import time

began = time.time()

HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = os.environ.get("VPM_SCRIPT") or os.path.join(
    os.path.dirname(HERE), "videopodcast-magic.py")

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
os.environ["VPM_NO_UPDATE_CHECK"] = "1"

import importlib.util
spec = importlib.util.spec_from_file_location("vpm", SCRIPT)
vpm = importlib.util.module_from_spec(spec)
sys.modules["vpm"] = vpm
spec.loader.exec_module(vpm)
vpm.set_language("en")

# Unmistakably invented, and it survives the program's escaping
# untouched: no backslash, no quotation mark, no space, so what is
# written into the config file is this string character for character.
KEY = "NOT-A-REAL-KEY-videopodcast-magic-test-only"
# A host that resolves nowhere, so even a stand-in that failed could not
# reach auphonic.com. One strand did reach it once by accident.
URL = "https://vpm-test.invalid/api/info.json"

done = 0
bad = []


def check(name, ok, extra=""):
    global done
    done += 1
    # The key must not stand in a report that travels. Only the place it
    # was found is ever named, and this is the second lock on that.
    name = str(name).replace(KEY, "<the key>")
    extra = str(extra).replace(KEY, "<the key>")
    print("  %-64s %s %s" % (name, "ok" if ok else "FAIL", extra))
    if not ok:
        bad.append("%s [%s]" % (name, extra or "no numbers"))


def stop():
    """Every way out passes the count and the return code."""
    print("\n%d checks in %.2f s" % (done, time.time() - began))
    print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
    sys.exit(1 if bad else 0)


# ---------------------------------------------------------------- ground
#
# The key store of this machine holds the real key, so nothing here may
# go near it. Both ways in are replaced; the stand-in for subprocess
# below would already stop them, and this says so a second time.
vpm._ask_key_store = lambda: ""
vpm.load_api_key = lambda: ""
vpm.store_api_key = lambda key: False
vpm.delete_api_key = lambda: False
# The bar would draw over the report, and nothing here is about the bar.
vpm.show_progress = lambda text, share=None: None


class Started(object):
    """One start of a program, read while its config file still exists."""

    def __init__(self, argv, kwargs):
        self.argv = ([str(x) for x in argv]
                     if isinstance(argv, (list, tuple)) else [str(argv)])
        self.shell = bool(kwargs.get("shell"))
        # What curl would inherit: an env of its own if one was handed
        # over, otherwise the environment of this process.
        given = kwargs.get("env")
        self.env = dict(given) if given is not None else dict(os.environ)
        self.out_file = getattr(kwargs.get("stdout"), "name", None)
        self.conf = None
        if "--config" in self.argv:
            at = self.argv.index("--config")
            if at + 1 < len(self.argv):
                self.conf = self.argv[at + 1]
        self.conf_there = bool(self.conf) and os.path.exists(self.conf)
        self.conf_mode = None
        self.conf_text = ""
        if self.conf_there:
            self.conf_mode = stat.S_IMODE(os.stat(self.conf).st_mode)
            with open(self.conf, "rb") as fh:
                self.conf_text = fh.read().decode("utf-8", "replace")


STARTS = []
PLAN = {"code": 0, "raise": None, "break_off": False}


class Broken(object):
    """curl's error channel, torn off after the first piece."""

    def __init__(self):
        self.left = 1

    def read(self, _n):
        if self.left:
            self.left = 0
            return b"  0  100    0    0\r"
        raise IOError("the transfer broke off")


class FakePopen(object):
    def __init__(self, argv, **kwargs):
        STARTS.append(Started(argv, kwargs))
        self.args = list(argv)
        self.returncode = None
        sink = kwargs.get("stdout")
        if sink is not None and hasattr(sink, "write"):
            sink.write(b'{"ok": 1}')
            sink.flush()
        self.stderr = (Broken() if PLAN["break_off"] else
                       io.BytesIO(b"  0  100    0    0\r"
                                 b"100  100    0    0\r"))

    def wait(self, timeout=None):
        self.returncode = PLAN["code"]
        return self.returncode

    def poll(self):
        return self.returncode

    def kill(self):
        self.returncode = -9


def fake_run(argv, **kwargs):
    STARTS.append(Started(argv, kwargs))
    if PLAN["raise"] is not None:
        raise PLAN["raise"]
    return subprocess.CompletedProcess(
        argv, PLAN["code"], b'{"ok": 1}', b"curl: (22) the server said no")


class NoSubprocess(object):
    """Everything the program looks for in subprocess, and no process."""

    PIPE = subprocess.PIPE
    STDOUT = subprocess.STDOUT
    DEVNULL = subprocess.DEVNULL
    CompletedProcess = subprocess.CompletedProcess
    TimeoutExpired = subprocess.TimeoutExpired
    CalledProcessError = subprocess.CalledProcessError
    SubprocessError = subprocess.SubprocessError
    run = staticmethod(fake_run)
    Popen = staticmethod(FakePopen)
    call = staticmethod(fake_run)
    check_output = staticmethod(fake_run)


# Only the name inside the program is rebound, so the test itself keeps
# the real module and nothing the program starts can leave this process.
vpm.subprocess = NoSubprocess


def call(**kw):
    """One call through the channel; what it raised, or None."""
    try:
        vpm._curl_call(KEY, [URL], **kw)
    except BaseException as why:      # every way out is a finding here
        return why
    return None


# ------------------------------------------------------- 1. A quiet call
print("1. The quiet call")

call()
call()
if len(STARTS) < 2:
    check("the channel starts a program at all", False,
          "%d starts against 2 calls" % len(STARTS))
    stop()
first, second = STARTS[0], STARTS[1]

check("the channel starts a program at all", len(STARTS) == 2,
      "%d starts against 2 calls" % len(STARTS))
check("the channel starts curl itself, with no shell in between",
      first.argv[:1] == ["curl"] and not first.shell,
      "started %r, shell %s" % (first.argv[0] if first.argv else "-",
                                first.shell))

holds = KEY in first.conf_text
check("the key is written into the config file curl is pointed at",
      first.conf_there and holds,
      "config file %s, %d bytes, the key %s"
      % ("there" if first.conf_there else "missing", len(first.conf_text),
         "in it" if holds else "in none of them"))

on_line = [i for i, one in enumerate(first.argv) if KEY in one]
check("no argument on curl's command line is the key", not on_line,
      "%d arguments, %s"
      % (len(first.argv), "none carries it" if not on_line
         else "argument %d of them carries it" % on_line[0]))

in_env = sorted(n for n, v in first.env.items() if KEY in str(v))
check("no environment variable curl inherits carries the key", not in_env,
      "%d variables, %s"
      % (len(first.env), "none carries it" if not in_env
         else "the one called %s carries it" % in_env[0]))

check("the config file may be read by its owner alone",
      first.conf_mode == 0o600,
      "mode %s against 0600"
      % ("none -- no config file" if first.conf_mode is None
         else "0%o" % first.conf_mode))

# The one file that holds the key belongs where the system keeps what a
# run throws away -- not beside the program, the working folder or the
# home folder, which get backed up, synced and packed into an archive.
TEMP_ROOT = os.path.realpath(tempfile.gettempdir())
BESIDE = [os.path.realpath(os.path.dirname(os.path.abspath(vpm.__file__))),
          os.path.realpath(os.getcwd()),
          os.path.realpath(os.path.expanduser("~"))]
folder = os.path.realpath(os.path.dirname(first.conf or "."))
check("the config file lies in the temporary folder, nowhere that is kept",
      bool(first.conf) and folder == TEMP_ROOT and folder not in BESIDE,
      "it lies in %s, and the temporary folder is %s" % (folder, TEMP_ROOT))

check("two calls do not share one config file name",
      bool(first.conf) and bool(second.conf) and first.conf != second.conf,
      "%s and %s" % (os.path.basename(first.conf or "-"),
                     os.path.basename(second.conf or "-")))

check("the config file is gone when the call has returned",
      bool(first.conf) and not os.path.exists(first.conf),
      "%s is %s" % (first.conf,
                    "still there" if first.conf
                    and os.path.exists(first.conf) else "gone"))

# --------------------------------------------- 2. When the call goes wrong
print("\n2. When the call goes wrong")

PLAN["code"] = 22
why = call()
PLAN["code"] = 0
failed = STARTS[-1]
check("a call curl reports as failed comes back as a fault",
      isinstance(why, RuntimeError),
      "return code 22, raised %s"
      % (type(why).__name__ if why is not None else "nothing"))
check("after a failed call the config file is gone",
      bool(failed.conf) and not os.path.exists(failed.conf),
      "%s is %s" % (failed.conf,
                    "still there" if failed.conf
                    and os.path.exists(failed.conf) else "gone"))

PLAN["raise"] = OSError("there is no curl on this machine")
why = call()
PLAN["raise"] = None
threw = STARTS[-1]
check("a call that cannot start at all comes back as a fault",
      isinstance(why, OSError),
      "raised %s" % (type(why).__name__ if why is not None else "nothing"))
check("after a call that could not start the config file is gone",
      bool(threw.conf) and not os.path.exists(threw.conf),
      "%s is %s" % (threw.conf,
                    "still there" if threw.conf
                    and os.path.exists(threw.conf) else "gone"))

# ------------------------------------------------------- 3. The transfer
print("\n3. The transfer with a progress bar")

call(progress="Uploading")
moved = STARTS[-1]
on_line = [i for i, one in enumerate(moved.argv) if KEY in one]
check("no argument on a transfer's command line is the key", not on_line,
      "%d arguments, %s"
      % (len(moved.argv), "none carries it" if not on_line
         else "argument %d of them carries it" % on_line[0]))
check("a transfer's config file may be read by its owner alone",
      moved.conf_mode == 0o600,
      "mode %s against 0600"
      % ("none -- no config file" if moved.conf_mode is None
         else "0%o" % moved.conf_mode))
check("a transfer that finished leaves no config file",
      bool(moved.conf) and not os.path.exists(moved.conf),
      "%s is %s" % (moved.conf,
                    "still there" if moved.conf
                    and os.path.exists(moved.conf) else "gone"))

PLAN["break_off"] = True
why = call(progress="Uploading")
PLAN["break_off"] = False
torn = STARTS[-1]
check("a transfer that breaks off in the middle comes back as a fault",
      why is not None,
      "raised %s" % (type(why).__name__ if why is not None else "nothing"))
check("a transfer that broke off leaves no config file",
      bool(torn.conf) and not os.path.exists(torn.conf),
      "%s is %s" % (torn.conf,
                    "still there" if torn.conf
                    and os.path.exists(torn.conf) else "gone"))
check("a transfer that broke off leaves no answer file",
      bool(torn.out_file) and not os.path.exists(torn.out_file),
      "%s is %s" % (torn.out_file,
                    "still there" if torn.out_file
                    and os.path.exists(torn.out_file) else "gone"))

# ------------------------------------------- 4. What is left lying about
print("\n4. What is left lying about")

# The count in this line is the finding, not the verdict: a transfer
# that ran to the end does leave its answer file behind, because the
# fallback that overwrites a file it could not remove also writes a new
# one where the normal path had already removed it. What is left holds
# one newline and no key, so the rule stands and this says so with a
# number beside it.
made = [p for one in STARTS for p in (one.conf, one.out_file) if p]
survivors = [p for p in made if os.path.exists(p)]
leaky = []
for path in survivors:
    try:
        with io.open(path, "rb") as fh:
            if KEY.encode("utf-8") in fh.read():
                leaky.append(path)
    except OSError:
        pass
check("no file this channel left behind holds the key", not leaky,
      "%d of the %d files it made are still there, %s"
      % (len(survivors), len(made),
         "none holds the key" if not leaky
         else "the one at %s holds it" % leaky[0]))

# Counted first, then swept: what the program made under this test is
# this test's to take away again, and only that.
for path in survivors:
    try:
        os.unlink(path)
    except OSError:
        pass

# --------------------------------------------------- 5. The project file
print("\n5. The project file")

# project_write sits inside gui() and cannot be called from out here, so
# its own body is cut out of the source and run for real against a
# folder of its own: the file that comes out is the one the program
# writes, not a copy of the rule in another shape.
with io.open(SCRIPT, encoding="utf-8") as fh:
    source = fh.read()


def lifted(name):
    """The source of a nested function, dedented to the left margin."""
    lines = source.split("\n")
    at = [i for i, x in enumerate(lines)
          if x.strip().startswith("def %s(" % name)]
    if not at:
        return ""
    room = len(lines[at[0]]) - len(lines[at[0]].lstrip())
    out = [lines[at[0]][room:]]
    for x in lines[at[0] + 1:]:
        if x.strip() and len(x) - len(x.lstrip()) <= room:
            break
        out.append(x[room:])
    return "\n".join(out)


room = tempfile.mkdtemp(prefix="vpm_key_view_")
project_path = os.path.join(room, "podcast.vpm")
ARGV = ["videopodcast-magic.py", "--out", room,
        "--auphonic-api-key", KEY, "--auphonic-preset", "podcast"]

body = lifted("project_write")
around = {"project_move": lambda: None,
          "axis_file": lambda: project_path,
          "project_collect": lambda p: {},
          "settings_extend": lambda d: d.update({"production": "Test"}),
          "FILE_FORMAT": vpm.FILE_FORMAT,
          "VERSION": vpm.VERSION,
          "files": [(os.path.join(room, "a.mov"), "camera")],
          "state": {"axis_absolute": False},
          "json": json,
          "write": lambda text: None,
          "as_head": lambda text: text,
          "T": vpm.T}
if body:
    exec(compile(body, "project_write", "exec"), around)
    around["project_write"](ARGV)

written = ""
if os.path.exists(project_path):
    with io.open(project_path, encoding="utf-8") as fh:
        written = fh.read()
check("a project file is written at all, so there is something to read",
      len(written) > 0,
      "%d bytes at %s, project_write %s"
      % (len(written), project_path, "lifted" if body else "not found"))

stored = []
try:
    stored = json.loads(written).get("call") or []
except ValueError:
    pass
check("the call stored in the project file drops the key's switch",
      "--auphonic-api-key" not in stored and "--auphonic-preset" in stored,
      "the call it wrote: %s" % (stored,))

at = written.find(KEY)
check("no character of the project file is the key", at < 0,
      "%d bytes, %s" % (len(written), "the key is in none of them" if at < 0
                        else "the key stands at byte %d" % at))

try:
    os.unlink(project_path)
    os.rmdir(room)
except OSError:
    pass

stop()
