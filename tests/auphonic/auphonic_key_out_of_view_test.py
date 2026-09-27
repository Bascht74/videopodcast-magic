# -*- coding: utf-8 -*-
"""Nobody else can read the key: not in the process list, not left behind.

Every call to auphonic.com goes through _curl_call. The place that
starts a process reads what it was handed -- the arguments, the
environment, its input -- and what the temporary folder holds at that
moment. Sections: the quiet call, the two ways one can go wrong, the
transfer with a bar, what is left lying about, the project file, where
a download goes, and a real process in curl's place that reads its
input and looks in the folder itself. The key is invented; no line
prints it.
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
import io
import json
import shutil
import subprocess
import tempfile
import time
import the_program

began = time.time()

SCRIPT = the_program.SCRIPT

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
os.environ["VPM_NO_UPDATE_CHECK"] = "1"

vpm = the_program.load()
vpm.set_language("en")
# Before anything can reach the credential store: all three names of
# it go somewhere throwaway. On a Mac the two keychain names decide,
# and REG_PATH alone moved nothing there.
import key_store_apart
key_store_apart.apart(vpm)

# Unmistakably invented, and it survives the program's escaping
# untouched: no backslash, no quotation mark, no space, so what curl is
# handed on its input carries this string character for character.
KEY = "NOT-A-REAL-KEY-videopodcast-magic-test-only"
# A host that resolves nowhere, so even a stand-in that failed could not
# reach auphonic.com. One strand did reach it once by accident.
URL = "https://vpm-test.invalid/api/info.json"

# The folder the system hands out for what a run throws away: where the
# key lay in a file of its own until b28, and so where it is looked for.
TEMP_ROOT = os.path.realpath(tempfile.gettempdir())

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


def holding_key(root, key=KEY):
    """Every file under *root* whose bytes hold *key*, by name."""
    found = []
    for folder, _dirs, files in os.walk(root):
        for one in files:
            try:
                with io.open(os.path.join(folder, one), "rb") as fh:
                    if key.encode("utf-8") in fh.read():
                        found.append(one)
            except OSError:
                pass
    return found


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
    """One start of a program: what it was handed, and the folder then."""

    def __init__(self, argv, kwargs):
        self.argv = ([str(x) for x in argv]
                     if isinstance(argv, (list, tuple)) else [str(argv)])
        self.shell = bool(kwargs.get("shell"))
        # What curl would inherit: an env of its own if one was handed
        # over, otherwise the environment of this process.
        given = kwargs.get("env")
        self.env = dict(given) if given is not None else dict(os.environ)
        self.out_file = getattr(kwargs.get("stdout"), "name", None)
        # What goes in on its input: handed whole to run(), written into
        # the pipe of a Popen and then closed -- see Input below.
        self.input = kwargs.get("input") or b""
        self.input_closed = kwargs.get("input") is not None
        # Every file in the temporary folder that holds the key while
        # this process starts, which is while curl would read it.
        self.lying = holding_key(TEMP_ROOT)


class Input(io.BytesIO):
    """A Popen's input: what was written, and whether it was closed."""

    def __init__(self, start):
        io.BytesIO.__init__(self)
        self.start = start

    def close(self):
        self.start.input = self.getvalue()
        self.start.input_closed = True
        io.BytesIO.close(self)


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
        start = Started(argv, kwargs)
        STARTS.append(start)
        self.args = list(argv)
        self.returncode = None
        self.stdin = (Input(start) if kwargs.get("stdin") == subprocess.PIPE
                      else None)
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


def on_input(start):
    """Whether *start* was told to read its configuration from its input
    and was handed the key there."""
    at = start.argv.index("--config") if "--config" in start.argv else -1
    return (at >= 0 and start.argv[at + 1:at + 2] == ["-"]
            and KEY.encode("utf-8") in start.input)


# ------------------------------------------------------- 1. A quiet call
print("1. The quiet call")

call()
call()
if len(STARTS) < 2:
    check("the channel starts a program at all", False,
          "%d starts against 2 calls" % len(STARTS))
    stop()
first = STARTS[0]

