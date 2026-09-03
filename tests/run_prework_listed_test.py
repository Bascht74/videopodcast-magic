# -*- coding: utf-8 -*-
"""Header line, prework, window suggestion and axis reuse all hold.

Four computations behind the file list, taken on their own so that no
interface has to be built. A file prework cannot get an answer for
drops out entirely instead of being guessed at, and a measured axis is
reused only where path, time and size match for every file, one
changed file discarding all of it: a partly stale axis is worse than
measuring again. The last section holds the program to these four."""
import os
HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = os.environ.get("VPM_SCRIPT") or os.path.join(
    os.path.dirname(HERE), "videopodcast_magic.py")
import sys, tempfile, shutil, importlib.util, time
began = time.time()
spec = importlib.util.spec_from_file_location(
    "vpm", SCRIPT)
vpm = importlib.util.module_from_spec(spec); sys.modules["vpm"] = vpm
spec.loader.exec_module(vpm)

done = 0
bad = []


def check(name, ok, extra=""):
    global done
    done += 1
    print("  %-58s %s %s" % (name, "ok" if ok else "FAIL", extra))
    if not ok:
        bad.append("%s [%s]" % (name, extra or "no numbers"))


def tasks(rows):
    """A prework list as basename and task, so the line stays readable."""
    return repr([(os.path.basename(p), t) for p, t in rows])

print("1. The header line of the audio group")
got = vpm.recordings_text(3, 3)
check("same count -> only the file count", got == "3 files",
        "%r, wanted '3 files'" % (got,))
got = vpm.recordings_text(2, 5)
check("blocks grouped -> both", got == "2 recordings from 5 files",
        "%r, wanted '2 recordings from 5 files'" % (got,))
got = vpm.recordings_text(1, 1)
check("a single one", got == "1 file", "%r, wanted '1 file'" % (got,))
got = vpm.recordings_text(1, 3)
check("one recording out of several files",
        got == "1 recording from 3 files",
        "%r, wanted '1 recording from 3 files'" % (got,))
got = vpm.recordings_text(0, 0)
check("none at all", got == "0 files", "%r, wanted '0 files'" % (got,))

print("\n2. What prework is still open")
D = tempfile.mkdtemp(prefix="prework_")
A = os.path.join(D, "a.mov"); B = os.path.join(D, "b.mov")
for x in (A, B):
    open(x, "wb").write(b"\0" * 8)
GONE = os.path.join(D, "gone.mov")

never = lambda p: False
always = lambda p: True
want = [(A, "audio"), (A, "envelope"), (B, "envelope")]
r = vpm.pending_prework([A, B], having_audio=[A], has_audio=never,
                        has_env_curve=never)
check("audio only for the one, envelope for both", r == want,
        "%s, wanted %s" % (tasks(r), tasks(want)))
want = [(A, "envelope"), (B, "envelope")]
r = vpm.pending_prework([A, B], having_audio=[A], has_audio=always,
                        has_env_curve=never)
check("audio is already there -> envelopes only", r == want,
        "%s, wanted %s" % (tasks(r), tasks(want)))
want = [(A, "audio")]
r = vpm.pending_prework([A, B], having_audio=[A], has_audio=never,
                        has_env_curve=always)
check("envelopes are already there -> audio only", r == want,
        "%s, wanted %s" % (tasks(r), tasks(want)))
r = vpm.pending_prework([A, B], having_audio=[A], has_audio=always,
                        has_env_curve=always)
check("everything there -> nothing to do", r == [],
        "%s, wanted []" % tasks(r))
want = [(A, "envelope"), (B, "envelope")]
r = vpm.pending_prework([A, GONE, B], having_audio=[], has_audio=never,
                        has_env_curve=never)
check("a file that is gone drops out", r == want,
        "%s, wanted %s (gone.mov was asked for and does not exist)"
        % (tasks(r), tasks(want)))
want = [(B, "audio"), (B, "envelope")]
r = vpm.pending_prework([A, B], having_audio=[A, B],
                        has_audio=lambda p: None if p == A else False,
                        has_env_curve=never)
check("cannot be asked -> left out entirely, envelope too", r == want,
        "%s, wanted %s (has_audio said None for a.mov)"
        % (tasks(r), tasks(want)))
