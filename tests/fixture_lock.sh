# The lock on the shared fixture folders, for every script that builds
# them and then reads them. Sourced, not run: run.sh and resolve.sh both
# take it, so a Resolve run and a suite on the same root wait for each
# other instead of one deleting what the other reads.
#
#   . "$HERE/fixture_lock.sh"     with HERE and VPM_FIXTURES set
#   fixtures_hold                 wait until this run may build
#   bash "$HERE/fixtures.sh"
#   fixtures_share                build done, read beside the others
#   fixtures_let_go               on the way out, from the EXIT trap
#
# Two suites on one machine share VPM_FIXTURES, and fixtures.sh deletes a
# folder before building it again. Measured 24.9.2026: two runs on an
# empty root, one stopped on "rm: whole.mp4: No such file or directory";
# another recipe word rebuilt under a running suite, three of four red.
FIX_LOCK="$VPM_FIXTURES.lock"
FIX_RUNS="$VPM_FIXTURES.runs"
# Runs with the same fixtures.sh build the same folders and may read side
# by side; a run with another one waits until they are gone. Not quite
# read-only: each start writes the interview project file again, and
# fixtures.sh says why -- in one step, so a reader never sees half of it.
RECIPE=$(cksum < "$HERE/fixtures.sh" | cut -d' ' -f1)
# Waiting lasts while the other run lives. The bound only ends a wait on
# a run that hangs; a whole run takes minutes. VPM_FIXTURE_WAIT=0 stops
# at once instead of waiting.
FIX_WAIT=${VPM_FIXTURE_WAIT:-3600}
fixtures_let_go() {
  rm -f "$FIX_RUNS/$$"
  holder=$(cat "$FIX_LOCK/holder" 2> /dev/null)
  [ "${holder%% *}" = "$$" ] && rm -rf "$FIX_LOCK"
}
fixtures_wait() {
  if [ "$1" != "$fix_said" ]; then
    echo "fixtures: $VPM_FIXTURES -- waiting: $1"
    fix_said="$1"
  fi
  if [ $((SECONDS - fix_began)) -ge "$FIX_WAIT" ]; then
    echo "fixtures: stopping after $FIX_WAIT s of waiting -- $1" >&2
    exit 2
  fi
  sleep 1
}
# What stands in the way: every live run reading with another recipe.
# A run that died without its trap is only a file, and goes here.
fixtures_other_readers() {
  for f in "$FIX_RUNS"/*; do
    [ -f "$f" ] && [ "${f##*/}" != "$$" ] || continue
    if ! kill -0 "${f##*/}" 2> /dev/null; then rm -f "$f"; continue; fi
    read -r recipe day clock at < "$f"
    [ "$recipe" = "$RECIPE" ] && continue
    echo "run ${f##*/} from $at reads it with another fixtures.sh since $day $clock"
  done
}
fixtures_hold() {
  fix_said=""
  fix_began=$SECONDS
  fix_empty=0
  # A suite that starts run.sh inside itself, as source_resolve_recalled
  # does, would wait on the suite it runs in. Its outer run holds the root
  # for it, so it goes in the way every run went before the lock.
  read -r held_pid held_root <<< "$VPM_FIXTURES_HELD"
  if [ "$held_root" = "$VPM_FIXTURES" ] && kill -0 "$held_pid" 2> /dev/null
  then
    fix_inside=1
  else
    fix_inside=""
  fi
  mkdir -p "$FIX_RUNS"
  until [ -n "$fix_inside" ] || mkdir "$FIX_LOCK" 2> /dev/null; do
    # Refused, and nothing there: not a lock but a place nobody may write.
    if [ ! -d "$FIX_LOCK" ]; then
      mkdir "$FIX_LOCK" 2> /dev/null && break
      [ -d "$FIX_LOCK" ] || { echo "fixtures: cannot make $FIX_LOCK" >&2; exit 2; }
    fi
    holder=$(cat "$FIX_LOCK/holder" 2> /dev/null)
    # A holder that is gone never let go, and neither did a run killed
    # between making the lock and naming itself in it: the name comes a
    # moment after, so ten seconds without one is a lock nobody holds.
    # Moved aside; two waiters doing that in the same instant can both
    # get through, a window left open.
    [ -z "$holder" ] && fix_empty=$((fix_empty + 1)) || fix_empty=0
    if { [ -n "$holder" ] && ! kill -0 "${holder%% *}" 2> /dev/null; } \
       || [ "$fix_empty" -gt 10 ]; then
      left="named no run for 10 s"
      [ -n "$holder" ] && left="was left by run ${holder%% *}, which is gone"
      mv "$FIX_LOCK" "$FIX_LOCK.gone.$$" 2> /dev/null \
        && rm -rf "$FIX_LOCK.gone.$$" \
        && echo "fixtures: $FIX_LOCK $left -- taken over"
      fix_empty=0
      continue
    fi
    if [ -z "$holder" ]; then
      fixtures_wait "another run is taking $FIX_LOCK"
      continue
    fi
    read -r pid day clock at <<< "$holder"
    fixtures_wait "run $pid from $at holds $FIX_LOCK since $day $clock"
  done
  [ -n "$fix_inside" ] \
    || echo "$$ $(date '+%Y-%m-%d %H:%M:%S') $HERE" > "$FIX_LOCK/holder"
  while [ -z "$fix_inside" ] && other=$(fixtures_other_readers | head -1) \
        && [ -n "$other" ]; do
    fixtures_wait "$other"
  done
}
# Built: from here on this run only reads, beside every run with the same
# recipe, and a run it starts inside itself goes straight in.
fixtures_share() {
  if [ -z "$fix_inside" ]; then
    echo "$RECIPE $(date '+%Y-%m-%d %H:%M:%S') $HERE" > "$FIX_RUNS/$$"
    rm -rf "$FIX_LOCK"
    export VPM_FIXTURES_HELD="$$ $VPM_FIXTURES"
  fi
}
