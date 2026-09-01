---
name: changelog
description: A section of CHANGELOG.md is to be written or changed -- a new version is due, a point has to be added, or somebody has to decide whether a change belongs in it at all.
---

# A section of the changelog

`CHANGELOG.md` is not a list of the work. It is what a stranger reads
who uses the program and wants to know what this version does
differently for them. The release text on GitHub is that same section,
not a summary of it.

## Both languages, in one section

**Every version says everything twice.** The English part first, then a
line reading `**Deutsch**`, then the same in German. Both halves go on
the release page, where anybody can jump to their own language; the
program shows only the one it is running in.

**Both halves hold the same number of points.** A point that stands on
one side and is missing on the other is a fault, not brevity. And
neither half carries words of the other language.

**The German half is not a translation of the English one. It is the
same point thought in German.** A point carried over sentence by
sentence reads as a translation, and it loses the places where German
groups things differently. Write the point again, in German, and let it
stand on its own.

## The groups

The version heading: `## [number] - YYYY-MM-DD`, newest at the top.

Under it the groups, **in this order**:

Added, Changed, Deprecated, Removed, Fixed, Security, Tests,
Documentation.

The everyday case is six of them: **Added, Changed, Removed, Fixed,
Tests, Documentation.** Deprecated and Security are allowed and keep
the place Keep a Changelog gives them. Tests and Documentation come at
the end, Documentation last: whoever reads the section wants to know
first what the program does differently.

**Each group at most once per version.** Two blocks headed Fixed are
two lists, and nobody reads them as one.

**The heading is the bare word.** No topic, no addition. The topic
belongs in the first sentence of the point.

## Who it is written for

**For somebody who was not there.** A point tells a stranger three
things: what the thing is, what changed about it, and why that matters
to them. Short comes after that.

**A point that only makes sense with the commit beside it is not a
point.** That is the common failure: written by somebody who watched it
being built and therefore no longer misses the half-sentence that is
gone.

## The shape of a point

* **Name the thing as it stands on the screen**, in quotation marks, so
  the reader can find it.
* **What it was, what it is now, what follows for them.** In that
  order, and rarely more than three sentences.
* **One point says one thing.** A second fact gets a point of its own,
  or none.
* **Do not justify the old state.** Why it was wrong belongs in the
  commit message, where whoever wants the reasoning will look.
* No allusion to the day's work, no idiom that only carries with the
  commit beside it, and the sentence has to parse for a native reader.
* **Where a measurement is the point, the number goes in** -- a number
  is understood without context. Where it is not, leave it out.

## Under Fixed, half a point is not a point

What was wrong is the first half. The reader needs the second: **what
happens now.** In German it is usually the word "jetzt" that carries
it. The German half of such a point:

```
- Die Schalter „−", „+" und „▭" unter dem Schnittband rückten beim
  ersten Druck um 104 Pixel weiter, der zweite Druck traf daneben. Die
  Anzeige daneben wird jetzt auf ihrer größten Breite gehalten, und die
  Schalter bleiben stehen.
```

Without the second sentence that would be a bug report, not news.

## What does not go in at all

**Editorial tidying.** A word changed in the interface for its own sake
is not something anybody has to read about. One that was struck out:
"The German texts say Version where they said Fassung."

**Findings from measuring that changed nothing.** A test showing the
other path would have been fine just as well changes nothing for
anybody. It belongs in the notes.

**Everything that only concerns the workshop.** A renamed or new test,
a guideline, a comment, a function name, a passage that was tidied up.
Somebody using the program notices none of it.

The groups Tests and Documentation are not the exception to that. They
are there for what a user really does notice: a check that will catch a
fault they would otherwise have had; a chapter that did not exist
before.

**When in doubt, leave it out.** A section of six points that all say
something is worth more than one of twenty in which they drown.

## What the machine checks

`tests/text_release_ready_test.py` checks what can be checked
mechanically:

* that the version number is the same in the program, in the changelog
  and in both READMEs;
* that the newest three sections carry only groups that are allowed,
  each once, in the right order with Documentation last;
* that the newest version has both halves and that both hold the same
  number of points;
* that no German function word stands on the English side and no
  English one on the German side;
* that no point stands out by its length -- measured against the middle
  of the section itself, half again as long as that, with a floor.

The length is measured against the middle rather than against a number
written down, because a number goes stale the moment the style moves
and the middle of what was just written does not.

## The read-back, and it is a step, not a good intention

**Before the section is finished, read every point once more as somebody
who was not there -- and the hard part is the "not there".** Whoever
just made the measurement cannot un-know it: 3.5 and 5.3 are then two
familiar quantities, not two similar numbers. So the read-back is not
done from memory. **Put the measurement away and read the point out of
the file**, or better out of the rendered release page, where it stands
without anything of yours around it. If a number's meaning has to be
supplied from your own head to make the sentence work, the sentence is
missing it.

**Read every point once more as somebody who was not there.** Not the whole section -- one point at a time, out of
its neighbours, the way a reader meets it in a release list. The skill
says elsewhere that an exhortation gets skipped; so this is a list of
questions with answers, and a point that fails one is rewritten.

1. **Two numbers in one point: can they be mistaken for each other?**
   This is the one that got through on 1.9.2026: "a speaker on 3.5 %" and
   "it is 5.3 % now" stood in one sentence, one a share of speaking time
   and the other a share of misplaced speech. Sebastian had to ask what
   it meant. **Where two numbers in a point measure different things,
   one of them goes** -- into a second point, or out. Where both must
   stay, say them in different units: half against a twentieth reads at
   a glance, 50 % against 5.3 % does not.
2. **Does a number in it need the setup to make sense?** A share of a
   test that is not described is noise. Either the setup goes in, or the
   number does not.
3. **Read the first sentence alone.** If it does not say which thing
   changed, no later sentence rescues it.
4. **Under Fixed: is the second half there** -- what happens now, not
   only what was wrong?
5. **Is there a word in it only somebody who built it would use?**
6. **Would a stranger have to open the commit to understand it?**

**The German half is read again on its own, not against the English
one.** A point carried over reads as a translation, and a number that
was clear in English can collide in German, where the sentence is
longer and the two figures end up closer together.

## What only a person sees

Whether the point reaches a stranger. Whether it says one thing instead
of two. Whether the second half is there under Fixed. Whether it names
the thing by the name it carries on the screen. **And whether it
belongs in there at all.**

A green test does not mean the section is finished. It means nothing is
in the way of reading it.
