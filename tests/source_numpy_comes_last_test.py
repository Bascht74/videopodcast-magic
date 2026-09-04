# -*- coding: utf-8 -*-
"""The program loads without numpy, so --help and --version stay cheap.

Nothing fetches numpy while the file is read: a stand-in holds the
name until the first calculation asks for it. A default value in a def
line is evaluated as the file is read, so one reaching for numpy there
would fetch it for every --help, and py_compile does not see that
because it never runs the body. In order: a child with every road to
numpy shut reads the file to the end, what stands under np afterwards,
that nothing reached for numpy at all, and a walk over the syntax tree
naming every default value and top-level line that reads np.
"""
import ast
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time

HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = os.path.realpath(os.environ.get("VPM_SCRIPT") or os.path.join(
    os.path.dirname(HERE), "videopodcast_magic.py"))

MARK = "NUMPY-REPORT"
# Reading the file costs well under a second here and the builder is
# some nine times slower, so a healthy run never comes near this. There
# is no sign of life to watch inside a child that only imports, so this
# is a limit and not a standstill -- and reaching it is red, with the
# waiting time in the line.
PATIENCE = 180.0

# The child: numpy is made unreachable before the program is read, and
# the argument list says --version so that the program answers without
# fetching anything. What it found goes out as one line of json.
CHILD = r'''# -*- coding: utf-8 -*-
"""Read the program with every road to numpy shut, and say what happened."""
import importlib.util
import json
import os
import sys
import traceback

SCRIPT = os.path.realpath(os.environ["VPM_NUMPY_SCRIPT"])
MARK = os.environ["VPM_NUMPY_MARK"]
asked = []


class NoNumpy:
    """A finder that shuts numpy and writes down who asked for it."""

    def find_spec(self, name, path=None, target=None):
        if name != "numpy" and not name.startswith("numpy."):
            return None
        line = 0
        for frame in traceback.extract_stack():
            # The outermost frame in the file: the line the program was
            # on when it set out for numpy, not the import call itself.
            if os.path.realpath(frame.filename) == SCRIPT and not line:
                line = frame.lineno
        asked.append(line)
        raise ImportError("numpy is out of reach in this test")


sys.modules.pop("numpy", None)
# In front of everything else, so find_spec never gets past it.
sys.meta_path.insert(0, NoNumpy())
# The cheap door in particular: whoever only wants the version number
# is the one who must not be made to wait for twenty megabytes.
sys.argv = ["videopodcast_magic.py", "--version"]

out = {"loaded": False, "kind": "", "message": "", "line": 0, "source": "",
       "names": 0, "np": "(the file was not read to the end)",
       "asked": asked}
try:
    spec = importlib.util.spec_from_file_location("vpm", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["vpm"] = mod
    spec.loader.exec_module(mod)
except BaseException as trouble:      # a sys.exit counts as not loaded
    out["kind"] = type(trouble).__name__
    out["message"] = " ".join(str(trouble).split())[:160]
    for frame in traceback.extract_tb(sys.exc_info()[2]):
        if os.path.realpath(frame.filename) == SCRIPT:
            out["line"] = frame.lineno
            out["source"] = " ".join((frame.line or "").split())[:120]
else:
    out["loaded"] = True
    out["names"] = len(dir(mod))
    out["np"] = repr(getattr(mod, "np", "(no np at all)"))[:120]
sys.stdout.write("\n%s %s\n" % (MARK, json.dumps(out)))
sys.stdout.flush()
'''

began = time.time()
done = 0
bad = []


def check(name, ok, extra=""):
    global done
    done += 1
    print("  %-58s %s %s" % (name, "ok" if ok else "FAIL", extra))
    if not ok:
        bad.append("%s [%s]" % (name, extra or "no numbers"))


def as_text(raw):
    """Whatever the child left behind, as text."""
    if isinstance(raw, bytes):
        return raw.decode("utf-8", "replace")
    return raw or ""


def tail(text, how_many=2):
    """The last non-empty lines of some output, flattened and cut short."""
    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
    return " / ".join(lines[-how_many:])[:160] if lines else "(nothing)"


# --- the program is read with numpy out of reach ----------------------

work = tempfile.mkdtemp(prefix="numpy_last_")
child = os.path.join(work, "read_without_numpy.py")
with open(child, "w", encoding="utf-8") as f:
    f.write(CHILD)

