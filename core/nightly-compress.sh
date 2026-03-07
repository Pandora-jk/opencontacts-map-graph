#!/bin/bash
# nightly-compress.sh
# Runs at 03:00 AEDT to summarize all departments and update global state

WORKSPACE="/home/ubuntu/.openclaw/workspace"
DATE=$(date +"%Y-%m-%d")
TIME=$(date +"%H:%M %Z")

echo "🌙 Starting Nightly Compression at $TIME"

# Initialize summary
SUMMARY="# Nightly Summary - $DATE\n\n"

# Process each department
for DEPT in finance coding travel infra; do
    DEPT_PATH="$WORKSPACE/departments/$DEPT"
    MEMORY_FILE="$DEPT_PATH/MEMORY.md"
    TODO_FILE="$DEPT_PATH/TODO.md"
    
    if [ -f "$MEMORY_FILE" ]; then
        echo "📊 Processing $DEPT department..."
        
        # Extract key metrics (simplified for demo)
        # In production, this would parse the actual content
        SUMMARY+="## ${DEPT^} Department\n"
        SUMMARY+="- Status: Processed\n"
        SUMMARY+="- Last Activity: $DATE\n\n"
    fi
done

# Update global status
echo -e "$SUMMARY" > "$WORKSPACE/memory/nightly-summary-$DATE.md"

# Update ORG-STATUS.md with timestamp
sed -i "s/Last Updated:.*/Last Updated: $DATE $TIME/" "$WORKSPACE/ORG-STATUS.md"

echo "✅ Nightly compression complete. Summary saved to memory/nightly-summary-$DATE.md"
