#!/bin/bash
# Safe markdown file editor
# Reads file, finds exact text, then edits it
# Usage: ./safe-edit-md.sh <file> <search_pattern> <replacement>

set -e

FILE="$1"
SEARCH="$2"
REPLACE="$3"

if [ ! -f "$FILE" ]; then
    echo "❌ File not found: $FILE"
    exit 1
fi

if [ -z "$SEARCH" ] || [ -z "$REPLACE" ]; then
    echo "Usage: ./safe-edit-md.sh <file> <search_pattern> <replacement>"
    exit 1
fi

# Read file content
CONTENT=$(cat "$FILE")

# Check if search pattern exists
if echo "$CONTENT" | grep -qF "$SEARCH"; then
    # Pattern found - can proceed with edit
    echo "✅ Found pattern in $FILE"
    
    # For simple replacements, use sed
    # Note: This is for ASCII-only patterns
    sed -i "s|$SEARCH|$REPLACE|g" "$FILE"
    echo "✅ Updated $FILE"
else
    echo "❌ Pattern not found in $FILE"
    echo "Searching for: $SEARCH"
    exit 1
fi
