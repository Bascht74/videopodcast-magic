# -*- coding: utf-8 -*-
"""--store-auphonic-key asks unseen, stores, and says whether the key holds.

The one way to the key without the window. Sections: a key typed in
is asked for through the unseen prompt, stored with its edges trimmed,
said to hold, and printed nowhere; a store that does not hold is said
with its reason; nothing typed stores nothing; and a word after the
switch -- the key on a command line -- is refused before anything is
asked. main() runs in this process; the prompt and the store are
stand-ins, so no keychain and no registry is reached.
"""
PLATFORM_BOUND = True
import os
import sys
# tests/, where the helpers and state/ lie; this file may stand in a
# folder under it, or in one under that.
HERE = os.path.dirname(os.path.abspath(__file__))
while not os.path.isfile(os.path.join(HERE, "the_program.py")) \
        and os.path.dirname(HERE) != HERE:
    HERE = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import contextlib
import getpass
import io
import time
import the_program

os.environ["VPM_NO_UPDATE_CHECK"] = "1"
vpm = the_program.load()
vpm.set_language("en")

began = time.time()
done = 0
bad = []


def check(name, ok, extra=""):
    global done
    done += 1
    print("  %-58s %s %s" % (name, "ok" if ok else "FAIL", extra))
    if not ok:
        bad.append("%s [%s]" % (name, extra or "no numbers"))


# Invented, and the only key this file knows.
KEY = "FAKEKEY-0000"

# ------------------------------------------------ the prompt and the store
# Both replaced: the typed line comes from here, and what the store is
# handed is written down. Nothing outside this process is touched.
typed = [""]
prompts = []
stored = []
holds = [True]


def prompt_stand_in(prompt="Password: ", stream=None):
    prompts.append(prompt)
    return typed[0]


def store_stand_in(key):
    stored.append(key)
    return holds[0]


getpass.getpass = prompt_stand_in
vpm.store_api_key = store_stand_in
vpm.load_api_key = lambda: ""


def switch(*words):
    """main() on --store-auphonic-key and words: (code, what it printed)."""
    del prompts[:], stored[:]
    sys.argv = ["videopodcast-magic", "--store-auphonic-key"] + list(words)
    out = io.StringIO()
    kept_stdin = sys.stdin
    sys.stdin = io.StringIO("")      # nobody at a keyboard behind it
    try:
        with contextlib.redirect_stdout(out):
            code = vpm.main()
    except SystemExit as e:
        code = e.code
    finally:
        sys.stdin = kept_stdin
    return code, out.getvalue()


print("1. A key typed in")
typed[0] = "  " + KEY + "  \n"
code, said = switch()
check("the key is asked for through the unseen prompt",
      len(prompts) == 1,
      "the unseen prompt was asked %d times, wanted 1" % len(prompts))
check("what was typed reaches the store, blanks at the edges off",
      stored == [KEY],
      "the store was handed %d value(s) of %s characters, wanted one of %d"
      % (len(stored), [len(x) for x in stored], len(KEY)))
check("a key that holds ends the switch with 0", code == 0,
      "returned %r" % (code,))
check("and it says the key is stored and read back",
      vpm.T('The key is stored, and reading it back gave the same key.')
      in said, "printed %d lines: %r" % (len(said.splitlines()),
                                        said.replace(KEY, "<key>")[:200]))
check("the key stands in no line it printed and in no prompt",
      KEY not in said and not any(KEY in p for p in prompts),
      "%d printed line(s) and %d prompt(s) carry it"
      % (len([x for x in said.splitlines() if KEY in x]),
         len([p for p in prompts if KEY in p])))

print("\n2. A store that does not hold")
holds[0] = False
code, said = switch()
holds[0] = True
check("a key the store does not hold ends the switch with 1", code == 1,
      "returned %r" % (code,))
reason = vpm.T('The key is not stored: %s') % vpm.key_store_trouble()
check("and it says the key is not stored, with the reason",
      reason in said, "printed %r" % said.replace(KEY, "<key>")[:200])

print("\n3. Nothing typed")
typed[0] = "   \n"
code, said = switch()
check("nothing typed hands the store nothing", not stored and code == 1,
      "the store was handed %d value(s), returned %r" % (len(stored), code))
check("and it says nothing was stored",
      vpm.T('No key was typed, so nothing was stored.') in said,
      "printed %r" % said[:200])

print("\n4. A word after the switch")
typed[0] = KEY
code, said = switch(KEY)
check("a word after the switch is refused before anything is asked",
      code == 2 and not prompts and not stored,
      "returned %r, prompt asked %d times, store handed %d value(s)"
      % (code, len(prompts), len(stored)))
check("and the refusal does not repeat the word",
      KEY not in said and said.strip() != "",
      "%d characters printed, the word %s among them"
      % (len(said), "is" if KEY in said else "is not"))

print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
