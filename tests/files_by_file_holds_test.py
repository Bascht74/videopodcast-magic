# -*- coding: utf-8 -*-
"""The dictionary of files finds one file under any of its names.

path_key says what shape a path takes; ByFile is the only place that
has to know. So this holds the type itself: that it covers every way a
dictionary can be read or written by key, that a second spelling of one
file reaches the first entry, and that what comes back out is the name
on the disc and not the shape.

Measured twice -- once with normcase as it is on this machine, where it
changes nothing, and once with one that folds the case. Without the
second half no Mac can see the fault this type exists for.

The last section names the dictionaries that hold files. That list may
grow and must not shrink: a dictionary that leaves it stopped being
keyed by a file, and that is said out loud rather than dropped.

It is the section that would have caught the one fault this rebuild
had: a plain dictionary standing beside one of these, filled from its
keys and read back under abspath. Keys handed out of a ByFile carry
the spelling they arrived in, so whatever they are then stored in or
compared against has to settle the shape as well.
"""
import os
import the_program
HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = the_program.SCRIPT
import ast, json, sys, time

# Before the program is loaded: path_key reads os.path.normcase at every
# call, so the fold can be switched on and off around it.
FOLD = [False]
_real_normcase = os.path.normcase


FOLDS_HERE = _real_normcase("A") != "A"


def normcase_that_folds(s):
    return s.lower() if FOLD[0] else _real_normcase(s)


os.path.normcase = normcase_that_folds
import posixpath, ntpath
posixpath.normcase = normcase_that_folds

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


A = "/tmp/vpm-holds/Guest_0001.wav"
SPELT = ["/tmp/vpm-holds/./Guest_0001.wav",      # a needless step
         "/tmp/vpm-holds/../vpm-holds/Guest_0001.wav"]
CASED = "/tmp/vpm-holds/GUEST_0001.WAV"          # only Windows calls this one
B = "/tmp/vpm-holds/Presenter_0001.wav"

#--------------------------------------- 1. Every way in and out is covered
print("\n1. Every way a dictionary is read or written by key")
BY_KEY = {"__getitem__", "get", "__contains__", "__setitem__", "__delitem__",
          "pop", "popitem", "setdefault", "update", "clear", "__ior__",
          "copy", "__init__"}
missing = sorted(n for n in BY_KEY if n not in vars(vpm.ByFile))
check("ByFile carries its own of every one of them", not missing,
      "missing: %s" % missing)
# And the other way round: dict itself grew a way of reading or writing
# by key, and ByFile does not know it yet. The whole of its surface is
# written down, so anything new here is a name to look at.
DICT_SURFACE = frozenset(dir(dict))
FROZEN = frozenset("""
__class__ __class_getitem__ __contains__ __delattr__ __delitem__ __dir__
__doc__ __eq__ __format__ __ge__ __getattribute__ __getitem__ __getstate__
__gt__ __hash__ __init__ __init_subclass__ __ior__ __iter__ __le__ __len__
__lt__ __ne__ __new__ __or__ __reduce__ __reduce_ex__ __repr__ __reversed__
__ror__ __setattr__ __setitem__ __sizeof__ __str__ __subclasshook__ clear
copy fromkeys get items keys pop popitem setdefault update values
""".split())
check("dict has grown no way of its own since this was written",
      DICT_SURFACE <= FROZEN,
      "new on dict: %s" % sorted(DICT_SURFACE - FROZEN))

