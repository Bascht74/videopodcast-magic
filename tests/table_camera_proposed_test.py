"""The suggestion finds the speaker's camera, and never freezes it.

Three sections, in the order the program asks the questions. "The name
alone" is the fuzzy match between a speaker's name and a camera file.
"The suggestion above it" is what the row is preselected to once a
hand-set camera, the camera the sound came out of and the name have all
had their say. "What is written back" is the rule that decides which of
those answers goes into the project -- only a real override does, so a
name changed afterwards still moves the camera.

The names here are made up; no file is opened. What that cannot show is
whether the window really asks these three in this order.
"""
import os
HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = os.environ.get("VPM_SCRIPT") or os.path.join(
    os.path.dirname(HERE), "videopodcast-magic.py")
import importlib.util, sys, time
spec = importlib.util.spec_from_file_location("vpm", SCRIPT)
m = importlib.util.module_from_spec(spec); sys.modules["vpm"] = m
spec.loader.exec_module(m)

began = time.time()
done = 0
bad = []


def check(name, ok, extra=""):
    global done
    done += 1
    print("  %-58s %s %s" % (name, "ok" if ok else "FAIL", extra))
    if not ok:
        bad.append("%s [%s]" % (name, extra or "no numbers"))


CAMERAS = ["/x/Colourchart.mov", "/x/Colourchart2.mov", "/x/Jingle.mp4",
           "/x/Guset_01011714_C003.mov",
           "/x/Hosts_01011714_C002.mov",
           "/x/Wide_01011714_C007.mov"]
PICKABLE = [os.path.basename(p) for p in CAMERAS]
GUEST, HOST = "Guset_01011714_C003.mov", "Hosts_01011714_C002.mov"

print("1. The name alone")


def finds(speaker):
    """The camera this speaker's name picks out, by its bare name."""
    hit = m.camera_for_speaker(speaker, CAMERAS)
    return os.path.basename(hit) if hit else None


# Written out one by one rather than looped: the register that holds the
# counter-proofs reads the first argument of every check out of the
# source, and a name put together while the test runs stands there as an
# expression and not as a sentence.
check("a name spelt right finds the camera whose name is not",
      finds("Guest") == GUEST, "found %s, wanted %s" % (finds("Guest"), GUEST))
check("the host's name finds the host camera",
      finds("Host") == HOST, "found %s, wanted %s" % (finds("Host"), HOST))
# Not "Co-host": that scores 0.67 against "Hosts" and would turn this
# fuzzy-match case into a no-match case.
check("a name close but not equal still finds its camera",
      finds("Cohosts") == HOST,
      "found %s, wanted %s" % (finds("Cohosts"), HOST))
check("a mix belongs to no camera",
      finds("Full-Mix") is None, "found %s, wanted None" % finds("Full-Mix"))
check("a name matching the wide shot finds the wide shot",
      finds("Wide") == "Wide_01011714_C007.mov",
      "found %s, wanted Wide_01011714_C007.mov" % finds("Wide"))
check("an empty name finds nothing",
      finds("") is None, "found %s, wanted None" % finds(""))
check("a name like no camera finds nothing",
      finds("Xy") is None, "found %s, wanted None" % finds("Xy"))

print("\n2. The suggestion above it")
check("a row nobody has named yet stays on the mix",
      m.preselected_camera(None, PICKABLE, "", CAMERAS) == m.MIX_ONLY,
      "suggested %s, wanted %s"
      % (m.preselected_camera(None, PICKABLE, "", CAMERAS), m.MIX_ONLY))
check("the camera the sound came out of is suggested before the name",
      m.preselected_camera(None, PICKABLE, "Host", CAMERAS,
                           own_camera=GUEST) == GUEST,
      "suggested %s, wanted %s"
      % (m.preselected_camera(None, PICKABLE, "Host", CAMERAS,
                              own_camera=GUEST), GUEST))
check("a camera set by hand survives the next rebuild",
      m.preselected_camera(HOST, PICKABLE, "Guest", CAMERAS) == HOST,
      "suggested %s, wanted %s"
      % (m.preselected_camera(HOST, PICKABLE, "Guest", CAMERAS), HOST))
check("a camera that is gone does not hold the row",
      m.preselected_camera("Deleted.mov", PICKABLE, "Guest",
                           CAMERAS) == GUEST,
      "suggested %s, wanted %s"
      % (m.preselected_camera("Deleted.mov", PICKABLE, "Guest", CAMERAS),
         GUEST))

print("\n3. What is written back into the project")
# The rule the channels already follow one level down: only a real
# override is kept. Without it the program's own first guess is stored
# as if somebody had chosen it, and from then on it wins over every
# fresh derivation -- so the last check here is the one that bites.
keep = getattr(m, "camera_to_remember", None)
check("the rule about what is kept is a function of its own",
      keep is not None,
      "vpm.camera_to_remember %s" % ("is there" if keep else "is missing"))
guessed = keep(HOST, HOST) if keep else "(no such function)"
check("a camera the program worked out itself is not kept",
      guessed is None, "kept %s, wanted None" % (guessed,))
chosen = keep(GUEST, HOST) if keep else "(no such function)"
check("a camera chosen against the suggestion is kept",
      chosen == GUEST, "kept %s, wanted %s" % (chosen, GUEST))
nothing = keep(GUEST, None) if keep else "(no such function)"
check("with nothing worked out, what stands is kept",
      nothing == GUEST, "kept %s, wanted %s" % (nothing, GUEST))
# The whole story in one line: guess, write back, rename, ask again.
first = m.preselected_camera(None, PICKABLE, "Guest", CAMERAS)
stored = keep(first, first) if keep else first
again = m.preselected_camera(stored, PICKABLE, "Host", CAMERAS)
check("a name changed after the first guess moves the camera with it",
      again == HOST,
      "first %s, kept %s, then %s, wanted %s"
      % (first, stored, again, HOST))

print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
