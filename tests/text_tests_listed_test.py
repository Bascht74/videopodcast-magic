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

Nothing here is a matter of taste: whatever it finds, `python3
overview.py` writes right again. The reading of the list and the
writing of it live in overview.py together, so the two cannot drift
apart.
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
listed = dict((name, said) for _, name, said in rows)

print("\n2. It names the tests that are here, and only those")
missing = sorted(set(here) - set(listed))
check("every test in the folder has a row", not missing,
      "%d without one: %s" % (len(missing), ", ".join(missing[:4])))
gone = sorted(set(listed) - set(here))
check("every row names a test that is here", not gone,
      "%d name none: %s" % (len(gone), ", ".join(gone[:4])))
# A name twice over is invisible to both checks above: the sets match
# and one row silently covers the other.
seen = [name for _, name, _ in rows]
twice = sorted(set(n for n in seen if seen.count(n) > 1))
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
for under, name, _ in rows:
    fits = [p for p, _gloss in overview.PREFIXES if name.startswith(p)]
    wanted = fits[0] if fits else ""
    if under != wanted:
        elsewhere.append("%s stands under %r, belongs under %r"
                         % (name, under or "no prefix",
                            wanted or "no prefix"))
check("every row stands under the heading of its prefix", not elsewhere,
      "%d in the wrong place -- %s"
      % (len(elsewhere), " ; ".join(elsewhere[:2])))

print("\n%d checks in %.2f s" % (done, time.time() - began))
if bad:
    print("FAIL: " + " | ".join(bad) + " -- fix with: python3 overview.py")
else:
    print("ALL OK")
sys.exit(1 if bad else 0)
