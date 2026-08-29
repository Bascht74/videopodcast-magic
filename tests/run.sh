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
# And which file was measured. VPM_SCRIPT sends a run against a snapshot
# in /tmp, which is how the suite runs while the working file is being
# written on. Unsaid, the two runs look exactly alike in the log, and a
# result gets read against the wrong file. Said, it costs one line.
echo "Script: ${VPM_SCRIPT:-$(dirname "$HERE")/videopodcast-magic.py}"
# Without ffmpeg most of the suite goes red, and none of those reds say
# anything about the program: they say the machine has no ffmpeg. One
# sentence beats thirty-eight of them. static-ffmpeg is named because it
# is what the program itself falls back to, so the suite can be brought
# up the same way the program comes up on a bare machine.
for tool in ffmpeg ffprobe; do
  if ! command -v "$tool" > /dev/null 2>&1; then
    echo "$tool is not on the search path. Almost every test needs it,"
    echo "and without it their red says nothing about the program."
    echo
    echo "  brew install ffmpeg              (macOS)"
    echo "  apt install ffmpeg               (Debian, Ubuntu)"
    echo
    echo "Or let the program do it: VPM_INSTALL_TOOLS=1 answers the"
    echo "question with yes, and it installs over the package manager."
    echo
    echo "Or the one it falls back to, into this Python:"
    echo "  $PY -m pip install static-ffmpeg"
    echo "  $PY -c 'import static_ffmpeg; static_ffmpeg.add_paths()'"
    echo "The second line prints where the binaries went; put that"
    echo "folder on PATH for the run."
    exit 2
  fi
done

# The time limit around a single test. macOS brings no timeout(1); GNU
# coreutils installs the same program under the name gtimeout. Where
# neither is there the tests run unguarded, and that is said out loud
# rather than passed over: a hung test would otherwise stop the suite
# with nothing to show for it.
#
# And the name is not asked, the program is. On Windows the name finds
# C:\Windows\System32\timeout.exe, which is a different program: it
# waits for a number of seconds, it does not put a limit on anything.
# The suite would then run every test through a pause. The CI names the
# same trap for find(1); this is the same trap one door along. So each
# candidate is made to do the thing itself -- run "true" under a limit --
# and only the one that comes back happy is used.
LIMIT=""
for candidate in timeout gtimeout; do
  command -v "$candidate" > /dev/null 2>&1 || continue
  if "$candidate" 5 true > /dev/null 2>&1 < /dev/null; then
    LIMIT="$candidate 900"; break
  fi
  echo "$candidate is on the search path, but it does not limit a run to"
  echo "  a number of seconds -- on Windows that is the system's own"
  echo "  timeout.exe, which only waits. Looking for another one."
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
# The speaker separation never starts by itself here. Setting it up
# fetches 218 MB, and a run takes minutes on the graphics unit -- a
# suite must do neither. The tests that need it say so themselves.
export VPM_NO_SPEAKER_SPLIT=1
# The suite never asks github.com whether a newer version is out, and
# it certainly never lets the program swap the file under test. The one
# test about updating unsets this itself and answers with a table.
export VPM_NO_UPDATE_CHECK=1

# A test that dies of a segmentation fault leaves nothing behind: no
# traceback, no line, only rc=139. With this, Python prints where it
# was when the ground gave way -- to stderr, which is kept with the
# rest of the test's output. Measured 29.8.2026: block_remove died
# this way on Windows with Python 3.10 and was green on 3.14 of the
# same machine, three runs in a row, and there was nothing to read.
export PYTHONFAULTHANDLER=1
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

# One cache folder per run, thrown away with the rest at the end.
RUN_TEMP_CACHE="${TMPDIR:-/tmp}/vpm_cache_$(id -u)_$$"
mkdir -p "$RUN_TEMP_CACHE"
export VPM_CACHE="$RUN_TEMP_CACHE"

# Three fixture folders are shared and read-only. Building them here,
# before the fan-out, keeps two tests from racing for the same files.
if ! bash "$HERE/fixtures.sh"; then
  echo "fixtures could not be built -- stopping." >&2
  exit 2
fi

# Tests wanting a whole job take the fixture unless real material is
# named. Without this they skip, and a skipped test looks harmless.
export VPM_MEDIA="${VPM_MEDIA:-$VPM_FIXTURES/interview}"

# How many tests may leave themselves out. A ratchet, like the counts in
# style_test.py: it may fall, it may not rise. Checked at the bottom,
# where it decides the return code along with the red ones.
#
# Measured, twice, because the two machines do not agree:
#
#   1 is what the CI reported -- all four jobs of run 32875834901 on
#     25 Aug 2026, on every system and both Python versions, every one
#     of them speakers_for_real. That figure is read off the workflow,
#     not measured here.
#   0 is what this suite reported on the machine it was written on, on
#     28 Aug 2026: speakers_for_real ran through. Measured by running
#     the eight tests that can leave themselves out at all.
#
# The difference is one folder and not a defect: that test wants the
# separation environment, 218 MB, which a test must not fetch. Where
# somebody set it up the test runs, everywhere else it stands aside. So
# the barrier is the figure that holds on both, and it comes down to 0
# the day every machine reports 0 -- not on the strength of one.
#
# A machine that cannot run a test for good reason takes it out of the
# folder, the way the CI does; it does not let it skip.
SKIPS_ALLOWED=1

