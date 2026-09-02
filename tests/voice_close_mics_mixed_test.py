# -*- coding: utf-8 -*-
"""Microphones that hear each other are mixed and taken apart by voice.

The switch, the source and the naming, in that order: how far apart the
microphones stand, whether the separation is refused or handed a mix of
them all, that the mix is a plain sum and nothing is levelled first,
and that the voices are named after the microphone that is left when
the recording level is taken out. Then a guard: where the microphones
can be told apart the cheap route stays untouched. Then a recording
that arrives in several blocks, which has to be measured as the one
recording it is. Last a run started out of the window with a separation
already in hand: below the limit the run overrules it, above the limit
and wherever the measurement could decide nothing it does not, and the
question of how far apart they stand is asked once a run at most. The
model itself is not run -- the voices are handed in with their true
times.
"""
import os
HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = os.environ.get("VPM_SCRIPT") or os.path.join(
    os.path.dirname(HERE), "videopodcast-magic.py")
import importlib.util
import io
import shutil
import struct
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


print("\n7. A recording that arrives in blocks is one recording")
#
# Most field recorders cut a long take into files of a few minutes, and
# the program joins them again by their clock. Two such blocks follow
# each other and never sound at the same moment: measured against each
# other they share no time at all, and measured against a neighbour's
# recording without a clock, minute three of the second block would be
# held against minute three of the first. So what the microphones hear
# of each other has to be asked of the recording, not of the blocks.
#
# The Presenter's recording is cut in two here, the Guest's is left
# whole -- the same audio as in section 1, so the number a whole
# recording gives is close_db and far_db and needs no second reading.


def frames_of(path):
    """The samples of a mono file, as they stand in it."""
    with wave.open(path, "rb") as f:
        return f.readframes(f.getnframes())


def written(path, frames, start_s=None):
    """One block, carrying the start a recorder writes where asked.

    The stamp is the BWF one: the start of the file in samples, counted
    at the rate the program reads it, in the bext chunk behind the RIFF
    header.
    """
    with wave.open(path, "wb") as f:
        f.setnchannels(1)
        f.setsampwidth(2)
        f.setframerate(SR)
        f.writeframes(frames)
    if start_s is None:
        return path
    body = bytearray(602)
    struct.pack_into("<Q", body, 338, int(round(start_s * vpm.SR)))
    raw = open(path, "rb").read()
    out = (raw[:12] + b"bext" + struct.pack("<I", len(body)) + bytes(body)
           + raw[12:])
    with open(path, "wb") as f:
        f.write(b"RIFF" + struct.pack("<I", len(out) - 8) + out[8:])
    return path


def in_blocks(tracks, tag, clock=True):
    """The Presenter's recording in two halves, plus the joined whole.

    With *clock* every file carries the timecode a recorder writes, so
    the blocks are placed one after the other; without it they are laid
    end to end in the order they came. The joining is the program's own,
    because it is the file the run works with afterwards.
    """
    named = dict(tracks)
    cut = int(30.0 * SR) * 2      # two bytes to a sample
    pres = frames_of(named["Presenter"])
    guest = written(os.path.join(WORK, "%s_Guest.wav" % tag),
                    frames_of(named["Guest"]), 0.0 if clock else None)
    first = written(os.path.join(WORK, "%s_Presenter_1.wav" % tag),
                    pres[:cut], 0.0 if clock else None)
    second = written(os.path.join(WORK, "%s_Presenter_2.wav" % tag),
                     pres[cut:], 30.0 if clock else None)
    joined, _info = vpm.join_audio_parts(
        [first, second], os.path.join(WORK, "%s_joined.wav" % tag))
    return guest, first, second, joined


def blocked_tracks(guest, first, second, joined):
    """The two tracks as they stand when the separation is chosen.

    By then the blocks are joined and laid on the common axis, so a
    track carries both: the recording it became and the files it came
    in.
    """
    return [{"name": "Guest", "source": guest, "blocks": [guest],
             "axis": guest, "a": 0.0, "b": 1.0},
            {"name": "Presenter", "source": joined,
             "blocks": [first, second], "axis": joined,
             "a": 0.0, "b": 1.0}]


