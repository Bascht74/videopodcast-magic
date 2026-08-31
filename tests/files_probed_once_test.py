"""Every file is measured once, not once per question.

Building the file list asks the same things about the same file over
and over -- length, timecode, channel count, frame rate -- and each
answer costs a process. The answers are kept in memory and on disk,
keyed on size and modification time; this test counts the processes.

In order: the same question twice, every measurement of its own, a file
rewritten under its old name, a caller who spoils what it was handed,
the warming pass before the window is drawn, what the store carries
from one run into the next, and a file that cannot be measured, which
must not stop the rest.
"""
import os
HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = os.environ.get("VPM_SCRIPT") or os.path.join(
    os.path.dirname(HERE), "videopodcast-magic.py")
import importlib.util, shutil, struct, subprocess, sys, tempfile, time, wave
spec = importlib.util.spec_from_file_location("vpm", SCRIPT)
vpm = importlib.util.module_from_spec(spec); sys.modules["vpm"] = vpm
spec.loader.exec_module(vpm)

began = time.time()
done = 0
bad = []


def check(name, ok, extra=""):
    global done
    done += 1
    print("  %-58s %s %s" % (name, "ok" if ok else "FAIL", extra))
    if not ok:
        bad.append("%s [%s]" % (name, extra or "no numbers"))


folder = tempfile.mkdtemp(prefix="vpm_probe_")
# A cache of its own: the suite hands every test the same folder, so
# without this the counts below would depend on which test ran first.
os.environ["VPM_CACHE"] = tempfile.mkdtemp(prefix="vpm_probe_cache_")


def forget_kept():
    """Empty what was kept on disk, so a count means what it says."""
    kept = vpm.cache_folder("probes")
    for name in (os.listdir(kept) if kept and os.path.isdir(kept) else []):
        try:
            os.unlink(os.path.join(kept, name))
        except OSError:
            continue

def tone(name, seconds=1.0, rate=48000):
    path = os.path.join(folder, name)
    with wave.open(path, "wb") as f:
        f.setnchannels(1); f.setsampwidth(2); f.setframerate(rate)
        f.writeframes(b"".join(struct.pack("<h", (i % 400) * 40)
                               for i in range(int(rate * seconds))))
    return path

a, b, c = tone("a.wav"), tone("b.wav"), tone("c.wav")

# --------------------------------------------------------------- Counting
run_real = subprocess.run
count = {"n": 0}

def run_counted(cmd, *args, **kwargs):
    if cmd and str(cmd[0]).endswith("ffprobe"):
        count["n"] += 1
    return run_real(cmd, *args, **kwargs)

subprocess.run = run_counted

def probes(work):
    """Return how many ffprobe processes a piece of work costs."""
    before = count["n"]
    work()
    return count["n"] - before


def duration_of(path):
    """The length ffprobe reports for a file, or None."""
    return vpm.ffprobe_json(path).get("format", {}).get("duration")


def cold():
    """Forget everything that was measured, in memory and on disk."""
    vpm._PROBE.clear()
    forget_kept()

# ------------------------------------------------------- One file, asked twice
print("1. The same question twice")
# The first judgement is the ground under every count below: if ffprobe
# answers nothing, or the counter never sees the process it starts,
# every "costs nothing" further down is true and means nothing.
cold()
first = probes(lambda: vpm.ffprobe_json(a))
answer = duration_of(a)
again = probes(lambda: vpm.ffprobe_json(a))
check("ffprobe answers about the material at all", answer is not None,
      "duration %s s, wanted a number" % (answer,))
check("the first question about a file starts one ffprobe", first == 1,
      "%d processes, wanted 1" % first)
check("the same question a second time starts none", again == 0,
      "%d processes, wanted 0" % again)

print("\n2. Every measurement of its own")
# Each question cold, so that "no second process" is not read off a
# store the question before it filled.
for what, ask in (("the channel count", lambda: vpm.channel_count(a)),
                  ("the length in samples", lambda: vpm.sample_count(a)),
                  ("the timecode", lambda: vpm.file_timecode(a))):
    cold()
    once, twice = probes(ask), probes(ask)
    check("%s is measured on the first ask" % what, once == 1,
          "%d processes, wanted 1" % once)
    check("%s is not asked of ffprobe a second time" % what, twice == 0,
          "%d processes, wanted 0" % twice)

print("\n3. The answer belongs to this file as it stands")
cold()
value_before = duration_of(a)
stamp_before = vpm.file_stamp(a) or ()
tone("a.wav", 2.0)                      # same name, other contents
stamp_after = vpm.file_stamp(a) or ()
after = probes(lambda: vpm.ffprobe_json(a))
value_after = duration_of(a)
# The path is left out of both: it is the same one, and it would carry
# the temporary folder into every failure line.
check("rewriting a file changes what it is known by",
      tuple(stamp_before[1:]) != tuple(stamp_after[1:]),
      "mtime and size %s -> %s, wanted two different ones"
      % (stamp_before[1:], stamp_after[1:]))
