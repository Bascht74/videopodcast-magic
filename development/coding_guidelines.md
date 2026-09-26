# Coding guidelines

For the folder `videopodcast_magic/` and the text files in it. These grew
out of the work on this program. What is written here either proved
right while building it, or was learned by getting it wrong.

---

## 1. Language: English in the source, German in the catalogue

That is the one rule with two sides, and the two are never mixed.

**English, and never translated.** Everything only a programmer reads:

- names of functions, variables, classes, parameters, constants
- comments in the code
- docstrings
- names of files and directories in the project
- messages to developers, in `assert` for example
- the column headings of the CSV files: they are read by other programs
  and compared across months, so they stay `Area`, `Metric`, `Before`

**English in the source, German from the catalogue.** Everything a user
sees:

- every string that ends up in the log
- every label, every hint, every error message of the interface
- the help texts of the command-line switches
- `README.md` and the short description

The reason for the split: code is read by people who are at home in
English as their technical language. It also has to sit well with
third-party libraries, which carry English names anyway. What the user
reads should be in the user's own language. That is what the catalogue
is for. It stood at the end of the program until 4.9.2026 and lives in
the folder `language/` beside it now, in a PO file of its own per
language -- `language/de.po` is the German one, `msgid` the English
wording and `msgstr` what is said instead.

**The seam is always a quoted string.** A German word never appears in
an identifier, and it appears nowhere else in the source either. The
German lives in the catalogue, keyed by the English wording.

```python
# right
def measure_crosstalk(tracks, rate=16000):
    """Measure how loud each voice appears in the other microphones."""
    ...
    print(T("  Bleed:  %.1f dB quieter") % separation)

# wrong: German name
def uebersprechen_messen(spuren):

# wrong: German message in the source
print("  Übersprechen:  %.1f dB leiser" % separation)
```

## 2. Names

**A name says what a thing is, not how it is made.**
`measure_crosstalk`, not `do_gcc_phat_loop`.

**Functions are verbs, values are nouns.** `read_timecode()` returns
something; `timecode` is what came back.

**Abbreviations only where the field uses them.** `lufs`, `fps`, `tc`,
`db` are fine. `tmp_v_lst` is not.

**A leading underscore means: this concerns nobody outside this file.**

**No numbers in a name where a word hits it better.** `pass_two` says
nothing; `after_alignment` says it.

**One word, one thing, and a qualifier makes it one.** A word may stand
for more than one thing. Something in front of it has to say which:
`speech band`, `frequency band`, `progress bar`, `cut strip`. What must
not stand is the bare head word where two of them meet. A plain `band`
in a file that also draws a `bar` leaves the reader to guess.

This works differently in the two languages, and both have to be right:

* **English puts the qualifier beside the word.** Two words, and the
  second may repeat elsewhere.
* **German writes it as one word.** `Schnittband`, `Frequenzband`,
  `Fortschrittsanzeige`. The qualifier is not beside the word, it is in
  it. A bare `Band` in the catalogue is therefore ambiguous in a way
  that `cut strip` is not, and it has to be compounded.

**And the word has to be the one the field uses.** Not what translates
neatly from the other language. Look the term up before choosing it:

* in the manual of the program we work with,
* in the guidelines of the platform,
* in what other tools of the trade call the same thing.

A word invented here, or carried over from German because it sounds
close, costs every reader the same moment of doubt.

## 3. Comments

**A comment explains the why, not the what.** What happens is in the
code; why it happens this way and not another way is known only to
whoever was there.

```python
# right
# ffprobe returns frames in decode order, which is not display order for
# H.264 with B-frames. Sorting first, otherwise we would measure the codec's
# GOP structure and call it a variable frame rate.
timestamps.sort()

# wrong
# sort the timestamps
timestamps.sort()
```

**Every number that is not obvious gets a sentence** -- why this
threshold and not a rounder one. The sentence is general: the reason,
not the run it came out of. The measurement itself lives in
`docs/notes/`.

**What once went wrong stays in as a warning, not as a history.** "This
looks redundant but is not, because …" is the most valuable comment
there is. "This was tried on such a date and reverted" is not: that
belongs in the commit message and in `docs/notes/`.

**Nothing dated, nothing named, nothing worked out as an example.** No
date, no person, no file, no measured figure. All of it ages, and none
of it helps somebody reading the line. Say the rule the measurement
produced.

