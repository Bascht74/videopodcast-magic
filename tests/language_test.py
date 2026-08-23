# -*- coding: utf-8 -*-
"""The language machinery: catalogue, detection, switch, log colours."""
import os
HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = os.environ.get("VPM_SCRIPT") or os.path.join(
    os.path.dirname(HERE), "videopodcast-magic.py")
import ast, importlib.util, io, json, re, sys, tokenize

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
STATE = os.path.join(HERE, "state", "language_state.json")
spec = importlib.util.spec_from_file_location("vpm", SCRIPT)
vpm = importlib.util.module_from_spec(spec); sys.modules["vpm"] = vpm
spec.loader.exec_module(vpm)

error = []
def check(name, ok, extra=""):
    print("  %-54s %s %s" % (name, "ok" if ok else "FAIL", extra))
    if not ok:
        error.append(name)

if not os.path.exists(STATE):
    # No baseline means every counter is seeded from what is there now, so
    # the ratchet cannot fail on this run. Say so -- a lost state file must
    # not look like a clean bill of health.
    print("  NOTE: %s is missing. The counters below are being set from\n"
          "        the source as it stands; nothing is being held to\n"
          "        account this run." % os.path.basename(STATE))

def remember_state(key, value):
    """Ratchet: the counter may only get smaller."""
    d = {}
    if os.path.exists(STATE):
        try:
            d = json.load(io.open(STATE, encoding="utf-8"))
        except Exception:
            d = {}
    old = d.get(key)
    d[key] = value if old is None else min(old, value)
    json.dump(d, io.open(STATE, "w", encoding="utf-8"))
    return old if old is not None else value

print("1. Which languages there are")
check("English is the source", vpm.SOURCE_LANG == "en")
check("German is among them", "de" in vpm.languages(), str(vpm.languages()))
check("de_DE.UTF-8 becomes de", vpm.known_language("de_DE.UTF-8") == "de")
check("de-AT becomes de", vpm.known_language("de-AT") == "de")
check("fr_FR becomes en", vpm.known_language("fr_FR") == "en")
check("nothing becomes en", vpm.known_language("") == "en")

print("\n2. One more language needs only a catalogue entry")
vpm.CATALOGUE["fr"] = {"Content": "Contenu"}
try:
    check("fr is now on offer", "fr" in vpm.languages())
    check("fr_FR now becomes fr", vpm.known_language("fr_FR") == "fr")
    vpm.set_language("fr")
    check("translated text comes out French", vpm.T("Content") == "Contenu")
    check("missing text stays English", vpm.T("Outro") == "Outro")
finally:
    del vpm.CATALOGUE["fr"]
vpm.set_language("de")

print("\n3. Translating and filling in")
# The German catalogue is the subject here, so this expectation is German.
check("German comes from the catalogue", vpm.T("Intro") == "Vorspann")
vpm.set_language("en")
check("English stays as it stands", vpm.T("Intro") == "Intro")
check("placeholders get filled", vpm.T("a %s c", "b") == "a b c")
check("several placeholders", vpm.T("%s-%s", 1, 2) == "1-2")
check("unknown language falls back to English", (vpm.set_language("xx"),
        vpm.LANG)[1] == "en")
vpm.set_language("de")

print("\n4. The --lang switch")
ap = vpm.build_argument_parser()
lang = [a for a in ap._actions if "--lang" in (a.option_strings or [])]
check("it is there", bool(lang))
check("knows every language", sorted(lang[0].choices) == vpm.languages(),
        str(lang[0].choices))
check("without a value: system language", ap.parse_args([]).lang is None)
check("with a value it arrives", ap.parse_args(["--lang", "en"]).lang == "en")

print("\n5. Values and labels are separate")
for name in ("MIX_ONLY", "IGNORE_AUDIO", "PRESET_NONE", "TYPE_CONTENT",
             "TYPE_INTRO", "TYPE_OUTRO", "TYPE_IGNORED"):
    value = getattr(vpm, name)
    check("%s is language-free" % name,
            re.match(r"^[a-z][a-z-]*$", value) is not None, value)
vpm.set_language("de")
check("German label", vpm.label_of(vpm.TYPE_INTRO) == "Vorspann")
vpm.set_language("en")
check("English label", vpm.label_of(vpm.TYPE_INTRO) == "Intro")
check("unknown text stays as it is", vpm.label_of("Camera 1.mov")
        == "Camera 1.mov")
