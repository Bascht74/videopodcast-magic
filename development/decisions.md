# Why the rules are what they are

For `AGENTS.md`. Every rule on that page was written after something
went wrong or after something was measured, and this file holds the day
it happened, the number that came out, and what was decided.

**It is looked things up in, not worked through.** The rule is on the
short page so it is always there; the case is here so a rule can be
argued with rather than only obeyed. **A rule whose case has been lost
gets thrown away by the next person, or kept for the wrong reason.**
Both have happened here, in the same week, over the same tool.

`coding_guidelines.md` says how the code is written, `internals.md` how
the program works inside, `measurements.md` what was measured about the
program itself, `test_guidelines.md` why the rules about tests are what
they are. This one is about the rules of working here.

---

## The ground, and what has moved off it

Told on 4.9.2026, after five of these had been taken for ground that was
only standing. The five that hold are on the short page.

**Everything else was a position, and several have already moved**: the
program had to run without pip, had to work without Qt, had to fetch
what it needed at run time, had to be one downloadable file. None of
those is true any more, and each of them had a good reason written
beside it in the source -- **which is why they read as ground.** The
source records what was true, not what is.

**One thing about the fifth is worth knowing, and it is not a hole.**
The program's own text says external scripting -- the way it talks to
Resolve -- may be reserved for the Studio edition since 19.1, and that
no official statement was found; every measurement here was made against
Studio 21.0.4.5. That looked like a threat to the ground until the owner
named the floor: the EDL is written whatever happens, so a run without
scripting still hands over a cut. The Studio edition costs 300 euro
once, updates included, and that is a price the owner accepts.

**And the lesson from raising it is the more useful half.** The risk was
reported before looking for what already covered it -- the two EDL files
have been built for a long time. **A finding is not finished when the
danger is named; it is finished when what would catch it has been looked
for.**

---

## The program became a folder, and what that broke

**It used to be one file, and it is a folder now.** The catalogue went
out first on 4.9.2026 and the rest followed the same day, so the aim
described for months was reached: a folder with an `__init__.py` in it
and no single program file left. **So nothing here copies, checksums or
ships "the script" any more** -- it takes the folder, whole.

**Fetching one file and calling it is not a way in any more.** It was
one until 4.9.2026, and older notes still say so. Measured that day and
again after the move: an `__init__.py` on its own stops while it is
being imported, with `FileNotFoundError` on the catalogue beside it --
before `main()` is ever reached, so there is nothing to see and nothing
to fall back to.

**That catalogue was `language/de.py` when the measurement was made and
is `language/de.po` now** (`57b9004`, because a translation is data).
Found on 5.9.2026 while this file was being written: eight documents
still named the Python file, `AGENTS.md`, `CONTRIBUTING.md` and the
skills among them. **No test catches it** --
`source_skills_resolve_test.py` only resolves paths beginning `tests/`,
`docs/`, `development/`, `.github/` or `.claude/`, and a path inside
`videopodcast_magic/` is invisible to it. That is a hole worth a check,
not a tidy-up.

**The old pattern is gone, and it goes noisily.** The recipe read
`cp -R videopodcast_magic*.py` until 4.9.2026, and that matches nothing
now. Measured the same day: under bash `cp` says `No such file or
directory` and returns 1, zsh refuses the line itself with `no matches
found`, `zip` warns `name not matched` and returns 12. So a stale
pattern in an older note stops the person reading it rather than handing
them an empty snapshot. **A recipe naming a shape of file name goes
stale; one naming a folder does not.**

---

## What a snapshot has to carry

**The copy is a folder, and that is the whole of it.** The snapshot is
not renamed and nothing is linked into it: the folder carries the
number, and the languages and the model travel inside it. Measured on
4.9.2026 against a copy made by exactly the two lines on the short page:
nine languages in it, `text_german_arrives` green, and
`voice_split_hears_two` running rather than bowing out for want of a
model.

