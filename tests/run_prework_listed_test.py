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
    os.path.dirname(HERE), "videopodcast-magic.py")
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

print("1. The header line of the audio group")
check("same count -> only the file count",
        vpm.recordings_text(3, 3) == "3 files", vpm.recordings_text(3, 3))
check("blocks grouped -> both",
        vpm.recordings_text(2, 5) == "2 recordings from 5 files",
        vpm.recordings_text(2, 5))
check("a single one", vpm.recordings_text(1, 1) == "1 file",
        vpm.recordings_text(1, 1))
check("one recording out of several files",
        vpm.recordings_text(1, 3) == "1 recording from 3 files",
        vpm.recordings_text(1, 3))
check("none at all", vpm.recordings_text(0, 0) == "0 files",
        vpm.recordings_text(0, 0))

print("\n2. What prework is still open")
D = tempfile.mkdtemp(prefix="prework_")
A = os.path.join(D, "a.mov"); B = os.path.join(D, "b.mov")
for x in (A, B):
    open(x, "wb").write(b"\0" * 8)
GONE = os.path.join(D, "gone.mov")

never = lambda p: False
always = lambda p: True
r = vpm.pending_prework([A, B], having_audio=[A], has_audio=never,
                        has_env_curve=never)
check("audio only for the one, envelope for both",
        r == [(A, "audio"), (A, "envelope"), (B, "envelope")], str(r))
r = vpm.pending_prework([A, B], having_audio=[A], has_audio=always,
                        has_env_curve=never)
check("audio is already there -> envelopes only",
        r == [(A, "envelope"), (B, "envelope")], str(r))
r = vpm.pending_prework([A, B], having_audio=[A], has_audio=never,
                        has_env_curve=always)
check("envelopes are already there -> audio only",
        r == [(A, "audio")], str(r))
r = vpm.pending_prework([A, B], having_audio=[A], has_audio=always,
                        has_env_curve=always)
check("everything there -> nothing to do", r == [], str(r))
r = vpm.pending_prework([A, GONE, B], having_audio=[], has_audio=never,
                        has_env_curve=never)
check("a file that is gone drops out",
        r == [(A, "envelope"), (B, "envelope")], str(r))
r = vpm.pending_prework([A, B], having_audio=[A, B],
                        has_audio=lambda p: None if p == A else False,
                        has_env_curve=never)
check("cannot be asked -> left out entirely, envelope too",
        r == [(B, "audio"), (B, "envelope")], str(r))
r = vpm.pending_prework([A], having_audio=[], has_audio=never,
                        has_env_curve=never)
check("without having_audio, has_audio is not asked",
        r == [(A, "envelope")], str(r))
r = vpm.pending_prework([])
check("nothing in -> nothing out", r == [])
# A relative path has to hit the same file as an absolute one
old = os.getcwd(); os.chdir(D)
r = vpm.pending_prework(["a.mov"], having_audio=["a.mov"], has_audio=never,
                        has_env_curve=never)
os.chdir(old)
check("relative path becomes absolute", r and r[0][0] == os.path.realpath(A)
        or r and os.path.samefile(r[0][0], A), str(r[:1]))
shutil.rmtree(D, ignore_errors=True)

print("\n3. In point and Out point from what the cameras offer")
f = vpm.window_suggestion
from_s, until, absolute = f([(61200.0, 600.0), (61260.0, 300.0)], 30.0)
check("absolute recognised", absolute is True)
check("earliest start", from_s == vpm.timecode_string(61200.0, 30.0), from_s)
check("latest end", until == vpm.timecode_string(61800.0, 30.0), until)
from_s, until, absolute = f([(None, 600.0), (61260.0, 300.0)], 30.0)
check("one without a clock time does not count",
        from_s == vpm.timecode_string(61260.0, 30.0) and absolute, from_s)
from_s, until, absolute = f([(None, 600.0), (None, 900.0)], 30.0)
check("no clock time at all -> relative", absolute is False)
check("from zero", from_s == "+0:00", from_s)
check("up to the longest", until.startswith("+0:15"), until)
from_s, until, absolute = f([(None, 0.0)], 30.0)
check("length zero -> no suggestion at all",
        (from_s, until, absolute) == ("", "", False))
from_s, until, absolute = f([], 30.0)
check("nothing in -> no suggestion at all", from_s == "" and until == "")
from_s, until, absolute = f([(61200.0, None)], 30.0)
check("duration unknown -> end equals start",
        from_s == until == vpm.timecode_string(61200.0, 30.0),
        "%s / %s" % (from_s, until))

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

check("fingerprint is path, time, size",
        vpm.file_fingerprint(X)[0] == os.path.abspath(X)
        and vpm.file_fingerprint(X)[2] == 100)
check("missing file -> None",
        vpm.file_fingerprint(os.path.join(D2, "gone.mov")) is None)

D_OK = {"timeline": [entry(X, 0.0), entry(Y, 5.0)],
        "timeline_absolute": True}
r = vpm.axis_still_valid(D_OK, [X, Y])
check("unchanged -> applies", r is not None and len(r["axis"]) == 2)
# Looked up by path_key, the one shape a path takes when two are
# compared. On a Mac that is the absolute path; on Windows it is that
# with the case and the separator settled as well, and the axis a
# measurement hands back is keyed the same way.
check("the values come along", r and r["axis"][vpm.path_key(Y)] == 5.0)
check("absolute is carried over", r and r["absolute"] is True)
check("weak is empty", r and r["weak"] == [])

D_OLD = {"timeline": [entry(X, 0.0), entry(Y, 5.0, mtime=1)]}
check("one file changed -> everything discarded",
        vpm.axis_still_valid(D_OLD, [X, Y]) is None)
D_SIZE = {"timeline": [entry(X, 0.0, size=99), entry(Y, 5.0)]}
check("different size -> discarded",
        vpm.axis_still_valid(D_SIZE, [X, Y]) is None)
check("a file not in it at all -> discarded",
        vpm.axis_still_valid({"timeline": [entry(X, 0.0)]}, [X, Y]) is None)
check("no files asked -> None", vpm.axis_still_valid(D_OK, []) is None)
check("empty data -> None", vpm.axis_still_valid({}, [X]) is None)
check("None -> None", vpm.axis_still_valid(None, [X]) is None)
check("without an absolute flag it counts as relative",
        vpm.axis_still_valid({"timeline": [entry(X, 0.0)]},
                          [X])["absolute"] is False)
shutil.rmtree(D2, ignore_errors=True)

print("\n5. The interface really calls this path")
source = open(SCRIPT, encoding="utf-8").read()
for call in ("header_value = recordings_text(",
             "fresh = pending_prework(",
             "from_s, until, absolute = window_suggestion(",
             "return axis_still_valid(d, paths)"):
    check("calls %s" % call.split("=")[-1].strip()[:20], call in source)
# Only the code half, so the catalogue's own entry does not count as a
# second place that builds the line. The "or" this replaces passed as
# soon as either half held, which is to say always.
code_only = source.split('CATALOGUE["de"] = {', 1)[0]
check("the header line is built in one place only",
      code_only.count("recordings from") == 1,
      "%d places outside the catalogue build it, wanted 1"
      % code_only.count("recordings from"))
check("the old window computation is gone",
        'start_var.set(timecode_string(min(starts), fps))' not in source)

print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
