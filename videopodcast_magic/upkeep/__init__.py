# -*- coding: utf-8 -*-
"""Keeping itself up to date: which release is out, and pip fetching it.

A piece of the program, read in by beside(): it cannot import the file
it was cut out of, so the program is handed in and bound below by name.
"""

# Put here by beside() before this file is read.
PROGRAM = PROGRAM

# Bound above the seam. Three names are missing, and the three blocks
# under the list say which and why.

T = PROGRAM.T
VERSION = PROGRAM.VERSION
cache_folder = PROGRAM.cache_folder
https_context = PROGRAM.https_context
installed_by_a_package_manager = PROGRAM.installed_by_a_package_manager
json = PROGRAM.json
os = PROGRAM.os
re = PROGRAM.re
subprocess = PROGRAM.subprocess
sys = PROGRAM.sys
write_through = PROGRAM.write_through

# UPDATE_SINK is the first: the window sets it on the program object,
# and that write reaches no piece, so a copy here would answer None for
# ever. Read as PROGRAM.UPDATE_SINK at the moment pip is handed over.

# LANG is the second: set_language() rebinds it as a global of the way
# in, so the release text asks PROGRAM.LANG at the moment it cuts.

# __file__ is the third and cannot be bound: in here it names this
# file, while start_again below means the program.

# Looking for a newer release is free and always happens; only
# VPM_NO_UPDATE_CHECK stops it. Fetching is asked every single time and
# never during a run, and pip is the only way -- this is a folder.


RELEASES = ("https://api.github.com/repos/Bascht74/videopodcast-magic"
            "/releases/latest")
# The whole list: whoever skipped two releases wants to read all three.
RELEASE_LIST = ("https://api.github.com/repos/Bascht74/videopodcast-magic"
                "/releases?per_page=30")
# Off for a test run: no network, and no swapping the file under test.
UPDATE_OFF = bool(os.environ.get("VPM_NO_UPDATE_CHECK"))
# What pip is pointed at where the program was installed rather than
# downloaded. No PyPI in it: pip reads the repository itself, and
# pip_update hangs the release on the end.
PIP_SOURCE = "git+https://github.com/Bascht74/videopodcast-magic"

# How far back the way back reaches. Below v3.0.0b0 the repository is
# no package at all -- v2.32.0-beta has neither pyproject.toml nor
# setup.py. Twenty, because a longer list is no longer a choice.
OLDEST_TO_GO_BACK_TO = "v3.0.0b0"
MOST_TO_GO_BACK_TO = 20


#--------------------------------------------------- What was chosen once


def update_skip_file():
    """Where the version somebody chose to pass over is kept."""
    folder = cache_folder()
    return os.path.join(folder, "update_skip") if folder else ""


def update_skipped():
    """The version somebody chose to pass over, or "" for none."""
    where = update_skip_file()
    if not where or not os.path.exists(where):
        return ""
    try:
        with open(where, encoding="utf-8") as f:
            return f.read().strip()
    except OSError:
        return ""


def set_update_skipped(tag):
    """Pass over this one version. The next one asks again.

    In place of "do not ask again", which stopped the looking for good:
    a no that cannot be taken back is a trap. One version passed over
    is not an answer about all of them.
    """
    where = update_skip_file()
    if not where:
        return
    try:
        with open(where, "w", encoding="utf-8") as f:
            f.write(str(tag or ""))
    except OSError:
        return


def updated_from_file():
    """Where the version the last install left behind is kept."""
    folder = cache_folder()
    return os.path.join(folder, "updated_from") if folder else ""


def updated_from():
    """The version that was running before the last install, or "".

    Whoever goes looking for the way back has nearly every time just
    been moved off that version, so it is what the list opens on. A
    guess: it is the entry picked out, never the only one on offer.
    """
    where = updated_from_file()
    if not where or not os.path.exists(where):
        return ""
    try:
        with open(where, encoding="utf-8") as f:
            return f.read().strip()
    except OSError:
        return ""