**And take the model with it, because it is free.** Measured on
4.9.2026, three runs each, from this disc to `/tmp`: the whole folder is
0.05 s and 36 MB, and leaving the 31 MB model out to link it back
instead is 0.05 s and 4.2 MB. **Same time, so copy the lot** -- the link
only adds a step that can be forgotten, and forgetting it eats the whole
allowance: without a `models/` beside the copy, `voice_split_hears_two`
bows out with *no separation model beside ...*, and the summary then
reads *skips: 1 of at most 1 allowed*. Measured 4.9.2026, so any second
skip turns the run red.

---

## The Auphonic key: what shuts the file is not the same everywhere

One file holds it, for the length of one call: the config file curl
reads it from, so that it is never in the process list. **What shuts
that file is not the same on every system, and saying "mode 0600" for
all three was untrue.** Measured on 31.8.2026:

* **macOS and Linux** -- mode 0600, the owner and nobody else.
* **Windows** -- `os.chmod` sets only the read-only flag there and
  `st_mode` answers 0666, so the mode shuts nothing. What shuts it is
  the folder: `%TEMP%` lies inside the user's profile and inherits its
  access list. The program does not set that list and does not check it.

Two guards hold everywhere and are the program's own doing: the name is
unpredictable (`mkstemp`, never a fixed path), and the file lives only
as long as the call -- removed on every path, and overwritten first
where it cannot be removed.

Whoever tightens this on Windows sets an access list of its own
(`icacls`, pywin32) and writes the third bullet again. **Until then the
rule promises less there, and says so rather than claiming a mode it
does not have.**

---

## Nothing out of a real production, and why it is written down

Measured on 1.9.2026: the manual's terminal pictures carried the whole
path of a private disc, publicly, for sixteen versions. The fixture
built by `tests/fixtures.sh` carried the file names of two real
episodes, readable on GitHub. **Both had been looked at many times and
seen by nobody, because each of them looked like what it was surrounded
by.**

Taking a name out afterwards costs the history, which is why the
question is asked before the first file rather than after it.

**A demo name still has to teach.** `a.wav` says nothing; a picture in
the manual is there to explain. It carries the shape a recorder or a
camera really writes, so the reader recognises it -- and it keeps the
length of what it replaces, because a shorter name would hide the place
where the program cuts a name off.

**And the rule reaches into an order given to a strand.** Measured on
2.9.2026: an order said "he saw it in the real window", and the strand
carried the name into the docstring of a test to explain where the
finding came from. It was doing its job. The check for real names went
red on all six builder jobs while a full run here had been green -- the
run went before the file reached its final shape. **A strand reads its
order as the standard**, and whoever writes "no real name" into it and
then puts one in the next paragraph has set two standards, and the
nearer one wins.

---

## Installing is pip3, and what follows from it

Decided on 4.9.2026. Measured: three seconds each for install and
update, and no PyPI needed. Every Python package the program needs
stands on the list pip reads, so nothing is fetched behind anybody's
back and nothing is missing on the first start. `requires-python` turns
a Python that is too old into pip's answer rather than a printed line.

**What follows from it, and it is the point: nothing is ever said before
the window.** The one case that used to need a printed line was a
missing PySide6, and pip3 brings it. So a run that finds something
missing opens the window and says it in the fourth tab -- which is the
program's console now, because nobody starts it from one.

---

## One road to a newer version, and why the second had to go

Decided on 5.9.2026, and it follows straight from the section above. The
program had two roads: pip, where a package manager owned the folder,
and, where none did, one file fetched from the tag and written over its
own way in, the one that had been running kept beside it as `.old`.

**The second was dead, and would have been wrong alive.** The address it
fetched, `RAW_FILE % tag`, ended in `videopodcast_magic.py` -- a file
that has not been there since the program became a folder on 4.9.2026.
It answers 404; that was measured elsewhere and not here, because no
test in this repository reaches the network. And had it answered, one
file written over `__init__.py` would have left `ui`, `cut`, `resolve`,
`speakers`, `speech` and `language` standing on the version before: a
mixed program, which is worse than no update at all.

**What was left was the one case it was never meant for.** It only fired
where the way in was not in site-packages, and since installing is pip3
and nothing else, that is somebody running out of a checked-out folder.
For them, a program that writes over their own source file is the last
thing they want.

