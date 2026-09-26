---
name: freigabe
description: A new version is about to go out -- somebody says "publish", names a version, a number, a tag or a release, or asks whether this state is finished and ready to be published.
when: a version is going out
tables: claude
order: 70
---

# Releasing a version

**A version is not a tag, and the tag comes last.** Evidence before the
mark: a tag whose attachment does not match what was tested is worse
than no tag. Six things belong to a version, and the tag is none of
them -- it is what follows once they hold. **Since 4.9.2026 nobody sets
that tag by hand:** one word starts `.github/workflows/publish.yml`, and
it does the mechanics. **It cannot check the six things.** Those are
the whole of this document, and they are still yours. How the workflow
does its part and where it stops is
`.claude/skills/freigabe/mechanics.md` -- read that one when a run
stopped somewhere, or when a command in it is being changed.

## The six things

1. **The tests are green on all seven builder jobs** -- the six
   systems and the neutral one. Not here on this Mac -- there. That is the evidence the tag later stands on.

2. **`CHANGELOG.md` says what changed.** How a section is built, what
   belongs in it and what does not: skill `changelog`.

3. **The manual is true again.** Skill `handbuch`. The heart of it in
   one sentence: **what the writing turns up becomes a test, and it does
   so before the tag.**

4. **The pictures show the program as it is now.** Skill `bilder`. Not
   every version moves them; one that changed the window does.

5. **The open work and the issue are up to date** -- the owner's
   decision board (private, outside the repository) for what is open,
   the roadmap issue for whoever reads from outside.

   **Before a release the owner reviews the board's "Prüfen" column and
   confirms it**: every card of this release is done, or has been moved
   to a later release. That confirmation is the owner's and it is a
   decision, not a count -- nobody else gives it. Two lines go into the
   release report, and a blank one stops the release:

   * `board: reviewed and confirmed by the owner`
   * `nothing this version's changelog claims is still standing as open`

   **Why a decision and not a number any more.** Until 3.0.0b24 this
   step counted the sections of a task file under `docs/notes/` and
   wrote the count into the repository at every release. The count said
   how long the list was, never whether this release's work was done.
   The owner's decision of 26.9.2026 replaced the file with the board,
   where every card belongs to a release, so the question is asked of
   the cards directly.

   What still holds at a finished card goes somewhere else before the
   card is closed: a standing decision to `claude_intern.md`, a
   measurement to `development/measurements.md`, what a user notices to
   `CHANGELOG.md`, what they must know to the manual.

   **The roadmap is not asked here any more. It is a gate.** Step 3b of
   `.github/workflows/publish.yml` reads the roadmap issue and refuses
   to tag where it does not name the version going out. So the roadmap
   is brought up to date **before** the word is said, the same way the
   changelog section is -- both describe a version that is about to
   exist.

   **The real case, and why it became a gate: "Where the program stands
   today" in the roadmap said 2.24.0-beta while the program was at
   2.25.0-beta.** It had drifted two releases with nothing noticing
   (`80f46d5`, 1.9.2026) -- and what was supposed to have caught it was
   a line in a report. A report nobody grades holds nothing.

6. **The Resolve tests have run, or the report says why not.**
   `tests/resolve.sh` starts the tests under `tests/resolve/live/`, the
   only ones that talk to a DaVinci Resolve really running. No builder
   has one, so the owner runs them -- on the owner's Mac, with Resolve
   open -- and nobody else starts them: not a strand, not a script.
   **This one point does not block.** One line goes into the release
   report either way, `resolve.sh: green`, or `resolve.sh: not run,
   because ...` with the reason, and then the release goes on. **A blank
   line is still no answer.** Until 25.9.2026, when the owner decided
   it, the point stood nowhere: `resolve.sh` came up here only as a file
   once forgotten while staging, never as a step.

## The workflow takes the handgrips, not the judgement

**The workflow takes the handgrips, not the judgement: it can see that
the suite was green on this commit and that the changelog has a section
under this number, and it cannot see a manual that still describes last
version's program, a picture run that was never made, or an open list
that has drifted two releases -- so a run that ends in a release proves
that the mechanics held, and never that the version was ready.**

The six things above stand exactly as they stood. What has moved is
only that "the tag comes last" now happens inside a machine, four
minutes after the word, with nobody watching. **That is the danger of
this change**: a run that goes through green from end to end leaves the
feeling that everything was seen to. Six checks were seen to. The other
five things are yours, they are the ones nobody will ask you about, and the
workflow will happily hang a tag on a version whose manual is a version
behind.

So the word is said when 1 to 5 hold and 6 is answered, and not when the
suite is green. Green is one of the six.

**Nothing is tagged by hand and nothing is published by hand any more**
-- no `git tag`, no `git push origin v...`, no `gh release create`. A
tag pushed from a desk is not a shortcut now, it is a fault: the
workflow would find that tag already standing and stop, and the release
nobody made would have to be made by hand after all.

