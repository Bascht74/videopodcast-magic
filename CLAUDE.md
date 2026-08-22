# videopodcast-magic

Raw material from a video podcast becomes an edited episode: the good
audio inside the video files, the cameras on one time axis, a first cut
by speaker, and a DaVinci Resolve project.

One file, `videopodcast-magic.py`, about 24000 lines. No package, no
build step.

`README.md` is the short version, `docs/` holds the manual: one file per
chapter, English as `docs/name.md` and German as `docs/name.de.md`.
Changing a chapter means changing both, or `german_hunt_test.py` turns
red -- it checks that every chapter has both languages and that no German
word stands in an English one.

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

**Measure, do not guess.** Where a number is needed it gets measured,
and what was measured goes into the log. Third-party names are asked for
at run time, never written into the code.

`docs/coding_guidelines.md` says how the code is written, and why.
`CHANGELOG.md` says what changed in each version, from 0.1.0.

## How to work here

Parallelise: several reviews at once over different angles, a serial
plan cut into blocks that run side by side. Say what was measured and
what was assumed. Never claim a test passed without running it.

Explain a change in plain words -- what it does and why -- not in terms
of the code.

## The working notes are not in this repository

Everything about who works on what, what is still open and what has been
decided lives in `docs/notes/`, which is deliberately not shipped: it
holds material from real productions. If you have that folder on disk,
**read `docs/notes/claude_intern.md` first** -- it is the counterpart to
this file and names the rest. If you do not have it, this file is
complete on its own; nothing here depends on it.
