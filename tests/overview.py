# -*- coding: utf-8 -*-
"""Writes the table of every test into README.md, out of the tests.

A list of every test kept by hand is wrong within a week: somebody
renames one, rewords a heading, adds one, and nobody opens the README.
So the tests are the source and this writes the list down from them --
the name as run.sh prints it, and the first line of the docstring,
which says what holds when the test is green.

    python3 overview.py            # write it into README.md
    python3 overview.py --show     # print it, change nothing
    python3 overview.py covers     # how many judgements a register row covers

text_tests_listed_test.py holds the README against the folder, so a
list that was not written back turns the suite red rather than going
quietly stale.
"""
import ast
import io
import os
import subprocess
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
README = os.path.join(HERE, "README.md")

# The twelve prefixes of the naming scheme, in the order the guidelines
# name them, and what part of the program each one stands for. The
# gloss is the only text here written by hand; the rows below it all
# come out of the files.
PREFIXES = [
    ("files_", "the material: what is read, what is written, what is left"),
    ("sound_", "channels, tracks and loudness"),
    ("time_", "the common time axis"),
    ("voice_", "who speaks, and where"),
    ("cut_", "the cut by speaker, and the player over it"),
    ("project_", "what DaVinci Resolve is handed"),
    ("auphonic_", "the way out to auphonic.com and back"),
    ("window_", "the interface"),
    ("table_", "the assignment table"),
    ("run_", "a whole run: command line, threads, progress, log"),
    ("text_", "the texts: catalogue, manual, changelog"),
    ("source_", "the source itself, held by ratchets"),
]

# The list lives between these two lines. Everything outside them is
# written by hand and never touched here.
BEGIN = "<!-- overview begins -- written by overview.py, not by hand -->"
END = "<!-- overview ends -->"

# What a row looks like, and what reads one back. Both here, so the two
# cannot drift apart.
ROW = "| `%s` | %s |"
ROW_READ = re.compile(r"^\| `([a-z0-9_]+)` \| (.*?) \|$")
HEAD_READ = re.compile(r"^### `([a-z]+_)`")
NO_PREFIX_HEAD = "### Under none of the twelve"
# The tests under resolve/live/ are not in the suite and not in its
# count; they stand in a table of their own, under this heading. Two
# folders down, so resolve/ itself stays a piece like any other.
APART = "resolve/live"
APART_HEAD = "### Under `resolve/live/`"
# Where each test lies: in tests/ or in the folder under it named after
# the piece of the program it checks. This index says which; the rows
# above it stay under their prefixes.
FOLDERS_HEAD = "### By folder"
FOLDER_ROW = "| %s | %s |"
FOLDER_READ = re.compile(r"^\| (`[a-z0-9_]+/`|tests/ itself) \| (.*) \|$")
ROOT_LABEL = "tests/ itself"
# The two folders that are no piece, each named where it holds a test.
ASIDE = (("source", "`source/` is no piece: it holds the tests that read"),
         ("source", "the source, the texts and the documents as a whole."),
         ("", "A test under `tests/ itself` has no piece folder yet."))
COUNT_READ = re.compile(r"(?<![0-9])([0-9]+) tests(?![A-Za-z])")


def first_line_of(text):
    """The first line of a source's module docstring, or a stand-in.

    A test without one is a defect, not a reason to leave a row out:
    the row is written with the fault in it so it is seen in the README
    and in the red line of the test that guards it.
    """
    try:
        doc = ast.get_docstring(ast.parse(text), clean=False)
    except SyntaxError as why:
        return "(will not parse: %s)" % why
    if not doc or not doc.split("\n")[0].strip():
        return "(no docstring)"
    return doc.split("\n")[0].strip()


def ours(path, below=""):
    """Whether a test at `path`, relative and with /, is the suite's.

    With `below` empty the suite is tests/ and every folder one below
    it, which leaves resolve/live/ out; with `below` named, that folder
    alone.
    """
    parent = path.rpartition("/")[0]
    if below:
        return parent == below
    return parent == "" or ("/" not in parent and parent != APART)


def git(folder, *args):
    """What git answers in `folder`, or None where there is no git."""
    try:
        out = subprocess.run(("git", "-C", folder) + args,
                             stdout=subprocess.PIPE,
                             stderr=subprocess.DEVNULL)
    except OSError:
        return None
    return out.stdout.decode("utf-8") if out.returncode == 0 else None


