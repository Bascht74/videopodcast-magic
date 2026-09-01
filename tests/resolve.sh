#!/bin/bash
# The tests that talk to a DaVinci Resolve really running on this machine.
# Success = return code 0, no traceback, no "FAIL".
#
# They are not in the suite and run.sh does not know them. On a machine
# without Resolve every one of them would be red for a reason that is not
# a fault, and a test that skipped instead would cost the skip ratchet in
# run.sh, which may fall and never rise. So they live in resolve/ and are
# started from here:
#
#   cd tests && bash resolve.sh              all of them
#   cd tests && bash resolve.sh project_clips_land_right    one of them
#
# One after another, never several at a time: there is one Resolve and one
# project open in it, and two tests would fight over it.
#
# Each test makes a project of its own -- the name carries vpm-test, the
# process id and a random ending -- and deletes it again at the end, also
# when it falls over. The project that was open beforehand is opened again.
# Nothing else in Resolve is touched, and nothing is written into any
# folder but the shared fixtures' own and a temporary one per run.
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$HERE"
WHERE="$HERE/resolve"

# The same interpreter the suite runs on, or the answer is about a Python
# nobody uses. VPM_PYTHON overrides it, as in run.sh.
PY="${VPM_PYTHON:-}"
if [ -z "$PY" ]; then
  for candidate in /opt/py3147/bin/python3.14 python3.14 python3; do
    if command -v "$candidate" > /dev/null 2>&1; then PY="$candidate"; break; fi
  done
fi
export VPM_PYTHON="$PY"
echo "Python: $("$PY" -V 2>&1)"
echo "Script: ${VPM_SCRIPT:-$(dirname "$HERE")/videopodcast-magic.py}"

# ffprobe counts the audio tracks in the camera files, and without it the
# program falls back to a guess -- then red or green says something about
# the machine rather than about the program.
for tool in ffmpeg ffprobe; do
  if ! command -v "$tool" > /dev/null 2>&1; then
    echo "$tool is not on the search path, and the camera files are"
    echo "measured with it."
    echo
    echo "  brew install ffmpeg              (macOS)"
    exit 2
  fi
done

# The same environment run.sh sets. Without it red or green is a statement
# about the machine and not about the program: LANG=C alone does not settle
# the language, because the program skips "C" on purpose and asks the
# system, which on a German Mac answers de_DE.
export LANG=C LC_ALL=C LANGUAGE=en
export VPM_SILENT=1
export VPM_NO_SPEAKER_SPLIT=1
export VPM_NO_UPDATE_CHECK=1
export PYTHONFAULTHANDLER=1
export VPM_FIXTURES="${VPM_FIXTURES:-/tmp/vpm-fixtures-$(id -u)}"

RUN_TEMP=$(mktemp -d "${TMPDIR:-/tmp}/vpm_resolve_XXXXXX")
RUN_CACHE="${TMPDIR:-/tmp}/vpm_cache_resolve_$(id -u)_$$"
mkdir -p "$RUN_CACHE"
export VPM_CACHE="$RUN_CACHE"
export TMPDIR="$RUN_TEMP"
# Set before the trap below uses them. RESOLVE_OK stays 0 until the
# interface has answered, and the tidying up is skipped while it is 0:
# where there is no Resolve nothing may be deleted, and that path ends in
# a readable line of its own further down.
RESOLVE_OK=0
OPEN_BEFORE=""
tidy_up_resolve() {
  [ "$RESOLVE_OK" = 1 ] || return 0
  echo
  "$PY" "$WHERE/sweep.py" --sweep --restore "$OPEN_BEFORE"
}
clean_up() {
  # Resolve first, the disc afterwards: this runs on every way out --
  # the tests passed, one was red, one threw, somebody pressed Ctrl-C --
  # and what it puts back is the project that was open at the start.
  tidy_up_resolve
  if [ -n "$KEEP_TEMP" ]; then
    echo "temporary material kept in $RUN_TEMP"
  else
    rm -rf "$RUN_TEMP" "$RUN_CACHE"
  fi
}
trap clean_up EXIT
# A Ctrl-C is an exit too, or gigabytes of material stay behind.
trap 'exit 130' INT TERM

# The camera files come from the shared fixtures, which are read and never
# written. Building them here, before anything starts, keeps a test from
# waiting on ffmpeg in the middle of a Resolve session.
if ! bash "$HERE/fixtures.sh"; then
  echo "fixtures could not be built -- stopping." >&2
  exit 2
fi

