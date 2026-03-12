#!/usr/bin/env python3
"""
Code Review Assignment Tool
Automatically assigns independent reviewers to PRs and tracks review status.
"""

import json
import sys
import os
from datetime import datetime

REVIEWERS = [
    "senior-dev-1",
    "security-auditor", 
    "android-specialist",
    "backend-lead"
]

def assign_reviewer(pr_number, author, repo="android-ecosystem"):
    """Assign an independent reviewer to a PR."""
    
    # Don't assign author as their own reviewer
    available_reviewers = [r for r in REVIEWERS if r != author]
    
    if not available_reviewers:
        reviewer = REVIEWERS[0]  # Fallback if only one person
    else:
        # Simple round-robin from available reviewers
        reviewer = available_reviewers[len(available_reviewers) % len(available_reviewers)]
    
    print(f"PR #{pr_number} ({repo})")
    print(f"  Author: {author}")
    print(f"  Assigned Reviewer: {reviewer}")
    print(f"  Status: Pending Review")
    print(f"  Deadline: 24 hours from now")
    
    return reviewer

def review_status(pr_number):
    """Check review status for a PR."""
    print(f"PR #{pr_number} Review Status:")
    print("  - Code submitted: ✅")
    print("  - Tests passing: ⏳")
    print("  - Reviewer assigned: ⏳")
    print("  - Security scan: ⏳")
    print("  - Approved: ❌")

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 assign-reviewer.py <pr_number> [author]")
        print("       python3 assign-reviewer.py status <pr_number>")
        sys.exit(1)
    
    if sys.argv[1] == "status":
        if len(sys.argv) < 3:
            print("Error: PR number required")
            sys.exit(1)
        review_status(sys.argv[2])
    else:
        pr_num = sys.argv[1]
        author = sys.argv[2] if len(sys.argv) > 2 else "developer"
        assign_reviewer(pr_num, author)

if __name__ == "__main__":
    main()
