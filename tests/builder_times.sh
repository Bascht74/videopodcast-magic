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
#   bash builder_times.sh                     the green run of the version
#                                             HEAD says it is
#   bash builder_times.sh <run id>            a named run
#   JOB='macos-latest / py3.10' bash ...      one named machine
#   bash builder_times.sh --record <version> [<run id>]
#                                             the same, and a section for
#                                             that release appended to
#                                             development/test_durations.md
#   bash builder_times.sh --dry-run ...       writes nothing: prints what
#                                             state/longest would hold
#
HERE=$(cd "$(dirname "$0")" && pwd)
# A German desk writes 171,0 for awk's 171.0, and the next release reads
# that back as 171.
export LC_ALL=C
LONGEST="$HERE/state/longest"
DURATIONS="${VPM_DURATIONS:-$HERE/../development/test_durations.md}"
RECORD=
DRY=
if [ "$1" = "--dry-run" ]; then
  DRY=1
  shift
fi
if [ "$1" = "--record" ]; then
  RECORD="$2"
  shift 2
  if [ -z "$RECORD" ]; then
    echo "--record wants the version: --record 3.0.0b25 [run id]" >&2
    exit 2
  fi
fi
RUN="$1"

if ! command -v gh >/dev/null 2>&1; then
  echo "needs the gh command line, and it is not installed" >&2
  exit 2
fi

# The version a commit says it is, read over the API: the run may stand
# on a branch this checkout never fetched.
version_of() {
  gh api "repos/{owner}/{repo}/contents/videopodcast_magic/__init__.py?ref=$1" \
     --jq .content 2>/dev/null | base64 --decode 2>/dev/null \
    | sed -n 's/^VERSION = "\(.*\)"$/\1/p' | head -1
}

# The run is found by the version its commit carries, on any branch --
# for the record and for the queue alike. The newest green run on main
# is not it while the merge's own run is still going: 3.0.0b24's times
# were read at 21:41 and came from 3.0.0b23's main run, because b24's
# finished at 21:53 (26.9.2026). Without --record the version is the
# one HEAD says it is. A run named for a record is held to it too.
WANT=$RECORD
if [ -z "$WANT" ] && [ -z "$RUN" ]; then
  WANT=$(git -C "$HERE" show HEAD:videopodcast_magic/__init__.py 2>/dev/null \
         | sed -n 's/^VERSION = "\(.*\)"$/\1/p' | head -1)
  if [ -z "$WANT" ]; then
    echo "could not read VERSION from videopodcast_magic/__init__.py at HEAD;"\
         "name a run: bash builder_times.sh <run id>" >&2
    exit 2
  fi
