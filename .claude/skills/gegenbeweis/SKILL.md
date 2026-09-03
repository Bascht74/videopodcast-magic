---
name: gegenbeweis
description: A check in tests/ has just been written or changed and it is green — how to show that the same check goes red when the thing it is about is false, and how to write the proof into tests/state/counterproof.
---

# Showing that a check bites

Green says nothing about the program until the same check has been seen
red with the thing it is about broken. **No change to a test and no new
test is finished until its entry stands in
`tests/state/counterproof`.**

Why this is held so tightly is in `development/test_guidelines.md`,
section 5. How to do it is here.

## The run

**Copy the program into scratch space, break the one thing there, run
the test against that copy. The repository is not touched.**

```bash
cp videopodcast_magic.py /tmp/broken.py
# break exactly the one thing the check is about
cd tests && LANG=C LC_ALL=C LANGUAGE=en VPM_SILENT=1 \
  VPM_NO_SPEAKER_SPLIT=1 VPM_NO_UPDATE_CHECK=1 \
  VPM_SCRIPT=/tmp/broken.py python3 <name>_test.py
```

**The language variables are not optional.** Without `LANG=C LC_ALL=C
LANGUAGE=en` the program runs German on this Mac — `LANG=C` alone does
not settle it, the program skips "C" on purpose and asks the system,
which answers `de_DE`. The test then holds an English expectation
against German output and goes **red for the wrong reason**, which is
not a counter-proof but a lost hour. `run.sh` sets these three and the
three beside them; a test started on its own has to set them itself.

**Where the check is not about a place in the program but about a
computation over data**, the falsified version belongs in the test
itself, next to the check: the same reading over a faked list, with the
offset turned round, with the switch off. That version stays in scratch
space too, or is taken back out after the run.

## One trap when they are done in series

**Give every broken copy its own file name.** Python keeps a
`__pycache__` entry for a copy loaded through `spec_from_file_location`
and holds it valid as long as **size and mtime** of the source agree.
Two turned-round signs one after the other are the same size, and
written within the same second they are the same mtime -- so the second
run reads the bytecode of the first.

Measured, and it cost a finding: a strand got a green run back from a
break that should have gone red, reported "this check tests nothing",
and had to withdraw it. **A green counter-proof is a claim about the
check. Make sure it is not a claim about the cache.**

A serial number in the name of every broken copy costs nothing and
settles it.

**And give every run its own `VPM_CACHE`.** The same trap wears a second
coat: a check on the words came back green not because the program was
whole but because the words were on disk from the run before, and the
broken place was never entered. Measured, and it cost one false find.
`VPM_CACHE=<your folder>` beside the three language variables.

## How small the damage has to be

**A sign turned round. A limit moved by one. A call taken away.**
Nothing larger.

Take the program apart wholesale and everything goes red, and you have
learned nothing about this one check. And the elaborately staged,
lifelike fault buys nothing the turned-round sign does not buy — that
is measured, not assumed.

## One per check, not one per file

**A file with sixty-five checks owes sixty-five counter-proofs.** A
counter-proof shows that *this one* check falls when *this one* thing
is false. About the sixty-four beside it, it says nothing — and that is
exactly where the checks that could not fall at all were standing.

It is cheaper than it looks: the copy is made once, the broken spot
travels from check to check, the run is the same. What costs time is
working out what exactly would have to be broken, and that is the
return: it forces you to read the check as a claim about the program
rather than as a line of source.

**For changed checks too, not only new ones.**

## Keeping the red line

**It is the evidence.** Take the `check` line that fell, word for word,
not the summary: it names the check and carries the numbers.

```
  a target is applied, not only reported               FAIL no target line in the log
```

**If the red line names something other than what you broke**, the
check did not catch what it was supposed to catch. Then it is not the
entry that gets written, it is the check that gets fixed.

## The entry

`tests/state/counterproof`, one line per test, **tab-separated**. Two
kinds of row:

```
test    when    checks  what was broken     the red line
open    test    checks
```

The five fields of an entry:

1. **The test name with the `_test.py` cut off.**
2. **The date as `YYYY-MM-DD`.** Anything else is refused.
3. **The wording of the check itself** — the first argument of the
   `check(...)` this row is about, copied exactly. One row per check,
   not one per file. That is also the whole answer to "does my edit void
   the entry?": leave those strings alone and it does not. Reword a
   check, add one or split one in two, and its row is void.

   The register is read as `(test, wording)`; the same pair twice is
   red, and so is a row whose wording no test says any more.
4. **What was broken**, at least eight characters, and precise enough
   that somebody can repeat it without thinking: the one place and the
   one change. If it was not the program, this says what it was against
   instead — the falsified data, the stricter stand-in.
