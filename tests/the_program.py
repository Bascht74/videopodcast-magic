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


# What a backslash means inside a PO string, for the reader below: the
# letter above, the character below.
PO_CODES = dict(zip('ntr"\\abfv', '\n\t\r"\\\a\b\f\v'))
PO_ESCAPE = re.compile(r"\\(.)")
PO_QUOTED = re.compile(r'^"(.*)"$')


def po_pairs(path):
    """Every entry of a PO file, as (English, translation, line number).

    A list and not a dictionary: a key written twice with two
    translations loses one of them in a dictionary without a sound, and
    a check exists to catch exactly that. The header entry, whose
    English side is empty, is left out -- it carries no text.

    A counted thing carries `msgid_plural` and a wording per form in
    place of the one `msgstr`, and it comes back by its **first**
    wording: one pair, the English singular against `msgstr[0]`. One
    pair and not one per form, because the wordings above the first
    all answer to the same English plural, and a caller that keeps one
    value per key would read three right wordings as one key said three
    times. What that leaves uncovered -- whether `msgstr[1]` and the
    rest carry the same placeholders -- the plural section of
    `text_only_texts_change_test.py` says outright, wording by wording.
    Before 5.9.2026 this reader knew none of that and handed a counted
    entry back with an empty translation.

    A reader of its own rather than the program's. A check that reads
    its subject with the subject's own eyes says only that the two
    agree, never that either is right.
    """
    found = []
    key = value = at = None
    began = 0

    def keep():
        if key:
            found.append((key, value or "", began))

    for number, line in enumerate(io.open(path, encoding="utf-8"), 1):
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("msgid "):
            keep()
            key, value, at, began = "", None, "msgid", number
            line = line[len("msgid "):]
        elif line.startswith("msgid_plural ") or line.startswith("msgstr["):
            # The second English wording, and every form after the
            # first: read past them, continuation lines included.
            if line.startswith("msgstr[0] "):
                value, at = "", "msgstr"
                line = line[len("msgstr[0] "):]
            else:
                at = None
                continue
        elif line.startswith("msgstr "):
            value, at = "", "msgstr"
            line = line[len("msgstr "):]
        quoted = PO_QUOTED.match(line)
        if not quoted or at is None:
            continue
        piece = PO_ESCAPE.sub(lambda m: PO_CODES.get(m.group(1), m.group(1)),
                              quoted.group(1))
        if at == "msgid":
            key += piece
        else:
            value += piece
    keep()
    return found


def po_texts(path):
    """One language's entries as {English wording: translation}."""
    return dict((key, value) for key, value, _at in po_pairs(path))


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
    program's folder, so a number keeps somewhere to point.

    The nine translations are not among them and need no keeping out:
    they are PO files, and only Python is program.
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
            name = os.path.relpath(os.path.join(here, one), FOLDER)
            found.append((name.replace(os.sep, "/"), body))
    found.sort(key=lambda piece: (piece[0] != entry, piece[0]))
    return found
