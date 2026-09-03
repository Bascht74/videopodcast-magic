# -*- coding: utf-8 -*-
"""The macOS key store is reached without a leak and without a prompt.

Nothing here starts a process or opens a real library: both places are
replaced and the program is told this machine is a Mac. The sections:
what the stand-ins refuse, what security is handed, there and back,
what is not there, deleting, a missing or deaf security, whether the
store is shut and who is asked, the line that greys the save box, that
a test run which left the real names standing is shut out of the store
altogether, and that nothing real ever ran. The key is invented and no
line prints it.
"""
import os
import subprocess
import sys
import time
import uuid

began = time.time()

# Unmistakably invented, and free of anything a shell or security would
# read as a flag: no leading dash, no blank, no quotation mark.
TAG = uuid.uuid4().hex[:8]
PLAIN = "not-a-key-" + TAG
# Written as escapes: text_no_german_left_test.py holds every test in
# this folder to English letters, and these are material, not words.
UMLAUTS = ("not-a-key-" + "\u00e4\u00f6\u00fc"
           + "-\u00c4\u00d6\u00dc-\u00df-" + TAG)
SPACED = "not a key with blanks in the middle " + TAG
LONG = "not-a-key-" + "x" * 4000
EDGED = "  " + PLAIN + "  \n"
SECRETS = (PLAIN, UMLAUTS, SPACED, LONG, EDGED)

done = 0
bad = []


def check(name, ok, extra=""):
    global done
    done += 1
    # No made-up key may stand in a report that travels either: only the
    # place one was found is ever named. This is the second lock on it.
    name, extra = str(name), str(extra)
    for secret in SECRETS:
        name = name.replace(secret, "<the value>")
        extra = extra.replace(secret, "<the value>")
    print("  %-64s %s %s" % (name, "ok" if ok else "FAIL", extra))
    if not ok:
        bad.append("%s [%s]" % (name, extra or "no numbers"))


def stop():
    """The one way out of this file: the count, the verdict, the code."""
    print("\n%d checks in %.2f s" % (done, time.time() - began))
    print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
    sys.exit(1 if bad else 0)


HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = os.environ.get("VPM_SCRIPT") or os.path.join(
    os.path.dirname(HERE), "videopodcast_magic.py")


def where_apart(got, want):
    """First place two strings differ, or -1 when they do not.

    The report says how long each side was and where they parted, never
    what either side held.
    """
    for i in range(min(len(got), len(want))):
        if got[i] != want[i]:
            return i
    return -1 if len(got) == len(want) else min(len(got), len(want))


def apart_says(got, want):
    """The numbers that go into a FAIL line, and no characters."""
    return "got %d chars, wanted %d, apart at %d" % (
        len(got), len(want), where_apart(got, want))


def same(got, want):
    return where_apart(got, want) == -1


def carried_by(starts, secret):
    """Index of the first start with the value on its command line."""
    for i, one in enumerate(starts):
        for word in one.argv:
            if secret in word:
                return i
    return -1


# ------------------------------------------------- the stand-in keychain
#
# The keychain of this machine holds the real key, so nothing here may
# go near it and "security" is never started. What takes its place reads
# what it was handed and answers the way security answers -- and it
# refuses what security refuses, or a check would be green over a store
# that took anything at all.
STORE = {}
STARTS = []
PLAN = {"raise": None, "deaf": 0, "mask": None}


class Started(object):
    """One start of a program, read off what it was handed."""

    def __init__(self, argv, kwargs):
        self.argv = ([str(x) for x in argv]
                     if isinstance(argv, (list, tuple)) else [str(argv)])
        self.shell = bool(kwargs.get("shell"))
        self.session = bool(kwargs.get("start_new_session"))
        self.limit = kwargs.get("timeout")
        fed = kwargs.get("input")
        self.fed = (fed.decode("utf-8", "replace")
                    if isinstance(fed, bytes) else fed)
        # What the child would inherit: an environment of its own where
        # one was handed over, otherwise this process's.
        given = kwargs.get("env")
        self.env = dict(given) if given is not None else dict(os.environ)


