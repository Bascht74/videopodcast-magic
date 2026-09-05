---
name: ci
description: A commit has just been pushed, or a run on the builder is being waited for, or one has come back red. Six machines answer in four minutes and nothing here says when -- so the answer has to be waited for rather than asked after.
when: a commit has been pushed and the builder has not answered yet
tables: claude, contributing, agents
order: 60
---

# The builder's answer

A commit has been pushed and six machines are answering, or one of them
has come back red. This file decides how the answer is waited for, what
it is worth once it arrives, what is done with the queue after a green
run, and how a red job caused by the machine is told from one caused by
us. What to do with a test that is red, wobbling or not to be trusted is
the skill `test-rot`; what a release needs beyond a green run is
`freigabe`.

## Waited for, not asked after

**Nothing tells this machine when a run ends.** The answer used to be
fetched by asking again, and again, and between two asks the work went
on against a state the builder had already faulted. Twice in one day a
repair was built on top of a commit that was red.

So it is waited for, not asked after. Straight after the push:

```bash
cd tests && bash await_ci.sh
```

**and started as a background command that the harness keeps hold of --
`run_in_background`, not a detached `&` in the shell.** That difference
is the whole point: a detached shell runs and finishes and nobody is
told, so the waiting has been done and the answer is still fetched by
asking. A background command the harness tracks wakes whoever started
it when it exits, with the verdict already in its output.

It finds the run for HEAD -- waiting for it to appear, because a push
and its run are seconds apart and "the newest run" answers with the one
before -- then blocks until the run ends and comes back by itself with
the verdict of every job. Green, it says the tag may follow. Red, it
names what fell.

## What the answer is worth

**Green here is not green there.** This Mac has cores to spare and
finishes the suite in half a minute; the builder takes four minutes over
six machines, and three of the things that went red this month could not
be seen here at all:

* **A path put into shape on one side of a comparison.** On a Mac the
  two are the same string. On Windows they differ by drive letter,
  separator and case.
* **A test set aside per platform.** The workflow moves the tests a
  machine cannot run out of the way, so counting what lies in `tests/`
  answers fewer there than here -- 143 against 145 when that was
  counted.
* **A wait that is generous here and tight there.**

**And red there is not always a fault.** Read the skill `test-rot`
before changing anything: language, snapshot, contention and deadline
between them explain a red run more often than the program does, and
they cost under a minute to rule out.

## Six jobs, and what you are waiting for

`ubuntu`, `macos` and `windows`, each on two versions of Python. **What
stands between a push and an answer is the longest job, not the sum** --
they run side by side. The sum is what the builder is billed.

A single reading of a macOS job says almost nothing: the same commit has
come back at 950 and at 1091 seconds, and once at 651 against 1088.
Never believe a jump from a single reading. Two runs, or a steadier machine,
before a number means anything.

## After a green run, the queue

**Before every release, fetch the builder's times and look at them.**
This is the moment the command is run, and this section is the whole
account of it -- nothing else in the project keeps a copy.

The suite runs the long tests first so nobody waits, and it takes that
order from `tests/state/longest`. **Those times have to come from the
builder**, and only a green run has them all:

```bash
cd tests && bash builder_times.sh
```

It asks the run which job was slowest -- that has changed platform
before, so it is asked and not written down -- and writes that job's
numbers over the file. Then read the ten it prints and ask whether the
top two can be made cheaper. That is where a minute of the builder's
time is.

**A renamed test leaves a dead row behind.** After a rename the file
names tests that no longer exist, `run.sh` finds no time for any of
them, and the queue orders nothing until this has run against a green
run made *after* the rename. It does not heal by itself.

## Watch what the runs are called

GitHub names a run after the commit subject unless it is told otherwise,
and a list of runs then reads as a heap of unrelated sentences. Every
workflow carries a `run-name:` of its own; one without it is not
finished.

## Where the log has gone

A deleted run answers 404 and an aged one answers nothing at all -- and
an empty list of failures reads exactly like a run that was red with
nothing wrong. `await_ci.sh` says which it is rather than printing
nothing.

