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
gone through for 2.10.1-beta.

## Where the program stands today

**Version 2.10.1-beta.** It runs every week, on real material.

It does the work that comes before the edit: it puts the processed
audio into the video files as the first track, brings recorders and
cameras onto one time axis, tells the speakers apart from the sound
alone, proposes a first cut by speaker, and writes a DaVinci Resolve
project.

Separation and speech recognition run on the machine in front of you.
The model sits in a folder beside the program: no account, no token,
and after the one download no network. Levelling, de-bleed, noise
removal and transcription at auphonic.com are optional, and the
program uploads only when somebody asks it to.

It is one Python file of about 30000 lines, with no package and no
build step. Python 3.10 or newer has to be there, and the two packages
it needs it installs itself. macOS and Windows are what it is used on,
and Linux works with two limits. A suite of 98 tests runs in about
half a minute.

**Why it is still beta.** The format of the project file may still
change. An older file is refused with a clear message rather than half
read. Anybody who keeps projects for months should know that. The beta
ends when the format holds still, and a change that breaks it raises
the major number.

## What comes next

Ordered by what each one gives against what it costs. The first three
are small and overdue; the rest is where the work sits.

**1. The release page offers the file people actually download.** A
release today offers a source archive of about 60 MB, and the one file
the README tells anybody to fetch is not where they look for it.
Attaching `videopodcast-magic.py` and its SHA-256 sum puts it there
and lets a reader check what arrived. The program holds every model
file against a checksum already; it does not yet hold itself against
one.

**2. A clone stops carrying 32 MB it does not need.** The working
folder of a test run reached the repository by accident and holds a
second copy of the separation model and an outdated copy of the
program. Everybody who clones pulls it along. Taking it out costs one
commit, and the history stays as it is: rewriting it would move the
tags that installed copies fetch their model from.

**3. The progress bar stops jumping backwards.** Under load the bar
can fall back while the run itself is fine. During a run of many
minutes that bar is the only thing saying whether anything is still
moving, so a display that lies is worse than no display.

**4. Windows and Linux get a run of their own.** The program is used
on Windows, and the suite has never run there. A workflow that starts
it on a hosted runner is being tried out, and whether the suite goes
green on Windows or on Linux at all is the open question. One gap
stays open whatever that run says: the program keeps the Auphonic key
on Windows in the registry, and no test anywhere touches that path.

**5. The manual stops drifting from the program in silence.** Five
lists in the manual copy a list out of the source: the switch table,
the menu bar, the cut rules, the numeric defaults, and the links
between chapters. About 140 lines of test hold set against set and go
red when one side moves. They compare sets, never sentences. A test
that goes red on every rewording is switched off within a week, and
after that it guards nothing.

**6. Multitrack names its own voices.** With one microphone per person
the program knows who talks when, and it knows which microphone is
which. Holding the two against each other should say by itself that
"Speaker 2" is the microphone of the person asking the questions, so
nobody has to name the voices by hand. The same comparison is a check:
if separation and microphone disagree, something is wrong. The data is
all there and the match has not been measured.

**7. The wide shot gets a calmer rhythm.** The interval after which
the wide shot returns is the one setting that decides how restless the
cut feels, and it changes nothing about how well speakers are
recognised. Raising it gives fewer and longer wide shots at the same
hit rate. How long an episode may run without a wide shot is a matter
of taste, so the number stays a switch.

**8. The two ways to auphonic.com get run against the service.**
Transcription of a single track, and a multitrack production carrying
one stereo track, are both built and neither has been sent for real.
Whether the service hands a stereo track back with both channels is
open. Until it has run, the manual describes those two ways from the
source instead of from a run.

## What comes later

Coarser, and in no fixed order.

* **Cutting exactly between two words.** The reaction cut lands where
  the sound is quietest, which is a real speech pause almost every
  time. Placing it between two words needs the word times Whisper
  gives. The recogniser macOS brings is far faster and reports on a
  60 ms grid, and it leaves no gap between words at all, so on its
  numbers "between two words" cannot be told from "inside a word".
  Speed against precision, and it will end as a switch rather than as
  a decision.

* **A "mhm" stops counting as silence.** Sounds under four tenths of a
  second are dropped before the pause search runs, so a short reaction
  reads as a pause and a wide shot can land on top of somebody
  answering. Correcting the threshold changes how many pauses the
  program believes in, which is why it is a measurement and not a
  one-line fix.

* **Defaults that carry evidence.** A few numbers come from a single
  reference edit rather than from a measurement. `--wide-latest` is
  the clearest case. Each of them gets measured or gets smaller.

* **The reaction cut is watched before it stays on.** It fires a few
  dozen times in an episode and it is on by default, and nobody has
  yet sat through every place it fires. Two cases it must not fire on
  are known: a rhetorical question, and the technical talk before the
  recording proper, where people look at equipment rather than at each
  other.

* **The opening title is checked in a real Resolve project.** The
  program puts it on the second video track and reads back how many
  clips landed there. A stand-in stands in for Resolve in the tests,
  so only a real project can confirm it.

* **The edges of the program get tests.** Measured coverage is about
  two thirds. What the suite does not touch is the whole run as a run,
  the single-file path, the way to auphonic.com, the separation and
  the self-update. Coverage gets measured now and then and never
  becomes a target.

* **The manual gets what it still lacks.** Every number with its
  range, default and direction. One screenshot that shows the wrong
  tab. A picture for the channel chapter. A keyword index beside the
  chapter list. A published address for the manual, once somebody
  needs one to hand out.

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

* **Pull requests as a review gate, required reviews, CODEOWNERS.**
  All three assume a second person. A maintainer who approves his own
  change has only made the path longer. Pull requests may still turn
  up once there is a workflow whose result can hang on them.

* **Discussions.** An empty room reads worse than no room. Issues are
  on, and that is where a question goes.

* **A wiki.** The manual lives in `docs/`, in two languages, and a
  test holds the two sides against each other. A wiki would be a
  second version that nothing checks.

* **A code of conduct, a contributing guide, issue and pull request
  templates.** They raise a percentage on a GitHub profile page while
  there is nobody writing. The templates arrive the day somebody
  actually reports something.

* **Conventional Commits.** Their purpose is a generated changelog and
  a generated version number. This changelog is written by hand and
  carries a measurement in almost every entry, and a generator would
  turn it into a list of subject lines.

* **A rewrite onto pytest, ruff, mypy and pre-commit.** All four want
  a package with a `pyproject.toml`. Here they would be four new
  dependencies for one file whose 98 tests run as plain scripts in
  half a minute. A thin pytest layer that starts those same scripts
  unchanged is a different thing, and that one may come.

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

* **Splitting the test run over several machines, retrying flaky
  tests, triage bots.** The suite is half a minute, no test has
  flapped yet, and there is no queue of reports. All of that answers a
  volume this project does not have.

* **Installers, signed packages, notarising, PyPI.** It is one file on
  purpose: fetch it and run it.

* **Sponsors, Projects.** Paperwork with nothing in return.

## How to report a fault or take part

**Issues are on**, at
[the issue tracker](https://github.com/Bascht74/videopodcast-magic/issues).
Discussions are off on purpose. A question, a fault and a wish all go
to the same place, and none of them needs a template.

**No item above carries an issue number.** The tracker is empty so
far, and an item gets an issue the day somebody besides the author
needs to follow it. Asking after one is a fair use of the tracker.

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

**Before a patch:** run `cd tests && bash run.sh` and leave it green.
The manual is bilingual and a test enforces it, so changing an English
chapter means changing the German one in the same commit.
