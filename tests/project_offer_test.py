# -*- coding: utf-8 -*-
"""A project file lying with the material is offered, not read behind a back.

Half a project used to arrive unasked: the output folder and the
production name were read out of any handover file beside the material,
possibly from an unrelated run. Now the folders are looked at when
material comes in, one file found is offered once, several are shown
with their dates, and what is opened is opened whole.
"""
import os, sys, time, shutil, tempfile
HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = os.environ.get("VPM_SCRIPT") or os.path.join(
    os.path.dirname(HERE), "videopodcast-magic.py")
import importlib.util
spec = importlib.util.spec_from_file_location("vpm", SCRIPT)
vpm = importlib.util.module_from_spec(spec); sys.modules["vpm"] = vpm
spec.loader.exec_module(vpm)

bad = []


def check(what, ok, detail=""):
    print("  %-58s %s%s" % (what, "ok" if ok else "FAIL",
                            "" if ok else "   " + detail))
    if not ok:
        bad.append(what)


def write(path, when=None):
    """Put a file there, optionally with a chosen age."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        f.write("{}")
    if when is not None:
        os.utime(path, (when, when))
    return path


root = tempfile.mkdtemp(prefix="vpm-offer-")
NAME = vpm.PROJECT_PREFIX + "%s.json"

print("1. Where a project file is looked for")
# The program writes its project file into the output folder below the
# material, so both places have to be searched.
material = os.path.join(root, "Recording")
write(os.path.join(material, "Kamera1.mp4"))
here = write(os.path.join(material, NAME % "beside"), when=1000)
below = write(os.path.join(material, "Output", NAME % "below"), when=2000)
deep = write(os.path.join(material, "Output", "again", NAME % "deep"),
             when=3000)
found = vpm.projects_beside([os.path.join(material, "Kamera1.mp4")])
paths = [p for p, _ in found]
check("the one in the material folder is found", here in paths)
check("the one in the output folder below is found", below in paths)
check("two folders down is not looked at", deep not in paths,
      "found %s" % paths)
check("nothing else came along", len(paths) == 2, str(paths))
check("the newest stands first", paths[0] == below,
      "%s came first" % os.path.basename(paths[0]))
check("the date comes with it", found[0][1] == 2000, str(found[0][1]))

# Two files of the same production name one folder, not two.
write(os.path.join(material, "Kamera2.mp4"))
twice = vpm.projects_beside([os.path.join(material, "Kamera1.mp4"),
                             os.path.join(material, "Kamera2.mp4")])
check("each project file is named once, not once per recording",
      len(twice) == 2, str([p for p, _ in twice]))

# A folder that is not there must not stop the search.
gone = vpm.projects_beside([os.path.join(root, "no-such", "x.mp4")])
check("a folder that does not exist gives nothing, not a crash", gone == [])
bare = os.path.join(root, "Bare")
write(os.path.join(bare, "Kamera1.mp4"))
check("material with no project file gives nothing",
      vpm.projects_beside([os.path.join(bare, "Kamera1.mp4")]) == [])

print("\n2. What the offer does with one file")


class Dialog(object):
    """Stands in for QInputDialog.getItem and counts what it was shown."""

    def __init__(self, answer=None, accept=True):
        self.shown, self.answer, self.accept = [], answer, accept

    def getItem(self, window, title, text, lines, index, editable):
        self.shown.append(list(lines))
        return (self.answer if self.answer is not None
                else lines[index]), self.accept


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
check("one file found: asked once", len(asked) == 1, str(asked))
check("and opened when the answer is yes", loaded == [only], str(loaded))
check("no list was shown for a single file", dialog.shown == [])
check("the question names the file",
      os.path.basename(only) in " ".join(str(x) for x in asked[0]))
# Asked through T(), or the check would read English on an English
# machine and fail on a German one.
whole = vpm.T('Everything comes back from it: names, separation, '
              'assignment, types, the time window. The list of files is '
              'replaced by the one the project holds.')
check("the question says the whole project comes back",
      whole in " ".join(str(x) for x in asked[0]), whole[:40])

asked, loaded, _ = offer([os.path.join(one, "Kamera1.mp4")], say_yes=False)
check("no means nothing is opened", loaded == [], str(loaded))
check("and it was still only asked once", len(asked) == 1)

print("\n3. Asked once, and once per folder")
# One window, one state: adding more from the same folder must not ask
# again.
state = {}
asked, loaded, _ = offer([os.path.join(one, "Kamera1.mp4")], state=state)
check("the first time asks", len(asked) == 1)
write(os.path.join(one, "Kamera2.mp4"))
asked, loaded, _ = offer([os.path.join(one, "Kamera1.mp4"),
                          os.path.join(one, "Kamera2.mp4")], state=state)
check("more material from the same folder does not ask again",
      asked == [] and loaded == [], "%s %s" % (asked, loaded))

# Another folder with a project of its own is a new finding, so it is
# offered -- otherwise a second recording could never be opened.
second = os.path.join(root, "Second")
write(os.path.join(second, "Kamera1.mp4"))
other = write(os.path.join(second, NAME % "second"), when=1000)
asked, loaded, _ = offer([os.path.join(one, "Kamera1.mp4"),
                          os.path.join(second, "Kamera1.mp4")], state=state)
check("a project in a folder not asked about yet is offered",
      len(asked) == 1 and loaded == [other], "%s %s" % (asked, loaded))

# Material arrives through the same door after a project is open --
# taking a block out of a recording and putting it back goes that way.
# Offering there would undo by hand what somebody had just done by hand.
after = {"project_from": os.path.join(one, "project.json")}
asked, loaded, dialog = offer([os.path.join(one, "Kamera1.mp4")],
                              state=after)
check("with a project open nothing is offered any more",
      asked == [] and loaded == [] and dialog.shown == [],
      "%s %s %s" % (asked, loaded, dialog.shown))
check("and nothing was noted as offered either",
      "projects_offered" not in after, str(after))

print("\n4. Several files are shown, not guessed between")
many = os.path.join(root, "Many")
write(os.path.join(many, "Kamera1.mp4"))
# Whole years apart, so a line showing the other file's date is visible
# as such; a few seconds apart they print the same day and minute.
old = write(os.path.join(many, NAME % "older"), when=1000)
new = write(os.path.join(many, NAME % "newer"), when=1000000000)

dialog = Dialog()
asked, loaded, dialog = offer([os.path.join(many, "Kamera1.mp4")],
                              dialog=dialog)
check("several files: no yes-or-no question", asked == [], str(asked))
check("a list was shown instead", len(dialog.shown) == 1, str(dialog.shown))
check("both files stand in it", len(dialog.shown[0]) == 2,
      str(dialog.shown))
check("the newest stands first", os.path.basename(new) in dialog.shown[0][0],
      dialog.shown[0][0])
stamps = {os.path.basename(old): 1000, os.path.basename(new): 1000000000}
askew = [line for line in dialog.shown[0]
         if not any(name in line
                    and time.strftime("%Y-%m-%d", time.localtime(when)) in line
                    for name, when in stamps.items())]
check("each file's own date stands beside it", not askew,
      "%s, wanted %s" % (askew, sorted(
          time.strftime("%Y-%m-%d", time.localtime(w))
          for w in stamps.values())))
check("the chosen one is opened", loaded == [new], str(loaded))

# The second entry, to be sure list and paths line up: picking the
# newest also succeeds on a list that has lost its order.
picked, lines_seen = [], []


class Older(Dialog):
    def getItem(self, window, title, text, lines, index, editable):
        lines_seen.extend(lines)
        return lines[1], True


vpm.project_offer(Widgets(Older()), None, {},
                  [os.path.join(many, "Kamera1.mp4")], lambda *a: True,
                  picked.append)
check("choosing the second entry opens the second file", picked == [old],
      "%s, list was %s" % (picked, lines_seen))

cancelled = []


class Cancel(Dialog):
    def getItem(self, window, title, text, lines, index, editable):
        return "", False


vpm.project_offer(Widgets(Cancel()), None, {},
                  [os.path.join(many, "Kamera1.mp4")], lambda *a: True,
                  cancelled.append)
check("cancelling the list opens nothing", cancelled == [], str(cancelled))

print("\n5. Nothing found, nothing said")
quiet = os.path.join(root, "Quiet")
write(os.path.join(quiet, "Kamera1.mp4"))
asked, loaded, dialog = offer([os.path.join(quiet, "Kamera1.mp4")])
check("no project file: no question", asked == [])
check("no project file: no list", dialog.shown == [])
check("no project file: nothing opened", loaded == [])

print("\n6. The output folder is no longer guessed from an old run")
# guess_result_folder set the output folder and the production name
# from an old handover file, possibly from another production.
check("the guessing is gone", not hasattr(vpm, "guess_result_folder"))
check("the offer is there in its place", hasattr(vpm, "project_offer"))

shutil.rmtree(root, ignore_errors=True)
print("\n----")
if bad:
    print("FAIL %d of them: %s" % (len(bad), "; ".join(bad)))
    sys.exit(1)
print("All good.")
