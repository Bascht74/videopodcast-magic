# All switches

*Auf Deutsch: [command-line.de.md](command-line.de.md). Back to the [contents](README.md).*

## All switches

`--help` prints this list too, always in English. Defaults in brackets.

**Basics**

| Switch | Does |
|---|---|
| `--lang {de,en}` | language of the messages (system language) |
| `--out FOLDER` | where the results go (next to each video) |
| `--suffix TEXT` | added to the file name (`_audio`) |
| `--name TEXT` | name of the new audio track (`Processed audio`) |
| `--name-camera TEXT` | name of the camera track (`Camera Original`) |
| `--parallel COUNT` | this many video files at once; 0 decides for you, 1 one after another |
| `--dry-run` | only measure and report, write nothing |
| `--version` | version number, and the Python this runs on |

**Audio and picture**

| Switch | Does |
|---|---|
| `--no-camera-audio` | drop the camera's own audio instead of keeping it |
| `--no-follow-ups` | do not look for numbered continuation files |
| `--together FILE ...` | these files are one recording, in this order; repeatable |
| `--apart FILE` | this block stands on its own, whatever its name says; repeatable |
| `--transcript` | have auphonic.com write down what is said: json, srt and txt |
| `--no-trim` | audio at full length instead of trimmed to the picture |
| `--no-single-tracks` | only the mix into the video, not the recordings beside it |
| `--head TIME` | cut this much off the front: seconds, MM:SS, HH:MM:SS |
| `--tail TIME` | the same for the end |
| `--no-drift` | measure clock drift and report it, but do not take it out |
| `--tc HH:MM:SS:FF` | start timecode of the picture, where the camera wrote none or a wrong one |
| `--fps NUMBER` | frame rate to assume, where ffprobe reports a wrong one |
| `--lufs NUMBER` | loudness target of the sum of all tracks (-16) |
| `--platform NAME` | that target by platform: `broadcast` -23, `podcast` -16, `podcast-mono` -19, `youtube` -14 |
| `--speech-language CODE` | language tag of the audio tracks, ISO 639-2/B: `ger`, `eng`. Careful, ffmpeg drops `deu` silently (none) |
| `--speech-language-camera CODE` | the same for the camera track (none -- that is what tells the two apart in the QuickTime audio menu) |
| `--speakers-local FILE` | take that recording apart by voice on this machine, and cut by the result (none) |
| `--speakers-from FILE` | take a finished separation out of a project or assignment file instead of computing one (none) |
| `--speakers-count NUMBER` | how many people `--speakers-local` should find (work it out) |
| `--no-speakers-local` | never take a recording apart by voice in this run (off) |
| `--no-speech-recognition` | do not write down what is said; the cut then has no sentence boundaries (off) |

**Auphonic**

| Switch | Does |
|---|---|
| `--auphonic-api-key KEY` | key from the account settings; turns processing on. Without files it only lists the presets |
| `--auphonic-preset NAME` | preset name or id (asked for) |
| `--auphonic-wait SECONDS` | how long to wait (7200) |
| `--auphonic-resume WHAT` | production already there: `result`, `rerun`, `adopt`, `upload`, `abort` (asked for) |
| `--auphonic-done FOLDER` | tracks already processed, named after the speakers -- nothing is uploaded, no credit is spent |
| `--multitrack` | every audio file as its own track, so the bleed can be taken out. Needs a multitrack preset |
| `--assign FILE` | JSON saying which audio belongs to which camera; the interface writes it |
| `--without-auphonic` | align, mix and write locally, camera cut from our own speech detection |

**Time window**

| Switch | Does |
|---|---|
| `--in-point TIME` | start: `17:20:14` absolute, `+12:30` or `90` from the start of the window |
| `--out-point TIME` | end, same notation; `-30` counts back from the end |

**Camera cut**

| Switch | Does |
|---|---|
| `--min-edit-duration SECONDS` | shortest a shot may stand; shorter ones merge into the one that follows, 0 off (3) |
| `--min-speech-to-switch SECONDS` | how long somebody has to hold the floor before the camera follows them, 0 off (1.5) |
| `--edit-change-delay SECONDS` | how much later than the audio the picture cuts; negative lets it lead (0.3) |
| `--reaction-lead SECONDS` | how much earlier the picture goes to the answer after a question (1.5) |
| `--reaction-gap SECONDS` | how soon the answer has to follow the question for the reaction cut to fire (3) |
| `--reaction-hold SHARE` | how much of the ten seconds after the question the answering speaker has to hold, between 0 and 1 (0.7) |
| `--on-monologue VALUE` | one person holds the floor: `wide`, `listener`, `alternate`, `hold` (alternate) |
| `--on-together VALUE` | several speak at once: the same four values (wide) |
| `--on-uncertain VALUE` | the recognition is uncertain: the same four values (wide) |
| `--on-question VALUE` | after a question: `off`, `answer`, `listener` (answer) |
| `--wide-after SECONDS` | from this hold time on the shot is broken up, set on a sentence boundary, not by the clock, 0 off (40) |
| `--wide-length SECONDS` | how long the interposed shot stands at least; it then runs to the end of the sentence (5) |
| `--wide-most SECONDS` | how long it stands at most; where the end of the sentence lies beyond it, the last clause break before it ends the shot (15) |
| `--wide-latest SECONDS` | longest one camera may stand without a cut (120) |
| `--no-wide-edges` | do not hold the wide shot over the greeting and the goodbye |

**Preflight and metrics**

| Switch | Does |
|---|---|
| `--no-preflight` | skip the check before the first long step |
| `--preflight-again` | measure again instead of taking the stored measurement |
| `--anyway` | run even where the preflight found a reason to stop |
| `--no-metrics` | no metrics and no colour comparison at the end |

**Intro and outro**

| Switch | Does |
|---|---|
| `--intro FILE` | laid over the beginning, on the second picture and audio track. Neither aligned nor processed |
| `--outro FILE` | the same for the end; starts where the last word ends |

**DaVinci Resolve**

| Switch | Does |
|---|---|
| `--resolve` | afterwards build the project and the timelines. Resolve has to be running |
| `--resolve-json FILE` | only the Resolve part, from a `..._resolve.json` that is already there |
| `--resolve-project WHAT` | project already there: `update`, `keep`, `new`, `abort` (asked for) |
| `--resolve-audio-tracks` | only print the audio mapping of the open project. Changes nothing |
| `--hdr-check FILE` | only look whether a finished file carries everything that marks it as HDR |
