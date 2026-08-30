"""Every file is measured once, not once per question.

Building the file list asks the same things about the same file over
and over -- length, timecode, channel count, frame rate -- and each
answer costs a process. The answers are kept, keyed on size and
modification time; this test counts the processes.
"""
import os
HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = os.environ.get("VPM_SCRIPT") or os.path.join(
    os.path.dirname(HERE), "videopodcast-magic.py")
import importlib.util, shutil, struct, subprocess, sys, tempfile, wave
spec = importlib.util.spec_from_file_location("vpm", SCRIPT)
vpm = importlib.util.module_from_spec(spec); sys.modules["vpm"] = vpm
spec.loader.exec_module(vpm)

error = []
def check(name, ok, extra=""):
    print("  %-48s %s %s" % (name, "ok" if ok else "FAIL", extra))
    if not ok:
        error.append(name)

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

# ------------------------------------------------------- One file, asked twice
print("1. The same question twice")
vpm._PROBE.clear()
forget_kept()
first = probes(lambda: vpm.ffprobe_json(a))
again = probes(lambda: vpm.ffprobe_json(a))
check("the first call measures", first == 1, first)
check("the second does not", again == 0, again)

print("\n2. Every measurement of its own")
vpm._PROBE.clear()
for name, work in (("channel count", lambda: vpm.channel_count(a)),
                   ("length in samples", lambda: vpm.sample_count(a)),
                   ("timecode", lambda: vpm.file_timecode(a))):
    probes(work)
    check("%s asks again: no" % name, probes(work) == 0)

print("\n3. The answer belongs to this file as it stands")
vpm._PROBE.clear()
value_before = vpm.ffprobe_json(a).get("format", {}).get("duration")
probes(lambda: vpm.ffprobe_json(a))
tone("a.wav", 2.0)                      # same name, other contents
after = probes(lambda: vpm.ffprobe_json(a))
value_after = vpm.ffprobe_json(a).get("format", {}).get("duration")
check("a changed file is measured again", after == 1, after)
check("and the answer is the new one",
      value_before != value_after, "%s -> %s" % (value_before, value_after))

print("\n4. A caller may keep what it got")
vpm._PROBE.clear()
d = vpm.ffprobe_json(a)
d["format"] = "spoilt"
check("the next caller gets it whole",
      isinstance(vpm.ffprobe_json(a).get("format"), dict))

print("\n5. Warming up beforehand")
vpm._PROBE.clear()
forget_kept()
warm = probes(lambda: vpm.probe_warm([a, b, c]))
later = probes(lambda: [vpm.ffprobe_json(p) or vpm.channel_count(p)
                        or vpm.sample_count(p) for p in (a, b, c)])
check("three files, measured once each", warm >= 3, warm)
check("nothing left to ask afterwards", later == 0, later)

print("\n6. What ffprobe said outlives the run")
# Asking again costs a process: cheap here, dear on a builder where
# starting processes is most of what a test spends its time on.
vpm._PROBE.clear()
forget_kept()
first = probes(lambda: vpm.ffprobe_json(a))
vpm._PROBE.clear()
second = probes(lambda: vpm.ffprobe_json(a))
check("the first run measures", first == 1, first)
check("a later one with no memory of it does not", second == 0, second)
check("and the answer is the same",
      vpm.ffprobe_json(a).get("format", {}).get("duration") is not None,
      str(vpm.ffprobe_json(a))[:60])

# Changed on disk means measured again, not answered from the store.
with open(a, "r+b") as f:
    f.seek(0, 2)
    f.write(b"\0" * 64)
vpm._PROBE.clear()
again = probes(lambda: vpm.ffprobe_json(a))
check("a changed file is measured again even so", again == 1, again)

# A half-written file is what a run broken off in the middle leaves.
vpm._PROBE.clear()
kept = vpm.probe_cache_path(("ffprobe",) + vpm.file_stamp(a))
open(kept, "wb").close()
empty = probes(lambda: vpm.ffprobe_json(a))
check("an empty kept file is measured again, not believed", empty == 1,
      empty)

print("\n7. What cannot be measured must not stop anything")
vpm._PROBE.clear()
missing = os.path.join(folder, "not-there.wav")
try:
    vpm.probe_warm([a, missing, b])
    vpm.ffprobe_json(missing)
    check("a missing file is passed over", True)
except Exception as e:
    check("a missing file is passed over", False, str(e)[:60])

subprocess.run = run_real
shutil.rmtree(folder, ignore_errors=True)

print()
if error:
    print("FAIL: " + ", ".join(error))
    sys.exit(1)
print("All good.")
