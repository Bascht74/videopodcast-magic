# For an assistant working on this repository

Read **`CONTRIBUTING.md`** before the first edit. It is short and it
holds the rules that are not visible in the code:

* every user-visible string exists twice, English in the source and
  German in the catalogue, reached through `T()`;
* every check owes a counter-proof -- broken on purpose, seen red, and
  the red line written into `tests/state/counterproof`;
* four ratchets may fall and never rise;
* a test says how many judgements it reached, and its failure line
  carries wanted and found as numbers;
* the Auphonic key never goes into a file, a script, a document or a
  command line.

`CLAUDE.md` is the same ground with the reasoning behind it.

**`.claude/skills/` is binding, not advisory.** One document per
situation, and in that situation it is read **before the first edit**:

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

A pull request that shows one of them was not read is turned back. The
pull request template asks which you read. `freigabe` is not in the
table because only the owner publishes a version.

**The table is written, not typed.** Every `SKILL.md` carries its own
row, `python3 development/skill_table.py` writes it into this file and
the three beside it, and `text_skills_listed_test.py` holds them
against the skills.

The tests:

```bash
cd tests && bash run.sh          # always through run.sh, never bare python
```
