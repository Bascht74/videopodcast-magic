# -*- coding: utf-8 -*-
"""onnxruntime is told to keep quiet before it loads, in both processes.

onnxruntime comes in with the speech recognition's voice filter and with
the speaker separation's pipelines. From its import on it keeps a store
of events under the home folder and a thread that posts them away, and
that thread has aborted Python at exit.

The sections: the recognition, in this process; the separation's
worker; and whether the onnxruntime installed here still reads the
variable the program sets. The first two drive a stand-in onnxruntime
that notes what stood in the environment when it was loaded and what
was called on it, so nothing here reaches the network. The last reads
the installed library's files without loading it, and says LEFT OUT
where there is none.
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
import the_program
SCRIPT = the_program.SCRIPT
import importlib
import importlib.util
import shutil
import tempfile
import time
import types

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
os.environ.setdefault("VPM_NO_SPEAKER_SPLIT", "1")

# Where the real one lies, asked before any stand-in stands in its way,
# and without importing it: an import is what starts the reporting.
try:
    REAL = importlib.util.find_spec("onnxruntime")
except (ImportError, ValueError):
    REAL = None
REAL = os.path.dirname(REAL.origin) if REAL and REAL.origin else None

vpm = the_program.load()
vpm.set_language("en")

began = time.time()
done = 0
bad = []


def check(name, ok, extra=""):
    global done
    done += 1
    print("  %-58s %s %s" % (name, "ok" if ok else "FAIL", extra))
    if not ok:
        bad.append("%s [%s]" % (name, extra or "no numbers"))


WORK = tempfile.mkdtemp(prefix="vpm_onnxquiet_")

# The stand-in: a file, so that importing it runs it, and what it finds
# in the environment at that moment is what the real one would find.
STAND_IN = '''import os
SEEN = {"variables": dict((k, v) for k, v in os.environ.items()
                          if k.startswith("ORT_")),
        "calls": []}
%s
class InferenceSession(object):
    def __init__(self, *args, **kwargs):
        SEEN["calls"].append("session")
'''
SWITCH = '''def disable_telemetry_events():
    SEEN["calls"].append("off")
'''
KINDS = {"whole": STAND_IN % SWITCH,
         "no switch": STAND_IN % "",
         "will not load": "raise ImportError('no onnxruntime here')\n"}


def stand_in(kind):
    """Put an onnxruntime of that kind first on the path, none loaded yet."""
    for name in list(sys.modules):
        if name == "onnxruntime" or name.startswith("onnxruntime."):
            del sys.modules[name]
    for name in list(os.environ):
        if name.startswith("ORT_"):
            del os.environ[name]
    where = os.path.join(WORK, kind.replace(" ", "_"))
    if not os.path.isdir(where):
        os.makedirs(where)
        with open(os.path.join(where, "onnxruntime.py"), "w",
                  encoding="utf-8") as f:
            f.write(KINDS[kind])
    while where in sys.path:
        sys.path.remove(where)
    sys.path.insert(0, where)
    importlib.invalidate_caches()
    return where


def seen():
    """What the stand-in noted, or None where it was never loaded."""
    mod = sys.modules.get("onnxruntime")
    return getattr(mod, "SEEN", None)


class Whisper(object):
    """faster-whisper as far as it touches onnxruntime: a filter session."""

    def __init__(self, *args, **kwargs):
        pass

    def transcribe(self, path, **rest):
        try:
            import onnxruntime
            onnxruntime.InferenceSession("silero_vad.onnx")
        except ImportError:
            pass
        word = types.SimpleNamespace(start=1.0, end=1.4, word=" Tag")
        return [types.SimpleNamespace(words=[word])], None


def recognise(kind):
    """Run the recognition over the stand-ins. (words, what was noted)."""
    where = stand_in(kind)
    fake = types.ModuleType("faster_whisper")
    fake.WhisperModel = Whisper
    was = sys.modules.get("faster_whisper")
    sys.modules["faster_whisper"] = fake
    try:
        words = vpm.whisper_words("/nowhere.wav", "de-DE", install=False)
        return words, seen()
    finally:
        sys.path.remove(where)
        if was is None:
            sys.modules.pop("faster_whisper", None)
        else:
            sys.modules["faster_whisper"] = was


#------------------------------------------------- 1. The recognition

print("1. The speech recognition")

words, noted = recognise("whole")
noted = noted or {"variables": {}, "calls": []}
check("the recognition sets onnxruntime's variable before loading it",
      noted["variables"].get("ORT_DISABLE_TELEMETRY") == "1",
      "onnxruntime found %r in the environment when it loaded, wanted "
      "ORT_DISABLE_TELEMETRY=1 -- afterwards its thread already runs"
      % (noted["variables"],))
check("the recognition throws the switch before a session exists",
      noted["calls"][:1] == ["off"] and "session" in noted["calls"],
      "the calls on onnxruntime went %r, wanted 'off' first and the "
      "filter's session after it" % (noted["calls"],))
PROGRAM_SETS = sorted(noted["variables"])



def recognise_or_fall(kind):
    """The words, and how the run fell where it did: a traceback is no line."""
    try:
        return recognise(kind)[0], ""
    except Exception as e:
        return None, " and fell with %s: %s" % (e.__class__.__name__, e)


words, fell = recognise_or_fall("no switch")
check("the recognition runs on where onnxruntime has no switch",
      bool(words),
      "it gave %r%s with an onnxruntime too old for the switch, wanted "
      "the one word" % (words, fell))

words, fell = recognise_or_fall("will not load")
check("the recognition runs on where onnxruntime will not load",
      bool(words),
      "it gave %r%s with no onnxruntime to load, wanted the one word"
      % (words, fell))


#---------------------------------------------- 2. The separation worker

print("\n2. The speaker separation's worker")

WORKER = {}
exec(compile(vpm.SPEAKER_SPLIT_WORKER, "worker", "exec"), WORKER)
hush = WORKER["hush"]
PYANNOTE = ("pyannote", "pyannote.audio", "pyannote.audio.telemetry")


def worker_hush(kind):
    """The worker's first act, over a quiet pyannote and that onnxruntime."""
    where = stand_in(kind)
    was = dict((name, sys.modules.get(name, "not there"))
               for name in PYANNOTE)
    quiet = types.ModuleType("pyannote.audio.telemetry")
    quiet.set_telemetry_metrics = lambda on: None
    try:
        for name in PYANNOTE:
            sys.modules[name] = types.ModuleType(name)
        sys.modules["pyannote.audio.telemetry"] = quiet
        try:
            said = hush()
        except Exception as e:
            said = "fell with %s: %s" % (e.__class__.__name__, e)
        return said, seen()
    finally:
        sys.path.remove(where)
        for name, mod in was.items():
            if mod == "not there":
                sys.modules.pop(name, None)
            else:
                sys.modules[name] = mod