env = dict(os.environ)
env["VPM_NUMPY_SCRIPT"] = SCRIPT
env["VPM_NUMPY_MARK"] = MARK
# The second lock. Should a later state of the program want numpy after
# all, pip fails at once instead of fetching twenty megabytes.
env["PIP_NO_INDEX"] = "1"
env["PIP_NO_INPUT"] = "1"
env["QT_QPA_PLATFORM"] = "offscreen"
env["VPM_SILENT"] = "1"
env["VPM_NO_SPEAKER_SPLIT"] = "1"
env["VPM_NO_UPDATE_CHECK"] = "1"
env.pop("VPM_SCRIPT", None)

started = time.time()
gave_up = False
code = -1
said = ""
went_wrong = ""
try:
    ran = subprocess.run([sys.executable, child], env=env, cwd=work,
                         capture_output=True, text=True, timeout=PATIENCE)
    code, said, went_wrong = ran.returncode, ran.stdout, ran.stderr
except subprocess.TimeoutExpired as slow:
    gave_up = True
    said, went_wrong = as_text(slow.stdout), as_text(slow.stderr)
waited = time.time() - started

report = {}
for line in said.splitlines():
    if line.startswith(MARK + " "):
        try:
            report = json.loads(line[len(MARK) + 1:])
        except ValueError:
            report = {}

asked = report.get("asked") or []
loaded = bool(report.get("loaded"))

if gave_up:
    why = ("no answer after %.2f s of a %.1f s wait, last words: %s"
           % (waited, PATIENCE, tail(went_wrong)))
elif not report:
    why = ("no report from the child, it ended %d after %.2f s, "
           "last words: %s" % (code, waited, tail(went_wrong)))
elif loaded:
    why = ("read in %.2f s, %d names defined, requests for numpy: %d"
           % (waited, report.get("names") or 0, len(asked)))
else:
    why = ("%s at line %d after %.2f s -- %s -- %s"
           % (report.get("kind") or "?", report.get("line") or 0, waited,
              report.get("source") or "(no source line)",
              report.get("message") or "(nothing said)"))
check("the program is read to the end with numpy out of reach",
      loaded and not gave_up, why)

# --- and it did not fetch numpy on the way ----------------------------

after = report.get("np") or "(no report at all)"
check("a run that only reads the version leaves np filled, not empty",
      after != "None" and after != "(no np at all)",
      "np is %s once the file has been read" % after)

check("nothing reaches for numpy while only the version is read",
      not asked,
      "requests for numpy: %d, from lines %s"
      % (len(asked), ", ".join(str(n) for n in asked) or "none"))

# --- and the file says as much, line by line --------------------------


def reads_np_while_read(tree):
    """Lines that read np as the file itself is read, defaults included.

    A function body runs later, so it is left out; its decorators, its
    default values and its annotations are evaluated where the def
    stands, so they are not. Assignments to np -- the two the program
    means -- are stores, not reads, and never appear here.
    """
    found = []
    stack = [tree]
    while stack:
        node = stack.pop()
        if (isinstance(node, ast.Name) and node.id == "np"
                and isinstance(node.ctx, ast.Load)):
            found.append(node.lineno)
            continue
        for piece in ast.iter_child_nodes(node):
            if isinstance(piece, (ast.FunctionDef, ast.AsyncFunctionDef)):
                stack.extend(piece.decorator_list)
                stack.append(piece.args)
                if piece.returns is not None:
                    stack.append(piece.returns)
            elif isinstance(piece, ast.Lambda):
                stack.append(piece.args)
            else:
                stack.append(piece)
    return sorted(found)


source = ""
unreadable = ""
try:
    with open(SCRIPT, encoding="utf-8") as f:
        source = f.read()
    tree = ast.parse(source)
except OSError as trouble:
    unreadable = "%s is not readable: %s" % (SCRIPT, trouble)
except SyntaxError as trouble:
    unreadable = "%s does not parse, line %s" % (SCRIPT, trouble.lineno)
lines = source.splitlines()
places = [] if unreadable else reads_np_while_read(tree)
first = " ".join(lines[places[0] - 1].split())[:100] if places else ""
check("no default value and no top-level line reads np",
      not places and not unreadable,
      unreadable or "%d of %d lines read np%s"
      % (len(places), len(lines),
         (", the first is %d: %s" % (places[0], first)) if places else ""))

shutil.rmtree(work, ignore_errors=True)

print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
