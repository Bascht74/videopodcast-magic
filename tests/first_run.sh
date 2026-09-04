#!/bin/bash
# Put the machine back the way it was before the program ever ran.
#
# Not part of the suite. run.sh picks up *_test.py and nothing else, so
# this file is never started by accident -- which is the point: it
# uninstalls, it deletes, and a suite must do neither.
#
# Run it when something about installing or caching has changed: the
# environment the separation is built in, a package the program fetches
# by itself, a cache folder, the model beside the program. Then open a
# real project and watch the first run put it all back.
#
#   bash first_run.sh              say what would go, delete nothing
#   bash first_run.sh --for-real   delete it, after one question
#
# With --then-install it does the whole thing in one go: it clears the
# machine and then fetches the program into ~/videopodcast-magic and
# starts it. Every file of it, not one -- the texts stand beside it,
# one per language, and it dies on import without them. That is the
# round trip: nothing installed, then the program bringing everything
# it needs by itself, the way anybody else would get it.
#
#   bash first_run.sh --for-real --then-install
#   bash first_run.sh --for-real --then-install --to PATH
#   bash first_run.sh --for-real --then-install --from-here
#
# --from-here copies the program out of this checkout instead of
# fetching it. For trying a change before it is pushed.
#
# Leave a group out with --without-<group>:
#   environment  the virtual environment the separation runs in
#   cache        what the program stores between runs
#   modules      the packages it installs into this Python
#   torch        torch and what came with it (see below)
#   models       the model files in the Hugging Face store
#   pip          pip's download store
#   keychain     the auphonic key
#
# What it never touches:
#   * models/ beside the program. The separation model travels with the
#     program and is not fetched, so removing it does not test an
#     install -- it breaks the program.
#   * project folders and their results.
#   * ffmpeg from a package manager.

set -u

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO="$(dirname "$HERE")"
PY="${VPM_PYTHON:-python3}"

# The same rule cache_folder() follows in the program, without importing
# it: importing would run the part that installs what is missing, which
# is the very thing this script takes away.
CACHE=$("$PY" - <<'EOF'
import os, sys
if sys.platform == "darwin":
    base = os.path.expanduser("~/Library/Caches")
elif os.name == "nt":
    base = os.environ.get("LOCALAPPDATA") or os.path.expanduser("~")
else:
    base = os.environ.get("XDG_CACHE_HOME") or os.path.expanduser("~/.cache")
print(os.path.join(base, "videopodcast-magic"))
EOF
)
HF="${HF_HOME:-$HOME/.cache/huggingface}/hub"
if [ "$(uname -s)" = "Darwin" ]; then
    PIPCACHE="$HOME/Library/Caches/pip"
else
    PIPCACHE="${XDG_CACHE_HOME:-$HOME/.cache}/pip"
fi

# What the program installs into the interpreter it runs in.
# shiboken6 is on the list because it comes in with PySide6 and does not
# go out with it: pip removes what was asked for, not what came along.
MODULES="numpy PySide6 PySide6_Addons PySide6_Essentials shiboken6 \
certifi faster-whisper"
# Only with these gone does the environment cost what it costs: it is
# built with --system-site-packages and borrows whatever is already
# here. What the program never installs is not on the list, because
# taking it away would test nothing.
TORCH="torch torchaudio"

# The bash on a Mac is 3.2 and has no named arrays, so the groups left
# out are one string with a space on either side of every name.
FOR_REAL=0
THEN_INSTALL=0
FROM_HERE=0
INTO="$HOME/videopodcast-magic"
WITHOUT=" "
want_into=0
for a in "$@"; do
    if [ $want_into -eq 1 ]; then INTO="$a"; want_into=0; continue; fi
    case "$a" in
    --for-real)        FOR_REAL=1 ;;
    --then-install)    THEN_INSTALL=1 ;;
    --from-here)       FROM_HERE=1 ;;
    --to)              want_into=1 ;;
    --without-*)       WITHOUT="$WITHOUT${a#--without-} " ;;
    -h|--help)         sed -n '2,44p' "$0" | sed 's/^# \{0,1\}//'; exit 0 ;;
    *) echo "not a switch: $a  (--help says what there is)"; exit 2 ;;
    esac