def value_after(words, flag):
    """The word after a flag, or None where the flag ends the line."""
    if flag not in words:
        return None
    at = words.index(flag)
    if at + 1 < len(words) and not words[at + 1].startswith("-"):
        return words[at + 1]
    return None


def answered(one):
    """What /usr/bin/security would answer, and no softer.

    add-generic-password with a bare -w asks for the word twice and
    compares the two; a mismatch is refused, and a caller that sends
    nothing is left waiting, which is what a time limit is for. A find
    for an item that is not there is return code 44 with nothing on
    standard output, and so is a delete of one.
    """
    words = one.argv
    sub = words[1] if len(words) > 1 else ""
    service, account = value_after(words, "-s"), value_after(words, "-a")
    if not service or not account:
        return 1, b"", b"security: no service or account named"
    at = (service, account)
    if sub == "add-generic-password":
        if "-w" not in words:
            return 1, b"", b"security: no password given"
        word = value_after(words, "-w")
        if word is None:
            # It asks on its own, once and once to confirm.
            if one.fed is None:
                raise subprocess.TimeoutExpired(words, one.limit or 20)
            lines = one.fed.split("\n")
            if len(lines) < 2:
                raise subprocess.TimeoutExpired(words, one.limit or 20)
            if lines[0] != lines[1]:
                return 1, b"", b"security: they do not match"
            word = lines[0]
        if "-U" not in words and at in STORE:
            return 45, b"", b"security: the item already exists"
        STORE[at] = word
        return 0, b"", b""
    if sub == "find-generic-password":
        if at not in STORE:
            return 44, b"", (b"security: SecKeychainSearchCopyNext: The "
                             b"specified item could not be found")
        if "-w" not in words:
            # Without -w it prints the attributes and not the word.
            return 0, b"keychain: \"login.keychain-db\"\n", b""
        return 0, STORE[at].encode("utf-8") + b"\n", b""
    if sub == "delete-generic-password":
        if at not in STORE:
            return 44, b"", (b"security: SecKeychainSearchCopyNext: The "
                             b"specified item could not be found")
        del STORE[at]
        return 0, b"password has been deleted.\n", b""
    return 2, b"", b"security: unknown command"


def fake_run(argv, **kwargs):
    one = Started(argv, kwargs)
    STARTS.append(one)
    if PLAN["raise"] is not None:
        raise PLAN["raise"]
    if one.argv[:1] != ["security"]:
        raise OSError("this stand-in knows no program but security")
    # A locked keychain leaves any of the three waiting, not only the
    # write, so what goes deaf here is the next call of whatever kind.
    if PLAN["deaf"] > 0:
        PLAN["deaf"] -= 1
        raise subprocess.TimeoutExpired(one.argv, one.limit or 20)
    code, out, err = answered(one)
    return subprocess.CompletedProcess(one.argv, code, out, err)


class NoChild(object):
    """What Popen hands back here: nothing anybody may lean on."""


def fake_popen(argv, **kwargs):
    """The way the program brings up an app, written down not walked."""
    one = Started(argv, kwargs)
    STARTS.append(one)
    if PLAN["raise"] is not None:
        raise PLAN["raise"]
    if one.argv[:1] != ["open"]:
        raise OSError("this stand-in brings up nothing but open")
    return NoChild()


class NoSubprocess(object):
    """The four names this way through the program needs, and no more.

    Nothing else is put here on purpose: a name the program reaches for
    and this does not carry raises AttributeError and is seen, where a
    catch-all would answer politely and hide the reach.
    """

    run = staticmethod(fake_run)
    Popen = staticmethod(fake_popen)
    CompletedProcess = subprocess.CompletedProcess
    TimeoutExpired = subprocess.TimeoutExpired


# --------------------------------------------- the stand-in library
#
# The lock is read out of Security.framework on the real machine. What
# takes its place here answers the mask the plan names, writes down
# every library opened and every call made into one, and refuses any
# other library, so a check cannot be green over a question asked
# somewhere else entirely.
LIBS = []
ASKED = []
MASK_OPEN = 0x7        # what the framework answers for an open keychain
MASK_LOCKED = 0x2      # and for a locked one