check("a changed file is measured again", after == 1,
      "%d processes, wanted 1" % after)
check("a changed file answers with its new length",
      value_before != value_after,
      "%s s -> %s s, wanted two different ones" % (value_before, value_after))

print("\n4. A caller may keep what it got")
vpm._PROBE.clear()
d = vpm.ffprobe_json(a)
check("the description of a file comes back as a dictionary",
      isinstance(d.get("format"), dict),
      "format is %s, wanted a dict" % type(d.get("format")).__name__)
d["format"] = "spoilt"
next_one = vpm.ffprobe_json(a).get("format")
check("a caller who spoils it does not spoil the next one's",
      isinstance(next_one, dict),
      "format is %s after one caller spoilt it, wanted a dict"
      % type(next_one).__name__)

print("\n5. Warming up beforehand")
cold()
warm = probes(lambda: vpm.probe_warm([a, b, c]))
check("warming three files starts one ffprobe for each", warm == 3,
      "%d processes, wanted 3" % warm)
# One line per question, and each one warmed afresh. Chained with "or"
# the first answer is truthy and the other two questions are never
# asked; asked one after another on the same warm cache, the first
# question fills it for the other two and only it can ever fall.
for what, ask in (("the whole description", vpm.ffprobe_json),
                  ("the channel count", vpm.channel_count),
                  ("the length in samples", vpm.sample_count)):
    cold()
    vpm.probe_warm([a, b, c])
    cost = dict((p, probes(lambda p=p: ask(p))) for p in (a, b, c))
    check("%s costs nothing after warming" % what,
          set(cost.values()) == set([0]),
          "%s, wanted 0 for each"
          % dict((os.path.basename(p), n) for p, n in cost.items()))

print("\n6. What ffprobe said outlives the run")
# Asking again costs a process: cheap here, dear on a builder where
# starting processes is most of what a test spends its time on.
cold()
first = probes(lambda: vpm.ffprobe_json(a))
measured = duration_of(a)
vpm._PROBE.clear()                      # a later run, nothing remembered
second = probes(lambda: vpm.ffprobe_json(a))
stored = duration_of(a)
check("the run that measures starts one ffprobe", first == 1,
      "%d processes, wanted 1" % first)
check("a later run with no memory of it starts none", second == 0,
      "%d processes, wanted 0" % second)
check("what the store gives back is what was measured",
      measured is not None and stored == measured,
      "%s s measured, %s s out of the store" % (measured, stored))

# Changed on disk means measured again, not answered from the store.
with open(a, "r+b") as f:
    f.seek(0, 2)
    f.write(b"\0" * 64)
vpm._PROBE.clear()
again = probes(lambda: vpm.ffprobe_json(a))
check("a file changed on disk is measured again, store or no store",
      again == 1, "%d processes, wanted 1" % again)

# A half-written file is what a run broken off in the middle leaves.
# Whether one was kept at all comes first: with nothing in the store,
# "measured again" is true of any program and says nothing.
vpm._PROBE.clear()
stamp = vpm.file_stamp(a)
kept = vpm.probe_cache_path(("ffprobe",) + stamp) if stamp else None
there = bool(kept) and os.path.exists(kept)
check("the store did keep what was measured", there,
      "kept file %s, wanted one that exists"
      % (os.path.basename(kept) if kept else "not named"))
if there:
    open(kept, "wb").close()
empty = probes(lambda: vpm.ffprobe_json(a))
check("an empty kept file is measured again, not believed", empty == 1,
      "%d processes, wanted 1" % empty)

print("\n7. What cannot be measured must not stop anything")
missing = os.path.join(folder, "not-there.wav")
check("the file this asks about really is not there",
      not os.path.exists(missing),
      "%s is there: %s, wanted False"
      % (os.path.basename(missing), os.path.exists(missing)))
cold()
try:
    vpm.probe_warm([a, missing, b])
    threw = ""
except Exception as e:
    threw = "%s while warming" % type(e).__name__
rest = probes(lambda: [vpm.ffprobe_json(a), vpm.ffprobe_json(b)])
check("a missing file does not stop the others being warmed",
      threw == "" and rest == 0,
      threw or "%d processes for the two good files afterwards, wanted 0"
      % rest)
try:
    got = vpm.ffprobe_json(missing)
    threw = ""
except Exception as e:
    got, threw = None, "%s while asking" % type(e).__name__
check("asking about a missing file answers instead of throwing",
      threw == "" and isinstance(got, dict),
      threw or "answer is %s, wanted a dict" % type(got).__name__)

subprocess.run = run_real
shutil.rmtree(folder, ignore_errors=True)

print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
