# videopodcast-magic

Raw material from a video podcast becomes an edited episode: the good
audio inside the video files, the cameras on one time axis, a first cut
by speaker, and a DaVinci Resolve project.

The folder `videopodcast_magic/` is the program, and it comes in
pieces. `__init__.py` is the way in and holds most of it; every piece
that has moved out sits beside it in a folder of its own with an
`__init__.py` of its own -- `language/` holds one file per language
(`language/de.py` is the German one), `ui/` holds the window since
5.9.2026. `models/` holds the speaker model and is not code.

**A piece is read out of the folder, not imported from it.** The entry
hands itself in (`ui = beside("ui", program=PROGRAM)`), the piece binds
by name what it takes, and a name that is bound again while the program
runs is reached through `PROGRAM.` rather than copied -- else the suite,
which bends 119 of the program's names from outside, would find a stale
copy. `development/internals.md` has the reasoning.

There is nothing to build, and one way in: `pip3 install git+...`,
which is its own section further down.
`pyproject.toml` makes a package of that folder and puts a
`videopodcast-magic` command on the path. The folder carries an
underscore while the repository and the command carry a hyphen, because
only an underscore can be imported.

**Fetching one file and calling it is not a way in any more.** It was
one until 4.9.2026, and older notes still say so. Measured that day and
again after the move: an `__init__.py` on its own stops while it is
being imported, with `FileNotFoundError` on `language/de.py` -- before
`main()` is ever reached, so there is nothing to see and nothing to
fall back to.

**It used to be one file, and it is a folder now.** The catalogue went
out first on 4.9.2026 and the rest followed the same day, so the aim
described here for months is reached: a folder with an `__init__.py` in
it and no single program file left. **So nothing here copies,
checksums or ships "the script" any more** -- it takes the folder,
whole. What happens when it does not is measured under *Running the
tests*.

**Working from outside, or opening a pull request? Read
`CONTRIBUTING.md` first.** It holds the same rules in the form somebody
needs who cannot ask: how the tests are run, what a counter-proof is,
which four ratchets may fall and never rise, and what a pull request
has to carry before it can be looked at. This file is the version with
the reasoning; that one is the version you can act on in ten minutes.

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
`FAIL`. Four are ratchets, whose counts may fall and never rise:
`source_limits_hold_test.py`, `text_only_texts_change_test.py`,
`source_no_loose_ends_test.py` and `text_whole_sentences_test.py`. Do not delete
`tests/state/`.

A full run takes a couple of minutes. Copy the program to a snapshot,
start the suite against that, and do the next thing:

```bash
mkdir -p /tmp/snap && cp -R videopodcast_magic /tmp/snap/vpm_sNN
(VPM_SCRIPT=/tmp/snap/vpm_sNN/__init__.py nohup bash run.sh > /tmp/suiteNN.log 2>&1 &)
```

**The copy is a folder, and that is the whole of it.** The snapshot is
not renamed any more and nothing is linked into it: the folder carries
the number, and the languages and the model travel inside it. Measured
on 4.9.2026 against a copy made by exactly these two lines: nine
languages in it, `text_german_arrives` green, and
`voice_split_hears_two` running rather than bowing out for want of a
model.

**Copy the folder, not the file in it.** An `__init__.py` on its own
looks for its texts in a `language/` that is not there and stops on the
first one, and so does every test that loads it.

**And take the model with it, because it is free.** Measured on
4.9.2026, three runs each, from this disc to `/tmp`: the whole folder is
0.05 s and 36 MB, and leaving the 31 MB model out to link it back
instead is 0.05 s and 4.2 MB. **Same time, so copy the lot** -- the
link only adds a step that can be forgotten, and forgetting it eats the
whole allowance: without a `models/` beside the copy,
`voice_split_hears_two` bows out with *no separation model beside ...*,
and the summary then reads *skips: 1 of at most 1 allowed* -- measured
4.9.2026, so any second skip turns the run red.

**The old pattern is gone, and it goes noisily.** The recipe here read
`cp -R videopodcast_magic*.py` until 4.9.2026, and that matches nothing
now. Measured the same day: under bash `cp` says `No such file or
directory` and returns 1, zsh refuses the line itself with `no matches
found`, `zip` warns `name not matched` and returns 12. So a stale
pattern in an older note stops the person reading it rather than
handing them an empty snapshot -- but it is stale, and what it means is
the folder.

## What a release is

**A version is not a tag, and the tag comes last.** Evidence before the
mark: a tag whose attachment does not match what was tested is worse
than no tag. Five things belong to a version -- green on all six builder
jobs, a changelog section in both languages, a manual that is true
again, pictures that show the program as it is, and the open list
brought up to date. The skill `freigabe` says how each is done and in
what order, `changelog` how a section is written, `handbuch` how a
chapter is, and `bilder` how the pictures are taken.