class Slot(object):
    """What c_uint32 makes: a number the called library writes into."""

    def __init__(self, value=0):
        self.value = value


class FakeLibrary(object):
    """Security.framework, as far as the one call into it goes."""

    def __init__(self, path):
        self.path = path

    def SecKeychainGetStatus(self, which, out):
        ASKED.append((self.path, "SecKeychainGetStatus"))
        if PLAN["mask"] is None:
            return -25293          # what it says when it will not answer
        out.value = PLAN["mask"]
        return 0


def fake_cdll(path):
    LIBS.append(str(path))
    if "Security.framework" not in str(path):
        raise OSError("this stand-in opens no library but Security")
    return FakeLibrary(str(path))


class NoCtypes(object):
    """The three names the lock question needs, and no more.

    As with the processes: a name the program reaches for and this does
    not carry raises AttributeError and is seen.
    """

    CDLL = staticmethod(fake_cdll)
    c_uint32 = Slot
    byref = staticmethod(lambda one: one)


# -------------------------------------- 1. What the stand-ins refuse
print("1. What the comparison and the stand-ins refuse")

check("the comparison calls two different values different",
      not same(PLAIN, PLAIN + "x"), apart_says(PLAIN, PLAIN + "x"))
check("it also spots a difference in the middle",
      not same("not-a-key-abc", "not-a-key-abd"),
      apart_says("not-a-key-abc", "not-a-key-abd"))

PROBE = ["security", "add-generic-password", "-U", "-s", "stand-in-probe",
         "-a", "probe", "-w"]
told = fake_run(PROBE, input=b"one\ntwo\n", capture_output=True, timeout=20)
check("the stand-in refuses a word that was not confirmed twice",
      told.returncode != 0,
      "return code %d, wanted anything but 0" % told.returncode)
told = fake_run(["security", "find-generic-password", "-s", "stand-in-probe",
                 "-a", "probe", "-w"], capture_output=True, timeout=20)
check("the stand-in hands back nothing it never stored",
      told.returncode != 0 and not told.stdout,
      "return code %d and %d bytes back, wanted anything but 0 and 0 bytes"
      % (told.returncode, len(told.stdout)))
waited = ""
try:
    fake_run(PROBE, capture_output=True, timeout=20)
except subprocess.TimeoutExpired:
    waited = "TimeoutExpired"
check("the stand-in waits when nobody sends the word at all",
      waited == "TimeoutExpired",
      "it answered with %s, wanted TimeoutExpired" % (waited or "no fault"))
refused = ""
try:
    fake_cdll("/usr/lib/libSystem.dylib")
except OSError:
    refused = "OSError"
check("the stand-in opens no library but Security", refused == "OSError",
      "it answered with %s, wanted OSError" % (refused or "a library"))
refused = ""
try:
    fake_popen(["security", "show-keychain-info"])
except OSError:
    refused = "OSError"
check("the stand-in brings up no program but open", refused == "OSError",
      "it answered with %s, wanted OSError" % (refused or "a child"))
del STARTS[:]
del LIBS[:]
STORE.clear()

# Nothing has gone near the program yet, and nothing should: a stand-in
# that takes whatever it is given would make every judgement below green
# over a key store that stored nothing.
if bad:
    stop()

os.environ["QT_QPA_PLATFORM"] = "offscreen"
os.environ["VPM_NO_UPDATE_CHECK"] = "1"

import importlib.util                                       # noqa: E402
import key_store_apart                                      # noqa: E402
spec = importlib.util.spec_from_file_location("vpm", SCRIPT)
vpm = importlib.util.module_from_spec(spec)
sys.modules["vpm"] = vpm
spec.loader.exec_module(vpm)

# Qt comes up here, before every way of starting a program is nailed
# shut below, and offscreen: the last section builds a row of widgets
# and nothing of it may reach anybody's screen.
try:
    from PySide6 import QtWidgets                           # noqa: E402
except ImportError as exc:                                  # noqa: BLE001
    QtWidgets, app, no_qt = None, None, type(exc).__name__
else:
    app = QtWidgets.QApplication(sys.argv[:1])
    no_qt = ""


