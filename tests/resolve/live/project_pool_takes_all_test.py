# -*- coding: utf-8 -*-
"""Every file the run hands over is in the media pool and found again.

Against a DaVinci Resolve that is really running. In order -- every file
handed over becomes a clip and none is quietly missing, each clip carries
the path of the file it came from, two files of the same name in two
folders stay two clips, and a file that is not there stops the run instead
of leaving a gap nobody notices.

The material is the shared interview fixture, read and never written; the
two files of one name are copies in a temporary folder of the test's own.

A step that throws is a failed judgement and not a traceback, so the
closing count is reached whatever happens.
"""
import os
import shutil
import sys
import tempfile
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import resolve_ground as ground_of

began = time.time()
done = 0
bad = []


def check(name, ok, extra=""):
    global done
    done += 1
    print("  %-58s %s %s" % (name, "ok" if ok else "FAIL", extra))
    if not ok:
        bad.append("%s [%s]" % (name, extra or "no numbers"))


def where(clip):
    """The path Resolve reports for a clip, comparable with a file name."""
    try:
        told = clip.GetClipProperty("File Path") or ""
    except Exception:
        told = ""
    return os.path.normcase(os.path.abspath(told)) if told else ""


vpm = ground_of.program()
resolve = ground_of.a_resolve(vpm)
print("Resolve: %s %s" % (resolve.GetProductName(), resolve.GetVersionString()))

folder = ground_of.fixture("interview")
if not os.path.isdir(folder):
    ground_of.leave_out("no interview fixture at %s -- run 'cd tests && "
                        "bash fixtures.sh' to build it" % folder)
camera = ground_of.cameras_of(folder)
if len(camera) < 2:
    ground_of.leave_out("the interview fixture holds %d camera files, at "
                        "least 2 are needed -- run 'cd tests && bash "
                        "fixtures.sh force'" % len(camera))

work = tempfile.mkdtemp(prefix="vpm_pool_")
ground = ground_of.OwnProject(vpm, resolve, "pool")
try:
    p = ground.open()
    mp = p.GetMediaPool()
    root = mp.GetRootFolder()

    print("\n1. Every file handed over is in the pool")
    got = vpm.import_media(mp, camera)
    check("a clip came back for every file handed over",
          len(got) == len(camera),
          "%d clips for %d files" % (len(got), len(camera)))
    # Read back rather than believed: Resolve reports success for things
    # it did not do, so what the pool holds is the only evidence.
    arrived, seen, waited = ground_of.standstill(
        lambda: len(mp.GetRootFolder().GetClipList() or []), len(camera))
    check("the media pool itself holds one clip per file",
          arrived, "%d clips in the pool after %.1f s, %d files went in"
          % (seen, waited, len(camera)))
    told = sorted(x for x in (where(c) for c in
                              (root.GetClipList() or [])) if x)
    wanted = sorted(os.path.normcase(os.path.abspath(f)) for f in camera)
    check("every clip carries the path of the file it came from",
          told == wanted,
          "pool reports %s, files handed over %s"
          % ([os.path.basename(x) for x in told],
             [os.path.basename(x) for x in wanted]))
    check("no two files were matched to the same clip",
          len(set(id(c) for c in got.values())) == len(camera),
          "%d distinct clips for %d files"
          % (len(set(id(c) for c in got.values())), len(camera)))
    check("every file handed over got a clip of its own back",
          sorted(got) == sorted(camera),
          "matched %s" % sorted(os.path.basename(f) for f in got))

    print("\n2. Two files of one name in two folders stay two clips")
    # Two cameras writing C0001.MP4 in two folders. Looked up by name both
    # land on one pool item, and the second camera then gets the first
    # one's picture without a word.
    twin = []
    for i, source in enumerate(camera[:2]):
        folder_of = os.path.join(work, "cam%d" % i)
        os.makedirs(folder_of)
        copy = os.path.join(folder_of, "C0001.MP4.mov")
        shutil.copy(source, copy)
        twin.append(copy)
    pair = vpm.import_media(mp, twin)
    check("both files of the same name came back",
          len(pair) == 2, "%d clips for 2 files of one name" % len(pair))
    check("the two are two clips, not one taken twice",
          len(set(id(c) for c in pair.values())) == 2,
          "%d distinct clips for %s"
          % (len(set(id(c) for c in pair.values())),
             [os.path.basename(os.path.dirname(t)) + "/C0001.MP4.mov"
              for t in twin]))
    check("each of the two is matched to the clip carrying its own path",
          all(where(pair[t]) == os.path.normcase(os.path.abspath(t))
              for t in twin),
          "matched %s"
          % [(os.path.basename(os.path.dirname(t)), where(pair[t]))
             for t in twin])

    print("\n3. A file that is not there stops the run")
    absent = os.path.join(work, "was-never-written.mov")
    complaint = ""
    try:
        vpm.import_media(mp, [absent])
    except RuntimeError as e:
        complaint = str(e)
    check("a file that does not exist is refused, not passed over",
          bool(complaint), "import_media said %r" % complaint[:60])
    # Which refusal matters. Handed on to Resolve, a file that is not
    # there comes back as "not found again after import", which reads
    # like a fault in Resolve and sends the reader the wrong way.
    check("and it is refused for not being there, not for being lost",
          complaint.startswith(vpm.T('These files do not exist:\n  ')),
          "said %r" % complaint.replace("\n", " ")[:80])
    check("and the refusal names the file that is missing",
          os.path.basename(absent) in complaint,
          "%r is not in %r" % (os.path.basename(absent),
                               complaint.replace("\n", " ")[:80]))
except Exception as e:
    import traceback
    traceback.print_exc()
    check("the run reached the end without an exception", False,
          "%s: %s" % (type(e).__name__, str(e).replace("\n", " ")[:120]))
finally:
    left_over = ground.close()
    shutil.rmtree(work, ignore_errors=True)

check("the project the test made is gone again", not left_over,
      left_over or "%r no longer in the project list" % ground.name)

print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