def test_places(folder=HERE, below=""):
    """Every test of this repository: its name and where it lies, in pairs.

    The repository is asked, not the folder. The builder moves the tests
    a machine cannot run out of the way before the suite starts -- the
    Windows key store on a Mac, the speech model where there is none --
    so the folder there is never the whole suite. Without git, the
    folder has to do. Pairs and not a dictionary: a name lying in two
    folders comes back twice, where a dictionary would keep one of them.
    """
    here = {}
    for top in (os.listdir(folder) if os.path.isdir(folder) else ()):
        inside = os.path.join(folder, top)
        paths = [top]
        if os.path.isdir(inside) and not top.startswith((".", "__")):
            paths = [top + "/" + one for one in os.listdir(inside)]
        # A folder named deeper down, resolve/live/, is read as well.
        if below.startswith(top + "/"):
            deep = os.path.join(folder, *below.split("/"))
            if os.path.isdir(deep):
                paths += [below + "/" + one for one in os.listdir(deep)]
        for path in paths:
            if path.endswith("_test.py") and ours(path, below):
                here[path] = None
    listed = git(folder, "ls-files", "--", "*_test.py") or ""
    for line in (one.strip() for one in listed.splitlines()):
        if line.endswith("_test.py") and ours(line, below):
            here.setdefault(line, None)
    return [(path.rpartition("/")[2][:-len("_test.py")], path)
            for path in sorted(here)]


def test_sources(folder=HERE, below=""):
    """Every test of this repository, by name, with its text.

    Which tests those are, and where, is test_places's to say. A file
    that is there is read from there, so uncommitted work counts; only
    one that was moved aside is read out of the last commit. `below`
    names a folder, and a test there is that folder's and not the suite's.
    """
    out = {}
    for name, path in test_places(folder, below):
        whole = os.path.join(folder, *path.split("/"))
        if os.path.exists(whole):
            out[name] = io.open(whole, encoding="utf-8").read()
        else:
            text = git(folder, "show", "HEAD:./" + path)
            if text is not None:
                out[name] = text
    return out


def folders(folder=HERE):
    """Every test of the suite by name, and the folder it lies in.

    "" stands for tests/ itself. The folder carries the name of the
    piece of the program whose logic the test checks.
    """
    return dict((name, path.rpartition("/")[0])
                for name, path in test_places(folder))


def statements(folder=HERE, below=""):
    """Every test: its name, and what green means.

    The name is the one run.sh prints and the one a red line carries,
    so `_test.py` comes off; that is what somebody grepping the README
    after a failure has in front of them.
    """
    return dict((name, first_line_of(text))
                for name, text in test_sources(folder, below).items())


def grouped(rows):
    """The tests under their prefix, and the rest under none.

    A test whose name starts with no known prefix is not dropped. It
    gets a group of its own at the end, because a list that quietly
    leaves one out is worth less than none.
    """
    left = dict(rows)
    out = []
    for prefix, gloss in PREFIXES:
        mine = sorted(n for n in left if n.startswith(prefix))
        for name in mine:
            del left[name]
        out.append((prefix, gloss, mine))
    return out, sorted(left)


def escape(text):
    """A pipe in a statement would end the table cell it stands in."""
    return text.replace("|", "\\|")


def unescape(text):
    return text.replace("\\|", "|")


def rendered(rows, apart=None, where=None):
    """The whole block, markers included, ready to stand in the README.

    `apart` are the tests under resolve/live/, by name as resolve.sh takes
    them. Their table carries no count: the one above is the suite's.
    `where` is each suite test's folder, for the index by folder.
    """
    groups, loose = grouped(rows)
    out = [BEGIN, ""]
    out.append("%d tests. The name is the one a red line carries, and beside"
               " it the" % len(rows))
    out.append("first line of that test's docstring: what holds about the"
               " program when")
    out.append("it is green.")
    for prefix, gloss, mine in groups:
        out += ["", "### `%s` -- %s" % (prefix, gloss), "",
                "| Test | Green means |", "|---|---|"]
        for name in mine:
            out.append(ROW % (name, escape(rows[name])))
    if loose:
        out += ["", NO_PREFIX_HEAD, "",
                "These are about the suite itself rather than about a part",
                "of the program, so no prefix fits them.", "",
                "| Test | Green means |", "|---|---|"]
        for name in loose:
            out.append(ROW % (name, escape(rows[name])))
    if where:
        out += ["", FOLDERS_HEAD + " -- the piece each test checks", "",
                "A test lies in the folder named after the piece of the",
                "program under `videopodcast_magic/` whose logic it checks;",
                "`bash run.sh <name>` finds it there by its name alone."]
        out += [line for one, line in ASIDE if one in where.values()]
        out += ["", "| Folder | Tests |", "|---|---|"]
        for one in sorted(set(where.values()), key=lambda f: (not f, f)):
            label = "`%s/`" % one if one else ROOT_LABEL
            out.append(FOLDER_ROW % (label, ", ".join(
                "`%s`" % name for name in sorted(where)
                if where[name] == one)))
    if apart:
        out += ["", APART_HEAD + " -- beside a running DaVinci Resolve", "",
                "Not in the suite and not in the count above: `resolve.sh`",
                "starts these by hand, one after another.", "",
                "| Test | Green means |", "|---|---|"]
        for name in sorted(apart):
            out.append(ROW % (name, escape(apart[name])))
    out += ["", END]
    return "\n".join(out) + "\n"


