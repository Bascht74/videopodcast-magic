# -*- coding: utf-8 -*-
"""The ratchet, held on places instead of on counts.

A ratchet that holds a bare count lets one violation be swapped for
another: shorten a long line here, write a new one there, and the count
has not moved. So the state keeps the places. ESLint's bulk suppressions
keep a count per file and rule, detekt's baseline keeps a signature per
find, Betterer keeps a hash per find and rewrites the file only when the
run got better. This is the same idea with one file to look at.

The fingerprint may not carry a line number. A line number moves as soon
as anybody inserts a line above it, and a state that compares line
numbers goes red on every change and is switched off a week later. What
the fingerprint carries instead is what the find is: the function it
sits in, the wording it has, the name it goes by. The line is written
down beside it, and never compared -- it is a hint for whoever reads a
diff of the state, taken when that entry was last written.

Two shapes of counter live here. `number()` holds a plain count, for the
ones standing at zero, where there is nothing to swap. `places()` holds
a fingerprint for every find, and goes red as soon as a find turns up
that the state does not cover -- by name.
"""
import ast
import io
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
IN_TREE = os.path.join(os.path.dirname(HERE), "videopodcast-magic.py")


def state_is_ours():
    """Whether this run may move the ratchet.

    A ratchet is only worth something while it stands for the file in
    the working tree. VPM_SCRIPT lets a run measure a snapshot instead,
    and every ratchet here writes itself down as soon as a count comes
    out lower -- so one run against an older or shorter copy pulls the
    ratchet down for good, to a number the real file may never reach
    again. Found on 24.8.2026, after a day of running the suite against
    snapshots in /tmp.

    So: measure whatever VPM_SCRIPT points at, but write the state down
    only where that is the file this repository ships.
    """
    named = os.environ.get("VPM_SCRIPT")
    if not named:
        return True
    try:
        return os.path.samefile(named, IN_TREE)
    except OSError:
        return False


def dumps(data):
    """The state as text: one find to a line, sorted.

    json.dump on its own writes the whole thing as a single line, and a
    diff of that says nothing about which find came or went. Sorted keys
    and one entry per line make the diff the report.
    """
    out = []
    for key in sorted(data):
        value = data[key]
        if isinstance(value, dict):
            if not value:
                out.append(" %s: {}" % json.dumps(key))
                continue
            rows = ["  %s: %s" % (json.dumps(mark), json.dumps(value[mark]))
                    for mark in sorted(value)]
            out.append(" %s: {\n%s\n }" % (json.dumps(key),
                                           ",\n".join(rows)))
        else:
            out.append(" %s: %s" % (json.dumps(key), json.dumps(value)))
    return "{\n" + ",\n".join(out) + "\n}\n"


class Held(object):
    """What one ratchet had to say about one counter."""

    def __init__(self, ok, worse, limit, tightened):
        self.ok = ok
        self.worse = worse
        self.limit = limit
        self.tightened = tightened

    def report(self):
        """Name every place the state does not cover.

        Red without a place is worth nothing: it says a number rose and
        leaves the reader to find out where. So every find that is not
        covered gets its line, its fingerprint and what the state allows
        at that spot.
        """
        for mark, measure, allowed, line in self.worse:
            if allowed:
                why = "%d here, the state allows %d" % (measure, allowed)
            else:
                why = "no such place in the state"
            print("      line %-6s %-44s %s" % (line or "?", mark[:44], why))


