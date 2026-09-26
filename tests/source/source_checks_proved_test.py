# -*- coding: utf-8 -*-
"""Which checks have been seen red, and which have not.

A check nobody has ever seen fail is not known to check anything, so
every check owes a counter-proof: the thing it is about broken on
purpose, the test run against that, the red line kept.
`state/counterproof` holds one row per check -- that red line, or a
census row where there is none yet.

There are two registers, and neither holds the other's rows. The suite's
own is state/counterproof; the tests under resolve/live/ want a
DaVinci Resolve really running, never take part in a run here, and
keep their proofs in resolve/live/counterproof. Both are held, each
against the tests that belong to it.

The sections: that the register can be read, that every entry carries
its evidence and that a program or test file it names by its path from
the repository's top is one the repository holds, that every row still
belongs to a check that is here, the ratchet over what is owed, red as
soon as a check enters the suite without a row of its own, the Resolve
tests against their own register, where nothing may be owed at all, and
last the reading that says how many judgements one row really covers,
held against a text of a known shape. Where a row broke is held to the
files it names, not to the functions: a break invents names of its own
often enough.

A row names its check by that check's wording and its test by name. So
rewording one check voids that one row and leaves its neighbours
standing, one wording in two tests stays two rows, and a renamed test is
found again by the wordings its rows carry -- the row that belongs to
nothing is the one whose test really is gone.

The account itself -- how many judgements each row covers across the
suite -- asks for nothing, so it is not printed here: `python3
overview.py covers` prints it, and the reading and the register's key
both live in overview.py. A loop over a list the test writes out is
counted out, a check in a helper once for every call of it, several
places carrying one wording added up; a loop over what the run brought
cannot be counted, stands as one, and is told apart from a list somebody
wrote out.
"""
PLATFORM_BOUND = False
import os
import sys
# tests/, where the helpers and state/ lie; this file may stand in a
# folder under it, or in one under that.
HERE = os.path.dirname(os.path.abspath(__file__))
while not os.path.isfile(os.path.join(HERE, "the_program.py")) \
        and os.path.dirname(HERE) != HERE:
    HERE = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import io
import overview
import re
import time

STATE = os.path.join(HERE, "state", "counterproof")
# The Resolve suite and its own register. It is a folder apart because
# nothing in it can run without a DaVinci Resolve, and a register apart
# because a row of it would name no test the suite here knows.
RESOLVE = os.path.join(HERE, "resolve", "live")
RESOLVE_STATE = os.path.join(RESOLVE, "counterproof")

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


print("1. The register can be read")
check("state/counterproof is there", os.path.exists(STATE), STATE)
if bad:
    stop()

census, entries, bad_shape = overview.rows_of(STATE)
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
# What was broken says where, so that somebody can break it there again.
# The day the tests went into folders of their own that place died under
# rows by the dozen and nothing said so. So a path of the two shapes the
# repository has, videopodcast_magic/....py and tests/....py, has to be
# one it holds. Only those two: the one file the program was before it
# became a folder has another shape, and a path counted from tests/
# ("resolve/...") is not told apart from one counted from the program.
# A function's name is not asked -- a break invents its own often
# enough -- and neither is a path the break itself makes, in the four
# words the register says that with: copied to, renamed to, written back
# as, and a path followed by "written,". Anything else a path follows,
# "appended to" as well, names a place that has to be there. The red
# line is not read; it is evidence, and stays as the run printed it.
# The repository and not the folder, as in section 3, for the builder
# moves tests aside.
ROOT = os.path.dirname(HERE)
NAMED = re.compile(
    r"(?<![\w.-])((?:videopodcast_magic|tests)/[\w./-]*?\.py)\b")
MADE_AFTER = ("copied to ", "renamed to ", "written back as ")
held = set((overview.git(ROOT, "ls-files") or "").splitlines())
named = 0
nowhere = []
for register, rows in (("state/counterproof", entries),
                       ("resolve/live/counterproof",
                        overview.rows_of(RESOLVE_STATE)[1])):
    for e in rows:
        for m in NAMED.finditer(e["how"]):
            if e["how"][:m.start()].endswith(MADE_AFTER) \
                    or e["how"][m.end():].startswith(" written,"):
                continue
            named += 1
            if m.group(1) not in held and not os.path.isfile(
                    os.path.join(ROOT, *m.group(1).split("/"))):
                nowhere.append("%s, %s: %s"
                               % (register, e["name"], m.group(1)))
check("every path a register row names exists", not nowhere,
      "%d of %d paths named are not in the repository: %s"
      % (len(nowhere), named, nowhere[:3]))
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
# holds them against their own register. They lie in resolve/live/, two
# folders down, and the suite's own list reaches one folder down and
# leaves that one out by name -- tests/resolve/ itself is a piece like
# any other, and its tests are the suite's. By name here as well, and
# not by that list alone: once they fell out of it by accident, two
# mistakes cancelling, and mending either would have dropped
# seventy-four proved checks into the register that is not theirs, all
# as fresh debts, and sent this ratchet up in one step.
resolve_tests = {}
if os.path.isdir(RESOLVE):
    resolve_tests = dict((name, overview.judgements(source)) for name, source
                         in overview.test_sources(RESOLVE).items())
sources = dict((name, source)
               for name, source in overview.test_sources(HERE).items()
               if name not in resolve_tests)
tests = dict((name, overview.judgements(source))
             for name, source in sources.items())
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
r_census, r_entries, r_shape = overview.rows_of(RESOLVE_STATE)
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

print("\n6. The reading that says how many judgements one row covers")
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
sample = overview.covers(SAMPLE)
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
print("  the account over the whole suite: python3 overview.py covers")

print("\n%d tests, %d checks, %d of them counter-proved, %d still owing"
      % (len(tests), sum(len(v) for v in tests.values()), len(proved), total))
print("%d Resolve tests, %d checks, %d of them counter-proved, %d still owing"
      % (len(resolve_tests), r_total, len(r_proved), len(r_owed)))
print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
