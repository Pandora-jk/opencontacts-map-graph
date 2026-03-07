#!/bin/bash
# Sync TODO items to Telegram (Jim's phone)
# Sends the current TODO.md content as a formatted message

WORKSPACE="/home/ubuntu/.openclaw/workspace"
TODO_FILE="$WORKSPACE/TODO.md"
JIM_TELEGRAM_ID="156480904"

# Check if TODO file exists
if [ ! -f "$TODO_FILE" ]; then
    echo "No TODO.md found - nothing to sync"
    exit 0
fi

# Read TODO content
TODO_CONTENT=$(cat "$TODO_FILE")

# Format for Telegram (markdown)
MESSAGE="📋 *TODO Items - Synced from Workspace*\n\n"
MESSAGE+="*Generated:* $(TZ="Australia/Sydney" date '+%Y-%m-%d %H:%M:%S AEDT')\n\n"
MESSAGE+="$(echo "$TODO_CONTENT" | sed 's/^# //g' | sed 's/^## /✅ */g' | sed 's/^- \[ \]/❌ /g' | sed 's/^- \[x\]/✅ /g')\n\n"
MESSAGE+="_Auto-synced by Pandora's self-improvement system_"

# Send via OpenClaw message tool
# Note: This requires the message tool to be available in scripts
# For now, we'll output the formatted message
echo "Formatted TODO for Telegram:"
echo "$MESSAGE"

# Alternative: Save as a file that can be sent
echo "$MESSAGE" > "${TODO_FILE%.md}.telegram.txt"
echo "Saved formatted version to: ${TODO_FILE%.md}.telegram.txt"
