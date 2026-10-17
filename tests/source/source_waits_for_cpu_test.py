# -*- coding: utf-8 -*-
"""A test starts only when the machine has processor to spare, one a look.

Waiters source tests/cpu_wait.sh into bash and start nothing but a line
in a log; a script off a list stands in for the look, a live process for
another run that waits, each case with a lock of its own. In order: busy
looks hold a start, the first free one lets it go, kept; two waiters
never start on one look, the lock let go while a test runs; the real
look counts a start as a busy processor; a gone holder's lock is taken
over; the bound ends a wait, kept; the summary's sums; behind a lasting
turn a waiter asks slowly and makes no lock; a wait's file in the folder
of runs goes with it, on its own and on run.sh's ways out; and alone,
CI, a limit of 0, inside a suite, no probe: no look at all.
"""
PLATFORM_BOUND = True
import os
import sys
# tests/, where the helpers and state/ lie; this file may stand in a
# folder under it, or in one under that.
HERE = os.path.dirname(os.path.abspath(__file__))
while not os.path.isfile(os.path.join(HERE, "the_program.py")) \
        and os.path.dirname(HERE) != HERE:
    HERE = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import re
import shutil
import subprocess
import tempfile
import time

GATE = os.path.join(HERE, "cpu_wait.sh")
# Far above what the slowest case takes on the slowest builder, so a wait
# that never ends is red here with the number beside it.
WAIT = 120
# How long one look of the pair takes, and how long each of the two
# stays after its start, a test still running: long enough that two looks
# at once, and a lock never let go, are told apart in whole seconds on a
# loaded machine.
LOOK = 2
STAY = 6

began = time.time()
done = 0
bad = []


def check(name, ok, extra=""):
    global done
    done += 1
    print("  %-58s %s %s" % (name, "ok" if ok else "FAIL", extra))
    if not ok:
        bad.append("%s [%s]" % (name, extra or "no numbers"))


def bash():
    r"""Where bash is -- on Windows Git's, not the WSL stub in System32."""
    if sys.platform == "win32":
        for root in (os.environ.get("EXEPATH"),
                     os.path.join(os.environ.get("ProgramFiles", ""),
                                  "Git")):
            exe = os.path.join(root or "", "bin", "bash.exe")
            if root and os.path.isfile(exe):
                return exe
    return shutil.which("bash") or "bash"


BASH = bash()


def spelt(path):
    """The path in bash's own spelling (/c/Users/... on Windows)."""
    if sys.platform != "win32":
        return path
    got = subprocess.run([BASH, "-c", 'cygpath -u "$0"', path],
                         capture_output=True, text=True)
    return got.stdout.strip() if got.returncode == 0 and got.stdout.strip() \
        else path


# The stand-in for the look. A look with a window of 0 only asks whether
# there is a probe at all, and is neither counted nor logged.
PROBE = r'''dir=${0%/*}
if [ "$1" = 0 ]; then head -1 "$dir/values"; exit 0; fi
echo "look $(date +%s)" >> "$dir/log"
n=0
{ read -r n < "$dir/count"; } 2> /dev/null
n=$((n + 1))
echo "$n" > "$dir/count"
v=$(sed -n "${n}p" "$dir/values")
[ -n "$v" ] || v=$(tail -1 "$dir/values")
[ -f "$dir/slow" ] && sleep "$(cat "$dir/slow")"
echo "$v"
'''
# Stand-ins for sleep and mkdir, first on a waiter's PATH: each call
# written down, then the real one, found on the rest of the PATH.
COUNTED = r'''#!/bin/sh
echo "${0##*/} $*" >> "$STANDIN_LOG"
PATH=${PATH#*:}
exec "${0##*/}" "$@"
'''
# A waiter: the gate, then a line saying it started, then the summary's
# line, then as long as it is asked to stay -- a test still running.
WAITER = r'''[ "$4" = inside ] && export VPM_FIXTURES_HELD="$$ $2"
. "$1"
CPU_WAITS="$2/waits"
mkdir -p "$CPU_WAITS"
cpu_wait "$3"
echo "start $(date +%s)" >> "$2/log"
cpu_wait_said > "$2/said"
sleep "${5:-0}"
'''
OUTSIDE = ("CI", "GITHUB_ACTIONS", "VPM_FIXTURES_HELD", "VPM_CPU_BUSY_MOST",
           "VPM_CPU_WAIT_MOST", "VPM_CPU_PROBE", "VPM_CPU_LOCK",
           "VPM_CPU_TICKS")
