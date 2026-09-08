# -*- coding: utf-8 -*-
"""The mix is found by its own name, not by a word inside another one.

Both places that look for the overall mix on the way into Resolve asked
whether "full" stood somewhere in the lower-cased name. The keys arrive
speakers first and the mix last, so a speaker called Fullerton won every
time rather than now and then.

The sections: the stored file out of the handover, the order it is
listed in, a speaker who only looks like the mix, the audio track of a
camera, and which camera goes on track one.
"""
import os
import the_program
HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = the_program.SCRIPT
import sys, tempfile, time
began = time.time()
vpm = the_program.load()
WORK = tempfile.mkdtemp(prefix="mixbyname_")
done = 0
bad = []


def check(name, ok, extra=""):
    global done
    done += 1
    print("  %-58s %s %s" % (name, "ok" if ok else "FAIL", extra))
    if not ok:
        bad.append("%s [%s]" % (name, extra or "no numbers"))


def laid(name):
    """Put an empty file of that name in the work folder and return it."""
    where = os.path.join(WORK, name + ".wav")
    open(where, "wb").close()
    return where


MIX = vpm.MIX_TRACK_NAME
DECOY = "Fullerton"
mix_file = laid(MIX)
decoy_file = laid(DECOY)

print("\n1. The stored file out of the handover")
# The order a real run writes: every speaker first, the mix appended
# last (pipeline builds single_files that way), so the decoy is met
# first and only the name decides.
found, said = vpm.mix_file_from_handover(
    {"audio_files": {DECOY: decoy_file, MIX: mix_file}})
check("a speaker met before the mix does not take its place",
      found == mix_file,
      "%r against %r" % (os.path.basename(found or ""), MIX + ".wav"))
check("and the line names the file it really took",
      bool(said) and os.path.basename(mix_file) in said,
      "%r against the name of %r"
      % (said, os.path.basename(mix_file)))

print("\n2. The order it is listed in decides nothing")
first, _ = vpm.mix_file_from_handover(
    {"audio_files": {MIX: mix_file, DECOY: decoy_file}})
check("the mix listed first is the same answer as the mix listed last",
      first == mix_file == found,
      "%r and %r, wanted both %r"
      % (os.path.basename(first or ""), os.path.basename(found or ""),
         os.path.basename(mix_file)))

print("\n3. A speaker who only looks like the mix")
alone, _ = vpm.mix_file_from_handover({"audio_files": {DECOY: decoy_file}})
check("a name carrying the mix word inside it is not the mix",
      alone is None,
      "%r, wanted nothing" % (os.path.basename(alone) if alone else None,))

print("\n4. The audio track of a camera")
cam_file = laid("WideCam")
found, said = vpm.mix_file_from_handover(
    {"cameras": [{"camera": "Cam", "file": cam_file,
                  "audio_tracks": [DECOY, MIX]}]})
check("the track number counts to the mix, not to the decoy before it",
      found == cam_file and said.endswith("2"),
      "%r said %r, wanted track 2" % (os.path.basename(found or ""), said))
only_decoy, _ = vpm.mix_file_from_handover(
    {"cameras": [{"camera": "Cam", "file": cam_file,
                  "audio_tracks": [DECOY]}]})
check("a camera carrying only the decoy offers no mix",
      only_decoy is None,
      "%r, wanted nothing" % (os.path.basename(only_decoy)
                              if only_decoy else None,))

print("\n5. Which camera goes on track one")
order = vpm.cameras_in_track_order([
    {"camera": "A", "audio_tracks": [DECOY]},
    {"camera": "B", "audio_tracks": [MIX]},
])
check("the camera whose first track is the mix leads",
      [c["camera"] for c in order] == ["B", "A"],
      "%r, wanted ['B', 'A']" % ([c["camera"] for c in order],))

print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
