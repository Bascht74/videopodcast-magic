"""Two talk at once: does the camera showing both come up?"""
import os
HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = os.environ.get("VPM_SCRIPT") or os.path.join(
    os.path.dirname(HERE), "videopodcast-magic.py")
import importlib.util, sys
spec = importlib.util.spec_from_file_location(
    "vpm", SCRIPT)
vpm = importlib.util.module_from_spec(spec); sys.modules["vpm"] = vpm
spec.loader.exec_module(vpm)

error = []
def check(name, ok, extra=""):
    print("  %-48s %s %s" % (name, "ok" if ok else "FAIL", extra))
    if not ok:
        error.append(name)


def show(title, tracks, camera_of, length=30.0):
    """Print the cut and hold it to what a cut must always be.

    Which camera is right where is a judgement about the material, and
    this test does not make it -- the numbers are here to be read. What
    can be settled without judgement is the shape: a cut is a run of
    segments, in order, without gap or overlap, from 0 to the end, and
    every one of them names a camera that exists.
    """
    print("\n== %s" % title)
    s = vpm.build_camera_cut(tracks, length, camera_of, "Wide",
                          min_len=0.0, lead_in=0.0)
    for a, b, who in s:
        print("   %5.1f - %5.1f s   %s" % (a, b, who))
    known = set(camera_of.values()) | {"Wide"}
    check("segments, and they run forwards",
          bool(s) and all(b > a for a, b, _w in s))
    check("no gap and no overlap",
          all(abs(s[i][1] - s[i + 1][0]) < 1e-6 for i in range(len(s) - 1)),
          str([(round(x[1], 2), round(y[0], 2))
               for x, y in zip(s, s[1:]) if abs(x[1] - y[0]) >= 1e-6][:2]))
    check("covers 0 to the end",
          abs(s[0][0]) < 1e-6 and abs(s[-1][1] - length) < 1e-6,
          "%.2f .. %.2f of %.1f" % (s[0][0], s[-1][1], length))
    strangers = sorted({w for _a, _b, w in s} - known)
    check("only cameras that exist", not strangers, str(strangers))

# Case 1: both hosts on ONE camera, the guest on a camera of their own
cameras = {"Host": "Hosts", "Co-host": "Hosts",
           "Guest": "Guest"}
tracks = [("Host",    [(0, 5), (10, 15)]),
          ("Co-host", [(12, 15), (20, 25)]),
          ("Guest",   [(5, 10), (22, 25)])]
show("hosts share one camera", tracks, cameras)

# Case 2: everyone has their own camera -> no two-shot exists
cameras2 = {"Host": "Host", "Co-host": "Co-host",
            "Guest": "Guest"}
show("everyone has their own camera", tracks, cameras2)

# Case 3: a three-shot camera covers them all
cameras3 = {"Host": "Hosts", "Co-host": "Hosts",
            "Guest": "All"}
tracks3 = [("Host", [(0, 10)]), ("Co-host", [(5, 10)]),
           ("Guest", [(8, 10)])]
show("three talk, only one camera covers all", tracks3,
     {"Host": "All", "Co-host": "All", "Guest": "All"}, 12.0)

print()
if error:
    print("FAIL: " + ", ".join(error))
    sys.exit(1)
print("All good.")
