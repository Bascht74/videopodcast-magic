# -*- coding: utf-8 -*-
"""One rule for any channel count: is this pair stereo or two tracks?

The judgement is the same whether a file has two channels or eight, so
the test walks the cases a recorder actually produces: one channel, a
mono signal on both sides, two different signals, a tick that overrides
the proposal, an unused input, eight channels where every neighbour is
asked, an odd channel at the end, a pair in the middle, a hand that
corrects the proposal instead of restarting it, a video file, and a
file that cannot be read at all. What the tracks are called is asked
with them, and a section that reads a single judgement counts the
neighbours first, so a section that lost its material says that rather
than the consequence.
"""
import os
HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = os.environ.get("VPM_SCRIPT") or os.path.join(
    os.path.dirname(HERE), "videopodcast-magic.py")
import importlib.util, subprocess, sys, tempfile, time
spec = importlib.util.spec_from_file_location("vpm", SCRIPT)
vpm = importlib.util.module_from_spec(spec); sys.modules["vpm"] = vpm
spec.loader.exec_module(vpm)

T = tempfile.mkdtemp(prefix="channels_")
began = time.time()
done = 0
# Not "bad": section 9 needs that name for the file that is not a wav,
# and a counter overwritten by a path ends the run in a traceback.
error = []


def check(name, ok, extra=""):
    global done
    done += 1
    print("  %-58s %s %s" % (name, "ok" if ok else "FAIL", extra))
    if not ok:
        error.append("%s [%s]" % (name, extra or "no numbers"))


# Stand-ins for a judgement or a track that never came. They answer no
# question with a yes, so a list that came back short leaves a red line
# behind rather than a traceback -- and the closing count, the second
# net under this file, is printed either way.
NO_PAIR = (None, None, None, "")
NO_TRACK = (None, None, None)


def nth(seq, k, blank):
    """Item k of the list, or *blank* where the list is that short."""
    return seq[k] if k < len(seq) else blank


def build(name, parts, video=False):
    """Build a file whose channels are exactly what the parts say.

    A part is a frequency, 0 for a channel never plugged in, or "=" to
    repeat the one before it, which is mono on two sides. The samples
    are written here rather than fetched from ffmpeg, whose join filter
    reorders channels into the canonical layout, and channel order is
    the one thing this test is about.
    """
    import wave
    import numpy as np
    rate, seconds = 8000, 6
    t = np.arange(rate * seconds, dtype=np.float64) / rate
    rows, before = [], None
    for p in parts:
        if p == "=":
            p = before
        before = p
        rows.append(0.4 * np.sin(2 * np.pi * p * t) if p
                    else np.zeros_like(t))
    block = (np.stack(rows, axis=1) * 32767).astype("<i2")
    wav = os.path.join(T, os.path.splitext(name)[0] + ".wav")
    with wave.open(wav, "wb") as f:
        f.setnchannels(len(rows))
        f.setsampwidth(2)
        f.setframerate(rate)
        f.writeframes(block.tobytes())
    if not video:
        return wav
    out = os.path.join(T, name)
    subprocess.run(
        ["ffmpeg", "-v", "error", "-f", "lavfi", "-i",
         "testsrc=size=160x90:rate=25:duration=%d" % seconds,
         "-i", wav, "-map", "0:v", "-map", "1:a", "-c:v", "libx264",
         "-pix_fmt", "yuv420p", "-c:a", "pcm_s16le", "-y", out],
        check=True, capture_output=True)
    return out


def judge(path):
    f = vpm.channel_facts(path)
    return f, vpm.channel_joins(f), vpm.channel_tracks(f, "X")


print("1. One channel stays one track")
f, pairs, tracks = judge(build("mono.wav", [300]))
check("one channel counted", f["channels"] == 1, str(f["channels"]))
check("one track, named after the file",
      [t[1] for t in tracks] == ["X"], str(tracks))
check("the whole file, no channel picked",
      nth(tracks, 0, NO_TRACK)[0] == (), str(nth(tracks, 0, NO_TRACK)))

print("\n2. Two channels carrying the same signal are one stereo track")
f, pairs, tracks = judge(build("dual.wav", [300, "="]))
check("one neighbour judged", len(pairs) == 1,
      "%d neighbours judged, wanted 1" % len(pairs))
pair = nth(pairs, 0, NO_PAIR)
check("judged stereo", pair[1] is True, str(pair))
# The third field says the verdict rests on a measurement. A pair the
# program could not measure comes back False there and reads "not
# recognisable", and that is the answer this line keeps out.
check("and that is measured, not guessed", pair[2] is True,
      "certain %r, reason %r" % (pair[2], pair[3]))
check("one track out of it", len(tracks) == 1, str(tracks))
check("it holds both channels", nth(tracks, 0, NO_TRACK)[0] == (0, 1),
      str(nth(tracks, 0, NO_TRACK)[0]))

