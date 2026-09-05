# -*- coding: utf-8 -*-
"""Every copy of the skill table says what the skills themselves say.

Four documents send a reader to `.claude/skills/`: CLAUDE.md,
CONTRIBUTING.md, AGENTS.md and the pull request template. All four
carried the table by hand until 5.9.2026, in four wordings, and by then
it was already wrong -- `ci` stood in none of them. So each SKILL.md
carries its own row now and development/skill_table.py writes the
copies out of them; this holds the written copies against the skills:

  1. the generator can be read at all
  2. every skill says where its row goes, and to a copy that exists
  3. each copy really has a table between its two markers
  4. and that table holds the rows those skills ask for, in order

Nothing here is a matter of taste: whatever it finds, `python3
development/skill_table.py` writes right again. The reading of a table
and the writing of it live in that one file, so the two cannot drift
apart.
"""
import io
import os
import sys
import time

began = time.time()
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)

done = 0
bad = []


def check(name, ok, extra=""):
    global done
    done += 1
    print("  %-58s %s %s" % (name, "ok" if ok else "FAIL", extra))
    if not ok:
        bad.append("%s [%s]" % (name, extra or "no numbers"))


def stop():
    """Nothing further can be read, so say so and go.

    Every way out of this test passes the count and the exit code, this
    one included: a precondition that failed must not look like a run
    that judged nothing.
    """
    print("\n%d checks in %.2f s" % (done, time.time() - began))
    print("FAIL: " + " | ".join(bad)
          + " -- fix with: python3 development/skill_table.py")
    sys.exit(1)


print("1. The generator can be read at all")
sys.path.insert(0, os.path.join(ROOT, "development"))
try:
    import skill_table
except ImportError as why:
    check("the generator stands under development/", False, str(why))
    stop()
check("the generator stands under development/", True, skill_table.__file__)

print("\n2. Every skill says where its row goes")
found = skill_table.skills()
# The floor first. Without it the three comparisons below run over two
# empty lists and pass on the strength of what is missing: no skills
# means no rows missing from any copy either.
check("the skills folder holds the skills", len(found) > 6,
      "%d folders with a SKILL.md under %s"
      % (len(found), os.path.join(".claude", "skills")))
if bad:
    stop()

short = []
for one in found:
    lacks = [f for f in ("when", "tables", "order") if not one.get(f)]
    if lacks:
        short.append("%s has no %s" % (one["name"], ", ".join(lacks)))
check("every skill carries a when, a tables and an order", not short,
      "%d of %d incomplete -- %s"
      % (len(short), len(found), " ; ".join(short[:3])))

known = [copy[0] for copy in skill_table.COPIES]
astray = []
for one in found:
    for where in one.get("tables") or []:
        if where not in known:
            astray.append("%s sends its row to %r" % (one["name"], where))
check("every skill sends its row to a copy that exists", not astray,
      "%d astray of %d, and the copies are %s -- %s"
      % (len(astray), len(found), ", ".join(known), " ; ".join(astray[:3])))

print("\n3. Each copy has a table between its two markers")
text = {}
listed = {}
for key, where, _begin, _end, _left, _right in skill_table.COPIES:
    path = os.path.join(ROOT, where)
    text[key] = (io.open(path, encoding="utf-8").read()
                 if os.path.exists(path) else "")
    listed[key] = skill_table.rows_in(key, text[key])


def found_after(key):
    """How many rows were read in one copy, and where the reading began.

    The judgement stays outside: a `check` whose name is worked out by
    a helper leaves one wording for three checks, and the counter-proof
    register can then not say which of the three was ever seen red.
    """
    begin, where = ([c[2] for c in skill_table.COPIES if c[0] == key][0],
                    [c[1] for c in skill_table.COPIES if c[0] == key][0])
    return "%d rows read after %r in %s" % (len(listed[key]), begin[:34],
                                            where)


check("CLAUDE.md has its table between its markers",
      len(listed["claude"]) > 3, found_after("claude"))
check("CONTRIBUTING.md has its table between its markers",
      len(listed["contributing"]) > 3, found_after("contributing"))
check("AGENTS.md has its table between its markers",
      len(listed["agents"]) > 3, found_after("agents"))
check("the pull request template has its table between its markers",
      len(listed["pr"]) > 3, found_after("pr"))

print("\n4. And every table says what those skills say")
# One check per copy, written out. A loop over the three would leave
# one wording for three judgements, and the register could then not say
# which of them was ever seen red.
claude = skill_table.apart(skill_table.rows_for("claude", found),
                           listed["claude"])
check("CLAUDE.md holds the rows its skills ask for", not claude,
      "%d wrong of %d rows -- %s"
      % (len(claude), len(listed["claude"]), " ; ".join(claude[:2])))

giving = skill_table.apart(skill_table.rows_for("contributing", found),
                           listed["contributing"])
check("CONTRIBUTING.md holds the rows its skills ask for", not giving,
      "%d wrong of %d rows -- %s"
      % (len(giving), len(listed["contributing"]), " ; ".join(giving[:2])))

agents = skill_table.apart(skill_table.rows_for("agents", found),
                           listed["agents"])
check("AGENTS.md holds the rows its skills ask for", not agents,
      "%d wrong of %d rows -- %s"
      % (len(agents), len(listed["agents"]), " ; ".join(agents[:2])))

asking = skill_table.apart(skill_table.rows_for("pr", found), listed["pr"])
check("the pull request template holds the rows its skills ask for",
      not asking,
      "%d wrong of %d rows -- %s"
      % (len(asking), len(listed["pr"]), " ; ".join(asking[:2])))

print("\n%d checks in %.2f s" % (done, time.time() - began))
if bad:
    print("FAIL: " + " | ".join(bad)
          + " -- fix with: python3 development/skill_table.py")
else:
    print("ALL OK")
sys.exit(1 if bad else 0)
