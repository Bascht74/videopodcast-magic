# All switches

*Auf Deutsch: [command-line.de.md](command-line.de.md). Back to the
[contents](README.md).*

`--help` prints this list too, always in English. Defaults in brackets.
A switch that works on one path only carries `[multitrack only]` or
`[simple path only]`, here and in `--help`; both markers stay English
whatever the language of the run.

![The start of a run in the terminal](images/terminal.png)

*`--multitrack --lufs -16 --dry-run` at the end of the call, the version
and the Python underneath, then the preflight with seven checks and two
hints. Without a key the multitrack run stops there.*

## Basics

| Switch | Does |
|---|---|
| `--lang {de,en}` | language of the messages (system language) |
| `--out FOLDER` | where the results go (next to each video) |
| `--suffix TEXT` | added to the file name (`_audio`) |
| `--name-camera TEXT` | name of the camera track (`Camera Original`) |
| `--parallel COUNT` | this many video files at once; 0 decides for you, 1 one after another (0)  `[multitrack only]` |
| `--dry-run` | only measure and report, write nothing |
| `--version` | version number, and the Python this runs on |
| `--no-update-check` | stop looking whether a newer version is out; the answer is remembered (it looks) |
| `--update-check` | look again, after `--no-update-check` was given at some point |

## What happens to audio and picture

| Switch | Does |
|---|---|
| `--no-camera-audio` | drop the camera's own audio instead of keeping it |
| `--no-follow-ups` | do not look for numbered continuation files (it looks for them) |
| `--together FILE ...` | these files are one recording, in this order; repeatable. The run sorts the other files by name and leaves the group untouched: one block at the first of its names |
| `--apart FILE` | this block stands on its own, whatever its name says; repeatable |
| `--transcript` | have auphonic.com write down what is said: json, srt and txt |
| `--no-single-tracks` | only the mix into the video, not the recordings beside it  `[simple path only]` |
| `--no-drift` | measure clock drift and report it, but do not take it out |
| `--tc HH:MM:SS:FF` | start timecode of the picture, if the camera wrote none or a wrong one (from the video file) |
| `--fps NUMBER` | frame rate to assume, if ffprobe reports a wrong one (from the video file) |
| `--lufs NUMBER` | loudness target in LUFS for the sum of the speaker tracks; lower is quieter, the usual targets lie between -23 and -14. Without it nothing is adjusted: the sound is taken from the source files as it is (none) |
| `--speech-language CODE` | language tag of the audio tracks, ISO 639-2/B: `ger`, `eng`. Careful, ffmpeg drops `deu` silently (none) |
| `--speech-language-camera CODE` | the same for the camera track (none: that is what tells the two apart in the QuickTime audio menu) |
| `--speakers-local FILE` | take that recording apart by voice on this machine, and cut by the result (the recording the run picks itself) |
| `--speakers-from FILE` | take a finished separation out of a project or assignment file instead of computing one (none) |
| `--speakers-count NUMBER` | how many people `--speakers-local` should find (work it out) |
| `--no-speakers-local` | never take a recording apart by voice in this run (off) |
| `--no-speech-recognition` | do not write down what is said; the cut then has no sentence boundaries (off)  `[multitrack only]` |
| `--no-transcript-file` | write no transcript beside the result; the words that were heard normally go into the output folder as json, srt and txt (off)  `[multitrack only]` |

## Processing at auphonic.com

| Switch | Does |
|---|---|
| `--auphonic-api-key KEY` | key from the account settings; turns processing on. Without files it only lists the presets |
| `--auphonic-preset NAME` | preset name or id (the program asks) |
| `--auphonic-wait SECONDS` | how long to wait (7200) |
| `--auphonic-resume WHAT` | production already there: `result`, `rerun`, `adopt`, `upload`, `abort` (the program asks)  `[multitrack only]` |
| `--auphonic-done FOLDER` | tracks already processed, named after the speakers. The run takes them from there instead of uploading them, and the account keeps its credit  `[multitrack only]` |
| `--multitrack` | every audio file as its own track, so auphonic.com can take the bleed out. Needs a multitrack preset |
| `--assign FILE` | JSON saying which audio belongs to which camera; the interface writes it  `[multitrack only]` |
| `--without-auphonic` | align, mix and write locally, camera cut from our own speech detection |

