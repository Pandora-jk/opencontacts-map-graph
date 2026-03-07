#!/usr/bin/env bash
set -euo pipefail

if [[ $# -lt 2 ]]; then
  echo "Usage: scripts/git-feature-start.sh <project-slug> <task-slug>"
  echo "Example: scripts/git-feature-start.sh automation-scripts csv-validator"
  exit 1
fi

PROJECT="$1"
TASK="$2"
DATE_TAG="$(date +%F)"
BRANCH="feature/${PROJECT}-${TASK}-${DATE_TAG}"

is_obsidian_repo() {
  local remote_url top repo_name
  remote_url="$(git remote get-url origin 2>/dev/null || true)"
  top="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
  repo_name="$(basename "$top")"
  [[ "$remote_url" == *obsidian* || "$repo_name" == *obsidian* ]]
}

git rev-parse --is-inside-work-tree >/dev/null 2>&1 || {
  echo "Not inside a git repository."
  exit 1
}

if is_obsidian_repo; then
  echo "Feature branches are blocked for the Obsidian repository. Stay on main/master."
  exit 2
fi

CURRENT="$(git rev-parse --abbrev-ref HEAD)"
if [[ "${CURRENT}" != "main" && "${CURRENT}" != "master" ]]; then
  echo "Current branch is ${CURRENT}. Switching from current branch baseline."
fi

git checkout -b "${BRANCH}"
echo "Created and checked out ${BRANCH}"
