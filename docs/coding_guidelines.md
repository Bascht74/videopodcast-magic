# Coding guidelines

For `videopodcast-magic.py`. These grew out of the work on this program;
what is written here either proved right while building it, or was
learned by getting it wrong.

---

## 1. Language: English in the source, German in the catalogue

That is the one rule with two sides, and the two are never mixed.

**English, and never translated — everything only a programmer reads:**

- names of functions, variables, classes, parameters, constants
- comments in the code
- docstrings
- names of files and directories in the project
- messages to developers, in `assert` for example
- the column headings of the CSV files: they are read by other programs
  and compared across months, so they stay `Area`, `Metric`, `Before`

**English in the source, German from the catalogue — everything a user
sees:**

- every string that ends up in the log
- every label, every hint, every error message of the interface
- the help texts of the command-line switches
- `README.md` and the short description

The reason for the split: code is read by people who are at home in
English as their technical language, and it has to sit well with
third-party libraries, which carry English names anyway. What the user
reads should be in the user's own language — that is what the catalogue
at the end of the file is for, and today it holds German.

**The seam is always a quoted string.** A German word never appears in
an identifier, and it appears nowhere else in the source either: the
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
`measure_crosstalk` — not `do_gcc_phat_loop`.

**Functions are verbs, values are nouns.** `read_timecode()` returns
something; `timecode` is what came back.

**Abbreviations only where the field uses them.** `lufs`, `fps`, `tc`,
`db` are fine. `tmp_v_lst` is not.

**A leading underscore means: this concerns nobody outside this file.**

**No numbers in a name where a word hits it better.** `pass_two` says
nothing; `after_alignment` says it.

**One word, one thing -- and a qualifier makes it one.** A word may be
used for more than one thing as long as something in front of it says
which: `speech band`, `frequency band`, `progress bar`, `cut strip`.
What must not stand is the bare head word where two of them meet: a
plain `band` in a file that also draws a `bar` leaves the reader to
guess.

This works differently in the two languages, and both have to be right:

* **English puts the qualifier beside the word.** Two words, and the
  second may repeat elsewhere.
* **German writes it as one word.** `Schnittband`, `Frequenzband`,
  `Fortschrittsanzeige`. The qualifier is not beside the word, it is in
  it -- so a bare `Band` in the catalogue is ambiguous in a way that
  `cut strip` is not, and it has to be compounded.

**And the word has to be the one the field uses.** Not what translates
neatly from the other language: a term is looked up -- in the manual of
the program we work with, in the guidelines of the platform, in what
other tools of the trade call the same thing -- and only then chosen.
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

**Every number that is not obvious gets a sentence.** Why 9.5 dB and not
10? Why 40 dB below the peak? Whoever reads it in a year should not have
to work the number out again.

**What once went wrong stays in as a comment.** Not as an anecdote — as
a warning. "This looks redundant but is not, because …" is the most
valuable comment there is.

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
They are therefore **asked for at run time**, not written into the code:

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

**If something is not found, nothing is guessed in its place.** The log
then says what was on offer instead.

## 6. Docstrings

Every function that does more than one line gets one. First line: one
sentence on what it does. After that, where needed, a paragraph on the
why, on the limits of the method, and on what it returns.

What has no place in a docstring: a list of the parameters that only
repeats the signature.

## 7. Measure instead of assume

Where a number is needed, it gets measured. A timecode can be set wrong,
a nominal frame rate can differ from the real one, a preset can hold
something other than what its name promises.

And: **whatever was measured goes into the log.** A silent correction is
a trap for the next person who wonders about it.

## 8. Errors

**Check where the input happens, not where the run starts.** A message
after twenty minutes of computing is no help.

**A disabled button says why it is disabled.**

**Stop before anything costs.** Whatever costs money, credit or hours is
checked beforehand — not afterwards.

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
usually means a small script that builds a test file, runs the function
on it and holds the result against the expected value. Those scripts
belong in the project, not in a temporary directory.

**A rename is a change.** It gets checked too, name by name, not in one
sweep.

