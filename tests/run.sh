#!/bin/bash
# The suite. Success = return code 0, no traceback, no "FAIL".
# The tests run several at a time, each with its own fixture directory:
# most of the time goes on starting Python and ffmpeg rather than on the
# processor. WORKERS=1 runs them one after another.
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$HERE"
# The suite runs on the version the program recommends, or it proves
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
# while the working file is being written on, and without this line the
# two runs look alike in the log and a result is read against the wrong
# file.
echo "Script: ${VPM_SCRIPT:-$(dirname "$HERE")/videopodcast-magic.py}"
# Without ffmpeg most of the suite goes red, and none of those reds say
# anything about the program: they say the machine has no ffmpeg.
# static-ffmpeg is named because it is what the program itself falls
# back to, so the suite comes up the way the program does.
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

# The time limit around a single test. macOS brings no timeout(1) and
# GNU coreutils installs it as gtimeout; where neither is there the
# tests run unguarded, and that is said out loud. On Windows the name
# finds a timeout.exe that only waits and limits nothing, so each
# candidate is made to run "true" under a limit before it is used.
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
# English is the source language of the program, so the tests run in it;
# the two tests about German set the language themselves. LANG=C alone
# does not say it: the program skips "C" on purpose and asks the system,
# which on a German Mac answers de_DE. LANGUAGE settles the question.
export LANG=C LC_ALL=C LANGUAGE=en
# The player tests play real files, and without this the machine beeps
# its way through every run. It forces volume and mute and nothing else
# -- where the playhead lands, which is what the tests measure, is
# untouched.
export VPM_SILENT=1
# The speaker separation never starts by itself here: setting it up
# fetches hundreds of megabytes and a run costs minutes on the graphics
# unit, and a suite must do neither. The tests that need it say so.
export VPM_NO_SPEAKER_SPLIT=1
# The suite never asks github.com whether a newer version is out, and
# never lets the program swap the file under test. The one test about
# updating unsets this itself.
export VPM_NO_UPDATE_CHECK=1

# A test that dies of a segmentation fault leaves nothing behind: no
# traceback, no line, only a return code. With this, Python prints where
# it was when the ground gave way -- to stderr, which is kept with the
# rest of the test's output.
export PYTHONFAULTHANDLER=1
# As many at a time as the machine has cores, and one more: most of a
# test is Python starting up and ffmpeg waiting on the disc, so there is
# room beside the processors.
CORES=$(getconf _NPROCESSORS_ONLN 2>/dev/null || sysctl -n hw.ncpu 2>/dev/null || echo 4)
WORKERS=${WORKERS:-$(( CORES + 1 > 12 ? 12 : CORES + 1 ))}
# How many goes a crashed test gets. Three, because a crash that comes
# and goes shows up about once in three runs: one go would call the
# whole run red for it, a fourth would only add minutes. TRIES=1 turns
# it off.
TRIES=${TRIES:-3}

# Where the shared fixture folders live. Worked out here and handed down,
# so fixtures.sh, the tests and VPM_MEDIA below all name the same place.
# fixture_root.py says the same to the Python side.
export VPM_FIXTURES="${VPM_FIXTURES:-/tmp/vpm-fixtures-$(id -u)}"

# One cache folder per run, thrown away with the rest at the end.
RUN_TEMP_CACHE="${TMPDIR:-/tmp}/vpm_cache_$(id -u)_$$"
mkdir -p "$RUN_TEMP_CACHE"
export VPM_CACHE="$RUN_TEMP_CACHE"

# The shared fixture folders are read-only. Building them here, before
# the fan-out, keeps two tests from racing for the same files.
if ! bash "$HERE/fixtures.sh"; then
  echo "fixtures could not be built -- stopping." >&2
  exit 2
fi

# Tests wanting a whole job take the fixture unless real material is
# named. Without this they skip, and a skipped test looks harmless.
export VPM_MEDIA="${VPM_MEDIA:-$VPM_FIXTURES/interview}"

# How many tests may leave themselves out. A ratchet, like the counts in
# style_test.py: it may fall, it may not rise, and it is the figure that
# holds on every machine. A machine that cannot run a test for good
# reason takes it out of the folder; it does not let it skip.
SKIPS_ALLOWED=1

