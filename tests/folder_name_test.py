# -*- coding: utf-8 -*-
"""Which folder name is a production, and which one says nothing.

The folder the files sit in names the production, which is wrong for
the handful of folders every home directory has. Which names those are
cannot be guessed: macOS and Windows keep the English name on disk and
only show the translated one, while Linux really renames them and
writes its choice into user-dirs.dirs, so the list is read from there.
"""
import os
HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = os.environ.get("VPM_SCRIPT") or os.path.join(
    os.path.dirname(HERE), "videopodcast-magic.py")
import importlib.util, sys, tempfile
spec = importlib.util.spec_from_file_location("vpm", SCRIPT)
vpm = importlib.util.module_from_spec(spec); sys.modules["vpm"] = vpm
spec.loader.exec_module(vpm)

bad = []


def check(what, ok, detail=""):
    print("  %-56s %s%s" % (what, "ok" if ok else "FAIL",
                            "" if ok else "   " + detail))
    if not ok:
        bad.append(what)


def fresh():
    """Forget what was read once -- the list is built on first use."""
    del vpm._general_extra[:]


def name_for(folder):
    return vpm.guess_production_name(os.path.join(folder, "a.mov"))


made_up = "Production "        # what a meaningless folder falls back to

print("1. A folder that means something keeps its name")
fresh()
check("a production folder", name_for("/Volumes/Recordings/Interview_7")
      == "Interview_7", name_for("/Volumes/Recordings/Interview_7"))
check("even one that reads like a date",
      name_for("/x/2026-08-15 Studio") == "2026-08-15 Studio")

print("\n2. The folders every home directory has say nothing")
for folder in ("Desktop", "Downloads", "Documents", "Movies", "Music",
               "Pictures", "Videos", "Public", "temp", "tmp"):
    check("%-10s -> date and time" % folder,
          name_for("/Users/x/" + folder).startswith(made_up),
          name_for("/Users/x/" + folder))
check("and the spelling does not matter",
      name_for("/Users/x/DOWNLOADS").startswith(made_up))

print("\n3. A place that has no folder name at all")
check("the home folder itself",
      name_for(os.path.expanduser("~")).startswith(made_up))
check("the root of a volume",
      name_for("/Volumes/Recordings").startswith(made_up))

print("\n4. Translated names are read, not guessed")
# On a Mac the desktop is called Desktop on disk whatever the system
# speaks, so without the file "Schreibtisch" is a folder somebody named.
home = tempfile.mkdtemp(prefix="foldername_")
os.environ["XDG_CONFIG_HOME"] = os.path.join(home, "empty")
fresh()
check("Schreibtisch without the file is a production",
      name_for("/Users/x/Schreibtisch") == "Schreibtisch",
      name_for("/Users/x/Schreibtisch"))
config = os.path.join(home, "config")
os.makedirs(config)
with open(os.path.join(config, "user-dirs.dirs"), "w") as f:
    f.write('# a Linux home directory in German\n'
            'XDG_DESKTOP_DIR="$HOME/Schreibtisch"\n'
            'XDG_DOWNLOAD_DIR="$HOME/Downloads"\n'
            'XDG_VIDEOS_DIR="$HOME/Videos"\n')
os.environ["XDG_CONFIG_HOME"] = config
fresh()
check("with the file it says nothing",
      name_for("/home/x/Schreibtisch").startswith(made_up),
      name_for("/home/x/Schreibtisch"))
check("the English names still count too",
      name_for("/home/x/Documents").startswith(made_up))
check("and a real folder is still a production",
      name_for("/home/x/Interview_7") == "Interview_7")

print("\n5. No language is hard coded")
import io
source = io.open(SCRIPT, encoding="utf-8").read()
where = source.split("def guess_production_name")[0].split(
    "GENERAL_FOLDERS")[-1]
check("no German folder name in the list",
      not any(w in where.lower() for w in
              ("schreibtisch", "dokumente", "filme", "musik", "bilder")),
      where[:120])

print()
if bad:
    print("FAIL: %d of the checks" % len(bad))
    sys.exit(1)
print("all checks passed")
