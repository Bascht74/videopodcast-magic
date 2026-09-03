# -*- coding: utf-8 -*-
"""Keeping itself up to date must not surprise anybody.

Nothing here touches the network: asking github.com for a version
number is answered from a table, so this says something about the
arithmetic rather than about the weather. The way out is nailed shut
at the top and every address asked for is written down, so a check
cannot pass over a real look.

The sections: which version is newer, that only a newer one is
offered, that nothing a user did once can stop the looking, that the
switches which did that are gone, that what comes back is read before
it is believed, that the old file is kept, that one version may be
passed over, that a release text is shown in one language, and what
the command line says and fetches.
"""
import os
HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = os.environ.get("VPM_SCRIPT") or os.path.join(
    os.path.dirname(HERE), "videopodcast_magic.py")
# The suite sets this, and the module reads it while it is loading.
os.environ.pop("VPM_NO_UPDATE_CHECK", None)
import importlib.util, io, subprocess, sys, tempfile, time
import urllib.request
began = time.time()
spec = importlib.util.spec_from_file_location("vpm", SCRIPT)
vpm = importlib.util.module_from_spec(spec); sys.modules["vpm"] = vpm
spec.loader.exec_module(vpm)
# The real one, kept before any section puts a stand-in in its place:
# the sections further down point VPM_CACHE at a folder of their own
# and want the reading that answers it.
REAL_CACHE_FOLDER = vpm.cache_folder

WENT_OUT = []


def no_network(url, *rest, **more):
    """Refuse every look and write down where it wanted to go."""
    WENT_OUT.append(str(getattr(url, "full_url", url)))
    raise IOError("this test asks github.com nothing")


# Nailed shut here rather than trusting VPM_NO_UPDATE_CHECK: the whole
# point of several checks below is that the looking is not switched
# off, so the switch cannot be the thing that keeps this test at home.
urllib.request.urlopen = no_network

done = 0
bad = []


def check(name, ok, extra=""):
    global done
    done += 1
    print("  %-58s %s %s" % (name, "ok" if ok else "FAIL", extra))
    if not ok:
        bad.append("%s [%s]" % (name, extra or "no numbers"))


def held_by(path):
    """What stands in that file, or, in its place, why nothing does.

    Evidence, not judgement: a missing file is the interesting case
    here, and a line that printed nothing for it would say nothing.
    """
    if not os.path.exists(path):
        return "<no such file>"
    try:
        return open(path, encoding="utf-8").read()
    except OSError as e:
        return "<unreadable: %s>" % e.strerror


print("1. Which version is newer")
# Semantic Versioning: a finished release beats its own pre-release,
# and a name nobody understands never wins.
ORDER = [("1.0.0", "1.0.1"), ("1.9.9", "2.0.0"), ("2.0.0-beta", "2.0.0"),
         ("2.0.0-beta", "2.0.1-beta"), ("v2.0.0", "v2.1.0"),
         ("banana", "0.0.1"), ("", "0.0.1")]
for older, newer in ORDER:
    first, second = vpm.version_key(older), vpm.version_key(newer)
    check("%r comes before %r" % (older, newer), first < second,
          "%r sorts to %r, %r to %r" % (older, first, newer, second))
with_v, bare = vpm.version_key("v2.0.0-beta"), vpm.version_key("2.0.0-beta")
check("the same version is the same", with_v == bare,
      "'v2.0.0-beta' sorts to %r, '2.0.0-beta' to %r" % (with_v, bare))
# Written out, not held against a second reading of itself. A version
# never beats itself whatever version_key does, so that judgement said
# only that the function answers the same twice: measured on 2.9.2026,
# flattening version_key to one constant turned 23 of the checks in
# this file red and left it green. Every pair above compares one
# reading with another, so a key that changed its meaning wholesale
# still sorts the same way. This is the one place that says what a
# reading is -- the three numbers, the 1 that lets a finished release
# beat its own pre-release, and the pre-release name kept whole.
WRITTEN_DOWN = (((2, 0, 0), 1, ""), ((2, 1, 0), 0, "beta.2"))
read_as = (vpm.version_key("2.0.0"), vpm.version_key("v2.1.0-beta.2"))
check("a version reads as the key written down here",
      read_as == WRITTEN_DOWN,
      "'2.0.0' and 'v2.1.0-beta.2' sort to %r, written down is %r"
      % (read_as, WRITTEN_DOWN))

