# -*- coding: utf-8 -*-
"""Which checks have been seen red, and which have not.

A check nobody has ever seen fail is not known to check anything, so
every check owes a counter-proof: the thing it is about broken on
purpose, the test run against that, the red line kept.
`state/counterproof` holds one row per check -- that red line, or a
census row where there is none yet.

The sections: that the register can be read, that every entry carries
its evidence, that every row still belongs to a check that is here, and
the ratchet over what is owed, red as soon as a check enters the suite
without a row of its own.

A row names its check by that check's wording and its test by name. So
rewording one check voids that one row and leaves its neighbours
standing, one wording in two tests stays two rows, and a renamed test is
found again by the wordings its rows carry -- the row that belongs to
nothing is the one whose test really is gone.
"""
import ast
import io
import overview
import os
import re
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
STATE = os.path.join(HERE, "state", "counterproof")

began = time.time()
done = 0
bad = []


def check(name, ok, extra=""):
    global done
    done += 1
    print("  %-58s %s %s" % (name, "ok" if ok else "FAIL", extra))
    if not ok:
        bad.append("%s [%s]" % (name, extra or "no numbers"))


def stop():
    """Nothing further can be read, so say so and go."""
    print("\n%d checks in %.2f s" % (done, time.time() - began))
    print("FAIL: " + " | ".join(bad))
    sys.exit(1)


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
        words = [k.value for k in ast.walk(node.args[0])
                 if isinstance(k, ast.Constant) and isinstance(k.value, str)]
        if words:
            out.append(" ".join(words).rstrip())
    if out:
        return sorted(set(out))
    # A few tests still judge with a bare assert and have no wording to
    # go by. The assertions themselves stand in for it, so those rows
    # survive a rename as well.
    lines = sorted(set(l.strip() for l in source.split("\n")
                       if l.strip().startswith("assert ")))
    return lines or sorted(set(l.strip() for l in source.split("\n")
                               if l.strip()))


print("1. The register can be read")
check("state/counterproof is there", os.path.exists(STATE), STATE)
if bad:
    stop()

census = []
entries = []
bad_shape = []
for number, line in enumerate(io.open(STATE, encoding="utf-8"), 1):
    line = line.rstrip("\n")
    if not line.strip() or line.startswith("#"):
        continue
    # Every field but the check's own wording is stripped. That one is
    # the key, and its leading blanks belong to it.
    fields = line.split("\t")
    kind = fields[0].strip()
    if kind == "open" and len(fields) == 3:
        census.append({"name": fields[1].strip(), "word": fields[2].rstrip(),
                       "line": number})
    elif kind != "open" and len(fields) == 5:
        entries.append({"name": kind, "when": fields[1].strip(),
                        "word": fields[2].rstrip(), "how": fields[3].strip(),
                        "red": fields[4].strip(), "line": number})
    else:
        bad_shape.append("line %d: %s with %d fields"
                         % (number, kind[:20], len(fields)))
check("every row has the fields of its kind", not bad_shape,
      "%d of %d rows do not: %s"
      % (len(bad_shape), len(census) + len(entries) + len(bad_shape),
         bad_shape[:3]))
check("the register holds rows at all", bool(census or entries),
      "%d open, %d proved" % (len(census), len(entries)))
if bad:
    stop()

print("\n2. Every entry carries its evidence")
# An entry without the red line in it is a claim that somebody once saw
# the check fail. That is exactly what is not worth writing down.
no_red = ["%s (line %d)" % (e["name"], e["line"]) for e in entries
          if "FAIL" not in e["red"]]
check("every entry holds a red line", not no_red,
      "%d of %d without one: %s" % (len(no_red), len(entries), no_red[:3]))
no_how = ["%s (line %d)" % (e["name"], e["line"]) for e in entries
          if len(e["how"]) < 8]
check("every entry says what was broken", not no_how,
      "%d of %d without it: %s" % (len(no_how), len(entries), no_how[:3]))
undated = ["%s: %r" % (e["name"], e["when"]) for e in entries
           if not re.match(r"^\d{4}-\d{2}-\d{2}$", e["when"])]
check("every entry says when", not undated,
      "%d of %d undated: %s" % (len(undated), len(entries), undated[:3]))
# The pair, never the wording on its own: nineteen wordings stand in
# more than one test -- "English label", "and it says why" -- and a key
# over the wording alone would fold them into one row.
keys = [(r["name"], r["word"]) for r in census + entries]
twice = sorted(set(k for k in keys if keys.count(k) > 1))
check("no check in the register twice", not twice,
      "%d of %d rows doubled: %s" % (len(twice), len(keys), twice[:3]))

print("\n3. Every row belongs to a check that is here")
# The repository, not the folder: the builder moves the tests a machine
# cannot run out of the way before the suite starts, so counting what
# lies about would make every such machine red for what is not a fault.
tests = dict((name, judgements(source))
             for name, source in overview.test_sources(HERE).items())
rows_by_name = {}
for row in entries + census:
    rows_by_name.setdefault(row["name"], []).append(row)

