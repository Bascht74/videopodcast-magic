# -*- coding: utf-8 -*-
"""What language the program speaks, and how a message is said in it.

Every message is written in English in the program. A translation lives
beside this file, one `<code>.py` per language holding a single name,
and `T()` looks a message up by its English wording -- so a text nobody
has translated shows up in English instead of disappearing.

The program reads those files itself and puts them in `CATALOGUE`, at
the end of its own file, and settles the language in the line after.
Not here, and the order is the point: what the program says while it is
still being read comes out English, because nothing has chosen yet.
"""
import os
import re
import subprocess
import sys


SOURCE_LANG = "en"    # the language the texts in the program are written in
CATALOGUE = {}        # language -> {English text: translation}
LANG = SOURCE_LANG    # what is spoken now; the program settles it at its end


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
