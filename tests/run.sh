#!/bin/bash
# The suite. Success = return code 0, no traceback, no "FAIL".
# The tests run several at a time: each has its own fixture directory, and
# most of the time goes on starting Python and ffmpeg rather than on the
# processor. WORKERS=1 runs them one after another.
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$HERE"
# Which Python runs the tests. The program states a recommended version
# and the suite runs on exactly that one, or the suite would be proving
# something about a Python nobody uses. VPM_PYTHON overrides it.
PY="${VPM_PYTHON:-}"
if [ -z "$PY" ]; then
  for candidate in /opt/py3147/bin/python3.14 python3.14 python3; do
    if command -v "$candidate" > /dev/null 2>&1; then PY="$candidate"; break; fi
  done
fi
export VPM_PYTHON="$PY"
export PY
echo "Python: $("$PY" -V 2>&1)"
# The time limit around a single test. macOS brings no timeout(1); GNU
# coreutils installs the same program under the name gtimeout. Where
# neither is there the tests run unguarded, and that is said out loud
# rather than passed over: a hung test would otherwise stop the suite
# with nothing to show for it.
LIMIT=""
for candidate in timeout gtimeout; do
  if command -v "$candidate" > /dev/null 2>&1; then LIMIT="$candidate 900"; break; fi
done
if [ -z "$LIMIT" ]; then
  echo "No timeout(1) and no gtimeout -- the tests run without a time limit."
fi
export LIMIT
# English is the source language of the program, so the tests run in it.
# German is the subject of language_test.py and interface_test.py; those
# two set the language themselves.
#
# LANG=C alone does not say it. The program skips "C" on purpose -- a
# double-clicked app starts without any of these -- and then asks the
# system: on macOS "defaults read -g AppleLocale", which on a German Mac
# answers de_DE. The program would speak German while the tests read
# English. LANGUAGE is the first name the program looks at, so it is the
# one that settles the question.
export LANG=C LC_ALL=C LANGUAGE=en
# The player tests play real files. Without this the machine beeps its
# way through every run, which is unbearable beside a suite that starts
# in the background. It forces volume and mute and nothing else -- where
# the playhead lands, which is what the tests measure, is untouched.
export VPM_SILENT=1
# As many at a time as the machine has cores, and one more: most of a
# test is Python starting up and ffmpeg waiting on the disc, so there is
# room beside the processors. Measured on a two-core box: 2 workers
# 2:31, 4 workers 1:57, 8 workers 1:48.
CORES=$(getconf _NPROCESSORS_ONLN 2>/dev/null || sysctl -n hw.ncpu 2>/dev/null || echo 4)
WORKERS=${WORKERS:-$(( CORES + 1 > 12 ? 12 : CORES + 1 ))}

# Where the shared fixture folders live. Worked out here and handed down,
# so fixtures.sh, the tests and VPM_MEDIA below all name the same place.
# fixture_root.py says the same thing to the Python side.
export VPM_FIXTURES="${VPM_FIXTURES:-/tmp/vpm-fixtures-$(id -u)}"

# Three fixture folders are shared and read-only. Building them here,
# before the fan-out, keeps two tests from racing for the same files.
if ! bash "$HERE/fixtures.sh"; then
  echo "fixtures could not be built -- stopping." >&2
  exit 2
fi

# Tests wanting a whole job take the fixture unless real material is
# named. Without this they skip, and a skipped test looks harmless.
export VPM_MEDIA="${VPM_MEDIA:-$VPM_FIXTURES/interview}"

# Every test builds its own material with tempfile.mkdtemp and most of them
# never clean up. Python puts those folders under TMPDIR, so one folder per
# run collects the lot and goes at the end -- a full suite is gigabytes.
# KEEP_TEMP=1 leaves it in place for looking at afterwards.
RUN_TEMP=$(mktemp -d "${TMPDIR:-/tmp}/vpm_run_XXXXXX")
export TMPDIR="$RUN_TEMP"
clean_up() {
  if [ -n "$KEEP_TEMP" ]; then
    echo "temporary material kept in $RUN_TEMP"
  else
    rm -rf "$RUN_TEMP"
  fi
}
trap clean_up EXIT
# Every *_test.py in this folder, so a new test is picked up by being
# there. Sorted, so the order does not depend on the file system.
TESTS=$(cd "$HERE" && ls *_test.py 2>/dev/null | sed 's/_test\.py$//' | sort)
if [ -z "$TESTS" ]; then
  echo "no tests found in $HERE" >&2
  exit 2
fi

OUT=$(mktemp -d /tmp/suite_XXXXXX)
run_one() {
  t="$1"
  out=$($LIMIT "$PY" "$HERE/${t}_test.py" 2>&1); rc=$?
  if [ $rc -eq 0 ] && echo "$out" | grep -q "^SKIPPED:"; then
    # Nothing was checked. Green would be a lie.
    { echo "skipped"
      echo "$out" | grep "^SKIPPED:" | head -1 | sed 's/^SKIPPED: /      /'
    } > "$OUT/$t"
  elif [ $rc -eq 0 ] && ! echo "$out" | grep -qE "^Traceback|FAIL"; then
    echo "ok" > "$OUT/$t"
  else
    { echo "RED (rc=$rc)"
      echo "$out" | grep -E "^Traceback|FAIL|Error" | head -4 | sed 's/^/      /'
    } > "$OUT/$t"
  fi
}
export -f run_one
export OUT HERE LIMIT

echo "$TESTS" | tr ' \n' '\n\n' | grep -v '^$' \
  | xargs -P "$WORKERS" -I{} bash -c 'run_one {}'

good=0; bad=0; past=0; names=""
for t in $TESTS; do
  first=$(head -1 "$OUT/$t")
  case "$first" in
    ok)      good=$((good+1)); printf "  %-24s ok\n" "$t" ;;
    skipped) past=$((past+1)); printf "  %-24s skipped\n" "$t"
             tail -n +2 "$OUT/$t" ;;
    *)       bad=$((bad+1)); names="$names $t"
             printf "  %-24s %s\n" "$t" "$first"
             tail -n +2 "$OUT/$t" ;;
  esac
done
rm -rf "$OUT"
echo "----"
if [ $past -gt 0 ]; then
  echo "green: $good   skipped: $past   red: $bad  $names"
else
  echo "green: $good   red: $bad  $names"
fi
# A note to whoever started this and is now watching it: a full run takes
# five minutes, and watching it is five minutes of nothing. Start it in
# the background and do the next thing meanwhile -- documentation, a
# review, the next defect. Only the file under test must stay untouched
# while it runs; a snapshot in /tmp makes even that free.
echo "(started in the background? then do the next thing while it runs.)"
exit $([ $bad -eq 0 ] && echo 0 || echo 1)
