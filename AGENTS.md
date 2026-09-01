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

| when this is about to happen | read first |
|---|---|
| the change touches more than one file | `strang` |
| anything inside a `tests/*_test.py` changes | `test-neu` |
| a test is red, wobbling, or green and not to be trusted | `test-rot` |
| a check was written or changed and is green | `gegenbeweis` |
| a commit message is about to be written | `commit` |
| a section of `CHANGELOG.md` is written or changed | `changelog` |
| a user can see the change and `docs/` says the old thing | `handbuch` |

A pull request that shows one of them was not read is turned back. The
pull request template asks which you read.

The tests:

```bash
cd tests && bash run.sh          # always through run.sh, never bare python
```
