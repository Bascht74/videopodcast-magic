# -*- coding: utf-8 -*-
"""Preflight for the preset: does it hold what the run needs?

check_preset in this process, the preset read replaced by a table of
presets written with the field names auphonic.com answers. In order:
which presets stop the run before the upload -- the wrong loudness, no
track template, a cut that would shorten the sound -- and which go on;
where the stop for a cut says to switch it off; that what the preset
has switched on is said, switch by switch, with its setting; that an
intro standing before the track in the preset's list is no template; and
that an intro or outro in a preset of either kind is said to be unused,
as a note, and where intro and outro come from instead.
"""
PLATFORM_BOUND = False
import os
import sys
# tests/, where the helpers and state/ lie; this file may stand in a
# folder under it, or in one under that.
HERE = os.path.dirname(os.path.abspath(__file__))
while not os.path.isfile(os.path.join(HERE, "the_program.py")) \
        and os.path.dirname(HERE) != HERE:
    HERE = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import the_program
SCRIPT = the_program.SCRIPT
import contextlib, io, time

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


# The field names are auphonic.com's: "filtering" is a switch and
# "filtermethod" its setting, as its own answers carry them; the cut
# switches and the Cut Mode as its API description names them.
TRACK = {"id": "Speaker", "algorithms": {"denoise": True,
                                         "denoisemethod": "speech_isolation",
                                         "filtering": True,
                                         "filtermethod": "autoeq"}}
INTRO = {"type": "intro", "id": "", "input_file": "intro.mp3",
         "algorithms": {"backforeground": "foreground", "leveler": True}}
OUTRO = {"type": "outro", "id": "", "input_file": "outro.mp3",
         "algorithms": {"backforeground": "foreground"}}
CASES = {
 "fits": {"algorithms": {"loudnesstarget": -16, "normloudness": True,
                         "leveler": True, "crossgate": False,
                         "filtering": True, "filtermethod": "autoeq"},
          "multi_input_files": [TRACK]},
 "other loudness": {"algorithms": {"loudnesstarget": -23, "leveler": True},
                    "multi_input_files": [TRACK]},
 "no track template": {"algorithms": {"loudnesstarget": -16},
                       "multi_input_files": []},
 "empty track template": {"algorithms": {"loudnesstarget": -16},
                          "multi_input_files": [{"id": "A",
                                                 "algorithms": {}}]},
 "cuts silence": {"algorithms": {"loudnesstarget": -16,
                                 "silence_cutter": True},
                  "multi_input_files": [TRACK]},
 "cuts fillers and coughs": {"algorithms": {"loudnesstarget": -16,
                                            "filler_cutter": True,
                                            "cough_cutter": True,
                                            "cut_mode": "apply_cuts"},
                             "multi_input_files": [TRACK]},
 "cuts set to silence": {"algorithms": {"loudnesstarget": -16,
                                        "silence_cutter": True,
                                        "cut_mode": "set_cuts_to_silence"},
                         "multi_input_files": [TRACK]},
 "cut switched off": {"algorithms": {"loudnesstarget": -16,
                                     "silence_cutter": False,
                                     "filler_cutter": False},
                      "multi_input_files": [TRACK]},
 # The API description's shape: an intro shares the list with the tracks,
 # told apart by "type", and carries settings of its own.
 "intro before the track": {"algorithms": {"loudnesstarget": -16},
                            "multi_input_files": [INTRO, dict(
                                TRACK, type="multitrack")]},
 "only an intro": {"algorithms": {"loudnesstarget": -16},
                   "multi_input_files": [INTRO]},
 "outro after the track": {"algorithms": {"loudnesstarget": -16},
                           "multi_input_files": [TRACK, OUTRO]},
 "intro and outro": {"algorithms": {"loudnesstarget": -16},
                     "multi_input_files": [INTRO, TRACK, OUTRO]},
}
said = {}
stop = {}
for name, p in CASES.items():
    vpm.read_preset = lambda key, uuid, _p=p: _p
    findings = vpm.check_preset("key", "uuid", "Podcast_Multitrack",
                                -16.0, True)
    with contextlib.redirect_stdout(io.StringIO()):
        stop[name] = bool(vpm.report_findings(
            findings, "does the preset fit the run?", False))
    said[name] = findings
    print("  %-26s -> %s" % (name, "stop" if stop[name] else "go"))


def why(name):
    """What the findings of one case said, for a failure line."""
    return " | ".join("%s %s: %s" % (b.kind, b.field, b.text)
                      for b in said.get(name, []))[:300]


def about(name, field):
    """The findings of one case under one field, by its shown name."""
    return [b for b in said.get(name, []) if b.field == vpm.T(field)]