vpm.set_language("de")

print("\n6. The kind of a log line sits on the text, not in the word")
check("heading", vpm.split_kind(vpm.as_head("X")) == ("heading", "X"))
check("success", vpm.split_kind(vpm.as_good("X")) == ("good", "X"))
check("warning", vpm.split_kind(vpm.as_warn("X")) == ("warning", "X"))
check("error", vpm.split_kind(vpm.as_bad("X")) == ("error", "X"))
check("without a marker: plain text",
        vpm.split_kind("CAREFUL: all good")
        == ("text", "CAREFUL: all good"))
check("the marker can be stripped",
        vpm.strip_marks(vpm.as_bad("X") + " " + vpm.as_head("Y")) == "X Y")
check("without a marker the text stays the same",
        vpm.strip_marks("nothing to do") == "nothing to do")

print("\n7. The terminal colours by that and leaves nothing behind")
class Catch(object):
    def __init__(self): self.text = ""
    def write(self, t): self.text += t
    def flush(self): pass

f = Catch(); w = vpm.ColourWriter(f, colour=True)
w.write(vpm.as_head("RESULT") + "\n")
check("colour for the heading", vpm.ANSI["heading"] in f.text, repr(f.text))
check("the marker is gone", "\x01" not in f.text)
check("the text stands there untouched", "RESULT" in f.text)

f = Catch(); w = vpm.ColourWriter(f, colour=False)
w.write(vpm.as_bad("Abort") + "\n")
check("without colour only the text", f.text == "Abort\n", repr(f.text))

f = Catch(); w = vpm.ColourWriter(f, colour=True)
w.write(vpm.as_head("\nRESULT") + "\n  Line\n")
check("a marker before the break belongs to the next line",
        f.text.startswith("\n" + vpm.ANSI["heading"] + "RESULT"),
        repr(f.text[:40]))
check("the line below stays uncoloured",
        f.text.endswith("  Line\n"), repr(f.text[-20:]))

f = Catch(); w = vpm.ColourWriter(f, colour=True)
w.write("  Done without a marker\n")
check("without a marker no colour", "\033[" not in f.text, repr(f.text))

print("\n8. The log window colours the same way")
try:
    from PySide6 import QtWidgets, QtGui
    app = QtWidgets.QApplication.instance() or QtWidgets.QApplication([])
    source = io.open(SCRIPT, encoding="utf-8").read()
    check("the log reads the marker",
            "split_kind(part)" in source and "self._kind" in source)
    check("the file gets the text without the marker",
            "self.having.write(strip_marks(text))" in source)
except ImportError:
    check("PySide6 missing -- window not checked", True)

print("\n9. Every T() text is in the catalogue")
tree = ast.parse(io.open(SCRIPT, encoding="utf-8").read())
asked = []
for node in ast.walk(tree):
    if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) \
            and node.func.id in ("T", "TN") and node.args:
        # T(text, ...) -- TN(number, singular, plural)
        args = node.args[1:] if node.func.id == "TN" else node.args[:1]
        for a in args:
            if isinstance(a, ast.Constant) and isinstance(a.value, str):
                asked.append(a.value)
for t in vpm.CHOICE_LABELS.values():
    asked.append(t)
absent = sorted(set(t for t in asked if t not in vpm.CATALOGUE["de"]))
check("no gap in the German catalogue", not absent,
        "%d missing: %s" % (len(absent), absent[:3]))

print("\n10. No output line guesses its colour from the wording")
OUTPUT = {"print", "write_through", "write", "append_text", "OUTPUT_SINK"}
MARKERS = {"as_head", "as_good", "as_warn", "as_bad"}

def first_text(node):
    while True:
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            return node.value
        if isinstance(node, ast.BinOp) and isinstance(node.op,
                                                      (ast.Mod, ast.Add)):
            node = node.left
            continue
        return None

