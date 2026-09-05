# -*- coding: utf-8 -*-
"""Keeping itself up to date must not surprise anybody or guess.

Nothing here touches the network: asking github.com for a version
number is answered from a table, so this says something about the
arithmetic rather than about the weather. The way out is nailed shut
at the top and every address asked for is written down, so a check
cannot pass over a real look.

The sections: which version is newer, that only a newer one is
offered, that a pre-release sorts under its release in both
spellings, that nothing a user did once can stop the looking, that
the switches which did that are gone, that what comes back is read
before it is believed, that the old file is kept, that one version
may be passed over, that a release text is shown in one language,
what the command line says and fetches, that a look which could not
happen says so instead of reading as nothing newer, and that an
installation is handed to pip rather than written over.
"""
import os
import the_program
HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = the_program.SCRIPT
# The suite sets this, and the module reads it while it is loading.
os.environ.pop("VPM_NO_UPDATE_CHECK", None)
import io, ssl, subprocess, sys, tempfile, time
import urllib.request
began = time.time()
vpm = the_program.load()
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
# beat its own pre-release, and the pre-release name cut into its runs,
# the digits of it as numbers.
WRITTEN_DOWN = (((2, 0, 0), 1, ()),
                ((2, 1, 0), 0, ((1, "beta."), (0, 2))))
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

print("\n3. A pre-release sorts under its release in both spellings")
# The tags on github read v2.32.0-beta; pip hangs the same thing
# straight on the numbers as 3.0.0b0, and that is what this program
# calls itself. Both have to fall under the finished release of the
# same numbers, and both have to fall into one line together.
RISING = ["2.32.0-beta", "3.0.0a1", "3.0.0b0", "3.0.0b1", "3.0.0b9",
          "3.0.0b10", "3.0.0b11", "3.0.0rc1", "3.0.0", "3.0.1", "3.1.0"]
keys = [vpm.version_key(one) for one in RISING]
# Step by step against the neighbour, never sorted(): sorting is
# stable, so a key that answered the same for every one of them would
# hand the list back in the order it was given and prove nothing.
flat = ["%s < %s is %r < %r" % (RISING[i], RISING[i + 1], keys[i],
                                keys[i + 1])
        for i in range(len(keys) - 1) if not keys[i] < keys[i + 1]]
check("the whole run of versions rises, oldest first", not flat,
      "%d of the %d steps do not rise: %s"
      % (len(flat), len(keys) - 1, flat[:2]))
# The key itself, written out, not only how two of them compare: the
# 0 in the middle is what puts a pre-release under its own release.
PIP_READ = ((3, 0, 0), 0, ((1, "b"), (0, 0)))
pip_key = vpm.version_key("3.0.0b0")
check("the pip spelling reads as the key written down here",
      pip_key == PIP_READ,
      "'3.0.0b0' sorts to %r, written down is %r" % (pip_key, PIP_READ))
# The tenth beta of a release is where a pre-release read as text goes
# wrong, because 9 stands behind 1 in the alphabet. The name that
# trails off with nothing after the dot is in the list because the
# reading has to cut that one into runs as well.
NUMBERED = ["2.0.0-beta.", "2.0.0-beta.2", "2.0.0-beta.10", "2.0.0"]
by_number = [vpm.version_key(one) for one in NUMBERED]
number_flat = ["%s < %s is %r < %r" % (NUMBERED[i], NUMBERED[i + 1],
                                       by_number[i], by_number[i + 1])
               for i in range(len(by_number) - 1)
               if not by_number[i] < by_number[i + 1]]
check("the dash spelling rises by the number after the dot",
      not number_flat, "%d of the %d steps do not rise: %s"
      % (len(number_flat), len(by_number) - 1, number_flat[:2]))
# The spelling already published, which forty-three tags carry: sorting
# those wrong would be worse than the fault this section is about. The
# patch number is in the list on purpose -- it is the piece that falls
# first when the dash is no longer split off.
PUBLISHED = ["v2.9.0-beta", "v2.10.0-beta", "v2.31.0-beta",
             "v2.31.1-beta", "v2.32.0-beta"]
old_keys = [vpm.version_key(one) for one in PUBLISHED]
old_flat = ["%s < %s is %r < %r" % (PUBLISHED[i], PUBLISHED[i + 1],
                                    old_keys[i], old_keys[i + 1])
            for i in range(len(old_keys) - 1)
            if not old_keys[i] < old_keys[i + 1]]
