#!/bin/bash
# What the tests took on the builder, written into state/longest.
#
# The order of the queue comes from state/longest, and the point of the
# order is that nobody waits. Nobody waits for this Mac -- it has cores
# to spare -- so the waiting happens on the builder and the builder's
# numbers have to get into the file. Every progress line there carries
# the seconds, but the job's disk goes when the job ends, so they are
# read back out of the log when somebody asks.
#
# One job, not all six. The six differ by a factor of two, and a
# largest-of-six would take the Windows number for one test and the
# Linux number for the next: that is two rulers, and a queue ordered
# with two rulers is not ordered. So the slowest job is asked and only
# it, because it holds every other one up. That is the Windows pair; if
# Windows ever stops being the slow one, that is the thing to act on.
#
# One run's times, not a median over several. What a run reports is
# noisy, but an order only has to know which handful of tests are the
# big ones, and that never wavers. Against knowing a run's own times in
# advance, ordering by an earlier run costs a tenth of a second, a
# median over several runs slightly more, the alphabet a seventh of the
# whole run and shortest-first half of it.
#
# The times read here are inflated, five tests running at once, but by
# much the same factor throughout -- the queue is full from end to end,
# so no test is inflated by luckier neighbours than any other -- and a
# factor that is the same everywhere moves nothing up or down.
#
# The numbers replace what stood in the file rather than being folded
# into it. Under a rule that state/longest may only rise, a test made
# three times faster keeps its old number for ever and no work on it
# can ever be shown. Tests the run did not measure keep what they had.
#
# Which job is the slowest is asked of the run, not written down here.
# It was windows-latest / py3.10 for weeks and then it was not: the
# macOS runners went from the middle of the field to twice the slowest
# of the others, and a queue ordered by yesterday's slowest machine
# orders nothing.
#
#   bash builder_times.sh                     the newest green run on main
#   bash builder_times.sh <run id>            a named run
#   JOB='macos-latest / py3.10' bash ...      one named machine
#
HERE=$(cd "$(dirname "$0")" && pwd)
LONGEST="$HERE/state/longest"
RUN="$1"

if ! command -v gh >/dev/null 2>&1; then
  echo "needs the gh command line, and it is not installed" >&2
  exit 2
fi
if [ -z "$RUN" ]; then
  # --workflow, not just the newest green run on main: since 5.9.2026
  # a second workflow answers there -- the one that takes a deleted
  # branch's caches with it -- and it has no test job at all. Without
  # the name this asked that run for its slowest test and got 'null'.
  RUN=$(gh run list --branch main --status success --workflow tests \
        --limit 1 --json databaseId --jq '.[0].databaseId' 2>/dev/null)
fi
if [ -z "$RUN" ]; then
  echo "no green run found on main" >&2
  exit 2
fi

# The slowest job of this run, by wall clock, unless one was named.
#
# Every job of the tests workflow, and no filter on the name. It used
# to keep only the ones with a "/" in them, from the day they were
# called "macos-latest / py3.14"; they are called "macOS py3.14" now,
# so the filter kept nothing and the slowest job came back as null.
if [ -z "$JOB" ]; then
  JOB=$(gh run view "$RUN" --json jobs --jq '
    [.jobs[]
     | {name, s: ((.completedAt | fromdate) - (.startedAt | fromdate))}]
    | sort_by(-.s) | .[0] | "\(.name)\t\(.s)"' 2>/dev/null)
  said=${JOB#*$'\t'}
  JOB=${JOB%%$'\t'*}
  if [ -n "$JOB" ]; then
    echo "slowest job of this run: '$JOB' at ${said} s"
  fi
fi
if [ -z "$JOB" ]; then
  echo "could not tell which job was the slowest" >&2
  exit 2
fi

log=$(mktemp); trap 'rm -f "$log"' EXIT
if ! gh run view "$RUN" --log > "$log" 2>/dev/null; then
  echo "run $RUN has no log any more -- GitHub keeps them for 90 days" >&2
  exit 2
fi

# The progress line, as run.sh prints it:
#   23:22:26   19/108  settings_window          ok        12 s   47 p
# In the CI log the job name, the step and a timestamp stand in front
# of it, tab separated, so the job is cut off the front and the line
# itself looked for anywhere in what is left.
#
# A digit is part of a test's name. It was not, and the one test whose
# name carries one was dropped from every reading in silence: the line
# that would have replaced its number never matched, so it kept the
# number it had for ever.
found=$(awk -F'\t' -v job="$JOB" '$1 == job { print }' "$log" \
        | grep -oE '[0-9]{2}:[0-9]{2}:[0-9]{2} +[0-9]+/[0-9]+ +[a-z0-9_]+ +[a-z]+ +[0-9]+ s' \
        | awk '{ print $3, $5 }')
if [ -z "$found" ]; then
  echo "run $RUN has no progress lines for '$JOB'. Either the job is"\
       "named differently there, or it did not get as far as the tests." >&2
  echo "The jobs in this run are:" >&2
  cut -f1 "$log" | sort -u | sed 's/^/  /' >&2
  exit 2
fi

count=$(echo "$found" | wc -l | tr -d ' ')
# And how many progress lines there were at all, counted by their shape
# rather than by the pattern above; the two have to agree. A pattern
# that quietly understands less than it was given looks exactly like a
# run that measured less. A test whose line was not read keeps the
# number it had, so this warns and carries on.
seen=$(awk -F'\t' -v job="$JOB" '$1 == job { print }' "$log" \
       | grep -cE '[0-9]{2}:[0-9]{2}:[0-9]{2} +[0-9]+/[0-9]+ +[^ ]')
if [ "$seen" -gt "$count" ]; then
  echo "warning: $seen progress lines for '$JOB', but only $count were"\
       "understood. The other $((seen - count)) keep the number they had."\
       "A red test reads that way too; so does a name the pattern above"\
       "does not allow for." >&2
fi
before=$( [ -f "$LONGEST" ] && awk '{ s += $2 } END { print s+0 }' "$LONGEST" || echo 0)
# The old line first, the builder's after it, and the builder's wins by
# standing later -- so a test that got faster shows it. A name with no
# test file beside it is dropped: a renamed test would otherwise hold a
# place in a queue it is no longer in.
{ [ -f "$LONGEST" ] && cat "$LONGEST" || true
  echo "$found"
} | awk -v here="$HERE" '
    { seen[$1] = $2 }
    END { for (n in seen)
            if ((getline junk < (here "/" n "_test.py")) >= 0)
              printf "%s %d\n", n, seen[n] }' \
  | sort > "$LONGEST.new" && mv "$LONGEST.new" "$LONGEST"
after=$(awk '{ s += $2 } END { print s+0 }' "$LONGEST")

echo "run $RUN, job '$JOB': $count tests measured"
echo "state/longest holds $(wc -l < "$LONGEST" | tr -d ' ') tests,"\
     "$before s before, $after s now"
echo
echo "the ten that go first from here on:"
sort -k2 -rn "$LONGEST" | head -10 | awk '{ printf "  %-24s %3d s\n", $1, $2 }'