**How long.** A comment block: **four lines.** A docstring: **eight**,
counted with its first line and its blank lines. Above that, either it
is saying what the code says, or it is telling a story, or two comments
have been written as one.

The exception is a section heading that teaches a reader how to do
something -- how a language is added, how a file format is laid out.
That is documentation and may be as long as it has to be.

**Half of it is not in the length.** Capping the two limits above cuts
about a fifth. The rest comes from deleting what the code already says,
what happened once, and what was measured where. That part is read line
by line; no rule finds it.

**A commit message follows the same rules.** A heading and a handful of
lines: what changed and why, not the road that led there. Where several
things changed, a list of one line each beats a paragraph apiece. The
measurements and the wrong turns belong in `docs/notes/`.

**No anecdotes.** No reference to a particular recording, no names of
people, no drive paths. Whatever one example taught is written down in
general terms:

```python
# right
# Recorders are set to different gains; a fixed threshold would treat the
# loudest track as always active and the quietest as never.

# wrong
# In interview 2 the candidate sits 13 dB above the other two.
```

## 4. Short and to the point

Applies to all of it: comments, docstrings, messages, help texts,
documentation.

**One thought, one sentence.** Anyone who needs three sentences to
justify a number has not found the justification yet.

**No storytelling.** Not "This is written down nowhere; it came out of
looking at the timeline", but "endFrame counts exclusively".

**No examples from actual runs.** No interview, no speaker, no file
name, no drive, no date. Whatever they taught is said in general terms.

**No justification.** The code does not have to defend itself. "Both are
defensible, so it is adjustable" becomes "adjustable".

**Messages: what the situation is, and what to do about it.** No more.

```
right:  Two cameras would produce the same file: Episode12_Hosts
wrong:  Careful, something has turned up here that is easy to miss:
        two of the cameras are apparently meant to produce the same
        file, and that would mean the second overwrites the first.
```

The limit: it has to stay understandable. Short does not mean cryptic.
If one more sentence is what it takes for someone to understand the
place, then it is there.

## 5. Never guess, always look

The most important rule when dealing with other people's programs.

The names of formats, codecs, colours and settings in third-party
software are undocumented, or they change from one release to the next.
The program therefore **asks for them at run time** and does not write
them into the code:

```python
# right
formats = project.GetRenderFormats()
name, key = first_match(formats, ["mp4"])
if not key:
    print(T("    No MP4 format found. Available: %s") % ...)
    return False

# wrong
project.SetCurrentRenderFormatAndCodec("mp4", "H264")
```

The same goes for values you want to set: set them, read them back,
compare, and write into the log what actually arrived.

**If something is not found, the program guesses nothing in its
place.** The log then says what was on offer instead.

## 6. Docstrings

Every function that does more than one line gets one. First line: one
sentence on what it does. After that, where needed, a paragraph on the
why, on the limits of the method, and on what it returns.

What has no place in a docstring: a list of the parameters that only
repeats the signature.

**A note saying a step is red goes out in the commit that makes it
green.** Not in the next clean-up pass. A test written while the fault
still stands describes the fault; if the fix lands in the same commit,
the sentence is untrue the moment it is written, and it stays untrue
for as long as nobody rereads it. Whoever comes next believes it and
leaves a working check alone.

And a note that is gone is no proof the check under it still bites.
That proof is a broken copy and a red line naming the fault.

## 7. Measure instead of assume

If a number is needed, it gets measured. A timecode can be set
wrong. A nominal frame rate can differ from the real one, and a preset
can hold something other than what its name promises.

And: **whatever was measured goes into the log.** A silent correction is
a trap for the next person who wonders about it.

## 8. Errors

**Check where the input happens, not where the run starts.** A message
after twenty minutes of computing is no help.

**A disabled button says why it is disabled.**

**Stop before anything costs.** The program checks whatever costs
money, credit or hours beforehand, not afterwards.

**`except` catches nothing unless it has to.** An error caught and
reported to nobody is worse than a crash: the result is then wrong
rather than absent. If it is caught, then narrowly and with a message.

## 9. Credentials

A key **never** appears in the code, never in a project file, never in
the log and never in the process list. It comes from the system
keychain, from the registry or from an environment variable. If it is
handed to another program, then through a file with mode 0600, not as an
argument.

Whenever a project file or a hand-over file is written, anything that
could be a key is explicitly filtered out.

## 10. Verifiability

**Every change comes with a way to check it.** For this program that
usually means a small script. It builds a test file, runs the function
on it and holds the result against the expected value. Those scripts
belong in the project, not in a temporary directory.

