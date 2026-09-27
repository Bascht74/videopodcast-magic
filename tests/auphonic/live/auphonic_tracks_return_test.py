# -*- coding: utf-8 -*-
"""Two tracks go through a real multitrack production and come back apart.

Against auphonic.com itself, and it spends credit: twenty seconds each
of two tracks, the Presenter speaking in the first half and the Guest
in the second, through the account's first multitrack preset, or the
one VPM_LIVE_PRESET names. In order -- the program creates, uploads,
starts, waits and fetches, and leaves one file for each track sent;
each is as long as the one sent, whatever auphonic.com put around it;
each carries its own voice and not the other's, so the tracks were not
mixed and not swapped; and the production, found again by its title, is
deleted. The title has the tests' own shape, so a run killed half way
is cleared by the sweep auphonic.sh makes at both ends.

The voices are told apart by where they speak, measured by ffmpeg
decoding and a plain RMS here, not by the program. A step that throws is
a failed judgement and not a traceback, so the closing count is reached
whatever happens.
"""
PLATFORM_BOUND = True
import array
import math
import os
import shutil
import subprocess
import sys
import tempfile
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import auphonic_ground as ground

ground.gate(spends=True)

began = time.time()
done = 0
bad = []
SECONDS = 20
HALF = SECONDS / 2.0
# How far a file left may differ from the one sent: a jingle is
# seconds, a lossy file cut to its frames keeps hundredths.
SLACK_S = 0.1
# Each half is measured a second short of its edges, so a cut that sits
# a few hundredths off does not carry one voice's edge into the other.
EDGE_S = 0.5
# How much quieter the other half has to be than the track's own: it
# was sent silent, and a mixed track would carry the other voice there
# at about the same level.
APART_DB = 20.0
# Roles, not people; each speaks in its own half of the same twenty
# seconds, as two microphones on one conversation would.
SPEAKS = {"Presenter": (0, HALF), "Guest": (HALF, SECONDS)}


def check(name, ok, extra=""):
    global done
    done += 1
    print("  %-58s %s %s" % (name, "ok" if ok else "FAIL", extra))
    if not ok:
        bad.append("%s [%s]" % (name, extra or "no numbers"))


def said(e):
    """An exception as one short line."""
    return " ".join(str(e).split())[:200]


def level_db(path, start, seconds):
    """RMS in dB below full scale of one span, decoded by ffmpeg here.

    Not through the program: which voice lies where is what is being
    judged, so the measure takes another road. Silence reads -120.
    """
    out = subprocess.run(
        ["ffmpeg", "-v", "error", "-ss", "%.3f" % start, "-t",
         "%.3f" % seconds, "-i", path, "-ac", "1", "-ar", "8000",
         "-f", "s16le", "-"], stdout=subprocess.PIPE,
        stderr=subprocess.PIPE)
    if out.returncode != 0:
        raise OSError("ffmpeg could not decode %s: %s" % (
            os.path.basename(path), said(out.stderr.decode("utf-8",
                                                           "replace"))))
    pcm = array.array("h")
    pcm.frombytes(out.stdout[:len(out.stdout) // 2 * 2])
    if sys.byteorder == "big":
        pcm.byteswap()
    if not pcm:
        raise ValueError("nothing decoded from %.1f s in %s"
                         % (start, os.path.basename(path)))
    rms = math.sqrt(sum(x * x for x in pcm) / float(len(pcm)))
    return max(-120.0, 20 * math.log10(max(rms, 1e-9) / 32768.0))


vpm = ground.program()
key, origin = ground.the_key(vpm)
preset = ground.a_preset(vpm, key, multitrack=True)
folder = tempfile.mkdtemp(prefix="vpm_auphonic_live_")
title = ground.a_test_title("multi")
try:
    tracks = [{"name": name, "axis": ground.syllables(
        os.path.join(folder, "%s.wav" % name.lower()), SECONDS,
        between=span, seed=3 + i)}
        for i, (name, span) in enumerate(sorted(SPEAKS.items()))]

    print("1. Create, upload, start, wait and fetch, the way a run does")
    result, why = {}, ""
    try:
        result = vpm.run_multitrack_production(
            key, preset, title, tracks, os.path.join(folder, "back"),
            wait_s=900) or {}
    except Exception as e:
        # Not only auphonic.com's refusals: a broken archive or a file
        # that will not unpack is this step failing too.
        why = said(e)
    there = sorted(n for n, p in result.items() if p and os.path.isfile(p))
    check("the production comes back with a file for each track sent",
          there == sorted(SPEAKS)
          and len(set(result[n] for n in there)) == len(SPEAKS),
          why or "back: %s against sent: %s, %d different files"
          % (", ".join(there) or "none", ", ".join(sorted(SPEAKS)),
             len(set(result[n] for n in there))))

    print("\n2. What the program leaves")
    lengths, why = {}, ""
    for name in there:
        try:
            lengths[name] = ground.measured(result[name])[0]
        except (OSError, ValueError) as e:
            why = said(e)
    check("every track the program leaves is as long as the one sent",
          sorted(lengths) == sorted(SPEAKS)
          and all(abs(s - SECONDS) <= SLACK_S for s in lengths.values()),
          "%s against %d s sent, %.1f s allowed%s"
          % (", ".join("%s %.2f s" % (n, lengths[n]) for n in sorted(lengths))
             or "nothing measured", SECONDS, SLACK_S,
             (" -- " + why) if why else ""))

    apart, why = {}, ""
    for name in there:
        own = SPEAKS[name]
        other = (HALF, SECONDS) if own[0] == 0 else (0, HALF)
        try:
            apart[name] = (
                level_db(result[name], own[0] + EDGE_S, HALF - 2 * EDGE_S),
                level_db(result[name], other[0] + EDGE_S,
                         HALF - 2 * EDGE_S))
        except (OSError, ValueError) as e:
            why = said(e)
    check("each track back carries its own voice and not the other's",
          sorted(apart) == sorted(SPEAKS)
          and all(o - x >= APART_DB for o, x in apart.values()),
          "%s, %.0f dB wanted%s"
          % (", ".join("%s %.1f dB where it speaks, %.1f dB where the other "
                       "does" % (n, apart[n][0], apart[n][1])
                       for n in sorted(apart)) or "nothing measured",
             APART_DB, (" -- " + why) if why else ""))

    print("\n3. The production is taken away again")
    found, why = None, ""
    try:
        found = vpm.find_production_by_title(key, title)
    except RuntimeError as e:
        why = said(e)
    check("the production stands at auphonic.com under the title given",
          bool(found) and bool(found.get("uuid")),
          why or "%s under %s among the last 50"
          % ((found or {}).get("uuid") or "none", title))
    if found and found.get("uuid"):
        gone, why = False, ""
        try:
            gone = ground.delete(vpm, key, found["uuid"])
        except RuntimeError as e:
            why = said(e)
        check("the tests' own production can be deleted again", gone,
              why or "auphonic.com said %s to deleting %s"
              % ("yes" if gone else "no", found["uuid"]))
except Exception as e:
    # Not a judgement of its own: a step that threw is named in the
    # closing line, so every path still ends there.
    bad.append("the test stopped half way [%s: %s]"
               % (type(e).__name__, said(e)))
finally:
    shutil.rmtree(folder, ignore_errors=True)

print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