unmarked = []
for node in ast.walk(tree):
    if not isinstance(node, ast.Call) or not node.args:
        continue
    if isinstance(node.func, ast.Name):
        name = node.func.id
    elif isinstance(node.func, ast.Attribute):
        # f.write(...) writes a file, not the log.
        if isinstance(node.func.value, ast.Name) \
                and node.func.value.id in ("f", "file"):
            continue
        name = node.func.attr
    else:
        name = ""
    if name not in OUTPUT:
        continue
    if isinstance(node.args[0], ast.Call) \
            and isinstance(node.args[0].func, ast.Name) \
            and node.args[0].func.id in MARKERS:
        continue
    t = first_text(node.args[0])
    if t is None:
        continue
    first = ([line for line in t.split("\n") if line.strip()]
             or [""])[0]
    head = first.strip().split(":", 1)[0]
    if first[:1] not in (" ", "\t") and len(head) > 2 \
            and head == head.upper() and re.search(r"[A-Z]", head) \
            and not head.startswith("%"):
        unmarked.append((node.lineno, first[:60]))
old = remember_state("uncoloured", len(unmarked))
check("headings without a marker: %d (ratchet %d)" % (len(unmarked), old),
        len(unmarked) <= old, str(unmarked[:3]))

print("\n11. The old word detection is really gone")
source = io.open(SCRIPT, encoding="utf-8").read()
check("no log_line_kind any more", "log_line_kind" not in source)
# These were the words the old guesser read the colour off.
for label in ("DONE", "failed\" in", "Finished with errors\" in"):
    check("colour no longer hangs on %r" % label, label not in source)

print("\n12. Switches and targets are English")
# The list stays German on purpose: it is what must not turn up.
GERMAN = ("ohne", "kein", "totale", "sprache_", "vorne", "hinten",
          "zuordnung", "trotzdem", "dateien", "mindest", "plattform",
          "vorflug", "pruefen", "projekt", "tonspuren", "warten", "weiter",
          "fertig", "schnitt", "spuren", "kennzahlen", "sprecher")
ap = vpm.build_argument_parser()
bad = []
for entry in ap._actions:
    for o in (entry.option_strings or [entry.dest]):
        label = o.lstrip("-").replace("-", "_")
        for d in GERMAN:
            if d in label or d in (entry.dest or ""):
                bad.append((o, entry.dest, d))
check("no German switch, no German target", not bad, str(bad[:3]))
bad_choices = []
for entry in ap._actions:
    for w in (entry.choices or []):
        if not isinstance(w, str):
            continue
        for d in ("ergebnis", "uebernehmen", "hochladen", "abbruch", "neu",
                  "aktualisieren", "verwenden", "rundfunk"):
            if w == d:
                bad_choices.append((entry.dest, w))
check("no German choice values", not bad_choices, str(bad_choices))


print("\n13. Every language writes numbers its own way")
vpm.set_language("de")
check("German: comma", vpm.decimal_text("%.3f" % 25.0) == "25,000")
check("German: clock time", vpm.as_hms(3725.5) == "1:02:05,500",
        vpm.as_hms(3725.5))
vpm.set_language("en")
check("English: dot", vpm.decimal_text("%.3f" % 25.0) == "25.000")
check("English: clock time", vpm.as_hms(3725.5) == "1:02:05.500",
        vpm.as_hms(3725.5))
check("no hard-coded comma left in the source",
        'replace(".", ",")' not in source)
vpm.set_language("de")
check("German: thousands with a dot", vpm.group_text(48000) == "48.000")
vpm.set_language("en")
check("English: thousands with a comma", vpm.group_text(48000) == "48,000")
check("no hard-coded thousands mark left",
        'format(SR, ",d").replace' not in source)
vpm.set_language("de")

print("\n14. No translation as early as import time")
import ast as _ast
_b = _ast.parse(source)
def _module_level(node):
    for k in _ast.iter_child_nodes(node):
        if isinstance(k, (_ast.FunctionDef, _ast.AsyncFunctionDef,
                          _ast.ClassDef)):
            continue
        if isinstance(k, _ast.Call) and isinstance(k.func, _ast.Name) \
                and k.func.id in ("T", "TN"):
            yield k
        for x in _module_level(k):
            yield x
_early = list(_module_level(_b))
check("no T()/TN() at module level", not _early,
        str([k.lineno for k in _early[:3]]))


print("\n15. The marker stays in the log")
import ast as _a2
_b2 = _a2.parse(source)
_MARK = {"as_head", "as_good", "as_warn", "as_bad"}
_in_file = []
for _k in _a2.walk(_b2):
    if isinstance(_k, _a2.Call) and isinstance(_k.func, _a2.Attribute) \
            and _k.func.attr == "write" \
            and isinstance(_k.func.value, _a2.Name) \
            and _k.func.value.id in ("f", "file"):
        for _x in _a2.walk(_k):
            if isinstance(_x, _a2.Call) and isinstance(_x.func, _a2.Name) \
                    and _x.func.id in _MARK:
                _in_file.append(_k.lineno)
