---
name: commit
description: A commit is about to be made and its message written, or a subject line has to be judged before it goes into the log -- and above all when the work was big enough that one commit may really be two.
when: a commit message is about to be written
tables: claude, contributing, agents, pr
order: 50
---

# A commit message

A commit is about to be made and its message written, or a subject line
has to be judged before it goes into the log. This file decides what the
subject has to carry, what belongs in the body and what does not, the
two lines every message ends with, and when a commit is made at all.
The worked cases -- subjects out of this repository that failed, with
what would have stood instead, and the ones that carried -- are in
`.claude/skills/commit/examples.md`.

## The difficulty

The message is read in a list, without the diff beside it. That is the
whole difficulty. `git log --oneline` and the commit list on github.com
show one line per commit and nothing else, and somebody scanning that
list has to be able to decide whether this one concerns them.

**A subject written from the inside fails that.** With the diff open it
reads perfectly well; without it, it names nothing a reader can look
for. Almost every weak subject in this repository fails in exactly that
one way.

## What it costs, measured

Writing the changelog for 2.23.0-beta: **seven of the nine points in
that section come out of a single commit, `c746179`, whose subject is
"tests that check, and a rule that says how".** It mentions none of
them. That commit changed 54 files and rewrote 1346 lines of the
program against 2003 taken out -- among them a whole new `--multitrack`
path for a run with no video, the "Intro" proposal, the grey in the
"Kind" field, the digits beside the cut band and "Close project"
calling off the measuring.

Read from the subject lines, that version has a nearly empty changelog.
The points had to be found afterwards with `git log -S` over the
strings, one at a time. **The message did not describe the commit, so
the log was not a source any more.**

That is the price of a subject that is vague, and of a commit that is
several commits.

## The subject line

Five rules. The first four are about the line, the fifth about the
commit under it.

**1. Name the thing, do not allude to it.** The name it carries where
somebody meets it: a switch (`--lufs`), an entry ("Intro"), a button, a
file, a test, a chapter. A subject with no proper noun in it is
suspect.

**2. Say what is different afterwards.** Not what the work was, not how
many of them there were, not how it felt. "Three more points" counts
the labour. Most commits here change tests, documents or workflows
rather than the program -- then the rule is the same one level down:
name the test or the chapter, and say what it does differently now.

**3. The fix, not only the fault.** "The rename had turned off the
release workflow" is half a line: the reader learns what was broken and
not what holds now. In German it is usually the word "jetzt" that
carries the second half; in English it is a present tense.

**4. No image that needs the diff to be decoded.** An image is not the
problem -- a reference only the author can resolve is. `728a873`, "the
counter-check does its jumps again where the window got in between": it
is eleven lines in one test file, it is exactly right, and nobody who
was not there can place a single noun in it.

**5. One commit, one thing.** If the subject needs an "and", it is
usually two commits. The "and" is only the symptom, though: `a268a82`,
"what one way can do, the other can", has no "and" and holds three
unrelated changes. **The reliable check is `git diff --stat`.** If the
files fall into groups that could have gone out separately, they should
have. This is the rule that would have prevented `c746179`.

## The probe: would this line pass as a changelog point?

Read the subject as if it stood under `### Fixed`. If a stranger would
learn nothing from it there, it is too vague -- or the commit is too
big. `f275a5f`, "the zoom buttons stay under the pointer", went into the
changelog nearly word for word. `c746179` could not have gone in at all,
and that was the warning nobody read.

**The probe holds, with one qualification.** Not every commit deserves a
changelog point: a test, a comment, a rename, a guideline. For those the
probe cannot be about worthiness, only about clarity, and it becomes:
**would a stranger reading this one line know which thing changed and
what about it?** A subject that fails both halves of the probe is not a
subject.

## Where the cases are

**Ten from this repository, bad and good**, each with what would have
carried instead or why it carried, stand in
`.claude/skills/commit/examples.md`. That file is read when a subject
line will not come, or when one has to be held against a line that
worked -- not every time a commit is made.

## The body

**Plain words, not code.** What the change does and why, for somebody
who does not have the file open. **Short: a heading and a handful of
lines**, a list where several things really did change.

What belongs in it:

* the reason, where the subject cannot carry it -- why this way and not
  the obvious other one;
* **what was measured**, with the number: "0 pixels where it was 104",
  "none before, seven, four and five now";
* where the fix deliberately does not reach, and why;
* a ratchet that moved, with both numbers.

What does not:

* **no date and no person's name.** The commit carries both already.
* **no list of the files touched.** `git show --stat` prints it better.
* **no story of the day** -- what was tried first, what was ruled out,
  which strand found it. That is `docs/notes/`.
* **no justification of the old state** beyond the one sentence that
  explains the fix.

## The two lines at the end

Every commit message ends with:

```
Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>
Claude-Session: <the session URL>
```

A pull request body ends with the "Generated with Claude Code" line and
the same session URL.

**"Easy to forget" is not a step, so they are counted.** After every
commit, and once more before a push:

```bash
git log -1 --format=%B | tail -2         # both lines, in this order

for h in $(git log origin/main..HEAD --format=%H); do   # prints nothing
  b=$(git log -1 --format=%B "$h")
  echo "$b" | grep -q Co-Authored-By && echo "$b" | grep -q Claude-Session ||
    echo "MISSING $(git log -1 --format='%h %s' "$h")"
done
```

A commit the loop names is amended **before the next one is made** --
`git commit --amend`. After a push the lines cannot be added without
rewriting the branch, so afterwards is never.

**Measured on 1.9.2026: ten of the 321 commits here carry neither line,
and the newest of them is `40361b7`, "2.25.0-beta -- the night of the
first" -- the release commit itself.** That is exactly the commit made in
a hurry. The sentence warning about it stood two lines above and was
skipped, which is what a sentence does.

## When a commit is made at all

**Only when it was asked for.** Finishing a piece of work is not a
request to commit it, and neither is a green suite.

**Never on the main branch.** If `main` is checked out, a branch comes
first.

**Nothing is pushed unless that was asked for too**, and a tag is its
own decision -- see the `freigabe` skill for what has to be true before
one is set.

## Before it counts as done

The pass before `git commit` runs.

1. Was this commit asked for? If not, it is not made.
2. Is `main` checked out? Then a branch comes first.
3. Does the subject name the thing by the name somebody meets it under
   -- a switch, an entry, a button, a file, a test, a chapter?
4. Does it say what is different afterwards, rather than what the work
   was or how much of it there was?
5. Where something was broken: does the line say what holds now, not
   only what failed?
6. Can a stranger place every noun in it without the diff open?
7. `git diff --stat`: do the files fall into groups that could have gone
   out separately? Then this is two commits, not one.
8. The probe: would the line pass as a changelog point -- or, where it
   deserves no point, would a stranger know which thing changed and what
   about it?
9. Is the body plain words, with the reason and every number that was
   measured?
10. Is the date, the name, the file list and the story of the day out of
    the body?
11. `git log -1 --format=%B | tail -2` -- both trailer lines, in this
    order?
12. The loop over `origin/main..HEAD` -- does it print nothing? A commit
    it names is amended before the next one is made.
13. Is anything being pushed or tagged that nobody asked for?
