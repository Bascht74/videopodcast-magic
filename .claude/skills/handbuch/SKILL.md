---
name: handbuch
description: Something a user can see or feel has changed in the program and the manual under docs/ still describes the old state -- or a chapter is to be written, checked, or brought up to date in the other language.
when: something a user can see has changed and `docs/` still says the old thing
tables: claude, contributing, agents, pr
order: 90
---

# The manual

`docs/` holds it, one chapter per file: English as `docs/<name>.md`,
German as `docs/<name>.de.md`.

**Changing a chapter means changing both.** Otherwise
`text_no_german_left_test.py` turns red. The test asks two things: that
every chapter stands in both languages, and that no German word is left
standing in an English one.

## The pass that finds what no test finds

**Writing the manual is the one pass that reads the program as a user.**
Not as source, not as a test case -- as somebody who opens the window
and wants to get something done. That is why it finds what no suite
finds:

* a switch that is taken and does nothing,
* a message naming a state that does not exist,
* a track that used to be in the file and is not any more.

Seven chapters once turned up five faults that 118 green tests had
passed over. One of them was a function a merge had silently removed.

**So write down what does not add up, as you go** -- and somewhere it
will be found again. A chapter that phrases its way around a discrepancy
has thrown the finding away.

**Every chapter read leaves one line, and "nothing" is one of the
answers:**

```
<chapter>   read <date>   text: <fixed / nothing>   program: <what does
                          not add up, or nothing>
```

Into `docs/notes/aufgaben.md`, or into the release report where the notes
are not on disc. **A pass that reports "the chapters are up to date" and
names no chapter has not been made.**

**The two halves of that line are counted apart on purpose**, because
pulling the text straight is not fixing the program and the two get
confused at exactly this point. **The real case: the pass of 31.8.2026
found two.** The log has three headings where the chapter said two --
wrong for thirteen versions -- and the greyed-out fields under "no camera
is free of speakers" do something other than what the notice under them
says. The text was pulled straight, the program was not, and both still
stand in `docs/notes/aufgaben.md` under "Zwei Befunde aus dem
Handbuchgang, nicht repariert". By the rule below each owed a test before
the tag; three tags have gone out since (v2.25.0-beta, v2.25.1-beta,
v2.26.0-beta, all 1.9.2026).

## Every finding becomes a test, before the tag

Not afterwards, not "some time". What the pass uncovered stands in the
suite as a test before the mark is set.

**Where the test is genuinely larger than the fix**, it goes into
`docs/notes/aufgaben.md`, and it goes in **with its shape written out**:

* what is set up -- the state the check runs against,
* what is checked -- the one sentence that has to be true,
* what has to be broken for it to go red.

It is then the first thing in the next round. **A note saying "test
this" is not an entry.** It costs the next pass the same work over
again, minus the head that made the finding.

## Report rather than repair

Where the finding lies outside your own errand -- in the program, in
somebody else's chapter, in a picture -- **report it, do not fix it in
passing**.

Patching the program while writing a chapter delivers a change nobody
asked for and nobody reviewed, inside a strand that is about text.

## What earns a chapter

**Anything a person can see or feel**: a default that moved, a new
answer in a field, a computation that costs their processor and makes
them wait.

**The German chapter is not a translation. It is the same content
thought in German.** The German sentence is the longer one, and a
sentence that only carries English word order is not a German sentence.
Carrying the English chapter over line by line yields German that reads
as translation, and it loses every place where German would have built
the thought differently.

## How it is written

* **No function names, no dates, no names of people.** The reader has no
  source in front of them and was not there.
* **Name things with the words that stand on the screen** -- in German,
  the German ones. Where the German window says "Trockenlauf", the
  German chapter says "Trockenlauf", not "Dry run".
* **What the reader can do, in the order they do it.** A chapter follows
  the handgrip, not the layout of the program.