# A renamed test is found again by the wordings its rows carry. The
# whole group has to fit, and only a test that has no rows of its own
# can take them: one wording shared with another file proves nothing,
# a majority does -- of the group and of the test it would move to, or
# a five-check test with one wording in common would swallow the single
# row of a test that was deleted. A tie is left alone rather than
# guessed.
taken = set(name for name in rows_by_name if name in tests)
renamed = {}
for old in sorted(n for n in rows_by_name if n not in tests):
    mine = set(r["word"] for r in rows_by_name[old])
    fits = sorted(((len(mine & set(tests[t])), t)
                   for t in tests
                   if t not in taken
                   and len(mine & set(tests[t])) * 2 > len(tests[t])),
                  reverse=True)
    if fits and fits[0][0] * 2 > len(mine) and (
            len(fits) == 1 or fits[0][0] > fits[1][0]):
        renamed[old] = fits[0][1]
        taken.add(fits[0][1])
for row in entries + census:
    row["name"] = renamed.get(row["name"], row["name"])

orphans = ["%s (line %d)" % (r["name"], r["line"]) for r in entries + census
           if r["name"] not in tests]
check("no row for a test that is gone", not orphans,
      "%d rows for %d tests that are not here: %s"
      % (len(orphans), len(set(o.split(" ")[0] for o in orphans)),
         sorted(set(o.split(" ")[0] for o in orphans))[:4]))
for row in sorted(set(orphans)):
    print("      %s names no test in the repository" % row)

# This is the one the rebuild is about. An entry stands or falls with
# its own check, and with no other: rewording a judgement voids the row
# under it and leaves the sixty-four beside it alone. Open rows are not
# held to it -- they owe a counter-proof either way, and nobody should
# have to produce one before they may touch a check.
void = ["%s: %s" % (e["name"], e["word"].strip()[:40]) for e in entries
        if e["name"] in tests and e["word"] not in tests[e["name"]]]
check("no entry for a check its test no longer makes", not void,
      "%d of %d entries: %s" % (len(void), len(entries), void[:3]))
for row in void:
    print("      %s -- reworded or gone since its counter-proof" % row)

print("\n4. The checks still owing a counter-proof")
proved = set((e["name"], e["word"]) for e in entries
             if e["name"] in tests and e["word"] in tests[e["name"]])
listed = set((r["name"], r["word"]) for r in census)
# The number this prints counts checks, not tests. It went from 100 to
# 2498 the day the register was rebuilt, and that is not a rise: a file
# with sixty-five checks used to be counted as one debt as soon as any
# one of them had been proved. Nothing came undone that day; the count
# stopped understating what is owed.
#
# What a test owed before is what it had rows for: its open rows, plus
# the entries that have just gone void. A reworded check moves from the
# one to the other, so the debt does not rise and only the line above
# speaks. A check that was not there yesterday does raise it.
owed = {}
new = []
grew = []
for name in sorted(tests):
    owed[name] = [w for w in tests[name] if (name, w) not in proved]
    before = len([r for r in census if r["name"] == name]) + len(
        [e for e in entries if e["name"] == name
         and e["word"] not in tests[name]])
    if len(owed[name]) > before:
        grew.append("%s: %d against %d" % (name, len(owed[name]), before))
        new += ["%s: %s" % (name, w.strip()[:46]) for w in owed[name]
                if (name, w) not in listed]
total = sum(len(v) for v in owed.values())
check("every check owing one is in the register: %d owing, %d new"
      % (total, len(new)), not new, "%s %s" % (grew[:2], new[:2]))
for row in new:
    print("      %s -- owes a counter-proof and has no row" % row)

# The register is written back for three reasons and no others: a test
# was renamed and the name beside its rows has gone stale, a check that
# owes a counter-proof was reworded or added or taken away, or one of
# them has been proved and its open row has become an entry. The
# evidence itself -- the date, what was broken, the red line -- is never
# touched by a program.
#
# A test whose source will not parse has no wordings at all, and
# regenerating against it would throw its rows away. So nothing is
# written in that case; a test in that state is red on its own account.
mute = sorted(name for name in tests if not tests[name])
for name in mute:
    print("      %s makes no judgement this can read -- nothing written back"
          % name)
if not bad and not mute:
    head = []
    for line in io.open(STATE, encoding="utf-8"):
        if line.strip() and not line.startswith("#"):
            break
        head.append(line)
    while head and not head[-1].strip():
        head.pop()
    out = head + ["\n"]
    for name in sorted(tests):
        kept = dict((e["word"], e) for e in entries if e["name"] == name)
        for word in tests[name]:
            if word in kept:
                e = kept[word]
                out.append("%s\t%s\t%s\t%s\t%s\n"
                           % (name, e["when"], word, e["how"], e["red"]))
            else:
                out.append("open\t%s\t%s\n" % (name, word))
    for old, now in sorted(renamed.items()):
        print("      renamed in the register: %s -> %s" % (old, now))
    if total < len(census):
        print("      ratchet tightened: %d -> %d" % (len(census), total))
    text = "".join(out)
    if text != io.open(STATE, encoding="utf-8").read():
        io.open(STATE, "w", encoding="utf-8").write(text)

print("\n%d tests, %d checks, %d of them counter-proved, %d still owing"
      % (len(tests), sum(len(v) for v in tests.values()), len(proved), total))
print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
