# -*- coding: utf-8 -*-
"""On Windows the key goes in only behind a lock, and holds only read back.

Walked on every machine against a stand-in registry: the piece that
keeps the key is told it runs on Windows, winreg is a stand-in and the
lock is replaced by one that writes down when it was asked. Sections:
the key goes in unchanged under the moved path, the entry is opened
with the right to change its readers and locked before the key goes
in, a failed lock keeps the key out, and the store says it holds only
where reading back gives the same key; then the rule the lock writes,
and the lock saying so where it could not lock. The real
registry and the real lock are walked by auphonic_key_kept on Windows.
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
import time
import types
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


KEY = "FAKEKEY-0000"
# WRITE_DAC: the right to change who may read an open registry key.
WRITE_DAC = 0x00040000
SID = "S-1-5-21-1-2-3-1001"

# ------------------------------------------------------ the stand-in winreg
# As strict as the real one where it matters here: a key that was never
# created cannot be opened, and a value comes back as it went in unless
# the plan says the registry mangles it.
REG = {}
EVENTS = []
PLAN = {"lock": True, "mangle": False}


class Handle(object):
    """An open key of the stand-in: its path and the rights it was given."""

    def __init__(self, path, access):
        self.path, self.access = path, access

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False

    def __int__(self):
        return 0


def create_key_ex(root, path, reserved=0, access=0x20006):
    EVENTS.append(("open", path, access))
    REG.setdefault(path, {})
    return Handle(path, access)


def create_key(root, path):
    return create_key_ex(root, path)


def open_key(root, path, reserved=0, access=0x20019):
    if path not in REG:
        raise FileNotFoundError(path)
    return Handle(path, access)


def set_value_ex(handle, name, reserved, kind, value):
    EVENTS.append(("set", handle.path))
    REG[handle.path][name] = (kind, value)


def query_value_ex(handle, name):
    kind, value = REG[handle.path][name]
    return (value + "-mangled" if PLAN["mangle"] else value), kind


def delete_value(handle, name):
    del REG[handle.path][name]


winreg = types.ModuleType("winreg")
winreg.HKEY_CURRENT_USER = 0x80000001
winreg.KEY_ALL_ACCESS, winreg.KEY_SET_VALUE = 0xF003F, 0x0002
winreg.KEY_READ, winreg.KEY_WRITE, winreg.REG_SZ = 0x20019, 0x20006, 1
winreg.CreateKeyEx, winreg.CreateKey = create_key_ex, create_key
winreg.OpenKey, winreg.SetValueEx = open_key, set_value_ex
winreg.QueryValueEx, winreg.DeleteValue = query_value_ex, delete_value


def lock_stand_in(handle):
    EVENTS.append(("lock", handle.path))
    return PLAN["lock"]


# --------------------------------------------- the piece, told it is Windows
class Seen(object):
    """A module as the piece sees it, with some names answered otherwise."""

    def __init__(self, real, **answers):
        self._real, self._answers = real, answers

    def __getattr__(self, name):
        if name in self._answers:
            return self._answers[name]
        return getattr(self._real, name)


def refused(*a, **k):
    raise OSError("no program is started in this test")


piece = vpm.setup
kept = dict((n, piece.__dict__[n]) for n in
            ("os", "sys", "subprocess", "registry_owner_only"))
kept_winreg = sys.modules.get("winreg")
# Names of its own, so the store does not shut a test run out -- and
# nothing is started, so no keychain is reached whatever breaks.
MARK = uuid.uuid4().hex[:12]
vpm.KEY_SERVICE = "videopodcast-magic-test-" + MARK
vpm.KEY_ACCOUNT = "auphonic-test-" + MARK
vpm.REG_PATH = r"Software\videopodcast-magic-test-" + MARK
piece.os = Seen(os, name="nt")
piece.sys = Seen(sys, platform="win32")
piece.subprocess = Seen(piece.subprocess, run=refused, Popen=refused)
piece.registry_owner_only = lock_stand_in
sys.modules["winreg"] = winreg
try:
    print("1. The key, the entry, and the lock")
    said = vpm.store_api_key("  " + KEY + " ")
    went = REG.get(vpm.REG_PATH, {}).get("auphonic_api_key")
    check("the key goes in unchanged, as text, under the moved path",
          went == (winreg.REG_SZ, KEY),
          "%s under the moved path, wanted text of %d characters"
          % ("nothing" if went is None else "type %d, %d characters"
             % (went[0], len(went[1])), len(KEY)))
    rights = [e[2] for e in EVENTS if e[0] == "open"]
    check("the entry is opened with the right to change its readers",
          len(rights) == 1 and rights[0] & WRITE_DAC == WRITE_DAC,
          "opened %d times, with rights %s"
          % (len(rights), ["0x%x" % r for r in rights]))
    order = [e[0] for e in EVENTS if e[0] in ("lock", "set")]
    check("the entry is locked before the key goes in",
          order == ["lock", "set"],
          "the stand-in saw %s, wanted lock then set" % (order,))
    check("a key read back the same is said to hold", said is True,
          "store_api_key answered %r" % (said,))

    print("\n2. When the lock or the read-back fails")
    REG.clear()
    del EVENTS[:]
    PLAN["lock"] = False
    said = vpm.store_api_key(KEY)
    PLAN["lock"] = True
    check("a lock that fails keeps the key out of the registry",
          "auphonic_api_key" not in REG.get(vpm.REG_PATH, {}),
          "the registry holds %d value(s) under the moved path"
          % len(REG.get(vpm.REG_PATH, {})))
    check("and the store says it does not hold", said is False,
          "store_api_key answered %r" % (said,))
    PLAN["mangle"] = True
    said = vpm.store_api_key(KEY)
    PLAN["mangle"] = False
    check("a key read back different is not said to hold", said is False,
          "store_api_key answered %r over a registry that changes it"
          % (said,))
finally:
    for name, what in kept.items():
        piece.__dict__[name] = what
    if kept_winreg is None:
        sys.modules.pop("winreg", None)
    else:
        sys.modules["winreg"] = kept_winreg

print("\n3. The rule the lock writes")
rule = vpm.registry_rule(SID)
check("the rule names this user alone and inherits nothing",
      rule == "D:P(A;;KA;;;%s)" % SID, "%r" % rule)
# Off Windows there are no libraries to ask; on Windows the handle is
# no key at all. Either way nothing was locked, and True would lie.
locked = vpm.registry_owner_only(Handle("nowhere", 0))
check("the lock says so where it could not lock",
      locked is False, "answered %r on %s" % (locked, sys.platform))

print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