check("the channel starts a program at all", len(STARTS) == 2,
      "%d starts against 2 calls" % len(STARTS))
check("the channel starts curl itself, with no shell in between",
      first.argv[:1] == ["curl"] and not first.shell,
      "started %r, shell %s" % (first.argv[0] if first.argv else "-",
                                first.shell))

check("the key is handed to curl on its input, as its configuration",
      on_input(first),
      "--config %s, %d bytes on the input, the key %s"
      % ("-" if "-" in first.argv else "not from the input",
         len(first.input),
         "in them" if KEY.encode("utf-8") in first.input else "not in them"))

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

check("no file in the temporary folder holds the key while curl starts",
      not first.lying,
      "%d files in %s hold it%s"
      % (len(first.lying), TEMP_ROOT,
         ": " + first.lying[0] if first.lying else ""))

# --------------------------------------------- 2. When the call goes wrong
print("\n2. When the call goes wrong")

PLAN["code"] = 22
why = call()
PLAN["code"] = 0
check("a call curl reports as failed comes back as a fault",
      isinstance(why, RuntimeError),
      "return code 22, raised %s"
      % (type(why).__name__ if why is not None else "nothing"))

PLAN["raise"] = OSError("there is no curl on this machine")
why = call()
PLAN["raise"] = None
check("a call that cannot start at all comes back as a fault",
      isinstance(why, OSError),
      "raised %s" % (type(why).__name__ if why is not None else "nothing"))

# ------------------------------------------------------- 3. The transfer
print("\n3. The transfer with a progress bar")

call(progress="Uploading")
moved = STARTS[-1]
on_line = [i for i, one in enumerate(moved.argv) if KEY in one]
check("no argument on a transfer's command line is the key", not on_line,
      "%d arguments, %s"
      % (len(moved.argv), "none carries it" if not on_line
         else "argument %d of them carries it" % on_line[0]))
# Closed, or curl waits on its input for more configuration for ever.
check("a transfer hands curl the key on its input and closes it",
      on_input(moved) and moved.input_closed,
      "the key %s, the input %s"
      % ("on the input" if on_input(moved) else "not on the input",
         "closed" if moved.input_closed else "left open"))
check("no file in the temporary folder holds the key while a transfer "
      "starts", not moved.lying,
      "%d files in %s hold it%s"
      % (len(moved.lying), TEMP_ROOT,
         ": " + moved.lying[0] if moved.lying else ""))
check("a transfer that finished leaves no answer file",
      bool(moved.out_file) and not os.path.exists(moved.out_file),
      "%s is %s" % (moved.out_file,
                    "still there" if moved.out_file
                    and os.path.exists(moved.out_file) else "gone"))

PLAN["break_off"] = True
why = call(progress="Uploading")
PLAN["break_off"] = False
torn = STARTS[-1]
check("a transfer that breaks off in the middle comes back as a fault",
      why is not None,
      "raised %s" % (type(why).__name__ if why is not None else "nothing"))
check("a transfer that broke off leaves no answer file",
      bool(torn.out_file) and not os.path.exists(torn.out_file),
      "%s is %s" % (torn.out_file,
                    "still there" if torn.out_file
                    and os.path.exists(torn.out_file) else "gone"))

# ------------------------------------------- 4. What is left lying about
print("\n4. What is left lying about")

# Every temporary file the channel made in this run, held against what
# is still on disk. The count stands in the line whether it falls or
# not, because it is the cheapest way to see litter come back: this
# found the fallback that recreated an answer file the normal path had
# already removed, one per transfer, and would find its like again.
made = [one.out_file for one in STARTS if one.out_file]
survivors = [p for p in made if os.path.exists(p)]
leaky = holding_key(TEMP_ROOT)
check("no file this channel left behind holds the key", not leaky,
      "%d of the %d answer files it made are still there, %d files in "
      "the temporary folder hold the key"
      % (len(survivors), len(made), len(leaky)))

# Counted first, then swept: what the program made under this test is
# this test's to take away again, and only that.
for path in survivors:
    try:
        os.unlink(path)
    except OSError:
        pass

