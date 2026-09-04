# -*- coding: utf-8 -*-
"""Where the names of the voices could come from, instead of by hand.

Two ways, both proposals that set nothing: the separation against the
microphone tracks, and who asks against who answers. Real microphones
often cannot be told apart, so most of this test asks where nothing
may be said at all -- a wrong name would stand over a whole episode.
"""
import os
import the_program
HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = the_program.SCRIPT
import random, sys, tempfile, time, wave
import numpy as np
vpm = the_program.load()

began = time.time()
done = 0
bad = []


def check(name, ok, extra=""):
    global done
    done += 1
    print("  %-58s %s %s" % (name, "ok" if ok else "FAIL", extra))
    if not ok:
        bad.append("%s [%s]" % (name, extra or "no numbers"))


PEOPLE = ["Anna", "Ben", "Cleo"]
SR = 8000


def turns(chatter=0.25, rounds=18, seed=3):
    """Three people taking turns, with the others chipping in."""
    r = random.Random(seed)
    out = {n: [] for n in PEOPLE}
    t = 1.0
    for _ in range(rounds):
        for n in PEOPLE:
            length = 3.0 * (0.6 + r.random() * 0.8)
            out[n].append((t, t + length))
            for m in PEOPLE:
                if m != n and r.random() < chatter:
                    a = t + r.random() * max(0.1, length - 0.5)
                    out[m].append((a, a + 0.4))
            t += length + 0.6
    return {n: sorted(v) for n, v in out.items()}, t + 2.0


TRUTH, LENGTH = turns()
VOICES = [("SPEAKER_%02d" % i, TRUTH[n]) for i, n in enumerate(PEOPLE)]


def named(rows):
    return dict((voice, track) for voice, track, _s, _d in rows)


# ------------------------------------------- the whole way, on built audio
print("Three microphones, 12 dB apart, through the audio")
WORK = tempfile.mkdtemp(prefix="voice_mic_")


def wave_of(name):
    x = np.zeros(int(LENGTH * SR), dtype=np.float64)
    tone = 180.0 + 90.0 * PEOPLE.index(name)
    for a, b in TRUTH[name]:
        i, j = int(a * SR), int(b * SR)
        w = np.arange(j - i) / float(SR)
        x[i:j] += 0.5 * np.sin(2 * np.pi * tone * w) * (
            0.6 + 0.4 * np.sin(2 * np.pi * 3.1 * w))
    return x


clean = dict((n, wave_of(n)) for n in PEOPLE)
tracks = []
for n in PEOPLE:
    x = clean[n] + 0.25 * sum(clean[m] for m in PEOPLE if m != n)
    x = x + np.random.RandomState(3).normal(0, 0.0015, len(x))
    path = os.path.join(WORK, "%s.wav" % n)
    with wave.open(path, "wb") as f:
        f.setnchannels(1)
        f.setsampwidth(2)
        f.setframerate(SR)
        f.writeframes((np.clip(x, -1, 1) * 32000).astype("<i2").tobytes())
    tracks.append((n, path, 0.0))
MICS = vpm.speakers_from_tracks(tracks, rate=SR)
check("every microphone reports speech",
      all(segs for _, segs in MICS), str([len(s) for _, s in MICS]))
rows = vpm.which_microphone(VOICES, MICS)
check("all three voices are matched", len(rows) == 3, str(rows))
check("and each one to its own microphone",
      named(rows) == dict(("SPEAKER_%02d" % i, n)
                          for i, n in enumerate(PEOPLE)), str(named(rows)))
check("the distance is far above the limit set from measurement",
      all(d >= vpm.VOICE_TRACK_MARGIN for _v, _t, _s, d in rows),
      str([round(d, 3) for _v, _t, _s, d in rows]))

print("\nThe report says what it is and what it assumes")
vpm.set_language("en")
lines = vpm.microphones_report(rows)
check("a heading, a line per voice and the assumption",
      len(lines) == 5, str(len(lines)))
