# -*- coding: utf-8 -*-
"""A block taken out of a recording by hand stays out."""
import os
HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = os.environ.get("VPM_SCRIPT") or os.path.join(
    os.path.dirname(HERE), "videopodcast-magic.py")
import importlib.util, shutil, sys, tempfile, wave
import numpy as np
spec = importlib.util.spec_from_file_location("vpm", SCRIPT)
vpm = importlib.util.module_from_spec(spec); sys.modules["vpm"] = vpm
spec.loader.exec_module(vpm)

error = []
def check(name, ok, extra=""):
    print("  %-52s %s %s" % (name, "ok" if ok else "FAIL", extra))
    if not ok:
        error.append(name)

RATE = 48000
folder = tempfile.mkdtemp(prefix="vpm_apart_")


def block(name, seconds=4.0, hz=300.0):
    path = os.path.join(folder, name)
    t = np.arange(int(seconds * RATE)) / float(RATE)
    x = 0.4 * np.sin(2 * np.pi * hz * t)
    with wave.open(path, "wb") as f:
        f.setnchannels(1); f.setsampwidth(2); f.setframerate(RATE)
        f.writeframes((x * 32767).astype("<i2").tobytes())
    return path


one = block("REC0001.wav")
two = block("REC0002.wav")
three = block("REC0003.wav")
other = block("Guest0001.wav", hz=700.0)
every = [one, two, three, other]

print("1. Without a mark the blocks belong together")
chains = vpm.group_recording_parts(every)
check("two recordings out of four files", len(chains) == 2, str(len(chains)))
long_one = max(chains, key=lambda c: len(c[0]))
check("and one of them has three blocks", len(long_one[0]) == 3,
      str([os.path.basename(x) for x in long_one[0]]))

print("\n2. A marked block stands on its own")
chains = vpm.group_recording_parts(every, apart=[two])
rows = sorted([sorted(os.path.basename(x) for x in row)
               for row, _d in chains])
check("three recordings now", len(chains) == 3, str(rows))
check("the marked one is alone", ["REC0002.wav"] in rows, str(rows))
check("and the rest stays together",
      ["REC0001.wav", "REC0003.wav"] in rows, str(rows))

print("\n3. It is not fetched back in either")
# Only the first block is selected: the others are found in the folder.
chains = vpm.group_recording_parts([one], apart=[two])
check("the search skips the marked block",
      [os.path.basename(x) for x in chains[0][0]]
      == ["REC0001.wav", "REC0003.wav"],
      str([os.path.basename(x) for x in chains[0][0]]))
got, _hints = vpm.collect_with_continuations([one], False, [two])
check("and so does the run",
      sorted(os.path.basename(x) for x in got)
      == ["REC0001.wav", "REC0003.wav"],
      str(sorted(os.path.basename(x) for x in got)))

print("\n4. The whole recording knows its blocks")
family = vpm.recording_family(one)
check("all three are named", len(family) == 3, str(sorted(
    os.path.basename(x) for x in family)))
check("the other recording is not in it",
      os.path.abspath(other) not in family)
check("and it works from any block",
      vpm.recording_family(three) == family)

print("\n5. Nothing marked, nothing changed")
check("an empty mark is the same as none",
      vpm.group_recording_parts(every, apart=[])
      == vpm.group_recording_parts(every))
check("and a mark on a file nobody has changes nothing",
      len(vpm.group_recording_parts(every, apart=["/nowhere.wav"])) == 2)

shutil.rmtree(folder, ignore_errors=True)
print()
if error:
    print("FAIL: " + ", ".join(error))
    sys.exit(1)
print("All good.")