def set_updated_from(tag):
    """Note the version an install that went through left behind."""
    where = updated_from_file()
    if not where:
        return
    try:
        with open(where, "w", encoding="utf-8") as f:
            f.write(str(tag or ""))
    except OSError:
        return


#----------------------------- What a version is, and what a release says

# PEP 440 hangs the pre-release straight on the numbers, with no dash:
# a1 alpha, b0 beta, rc1 candidate. Without a number, the zeroth.
PIP_PRE_RELEASE = re.compile(r"^(\d+(?:\.\d+)*)(a|b|rc)(\d*)$")


def pre_release_key(pre):
    """The name of a pre-release, cut so that ten comes after nine.

    Runs of digits and runs of everything else, each run of digits as
    the number it is. The 0 and the 1 in front keep the two kinds
    apart: b9 falls under b10, and beta.2 under beta.10.
    """
    return tuple((0, int(run)) if run.isdigit() else (1, run)
                 for run in re.findall(r"\d+|\D+", pre))


def version_key(text):
    """A version as something that can be compared.

    Two spellings and one order: 2.0.0-beta the way the tags read, and
    3.0.0b0 the way pip writes it. Both are older than the bare numbers,
    as both standards say. Anything unreadable sorts oldest, never newer.
    """
    text = str(text or "").strip().lstrip("vV")
    core, _, pre = text.partition("-")
    hung_on = None if pre else PIP_PRE_RELEASE.match(core)
    if hung_on:
        core = hung_on.group(1)
        pre = hung_on.group(2) + (hung_on.group(3) or "0")
    numbers = []
    for piece in core.split(".")[:3]:
        numbers.append(int(piece) if piece.isdigit() else 0)
    while len(numbers) < 3:
        numbers.append(0)
    # 1 for a finished release, 0 for a pre-release: 2.0.0 after 2.0.0-beta.
    return (tuple(numbers), 1 if not pre else 0, pre_release_key(pre))


MARK_DE = "**Deutsch**"

# What separates the two halves of a release text: the English part
# first, the German under this line. The changelog writes them, the
# window looks for them, and the release test insists on them.
MARK_EN = "**English**"


def release_text_in(text, language=None):
    """Keep the half of a release text that is in this language.

    A release says everything twice, in two blocks one under the other:
    English first, German under a line of its own. Both belong on the
    release page; in the window only one is wanted. Given away only
    where the mark is there -- half a text is worse than a wrong one.
    """
    lines = str(text or "").split("\n")
    at = [i for i, x in enumerate(lines) if x.strip() == MARK_DE]
    if not at:
        return text
    if (language or PROGRAM.LANG) == "de":
        kept = lines[at[0] + 1:]
    else:
        kept = lines[:at[0]]
        # The rule that draws the line between them goes with it.
        while kept and kept[-1].strip() in ("", "---", "***", "___"):
            kept.pop()
    return "\n".join(x for x in kept
                      if x.strip() not in (MARK_EN, MARK_DE)).strip()


#------------------------------------------------------ What is out there


def releases_in_between(newest, running):
    """The release texts from *running* up to *newest*, newest first.

    GitHub answers with the whole list, so the versions in between cost
    one more request. Returns "" where the list cannot be had, and the
    caller then keeps the text it has: a failure here must never be
    worse than not asking at all.
    """
    try:
        import urllib.request
        with urllib.request.urlopen(RELEASE_LIST, context=https_context(),
                                    timeout=20) as answer:
            found = json.load(answer)
    except Exception:
        return ""
    if not isinstance(found, list):
        return ""
    want = []
    for one in found:
        if not isinstance(one, dict) or one.get("draft"):
            continue
        tag = str(one.get("tag_name") or "")
        if not tag:
            continue
        # Strictly between: the newest is in hand, the running one is had.
        if version_key(running) < version_key(tag) <= version_key(newest):
            want.append((version_key(tag), tag,
                         str(one.get("body") or "").strip()))
    want.sort(reverse=True)
    # Cut to the language here rather than where it is shown, because
    # two windows show this text and both must cut it the same way.
    return "\n\n".join("## %s\n\n%s" % (tag, release_text_in(body))
                        for _k, tag, body in want if body)


