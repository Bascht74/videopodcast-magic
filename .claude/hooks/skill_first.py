#!/usr/bin/env python3
"""Name the skill that belongs to what is about to happen.

The rules of this repository live in .claude/skills/, one document per
situation, and each is meant to be read before the first edit. A table
in CLAUDE.md says which is which -- and a table is not enough. In one
night a release went out with the changelog and the release skills
unread, by somebody who had written them the same day.

So the reminder is hung where the situation actually arises: on the
command itself. It does not block -- a block on a wrong guess would be
worse than the forgetting -- it puts the skill's name into the context
at the one moment it is needed.

Reads the hook's json on stdin, writes the hook's json on stdout, and
says nothing at all when nothing matches.
"""
import json
import re
import sys

# What is about to happen -> which skill says how. The wording is the
# one in CLAUDE.md and in CONTRIBUTING.md; three places, one sentence.
WHEN = (
    (r"\bgit\s+commit\b",
     "commit",
     "A commit message is about to be written. It is read in a list, "
     "without the diff beside it -- so the subject names the thing as "
     "it stands on the screen, says what is different afterwards, and "
     "carries the fix rather than only the fault. One commit, one "
     "thing: if the subject needs an \"and\", it is usually two."),
    (r"\bgit\s+tag\b|\bgh\s+release\s+create\b",
     "freigabe",
     "A version is going out. The tag comes last: five things belong "
     "to a version first -- green on all six builder jobs, a changelog "
     "section in both languages, a manual that is true again, pictures "
     "that show the program as it is, and the open list brought up to "
     "date."),
    (r"\bgh\s+pr\s+create\b",
     "commit",
     "A pull request is about to be opened. Its body is read by "
     "somebody who was not there: what changes for a user, what was "
     "measured with the number, and the counter-proof for every check "
     "that was added or reworded."),
)


def main():
    try:
        given = json.load(sys.stdin)
    except (ValueError, OSError):
        return 0
    command = ((given.get("tool_input") or {}).get("command") or "")
    if not command:
        return 0
    said = []
    for pattern, skill, why in WHEN:
        if re.search(pattern, command):
            said.append("The skill `%s` covers this, and it is read "
                        "before the first edit, not after. %s" % (skill, why))
    if not said:
        return 0
    json.dump({"hookSpecificOutput": {
        "hookEventName": "PreToolUse",
        "additionalContext": "\n".join(said)}}, sys.stdout)
    return 0


if __name__ == "__main__":
    sys.exit(main())
