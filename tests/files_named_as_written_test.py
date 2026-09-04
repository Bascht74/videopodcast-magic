# -*- coding: utf-8 -*-
"""Curve and camera are named from the file's words, not from a likeness.

The identifiers are the ones real recordings carry: the two Apple log
atoms with the two colour spaces they stand for, an identifier nobody
knows, an empty atom. Then the markers the camera keys are searched by
-- a marker is a word of its own and a version digit may follow it,
while a longer word that merely contains it is not one. Last the camera
line, where a plain key names the device and the usual keys are absent.
A marker glued behind a letter, SonySLog3, is not found and is not
asked for here.
"""
import os
HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = os.environ.get("VPM_SCRIPT") or os.path.join(
    os.path.dirname(HERE), "videopodcast_magic.py")
import sys, time, importlib.util
spec = importlib.util.spec_from_file_location("vpm", SCRIPT)
vpm = importlib.util.module_from_spec(spec); sys.modules["vpm"] = vpm
spec.loader.exec_module(vpm)
vpm.set_language("en")

began = time.time()
done = 0
bad = []


def check(name, ok, extra=""):
    global done
    done += 1
    print("  %-58s %s %s" % (name, "ok" if ok else "FAIL", extra))
    if not ok:
        bad.append("%s [%s]" % (name, extra or "no numbers"))


print("A. The logs atom names the curve and the space it was shot in")
got = vpm.log_curve_from_atom("com.apple.rec2020.apple-log")
check("the rec2020 atom names Apple Log in Rec.2020",
      got == "Apple Log (Rec.2020)",
      "read back %r, wanted %r" % (got, "Apple Log (Rec.2020)"))

got = vpm.log_curve_from_atom("com.apple.apple-wide-gamut.apple-log")
check("the apple-wide-gamut atom names Apple Log 2 in its own space",
      got == "Apple Log 2 (Apple Wide Gamut)",
      "read back %r, wanted %r" % (got, "Apple Log 2 (Apple Wide Gamut)"))

got = vpm.log_curve_from_atom("com.example.some-space.some-log")
check("an identifier nobody knows stands there as it is",
      got == "com.example.some-space.some-log",
      "read back %r, wanted %r" % (got, "com.example.some-space.some-log"))

got = vpm.log_curve_from_atom("")
check("an empty logs atom names no curve at all", got == "",
      "read back %r, wanted %r" % (got, ""))

got = vpm.log_curve_from_atom("\x00com.apple.rec2020.apple-log\x00\x00")
check("zero bytes around the identifier do not hide it",
      got == "Apple Log (Rec.2020)",
      "read back %r, wanted %r" % (got, "Apple Log (Rec.2020)"))

print("\nB. A marker is a word, not a piece of a longer one")
got = vpm._marker_stands_alone("s-log3", "s-log")
check("a version digit after the marker still counts as the marker",
      got is True, "s-log in %r gave %r, wanted True" % ("s-log3", got))

got = vpm._marker_stands_alone("logc4", "logc")
check("logc with a version digit after it still counts", got is True,
      "logc in %r gave %r, wanted True" % ("logc4", got))

got = vpm._marker_stands_alone("vlogger in shot", "vlog")
check("a longer word that only contains vlog is no marker", got is False,
      "vlog in %r gave %r, wanted False" % ("vlogger in shot", got))

got = vpm._marker_stands_alone("slogan of the day", "slog")
check("a longer word that only contains slog is no marker", got is False,
      "slog in %r gave %r, wanted False" % ("slogan of the day", got))

got = vpm._marker_stands_alone("catalog gamma", "log gamma")
check("a marker that only ends a longer word is no marker", got is False,
      "log gamma in %r gave %r, wanted False" % ("catalog gamma", got))

got = vpm._log_in_colour_tags(
    {"com.blackmagic-design.camera.gamma": "Blackmagic Design Film"})
check("a camera key that names a log curve is reported as log",
      got == "com.blackmagic-design.camera.gamma = Blackmagic Design Film",
      "read back %r, wanted the key and its value" % (got,))

got = vpm._log_in_colour_tags(
    {"com.apple.quicktime.description": "Vlogger in shot"})
check("a camera key whose text only contains vlog reports nothing",
      got == "", "read back %r, wanted %r" % (got, ""))

print("\nC. The camera line takes the name wherever the file puts it")
got = vpm.camera_text({"encoder": "Osmo 360"})
check("a device named only by the encoder key reaches the line",
      got == "Osmo 360", "read back %r, wanted %r" % (got, "Osmo 360"))

got = vpm.camera_text({"com.apple.quicktime.model": "Apple iPhone 17 Pro",
                       "com.apple.quicktime.software": "Camera 1.0",
                       "encoder": "Lavf63.1.101"})
check("a device that names itself keeps the encoder out of the line",
      got == "Apple iPhone 17 Pro  --  Software Camera 1.0",
      "read back %r, wanted %r"
      % (got, "Apple iPhone 17 Pro  --  Software Camera 1.0"))

got = vpm.camera_text({"major_brand": "qt  "})
check("a file that names nothing at all says so",
      got == vpm.T('no information in the file'),
      "read back %r, wanted %r" % (got, vpm.T('no information in the file')))

print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
