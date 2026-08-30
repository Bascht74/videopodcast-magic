# -*- coding: utf-8 -*-
"""The Windows way to the key store, walked for real.

Every other test replaces load_api_key with a lambda, so the storing
functions are never run, and only a Windows runner has a registry to
run them on; elsewhere this checks nothing and says so. REG_PATH goes
to a throwaway key with made-up values, and nothing read back is ever
printed: a failed redirect would print the real key.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = os.environ.get("VPM_SCRIPT") or os.path.join(
    os.path.dirname(HERE), "videopodcast-magic.py")

# On a Mac the same functions talk to the keychain, and that is the one
# store this file must not go near: it holds the real key.
if os.name != "nt":
    print("SKIPPED: no registry here -- this walks the Windows way to "
          "the key store, and os.name is %r on this machine." % os.name)
    sys.exit(0)

try:
    import winreg
except ImportError:
    print("SKIPPED: this Python has no winreg, so there is no way in "
          "to the registry from here.")
    sys.exit(0)

import uuid
import importlib.util

os.environ["VPM_NO_UPDATE_CHECK"] = "1"
spec = importlib.util.spec_from_file_location("vpm", SCRIPT)
vpm = importlib.util.module_from_spec(spec)
sys.modules["vpm"] = vpm
spec.loader.exec_module(vpm)

bad = []


def check(name, ok, extra=""):
    print("  %-52s %s %s" % (name, "ok" if ok else "FAIL", extra))
    if not ok:
        bad.append(name)


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


# --------------------------------------------------- where this may write
REAL = r"Software\videopodcast-magic"
STEM = REAL + "-test-"
# Both thrown away at the end; NEVER is never written to at all.
MINE = STEM + uuid.uuid4().hex[:12]
NEVER = STEM + uuid.uuid4().hex[:12]
# Values that could not be mistaken for a key, by anybody, at any point.
TAG = uuid.uuid4().hex[:8]
PLAIN = "not-a-key-" + TAG
# Written as escapes: german_hunt_test.py holds every test in this
# folder to English letters, and these are material, not words.
UMLAUTS = ("not-a-key-" + "\u00e4\u00f6\u00fc"
           + "-\u00c4\u00d6\u00dc-\u00df-" + TAG)
SPACED = "not a key with blanks in the middle " + TAG
LONG = "not-a-key-" + "x" * 4000


def scrub():
    """Take the throwaway keys out again, whatever happened before.

    delete_api_key only takes the value out, so an empty key would stay
    behind for good.
    """
    for path in (MINE, NEVER):
        try:
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, path, 0,
                                winreg.KEY_SET_VALUE) as k:
                winreg.DeleteValue(k, "auphonic_api_key")
        except OSError:
            pass
        try:
            winreg.DeleteKey(winreg.HKEY_CURRENT_USER, path)
        except OSError:
            pass


def leftovers():
    """Names under HKCU\\Software that this file or an earlier run left.

    Only key names are read, never a value, so the program's own key is
    counted and never opened.
    """
    out = []
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Software") as k:
            i = 0
            while True:
                try:
                    name = winreg.EnumKey(k, i)
                except OSError:
                    break
                if name.startswith("videopodcast-magic-test-"):
                    out.append(name)
                i += 1
    except OSError:
        pass
    return out


print("1. Before anything is written")
# The whole file rests on these two lines. If REG_PATH still pointed at
# the program's own key, every store below would overwrite the real one.
check("the throwaway names are three different names",
      len(set((MINE, NEVER, REAL))) == 3,
      "%d of 3 names are different" % len(set((MINE, NEVER, REAL))))
check("and neither reaches into the program's key",
      MINE.startswith(STEM) and NEVER.startswith(STEM)
      and not MINE.startswith(REAL + "\\")
      and not NEVER.startswith(REAL + "\\"),
      "%d chars, %d of them the shared stem" % (len(MINE), len(STEM)))
check("this machine goes to the registry, not a keychain",
      sys.platform != "darwin" and os.name == "nt",
      "platform %r, os.name %r" % (sys.platform, os.name))
# A run killed halfway leaves a key behind. Taking it out beats staying
# red over a name that is this file's own; section 7 is the clean one.
stale = leftovers()
for name in stale:
    try:
        winreg.DeleteKey(winreg.HKEY_CURRENT_USER, "Software\\" + name)
    except OSError:
        pass
print("  %d throwaway keys left by an earlier run, taken out"
      % len(stale))

if bad:
    print()
    print("FAIL: " + ", ".join(bad))
    sys.exit(1)

vpm.REG_PATH = MINE
try:
    print("\n2. There and back")
    stored = vpm.store_api_key(PLAIN)
    check("store_api_key says it stored the value", stored is True,
          "returned %r" % (stored,))
    got = vpm.load_api_key()
    check("what went in comes out unchanged", same(got, PLAIN),
          apart_says(got, PLAIN))

    print("\n3. What is not there is not there")
    vpm.REG_PATH = NEVER
    try:
        missing = vpm.load_api_key()
        threw = ""
    except Exception as exc:                      # noqa: BLE001
        missing, threw = "", type(exc).__name__
    check("a name that was never written throws nothing", not threw,
          "raised %s" % threw)
    check("and it gives back nothing at all", missing == "",
          "%d chars came back" % len(missing))
    try:
        removed = vpm.delete_api_key()
        threw = ""
    except Exception as exc:                      # noqa: BLE001
        removed, threw = None, type(exc).__name__
    check("deleting what is not there throws nothing", not threw,
          "raised %s" % threw)
    check("and it says it removed nothing", removed is False,
          "returned %r" % (removed,))

    print("\n4. Deleting deletes")
    vpm.REG_PATH = MINE
    before = vpm.load_api_key()
    check("the value is still there before the delete",
          same(before, PLAIN), apart_says(before, PLAIN))
    removed = vpm.delete_api_key()
    check("delete_api_key says it removed the value", removed is True,
          "returned %r" % (removed,))
    after = vpm.load_api_key()
    check("afterwards nothing comes back", after == "",
          "%d chars came back" % len(after))

    print("\n5. Awkward values survive the trip")
    # Blanks at the edges are taken off on purpose: a pasted key carries
    # a newline more often than not, so the material has them inside.
    for name, value in (("umlauts and eszett", UMLAUTS),
                        ("blanks in the middle", SPACED),
                        ("4010 characters", LONG)):
        vpm.store_api_key(value)
        got = vpm.load_api_key()
        check("%s survive the trip" % name, same(got, value),
              apart_says(got, value))
    vpm.store_api_key("  " + PLAIN + "  \n")
    got = vpm.load_api_key()
    check("blanks at the edges are taken off, as meant",
          same(got, PLAIN), apart_says(got, PLAIN))

    print("\n6. The other way round: the checks do fire")
    # Without this section every check above would still be green if the
    # store wrote nowhere and the read gave back what it was handed.
    check("the comparison calls two different values different",
          not same(PLAIN, PLAIN + "x"),
          apart_says(PLAIN, PLAIN + "x"))
    check("it also spots a difference in the middle",
          not same("not-a-key-abc", "not-a-key-abd"), "one character")
    vpm.store_api_key(PLAIN)
    vpm.REG_PATH = NEVER
    elsewhere = vpm.load_api_key()
    check("a store that went nowhere would have been caught",
          not same(elsewhere, PLAIN), apart_says(elsewhere, PLAIN))
    # And the delete: had it done nothing, section 4 would have said so.
    vpm.REG_PATH = MINE
    still = vpm.load_api_key()
    check("a delete that did nothing would have been caught",
          same(still, PLAIN), apart_says(still, PLAIN))
finally:
    vpm.REG_PATH = REAL
    scrub()
    left = leftovers()
    print("\n7. Nothing of this run is left")
    check("the throwaway keys are gone again", not left,
          "%d still standing: %s" % (len(left), left[:2]))
    for number, path in enumerate((MINE, NEVER), 1):
        there = True
        try:
            winreg.OpenKey(winreg.HKEY_CURRENT_USER, path).Close()
        except OSError:
            there = False
        check("key %d of 2 cannot be opened any more" % number,
              not there, "%d still there: %s" % (int(there), path))

print()
if bad:
    print("FAIL: " + ", ".join(bad))
    sys.exit(1)
print("All good.")
