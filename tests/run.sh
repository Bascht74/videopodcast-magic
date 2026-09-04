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
echo "Script: ${VPM_SCRIPT:-$(dirname "$HERE")/videopodcast_magic/__init__.py}"
# Without ffmpeg most of the suite goes red, and none of those reds say
# anything about the program: they say the machine has no ffmpeg. The
# program brings none of its own either -- it names the package manager
# and stops -- so the way out named here is the way out it names.
for tool in ffmpeg ffprobe; do
  if ! command -v "$tool" > /dev/null 2>&1; then
    echo "$tool is not on the search path. Almost every test needs it,"
    echo "and without it their red says nothing about the program."
    echo
    echo "  brew install ffmpeg              (macOS)"
    echo "  apt install ffmpeg               (Debian, Ubuntu)"
    echo
    echo "Or let the program ask for it: VPM_INSTALL_TOOLS=1 answers the"
    echo "question with yes, and it installs over the package manager."
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

# And one settings folder per run, thrown away with it. A cache and a
# choice are two things: a test that wants a fresh cache may want a
# settings file that stands, so they are two variables. Without this,
# VPM_SILENT alone makes the store refuse a place, and no test writes.
RUN_TEMP_SETTINGS="${TMPDIR:-/tmp}/vpm_settings_$(id -u)_$$"
mkdir -p "$RUN_TEMP_SETTINGS"
export VPM_SETTINGS="$RUN_TEMP_SETTINGS"

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
# source_limits_hold_test.py: it may fall, it may not rise, and it is the figure that
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
# One file per test again, holding the number of judgements it printed.
# The summary reads them back and carries state/checks forward, and a
# worker cannot hand a number up any other way: it runs in a shell of
# its own.
COUNTS="$RUN_TEMP/counts"
mkdir -p "$COUNTS"
export COUNTS
export TMPDIR="$RUN_TEMP"
clean_up() {
  if [ -n "$KEEP_TEMP" ]; then
    echo "temporary material kept in $RUN_TEMP"
    echo "cache of this run kept in $RUN_TEMP_CACHE"
    echo "settings of this run kept in $RUN_TEMP_SETTINGS"
    echo "what each test reported kept in $OUT"
  else
    rm -rf "$RUN_TEMP" "$RUN_TEMP_CACHE" "$RUN_TEMP_SETTINGS" "$OUT"
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
# WHOLE says whether this run saw the whole folder. A baseline may only
# be set by one that did: a run of three tests that wrote state/checks
# would leave the file no longer empty, and every test it never saw
# would then be red for never having been counted.
WHOLE=1
[ $# -gt 0 ] && { TESTS="$*"; WHOLE=0; }

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

# What each test judged when it last ran. Every test ends on a line of
# its own -- "21 checks in 0.05 s" -- and until now nobody read it: a
# test whose checking part dies without throwing prints "0 checks in
# 2.74 s", then "All good.", and leaves green, and that line was the
# only thing in the whole run saying nothing had been checked. Held to a
# floor here, per test, so it is the run that notices and not a person
# reading.
#
# Both kinds of row go into one string apiece rather than being looked
# up in the file 146 times over. The lookup in run_one is then a shell
# expansion and costs no process at all, which is what a step taken once
# per test can afford.
CHECKS="$HERE/state/checks"
FLOORS="|"
SILENT="|"
# Asked after before it is read. A redirection that cannot be opened is
# the shell's own complaint, not the loop's, so a 2>/dev/null on the
# loop never silences it -- and a missing state file would print a line
# that looks like a fault in the suite.
if [ -f "$CHECKS" ]; then
  while read -r what which rest; do
    case "$what" in ""|"#"*) continue ;; esac
    if [ "$what" = silent ]; then
      SILENT="$SILENT$which|"
    else
      FLOORS="$FLOORS$what=$which|"
    fi
  done < "$CHECKS"
fi
# Nothing to hold anything to. Said out loud and then measured, the way
# ratchet.py answers a state file that is not there: a run that silently
# held nothing would look exactly like a run that held everything.
CHECKS_FRESH=0
if [ "$FLOORS$SILENT" = "||" ]; then
  CHECKS_FRESH=1
  if [ "$WHOLE" = 1 ]; then
    echo "NOTE: state/checks holds no floors yet. They are being taken"
    echo "      from this run, and no test is held to a count in it."
  else
    echo "NOTE: state/checks holds no floors yet, and this run is only"
    echo "      part of the folder. Nothing is held and nothing written."
    echo "      One run of the whole suite sets them."
  fi
fi
export CHECKS FLOORS SILENT CHECKS_FRESH

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
  # How many judgements the test says it reached. The last such line it
  # printed: three tests have a short way out that prints the same
  # closing line early, and every one of those ways ends in FAIL anyway.
  judged=$(printf '%s\n' "$out" \
    | awk '/^[0-9]+ checks in /{ n = $1 } END { if (n != "") print n }')
  printf '%s\n' "$judged" > "$COUNTS/$t"
  floor=""
  case "$FLOORS" in
    *"|$t="*) floor=${FLOORS#*"|$t="}; floor=${floor%%|*} ;;
  esac
  # Only asked of a test that claims to have run. Red is red already,
  # and a test that printed SKIPPED: is not counted green anyway -- it
  # has named the piece it could not do, and fewer judgements follow
  # from that rather than from anything being wrong.
  if [ "$rc" -eq 0 ] \
     && ! printf '%s\n' "$out" | grep -qE "^Traceback|FAIL|^SKIPPED:"; then
    short=""
    if [ -n "$floor" ] && [ -z "$judged" ]; then
      short="FAIL the test got as far as its closing line -- it printed no count of judgements, where $floor were counted last time"
    elif [ -n "$floor" ] && [ "$judged" -eq 0 ]; then
      short="FAIL the test judged anything at all -- 0 judgements against $floor last time"
    elif [ -n "$floor" ] && [ "$judged" -lt "$floor" ] \
         && ! printf '%s\n' "$out" | grep -qE '^ *(LEFT OUT|Left out)'; then
      short="FAIL the test reached all of its judgements -- $judged against $floor last time, and it left no piece out"
    elif [ -z "$floor" ] && [ -z "$judged" ] && [ "$CHECKS_FRESH" != 1 ]; then
      case "$SILENT" in
        *"|$t|"*) ;;
        *) short="FAIL the test says how much it judged -- it printed no count, and state/checks holds neither a floor nor a silent row for it" ;;
      esac
    fi
    # Written into the test's own output rather than kept beside it, so
    # everything below -- the verdict, the ranking that puts a summing-up
    # line first, the retry alone -- treats it as the test's own FAIL.
    if [ -n "$short" ]; then
      out="$out
