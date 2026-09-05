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

# A count does not pick a wording the same way in every language.
# English and German want two, Russian three, Arabic six, Japanese one.
# The rule is not in the program: each PO file carries its own, in the
# Plural-Forms line of its header, and these two hold what was read.
PLURALS = {}          # language -> {English singular: [wording per form]}
PLURAL_RULE = {}      # language -> (how many forms, the rule as a tree)

# What a backslash means inside a PO string: the letter above, the
# character below. Everything else stands as it is written, so a text
# keeps its own characters.
UNESCAPE = dict(zip('ntr"\\abfv',
                    '\n\t\r"\\\a\b\f\v'))
QUOTED = re.compile(r'^\s*"(.*)"\s*$')
INDEXED = re.compile(r"^msgstr\[(\d+)\]\s")


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


def read_po(path):
    """One PO file, as its texts, its plural wordings and its header.

    Forgiving on purpose. A line that makes no sense costs the entry it
    stands in and nothing more: the reader drops that one and carries
    on, so a typo in a translation loses a sentence rather than a
    language. The empty msgid is gettext's header; it is no text, and
    it is handed back on its own because the plural rule lives in it.
    """
    texts, plurals = {}, {}
    header = ""
    key = value = other = None
    forms = {}
    where = None          # which field is being read just now
    hurt = 0

    def keep():
        if key == "" and value:
            return value                  # the header, handed upward
        if key and forms:
            plurals[key] = [forms[i] for i in sorted(forms)]
        elif key and value is not None:
            texts[key] = value
        return None

    for line in io.open(path, encoding="utf-8", errors="replace"):
        bare = line.strip()
        if not bare or bare.startswith("#"):
            continue
        if bare.startswith("msgid_plural "):
            where, other = "plural", None
            bare = bare[len("msgid_plural "):]
        elif bare.startswith("msgid "):
            header = keep() or header
            key = value = other = None
            forms, where = {}, "msgid"
            bare = bare[len("msgid "):]
        elif INDEXED.match(bare):
            which = int(INDEXED.match(bare).group(1))
            where = which
            bare = bare[bare.index(" ") + 1:]
            forms.setdefault(which, "")
        elif bare.startswith("msgstr "):
            where = "msgstr"
            bare = bare[len("msgstr "):]
        elif not QUOTED.match(bare):
            # msgctxt, or a line nobody can read: the entry it belongs
            # to is dropped, the file goes on.
            key = value = other = None
            forms, where = {}, None
            hurt += 1
            continue
        piece = QUOTED.match(bare)
        if not piece or where is None:
            key = value = other = None
            forms, where = {}, None
            hurt += 1
            continue
        piece = po_string(piece.group(1))
        if where == "msgid":
            key = piece if key is None else key + piece
        elif where == "plural":
            other = piece if other is None else other + piece
        elif where == "msgstr":
            value = piece if value is None else value + piece
        else:
            forms[where] += piece
    header = keep() or header
    return texts, plurals, header


def texts_of_file(path):
    """Every ordinary entry of one PO file, English wording to translation."""
    return read_po(path)[0]


def texts_of_language(code):
    """One language's texts, out of the PO file beside this one.

    Read from beside this file rather than by name: a test loads the
    program from an absolute path, and Python leaves the folder off the
    search path then. A file that is missing is no language and gives
    nothing back. The plural wordings and the rule are put away rather
    than handed back, because what comes back is assigned to CATALOGUE.
    """
    beside_it = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                             code + ".po")
    try:
        texts, plurals, header = read_po(beside_it)
    except OSError:
        return {}
    if plurals:
        PLURALS[code] = plurals
    rule = plural_rule(header)
    if rule:
        PLURAL_RULE[code] = rule
    return texts


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


# A header carries its language's plural rule as a C expression over one
# name: "nplurals=3; plural=(n%10==1 && n%100!=11 ? 0 : ...)". Read into
# a tree once per language and walked per count -- read, never evaluated,
# because a catalogue is the one file here a stranger is invited to edit.
RULE_TOKEN = re.compile(r"\s*(\d+|n|\?|:|\|\||&&|[=!<>]=|[<>]|%|\(|\))")
# The header is many lines and Plural-Forms is rarely the last of them,
# so the rule ends at its own line end and not at the end of the header.
RULE_HEAD = re.compile(r"nplurals\s*=\s*(\d+)\s*;\s*"
                       r"plural\s*=\s*([^\n]+)")
