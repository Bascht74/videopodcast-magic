# Channels: one track or two?

*Auf Deutsch: [channels.de.md](channels.de.md). Back to the [contents](README.md).*

## Channels: one track or two?

A file with two channels can be two things: one pair of microphones, or
two people that a recorder wrote into one file. The difference matters --
read as a pair, both speakers land in one track, and the camera cut has
nothing left to switch between.

Every neighbour is asked, not every second one. Each channel has a row
of its own, and on it a tick that offers "join with Channel 3"; what was
measured stands beside it. A channel can belong to only one pair, so
once 2 and 3 are joined, the row of channel 3 has no tick of its own any
more and says "with Channel 2 one stereo track" -- it is spoken for.
Where two neighbours both look like a pair, the left one wins until
somebody says otherwise.

The measurement proposes once, and a tick corrects that proposal rather
than starting it over: taking a pair apart takes exactly that pair apart
and joins nothing else, putting one together frees both its neighbours.
A tick that says the same as the measurement is no override and is not
kept as one; only a row that says something else reads "set by hand --
overrides the measurement". Until the measurement is in, the row says so
instead of guessing; where the channel count of a file cannot be read at
all, the run says that rather than leaving the row waiting.

The tracks are named after their channels: `Channel 1`, `Channel 2+3`. So
are the files they are cut into, closed up and with a short fingerprint of
the source folder in between -- `Mixer_3f9a1c02_Channel1+2.wav`. The
word "Channel" stays English in every language.

What decides is *when* the two channels hear the same thing, not how
alike they are. One
pair of microphones hears everything at practically the same moment; two
clip-ons on two people hear each other late, and by exactly their
distance.

The distance it reports is right to a tenth of a metre, and it still
holds where the bleed is 26 dB below the speaker.

Two limits, both named on the row. A pair spaced wider than about 35 cm
is read as two microphones. And a file whose two channels were laid on a
common time axis before being joined looks like a pair. Where the two
channels share too little sound to tell, nothing is claimed -- the split
is proposed.

Every track that comes out of this is a track like any other: a row in
the assignment, a name, a camera, and it can be listened to on its own.
Silent channels do not become tracks. The tick overrules the measurement
at any time, and an override is stored in the project.

Whether a channel counts as used is decided by two rules, and one of them
is enough. Relative: 45 dB below the loudest channel is an input nobody
plugged anything into. Absolute: below −70 dBFS there is only the noise
floor of the converter. The absolute rule comes from a measurement, not
from a guess. It only applies where at least one channel is above it; a
recording that is quiet throughout is still judged by the relative rule.

Judged is the whole recording, not its first block. Each block is
measured on its own and the answers are combined: a channel counts as
used where it carries something in any block, and each pair is judged in
the block where it is loudest.

### Stereo stays stereo

A track keeps the channels its source has. Where the measurement above
reads two channels as one pair -- or the tick says so -- that pair stays
two channels the whole way: onto the time axis, through the loudness
measurement, into its own audio track on the camera file, and into the
mix. A two channel file that was never split behaves exactly the same
way; nothing extra marks it.

The mix has two channels anyway, so a stereo track needs no room made
for it; what that means for the loudness measurement is in
[Preflight](preflight.md). Mono tracks are copied to both sides before
the sum, not after.

At auphonic.com the finished mixdown is asked for in two channels as
soon as one track is stereo. On the simple path the mono fold is
switched off for every output the preset asks for: what a preset folds
cannot be unfolded afterwards.

What auphonic.com does with a stereo track inside a multitrack
production is not something I have measured against the real service. If
a track goes up in stereo and comes back in one channel, the run says so
and carries on -- the mix keeps its two channels, and what is gone is
the difference between the two microphones of that one track.