$short"
    fi
  fi
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
    # A green test may still have left a piece out -- no network, no
    # model, an ffmpeg without the option it needed. The line saying so
    # was the only trace of it, and throwing a green test's output away
    # threw that away too. Its own first word, so the summary does not
    # take it for a test that crashed and came back.
    left=$(echo "$out" | grep -E '^ *(LEFT OUT|Left out)' | head -3)
    if [ -n "$left" ]; then
      { echo "partial"
        echo "$left" | sed 's/^ *//; s/^/      /'
      } > "$OUT/$t"
    else
      echo "ok" > "$OUT/$t"
    fi
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

# A test that measures real time cannot share the machine. Playing a
# second of sound takes a second; beside eleven others it took sixteen
# and reached a fifth of a second, and no waiting fixes that. These run
# by themselves, at the end, when everything else is done.
ALONE_ONLY="cut_player_in_sync"
CROWD=$(echo "$TESTS" | tr ' \n' '\n\n' | grep -v '^$')
for t in $ALONE_ONLY; do
  CROWD=$(echo "$CROWD" | grep -vx "$t" || true)
done
TOTAL=$(echo "$TESTS" | tr ' \n' '\n\n' | grep -cv '^$')
echo "$CROWD" | grep -v '^$' \
  | xargs -P "$WORKERS" -I{} bash -c 'run_one {}'
for t in $ALONE_ONLY; do
  echo "$TESTS" | tr ' \n' '\n\n' | grep -qx "$t" && run_one "$t"
