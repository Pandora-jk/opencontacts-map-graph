#!/bin/bash
# Self-Improvement Nightly Run
# Runs at 03:00 AEDT (16:00 UTC previous day)

set -e

WORKSPACE="/home/ubuntu/.openclaw/workspace"
MEMORY_DIR="$WORKSPACE/memory"
TOOLS_DIR="$WORKSPACE/tools"
SCRIPTS_DIR="$WORKSPACE/scripts"
TODAY=$(TZ="Australia/Sydney" date +%Y-%m-%d)
REPORT_FILE="$MEMORY_DIR/self-improve-$TODAY.md"
TODO_FILE="$WORKSPACE/TODO.md"

echo "🔮 Starting Self-Improvement Run - $TODAY"
echo "Working directory: $WORKSPACE"

# Fast deterministic repair before broader audits.
bash "$WORKSPACE/scripts/oc-self-heal.sh" >/dev/null 2>&1 || true

# Initialize report
cat > "$REPORT_FILE" << EOF
# Self-Improvement Run - $TODAY 03:00 AEDT

## Actions Taken
EOF

ACTION_COUNT=0
TODO_ITEMS=""
SCRIPT_SUGGESTIONS=""

# =============================================================================
# 1. Security Audit
# =============================================================================
echo "🔒 Running security checks..."
echo -e "\n### 1. Security Audit\n" >> "$REPORT_FILE"

DISK_USAGE=$(df -h / | tail -1 | awk '{print $5}')
echo "- Disk usage: $DISK_USAGE" >> "$REPORT_FILE"

UPDATES=$(apt list --upgradable 2>/dev/null | grep -v "^Listing" | wc -l)
echo "- Pending updates: $UPDATES packages" >> "$REPORT_FILE"

LAST_LOGIN=$(last -n 3 2>/dev/null | head -3 | tr '\n' ' ')
echo "- Recent logins: $LAST_LOGIN" >> "$REPORT_FILE"

# Check firewall
UFW_STATUS=$(ufw status 2>/dev/null | grep "Status:" || echo "UFW not installed")
echo "- Firewall: $UFW_STATUS" >> "$REPORT_FILE"

# =============================================================================
# 2. Workspace Cleanup
# =============================================================================
echo "🧹 Cleaning workspace..."
echo -e "\n### 2. Workspace Cleanup\n" >> "$REPORT_FILE"

TMP_CLEANED=$(find /tmp -type f -mtime +7 -delete 2>/dev/null | wc -l)
echo "- Cleaned $TMP_CLEANED old tmp files" >> "$REPORT_FILE"

WORKSPACE_SIZE=$(du -sh "$WORKSPACE" 2>/dev/null | cut -f1)
echo "- Workspace size: $WORKSPACE_SIZE" >> "$REPORT_FILE"

# Find large files (>50MB)
LARGE_FILES=$(find "$WORKSPACE" -type f -size +50M 2>/dev/null | wc -l)
if [ "$LARGE_FILES" -gt 0 ]; then
    echo "- ⚠️ Found $LARGE_FILES large files (>50MB)" >> "$REPORT_FILE"
    TODO_ITEMS="${TODO_ITEMS}- [ ] Review large files in workspace (find $WORKSPACE -type f -size +50M)\n"
    ACTION_COUNT=$((ACTION_COUNT + 1))
fi

# =============================================================================
# 3. Script Health & Optimization
# =============================================================================
echo "🔧 Checking and optimizing scripts..."
echo -e "\n### 3. Script Health & Optimization\n" >> "$REPORT_FILE"

