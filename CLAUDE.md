# videopodcast-magic

Raw material from a video podcast becomes an edited episode: the good
audio inside the video files, the cameras on one time axis, a first cut
by speaker, and a DaVinci Resolve project.

One file, `videopodcast-magic.py`, about 30000 lines. No package, no
build step.

`README.md` is the short version. `docs/` holds the manual: one file per
chapter, English as `docs/name.md` and German as `docs/name.de.md`.
Changing a chapter means changing both, or `text_no_german_left_test.py` turns
red. The test checks that every chapter has both languages and that no
German word stands in an English one.

## Running the tests

```bash
cd tests && bash run.sh          # all of them, several at a time
WORKERS=1 bash run.sh            # one after another, easier to read
VPM_PYTHON=/usr/bin/python3 bash run.sh    # a different interpreter
```

A test is green when it returns 0 and prints neither a traceback nor
`FAIL`. `source_limits_hold_test.py`, `text_only_texts_change_test.py` and `source_no_loose_ends_test.py`
are ratchets: their counts may fall, never rise. Do not delete
`tests/state/`.

A full run takes a couple of minutes. Copy the script to a snapshot,
start the suite against that, and do the next thing:

```bash
cp videopodcast-magic.py /tmp/snap/vpm_sNN.py
(VPM_SCRIPT=/tmp/snap/vpm_sNN.py nohup bash run.sh > /tmp/suiteNN.log 2>&1 &)
```

## What a release is

A version is not a tag. Five things belong to it, and the tag comes
last:

1. **The tests are green on all six builder jobs.** Evidence before the
   mark: a tag whose attachment does not match what was tested is worse
   than no tag.
2. **`CHANGELOG.md` says what changed**, in the groups Keep a Changelog
   wants and in their order -- Added, Changed, Removed, Fixed, Tests,
   Documentation. The release notes are cut from that section.

   **Written for somebody who was not there.** Every version says
   everything twice: the English part first, then a line reading
   `**Deutsch**`, then the same in German. Both go on the release page,
   where anybody can jump to their language; the program shows only the
   one it is running in.

   A point has to say three things to a stranger: what the thing is,
   what changed about it, and why that matters to them. Short is
   second. Sebastian, 31.8.2026, on "The ranking of who asks becomes
   names to propose -- Guest, Host, Host 1 to n -- and only ever over a
   name the program made up itself": *"Is that actually good English?
   And does a third party understand what this is about?"* It is not,
   and they do not. It was written for somebody who had watched it
   being built.

   **The shape of a point**, taken from a rewrite Sebastian did of one
   of mine on 31.8.2026, five lines cut to three:

   * Name the thing as it stands on the screen, in quotation marks, so
     a reader can find it.
   * What it was, what it is now, what follows for them. In that order,
     and rarely more than three sentences.
   * One point says one thing. A second fact gets a point of its own,
     or none.
   * No justifying the old state. Why it was wrong belongs in the
     commit message, where whoever wants the reasoning will look.

   And: no allusions to the day's work, no idiom that only makes sense
   with the commit beside it, and the sentence has to parse for a
   native reader. Where a measurement is the point, the number goes in
   -- a number is understood without context. Where it is not, leave it
   out.

   **What does not go in at all**, from Sebastian's reading of a draft
   on 30.8.2026:

   * **Editorial tidying.** A word changed in the interface for its own
     sake is not something anybody has to read about. His example, and
     it was struck out: *"The German texts say Version where they said
     Fassung."*
   * **Findings from measuring.** A test that showed the other path was
     fine changed nothing for anybody. It belongs in the notes, not
     here. His words: *"That sort of thing does not go in the
     changelog, does it?"*

   **Under Fixed, half a point is not a point.** Both of the ones he
   struck said what had been wrong and stopped there. A reader needs
   the second half -- what happens now -- and in German it is usually
   the word "jetzt" that carries it. `text_release_ready_test.py` checks for it.

   `text_release_ready_test.py` checks what a machine can: that both halves are
   there, that they hold the same number of points, that neither is
   written in the other's language, and that no point stands out by its
   length. The last one measures against the middle of the section
   itself -- half again as long as that, with a floor -- rather than
   against a number written down, because a number goes stale the
   moment the style moves and the middle of what was just written does
   not.
3. **The manual is true again.** Anything a person can see or feel is a
   chapter, in both languages. A default that moved, a new answer in a
   field, a computation that costs their processor: all of that.

   **And what writing it turns up becomes a test.** Writing the manual
   is the one pass that reads the program as a user, and it finds what
   the tests do not: a switch that is taken and does nothing, a track
   that used to be in the file and is not, a message naming a mode
   nobody asked for. Every such finding gets a test before the tag.
   Where the test is genuinely larger than the fix, it goes into
   `docs/notes/aufgaben.md` with its shape written out, and it is the
   first thing in the next round -- not a note saying "test this".

   Sebastian asked for this on 30.8.2026, after seven manual chapters
   turned up five faults that 118 green tests had passed over, one of
   them a function the merge had silently removed.
4. **The pictures show the program as it is now.** `docs/notes/` says
   how they are taken. Not every release moves them; a release that
   changed the window does.
