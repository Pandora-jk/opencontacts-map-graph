#!/usr/bin/env python3
"""
Polls for new TODO commands from Telegram history.
Stores last processed message ID to avoid duplicates.
"""
import os
import json
import subprocess
from pathlib import Path

STATE_FILE = Path("/home/ubuntu/.openclaw/workspace/.todo_state.json")
LOG_FILE = Path("/home/ubuntu/.openclaw/workspace/logs/todo-poll.log")

def get_last_msg_id():
    if STATE_FILE.exists():
        with open(STATE_FILE) as f:
            return json.load(f).get("last_msg_id", 0)
    return 0

def set_last_msg_id(msg_id):
    with open(STATE_FILE, 'w') as f:
        json.dump({"last_msg_id": msg_id}, f)

def get_recent_messages(limit=5):
    """Fetch recent messages from Telegram history (simulated for now)"""
    # In a real implementation, this would call Telegram API or read a queue
    # For now, we rely on the message tool's ability to trigger scripts
    return []

def process_command(text, user_id):
    """Process a command string"""
    if not text.startswith('/todo'):
        return None
    
    from todo_bot import handle_todo_command
    parts = text.split(' ', 1)
    action = parts[1] if len(parts) > 1 else "list"
    arg = parts[2] if len(parts) > 2 else ""
    
    # Special handling for 'add' which needs full sentence
    if action == "add" and len(parts) > 1:
        # Re-extract full argument
        match = re.search(r'/todo\s+add\s+(.+)', text)
        if match:
            arg = match.group(1)
        else:
            arg = parts[2] if len(parts) > 2 else ""
    
    return handle_todo_command(action, arg, str(user_id))

if __name__ == "__main__":
    print("TODO Poller running... (Waiting for triggers)")
    # This script is a placeholder. 
    # Real implementation requires Telegram Bot API or a webhook.
    # For now, we use the direct CLI method via the bot script.