**A rename is a change.** It gets checked too, name by name, not in one
sweep.

**No silent limits.** If something is cut off, shortened or skipped, it
goes into the log. Otherwise "done" reads like "complete".

**A test waits for a condition, never for a clock.** A fixed pause is
allowed while a test is being written and nowhere else. It costs time
on every run for ever. Worse, it makes the test lie in both directions.
Too short and it fails on a busy machine; too long and nobody notices
that it is waiting for something that will never happen.

Measured on this suite: `table_row_per_channel_test.py` spent 121 of its 123
seconds waiting for a tick on a row that never gets one. It ran into
its own limit every single time and reported green afterwards. Asking
for the right condition brought it to 3 seconds. Three more tests were
built the same way; together they went from 112 seconds to 33.

The shape is always the same: a short interval, the condition, and an
upper bound so a slow machine does not turn red. What the condition has
to be is worth measuring. Put a probe on a copy and see when the thing
really happens, rather than guessing a number that looks safe.

## 11. Structure

**A function does one thing.** Once it runs longer than about 300 lines,
it is doing more than one. One function in this program breaks that
knowingly; section 12 says which one, why, and what still holds inside
it.

**What belongs together stays together.** The video player is a video
player and has nothing to do with building the interface, so it lives
somewhere else.

**And when something moves house, the subject decides, not the price.**
A move out of one piece into another costs crossings at the seam --
head lines, forced `PROGRAM.` reads, a name bound back -- and
`development/price.py` counts them. **That number says what the move
will cost. It never says whether the move is right.** What belongs to
the same subject goes, even where it costs; what does not, stays, even
where it would be free.

Measured 7.9.2026, and it is written down because it nearly went the
other way: `make_project_file` was to be moved into `cut/` because that
cost four crossings while `filing/`, where a project file actually
belongs, cost thirteen. Both were wrong. The project file's own
business -- writing it, reading it back, finding it, offering it, and
what becomes of the work before the window is rebuilt -- is a subject,
and a subject gets a piece.

**So a report on a cut names what a number buys in the same breath.**
"Three crossings more" on its own teaches whoever reads it that
crossings are the point. "Three crossings more, and the project file is
in one file instead of three" says what happened.

**And the seam that is not made of names is the wider one.** Every
piece reaches into one untyped record, `state`, by string key.
`development/seam.py` counts it: **98 keys, 61 of them touched by more
than one piece, 45 crossing the boundary of the window** on 7.9.2026.
A name that crosses stands in a head line and can be seen; a key does
not. `state["speakers_local"]` written in one piece and read in five
others is an agreement between six files that nothing declares and
nothing checks.

**Splitting a file does not narrow that seam, and moving a reader does
not either -- it moves it.** This paragraph said the opposite for half a
day, and the move it named as the example is the one that disproved it.
Measured: the speakers' window part went out of `ui/` into `speakers/`,
and the crossings of the window's boundary rose **45 to 49**, the shared
keys **61 to 66**. Two keys stopped crossing, because the moved code was
the only thing in `ui/` that touched them. **Six started**, because
`ui/` alone had touched them and now two pieces do.

**That is not a fault in the move. It is what a shared record does when
a subject gets whole**: putting the window part beside the logic it
shows means two files reach into the same keys. The seam widens because
the subject stopped being split, which is the thing that was wanted.

So the number measures the record, not the cut. It belongs in a report
beside the crossing count, and it says one useful thing there -- how
much of the program's coupling this move did *not* touch. **It must
never become a ratchet**: a ratchet on it would forbid exactly the moves
that put a subject in one file. What would really narrow it is work on
`state` itself, giving its keys owners, and that is a different job from
moving code.

**One thing lives in one place.** Two ways of computing the same result
drift apart sooner or later. That has happened twice in this program,
with the cut sliders and with the window arithmetic.

**Lines up to 79 characters.** Not out of nostalgia: when comparing, two
files side by side on one screen are worth more than long lines.

## 12. The window, and where Qt is loaded

**`gui()` is still one long function, and it is being rebuilt into
components**: a `MainWindow` class, one piece per tab, and a
`ProjectModel` holding what the tabs share. Until that is done,
`gui()` is the one function that breaks section 11 knowingly.
`source_limits_hold_test.py` prints its size on every run, so the
number is read there and not here.

