# -*- coding: utf-8 -*-
"""Microphones that hear each other are mixed and taken apart by voice.

The switch, the source and the naming, in that order: how far apart the
microphones stand, whether the separation is refused or handed a mix of
them all, that the mix is a plain sum and nothing is levelled first,
and that the voices are named after the microphone that is left when
the recording level is taken out. Last a guard: where the microphones
can be told apart the cheap route stays untouched. The model itself is
not run -- the voices are handed in with their true times.
"""
import os
HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = os.environ.get("VPM_SCRIPT") or os.path.join(
    os.path.dirname(HERE), "videopodcast-magic.py")
import importlib.util
import shutil
import sys
import tempfile
import time
import wave
import numpy as np
spec = importlib.util.spec_from_file_location("vpm", SCRIPT)
vpm = importlib.util.module_from_spec(spec); sys.modules["vpm"] = vpm
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


#------------------------------------------------------------- Material
#
# Two people taking turns, and the shape that was measured on a real
# interview: the two recorders are set 11 dB apart, and the bleed of
# the quieter one into the louder one's microphone is almost exactly as
# loud as his own recording. That is what makes "the loudest microphone
# wins" pick the wrong one, and it is the whole point of the material.
#
#   Guest      speaks loudly into a recorder turned up
#   Presenter  speaks into one turned down 11 dB, and stands 0.5 dB
#              louder in the Guest's microphone than in his own
#
# Filtered noise rather than speech: nothing here listens for words,
# and the levels are what everything below reads.

WORK = tempfile.mkdtemp(prefix="vpm_close_")
SR = 8000
LENGTH = 60.0
TURNS = {"Guest": [(1.0, 6.0), (13.0, 19.0), (26.0, 32.0), (39.0, 45.0),
                   (52.0, 58.0)],
         "Presenter": [(7.0, 12.0), (20.0, 25.0), (33.0, 38.0),
                       (46.0, 51.0)]}
# Own voice, and the same voice in the other microphone. Measured in
# dB, so the table below can be read against the one in the note.
GAIN = {"Guest": {"Guest": 0.0, "Presenter": -21.0},
        "Presenter": {"Guest": -10.5, "Presenter": -11.0}}
# The same room, far apart: what a well-placed pair of microphones
# does, and the guard at the end runs on this.
APART = {"Guest": {"Guest": 0.0, "Presenter": -31.0},
         "Presenter": {"Guest": -31.0, "Presenter": 0.0}}


def voice_of(who):
    """One person's speech, as filtered noise in their turns."""
    r = np.random.RandomState(7 + len(who))
    x = np.zeros(int(LENGTH * SR))
    for a, b in TURNS[who]:
        i, j = int(a * SR), int(b * SR)
        piece = r.normal(0, 0.25, j - i)
        # A little shaping, so the level moves the way a voice does.
        w = np.arange(j - i) / float(SR)
        x[i:j] = piece * (0.6 + 0.4 * np.sin(2 * np.pi * 2.7 * w))
    return x


SPOKEN = dict((who, voice_of(who)) for who in TURNS)


def write_tracks(gain, prefix, levelled=False):
    """One file per microphone: own voice plus the neighbour's, as set.

    With *levelled* every track is brought to the same loudness before
    it is written -- what the mix would be built out of if it were
    levelled first, so the check below has something to hold against.
    """
    out = []
    r = np.random.RandomState(11)
    for mic in ("Guest", "Presenter"):
        x = sum(SPOKEN[who] * (10.0 ** (gain[who][mic] / 20.0))
                for who in SPOKEN)
        # Room noise, so the noise floor is not digital silence: the
        # level route reads its floor off the quiet blocks.
        x = x + r.normal(0, 0.0008, len(x)) * (
            10.0 ** (gain["Presenter"][mic] / 20.0) if mic == "Presenter"
            else 1.0)
        if levelled:
            x = 0.1 * x / max(1e-9, float(np.percentile(np.abs(x), 95)))
        path = os.path.join(WORK, "%s_%s.wav" % (prefix, mic))
        with wave.open(path, "wb") as f:
            f.setnchannels(1)
            f.setsampwidth(2)
            f.setframerate(SR)
            f.writeframes((np.clip(x, -1, 1) * 32000).astype("<i2").tobytes())
        out.append((mic, path))
    return out


CLOSE = write_tracks(GAIN, "close")
FAR = write_tracks(APART, "far")
LEVELLED = write_tracks(GAIN, "levelled", levelled=True)
VOICES = [("SPEAKER_00", TURNS["Guest"]),
          ("SPEAKER_01", TURNS["Presenter"])]


def grid_of(tracks):
    """The level grid of one reading, as speakers_from_tracks hands it out."""
    box = []
    vpm.speakers_from_tracks([(n, p, 0.0) for n, p in tracks], rate=SR,
                             grid=box)
    return box


print("1. How far apart the microphones really stand")
close_db = vpm.microphones_apart_db([p for _n, p in CLOSE])
check("microphones that hear each other are under the limit",
      close_db is not None and close_db < vpm.MICROPHONES_APART_DB,
      "%s dB against a limit of %.1f dB"
      % ("none" if close_db is None else "%.1f" % close_db,
         vpm.MICROPHONES_APART_DB))
