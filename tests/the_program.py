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
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SCRIPT = os.environ.get("VPM_SCRIPT") or os.path.join(
    ROOT, "videopodcast_magic", "__init__.py")
FOLDER = os.path.dirname(os.path.abspath(SCRIPT))


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


def whole():
    """Every piece of the program joined, for a reader hunting a word.

    A word search does not care which file the word stands in, and
    twenty readers would otherwise write the same loop. Never for a
    line number: a number into this points nowhere -- `pieces()` hands
    the same text back with the name of the piece each part came from.
    """
    return "\n".join(body for _name, body in pieces())


# A translation is data, not program: one name and nothing else. Held
# apart by what stands in the file rather than by where it lies, so a
# ninth language tomorrow needs nothing written here.
HOLDS_TEXTS = re.compile(r"^TEXTS = \{", re.M)
HOLDS_CODE = re.compile(r"^(?:def |class |import |from )", re.M)


def a_catalogue(body):
    """Whether that file holds a translation rather than program."""
    return bool(HOLDS_TEXTS.search(body)) and not HOLDS_CODE.search(body)


def on_disk():
    """How many bytes the whole program weighs, over all its pieces.

    A floor worked out from one file was a floor over the whole
    program until the window moved out of it. Two guards asked
    getsize(SCRIPT) and went on measuring the entry alone -- one of
    them exists to notice a reader that came back with a fragment, and
    it let the whole window go missing and stayed green. Asked here
    once, so the next piece to leave moves both by itself.
    """
    # The names pieces() hands back are relative to the folder,
    # which is what makes them printable beside a line number.
    return sum(os.path.getsize(os.path.join(FOLDER, name))
               for name, _body in pieces())


def pieces():
    """Every piece of the program, each as (its name, its text).

    `text()` above answers for one file, and a reader that builds a
    tree or a call graph out of it measures a program with holes in it
    the moment a piece moves out -- silently, because a name that is no
    longer there is simply never reached. This hands back all of them.

    Not joined into one string, because a good many of these readers
    print a line number and a number into a joined text points
    nowhere. The name beside each piece is its path under the
    program's folder, so a number keeps somewhere to point. Whoever
    only searches for a word may join them and has the catalogues
    already left out: a translation is data, and three checks go red
    over it for the wrong reason.
    """
    entry = os.path.relpath(os.path.abspath(SCRIPT), FOLDER)
    entry = entry.replace(os.sep, "/")
    found = []
    for here, folders, files in os.walk(FOLDER):
        folders[:] = [one for one in folders if one != "__pycache__"]
        for one in files:
            if not one.endswith(".py"):
                continue
            body = io.open(os.path.join(here, one), encoding="utf-8").read()
            if a_catalogue(body):
                continue
            name = os.path.relpath(os.path.join(here, one), FOLDER)
            found.append((name.replace(os.sep, "/"), body))
    found.sort(key=lambda piece: (piece[0] != entry, piece[0]))
    return found
