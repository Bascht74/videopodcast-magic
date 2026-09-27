# -*- coding: utf-8 -*-
"""A model file list naming a place outside the model folder writes nothing.

The list of model files, SHA256SUMS.txt, comes off the network, and a
name in it decides where a file is written beside the program. A name
that climbs out with "..", an absolute one, one with a drive letter or
a backslash, and one through a folder that links elsewhere each stop
the fetch with a message naming it, before a single model file is
asked for, and leave no file anywhere. The model's own nested names --
a file in a subfolder -- are still written, inside the folder.

The link case needs a symbolic link; where the system refuses one, that
section is left out with a line saying so.

Nothing goes out: urlopen is replaced, and the program's folder is
pointed at a throwaway one.
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
import hashlib
import io
import tempfile
import time
import urllib.request

import the_program


def no_network(url, *rest, **more):
    """Refuse every look that the stand-in below does not answer."""
    raise IOError("this test asks github.com nothing")


urllib.request.urlopen = no_network

began = time.time()
vpm = the_program.load()
vpm.set_language("en")
done = 0
bad = []

PAYLOAD = b"weights\n"
DIGEST = hashlib.sha256(PAYLOAD).hexdigest()


def check(name, ok, extra=""):
    global done
    done += 1
    print("  %-58s %s %s" % (name, "ok" if ok else "FAIL", extra))
    if not ok:
        bad.append("%s [%s]" % (name, extra or "no numbers"))


def fetch(name, before=None):
    """Fetch a model whose list names only *name*, with a matching hash.

    *before* is handed the model folder to lay something there first.
    Returns (what fetch_model said, the files asked for other than the
    list, every file under the throwaway root as a relative path).
    """
    root = tempfile.mkdtemp()
    program = os.path.join(root, "program")
    os.makedirs(program)
    folder = os.path.join(program, "models", vpm.SPEAKER_MODEL_NAME)
    if before:
        before(root, folder)
    vpm.fetch_model.__globals__["running_from"] = \
        lambda: os.path.join(program, "__init__.py")
    asked = []

    def stand_in(url, *rest, **more):
        wanted = url.split("/" + vpm.SPEAKER_MODEL_NAME + "/", 1)[1]
        if wanted == "SHA256SUMS.txt":
            return io.BytesIO(("%s  %s\n" % (DIGEST, name)).encode())
        asked.append(wanted)
        return io.BytesIO(PAYLOAD)

    urllib.request.urlopen = stand_in
    try:
        said = vpm.fetch_model()
    finally:
        urllib.request.urlopen = no_network
    files = sorted(os.path.relpath(os.path.join(d, f), root)
                   .replace(os.sep, "/")
                   for d, _, fs in os.walk(root) for f in fs)
    return said, asked, files


print("Names that leave the folder")
said, asked, files = fetch("../../x.py")
check("a name climbing out with .. stops the fetch",
      "../../x.py" in said and not asked,
      "said %r, asked %s" % (said, asked))
check("a name climbing out with .. leaves no file anywhere",
      files == [], "files %s" % files)

outside = os.path.join(tempfile.mkdtemp(), "x.py").replace(os.sep, "/")
said, asked, files = fetch(outside)
check("an absolute name stops the fetch",
      outside in said and not asked and not os.path.exists(outside),
      "said %r, asked %s, written there %s"
      % (said, asked, os.path.exists(outside)))

said, asked, files = fetch("C:x.py")
check("a name with a drive letter stops the fetch",
      "C:x.py" in said and not asked and files == [],
      "said %r, asked %s, files %s" % (said, asked, files))

said, asked, files = fetch("sub\\..\\..\\x.py")
check("a name with a backslash stops the fetch",
      "sub\\..\\..\\x.py" in said and not asked and files == [],
      "said %r, asked %s, files %s" % (said, asked, files))


def linked_out(root, folder):
    os.makedirs(folder)
    os.makedirs(os.path.join(root, "elsewhere"))
    os.symlink(os.path.join(root, "elsewhere"),
               os.path.join(folder, "sub"))


try:
    said, asked, files = fetch("sub/x.py", linked_out)
except (OSError, NotImplementedError) as e:
    print("LEFT OUT the link case: this system made no symbolic link"
          " (%s)" % e)
else:
    check("a name through a folder linking outside stops the fetch",
          "sub/x.py" in said and not asked
          and "elsewhere/x.py" not in files,
          "said %r, asked %s, files %s" % (said, asked, files))

print("The model's own names")
said, asked, files = fetch("embedding/pytorch_model.bin")
inside = "program/models/%s/embedding/pytorch_model.bin" \
    % vpm.SPEAKER_MODEL_NAME
check("a file in a subfolder of the model is written inside it",
      said == "" and inside in files,
      "said %r, files %s" % (said, files))

print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
