# -*- coding: utf-8 -*-
"""Window, project file and command line come to the same cut.

Three doors lead into one run: the settings a person makes in the
window, the project file they are written into, and the command line
the window builds out of them. A fault comes in through one while the
other two are watched, and it sits in the caller rather than in the
function it calls. In order: the file is found, read and given back
whole; a line is built out of it and the parser takes every switch on
it; the cut numbers and the cut rules; the five kinds a clip
can have; the assignment; the time window, the wide shot at the edges
and the loudness; and last the census -- no setting the window writes
stops half way, and the five that carry no switch are named.
"""
import argparse
import ast
import io
import json
import os
import sys
import tempfile
import time
import the_program

began = time.time()
HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = the_program.SCRIPT

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


# ---------------------------------------------------------------------
# The material. Nothing is opened or measured here: run_argv, the
# project reader and the parser all work on paths, so empty files are
# the whole production.
# ---------------------------------------------------------------------
folder = tempfile.mkdtemp(prefix="vpm_three_ways_")
out_folder = os.path.join(folder, "Result")
os.makedirs(out_folder)


def touch(name):
    path = os.path.join(folder, name)
    with io.open(path, "wb") as f:
        f.write(b"")
    return path


SOUND_A = touch("SoundA.wav")
SOUND_A2 = touch("SoundA_2.wav")
SOUND_B = touch("SoundB.wav")
CAM_A = touch("CamA.mov")
CAM_B = touch("CamB.mov")
WIDE = touch("Wide.mov")
OPENING = touch("Opening.mov")
CLOSING = touch("Closing.mov")
DISCARD = touch("Discard.mov")

FILES = [(SOUND_A, "audio"), (SOUND_B, "audio"), (CAM_A, "video"),
         (CAM_B, "video"), (WIDE, "video"), (OPENING, "video"),
         (CLOSING, "video"), (DISCARD, "video")]

# Precondition of the material, not a judgement about the program: the
# project reader asks the file system whether each entry is still there.
assert all(os.path.exists(p) for p, _a in FILES), folder

PRODUCTION = "Three Ways"
IN_POINT, OUT_POINT = "00:00:10:00", "00:12:30:00"
LUFS = -16.0
LANGUAGE_TAG = "eng"
CUT = {"min-edit-duration": "2.5", "min-speech-to-switch": "0.9",
       "edit-change-delay": "0.4", "reaction-lead": "2.0",
       "wide-after": "55", "wide-latest": "100",
       "wide-length": "6", "wide-most": "12", "silence-hold": "1.7",
       "on-question": vpm.SHOT_LISTENER, "on-monologue": vpm.SHOT_WIDE,
       "on-together": vpm.SHOT_HOLD, "on-uncertain": vpm.SHOT_LISTENER,
       "on-silence": vpm.SHOT_HOLD_BRIEF}

# Precondition of the material again: not one of the answers is the
# built-in default. A command line that quietly fell back to the
# defaults would otherwise look exactly like one that carried them.
assert all(CUT[s] != d for s, _c, d, _u, _k, _l in vpm.CUT_FIELDS), CUT
assert all(CUT[s] != d for s, _c, d, _v, _k, _l in vpm.CUT_CHOICES), CUT

KIND_OF = {CAM_A: vpm.TYPE_CONTENT, CAM_B: vpm.TYPE_CONTENT,
           WIDE: vpm.TYPE_WIDE, OPENING: vpm.TYPE_INTRO,
           CLOSING: vpm.TYPE_OUTRO, DISCARD: vpm.TYPE_IGNORED}
WHO_ON_WHAT = {"Anna": CAM_A, "Ben": CAM_B}
CAMERA_NAMES = {CAM_A: "Show_CamA", CAM_B: "Show_CamB", WIDE: "Show_Wide"}

# ---------------------------------------------------------------------
# Door one: the answers as the window holds them, written into the
# project file in the shape settings_extend writes it -- the kinds and
# the assignment inside "assignment", the grouping as block -> recording.
# ---------------------------------------------------------------------
ASSIGNMENT = {}
for name, camera in sorted(WHO_ON_WHAT.items()):
    recording = SOUND_A if name == "Anna" else SOUND_B
    ASSIGNMENT["audio:" + recording] = [name, os.path.basename(camera)]
for path, out_name in sorted(CAMERA_NAMES.items()):
    ASSIGNMENT["video:" + path] = out_name
    ASSIGNMENT["own:" + path] = False
