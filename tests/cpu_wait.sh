# The wait for processor before a test starts, and before a measurement
# that does not go through run.sh. Several suites, strands and
# measurements share this machine, and a test started beside them all
# measures the crowd: a second of sound beside eleven others took
# sixteen. So nothing starts until the machine has processor to spare.
#
#   . "$HERE/cpu_wait.sh"         sourced by run.sh, with PY set
#   cpu_wait <test>               at the top of run_one, before `began`
#   cpu_wait_carry                the lines a worker needs, for $FUNCS
#   cpu_wait_said                 the summary's line
#   cpu_wait_let_go               on the way out, from the EXIT trap
#
#   bash tests/cpu_wait.sh <command ...>   a measurement of its own
#   bash tests/cpu_wait.sh && <command>    the same, unseen while it runs
#
# The rule: while another suite or measurement that waits too is
# running, a test starts only on a look that finds the machine under
# VPM_CPU_BUSY_MOST percent busy (default 90) over the last half second,
# each test started in it counted as a busy processor for the part it
# missed; after VPM_CPU_WAIT_MOST seconds (default 600) it starts
# anyway, and the summary says so. One waiter at a time looks, across
# every run of this user: the others queue on a lock. A run alone does
# not look -- its own tests keep this machine above 90 % for two thirds
# of its seconds, and held to that it took 8 to 12 % longer.
#
# Off where nothing runs beside it -- CI or GITHUB_ACTIONS set, as
# GitHub sets them -- with VPM_CPU_BUSY_MOST=0, inside a suite a test
# started (its outer run waited already, and the test's own 300 s would
# pay for a second wait), and where no probe works; the summary's line
# says which. For the gate's own test, which must not hold the real
# lock: VPM_CPU_LOCK names another, VPM_CPU_PROBE a bash script standing
# in for the look, VPM_CPU_TICKS a file standing in for the counters.

# On the way out: this run's file out of the folder of runs, the way
# fixtures_let_go takes its own; a worker has none. First in the file,
# so an exit anywhere below finds it.
CPU_RUNS=""
cpu_wait_let_go() {
  [ -z "$CPU_RUNS" ] || rm -f "$CPU_RUNS/$CPU_SELF"
}
CPU_BUSY_MOST=${VPM_CPU_BUSY_MOST:-90}
CPU_WAIT_MOST=${VPM_CPU_WAIT_MOST:-600}
for cw_value in "$CPU_BUSY_MOST" "$CPU_WAIT_MOST"; do
  case "$cw_value" in
    ""|*[!0-9]*)
      echo "VPM_CPU_BUSY_MOST and VPM_CPU_WAIT_MOST take whole numbers," \
           "percent and seconds; 0 percent turns the wait off" >&2
      exit 2 ;;
  esac
done
CPU_PROBE=${VPM_CPU_PROBE:-}
CPU_PY=${PY:-${VPM_PYTHON:-python3}}
# Seconds, measured 17.10.2026 (development/test_guidelines.md, section
# 6). WINDOW is a look's own window where no earlier look left its
# counters behind; PAUSE how long a holder that saw a busy machine
# sleeps before it looks again; POLL how often one in the queue asks
# after the lock for its first ten asks behind one holder -- a look's
# length. After that it asks every half second to second, drawn afresh
# each time: each ask starts a process, the sleep, and a queue is
# longest on a busy machine, where thirty waiters behind a holder that
# looked for 20 s took 0.9 of a processor asking every quarter second
# and 0.35 so -- counted in the share they wait on. Drawn, because a
# queue that started together asks together, and the first ask after a
# long turn then came a whole second late.
CPU_WINDOW=0.25
CPU_PAUSE=0.2
CPU_POLL=0.05
# Where run.sh keeps one line per test that waited; empty, nothing kept.
CPU_WAITS=""
# The look, in whole percent busy: every processor's ticks now against
# those a look half a second ago left behind, so it costs a Python start
# and no sleep, and a burst of a tenth of a second does not read as a
# full machine. A test started in that half second is not yet in it
# whole, so it is added as a processor for the part it missed. With a
# limit given, a look under it is written down as a start. macOS answers
# per processor, host_processor_info -- the machine's total,
# host_statistics, comes back unchanged when asked often -- and Linux
# in the first line of /proc/stat; elsewhere there is no probe.
CPU_TICKS='import os, sys, time
SPAN, OLD = 0.5, 3.0
def ticks():
    fake = os.environ.get("VPM_CPU_TICKS")
    if fake:
        with open(fake) as f:
            return [int(x) for x in f.read().split()], 4, (2,)
    if sys.platform == "darwin":
        import ctypes
        c = ctypes.CDLL(None)
        c.mach_host_self.restype = ctypes.c_uint
        cpus, size = ctypes.c_uint(), ctypes.c_uint()
        info = ctypes.POINTER(ctypes.c_uint)()
        if c.host_processor_info(c.mach_host_self(), 2, ctypes.byref(cpus),
                                 ctypes.byref(info), ctypes.byref(size)):
            sys.exit(1)
        return list(info[:size.value]), 4, (2,)
    if sys.platform.startswith("linux"):
        with open("/proc/stat") as f:
            return [int(x) for x in f.readline().split()[1:9]], 8, (3, 4)
    sys.exit(1)