class Bare(object):
    """As much of the parsed command line as the choice reads."""

    _camera_audio = None


measured = []
offered = []
straight_apart = vpm.microphones_apart_db
straight_mix = vpm.speaker_mix_file


def watched(paths):
    """The real measurement, with its answer written down as it passes."""
    got = straight_apart(paths)
    measured.append(got)
    return got


def noted_mix(paths, made_of, folder=""):
    """A stand-in for the mixing: what was offered is what is asked."""
    offered.append(list(paths))
    return os.path.join(WORK, "blockmix.wav")


vpm.microphones_apart_db = watched
vpm.speaker_mix_file = noted_mix
try:
    del measured[:]
    del offered[:]
    close_run = vpm.separation_source_of_run(
        Bare(), blocked_tracks(*in_blocks(CLOSE, "blocked_close")), [],
        mixable=True)
    close_blocks_db = measured[-1] if measured else None
    close_offered = offered[-1] if offered else []
    check("a recording in blocks is measured as one, so close "
          "microphones are still mixed",
          close_run[1] == "microphones mixed",
          "%r at %s dB, wanted 'microphones mixed' under %.1f dB"
          % (close_run[1],
             "none" if close_blocks_db is None else "%.1f" % close_blocks_db,
             vpm.MICROPHONES_APART_DB))
    check("and the mix is offered one file per recording, not one per "
          "block",
          len(close_offered) == 2,
          "%d files offered (%s), wanted 2 -- one Guest, one Presenter"
          % (len(close_offered),
             ", ".join(os.path.basename(p) for p in close_offered) or "none"))
    # How the recording was cut into files may not move the answer.
    # The tenth of a decibel is wide enough for another way of asking
    # the same question -- measured, a reading over the first block
    # alone lands 0.001 dB away -- and far under what a reading block
    # against block costs, which is 0.73 dB here.
    check("what a recording in blocks measures is what the same "
          "recording in one file measures",
          close_blocks_db is not None and close_db is not None
          and abs(close_blocks_db - close_db) <= 0.10,
          "%s dB in blocks against %s dB in one file, wanted within 0.10 dB"
          % ("none" if close_blocks_db is None else "%.3f" % close_blocks_db,
             "none" if close_db is None else "%.3f" % close_db))

    del measured[:]
    del offered[:]
    far_run = vpm.separation_source_of_run(
        Bare(), blocked_tracks(*in_blocks(FAR, "blocked_far")), [],
        mixable=True)
    far_blocks_db = measured[-1] if measured else None
    check("microphones far apart are left alone even when a recording "
          "comes in blocks",
          far_run == ("", "several microphones") and offered == [],
          "%r at %s dB and %d mixes asked for, wanted 'several "
          "microphones' over %.1f dB and none"
          % (far_run[1],
             "none" if far_blocks_db is None else "%.1f" % far_blocks_db,
             len(offered), vpm.MICROPHONES_APART_DB))

    # Without a clock nothing gives up: a number comes out either way,
    # and only its size says whether the blocks were joined first or
    # held against each other at the wrong minute.
    del measured[:]
    del offered[:]
    loose_run = vpm.separation_source_of_run(
        Bare(), blocked_tracks(*in_blocks(CLOSE, "loose_close", clock=False)),
        [], mixable=True)
    loose_db = measured[-1] if measured else None
    check("and without a clock too, blocks answer as the one recording "
          "and not each other",
          loose_db is not None and close_db is not None
          and abs(loose_db - close_db) <= 0.10,
          "%s dB in blocks against %s dB in one file (%r), wanted within "
          "0.10 dB"
          % ("none" if loose_db is None else "%.3f" % loose_db,
             "none" if close_db is None else "%.3f" % close_db,
             loose_run[1]))
finally:
    vpm.microphones_apart_db = straight_apart
    vpm.speaker_mix_file = straight_mix


