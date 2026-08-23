#!/usr/bin/env python3
"""Fetch videopodcast-magic and everything it cannot fetch itself.

One file for every system. Python has to be there anyway -- it is the
program's only hard requirement -- so the installer is written in it
rather than as a shell script per system, and macOS, Windows and Linux
read the same instructions.

    python3 install.py              into ./videopodcast-magic
    python3 install.py --to PATH    somewhere else
    python3 install.py --check      hold what is there against the sums
    python3 install.py --packages   fetch numpy and PySide6 as well
    python3 install.py --from PATH  out of a folder instead of the net
    python3 install.py --no-start   fetch it, do not start it

What it brings:

  videopodcast-magic.py    the program, one file
  models/...               the speaker separation model, five files

The model is the reason this installer exists. The program never
fetches it: it is loaded from a folder beside the script, without a
Hugging Face account, without a token and without a network. That makes
the separation work on a machine that has none of those -- and it means
somebody who downloads the one file alone ends up without it.

Every downloaded file is held against the SHA-256 sums that come with
the model. A file that does not match is not written.
"""

import argparse
import hashlib
import os
import ssl
import subprocess
import sys
import urllib.error
import urllib.request

RAW = "https://raw.githubusercontent.com/Bascht74/videopodcast-magic"
PROGRAM = "videopodcast-magic.py"
MODEL = "models/speaker-diarization-community-1"
SUMS = MODEL + "/SHA256SUMS.txt"
# Beside the weights: what the licence asks to be passed on with them.
PAPERS = [MODEL + "/" + n for n in ("LICENSE-CC-BY-4.0.txt",
                                    "MODEL_CARD.md", "NOTICE.md")]
NEEDS_PYTHON = (3, 10)
LIKES_PYTHON = "3.14.7"


def say(text=""):
    """Print and flush: a download in between must not sit in a buffer."""
    print(text)
    sys.stdout.flush()


def context():
    """An SSL context that also works on a Python without certificates.

    A Python from python.org brings none of its own, and every download
    then fails with CERTIFICATE_VERIFY_FAILED. certifi is the bundle;
    it is fetched over pip if it is not there. The program does the
    same thing for the same reason, and this is the same solution: no
    unverified connection, ever.
    """
    try:
        import certifi
    except ImportError:
        certifi = None
    if certifi is None:
        return ssl.create_default_context()
    return ssl.create_default_context(cafile=certifi.where())


def with_certificates():
    """Fetch certifi once, after a verification has failed."""
    say("  The certificates are missing -- fetching certifi.")
    ok = pip_install("certifi")
    if not ok:
        say("  certifi could not be installed. On a Mac, running")
        say("  'Install Certificates.command' in the Python folder does")
        say("  the same thing.")
    return ok


def pip_install(*packages):
    """Run pip, going the polite way first.

    The same order the program uses: plain, then --user, then each of
    them again allowed to write past an externally managed
    installation.
    """
    for extra in ([], ["--user"], ["--break-system-packages"],
                  ["--user", "--break-system-packages"]):
        try:
            p = subprocess.run([sys.executable, "-m", "pip", "install"]
                               + extra + list(packages),
                               stderr=subprocess.PIPE)
        except OSError:
            return False
        if p.returncode == 0:
            return True
    return False


def read_local(base, name):
    """Read one file out of a folder. Returns the bytes or None.

    --from turns the installer on a checkout or a copy on a stick,
    which is how it is tested and how it works without a network.
    """
    path = os.path.join(base, name.replace("/", os.sep))
    try:
        with open(path, "rb") as f:
            return f.read()
    except OSError as e:
        say("  %s" % e)
        return None


def fetch(url, tries=2):
    """Read one file off the network. Returns the bytes or None."""
    for attempt in range(tries):
        try:
            with urllib.request.urlopen(url, context=context(),
                                        timeout=60) as answer:
                return answer.read()
        except urllib.error.URLError as e:
            if isinstance(getattr(e, "reason", None), ssl.SSLError) \
                    and attempt == 0 and with_certificates():
                continue
            say("  %s" % e)
            return None
        except OSError as e:
            say("  %s" % e)
            return None
    return None