window = float(sys.argv[1])
kept = sys.argv[2] if len(sys.argv) > 2 else ""
most = int(sys.argv[3]) if len(sys.argv) > 3 else 0
now, step, idle = ticks()
at = time.time()
samples, starts = [], []
try:
    with open(kept) as f:
        for line in f:
            w = line.split()
            if w[:1] == ["s"] and len(w) == len(now) + 2:
                samples.append((float(w[1]), [int(x) for x in w[2:]]))
            elif w[:1] == ["g"] and len(w) == 2:
                starts.append(float(w[1]))
except (OSError, ValueError):
    samples, starts = [], []
samples = sorted(s for s in samples if 0.02 <= at - s[0] <= OLD)
older = [s for s in samples if at - s[0] >= SPAN]
base = older[-1] if older else samples[0] if samples else None
if base is None:
    base = (at, now)
    time.sleep(window)
    now, step, idle = ticks()
    at = time.time()
d = [(y - x) & 0xffffffff for x, y in zip(base[1], now)]
free = sum(v for i, v in enumerate(d) if i % step in idle)
busy = 100.0 * (sum(d) - free) / sum(d) if sum(d) else 0.0
cpus = len(now) // step if step == 4 else os.cpu_count() or 1
missing = sum(1 - (at - g) / (at - base[0]) for g in starts
              if base[0] < g <= at)
guess = busy + 100.0 * missing / cpus
if most and guess < most:
    starts.append(at)
if kept:
    rows = []
    for t, v in samples + [(at, now)]:
        if not rows or t - rows[-1][0] >= 0.1 or t == at:
            rows.append((t, v))
    with open(kept + ".new", "w") as f:
        for t, v in rows:
            f.write("s %r %s\n" % (t, " ".join(map(str, v))))
        for g in starts:
            if at - g <= OLD:
                f.write("g %r\n" % g)
    os.replace(kept + ".new", kept)
print(int(guess))'

cpu_look() {
  if [ -n "$CPU_PROBE" ]; then
    "$BASH" "$CPU_PROBE" "$@"
  else
    "$CPU_PY" -I -S -c "$CPU_TICKS" "$@"
  fi 2> /dev/null
}

# Why the wait is off for this run, or nothing. Asked once, here; a
# look of window 0 only asks whether the probe answers.
CPU_OFF=""
if [ -n "${CI:-}" ] || [ -n "${GITHUB_ACTIONS:-}" ]; then
  CPU_OFF="CI is set, and on the builder nothing runs beside the suite"
elif [ "$CPU_BUSY_MOST" -eq 0 ]; then
  CPU_OFF="VPM_CPU_BUSY_MOST=0"
else
  cw_outer=${VPM_FIXTURES_HELD%% *}
  if [ -n "$cw_outer" ] && kill -0 "$cw_outer" 2> /dev/null; then
    CPU_OFF="inside the suite of run $cw_outer, which waited for it"
  else
    case "$(cpu_look 0)" in
      ""|*[!0-9]*) CPU_OFF="no probe reads the processors on this system" ;;
    esac
  fi