# Every test builds its own material with tempfile.mkdtemp and most of them
# never clean up. Python puts those folders under TMPDIR, so one folder per
# run collects the lot and goes at the end -- a full suite is gigabytes.
# KEEP_TEMP=1 leaves it in place for looking at afterwards.
RUN_TEMP=$(mktemp -d "${TMPDIR:-/tmp}/vpm_run_XXXXXX")
# One line per test, written by the worker and read back by the summary.
# Made here rather than further down, because from here on the trap knows
# it: a Ctrl-C used to leave /tmp/suite_XXXXXX behind for good, and a
# machine that runs the suite twenty times a day collects twenty of them.
OUT=$(mktemp -d "${TMPDIR:-/tmp}/suite_XXXXXX")
export TMPDIR="$RUN_TEMP"
clean_up() {
  if [ -n "$KEEP_TEMP" ]; then
    echo "temporary material kept in $RUN_TEMP"
    echo "cache of this run kept in $RUN_TEMP_CACHE"
    echo "what each test reported kept in $OUT"
  else
    rm -rf "$RUN_TEMP" "$RUN_TEMP_CACHE" "$OUT"
  fi
}
trap clean_up EXIT
# And a Ctrl-C is an exit too. Without this the suite dies where it
# stands and clean_up never runs: gigabytes of test material, a cache
# and the report folder stay behind, and a machine that starts the suite
# and stops it twenty times a day collects twenty of each. Exiting rather
# than cleaning up in here keeps it to one place -- the exit runs the
# trap above. 130 is the number a shell gives for "stopped by Ctrl-C".
trap 'exit 130' INT TERM
# Every *_test.py in this folder, so a new test is picked up by being
# there. Sorted, so the order does not depend on the file system.
TESTS=$(cd "$HERE" && ls *_test.py 2>/dev/null | sed 's/_test\.py$//' | sort)
if [ -z "$TESTS" ]; then
  echo "no tests found in $HERE" >&2
  exit 2
fi

run_one() {
  t="$1"
  out=$($LIMIT "$PY" "$HERE/${t}_test.py" 2>&1); rc=$?
  # A failure beats a skip, always. Both can be in one run: a test leaves
  # out the part this machine cannot do, goes on with the part it can and
  # falls over that. Asking after the skip first made such a test read
  # "skipped" -- the failure was not shown at all and did not count. That
  # is the same lie as calling it green, one room further along. So the
  # failure is asked after first, and where both are true both are said.
  if [ $rc -ne 0 ] || echo "$out" | grep -qE "^Traceback|FAIL"; then
    { echo "RED (rc=$rc)"
      # 124 is what the time limit returns when it kills a test, 137 when
      # a polite TERM was not enough and it had to go further. On its own
      # that number says nothing, and working out what it means once cost
      # ten minutes. It is one line.
      if [ -n "$LIMIT" ] && { [ $rc -eq 124 ] || [ $rc -eq 137 ]; }; then
        echo "      killed by the ${LIMIT##* } s time limit -- it never finished"
      fi
      # What the report shows, best first. A test sums itself up in its
      # last line, "FAIL: a, b" hard against the left margin -- that one
      # goes first, or twenty failed checks push it out of the way. Then
      # the checks themselves, "  check name   FAIL extra", and the first
      # and last line of a traceback. Then a real error message, the kind
      # with a colon after it. Only then a bare "Error" from the middle of
      # ffmpeg's chatter.
      #
      # It used to be one grep for "^Traceback|FAIL|Error" and the first
      # four lines of that. On Windows the first four were four harmless
      # ffmpeg lines that happened to carry the word "Error", and the FAIL
      # line below them was cut off: a red test that did not say what it
      # was red about. The rank now decides, not the position in the log.
      #
      # Each rank leaves out what a rank above it already took, so no line
      # is printed twice and within a rank the log keeps its own order.
      # grep alone does it: this went wrong on a Windows machine, and a
      # Git-Bash there is a thinner set of tools than a Mac's.
      sums="^FAIL"
      says="FAIL|^Traceback|^[A-Za-z_.]*(Error|Exception|Interrupt)(:|\$)"
      real="[Ee]rror:"
      lines=$( { echo "$out" | grep -E "$sums"
                 echo "$out" | grep -E "$says" | grep -vE "$sums"
                 echo "$out" | grep -E "$real" | grep -vE "$says"
                 echo "$out" | grep -E "[Ee]rror" | grep -vE "$says|$real"
               } | grep -v "^[[:space:]]*\$" )
      # A test can be red and never say FAIL: killed by the time limit,
      # or exiting non-zero after a sentence of its own. Then the end of
      # its output is all there is, and printing nothing would leave the
      # reader with a bare return code.
      [ -z "$lines" ] && lines=$(echo "$out" | grep -v "^[[:space:]]*\$" | tail -6)
      [ -z "$lines" ] && lines="(the test printed nothing)"
      # A crash report is one block and must not be sampled. Where the
      # ground gave way, Python names every thread and the lines it was
      # on -- and picking single lines out of that by pattern keeps the
      # one thread that has no Python in it and drops the one that does.
      # Measured 29.8.2026: three runs showed "access violation" and
      # "<no Python frame>" and nothing else, while the frames that
      # would have said where were in the same output all along.
      crash=$(echo "$out" | sed -n "/Fatal Python error\|fatal exception/,\$p")
      SHOW=12
      [ -n "$crash" ] && { lines="$crash"; SHOW=44; }
      # Twelve, not four. A red test prints one line per failed check and
      # one summing them up, and four leaves no room beside a traceback.
      echo "$lines" | head -"${SHOW:-12}" | sed 's/^/      /'
      rest=$(( $(echo "$lines" | wc -l) - ${SHOW:-12} ))
      if [ "$rest" -gt 0 ]; then
        echo "      ($rest more such lines -- run this test on its own)"
      fi
      # Red and skipped at once. Said out loud, or the reader wonders
      # why the count of skips further down does not add up, and the
      # part that was left out stays invisible behind the part that fell.
      if echo "$out" | grep -q "^SKIPPED:"; then
        echo "$out" | grep "^SKIPPED:" | head -1 \
          | sed 's/^SKIPPED: /      and it also left something out: /'
      fi
    } > "$OUT/$t"
  elif echo "$out" | grep -q "^SKIPPED:"; then
    # Nothing was checked. Green would be a lie.
    { echo "skipped"
      echo "$out" | grep "^SKIPPED:" | head -1 | sed 's/^SKIPPED: /      /'
    } > "$OUT/$t"
  else
    echo "ok" > "$OUT/$t"
  fi
  # Say it as it happens, not only at the end. A suite that prints
  # nothing for two minutes and then everything at once cannot be
  # followed -- neither by the person waiting nor by whoever reads a
  # builder's log afterwards and wants to know where it stopped.
  # Counted by what is already written: several tests finish at once,
  # so two may report the same number. It is a place in the queue, not
  # an accounting.
  printf '  %s  %3d/%s  %-24s %s\n' "$(date '+%H:%M:%S')" \
    "$(ls "$OUT" | wc -l | tr -d ' ')" "$TOTAL" "$t" "$(head -1 "$OUT/$t")"
}
export -f run_one
export OUT HERE LIMIT TOTAL

