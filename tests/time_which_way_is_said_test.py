# -*- coding: utf-8 -*-
"""The run says which way put a track on the axis, and how sure it is.

Three ways lead to a place and the report used to name only two of
them, on only one of the two roads. In order: the note itself, where
the plain curve says nothing and the two later ways say who they are;
the phase, which carries its sharpness against the floor and admits
that no drift was measured; the road without a picture, which said
nothing at all and showed +0.00 ppm beside a drift nobody knows; and
last that the wording lives in one place, so the two roads cannot
drift apart again. The road with a picture is not driven here -- it is
minutes of material for one line of text -- so what it is held to is
that it can say nothing of its own.
"""
import ast
import contextlib
import io
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = os.environ.get("VPM_SCRIPT") or os.path.join(
    os.path.dirname(HERE), "videopodcast-magic.py")
import importlib.util
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


# The three answers the alignment hands back, written out rather than
# measured: what a real run puts in them is time_second_try_places's
# question, and a second reading of it here would only repeat it.
PLAIN = {"quality": 0.62, "points": 51, "candidates": 60,
         "spread_ms": 4.0, "ppm": -3.2, "ppm_error": 0.4}
BANDS = dict(PLAIN, from_bands=True)
SHARP = 28.7
# The phase answers where and not how fast, so it brings back no
# sample points -- and with fewer than three of them the alignment
# writes neither a drift nor a spread. That is why the line beside the
# note reads "+0.00 ppm": the nought is a default, not a measurement.
PHASE = {"quality": 0.01, "points": 0, "candidates": 60,
         "from_phase": True, "phase_sharp": SHARP, "phase_s": 4.0}

print("1. The note says which way answered")
check("the plain curve is the ordinary answer and adds nothing",
      vpm.which_way_placed(PLAIN, "") == "",
      "%r came back, wanted nothing at all"
      % (vpm.which_way_placed(PLAIN, ""),))
bands_note = vpm.which_way_placed(BANDS, "")
check("the bands that move say so",
      bands_note == vpm.T('placed on the bands that move'),
      "%r against %r" % (bands_note, vpm.T('placed on the bands that move')))
kept = vpm.which_way_placed(BANDS, "two blocks joined")
check("and a note the track already carried is kept, not written over",
      kept == "two blocks joined, " + vpm.T('placed on the bands that move'),
      "%r, wanted the old note, a comma and the new one" % (kept,))

print("\n2. The phase says how close it came, and what it did not measure")
phase_note = vpm.which_way_placed(PHASE, "")
check("the phase says so as well",
      "phase" in phase_note.lower(), "%r" % (phase_note,))
check("and carries the sharpness it was judged on",
      "28.7" in phase_note,
      "%r, wanted the measured sharpness of %.1f in it" % (phase_note, SHARP))
check("and the floor beside it, so anybody can see how close it was",
      ("%.1f" % vpm.PHASE_SHARP_ENOUGH) in phase_note,
      "%r, wanted the floor of %.1f in it"
      % (phase_note, vpm.PHASE_SHARP_ENOUGH))
# The line beside the note prints "+0.00 ppm" for this track, because
# the phase answers where and not how fast. Without a word the zero
# reads as a drift that was measured.
check("and says the drift is unknown rather than leaving 0.00 ppm to "
      "be read as one",
      "unknown" in phase_note.lower(), "%r" % (phase_note,))
vpm.set_language("de")
german = vpm.which_way_placed(PHASE, "")
vpm.set_language("en")
check("the sharpness carries the decimal mark of the language it is "
      "printed in",
      "28,7" in german and "28.7" not in german,
      "in German the note reads %r -- wanted 28,7 in it and 28.7 not"
      % (german,))

print("\n3. The road without a picture says it too")
# measure_tracks_against_each_other reports every track it places, and
# it never said which way had placed one -- so a track put there by
# phase showed "+0.00 ppm" and nothing else. The alignment is stood in
# for: what it answers is section 1's material, and this asks only what
# the report makes of it.
kept_align = vpm.align_audio_to_video
kept_count = vpm.sample_count
LENGTHS = {"/x/Presenter.wav": 48000 * 60, "/x/Guest.wav": 48000 * 30}
try:
    vpm.sample_count = lambda p: LENGTHS[p]
    vpm.align_audio_to_video = lambda *a, **k: (4.0, 1.0, dict(PHASE))
    tracks = [{"name": "Presenter", "source": "/x/Presenter.wav",
               "hint": "", "blocks": ["/x/Presenter.wav"]},
              {"name": "Guest", "source": "/x/Guest.wav",
               "hint": "", "blocks": ["/x/Guest.wav"]}]
    said = io.StringIO()
    with contextlib.redirect_stdout(said):
        placed = vpm.measure_tracks_against_each_other(tracks)
    text = said.getvalue()
finally:
    vpm.align_audio_to_video = kept_align
    vpm.sample_count = kept_count
check("both tracks are placed, so there is a line to read",
      len(placed) == 2, "%d tracks placed, wanted 2" % len(placed))
# The way a track was placed is written at the END of its line, so the
# evidence is read from there: cut off the front, both runs show the
# same first hundred and fifty characters and the line proves nothing.
check("the report there names the phase as well",
      "phase" in text.lower(),
      "the report ends %r"
      % (text.replace("\n", " | ")[-170:],))
check("and it carries the sharpness, beside the +0.00 ppm",
      "28.7" in text and "0.00 ppm" in text,
      "sharpness %.1f in it: %r, and +0.00 ppm in it: %r -- the report "
      "ends %r"
      % (SHARP, "28.7" in text, "0.00 ppm" in text,
         text.replace("\n", " | ")[-170:]))

print("\n4. One wording, in one place")
# Two roads report the same measurement. Written out twice they drift,
# and that is how one of them came to say nothing at all for versions.
source = open(SCRIPT, encoding="utf-8").read()
program = ast.parse(source)


def built_in_places(wording):
    """How many places in the program build this text through T().

    Read out of the syntax, not out of the characters: one wording
    wrapped over two lines is one call either way, and counting
    characters would go red at the next reflow while nothing drifted.
    The German catalogue carries the English as its key, and a key
    builds nothing, so only a call to T is counted.
    """
    return sum(1 for node in ast.walk(program)
               if isinstance(node, ast.Call)
               and isinstance(node.func, ast.Name) and node.func.id == "T"
               and len(node.args) == 1
               and isinstance(node.args[0], ast.Constant)
               and node.args[0].value == wording)


PHASE_SAID = ('placed by phase, sharpness %s against a floor of %s, '
              'drift unknown')
built = built_in_places(PHASE_SAID)
check("the phase wording is built in exactly one place in the program",
      built == 1,
      "%d places build %r -- wanted 1; none means the wording moved and "
      "two mean a second one waiting to drift" % (built, PHASE_SAID))
BANDS_SAID = 'placed on the bands that move'
bands = built_in_places(BANDS_SAID)
check("and so is the wording for the bands that move",
      bands == 1,
      "%d places build %r -- wanted 1" % (bands, BANDS_SAID))

print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