5. **The list and the issue are brought up to date** -- `docs/notes/`
   for what is open, and the roadmap issue for whoever reads from
   outside.

Sebastian asked for this to be written down on 31.8.2026, after the
fourth release in two days where the manual and the list were caught up
afterwards rather than as part of the work.

**Every workflow says what it is, in the same shape every time.** GitHub
names a run after the commit subject unless it is told otherwise, so a
list of runs reads as a heap of unrelated sentences and nothing can be
found in it. Each workflow carries a `run-name:` of its own -- what it
is, and the number the list is ordered by. A new workflow without one is
not finished.

**Before every release, fetch the builder's times and look at them.**

```bash
cd tests && bash builder_times.sh      # the newest green run on main
```

The suite runs the long tests first so nobody waits, and it takes the
order from `tests/state/longest`. This Mac must not decide that order:
it has cores to spare and finishes in half a minute, while the builder
takes two to four minutes, and the two disagree badly. `sound_bleed_reported` was
four seconds here and 118 on the builder -- thirtieth in the queue, and
the longest test there was.

So the order comes from one machine, the slowest of the six -- and
**which one that is, the script asks the run.** It was
`windows-latest / py3.10` for weeks and then it was not: the macOS
runners went from the middle of the field to twice the slowest of the
others, and a queue ordered by yesterday's slowest machine orders
nothing. The script says which job it took and how long that job ran.

It writes its numbers into `state/longest`, replacing what stood there,
and prints the ten that will go first. Read those ten and ask whether
the top two or three can be made cheaper; that is where a minute of the
builder's time is. What was made faster shows up in the next run's
numbers, which is the point of replacing rather than only ever rising.

**What you wait for is the longest job, not the sum.** The six run side
by side. The sum is what the builder is billed; the longest is what
stands between a push and an answer, and it is the number to watch.

**And read the same commit twice before believing a jump.** The macOS
runners have come back 950 and 1091 seconds on identical code, and once
651 against 1088 -- so a single reading says almost nothing there. Two
runs of one commit, or a steadier machine, or both.

## The rules that are not negotiable

**The Auphonic API key never goes into a file, a script, a document or a
command line.** It lives in the macOS Keychain or the Windows Registry.
Inside the program it reaches curl through a temporary config file with
mode 0600, so it is never in the process list. The project file strips
`--auphonic-api-key`.

**The program never uploads to auphonic.com on its own.** Only when
somebody asked for it.

**English in the source, German from the catalogue.** Every user-visible
string goes through `T()`; the German lives in `CATALOGUE["de"]` at the
end of the file. Changing a string means changing both sides, or
`text_no_german_left_test.py` turns red.

**Measure, do not guess.** If a number is needed, it gets measured. What
was measured goes into the log. Third-party names are asked for at run
time, never written into the code.

`development/coding_guidelines.md` says how the code is written, and why.
`CHANGELOG.md` says what changed in each version, from 0.1.0.

## How to work here

**Parallelise, and account for it.** Before the first edit of any task
that touches more than one file, split the work by file and start the
strands. The same before the first edit of any task that has more than
two pieces which do not depend on each other. One file, one strand,
never two strands in one file. Say which file each one owns.

Working alone is allowed. Saying nothing is not: **if you do not split,
write one sentence saying why** ("one file", "three lines", "the second
piece needs the first"). That sentence is the point of the rule. An
exhortation to parallelise gets skipped once you are deep in a task; a
sentence that has to be written does not.

**A file another strand owns is not a reason to wait. Prepare instead.**
The second strand reads that file now and lays down its changes as
verbatim old-text/new-text pairs -- never line numbers, which the first
strand invalidates as it works -- and they are applied the moment the
file comes free. Every pair has to match exactly once in the file as it
stands; a pair that matches twice or not at all is thrown away, not
guessed at. What must not happen is two strands editing one file and
their work being merged by hand afterwards.

Say what was measured and what was assumed. Never claim a test passed
without running it.

**Every check owes a counter-proof, and it is written down.** A check
that has never been seen red is not known to check anything -- in one
day seventeen were found that had been green for months while testing
nothing, and two more where the fault was in the stand-in rather than
the check. So: break the thing the check is about, run it, and keep the
red line verbatim. `tests/state/counterproof` holds one entry per test;
`counterproof_test.py` is a ratchet over the tests still missing one,
and that number may fall, never rise. **No change to a test and no new
test is finished until its entry is in that file.**

And when a counter-proof will not go red, ask which of the two is at
fault: the check, or the stand-in it runs against. A stand-in that
allows more than the real thing makes every check above it worthless,
and everything stays green while it does.

`development/test_guidelines.md` says how a test is built, named,
documented and counter-proved, and carries the checklist to run through.

Explain a change in plain words, not in terms of the code: what it does
and why. **Short**, in a commit message as in a comment: a heading and a
handful of lines, a list where several things changed. The road that led
there goes in `docs/notes/`, not into the message.

## The working notes are not in this repository

Everything about who works on what, what is still open and what has been
decided lives in `docs/notes/`. That folder is deliberately not shipped:
it holds material from real productions. If you have it on disk, **read
`docs/notes/claude_intern.md` first**. It is the counterpart to this
file and names the rest. If you do not have it, this file is complete on
its own; nothing here depends on it.
