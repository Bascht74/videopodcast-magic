---
name: test-neu
description: Anything inside a `tests/*_test.py` is about to change -- a new file, a section, a rewritten `check`, a name, a docstring, a printed line, a cleanup. Also when it is only one line, and also when no judgement changes.
---

# Writing or changing a test

`development/test_guidelines.md` says **why** all of this is so. This
says **how, and in what order**. Every rule stands in one place only:
the sections carry the mechanism, the measurement and the case, the
twelve points at the end carry the question that has to be answered
before the test is finished. Neither says what the other says.

## 1. Where it belongs

**A section inside an existing test is the rule; a new file is the
exception.** What costs is not the check, it is the ground under it:
starting Python, importing a megabyte and a half of program, bringing Qt
up, letting ffmpeg build a piece of material. Whoever has already built
that ground can ask it a twentieth question for nothing.

Look at what is there first. The second line of every file is its claim,
and all of them together stand in the table at the end of
`tests/README.md`, sorted under the twelve prefixes.

**It joins an existing file only if all three are yes:**

* **The same claim.** The new check fits under the existing first line
  without that line needing an "and".
* **The same ground.** It questions what already stands, instead of
  building a second lot of material beside it.
* **The same name.** The file name stays true without growing vaguer.

**One no means a new file**, even though the ground then gets built
twice. One file, one claim beats the saving: a file that claims two
things has a name that conceals one of them, and at the next rebuild
somebody clears the concealed one away.

**A new file owes a row in that table, and the row is not written by
hand.** `python3 overview.py` writes the whole table out of the
docstrings; `text_tests_listed_test.py` holds it against the folder, so
a list that was not written back turns the suite red instead of going
quietly stale. Renaming a test and rewording its first line need the
same step.

## 2. What it is called

**`<subject>_<claim>_test.py`**, at most 24 characters before
`_test.py`, lower case, English. Twelve fixed prefixes:

```
files_  sound_  time_  voice_  cut_  project_
auphonic_  window_  table_  run_  text_  source_
```

**The rule that settles every borderline case: the prefix says where
the fault would sit, not what the material is about.** A test about
channels whose fault would show in the table is `table_…`, not
`sound_…`. Whoever reads the red line should know which part of the
program is broken without opening the file.

**The second half is a claim, not a thing:** `atom_travels`, not
`log_atom`. A thing in the name covers every check that has anything to
do with that thing — including one that measures something else
entirely. **If the claim does not fit in two or three words, it is two
claims**, and it is split rather than shortened back to a thing.

## 3. The docstring

**The first line states what holds when the test is green** — not what
it does. At most 79 characters including the three quotes, so that this
line alone decides whether a red run concerns the reader.

Under it, in eight lines: the sections in the order they come, and a
sentence about the limit of the method where there is one. **No number
that would have to travel** — "six things" over seven blocks is a second
place wanting maintenance, and it always loses. **So the blocks carry
names, not numbers**; and where they are numbered after all, the
numbering is the one the test itself prints, copied from there.

What else does not belong in it: a date, a name, a path, the road that
led there, and a number out of a single run. All of that ages, and no
line is helped by it.

## 4. The judgements

**Model: `tests/table_no_place_not_wide_test.py`.** Eighteen checks on
one piece of ground, the canonical `check`, the canonical closing
lines. Canonical is what a new test is written to, not what the folder
already does: of the closing lines 46 say `ALL OK` and 69 `All good.`,
and the `check` shape below stands in five files of a hundred and
forty-five. The field is uneven; write to the canon and leave the rest.
Whoever is unsure what a line should look like reads it there.

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

**A `check` name is the sentence that lands in the report**, and it is
read when nothing else is left: `check("a marked camera is the wide shot
even with a speaker on it", …)`, not `check("wide shot", …)`.

**No logic in a test.** A loop that computes the expectation usually
computes it as wrongly as the program does. **So what the test expects
stands there as a value** — and where it really has to be computed, then
by a different route than the program takes.

**The closing lines are always the same, and every path leads past
them:**

```python
print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
```

**One line per judgement, and the closing line sums them up** — the
report shows that summary first, so it has to name every check that
fell and not only how many, which is what collecting them in `bad` is
for.

## 5. What belongs in the FAIL line

**On someone else's machine, only what stands in the line itself
exists.** Six builder jobs, and all that comes back are the lines that
look like a failure; everything printed before is gone, and the run
cannot be repeated. **So: expected and actual, as numbers. The third
argument is not optional.**

```python
# right
check("the shot does not fall below the minimum", shortest >= limit,
      "shortest %.2f s against a minimum of %.2f s" % (shortest, limit))

# wrong
check("the shot does not fall below the minimum", shortest >= limit)
```