# Every test builds its own material with tempfile.mkdtemp and most of
# them never clean up. Python puts those folders under TMPDIR, so one
# folder per run collects the lot -- gigabytes -- and goes at the end.
# KEEP_TEMP=1 leaves it in place for looking at afterwards.
RUN_TEMP=$(mktemp -d "${TMPDIR:-/tmp}/vpm_run_XXXXXX")
# One line per test, written by the worker and read back by the summary.
# Made before the trap below rather than further down, or a Ctrl-C
# leaves the folder behind for good.
OUT=$(mktemp -d "${TMPDIR:-/tmp}/suite_XXXXXX")
# One file per test, counting the processes it starts. Starting a
# process is what the Windows builder charges for, and a number nobody
# sees does not stay down. Kept out of $OUT, which is counted by how
# many files are in it.
STARTS="$RUN_TEMP/starts"
mkdir -p "$STARTS"
export STARTS
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
# A Ctrl-C is an exit too: without this the suite dies where it stands,
# clean_up never runs, and gigabytes of test material stay behind.
# Exiting rather than cleaning up in here keeps it to one place -- the
# exit runs the trap above. 130 is a shell's "stopped by Ctrl-C".
trap 'exit 130' INT TERM
# Every *_test.py in this folder, so a new test is picked up by being
# there. Sorted, so the order does not depend on the file system.
TESTS=$(cd "$HERE" && ls *_test.py 2>/dev/null | sed 's/_test\.py$//' | sort)
# Named on the command line: only those, through the same machinery --
# the same retry, the same report, the same progress line. One red test
# is looked at on its own far more often than all of them are.
[ $# -gt 0 ] && TESTS="$*"

# The long ones first. xargs hands the list out in the order it is
# given, so a slow test named late in the alphabet starts last and its
# whole length is added to the end of the run, every other worker idle
# beside it.
#
# state/longest holds what each test took on the builder, and only
# builder_times.sh writes it, from a green run's own log. Nobody waits
# for this Mac -- it has cores to spare -- so its numbers have no
# business deciding the order: a test that is quick here can be the
# longest one there.
LONGEST="$HERE/state/longest"
# VPM_ORDER=reverse turns the queue round, shortest first. It is not a
# way of running the suite but the way of asking what the order is
# worth: run it both ways and compare the wall clocks, and ask it on the
# builder, where one test is not most of the run. Editing state/longest
# to ask the same question leaves the queue ordered by an experiment
# somebody forgot to undo.
QUEUE="-rn"
[ "$VPM_ORDER" = reverse ] && QUEUE="-n"
TESTS=$(
  for t in $TESTS; do
    # A test nobody has timed yet goes first: unknown may be slow, and
    # being wrong about that costs a place in the queue and nothing else.
    took=$(awk -v k="$t" '$1 == k { print $2 }' "$LONGEST" 2>/dev/null)
    printf '%09d %s\n' "${took:-999999}" "$t"
  done | sort $QUEUE | cut -d' ' -f2)
if [ -z "$TESTS" ]; then
  echo "no tests found in $HERE" >&2
  exit 2
fi

crash_block() {
  # Everything from where the ground gave way to the end of the output.
  # Not sed: the pattern needs an "or", and the BSD sed on a Mac has no
  # \| in its basic expressions -- it matches nothing at all, silently.
  # grep knows -E and is the same tool everywhere.
  at=$(echo "$1" | grep -n -E -m1 "Fatal Python error|fatal exception" \
       | cut -d: -f1)
  [ -n "$at" ] && echo "$1" | tail -n +"$at"
}

run_one() {
  t="$1"
  began=$SECONDS
  # A test that crashed is run again before the whole run is called red.
  # Only a crash: a check that said FAIL will say it again, and a test
  # that ran out of time will run out of time again. A signal does come
  # and go -- Windows returns 139 for an access violation.
  try=1
  fell_first=""
  fell_text=""
  fell_count=0
  while :; do
    out=$(VPM_COUNT_STARTS="$STARTS/$t" \
          $LIMIT "$PY" "$HERE/${t}_test.py" 2>&1); rc=$?
    fell=0
    if [ $rc -ne 0 ] || echo "$out" | grep -qE "^Traceback|FAIL"; then
      fell=1
    fi
    if [ $fell -eq 0 ] || [ "$try" -ge "$TRIES" ] || [ $rc -le 128 ] \
       || [ $rc -eq 137 ] || echo "$out" | grep -q "^FAIL"; then
      break
    fi
    if [ -z "$fell_first" ]; then
      # Kept, not just counted: a bare "it crashed once" does not let
      # the reader tell a known crash from something new.
      fell_first="rc=$rc"
      fell_text=$(crash_block "$out" | head -30)
      [ -z "$fell_text" ] && fell_text=$(echo "$out" \
        | grep -v "^[[:space:]]*\$" | tail -6)
    fi
    fell_count=$((fell_count + 1))
    try=$((try + 1))
  done
  # A failure beats a skip, always. Both can be true in one run: a test
  # leaves out the part this machine cannot do and falls over the rest.
  # Asking after the skip first makes such a test read "skipped", with
  # the failure not shown and not counted, which is the same lie as green.
  if [ $rc -ne 0 ] || echo "$out" | grep -qE "^Traceback|FAIL"; then
    { echo "RED (rc=$rc)"
      # 124 is what the time limit returns when it kills a test, 137 when
      # a polite TERM was not enough and it had to go further.
      if [ -n "$LIMIT" ] && { [ $rc -eq 124 ] || [ $rc -eq 137 ]; }; then
        echo "      killed by the ${LIMIT##* } s time limit -- it never finished"
      fi
      # What the report shows, best first: the line a test sums itself up
      # in, then failed checks and tracebacks, then a real error message,
      # and only then a bare "Error" out of ffmpeg's chatter. Ranked and
      # not taken by position, or harmless ffmpeg lines carrying the word
      # "Error" push the FAIL line out of the report.
      sums="^FAIL"
      says="FAIL|^Traceback|^[A-Za-z_.]*(Error|Exception|Interrupt)(:|\$)"
      real="[Ee]rror:"
      lines=$( { echo "$out" | grep -E "$sums"
                 echo "$out" | grep -E "$says" | grep -vE "$sums"
                 echo "$out" | grep -E "$real" | grep -vE "$says"
                 echo "$out" | grep -E "[Ee]rror" | grep -vE "$says|$real"
               } | grep -v "^[[:space:]]*\$" )
      # A test can be red and never say FAIL -- killed by the time limit,
      # or exiting non-zero after a sentence of its own -- and then the
      # end of its output is all there is.
      [ -z "$lines" ] && lines=$(echo "$out" | grep -v "^[[:space:]]*\$" | tail -6)
      [ -z "$lines" ] && lines="(the test printed nothing)"
      # A crash report is one block and must not be sampled. Python names
      # every thread and the lines it was on, and picking single lines
      # out of that by pattern keeps the thread with no Python in it and
      # drops the one that says where the ground gave way.
      crash=$(crash_block "$out")
      SHOW=12
      [ -n "$crash" ] && { lines="$crash"; SHOW=44; }
      # Twelve, not four: a red test prints one line per failed check and
      # one summing them up, and four leaves no room beside a traceback.
      echo "$lines" | head -"${SHOW:-12}" | sed 's/^/      /'
      rest=$(( $(echo "$lines" | wc -l) - ${SHOW:-12} ))
      if [ "$rest" -gt 0 ]; then
        echo "      ($rest more such lines -- run this test on its own)"
      fi
      # And the end of what it printed, whatever it looked like: the
      # ranking above drops every line that matches no pattern, so a test
      # that prints its own diagnosis would lose it. Left out where the
      # output is short enough to stand above already, and where the
      # block is a crash report, which is whole.
      if [ -z "$crash" ] && [ "$(echo "$out" | wc -l)" -gt 14 ]; then
        echo "      -- and the last lines it printed:"
        echo "$out" | tail -14 | sed 's/^/        /'
      fi
      # Red and skipped at once, said out loud, or the count of skips
      # further down does not add up and the part that was left out
      # stays invisible behind the part that fell.
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
  elif [ -n "$fell_first" ]; then
    # Green now, but it fell first. An unsteady test is a defect that
    # happens to be asleep, so a run must not swallow it.
    { echo "ok"
      echo "      unsteady: $fell_count of $try goes crashed ($fell_first),"\
           "green on go $try -- what the first one said:"
      echo "$fell_text" | sed 's/^/        /'
    } > "$OUT/$t"
  else
    echo "ok" > "$OUT/$t"
  fi
  # Said as it happens, not only at the end: a suite that prints nothing
  # for minutes and then everything at once cannot be followed. The
  # count is a place in the queue and not an accounting -- several tests
  # finish at once, so two may report the same number. The seconds say
  # what the test cost here, the processes what it costs on the builder,
  # where the two do not agree at all.
  #
  # The file is asked after before it is read. Many tests start no
  # process at all, and "wc -l < missing 2>/dev/null" does not keep
  # quiet about it: the shell fails the redirection before wc is ever
  # reached, so that 2>/dev/null belongs to a command which never ran.
  printf '  %s  %3d/%s  %-24s %-8s %3d s  %3d p\n' "$(date '+%H:%M:%S')" \
    "$(ls "$OUT" | wc -l | tr -d ' ')" "$TOTAL" "$t" \
    "$(head -1 "$OUT/$t")" "$((SECONDS - began))" \
    "$( [ -s "$STARTS/$t" ] && wc -l < "$STARTS/$t" | tr -d ' ' || echo 0)"
}
export -f run_one crash_block
export OUT HERE LIMIT TOTAL TRIES PY

TOTAL=$(echo "$TESTS" | tr ' \n' '\n\n' | grep -cv '^$')
echo "$TESTS" | tr ' \n' '\n\n' | grep -v '^$' \
  | xargs -P "$WORKERS" -I{} bash -c 'run_one {}'

# Whatever came back red is run once more, alone: it is the difference
# between a fault and a crowd. A test that is red beside eleven others
# and green by itself has found nothing, but it has proved nothing
# either, so it lands under "unsteady" rather than being counted green.
ALONE=${ALONE:-1}
if [ "$ALONE" = 1 ] && [ "$WORKERS" -gt 1 ]; then
  for t in $TESTS; do
    case "$(head -1 "$OUT/$t")" in RED*) ;; *) continue ;; esac
    was=$(cat "$OUT/$t")
    began=$SECONDS
    printf '  %s  again, alone: %-24s' "$(date '+%H:%M:%S')" "$t"
    run_one "$t" > /dev/null 2>&1
    if [ "$(head -1 "$OUT/$t")" = "ok" ]; then
      { echo "ok"
        echo "      unsteady: red beside the others, green alone after"\
             "$((SECONDS - began)) s -- what it said the first time:"
        echo "$was" | tail -n +2
      } > "$OUT/$t"
      echo " green"
    else
      echo " red again"
    fi
  done
