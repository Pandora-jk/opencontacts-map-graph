#!/usr/bin/env python3
"""Send a message to Telegram using OpenClaw's message tool infrastructure."""
import argparse
import subprocess
import sys

def send_telegram(to: str, text: str) -> bool:
    """Send message via OpenClaw message tool."""
    try:
        # Call the message tool via gateway
        cmd = [
            'openclaw', 'message', 'send',
            '--target', to,
            '--message', text
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        return result.returncode == 0
    except Exception as e:
        print(f"Failed to send message: {e}", file=sys.stderr)
        return False

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Send Telegram message')
    parser.add_argument('--to', required=True, help='Telegram user ID')
    parser.add_argument('--text', required=True, help='Message text')
    args = parser.parse_args()
    
    if send_telegram(args.to, args.text):
        print("Message sent successfully")
        sys.exit(0)
    else:
        print("Failed to send message", file=sys.stderr)
        sys.exit(1)