# The last line of defence, put in after the import so the import itself
# keeps the machine it was built for: from here on every real way to
# start a program is written down and refused. OSError is what the
# program already expects from a machine without security, so a slip
# does not end the run in a traceback -- it ends it in section 7.
REAL_STARTS = []


def never(*args, **kwargs):
    first = args[0] if args else kwargs.get("args", "?")
    name = first[0] if isinstance(first, (list, tuple)) and first else first
    REAL_STARTS.append(str(name)[:40])
    raise OSError("this test starts no process")


for holder, names in ((subprocess, ("run", "Popen", "call", "check_output",
                                    "check_call", "getoutput")),
                      (os, ("system", "popen", "posix_spawn", "posix_spawnp",
                            "execv", "execvp", "fork", "spawnv"))):
    for one in names:
        if hasattr(holder, one):
            setattr(holder, one, never)


class MacSys(object):
    """The real sys module, except that this machine says it is a Mac.

    Five of the six builder jobs are not Macs and the keychain branch is
    the one under test, so the branch is chosen rather than the machine.
    Nothing is loosened by it: no process starts either way, and every
    name but the platform is the real module's, so a name the program
    wants and this has not fails exactly as it would anywhere.
    """

    platform = "darwin"

    def __getattr__(self, name):
        return getattr(sys, name)


class NotMacSys(MacSys):
    """The same again, except that this machine is not a Mac."""

    platform = "linux"


vpm.subprocess = NoSubprocess
vpm.ctypes = NoCtypes
vpm.sys = MacSys()
# All three names of the store go somewhere throwaway, so no slip of a
# branch could reach a real one. The two keychain names are the ones
# that decide here: pointing only REG_PATH away moved nothing on a Mac,
# because the service and the account were written out in the program.
APART = key_store_apart.apart(vpm)

# ------------------------------------- 2. What security is handed
print("\n2. What security is handed when the key is stored")

mark = len(STARTS)
said = vpm.store_api_key(PLAIN)
storing = STARTS[mark:]
check("storing the key starts a program at all", bool(storing),
      "%d starts, wanted at least 1" % len(storing))
if not storing:
    stop()
first = storing[0]
check("it starts security itself, with no shell in between",
      first.argv[:1] == ["security"] and not first.shell,
      "started %r, shell %s" % (first.argv[0], first.shell))
check("the key reaches security through its standard input",
      first.fed is not None and PLAIN in first.fed,
      "%d bytes went in, and the value is %s"
      % (len(first.fed or ""),
         "in them" if first.fed and PLAIN in first.fed else "in none of them"))
at = carried_by(storing, PLAIN)
check("no word of the command line that stores the key is the key", at < 0,
      "%d starts, %s" % (len(storing), "none carries it" if at < 0
                         else "start %d of them carries it" % at))
loud = sorted(n for one in storing for n, v in one.env.items()
              if PLAIN in str(v))
check("no environment variable security inherits carries the key", not loud,
      "%d variables, %s" % (len(first.env), "none carries it" if not loud
                            else "the one called %s carries it" % loud[0]))
check("the call that stores the key has a session of its own",
      first.session, "start_new_session %s, wanted True" % first.session)
check("the call that stores the key gives up after a while",
      isinstance(first.limit, (int, float)) and not isinstance(
          first.limit, bool) and first.limit > 0,
      "the limit it names is %r, wanted a number of seconds" % (first.limit,))
check("storing says it stored the key", said is True,
      "returned %r, wanted True" % (said,))

# ------------------------------------------------- 3. There and back
print("\n3. What went in comes out")

vpm.forget_api_key()
mark = len(STARTS)
got = vpm.load_api_key()
reading = STARTS[mark:]
check("what went in comes out unchanged", same(got, PLAIN),
      apart_says(got, PLAIN))
check("reading the key starts a program at all", bool(reading),
      "%d starts, wanted at least 1" % len(reading))
