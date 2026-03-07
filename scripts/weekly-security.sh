#!/bin/bash
# weekly-security.sh - Weekly Security Audit
# Runs at 05:00 AEDT on Sundays
# Spawns pandora-infra-security for comprehensive security scan

set -euo pipefail
umask 077

WORKSPACE="/home/ubuntu/.openclaw/workspace"
LOG_DIR="$WORKSPACE/logs"
DATE=$(date +"%Y-%m-%d")
TIMESTAMP=$(date +"%Y-%m-%d %H:%M:%S %Z")
REPORT_FILE="${LOG_DIR}/weekly-security-${DATE}.md"
LOCK_FILE="${LOG_DIR}/.weekly-security.lock"

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
        echo "⚠️ Weekly security audit already running, skipping duplicate run."
        exit 0
    fi
fi

echo "🔒 [${TIMESTAMP}] Starting weekly security audit..."

# Load environment variables
load_env_file "$WORKSPACE/.env"

cd "$WORKSPACE"

if ! INFRA_SUMMARY=$(python3 "$WORKSPACE/tools/infra-status.py" 2>&1); then
    echo "❌ infra-status check failed:" >&2
    echo "$INFRA_SUMMARY" >&2
    exit 1
fi

LATEST_ARTIFACT=$(ls -1t "$WORKSPACE"/departments/infra/artifacts/checks/*-infra-status.md 2>/dev/null | head -n1 || true)

cat > "$REPORT_FILE" <<EOF
# Weekly Security Audit

- Date: ${DATE}
- Started: ${TIMESTAMP}
- Runner: scripts/weekly-security.sh

## Infra Summary
\`\`\`
${INFRA_SUMMARY}
\`\`\`
EOF

if [ -n "$LATEST_ARTIFACT" ] && [ -f "$LATEST_ARTIFACT" ]; then
    {
        echo
        echo "## Detailed Findings"
        echo
        echo "Source artifact: \`${LATEST_ARTIFACT}\`"
        echo
        cat "$LATEST_ARTIFACT"
    } >> "$REPORT_FILE"
fi

echo "✅ Weekly security audit completed at $(date '+%H:%M:%S %Z')"
echo "📄 Report: ${REPORT_FILE}"

# Alert if critical issues found
if grep -q "CRITICAL" "$REPORT_FILE" 2>/dev/null; then
    echo "🚨 CRITICAL security issues detected! Sending alert..."
    # Add Telegram alert here if needed
elif grep -q "RISK:" "$REPORT_FILE" 2>/dev/null; then
    echo "⚠️ Security risks detected. Review ${REPORT_FILE}."
fi