**The command line loads no Qt, and it stays that way.** `--help`,
`--version`, `--hdr-check` and a real `--dry-run` load no PySide6
module -- and still none with `from PySide6 import QtWidgets` and a
widget class at the top of `ui/`, because `ui/` is only read in
`window()`, when the window opens. The same lines at the top of
`player/`, `fittings/` or `tables/` load Qt on every call, because the
way in reads those pieces for every run. So:

- **Qt may be imported at the top of `ui/`, and of any piece only the
  window reads.** A widget class may stand at module level there; it
  needs no factory around it.
- **In a piece the command line reads, Qt stays inside the function
  that needs it.** `run_choice_kept_test.py` holds that reading and
  writing a setting loads no Qt.

**A class is not a split by itself.** Moving `gui()` into a class one
for one -- every inner function a method, every captured name an
attribute -- leaves every method free to touch every attribute. It
brings the largest function down and leaves the structure where it was.
So `source_limits_hold_test.py` holds classes the way it holds
functions: the largest class as a number, and every class over 300
lines by name. A component counts when it owns its data and the others
reach it through what it offers, not through its fields.

**What holds meanwhile.**

- **New code that gets by without a widget does not go into the
  window.** Computation, checking, preparation: it is written beside the
  window and takes what it needs as an argument.
- **No `nonlocal`, anywhere in the program.** Shared mutable state runs
  through named containers -- the `state` dictionary, the `Value`
  objects, and the model once it exists -- never through rebinding a
  name.
- **A helper inside `gui()` that captures nothing is in the wrong
  place.** Whether it captures anything has an exact answer:
  `co_freevars` of the compiled function, not a search through the text.
- **The numbers go down, never up.** The ratchets in
  `tests/state/style_state.json` are the record.

## 13. Interface

**The workflow is the order of the tabs.** Whatever comes first sits on
the left.

**Defaults should be right in nine cases out of ten.** What the default
is appears beside the field in grey.

**The program does not offer the impossible.** A field that changes
nothing is worse than a missing field.

**Buttons carry the action, not yes and no.** "Go ahead" and "Cancel",
not "OK" and "Cancel".

**No jargon in the interface**, except where it is the target program's
own term. Then it has to be looked up, not assumed. "Edit Change Delay"
is called that because DaVinci Resolve calls it that; the manual has
it. Two others were put right the same way. "Cut in" and "Cut out"
appear nowhere in Resolve's manual, which says In point and Out point.
What we called "Minimum shot length" is "Minimum Edit Duration" there.
Both now carry Resolve's name: in the interface, on the switches and in
the project file.

**Long work shows a bar, and the bar does not lie.** It does not sit at
100 % while something is still running.

## 14. Changing something

**A change covers the case, not the instance that was reported.** What
comes back a second time cost twice: once to find, once to find again.
Six of these came back on one day, and every one of them was the same
mistake. The reported half was mended and the other half left.

**Both directions.** A rule that decides between two answers has to
handle both. The colour space let the material win where the project
said SDR and the material was HDR, and said nothing in the other
direction. SDR material was therefore delivered wrapped in HDR.

**Every place the same reasoning lives.** One word renamed in the
tooltip while the same collision stood in the palette and in the
progress code. One lookup by file name mended while three others still
looked up by file name. Before finishing, search the source for the
pattern, not for the line -- and the source is the whole folder
`videopodcast_magic/`, not just the big file in it.

**Zero, one, two, many.** Two is where it breaks. Two cameras writing
the same file name, two channels of one pair, two items on one track,
two files claiming the same moment. `sorted()` over `(track, item)`
pairs works until two items share a track. Then it compares the items
themselves and raises.

**Identify a thing by what it is, not by what it looks like.** A test
that found the progress bar by its height and width broke the moment
the bar was made wider. It now finds it by counting in thousandths,
which is what that bar *is*. The same goes for the code: look things up
by their path, not by their name.

**Say where the rule stops.** A rule without a boundary is applied
where it does not belong. "In a project we created ourselves" is the
boundary of the colour space rule, and it is written next to it.

**If the general case is by-catch, take it along. If it is a decision,
ask once, with the options, before building.** By-catch is what costs
no rebuild. It changes nothing anybody would notice: the crash when two
clips share a track, the second lookup that goes by name. A decision is
what changes the material, the delivery or the way somebody works. That
SDR sources would come out as SDR from now on is not a detail. It is a
different result from the same button.

Ask before building, not after the next failure. A question costs a
minute. A second pass over the same code costs an afternoon. The second
answer is rarely different from what the first question would have got.