check("the spelling already published still rises the same way",
      not old_flat, "%d of the %d steps do not rise: %s"
      % (len(old_flat), len(old_keys) - 1, old_flat[:2]))
# Not version_key on its own: this is the jump that stands next, and
# what a person is shown comes out of newer_release.
was_running = vpm.VERSION
vpm.VERSION = "3.0.0b0"
offered = with_tag("v3.0.0")[0]
check("whoever runs the pip pre-release is offered the release",
      offered == "v3.0.0",
      "v3.0.0 against a running %s: offered %r, wanted 'v3.0.0'"
      % (vpm.VERSION, offered))
offered = with_tag("v3.0.0b0")[0]
check("and the pre-release they run is not offered back to them",
      offered == "",
      "v3.0.0b0 against a running %s: offered %r, wanted ''"
      % (vpm.VERSION, offered))
vpm.VERSION = "3.0.0"
offered = with_tag("v3.0.0b1")[0]
check("and nobody on the release is sent back to a pre-release",
      offered == "",
      "v3.0.0b1 against a running %s: offered %r, wanted ''"
      % (vpm.VERSION, offered))
vpm.VERSION = was_running
# A label somebody set wrong must not end the looking in a traceback.
# What it earns is a key that loses, not an exception.
NOT_A_VERSION = ["main", "", "v", "nightly", "3.0.0b", "2.0.0-beta."]
labels, threw = {}, []
for one in NOT_A_VERSION:
    try:
        labels[one] = vpm.version_key(one)
    except Exception as e:
        threw.append("%r threw %s: %s" % (one, type(e).__name__, e))
check("a label that is no version is read without throwing", not threw,
      "%d of the %d threw: %s"
      % (len(threw), len(NOT_A_VERSION), threw[:2]))
OLDEST = vpm.version_key("0.0.1")
counted = [one for one in ("main", "", "v", "nightly")
           if labels.get(one, OLDEST) >= OLDEST]
check("and a label nobody can read never counts as newer", not counted,
      "%s sort to %s, wanted below the %r of '0.0.1'"
      % (counted, [labels.get(one) for one in counted], OLDEST))
# PEP 440 reads an a, b or rc with no number after it as the zeroth of
# them, so a mistyped 3.0.0b is a pre-release and not the release. The
# reading comes out of the loop above rather than being asked for
# again: a reading that threw there would end this file in a traceback
# here, and the judgement below would never be reached.
finished = vpm.version_key("3.0.0")
loose = labels.get("3.0.0b", finished)
check("a pre-release mark with no number is not the release",
      loose < finished, "'3.0.0b' sorts to %r, '3.0.0' to %r"
      % (loose, finished))

print("\n4. Nothing a user did once stops the looking")
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

print("\n5. The switches that stopped it are gone")
# Not the parser alone: the two switches were answered off sys.argv
# before a namespace ever existed, so a parser that does not know them
# proves nothing on its own. The whole text is read, and the program
# is asked as a user asks it.
source = the_program.whole()


def times(*words):
    """How often each of those stands in the program, as evidence."""
    return "%s in the %d characters of the program" % (
        ", ".join("%s %d time(s)" % (w, source.count(w)) for w in words),
        len(source))


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

print("\n6. What comes back is read before it is believed")
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

print("\n7. The old file is kept")
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

print("\n8. Passing over one version")
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
    tag, _page, _text, _trouble = vpm.newer_release()
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
    tag, _p, _t, _tr = vpm.newer_release()
    check("and it is not offered again by itself", tag == "",
          "unasked with 'v2.19.0-beta' passed over: offered %r, wanted ''"
          % (tag,))

    # The whole point of the change: the next one asks again.
    urllib.request.urlopen = what_github_says("v2.20.0-beta")
    tag, _p, _t, _tr = vpm.newer_release()
    check("but the next version is offered", tag == "v2.20.0-beta",
          "github said v2.20.0-beta with 'v2.19.0-beta' passed over:"
          " offered %r, wanted 'v2.20.0-beta'" % (tag,))

    # Asking from the menu is a person wanting to know, and what was
    # passed over does not stand against that.
    urllib.request.urlopen = what_github_says("v2.19.0-beta")
    tag, _p, _t, _tr = vpm.newer_release(asked=True)
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
print("\n9. The window shows one language")
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

