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
gone through for 3.0.0b26.

## Where the program stands today

**Version 3.0.0b26.** It runs every week, on real material.

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
and even then by a frame or two. Each recording also says what is in its
sound: speech, or a mix with music under the voices. Only a mixed one
may be placed by the phase of its sound; a speech recording that shares
no sound with the cameras is refused rather than guessed at, and one
that no way of measuring can place stands at its timecode. The window,
the preview and the finished project are all built on that one
reckoning.

Separation, speech recognition and the transcript run on the machine in
front of you. Separation and recognition each need a
model, fetched once on first use: the separation's lies in a folder
beside the program, the recognition's in a cache of its own. No account,
no token, and after that one download no network. Ordering the transcript
from auphonic.com is gone, tick and switch with it, so the words no
longer depend on a service being reachable or on a preset being chosen.
Levelling, de-bleed and noise removal there are still optional, and the
program uploads only when somebody asks it to. Who speaks when is
worked out by voice on the raw microphones either way, after the
service as without it.

Where a fact is missing, the window says so instead of taking an answer
that changes nothing. The settings that need the words open before the
first run: once the time axis stands, the window writes the transcript
in the background. Until it is there, or where the recognition is
switched off or has failed, they stand greyed with the reason under
them, as do those that need a wide shot, and they open again the moment
the fact arrives.

The log beside the program says what a run did outside itself: every
call to ffmpeg and ffprobe with the file it was about and how long it
took, the recognition and the separation the same way, what the two
players loaded and played, and which of the three ways placed each
recording. Everything the window showed in red stands there too, with
the time of day -- a red mark is gone the moment its row is drawn
again, and the complaint about it arrives hours later.

Every language the window offers says everything: its catalogue
answers every one of the
roughly 1600 texts the program has, the lines of a run and the step
into Resolve included. What each language answers is counted at every
push and may only grow. Whether the texts fit the window is measured at
every push for English and German, and for every language in the run
before a release; a text cut off there is noted for the next version
and does not stop this one.

It is a Python program: a folder, `videopodcast_magic/`, holding a small
file the program starts in, forty-three pieces beside it in folders of
their own, and the speaker model. It is installed with
`pip3 install git+...` and there is nothing to build. Fetching one file
and starting it was the other way in until 4.9.2026 and is not one any
more -- a copy without the rest of the folder stops during the import.
Python 3.10 or newer has to be there, and `ffmpeg`, which is not Python
and is the one thing pip cannot bring; every Python package it needs is
on the list pip reads and arrives with the install. macOS and Windows
are what it is used on, and it runs on Linux as well, where the Auphonic
key is kept in the desktop's keyring through `secret-tool`.

**It was one file until 4.9.2026, and it is a folder now.** The texts
went out first, into a file for each language, and the rest followed
over the next three days: the file the program starts in held 37 535
lines that day and holds 811 now. The window, long the largest piece,
was taken apart in 3.0.0b26 into a main window, one piece for each of
its four tabs, and one model of the production that the project file,
the start of a run and the file list read; what is left of it holds
3206 lines, and the largest piece is now the one that tells the
speakers apart, with 3847. The assignment table and the run's time base
became pieces of their own the same way. What follows for anybody
working on it is only this -- the program is copied as a folder, never
as the file inside it. A suite of 401 tests runs at every push: six runs
side by side, three systems and two versions of Python. Beside it stand
eight more that cannot run anywhere else: four want a real Resolve, and
four auphonic.com itself. The six are not equally fast, and
Windows is the slow one: for 3.0.0b24 the slowest of the six took 1067
seconds, Windows with Python 3.10, and in the seven green runs measured
on 3.9.2026 it was a Windows job every time. That longest job is the wait, not the
sum of the six.

**Why it is still beta.** The format of the project file may still
change. An older file is refused with a clear message rather than half
read. Anybody who keeps projects for months should know that. The beta
ends when the format holds still, and a change that breaks it raises
the major number.

## What comes next

