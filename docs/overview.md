# Overview

*Auf Deutsch: [overview.de.md](overview.de.md). Back to the [manual](README.md).*

Raw material from a video podcast becomes an edited episode: the good
audio inside the video files, the cameras on one time axis, and a first
camera cut in DaVinci Resolve. One command, or one window. What follows
is the story of one run.

## What it takes off your hands

An interview is in the can. Two cameras ran, and because a camera
microphone never sounds good, a recorder stood next to them. On the disk
there are now two kinds of file: big picture with poor sound, good sound
with no picture. Laying one on the other should be enough.

It is not. The recorder split the take at two gigabytes, so one interview
became three files. Sound and picture do not start together. And after an
hour of cutting the lips are off by a tenth of a second: camera and
recorder each have their own quartz, and one ticks a few millionths
faster. Timecode would settle it, if anybody had set both devices to the
same clock.

So the program listens instead. It compares when the good audio gets loud
and when the camera microphone does, slides them together, and takes the
drift out over the length. Where the measurement is too shaky for that,
it leaves it alone and says so, because a bad correction is worse than
none.

## What comes out

One new video file per camera. The picture is copied, not re-encoded, and
inside it the good audio sits as the first audio track, the camera
microphone as the second, both named. In the edit you say "audio from
track one" and you are done. Afterwards the program measures the two
tracks against each other and writes down how far apart they are. One
recorder and one camera need nothing more: [the simple
path](simple-path.md).

Before the first long step the material is looked over
([preflight](preflight.md)), and at the end every measurement lands in a
CSV the next run does not overwrite -- over a few months that is where a
recorder going slow, or a camera drifting away from the others in colour,
shows up.

## Several speakers, several cameras

Three people at a table means three microphones, and all three voices are
on each of them. That bleed is what makes podcast audio sound cheap.
auphonic.com can take it out, given every track exactly the same length
to the millisecond ([processing](auphonic.md)) -- so the program puts
every camera and every track on one common time axis first.

Then you say who belongs to which camera, in a table with a player beside
it. Each camera file then carries the mix of exactly the speakers in its
frame as the first audio track, and the single voices behind it: play it
alone and you hear the right thing, cut with it and you have everything
separately ([multitrack](multitrack.md)).

The service is optional. Without it only de-bleed, leveler and noise
removal are missing. The program works out who speaks when for itself,
and nothing about the distance between the microphones is assumed -- it
is measured.

## The camera cut

Whoever speaks alone gets their camera, with a little lead so the cut
sits before the first word. When several speak at once, a camera showing
exactly those people beats the wide shot. The wide shot itself does not
come by the clock: what is looked for is a long pause, shortly before
someone else starts, so the rhythm comes out irregular by itself. Two
numbers set how fine the cut turns out, and the window shows their effect
at once, without writing anything. Out come a table, an EDL and the
speaker statistics: who talked how long, in per cent ([camera
cut](camera-cut.md)).

## Into DaVinci Resolve

On request the program creates the project and builds two timelines
([DaVinci Resolve](resolve.md)). One is the finished cut: the camera
pieces on top without their sound, a continuous overall mix below, so the
sound does not jump at the cuts. The other has every camera on its own
video track, uncut, ready to become a multicam clip if you would rather
have Resolve cut it itself.

Turning it into one is a right click, and the only thing the program does
not do for you -- Resolve's scripting interface has no multicam -- so it
says exactly what to click. Colour tagging, a colour group per camera and
the render job are set up; in Resolve one click on "Render All" is
left.

## What it does not decide

The camera cut is a proposal that takes the first blunt hour off your
hands. What the episode is to become stays yours: which passage survives,
where it drags, how the picture is graded, where the intro dissolves. The
program makes sure everything is where it belongs when the actual work
starts -- and tells you when something does not fit, before you have put
an hour into the wrong cut.
