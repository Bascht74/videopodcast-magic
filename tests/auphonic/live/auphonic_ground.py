# -*- coding: utf-8 -*-
"""The ground the Auphonic tests stand on: the gate, the key, a title of
their own, and the sweep that takes their productions away again.

These tests talk to auphonic.com, so they cannot go into the suite: the
suite reaches nothing outside, and a run without the network or without
a key would be red for a reason that is not a fault. They live beside it
and are started by auphonic.sh, which lets them through only when it was
given the word -- --online for the ones that cost nothing, and
--spend-credit as well for the ones that start a production. Started
any other way, each one leaves itself out and says how to start it.

The key is the program's own: AUPHONIC_TOKEN where that is set, the
credential store otherwise, read through the program's functions at the
moment it is needed. It is never printed, written or put on a command
line; the program hands it to curl in a file of its own.

Run as a script, this file is what auphonic.sh calls: --probe says
whether a key is there and from where, --sweep deletes what the tests
made at auphonic.com -- productions whose title has the tests' shape,
and nothing else.
"""
import json
import os
import random
import re
import struct
import subprocess
import sys
import wave

HERE = os.path.dirname(os.path.abspath(__file__))
# tests/, where the helpers and state/ lie; this file stands two folders
# under it, and finds it the way every test in the suite does.
TESTS = HERE
while not os.path.isfile(os.path.join(TESTS, "the_program.py")) \
        and os.path.dirname(TESTS) != TESTS:
    TESTS = os.path.dirname(TESTS)
sys.path.insert(0, TESTS)
import the_program

# The two words auphonic.sh sets, and only after it was given them.
ONLINE = "VPM_LIVE_AUPHONIC"
CREDIT = "VPM_LIVE_AUPHONIC_CREDIT"
STARTED = "cd tests && bash auphonic.sh --online"
# A key nobody holds, for the test that asks what a refusal looks like.
# The same shape a stand-in in the suite refuses, which is why it stands
# here once and is read from here.
REFUSED_KEY = "not-a-key-only-a-test"
# The shape of a title the tests give their own productions, and nothing
# else -- the same shape the Resolve tests give their projects. The sweep
# deletes what this matches, so it is narrow rather than convenient.
TEST_TITLE = re.compile(r"^vpm-test-[a-z0-9]+-[0-9]+-[0-9a-f]{4}$")


def leave_out(why):
    """Say out loud that nothing was checked, and stop.

    Not sys.exit(0): a test that bows out and returns 0 cannot be told
    from one that checked everything. auphonic.sh reads the 2.
    """
    print("SKIPPED: %s" % why)
    sys.exit(2)


def gate(spends=False):
    """Go on only where auphonic.sh was given the word; leave out otherwise."""
    if os.environ.get(ONLINE) != "1":
        leave_out("this test talks to auphonic.com and is started only on "
                  "consent -- %s" % STARTED)
    if spends and os.environ.get(CREDIT) != "1":
        leave_out("this test starts a production and spends credit at "
                  "auphonic.com -- only after the owner's OK: %s "
                  "--spend-credit" % STARTED)


def program():
    """Load the program under test, in English."""
    vpm = the_program.load()
    vpm.set_language("en")
    return vpm


def the_key(vpm):
    """(the key, where it came from), or leave the test out saying why.

    VPM_SILENT makes the credential store refuse, so it is lifted for
    the one reading and put back at once. The key stays in memory.
    """
    was = os.environ.pop("VPM_SILENT", None)
    try:
        key, origin = vpm.api_key_source(None)
    finally:
        if was is not None:
            os.environ["VPM_SILENT"] = was
    key = (key or "").strip()
    if not key:
        leave_out("no key for auphonic.com on this machine -- remember it "
                  "once in the window's settings, then %s" % STARTED)
    return key, origin


def a_test_title(what):
    """A title of the tests' own shape, for one production."""
    return "vpm-test-%s-%d-%04x" % (what, os.getpid(),
                                     random.randrange(0x10000))


def a_preset(vpm, key, multitrack=False):
    """The uuid of a preset of the right kind, or leave the test out.

    VPM_LIVE_PRESET names one by its uuid; otherwise the first one the
    account holds of that kind. Its name is not printed: a preset is
    named after somebody's production often enough.
    """
    wanted = os.environ.get("VPM_LIVE_PRESET", "").strip()
    presets = vpm.presets_for_mode(key, multitrack)
    for name, uuid, mark in presets:
        if uuid and (not wanted or uuid == wanted):
            return uuid
    leave_out("no %s preset in this account%s -- create one at "
              "auphonic.com, or name one with VPM_LIVE_PRESET"
              % ("multitrack" if multitrack else "single-track",
                 " with the uuid VPM_LIVE_PRESET names" if wanted else ""))


def tone(path, seconds, channels):
    """A WAV with a different tone in each channel, so stereo is stereo."""
    rate = 48000
    with wave.open(path, "wb") as w:
        w.setnchannels(channels)
        w.setsampwidth(2)
        w.setframerate(rate)
        frames = bytearray()
        for i in range(int(seconds * rate)):
            for c in range(channels):
                # 220 Hz on the left, 330 on the right, in a square wave:
                # no import beyond the standard library.
                half = rate // (440 + 220 * c)
                frames += struct.pack("<h", 6000 if (i // half) % 2 else -6000)
        w.writeframes(bytes(frames))
    return path


def measured(path):
    """(seconds, channels) of an audio file, asked of ffprobe directly.

    Not through the program: what it says about a file is what is being
    judged, so the measure takes another road.
    """
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-select_streams", "a:0",
         "-show_entries", "stream=channels:format=duration", "-of", "json",
         path], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    d = json.loads(out.stdout.decode("utf-8", "replace") or "{}")
    streams = d.get("streams") or [{}]
    return (float((d.get("format") or {}).get("duration") or 0),
            int(streams[0].get("channels") or 0))


def productions(vpm, key):
    """Every production the account lists: (title, uuid)."""
    d = vpm._parse_json(vpm._curl_call(
        key, [vpm.AUPHONIC + "/api/productions.json?limit=100"]))
    return [(((p.get("metadata") or {}).get("title") or ""), p.get("uuid"))
            for p in (d.get("data") or [])]


def delete(vpm, key, uuid):
    """Delete one production. True when auphonic.com said yes."""
    d = vpm._parse_json(vpm._curl_call(
        key, ["-X", "DELETE", vpm.AUPHONIC + "/api/production/%s.json" % uuid])
        or "{}")
    return d.get("status_code") in (200, 204, None)


def swept(vpm, key):
    """Delete every production of the tests' shape; return how many went."""
    gone = 0
    for title, uuid in productions(vpm, key):
        if uuid and TEST_TITLE.match(title) and delete(vpm, key, uuid):
            gone += 1
    return gone


if __name__ == "__main__":
    vpm = program()
    if "--probe" in sys.argv:
        # Where the key came from, never the key.
        was = os.environ.pop("VPM_SILENT", None)
        key, origin = vpm.api_key_source(None)
        if was is not None:
            os.environ["VPM_SILENT"] = was
        print("  key for auphonic.com: %s"
              % ({"environment": "from AUPHONIC_TOKEN",
                  "store": "from the credential store"}.get(origin)
                 if key else "none found"))
        sys.exit(0 if key else 3)
    if "--sweep" in sys.argv:
        key, origin = the_key(vpm)
        try:
            print("  swept at auphonic.com: %d productions of the tests' "
                  "own shape" % swept(vpm, key))
        except RuntimeError as e:
            print("  the sweep could not ask auphonic.com: %s"
                  % " ".join(str(e).split())[:200])
