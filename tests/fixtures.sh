#!/bin/bash
# Build the fixture folders the suite does not build for itself.
#
# Most tests make their own material and clean it up again. Six folders
# are shared and read-only, so they are built once, here: "$FIX/foreign"
# (everything that is not a camera file), "$FIX/hdrtest" (HDR variants),
# "$FIX/playertest" (long enough to play), "$FIX/interview" (the shape of
# a whole job), "$FIX/mixer" (one file with eight channels) and
# "$FIX/twovoices" (two synthetic voices taking turns). run.sh calls
# this before the tests fan out; pass "force" to build them again.
set -e
force="$1"
# Where this script lives, worked out before anything changes the
# directory: the blocks below cd into the folders they build, and a
# relative path would then point at the wrong place.
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# A folder counts as built only when the marker is there. Non-empty is not
# enough: a build broken off half way leaves files behind, and then every
# later run would take the ruin for a finished folder.
# Where the shared folders live. Fixed paths in a directory everybody
# can write to, each one preceded by an rm -rf, is a poor idea on a
# machine with two users or a CI with two jobs: the second run deletes
# the first one's material. The root carries the user id, and
# VPM_FIXTURES overrides it. fixture_root.py says the same thing to the
# Python side.
FIX="${VPM_FIXTURES:-/tmp/vpm-fixtures-$(id -u)}"
mkdir -p "$FIX"
export VPM_FIXTURES="$FIX"

MARK=.built
# The marker may also carry a word for the recipe that wrote the folder.
# Without one, a folder built by an older version of this script is there,
# looks finished, and is taken for current for ever: the day the cameras
# below were given a timecode, every machine that had already built the
# fixture went on using material without one, and the tests that ask
# about the timecode would have gone red for want of a rebuild rather
# than for want of a program. A block that hands a word to have and
# done_with rebuilds its folder as soon as that word changes; a block
# that hands none keeps the old behaviour, marker there is enough, so
# the folders that did not change are not rebuilt either.
have() {
  [ -f "$1/$MARK" ] || return 1
  [ "$force" != force ] || return 1
  [ -z "$2" ] || [ "$(cat "$1/$MARK" 2> /dev/null)" = "$2" ]
}
done_with() { printf '%s' "$2" > "$1/$MARK"; }
FF="ffmpeg -v error"

# ---- "$FIX/foreign": everything that is not a camera file ----
if have "$FIX/foreign"; then
  echo "  "$FIX/foreign"      already there"
else
  rm -rf "$FIX/foreign" && mkdir -p "$FIX/foreign"/folder
  cd "$FIX/foreign"
  $FF -f lavfi -i testsrc=size=64x36:rate=30:duration=1 -c:v libx264 v.mp4 -y
  $FF -f lavfi -i testsrc=size=64x36:rate=30:duration=1 -c:v libx264 v.mkv -y
  $FF -f lavfi -i testsrc=size=64x36:rate=30:duration=1 -frames:v 1 image.png -y
  $FF -f lavfi -i "sine=frequency=440:duration=1" audio.wav -y
  $FF -f lavfi -i "sine=frequency=440:duration=1" -c:a aac audioonly.mov -y
  printf 'just text\n' > text.txt
  : > empty.bin
  head -c 20000 /dev/urandom > junk.mov
  # Cut off in the middle: the front is sound, the back is missing.
  $FF -f lavfi -i testsrc=size=64x36:rate=30:duration=2 -c:v libx264 whole.mp4 -y
  head -c 800 whole.mp4 > frag.mp4 && rm whole.mp4
  done_with "$FIX/foreign"
  echo "  "$FIX/foreign"      built"
fi

# ---- "$FIX/hdrtest": one file per HDR case ----
if have "$FIX/hdrtest"; then
  echo "  "$FIX/hdrtest"      already there"
