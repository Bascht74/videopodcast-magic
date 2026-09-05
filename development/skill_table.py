# -*- coding: utf-8 -*-
"""Writes the skill table into the four documents that carry it.

`.claude/skills/` holds one document per situation, and four places
send a reader to them: `CLAUDE.md` for whoever works here,
`CONTRIBUTING.md` for somebody from outside, `AGENTS.md` for an agent
that is not Claude, and `.github/pull_request_template.md` for somebody
opening a pull request. All four carried the table by hand until
5.9.2026, in four wordings, and by then it was already wrong: `ci` --
165 lines about the situation after *every* push -- stood in none of
them.

So the skills are the source and this writes the copies out of them.
Each `SKILL.md` carries three fields of its own beside its `name` and
its `description`:

    when:    the situation, one line, as it stands in the table
    tables:  which of the copies show the row -- claude, contributing,
             agents, pr, comma-separated
    order:   where the row stands; the same order in all of them

`description` was measured first and does not do: it is 146 to 264
characters and says both the situation and what the document teaches,
while a table cell is 20 to 94. Cutting one out of the other would be
guesswork per skill, so the row is written where the skill is.

    python3 development/skill_table.py           # write the copies
    python3 development/skill_table.py --check   # compare, change nothing
    python3 development/skill_table.py --show    # print, change nothing

`--check` returns 1 and names every copy that has gone stale, with what
is missing, extra or reworded in it. `text_skills_listed_test.py` runs
the same comparison inside the suite, so a copy that was not written
back turns the suite red rather than going quietly wrong again.

**`.claude/hooks/skill_first.py` is deliberately not one of them.**
It hangs a reminder on a shell command -- `git commit`, `git tag`, `gh
pr create` -- so it can only ever name the skills whose situation is
visible in a command line, and it carries a paragraph of reasoning per
entry rather than a table row. Holding it against this table would
demand rows for the nine situations no command can show. What it is
missing instead is a `git push` entry pointing at `ci`; that is a
change to the hook, not to this file.
"""
import io
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SKILLS = os.path.join(ROOT, ".claude", "skills")

# The copies. Each names the file, the two markers the block stands
# between, and the two column heads -- which differ because the
# surrounding prose does: the three documents ask what is about to
# happen, the template asks which situation the change was in.
#
# The markers differ for the same kind of reason and it is not taste:
# in the template the table stands inside an HTML comment, and an HTML
# comment does not nest. A `<!-- ... -->` marker there would end the
# comment around it and print the whole block into every pull request.
COPIES = (
    ("claude", "CLAUDE.md",
     "<!-- skills begin: written by development/skill_table.py,"
     " not by hand -->",
     "<!-- skills end -->",
     "when this is about to happen", "read first"),
    ("contributing", "CONTRIBUTING.md",
     "<!-- skills begin: written by development/skill_table.py,"
     " not by hand -->",
     "<!-- skills end -->",
     "when this is about to happen", "read first"),
    ("agents", "AGENTS.md",
     "<!-- skills begin: written by development/skill_table.py,"
     " not by hand -->",
     "<!-- skills end -->",
     "when this is about to happen", "read first"),
    ("pr", os.path.join(".github", "pull_request_template.md"),
     "[skills begin: written by development/skill_table.py, not by hand]",
     "[skills end]",
     "situation", "skill"),
)

ROW = "| %s | `%s` |"
ROW_READ = re.compile(r"^\| (.*?) \| `([a-z-]+)` \|$")
FIELD = re.compile(r"^([a-z]+):\s*(.*)$")


def escape(text):
    """A pipe in a situation would end the table cell it stands in."""
    return text.replace("|", "\\|")


def unescape(text):
    return text.replace("\\|", "|")


def skills(folder=SKILLS):
    """Every skill that carries a row, in the order the tables show it.

    A skill without the three fields is not silently left out: it comes
    back with what it has, so the test below can say which one is
    missing what instead of a row disappearing unnoticed.
    """
    out = []
    for name in sorted(os.listdir(folder)):
        path = os.path.join(folder, name, "SKILL.md")
        if not os.path.exists(path):
            continue
        lines = io.open(path, encoding="utf-8").read().split("\n")
        if not lines or lines[0].strip() != "---":
            out.append({"name": name, "path": path})
            continue
        got = {"name": name, "path": path}
        for line in lines[1:]:
            if line.strip() == "---":
                break
            found = FIELD.match(line)
            if found and found.group(1) in ("when", "tables", "order"):
                got[found.group(1)] = found.group(2).strip()
        if "tables" in got:
            got["tables"] = [t.strip() for t in got["tables"].split(",")
                             if t.strip()]
        out.append(got)
    return out


