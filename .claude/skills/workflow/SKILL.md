---
name: workflow
description: A task is wide enough that several agents should work on it at once -- an audit across many files, a sweep for one class of fault, a question where an answer has to be refuted before it is believed. How the script is cut so it runs fast and comes back trustworthy.
when: a task is wide enough for several agents at once
tables: claude, contributing, agents
order: 110
---

# Orchestrating a workflow

A workflow is worth it for three things and nothing else: **to be
thorough** (fan out and cover), **to be sure** (independent finders, then
refuters), and **to reach further than one context holds** (a sweep over
a file too big to read at once, an audit across every test there is).

It is not worth it to be fast. A single edit with a known cause is
faster by hand, and a workflow around it is ceremony.

## Scout first, then fan out

Find the work-list yourself, cheaply, before writing the script: list the
files, grep for the shape, read the failing line. Then hand the list to
the workflow. A workflow that has to discover its own scope spends its
first round doing what one `grep` would have done.

## The chain, not the barrier

**This is the mistake that costs the most, and it is easy to make.**

`parallel()` is a barrier: nothing in the next stage starts until
everything in this one has come back. `pipeline()` lets each item run
its whole chain on its own — item A can be at the refuting stage while
item D is still being read.

```js
// wrong: no refuter starts until the slowest sweep is back
const found = await parallel(SWEEPS.map(s => () => agent(s.prompt, {schema: F})))
const checked = await parallel(found.flat().map(f => () => agent(refute(f))))

// right: each finding is refuted the moment it exists
const checked = await pipeline(SWEEPS,
  s => agent(s.prompt, {phase: 'Sweep', schema: F}),
  r => parallel(r.findings.map(f => () => agent(refute(f), {phase: 'Verify'}))))
```

A barrier is right in exactly one case: **the next stage needs all of
the previous one at once** — deduplicating across every finding, or
stopping early when the count is nought. "I have to flatten the list
first" is not that case; flatten inside a stage.

## Effort by stage, not by workflow

Mechanical stages -- grep for a shape, read and report -- take
`effort: 'low'`. The stages where something is decided or refuted take
`'high'`. One tier for the whole workflow wastes time at one end and
quality at the other.

## What a workflow is not slower at

Measured, one task, identical output down to the byte: an agent in the
background wrote 200 generated lines in **21 seconds**; the same work in
the main conversation took about **50**. Nothing is throttled.

Where a workflow *feels* slow, it is doing more: an agent that reads a
36000-line file before writing a word has earned its minute. And the
progress display only moves when an agent finishes, so twelve agents
thinking look like nothing happening.

The concurrency cap is `min(16, cores - 2)` per workflow — on a machine
with fourteen cores, twelve at once. Passing more items than that is
fine; they queue.

## Refuting is the point

A finder that reports and nobody checks is a finder that reports
plausible things. **Every finding goes to an agent whose job is to prove
it wrong**, and that agent is told to reject when unsure.

```js
agent(`**Your job is to REFUTE this.** Assume it is wrong until the file
says otherwise. Go to the line, read the callers, measure. Reject it
when the line numbers do not show what is claimed, when another finding
covers it better, or when it is true and harmless. Default to
refuted when you are unsure.`, {schema: VERDICT, effort: 'high'})
```

Ask for the rejections too, with their reasons. A rejection is worth as
much as a confirmation: it says where the finders are being careless.

**And add one agent whose only task is to ask what everyone missed.**
Give it the others' findings so it does not repeat them, and send it at
the sources they did not read -- the git history, the workflow files,
the notes that ship with nothing.

## The schema is the interface

Ask for structured output. A `schema` forces the agent through a
validating tool call, so a mismatch is retried instead of parsed. Make
the fields say what you will do with them: a `severity` the reader can
sort by, an `evidence` field that has to hold what was measured, a
`kind` from a fixed list. **A field called `evidence` that is allowed to
hold a suspicion produces suspicions.**

## What the prompt has to carry

Each agent starts with nothing. Every prompt says, in this order:

* **Where it is** and that it reads only -- no commit, no push.
* **What is already known**, including what went wrong before. An agent
  that knows a rule was once lost between two files looks for that.
* **That your description is a signpost, not a source.** Say it in those
  words and ask to be contradicted. It is where the best findings come
  from -- three times in one day a strand overturned the premise it was
  given, and each time that was worth more than the task.
* **The limits of this machine**: no `timeout`, windows only offscreen,
  broken copies into scratch space and never into the repository.
* **Measured against read.** Ask for the two apart, in the report. A line
  number looks like evidence and is not one.

## One file, one owner

The project rule holds inside a workflow: **one file, one agent, never
two agents in one file.** Say in each prompt which files that agent owns
and which are somebody else's, by name. Where two would collide,
`isolation: 'worktree'` gives an agent its own copy — expensive, so only
where they really write at once.

## Say what was dropped

If the script bounds anything — the top ten, no retry, a sample —
`log()` it. A silent cap reads afterwards as complete coverage.
