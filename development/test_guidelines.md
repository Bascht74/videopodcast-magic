# Test guidelines

For `tests/`. These grew out of this suite. What is written here either
proved right while building it, or was learned by getting it wrong.

**This file says why the rules are what they are. It does not say how to
follow them.** Three skills do that, and they hold the commands, the
order of the steps and the list that is ticked off at the end:

- `test-neu` — writing or changing a check.
- `gegenbeweis` — showing that a check goes red when the thing it is
  about is broken, and writing that proof into the register.
- `test-rot` — a test that is red, wobbling, or green and not to be
  trusted.

Whoever is about to write a test reads the skill. Whoever wants to know
why the tests here look the way they do reads this.

**Where these rules come from, as a pattern.** Reading every test
heading in one pass turned up seventeen tests that checked less than
their heading promised. Not one of them was red. Reading found them, the
suite did not — and that is the standard everything below is held to: **a
rule is worth having only if it bites while a test is being written, not
when somebody happens to read it again.**

This suite has no framework, no classes, no test library. A test is a
script that prints one judgement per line and sets an exit code. What is
taken from the literature is taken because it fits that shape; what does
not fit is in section 9, with the reason. Section 10 names the sources.

---

## 1. A test that asserts nothing is not a test

If it calls a function, prints the result and ends, then green there
means "did not crash" — and from outside that looks exactly like a test
that passed. Every other fault in this file follows from that one.

The literature files it under the self-validating property, the S of
FIRST: *"Tests are pass-fail. No agency must examine the results to
determine if they are valid and reasonable."* A test without an
assertion escapes that distinction; the catalogue of test smells calls
it the test that never fails — *"If a test won't fail even when the code
to implement the functionality doesn't exist, how useful is it?"*

And it is not rare. Across 656 open-source Android projects, nearly half
carried at least one test with no assertion at all, and one test file in
three. Asked about them, the authors called them oversights throughout.
It is the commonest way for a suite to grow without checking more.

**The judgement is printed, never asserted.** A bare `assert` throws a
traceback instead of a readable line, carries no numbers, and ends the
run at the first failure, so a test with four faults reports one and
conceals three. Above all nothing is counted — and without a count
nobody notices a test that passes no judgement at all.

**The printed count is the second safeguard.** It stands there in every
run. Whoever reads it sees a zero, and sees three where the heading
promises twelve. No assertion finds that; a number beside an expectation
finds it at a glance.

**Every path through a test has to pass the line that counts.** A test
whose assertions sat in one branch of a timer chain, while a second
timer ended the program on a deadline of its own, exited 0 although it
had crashed at the first step. It passed for months.

**Set the situation up once, then ask it many questions.** Arrange-Act-
Assert wants one action per test, and its strictest reading one
assertion per test. That is written for tests costing milliseconds; here
the situation costs an ffmpeg run. So it is built once and questioned
twenty times — but every question with its own name on its own line,
which is the separation AAA is actually after. That is no special
pleading: whoever named the pattern does not keep to the single
assertion either, and the common softening is not one assertion per test
but **one concept per test**. The boundary is not the number of checks,
it is the point where a test claims two different things. Then it is two
tests.

**No logic in a test.** A loop that computes the expectation usually
computes it as wrongly as the program does.

**A test that can genuinely only catch a crash says so** in its heading
and in its closing line, and claims no count it does not have. Three
here are of that kind and stay: what they build can only be judged by
another program. That is an exception with a reason, not a pattern.

## 2. The docstring is the contract

**Its first line says what holds when the test is green** — not what the
test does. One sentence about the program, so that from it alone one
could decide whether a red run is any of one's business.

**Whatever stands in the heading has a check, and whatever a check tests
stands in the heading.** Both directions. A heading that promises more
than the test holds has a name in the literature: the liar — *"a test
that runs, but does not test what it claims to test … Liars give a false
sense of security."* Both directions get broken here. One test ended on
"colour tags and camera audio came through" and checked exactly one
colour tag. Another checked the rejections in all twelve of its sections
while its heading asked only about the result that was built. The second
is the milder case and still a fault: what the heading does not mention
is what the next rebuild clears away.

**The heading is reread on every change.** One that describes a set-up
the test stopped building two rebuilds ago sends every reader in the
wrong direction, and it is the likeliest reason a hole goes unnoticed
for years.

**No number in a heading that would have to travel with the code.** Six
things over seven blocks, a block numbered 8 twice and none 9, a stage
number out of last week's plan. A number in a heading is a second place
that wants maintaining, and it always loses.