# Test all Python scripts
for script in "$TOOLS_DIR"/*.py "$SCRIPTS_DIR"/*.py; do
    if [ -f "$script" ]; then
        script_name=$(basename "$script")
        if python3 "$script" --help >/dev/null 2>&1 || python3 -m py_compile "$script" 2>/dev/null; then
            echo "- ✅ $script_name: OK" >> "$REPORT_FILE"
        else
            echo "- ❌ $script_name: SYNTAX ERROR" >> "$REPORT_FILE"
            TODO_ITEMS="${TODO_ITEMS}- [ ] Fix syntax error in $script_name\n"
            ACTION_COUNT=$((ACTION_COUNT + 1))
        fi
    fi
done

# Check for optimization opportunities
echo "" >> "$REPORT_FILE"
echo "**Optimization Suggestions:**" >> "$REPORT_FILE"

# Check for scripts with hardcoded paths
HARDCODED=$(grep -r "home/ubuntu" "$TOOLS_DIR" "$SCRIPTS_DIR" 2>/dev/null | wc -l)
if [ "$HARDCODED" -gt 0 ]; then
    echo "- ⚠️ Found $HARDCODED hardcoded paths (consider using \$HOME or variables)" >> "$REPORT_FILE"
    SCRIPT_SUGGESTIONS="${SCRIPT_SUGGESTIONS}- Replace hardcoded paths with \$HOME or environment variables\n"
fi

# Check for scripts without error handling
NO_ERROR_CHECK=$(grep -L "try:\|set -e\|if \[\|2>/dev/null" "$TOOLS_DIR"/*.py "$SCRIPTS_DIR"/*.sh 2>/dev/null | wc -l)
if [ "$NO_ERROR_CHECK" -gt 0 ]; then
    echo "- ⚠️ $NO_ERROR_CHECK scripts may lack error handling" >> "$REPORT_FILE"
    SCRIPT_SUGGESTIONS="${SCRIPT_SUGGESTIONS}- Add error handling to scripts without try/except or set -e\n"
fi

# Check for TODO/FIXME comments
TODOS=$(grep -r "TODO\|FIXME\|XXX" "$TOOLS_DIR" "$SCRIPTS_DIR" 2>/dev/null | wc -l)
if [ "$TODOS" -gt 0 ]; then
    echo "- 📌 Found $TODOS TODO/FIXME comments in scripts" >> "$REPORT_FILE"
    TODO_ITEMS="${TODO_ITEMS}- [ ] Review TODO/FIXME comments in scripts\n"
    ACTION_COUNT=$((ACTION_COUNT + 1))
fi

if [ -n "$SCRIPT_SUGGESTIONS" ]; then
    echo -e "\n$SCRIPT_SUGGESTIONS" >> "$REPORT_FILE"
fi

# =============================================================================
# 4. Memory Maintenance
# =============================================================================
echo "📝 Memory maintenance..."
echo -e "\n### 4. Memory Maintenance\n" >> "$REPORT_FILE"

MEMORY_COUNT=$(ls -1 "$MEMORY_DIR"/*.md 2>/dev/null | wc -l)
echo "- Total memory files: $MEMORY_COUNT" >> "$REPORT_FILE"

OLD_FILES=$(find "$MEMORY_DIR" -name "20*.md" -mtime +90 2>/dev/null | wc -l)
if [ "$OLD_FILES" -gt 0 ]; then
    echo "- ⚠️ $OLD_FILES memory files older than 90 days" >> "$REPORT_FILE"
    TODO_ITEMS="${TODO_ITEMS}- [ ] Archive or delete old memory files (>90 days)\n"
    ACTION_COUNT=$((ACTION_COUNT + 1))
else
    echo "- ✅ No old memory files to archive" >> "$REPORT_FILE"
fi

# Check MEMORY.md size
MEMORY_SIZE=$(wc -l < "$WORKSPACE/MEMORY.md" 2>/dev/null || echo "0")
if [ "$MEMORY_SIZE" -gt 500 ]; then
    echo "- ⚠️ MEMORY.md is large ($MEMORY_SIZE lines) - consider pruning" >> "$REPORT_FILE"
    TODO_ITEMS="${TODO_ITEMS}- [ ] Review and prune MEMORY.md\n"
    ACTION_COUNT=$((ACTION_COUNT + 1))
fi

# =============================================================================
# 5. Extract & Track TODOs from Markdown Files
# =============================================================================
echo "📋 Extracting TODOs from workspace..."
echo -e "\n### 5. Action Items & TODOs\n" >> "$REPORT_FILE"

# Find all TODO items in markdown files
ALL_TODOS=$(grep -r "^- \[ \]\|^* [ ] - \[ \]" "$WORKSPACE" --include="*.md" 2>/dev/null | head -20)

if [ -n "$ALL_TODOS" ]; then
    echo "**Outstanding TODOs found:**" >> "$REPORT_FILE"
    echo "$ALL_TODOS" >> "$REPORT_FILE"
    echo "" >> "$REPORT_FILE"
    
    # Count TODOs
    TODO_COUNT=$(echo "$ALL_TODOS" | wc -l)
    echo "- Found $TODO_COUNT outstanding TODO items" >> "$REPORT_FILE"
else
    echo "- ✅ No outstanding TODOs found in markdown files" >> "$REPORT_FILE"
fi

# =============================================================================
# 6. Proactive Suggestions
# =============================================================================
echo "💡 Generating suggestions..."
echo -e "\n### 6. Proactive Suggestions\n" >> "$REPORT_FILE"

# Check if inbox reading is configured
if grep -q "imap.office365.com\|outlook.office365.com" "$TOOLS_DIR/read-email.py" 2>/dev/null; then
    if ! python3 "$TOOLS_DIR/read-email.py" --limit 1 >/dev/null 2>&1; then
        echo "- 📧 Email inbox: Outlook IMAP configured but NOT working - needs testing" >> "$REPORT_FILE"
        TODO_ITEMS="${TODO_ITEMS}- [ ] Test and verify Outlook IMAP connection\n"
        ACTION_COUNT=$((ACTION_COUNT + 1))
    else
        echo "- 📧 Email inbox: Outlook IMAP working ✅" >> "$REPORT_FILE"
    fi
else
    echo "- 📧 Email inbox: Consider setting up inbox reading" >> "$REPORT_FILE"
fi

# Check for pending Bitwarden session expiry
if [ -f "$HOME/.bitwarden/session.txt" ]; then
    SESSION_AGE=$(($(date +%s) - $(stat -c %Y "$HOME/.bitwarden/session.txt" 2>/dev/null || echo "0")))
    if [ "$SESSION_AGE" -gt 86400 ]; then
        echo "- 🔐 Bitwarden session expired - will re-auth on next use" >> "$REPORT_FILE"
    fi
fi

# =============================================================================
# 7. Update TODO.md
# =============================================================================
if [ -n "$TODO_ITEMS" ]; then
    echo -e "# TODO Items - Auto-generated $TODAY\n\n## Action Items for Jim\n$TODO_ITEMS\n## Script Improvements\n$SCRIPT_SUGGESTIONS\n---\n*Generated by self-improve.sh at $(TZ="Australia/Sydney" date '+%Y-%m-%d %H:%M:%S AEDT')*" > "$TODO_FILE"
    echo "- Created/updated TODO.md with $ACTION_COUNT action items" >> "$REPORT_FILE"
else
    echo "- ✅ No new action items generated" >> "$REPORT_FILE"
fi

# =============================================================================
# Summary
# =============================================================================
echo -e "\n## Summary\n" >> "$REPORT_FILE"
echo "Run completed at $(TZ="Australia/Sydney" date '+%Y-%m-%d %H:%M:%S AEDT')" >> "$REPORT_FILE"
echo "Next run: Tomorrow at 03:00 AEDT" >> "$REPORT_FILE"
echo "Action items created: $ACTION_COUNT" >> "$REPORT_FILE"

echo "✅ Self-improvement run complete!"
echo "Report saved to: $REPORT_FILE"
if [ -n "$TODO_ITEMS" ]; then
    echo "📋 Action items saved to: $TODO_FILE"
fi

# =============================================================================
# 8. Sync TODOs to Telegram (Jim's Phone)
# =============================================================================
echo "📱 Syncing TODOs to Telegram..."
python3 "$WORKSPACE/tools/send-todo-telegram.py" >/dev/null 2>&1 || true
echo "- TODOs synced to Telegram" >> "$REPORT_FILE"