print("\n10. The command line says it and fetches nothing")
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

print("\n11. --update puts the new version in place")
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

print("\n12. Not being able to look is not nothing new")
# The fault this is about: every failure came back as the empty answer,
# which is what "there is nothing newer" looks like as well. Measured on
# 3.9.2026 in a fresh environment without certifi -- the certificate
# could not be checked, and the program said "no newer version" after
# 0.19 s. The certificate is therefore what fails here too.
os.environ["VPM_CACHE"] = _tf.mkdtemp(prefix="vpm_update_blind_")
vpm.VERSION = "2.15.0-beta"
vpm.UPDATE_OFF = False


def refused(*a, **k):
    """What urlopen does where the certificate cannot be checked."""
    raise ssl.SSLCertVerificationError(
        1, "[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed:"
           " unable to get local issuer certificate")


def sayable(text):
    """That sentence, fit to be printed. Evidence, not judgement.

    run.sh reads FAIL anywhere in a test's output as a verdict, and
    OpenSSL's own reason is CERTIFICATE_VERIFY_FAILED. Printed as it
    stands it turns this test red with every check in it green, so the
    one word is masked here and nowhere else -- the exception the
    stand-in raises carries it whole.
    """
    return text.replace("FAILED", "<refused>")


def when_the_look_fails(asked):
    """newer_release with every look failing on the certificate."""
    was = urllib.request.urlopen
    urllib.request.urlopen = refused
    try:
        return vpm.newer_release(asked)
    finally:
        urllib.request.urlopen = was


tag, _p, _c, trouble = when_the_look_fails(True)
check("a look that could not happen says so when somebody asked",
      tag == "" and trouble != "",
      "an asked look met the certificate: offered %r and said %r, wanted"
      " no tag and a sentence" % (tag, sayable(trouble)))
# Nobody asked, so nobody is told: a start without a network would
# otherwise complain on every single run.
_t, _p, _c, unasked = when_the_look_fails(False)
check("and it says nothing where nobody asked", unasked == "",
      "an unasked look met the certificate and said %r, wanted ''"
      % (sayable(unasked),))
# The judgement the section is really for: the two answers that used to
# be the same answer. Held against the sentence a failed look gives, so
# the line shows both halves of the distinction rather than one empty
# string on its own.
_t, _p, _c, nothing_new = with_tag("v1.0.0", asked=True)
check("and a look that found nothing newer says nothing went wrong",
      nothing_new == "",
      "github said v1.0.0 to a running %s: trouble %r, wanted '', where a"
      " look that could not happen says %r"
      % (vpm.VERSION, nothing_new, sayable(trouble)))


def update_run_when_the_look_fails():
    """--update against the copy while every look fails."""
    was, out = urllib.request.urlopen, io.StringIO()
    was_file, was_stdout = vpm.__file__, sys.stdout
    sys.stdout = out
    urllib.request.urlopen = refused
    vpm.__file__ = COPY
    try:
        return vpm.update_from_command_line(), out.getvalue()
    finally:
        sys.stdout = was_stdout
        urllib.request.urlopen = was
        vpm.__file__ = was_file


code, spoken = update_run_when_the_look_fails()
check("--update does not report a failed look as a finished one", code != 0,
      "returned %r saying %r, wanted anything but 0"
      % (code, sayable(spoken.strip()[:80])))
# Not written out: the sentence goes through T() and is German in a
# German run, so it is asked for the same way the program asks for it.
NOTHING_NEW = vpm.T('No newer version found. This one is %s.') % vpm.VERSION
check("and it does not say there is nothing newer",
      NOTHING_NEW not in spoken and spoken.strip() != "",
      "it said %r, where a look that happened and found nothing would say"
      " %r" % (sayable(spoken.strip()[:120]), NOTHING_NEW))

print("\n13. An installation is updated by pip, not by a file swap")
# pip is the one thing here that must never be the real one. The
# stand-in refuses a command whose program is not on this machine, the
# way starting one really does, so a wrong call cannot come back
# looking like a good one.
import subprocess
import sysconfig

