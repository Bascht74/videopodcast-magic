# -*- coding: utf-8 -*-
"""No language answers fewer of the program's texts than it did before.

German answers all of them; the eleven others answer a quarter, and
nothing said so for months -- what the catalogues are held to is that
they carry the same placeholders and no key twice, never how much of
the program they cover.

The sections: that no shipped catalogue carries an empty translation,
which would blank a label rather than leave it English; that the gap
between what the program says and what each language answers may only
close; and that the languages the window offers and the catalogues on
disk are the same set, so neither can appear without the other.
"""
import ast
import os
import the_program
HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = the_program.SCRIPT
import sys, time
import ratchet
vpm = the_program.load()
began = time.time()
STATE = os.path.join(HERE, "state", "coverage_state.json")
state = ratchet.Ratchet(STATE)
done = 0
bad = []


def check(name, ok, extra=""):
    global done
    done += 1
    print("  %-58s %s %s" % (name, "ok" if ok else "FAIL", extra))
    if not ok:
        bad.append("%s [%s]" % (name, extra or "no numbers"))


state.announce()
HOME = os.path.dirname(SCRIPT)
CATALOGUES = sorted(
    (os.path.splitext(os.path.basename(p))[0], os.path.join(HOME, "language", p))
    for p in os.listdir(os.path.join(HOME, "language")) if p.endswith(".po"))

print("\n1. What the program says")
# Every text handed to T() or TN() as a literal, over every piece --
# reading one file measures a program with holes in it the moment a
# piece moves out, and it moves out silently.
said = set()
for _piece, body in the_program.pieces():
    for node in ast.walk(ast.parse(body)):
        if not (isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
                and node.func.id in ("T", "TN")):
            continue
        for arg in node.args:
            if isinstance(arg, ast.Constant) and isinstance(arg.value, str):
                said.add(arg.value)
check("the program was read, not an empty tree",
      len(said) > 1000,
      "%d texts out of %d pieces" % (len(said), len(the_program.pieces())))

print("\n2. No catalogue carries an empty translation")
# An empty msgstr used to be kept, and T() handed back the empty string
# -- the label vanished instead of staying English. read_po leaves it
# out now, so an empty entry is dead weight rather than damage; it is
# still a fault, because somebody wrote a key and no answer.
blank = []
for code, path in CATALOGUES:
    for key, value, at in the_program.po_pairs(path):
        if key and not value:
            blank.append("%s:%d" % (code, at))
check("no shipped catalogue carries an empty translation",
      not blank,
      "%d empty of %d catalogues: %s"
      % (len(blank), len(CATALOGUES), blank[:4] or "none"))

print("\n3. The gap may only close")
gaps = {}
for code, path in CATALOGUES:
    answers = set(the_program.po_texts(path))
    gaps[code] = len([w for w in said if w not in answers])
# One check over all of them, not one per language: a check whose name
# is computed carries one wording for twelve judgements, and the
# register cannot then say which of the twelve was ever seen red.
worse = []
for code in sorted(gaps):
    limit = state.number("gap_" + code, gaps[code])
    state.note(limit, gaps[code])
    if gaps[code] > limit:
        worse.append("%s %d against %d" % (code, gaps[code], limit))
check("no language answers fewer of the program's texts than before",
      not worse,
      "%d of %d languages fell back: %s"
      % (len(worse), len(gaps), worse[:4] or "none"))

print("\n4. The list of languages and the catalogues on disk agree")
# Not "is every catalogue held to a number": the ratchet adopts a new
# key the first time it sees it, so that judgement is true by
# construction and can never fall. This one can: a language offered
# without a catalogue answers English under its own name, and a
# catalogue nobody offers is never read.
offered = set(vpm.language.LANGUAGE_NAMES) - {"en"}
on_disk = set(code for code, _p in CATALOGUES)
check("every language the window offers has a catalogue on disk",
      not (offered - on_disk),
      "%d offered, %d on disk, without a catalogue: %s"
      % (len(offered), len(on_disk), sorted(offered - on_disk) or "none"))
check("and no catalogue lies there that the window never offers",
      not (on_disk - offered),
      "%d on disk, %d offered, never offered: %s"
      % (len(on_disk), len(offered), sorted(on_disk - offered) or "none"))

print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
