# -*- coding: utf-8 -*-
"""--resolve-audio-tracks shows each clip and track, and changes nothing.

print_audio_track_mapping against a stand-in Resolve with one project
open: clips in the root bin and in a bin inside it, a timeline among
them, and a timeline with an empty audio track and one with a file on
it. In turn: the media pool -- the clip in the inner bin is shown, the
timeline is not taken for a clip, the documented mapping is read as one
track of four channels, a clip with no mapping says so, a clip whose
mapping raises is named while the look goes on to the next clip in its
bin, and a mapping no count of tracks can be read from says so and the
look goes on; the timelines -- every audio track listed, and the file
on it named; then that nothing in Resolve was set, made or deleted; and
last, that with no project open, or no project manager, it stops and
says why.
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
import contextlib
import io
import json
import time
import resolve_stand_in as stand

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


# The door nailed shut before anything calls at it: the look reaches the
# stand-in holding whichever project manager the section put here.
CURRENT = {}
vpm.connect_to_resolve = lambda: stand.Resolve(
    pm=CURRENT["pm"], refuse=CURRENT["refuse"])


def look(pm, refuse=()):
    """(what it printed as lines, what it returned, what it raised).

    *refuse* names the calls of Resolve itself that answer no.
    """
    CURRENT["pm"], CURRENT["refuse"] = pm, refuse
    said = io.StringIO()
    got = raised = None
    with contextlib.redirect_stdout(said):
        try:
            got = vpm.print_audio_track_mapping()
        except Exception as e:  # judged below, never handed on
            raised = e
    return said.getvalue().splitlines(), got, raised


def block(lines, name):
    """The lines under a clip's name, up to the blank line after them."""
    head = "    " + name
    if head not in lines:
        return []
    rest = lines[lines.index(head) + 1:]
    return rest[:rest.index("")] if "" in rest else rest


MONO = {"channel_idx": [1], "mute": False, "type": "mono"}
DOCUMENTED = json.dumps({"embedded_audio_channels": 4, "linked_audio": {},
                         "track_mapping": {"1": MONO}})
GUEST = stand.Clip("/tmp/GuestCam_C003.mov", mapping=DOCUMENTED,
                   properties={"Type": "Video + Audio"})
PRESENTER = stand.Clip("/tmp/Presenter_TR01.WAV", mapping=None)
BROKEN = stand.Clip("/tmp/CoPresenter_TR02.WAV", throw=["GetAudioMapping"])
# A mapping with no part that names tracks: the channels are there, how
# many tracks they make is not. The clip after it shows the look goes on.
UNCOUNTED = stand.Clip("/tmp/Guest_TR01.WAV", mapping=json.dumps(
    {"embedded_audio_channels": 2, "linked_audio": {}}))
LATER = stand.Clip("/tmp/Presenter_TR03.WAV", mapping=DOCUMENTED)
CUT = stand.Clip("/tmp/Episode cut", properties={"Type": "Timeline"})
WIDE = stand.Clip("/tmp/WideCam_C001.mov", mapping=DOCUMENTED)

pm = stand.ProjectManager(names=["Episode"])
p = pm.current = pm.projects["Episode"]
p.pool.root.clips += [GUEST, PRESENTER, BROKEN, UNCOUNTED, LATER, CUT]
inner = stand.Folder()
inner.clips.append(WIDE)
p.pool.root.folders.append(inner)
tl = stand.Timeline("Episode cut")
p.timelines.append(tl)
tl.lay("video", 1, stand.Item(GUEST.GetName()))
tl.lay("audio", 2, stand.Item(PRESENTER.GetName()))
tl.names["audio"][1] = "Presenter"
asked = [pm, p, p.pool, tl, GUEST, PRESENTER, BROKEN, UNCOUNTED, LATER,
         CUT, WIDE] \
    + tl.tracks["video"][0] + tl.tracks["audio"][1]

lines, got, raised = look(pm)
timelines = lines[lines.index(vpm.T('\n  TIMELINES').strip("\n")) + 1:] \
    if vpm.T('\n  TIMELINES').strip("\n") in lines else []