Numbers, not adjectives: "too short" says nothing, "0.31 s against
0.80 s" says everything.

## 6. Waiting

**On a condition, never on the clock.** A fixed pause costs time in
every run for ever, and it lies in both directions: too short and it
falls on a loaded machine, too long and nobody notices it is waiting for
something that never comes.

The shape is always the same: **a short interval, the condition, and a
generous upper bound.** The interval is the time lost in the normal
case; the bound is never reached in the normal case and is therefore
free.

**What is measured is how long nothing has changed, not how long the
step has taken.** The builder is about nine times slower than this
machine -- measured on 31.8.2026 over twelve tests, median 8.7, never
below 5. Standstill does not punish the slow machine, and it
additionally catches the case a deadline cannot see: something hanging
while there is still time left.

**A usable sign of life changes because the program is working.** A
progress bar that creeps along by itself is not one: it moves whether
anything happens or not. "The window is still up" is not one. Usable are
a value the step itself writes, a file that appears, a number that
rises, a state the program reports outright.

Where timeout and arrival return the same value, the test carries on and
measures something half-finished, so they must be told apart.

**A fixed pause is allowed while a test is being written, and nowhere
else.** What the condition has to be is worth measuring rather than
guessing a number that looks safe: put a probe on a copy and see when
the thing really happens. Then the pause goes out again.

## 7. Leaving something out

**A skipped test is not a green one.** It prints `SKIPPED:` on a line of
its own, `run.sh` counts it apart, and the summary names it — `green: 50
skipped: 1`. A `sys.exit(0)` in passing is the same lie: a test that
bows out because its material is missing and returns 0 cannot be told
from one that checked everything. **The reason stands in that line: what
is missing, and what would bring it back** — "no test project" is not a
reason, "no test project — point `VPM_MEDIA` at a folder with …" is one.

There are two ways to say a section was left out, and they are counted
differently:

* **`SKIPPED:` is the loud one, and it carries the fraction.**
  `tests/text_no_german_left_test.py` prints `SKIPPED: %d of %d sections
  ran in full` and ends on `Good as far as it went -- %d of %d
  sections.` in place of `All good.` The run then counts that test as
  skipped, so it goes against the ratchet below.
* **A line beginning `LEFT OUT` is the quiet one.** `run.sh` keeps the
  test green, prints `ok, but left a piece out`, and repeats the line
  underneath — so the piece is named without the whole test being
  written off.

**How much may be left out is a ratchet.** `SKIPS_ALLOWED` in `run.sh`
holds the number; it may fall, never rise. A run that skips more returns
1 **although every check in it was green**, because it then proved less
than the run that set the number. So a new skip is never free.

**What no machine can run is removed; what one machine cannot run is
set aside by name.** The tests a single builder job cannot run are
listed in `.github/workflows/tests.yml` — a Windows registry on Linux, a
`#!/bin/sh` stand-in on Windows, a German dictation asset the macOS
runner does not carry. That step moves them out of `tests/` before the
suite starts, with the reason beside each and the count printed, so they
never reach the skip ratchet.

## 8. Cleaning up

**`tempfile.mkdtemp()`, never a fixed path.** The run points `TMPDIR` at
one folder per run and throws it away at the end.

A fixed path collides the moment two tests run side by side, it outlives
the run, and it makes one run's result depend on the last one's. **It has
already poisoned a test:** the program put its project file there, and
every following run walked into a question nobody answered.

**Leave nothing behind that a second run can find** — not in the cache,
not in the preferences store, not in the keychain. What the test sets,
it puts back.

**Never delete anything the test did not create itself.** Not
`tests/state/`, not the shared fixture folders, not the material in the
project folder. The fixture folders are built once before the fan-out and
only read afterwards; writing into them builds the next wobble.

**And nothing goes outside.** No network, no upload, no asking whether a
newer version is out. **Where a connection has to be checked, the place
that opens it is replaced** — the check is then about what the program
does with the answer, and the weather is no longer part of the result.

## 8b. What the tree looks like where it runs

**Never take the folder for the whole of what exists.** Three red runs in
one day came from that one assumption, each in a different disguise:

* **The builder sets tests aside** (§7), so counting what lies in the
  folder answers 143 on Windows and 145 here. **Ask the repository, not
  the folder** -- `git ls-files` knows what belongs to the suite whatever
  was moved; a file that is there is read from there, so uncommitted work
  still counts, and only a file that was set aside is read out of the
  last commit.
