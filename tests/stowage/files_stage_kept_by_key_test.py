# -*- coding: utf-8 -*-
"""A stage's result comes back only under the inputs it was worked from.

The sections: the key -- same inputs one key, any changed input another,
one file spelled two ways one key; the store -- a hit, what an entry
records, a stale or broken entry read as none, a write that never shows
half an entry; the sweep -- by age and by count, a read dating an entry.
Everything lies in a cache folder of the test's own.
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
import the_program
SCRIPT = the_program.SCRIPT
import json, shutil, tempfile, time
vpm = the_program.load()

began = time.time()
done = 0
bad = []


def check(name, ok, extra=""):
    global done
    done += 1
    print("  %-58s %s %s" % (name, "ok" if ok else "FAIL", extra))
    if not ok:
        bad.append("%s [%s]" % (name, extra or "no numbers"))


WORK = tempfile.mkdtemp(prefix="vpm_stage_")
CACHE = os.path.join(WORK, "cache")
os.environ["VPM_CACHE"] = CACHE
MEDIA = os.path.join(WORK, "media")
os.makedirs(MEDIA)
CAM = os.path.join(MEDIA, "Guest_cam.mov")
MIC = os.path.join(MEDIA, "Presenter_mic.wav")
for p in (CAM, MIC):
    with open(p, "wb") as f:
        f.write(b"x" * 1000)
    os.utime(p, (1700000000, 1700000000))
ASSIGN = {"Guest": CAM, "Presenter": MIC}
KNOBS = {"hold_s": 1.5, "min_edit_s": 2.0}


def key(files=(CAM, MIC), assign=ASSIGN, in_out=(0.0, 60.0), knobs=KNOBS,
        stage="axis"):
    """The key of one stage over the fixed material, one input moved."""
    return vpm.stage_key(stage, files=files, assignment=assign,
                         in_out=in_out, settings=knobs)


try:
    print("1. The key")
    first = key()
    check("a stage over its inputs has a key",
          isinstance(first, str) and first.startswith("axis_"),
          "key %r" % (first,))

    vpm.stage_put(first, {"CAM": 0.0, "MIC": 1.25})
    again = key()
    check("the same inputs worked out again find the kept result",
          vpm.stage_get(again) == {"CAM": 0.0, "MIC": 1.25},
          "key %r then %r, read %r" % (first, again, vpm.stage_get(again)))

    os.utime(CAM, (1700000100, 1700000100))
    touched = key()
    check("a file with another time is another key, and a miss",
          touched != first and vpm.stage_get(touched) is None,
          "key %r against %r, read %r"
          % (touched, first, vpm.stage_get(touched)))
    os.utime(CAM, (1700000000, 1700000000))

    with open(MIC, "ab") as f:
        f.write(b"y")
    os.utime(MIC, (1700000000, 1700000000))
    grown = key()
    check("a file of another size is another key, and a miss",
          grown != first and vpm.stage_get(grown) is None,
          "key %r against %r, read %r" % (grown, first, vpm.stage_get(grown)))
    with open(MIC, "wb") as f:
        f.write(b"x" * 1000)
    os.utime(MIC, (1700000000, 1700000000))
    check("the file put back as it was finds the kept result again",
          key() == first, "key %r against %r" % (key(), first))

    swapped = key(assign={"Guest": MIC, "Presenter": CAM})
    check("another assignment is another key",
          swapped != first, "both %r" % (first,))
    moved = key(in_out=(0.0, 59.0))
    check("another In/Out is another key", moved != first,
          "both %r" % (first,))
    turned = key(knobs={"hold_s": 1.6, "min_edit_s": 2.0})
    check("another setting is another key", turned != first,
          "both %r" % (first,))
    other = key(stage="speakers")
    check("another stage over the same inputs is another key",
          other != first and vpm.stage_get(other) is None,
          "key %r against %r" % (other, first))
    fewer = key(files=(CAM,))
    check("a file left out is another key", fewer != first,
          "both %r" % (first,))

    roundabout = os.path.join(MEDIA, "..", "media", ".", "Guest_cam.mov")
    spelled = key(files=(roundabout, MIC))
    check("one file spelled with dots in its path is one key",
          spelled == first, "key %r against %r for %s"
          % (spelled, first, os.path.relpath(roundabout, WORK)))
    # Windows compares paths without case; normcase says so there.
    plain = os.path.normcase
    os.path.normcase = lambda p: plain(p).lower()
    try:
        upper = key(files=(CAM.replace("Guest_cam", "GUEST_CAM"), MIC))
        lower = key(files=(CAM, MIC))
    finally:
        os.path.normcase = plain
    check("where paths fold case, two spellings of one file are one key",
          upper == lower, "key %r against %r" % (upper, lower))

    check("an input json cannot hold gives no key, not a wrong one",
          key(knobs={"hold_s": object()}) is None,
          "key %r" % (key(knobs={"hold_s": object()}),))
    check("a stage name that could leave the store folder gives no key",
          key(stage="../axis") is None, "key %r" % (key(stage="../axis"),))

    print("2. The store")
    path = os.path.join(CACHE, vpm.FROZEN_NAME, "stages", first + ".json")
    check("the entry lies in the program's cache and nowhere else",
          os.path.isfile(path) and len(os.listdir(MEDIA)) == 2,
          "entry there %s, media folder holds %r"
          % (os.path.isfile(path), sorted(os.listdir(MEDIA))))
    with open(path, "rb") as f:
        entry = json.loads(f.read().decode("utf-8"))
    check("an entry records the program's version and the stage's shape",
          entry.get("version") == vpm.VERSION and entry.get("schema") == 1,
          "version %r against %r, schema %r"
          % (entry.get("version"), vpm.VERSION, entry.get("schema")))
    check("a stage of another shape reads the entry as none",
          vpm.stage_get(first, schema=2) is None,
          "read %r" % (vpm.stage_get(first, schema=2),))

    good = open(path, "rb").read()

    def read():
        """The entry as the program reads it, or what it raised."""
        try:
            return vpm.stage_get(first)
        except Exception as e:
            return "raised %s: %s" % (type(e).__name__,
                                      str(e).replace(path, "<entry>"))

    def stored(data):
        """Put *data* where the entry lies and read it as the program does."""
        with open(path, "wb") as f:
            f.write(data)
        return read()

    older = dict(entry, version="0.0.1")
    got = stored(json.dumps(older).encode("utf-8"))
    check("an entry another version wrote is read as none",
          got is None, "read %r" % (got,))
    got = stored(good[:len(good) // 2])
    check("a half-written entry is read as none, not raised",
          got is None, "read %r" % (got,))
    got = stored(b"[1, 2, 3]")
    check("an entry that is no dictionary is read as none, not raised",
          got is None, "read %r" % (got,))
    got = stored(b"\xff\xfe\x00")
    check("an entry that is no text is read as none, not raised",
          got is None, "read %r" % (got,))
    got = stored(json.dumps(dict(entry, key=other)).encode("utf-8"))
    check("an entry kept for another key is read as none",
          got is None, "read %r" % (got,))
    os.unlink(path)
    os.makedirs(path)
    got = read()
    check("a folder where the entry should lie is read as none",
          got is None, "read %r" % (got,))
    os.rmdir(path)
    stored(good)

    plain_replace = os.replace

    def refused(a, b):
        raise OSError("refused for the test")
    os.replace = refused
    try:
        went = vpm.stage_put(moved, {"CAM": 9.0})
    finally:
        os.replace = plain_replace
    beside = sorted(n for n in os.listdir(os.path.dirname(path))
                    if not n.endswith(".json"))
    check("a write stopped before its move leaves no entry behind",
          not went and vpm.stage_get(moved) is None,
          "put answered %r, read %r" % (went, vpm.stage_get(moved)))
    check("a write stopped before its move leaves no half file beside",
          beside == [], "beside the entries: %r" % (beside,))
    went = vpm.stage_put(moved, {"CAM": 9.0})
    check("the same write let through is read back whole",
          went and vpm.stage_get(moved) == {"CAM": 9.0},
          "put answered %r, read %r" % (went, vpm.stage_get(moved)))

    print("3. The sweep")
    os.utime(path, (time.time() - 40 * 86400,) * 2)
    fresh = os.path.join(os.path.dirname(path), moved + ".json")
    vpm.clean_kept_stores(30)
    check("an entry unused for longer than the stores keep is swept",
          not os.path.exists(path) and os.path.isfile(fresh),
          "old one still there %s, fresh one there %s"
          % (os.path.exists(path), os.path.isfile(fresh)))

    os.utime(fresh, (time.time() - 20 * 86400,) * 2)
    vpm.stage_get(moved)
    age = (time.time() - os.path.getmtime(fresh)) / 86400
    check("a read dates the entry to its use, not to its writing",
          age < 1, "entry %.1f days old after the read" % age)

    stowage = vpm.stowage
    limit = stowage.STAGE_KEEP_COUNT
    stowage.STAGE_KEEP_COUNT = 3
    try:
        keys = [key(in_out=(0.0, float(n))) for n in range(5)]
        for n, k in enumerate(keys):
            vpm.stage_put(k, {"n": n})
            os.utime(os.path.join(os.path.dirname(path), k + ".json"),
                     (1700000000 + n, 1700000000 + n))
        vpm.stage_put(first, {"n": 9})
    finally:
        stowage.STAGE_KEEP_COUNT = limit
    # Three kept: the entry just written, the one read above, and the
    # last of the five, dated after the other four.
    left = [vpm.stage_get(k) for k in keys]
    check("beyond the count the entries used longest ago go first",
          left == [None, None, None, None, {"n": 4}]
          and vpm.stage_get(first) == {"n": 9}
          and vpm.stage_get(moved) == {"CAM": 9.0},
          "left %r, newest %r, read before %r"
          % (left, vpm.stage_get(first), vpm.stage_get(moved)))
except Exception as e:
    check("the test ran through", False,
          "stopped on %s: %s" % (type(e).__name__, e))
finally:
    shutil.rmtree(WORK, ignore_errors=True)

print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
