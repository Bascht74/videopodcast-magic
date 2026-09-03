# -*- coding: utf-8 -*-
"""Remote grades: off by default, and always set -- old projects too.

The sections: an old project put back to local, remote grades asked
for, the default without an argument, a setting that only pretends to
have been made, a project whose settings cannot be read, and the build
turning back before it reaches them at all. Nothing here opens a
connection -- the place that would is replaced by one that refuses, so
a Resolve running on this machine is never asked for anything. What
the setting does to a picture is not judged, only what the program
writes and what it reports.
"""
import os
HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = os.environ.get("VPM_SCRIPT") or os.path.join(
    os.path.dirname(HERE), "videopodcast_magic.py")
import importlib.util, sys, time
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


class P(object):
    """Resolve holding the setting -- key named as in a real project."""
    KEY = "useLocalVersionsAsDefault"
    def __init__(self, start="0"):
        self.settings = {self.KEY: start, "timelineFrameRate": "30",
                         "colorScienceMode": "davinciYRGB"}
    def GetSetting(self, k=""):
        return dict(self.settings) if k == "" else self.settings.get(k)
    def SetSetting(self, k, v):
        self.settings[k] = str(v); return True


print("1. Old project with remote grades -> put back to local")
p = P("0")
ok = vpm.set_remote_grades(p, False)
check("reported as set", ok is True, str(ok))
check("setting says local", p.settings[P.KEY] == "1", p.settings[P.KEY])

print("\n2. Remote grades asked for -> local versions off")
p = P("1")
ok = vpm.set_remote_grades(p, True)
check("reported as set", ok is True, str(ok))
check("setting says remote", p.settings[P.KEY] == "0", p.settings[P.KEY])

print("\n3. The function defaults to 'local'")
p = P("0")
vpm.set_remote_grades(p)
check("local without an argument", p.settings[P.KEY] == "1",
        p.settings[P.KEY])

print("\n4. Setting it goes wrong -> not glossed over")
class Stubborn(P):
    def SetSetting(self, k, v): return True     # only pretends to
stubborn = Stubborn("0")
said = vpm.set_remote_grades(stubborn, False)
check("returns False", said is False,
      "returned %r, wanted False; the setting stands at %r"
      % (said, stubborn.settings[P.KEY]))

print("\n5. No settings readable -> a hint, not a crash")
class Blind(object):
    def GetSetting(self, k=""): return None
said = vpm.set_remote_grades(Blind(), False)
check("returns None", said is None, "returned %r, wanted None" % (said,))

print("\n6. build_resolve_project sets them even without a switch")
seen = {}
real = vpm.set_remote_grades
vpm.set_remote_grades = lambda p, on=False: seen.setdefault("on", on)


# The one door to a Resolve that is really running, and it is nailed
# shut. Resolve may be up on this machine, and a project built into it
# would stay in somebody's project manager. Whoever later writes a
# camera into the handover below gets this refusal out loud instead of
# a project -- and it hands out nothing, so it can invent no project
# manager, no timeline and no track either.
knocked = []


def no_resolve():
    knocked.append("build_resolve_project asked for a Resolve")
    raise RuntimeError(knocked[-1])


vpm.connect_to_resolve = no_resolve
# Nothing is caught: without cameras the call turns back before the
# door, so anything coming out of it is news and not noise.
vpm.build_resolve_project({"production": "X", "cameras": []}, "keep",
                  log="")
vpm.set_remote_grades = real
check("without cameras it never gets that far", "on" not in seen,
        "%s, %d knocks at the door" % (seen, len(knocked)))

print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
