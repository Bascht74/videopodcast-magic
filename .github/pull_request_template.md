<!--
Read CONTRIBUTING.md before filling this in. It is ten minutes and it
holds the five rules that turn a pull request away here -- both
languages, the counter-proof, the ratchets, the count of judgements,
and the numbers in a failure line.

Delete the lines that do not apply, and say WHY you deleted them
rather than removing them silently. "Does not apply" is an answer;
a blank is not.
-->

## What changes for somebody using the program

<!-- One or two sentences, in plain words rather than in terms of the
code. Name the thing as it stands on the screen: a switch, a button,
an entry, a file. If a user cannot see the change, say so here -- a
tidied function or a new test is welcome and needs no changelog. -->


## Why

<!-- What was wrong, or what was missing. If it is a fault: how it
shows, and what a person saw. -->


## What was measured

<!-- The house rule is "measure, do not guess". A claim without a
number is an opinion. Paste the numbers: before and after, the units,
and how they were taken. -->


## Which skills you read

<!-- `.claude/skills/` holds one document per situation, and in that
situation it is read BEFORE the first edit. Name the ones that applied.
"None applied, because ..." is a fine answer; a wrong "all of them" is
found in the first review.

[skills begin: written by development/skill_table.py, not by hand]

| situation | skill |
|---|---|
| a task touches more than one file | `strang` |
| anything inside a `tests/*_test.py` changes -- also one line, also when no judgement changes | `test-neu` |
| a test is red, wobbling, or green and not to be trusted | `test-rot` |
| a check was written or changed and is green | `gegenbeweis` |
| a commit message is about to be written | `commit` |
| a section of `CHANGELOG.md` is written or changed | `changelog` |
| something a user can see has changed and `docs/` still says the old thing | `handbuch` |

[skills end]

Four of the eleven are not in this list, on purpose: freigabe (only
the owner publishes), bilder (only he takes the pictures), ci (the
builder's answer comes after the push, not before the first edit) and
workflow (how an order is cut for several agents, which is nobody's
business but yours). CONTRIBUTING.md has the longer table.
-->

Read:

## The tests

```
<!-- Paste the summary line of `cd tests && bash run.sh` from your
machine, the whole thing:

green: 148   skipped: 1   red: 0
skips: 1 of at most 1 allowed
judgements: 146 tests reported a count and were held to it
-->
```

**Checks added or reworded:** <!-- how many, or "none" -->

<!-- For EVERY one of them, the counter-proof. Without it the check
does not count: a check that has never been seen red is not known to
check anything. Break the one thing it is about in a copy of the
program under /tmp, run the test with VPM_SCRIPT=<the copy>, and paste
the red line verbatim.

| check | what was broken | the red line |
|---|---|---|
|  |  |  |

And the same rows belong in tests/state/counterproof, or
source_checks_proved_test.py turns red.
-->

**Ratchets:** <!-- unchanged / one fell (say which, from what to what).
A ratchet that rises is red, and raising one is the owner's decision in
a commit of its own. -->


## The manual and the changelog

- [ ] A user can see this change, and `docs/<name>.md` **and**
      `docs/<name>.de.md` say so — the German thought in German, not
      translated.
- [ ] A point in `CHANGELOG.md`, both halves, the same number of
      points on each side.
- [ ] The window moved and the pictures are now out of date. **Do not
      regenerate them** — say which ones, the owner takes them.
- [ ] None of the above applies, because: <!-- ... -->


## Anything you found and did not fix

<!-- The most valuable part of many pull requests. A switch that does
nothing, a message naming a state that does not exist, a check that
cannot fall. Report it here rather than widening the change. -->


<!--
Not in a pull request, please: a new version number, a tag, regenerated
pictures, reformatting, or several unrelated things at once. If the
subject line needs an "and", it is usually two pull requests.
-->
