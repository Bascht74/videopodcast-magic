#!/bin/bash
# What the tests took on the builder, written into state/longest.
#
# The order of the queue is decided by state/longest, and the point of
# the order is to keep anybody from waiting. Nobody waits for this Mac:
# it has cores to spare and finishes the suite in half a minute. The
# waiting happens on the builder, where the same suite takes two to
# four minutes. So the order has to be right for the builder, and the
# builder's numbers have to get into the file.
#
# The builder measures already -- every progress line carries the
# seconds -- but its disk is thrown away when the job ends, so the
# numbers never come back on their own. Letting the CI commit the file
# would mean six jobs writing one file on every push. Reading the log
# costs nothing and happens when somebody asks.
#
# One job, not all six. The six differ by a factor of two, and a
# largest-of-six would take the Windows number for one test and the
# Linux number for the next: that is two rulers, and a queue ordered
# with two rulers is not ordered. So the slowest of them is asked, and
# only it. Measured on run 33280943877: windows/3.10 208 s,
# macos/3.10 164, ubuntu/3.10 150, windows/3.14 144, macos/3.14 118,
# ubuntu/3.14 101. Whichever is slowest holds every other one up, so
# that is the one worth ordering for.
#
# The numbers replace what stood in the file rather than being folded
# into it. The rule that state/longest may only rise was there to stop
# two machines of different speed pushing each other back and forth,
# and once one machine decides there is nothing left to churn against.
# It also has to be this way round to see any work: a test made three
# times faster keeps its old number for ever under a rule that only
# rises, and then no optimisation can ever be shown. Tests the run did
# not measure keep whatever they had.
#
#   bash builder_times.sh                     the newest green run on main
#   bash builder_times.sh 33280943877         a named run
#   JOB='macos-latest / py3.10' bash ...      a different machine
#
HERE=$(cd "$(dirname "$0")" && pwd)
LONGEST="$HERE/state/longest"
RUN="$1"
JOB="${JOB:-windows-latest / py3.10}"

if ! command -v gh >/dev/null 2>&1; then
  echo "needs the gh command line, and it is not installed" >&2
  exit 2
fi
if [ -z "$RUN" ]; then
  RUN=$(gh run list --branch main --status success --limit 1 \
        --json databaseId --jq '.[0].databaseId' 2>/dev/null)
fi
if [ -z "$RUN" ]; then
  echo "no green run found on main" >&2
  exit 2
fi

log=$(mktemp); trap 'rm -f "$log"' EXIT
if ! gh run view "$RUN" --log > "$log" 2>/dev/null; then
  echo "run $RUN has no log any more -- GitHub keeps them for 90 days" >&2
  exit 2
fi

# The progress line, as run.sh prints it:
#   23:22:26   19/108  settings_window          ok        12 s
# In the CI log the job name, the step and a timestamp stand in front
# of it, tab separated, so the job is cut off the front and the line
# itself looked for anywhere in what is left.
found=$(awk -F'\t' -v job="$JOB" '$1 == job { print }' "$log" \
        | grep -oE '[0-9]{2}:[0-9]{2}:[0-9]{2} +[0-9]+/[0-9]+ +[a-z_]+ +[a-z]+ +[0-9]+ s' \
        | awk '{ print $3, $5 }')
if [ -z "$found" ]; then
  echo "run $RUN has no progress lines for '$JOB'. Either the job is"\
       "named differently there, or it did not get as far as the tests." >&2
  echo "The jobs in this run are:" >&2
  cut -f1 "$log" | sort -u | sed 's/^/  /' >&2
  exit 2
fi

count=$(echo "$found" | wc -l | tr -d ' ')
before=$( [ -f "$LONGEST" ] && awk '{ s += $2 } END { print s+0 }' "$LONGEST" || echo 0)
# The old line first, the builder's after it, and the builder's wins by
# standing later -- so a test that got faster shows it.
# A name with no test file beside it is dropped: a renamed test would
# otherwise sit in the file for ever, holding a place in a queue it is
# no longer in.
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
