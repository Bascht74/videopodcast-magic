#!/bin/bash
# Build the fixture folders the suite does not build for itself.
#
# Most tests make their own material and clean it up again. Three folders
# are shared and read-only, so they are built once, here: "$FIX/foreign"
# (everything that is not a camera file), "$FIX/hdrtest" (HDR variants) and
# "$FIX/playertest" (long enough to play). run.sh calls this before the
# tests fan out; pass "force" to build them again.
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
have() { [ -f "$1/$MARK" ] && [ "$force" != force ]; }
done_with() { touch "$1/$MARK"; }
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
if have "$FIX/interview"; then
  echo "  "$FIX/interview"    already there"
else
  rm -rf "$FIX/interview" && mkdir -p "$FIX/interview"/Ergebnis
  cd "$FIX/interview"
  mic() { $FF -f lavfi -i "sine=frequency=$2:duration=$3" -ac 1 -ar 48000 \
            -c:a pcm_s16le "$1" -y; }
  cam() { $FF -f lavfi -i "testsrc=size=320x180:rate=25:duration=$2" \
            -f lavfi -i "sine=frequency=$3:duration=$2" \
            -c:v libx264 -preset ultrafast -pix_fmt yuv420p -c:a aac \
            -shortest "$1" -y; }
  mic Kandidat_0008A_Timecode.wav 220 120
  for i in 00009 00010 00011; do mic "Moderator_REC$i.wav" 330 40; done
  for i in 00008 00009 00010; do mic "Moderatorin_REC$i.wav" 440 40; done
  cam Kandidat_08141858_C009.mov    120 220
  cam Moderatoren_08141855_C005.mov 120 330
  cam Totale_08141855_C003.mov      120 550
  done_with "$FIX/interview"
  echo "  "$FIX/interview"    built"
fi
# Opening a project moves the project file into the output folder, so
# after one run the fixture would have none. Written again every time.
"${VPM_PYTHON:-python3}" "$HERE/interview_project.py" "$FIX/interview"