fi
if [ -n "$WANT" ] && [ -z "$RUN" ]; then
  for pair in $(gh run list --workflow tests --status success --limit 20 \
                  --json databaseId,headSha \
                  --jq '.[] | "\(.databaseId):\(.headSha)"' 2>/dev/null); do
    if [ "$(version_of "${pair#*:}")" = "$WANT" ]; then
      RUN=${pair%%:*}
      break
    fi
  done
  if [ -z "$RUN" ]; then
    echo "no green run among the last 20 stands on a commit that says"\
         "VERSION = \"$WANT\" -- has its run finished? Or name one:"\
         "bash builder_times.sh ${RECORD:+--record $RECORD }<run id>" >&2
    exit 2
  fi
  echo "green run of $WANT: $RUN"
elif [ -n "$RECORD" ]; then
  sha=$(gh run view "$RUN" --json headSha --jq .headSha 2>/dev/null)
  said=$(version_of "$sha")
  if [ "$said" != "$RECORD" ]; then
    echo "run $RUN stands on ${sha:0:7}, which says VERSION = \"$said\","\
         "not \"$RECORD\" -- that is another release's run" >&2
    exit 2
  fi
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
# test file here or in a folder under it is dropped: a renamed test would
# otherwise hold a place in a queue it is no longer in.
suite=$(cd "$HERE" && ls *_test.py */*_test.py 2> /dev/null \
        | grep -v '^resolve/live/' | sed 's|.*/||; s/_test\.py$//' | tr '\n' ' ')
{ [ -f "$LONGEST" ] && cat "$LONGEST" || true
  echo "$found"
} | awk -v suite=" $suite" '
    { seen[$1] = $2 }
    END { for (n in seen)
            if (index(suite, " " n " "))
              printf "%s %d\n", n, seen[n] }' \
  | sort > "$LONGEST.new" || exit 2
if [ -n "$DRY" ]; then
  echo "--dry-run: state/longest left as it is; it would hold:"
  sed 's/^/  /' "$LONGEST.new"
  SHOWN="$LONGEST.new"; trap 'rm -f "$log" "$LONGEST.new"' EXIT
else
  mv "$LONGEST.new" "$LONGEST"; SHOWN="$LONGEST"
fi
after=$(awk '{ s += $2 } END { print s+0 }' "$SHOWN")

echo "run $RUN, job '$JOB': $count tests measured"
holds=holds; now=now; [ -n "$DRY" ] && { holds="would hold"; now=after; }
echo "state/longest $holds $(wc -l < "$SHOWN" | tr -d ' ') tests,"\
     "$before s before, $after s $now"
echo
echo "the ten that go first from here on:"
sort -k2 -rn "$SHOWN" | head -10 | awk '{ printf "  %-24s %3d s\n", $1, $2 }'

[ -n "$RECORD" ] || exit 0

# The record: every job this time, not only the slowest. The queue wants
# one ruler; a record of what a change cost wants a figure no single
# machine's mood decides. How it is reckoned and why stands in the head
# of development/test_durations.md, and only there.
if [ ! -f "$DURATIONS" ]; then
  echo "$DURATIONS is not there; it carries the head the sections go under" >&2
  exit 2
fi
if grep -q "^## $RECORD -- " "$DURATIONS"; then
  echo "$DURATIONS already has a section for $RECORD; nothing appended" >&2
  exit 2
fi
jobs=$(gh run view "$RUN" --json jobs --jq '.jobs[]
  | "\(.name)\t\((.completedAt | fromdate) - (.startedAt | fromdate))"' 2>/dev/null)
meta=$(gh run view "$RUN" --json headBranch,headSha,createdAt,displayTitle \
       --jq '"\(.headBranch)\t\(.headSha[0:7])\t\(.createdAt[0:10])\t\(.displayTitle)"' 2>/dev/null)
# Every progress line of every job, as "job <tab> test <tab> seconds",
# read with the same pattern as the slowest job's above.
times=$(printf '%s\n' "$jobs" | cut -f1 | while IFS= read -r j; do
          awk -F'\t' -v job="$j" '$1 == job { print }' "$log" \
          | grep -oE '[0-9]{2}:[0-9]{2}:[0-9]{2} +[0-9]+/[0-9]+ +[a-z0-9_]+ +[a-z]+ +[0-9]+ s' \
          | awk -v job="$j" '{ print job "\t" $3 "\t" $5 }'
        done)
# The previous release is the last section's every-test block: first
# word the test, last word its trimmed mean.
previous=$(awk '/^## / { n = 0 }
  /^```text$/ { inside = 1; next }  /^```$/ { inside = 0; next }
  inside && $1 != "test" { last[++n] = $1 "\t" $NF }
  END { for (i = 1; i <= n; i++) print last[i] }' "$DURATIONS")

{ printf '%s\n' "$jobs" | sed 's/^/J	/'
  printf '%s\n' "$times" | sed 's/^/T	/'
  [ -n "$previous" ] && printf '%s\n' "$previous" | sed 's/^/P	/'
} | awk -F'\t' -v version="$RECORD" -v run="$RUN" -v meta="$meta" '
  # Six values: the highest and the lowest go, the four between are
  # averaged. Fewer -- a test set aside on a platform -- the median.
  function trimmed(t,    n, i, j, v, s, x) {
    n = 0
    for (i = 1; i <= nj; i++) if ((t, job[i]) in secs) v[++n] = secs[t, job[i]]
    for (i = 2; i <= n; i++) {
      x = v[i]; for (j = i - 1; j >= 1 && v[j] > x; j--) v[j + 1] = v[j]
      v[j + 1] = x
    }
    if (n >= 6) { s = 0; for (i = 2; i < n; i++) s += v[i]; return s / (n - 2) }
    how[t] = " (median of " n ")"
    return (n % 2) ? v[(n + 1) / 2] : (v[n / 2] + v[n / 2 + 1]) / 2
  }
  function cell(t, i) { return ((t, job[i]) in secs) ? secs[t, job[i]] : "-" }
  $1 == "J" { job[++nj] = $2; wall[$2] = $3 }
  $1 == "T" { secs[$3, $2] = $4; sum[$2] += $4
              if (!($3 in known)) { known[$3] = 1; test[++nt] = $3 } }
  $1 == "P" { prev[$2] = $3; had_prev = 1 }
  END {
    for (i = 2; i <= nj; i++) {
      x = job[i]; for (j = i - 1; j >= 1 && tolower(job[j]) > tolower(x); j--) job[j + 1] = job[j]
      job[j + 1] = x
    }
    for (i = 1; i <= nt; i++) { t = test[i]; mean[t] = trimmed(t); total += mean[t]
      # "in" before prev[t]: in awk, naming an element makes it
      if (!had_prev) { change[t] = "--"; continue }
      if (!(t in prev)) { change[t] = "new"; continue }
      d = mean[t] - prev[t]
      change[t] = sprintf("%+.1f", d)
      # grown: more than a fifth, and at least ten seconds
      if (d >= 10 && (prev[t] == 0 || d / prev[t] > 0.2)) {
        change[t] = change[t] " **grown**"
        grown = grown sprintf("%s`%s` %.1f -> %.1f s", (grown == "" ? "" : ", "),
                              t, prev[t], mean[t])
      }
    }
    for (i = 1; i <= nt; i++) order[i] = test[i]
    for (i = 2; i <= nt; i++) {
      x = order[i]
      for (j = i - 1; j >= 1 && (mean[order[j]] < mean[x] || \
           (mean[order[j]] == mean[x] && order[j] > x)); j--) order[j + 1] = order[j]
      order[j + 1] = x
    }
    slow = job[1]; for (i = 2; i <= nj; i++) if (wall[job[i]] > wall[slow]) slow = job[i]
    split(meta, m, "\t")
    printf "\n## %s -- %s\n\n", version, m[3]
    printf "Run %s on `%s` at `%s`: %s.\n\n", run, m[1], m[2], m[4]
    printf "The slowest job, and what a push waits for: **%s, %d s**.\n", slow, wall[slow]
    printf "The suite summed over the trimmed means: **%d s** for %d tests.\n\n", total + 0.5, nt
    printf "| job | wall s | tests summed s |\n|---|---:|---:|\n"
    for (i = 1; i <= nj; i++) printf "| %s | %d | %d |\n", job[i], wall[job[i]], sum[job[i]]
    printf "\nThe 15 longest by trimmed mean:\n\n| test |"
    for (i = 1; i <= nj; i++) printf " %s |", job[i]
    printf " trimmed | change |\n|---|"
    for (i = 1; i <= nj; i++) printf "---:|"
    printf "---:|---|\n"
    for (k = 1; k <= nt && k <= 15; k++) {
      t = order[k]; printf "| `%s` |", t
      for (i = 1; i <= nj; i++) printf " %s |", cell(t, i)
      printf " %.1f%s | %s |\n", mean[t], how[t], change[t]
    }
    if (!had_prev) printf "\nGrown: no earlier section to compare with.\n"
    else printf "\nGrown by more than 20 %% and at least 10 s: %s.\n", (grown == "" ? "none" : grown)
    printf "\n<details>\n<summary>Every test, %d</summary>\n\n```text\ntest", nt
    for (i = 1; i <= nj; i++) { x = job[i]; gsub(/ /, "_", x); printf " %s", x }
    printf " trimmed\n"
    for (k = 1; k <= nt; k++) {
      t = order[k]; printf "%s", t
      for (i = 1; i <= nj; i++) printf " %s", cell(t, i)
      printf " %.1f\n", mean[t]
    }
    printf "```\n\n</details>\n"
  }' > "$DURATIONS.new" || exit 2
if [ -n "$DRY" ]; then
  echo; echo "--dry-run: the section for $RECORD, not appended:"
  cat "$DURATIONS.new"; rm -f "$DURATIONS.new"
  exit 0
fi
cat "$DURATIONS.new" >> "$DURATIONS" && rm -f "$DURATIONS.new"
echo
echo "appended $RECORD to $DURATIONS:"
tail -n +2 "$DURATIONS" | grep -E '^(The slowest|The suite summed|Grown)' \
  | tail -3 | sed 's/^/  /'