So there is one road, and `--update` takes it: the same `pip_update()`
the window's button hands to its thread, in the same Python, with the
same command. What differs is only where pip's lines go -- through
`write_through` on a console, through `UPDATE_SINK` into the fourth tab.
Where pip owns nothing, both say so and do nothing, out of one sentence
in one place that names what the case is and the command that installs
it properly.

**What fetching left behind is still standing.** Nothing writes an
`.old` any more, so `restore_old_self()` and the Help entry that offers
it can only find one left over from before 3.0.0, beside a checked-out
copy. They were left because the window is another strand's file, and
they are the next thing to go.

---

## A measurement holds for the thing measured, and not for its neighbour

Measured on 3.9.2026: a strand found that `pipx` cannot update an
installation made from a git URL, and that was reported as "without PyPI
there is no updating". `pip3` does it in three seconds -- measured, but
only after the owner asked.

**What is unmeasured may be named, and may never decide.** That first
rule says how a thing is labelled; this one says what the label permits,
and without it the label changes nothing. A case nobody asked for and
nobody measured is not a reason to keep something -- it is a note.

---

## The two failures over ffmpeg, and they are one failure

Measured on 4.9.2026, and it went wrong twice in one day over the same
tool, in opposite directions -- which is why it is written down at
length.

**First, to keep something.** `+write_colr` was to stay because an older
ffmpeg "might" behave as the comment beside it claimed. Only ffmpeg 9
had been measured. Nobody was running an older one, nobody had asked,
and the risk was invented on the spot, then allowed to decide. The
owner's answer: **supporting old versions is a position, not ground.**

**The floor is ffmpeg 9.0.1 and has been since the evening of
4.9.2026. Below it nothing runs.** What follows is how it got there,
and every older number in it is a reading from one day, not a build
anybody may fetch today.

**Then, to shut something out.** Out of the same unmeasured place came
that floor, set because 9 was what had been measured -- and it turned
**all six builder jobs red at once**, because what they carried that
morning was older. The measurement that then took five minutes said
that older build handed the metadata through. So the floor was lowered
to meet the builders for a day, on the owner's rule for where a floor
belongs: **only what we know.**

**It stands at 9.0.1 again since that evening -- and how it got there
is the whole lesson.** The same number, the opposite way round: first
the program was given something to offer on all three systems, then the
builders were measured and mended (Homebrew was serving an older build
off a formula index frozen at image-build day), and only then did the
floor rise. **A floor is raised last, never first.** What
it costs to do it the other way was measured that morning: six red jobs
in one push.

**The two failures are one failure.** Both times something unmeasured
was allowed to decide -- once for the old, once against it. Caution that
points outward and caution that points inward are the same mistake, and
neither is safer than the other.

**And the surroundings are rarely as fixed as they look.** An old
version, a foreign tool, an operating system: those are mostly
decisions, not laws of nature. Whoever takes them as given builds
detours around a wall that could have been moved.

---

## Green here is not green there

Measured in the night to 4.9.2026: a change was green on this Mac three
times over, 219 tests, and turned four of six builder jobs red. The
cause was `certifi`, which macOS brings along -- **the absence of a
thing cannot be seen where it is never absent.**

**A question is only asked where somebody can answer it.** Same night:
the install question was printed first and the terminal checked
afterwards, so a run with nobody in front of it wrote two lines into a
place that has to stay silent.

---

## A promise is an entry, not an intention

Measured on 2.9.2026: six points were promised in one night, none of
them written down, and all six were found only because the owner asked
a second time.

A strand that reports gets written down because its report arrives; a
sentence said to somebody has nothing that arrives. So "that goes on the
list" means it goes into `docs/notes/aufgaben.md` in the same breath,
before the next thing is started.

---

## What belongs in a skill, and what does not

**A skill carries rules and the cases that taught them -- not the state
of the repository.** A number that justifies a rule stays, because it is
about a day that is over: the commit that was six commits, the wheel
that shipped 21 files instead of 11. A number that says how things stand
today does not: it goes stale between two commits, and a stale one
discourages or misleads. One said two thirds of the counter-proof
register were still owed; it was 12 % when somebody finally counted.
**Those belong in `docs/notes/`, or in a command that answers them.**