**A note saying a step is red goes out with the repair**, not in the
next clean-up. Otherwise the sentence is untrue the moment it is
written, and stays untrue. Whoever comes next believes it and leaves a
working check alone.

## 3. The name is a claim

**The prefix says where the fault would sit, not what the material is
about.** That is the rule which settles every borderline case. A test
about channels whose failure would show in the table belongs under
`table_`, however much sound it is made of. A name taken from the
material — from the recording, from the path, from the folder — forces
everyone who sees the red line to open the file before they know which
part of the program is broken.

**The second half is a claim, not a thing:** `atom_travels`, not
`log_atom`. A thing in the name leaves open what is supposed to hold,
and so covers every check that has anything to do with that thing —
including one that measures something else entirely. That is how a
heading comes about promising "shows the cut correctly" while what is
mostly counted is pixel colours.

**The cap is what forces the claim to be one claim.** After the prefix,
two or three words are left. Whoever cannot get the claim into three
words is usually claiming two things; then the test is split, and the
name is not shortened back to a thing.

**The same holds for every single check.** Its name is the sentence that
lands in the report, and it is read when nothing else is left.

### The known objections

A rule with its objections beside it lasts longer than one that pretends
there are none. Of the parts of this scheme, two are unattested and one
is contested.

**The file carries twenty claims and is named after one.** There is no
literature on this: everything written assumes the file is named after
its subject and the claims live in the names of the individual checks.
The one source that governs file names at all names them by area and
sub-area — after a thing. Our scheme lifts the claim one level up. That
is unattested, and also uncontradicted.

**The risk is that nineteen claims are invisible in the name.** The
countermeasure is section 2 and the checklist point that enforces it:
the heading carries them all, checked in both directions. Without that
point the scheme would be dangerous, because it makes the name a promise
about the file of which the file keeps a twentieth.

**The scenario is missing from the name.** The common schemes have three
parts — subject, scenario, expectation — ours has two, and the scenario
stands in the heading below. The loss is spelled out in the literature:
the name is often the only thing visible in a failure report, and one
has to be able to understand what is broken **without reading the test's
source.**

**The answer is where our failure report begins.** What is visible there
is not the file name but the check line that fell, and that carries
scenario and expectation because section 4 demands it. The demand is
met, one level lower than it was meant. Besides, a file with twenty
scenarios cannot name one without concealing the other nineteen. What
the literature backs without reservation is brevity, and the character
cap is the best-attested rule of the whole scheme.

**Twelve prefixes by part of the program: the sources are split.** One
side warns against ordering tests by the structure of the program — test
behaviour, not source, and a one-to-one mirror ties the tests to the
build. The other side orders explicitly by area of the program, with our
intention exactly: find a test quickly, place a failure quickly. What
makes both compatible is that **a coarse area is not a mirror.** Twelve
prefixes over a hundred and forty tests reproduce no part of the
program; they make a register.

**The literature gives no number for too coarse or too fine.** The
usable test is a different one: **does every prefix actually separate?**
A prefix with one member is not a category, one with sixty is not
information. By that measure twelve is well chosen: before the rename
the tests carried ninety-two different first words, which is no
classification at all. If one prefix grows past a quarter of the stock,
or shrinks to a single test, the classification is redrawn — the test is
not bent to fit.

**And a word every name carries separates nothing.** An earlier form of
this scheme put `check` between the two halves, to force the reader to
take what followed as a statement. Four sources argue against a filler
word common to all names and none for it, and it cost a fifth of the
character budget. It is gone. The objections had been written down
before it went, which is why they were there to decide the question.

## 4. The failure line has to carry its evidence

**On somebody else's machine, only what stands in the line itself
exists.** Six builder jobs, and out of a test's whole output the report
picks the lines that look like a failure. Everything printed before is
gone, and whoever needs the number beside it has to repeat the run on a
machine they do not have. That is the property the rest of this section
hangs from: **a failure has to make you able to act.** *"When a test
fails, you should be able to begin investigation with nothing more than
the test's name and its failure messages — no need to add more
information and rerun the test."*

**Numbers, not adjectives.** "Too short" says nothing anybody can
recompute. "0.31 s against 0.80 s" says everything.

That is the answer to a smell with a name of its own, assertion
roulette: several assertions of the same kind in one test, and the red
message does not say which one fell. The rule against it names the case
where it counts most — a test run on the command line, where no
development environment highlights the line that failed. That is our
situation in every run.

And it is rarely followed. Across twenty open-source projects about five
percent of assertions carried a message at all, while in a survey six
developers in ten said they always or very often supplied one. It is not
something one does by oneself. It is something that has to stand on a
list.