if reading:
    ask = reading[0]
    check("the call that reads the key has a session of its own",
          ask.session, "start_new_session %s, wanted True" % ask.session)
    check("the call that reads the key gives up after a while",
          isinstance(ask.limit, (int, float)) and not isinstance(
              ask.limit, bool) and ask.limit > 0,
          "the limit it names is %r, wanted a number of seconds"
          % (ask.limit,))
    # security must not be left holding this program's own standard
    # input: a question it decides to ask there would eat what the
    # program was reading, and nobody would see it asked.
    check("the call that reads hands security an input of its own",
          ask.fed is not None, "%s, wanted a pipe of its own"
          % ("%d bytes went in" % len(ask.fed) if ask.fed is not None
             else "standard input inherited from this process"))

def round_trip(value):
    """Store one value, forget what was read, and read it back."""
    vpm.store_api_key(value)
    vpm.forget_api_key()
    return vpm.load_api_key()


# Written out one by one rather than looped: the register that holds the
# counter-proofs reads the wording of a judgement out of the source, and
# three checks sharing one "%s" there are one row for three claims.
back = round_trip(UMLAUTS)
check("umlauts and eszett survive the trip", same(back, UMLAUTS),
      apart_says(back, UMLAUTS))
back = round_trip(SPACED)
check("blanks in the middle survive the trip", same(back, SPACED),
      apart_says(back, SPACED))
back = round_trip(LONG)
check("4010 characters survive the trip", same(back, LONG),
      apart_says(back, LONG))

# A pasted key carries a newline more often than not, and both callers
# strip before they store. The store itself takes the edges off on the
# way back, and that is what is asked here.
back = round_trip(EDGED)
check("blanks at the edges are taken off, as meant", same(back, PLAIN),
      apart_says(back, PLAIN))

# ------------------------------------------- 4. What is not there
print("\n4. What is not there is not there")

STORE.clear()
vpm.forget_api_key()
try:
    missing, threw = vpm.load_api_key(), ""
except Exception as exc:                              # noqa: BLE001
    missing, threw = "", type(exc).__name__
check("a name that was never written throws nothing", not threw,
      "raised %s, wanted nothing" % (threw or "nothing"))
check("and it gives back nothing at all", missing == "",
      "%d chars came back, wanted 0" % len(missing))
try:
    removed, threw = vpm.delete_api_key(), ""
except Exception as exc:                              # noqa: BLE001
    removed, threw = None, type(exc).__name__
check("deleting what is not there throws nothing", not threw,
      "raised %s, wanted nothing" % (threw or "nothing"))
check("and it says it removed nothing", removed is False,
      "returned %r, wanted False" % (removed,))

# ---------------------------------------------- 5. Deleting deletes
print("\n5. Deleting deletes")

vpm.store_api_key(PLAIN)
vpm.forget_api_key()
before = vpm.load_api_key()
check("the value is still there before the delete", same(before, PLAIN),
      apart_says(before, PLAIN))
mark = len(STARTS)
removed = vpm.delete_api_key()
erasing = [one for one in STARTS[mark:]
           if one.argv[1:2] == ["delete-generic-password"]]
check("delete_api_key says it removed the value", removed is True,
      "returned %r, wanted True" % (removed,))
# The delete hangs off a click on a checkbox, where nothing catches a
# fault, so it wants the same three guards as the other two calls.
check("deleting the key starts a program at all", bool(erasing),
      "%d starts of the delete, wanted at least 1" % len(erasing))
if erasing:
    gone = erasing[0]
    check("the call that deletes the key has a session of its own",
          gone.session, "start_new_session %s, wanted True" % gone.session)
    check("the call that deletes the key gives up after a while",
          isinstance(gone.limit, (int, float)) and not isinstance(
              gone.limit, bool) and gone.limit > 0,
          "the limit it names is %r, wanted a number of seconds"
          % (gone.limit,))
    check("the call that deletes hands security an input of its own",
          gone.fed is not None, "%s, wanted a pipe of its own"
          % ("%d bytes went in" % len(gone.fed) if gone.fed is not None
             else "standard input inherited from this process"))
after = vpm.load_api_key()
check("afterwards nothing comes back", after == "",
      "%d chars came back, wanted 0" % len(after))
# The read after a delete has to go to the store again. If the answer
# came out of what was remembered from before, the line above would be
# green with the key still standing in the keychain.
asked = [one for one in STARTS[mark:]
         if one.argv[1:2] == ["find-generic-password"]]