ROOT = tempfile.mkdtemp(prefix="vpm-cpu-wait-")


# Another run that waits, as the gate sees one: a process that lives,
# named in the folder of runs beside the lock. Kept alive on its input.
peer = subprocess.Popen([BASH, "-c", "echo $$; read -r _"],
                        stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                        text=True)
PEER = peer.stdout.readline().strip()


def case(name, values, extra=None, slow=False, alone=False):
    """A folder with its list of busy shares, its stand-in and its lock."""
    folder = os.path.join(ROOT, name)
    os.makedirs(folder)
    if not alone:
        os.makedirs(os.path.join(folder, "lock.runs"))
        open(os.path.join(folder, "lock.runs", PEER), "w").close()
    with open(os.path.join(folder, "values"), "w") as f:
        f.write("".join("%d\n" % v for v in values))
    with open(os.path.join(folder, "probe.sh"), "w", newline="\n") as f:
        f.write(PROBE)
    if slow:
        with open(os.path.join(folder, "slow"), "w") as f:
            f.write("%d\n" % LOOK)
    env = {k: v for k, v in os.environ.items() if k not in OUTSIDE}
    # The limit said here and not left to the default, which may move.
    env.update(VPM_CPU_PROBE=spelt(os.path.join(folder, "probe.sh")),
               VPM_CPU_LOCK=spelt(os.path.join(folder, "lock")),
               VPM_CPU_BUSY_MOST="90", VPM_CPU_WAIT_MOST="30")
    env.update(extra or {})
    return folder, env


running = []


def wait_in(folder, env, who, how="", stay=0):
    """One waiter started in the case's folder; its end is timed below."""
    p = subprocess.Popen([BASH, "-c", WAITER, "_", spelt(GATE),
                          spelt(folder), who, how, str(stay)],
                         env=env, stdout=subprocess.PIPE,
                         stderr=subprocess.STDOUT)
    running.append([p, time.time(), None])
    return running[-1]


def log(folder):
    """The log as (what, second) pairs, looks and starts in order."""
    try:
        with open(os.path.join(folder, "log")) as f:
            rows = [line.split() for line in f]
    except OSError:
        return []
    return [(r[0], int(r[1])) for r in rows if len(r) == 2
            and r[1].isdigit()]


def shown(rows):
    """The log's words in order, a run of one word counted: look x3 start."""
    runs = []
    for w, _ in rows:
        if runs and runs[-1][0] == w:
            runs[-1][1] += 1
        else:
            runs.append([w, 1])
    return " ".join(w if n == 1 else "%s x%d" % (w, n)
                    for w, n in runs) or "nothing"


def kept(folder):
    """The lines the gate kept for the summary, one per test that waited."""
    out = []
    waits = os.path.join(folder, "waits")
    for name in sorted(os.listdir(waits)) if os.path.isdir(waits) else []:
        with open(os.path.join(waits, name)) as f:
            out += ["%s: %s" % (name, line.strip()) for line in f]
    return out


def secs(took):
    return "%.1f" % took if took is not None else "never"


# The words run.sh judges a run by; what a waiter printed is quoted, so
# it goes through this first.
LOUD = ("FAIL", "Traceback", "SKIPPED", "LEFT OUT", "Left out",
        "Error", "error", "Exception", "Interrupt")


def quiet(text):
    """Text out of another process, safe to print in a line of ours."""
    text = " ".join(str(text).split())
    for word in LOUD:
        text = text.replace(word, word[:2] + "-" + word[2:])
    return text


def output(argv, env):
    """What a bash line printed, or nothing if it did not end in time."""
    try:
        return subprocess.run(argv, env=env, capture_output=True, text=True,
                              timeout=WAIT).stdout
    except (OSError, subprocess.TimeoutExpired):
        return ""


