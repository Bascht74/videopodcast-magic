# -*- coding: utf-8 -*-
"""The format check: an older file is reported, not read.

The sections, in the order they run: what the complaint says, that it
speaks the language of the run, that nothing anywhere converts an older
file, that a freshly written file carries the number and is found again,
that both writers stamp it -- and, on the same read of the source, that
no text with named placeholders is handed a dictionary missing one.

The last section rides along on that read and is not about the file
format; it is named here so that no check of this file goes unmentioned.

Where the test reads the source it reads the file under test, so a run
against a snapshot searches the snapshot and not the working file.
"""
import os
HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = os.environ.get("VPM_SCRIPT") or os.path.join(
    os.path.dirname(HERE), "videopodcast-magic.py")
import importlib.util, io, json, sys, tempfile, time
spec = importlib.util.spec_from_file_location(
    "vpm", SCRIPT)
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


print("1. What the complaint says")
vpm.set_language("en")
# Everything below compares against this number, so it is asked after
# first: with no usable number the answers underneath say nothing.
check("the program carries a format number to compare against",
      isinstance(vpm.FILE_FORMAT, int) and vpm.FILE_FORMAT >= 1,
      "FILE_FORMAT is %r, wanted a whole number of 1 or more"
      % (vpm.FILE_FORMAT,))

fitting = vpm.format_complaint({"format": vpm.FILE_FORMAT})
check("a file written in this format draws no complaint",
      fitting == "",
      "format %d gave %d characters: %r"
      % (vpm.FILE_FORMAT, len(fitting), fitting[:40]))

older = vpm.format_complaint({"format": 1, "version": "2.11.0"})
check("a file written in an older format is complained about",
      bool(older),
      "format 1 against %d gave %d characters"
      % (vpm.FILE_FORMAT, len(older)))
check("the complaint names the version that wrote the file",
      "2.11.0" in older,
      "looked for 2.11.0 in the %d characters: %r"
      % (len(older), older[:60]))

# No version here, so it stands as "?" and brings no digits of its own:
# the only numbers findable in this text are the two format numbers.
numbers = vpm.format_complaint({"format": 1})
check("the complaint names the file's format and this one's",
      "1" in numbers and str(vpm.FILE_FORMAT) in numbers,
      "looked for 1 and %d in %r" % (vpm.FILE_FORMAT, numbers[:70]))

check("a file with no format number counts as format 1",
      vpm.format_complaint({"files": []}) == numbers,
      "without a number %r, with format 1 %r"
      % (vpm.format_complaint({"files": []})[:40], numbers[:40]))

not_a_file = vpm.format_complaint("no dict")
check("what is not a file of this program is refused as that",
      not_a_file == vpm.T("This is not a file of this program."),
      "got %d characters: %r" % (len(not_a_file), not_a_file[:60]))

print("\n2. The complaint speaks the language of the run")
# The complaint has to come out of the catalogue, not out of the code.
vpm.set_language("de")
german = vpm.format_complaint({"format": 1})
vpm.set_language("en")
english = vpm.format_complaint({"format": 1})
check("the complaint is German where the run is German",
      "Bitte den Lauf neu einrichten." in german,
      "%d characters ending %r" % (len(german), german[-40:]))
check("the complaint is English where the run is English",
      "Please set the run up again." in english,
      "%d characters ending %r" % (len(english), english[-40:]))

print("\n3. Nothing is converted")
source = io.open(SCRIPT,
                 encoding="utf-8").read()
# The old words may stand only as a label in the catalogue, never as a
# comparison value. They stay German here because German is searched for.
without_catalogue = source.split('CATALOGUE["de"] = {')[0]
# What is searched is everything before the catalogue. If that marker
# turned up early -- in a comment, in a second place -- the searches
# below would run over a handful of lines and stay green on a program
# full of leftovers, so how much of it is being read is asked first.
check("the search covers the code in front of the catalogue",
      len(without_catalogue) > len(source) // 2,
      "%d of %d characters searched" % (len(without_catalogue), len(source)))
for label in ("Inhalt", "nur in den Mix", "Audio ignorieren",
             "ohne Auphonic arbeiten", "Vorspann", "Abspann"):
    check("the old name %r is gone from the code" % label,
          '"%s"' % label not in without_catalogue,
          "found %d times in the %d characters before the catalogue"
          % (without_catalogue.count('"%s"' % label),
             len(without_catalogue)))
check("no table converts an older file instead of refusing it",
      "MIGRAT" not in source.upper() and "umstellen_alt" not in source,
      "MIGRAT %d times, umstellen_alt %d times in %d characters"
      % (source.upper().count("MIGRAT"), source.count("umstellen_alt"),
         len(source)))

print("\n4. New files carry the number")
# An empty prefix would make every json file in the folder a candidate,
# and the two searches below would then be about something else.
check("the program says what a project file is called",
      isinstance(vpm.PROJECT_PREFIX, str) and vpm.PROJECT_PREFIX != "",
      "PROJECT_PREFIX is %r" % (vpm.PROJECT_PREFIX,))