Logs are kept for ninety days, and deleting old runs by hand deletes the
evidence with them. What is worth keeping across that is counted into
`tests/state/wobbly` by `bash wobbly.sh`, which reads a run once and
keeps its numbers whether or not the run survives.

## Is it us, or is it the machine?

**Ask this before reading a single test line.** A red job has two quite
different causes, and treating one as the other wastes a whole round: a
check that really failed, or a runner that never got as far as checking.

**The signs that it is the machine, not the code:**

* **A tool is missing that the workflow installs** -- ffmpeg absent on
  Linux, PySide6 not resolving, a wheel that would not build. The red
  line then names a program, not a judgement.
* **The failure sorts by something the code knows nothing about.** Two
  jobs of the same Python version on different operating systems, or
  every job on one runner image. Our faults sort by *platform* (paths,
  file locking, a fixed `/tmp`), almost never by interpreter version
  across platforms.
* **A job hangs far past the others.** Measured on 1.9.2026: four jobs
  finished in three to five minutes while two sat at thirteen. Compare
  against `state/longest`, which holds what the slowest job really costs.
* **The step that failed is a setup step**, not the suite step.
* **Nothing changed here that could reach it** -- the commit touched a
  document, or a platform the job does not run.

**What to do, in this order:**

1. **Name the step that failed**, not the job. `gh run view --job <id>
   --json steps` says which one. Setup step -> the machine. Suite step ->
   probably us.
2. **Wait for the whole run before reading the log.** GitHub releases a
   job's log only when the run is finished. Reading before that gets
   "still in progress", and re-asking costs rounds.
3. **The machine: start again as small as it goes, without a new
   commit.** Three sizes, and the smallest that fits is the right one:
   `gh run rerun <id> --job <job-id>` for one job -- a single hang, a
   single missing tool; `--failed` for the failed ones; the bare `rerun`
   for all six. All three keep the same commit, so the evidence still
   belongs to what will be tagged. **Never push a commit to trigger a
   retry** -- that changes the state the evidence is about, and it kills
   the run that was going to be it.
   **The one job green is not the release.** A rerun answers only for
   that job on that state. Once it is green, let the whole run go once
   more before the tag: six green on one state is the evidence, six green
   collected over four attempts is not.
   **And a rerun cannot carry a fix.** It repeats the same commit, so
   nothing you changed here is in it. Repaired code needs a push, and a
   push means a new run and the waiting that goes with it.
   **Which is exactly why the two causes want different tools.** Was it
   the machine? Then the rerun is the right instrument and the cheap one:
   the state was never at fault, so repeating it against the same commit
   is the whole repair. Was it us? Then a rerun answers nothing, however
   often it is asked. So decide the question above first, and the tool
   follows from the answer.
4. **Twice in a row on the same job is not the machine any more.** A
   flake repeats randomly; a fault repeats in the same place. Two reds in
   the same job and the same step: read it as ours and stop rerunning.
5. **Us: repair, then one push.** See the release skill -- one run per
   attempt.

**Write down which it was.** A red run put down to "GitHub" and never
looked at again is how a real fault survives for weeks. If it was the
machine, the line says which tool was missing and on which image; if it
was us, the red line goes into the counter-proof register where it
belongs.

## Before it counts as done

The pass before a red run is called explained.

1. Was the answer waited for -- `await_ci.sh` as a background command
   the harness holds -- rather than asked after?
2. Did the run it reports belong to HEAD, not to the push before?
3. Was the whole run finished before a log was read?
4. Is the step that failed named, not just the job? Setup step or suite
   step?
5. Machine or us: does the failure sort by platform or by runner image,
   and does the red line name a program or a judgement?
6. Language, snapshot, contention and deadline -- ruled out before
   anything was changed?
7. If the machine: was the smallest rerun used, and was no commit pushed
   to trigger it?
8. Was the same job red twice in the same step? Then it is ours, and the
   rerunning stops.
9. If reruns carried it: has one whole run gone green on one state
   before the tag?
10. If it was us: one repair, then one push, then the waiting again.
11. Is it written down which of the two it was -- the missing tool and
    its image, or the red line in the counter-proof register?
12. After a green run: `bash builder_times.sh`, and no dead rows left
    behind by a rename?
13. Does every workflow touched carry a `run-name:` of its own?