**And the tag is not typed by hand any more.** Decided on 4.9.2026: the
owner says the word, you dispatch `.github/workflows/publish.yml` over
the GitHub connection, and the workflow does the rest -- it asks for the
title first because that is free, then runs the suite itself on this
very commit, reads the version out of the program, cuts the changelog
section, and only then makes tag and release. The suite runs inside
that workflow rather than being asked about: a called workflow appears
under no run of its own, so a question would find nothing. A missing section, a tag that is already there, a
`pyproject.toml` that says another number: it stops before the mark,
because everything it asks would otherwise be found hanging on a tag
nobody can move. **The owner clicks nothing, and nothing here pushes a
tag again.** The five things above are still done by hand and before the
word; `freigabe` has the rest.

**What the manual pass turns up becomes a test, and before the tag.**
That pass is the only one that reads the program as a user, and it finds
what the tests do not: a switch that is taken and does nothing, a track
that used to be in the file and is not. Where the test is larger than
the fix, its shape is written out in `docs/notes/aufgaben.md` and it is
the first thing in the next round -- not a note saying "test this".

**Every workflow says what it is, in the same shape every time.** GitHub
names a run after the commit subject unless it is told otherwise, so a
list of runs reads as a heap of unrelated sentences. Each workflow
carries a `run-name:` of its own; a new one without it is not finished.

**Before every release, fetch the builder's times and look at them**
(`cd tests && bash builder_times.sh`). The queue order comes from the
slowest of the six jobs, because this Mac has cores to spare and
finishes in half a minute while the builder takes minutes -- and the two
disagree badly. **What you wait for is the longest job, not the sum**:
the six run side by side. And a single reading of a macOS job says
almost nothing; the same commit has come back 950 and 1091 seconds.

## What has to hold, and what is only a way of getting there

Told on 4.9.2026, after five of these had been taken for ground that
was only standing. **Everything not on this list is a means.** The
test for any proposal is one question: does it make something simpler
or let something be dropped, **without losing the cut video or making
it worse**?

**The ground:**

1. **Cameras onto one time axis, cut by who is speaking.** This is the
   thing itself. Without it nothing else has a point.
2. **The sound has to be publishable, and no voice may go under.**
3. **It runs on real material, every week.** What breaks that is not
   progress, however clean it is.
4. **Nothing out of a real production leaves this machine.**
5. **The cut has to be transferable, and the EDL is the floor.**
   DaVinci Resolve is the comfortable way and stays the target -- the
   Studio edition costs 300 euro once, updates included, and that is a
   price the owner accepts. But the program also writes
   `<name>_speakers.edl` and `<name>_cameracut.edl`, and those import
   into Resolve free and into other editors. **Less comfort, the same
   cut.** So the ground is the transfer, not the edition.

**Everything else was a position, and several have already moved**: the
program had to run without pip, had to work without Qt, had to fetch
what it needed at run time, had to be one downloadable file. None of
those is true any more, and each of them had a good reason written
beside it in the source -- **which is why they read as ground.** The
source records what was true, not what is.

**One thing about the fifth is worth knowing, and it is not a hole.**
The program's own text says external scripting -- the way it talks to
Resolve -- may be reserved for the Studio edition since 19.1, and that
no official statement was found; every measurement here was made
against Studio 21.0.4.5. That looked like a threat to the ground until
the owner named the floor: the EDL is written whatever happens, so a
run without scripting still hands over a cut.

**And the lesson from raising it is the more useful half.** The risk
was reported before looking for what already covered it -- the two EDL
files have been built for a long time. A finding is not finished when
the danger is named; it is finished when what would catch it has been
looked for.

## The rules that are not negotiable

**The Auphonic API key never goes into a script, a document or a command
line.** It lives in the macOS Keychain or the Windows Registry, and the
project file strips `--auphonic-api-key`.

One file holds it, for the length of one call: the config file curl
reads it from, so that it is never in the process list. **What shuts
that file is not the same on every system, and saying "mode 0600" for
all three was untrue.** Measured on 31.8.2026:

* **macOS and Linux** -- mode 0600, the owner and nobody else.
* **Windows** -- `os.chmod` sets only the read-only flag there and
  `st_mode` answers 0666, so the mode shuts nothing. What shuts it is
  the folder: `%TEMP%` lies inside the user's profile and inherits its
  access list. The program does not set that list and does not check
  it.

Two guards hold everywhere and are the program's own doing: the name is
unpredictable (`mkstemp`, never a fixed path), and the file lives only
as long as the call -- removed on every path, and overwritten first
where it cannot be removed.

