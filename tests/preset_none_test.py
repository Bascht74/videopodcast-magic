# -*- coding: utf-8 -*-
"""The entry "work without Auphonic" instead of a tick of its own."""
import os
HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = os.environ.get("VPM_SCRIPT") or os.path.join(
    os.path.dirname(HERE), "videopodcast-magic.py")
import sys, importlib.util
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
spec = importlib.util.spec_from_file_location(
    "vpm", SCRIPT)
vpm = importlib.util.module_from_spec(spec); sys.modules["vpm"] = vpm
spec.loader.exec_module(vpm)

error = []
def check(name, ok, extra=""):
    print("  %-52s %s %s" % (name, "ok" if ok else "FAIL", extra))
    if not ok:
        error.append(name)

print("1. The constant lives on the module, not in the interface")
check("value is stable and language-free", vpm.PRESET_NONE == "no-auphonic",
        vpm.PRESET_NONE)
# The entry has to come out of the catalogue, not out of the code.
vpm.set_language("de")
check("German label",
        vpm.label_of(vpm.PRESET_NONE) == "ohne Auphonic arbeiten",
        vpm.label_of(vpm.PRESET_NONE))
vpm.set_language("en")
check("English label",
        vpm.label_of(vpm.PRESET_NONE) == "work without Auphonic",
        vpm.label_of(vpm.PRESET_NONE))
# Back to the language the suite runs in, so the rest reads English.
vpm.set_language("en")

# --- The filter and plaintext logic rebuilt, as it stands in gui() -------
class Box(object):
    """A combo box that keeps value and label apart."""
    def __init__(self): self.names = []; self.values = []; self.i = 0
    def clear(self): self.names = []; self.values = []; self.i = 0
    def addItem(self, n, v=None):
        self.names.append(n); self.values.append(n if v is None else v)
    def count(self): return len(self.names)
    def currentText(self): return self.names[self.i] if self.names else ""
    def currentData(self): return self.values[self.i] if self.values else ""
    def findData(self, v):
        return self.values.index(v) if v in self.values else -1
    def setCurrentIndex(self, i): self.i = i
    def setEnabled(self, a): self.on = a
    def blockSignals(self, a): pass

def presets_filter(box, presets, multitrack, wanted=None):
    """The presets_filter of gui(), without Qt, line for line.

    A copy that drifts here asserts the opposite of the program: it
    jumps to the first real preset where the program stays on "without
    Auphonic", and a run may not spend credit because a list arrived.
    The two lines a copy tends to get wrong carry a marker.
    """
    matching = [(n, u) for n, u, m in presets if m == multitrack]
    entries = [(vpm.PRESET_NONE, vpm.label_of(vpm.PRESET_NONE))] + [
        (n, "%s  (%s)" % (n, "Multitrack" if multitrack else "normal"))
        for n, _ in matching]
    before_value = box.currentData() or ""          # <- no count() test
    box.clear()
    for value, text in entries:
        box.addItem(text, value)
    box.setCurrentIndex(0)                          # <- 0, never 1
    box.setEnabled(True)
    w = wanted or before_value or ""
    if w:
        i = box.findData(w)
        if i >= 0:
            box.setCurrentIndex(i)
    return [v for v, _ in entries]

def plaintext(box):
    choice = box.currentData()
    return "" if not choice or choice == vpm.PRESET_NONE else choice

PRESETS = [("Podcast_Zoom", "u1", False),
           ("Podcast_Multitrack", "u2", True)]

print("\n2. Without a checked key only the one entry is there")
b = Box(); names = presets_filter(b, [], False)
check("exactly one entry", names == [vpm.PRESET_NONE], str(names))
check("it is selected", b.currentData() == vpm.PRESET_NONE)
check("the list still works", b.on is True)
check("plaintext empty -> no preset in the run", plaintext(b) == "")

print("\n3. With presets the entry is on top and stays chosen")
b = Box(); names = presets_filter(b, PRESETS, False)
check("entry first", names[0] == vpm.PRESET_NONE)
check("preset after it", names[1] == "Podcast_Zoom")
# The list arriving is not a choice; Start must not spend credit unasked.
check("nothing is chosen by the list arriving", plaintext(b) == "",
      repr(b.currentData()))

print("\n4. Multitrack filters, the entry stays")
b = Box(); names = presets_filter(b, PRESETS, True)
check("entry stays on top", names[0] == vpm.PRESET_NONE)
check("only multitrack presets", names[1:] == ["Podcast_Multitrack"])

print("\n5. The choice survives a rebuild of the list")
b = Box(); presets_filter(b, PRESETS, False)
b.setCurrentIndex(b.findData(vpm.PRESET_NONE))
presets_filter(b, PRESETS, False)      # as after a multitrack switch
check("stays on the entry", b.currentData() == vpm.PRESET_NONE)

print("\n5b. The placeholder alone is not a choice")
b = Box(); presets_filter(b, [], False)     # unchecked: placeholder only
check("sits on the placeholder", b.currentData() == vpm.PRESET_NONE)
presets_filter(b, PRESETS, False)
check("and still sits on it when the presets arrive",
      plaintext(b) == "", repr(b.currentData()))

print("\n6. Back from the project file")
b = Box(); presets_filter(b, PRESETS, False, wanted=vpm.PRESET_NONE)
check("the wish from the project holds", b.currentData() == vpm.PRESET_NONE)
b = Box(); presets_filter(b, PRESETS, False, wanted="Podcast_Zoom")
check("a plain preset name still holds",
        plaintext(b) == "Podcast_Zoom")

print("\n7. The run: without a key nothing goes to auphonic.com")
def argv_with(key, preset):
    values = {"files": [("/tmp/a.mov", "video")], "clip_kinds": {},
              "multitrack": False, "key": key, "preset": preset}
    return vpm.run_argv(values, "")
argv, _plan, messages = argv_with("", "")
check("without a key: no --auphonic-api-key",
        argv is not None and "--auphonic-api-key" not in argv)
check("without a key: no message", not messages, str(messages)[:60])
argv, _plan, messages = argv_with("SECRET", "Podcast_Zoom")
check("with key and preset: both there",
        argv is not None and "--auphonic-api-key" in argv
        and "--auphonic-preset" in argv)
argv, _plan, messages = argv_with("SECRET", "")
check("key without preset: an error message",
        argv is None and messages and messages[0][0] == "error",
        messages[0][1] if messages else "")

print("\n8. The old tick is really gone")
source = open(SCRIPT, encoding="utf-8").read()
check("no QCheckBox 'this time without'",
        "this time without auphonic.com" not in source)
check("PRESET_NONE is used in the interface",
        source.count("PRESET_NONE") >= 5, str(source.count("PRESET_NONE")))

print("\n%s" % ("all good" if not error
                else "FAIL: %s" % ", ".join(error)))
sys.exit(1 if error else 0)