5. **The red line, word for word.** It has to contain `FAIL`, and it
   must contain no tab, or it falls apart into several fields.

The `open` rows are the census of what is still owed, and there are
more of them than finished entries -- about two thirds of the file. A
row that carries a red line is the exception so far, not the rule.

**A row is addressed by its wording, never by its line number.** The
file is written by many hands in one night, and every entry above a row
moves it. Measured on 2.9.2026: a strand handed the next one "delete
line 1452"; by the time that was read, 1452 was a row belonging to a
different test, and following the instruction would have taken out an
unrelated file's counter-proof.

**So a hand-off says the test and the wording**, and whoever merges
looks the pair up. The same holds for a machine: a merge keyed on
`(test, wording)` replaces the right row and cannot damage a
neighbour's. One keyed on a line number can.
They are the
ratchet: the number may fall, never rise. **So a new test gets a
finished entry, not an `open` row** — an `open` row would raise it.

**Delete that test's `open` row in the same edit that adds its entry.**
With both rows carrying the same wording, `source_checks_proved_test.py`
reports the check as being in the register twice.

### The suite finds a row by its wording, not by the file name

`source_checks_proved_test.py` reads the first argument of every
`check(...)` out of each test and holds the set against the register.
So a row survives the **file** being renamed, and it dies when a
**check** is reworded — the wording is the whole of the link.

* **A test that still owes rows** stands in the register as `open`
  lines, one per unproved check: `open <test> <wording>`.
* **Replace an `open` line with the finished row in the same edit.**
  Both carrying the same wording counts as the check being in the
  register twice, and the run says so.
* **A finished row whose wording no check says any more** is just as
  red. Whoever rewords a check takes its old row out and earns a new
  one — see §12 of `test-neu`.

Both only happen when nothing else in that run is red. And
`source_checks_proved_test.py` writes the file back itself — do not edit it by
hand while a run is going.

### When an old entry has to be replaced

**If *what* the check claims changes, the entry is void and a new one
is owed. If only *how* it looks changes, the entry stands.** Moving a
limit, turning a comparison round, swapping one field for another: the
what changes.

The machine sees one half of this. Reword a judgement and the register
no longer finds it, and `source_checks_proved_test.py` reports the
check as owing a counter-proof again. **The other half it cannot
see:** a check that keeps its wording and changes its claim stays green
with an entry that no longer proves anything.

Nothing goes red there, so it gets a step. Before the test is called
finished:

```bash
git diff -- tests/<name>_test.py             # what really moved
grep -P '^<name>\t' tests/state/counterproof # the rows as they stand
```

**For every check the diff touched whose wording did not move, quote its
row's fourth field -- what was broken -- and answer one question: would
breaking exactly that, in exactly that place, still make this check
fall?** Not "probably". No, or unsure, and the row is void: earn it
again. The quoted field and the answer go in the report beside the
check, because an answer that is only thought is the same as no answer.

**No case of this is on record, and that is the finding**, not an
acquittal: nothing in the repository can report one. What the register
*can* see went unnoticed for versions all the same -- two checks with a
computed name in `text_release_ready_test.py`, one wording for four
checks, and the ratchet said nothing (`80f46d5`, 1.9.2026).

## When the counter-proof will not go red

**Then the first question is: the check, or the stand-in?** Anybody who
does not ask it is taking a generous stand-in for a check that passed.

**A stand-in has to be at least as strict as the real thing in every
point the check touches.** Two ways it fails to be, and both have
happened here:

* **It invents what the real thing refuses.** A stand-in media pool
  created every track it was asked for. The check "only one video track
  was made" was green while things sat on tracks that did not exist.
  How to spot it: the check stays green when you ask the program for
  something plainly impossible. Ask the stand-in for something that
  cannot exist — if it answers politely, the stand-in is the fault.
* **It lacks a method whose absence the real thing would make felt.** A
  stand-in timeline had no way to delete a track. The function that
  removes empty tracks ran into a swallowed exception, and ten empty
  tracks survived every run. How to spot it: **an `except` that prints
  nothing**, in the program as in the stand-in. Find the ones on the
  path the check takes, and make them talk once.

**The swallowed exception is the dangerous case**, because not even a
traceback appears: the program asks for something the stand-in does not
have, and the test sees none of it.

**So the counter-proof tests not only the check but the scaffolding
under it.** That is its second return.

## Two findings that fall out along the way

**If other checks that should have caught the same fault stay green,
that is a second finding** — not a reason to relax.

**Where it becomes disproportionate**, because the thing checked can
only be false outside this program — a third-party tool that cannot be
broken without being replaced — then a stricter stand-in is the
counter-proof, or it is a smoke test and says so in its head. **What
does not count as a reason: there are a lot of them.**
