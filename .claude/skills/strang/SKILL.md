---
name: strang
description: A task is about to touch more than one file, or more than two pieces that do not need each other, and nothing has been edited yet — how to cut the order for a strand so that what comes back is usable, and when to work alone instead.
---

# Cutting an order for a strand

Before the first edit, not after. Splitting a half-edited folder is not
a split; it is a merge by hand, waiting to happen.

## When to split

Two occasions, and either one is enough:

* The task edits **more than one file**.
* The task has **more than two pieces that do not need each other** —
  even inside one file.

## When not to, and the sentence that goes with it

Working alone is allowed. Saying nothing is not. **If you do not split,
write one sentence saying why.** Three reasons carry:

* one file,
* three lines,
* the second piece needs the first.

That sentence is the point of the rule. An exhortation gets skipped once
you are deep in a task; a sentence that has to be written does not.

## The split goes by file

**One file, one owner. Never two strands in one file.** Everything else
here hangs off that. Two strands in one file always end with somebody
merging their work by hand afterwards, and something is lost in the
merge.

**The order names both sides: which files the strand owns, and which
are somebody else's.** Name the foreign ones **by path**, not as
"everything else" — above all `videopodcast-magic.py` when another
strand is working in it. "Everything else" reads as a courtesy; a path
reads as a border.

## A foreign file: prepare, do not wait

**Whoever waits, loses.** If a file belongs to another strand, read it
now and write the change now, as pairs of verbatim old text and new
text, to be applied the moment the file comes free.

**Text anchors, never line numbers.** The first strand invalidates
every line number as it works.

**Every anchor has to match exactly once, and that is counted, not
eyeballed.** Put the anchor in a file of its own and ask:

```bash
python3 - <<'EOF'
anchor = open("anchor.txt").read()
print(open("<the foreign file>").read().count(anchor))   # must print 1
EOF
```

**Counted twice: when the pair is cut, and again the moment the file
comes free** -- the strand that owned it has been editing in between, and
an anchor that matched once an hour ago may match twice or not at all
now. Anything but 1 is cut again, never guessed at and never forced: an
editor that applies by proximity puts the lines silently beside the right
place, and nothing goes red.

**The real case is in `docs/notes/aufgaben.md`**, in the plan for the 29
remaining path places: two of the old lines occur **twice** in
`videopodcast-magic.py` and need the following line taken into the anchor
to be unique. That was found by counting. Seventeen replacements were cut
against that file; an uncounted anchor among them lands in the wrong
function.

## The order carries the rules it demands

**A name that must not stand in the repository must not stand in the
order either.** Measured on 2.9.2026: an order said "he saw it in the
real window", and the strand carried the name into the docstring of a
test to explain where the finding came from. It was doing its job. The
check for real names went red on all six builder jobs, while a full run
here had been green -- the run went before the file reached its final
shape.

**A strand reads its order as the standard.** Whoever writes "no real
name" into it and then puts one in the next paragraph has set two
standards, and the nearer one wins. So: the person who saw it is "it
was seen", the production is a role, the disc is `/tmp`. **In the order
as much as in the file.**

## What this machine cannot do

These belong in every order, because a strand that is not told will try
them and lose the time:

* **No `timeout`** and no `gtimeout`. A strand that needs a deadline
  builds it into the script it starts.
* **And when it has to wait for something it started itself, this is
  the shape** -- wait on the process, not on its name:

  ```bash
  nohup bash run.sh > /tmp/out.log 2>&1 &
  waiting=$!
  while kill -0 "$waiting" 2>/dev/null; do sleep 5; done
  ```

  **Not `pgrep -f`.** `pgrep -f` searches whole command lines, and the
  waiting line contains the name it is searching for -- **so the guard
  finds itself and waits for itself, for ever.** Measured on 2.9.2026:
  two of them stood for half an hour at no cost in processor and never
  ended, and the work they were waiting for had finished in two
  minutes. `pgrep -f` is for a process somebody else started, and even
  then the pattern must not appear in one's own line.

  Nothing cleverer than either of those two. A strand invented
  `until [ ! -e /proc/self ] && false; do :; done` -- there is no
  `/proc` on a Mac, so the condition is false for ever and `until`
  spins. Measured: **99,3 % of one core for seventeen minutes**, and
  the line it was waiting for never ran. Whoever writes a wait tries it
  once on something that finishes in a second.
* **Windows offscreen only.** Nothing may jump onto the screen.
* **Nothing is committed, nothing is pushed.** Not even "just to be
  safe".
* **Broken copies live in the scratch space**, never in the repository.
  That holds above all for the counter-proof; see the `gegenbeweis`
  skill.

## What the order has to ask back for

Three things. Without them a claim comes back instead of a result.

* **A counter-proof.** Every new or changed check has been seen red
  once, and the red line is in the report, word for word.
* **Measured or read — for every statement.** A line number looks like
  evidence and is not. The strand says, for each finding, whether it
  ran the thing or read it.
* **Report, do not repair.** Whatever the strand finds outside its own
  order, it reports and leaves alone. Otherwise one strand grows into
  another's file and the split is undone.

## The reversal: the brief is a signpost, not a source

**Tell the strand outright that the description it was given is a
guess, not a source.** It should measure and contradict where the
program says something other than the order does.

This is not a politeness. A strand that takes it seriously finds the
wrong threshold the whole order hangs on, before eight more strands
build on top of it. A strand that is not told builds the guess out
neatly.

## The template

To be filled in, not shortened. Any line left blank is a question that
comes back.

```
Order: <one sentence: what is different at the end>

You own:      <paths, absolute>
Not yours:    <paths, absolute, by name — including
               videopodcast-magic.py if somebody is working in it>
Prepare only: <a foreign file you deliver old-text/new-text pairs for
               instead of waiting. Text anchors, no line numbers; every
               anchor matches exactly once.>

Read first:   <file, section — what the rules say about this>

This machine: no timeout, windows offscreen only, nothing committed,
              nothing pushed, broken copies in scratch space only.

Send back:
  - what you changed, one sentence per file
  - the counter-proof: the red line word for word
  - for every finding: measured or read
  - what you found outside this order — reported, not repaired

The description above is a signpost, not a source. Measure, and
contradict it if the program says otherwise.
```

## Bringing the strands back in

**Prepared edits go in the moment the file comes free** — and an anchor
that now matches twice or not at all is cut again, never forced.

**A contradiction from a strand is handled first.** It is the most
expensive finding if it is right, and the cheapest if it arrives early.

**A finding reported from outside an order does not go away by
itself.** It goes into `docs/notes/`, or it becomes a strand of its
own. A finding nobody writes down has been found twice and kept once
too few.

## Working on a skill itself

**The body is read fresh every time it is called.** Write, call, look,
write again -- an edit costs nothing and shows at once.

**The `description` line is not.** It is taken when the session starts,
and it is the only part loaded into every session -- so it is what
decides whether a skill is found at the right moment. A new skill, or a
changed description, needs the session restarted once before anybody can
call it. Measured: nine skills written in one session stayed documents
for the rest of it, and their bodies were readable the whole time --
nobody could find them.
