---
name: freigabe
description: A new version is about to go out -- somebody names a version, a number, a tag or a release, or asks whether this state is finished and ready to be published.
---

# Releasing a version

**A version is not a tag, and the tag comes last.** Evidence before the
mark: a tag whose attachment does not match what was tested is worse
than no tag. Five things belong to a version, and the tag is none of
them -- it is what follows once they hold.

## Beforehand: the builder's times

```bash
cd tests && bash builder_times.sh
```

The script asks the run which of the six jobs was the slowest, writes
that job's numbers into `tests/state/longest`, and prints the ten tests
that will go first from now on. Read the top two or three and ask
whether they can be made cheaper -- that is where a minute of the
builder's time is.

**What you wait for is the longest job, not the sum.** The six run side
by side. The sum is what the builder is billed; the longest is what
stands between a push and an answer.

**Never believe a jump from a single reading.** The macOS machines have
come back with 950 and 1091 seconds on identical code, and once 651
against 1088. So two runs of one commit, or a steadier machine, before
a number means anything.

## The five things

1. **The tests are green on all six builder jobs.** Not here on this
   Mac -- there. That is the evidence the tag later stands on.

2. **`CHANGELOG.md` says what changed.** How a section is built, what
   belongs in it and what does not: skill `changelog`.

3. **The manual is true again.** Skill `handbuch`. The heart of it in
   one sentence: **what the writing turns up becomes a test, and it does
   so before the tag.**

4. **The pictures show the program as it is now.** Skill `bilder`. Not
   every version moves them; one that changed the window does.

5. **The list and the issue are up to date** -- `docs/notes/` for what
   is open, the roadmap issue for whoever reads from outside.

## The mechanics, in this order

**Set the number.** `VERSION = "..."` in `videopodcast-magic.py`, around
line 590. The same number stands as the topmost numbered section in
`CHANGELOG.md`, and in `README.md` and `README.de.md` as
`**Version ....**`. `tests/text_release_ready_test.py` holds the four
against each other.

**Which number**, by Semantic Versioning:

* A fault is fixed and nothing else: PATCH.
* Something is added and the old still runs: MINOR.
* The old does not run any more: MAJOR.

What that refers to is the command-line switches, the format of the
project file, and the names of what comes out. **Manual, tests or notes
alone get no new number.**

**Commit, then wait** until the suite is green on all six jobs. Only
then the tag:

```bash
git tag -a v2.5.0-beta -m "videopodcast-magic 2.5.0-beta"
git push origin v2.5.0-beta
```

**The notes are cut out of the changelog, not written again:**

```bash
awk '/^## \[2\.5\.0-beta\]/{f=1;next} /^## \[/{f=0} f' CHANGELOG.md \
    > /tmp/notes.md
```

The square brackets belong in the pattern; without them the release
comes out empty. For the oldest bracketed section the stop mark is
`/^## /`, otherwise awk reads on past it.

**The release title carries the humour, and nothing else does.** Not
the notes, not a closing line -- the headline. It is what somebody sees
in the list of releases before they open anything, and it is the one
place in this project where a lighter tone costs nothing.

It says what this version is really about while it does it. Half a
sentence after the number:

```
2.23.0-beta -- the project asks before it measures, and stops when told
```

Nothing else here carries a joke: the changelog is looked things up in,
the commits are searched through, the manual is read while working. A
title stays honest all the same -- about the work, never at the expense
of whoever ran into the fault, and it names the thing that matters
rather than being funny beside it. A release that fixed one thing gets a
title about that one thing.

**The file goes on at creation, not afterwards:**

```bash
gh release create v2.5.0-beta \
   --title "2.5.0-beta -- <half a sentence>" \
   --notes-file /tmp/notes.md --latest \
   videopodcast-magic.py
```

Three releases went out without the file. The check for it sits in
`.github/workflows/release.yml` and runs on `release: published`:
whoever creates first and uploads after has already seen it red -- and a
check that is red by design is one nobody reads for long. Without the
attachment the release page offers only "Source code (zip)" at
63 735 119 bytes, while the one file the README tells people to download
is 1 308 045 bytes.

**No `--prerelease`.** Then look that "Latest" is on it:

```bash
gh release view v<number>
gh release edit v<number> --prerelease=false --latest   # if it is not
```

**The title carries half a sentence** that a person can be seen to have
written -- out of the thing itself, no exclamation mark, no explanation
behind it. If none comes, dry beats laboured.

**If a changelog section changes later, the release text is pulled up
with it**, for every release it touches and not only the newest:

```bash
gh release edit v<number> --notes-file /tmp/n.md
```

Otherwise a version stands on GitHub that no longer exists in the file,
and nobody knows which one holds.

## In passing: every workflow says what it is

**A new workflow without a `run-name:` is not finished.** GitHub names a
run after the commit subject otherwise, and the list of runs becomes a
heap of unrelated sentences. The `run-name:` says what the run is and
carries the number the list is ordered by.

## What must not hold it up

**Work no user notices.** A renamed test, a tidied function, a sharper
comment hold up no release -- and they do not go in a changelog either.
A release is held up by the five things and by nothing else.