def read_sums(text):
    """Read a SHA256SUMS file: {file name: digest}.

    The plain format that shasum -c reads back, digest and name
    separated by spaces, with a comment block above it.
    """
    out = {}
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        parts = line.split()
        if len(parts) >= 2 and len(parts[0]) == 64:
            out[parts[-1]] = parts[0].lower()
    return out


def digest_of(path):
    """The SHA-256 of a file on disc, read in pieces."""
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def put(folder, name, data):
    """Write one file, making the folders above it first."""
    path = os.path.join(folder, name.replace("/", os.sep))
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    beside = path + ".part"
    with open(beside, "wb") as f:
        f.write(data)
    os.replace(beside, path)
    return path


def as_mb(count):
    """A byte count as megabytes, for reading rather than arithmetic."""
    return "%.1f MB" % (count / 1e6)


def check_python():
    """Say which Python this is and whether it is new enough."""
    got = sys.version_info[:3]
    say("Python %d.%d.%d  (%s)" % (got + (sys.executable,)))
    if got[:2] < NEEDS_PYTHON:
        say("Too old. The program needs %d.%d or newer -- the window "
            "does, PySide6 is not built below it." % NEEDS_PYTHON)
        say("Recommended: %s, the one it is used on daily."
            % LIKES_PYTHON)
        return False
    if ".".join(str(n) for n in got) != LIKES_PYTHON:
        say("  (recommended version %s -- this one works too)"
            % LIKES_PYTHON)
    return True


def check_ffmpeg():
    """Report ffmpeg, and say how to get it where it is missing.

    It is not installed here. ffmpeg is not a Python package, and
    where a package manager owns it, an installer that goes around it
    creates a second one nobody asked for. The program falls back to
    static-ffmpeg over pip on its own if it has to.
    """
    import shutil
    found = [n for n in ("ffmpeg", "ffprobe") if shutil.which(n)]
    if len(found) == 2:
        say("ffmpeg and ffprobe: on the search path.")
        return True
    say("ffmpeg or ffprobe is missing. The program can fetch a Python "
        "build itself, but the real one is better:")
    how = {"darwin": "  brew install ffmpeg",
           "win32": "  winget install ffmpeg     (or ffmpeg.org)"}
    say(how.get(sys.platform,
                "  apt install ffmpeg   /   dnf install ffmpeg"))
    return False


def verify(folder, sums):
    """Hold what is on disc against the sums. Returns the bad names."""
    bad = []
    for name, want in sorted(sums.items()):
        path = os.path.join(folder, MODEL.replace("/", os.sep),
                            name.replace("/", os.sep))
        if not os.path.exists(path):
            bad.append(name + " (missing)")
        elif digest_of(path) != want:
            bad.append(name + " (does not match)")
    return bad