PURELIB = sysconfig.get_paths()["purelib"]
INSTALLED = os.path.join(PURELIB, "videopodcast_magic.py")
LOOSE = os.path.join(tempfile.mkdtemp(prefix="vpm_update_loose_"),
                     "videopodcast_magic.py")
ORDERS = []          # every command a stand-in pip was asked to start
GOT = []             # every piece of text the program handed on
HANDED = []          # how much had been handed on as each line was read
ASKED = []           # every address the installed --update asked for
PIP_SAYS = [b"Collecting videopodcast-magic\n",
            b"Building wheel for videopodcast-magic\n",
            b"Successfully installed videopodcast-magic-9.9.9\n"]
PIP_CODE = [0]


class Trickle(object):
    """pip's output, and a note of what was passed on before each line."""

    def __iter__(self):
        for line in PIP_SAYS:
            HANDED.append(len(GOT))
            yield line


class StandInPip(object):
    """As much of Popen as the program uses, and nothing more.

    A command whose first word is no program on this machine is refused
    with OSError, the way exec refuses one: a stand-in that starts
    anything would let a wrong call pass for a good one.
    """

    def __init__(self, order, stdout=None, stderr=None):
        ORDERS.append(list(order))
        if not os.path.exists(order[0]):
            raise OSError(2, "no such program: %s" % order[0])
        self.stdout = Trickle()

    def wait(self):
        return PIP_CODE[0]


def with_pip(what):
    """Run *what* with pip replaced, and put the real one back after."""
    was = subprocess.Popen
    subprocess.Popen = StandInPip
    try:
        return what()
    finally:
        subprocess.Popen = was


IN_PLACE = vpm.T('%s is installed. It runs from the next start.') % "v9.9.9"
trouble = with_pip(lambda: vpm.pip_update("v9.9.9", GOT.append))
WANTED = [sys.executable, "-m", "pip"]
check("pip runs in the Python this program runs in",
      bool(ORDERS) and ORDERS[0][:3] == WANTED,
      "pip was started as %r, wanted %r at the front"
      % (ORDERS[0][:3] if ORDERS else None, WANTED))
check("pip is told to upgrade from the repository itself",
      bool(ORDERS) and ORDERS[0][3:] == ["install", "-U", vpm.PIP_SOURCE]
      and vpm.PIP_SOURCE.startswith("git+https://github.com/"),
      "the rest of the command was %r and the address is %r, wanted "
      "install -U and a git+https address"
      % (ORDERS[0][3:] if ORDERS else None, vpm.PIP_SOURCE))
# Written down as each line was read, not counted at the end: what this
# is about is a run of minutes whose output arrives while it runs.
STEPS = list(range(1, len(PIP_SAYS) + 1))
check("what pip says is passed on as it comes, not collected first",
      HANDED == STEPS,
      "as each of the %d lines was read, %r pieces had gone to the "
      "window, wanted %r" % (len(PIP_SAYS), HANDED, STEPS))
check("the new version is named once pip is through", IN_PLACE in "".join(GOT),
      "the window was handed %r, wanted %r in it"
      % ("".join(GOT)[-60:], IN_PLACE))
check("a pip that went through is not reported as trouble", trouble == "",
      "pip returned 0 and pip_update said %r, wanted ''" % (trouble,))

del GOT[:], ORDERS[:], HANDED[:]
PIP_CODE[0] = 3
trouble = with_pip(lambda: vpm.pip_update("v9.9.9", GOT.append))
check("a pip that stops part way says so and names the number",
      trouble != "" and "3" in trouble,
      "pip returned 3 and pip_update said %r, wanted a sentence with 3 "
      "in it" % (trouble,))
check("and nothing then claims the new version is installed",
      IN_PLACE not in "".join(GOT),
      "the window was handed %r, which must not carry %r"
      % ("".join(GOT)[-60:], IN_PLACE))


def no_pip_at_all(order, stdout=None, stderr=None):
    """A machine whose Python has no pip in it."""
    ORDERS.append(list(order))
    raise OSError(2, "no such program: %s" % order[0])


del GOT[:], ORDERS[:]
was_popen = subprocess.Popen
subprocess.Popen = no_pip_at_all
try:
    trouble = vpm.pip_update("v9.9.9", GOT.append)
finally:
    subprocess.Popen = was_popen
