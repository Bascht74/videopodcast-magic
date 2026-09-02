# -*- coding: utf-8 -*-
"""The Windows way to the key store, walked for real.

Every other test replaces load_api_key with a lambda, so the storing
functions are never run, and only a Windows runner has a registry to run
them on. What needs no registry is judged on every machine: that the
three names this file may write under really are three, that the Mac
names are moved as well and that the store shuts a test run out while
they are not, and that the comparison the whole walk rests on tells two
values apart. Off Windows the rest is named as left out rather than
passed over. All three names of the store go to throwaway ones with
made-up values, and nothing read back is ever printed: a failed
redirect would print the real key.

The sections: the names and the comparison, there and back, what is not
there, deleting, awkward values, the other way round, and what is left
behind.
"""
import os
import sys
import time
import traceback
import uuid

began = time.time()
done = 0
bad = []


def check(name, ok, extra=""):
    global done
    done += 1
    print("  %-58s %s %s" % (name, "ok" if ok else "FAIL", extra))
    if not ok:
        bad.append("%s [%s]" % (name, extra or "no numbers"))


def finish(skipped=""):
    """The one way out of this file: the count, the verdict, the code.

    Nothing else calls sys.exit. A run that stopped early used to leave
    without saying how much it had judged, and a test that prints no
    count is one no floor can hold. "ALL OK" is left off a run that left
    something out -- the SKIPPED line is the verdict there, and nothing
    behind it may read as everything having been checked.
    """
    if skipped:
        print("SKIPPED: " + skipped)
    print("\n%d checks in %.2f s" % (done, time.time() - began))
    if bad:
        print("FAIL: " + " | ".join(bad))
    elif not skipped:
        print("ALL OK")
    sys.exit(1 if bad else 0)


HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = os.environ.get("VPM_SCRIPT") or os.path.join(
    os.path.dirname(HERE), "videopodcast-magic.py")


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
# Written as escapes: text_no_german_left_test.py holds every test in this
# folder to English letters, and these are material, not words.
UMLAUTS = ("not-a-key-" + "\u00e4\u00f6\u00fc"
           + "-\u00c4\u00d6\u00dc-\u00df-" + TAG)
SPACED = "not a key with blanks in the middle " + TAG
LONG = "not-a-key-" + "x" * 4000

# The program is loaded here and not further down, because the first
# section asks about the names it keeps and those have to be readable on
# every machine -- the Mac names above all, which is where the fault
# was. Loading it writes nothing anywhere.
import importlib.util                                  # noqa: E402
import key_store_apart                                 # noqa: E402

os.environ["VPM_NO_UPDATE_CHECK"] = "1"
spec = importlib.util.spec_from_file_location("vpm", SCRIPT)
vpm = importlib.util.module_from_spec(spec)
sys.modules["vpm"] = vpm
spec.loader.exec_module(vpm)
# The Mac side of the same move: service and account go to throwaway
# names of their own. REG_PATH goes with them and is set again below,
# to the name this file's own sections write under.
MAC_APART = key_store_apart.apart(vpm)
# What the store answers a test run that left the real names standing.
# Nothing is touched to find out -- three strings are compared.
KEPT_NAMES = (vpm.KEY_SERVICE, vpm.KEY_ACCOUNT, vpm.REG_PATH)
KEPT_SILENT = os.environ.get("VPM_SILENT")
try:
    vpm.KEY_SERVICE, vpm.KEY_ACCOUNT, vpm.REG_PATH = vpm.KEY_STORE_REAL
    os.environ["VPM_SILENT"] = "1"
    off_limits_with_the_real_names = vpm.key_store_off_limits()
finally:
    vpm.KEY_SERVICE, vpm.KEY_ACCOUNT, vpm.REG_PATH = KEPT_NAMES
    if KEPT_SILENT is None:
        os.environ.pop("VPM_SILENT", None)
    else:
        os.environ["VPM_SILENT"] = KEPT_SILENT

print("1. Before anything is written")
# The whole file rests on these two lines. If REG_PATH still pointed at
# the program's own key, every store below would overwrite the real one.
# They need no registry, so they are asked on every machine: a name that
# had crept back onto the real key would otherwise be found only by the
# one runner that walks the store.
check("the throwaway names are three different names",
      len(set((MINE, NEVER, REAL))) == 3,
      "%d of 3 names are different" % len(set((MINE, NEVER, REAL))))
under_stem = sum(1 for n in (MINE, NEVER) if n.startswith(STEM))
under_real = sum(1 for n in (MINE, NEVER) if n.startswith(REAL + "\\"))
check("and neither reaches into the program's key",
      under_stem == 2 and under_real == 0,
      "%d of 2 under the throwaway stem, wanted 2; %d under the "
      "program's own key, wanted 0" % (under_stem, under_real))
