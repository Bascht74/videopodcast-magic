# videopodcast-magic -- for Claude

**Read `AGENTS.md` before the first edit. It is the source; this file is
a pointer to it.** Everything that used to stand here -- the ground, the
rules that are not negotiable, how the tests are run, what a release is
-- is there, shorter, and the measured case behind each rule is in
`development/decisions.md`.

Not a symlink, and that is measured, not taste. Home Assistant makes
`CLAUDE.md` a nine-byte symlink onto `AGENTS.md`; here that turns
`text_skills_listed_test.py` red twice over. Measured 5.9.2026: the two
documents deliberately carry **different rows** -- `freigabe` stands in
this one only, because only the owner publishes -- and one file cannot
hold two tables, so `skill_table.py` writes eleven rows and then
overwrites them with ten. Separately, a checkout without symlink support
leaves nine bytes of text here and the same test reads no table at all.

## The skills are binding, not advisory

Each names a situation, and in that situation it is read **before the
first edit** -- by whoever is working, and by every strand they send
out.

<!-- skills begin: written by development/skill_table.py, not by hand -->

| when this is about to happen | read first |
|---|---|
| a task touches more than one file | `strang` |
| anything inside a `tests/*_test.py` changes -- also one line, also when no judgement changes | `test-neu` |
| a test is red, wobbling, or green and not to be trusted | `test-rot` |
| a check was written or changed and is green | `gegenbeweis` |
| a commit message is about to be written | `commit` |
| a commit has been pushed and the builder has not answered yet | `ci` |
| a version is going out | `freigabe` |
| a section of `CHANGELOG.md` is written or changed | `changelog` |
| something a user can see has changed and `docs/` still says the old thing | `handbuch` |
| the window changed, or a release is coming | `bilder` |
| a task is wide enough for several agents at once | `workflow` |

<!-- skills end -->

The table is written by `python3 development/skill_table.py` out of the
skills themselves, never by hand. Reword the `when:` line in the skill.

## The two that have actually gone wrong, so they stand here too

**This repetition is deliberate.** Both are in `AGENTS.md` with their
reasoning; they are repeated here because this file is the one loaded
without anybody asking, and these are the two that cost something when
they are missed. Do not tidy them away.

* **Nothing out of a real production goes anywhere** -- not into a file,
  a test, a picture, a note, **or an order given to a strand**. Roles
  and `/tmp`. Write "the owner", never a name.
* **The Auphonic API key never goes into a script, a document or a
  command line.**

## What is Claude's alone

**Every commit message ends with two lines** -- `Co-Authored-By:` and
`Claude-Session:` with this session's URL. A pull request body ends with
the "Generated with Claude Code" line and the same URL. Skill `commit`
holds the loop that counts them, and why afterwards is never.

**The working notes are not in this repository.** Everything about who
works on what, what is open and what was decided lives in `docs/notes/`,
which is deliberately not shipped. If it is on disk, **read
`docs/notes/claude_intern.md` first** -- it is the counterpart to
`AGENTS.md` and names the rest.

**Working from outside, or opening a pull request?** `CONTRIBUTING.md`
is the same ground in the form somebody needs who cannot ask, and it
takes ten minutes.
