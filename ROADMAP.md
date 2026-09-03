# Roadmap

*Auf Deutsch: [ROADMAP.de.md](ROADMAP.de.md)*

What is built, what comes next, and what this program will not become.
It gives an order and no dates. One person writes it beside real
production work, and a date here would be a guess that reads like a
promise.

Nothing on this page is a commitment. An item moves up when it turns
out to matter more, and it is dropped when a measurement says it is
not worth building. What has actually shipped stands in
[CHANGELOG.md](CHANGELOG.md), version by version. This page was last
gone through for 2.24.0-beta.

## Where the program stands today

**Version 2.32.0-beta.** It runs every week, on real material.

It does the work that comes before the edit: it puts the processed
audio into the video files as the first track, brings recorders and
cameras onto one time axis, tells the speakers apart from the sound
alone, writes down what was said, proposes a first cut by speaker, and
writes a DaVinci Resolve project.

Every run goes the same way. `--multitrack` says how the recordings are
grouped into productions and nothing else: the time axis, the place of
each camera and the files that come out are the same with the switch
and without it. Several recordings with no camera among them are laid
against each other instead -- equally long, one starting point -- rather
than turned away.

Separation, speech recognition and the transcript run on the machine in
front of you. The model sits in a folder beside the program: no account,
no token, and after the one download no network. Ordering the transcript
from auphonic.com is gone, tick and switch with it, so the words no
longer depend on a service being reachable or on a preset being chosen.
Levelling, de-bleed and noise removal there are still optional, and the
program uploads only when somebody asks it to.

Where a fact is missing, the window says so instead of taking an answer
that changes nothing. The settings that need the words, and those that
need a wide shot, stand greyed with the reason under them, and they open
again the moment the fact arrives.

It is one Python file of about 35000 lines, with no package and no
build step. Python 3.10 or newer has to be there, and the two packages
it needs it installs itself. macOS and Windows are what it is used on,
and Linux works with two limits. A suite of 159 tests runs at every
push: six runs side by side, three systems and two versions of Python.
They are not equally fast, and Windows is almost always the slow one:
over the last seven green runs the slowest of the six took between 263
and 374 seconds. That longest job is the wait, not the sum of the six.

**Why it is still beta.** The format of the project file may still
change. An older file is refused with a clear message rather than half
read. Anybody who keeps projects for months should know that. The beta
ends when the format holds still, and a change that breaks it raises
the major number.

## What comes next

Four items. The first two are work. The last two are built, and what
they wait on is a run rather than more building.

**Gone out with 2.25.0-beta: the cameras are written only for the
window that is cut** -- 83.57 GB became 6.09 GB on real material. It
came without the switch this page promised, because the In and Out
points already are one: set them and only the window goes out, leave
them empty and nothing is cut. The timecode trap was real and is
measured -- ffmpeg leaves it where it was, so the program sets it -- and
a second trap turned up beside it: cutting between two key frames puts
picture and sound 400 ms apart, so the cut goes back to the key frame
before the window.

**The whole way gets tests, not the single functions along it.** Seven
steps, and each of them on both paths: the program opens, files come
in, In and Out are marked, the change to the third tab, the cut with a
speaker recognition that is already there, the run itself, the import
into Resolve. A survey counted 121 stations along that way -- 65
covered, 56 not -- and nine of the gaps have been built since. It is
one item and not fifty-six: whoever takes it on covers one of the seven
steps whole, because fifty-six tests picked off by number check
something each and no way at all.

**Tests against a real DaVinci Resolve.** They cannot live in the
suite: on a machine without Resolve every one of them would be red for
a reason that is not a fault. They sit beside it, in a folder of their
own with a starter the suite does not know, and they run one after
another on the one machine that has Resolve. Four are built. The
opening title belongs here -- the program puts it on the second video
track and reads back how many clips landed there, and a stand-in cannot
confirm that. So does the case no stand-in has ever shown: a Resolve
that says no.

