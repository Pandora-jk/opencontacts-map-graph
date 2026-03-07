#!/bin/bash
# Daily session retention cleanup script.
# Removes deleted session files older than the configured retention window.

set -euo pipefail

DEFAULT_SESSIONS_DIR="$HOME/.openclaw/agents/main/sessions"
SESSIONS_DIR="${SESSIONS_DIR:-$DEFAULT_SESSIONS_DIR}"
RETENTION_HOURS="${RETENTION_HOURS:-24}"
REMOVED_COUNT=0
REMOVED_SIZE=0
CURRENT_TIME=$(date +%s)
ACTIONS_FILE=$(mktemp)
trap 'rm -f "$ACTIONS_FILE"' EXIT

echo "Starting session retention cleanup..." >&2

case "$RETENTION_HOURS" in
    ''|*[!0-9]*)
        echo "RETENTION_HOURS must be a non-negative integer" >&2
        exit 1
        ;;
esac

if [ ! -d "$SESSIONS_DIR" ]; then
    jq -n \
        --arg status "success" \
        --arg message "Sessions directory not found: $SESSIONS_DIR" \
        --argjson cleanup_actions '[]' \
        --argjson removed_count 0 \
        --argjson removed_size 0 \
        '{status: $status, message: $message, cleanup_actions: $cleanup_actions, removed_count: $removed_count, removed_size_bytes: $removed_size}'
    echo "SESSION_RETENTION_OK" >&2
    exit 0
fi

while IFS= read -r -d '' file; do
    file_time=$(stat -c %Y "$file")
    age_hours=$(( (CURRENT_TIME - file_time) / 3600 ))

    if [ "$age_hours" -ge "$RETENTION_HOURS" ]; then
        file_size=$(stat -c %s "$file")
        REMOVED_SIZE=$((REMOVED_SIZE + file_size))

        rm -f -- "$file"
        REMOVED_COUNT=$((REMOVED_COUNT + 1))

        jq -cn \
            --arg file "$(basename "$file")" \
            --argjson age_hours "$age_hours" \
            --argjson size_bytes "$file_size" \
            '{file: $file, age_hours: $age_hours, size_bytes: $size_bytes}' >> "$ACTIONS_FILE"
    fi
done < <(find "$SESSIONS_DIR" -type f -name "*.jsonl.deleted.*" -print0)

if [ -s "$ACTIONS_FILE" ]; then
    ACTIONS_JSON=$(jq -s '.' "$ACTIONS_FILE")
    MESSAGE="Cleaned up $REMOVED_COUNT deleted session file(s)"
else
    ACTIONS_JSON='[]'
    MESSAGE="No deleted session files older than ${RETENTION_HOURS}h to clean up"
fi

jq -n \
    --arg status "success" \
    --arg message "$MESSAGE" \
    --argjson cleanup_actions "$ACTIONS_JSON" \
    --argjson removed_count "$REMOVED_COUNT" \
    --argjson removed_size "$REMOVED_SIZE" \
    '{status: $status, message: $message, cleanup_actions: $cleanup_actions, removed_count: $removed_count, removed_size_bytes: $removed_size}'
echo "SESSION_RETENTION_OK" >&2
