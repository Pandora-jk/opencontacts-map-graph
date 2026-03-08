#!/usr/bin/env python3
"""
Cold Email Campaign - Batch 1
Generates outreach drafts for the first 20 founder-led B2B agency targets.
"""

import csv
import json
from pathlib import Path
from datetime import datetime, timezone

# Output file for tracking
BATCH_FILE = Path(__file__).parent / "batch-1-sent.json"
TARGETS_FILE = Path(__file__).parent.parent / "targets" / "founder-led-b2b-agencies-first-20.csv"

def generate_email_template(
    company_name: str,
    contact_name: str,
    title: str = "",
    segment: str = "agency",
    opening_line: str = "",
) -> dict:
    """Generate a founder-led agency outbound draft."""

    subject = f"quick idea for {company_name}'s outbound pipeline"
    opener = opening_line or (
        f"Noticed {company_name} is growing in {segment}. "
        "At that stage, outbound list building usually ends up back on the founder's plate."
    )

    body = f"""Hi {contact_name},

{opener}

I help founder-led B2B agencies build qualified outbound pipelines so they can spend more time closing and less time prospecting.

The usual gap for agencies in the 5-30 person range is not service quality. It is consistent list building, qualification, and outreach-ready handoff.

Our Starter offer is $300 one-time and includes:
- 100 qualified prospects
- enrichment
- outreach-ready handoff
- 3 personalized opening-line examples

If useful, I can send a small sample built around {company_name}'s current offer.

Best,
{{sender_name}}

{{business_name}}
{{business_address}}
Unsubscribe: {{unsubscribe_url}}
"""

    return {
        "subject": subject,
        "body": body,
        "tone": "direct_service_offer",
        "cta": "Reply for a sample"
    }

def load_targets():
    """Load targets from CSV."""
    targets = []
    with open(TARGETS_FILE, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            targets.append(row)
    return targets

def send_batch(targets: list, limit: int = 100):
    """
    Send batch of cold emails.
    In production, this would use an email service API.
    For now, it generates the emails and logs them.
    """
    sent = []
    
    for i, target in enumerate(targets[:limit]):
        company = target.get('company_name', '')
        contact = target.get('founder_name', '') or target.get('contact_name', 'there')
        email = target.get('work_email', '') or target.get('email', '')
        title = target.get('title', '')
        segment = target.get('segment', 'agency')
        opening_line = target.get('opening_line_1', '')
        status = target.get('status', '')

        # Skip if no verified contact method or the row is not ready.
        if not email or status in {'to_research', 'skip'}:
            continue

        # Generate personalized email
        email_data = generate_email_template(company, contact, title, segment, opening_line)

        # Create record
        record = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "company": company,
            "contact": contact,
            "title": title,
            "email": email,
            "subject": email_data['subject'],
            "body": email_data['body'],
            "status": "ready_to_send",
            "batch": 1
        }
        
        sent.append(record)
        
        # In production, would call email API here:
        # send_email_api(to=email, subject=..., body=...)
    
    # Save batch record
    BATCH_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(BATCH_FILE, 'w', encoding='utf-8') as f:
        json.dump({
            "batch_id": 1,
            "sent_at": datetime.now(timezone.utc).isoformat(),
            "total_sent": len(sent),
            "targets": sent
        }, f, indent=2)
    
    return sent

if __name__ == '__main__':
    print("Loading targets...")
    targets = load_targets()
    print(f"Loaded {len(targets)} targets")

    print("\nGenerating batch 1 drafts...")
    sent = send_batch(targets, limit=20)

    print(f"\n✅ Batch 1 complete:")
    print(f"   Drafted: {len(sent)} emails")
    print(f"   Batch file: {BATCH_FILE}")
    print(f"\nNext steps:")
    print(f"   - Verify footer placeholders with real business details")
    print(f"   - Run final compliance review")
    print(f"   - Send to verified contacts only")