def older_releases(running):
    """The versions to go back to, newest first, and why not: (list, "").

    Older than *running* and never *running* itself, none below
    OLDEST_TO_GO_BACK_TO, at most MOST_TO_GO_BACK_TO of them. An empty
    list alone means there is nothing older; an empty list with a
    sentence means nobody knows, and the two must not read alike. The
    address answers with the newest thirty releases and no more.
    """
    try:
        import urllib.request
        with urllib.request.urlopen(RELEASE_LIST, context=https_context(),
                                    timeout=20) as answer:
            found = json.load(answer)
    except Exception as e:
        return [], T('Could not look for earlier versions: %s') % e
    if not isinstance(found, list):
        return [], T('The list of earlier versions could not be read.')
    floor, here = version_key(OLDEST_TO_GO_BACK_TO), version_key(running)
    want = []
    for one in found:
        if not isinstance(one, dict) or one.get("draft"):
            continue
        tag = str(one.get("tag_name") or "")
        if not tag:
            continue
        if floor <= version_key(tag) < here:
            want.append((version_key(tag), tag))
    want.sort(reverse=True)
    return [tag for _key, tag in want[:MOST_TO_GO_BACK_TO]], ""


def back_pick(older):
    """Which of *older* the way back is opened on, or "" for none.

    The version the last install left behind where it is still on
    offer, otherwise the newest. Held by version_key and not as text:
    VERSION reads 3.0.0b4 where the release carrying it is v3.0.0b4.
    """
    was = updated_from()
    if was:
        for tag in older:
            if version_key(tag) == version_key(was):
                return tag
    return older[0] if older else ""


def newer_release(asked=False):
    """(tag, page, what changed, trouble) of a newer release.

    All four are "" where nothing newer was found. *trouble* carries a
    sentence where the looking itself could not happen -- no network,
    an unreadable certificate store -- and must not read as "nothing
    newer". A pre-release is never the answer. The release text comes
    with it. *asked* is a direct question; VPM_NO_UPDATE_CHECK beats it.
    """
    if UPDATE_OFF:
        return "", "", "", ""
    passed_over = "" if asked else update_skipped()
    try:
        import urllib.request
        with urllib.request.urlopen(RELEASES, context=https_context(),
                                    timeout=20) as answer:
            found = json.load(answer)
    except Exception as e:
        # Said, not swallowed; whoever did not ask is not told.
        return "", "", "", (T('Could not look for a newer version: %s')
                            % e if asked else "")
    tag = str(found.get("tag_name") or "")
    if passed_over and tag == passed_over:
        # Passed over once, so it is not offered again by itself. The
        # next release has another name and asks, and the menu asks too.
        return "", "", "", ""
    if not tag or version_key(tag) <= version_key(VERSION):
        # Nothing newer. The answer still carries the text of the release
        # that is running, so nobody has to open a browser to read what
        # they have. The tag comes back empty.
        same = version_key(tag) == version_key(VERSION) if tag else False
        return ("", str(found.get("html_url") or "") if same else "",
                str(found.get("body") or "").strip() if same else "", "")
    text = str(found.get("body") or "").strip()
    # Two versions may lie between; the newest alone hides the rest.
    whole = releases_in_between(tag, VERSION)
    return (tag, str(found.get("html_url") or ""), whole or text, "")


#-------------------------------------------- Letting pip put it in place


def not_installed_note():
    """The one sentence for "pip has nothing here to update".

    One place, so the window and the console cannot say two different
    things. pip is the only way in and the only way on; a copy in a
    folder of its own is no version pip keeps a record of.
    """
    return T('This copy runs out of a folder of its own, so pip has '
             'nothing here to update. This installs it: %s') % (
                 "pip3 install -U " + PIP_SOURCE)


