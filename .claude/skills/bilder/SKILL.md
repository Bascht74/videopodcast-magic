---
name: bilder
description: The window has changed and the pictures in the manual show a state that no longer exists, or a release is coming up and the pictures belong to it.
---

# The pictures in the manual

Every picture exists twice: English as `docs/images/NAME.png`, German as
`docs/images/NAME.de.png`. None of them is taken by hand.
`docs/notes/shoot_screenshots.py` loads `videopodcast_magic.py` as a
module, opens a project built from the test fixtures, steps through the
tabs and saves `window.grab()`. No desktop in the frame, no foreign
window, and repeatable at any time.

**`docs/notes/bilder.md` is the fuller source.** It says of every
picture what can be seen on it and **which change to the window makes it
invalid**. That folder is deliberately not shipped -- it holds material
from real productions -- so anybody who clones this repository works
from this file alone. Every command and every condition is written out
here. What is missing without the note is only the list of which change
invalidates which picture; that has to be worked out from the finished
pictures themselves.

## When they are taken: once per version

**Not after every change, but before every release.** The window moves
often; on a single day it changed three times. Whoever photographs each
time photographs twice for nothing and asks three times for the screen.

**In between: an outdated picture is noted, not replaced on the spot.**
A note costs nothing and does not get lost; a picture pass costs the
screen two to three minutes. Before the release then all of them at
once -- ask, shoot, bring the descriptions up to date, check in.

## What the pass needs

* **A logged-in graphical session on this Mac, from the terminal.** The
  platform is `cocoa`, and it talks to the window server. Over SSH, or
  without a logged-in screen, there is no picture; the script stops
  rather than quietly delivering the Fusion look.
  `VPM_SHOT_PLATFORM=offscreen` is an emergency exit for somebody
  without a Mac who needs a picture at all -- its pictures must **not**
  go into the manual.
* **Ask first.** The picture pass is not a background pass. The window
  itself stays off the desktop (`WA_DontShowOnScreen`), but the
  application activates itself at start and macOS jumps to its space. So
  not in the middle of a full screen, and not while somebody is working
  at the machine.
* **The fixtures.** `cd tests && bash fixtures.sh` builds
  `/tmp/vpm-fixtures-<uid>/interview` (for `main` and `split`) and
  `/mixer` (for `channels` only).
* **PySide6**, and `ffprobe` on the path -- the latter only for the
  `channels` set.

## The commands

```bash
cd tests && bash fixtures.sh          # builds /tmp/vpm-fixtures-<uid>/interview and /mixer
mkdir -p /tmp/vpm_shots && cp docs/notes/shoot_screenshots.py /tmp/vpm_shots/
cd /tmp/vpm_shots
for s in main split channels; do for l in en de; do
  VPM_SHOT_SET=$s LANGUAGE=$l python3 shoot_screenshots.py
done; done
```

What each set delivers:

| Set | delivers |
|---|---|
| `main` | `files`, `blocks`, `assignment`, `resolve-cut`, `settings` |
| `split` | `voices` |
| `channels` | `channels` |

The terminal picture comes from a second script, `shoot_terminal.py`,
through `VPM_SHOT_TERMINAL_LANG`. It needs an **unlocked** screen, or
`screencapture` hands back nothing.

**The smallest unit is one set in one language, not one picture.**
Whoever needs only `resolve-cut` runs `main` and gets `files`, `blocks`,
`assignment` and `settings` along with it. That is harmless, because the
pass is repeatable -- unchanged pictures come out byte for byte the
same. Six passes together: about two and a half minutes.

## The choosing happens when copying, not when shooting

**Copy only what has really changed.** Compare the checksum first:

```bash
shasum -a 256 /tmp/vpm_shots/png_en/NAME.png docs/images/NAME.png
cp /tmp/vpm_shots/png_en/NAME.png docs/images/NAME.png
cp /tmp/vpm_shots/png_de/NAME.png docs/images/NAME.de.png
```

The output folder is called `Result` in the English pass and `Ergebnis`
in the German one: a German word in an English window reads as a mistake
in the manual.

## Look at them, do not just produce them

**The set is bounded by the checksum comparison above: every picture
whose sum moved is looked at in both languages, and the answers are
written down.** "Look at them" gets skipped; six questions with answers
do not. The first four each caught a fault no test had; 5 and 6 are
there to stop the next one.

1. **Is a label cut off, is anything overlapping?** The German sentence
   is the longer one; what fits in English says nothing. Four German
   buttons and a checkbox wanted a measured 548 px in a row of about
   480 px. **Ask it again after the correction** -- the first attempt, a
   minimum width, turned cut off into overlapping, and without the second
   picture that would have passed as fixed. Only a row of its own solved
   it, the same way in **both** languages.
2. **Does every word on it come out of the right catalogue?** A checkbox
   saying „mit Channel 2 zusammenlegen" stood next to rows called
   „Kanal 1": three catalogue entries left in English.
3. **Does every sentence assembled from pieces parse?** „Der Schlüssel
   geht nie in eine Datei" was built from building blocks and took the
   wrong article.
4. **Is anything on it out of the list below that may appear on no
   picture?** Once the settings window came out with a filled field
   **API Key** and a ticked **Im Schlüsselbund speichern** -- the program
   had fetched the key from the Keychain at start. Noticed by looking,
   not from the return code.
5. **Does it show the program prettier than it is?** A label that is cut
   off gets fixed in the program, never widened in the shooting script.
6. **Did it change for the reason you expected?** A sum that moved where
   nothing was touched is itself the finding -- a picture pass that
   catches something nobody asked for is the return on the whole pass.

**One line per changed picture goes into the release report:** the name,
both languages, and what was found. "Nothing" is an answer; a pass that
names no picture has not been made.

Hence the three nets in the script: `load_api_key` returns empty,
`AUPHONIC_TOKEN` is cleared out of the environment, and the three
`speaker_split_*` are replaced. **A picture pass reads no key, computes
no separation and installs nothing.** Before anybody removes one of
them, they have to know what stands in the picture afterwards.

**What may appear on no picture** (question 4): real production names,
real presets or production IDs, paths from a private disc, people's
names, a key. Only fixture names and `/tmp` paths.

## Afterwards, note what has become invalid

After the pass, record for every picture **which change to the window
invalidated it** and what can be seen on it now. Without that note,
nobody knows next time what has to be brought up to date.

The place for it is `docs/notes/bilder.md`. If the note is not on the
disc, the same record belongs in the release report -- what it must not
do is get lost.

## What moves no picture

**A change to the menu.** On the Mac, Qt hangs the menu bar at the top
edge of the screen rather than in the window, and `window.grab()` takes
only the window. So a new menu entry makes no picture invalid.

The same holds for anything that touches only the command line, the log
or the handover, and for every state the picture pass does not set up.

## When a window may be visible

**Only for the picture pass** -- that is what it is for. The normal case
is still `WA_DontShowOnScreen`: it costs a measured 0.43 % of the pixels
and puts nothing on the desktop.

**Everything else -- measurements, the suite, trial runs, checks -- never
visible.** `WA_DontShowOnScreen`, and where that is not possible,
`QT_QPA_PLATFORM=offscreen`. That this yields the Fusion palette does
not matter for a measurement; for a picture it would be a fault.

Whoever is unsure takes the invisible form. A picture that is 0.43 % off
is better than an interruption.