print("\n2. Only a newer release counts")
# A folder of its own: what a real run left in the cache of whoever
# starts this test has no business deciding anything here.
ANSWERS = tempfile.mkdtemp(prefix="vpm_update_")
vpm.cache_folder = lambda sub="": ANSWERS
def with_tag(tag, asked=False):
    """Answer the question with this tag, without a network."""
    class Answer(object):
        def read(self):
            return ('{"tag_name": "%s", "html_url": "u"}' % tag).encode()
        def __enter__(self):
            return self
        def __exit__(self, *rest):
            return False
    import urllib.request
    was = urllib.request.urlopen
    urllib.request.urlopen = lambda *a, **k: Answer()
    try:
        return vpm.newer_release(asked)
    finally:
        urllib.request.urlopen = was

vpm.VERSION = "2.0.0-beta"
offered = with_tag("v2.1.0")[0]
check("a newer tag is offered", offered == "v2.1.0",
      "v2.1.0 against a running %s: offered %r, wanted 'v2.1.0'"
      % (vpm.VERSION, offered))
offered = with_tag("v2.0.0-beta")[0]
check("the same tag is not", offered == "",
      "v2.0.0-beta against a running %s: offered %r, wanted ''"
      % (vpm.VERSION, offered))
offered = with_tag("v1.9.0")[0]
check("an older tag is not", offered == "",
      "v1.9.0 against a running %s: offered %r, wanted ''"
      % (vpm.VERSION, offered))

offered = with_tag("v2.0.0")[0]
check("the finished version beats the pre-release", offered == "v2.0.0",
      "v2.0.0 against a running %s: offered %r, wanted 'v2.0.0'"
      % (vpm.VERSION, offered))
offered = with_tag("nightly")[0]
check("an unreadable tag is not offered", offered == "",
      "'nightly' against a running %s: offered %r, wanted ''"
      % (vpm.VERSION, offered))

print("\n3. Nothing a user did once stops the looking")
# The fault this is about: a no given once in passing was written into
# the cache and the program went quiet for good, with nothing on any
# screen saying why. It caught the owner twice, in August and again on
# 1.9.2026, so the answer is not shown -- it is gone.
folder = tempfile.mkdtemp(prefix="vpm_update_left_")
os.environ["VPM_CACHE"] = folder
vpm.cache_folder = REAL_CACHE_FOLDER
LEFT = os.path.join(REAL_CACHE_FOLDER(), "update_check")
with open(LEFT, "w", encoding="utf-8") as f:
    f.write("no")
offered = with_tag("v9.9.9")[0]
check("a no left in the cache does not stop the unasked look",
      offered == "v9.9.9",
      "with %r holding %r: offered %r for v9.9.9, wanted 'v9.9.9'"
      % (os.path.basename(LEFT), held_by(LEFT), offered))
offered = with_tag("v9.9.9", asked=True)[0]
check("and it does not stop a direct question either", offered == "v9.9.9",
      "asked with %r holding %r: offered %r for v9.9.9, wanted 'v9.9.9'"
      % (os.path.basename(LEFT), held_by(LEFT), offered))
# Neither read nor written: a file the program still wrote to would be
# the same mechanism under another name, waiting to be read again.
os.unlink(LEFT)
with_tag("v9.9.9")
with_tag("v9.9.9", asked=True)
check("and no look writes that file back", not os.path.exists(LEFT),
      "after two looks %r holds %r, wanted no such file"
      % (os.path.basename(LEFT), held_by(LEFT)))
