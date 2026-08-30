# -*- coding: utf-8 -*-
"""Who is asking the questions, as a proposal and never as a verdict.

Sebastian asked on 29.8.2026 whether the roles could be read off the
recognition. Measured over four episodes out of two productions, and
the answer had three parts:

* It carries as an ORDER, not as a threshold. In all four the guest
  asks the fewest questions per sentence and speaks the longest, and
  that order never turns round. The distance does: 20 to 27 percentage
  points in one production and 6.9 in the other, so any fixed line
  would have been wrong in the second.
* The QUESTIONS BEAT the speaking share. One episode opens with a long
  build-up in which the host talks, and the share points at the wrong
  person for 23 minutes while the share of questions is right from
  minute six.
* Switching after a question carries nothing: at four of eight host
  lines the question made no difference at all.

So this file holds the order, holds the questions above the share, and
holds the silence where there is too little to say anything from.
"""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = os.environ.get("VPM_SCRIPT") or os.path.join(
    os.path.dirname(HERE), "videopodcast-magic.py")
import importlib.util
spec = importlib.util.spec_from_file_location("vpm", SCRIPT)
vpm = importlib.util.module_from_spec(spec); sys.modules["vpm"] = vpm
spec.loader.exec_module(vpm)

bad = []


def check(what, ok, detail=""):
    print("  %-56s %s%s" % (what, "ok" if ok else "FAIL",
                            "" if ok else "   " + detail))
    if not ok:
        bad.append(what)


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
# A host who asks in most of their sentences, a guest who answers at
# length. This is the plain case, and it is the one that must never
# come out the other way round.
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
# The measured trap. The host holds the floor for a long opening, so
# the share of the talking points at the host as the guest -- while the
# questions point the right way from early on. Whoever ranks by time
# gets this episode wrong for 23 minutes.
words, tracks = episode([("Host", 25, 20, 30), ("Guest", 25, 0, 4)])
order = vpm.who_asks(tracks, words)
held = {n: t for n, _s, _q, t in order}
check("the host does hold the floor here",
      held.get("Host", 0) > held.get("Guest", 0),
      str({k: round(v, 1) for k, v in held.items()}))
check("and is still named as the one asking",
      order and order[0][0] == "Host", str([r[0] for r in order]))

print("\n3. Where nobody asks, the shorter turn decides")
# Neither asks anything. Then the order falls back on the time, and the
# one who talks less is the one more likely to be asking -- but nothing
# beyond that is claimed, which is what a ranking is for.
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

check("no words at all: nothing is claimed",
      vpm.who_asks(tracks, []) == [])
words, tracks = episode([("Host", 30, 20, 4)])
check("one track alone: nothing is claimed",
      vpm.who_asks(tracks, words) == [], str(vpm.who_asks(tracks, words)))

print("\n5. Three speakers keep their order")
# Two hosts and a guest, which is what Sebastian records. The guest
# must come last, and the one asking most must come first.
words, tracks = episode([("HostA", 25, 20, 4), ("HostB", 25, 10, 5),
                         ("Guest", 30, 0, 14)])
order = vpm.who_asks(tracks, words)
check("all three are ranked", len(order) == 3, str([r[0] for r in order]))
check("the guest comes last", order and order[-1][0] == "Guest",
      str([r[0] for r in order]))
check("and the one asking most comes first",
      order and order[0][0] == "HostA", str([r[0] for r in order]))

print("\n6. A question is what the rest of the program calls one")
# Closing marks are stripped before the mark is read, or a quoted
# question would not count.
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
check("nothing to report is nothing printed",
      vpm.roles_report([]) == [])

print("\n----")
if bad:
    print("FAIL %d of them: %s" % (len(bad), "; ".join(bad)))
    sys.exit(1)
print("All good.")
