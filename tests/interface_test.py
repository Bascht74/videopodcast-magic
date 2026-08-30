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
# How long one window may take before it is called hung. Measured on an
# idle machine: 3.5, 3.7 and 6.0 seconds one at a time, and 6.0 seconds
# for all six side by side. The scripts carry their own emergency exit
# at 45 and 60 seconds, so anything past a minute is a window that never
# reached its event loop at all. 120 gives the slowest of them twice its
# own deadline and still says something inside two minutes; 600 meant
# ten minutes of silence before the first word.
#
# The clock starts when a window's turn to be read comes, not when it
# was started, so the ones waiting their turn are not charged for the
# wait.
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
    keeps it as bytes even where the pipes were opened as text. It is
    the last resort here: what the window said before it stopped saying
    anything.
    """
    if not what:
        return ""
    if isinstance(what, bytes):
        return what.decode("utf-8", "replace")
    return what


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
# A script that is not there was passed over without a word, and only a
# run in which all three were missing said anything at all. One missing
# window is the more likely case and the one worth hearing about.
present = [s for s in SCRIPTS if os.path.exists(s)]
for s in SCRIPTS:
    if s not in present:
        print("  %-46s is not next to this test -- not checked"
              % os.path.basename(s))
for language in ("de_DE.UTF-8", "en_US.UTF-8"):
    # LANGUAGE too: the suite sets LANGUAGE=en, and the program reads
    # that name before LANG. Without it this test would run English
    # twice and prove nothing about the German window.
    # PYTHONUNBUFFERED, because of the kill further down: a window
    # script writes into a pipe, so Python collects its lines in a
    # buffer of some kilobytes and only hands them over at the end. A
    # window that hangs never reaches that end, and the kill takes the
    # buffer with it -- what was left over then was ffmpeg's chatter,
    # which writes unbuffered, and not one line of the script's own
    # trace. Measured with the limit at one second: without this the
    # last step it reported was gone, with it it stands there.
    env = dict(os.environ, LANG=language, LC_ALL=language,
               LANGUAGE=language, QT_QPA_PLATFORM="offscreen",
               PYTHONUNBUFFERED="1")
    if language != "en_US.UTF-8":
        # The window scripts save their pictures under fixed names. One
        # after the other the last language won, and that was English;
        # side by side they would write the same file in the same
        # moment. So every language but the last gets a folder of its
        # own, and what stays in tests/shots/ is what stayed there
        # before: the English windows.
        env["VPM_SHOTS"] = tempfile.mkdtemp(prefix="vpm_shots_")
    row = []
    for s in present:
        row.append((s, subprocess.Popen(
            [sys.executable, s], stdout=subprocess.PIPE,
            stderr=subprocess.PIPE, text=True, env=env, cwd=HERE)))
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
            #
            # It used to be killed, read, the reading thrown away, and
            # the exception let through -- which ended the test on the
            # spot without one line about the window that hung, and
            # took the windows after it with it. In the CI that was
            # "RED (rc=1)" and nothing else.
            p.kill()
            try:
                # Reading after the kill can hang in turn: the program
                # starts ffmpeg, and a surviving grandchild holds the
                # same pipe open, so the end of the output never comes.
                # Ten seconds for what is already in the pipe, then on
                # with what there is.
                out, err = p.communicate(timeout=10)
                hung = "still running after %d s" % LIMIT
            except subprocess.TimeoutExpired as still_open:
                # Even here what came in is not lost: both timeouts
                # carry it with them.
                out = readable(still_open.stdout) or readable(ran_on.stdout)
                err = readable(still_open.stderr) or readable(ran_on.stderr)
                hung = ("still running after %d s, and the pipe stayed "
                        "open -- a child of it is still alive" % LIMIT)
        out = (out or "") + (err or "")
        if not hung and "SKIPPED:" in out:
            # A window script that stops for want of material has not been
            # checked. Say so rather than counting it as a pass.
            print("  %-46s skipped %s"
                  % (os.path.basename(s),
                     out.split("SKIPPED:")[1].split("\n")[0][:44]))
            skipped += 1
            continue
        serious = [line for line in out.split("\n")
                   if "Traceback" in line or "KeyError" in line
                   or "AttributeError" in line or "NameError" in line]
        good = not hung and p.returncode == 0 and not serious
        if not good and not hung and not serious:
            # A failure that says nothing is not a finding. Six windows
            # start here at once -- three scripts in two languages --
            # and on the two-core Linux builder one of them comes back
            # with a return code and no traceback, no FAIL of its own
            # and no line about a step it missed. Measured 31.8.2026:
            # green, red, green, red on the same commit twice over.
            # So it is run once more, alone, and only a second silent
            # failure counts. Where it says anything at all -- a
            # traceback, its own FAIL, a hang -- nothing is repeated.
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
        # Why it is red, in the same line: the reason it hung, or the
        # return code. The code used to be left out, so a window killed
        # by a signal and one that ended with an error read alike.
        note = ""
        if not good:
            note = hung or "return code %s" % p.returncode
            if serious:
                note += " -- " + serious[0][:60]
            else:
                # Where it stopped, in this line and not only in the
                # block below it: a builder's log keeps the lines that
                # say FAIL and drops the rest, so "return code 1" was
                # all that ever came back from the one machine that
                # could say more. Measured 29.8.2026, twice.
                # Qt's own grumbling is not the script's last word. It
                # comes out of the offscreen platform and stands after
                # everything the script said, so taking the last line
                # literally gave "This plugin does not support raise()"
                # and nothing else -- measured 29.8.2026 on the builder.
                said = [x.strip() for x in out.rstrip().split("\n")
                        if x.strip() and "This plugin does not" not in x
                        and not x.startswith("qt.")]
                if said:
                    note += " -- last words: " + " | ".join(
                        w[:45] for w in said[-3:])
        check("%s runs through" % os.path.basename(s), good, note[:160])
        if not good:
            # The one line above says a window did not build; it does
            # not say why. Under load this happens rarely, and a rare
            # failure without its traceback cannot be chased at all.
            print("    --- what %s printed ---" % os.path.basename(s))
            tail = out.rstrip().split("\n")[-25:]
            if not any(line.strip() for line in tail):
                # An empty block under this heading looks like the
                # printing went wrong. It is a finding of its own.
                print("    (nothing -- it printed not one line)")
            for line in tail:
                print("    " + line[:150])

print()
if error:
    print("FAIL: " + ", ".join(error))
    sys.exit(1)
if not checked:
    # Nothing was really tried, so "All good." would be a lie. The suite
    # reads a line beginning with this word and counts the test as
    # skipped instead of green.
    print("SKIPPED: not one window was checked -- %d skipped, %d of %d "
          "scripts missing" % (skipped, len(SCRIPTS) - len(present),
                               len(SCRIPTS)))
    sys.exit(0)
if skipped:
    print("%d window(s) checked, %d skipped." % (checked, skipped))
print("All good.")
