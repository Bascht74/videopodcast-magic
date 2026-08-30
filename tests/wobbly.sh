#!/bin/bash
# Which tests wobble, counted over runs, written into state/wobbly.
#
# A test that is red beside the others and green alone is a defect
# asleep, and run.sh says so in its own line. But that line lives in the
# run's log, and a log is gone when the run is -- deleted by hand, or
# aged out after 90 days. An investigation that has to start by asking
# what happened last week then has nothing to read.
#
# So the lines are taken out and kept. What is already in the file is
# not fetched again: a run is read once, and after that its numbers
# stand whether or not the run does. That is the whole point of the
# file, and the reason it accumulates rather than being replaced -- the
# opposite of state/longest, which measures what is true now.
#
# Two shapes are counted apart, because they are two faults. "beside"
# is a test that lost against its neighbours and won alone: contention.
# "crashed" is a test that died and came back: a return code above 128
# is a signal, and the number says which.
#
#   bash wobbly.sh              read the runs not yet read, then report
#   bash wobbly.sh 40           look that far back (default 20)
#   bash wobbly.sh report       report on what is in the file, ask nothing
#
HERE=$(cd "$(dirname "$0")" && pwd)
FILE="$HERE/state/wobbly"
BACK=${1:-20}

report() {
  if [ ! -s "$FILE" ]; then
    echo "nothing counted yet"
    return
  fi
  runs=$(cut -f1 "$FILE" | sort -u | grep -cv '^#')
  echo
  echo "$(grep -cv '^#' "$FILE") wobbles over $runs runs, from $(
    grep -v '^#' "$FILE" | cut -f2 | sort | head -1) to $(
    grep -v '^#' "$FILE" | cut -f2 | sort | tail -1)"
  echo
  echo "  by test:"
  grep -v '^#' "$FILE" | awk -F'\t' '{ print $4, $5 }' | sort | uniq -c \
    | sort -rn | awk '{ printf "  %6s  %-26s %s\n", $1, $2, $3 }'
  echo
  echo "  by machine:"
  grep -v '^#' "$FILE" | cut -f3 | sort | uniq -c | sort -rn \
    | awk '{ c = $1; $1 = ""; sub(/^ +/, ""); printf "  %6s  %s\n", c, $0 }'
  echo
  # A test that wobbles on one machine only is a different animal from
  # one that wobbles everywhere, and the pair is what says which.
  echo "  test on machine, where it happened more than once:"
  grep -v '^#' "$FILE" | awk -F'\t' '{ print $4 "\t" $3 }' | sort | uniq -c \
    | awk '$1 > 1' | sort -rn \
    | awk -F'\t' '{ printf "  %-34s %s\n", $1, $2 }'
  echo
}

if [ "$1" = "report" ]; then
  report
  exit 0
fi

if ! command -v gh >/dev/null 2>&1; then
  echo "needs the gh command line, and it is not installed" >&2
  exit 2
fi

mkdir -p "$HERE/state"
[ -f "$FILE" ] || printf '# run\tfinished\tjob\ttest\thow\n' > "$FILE"

runs=$(gh run list --workflow=tests.yml --limit "$BACK" \
       --json databaseId,conclusion,updatedAt \
       --jq '.[] | select(.conclusion == "success" or .conclusion == "failure")
             | "\(.databaseId)\t\(.updatedAt)"' 2>/dev/null)
if [ -z "$runs" ]; then
  echo "no finished runs of the suite found" >&2
  exit 2
fi

log=$(mktemp); trap 'rm -f "$log"' EXIT
fresh=0; already=0; gone=0

while IFS=$'\t' read -r id when; do
  [ -n "$id" ] || continue
  if grep -q "^$id	" "$FILE" 2>/dev/null; then
    already=$((already + 1)); continue
  fi
  if ! gh run view "$id" --log > "$log" 2>/dev/null; then
    # Counted as read all the same, with no wobbles: without this the
    # script would ask after the same vanished run for ever.
    printf '# %s\t%s\tlog gone\n' "$id" "${when%%T*}" >> "$FILE"
    gone=$((gone + 1)); continue
  fi
  # Which tests wobbled comes from the run's closing summary, which
  # names them: "unsteady: 1 -- interface". How each one fell comes
  # from its own progress line, which carries the name and the code
  # together: "15/120  interface  RED (rc=1)  48 s  221 p". Reading the
  # code off any other line in the job would hang one test's death on
  # another test's name.
  awk -F'\t' -v id="$id" -v day="${when%%T*}" '
    $1 ~ /\// {
      job = $1
      line = $0
      if (match(line, /unsteady: [0-9]+ --[^(]*/)) {
        s = substr(line, RSTART, RLENGTH)
        sub(/unsteady: [0-9]+ -- */, "", s)
        n = split(s, names, /[ \t]+/)
        for (i = 1; i <= n; i++)
          if (names[i] != "") seen[job "\t" names[i]] = 1
      }
      # A signal is anything over 128, and the number says which one.
      # Below that it is an ordinary failure, and calling that a crash
      # is what sent an earlier reading of this file down a false path.
      if (match(line, /[0-9]+\/[0-9]+ +[a-z0-9_]+ +RED \(rc=[0-9]+\)/)) {
        hit = substr(line, RSTART, RLENGTH)
        split(hit, w, /[ \t]+/)
        rc = hit; sub(/.*rc=/, "", rc); sub(/\).*/, "", rc)
        fell[job "\t" w[2]] = (rc + 0 > 128 ? "crashed rc=" rc : "beside rc=" rc)
      }
    }
    END {
      for (k in seen) {
        split(k, part, "\t")
        printf "%s\t%s\t%s\t%s\t%s\n", id, day, part[1], part[2],
               (k in fell ? fell[k] : "unknown")
      }
    }' "$log" >> "$FILE"
  fresh=$((fresh + 1))
done <<< "$runs"

echo "runs read now: $fresh   already in the file: $already   log gone: $gone"
report