Whoever tightens this on Windows sets an access list of its own
(`icacls`, pywin32) and writes the third bullet again. Until then the
rule promises less there, and says so rather than claiming a mode it
does not have.

**Nothing out of a real production goes into this repository.** Not a
file name, not a folder, not a path, not a person, not a preset or a
production number -- neither in the test material, nor in a picture, nor
in a test, nor in a note that is shipped. Everything here uses roles:
`Guest`, `Presenter`, `CoPresenter`, `WideCam`. Everything here lives
under `/tmp`.

Measured on 1.9.2026, and this is why the rule is written down: the
manual's terminal pictures carried the whole path of a private disc,
publicly, for sixteen versions. The fixture built by `tests/fixtures.sh`
carried the file names of two real episodes, readable on GitHub. Both
had been looked at many times and seen by nobody, because each of them
looked like what it was surrounded by.

**A demo name still has to teach.** `a.wav` says nothing; a picture in
the manual is there to explain. It carries the shape a recorder or a
camera really writes, so the reader recognises it -- and it keeps the
length of what it replaces, because a shorter name would hide the place
where the program cuts a name off. **A picture that shows the program
prettier than it is, is no picture.**

Whoever adds material asks the question before the first file: **could
this name have come off somebody's disc?** If yes, it is renamed before
it is written, not afterwards -- afterwards it is in the history, and
taking it out of there costs the history.

**Installing is pip3, and nothing else.** Decided on 4.9.2026.

    pip3 install git+https://github.com/Bascht74/videopodcast-magic
    pip3 install -U git+https://github.com/Bascht74/videopodcast-magic

Measured: three seconds each, and no PyPI needed. Every Python package
the program needs stands on the list pip reads -- `requirements.txt`
and `pyproject.toml` -- so nothing is fetched behind anybody's back and
nothing is missing on the first start. `requires-python` turns a Python
that is too old into pip's answer rather than a printed line.

**What follows from it, and it is the point: nothing is ever said
before the window.** The one case that used to need a printed line was
a missing PySide6, and pip3 brings it. So a run that finds something
missing opens the window and says it in the fourth tab -- which is the
program's console now, because nobody starts it from one.

**ffmpeg is the exception it cannot be**, because it is not Python.
That is what the fourth tab is for: what pip3 cannot bring is fetched
there, in front of somebody, asked rather than done.

**The program never uploads to auphonic.com on its own.** Only when
somebody asked for it.

**English in the source, German from the catalogue.** Every user-visible
string goes through `T()`; the German lives in `language/de.py` inside
the program's folder, keyed by the English wording, and is read out of
the folder the program sits in.
Changing a string means changing both sides, or
`text_no_german_left_test.py` turns red.

**Measure, do not guess.** If a number is needed, it gets measured. What
was measured goes into the log. Third-party names are asked for at run
time, never written into the code.

**A measurement holds for the thing measured, and not for its
neighbour.** Measured on 3.9.2026: a strand found that `pipx` cannot
update an installation made from a git URL, and that was reported here
as "without PyPI there is no updating". `pip3` does it in three
seconds -- measured, but only after the owner asked. A finding about
one tool, one switch, one platform says nothing about the one beside
it. Where it is named anyway, it is named as unmeasured.

**What is unmeasured may be named, and may never decide.** That rule
above says how a thing is labelled; this one says what the label
permits, and without it the label changes nothing. A case nobody asked
for and nobody measured is not a reason to keep something -- it is a
note. So two questions stand in front of every recommendation to leave
a thing as it is: **who asked for this case, and who measured it?** If
the answer to both is nobody, what falls away is the recommendation,
not the thing.

Measured on 4.9.2026, and it went wrong twice in one day over the same
tool, in opposite directions -- which is why it is written down at
length.

**First, to keep something.** `+write_colr` was to stay because an
older ffmpeg "might" behave as the comment beside it claimed. Only
ffmpeg 9 had been measured. Nobody was running an older one, nobody had
asked, and the risk was invented on the spot, then allowed to decide.
The owner's answer: **supporting old versions is a position, not
ground.**

**Then, to shut something out.** Out of the same unmeasured place came
a floor: ffmpeg 9.0.1, below it nothing runs. It was set because 9 was
what had been measured -- and it turned **all six builder jobs red at
once**, because they carry 8.1.2. The measurement that then took five
minutes says 8.1.2 hands the metadata through perfectly well. The
floor went to 8.1.2 that day, on the owner's rule for where a floor
belongs: **only what we know.** A floor says what we answer for; it
does not claim that what lies below is broken.