**Measured on 1.9.2026, and it is why they are not yet a routine:** the
test that proves an interrupted run leaves nothing behind makes the
interruption by killing a process that holds an open connection to
Resolve with a project open. Three runs, two survived, the third took
Resolve down and left a half-made project the sweeper cannot see -- it
reads projects, and that thing shows as a folder. Before they run again
the interruption has to be made in an orderly way. Three projects from
three sessions were found in the owner's project manager the same night,
none of them ever removable, because nothing forces a test's project
name into the one shape the sweeper knows.


**The two ways to auphonic.com get run against the service.** Both ask
the same question -- does a stereo recording come back with both
channels -- and they ask it in two entirely different ways. A single
recording goes through the simple interface: the production is created
without starting it, the output files are read back, the fold to mono
is struck from each of them, and the whole thing is sent again, so two
calls. Several recordings go through the full one, which puts the same
wish into the single request. Neither has ever been sent for real, and
one does not stand in for the other. Until they have run, the manual
describes those two ways from the source instead of from a run.

**The reaction cut is watched before it stays on.** It fires a few
dozen times in an episode and it is on by default, and nobody has yet
sat through every place it fires. Its seconds count from the end of the
question now rather than from the start of the answer, so what is set is
what is seen. Two cases it must not fire on are known: a rhetorical
question, and the technical talk before the recording proper, where
people look at equipment rather than at each other.

## What comes later

Coarser, and in no fixed order.

* **Defaults that carry evidence.** A few numbers come from a single
  reference edit rather than from a measurement. `--wide-latest` is the
  clearest case: 120 seconds, with one edit behind it. Each of them
  gets measured or gets smaller.

* **The edges of the program get tests.** What the coverage is, a run
  says: coverage.py over `bash run.sh`, with `COVERAGE_PROCESS_START`
  set so the runs the tests start are counted too. On a green run it
  stands at about three quarters of the statements; it is read as a
  band, and never as a target. What no test enters: the run that takes
  its sound from the cameras, the failure exits of `main()`, the one
  place the Auphonic key touches the disk, the preset preflight, a
  Resolve that refuses, and the way back after an update that went
  wrong. And several switches are taken with nothing checking what they
  do: `--tc`, `--fps`, `--wide-shot`, `--hdr-check`, `--version`.

* **The comments in the program get the treatment the tests have had.**
  27 % of the file is comment, and most of it was written before the
  rules for writing one. In the tests it is done, and they came out a
  third shorter.

* **The manual gets what it still lacks.** About a dozen numbers still
  stand without their default and the direction they pull in. And a
  published address for the manual, once somebody needs one to hand
  out.

* **Smaller commits.** A commit whose subject needs an "and" is two
  commits. It costs nothing, and it makes `git bisect` and `git blame`
  answer a question instead of pointing at a heap.

## What we do not plan to do

The most useful section on this page, because it saves you asking. A
wish that is missing from this page is a different matter: it has not
been refused, it has only not come up yet.

* **A production at auphonic.com without a preset.** Their own page
  allows it, and it would be the third entry in our list. It stays out:
  a production without a preset carries no settings, and offering the
  settings here would mean building their interface a second time. Pick
  the preset there, choose it here.

* **Cut the episode.** The camera cut is a proposal and the edit stays
  yours. The program measures and hands over; deciding is not a later
  stage of that.

* **Placing a cut on a word boundary instead of on the sound.** It
  stood under what comes later, and the measurement has answered it
  the other way round: the quietest point lands in a real
  speech pause 97 to 99 times in a hundred, the word boundary of the
  recognition 42 to 46. The text still says roughly where -- sentence
  and clause ends come from the word times -- and the sound says
  exactly where. Swapping that round would make the cut worse.

