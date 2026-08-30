# -*- coding: utf-8 -*-
"""A mono master does not stand in for the stereo one.

On resume the outputs already there are read back and only the rest
is asked for. Auphonic appends rather than replaces, so an output
sent twice is computed and billed twice.
"""
import os
HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = os.environ.get("VPM_SCRIPT") or os.path.join(
    os.path.dirname(HERE), "videopodcast-magic.py")
import importlib.util, sys
spec = importlib.util.spec_from_file_location("vpm", SCRIPT)
vpm = importlib.util.module_from_spec(spec); sys.modules["vpm"] = vpm
spec.loader.exec_module(vpm)
bad = []


def check(what, ok, detail=""):
    print("  %-58s %s%s" % (what, "ok" if ok else "FAIL",
                            "" if ok else "   " + detail))
    if not ok:
        bad.append(what)


# On resume the existing outputs are read back; the answer names the
# file but not always its channel count, and where it does it decides.
mono_there = [{"format": "wav", "filename": "Show_master.wav",
               "mono_mixdown": True}]
want_stereo = [{"format": "wav", "suffix": "_master", "mono_mixdown": False}]
check("the two-channel one is still missing",
      vpm.missing_outputs(mono_there, want_stereo) == want_stereo,
      str(vpm.missing_outputs(mono_there, want_stereo)))
check("and the one that is there is not asked for again",
      vpm.missing_outputs(mono_there, [dict(want_stereo[0],
                                            mono_mixdown=True)]) == [])
unsaid = [{"format": "wav", "filename": "Show_master.wav"}]
check("where the answer says nothing, nothing is sent twice",
      vpm.missing_outputs(unsaid, want_stereo) == [],
      str(vpm.missing_outputs(unsaid, want_stereo)))
# An empty channel count is no answer: taken for one, a resume sends
# the master again, and auphonic.com appends rather than replaces, so
# it is computed and billed twice.
empty = [{"format": "wav", "filename": "Show_master.wav",
          "mono_mixdown": None}]
check("an empty channel count counts as no answer",
      vpm.missing_outputs(empty, want_stereo) == [],
      str(vpm.missing_outputs(empty, want_stereo)))
# Configured but never rendered: no file name to read a suffix from.
planned = [{"format": "wav", "suffix": "_master", "mono_mixdown": False}]
check("a configured output is found by its own suffix",
      vpm.missing_outputs(planned, want_stereo) == [],
      str(vpm.missing_outputs(planned, want_stereo)))
check("and one that says nothing about its channels counts for both",
      vpm.missing_outputs([{"format": "wav", "suffix": "_master"}],
                          want_stereo) == [])
check("and a stated one channel still asks for the two channel one",
      vpm.missing_outputs(
          [{"format": "wav", "filename": "Show_master.wav",
            "mono_mixdown": True}],
          [dict(want_stereo[0], mono_mixdown=False)]) != [])

print()
if bad:
    print("FAIL: %d of the checks" % len(bad))
    sys.exit(1)
print("all checks passed")