print("\n8. A separation handed over from the window does not settle it")
#
# The window picks its source without knowing how far the microphones
# stand apart, so it can only ever take a single recording. Measured on
# 2.9.2026 the run then never asked the question at all -- it carried
# the window's answer over to save the graphics unit three minutes, and
# below the limit that is the worse answer by a long way. So the run
# overrules it, and only where it can really do better.
#
# The model is a stand-in answering out of a table, as everywhere else
# in this file; the mix under it is the program's own and is really
# made. The store is this test's own, so nothing another test left
# behind can answer for a recording this one mixed.
KEPT_CACHE = os.environ.get("VPM_CACHE")
OWN_STORE = tempfile.mkdtemp(prefix="vpm_close_store_")
os.environ["VPM_CACHE"] = OWN_STORE
KEPT_OFF = vpm.SPEAKER_SPLIT_OFF
vpm.SPEAKER_SPLIT_OFF = False
vpm.speaker_split_available = lambda deep=False: True
vpm.speaker_split_run = lambda path, count=0, **kw: (
    [("SPEAKER_00", [(1.0, 6.0)]), ("SPEAKER_01", [(7.0, 12.0)])], "")
counted = {"apart": 0, "picked": []}
straight_apart = vpm.microphones_apart_db
straight_pick = vpm.separation_source_of_run


def counting_apart(paths):
    """The real measurement, counted: it may not fall in every run."""
    counted["apart"] += 1
    return straight_apart(paths)


def counting_pick(args, tracks, video_paths, mixable=False, window=()):
    """The real source pick, with a note of whether it was asked at all."""
    counted["picked"].append(bool(mixable))
    return straight_pick(args, tracks, video_paths, mixable=mixable,
                         window=window)


vpm.microphones_apart_db = counting_apart
vpm.separation_source_of_run = counting_pick


def on_the_axis(tracks):
    """The two microphones as they stand when the separation is chosen."""
    return [{"name": n, "source": p, "blocks": [p], "axis": p,
             "a": 0.0, "b": 1.0} for n, p in tracks]


def handed_over(tracks):
    """What the window took apart: one recording, one voice, one name."""
    return {"source": tracks[0][1],
            "names": {"SPEAKER_00": "WindowVoice"},
            "segments": [["SPEAKER_00", 2.0, 9.0]]}


class Started(object):
    """As much of the parsed command line as the separation reads."""

    def __init__(self, **over):
        self.speakers_local = None
        self.speakers_from = None
        self.speakers_count = 0
        self.no_speakers_local = False
        self.dry_run = False
        self.without_auphonic = True
        self.auphonic_done = None
        self._camera_audio = None
        self.__dict__.update(over)


def out_of_the_window(tracks, **over):
    """One run started from the window, and everything it said."""
    counted["apart"] = 0
    del counted["picked"][:]
    kept_out, sys.stdout = sys.stdout, io.StringIO()
    try:
        out, where_from = vpm.separation_for_run(
            Started(_speakers_of=handed_over(tracks), **over),
            on_the_axis(tracks), {}, 0.0, LENGTH, [])
    finally:
        said, sys.stdout = sys.stdout.getvalue(), kept_out
    return {"voices": [n for n, _s in out], "from": where_from,
            "said": said, "apart": counted["apart"],
            "picked": list(counted["picked"])}