---

## Four copies of one table, in four wordings

Measured on 5.9.2026. `CLAUDE.md`, `CONTRIBUTING.md`, `AGENTS.md` and
the pull request template all sent a reader to the skills, all four
carried the table by hand, and by then it was already wrong: `ci` -- the
situation after *every* push -- stood in none of them.

So the skills became the source and `development/skill_table.py` writes
the copies out of them. `description` was measured first and does not
do: it is 146 to 264 characters and says both the situation and what the
document teaches, while a table cell is 20 to 94. Cutting one out of the
other would be guesswork per skill, so the row is written where the
skill is.

**The copies do not all show the same rows, and that is declared in the
skill.** `freigabe` is only in `CLAUDE.md`, because only the owner
publishes; the pull request template leaves out the four a contributor
never reaches. What is no longer allowed to differ is the *wording*: one
situation, one sentence, everywhere it appears.

**Which is also why `CLAUDE.md` is not a symlink onto `AGENTS.md`.**
Measured 5.9.2026 on a clone: one file cannot hold two different tables,
so `skill_table.py` writes eleven rows for the one copy and then
overwrites them with the other's ten, and `text_skills_listed_test.py`
reports `freigabe` missing. On a checkout without symlink support the
file is nine bytes of text and the same test reads no table at all.

---

## Some duplication is deliberate

**The language and snapshot environment stands in three skills** --
`gegenbeweis`, `test-rot` and `test-neu` -- and that is on purpose.
Each place is reached without reading the other two, and a wrongly set
`LANGUAGE` costs an hour: `LANG=C` alone does not settle it, because the
program skips "C" and asks the system, which answers `de_DE`. The test
then holds an English expectation against German output and goes red for
the wrong reason.

**The two rules in `CLAUDE.md` that also stand in `AGENTS.md`** -- no
real production anywhere, and the Auphonic key -- are repeated for the
same kind of reason: `CLAUDE.md` is the file that is loaded without
anybody asking, and those two are the ones that cost something when they
are missed.

**And the short page repeating a skill in one line is the design, not a
copy.** `AGENTS.md` carries the rule so it is there without anybody
asking; the skill carries the mechanism, the measurement and the case.
What must never differ is the rule itself.

Anything else that stands twice is a fault. Four such were measured on
5.9.2026 and moved to one home each:

* **the stand-in questions**, which stood in `gegenbeweis`, `test-rot`
  and `test-neu` -- home: `gegenbeweis`, because `test-rot` opened its
  own copy with "this question comes when the counter-proof will not go
  red", which is `gegenbeweis`'s situation;
* **when a register entry falls void**, in `test-neu` and
  `gegenbeweis` -- home: `gegenbeweis`, because `test-neu` already said
  "call it, do not copy it out" one section earlier and then copied it
  out;
* **the builder's times**, in `freigabe`, `ci` and the short page --
  home: `ci`, because that is the moment the command is run;
* **`run-name:` on every workflow**, in `freigabe`, `ci` and the short
  page -- home: `ci`, because it is about how a list of runs reads.

---

## The plural rule is read by the standard library, not by us

**5.9.2026.** A PO header carries its language's plural rule as a C
expression over one name: `nplurals=3; plural=(n%10==1 && n%100!=11 ? 0
: ...)`. Something has to turn that into an index.

**118 lines of our own stood here for an afternoon, and they were not
wrong.** Measured against `gettext.c2py` over nine languages and every
count from 0 to 1000: **9009 comparisons, not one difference.** They
were unnecessary, and that is the finding -- the standard library has
had `c2py` for as long as it has had `.mo` files, and nobody looked.

**It is also the stricter of the two.** Measured: c2py refuses an
expression nested too deep (*"plural form expression is too complex"*)
and refuses a `;` outright; ours took twenty-two levels of brackets
without a word. A catalogue is the one file in this program a stranger
is invited to edit, so the strict reader is the right one.

