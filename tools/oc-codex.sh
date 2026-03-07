#!/usr/bin/env bash
# OC Codex runner: stable entrypoint for invoking Codex from OpenClaw.

set -euo pipefail

WORKDIR="${PWD}"
TASK=""
MODEL=""
INIT_GIT=0
YOLO=0
TIMEOUT=0

usage() {
  cat <<'EOF'
Usage:
  tools/oc-codex.sh --task "your coding task" [options]

Options:
  --task TEXT        Required task prompt for Codex.
  --workdir PATH     Working directory for Codex run (default: current dir).
  --model MODEL      Optional Codex model override.
  --init-git         If workdir is not a git repo, run `git init` first.
  --yolo             Use --yolo mode (no sandbox / no approvals). Use carefully.
  --timeout SEC      Command timeout in seconds (0 = no timeout, default).
  -h, --help         Show help.

Examples:
  tools/oc-codex.sh --workdir ~/project --task "Add unit tests for parser.py"
  tools/oc-codex.sh --workdir ~/scratch --init-git --task "Create a hello-world Flask app"
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --task) TASK="${2:-}"; shift 2 ;;
    --workdir) WORKDIR="${2:-}"; shift 2 ;;
    --model) MODEL="${2:-}"; shift 2 ;;
    --init-git) INIT_GIT=1; shift ;;
    --yolo) YOLO=1; shift ;;
    --timeout) TIMEOUT="${2:-0}"; shift 2 ;;
    -h|--help) usage; exit 0 ;;
    *) echo "Unknown argument: $1" >&2; usage; exit 2 ;;
  esac
done

if [[ -z "$TASK" ]]; then
  echo "Missing required --task." >&2
  usage
  exit 2
fi

if ! command -v codex >/dev/null 2>&1; then
  echo "codex CLI not found in PATH." >&2
  exit 127
fi

mkdir -p "$WORKDIR"
cd "$WORKDIR"

if [[ ! -d .git ]]; then
  if [[ "$INIT_GIT" -eq 1 ]]; then
    git init >/dev/null
  else
    echo "Workdir is not a git repo: $WORKDIR" >&2
    echo "Re-run with --init-git to bootstrap a repo." >&2
    exit 3
  fi
fi

CMD=(codex exec --full-auto)
if [[ -n "$MODEL" ]]; then
  CMD+=(--model "$MODEL")
fi
if [[ "$YOLO" -eq 1 ]]; then
  CMD=(codex --yolo)
  if [[ -n "$MODEL" ]]; then
    CMD+=(--model "$MODEL")
  fi
fi
CMD+=("$TASK")

if [[ "$TIMEOUT" -gt 0 ]]; then
  timeout "$TIMEOUT" "${CMD[@]}"
else
  "${CMD[@]}"
fi