try:
    close_run = out_of_the_window(CLOSE)
    check("close microphones: the window's separation is dropped and the "
          "run picks its own",
          close_run["from"] == vpm.T('the separation in this run')
          and close_run["picked"] == [True],
          "the run says %r after %d source picks %s -- wanted %r and one "
          "pick with the mix allowed"
          % (close_run["from"], len(close_run["picked"]),
             close_run["picked"], vpm.T('the separation in this run')))
    check("and the voices that reach the cut are the mix's, not the "
          "window's one",
          sorted(close_run["voices"]) == ["SPEAKER_00", "SPEAKER_01"],
          "%s came back, wanted the two the mix was taken apart into and "
          "not ['WindowVoice']" % (close_run["voices"],))
    check("and the run names both numbers for the work it threw away",
          ("%.1f" % close_db) in close_run["said"]
          and ("%.1f" % vpm.MICROPHONES_APART_DB) in close_run["said"],
          "the log carries %.1f dB: %r, and the limit %.1f dB: %r -- "
          "wanted both"
          % (close_db, ("%.1f" % close_db) in close_run["said"],
             vpm.MICROPHONES_APART_DB,
             ("%.1f" % vpm.MICROPHONES_APART_DB) in close_run["said"]))
    check("and how far apart they stand is measured once in that run",
          close_run["apart"] == 1,
          "%d measurements, wanted 1" % close_run["apart"])

    far_run = out_of_the_window(FAR)
    check("microphones far apart: what the window handed over is what the "
          "run uses",
          far_run["from"] == vpm.T('the interface')
          and far_run["voices"] == ["WindowVoice"],
          "the run says %r and %s came back -- wanted %r and "
          "['WindowVoice']"
          % (far_run["from"], far_run["voices"], vpm.T('the interface')))
    check("and no separation of its own is started there",
          far_run["picked"] == [] and far_run["apart"] == 1,
          "%d source picks %s after %d measurements -- wanted none after "
          "one" % (len(far_run["picked"]), far_run["picked"],
                   far_run["apart"]))

    # The measurement reads five windows out of every recording against
    # every other, so it may not fall where its answer changes nothing.
    auphonic_run = out_of_the_window(CLOSE, without_auphonic=False)
    check("where auphonic.com takes the bleed out the window's answer "
          "stands, unmeasured",
          auphonic_run["from"] == vpm.T('the interface')
          and auphonic_run["apart"] == 0,
          "the run says %r after %d measurements -- wanted %r and none"
          % (auphonic_run["from"], auphonic_run["apart"],
             vpm.T('the interface')))
    refused_run = out_of_the_window(CLOSE, no_speakers_local=True)
    check("and --no-speakers-local leaves it alone, unmeasured, as well",
          refused_run["from"] == vpm.T('the interface')
          and refused_run["apart"] == 0,
          "the run says %r after %d measurements -- wanted %r and none"
          % (refused_run["from"], refused_run["apart"],
             vpm.T('the interface')))
    # Three more ways the run cannot do better, each with a run of its
    # own: a recording named on the command line, sound taken off the
    # cameras, and a machine that has no model to take anything apart
    # with. The microphones stand close in all three, so only the term
    # under test keeps the measurement from happening.
    named_run = out_of_the_window(CLOSE, speakers_local="/nowhere/one.wav")
    check("a recording named with --speakers-local keeps the window's "
          "answer, unmeasured",
          named_run["from"] == vpm.T('the interface')
          and named_run["apart"] == 0,
          "the run says %r after %d measurements -- wanted %r and none"
          % (named_run["from"], named_run["apart"],
             vpm.T('the interface')))
    camera_run = out_of_the_window(CLOSE, _camera_audio=True)
    check("and sound taken off the cameras keeps it too, unmeasured",
          camera_run["from"] == vpm.T('the interface')
          and camera_run["apart"] == 0,
          "the run says %r after %d measurements -- wanted %r and none"
          % (camera_run["from"], camera_run["apart"],
             vpm.T('the interface')))
    vpm.SPEAKER_SPLIT_OFF = True
    try:
        no_model_run = out_of_the_window(CLOSE)
    finally:
        vpm.SPEAKER_SPLIT_OFF = False
    check("and a machine with no model to take a recording apart keeps "
          "it as well, unmeasured",
          no_model_run["from"] == vpm.T('the interface')
          and no_model_run["apart"] == 0,
          "the run says %r after %d measurements -- wanted %r and none"
          % (no_model_run["from"], no_model_run["apart"],
             vpm.T('the interface')))
finally:
    vpm.microphones_apart_db = straight_apart
    vpm.separation_source_of_run = straight_pick
    vpm.SPEAKER_SPLIT_OFF = KEPT_OFF
    if KEPT_CACHE is None:
        os.environ.pop("VPM_CACHE", None)
    else:
        os.environ["VPM_CACHE"] = KEPT_CACHE
    shutil.rmtree(OWN_STORE, ignore_errors=True)


shutil.rmtree(WORK, ignore_errors=True)
print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
