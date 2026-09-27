# -*- coding: utf-8 -*-
"""Dry run and run cut by the window's stored transcript, and cut alike.

way_ground's production on the command line, the plan file naming the
transcript the window keeps (words_of), the words stored in each
child's own store and nothing heard. A dry run with the words stored
and one without, the same line; then the run. Judged: the dry run's
handover carries every stored word, the words move its cut into a
reaction cut before the answer, and the run carries the same words and
cuts the same shots. The words are stood in; no recogniser is asked.
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
import json
import shutil
import tempfile
import time
import the_program
import way_ground as ground

SCRIPT = the_program.SCRIPT
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
    print("\n%d checks in %.2f s" % (done, time.time() - began))
    print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
    sys.exit(1 if bad else 0)


if ground.missing():
    print("SKIPPED: " + ground.missing())
    stop()

vpm = the_program.load()
vpm.set_language("en")
ROOM = tempfile.mkdtemp(prefix="vpm_stored_words_")
SOURCE = ground.media(ground.HEARD_IN)


def said(first, last, closer):
    """Filler speech between two seconds, in sentences of six words."""
    out, t, n = [], first + 0.3, 0
    while t < last - 0.6:
        n += 1
        out.append(vpm.speech_word(t, t + 0.4, "wort" if n % 6 else closer))
        t += 0.6
    return out


# In the recording's own seconds, which are the programme's (way_ground:
# the guest's recorder rolls at 0). Every word after the last camera
# rolls and before the recording ends, so every one belongs in the cut.
# The presenter's turn from 36 s ends on a question at 41.3 s; the
# guest, who holds the floor longest, answers from 43 s -- what a
# reaction cut needs. The guest's five seconds of the next ten are
# less than the 0.7 the cut asks by default, so every line asks 0.4.
WORDS = (said(7.5, 12.5, "so.") + said(14.0, 20.0, "gut.")
         + said(21.5, 27.5, "ja.") + said(29.0, 34.5, "genau.")
         + said(36.0, 39.6, "und.")
         + [vpm.speech_word(39.3, 39.7, "Wie"),
            vpm.speech_word(39.8, 40.2, "hast"),
            vpm.speech_word(40.3, 40.7, "du"),
            vpm.speech_word(40.8, 41.0, "das"),
            vpm.speech_word(41.0, 41.3, "gemacht?")]
         + said(43.0, 48.0, "so.") + said(49.5, 53.5, "gut."))
HOLD = ["--reaction-hold", "0.4"]
# A precondition of the material, not a statement about the program.
assert any(w["word"].endswith("?") for w in WORDS)


def store(with_words):
    """A store of its own for one child; the words in it, or none."""
    where = tempfile.mkdtemp(prefix="store_", dir=ROOM)
    if with_words:
        os.environ["VPM_CACHE"] = where
        vpm.words_cache_write(vpm.file_content_mark(SOURCE), "",
                              vpm.WORD_WAYS[0][1], WORDS)
    return where


# The plan the window hands its run: the separation, and where the
# window's own transcript is kept -- one recording, at the start of its
# axis, its clock as recorded.
with open(ground.separation_file(vpm, ROOM), encoding="utf-8") as f:
    PLAN_HELD = json.load(f)
PLAN_HELD.update(production=ground.PRODUCTION, words_of={
    "language": "", "recordings": [[SOURCE, 0.0, 1.0]]})
PLAN = os.path.join(ROOM, "plan.json")
with open(PLAN, "w", encoding="utf-8") as f:
    json.dump(PLAN_HELD, f, ensure_ascii=False, indent=1)


def line(out, extra):
    """way_ground's line with the plan in place of --speakers-from."""
    argv = ground.line(SCRIPT, PLAN, out, extra)
    at = argv.index("--speakers-from")
    argv[at] = "--assign"
    return argv


