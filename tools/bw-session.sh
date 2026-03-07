#!/bin/bash
# bw-session.sh — Get a valid Bitwarden session key.
# Checks cached session first; unlocks fresh if expired or missing.
# Prints the session key to stdout. Cache stored at ~/.openclaw/credentials/.bw_session
#
# Usage:
#   SESSION=$(bash tools/bw-session.sh)
#   bw list items --session "$SESSION"

set -euo pipefail

CREDS="$HOME/.openclaw/credentials/bitwarden.json"
SESSION_FILE="$HOME/.openclaw/credentials/.bw_session"

if [ ! -f "$CREDS" ]; then
    echo "ERROR: No BW credentials at $CREDS" >&2
    exit 1
fi

# Check if cached session is still valid
if [ -f "$SESSION_FILE" ]; then
    CACHED=$(cat "$SESSION_FILE")
    if [ -n "$CACHED" ]; then
        STATUS=$(bw status --session "$CACHED" 2>/dev/null \
            | python3 -c "import json,sys; d=json.load(sys.stdin); print(d.get('status',''))" 2>/dev/null || true)
        if [ "$STATUS" = "unlocked" ]; then
            echo "$CACHED"
            exit 0
        fi
    fi
fi

# Need a fresh unlock — load API key credentials
export BW_CLIENTID=$(python3 -c "import json; d=json.load(open('$CREDS')); print(d['client_id'])")
export BW_CLIENTSECRET=$(python3 -c "import json; d=json.load(open('$CREDS')); print(d['client_secret'])")

# Login via API key (idempotent — safe if already logged in)
bw login --apikey 2>/dev/null || true

# Unlock using passwordfile to avoid shell-escaping issues with special chars
PASS_FILE="/tmp/.bw_pass_$$"
python3 -c "import json; d=json.load(open('$CREDS')); print(d['master_password'], end='')" > "$PASS_FILE"
chmod 600 "$PASS_FILE"
SESSION=$(bw unlock --passwordfile "$PASS_FILE" --raw 2>/dev/null || true)
rm -f "$PASS_FILE"

if [ -z "$SESSION" ]; then
    echo "ERROR: bw unlock failed — check credentials in $CREDS" >&2
    exit 1
fi

# Cache for reuse
echo "$SESSION" > "$SESSION_FILE"
chmod 600 "$SESSION_FILE"
echo "$SESSION"
