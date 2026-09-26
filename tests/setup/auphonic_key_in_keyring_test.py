# -*- coding: utf-8 -*-
"""Off Mac and Windows the key goes to the keyring over stdin, read back.

Walked against a stand-in secret-tool on PATH that writes down every
argument list it gets and keeps what it is handed in its own folder.
Sections: the key stored, out of argv, under the moved names and read
back; the switch saying so; a read-back that differs; no Secret Service
and no secret-tool at all, each said plainly as a failure; and deleting.
The piece is told it runs on Linux; the stand-in is a #! file, so a
Windows runner sets this test aside. No real keyring is reached.
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
import getpass
import io
import json
import shutil
import stat
import tempfile
import time
import uuid
import the_program

os.environ["VPM_NO_UPDATE_CHECK"] = "1"
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


# Invented, and the only key this file knows.
KEY = "FAKEKEY-0000"

# ---------------------------------------------------- the stand-in tool
# As strict as the real one where it matters here: an entry is found
# only under the attributes it was stored under, a lookup of nothing
# answers 1 with nothing printed, and stdin is kept byte for byte.
WORK = tempfile.mkdtemp()
TOOLS = os.path.join(WORK, "bin")
EMPTY = os.path.join(WORK, "empty")
os.makedirs(TOOLS)
os.makedirs(EMPTY)
ARGV = os.path.join(WORK, "argv.log")
KEPT = os.path.join(WORK, "kept.json")
PLAN = os.path.join(WORK, "plan")
FAKE = r'''#!%s
import json, os, sys
work = %r
with open(os.path.join(work, "argv.log"), "a") as f:
    f.write(json.dumps(sys.argv[1:]) + "\n")
plan = open(os.path.join(work, "plan")).read().strip()
if plan == "noservice":
    sys.stderr.write("secret-tool: Cannot autolaunch D-Bus without X11\n")
    sys.exit(1)
words = sys.argv[1:]
what = words.pop(0) if words else ""
if what == "store":
    if not words or not words[0].startswith("--label="):
        sys.exit(2)
    words.pop(0)
if len(words) %% 2 or what not in ("store", "lookup", "clear"):
    sys.exit(2)
place = json.dumps(sorted(zip(words[0::2], words[1::2])))
kept_file = os.path.join(work, "kept.json")
kept = json.load(open(kept_file)) if os.path.exists(kept_file) else {}
if what == "store":
    kept[place] = sys.stdin.buffer.read().decode("utf-8")
elif what == "clear":
    kept.pop(place, None)
else:
    if place not in kept:
        sys.exit(1)
    sys.stdout.write(kept[place] + ("-mangled" if plan == "mangle" else ""))
json.dump(kept, open(kept_file, "w"))
''' % (sys.executable, WORK)
TOOL = os.path.join(TOOLS, "secret-tool")
with open(TOOL, "w") as f:
    f.write(FAKE)
os.chmod(TOOL, os.stat(TOOL).st_mode | stat.S_IXUSR)


def plan(what):
    """Tell the stand-in how to answer from now on."""
    with open(PLAN, "w") as f:
        f.write(what)


def calls():
    """Every argument list the stand-in was started with, in order."""
    if not os.path.exists(ARGV):
        return []
    return [json.loads(line) for line in open(ARGV)]


def kept():
    """What the stand-in holds, as {attributes: secret}."""
    if not os.path.exists(KEPT):
        return {}
    return json.load(open(KEPT))


# --------------------------------------------- the piece, told it is Linux
class Seen(object):
    """A module as the piece sees it, with some names answered otherwise."""

    def __init__(self, real, **answers):
        self._real, self._answers = real, answers

    def __getattr__(self, name):
        if name in self._answers:
            return self._answers[name]
        return getattr(self._real, name)


typed = [""]


def prompt_stand_in(prompt="Password: ", stream=None):
    return typed[0]


def switch():
    """store_key_from_terminal on what typed holds: (code, what it said)."""
    out = io.StringIO()
    with contextlib.redirect_stdout(out):
        code = piece.store_key_from_terminal()
    return code, out.getvalue()


piece = vpm.setup
saved = dict((n, piece.__dict__[n]) for n in ("sys", "os"))
saved_prompt = getpass.getpass
saved_path = os.environ.get("PATH", "")
# Names of its own, so the store does not shut a test run out.
MARK = uuid.uuid4().hex[:12]
vpm.KEY_SERVICE = "videopodcast-magic-test-" + MARK
vpm.KEY_ACCOUNT = "auphonic-test-" + MARK
vpm.REG_PATH = r"Software\videopodcast-magic-test-" + MARK
vpm.forget_api_key()
PLACE = json.dumps(sorted([["service", vpm.KEY_SERVICE],
                           ["account", vpm.KEY_ACCOUNT]]))
piece.sys = Seen(sys, platform="linux")
piece.os = Seen(os, name="posix")
getpass.getpass = prompt_stand_in
os.environ["PATH"] = TOOLS + os.pathsep + saved_path
try:
    print("1. The key into the keyring")
    plan("ok")
    said = vpm.store_api_key("  " + KEY + " \n")
    held = kept().get(PLACE)
    check("the key reaches the keyring exactly, without a newline",
          held == KEY,
          "%s under the moved names, wanted %d characters"
          % ("nothing" if held is None else "%d characters" % len(held),
             len(KEY)))
    lists = calls()
    check("the key stands in no argument list secret-tool was given",
          lists and not any(KEY in w for c in lists for w in c),
          "%d call(s), %d of them carrying the key"
          % (len(lists), len([c for c in lists if any(KEY in w for w in c)])))
    check("the entry is filed under the moved service and account",
          lists and lists[0][-4:] == ["service", vpm.KEY_SERVICE,
                                      "account", vpm.KEY_ACCOUNT],
          "the first call ended in %d words, service %s, account %s"
          % (len(lists[0]) if lists else 0,
             "moved" if lists and vpm.KEY_SERVICE in lists[0] else "not moved",
             "moved" if lists and vpm.KEY_ACCOUNT in lists[0] else "not moved"))
    check("a key read back the same is said to hold", said is True,
          "store_api_key answered %r" % (said,))
    vpm.forget_api_key()
    back = vpm.load_api_key()
    check("and the stored key is read back out of the keyring",
          back == KEY, "read %d characters, wanted %d" % (len(back), len(KEY)))

    print("\n2. The switch on the command line")
    typed[0] = KEY
    code, out = switch()
    check("--store-auphonic-key stores there and ends with 0", code == 0,
          "returned %r" % (code,))
    check("and says the key is stored and read back",
          vpm.T('The key is stored, and reading it back gave the same key.')
          in out, "printed %r" % out.replace(KEY, "<key>")[:200])

    print("\n3. A read-back that differs")
    plan("mangle")
    said = vpm.store_api_key(KEY)
    check("a key read back different is not said to hold", said is False,
          "store_api_key answered %r over a keyring that changes it"
          % (said,))

    print("\n4. No Secret Service")
    os.remove(KEPT)
    plan("noservice")
    said = vpm.store_api_key(KEY)
    check("with no Secret Service the store says it does not hold",
          said is False, "store_api_key answered %r" % (said,))
    code, out = switch()
    check("and the switch ends with 1", code == 1, "returned %r" % (code,))
    words = vpm.T('No Secret Service keyring answered, so nothing was '
                  'stored. Off Mac and Windows the key is kept in the '
                  'desktop\'s keyring, through the secret-tool command '
                  'from libsecret. It does not go into a file.')
    check("saying plainly that no Secret Service answered",
          (vpm.T('The key is not stored: %s') % words) in out,
          "printed %r" % out.replace(KEY, "<key>")[:200])
    os.environ["PATH"] = EMPTY
    try:
        said = vpm.store_api_key(KEY)
    except Exception as e:
        said = "raised %s" % type(e).__name__
    os.environ["PATH"] = TOOLS + os.pathsep + saved_path
    check("with no secret-tool at all it does not hold either",
          said is False, "store_api_key answered %r" % (said,))

    print("\n5. Deleting")
    plan("ok")
    vpm.store_api_key(KEY)
    gone = vpm.delete_api_key()
    check("deleting the key is said to have gone", gone is True,
          "delete_api_key answered %r" % (gone,))
    check("and the keyring holds no entry under the names any more",
          PLACE not in kept(),
          "%d entr(y/ies) left under the moved names"
          % len([p for p in kept() if p == PLACE]))
finally:
    for name, what in saved.items():
        piece.__dict__[name] = what
    getpass.getpass = saved_prompt
    os.environ["PATH"] = saved_path
    shutil.rmtree(WORK, ignore_errors=True)

print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