def main():
    ap = argparse.ArgumentParser(
        description="Fetch videopodcast-magic and its model.",
        formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--to", default="videopodcast-magic",
                    metavar="PATH", help="where it goes "
                    "(default: ./videopodcast-magic)")
    ap.add_argument("--ref", default="main", metavar="NAME",
                    help="which state to fetch: a branch or a tag, "
                         "for instance v2.0.0-beta (default: main)")
    ap.add_argument("--check", action="store_true",
                    help="hold what is there against the sums and "
                         "fetch nothing")
    ap.add_argument("--from", dest="source", default="", metavar="PATH",
                    help="take the files out of this folder instead of "
                         "off the network -- a checkout, or a copy on a "
                         "stick (default: off the network)")
    ap.add_argument("--packages", action="store_true",
                    help="fetch numpy and PySide6 here instead of "
                         "leaving it to the program, which fetches them "
                         "at its first start anyway")
    ap.add_argument("--no-start", dest="start", action="store_false",
                    help="fetch everything and stop, instead of "
                         "starting the program at the end")
    args = ap.parse_args()

    folder = os.path.abspath(os.path.expanduser(args.to))
    source = os.path.abspath(os.path.expanduser(args.source)) \
        if args.source else ""
    say("videopodcast-magic -- installer")
    say("=" * 60)
    say("Into:  %s" % folder)
    if source:
        say("From:  %s" % source)
    else:
        say("From:  %s (%s)" % (RAW, args.ref))
    say()
    if source and os.path.abspath(folder) == source:
        say("Into and from are the same folder. Nothing to do.")
        return 1

    if not check_python():
        return 1
    say()

    base = "%s/%s/" % (RAW, args.ref)

    def take(name):
        """One file, out of the folder or off the network."""
        return read_local(source, name) if source else fetch(base + name)

    if args.check:
        path = os.path.join(folder, MODEL.replace("/", os.sep),
                            "SHA256SUMS.txt")
        if not os.path.exists(path):
            say("No sums at %s -- nothing to hold anything against."
                % path)
            return 1
        with open(path, encoding="utf-8") as f:
            sums = read_sums(f.read())
        bad = verify(folder, sums)
        for name in bad:
            say("  %s" % name)
        say("%d of %d files match." % (len(sums) - len(bad), len(sums)))
        return 1 if bad else 0

    # The sums first: they name the files to fetch, so the list is not
    # written twice and cannot drift from what the model actually is.
    say("Reading the file list ...")
    text = take(SUMS)
    if text is None:
        say("The file list could not be read. Nothing was written.")
        return 1
    sums = read_sums(text.decode("utf-8", "replace"))
    if not sums:
        say("The file list is empty. Nothing was written.")
        return 1
    say("  %d model files listed." % len(sums))
    say()

    say("Fetching the program ...")
    data = take(PROGRAM)
    if data is None:
        say("The program could not be fetched. Nothing was written.")
        return 1
    put(folder, PROGRAM, data)
    say("  %s  %s" % (PROGRAM, as_mb(len(data))))
    say()

    say("Fetching the model (about 33 MB) ...")
    put(folder, SUMS, text)
    total = 0
    for name in sorted(sums):
        where = MODEL + "/" + name
        data = take(where)
        if data is None:
            say("  %s could not be fetched." % name)
            return 1
        got = hashlib.sha256(data).hexdigest()
        if got != sums[name]:
            say("  %s does not match its sum -- not written." % name)
            return 1
        put(folder, where, data)
        total += len(data)
        say("  %-34s %10s  sum ok" % (name, as_mb(len(data))))
    for name in PAPERS:
        data = take(name)
        if data is not None:
            put(folder, name, data)
    say("  %s together." % as_mb(total))
    say()

    check_ffmpeg()
    say()

    if args.packages:
        say("Fetching numpy and PySide6 (about 100 MB) ...")
        if pip_install("numpy", "PySide6"):
            say("  done.")
        else:
            say("  pip refused. The program tries again at its first "
                "start and says what went wrong.")
        say()

    program = os.path.join(folder, PROGRAM)
    if not os.path.exists(program):
        say("The program is not there. Something went wrong above.")
        return 1

    say("=" * 60)
    say("Here again, to come back to:")
    say()
    say("  cd %s" % folder)
    say("  %s %s" % (os.path.basename(sys.executable), PROGRAM))
    say()
    say("The manual is at %s#readme" % RAW.replace(
        "raw.githubusercontent.com", "github.com"))
    say()

    if not args.start:
        return 0

    if not args.packages:
        say("Starting it. The first start fetches numpy and PySide6,")
        say("about 100 MB, and says so while it does. The speaker")
        say("separation sets itself up the first time it is asked")
        say("for, another 218 MB.")
    else:
        say("Starting it.")
    say("=" * 60)
    say()
    # Handed over rather than imported: the program is a program, and
    # its own start is the one that is tested. Its return code becomes
    # this one, so a failure is not swallowed by an installer that
    # thinks it is finished.
    try:
        p = subprocess.run([sys.executable, PROGRAM], cwd=folder)
    except OSError as e:
        say("It could not be started: %s" % e)
        return 1
    return p.returncode


if __name__ == "__main__":
    sys.exit(main())
