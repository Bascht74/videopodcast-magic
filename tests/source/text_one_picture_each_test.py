# -*- coding: utf-8 -*-
"""Every chapter about the window shows one picture, the two others none.

The owner's rule, read out of docs/NAME.md and docs/NAME.de.md as the
distinct pictures each shows: the chapters are there to be read; one
picture each, the German side the German form of the same one; none in
command-line and requirements; and what is owed. A chapter in OWED is
said as a LEFT OUT line until the picture pass, and is red once its
version is set in the program or stands in the changelog, or once it
keeps the rule. The README is the table of contents; overview counts.
"""
PLATFORM_BOUND = False
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
import re
import time
import the_program

began = time.time()

ROOT = os.path.dirname(HERE)
DOCS = os.path.join(ROOT, "docs")

# The two chapters the rule gives no picture: what they describe is
# typed or installed, not seen in the window.
NO_PICTURE = ("command-line", "requirements")
# The table of contents, which describes the manual and not the window.
NOT_A_CHAPTER = ("README",)
# A chapter that breaks the rule today, the version that may not go out
# before it keeps it, and what is owed. Put right at the picture pass of
# that version, then the entry goes; the run says when it has to.
OWED = {
    "interface": ("3.0.0b29",
                  "shows three pictures -- files, assignment, output; "
                  "the owner says which one the chapter keeps"),
}

# A picture as markdown writes it, and as HTML would.
SHOWN = re.compile(r"!\[[^\]]*\]\(([^)\s]+)[^)]*\)|<img[^>]*src=\"([^\"]+)\"")

done = 0
bad = []


def check(name, ok, extra=""):
    global done
    done += 1
    print("  %-58s %s %s" % (name, "ok" if ok else "FAIL", extra))
    if not ok:
        bad.append("%s [%s]" % (name, extra or "no numbers"))


def text_of(path):
    return io.open(path, encoding="utf-8").read()


def pictures(path):
    """The distinct pictures one chapter shows, by file name."""
    found = set()
    for a, b in SHOWN.findall(text_of(path)):
        found.add(os.path.basename(a or b))
    return sorted(found)


print("1. The chapters are there to be read")
names = sorted(n[:-3] for n in os.listdir(DOCS)
               if n.endswith(".md") and not n.endswith(".de.md"))
chapters = [n for n in names if n not in NOT_A_CHAPTER]
no_german = [n for n in chapters
             if not os.path.isfile(os.path.join(DOCS, n + ".de.md"))]
check("every chapter has its German side to be read", not no_german,
      "%d of %d chapters without NAME.de.md: %s"
      % (len(no_german), len(chapters), no_german))
gone = [n for n in NO_PICTURE if n not in chapters]
check("every chapter named without a picture is there", not gone,
      "%s named, not among the %d chapters %s" % (gone, len(chapters),
                                                 chapters))
gone_owed = sorted(n for n in OWED if n not in chapters)
check("every chapter on the owed list is there", not gone_owed,
      "%s owed, not among the %d chapters %s" % (gone_owed, len(chapters),
                                                 chapters))

shown = {}
for n in chapters:
    en = pictures(os.path.join(DOCS, n + ".md"))
    de_path = os.path.join(DOCS, n + ".de.md")
    de = pictures(de_path) if os.path.isfile(de_path) else []
    shown[n] = (en, de)
    print("     %-14s en %s  de %s" % (n, en or "-", de or "-"))

print("\n2. One picture each, the same one on both sides")
window = [n for n in chapters if n not in NO_PICTURE]
en_wrong = ["%s: %d %s" % (n, len(shown[n][0]), shown[n][0])
            for n in window if n not in OWED and len(shown[n][0]) != 1]
check("every chapter about the window shows exactly one picture",
      not en_wrong, "%d of %d English chapters, wanted 1 each: %s"
      % (len(en_wrong), len(window), en_wrong))
de_wrong = ["%s: %d %s" % (n, len(shown[n][1]), shown[n][1])
            for n in window if n not in OWED and len(shown[n][1]) != 1]
check("and its German side shows exactly one as well",
      not de_wrong, "%d of %d German chapters, wanted 1 each: %s"
      % (len(de_wrong), len(window), de_wrong))
unpaired = ["%s: en %s, de %s" % (n, shown[n][0], shown[n][1])
            for n in window
            if n not in OWED and len(shown[n][0]) == 1
            and len(shown[n][1]) == 1
            and (shown[n][0][0].endswith(".de.png")
                 or shown[n][1][0] != shown[n][0][0][:-4] + ".de.png")]
check("the German side shows the German form of the same picture",
      not unpaired, "wanted NAME.png in English and NAME.de.png in "
      "German: %s" % unpaired)

print("\n3. The two chapters without a picture")
pictured = ["%s: en %s, de %s" % (n, shown[n][0], shown[n][1])
            for n in NO_PICTURE if n in shown
            and (shown[n][0] or shown[n][1])]
check("the command-line and requirements chapters show no picture",
      not pictured, "wanted none on either side: %s" % pictured)

print("\n4. What is owed until the picture pass")
for n in sorted(OWED):
    print("LEFT OUT %s: owed for %s -- %s; today en %s, de %s"
          % (n, OWED[n][0], OWED[n][1],
             shown.get(n, ([], []))[0], shown.get(n, ([], []))[1]))
kept = sorted(n for n in OWED if n in shown and n not in NO_PICTURE
              and len(shown[n][0]) == 1 and len(shown[n][1]) == 1)
check("an owed chapter still breaks the rule", not kept,
      "%s keep it now -- take them off OWED" % kept)
found = re.search(r'^VERSION = "([^"]+)"', the_program.text(), re.M)
version = found.group(1) if found else ""
released = set(re.findall(r"^## \[([^\]]+)\]",
                          text_of(os.path.join(ROOT, "CHANGELOG.md")),
                          re.M))
due = sorted("%s owed for %s" % (n, v) for n, (v, _) in OWED.items()
             if v == version or v in released)
check("nothing is owed past the version it was owed for", not due,
      "the program says %r, the changelog holds %d sections; set or "
      "released already: %s" % (version, len(released), due))

print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
