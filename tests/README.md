# The test suite

121 tests against `../videopodcast-magic.py`.

```bash
bash run.sh              # all of them, several at a time
WORKERS=1 bash run.sh    # one after another, easier to read
python3 speakers_test.py # a single one
```

A test started by hand stays silent: every test that builds a player
sets `VPM_SILENT` itself, so it plays nothing at whoever is working
next to it, and `run.sh` sets the variable for the whole run anyway.
The program reads it with `bool()`, so any value silences the player,
`0` included, and `env -u VPM_SILENT` does not help -- the test would
set it again. Sound comes back with an empty value:
`VPM_SILENT= python3 player_test.py`.

A test counts as green when it returns 0 and prints neither a traceback
nor `FAIL`. A test that finds nothing to work on prints `SKIPPED:` and is
counted apart -- the summary line then reads `green: 50 skipped: 1`, never
green for a test that checked nothing.

Needed: `python3`, `ffmpeg`, `ffprobe`, `numpy`, `PySide6` and
`pyspellchecker` (with its German and English word lists -- without it
`language_test.py` turns red rather than skipping). The window tests run
offscreen (`QT_QPA_PLATFORM=offscreen`), so no display is required.

## Fixtures and temporary material

Every test builds its own material below `TMPDIR`. `run.sh` points that at
one folder per run and removes it at the end -- most tests do not clean up
after themselves, and a whole run is several gigabytes. `KEEP_TEMP=1 bash
run.sh` leaves it in place for looking at.

Four folders are shared and read-only, so `fixtures.sh` builds them once
before the tests fan out -- otherwise `hdr_test.py` and
`foreign_files_test.py` would race for `/tmp/foreign`:

| Folder | Holds |
|---|---|
| `/tmp/foreign` | everything that is not a camera file: text, an empty file, a truncated MP4, a folder |
| `/tmp/hdrtest` | one file per HDR case: HDR10, HLG, no static metadata, the wrong curve, SDR |
| `/tmp/playertest` | a minute of picture and sound, enough for a cut of five shots |
| `/tmp/interview` | a whole small production: three recordings, three cameras, a project file |

A finished folder carries a `.built` marker; a build broken off half way
is therefore built again rather than taken for complete. `bash fixtures.sh
force` rebuilds regardless.

## Environment

| Variable | Effect |
|---|---|
| `VPM_SCRIPT` | which script is tested (default: the one in the folder above) |
| `VPM_MEDIA` | folder with a project to open (default: `/tmp/interview`, which `fixtures.sh` builds) |
| `VPM_SHOTS` | where the window screenshots go (default: `tests/shots/`) |
| `WORKERS` | how many tests at once (default: processors + 1, at most 12) |
| `KEEP_TEMP` | keep the run's temporary folder and its cache |
| `VPM_CACHE` | where the program keeps what it computes between runs. `run.sh` points it at one folder per run and throws it away at the end, so a suite leaves nothing in the cache of whoever started it |
| `VPM_NO_UPDATE_CHECK` | do not look whether a newer version is out (`run.sh` sets it: a suite has no business on the network, and none swapping the file it is testing) |
| `VPM_INSTALL_TOOLS` | answer the ffmpeg question with yes before it is asked, so a run with nobody in front of it installs it over the package manager instead of stopping |

Five tests need a folder holding `videopodcast-magic_Interview_2.json` and
the files it points at: `start_button_test.py`, `footer_bar_test.py`,
`run_bar_test.py` and the two screenshot scripts `preview_shot.py` and
`assignment_shot.py`, which `run.sh` does not collect. `fixtures.sh` builds
a synthetic one in `/tmp/interview`, so they run from a fresh checkout.
Point `VPM_MEDIA` at real recordings to run them against those instead;
where neither is there they print `SKIPPED:` and are counted apart.

## The ratchets

`style_test.py`, `language_test.py` and `consistency_test.py` count things
that are meant to go to zero and keep the count in `state/`. A count may
fall, never rise. Today:

| Counter | Stands at |
|---|---|
| German passages in comments and docstrings | 0 |
| narrating comments | 0 |
| text lines over 79 characters | 0 |
| docstring heading defects | 0 |
| lazy plurals (`file(s)`) | 0 |
| uncoloured messages | 0 |
| German words in the source | 0 |
| project keys nobody reads | 10 |

So any German word or `(s)` plural that creeps back into the source turns
the suite red. **Do not delete `state/`**: a missing count is treated as
"no baseline yet" and seeded from the current source, which would quietly
disarm the ratchet.

## Back to a first run

`first_run.sh` takes off the machine everything the program puts on it:
the environment the separation runs in, the packages it installs by
itself, what it stores between runs, the models in the Hugging Face
store, pip's download store, the auphonic key in the keychain. The next
start is then a first start.

```bash
bash first_run.sh              # say what would go, delete nothing
bash first_run.sh --for-real   # delete it, after one question
```

It is not part of the suite -- `run.sh` picks up `*_test.py` and nothing
else -- and it is not run in passing. It belongs to a change in how the
program installs or caches: then it is run once, a real project is
opened, and the first run is watched putting it all back.

Two things it leaves alone on purpose. `models/` beside the program: the
separation model travels with the program rather than being fetched, so
removing it does not test an install, it breaks the program. And the
project folders, whose results are nobody's to delete but their owner's.

`--without-torch`, `--without-modules` and the other `--without-` names
leave a group standing. That matters for `torch`: the environment is
built with `--system-site-packages`, so a torch already in the
interpreter makes it fetch 58 MB instead of 218 -- but other work on the
same machine may need it.

## What these tests do not do

Three of them -- `render`, `render_hdr`, `multicam` -- print their result
and compare it to nothing. They catch a crash, not a wrong number, and
they will stay that way: what they build is a render job or a multicam
clip for DaVinci Resolve, and only Resolve can say whether it is right.
Each of the three says so in its docstring rather than leaving the reader
to find out.

The other five that used to be silent -- `colours`, `metrics`,
`dualmono`, `crosstalk`, `intro` -- now measure what they print.