def said(folder):
    try:
        with open(os.path.join(folder, "said")) as f:
            return f.read().strip()
    except OSError:
        return ""


# A process that has ended, for a lock it left behind.
gone = output([BASH, "-c", "echo $$"], dict(os.environ)).strip()

busy, env = case("busy", [95, 95, 95, 40])
wait_in(busy, env, "busy")
pair, env = case("pair", [40], slow=True)
wait_in(pair, env, "first", stay=STAY)
wait_in(pair, env, "second", stay=STAY)
left, env = case("left", [40])
os.makedirs(os.path.join(left, "lock"))
with open(os.path.join(left, "lock", "holder"), "w") as f:
    f.write("%s 4711 1\n" % gone)
taken = wait_in(left, env, "left")
late, env = case("late", [95], {"VPM_CPU_WAIT_MOST": "2"})
bounded = wait_in(late, env, "late")
# A holder in a first look that lasts: a process that lives, its line
# never changing, so the waiter behind it asks until its bound of 5 s.
queue, env = case("queue", [40], {"VPM_CPU_WAIT_MOST": "5"})
os.makedirs(os.path.join(queue, "lock"))
with open(os.path.join(queue, "lock", "holder"), "w") as f:
    f.write("%s 4711 1\n" % PEER)
os.makedirs(os.path.join(queue, "bin"))
for tool in ("sleep", "mkdir"):
    with open(os.path.join(queue, "bin", tool), "w", newline="\n") as f:
        f.write(COUNTED)
    os.chmod(os.path.join(queue, "bin", tool), 0o755)
env.update(PATH=os.path.join(queue, "bin") + os.pathsep + env.get("PATH", ""),
           STANDIN_LOG=spelt(os.path.join(queue, "calls")))
asking = wait_in(queue, env, "queue")
offs = {}
folder, env = case("alone", [95], {"VPM_CPU_WAIT_MOST": "3"}, alone=True)
offs["alone"] = folder, wait_in(folder, env, "alone")
for name, values, extra, how in (
        ("ci", [95], {"CI": "true"}, ""),
        ("zero", [95], {"VPM_CPU_BUSY_MOST": "0"}, ""),
        ("inside", [95], {}, "inside"),
        ("noprobe", [], {}, "")):
    folder, env = case(name, values, dict(extra, VPM_CPU_WAIT_MOST="3"))
    offs[name] = folder, wait_in(folder, env, name, how)

# Every waiter timed to its end, all of them side by side.
while any(r[2] is None for r in running) and time.time() - began < WAIT:
    for r in running:
        if r[2] is None and r[0].poll() is not None:
            r[2] = time.time()
    time.sleep(0.02)
for r in running:
    if r[2] is None:
        r[0].kill()
    r.append(r[0].communicate()[0].decode("utf-8", "replace").strip())

# The wait as a command of its own, twice, while the other run lives:
# with a command that lists the folder of runs, and in the && form.
own, env = case("own", [40])
runs = os.path.join(own, "lock.runs")
during = output([BASH, spelt(GATE), BASH, "-c", 'ls "$0"', spelt(runs)],
                env).split()
after = sorted(os.listdir(runs))
output([BASH, spelt(GATE)], env)
after_and = sorted(os.listdir(runs))
peer.communicate("")

# ------------------------------------------------------------------ 1.
print("1. A machine busy for three looks, then free")
rows = log(busy)
check("a start waits while the looks find the machine busy",
      [w for w, _ in rows][:3] == ["look"] * 3,
      "log: %s" % shown(rows))
check("a start goes on the first look that finds room",
      [w for w, _ in rows] == ["look"] * 4 + ["start"],
      "log: %s, wanted four looks and a start" % shown(rows))
check("a start that waited is kept for the summary",
      len(kept(busy)) == 1 and not kept(busy)[0].endswith("bound"),
      "kept: %s" % (kept(busy) or "nothing"))

