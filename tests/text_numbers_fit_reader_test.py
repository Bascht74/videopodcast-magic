# -*- coding: utf-8 -*-
"""A number takes the language's form for a person, never for a machine.

The sections in the order they come. The first runs German and asks a
count and a measured distance for the thousands mark and the decimal
comma; the second asks the same two in English, where both marks are
the other way round -- that is what shows the marks come out of the
catalogue and not out of the program. The third asks for both marks in
one number, where a thousands mark stands beside a decimal place. The
fourth asks for the thousands mark on a whole number, which has no
decimal place to carry the other one. The fifth asks a size, where a
unit stands beside the digits and must not be counted among them. The
sixth asks an offset that no single measurement can reach, only the
chain of them. The seventh asks what is written where there is no
number to write. The last is the direction that costs something when
it is wrong: what leaves for a machine -- the filter chain handed to
ffmpeg, the iXML block written into the delivered track, the name that
track is written under -- keeps plain digits under German too.

The channel facts, the picture's timecode, the camera file's frame
rate and the bleed between two microphones are stand-in dictionaries,
so what is judged is what the program writes, not what a recorder
would have measured. No wording is held against anything, only the
shape of the number, so the checks stand whether a catalogue carries
the sentence or not.
"""
import contextlib
import io
import sys
import time

import the_program

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


def quietly(work):
    """Run work with its printing caught, and hand back what it returned."""
    with contextlib.redirect_stdout(io.StringIO()):
        return work()


def printed(work):
    """Run work and hand back what it printed, for the ones that report."""
    caught = io.StringIO()
    with contextlib.redirect_stdout(caught):
        work()
    return caught.getvalue()


def holding(text, *pieces):
    """The first line of text carrying one of pieces, for the FAIL line."""
    for line in text.splitlines():
        if any(p in line for p in pieces):
            return line.strip()
    return ""


# Two channels whose delay puts them apart: 3.6 ms of spacing is
# 1.2348 m at 343 m/s, and the line rounds that to one decimal. Nothing
# in it is agreed anywhere, so no count comes along and the decimal
# mark stands on its own.
SPACED = {"channels": 2, "readable": True, "silent": [False, False],
          "level": [-20.0, -21.0], "pair_same": [0.1], "pair_zero": [0.0],
          "pair_apart": [3.6]}
# Four digits, so the thousands mark has somewhere to stand.
MANY = 1234


def spacing_line(code):
    vpm.set_language(code)
    return quietly(lambda: vpm.channel_joins(SPACED))[0][3]


print("1. German: a person reads it, so the language decides")
vpm.set_language("de")
counted = vpm.channel_text(MANY)
check("a channel count carries the German thousands mark",
      "1.234" in counted and "1234" not in counted,
      "%r -- wanted %r in it and %r not" % (counted, "1.234", "1234"))

said = spacing_line("de")
check("the measured microphone spacing carries the German decimal comma",
      "1,2 m" in said and "1.2 m" not in said,
      "%r -- wanted %r in it and %r not" % (said, "1,2 m", "1.2 m"))

print("\n2. English: the same two numbers, both marks the other way round")
vpm.set_language("en")
counted = vpm.channel_text(MANY)
check("the same channel count carries the English thousands comma",
      "1,234" in counted and "1234" not in counted,
      "%r -- wanted %r in it and %r not" % (counted, "1,234", "1234"))

said = spacing_line("en")
check("the same spacing carries the English decimal point",
      "1.2 m" in said and "1,2 m" not in said,
      "%r -- wanted %r in it and %r not" % (said, "1.2 m", "1,2 m"))

print("\n3. German: one number with a thousands mark and a decimal place")
# For years the program had one helper for each half and none for
# both, so a number with a decimal place came out ungrouped: "2000,0
# ms" stood in the same German line as "1.234 points". 1234.5 has
# somewhere for each of the two marks to stand.
BOTH = 1234.5
vpm.set_language("de")
written_out = vpm.number_text(BOTH, 1)
check("a number with a decimal place carries the thousands mark as well",
      written_out == "1.234,5",
      "number_text(%s, 1) is %r, wanted %r"
      % (BOTH, written_out, "1.234,5"))

