---
name: freigabe
description: A new version is about to go out -- somebody says "publish", names a version, a number, a tag or a release, or asks whether this state is finished and ready to be published.
---

# Releasing a version

**A version is not a tag, and the tag comes last.** Evidence before the
mark: a tag whose attachment does not match what was tested is worse
than no tag. Five things belong to a version, and the tag is none of
them -- it is what follows once they hold.

**Since 4.9.2026 nobody sets that tag by hand.** One word starts
`.github/workflows/publish.yml`, and it does the mechanics: it reads the
number, cuts the notes, builds the archive, sets the tag, makes the
release, and stops where any of that does not hold. **It cannot check
the five things.** Those are the whole of this document, and they are
still yours.

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

**Since 4.9.2026 the mechanics are a workflow, and the word is the whole
of your part in them.** The owner says *publish*; the tool starts
`.github/workflows/publish.yml` over the GitHub connection; the workflow
reads the version out of the program, cuts the notes out of the
changelog, builds the archive and the sum beside it, sets the tag and
makes the release. **Nothing is tagged by hand and nothing is published
by hand any more** -- no `git tag`, no `git push origin v...`, no
`gh release create`. A tag pushed from a desk is not a shortcut now, it
is a fault: the workflow would find that tag already standing and stop,
and the release nobody made would have to be made by hand after all.

Everything under this heading is still the source, because the workflow
has no reasoning of its own: every command in it is quoted out of here
-- the four exclusions of the archive, the manifest beside it, the awk
over the changelog, the spelling of the tag. **Change one of them here
and the workflow says the old thing until somebody carries it over**,
and nothing tells you: no test holds the two against each other
(4.9.2026).

### The workflow is the mechanics, and the five things are not mechanics

**The workflow takes the handgrips, not the judgement: it can see that
the suite was green on this commit and that the changelog has a section
under this number, and it cannot see a manual that still describes last
version's program, a picture run that was never made, or an open list
that has drifted two releases -- so a run that ends in a release proves
that the mechanics held, and never that the version was ready.**

The five things above stand exactly as they stood. What has moved is
only that "the tag comes last" now happens inside a machine, four
minutes after the word, with nobody watching. **That is the danger of
this change**: a run that goes through green from end to end leaves the
feeling that everything was seen to. Six checks were seen to. The other
five are yours, they are the ones nobody will ask you about, and the
workflow will happily hang a tag on a version whose manual is a version
behind.

So the word is said when 1 to 5 hold, and not when the suite is green.
Green is one of the five.

### Still by hand, and before the word

**Set the number.** `VERSION = "..."` in the program itself,
`videopodcast_magic/__init__.py`. The same number stands as the topmost
numbered section in `CHANGELOG.md`, and as `**Version ....**` in
`README.md`, `README.de.md`, `ROADMAP.md` and `ROADMAP.de.md`.
`tests/text_release_ready_test.py` holds those six against each other,
and the workflow's first question is whether that test was green here.

**A seventh place, and no test reaches it: `version = "..."` in
`pyproject.toml`.** It is what pip hands somebody who installs rather
than fetches, and a package calling itself one thing while the program
calls itself another looks amiss nowhere on the release page. Two
workflows hold it against the program letter for letter now, and only
one of them is in time: `publish.yml` reads both lines and stops before
the tag; `.github/workflows/release.yml` asks the same question once the
release is out, when the push is long gone. So it is set by hand, with
the other six, before the word.

**Which number**, by Semantic Versioning:

* A fault is fixed and nothing else: PATCH.
* Something is added and the old still runs: MINOR.
* The old does not run any more: MAJOR.

What that refers to is the command-line switches, the format of the
project file, and the names of what comes out. **Manual, tests or notes
alone get no new number.**

**Write the changelog section before the push, because the workflow
reads it and does not write it.** Skill `changelog` says what goes in
one. What the workflow does with it is cut everything between
`## [<number>]` and the next line beginning `## `, so two things about
the heading are not cosmetic: **the square brackets belong in it**, and
**the number in it is the number in the program, letter for letter**.
A section that is missing, spelt differently or empty stops the run --
before the tag, which is the whole reason that question is asked twice
in this project.