# ------------------------------------------------------------------ 2.
print("\n2. Two waiters at once, each look %d s long" % LOOK)
# Each line is written as it happens, so a start can stand after the next
# look in the log when its own line came late; the seconds cannot.
rows = log(pair)
looks = [t for w, t in rows if w == "look"]
starts = [t for w, t in rows if w == "start"]
check("two waiters never start on one look",
      len(looks) == 2 and len(starts) == 2 and looks[1] - looks[0] >= LOOK,
      "looks began at %s, starts at %s; a look takes %d s"
      % (looks, starts, LOOK))
check("the lock is let go after a start, while the test runs",
      len(starts) == 2 and starts[1] - starts[0] <= LOOK + 3,
      "starts at %s, one look of %d s between them, and the first stays"
      " %d s after its own" % (starts, LOOK, STAY))

# ------------------------------------------------------------------ 3.
print("\n3. The real look twice, on four processors at 70 % busy")
# Their counters stand still, and the line the looks keep holds them as
# they were a second and a half ago: 70 % busy over that second. The
# first look is under the limit and is written down as a start; the
# second, right after it, has to count that start as one of the four.
herd, env = case("herd", [])
del env["VPM_CPU_PROBE"]
env.update(PY=spelt(sys.executable),
           VPM_CPU_TICKS=os.path.join(herd, "counters"))
with open(os.path.join(herd, "counters"), "w") as f:
    f.write(" ".join(["70 0 30 0"] * 4))
with open(os.path.join(herd, "lock.ticks"), "w") as f:
    f.write("s %r %s\n" % (time.time() - 1.5, " ".join(["0"] * 16)))
looks = output(
    [BASH, "-c", '. "$1"; for i in 1 2; do cpu_look 0.25 "$2" 90; done',
     "_", spelt(GATE), spelt(os.path.join(herd, "lock.ticks"))], env).split()
looks = [int(v) for v in looks if v.isdigit()]
check("a start counts as a busy processor on the next look",
      len(looks) == 2 and looks[0] == 70 and 20 <= looks[1] - looks[0] <= 25,
      "the looks read %s, wanted 70 and then up to one processor in four"
      " more" % (looks or "nothing"))

# ------------------------------------------------------------------ 4.
print("\n4. A lock left by a process that is gone")
took = taken[2] - taken[1] if taken[2] is not None else None
check("a lock left by a process that is gone is taken over",
      took is not None and took < 5 and [w for w, _ in log(left)]
      == ["look", "start"],
      "started after %s s (10 s is the rule for a holder that went quiet),"
      " log: %s" % (secs(took), shown(log(left))))

# ------------------------------------------------------------------ 5.
print("\n5. A machine that stays busy, a bound of 2 s")
took = bounded[2] - bounded[1] if bounded[2] is not None else None
# The gate counts whole seconds, so a bound of 2 can end a wait after 1.
check("the bound ends a wait on a machine that stays busy",
      took is not None and 1 <= took < 30
      and "start" in [w for w, _ in log(late)],
      "ended after %s s against a bound of 2 s, log: %s"
      % (secs(took), shown(log(late))))
check("a start after the bound is kept as one",
      len(kept(late)) == 1 and kept(late)[0].endswith(" bound"),
      "kept: %s" % (kept(late) or "nothing"))

# ------------------------------------------------------------------ 6.
print("\n6. The summary over three kept waits")
sums = os.path.join(ROOT, "sums")
os.makedirs(os.path.join(sums, "waits"))
for name, line in (("a", "3 "), ("b", "7 bound"), ("c", "0 ")):
    with open(os.path.join(sums, "waits", name), "w", newline="\n") as f:
        f.write(line + "\n")
env = {k: v for k, v in os.environ.items() if k not in OUTSIDE}
env.update(VPM_CPU_PROBE=spelt(os.path.join(busy, "probe.sh")),
           VPM_CPU_LOCK=spelt(os.path.join(sums, "lock")),
           VPM_CPU_BUSY_MOST="80", VPM_CPU_WAIT_MOST="500")
line = output(
    [BASH, "-c", '. "$1"; CPU_WAITS="$2/waits"; cpu_wait_said', "_",
     spelt(GATE), spelt(sums)], env).strip()
