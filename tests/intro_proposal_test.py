# -*- coding: utf-8 -*-
"""A jingle is proposed as the intro, not for "ignore this video".

A file that fits nothing used to be proposed for leaving out, whatever
it was. That is right for a camera whose microphone heard nothing of the
room, and wrong for a jingle: a jingle fits nothing because it is not a
camera, and it is meant to be used -- set at the front rather than
measured. The two are told apart by length, against the middle of the
material around them.
"""
import os
HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = os.environ.get("VPM_SCRIPT") or os.path.join(
    os.path.dirname(HERE), "videopodcast-magic.py")
import importlib.util, shutil, subprocess, sys, wave
import numpy as np
sys.path.insert(0, HERE)
from fixture_root import fixture

spec = importlib.util.spec_from_file_location("vpm", SCRIPT)
vpm = importlib.util.module_from_spec(spec)
sys.modules["vpm"] = vpm
spec.loader.exec_module(vpm)

error = []


def check(name, ok, extra=""):
    print("  %-58s %s %s" % (name, "ok" if ok else "FAIL", extra))
    if not ok:
        error.append(name)


#------------------------------------------------------------- Material

RATE = 48000
CAM_LEN, JINGLE_LEN = 60.0, 4.0


def turns(seconds, seed):
    """Speech-like turns: noise in irregular pieces with pauses between."""
    rng = np.random.default_rng(seed)
    n = int(seconds * RATE)
    x = np.zeros(n)
    t = 0.2
    while t < seconds - 1.0:
        long_s = float(rng.uniform(0.25, 0.9))
        k, i0 = int(long_s * RATE), int(t * RATE)
        shape = np.hanning(k) if k > 2 else 1.0
        x[i0:i0 + k] = rng.normal(0, 0.25, k) * shape
        t += long_s + float(rng.uniform(0.2, 1.1))
    return x


def write(path, x):
    with wave.open(path, "wb") as f:
        f.setnchannels(1)
        f.setsampwidth(2)
        f.setframerate(RATE)
        f.writeframes((np.clip(x, -1, 1) * 32000).astype("<i2").tobytes())


D = fixture("intropropose")
shutil.rmtree(D, ignore_errors=True)
os.makedirs(D)
write(D + "/room.wav", turns(CAM_LEN + 10, 1))
# A jingle: music, loud all the way through, with no turns to align on.
t = np.arange(int(JINGLE_LEN * RATE)) / float(RATE)
music = 0.1 * (np.sin(2 * np.pi * 220 * t) + np.sin(2 * np.pi * 277 * t)
               + np.sin(2 * np.pi * 330 * t))
write(D + "/music.wav", music * (1.0 + 0.3 * np.sin(2 * np.pi * 2.0 * t)))
# The other kind of file that fits nothing: a camera as long as the
# rest whose microphone heard nothing but its own hiss.
write(D + "/dead.wav",
      np.random.default_rng(3).normal(0, 0.2, int(CAM_LEN * RATE)))

# One ffmpeg call for all four videos: a process start is what the
# Windows builder charges for. Colour bars at ultrafast, since no frame
# is ever decoded.
PICTURE = ["-c:v", "libx264", "-preset", "ultrafast", "-pix_fmt", "yuv420p",
           "-c:a", "pcm_s16le"]
command = ["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i",
           "smptebars=size=320x180:rate=25:duration=%.1f" % (CAM_LEN + 10),
           "-i", D + "/room.wav", "-i", D + "/music.wav",
           "-i", D + "/dead.wav"]
for name, from_s in (("CamA", 0.0), ("CamB", 4.0)):
    command += ["-map", "0:v", "-map", "1:a", "-ss", "%.2f" % from_s,
                "-t", "%.2f" % CAM_LEN] + PICTURE + [D + "/%s.mov" % name]
command += ["-map", "0:v", "-map", "2:a", "-t", "%.2f" % JINGLE_LEN] \
    + PICTURE + [D + "/Jingle.mov"]
command += ["-map", "0:v", "-map", "3:a", "-t", "%.2f" % CAM_LEN] \
    + PICTURE + [D + "/Dead.mov"]
subprocess.run(command, check=True)

A, B = D + "/CamA.mov", D + "/CamB.mov"
JINGLE, DEAD = D + "/Jingle.mov", D + "/Dead.mov"
FILES = [A, B, JINGLE, DEAD]


#------------------------------------------- 1. What the measurement says

print("1. Two cameras, a jingle and a camera that heard nothing")
data, text = vpm.measure_time_axis(FILES)


def short(row):
    return sorted(os.path.basename(p) for p in (row or []))


print("   weak: %s   unplaceable: %s   brief: %s"
      % (short(data.get("weak")), short(data.get("unplaceable")),
         short(data.get("brief"))))
check("both files that fit nothing are named",
      short(data.get("weak")) == ["Dead.mov", "Jingle.mov"],
      str(short(data.get("weak"))))
check("only the long one has no place at all",
      short(data.get("unplaceable")) == ["Dead.mov"],
      str(short(data.get("unplaceable"))))