said, noted = worker_hush("whole")
noted = noted or {"variables": {}, "calls": []}
check("the worker sets onnxruntime's variable before loading it",
      noted["variables"].get("ORT_DISABLE_TELEMETRY") == "1",
      "onnxruntime found %r in the worker's environment when it loaded, "
      "wanted ORT_DISABLE_TELEMETRY=1" % (noted["variables"],))
check("the worker throws onnxruntime's own switch",
      noted["calls"] == ["off"],
      "the calls on onnxruntime went %r, wanted ['off']"
      % (noted["calls"],))

said, _noted = worker_hush("no switch")
check("a worker whose onnxruntime has no switch still separates",
      said == "",
      "its first act said %r, wanted '' -- an older onnxruntime is no "
      "reason to refuse the separation" % (said,))


#------------------------------------------- 3. The library installed here

print("\n3. The onnxruntime installed here")

COLLECTOR = b"events.data.microsoft.com"


def library_files(folder):
    """The native files of the package: where the variable is read."""
    out = []
    for top, _dirs, names in os.walk(folder):
        for name in names:
            if name.endswith((".so", ".pyd", ".dll", ".dylib")) \
                    or ".so." in name:
                out.append(os.path.join(top, name))
    return out


if not REAL:
    print("LEFT OUT: no onnxruntime is installed here, so whether it "
          "reads the variable cannot be asked -- pip3 install "
          "faster-whisper brings it")
else:
    reporting, reads = [], []
    for path in library_files(REAL):
        with open(path, "rb") as f:
            body = f.read()
        if COLLECTOR in body:
            reporting.append(os.path.basename(path))
            if PROGRAM_SETS and all(name.encode("ascii") in body
                                    for name in PROGRAM_SETS):
                reads.append(os.path.basename(path))
    if not reporting:
        print("LEFT OUT: the onnxruntime here carries no address to "
              "report to, so there is nothing for the variable to stop")
    else:
        check("the installed onnxruntime reads the variable the program sets",
              reads == reporting,
              "the program sets %r; of the files that report to %s, %r "
              "carry it and %r do not"
              % (PROGRAM_SETS, COLLECTOR.decode(), reads,
                 sorted(set(reporting) - set(reads))))

for name in list(os.environ):
    if name.startswith("ORT_"):
        del os.environ[name]
shutil.rmtree(WORK, ignore_errors=True)

print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