TOTAL=$(echo "$TESTS" | tr ' \n' '\n\n' | grep -cv '^$')
echo "$TESTS" | tr ' \n' '\n\n' | grep -v '^$' \
  | xargs -P "$WORKERS" -I{} bash -c 'run_one {}'

good=0; bad=0; past=0; names=""; left_out=""
for t in $TESTS; do
  first=$(head -1 "$OUT/$t")
  case "$first" in
    ok)      good=$((good+1)); printf "  %-24s ok\n" "$t" ;;
    skipped) past=$((past+1)); left_out="$left_out $t"
             printf "  %-24s skipped\n" "$t"
             tail -n +2 "$OUT/$t" ;;
    *)       bad=$((bad+1)); names="$names $t"
             printf "  %-24s %s\n" "$t" "$first"
             tail -n +2 "$OUT/$t" ;;
  esac
done
echo "----"
if [ $past -gt 0 ]; then
  echo "green: $good   skipped: $past   red: $bad  $names"
else
  echo "green: $good   red: $bad  $names"
fi
# The barrier on what may be left out, and it is a ratchet like the counts
# in style_test.py: it may fall, it may not rise. A skipped test checked
# nothing, and nothing that a suite does not check can turn it red -- so
# without this line a machine where every test skips returns 0 and the CI
# goes green having proved nothing at all.
#
# Written for reading from outside as well: the CI reads this line, it
# does not count for itself. One place holds the number, and it is here.
if [ $past -gt "$SKIPS_ALLOWED" ]; then
  echo "skips: $past of at most $SKIPS_ALLOWED allowed -- risen, so the suite"\
       "checked less than it did when the number was measured: $left_out"
elif [ $past -lt "$SKIPS_ALLOWED" ]; then
  echo "skips: $past of at most $SKIPS_ALLOWED allowed -- fewer here; the"\
       "number comes down when every machine reports $past"
else
  echo "skips: $past of at most $SKIPS_ALLOWED allowed"
fi
# A note to whoever started this and is now watching it: a full run takes
# five minutes, and watching it is five minutes of nothing. Start it in
# the background and do the next thing meanwhile -- documentation, a
# review, the next defect. Only the file under test must stay untouched
# while it runs; a snapshot in /tmp makes even that free.
echo "(started in the background? then do the next thing while it runs.)"
# Red if anything failed, and red if more was left out than the barrier
# allows. The second one is a failure too: it means this run proved less
# than the last one did.
if [ $bad -eq 0 ] && [ $past -le "$SKIPS_ALLOWED" ]; then exit 0; fi
exit 1
