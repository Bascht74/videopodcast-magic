# -*- coding: utf-8 -*-
"""The opening wide shot must not depend on how finely a source cuts.

The rule holds the wide shot until the floor changes hands. A
recogniser that chops one long introduction into ten blocks used to
read as ten handovers, and the opening ended after the first of them.
"""
import os
HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = os.environ.get("VPM_SCRIPT") or os.path.join(
    os.path.dirname(HERE), "videopodcast-magic.py")
import importlib.util, sys
spec = importlib.util.spec_from_file_location("vpm", SCRIPT)
vpm = importlib.util.module_from_spec(spec); sys.modules["vpm"] = vpm
spec.loader.exec_module(vpm)

error = []
def check(name, ok, extra=""):
    print("  %-52s %s %s" % (name, "ok" if ok else "FAIL", extra))
    if not ok:
        error.append(name)

LENGTH = 600.0
# The guest holds the floor for most of the programme, so the guest is
# the main speaker and the host is who ends the opening.
GUEST = [(100.0 + 30 * i, 125.0 + 30 * i) for i in range(15)]
CLOSING = [(560.0, 585.0)]
CAMERA_OF = {"Guest": "CamGuest", "Host": "CamHost", "Ghost": "CamHost"}

# The introduction, once as one block and once chopped into pieces of
# four to eight seconds with gaps of a fifth of a second to one and a
# half. Both are the same ninety-two seconds of one person talking.
PIECES = [(0.0, 6.4), (7.1, 12.6), (13.5, 18.0), (19.4, 24.6),
          (25.3, 32.0), (32.6, 38.1), (39.0, 46.2), (47.0, 51.9),
          (53.1, 58.8), (59.3, 66.5), (67.2, 72.4), (73.9, 79.1),
          (80.0, 85.3), (86.1, 92.2)]


def opening_until(tracks):
    """Where the wide shot at the start gives way, or 0 without one."""
    cut = vpm.camera_cut(tracks, LENGTH, CAMERA_OF, "Wide",
                         3.0, 0.3, 0.0, 5.0, 120.0, True, None, faint=True)
    return cut[0][1] if cut and cut[0][2] == "Wide" else 0.0


print("1. The same introduction, told coarsely and finely")
whole = [("Host", [(0.0, 92.2)] + CLOSING), ("Guest", GUEST)]
chopped = [("Host", PIECES + CLOSING), ("Guest", GUEST)]
one_block = opening_until(whole)
many_blocks = opening_until(chopped)
check("one block holds the opening", one_block > 90.0, "%.1f s" % one_block)
check("fourteen blocks hold it just as long",
      abs(many_blocks - one_block) < 0.001,
      "%.1f s against %.1f s" % (many_blocks, one_block))

print("\n2. A gap longer than a breath does end it")
# The same pieces, but the host stops for five seconds after the third
# one. That is a handover, and the opening ends there.
broken = [("Host", PIECES[:3] + [(a + 5.0, b + 5.0) for a, b in PIECES[3:]]
           + CLOSING), ("Guest", GUEST)]
early = opening_until(broken)
check("the opening ends at the pause", 0.0 < early < 30.0, "%.1f s" % early)

print("\n3. One block of the introduction under a wrong name")
# The separation gives two blocks of the introduction a label of their
# own. That used to end the opening after the first of them.
mislabel = [("Host", PIECES[:4] + PIECES[6:] + CLOSING),
            ("Ghost", [PIECES[4], PIECES[5]]), ("Guest", GUEST)]
wrong_name = opening_until(mislabel)
check("the opening is longer than one block",
      wrong_name > PIECES[0][1], "%.1f s" % wrong_name)

print("\n4. floor_handovers on its own")
handovers = vpm.floor_handovers(chopped, "Guest", 4.0)
check("the chopped introduction is one handover",
      len(handovers) == 2, str(handovers))
check("and it runs to the end of the introduction",
      abs(handovers[0][1] - 92.2) < 0.001, str(handovers[0]))
# An island inside somebody else's continuous speech is not a handover:
# nobody has taken the floor there.
island = [("Host", [(0.0, 92.2)] + CLOSING), ("Guest", GUEST),
          ("Ghost", [(30.0, 36.0)])]
_found = vpm.floor_handovers(island, "Guest", 4.0)
check("an island inside another voice is no handover",
      not any(abs(a - 30.0) < 0.001 for a, _b in _found), str(_found))

print("\n%s" % ("all good" if not error
                else "FAIL: %s" % ", ".join(error)))
sys.exit(1 if error else 0)
