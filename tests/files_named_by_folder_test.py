# -*- coding: utf-8 -*-
"""Which folder name is a production, and which one says nothing.

The folder the files sit in names the production, which is wrong for
the handful of folders every home directory has. Which names those are
cannot be guessed: macOS and Windows keep the English name on disk and
only show the translated one, while Linux really renames them and
writes its choice into user-dirs.dirs, so the list is read from there.

The sections: the built-in list alone, before anything is read; a
folder that means something keeps its name; the folders every home has
say nothing whatever their spelling, and what stands in carries the day
and the minute; so do the places with no folder name of their own --
disk root, volume root, home folder; a translated name counts only
where user-dirs.dirs gives it, and the built-in names count on beside
it; and no language stands in the list. What a section rests on is
checked before it, so a red line names the first thing that was wrong.
"""
import os
HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = os.environ.get("VPM_SCRIPT") or os.path.join(
    os.path.dirname(HERE), "videopodcast-magic.py")
import importlib.util, io, re, sys, tempfile, time
spec = importlib.util.spec_from_file_location("vpm", SCRIPT)
vpm = importlib.util.module_from_spec(spec); sys.modules["vpm"] = vpm
spec.loader.exec_module(vpm)

began = time.time()
done = 0
bad = []


def check(name, ok, extra=""):
    global done
    done += 1
    print("  %-58s %s %s" % (name, "ok" if ok else "FAIL", extra))
    if not ok:
        bad.append("%s [%s]" % (name, extra or "no numbers"))


def fresh():
    """Forget what was read once -- the list is built on first use."""
    del vpm._general_extra[:]


def name_for(folder):
    return vpm.guess_production_name(os.path.join(folder, "a.mov"))


# What a folder name that says nothing turns into. Written out here and
# not fetched from the program, so a change on that side shows up as a
# failure rather than travelling into the expectation unseen.
FALLBACK = "Production "
SHAPE = re.compile(r"^Production \d{4}-\d\d-\d\d \d\d-\d\d$")
# The names the program carries built in, again as a value rather than
# read out of it.
BUILT_IN = ("desktop", "downloads", "documents", "movies", "music",
            "pictures", "videos", "public", "temp", "tmp")
GERMAN = ("schreibtisch", "dokumente", "filme", "musik", "bilder")

# Every section but the fifth has to see the built-in list on its own,
# so the reader is pointed at a folder that holds no user-dirs.dirs --
# otherwise a German Linux machine would answer the first four.
home = tempfile.mkdtemp(prefix="foldername_")
nothing_there = os.path.join(home, "empty")
os.environ["XDG_CONFIG_HOME"] = nothing_there
fresh()

print("1. The built-in list alone, before anything is read")
have = vpm.general_folder_names()
check("the list of names that say nothing is the built-in one and no more",
      have == set(BUILT_IN),
      "%d names against %d built in, over and above them %s"
      % (len(have), len(BUILT_IN), sorted(have - set(BUILT_IN))))

print("\n2. A folder that means something keeps its name")
got = name_for("/Volumes/Recordings/Interview_7")
check("the folder the files sit in becomes the production name",
      got == "Interview_7", "%r wanted 'Interview_7'" % got)
got = name_for("/x/2026-08-15 Studio")
check("a folder name that begins with a date is kept as it stands",
      got == "2026-08-15 Studio", "%r wanted '2026-08-15 Studio'" % got)

print("\n3. The folders every home directory has say nothing")
for folder in ("Desktop", "Downloads", "Documents", "Movies", "Music",
               "Pictures", "Videos", "Public", "temp", "tmp"):
    got = name_for("/Users/x/" + folder)
    check("%s is a folder every home has and names no production" % folder,
          got.startswith(FALLBACK), "%r wanted a name beginning %r"
          % (got, FALLBACK))
got = name_for("/Users/x/DOWNLOADS")
check("the same folder shouted in capitals names no production either",
      got.startswith(FALLBACK), "%r wanted a name beginning %r"
      % (got, FALLBACK))