def rows_for(key, found=None):
    """The rows of one copy: the situation and the skill, in order.

    Anything without all three fields is left out here and reported by
    the test rather than by a traceback: this function is also what
    writes the file, and a half-filled skill must not be able to empty
    a table.
    """
    found = skills() if found is None else found
    mine = [s for s in found
            if s.get("when") and s.get("order", "").isdigit()
            and key in s.get("tables", [])]
    mine.sort(key=lambda s: (int(s["order"]), s["name"]))
    return [(s["when"], s["name"]) for s in mine]


def rendered(key, rows):
    """The whole block for one copy, markers included."""
    begin, end, left, right = [c[2:] for c in COPIES if c[0] == key][0]
    out = [begin, "", "| %s | %s |" % (left, right), "|---|---|"]
    for when, name in rows:
        out.append(ROW % (escape(when), name))
    out += ["", end]
    return "\n".join(out) + "\n"


def rows_in(key, text):
    """Read one copy's block back: the situations and the skills.

    The reading and the writing live in one file, so the two cannot
    come apart -- the same reason overview.py keeps them together.
    """
    begin, end = [c[2:4] for c in COPIES if c[0] == key][0]
    inside = False
    out = []
    for line in text.splitlines():
        if line.strip() == begin:
            inside = True
            continue
        if line.strip() == end:
            inside = False
            continue
        if not inside:
            continue
        row = ROW_READ.match(line)
        if row:
            out.append((unescape(row.group(1)), row.group(2)))
    return out


def spliced(text, block, key):
    """The document with the block put in place of the old one."""
    begin, end = [c[2:4] for c in COPIES if c[0] == key][0]
    start = text.find(begin)
    stop = text.find(end)
    if start < 0 or stop < 0:
        raise SystemExit("no %r / %r markers found" % (begin, end))
    return text[:start] + block + text[stop + len(end) + 1:]


def apart(wanted, listed):
    """What the copy gets wrong, in words, or an empty list.

    Three kinds, and they are told apart on purpose: a missing row is
    what happened to `ci`, an extra row is a skill that was deleted or
    renamed, and a reworded row is the drift that made four wordings
    out of one.
    """
    said = []
    by_name = dict((name, when) for when, name in listed)
    for when, name in wanted:
        if name not in by_name:
            said.append("missing: `%s` -- %s" % (name, when))
        elif by_name[name] != when:
            said.append("reworded: `%s` says %r, the skill says %r"
                        % (name, by_name[name], when))
    for when, name in listed:
        if name not in [n for _, n in wanted]:
            said.append("not a skill of this copy: `%s`" % name)
    if not said and [n for _, n in wanted] != [n for _, n in listed]:
        said.append("out of order: the copy has %s, the skills say %s"
                    % (", ".join(n for _, n in listed),
                       ", ".join(n for _, n in wanted)))
    return said


def main(argv):
    found = skills()
    stale = []
    for key, where, _begin, _end, _l, _r in COPIES:
        path = os.path.join(ROOT, where)
        rows = rows_for(key, found)
        block = rendered(key, rows)
        if "--show" in argv:
            sys.stdout.write(block + "\n")
            continue
        text = io.open(path, encoding="utf-8").read()
        if "--check" in argv:
            said = apart(rows, rows_in(key, text))
            if said:
                stale.append((where, said))
            continue
        fresh = spliced(text, block, key)
        if fresh == text:
            print("%s is up to date: %d rows" % (where, len(rows)))
            continue
        io.open(path, "w", encoding="utf-8").write(fresh)
        print("%s written: %d rows" % (where, len(rows)))
    if "--check" in argv:
        if not stale:
            print("the skill table is the same in all %d copies"
                  % len(COPIES))
            return 0
        for where, said in stale:
            print("%s is out of date:" % where)
            for one in said:
                print("    %s" % one)
        print("Fix with: python3 development/skill_table.py")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
