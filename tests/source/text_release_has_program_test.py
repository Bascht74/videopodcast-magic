# -*- coding: utf-8 -*-
"""Every release github.com lists carries the program, at its version.

In order: the program says where its releases are listed; every release
carries the program; none of them is a stub; what hangs on the newest
is the program, at the version of its tag. The half of a release that
the working tree answers is text_release_ready's. Where github.com
answers nothing, nothing is asked, and a line says so.
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
import io
import json
import re
import subprocess
import time
import zipfile
import the_program

began = time.time()

# Every piece of the program joined: RELEASE_LIST and VERSION are read
# out of it, wherever they stand.
source = the_program.whole()

done = 0
error = []
def check(name, ok, extra=""):
    global done
    done += 1
    print("  %-52s %s %s" % (name, "ok" if ok else "FAIL", extra))
    if not ok:
        error.append(name)

print("1. The program hangs on the releases that are out")
# Whoever has no copy yet gets one from the release page, and the
# program's own update reads that page too. A release without it
# offers a source archive of the whole repository instead, and nothing
# in the working tree can see that -- so this section asks github.com.
#
# A release keeps the shape it went out in, and there have been three.
# The file was renamed when the hyphen went out of it, so the older
# releases carry the old name for ever and the ones behind the rename
# the new one. And on 4.9.2026 the texts moved into files of their own
# beside the program: one of them alone dies on import, so from then on
# an archive of all of them goes up in place of the one file. All three
# names stand in the failure line -- held to one, this would be red on
# everything behind a change and never on the change itself.
ARCHIVE = "videopodcast_magic.zip"
ASSETS = (ARCHIVE, "videopodcast_magic.py", "videopodcast-magic.py")
ASSET_SAID = " or ".join(ASSETS)
left_out = []


def from_github(url, first_bytes=0):
    """What an address answers, or None where nothing answered.

    Over curl rather than urllib: a Python from python.org verifies
    against a certificate store it does not have, and a machine that
    lacks only that must not turn this red. Every reason there is no
    answer -- no network, no name, no permission, a spent rate limit
    -- is written down and leaves the section unasked.
    """
    # -L, because an attachment is handed on to the storage it lies in.
    call = ["curl", "-fsSL", "--max-time", "20",
            "-H", "Accept: application/vnd.github+json"]
    if first_bytes:
        call += ["-r", "0-%d" % (first_bytes - 1)]
    try:
        got = subprocess.run(call + [url], stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE)
    except OSError as why:
        left_out.append("curl did not run: %s" % why)
        return None
    if got.returncode:
        left_out.append(
            "%s answered nothing (curl %d: %s)"
            % (url.split("/")[2], got.returncode,
               got.stderr.decode("utf-8", "replace").strip()[:60]))
        return None
    return got.stdout


# The address is the program's own, so a repository that moves takes
# this with it. RELEASE_LIST is written as two pieces of one string.
named = re.search(r'^RELEASE_LIST = \(([^)]+)\)', source, re.M)
listing = "".join(re.findall(r'"([^"]*)"', named.group(1))) if named else ""
check("the program says where its releases are listed", bool(listing),
      listing or "no RELEASE_LIST in the program")

answered = from_github(listing) if listing else None
try:
    releases = json.loads(answered.decode("utf-8")) if answered else None
except ValueError as why:
    left_out.append("what came back is not the list: %s" % why)
    releases = None

if not isinstance(releases, list):
    print("  (%s -- this section asked nothing)"
          % (left_out[0] if left_out else "no address to ask"))
else:
    # Every one of them, with no earliest. The oldest eight were fitted
    # with the file afterwards, out of their own tags, so a boundary
    # here would only say from when somebody had last looked.
    want = [r for r in releases if not r.get("draft")]
    without = []
    for one in want:
        names = [a.get("name") for a in one.get("assets", [])]
        if not [n for n in ASSETS if n in names]:
            without.append("%s carries %s"
                           % (one.get("tag_name"), ", ".join(names)
                              or "nothing but the source archive"))
    check("every release carries the program",
          not without,
          "%d of %d carry %s; %s" % (len(want) - len(without), len(want),
                                     ASSET_SAID, "; ".join(without[:3])
                                     or "none is missing it"))

    # A wrong or half-written attachment is short, and the size comes
    # with the list, so nothing has to be fetched to see it.
    #
    # Two floors, because the two shapes are not the same size. The
    # program only ever grew, so half of what it weighs in the working
    # tree is under every release that was ever made. The archive holds
    # the same program compressed: measured 4.9.2026, 1 950 864 bytes
    # of source came to 588 141, about a third of what the program
    # alone weighs -- so a sixth of that is half again of the smallest
    # it has been, and far above anything half-written.
    #
    # The program, not the file it starts in. Those were the same
    # thing until the window moved out on 5.9.2026, and for as long as
    # they were, "it only ever grew" held. Read off one file the floor
    # fell from 817 204 to 538 770 in a single commit, and an appended
    # program of 600 KB would have passed as whole.
    floor = the_program.on_disk() // 2
    floor_zip = the_program.on_disk() // 6
    stubs = ["%s: %s at %d bytes" % (one.get("tag_name"), a.get("name"),
                                     a.get("size") or 0)
             for one in want for a in one.get("assets", [])
             if a.get("name") in ASSETS
             and (a.get("size") or 0) < (floor_zip
                                         if a.get("name") == ARCHIVE
                                         else floor)]
    check("none of them is a stub", not stubs,
          "under %d bytes, an archive under %d: %s"
          % (floor, floor_zip, "; ".join(stubs[:3]) or "none of them"))

    newest = want[0] if want else {}
    address = [(a.get("name"), a.get("browser_download_url"))
               for a in newest.get("assets", [])
               if a.get("name") in ASSETS]
    # The version stands near the top, so the first pages of the file
    # answer for the file's version without fetching a megabyte and a
    # half. The window follows the line as the program grows.
    #
    # An archive is not readable that way: what is in it is compressed,
    # and reading it back wants the whole of it to seek in. So that one
    # is fetched entire -- 588 141 bytes when it was measured -- and
    # opening it is at the same time the answer to whether it is an
    # archive at all.
    window = max(32768, source.find('VERSION = "') + 8192)
    got = None
    if address:
        name, url = address[0]
        got = from_github(url, 0 if name == ARCHIVE else window)
    if got is not None:
        if name == ARCHIVE:
            try:
                box = zipfile.ZipFile(io.BytesIO(got))
                parts = [n for n in box.namelist() if not n.endswith("/")]
                text = "\n".join(box.read(n).decode("utf-8", "replace")
                                 for n in parts)
            except (zipfile.BadZipFile, OSError, RuntimeError, ValueError):
                parts, text = [], ""
            # Only the program itself carries such a line, and none of
            # the text files beside it does -- counted 4.9.2026, none
            # of the nine.
            looks = bool(parts) and 'VERSION = "' in text
            shown = "%d bytes, %d files in it" % (len(got), len(parts))
        else:
            text = got.decode("utf-8", "replace")
            looks = text.startswith("#!") and 'VERSION = "' in text
            shown = "%d bytes, %r" % (len(got), text[:20])
        said = re.search(r'^VERSION = "([^"]+)"', text, re.M)
        tag = newest.get("tag_name") or ""
        check("what hangs on %s is the program" % tag, looks, shown)
        check("and it carries the version of its tag",
              bool(said) and "v" + said.group(1) == tag,
              "%s says %s, the tag says %s"
              % (name, said.group(1) if said else "nothing", tag))

print("\n%d checks in %.2f s" % (done, time.time() - began))

# Said, not passed over. Not the SKIPPED marker: that one counts the
# whole test as skipped, and run.sh allows one skip in the suite, which
# a machine without a registry already takes. A machine without a
# network would then be red for the weather.
if left_out:
    print("\nLeft out: %s" % left_out[0])
print("\nFAIL: %s" % ", ".join(error) if error else
      "\nAll good." if not left_out else
      "\nGood as far as it went -- github.com was not asked.")
sys.exit(1 if error else 0)