**One run per attempt at a release, and the workflow now insists on
it.** Everything finished first -- every file, every register, the whole
suite green here -- then **one** push. Then wait, without adding
anything. This was a rule about evidence and it is a mechanism now: the
workflow asks GitHub for a *successful run of `tests.yml` on this very
commit*, and a green run on the commit before it is no answer. A second
commit pushed after the first therefore does not merely muddy the list
of runs -- it moves the head the dispatch would run against, and the
release stops at step 1 until the suite has answered for that commit
too. (Read out of `publish.yml` and `tests.yml`, not measured: the run
it asks about is the one job with the six-way matrix, `fail-fast:
false`, so that run is successful only when all six were.)

**Before the word, count what is left over.** The commonest way to break
the one-run rule is not impatience, it is a file forgotten while
staging:

```bash
git status --short            # must be empty, or every line explained
git stash list                # nothing of this work parked
```

A `git status` that is not empty after the commit means the push is not
the whole thing. Look at every remaining line and say out loud why it
stays -- a state file another strand owns is a reason; "I did not see
it" is the fault this check exists for. It has happened: `tests/resolve.sh`
was missed, reached as a second commit, and killed the first run.

**And before the word, count what git cannot see.** `git status` answers
for the files git knows about. A package is not built out of git:
setuptools builds it out of this folder and keeps a `build/` beside it
that `.gitignore` hides -- and **setuptools uses that folder again
instead of building afresh**, so whatever lay in it last time goes into
the new package too.

Measured 4.9.2026, the day the program became a folder: `pip3 wheel
--no-deps .` in a checkout still holding the morning's `build/lib/` came
out with 21 files -- the new package, and beside it the
`videopodcast_magic.py` and the nine `videopodcast_magic_texts_*.py`
that do not exist any more. After
`rm -rf build videopodcast_magic.egg-info`: 11 files. **git was clean,
the working tree was clean, and only the package was wrong.** Nothing
would have shown it.

So what is lying about goes:

```bash
rm -rf build dist ./*.egg-info
```

and then the package is built and looked into. **Always `--no-deps`**:
without it pip builds every dependency as well, and torch alone is
536 MB.

```bash
rm -rf /tmp/vpm-wheel
pip3 wheel --no-deps . -w /tmp/vpm-wheel

find videopodcast_magic \( -name models -o -name __pycache__ \) -prune \
     -o -name '*.py' -print | LC_ALL=C sort > /tmp/vpm-here.txt
python3 - /tmp/vpm-wheel/*.whl <<'PY' | LC_ALL=C sort > /tmp/vpm-inside.txt
import sys, zipfile
for name in zipfile.ZipFile(sys.argv[1]).namelist():
    if not name.endswith("/") and ".dist-info/" not in name:
        print(name)
PY
[ -s /tmp/vpm-here.txt ] \
  || echo "FAIL  no .py file under videopodcast_magic/ -- wrong folder?"
diff /tmp/vpm-here.txt /tmp/vpm-inside.txt \
  && echo "ok    the package is the program and nothing else" \
  || echo "FAIL  < is missing from the package, > does not belong in it"

rm -rf build dist ./*.egg-info /tmp/vpm-wheel
```

**Tidying up is a request to the next person; looking inside is the
answer.** Which is why the second block does not tidy first: it builds
out of whatever is lying here, so a `build/` the line above did not
reach -- a second checkout, the wrong folder, a build made in
between -- comes out red rather than quietly right. And it clears up
after itself, because a check that leaves a `build/` behind lays the
trap it exists for.

**It asks after the shape, not the number.** Eleven files is today; a
tenth language tomorrow is a file in `language/` and travels by itself,
and a written-down eleven would turn a good release red. `models/` and
`__pycache__` are pruned on this side for the same reasons as in the
archive: 31 MB of speaker model that the program fetches itself, and
bytecode that is not in the repository at all. `*.py` is what
setuptools ships out of a package that declares no data of its own; the
day it declares some, this line names it too.

**Both directions at once, and one case is not covered here.** Measured
4.9.2026 on copies: a `build/lib/` holding a stale
`videopodcast_magic_texts_de.py` comes out as
`> videopodcast_magic_texts_de.py`, by name; and a `pyproject.toml`
whose `packages` has lost `videopodcast_magic.language` comes out as
ten `<` lines -- which is the only place that fault is caught at all,
because the archive is built out of the folder and pip's own
`--version` answers in English either way. What it does not see is a
file gone from the folder itself: then both sides lack it and the diff
is content. `git status` answers for that one, which is why it stands
above this and not instead of it.

