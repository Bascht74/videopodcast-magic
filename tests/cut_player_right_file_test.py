# -*- coding: utf-8 -*-
"""#62: The player takes the file that holds the In point and the Out point.

The rules sit inside gui() and cannot be called from outside, so the
three of them are lifted by name out of gui()'s own body and run here
over six made-up files on one time axis: what is judged is the
program's code, not a copy kept beside it. The sections: the rules come
out and answer, the order they put the files in, the kinds that never
come into question, the file chosen last, what covers() says about the
axis, a missing timecode and the ends of a file, the values it can and
cannot answer, the order over two cards, and nothing left to play at
all. What the method
costs, in full: the three have to keep their names and stay directly
inside gui() -- their order, their parameters and their layout are
free; a rule that starts reading a further name out of gui() shows up
as no answer at all; and nothing here says the window ever reaches
these rules.
"""
import os
import the_program
HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = the_program.SCRIPT
import sys, time, inspect, ast
os.environ["QT_QPA_PLATFORM"] = "offscreen"
os.environ.setdefault("VPM_SILENT", "1")   # never beep at a person
# No window is built here, so no application either.
vpm = the_program.load()

began = time.time()
done = 0
error = []


def check(name, ok, extra=""):
    global done
    done += 1
    print("  %-58s %s %s" % (name, "ok" if ok else "FAIL", extra))
    if not ok:
        error.append("%s [%s]" % (name, extra or "no numbers"))

# Six files, and each one is there so that exactly one rule decides.
#
#   the guest    16:40 - 18:10   the longest, and the only one carrying
#                                a speaker, so "no speaker" is the only
#                                rule that can ever put it behind
#   the wide     17:00 - 18:00   inside the guest, so a boundary can lie
#                                in one of them and not in the other --
#                                in either direction
#   the short    17:50 - 17:51   short enough to lose on length, long
#                                enough to hold one boundary and not two
#   copresenter  no span at all  the file whose length was never read
#   the jingle   no timecode     an intro, and undecidable on a clock
#   guest.wav    sound           never a picture
#
# The wide shot used to be the longest as well as the only free one, so
# it won every field of the sort key at once and no judgement could say
# which rule had decided, nor notice when one of them was gone.
SPANS = {
    "/x/Guest.mov":   {"duration": 5400.0, "fps": 30.0,
                       "tc0": 16 * 3600.0 + 2400.0, "axis": 0.0},
    "/x/WideCam.mov": {"duration": 3600.0, "fps": 30.0,
                       "tc0": 17 * 3600.0, "axis": 1200.0},
    "/x/Short.mov":   {"duration": 60.0, "fps": 30.0,
                       "tc0": 17 * 3600.0 + 3000.0, "axis": 4200.0},
    "/x/Jingle.mp4":  {"duration": 10.0, "fps": 30.0,
                       "tc0": None, "axis": None},
}


# What the window holds around those rules: only what they reach for.
class Value(object):
    def __init__(self, v=""): self.v = v
    def get(self): return self.v
    def set(self, v): self.v = v


# Deliberately not in alphabetical order, so that the sorting the
# program does is visible in the answer rather than free.
files = [("/x/WideCam.mov", "video"),
         ("/x/Guest.wav", "audio"),
         ("/x/Short.mov", "video"),
         ("/x/Jingle.mp4", "video"),
         ("/x/CoPresenter.mov", "video"),
         ("/x/Guest.mov", "video")]
IN_ORDER = ["/x/CoPresenter.mov", "/x/Guest.mov",
            "/x/Short.mov", "/x/WideCam.mov"]
clip_kind_values = {"/x/Jingle.mp4": Value(vpm.TYPE_INTRO),
                    "/x/WideCam.mov": Value(vpm.TYPE_WIDE)}
assign_lines = [(["/x/Guest.wav"], Value("Tr1"), Value("Guest.mov"))]
remembered = {}
start_var, end_var = Value(""), Value("")


def picture_span(file_path):
    """Where the fixture stops and the program starts: the spans above."""
    return SPANS.get(file_path)