check("the heading calls it a proposal",
      "proposal" in lines[0] and "nothing is set" in lines[0], "%r" % lines[0])
check("the last line names the assumption",
      "one microphone per person" in lines[-1],
      "wanted 'one microphone per person' in the last of %d lines: %r"
      % (len(lines), lines[-1][:100]))
check("every voice and its microphone stand in a line",
      all(any(v in line and t in line for line in lines[1:-1])
          for v, t in named(rows).items()), str(lines[1:-1]))
vpm.set_language("de")
german = vpm.microphones_report(rows)
check("the German side is there and is not the English one",
      len(german) == len(lines) and german[0] != lines[0], "%r" % german[0])
vpm.set_language("en")
no_rows = vpm.microphones_report([])
check("nothing to say, nothing printed",
      no_rows == [], "0 rows in, %d lines out, wanted 0: %s"
      % (len(no_rows), no_rows))

# ---------------------------------------------------- where it must be quiet
print("\nQuiet where the answer would be a guess")
one_track = vpm.which_microphone(VOICES, MICS[:1])
check("one microphone alone says nothing",
      one_track == [], "%d voices against 1 microphone: %d named, wanted 0: %s"
      % (len(VOICES), len(one_track), named(one_track)))
one_voice = vpm.which_microphone(VOICES[:1], MICS)
check("one voice alone says nothing",
      one_voice == [], "1 voice against %d microphones: %d named, wanted 0: %s"
      % (len(MICS), len(one_voice), named(one_voice)))
no_voices = vpm.which_microphone([], MICS)
check("no voices at all", no_voices == [],
      "0 voices against %d microphones: %d named, wanted 0: %s"
      % (len(MICS), len(no_voices), named(no_voices)))
no_tracks = vpm.which_microphone(VOICES, [])
check("no tracks at all", no_tracks == [],
      "%d voices against 0 microphones: %d named, wanted 0: %s"
      % (len(VOICES), len(no_tracks), named(no_tracks)))
one_mute = vpm.which_microphone(VOICES, [(MICS[0][0], []), MICS[1]])
check("a track without any speech says nothing",
      one_mute == [], "%d voices against 2 microphones, one with 0 passages: "
      "%d named, wanted 0: %s" % (len(VOICES), len(one_mute), named(one_mute)))

# The shape of real material: both microphones carry the same person.
union = []
for a, b in sorted(list(MICS[0][1]) + list(MICS[1][1])):
    if union and a <= union[-1][1]:
        union[-1][1] = max(union[-1][1], b)
    else:
        union.append([a, b])
both = [MICS[0], (MICS[1][0], [(a, b) for a, b in union])]
share = vpm.shared_seconds(both[0][1], both[1][1]) / sum(
    b - a for a, b in both[0][1])
check("two microphones carrying the same person: %.0f%% shared"
      % (100 * share), share > vpm.VOICE_TRACK_TOGETHER, "%.3f" % share)
check("and then nothing at all is claimed",
      vpm.which_microphone(VOICES, both) == [],
      str(vpm.which_microphone(VOICES, both)))

# Off the axis the shares stay high -- speech is everywhere -- so only
# the distance between first and second catches it.
moved = [(n, [(a + 10.0, b + 10.0) for a, b in segs]) for n, segs in VOICES]
check("a separation ten seconds off the axis is not named",
      vpm.which_microphone(moved, MICS) == [],
      str(vpm.which_microphone(moved, MICS)))

print("\nVoices that cannot be placed are left out, the others stay")
# A fourth person on nobody's microphone: every track hears them about
# equally, so no track is ahead of the next.
rows = vpm.which_microphone(
    VOICES + [("SPEAKER_03", sorted(
        [(a, a + 0.4) for a, _b in MICS[0][1][:30]]
        + [(a, a + 0.4) for a, _b in MICS[1][1][:30]]
        + [(a, a + 0.4) for a, _b in MICS[2][1][:30]]))], MICS)
check("the one nobody has a microphone for gets no line",
      "SPEAKER_03" not in named(rows), str(named(rows)))
