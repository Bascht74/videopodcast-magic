# -*- coding: utf-8 -*-
"""A project file lying with the material is offered, not read behind a back.

Half a project used to arrive unasked: the output folder and the
production name were read out of any handover file beside the material,
possibly from an unrelated run.

The sections in the order they run: the offer stands in the program and
the guess is gone; the folder the material lies in and the one below it
are searched and nothing further; one file found is offered once and
opened only on a yes; the same folder is asked about once and a new one
again; several are shown with their dates and the line chosen is the
file that opens; and where nothing lies, nothing is said.

The question and the list are stand-ins, so no window opens, and what
they answer is all the test sees of Qt.
"""
import os, sys, time, shutil, tempfile
import the_program
HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = the_program.SCRIPT
vpm = the_program.load()

began = time.time()
done = 0
bad = []


def check(name, ok, extra=""):
    global done
    done += 1
    print("  %-58s %s %s" % (name, "ok" if ok else "FAIL", extra))
    if not ok:
        bad.append("%s [%s]" % (name, extra or "no numbers"))


def write(path, when=None):
    """Put a file there, optionally with a chosen age."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        f.write("{}")
    if when is not None:
        os.utime(path, (when, when))
    return path


def named(paths):
    """The bare names, so a failing line stays one line."""
    return [os.path.basename(p) for p in paths]


print("1. The offer stands in the program, and the guess is gone")
# Asked first and on their own: everything below runs through these two,
# and without them the run would end in a traceback naming the last
# thing that broke rather than the first.
check("the program looks for project files beside the material",
      hasattr(vpm, "projects_beside"),
      "projects_beside there: %s, wanted True"
      % hasattr(vpm, "projects_beside"))
check("the offer is there in its place", hasattr(vpm, "project_offer"),
      "project_offer there: %s, wanted True" % hasattr(vpm, "project_offer"))
check("the guessing is gone", not hasattr(vpm, "guess_result_folder"),
      "guess_result_folder there: %s, wanted False"
      % hasattr(vpm, "guess_result_folder"))
if not (hasattr(vpm, "projects_beside") and hasattr(vpm, "project_offer")):
    # The one way out, and it goes past the count like every other path.
    print("\n%d checks in %.2f s" % (done, time.time() - began))
    print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
    sys.exit(1 if bad else 0)

root = tempfile.mkdtemp(prefix="vpm-offer-")
NAME = vpm.PROJECT_PREFIX + "%s.json"

print("\n2. Where a project file is looked for")
# The program writes its project file into the output folder below the
# material, so both places have to be searched -- and nothing further.
# Two decoys lie beside it, older than either so they cannot disturb the
# order: the right ending without the prefix, and the prefix without the
# ending.
material = os.path.join(root, "Recording")
write(os.path.join(material, "Kamera1.mp4"))
here = write(os.path.join(material, NAME % "beside"), when=1000)
write(os.path.join(material, "notes.json"), when=500)
write(os.path.join(material, vpm.PROJECT_PREFIX + "beside.log"), when=500)
below = write(os.path.join(material, "Output", NAME % "below"), when=2000)
deep = write(os.path.join(material, "Output", "again", NAME % "deep"),
             when=3000)
found = vpm.projects_beside([os.path.join(material, "Kamera1.mp4")])
paths = [p for p, _ in found]
check("the one in the material folder is found", here in paths,
      "%d found, %s among them: %s"
      % (len(paths), os.path.basename(here), named(paths)))
check("the one in the output folder below is found", below in paths,
      "%d found, %s among them: %s"
      % (len(paths), os.path.basename(below), named(paths)))
check("two folders down is not looked at", deep not in paths,
      "%d found, %s not among them: %s"
      % (len(paths), os.path.basename(deep), named(paths)))
check("nothing else came along", len(paths) == 2,
      "%d found, wanted 2, beside 2 decoys: %s" % (len(paths), named(paths)))
check("the newest stands first", paths[:1] == [below],
      "first of %d is %s, wanted %s"
      % (len(paths), (named(paths) + ["nothing"])[0],
         os.path.basename(below)))
check("the date comes with it", bool(found) and found[0][1] == 2000,
      "%s came with the first of %d, wanted 2000"
      % (found[0][1] if found else "nothing", len(found)))

# Two recordings out of one folder name that folder's project once.
write(os.path.join(material, "Kamera2.mp4"))
twice = vpm.projects_beside([os.path.join(material, "Kamera1.mp4"),
                             os.path.join(material, "Kamera2.mp4")])
check("each project file is named once, not once per recording",
      len(twice) == 2,
      "%d named for 2 recordings, wanted 2: %s"
      % (len(twice), named([p for p, _ in twice])))

# A folder that is not there must not stop the search.
try:
    gone, threw = vpm.projects_beside([os.path.join(root, "no-such", "x.mp4")]), ""
except Exception as e:
    gone, threw = None, type(e).__name__
check("a folder that does not exist gives nothing, not a crash",
      gone == [],
      ("it threw %s, wanted 0 found" % threw) if threw
      else "%d found, wanted 0: %s" % (len(gone), named([p for p, _ in gone])))

bare = os.path.join(root, "Bare")
write(os.path.join(bare, "Kamera1.mp4"))
nothing = vpm.projects_beside([os.path.join(bare, "Kamera1.mp4")])
check("material with no project file gives nothing", nothing == [],
      "%d found, wanted 0: %s"
      % (len(nothing), named([p for p, _ in nothing])))

print("\n3. What the offer does with one file")


class Dialog(object):
    """Stands in for QInputDialog.getItem and keeps what it was shown.

    `takes` is which line it picks; None means the one the program
    offers as the current one. It never reaches past the end of the
    list: a stand-in that threw would end the run in a traceback
    instead of a judgement, and the judgement is the point.
    """

    def __init__(self, accept=True, takes=None):
        self.shown, self.accept, self.takes = [], accept, takes
        self.picked = ""

    def getItem(self, window, title, text, lines, index, editable):
        self.shown.append(list(lines))
        want = index if self.takes is None else self.takes
        self.picked = lines[want] if len(lines) > want else ""
        return self.picked, self.accept


class Widgets(object):
    def __init__(self, dialog):
        self.QInputDialog = dialog


def offer(paths, say_yes=True, state=None, dialog=None):
    """Run the offer with counted stand-ins, give back what happened."""
    asked, loaded = [], []
    dialog = dialog or Dialog()
    vpm.project_offer(Widgets(dialog), None, state if state is not None else {},
                      paths, lambda *a: (asked.append(a), say_yes)[1],
                      loaded.append)
    return asked, loaded, dialog


one = os.path.join(root, "Single")
write(os.path.join(one, "Kamera1.mp4"))
only = write(os.path.join(one, NAME % "only"), when=1000)

asked, loaded, dialog = offer([os.path.join(one, "Kamera1.mp4")])
check("one file found: asked once", len(asked) == 1,
      "asked %d times, wanted 1" % len(asked))
check("and opened when the answer is yes", loaded == [only],
      "%d opened, wanted 1 (%s): %s"
      % (len(loaded), os.path.basename(only), named(loaded)))
check("no list was shown for a single file", dialog.shown == [],
      "%d lists shown, wanted 0" % len(dialog.shown))
question = " ".join(str(x) for x in (asked[0] if asked else ()))
check("the question names the file", os.path.basename(only) in question,
      "looked for %s in %d characters of question"
      % (os.path.basename(only), len(question)))
# Asked through T(), or the check would read English on an English
# machine and fail on a German one.
whole = vpm.T('Everything comes back from it: names, separation, '
              'assignment, types, the time window. The list of files is '
              'replaced by the one the project holds.')
check("the question says the whole project comes back", whole in question,
      "looked for its %d characters in %d of question"
      % (len(whole), len(question)))

asked, loaded, _ = offer([os.path.join(one, "Kamera1.mp4")], say_yes=False)
check("no means nothing is opened", loaded == [],
      "%d opened, wanted 0: %s" % (len(loaded), named(loaded)))
check("a no is not followed by a second question", len(asked) == 1,
      "asked %d times, wanted 1" % len(asked))

print("\n4. Asked once, and once per folder")
# One window, one state: adding more from the same folder must not ask
# again.
state = {}
asked, loaded, _ = offer([os.path.join(one, "Kamera1.mp4")], state=state)
check("the first material out of a folder is asked about", len(asked) == 1,
      "asked %d times, wanted 1" % len(asked))
write(os.path.join(one, "Kamera2.mp4"))
asked, loaded, _ = offer([os.path.join(one, "Kamera1.mp4"),
                          os.path.join(one, "Kamera2.mp4")], state=state)
check("more material from the same folder does not ask again",
      asked == [] and loaded == [],
      "asked %d times and opened %d, wanted 0 and 0"
      % (len(asked), len(loaded)))

# Another folder with a project of its own is a new finding, so it is
# offered -- otherwise a second recording could never be opened.
second = os.path.join(root, "Second")
write(os.path.join(second, "Kamera1.mp4"))
other = write(os.path.join(second, NAME % "second"), when=1000)
asked, loaded, _ = offer([os.path.join(one, "Kamera1.mp4"),
                          os.path.join(second, "Kamera1.mp4")], state=state)
check("a project in a folder not asked about yet is offered",
      len(asked) == 1 and loaded == [other],
      "asked %d times and opened %s, wanted 1 and %s"
      % (len(asked), named(loaded), os.path.basename(other)))

# Material arrives through the same door after a project is open --
# taking a block out of a recording and putting it back goes that way.
# Offering there would undo by hand what somebody had just done by hand.
after = {"project_from": os.path.join(one, "project.json")}
asked, loaded, dialog = offer([os.path.join(one, "Kamera1.mp4")],
                              state=after)
check("with a project open nothing is offered any more",
      asked == [] and loaded == [] and dialog.shown == [],
      "asked %d, opened %d, lists %d, wanted 0, 0 and 0"
      % (len(asked), len(loaded), len(dialog.shown)))
check("with a project open nothing is noted as offered either",
      "projects_offered" not in after,
      "%d keys in the state, wanted the 1 it came with: %s"
      % (len(after), sorted(after)))

print("\n5. Several files are shown, not guessed between")
many = os.path.join(root, "Many")
write(os.path.join(many, "Kamera1.mp4"))
# Whole years apart, so a line showing the other file's date is visible
# as such; a few seconds apart they print the same day and minute.
old = write(os.path.join(many, NAME % "older"), when=1000)
new = write(os.path.join(many, NAME % "newer"), when=1000000000)
old_day = time.strftime("%Y-%m-%d", time.localtime(1000))
new_day = time.strftime("%Y-%m-%d", time.localtime(1000000000))

asked, loaded, dialog = offer([os.path.join(many, "Kamera1.mp4")])
shown = dialog.shown[0] if dialog.shown else []
check("several files: no yes-or-no question", asked == [],
      "asked %d times, wanted 0" % len(asked))
check("a list was shown instead", len(dialog.shown) == 1,
      "%d lists shown, wanted 1" % len(dialog.shown))
check("both files stand in it", len(shown) == 2,
      "%d lines, wanted 2: %s" % (len(shown), shown))
check("the newest stands at the top of the list",
      bool(shown) and os.path.basename(new) in shown[0],
      "line 1 of %d is %s, wanted %s in it"
      % (len(shown), shown[0] if shown else "nothing",
         os.path.basename(new)))
stamps = {os.path.basename(old): old_day, os.path.basename(new): new_day}
askew = [line for line in shown
         if not any(name in line and day in line
                    for name, day in stamps.items())]
check("each file's own date stands beside it", bool(shown) and not askew,
      "%d of %d lines carry their own date, wanted %s and %s: %s"
      % (len(shown) - len(askew), len(shown), old_day, new_day, askew))
check("the chosen one is opened", loaded == [new],
      "%d opened, wanted 1 (%s): %s"
      % (len(loaded), os.path.basename(new), named(loaded)))

# The line and the file behind it have to be the same one: a list that
# lost its order must not open a file nobody pointed at. So the second
# entry is taken, and the file that opens is held against that line and
# not against a place in the list.
picked, took = [], Dialog(takes=1)
vpm.project_offer(Widgets(took), None, {},
                  [os.path.join(many, "Kamera1.mp4")], lambda *a: True,
                  picked.append)
check("the file opened is the one named in the line chosen",
      len(picked) == 1 and os.path.basename(picked[0]) in took.picked,
      "%d opened (%s) out of the line %s"
      % (len(picked), named(picked), took.picked or "nothing"))

# Qt gives back the entry standing on when it is cancelled, not an empty
# string, so the stand-in does too: a cancel that answered "" would pass
# a program that never looked at the second half of the answer.
cancelled, cancel = [], Dialog(accept=False)
vpm.project_offer(Widgets(cancel), None, {},
                  [os.path.join(many, "Kamera1.mp4")], lambda *a: True,
                  cancelled.append)
check("cancelling the list opens nothing", cancelled == [],
      "%d opened, wanted 0, after a cancel over %s"
      % (len(cancelled), cancel.picked or "nothing"))

print("\n6. Nothing found, nothing said")
quiet = os.path.join(root, "Quiet")
write(os.path.join(quiet, "Kamera1.mp4"))
asked, loaded, dialog = offer([os.path.join(quiet, "Kamera1.mp4")])
check("no project file: no question", asked == [],
      "asked %d times, wanted 0" % len(asked))
check("no project file: no list", dialog.shown == [],
      "%d lists shown, wanted 0" % len(dialog.shown))
check("no project file: nothing opened", loaded == [],
      "%d opened, wanted 0: %s" % (len(loaded), named(loaded)))

shutil.rmtree(root, ignore_errors=True)
print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
