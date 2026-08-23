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
def with_tag(tag):
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
        return vpm.newer_release()
    finally:
        urllib.request.urlopen = was

vpm.VERSION = "2.0.0-beta"
check("a newer tag is offered", with_tag("v2.1.0")[0] == "v2.1.0")
check("the same tag is not", with_tag("v2.0.0-beta")[0] == "")
check("an older tag is not", with_tag("v1.9.0")[0] == "")
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

print("\nAll good." if not error else "\nFAIL: %s" % ", ".join(error))
sys.exit(1 if error else 0)
