# -*- coding: utf-8 -*-
"""Two cameras whose files share a name stay two cameras.

The map from file name to camera overwrote silently, and two cameras
writing C0001.MP4 in two folders landed on one media pool item, so the
second camera showed the first one's picture.
"""
import os
import the_program
HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = the_program.SCRIPT
import io, sys, tempfile, time
import contextlib
began = time.time()
vpm = the_program.load()
WORK = tempfile.mkdtemp(prefix="twocameras_")
done = 0
bad = []


def check(name, ok, extra=""):
    global done
    done += 1
    print("  %-58s %s %s" % (name, "ok" if ok else "FAIL", extra))
    if not ok:
        bad.append("%s [%s]" % (name, extra or "no numbers"))


def spoken(call, *a, **k):
    """Run something and hand back what it printed."""
    said = io.StringIO()
    with contextlib.redirect_stdout(said):
        out = call(*a, **k)
    return out, said.getvalue()


print("The camera is told apart by more than the file name")


def cam(track, file_path):
    return {"track": track, "file": file_path, "source": file_path}


out, said = spoken(vpm.cameras_by_file_name,
                   [cam("Wide", "/a/C0001.MP4"), cam("Guest", "/b/G.MP4")])
check("two different names, nothing said", len(out) == 2 and not said,
      said.strip()[:50])
out, said = spoken(vpm.cameras_by_file_name,
                   [cam("Wide", "/a/C0001.MP4"),
                    cam("Guest", "/b/C0001.MP4")])
check("same name on both, and it is said", "C0001.MP4" in said
      and "Wide" in said and "Guest" in said, repr(said[:60]))


print("\nThe clip is found again by its path, not by its name")


class Clip(object):
    def __init__(self, name, where=None):
        self.name, self.where = name, where

    def GetName(self):
        return self.name

    def GetClipProperty(self, what):
        if what == "File Path":
            return self.where
        return ""


class Pool(object):
    def __init__(self, clips):
        self.clips = clips

    def ImportMedia(self, paths):
        return list(paths)

    def GetRootFolder(self):
        return self

    def GetClipList(self):
        return self.clips


here = os.path.join(WORK, "one")
there = os.path.join(WORK, "two")
os.makedirs(here); os.makedirs(there)
first = os.path.join(here, "C0001.MP4")
second = os.path.join(there, "C0001.MP4")
for f in (first, second):
    open(f, "w").write("x")
pool = Pool([Clip("C0001.MP4", first), Clip("C0001.MP4", second)])
out, said = spoken(vpm.import_media, pool, [first, second])
check("each path gets its own clip",
      out[first] is not out[second],
      "both on %s" % out[first].where)
check("and the right one", out[first].where == first
      and out[second].where == second,
      "%s and %s, wanted %s and %s -- under %s"
      % (str(out[first].where).replace(WORK + os.sep, ""),
         str(out[second].where).replace(WORK + os.sep, ""),
         first.replace(WORK + os.sep, ""),
         second.replace(WORK + os.sep, ""), WORK))

# The same again from a Resolve that reports no path at all. Guessing
# would put one camera's picture on two tracks, so the run stops.
blind = Pool([Clip("C0001.MP4"), Clip("C0001.MP4")])
try:
    with contextlib.redirect_stdout(io.StringIO()):
        vpm.import_media(blind, [first, second])
    check("no path reported: the run stops", False, "it carried on")
except RuntimeError as e:
    check("no path reported: the run stops", "C0001.MP4" in str(e),
          str(e)[:60])

# One path twice in the list is not a collision.
single = Pool([Clip("C0001.MP4", first)])
try:
    with contextlib.redirect_stdout(io.StringIO()):
        out = vpm.import_media(single, [first, first])
    check("the same path twice is no collision", len(out) == 1,
          "%d clips back for one path named twice, wanted 1" % len(out))
except RuntimeError as e:
    check("the same path twice is no collision", False, str(e)[:60])

print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
