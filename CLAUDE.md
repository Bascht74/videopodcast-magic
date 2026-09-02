# videopodcast-magic

Raw material from a video podcast becomes an edited episode: the good
audio inside the video files, the cameras on one time axis, a first cut
by speaker, and a DaVinci Resolve project.

One file, `videopodcast-magic.py`, about 35 000 lines. No package, no
build step.

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

A full run takes a couple of minutes. Copy the script to a snapshot,
start the suite against that, and do the next thing:

```bash
mkdir -p /tmp/snap && cp videopodcast-magic.py /tmp/snap/vpm_sNN.py
ln -sfn "$PWD/models" /tmp/snap/models       # or the run skips and returns 1
(VPM_SCRIPT=/tmp/snap/vpm_sNN.py nohup bash run.sh > /tmp/suiteNN.log 2>&1 &)
```

**The link is not optional.** What the program looks for beside itself is
not beside the copy, and the speaker model is 33 MB -- so
`voice_split_hears_two` bows out, the run skips twice where one is
allowed, and it **returns 1 with every check in it green**. Measured on
1.9.2026: two skips against a bare snapshot, one against the working
file, and green with the link.

## What a release is

**A version is not a tag, and the tag comes last.** Evidence before the
mark: a tag whose attachment does not match what was tested is worse
than no tag. Five things belong to a version -- green on all six builder
jobs, a changelog section in both languages, a manual that is true
again, pictures that show the program as it is, and the open list
brought up to date. The skill `freigabe` says how each is done and in
what order, `changelog` how a section is written, `handbuch` how a
chapter is, and `bilder` how the pictures are taken.

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
