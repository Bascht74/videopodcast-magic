# Working on videopodcast-magic

*In English only, deliberately: the source, the tests and every check
name are English, and whoever reads this is reading those anyway. The
program itself speaks both languages -- see the rule about `T()` below.*

This repository has a few rules that are not obvious from the code, and
a pull request that misses them cannot be merged however good the idea
is. They are all here. It takes ten minutes to read and saves a round
of review.

If you are an AI assistant working on somebody's behalf: read
`CLAUDE.md` as well. It is the same rules with the reasoning behind
them.

## The skills are not optional

`.claude/skills/` holds one document per situation. **Each one names a
situation, and in that situation it is read before the first edit** —
not afterwards, not from memory, not "I know what it says". A pull
request that shows a skill was not read is turned back, whatever else
is in it.

| when this is about to happen | read first |
|---|---|
| a task touches more than one file | `strang` |
| anything inside a `tests/*_test.py` changes -- also one line, also when no judgement changes | `test-neu` |
| a test is red, wobbling, or green and not to be trusted | `test-rot` |
| a check was written or changed and is green | `gegenbeweis` |
| a commit message is about to be written | `commit` |
| a section of `CHANGELOG.md` is written or changed | `changelog` |
| something a user can see has changed and `docs/` still says the old thing | `handbuch` |
| the window changed | `bilder` |
| a task is wide enough for several agents at once | `workflow` |

Two are the owner's alone and not yours: `freigabe` (a version goes
out) and `bilder` beyond reading it — the pictures need a logged-in
screen on the owner's Mac.

**This is not politeness, it is arithmetic.** The rules in these
documents were each written after something went wrong, and the
documents hold the details this page has no room for: the twelve
prefixes and what a check name has to be, how a counter-proof is earned
when the check will not go red, why a subject line that needs the diff
beside it is worth nothing. Reading the right one costs five minutes.
Not reading it has cost this project a release with three faults in it.

The pull request asks you which ones you read. Answer honestly — "none
applied, because ..." is a fine answer; a wrong "all of them" is found
in the first review.

## What the program is

`videopodcast_magic.py` is the program, and `videopodcast_magic_texts_de.py`
beside it holds every German text. There is nothing to build:
`pyproject.toml` makes a package of those modules and puts a
`videopodcast-magic` command on the path. The names carry an underscore
while the repository and the command carry a hyphen, because only an
underscore can be imported.

**It was one file until 4.9.2026, and it is being taken apart.** The
catalogue moved out first; the aim is a folder `videopodcast_magic/`
with an `__init__.py` in it and no `videopodcast_magic.py` left. None
of that is finished, and the one part of it you have to know is this:
**copy the program with the star, never alone.**

```bash
cp videopodcast_magic*.py /tmp/somewhere/      # not just the one file
```

The program reads its texts out of the folder it sits in, so a copy
without them stops on the first line with a `FileNotFoundError` -- 210
of 223 tests red at once, measured 4.9.2026. Wherever this page says
"a copy of the program", it means all of them.

**Users install it with pip3 and no other way** -- that is the rule in
`CLAUDE.md`, and it is why every Python package the program needs
stands in `pyproject.toml` and `requirements.txt`. Working on it, you
run the file out of the clone instead; the tests do the same, and for
them nothing has to be installed beyond what `requirements.txt` names
and ffmpeg on the path.

```bash
git clone https://github.com/Bascht74/videopodcast-magic.git
cd videopodcast-magic/tests
bash run.sh                    # the whole suite, several at a time
bash run.sh <name>             # one test, without the _test.py
WORKERS=1 bash run.sh          # one after another, easier to read
```

The tests under `tests/resolve/` are not part of `run.sh` and not part
of the builder. They need a running DaVinci Resolve and are started by
hand: `cd tests && bash resolve.sh`. Every run of the suite says at the
end that they are there and did not run, and says it more sharply where
git shows the Resolve branch has been worked on. On the builder it says
nothing: nobody there could start them.

A full run takes a couple of minutes. **Always through `run.sh`** — run
by hand a test lacks `LANG=C LC_ALL=C LANGUAGE=en`, `TMPDIR`,
`VPM_FIXTURES` and four more, and then red or green is a statement
about your machine and not about the program.

## The five rules that get a pull request turned away

**1. Every user-visible string exists twice.** English in the source,
German in `videopodcast_magic_texts_de.py` beside the program, keyed by
the English wording and reached through `T()`. Change one side and
`text_no_german_left_test.py` turns red. The
same holds for the manual: `docs/name.md` and `docs/name.de.md` change
together, and the German is the same thought in German, not a
translation of the English sentence.