**And it has to name the right fault.** One line claimed the camera had
not changed when in truth the player had never started. Where a claim
rests on a precondition, the precondition becomes a check of its own and
comes first, so that the red line names the first thing that was untrue
rather than the last.

## 5. Green proves nothing until the check has been seen red

**This is the most important section of this file.**

**A check nobody can make fail is worth nothing.** Twelve checks here
could not fall at all: one compared a call with itself, one was
satisfied as soon as a word appeared anywhere in the source, one looped
over a list that could never fill, one asserted the same thing twice,
one asked whether a key began with a prefix instead of which one, one
passed at zero. All twelve were green for years, and no suite in the
world would have reported it.

**What only the counter-proof catches.** One check looked for the word
*offset* in everything printed. It was always green, because the program
prints its own absolute path and the working folder was named that. No
reading finds that, no ratchet, no coverage figure: the line runs, the
condition is true, everything looks right. A broken copy in which the
word is never printed finds it on the first attempt.

**Broken means exactly one thing, and small.** Take the program apart
wholesale and everything goes red and nothing has been learned about
this check. The mutation-testing work measured that test data catching
the small deviations catches over 99 percent of the compound ones as
well, so an elaborately staged, lifelike fault buys nothing that a
turned-round sign does not. And if other checks that should have caught
the same fault stay green, that is a second finding.

### The stand-in

**When the counter-proof will not go red, the first question is: the
check, or the stand-in?** Whoever does not ask it takes a generous
stand-in for a check that passed.

**A stand-in that allows more than the real thing makes every check
above it worthless — invisibly, because everything stays green.** In
every point the check touches it has to be at least as strict as the
thing it stands for: refuse what that refuses, and have the methods
whose absence that would make felt. Both halves have occurred here. A
stand-in media pool invented every track it was asked for, so the check
"only one video track was made" was green while things sat on tracks
that did not exist — the real thing refuses that silently, which is
exactly why the program clears space first. And a stand-in timeline had
no way to delete a track, so the function that removes empty ones ran
into a swallowed exception and ten empty tracks survived every run.

**A swallowed `except` in the stand-in is the dangerous case**, because
then not even a traceback appears: the program asks for something the
stand-in does not have, and the test sees none of it.

**So the counter-proof tests not only the check but the scaffolding
under it.** That is its second return, and without it neither of those
two faults would have come to light.

### One per check, not one per file

**A file with sixty-five checks owes sixty-five counter-proofs.** This is
not pedantry, it follows from what a counter-proof shows: that **this
one** check falls when **this one** thing is false. About the sixty-four
beside it, it says nothing. The twelve checks that could not fall at all
stood exactly there — in files full of checks that did what they should.

And it is cheaper than it looks. The copy is made once, the broken spot
travels from check to check, the run is the same. What costs time is
working out what would have to be broken, and that thinking is the
return: it forces the check to be read as a claim about the program
rather than as a line of source.

### What the register can carry, and what it cannot

**The debt is per check; the bookkeeping is per file.** Both are true
from their own side, and a reader who meets only one of them gets it
wrong. `tests/state/counterproof` holds one row per test, with one field
for what was broken and one red line. A file with sixty-five checks
therefore owes sixty-five counter-proofs and has room to show the
evidence for one.

**The bookkeeping is the weaker of the two, and it is the part that
would have to grow.** A row per check, tied to that check's own wording,
would let the ratchet count what is actually owed; today its number
counts files without an entry and so understates the debt by whatever a
proved file's other checks amount to. Until then the rule stands as
written — every check gets its counter-proof, and the entry documents
the one that was hardest to break — and the gap is named here rather
than quietly closed by lowering the rule to what the file format can
hold.

**Whether an old proof still holds is half a machine question.** The
register ties a row to the wording of the judgements in the file, not to
the file name. So renaming the **file** costs nothing: the row follows
it, and the register writes the new name in. Reordering costs nothing
either, because the wordings are compared as a set. But rewording a
judgement, adding one or splitting one changes the fingerprint, and the
register then reports the test as rewritten since its counter-proof —
whatever the change meant. That is stricter than the rule of thumb
below, and on purpose: the wording is the only handle a machine has on a
claim.

**The other half no machine sees, and it is the dangerous one.** A check
that keeps its wording while its condition changes — a limit moved, a
comparison turned round, one field swapped for another — stays green
with an entry that no longer proves anything. Only whoever makes the
change catches that. Hence the rule of thumb:

> If **what** the check claims changes, the entry is void and a fresh
> one is owed. If only **how** it looks changes, it stands — and
> changing the how without changing the what is rare, so when in doubt,
> prove it again.