done

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
half=0; halved=""
for t in $TESTS; do
  first=$(head -1 "$OUT/$t")
  case "$first" in
    ok)      good=$((good+1)); printf "  %-24s ok\n" "$t"
             if [ "$(wc -l < "$OUT/$t")" -gt 1 ]; then
               shaky=$((shaky+1)); unsteady="$unsteady $t"
               tail -n +2 "$OUT/$t"
             fi ;;
    partial) good=$((good+1)); half=$((half+1)); halved="$halved $t"
             printf "  %-24s ok, but left a piece out\n" "$t"
             tail -n +2 "$OUT/$t" ;;
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
# Counted green, because what they did check held. Named all the same:
# a piece nobody sees left out is a piece nobody knows is missing.
if [ $half -gt 0 ]; then
  echo "left a piece out: $half --$halved   (the line under each one"\
       "says which piece, and why it could not be checked here)"
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
# state/checks carried forward. The count of judgements rises with every
# check anybody adds, so a floor kept by hand would be behind within the
# day and then be raised in a hurry, which is how a floor stops meaning
# anything. A green test that judged more than its floor writes the new
# number down itself.
#
# Upwards only, and only out of a test that came back green. A count
# that fell is red above, and a red test's number is never written back,
# so a floor cannot come down except through somebody's edit -- where a
# diff shows it, and the test is named beside the number.
counting=0
nocount=0
raised=""
census=""
for t in $TESTS; do
  judged=$(cat "$COUNTS/$t" 2> /dev/null)
  if [ -z "$judged" ]; then
    nocount=$((nocount + 1))
    # The first run writes the census too. A floor of nought would be a
    # lie about these: they report nothing, so nothing holds them, and
    # that is what the row says. Only on the first run -- afterwards a
    # test that stops counting is red rather than quietly enrolled.
    # Whatever the verdict was: a test that is red today still reports
    # no count, and leaving it out here would make it red tomorrow for
    # a reason that has nothing to do with it.
    [ "$CHECKS_FRESH" = 1 ] && census="$census $t"
    continue
  fi
  case "$(head -1 "$OUT/$t")" in ok|partial) ;; *) continue ;; esac
  counting=$((counting + 1))
  floor=""
  case "$FLOORS" in
    *"|$t="*) floor=${FLOORS#*"|$t="}; floor=${floor%%|*} ;;
  esac
  if [ -z "$floor" ] || [ "$judged" -gt "$floor" ]; then
    raised="$raised $t=$judged"
  fi
done
# A baseline set by half a run is worse than none: see WHOLE above.
if [ "$CHECKS_FRESH" = 1 ] && [ "$WHOLE" != 1 ]; then
  raised=""
  census=""
fi
# This net reaches as far as the tests that report a count, and no
# further. The rest is a hole with a number written on it rather than a
# hole nobody sees. Both numbers come out of this run and not out of the
# file: a test that this very run promoted out of the census would
# otherwise still be counted among the silent ones.
echo "judgements: $counting tests reported a count and were held to it,"\
     "$nocount report none (state/checks)"
if [ -n "$raised$census" ] && "$PY" -c \
     'import ratchet, sys; sys.exit(0 if ratchet.state_is_ours() else 1)' \
     2> /dev/null; then
  # The file as it stands, then this run's rows, then one row per test.
  # Sorting alone is not enough: several suites run side by side here,
  # and two of them writing the census at once wrote it twice over --
  # 248 rows where there are 124 tests. So the rows are folded by name,
  # which also makes writing the file twice change nothing the second
  # time.
  { grep '^#' "$CHECKS" 2> /dev/null
    { grep -v '^#' "$CHECKS" 2> /dev/null
      for r in $raised; do printf '%s\t%s\n' "${r%%=*}" "${r#*=}"; done
      for t in $census; do printf 'silent\t%s\n' "$t"; done
    } | awk -F'\t' '
        NF < 2 { next }
        $1 == "silent" { quiet[$2] = 1; next }
        # Of two numbers for one test the larger stands. Two runs
        # writing at once can then lose a raise, never a floor.
        { if (!($1 in floor) || $2 + 0 > floor[$1] + 0) floor[$1] = $2 + 0 }
        END {
          # A test that reports a number is out of the census by that
          # fact, wherever its rows stood in the file.
          for (k in floor) printf "%s\t%d\n", k, floor[k]
          for (k in quiet) if (!(k in floor)) printf "silent\t%s\n", k
        }' | sort
  # A name of its own, not a fixed one: several suites run side by side
  # here, and two of them writing state/checks.new at once wrote into
  # one file and lost the head of it. The move is what makes the change
  # visible, and a move is one step.
  } > "$CHECKS.$$" && mv "$CHECKS.$$" "$CHECKS"
  # A floor raised out of a file somebody is still writing is a floor set
  # by half a thought. The run cannot know whether the edit is finished,
  # so it does not refuse the raise -- it says so beside it.
  if [ -n "$raised" ]; then
    echo "state/checks: raised --$raised"
    for r in $raised; do
      git -C "$HERE" status --porcelain -- "${r%%=*}_test.py" 2> /dev/null \
        | sed 's|^...|state/checks: raised out of a file that is not saved: |'
    done
  fi
  [ -n "$census" ] && echo "state/checks: written from this run --"\
    "$(echo $census | wc -w | tr -d ' ') tests report no count"
fi
# Nothing is written to state/longest here. What this machine takes
# stands in the progress line above, which is where it is useful; the
# order of the queue belongs to the builder, and builder_times.sh fills
# it. Times written here put a test that is slow there last in the
# queue on the strength of how fast it is on this machine.

# The tests under resolve/ talk to a DaVinci Resolve really running on
# this machine. They are not in this folder, so nothing above collected
# them, counted them or judged them -- they are not skipped, they are
# not part of this run at all, and the skips barrier must never hear of
# them. The only thing that starts them is a person, and a person
# forgets. So the run says at the end that they are there.
#
# Said after everything is counted and printed, and in a line that
# begins with none of the words anything reads: run_one judges each
# test's own output, not this one, and the CI report lifts "green:" and
# "skips:" out of the log by name.
#
# Not on the builder. No runner has a Resolve, "start them by hand" is
# an instruction nobody there can follow, and tests.yml already says
# where it belongs -- in the step that sets tests aside. CI and
# GITHUB_ACTIONS are both set by GitHub; neither is set here.
if [ -z "${CI:-}" ] && [ -z "${GITHUB_ACTIONS:-}" ] && [ -d "$HERE/resolve" ]
then
  apart=$(ls "$HERE"/resolve/*_test.py 2>/dev/null | wc -l | tr -d ' ')
  # Sharper when the Resolve branch has just been worked on: a line that
  # reads the same every day is read once. Two signals, both out of git,
  # both without guesswork -- work under those paths not committed yet,
  # and the newest commit touching them being the one this run stands
  # on. What the program's own diff says was measured and thrown away:
  # over 40 commits, "a changed line in videopodcast-magic.py naming
  # Resolve" fired three times and every one of the three was a comment
  # or a key name, while no commit in those 40 changed the Resolve code
  # itself. A sharp line that is wrong three times in forty is noise.
  #
  # Where there is no git and no repository both questions come back
  # empty and the plain line stands.
  touched=""
  if command -v git > /dev/null 2>&1 \
     && git -C "$HERE" rev-parse --git-dir > /dev/null 2>&1; then
    # Named, not counted: "something changed" sends whoever reads it
    # looking for what. Three names and then a number, because the line
    # is a reminder and not a listing.
    changed=$(git -C "$HERE" status --porcelain -- resolve resolve.sh \
              2>/dev/null | sed 's/^...//' | grep -c . )
    if [ "${changed:-0}" -gt 0 ]; then
      touched=$(git -C "$HERE" status --porcelain -- resolve resolve.sh \
                2>/dev/null | sed 's/^...//' | head -3 | tr '\n' ' ' \
                | sed 's/ *$//')
      [ "$changed" -gt 3 ] && touched="$touched and $((changed - 3)) more"
    else
      # Asked for, not derived from HEAD~1: a repository whose first
      # commit is its only one has no HEAD~1, and a run there must not
      # break. An unborn HEAD answers nothing at all, which is why the
      # emptiness is asked after rather than compared.
      was=$(git -C "$HERE" log -1 --format=%H -- resolve resolve.sh \
            2>/dev/null)
      now=$(git -C "$HERE" rev-parse HEAD 2>/dev/null)
      [ -n "$was" ] && [ "$was" = "$now" ] \
        && touched="the commit this run stands on"
    fi
  fi
  if [ "$apart" -gt 0 ] && [ -n "$touched" ]; then
    echo "resolve: $apart tests under resolve/ did not run here, and the"
    echo "         Resolve branch has been worked on: $touched"
    echo "         Nothing but a person starts them, and they want a"
    echo "         Resolve running:"
    echo "             cd tests && bash resolve.sh"
  elif [ "$apart" -gt 0 ]; then
    echo "resolve: $apart tests under resolve/ did not run here. They talk"
    echo "         to a DaVinci Resolve really running, so a person"
    echo "         starts them:"
    echo "             cd tests && bash resolve.sh"
  fi
fi
echo "(started in the background? then do the next thing while it runs.)"
# Red if anything failed, and red if more was left out than the barrier
# allows: the second is a failure too, because this run then proved
# less than the last one did.
if [ $bad -eq 0 ] && [ $past -le "$SKIPS_ALLOWED" ]; then exit 0; fi
exit 1