# --------------------------------------------------- 5. The project file
print("\n5. The project file")

# project_write sits inside make_project_file() and cannot be called
# from out here, so its own body is cut out of the source and run for
# real against a folder of its own: the file that comes out is the one
# the program writes, not a copy of the rule in another shape.
source = the_program.whole()


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


class Production(object):
    """What project_write reads off the window's model: the files."""
    files = [(os.path.join(room, "a.mov"), "camera")]


body = lifted("project_write")
around = {"project_move": lambda: None,
          "axis_file": lambda: project_path,
          "project_collect": lambda p: {},
          "settings_extend": lambda d: d.update({"production": "Test"}),
          "FILE_FORMAT": vpm.FILE_FORMAT,
          "VERSION": vpm.VERSION,
          "model": Production(),
          "state": {"axis_absolute": False},
          "json": json,
          "write": lambda text: None,
          "as_head": lambda text: text,
          # Within reach on purpose: since no command line is stored,
          # the store is the only way the key could still get into the
          # file, and a check nothing can break is no check.
          "load_api_key": lambda: KEY,
          "T": vpm.T}
if body:
    exec(compile(body, "project_write", "exec"), around)
    around["project_write"]()

written = ""
if os.path.exists(project_path):
    with io.open(project_path, encoding="utf-8") as fh:
        written = fh.read()
check("a project file is written at all, so there is something to read",
      len(written) > 0,
      "%d bytes at %s, project_write %s"
      % (len(written), project_path, "lifted" if body else "not found"))

# The switch cannot be filtered out of a line that is not written.
# project_write stores no command line, and it is handed none: the two
# checks below say both, because either one alone could come back.
holds = {}
try:
    holds = json.loads(written)
except ValueError:
    pass
check("the project file holds no command line",
      "call" not in holds,
      "keys in it: %s" % (sorted(holds),))
check("and project_write is handed none either",
      "argv" not in body.split("\n")[0],
      "its first line: %s" % (body.split("\n")[0].strip(),))

at = written.find(KEY)
check("no character of the project file is the key", at < 0,
      "%d bytes, %s" % (len(written), "the key is in none of them" if at < 0
                        else "the key stands at byte %d" % at))

try:
    os.unlink(project_path)
    os.rmdir(room)
except OSError:
    pass

# ------------------------------------------ 6. Where a download goes
print("\n6. Where a download goes")

# A download address is the server's word and can name any host. It is
# fetched the way the program fetches it -- fetch_text_outputs, the
# first of the downloading functions -- and what the one start of curl
# was handed is read: its input, the arguments.
fetch_room = tempfile.mkdtemp(prefix="vpm_key_host_")


def fetched_with(url):
    """The start of curl one download to *url* made, or None."""
    before = len(STARTS)
    try:
        with io.StringIO() as said:
            old_out, sys.stdout = sys.stdout, said
            try:
                vpm.fetch_text_outputs(
                    KEY, [{"filename": "chapters.txt", "download_url": url}],
                    fetch_room)
            finally:
                sys.stdout = old_out
    except BaseException:
        pass
    return STARTS[before] if len(STARTS) > before else None


def carries(start):
    """Where in one start of curl the key stands, or "nowhere"."""
    if start is None:
        return "no start"
    if KEY.encode("utf-8") in start.input:
        return "curl's input"
    if any(KEY in one for one in start.argv):
        return "an argument"
    return "nowhere"


home = fetched_with("https://auphonic.com/api/download/chapters.txt")
check("a download from auphonic.com is handed the key",
      carries(home) == "curl's input",
      "the key stands in %s" % carries(home))

foreign = fetched_with("http://127.0.0.1:9/chapters.txt")
check("a download from another host is handed no key",
      carries(foreign) == "nowhere"
      and "--config" not in (foreign.argv if foreign else []),
      "the key stands in %s, --config %s"
      % (carries(foreign), "on the line" if foreign
         and "--config" in foreign.argv else "not on the line"))

