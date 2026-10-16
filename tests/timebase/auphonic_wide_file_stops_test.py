# -*- coding: utf-8 -*-
"""A file of more than two channels never goes up to auphonic.com.

auphonic.com takes at most two channels in one file. One recording of
four channels stops the run before the time axis and before a preset
is asked for -- alone, with the picture and without, and beside a
second recording as a Multitrack track -- sends nothing and names the
file and its channels. Cut into pairs, as the window's channel rows cut
it, it goes on; a stereo recording alone still goes up, and a run that
sends nothing is not stopped. auphonic.com and the axis are stood in
for where the piece looks them up: the run stops at the axis.
"""
PLATFORM_BOUND = True
import os
import sys
# tests/, where the helpers and state/ lie; this file may stand in a
# folder under it, or in one under that.
HERE = os.path.dirname(os.path.abspath(__file__))
while not os.path.isfile(os.path.join(HERE, "the_program.py")) \
        and os.path.dirname(HERE) != HERE:
    HERE = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import the_program
import contextlib
import io
import shutil
import subprocess
import tempfile
import time

began = time.time()
vpm = the_program.load()
vpm.set_language("en")

done = 0
bad = []


def check(name, ok, extra=""):
    global done
    done += 1
    print("  %-58s %s %s" % (name, "ok" if ok else "FAIL", extra))
    if not ok:
        bad.append("%s [%s]" % (name, extra or "no numbers"))


PRESETS = [("Podcast_Single", "u1", False), ("Podcast_Multi", "u2", True)]
events, sent = [], []


class AxisReached(Exception):
    """Raised where the time axis would be measured: the run ends there."""


def offline(*_a, **_k):
    """The one road to auphonic.com, stood in for: it refuses."""
    events.append("curl")
    raise RuntimeError("auphonic.com is not asked in this test")


def single(audio, preset, _name, *_a, **_k):
    """One Singletrack production, written down; its result the upload."""
    sent.append(("single", vpm.channel_count(audio)))
    return audio


def multi(_key, _preset, _title, tracks, *_a, **_k):
    """One Multitrack production, written down; the uploads come back."""
    sent.append(("multi", len(tracks)))
    return dict((t["name"], t["axis"]) for t in tracks)


def axis(*_a, **_k):
    """The first step of the time axis: noted, and the run stops."""
    events.append("axis")
    raise AxisReached()


vpm._curl_call = offline
vpm.api_key_source = lambda *a, **k: ("FAKEKEY-0000", "store")
vpm.load_api_key = lambda *a, **k: ""
vpm.list_presets = lambda key: events.append("preset") or list(PRESETS)
vpm.check_preset = lambda *a, **k: []
vpm.run_single_production = single
vpm.run_multitrack_production = multi
vpm.verify_returned_tracks = lambda *a, **k: True
vpm.normalise_loudness = lambda *a, **k: (0.0, None)
vpm.align_cameras = axis

WORK = tempfile.mkdtemp(prefix="vpm_wide_")


def made(name, *args):
    """A few seconds of material, written by ffmpeg; its path."""
    path = os.path.join(WORK, name)
    subprocess.run(["ffmpeg", "-v", "error", "-y"] + list(args) + [path],
                   check=True)
    return path


TONE = "sine=frequency=%d:duration=3"
FOUR = made("Guest_4ch.wav",
            "-f", "lavfi", "-i", TONE % 220, "-f", "lavfi", "-i", TONE % 330,
            "-f", "lavfi", "-i", TONE % 440, "-f", "lavfi", "-i", TONE % 550,
            "-filter_complex", "[0][1][2][3]amerge=inputs=4", "-ar", "48000")
TWO = made("Guest_2ch.wav",
           "-f", "lavfi", "-i", TONE % 220, "-f", "lavfi", "-i", TONE % 330,
           "-filter_complex", "[0][1]amerge=inputs=2", "-ar", "48000")