**It stands at 9.0.1 again since the evening of 4.9.2026 -- and how it
got there is the whole lesson.** The same number, the opposite way
round: first the program was given something to offer on all three
systems, then the builders were measured and mended (Homebrew was
serving 8.1.2 off a formula index frozen at image-build day), and only
then did the floor rise. **A floor is raised last, never first.** What
it costs to do it the other way was measured that morning: six red jobs
in one push.

**The two failures are one failure.** Both times something unmeasured
was allowed to decide -- once for the old, once against it. Caution
that points outward and caution that points inward are the same
mistake, and neither is safer than the other.

**And the surroundings are rarely as fixed as they look.** An old
version, a foreign tool, an operating system: those are mostly
decisions, not laws of nature. Whoever takes them as given builds
detours around a wall that could have been moved. **The question is not
"what is there?" but "what do we require?"**

**Green here is not green there, and the gap is what this machine
carries.** Measured in the night to 4.9.2026: a change was green on
this Mac three times over, 219 tests, and turned four of six builder
jobs red. The cause was `certifi`, which macOS brings along -- **the
absence of a thing cannot be seen where it is never absent.** Before a
release, what is missing elsewhere matters more than what passes here.

**A question is only asked where somebody can answer it.** Same night:
the install question was printed first and the terminal checked
afterwards, so a run with nobody in front of it wrote two lines into a
place that has to stay silent. Where nothing can be answered, nothing
is asked and nothing is said -- the caller knows what it wanted and
says that in its own words.

`development/coding_guidelines.md` says how the code is written, and why.
`CHANGELOG.md` says what changed in each version, from 0.1.0.

## How to work here

**Parallelise, and account for it.** Before the first edit of any task
that touches more than one file, split the work by file and start the
strands. One file, one strand, never two strands in one file. Say which
file each one owns. Working alone is allowed; saying nothing is not, so
**if you do not split, write one sentence saying why**. A file another
strand owns is not a reason to wait either -- prepare instead. The skill
`strang` says how an order is cut, and how work is prepared against a
file somebody else is holding.

Say what was measured and what was assumed. Never claim a test passed
without running it.

**Every check owes a counter-proof, and it is written down.** A check
that has never been seen red is not known to check anything -- in one
day seventeen were found that had been green for months while testing
nothing. **No change to a test and no new test is finished until its
entry is in `tests/state/counterproof`**, and
`source_checks_proved_test.py` is a ratchet over the tests still missing
one. The skill `gegenbeweis` says
how it is done, including the question to ask when a counter-proof
refuses to go red.

**The skills are not suggestions. Each one names a situation, and in
that situation it is read before the first edit** -- by whoever is
working, and by every strand they send out. A skill nobody opens at the
right moment is a document, and this project has learned that twice in
one day.

| when this is about to happen | read first |
|---|---|
| a task touches more than one file | `strang` |
| anything inside a `tests/*_test.py` changes -- also one line, also when no judgement changes | `test-neu` |
| a test is red, wobbling, or green and not to be trusted | `test-rot` |
| a check was written or changed and is green | `gegenbeweis` |
| a commit message is about to be written | `commit` |
| a version is going out | `freigabe` |
| a section of `CHANGELOG.md` is written or changed | `changelog` |
| something a user can see has changed and `docs/` still says the old thing | `handbuch` |
| the window changed, or a release is coming | `bilder` |
| a task is wide enough for several agents at once | `workflow` |

`development/` is not in that table on purpose: it is looked things up
in, not worked through. `coding_guidelines.md` says how the code is
written, `internals.md` how the program works inside, `measurements.md`
what was measured, `test_guidelines.md` why the rules about tests are
what they are.

**What you promise in conversation is an entry, not an intention.** Say
"that goes on the list" and it goes on the list -- into
`docs/notes/aufgaben.md`, in the same breath, before the next thing is
started. A strand that reports gets written down because its report
arrives; a sentence you said to somebody has nothing that arrives.
Measured on 2.9.2026: six points promised in one night, none of them
written, all six found only because he asked a second time.

Explain a change in plain words, not in terms of the code: what it does
and why. **Short**, in a comment as in a commit message. The road that
led there goes in `docs/notes/`, not into the message. The skill `commit`
says how a message is written, and why a subject line that needs the diff
beside it is worth nothing.

## The working notes are not in this repository

Everything about who works on what, what is still open and what has been
decided lives in `docs/notes/`. That folder is deliberately not shipped:
it holds material from real productions. If you have it on disk, **read
`docs/notes/claude_intern.md` first**. It is the counterpart to this
file and names the rest.

Without it this file still stands, but not everything does: two tests
read `docs/notes/`, and where a chapter of it is missing they leave that
piece out and say so rather than going red.
