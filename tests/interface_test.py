# -*- coding: utf-8 -*-
"""The interface really builds itself -- in both languages.

A stylesheet with a placeholder that no longer exists, or a table that
reads a renamed key, shows up in none of the functional tests. Here the
window is really built.
"""
import os, subprocess, sys, tempfile

# The three window scripts are not part of this suite; they were renamed
# along with it and are only started here.
HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPTS = [os.path.join(HERE, name) for name in
           ("assignment_shot.py", "preview_shot.py", "preset_shot.py")]
error = []


def check(name, ok, extra=""):
    print("  %-46s %s %s" % (name, "ok" if ok else "FAIL", extra))
    if not ok:
        error.append(name)


# German is the point of this test: the window has to build in the
# translated language as well, so the language is set here, not by the
# suite.
#
# All six windows are started at once and read afterwards. Almost none
# of the time here is work: a window script sits on its own timers
# between steps -- 1.8 and 2.5 seconds -- so that the measurement behind
# the interface has room. Started one after the other that came to 54
# seconds with the processor idle; started together it takes as long as
# the slowest single window. Every window is still its own process with
# its own language, and is judged by exactly the same lines below.
started = []
for language in ("de_DE.UTF-8", "en_US.UTF-8"):
    # LANGUAGE too: the suite sets LANGUAGE=en, and the program reads
    # that name before LANG. Without it this test would run English
    # twice and prove nothing about the German window.
    env = dict(os.environ, LANG=language, LC_ALL=language,
               LANGUAGE=language, QT_QPA_PLATFORM="offscreen")
    if language != "en_US.UTF-8":
        # The window scripts save their pictures under fixed names. One
        # after the other the last language won, and that was English;
        # side by side they would write the same file in the same
        # moment. So every language but the last gets a folder of its
        # own, and what stays in tests/shots/ is what stayed there
        # before: the English windows.
        env["VPM_SHOTS"] = tempfile.mkdtemp(prefix="vpm_shots_")
    row = []
    for s in SCRIPTS:
        if not os.path.exists(s):
            continue
        row.append((s, subprocess.Popen(
            [sys.executable, s], stdout=subprocess.PIPE,
            stderr=subprocess.PIPE, text=True, env=env, cwd=HERE)))
    started.append((language, row))

for language, row in started:
    print("\nLanguage %s" % language)
    for s, p in row:
        try:
            out, err = p.communicate(timeout=600)
        except subprocess.TimeoutExpired:
            # A window that never comes up must not hold the suite; and
            # it must not pass either, so the error goes on standing.
            p.kill()
            p.communicate()
            raise
        out = (out or "") + (err or "")
        if "SKIPPED:" in out:
            # A window script that stops for want of material has not been
            # checked. Say so rather than counting it as a pass.
            print("  %-46s skipped %s"
                  % (os.path.basename(s),
                     out.split("SKIPPED:")[1].split("\n")[0][:44]))
            continue
        serious = [line for line in out.split("\n")
                   if "Traceback" in line or "KeyError" in line
                   or "AttributeError" in line or "NameError" in line]
        good = p.returncode == 0 and not serious
        check("%s runs through" % os.path.basename(s), good,
              (serious[:1] or [""])[0][:70])
        if not good:
            # The one line above says a window did not build; it does
            # not say why. Under load this happens rarely, and a rare
            # failure without its traceback cannot be chased at all.
            print("    --- what %s printed ---" % os.path.basename(s))
            for line in out.rstrip().split("\n")[-25:]:
                print("    " + line[:150])

if not any(os.path.exists(s) for s in SCRIPTS):
    print("  no window script found next to this test -- nothing checked.")

print()
if error:
    print("FAIL: " + ", ".join(error))
    sys.exit(1)
print("All good.")
