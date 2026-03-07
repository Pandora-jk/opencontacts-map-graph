#!/usr/bin/env python3
"""
Send TODO items to Jim's Telegram
Usage: python3 tools/send-todo-telegram.py [--force]
"""
import subprocess
import sys
from pathlib import Path
from datetime import datetime

WORKSPACE = Path("/home/ubuntu/.openclaw/workspace")
TODO_FILE = WORKSPACE / "TODO.md"
JIM_TELEGRAM_ID = "156480904"

def read_todo():
    """Read the current TODO.md file"""
    if not TODO_FILE.exists():
        return None
    
    with open(TODO_FILE, 'r') as f:
        return f.read()

def format_for_telegram(content):
    """Format TODO content for Telegram markdown"""
    lines = []
    lines.append("📋 *TODO Items - Auto-Synced*\n")
    lines.append(f"_Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S AEDT')}_\n")
    lines.append("")
    
    in_section = False
    for line in content.split('\n'):
        if line.startswith('# '):
            # Skip main title
            continue
        elif line.startswith('## '):
            # Section header
            section = line.replace('## ', '').strip()
            lines.append(f"\n✅ *{section}*")
            in_section = True
        elif line.startswith('- [ ]'):
            # Unchecked item
            item = line.replace('- [ ]', '❌').strip()
            lines.append(f"  {item}")
        elif line.startswith('- [x]'):
            # Checked item
            item = line.replace('- [x]', '✅').strip()
            lines.append(f"  {item}")
        elif line.startswith('---') or line.startswith('*Generated'):
            # Skip footer
            continue
        elif line.strip():
            # Other content
            if in_section:
                lines.append(f"  {line}")
            else:
                lines.append(line)
    
    lines.append("\n_🔮 Auto-synced by Pandora's self-improvement system_")
    return '\n'.join(lines)

def send_to_telegram(message):
    """Send message to Jim's Telegram using OpenClaw message tool"""
    import json
    import os
    
    # Create a temporary file with the message
    temp_file = Path("/tmp/todo_telegram_msg.txt")
    with open(temp_file, 'w') as f:
        f.write(message)
    
    # Use the message tool via subprocess
    # Note: This assumes we can call the message tool
    # In OpenClaw, we'd use the message tool directly
    cmd = f'''
    # This would be called via OpenClaw's message tool
    # For now, output the message to be sent
    echo "Message ready to send to Telegram ID {JIM_TELEGRAM_ID}:"
    cat {temp_file}
    '''
    
    return temp_file

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description='Send TODO items to Telegram')
    parser.add_argument('--force', action='store_true', help='Force send even if recently sent')
    args = parser.parse_args()
    
    # Read TODO
    todo_content = read_todo()
    if not todo_content:
        print("❌ No TODO.md found or file is empty")
        sys.exit(1)
    
    # Format for Telegram
    formatted = format_for_telegram(todo_content)
    
    # Output the message (to be sent via OpenClaw message tool)
    print("✅ TODO formatted for Telegram:")
    print("-" * 80)
    print(formatted)
    print("-" * 80)
    print(f"\nTo send this to Jim's Telegram (ID: {JIM_TELEGRAM_ID}), use the message tool with this content.")
    
    # Save formatted version
    output_file = TODO_FILE.with_suffix('.telegram.txt')
    with open(output_file, 'w') as f:
        f.write(formatted)
    
    print(f"\n💾 Saved formatted version to: {output_file}")