**This one stays on the disc, and no workflow can take it.** Neither
`publish.yml` nor `release.yml` can ask it: both work in a checkout made
seconds ago, where a stale `build/` cannot exist, so the check would be
green for ever on a machine where the fault is impossible. It has to be
asked here, on the disc where the folder lies, and before the word.

### The word, and the one box the workflow cannot fill

**The release title carries the humour, and nothing else does.** Not the
notes, not a closing line -- the headline. It is what somebody sees in
the list of releases before they open anything, and it is the one place
in this project where a lighter tone costs nothing.

It says what this version is really about while it does it. Half a
sentence after the number:

```
2.23.0-beta -- the project asks before it measures, and stops when told
```

**Only the half after the `--` is typed anywhere**; the number and the
dashes are put in front by the workflow.

Nothing else here carries a joke: the changelog is looked things up in,
the commits are searched through, the manual is read while working. A
title stays honest all the same -- about the work, never at the expense
of whoever ran into the fault, and it names the thing that matters
rather than being funny beside it. A release that fixed one thing gets a
title about that one thing. It reads as something a person wrote: out of
the thing itself, no exclamation mark, no explanation behind it. If
nothing comes, dry beats laboured.

**This is the one thing in a release a machine cannot supply, and it is
the only thing the dispatch asks for.** `publish.yml` has a single input,
`title`, and what goes in it is **the half sentence and not the number**:
the workflow reads the number out of the program and puts it in front
itself, so the headline and the tag are built out of the same one number
and cannot come apart. Two ways to get it wrong, and the run stops on
both rather than guessing: an empty box (a bare number is not a quieter
title, it is a missing one, and nothing downstream would ever notice
it), and a half sentence that already begins with the number (it says
what to type instead rather than silently stripping it).

### What the workflow asks, and where it stops

In its own order. Whoever knows this list does not have to open the
YAML:

0. **The title is not empty.** First because it costs nothing -- no
   checkout, no network -- and the commonest wrong start is found in two
   seconds.
1. **The suite is green on this very commit.** It asks GitHub for a
   completed, successful run of `tests.yml` whose head is this commit,
   and prints the newest one it found. No run, still running, or red:
   stop.
2. **One version number.** The program and `pyproject.toml` each carry
   exactly one line to read, and the two say the same thing. The title
   does not repeat the number. Stop on any of the three.
3. **The changelog section exists and is not empty.** The cut goes into
   the notes file; nothing to publish until there is something in it.
4. **The tag does not exist yet.** `git ls-remote` against the remote --
   a tag is the one thing here nobody can take back once it has been
   fetched, so a tag already standing means this run has nothing to do.
5. **The archive is the program.** It builds the zip and the sum, then
   holds the archive's listing against what is at this commit, both
   directions. A wrong archive is stopped here rather than found hanging
   on a tag.
