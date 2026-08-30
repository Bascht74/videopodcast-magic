---
name: test-neu
description: Anything inside a `tests/*_test.py` is about to change -- a new file, a section, a rewritten `check`, a name, a docstring, a printed line, a cleanup. Also when it is only one line, and also when no judgement changes.
---

# Writing or changing a test

`development/test_guidelines.md` says **why** all of this is so. This
says **how, and in what order**, and the twelve points at the end are
what gets answered last, one by one.

## 1. Where it belongs

**A section inside an existing test is the rule; a new file is the
exception.** What costs is not the check, it is the ground under it:
starting Python, importing a megabyte and a half of program, bringing Qt
up, letting ffmpeg build a piece of material. Whoever has already built
that ground can ask it a twentieth question for nothing.

Look at what is there first. The second line of every file is its claim:

```bash
cd tests && for f in *_test.py; do
  printf '%-26s %s\n' "${f%_test.py}" \
    "$(python3 -c 'import ast,sys
d = ast.get_docstring(ast.parse(open(sys.argv[1]).read())) or ""
print(d.splitlines()[0] if d else "(no docstring)")' "$f")"
done
```

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
entirely.

**If the claim does not fit in two or three words, it is two claims.**
Then it is split, and the name is not shortened back to a thing.

## 3. The docstring

**The first line states what holds when the test is green** — not what
it does. At most 79 characters including the three quotes, so that this
line alone decides whether a red run concerns the reader.

Under it, in eight lines: the sections in the order they come, and a
sentence about the limit of the method where there is one. **No number
that would have to travel** — "six things" over seven blocks is a second
place wanting maintenance, and it always loses. No date, no name, no
path.

**What stands in the docstring has a `check`. What a `check` tests
stands in the docstring.** Both directions, and it is looked up, not
assumed.

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

**Never a bare `assert` as a judgement.** It throws a traceback instead
of a readable line, it stops at the first failure and hides everything
behind it, it carries no numbers, and it is not counted. An `assert` is
allowed for a precondition of the material that says nothing about the
program — and then the comment beside it says that is what it is.

**A `check` name is the sentence that lands in the report**, and it is
read when nothing else is left: `check("a marked camera is the wide shot
even with a speaker on it", …)`, not `check("wide shot", …)`.

**The closing lines are always the same, and every path leads past
them:**

```python
print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
```

Where anything runs concurrently — a timer, a window — the test ends in
**one** place, and that place asks the count. A second timer that stops
the run after a deadline otherwise sends the test out with 0 although it
crashed on its first step.

## 5. What belongs in the FAIL line

**On someone else's machine, only what stands in the line itself
exists.** Six builder jobs, and all that comes back are the lines that
look like a failure; everything printed before is gone, and the run
cannot be repeated.

**So: expected and actual, as numbers.** The third argument is not
optional.

```python
# right
check("the shot does not fall below the minimum", shortest >= limit,
      "shortest %.2f s against a minimum of %.2f s" % (shortest, limit))

# wrong
check("the shot does not fall below the minimum", shortest >= limit)
```

Numbers, not adjectives: "too short" says nothing, "0.31 s against
0.80 s" says everything.

**And it must name the first thing that was wrong, not the last.**
Where a claim rests on a precondition — the player was running, the file
appeared — the precondition becomes a check of its own and stands
before it. Otherwise the line reports that the camera did not switch
while in truth nothing ever played.

## 6. Waiting

**On a condition, never on the clock.** A fixed pause costs time in
every run for ever, and it lies in both directions: too short and it
falls on a loaded machine, too long and nobody notices it is waiting for
something that never comes.

The shape is always the same: **a short interval, the condition, and a
generous upper bound.** The interval is the time lost in the normal
case; the bound is never reached in the normal case and is therefore
free.

**Give up on standstill, not on a deadline.** The builder is up to three
times slower than this machine. So what gets measured is how long
nothing has changed — that does not punish the slow machine, and it
additionally catches the case a deadline cannot see: something hanging
while there is still time left.

**A usable sign of life changes because the program is working.** A
progress bar that creeps along by itself is not one: it moves whether
anything happens or not. "The window is still up" is not one. Usable are
a value the step itself writes, a file that appears, a number that
rises, a state the program reports outright.