# The one thing that may still stop it belongs to whoever runs the
# machine, not to whoever clicks.
was_off = vpm.UPDATE_OFF
vpm.UPDATE_OFF = True
offered = with_tag("v9.9.9", asked=True)[0]
vpm.UPDATE_OFF = was_off
check("only VPM_NO_UPDATE_CHECK still stops it", offered == "",
      "asked with the switch set: offered %r for v9.9.9, wanted ''"
      % (offered,))

print("\n4. The switches that stopped it are gone")
# Not the parser alone: the two switches were answered off sys.argv
# before a namespace ever existed, so a parser that does not know them
# proves nothing on its own. The whole text is read, and the program
# is asked as a user asks it.
source = io.open(SCRIPT, encoding="utf-8").read()


def times(*words):
    """How often each of those stands in the program, as evidence."""
    return "%s in the %d characters of %s" % (
        ", ".join("%s %d time(s)" % (w, source.count(w)) for w in words),
        len(source), os.path.basename(SCRIPT))


OFF_SWITCHES = ("--no-update-check", "--update-check")
check("no switch that stops the looking stands in the program",
      not any(w in source for w in OFF_SWITCHES), times(*OFF_SWITCHES))
KEEPS_ANSWER = ("set_update_wanted", "update_answer_file", "update_wanted")
check("and nothing writes or reads a remembered answer",
      not any(w in source for w in KEEPS_ANSWER), times(*KEEPS_ANSWER))
handed = set()
for entry in vpm.build_argument_parser()._actions:
    handed.update(entry.option_strings)
check("the program hands out a switch that fetches the new version",
      "--update" in handed,
      "%d switches, and --update is %s among them"
      % (len(handed), "" if "--update" in handed else "not"))
# The switch on its own, and no --version or --help beside it: those
# two answer and leave before argparse reports anything it does not
# know, so the run would end at 0 with the switch never judged. And
# held against a name nobody ever gave the program, because a switch
# that is taken and ignored also ends in a complaint about the files.
REFUSE_ENV = dict(os.environ, VPM_NO_UPDATE_CHECK="1", LANG="C",
                  LC_ALL="C", LANGUAGE="en")


def given(switch):
    """Start the program with that one switch. (code, what it said)"""
    said = subprocess.run([sys.executable, SCRIPT, switch],
                          capture_output=True, text=True,
                          stdin=subprocess.DEVNULL, env=REFUSE_ENV)
    return said.returncode, ((said.stdout or "") + (said.stderr or "")
                             ).replace(switch, "<the switch>").strip()


off_code, off_said = given("--no-update-check")
made_code, made_said = given("--a-switch-nobody-ever-gave-it")
check("and the program refuses it the way it refuses a made-up name",
      off_code == made_code and off_said == made_said,
      "returned %d saying %r, while a made-up name returned %d saying %r"
      % (off_code, off_said[-70:], made_code, made_said[-70:]))

print("\n5. What comes back is read before it is believed")
def with_body(body):
    class Answer(object):
        def read(self):
            return body
        def __enter__(self):
            return self
        def __exit__(self, *rest):
            return False
    import urllib.request
    was = urllib.request.urlopen
    urllib.request.urlopen = lambda *a, **k: Answer()
    try:
        return vpm.fetch_new_self("v9.9.9")
    finally:
        urllib.request.urlopen = was

good = b'VERSION = "9.9.9"\nCATALOGUE = {}\n'
text, trouble = with_body(good)
check("a whole program is taken", bool(text) and not trouble,
      "%d of the %d characters came back, and the trouble was %r"
      % (len(text or ""), len(good), trouble))
text, trouble = with_body(b'<html>404</html>')
check("an error page is refused", not text and bool(trouble),
      "<html>404</html> gave back %d characters of program, trouble %r"
      % (len(text or ""), trouble))
# The wording is not checked: the message goes through T() and is
# German in a German run. What matters is that it is refused and that
# a broken file and an error page do not get the same answer.
text, trouble = with_body(b'VERSION = "9"\nCATALOGUE = {\n')
_, other = with_body(b'<html>404</html>')
check("something that does not compile is refused",
      not text and bool(trouble),
      "an unclosed brace gave back %d characters of program, trouble %r"
      % (len(text or ""), trouble))
