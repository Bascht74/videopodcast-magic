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
   is open, the roadmap issue for whoever reads from outside. **Said in
   numbers, not asserted**, because a list nobody counts drifts without
   anything noticing:

   ```bash
   gh issue view <roadmap issue> --json updatedAt,title
   git log --oneline v<previous>..HEAD -- docs/notes/aufgaben.md | wc -l
   ```

   Three lines go into the release report, and a blank one stops the
   release:

   * `aufgaben.md: N entries struck off since v<previous>, M added`
   * `roadmap issue: last touched <date>, <what changed in it>`
   * `nothing this version's changelog claims is still standing as open`

   **The real case: "Where the program stands today" in the roadmap said
   2.24.0-beta while the program was at 2.25.0-beta.** It had drifted two
   releases with nothing noticing (`80f46d5`, 1.9.2026). The *number* is
   held mechanically in six places now; the *content* of the list is held
   by nothing but these three lines.

## The mechanics, in this order

**Set the number.** `VERSION = "..."` in `videopodcast_magic.py`, around
line 700. The same number stands as the topmost numbered section in
`CHANGELOG.md`, and as `**Version ....**` in `README.md`,
`README.de.md`, `ROADMAP.md` and `ROADMAP.de.md`.
`tests/text_release_ready_test.py` holds those six against each other.

**A seventh place, and no test here reaches it: `version = "..."` in
`pyproject.toml`.** It is what pip hands somebody who installs rather
than fetches, and a package calling itself one thing while the program
calls itself another looks amiss nowhere on the release page.
`.github/workflows/release.yml` holds it against the program letter for
letter -- but only once the release is out, and by then the push is
long gone. So it is set by hand, with the other six, before the push.

**Which number**, by Semantic Versioning:

* A fault is fixed and nothing else: PATCH.
* Something is added and the old still runs: MINOR.
* The old does not run any more: MAJOR.

What that refers to is the command-line switches, the format of the
project file, and the names of what comes out. **Manual, tests or notes
alone get no new number.**

**One run per attempt at a release.** Everything finished first -- every
file, every register, the whole suite green here -- then **one** push.
Then wait, without adding anything. A commit pushed after it kills the
run that was going to be the evidence, and the list of runs stops saying
which state was really tested. Green -> the tag. Red -> repair, and the
next push is the next attempt.

**Before that push, count what is left over.** The commonest way to
break this rule is not impatience, it is a file forgotten while staging:

```bash
git status --short            # must be empty, or every line explained
git stash list                # nothing of this work parked
```

A `git status` that is not empty after the commit means the push is not
the whole thing. Look at every remaining line and say out loud why it
stays -- a state file another strand owns is a reason; "I did not see
it" is the fault this check exists for. It has happened: `tests/resolve.sh`
was missed, reached as a second commit, and killed the first run.

**Then wait** until the suite is green on all six jobs. Only then the
tag. **It is `v` plus the number in the program, letter for letter** --
the program builds the address it fetches its model from out of
`VERSION` that way, so a tag spelled differently sends a fresh
installation to an address that is not there.
`.github/workflows/release.yml` holds the two against each other:

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
title about that one thing. It reads as something a person wrote: out of
the thing itself, no exclamation mark, no explanation behind it. If
nothing comes, dry beats laboured.

**The archive goes on at creation, not afterwards. Built at the top of
the checkout, and the tree clean:**

```bash
rm -f /tmp/videopodcast_magic.zip /tmp/SHA256SUMS.txt
zip -X -r /tmp/videopodcast_magic.zip videopodcast_magic*.py
( cd /tmp && shasum -a 256 videopodcast_magic.zip > SHA256SUMS.txt )

gh release create v2.5.0-beta \
   --title "2.5.0-beta -- <half a sentence>" \
   --notes-file /tmp/notes.md --latest \
   /tmp/videopodcast_magic.zip /tmp/SHA256SUMS.txt
```

**The `rm -f` is not tidiness.** `zip` adds to an archive that is
already there instead of replacing it, so without it a second attempt
ships yesterday's files beside today's and nothing says so. And from
the top of the checkout, so the names inside are bare: whoever unpacks
it has the program in a folder of their choosing and it starts there.

**An archive and not a file, since 4.9.2026.** The texts of each
language stand in files beside the program that day, and the program
alone does not start -- `FileNotFoundError` on the first line, measured.
So all of it goes up or none of it does.

**And an archive of the program, not of the repository.** GitHub hangs
"Source code (zip)" on every release by itself: 63 735 119 bytes,
because the whole tree is in it. The ten files of the program came to
588 141 (measured 4.9.2026). That small one is what "the state of the
program" means, and it is the reason to attach anything at all --
**installing is `pip3 install git+...` and nothing else**, so the
attachment documents a state rather than offering a way in. The owner,
4.9.2026: the newest release comes over pip3; the archive writes the
state of the work down once, cleanly.

**Zip, and always that name.** Zip because it opens by double-click on
a Mac and on Windows with nothing installed, because the source archive
beside it on the same page is one too, and because the release workflow
opens it with Python's own `zipfile` and needs nothing fetched to do
it. Always `videopodcast_magic.zip`, never the version in the name:
`.github/workflows/release.yml` and `tests/text_release_ready_test.py`
name it letter for letter, the way `SHA256SUMS.txt` is named, and a
name built out of the tag would have to be built the same way in three
places.

**The star picks by shape, and that is the whole of the maintenance.**
A language added tomorrow is a file matching `videopodcast_magic*.py`
and travels by itself. The day the program becomes a folder
`videopodcast_magic/`, **this line is the one that changes** --
`zip -X -r /tmp/videopodcast_magic.zip videopodcast_magic` -- and the
workflow follows by itself, because it lists what is at the tag rather
than holding a list of its own. What does not follow by itself that day
is the `starts:` job in the workflow and the fetch in
`tests/first_run.sh`: both ask github.com for names ending in `.py`.

**Two files hang on a release: the archive and the sum of it.** The sum
is made from the archive that is about to go up and goes up beside it.

**It is over the archive, not over the files in it.** An archive cannot
be built twice into the same bytes -- it carries the times and the order
the files went in -- so a sum over the files inside would be one nobody
could repeat against what is in their hand, while the archive's own sum
is exactly that. Whether the files inside are the ones that were tagged
is the workflow's question, and it answers it byte for byte without
needing a sum.

Why a file of its own rather than a line in the notes: **whoever
checks it is not a person.** The notes are prose and change shape from
version to version; a manifest is read by a program. The model already
carries one under exactly this name and in exactly this format, so one
reader serves both -- a line whose first field is 64 characters, the
file name last, comments skipped.

**Without it, somebody who downloads has nothing in their hand.** The
release workflow holds the archive against the tag, but that is our
answer to ourselves; it is not something the person downloading can
repeat.

Three releases went out with nothing attached at all. The check for it
sits in `.github/workflows/release.yml` and runs on
`release: published`: whoever creates first and uploads after has
already seen it red -- and a check that is red by design is one nobody
reads for long.

**No `--prerelease`.** Then look that "Latest" is on it:

```bash
gh release view v<number>
gh release edit v<number> --prerelease=false --latest   # if it is not
```

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
