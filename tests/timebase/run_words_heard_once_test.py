# -*- coding: utf-8 -*-
"""A run listens only where the window's transcript is not stored.

way_ground's production on the command line, the plan file naming the
transcript the window keeps (words_of), the recognition switched on
and stood in by one that counts. Two runs: the window's words stored
in the run's own store, and none. Judged: with them the run asks no
recogniser and carries them; without them it asks once and carries
what it heard. The stand-in's words are made up; nothing listens.
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
ROOM = tempfile.mkdtemp(prefix="vpm_heard_once_")
SOURCE = ground.media(ground.HEARD_IN)


def said(first, last, word):
    """One word every 0.6 s between two seconds, each a sentence."""
    out, t = [], first + 0.3
    while t < last - 0.6:
        out.append(vpm.speech_word(t, t + 0.4, word))
        t += 0.6
    return out


# The window's words, in the recording's own seconds (the programme's,
# way_ground): inside every camera's stretch, so all belong in the cut.
STORED = said(7.5, 12.5, "stored.") + said(14.0, 20.0, "stored.")
# What the stand-in hears in the run's mix, on the cut's time: another
# word, so the handover says whose words it carries.
HEARD = said(2.0, 8.0, "heard.") + said(20.0, 26.0, "heard.")


def store(with_words):
    """A store of its own for one child; the window's words in it, or none."""
    where = tempfile.mkdtemp(prefix="store_", dir=ROOM)
    if with_words:
        os.environ["VPM_CACHE"] = where
        vpm.words_cache_write(vpm.file_content_mark(SOURCE), "",
                              vpm.WORD_WAYS[0][1], STORED)
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

# The program as a child, its recognition stood in: every call leaves
# the file it was asked about in *asked*, and HEARD comes back.
def child_text(asked):
    """The child's program: load, stand the recognition in, run."""
    return "\n".join([
        "import json, sys",
        "sys.path.insert(0, %r)" % HERE,
        "import the_program",
        "vpm = the_program.load()",
        "def stand_in(audio_path, language='', way=''):",
        "    with open(%r, 'a') as f:" % asked,
        "        f.write(audio_path + '\\n')",
        "    return json.loads(%r), 'stand-in'" % json.dumps(HEARD),
        "vpm.recognise_speech = stand_in",
        "sys.argv = ['videopodcast-magic'] + sys.argv[1:]",
        "sys.exit(vpm.main())"])


def child(name, with_words):
    """One run; (its handover, the files it listened to, what it said)."""
    out = os.path.join(ROOM, name)
    os.makedirs(out)
    asked = os.path.join(ROOM, name + ".asked")
    argv = ground.line(SCRIPT, PLAN, out)
    argv[argv.index("--speakers-from")] = "--assign"
    # The recognition is the subject here, so it is not switched off.
    argv.remove("--no-speech-recognition")
    argv[1:2] = ["-c", child_text(asked)]
    code, said_, stuck = ground.line_run(argv, store(with_words))
    try:
        with open(asked, encoding="utf-8") as f:
            heard_in = f.read().splitlines()
    except OSError:
        heard_in = []
    return (ground.handover(out), heard_in,
            "code %s%s, last said %r" % (code, ", stuck" if stuck else "",
                                         said_.strip()[-160:]))


def words_of(d):
    """A handover's words, as (start, word), as the program reads them."""
    return [(round(w["start"], 3), w["word"])
            for w in vpm.words_from_handover(d or {})]


kept, kept_asked, kept_why = child("kept", True)
bare, bare_asked, bare_why = child("bare", False)
shutil.rmtree(ROOM, ignore_errors=True)
STORED_HERE = [w for _s, w in words_of(kept)]
HEARD_HERE = words_of(bare)
WANT_HEARD = [(round(w["start"], 3), w["word"]) for w in HEARD]

print("1. The window's words stored")
check("the run leaves a handover, with the words stored and without",
      bool(kept) and bool(bare),
      "with: %s; without: %s" % (kept_why, bare_why))
check("with the window's words stored the run asks no recogniser",
      not kept_asked and STORED_HERE == ["stored."] * len(STORED),
      "the recogniser asked %d times against 0 (%s); the handover carries "
      "%d stored and %d heard words against %d stored"
      % (len(kept_asked), ", ".join(os.path.basename(p)
                                    for p in kept_asked) or "none",
         STORED_HERE.count("stored."), STORED_HERE.count("heard."),
         len(STORED)))

print("\n2. None stored")
check("with none stored the run asks the recogniser once",
      len(bare_asked) == 1 and HEARD_HERE == WANT_HEARD,
      "the recogniser asked %d times against 1 (%s); the handover carries "
      "%d words against the %d it heard, first %s against %s"
      % (len(bare_asked), ", ".join(os.path.basename(p)
                                    for p in bare_asked) or "none",
         len(HEARD_HERE), len(WANT_HEARD), HEARD_HERE[:1], WANT_HEARD[:1]))
stop()