# And a line a person really sees. The timecode check reports how far
# the sound sits from the picture in frames, and that branch of it runs
# up to a minute: 59 seconds at 25 frames a second is 1475 frames. The
# picture's facts are made up here; nothing is read off a file.
LATE_S = 59.0
FPS = 25.0
AT_HOUR = 3600.0
report = printed(lambda: vpm.report_timecode_check(
    AT_HOUR, {"tc": "01:00:00:00", "fps": FPS}, LATE_S))
said = holding(report, "1.475,0", "1475,0")
check("the frames a timecode is out by carry the thousands mark too",
      "1.475,0" in report and "1475,0" not in report,
      "%r -- wanted %r in it and %r not, for %s s at %s frames a second"
      % (said, "1.475,0", "1475,0", LATE_S, FPS))

print("\n4. German: a whole number, with no decimal place beside it")
# The other half of the same fault. "%.0f" writes no point, so
# decimal_text found nothing to replace and handed the digits back
# ungrouped, in every language alike. 2000 has one place for a
# thousands mark and none at all for a decimal one.
ROUND = 2000.0
vpm.set_language("de")
written_out = vpm.number_text(ROUND, 0)
check("a whole number is grouped and carries no decimal mark",
      written_out == "2.000",
      "number_text(%s, 0) is %r, wanted %r"
      % (ROUND, written_out, "2.000"))

# And a line a person really sees. The preflight says how many frames a
# camera file is short of what its container claims: two hours at 25
# frames a second would be 180000, the file holds 150000, so it is
# 30000 frames and 1200 seconds short. The frame rate comes from a
# stand-in here, and the path is one nothing lies under, so what the
# rest of the check reads off the disk is "nothing there".
CLAIMED_FPS = 25.0
FRAMES = 150000
TWO_HOURS = 7200.0
SHORT_BY = int(TWO_HOURS * CLAIMED_FPS) - FRAMES
MADE_UP = {"path": "/tmp/no-such-camera.mov", "nominal": CLAIMED_FPS,
           "mean": FRAMES / TWO_HOURS, "duration": TWO_HOURS,
           "videos": FRAMES, "varies": False, "spread": 0.0,
           "offset_s": TWO_HOURS - FRAMES / CLAIMED_FPS, "codec": "h264",
           "width": 1920, "height": 1080, "gaps": 0}
real_one = vpm.preflight.inspect_frame_rate
vpm.preflight.inspect_frame_rate = lambda path: dict(MADE_UP)
try:
    found, _facts = quietly(
        lambda: vpm.preflight.check_camera_file(MADE_UP["path"]))
finally:
    vpm.preflight.inspect_frame_rate = real_one
report = "\n".join(f.text for f in found)
said = holding(report, "30.000", "30000")
check("the frames a camera file is short by carry the thousands mark too",
      "30.000" in report and "30000" not in report,
      "%r -- wanted %r in it and %r not, for %s frames of the %s a "
      "container claiming %s s at %s holds"
      % (said, "30.000", "30000", SHORT_BY, int(TWO_HOURS * CLAIMED_FPS),
         TWO_HOURS, CLAIMED_FPS))

print("\n5. German: the unit stands beside the number, not inside it")
# A size went into the helper as one finished string with its unit
# already in it, and then only the decimal mark could be set: telling
# the thousands apart needs the digits told apart from the rest first.
# A 1 TB card is the first size with four digits before the point.
CARD_MB = 1024000.0
vpm.set_language("de")
said = vpm.as_data_size(CARD_MB)
check("a card's size keeps its unit and carries the thousands mark",
      said == "1.024,0 GB",
      "as_data_size(%s) is %r, wanted %r" % (CARD_MB, said, "1.024,0 GB"))

print("\n6. German: an offset no single measurement could reach")
# The bleed between two microphones is read at most 120 ms out, so no
# one hop can print four digits -- the chain of them can. Ten tracks in
# a line, every hop at that cap and all leaning the same way, and the
# tenth stands 1080 ms off the first. Only the reading is a stand-in;
# the fit, the chain and the line are the program's own.
CAP_MS = 120.0
IN_A_LINE = 10


