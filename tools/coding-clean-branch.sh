#!/usr/bin/env bash
set -euo pipefail

REPO="${PWD}"
BRANCH=""
WORKTREE=""
MESSAGE=""

EXCLUDE_GLOBS=(
  "logs/**"
  "departments/*/STATUS.md"
  "departments/*/artifacts/**"
  "memory/SESSION-SUMMARY-*"
  "memory/*-autopilot-state.json"
  "memory/proactive-pulse-state.json"
  "system/*.bak-*"
  "**/__pycache__/**"
  "**/*.pyc"
)

usage() {
  cat <<'EOF'
Usage: tools/coding-clean-branch.sh [options]

Options:
  --repo PATH       Source git repository (default: current directory).
  --branch NAME     Target clean branch name.
  --worktree PATH   Target worktree path (default: /tmp/<repo>-clean-<stamp>).
  --message TEXT    Commit message for the clean snapshot.
  -h, --help        Show help.

Creates a clean orphan branch in a separate worktree from the current working
tree, omitting generated/runtime paths that should not be part of the rescue
snapshot.
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --repo) REPO="${2:-}"; shift 2 ;;
    --branch) BRANCH="${2:-}"; shift 2 ;;
    --worktree) WORKTREE="${2:-}"; shift 2 ;;
    --message) MESSAGE="${2:-}"; shift 2 ;;
    -h|--help) usage; exit 0 ;;
    *) echo "Unknown argument: $1" >&2; usage; exit 2 ;;
  esac
done

if [[ ! -d "$REPO/.git" ]]; then
  echo "CLEAN_BRANCH_FAIL: not a git repo: $REPO"
  exit 2
fi

REPO="$(cd "$REPO" && pwd)"
SOURCE_BRANCH="$(git -C "$REPO" rev-parse --abbrev-ref HEAD)"
STAMP="$(date -u +%Y%m%d-%H%M%S)"
SAFE_SOURCE_BRANCH="${SOURCE_BRANCH//\//-}"

if [[ -z "$BRANCH" ]]; then
  BRANCH="feature/clean-snapshot-${SAFE_SOURCE_BRANCH}-${STAMP}"
fi

if [[ -z "$WORKTREE" ]]; then
  WORKTREE="/tmp/$(basename "$REPO")-clean-${STAMP}"
fi

if [[ -z "$MESSAGE" ]]; then
  MESSAGE="chore(repo): clean snapshot from ${SOURCE_BRANCH} ${STAMP}"
fi

if git -C "$REPO" show-ref --verify --quiet "refs/heads/${BRANCH}"; then
  echo "CLEAN_BRANCH_FAIL: branch already exists: ${BRANCH}"
  exit 3
fi

if [[ -e "$WORKTREE" ]]; then
  echo "CLEAN_BRANCH_FAIL: worktree path already exists: $WORKTREE"
  exit 4
fi

SOURCE_FILES=()
LIST_CMD=(git -C "$REPO" ls-files -z --cached --others --exclude-standard -- .)
for pat in "${EXCLUDE_GLOBS[@]}"; do
  LIST_CMD+=(":(exclude,glob)$pat")
done
mapfile -d '' SOURCE_FILES < <("${LIST_CMD[@]}")

if [[ "${#SOURCE_FILES[@]}" -eq 0 ]]; then
  echo "CLEAN_BRANCH_FAIL: no source files selected for snapshot"
  exit 5
fi

git -C "$REPO" worktree add --detach "$WORKTREE" HEAD >/dev/null
git -C "$WORKTREE" switch --orphan "$BRANCH" >/dev/null

while IFS= read -r -d '' existing; do
  rm -rf "$existing"
done < <(find "$WORKTREE" -mindepth 1 -maxdepth 1 ! -name .git -print0)

for rel in "${SOURCE_FILES[@]}"; do
  src="$REPO/$rel"
  dst="$WORKTREE/$rel"
  if [[ ! -e "$src" && ! -L "$src" ]]; then
    continue
  fi
  mkdir -p "$(dirname "$dst")"
  cp -a "$src" "$dst"
done

git -C "$WORKTREE" add -A

if git -C "$WORKTREE" diff --cached --quiet; then
  echo "CLEAN_BRANCH_FAIL: clean snapshot produced no staged changes"
  exit 6
fi

git -C "$WORKTREE" -c commit.gpgsign=false commit -m "$MESSAGE" >/dev/null

SCANNER="$REPO/tools/git-secret-scan.py"
if [[ -f "$SCANNER" ]]; then
  python3 "$SCANNER" --repo "$WORKTREE" >/tmp/coding-clean-branch-tracked.out || {
    cat /tmp/coding-clean-branch-tracked.out
    echo "CLEAN_BRANCH_FAIL: clean snapshot still includes tracked secret patterns"
    exit 7
  }
  python3 "$SCANNER" --repo "$WORKTREE" --history-ref HEAD --max-commits 20 >/tmp/coding-clean-branch-history.out || {
    cat /tmp/coding-clean-branch-history.out
    echo "CLEAN_BRANCH_FAIL: clean snapshot history still includes secret patterns"
    exit 8
  }
fi

echo "CLEAN_BRANCH_OK repo=$REPO source_branch=$SOURCE_BRANCH branch=$BRANCH worktree=$WORKTREE files=${#SOURCE_FILES[@]}"