check("and only the short one counts as far shorter than the rest",
      short(data.get("brief")) == ["Jingle.mov"],
      str(short(data.get("brief"))))
# The number the rule turns on, said out loud: what each file is
# against the middle of the others.
# The lengths come off the envelopes the measurement above already
# computed -- the same numbers the rule works on, and free to read.
length = dict((p, len(vpm.video_envelope(p, 5.0, 4000)) * 0.005)
              for p in FILES)
for p in (JINGLE, DEAD):
    others = sorted(s for q, s in length.items() if q != p)
    share = length[p] / others[len(others) // 2]
    print("   %-11s %5.1f s, %.3f of the middle of the others"
          % (os.path.basename(p), length[p], share))
    check("%s falls on the right side of the limit"
          % os.path.basename(p),
          (share <= vpm.INTRO_SHORT_ENOUGH) == (p == JINGLE),
          "%.3f against %.2f" % (share, vpm.INTRO_SHORT_ENOUGH))


#------------------------------------------------- 2. What is proposed

print("\n2. The proposal: intro for the one, out of the run for the other")
kinds = dict((p, vpm.Value(vpm.TYPE_CONTENT)) for p in FILES)
moved = vpm.kind_proposal_say(kinds, data)
print("   %s" % {os.path.basename(p): kinds[p].get() for p in FILES})
check("the jingle is proposed as the intro",
      kinds[JINGLE].get() == vpm.TYPE_INTRO, kinds[JINGLE].get())
check("the camera that heard nothing stays out of the run",
      kinds[DEAD].get() == vpm.TYPE_IGNORED, kinds[DEAD].get())
check("the cameras keep what they were",
      kinds[A].get() == vpm.TYPE_CONTENT
      and kinds[B].get() == vpm.TYPE_CONTENT)
check("both moves are reported back", sorted(moved) == sorted([JINGLE, DEAD]),
      str([os.path.basename(p) for p in moved]))
check("a second round changes nothing again",
      vpm.kind_proposal_say(kinds, data) == [])
check("and a measurement that places them takes both proposals back",
      sorted(vpm.kind_proposal_apply(kinds, [], [])) == sorted([JINGLE, DEAD])
      and kinds[JINGLE].get() == vpm.TYPE_CONTENT
      and kinds[DEAD].get() == vpm.TYPE_CONTENT)


#--------------------------------------------- 3. Where it keeps its hands off

print("\n3. The proposal stops at every answer somebody gave")
by_hand = vpm.Value(vpm.TYPE_CONTENT)
by_hand.chosen_by_hand = True
check("a Kind somebody picked is never written over",
      vpm.kind_proposal_apply({JINGLE: by_hand}, [DEAD],
                              [JINGLE]) == []
      and by_hand.get() == vpm.TYPE_CONTENT)
# An intro exists once. Where somebody has already marked one, a second
# proposal would silently push the first back to content.
mine = vpm.Value(vpm.TYPE_INTRO)
mine.chosen_by_hand = True
already = {D + "/Other.mov": mine, JINGLE: vpm.Value(vpm.TYPE_CONTENT)}
vpm.kind_proposal_apply(already, [DEAD], [JINGLE])
check("no second intro where one already stands, and no other guess",
      mine.get() == vpm.TYPE_INTRO
      and already[JINGLE].get() == vpm.TYPE_CONTENT,
      "%s / %s" % (mine.get(), already[JINGLE].get()))
check("without a measurement nothing moves in either direction",
      vpm.kind_proposal_apply(kinds, None, [JINGLE]) == []
      and kinds[JINGLE].get() == vpm.TYPE_CONTENT)


#------------------------------------------------------- 4. The rule itself

print("\n4. The rule, on bare numbers")
lengths = {"a": 4000.0, "b": 4000.0, "c": 4000.0, "jingle": 18.0}
check("a jingle among long cameras is far shorter",
      vpm.files_far_shorter(["jingle"], lengths) == ["jingle"])
check("a file as long as the rest is not",
      vpm.files_far_shorter(["a"], lengths) == [])
limit = 4000.0 * vpm.INTRO_SHORT_ENOUGH
lengths["edge"] = limit
check("the limit itself still counts as far shorter",
      vpm.files_far_shorter(["edge"], lengths) == ["edge"],
      "%.0f s against a middle of %.0f" % (limit, 4000.0))
lengths["edge"] = limit + 1.0
check("and a second above it does not",
      vpm.files_far_shorter(["edge"], lengths) == [])
lengths = {"one": 60.0, "two": 3.0, "three": 2.0}
check("the shortest comes first, because only one can be the intro",
      vpm.files_far_shorter(["two", "three"], lengths) == ["three", "two"],
      str(vpm.files_far_shorter(["two", "three"], lengths)))

source = open(SCRIPT, encoding="utf-8").read()
check("the window goes through the proposal and not past it",
      "kind_proposal_say(state.get(\"clip_kinds\")" in source
      and source.count("def kind_proposal_apply") == 1)

print("\n%s" % ("All good." if not error
                else "FAIL: %s" % ", ".join(error)))
sys.exit(1 if error else 0)