check("and the store was asked again, not the last answer", bool(asked),
      "%d reads of the store after the delete, wanted at least 1"
      % len(asked))

# ------------------------------- 6. When security is missing, or deaf
print("\n6. When security is missing, or deaf")

STORE.clear()
vpm.forget_api_key()
PLAN["raise"] = OSError("there is no security on this machine")
try:
    said, threw = vpm.store_api_key(PLAIN), ""
except BaseException as exc:                          # noqa: BLE001
    said, threw = None, type(exc).__name__
check("storing throws nothing when security is missing", not threw,
      "raised %s, wanted nothing" % (threw or "nothing"))
check("and storing says it failed", said is False,
      "returned %r, wanted False" % (said,))
vpm.forget_api_key()
try:
    got, threw = vpm.load_api_key(), ""
except BaseException as exc:                          # noqa: BLE001
    got, threw = None, type(exc).__name__
check("reading throws nothing when security is missing", not threw,
      "raised %s, wanted nothing" % (threw or "nothing"))
check("and reading gives back nothing at all", got == "",
      "%d chars came back, wanted 0" % len(got or ""))
try:
    removed, threw = vpm.delete_api_key(), ""
except BaseException as exc:                          # noqa: BLE001
    removed, threw = None, type(exc).__name__
check("deleting throws nothing when security is missing", not threw,
      "raised %s, wanted nothing" % (threw or "nothing"))
PLAN["raise"] = None

# A keychain that is locked leaves security waiting until the limit runs
# out. What the caller must not get is the fault itself: it is thrown
# inside a click on a checkbox, where nothing catches it.
STORE.clear()
vpm.forget_api_key()
mark = len(STARTS)
PLAN["deaf"] = 9
try:
    said, threw = vpm.store_api_key(PLAIN), ""
except BaseException as exc:                          # noqa: BLE001
    said, threw = None, type(exc).__name__
PLAN["deaf"] = 0
deaf_starts = STARTS[mark:]
check("a keychain that never answers comes back with a verdict, not a fault",
      not threw and isinstance(said, bool),
      "raised %s and returned %r, wanted no fault and a yes or no"
      % (threw or "nothing", said))
# The rule the whole file is about, at the one place it was broken: a
# try that fails is no licence to hand the key over as an argument,
# where the process list carries it to every user of the machine.
at = carried_by(deaf_starts, PLAIN)
check("no word of any command line is the key, also when the first try "
      "fails", at < 0,
      "%d starts, %s" % (len(deaf_starts), "none carries it" if at < 0
                         else "start %d of them carries it" % at))
vpm.forget_api_key()
PLAN["deaf"] = 9
try:
    removed, threw = vpm.delete_api_key(), ""
except BaseException as exc:                          # noqa: BLE001
    removed, threw = None, type(exc).__name__
PLAN["deaf"] = 0
check("a delete that never answers comes back with a verdict, not a fault",
      not threw and isinstance(removed, bool),
      "raised %s and returned %r, wanted no fault and a yes or no"
      % (threw or "nothing", removed))

# ------------------------- 7. Whether the store is shut, and who is asked
print("\n7. Whether the store is shut, and who is asked")

del LIBS[:]
del ASKED[:]
mark, real_mark = len(STARTS), len(REAL_STARTS)
PLAN["mask"] = MASK_OPEN
says = vpm.key_store_locked()
check("an unlocked keychain is reported unlocked", says is False,
      "answered %r, wanted False" % (says,))
PLAN["mask"] = MASK_LOCKED
says = vpm.key_store_locked()
check("a locked keychain is reported locked", says is True,
      "answered %r, wanted True" % (says,))
check("the question goes to Security.framework and nowhere else",
      bool(ASKED) and all("Security.framework" in one for one in LIBS),
      "%d calls into %s" % (len(ASKED), sorted(set(LIBS)) or "no library"))
# The one thing this must never do. The command-line way answers the
# same question and puts a password window on the screen for it, so a
# start of any program at all on this path is the fault itself.
started = ([one.argv[0] for one in STARTS[mark:]]
           + REAL_STARTS[real_mark:])
