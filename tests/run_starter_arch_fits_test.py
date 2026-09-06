# -*- coding: utf-8 -*-
"""The start asks for the architecture the installed packages fit.

Reading a Mach-O header, so that a universal interpreter and a package
built for one processor can be told apart; the rule that picks one of
them, over made-up sets rather than over this machine; the cut over a
folder of packages; the entry the Dock reads, with the architecture in
it, the plain start still under it and nothing at all on a system that
cannot grant one; and the sentence a person gets where the two no
longer fit. Every architecture in here is a stand-in: six builder jobs
and one of them is an Apple Silicon Mac.
"""
import os
import shutil
import sys
import tempfile
import time

import the_program

began = time.time()
vpm = the_program.load()
vpm.set_language("en")
desktop = vpm.beside("desktop", program=vpm.PROGRAM)

done = 0
bad = []


def check(name, ok, extra=""):
    global done
    done += 1
    print("  %-58s %s %s" % (name, "ok" if ok else "FAIL", extra))
    if not ok:
        bad.append("%s [%s]" % (name, extra or "no numbers"))


# The first bytes of two real files, read off a Mac on 6.9.2026 and
# written down here: a universal interpreter, and one package built for
# one processor. They stand in for those two files, which no builder
# job outside macOS has and which no test may go looking for.
UNIVERSAL = bytes.fromhex(
    "cafebabe00000002"
    "01000007000000030000400000007e000000000e"
    "0100000c000000000000c00000010e000000000e")
ONE_ARM64 = bytes.fromhex("cffaedfe0c000001") + b"\0" * 24
ONE_X86_64 = bytes.fromhex("cffaedfe07000001") + b"\0" * 24

BOTH = set(["arm64", "x86_64"])


def a_file(folder, name, raw):
    """One file of those bytes in that folder, and its path."""
    where = os.path.join(folder, name)
    os.makedirs(os.path.dirname(where), exist_ok=True)
    with open(where, "wb") as f:
        f.write(raw)
    return where


ROOM = tempfile.mkdtemp(prefix="vpm_arch_")


print("1. What a file says about the architectures it carries")
got = desktop.architectures_of(a_file(ROOM, "interpreter", UNIVERSAL))
check("a file carrying two architectures is read as carrying both",
      got == BOTH, "%s against %s" % (sorted(got), sorted(BOTH)))

got = desktop.architectures_of(a_file(ROOM, "one.so", ONE_ARM64))
check("a package built for one processor is read as carrying that one",
      got == set(["arm64"]), "%s against ['arm64']" % sorted(got))

got = desktop.architectures_of(a_file(ROOM, "starter", b"#!/bin/sh\nexit 0\n"))
check("a file that is not a program carries no architecture at all",
      got == set(), "%s against []" % sorted(got))

got = desktop.architectures_of(os.path.join(ROOM, "was never written"))
check("a file that is not there carries no architecture either",
      got == set(), "%s against []" % sorted(got))


print("\n2. Which architecture the three of them agree on")
# The machine's own architecture is the third party and it only breaks
# a tie: it may not overrule a package that fits one thing only.
got = desktop.architecture_that_fits(BOTH, set(["arm64"]), "arm64")
check("an interpreter with two is asked for the one the packages fit",
      got == "arm64", "%r against 'arm64'" % got)

got = desktop.architecture_that_fits(BOTH, set(["x86_64"]), "arm64")
check("packages built the other way round are not overruled",
      got == "x86_64", "%r against 'x86_64'" % got)

got = desktop.architecture_that_fits(set(["x86_64"]), set(["x86_64"]),
                                     "x86_64")
check("an interpreter that carries one architecture is left alone",
      got == "", "%r against ''" % got)

got = desktop.architecture_that_fits(BOTH, BOTH, "arm64")
check("where every package fits both, the machine's own is asked for",
      got == "arm64", "%r against 'arm64'" % got)

got = desktop.architecture_that_fits(BOTH, set(), "arm64")
check("packages that agree on nothing have nothing asked for them",
      got == "", "%r against ''" % got)


