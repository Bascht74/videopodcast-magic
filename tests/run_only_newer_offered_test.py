# -*- coding: utf-8 -*-
"""Keeping itself up to date must not surprise anybody.

Nothing here touches the network: asking github.com for a version
number is answered from a table, so this says something about the
arithmetic rather than about the weather.
"""
import os
HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = os.environ.get("VPM_SCRIPT") or os.path.join(
    os.path.dirname(HERE), "videopodcast-magic.py")
# The suite sets this, and the module reads it while it is loading.
os.environ.pop("VPM_NO_UPDATE_CHECK", None)
import importlib.util, sys, tempfile, time
began = time.time()
spec = importlib.util.spec_from_file_location("vpm", SCRIPT)
vpm = importlib.util.module_from_spec(spec); sys.modules["vpm"] = vpm
spec.loader.exec_module(vpm)

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


def answer_in(folder):
    """The remembered yes or no as it lies on disk."""
    return held_by(os.path.join(folder, "update_check"))


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
itself = vpm.version_key("2.0.0")
check("a version does not beat itself",
      not vpm.version_key("2.0.0") < vpm.version_key("2.0.0"),
      "'2.0.0' sorts to %r, held against the same reading of itself"
      % (itself,))

print("\n2. Only a newer release counts")
# The remembered answer belongs to whoever runs the test, not to the
# test: somebody who ticked "Do not ask again" in the program would
# turn this file red. So it gets a folder of its own.
ANSWERS = tempfile.mkdtemp(prefix="vpm_update_")
# Over cache_folder, not update_answer_file: section 3 takes the same
# lever, and two would leave the answer where the test does not look.
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

vpm.set_update_wanted(False)
wanted = vpm.update_wanted()
check("a remembered no switches the unasked look off", not wanted,
      "update_wanted() is %r, wanted False; the answer on disk is %r"
      % (wanted, answer_in(ANSWERS)))
offered = with_tag("v2.1.0")[0]
check("a remembered no holds back the unasked look", offered == "",
      "unasked after a no: offered %r for v2.1.0, wanted ''" % (offered,))
offered = with_tag("v2.1.0", asked=True)[0]
check("but a direct question is still answered", offered == "v2.1.0",
      "asked after a no: offered %r for v2.1.0, wanted 'v2.1.0'"
      % (offered,))
vpm.set_update_wanted(True)
offered = with_tag("v2.1.0")[0]
check("and a yes brings it back", offered == "v2.1.0",
      "unasked after a yes: offered %r for v2.1.0, wanted 'v2.1.0'"
      % (offered,))
offered = with_tag("v2.0.0")[0]
check("the finished version beats the pre-release", offered == "v2.0.0",
      "v2.0.0 against a running %s: offered %r, wanted 'v2.0.0'"
      % (vpm.VERSION, offered))
offered = with_tag("nightly")[0]
check("an unreadable tag is not offered", offered == "",
      "'nightly' against a running %s: offered %r, wanted ''"
      % (vpm.VERSION, offered))

print("\n3. Switched off means switched off")
folder = tempfile.mkdtemp()
vpm.cache_folder = lambda sub="": folder
vpm.set_update_wanted(False)
wanted = vpm.update_wanted()
check("a no is remembered", wanted is False,
      "update_wanted() is %r, wanted False; the answer on disk is %r"
      % (wanted, answer_in(folder)))
offered = with_tag("v9.9.9")[0]
check("and then nothing is asked", offered == "",
      "unasked after a no: offered %r for v9.9.9, wanted ''" % (offered,))
vpm.set_update_wanted(True)
wanted = vpm.update_wanted()
check("a yes is remembered too", wanted is True,
      "update_wanted() is %r, wanted True; the answer on disk is %r"
      % (wanted, answer_in(folder)))
os.unlink(os.path.join(folder, "update_check"))
wanted = vpm.update_wanted()
check("without an answer it looks", wanted is True,
      "update_wanted() is %r with nothing remembered (%r), wanted True"
      % (wanted, answer_in(folder)))

print("\n3b. A no can be taken back")
# The trap this closes: --no-update-check given once in passing kept
# the program from ever looking again, with no switch to undo it.
import io as _io
source = _io.open(SCRIPT, encoding="utf-8").read()
TAKES_BACK = '"--update-check"'
WRITES_YES = 'if "--update-check" in rest:\n        set_update_wanted(True)'
check("there is a switch that takes it back", TAKES_BACK in source,
      "%s found %d time(s) in the %d characters of %s"
      % (TAKES_BACK, source.count(TAKES_BACK), len(source),
         os.path.basename(SCRIPT)))
check("and it writes the yes", WRITES_YES in source,
      "%r found %d time(s), while %s stands there %d time(s)"
      % (WRITES_YES, source.count(WRITES_YES), TAKES_BACK,
         source.count(TAKES_BACK)))
vpm.set_update_wanted(False)
wanted = vpm.update_wanted()
check("a no still holds for the unasked look", wanted is False,
      "update_wanted() is %r, wanted False; the answer on disk is %r"
      % (wanted, answer_in(folder)))
offered = with_tag("v9.9.9", asked=True)[0]
check("but a direct question is answered anyway", offered == "v9.9.9",
      "asked after a no: offered %r for v9.9.9, wanted 'v9.9.9'"
      % (offered,))
vpm.set_update_wanted(True)
offered = with_tag("v9.9.9")[0]
check("and the yes brings the unasked look back",
      offered == "v9.9.9",
      "unasked after a yes taken back: offered %r for v9.9.9, wanted"
      " 'v9.9.9'" % (offered,))

print("\n4. What comes back is read before it is believed")
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
text, trouble = with_body(b'\xff\xfe not text')
check("bytes that are not text are refused", not text and bool(trouble),
      "two bytes that are no utf-8 gave back %d characters of program,"
      " trouble %r" % (len(text or ""), trouble))

print("\n5. The old file is kept")
work = tempfile.mkdtemp()
mine = os.path.join(work, "videopodcast-magic.py")
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
      "videopodcast-magic.py holds %r, wanted %r" % (now, "the new one\n"))
kept = held_by(mine + ".old")
check("the old one is beside it", kept == "the one that works\n",
      "videopodcast-magic.py.old holds %r, wanted %r"
      % (kept, "the one that works\n"))

print("\nPassing over one version")
# "Do not ask again" stopped the looking for good, and a no that
# cannot be taken back is a trap. It is now "skip this version": one
# version passed over is not an answer about all of them.
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
print("\n5. The window shows one language")
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

print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
