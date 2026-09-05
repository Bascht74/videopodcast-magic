# -*- coding: utf-8 -*-
"""Going back to an earlier version is offered, and never into a dead end.

Nothing here touches the network and nothing here starts pip: the list
of releases is answered from a table and pip is a stand-in that refuses
a command whose first word is no program, so a wrong call cannot come
back looking like a good one. The way out is nailed shut at the top.

The sections: which earlier versions are put on offer and which are
kept off it, which one the offer opens on, and what is handed to pip
when somebody takes it.
"""
import os
import the_program
HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = the_program.SCRIPT
# The suite sets this, and the module reads it while it is loading.
os.environ.pop("VPM_NO_UPDATE_CHECK", None)
import json, subprocess, sys, tempfile, time
import urllib.request
began = time.time()
vpm = the_program.load()

WENT_OUT = []


def no_network(url, *rest, **more):
    """Refuse every look and write down where it wanted to go."""
    WENT_OUT.append(str(getattr(url, "full_url", url)))
    raise IOError("this test asks github.com nothing")


# Nailed shut here rather than trusting VPM_NO_UPDATE_CHECK: the point
# of this whole file is that the looking happens, so the switch that
# stops it cannot be what keeps this test at home.
urllib.request.urlopen = no_network

done = 0
bad = []


def check(name, ok, extra=""):
    global done
    done += 1
    print("  %-58s %s %s" % (name, "ok" if ok else "FAIL", extra))
    if not ok:
        bad.append("%s [%s]" % (name, extra or "no numbers"))


def fresh_cache(what):
    """A cache folder of its own, so nothing a run before it left counts."""
    os.environ["VPM_CACHE"] = tempfile.mkdtemp(prefix="vpm_back_%s_" % what)


fresh_cache("start")

print("1. Which earlier versions are put on offer")
# Thirty releases, five of them from before the repository was a package
# at all. Handed over shuffled rather than sorted: a list that arrives
# in order lets a program that never sorts look right.
UNDER_THE_FLOOR = ["v2.28.0-beta", "v2.29.0-beta", "v2.30.0-beta",
                   "v2.31.0-beta", "v2.32.0-beta"]
ON_OFFER = (["v3.0.0b%d" % n for n in range(5)]
            + ["v3.%d.0" % n for n in range(20)])
THIRTY = sorted(UNDER_THE_FLOOR + ON_OFFER)
RUNNING = "v3.20.0"
# Written out rather than worked out: the newest twenty of the
# twenty-five pip could install, newest first. The five pre-releases of
# 3.0.0 fall off the end, v3.10.0 stands above v3.9.0 and not under it.
TWENTY = ["v3.19.0", "v3.18.0", "v3.17.0", "v3.16.0", "v3.15.0",
          "v3.14.0", "v3.13.0", "v3.12.0", "v3.11.0", "v3.10.0",
          "v3.9.0", "v3.8.0", "v3.7.0", "v3.6.0", "v3.5.0", "v3.4.0",
          "v3.3.0", "v3.2.0", "v3.1.0", "v3.0.0"]
ASKED = []


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


def the_releases(url, *rest, **more):
    """Answer the list of releases, and nothing else that is asked for.

    Stricter than github on purpose: a stand-in that hands back
    whatever address it is given proves nothing about which address the
    program went to, and a check on the tags it got back would stay
    green while the program asked somewhere else entirely.
    """
    where = str(getattr(url, "full_url", url))
    ASKED.append(where)
    if where != vpm.RELEASE_LIST:
        raise IOError("nothing but the list of releases is answered here")
    return Said(json.dumps([{"tag_name": t} for t in THIRTY]).encode("utf-8"))


def with_releases(what):
    """Run *what* with the release list answered, and undo it after."""
    was = urllib.request.urlopen
    urllib.request.urlopen = the_releases
    try:
        return what()
    finally:
        urllib.request.urlopen = was


older, trouble = with_releases(lambda: vpm.older_releases(RUNNING))
check("exactly twenty earlier versions are put on offer",
      len(older) == 20 and not trouble,
      "%d of the %d releases came back, %d of them installable, and the "
      "trouble was %r" % (len(older), len(THIRTY), len(ON_OFFER), trouble))
# Asked again from low down, and that is the point: with twenty-five
# above the floor the cap alone keeps the five below it out, and this
# judgement would be green with no floor in the program at all. From
# v3.0.0b3 only three stand above the floor, so a floor that stopped
# holding shows itself here.
DEEP = "v3.0.0b3"
THREE = ["v3.0.0b2", "v3.0.0b1", "v3.0.0b0"]
low, _said = with_releases(lambda: vpm.older_releases(DEEP))
check("no version from before the repository was a package is offered",
      low == THREE,
      "asked from %s, %d came back -- %r -- and %r was wanted; %d of "
      "them are below %s"
      % (DEEP, len(low), low[:6], THREE,
         len([t for t in low if t in UNDER_THE_FLOOR]),
         vpm.OLDEST_TO_GO_BACK_TO))
check("the twenty are the newest that pip could install, newest first",
      older == TWENTY,
      "got %r ... %r, wanted %r ... %r"
      % (older[:3], older[-2:], TWENTY[:3], TWENTY[-2:]))
# pip does nothing at all when it is handed the version that is already
# installed, and says nothing about it either -- measured. So the list
# must never be able to name it.
same, _trouble = with_releases(lambda: vpm.older_releases("v3.5.0"))
check("the version that is running is never offered as the way back",
      "v3.5.0" not in same and same[:1] == ["v3.4.0"],
      "asked while v3.5.0 runs, the offer began %r and held v3.5.0 %d "
      "time(s)" % (same[:2], same.count("v3.5.0")))
