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
gone through for 3.0.0b18.

## Where the program stands today

**Version 3.0.0b18.** It runs every week, on real material.

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

Where a file sits on the shared time axis comes out of its sound. A
camera's own clock counts only where the sound gave nothing to go on,
and the run names every file it had to place by the clock alone --
because two cameras agree on a clock only if somebody set them to one,
and even then by a frame or two. The window, the preview and the
finished project are all built on that one reckoning.

Separation, speech recognition and the transcript run on the machine in
front of you. Separation and recognition each need a
model, fetched once on first use: the separation's lies in a folder
beside the program, the recognition's in a cache of its own. No account,
no token, and after that one download no network. Ordering the transcript
from auphonic.com is gone, tick and switch with it, so the words no
longer depend on a service being reachable or on a preset being chosen.
Levelling, de-bleed and noise removal there are still optional, and the
program uploads only when somebody asks it to.

Where a fact is missing, the window says so instead of taking an answer
that changes nothing. The settings that need the words, and those that
need a wide shot, stand greyed with the reason under them, and they open
again the moment the fact arrives.

The log beside the program says what a run did outside itself: every
call to ffmpeg and ffprobe with the file it was about and how long it
took, the recognition and the separation the same way, what the two
players loaded and played, and which of the three ways placed each
recording. Everything the window showed in red stands there too, with
the time of day -- a red mark is gone the moment its row is drawn
again, and the complaint about it arrives hours later.

Every language the window offers says everything: its catalogue
answers every one of the
roughly 1400 texts the program has, the lines of a run and the step
into Resolve included. What each language answers is counted at every
push and may only grow, and every one is held to all of it.

It is a Python program: a folder, `videopodcast_magic/`, holding a small
file the program starts in, thirty-five pieces beside it in folders of
their own, and the speaker model. It is installed with
`pip3 install git+...` and there is nothing to build. Fetching one file
and starting it was the other way in until 4.9.2026 and is not one any
more -- a copy without the rest of the folder stops during the import.
Python 3.10 or newer has to be there, and `ffmpeg`, which is not Python
and is the one thing pip cannot bring; every Python package it needs is
on the list pip reads and arrives with the install. macOS and Windows
are what it is used on, and Linux works with two limits.

**It was one file until 4.9.2026, and it is a folder now.** The texts
went out first, into a file for each language, and the rest followed
over the next three days: the file the program starts in held 37 535
lines that day and holds 717 now, and the largest piece, the window,
holds 3867. What follows for anybody working on it is only this -- the
program is copied as a folder, never as the file inside it. A suite of
263 tests runs at every push: six runs side by side, three systems and
two versions of Python. Beside it stand four more that want a real
Resolve and cannot run anywhere else. The six are not equally fast, and
Windows is the slow one: over the last seven green runs, measured on
3.9.2026, the slowest of the six took between 404 and 835 seconds, and
it was a Windows job every time. That longest job is the wait, not the
sum of the six.

**Why it is still beta.** The format of the project file may still
change. An older file is refused with a clear message rather than half
read. Anybody who keeps projects for months should know that. The beta
ends when the format holds still, and a change that breaks it raises
the major number.

## What comes next

Five items. The first three are work. The last two are built, and what
they wait on is somebody sitting down with real material rather than
more building.

**The whole way gets tests, not the single functions along it.** Seven
steps, and each of them on both paths: the program opens, files come
in, In and Out are marked, the change to the third tab, the cut with a
speaker recognition that is already there, the run itself, the import
into Resolve. It is one item and not a list of fifty: whoever takes it
on covers one of the seven steps whole, because gaps picked off by
number give a test each and no way at all. The survey that counted
those gaps is several versions old and most of what it named has been
covered since, so it is worth taking again before anything is built on
it.

**Tests against a real DaVinci Resolve.** They cannot live in the
suite: on a machine without Resolve every one of them would be red for
a reason that is not a fault. They sit beside it, in a folder of their
own with a starter the suite does not know, and they run one after
another on the one machine that has Resolve. Four are built, and three
of them now run against the untitled project Resolve opens with, which
is the state after every start. The opening title belongs here -- the
program puts it on the second video track and reads back how many clips
landed there, and a stand-in cannot confirm that. So does the case no
stand-in has ever shown: a Resolve that says no.

**The tests move into folders like the pieces they test.** The program
is cut into pieces, each in a folder of its own. All but four of the
tests still stand side by side in one folder, well over two hundred of
them. Once they
follow, a piece and its checks stand in one place, and whoever changes a
piece finds its tests beside it.

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
sat through every place it fires. Two cases it must not fire on are
known: a rhetorical question, and the technical talk before the
recording proper, where people look at equipment rather than at each
other.