**No silent limits.** If something is cut off, shortened or skipped, it
goes into the log. Otherwise "done" reads like "complete".

**A test waits for a condition, never for a clock.** A fixed pause is
allowed while a test is being written and nowhere else. It costs time on
every run for ever, and worse, it makes the test lie in both directions:
too short and it fails on a busy machine, too long and nobody notices
that it is waiting for something that will never happen.

Measured on this suite: `channel_rows_test.py` spent 121 of its 123
seconds waiting for a tick on a row that never gets one -- it ran into
its own limit every single time and reported green afterwards. Asking
for the right condition brought it to 3 seconds. Three more tests were
built the same way; together they went from 112 seconds to 33.

The shape is always the same: a short interval, the condition, and an
upper bound so a slow machine does not turn red. What the condition has
to be is worth measuring -- put a probe on a copy and see when the thing
really happens, rather than guessing a number that looks safe.

## 11. Structure

**A function does one thing.** Once it runs longer than about 300 lines,
it is doing more than one.

**What belongs together stays together.** The video player is a video
player and has nothing to do with building the interface — so it lives
somewhere else.

**One thing lives in one place.** Two ways of computing the same result
drift apart sooner or later; that has happened twice in this program,
with the cut sliders and with the window arithmetic.

**Lines up to 79 characters.** Not out of nostalgia: when comparing, two
files side by side on one screen are worth more than long lines.

## 12. Interface

**The workflow is the order of the tabs.** Whatever comes first sits on
the left.

**Defaults should be right in nine cases out of ten.** What the default
is appears beside the field in grey.

**The impossible is not offered.** A field that changes nothing is worse
than a missing field.

**Buttons carry the action, not yes and no.** "Go ahead" and "Cancel",
not "OK" and "Cancel".

**No jargon in the interface**, except where it is the target program's
own term -- and then it has to be looked up, not assumed. "Edit Change
Delay" is called that because DaVinci Resolve calls it that; the manual has
it. Two others were put right the same way: "Cut in" and "Cut out" appear
nowhere in Resolve's manual, which says In point and Out point, and what we
called "Minimum shot length" is "Minimum Edit Duration" there. Both now
carry Resolve's name -- in the interface, on the switches and in the project
file.

**Long work shows a bar, and the bar does not lie.** It does not sit at
100 % while something is still running.

## 13. Changing something

**A change covers the case, not the instance that was reported.** What
comes back a second time cost twice: once to find, once to find again.
Six of these came back on one day, and every one of them was the same
mistake -- the reported half was mended and the other half left.

**Both directions.** A rule that decides between two answers has to
handle both. The colour space let the material win where the project
said SDR and the material was HDR, and said nothing in the other
direction -- so SDR material was delivered wrapped in HDR.

**Every place the same reasoning lives.** One word renamed in the
tooltip while the same collision stood in the palette and in the
progress code. One lookup by file name mended while three others still
looked up by file name. Before finishing, search the file for the
pattern, not for the line.

**Zero, one, two, many.** Two is where it breaks: two cameras writing
the same file name, two channels of one pair, two items on one track,
two files claiming the same moment. `sorted()` over `(track, item)`
pairs works until two items share a track -- then it compares the items
themselves and raises.

**Identify a thing by what it is, not by what it looks like.** A test
that found the progress bar by its height and width broke the moment
the bar was made wider; it now finds it by counting in thousandths,
which is what that bar *is*. The same goes for the code: look things up
by their path, not by their name.

**Say where the rule stops.** A rule without a boundary is applied
where it does not belong. "In a project we created ourselves" is the
boundary of the colour space rule, and it is written next to it.

**Where the general case is by-catch, take it along. Where it is a
decision, ask -- once, with the options, before building.** By-catch is
what costs no rebuild and changes nothing anybody would notice: the
crash when two clips share a track, the second lookup that goes by name.
A decision is what changes the material, the delivery or the way
somebody works: that SDR sources would come out as SDR from now on is
not a detail, it is a different result from the same button.

Ask before building, not after the next failure. A question costs a
minute; a second pass over the same code costs an afternoon, and the
second answer is rarely different from what the first question would
have got.