**2. Every check owes a counter-proof.** A check that has never been
seen red is not known to check anything — in one day seventeen were
found that had been green for months while testing nothing. So: break
the one thing your check is about, in a copy of the program under
`/tmp` -- `videopodcast_magic*.py`, all of them -- run the test against
it with `VPM_SCRIPT=<the copy of the program itself>`, and keep
the red line. Then the entry in `tests/state/counterproof`: the test,
the date, the check's wording, what you broke, the red line verbatim.
`source_checks_proved_test.py` is a ratchet over the checks still
missing one.

**3. The ratchets may fall and never rise.** Four of them, in
`tests/state/`: how many comparisons shape a path on one side only, how
many comments run past four lines, how many tests skip, how many checks
owe a proof. If your change raises one, the suite is red — and the
answer is to build tighter, not to raise the number. Raising one is a
decision for the owner of the repository, in its own commit, with the
reason.

**4. A test says how many judgements it reached.** The last three lines
of every test are the same, and `run.sh` holds that number against a
floor in `tests/state/checks`. A test whose checking part dies quietly
would otherwise print nothing and stay green.

```python
print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
```

**5. The failure line carries its own evidence.** On somebody else's
machine only what stands in that line exists — six builder jobs, and
all that comes back is the lines that look like a failure. So: wanted
and found, as numbers. `"0.31 s against 0.80 s"`, never `"too short"`.

## How a test is written here

`tests/table_no_place_not_wide_test.py` is the model. The name is
`<subject>_<claim>_test.py`, at most 24 characters before `_test.py`,
and the prefix says **where the fault would sit**, not what the
material is about:

```
files_  sound_  time_  voice_  cut_  project_
auphonic_  window_  table_  run_  text_  source_
```

The second line of the file is its claim — what holds when the test is
green — and it lands in the table at the end of `tests/README.md`,
which is written by `python3 overview.py` and never by hand.

A section inside an existing test is the rule; a new file is the
exception. What costs is not the check, it is the ground under it.

**Never a bare `assert` as a judgement.** It throws a traceback instead
of a readable line, stops at the first failure, carries no numbers and
is not counted.

**Wait on a condition, never on the clock**, and give up on standstill
rather than on a deadline: the builder is up to three times slower than
a workstation.

## What the program must never do

**The Auphonic API key never goes into a file, a script, a document or
a command line.** It lives in the macOS Keychain or the Windows
Registry, and reaches curl through a temporary config file with mode
0600 so that it is never in the process list. A patch that puts it
anywhere else will not be taken.

**The program never uploads to auphonic.com on its own** — only when
somebody asked.

**Nothing is fetched from the network in a test.** Where a connection
has to be checked, the place that opens it is replaced.

## What a pull request has to carry

The template fills itself in when you open one. The short form:

* **What changes for somebody using the program**, in one sentence, in
  plain words rather than in terms of the code.
* **What you measured**, with the number. "Measure, do not guess" is
  the house rule; a claim without a number is an opinion.
* **The counter-proof for every check you added or reworded** — the
  red line, verbatim, and what you broke to get it.
* **`bash run.sh` green on your machine**, with the summary line pasted
  in. The six builder jobs run by themselves on the pull request; they
  are the evidence the merge stands on.
* **The manual, if a user can see the change.** Both languages. If the
  window moved, say so — the pictures are taken once per version by the
  owner and are not yours to regenerate.
* **A changelog entry, if a user can see the change.** Both languages,
  the same number of points on each side. `CHANGELOG.md`, under the
  topmost unreleased heading, or say in the pull request that you left
  it to the owner.

## What a pull request should not carry

* **A new version number or a tag.** Releases are the owner's, and the
  tag comes last, after the six jobs are green.
* **Regenerated pictures.** `docs/images/` is taken by a script that
  needs a logged-in screen on the owner's Mac.
* **A raised ratchet**, unless that is the whole point of the change
  and it says so.
* **Reformatting.** A diff that moves lines nobody asked about hides
  the change inside it.
* **Several things at once.** If the subject line needs an "and", it is
  usually two pull requests. The reliable check is `git diff --stat`:
  if the files fall into groups that could have gone out separately,
  they should have.

## The commit message

It is read in a list, without the diff beside it — `git log --oneline`
shows one line and nothing else. So the subject names the thing as it
stands on the screen (a switch, a button, an entry, a file), says what
is different afterwards, and carries the fix rather than only the
fault. The reasoning, the numbers and what the change deliberately does
not reach go in the body.

Not: `tests that check, and a rule that says how`.
Rather: `--head and --tail are gone` or `the zoom buttons stay under
the pointer`.

## If something here is wrong

Say so in the pull request. These rules were written down because the
project learned them the hard way, but a rule that has outlived its
reason is worth more as a question than as an obstacle.
