# -*- coding: utf-8 -*-
"""Which checks have been seen red, and which have not.

A check nobody has ever seen fail is not known to check anything, so
every check owes a counter-proof: the thing it is about broken on
purpose, the test run against that, the red line kept.
`state/counterproof` holds one row per check -- that red line, or a
census row where there is none yet.

There are two registers, and neither holds the other's rows. The suite's
own is state/counterproof; the tests under resolve/ want a DaVinci
Resolve really running, never take part in a run here, and keep their
proofs in resolve/counterproof. Both are held, each against the tests
that belong to it.

The sections: that the register can be read, that every entry carries
its evidence, that every row still belongs to a check that is here, the
ratchet over what is owed, red as soon as a check enters the suite
without a row of its own, the Resolve tests against their own register,
where nothing may be owed at all, and last how many judgements one row
really covers.

A row names its check by that check's wording and its test by name. So
rewording one check voids that one row and leaves its neighbours
standing, one wording in two tests stays two rows, and a renamed test is
found again by the wordings its rows carry -- the row that belongs to
nothing is the one whose test really is gone.

The last section is an account and asks for nothing: a wording inside a
loop, or said in several places, is one row over many judgements, and
until now nothing said how many. It is read out of the source -- a loop
over a list the test writes out is counted out, a check in a helper once
for every call of it, several places carrying one wording added up; a
loop over what the run brought cannot be counted at all and stands as
one, which is also the line between a row over things that have nothing
to do with each other and one over data of a kind.
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
# The Resolve suite and its own register. It is a folder apart because
# nothing in it can run without a DaVinci Resolve, and a register apart
# because a row of it would name no test the suite here knows.
RESOLVE = os.path.join(HERE, "resolve")
RESOLVE_STATE = os.path.join(RESOLVE, "counterproof")
# What the last run really printed, per test. Read in section 6 and
# nowhere held to: it says how far the reading of the source and the
# run agree, and a machine that has never run the suite has no file
# here at all.
RAN = os.path.join(HERE, "state", "checks")

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


def wording(call):
    """The register's key for one check(...) call, or None.

    Only the string constants inside the first argument, joined and with
    the trailing blanks off. Section 6 reads the same call a second time
    and has to arrive at the same key, so the one place that makes a key
    stands here and both come to it.
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
    # say how often. Six rounds settle every nesting this suite has.
    weight = {None: [(1, True, False)]}
    for _ in range(6):
        moved = False
        for name in named:
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


print("1. The register can be read")
check("state/counterproof is there", os.path.exists(STATE), STATE)
if bad:
    stop()

census, entries, bad_shape = rows_of(STATE)
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
#
# The Resolve tests are taken out of this set by name, and section 5
# holds them against their own register. By name and not by accident:
# until now they fell out of their own accord, because git lists them
# as `resolve/x_test.py`, no `x_test.py` lies here, and the way back
# through the last commit misses them too. Two mistakes cancelling --
# and mending either one would have dropped seventy-four proved checks
# into the register that is not theirs, all as fresh debts, and sent
# this ratchet up in one step.
resolve_tests = {}
if os.path.isdir(RESOLVE):
    resolve_tests = dict((name, judgements(source)) for name, source
                         in overview.test_sources(RESOLVE).items())
sources = dict((name, source)
               for name, source in overview.test_sources(HERE).items()
               if name not in resolve_tests)
tests = dict((name, judgements(source)) for name, source in sources.items())
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

# The Resolve section stands after the write-back on purpose: the two
# registers are independent, and a fault in one must not stop the other
# being brought up to date.
print("\n5. The Resolve tests, against their own register")
r_census, r_entries, r_shape = rows_of(RESOLVE_STATE)
# The two checks that keep this section from reporting nothing.
# Everything under it compares two sets, and two empty sets agree
# beautifully: a route that stopped finding the tests, or a register
# that was moved away, would leave the rest cheerfully green while
# seventy-four checks went unheld. So each side is asked for its
# existence first, and named in the line if it is missing.
check("the Resolve tests are found where their register looks for them",
      bool(resolve_tests),
      "%d test files under %s, holding %d checks"
      % (len(resolve_tests), RESOLVE,
         sum(len(v) for v in resolve_tests.values())))
check("the Resolve register holds rows at all", bool(r_entries or r_census),
      "%d proved, %d open in %s" % (len(r_entries), len(r_census),
                                    RESOLVE_STATE))
check("every Resolve row has the fields of its kind", not r_shape,
      "%d of %d rows do not: %s"
      % (len(r_shape), len(r_census) + len(r_entries) + len(r_shape),
         r_shape[:3]))
# The same evidence the other register's entries owe. Held in one line
# because a Resolve row that is short of any of the three is short of
# the whole of what it claims: somebody once saw this check fall.
thin = ["%s (line %d)" % (e["name"], e["line"]) for e in r_entries
        if "FAIL" not in e["red"] or len(e["how"]) < 8
        or not re.match(r"^\d{4}-\d{2}-\d{2}$", e["when"])]
check("every Resolve entry carries its evidence", not thin,
      "%d of %d entries short of a red line, a date or what was broken: %s"
      % (len(thin), len(r_entries), thin[:3]))
r_orphans = ["%s (line %d)" % (r["name"], r["line"])
             for r in r_entries + r_census if r["name"] not in resolve_tests]
check("no Resolve row for a test that is not there", not r_orphans,
      "%d of %d rows name %d tests that are not among the %d found: %s"
      % (len(r_orphans), len(r_entries) + len(r_census),
         len(set(o.split(" ")[0] for o in r_orphans)), len(resolve_tests),
         sorted(set(o.split(" ")[0] for o in r_orphans))[:4]))