print("0. The player's own rules are cut out of the script and run here")
WANTED = ("covers", "player_candidates", "player_suggestion")
# Each rule is taken on its own, by name, out of gui()'s own body, and
# only as far as gui() says it reaches. So their order among each other,
# a parameter added to one of them and the way their lines are laid out
# are all free, and a statement of gui()'s standing between two of them
# is not dragged along and cannot raise in here unnoticed.
source = inspect.getsource(vpm.gui)
cut = {}
for node in ast.parse(source).body[0].body:
    if isinstance(node, ast.FunctionDef) and node.name in WANTED:
        cut[node.name] = ast.get_source_segment(source, node) or ""
block = "\n".join(cut[n] for n in WANTED if cut.get(n))
rules = {"os": os, "picture_span": picture_span, "files": files,
         "clip_kind_values": clip_kind_values, "assign_lines": assign_lines,
         "start_var": start_var, "end_var": end_var, "remembered": remembered,
         "parse_time_point": vpm.parse_time_point,
         "CAMERA_TYPES": vpm.CAMERA_TYPES}
trouble = ""
if block:
    try:
        exec(compile(block, "<gui>", "exec"), rules)
    except Exception as why:                 # reported, and it counts below
        trouble = "%s: %s" % (type(why).__name__, why)
missing = [n for n in WANTED if n not in cut]
standing = sum(1 for n in WANTED if callable(rules.get(n)))
# Anything that went wrong up here has to reach the verdict: a value
# that is only printed lets a rule fall over in silence.
ran = standing == len(WANTED) and not trouble
check("the player's own rules run here, cut out of the script",
        ran,
        "%d of %d rules standing out of %d characters cut from gui()%s%s"
        % (standing, len(WANTED), len(block),
           "; gui() holds no " + ", ".join(missing) if missing else "",
           ", " + trouble if trouble else ""))

answered = ""
if ran:
    try:
        first_answer = rules["player_suggestion"]()
    except Exception as why:                 # reported, never swallowed
        first_answer, answered = None, "%s: %s" % (type(why).__name__, why)
    check("the rules answer with one of the files, not with a complaint",
            first_answer in IN_ORDER,
            "answered %r, wanted one of %d files%s"
            % (first_answer, len(IN_ORDER),
               "; " + answered if answered else ""))