done
[ $want_into -eq 1 ] && { echo "--to wants a path after it"; exit 2; }
wanted() { case "$WITHOUT" in *" $1 "*) return 1 ;; *) return 0 ;; esac; }

size_of() { du -sh "$1" 2>/dev/null | cut -f1; }
LINES=()    # what the summary prints
GOING=()    # what gets deleted
COUNT=0     # bash 3.2 with set -u calls an empty array unbound, so the
            # question "is there anything" gets its own counter

note() {    # note <path> <what it is>
    [ -e "$1" ] || return 0
    LINES+=("$(printf '  %-7s %s\n           %s' "$(size_of "$1")" "$2" "$1")")
    GOING+=("$1")
    COUNT=$((COUNT + 1))
}

echo "======================================================================"
echo " Back to a first run -- videopodcast-magic"
echo "======================================================================"
echo " Python: $("$PY" -c 'import sys; print(sys.executable)' 2>/dev/null)"
echo " Cache:  $CACHE"
echo

# --- 1. The environment: the thing actually under test -----------------
if wanted environment; then
    echo "1. The environment the separation runs in"
    note "$CACHE/pyannote" "the environment and the worker file"
    if [ ! -d "$CACHE/pyannote" ] \
       || [ -z "$(ls -A "$CACHE/pyannote" 2>/dev/null)" ]; then
        echo "   (already empty -- nothing set up here yet)"
    fi
    echo
fi

# --- 2. What the program keeps between runs ----------------------------
if wanted cache; then
    echo "2. What the program keeps between runs"
    for n in envelopes preflight speakers speech huellkurven vorflug; do
        case "$n" in
        envelopes)   w="envelopes of the sound tracks" ;;
        preflight)   w="preflight measurements: length, channels, timecode" ;;
        speakers)    w="separations already computed" ;;
        speech)      w="the compiled macOS recogniser" ;;
        huellkurven) w="DEAD: a name from before, nothing reads it" ;;
        vorflug)     w="DEAD: a name from before, nothing reads it" ;;
        esac
        note "$CACHE/$n" "$w"
    done
    note "$CACHE/protokoll.log" "DEAD: the log under its old name"
    note "$REPO/videopodcast-magic.log"   "the log beside the program"
    note "$REPO/videopodcast-magic_1.log" "the log beside the program"
    note "$REPO/__pycache__" "compiled Python left over"
    note "$HOME/.lhotse" "DEAD: left over from the separation measurements"
    echo
fi

# --- 3. The packages the program fetches for itself --------------------
FOUND=""
if wanted modules; then
    echo "3. The packages the program installs by itself"
    for m in $MODULES; do
        v=$("$PY" -m pip show "$m" 2>/dev/null | awk '/^Version:/{print $2}')
        [ -n "$v" ] && { echo "   $m $v"; FOUND="$FOUND $m"; }
    done
    [ -z "$FOUND" ] && echo "   (none of them is here)"
    echo "   Careful: whatever else in this interpreter stands on numpy --"
    echo "   scipy, scikit-learn, numba, OpenCV -- is broken until it is"
    echo "   back. The program fetches it again on the next start; other"
    echo "   work does not."
    echo
fi
FOUND_TORCH=""
if wanted torch; then
    echo "4. torch and what came with it"
    for m in $TORCH; do
        v=$("$PY" -m pip show "$m" 2>/dev/null | awk '/^Version:/{print $2}')
        [ -n "$v" ] && { echo "   $m $v"; FOUND_TORCH="$FOUND_TORCH $m"; }
    done
    [ -z "$FOUND_TORCH" ] && echo "   (none of it is here)"
    echo "   The environment is built with --system-site-packages: with a"
    echo "   torch already in this interpreter it fetches 58 MB instead of"
    echo "   218, and the first run measures a shortcut."
    echo "   Nothing brings these back on their own. The environment gets"
    echo "   its own torch and leaves this interpreter alone, so whatever"
    echo "   here stands on torch stays broken until it is installed by"
    echo "   hand. Leave the group out with --without-torch."
    echo