* **The working notes are not shipped.** `docs/notes/` is in
  `.gitignore` on purpose, so it is present here and absent on every
  clone. A check that resolved paths against it was green here and red on
  all six.
* **A snapshot has nothing beside it.** Under `VPM_SCRIPT` the program
  is a copy in `/tmp`, and what the program looks for next to itself --
  the speaker model, the log, the project file -- is not there. Two tests
  sat out silently for months on that.

**The proof is a clone, and it costs one command:**

```bash
git archive HEAD | tar -x -C "$(mktemp -d)"
```

Run the test in that tree. What is green there is green on the builder;
what needs the notes, a snapshot's neighbours or a full folder shows
itself at once, here, instead of four minutes later on six machines.

## 9. Visible texts

**What a user sees goes through `T()`, and the German lives in
`CATALOGUE["de"]`.** If the check brings a new string into the program,
both sides change, or `text_no_german_left_test.py` turns red.

**A text is never written out literally in a test.** A button is found
through `vpm.T('Add files ...')`, and the test sets `vpm.set_language(
"en")` at the top. A literal ties the check to one language and one
wording.

## 10. Running it

**Always through `run.sh`, a single test included:**

```bash
cd tests && bash run.sh <name_without_test_py>
```

Called by hand it lacks `LANG=C LC_ALL=C LANGUAGE=en`, `TMPDIR`,
`VPM_FIXTURES`, `VPM_SILENT`, `VPM_NO_SPEAKER_SPLIT`,
`VPM_NO_UPDATE_CHECK` — and then red or green is a statement about the
environment and not about the program.

A test is green when it returns 0 and prints neither a traceback nor
`FAIL`. **Never claim it is green without having run it.**

**A test that measures real time cannot share the machine.** Playing a
second of sound takes a second; beside eleven others it took sixteen,
and no amount of waiting fixes that. Such a test goes into `ALONE_ONLY`
in `run.sh` by name and runs by itself at the end, when everything else
is done.

## 11. The counter-proof

How a check is shown to go red when the thing it is about is wrong, and
how the entry in `tests/state/counterproof` is written, is in the
**`gegenbeweis`** skill. Call it; do not copy it out. What it leaves for
you to answer is points 6 to 8.

## 11b. When no judgement changes

A closing line, a diagnosis, a reason beside a skip, a tidier temporary
folder: none of these touch what the test claims, so the entry in
`tests/state/counterproof` stands and nothing is owed. The register hangs
on **the first argument of every `check(...)`**, nothing else -- leave
those alone and the fingerprint does not move.

Two things still have to be looked at, and both have caught somebody
out:

**Is the name already taken?** The counter template prints `done = 0`
and `global done`. In one test `done` already stood for something else,
and `%d` against `None` would have ended the file in a traceback instead
of a verdict -- the line would have broken the test it was meant to
secure.

**Does `run.sh` read the new line as something else?** It greps the
output for `^FAIL`, `[Ee]rror`, `^SKIPPED:` and `^ *(LEFT OUT|Left out)`.
A printed line that begins with any of those changes the verdict of the
whole test, however harmless it looks.

And know what the line is worth: **nothing reads the count.** Not
`run.sh`, not another test, no ratchet. A test whose checking part dies
quietly prints `0 checks in 2.7 s`, then `All good.`, and leaves green.
The line tells a person who looks; it becomes a check the day the number
is held against a floor, and then it owes a counter-proof like any
other.

## 12. What a change costs in the register

**The old counter-proof entry is replaced as soon as *what* is checked
has changed.** Moving a limit, turning a comparison round, swapping one
field for another: the what changes, and the entry is earned again.
Changing only the how is rare — so when in doubt, earn it again.

**The register draws that line for itself, and it draws it over the
wordings.** `source_checks_proved_test.py` fingerprints the first
argument of every `check(...)` in the file, as a sorted set. So renaming
the **file** costs nothing — the row is found by its fingerprint, not by
the name — and reordering the checks costs nothing either. But rewording
a judgement, adding one, or **splitting one in two** moves the
fingerprint, and the register then reports the test as rewritten since
its counter-proof, whatever the change was meant to be. A split earns
its entry again.

**And a check whose name is computed hides from all of this.** The
register collects the string constants inside the first argument, so
`check("%s names this version" % name, ...)` leaves one wording for
four checks -- and the row cannot say which of the four was ever seen
red. Two such checks stood in `text_release_ready_test.py` for versions
with no entry possible, and nothing said so: the ratchet counts tests
missing a row, and that test had rows for its other checks.

So **write the name out, once per check, even where a loop is
shorter.** A loop over four file names is four lines saved and four
counter-proofs lost.

---

## The checklist

