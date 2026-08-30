# -*- coding: utf-8 -*-
"""Where the shared fixture folders live.

Built once and read by several tests, so they cannot go under the
per-run TMPDIR that is thrown away at the end. A fixed path in a
directory everybody may write to is worse: with two users, or two jobs
on one builder, the second run deletes the first one's material. The
root therefore carries the user id, and VPM_FIXTURES overrides it.
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
