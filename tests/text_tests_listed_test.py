# -*- coding: utf-8 -*-
"""README.md lists every test with the sentence that test stands for.

The list at the end of tests/README.md is the only place where all the
tests are described together, and a list kept by hand is wrong within a
week. So the docstrings are the source, overview.py writes the list out
of them, and this holds the written list against the folder:

  1. every test in tests/ has a row, and every row a test
  2. no test stands there twice
  3. each row repeats that test's own first docstring line
  4. the number of tests the README names is the number there are
  5. each row stands under the heading of its own prefix
  6. the same for the tests under resolve/, in a table of their own

Nothing here is a matter of taste: whatever it finds, `python3
overview.py` writes right again, and the reading and the writing of
the list live in overview.py together.
"""
import io
import os
import sys
import time

began = time.time()
HERE = os.path.dirname(os.path.abspath(__file__))
README = os.path.join(HERE, "README.md")

done = 0
bad = []


def check(name, ok, extra=""):
    global done
    done += 1
    print("  %-54s %s %s" % (name, "ok" if ok else "FAIL", extra))
    if not ok:
        bad.append("%s [%s]" % (name, extra or "no numbers"))


def stop():
    """Nothing further can be read, so say so and go.

    Every way out of this test passes the count and the exit code, this
    one included: a precondition that failed must not look like a run
    that judged nothing.
    """
    print("\n%d checks in %.2f s" % (done, time.time() - began))
    print("FAIL: " + " | ".join(bad) + " -- fix with: python3 overview.py")
    sys.exit(1)


print("1. The list can be read at all")
sys.path.insert(0, HERE)
try:
    import overview
except ImportError as why:
    check("overview.py is beside the tests", False, str(why))
    stop()
check("overview.py is beside the tests", True, overview.__file__)

if not os.path.exists(README):
    check("README.md is there", False, README)
    stop()
check("README.md is there", True, README)

text = io.open(README, encoding="utf-8").read()
rows = overview.rows_in(text)
# Without this the two checks below run over an empty list and pass on
# the strength of what is missing: no rows means nothing is missing
# from the rows either.
check("the list stands between its two markers", len(rows) > 20,
      "%d rows read between %r and %r"
      % (len(rows), overview.BEGIN[:24], overview.END[:20]))
if bad:
    stop()

here = overview.statements(HERE)
# The tests under resolve/ are held apart, in section 6: they are not in
# the suite, so neither in its count nor under its headings.
APART = overview.APART + "/"
suite_rows = [row for row in rows if row[0] != APART]
listed = dict((name, said) for _, name, said in suite_rows)

print("\n2. It names the tests that are here, and only those")
missing = sorted(set(here) - set(listed))
check("every test in the folder has a row", not missing,
      "%d without one: %s" % (len(missing), ", ".join(missing)))
gone = sorted(set(listed) - set(here))
check("every row names a test that is here", not gone,
      "%d name none: %s" % (len(gone), ", ".join(gone[:4])))
# A name twice over is invisible to both checks above: the sets match
# and one row silently covers the other.
seen = [(under == APART, name) for under, name, _ in rows]
twice = sorted(set(n for apart, n in seen if seen.count((apart, n)) > 1))
check("no test stands in the list twice", not twice,
      "%d twice over: %s" % (len(twice), ", ".join(twice[:4])))

print("\n3. And says what each of them says")
# The row against the docstring, word for word. Anything looser and a
# reworded head stays unnoticed, which is the whole reason for this.
apart = []
for name in sorted(set(here) & set(listed)):
    if listed[name] != here[name]:
        apart.append("%s: the list says %r, the test says %r"
                     % (name, listed[name][:60], here[name][:60]))
check("every row repeats the test's own first line", not apart,
      "%d differ -- %s" % (len(apart), " ; ".join(apart[:2])))

print("\n4. And counts them")
named = overview.counts_in(text)
wrong = sorted(set(n for n in named if n != len(here)))
check("the number the README names is the number there are", not wrong,
      "the README says %s, the folder holds %d test files"
      % (sorted(set(named)) or "no number at all", len(here)))

print("\n5. And each one under its own heading")
# The prefix says which part of the program a red line is about, so a
# row under the wrong heading sends the reader to the wrong place.
elsewhere = []
for under, name, _ in suite_rows:
    fits = [p for p, _gloss in overview.PREFIXES if name.startswith(p)]
    wanted = fits[0] if fits else ""
    if under != wanted:
        elsewhere.append("%s stands under %r, belongs under %r"
                         % (name, under or "no prefix",
                            wanted or "no prefix"))
check("every row stands under the heading of its prefix", not elsewhere,
      "%d in the wrong place -- %s"
      % (len(elsewhere), " ; ".join(elsewhere[:2])))

print("\n6. And the tests under resolve/ in a table of their own")
apart_here = overview.statements(HERE, overview.APART)
apart_listed = dict((name, said) for under, name, said in rows
                    if under == APART)
# Without this the three below pass over nothing, the way section 1
# guards sections 2 to 5.
check("the tests under resolve/ are found at all", len(apart_here) > 0,
      "%d found in %s" % (len(apart_here), os.path.join(HERE, APART)))
missing = sorted(set(apart_here) - set(apart_listed))
check("every test under resolve/ has a row in its own table", not missing,
      "%d of %d without one: %s"
      % (len(missing), len(apart_here), ", ".join(missing)))
gone = sorted(set(apart_listed) - set(apart_here))
check("every resolve/ row names a test under resolve/", not gone,
      "%d name none: %s" % (len(gone), ", ".join(gone[:4])))
apart = ["%s: the list says %r, the test says %r"
         % (name, apart_listed[name][:60], apart_here[name][:60])
         for name in sorted(set(apart_here) & set(apart_listed))
         if apart_listed[name] != apart_here[name]]
check("every resolve/ row repeats its test's own first line", not apart,
      "%d differ -- %s" % (len(apart), " ; ".join(apart[:2])))

print("\n%d checks in %.2f s" % (done, time.time() - began))
if bad:
    print("FAIL: " + " | ".join(bad) + " -- fix with: python3 overview.py")
else:
    print("ALL OK")
sys.exit(1 if bad else 0)