# Each of these begins, ends or is spelled like auphonic.com and names
# another host, or the right one without https.
LOOKALIKES = ["https://auphonic.com@vpm-test.invalid/chapters.txt",
              "https://auphonic.com.vpm-test.invalid/chapters.txt",
              "https://vpm-testauphonic.com/chapters.txt",
              "https://vpm-test.invalid/?auphonic.com/chapters.txt",
              "http://auphonic.com/chapters.txt"]
given = [url for url in LOOKALIKES
         if carries(fetched_with(url)) != "nowhere"]
check("an address that only looks like auphonic.com is handed no key",
      not given,
      "%d of %d handed it: %s" % (len(given), len(LOOKALIKES), given))
shutil.rmtree(fetch_room, ignore_errors=True)

# ------------------------------------------ 7. A real process in its place
print("\n7. A real process in curl's place")

# Everything above asked a stand-in in this process. Here a process of
# its own is started where curl would be -- this Python, a script that
# reads its input the way curl reads "--config -" and, while it runs,
# looks through the temporary folder itself. What it saw it writes as
# yes and no, never the key. The key it watches for comes in its
# environment from this test, not from the program.
room = tempfile.mkdtemp(prefix="vpm_key_real_")
STANDIN = os.path.join(room, "curl_reads_input.py")
REPORT = os.path.join(room, "seen.jsonl")
with io.open(STANDIN, "w", encoding="utf-8") as f:
    f.write(r"""
import json, os, sys
args = sys.argv[1:]
key = os.environ["VPM_KEY_WATCH"].encode("utf-8")
handed = sys.stdin.buffer.read() if args[args.index("--config") + 1:][:1] \
    == ["-"] else b""
lying = []
for folder, _d, files in os.walk(os.environ["VPM_KEY_ROOT"]):
    for one in files:
        try:
            with open(os.path.join(folder, one), "rb") as fh:
                if key in fh.read():
                    lying.append(one)
        except OSError:
            pass
with open(os.environ["VPM_KEY_REPORT"], "a") as out:
    out.write(json.dumps({"on_input": key in handed,
                          "in_args": any(key.decode() in a for a in args),
                          "lying": len(lying)}) + "\n")
sys.stderr.write("100  10  100  10    0     0\r")
sys.stdout.write('{"ok": 1}')
""")


def started_here(argv, kwargs):
    """curl's place taken by the script, the key to watch beside it."""
    argv = [sys.executable, STANDIN] + list(argv[1:])
    env = dict(kwargs.pop("env", None) or os.environ)
    env.update({"VPM_KEY_WATCH": KEY, "VPM_KEY_ROOT": TEMP_ROOT,
                "VPM_KEY_REPORT": REPORT})
    return argv, dict(kwargs, env=env)


class RealSubprocess(NoSubprocess):
    """subprocess itself, with the script started where curl was asked."""

    @staticmethod
    def run(argv, **kwargs):
        argv, kwargs = started_here(argv, kwargs)
        return subprocess.run(argv, **kwargs)

    @staticmethod
    def Popen(argv, **kwargs):
        argv, kwargs = started_here(argv, kwargs)
        return subprocess.Popen(argv, **kwargs)


vpm.subprocess = RealSubprocess
quiet_why = call()
moved_why = call(progress="Uploading")
vpm.subprocess = NoSubprocess
seen = []
if os.path.exists(REPORT):
    with io.open(REPORT, encoding="utf-8") as fh:
        seen = [json.loads(one) for one in fh if one.strip()]
check("a real process in curl's place reads the key off its input",
      len(seen) == 2 and all(one["on_input"] for one in seen),
      "%d of %d starts found it on their input; the calls raised %s, %s"
      % (len([one for one in seen if one["on_input"]]), len(seen),
         type(quiet_why).__name__ if quiet_why else "nothing",
         type(moved_why).__name__ if moved_why else "nothing"))
check("while it ran no file in the temporary folder held the key",
      len(seen) == 2 and not any(one["lying"] for one in seen),
      "%s files holding it, per start, in %s"
      % ([one["lying"] for one in seen], TEMP_ROOT))
shutil.rmtree(room, ignore_errors=True)

stop()
