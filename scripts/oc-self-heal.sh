#!/bin/bash
# OpenClaw self-heal: repair common config/runtime drift.

set -euo pipefail

BASE="$HOME/.openclaw"
WORKSPACE="$BASE/workspace"
RUNTIME_CONFIG="$BASE/openclaw.json"
WORKSPACE_CONFIG="$WORKSPACE/system/openclaw.json"
SESSIONS_FILE="$BASE/agents/main/sessions/sessions.json"
LOG_DIR="$WORKSPACE/logs"
LOG_FILE="$LOG_DIR/self-heal.log"
LOCK_FILE="/tmp/oc-self-heal.lock"
TELEGRAM_CHAT_ID="${OPENCLAW_TELEGRAM_CHAT_ID:-156480904}"
OPENCLAW_BIN=""

mkdir -p "$LOG_DIR"
mkdir -p "$(dirname "$LOCK_FILE")"
export PATH="$HOME/.npm-global/bin:$HOME/.local/bin:$PATH"

timestamp() {
  date -u +"%Y-%m-%dT%H:%M:%SZ"
}

log() {
  echo "[$(timestamp)] $*" | tee -a "$LOG_FILE"
}

acquire_lock() {
  if ! command -v flock >/dev/null 2>&1; then
    log "warn: flock not available, continuing without run lock"
    return
  fi

  exec 9>"$LOCK_FILE"
  if ! flock -n 9; then
    log "warn: another self-heal run is active, skipping duplicate run"
    exit 0
  fi
}

resolve_openclaw() {
  if command -v openclaw >/dev/null 2>&1; then
    OPENCLAW_BIN="$(command -v openclaw)"
  elif [ -x "$HOME/.npm-global/bin/openclaw" ]; then
    OPENCLAW_BIN="$HOME/.npm-global/bin/openclaw"
  elif [ -x "/usr/local/bin/openclaw" ]; then
    OPENCLAW_BIN="/usr/local/bin/openclaw"
  else
    OPENCLAW_BIN=""
  fi
}

has_openclaw() {
  [ -n "$OPENCLAW_BIN" ]
}

oc() {
  "$OPENCLAW_BIN" "$@"
}

repair_config_if_invalid() {
  local config_readable="false"

  if has_openclaw && oc config get agents.defaults.model.primary >/dev/null 2>&1; then
    config_readable="true"
  elif command -v jq >/dev/null 2>&1 && [ -s "$RUNTIME_CONFIG" ] && jq -e . "$RUNTIME_CONFIG" >/dev/null 2>&1; then
    config_readable="true"
  fi

  if [ "$config_readable" = "true" ]; then
    log "ok: runtime config is readable"
    return
  fi

  log "warn: runtime config invalid/unreadable, attempting restore from workspace template"
  if [ -f "$WORKSPACE_CONFIG" ]; then
    cp "$RUNTIME_CONFIG" "${RUNTIME_CONFIG}.bak-self-heal-$(date +%s)" 2>/dev/null || true
    cp "$WORKSPACE_CONFIG" "$RUNTIME_CONFIG"
    log "fix: restored runtime config from $WORKSPACE_CONFIG"
  else
    log "error: workspace config template missing at $WORKSPACE_CONFIG"
  fi
}

fix_permissions() {
  local paths=(
    "$RUNTIME_CONFIG"
    "$BASE/agents/main/agent/models.json"
    "$BASE/agents/main/agent/auth.json"
    "$BASE/agents/main/agent/auth-profiles.json"
  )
  for p in "${paths[@]}"; do
    if [ -f "$p" ]; then
      chmod 600 "$p" || true
    fi
  done
  log "ok: enforced secure permissions on runtime/auth files"
}

ensure_model_chain() {
  if ! has_openclaw; then
    log "warn: openclaw CLI unavailable, skipping model chain checks"
    return
  fi

  local primary
  primary="$(oc config get agents.defaults.model.primary 2>/dev/null || echo "")"
  if [ -z "$primary" ]; then
    log "warn: missing primary model, setting default groq chain"
    oc config set agents.defaults.model.primary '"groq/llama-3.3-70b-versatile"' >/dev/null
    oc config set agents.defaults.model.fallbacks '["google/gemini-2.5-flash","nvidia/qwen/qwen3-235b-a22b","cerebras/gpt-oss-120b","openrouter/auto"]' >/dev/null
    log "fix: restored default model chain"
  else
    log "ok: model primary=$primary"
  fi
}

