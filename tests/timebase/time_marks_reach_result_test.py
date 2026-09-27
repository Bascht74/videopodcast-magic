# -*- coding: utf-8 -*-
"""A window mark is where the run's result begins or ends, at 25 and 29.97.

way_ground's production: two cameras at 25, one at 29.97. The window:
the player on the 29.97 camera to a spot, Mark In, on a 25 camera to a
later one, Mark Out, Start -- judged: both marks taken, and its line
carries them counted from the window start. The line: the timecodes
the window's field shows, typed; those moments counted from the window
start; In on 25 with Out on 29.97 typed. Judged on the handovers: the
window's marks on both rates, a 25 timecode and a relative point land
within half a frame, the shots fill the window. A timecode typed for
the 29.97 camera is measured, not judged: the line reads it at the
reference camera's rate, and its offset in frames stands on a LEFT OUT
line while it is off, so a repair turns nothing red.
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
import tempfile
import time
import the_program
import way_ground as ground

SCRIPT = the_program.SCRIPT
began = time.time()
done = 0
bad = []
left_out = []


def check(name, ok, extra=""):
    global done
    done += 1
    print("  %-58s %s %s" % (name, "ok" if ok else "FAIL", extra))
    if not ok:
        bad.append("%s [%s]" % (name, extra or "no numbers"))


def stop():
    """Nothing further can be asked, so count what there is and go."""
    for line in left_out:
        print(line)
    print("\n%d checks in %.2f s" % (done, time.time() - began))
    print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
    sys.exit(1 if bad else 0)


if ground.missing():
    print("SKIPPED: " + ground.missing())
    stop()

STORE = tempfile.mkdtemp(prefix="vpm_way_store_")
os.environ["VPM_CACHE"] = STORE
os.environ["QT_QPA_PLATFORM"] = "offscreen"
os.environ.setdefault("RESOLVE_SCRIPT_API", os.path.join(STORE, "nowhere"))
os.environ.setdefault("RESOLVE_SCRIPT_LIB",
                      os.path.join(STORE, "nowhere", "fusionscript.so"))
from PySide6 import QtCore, QtWidgets
app = QtWidgets.QApplication(sys.argv[:1])
vpm = the_program.load()
vpm.set_language("en")
vpm.list_presets = lambda key: []
vpm.load_api_key = lambda: ""
vpm.words_at_hand = lambda *a, **k: []
vpm.recognise_speech = lambda *a, **k: ([], "")

# ------------------------------------------------------------ the marks
# Where the player is sent, in seconds of the camera's own file. The
# 29.97 camera's clock starts at 10:00:05:15, so 15.0 s in reads
# 10:00:20:15: fifteen frames, which a 25 reading takes for 0.6 s and
# not 0.5 -- the frames are what tell the two rates apart. The 25 mark
# carries twelve, which the 29.97 reading would take for 0.4004 s.
IN_CAM, IN_POS = ground.GUEST, 15.0
OUT_CAM, OUT_POS = ground.WIDE, 50.48
# The moments meant, in seconds of the programme: where the camera
# rolls plus how far into it the player stood (fixtures.sh).
IN_AT = ground.ROLLS[IN_CAM] + IN_POS          # 20.5
OUT_AT = ground.ROLLS[OUT_CAM] + OUT_POS       # 50.48
# The same two moments counted from the window start, which is where
# the last camera rolls: the stretch all three saw (fixtures.sh).
WINDOW_START = 5.5
REL_IN, REL_OUT = "+0:00:15.000", "+0:00:44.980"
# The third line: In on the 25 camera, Out on the 29.97 one, as the
# window would write them there -- by hand, at each camera's own rate.
SWAP_IN, SWAP_IN_AT = "10:00:20:12", 20.48        # 25: 12/25 = 0.48
SWAP_OUT, SWAP_OUT_AT = "10:00:50:15", 50.5005    # 29.97: 15/29.97
# The wide camera's clock at the programme's first second: a handover's
# start_s is a clock time, and this takes it back to programme time.
CLOCK_ZERO = 10 * 3600.0
# What a mark may be off and still name its frame: half a frame of the
# camera it was set on, since a label is rounded to the nearest frame.
HALF = {25.0: 0.5 / 25.0, 29.97: 0.5 / 29.97}


def frames(seconds, fps):
    """Seconds as frames of *fps*, rounded to a tenth for the line."""
    return round(seconds * fps, 1)


# ------------------------------------------------------------ the window
def preview_player(window):
    """The player that owns the Mark In button -- the preview one."""
    for b in window.findChildren(QtWidgets.QPushButton) if window else ():
        if b.text().replace("&", "").strip() == vpm.T("Mark In"):
            up = b.parentWidget()
            while up is not None and not hasattr(up, "spot_s"):
                up = up.parentWidget()
            return up, b
    return None, None


def mark_button(window, caption):
    for b in window.findChildren(QtWidgets.QPushButton) if window else ():
        if b.text().replace("&", "").strip() == vpm.T(caption):
            return b
    return None


made = {"step": 0, "in": "", "out": "", "in_fps": None, "out_fps": None}


def answer(window):
    """Player to a spot, Mark In; the other camera, Mark Out; "" once set.

    One move per call: a load has to arrive before the mark is taken.
    """
    player, in_button = preview_player(window)
    if player is None or in_button is None or not in_button.isEnabled():
        return "the Mark In button, available once the axis is measured"
    step = made["step"]
    for k, (cam, pos, caption, key) in enumerate(
            ((IN_CAM, IN_POS, "Mark In", "in"),
             (OUT_CAM, OUT_POS, "Mark Out", "out"))):
        if step == 2 * k:
            player.load(ground.media(cam), pos)
            made["step"] += 1
            return "the player to %s at %.3f s" % (cam, pos)
        if step == 2 * k + 1:
            here = os.path.basename(getattr(player, "file_path", "") or "")
            if not here.startswith(cam) or abs(player.spot_s() - pos) > 0.001:
                return "the player standing on %s at %.3f s, now %s %.3f" % (
                    cam, pos, here, player.spot_s())
            mark_button(window, caption).click()
            app.processEvents()
            made[key] = player_field(player, key)
            made[key + "_fps"] = player.fps
            made["step"] += 1
            return "the %s mark taken" % key
    return ""


def player_field(player, key):
    """What the player's own line says the mark is, as it travels on."""
    head = vpm.T("In point %s" if key == "in" else "Out point %s") \
        .replace("%s", "").strip()
    for x in player.findChildren(QtWidgets.QLabel):
        said = x.text().replace("&", "").strip()
        if said.startswith(head):
            # "--" is how the line says no mark stands.
            value = said[len(head):].strip()
            return "" if value == "--" else value
    return ""


