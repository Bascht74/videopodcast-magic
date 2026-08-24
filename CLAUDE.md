# videopodcast-magic

Raw material from a video podcast becomes an edited episode: the good
audio inside the video files, the cameras on one time axis, a first cut
by speaker, and a DaVinci Resolve project.

One file, `videopodcast-magic.py`, about 24000 lines. No package, no
build step.

`README.md` is the short version. `docs/` holds the manual: one file per
chapter, English as `docs/name.md` and German as `docs/name.de.md`.
Changing a chapter means changing both, or `german_hunt_test.py` turns
red. The test checks that every chapter has both languages and that no
German word stands in an English one.

## Running the tests

```bash
cd tests && bash run.sh          # all of them, several at a time
WORKERS=1 bash run.sh            # one after another, easier to read
VPM_PYTHON=/usr/bin/python3 bash run.sh    # a different interpreter
```

A test is green when it returns 0 and prints neither a traceback nor
`FAIL`. `style_test.py`, `language_test.py` and `consistency_test.py`
are ratchets: their counts may fall, never rise. Do not delete
`tests/state/`.

A full run takes a couple of minutes. Copy the script to a snapshot,
start the suite against that, and do the next thing:

```bash
cp videopodcast-magic.py /tmp/snap/vpm_sNN.py
(VPM_SCRIPT=/tmp/snap/vpm_sNN.py nohup bash run.sh > /tmp/suiteNN.log 2>&1 &)
```

## The rules that are not negotiable

**The Auphonic API key never goes into a file, a script, a document or a
command line.** It lives in the macOS Keychain or the Windows Registry.
Inside the program it reaches curl through a temporary config file with
mode 0600, so it is never in the process list. The project file strips
`--auphonic-api-key`.

**The program never uploads to auphonic.com on its own.** Only when
somebody asked for it.

**English in the source, German from the catalogue.** Every user-visible
string goes through `T()`; the German lives in `CATALOGUE["de"]` at the
end of the file. Changing a string means changing both sides, or
`german_hunt_test.py` turns red.

**Measure, do not guess.** If a number is needed, it gets measured. What
was measured goes into the log. Third-party names are asked for at run
time, never written into the code.

`development/coding_guidelines.md` says how the code is written, and why.
`CHANGELOG.md` says what changed in each version, from 0.1.0.

## How to work here

**Parallelise, and account for it.** Before the first edit of any task
that touches more than one file, split the work by file and start the
strands. The same before the first edit of any task that has more than
two pieces which do not depend on each other. One file, one strand,
never two strands in one file. Say which file each one owns.

Working alone is allowed. Saying nothing is not: **if you do not split,
write one sentence saying why** ("one file", "three lines", "the second
piece needs the first"). That sentence is the point of the rule. An
exhortation to parallelise gets skipped once you are deep in a task; a
sentence that has to be written does not.

Say what was measured and what was assumed. Never claim a test passed
without running it.

Explain a change in plain words, not in terms of the code: what it does
and why.

## The working notes are not in this repository

Everything about who works on what, what is still open and what has been
decided lives in `docs/notes/`. That folder is deliberately not shipped:
it holds material from real productions. If you have it on disk, **read
`docs/notes/claude_intern.md` first**. It is the counterpart to this
file and names the rest. If you do not have it, this file is complete on
its own; nothing here depends on it.