CAMERA = made("WideCam.mp4",
              "-f", "lavfi", "-i", "smptebars=size=160x90:rate=25:duration=3",
              "-f", "lavfi", "-i", TONE % 330, "-ar", "48000", "-shortest")
# The four channels in two pairs, as the window hands them to its run
# when the tick joins channel 1 with 2 and 3 with 4.
PAIRS = []
for pair in ((0, 1), (2, 3)):
    PAIRS.append(vpm.split_target(FOUR, pair, WORK))
    vpm.split_channels(FOUR, pair, PAIRS[-1])
# Material, not program: the stop is about four channels, so the file
# has to have them, the stereo one and each pair two.
assert vpm.channel_count(FOUR) == 4 and vpm.channel_count(TWO) == 2
assert [vpm.channel_count(p) for p in PAIRS] == [2, 2]


def run(audios, videos, *switches):
    """The time base on *audios*: (return, events, sent, log).

    One recording asks a Singletrack preset, two a Multitrack one.
    """
    del events[:], sent[:]
    preset = "Podcast_Multi" if len(audios) > 1 else "Podcast_Single"
    args = vpm.build_argument_parser().parse_args(
        audios + videos + ["--auphonic-preset", preset,
                           "--out", WORK] + list(switches))
    args.auphonic_key = "FAKEKEY-0000"
    plan = [{"audio": audio, "blocks": [audio], "speakers": speaker,
             "camera": ""}
            for audio, speaker in zip(audios, ("Guest", "Presenter"))]
    kept, sys.stdin = sys.stdin, io.StringIO("")
    log = io.StringIO()
    try:
        with contextlib.redirect_stdout(log):
            code = vpm.build_common_timebase(args, plan, [], videos)
    except AxisReached:
        code = "axis"
    finally:
        sys.stdin = kept
    return code, list(events), list(sent), log.getvalue()


try:
    print("One recording of four channels")
    code, seen, up, log = run([FOUR], [CAMERA])
    check("with a picture it stops before the axis and the preset",
          code == 1 and seen == [] and up == [],
          "returned %r against 1, asked %s and sent %s, wanted neither"
          % (code, seen, up))
    code, seen, up, log = run([FOUR], [], "--lufs", "source")
    check("without one it stops before anything is sent",
          code == 1 and seen == [] and up == [],
          "returned %r against 1, asked %s and sent %s, wanted neither"
          % (code, seen, up))
    said = [line for line in log.splitlines() if "Guest_4ch.wav" in line]
    check("the stop names the file and its four channels",
          any("Guest_4ch.wav has 4 channels" in line for line in said),
          "lines naming the file: %s" % (said or "none"))
    code, seen, up, log = run([FOUR], [], "--without-auphonic")
    check("a run that sends nothing is not stopped by four channels",
          code == 0 and up == [],
          "returned %r against 0, sent %s" % (code, up))

    print("\nBeside a second recording, as a Multitrack production")
    code, seen, up, log = run([FOUR, TWO], [CAMERA])
    check("beside a second recording it stops before the axis too",
          code == 1 and seen == [] and up == [],
          "returned %r against 1, asked %s and sent %s, wanted neither"
          % (code, seen, up))
    code, seen, up, log = run(PAIRS, [CAMERA])
    check("cut into two pairs by the channel rows it goes on",
          code == "axis" and seen == ["preset", "axis"] and up == [],
          "returned %r against 'axis', asked %s and sent %s, wanted "
          "['preset', 'axis'] and nothing" % (code, seen, up))

    print("\nOne recording of two channels")
    code, seen, up, log = run([TWO], [])
    check("a stereo recording alone still goes up as one production",
          code == 0 and up == [("single", 2)],
          "returned %r against 0, sent %s, wanted [('single', 2)]"
          % (code, up))
except Exception as e:
    bad.append("the test ran into %s: %s" % (type(e).__name__, e))
finally:
    shutil.rmtree(WORK, True)

print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