r_void = ["%s: %s" % (e["name"], e["word"].strip()[:40]) for e in r_entries
          if e["name"] in resolve_tests
          and e["word"] not in resolve_tests[e["name"]]]
check("no Resolve entry for a check its test no longer makes", not r_void,
      "%d of %d entries: %s" % (len(r_void), len(r_entries), r_void[:3]))
# No census here, and so no ratchet: the Resolve register carries proofs
# and nothing else. A check that cannot be run without a Resolve is
# written by somebody who has one, and that is the same somebody who can
# break the one thing and keep the red line.
r_proved = set((e["name"], e["word"]) for e in r_entries
               if e["name"] in resolve_tests
               and e["word"] in resolve_tests[e["name"]])
r_owed = ["%s: %s" % (name, word.strip()[:46])
          for name in sorted(resolve_tests)
          for word in resolve_tests[name] if (name, word) not in r_proved]
r_total = sum(len(v) for v in resolve_tests.values())
check("every Resolve check carries a counter-proof of its own", not r_owed,
      "%d of %d checks in %d tests without one: %s"
      % (len(r_owed), r_total, len(resolve_tests), r_owed[:3]))
for row in r_owed:
    print("      %s -- owes a counter-proof and has no row" % row)

print("\n6. How many judgements one row covers")
# A source of a shape that is known, so the reading is held against
# numbers and not against itself. Beside each wording stands what this
# text really prints when it runs.
SAMPLE = '''
def check(name, ok, extra=""):
    pass


def in_a_helper(x):
    check("in a helper", True, x)


for name in ("first", "second", "third"):
    check("over a list written out", True, name)

for thing in what_the_run_brought:
    check("over what the run brought", True, thing)

in_a_helper(1)
in_a_helper(2)

check("said in two places", True, "here")
if True:
    check("said in two places", True, "and there")
'''
NOTHING = {"n": 0, "sites": 0, "hand": False, "settled": True}
sample = covers(SAMPLE)
written = sample.get("over a list written out", NOTHING)
brought = sample.get("over what the run brought", NOTHING)
helper = sample.get("in a helper", NOTHING)
twice = sample.get("said in two places", NOTHING)
check("a loop over a list written out in the test is counted out",
      written["n"] == 3 and written["settled"],
      "%d turns of three, settled %s" % (written["n"], written["settled"]))
check("what the source cannot count is counted as one and marked so",
      brought["n"] == 1 and not brought["settled"],
      "%d of one, settled %s" % (brought["n"], brought["settled"]))
check("a check in a helper is counted once for every call of it",
      helper["n"] == 2, "%d of the two calls" % helper["n"])
check("one wording said in several places is added up",
      twice["n"] == 2 and twice["sites"] == 2,
      "%d judgements over %d places, wanted 2 over 2"
      % (twice["n"], twice["sites"]))
check("a list written out is told from one the run brought",
      written["hand"] and not brought["hand"],
      "written out reads %s, what the run brought reads %s"
      % ("by hand" if written["hand"] else "from the run",
         "by hand" if brought["hand"] else "from the run"))

# The account itself. It asks for nothing: a loop that runs one check
# over gathered data is not a fault, and demanding a counter-proof per
# turn would ask for hundreds that prove the same mechanism twice. What
# was missing is the number, so here it is.
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
        got = said.get(word) or dict(NOTHING, n=1, sites=1)
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
print("  %d of those stand under a list written out in the test, where each "
      "item is a thing of its own and unproved on its own; the other %d "
      "under a count the source knows some other way"
      % (hand_spare, spare - hand_spare))
# What the reading does not see, in the numbers that measure it. The
# suite writes down what each test really printed, so the source and the
# run can be held against each other. Where the run printed more, a loop
# ran over what the run itself brought and the source cannot say how
# long that list was; where it printed fewer, a branch inside a loop did
# not fire every turn. Both are marked ~ in the list below.
ran = {}
if os.path.exists(RAN):
    for line in io.open(RAN, encoding="utf-8"):
        field = line.rstrip("\n").split("\t")
        if len(field) == 2 and field[0] in tests and field[1].isdigit():
            ran[field[0]] = int(field[1])
agree = [name for name in ran if ran[name] == counted[name]]
unplaced = sum(max(0, ran[name] - counted[name]) for name in ran)
doubled = sum(max(0, counted[name] - ran[name]) for name in ran)
print("  the source was read, not a run: %d of the %d tests that printed a "
      "count come to that number here" % (len(agree), len(ran)))
print("  where they part: %d judgements the source could not place, under "
      "loops over what the run brought, and %d it placed twice, under a "
      "branch inside a loop" % (unplaced, doubled))
big.sort(key=lambda row: (-row[0], row[3], row[4]))
print("  the %d rows that cover most, biggest first -- a ~ means the "
      "source does not settle the number:" % min(20, len(big)))
for many, hand, settled, name, word, is_proved in big[:20]:
    print("    %s%3d  %-9s %-6s %-27s %s"
          % (" " if settled else "~", many,
             "by hand" if hand else "from run",
             "proved" if is_proved else "open",
             name, word.strip()[:32]))

print("\n%d tests, %d checks, %d of them counter-proved, %d still owing"
      % (len(tests), sum(len(v) for v in tests.values()), len(proved), total))
print("%d Resolve tests, %d checks, %d of them counter-proved, %d still owing"
      % (len(resolve_tests), r_total, len(r_proved), len(r_owed)))
print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