for path, kind in sorted(KIND_OF.items()):
    ASSIGNMENT["kind:" + path] = kind

WRITTEN = {"format": vpm.FILE_FORMAT, "version": vpm.VERSION,
           "files": [{"path": p, "kind": a} for p, a in FILES],
           "production": PRODUCTION, "out_folder": out_folder,
           "multitrack": True, "wide_at_edges": False,
           "camera_cut": dict(CUT), "in_point": IN_POINT,
           "out_point": OUT_POINT, "assignment": ASSIGNMENT,
           "preset": vpm.PRESET_NONE, "speech_language": LANGUAGE_TAG,
           "lufs": LUFS, "speakers": {}, "speakers_source": "",
           "speakers_local": False, "apart": [SOUND_B],
           "together": {SOUND_A2: SOUND_A}, "channels": {}}

project_path = os.path.join(
    out_folder, "%s%s.json" % (vpm.PROJECT_PREFIX,
                               vpm.safe_filename(PRODUCTION)))
with io.open(project_path, "w", encoding="utf-8") as f:
    f.write(json.dumps(WRITTEN, ensure_ascii=False, indent=1))

# ---------------------------------------------------------------------
# Door two: read it back the way a person opening a project does.
# ---------------------------------------------------------------------
print("1. What the window wrote comes back off the disc")
found, found_at = vpm.find_project_file(out_folder)
check("the project file is found again where the window put it",
      found is not None
      and os.path.abspath(found_at or "") == os.path.abspath(project_path),
      "%d files lie in the folder, the reader took %r, wanted %r"
      % (len(os.listdir(out_folder)), os.path.basename(found_at or ""),
         os.path.basename(project_path)))

d = found if isinstance(found, dict) else {}
complaint = vpm.format_complaint(d)
check("and it is not refused for the naming it was written with",
      complaint == "",
      "format %r against %d, the complaint is %r"
      % (d.get("format"), vpm.FILE_FORMAT, complaint[:60]))

present, missing = vpm.project_files(d)
check("every file it lists comes back, and none is counted missing",
      len(present) == len(FILES) and missing == [],
      "%d of %d files back, %d counted missing"
      % (len(present), len(FILES), len(missing)))

# What project_open puts into the widgets, in the same turns: the kinds
# come out of "assignment", and together_now() turns the file's
# block -> recording round into the recording-first pairs a run wants.
assignment = d.get("assignment") or {}
back = {
    "files": present,
    "clip_kinds": dict((p, assignment["kind:" + p]) for p, _a in present
                       if "kind:" + p in assignment),
    "out_folder": d.get("out_folder") or "",
    "multitrack": bool(d.get("multitrack")),
    "camera_audio_only": False,
    "dry_run": False,
    "rows": [{"blocks": [k[len("audio:"):]], "speakers": value[0],
              "camera_choice": value[1], "own_audio": False,
              "from_camera": "", "audio_done": None}
             for k, value in sorted(assignment.items())
             if k.startswith("audio:")],
    "cameras": [{"path": k[len("video:"):], "name": value}
                for k, value in sorted(assignment.items())
                if k.startswith("video:")],
    "production": d.get("production") or "",
    "in_point": d.get("in_point") or "",
    "out_point": d.get("out_point") or "",
    "cut": d.get("camera_cut") or {},
    "wide_at_edges": bool(d.get("wide_at_edges", True)),
    "speakers_of": None,
    "speakers_wanted": (bool(d["speakers_local"])
                        if "speakers_local" in d else None),
    "voices": [],
    # The "no Auphonic" entry is the preset here, so no key and no
    # preset name travel -- and a key never stands in a file anyway.
    "key": "", "preset": "", "done_folder": "",
    "speech_language": d.get("speech_language") or "",
    "lufs": d.get("lufs"),
    "apart": sorted(d.get("apart") or []),
    "together": [[target, source] for source, target
                 in sorted((d.get("together") or {}).items())
                 if target and target != source],
}

# ---------------------------------------------------------------------
# Door three: the command line the window builds, and the parser a run
# reads it with.
# ---------------------------------------------------------------------
handle, assign_path = tempfile.mkstemp(prefix="vpm_assign_", suffix=".json",
                                       dir=folder)
os.close(handle)
argv, plan, messages = vpm.run_argv(back, assign_path)
check("a command line is built out of it, and nothing is refused",
      argv is not None
      and [m[0] for m in messages if m[0] == "error"] == [],
      "%d words on the line, %d messages of kinds %s"
      % (len(argv or []), len(messages), [m[0] for m in messages]))


