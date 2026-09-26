---
name: test-neu
description: Anything inside a `*_test.py` under `tests/` is about to change -- a new file, a section, a rewritten `check`, a name, a docstring, a printed line, a cleanup. Also when it is only one line, and also when no judgement changes.
when: anything inside a `*_test.py` under `tests/` changes -- also one line, also when no judgement changes
tables: claude, contributing, agents, pr
order: 20
---

# Writing or changing a test

`development/test_guidelines.md` says **why** all of this is so. This
says **how, and in what order**; the questions at the end carry what has
to be answered before the test is finished. The measured case behind a
rule stands in the case book, `.claude/skills/test-neu/cases.md`, under
the number of its section here.

## Before any of it: should this check exist at all?

This decides **whether**, before everything below decides where and how.

**Do not write a check because something was changed.** Write one where
something could break without anybody noticing, and say in one sentence
**what it protects**. A function that only hands its argument on, a
wrapper with no judgement of its own, a value read straight back out of
a dictionary: those break loudly or not at all.

**Here a needless check costs a chain**: a counter-proof, a deliberately
broken copy, a run against it, a row in the register -- and everybody
who comes after reads it. **When you are not sure, do not write it.**
Describe the check and what it would catch, and let the owner decide;
that costs one sentence and is reversible.

## 1. Where it belongs

**A section inside an existing test is the rule; a new file is the
exception.** What costs is the ground, not the check: starting Python,
importing the program, bringing Qt up, letting ffmpeg build material.
Whoever has built that ground can ask it a twentieth question for
nothing. Look first: the second line of every file is its claim, and all
of them stand in the table at the end of `tests/README.md`, sorted under
the twelve prefixes.

**It joins an existing file only if all three are yes:**

* **The same claim.** It fits under the existing first line without an "and".
* **The same ground.** It questions what stands, instead of building
  a second lot of material beside it.
* **The same name.** The file name stays true without growing vaguer.

**One no means a new file**, even though the ground is then built twice:
a file that claims two things has a name that conceals one, and at the
next rebuild somebody clears the concealed one away.

**A new file owes a row in that table, never written by hand.**
`python3 overview.py` writes it out of the docstrings, and
`text_tests_listed_test.py` holds it against the files. Renaming a test
and rewording its first line need the same step.

**A new file lies in the folder of the piece it checks** --
`tests/<piece>/`, `<piece>` being the folder under `videopodcast_magic/`
whose logic it judges. Two kinds of folder are no piece:
`tests/source/` holds the tests that read the source, the texts and the
documents as a whole; a `live/` folder under a piece holds the tests
that talk to what the suite only stands in for -- `tests/resolve/live/`
a running Resolve, `tests/auphonic/live/` auphonic.com. `run.sh` never
takes them; `tests/<piece>.sh` starts them on the owner's OK, and their
counter-proofs stand in a `counterproof` beside them. `tests/resolve/`
itself is a piece like any other; `tests/samples/` holds checked-in
material and no test. `run.sh` finds a test by name wherever it lies,
and the preamble every test opens with finds `tests/` from there -- copy
it from any test, word for word.

**Under the docstring stands `PLATFORM_BOUND = True` or `False`: a new
test sets it, a changed test has it looked at again.** False means the
verdict cannot differ between Linux, macOS, Windows or the two Pythons
-- the test reads the repository or calls the program in memory -- and
it then runs once, on the builder's neutral job. The day it starts a
process, opens a window, writes a file whose path or lock matters, or
asks the platform, it is True; in doubt, True.
`source_platform_declared` holds the spelling and the imports.

## 2. What it is called

**`<subject>_<claim>_test.py`**, at most 24 characters before
`_test.py`, lower case, English. Twelve fixed prefixes:

```
files_  sound_  time_  voice_  cut_  project_
auphonic_  window_  table_  run_  text_  source_
```

**The prefix says where the fault would sit, not what the material is
about** -- that settles every borderline case. A test about channels
whose fault would show in the table is `table_…`, so whoever reads the
red line knows which part is broken without opening the file.

