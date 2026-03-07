# Coding Department - Memory Log

## Current State
- **Active Projects:** 
  - Income Engine Scripts (PDF-to-CSV, Outreach Generator)
  - GitHub Repo Management (`automation-scripts`, `data-brokerage`)
- **Open Bounties:** 0 (Searching...)
- **Security Status:** Green (Last audit: 2026-03-01)
- **Pending Deploys:** None

## Recent Activity
- **2026-03-01:** 
  - Fixed `fix-edit-issues.py` syntax error (Python 2 → 3).
  - Replaced hardcoded paths with env vars.
  - Deployed assets to GitHub repos via PAT.
- **2026-02-28:** 
  - Diagnosed GitHub PAT sync issue.
  - Created initial repo structure.

## Known Issues
- GitHub PAT must be refreshed manually if expired.
- Some scripts lack `try/except` blocks (queued for refactor).

## Tech Stack
- Python 3.8+, Bash, Git, NVIDIA NIM (LLM), Bitwarden (Secrets)
