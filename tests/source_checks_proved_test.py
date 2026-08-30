# -*- coding: utf-8 -*-
"""Which tests have been seen red, and which have not.

A check nobody has ever seen fail is not known to check anything. So
every check owes a counter-proof: break the thing it is about, run it,
keep the red line. `state/counterproof` holds one entry per test that
has had one, with the red line word for word, and a census row for every
test that has not.

This is the ratchet over the rest. A test that owes a counter-proof and
is not in the census is new, and turns the suite red at once; the ones
already in it are worked off one at a time.
"""
import ast
import hashlib
import io
import overview
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
STATE = os.path.join(HERE, "state", "counterproof")

error = []
judged = []


def check(name, ok, extra=""):
    judged.append(name)
    print("  %-54s %s %s" % (name, "ok" if ok else "FAIL", extra))
    if not ok:
        error.append(name)


def stop():
    """Nothing further can be read, so say so and go."""
    print("\n%d judgements" % len(judged))
    print("\nFAIL: " + ", ".join(error))
    sys.exit(1)


def judgements(source):
    """The wording of every judgement in one test.

    This, and not the file name, is what a row is tied to: all of these
    tests are about to be renamed, and a row hanging on the name would
    be lost the moment its file was.

    Only the strings are read, never the shape of the expression around
    them: `ast.unparse` writes the same code differently on different
    versions of Python, and a fingerprint that moved between 3.10 and
    3.14 would be red on the builder and green here.
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
        words = [k.value for k in ast.walk(node.args[0])
                 if isinstance(k, ast.Constant) and isinstance(k.value, str)]
        if words:
            out.append(" ".join(words))
    if out:
        return sorted(set(out))
    # A few tests still judge with a bare assert and have no wording to
    # go by. The assertions themselves stand in for it, so those rows
    # survive a rename as well.
    lines = sorted(set(l.strip() for l in source.split("\n")
                       if l.strip().startswith("assert ")))
    return lines or sorted(set(l.strip() for l in source.split("\n")
                               if l.strip()))


def mark_of(names):
    """Twelve characters over the wording, short enough to read."""
    return hashlib.sha1("\n".join(names).encode("utf-8")).hexdigest()[:12]


print("1. The register can be read")
check("state/counterproof is there", os.path.exists(STATE), STATE)
if error:
    stop()

census = []
entries = []
bad_shape = []
for number, line in enumerate(io.open(STATE, encoding="utf-8"), 1):
    line = line.rstrip("\n")
    if not line.strip() or line.startswith("#"):
        continue
    fields = [f.strip() for f in line.split("\t")]
    if fields[0] == "open" and len(fields) == 3:
        census.append({"name": fields[1], "mark": fields[2], "line": number})
    elif fields[0] != "open" and len(fields) == 5:
        entries.append({"name": fields[0], "when": fields[1],
                        "mark": fields[2], "how": fields[3],
                        "red": fields[4], "line": number})
    else:
        bad_shape.append("line %d: %s with %d fields"
                         % (number, fields[0][:20], len(fields)))
check("every row has the fields of its kind", not bad_shape,
      str(bad_shape[:3]))
check("the register holds rows at all", bool(census or entries),
      "%d open, %d proved" % (len(census), len(entries)))
if error:
    stop()

print("\n2. Every entry carries its evidence")
# An entry without the red line in it is a claim that somebody once saw
# the test fail. That is exactly what is not worth writing down.
no_red = ["%s (line %d)" % (e["name"], e["line"]) for e in entries
          if "FAIL" not in e["red"]]
check("every entry holds a red line", not no_red, str(no_red[:3]))
no_how = ["%s (line %d)" % (e["name"], e["line"]) for e in entries
          if len(e["how"]) < 8]
check("every entry says what was broken", not no_how, str(no_how[:3]))
undated = ["%s: %r" % (e["name"], e["when"]) for e in entries
           if not re.match(r"^\d{4}-\d{2}-\d{2}$", e["when"])]
check("every entry says when", not undated, str(undated[:3]))
marks = [r["mark"] for r in census + entries]
twice = sorted(set(m for m in marks if marks.count(m) > 1))
check("no test in the register twice", not twice, str(twice[:3]))

print("\n3. Every row belongs to a test that is here")
# The repository, not the folder: the builder moves the tests a machine
# cannot run out of the way before the suite starts, so counting what
# lies about would make every such machine red for what is not a fault.
tests = dict((name, mark_of(judgements(source)))
             for name, source in overview.test_sources(HERE).items())
by_mark = dict((mark, name) for name, mark in tests.items())

# A row whose fingerprint is still somewhere in the folder belongs to
# that file, whatever the file is called today. A row that matches by
# name alone belongs to a test that has been rewritten since. What
# matches neither is dead wood, and it has to be seen: otherwise the
# register fills with rows for tests that are gone and the count stops
# meaning anything.
proved = {}
still_open = {}
stale = []
orphans = []
for row in entries:
    if row["mark"] in by_mark:
        proved[by_mark[row["mark"]]] = row
    elif row["name"] in tests:
        stale.append("%s (counter-proved %s)" % (row["name"], row["when"]))
    else:
        orphans.append("%s (line %d, proved)" % (row["name"], row["line"]))
for row in census:
    if row["mark"] in by_mark:
        still_open[by_mark[row["mark"]]] = row
    elif row["name"] in tests:
        # An open test that was edited is still open. Its fingerprint is
        # written straight below; going red here would mean nobody could
        # touch one of them without a counter-proof they do not owe yet.
        still_open[row["name"]] = row
    else:
        orphans.append("%s (line %d, open)" % (row["name"], row["line"]))
check("no row for a test that is gone", not orphans, str(orphans[:4]))
for row in orphans:
    print("      %s" % row)
# Kept apart from the count below: this is one test to look at, and the
# line has to say which one and why.
check("no entry whose test has been rewritten since", not stale,
      str(stale[:4]))
for row in stale:
    print("      %s" % row)

print("\n4. The tests still owing a counter-proof")
owing = sorted(name for name in tests if name not in proved)
new = [name for name in owing if name not in still_open]
check("every test owing one is in the register: %d owing, %d new"
      % (len(owing), len(new)), not new, str(new[:3]))
for name in new:
    print("      %s_test.py owes a counter-proof and has no row"
          % name)
both = sorted(set(proved) & set(still_open))
check("no test both proved and open", not both, str(both[:4]))

# The register is written back for three reasons and no others: a test
# was renamed and the name beside its row has gone stale, an open test
# was edited, or one of them has been counter-proved and its open row
# has to go. The evidence itself is never touched by a program.
if not error:
    text = io.open(STATE, encoding="utf-8").read()
    was = text
    done = [row for name, row in still_open.items() if name in proved]
    for row in done:
        text = text.replace("open\t%s\t%s\n" % (row["name"], row["mark"]), "")
    for name, row in sorted(still_open.items()):
        if name in proved:
            continue
        fresh = "open\t%s\t%s" % (name, tests[name])
        old = "open\t%s\t%s" % (row["name"], row["mark"])
        if fresh != old:
            text = text.replace(old + "\n", fresh + "\n", 1)
            print("      written straight: %s -> %s" % (old, fresh))
    for name, row in sorted(proved.items()):
        if row["name"] != name:
            text = re.sub(r"(?m)^%s\t" % re.escape(row["name"]),
                          "%s\t" % name, text, 1)
            print("      renamed in the register: %s -> %s"
                  % (row["name"], name))
    if done:
        print("      ratchet tightened: %d -> %d"
              % (len(still_open), len(still_open) - len(done)))
    if text != was:
        io.open(STATE, "w", encoding="utf-8").write(text)

print("\n%d tests, %d of them counter-proved, %d judgements"
      % (len(tests), len(proved), len(judged)))
print("\n%s" % ("All good." if not error else "FAIL: " + ", ".join(error)))
sys.exit(1 if error else 0)
