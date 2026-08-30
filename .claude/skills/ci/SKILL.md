---
name: ci
description: A commit has just been pushed, or a run on the builder is being waited for, or one has come back red. Six machines answer in four minutes and nothing here says when -- so the answer has to be waited for rather than asked after.
---

# The builder's answer

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
  answers 143 there and 145 here.
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
come back at 950 and at 1091 seconds. Two runs, or a steadier machine,
before a number means anything.

## After a green run, the queue

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
