# -*- coding: utf-8 -*-
"""The speech time the preview reports fits inside the timeline.

The sentence under the preview says how many minutes land on each
camera. Counted once per speaker instead of once per moment, three
people talking at once are counted three times: a real run reported
181 minutes on the wide shot of a timeline 83 minutes long, and the
percentage beside it looked right. Two grounds, both built here: one
where everybody talks over everybody, and one where nobody does.
"""
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = os.environ.get("VPM_SCRIPT") or os.path.join(
    os.path.dirname(HERE), "videopodcast-magic.py")

import importlib.util

spec = importlib.util.spec_from_file_location("vpm", SCRIPT)
vpm = importlib.util.module_from_spec(spec)
sys.modules["vpm"] = vpm
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


LENGTH = 600.0
CAMERAS = [{"track": "CamA", "speakers": ["Presenter"]},
           {"track": "CamB", "speakers": ["Guest"]},
           {"track": "CamC", "speakers": ["CoPresenter"]},
           {"track": "WideCam", "speakers": []}]

# Everybody over everybody: three people, forty seconds each in every
# minute, offset by ten and twenty. Their speech adds up to twenty
# minutes inside a ten-minute programme, which is exactly the shape
# that made the sentence impossible.
TALKED_OVER = [{"name": name,
                "sections": [[float(a + lead), float(a + lead + 40)]
                             for a in range(0, int(LENGTH) - 60, 60)]}
               for name, lead in (("Presenter", 0), ("CoPresenter", 10),
                                  ("Guest", 20))]
# And nobody over anybody: turns of twenty seconds, five seconds of
# silence between them, so the speech there is can be added up by hand.
ONE_AT_A_TIME = [{"name": "Presenter",
                  "sections": [[float(a), float(a + 20)]
                               for a in range(0, int(LENGTH) - 50, 50)]},
                 {"name": "Guest",
                  "sections": [[float(a + 25), float(a + 45)]
                               for a in range(0, int(LENGTH) - 50, 50)]}]
ALONE_SPEECH = sum(b - a for s in ONE_AT_A_TIME for a, b in s["sections"])


def numbers_for(speakers):
    """What the preview would report over these speakers."""
    return vpm.cut_statistics({"speakers": speakers, "cameras": CAMERAS,
                               "length_s": LENGTH},
                              3.0, 0.3, 0.0, 5.0, 120.0, True)


print("1. Three people talking over each other")
crowd = numbers_for(TALKED_OVER) or {}
shares = [crowd.get("in_frame_s"), crowd.get("on_wide_s"),
          crowd.get("off_camera_s")]
told = "on their own camera %s, on the wide shot %s, off camera %s, of a "\
       "timeline of %.1f s" % (shares[0], shares[1], shares[2], LENGTH)
check("three people talking at once still make a cut, so the numbers "
      "below are about something",
      bool(crowd.get("cut")) and None not in shares,
      "%d shots, %s" % (len(crowd.get("cut") or []), told))
check("no one share of the speech time is longer than the timeline",
      all(v is not None and v <= LENGTH for v in shares), told)
check("the three shares of speech time together fit inside the timeline",
      None not in shares and sum(shares) <= LENGTH,
      "they add up to %s s, %s"
      % ("%.1f" % sum(shares) if None not in shares else "?", told))
check("and they add up to the speech time the preview reports",
      None not in shares
      and abs(sum(shares) - (crowd.get("speech_time_s") or -1)) < 0.05,
      "the three add up to %s s, the reported speech time is %s s"
      % ("%.1f" % sum(shares) if None not in shares else "?",
         crowd.get("speech_time_s")))
per_cent = [crowd.get("in_frame"), crowd.get("on_wide"),
            crowd.get("off_camera")]
check("the same three in per cent add up to a hundred",
      None not in per_cent and abs(sum(per_cent) - 100.0) < 0.05,
      "%s add up to %s"
      % (per_cent, "%.2f" % sum(per_cent) if None not in per_cent else "?"))

print("\n2. And where nobody talks over anybody")
alone = numbers_for(ONE_AT_A_TIME) or {}
apart = [alone.get("in_frame_s"), alone.get("on_wide_s"),
         alone.get("off_camera_s")]
check("where nobody talks over anybody the speech time is the speech "
      "there is",
      None not in apart and abs(sum(apart) - ALONE_SPEECH) < 0.5,
      "the preview counts %s s, the turns add up to %.1f s"
      % ("%.1f" % sum(apart) if None not in apart else "?", ALONE_SPEECH))

print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