**And the mechanics in `.claude/skills/freigabe/mechanics.md` are still
the source, because the workflow has no reasoning of its own**: every
command in it is quoted out of these two files -- the four exclusions of
the archive, the manifest beside it, the awk over the changelog, the
spelling of the tag. **Change one of them in either file and the
workflow says the old thing until somebody carries it over**, and
nothing tells you: no test holds the two against each other (4.9.2026).

## Beforehand: the builder's times

**Fetch them before a release and look at them**:

```bash
cd tests && bash builder_times.sh --record <version>
```

**What you wait for is the longest of the seven jobs, not the sum** -- they
run side by side. What the numbers mean for the queue, and what to do
with them, is in the skill `ci` under "After a green run, the queue",
because that is the moment the command is run.

**`--record` keeps them, one section per release, in
`development/test_durations.md`** -- every job, a trimmed mean per
test, and the change against the release before. `state/longest` is
overwritten each time and so cannot say that a test got slower; the
record can, and a test marked **grown** there (more than 20 % and at
least 10 s) is named in the release report with what made it so. It
finds its run by the version the commit carries, because the newest
green run on main is not the release's while the merge's own run is
still going: 3.0.0b24's `state/longest` was read that way and holds
3.0.0b23's times (measured 26.9.2026).

## Still by hand, and before the word

**Set the number.** `VERSION = "..."` in the program itself,
`videopodcast_magic/__init__.py`. The same number stands as the topmost
numbered section in `CHANGELOG.md`, and as `**Version ....**` in
`README.md`, `README.de.md`, `ROADMAP.md` and `ROADMAP.de.md`.
`tests/source/text_release_ready_test.py` holds those six against each
other, and the workflow's first question is whether that test was green
here.

**A seventh place, and no test reaches it: `version = "..."` in
`pyproject.toml`.** It is what pip hands somebody who installs rather
than fetches, and a package calling itself one thing while the program
calls itself another looks amiss nowhere on the release page. Two
workflows hold it against the program letter for letter now, and only
one of them is in time: `.github/workflows/publish.yml` reads both lines and stops before
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