folder = tempfile.mkdtemp(prefix="format_")
fresh = {"format": vpm.FILE_FORMAT, "version": vpm.VERSION, "files": []}
new_path = os.path.join(folder, vpm.PROJECT_PREFIX + "x.json")
json.dump(fresh, io.open(new_path, "w", encoding="utf-8"))
loaded, found = vpm.find_project_file(new_path)
# The path as well as the contents: the search falls through to the
# neighbours in the same folder, so "something was found" is also true
# when the file asked after was passed over and another one answered.
check("the file just written is the one that is found",
      loaded is not None and found == new_path,
      "find_project_file returned %r for the %d bytes at %r"
      % (found, os.path.getsize(new_path), new_path))
check("and that file draws no complaint",
      vpm.format_complaint(loaded) == "",
      "format %r in the file, this version writes %d, complaint %r"
      % ((loaded or {}).get("format"), vpm.FILE_FORMAT,
         vpm.format_complaint(loaded)[:40]))

older_file = dict(fresh, format=1)
old_path = os.path.join(folder, vpm.PROJECT_PREFIX + "old.json")
json.dump(older_file, io.open(old_path, "w", encoding="utf-8"))
loaded_old, found_old = vpm.find_project_file(old_path)
check("an older file is found as well, and it is that file",
      loaded_old is not None and found_old == old_path,
      "find_project_file returned %r for the %d bytes at %r"
      % (found_old, os.path.getsize(old_path), old_path))
check("and that one is complained about",
      bool(vpm.format_complaint(loaded_old)),
      "format %r in the file, this version writes %d, complaint %d "
      "characters" % ((loaded_old or {}).get("format"), vpm.FILE_FORMAT,
                      len(vpm.format_complaint(loaded_old))))

print("\n5. Both writers stamp the number")
# Each writer by its own anchor rather than by counting the stamps: four
# places in the file write one, so a count would stay green with the
# project file's own gone.
check("the project file is stamped where it is written",
      'd = {"format": FILE_FORMAT,' in source,
      '%d such openings in %d characters'
      % (source.count('d = {"format": FILE_FORMAT,'), len(source)))
check("the project file is stamped again where it is updated",
      'd["format"] = FILE_FORMAT' in source,
      '%d such assignments in %d characters'
      % (source.count('d["format"] = FILE_FORMAT'), len(source)))
# Without the opening there is nothing to look into, and the check under
# it would search an empty piece and pass.
check("the handover file is built somewhere to be looked into",
      "handover = {" in source,
      "%d places build one in %d characters"
      % (source.count("handover = {"), len(source)))
# Two dictionaries are called handover, and only one of them is written
# out, so the stamp is asked for at the opening it belongs to rather
# than anywhere after the name.
stamped_handover = 'handover = {\n        "format": FILE_FORMAT,'
check("the handover file is stamped where it is built",
      stamped_handover in source,
      "%d of the %d openings carry the stamp on the next line"
      % (source.count(stamped_handover), source.count("handover = {")))
# Without the function the next check would read a piece of some other
# part of the file, or fall over an index; either way it would not be
# about the Resolve path any more.
pieces = source.split("def build_resolve_project")
check("the Resolve path is in the source to be searched",
      len(pieces) > 1,
      "%d pieces after splitting %d characters on the name"
      % (len(pieces), len(source)))
resolve_body = pieces[1].split("\ndef ")[0] if len(pieces) > 1 else ""
check("the Resolve path asks for the complaint before it builds",
      "complaint = format_complaint(d)" in resolve_body,
      "%d characters of build_resolve_project searched"
      % len(resolve_body))

print("\n6. Placeholders and their dictionary match")
import ast, re
tree = ast.parse(source)
gaps = []
looked = 0


def names_in_text(t):
    return set(re.findall(r"%\(([A-Za-z_][A-Za-z0-9_]*)\)", t))


def text_of(node):
    """Get the format text of an expression, joined pieces included."""
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return node.value
    if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Add):
        a, b = text_of(node.left), text_of(node.right)
        return None if a is None or b is None else a + b
    return None


for k in ast.walk(tree):
    if not (isinstance(k, ast.BinOp) and isinstance(k.op, ast.Mod)):
        continue
    text = text_of(k.left)
    if not text:
        continue
    needed = names_in_text(text)
    if not needed:
        continue
    looked += 1
    right = k.right
    if isinstance(right, ast.Dict):
        present = set(x.value for x in right.keys
                 if isinstance(x, ast.Constant))
    elif isinstance(right, ast.DictComp) and isinstance(right.value,
                                                        ast.Subscript):
        # {k: TABLE[k] for k in ("a", "b", ...)}
        present = set()
        for g in right.generators:
            if isinstance(g.iter, (ast.Tuple, ast.List)):
                present |= set(x.value for x in g.iter.elts
                          if isinstance(x, ast.Constant))
    else:
        continue
    missing = needed - present
    if missing:
        gaps.append((k.lineno, sorted(missing)))

# With nothing found the search below has nothing to say, and saying it
# green would be the quiet death this file is meant not to die.
check("the source holds texts with named placeholders at all",
      looked > 0,
      "%d such texts in %d characters" % (looked, len(source)))
check("no named placeholder is left without an entry",
      not gaps,
      "%d of %d texts short: %s" % (len(gaps), looked, gaps[:3]))


print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