else
  rm -rf "$FIX/hdrtest" && mkdir -p "$FIX/hdrtest"
  cd "$FIX/hdrtest"
  STATIC="master-display=G(8500,39850)B(6550,2300)R(35400,14600)WP(15635,16450)L(10000000,1):max-cll=1000,400"
  # Two passes on purpose. ffmpeg 9 no longer carries -color_primaries and
  # -color_trc from the command line into the file: the values reach the
  # bitstream through the encoder's own parameters, but the container is
  # left saying "unspecified", and then the program rightly reports that
  # the colr box is missing. Measured on ffmpeg 9.0.1. Encoding first and
  # then repacking with -c:v copy takes the values out of the bitstream,
  # where the muxer does pick them up. Works on older ffmpeg too.
  hdr() {  # hdr <file> <transfer> <extra x265 params>
    $FF -f lavfi -i testsrc=size=128x72:rate=30:duration=1 \
      -c:v libx265 -pix_fmt yuv420p10le \
      -x265-params "colorprim=bt2020:transfer=$2:colormatrix=bt2020nc${3:+:$3}" \
      -tag:v hvc1 "raw_$1" -y
    $FF -i "raw_$1" -c:v copy -tag:v hvc1 -movflags +write_colr "$1" -y
    rm -f "raw_$1"
  }
  hdr hdr10.mp4      smpte2084     "hdr10=1:$STATIC"
  hdr hlg.mp4        arib-std-b67  ""
  hdr nostatic.mp4   smpte2084     ""
  hdr wrongcurve.mp4 bt2020-10     ""
  $FF -f lavfi -i testsrc=size=128x72:rate=30:duration=1 -c:v libx264 \
    -pix_fmt yuv420p \
    -x264opts "colorprim=bt709:transfer=bt709:colormatrix=bt709" \
    raw_sdr.mp4 -y
  $FF -i raw_sdr.mp4 -c:v copy -movflags +write_colr sdr.mp4 -y
  rm -f raw_sdr.mp4
  done_with "$FIX/hdrtest"
  echo "  "$FIX/hdrtest"      built"
fi

# ---- "$FIX/playertest": long enough for a cut of five shots ----
if have "$FIX/playertest"; then
  echo "  "$FIX/playertest"   already there"
else
  rm -rf "$FIX/playertest" && mkdir -p "$FIX/playertest"
  cd "$FIX/playertest"
  $FF -f lavfi -i "testsrc=size=320x180:rate=25:duration=60" \
    -c:v libx264 -pix_fmt yuv420p a.mp4 -y
  $FF -f lavfi -i "smptebars=size=320x180:rate=25:duration=60" \
    -c:v libx264 -pix_fmt yuv420p b.mp4 -y
  $FF -f lavfi -i "sine=frequency=440:duration=60" -c:a aac audio.m4a -y
  done_with "$FIX/playertest"
  echo "  "$FIX/playertest"   built"
fi

# ---- "$FIX/interview": the shape of a real job, so nothing is skipped ----
#
# Three speakers, one of them recorded in three blocks, three cameras, and
# a project file pointing at them. Tests that want a whole job used to be
# skipped for want of material, and a skipped test says nothing while
# looking harmless. Set VPM_MEDIA to point at real material instead.
#
# The cameras carry a timecode, and it is the point of this folder as
# much as the pictures are. A job has three clocks -- the time of the
# programme, the time inside each file, and the window somebody asks
# for -- and the only bridge between them is the timecode a camera
# writes beside its pictures. Until 28.8.2026 not one file here had
# one, so no test could look at that bridge at all, and an error of 37
# and of 77 seconds walked through the whole suite unseen.
#
# Three different values with three different distances, because "all
# the same" and "correctly converted" look alike when every distance is
# zero, and two equal distances hide which of the two was taken:
#
#   Totale_08141855_C003.mov       18:55:00:00   68100.00 s
#   Moderatoren_08141855_C005.mov  18:55:04:00   68104.00 s   +4.00 s
#   Kandidat_08141858_C009.mov     18:55:17:12   68117.48 s  +17.48 s
#
# The wide shot rolls first, which is what a wide shot does. The last
# one holds 12 frames, so one distance is not a whole number of
# seconds and a conversion that throws the frames away is off by
# 0.48 s rather than by nothing at all.
#
# The pictures are 25 frames a second, so a frame is 0.04 s and the
# twelve are 0.48 s. Measured on ffmpeg 9.0.1: file_timecode reads the
# string off the video stream tag, not off the format tag -- a MOV
# keeps it there -- and its own default is 30 frames a second, under
# which the same string comes out as 68117.43. That gap is not a fault
# of the material; it is the thing the material now lets a test see.
#
# The distances are seconds and not the minutes the file names suggest,
# because the files are two minutes long and three cameras that do not
# overlap are not a job. And the pictures themselves are the same
# testsrc in all three, so the measured offset between them stays zero
# while the timecodes say otherwise: an axis over this folder is
# absolute and lands on the middle timecode. What can be checked here
# is the conversion for one file, not the alignment of three.
INTERVIEW_BUILD=timecode-1
if have "$FIX/interview" "$INTERVIEW_BUILD"; then
  echo "  "$FIX/interview"    already there"