## What comes later

Coarser, and in no fixed order.

* **Defaults that carry evidence.** A few numbers come from a single
  reference edit rather than from a measurement. `--wide-latest` is the
  clearest case: 120 seconds, with one edit behind it. Each of them
  gets measured or gets smaller.

* **The edges of the program get tests.** What the coverage is, a run
  says: coverage.py over `bash run.sh`, with `COVERAGE_PROCESS_START`
  set so the runs the tests start are counted too. The last such run
  found about seven statements in ten entered. It is read as a band and
  never as a target, and it was taken while the program was still one
  file, so it wants taking again. What is worth having out of such a run
  is the list of places no test ever enters. Two are known without it:
  the messages the program stops with when something unexpected goes
  wrong, and the way that takes the sound from the cameras alone when
  there are no separate recordings. A third, a Resolve that refuses,
  belongs to the tests against a real Resolve above.

* **Eight long definitions get their description.** The comments in the
  program have had the treatment the tests had: comment and docstring
  fell from nearly a third of its lines to a quarter, and the places
  where a comment runs longer than the rules want fell from 104 and 141
  to seven each. What is left is the opposite gap. Eight definitions of
  a hundred lines and more, the cut player among them, still carry no
  description at all, and a check holds that number so it can only fall.

* **The manual gets what it still lacks.** About a dozen numbers still
  stand without their default and the direction they pull in. And a
  published address for the manual, once somebody needs one to hand
  out.

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

* **Required reviews and CODEOWNERS.** Both assume a second person, and
  a maintainer who approves his own change has only made the path
  longer. What does stand in front of `main` is the builder: a change
  arrives as a pull request, and it goes in only once all six runs have
  come back green.

* **Discussions.** An empty room reads worse than no room. Issues are
  on, and that is where a question goes.

* **A wiki.** The manual lives in `docs/`, in two languages, and a
  test holds the two sides against each other. A wiki would be a
  second version that nothing checks.

* **A code of conduct, and templates for issues.** They raise a
  percentage on a GitHub profile page while there is nobody writing.
  The issue template arrives the day somebody actually reports
  something. What a patch really has to carry is written down for the
  opposite reason: five rules here turn a change back however good the
  idea is, and somebody who cannot ask has to be able to read them in
  ten minutes. That is [CONTRIBUTING.md](CONTRIBUTING.md), and the form
  a pull request opens with already asks for them.

* **Conventional Commits.** Their purpose is a generated changelog and
  a generated version number. This changelog is written by hand and
  carries a measurement in almost every entry, and a generator would
  turn it into a list of subject lines.

* **A rewrite onto pytest, ruff, mypy and pre-commit.** They would be
  four new dependencies for a program whose 263 tests run as plain
  scripts. A thin pytest layer that starts those same scripts
  unchanged is a different thing, and that one may come.

* **Screenshot comparison in the test suite.** The manual's pictures are
  taken in the real window style, which needs a screen somebody is
  logged in to, and a test may not take the foreground. Such a test
  would be red everywhere else or blind. Instead, a version that changes
  the window has its pictures taken again before it goes out, so the
  manual shows the window it ships with.

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

* **Installers, signed packages, notarising, a release on PyPI.** One
  way in is enough: from the repository, with `pip3 install`, or with
  `pipx install` and the same address where a system's Python keeps pip
  out. The first install takes minutes, because the window, the speech
  recognition and the speaker separation come with it. The program
  comes from the repository and what it needs from others from PyPI;
  three things arrive past pip -- ffmpeg where it is missing, which is
  not Python, and two models on first use: the speaker separation's
  from the program's own repository, the speech recognition's fetched
  by the recognition itself. Updating takes the same road as installing,
  from the window as from the command line: it runs pip.

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
telling later why two runs came out differently. A complaint about the
preview, or about where a camera landed, wants the log itself: it holds
what the players loaded and played, which recording was laid under
which picture, and how every file got its place on the time axis.

**Never paste your Auphonic key.** On a Mac the program keeps it in the
keychain and on Windows in the registry; on Linux it does not store it
at all. The project file holds no command line, so the key is not in it
either. No report needs it.

**Patches are welcome, and there is no second reviewer.** A small
change that does one thing gets read and merged; a large one waits.
MIT, and no contributor agreement to sign.

**Before a patch, read [CONTRIBUTING.md](CONTRIBUTING.md).** It is ten
minutes and it holds the rules that turn a change back however good the
idea is: run `cd tests && bash run.sh` and leave it green, every check
owes a proof that it can go red, and the manual is bilingual with a
test enforcing it -- so changing an English chapter means changing the
German one in the same commit.
