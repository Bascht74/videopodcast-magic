# -*- coding: utf-8 -*-
"""#38 Stage 5c: the decisions of the assignment table without a window."""
import os
HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = os.environ.get("VPM_SCRIPT") or os.path.join(
    os.path.dirname(HERE), "videopodcast-magic.py")
import sys, tempfile, shutil, importlib.util
spec = importlib.util.spec_from_file_location(
    "vpm", SCRIPT)
vpm = importlib.util.module_from_spec(spec); sys.modules["vpm"] = vpm
spec.loader.exec_module(vpm)

error = []
def check(name, ok, extra=""):
    print("  %-58s %s %s" % (name, "ok" if ok else "FAIL", extra))
    if not ok:
        error.append(name)

D = tempfile.mkdtemp(prefix="assignment5c_")
def file(n):
    p = os.path.join(D, n)
    open(p, "wb").write(b"\0" * 16)
    return p

print("1. Which rows the upper table gets")
t1, t2 = file("Guest_REC001.wav"), file("Co-host_REC002.wav")
b1, b2, b3 = (file("Wide_C003.mov"), file("Guest_C009.mov"),
              file("Host_C005.mov"))
rows, cam_audio, own = vpm.assignment_rows([t1, t2], [b1, b2, b3])
check("two audio recordings -> two rows", len(rows) == 2, str(len(rows)))
check("no camera audio", cam_audio is False)
check("no own-audio rows", own == {})

rows, cam_audio, own = vpm.assignment_rows([t1, t2], [b1, b2, b3],
                                           own_flag_cameras=[b1])
check("with one own-audio camera -> three rows", len(rows) == 3,
        str(len(rows)))
check("it sits at the back", rows[-1][0] == [b1])
check("and is noted as own audio",
        own == {os.path.abspath(b1): os.path.abspath(b1)})

rows, cam_audio, own = vpm.assignment_rows([], [b1, b2, b3])
check("no audio, three cameras -> camera audio", cam_audio is True)
check("one row per camera", [r[0] for r, _ in rows] == [b1, b2, b3])
# Every camera is a track here, so each one maps to itself. A camera cut
# into two would map both pieces to it.
check("every camera is its own track",
        own == {os.path.abspath(b): os.path.abspath(b) for b in (b1, b2, b3)})

rows, cam_audio, own = vpm.assignment_rows([], [b1], own_flag_cameras=[b1])
check("only one camera -> no camera audio", cam_audio is False)
check("but its checkbox counts", len(rows) == 1 and own)
rows, cam_audio, own = vpm.assignment_rows([], [])
check("nothing at all -> nothing at all", rows == [] and cam_audio is False)

print("\n2. Which camera a track is preselected to")
TARGETS = ["Wide_C003.mov", "Guest_C009.mov", "Host_C005.mov",
           vpm.MIX_ONLY, vpm.IGNORE_AUDIO]
VIDEOS = [b1, b2, b3]
check("set by hand still applies",
        vpm.preselected_camera("Host_C005.mov", TARGETS, "Guest", VIDEOS)
        == "Host_C005.mov")
check("ignore stays as well",
        vpm.preselected_camera(vpm.IGNORE_AUDIO, TARGETS, "Guest", VIDEOS)
        == vpm.IGNORE_AUDIO)
check("camera gone -> guessed anew",
        vpm.preselected_camera("Gone_C099.mov", TARGETS, "Guest", VIDEOS)
        == "Guest_C009.mov")
check("without an old choice, by the name",
        vpm.preselected_camera(None, TARGETS, "Guest", VIDEOS)
        == "Guest_C009.mov")
# No camera carries this speaker's name, not even a similar one.
check("no match -> mix only",
        vpm.preselected_camera(None, TARGETS, "Visitor", VIDEOS)
        == vpm.MIX_ONLY)
check("empty name -> mix only",
        vpm.preselected_camera(None, TARGETS, "", VIDEOS) == vpm.MIX_ONLY)
# The camera the audio came out of is where a row starts, but only until
# somebody says otherwise: a clip-on microphone in one camera may belong
# to a person another camera is filming.
check("own camera is the preselection",
        vpm.preselected_camera(None, TARGETS, "Guest", VIDEOS,
                           own_camera="Wide_C003.mov")
        == "Wide_C003.mov")