**The test is finished when these twelve have been answered one by one.**
One by one, not skimmed: the seventeen tests that checked less than
their docstring promised were all green, and every point below caught at
least one of them, except 4 and 7, which are there to stop the next one.

**1. Assert.** Does the test reach a verdict at all -- with `check`, not
a bare `assert`? A bare `assert` throws a traceback instead of a
readable line, stops at the first failure and hides everything behind
it, carries no numbers, and is not counted. It is allowed for a
precondition of the material that says nothing about the program, and
then the comment beside it says that is what it is. How many verdicts?
And if none: does that stand in the docstring **and** in the closing
line?

**2. Head and checks agree.** Has every claim of the first line got a
`check`? And does every `check` appear in the head? Both directions, and
it is looked up, not assumed.

**3. The end is always reached.** Does every path through the test --
the crashed one, the concurrent one -- pass the line that counts and
sets the return code? Where a timer or a window runs alongside, the test
ends in **one** place and that place asks the count: a second timer that
stops the run after a deadline otherwise sends the test out with 0
although it crashed on its first step. Is the number of verdicts
printed, and does it match what the head promises?

**4. The name is a claim** (§2). Does the prefix say which part of the
program would be broken, rather than what the material is about? Is the
second half a claim and not a thing? Does that hold for every single
`check` as well?

**5. The failure line carries its evidence** (§5). Is it in every one --
wanted and found, as a number? And does it name the first thing that was
wrong rather than a consequence? Where a claim rests on a precondition
-- the player was running, the file appeared -- the precondition is a
check of its own and stands before it; otherwise the line reports that
the camera did not switch while in truth nothing ever played.

**5b. Three questions before the counter-proof, not after.** Twenty-two
judgements were found green and testing nothing in one night, and they
fall into three shapes. Ask these of every judgement while you write it:

* **Does it hold A against A?** One pure function, one argument, called
  twice. `not version_key("2.0.0") < version_key("2.0.0")` proves that
  the function is deterministic, nothing about the ordering it is named
  after -- measured, three breaks that flattened it entirely left it
  green while 23 neighbours fell.
* **Does it repeat a guard above it?** Four lines up the code already
  demanded it and waited. Then nothing happens, and the judgement asks
  the same thing again. Per construction always true.
* **Does a second net repair the fault before it looks?** Take the guard
  away and the program puts it right on a later pass, or the fixture
  happens to give the right answer for the wrong reason. Measured: a
  whole name check could be deleted and all 21 judgements stayed green.

**All three are invisible from the source.** Only a broken copy finds
them -- which is why the counter-proof is the rule and not the polish.

**6. The counter-proof is done -- for each check on its own.** A version
in which exactly this one thing is false, the test run against it, the
red line read. Not one per file, one per check. Without it the check
does not count.

**7. And it stands in `tests/state/counterproof`.** The check by name,
how it was broken, the red line verbatim. This point cannot be ticked
without the entry written -- and §12 says when an entry the diff never
touched has gone void anyway.

**8. And if it would not go red: the check, or the stand-in?** Does the
stand-in allow more anywhere than the real thing -- inventing what the
real one refuses, missing a method whose absence the real one would make
felt? Does an `except` anywhere swallow the answer?

**9. Waiting is on a condition** (§6). No fixed pause. Does the test
give up on standstill rather than on a deadline running out? Is the sign
of life something that only moves because the program is working? Do the
steps' deadlines stay under the whole run's, so a slow machine learns
which step never came and not merely that the total time is up? Is
exhausted patience red rather than green, with a line saying how long it
waited and what never came?

**10. Skipping is visible** (§7). `SKIPPED:` with a reason and the way
back, no silent `sys.exit(0)`, no step quietly left out -- and where one
was, does the closing line say how many of how many sections ran in
full, rather than claiming everything was checked? Does the skip count
stay under `SKIPS_ALLOWED`? What can run on no machine is removed rather
than skipped.

**11. It cleans up, and it does not take the folder for the world** (§8,
§8b). A temporary folder rather than a fixed path, nothing left standing
afterwards, nothing deleted or altered that the test did not create
itself. And what it reads out of the tree: would it still be there in a
clone, on a machine that set some tests aside, beside a snapshot? The
proof is the clone in §8b, and it has been run.

**12. The head has been reread.** Does its first line still describe
what the test claims today, or does it talk about a setup some rebuild
replaced long ago? A wrong docstring sends every reader in the wrong
direction, and it is the likeliest reason a hole goes unnoticed for
years. Is there no number in it that would have to travel? Has a note
saying "this step is red" gone out with the repair, rather than waiting
for the next tidy-up?