if ran and not answered:
    covers = rules["covers"]
    player_candidates = rules["player_candidates"]
    player_suggestion = rules["player_suggestion"]

    print("\n1. Nothing to go by: a speaker puts a file behind one without,"
          "\n   and among those the length decides")
    check("the camera with no speaker beats a longer one that has one",
            player_suggestion() == "/x/WideCam.mov",
            "chose %s: guest %.0f s with a speaker on it, wide %.0f s with"
            " none, copresenter with no length read"
            % (player_suggestion(), SPANS["/x/Guest.mov"]["duration"],
               SPANS["/x/WideCam.mov"]["duration"]))
    files.remove(("/x/Guest.mov", "video"))
    check("among cameras with no speaker the longest one wins",
            player_suggestion() == "/x/WideCam.mov",
            "with the guest's file away, chose %s of %s: wide %.0f s,"
            " short %.0f s"
            % (player_suggestion(), player_candidates(),
               SPANS["/x/WideCam.mov"]["duration"],
               SPANS["/x/Short.mov"]["duration"]))
    files.append(("/x/Guest.mov", "video"))

    print("\n2. The Out point decides: In point in both files, Out point"
          "\n   only in the guest's")
    start_var.set("17:30:00:00"); end_var.set("18:05:00:00")
    check("a file holding both boundaries beats one holding the In point only",
            player_suggestion() == "/x/Guest.mov",
            "chose %s: guest holds %d of the two boundaries, wide %d"
            % (player_suggestion(),
               sum(1 for t in ("17:30:00:00", "18:05:00:00")
                   if covers("/x/Guest.mov", t) is True),
               sum(1 for t in ("17:30:00:00", "18:05:00:00")
                   if covers("/x/WideCam.mov", t) is True)))

    print("\n3. The In point decides: Out point in both files, In point"
          "\n   only in the guest's")
    start_var.set("16:50:00:00"); end_var.set("17:30:00:00")
    check("a file holding both boundaries beats one holding the Out point"
          " only",
            player_suggestion() == "/x/Guest.mov",
            "chose %s: guest holds %d of the two boundaries, wide %d"
            % (player_suggestion(),
               sum(1 for t in ("16:50:00:00", "17:30:00:00")
                   if covers("/x/Guest.mov", t) is True),
               sum(1 for t in ("16:50:00:00", "17:30:00:00")
                   if covers("/x/WideCam.mov", t) is True)))

    print("\n4. A file that cannot say does not thereby hold the boundaries")
    SPANS["/x/WideCam.mov"]["tc0"] = None     # its timecode was never read
    start_var.set("16:45:00:00"); end_var.set("16:55:00:00")
    check("a file with no timecode does not count as holding a clock time",
            player_suggestion() == "/x/Guest.mov",
            "chose %s: wide answers %s for 16:45:00:00, guest holds %d of the"
            " two boundaries"
            % (player_suggestion(), covers("/x/WideCam.mov", "16:45:00:00"),
               sum(1 for t in ("16:45:00:00", "16:55:00:00")
                   if covers("/x/Guest.mov", t) is True)))
    SPANS["/x/WideCam.mov"]["tc0"] = 17 * 3600.0

    print("\n5. What comes into question at all")
    start_var.set(""); end_var.set("")
    standing_files = player_candidates()
    check("an intro is not among the candidates",
            "/x/Jingle.mp4" not in standing_files,
            "%d candidates: %s" % (len(standing_files), standing_files))
    check("a sound file is not among the candidates",
            "/x/Guest.wav" not in standing_files,
            "%d candidates: %s" % (len(standing_files), standing_files))
    check("a camera marked as the wide shot is among the candidates",
            "/x/WideCam.mov" in standing_files,
            "%d candidates: %s" % (len(standing_files), standing_files))
    check("the candidates come back sorted by file name",
            standing_files == IN_ORDER,
            "got %s, wanted %s" % (standing_files, IN_ORDER))

    print("\n6. 'ignore this video' never comes into question")
    clip_kind_values["/x/WideCam.mov"] = Value(vpm.TYPE_IGNORED)
    left_over = player_candidates()
    check("a video set to be ignored is not among the candidates",
            "/x/WideCam.mov" not in left_over,
            "%d candidates: %s" % (len(left_over), left_over))
    check("a video set to be ignored is not suggested either",
            player_suggestion() == "/x/Short.mov",
            "chose %s while the wide shot is set to be ignored; the"
            " candidates are %s" % (player_suggestion(), left_over))
    clip_kind_values["/x/WideCam.mov"] = Value(vpm.TYPE_WIDE)

    print("\n7. The file chosen last keeps its place on a tie")
    # All three hold both boundaries, so the tie is decided by nothing
    # but the memory: the short file is the shortest of them, and the
    # wide shot is free of a speaker.
    start_var.set("17:50:10:00"); end_var.set("17:50:50:00")
    remembered["player_file"] = "/x/Short.mov"
    tied = [f for f in player_candidates()
            if covers(f, "17:50:10:00") is True
            and covers(f, "17:50:50:00") is True]
    check("the file chosen last wins a tie against a longer one",
            player_suggestion() == "/x/Short.mov",
            "chose %s of %d files holding both boundaries: %s"
            % (player_suggestion(), len(tied), tied))

    print("\n8. ... but it gives way to a file that holds more")
    start_var.set("17:50:30:00"); end_var.set("17:55:00:00")
    check("the file chosen last gives way when another holds more boundaries",
            player_suggestion() == "/x/WideCam.mov",
            "chose %s: short holds %d of the two boundaries, wide %d"
            % (player_suggestion(),
               sum(1 for t in ("17:50:30:00", "17:55:00:00")
                   if covers("/x/Short.mov", t) is True),
               sum(1 for t in ("17:50:30:00", "17:55:00:00")
                   if covers("/x/WideCam.mov", t) is True)))
    remembered.pop("player_file")

    print("\n9. A value counted from the start of the material needs the axis")
    # The wide shot begins 1200 s into the material, so the axis is the
    # whole difference between +0:15:00 and +0:50:00 landing outside and
    # inside it.
    late = covers("/x/WideCam.mov", "+0:50:00")
    check("a value 3000 s along the axis lies inside the wide shot",
            late is True,
            "wide at +0:50:00: %s, wanted True -- 3000 s along an axis the"
            " wide shot joins at %.0f s, and it runs %.0f s"
            % (late, SPANS["/x/WideCam.mov"]["axis"],
               SPANS["/x/WideCam.mov"]["duration"]))
    early = covers("/x/WideCam.mov", "+0:15:00")
    check("a value 900 s along the axis lies before the wide shot",
            early is False,
            "wide at +0:15:00: %s, wanted False -- 900 s along an axis the"
            " wide shot joins at %.0f s"
            % (early, SPANS["/x/WideCam.mov"]["axis"]))
    SPANS["/x/WideCam.mov"]["axis"] = None
    no_axis = covers("/x/WideCam.mov", "+0:50:00")
    check("with no axis measured such a value gets no answer at all",
            no_axis is None,
            "wide without an axis at +0:50:00: %s, wanted None" % (no_axis,))
    SPANS["/x/WideCam.mov"]["axis"] = 1200.0

    print("\n10. No timecode, no answer for a clock time")
    no_clock = covers("/x/Jingle.mp4", "17:20:00:00")
    check("a file with no timecode gets no answer for a clock time",
            no_clock is None,
            "jingle at 17:20:00:00: %s, wanted None -- it has no timecode"
            " and runs %.0f s"
            % (no_clock, SPANS["/x/Jingle.mp4"]["duration"]))

    print("\n11. Where a file begins and ends")
    last_frame = covers("/x/Short.mov", "17:51:00:00")
    check("a boundary on the file's last frame still lies inside it",
            last_frame is True,
            "short at 17:51:00:00: %s, wanted True -- 60.0 s into a file"
            " of %.1f s" % (last_frame, SPANS["/x/Short.mov"]["duration"]))
    past_end = covers("/x/Short.mov", "17:51:30:00")
    check("a boundary past the end of the file lies outside it",
            past_end is False,
            "short at 17:51:30:00: %s, wanted False -- 90.0 s into a file"
            " of %.1f s" % (past_end, SPANS["/x/Short.mov"]["duration"]))
    from_end = covers("/x/Short.mov", "-0:00:10")
    check("a value counted back from the end lands inside the file",
            from_end is True,
            "short at -0:00:10: %s, wanted True -- 10 s back from the end"
            " of %.1f s" % (from_end, SPANS["/x/Short.mov"]["duration"]))
    # And how far outside is far enough. The two above hold the sign of
    # the comparison, not the slack around it: widening either end
    # tenfold leaves both green. Twelve frames is well outside any
    # rounding a timecode can carry.
    just_past = covers("/x/Short.mov", "17:51:00:12")
    check("four tenths of a second past the end is outside",
            just_past is False,
            "short at 17:51:00:12: %s, wanted False -- 60.4 s into a file"
            " of %.1f s" % (just_past, SPANS["/x/Short.mov"]["duration"]))
    just_before = covers("/x/Short.mov", "17:49:59:18")
    check("and four tenths before the start is outside as well",
            just_before is False,
            "short at 17:49:59:18: %s, wanted False -- 0.4 s before a file"
            " that begins at 17:50:00:00" % (just_before,))

    print("\n12. The values a file cannot answer, and the ones it can")
    # Everything above asks a file that has both a timecode and a
    # measured axis, and both of those read zero in an ordinary project:
    # the reference camera joins the material at 0.0 s, and a camera
    # with no time-of-day clock reads 00:00:00:00. A guard written
    # "if not ..." instead of "is None" turns both of those into "I
    # cannot say", and every judgement above stays green.
    at_zero_axis = covers("/x/Guest.mov", "+0:10:00")
    check("the file the axis is counted from can still answer",
            at_zero_axis is True,
            "guest at +0:10:00: %s, wanted True -- 600 s along an axis it"
            " joins at %.0f s"
            % (at_zero_axis, SPANS["/x/Guest.mov"]["axis"]))
    SPANS["/x/Jingle.mp4"]["tc0"] = 0.0       # a camera with no clock
    at_zero_clock = covers("/x/Jingle.mp4", "00:00:05:00")
    check("and a file whose clock reads zero can answer too",
            at_zero_clock is True,
            "jingle at 00:00:05:00 with a timecode of 0.0: %s, wanted True"
            " -- 5 s into a file of %.0f s"
            % (at_zero_clock, SPANS["/x/Jingle.mp4"]["duration"]))
    SPANS["/x/Jingle.mp4"]["tc0"] = None
    # The very start of the material is what the program's own writing of
    # a relative time produces, so it is a value it hands itself. It has
    # to be read forwards from the beginning, not backwards from the end.
    axis_start = covers("/x/WideCam.mov", "+0:00:00")
    check("the start of the axis lies before a camera that joins later",
            axis_start is False,
            "wide at +0:00:00: %s, wanted False -- it joins the axis at"
            " %.0f s" % (axis_start, SPANS["/x/WideCam.mov"]["axis"]))
    # A file whose length was never read arrives as a duration of 0.0,
    # not as no span at all: file_span writes float(... or 0.0).
    SPANS["/x/CoPresenter.mov"] = {"duration": 0.0, "fps": 30.0,
                                   "tc0": 17 * 3600.0, "axis": 0.0}
    no_length = covers("/x/CoPresenter.mov", "17:00:00:00")
    check("a file whose length was never read answers nothing",
            no_length is None,
            "copresenter with a duration of 0.0 at 17:00:00:00: %s,"
            " wanted None" % (no_length,))
    del SPANS["/x/CoPresenter.mov"]
    # In point and Out point are free text somebody types, so a slip of
    # the finger travels from here through the suggestion into the
    # window.
    mistyped = []
    for text in ("abc", "17:xx:00:00", ".."):
        try:
            mistyped.append(covers("/x/Guest.mov", text))
        except Exception as why:
            mistyped.append("%s: %s" % (type(why).__name__, why))
    check("a mistyped boundary gets no answer instead of falling over",
            mistyped == [None, None, None],
            "%s for 'abc', '17:xx:00:00' and '..', wanted no answer to any"
            % (mistyped,))

    print("\n13. The order the candidates come back in")
    # The six above all begin with a capital and all lie in one folder,
    # so neither half of the sort key is held by them. Two cards, and a
    # camera that writes its name in lower case: sorting the whole path
    # and sorting without folding the case both turn this pair round.
    files.append(("/x/card_b/cam_0001.mov", "video"))
    files.append(("/x/card_a/Guest_C001.mov", "video"))
    ON_TWO_CARDS = ["/x/card_b/cam_0001.mov", "/x/CoPresenter.mov",
                    "/x/Guest.mov", "/x/card_a/Guest_C001.mov",
                    "/x/Short.mov", "/x/WideCam.mov"]
    spread = player_candidates()
    check("the sort ignores the folder and the case of the name",
            spread == ON_TWO_CARDS,
            "got %s, wanted %s" % (spread, ON_TWO_CARDS))
    files.pop(); files.pop()

    print("\n14. Nothing left to play")
    # A person can set every video to "ignore this video" by hand, and
    # then there is nothing to choose from at all.
    was = dict(clip_kind_values)
    for file_path, kind in files:
        if kind == "video":
            clip_kind_values[file_path] = Value(vpm.TYPE_IGNORED)
    try:
        empty_answer = player_suggestion()
    except Exception as why:                 # reported, never swallowed
        empty_answer = "%s: %s" % (type(why).__name__, why)
    clip_kind_values.clear(); clip_kind_values.update(was)
    check("with every video ignored the player is offered nothing",
            empty_answer is None,
            "%r, wanted None -- %d candidates left"
            % (empty_answer, len(player_candidates())))
else:
    print("\nThe judgements below need those rules, and they did not run.")

print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(error) if error else "ALL OK")
sys.exit(1 if error else 0)
