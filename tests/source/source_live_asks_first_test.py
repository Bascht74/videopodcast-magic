# -*- coding: utf-8 -*-
"""The live tests reach nothing outside until the word that starts them.

Sections: the suite knows no test under a live/ folder; auphonic.sh
without its word sends nothing and says the word; with --online alone,
against a stand-in curl, it starts no production and the key it was
given stands in no line and no argument; a run here names the Auphonic
tests and how to start them; resolve.sh without --go starts nothing and
says the word; and every file under resolve/live/ started directly stops
with the word and loads neither the program nor the Resolve module, as a
watch put into every child records. auphonic.com is never spoken to:
curl is a stand-in, a proxy that answers nothing stands behind it, and
the Resolve interface is pointed at a folder that is not there.
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
import json
import shutil
import subprocess
import tempfile
import time

RUN = os.path.join(HERE, "run.sh")
STARTER = os.path.join(HERE, "auphonic.sh")
LIVE = os.path.join(HERE, "auphonic", "live")
sys.path.insert(0, LIVE)
import auphonic_ground

RESOLVE_STARTER = os.path.join(HERE, "resolve.sh")
RESOLVE_LIVE = os.path.join(HERE, "resolve", "live")
# What a person types, written out here and not read from the ground:
# a line that only repeated the ground's own constant could not fall.
RESOLVE_WORD = "bash resolve.sh --go"
# The modules a child that could reach Resolve has to load first -- the
# program, and the scripting module the program connects through.
WATCHED = ("the_program", "videopodcast_magic", "DaVinciResolveScript",
           "fusionscript")

KEY = "FAKEKEY-0000"
# A suite of one comes back in well under a second here and the builder
# is some nine times slower; the bound is for a run that hangs.
WAIT = 600
# The test run.sh is started on for its closing lines -- the one
# source_resolve_recalled names, for the same reasons.
NAMED = "cut_rules_hold"

began = time.time()
done = 0
bad = []


def check(name, ok, extra=""):
    global done
    done += 1
    print("  %-58s %s %s" % (name, "ok" if ok else "FAIL", extra))
    if not ok:
        bad.append("%s [%s]" % (name, extra or "no numbers"))


# The words run.sh judges a whole run by, anywhere in a line. What
# another run printed is quoted here, so it goes through this first.
LOUD = ("FAIL", "Traceback", "SKIPPED", "LEFT OUT", "Left out",
        "Error", "error", "Exception", "Interrupt")


def quiet(text):
    """Text out of another run, safe to print in a line of ours."""
    text = " ".join(str(text).split())
    for word in LOUD:
        text = text.replace(word, word[:2] + "-" + word[2:])
    return text


D = tempfile.mkdtemp(prefix="liveasks_")
LOG = os.path.join(D, "curl.log")
BIN = os.path.join(D, "bin")
os.makedirs(BIN)
# The stand-in lies beside the live tests, and goes onto PATH here under
# curl's name with this interpreter in its first line.
with open(os.path.join(LIVE, "curl_standin.py"), encoding="utf-8") as f:
    body = f.read()
with open(os.path.join(BIN, "curl"), "w", encoding="utf-8") as f:
    f.write("#!%s\n" % sys.executable + body)
os.chmod(os.path.join(BIN, "curl"), 0o755)


def fenced():
    """The environment for a child: stand-in curl first, a dead proxy."""
    env = dict(os.environ)
    for name in (auphonic_ground.ONLINE, auphonic_ground.CREDIT, "CI",
                 "GITHUB_ACTIONS", "VPM_LIVE_PRESET", "VPM_LIVE_RESOLVE"):
        env.pop(name, None)
    env["PATH"] = BIN + os.pathsep + env.get("PATH", "")
    env["AUPHONIC_TOKEN"] = KEY
    env["VPM_STANDIN_LOG"] = LOG
    env["VPM_STANDIN_WATCH"] = KEY
    env["VPM_STANDIN_REFUSED"] = auphonic_ground.REFUSED_KEY
    for proxy in ("https_proxy", "HTTPS_PROXY", "http_proxy", "HTTP_PROXY",
                  "ALL_PROXY", "all_proxy"):
        env[proxy] = "http://127.0.0.1:9"
    env.pop("NO_PROXY", None)
    env.pop("no_proxy", None)
    # And Resolve bolted out: were run.sh ever to take a test under
    # resolve/live/, it would find no interface and leave itself out.
    env["RESOLVE_SCRIPT_API"] = os.path.join(D, "no-resolve")
    env["RESOLVE_SCRIPT_LIB"] = os.path.join(D, "no-resolve", "none.so")
    return env


def started(*args):
    """(return code, lines) of a child, or (None, [why])."""
    try:
        ran = subprocess.run(["bash"] + list(args), cwd=HERE, env=fenced(),
                             stdout=subprocess.PIPE,
                             stderr=subprocess.STDOUT, timeout=WAIT)
    except (OSError, subprocess.TimeoutExpired) as e:
        return None, [type(e).__name__]
    return ran.returncode, ran.stdout.decode("utf-8", "replace").splitlines()


# The watch: a sitecustomize first on PYTHONPATH, so every Python a
# child starts writes down each watched module it loads, before anything
# of the child's own runs. A connection has to load one of them first.
HOOK = os.path.join(D, "hook")
WATCH_LOG = os.path.join(D, "watch.log")
os.makedirs(HOOK)
with open(os.path.join(HOOK, "sitecustomize.py"), "w", encoding="utf-8") as f:
    f.write("import os, sys\n"
            "def heard(event, args):\n"
            "    if event == 'import' and args and \\\n"
            "            str(args[0]).split('.')[0] in %r:\n"
            "        with open(%r, 'a') as log:\n"
            "            log.write('%%s\\n' %% args[0])\n"
            "sys.addaudithook(heard)\n" % (WATCHED, WATCH_LOG))
FIXTURES = os.path.join(D, "fixtures")


def watched():
    """The environment for a Resolve child: fenced, and watched."""
    env = fenced()
    env["PYTHONPATH"] = HOOK + os.pathsep + env.get("PYTHONPATH", "")
    env["VPM_FIXTURES"] = FIXTURES
    return env


def loaded():
    """What the watched children loaded since the last look, and forget it."""
    if not os.path.isfile(WATCH_LOG):
        return []
    with open(WATCH_LOG, encoding="utf-8") as f:
        seen = sorted(set(line.strip() for line in f if line.strip()))
    os.remove(WATCH_LOG)
    return seen


def run_watched(argv):
    """(return code, lines) of a watched child, or (None, [why])."""
    try:
        ran = subprocess.run(argv, cwd=HERE, env=watched(),
                             stdout=subprocess.PIPE,
                             stderr=subprocess.STDOUT, timeout=WAIT)
    except (OSError, subprocess.TimeoutExpired) as e:
        return None, [type(e).__name__]
    return ran.returncode, ran.stdout.decode("utf-8", "replace").splitlines()


def calls():
    """What the stand-in curl was handed, one entry per call."""
    if not os.path.isfile(LOG):
        return []
    with open(LOG, encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


try:
    # -------------------------------------------------------------- 1.
    print("1. The suite knows no test under a live/ folder")
    live = sorted(name[:-len("_test.py")]
                  for top in os.listdir(HERE)
                  if os.path.isdir(os.path.join(HERE, top, "live"))
                  for name in os.listdir(os.path.join(HERE, top, "live"))
                  if name.endswith("_test.py"))
    check("there are live tests to ask the suite about",
          any(n.startswith("auphonic_") for n in live),
          "%d found: %s" % (len(live), quiet(", ".join(live)) or "none"))
    taken = []
    for name in live:
        rc, lines = started(RUN, name)
        if rc != 2 or not any("no test named" in one for one in lines):
            taken.append("%s (rc=%s)" % (name, rc))
    check("run.sh takes no test that lies under a live/ folder",
          not taken, "%d of %d taken: %s"
          % (len(taken), len(live), quiet(", ".join(taken)) or "none"))

    # -------------------------------------------------------------- 2.
    print("\n2. auphonic.sh without its word")
    rc, lines = started(STARTER)
    check("auphonic.sh without --online sends nothing and stops",
          rc not in (0, None) and not calls(),
          "rc=%s, %d calls reached curl" % (rc, len(calls())))
    check("and it says the word that starts it",
          any("--online" in one for one in lines),
          "--online in %d of %d lines" % (
              len([one for one in lines if "--online" in one]), len(lines)))

    # -------------------------------------------------------------- 3.
    print("\n3. auphonic.sh --online, against a stand-in curl")
    rc, lines = started(STARTER, "--online")
    seen = calls()
    check("the stand-in answered in place of curl", bool(seen),
          "%d calls, rc=%s, last line %s"
          % (len(seen), rc, quiet(lines[-1] if lines else "none")))
    made = [a for c in seen if "POST" in c["args"]
            for a in c["args"] if "productions.json" in a]
    check("--online alone starts no production", not made,
          "%d of %d calls create one: %s"
          % (len(made), len(seen), quiet(", ".join(made[:2])) or "none"))
    spenders = sorted(
        name[:-len("_test.py")] for name in os.listdir(LIVE)
        if name.endswith("_test.py")
        and "gate(spends=True)" in open(os.path.join(LIVE, name),
                                        encoding="utf-8").read())
    stayed = [n for n in spenders
              if "--- %s left itself out" % n not in "\n".join(lines)]
    check("every test that spends credit leaves itself out",
          bool(spenders) and not stayed,
          "%d of %d ran: %s" % (len(stayed), len(spenders),
                                quiet(", ".join(stayed)) or "none"))
    summary = [one for one in lines if one.startswith("green:")]
    check("the free tests are green against the stand-in",
          len(summary) == 1 and " red: 0 " in summary[0] + " ",
          quiet(summary[0] if summary else "no summary line"))

    print("\n4. The key it was given")
    check("the key reached curl in its own file",
          any(c["key_in_config"] for c in seen),
          "%d of %d calls had it in the file"
          % (len([c for c in seen if c["key_in_config"]]), len(seen)))
    in_args = [c["args"] for c in seen if any(KEY in a for a in c["args"])]
    check("the key stands in no argument curl was handed", not in_args,
          "%d of %d calls carry it" % (len(in_args), len(seen)))
    in_lines = [one for one in lines if KEY in one]
    check("the key stands in no line the run printed", not in_lines,
          "%d of %d lines carry it" % (len(in_lines), len(lines)))

    # -------------------------------------------------------------- 5.
    print("\n5. What a run here says about them")
    rc, lines = started(RUN, NAMED)
    at = [i for i, one in enumerate(lines) if one.startswith("auphonic:")]
    after = lines[at[0]:] if at else []
    check("a run here names the Auphonic tests and how to start them",
          len(at) == 1 and any("bash auphonic.sh" in one for one in after),
          "%d lines open with auphonic: in the %d the run printed; "
          "'bash auphonic.sh' in %d after it"
          % (len(at), len(lines),
             len([one for one in after if "bash auphonic.sh" in one])))

    # -------------------------------------------------------------- 6.
    print("\n6. resolve.sh without its word")
    loaded()
    rc, lines = run_watched(["bash", RESOLVE_STARTER])
    took = loaded()
    check("resolve.sh without --go starts nothing and stops",
          rc not in (0, None) and not took and not os.path.exists(FIXTURES),
          "rc=%s, %d modules loaded: %s; fixtures %s"
          % (rc, len(took), quiet(", ".join(took[:3])) or "none",
             "made" if os.path.exists(FIXTURES) else "not made"))
    check("and it says the word that starts Resolve's tests",
          any(RESOLVE_WORD in one for one in lines),
          "%r in %d of %d lines" % (RESOLVE_WORD, len(
              [one for one in lines if RESOLVE_WORD in one]), len(lines)))

    # -------------------------------------------------------------- 7.
    print("\n7. A file under resolve/live/ started directly")
    rc, lines = run_watched([sys.executable, "-c", "import the_program"])
    took = loaded()
    check("the watch sees the program when a child loads it",
          rc == 0 and "the_program" in took,
          "rc=%s, loaded: %s" % (rc, quiet(", ".join(took)) or "nothing"))
    started_here = sorted(name for name in os.listdir(RESOLVE_LIVE)
                          if name.endswith("_test.py") or name == "sweep.py")
    check("there are Resolve live tests and a sweep to start",
          "sweep.py" in started_here and len(started_here) > 1,
          "%d found: %s" % (len(started_here),
                            quiet(", ".join(started_here)) or "none"))
    zero, mute, loading = [], [], []
    for name in started_here:
        argv = [sys.executable, os.path.join(RESOLVE_LIVE, name)]
        rc, lines = run_watched(argv + (["--which"] if name == "sweep.py"
                                        else []))
        took = loaded()
        if rc in (0, None):
            zero.append("%s (rc=%s)" % (name, rc))
        if not any(RESOLVE_WORD in one for one in lines):
            mute.append("%s (%s)" % (name, quiet(lines[-1] if lines
                                                  else "no output")))
        if took:
            loading.append("%s (%s)" % (name, ", ".join(took[:2])))
    check("each one stops with a return code other than 0",
          bool(started_here) and not zero, "%d of %d returned 0: %s"
          % (len(zero), len(started_here), quiet(", ".join(zero)) or "none"))
    check("each one says the word that starts it",
          bool(started_here) and not mute, "%d of %d without %r: %s"
          % (len(mute), len(started_here), RESOLVE_WORD,
             quiet("; ".join(mute[:2])) or "none"))
    check("none loads the program or the Resolve module first",
          bool(started_here) and not loading, "%d of %d loaded: %s"
          % (len(loading), len(started_here),
             quiet("; ".join(loading[:2])) or "none"))
except Exception as e:
    # Not a judgement of its own: a step that threw is named in the
    # closing line, so every path still ends there.
    bad.append("the test stopped half way [%s: %s]"
               % (type(e).__name__, quiet(e)))
finally:
    shutil.rmtree(D, ignore_errors=True)

print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
