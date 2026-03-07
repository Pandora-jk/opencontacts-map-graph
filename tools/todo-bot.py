#!/usr/bin/env python3
"""
Telegram Bot for TODO Management
Listens for /todo commands and updates TODO.md
"""
import os
import sys
import re
import subprocess
from pathlib import Path

TODO_FILE = Path("/home/ubuntu/.openclaw/workspace/TODO.md")

def run_todo_cli(args):
    """Run the todo.py CLI and capture output"""
    cmd = ["python3", "/home/ubuntu/.openclaw/workspace/tools/todo.py"] + args
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.stdout.strip(), result.returncode

def parse_command(text):
    """Parse Telegram message into command parts"""
    if not text.startswith('/todo'):
        return None, None
    
    parts = text.split(' ', 1)
    if len(parts) < 2:
        return "list", ""
    
    rest = parts[1]
    sub_parts = rest.split(' ', 1)
    action = sub_parts[0].lower()
    arg = sub_parts[1] if len(sub_parts) > 1 else ""
    
    return action, arg

def handle_todo_command(action, arg, user_id):
    """Handle TODO commands from Telegram"""
    
    # Security: Only allow Jim (user_id from config)
    JIM_ID = "156480904"
    if str(user_id) != JIM_ID:
        return "🚫 Unauthorized user."

    response = ""

    try:
        if action == "add" or action == "new":
            if not arg:
                response = "❌ Usage: /todo add <task description>"
            else:
                out, _ = run_todo_cli(["add", arg])
                response = f"✅ Added: {arg}"

        elif action == "done" or action == "complete":
            if not arg:
                response = "❌ Usage: /todo done <index>"
            else:
                try:
                    idx = int(arg)
                    out, _ = run_todo_cli(["complete", str(idx)])
                    response = f"✅ Marked #{idx} as done!"
                except ValueError:
                    response = "❌ Index must be a number."

        elif action == "list" or action == "ls" or action == "":
            out, _ = run_todo_cli(["list"])
            # Clean up the output for Telegram
            response = out.replace("📋 TODO List", "**TODO List**")

        elif action == "status":
            out, _ = run_todo_cli(["status"])
            response = out

        elif action == "help":
            response = (
                "📋 **TODO Bot Help**\n\n"
                "/todo add <text> - Add new task\n"
                "/todo done <num> - Complete task #num\n"
                "/todo list - Show all tasks\n"
                "/todo status - Quick stats\n"
                "/todo help - This message"
            )
        else:
            response = f"❓ Unknown command: {action}. Use /todo help"

    except Exception as e:
        response = f"❌ Error: {str(e)}"

    return response

if __name__ == "__main__":
    # Test mode
    if len(sys.argv) > 1:
        action = sys.argv[1]
        arg = " ".join(sys.argv[2:]) if len(sys.argv) > 2 else ""
        print(handle_todo_command(action, arg, "156480904"))
    else:
        print("Usage: python3 todo-bot.py <action> [arg]")
        print("Example: python3 todo-bot.py add 'Buy milk'")
