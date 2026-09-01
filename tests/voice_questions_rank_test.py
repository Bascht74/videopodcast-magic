# -*- coding: utf-8 -*-
"""Who is asking the questions, as a proposal and never as a verdict.

The roles can be read off the recognition only as an ORDER: the guest
asks the fewest questions per sentence and speaks the longest, but the
distance varies too much for a fixed threshold. Questions beat the
share of talking, because a long opening by the host points at the
wrong person for minutes. And it all takes one voice per track. So
this file holds the order, holds the questions above the share, stays
quiet where there is too little, and quiet again where two tracks
carry the same speech.
"""
import os, sys, time
HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = os.environ.get("VPM_SCRIPT") or os.path.join(
    os.path.dirname(HERE), "videopodcast-magic.py")
import importlib.util
spec = importlib.util.spec_from_file_location("vpm", SCRIPT)
vpm = importlib.util.module_from_spec(spec); sys.modules["vpm"] = vpm
spec.loader.exec_module(vpm)

started = time.time()
done = 0
bad = []


def check(name, ok, extra=""):
    global done
    done += 1
    print("  %-58s %s %s" % (name, "ok" if ok else "FAIL", extra))
    if not ok:
        bad.append("%s [%s]" % (name, extra or "no numbers"))


def sentence(at, words, asking):
    """One sentence of *words* words, starting there, a question or not."""
    out = []
    for i in range(words):
        out.append({"word": "wort", "start": at + i * 0.4,
                    "end": at + i * 0.4 + 0.35})
    out[-1]["word"] = "wort?" if asking else "wort."
    return out, at + words * 0.4 + 0.2


def episode(plan):
    """Build words and tracks from [(name, sentences, questions, words)]."""
    words, tracks, at = [], {}, 0.0
    for name, n, asking, per in plan:
        tracks.setdefault(name, [])
        for k in range(n):
            began = at
            said, at = sentence(at, per, k < asking)
            words.extend(said)
            tracks[name].append((began, at - 0.2))
    return words, sorted(tracks.items())


print("1. The one asking comes first")
# The plain case: a host who mostly asks, a guest who answers at
# length. It must never come out the other way round.
words, tracks = episode([("Host", 30, 22, 4), ("Guest", 30, 1, 12)])
order = vpm.who_asks(tracks, words)
check("both speakers are ranked", len(order) == 2, str(order))
check("the one asking stands first",
      order and order[0][0] == "Host", str([r[0] for r in order]))
check("the numbers come with it, so a person can check them",
      order and order[0][1] == 30 and order[0][2] == 22, str(order[0]))
check("and the guest speaks the longer of the two",
      order and order[-1][3] > order[0][3],
      str([(r[0], round(r[3], 1)) for r in order]))

print("\n2. The questions beat the speaking share")
# The trap: a long opening by the host makes the share of the talking
# point at the host as the guest, while the questions point the right
# way. Whoever ranks by time gets such an episode wrong.
words, tracks = episode([("Host", 25, 20, 30), ("Guest", 25, 0, 4)])
order = vpm.who_asks(tracks, words)
held = {n: t for n, _s, _q, t in order}
check("the host does hold the floor here",
      held.get("Host", 0) > held.get("Guest", 0),
      str({k: round(v, 1) for k, v in held.items()}))
check("and is still named as the one asking",
      order and order[0][0] == "Host", str([r[0] for r in order]))

print("\n3. Where nobody asks, the shorter turn decides")
# With no questions the order falls back on the time: the one who
# talks less is the likelier asker, and nothing beyond that is claimed.
words, tracks = episode([("Host", 25, 0, 4), ("Guest", 25, 0, 12)])
order = vpm.who_asks(tracks, words)
check("the shorter speaker comes first", order and order[0][0] == "Host",
      str([(r[0], round(r[3], 1)) for r in order]))

print("\n4. Too little to say anything from")
words, tracks = episode([("Host", 5, 4, 4), ("Guest", 5, 0, 8)])
check("five sentences each: nothing is claimed",
      vpm.who_asks(tracks, words) == [], str(vpm.who_asks(tracks, words)))

words, tracks = episode([("Host", 30, 20, 4), ("Guest", 3, 0, 8)])
order = vpm.who_asks(tracks, words)
check("one speaker with too little: nothing is claimed either",
      order == [], str(order))

none_said = vpm.who_asks(tracks, [])
check("no words at all: nothing is claimed", none_said == [],
      "%d speakers ranked: %s" % (len(none_said), none_said))
words, tracks = episode([("Host", 30, 20, 4)])
check("one track alone: nothing is claimed",
      vpm.who_asks(tracks, words) == [], str(vpm.who_asks(tracks, words)))

