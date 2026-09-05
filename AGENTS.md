# videopodcast-magic

Raw material from a video podcast becomes an edited episode: the good
audio inside the video files, the cameras on one time axis, a first cut
by speaker, and a DaVinci Resolve project.

**This file is the source.** `CLAUDE.md` points here,
`CONTRIBUTING.md` says the same for somebody who cannot ask, and
**`development/decisions.md` holds the measured case behind every rule
below** -- which day it was learned and what it cost. Where a rule here
looks arbitrary, that file has the reason. Nothing on this page is
shortened to the point of being unarguable; it is shortened to the point
of being loadable.

## The ground: five things that have to hold

**Everything not on this list is a means.** The test for any proposal:
does it make something simpler or let something be dropped, **without
losing the cut video or making it worse**?

1. **Cameras onto one time axis, cut by who is speaking.** The thing
   itself. Without it nothing else has a point.
2. **The sound has to be publishable, and no voice may go under.**
3. **It runs on real material, every week.**
4. **Nothing out of a real production leaves this machine.**
5. **The cut has to be transferable, and the EDL is the floor.** Resolve
   is the comfortable way and stays the target; the two EDL files are
   written whatever happens. **Less comfort, the same cut.**

**Everything else was a position, and several have already moved** -- no
pip, no Qt, fetch at run time, one downloadable file. Each had a good
reason beside it in the source, **which is why they read as ground.**
The source records what was true, not what is.

## The skills are binding, not advisory

`.claude/skills/` holds one document per situation. **Each names a
situation, and in that situation it is read before the first edit** --
by whoever is working, and by every strand they send out. A skill nobody
opens at the right moment is a document, and this project has learned
that twice in one day.

<!-- skills begin: written by development/skill_table.py, not by hand -->

| when this is about to happen | read first |
|---|---|
| a task touches more than one file | `strang` |
| anything inside a `tests/*_test.py` changes -- also one line, also when no judgement changes | `test-neu` |
| a test is red, wobbling, or green and not to be trusted | `test-rot` |
| a check was written or changed and is green | `gegenbeweis` |
| a commit message is about to be written | `commit` |
| a commit has been pushed and the builder has not answered yet | `ci` |
| a section of `CHANGELOG.md` is written or changed | `changelog` |
| something a user can see has changed and `docs/` still says the old thing | `handbuch` |
| the window changed, or a release is coming | `bilder` |
| a task is wide enough for several agents at once | `workflow` |

<!-- skills end -->

`freigabe` is not in this copy: only the owner publishes a version.

**Every skill has the same shape** -- frontmatter, title, an orientation
paragraph, named sections, and `## Before it counts as done` last, ten
to twenty-five lines. A file beside a `SKILL.md` is read on demand, not
every time.

**The table is written, not typed.** Each `SKILL.md` carries its own
row; `python3 development/skill_table.py` writes the table into this
file, `CLAUDE.md`, `CONTRIBUTING.md` and the pull request template, and
`--check` compares instead of writing. The copies deliberately show
different rows; what may not differ is the **wording**.

**A skill carries rules and the cases that taught them, never the state
of the repository.** A number about how things stand today goes stale
between two commits: those belong in `docs/notes/`, or in a command.

## Where things are

* `videopodcast_magic/` **is the program, and it is a folder.**
  `__init__.py` is the way in; `language/` one file per language, `ui/`
  the window, `models/` the speaker model. **A piece is read out of the
  folder, not imported from it** -- `development/internals.md`.
* **Copy the folder, never the file in it.** A lone `__init__.py` stops
  during the import on the catalogue beside it.
* `docs/` is the manual: `docs/name.md` and `docs/name.de.md`. Changing
  one means changing both.
* `development/` is looked things up in, not worked through:
  `coding_guidelines.md`, `internals.md`, `measurements.md`,
  `test_guidelines.md`, and `decisions.md` for the rules on this page.
* `docs/notes/` is **not shipped** -- it holds material from real
  productions. If it is on disk, read `docs/notes/claude_intern.md`.

## Commands

```bash
cd tests && bash run.sh          # all of them, several at a time
cd tests && bash run.sh <name>   # one, without the _test.py
WORKERS=1 bash run.sh            # one after another, easier to read
python3 development/skill_table.py --check
```

**Always through `run.sh`.** By hand a test lacks `LANG=C LC_ALL=C
LANGUAGE=en`, `TMPDIR`, `VPM_FIXTURES` and three more, and red or green
is then a statement about the machine.

A test is green when it returns 0 and prints neither a traceback nor
`FAIL`. **Four ratchets may fall and never rise**:
`source_limits_hold_test.py`, `text_only_texts_change_test.py`,
`source_no_loose_ends_test.py`, `text_whole_sentences_test.py`. Do not
delete `tests/state/`.

A full run takes a couple of minutes, so snapshot and carry on. **The
model travels inside the folder** and is copied with it -- same time
measured, and without it a test spends the one skip the run allows.

```bash
mkdir -p /tmp/snap && cp -R videopodcast_magic /tmp/snap/vpm_sNN
(VPM_SCRIPT=/tmp/snap/vpm_sNN/__init__.py nohup bash run.sh > /tmp/suiteNN.log 2>&1 &)
```

