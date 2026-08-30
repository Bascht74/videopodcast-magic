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
# One run is a thin basis for that, and over eight green runs of
# 30.8.2026 the picture is closer: windows/3.14 137 s on average,
# windows/3.10 129, macos/3.14 122, macos/3.10 121, ubuntu/3.14 95,
# ubuntu/3.10 84 -- measured from the first progress line to the last,
# so fixture building is left out of it. The two Windows jobs have
# drawn level and swapped places, and which of them is slowest on a
# given day is inside the noise. It is left at 3.10: they are the same
# machine and the same order comes out either way, and changing it
# would rewrite every number in the file to buy nothing. If Windows
# ever stops being the slow pair, that is the thing to act on.
#
# The times of a single run, not a median over several. That was
# measured, on 30.8.2026, over eight green runs.
#
# What a run reports is noisy. A test's slowest reading was about its
# own median away from its fastest: crosstalk came in at 31, 12, 12, 6,
# 3, 2, 3 and 1 s. That looks like it ought to matter, and it does not.
# Take one run's numbers, order the queue by them, and hand the next
# run's real times to five workers in that order: the run comes out
# 0.1 s longer than if its own times had been known in advance. A
# median over seven other runs comes out 0.4 s longer -- no better, a
# hair worse. Alphabetical order, which is what there was before any of
# this, costs 19 s of about 140; shortest-first costs 68.
#
# So the order is worth having and the numbers are not worth making
# more accurate. What an order needs to know is which handful of tests
# are the big ones, and that never wavers: local_run was the longest
# test in all eight runs, german_hunt the second longest in all eight.
#
# The same 0.1 s disposes of the other idea, which is to time the tests
# one at a time with WORKERS=1 and order by what each costs alone. It
# cannot win more than that 0.1 s, because 0.1 s is the whole gap to
# knowing the run's own times in advance, and nothing predicts a run
# better than the run itself. It would cost an extra job on the builder
# to bid for it.
#
# The times read here are inflated -- five tests run at once, so each
# is carrying the others -- but by much the same factor throughout, and
# a factor that is the same everywhere moves nothing up or down the
# queue. Reading each test's start back out of the log, as its end less
# its seconds: while any test ran, 4.97 tests were running at once on
# average, counting itself, out of five workers, and never fewer than
# 4.2. The queue is full from end to end, so no test is inflated by
# luckier neighbours than any other. That is also why the seconds in
# one job add up to four or five times the job's own length: five
# workers being busy, not a fault in the numbers.
#
# Counting process starts instead of seconds was measured too, on the
# three runs that carry that column: it orders worse than seconds do
# (+7.7 s) and barely better than the alphabet. The two correlate at
# r = 0.49, so it is a different question, not a cheaper answer to
# this one.
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
#   23:22:26   19/108  settings_window          ok        12 s   47 p
# In the CI log the job name, the step and a timestamp stand in front
# of it, tab separated, so the job is cut off the front and the line
# itself looked for anywhere in what is left.
#
# A digit is part of a test's name. It was not, and the one test that
# has one -- assignment5c -- was dropped from every reading in silence.
# Checked over eight green runs on 30.8.2026: the pattern came up
# exactly one line short in every one of the eight, and the missing
# line was that test every time. So it kept whatever number happened to
# stand against its name for ever, because the line that would have
# replaced it never matched, and nothing said so.
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
# alone rather than by the pattern above. The two have to agree, and
# for months they did not: a pattern that quietly understands less than
# it was given looks exactly like a run that measured less, and neither
# says anything. Not an error -- a test whose line was not read keeps
# the number it had -- so this warns and carries on.
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
