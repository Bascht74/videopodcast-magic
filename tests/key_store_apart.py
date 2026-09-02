# -*- coding: utf-8 -*-
"""Point the credential store at a throwaway name -- all three of them.

Three names say where the API key is kept: on Windows the registry path
under HKEY_CURRENT_USER, on a Mac the service and the account a generic
password is filed under. A test that moved only one of them moved
nothing on the other machine.

Measured on 2.9.2026: on a Mac the two keychain names were written out
in the program where they were used, so `REG_PATH = <throwaway>`
redirected nothing there, and the store the test walked was the one the
person at the machine really uses.

So this moves all three, in one place, and every test with business in
the store calls it right after the program is imported and before
anything reads or writes a key. The program refuses to touch the store
at all while a test run still carries the real names, so forgetting
this is a red test rather than a lost key -- see key_store_off_limits.
"""
import atexit
import subprocess
import sys
import uuid


def _scrub(service, account):
    """Take the throwaway entry out of the keychain again.

    A test that stores something leaves an item behind for good
    otherwise -- a new one every run, under a new name every run. Only
    ever this test's own name, and the answer is not looked at: there
    is nothing to do about a failure here and nothing to say about one.
    """
    if sys.platform != "darwin":
        return
    try:
        subprocess.run(["security", "delete-generic-password",
                        "-s", service, "-a", account],
                       input=b"", capture_output=True, timeout=20,
                       start_new_session=True)
    except (OSError, subprocess.SubprocessError):
        pass


def apart(vpm, tag=""):
    """Give this test's key store three names of its own.

    Returns them, so a check can hold them against the real ones. The
    cache in front of the store is emptied as well: it is keyed on the
    place, but a value read before the move would otherwise still be
    sitting there under the old key. What the test writes under the new
    name is taken out again when the run ends.
    """
    mark = (tag or "") + uuid.uuid4().hex[:12]
    vpm.KEY_SERVICE = "videopodcast-magic-test-" + mark
    vpm.KEY_ACCOUNT = "auphonic-test-" + mark
    vpm.REG_PATH = r"Software\videopodcast-magic-test-" + mark
    vpm.forget_api_key()
    atexit.register(_scrub, vpm.KEY_SERVICE, vpm.KEY_ACCOUNT)
    return vpm.KEY_SERVICE, vpm.KEY_ACCOUNT, vpm.REG_PATH