def rows_in(text):
    """Read the block back: the rows, and the heading each one sits under.

    Used by the test that guards the list, so the reading and the
    writing sit in one file and cannot come apart.
    """
    inside = False
    under = ""
    out = []
    for line in text.splitlines():
        if line.strip() == BEGIN:
            inside = True
            continue
        if line.strip() == END:
            inside = False
            continue
        if not inside:
            continue
        head = HEAD_READ.match(line)
        if head:
            under = head.group(1)
        elif line.startswith(NO_PREFIX_HEAD):
            under = ""
        elif line.startswith(APART_HEAD):
            under = APART + "/"
        row = ROW_READ.match(line)
        if row:
            out.append((under, row.group(1), unescape(row.group(2))))
    return out


def folders_in(text):
    """Read the index back: every test named in it, and its folder.

    Pairs and not a dictionary, so a name standing in two rows of the
    index is seen twice rather than once.
    """
    out = []
    inside = False
    for line in text.splitlines():
        if line.strip() == BEGIN:
            inside = True
        elif line.strip() == END:
            inside = False
        row = FOLDER_READ.match(line) if inside else None
        if row:
            one = "" if row.group(1) == ROOT_LABEL else row.group(1)[1:-2]
            out += [(name, one) for name in
                    re.findall(r"`([a-z0-9_]+)`", row.group(2))]
    return out


def counts_in(text):
    """Every "N tests" the README claims, as numbers."""
    return [int(n) for n in COUNT_READ.findall(text)]


# The reading source_checks_proved keys its register by, and the account
# of how many judgements one row covers. The account judges nothing, so
# it is printed here on demand rather than in every run of that test.


def wording(call):
    """The register's key for one check(...) call, or None.

    Only the string constants inside the first argument, joined and with
    the trailing blanks off. source_checks_proved keys the register by
    it and covers() below reads the same call a second time, so the one
    place that makes a key stands here and both come to it.
    """
    words = [k.value for k in ast.walk(call.args[0])
             if isinstance(k, ast.Constant) and isinstance(k.value, str)]
    return " ".join(words).rstrip() if words else None


def judgements(source):
    """The wording of every judgement in one test.

    This, and not the file name, is what a row is tied to: a test can be
    renamed, and a row hanging on the name would be lost the moment its
    file was.

    Only the strings are read, never the shape of the expression around
    them: `ast.unparse` writes the same code differently on different
    versions of Python, and a wording that moved between 3.10 and 3.14
    would be red on the builder and green here.

    Trailing blanks come off, leading ones do not. A check name padded
    at the front is a sub-check in the printed report and stands apart
    from its unindented twin; padding at the end is invisible in every
    report and would only make the register fragile to an editor.
    """
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return []
    out = []
    for node in ast.walk(tree):
        if not (isinstance(node, ast.Call)
                and isinstance(node.func, ast.Name)
                and node.func.id == "check" and node.args):
            continue
        said = wording(node)
        if said is not None:
            out.append(said)
    if out:
        return sorted(set(out))
    # A few tests still judge with a bare assert and have no wording to
    # go by. The assertions themselves stand in for it, so those rows
    # survive a rename as well.
    lines = sorted(set(l.strip() for l in source.split("\n")
                       if l.strip().startswith("assert ")))
    return lines or sorted(set(l.strip() for l in source.split("\n")
                               if l.strip()))