**The one cost, and it is named rather than hidden:** `c2py` is not in
`gettext.__all__`. So it is asked for and not assumed -- where it is
missing, no language has a rule, every count falls back on the English
one, and nothing breaks. It has been in CPython for decades and
`GNUTranslations` uses it for every catalogue in the world; removing it
would break far more than this program.

**Three counter-proofs died with the old code** and were earned again:
they broke a table, a tree walk and a return shape that no longer
exist. What a check claims did not change, so its wording stands; what
it takes to make it fall did change, and the register says so.

---

## The search path a program gets, and the one it is started from

Measured 5.9.2026. `find_required_tools` looked for ffmpeg with
`shutil.which` and nothing else, so it saw only what was in `PATH` --
and on macOS what is in `PATH` depends on how the program was started.
`launchctl getenv PATH` is empty on this Mac and `getconf PATH` answers
`/usr/bin:/bin:/usr/sbin:/sbin`, so a program opened from the Dock or
the Finder inherits those four and no more. Homebrew puts ffmpeg in
`/opt/homebrew/bin`. Out of a terminal it ran; out of the Finder it said
"ffmpeg is missing" -- the same machine, the same install, two answers.

**A fault that depends on how somebody started the program is the worst
shape a fault can take**, because the bug report and the reproduction
never meet. So the search now also looks where the package managers of
each system leave a program: `/opt/homebrew/bin`, `/usr/local/bin` and
`/opt/local/bin` on a Mac (Homebrew on Apple silicon, Homebrew on Intel,
MacPorts); `/usr/local/bin`, `/snap/bin` and `~/.local/bin` on Linux;
Chocolatey, Scoop and winget on Windows. Only the macOS three are
measured, and they are measured on one Mac; the rest is read.

**Four rules cut it to size.** A build this program fetched itself keeps
the front of the path, so a distribution's older ffmpeg cannot win.
The manager folders go behind the real path, so whoever has an ffmpeg on
their path keeps that one. A folder that is not on the disc never enters
`PATH`, or the path would grow at every start. And each system gets its
own folders only -- nothing is installed, nothing outside this one
process's environment is touched.

**The repair made three checks stop checking, and that is the more
expensive half of this entry.** Three checks in
`run_ffmpeg_new_enough_test.py` start the program in a child process
with one empty folder as the whole search path, to prove that `--help`,
`--version` and `--update` still answer while the ffmpeg gate is shut.
From the moment the search looked in the manager folders as well, that
empty path shut nothing on any machine with an ffmpeg from a manager:
the three stayed green and proved only that three switches answer.
Nothing went red to say so.

**So the switch is its own, and a check stands in front of them.**
`VPM_NO_MANAGER_PATH` is set by that test alone and by nothing else --
deliberately not a second meaning hung on `VPM_SILENT`, which the whole
suite runs under and which would have silenced the seven checks that
measure the repair. And before the three, one check asks the child
outright what its own search came back with, and wants `missing`. A
check whose precondition can quietly stop holding needs a check on the
precondition, or the day it stops holding is a day nobody hears about.

---

## The shortcut on the first start, and what it cost to weigh

Measured on 5.9.2026, when the program learned to put itself where a
person looks for programs -- a bundle in Applications, an entry in the
Start menu, a launcher in the desktop's program list.

**A piece of its own, and read where it is called.** It came in as 773
lines built to stand alone. Cut to what this program needs -- the
resizing of artwork that is not an icon size went, because the picture
we ship is one; so did a way of asking what stands there today, which
had no caller. Then the cost was measured rather than argued: reading
the piece is **0.07 ms**, median of two hundred, against **56 ms** for
the program's own import warm and 1.5 s cold. It is noise, and the
piece stays a piece.

**The finding was not the file, it was the three imports over it.**
`plistlib`, `sysconfig` and `collections` are not loaded anywhere else
in this program, and asking for the three of them at the top of the
piece cost **2.5 to 3.5 ms on every start** -- forty times the file
itself -- for code that runs once in the life of an installation. They
are asked for inside the two functions that need them, and the
namedtuple was written out as a small class. **A stdlib import is not
free because it is stdlib**, and the ratio, not the number, is what
makes it worth looking at.