far_db = vpm.microphones_apart_db([p for _n, p in FAR])
check("microphones that can be told apart are over it",
      far_db is not None and far_db >= vpm.MICROPHONES_APART_DB,
      "%s dB against a limit of %.1f dB"
      % ("none" if far_db is None else "%.1f" % far_db,
         vpm.MICROPHONES_APART_DB))
check("the limit is the measured 20 dB",
      vpm.MICROPHONES_APART_DB == 20.0,
      "MICROPHONES_APART_DB %r dB against 20.0 dB"
      % (vpm.MICROPHONES_APART_DB,))


print("\n2. Refused, or handed a mix of them all")
asked = []


def a_mix(chosen):
    asked.append(list(chosen))
    return os.path.join(WORK, "themix.wav")


paths = [p for _n, p in CLOSE]
under = vpm.speaker_source_pick(paths, [], apart_db=3.0, mix=a_mix)
check("under the limit the separation is not refused any more",
      under == (os.path.join(WORK, "themix.wav"), "microphones mixed"),
      "%r against a mix and 'microphones mixed'" % (under[1],))
check("and it is offered every microphone, not one of them",
      asked and sorted(asked[-1]) == sorted(paths),
      "%d files offered, wanted %d" % (len(asked[-1]) if asked else 0,
                                       len(paths)))
del asked[:]
over = vpm.speaker_source_pick(paths, [], apart_db=31.0, mix=a_mix)
check("over the limit it stands out of the way as before",
      over == ("", "several microphones"),
      "%r against ('', 'several microphones')" % (over,))
check("and no mix is built there at all",
      asked == [], "%d mixes asked for, wanted 0" % len(asked))
del asked[:]
plain = vpm.speaker_source_pick(paths, [], mix=a_mix)
check("with nothing measured it mixes nothing either",
      plain == ("", "several microphones") and asked == [],
      "%r and %d mixes asked for, wanted ('', 'several microphones') "
      "and 0" % (plain, len(asked)))
nothing = vpm.speaker_source_pick(paths, [], apart_db=3.0,
                                  mix=lambda chosen: "")
check("a mix that could not be made falls back to standing out",
      nothing == ("", "several microphones"),
      "%r against ('', 'several microphones')" % (nothing,))


print("\n3. The mix is the plain sum, and nothing is levelled")
MIXES = os.path.join(WORK, "mixes")
os.makedirs(MIXES, exist_ok=True)
mixed = vpm.speaker_mix_file(paths, ["one", "two"], folder=MIXES)
check("a mix is made of the two microphones", bool(mixed) and
      os.path.exists(mixed), "%r" % mixed)
if mixed:

    def apart_in(path):
        """How far the two speakers stand apart inside one mix, in dB."""
        x = vpm.decode_audio(path, rate=SR)

        def loud(segs):
            got = np.concatenate([x[int(a * SR):int(b * SR)]
                                  for a, b in segs])
            return 20.0 * np.log10(max(float(np.sqrt(
                (got.astype(np.float64) ** 2).mean())), 1e-12))

        return loud(TURNS["Guest"]) - loud(TURNS["Presenter"])

    # The Guest was recorded 11 dB louder than the Presenter, and in a
    # plain sum he stays louder. Levelling each track first is what
    # flattens that -- and measured on a real interview it costs 1.6
    # points of recall, because the same voice then stands equally loud
    # in every track and one near recording has become three copies.
    step = apart_in(mixed)
    flat = apart_in(vpm.speaker_mix_file([p for _n, p in LEVELLED],
                                         ["levelled"], folder=MIXES))
    check("the two speakers stand apart in the mix as they were recorded",
          step >= 4.0, "%.1f dB apart, wanted 4.0 dB or more" % step)
    check("while levelling each track first would flatten them",
          abs(flat) <= 1.5,
          "levelled first they are %.1f dB apart, against %.1f dB in the "
          "plain sum" % (flat, step))
    check("the mix is one channel at the rate the model hears",
          vpm.kept_channels(mixed) == 1,
          "%d channels against 1" % vpm.kept_channels(mixed))
    again = vpm.speaker_mix_file(paths, ["one", "two"], folder=MIXES)
    check("the same material gives the same file, not a new one",
          again == mixed, "%r against %r" % (again, mixed))
    other = vpm.speaker_mix_file(paths, ["one", "three"], folder=MIXES)
    check("other material gives another file",
          other != mixed, "%r against %r" % (other, mixed))


print("\n4. The naming takes the recording level out")
box = grid_of(CLOSE)
check("the reading hands out its levels rather than being made twice",
      len(box) == 1 and box[0]["level"].shape[0] == 2,
      "%d grids, %s" % (len(box),
                        box[0]["level"].shape if box else "none"))
g = box[0]
rows = vpm.voices_by_level(VOICES, g["names"], g["level"], g["block"],
                           g["begin"])