print("\n3. Two different channels are proposed as two tracks")
f, pairs, tracks = judge(build("two.wav", [300, 900]))
check("one neighbour judged", len(pairs) == 1,
      "%d neighbours judged, wanted 1" % len(pairs))
pair = nth(pairs, 0, NO_PAIR)
apart_verdict = pair[1:3]               # section 8 holds a video against it
check("judged separate", pair[1] is False, str(pair[1]))
check("the reason says why in plain words",
      "%" not in pair[3] and len(pair[3].split()) >= 4,
      "%d words, wanted 4 and no %%: %r" % (len(pair[3].split()), pair[3]))
check("two tracks", len(tracks) == 2, str([t[1] for t in tracks]))
check("numbered by channel",
      [t[1] for t in tracks] == ["X Channel 1", "X Channel 2"],
      str([t[1] for t in tracks]))

print("\n4. The person can override the proposal")
f = vpm.channel_facts(build("two2.wav", [300, 900]))
joined = vpm.channel_tracks(f, "X", {0: True})
check("forced together -> one track", len(joined) == 1, str(joined))
check("holding both channels", nth(joined, 0, NO_TRACK)[0] == (0, 1),
      str(nth(joined, 0, NO_TRACK)[0]))
f2 = vpm.channel_facts(build("dual2.wav", [300, "="]))
apart = vpm.channel_tracks(f2, "X", {0: False})
check("forced apart -> two tracks", len(apart) == 2, str(apart))

print("\n5. An unused recorder input is found and set aside")
f, pairs, tracks = judge(build("four.wav", [300, 0, 700, 1300]))
check("four channels", f["channels"] == 4, str(f["channels"]))
check("three neighbours judged", len(pairs) == 3,
      "%d neighbours judged, wanted 3" % len(pairs))
check("exactly one silent", sum(1 for x in f["silent"] if x) == 1,
      str(f["silent"]))
check("it is the second", nth(f["silent"], 1, None) is True,
      str(f["silent"]))
check("three tracks are left",
      len([t for t in tracks if not t[2]]) == 3,
      str([t[1] for t in tracks if not t[2]]))
check("the empty one is marked, not dropped",
      len(tracks) == 4 and any(t[2] for t in tracks), str(tracks))
pair = nth(pairs, 0, NO_PAIR)
check("a pair with an empty channel is not stereo",
      pair[1] is False and pair[2] is True, str(pair))

print("\n6. Eight channels: every neighbour is asked")
f, pairs, tracks = judge(build("eight.wav",
                               [300, "=", 500, 900, 1100, "=", 1500, 1900]))
# Seven neighbours, not four pairs: 2 and 3 can be the pair just as
# well as 1 and 2, so every neighbour is measured and the
# non-overlapping set is picked afterwards.
check("seven neighbours judged", len(pairs) == 7,
      "%d neighbours judged, wanted 7" % len(pairs))
check("channels 1 and 2 are one", nth(pairs, 0, NO_PAIR)[1] is True,
      str(nth(pairs, 0, NO_PAIR)))
check("2 and 3 are not -- 2 is already spoken for anyway",
      nth(pairs, 1, NO_PAIR)[1] is False, str(nth(pairs, 1, NO_PAIR)))
check("5 and 6 are one", nth(pairs, 4, NO_PAIR)[1] is True,
      str(nth(pairs, 4, NO_PAIR)))
check("six tracks come out", len(tracks) == 6,
      str([t[1] for t in tracks]))
check("the stereo ones carry their pair",
      nth(tracks, 0, NO_TRACK)[0] == (0, 1)
      and nth(tracks, 3, NO_TRACK)[0] == (4, 5),
      str([t[0] for t in tracks]))
check("and they are named after their channels",
      nth(tracks, 0, NO_TRACK)[1] == "X Channel 1+2"
      and nth(tracks, 3, NO_TRACK)[1] == "X Channel 5+6",
      str([t[1] for t in tracks]))

print("\n7. An odd channel at the end stands on its own")
f, pairs, tracks = judge(build("three.wav", [300, "=", 900]))
check("two neighbours judged", len(pairs) == 2,
      "%d neighbours judged, wanted 2" % len(pairs))
check("the first two belong together", nth(pairs, 0, NO_PAIR)[1] is True,
      str(nth(pairs, 0, NO_PAIR)))
check("the third does not go with them",
      nth(pairs, 1, NO_PAIR)[1] is False, str(nth(pairs, 1, NO_PAIR)))
check("two tracks", len(tracks) == 2, str([t[1] for t in tracks]))
check("and the last one stands alone",
      nth(tracks, 1, NO_TRACK)[0] == (2,), str(nth(tracks, 1, NO_TRACK)))

