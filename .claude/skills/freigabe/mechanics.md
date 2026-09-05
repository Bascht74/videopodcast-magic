# The mechanics of a release

The side file of `.claude/skills/freigabe/SKILL.md`. It says what
`.github/workflows/publish.yml` does with the word, in what order, and
why each command in it is the command it is. Read it when a run stopped
somewhere and the message alone does not say why, or when one of those
commands is about to be changed. What a release *is* -- the five things,
and everything still done by hand -- stands in `SKILL.md` and not here.

## What the workflow asks, and where it stops

**Since 4.9.2026 the mechanics are a workflow, and the word is the whole
of your part in them.** The owner says *publish*; the tool starts
`.github/workflows/publish.yml` over the GitHub connection; the workflow
reads the version out of the program, cuts the notes out of the
changelog, builds the archive and the sum beside it, sets the tag and
makes the release.

In its own order. Whoever knows this list does not have to open the
YAML:

0. **The title is not empty.** First because it costs nothing -- no
   checkout, no network -- and the commonest wrong start is found in two
   seconds.
1. **The suite runs, here, on this commit.** `.github/workflows/tests.yml` is called from
   this workflow, so the six jobs are part of this run and answer for
   the commit the dispatch was started against. Red on any of them:
   no tag.
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

## Why it runs the suite rather than asking whether somebody did

The first build asked the API for a successful run of `.github/workflows/tests.yml` on this
commit. Measured 4.9.2026: a workflow called with `uses:` is part of
the calling run and appears under **no run of its own**, so that
question would have found nothing and every release would have stopped
at it. Running the suite here answers the same thing without the
question, and one word does the whole of a release.

## Why the archive is what it is

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
alone does not start -- `FileNotFoundError` on the catalogue beside it
during the import, measured. So all of it goes up or none of it does.
(That catalogue was a Python file the day it was measured and is
`language/de.po` since `57b9004`.)

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
`starts:` job in `.github/workflows/release.yml` and the fetch in `tests/first_run.sh`:
both ask github.com for names ending in `.py`.

**Two files hang on a release: the archive and the sum of it.** The sum
is made from the archive that is about to go up and goes up beside it.

**It is over the archive, not over the files in it.** An archive cannot
be built twice into the same bytes -- it carries the times and the order
the files went in -- so a sum over the files inside would be one nobody
could repeat against what is in their hand, while the archive's own sum
is exactly that. Whether the files inside are the ones that were tagged
is `.github/workflows/release.yml`'s question, and it answers it byte for byte without
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
the attachment step in `.github/workflows/publish.yml` cannot repeat -- both files are
named in the same `gh release create` that makes the release, so a
release without them is no longer a thing a tired hand can produce.

## What it does not ask, on purpose

Everything that judges a release already standing stays in
`.github/workflows/release.yml`, which runs on `release: published`: the
archive against the tree at the tag byte for byte, the notes against the
changelog line by line, the addresses a fetched copy updates itself
from, and that the thing installs and answers `--version`. Three
questions are in both files, each marked "too late" where it stands in
`.github/workflows/publish.yml` -- program against `pyproject.toml`, the
section not empty, the archive's listing. Not duplication: after the
tag, an answer only tells you what you can no longer change.

**So the publish run is not the last one to watch.** `.github/workflows/publish.yml` going
green means the mark was set well; `.github/workflows/release.yml`, which starts by itself
the moment the release is published, is what says the thing hanging on
it is right.

## Afterwards

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