# An empty list and a sentence beside it are two different answers, and
# reading the second as the first tells somebody there is no way back
# when in truth nobody could look. A refusal of its own, not the one at
# the top of this file: that one is the net under the whole run, and a
# look it caught would have to count as a look that got out.
def no_route(url, *rest, **more):
    """A machine that cannot reach github.com at all."""
    raise IOError("no route to github.com")


def with_no_route(what):
    was = urllib.request.urlopen
    urllib.request.urlopen = no_route
    try:
        return what()
    finally:
        urllib.request.urlopen = was


blind, said = with_no_route(lambda: vpm.older_releases(RUNNING))
check("a look that could not happen says so instead of saying nothing "
      "is older", blind == [] and bool(said),
      "%d versions came back with the trouble %r" % (len(blind), said))

print("\n2. What the offer opens on")
# What the program writes down as it installs, and what it makes of it
# afterwards. The two are apart on purpose: the note is written in one
# place and read in another, and either half can go without the other.
ORDERS = []
GOT = []
PIP_SAYS = [b"Collecting videopodcast-magic\n",
            b"Successfully installed videopodcast-magic-3.0.0b4\n"]
PIP_CODE = [0]


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
        self.stdout = iter(PIP_SAYS)

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


fresh_cache("through")
before = vpm.updated_from()
with_pip(lambda: vpm.pip_update("v3.12.0", GOT.append))
noted = vpm.updated_from()
check("an install that went through notes the version it left behind",
      before == "" and noted == vpm.VERSION,
      "the note held %r before and %r after an install of v3.12.0, "
      "wanted '' and %r" % (before, noted, vpm.VERSION))
fresh_cache("stopped")
PIP_CODE[0] = 3
del GOT[:], ORDERS[:]
with_pip(lambda: vpm.pip_update("v3.12.0", GOT.append))
check("an install that stopped part way notes nothing",
      vpm.updated_from() == "",
      "pip returned 3 and the note held %r, wanted ''"
      % (vpm.updated_from(),))
PIP_CODE[0] = 0

# The note is what the offer opens on, because whoever wants the way
# back has nearly always just been moved off that one version. Asked of
# the note the install above really wrote and not of one put there by
# hand: the program writes its own VERSION, 3.0.0b4, while the release
# carrying it is tagged v3.0.0b4, and a note held against the tags as
# text would never match one.
fresh_cache("pick")
with_pip(lambda: vpm.pip_update("v3.12.0", GOT.append))
# Asked from v3.2.0 rather than from v3.20.0 on purpose: from there the
# version just left behind is the third on offer and not the first, so
# an offer that simply opened on the newest would not pass for one that
# read the note.
seven, _said = with_releases(lambda: vpm.older_releases("v3.2.0"))
check("the offer opens on the version the last install left behind",
      vpm.back_pick(seven) == "v" + vpm.VERSION,
      "the install left %r behind, the %d on offer are %r, the newest "
      "of them is %r, and the offer opened on %r"
      % (vpm.updated_from(), len(seven), seven[:4],
         seven[0] if seven else None, vpm.back_pick(seven)))
fresh_cache("nopick")
check("and on the newest of them where nothing was noted",
      vpm.back_pick(older) == "v3.19.0",
      "with no note the offer opened on %r, wanted 'v3.19.0'"
      % (vpm.back_pick(older),))
fresh_cache("stale")
vpm.set_updated_from("v2.30.0-beta")
check("a note naming a version nobody may install does not take the "
      "choice with it", vpm.back_pick(older) == "v3.19.0",
      "the note held 'v2.30.0-beta', which is not among the %d on "
      "offer, and the offer opened on %r"
      % (len(older), vpm.back_pick(older)))

print("\n3. What is handed to pip")
# The whole road the window takes: the version that was chosen goes to
# update_fetched, which hands the window a job, and the job starts pip.
CHOSEN = "v3.12.0"
check("the version chosen below is one the offer really holds",
      CHOSEN in older, "%r among %r ... %r" % (CHOSEN, older[:2], older[-2:]))
JOBS = []
del GOT[:], ORDERS[:]
was_sink = vpm.UPDATE_SINK
try:
    vpm.UPDATE_SINK = JOBS.append
    answered = vpm.update_fetched(CHOSEN, "/some/folder/pip/owns")
finally:
    vpm.UPDATE_SINK = was_sink
if JOBS:
    with_pip(lambda: JOBS[0](GOT.append))
# The command itself, not the sentence beside it: the address without a
# release hung on it is the head of the default branch, and pip sent
# there climbs forward again instead of going back.
AT_RELEASE = vpm.PIP_SOURCE + "@" + CHOSEN
check("pip is asked for the version that was chosen, not for a branch",
      answered == "" and bool(ORDERS) and ORDERS[0][5:] == [AT_RELEASE],
      "update_fetched said %r and pip was pointed at %r, wanted '' and "
      "the one address %r"
      % (answered, ORDERS[0][5:] if ORDERS else None, AT_RELEASE))
IN_PLACE = vpm.T('%s is installed. It runs from the next start.') % CHOSEN
check("and the version that was chosen is the one reported in place",
      IN_PLACE in "".join(GOT),
      "the window was handed %r, wanted %r in it"
      % ("".join(GOT)[-60:], IN_PLACE))

STRAY = [a for a in ASKED if a != vpm.RELEASE_LIST]
check("nothing but the list of releases was ever asked for", not STRAY,
      "of the %d addresses asked for, %d go elsewhere: %r"
      % (len(ASKED), len(STRAY), STRAY[:2]))
check("no look in this whole run left the machine", not WENT_OUT,
      "%d addresses got past the stand-ins, the first of them %s"
      % (len(WENT_OUT), WENT_OUT[0] if WENT_OUT else "none"))

print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