check("asking whether the keychain is locked starts no program",
      not started, "%d starts, the first of them %s"
      % (len(started), started[0] if started else "none"))
PLAN["mask"] = None
says = vpm.key_store_locked()
check("a library that will not answer leaves the state unknown",
      says is None, "answered %r, wanted None" % (says,))
PLAN["mask"] = MASK_LOCKED
vpm.sys = NotMacSys()
mark = len(ASKED)
says = vpm.key_store_locked()
vpm.sys = MacSys()
check("off a Mac the keychain is not asked at all",
      says is None and len(ASKED) == mark,
      "answered %r after %d calls, wanted None after 0"
      % (says, len(ASKED) - mark))

# What a failed save tells the person who pressed the box. On a Mac the
# old wording blamed the machine, and the machine was never the reason.
locked_words = vpm.T('The keychain is locked. Unlock it and try again.')
PLAN["mask"] = MASK_LOCKED
said = vpm.key_store_trouble()
check("a save that failed over a locked keychain blames the lock",
      said == locked_words,
      "said %d chars, the locked wording has %d"
      % (len(said), len(locked_words)))
PLAN["mask"] = MASK_OPEN
said = vpm.key_store_trouble()
check("and with the keychain open it does not blame the lock",
      bool(said) and said != locked_words,
      "said %d chars, the locked wording has %d"
      % (len(said), len(locked_words)))

# Twenty seconds of a frozen window is what the look is there to spare,
# and the delete needs it too: putting the tick back after a failed
# write walks straight into it.
PLAN["mask"] = MASK_LOCKED
STORE.clear()
vpm.forget_api_key()
mark = len(STARTS)
said = vpm.store_api_key(PLAIN)
check("a locked keychain is not written to at all",
      said is False and len(STARTS) == mark,
      "returned %r after %d starts, wanted False after 0"
      % (said, len(STARTS) - mark))
mark = len(STARTS)
removed = vpm.delete_api_key()
check("and nothing is deleted out of it either",
      removed is False and len(STARTS) == mark,
      "returned %r after %d starts, wanted False after 0"
      % (removed, len(STARTS) - mark))
PLAN["mask"] = MASK_OPEN

WAY = ["open", "-b", "com.apple.keychainaccess"]
mark = len(STARTS)
opened = vpm.open_key_store_app()
way = STARTS[mark:]
check("the keychain app is asked for by bundle name, not by a path",
      opened is True and len(way) == 1 and way[0].argv == WAY,
      "returned %r after %d starts, the first %r"
      % (opened, len(way), way[0].argv if way else None))

# ------------------------------- 8. The line that greys the save box
print("\n8. The line that greys the save box")

if no_qt:
    print("  LEFT OUT the line that greys the save box: no PySide6 here"
          " (%s) -- pip install -r requirements.txt brings it" % no_qt)
else:
    PLAN["mask"] = MASK_LOCKED
    holder = QtWidgets.QWidget()
    into = QtWidgets.QVBoxLayout(holder)
    keep_box = QtWidgets.QCheckBox(vpm.T('Save in Keychain'))
    vpm.keychain_row_add(into, keep_box)
    row = holder.findChild(QtWidgets.QWidget, "keychain_row")
    check("the line that says why the box is grey was built",
          row is not None, "found %r, wanted a widget" % (row,))
    check("the save box is grey while the keychain is locked",
          not keep_box.isEnabled(),
          "enabled %s, wanted False" % keep_box.isEnabled())
    check("and the line that says why stands there",
          row is not None and not row.isHidden(),
          "hidden %s, wanted False" % (row.isHidden() if row else "no row"))

    # Nothing calls the reading again: the row's own timer has to, or
    # nobody can tell whether unlocking took. So the wait is on the box
    # coming alive, and running out of patience is red.
    WAKE_LIMIT = 20.0
    PLAN["mask"] = MASK_OPEN
    waited = time.time()
    while not keep_box.isEnabled() and time.time() - waited < WAKE_LIMIT:
        app.processEvents()
        time.sleep(0.01)
    woke = time.time() - waited
    check("the save box wakes up by itself once the keychain is open",
          keep_box.isEnabled(), "enabled %s after %.2f s of at most %.1f"
          % (keep_box.isEnabled(), woke, WAKE_LIMIT))
    check("and the line that says why goes away with it",
          row is not None and row.isHidden(),
          "hidden %s, wanted True" % (row.isHidden() if row else "no row"))

    press = holder.findChild(QtWidgets.QPushButton, "keychain_way")
    check("the button beside that line was built", press is not None,
          "found %r, wanted a button" % (press,))
    if press is not None:
        mark = len(STARTS)
        press.click()
        pressed = STARTS[mark:]
        check("pressing it brings up the keychain app",
              len(pressed) == 1 and pressed[0].argv == WAY,
              "%d starts, the first %r"
              % (len(pressed), pressed[0].argv if pressed else None))