want = [(A, "envelope")]
# Not "no audio was queued" -- that also holds when the file was asked
# about and said no. The probe writes down every file it was asked for.
asked = []
def note_asked(p):
    asked.append(os.path.basename(p))
    return False
r = vpm.pending_prework([A], having_audio=[], has_audio=note_asked,
                        has_env_curve=never)
check("without having_audio, has_audio is not asked",
        r == want and asked == [],
        "%s and has_audio asked for %r, wanted %s and []"
        % (tasks(r), asked, tasks(want)))
r = vpm.pending_prework([])
check("nothing in -> nothing out", r == [], "%s, wanted []" % tasks(r))
# A relative path has to hit the same file as an absolute one
old = os.getcwd(); os.chdir(D)
r = vpm.pending_prework(["a.mov"], having_audio=["a.mov"], has_audio=never,
                        has_env_curve=never)
os.chdir(old)
check("relative path becomes absolute", r and r[0][0] == os.path.realpath(A)
        or r and os.path.samefile(r[0][0], A),
        "%r, wanted the same file as %r" % (r[:1], A))
shutil.rmtree(D, ignore_errors=True)

print("\n3. In point and Out point from what the cameras offer")
f = vpm.window_suggestion
want_in = vpm.timecode_string(61200.0, 30.0)
want_out = vpm.timecode_string(61800.0, 30.0)
from_s, until, absolute = f([(61200.0, 600.0), (61260.0, 300.0)], 30.0)
check("absolute recognised", absolute is True,
        "absolute %r, wanted True (from %r until %r)"
        % (absolute, from_s, until))
check("earliest start", from_s == want_in,
        "%r, wanted %r (starts 61200 s and 61260 s)" % (from_s, want_in))
check("latest end", until == want_out,
        "%r, wanted %r (61200+600 s against 61260+300 s)"
        % (until, want_out))
want_in = vpm.timecode_string(61260.0, 30.0)
from_s, until, absolute = f([(None, 600.0), (61260.0, 300.0)], 30.0)
check("one without a clock time does not count",
        from_s == want_in and absolute,
        "%r and absolute %r, wanted %r and True"
        % (from_s, absolute, want_in))
from_s, until, absolute = f([(None, 600.0), (None, 900.0)], 30.0)
check("no clock time at all -> relative", absolute is False,
        "absolute %r, wanted False (from %r until %r)"
        % (absolute, from_s, until))
check("from zero", from_s == "+0:00", "%r, wanted '+0:00'" % (from_s,))
check("up to the longest", until.startswith("+0:15"),
        "%r, wanted a start of '+0:15' (the longer of 600 s and 900 s)"
        % (until,))
from_s, until, absolute = f([(None, 0.0)], 30.0)
check("length zero -> no suggestion at all",
        (from_s, until, absolute) == ("", "", False),
        "%r, wanted ('', '', False)" % ((from_s, until, absolute),))
from_s, until, absolute = f([], 30.0)
check("nothing in -> no suggestion at all", from_s == "" and until == "",
        "from %r until %r, wanted '' and ''" % (from_s, until))
want_in = vpm.timecode_string(61200.0, 30.0)
from_s, until, absolute = f([(61200.0, None)], 30.0)
check("duration unknown -> end equals start",
        from_s == until == want_in,
        "%r / %r, wanted both %r" % (from_s, until, want_in))

print("\n4. Does an axis measured earlier still apply?")
D2 = tempfile.mkdtemp(prefix="axisvalid_")
X = os.path.join(D2, "x.mov"); Y = os.path.join(D2, "y.mov")
for f_ in (X, Y):
    open(f_, "wb").write(b"\0" * 100)
def entry(file_path, start, mtime=None, size=None):
    k = vpm.file_fingerprint(file_path)
    return {"path": k[0], "mtime": mtime if mtime is not None else k[1],
            "size": size if size is not None else k[2],
            "start_s": start}

fp = vpm.file_fingerprint(X)
# The time is asked by the other route, so a fingerprint that fills the
# middle field with a constant does not pass here.
want_mtime = int(os.path.getmtime(X))
check("fingerprint is path, time, size",
        fp[0] == os.path.abspath(X)
        and fp[1] == want_mtime
        and fp[2] == 100,
        "%r, wanted path %r, time %d and size 100"
        % (fp, os.path.abspath(X), want_mtime))