**3.0.0b26, and the four versions after it, in short.** 3.0.0b26 did what it was set
to: it took the window apart into pieces, split the assignment table
and the run's pipeline the same way, and built tests against
auphonic.com beside those against a real Resolve -- both run only on
the owner's machine, when a change calls for them. It also brought the
first of the whole-way tests forward. 3.0.0b27 takes the whole-way
tests further and fixes what the window visibly still does wrong.
3.0.0b28 makes the time axis and the hand-over to Resolve more exact,
with the rest of the whole-way tests. 3.0.0b29 opens more of the
Auphonic options, takes more than two channels, replaces set thresholds
with measured ones and shows the preview in HDR. 3.0.0b30 gives the
program a sound path of its own, without auphonic.com. The order can
change; the four items below are what stands first in it.

Four items. The first three are work. The last one is built, and what
it waits on is somebody sitting down with real material rather than
more building.

**The whole way gets tests, not the single functions along it.** Seven
steps, and each of them on both paths: the program opens, files come
in, In and Out are marked, the change to the third tab, the cut with a
speaker recognition that is already there, the run itself, the import
into Resolve. It is one item and not a list of fifty: whoever takes it
on covers one of the seven steps whole, because gaps picked off by
number give a test each and no way at all. Four of the seven have their
test since 3.0.0b26 -- files coming in, the cut with a speaker
recognition already there, the run itself, and the import into Resolve,
that one against a stand-in -- and a fifth test holds the assignment
table; each runs the same production once from the window and once
from the command line and holds the two against each other. The
program opening, In and Out, and the change to the third tab are still
open. A test of In and Out on a 29.97 camera found the window's mark
landing about three frames late, and what to do about it is not yet
decided. The survey that counted those gaps is several versions old and
most of what it named has been covered since, so it is worth taking
again before anything is built on it.

**Tests against a real DaVinci Resolve.** They cannot live in the
suite: on a machine without Resolve every one of them would be red for
a reason that is not a fault. They sit beside it, in a folder of their
own with a starter the suite does not know, and they run one after
another on the one machine that has Resolve, and only when started
with `bash resolve.sh --go`. Four are built, and three of them now run
against the untitled project Resolve opens with, which is the state
after every start. The opening title belongs here -- the
program puts it on the second video track and reads back how many clips
landed there, and a stand-in cannot confirm that. So does the case no
stand-in has ever shown: a Resolve that says no.

**The two ways to auphonic.com get run against the service.** Both ask
the same question -- does a stereo recording come back with both
channels -- and they ask it in two entirely different ways. A single
recording goes through the simple interface: the production is created
without starting it, the output files are read back, the fold to mono
is struck from each of them, and the whole thing is sent again, so two
calls. Several recordings go through the full one, which puts the same
wish into the single request. The first way has a test against the
service now, beside three that fetch the presets, send a key nobody
holds and run a short mono file; they start only with `bash auphonic.sh
--online`. The second way has no test of its own yet, and one does not
stand in for the other. Until both have run, the manual describes those
two ways from the source instead of from a run.

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

* **A published address for the manual**, once somebody needs one to
  hand out. The dozen numbers in it that stood without their default
  and the direction they pull in have both now.

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
  four new dependencies for a program whose 401 tests run as plain
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
keychain, on Windows in the registry and on Linux in the desktop's
keyring; where Linux has no keyring, it does not store it at all. The
project file holds no command line, so the key is not in it
either, and a run from the command line takes the stored one;
`--store-auphonic-key` asks for it where the terminal does not show it,
so it stands in no shell history. No report needs it.

**Patches are welcome, and there is no second reviewer.** A small
change that does one thing gets read and merged; a large one waits.
MIT, and no contributor agreement to sign.

**Before a patch, read [CONTRIBUTING.md](CONTRIBUTING.md).** It is ten
minutes and it holds the rules that turn a change back however good the
idea is: run `cd tests && bash run.sh` and leave it green, every check
owes a proof that it can go red, and the manual is bilingual with a
test enforcing it -- so changing an English chapter means changing the
German one in the same commit.