**One picture at 256 by 256, and not the drawing script.** The other
strand offered a script that draws the symbol at any size: 7 kB of
source against 10.9 kB of picture, and it hits the 82 px of the Dock
and the 96 px of a Finder list exactly, which no fixed file does. It
needs Qt. The shortcut is laid before the window is built and on a
command-line run Qt is never loaded at all, so the script would tie a
decoration to the heaviest thing in the program. 256 is the one size
all three formats take: `.icns` has a slot for it, `.ico` refuses
anything over 256, and the icon theme on Linux keeps it under
`256x256`. A 512 would leave Windows with the blank sheet. What it
costs is a Finder "get info" at 512 points, which is scaled up.

**And the picture is in `desktop/` rather than at the top of the
package, which is the whole reason it is safe.** The check in
`text_german_arrives_test.py` walks every folder the program reads out
of with `beside()` and demands that each kind of file in it is named in
`[tool.setuptools.package-data]`. A file at the top of the package is
not covered by it. Measured both ways: with the line the wheel carries
`videopodcast_magic/desktop/icon.png`; without it the wheel carries no
PNG at all and says nothing -- the same silence the nine translations
went missing in earlier the same day.

**What is said, and where.** One line, no box, no question: a shortcut
was made and where, or none was and why. It is printed, and `AGENTS.md`
says nothing is ever said before the window. The tension is smaller
than it looks: the only start that lays anything is the first, and the
first cannot come from the Dock or the Start menu, because what they
start is what the first start creates. So the line is printed to a
console every time it is printed at all. It goes into the log as well,
for the start that has no console. Where the program was never
installed by pip -- a checkout somebody is working in -- nothing is
laid and nothing is printed, only written down: a line on every start
of every working copy is noise, not information.

**Windows and Linux are unmeasured, and that has to be said.** There is
no Windows and no Linux here. The macOS bundle was written and read
back by the system that owns it: `plutil` takes the plist, `sips` reads
the 256 out of the `.icns`, `mdls` calls the folder
`com.apple.application-bundle`, and the runner inside it starts the
program. The Linux launcher is written here and read back here, which
says its text is right and nothing about a desktop. The Windows link is
not written at all -- it needs the shell object that owns the `.lnk`
format -- and the test says so on a `LEFT OUT` line rather than
pretending.

---

## A guard that asks what a run is not, and what that cost

**5.9.2026.** `lay_on_first_start()` asked `VPM_SILENT` and laid nothing
when it was set. Every test run through `run.sh` sets it, so the suite
was safe, and that was measured: after a whole run the owner's
`~/Applications` held nothing.

**A measurement copy run by hand sets no such thing.** At 20:18:11 a
bundle appeared in the owner's own Applications folder, and
`~/Library/Application Support/videopodcast-magic/settings.json` was
created in the same second. pip did not install the piece that lays
bundles until **20:49:06**, half an hour later -- so it was not the
installed program, and it was not the owner starting it. It was one of
ours, out of a folder in scratch space, finding the installed starter
on `PATH` like any other program would.

**The log that would name the run died with the copy**: a run from a
checkout writes its log beside itself, and the counter-proof copies are
deleted when the measurement is written. So the culprit is not named
here. It does not have to be -- what has to change is the question.

**A guard that asks "is this a test?" is wrong however it is spelled.**
It can only list the ways a run marks itself, and a run that forgets
one passes. The condition is now positive:
`installed_by_a_package_manager()`, with `VPM_SHORTCUT` as the way a
test names a home of its own. A copy in scratch space is never
installed, so no forgotten variable can reach the owner's account
again.

**Two things fall out of it.** A checkout that happens to have an
installed starter on `PATH` -- the ordinary state of a developer's
machine -- now lays nothing, which is right and was not true before.
And the line the laying says goes into the log and never to the
console: it runs before the window opens and before the console is
redirected, so a print there is the one line somebody sees in a
terminal they did not ask for.
