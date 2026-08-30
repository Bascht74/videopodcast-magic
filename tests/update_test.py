# -*- coding: utf-8 -*-
"""Keeping itself up to date must not surprise anybody.

Nothing here touches the network. The one thing that does -- asking
github.com for a version number -- is replaced by a table, so the test
says something about the arithmetic rather than about the weather.
"""
import os
HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = os.environ.get("VPM_SCRIPT") or os.path.join(
    os.path.dirname(HERE), "videopodcast-magic.py")
# The suite sets this, and the module reads it while it is loading.
os.environ.pop("VPM_NO_UPDATE_CHECK", None)
import importlib.util, sys, tempfile
spec = importlib.util.spec_from_file_location("vpm", SCRIPT)
vpm = importlib.util.module_from_spec(spec); sys.modules["vpm"] = vpm
spec.loader.exec_module(vpm)

error = []
def check(name, ok, extra=""):
    print("  %-52s %s %s" % (name, "ok" if ok else "FAIL", extra))
    if not ok:
        error.append(name)

print("1. Which version is newer")
# Semantic Versioning: a finished release beats its own pre-release,
# and a name nobody understands never wins.
ORDER = [("1.0.0", "1.0.1"), ("1.9.9", "2.0.0"), ("2.0.0-beta", "2.0.0"),
         ("2.0.0-beta", "2.0.1-beta"), ("v2.0.0", "v2.1.0"),
         ("banana", "0.0.1"), ("", "0.0.1")]
for older, newer in ORDER:
    check("%r comes before %r" % (older, newer),
          vpm.version_key(older) < vpm.version_key(newer))
check("the same version is the same",
      vpm.version_key("v2.0.0-beta") == vpm.version_key("2.0.0-beta"))
check("a version does not beat itself",
      not vpm.version_key("2.0.0") < vpm.version_key("2.0.0"))

print("\n2. Only a newer release counts")
# The remembered answer belongs to whoever runs the test, not to the
# test. On 25.8.2026 this file went red on Sebastian's machine because
# he had ticked "Do not ask again" in the program: update_wanted() read
# ~/Library/Caches/videopodcast-magic/update_check and said no. A test
# that reads the environment of the person running it measures that
# person, so it gets a folder of its own here.
ANSWERS = tempfile.mkdtemp(prefix="vpm_update_")
# Over cache_folder and not over update_answer_file: section 3 takes
# the same lever, and two different ones would leave the answer in one
# folder while the test looks in the other.
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
check("a newer tag is offered", with_tag("v2.1.0")[0] == "v2.1.0")
check("the same tag is not", with_tag("v2.0.0-beta")[0] == "")
check("an older tag is not", with_tag("v1.9.0")[0] == "")

# And the remembered answer itself, now that the file is ours: a no
# holds back the unasked look and gives way to a direct question.
vpm.set_update_wanted(False)
check("a remembered no switches the unasked look off",
      not vpm.update_wanted())
check("a remembered no holds back the unasked look",
      with_tag("v2.1.0")[0] == "")
check("but a direct question is still answered",
      with_tag("v2.1.0", asked=True)[0] == "v2.1.0")
vpm.set_update_wanted(True)
check("and a yes brings it back", with_tag("v2.1.0")[0] == "v2.1.0")
check("the finished version beats the pre-release",
      with_tag("v2.0.0")[0] == "v2.0.0")
check("an unreadable tag is not offered", with_tag("nightly")[0] == "")

print("\n3. Switched off means switched off")
folder = tempfile.mkdtemp()
vpm.cache_folder = lambda sub="": folder
vpm.set_update_wanted(False)
check("a no is remembered", vpm.update_wanted() is False)
check("and then nothing is asked", with_tag("v9.9.9")[0] == "")
vpm.set_update_wanted(True)
check("a yes is remembered too", vpm.update_wanted() is True)
os.unlink(os.path.join(folder, "update_check"))
check("without an answer it looks", vpm.update_wanted() is True)

print("\n3b. A no can be taken back")
# The trap this closes: on 23.8.2026 --no-update-check had been given
# once in passing, and the program never looked again. Nothing said so,
# and there was no switch to undo it.
import io as _io
source = _io.open(SCRIPT, encoding="utf-8").read()
check("there is a switch that takes it back",
      '"--update-check"' in source and "--update-check" in source)
check("and it writes the yes",
      'if "--update-check" in rest:\n        set_update_wanted(True)'
      in source)
vpm.set_update_wanted(False)
check("a no still holds for the unasked look", vpm.update_wanted() is False)
check("but a direct question is answered anyway",
      with_tag("v9.9.9", asked=True)[0] == "v9.9.9")
vpm.set_update_wanted(True)
check("and the yes brings the unasked look back",
      vpm.update_wanted() is True)

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
check("a whole program is taken", text and not trouble)
text, trouble = with_body(b'<html>404</html>')
check("an error page is refused", not text and trouble)
# The wording is checked nowhere here: the message goes through T()
# and is German in a German run. What matters is that it is refused,
# that something is said, and that a broken file and an error page do
# not get the same answer.
text, trouble = with_body(b'VERSION = "9"\nCATALOGUE = {\n')
_, other = with_body(b'<html>404</html>')
check("something that does not compile is refused",
      not text and bool(trouble))
check("and says something else than an error page does", trouble != other)
text, trouble = with_body(b'\xff\xfe not text')
check("bytes that are not text are refused", not text and trouble)

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
check("writing works", not trouble, trouble)
check("the new one is in place",
      open(mine, encoding="utf-8").read() == "the new one\n")
check("the old one is beside it",
      open(mine + ".old", encoding="utf-8").read() == "the one that works\n")

print("\nPassing over one version")
# "Do not ask again" stopped the looking for good, and a no that cannot
# be taken back is a trap: it caught Sebastian in August, the program
# went quiet, and nothing anywhere said why. His own answer, 31.8.2026:
# turn it into "skip this version". One version passed over is not an
# answer about all of them.
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
# The suite switches the looking off for every test, which is right --
# nothing here may reach for the network. This one does not either: it
# answers every look itself. So the switch is lifted for the length of
# these checks, or newer_release would turn back at the door and every
# one of them would pass without asking anything.
vpm.UPDATE_OFF = False
vpm.VERSION = "2.15.0-beta"
try:
    urllib.request.urlopen = what_github_says("v2.19.0-beta")
    tag, _page, _text = vpm.newer_release()
    check("a newer version is offered", tag == "v2.19.0-beta", tag)

    vpm.set_update_skipped(tag)
    check("what was passed over is what was shown",
          vpm.update_skipped() == "v2.19.0-beta", vpm.update_skipped())
    tag, _p, _t = vpm.newer_release()
    check("and it is not offered again by itself", tag == "", tag)

    # The whole point of the change: the next one asks again.
    urllib.request.urlopen = what_github_says("v2.20.0-beta")
    tag, _p, _t = vpm.newer_release()
    check("but the next version is offered", tag == "v2.20.0-beta", tag)

    # Asking from the menu is a person wanting to know, and what was
    # passed over does not stand against that.
    urllib.request.urlopen = what_github_says("v2.19.0-beta")
    tag, _p, _t = vpm.newer_release(asked=True)
    check("and asking from the menu shows it anyway",
          tag == "v2.19.0-beta", tag)
finally:
    urllib.request.urlopen = was_open

print("\nAll good." if not error else "\nFAIL: %s" % ", ".join(error))
sys.exit(1 if error else 0)
