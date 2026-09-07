# Inside the script

For the folder `videopodcast_magic/` and the text files in it. How the
program is put together, and how each step works. Not part of the
manual and English only: this is for whoever changes the program, not
for whoever uses it.

What was measured is in [What was measured](measurements.md): hit
rates, run times, distributions, comparisons.

---

## How the script is put together

`videopodcast_magic/__init__.py` is the way in, and it is not where the
program lives any more -- 690 lines of it, against the 37 535 it held
on 4.9.2026, the day the single file became a folder. **Thirty-four
pieces have moved out**, each in a folder of its own beside it with an
`__init__.py` in it, and the way in reaches them with `beside()`.
Nothing in it belongs anywhere else any more: what is left is the
loader, the version check, the run, the values more than one piece
reads, and the catalogue.

What is in them, largest first, every folder of the program on the list
and counted 7.9.2026 with `wc -l` over its `__init__.py` -- and **the
figure of the day is that command, not this paragraph**:

* `ui/` **6224** -- the window and everything it shows, asks or offers
* `cut/` **3955** -- who is on camera when, and what carries it out of
  here
* `player/` **3018** -- the moving picture: the player, the cut band,
  the log view, the player menu, and the hush that stops one player
  when the other starts
* `resolve/` **2591** -- the DaVinci Resolve project, timelines, colour,
  markers
* `material/` **2417** -- channels, chains, continuation files, what a
  track is made of
* `bearings/` **2075** -- the time axis, the offsets, which camera
  belongs to which voice
* `speakers/` **2157** -- who is speaking, out of the sound alone
* `pipeline/` **1972** -- the chain the recordings run until the camera
  files are written
* `preflight/` **1385** -- whether the material fits together before the
  first long step
* `speech/` **1089** -- what is said and when, and what is written down
  from it
* `auphonic/` **1314** -- the sending to auphonic.com and the fetching
  back
* `setup/` **1089** -- finding ffmpeg, installing a missing module,
  keeping the key
* `hearing/` **1046** -- decoding, envelopes, bands, phase, aligning
  audio to video
* `fittings/` **789** -- helpers that shape what the window shows and
  hold none of its state
* `metadata/` **725** -- MOV atoms, colour tags, what a recording says
  about itself
* `orders/` **703** -- the command line a run is given: written out of
  the window, and read back off the line
* `herald/` **615** -- the progress bar, the stages, the console and log
  redirection
* `desktop/` **865** -- the picture and the shortcut the first start
  lays down
* `upkeep/` **457** -- which release is out, the way back, and pip
  putting one in place
* `filelist/` **439** -- the list of chosen files: the tree it is
  shown in, and what adding and removing do to it
* `prework/` **435** -- the audio, envelopes, channels and tracks
  fetched in advance, and the bar that counts them
* `language/` **324** -- a .po file per language and the reader that
  looks one up
* `tables/` **348** -- the tables and trees the window builds
* `running/` **344** -- what a run is offered before it starts, the
  command line it builds, and the thread it goes in
* `timecode/` **317** -- timecode strings, frame rates, the clock a file
  carries
* `livery/` **276** -- the colours, the marks that say what kind a line
  is, and the room a name or a table may take
* `menus/` **237** -- the menu bar and what follows it
* `workbench/` **232** -- what more than one piece reaches over for:
  numbers as words, a channel count, one tool run, two recordings in
  step, what a video file says of itself, and the four the way in used
  itself
* `logbook/` **191** -- where the log of a run goes, and what goes into
  it
* `stowage/` **178** -- where things are put down between one run and
  the next: the work folder, what somebody chose, and the write that is
  moved into place rather than left half done
* `dials/` **174** -- the kinds a shot can be, the cut fields and their
  choices
* `filing/` **158** -- path_key, ByFile and FileSet
* `soundings/` **134** -- what has been measured of a file, taken once
  and kept
* `choices/` **75** -- the values a choice box holds, and what they are
  called

`models/` is the odd one out among the folders: the speaker model lives
there and no code at all, so `beside()` never reaches for it. There is
nothing to build.

**Seven pieces are asked for by another piece, not by the way in.**
`player/`, `fittings/`, `tables/`, `menus/`, `filelist/`, `prework/` and
`running/` are read out of `ui/__init__.py`, where the blocks they hold
used to stand, and two of them again one folder deeper: `player/` out of
`fittings/` and `fittings/` out of `filelist/`. `orders/` stood among them until
6.9.2026, when `build_argument_parser` moved into it and the way in
began to read it too -- the window then asks `beside()` for a piece
that is read already. `beside()` does not mind -- it lays
its path against the folder the *way in* sits in, whoever calls it, so
`beside("player")` out of `ui/` finds `videopodcast_magic/player/`, one
folder up from the caller and beside its own.

**What did mind was the check.** `text_german_arrives` collects the
`beside(...)` folder names out of the way in and holds them against
`packages =`, and it reads no other file -- so a `beside()` inside a
piece was invisible to it, and an installed copy could open no window
with nothing red anywhere. `source_piece_list_holds_test.py` closes
that: it walks every `beside()` call in **every** piece, holds the
folders against the list in both directions, and its fourth judgement
goes red the day the search is ever narrowed back to the way in alone.
Both halves measured 6.9.2026 on a copy, one name taken off
`packages =` at a time: `"videopodcast_magic.player"` leaves
`text_german_arrives` green and turns `source_piece_list_holds` red,
which names the call site it read the folder from
(`fittings/__init__.py line 41`); `"videopodcast_magic.filelist"` does
the same, from `ui/__init__.py line 1366`; and
`"videopodcast_magic.speech"`, which the way in fetches itself, turns
both of them red. So no name can come off this list quietly any more.

**How a piece is joined on, and why it is not an import.** `beside()`
reads the piece out of the folder and hands the program in before the
file is read; the piece then binds by name what it takes, one line per
name, because `source_no_loose_ends` wants a visible origin for every
name in its own file. What is bound again while the program runs -- the
five sinks, `LANG`, `TOOL_TROUBLE` and the rest -- is reached through
`PROGRAM.` instead, and a name bent from outside is written through
into every piece that holds it. That last line is what keeps the suite
working: it bends 124 of the program's names -- counted 6.9.2026 as the
attributes the suite assigns on the module `the_program.load()` hands
back, over every `tests/*.py` -- and a copy would part from the
original at the first assignment. It can be installed as well -- `pyproject.toml` makes a package
of that folder and puts a `videopodcast-magic` command on the path --
and nothing inside knows the difference: it is the same code either
way, and the name carries an underscore only because a hyphen cannot be
imported.

**A piece asks the program where the program is, never itself.** A
piece lies one folder deeper than the way in, so `__file__` in it names
that deeper folder. `find_required_tools` looks for an ffmpeg lying
beside the program and asks `PROGRAM.__file__` for the place; with the
piece's own `__file__` there it puts `videopodcast_magic/setup` on the
search path and answers "ffmpeg, ffprobe is missing." with both of them
lying beside the program -- measured 6.9.2026 on a copy that kept
`__file__`, against the same copy that asks the program.