fi
# The lock, per user, and beside it one empty file per run or
# measurement that waits, named by its process: this one, for the others
# to see while it lives, and taken away by cpu_wait_let_go on its way
# out -- left behind, its number given to another process that lives,
# it would hold every run alone to the wait. A file whose process went
# without letting go is cleared by whoever finds it. Not made where the
# wait is off, nor its id asked.
CPU_SELF=$$
CPU_LOCK=""
if [ -z "$CPU_OFF" ]; then
  CPU_LOCK=${VPM_CPU_LOCK:-/tmp/vpm-cpu-$(id -u).lock}
  CPU_RUNS="$CPU_LOCK.runs"
  mkdir -p "$CPU_RUNS" 2> /dev/null && : > "$CPU_RUNS/$CPU_SELF"
fi

# Waits until a look finds the machine under the limit, or the bound has
# passed -- and only while another run that waits is alive. The lock is
# a folder; the line in it names the holder's process and how often it
# has looked, so a waiter in the queue knows a holder that is gone from
# one that is waiting on a busy machine.
cpu_wait() {
  [ -z "$CPU_OFF" ] || return 0
  cw_other=""
  for cw_run in "$CPU_RUNS"/*; do
    [ -f "$cw_run" ] && [ "${cw_run##*/}" != "$CPU_SELF" ] || continue
    if kill -0 "${cw_run##*/}" 2> /dev/null; then
      cw_other=1
      break
    fi
    rm -f "$cw_run"
  done
  [ -n "$cw_other" ] || return 0
  cw_began=$SECONDS
  cw_busy=0
  cw_bound=""
  cw_seen=""
  cw_since=$SECONDS
  cw_me="$$ $RANDOM$RANDOM"
  cw_turn=""
  cw_asks=0
  while :; do
    # Free: taken now. Refused, and nothing there: not a lock but a place
    # nobody may write -- started, rather than held back by that. Asked
    # only while there is no lock, so an ask behind a holder starts no
    # mkdir.
    if [ ! -d "$CPU_LOCK" ]; then
      mkdir "$CPU_LOCK" 2> /dev/null && break
      [ -d "$CPU_LOCK" ] || return 0
    fi
    cw_holder=""
    { read -r cw_holder < "$CPU_LOCK/holder"; } 2> /dev/null
    if [ "$cw_holder" != "$cw_seen" ]; then
      cw_seen=$cw_holder
      cw_since=$SECONDS
    fi
    # Its third word is how often it has looked: more than once, and it
    # is waiting on a busy machine -- so is everybody behind it.
    case "$cw_holder" in
      *" "*" "[2-9]|*" "*" "[1-9][0-9]*) cw_busy=1 ;;
    esac
    # The first two words are the holder's turn; behind one turn, quick
    # for ten asks and then slow.
    if [ "${cw_holder% *}" != "$cw_turn" ]; then
      cw_turn=${cw_holder% *}
      cw_asks=0
    fi
    cw_asks=$((cw_asks + 1))
    cw_poll=$CPU_POLL
    [ "$cw_asks" -le 10 ] \
      || printf -v cw_poll '0.%02d' $((50 + RANDOM % 50))
    # A holder that is gone never let go, nor did one killed between
    # making the folder and naming itself in it; and one whose line has
    # not changed for 10 s has stopped looking. Moved aside; two waiters
    # doing that in the same instant can both get through, a window left
    # open as in fixture_lock.sh.
    if { [ -n "$cw_holder" ] && ! kill -0 "${cw_holder%% *}" 2> /dev/null; } \
       || [ $((SECONDS - cw_since)) -ge 10 ]; then
      mv "$CPU_LOCK" "$CPU_LOCK.gone.$$" 2> /dev/null \
        && rm -rf "$CPU_LOCK.gone.$$"
      cw_since=$SECONDS
      continue
    fi
    if [ $((SECONDS - cw_began)) -ge "$CPU_WAIT_MOST" ]; then
      cw_bound=1
      break
    fi
    sleep "$cw_poll"
  done
  if [ -z "$cw_bound" ]; then
    cw_looks=0
    while :; do
      cw_looks=$((cw_looks + 1))
      echo "$cw_me $cw_looks" 2> /dev/null > "$CPU_LOCK/holder"
      cw_now=$(cpu_look "$CPU_WINDOW" "$CPU_LOCK.ticks" "$CPU_BUSY_MOST")
      # A look that fails holds nobody back.
      case "$cw_now" in ""|*[!0-9]*) break ;; esac
      [ "$cw_now" -lt "$CPU_BUSY_MOST" ] && break
      cw_busy=$((cw_busy + 1))
      if [ $((SECONDS - cw_began)) -ge "$CPU_WAIT_MOST" ]; then
        cw_bound=1
        break
      fi
      sleep "$CPU_PAUSE"
    done
    # Let go, unless another took the lock over while this one slept.
    cw_holder=""
    { read -r cw_holder < "$CPU_LOCK/holder"; } 2> /dev/null
    [ "$cw_holder" = "$cw_me $cw_looks" ] && rm -rf "$CPU_LOCK"
  fi
  # Kept only for a start that was held back: by a busy look of its own,
  # or behind one, or by the bound. The seconds are whole ones.
  if [ -n "$CPU_WAITS" ] && { [ "$cw_busy" -gt 0 ] || [ -n "$cw_bound" ]; }
  then
    echo "$((SECONDS - cw_began)) ${cw_bound:+bound}" >> "$CPU_WAITS/${1:-run}"
  fi
  return 0
}