print("\n5. Three speakers keep their order")
# The usual recording. The guest must come last, and the one asking
# most must come first.
words, tracks = episode([("HostA", 25, 20, 4), ("HostB", 25, 10, 5),
                         ("Guest", 30, 0, 14)])
order = vpm.who_asks(tracks, words)
check("all three are ranked", len(order) == 3, str([r[0] for r in order]))
check("the guest comes last", order and order[-1][0] == "Guest",
      str([r[0] for r in order]))
check("and the one asking most comes first",
      order and order[0][0] == "HostA", str([r[0] for r in order]))

print("\n6. A question is what the rest of the program calls one")
# Closing marks are stripped first, or a quoted question would not
# count.
quoted, _at = sentence(0.0, 3, False)
quoted[-1]["word"] = 'wort?"'
plain, _at = sentence(10.0, 3, False)
check("a question inside quotation marks still counts",
      vpm.word_mark(quoted[-1]["word"]) == "sentence"
      and quoted[-1]["word"].rstrip(vpm.CLOSING_MARKS).endswith("?"),
      quoted[-1]["word"])
check("and an ordinary full stop does not",
      not plain[-1]["word"].rstrip(vpm.CLOSING_MARKS).endswith("?"),
      plain[-1]["word"])

print("\n7. What the run says about it")
words, tracks = episode([("Host", 30, 22, 4), ("Guest", 30, 1, 12)])
lines = vpm.roles_report(vpm.who_asks(tracks, words))
check("the report has a heading and one line per speaker",
      len(lines) == 4, str(len(lines)))
check("the one asking is named first",
      len(lines) > 1 and "Host" in lines[1], str(lines[1:2]))
check("the numbers are in it, not just the order",
      any("22 of 30" in x for x in lines), str(lines[1:3]))
check("it says the order carries and the distance does not",
      any("order carries" in x or "Reihenfolge" in x for x in lines),
      str(lines[-1])[:70])
check("it says it takes one voice per track",
      any("one voice per track" in x or "Stimme je Spur" in x
          for x in lines), str(lines[-1])[:70])
empty_report = vpm.roles_report([])
check("nothing to report is nothing printed", empty_report == [],
      "%d lines printed: %s" % (len(empty_report), empty_report))

print("\n8. One voice per track, or the ranking is not said")
# Two clip-on microphones in one room hear each other, and then both
# tracks carry the whole conversation. Measured on real episodes: a few
# per cent where the tracks are clean, 85 to 93 where they are not.
seams = [("A", [(0.0, 100.0)]), ("B", [(93.0, 200.0)])]
carried = [("A", [(0.0, 100.0)]), ("B", [(10.0, 100.0), (200.0, 210.0)])]
check("a few seconds at the seams, the way separated voices touch, pass",
      vpm.one_voice_each(seams),
      "7 s of the shorter track's 100 s shared, guard above %d %%"
      % round(100 * vpm.VOICE_TRACK_TOGETHER))
check("two tracks carrying the same speech do not",
      not vpm.one_voice_each(carried),
      "90 s of the shorter track's 100 s shared, guard above %d %%"
      % round(100 * vpm.VOICE_TRACK_TOGETHER))

words, tracks = episode([("Host", 30, 22, 4), ("Guest", 30, 1, 12)])
# The same episode, but the host's microphone heard the guest as well.
guest = dict(tracks)["Guest"]
heard_too = [(n, sorted(s + guest) if n == "Host" else s) for n, s in tracks]
check("with one microphone carrying both, no ranking is given",
      vpm.who_asks(heard_too, words) == [],
      "%d ranked, %d without the bleed"
      % (len(vpm.who_asks(heard_too, words)), len(vpm.who_asks(tracks, words))))
voices = [("SPEAKER_00", dict(tracks)["Host"]), ("SPEAKER_01", guest)]
matched = vpm.which_microphone(voices, heard_too)
check("and the microphone proposal falls silent on those same tracks",
      matched == [], "%d voices matched to a microphone, wanted none: %s"
      % (len(matched), matched))

said = vpm.T('  Who asks -- not said here: two of the tracks carry the '
             'same speech, so the questions would go to whichever '
             'recorder was turned up loudest.')
bled = vpm.roles_report([], heard_too)
check("the run says in one line why nothing was ranked", bled == [said],
      "%d lines: %s" % (len(bled), str(bled)[:60]))
clean = vpm.roles_report([], tracks)
check("and stays quiet where the silence has another reason", clean == [],
      "%d lines: %s" % (len(clean), str(clean)[:60]))

print("\n%d checks in %.2f s" % (done, time.time() - started))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