def child(name, extra, with_words):
    """One run of the line; (its handover, what it said, its code)."""
    out = os.path.join(ROOM, name)
    os.makedirs(out)
    cache = store(with_words)
    code, said_, stuck = ground.line_run(
        line(out, HOLD + list(extra)), cache)
    if "--dry-run" in extra:
        found = handovers_in(cache)
    else:
        found = [ground.handover(out)] if ground.handover(out) else []
    return (found[0] if found else None,
            "code %s%s, last said %r" % (code, ", stuck" if stuck else "",
                                         said_.strip()[-160:]))


def handovers_in(where):
    """Every handover the dry run kept in *where*: a cut and a start."""
    found = []
    for root, _dirs, names in os.walk(where):
        for name in names:
            if not name.endswith(".json"):
                continue
            try:
                with open(os.path.join(root, name), encoding="utf-8") as f:
                    d = json.load(f)
            except (OSError, ValueError):
                continue
            if isinstance(d, dict) and isinstance(d.get("result"), dict):
                d = d["result"]
            if isinstance(d, dict) and isinstance(d.get("cut"), list) \
                    and d.get("start_s") is not None:
                found.append(d)
    return found


def shots(d):
    """A handover's cut as (start, end, camera), to the millisecond."""
    return [(round(float(c["start"]), 3), round(float(c["end"]), 3),
             os.path.basename(str(c["camera"])))
            for c in ((d or {}).get("cut") or ())]


def words_of(d):
    """A handover's words, as the program reads them back."""
    return vpm.words_from_handover(d or {})


# Where the guest's shot begins around the question, on the cut's time,
# which starts where the last camera rolls (5.5 s, way_ground). Without
# words at the change of speaker; with them the reaction lead (1.5 s)
# before the question ends, 41.3 - 1.5 - 5.5.
GUEST_PLAIN, GUEST_EARLY = 36.5, 34.3


def guest_at_question(d):
    """Where the guest's shot around the question begins, or None."""
    for a, _b, cam in shots(d):
        if ground.GUEST in cam and 32.0 <= a < 38.0:
            return a
    return None


def near(value, wanted):
    """Within a frame at 25 of *wanted*."""
    return value is not None and abs(value - wanted) <= 0.04


bare, bare_why = child("dry_bare", ["--dry-run"], False)
dry, dry_why = child("dry", ["--dry-run"], True)
run, run_why = child("run", [], True)
shutil.rmtree(ROOM, ignore_errors=True)

print("1. The dry run")
check("the dry run leaves a handover, with the words and without",
      bool(dry) and bool(bare), "with: %s; without: %s" % (dry_why, bare_why))
check("the dry run's handover carries every stored word",
      len(words_of(dry)) == len(WORDS),
      "%d words in the handover, %d stored" % (len(words_of(dry)),
                                               len(WORDS)))
check("with no words stored the dry run's handover carries none",
      bool(bare) and not words_of(bare),
      "%d words in the handover" % len(words_of(bare)))
check("the stored question brings the guest in early, in the dry run",
      near(guest_at_question(dry), GUEST_EARLY)
      and near(guest_at_question(bare), GUEST_PLAIN),
      "the guest's shot from %s s with the words, %s s without; wanted "
      "%.2f and %.2f" % (guest_at_question(dry), guest_at_question(bare),
                         GUEST_EARLY, GUEST_PLAIN))

print("\n2. The run")
check("the run writes a handover", bool(run), run_why)
check("the run's handover carries the dry run's words",
      bool(words_of(dry)) and [(w["start"], w["word"])
                               for w in words_of(run)]
      == [(w["start"], w["word"]) for w in words_of(dry)],
      "%d words in the run, %d in the dry run" % (len(words_of(run)),
                                                  len(words_of(dry))))
first = next((i for i, (p, r) in enumerate(zip(shots(dry), shots(run)))
              if p != r), None)
check("the run cuts the dry run's shots, question cut included",
      near(guest_at_question(run), GUEST_EARLY)
      and shots(run) == shots(dry),
      "the guest's shot from %s s, wanted %.2f; %d shots in the run, %d "
      "in the dry run; first apart: %s"
      % (guest_at_question(run), GUEST_EARLY, len(shots(run)),
         len(shots(dry)), "none" if first is None else
         "shot %d, %s against %s" % (first + 1, shots(run)[first],
                                     shots(dry)[first])))
stop()
