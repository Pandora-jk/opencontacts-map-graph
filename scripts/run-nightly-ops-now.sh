#!/bin/bash
# run-nightly-ops-now.sh
# Manually trigger the nightly ops run for testing

echo "🌙 Manually triggering nightly ops run..."
/home/ubuntu/.openclaw/workspace/scripts/nightly-ops.sh

echo ""
echo "✅ Test complete. Check /home/ubuntu/.openclaw/workspace/logs/ for the health report."