COMPARE = ("==", "!=", "<", "<=", ">", ">=")
RULE_DO = {"||": lambda a, b: 1 if (a or b) else 0,
           "&&": lambda a, b: 1 if (a and b) else 0,
           "==": lambda a, b: 1 if a == b else 0,
           "!=": lambda a, b: 1 if a != b else 0,
           "<": lambda a, b: 1 if a < b else 0,
           "<=": lambda a, b: 1 if a <= b else 0,
           ">": lambda a, b: 1 if a > b else 0,
           ">=": lambda a, b: 1 if a >= b else 0,
           "%": lambda a, b: a % b if b else 0}


class RuleReader(object):
    """Reads the expression by precedence, from ternary down to atom."""

    def __init__(self, text):
        self.t, self.at = [], 0
        while len(text) > self.at and text[self.at:].strip():
            found = RULE_TOKEN.match(text, self.at)
            if not found:
                raise ValueError("cannot read %r" % text[self.at:][:20])
            self.t.append(found.group(1))
            self.at = found.end()
        self.at = 0

    def peek(self):
        return self.t[self.at] if self.at < len(self.t) else None

    def take(self, want=None):
        got = self.peek()
        if want and got != want:
            raise ValueError("wanted %r, found %r" % (want, got))
        self.at += 1
        return got

    def ternary(self):
        cond = self.two("||", self.andalso)
        if self.peek() != "?":
            return cond
        self.take("?")
        yes = self.ternary()
        self.take(":")
        return ("?", cond, yes, self.ternary())

    def two(self, sign, below):
        left = below()
        while self.peek() == sign:
            self.take()
            left = (sign, left, below())
        return left

    def andalso(self):
        return self.two("&&", self.compare)

    def compare(self):
        left = self.remainder()
        while self.peek() in COMPARE:
            sign = self.take()
            left = (sign, left, self.remainder())
        return left

    def remainder(self):
        return self.two("%", self.atom)

    def atom(self):
        got = self.take()
        if got == "(":
            inside = self.ternary()
            self.take(")")
            return inside
        if got == "n":
            return ("n",)
        if got is not None and got.isdigit():
            return ("k", int(got))
        raise ValueError("cannot read %r here" % got)


def plural_rule(header):
    """How many wordings this language has, and the rule that picks one.

    Nothing back where the header says nothing or says something that
    cannot be read: the caller then keeps the English rule, which is
    right for English and wrong quietly rather than loudly.
    """
    found = RULE_HEAD.search(header or "")
    if not found:
        return None
    try:
        reader = RuleReader(found.group(2).strip().rstrip(";"))
        tree = reader.ternary()
        if reader.peek() is not None:
            return None
        return int(found.group(1)), tree
    except (ValueError, IndexError):
        return None


def which_form(tree, number):
    """Which of the wordings a count wants, counting from zero."""
    kind = tree[0]
    if kind == "n":
        return number
    if kind == "k":
        return tree[1]
    if kind == "?":
        return which_form(tree[2] if which_form(tree[1], number)
                          else tree[3], number)
    return RULE_DO[kind](which_form(tree[1], number),
                         which_form(tree[2], number))


def T(text, *args):
    """Return a message in the chosen language, %-arguments applied.

    The English wording is the key, so the code stays readable and an
    untranslated text shows up in English instead of disappearing.
    """
    out = CATALOGUE.get(LANG, {}).get(text, text)
    return out % args if args else out


def TN(number, one, many):
    """Pick the wording a count wants, in the language being spoken.

    The two English wordings stand here because English needs no
    catalogue. Every other language says in its own file how many it
    has and which one a count wants -- Russian three, Arabic six -- and
    where it does, that answer wins. Where it does not, the English
    rule stands: one is singular, everything else is not.
    """
    forms = PLURALS.get(LANG, {}).get(one)
    rule = PLURAL_RULE.get(LANG)
    if forms and rule:
        how_many, tree = rule
        wanted = which_form(tree, number)
        if 0 <= wanted < min(how_many, len(forms)) and forms[wanted]:
            return forms[wanted]
    return T(one if number == 1 else many)
