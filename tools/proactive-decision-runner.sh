#!/bin/bash
set -euo pipefail

# Gateway owns delivery; this runner only emits decision text when a new decision exists.
exec python3 /home/ubuntu/.openclaw/workspace/tools/proactive-pulse.py --mode immediate-decision