#------------------------------------------- 2. One file, any of its names
for folding in (False, True):
    FOLD[0] = folding
    print("\n2%s. One file under any of its names -- normcase %s"
          % ("b" if folding else "a",
             "folds the case" if folding else "as on this machine"))
    d = vpm.ByFile()
    d[A] = 1
    missed = [o for o in SPELT if not (d.get(o) == 1 and o in d)]
    check("one file is found under every spelling of its name",
          not missed, "%d of %d found, missed: %s"
          % (len(SPELT) - len(missed), len(SPELT), missed))
    hits = folding or FOLDS_HERE
    check("the upper-cased name counts as one file only where the "
          "machine folds it",
          (d.get(CASED) == 1) if hits else (d.get(CASED) is None),
          "folding %s, this machine folds %s, got %r"
          % (folding, FOLDS_HERE, d.get(CASED)))
    d[SPELT[0]] = 2
    check("a second spelling writes into the entry, not beside it",
          len(d) == 1 and d[A] == 2, "len %d" % len(d))
    check("and the key that comes back out is the name on the disc",
          list(d) == [A], repr(list(d)))
    d[B] = 3
    check("the project file gets the names on the disc",
          json.loads(json.dumps(d)) == {A: 2, B: 3}, json.dumps(d))
    old = vpm.ByFile({A: 7})
    check("an older project opens: update puts its keys into shape",
          old.get(SPELT[0]) == 7, "%r under %s" % (old.get(SPELT[0]),
                                                   SPELT[0]))
    e = d.copy()
    check("a copy is one of these too and finds the same",
          isinstance(e, vpm.ByFile) and e.get(SPELT[0]) == 2,
          "%s, %r" % (type(e).__name__, e.get(SPELT[0])))
    d.pop(SPELT[1], None)
    check("pop under a third spelling takes the entry out", len(d) == 1,
          "len %d, left: %r" % (len(d), list(d)))
    f = vpm.ByFile()
    f[A] = []
    f.setdefault(SPELT[0], ["beside it"]).append("x")
    check("setdefault under a second spelling finds the list that is there",
          len(f) == 1 and f[SPELT[1]] == ["x"],
          "len %d, %r" % (len(f), f.get(SPELT[1])))
    tupled = vpm.ByFile({(A, "envelope"): 5})
    check("a key that is not a file passes through",
          tupled.get((A, "envelope")) == 5,
          repr(tupled.get((A, "envelope"))))

    s = vpm.FileSet([A])
    check("the set does the same", all(x in s for x in SPELT),
          "%d of %d spellings found" % (sum(1 for x in SPELT if x in s),
                                        len(SPELT)))
    s.discard(SPELT[0])
    check("and takes one out under any of its names", A not in s,
          "%d left: %r" % (len(s), sorted(s)))

#---------------------------------- 3. The dictionaries that hold files
FOLD[0] = False
print("\n3. The dictionaries that hold files are of that kind")
HOLD_FILES = [
    ("gui", "blocks_of"), ("gui", "recording_of"), ("gui", "join_to"),
    ("gui", "channel_choice"), ("gui", "channel_node"),
    ("gui", "video_kind_again"), ("gui", "split_files"),
    ("gui", "lines_node"), ("gui", "prework_node"),
    ("gui", "prework_pending"), ("gui", "tree_open"),
    ("gui", "clip_kind_values"), ("gui", "audio_use_values"),
    ("gui", "suggestions"), ("gui", "piece_label"),
    ("gui", "own_audio_names"),
    ("distribute_tracks_to_cameras", "after_camera"),
    ("distribute_tracks_to_cameras", "camera_mix"),
    ("speakers_all_from_project", "out"),
    ("distribute_tracks_to_cameras", "track_names"),
    ("distribute_tracks_to_cameras", "offsets"),
    ("distribute_tracks_to_cameras", "lengths"),
    ("assignment_rows", "own"), ("by_recording", "after_file_path"),
    ("import_media", "after_path"),
    ("one_separation_on_axis", "where"),
    ("plan_from_camera_audio", "named"),
    ("voice_names_by_source", "out"),
]
HOLD_FILES_SET = [("gui", "no_join"),
                  ("group_recording_parts", "apart")]
# Every piece of the program: the window is one of its own, and half
# the dictionaries this section is about are built inside it.
where = {}
for _piece, _body in the_program.pieces():
    for node in ast.walk(ast.parse(_body)):
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        for st in ast.walk(node):
            if not isinstance(st, ast.Assign) or len(st.targets) != 1:
                continue
            # a, b = X(), Y() counts too: several of them are declared
            # in one line, and a check that missed those would be green
            # on the very lines it is about.
            left, right = st.targets[0], st.value
            pairs = (list(zip(left.elts, right.elts))
                     if isinstance(left, ast.Tuple)
                     and isinstance(right, ast.Tuple)
                     else [(left, right)])
            for name, value in pairs:
                if isinstance(name, ast.Name):
                    where.setdefault((node.name, name.id), []).append(value)


def made_by(pair, wanted):
    for value in where.get(pair, ()):
        if (isinstance(value, ast.Call) and isinstance(value.func, ast.Name)
                and value.func.id == wanted):
            return True
    return False


off = [p for p in HOLD_FILES if not made_by(p, "ByFile")]
check("every dictionary that holds files is built as a ByFile",
      not off, "%d of %d, not: %s"
      % (len(HOLD_FILES) - len(off), len(HOLD_FILES), off[:4]))
off = [p for p in HOLD_FILES_SET if not made_by(p, "FileSet")]
check("and every set of files as a FileSet", not off,
      "%d of %d, not: %s"
      % (len(HOLD_FILES_SET) - len(off), len(HOLD_FILES_SET), off[:4]))

print("\n%d checks in %.2f s" % (done, time.time() - began))
if bad:
    print("FAIL: %s" % "; ".join(bad))
    sys.exit(1)
print("ALL OK")