check("and says something else than an error page does", trouble != other,
      "the unclosed brace says %r, the 404 page says %r" % (trouble, other))
# Held against the error page's reason too, not only against "it was
# refused". The question under this one turns away anything that is
# not this program, and it answers bytes that never decoded as well --
# so the decoding could be taken out altogether and this stayed green.
# Measured on 2.9.2026: decoding with errors="replace" left every
# check in the file green.
text, trouble = with_body(b'\xff\xfe not text')
check("bytes that are not text are refused, not as an error page",
      not text and bool(trouble) and trouble != other,
      "two bytes that are no utf-8 gave back %d characters of program,"
      " trouble %r, where an error page says %r"
      % (len(text or ""), trouble, other))

print("\n6. The old file is kept")
work = tempfile.mkdtemp()
mine = os.path.join(work, "videopodcast_magic.py")
with open(mine, "w", encoding="utf-8") as f:
    f.write("the one that works\n")
was_file = vpm.__file__
vpm.__file__ = mine
try:
    trouble = vpm.put_new_self("the new one\n")
finally:
    vpm.__file__ = was_file
check("writing works", not trouble, "put_new_self said %r" % (trouble,))
now = held_by(mine)
check("the new one is in place", now == "the new one\n",
      "videopodcast_magic.py holds %r, wanted %r" % (now, "the new one\n"))
kept = held_by(mine + ".old")
check("the old one is beside it", kept == "the one that works\n",
      "videopodcast_magic.py.old holds %r, wanted %r"
      % (kept, "the one that works\n"))

print("\n7. Passing over one version")
# The one answer left that a person can give, and it is about one
# version: the next release has another name and asks again.
import tempfile as _tf
os.environ["VPM_CACHE"] = _tf.mkdtemp(prefix="vpm_update_cache_")


def what_github_says(tag):
    """Answer every look with that one release, as github would."""
    class Answer(object):
        def __enter__(self):
            return self

        def __exit__(self, *_):
            return False

        def read(self):
            return json.dumps({
                "tag_name": tag, "html_url": "https://example/%s" % tag,
                "body": "what changed"}).encode("utf-8")
    return lambda *a, **k: Answer()


import json, urllib.request
was_open = urllib.request.urlopen
# The suite switches the looking off for every test. This one answers
# every look itself, so the switch is lifted here -- otherwise
# newer_release turns back at the door and every check passes blind.
vpm.UPDATE_OFF = False
vpm.VERSION = "2.15.0-beta"
try:
    urllib.request.urlopen = what_github_says("v2.19.0-beta")
    tag, _page, _text = vpm.newer_release()
    # repr, not the bare tag: the case this is about is the empty one,
    # and a line ending in nothing says nothing.
    check("a newer version is offered", tag == "v2.19.0-beta",
          "github said v2.19.0-beta to a running %s: offered %r, wanted"
          " 'v2.19.0-beta'" % (vpm.VERSION, tag))

    vpm.set_update_skipped(tag)
    passed_over = vpm.update_skipped()
    check("what was passed over is what was shown",
          passed_over == "v2.19.0-beta",
          "passed over %r after being shown 'v2.19.0-beta', wanted"
          " 'v2.19.0-beta'" % (passed_over,))
    tag, _p, _t = vpm.newer_release()
    check("and it is not offered again by itself", tag == "",
          "unasked with 'v2.19.0-beta' passed over: offered %r, wanted ''"
          % (tag,))

    # The whole point of the change: the next one asks again.
    urllib.request.urlopen = what_github_says("v2.20.0-beta")
    tag, _p, _t = vpm.newer_release()
    check("but the next version is offered", tag == "v2.20.0-beta",
          "github said v2.20.0-beta with 'v2.19.0-beta' passed over:"
          " offered %r, wanted 'v2.20.0-beta'" % (tag,))

    # Asking from the menu is a person wanting to know, and what was
    # passed over does not stand against that.
    urllib.request.urlopen = what_github_says("v2.19.0-beta")
    tag, _p, _t = vpm.newer_release(asked=True)
    check("and asking from the menu shows it anyway",
          tag == "v2.19.0-beta",
          "asked with 'v2.19.0-beta' passed over: offered %r, wanted"
          " 'v2.19.0-beta'" % (tag,))