# ------------------------- 9. A test run cannot reach the real store
print("\n9. A test run cannot reach the real store")
#
# Measured on 2.9.2026: the keychain service and account stood in the
# program where they were used, so a test that pointed REG_PATH at a
# throwaway name moved nothing here and wrote over the key the person
# at this machine really uses -- fourteen characters where an Auphonic
# key has about forty. The real names are put back for these few
# lines, which is safe only because nothing in this file starts a real
# process: the stand-in above is what makes the question askable.
check("the throwaway names are three, and none of them the real ones",
      len(set(APART)) == 3 and not set(APART) & set(vpm.KEY_STORE_REAL),
      "%d different names of %d, and %d of them real -- wanted three "
      "and none"
      % (len(set(APART)), len(APART),
         len(set(APART) & set(vpm.KEY_STORE_REAL))))
# That the gate stands open while the names are throwaway ones gets no
# judgement of its own here: every section above went to the store and
# came back, so it was open, and a check saying so again would be one
# that cannot fall. auphonic_key_kept asks it, where nothing else does.
kept_names = (vpm.KEY_SERVICE, vpm.KEY_ACCOUNT, vpm.REG_PATH)
kept_silent = os.environ.get("VPM_SILENT")
try:
    vpm.KEY_SERVICE, vpm.KEY_ACCOUNT, vpm.REG_PATH = vpm.KEY_STORE_REAL
    os.environ["VPM_SILENT"] = "1"
    vpm.forget_api_key()
    shut = vpm.key_store_off_limits()
    mark = len(STARTS)
    wrote = vpm.store_api_key(PLAIN)
    read = vpm.load_api_key()
    removed = vpm.delete_api_key()
    tried = len(STARTS) - mark
    why = vpm.key_store_trouble()
finally:
    vpm.KEY_SERVICE, vpm.KEY_ACCOUNT, vpm.REG_PATH = kept_names
    if kept_silent is None:
        os.environ.pop("VPM_SILENT", None)
    else:
        os.environ["VPM_SILENT"] = kept_silent
    vpm.forget_api_key()
check("a test run that left the real names standing is shut out",
      shut is True, "%r, wanted True" % (shut,))
# The store itself is asked as well as the three answers. With the
# guard gone from the write alone, the key really lands in the store
# and all three answers still read right: the write reports False
# because the read it confirms itself with is the one still shut out.
landed = [at for at in STORE if at == vpm.KEY_STORE_REAL[:2]]
check("so nothing is written, read or deleted under the real names",
      wrote is False and read == "" and removed is False and not landed,
      "the store said %r, the read gave %d characters, the delete said "
      "%r, and %d entries stand under the real names -- wanted False, 0, "
      "False and none" % (wrote, len(read), removed, len(landed)))
check("and not one process is started to try",
      tried == 0, "%d starts, wanted 0" % tried)
check("and the program says why nothing was saved",
      why == vpm.T('This run is a test run and the store still carries '
                   'its real name, so nothing was written. Point '
                   'KEY_SERVICE, KEY_ACCOUNT or REG_PATH somewhere else '
                   'first.'),
      "it says %r" % (why,))

# --------------------------------------- 10. Nothing real ever ran
print("\n10. Nothing real ever ran")

check("no real process was started anywhere in this run", not REAL_STARTS,
      "%d starts got past the stand-in, the first of them %s"
      % (len(REAL_STARTS), REAL_STARTS[0] if REAL_STARTS else "none"))

stop()