**The second half is a claim, not a thing:** `atom_travels`, not
`log_atom`. A thing covers every check that touches it, including one
that measures something else. **If the claim does not fit in two or
three words, it is two claims**, and it is split, not shortened back to
a thing.

## 3. The docstring

**The first line states what holds when the test is green**, not what
it does -- at most 79 characters including the three quotes, so that
this line alone decides whether a red run concerns the reader.

Under it, in eight lines: the sections in the order they come, and the
limit of the method where there is one. **No number that would have to
travel** -- "six things" over seven blocks is a second place wanting
maintenance, and it always loses. **So blocks carry names, not
numbers**; where they are numbered after all, it is the numbering the
test itself prints. Nor a date, a name, a path, the road that led there,
or a number out of a single run: all of that ages.

**Head and checks are held against each other in both directions, and
it is looked up, not assumed** -- every claim of the first line has a
`check`, and every `check` appears in the head (the seventeen that
failed this: the case book, §3).

**The head is reread whenever the test changes**: a wrong docstring
sends every reader the wrong way and is the likeliest reason a hole
survives for years. A note saying "this step is red" goes out with the
repair, not at the next tidy-up.

## 4. The judgements

**Model: `tests/cut/table_no_place_not_wide_test.py`** -- eighteen checks
on one piece of ground, the canonical `check` and closing lines.
Canonical is what a new test is written to, not what the folder already
does (it is uneven: the case book, §4); write to the canon and leave the
rest. Unsure what a line should look like, read it there.

```python
began = time.time()
done = 0
bad = []


def check(name, ok, extra=""):
    global done
    done += 1
    print("  %-58s %s %s" % (name, "ok" if ok else "FAIL", extra))
    if not ok:
        bad.append("%s [%s]" % (name, extra or "no numbers"))
```

**A verdict is a `check`, never a bare `assert`.** An `assert` throws a
traceback instead of a line, stops at the first failure and hides the
rest, carries no numbers, and is not counted. It is allowed for a
precondition of the material that says nothing about the program, with
a comment beside it saying so.

**A `check` name is the sentence that lands in the report**, read when
nothing else is left: `check("a marked camera is the wide shot even with
a speaker on it", …)`, not `check("wide shot", …)`. **§2 holds for it
too**: a claim, naming the part the fault would sit in.

**No logic in a test.** A loop that computes the expectation usually
computes it as wrongly as the program. **What the test expects stands
there as a value** -- and where it has to be computed, by a different
route than the program takes.

**The closing lines are always the same, and every path leads past
them:**

```python
print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
```

**One line per judgement, and the closing line names every check that
fell**, not only how many -- the report shows that summary first, which
is what `bad` is for. **Where a test reaches no verdict at all** (it only
builds or prints), docstring and closing line say so, rather than let
`0 checks` read as a pass.

**Every path means the crashed one and the concurrent one.** Where a
timer or a window runs alongside, the test ends in **one** place that
asks the count; otherwise a second timer that stops the run after a
deadline sends it out with 0 although it crashed on its first step.

## 5. What belongs in the FAIL line

**On someone else's machine, only what stands in the line itself
exists.** Six builder jobs, and all that comes back are the lines that
look like a failure; the rest is gone and the run cannot be repeated.
**So: expected and actual, as numbers. The third argument is not
optional.** Numbers, not adjectives: "too short" says nothing, "0.31 s
against 0.80 s" says everything.

```python
# right
check("the shot does not fall below the minimum", shortest >= limit,
      "shortest %.2f s against a minimum of %.2f s" % (shortest, limit))

# wrong
check("the shot does not fall below the minimum", shortest >= limit)
```

**The line names the first thing that was wrong, not a consequence.**
Where a claim rests on a precondition -- the player was running, the
file appeared -- that is a check of its own and stands before it;
otherwise the line says the camera did not switch while nothing ever
played.