check("no marker in a written file", not _in_file, str(_in_file[:3]))

print("\n16. Numbers in files do not hang on the language")
check("the metrics CSV writes with a dot",
        'return "" if x is None else "%.*f" % (spots, x)' in source)
check("the speakers CSV too", 'as_hms(a, ".")' in source)
# The headers are written through csv_line() as tuples, so the check looks
# for the tuple rather than for a finished line.
for head in ('("Area", "Metric", "Before", "After",',
             '("Speaker", "Start TC", "End TC",',
             '("Shot", "Camera", "Speaker", "Start TC",'):
    check("CSV header fixed: %s" % head[1:29], head in source)
check("CSV rows are comma separated, never by language",
        'return ",".join(out) + "\\n"' in source)
check("no semicolon separator left",
        'f.write("%s;' not in source and '";".join(str(x) for x in r)'
        not in source)

print("\n17. No German word outside the catalogue")
# Two dictionaries decide, and the catalogue acts as a third: a word that
# German knows and English does not is German, and so is every word the
# German side of the catalogue uses but the English side does not. What
# is left over after the two lists below is a real find.
GERMAN_KEEP = set("""
bilder dokumente filme musik schreibtisch
""".split())          # folder names on a German system, on purpose
NOT_GERMAN = set("""
also ansi antialiasing api ascii backend byte codec codecs cpu eng ext
frontend gbr html installation iso lang man marker mpeg multi normal
popen programme sei stand std standard systems url urls xml
""".split())          # technical words a German dictionary happens to know


def word_parts(word):
    """Split a name, a text or a comment into its word parts."""
    out = []
    for piece in re.split(r"[^0-9A-Za-z\u00c0-\u024f]+", word):
        for part in re.findall(r"[A-Z]?[a-z\u00df-\u00ff]+"
                                r"|[A-Z]+(?![a-z])", piece):
            if len(part) > 2:
                out.append(part.lower())
    return out


def catalogue_words():
    """German words the catalogue uses and the English side does not."""
    i = source.find('CATALOGUE["de"] = {')
    keys, values = set(), set()
    for node in ast.walk(ast.parse(source[i:])):
        if not isinstance(node, ast.Dict):
            continue
        for a, b in zip(node.keys, node.values):
            if isinstance(a, ast.Constant) and isinstance(a.value, str):
                keys.update(word_parts(a.value))
            if isinstance(b, ast.Constant) and isinstance(b.value, str):
                values.update(word_parts(b.value))
    return values - keys


def german_check():
    """A test for "is this word German" -- None without a dictionary."""
    try:
        from spellchecker import SpellChecker
    except ImportError:
        return None
    de, en = SpellChecker(language="de"), SpellChecker(language="en")
    return lambda w: w in de and w not in en


_known = catalogue_words()
_is_german = german_check()
_border = source[:source.find('CATALOGUE["de"] = {')].count("\n") + 1
_found = []
for _t in tokenize.generate_tokens(io.StringIO(source).readline):
    if _t.start[0] >= _border:
        break
    if _t.type not in (tokenize.NAME, tokenize.STRING, tokenize.COMMENT):
        continue
    # A long run without a space is data (base64, a hash), not language.
    if _t.type == tokenize.STRING and len(_t.string) > 40 \
            and " " not in _t.string:
        continue
    for _w in word_parts(_t.string):
        if _w in NOT_GERMAN or _w in GERMAN_KEEP:
            continue
        if _w in _known or (_is_german and _is_german(_w)):
            _found.append((_t.start[0], _w))
check("a dictionary is installed", _is_german is not None,
        "" if _is_german else "pip install pyspellchecker")
_limit = remember_state("german_words", len(_found))
check("German words: %d (ratchet %d)" % (len(_found), _limit),
        len(_found) <= _limit, str(sorted(set(w for _z, w in _found))[:6]))

# The suite runs under LANG=C, so hand the module back in English.
vpm.set_language("en")

print()
if error:
    print("FAIL: " + ", ".join(error))
    sys.exit(1)
print("All good.")