finally:
    urllib.request.urlopen = was_open

# ---------------------------------------------------- one language, not two
# A release says everything twice, English first and German under a rule.
# The window shows one of them. Two windows show this text and only one
# was cutting, so a German reader was handed the English half -- and it
# is the half that comes first.
print("\n8. The window shows one language")
TWO = ("**English**\n\n### Changed\n\n- the English point\n\n---\n\n"
       "**Deutsch**\n\n### Ge\u00e4ndert\n\n- der deutsche Punkt")


def between(language, releases):
    """What the collector hands a window, in that language."""
    class Answer(object):
        def __enter__(self):
            return self

        def __exit__(self, *_):
            return False

        def read(self):
            return json.dumps(releases).encode("utf-8")

    was, was_open = vpm.LANG, urllib.request.urlopen
    vpm.set_language(language)
    urllib.request.urlopen = lambda *a, **k: Answer()
    try:
        return vpm.releases_in_between("v3.0.0-beta", "v1.0.0-beta")
    finally:
        urllib.request.urlopen = was_open
        vpm.set_language(was)


one = [{"tag_name": "v2.0.0-beta", "body": TWO}]
for language, wanted, unwanted in (("de", "der deutsche Punkt", "the English point"),
                                   ("en", "the English point", "der deutsche Punkt")):
    text = between(language, one)
    # Whole, not cut: the half that was missing sat at the end, and
    # text[:60] showed the beginning, where nothing was ever wrong.
    check("%s: its own half is there" % language, wanted in text,
          "wanted %r among the %d characters %r" % (wanted, len(text), text))
    check("and the other one is not", unwanted not in text,
          "%r found %d time(s) among the %d characters %r"
          % (unwanted, text.count(unwanted), len(text), text))

# The collector joins several releases into one text, and each one has
# to be cut before they are joined -- otherwise the second brings the
# other language back in.
two = [{"tag_name": "v2.0.0-beta", "body": TWO},
       {"tag_name": "v2.1.0-beta", "body": TWO}]
text = between("de", two)
check("two releases, and still one language", "the English point" not in text,
      "found the English half %d time(s)" % text.count("the English point"))
check("and both of them are in it", text.count("der deutsche Punkt") == 2,
      "%d German points" % text.count("der deutsche Punkt"))

# A release from before the two halves comes back whole: half a text is
# worse than one in the wrong language.
older = [{"tag_name": "v2.0.0-beta", "body": "just one language here"}]
text = between("de", older)
check("a release without the two halves is kept whole",
      "just one language here" in text,
      "wanted 'just one language here' among the %d characters %r"
      % (len(text), text))

print("\n9. The command line says it and fetches nothing")
# A run started out of a script must not stop to ask anything, so the
# command line gets a line and no box. Fetching is a second step and
# has its own switch.
os.environ["VPM_CACHE"] = _tf.mkdtemp(prefix="vpm_update_line_")
vpm.VERSION = "2.15.0-beta"
RAW = "raw.githubusercontent.com"


def said_on_the_line(tag):
    """What update_note() prints, and which addresses it asked for."""
    asked = []

    class Answer(object):
        def __init__(self, body):
            self.body = body

        def __enter__(self):
            return self

        def __exit__(self, *_):
            return False

        def read(self):
            return self.body

    def opened(url, *a, **k):
        where = str(getattr(url, "full_url", url))
        asked.append(where)
        if RAW in where:
            return Answer(b'VERSION = "9.9.9"\nCATALOGUE = {}\n')
        return Answer(json.dumps({
            "tag_name": tag, "html_url": "https://example/%s" % tag,
            "body": "what changed"}).encode("utf-8"))

    was, out = urllib.request.urlopen, io.StringIO()
    was_stdout, sys.stdout = sys.stdout, out
    urllib.request.urlopen = opened
    try:
        vpm.update_note()
    finally:
        sys.stdout = was_stdout
        urllib.request.urlopen = was
    return out.getvalue(), asked