check("the other three keep theirs", len(rows) == 3, str(named(rows)))

short = [(a, b) for a, b in TRUTH["Ben"]][:3]
held = sum(b - a for a, b in short)
check("a voice with %.0f s of speech is under the floor of %.0f s"
      % (held, vpm.VOICE_MIN_SPEECH_S), held < vpm.VOICE_MIN_SPEECH_S,
      "%.1f" % held)
rows = vpm.which_microphone(
    [VOICES[0], VOICES[2], ("SPEAKER_09", short)], MICS)
check("and it is not named", "SPEAKER_09" not in named(rows),
      str(named(rows)))
check("while the two that spoke enough are", len(rows) == 2, str(named(rows)))

# The separation cut one person in two, both halves on one microphone.
half = len(TRUTH["Anna"]) // 2
split = [("SPEAKER_10", TRUTH["Anna"][:half]),
         ("SPEAKER_11", TRUTH["Anna"][half:]), VOICES[1], VOICES[2]]
rows = vpm.which_microphone(split, MICS)
check("two voices on one microphone: neither is named",
      "SPEAKER_10" not in named(rows) and "SPEAKER_11" not in named(rows),
      str(named(rows)))
check("and the microphone itself is left out",
      "Anna" not in named(rows).values(), str(named(rows)))
check("the two that are clear are still there", len(rows) == 2,
      str(named(rows)))

print("\nHow long two lists of passages run at once")
apart = vpm.shared_seconds([(0.0, 1.0)], [(2.0, 3.0)])
check("no overlap is zero", apart == 0.0,
      "(0,1) against (2,3): %.9f s, wanted 0" % apart)
inside = vpm.shared_seconds([(0.0, 10.0)], [(2.0, 3.0)])
check("one inside the other is the inner one", inside == 1.0,
      "(0,10) against (2,3): %.9f s, wanted 1" % inside)
overlap = vpm.shared_seconds([(0.0, 2.0)], [(1.0, 4.0)])
check("half over half", abs(overlap - 1.0) < 1e-9,
      "(0,2) against (1,4): %.9f s, wanted 1 within 1e-9" % overlap)
several = vpm.shared_seconds([(0.0, 2.0), (4.0, 6.0)], [(1.0, 5.0)])
check("several against several", abs(several - 2.0) < 1e-9,
      "(0,2)+(4,6) against (1,5): %.9f s, wanted 2 within 1e-9" % several)
nothing = vpm.shared_seconds([], [(1.0, 2.0)])
check("empty against anything is zero", nothing == 0.0,
      "nothing against (1,2): %.9f s, wanted 0" % nothing)

# ----------------------------------------- the roles, out of who asks
# Two people asking, one only ever answering and twice as long: the
# shape the ranking was made for, with the guest at the end of it.
print("\nThe roles, read off who asks and who answers")
vpm.set_language("en")
PLAN = [("Speaker 1", True), ("Speaker 3", False), ("Speaker 2", True),
        ("Speaker 3", False), ("Speaker 1", True), ("Speaker 3", False),
        ("Speaker 2", False)]


def conversation(rounds=12, plan=PLAN):
    """Segments and words for a conversation of the shape above."""
    parts, words, t = {}, [], 0.0
    for _ in range(rounds):
        for who, question in plan:
            length = 4.0 if who == "Speaker 3" else 2.0
            parts.setdefault(who, []).append((t, t + length))
            words.append({"start": t + 0.2, "end": t + 0.6, "word": "hello"})
            words.append({"start": t + 0.8, "end": t + 1.2,
                          "word": "there?" if question else "there."})
            t += length + 0.2
    return sorted(parts.items()), words


spoke, said = conversation()
ORDER = vpm.who_asks(spoke, said)
check("all three voices reach the ranking", len(ORDER) == 3, str(ORDER))
roles = vpm.voice_role_names(ORDER)
check("the one who never asks is the guest",
      roles.get("Speaker 3") == "Guest", str(roles))
check("the one asking most is the first host",
      roles.get("Speaker 1") == "Host 1", str(roles))
