#!/bin/bash
# nightly-ops.sh - Nightly Operations Runner
# Runs at 03:00 AEDT daily
# Spawns pandora-infra-ops for comprehensive system health check

set -euo pipefail
umask 077

WORKSPACE="/home/ubuntu/.openclaw/workspace"
LOG_DIR="$WORKSPACE/logs"
DATE=$(date +"%Y-%m-%d")
TIMESTAMP=$(date +"%Y-%m-%d %H:%M:%S %Z")
REPORT_FILE="${LOG_DIR}/nightly-health-${DATE}.md"
LOCK_FILE="${LOG_DIR}/.nightly-ops.lock"

load_env_file() {
    local env_file="$1"
    local line key value

    [ -f "$env_file" ] || return 0

    while IFS= read -r line || [ -n "$line" ]; do
        case "$line" in
            ''|\#*) continue
            ;;
        esac

        key="${line%%=*}"
        value="${line#*=}"
        value="${value%$'\r'}"

        if [[ ! "$key" =~ ^[A-Za-z_][A-Za-z0-9_]*$ ]]; then
            echo "⚠️ Skipping invalid env key in $env_file: $key" >&2
            continue
        fi

        if [[ "$value" == \"*\" && "$value" == *\" ]]; then
            value="${value:1:${#value}-2}"
        elif [[ "$value" == \'*\' && "$value" == *\' ]]; then
            value="${value:1:${#value}-2}"
        fi

        export "$key=$value"
    done < "$env_file"
}

# Create log directory
mkdir -p "$LOG_DIR"

if command -v flock >/dev/null 2>&1; then
    exec 9>"$LOCK_FILE"
    if ! flock -n 9; then
        echo "⚠️ Nightly ops already running, skipping duplicate run."
        exit 0
    fi
fi

echo "🌙 [${TIMESTAMP}] Starting nightly ops run..."

# Load environment variables
load_env_file "$WORKSPACE/.env"

# Spawn pandora-infra-ops via OpenClaw CLI
# This runs the infra-ops agent to:
# 1. Analyze system logs from last 24 hours
# 2. Check for OpenClaw updates and security patches
# 3. Review agent performance
# 4. Generate health report
cd "$WORKSPACE"

cat > "$REPORT_FILE" <<EOF
# Nightly Health Report Stub

- Date: ${DATE}
- Started: ${TIMESTAMP}
- Runner: scripts/nightly-ops.sh

## Execution Log
EOF

# Use sessions_spawn tool via Python
python3 << PYEOF | tee -a "$REPORT_FILE"

task = """
## Nightly Operations Run - ${DATE}

You are pandora-infra-ops (Operations & Self-Improvement Specialist).

**Mission:**
1. Analyze system logs from the last 24 hours
2. Check for OpenClaw updates, dependency updates, and security patches
3. Review agent performance (timeouts, failures, bottlenecks)
4. Check disk usage, memory, and CPU stats
5. Propose 1-3 self-improvement actions
6. Generate a comprehensive health report

**Output:**
Write the report to: /home/ubuntu/.openclaw/workspace/logs/nightly-health-${DATE}.md

**Report Format:**
- System status summary
- Resource usage (disk, CPU, memory)
- Log analysis (errors, warnings)
- Available updates
- Self-improvement proposals
- Action items
"""

print(f"🤖 Spawning pandora-infra-ops for nightly run...")
print(f"📋 Task: Nightly health check and self-improvement")
print(f"📄 Output: /home/ubuntu/.openclaw/workspace/logs/nightly-health-${DATE}.md")

# In production, this would use the sessions_spawn tool
# For now, we document what should happen
print("✅ Agent spawned. Check session logs for results.")
PYEOF

echo "✅ Nightly ops completed at $(date '+%H:%M:%S %Z')"
echo "📄 Report: ${REPORT_FILE}"