## Rules that are not negotiable

* **The Auphonic API key never goes into a script, a document or a
  command line.** macOS Keychain or Windows Registry; the project file
  strips `--auphonic-api-key`. One file holds it for one call, its name
  unpredictable (`mkstemp`), removed on every path. What shuts that file
  is not the same on every system.
* **The program never uploads to auphonic.com on its own.**
* **Nothing out of a real production goes into this repository** -- not
  a file name, folder, path, person, preset or production number.
  Not in test material, a picture, a test, a shipped note, **or an order
  given to a strand**. Roles only: `Guest`, `Presenter`, `CoPresenter`,
  `WideCam`; paths under `/tmp`. Ask before the first file: **could this
  name have come off somebody's disc?** If yes it is renamed before it
  is written -- afterwards it is in the history.
* **A demo name still has to teach.** It carries the shape a recorder
  really writes and keeps the length of what it replaces. **A picture
  that shows the program prettier than it is, is no picture.**
* **Installing is pip3, and nothing else.**
  `pip3 install git+https://github.com/Bascht74/videopodcast-magic`,
  with `-U` to update. Everything the program needs stands in
  `requirements.txt` and `pyproject.toml`.
* **Nothing is ever said before the window.** A run that finds something
  missing opens the window and says it in the fourth tab. **ffmpeg is
  the exception it cannot be**, because it is not Python: it is fetched
  there, in front of somebody, asked rather than done.
* **English in the source, German from the catalogue.** Every
  user-visible string goes through `T()`; the German lives in
  `language/de.po`, keyed by the English wording. Change one side and
  `text_no_german_left_test.py` turns red. **It is `.po` and not a
  Python file since `57b9004`** -- older notes here still say `de.py`.

## Measuring

* **Measure, do not guess.** What was measured goes into the log.
  Third-party names are asked for at run time, never written into code.
* **A measurement holds for the thing measured, not for its neighbour.**
  Where an unmeasured neighbour is named anyway, it is named as
  unmeasured.
* **What is unmeasured may be named, and may never decide.** Two
  questions before every recommendation to leave a thing as it is: **who
  asked for this case, and who measured it?** Nobody to both, and what
  falls away is the recommendation, not the thing.
* **A floor is raised last, never first.** A floor says what we answer
  for; it does not claim what lies below is broken.
* **The surroundings are rarely as fixed as they look.** **The question
  is not "what is there?" but "what do we require?"**
* **Green here is not green there.** Before a release, what is missing
  elsewhere matters more than what passes here -- **the absence of a
  thing cannot be seen where it is never absent.**
* **A question is only asked where somebody can answer it.**
* **A finding is not finished when the danger is named**, but when what
  would catch it has been looked for.

Each of these cost something, and `development/decisions.md` says what.

## Working here

* **Parallelise, and account for it.** Before the first edit of a task
  touching more than one file, split by file and start the strands. One
  file, one strand, never two strands in one file; name the foreign
  files by path. **If you do not split, write one sentence saying why.**
  A file another strand owns is not a reason to wait -- prepare
  instead. Skill `strang`.
* **Say what was measured and what was assumed.** Never claim a test
  passed without running it.
* **Every check owes a counter-proof, and it is written down.** A check
  never seen red is not known to check anything. **No change to a test
  and no new test is finished until its entry is in
  `tests/state/counterproof`**; `source_checks_proved_test.py` is a
  ratchet over those still missing one. Skill `gegenbeweis`.
* **What you promise in conversation is an entry, not an intention.**
  It goes into `docs/notes/aufgaben.md` in the same breath.
* **Explain a change in plain words, not in terms of the code**: what it
  does and why, short. The road that led there goes in `docs/notes/`.
* **A commit is made only when it was asked for**, never on `main`, and
  nothing is pushed unless that was asked for too.

## Releases

**A version is not a tag, and the tag comes last.** Five things belong
to it: green on all six builder jobs, a changelog section in both
languages, a manual that is true again, pictures that show the program
as it is, and the open list brought up to date.

**The tag is not typed by hand.** The owner says the word,
`.github/workflows/publish.yml` is dispatched, and it runs the suite on
that very commit before it marks anything. **The workflow takes the
handgrips, not the judgement**: a green run proves the mechanics held,
never that the version was ready. Skill `freigabe`.

**What the manual pass turns up becomes a test, and before the tag.**
Where the test is larger than the fix, its shape is written out in
`docs/notes/aufgaben.md` -- not a note saying "test this".

**Before every release fetch the builder's times** (`cd tests && bash
builder_times.sh`); skill `ci` says what to do with them. What you wait
for is the longest of the six jobs, not the sum. Every workflow carries
a `run-name:` of its own, or it is not finished.

## The AI policy of this repository

**Nothing here is autonomous.** A commit, a push, a tag, an upload and a
release each need somebody to have asked for them. Where a decision is
the owner's, it is put to them as running text with a recommendation,
and the work waits rather than guessing.

**What is written down is what was done.** A number that stands only in
a strand's report is not evidence, and a test that was not run was not
run. Where something is unmeasured, it says so.