check("the summary counts the waits, the longest, the sum, the late",
      re.search(r"^processor: 3 tests waited\b.* under 80 % busy, the"
                r" longest 7 s, 10 s in all; 1 started anyway after 500 s$",
                line) is not None,
      "line: %s" % (line or "none"))

# ------------------------------------------------------------------ 7.
print("\n7. Behind a first look that lasts, a bound of 5 s")
try:
    with open(os.path.join(queue, "calls")) as f:
        calls = [line.split() for line in f]
except OSError:
    calls = []
# The waiter's own last sleep, of 0 s, is no ask; nor is a mkdir -p.
asks = len([c for c in calls if c[:1] == ["sleep"] and c[1:] != ["0"]])
made = len([c for c in calls if c[:1] == ["mkdir"] and c[1:2] != ["-p"]])
took = asking[2] - asking[1] if asking[2] is not None else None
most = 11 + 2 * took if took is not None else 0
if sys.platform == "win32" and not calls:
    # Git Bash on the Windows builder does not reach the stand-ins put
    # first on the waiter's PATH: measured 0 asks in 5.3 s while the
    # waiter waited out its bound. The queue's cost is judged on macOS
    # and Linux; the wait itself is judged above on every system.
    print("LEFT OUT: the queue's asks are not counted here -- the stand-ins"
          " for sleep and mkdir first on the waiter's PATH were not reached"
          " (0 calls in %s s); macOS and Linux judge them." % secs(took))
else:
    check("behind a turn that lasts, a waiter asks at most twice a second",
          took is not None and took >= 3 and 10 <= asks <= most,
          "%d asks in %s s, wanted ten quick ones and then at most two a"
          " second, %d in all" % (asks, secs(took), most))
    check("an ask behind a holder starts no mkdir",
          asks >= 10 and made == 0,
          "%d mkdir of the lock in %d asks" % (made, asks))

# ------------------------------------------------------------------ 8.
print("\n8. A wait's own file in the folder of runs")
check("a wait run on its own is seen while it runs and gone after",
      len([n for n in during if n != PEER]) == 1 and after == [PEER]
      and after_and == [PEER],
      "while its command ran: %s; after: %s; after the && form: %s,"
      " the other run being %s" % (during, after, after_and, PEER))
# run.sh is a whole suite and is not started here: its ways out are read.
with open(os.path.join(HERE, "run.sh"), encoding="utf-8") as f:
    suite = f.read()
exits = re.findall(r"^trap '?(\w+)'? EXIT$", suite, re.M)
taken_out = {}
for name in exits:
    body = re.search(r"^%s\(\) \{\n(.*?)^\}" % name, suite, re.M | re.S)
    taken_out[name] = bool(body) and re.search(
        r"^\s*cpu_wait_let_go\s*$", body.group(1), re.M) is not None
check("every way out of run.sh takes its file out of the runs",
      exits and all(taken_out.values()),
      "trap ... EXIT names %s; calls cpu_wait_let_go: %s"
      % (exits or "nothing", taken_out))

# ------------------------------------------------------------------ 9.
print("\n9. Where the wait is off")


def off(name):
    """Whether the case's waiter started without a look, and the numbers."""
    folder, r = offs[name]
    took = r[2] - r[1] if r[2] is not None else None
    return [w for w, _ in log(folder)] == ["start"] and took is not None \
        and took < 3, "log: %s, ended after %s s, line: %s" % (
            shown(log(folder)), secs(took), said(folder) or "none")


ok, numbers = off("alone")
check("a run alone starts its tests without a look", ok, numbers)
ok, numbers = off("ci")
check("with CI set a test starts without a look", ok, numbers)
ok, numbers = off("zero")
check("with VPM_CPU_BUSY_MOST=0 a test starts without a look", ok, numbers)
ok, numbers = off("inside")
check("inside a suite a test started, it starts without a look", ok,
      numbers)
ok, numbers = off("noprobe")
check("with no probe a test starts without a look, and it is said",
      ok and "no probe" in said(offs["noprobe"][0]), numbers)

for r in running:
    if r[3]:
        print("  (a waiter printed: %s)" % quiet(r[3].splitlines()[:3]))
shutil.rmtree(ROOT, ignore_errors=True)
print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