# Is there a Resolve to talk to at all? Asked through the program's own
# check_resolve, so what comes back is the program's own reason and its
# own idea of where the interface lives -- and a missing Resolve stops
# here with a readable line instead of three tracebacks.
echo
if ! "$PY" - <<'PROBE'
import os, sys, importlib.util
script = os.environ.get("VPM_SCRIPT") or os.path.join(
    os.path.dirname(os.getcwd()), "videopodcast-magic.py")
spec = importlib.util.spec_from_file_location("vpm", script)
vpm = importlib.util.module_from_spec(spec)
sys.modules["vpm"] = vpm
spec.loader.exec_module(vpm)
vpm.set_language("en")
works, lines = vpm.check_resolve()
for line in lines:
    print("  " + str(line).replace("\n", "\n  "))
if works:
    pm = vpm.connect_to_resolve().GetProjectManager()
    p = pm.GetCurrentProject()
    print("  open in Resolve just now: %r" % (p.GetName() if p else None))
    print("  database: %r" % (pm.GetCurrentDatabase(),))
sys.exit(0 if works else 3)
PROBE
then
  echo
  echo "No Resolve to talk to, so nothing was tested."
  echo
  echo "These tests need a DaVinci Resolve running on this machine:"
  echo "  1. Start DaVinci Resolve and leave it open."
  echo "  2. Preferences > System > General: set external scripting to"
  echo "     'Local'. With 'None' the interface answers nothing."
  echo "  3. The scripting module has to be installed -- on macOS under"
  echo "     /Library/Application Support/Blackmagic Design/DaVinci"
  echo "     Resolve/Developer/Scripting."
  echo
  echo "External scripting is reported to be reserved for the Studio"
  echo "edition since version 19.1. I found no official statement."
  exit 2
fi

# From here on there is a Resolve to talk to, so the tidying up may run.
RESOLVE_OK=1
OPEN_BEFORE=$("$PY" "$WHERE/sweep.py" --which 2> /dev/null)

echo
echo "Somebody's project will be closed and opened again while these run."
echo "Each test makes one of its own and deletes it afterwards, and"
echo "whatever a killed run left behind is cleared away here and at the"
echo "end. Only names of the tests' own shape, never a project somebody"
# Nothing to remember has two reasons and the line names both, because
# they want different things done. Either a project the tests made is
# still open, which only a killed run leaves behind -- or what is open
# stands in no project list, which is what a project nobody ever saved
# looks like. The second one somebody can put right by saving it, and
# until then the tests leave themselves out rather than take it away.
echo "named. Open at the start, and open again at the end: ${OPEN_BEFORE:-none -- what is open cannot be opened again: either a project the tests made and an earlier run was killed, or one that was never saved and stands in no project list}"
# Here and not only at the end: a project a killed run left behind can be
# found nowhere else. Same narrow pattern, and the same putting back.
"$PY" "$WHERE/sweep.py" --sweep --restore "$OPEN_BEFORE"

TESTS=$(cd "$WHERE" && ls *_test.py 2>/dev/null | sed 's/_test\.py$//' | sort)
[ $# -gt 0 ] && TESTS="$*"
if [ -z "$TESTS" ]; then
  echo "no tests found in $WHERE" >&2
  exit 2
fi

green=0; red=0; left_out=0; fell=""
for t in $TESTS; do
  if [ ! -f "$WHERE/${t}_test.py" ]; then
    echo "no such test: $WHERE/${t}_test.py" >&2
    red=$((red + 1)); fell="$fell $t"
    continue
  fi
  echo
  echo "=== $t ==="
  began=$SECONDS
  out=$("$PY" "$WHERE/${t}_test.py" 2>&1); rc=$?
  took=$((SECONDS - began))
  printf '%s\n' "$out"
  if printf '%s\n' "$out" | grep -q "^SKIPPED:"; then
    left_out=$((left_out + 1))
    echo "--- $t left itself out after ${took}s"
  elif [ $rc -ne 0 ] || printf '%s\n' "$out" | grep -qE "^Traceback|FAIL"; then
    red=$((red + 1)); fell="$fell $t"
    echo "--- $t RED after ${took}s (rc=$rc)"
  else
    green=$((green + 1))
    echo "--- $t green after ${took}s"
  fi
done

echo
echo "green: $green  red: $red  left out: $left_out"
[ -n "$fell" ] && echo "red:$fell"
# A test that left itself out checked nothing, so the run cannot be called
# a pass either -- but it is not a fault, and it is counted apart.
[ $red -gt 0 ] && exit 1
[ $left_out -gt 0 ] && exit 2
exit 0
