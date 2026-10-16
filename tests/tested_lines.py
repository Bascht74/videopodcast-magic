# -*- coding: utf-8 -*-
"""Which of the program's lines the suite runs, function by function.

The measuring half of `source_lines_stay_tested`; the judging half is
that test. Nothing here runs on an ordinary `bash run.sh`: the suite
measures only under `VPM_COVERAGE=1`, which a release sets on one job
(tests.yml says which), and the whole of the cost is behind that switch.

How it measures. coverage.py, from 7.10 on, puts a `.pth` file into the
site-packages it is installed in, and every Python started from there
looks for `COVERAGE_PROCESS_START` and, finding it, measures itself.
So run.sh writes the configuration `config()` gives, points that one
variable at it, and every process the suite starts -- the tests, the
program they start, the program that program starts -- writes a data
file of its own into one folder. No sitecustomize, no wrapper, nothing
in the program: a Python without coverage.py beside it is not measured,
and a run without the variable costs nothing at all.

The sys.monitoring core and not the tracer: the tracer follows only
threads started through `threading`, and the window's work runs in
QThreads as well. `sigterm` because the suite's time limit and some
tests end a process with SIGTERM, and without it that process's lines
are lost.

The count is per function, by the same fingerprint `ratchet.py` gives
every other place: the file's path inside the program folder and the
dotted name of the function. A line belongs to the innermost function
whose body holds it; the `def` line and its decorators belong to what
holds the function, because they run when the module is read and say
nothing about whether the function was ever called. What stands outside
every function is `<module>`, and a class body is its class.

**Nothing in this file prints**, as `the_program.py` asks of a helper,
except when it is started on its own to write the configuration.
"""
import ast
import io
import os
import sys

# The name the data files are written under, inside the folder run.sh
# names. coverage.py appends the machine, the process and a random part.
DATA_NAME = ".coverage"


def config(data_folder, program_folder):
    """The configuration every measured process reads, as text."""
    return "\n".join([
        "[run]",
        "parallel = true",
        "data_file = %s" % os.path.join(data_folder, DATA_NAME),
        "source = %s" % program_folder,
        "core = sysmon",
        "sigterm = true",
        # Every process is measured, most never touch the program: a
        # test's helper, ffmpeg's wrapper. Each of them would warn on
        # stderr, and several tests read stderr.
        "disable_warnings = no-data-collected, module-not-imported,"
        " module-not-measured, couldnt-parse, no-ctracer",
        "",
    ])


def program_files(folder):
    """Every Python file of the program, as paths inside `folder`."""
    out = []
    for top, dirs, files in os.walk(folder):
        dirs[:] = sorted(d for d in dirs
                         if d != "__pycache__" and not d.startswith("."))
        for name in sorted(files):
            if name.endswith(".py"):
                out.append(os.path.relpath(os.path.join(top, name), folder))
    return out


def owners_of_lines(source):
    """{line: dotted name of the innermost function or class body}."""
    tree = ast.parse(source)
    paint = {}

    def walk(node, path):
        for child in ast.iter_child_nodes(node):
            if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef,
                                  ast.ClassDef)):
                name = path + [child.name]
                first = child.body[0].lineno
                for line in range(first, child.end_lineno + 1):
                    paint[line] = ".".join(name)
                walk(child, name)
            else:
                walk(child, path)

    walk(tree, [])
    return paint


def combine(data_folder):
    """The data files in `data_folder` joined into one, and that one read.

    coverage.py deletes the pieces once they are joined, which is what a
    disc that is nearly full wants. Returns the CoverageData, or None
    when the folder holds nothing to join.
    """
    import coverage
    base = os.path.join(data_folder, DATA_NAME)
    cov = coverage.Coverage(data_file=base, config_file=False)
    try:
        cov.combine([data_folder], strict=True)
    except coverage.exceptions.NoDataError:
        if not os.path.exists(base):
            return None
    cov.save()
    data = coverage.CoverageData(basename=base)
    data.read()
    return data


def executed(data, measured_folder):
    """{path inside the program folder: set of lines run}."""
    root = os.path.realpath(measured_folder)
    out = {}
    for name in data.measured_files():
        real = os.path.realpath(name)
        if not real.startswith(root + os.sep):
            continue
        rel = os.path.relpath(real, root)
        out.setdefault(rel, set()).update(data.lines(name) or ())
    return out


def statements(path):
    """The lines coverage.py counts as executable in one file."""
    from coverage.parser import PythonParser
    parser = PythonParser(filename=path)
    parser.parse_source()
    return set(parser.statements)


def tally(analysed_folder, ran):
    """{mark: (lines untested, lines in all, first line)}, and totals.

    `ran` comes from `executed()` over the folder that was measured; it
    is matched to `analysed_folder` by the path inside the folder, so a
    copy can be judged against the measurement of the original as long
    as the lines above what was changed stand where they stood.
    """
    found = {}
    for rel in program_files(analysed_folder):
        path = os.path.join(analysed_folder, rel)
        source = io.open(path, encoding="utf-8").read()
        paint = owners_of_lines(source)
        hit = ran.get(rel, set())
        for line in sorted(statements(path)):
            mark = "%s:%s" % (rel.replace(os.sep, "/"),
                              paint.get(line, "<module>"))
            missed, whole, first = found.get(mark, (0, 0, line))
            found[mark] = (missed + (line not in hit), whole + 1,
                           min(first, line))
    untested = sum(m for m, _w, _f in found.values())
    lines = sum(w for _m, w, _f in found.values())
    return found, untested, lines


if __name__ == "__main__":
    # bash run.sh writes the configuration through this, so it is said
    # in one place: python3 tested_lines.py <data folder> <program folder>
    sys.stdout.write(config(sys.argv[1], sys.argv[2]))