**Every language, once, before the word.** The everyday suite tests
English and German only (the owner's rule, 26.9.2026); a release tests
every catalogue. Here that is `cd tests && VPM_ALL_LANGUAGES=1 bash
run.sh`, green before the push. On the builder nothing has to be
asked for: the release pull request changes the version, so its seven
checks run every language by themselves, and the long way passes
`all_languages: true` -- why, beside that input in
`.github/workflows/tests.yml`.

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
workflow **runs the suite itself**, on the commit the dispatch was
started against, and makes the tag only where all seven jobs came back.
A second commit pushed after the first therefore does not merely muddy
the list of runs -- it moves the head the next dispatch would run
against, and the suite answers for that commit instead.

**Since 21.9.2026 the workflow reuses the evidence where it already
exists, and only there.** A release goes out of `main`, and `main` is
the merge of a pull request whose six checks the branch protection
wanted green before it could merge. Where the merge commit's tree is
byte for byte the tree of that pull request's head -- nothing else
landed on `main` in between -- and the six check runs of that head
concluded success, the workflow says so in one line (`way: short --
...`) and does not run the suite a second time: the evidence is the
pull request's run on the identical tree, and evidence before the mark
holds exactly as before. Where `main` moved in between, or the commit
is not a merge, or a check is missing or red, or the merge brings in a
file of the speaker separation, the suite runs as it has since
4.9.2026 (`way: long -- ...`, with the reason). Measured
21.9.2026: `484daa8`, the merge of #186, carries the tree of `8a58ea4`,
its head, and the six check runs of `8a58ea4` all concluded success.
**One thing the short way does not give you:** the pull request's run
is the everyday suite, separation off, and only the workflow's own run
turns it on -- so `voice_split_hears_two` runs for a release only on
the long way. **Since 24.9.2026 the owner's answer to that is a fourth
question:** the short way is taken only where the merge touches nothing
of the separation -- since 25.9.2026 its code, its model,
requirements.txt and the test that runs it, but not pyproject.toml,
whose version every release changes. A pull request that changed one of
them goes the long way, and the line names the file that sent it
there. **Since 26.9.2026 a fifth:** a pull request runs English and
German only, every language only where it changes the `VERSION` line,
so the short way is taken only where the merge changes the version.
How the five questions are asked, and where that difference is kept,
is `.claude/skills/freigabe/mechanics.md`.

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
out with 21 files -- the new package, and beside it the flat
videopodcast_magic.py and the nine videopodcast_magic_texts_ files
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
     -o \( -name '*.py' -o -name '*.po' -o -name '*.png' \) -print \
     | LC_ALL=C sort > /tmp/vpm-here.txt
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

**It asks after the shape, not the number.** Forty-nine files is
today -- 36 of program, twelve catalogues and one icon; a thirteenth language tomorrow is a file in `language/` and
travels by itself, and a written-down number would turn a good release
red. `models/` and `__pycache__` are pruned on this side for the same
reasons as in the archive: 31 MB of speaker model that the program
fetches itself, and bytecode that is not in the repository at all.

**The three patterns are the three things `pyproject.toml` ships**, and
they have to be read off it rather than remembered: `.py` for the
program, and `[tool.setuptools.package-data]` for the rest -- today
`"videopodcast_magic.desktop" = ["*.png"]` and
`"videopodcast_magic.language" = ["*.po"]`. **This line stood at `.py`
alone until 7.9.2026 and turned a sound package red**: the icon and
twelve catalogues came out as thirteen `>` lines, and the sentence
warning that the day would come stood right beneath it. So whoever
adds a line to `package-data` adds its pattern here in the same
breath.

**Both directions at once, and one case is not covered here.** Measured
4.9.2026 on copies: a `build/lib/` holding a stale
videopodcast_magic_texts_de.py comes out as a `>` line naming it; and a `pyproject.toml`
whose `packages` has lost `videopodcast_magic.language` comes out as
ten `<` lines -- which is the only place that fault is caught at all,
because the archive is built out of the folder and pip's own
`--version` answers in English either way. What it does not see is a
file gone from the folder itself: then both sides lack it and the diff
is content. `git status` answers for that one, which is why it stands
above this and not instead of it.

**This one stays on the disc, and no workflow can take it.** Neither
`.github/workflows/publish.yml` nor `.github/workflows/release.yml` can ask it: both work in a checkout made
seconds ago, where a stale `build/` cannot exist, so the check would be
green for ever on a machine where the fault is impossible. It has to be
asked here, on the disc where the folder lies, and before the word.

## The release title, the one box the workflow cannot fill

**The release title carries the humour, and nothing else does.** Not the
notes, not a closing line -- the headline. It is what somebody sees in
the list of releases before they open anything, and it is the one place
in this project where a lighter tone costs nothing.

**It is English.** The notes say everything twice and the program speaks
nine languages; the headline does not. Counted 4.9.2026: seven of the
eight newest titles are English and one is German, and the odd one out
reads as a slip rather than a choice. The rule had never said so, and
the gap cost a wrong proposal that evening -- so it says so now.

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
the only thing the dispatch asks for.** `.github/workflows/publish.yml` has a single input,
`title`, and what goes in it is **the half sentence and not the number**:
the workflow reads the number out of the program and puts it in front
itself, so the headline and the tag are built out of the same one number
and cannot come apart. Two ways to get it wrong, and the run stops on
both rather than guessing: an empty box (a bare number is not a quieter
title, it is a missing one, and nothing downstream would ever notice
it), and a half sentence that already begins with the number (it says
what to type instead rather than silently stripping it).

## In passing: every workflow says what it is

**A new workflow without a `run-name:` is not finished**, and a release
is when workflows get written. Why, and what a list of runs looks like
without it, is in the `ci` skill.

## What must not hold it up

**Work no user notices.** A renamed test, a tidied function, a sharper
comment hold up no release -- and they do not go in a changelog either.
A release is held up by the first five things and by nothing else; the
sixth is answered in the report, and "not run, because ..." answers it.

## Before it counts as done

1. All seven builder jobs green on the very tree that is about to be tagged -- on the commit itself, or on the pull request's head it merges byte for byte?
2. `CHANGELOG.md` carries a section under this number, in both languages?
3. The manual true again -- every chapter a visible change touched, both?
4. What the manual pass turned up: a test, or its shape a card on the owner's board?
5. Do the pictures show the program as it is now?
6. The three lines of the release report written down, none of them blank -- the owner's confirmation of the board among them?
6b. `resolve.sh` run by the owner with Resolve open -- or the line "not
    run, because ..." in the report, with the reason?
7. The number set in the program and the four documents that carry it?
8. Set in `pyproject.toml` too -- the seventh place, which no test reaches?
9. The number Semantic Versioning asks for -- PATCH, MINOR or MAJOR?
10. `tests/source/text_release_ready_test.py` green here, and the whole
    suite with it, in every language (`VPM_ALL_LANGUAGES=1`)?
11. The builder's times fetched with `--record <version>`, the section in
    `development/test_durations.md` looked at, and every test marked
    grown there named in the release report?
12. `git status --short` empty, or every line in it explained out loud?
13. `git stash list` free of this work?
14. `build/` cleared, the wheel built and diffed, and cleared up again after?
15. One commit and one push, with nothing added after it?
16. A title: English, the half sentence only, no number in it, not empty?
17. Do the first five things hold and is the sixth answered -- not only
    the green suite, which is one of them?
18. Only then is the word said.