align_main_session_model() {
  if ! has_openclaw; then
    return
  fi
  if [ ! -f "$SESSIONS_FILE" ]; then
    return
  fi
  if ! command -v jq >/dev/null 2>&1; then
    return
  fi

  local primary provider model
  primary="$(oc config get agents.defaults.model.primary 2>/dev/null || echo "")"
  if [ -z "$primary" ] || [[ "$primary" != *"/"* ]]; then
    return
  fi
  provider="${primary%%/*}"
  model="${primary#*/}"

  local key
  key="agent:main:telegram:direct:${TELEGRAM_CHAT_ID}"
  if jq -e --arg k "$key" '.[$k] != null' "$SESSIONS_FILE" >/dev/null 2>&1; then
    if [ ! -w "$SESSIONS_FILE" ]; then
      log "warn: session file not writable, skipping telegram session alignment"
      return
    fi

    local tmp
    tmp="$(mktemp)"
    if jq --arg k "$key" --arg p "$provider" --arg m "$model" \
      '(.[$k].modelProvider) = $p | (.[$k].model) = $m |
       (if .[$k].systemPromptReport then
          (.[$k].systemPromptReport.provider) = $p |
          (.[$k].systemPromptReport.model) = $m
        else . end)' \
      "$SESSIONS_FILE" > "$tmp" && cp "$tmp" "$SESSIONS_FILE" 2>/dev/null; then
      log "fix: aligned active telegram session model to $primary"
    else
      log "warn: could not align active telegram session model (non-fatal)"
    fi
    rm -f "$tmp"
  fi
}

ensure_gateway_running() {
  if pgrep -f "openclaw-gateway" >/dev/null 2>&1; then
    log "ok: gateway process running"
    return
  fi

  if ! has_openclaw; then
    log "warn: gateway not running and openclaw CLI unavailable, cannot auto-start"
    return
  fi

  log "warn: gateway not running, attempting start"
  nohup "$OPENCLAW_BIN" gateway >/tmp/openclaw-gateway.log 2>&1 &
  sleep 1
  if pgrep -f "openclaw-gateway" >/dev/null 2>&1; then
    log "fix: gateway started"
  else
    log "error: gateway start failed"
  fi
}

verify_proactive_delivery_hook() {
  local proactive="$WORKSPACE/scripts/proactive-check.sh"
  local morning="$WORKSPACE/scripts/proactive-morning.sh"

  if grep -q "PROACTIVE_PULSE_OWNED=1" "$proactive" && grep -q "PROACTIVE_PULSE_OWNED=1" "$morning"; then
    log "ok: legacy proactive scripts are retired; Proactive Pulse owns outbound delivery"
  elif grep -q "HEARTBEAT_OWNED_PROACTIVE=1" "$proactive" && grep -q "HEARTBEAT_OWNED_PROACTIVE=1" "$morning"; then
    log "warn: legacy proactive scripts still point at heartbeat ownership; migrate to Proactive Pulse"
  elif grep -q "openclaw message send" "$proactive" && grep -q "openclaw message send" "$morning"; then
    log "warn: legacy proactive scripts still own outbound delivery; migrate to Proactive Pulse"
  else
    log "warn: proactive script state is unclear"
  fi
}

main() {
  acquire_lock
  resolve_openclaw

  log "start: self-heal run"
  if has_openclaw; then
    log "ok: using openclaw CLI at $OPENCLAW_BIN"
  else
    log "warn: openclaw CLI not found in PATH; running degraded self-heal mode"
  fi
  repair_config_if_invalid
  fix_permissions
  ensure_model_chain
  align_main_session_model
  ensure_gateway_running
  verify_proactive_delivery_hook
  log "done: self-heal run complete"
}

main "$@"