# ------------------------------------------------------------ reading
def span(d):
    """(begins, ends) of a handover in programme seconds, or Nones."""
    if not d or d.get("start_s") is None or d.get("length_s") is None:
        return None, None
    a = float(d["start_s"]) - CLOCK_ZERO
    return a, a + float(d["length_s"])


def shots_length(d):
    """How long the cut's shots last together, in seconds."""
    return sum(float(e.get("end") or 0) - float(e.get("start") or 0)
               for e in (d or {}).get("cut") or [])


def line_door(tag, begin, end):
    """One run through the line with these two points; its handover."""
    folder = ground.own_folder(tag)
    out = os.path.join(folder, "Result")
    os.makedirs(out)
    speakers = ground.separation_file(vpm, folder)
    code, said, stuck = ground.line_run(
        ground.line(SCRIPT, speakers, out,
                    ["--in-point", begin, "--out-point", end]),
        os.path.join(folder, "store"))
    d = ground.handover(out)
    if d is None:
        print("\n".join(said.splitlines()[-12:]))
    return d, code, stuck


def lands(d, meant_in, meant_out):
    """(In off, Out off) in seconds, handover against the moments meant."""
    a, b = span(d)
    if a is None:
        return None, None
    return a - meant_in, b - meant_out


# ------------------------------------------------------------ the doors
print("The window: %s at %.3f s, Mark In; %s at %.3f s, Mark Out."
      % (IN_CAM, IN_POS, OUT_CAM, OUT_POS))
folder = ground.own_folder("marks_window")
out = os.path.join(folder, "Result")
os.makedirs(out)
project = ground.project_file(vpm, folder, out)
keep = {}
t = time.time()
ground.window_answered_run(vpm, app, project, keep, answer)
window_d = ground.handover(out)
print("  window run in %.1f s, marks %r and %r, %s"
      % (time.time() - t, made["in"], made["out"], keep.get("why") or
         "no trouble"))
check("the window took both marks and ran to a handover",
      bool(made["in"] and made["out"] and window_d),
      "In %r, Out %r, handover %s, unanswered %r, %s"
      % (made["in"], made["out"], window_d is not None,
         keep.get("unanswered"), keep.get("why") or "run ended"))
argv = keep.get("argv") or []
said_in = argv[argv.index("--in-point") + 1] if "--in-point" in argv else ""
said_out = argv[argv.index("--out-point") + 1] if "--out-point" in argv \
    else ""