6. **The tag, then the release on it** -- and this is the first step
   that changes anything outside the runner. The tag is annotated and
   made by `git` on this very commit, not left to `gh` (which would make
   a lightweight one and, where the tag is absent, hang it on the
   default branch's head). **If the release will not be made, the tag is
   taken down again**, because a tag with no release is a mark with no
   evidence -- and step 4 of the next attempt would refuse to run into
   it.

Two runs cannot overlap (`concurrency: publish`, and a publish is never
cancelled halfway), and the run says what it is in the list of runs
rather than borrowing the commit subject.

**What it does not ask, on purpose.** Everything that judges a release
already standing stays in `.github/workflows/release.yml`, which runs on
`release: published`: the archive against the tree at the tag byte for
byte, the notes against the changelog line by line, the addresses a
fetched copy updates itself from, and that the thing installs and
answers `--version`. Three questions are in both files, each marked
"too late" where it stands in `publish.yml` -- program against
`pyproject.toml`, the section not empty, the archive's listing. Not
duplication: after the tag, an answer only tells you what you can no
longer change.

**So the publish run is not the last one to watch.** `publish.yml` going
green means the mark was set well; `release.yml`, which starts by itself
the moment the release is published, is what says the thing hanging on
it is right.

### Why the archive is what it is

The workflow builds it, out of the top of the checkout, with the
recipe's four exclusions:

```bash
zip -X -r /tmp/videopodcast_magic.zip videopodcast_magic \
    -x '*/__pycache__/*' '*/.DS_Store' '*.log' 'videopodcast_magic/models/*'
( cd /tmp && shasum -a 256 videopodcast_magic.zip > SHA256SUMS.txt )
```

**The `rm -f` in front of it is not tidiness.** `zip` adds to an archive
that is already there instead of replacing it, so without it a second
attempt ships yesterday's files beside today's and nothing says so. And
from the top of the checkout, so the folder inside is named
`videopodcast_magic/`: whoever unpacks it has the program in a folder of
their choosing and it starts there.

**The four exclusions are not tidiness either, and one of them is the
rule.** Measured 4.9.2026, zipping the folder plainly: 32 085 423 bytes
and 42 files, against 593 059 and 13 with them. Three sweep in junk --
`.DS_Store`, the compiled `__pycache__`, and the 31 MB speaker model,
which is fetched rather than shipped. The fourth is why this paragraph
is in bold: **an uninstalled run writes its log beside the program**, so
`videopodcast_magic/videopodcast-magic.log` lies in the folder on any
machine the program has been started on -- and on this machine that log
holds the file names of a real production. `.gitignore` keeps it out of
git; only `-x '*.log'` keeps it out of the archive. A runner's fresh
checkout has none of the four and the exclusions stay all the same: the
archive is to say what it is on any machine it is ever built on, and
this one is built on a Mac whenever somebody checks the recipe by hand.

**An archive and not a file, since 4.9.2026.** The texts of each
language stand in a folder beside the program that day, and the program
alone does not start -- `FileNotFoundError` on `language/de.py` during
the import, measured. So all of it goes up or none of it does.

**And an archive of the program, not of the repository.** GitHub hangs
"Source code (zip)" on every release by itself: 63 735 119 bytes,
because the whole tree is in it. The program's own files came to
593 059 (measured 4.9.2026, after the move to a folder; 588 141 the
same day, before it). That small one is what "the state of the
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

**The folder picks by place, and that is the whole of the maintenance.**
A language added tomorrow is a file in `language/` and travels by
itself; so does a piece cut out of the big file into a module beside
it. That day came on 4.9.2026, and this line was what changed: it named
a pattern of file names and names the folder now. Both workflows follow
by themselves, because they list what is at the commit rather than
holding a list of their own. What does not follow by itself is the
`starts:` job in `release.yml` and the fetch in `tests/first_run.sh`:
both ask github.com for names ending in `.py`.

**Two files hang on a release: the archive and the sum of it.** The sum
is made from the archive that is about to go up and goes up beside it.

**It is over the archive, not over the files in it.** An archive cannot
be built twice into the same bytes -- it carries the times and the order
the files went in -- so a sum over the files inside would be one nobody
could repeat against what is in their hand, while the archive's own sum
is exactly that. Whether the files inside are the ones that were tagged
is `release.yml`'s question, and it answers it byte for byte without
needing a sum.

Why a file of its own rather than a line in the notes: **whoever checks
it is not a person.** The notes are prose and change shape from version
to version; a manifest is read by a program. The model already carries
one under exactly this name and in exactly this format, so one reader
serves both -- a line whose first field is 64 characters, the file name
last, comments skipped. Which is also why the sum is made from inside
`/tmp`: the name in the manifest is to carry no path.

**Without it, somebody who downloads has nothing in their hand.** The
release workflow holds the archive against the tag, but that is our
answer to ourselves; it is not something the person downloading can
repeat.

Three releases went out with nothing attached at all. That is the fault
the attachment step in `publish.yml` cannot repeat -- both files are
named in the same `gh release create` that makes the release, so a
release without them is no longer a thing a tired hand can produce.

### Afterwards

**`--latest`, and no `--prerelease`.** The workflow sets it, and the
reason is not neatness: a fetched copy asks github.com for the *newest*
release when it looks for an update, and a release that is not the
latest is one it never sees. Should it ever have to be put right by
hand:

```bash
gh release view v<number>
gh release edit v<number> --prerelease=false --latest
```

**If a changelog section changes later, the release text is pulled up
with it** -- for every release it touches and not only the newest. This
is the one `gh` command still typed here, because the workflow only ever
runs once per version:

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
