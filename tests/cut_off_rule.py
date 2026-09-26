# -*- coding: utf-8 -*-
"""A text cut off is noted, not failed, in the builder's release run.

The owner's rule, 26.9.2026: a text not fully shown, in any language,
English and German included, is reported by the release run and does
not stop the release; every everyday run stays red on it. The release
run is the one tests.yml gives VPM_CUT_OFF=noted, and only beside
VPM_ALL_LANGUAGES=1 -- run.sh refuses it alone. Everything else a test
judges stays red in both.
"""
import os

NOTED = os.environ.get("VPM_CUT_OFF") == "noted"


def noted(name, extra):
    """True where this cut-off finding is noted instead of failed.

    It then prints the line run.sh collects into the summary's block,
    with every number the check would have failed with.
    """
    if not NOTED:
        return False
    print("NOTED cut off: %s [%s]" % (name, extra or "no numbers"))
    return True
