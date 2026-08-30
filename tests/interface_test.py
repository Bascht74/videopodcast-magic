# -*- coding: utf-8 -*-
"""The interface really builds itself -- in both languages.

A stylesheet with a placeholder that no longer exists, or a table that
reads a renamed key, shows up in none of the functional tests. Here the
window is really built.
"""
import os, subprocess, sys, tempfile

# The three window scripts are not part of this suite; they are only
# started here.
HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPTS = [os.path.join(HERE, name) for name in
           ("assignment_shot.py", "preview_shot.py", "preset_shot.py")]
# How long one window may take before it is called hung. The scripts
# carry their own emergency exit at 45 and 60 seconds, so anything past
# a minute is a window that never reached its event loop. The clock
# starts when a window's turn to be read comes, not when it was started.
LIMIT = 120
error = []
checked = 0
skipped = 0


def check(name, ok, extra=""):
    print("  %-46s %s %s" % (name, "ok" if ok else "FAIL", extra))
    if not ok:
        error.append(name)


def readable(what):
    """What a timeout carried with it, as text.

    subprocess.TimeoutExpired keeps whatever had already arrived, and
    keeps it as bytes even where the pipes were opened as text.
    """
    if not what:
        return ""
    if isinstance(what, bytes):
        return what.decode("utf-8", "replace")
    return what


# German is the point of this test: the window has to build in the
# translated language as well, so the language is set here, not by the
# suite. All six windows are started at once and read afterwards,
# because each sits on timers between its steps and they add up.
started = []
# One missing window is the likely case and the one worth hearing
# about, so a script that is not there is named rather than passed over.
present = [s for s in SCRIPTS if os.path.exists(s)]
for s in SCRIPTS:
    if s not in present:
        print("  %-46s is not next to this test -- not checked"
              % os.path.basename(s))
for language in ("de_DE.UTF-8", "en_US.UTF-8"):
    # LANGUAGE too: the suite sets LANGUAGE=en and the program reads
    # that name before LANG, so without it this test runs English twice.
    # PYTHONUNBUFFERED because of the kill further down: a window that
    # hangs never flushes its pipe, and its own trace dies with it.
    env = dict(os.environ, LANG=language, LC_ALL=language,
               LANGUAGE=language, QT_QPA_PLATFORM="offscreen",
               PYTHONUNBUFFERED="1")
    if language != "en_US.UTF-8":
        # The window scripts save their pictures under fixed names and
        # would write the same file in the same moment, so every
        # language but the last gets a folder of its own and
        # tests/shots/ keeps the English windows.
        env["VPM_SHOTS"] = tempfile.mkdtemp(prefix="vpm_shots_")
    row = []
    for s in present:
        # A runtime folder of its own for every window: six Qt processes
        # start here at the same moment, and Qt puts lock files and
        # shared memory under the one folder they would otherwise share.
        # The line the retry prints below says whether it helped.
        alone = tempfile.mkdtemp(prefix="vpm_runtime_")
        os.chmod(alone, 0o700)
        mine = dict(env, XDG_RUNTIME_DIR=alone)
        row.append((s, subprocess.Popen(
            [sys.executable, s], stdout=subprocess.PIPE,
            stderr=subprocess.PIPE, text=True, env=mine, cwd=HERE)))
    started.append((language, row, env))

for language, row, env in started:
    print("\nLanguage %s" % language)
    for s, p in row:
        hung = ""
        try:
            out, err = p.communicate(timeout=LIMIT)
        except subprocess.TimeoutExpired as ran_on:
            # A window that never comes up must not hold the suite, and
            # it must not pass either. What it printed before it got
            # stuck is the only trace there is, so it is read here and
            # judged below like any other run.
            p.kill()
            try:
                # Reading after the kill can hang in turn: a surviving
                # ffmpeg grandchild holds the same pipe open, so the
                # end of the output never comes.
                out, err = p.communicate(timeout=10)
                hung = "still running after %d s" % LIMIT
            except subprocess.TimeoutExpired as still_open:
                # Both timeouts carry what had already arrived.
                out = readable(still_open.stdout) or readable(ran_on.stdout)
                err = readable(still_open.stderr) or readable(ran_on.stderr)
                hung = ("still running after %d s, and the pipe stayed "
                        "open -- a child of it is still alive" % LIMIT)
        out = (out or "") + (err or "")
        if not hung and "SKIPPED:" in out:
            # A window that stops for want of material has not been
            # checked, so it must not count as a pass.
            print("  %-46s skipped %s"
                  % (os.path.basename(s),
                     out.split("SKIPPED:")[1].split("\n")[0][:44]))
            skipped += 1
            continue
        # What the run said about itself. A script's own FAIL line counts
        # for as much as a traceback: a window that named what it could
        # not find has not failed silently, so it is neither run again
        # below nor allowed through on a return code of nought.
        serious = [line for line in out.split("\n")
                   if line.startswith("FAIL") or "Traceback" in line
                   or "KeyError" in line or "AttributeError" in line
                   or "NameError" in line]
        good = not hung and p.returncode == 0 and not serious
        if not good and not hung and not serious:
            # A failure that says nothing is not a finding: on a busy
            # two-core builder a window comes back with a return code
            # and no trace of any kind. So it is run once more, alone,
            # and only a second silent failure counts.
            again = subprocess.run(
                [sys.executable, s], stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT, text=True, env=env, cwd=HERE)
            if again.returncode == 0:
                print("  %-46s ok on its own, after failing silently "
                      "beside five other windows"
                      % os.path.basename(s))
                good = True
            else:
                out = (out or "") + "\n--- and again, alone: ---\n" \
                    + (again.stdout or "")
        checked += 1
        # Why it is red, in the same line: the reason it hung or the
        # return code, so a signal and an error do not read alike.
        note = ""
        if not good:
            note = hung or "return code %s" % p.returncode
            if serious:
                note += " -- " + serious[0][:60]
            else:
                # Where it stopped, in this line and not only in the
                # block below it: a builder's log keeps the lines that
                # say FAIL and drops the rest. Qt's offscreen grumbling
                # stands after the script's last word, so it is dropped.
                said = [x.strip() for x in out.rstrip().split("\n")
                        if x.strip() and "This plugin does not" not in x
                        and not x.startswith("qt.")]
                if said:
                    note += " -- last words: " + " | ".join(
                        w[:45] for w in said[-3:])
        check("%s runs through" % os.path.basename(s), good, note[:160])
        if not good:
            # The one line above says a window did not build, not why,
            # and a rare failure without its traceback cannot be chased.
            print("    --- what %s printed ---" % os.path.basename(s))
            tail = out.rstrip().split("\n")[-25:]
            if not any(line.strip() for line in tail):
                # An empty block under this heading is a finding of its
                # own, not a printing that went wrong.
                print("    (nothing -- it printed not one line)")
            for line in tail:
                print("    " + line[:150])

print()
if error:
    print("FAIL: " + ", ".join(error))
    sys.exit(1)
if not checked:
    # Nothing was really tried, so "All good." would be a lie: the suite
    # reads this word and counts the test as skipped rather than green.
    print("SKIPPED: not one window was checked -- %d skipped, %d of %d "
          "scripts missing" % (skipped, len(SCRIPTS) - len(present),
                               len(SCRIPTS)))
    sys.exit(0)
if skipped:
    print("%d window(s) checked, %d skipped." % (checked, skipped))
print("All good.")