spoken, asked = said_on_the_line("v2.19.0-beta")
# Both versions, not the new one alone: the address underneath carries
# the new tag as well, so half the sentence could go and the tag would
# still stand there.
check("the line names the new version and the running one",
      "v2.19.0-beta" in spoken and vpm.VERSION in spoken,
      "with github saying v2.19.0-beta to a running %s it printed %r"
      % (vpm.VERSION, spoken))
check("and the way to fetch it is named with it",
      "--update" in spoken,
      "'--update' found %d time(s) in %r" % (spoken.count("--update"),
                                             spoken))
check("but nothing of the program itself is fetched",
      not any(RAW in one for one in asked),
      "%d addresses asked for, %s" % (len(asked), asked))
quiet, asked = said_on_the_line("v1.0.0")
check("and nothing is said where nothing is newer", quiet == "",
      "with github saying v1.0.0 to a running %s it printed %r"
      % (vpm.VERSION, quiet))

print("\n10. --update puts the new version in place")
# The only way the command line fetches anything. It writes over the
# file it is running from, so it is pointed at a copy of its own --
# nothing here may touch the program under test.
HOME = tempfile.mkdtemp(prefix="vpm_update_self_")
COPY = os.path.join(HOME, "videopodcast_magic.py")
with open(COPY, "w", encoding="utf-8") as f:
    f.write("the one that works\n")


def update_run(tag, switched_off=False):
    """Run --update against the copy, and keep what it printed."""
    class Answer(object):
        def __init__(self, body):
            self.body = body

        def __enter__(self):
            return self

        def __exit__(self, *_):
            return False

        def read(self):
            return self.body

    def opened(url, *a, **k):
        where = str(getattr(url, "full_url", url))
        if RAW in where:
            return Answer(b'VERSION = "9.9.9"\nCATALOGUE = {}\n')
        return Answer(json.dumps({
            "tag_name": tag, "html_url": "https://example/%s" % tag,
            "body": "what changed"}).encode("utf-8"))

    was, out = urllib.request.urlopen, io.StringIO()
    was_file, was_off = vpm.__file__, vpm.UPDATE_OFF
    was_stdout, sys.stdout = sys.stdout, out
    urllib.request.urlopen = opened
    vpm.__file__, vpm.UPDATE_OFF = COPY, switched_off
    try:
        return vpm.update_from_command_line(), out.getvalue()
    finally:
        sys.stdout = was_stdout
        urllib.request.urlopen = was
        vpm.__file__, vpm.UPDATE_OFF = was_file, was_off


code, spoken = update_run("v2.19.0-beta")
check("--update reports that it worked", code == 0,
      "returned %r and said %r, wanted 0" % (code, spoken.strip()[:80]))
now = held_by(COPY)
check("and the new version is in place", now.startswith('VERSION = "9.9.9"'),
      "the copy holds %r, wanted the fetched program" % (now[:40],))
kept = held_by(COPY + ".old")
check("and the one that ran is beside it", kept == "the one that works\n",
      "videopodcast_magic.py.old holds %r, wanted %r"
      % (kept, "the one that works\n"))
code, spoken = update_run("v2.19.0-beta", switched_off=True)
check("and with VPM_NO_UPDATE_CHECK it fetches nothing and says so",
      code == 1 and spoken.strip() != "",
      "returned %r and said %r, wanted 1 and a word" % (code, spoken.strip()))

check("no look in this whole run left the machine", not WENT_OUT,
      "%d addresses got past the stand-ins, the first of them %s"
      % (len(WENT_OUT), WENT_OUT[0] if WENT_OUT else "none"))

print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
