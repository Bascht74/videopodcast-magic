# -*- coding: utf-8 -*-
"""Where the shared fixture folders live.

Four folders are built once by fixtures.sh and read by several tests, so
they cannot go under the per-run TMPDIR that run.sh throws away at the
end. They used to be /tmp/foreign and friends -- fixed paths in a
directory everybody can write to, each one preceded by an rm -rf. On a
machine with two users, or a CI with two jobs, the second run deletes
the first one's material out from under it.

The root now carries the user id, and VPM_FIXTURES overrides it.
"""
import os


def fixture_root():
    """The folder the shared fixtures live in, made if it is not there."""
    root = os.environ.get("VPM_FIXTURES")
    if not root:
        try:
            who = os.getuid()
        except AttributeError:
            who = os.environ.get("USERNAME") or "user"   # Windows
        root = os.path.join("/tmp", "vpm-fixtures-%s" % who)
    os.makedirs(root, exist_ok=True)
    return root


def fixture(name):
    """One shared fixture folder by name: foreign, hdrtest, interview ..."""
    return os.path.join(fixture_root(), name)