# What a loop is written round, where the length of the thing inside
# decides the length of the loop.
WRAPS = ("sorted", "list", "set", "tuple", "reversed", "enumerate")


def turns(node, consts, seen=()):
    """How many turns a loop over this expression takes, or None.

    None is the honest answer wherever the source does not say: a list
    the run built, a name from elsewhere, a call that is not one of the
    handful below.
    """
    if node is None:
        return None
    if isinstance(node, (ast.List, ast.Tuple, ast.Set)):
        if any(isinstance(e, ast.Starred) for e in node.elts):
            return None
        return len(node.elts)
    if isinstance(node, ast.Dict):
        return None if any(k is None for k in node.keys) else len(node.keys)
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return len(node.value)
    if isinstance(node, ast.Name):
        if node.id in seen:
            return None
        return turns(consts.get(node.id), consts, seen + (node.id,))
    if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
        if node.func.id == "range":
            try:
                nums = [ast.literal_eval(a) for a in node.args]
            except Exception:
                return None
            if not nums or not all(isinstance(n, int) for n in nums):
                return None
            return len(range(*nums))
        if node.func.id in WRAPS:
            return turns(node.args[0] if node.args else None, consts, seen)
        if node.func.id == "zip":
            got = [turns(a, consts, seen) for a in node.args]
            if got and None not in got:
                return min(got)
            return None
    if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
        if node.func.attr in ("items", "keys", "values"):
            return turns(node.func.value, consts, seen)
    return None


def by_hand(node, consts, seen=()):
    """True where the loop runs over a list somebody wrote out.

    This is the whole of the difference the account turns on. A loop
    over a written-out list runs the same check over things that have
    nothing to do with each other -- seven constants, four folder names
    -- and breaking one of them says nothing about the six beside it. A
    loop over what the run brought runs it over data of one kind, and
    one break there does prove the mechanism.
    """
    if isinstance(node, (ast.List, ast.Tuple, ast.Set, ast.Dict,
                         ast.Constant)):
        return True
    if isinstance(node, ast.Name):
        if node.id in seen or node.id not in consts:
            return False
        return by_hand(consts[node.id], consts, seen + (node.id,))
    if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) \
            and node.func.id in WRAPS + ("zip",):
        return bool(node.args) and all(by_hand(a, consts, seen)
                                       for a in node.args)
    if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) \
            and node.func.attr in ("items", "keys", "values"):
        return by_hand(node.func.value, consts, seen)
    return False


def written_once(tree):
    """The names a loop may take its length from, with their value.

    Only a name assigned once at the top of the file, never appended to
    and not empty to start with. `started = []` filled by the loop above
    is the case this is for: read as a constant it made six judgements
    read as none.
    """
    consts, times = {}, {}
    for node in tree.body:
        if isinstance(node, ast.Assign) and len(node.targets) == 1 \
                and isinstance(node.targets[0], ast.Name):
            name = node.targets[0].id
            times[name] = times.get(name, 0) + 1
            consts[name] = node.value
    grown = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.AugAssign) and isinstance(node.target,
                                                          ast.Name):
            grown.add(node.target.id)
        if isinstance(node, ast.Call) \
                and isinstance(node.func, ast.Attribute) \
                and isinstance(node.func.value, ast.Name):
            grown.add(node.func.value.id)
    for name in list(consts):
        value = consts[name]
        empty = isinstance(value, (ast.List, ast.Tuple, ast.Set, ast.Dict)) \
            and not (getattr(value, "elts", None)
                     or getattr(value, "keys", None))
        if times[name] > 1 or name in grown or empty:
            del consts[name]
    return consts


