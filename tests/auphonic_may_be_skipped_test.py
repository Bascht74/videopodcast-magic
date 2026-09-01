# -*- coding: utf-8 -*-
"""The entry "work without Auphonic" instead of a tick of its own."""
import os
HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = os.environ.get("VPM_SCRIPT") or os.path.join(
    os.path.dirname(HERE), "videopodcast-magic.py")
import sys, importlib.util, time

began = time.time()

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
spec = importlib.util.spec_from_file_location(
    "vpm", SCRIPT)
vpm = importlib.util.module_from_spec(spec); sys.modules["vpm"] = vpm
spec.loader.exec_module(vpm)

done = 0
error = []
def check(name, ok, extra=""):
    global done
    done += 1
    print("  %-52s %s %s" % (name, "ok" if ok else "FAIL", extra))
    if not ok:
        error.append("%s [%s]" % (name, extra or "no numbers"))


# --- Saying what came out, on one line, without hiding the empty case ---
def nth(seq, i):
    """The i-th entry, or None where the list is shorter.

    A short list is a result and has to be reported; seq[i] would end
    the run in an IndexError and the failed check would never print.
    """
    return seq[i] if len(seq) > i else None


def switches(argv, *names):
    """Which of the named switches stand in the command line.

    Never the value beside them: one of them is the API key, and a key
    does not go into a log.
    """
    if argv is None:
        return "no command line at all"
    return "%d words, " % len(argv) + ", ".join(
        "%s %s" % (n, "there" if n in argv else "absent") for n in names)


def said(messages):
    """How many messages came back, with the kind and title of each."""
    short = [(m[0], m[1]) for m in messages]
    return "%d messages %s" % (len(messages), str(short).replace("\n", " "))


print("1. The constant lives on the module, not in the interface")
check("value is stable and language-free", vpm.PRESET_NONE == "no-auphonic",
        "PRESET_NONE is %r, wanted %r" % (vpm.PRESET_NONE, "no-auphonic"))
# The entry has to come out of the catalogue, not out of the code.
vpm.set_language("de")
check("German label",
        vpm.label_of(vpm.PRESET_NONE) == "ohne Auphonic arbeiten",
        "label_of(%r) is %r, wanted %r"
        % (vpm.PRESET_NONE, vpm.label_of(vpm.PRESET_NONE),
           "ohne Auphonic arbeiten"))
vpm.set_language("en")
check("English label",
        vpm.label_of(vpm.PRESET_NONE) == "work without Auphonic",
        "label_of(%r) is %r, wanted %r"
        % (vpm.PRESET_NONE, vpm.label_of(vpm.PRESET_NONE),
           "work without Auphonic"))
# Back to the language the suite runs in, so the rest reads English.
vpm.set_language("en")

# --- The filter and plaintext logic rebuilt, as it stands in gui() -------
class Box(object):
    """A combo box that keeps value and label apart."""
    def __init__(self):
        self.names = []; self.values = []; self.i = 0
        # Not set only by setEnabled, so a filter that never enables the
        # list reports "None against True" instead of an AttributeError.
        self.on = None
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
check("exactly one entry", names == [vpm.PRESET_NONE],
      "%d entries %s, wanted [%r]" % (len(names), names, vpm.PRESET_NONE))
check("it is selected", b.currentData() == vpm.PRESET_NONE,
      "entry %d of %d is %r, wanted %r"
      % (b.i, b.count(), b.currentData(), vpm.PRESET_NONE))
check("the list still works", b.on is True,
      "the list is enabled=%r, wanted True" % (b.on,))
check("plaintext empty -> no preset in the run", plaintext(b) == "",
      "plaintext %r, wanted '' (the box sits on %r)"
      % (plaintext(b), b.currentData()))

print("\n3. With presets the entry is on top and stays chosen")
b = Box(); names = presets_filter(b, PRESETS, False)
check("entry first", nth(names, 0) == vpm.PRESET_NONE,
      "first of %d is %r, wanted %r -- whole list %s"
      % (len(names), nth(names, 0), vpm.PRESET_NONE, names))
check("preset after it", nth(names, 1) == "Podcast_Zoom",
      "second of %d is %r, wanted %r -- whole list %s"
      % (len(names), nth(names, 1), "Podcast_Zoom", names))