def read_back(line):
    """Parse a built command line. Returns (namespace, leftovers, refusal).

    argparse answers a value it will not take by leaving the process,
    and a test that walked out there would print no verdict at all. So
    the refusal is caught and handed on as a sentence the check prints.
    """
    try:
        space, over = vpm.build_argument_parser().parse_known_args(line[1:])
        return space, over, ""
    except SystemExit as e:
        return argparse.Namespace(), [], "the parser walked out (%s)" % e


ns, left_over, refused = read_back(list(argv or ["videopodcast_magic.py"]))
check("the parser knows every switch that command line carries",
      left_over == [] and refused == "",
      "%d of %d words unknown: %s %s"
      % (len(left_over), len(argv or []) - 1, left_over[:6], refused))


def got(field):
    return getattr(ns, field, None)


print("\n2. The cut numbers and the cut rules")


def field_of(switch):
    """What a run calls the switch. --edit-change-delay is the one whose
    name in the parser is not its name on the command line."""
    return "delay" if switch == "edit-change-delay" \
        else switch.replace("-", "_")


numbers_off = ["%s wanted %s got %r" % (s, CUT[s], got(field_of(s)))
               for s, _c, _d, _u, _k, _l in vpm.CUT_FIELDS
               if got(field_of(s)) != float(CUT[s])]
check("every cut number reaches the run as the file has it",
      numbers_off == [],
      "%d of %d differ: %s" % (len(numbers_off), len(vpm.CUT_FIELDS),
                               "; ".join(numbers_off[:3])))

rules_off = ["%s wanted %r got %r" % (s, CUT[s], got(field_of(s)))
             for s, _c, _d, _v, _k, _l in vpm.CUT_CHOICES
             if got(field_of(s)) != CUT[s]]
check("every cut rule reaches the run as the file has it",
      rules_off == [],
      "%d of %d differ: %s" % (len(rules_off), len(vpm.CUT_CHOICES),
                               "; ".join(rules_off)))

print("\n3. The five kinds a clip can have")
in_list = [os.path.abspath(p) for p in (got("files") or [])]
check("the clip set to intro becomes the intro and leaves the file list",
      got("intro") == OPENING and os.path.abspath(OPENING) not in in_list,
      "--intro is %r, and it stands %d times among the %d files"
      % (os.path.basename(got("intro") or ""),
         in_list.count(os.path.abspath(OPENING)), len(in_list)))
check("the clip set to outro becomes the outro and leaves the file list",
      got("outro") == CLOSING and os.path.abspath(CLOSING) not in in_list,
      "--outro is %r, and it stands %d times among the %d files"
      % (os.path.basename(got("outro") or ""),
         in_list.count(os.path.abspath(CLOSING)), len(in_list)))
check("the clip set to wide shot becomes it and stays a camera",
      (got("wide_shot") or []) == [WIDE]
      and os.path.abspath(WIDE) in in_list,
      "--wide-shot is %s, and it stands %d times among the %d files"
      % ([os.path.basename(p) for p in (got("wide_shot") or [])],
         in_list.count(os.path.abspath(WIDE)), len(in_list)))
check("the clip set to ignore reaches the run through no door at all",
      os.path.abspath(DISCARD) not in in_list
      and DISCARD not in (got("intro"), got("outro"))
      and DISCARD not in (got("wide_shot") or []),
      "%d times among the %d files, %d times as intro, outro or wide shot"
      % (in_list.count(os.path.abspath(DISCARD)), len(in_list),
         [got("intro"), got("outro")].count(DISCARD)
         + (got("wide_shot") or []).count(DISCARD)))
WANTED_FILES = sorted(os.path.abspath(p)
                      for p in (SOUND_A, SOUND_B, CAM_A, CAM_B, WIDE))
check("the recordings and the content cameras are the run's file list",
      sorted(in_list) == WANTED_FILES,
      "%d files wanted, %d came: %s"
      % (len(WANTED_FILES), len(in_list),
         sorted(os.path.basename(p) for p in in_list)))

print("\n4. Who speaks on which camera")
check("the run is handed an assignment file, and the line names it",
      got("multitrack") is True and got("assign") == assign_path,
      "--multitrack is %r, --assign is %r, wanted %r"
      % (got("multitrack"), os.path.basename(got("assign") or ""),
         os.path.basename(assign_path)))
pairs = dict((t.get("speakers"), t.get("camera"))
             for t in ((plan or {}).get("tracks_of") or []))