else
  rm -rf "$FIX/interview" && mkdir -p "$FIX/interview"/Ergebnis
  cd "$FIX/interview"
  mic() { $FF -f lavfi -i "sine=frequency=$2:duration=$3" -ac 1 -ar 48000 \
            -c:a pcm_s16le "$1" -y; }
  # cam <file> <seconds> <sine Hz> <timecode>
  cam() { $FF -f lavfi -i "testsrc=size=320x180:rate=25:duration=$2" \
            -f lavfi -i "sine=frequency=$3:duration=$2" \
            -c:v libx264 -preset ultrafast -pix_fmt yuv420p -c:a aac \
            -timecode "$4" -shortest "$1" -y; }
  mic Kandidat_0008A_Timecode.wav 220 120
  for i in 00009 00010 00011; do mic "Moderator_REC$i.wav" 330 40; done
  for i in 00008 00009 00010; do mic "Moderatorin_REC$i.wav" 440 40; done
  cam Kandidat_08141858_C009.mov    120 220 18:55:17:12
  cam Moderatoren_08141855_C005.mov 120 330 18:55:04:00
  cam Totale_08141855_C003.mov      120 550 18:55:00:00
  done_with "$FIX/interview" "$INTERVIEW_BUILD"
  echo "  "$FIX/interview"    built"
fi
# Opening a project moves the project file into the output folder, so
# after one run the fixture would have none. Written again every time.
"${VPM_PYTHON:-python3}" "$HERE/interview_project.py" "$FIX/interview"

# ---- "$FIX/mixer": eight channels in one file, one case each ----
#
# What a field mixer writes: eight inputs into one poly WAV. Nothing
# else in the fixtures has more than one channel, so every case the
# channel measurement knows is put into this one file, once each -- a
# single reading of it shows the lot.
#
# Measured with channel_facts on ffmpeg 9.0.1. "share" is how much of
# what two neighbours have in common arrives at the same moment; that,
# and not how alike they are, is what decides a pair.
#
#   1  host lav           -33.8 dBFS   1+2  share 0.17, 2.5 ms apart
#   2  guest lav          -33.5 dBFS   2+3  share 0.12, 4.5 ms apart
#   3  room mic left      -37.1 dBFS   3+4  share 1.00, 0.0 ms  -> pair
#   4  room mic right     -37.0 dBFS   4+5  channel 5, 63 dB under
#   5  nothing plugged in -96.9 dBFS   5+6  channel 6 at -73 dBFS
#   6  gain shut          -73.4 dBFS   6+7  channel 7 silent
#   7  dead input          -inf        7+8  channel 7 silent
#   8  spare microphone   -33.9 dBFS
#
# Both rules that take a channel out of the run fire here, and they can
# only both fire in one file when the loudest channel stays under
# -25 dBFS: the relative rule catches everything more than 45 dB under
# the loudest first, so a channel can reach the absolute rule -- under
# -70 dBFS -- only while the loudest is less than 45 dB above it. Hence
# a recording that is quiet all through, the way a mixer sounds with
# honest headroom. Channel 5 is 63 dB down and goes out on the relative
# rule, channel 6 is 40 dB down but under -70 dBFS and goes out on the
# absolute one. Channel 7 holds nothing at all, which is the third
# wording again.
#
# The pairs are built, not hoped for. Noise on every channel makes no
# pairs at all: what makes one is a signal two channels share with a
# known delay. The two lavs hear each other 120 samples late (2.5 ms,
# 0.86 m), the room pair is one signal 14 samples apart (0.29 ms, well
# inside the 1 ms window), and the room mic hears both speakers 216
# samples late (4.5 ms, 1.5 m). 24 bit, because channel 5 lies below
# the last step of 16. Eight seconds, and the build takes under a
# second -- run.sh calls this before every suite run.
if have "$FIX/mixer"; then
  echo "  "$FIX/mixer"        already there"
