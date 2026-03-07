#!/bin/bash
# Check current session context usage
# Returns: context_percentage (e.g., "45")

# Get session status
STATUS=$(session_status 2>&1)

# Extract context percentage from usage footer
# Format: Usage: Xk in / Yk out · ctx Z%
if echo "$STATUS" | grep -q "ctx"; then
    CTX=$(echo "$STATUS" | grep -oP 'ctx \K[0-9]+')
    echo "$CTX"
else
    echo "0"
fi