print("\n3. The cut over a folder of installed packages")
mixed = os.path.join(ROOM, "packages")
a_file(mixed, os.path.join("both_ways", "_engine.so"), UNIVERSAL)
a_file(mixed, os.path.join("one_way", "_engine.so"), ONE_ARM64)
a_file(mixed, os.path.join("one_way-1.0.dist-info", "WHEEL"), b"Tag: x\n")
a_file(mixed, os.path.join("plain_text", "words.py"), b"x = 1\n")
got = desktop.installed_architectures(mixed)
check("one package fitting a single architecture settles it for all",
      got == set(["arm64"]), "%s against ['arm64']" % sorted(got))

empty = os.path.join(ROOM, "nothing")
a_file(empty, os.path.join("plain_text", "words.py"), b"x = 1\n")
got = desktop.installed_architectures(empty)
check("a folder with no compiled package settles nothing",
      got == set(), "%s against []" % sorted(got))


print("\n4. The entry the Dock reads, and where nothing is asked for")
home = os.path.join(ROOM, "home")
starter = a_file(home, os.path.join("bin", "videopodcast-magic"),
                 b"#!/bin/sh\nexit 0\n")
os.chmod(starter, 0o755)
laid = desktop.make_shortcut(root=home, target=starter, png=b"",
                             system="darwin", run_as="arm64")
stub = os.path.join(laid.where, "Contents", "MacOS", "videopodcast-magic")
with open(stub, encoding="utf-8") as f:
    runner = f.read()
asked = "%s -arm64" % desktop.ARCH_TOOL
named = [one for one in runner.splitlines() if desktop.ARCH_TOOL in one]
check("the entry asks for the architecture it was told to ask for",
      asked in runner, "wanted %r, %d line(s) name the tool: %r"
      % (asked, len(named), named[:1]))

lines = [one for one in runner.splitlines() if one.startswith("exec ")]
check("the plain start stands under it, for a machine without the tool",
      lines == ['exec "%s" "$@"' % starter],
      "%d line(s) begin with exec, the last %r"
      % (len(lines), lines[-1] if lines else ""))

points = desktop._points_at(laid.where, "darwin")
check("the starter is still read back out of an entry that asks",
      points == starter, "%s against %s" % (points, starter))

plain = desktop._stub_text(starter, "")
check("an entry that asks for nothing is written as it was before",
      desktop.ARCH_TOOL not in plain and "exec " in plain,
      "%d characters, %d of them naming the tool, %d starting a run"
      % (len(plain), plain.count(desktop.ARCH_TOOL), plain.count("exec ")))

# The guard, asked with a stand-in system and a stand-in tool: the real
# ones differ per builder job, and this claim may not.
tool = a_file(ROOM, "grants_it", b"#!/bin/sh\nexit 0\n")
os.chmod(tool, 0o755)
check("nothing at all is asked for on a system that is not macOS",
      desktop._may_ask("linux", tool) is False,
      "it said %r for linux with a tool that is there"
      % desktop._may_ask("linux", tool))

gone = os.path.join(ROOM, "no such tool")
check("and nothing where the program that grants it is not there",
      desktop._may_ask("darwin", gone) is False,
      "it said %r for darwin with no tool"
      % desktop._may_ask("darwin", gone))

check("and it is asked for where the system and the tool are both there",
      desktop._may_ask("darwin", tool) is True,
      "it said %r for darwin with a tool that is there"
      % desktop._may_ask("darwin", tool))


print("\n5. What a person is told when the two no longer fit")
# Two architectures installed, so that naming them is a different
# claim from the command underneath, which names only the first.
said = desktop.architecture_mismatch("x86_64", set(["arm64", "i386"]))
check("the sentence names the architecture the program came up as",
      "x86_64" in said, "it said %r" % said)
check("and every architecture the installed packages carry",
      "arm64" in said and "i386" in said, "it said %r" % said)
check("and a command that starts it the way that works",
      "arch -arm64 videopodcast-magic" in said, "it said %r" % said)

quiet = desktop.architecture_mismatch("arm64", BOTH)
check("nothing is said where what is running fits what is installed",
      quiet == "", "it said %r" % quiet)

quiet = desktop.architecture_mismatch("x86_64", set())
check("and nothing where no compiled package could be read at all",
      quiet == "", "it said %r" % quiet)

shutil.rmtree(ROOM, ignore_errors=True)

print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