# What a worker needs to wait as run.sh's own shell does: the functions
# and the settings, into the file of functions, not the environment.
cpu_wait_carry() {
  declare -f cpu_wait cpu_look
  declare -p CPU_BUSY_MOST CPU_WAIT_MOST CPU_LOCK CPU_RUNS CPU_PROBE \
    CPU_PY CPU_WINDOW CPU_PAUSE CPU_POLL CPU_WAITS CPU_OFF \
    CPU_TICKS CPU_SELF
}

# The summary's line. Its first word is one nothing reads a run by.
cpu_wait_said() {
  if [ -n "$CPU_OFF" ]; then
    echo "processor: not waited for -- $CPU_OFF"
    return 0
  fi
  cat "$CPU_WAITS"/* 2> /dev/null | awk -v most="$CPU_BUSY_MOST" \
      -v bound="$CPU_WAIT_MOST" '
    { tests++; all += $1; if ($1 > longest) longest = $1
      if ($2 == "bound") late++ }
    END {
      if (!tests) {
        printf "processor: no test waited for it to fall under %d %%" \
          " busy\n", most
        exit
      }
      printf "processor: %d %s waited for it to fall under %d %% busy," \
        " the longest %d s, %d s in all; %d started anyway after %d s\n",
        tests, (tests == 1 ? "test" : "tests"), most, longest, all,
        late + 0, bound
    }'
}

# Run on its own: one wait, said on stderr when it was one, then the
# command if one is named -- seen by the others while it runs -- or 0,
# so the command after && runs whatever happened. Its file goes on
# every way out, a TERM included.
if [ "${BASH_SOURCE[0]}" = "$0" ]; then
  trap cpu_wait_let_go EXIT
  [ "$CPU_OFF" = "no probe reads the processors on this system" ] \
    && echo "cpu_wait.sh: not waited -- $CPU_OFF" >&2
  cw_from=$SECONDS
  cpu_wait
  if [ -n "$cw_bound" ]; then
    echo "cpu_wait.sh: still over $CPU_BUSY_MOST % busy after" \
         "$CPU_WAIT_MOST s -- starting anyway" >&2
  elif [ "${cw_busy:-0}" -gt 0 ]; then
    echo "cpu_wait.sh: waited $((SECONDS - cw_from)) s for the processor" \
         "to fall under $CPU_BUSY_MOST % busy" >&2
  fi
  [ $# -eq 0 ] && exit 0
  "$@"
  exit
fi
