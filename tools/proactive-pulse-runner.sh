#!/bin/bash
set -euo pipefail

# Cron delivery is handled by Gateway delivery.mode, not by this runner.
exec python3 /home/ubuntu/.openclaw/workspace/tools/proactive-pulse.py