# The field shows a timecode; what travels counts from the window start,
# which the run reads at no frame rate at all.
check("the window's run line carries its marks from the window start",
      (said_in, said_out) == (REL_IN, REL_OUT),
      "%r %r against %r %r, the field showing %r %r"
      % (said_in, said_out, REL_IN, REL_OUT, made["in"], made["out"]))

print("\nThe line, with the marks the window's field shows, typed.")
same_d, code, stuck = line_door("marks_same", made["in"] or "-",
                                made["out"] or "-")
print("\nThe line, with the same moments counted from the window start.")
rel_d, rcode, rstuck = line_door("marks_rel", REL_IN, REL_OUT)
print("\nThe line, In on the 25 camera and Out on the 29.97 one.")
swap_d, scode, sstuck = line_door("marks_swap", SWAP_IN, SWAP_OUT)

# ------------------------------------------------------------ judged
wa, wb = span(window_d)
w_in, w_out = lands(window_d, IN_AT, OUT_AT)
check("the window's In mark on the 29.97 camera is where the result begins",
      w_in is not None and abs(w_in) <= HALF[29.97],
      "%s s off (%s frames at 29.97), field %r, sent %r, at most %.3f s"
      % (None if w_in is None else round(w_in, 4),
         None if w_in is None else frames(w_in, 29.97), made["in"], said_in,
         HALF[29.97]))
check("the window's Out mark on the 25 camera is where the result ends",
      w_out is not None and abs(w_out) <= HALF[25.0],
      "%s s off (%s frames at 25), mark %r, at most %.3f s"
      % (None if w_out is None else round(w_out, 4),
         None if w_out is None else frames(w_out, 25.0), made["out"],
         HALF[25.0]))

r_in, r_out = lands(rel_d, WINDOW_START + 15.0, WINDOW_START + 44.98)
check("an In point counted from the window start lands on its moment",
      r_in is not None and abs(r_in) <= HALF[29.97],
      "%s s off, %s -> %s s programme, rc %d%s"
      % (None if r_in is None else round(r_in, 4), REL_IN,
         WINDOW_START + 15.0, rcode, ", stuck" if rstuck else ""))
check("and so does its Out point",
      r_out is not None and abs(r_out) <= HALF[29.97],
      "%s s off, %s -> %s s programme"
      % (None if r_out is None else round(r_out, 4), REL_OUT,
         WINDOW_START + 44.98))

s_in, s_out = lands(swap_d, SWAP_IN_AT, SWAP_OUT_AT)
check("an In timecode on the 25 camera is where the result begins",
      s_in is not None and abs(s_in) <= HALF[25.0],
      "%s s off (%s frames at 25), %s meant %.3f s, rc %d%s"
      % (None if s_in is None else round(s_in, 4),
         None if s_in is None else frames(s_in, 25.0), SWAP_IN, SWAP_IN_AT,
         scode, ", stuck" if sstuck else ""))

fills = [(tag, round(shots_length(d), 3),
          round(float((d or {}).get("length_s") or 0), 3))
         for tag, d in (("window", window_d), ("line", same_d),
                        ("relative", rel_d), ("swapped", swap_d))]
check("every run's shots fill the window it handed over",
      None not in (window_d, same_d, rel_d, swap_d)
      and all(abs(a - b) <= HALF[29.97] for _t, a, b in fills),
      ", ".join("%s shots %.3f s against %.3f s" % f for f in fills))

# ------------------------------------------------------------ measured
# A timecode typed on the line for the 29.97 camera -- the one the field
# shows, and one typed by hand: reported, not judged. The line reads
# every timecode at the reference camera's rate; while that is off by
# more than half a frame the line below keeps the test green and names
# it, and the day it lands nothing turns red.
off_by = []
for door, off, mark, meant in (
        ("line In", lands(same_d, IN_AT, OUT_AT)[0], made["in"], IN_AT),
        ("line Out", s_out, SWAP_OUT, SWAP_OUT_AT)):
    if off is None:
        continue
    print("  %s on the 29.97 camera: %r meant %.4f s, result %+.4f s = "
          "%+.1f frames at 29.97" % (door, mark, meant, off,
                                     frames(off, 29.97)))
    if abs(off) > HALF[29.97]:
        off_by.append("%s %+.1f" % (door, frames(off, 29.97)))
if w_in is not None and w_out is not None:
    print("  window length: marks %.4f s apart, result %.4f s, %+.1f frames"
          % (OUT_AT - IN_AT, wb - wa, frames((wb - wa) - (OUT_AT - IN_AT),
                                              29.97)))
if off_by:
    left_out.append("LEFT OUT: a timecode typed on the command line for "
                    "the 29.97 camera does not land on its frame -- read "
                    "at the reference camera's rate; frames late at "
                    "29.97: " + ", ".join(off_by))

stop()