class Ratchet(object):
    """The state file of one test, and the counters kept in it."""

    def __init__(self, path):
        self.path = path
        self.fresh = not os.path.exists(path)
        self.old = {}
        if not self.fresh:
            try:
                self.old = json.load(io.open(path, encoding="utf-8"))
            except ValueError:
                self.old = {}
        self.new = dict(self.old)

    def announce(self):
        """Say it out loud when there is no baseline to hold anything to."""
        if self.fresh:
            print("  NOTE: %s is missing. The counters below are being set\n"
                  "        from the source as it stands; nothing is being\n"
                  "        held to account this run."
                  % os.path.basename(self.path))

    def _save(self):
        """Write the state down, and say whether it really was written."""
        if not state_is_ours():
            return False
        io.open(self.path, "w", encoding="utf-8").write(dumps(self.new))
        return True

    def note(self, limit, now):
        """Say the ratchet has moved -- where it really has.

        A run against a snapshot measures but is not allowed to write,
        so a line saying the ratchet tightened would send whoever reads
        the log looking for a change that is not in the file. Measured
        on 24.8.2026: a snapshot with one silent except taken out
        printed "98 -> 97" while style_state.json stayed byte for byte
        the same.
        """
        if now < limit and state_is_ours():
            print("      ratchet tightened: %d -> %d" % (limit, now))

    def number(self, key, value):
        """A counter with nothing to point at: it may fall, never rise.

        Returns the limit this run is held to.
        """
        old = self.old.get(key)
        if not isinstance(old, int):
            self.new[key] = value
            self._save()
            return value
        if value < old:
            self.new[key] = value
            self._save()
        return old

    def places(self, key, found):
        """A counter that knows where its finds sit.

        `found` maps a fingerprint to (how many, line). Two finds with
        the same fingerprint are one entry with a count of two, and the
        line beside it is only a hint for the reader.
        """
        old = self.old.get(key)
        allowed = None
        limit = None
        if isinstance(old, dict):
            allowed = dict((mark, entry[0]) for mark, entry in old.items())
            limit = sum(allowed.values())
        elif isinstance(old, int):
            # The state still holds the bare count from before the
            # changeover. Hold the run to that count first, and write the
            # places down only once it holds -- so nothing slips through
            # on the one run that does the migration.
            limit = old
        now = sum(m for m, _l in found.values())

        worse = []
        if allowed is not None:
            for mark in sorted(found):
                measure, line = found[mark]
                may = allowed.get(mark, 0)
                if measure > may:
                    worse.append((mark, measure, may, line))
        elif limit is not None and now > limit:
            worse.append(("(a count rose; the state knew no places yet)",
                          now, limit, 0))

        if worse:
            # Never write a state that is worse than the one held: that
            # would bake the new violation in and let it pass next time.
            return Held(False, worse, limit if limit is not None else now,
                        False)

        kept = {}
        for mark in found:
            measure, line = found[mark]
            was = old.get(mark) if isinstance(old, dict) else None
            # An entry whose measure has not moved keeps its old line as
            # well, so the diff of this file shows what really changed
            # and not every line number that shifted underneath it.
            kept[mark] = was if was and was[0] == measure else [measure,
                                                                line]
        tightened = False
        if kept != old:
            self.new[key] = kept
            wrote = self._save()
            tightened = wrote and limit is not None and now < limit
        return Held(True, [], limit if limit is not None else now, tightened)


def owners(tree):
    """For every node, the dotted name of the function it sits in.

    A find anchored to a function survives every insertion above it, and
    that is the whole point of the fingerprint. Class bodies count
    towards the name as well, so two methods called `run` stay apart.
    """
    seen = {}

    def walk(node, path):
        for child in ast.iter_child_nodes(node):
            seen[id(child)] = ".".join(path) or "<module>"
            if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef,
                                  ast.ClassDef)):
                walk(child, path + [child.name])
            else:
                walk(child, path)

    seen[id(tree)] = "<module>"
    walk(tree, [])
    return seen


def qualified(seen, node):
    """The dotted name of a function itself, not of what holds it."""
    above = seen.get(id(node), "<module>")
    return node.name if above == "<module>" else above + "." + node.name


def tally(finds):
    """Count finds by fingerprint: {mark: (how many, first line)}.

    Two finds with the same fingerprint are not told apart -- the same
    kind of violation, in the same place, is one entry with a count of
    two. That is where ESLint's suppressions stop as well, and going
    finer would mean reaching for the line number again.
    """
    out = {}
    for mark, line in finds:
        if mark in out:
            out[mark] = (out[mark][0] + 1, min(out[mark][1], line))
        else:
            out[mark] = (1, line)
    return out