MISSING = os.path.join(D2, "gone.mov")
fp_gone = vpm.file_fingerprint(MISSING)
check("missing file -> None", fp_gone is None,
        "%r, wanted None for a file that does not exist" % (fp_gone,))

D_OK = {"timeline": [entry(X, 0.0), entry(Y, 5.0)],
        "timeline_absolute": True}
r = vpm.axis_still_valid(D_OK, [X, Y])
check("unchanged -> applies", r is not None and len(r["axis"]) == 2,
        "%r, wanted an axis over 2 files" % (r,))
# Looked up by path_key, the one shape a path takes when two are
# compared. On a Mac that is the absolute path; on Windows it is that
# with the case and the separator settled as well, and the axis a
# measurement hands back is keyed the same way.
axis = (r or {}).get("axis") or {}
check("the values come along", axis.get(vpm.path_key(Y)) == 5.0,
        "%r for y.mov out of %r, wanted 5.0"
        % (axis.get(vpm.path_key(Y)), sorted(axis)))
flag = (r or {}).get("absolute")
check("absolute is carried over", flag is True,
        "%r, wanted True (timeline_absolute was stored as True)" % (flag,))
weak = (r or {}).get("weak")
check("weak is empty", weak == [], "%r, wanted []" % (weak,))

D_OLD = {"timeline": [entry(X, 0.0), entry(Y, 5.0, mtime=1)]}
r_old = vpm.axis_still_valid(D_OLD, [X, Y])
check("one file changed -> everything discarded", r_old is None,
        "%r, wanted None (y.mov stored with mtime 1, on disk %r)"
        % (r_old, vpm.file_fingerprint(Y)[1]))
D_SIZE = {"timeline": [entry(X, 0.0, size=99), entry(Y, 5.0)]}
r_size = vpm.axis_still_valid(D_SIZE, [X, Y])
check("different size -> discarded", r_size is None,
        "%r, wanted None (x.mov stored with size 99, on disk 100)"
        % (r_size,))
r_short = vpm.axis_still_valid({"timeline": [entry(X, 0.0)]}, [X, Y])
check("a file not in it at all -> discarded", r_short is None,
        "%r, wanted None (2 files asked for, only x.mov stored)"
        % (r_short,))
r_nofiles = vpm.axis_still_valid(D_OK, [])
check("no files asked -> None", r_nofiles is None,
        "%r, wanted None (2 files stored, 0 asked for)" % (r_nofiles,))
r_nodata = vpm.axis_still_valid({}, [X])
check("empty data -> None", r_nodata is None,
        "%r, wanted None (no timeline stored, 1 file asked for)"
        % (r_nodata,))
r_nil = vpm.axis_still_valid(None, [X])
check("None -> None", r_nil is None,
        "%r, wanted None (nothing stored at all)" % (r_nil,))
r_rel = vpm.axis_still_valid({"timeline": [entry(X, 0.0)]}, [X])
check("without an absolute flag it counts as relative",
        (r_rel or {}).get("absolute") is False,
        "%r, wanted False (no timeline_absolute stored)"
        % ((r_rel or {}).get("absolute"),))
shutil.rmtree(D2, ignore_errors=True)

print("\n5. The interface really calls this path")
source = open(SCRIPT, encoding="utf-8").read()
for call in ("header_value = recordings_text(",
             "fresh = pending_prework(",
             "from_s, until, absolute = window_suggestion(",
             "return axis_still_valid(d, paths)"):
    check("calls %s" % call.split("=")[-1].strip()[:20], call in source,
          "%d places in %s hold %r, wanted at least 1"
          % (source.count(call), os.path.basename(SCRIPT), call))
# Only the code half, so the catalogue's own entry does not count as a
# second place that builds the line. The "or" this replaces passed as
# soon as either half held, which is to say always.
code_only = source.split('CATALOGUE["de"] = {', 1)[0]
check("the header line is built in one place only",
      code_only.count("recordings from") == 1,
      "%d places outside the catalogue build it, wanted 1"
      % code_only.count("recordings from"))
OLD_WINDOW = 'start_var.set(timecode_string(min(starts), fps))'
check("the old window computation is gone", OLD_WINDOW not in source,
        "%d places still hold %r, wanted 0"
        % (source.count(OLD_WINDOW), OLD_WINDOW))

print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
