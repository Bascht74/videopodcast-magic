---
name: test-rot
description: A test in `tests/` is red, wobbling, or green and not to be trusted — red on the builder and green here, red beside the others and green alone, a counter-proof that will not go red. Before anything is changed in the program, the test or a stand-in.
---

# Taking a red test apart

The question is: **is it the program, the test, or the stand-in?** It is
expensive when answered wrongly and cheap when asked in the right order.

The order below runs from cheap to expensive. **No step is skipped
because the next one sounds more plausible** — the first three together
cost under a minute, and they explain a red run more often than
everything after them.

---

## First: was the run even the run?

Three questions that need no file read.

### 1. The language

**`run.sh` sets `LANG=C LC_ALL=C LANGUAGE=en`. Called by hand, the
program runs in German on this Mac.** `LANG=C` alone does not settle it:
the program skips "C" on purpose and asks the system, which answers
`de_DE`. Only `LANGUAGE` decides the question.

How it shows: `0:01:00,000` instead of `0:01:00.000`, "Sprecher 1"
instead of "Speaker 1", a button that is not found, a comparison against
a string that does not exist in this language.

**This is why a single test also runs through `run.sh`:**

```bash
cd tests && bash run.sh <name_without_test_py>
```

That also sets `TMPDIR`, `VPM_FIXTURES`, `VPM_SILENT`,
`VPM_NO_SPEAKER_SPLIT`, `VPM_NO_UPDATE_CHECK`. Starting the test
straight from Python measures the environment, not the program.

### 2. The snapshot

**`VPM_SCRIPT` points at a copy, and what lies beside the program does
not lie beside the copy.** The speaker separation model is looked for
under `os.path.dirname(__file__)/models/…`, the log file is put beside
the program, the project file likewise.

Two tests sat out silently for months because of this — not red, but
skipped, and a skipped test looks harmless in the summary.

How it shows: a `SKIPPED:`, a "left a piece out", a path under
`/tmp/snap/` in the message. The probe costs one run: the same test
without `VPM_SCRIPT`, against the working file. If it goes green, it was
the snapshot.

### 3. Beside the others, or alone?

**Red beside the others and green alone means contention, not a fault.**
`run.sh` repeats every red test alone at the end by itself and then
reports it as `unsteady` — that line is already in the run and only has
to be read. `WORKERS=1` runs the whole suite one at a time.

Across runs it is counted by `tests/wobbly.sh`, and that survives the
runs being deleted:

```bash
cd tests && bash wobbly.sh report      # what is already counted
cd tests && bash wobbly.sh             # fetch the runs not yet read
```

The report keeps "beside" apart from "crashed" and names the test **and**
the machine — a test that wobbles on one machine only is a different
animal from one that wobbles everywhere.

**But contention does not mean green.** A test that loses beside eleven
others has found nothing and proved nothing. It is a defect that happens
to be asleep, and the next step is about it.

---

## Then: what the red line already says

### 4. Was it waiting on the clock instead of a condition?

**The commonest real reason for red on the builder and green here.** The
builder is about nine times slower -- measured over twelve tests on
31.8.2026, median factor 8.7, spread 5.1 to 12.6; a deadline that is
generous here is
tight there, and the test goes red while the window was working the whole
time.

**How to recognise it: the message names a deadline.** "did not appear
within 30 s", "killed by the 900 s time limit", a fixed pause in the
source, an exit after exhausted patience that does not say what never
came.

**And green on this machine proves nothing.** In a study of five large
projects, 86 percent of the tests that flaked on the pipeline could not
be made to flake on an ordinary workstation — not even in a hundred
runs. Whoever touches a waiting point checks it on the builder.

**Turning the deadline up is not a repair.** It makes every run more
expensive and pushes the fault to the next, slower machine. What helps: a
short interval, the right condition, a standstill counter instead of a
wall clock, and a sign of life that moves only because the program is
working.

---

## Only now: reading

### 5. The stand-in

**This question comes when the counter-proof will not go red.** Whoever
does not ask it mistakes a generous stand-in for a passed check — and
invisibly, because everything stays green.

A stand-in must be **at least as strict as the real thing** in every
point the check touches. Four questions:

* **Does it allow more than the real thing?**
* **Does it invent what the real thing refuses?** A stand-in media pool
  invented every track it was asked for; "only one video track created"
  was therefore green while things lay on tracks that did not exist.
* **Is it missing a call whose absence the real thing would make
  noticeable?** A stand-in timeline had no way to delete a track. The
  function that removes empty tracks ran into a swallowed exception, and
  ten empty tracks survived every run.
* **Does an `except` swallow the answer?** The most dangerous case,
  because then not even a traceback appears.

### 6. The test itself

**Does it still check what its docstring says?** A docstring that talks
about a setup some rebuild replaced sends every reader in the wrong
direction.

**Was it falsely green, and is only now showing it?** Then the red is the
find, not the damage. The question is not how it gets back to green, but
since when it checked nothing, and what went past unnoticed in that time.

**Does the failed claim rest on a precondition that is not checked
itself?** Then the red line names the last thing that was wrong and not
the first — that the camera did not switch, while in truth the player
never ran. The precondition gets a check of its own in front of it, and
the investigation starts over.

### 7. And only then the program

Now, and not before: what changed, where the fault would sit according to
the test name's prefix, and whether the number in the red line agrees
with what the program computes.

**If the program really was wrong, the red line is a gift.** Word for
word it is what belongs in `tests/state/counterproof` after the repair —
see the `gegenbeweis` skill.

---

## The other direction: green is no acquittal

**A test that is green can still be broken**, and that is the more
expensive case, because nobody goes looking for it. The signs:

* **No judgement at all.** No `check` anywhere. Green there means only
  "it did not crash", and from outside that looks exactly like a test
  that passes.
* **Too few judgements.** `%d checks` prints three where the docstring
  promises twelve. The printed count is the second safeguard, and it
  stands there in every run.
* **A `sys.exit(0)` in an escape branch.** Bowing out because the
  material is missing, and returning 0 while doing it, is
  indistinguishable from a test that checked everything. It should be
  `SKIPPED:` with the reason and the way back.
* **Assertions inside one branch of a timer chain, with an emergency
  brake beside it.** The second timer ends the test after a deadline, the
  return code is 0, and the crash on the first step goes unnoticed for
  months.
* **A check nobody has ever seen red.** No line in
  `tests/state/counterproof`. Twelve checks in this suite could not fall
  at all: one compared a call with itself, one was satisfied as soon as a
  word stood anywhere in the source, one looped over a list that could
  never fill, one passed at zero.
* **A condition the environment satisfies.** One check looked for the
  word *offset* in everything printed and was always green, because the
  program prints its own path and the working folder is called that. No
  amount of reading finds that — only a broken copy does.

---

## What stands at the end

**A red test is not made green, it is understood.**

Whoever moves the threshold until it fits has repaired nothing: they have
removed the check and left the name standing. Whoever turns the deadline
up has handed the fault on to the next machine. Whoever makes the
stand-in more generous has made the check worthless and kept everything
green while doing it.

At the end stands a sentence saying **what was wrong** — language,
snapshot, contention, deadline, stand-in, test or program — and the
number it was seen by.
