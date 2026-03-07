#!/usr/bin/env python3
"""
Nightly session reset for OpenClaw.
Sets systemSent=False on active Telegram/main sessions so the next message
regenerates the system prompt — picking up any changes to SOUL.md, MEMORY.md, etc.

Run nightly via cron (e.g. 3am UTC). Does NOT clear conversation history.
Only forces the system prompt to be re-injected on the next turn.
"""

import json
import sys
from pathlib import Path
from datetime import datetime, timezone

SESSIONS_PATH = Path.home() / ".openclaw/agents/main/sessions/sessions.json"
LOG_TAG = "[nightly-reset]"


def main():
    if not SESSIONS_PATH.exists():
        print(f"{LOG_TAG} sessions.json not found — skipping", file=sys.stderr)
        return

    data = json.loads(SESSIONS_PATH.read_text())
    now_ms = int(datetime.now(timezone.utc).timestamp() * 1000)
    reset_count = 0

    for key, entry in data.items():
        if not isinstance(entry, dict):
            continue
        # Only reset sessions that have been active (have a model set)
        if not entry.get("model") and not entry.get("modelProvider"):
            continue
        # Force system prompt re-injection on next turn
        entry["systemSent"] = False
        reset_count += 1
        print(f"{LOG_TAG} scheduled reset: {key}", file=sys.stderr)

    if reset_count == 0:
        print(f"{LOG_TAG} no active sessions found", file=sys.stderr)
        return

    SESSIONS_PATH.write_text(json.dumps(data, indent=2))
    print(f"{LOG_TAG} {reset_count} session(s) will refresh system prompt on next message", file=sys.stderr)


if __name__ == "__main__":
    main()
