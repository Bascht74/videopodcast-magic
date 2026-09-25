# -*- coding: utf-8 -*-
"""A file's details say their units and headings in the reader's language.

First the details the file list shows under two sound files and a camera
file, in German: bit depth, channel words, picture heading, and the bit
depth in the colour row. Then the same under a catalogue of the test's
own that marks every text it hands out, asked for a word outside every
mark -- a unit glued on beside a number, kHz, MB and fps among them --
and the preflight's lines on the two sound files with them. Limits: the
list itself is not opened; the colour row's names and the camera row
come out of the file and are left out of the marks; and a word handed
into a text as a value sits inside that text's marks, which is why the
channel words are asked in German.
"""
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time

# tests/, where the helpers and state/ lie; this file may stand in a
# folder under it, or in one under that.
HERE = os.path.dirname(os.path.abspath(__file__))
while not os.path.isfile(os.path.join(HERE, "the_program.py")) \
        and os.path.dirname(HERE) != HERE:
    HERE = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import the_program

began = time.time()
vpm = the_program.load()
vpm.set_language("en")

done = 0
bad = []


def check(name, ok, extra=""):
    global done
    done += 1
    print("  %-58s %s %s" % (name, "ok" if ok else "FAIL", extra))
    if not ok:
        bad.append("%s [%s]" % (name, extra or "no numbers"))


def made(*args):
    """Have ffmpeg write one file, quietly, and stop the run if it cannot."""
    subprocess.run(["ffmpeg", "-v", "error", "-y"] + list(args), check=True)


FOLDER = tempfile.mkdtemp(prefix="vpm_units_")
# Three files, each for a different wording: a one-channel sound file
# at 24 bit with a timecode, a two-channel one in float, and a camera
# file with a timecode track and two channels of its own sound.
DEEP = os.path.join(FOLDER, "Guest_REC00005.wav")
FLOAT = os.path.join(FOLDER, "Presenter_REC00005.wav")
CAMERA = os.path.join(FOLDER, "WideCam_C0005.mov")


def material():
    """Build the three files; inside the run, so a failure still counts."""
    made("-f", "lavfi", "-i",
         "sine=frequency=300:duration=1:sample_rate=48000",
         "-ac", "1", "-c:a", "pcm_s24le", "-write_bext", "1",
         "-metadata", "time_reference=%d" % (3600 * 48000), DEEP)
    made("-f", "lavfi", "-i",
         "sine=frequency=300:duration=1:sample_rate=48000",
         "-ac", "2", "-c:a", "pcm_f32le", FLOAT)
    made("-f", "lavfi", "-i", "testsrc=size=160x90:rate=25:duration=1",
         "-f", "lavfi", "-i",
         "sine=frequency=300:duration=1:sample_rate=48000",
         "-ac", "2", "-c:v", "libx264", "-pix_fmt", "yuv420p", "-c:a", "aac",
         "-timecode", "01:00:00:00", "-shortest", CAMERA)
    # A precondition of the material, not a judgement about the program.
    missing = [p for p in (DEEP, FLOAT, CAMERA) if not os.path.exists(p)]
    assert not missing, "material: ffmpeg wrote no %s" % missing


def details():
    """The rows the file list shows under the three files, as it asks them."""
    return (vpm.metadata.audio_summary(DEEP),
            vpm.metadata.audio_summary(FLOAT),
            vpm.metadata.video_summary(CAMERA, vpm.video_facts(CAMERA)))


try:
    material()
    print("1. German: the file details say the German forms")
    vpm.set_language("de")
    deep, floating, camera = details()
    # The German words are written out: what is asked is that German
    # arrives, and a catalogue lookup here would agree with a missing
    # entry as readily as with a present one.
    said = deep[0][1]
    check("a sound file's bit depth is said in German",
          "24 Bit" in said and "24 bit" not in said,
          "%r -- wanted %r in it and %r not" % (said, "24 Bit", "24 bit"))
    said = floating[0][1]
    check("a float sound file's bit depth is said in German",
          "32 Bit" in said and "32 bit" not in said,
          "%r -- wanted %r in it and %r not" % (said, "32 Bit", "32 bit"))
    said = deep[0][1]
    check("a one-channel sound file is called Mono in German",
          "Mono" in said and "mono" not in said,
          "%r -- wanted %r in it and %r not" % (said, "Mono", "mono"))
    said = dict(camera).get(vpm.T('Camera audio'), "")
    check("a camera's two channels of sound are called Stereo in German",
          "Stereo" in said and "stereo" not in said,
          "%r -- wanted %r in it and %r not" % (said, "Stereo", "stereo"))
    headings = [k for k, _v in camera]
    check("the camera file's picture row is headed in German",
          "Bild" in headings and "Video" not in headings,
          "the rows are headed %r -- wanted %r among them and %r not"
          % (headings, "Bild", "Video"))
    said = dict(camera).get(vpm.T('Colour'), "")
    check("the camera file's colour row says its bit depth in German",
          "8 Bit" in said and "8 bit" not in said,
          "%r -- wanted %r in it and %r not" % (said, "8 Bit", "8 bit"))

    print("\n2. Every word in them comes out of the catalogue")

    class Marked(dict):
        """A catalogue that answers every text with the text in marks.

        The two number marks are left alone: they are asked of every
        number, and a mark inside the digits would say nothing more.
        """

        def get(self, key, default=None):
            """The text in marks, for any text at all."""
            return key if key in (",", ".") else "⟦%s⟧" % key

    OUTSIDE = re.compile(r"⟦[^⟦⟧]*⟧")
    LETTER = re.compile(r"[^\W\d_]+")

    def glued(rows):
        """The words in rows that no mark holds, row by row."""
        found = []
        for heading, value in rows:
            line = "%s: %s" % (heading, value)
            bare = None
            while bare != line:
                bare, line = line, OUTSIDE.sub("", line)
            if LETTER.search(line):
                found.append("%s: %s -> %r" % (heading, value,
                                               LETTER.findall(line)))
        return found

    vpm.CATALOGUE["qa"] = Marked()
    taken = vpm.set_language("qa")
    deep, floating, camera = details()
    left = glued(deep + floating)
    check("no word in a sound file's details is set outside the catalogue",
          not left,
          "language %r; %d rows carry a word no text holds: %s"
          % (taken, len(left), "; ".join(left)[:300]))
    # The colour row and the camera row are resolve/'s, see the head.
    theirs = (vpm.T('Colour'), vpm.T('Camera'))
    own = [(k, v) for k, v in camera if k not in theirs]
    left = glued(own)
    check("no word in a camera file's own rows is set outside the catalogue",
          len(own) == len(camera) - 2 and not left,
          "language %r; %d of %d rows asked, %d carry a word no text "
          "holds: %s" % (taken, len(own), len(camera), len(left),
                         "; ".join(left)[:300]))
    # Only the text: the field beside it is the file's own name.
    lines = [("", x.text) for p in (DEEP, FLOAT)
             for x in vpm.check_audio_file(p)[0]]
    left = glued(lines)
    check("no word the preflight says about a sound file is set outside "
          "the catalogue",
          len(lines) >= 2 and not left,
          "language %r; %d lines asked, %d carry a word no text holds: %s"
          % (taken, len(lines), len(left), "; ".join(left)[:300]))
except Exception:
    import traceback
    traceback.print_exc()
    bad.append("crash")
finally:
    vpm.CATALOGUE.pop("qa", None)
    vpm.set_language("en")
    shutil.rmtree(FOLDER, ignore_errors=True)

print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