check("and the other one the second", roles.get("Speaker 2") == "Host 2",
      str(roles))
two = vpm.voice_role_names(ORDER[1:])
check("with only two there is one host, and it is not numbered",
      sorted(two.values()) == ["Guest", "Host"], str(two))
alone = vpm.voice_role_names(ORDER[:1])
check("one voice alone is no ranking", alone == {},
      "1 voice in, %d roles out, wanted 0: %s" % (len(alone), alone))
none = vpm.voice_role_names([])
check("nothing in, nothing out", none == {},
      "0 voices in, %d roles out, wanted 0: %s" % (len(none), none))

print("\nA voice that hardly speaks in the window gets no role")
# A voice under ROLE_MIN_SENTENCES -- the person behind the camera --
# is left out by who_asks, and the proposal must not put it back in.
spoke4, said4 = conversation(rounds=1, plan=[("Speaker 4", False)])
spoke_all, said_all = conversation()
spoke_all = spoke_all + [("Speaker 4", [(a + 1000.0, b + 1000.0)
                                        for a, b in spoke4[0][1]])]
said_all = said_all + [dict(w, start=w["start"] + 1000.0,
                            end=w["end"] + 1000.0) for w in said4]
order4 = vpm.who_asks(spoke_all, said_all)
check("who_asks leaves the passer-by out",
      "Speaker 4" not in [row[0] for row in order4],
      str([row[0] for row in order4]))
check("and so does the proposal",
      "Speaker 4" not in vpm.voice_role_names(order4),
      str(vpm.voice_role_names(order4)))

print("\nOnly names the program gave itself are proposed over")
label = vpm.is_stand_in_name("SPEAKER_00")
check("the label of the separation is one", label,
      "'SPEAKER_00' -> %s, wanted True" % label)
numbered = vpm.is_stand_in_name("Speaker 3")
check("the numbered stand-in is one", numbered,
      "'Speaker 3' -> %s, wanted True" % numbered)
vpm.set_language("de")
in_german = vpm.is_stand_in_name("Sprecher 2")
check("in German as well", in_german,
      "'Sprecher 2', language de -> %s, wanted True" % in_german)
vpm.set_language("en")
in_english = vpm.is_stand_in_name("Sprecher 2")
check("but it is checked in every language, not only the one running",
      in_english, "'Sprecher 2', language en -> %s, wanted True" % in_english)
for typed in ("Anna", "Speaker", "", "Speaker one", "Presenter"):
    answer = vpm.is_stand_in_name(typed)
    check("  a typed name is left alone: %r" % typed,
          not answer, "%r -> %s, wanted False" % (typed, answer))

print("\nThe report on the roles")
lines = vpm.voice_names_report(ORDER)
check("a heading, three lines and the assumption", len(lines) == 5,
      str(len(lines)))
check("it calls itself a proposal", "proposal" in lines[0], "%r" % lines[0])
check("and the last line says nothing is set",
      "never touched" in lines[-1] and "not a setting" in lines[-1],
      "'never touched' %s, 'not a setting' %s in the last of %d lines: %r"
      % ("never touched" in lines[-1], "not a setting" in lines[-1],
         len(lines), lines[-1][:90]))
named_order = [(n.replace("Speaker", "Anna"), s, q, h)
               for n, s, q, h in ORDER]
check("voices somebody has named get no proposal",
      vpm.voice_names_report(named_order) == [],
      str(vpm.voice_names_report(named_order)))
no_report = vpm.voice_names_report([])
check("no ranking, no report", no_report == [],
      "0 voices in, %d lines out, wanted 0: %s" % (len(no_report), no_report))
vpm.set_language("de")
german_lines = vpm.voice_names_report(ORDER)
check("the German side of the report is there",
      len(german_lines) == 5 and german_lines[0] != lines[0],
      "%d lines, wanted 5; first line %r against the English %r"
      % (len(german_lines), german_lines[0] if german_lines else None,
         lines[0]))
vpm.set_language("en")

print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