got = dict((voice, mic) for voice, mic, _l, _d in rows)
check("both voices are named", len(rows) == 2, str(got))
check("and each one after the microphone it spoke into",
      got == {"SPEAKER_00": "Guest", "SPEAKER_01": "Presenter"},
      "%s against {'SPEAKER_00': 'Guest', 'SPEAKER_01': 'Presenter'}" % got)
check("each of them well past the limit of 1.0 dB",
      all(d >= vpm.VOICE_LEVEL_MARGIN_DB for _v, _m, _l, d in rows),
      "margins %s dB against %.1f dB"
      % ([d for _v, _m, _l, d in rows], vpm.VOICE_LEVEL_MARGIN_DB))

# The counter-case, and without it the check above says nothing: on
# this very material the simple rule really does lose the quiet one.
level, names, block = g["level"], g["names"], g["block"]
loudest = {}
for name, segs in VOICES:
    want = np.zeros(level.shape[1], dtype=bool)
    for a, b in segs:
        want[int((a - g["begin"]) / block):int((b - g["begin"]) / block)] = True
    loudest[name] = names[int(np.argmax(
        [np.median(level[m][want]) for m in range(len(names))]))]
check("while the loudest microphone puts both of them on one",
      loudest["SPEAKER_00"] == loudest["SPEAKER_01"] == "Guest",
      "%s -- and two voices on one microphone name neither" % loudest)
# And the other half of the reason: on microphones this close the
# tracks no longer say who is speaking at all. The truth here is 29 s
# and 20 s; the level route hears both of them talking throughout.
close_rows = vpm.speakers_from_tracks([(n, p, 0.0) for n, p in CLOSE],
                                      rate=SR)
heard_s = dict((n, sum(b - a for a, b in s)) for n, s in close_rows)
check("the tracks alone say both of them talk nearly throughout",
      all(heard_s[n] > 40.0 for n in ("Guest", "Presenter")),
      "%s s of speech against a truth of 29.0 and 20.0 s"
      % {n: round(v, 1) for n, v in heard_s.items()})
check("so the old rule names nobody, and nobody gets a camera",
      vpm.which_microphone(VOICES, close_rows) == [],
      "%s, wanted nothing said"
      % (vpm.which_microphone(VOICES, close_rows),))

# A voice with no microphone of its own: every one hears it alike.
third = [(a, a + 0.4) for a, _b in TURNS["Guest"]] + [
    (a, a + 0.4) for a, _b in TURNS["Presenter"]]
crowd = vpm.voices_by_level(VOICES + [("SPEAKER_02", sorted(third))],
                            g["names"], g["level"], g["block"], g["begin"])
check("three voices against two microphones say nothing at all",
      crowd == [], "%d named, wanted 0" % len(crowd))
# A separation placed past the end of the reading is refused too, and
# the guard in voices_by_level says so -- but it is not checked here:
# with nothing to read the arithmetic comes out as "not a number" and
# refuses on its own, so a check could not tell the two apart.


print("\n5. The voices come out under the names of the tracks")
voices, lines = vpm.name_voices_by_microphone(VOICES, box)
check("the labels are gone and the track names are there",
      sorted(n for n, _s in voices) == ["Guest", "Presenter"],
      str([n for n, _s in voices]))
check("the passages are the ones that went in",
      [s for _n, s in voices] == [s for _n, s in VOICES],
      "%d and %d passages" % (len(voices[0][1]), len(voices[1][1])))
check("and the log says which microphone decided, with the number",
      len(lines) == 2 and all("dB ahead" in line for line in lines),
      "%s" % lines)
# A nameless voice has no camera behind it, so a cut built out of them
# would stand on the wide shot from beginning to end -- worse than the
# tracks, badly as those do here. So the voices are let go instead.
kept, said = vpm.name_voices_by_microphone(VOICES, [])
check("voices nobody can name are let go, not carried nameless",
      kept == [], "%s came back, wanted nothing" % ([n for n, _s in kept],))
check("and the log says the tracks answer instead",
      len(said) == 1 and "tracks are measured instead" in said[0],
      "%s" % said)


print("\n6. Where the microphones can be told apart, nothing moves")
far_grid = grid_of(FAR)
far_rows = vpm.speakers_from_tracks([(n, p, 0.0) for n, p in FAR], rate=SR)
held = dict((n, sum(b - a for a, b in s)) for n, s in far_rows)
check("both well-placed microphones report their own speaker and no more",
      all(18.0 <= held.get(n, 0) <= 33.0 for n in ("Guest", "Presenter")),
      "%s s of speech against a truth of 29.0 and 20.0 s"
      % {n: round(v, 1) for n, v in held.items()})
check("and the old rule names them from the tracks alone",
      len(vpm.which_microphone(VOICES, far_rows)) == 2,
      "%s" % (vpm.which_microphone(VOICES, far_rows),))
check("so the run there never asks for a mix",
      vpm.speaker_source_pick([p for _n, p in FAR], [],
                              apart_db=far_db, mix=a_mix)
      == ("", "several microphones"),
      "%r against ('', 'several microphones')"
      % (vpm.speaker_source_pick([p for _n, p in FAR], [],
                                 apart_db=far_db, mix=a_mix),))


shutil.rmtree(WORK, ignore_errors=True)
print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
