#!/bin/bash
# bw-get.sh — Retrieve a credential from Bitwarden (auto-unlocks if needed).
#
# Usage:
#   bash tools/bw-get.sh <item-name> [field]
#
# Fields:  password (default), username, totp
#          or any custom field name (case-insensitive)
#
# Examples:
#   bash tools/bw-get.sh "Outlook SMTP" password
#   bash tools/bw-get.sh "Outlook SMTP" username
#   bash tools/bw-get.sh --list

set -euo pipefail

TOOLS_DIR="$(cd "$(dirname "$0")" && pwd)"

if [ "${1:-}" = "--list" ]; then
    SESSION=$(bash "$TOOLS_DIR/bw-session.sh")
    bw list items --session "$SESSION" \
        | python3 -c "import json,sys; [print(i['name']) for i in json.load(sys.stdin)]"
    exit 0
fi

ITEM="${1:-}"
FIELD="${2:-password}"

if [ -z "$ITEM" ]; then
    echo "Usage: bw-get.sh <item-name> [field]" >&2
    echo "       bw-get.sh --list" >&2
    exit 1
fi

SESSION=$(bash "$TOOLS_DIR/bw-session.sh")

# Standard BW object types supported by 'bw get'
BW_NATIVE="password username totp notes uri exposed attachment"

if echo "$BW_NATIVE" | grep -qw "$FIELD"; then
    bw get "$FIELD" "$ITEM" --session "$SESSION"
else
    # Custom field — fetch via item JSON
    bw get item "$ITEM" --session "$SESSION" \
        | python3 -c "
import json, sys
d = json.load(sys.stdin)
field = '${FIELD}'.lower()
for f in d.get('fields', []):
    if f.get('name', '').lower() == field:
        print(f.get('value', ''))
        exit(0)
print('Field not found: ${FIELD}', file=sys.stderr)
exit(1)
"
fi
