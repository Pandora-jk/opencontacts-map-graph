#!/usr/bin/env python3
"""
Unsubscribe Handler
Processes opt-out requests and maintains suppression list.
Compliant with CAN-SPAM, GDPR, and Australian Spam Act.
"""

import json
import hashlib
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, Dict, List

SUPPRESSION_FILE = Path(__file__).parent / "suppression_list.json"
LOG_FILE = Path(__file__).parent.parent.parent.parent / "logs" / "unsubscribe_log.jsonl"

class SuppressionList:
    """Manages the global suppression list for opt-outs."""
    
    def __init__(self):
        self.entries: Dict[str, dict] = {}
        self.load()
    
    def load(self) -> None:
        """Load suppression list from file."""
        if SUPPRESSION_FILE.exists():
            try:
                data = json.loads(SUPPRESSION_FILE.read_text(encoding='utf-8'))
                self.entries = data.get('entries', {})
            except (json.JSONDecodeError, FileNotFoundError):
                self.entries = {}
    
    def save(self) -> None:
        """Save suppression list to file."""
        SUPPRESSION_FILE.parent.mkdir(parents=True, exist_ok=True)
        data = {'entries': self.entries, 'updated_at': datetime.now(timezone.utc).isoformat()}
        SUPPRESSION_FILE.write_text(json.dumps(data, indent=2), encoding='utf-8')
    
    def add(self, email: str, reason: str = "user_request", source: str = "unsubscribe_handler") -> bool:
        """
        Add email to suppression list.
        
        Args:
            email: Email address to suppress
            reason: Reason for suppression (user_request, bounce, complaint, etc.)
            source: Source of the request (unsubscribe_link, api, manual, etc.)
        
        Returns:
            True if added, False if already exists
        """
        email_lower = email.lower().strip()
        
        if email_lower in self.entries:
            # Update existing entry
            self.entries[email_lower]['reason'] = reason
            self.entries[email_lower]['source'] = source
            self.entries[email_lower]['updated_at'] = datetime.now(timezone.utc).isoformat()
            self.save()
            self._log_action(email_lower, "updated", reason, source)
            return False
        
        self.entries[email_lower] = {
            'email': email_lower,
            'reason': reason,
            'source': source,
            'created_at': datetime.now(timezone.utc).isoformat(),
            'updated_at': datetime.now(timezone.utc).isoformat()
        }
        self.save()
        self._log_action(email_lower, "added", reason, source)
        return True
    
    def remove(self, email: str) -> bool:
        """
        Remove email from suppression list (if user re-subscribes).
        
        Returns:
            True if removed, False if not found
        """
        email_lower = email.lower().strip()
        if email_lower in self.entries:
            del self.entries[email_lower]
            self.save()
            self._log_action(email_lower, "removed", "re-subscribed", "manual")
            return True
        return False
    
    def is_suppressed(self, email: str) -> bool:
        """Check if email is on suppression list."""
        return email.lower().strip() in self.entries
    
    def _log_action(self, email: str, action: str, reason: str, source: str) -> None:
        """Log action to JSONL file."""
        LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
        log_entry = {
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'action': action,
            'email_hash': hashlib.sha256(email.encode()).hexdigest()[:16],  # Pseudonymize
            'reason': reason,
            'source': source
        }
        with LOG_FILE.open('a', encoding='utf-8') as f:
            f.write(json.dumps(log_entry) + '\n')


def process_unsubscribe_request(email: str, reason: Optional[str] = None) -> Dict:
    """
    Process an unsubscribe request.
    
    Args:
        email: Email address requesting unsubscribe
        reason: Optional reason provided by user
    
    Returns:
        Dict with status and message
    """
    suppression = SuppressionList()
    
    if suppression.is_suppressed(email):
        return {
            'status': 'already_suppressed',
            'message': 'You are already unsubscribed.',
            'email': email
        }
    
    suppression.add(email, reason=reason or "user_request", source="unsubscribe_link")
    
    return {
        'status': 'success',
        'message': 'You have been unsubscribed successfully.',
        'email': email,
        'effective_immediately': True
    }


def generate_unsubscribe_page(email: str, reason: Optional[str] = None) -> str:
    """
    Generate HTML for unsubscribe confirmation page.
    
    Returns:
        HTML string
    """
    result = process_unsubscribe_request(email, reason)
    
    if result['status'] == 'success':
        html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Unsubscribed - Pandora Lead Qual</title>
    <meta charset="UTF-8">
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; max-width: 600px; margin: 40px auto; padding: 20px; }}
        .success {{ color: #27ae60; }}
        .info {{ background: #f8f9fa; padding: 15px; border-radius: 5px; margin-top: 20px; }}
        a {{ color: #3498db; }}
    </style>
</head>
<body>
    <h1 class="success">✓ You've been unsubscribed</h1>
    <p><strong>{email}</strong> has been removed from our mailing list.</p>
    
    <div class="info">
        <h3>What happens next?</h3>
        <ul>
            <li>You will no longer receive emails from us</li>
            <li>This change is effective immediately</li>
            <li>Your data will be deleted within 30 days</li>
        </ul>
    </div>
    
    <p style="margin-top: 30px;">
        <small>
            Accidentally unsubscribed? <a href="mailto:hello@pandora-leadqual.com?subject=Resubscribe&body=Please resubscribe {email}">Contact us</a> to resubscribe.
        </small>
    </p>
    
    <p style="margin-top: 20px;">
        <small>
            Pandora Lead Qual<br>
            123 Business St, Sydney NSW 2000, Australia<br>
            <a href="https://pandora-leadqual.com/privacy">Privacy Policy</a>
        </small>
    </p>
</body>
</html>
"""
    else:
        html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Already Unsubscribed - Pandora Lead Qual</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; max-width: 600px; margin: 40px auto; padding: 20px; }}
        .info {{ color: #7f8c8d; }}
    </style>
</head>
<body>
    <h1 class="info">ℹ Already unsubscribed</h1>
    <p>This email address is already on our suppression list.</p>
    <p><strong>{email}</strong> will not receive future emails from us.</p>
</body>
</html>
"""
    
    return html


# CLI interface
if __name__ == '__main__':
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python unsubscribe-handler.py <email> [reason]")
        print("Example: python unsubscribe-handler.py user@example.com 'not_interested'")
        sys.exit(1)
    
    email = sys.argv[1]
    reason = sys.argv[2] if len(sys.argv) > 2 else None
    
    result = process_unsubscribe_request(email, reason)
    print(json.dumps(result, indent=2))