## Setting the time window

| Switch | Does |
|---|---|
| `--in-point TIME` | start: `17:20:14` absolute, `+12:30` or `90` from the start of the window (from the video files) |
| `--out-point TIME` | end, same notation; `-30` counts back from the end (from the video files) |

## Steering the camera cut

| Switch | Does |
|---|---|
| `--min-edit-duration SECONDS` | shortest a shot may stand; shorter ones merge into the one that follows, 0 off (3) |
| `--min-speech-to-switch SECONDS` | how long somebody has to hold the floor before the camera follows them, 0 off (1.5) |
| `--edit-change-delay SECONDS` | how much later than the audio the picture cuts; negative lets it lead (0.3) |
| `--reaction-lead SECONDS` | how much earlier the picture goes to the answer after a question (1.5) |
| `--reaction-gap SECONDS` | how soon the answer has to follow the question for the reaction cut to fire (3) |
| `--reaction-hold SHARE` | how much of the ten seconds after the question the answering speaker has to hold, between 0 and 1 (0.7) |
| `--on-monologue VALUE` | one person holds the floor longer than `--wide-after`: `wide`, `listener`, `alternate`, `hold` (alternate) |
| `--on-together VALUE` | several speak at once and no camera shows exactly them: the same four values (wide) |
| `--on-uncertain VALUE` | the recognition is uncertain: the same four values (wide) |
| `--on-question VALUE` | after a question: `off`, `answer`, `listener` (answer) |
| `--wide-shot FILE` | this video file is a wide shot: a camera nobody sits in front of, it takes no speaker; repeatable. Without it the cameras with no speaker assigned are the wide shots |
| `--wide-after SECONDS` | from this hold time on the program breaks the shot up at a sentence boundary, not by the clock, 0 off (70) |
| `--wide-length SECONDS` | how long the interposed shot stands at least; it then runs to the end of the sentence (5) |
| `--wide-most SECONDS` | how long it stands at most; if the end of the sentence lies beyond it, the last clause break before it ends the shot (15) |
| `--wide-latest SECONDS` | longest one camera may stand without a cut (120) |
| `--no-wide-edges` | do not hold the wide shot over the greeting and the goodbye |

## Steering the preflight and the metrics

| Switch | Does |
|---|---|
| `--no-preflight` | skip the check before the first long step |
| `--preflight-again` | measure again instead of taking the stored measurement |
| `--anyway` | run even if the preflight found a reason to stop |
| `--no-metrics` | no metrics and no colour comparison at the end  `[multitrack only]` |

## Adding intro and outro

| Switch | Does |
|---|---|
| `--intro FILE` | laid over the beginning, on the second picture and audio track. Neither aligned nor processed |
| `--outro FILE` | the same for the end; starts where the last word ends |

## Working with DaVinci Resolve

| Switch | Does |
|---|---|
| `--resolve` | afterwards build the project and the timelines. Resolve has to be running |
| `--resolve-json FILE` | only the Resolve part, from a `..._resolve.json` that is already there |
| `--resolve-project WHAT` | project already there: `update`, `keep`, `new`, `abort` (the program asks) |
| `--resolve-audio-tracks` | only print the audio mapping of the open project; the program reads it and leaves it as it is |
| `--hdr-check FILE` | only look whether a finished file carries everything that marks it as HDR |

That is every switch. The chapter a switch belongs to also names the
field in the window that sets it; the [contents](README.md) lists the
chapters.

## When something goes wrong

* **A switch the program does not know.** The run stops before
  anything happens and prints the whole list of switches. Compare the
  spelling with the tables above.
* **A value with a space in it.** Put it in quotes:
  `--auphonic-preset "<name of the preset>"`. Without them the second
  word arrives as a file name.
* **`--multitrack` without a key.** The run stops after the preflight.
  Give the program a key, or let `--without-auphonic` align, mix and cut
  on this machine.
* **The list is English in a German run.** `--help` and the names of
  the switches do not follow `--lang`; that switch sets the language of
  the messages.
