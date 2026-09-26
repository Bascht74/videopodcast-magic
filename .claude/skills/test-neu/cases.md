# The case book: what the rules in test-neu were measured on

The worked cases behind `.claude/skills/test-neu/SKILL.md`, which sends
you here, under the number of the section they belong to. Read it when
you want to see what a fault looked like when one was actually found --
the rules are in the skill, the measurements are here.

## §3. Seventeen heads that promised more

Seventeen tests checked less than their docstring promised, and all
seventeen were green. Every question in the closing list caught at least
one of them, except the fourth and the seventh, which are there to stop
the next one.

## §4. The field is uneven

Counted when the canon was set: of the closing lines 46 said `ALL OK`
and 69 `All good.`, and the canonical `check` shape stood in five files
of a hundred and forty-five. That is why the model file, not the folder,
is what a new test is written to.

## §5b. The three shapes of a blind judgement

Twenty-two judgements were found green and testing nothing in one
night, and they fall into three shapes.

**A against A.** One pure function, one argument, called twice. `not
version_key("2.0.0") < version_key("2.0.0")` proves that the function
is deterministic, nothing about the ordering it is named after --
measured, three breaks that flattened it entirely left it green while
23 neighbours fell.

**A guard repeated.** Four lines up the code already demanded it and
waited. Then nothing happens, and the judgement asks the same thing
again. Per construction always true.

**A second net repairing the fault before the judgement looks.** Take
the guard away and the program puts it right on a later pass, or the
fixture happens to give the right answer for the wrong reason.
Measured: a whole name check could be deleted and all 21 judgements
stayed green.

All three are invisible from the source. Only a broken copy finds them.

## §5c. A judgement that forbids the repair

Found twice in one day, independently:

* A judgement demanded that `apply_time_window` leave the timecode
  behind. Five lines put that right, and the test fell -- **its own FAIL
  line proving with its own numbers that the program was now correct.**
  Fifteen lines further down the same file demanded the opposite for the
  same thing.
* A file whose docstring asks for a leverage-aware rule went red when
  somebody wrote one, although it cut the edge miss from 54.4 % to
  22.0 %.

## §5d. A guard that eats the judgement below it

Found twice in one day, 2.9.2026, and one of them was put there that
same morning by somebody improving a failure line:

* `needed("the project file the closing window writes", …)` above
  `check("closing the window leaves one project file behind", …)`.
  Measured against the register's own recorded break: **11 checks, dies
  at the guard**; with the guard letting go into the judgement, 12
  checks and the check falls with its own line.
* A guard demanding the title bar carry the project name, three lines
  above the check that asks the same. Its row had been void since the
  guard went in, and nothing reported it.

## §6. How much slower the builder is

Measured on 31.8.2026 over twelve tests: the builder took a median of
8.7 times as long as this machine, and never less than 5 times.

## §8b. Three red runs from one assumption

* **Tests set aside.** Counting what lay in the folder answered 143 on
  Windows against 145 here, when that was counted.
* **A snapshot's neighbours.** Two tests sat out silently for months
  because the speaker model was not beside the `/tmp` copy. It lies
  inside the program's own folder since 4.9.2026.
* **The index, not the repository.** "An empty repository is enough"
  stood in the skill wrongly until 6.9.2026 and cost two people an hour
  on one night. Measured on the same clone, one test, twice:

```
git init only    : git ls-files counts 0     green: 0  skipped: 1
plus git add -A  : git ls-files counts 406   green: 1  red: 0
```

## §8c. The version written down in a stand-in

Measured 6.9.2026, and it cost a release its first attempt:
`run_way_back_offered` held a stand-in list of releases that spelled
out `v3.0.0b0` to `v3.0.0b4`. The hour VERSION became `3.0.0b5`, the
note an install writes named a release the list did not hold, and all
six machines went red on work that was otherwise finished.

The first fix took the list from `VERSION` and was green -- and would
have held for exactly one release, because the point the list was
*asked from* was still written down. That only showed against a copy
set two releases ahead.

## §11b. A counter line that would have broken its test

The counter template prints `done = 0` and `global done`. In one test
`done` already stood for something else, and `%d` against `None` would
have ended the file in a traceback instead of a verdict -- the line
would have broken the test it was meant to secure.

## §12. Two checks with no row possible

Two checks with a computed name stood in `text_release_ready_test.py`,
for versions, with no register entry possible, and nothing said so: the
ratchet counts tests missing a row, and that test had rows for its other
checks.
