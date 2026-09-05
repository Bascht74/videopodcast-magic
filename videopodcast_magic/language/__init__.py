# -*- coding: utf-8 -*-
"""What language the program speaks, and how a message is said in it.

Every message is written in English in the program. A translation lives
beside this file, one `<code>.po` per language, and `T()` looks a
message up by its English wording -- so a text nobody has translated
shows up in English instead of disappearing.

The program reads those files itself and puts them in `CATALOGUE`, at
the end of its own file, and settles the language in the line after.
Not here, and the order is the point: what the program says while it is
still being read comes out English, because nothing has chosen yet.

Why `.po` and not Python: a translation is data, and data that is
program can bring the program down. A missing comma in a Python
catalogue turned all 1531 German texts into nothing and stopped the
start with a SyntaxError. The reader below reads a broken entry as one
lost sentence instead, and every translation tool in the world can open
the file. Nothing is compiled: `.mo` files would have to be built on
the machine that installs, and the one way in here -- pip3 from a git
URL -- runs no step of ours there.
"""
import io
import os
import re
import subprocess
import sys


SOURCE_LANG = "en"    # the language the texts in the program are written in
CATALOGUE = {}        # language -> {English text: translation}
LANG = SOURCE_LANG    # what is spoken now; the program settles it at its end

# What a backslash means inside a PO string: the letter above, the
# character below. Everything else stands as it is written, so a text
# keeps its own characters.
UNESCAPE = dict(zip('ntr"\\abfv',
                    '\n\t\r"\\\a\b\f\v'))
QUOTED = re.compile(r'^\s*"(.*)"\s*$')


def po_string(text):
    """Turn what stands between the quotes back into the text itself."""
    out, escaped = [], False
    for char in text:
        if escaped:
            out.append(UNESCAPE.get(char, char))
            escaped = False
        elif char == "\\":
            escaped = True
        else:
            out.append(char)
    return "".join(out)


def texts_of_file(path):
    """Every entry of one PO file, as {English wording: translation}.

    Forgiving on purpose. A line that makes no sense costs the entry it
    stands in and nothing more: the reader drops that one and carries
    on, so a typo in a translation loses a sentence rather than a
    language. The empty msgid is gettext's header and is not a text.
    """
    texts = {}
    key = value = None
    where = None          # "msgid" or "msgstr", whichever is being read
    hurt = 0

    def keep():
        if key and value is not None:
            texts[key] = value

    for line in io.open(path, encoding="utf-8", errors="replace"):
        bare = line.strip()
        if not bare or bare.startswith("#"):
            continue
        if bare.startswith("msgid "):
            keep()
            key, value, where = None, None, "msgid"
            bare = bare[len("msgid "):]
        elif bare.startswith("msgstr "):
            where = "msgstr"
            bare = bare[len("msgstr "):]
        elif not QUOTED.match(bare):
            # msgid_plural, msgctxt, or a line nobody can read: the
            # entry it belongs to is dropped, the file goes on.
            key, value, where = None, None, None
            hurt += 1
            continue
        piece = QUOTED.match(bare)
        if not piece or where is None:
            key, value, where = None, None, None
            hurt += 1
            continue
        piece = po_string(piece.group(1))
        if where == "msgid":
            key = piece if key is None else key + piece
        else:
            value = piece if value is None else value + piece
    keep()
    return texts


def texts_of_language(code):
    """One language's texts, out of the PO file beside this one.

    Read from beside this file rather than by name: every test loads
    the program from an absolute path, and Python leaves the folder off
    the search path then. A language whose file is missing or
    unreadable is no language and gives nothing back -- the program
    then says everything in English, which is what it is written in.
    """
    beside_it = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                             code + ".po")
    try:
        return texts_of_file(beside_it)
    except OSError:
        return {}


def languages():
    """Return every language code this program can speak, sorted."""
    return sorted(set(CATALOGUE) | {SOURCE_LANG})


def known_language(code):
    """Reduce a locale name to a language this program has texts for.

    "de_DE.UTF-8" becomes "de". Anything without a catalogue becomes
    English, because that is what the untranslated texts already are.
    """
    # LANGUAGE may hold a list, "de:en"; the first entry counts.
    code = re.split(r"[-_.@:]", (code or "").strip())[0].lower()
    return code if code in languages() else SOURCE_LANG


def system_locale():
    """Return the locale name the system asks for, or "".

    The environment is asked first, because that is what a terminal
    session sets. A double-clicked app starts without it, so macOS and
    Windows are asked directly before the C library gets a turn.
    """
    for name in ("LANGUAGE", "LC_ALL", "LC_MESSAGES", "LANG"):
        value = os.environ.get(name) or ""
        if value and value not in ("C", "POSIX"):
            return value
    if sys.platform == "darwin":
        try:
            p = subprocess.run(["defaults", "read", "-g", "AppleLocale"],
                               capture_output=True, text=True, timeout=5)
            if p.returncode == 0 and p.stdout.strip():
                return p.stdout.strip()
        except Exception:
            pass
    if os.name == "nt":
        try:
            import ctypes
            buffer = ctypes.create_unicode_buffer(85)
            if ctypes.windll.kernel32.GetUserDefaultLocaleName(buffer, 85):
                return buffer.value
        except Exception:
            pass
    try:
        import locale
        return locale.getlocale()[0] or ""
    except Exception:
        return ""


def set_language(name):
    """Switch every message to that language, and give the code back.

    Given back so that the program can hold the same code under its own
    name, where a reader of it and every test look for it.
    """
    global LANG
    LANG = known_language(name)
    return LANG


def T(text, *args):
    """Return a message in the chosen language, %-arguments applied.

    The English wording is the key, so the code stays readable and an
    untranslated text shows up in English instead of disappearing.
    """
    out = CATALOGUE.get(LANG, {}).get(text, text)
    return out % args if args else out


def TN(number, one, many):
    """Pick the singular or the plural wording; both are translated.

    Languages do not agree on how a plural is built, so each wording is
    its own text instead of a suffix glued on in the code.
    """
    return T(one if number == 1 else many)
