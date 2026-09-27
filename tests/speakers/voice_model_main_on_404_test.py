# -*- coding: utf-8 -*-
"""The model comes from main only when this version's tag answers 404.

The model is fetched from the tag of the running version, so program
and model never stand a version apart. A tag that does not exist is a
run off the branch, and main is the right place then; a tag that is
there but did not answer -- a timeout, an unreachable host, a server
fault -- is not, and a release must not quietly take main's model.

The sections: a 404 on the tag goes on to main and the report line
names main; a timeout, an unreachable host and a 500 each ask main
nothing, and the message names the tag and what went wrong.

Nothing goes out: urlopen is replaced at the top of the file, and the
program's folder is pointed at a throwaway one so no model is written
beside the real program.
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
import socket
import tempfile
import time
import urllib.error
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

# The tag the program asks for, taken from the program, not written here.
TAG = vpm.model_reference()
PAYLOAD = b"weights\n"
SUMS = ("%s  a.bin\n" % hashlib.sha256(PAYLOAD).hexdigest()).encode()


def check(name, ok, extra=""):
    global done
    done += 1
    print("  %-58s %s %s" % (name, "ok" if ok else "FAIL", extra))
    if not ok:
        bad.append("%s [%s]" % (name, extra or "no numbers"))


def fetch(fault):
    """One fetch whose tag answers with *fault*; main answers fine.

    Returns (what fetch_model said, the references asked in order,
    the report lines).
    """
    root = tempfile.mkdtemp()
    program = os.path.join(root, "program")
    os.makedirs(program)
    vpm.fetch_model.__globals__["running_from"] = \
        lambda: os.path.join(program, "__init__.py")
    asked = []

    def stand_in(url, *rest, **more):
        tail = url.split("/videopodcast_magic/models/")[0]
        asked.append(tail.rsplit("/", 1)[-1])
        if "/%s/" % TAG in url:
            raise fault(url)
        name = url.rsplit("/", 1)[-1]
        return io.BytesIO(SUMS if name == "SHA256SUMS.txt" else PAYLOAD)

    urllib.request.urlopen = stand_in
    lines = []
    try:
        said = vpm.fetch_model(lambda text, part: lines.append(text))
    finally:
        urllib.request.urlopen = no_network
    return said, asked, lines


def http(code):
    return lambda url: urllib.error.HTTPError(url, code, "stand-in", {},
                                              None)


def timeout(url):
    return socket.timeout("timed out")


def unreachable(url):
    return urllib.error.URLError("stand-in host unreachable")


print("A tag that answers 404")
said, asked, lines = fetch(http(404))
check("a tag that answers 404 is fetched from main",
      said == "" and asked[:2] == [TAG, "main"],
      "said %r, asked %s" % (said, asked))
check("the report line names main when main was fetched",
      any("main" in line for line in lines),
      "report lines %s" % lines)

print("A tag that times out")
said, asked, lines = fetch(timeout)
check("a timeout on the tag asks main nothing",
      asked == [TAG], "asked %s" % asked)
check("a timeout on the tag names the tag and the reason",
      TAG in said and "timed out" in said,
      "said %r, tag %s" % (said, TAG))

print("A host that cannot be reached")
said, asked, lines = fetch(unreachable)
check("an unreachable host on the tag asks main nothing",
      asked == [TAG], "asked %s, said %r" % (asked, said))

print("A tag that answers 500")
said, asked, lines = fetch(http(500))
check("a 500 on the tag asks main nothing",
      asked == [TAG], "asked %s" % asked)
check("a 500 on the tag names the tag and the reason",
      TAG in said and "500" in said,
      "said %r, tag %s" % (said, TAG))

print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
