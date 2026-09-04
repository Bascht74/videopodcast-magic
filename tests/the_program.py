# -*- coding: utf-8 -*-
"""Where the program under test is, and how a test gets hold of it.

Nearly every test needs the same two things before it can ask anything:
the path of the program, and the program executed in this process under
the name `vpm`. Both stood in every test file -- two hundred copies of
the same six lines, and therefore two hundred places to mend on the day
the program stops being one file and becomes a folder. They stand here
instead, once.

`VPM_SCRIPT` names the copy to measure. Every run against a snapshot
goes through it, so it is read here and nowhere else.

The name has no `_test` in it on purpose: `run.sh` collects the suite
as `*_test.py`, and a helper called `under_test.py` was picked up and
run as a test -- red, with three further tests red behind it for
counting a file that checks nothing.

**Nothing in this file prints, and nothing may.** `run.sh` reads each
test's output for `FAIL`, `Error`, `SKIPPED:` and `LEFT OUT`, and a line
out of a helper would be counted against whichever test imported it.
"""
import importlib.util
import io
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SCRIPT = os.environ.get("VPM_SCRIPT") or os.path.join(
    ROOT, "videopodcast_magic.py")


def load(name="vpm"):
    """The program, freshly executed in this process, and handed back.

    It goes into `sys.modules` before it runs and not after, which is
    what every test did by hand: a module that executes while it is not
    yet registered is executed a second time by the first `import` of
    its own name, and then two copies stand side by side -- the test
    bending a name in one of them and the program using the other.

    The name is an argument because it is the name the tests reach the
    program by. What they bend afterwards -- `vpm.load_api_key =
    something harmless` -- they bend in the object handed back here.
    """
    spec = importlib.util.spec_from_file_location(name, SCRIPT)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def text():
    """The program as one string, for the tests that read it rather than run it.

    The same read those tests did for themselves. It is here so that
    they ask the same place as everybody else where the program is: a
    reader is the one a folder catches out most quietly, because a
    folder opens as a directory and not as a file.
    """
    return io.open(SCRIPT, encoding="utf-8").read()