got = name_for("/Users/x/Desktop")
check("what stands in instead carries the day and the minute",
      bool(SHAPE.match(got)), "%r against %s" % (got, SHAPE.pattern))

print("\n4. A place that has no folder name of its own")
got = name_for(os.sep)
check("a file lying at the root of the disk names no production",
      got.startswith(FALLBACK), "%r wanted a name beginning %r"
      % (got, FALLBACK))
got = name_for("/Volumes/Recordings")
check("a file lying on the root of a volume names no production",
      got.startswith(FALLBACK), "%r wanted a name beginning %r"
      % (got, FALLBACK))
got = name_for(os.path.expanduser("~"))
check("the home folder itself names no production",
      got.startswith(FALLBACK), "%r for %s, wanted a name beginning %r"
      % (got, os.path.expanduser("~"), FALLBACK))

print("\n5. Translated names are read, not guessed")
# On a Mac the desktop is called Desktop on disk whatever the system
# speaks, so without the file "Schreibtisch" is a folder somebody named.
absent = os.path.join(nothing_there, "user-dirs.dirs")
check("no user-dirs.dirs stands where the program has looked so far",
      not os.path.exists(absent), "nothing wanted at %s" % absent)
got = name_for("/Users/x/Schreibtisch")
check("a translated name no file on disk claims is a production",
      got == "Schreibtisch", "%r wanted 'Schreibtisch'" % got)

config = os.path.join(home, "config")
os.makedirs(config)
written = os.path.join(config, "user-dirs.dirs")
with io.open(written, "w", encoding="utf-8") as f:
    f.write(u'# a Linux home directory in German\n'
            u'XDG_DESKTOP_DIR="$HOME/Schreibtisch"\n'
            u'XDG_DOWNLOAD_DIR="$HOME/Downloads"\n'
            u'XDG_VIDEOS_DIR="$HOME/Videos"\n')
os.environ["XDG_CONFIG_HOME"] = config
fresh()
# The program joins XDG_CONFIG_HOME with this name, so the check asks
# for that path and not for the one the test wrote -- asking for its own
# would pass whatever name it had put the file under.
looked_at = os.path.join(os.environ["XDG_CONFIG_HOME"], "user-dirs.dirs")
check("the user-dirs.dirs the test wrote is where the program looks",
      os.path.exists(looked_at) and u"Schreibtisch" in io.open(
          looked_at, encoding="utf-8").read(),
      "%d bytes at %s, %s written"
      % (os.path.getsize(looked_at) if os.path.exists(looked_at) else -1,
         looked_at, written))
got = name_for("/home/x/Schreibtisch")
check("a name user-dirs.dirs gives a folder names no production",
      got.startswith(FALLBACK), "%r wanted a name beginning %r"
      % (got, FALLBACK))
got = name_for("/home/x/Documents")
check("the built-in English names count on beside the ones read in",
      got.startswith(FALLBACK), "%r wanted a name beginning %r"
      % (got, FALLBACK))
got = name_for("/home/x/Interview_7")
check("a folder user-dirs.dirs does not name is still a production",
      got == "Interview_7", "%r wanted 'Interview_7'" % got)

print("\n6. No language is written into the list")
source = io.open(SCRIPT, encoding="utf-8").read()
check("the built-in list and the function that guesses are both in the source",
      "\nGENERAL_FOLDERS = (" in source
      and "\ndef guess_production_name" in source,
      "list at %d, guesser at %d, -1 is missing"
      % (source.find("\nGENERAL_FOLDERS = ("),
         source.find("\ndef guess_production_name")))
where = source.split("\ndef guess_production_name")[0].split(
    "\nGENERAL_FOLDERS = (")[-1]
check("what is read out of the source is that list and its reader, no more",
      len(where) < 1500 and all(n in where for n in BUILT_IN),
      "%d characters under a bound of 1500, %d of %d built-in names in them"
      % (len(where), sum(1 for n in BUILT_IN if n in where), len(BUILT_IN)))
found = [w for w in GERMAN if w in where.lower()]
check("no German folder name stands in the built-in list",
      not found, "%d of %d German names found: %s"
      % (len(found), len(GERMAN), found))

print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
