#!/usr/bin/env bash
# Has the tree of this merge commit already been tested, green, as the
# head of the pull request it merges?
#
#   bash .github/tree_tested.sh <sha> [<owner/repo>]
#
# Three questions, asked of the API and not of a checkout, so it
# answers the same on a runner and on a laptop, and a clone of the
# whole history is not needed for it:
#
#   a. Is <sha> a merge -- does it have two parents?
#   b. Is its tree the tree of its second parent, the pull request's
#      head? The same question as `git diff --quiet <sha>^2 <sha>`,
#      asked of the tree ids: one tree id is the same bytes. Identical
#      means nothing else landed on main between the pull request and
#      the merge -- the one case where "green apart, broken together"
#      cannot happen.
#   c. Did every job of the suite conclude success on that head? The
#      names are read off tests.yml at <sha> -- the suite job's name
#      with each matrix row put into it -- so a job added to the
#      matrix is asked about without this file being touched. A wanted
#      name with no check run, or with any run of it not success
#      (a rerun that went red, one still running), is no evidence.
#
# These are the questions a. to c. of publish.yml's evidence job,
# written once here so tests.yml asks them the same way (see its job
# "gate"). publish.yml's evidence job calls this file too; its d.
# (the speaker separation) is about a release and does not belong here.
#
# Exit 0: yes to all three. Exit 1: no -- including GitHub not
# answering, which is never a yes. Exit 3: tests.yml at <sha> could
# not be read for its job names, a fault of its own.
#
# What it found is left in $TREE_TESTED_DIR (a fresh folder if unset):
# reason.txt (one line, the fact without its consequence), head.json,
# wanted.txt, runs.txt, and run.txt -- the number of the tests.yml
# run(s) of the head, for the reader; empty if GitHub would not say.
# Needs gh, jq, python3 with PyYAML; reads contents, checks, actions.
set -u
SHA=${1:?"usage: tree_tested.sh <sha> [<owner/repo>]"}
R=${2:-${GITHUB_REPOSITORY:-$(gh repo view --json nameWithOwner -q .nameWithOwner)}}
D=${TREE_TESTED_DIR:-$(mktemp -d)}
mkdir -p "$D"
: > "$D/run.txt"
short="${SHA:0:7}"

no() {
  printf '%s\n' "$1" | tr -d '\r' | head -n 1 > "$D/reason.txt"
  echo "no: $(cat "$D/reason.txt")"
  exit 1
}

# a. Two parents.
if ! gh api "repos/$R/commits/$SHA" > "$D/head.json"; then
  no "GitHub did not answer for $short"
fi
SHA=$(jq -r '.sha' "$D/head.json")
parents=$(jq -r '.parents | length' "$D/head.json")
tree=$(jq -r '.commit.tree.sha' "$D/head.json")
if [ "$parents" != "2" ]; then
  no "$short has $parents parent(s), not two: it is not the merge of a pull request"
fi
head2=$(jq -r '.parents[1].sha' "$D/head.json")
echo "merge:  $SHA"
echo "head:   $head2 (second parent, the pull request's head)"

# b. One tree.
if ! tree2=$(gh api "repos/$R/commits/$head2" --jq .commit.tree.sha); then
  no "GitHub did not answer for ${head2:0:7}"
fi
echo "tree:   $tree"
echo "tree':  $tree2"
if [ "$tree" != "$tree2" ]; then
  no "main moved: the tree of $short is not the tree of ${head2:0:7}, so this tree was never tested as it is"
fi

# The run(s) that tested the head, named for the reader only -- the
# decision below rests on the check runs, not on this.
gh api "repos/$R/actions/runs?head_sha=$head2&per_page=100" \
  --jq '[.workflow_runs[]
         | select(.path | startswith(".github/workflows/tests.yml"))
         | "#\(.run_number)"] | unique | join(", ")' \
  > "$D/run.txt" 2>/dev/null || : > "$D/run.txt"

# c. Every job of the suite, green on that head.
if ! gh api "repos/$R/contents/.github/workflows/tests.yml?ref=$SHA" \
       --jq .content | base64 -d > "$D/tests.yml" 2> "$D/why.txt" \
   || ! python3 - "$D/tests.yml" > "$D/wanted.txt" 2>> "$D/why.txt" <<'PY'
import re, sys
try:
    import yaml
except ImportError:
    sys.exit("no PyYAML here")
suite = yaml.safe_load(open(sys.argv[1]))["jobs"]["suite"]
name = suite["name"]
for row in suite["strategy"]["matrix"]["include"]:
    print(re.sub(r"\$\{\{\s*matrix\.(\w+)\s*\}\}",
                 lambda m: str(row[m.group(1)]), name))
PY
then
  echo "FAIL: tests.yml at $short could not be read for the names of"
  echo "      the suite's jobs: $(tr '\n' ' ' < "$D/why.txt")"
  echo "tests.yml at $short could not be read for its job names" > "$D/reason.txt"
  exit 3
fi
n=$(grep -c '' "$D/wanted.txt" || true)
if [ "$n" = "0" ]; then
  echo "FAIL: tests.yml at $short names no job in its matrix."
  echo "tests.yml at $short names no job in its matrix" > "$D/reason.txt"
  exit 3
fi

if ! gh api --paginate "repos/$R/commits/$head2/check-runs" \
       --jq '.check_runs[] | .name + "\t" + (.conclusion // "unfinished")' \
       > "$D/runs.txt"; then
  no "GitHub did not answer for the check runs of ${head2:0:7}"
fi
echo "check runs of ${head2:0:7}:"
sed 's/^/  /' "$D/runs.txt"
missing=""
notgreen=""
while IFS= read -r want; do
  [ -n "$want" ] || continue
  got=$(awk -F'\t' -v w="$want" '$1 == w {print $2}' "$D/runs.txt")
  if [ -z "$got" ]; then
    missing="$missing '$want'"
  elif printf '%s\n' "$got" | grep -qvx success; then
    notgreen="$notgreen '$want'"
  fi
done < "$D/wanted.txt"
if [ -n "$missing$notgreen" ]; then
  no "the tree of $short is the tree of ${head2:0:7}, but of its $n jobs these have no check run:${missing:- none}, and these did not conclude success:${notgreen:- none}"
fi

names=$(paste -sd ',' "$D/wanted.txt" | sed 's/,/, /g')
echo "the tree of $short is the tree of ${head2:0:7}, the head of the pull request it merges, and all $n jobs of that head ($names) concluded success" > "$D/reason.txt"
echo "yes: $(cat "$D/reason.txt")"
exit 0