else
  rm -rf "$FIX/mixer" && mkdir -p "$FIX/mixer"
  cd "$FIX/mixer"
  # The gains are set here and not left to amix: the levels are the
  # point of channels 5 and 6, and amix's own normalising would move
  # them. 0.040 puts a voice at about -34 dBFS.
  $FF -filter_complex "
    anoisesrc=c=white:r=48000:d=8:a=0.9:seed=1101,
      highpass=f=140,lowpass=f=5200,tremolo=f=0.62:d=0.6,
      asplit=3[a1][a2][a3];
    anoisesrc=c=white:r=48000:d=8:a=0.9:seed=2202,
      highpass=f=170,lowpass=f=6000,tremolo=f=0.83:d=0.6,
      asplit=3[b1][b2][b3];
    anoisesrc=c=pink:r=48000:d=8:a=0.9:seed=3303,
      highpass=f=60,lowpass=f=9000[r1];
    anoisesrc=c=white:r=48000:d=8:a=0.9:seed=4404,
      highpass=f=150,lowpass=f=5600,tremolo=f=0.71:d=0.6[c1];
    anoisesrc=c=white:r=48000:d=8:a=0.9:seed=5505,volume=0.00002[ch5];
    anoisesrc=c=white:r=48000:d=8:a=0.9:seed=6606,volume=0.0003[ch6];
    anullsrc=r=48000:cl=mono,atrim=end=8[ch7];
    anoisesrc=c=white:r=48000:d=8:a=0.9:seed=7707,volume=0.06[nr];
    [a2]adelay=delays=120S,volume=0.22[a2d];
    [b2]adelay=delays=120S,volume=0.30[b2d];
    [a3]adelay=delays=216S,volume=0.45[a3d];
    [b3]adelay=delays=216S,volume=0.45[b3d];
    [a1][b2d]amix=inputs=2:normalize=0,volume=0.040[ch1];
    [b1][a2d]amix=inputs=2:normalize=0,volume=0.040[ch2];
    [r1][a3d][b3d]amix=inputs=3:normalize=0:duration=first,
      volume=0.8,asplit=2[p1][p2];
    [p1]volume=0.040[ch3];
    [p2]adelay=delays=14S,volume=0.040[p2d];
    [p2d][nr]amix=inputs=2:normalize=0:weights=1 0.05:duration=first[ch4];
    [c1]volume=0.040[ch8];
    [ch1][ch2][ch3][ch4][ch5][ch6][ch7][ch8]amerge=inputs=8[out]" \
    -map "[out]" -c:a pcm_s24le -ar 48000 -t 8 Mixer.wav -y
  # One camera beside it, so the folder is a job and not a single file.
  # Its sound is channel 1 of the mixer, which is what a camera picks up
  # in that room -- anything else would be a file that cannot be lined
  # up with the recording next to it.
  $FF -f lavfi -i "testsrc=size=320x180:rate=25:duration=8" -i Mixer.wav \
    -filter_complex "[1:a]pan=mono|c0=c0[a]" -map 0:v -map "[a]" \
    -c:v libx264 -preset ultrafast -pix_fmt yuv420p -c:a aac \
    -shortest Studio_08141855_C001.mov -y
  done_with "$FIX/mixer"
  echo "  "$FIX/mixer"        built"
fi

# ---- "$FIX/twovoices": two synthetic voices, taking turns ----
#
# Everything else here is sine tones and noise, and a speaker
# separation finds nobody in those. This folder holds speech, because
# it is spoken: macOS brings say(1), and two of its voices reading one
# sentence each in turn give a recording whose truth is exact -- the
# length of every turn is the length of the file that voice wrote, so
# every boundary is known to the millisecond. speakers_for_real_test.py
# runs the real separation over it.
#
# Measured on 24 August 2026, Apple M4 Pro, macOS 26.6.1: the build
# takes about 4 s, six turns come to about 32 s of audio, and the
# separation over it takes 4.4 s. Four turns would do -- the separation
# gets those right too -- but six leave room for one turn to go astray
# without the count of turns saying nothing.
#
# The voices are picked from what the machine really lists, not from a
# name somebody remembered: say -v '?' differs between machines and
# between system languages. The newer Apple voices carry the language
# in their name, translated ("Eddy (English (UK))" on an English Mac,
# "Eddy (Englisch (UK))" on a German one), so only the plain one-word
# names are asked for. Measured over four pairs -- Samantha/Daniel,
# Samantha/Kathy, Samantha/Fred, Anna/Daniel -- the separation told all
# four apart and put every boundary within 0.11 s, so the order below
# is a preference and not a condition. Where fewer than two of them are
# there the folder is not built and the test skips.
if have "$FIX/twovoices"; then
  echo "  "$FIX/twovoices"    already there"
