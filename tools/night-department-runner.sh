#!/usr/bin/env bash
set -euo pipefail

WORKSPACE="/home/ubuntu/.openclaw/workspace"
DEPARTMENT="${1:-}"
if [[ -z "$DEPARTMENT" ]]; then
  echo "Usage: $0 <coding|infra>"
  exit 2
fi
if [[ "$DEPARTMENT" != "coding" && "$DEPARTMENT" != "infra" ]]; then
  echo "Unsupported department: $DEPARTMENT"
  exit 2
fi

SYD_HOUR="$(TZ='Australia/Sydney' date +%H)"
CODING_ALLOW_DAY="${CODING_ALLOW_DAY:-0}"
if [[ "$DEPARTMENT" == "coding" ]]; then
  # Coding night window: 00:00-05:59 Sydney
  if (( 10#${SYD_HOUR} >= 6 )) && [[ "$CODING_ALLOW_DAY" != "1" ]]; then
    echo "Coding night window inactive (Sydney hour=${SYD_HOUR}). Skipping."
    exit 0
  fi
else
  # Infra night window: 22:00-05:59 Sydney
  if (( 10#${SYD_HOUR} >= 6 && 10#${SYD_HOUR} < 22 )); then
    echo "Infra night window inactive (Sydney hour=${SYD_HOUR}). Skipping."
    exit 0
  fi
fi

LOG_DIR="${WORKSPACE}/logs"
mkdir -p "${LOG_DIR}"
STAMP="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
if [[ "$DEPARTMENT" == "coding" && "$CODING_ALLOW_DAY" == "1" ]]; then
  LOG_FILE="${LOG_DIR}/day-${DEPARTMENT}.log"
else
  LOG_FILE="${LOG_DIR}/night-${DEPARTMENT}.log"
fi

TASK_CODING_NIGHT="Night coding sprint in ${WORKSPACE}: pick the top Ready coding kanban task, work on a feature branch, implement in small steps, run tests, then commit and push to GitHub origin before finishing."
TASK_CODING_DAY="Day coding sprint in ${WORKSPACE}: pick the top Ready coding kanban task, work on a feature branch, implement in small steps, run tests, then commit and push to GitHub origin before finishing."
TASK_INFRA="Night infra sprint in ${WORKSPACE}: pick the top infra reliability/security task from TODO and logs, implement safe hardening changes, and verify with checks."

if [[ "$DEPARTMENT" == "coding" ]]; then
  if [[ "$CODING_ALLOW_DAY" == "1" ]]; then
    TASK="$TASK_CODING_DAY"
  else
    TASK="$TASK_CODING_NIGHT"
  fi
else
  TASK="$TASK_INFRA"
fi

pick_cli() {
  if [[ -n "${NIGHT_DEV_CLI:-}" ]]; then
    if command -v "${NIGHT_DEV_CLI}" >/dev/null 2>&1; then
      echo "${NIGHT_DEV_CLI}"
      return
    fi
  fi
  if pgrep -f "codex" >/dev/null 2>&1 && command -v codex >/dev/null 2>&1; then
    echo "codex"
    return
  fi
  if pgrep -f "claude" >/dev/null 2>&1 && command -v claude >/dev/null 2>&1; then
    echo "claude"
    return
  fi
  if command -v codex >/dev/null 2>&1; then
    echo "codex"
    return
  fi
  if command -v claude >/dev/null 2>&1; then
    echo "claude"
    return
  fi
  echo ""
}

CLI="$(pick_cli)"
if [[ -z "$CLI" ]]; then
  echo "[${STAMP}] ${DEPARTMENT}: no codex/claude CLI found" | tee -a "$LOG_FILE"
  if [[ "$DEPARTMENT" == "coding" ]]; then
    python3 "${WORKSPACE}/tools/coding-autopilot.py" --emit-telegram >> "$LOG_FILE" 2>&1 || true
    echo "NIGHT_${DEPARTMENT^^}_OK cli=deterministic fallback=no_dev_cli log=${LOG_FILE}"
    exit 0
  fi
  exit 1
fi

RUN_OUT=""
RUN_RC=0
has_pattern() {
  local text="$1"
  local pat="$2"
  if command -v rg >/dev/null 2>&1; then
    printf '%s' "$text" | rg -qi "$pat"
    return $?
  fi
  printf '%s' "$text" | grep -Eiq "$pat"
}

run_coding_fallback() {
  local reason="$1"
  local fallback_out=""
  local fallback_rc=0

  set +e
  fallback_out=$(python3 "${WORKSPACE}/tools/coding-autopilot.py" --emit-telegram 2>&1)
  fallback_rc=$?
  set -e

  {
    echo "[$STAMP] department=${DEPARTMENT} cli=deterministic fallback_reason=${reason}"
    echo "${fallback_out}"
    echo "-----"
  } >> "$LOG_FILE"

  if (( fallback_rc == 0 )); then
    echo "NIGHT_${DEPARTMENT^^}_OK cli=deterministic fallback=${reason} log=${LOG_FILE}"
    exit 0
  fi

  echo "NIGHT_${DEPARTMENT^^}_FAIL cli=deterministic rc=${fallback_rc} fallback=${reason} log=${LOG_FILE}"
  exit 1
}

should_use_coding_fallback() {
  local text="$1"
  has_pattern "$text" "failed to connect to websocket|stream disconnected before completion|error sending request for url|Operation not permitted \\(os error 1\\)|codex CLI not found in PATH|no codex/claude CLI found"
}

if [[ "$CLI" == "codex" ]]; then
  set +e
  # Use nohup to preserve stdin for claude -p mode fallback
  RUN_OUT=$(bash "${WORKSPACE}/tools/oc-codex.sh" --workdir "${WORKSPACE}" --task "${TASK}" --timeout 900 2>&1)
  RUN_RC=$?
  set -e
  # Codex may ask for user direction when unrelated local changes are present.
  if has_pattern "$RUN_OUT" "need your direction|how do you want me to handle|unrelated local changes"; then
    if command -v claude >/dev/null 2>&1; then
      CLI="claude"
      set +e
      # Use stdbuf to preserve stdin for claude -p mode
      RUN_OUT=$(stdbuf -oL timeout 900 claude -p --permission-mode dontAsk --add-dir "${WORKSPACE}" "${TASK}" 2>&1)
      RUN_RC=$?
      set -e
    fi
  fi
else
  set +e
  # Use stdbuf to preserve stdin for claude -p mode
  RUN_OUT=$(stdbuf -oL timeout 900 claude -p --permission-mode dontAsk --add-dir "${WORKSPACE}" "${TASK}" 2>&1)
  RUN_RC=$?
  set -e
fi

{
  echo "[$STAMP] department=${DEPARTMENT} cli=${CLI}"
  echo "${RUN_OUT}"
  echo "-----"
} >> "$LOG_FILE"

if [[ "$DEPARTMENT" == "coding" ]] && should_use_coding_fallback "$RUN_OUT"; then
  run_coding_fallback "llm_transport_unavailable"
fi

if (( RUN_RC == 0 )) && ! has_pattern "$RUN_OUT" "ERROR:|Failed to shutdown rollout recorder|stream disconnected before completion"; then
  if [[ "$DEPARTMENT" == "coding" ]]; then
    set +e
    ENFORCE_OUT="$(bash "${WORKSPACE}/tools/coding-git-enforce.sh" \
      --repo "${WORKSPACE}" \
      --auto-branch \
      --auto-commit \
      --push \
      --message "chore(coding): autonomous night run ${STAMP}" 2>&1)"
    ENFORCE_RC=$?
    set -e
    {
      echo "[$STAMP] department=${DEPARTMENT} git_enforce_rc=${ENFORCE_RC}"
      echo "${ENFORCE_OUT}"
      echo "-----"
    } >> "$LOG_FILE"
    if (( ENFORCE_RC != 0 )); then
      echo "NIGHT_${DEPARTMENT^^}_FAIL cli=${CLI} rc=${ENFORCE_RC} log=${LOG_FILE}"
      exit 1
    fi
  fi
  echo "NIGHT_${DEPARTMENT^^}_OK cli=${CLI} log=${LOG_FILE}"
  exit 0
fi

echo "NIGHT_${DEPARTMENT^^}_FAIL cli=${CLI} rc=${RUN_RC} log=${LOG_FILE}"
exit 1