**Where a piece is read decides what it can bind.** Every read has its
own row in [the table further down](#where-each-piece-is-read-and-why-it-must-stand-there),
which is where the way in's own notes went. Most of them stand
at the end of the way in, after everything they take; `setup/` is read
at the top instead, because what stands under it wants ffmpeg or a
module that may not be installed yet -- and so it can bind only what is
above that line. `as_warn` is the one name it uses that is not, and it
goes through `PROGRAM.` for that reason and no other. `FFMPEG_FLOOR`
stays on the near side of the seam as well, and that one is measured:
`text_lang_settled_first` rewrites the floor line in the way in to put
a run under it, and reads no other file.

**`workbench/` has the narrowest window of any of them, and both its edges
are measured.** It holds what more than one piece reaches over for --
`number_text` (nineteen pieces), `video_facts` (eight), `channel_text`
(four), `shell_quote` (three), `gcc_phat_offset` with `PHAT_BAND`,
`finished_tracks_find` and `stop_wanted` (two each) -- and it is read
between `language/` and `setup/`, because `setup/` is the second piece
read and binds `number_text` at its head. Measured 6.9.2026 in a child
process with `PYTHONDONTWRITEBYTECODE=1`, one line above and one
position below: read before the catalogue it stops at `T = PROGRAM.T`
with `AttributeError: 'Program' object has no attribute 'T'`, and read
after the setting up it stops at `setup/__init__.py line 22` with
`AttributeError: 'Program' object has no attribute 'number_text'`.
Either way the program does not read at all, so there is no window
either side of that one line. What it needs from below the seam --
`AUDIO_SUFFIXES`, `RUN_STOP`, `ffprobe_json` and numpy -- it reaches
through `PROGRAM.` where it uses it.

**Two pieces that need each other are read in the order that leaves one
name over.** `auphonic/` and `preflight/` are the pair: `choose_preset`
asks `check_preset` whether the chosen preset fits the run, and
`check_preset` reads that preset out of auphonic.com to answer. Read
`auphonic/` first and two names have to wait -- `check_preset` and
`report_findings`; read it after `preflight/` and one does --
`read_preset`. So it is read after, `preflight/` drops the binding line
and its one call site says `PROGRAM.read_preset(key, uuid)`. Counted
6.9.2026 out of the two files: 27 names cross that seam into
`auphonic/`, 26 of them bound at its head.

**The catalogues only travel because they are named.** setuptools packs
`.py` and nothing else, so `[tool.setuptools.package-data]` in
`pyproject.toml` names `"videopodcast_magic.language" = ["*.po"]`.
Before that line stood there the built wheel held not one `.po` file,
and nothing went red over it: it was found by looking inside the wheel,
which is the only place it shows. Both halves measured 5.9.2026 -- the
same package built without the line puts no `.po` into the wheel and
with it puts them in, and a copy of the program with every `.po`
deleted starts, still answers `languages()` with every code it knows,
holds an empty `CATALOGUE["de"]`, and says everything in English.

**It was a single file, on purpose, until 4.9.2026, and that day it
became a folder.** The catalogue was the first piece to move out and
the rest followed the same day. The large file is still large and
further cuts are to come, but the shape is now the one aimed at: a
folder with an `__init__.py` in it and no single program file left. One
thing follows from it, and it holds whatever the next cut does: **the
program is never copied out of its folder.** It reads its pieces out of
the folder it sits in, so the folder travels whole or the copy stops
during the import with a `FileNotFoundError` on `language/__init__.py`,
the reader beside it -- measured 5.9.2026 with the lone file copied out.
The `.po` files are the quieter half of the same rule: without them the
program starts and says everything in English, and nothing complains.

One rule holds inside it: everything that computes or decides sits as a
function at the top level and can be tested without a window. `gui()`
only builds the interface. So far:

| Function | what it decides |
|---|---|
| `run_argv` | the whole command line, checks and queries included |
| `slider_numbers` | the cut sliders as numbers, defaults filled in |
| `slider_argv` | the same sliders as switches |
| `build_handover` | the handover, with a sentence for every no |
| `choose_zero_point` | where programme time starts: audio first, picture as stand-in |
| `find_project_file` | the project file for whatever was pointed at |
| `format_complaint` | whether a stored file may be read at all |
| `project_files` | what of the project is still there and what is missing |
| `metrics_sentence` | the line under the preview: where speech time lands |
| `speech_heading` | sections from auphonic.com or measured here |
| `assignment_rows` | the rows of the upper table, camera audio included |
| `preselected_camera` | which camera an audio track is preset to |
| `camera_output_name` | the name of the new video file, without a duplicate |
| `measure_time_axis` | how the files lie against each other and against the clock |
| `axis_still_valid` | whether a measured axis still holds for these files |
| `pending_prework` | what envelopes and audio are still to fetch |
| `window_suggestion` | In point and Out point from what the cameras offer |
| `recordings_text` | the heading of the audio group |
| `hdr_findings` | whether a finished file passes as HDR |
| `copy_mov_atoms` | carry the `logs` atom over and read it back |

`choose_zero_point` is four lines and was twice the cause of a misplaced
cut. Now the rule stands in one place and has test cases. The other way
round, a building block of the interface that decides nothing does not
have to leave the function it is called from: `cell` and `report` are
still inside `gui()` for that reason alone. Where such a block is
wanted in more than one place it moves, and three of them have --
`table_build` into `tables/`, `mark_red` into `fittings/`, `item` into
`filelist/` -- so this is not a rule against moving them, only against
moving them for the sake of the count.

`run_argv` shows no dialogs. It returns a list of `(kind, title, text,
button)` in the order intended. `"error"` means show and abort,
`"question"` means ask and abort on no. So the order of the queries can
be tested: `run_command_built_test.py` goes through eighteen cases.

## What a cut out of the way in has to know

Every piece cut out of the way in has paid for the same handful of
lessons again, and each one was learned by running something the
reader before had reasoned about. They are written down here so that
the next cut does not pay a third time. The list of head lines that
cannot be written comes first, because it is the one that costs a
whole round when it is missed.

**`PROGRAM.X = value` does not write through to the pieces.
`module.X = value` does.** The way in sets `PROGRAM.__dict__ =
globals()`, so an attribute written on `PROGRAM` is a plain write into
the way in's own globals and never passes `OneName.__setattr__`. A test
that bends `vpm.X` goes through the other door and does reach the
pieces. Measured:

```
after PROGRAM.SINK = x : way in='x'  piece=None  piece read late='x'
after module.SINK  = x : way in='x'  piece='x'   piece read late='x'
```

**So a name written that way must not travel into a piece, and must not
get a binding line at its head.** `OUTPUT_SINK`, `ASK_SINK`,
`PROGRESS_SINK` and `UPDATE_SINK` are written from the window that way.
Move one and the program breaks where nobody looks -- while the suite
stays green, because the suite bends the name through the door that
does write through. `ASK_SINK` stood inside a cut range and was caught
by this rule, not by a red test.

### Six kinds of name that may not be bound at a piece's head

They were found one at a time over three nights, each by a different
hand, and each paragraph below carries its own measured case. Read the
list first, because from outside four of the six look identical -- the
same `AttributeError: 'Program' object has no attribute '<name>'`,
rc=1 -- and the two that do not are the expensive ones.

1. **a name the window writes through `module.X = value`** -- it must
   not travel and must not be bound. Not an error: the copy simply
   stops following. See the paragraph above.
2. **a name defined below the seam** -- `AttributeError`.
3. **a name that lives in another piece**, and above all a name of
   `ui/`, which reaches the programme only with `take_from(ui)` at the
   very end -- `AttributeError`.
4. **a name from a piece read *after* the receiving one** -- the same
   error, and from outside indistinguishable from 3, though both pieces
   are read by the way in long before any window.
5. **the receiving piece's own name** -- `AttributeError`, and the way
   out is not `PROGRAM.` but **no head line at all**.
6. **a name a piece rebinds with `global`** -- **this one is accepted**,
   rc=0, and is therefore the dangerous one: it keeps a copy of the
   value as it stood when the piece was read, and nothing catches it.

**Ways out, in order of preference**: a head line where the name is
already on the programme; `beside("<piece>", program=PROGRAM)` to take
it off the piece directly; `PROGRAM.<name>` at the use. And for 5 and
6, nothing -- the name is read as it is, or the function does not move.

**One trap that is not a head line**: `take_from` skips a name the way
in already holds, so a forced `PROGRAM.<name>` can answer a different
object than the one meant. Ask it at runtime -- `PROGRAM.x is
<piece>.x` -- for every forced read introduced.

**A name defined below the seam gets no binding line either.** The head
of a piece is read while the way in is still being read, so a copy of
something further down is an `AttributeError`. It is reached as
`PROGRAM.<name>` where it is used.

**And so does a name that lives in another piece, wherever the seam
stands.** `PROGRAM` is not the module: `PROGRAM.__dict__ = globals()`
makes `PROGRAM.x` a plain lookup in the way in's globals, which never
reaches the way in's own `__getattr__` and so never reads a piece to
answer. A name of `ui/` is in there only once `take_from(ui)` has run,
which is after `ui/` has been read whole -- so a piece read out of
`ui/` cannot bind one of `ui/`'s names at its head at any seam, early
or late, and reads it as `PROGRAM.<name>` where it calls it. Measured
6.9.2026 while `filelist/` was cut: a head line for `chain_fill_in`,
which stands 800 lines *above* that seam, answers `AttributeError:
'Program' object has no attribute 'chain_fill_in'`, and the same name
at the call site answers the very function the window holds.

**And a piece read *after* the receiving one is just as far away as one
read out of `ui/`.** This is the same rule as the first, seen from a
distance nobody looks at: the way in reads its pieces in order, and a
name is on the programme only once its own piece has been read and
`take_from` has run. Measured 7.9.2026 while `make_preview` moved into
`cut/`: `slider_numbers` and `speakers_to_cameras` live in `orders/`,
which the way in reads at line 632, and `cut/` is read at 604 --
twenty-eight lines earlier, and that is enough. A head line for either
answers the same `AttributeError` with rc=1.

From outside this looks exactly like a name of `ui/`, and it is not:
both pieces are read by the way in, both stand on the programme long
before any window. **What decides is only the order of the two reads.**
So whoever moves a function into a piece looks up where the receiving
piece is read, and treats every piece below that line as unreachable
from its head.

**And a piece cannot bind its own name at its head either -- there the
`def` has not run.** This one wears the same coat as the rule above and
is a different animal: it is not a name that arrives late, it is a name
that arrives *here*, further down the same file. Measured 7.9.2026 while
the six `preset_*` names moved into `auphonic/`: a head line for
`preset_fits_mode`, which `auphonic/` defines at its own line 261,
answers `AttributeError: 'Program' object has no attribute
'preset_fits_mode'`, rc=1 -- because at the head neither the `def` nor
`take_from` has run.

The way out is neither `PROGRAM.` nor `beside()`: it is **no head line
at all**. The piece reads its own names the way any module does. So
whoever moves a function into a piece has to sort the names it reads
into three heaps, not two -- what the programme already carries (head
line), what only exists after `ui/` (`PROGRAM.` at the use, or off the
piece with `beside()`), and **what the receiving piece already owns
(nothing to do)**. The third heap looks exactly like the second from
outside, and only the run tells them apart.

**And the rule about `global` is about the function, not the name.** A
piece that rebinds a name with `global` -- `set_language` writing `LANG`,
`Numpy` writing `np` -- cannot move that function anywhere, because the
`global` would then write a different module's name. But a **head line**
for such a name is not refused at all: measured 7.9.2026, `LANG =
PROGRAM.LANG` and `np = PROGRAM.np` at `fittings/`'s head both load and
build the window, rc=0, and `source_names_stay_fresh` on the copy came
back green.

**That makes it the dangerous one of the five**, and the opposite of
what it looks like. The other four announce themselves with an
`AttributeError` the moment anybody runs them. This one takes the head
line, keeps a **copy of the value as it stood when the piece was read**,
and goes on answering that copy after the programme has changed its
mind. Nothing catches it. `source_names_stay_fresh` exists for the
narrower case and does not reach this one.

**A cycle is broken by deleting the binding line, not by forwarding.**
A function of the same name that calls the real one is bound into the
way in under its own name before the real one exists, and the call ends
in `RecursionError` -- which no test catches.

**The seam has to carry what tests reach for, not only what code
reads.** `NAME_HOLD_S` is read by no code across its seam and is bound
back all the same, because one test asks the program for it. The cheap
way to find these: `set(dir(vpm))` before the cut and after, and it may
lose nothing.

**`__file__` in a piece means the piece's file.** `find_required_tools`
put the piece's own folder on the search path and reported present
tools as missing; `running_from` and `start_again` would name and
restart the piece. Whatever needs the program's own path reads
`PROGRAM.__file__`.

**And the fourth case of it went silent.** `log_path` in `logbook/`
answers with the folder it is asked from, so a plain `__file__` writes
the log inside the piece -- and **not one test in the suite goes red for
it**, measured 6.9.2026 on a copy. Three of the four cases were found by
a red run and this one only by counting the names that cross. So
`__file__` is counted like any other name over the seam, not looked for
after something breaks.

**And the obvious way to measure it hides it.** Bending `vpm.__file__ =
somewhere` from a test looks like the way to ask whether a piece names
the program or itself -- and it is not. That write goes through
`OneName.__setattr__`, which puts `__file__` into every piece as well,
so the piece's own `__file__` becomes the way in's and a plain
`__file__` answers correctly by accident. Measured 6.9.2026 while
`start_again` moved into `upkeep/`: the first broken copy came back "the
same file: true" and the fault was there all along. The only reading
that answers is the program read from where it really lies.

**Where a piece is read costs as much as where it is cut.** The same
range of lines needed 27 late names read at the place the code stood
and two read further down. Both ends of every candidate are worth
measuring before a line is moved.

**Let the loader answer where the seam may sit.** Move the seam in a
copy, read the copy in a child process, and take the return code and
the last line: it answers `AttributeError: 'Program' object has no
attribute '<name>'` and names the one thing in the way. Walking the
candidate positions that way gives the window as two line numbers --
6.9.2026 one piece was placed off fourteen such trials and another off
eight. It is cheaper than reckoning, and it found three windows that a
reckoning had got wrong.

**Run that sweep with `PYTHONDONTWRITEBYTECODE=1`, or it lies.** Every
variant of the file is the same size -- the block only moves -- and two
trials in the same second are the same size and the same mtime, so
Python holds the `.pyc` of the one before valid and runs it again. A
sweep of 301 positions came back naming `beside` as missing at places
where it was long since defined, and gave a window 42 lines off. It is
the trap the `gegenbeweis` skill records for broken copies, in a second
coat.

**Leave a `#---` rule behind.** Take out the first rule of a stretch and
the ground section grows to the next one, and
`source_sections_named_test.py` reports names reaching up out of the
ground. It happened twice in that one night. A rule line also counts
towards the comment-block ratchet: rule plus three lines is the shape
that fits.

**The written-out `X = piece.X` lines are for a reader and for
`source_no_loose_ends_test.py`, not for the machine.** `take_from` has
placed the names long before. Whoever takes them for the binding order
draws the next seam in the wrong place.

**A probe that only calls `the_program.load()` proves nothing about
`ui/`.** The window is read lazily out of `window()`, so a seam that
breaks it is invisible until something asks: one such probe came back
411 of 411 green over a cut it never touched. The probe calls `load()`
**and** `window()`, and holds `set(dir(vpm))` after both against the
same set taken from a copy of the tree before the cut.

**A value with one reader belongs beside that reader, and four kinds of
value do not.** Counted 6.9.2026 over the way in's top level, uses and
not mentions: `INSTALL_TOOLS` went to `setup/`, `CEILING_DBTP` and
`LIMIT_MAX_DB` to `material/`, `ONLY_MULTITRACK` to `orders/`. The four
kinds that stay: a value the way in reads itself (`LIKES_PYTHON` in the
version check, `TOOL_TROUBLE` in `main`) or that more than one piece
reads (`SPEECH_CODES`, out of `speech/` and out of `ui/`); a sink the
window writes on the program object
(`ASK_SINK`, `PROGRESS_SINK` -- see the rule at the head of this
section); `FFMPEG_FLOOR`, whose line `text_lang_settled_first` rewrites
in the way in and nowhere else; and a value the piece itself writes
back with `PROGRAM.name = value`. The last is `_SPEAKER_READY` and
`_SPEAKER_WHY`, and it was measured rather than reasoned: moved into
`speakers/` the whole suite goes on reading them correctly -- even the
test that bends one, `voice_split_names_fault`, stays 7 of 7 green,
because `take_from` carries the value up and the piece reads it back
through `PROGRAM.` -- and `source_names_stay_fresh` is the one that
falls, naming both by line: *"2 in both, wanted 0 in both:
_SPEAKER_READY bound at speakers/__init__.py line 72, written at
speakers/__init__.py line 347"*. A copy at the top of a piece under a
name the program writes on itself is the stale copy that check exists
for, whether or not anything reads it today.

**A function that rebinds a shared name with `global` cannot leave this
file either, and it is the same check again.** `set_language` writes
`LANG`, the `Numpy` stand-in writes `np`; inside a piece `global` binds
the piece's own name, so each would have to write `PROGRAM.LANG` or
`PROGRAM.np` -- and `LANG` is bound at the top of `language/`, `np` at
the top of seven pieces. Measured 6.9.2026 on two copies, one name
moved into `workbench/` in each: *"1 in both ... LANG bound at
language/__init__.py line 32, written at workbench/__init__.py line
41"*, and the same for `np` from `bearings/__init__.py line 81`. What
did go: `only_reading`, `count_process_starts`, `safe_filename` and
`Stopped`, none of which rebinds anything.

**The last three names to leave, and the two that could not.**
`language_of_system`, `spoken_language_choices` and `SPOKEN_LANGUAGES`
went into `ui/` on 6.9.2026 -- counted with `ast` over the way in *and*
all 34 pieces, uses and not mentions, `ui/` was their only reader. Two
that were meant to go with them stayed, and both refusals were measured
in a child process with `PYTHONDONTWRITEBYTECODE=1`, the probe calling
`load()` and `window()`:

* **`SPEECH_CODES` cannot go to `ui/`**, because `speech/` binds it at
  its head and `speech/` is read twenty read-blocks earlier. The broken
  copy stops at `speech/__init__.py line 19` with `AttributeError:
  'Program' object has no attribute 'SPEECH_CODES'`, return code 1. It
  now has two piece-readers, so by the rule above it stays where both
  can reach it.
* **`kept_language` cannot leave the way in at all**, because the way
  in calls it itself -- in `main()`, and on the last line before the
  `__main__` guard, which runs while the file is still being read.
  Moved into `ui/` the copy stops on that line with `NameError: name
  'kept_language' is not defined`; asking `PROGRAM.kept_language()`
  instead stops on the same line with `AttributeError: 'Program' object
  has no attribute 'kept_language'`, because `PROGRAM.x` is a plain
  lookup in the way in's globals and `take_from(ui)` has not run. Both
  return code 1. **A count over the pieces alone would have missed
  this**: the way in has to be counted with them.

**What the way in is made of.** Measured 6.9.2026: 690 lines, 419 of
them code -- 60.7 %, against 62.7 % averaged over the 34 pieces and
82.8 % in `orders/`. It was 806 lines and 54.8 % that morning. What
came out was not code: 42 comment lines standing one note per
`beside()` call, and the seven seam docstrings cut from 41 lines to one
each. **Both are in this chapter now** -- the notes as the table below,
the docstrings as the paragraphs under it -- and one comment line went
back into the way in, at the head of the read-blocks, saying so. The
syntax tree of both files with docstrings stripped came back identical
before and after that trim, character for character, so nothing that
runs was touched. 147 lines are still blank, because this is a list of
27 read-blocks with no function bodies to fill the space, and that is
the floor for a file of this shape.

### Where each piece is read, and why it must stand there

One row per `beside()` call, in the order the way in makes them. **What
binds what is the whole of it**: a piece binds at its head the names it
takes, so it has to stand under everything it binds and above every
piece that binds one of its own. Move a row and the loader answers
`AttributeError: 'Program' object has no attribute '<name>'` and names
the one thing in the way -- which is cheaper than reckoning, and the
way every window in this table was found.

| read | what binds what | why it stands there |
|---|---|---|
| `language/` | binds nothing: `beside()` is called for it without `program=` | first of all, because every message under it goes through `T` |
| `workbench/` | binds `T`; `setup/` binds its `number_text` at its head | between the language and the setting up, and both edges are measured -- above, no `T`; after setup, no `number_text`. Either is fatal |
| `setup/` | binds only what stands above it, and reaches `as_warn` through `PROGRAM.` | at the top: what stands under it wants tools and modules that may not be installed yet |
| `choices/` | takes `T` alone; ten pieces below bind its names at their heads | anywhere under the language and above those ten |
| `livery/` | takes `os`, `re` and `sys` only; 15 pieces bind its names at their heads | above all 15 |
| `dials/` | reads no name out of the program; six pieces below bind its own | above those six |
| `filing/` | 12 pieces bind its names at their heads; no line above it reads any | above all 12 |
| `stowage/` | `logbook/` binds its `cache_folder` at its head | before `logbook/`. `kept_language` stands far above it and reaches `settings` through `PROGRAM.` |
| `logbook/` | binds `cache_folder` above; `herald/` and `soundings/` bind its `outside_say` at their heads | after `cache_folder`, before `soundings/` |
| `soundings/` | binds `outside_say` above; `timecode/` binds its `ffprobe_json` at its head, as do ten pieces after it | after `outside_say`, before `timecode/` |
| `timecode/` | 13 pieces bind its names at their heads | above all 13 |
| `metadata/` | 8 pieces bind its names at their heads | above all 8 |
| `herald/` | `material/` and `hearing/` bind the progress line -- `progress_from_line` and `show_progress` -- at their heads | before both of them |
| `hearing/` | binds the herald's progress line; `material/` binds 10 of its names | after the herald, before the material |
| `upkeep/` | binds the herald's `write_through`, and nothing else binds that; the separation binds its `PIP_SOURCE` | after the herald, before the separation |
| `speech/` | binds `SPEECH_CODES`, which is the last name of the way in's own that it takes | anywhere from `SPEECH_CODES` down would do; it stands above the run that wants it |
| `material/` | the checking binds the camera margin, the clipping and `parallel_map` out of it | before the checking |
| `bearings/` | binds the material's names; the window's colours and the cut list it reads late | after the material, before the checking |
| `preflight/` | binds `RUN_STOP`; the separation binds its `run_ffmpeg_with_progress` | after `RUN_STOP`, before the separation |
| `auphonic/` | binds `check_preset` and `report_findings` out of `preflight/`, and `gui_log` out of `herald/`; `preflight/` reaches back for the one name that would close the circle, `read_preset`, through `PROGRAM.` | after the checking, because `choose_preset` asks it whether the preset fits |
| `speakers/` | the cut binds 20 of its names and the window 28; `orders/` and three pieces the window reads bind one or two more | before all of them |
| `resolve/` | binds `Finding`, which the preflight above brings in | here, and not where it is first used |
| `cut/` | the window binds its names | before the line that reads the window |
| `pipeline/` | binds the cut's names; `prework/`, which the window reads, binds its `unpack_kind` | after the cut, before the window |
| `orders/` | its head binds `MIN_SPEECH_TO_SWITCH_S` and `WIDE_AFTER_S` out of the cut just above | this late for that reason. The window asks `beside()` for the same piece and is handed this one, read already |
| `desktop/` | asked for inside `main()`, not at the top level | below the branch on purpose: `redirect_console()` renames the running log, so a line written above it lands in the log of the run before |
| `ui/` | binds 19 names out of `speakers/` and 20 out of `cut/`, both read above it | on the way to the window and not in the list: a run on the command line opens none and never reads it |

### The seven functions the seam is made of

Their docstrings say one line each in the code. What the lines said
stands here, where the rest of the seam is explained anyway.

**`OneName.__setattr__`.** A piece binds what it uses under its own
name, so a bend from outside -- only a test bends -- would reach the
way in's copy alone. Bent on the module, every piece that carries the
name follows. That is the door the head of this section is about.

**`pieces_answer_together`.** True where it took. A run that never
registers this file under its own name has no module object at all, and
so bends nothing either; it hands back False rather than dying, because
the program is also started as a plain file.

**`beside`.** By path, never by name. An import by name finds the piece
only in an installed copy, and the program is also started as a plain
file and from a path under a name a test picks -- `the_program.load()`
picks `vpm`. The program is handed in before the piece is read, so the
piece has something to bind out of at its head.

**`take_from`.** A piece is not a library beside the program: what it
brings answers here under the same name, so nothing outside has to know
which file a name ended up in. It places every name long before the
written-out `X = piece.X` lines, which are for a reader and for
`source_no_loose_ends` -- see the rule further up this chapter.

**`set_language`.** The code is held twice -- beside the way in, where
`T()` reads it, and in the way in, where a reader and every test look
for it. One door sets both, so they cannot come apart. That `global
LANG` is also why the function cannot leave the file; the rule and the
measurement stand above.

**`Numpy`.** Reading the program fetches nothing. `--version` answers
cheaply because it calculates nothing, not because argv was read while
the file was being read -- a default value in a `def` line is evaluated
as the file is read, so one reaching for numpy there would fetch it for
every `--help`. `source_numpy_comes_last_test.py` holds that.
The `global np` is why this one cannot leave the file either.

**`__getattr__`.** A name of the window, asked for before the window
was read. What the window brings stands in the way in once `window()`
has run; until then this answers by reading it. It is why a probe has
to call `window()` as well as `load()`, and why a test may ask
`vpm.spoken_language_choices` before any window exists.

## How speech is detected without Auphonic

Recorders are turned up to different degrees, so the threshold sits
over each track's own noise floor and not at a fixed level.

Without the bleed taken out of the tracks, every microphone reports
speech at once, and no camera shows exactly those speakers. The cut
then stays on the wide shot for the whole recording.

## How the recogniser is built

The small Swift program is built once and kept in the cache until it
changes or the system is updated. The recognition takes its language
version from the system region.

## How the separation is run and stored

The segments are stored raw in file time, into the cache and into the
project file; the conversion happens where they are used.

pyannote 4 sends a trace to `otel.pyannote.ai` on every run. The
worker process switches that off first and does not run at all if it
cannot find the switch.

The waveform is handed over, not the file path: `torchcodec` cannot
load the ffmpeg libraries everywhere. The checksums of the model are
checked before every load.

## How the players reach a spot

Seeking is a request in Qt, not a command, so every spot is set again
until it holds. Every 120 ms, tolerance 350 ms, up to five seconds, and
always at a standstill. A `play` that does not arrive is repeated after
400 ms. When the output device changes, the player follows the new
device.

## How the progress bar counts

The run is split into weighted sections. Writing the camera files gets
the largest share, reading the plan the smallest. If a section reports
nothing, the bar creeps on slowly, only a little past what was last
reported. It stops short of the end rather than standing still.

## How the channels are measured

*When* both channels hear the same thing decides which two of them are
one stereo pair, not how alike they are. Level and correlation both
fail here: with bleed the two microphones are loud together most of the
time. Read as a pair, both speakers land in one track, and the camera
cut has nothing left to switch between.

The program judges the recording as a whole and not block by block. It
reads blocks one at a time because they do not all fit in memory at
once. A block is read in one pass and taken apart afterwards, rather
than decoded once per channel. A 32 channel recording used to go
through ffmpeg 32 times.

The program writes both channel conversions out rather than leaving
them to ffmpeg. ffmpeg's own result depends on the output format.
Writing integers it scales the matrix down against clipping and the
level comes out right after all; writing floats it does not. The same
call is correct in one place and 3 dB out in the next. The script's own
conversion uses an equal-power law.

Only neighbours are compared: channel 1 against 2, 2 against 3, and so
on. A pair whose two channels do not sit side by side is not found.

A camera's two channels are judged like a two channel recorder file:
two clip-on microphones on them give two rows with two speaker names.
On the command line (`--multitrack`) the count works the same way as in
the window, and it is a count of input tracks rather than of files: a
recording of its own, a channel of a multichannel recorder, or the
audio of a camera whose **Camera audio** stands on **use the audio**.
The count is read from the assignment file: `cameras_as_tracks` counts
the rows of `tracks_of` that carry `own_audio`, `camera_audio` or
`from_camera`. A two channel file that was never split carries no extra
mark.

## Which way a camera's audio goes

A camera's audio takes one of two ways, and they behave differently.
This is written down because reading only one of them leads to the
wrong conclusion about the other.

What decides is the **Camera audio** field at the video file: in the
file list on **Files & production**, and again in the camera table
beside the player on **Assignment & time window**, on the same value
both times (`audio_use_value`, `audio_use_bind`). It stands on **do not
use the audio** until somebody says otherwise, and there the sound is
not material at all and takes neither way. Synchronising is not part of
the question: the time axis is measured over the envelope of every
file, whatever the field says.

| Way | What happens to more than two channels |
|---|---|
| **use the audio**, with Multitrack | `camera_audio_tracks` cuts it into tracks, by the same measurement as a recorder file |
| the simple path: one video, no audio recording | `extract_audio_from_video` keeps every channel, and the file goes on whole |

On the first way a camera is not automatically one track: two clip-on
microphones on one channel each are two people, while a real stereo
pair stays one two channel track. The audio is extracted with every
channel it has and folded afterwards, never before -- folding four
channels to one and then asking what is on them would always answer
"one voice".

On the second way the field has nothing to decide: one video with sound
and no audio recording beside it is the only sound there is, so
`audio_use_settled` returns it as used with that reason, greyed out and
never stored. The way has one track by definition, so nothing is cut
there. `kept_channels` answers 2 for two channels and 1 for anything
else, which means a four channel file is treated as mono. Nothing then
happens to it, and the four channels survive by accident rather than by
design.

## How the time axis is measured

The time axis is measured with sample points over the whole runtime, a
regression line through them, and the median instead of the mean. The
interface uses the same method in the background as the run itself.

The spread of a file is read at five spots over it, two seconds each,
from the packet timestamps in the container.

**Two ways lead to a place and either one is enough**, and
`cannot_be_placed` is the only reading of that: the timecode places a
file (`timecode_places_it` -- one on the file and one on something else
in the material), or the measurement does. Only where neither answers
is the file refused.

What decides whether a measurement answers is not the correlation.
Measured over 85 pairs that belong together and 293 that do not, the
correlation runs to 0.203 at worst for a true pair and 0.124 at best
for a false one, so no threshold separates them -- a steady mains hum
pushes it down without moving where the file belongs. `fit_places_it`
reads the two numbers the fit already produced and throws away:
how many sample points were set (`FIT_POINTS_ENOUGH`, 50) and how far
they scatter (`FIT_SPREAD_MS`, 15 ms). Those give 85 of 85 and 0 of
293. The camera-against-camera door in the window's measurement reads
it, as the run's does.

The window used to leave a file out where the run kept it, so the cut
band showed one camera fewer than the finished project. It asks the
same question now. A file the sound could not vouch for is still marked
-- `weak` -- but it keeps the place its clock gave it, and only
`no_place` bars anything. `weak_note` and `weak_colour` turn the two
apart: warning colour and "sound not recognised; placed by its
timecode" against error colour and "does not fit the other files".

`speaker_source_pick` follows the same rule rather than one of its
own. It leaves out only what has no place at all; a camera whose sound
was not recognised may be the source of the separation. Measured on
such a camera -- hum at 99.94 Hz sitting 51.7 dB over the speech -- two
speakers in 90 seconds of it.

## What the preflight remembers a file by

A measurement is filed under a fingerprint. The fingerprint is a sha1
over the measurement version and the language of the run. For every
file involved it also covers the absolute path, the size and the
modification time. The first sixteen hex digits of that hash name the
file in the preflight cache. A file that changed gets a different
fingerprint and is measured again; an unchanged one is read from the
cache.

The language belongs in the fingerprint because a stored finding holds
its text ready-made. Without it a run in one language would serve the
report of the last run in the other. The measurement version is raised
whenever a measurement starts to contain something new, which makes all
older entries stale at once. A cached entry written by a different
version of the program is ignored.

Every entry is written beside its place and then moved into it. A run
broken off halfway therefore leaves no half json to be read as a
measurement later.

## The order of work per video file

Per video file the run works in this order:

1. Which part of the audio has a counterpart in the picture? The rest
   falls away.
2. Align over envelopes against the camera's audio track.
3. Measure the clock drift and take it out, as far as the measurement
   carries; the picture is the reference.
4. Bring the audio to the start point and length of the picture, gaps
   filled with silence.
5. Reassemble: picture untouched (`-c:v copy`), the new audio as the
   first track, the camera track behind it, both named, timecode kept.
6. Measure again how far the new track lies against the camera track.

## How many processors are used

Half of the processors this process **may** use, at most four, never
more than there are files. A container or a taskset can hold the
process to two of thirty-two. Counting all thirty-two would mean
threads taking turns. Python 3.13 and newer answer that question
directly (`os.process_cpu_count()`); below it the machine's count has
to do.

## How a production at auphonic.com is created and started

The simple interface Auphonic offers for a single file has no field for
speech recognition. A production with a transcript is created first and
started second. For a single track the file goes to
`/api/simple/productions.json` together with preset and title, and
`action=start` is left out, so the production waits. The program then
reads the production back from `/api/production/<id>.json` and adds the
recognition to its own output files. It posts all of it in one call to
the same address, and that call starts the production.

For multitrack the recognition is already part of the create request to
`/api/productions.json`. The tracks follow through
`/api/production/<id>/upload.json`, and
`/api/production/<id>/start.json` starts the run.

Speech recognition is switched on with an empty service id, so
Auphonic's own Whisper does the work. Shownotes stay off, and the
language stays empty if none is set. Three output files are asked for
beside the audio: `speech` as json, `subtitle` as srt, `transcript` as
txt.

When the production is done, everything is downloaded into
`auphonic-tracks/`: the ZIP with the single tracks and every further
output file the production carries.

On the simple path every output the preset would fold to mono is
switched off: what a preset folds cannot be unfolded afterwards.

On a recompute the track settings are brought to the preset as well,
each through its own address (`.../multi_input_files/<Name>.json`).

## How the key reaches curl

The key reaches curl through a temporary config file. `mkstemp` creates
that file readable by its owner alone, and a `chmod` to `0600` says so
again for the reader. On Windows the `chmod` only toggles the read-only
bit, and the protection there comes from the temporary directory. The
file holds one line, `header = "Authorization: bearer <key>"`, and the
key goes in escaped. Backslash and quotation mark get a backslash;
carriage return and line feed are dropped. curl reads this file as
configuration. Without that escaping a quotation mark or a line break
inside the key would start a directive of its own.

The file is removed in a `finally`, whatever happened. If it cannot be
removed it is overwritten with a single line first, so a file left
behind no longer holds the key. A failure to remove it never replaces
the real error.

## Track names and the MOV target

The target is MOV for every run, MP4 sources included. MOV keeps a
track name of its own; MP4 throws it away and writes "SoundHandler"
regardless, so the tracks could not be told apart. MP4 also has no PCM
in the standard. Nothing is computed again: the picture is copied over
(`-c:v copy`) and the audio is written uncompressed. There is no
`--container`.

## How a file name with a clock in it is read

Blocks whose names carry a time of day are joined when one follows the
other within two seconds. Recorders write whole seconds and a block is
rarely a whole one long, which is where the slack comes from. Two
blocks that really follow one another are never further apart than
that. Six digits for the date or eight, six for the time, and the
calendar has to accept them. `Take_991399_120000` is not a date and is
not read as one. Two names spelling the same moment cannot be told
apart, so neither of them is taken, and that is said as well. `260808`
and `20260808` are the same day.

The "belongs to" chooser, which joins by hand what the search did not
find, asks that same `_joins_seamlessly` before it offers a target.
`join_barred` returns the ones it rules out and the reason, and
`choices_shut` greys those entries instead of dropping them: the answer
to "why can I not pick this" has to stand on the entry it is about.
Only where both sides carry a timecode -- without one there is nothing
to check, and that is what the chooser is for. `BLOCK_GAP_MAX_S` is the
fence, half an hour, because a clock is set wrong by whole hours and
half of the smallest of those catches every one while still letting a
real pause through. Joined over a gap of 12:19:48 the difference went
into the file as silence: 40 seconds of sound came out as 5.95 GB.

## How the colour tagging survives the copy

With `-c:v copy` ffmpeg rewrites the `colr` box from its own values and
replaces what it does not know. Transfer function 21 (Apple Log) comes
back out as an 18. Without `-movflags +write_colr` it writes no `colr`
box at all, and the values live only in the bitstream, where Resolve
does not look. So the script reads the box out of the source itself,
not through ffprobe. ffprobe reports names instead of numbers, and a
wrong name for what it does not know. The script passes the numbers on
explicitly (`-color_primaries`, `-color_trc`, `-colorspace`,
`-color_range`), forces the write and checks afterwards: log line
**Colour**.

ffmpeg throws the QuickTime keys of the container away
(`com.apple.quicktime.model`, `com.apple.quicktime.software`,
`com.blackmagic-design.camera.*`) without `-map_metadata 0 -movflags
+use_metadata_tags`. The script sets both.

## What makes a file count as HDR

Ungraded, Log looks flat and is easily taken for harmless SDR. It
carries the camera's full dynamic range all the same, and it bands in
eight bit.

The search through the QuickTime keys runs on word markers, not on
"log": that syllable hides in too many harmless words.

## How the `logs` atom is carried over

The atom sits in the picture description itself,
`moov/trak/mdia/minf/stbl/stsd/hvc1`.

ffmpeg cannot keep the atom. Its MOV *demuxer* does not know the box
type and never reads it in. Its *muxer* writes only `colr`, `pasp`,
`gama`, `btrt` and the codec's own box into a picture entry. There is
no switch for it.

So the script adds the atom itself after writing, byte for byte from
the source. That works only because ffmpeg puts `moov` at the end of
the file. Growing it there moves no media data, and the chunk offsets
in `stco`/`co64` stay valid. It keeps its hands off when

- `moov` is not the last box at the end of the file (as with
  `-movflags faststart`),
- a 64 bit box is in the chain,
- the picture entries are of different kinds, `hvc1` against `avc1`,
- the atom is over 64 KiB,
- or the atom is already there.

Afterwards it reads back:

- the top level boxes at the same offsets,
- `moov` grown and still ending at the end of the file,
- the chain down to the picture description readable again,
- every box inside its parent,
- the atom there.

On any mismatch the old `moov` comes back byte for byte.

## What stands in the project file

| Key | What |
|---|---|
| `format`, `version` | the naming (currently 3) and the version that wrote it |
| `files` | the list, each entry `{"path": ..., "kind": ...}` |
| `production`, `out_folder` | name and where it goes |
| `multitrack` | the tick, and with it the later tabs |
| `in_point`, `out_point` | the time window |
| `camera_cut`, `wide_at_edges` | every value of the camera cut |
| `assignment` | what is remembered per row and per file, each key by its prefix: `audio:` speaker name and camera, `video:` the name of the new video file, `own:` whether **Camera audio** is in use, `ownname:` the name that camera's track carries, `kind:` content, intro, outro or ignored, `voice:` the camera a separated voice sits on -- and `player_file`, `player_spot`, where the player stood |
| `preset` | the chosen Auphonic preset, or `no-auphonic` |
| `transcript`, `speech_language` | the transcript tick and the language tag |
| `apart`, `together` | blocks taken out by hand, and put together by hand |
| `channels` | the stereo ticks, per file and channel |
| `timeline`, `timeline_absolute` | the measured position of every file, and how fast its recorder ran |
| `call` | the command line of the last run |

The `assignment` cannot be guessed. `own:` holds only what somebody set
themselves; a **Camera audio** field that settled itself is derived
again at every start and leaves nothing behind. The `timeline` saves the
measurement at the next start.

Each `timeline` entry carries `path`, `mtime`, `size`, `start_s` and
`clock`. `clock` is the `b` of "recorder time = a + b * axis time", the
same figure the run takes out before it rewrites a track; it rides along
with the position because measuring it again costs the same minutes, and
a file that changed is caught by `mtime` and `size` anyway. It is not a
new format: an entry written before `clock` existed reads back as 1.0,
so an older project file opens and the axis in it still holds. The
format number stays 3.

## How a spot for the wide shot is scored

A sentence or a clause boundary near the wanted spot wins outright, and
nothing is weighed at all: `cut_point` answers and the search stops
there.

Only where there is no usable boundary does a score come in, over the
speech pauses lying in the stretch, and it is a sum of two:

- length of the pause, capped at 2 s, x3,
- distance from the wanted spot, measured against the shot length, x1.5,
  negative.

With no pause either, the spot is set by the clock: the stretch is
divided into even strides no longer than the latest a cut may come.

## How a heap of leftovers is found

Mean segment length under 1.5 s and a share under 10 % of the
recognised speech time.

## How restlessness is found

At least 7 camera changes in a sliding 12 second window.

## Where the wide shot comes in

The wide shot comes in at the first of these that is found, in both
directions:

1. a sentence beginning within +/-2 s,
2. a clause break within +/-2 s,
3. a sentence beginning within +/-5 s,
4. a clause break within +/-5 s.

The exact spot comes out of the audio. In a window of +/-0.5 s around
the target the script takes the dip. The threshold is
p5 + 0.30 * (p95 - p5) of the 10 ms levels in that window itself, and
the dip is chosen by width - 0.5 * distance. A fixed dB threshold fails
on quiet material.

## Where the wide shot goes out

At least 5 s, then to the end of the sentence; beyond that the last
clause break at or under 15 s.

## How the level curve is measured

ffmpeg rectifies the signal and samples it down to 100 Hz: two seconds
for one hour of audio, cached afterwards.

## Cutting when all speakers sit on one camera

With several speakers on one camera the cut has nothing to switch
between. The program cuts anyway, at the change of speaker.

## What the key figures compare

What counts is the distance between the cameras, so the figures are
measured against the mean of all cameras and not against a target.

## Where the preview takes its offsets from

A handover file carries `offset` per camera. A preview without a
handover file works from `start_s` per camera. The speaker segments
are stored raw in the time of their source file and converted where
they are used.

The offset is not the whole of it: **Measure speakers now** applies the
clock speed as well. The run takes it out by rewriting the audio; here
the level curve is resampled instead -- `clock_on_axis` stretches the
100 Hz curve by `b` before the tracks are laid on one grid -- which is
the same correction at the resolution the levels are read with. The
speed comes out of the axis, is kept in `state["axis_clock"]`, and is
read per file by `audio_clock_of`, which answers 1.0 where nothing is
stored.

Measured over an hour: without it the preview's edit points ran about
143 ms away from the run's, three to four frames; with it they stay
inside one frame. Which camera the cut goes to never changed -- the
gap was always far under the shortest shot.

## What the line on the third tab stands on

`state["cut_basis"]` is set on every pass of the preview, before
anything is computed: `"run"` where this window's own handover file was
read, `"auphonic"` where that run went over auphonic.com
(`state["run_auphonic"]`, held when **Start** is pressed, so turning the
preset box afterwards cannot change the answer), otherwise `"measured"`.
`cut_basis_line` turns it into the sentence and the colour -- warning
for `"measured"`, good for the other two.

The line stands whenever there are numbers. It gives way to who is still
unmeasured (`tracks_left`) and to the reason a measurement failed
(`measure_failed`); the button beside it comes and goes on `tracks_left`
alone. Before this it was overwritten 400 ms after the measurement, when
the preview timer next ran and hid the whole row.

## How a separation reaches the run

The assignment file carries `speakers_of` with the source, the names
and the segments in the time of the source file. The run knows from
the alignment where this file lies on the axis and computes
`(t - a) / b`.

Files are looked up over the real path: `/tmp` on macOS is a link to
`/private/tmp`.

## Where the minimum edit duration stands

The minimum edit duration stands at one place in the source, and
interface, switch and function defaults read that same value: 3.0 s.

## How the script talks to Resolve

The check runs in the background on the first look at the tab. A run
that ends by building a project should not find out at the end that
Resolve was never running.

Reports say that external scripting has been kept to the Studio edition
since version 19.1. There is no official statement. This is why the
program measures whether scripting answers instead of going by the
edition it finds.

The word "multicam" does not appear once in the README that comes with
Resolve's scripting interface. The words "transition", "dissolve" and
"fade" do not appear once in that documentation either. The dissolve is
therefore pulled by hand. The intro and outro clips lie over the
content instead of beside it, so that one drag on the upper corner is
enough.

## How the timelines are built

The cameras started at different times. Which part of each camera file
lands in the cut therefore comes from the measured offset, not from the
timecode.

A timeline destined to become a multicam clip has to look like this:
full length, uncut, one camera per video track. Each camera sits at its
measured place.

Conversion turns every audio track into an angle. The Full-Mix and the
camera microphone would become angles without picture, and SmartSwitch
would hear every speaker on every camera. The surplus audio is
therefore deleted after the insert.

Remote grades glue the **Clip** level together with the source file, so
a single cut can no longer be corrected on its own. The colour group
does the same work without giving up the clip level. The script sets
local versions on every run because a project from an earlier run would
otherwise still have remote grades on.

## Which frame rate counts where

Four rates have to be kept apart, and confusing two of them put every
shot of a mixed-rate cut in the wrong place -- twice, on two different
pairs.

`timeline_frame_rate` says what the timeline runs at: the highest `fps`
among the videos, with intro and outro dropped by path and a file set to
"ignore this video" never in the list to begin with. Where nothing is
left the reference clip decides, as before. It stands in for
`ref_clip[1]["fps"]` in `write_handover`, in `write_cut_list` and in the
timecode of the stored tracks. The reference clip still decides the time
axis, and the log still names it as the longest running time -- that is
a different question from the rate. Upwards Resolve repeats frames,
downwards it throws every fifth one away, so taking the highest loses no
picture.

`resolve_timeline_rate` puts that answer onto a rate Resolve offers a
timeline for. `RESOLVE_FRAME_RATES` holds the nineteen it has, read off
Resolve's own list, and nothing else is a project rate: measured on
21.0.4.5, 15 and 240 are refused, 16 and 120 are the two ends. So the
next rate **up** is taken, never the nearest -- upwards costs repeated
frames, downwards thrown-away ones -- and above 120 there is nothing
higher, which is the one place it goes down instead.

`known_frame_rate` answers which of those nineteen a reading means, or
`None`. The fence is relative (`FRAME_RATE_TOLERANCE`, one per cent),
because one frame at 120 is a fifth of one at 24: a container names its
rate to within a millionth, an averaged reading strays a few
ten-thousandths, and the nearest foreign rate lies four times further
out than that.

`own_frame_rate` is the rate a file's own frames are counted at, and it
is not the same question. Where the reading means one of Resolve's
rates, that is the answer; where it means none of them, **the reading
itself is**, and it is not moved to the nearest. A 15 fps file counts
fifteen frames to the second in its length, its timecode and its cut.
Rounding a foreign rate here was the fault behind the whole change: one
function answered both questions, so a 15 file had its timecode counted
at 16 frames to the second. `frames_to_timecode` and `timecode_to_frames`
go through `own_frame_rate` for that reason.

Nothing is refused for its rate. The file is read, placed and cut like
any other; only the timeline gets a rate Resolve has. Measured on
21.0.4.5, a 15 file in a 30 timeline sits within half a source frame at
every shot, with no gaps and the length exact; alone it gets a 16
timeline and keeps its length to the millisecond. `video_summary` puts
the note on the **Video** line of the file list where
`known_frame_rate` is `None`, and the time-base step says the same at
the file while it reads it.

`startFrame` and `endFrame` of an appended clip are frames of the source
file, counted at that file's own rate. Measured against Resolve
21.0.4.5: three clips at 24, 25 and 30 frames, each given
`startFrame=240`, answered `GetSourceStartTime` with 10.000, 9.600 and
8.000 seconds. `write_handover` therefore writes an `fps` into every
camera entry of the handover file, and `build_cut_timeline` carries one
rate per camera and counts the in point at that rate. Against the
timeline's rate a 24 camera in a 30 timeline showed a quarter of the
elapsed time too late, and its shots came out a quarter too long.
Measured over the round trip -- the cut list read back out of Resolve
and held against what went in -- six shots gave sixteen complaints
before and none after. The head cut of the Full-Mix runs at the rate of
the camera file it comes from for the same reason. The `offset` of a
camera goes the same way: `camera_place` reads the timecode of that
file, so it is handed that file's rate and no longer the reference
clip's.

`frames_of_the_file` turns a length in timeline frames into source
frames: the most that fit and never one more. Not every length is
reachable, because a 24 clip covers timeline frames of a 30 timeline in
steps of 1.25, so about one cut in five ends one timeline frame short.
The overrun was measured too and dropped: it closes that frame but moves
every following shot, and the moves accumulate over an hour into
seconds. One frame is the floor -- no picture at all is worse than one
frame too many.

`recordFrame` is the one number that really counts in timeline frames.
`build_camera_timeline` sends nothing else, which is why the multicam
timeline was right the whole time: measured, all three cameras placed at
+3.000 s kept their true running time in a 30 timeline.

The written camera files stay out of all of it. `write_camera_file`
copies the picture and takes the timecode from `info["fps"]`, the rate
of that file. Measured with ffprobe over eighteen written files: the
frame rate is the source's in every one, and where the head cut is not a
whole second the frame part of the timecode is the one that file's own
rate gives.

## German and English: what lives where

The whole source is English: names, messages, comments. German exists
only as translation strings, in `language/de.po` in the program's own
folder, keyed by the English text. That file is PO and holds no code at
all: one entry per message, `msgid` the English wording the program is
written in and `msgstr` what is said instead, so that a translator can
work in it without reading the program. Counted 6.9.2026: 1 531 `msgid`
lines beside the header entry, of which 1 491 carry a translation and
reach `CATALOGUE["de"]`. The two numbers are not the same reading, and
an entry left empty is not a fault -- the last paragraph of this
section says why.

`texts_of_language("de")` -- the project's own reader in
`language/__init__.py`, not `gettext` and not `polib`, and nothing is
compiled -- reads it out of the folder the program sits in, not by
import name: a program loaded from an absolute path, which is how every
test loads it, leaves its own folder off the search path.
What comes back is put into `CATALOGUE`, keyed by the language code.
`T()` looks a text up there; a missing entry shows English rather than
a gap.

`--lang de` or `--lang en` fixes the language of a run. Without the
switch `system_locale()` decides, from `LANGUAGE`, `LC_ALL`,
`LC_MESSAGES`, `LANG`, on macOS `AppleLocale`, on Windows
`GetUserDefaultLocaleName`. A run speaks one language. `--help` is the
exception: the help stays English, because those texts do not go
through `T()`.

Nothing a machine reads is translated: file names, folder names, track
names, the keys in the project and handover files, the column heads of
the CSV files. The keys are English (`speakers`, `cameras`, `length_s`,
`start_s`, `timeline`, `offset`), and the files carry `"format": 3`.
`format_complaint()` turns down anything older instead of reading a new
meaning into old names.

Numbers are split. On screen they follow the language (25,000 against
25.000, 1.2 s against 1,2 s), into files they always go English. One
helper in `workbench/` does all of it:
`number_text(number, places=1, plus=False)`,
where `places=None` means as many places as the number needs and
`plus=True` puts a sign in front of a positive one. The CSV files are
comma separated with a full stop as the decimal mark, in every
language: two runs have to stay comparable.

A further language is one file and one line: copy `language/de.po` to a
name carrying the new two-letter code, translate every `msgstr` and
leave every `msgid` as it stands -- it is the key -- and name that code
where the catalogue is filled at the end of the program --
`CATALOGUE["xx"] = texts_of_language("xx")`. `--lang` offers it
afterwards, and a system set to it picks it up by itself.

**A language file may be incomplete, and it still works.** Measured
4.9.2026: an entry that is not there falls back to the English source
text, and a language stands in `languages()` by nothing more than
having an entry in `CATALOGUE`. So a file with a fifth of its lines
translated is a usable language and can be filled in later; nothing
has to be finished before it is added.

The test suite is English throughout. `source_limits_hold_test.py` watches the
source: German comments, narrating comments, text lines over 79
characters, over-long blocks, over-long docstrings, docstring headings
without a full stop. The counters that are not about length stand at
zero and are held there. The two that are -- `long_blocks` and
`long_docstrings` -- do not: those are ratcheted down instead, because
the rule came in over a source that was already written. What each
stands at is in `tests/state/style_state.json`, which is where to read
it and not here.