def covers(source):
    """Per wording: how many judgements it prints, and where they come
    from.

    Four fields. `n` is how many the source says; `sites` how many
    check(...) calls carry the wording; `hand` whether any of that
    number was written out by somebody rather than brought by the run;
    `settled` whether the source really says the number.

    What it does not see, and both directions: a loop over what the run
    found counts as one, so the number is too small; a check under an
    `if` inside a loop is counted every turn, so the number is too
    large. Either way `settled` is false and the printed line says so.
    """
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return {}
    consts = written_once(tree)
    seen, calls = [], {}
    named = set()
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            named.add(node.name)

    def scan(body, factor, settled, hand, owner):
        for statement in body:
            walk(statement, factor, settled, hand, owner)

    def walk(node, factor, settled, hand, owner):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            scan(node.body, 1, True, hand, node.name)
            return
        if isinstance(node, ast.For):
            walk(node.iter, factor, settled, hand, owner)
            many = turns(node.iter, consts)
            mine = hand or by_hand(node.iter, consts)
            scan(node.body, factor if many is None else factor * many,
                 settled and many is not None, mine, owner)
            scan(node.orelse, factor, False, hand, owner)
            return
        if isinstance(node, ast.While):
            walk(node.test, factor, settled, hand, owner)
            scan(node.body + node.orelse, factor, False, hand, owner)
            return
        if isinstance(node, (ast.If, ast.Try)):
            # A branch inside a loop is the overcount: the check is
            # counted every turn and may fire on none of them. Outside a
            # loop it changes no number, so it costs nothing there.
            for field in ("test", "body", "orelse", "handlers",
                          "finalbody"):
                got = getattr(node, field, None)
                if isinstance(got, list):
                    scan(got, factor, settled and factor == 1, hand, owner)
                elif got is not None:
                    walk(got, factor, settled, hand, owner)
            return
        if isinstance(node, (ast.ListComp, ast.SetComp, ast.DictComp,
                             ast.GeneratorExp)):
            for child in ast.iter_child_nodes(node):
                walk(child, factor, False, hand, owner)
            return
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
            if node.func.id == "check" and node.args:
                seen.append({"word": wording(node), "n": factor,
                             "settled": settled, "hand": hand,
                             "owner": owner})
            elif node.func.id in named:
                calls.setdefault(node.func.id, []).append(
                    (factor, settled, hand, owner))
        for child in ast.iter_child_nodes(node):
            walk(child, factor, settled, hand, owner)

    scan(tree.body, 1, True, False, None)

    # A check inside a helper runs once per call of that helper, and the
    # call may itself sit in a loop. A helper nobody calls by name was
    # handed to a timer or a thread: it runs, and the source does not
    # say how often. Six rounds, in a fixed order: a helper that calls
    # itself never settles, and in a set's order its number moved with
    # the hash seed from one run to the next over the same files.
    weight = {None: [(1, True, False)]}
    for _ in range(6):
        moved = False
        for name in sorted(named):
            got = []
            for factor, settled, hand, owner in calls.get(name, []):
                many = len(calls[name]) > 1
                for up, up_settled, up_hand in weight.get(owner, []):
                    got.append((factor * up, settled and up_settled,
                                hand or up_hand or many))
            if not got:
                got = [(1, False, False)]
            if weight.get(name) != got:
                weight[name] = got
                moved = True
        if not moved:
            break

    out = {}
    for site in seen:
        if site["word"] is None:
            continue
        got = out.setdefault(site["word"], {"n": 0, "sites": 0,
                                            "hand": False, "settled": True})
        got["sites"] += 1
        for up, up_settled, up_hand in weight.get(site["owner"], []):
            got["n"] += site["n"] * up
            got["settled"] = got["settled"] and site["settled"] \
                and up_settled
            got["hand"] = got["hand"] or site["hand"] or up_hand
    for word in out:
        # One wording said in several places is several things by
        # definition: somebody wrote each of those calls.
        out[word]["hand"] = out[word]["hand"] or out[word]["sites"] > 1
    return out


def rows_of(path):
    """One register read: its census rows, its entries, what is malformed.

    Both registers have the same two shapes, so both are read here. A
    file that is not there reads as empty; whether it should have been
    there is a judgement, not something to raise an exception over.
    """
    census, entries, bad_shape = [], [], []
    if not os.path.exists(path):
        return census, entries, bad_shape
    for number, line in enumerate(io.open(path, encoding="utf-8"), 1):
        line = line.rstrip("\n")
        if not line.strip() or line.startswith("#"):
            continue
        # Every field but the check's own wording is stripped. That one
        # is the key, and its leading blanks belong to it.
        fields = line.split("\t")
        kind = fields[0].strip()
        if kind == "open" and len(fields) == 3:
            census.append({"name": fields[1].strip(),
                           "word": fields[2].rstrip(), "line": number})
        elif kind != "open" and len(fields) == 5:
            entries.append({"name": kind, "when": fields[1].strip(),
                            "word": fields[2].rstrip(),
                            "how": fields[3].strip(),
                            "red": fields[4].strip(), "line": number})
        else:
            bad_shape.append("line %d: %s with %d fields"
                             % (number, kind[:20], len(fields)))
    return census, entries, bad_shape