elif ! command -v say > /dev/null 2>&1; then
  echo "  "$FIX/twovoices"    skipped -- no say(1) on this machine"
else
  # Two voices out of the ones this machine really has.
  spoken=$(say -v '?' 2>/dev/null | sed 's/ .*//' | sort -u)
  picked=()
  for want in Samantha Daniel Alex Karen Moira Tessa Fiona Victoria \
              Serena Fred Anna Markus Petra Yannick; do
    if [ "${#picked[@]}" -lt 2 ] && echo "$spoken" | grep -qx "$want"
    then
      picked+=("$want")
    fi
  done
  if [ "${#picked[@]}" -lt 2 ]; then
    echo "  "$FIX/twovoices"    skipped -- fewer than two known voices"
  else
    V1="${picked[0]}"; V2="${picked[1]}"
    rm -rf "$FIX/twovoices" && mkdir -p "$FIX/twovoices"
    cd "$FIX/twovoices"
    # The pause between two turns. Long enough for the separation to
    # see a boundary, short enough to sound like a conversation.
    GAP=0.40
    # Six sentences, long enough that a voice is more than a word.
    # English, like everything else here.
    #
    # LC_ALL=C in front of every awk, and it is not decoration:
    # printf "%.3f" writes the decimal separator of the locale, so on
    # this German machine the truth file came out as "4,988" while
    # ffprobe kept writing "4.988". The reader then had a truth it
    # could not parse. run.sh sets LC_ALL=C for the whole suite, but
    # fixtures.sh is also run by hand.
    say_turn() {  # say_turn <who> <voice> <number> <text>
      say -v "$2" -o "piece$3.wav" --data-format=LEI16@16000 \
        --file-format=WAVE "$4"
      dur=$(ffprobe -v error -show_entries format=duration \
        -of csv=p=0 "piece$3.wav")
      end=$(LC_ALL=C awk -v a="$at" -v d="$dur" \
        'BEGIN{printf "%.3f", a+d}')
      echo "$1 $at $end" >> truth.txt
      echo "file 'piece$3.wav'" >> list.txt
      $FF -f lavfi -i anullsrc=r=16000:cl=mono -t "$GAP" \
        -c:a pcm_s16le "hush$3.wav" -y
      echo "file 'hush$3.wav'" >> list.txt
      at=$(LC_ALL=C awk -v e="$end" -v g="$GAP" \
        'BEGIN{printf "%.3f", e+g}')
    }
    at=0.000
    : > truth.txt
    : > list.txt
    say_turn A "$V1" 0 "Welcome to the show. Today we are talking \
about how a recording becomes an episode."
    say_turn B "$V2" 1 "Thank you for having me. I have been looking \
forward to this conversation all week."
    say_turn A "$V1" 2 "Let us start at the beginning. What happens \
to the sound before anything else is done?"
    say_turn B "$V2" 3 "The first thing is to find the good audio \
inside the video files, and that takes a while."
    say_turn A "$V1" 4 "And after that the cameras have to go onto \
one time axis, if I understand it right."
    say_turn B "$V2" 5 "Exactly. Without a common clock nothing lines \
up and every cut lands in the wrong place."
    $FF -f concat -safe 0 -i list.txt -c:a pcm_s16le -ar 16000 -ac 1 \
      talk.wav -y
    printf '%s %s\n' "$V1" "$V2" > voices.txt
    rm -f piece*.wav hush*.wav list.txt
    done_with "$FIX/twovoices"
    echo "  "$FIX/twovoices"    built ($V1, $V2)"
  fi
fi
