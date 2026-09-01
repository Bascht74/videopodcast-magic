"""Two talk at once: does the camera showing both come up?"""
import os
HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = os.environ.get("VPM_SCRIPT") or os.path.join(
    os.path.dirname(HERE), "videopodcast-magic.py")
import importlib.util, sys, time
spec = importlib.util.spec_from_file_location(
    "vpm", SCRIPT)
vpm = importlib.util.module_from_spec(spec); sys.modules["vpm"] = vpm
spec.loader.exec_module(vpm)

began = time.time()
done = 0
bad = []


def check(name, ok, extra=""):
    global done
    done += 1
    print("  %-58s %s %s" % (name, "ok" if ok else "FAIL", extra))
    if not ok:
        bad.append("%s [%s]" % (name, extra or "no numbers"))


def at(cut, t):
    """The camera on screen at that moment."""
    return next((w for a, b, w in cut if a <= t < b), "nothing")


def show(title, tracks, camera_of, length=30.0):
    """Print the cut, check the shape every cut must have, hand it back.

    Which camera belongs where is judged by the caller. The shape is
    not: segments in order, without gap or overlap, from 0 to the end,
    and every one of them names a camera that exists.
    """
    print("\n== %s" % title)
    s = vpm.build_camera_cut(tracks, length, camera_of, "Wide",
                          min_len=0.0, lead_in=0.0)
    for a, b, who in s:
        print("   %5.1f - %5.1f s   %s" % (a, b, who))
    known = set(camera_of.values()) | {"Wide"}
    check("segments, and they run forwards",
          bool(s) and all(b > a for a, b, _w in s),
          "%d segments, backwards: %s" % (
              len(s), [(a, b) for a, b, _w in s if b <= a][:2]))
    check("no gap and no overlap",
          all(abs(s[i][1] - s[i + 1][0]) < 1e-6 for i in range(len(s) - 1)),
          str([(round(x[1], 2), round(y[0], 2))
               for x, y in zip(s, s[1:]) if abs(x[1] - y[0]) >= 1e-6][:2]))
    check("covers 0 to the end",
          abs(s[0][0]) < 1e-6 and abs(s[-1][1] - length) < 1e-6,
          "%.2f .. %.2f of %.1f" % (s[0][0], s[-1][1], length))
    strangers = sorted({w for _a, _b, w in s} - known)
    check("only cameras that exist", not strangers, str(strangers))
    return s

cameras = {"Host": "Hosts", "Co-host": "Hosts",
           "Guest": "Guest"}
tracks = [("Host",    [(0, 5), (10, 15)]),
          ("Co-host", [(12, 15), (20, 25)]),
          ("Guest",   [(5, 10), (22, 25)])]
shared = show("hosts share one camera", tracks, cameras)

# Everyone on a camera of their own, so no two-shot exists.
cameras2 = {"Host": "Host", "Co-host": "Co-host",
            "Guest": "Guest"}
apart = show("everyone has their own camera", tracks, cameras2)

# The question the file is here for, asked both ways round: the hosts
# talk over each other from 12 to 15 s.
check("both hosts at once: the camera showing both comes up",
      at(shared, 13.0) == "Hosts", at(shared, 13.0))
check("and where no camera shows both, the wide shot does",
      at(apart, 13.0) == "Wide", at(apart, 13.0))

tracks3 = [("Host", [(0, 10)]), ("Co-host", [(5, 10)]),
           ("Guest", [(8, 10)])]
show("three talk, only one camera covers all", tracks3,
     {"Host": "All", "Co-host": "All", "Guest": "All"}, 12.0)

# The only place where all three speak at once and no camera shows them
# all: the cut has to fall back on the wide shot there. The cases above
# overlap in pairs only.
cameras3 = {"Host": "Hosts", "Co-host": "Hosts",
            "Guest": "Guest"}
show("all three at once, no camera covers them", tracks3, cameras3, 12.0)

print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
