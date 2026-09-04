# -*- coding: utf-8 -*-
"""The tracks of a run are read once, whatever the reading is used for.

Two things live off that reading: who is in the cut, and the proposal
saying which microphone a separated voice was speaking into. Until
31.8.2026 each fetched its own, and an hour of conversation was decoded
twice per track for an answer that was already there.

Two runs. In one the separation speaks for neither track, so both are
measured into the cut: the reading is handed every track, and it happens
once. In the other the separation speaks for both, so nobody needs the
reading for the cut -- it happens all the same, once, and the proposal
is made out of it. A run that saved the second reading by dropping the
proposal would have saved it just as well and said less.

The reading is stood in for. What is counted is how often the program
asks, which no real measurement would say more clearly, and the stand-in
opens every file it is handed so that it refuses what the real one
refuses.
"""
import contextlib
import io
import os
import sys
import tempfile
import time
import wave

import the_program

HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = the_program.SCRIPT

began = time.time()
vpm = the_program.load()

done = 0
bad = []


def check(name, ok, extra=""):
    global done
    done += 1
    print("  %-58s %s %s" % (name, "ok" if ok else "FAIL", extra))
    if not ok:
        bad.append("%s [%s]" % (name, extra or "no numbers"))


#------------------------------------------------------------- Material

D = tempfile.mkdtemp(prefix="vpmreadonce_")
MIC_A = os.path.join(D, "Mic_Anna.wav")
MIC_B = os.path.join(D, "Mic_Bea.wav")
CAM_A = os.path.join(D, "CamOne.mov")
CAM_B = os.path.join(D, "CamTwo.mov")
ROOM = os.path.join(D, "room.wav")
for path in (MIC_A, MIC_B):
    with wave.open(path, "wb") as f:
        f.setnchannels(1); f.setsampwidth(2); f.setframerate(8000)
        f.writeframes(b"\0" * 16000)
for path in (CAM_A, CAM_B):
    with open(path, "wb") as f:
        f.write(b"\0" * 16)

# A separation that named nobody -- SPEAKER_00 upwards is what a model
# hands back -- beside two tracks a person has named. That is the case
# the microphone proposal is for. The turns are long because a voice
# under VOICE_MIN_SPEECH_S is not matched to a microphone at all.
VOICES = [("SPEAKER_00", [(0.0, 15.0), (30.0, 45.0)]),
          ("SPEAKER_01", [(15.0, 30.0), (45.0, 60.0)])]
SAID = {"Anna": [(0.0, 15.0), (30.0, 45.0)],
        "Bea": [(15.0, 30.0), (45.0, 60.0)]}
WANTED_READINGS = 1
TRACKS = [{"name": "Anna", "axis": MIC_A, "camera": CAM_A, "blocks": [MIC_A]},
          {"name": "Bea", "axis": MIC_B, "camera": CAM_B, "blocks": [MIC_B]}]


class Args(object):
    pass


def run_with(separated):
    """One call of speakers_for_the_cut, and what it asked for.

    Returns (what each reading was handed, the log). The stand-in for
    the reading refuses what the real one refuses: speakers_from_tracks
    decodes every file it is handed and answers one entry per track, so
    a call counted here is a call the program would really have paid
    for, and no track is invented that a run would not have.
    """
    handed = []

    def reading_of(tracks, note=None, **rest):
        for _name, path, _offset in tracks:
            with open(path, "rb"):
                pass
        handed.append([name for name, _p, _o in tracks])
        return [(name, list(SAID.get(name) or [])) for name, _p, _o in tracks]

    args = Args()
    args._speakers = (VOICES, "the separation in this run")
    args._separated = separated
    was = vpm.speakers_from_tracks
    vpm.speakers_from_tracks = reading_of
    try:
        with contextlib.redirect_stdout(io.StringIO()) as log:
            vpm.speakers_for_the_cut(args, TRACKS)
    finally:
        vpm.speakers_from_tracks = was
    return handed, log.getvalue()


print("1. A run whose tracks the separation does not speak for")
# The separation was made on a recording that is no track here, so both
# tracks are measured into the cut.
handed, _text = run_with([ROOM])
# The precondition, and it stands first: with no reading at all the
# count below would be 0 and read as the best possible result.
check("the reading is handed every track of the run",
      handed[:1] == [["Anna", "Bea"]], "first reading got %s, wanted %s"
      % (handed[0] if handed else "nothing", ["Anna", "Bea"]))
check("and the run reads them once, not once per use",
      len(handed) == WANTED_READINGS, "%d readings %s, wanted %d"
      % (len(handed), handed, WANTED_READINGS))

print("\n2. A run whose tracks the separation speaks for")
# Nobody is added to the cut from a microphone here -- and the reading
# happens anyway, because the proposal lives off it.
handed, text = run_with([MIC_A, MIC_B])
check("the reading is made even where the cut has no use for it",
      len(handed) == WANTED_READINGS, "%d readings %s, wanted %d"
      % (len(handed), handed, WANTED_READINGS))
# The heading is asked for through the catalogue: a literal would tie
# the check to one language and one wording.
head = vpm.T('\nWHICH MICROPHONE -- a proposal, and nothing is set '
             'from it').strip()
check("and the microphone proposal comes out of that one reading",
      head in text, "%d lines in the log, the proposal's heading %s"
      % (len(text.splitlines()),
         "among them" if head in text else "not among them"))

print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
