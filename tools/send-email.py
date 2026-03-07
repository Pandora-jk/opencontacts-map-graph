#!/usr/bin/env python3
"""
Pandora Email Sender — sends via Gmail API (Maton) for reliable delivery.
Usage: python3 send-email.py --to <addr> --subject <subject> --body <body> [--html]
Requires: MATON_API_KEY env var
"""

import argparse
import base64
import json
import os
import sys
import urllib.request
import urllib.error
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

GMAIL_SEND_URL = "https://gateway.maton.ai/google-mail/gmail/v1/users/me/messages/send"
FROM_NAME = "Pandora"
FROM_EMAIL = "jim.cooding@gmail.com"


def send(to: str, subject: str, body: str, html: bool = False):
    api_key = os.environ.get("MATON_API_KEY")
    if not api_key:
        print("ERROR: MATON_API_KEY not set", file=sys.stderr)
        sys.exit(1)

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = f"{FROM_NAME} <{FROM_EMAIL}>"
    msg["To"] = to
    msg.attach(MIMEText(body, "html" if html else "plain", "utf-8"))

    raw = base64.urlsafe_b64encode(msg.as_bytes()).decode()
    payload = json.dumps({"raw": raw}).encode()

    req = urllib.request.Request(GMAIL_SEND_URL, data=payload, method="POST")
    req.add_header("Authorization", f"Bearer {api_key}")
    req.add_header("Content-Type", "application/json")

    try:
        resp = json.load(urllib.request.urlopen(req))
        print(f"OK: Email sent to {to} (id: {resp.get('id', '?')})")
    except urllib.error.HTTPError as e:
        err = e.read().decode()
        print(f"ERROR: Gmail API {e.code} — {err}", file=sys.stderr)
        sys.exit(2)
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(3)


def main():
    parser = argparse.ArgumentParser(description="Pandora email sender")
    parser.add_argument("--to", required=True, help="Recipient email address")
    parser.add_argument("--subject", required=True, help="Email subject")
    parser.add_argument("--body", required=True, help="Email body text")
    parser.add_argument("--html", action="store_true", help="Treat body as HTML")
    args = parser.parse_args()
    send(args.to, args.subject, args.body, args.html)


if __name__ == "__main__":
    main()