print("\n1. Which presets stop the run before the upload")
check("a preset that fits goes on", stop["fits"] is False, why("fits"))
check("another loudness than the run's stops it",
      stop["other loudness"] is True, why("other loudness"))
check("a Multitrack preset with no track stops it",
      stop["no track template"] is True, why("no track template"))
check("a Multitrack preset with only an intro stops it",
      stop["only an intro"] is True, why("only an intro"))
check("a track switched to nothing only says so",
      stop["empty track template"] is False, why("empty track template"))
check("a preset that cuts silence stops it",
      stop["cuts silence"] is True, why("cuts silence"))
check("a preset that cuts fillers and coughs stops it",
      stop["cuts fillers and coughs"] is True, why("cuts fillers and coughs"))
check("cuts set to silence keep the length and go on",
      stop["cuts set to silence"] is False, why("cuts set to silence"))
check("a cut switched off goes on",
      stop["cut switched off"] is False, why("cut switched off"))

print("\n2. The stop for a cut says where to switch it off")
cut = about("cuts fillers and coughs", "Cutting")
advice = cut[0].advice if cut else ""
check("the cut is named by what the preset page shows",
      bool(cut) and "Cut Fillers" in cut[0].text
      and "Cut Coughs" in cut[0].text,
      "%d findings under Cutting: %s" % (len(cut), why("cuts fillers and coughs")))
check("the advice names the place in the preset",
      "Automatic Cutting" in advice and "Cut Fillers" in advice,
      "advice %r" % advice[:200])

print("\n3. What the preset has on is said, with its setting")
line = " ".join(b.text for b in about("fits", "Algorithms"))
check("a switch that is on is named",
      "leveler" in line, "Algorithms said %r" % line[:200])
check("a switch's setting stands beside it",
      "filtering (autoeq)" in line and "normloudness (-16 LUFS)" in line,
      "Algorithms said %r" % line[:200])
check("a switch that is off is not named",
      "crossgate" not in line, "Algorithms said %r" % line[:200])
track = " ".join(b.text for b in about("fits", "per track"))
check("the track template's switches are said too",
      "denoise (speech_isolation)" in track,
      "per track said %r" % track[:200])

print("\n4. An intro before the track in the preset is no template")
track = " ".join(b.text for b in about("intro before the track",
                                       "per track"))
check("the track's switches are said, not the intro's",
      "denoise (speech_isolation)" in track and "leveler" not in track,
      "per track said %r" % track[:200])

print("\n5. An intro or outro in a preset of either kind is said unused")
ends = about("intro before the track", "Intro / outro")
check("an intro in the preset is said to be unused, by name",
      [b.text for b in ends] == [vpm.T(
          'the preset has an intro -- it is not used: intro and outro come '
          'from the video files.')],
      "Intro / outro said %r" % [b.text for b in ends])
ends = about("outro after the track", "Intro / outro")
check("an outro in the preset is said to be unused, by name",
      [b.text for b in ends] == [vpm.T(
          'the preset has an outro -- it is not used: intro and outro come '
          'from the video files.')],
      "Intro / outro said %r" % [b.text for b in ends])
ends = about("intro and outro", "Intro / outro")
check("an intro and an outro together are named in one line",
      [b.text for b in ends] == [vpm.T(
          'the preset has an intro and an outro -- neither is used: intro '
          'and outro come from the video files.')],
      "Intro / outro said %r" % [b.text for b in ends])
advice = ends[0].advice if ends else ""
check("the line says where intro and outro come from instead",
      "--intro" in advice and "Kind" in advice, "advice %r" % advice[:200])
check("a preset with neither says nothing of them",
      about("fits", "Intro / outro") == [], why("fits"))
check("an intro and an outro in the preset stop nothing",
      stop["intro and outro"] is False, why("intro and outro"))
# A Singletrack preset's list holds its intro and outro alone, by type,
# as a Singletrack production lists them.
vpm.read_preset = lambda key, uuid: {"algorithms": {"loudnesstarget": -16},
                                     "multi_input_files": [INTRO, OUTRO]}
single = [b for b in vpm.check_preset("key", "uuid", "Podcast_Single",
                                      -16.0, False)
          if b.field == vpm.T('Intro / outro')]
check("a Singletrack preset's intro and outro are said unused too",
      [b.text for b in single] == [vpm.T(
          'the preset has an intro and an outro -- neither is used: intro '
          'and outro come from the video files.')],
      "Intro / outro said %r" % [b.text for b in single])
# A note is shown and stops nothing; "good" would only be counted, and
# a warning would wear the marker of a fault.
kinds = [b.kind for b in about("intro and outro", "Intro / outro") + single]
check("the Intro / outro line is a note, for either kind of preset",
      kinds == ["hint", "hint"],
      "kinds %r against ['hint', 'hint'], Multitrack then Singletrack"
      % kinds)

print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