# The registry path is half the answer. On a Mac the same three
# functions go to the keychain under a service and an account of their
# own, and those two used to stand in the program where they were used
# -- so this file's redirect moved nothing there. Asked on every
# machine for the same reason as the two above.
check("the Mac names are moved as well, and none of them is the "
      "program's own",
      len(set(MAC_APART)) == 3
      and not set(MAC_APART) & set(vpm.KEY_STORE_REAL),
      "%d different names of %d, %d of them the program's own -- wanted "
      "three and none"
      % (len(set(MAC_APART)), len(MAC_APART),
         len(set(MAC_APART) & set(vpm.KEY_STORE_REAL))))
check("and the store refuses a test run that left them standing",
      vpm.key_store_off_limits() is False
      and off_limits_with_the_real_names is True,
      "with the throwaway names it says %r and with the real ones %r -- "
      "wanted False and True"
      % (vpm.key_store_off_limits(), off_limits_with_the_real_names))
# And these two say what the comparison is worth. Without them every
# judgement further down would still be green with a store that wrote
# nowhere and a read that handed back whatever it was given -- so they
# too are asked wherever this file runs, registry or none.
check("the comparison calls two different values different",
      not same(PLAIN, PLAIN + "x"),
      apart_says(PLAIN, PLAIN + "x"))
check("it also spots a difference in the middle",
      not same("not-a-key-abc", "not-a-key-abd"),
      apart_says("not-a-key-abc", "not-a-key-abd"))

# On a Mac the same functions talk to the keychain, and that is the one
# store this file must not go near: it holds the real key.
if os.name != "nt":
    finish("1 of 7 sections ran in full -- the six that walk the key "
           "store want a registry under HKEY_CURRENT_USER and os.name is "
           "%r here. Run it on Windows; on a Mac those same three "
           "functions go to the keychain, which holds the real key."
           % os.name)

try:
    import winreg
except ImportError:
    finish("1 of 7 sections ran in full -- this Python has no winreg, so "
           "there is no way in to the registry from here. Run it on a "
           "Windows build of CPython.")

check("this machine goes to the registry, not a keychain",
      sys.platform != "darwin" and os.name == "nt",
      "platform %r and os.name %r, wanted anything but 'darwin' and 'nt'"
      % (sys.platform, os.name))
# Nothing has been written yet, so this is the place to stop: a name
# that is not safe must not reach a store at all.
if bad:
    finish()

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

vpm.REG_PATH = MINE
try:
    print("\n2. There and back")
    stored = vpm.store_api_key(PLAIN)
    check("store_api_key says it stored the value", stored is True,
          "returned %r, wanted True" % (stored,))
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
          "raised %s, wanted nothing" % (threw or "nothing"))
    check("and it gives back nothing at all", missing == "",
          "%d chars came back, wanted 0" % len(missing))
    try:
        removed = vpm.delete_api_key()
        threw = ""
    except Exception as exc:                      # noqa: BLE001
        removed, threw = None, type(exc).__name__
    check("deleting what is not there throws nothing", not threw,
          "raised %s, wanted nothing" % (threw or "nothing"))
    check("and it says it removed nothing", removed is False,
          "returned %r, wanted False" % (removed,))

    print("\n4. Deleting deletes")
    vpm.REG_PATH = MINE
    before = vpm.load_api_key()
    check("the value is still there before the delete",
          same(before, PLAIN), apart_says(before, PLAIN))
    removed = vpm.delete_api_key()
    check("delete_api_key says it removed the value", removed is True,
          "returned %r, wanted True" % (removed,))
    after = vpm.load_api_key()
    check("afterwards nothing comes back", after == "",
          "%d chars came back, wanted 0" % len(after))

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
    # The two that ask what the comparison is worth stand in section 1,
    # because they need no store. These two ask the same of the store
    # itself: that a write which went nowhere, and a delete which did
    # nothing, would both have been caught above.
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
except Exception as exc:                          # noqa: BLE001
    # The walk fell over somewhere the checks do not reach. Said out
    # loud and carried into the verdict, or the file would leave through
    # a traceback and never print how much it had judged.
    traceback.print_exc()
    bad.append("the walk got to the end of section 6 [%s: %s]"
               % (type(exc).__name__, exc))
finally:
    vpm.REG_PATH = REAL
    scrub()
    left = leftovers()
    print("\n7. Nothing of this run is left")
    check("the throwaway keys are gone again", not left,
          "%d still standing, wanted 0: %s" % (len(left), left[:2]))
    for number, path in enumerate((MINE, NEVER), 1):
        there = True
        try:
            winreg.OpenKey(winreg.HKEY_CURRENT_USER, path).Close()
        except OSError:
            there = False
        check("key %d of 2 cannot be opened any more" % number,
              not there, "%d still there, wanted 0: %s" % (int(there), path))

finish()
