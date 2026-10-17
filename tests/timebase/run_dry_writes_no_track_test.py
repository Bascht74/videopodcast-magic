# -*- coding: utf-8 -*-
"""A dry run writes no track onto the axis unless a reader past the check does.

The interview fixture, a dry run per section in this process, every track the
run writes onto the axis counted. Without a key and with no separation
it writes none and still ends with 0. With a key it writes each track,
because what it says would go up to auphonic.com is read off them, and
it says so. Where the microphones hear each other too well for the
separation, it writes each track and keeps the mix made of them for the
run after; where they stand far apart, the separation needs no mix and
it writes none. Nothing reaches auphonic.com: the key is made up, the
preset a stand-in, the preflight off. The limit: the tracks written are
counted at the one function that writes them, not on the disc.
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
import glob
import io
import shutil
import tempfile
import time
import the_program
from fixture_root import fixture

WORK = tempfile.mkdtemp(prefix="vpm_drytracks_")
os.environ["VPM_CACHE"] = os.path.join(WORK, "cache")
vpm = the_program.load()
vpm.set_language("en")
vpm.list_presets = lambda key: []

began = time.time()
done = 0
bad = []


def check(name, ok, extra=""):
    global done
    done += 1
    print("  %-58s %s %s" % (name, "ok" if ok else "FAIL", extra))
    if not ok:
        bad.append("%s [%s]" % (name, extra or "no numbers"))


def stop():
    """Nothing further can be asked, so count what there is and go."""
    shutil.rmtree(WORK, ignore_errors=True)
    print("\n%d checks in %.2f s" % (done, time.time() - began))
    print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
    sys.exit(1 if bad else 0)


MEDIA = fixture("interview")
FILES = sorted(glob.glob(os.path.join(MEDIA, "*.wav"))
               + glob.glob(os.path.join(MEDIA, "*.mov")))
# One track per speaker: three recordings, one of them in three blocks.
TRACKS = 3
if len(FILES) < 6:
    print("SKIPPED: no interview fixture -- tests/fixtures.sh builds it "
          "under VPM_FIXTURES (looked in %s)" % MEDIA)
    stop()

written = []
real_place = vpm.place_track_on_axis


def counted_place(source, target, *rest, **named):
    """The one function that writes a track onto the axis, counted."""
    written.append(target)
    return real_place(source, target, *rest, **named)


vpm.place_track_on_axis = counted_place


def dry_run(name, extra=()):
    """A dry run over the fixture, its own store: (code, what it said)."""
    del written[:]
    os.environ["VPM_CACHE"] = os.path.join(WORK, "cache_" + name)
    argv = (["videopodcast_magic.py"] + FILES
            + ["--out", os.path.join(WORK, "out"), "--dry-run",
               "--no-metrics", "--no-speech-recognition",
               "--no-transcript-file", "--no-preflight"] + list(extra))
    ap = vpm.build_argument_parser()
    args = ap.parse_args(vpm.time_values_joined(list(argv[1:])))
    said, old = io.StringIO(), (sys.argv, sys.stdout)
    sys.argv, sys.stdout = list(argv), said
    try:
        code = vpm.run_from_command_line(args, ap)
    except Exception as e:
        code = "crashed: %r" % e
    finally:
        sys.argv, sys.stdout = old
    return code, said.getvalue()


try:
    print("1. Without a key, and no separation")
    vpm.load_api_key = lambda: ""
    code, log = dry_run("plain", ["--without-auphonic"])
    check("a dry run with nobody to read its tracks ends with 0",
          code == 0, "return code %r, the last it said: %r"
          % (code, log[-160:]))
    check("and writes not one track onto the axis",
          len(written) == 0, "%d tracks written, %d expected"
          % (len(written), 0))

    print("\n2. With a key: what would go up is read off the tracks")
    vpm.load_api_key = lambda: "not-a-key-only-a-test"
    vpm.choose_preset = lambda *a, **k: ("uuid", "Stand-in preset")
    code, log = dry_run("keyed")
    upload = vpm.T('  To upload:   %s').split("%s")[0]
    line = next((x for x in log.splitlines() if x.startswith(upload)), "")
    check("a dry run with a key writes every track onto the axis",
          code == 0 and len(written) == TRACKS,
          "return code %r, %d tracks written, %d expected; the last it "
          "said: %r" % (code, len(written), TRACKS, log[-160:]))
    check("and says how much of them would go up",
          line and not line.endswith(vpm.as_data_size(0.0)),
          "the upload line reads %r" % line)

    print("\n3. Microphones too close to tell apart: the separation mixes")
    vpm.load_api_key = lambda: ""
    vpm.SPEAKER_SPLIT_OFF = False
    vpm.speaker_split_available = lambda deep=False: True
    vpm.microphones_apart_db = lambda paths: 3.0
    code, log = dry_run("mixed", ["--without-auphonic"])
    mixes = glob.glob(os.path.join(WORK, "cache_mixed", "*", "speakers",
                                   "mix_*.wav"))
    check("a dry run mixing the microphones writes every track first",
          code == 0 and len(written) == TRACKS,
          "return code %r, %d tracks written, %d expected; the last it "
          "said: %r" % (code, len(written), TRACKS, log[-160:]))
    check("and keeps the mix it made of them for the run after",
          len(mixes) == 1, "%d mixes kept in the store, 1 expected"
          % len(mixes))

    print("\n4. Microphones far apart: the separation needs no mix")
    vpm.load_api_key = lambda: ""
    vpm.SPEAKER_SPLIT_OFF = False
    vpm.speaker_split_available = lambda deep=False: True
    # Well above the program's own limit, wherever that limit stands.
    far = vpm.MICROPHONES_APART_DB + 20.0
    vpm.microphones_apart_db = lambda paths: far
    code, log = dry_run("apart", ["--without-auphonic"])
    check("a dry run separating microphones far apart writes no track",
          code == 0 and len(written) == 0,
          "return code %r, %d tracks written, %d expected at %.1f dB apart "
          "against a limit of %.1f dB; the last it said: %r"
          % (code, len(written), 0, far, vpm.MICROPHONES_APART_DB,
             log[-160:]))
except Exception as e:
    # A crash ends the runs, not the count: it goes out through stop().
    bad.append("the runs crashed [%r]" % e)
    print("  the runs crashed: %r" % e)
stop()
