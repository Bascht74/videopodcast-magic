#!/bin/bash
# Wait for the builder's answer to the commit that was just pushed.
#
# Nothing tells this machine when a run ends, so the answer used to be
# fetched by asking again and again -- and between two asks the work
# went on against a state the builder had already faulted. Started in
# the background right after a push, this one comes back by itself.
#
# It waits for the run to appear first: a push and the run that follows
# it are seconds apart, and asking for "the newest run" too early
# answers with the one before.
#
#   (bash await_ci.sh &)            the run for HEAD
#   bash await_ci.sh <run id>       a named run
#
HERE=$(cd "$(dirname "$0")" && pwd)
WANT="$1"

if ! command -v gh >/dev/null 2>&1; then
  echo "needs the gh command line, and it is not installed" >&2
  exit 2
fi

if [ -z "$WANT" ]; then
  head=$(git -C "$HERE" rev-parse HEAD)
  # Three minutes: a run appears in seconds, and waiting longer than
  # that means the push did not start one -- which is the answer.
  for _ in $(seq 1 36); do
    WANT=$(gh run list --workflow=tests.yml --limit 10 \
           --json databaseId,headSha \
           --jq "map(select(.headSha == \"$head\")) | .[0].databaseId" \
           2>/dev/null)
    [ -n "$WANT" ] && [ "$WANT" != "null" ] && break
    WANT=""
    sleep 5
  done
  if [ -z "$WANT" ]; then
    echo "no suite run for ${head:0:7} after three minutes --"\
         "was the push rejected, or does the workflow not trigger?"
    exit 2
  fi
fi

echo "waiting on run $WANT"
gh run watch "$WANT" --exit-status >/dev/null 2>&1
verdict=$?

# The name of every job, so a red one is named without a second ask.
gh run view "$WANT" --json jobs,displayTitle \
   --jq '"\(.displayTitle)"' 2>/dev/null
gh run view "$WANT" --json jobs \
   --jq '.jobs[] | "  \(.conclusion)  \(.name)"' 2>/dev/null

if [ "$verdict" = 0 ]; then
  echo "green on all six. The tag may follow -- see the skill freigabe."
else
  echo "RED. What fell, and where:"
  # Only the lines that say something: the suite's own summary and the
  # failing test names. The whole log is megabytes.
  said=$(gh run view "$WANT" --log-failed 2>/dev/null \
         | grep -E "green:|RED \(rc|FAIL:" \
         | sed 's/^[^\t]*\t[^\t]*\t[^ ]* //' | sort -u | head -20)
  if [ -n "$said" ]; then
    echo "$said"
  else
    # A deleted run answers 404 and an aged one answers nothing, and an
    # empty list would read as "red with nothing wrong".
    echo "  the log says nothing -- the run was deleted, or its log has"\
         "aged out. Open it on github.com: $(gh run view "$WANT" \
         --json url --jq .url 2>/dev/null)"
  fi
  echo "-- read the skill test-rot before changing anything."
fi
exit "$verdict"