* **Pull requests as a review gate, required reviews, CODEOWNERS.**
  All three assume a second person. A maintainer who approves his own
  change has only made the path longer. Pull requests may still turn
  up once there is a workflow whose result can hang on them.

* **Discussions.** An empty room reads worse than no room. Issues are
  on, and that is where a question goes.

* **A wiki.** The manual lives in `docs/`, in two languages, and a
  test holds the two sides against each other. A wiki would be a
  second version that nothing checks.

* **A code of conduct, and templates for issues.** They raise a
  percentage on a GitHub profile page while there is nobody writing.
  The issue template arrives the day somebody actually reports
  something. **The contributing guide and the pull request template
  stood on this list and have since been built** -- not for the
  percentage: four rules here turn a change back however good the idea
  is, and somebody who cannot ask has to be able to read them in ten
  minutes. That is [CONTRIBUTING.md](CONTRIBUTING.md), and the form a
  pull request opens with already asks for them.

* **Conventional Commits.** Their purpose is a generated changelog and
  a generated version number. This changelog is written by hand and
  carries a measurement in almost every entry, and a generator would
  turn it into a list of subject lines.

* **A rewrite onto pytest, ruff, mypy and pre-commit.** All four want
  a package with a `pyproject.toml`. Here they would be four new
  dependencies for one file whose 159 tests run as plain scripts. A
  thin pytest layer that starts those same scripts unchanged is a
  different thing, and that one may come.

* **Screenshot comparison in the test suite.** The manual's pictures
  are taken in the real window style, which needs a screen somebody is
  logged in to, and a test may not take the foreground. Such a test
  would be red everywhere else or blind. A written baseline of the
  window tree does the same job more cheaply and reads in a diff.

* **Documentation tests that compare sentences.** Measured against the
  manual as it stands, checking every bold label or every stated
  default produces a fifth to a third false alarms on the first day,
  and the first day is when such a test looks its best. We do not
  build a test that starts above five per cent false alarm.

* **A coverage threshold as a gate.** Make a number a target and it
  will be met. The list of functions no test ever calls is worth
  having; the percentage is not.

* **Splitting the test run over several machines, and triage bots.**
  The six runs answer in minutes, and there is no queue of reports.
  Both would answer a volume this project does not have. Running a test
  a second time is a different matter, and that one is built: a test
  that crashed gets another go, one that came back red beside the
  others is run once more alone, and either way the run calls it
  unsteady rather than counting it green. A test that flaps is a fault
  to be found, not noise to be retried away.

* **Installers, signed packages, notarising, PyPI.** It is one file on
  purpose: fetch it and run it.

* **Sponsors, Projects.** Paperwork with nothing in return.

## How to report a fault or take part

**Issues are on**, at
[the issue tracker](https://github.com/Bascht74/videopodcast-magic/issues).
Discussions are off on purpose. A question, a fault and a wish all go
to the same place, and none of them needs a template.

**No item above carries an issue number.** The tracker holds one
issue, and it points at this page. An item gets an issue of its own
the day somebody besides the author needs to follow it. Asking after
one is a fair use of the tracker.

**What makes a report usable:** what you started, what came out, and
what you expected instead. The log names the version and which copy of
the script ran, so that line is worth pasting. Several runnable copies
of one version are normal here, and without that line there is no
telling later why two runs came out differently.

**Never paste your Auphonic key.** The program keeps it in the
keychain or the registry, never in a file, and it strips the key from
the project file. No report needs it.

**Patches are welcome, and there is no second reviewer.** A small
change that does one thing gets read and merged; a large one waits.
MIT, and no contributor agreement to sign.

**Before a patch, read [CONTRIBUTING.md](CONTRIBUTING.md).** It is ten
minutes and it holds the rules that turn a change back however good the
idea is: run `cd tests && bash run.sh` and leave it green, every check
owes a proof that it can go red, and the manual is bilingual with a
test enforcing it -- so changing an English chapter means changing the
German one in the same commit.