## 5b. Three shapes of a blind judgement

**Ask these of every judgement while you write it, before the
counter-proof and not after:**

* **Does it hold A against A?** One pure function, one argument, called
  twice: it proves determinism, nothing about the rule it is named after.
* **Does it repeat a guard above it?** The code already demanded and
  waited for it; the judgement asks again and is true by construction.
* **Does a second net repair the fault before it looks?** Take the guard
  away and a later pass puts it right, or the fixture gives the right
  answer for the wrong reason.

**All three are invisible from the source.** Only a broken copy finds
them -- which is why the counter-proof is the rule, not the polish.

## 5c. A judgement that forbids the repair

**The other direction: the judgement is green while a fault stands and
goes red the moment somebody fixes it.** It is dearer than a blind one,
because it **costs the next person their improvement**: they build what
the head asks for, see red, and believe they broke something.

**Ask: if the thing this judgement describes were put right tomorrow,
would the judgement still be true?** If not, it describes today's state
as though it were the contract. It says what the program does, never
what the program may never stop doing. **Where a judgement really has to
pin a fault**, because something downstream depends on it, the docstring
says so in words, so the next person reads it before the red line.

## 5d. A guard that eats the judgement

**Does a guard above it ask what the judgement below asks?** A wait or
precondition put in for a better failure line can demand exactly what
the check demands -- and then the check never runs, while the file still
counts it and the register still holds its row.

**`source_checks_proved` cannot see it** -- it sees a wording that has
gone, not a judgement that can no longer be reached. **So ask it by hand:
run the row's own recorded break and count the checks.** Short means a
guard ate the judgement. **The repair keeps the guard** and lets it
**give up into** the judgement rather than instead of it: wait, then
judge either way, and let the line say which of the two happened.

## 6. Waiting

**On a condition, never on the clock.** A fixed pause costs time in
every run for ever and lies both ways: too short, it falls on a loaded
machine; too long, nobody notices it waits for something that never
comes. **The shape: a short interval, the condition, a generous upper
bound** -- the interval is what the normal case loses, the bound is
never reached and so free.

**Measure how long nothing has changed, not how long the step took.**
The builder is about nine times slower than this machine (the case book,
§6). Standstill does not punish the slow machine, and it catches what a
deadline cannot: a hang while time is left.

**A usable sign of life changes because the program is working** -- a
value the step writes, a file that appears, a number that rises, a state
the program reports outright. A progress bar that creeps by itself is
not one, nor "the window is still up". **Timeout and arrival must be
told apart** where they return the same value, or the test carries on
measuring something half-finished.

**A step's own deadline stays under the whole run's**, so a slow machine
learns which step never came. **Exhausted patience is red, not green**,
with a line saying how long it waited and what never came.

**A fixed pause is allowed while a test is being written, and nowhere
else.** Measure what the condition has to be -- a probe on a copy, see
when the thing really happens -- then the pause goes out again.

## 7. Leaving something out

**A skipped test is not a green one.** It prints `SKIPPED:` on a line of
its own, `run.sh` counts it apart, and the summary names it -- `green:
50 skipped: 1`. A `sys.exit(0)` because material is missing is the same
lie. **The reason says what is missing and what would bring it back** --
not "no test project", but "no test project -- point `VPM_MEDIA` at a
folder with …".

Two ways to say a section was left out, counted differently:

* **`SKIPPED:` is the loud one, with the fraction.**
  `tests/language/text_no_german_left_test.py` prints `SKIPPED: %d of
  %d sections ran in full` and ends on `Good as far as it went -- %d of %d
  sections.` instead of `All good.`; the run counts it as skipped, so it
  goes against the ratchet.
* **A line beginning `LEFT OUT` is the quiet one.** `run.sh` keeps the
  test green, prints `ok, but left a piece out`, and repeats the line
  underneath.

**How much may be left out is a ratchet.** `SKIPS_ALLOWED` in `run.sh`
may fall, never rise; a run that skips more returns 1 **although every
check was green**, because it proved less. A new skip is never free.