def bleed_at_the_cap(tracks, rate=16000):
    """Stand in for the crosstalk reading: every neighbour at the cap."""
    heard = {}
    for i in range(len(tracks) - 1):
        heard[(i, i + 1)] = [(s + 0.5, CAP_MS) for s in range(3)]
        heard[(i + 1, i)] = [(s + 0.5, -CAP_MS) for s in range(3)]
    return heard, []


# The first two land inside the 250 ms the program still believes and
# would have their files rewritten. They are handed no source, so the
# run leaves them where they are; from the third on the line is printed.
chained = [{"name": "role %d" % i, "axis": "/tmp/no-such-track-%d.wav" % i,
            "source": "" if i < 3 else "/tmp/no-such-track-%d.wav" % i,
            "a": 0.0, "b": 1.0} for i in range(IN_A_LINE)]
real_bleed = vpm.bearings.measure_offsets_by_crosstalk
vpm.bearings.measure_offsets_by_crosstalk = bleed_at_the_cap
try:
    report = printed(
        lambda: vpm.bearings.verify_alignment(chained, 0.0, 60.0))
finally:
    vpm.bearings.measure_offsets_by_crosstalk = real_bleed
said = holding(report, "+1.080", "+1080")
check("a chained offset carries the thousands mark on the line that "
      "refuses it",
      "+1.080 ms" in report and "+1080 ms" not in report,
      "%r -- wanted %r in it and %r not, over %s hops of %s ms"
      % (said, "+1.080 ms", "+1080 ms", IN_A_LINE - 1, CAP_MS))

print("\n7. Where there is no number, the line says so and the run goes on")
# A fit with no spread of its own reports its error as inf, and that
# error is printed in the same line as the drift. The half-helper wrote
# the word; the whole one has to as well, or the report stops the run at
# the very place it was describing.
try:
    written_out = vpm.number_text(float("inf"), 2)
except Exception as trouble:
    written_out = "stopped: %s" % type(trouble).__name__
check("a number that is not finite is written out, not thrown",
      written_out == "inf",
      "number_text(inf, 2) is %r, wanted %r" % (written_out, "inf"))

print("\n8. German: a machine reads it, so the digits stay plain")
# From here on the run is German, which is the language whose thousands
# mark is a full stop -- the one that would silently turn a rate into a
# different number, a file name into another file, an XML field into
# text no reader parses.
vpm.set_language("de")

# The resample chain that takes the clock drift out. Both branches of
# it name the sample rate, so which one this machine takes -- with soxr
# or without -- does not decide the check.
chain = quietly(lambda: vpm.rate_filter_chain(1.0000123))
check("the resample chain handed to ffmpeg keeps its sample rates plain",
      "48000" in chain and "48.000" not in chain and "4.800.000" not in chain,
      "%r -- wanted %r in it, %r and %r not"
      % (chain, "48000", "48.000", "4.800.000"))

# The iXML block goes into every track the program delivers, and
# Resolve, Premiere and Media Composer read it. 1234567890123 samples
# since midnight splits into 287 and 1912276171 -- ten digits, three
# places for a thousands mark to appear in.
xml = vpm.build_ixml("Guest", 1234567890123, 30.0)
numbered = [line.strip() for line in xml.splitlines()
            if "SAMPLE_RATE" in line or "MIDNIGHT_LO" in line]
check("the iXML block written into the track keeps its numbers plain",
      "<FILE_SAMPLE_RATE>48000<" in xml and ">1912276171<" in xml
      and "48.000" not in xml and "1.912.276.171" not in xml,
      "%r -- wanted 48000 and 1912276171 in them, 48.000 and 1.912.276.171 not"
      % (numbered,))

# The track's own name: channel_tracks labels a cut-out track, and the
# file it is written to is "ready_" plus that label made safe.
written = "ready_%s.wav" % vpm.safe_filename(
    vpm.channel_name("Mixer", (MANY - 1, MANY)))
check("the name a track is written under keeps its channel number plain",
      "1234" in written and "1.234" not in written,
      "%r -- wanted %r in it and %r not" % (written, "1234", "1.234"))

vpm.set_language("en")

print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