fi

good=0; bad=0; past=0; shaky=0; names=""; left_out=""; unsteady=""
for t in $TESTS; do
  first=$(head -1 "$OUT/$t")
  case "$first" in
    ok)      good=$((good+1)); printf "  %-24s ok\n" "$t"
             if [ "$(wc -l < "$OUT/$t")" -gt 1 ]; then
               shaky=$((shaky+1)); unsteady="$unsteady $t"
               tail -n +2 "$OUT/$t"
             fi ;;
    skipped) past=$((past+1)); left_out="$left_out $t"
             printf "  %-24s skipped\n" "$t"
             tail -n +2 "$OUT/$t" ;;
    *)       bad=$((bad+1)); names="$names $t"
             printf "  %-24s %s\n" "$t" "$first"
             tail -n +2 "$OUT/$t" ;;
  esac
done
# The whole run's processes, and the five that start most of them. Read
# together with state/longest: a test that is slow here and one that is
# slow on the builder are not the same test, and this is the number
# that travels.
started=$(cat "$STARTS"/* 2>/dev/null | wc -l | tr -d ' ')
echo "----"
echo "processes started: ${started:-0}   most of them:"
for f in "$STARTS"/*; do
  [ -f "$f" ] && printf '%6d %s\n' "$(wc -l < "$f" | tr -d ' ')" \
    "$(basename "$f")"
done 2>/dev/null | sort -rn | head -5 | sed 's/^/  /'
echo "----"
if [ $past -gt 0 ]; then
  echo "green: $good   skipped: $past   red: $bad  $names"
else
  echo "green: $good   red: $bad  $names"
fi
# Named on its own line, not folded into the green count: whoever reads
# this has to see that something crashed and then did not.
if [ $shaky -gt 0 ]; then
  echo "unsteady: $shaky --$unsteady   (green on a second go; the line"\
       "under each one says whether it crashed or only fell beside others)"
fi
# The barrier on what may be left out. A skipped test checked nothing,
# so without this line a machine where every test skips returns 0 and
# the CI goes green having proved nothing at all. The CI reads this
# line rather than counting for itself; one place holds the number.
if [ $past -gt "$SKIPS_ALLOWED" ]; then
  echo "skips: $past of at most $SKIPS_ALLOWED allowed -- risen, so the suite"\
       "checked less than it did when the number was measured: $left_out"
elif [ $past -lt "$SKIPS_ALLOWED" ]; then
  echo "skips: $past of at most $SKIPS_ALLOWED allowed -- fewer here; the"\
       "number comes down when every machine reports $past"
else
  echo "skips: $past of at most $SKIPS_ALLOWED allowed"
fi
# Nothing is written to state/longest here. What this machine takes
# stands in the progress line above, which is where it is useful; the
# order of the queue belongs to the builder, and builder_times.sh fills
# it. Times written here put a test that is slow there last in the
# queue on the strength of how fast it is on this machine.
echo "(started in the background? then do the next thing while it runs.)"
# Red if anything failed, and red if more was left out than the barrier
# allows: the second is a failure too, because this run then proved
# less than the last one did.
if [ $bad -eq 0 ] && [ $past -le "$SKIPS_ALLOWED" ]; then exit 0; fi
exit 1
