#!/usr/bin/env bash
set -euo pipefail

REPO=""
AUTO_BRANCH=0
AUTO_COMMIT=0
PUSH=0
COMMIT_MSG=""
EXCLUDE_PATHS=(
  ":(exclude,glob)logs/**"
  ":(exclude,glob)memory/SESSION-SUMMARY-*"
  ":(exclude,glob)system/*.bak-*"
  ":(exclude,glob)**/__pycache__/**"
  ":(exclude,glob)**/*.pyc"
)

is_obsidian_repo() {
  local remote_url top repo_name
  remote_url="$(git remote get-url origin 2>/dev/null || true)"
  top="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
  repo_name="$(basename "$top")"
  [[ "$remote_url" == *obsidian* || "$repo_name" == *obsidian* ]]
}

usage() {
  cat <<'EOF'
Usage: tools/coding-git-enforce.sh --repo <path> [options]

Options:
  --repo PATH     Git repository path to enforce.
  --auto-branch   If current branch is not feature/*, create/switch to generated feature branch.
  --auto-commit   If working tree is dirty, stage and create one commit automatically.
  --push          Push branch to origin and fail if unpushed commits remain.
  --message TEXT  Commit message used with --auto-commit.
  -h, --help      Show help.
EOF
}

secret_scan() {
  local scanner="$REPO/tools/git-secret-scan.py"
  if [[ ! -f "$scanner" ]]; then
    echo "GIT_ENFORCE_FAIL: missing secret scanner: $scanner"
    exit 10
  fi
  python3 "$scanner" --repo "$REPO" "$@"
}

relevant_status_count() {
  git status --porcelain -- . "${EXCLUDE_PATHS[@]}" | wc -l | tr -d ' '
}

stage_relevant_changes() {
  git add -A -- . "${EXCLUDE_PATHS[@]}"
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --repo) REPO="${2:-}"; shift 2 ;;
    --auto-branch) AUTO_BRANCH=1; shift ;;
    --auto-commit) AUTO_COMMIT=1; shift ;;
    --push) PUSH=1; shift ;;
    --message) COMMIT_MSG="${2:-}"; shift 2 ;;
    -h|--help) usage; exit 0 ;;
    *) echo "Unknown argument: $1" >&2; usage; exit 2 ;;
  esac
done

if [[ -z "$REPO" ]]; then
  echo "Missing required --repo." >&2
  usage
  exit 2
fi

if [[ ! -d "$REPO/.git" ]]; then
  echo "GIT_ENFORCE_FAIL: not a git repo: $REPO"
  exit 3
fi

cd "$REPO"

branch="$(git rev-parse --abbrev-ref HEAD)"

if is_obsidian_repo; then
  if [[ "$branch" != "main" && "$branch" != "master" ]]; then
    echo "GIT_ENFORCE_FAIL: obsidian repo must stay on main/master (current: '$branch')"
    exit 4
  fi
  if [[ "$AUTO_BRANCH" -eq 1 ]]; then
    echo "Obsidian repo detected. Staying on $branch."
  fi
elif [[ ! "$branch" =~ ^feature/ ]]; then
  if [[ "$AUTO_BRANCH" -eq 1 ]]; then
    stamp="$(date -u +%Y%m%d-%H%M%S)"
    new_branch="feature/autopilot-${stamp}"
    git checkout -b "$new_branch" >/dev/null 2>&1 || git checkout "$new_branch" >/dev/null 2>&1
    branch="$new_branch"
  else
    echo "GIT_ENFORCE_FAIL: branch '$branch' is not feature/*"
    exit 4
  fi
fi

remote_url="$(git remote get-url origin 2>/dev/null || true)"
if [[ -z "$remote_url" ]]; then
  echo "GIT_ENFORCE_FAIL: missing origin remote"
  exit 5
fi

if [[ "$remote_url" != *github.com* ]]; then
  echo "GIT_ENFORCE_FAIL: origin is not GitHub"
  exit 6
fi

if [[ "$(relevant_status_count)" != "0" ]]; then
  if [[ "$AUTO_COMMIT" -eq 1 ]]; then
    stage_relevant_changes
    if ! git diff --cached --quiet; then
      secret_scan --staged >/tmp/coding-secret-scan.out || {
        cat /tmp/coding-secret-scan.out
        echo "GIT_ENFORCE_FAIL: staged changes include likely secrets"
        exit 10
      }
    fi
    if [[ -z "$COMMIT_MSG" ]]; then
      COMMIT_MSG="chore(coding): autonomous update $(date -u +%Y-%m-%dT%H:%M:%SZ)"
    fi
    if ! git diff --cached --quiet; then
      git commit -m "$COMMIT_MSG" >/dev/null || true
    fi
  else
    echo "GIT_ENFORCE_FAIL: dirty working tree (requires commit)"
    exit 7
  fi
fi

if [[ "$PUSH" -eq 1 ]]; then
  secret_scan >/tmp/coding-secret-scan.out || {
    cat /tmp/coding-secret-scan.out
    echo "GIT_ENFORCE_FAIL: tracked files include likely secrets; sanitize repo before pushing"
    exit 10
  }
  secret_scan --history-ref HEAD >/tmp/coding-secret-history-scan.out || {
    cat /tmp/coding-secret-history-scan.out
    echo "GIT_ENFORCE_FAIL: branch history includes likely secrets; run tools/coding-clean-branch.sh --repo $REPO to create a clean rescue branch before pushing"
    exit 11
  }
  # Push current branch (main or feature/*)
  if git rev-parse --abbrev-ref --symbolic-full-name '@{u}' >/dev/null 2>&1; then
    git push >/dev/null
  else
    git push -u origin "$branch" >/dev/null
  fi
fi

ahead_count="$(git rev-list --count @{u}..HEAD 2>/dev/null || echo 0)"
dirty_count="$(relevant_status_count)"

if [[ "$ahead_count" != "0" ]]; then
  echo "GIT_ENFORCE_FAIL: branch '$branch' has unpushed commits ($ahead_count)"
  exit 8
fi

if [[ "$dirty_count" != "0" ]]; then
  echo "GIT_ENFORCE_FAIL: working tree still dirty ($dirty_count files)"
  exit 9
fi

echo "GIT_ENFORCE_OK repo=$REPO branch=$branch remote=origin"