def account(folder=HERE):
    """How many judgements one register row covers, over the whole suite.

    It asks for nothing: a loop that runs one check over gathered data
    is not a fault, and demanding a counter-proof per turn would ask for
    hundreds that prove the same mechanism twice. What was missing is
    the number. It stands here and not in source_checks_proved because
    it judges nothing, and there it cost four fifths of the test's time
    in every run.
    """
    nothing = {"n": 0, "sites": 0, "hand": False, "settled": True}
    sources = test_sources(folder)
    tests = dict((name, judgements(source))
                 for name, source in sources.items())
    _census, entries, _bad_shape = rows_of(
        os.path.join(folder, "state", "counterproof"))
    proved = set((e["name"], e["word"]) for e in entries
                 if e["name"] in tests and e["word"] in tests[e["name"]])
    all_rows = judged = spare = hand_spare = 0
    big = []
    counted = {}
    for name in sorted(tests):
        said = covers(sources[name])
        counted[name] = 0
        for word in tests[name]:
            # A wording the reading did not find stands for one judgement:
            # the tests that judge with a bare assert have no check(...) to
            # read, and one is the truth for the rest of them.
            got = said.get(word) or dict(nothing, n=1, sites=1)
            many = got["n"] or 1
            all_rows += 1
            judged += many
            counted[name] += many
            if many > 1:
                spare += many - 1
                hand_spare += (many - 1) if got["hand"] else 0
                big.append((many, got["hand"], got["settled"], name, word,
                            (name, word) in proved))
    print("  %d rows over %d judgements: %d rows cover more than one, and %d "
          "judgements have no row of their own"
          % (all_rows, judged, len(big), spare))
    print("  %d of those stand under a list written out in the test, where "
          "each item is a thing of its own and unproved on its own; the "
          "other %d under a count the source knows some other way"
          % (hand_spare, spare - hand_spare))
    # What the reading does not see, in the numbers that measure it. The
    # suite writes down what each test really printed; where the run
    # printed more, a loop ran over what the run brought, and where it
    # printed fewer, a branch inside a loop did not fire every turn.
    ran = {}
    checks = os.path.join(folder, "state", "checks")
    if os.path.exists(checks):
        for line in io.open(checks, encoding="utf-8"):
            field = line.rstrip("\n").split("\t")
            if len(field) == 2 and field[0] in tests \
                    and field[1].isdigit():
                ran[field[0]] = int(field[1])
    agree = [name for name in ran if ran[name] == counted[name]]
    unplaced = sum(max(0, ran[name] - counted[name]) for name in ran)
    doubled = sum(max(0, counted[name] - ran[name]) for name in ran)
    print("  the source was read, not a run: %d of the %d tests that printed "
          "a count come to that number here" % (len(agree), len(ran)))
    print("  where they part: %d judgements the source could not place, "
          "under loops over what the run brought, and %d it placed twice, "
          "under a branch inside a loop" % (unplaced, doubled))
    big.sort(key=lambda row: (-row[0], row[3], row[4]))
    print("  the %d rows that cover most, biggest first -- a ~ means the "
          "source does not settle the number:" % min(20, len(big)))
    for many, hand, settled, name, word, is_proved in big[:20]:
        print("    %s%3d  %-9s %-6s %-27s %s"
              % (" " if settled else "~", many,
                 "by hand" if hand else "from run",
                 "proved" if is_proved else "open",
                 name, word.strip()[:32]))
    return 0


def spliced(text, block):
    """The README with the block put in place of the old one."""
    start = text.find(BEGIN)
    stop = text.find(END)
    if start < 0 or stop < 0:
        raise SystemExit("no %s / %s markers in %s" % (BEGIN, END, README))
    return text[:start] + block + text[stop + len(END) + 1:]


def main(argv):
    if "covers" in argv:
        return account()
    rows = statements()
    block = rendered(rows, statements(HERE, APART), folders())
    if "--show" in argv:
        sys.stdout.write(block)
        return 0
    text = io.open(README, encoding="utf-8").read()
    fresh = spliced(text, block)
    # The count outside the block as well, or the README says one thing
    # at the top and another in the middle.
    fresh = COUNT_READ.sub("%d tests" % len(rows), fresh)
    if fresh == text:
        print("%s is up to date: %d tests" % (README, len(rows)))
        return 0
    io.open(README, "w", encoding="utf-8").write(fresh)
    print("%s written: %d tests" % (README, len(rows)))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