**Exhausted patience is red, not green**, and the line says how long it
waited and what never came. Where timeout and arrival return the same
value, the test carries on and measures something half-finished.

**A step's deadlines stay under the whole run's**, or a slow machine
learns only that the total time is up, and not which step never came.

## 7. Cleaning up

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
newer version is out.

## 8. Visible texts

**What a user sees goes through `T()`, and the German lives in
`CATALOGUE["de"]`.** If the check brings a new string into the program,
both sides change, or `german_hunt_test.py` turns red.

**A text is never written out literally in a test.** A button is found
through `vpm.T('Add files ...')`, and the test sets `vpm.set_language(
"en")` at the top. A literal ties the check to one language and one
wording.

## 9. Running it

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

## 10. The counter-proof

**Without it the check does not count.** Green says nothing about the
program until the same check has been shown to go red when the thing it
is about is wrong — and that is **per check, not per file**. Then the
entry in `tests/state/counterproof`.

How both are done is in the **`gegenbeweis`** skill. Call it; do not
copy it out.

## 10b. When no judgement changes

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

## 11. When an existing test is changed

**Read the docstring again, every time.** Does its first line still
describe what the test claims today? Does it talk about a setup some
rebuild replaced long ago? A wrong docstring sends every reader in the
wrong direction, and it is the likeliest reason a hole goes unnoticed
for years.

**A note saying "this step is red" goes out with the repair**, not in
the next tidy-up.

**And the old counter-proof entry is replaced as soon as *what* is
checked has changed.** Renaming, reordering, splitting: the what stays,
the entry holds. Moving a limit, turning a comparison round, swapping one
field for another: the what changes, and the entry is earned again.
Changing only the how is rare — so when in doubt, earn it again.

---

**The test is finished when the twelve points below have been answered
one by one.** One by one, not skimmed: the seventeen tests that checked
less than their docstring promised were all green.

## The checklist

Every one of these caught at least one of the seventeen, except 4 and 7,
which are there to stop the next one.

**1. Assert.** Does the test reach a verdict at all -- with `check`, not
a bare `assert`? How many? And if none: does that stand in the docstring
**and** in the closing line?

**2. Head and checks agree.** Has every claim of the first line got a
`check`? And does every `check` appear in the head? Both directions.

**3. The end is always reached.** Does every path through the test --
the crashed one, the concurrent one -- pass the line that counts and
sets the return code? Is the number of verdicts printed, and does it
match what the head promises?

**4. The name is a claim.** Does the prefix say which part of the
program would be broken, rather than what the material is about? Is the
second half a claim and not a thing? Does that hold for every single
`check` as well?

**5. The failure line carries its evidence.** Is it in every one --
wanted and found, as a number? And does it name the first thing that was
wrong rather than a consequence: is every precondition a check of its
own, before it?

**6. The counter-proof is done -- for each check on its own.** A version
in which exactly this one thing is false, the test run against it, the
red line read. Not one per file, one per check. Without it the check
does not count.

**7. And it stands in `tests/state/counterproof`.** The check by name,
how it was broken, the red line verbatim. This point cannot be ticked
without the entry written -- and where a check was reworded, the old
entry is replaced as soon as **what** it claims has changed.

**8. And if it would not go red: the check, or the stand-in?** Does the
stand-in allow more anywhere than the real thing -- inventing what the
real one refuses, missing a method whose absence the real one would make
felt? Does an `except` anywhere swallow the answer?

**9. Waiting is on a condition.** No fixed pause. Does the test give up
on standstill rather than on a deadline running out? Is the sign of life
something that only moves because the program is working? Do the steps'
deadlines stay under the whole run's? Is exhausted patience red?

**10. Skipping is visible.** `SKIPPED:` with a reason and the way back,
no silent `sys.exit(0)`, no step quietly left out -- and the closing line
claims nothing that was not checked. What can run on no machine is
removed rather than skipped.

**11. It cleans up.** A temporary folder rather than a fixed path,
nothing left standing afterwards, and nothing deleted or altered that
the test did not create itself.

**12. The head has been reread.** Does it still describe what the test
builds today? Is there no number in it that would have to travel? Has a
note saying "this step is red" gone out with the repair?