check("but a setting made by hand beats it",
        vpm.preselected_camera("Host_C005.mov", TARGETS, "Guest", VIDEOS,
                           own_camera="Wide_C003.mov")
        == "Host_C005.mov")

print("\n3. What the new video file is called")
f = vpm.camera_output_name
check("speakers into the middle",
        f("Interview 1", "Hosts_08141714_C002.mov", ["Host", "Co-host"])
        == "Interview 1_Hosts_Host+Co-host_08141714_C002",
        f("Interview 1", "Hosts_08141714_C002.mov", ["Host", "Co-host"]))
check("camera already named like the speaker -> not twice",
        f("Interview 2", "Guest_08141858_C009.mov", ["Guest"])
        == "Interview 2_Guest_08141858_C009",
        f("Interview 2", "Guest_08141858_C009.mov", ["Guest"]))
# The typo is "Gueest", not "Guset": a swapped pair only scores 0.80 and
# stays under the 0.85 mark, so the check would test nothing.
check("not twice with a typo either",
        "Gueest_Guest" not in f("I", "Gueest_C009.mov", ["Guest"]),
        f("I", "Gueest_C009.mov", ["Guest"]))
check("without speakers the full mix",
        f("Interview 2", "Wide_08141855_C003.mov", ["Audio-Full-Mix"])
        == "Interview 2_Wide_Audio-Full-Mix_08141855_C003",
        f("Interview 2", "Wide_08141855_C003.mov", ["Audio-Full-Mix"]))
check("camera name without a separator -> appended at the back",
        f("I", "C009.mov", ["Guest"]) == "I_C009_Guest",
        f("I", "C009.mov", ["Guest"]))
check("empty production becomes 'Production'",
        f("", "Camera_C001.mov", []).startswith("Production_"),
        f("", "Camera_C001.mov", []))
check("only spaces counts as empty",
        f("   ", "Camera_C001.mov", []).startswith("Production_"))
check("empty speaker names drop out",
        f("I", "Camera_C001.mov", ["", "  ", "Anna"])
        == "I_Camera_Anna_C001",
        f("I", "Camera_C001.mov", ["", " ", "Anna"]))
check("a whole path works too",
        f("I", "/deep/in/folder/Camera_C001.mov", ["Anna"])
        == "I_Camera_Anna_C001")
check("dots in the camera name separate too",
        f("I", "Camera.C001.mov", ["Anna"]) == "I_Camera_Anna_C001",
        f("I", "Camera.C001.mov", ["Anna"]))
check("no crash without a speaker list",
        isinstance(f("I", "Camera_C001.mov"), str))

print("\n4. What comes out in the same order as before")
# The three cameras of a real two-part interview, in the shape they
# were delivered in: a production name with spaces and a number.
REAL = [("Wide_08141855_C003.mov", ["Audio-Full-Mix"],
         "Interview Example Town 2_Wide_Audio-Full-Mix_08141855_C003"),
        ("Guest_08141858_C009.mov", ["Guest"],
         "Interview Example Town 2_Guest_08141858_C009"),
        ("Hosts_08141855_C005.mov", ["Host", "Co-host"],
         "Interview Example Town 2_Hosts_Host+Co-host_"
         "08141855_C005")]
for cam, spk, want in REAL:
    have = f("Interview Example Town 2", cam, spk)
    check("as delivered: %s" % cam.split("_")[0], have == want, have)

print("\n5. The interface really calls this path")
source = open(SCRIPT, encoding="utf-8").read()
for call in ("chains, camera_audio, own = assignment_rows(",
             "camera_value = Value(preselected_camera(",
             "suggestion = camera_output_name("):
    check("calls %s" % call.split("=")[-1].strip()[:22], call in source)
check("the old name computation is gone",
        'parts = re.split(r"[_\\-. ]", camera_stem' not in source)
check("the old camera choice is gone",
        "hit = camera_for_speaker(name_value.get(), videos)" not in source)

shutil.rmtree(D, ignore_errors=True)
print("\n%s" % ("All good." if not error
                else "FAIL: %s" % ", ".join(error)))
sys.exit(1 if error else 0)