fi

# --- 5. The model the program fetches for itself -----------------------
# Only that one. The store is shared with everything else on the machine
# that speaks to Hugging Face, and a reset for this program has no
# business in another one's models.
if wanted models; then
    echo "5. The speech model in the Hugging Face store"
    if [ -d "$HF" ]; then
        for d in "$HF"/models--*whisper*turbo*; do
            [ -e "$d" ] || continue
            n=$(basename "$d"); n=${n#models--}; n=${n//--//}
            note "$d" "$n -- fetched again where macOS does not recognise"
        done
        others=$(ls -d "$HF"/models--* 2>/dev/null | grep -cv "whisper.*turbo")
        if [ "${others:-0}" -gt 0 ]; then
            echo "   $others other models in the store are left alone --"
            echo "   they belong to other work, not to this program."
        fi
    else
        echo "   (no Hugging Face store here)"
    fi
    echo
fi

# --- 6. pip's download store -------------------------------------------
if wanted pip; then
    echo "6. pip's download store"
    echo "   Left in place, pip takes the packages off the shelf instead"
    echo "   of the network, and a first install is not what is measured."
    note "$PIPCACHE" "packages already downloaded"
    echo
fi

# --- 7. The keychain ----------------------------------------------------
KEY=0
if wanted keychain && [ "$(uname -s)" = "Darwin" ]; then
    echo "7. The keychain"
    if security find-generic-password -s videopodcast-magic \
            -a auphonic > /dev/null 2>&1; then
        echo "   The auphonic key is in the keychain and goes with the"
        echo "   rest; the window asks for it again. Have it ready -- this"
        echo "   script never reads it and cannot put it back."
        KEY=1
    else
        echo "   (no entry)"
    fi
    echo
fi

# --- The summary --------------------------------------------------------
echo "----------------------------------------------------------------------"
echo " What goes"
echo "----------------------------------------------------------------------"
if [ $COUNT -eq 0 ] && [ -z "$FOUND$FOUND_TORCH" ] && [ $KEY -eq 0 ]; then
    echo " Nothing. The machine already stands that way."
    exit 0
fi
[ $COUNT -gt 0 ] && for z in "${LINES[@]}"; do echo "$z"; done
[ -n "$FOUND" ]       && echo "  packages: $FOUND"
[ -n "$FOUND_TORCH" ] && echo "  torch:    $FOUND_TORCH"
[ $KEY -eq 1 ]        && echo "  keychain: videopodcast-magic/auphonic"
echo
if [ $COUNT -gt 0 ]; then
    echo -n " On disc together: "
    du -shc "${GOING[@]}" 2>/dev/null | tail -1 | cut -f1
fi
echo
echo " Staying: models/ beside the program, the project folders, ffmpeg."
echo

if [ $FOR_REAL -eq 0 ]; then
    echo " Nothing deleted -- that was the look beforehand."
    echo " Delete it with:  bash $0 --for-real"
    exit 0
fi

printf " Delete all of that? Type  yes  and press return: "
read -r answer
[ "$answer" = "yes" ] || { echo " Stopped, nothing touched."; exit 1; }
echo

# --- Doing it -----------------------------------------------------------
if [ $COUNT -gt 0 ]; then
    for p in "${GOING[@]}"; do
        [ -n "$p" ] && [ -e "$p" ] || continue
        rm -rf -- "$p" && echo " gone: $p"
    done
fi
if [ -n "$FOUND$FOUND_TORCH" ]; then
    echo " uninstalling:$FOUND$FOUND_TORCH"
    "$PY" -m pip uninstall -y $FOUND $FOUND_TORCH 2>&1 \
        | grep -i "success\|not installed" | sed 's/^/   /'
    # pip leaves the __pycache__ folder of a package behind, and Python
    # reads that folder as a namespace package: the import goes through
    # and the module is hollow, so the program takes the shell for the
    # package and never installs it. No fresh machine is in that state.
    "$PY" - <<'EOF' 
import os, shutil, site, sys

roots = set(site.getsitepackages())
try:
    roots.add(site.getusersitepackages())
except Exception:
    pass
for name in ("numpy", "PySide6", "certifi", "faster_whisper",
             "torch", "torchaudio", "shiboken6"):
    for root in roots:
        folder = os.path.join(root, name)
        if not os.path.isdir(folder):
            continue
        # Only a shell: nothing in it but compiled leftovers.
        alive = [f for _, _, fs in os.walk(folder) for f in fs
                 if not f.endswith((".pyc", ".pyo"))]
        if alive:
            continue
        try:
            shutil.rmtree(folder)
            print("   left-over package removed: %s" % folder)
        except OSError as e:
            print("   %s" % e)
EOF
fi
if [ $KEY -eq 1 ]; then
    security delete-generic-password -s videopodcast-magic \
        -a auphonic > /dev/null 2>&1 && echo " gone: the keychain entry"
fi

echo
echo "======================================================================"
echo " Done. The next start is a first run."
echo "======================================================================"

if [ $THEN_INSTALL -eq 1 ]; then
    echo " Installing again, the way a stranger would."
    echo " Into: $INTO"
    echo "-------------------------------------------------------------------"
    mkdir -p "$INTO" || { echo " $INTO cannot be made."; exit 1; }
    if [ $FROM_HERE -eq 1 ]; then
        # Every file of the program, not the one: the texts stand
        # beside it, one file per language, and it reads them from
        # there. Named by shape, so a language added later travels too.
        cp "$REPO"/videopodcast_magic*.py "$INTO/" || exit 1
        echo " taken from $REPO"
    else
        # The state at main, fetched and started. Not one file any
        # more: the texts stand beside the program, one per language,
        # and the program without them dies on import. Which files
        # those are is asked of github.com rather than written down
        # here, so a language added later travels by itself -- the same
        # shape the branch above copies by, and the same one
        # .github/workflows/release.yml fetches a tag by.
        API="https://api.github.com/repos/Bascht74"
        API="$API/videopodcast-magic/contents?ref=main"
        RAW="https://raw.githubusercontent.com/Bascht74"
        RAW="$RAW/videopodcast-magic/main"
        if ! "$PY" - "$API" "$RAW" "$INTO" <<'EOF'
import json, re, subprocess, sys
api, raw, into = sys.argv[1:4]


def curl(url, *more):
    """What an address answers, over curl rather than urllib.

    A Python from python.org verifies against a certificate store macOS
    never gives it -- measured 4.9.2026, urlretrieve here died on
    CERTIFICATE_VERIFY_FAILED against raw.githubusercontent.com. curl
    carries its own. tests/text_release_ready_test.py fetches the same
    way and says the same thing.
    """
    return subprocess.run(["curl", "-fsSL", url] + list(more),
                          stdout=subprocess.PIPE)


got = curl(api)
if got.returncode:
    sys.exit(" github.com did not answer (curl %d)" % got.returncode)
names = [one["name"] for one in json.loads(got.stdout)
         if re.match(r"videopodcast_magic.*[.]py$", one["name"])]
if not names:
    sys.exit(" github.com named no file the program is made of")
for name in names:
    if curl(raw + "/" + name, "-o", into + "/" + name).returncode:
        sys.exit(" %s did not come down" % name)
print(" %d files: the program and the texts beside it" % len(names))
EOF
        then
            echo " The program could not be fetched. Nothing installed."
            exit 1
        fi
        echo " fetched from github.com"
    fi
    cd "$INTO" || exit 1
    exec "$PY" videopodcast_magic.py
fi

echo " What happens by itself from here:"
echo "   * numpy and PySide6 are fetched before the window opens"
echo "   * the environment is built the first time a separation is asked"
echo "     for -- 218 MB and some minutes"
echo "   * envelopes and preflight are measured again"
echo "   * the macOS recogniser is compiled once, about a second"
echo
echo " Not coming back on their own -- by hand, if something else on"
echo " this machine needs them:"
echo "   $PY -m pip install torch torchaudio"