print("1. The media pool")
check("a clip in a bin inside the root bin is shown",
      "    " + WIDE.GetName() in lines,
      "%r looked for among %d lines printed, raised %r"
      % (WIDE.GetName(), len(lines), raised))
check("a timeline in the media pool is not shown as a clip",
      "    " + CUT.GetName() not in lines,
      "%r looked for as a clip, with %r under it"
      % (CUT.GetName(), block(lines, CUT.GetName())))
WANT = vpm.TN(1, '      --> interpreted as %s audio track%s',
              '      --> interpreted as %s audio tracks%s') \
    % (1, vpm.TN(4, ' of %s embedded channel', ' of %s embedded channels')
       % vpm.number_text(4, 0))
check("the documented mapping is read as one track of four channels",
      WANT in block(lines, GUEST.GetName()),
      "%r looked for in %r" % (WANT, block(lines, GUEST.GetName())))
WANT = vpm.T('      GetAudioMapping   empty (%r)') % None
check("a clip with no mapping says it has none",
      WANT in block(lines, PRESENTER.GetName()),
      "%r looked for in %r" % (WANT, block(lines, PRESENTER.GetName())))
WANT = vpm.T('      GetAudioMapping   fails: %s') \
    % "stand-in GetAudioMapping refused by raising"
check("a clip whose mapping raises is named, and the look goes on",
      WANT in block(lines, BROKEN.GetName()) and raised is None and got == 0,
      "%r %s, returned %r, raised %r"
      % (WANT, "said" if WANT in block(lines, BROKEN.GetName())
         else "not said", got, raised))
check("and the clip after it in the same bin is still shown",
      "    " + UNCOUNTED.GetName() in lines,
      "%r looked for among %d lines printed, after %r"
      % (UNCOUNTED.GetName(), len(lines), BROKEN.GetName()))
WANT = vpm.T('      --> no count of audio tracks can be read from this '
             'mapping')
check("a mapping no count of tracks can be read from says so",
      WANT in block(lines, UNCOUNTED.GetName()),
      "%r looked for in %r" % (WANT, block(lines, UNCOUNTED.GetName())))
check("and the look goes on to the next clip in that bin",
      "    " + LATER.GetName() in lines,
      "%r looked for among %d lines printed, after %r, raised %r"
      % (LATER.GetName(), len(lines), UNCOUNTED.GetName(), raised))

print("\n2. The timelines")
tracks = [s for s in timelines if s.startswith("      A")]
check("every audio track of a timeline is listed", len(tracks) == 2,
      "%d audio track lines against 2: %r" % (len(tracks), tracks))
second = [s for s in tracks if s.startswith("      A2 ")]
check("an audio track names its own name and the file on it",
      len(second) == 1 and "Presenter " in second[0]
      and second[0].rstrip().endswith(PRESENTER.GetName()),
      "A2 line %r against track 'Presenter' and %r"
      % (second, PRESENTER.GetName()))

print("\n3. Nothing changes")
WRITES = ("Set", "Add", "Create", "Delete", "Import", "Append", "Load",
          "Clear", "Assign", "Insert")
writes = [c[0] for o in asked for c in o.calls if c[0].startswith(WRITES)]
check("the look sets, makes and deletes nothing in Resolve", writes == [],
      "%d calls that change something: %r" % (len(writes), writes))

print("\n4. No project open")
lines, got, raised = look(stand.ProjectManager())
WANT = vpm.T('No project open.')
check("with no project open it stops and says so",
      isinstance(raised, RuntimeError) and str(raised) == WANT,
      "raised %r against RuntimeError(%r), returned %r"
      % (raised, WANT, got))
lines, got, raised = look(stand.ProjectManager(),
                          refuse=["GetProjectManager"])
check("with no project manager it stops the same way",
      isinstance(raised, RuntimeError) and str(raised) == WANT,
      "raised %r against RuntimeError(%r), returned %r"
      % (raised, WANT, got))

print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