print("\n7b. Channels 2 and 3 can be the pair")
f, pairs, tracks = judge(build("middle.wav", [300, 900, "=", 1500]))
check("three neighbours judged", len(pairs) == 3,
      "%d neighbours judged, wanted 3" % len(pairs))
check("the middle neighbour is the stereo one",
      nth(pairs, 1, NO_PAIR)[1] is True, str(nth(pairs, 1, NO_PAIR)))
check("three tracks", len(tracks) == 3, str([t[1] for t in tracks]))
check("and the pair is 2 and 3",
      [t[0] for t in tracks] == [(0,), (1, 2), (3,)],
      str([t[0] for t in tracks]))
check("named accordingly",
      nth(tracks, 1, NO_TRACK)[1] == "X Channel 2+3",
      str(nth(tracks, 1, NO_TRACK)[1]))

print("\n7c. Ticking one channel takes the tick from the next")
# Channels 1, 2 and 3 carry the same thing, so 1+2 and 2+3 both look
# like a pair. They cannot both be one, so the left one wins.
f = vpm.channel_facts(build("middle2.wav", [300, "=", "=", 1500]))
check("without a hand the left pair wins",
      vpm.joined_channels(f) == {0: True}, str(vpm.joined_channels(f)))
by_hand = vpm.joined_channels(f, {0: False, 1: True})
check("ticking channel 2 makes 2 and 3 the pair",
      by_hand == {1: True}, str(by_hand))
check("so 1 and 4 stand alone",
      [t[0] for t in vpm.channel_tracks(f, "X", {0: False, 1: True})]
      == [(0,), (1, 2), (3,)],
      str([t[0] for t in vpm.channel_tracks(f, "X", {0: False, 1: True})]))

print("\n7d. A hand corrects the proposal, it does not restart it")
# Six channels, proposed as the pairs 1+2, 3+4, 5+6. Taking one apart
# must not rerun the proposal over the freed channels: undoing 3+4
# would then create 4+5, one click and a second change nobody asked for.
alike = {"channels": 6, "readable": True, "silent": [False] * 6,
         "level": [-20.0] * 6, "pair_same": [0.99] * 5,
         "pair_zero": [0.9, 0.1, 0.9, 0.1, 0.9],
         "pair_apart": [0.0] * 5}
check("the proposal pairs them up from the left",
      vpm.joined_channels(alike) == {0: True, 2: True, 4: True},
      str(vpm.joined_channels(alike)))
check("taking one apart takes exactly that one apart",
      vpm.joined_channels(alike, {2: False}) == {0: True, 4: True},
      str(vpm.joined_channels(alike, {2: False})))
check("and nothing moves up into the gap",
      3 not in vpm.joined_channels(alike, {2: False}),
      "3 joined %r, wanted False, out of %s"
      % (3 in vpm.joined_channels(alike, {2: False}),
         vpm.joined_channels(alike, {2: False})))
check("putting one together frees both its neighbours",
      vpm.joined_channels(alike, {1: True}) == {1: True, 4: True},
      str(vpm.joined_channels(alike, {1: True})))
check("two hands, two changes, no more",
      vpm.joined_channels(alike, {0: False, 2: False}) == {4: True},
      str(vpm.joined_channels(alike, {0: False, 2: False})))
check("a tick on a channel that has none does nothing",
      vpm.joined_channels(alike, {9: True}) == {0: True, 2: True, 4: True},
      str(vpm.joined_channels(alike, {9: True})))

print("\n8. A video file is judged exactly the same way")
f, pairs, tracks = judge(build("cam.mov", [300, 900], video=True))
check("two channels found in the video", f["channels"] == 2,
      str(f["channels"]))
check("one neighbour judged", len(pairs) == 1,
      "%d neighbours judged, wanted 1" % len(pairs))
pair = nth(pairs, 0, NO_PAIR)
check("same judgement as for the audio file",
      pair[1:3] == apart_verdict,
      "video %s, audio %s" % (pair[1:3], apart_verdict))
check("two tracks", len(tracks) == 2, str([t[1] for t in tracks]))

print("\n9. An unreadable file says so instead of inventing channels")
bad = os.path.join(T, "bad.wav")
open(bad, "wb").write(b"not a wav at all")
f = vpm.channel_facts(bad)
check("not readable", f["readable"] is False, str(f))
check("no pairs judged", vpm.channel_joins(f) == [], str(vpm.channel_joins(f)))
check("one track, so the file does not vanish",
      len(vpm.channel_tracks(f, "X")) == 1,
      "%d tracks, wanted 1: %s" % (len(vpm.channel_tracks(f, "X")),
                                   vpm.channel_tracks(f, "X")))

print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(error) if error else "ALL OK")
sys.exit(1 if error else 0)