**What no machine can run is removed; what one machine cannot run is set
aside by name** in `.github/workflows/tests.yml` -- a Windows registry
on Linux, a `#!/bin/sh` stand-in on Windows, a German dictation asset
the macOS runner lacks. That step moves them out of `tests/` before the
suite, with the reason beside each and the count printed, so they never
reach the ratchet.

## 8. Cleaning up

**`tempfile.mkdtemp()`, never a fixed path.** The run points `TMPDIR` at
one folder per run and throws it away. A fixed path collides when two
tests run side by side, outlives the run, and ties one run's result to
the last -- **it has already poisoned a test**, whose project file left
every following run in a question nobody answered.

**Leave nothing a second run can find** -- not in the cache, the
preferences store or the keychain. What the test sets, it puts back.
**Never delete what the test did not create** -- not `tests/state/`, not
the shared fixture folders, not the project material. Fixture folders
are built once before the fan-out and only read afterwards; writing into
them builds the next wobble.

**Nothing goes outside.** No network, no upload, no update check.
**Where a connection has to be checked, the place that opens it is
replaced** -- the check is then about what the program does with the
answer, and the weather is no longer part of the result.

## 8b. What the tree looks like where it runs

**Never take the folder for the whole of what exists** -- three red runs
in one day came from that assumption:

* **The builder sets tests aside** (§7), so counting the folder answers
  fewer on Windows than here. **Ask the repository** -- `git ls-files`
  knows what belongs to the suite whatever was moved; a file that is
  there is read from there, so uncommitted work counts, and only a file
  set aside is read out of the last commit.
* **The working notes are not shipped.** `docs/notes/` is in
  `.gitignore`, present here and absent on every clone; a check that
  resolved paths against it was red on all six.
* **A snapshot has nothing beside it.** Under `VPM_SCRIPT` the program
  is a copy in `/tmp`, and the log and project file it looks for beside
  itself are not there. The speaker model is the exception: it lies in
  the program's own folder and travels with a `cp -R` of it.

**The proof is a clone, and it costs one command:**

```bash
d=$(mktemp -d) && git archive HEAD | tar -x -C "$d" \
    && ( cd "$d" && git init -q && git add -A )
```

**Neither the `git init` nor the `git add` is tidiness.** Without `.git`,
`source_no_real_names` skips, and with the one allowed skip already spent
on `auphonic_key_kept` the run comes back red with nothing red in it.
**An empty repository is not enough either**: the check asks `git
ls-files`, which reads the index, and `git init` leaves it empty
(measured: the case book, §8b). Run the test in that tree: what is green
there is green on the builder, and what needs the notes, a snapshot's
neighbours or a full folder shows itself here, not four minutes later.

## 8c. A number that is also in the program is not written down twice

**Fetch it from there.** A test that spells out what the program says is
green until the program says something else, and then red for a reason
that is not a fault. **The version number is the dearest**: it moves
once per release, and the test looks green every day in between -- it
has cost a release its first attempt (the case book, §8c).

**The repair is measured against a different number, not today's**: a
fix that derives the value but still writes down the point it is asked
from holds for exactly one release. So: derive it, and prove the
derivation by moving the number -- a copy set two releases ahead.

## 9. Visible texts

**What a user sees goes through `T()`, and the German lives in
`language/de.po` inside the program's folder, read by
`language/__init__.py` into `CATALOGUE`.** A new string changes both
sides, or `text_no_german_left_test.py` turns red. **A text is never
written out literally in a test**: a button is found through
`vpm.T('Add files ...')`, with `vpm.set_language("en")` at the top. A
literal ties the check to one language and one wording.

## 10. Running it

**Always through `run.sh`, a single test included:**

```bash
cd tests && bash run.sh <name_without_test_py>
```

