# -*- coding: utf-8 -*-
"""One file, whatever it is called: the shape a path is compared in.

A piece of the program, read in by beside(): it cannot import the file
it was cut out of, so the program is handed in and bound below by name.
"""

# Put here by beside() before this file is read.
PROGRAM = PROGRAM

# Bound above the seam, so it is a copy and not read late.
os = PROGRAM.os


# =====================================================================
#  One file, whatever it is called
#  -------------------------------

def path_key(path):
    """The one shape a path takes when two of them are compared.

    abspath settles the folder; normcase settles case and separator, so
    the same file reached two ways on Windows compares equal. Every
    comparison and every path used as a key goes through here.
    """
    return os.path.normcase(os.path.abspath(path))


class ByFile(dict):
    """A dictionary of files: one entry per file, whatever it is called.

    On Windows one file arrives under several spellings, so finding
    goes through path_key on every side. The key keeps the spelling it
    was first written under: what is shown or saved is the name on disc.
    """

    # A key that is not a string passes through untouched; a compound
    # key is put into shape where it is built -- see prework_api_key.

    def __init__(self, *given, **named):
        dict.__init__(self)
        self._spelt = {}
        if given or named:
            self.update(*given, **named)

    def _index(self):
        """The spelling each file sits under, rebuilt if it is gone.

        A dictionary can come into being without __init__ -- fromkeys,
        a copy read back in -- and a lookup would then quietly miss.
        """
        try:
            return self._spelt
        except AttributeError:
            self._spelt = {path_key(k): k for k in self if isinstance(k, str)}
            return self._spelt

    def _as_stored(self, key):
        """The key this file already sits under, or the key itself."""
        if not isinstance(key, str):
            return key
        if dict.__contains__(self, key):
            return key
        return self._index().get(path_key(key), key)

    def __getitem__(self, key):
        return dict.__getitem__(self, self._as_stored(key))

    def __setitem__(self, key, value):
        here = self._as_stored(key)
        dict.__setitem__(self, here, value)
        if isinstance(key, str):
            self._index()[path_key(key)] = here

    def __delitem__(self, key):
        here = self._as_stored(key)
        dict.__delitem__(self, here)
        if isinstance(here, str):
            self._index().pop(path_key(here), None)

    def __contains__(self, key):
        return dict.__contains__(self, self._as_stored(key))

    def __ior__(self, other):
        self.update(other)
        return self

    def get(self, key, fallback=None):
        return dict.get(self, self._as_stored(key), fallback)

    def setdefault(self, key, fallback=None):
        here = self._as_stored(key)
        if dict.__contains__(self, here):
            return dict.__getitem__(self, here)
        self[key] = fallback
        return fallback

    def pop(self, key, *fallback):
        here = self._as_stored(key)
        got = dict.pop(self, here, *fallback)
        if isinstance(here, str):
            self._index().pop(path_key(here), None)
        return got

    def popitem(self):
        key, value = dict.popitem(self)
        if isinstance(key, str):
            self._index().pop(path_key(key), None)
        return key, value

    def clear(self):
        dict.clear(self)
        self._index().clear()

    def update(self, *given, **named):
        for other in given:
            pairs = other.items() if hasattr(other, "items") else other
            for key, value in pairs:
                self[key] = value
        for key, value in named.items():
            self[key] = value

    def copy(self):
        return ByFile(self)


class FileSet(set):
    """A set of files: one entry per file, whatever it is called."""

    def __init__(self, given=()):
        set.__init__(self)
        self.update(given)

    @staticmethod
    def _shape(item):
        return path_key(item) if isinstance(item, str) else item

    def __contains__(self, item):
        return set.__contains__(self, self._shape(item))

    def add(self, item):
        set.add(self, self._shape(item))

    def discard(self, item):
        set.discard(self, self._shape(item))

    def remove(self, item):
        set.remove(self, self._shape(item))

    def update(self, *given):
        for other in given:
            for item in other or ():
                self.add(item)

    def difference_update(self, *given):
        for other in given:
            for item in other or ():
                self.discard(item)
