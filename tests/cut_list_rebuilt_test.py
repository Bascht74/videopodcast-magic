# -*- coding: utf-8 -*-
"""The cut list is built again unless the window really moved.

The button once returned at once and left the cut of the last run
standing. A test held the In point against start_s -- but start_s is
the zero of the axis, earlier than any In point anybody sets, so every
window was refused, and a window is the exception, not the rule. And
what Resolve is built from is the file, so the changed cut is read back
off the disk and not out of the dictionary the call was handed.
"""
import os
HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = os.environ.get("VPM_SCRIPT") or os.path.join(
    os.path.dirname(HERE), "videopodcast_magic.py")
import importlib.util, io, json, sys, tempfile, time
import contextlib
spec = importlib.util.spec_from_file_location("vpm", SCRIPT)
vpm = importlib.util.module_from_spec(spec); sys.modules["vpm"] = vpm
spec.loader.exec_module(vpm)
WORK = tempfile.mkdtemp(prefix="cutagain_")
began = time.time()
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


ZERO = 68100.0                                   # 18:55:00:00, the wide shot
speaker_a, speaker_b, at = [], [], 0.0
while at < 300.0:
    speaker_a.append([round(at, 3), round(at + 5.0, 3)])
    speaker_b.append([round(at + 5.0, 3), round(at + 10.0, 3)])
    at += 10.0
STALE = [{"start": 0.0, "end": 300.0, "camera": "Wide"}]
cut_folder = os.path.join(WORK, "cut")
os.makedirs(cut_folder)
for who in ("Wide", "A", "B"):
    open(os.path.join(cut_folder, who + ".mov"), "w").write("x")


def a_handover(window=None):
    """A handover file as a run writes it -- by default without a window."""
    cams = []
    for who, speaks in (("Wide", []), ("A", ["A"]), ("B", ["B"])):
        path = os.path.join(cut_folder, who + ".mov")
        cams.append({"camera": who, "source": path, "file": path,
                     "track": who, "speakers": speaks, "offset": 0.0})
    return {"production": "Test", "start_s": ZERO, "fps": 30,
            "fps_measured": 30.0, "start_tc": "18:55:00:00",
            "length_s": 300.0,
            "in_point": (window or (None, None))[0],
            "out_point": (window or (None, None))[1],
            "speakers": [{"name": "A", "sections": speaker_a},
                         {"name": "B", "sections": speaker_b}],
            "cameras": cams, "cut": list(STALE)}


def refreshed(call, window=None):
    """Put the settings in the project file and press the button."""
    with open(os.path.join(cut_folder, "videopodcast-magic_Test.json"),
              "w", encoding="utf-8") as f:
        json.dump({"production": "Test", "call": call}, f)
    d = a_handover(window)
    path = os.path.join(cut_folder, "Test_resolve.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(d, f)
    kept, sys.argv[1:] = sys.argv[1:], []
    try:
        reason, _said = spoken(vpm.refresh_cut_list, d, path)
    finally:
        sys.argv[1:] = kept
    # And the file as it now lies: the button's whole point is that
    # Resolve is built from what is on disk, not from a dictionary.
    with open(path, encoding="utf-8") as f:
        return reason, d.get("cut") or [], json.load(f)


def as_shots(cut):
    """One cut list as plain tuples, whichever side it came from."""
    return [(c["start"], c["end"], c["camera"]) for c in (cut or [])]


short, short_cut, short_disk = refreshed(["--min-edit-duration", "3"])
check("without a window it does not refuse", short is None, str(short))
check("and the cut of the last run is gone", short_cut != STALE,
      str(short_cut[:2]))
long_r, long_cut, _disk = refreshed(["--min-edit-duration", "12"])
check("the turned setting does not refuse either", long_r is None,
      str(long_r))
check("and it really builds again: another number of shots",
      len(long_cut) != len(short_cut),
      "%d and %d" % (len(long_cut), len(short_cut)))
# What Resolve is really built from is the file, and a changed setting
# that never reaches it leaves the old cut standing there.
check("the changed cut reaches the handover file on disk",
      as_shots(short_disk.get("cut")) == as_shots(short_cut)
      and as_shots(short_disk.get("cut")) != as_shots(STALE),
      "the file carries %d shots, the button built %d, the run left %d"
      % (len(short_disk.get("cut") or []), len(short_cut), len(STALE)))
check("and the speakers in the file are still the ones the run measured",
      [x.get("name") for x in (short_disk.get("speakers") or [])]
      == ["A", "B"],
      "the file names %s, wanted ['A', 'B']"
      % [x.get("name") for x in (short_disk.get("speakers") or [])])
# The In point of the interface against a handover that has none: the
# pair that was refused.
with_in, in_cut, _disk = refreshed(["--in-point", "18:55:30:00",
                                    "--min-edit-duration", "12"])
check("an In point beside a handover without one does not refuse",
      with_in is None, str(with_in))
check("and gives the same cut as without it", in_cut == long_cut,
      "%d against %d" % (len(in_cut), len(long_cut)))
# And what may still be refused, so that the repair did not take the
# guard with it: the window really did move since the files were made.
moved, _c, _disk = refreshed(["--in-point", "19:00:00:00",
                              "--min-edit-duration", "12"],
                             window=("18:55:30:00", "18:59:00:00"))
check("a window that really moved is still refused", bool(moved),
      str(moved))

print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