# The list arriving is not a choice; Start must not spend credit unasked.
check("nothing is chosen by the list arriving", plaintext(b) == "",
      "plaintext %r, wanted '' -- the box sits on entry %d of %d, %r"
      % (plaintext(b), b.i, b.count(), b.currentData()))

print("\n4. Multitrack filters, the entry stays")
b = Box(); names = presets_filter(b, PRESETS, True)
check("entry stays on top", nth(names, 0) == vpm.PRESET_NONE,
      "first of %d is %r, wanted %r -- whole list %s"
      % (len(names), nth(names, 0), vpm.PRESET_NONE, names))
check("only multitrack presets", names[1:] == ["Podcast_Multitrack"],
      "after the entry %s, wanted ['Podcast_Multitrack']" % (names[1:],))

print("\n5. The choice survives a rebuild of the list")
b = Box(); presets_filter(b, PRESETS, False)
b.setCurrentIndex(b.findData(vpm.PRESET_NONE))
presets_filter(b, PRESETS, False)      # as after a multitrack switch
check("stays on the entry", b.currentData() == vpm.PRESET_NONE,
      "after the rebuild entry %d of %d, %r, wanted %r"
      % (b.i, b.count(), b.currentData(), vpm.PRESET_NONE))

print("\n5b. The placeholder alone is not a choice")
b = Box(); presets_filter(b, [], False)     # unchecked: placeholder only
check("sits on the placeholder", b.currentData() == vpm.PRESET_NONE,
      "entry %d of %d is %r, wanted %r"
      % (b.i, b.count(), b.currentData(), vpm.PRESET_NONE))
presets_filter(b, PRESETS, False)
check("and still sits on it when the presets arrive",
      plaintext(b) == "",
      "plaintext %r, wanted '' -- the box sits on entry %d of %d, %r"
      % (plaintext(b), b.i, b.count(), b.currentData()))

print("\n6. Back from the project file")
b = Box(); presets_filter(b, PRESETS, False, wanted=vpm.PRESET_NONE)
check("the wish from the project holds", b.currentData() == vpm.PRESET_NONE,
      "the wish was %r, the box sits on %r"
      % (vpm.PRESET_NONE, b.currentData()))
b = Box(); presets_filter(b, PRESETS, False, wanted="Podcast_Zoom")
check("a plain preset name still holds",
        plaintext(b) == "Podcast_Zoom",
        "the wish was %r, plaintext %r, the box sits on %r"
        % ("Podcast_Zoom", plaintext(b), b.currentData()))

print("\n7. The run: without a key nothing goes to auphonic.com")
def argv_with(key, preset):
    values = {"files": [("/tmp/a.mov", "video")], "clip_kinds": {},
              "multitrack": False, "key": key, "preset": preset}
    return vpm.run_argv(values, "")
argv, _plan, messages = argv_with("", "")
check("without a key: no --auphonic-api-key",
        argv is not None and "--auphonic-api-key" not in argv,
        "%s, wanted a command line without it"
        % switches(argv, "--auphonic-api-key"))
check("without a key: no message", not messages,
      "%s, wanted none" % said(messages))
argv, _plan, messages = argv_with("SECRET", "Podcast_Zoom")
check("with key and preset: both there",
        argv is not None and "--auphonic-api-key" in argv
        and "--auphonic-preset" in argv,
        "%s, wanted both there"
        % switches(argv, "--auphonic-api-key", "--auphonic-preset"))
argv, _plan, messages = argv_with("SECRET", "")
check("key without preset: an error message",
        argv is None and messages and messages[0][0] == "error",
        "command line %s, %s, wanted none and the first one an 'error'"
        % ("None" if argv is None else "%d words" % len(argv),
           said(messages)))

print("\n8. The old tick is really gone")
source = open(SCRIPT, encoding="utf-8").read()
check("no QCheckBox 'this time without'",
        "this time without auphonic.com" not in source,
        "'this time without auphonic.com' stands %d times in %s, wanted 0"
        % (source.count("this time without auphonic.com"),
           os.path.basename(SCRIPT)))
check("PRESET_NONE is used in the interface",
        source.count("PRESET_NONE") >= 5,
        "PRESET_NONE stands %d times in %s, wanted at least 5"
        % (source.count("PRESET_NONE"), os.path.basename(SCRIPT)))

print("\n%d checks in %.2f s" % (done, time.time() - began))
print("\n%s" % ("all good" if not error
                else "FAIL: %s" % " | ".join(error)))
sys.exit(1 if error else 0)
