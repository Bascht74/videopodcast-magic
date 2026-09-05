# The case book: judgements that were green and proved nothing

The worked cases behind sections 5b, 5c and 5d of
`.claude/skills/test-neu/SKILL.md`, which sends you here. Read it while
a check is being written and you want to see what a blind judgement
looked like when one was actually found -- the rules are in the skill,
the measurements are here.

## 5b. The three shapes of a blind judgement

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

## 5c. A judgement that forbids the repair

Found twice in one day, independently:

* A judgement demanded that `apply_time_window` leave the timecode
  behind. Five lines put that right, and the test fell -- **its own FAIL
  line proving with its own numbers that the program was now correct.**
  Fifteen lines further down the same file demanded the opposite for the
  same thing.
* A file whose docstring asks for a leverage-aware rule went red when
  somebody wrote one, although it cut the edge miss from 54.4 % to
  22.0 %.

## 5d. A guard that eats the judgement below it

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