**The origin is mutation testing.** One changes the program in one place
and looks whether a test goes red; if none does, none of them is
checking there. The tool of that school says what it is up against:
*"Traditional test coverage measures only which code is executed by your
tests. It does not check that your tests are actually able to detect
faults in the executed code."* That is the difference between a line
that ran and a line something was claimed about. At scale it is too
expensive — one mutant costs a suite run — but restricted to the lines
that changed it is affordable, and that is what is done here by hand.

## 6. Waiting is on a condition, never on the clock

A fixed pause costs time in every run for ever, and it makes the test lie
in both directions: too short and it fails on a busy machine, too long
and nobody notices it is waiting for something that never comes. One test
here spent 121 of its 123 seconds waiting for an event that never
arrives at that point, and reported green afterwards. Asked for the right
condition, it took three seconds.

**The interval is short, the ceiling may be generous.** The two numbers
cost different things: the interval is time lost in the normal case, the
ceiling is never reached in the normal case. A high ceiling is therefore
free as long as the question is asked often, and it is what keeps the
builder green. Turning up a fixed pause instead makes every run dearer
and defers the failure to the next, slower machine.

**Give up on standstill, not on a deadline.** The builder is up to three
times slower than the workstation, so a deadline that is generous here is
tight there and the test goes red while the window was working the whole
time. What is measured is therefore how long since anything last
changed. That does not scale with the machine, and it catches the case a
deadline cannot see at all — that something is stuck although there is
time left. The pipeline tools know this as a no-output timeout, a
setting of its own beside the wall-clock deadline; **our builder does not
have it**, so the standstill counter has to live in the test. That is
also why it pays: a wall-clock deadline across six jobs of different
speeds can only be set wrongly, a standstill counter cannot.

**Green on this machine proves nothing about the builder.** In a study of
five large projects, 86 percent of the tests that flaked on the pipeline
could not be made to flake on an ordinary workstation, not even in a
hundred runs. Whoever touches a waiting place checks it on the builder.

**Exhausted patience is red, not green**, and a sign of life has to
change because the program is working. A bar that creeps on by itself
moves whether anything happens or not, so waiting on it measures the
bar. What the condition should be is worth measuring rather than
guessing: put a probe on a copy and see when the thing really happens.

The origin: in the largest survey of flaky tests — 201 repairs from 51
projects — waiting on a fixed time is by a distance the biggest group of
causes, 45 percent, ahead of concurrency. The advice is put there as a
prohibition: *"Never use bare sleeps to wait for asynchronous responses:
use a callback or polling."* And flakiness is not wear: 78 percent of
flaky tests were already flaky when they were written. It is built in,
which is why this stands in the rules and not in a clean-up plan.

## 7. A skipped test is not a green one

**Skipping has to be visible or it is a lie.** A test that bows out
because its material is missing and returns 0 is indistinguishable from
one that checked everything. The same holds for a single step left out
because a folder was not there: what is missing here is probably missing
on the builder always, so a closing line claiming that everything was
checked is false exactly where it matters. And a reason is only a reason
if it says what would bring the material back.

**Red beats skipped.** Both can be true in one run — a test leaves out
what this machine cannot do and fails over the rest. Ask about the
skipping first and it reads as skipped, the failure is neither shown nor
counted, and that is the same lie as green.

**What runs on no machine is removed, not skipped.** A test that looks
for files which do not exist and bows out satisfied stands in the list
as a full member and is worse than none: it holds the place where
somebody would expect a real one. How much may be skipped is therefore a
ratchet like the others — it may fall, never rise.

## 8. A test cleans up after itself

**A fixed path makes one run's result depend on the last one's.** It
collides as soon as two tests run side by side, and it survives the run.
One test with a fixed folder poisoned itself: the program writes its
project file beside the material, and every run after the first walked
into a question nobody answered. The shared fixture folders are the one
exception, and only because they are built before the fan-out and read
afterwards; writing into them turns them into shared mutable state and
into the cause of the next flake.

**What was there before belongs to whoever put it there.** A test
deletes what it created and nothing else, and leaves nothing behind that
a second run could find — not in the cache, not in the preferences, not
in the keychain. Otherwise the suite stops being repeatable, and the
first symptom is a test that passes only in the order it was written in.

**And nothing goes outside.** No network, no upload, no checking for a
newer version. A test that reaches the network makes the weather part of
the result.

## 9. What is deliberately not taken over

For completeness, so that it is not weighed up a third time.

**A framework.** What one gives — discovery, concurrency, isolation,
skipping, a time limit — the run already has. The price would be
rewriting the whole folder, and every printed line with its measurement
beside it would become an `assert`. That line is what makes a case
recognisable.