Called by hand it lacks `LANG=C LC_ALL=C LANGUAGE=en`, `TMPDIR`,
`VPM_FIXTURES`, `VPM_SILENT`, `VPM_NO_SPEAKER_SPLIT`,
`VPM_NO_UPDATE_CHECK` -- and then red or green is a statement about the
environment and not about the program.

**That list stands here, in `gegenbeweis` and in `test-rot`, and the
repetition is on purpose:** each of the three is reached without reading
the other two, and a wrongly set `LANGUAGE` costs an hour. Do not tidy
it away.

A test is green when it returns 0 and prints neither a traceback nor
`FAIL`. **Never claim it is green without having run it.** **A test that
measures real time cannot share the machine** -- a second of sound took
sixteen beside eleven others -- so it goes into `ALONE_ONLY` in `run.sh`
by name and runs alone at the end.

## 11. The counter-proof

How a check is shown to go red when the thing it is about is wrong, and
how the entry in `tests/state/counterproof` is written, is in the
**`gegenbeweis`** skill. Call it; do not copy it out. What it leaves for
you to answer is points 6 to 8.

## 11b. When no judgement changes

A closing line, a diagnosis, a reason beside a skip, a tidier temporary
folder: none touch what the test claims, so the entry in
`tests/state/counterproof` stands and nothing is owed. The register
hangs on **the first argument of every `check(...)`**, nothing else --
leave those alone and the fingerprint does not move. Three things are
still looked at:

* **Is the name already taken?** The counter template brings `done = 0`
  and `global done`; where `done` already means something else, the line
  ends the file in a traceback (the case book, §11b).
* **Does `run.sh` read the new line as something else?** It greps for
  `^FAIL`, `[Ee]rror`, `^SKIPPED:` and `^ *(LEFT OUT|Left out)`; a
  printed line beginning with any of those changes the whole verdict.
* **Nothing reads the count.** Not `run.sh`, not a test, no ratchet: a
  test whose checking part dies quietly prints `0 checks`, then `All
  good.`, and leaves green. The line becomes a check the day the number
  is held against a floor, and then it owes a counter-proof.

## 12. What a change costs in the register

**When an entry goes void and has to be earned again -- *what* is
checked against *how* it looks -- is in the `gegenbeweis` skill.** Call
it; do not copy it out.

**One rule belongs here: a check whose name is computed hides from the
register.** It collects the string constants in the first argument, so
`check("%s names this version" % name, ...)` leaves one wording for four
checks, and the row cannot say which was ever seen red (the case book,
§12). So **write the name out, once per check, even where a loop is
shorter** -- four lines saved are four counter-proofs lost.

## Before it counts as done

**Thirteen questions, answered one by one and not skimmed.**

1. **Assert** (§4). Every verdict through `check`, never a bare `assert`?
2. **Head and checks agree** (§3). Both directions, and looked up?
3. **The end is always reached** (§4). Every path past the closing
   lines, the crashed and the concurrent one included?
4. **The name is a claim** (§2, §4). The file's name, and every
   `check` name in it? And the file in the folder of its piece (§1)?
5. **The failure line carries its evidence** (§5). In every one, as numbers?
6. **The judgement can fall, and was seen falling** (§5b, §5c, §5d,
   §11). A counter-proof for each check on its own?
7. **And it stands in `tests/state/counterproof`** (§11, §11b, §12).
   No check hiding behind a computed name?
8. **And if it would not go red: the check, or the stand-in?** The
   four questions are in the `gegenbeweis` skill.
9. **Waiting is on a condition** (§6). Standstill rather than a
   deadline, and exhausted patience red?
10. **Skipping is visible** (§7). `SKIPPED:` with the reason and the
    way back, and the count under `SKIPS_ALLOWED`?
11. **It cleans up, and does not take the folder for the world** (§8,
    §8b). Has the clone been run, with `git init` and `git add -A` in it?
12. **No number written twice** (§8c). Does any judgement spell out a
    number the program also holds -- the version above all? Taken from
    there, and proved by moving it?
13. **The head has been reread** (§3). Does its first line still
    describe what the test claims today?
