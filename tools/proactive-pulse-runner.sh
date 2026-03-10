#!/bin/bash
# Proactive Pulse Runner - only delivers if there's something to report
OUTPUT=$(python3 /home/ubuntu/.openclaw/workspace/tools/proactive-pulse.py)
echo "$OUTPUT"
# Only send to Telegram if output is not NO_REPLY
if [[ "$OUTPUT" != "NO_REPLY" && -n "$OUTPUT" ]]; then
    # Use OpenClaw message tool to send
    python3 /home/ubuntu/.openclaw/workspace/tools/send-telegram-message.py --to "156480904" --text "$OUTPUT"
fi
