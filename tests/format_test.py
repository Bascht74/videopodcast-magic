# -*- coding: utf-8 -*-
"""The format check: an older file is reported, not read."""
import os
HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = os.environ.get("VPM_SCRIPT") or os.path.join(
    os.path.dirname(HERE), "videopodcast-magic.py")
import importlib.util, io, json, sys, tempfile
spec = importlib.util.spec_from_file_location(
    "vpm", SCRIPT)
vpm = importlib.util.module_from_spec(spec); sys.modules["vpm"] = vpm
spec.loader.exec_module(vpm)

error = []
def check(name, ok, extra=""):
    print("  %-54s %s %s" % (name, "ok" if ok else "FAIL", extra))
    if not ok:
        error.append(name)

print("1. What the check says")
vpm.set_language("en")
check("matching format: no complaint",
        vpm.format_complaint({"format": vpm.FILE_FORMAT}) == "")
complaint = vpm.format_complaint({"format": 1, "version": "2.11.0"})
check("old format: complaint", bool(complaint), complaint[:60])
check("names the old version", "2.11.0" in complaint)
check("names both formats",
        "1" in complaint and str(vpm.FILE_FORMAT) in complaint)
check("without a number format 1 applies",
        bool(vpm.format_complaint({"files": []})))
check("not a dict: its own complaint",
        vpm.format_complaint("no dict")
        == "This is not a file of this program.")

print("\n2. The complaint speaks the language of the run")
# The complaint has to come out of the catalogue, not out of the code.
vpm.set_language("de")
check("German", "Bitte den Lauf neu einrichten." in
        vpm.format_complaint({"format": 1}))
vpm.set_language("en")
check("English", "Please set the run up again." in
        vpm.format_complaint({"format": 1}))
# Back to the language the suite runs in, so the rest reads English.
vpm.set_language("en")

print("\n3. Nothing is converted")
source = io.open(SCRIPT,
                 encoding="utf-8").read()
# The old words may stand only as a label in the catalogue, never as a
# comparison value. They stay German here because German is searched for.
without_catalogue = source.split('CATALOGUE["de"] = {')[0]
for label in ("Inhalt", "nur in den Mix", "Audio ignorieren",
             "ohne Auphonic arbeiten", "Vorspann", "Abspann"):
    check("no leftover for %r" % label,
            '"%s"' % label not in without_catalogue)
check("no conversion table", "MIGRAT" not in source.upper()
        and "umstellen_alt" not in source)

print("\n4. New files carry the number")
T = tempfile.mkdtemp(prefix="format_")
d = {"format": vpm.FILE_FORMAT, "version": vpm.VERSION, "files": []}
p = os.path.join(T, vpm.PROJECT_PREFIX + "x.json")
json.dump(d, io.open(p, "w", encoding="utf-8"))
loaded, found = vpm.find_project_file(p)
check("project file is found", loaded is not None)
check("and is in order", vpm.format_complaint(loaded) == "")

old = dict(d, format=1)
p2 = os.path.join(T, vpm.PROJECT_PREFIX + "old.json")
json.dump(old, io.open(p2, "w", encoding="utf-8"))
loaded2, _ = vpm.find_project_file(p2)
check("old file is found too", loaded2 is not None)
check("but complained about", bool(vpm.format_complaint(loaded2)))

print("\n5. Both writers stamp")
check("project file", '"format": FILE_FORMAT' in source
        and 'd["format"] = FILE_FORMAT' in source)
check("handover file", source.count('"format": FILE_FORMAT') >= 2)
check("the Resolve path checks too",
        "complaint = format_complaint(d)" in
        source.split("def build_resolve_project")[1].split("\ndef ")[0])

print("\n6. Placeholders and their dictionary match")
import ast, re
tree = ast.parse(source)
bad = []


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
        bad.append((k.lineno, sorted(missing)))

check("no placeholder without an entry", not bad, str(bad[:3]))


print()
if error:
    print("FAIL: " + ", ".join(error))
    sys.exit(1)
print("All good.")