check("and in it every speaker stands on the camera the file gave them",
      pairs == WHO_ON_WHAT,
      "%d of %d pairs: %s, wanted %s"
      % (len(pairs), len(WHO_ON_WHAT),
         sorted((k, os.path.basename(v or "")) for k, v in pairs.items()),
         sorted((k, os.path.basename(v)) for k, v in WHO_ON_WHAT.items())))

print("\n5. The time window, the edges and the loudness")
check("In point and Out point reach the run as the file has them",
      got("in_point") == IN_POINT and got("out_point") == OUT_POINT,
      "in %r wanted %r, out %r wanted %r"
      % (got("in_point"), IN_POINT, got("out_point"), OUT_POINT))
# The one setting that travels as its own opposite: the window holds
# "keep the wide shot at the edges", the run is told when not to.
edges_argv, _plan, _messages = vpm.run_argv(dict(back, wide_at_edges=True),
                                            assign_path)
edges_ns, _over, _refused = read_back(
    list(edges_argv or ["videopodcast_magic.py"]))
check("the edges are only taken away where the file turned them off",
      got("no_wide_edges") is True
      and getattr(edges_ns, "no_wide_edges", None) is False,
      "off in the file gives %r, on in the file gives %r"
      % (got("no_wide_edges"), getattr(edges_ns, "no_wide_edges", None)))
check("the loudness reaches the run as the file has it",
      got("lufs") == LUFS, "--lufs is %r, wanted %r" % (got("lufs"), LUFS))

print("\n6. Nothing the window writes stops half way")
# Every setting the window puts into the project file, taken from the
# one place that puts them there. A setting added there and nowhere
# else is the fault this section is for.
KEYS = []
for node in ast.walk(ast.parse(the_program.text())):
    if isinstance(node, ast.FunctionDef) and node.name == "settings_extend":
        for inner in ast.walk(node):
            if not isinstance(inner, ast.Assign):
                continue
            for target in inner.targets:
                if (isinstance(target, ast.Subscript)
                        and isinstance(target.value, ast.Name)
                        and target.value.id == "d"
                        and isinstance(target.slice, ast.Constant)):
                    KEYS.append(target.slice.value)

# setting in the file -> the switch it becomes, what a run reads it as,
# and the answer that has to arrive.
CENSUS = (("out_folder", "--out", "out", out_folder),
          ("multitrack", "--multitrack", "multitrack", True),
          ("wide_at_edges", "--no-wide-edges", "no_wide_edges", True),
          ("in_point", "--in-point", "in_point", IN_POINT),
          ("out_point", "--out-point", "out_point", OUT_POINT),
          ("speech_language", "--speech-language", "speech_language",
           LANGUAGE_TAG),
          ("lufs", "--lufs", "lufs", LUFS),
          ("apart", "--apart", "apart", [SOUND_B]),
          ("together", "--together", "together", [[SOUND_A, SOUND_A2]]),
          ("preset", "--without-auphonic", "without_auphonic", True),
          ("speakers_local", "--no-speakers-local", "no_speakers_local",
           True),
          ("camera_cut", "--min-edit-duration", "min_edit_duration", 2.5))
# The five that carry no switch, and the door each takes instead:
# the production names the job in the assignment file, the assignment
# reaches the run as the kinds above and the tracks in that same file,
# the separation and its source travel in it as well, and the channel
# split decides which tracks the file list is made of.
OTHER_DOOR = ("production", "assignment", "speakers", "speakers_source",
              "channels")

lost = ["%s (%s): %r wanted %r"
        % (key, switch, got(field), wanted)
        for key, switch, field, wanted in CENSUS
        if switch not in (argv or []) or got(field) != wanted]
check("every setting with a switch of its own arrives with its answer",
      lost == [], "%d of %d lost: %s"
      % (len(lost), len(CENSUS), "; ".join(lost[:3])))
check("and the settings that carry no switch are the five named here",
      set(KEYS) == set(k for k, _s, _f, _w in CENSUS) | set(OTHER_DOOR),
      "%d settings written, %d followed; unfollowed %s, gone %s"
      % (len(set(KEYS)), len(CENSUS) + len(OTHER_DOOR),
         sorted(set(KEYS) - set(k for k, _s, _f, _w in CENSUS)
                - set(OTHER_DOOR)),
         sorted((set(k for k, _s, _f, _w in CENSUS) | set(OTHER_DOOR))
                - set(KEYS))))

print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