check("a pip that cannot be started is reported, not passed over",
      trouble != "" and IN_PLACE not in "".join(GOT),
      "starting pip raised and pip_update said %r, having handed over %r"
      % (trouble, "".join(GOT)[-60:]))

was_file = vpm.__file__
try:
    vpm.__file__ = INSTALLED
    owner = vpm.installed_by_a_package_manager()
    vpm.__file__ = LOOSE
    loose = vpm.installed_by_a_package_manager()
finally:
    vpm.__file__ = was_file
check("a file in the folder pip installs into counts as installed",
      owner == PURELIB, "%r for a file in %r, wanted the folder itself"
      % (owner, PURELIB))
check("and one in a folder of its own does not", loose == "",
      "%r for a file in %r, wanted ''" % (loose, os.path.dirname(LOOSE)))
check("the window promises something else where pip owns the folder",
      vpm.update_promise(PURELIB) != vpm.update_promise(""),
      "both said %r, wanted two different sentences"
      % (vpm.update_promise("")[:60],))
check("and it names the folder pip will write into",
      PURELIB in vpm.update_promise(PURELIB),
      "it said %r, wanted %r in it"
      % (vpm.update_promise(PURELIB)[:80], PURELIB))

JOBS = []
was_sink = vpm.UPDATE_SINK
try:
    vpm.UPDATE_SINK = JOBS.append
    answer = vpm.update_fetched("v9.9.9", PURELIB)
    vpm.UPDATE_SINK = None
    without = vpm.update_fetched("v9.9.9", PURELIB)
finally:
    vpm.UPDATE_SINK = was_sink
check("an installed program is handed to the window, not written over",
      answer == "" and len(JOBS) == 1,
      "update_fetched said %r and handed the window %d jobs, wanted '' "
      "and one" % (answer, len(JOBS)))
del GOT[:], ORDERS[:]
PIP_CODE[0] = 0
if JOBS:
    with_pip(lambda: JOBS[0](GOT.append))
check("and what the window is handed starts pip",
      bool(ORDERS) and ORDERS[0][:3] == WANTED,
      "the job the window got started %r, wanted %r at the front"
      % (ORDERS[0][:3] if ORDERS else None, WANTED))
check("without a window to show pip, the update is refused with a word",
      without != "",
      "update_fetched with no window said %r, wanted a sentence"
      % (without,))


class Said(object):
    """One answer from github, in the shape urlopen hands back."""

    def __init__(self, body):
        self.body = body

    def __enter__(self):
        return self

    def __exit__(self, *_):
        return False

    def read(self):
        return self.body


def only_the_release(url, *rest, **more):
    """Answer the version question, and refuse to hand out the program."""
    where = str(getattr(url, "full_url", url))
    ASKED.append(where)
    if RAW in where:
        raise IOError("the program file is not fetched in an installation")
    return Said(json.dumps({
        "tag_name": "v9.9.9", "html_url": "https://example/v9.9.9",
        "body": "what changed"}).encode("utf-8"))


def update_run_installed():
    """--update while the program sits where pip installed it."""
    was, out = urllib.request.urlopen, io.StringIO()
    was_here, was_stdout = vpm.__file__, sys.stdout
    sys.stdout = out
    urllib.request.urlopen = only_the_release
    vpm.__file__ = INSTALLED
    try:
        return with_pip(vpm.update_from_command_line), out.getvalue()
    finally:
        sys.stdout = was_stdout
        urllib.request.urlopen = was
        vpm.__file__ = was_here


del ORDERS[:]
code, spoken = update_run_installed()
check("--update in an installation lets pip do it instead of refusing",
      code == 0 and bool(ORDERS) and ORDERS[0][:3] == WANTED,
      "returned %r, pip was started as %r, and it said %r"
      % (code, ORDERS[0][:3] if ORDERS else None, spoken.strip()[:60]))
check("and it fetches no program file of its own in that case",
      not [a for a in ASKED if RAW in a],
      "of the %d addresses asked for, these carry the raw file: %r"
      % (len(ASKED), [a for a in ASKED if RAW in a][:2]))

check("no look in this whole run left the machine", not WENT_OUT,
      "%d addresses got past the stand-ins, the first of them %s"
      % (len(WENT_OUT), WENT_OUT[0] if WENT_OUT else "none"))

print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
