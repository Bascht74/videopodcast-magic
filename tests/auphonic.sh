#!/bin/bash
# The tests that talk to auphonic.com itself. Success = return code 0,
# no traceback, no "FAIL".
#
# They are not in the suite and run.sh does not know them: the suite
# reaches nothing outside this machine, and a run without the network or
# without a key would be red for a reason that is not a fault. They live
# in auphonic/live/ and are started from here -- and only with the word,
# because the owner decides when auphonic.com is spoken to:
#
#   cd tests && bash auphonic.sh --online                  the free ones
#   cd tests && bash auphonic.sh --online --spend-credit   all of them
#   cd tests && bash auphonic.sh --online auphonic_presets_arrive   one
#
# --online lets through the tests that only read: the key, the presets.
# --spend-credit lets through the ones that start a production, which
# costs credit; without it they leave themselves out and say so. Claude
# proposes a run when a change needs one and starts it after the owner's
# OK; nobody runs these as a matter of routine.
#
# The key is never handed to this script. The program reads it at run
# time from the credential store -- the window or --store-auphonic-key
# puts it there -- and hands it to curl on curl's input. Nothing here
# prints it, and nothing here asks for it on a command line.
#
# Each production a test makes carries a title of the tests' own shape
# and is deleted again at the end; the sweep here clears whatever a
# killed run left behind, at the start and at the end, and nothing else.
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$HERE"
WHERE="$HERE/auphonic/live"

ONLINE=0
CREDIT=0
TESTS=""
for a in "$@"; do
  case "$a" in
    --online) ONLINE=1 ;;
    --spend-credit) CREDIT=1 ;;
    -*) echo "auphonic.sh does not know $a -- it takes --online and" \
             "--spend-credit" >&2; exit 2 ;;
    *) TESTS="$TESTS $a" ;;
  esac
done
# No word, no call. Said before anything is started, so a run nobody
# asked for costs nothing and reaches nothing.
if [ "$ONLINE" != 1 ]; then
  echo "auphonic.sh talks to auphonic.com, and only on consent."
  echo
  echo "  cd tests && bash auphonic.sh --online                  reads only"
  echo "  cd tests && bash auphonic.sh --online --spend-credit   starts productions"
  echo
  echo "Nothing was started and nothing was sent."
  exit 2
fi

# The same interpreter the suite runs on. VPM_PYTHON overrides it.
PY="${VPM_PYTHON:-}"
if [ -z "$PY" ]; then
  for candidate in /opt/py3147/bin/python3.14 python3.14 python3; do
    if command -v "$candidate" > /dev/null 2>&1; then PY="$candidate"; break; fi
  done
fi
export VPM_PYTHON="$PY"
echo "Python: $("$PY" -V 2>&1)"
echo "Script: $("$PY" -c 'import the_program; print(the_program.SCRIPT)')"

# curl carries every call, and ffprobe measures what comes back.
for tool in curl ffprobe; do
  if ! command -v "$tool" > /dev/null 2>&1; then
    echo "$tool is not on the search path, and these tests need it."
    exit 2
  fi
done

# The same environment run.sh sets, for the same reason: without it red
# or green is a statement about the machine and not about the program.
export LANG=C LC_ALL=C LANGUAGE=en
export VPM_SILENT=1
export VPM_NO_SPEAKER_SPLIT=1
export VPM_NO_UPDATE_CHECK=1
export PYTHONFAULTHANDLER=1
export VPM_LIVE_AUPHONIC=1
if [ "$CREDIT" = 1 ]; then
  export VPM_LIVE_AUPHONIC_CREDIT=1
else
  unset VPM_LIVE_AUPHONIC_CREDIT
fi

RUN_TEMP=$(mktemp -d "${TMPDIR:-/tmp}/vpm_auphonic_XXXXXX")
RUN_CACHE="${TMPDIR:-/tmp}/vpm_cache_auphonic_$(id -u)_$$"
mkdir -p "$RUN_CACHE"
export VPM_CACHE="$RUN_CACHE"
export TMPDIR="$RUN_TEMP"
KEY_OK=0
clean_up() {
  # auphonic.com first, the disc afterwards, on every way out.
  if [ "$KEY_OK" = 1 ]; then
    echo
    "$PY" "$WHERE/auphonic_ground.py" --sweep
  fi
  rm -rf "$RUN_TEMP" "$RUN_CACHE"
}
trap clean_up EXIT
trap 'exit 130' INT TERM

# Is there a key at all? Asked of the program, which says where it came
# from and never what it is.
echo
if ! "$PY" "$WHERE/auphonic_ground.py" --probe; then
  echo
  echo "No key for auphonic.com on this machine, so nothing was tested."
  echo "Remember it once in the window's settings -- it goes into the"
  echo "credential store -- and start this again. Not on a command line."
  exit 2
fi
KEY_OK=1
"$PY" "$WHERE/auphonic_ground.py" --sweep

[ -z "$TESTS" ] && TESTS=$(cd "$WHERE" && ls *_test.py 2>/dev/null \
                           | sed 's/_test\.py$//' | sort)
if [ -z "$TESTS" ]; then
  echo "no tests found in $WHERE" >&2
  exit 2
fi

green=0; red=0; left_out=0; fell=""
for t in $TESTS; do
  t=$(printf '%s' "$t" | sed 's|.*/||; s/_test\.py$//')
  if [ ! -f "$WHERE/${t}_test.py" ]; then
    echo "no such test: $WHERE/${t}_test.py" >&2
    red=$((red + 1)); fell="$fell $t"
    continue
  fi
  echo
  echo "=== $t ==="
  began=$SECONDS
  out=$("$PY" "$WHERE/${t}_test.py" 2>&1); rc=$?
  took=$((SECONDS - began))
  printf '%s\n' "$out"
  if printf '%s\n' "$out" | grep -q "^SKIPPED:"; then
    left_out=$((left_out + 1))
    echo "--- $t left itself out after ${took}s"
  elif [ $rc -ne 0 ] || printf '%s\n' "$out" | grep -qE "^Traceback|FAIL"; then
    red=$((red + 1)); fell="$fell $t"
    echo "--- $t RED after ${took}s (rc=$rc)"
  else
    green=$((green + 1))
    echo "--- $t green after ${took}s"
  fi
done

echo
echo "green: $green  red: $red  left out: $left_out"
[ -n "$fell" ] && echo "red:$fell"
# A test that left itself out checked nothing, so the run is no pass --
# but it is not a fault either, and it is counted apart.
[ $red -gt 0 ] && exit 1
[ $left_out -gt 0 ] && exit 2
exit 0