**A coverage target.** Make a coverage figure a target and it will be
reached, and the suite is no better for it. The number serves as a way
of searching for unchecked paths and for nothing else.

**A mutation-testing tool.** The idea yes, the tool no: one mutant costs
a suite run, and for every site in this program that is days. By hand
and restricted to the check that changed, it is affordable, which is
section 5.

**The test pyramid.** It wants many small tests, and small is defined
not by the size of what is checked but by the resources allowed: one
process, one thread, no network, no disk, **no sleeping**. By that
measure not one test here is small, because the program consists of
files, ffmpeg and a window. Small would only be had with a stand-in for
ffmpeg, and then the test checks the stand-in — a stand-in that size
could not be answered for under section 5 anyway. In exchange our tests
go the way a user goes, and the more a test resembles real use, the more
confidence it carries.

**The price is paid, though, not argued away.** Large tests flake more,
almost linearly with their size; that is measured. Exactly what small
tests are forbidden — sleeping, blocking, waiting — ours do unavoidably.
That is why section 6 is not a refinement but the thing that makes this
shape bearable, and why the flake rate is a number worth knowing: it
loses its value as it approaches one percent.

**One action per test.** See section 1: the situation is too expensive
here.

**Given/When/Then as a name form.** The criticism of it — names one has
to scroll to read, repeated parts that make finding harder — weighs
heavier under a character cap than what it gives.

**7±2 as a measure for the number of prefixes.** In the taxonomy
literature it is applied and never justified, and in the interface
literature it is contested. In its place a test that can be measured:
does every prefix actually separate?

**Time limits per test size.** Not attestable from a primary source, so
not adopted.

## 10. The sources

What was taken from each, so that a rule can be traced to its ground.

**F.I.R.S.T., Ottinger and Schuchert, 2009, and *Clean Code* ch. 9.**
Self-validating: tests are pass-fail. Section 1.

**Meszaros, *xUnit Test Patterns*, 2007.** The never-fail test, section
1. Assertion roulette and the missing assertion message, section 4 —
including the point that it counts most with a command-line runner,
which is our case in every run.

**Peruma et al., CASCON 2019**, over 656 open-source Android projects.
47 percent of projects and 34 percent of test files hold a test with no
assertion at all. Section 1, the figure that shows it is not a one-off.

**Carr, TDD anti-patterns, 2006.** The liar: a test that runs but does
not test what it claims to. Section 2.

**Winters, Google Testing Blog, 2024.** Begin the investigation with
nothing but the test's name and its failure message. Section 4.

**Takebayashi and Peruma et al., 2023 and 2024.** Five percent of
assertions carry a message, while 62 percent of developers say they add
one. Section 4, why it has to stand on a list rather than be left to
habit.

**Luo et al., FSE 2014**, 201 repairs from 51 projects. Async wait is 45
percent of all causes of flakiness, and 78 percent of flaky tests were
flaky when written. Section 6.

**Fowler, *Eradicating Non-Determinism in Tests*.** Never bare sleeps,
use a callback or polling; a short interval with a high ceiling costs
nothing. Section 6.

**Lam et al., ISSTA 2019.** 86 percent of the tests that flaked on the
pipeline could not be made to flake on a workstation. Section 6.

**The no-output timeout of the pipeline tools**, and the standing request
for one on ours. Aborting on output silence is an established idea, and
our builder does not have it. Section 6, why the standstill counter has
to live in the test.

**PIT, pitest.org.** Coverage measures which code ran, not whether the
tests could detect a fault in it. Section 5.

**Jia and Harman, TSE 2011**, the coupling effect. Test data that
catches the small mutants catches over 99 percent of the compound ones.
Section 5, why broken means small.

**Google, *Software Engineering at Google*, ch. 11.** Test sizes are
defined by the resources allowed, no sleeping among them, and flakiness
loses its value as it approaches one percent. Section 9.

**Google Testing Blog, 2017.** Flakiness rises almost linearly with the
size of a test. Section 9, the price of our shape.

**Dodds, the testing trophy.** The more a test resembles the way the
software is used, the more confidence it gives. Section 9.

**Wake on Arrange-Act-Assert, and *Clean Code* on a single concept per
test.** Not one assertion per test but one concept per test. Section 1.

**The KUnit style guide, *Clean Code* ch. 2, Zilberfeld, Osherove,
Google ch. 12, Reid, Khorikov and INNOQ.** The objections in section 3:
against a filler word that every name carries, for brevity, for the
scenario in the name, and the split verdict on ordering tests by part of
the program.