def pip_update(tag, say):
    """Let pip put that release in place. "" when it worked, or why not.

    The one road, forwards and backwards alike: a direct git address
    tells pip to install what the address names rather than only to
    climb. pip's lines go on as they arrive -- silence looks broken.
    """
    order = [sys.executable, "-m", "pip", "install", "-U",
             PIP_SOURCE + "@" + tag]
    say("  %s\n" % " ".join(order))
    try:
        started = subprocess.Popen(order, stdout=subprocess.PIPE,
                                   stderr=subprocess.STDOUT)
    except OSError as e:
        return T('pip could not be started: %s') % e
    for line in started.stdout:
        say(line.decode("utf-8", "replace"))
    code = started.wait()
    if code:
        return T('pip stopped with %s. What it managed stands in the '
                 'lines above.') % code
    # Written only where pip went through, and it is what was running
    # until this moment: the way back opens on it.
    set_updated_from(VERSION)
    say(T('%s is installed. It runs from the next start.') % tag + "\n")
    return ""


def update_promise(owner):
    """What the window says it will do before it asks.

    Two different things happen, so two sentences are owed. *owner* is
    the folder a package manager installed this into; where there is
    none there is nothing pip keeps a record of, and it says so first.
    """
    if owner:
        return T('Update? pip fetches it into %s. What pip says appears '
                 'under Output, and the new version runs from the next '
                 'start.') % owner
    return not_installed_note()


def update_fetched(tag, owner):
    """Hand that release to pip. "" where it is under way, or why not.

    pip is the only way in and therefore the only way on: it keeps the
    record of which version is installed, and this program is a whole
    folder. pip takes minutes, so the window runs it beside itself.
    """
    if not owner:
        return not_installed_note()
    if PROGRAM.UPDATE_SINK is None:
        return T('There is no window to show what pip says.')
    PROGRAM.UPDATE_SINK(lambda say: pip_update(tag, say))
    return ""


def update_note():
    """Say on the command line that a newer version is out.

    A line and nothing else. A run started out of a script must not
    stop to ask, so there is no box and nothing is fetched. The second
    line names the way that works here.
    """
    tag, page, _changed, _trouble = newer_release()
    if not tag:
        return
    print(T('%s is out. This is %s.') % (tag, VERSION))
    if installed_by_a_package_manager():
        print(T('--update fetches it and puts it in place.'))
    else:
        print(not_installed_note())
    if page:
        print("  %s" % page)


def update_from_command_line():
    """Let pip fetch the newer version. 0, or 1 with a word.

    Asked for outright, so a version passed over does not stand against
    it. The same machinery as the window's button; what differs is
    where pip's lines go. Nothing is started again afterwards.
    """
    if UPDATE_OFF:
        print(T('The check for new versions is switched off here.'))
        return 1
    tag, _page, _changed, trouble = newer_release(asked=True)
    if trouble:
        print(trouble)
        return 1
    if not tag:
        print(T('No newer version found. This one is %s.') % VERSION)
        return 0
    if not installed_by_a_package_manager():
        print(not_installed_note())
        return 1
    # Whoever typed --update has a console, so pip writes into it as it
    # goes -- write_through is to this what UPDATE_SINK is to the window.
    # pip's first install fetches a gigabyte; silence looks like a hang.
    trouble = pip_update(tag, write_through)
    if trouble:
        print(trouble)
        return 1
    return 0


def start_again():
    """Start this program once more, in place of this run."""
    here = os.path.abspath(PROGRAM.__file__)
    try:
        sys.stdout.flush()
        os.execv(sys.executable, [sys.executable, here] + sys.argv[1:])
    except OSError as e:
        print(T('Starting again did not work: %s') % e)
        print(T('Start it by hand: %s %s') % (sys.executable, here))
