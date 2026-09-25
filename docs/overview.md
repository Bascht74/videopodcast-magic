# Overview

*Auf Deutsch: [overview.de.md](overview.de.md). Back to the
[contents](README.md).*

Raw material from a video podcast becomes an edited episode: the good
audio inside the video files, the cameras on one time axis, and a first
camera cut in DaVinci Resolve. One window, or one command.

![The main window with material in it](images/files.png)

*Three tabs: Files & production, Assignment & time window, Resolve cut.
The first one is open, with the recordings, the video files and the
notes from the preflight. This chapter explains none of them; the
chapters after it do.*

## What it takes off your hands

An interview is in the can. Two cameras ran, and because a camera
microphone never sounds good, a recorder stood next to them. On the disk
there are now two kinds of file: big picture with poor sound, good sound
with no picture. Laying one on the other should be enough.

It is not. The recorder split the take at two gigabytes, so one interview
became three files. Sound and picture do not start together. And after an
hour of cutting the lips are off by a tenth of a second or so. Camera and
recorder each have their own quartz, and one ticks a few millionths
faster. Timecode would settle it, if anybody had set both devices to the
same clock.

So the program listens instead. It compares when the good audio gets loud
and when the camera microphone does, slides them together, and takes the
drift out over the length. If the measurement is too shaky for that, the
program leaves it alone and says so.

A steady tone defeats that comparison. A hum off the mains, an air
conditioner, a signal tone somewhere in the building: it stands there
from the first second to the last, unchanging, and it buries the ups and
downs the comparison lives on. So the program runs the same comparison
again, this time only on the frequency bands that move over the
recording; the ones that stand still are left out. It looks for no
frequency it knows in advance -- it asks each recording which of its own
bands carry movement. With such a tone 40 dB above the recording the
first comparison missed the place by as much as 2247 seconds; the second
lands within 31 milliseconds. It counts only where it has set enough
points over the whole running time and they all sit on one line;
otherwise the recording goes on to the third way. Where it holds, the
drift comes out of the length as before, and the log marks the line:
`placed on the bands that move`.

Both comparisons live on pauses in the speech, and music has none. Where
neither finds anything, the program looks at the phase, which survives a
room and a second microphone. The phase answers where the audio sits. How
fast the clocks run stays unknown, so the program takes no drift out on
this path. The log marks that line too: `placed by phase`.

Cameras are set against each other by their own microphones, each
against the longest of them, but only with the first comparison: between
two cameras there is no second or third way, so the program asks more
of the match before it lets it count. Where a camera's sound falls short
of that, its timecode is the second way, and the camera stands where its
timecode says -- counted from a camera the sound has placed and that
carries a timecode too, so this holds only where both clocks were set to
the same time. The log names the camera and says why its sound was not
enough: how far the match fell short, or that the camera gave no sound
to measure at all. A camera with neither -- no sound to go by and no
timecode that fits -- is not laid down at a guess: the log names it and
leaves it out, and where the window sees that already, it proposes
**ignore this video** for it, or **Intro** where the file is far shorter
than the rest.

## What comes out

One new video file per camera. The program copies the picture instead of
re-encoding it. Where a time window is set, the file holds that window
and a second at either end rather than the whole shoot -- five minutes
out of a real interview came to 6.09 GB where the whole day came to
83.57 GB. Inside it the good audio sits as the first audio track,
the camera microphone as the second, both named. In the edit you say
"audio from track one" and you are done. Afterwards the program measures
the two tracks against each other and writes down how far apart they are.
With one recorder and one camera that is the simplest case: [the simple
path](simple-path.md).

Before the first long step the program looks the material over; it calls
that check the preflight ([preflight](preflight.md)). At the end every
measurement lands in a CSV the next run does not overwrite. Over a few
months that is where a recorder going slow, or a camera drifting away
from the others in colour, shows up.

## Two kinds of production

The window asks one thing first: what the production is to become. The
field **Project type** on the first tab has two answers. **Cut by
speaker** is everything below: the cameras on one time axis and a cut by
who is speaking, with the speakers told apart, the words written down
and a Resolve project that holds the cut. **Sync only** stops after the
time axis: the good audio in every camera file, one timeline with all
the cameras side by side, and nothing about speakers -- no separation,
no transcript, no cut. That is the answer where the cut is to be made by
hand or in Resolve, and it takes one audio recording and no second one.
The type is asked once, kept in the project file, and stands on the
command line as `--project-type`.

## Putting several speakers on one time axis

Three people at a table means three microphones, and all three voices are
on each of them. That bleed is what makes podcast audio sound cheap.
auphonic.com can take it out, given every track exactly the same length
to the millisecond ([processing](auphonic.md)). So the program puts every
camera and every track on one common time axis first.

Then you say who belongs to which camera, in a table with a player beside
it. Each camera file then carries the mix of exactly the speakers in its
frame as the first audio track, and the single voices behind it. Play it
alone and you hear the right thing; cut with it and you have everything
separately ([multitrack](multitrack.md)).

The service is optional. Without it three steps are missing: de-bleed,
leveler and noise removal. The program works out who speaks when for
itself, and it measures the distance between the microphones instead of
assuming it.

## Cutting by speaker

Whoever speaks alone gets their camera, with a little lead so the cut
sits before the first word. When several speak at once, a camera showing
exactly those people beats the wide shot, the one camera with everybody
in frame. The wide shot itself does not come by the clock, but at a long
pause shortly before someone else starts.

Nine number fields and five selectors set how fine the cut turns out, and
the window shows their effect at once, without writing anything. Out come
a table, an EDL and the speaking times: who talked how long, in per cent
([camera cut](camera-cut.md)).

## Building the Resolve project

On request the program creates the project and builds two timelines
([DaVinci Resolve](resolve.md)). One is the finished cut: the camera
pieces on top without their sound, a continuous overall mix below, so the
sound does not jump at the cuts. The other has every camera on its own
video track, uncut, ready to become a multicam clip if you would rather
have Resolve cut it itself.

Turning it into one is a right click, and the only thing the program does
not do for you. Resolve's scripting interface has no multicam, so it says
exactly what to click. The program sets up colour tagging, a colour group
per camera and the render job; in Resolve one click on **Render All** is
left.

## What it does not decide

The camera cut is a proposal that takes the first blunt hour off your
hands. What the episode is to become stays yours: which passage survives,
where it drags, how the picture is graded, where the intro dissolves. The
program makes sure everything is where it belongs when the actual work
starts. It tells you when something does not fit, before you have put an
hour into the wrong cut.

[What it needs](requirements.md) names what to install first. [The
interface](interface.md) shows the window itself.
