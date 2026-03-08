#!/bin/bash
# weekly-drift-report.sh - Weekly Agent Drift Report
# Runs at 17:00 UTC on Sundays
# Analyzes agent activity logs for drift detection and reporting

set -euo pipefail
umask 077

WORKSPACE="/home/ubuntu/.openclaw/workspace"
LOG_DIR="$WORKSPACE/logs"
REPORT_DIR="$WORKSPACE/reports"
DATE=$(date +"%Y-%m-%d")
TIMESTAMP=$(date +"%Y-%m-%d %H:%M:%S %Z")
WEEK_AGO=$(date -d "7 days ago" +"%Y-%m-%d" 2>/dev/null || date -v-7d +"%Y-%m-%d" 2>/dev/null || echo "unknown")
REPORT_FILE="${REPORT_DIR}/weekly-drift-${DATE}.md"
LOCK_FILE="${LOG_DIR}/.weekly-drift.lock"

# Create directories
mkdir -p "$REPORT_DIR"
mkdir -p "$LOG_DIR"

# Lock to prevent duplicate runs
if command -v flock >/dev/null 2>&1; then
    exec 9>"$LOCK_FILE"
    if ! flock -n 9; then
        echo "⚠️ Weekly drift report already running, skipping duplicate run."
        exit 0
    fi
fi

echo "📊 [${TIMESTAMP}] Starting weekly drift report..."

cd "$WORKSPACE"

# Initialize report
cat > "$REPORT_FILE" <<EOF
# Weekly Agent Drift Report

**Generated:** ${TIMESTAMP}
**Period:** ${WEEK_AGO} to ${DATE}
**Runner:** tools/weekly-drift-report.sh

---

## Executive Summary

EOF

# Analyze infra-activity.log
INFRA_LOG="$LOG_DIR/infra-activity.log"
if [ -f "$INFRA_LOG" ]; then
    INFRA_ENTRIES=$(wc -l < "$INFRA_LOG" 2>/dev/null || echo "0")
    INFRA_ALERTS=$(grep -c "ALERT:" "$INFRA_LOG" 2>/dev/null || echo "0")
    INFRA_WARNS=$(grep -c "WARN:" "$INFRA_LOG" 2>/dev/null || echo "0")
    INFRA_ERRORS=$(grep -c "ERROR:" "$INFRA_LOG" 2>/dev/null || echo "0")
    
    # Get unique risk patterns
    RISK_PATTERNS=$(grep -oP "RISK: [^;]+" "$INFRA_LOG" 2>/dev/null | sort -u | head -10 || echo "None detected")
    
    # Get persistent issues (repeated alerts)
    PERSISTENT_ISSUES=$(grep -oP "ALERT: [^;]+" "$INFRA_LOG" 2>/dev/null | sort | uniq -c | sort -rn | head -5 || echo "None")
    
    cat >> "$REPORT_FILE" <<EOF
## Infrastructure Department

**Activity Metrics:**
- Total log entries: ${INFRA_ENTRIES}
- Alerts triggered: ${INFRA_ALERTS}
- Warnings: ${INFRA_WARNS}
- Errors: ${INFRA_ERRORS}

**Top Risk Patterns:**
\`\`\`
${RISK_PATTERNS:-None detected}
\`\`\`

**Persistent Issues (by frequency):**
\`\`\`
${PERSISTENT_ISSUES:-None}
\`\`\`

EOF
else
    echo "⚠️ Infra activity log not found: ${INFRA_LOG}" >> "$REPORT_FILE"
    echo "" >> "$REPORT_FILE"
fi

# Analyze coding-activity.log
CODING_LOG="$LOG_DIR/coding-activity.log"
if [ -f "$CODING_LOG" ]; then
    CODING_ENTRIES=$(wc -l < "$CODING_LOG" 2>/dev/null || echo "0")
    CODING_BRANCHES=$(grep -oP "branch: [^ ]+" "$CODING_LOG" 2>/dev/null | sort -u | wc -l || echo "0")
    CODING_PRS=$(grep -c "PR\|pull.request" "$CODING_LOG" 2>/dev/null || echo "0")
    
    cat >> "$REPORT_FILE" <<EOF
## Coding Department

**Activity Metrics:**
- Total log entries: ${CODING_ENTRIES}
- Unique branches: ${CODING_BRANCHES}
- PR references: ${CODING_PRS}

EOF
else
    echo "## Coding Department" >> "$REPORT_FILE"
    echo "⚠️ Coding activity log not found: ${CODING_LOG}" >> "$REPORT_FILE"
    echo "" >> "$REPORT_FILE"
fi

# Analyze finance-activity.log
FINANCE_LOG="$LOG_DIR/finance-activity.log"
if [ -f "$FINANCE_LOG" ]; then
    FINANCE_ENTRIES=$(wc -l < "$FINANCE_LOG" 2>/dev/null || echo "0")
    
    cat >> "$REPORT_FILE" <<EOF
## Finance Department

**Activity Metrics:**
- Total log entries: ${FINANCE_ENTRIES}

EOF
else
    echo "## Finance Department" >> "$REPORT_FILE"
    echo "⚠️ Finance activity log not found: ${FINANCE_LOG}" >> "$REPORT_FILE"
    echo "" >> "$REPORT_FILE"
fi

# Check for config drift (SOUL.md, AGENTS.md changes)
echo "## Configuration Drift Detection" >> "$REPORT_FILE"
echo "" >> "$REPORT_FILE"

# Check git status for uncommitted changes
if command -v git >/dev/null 2>&1 && [ -d "$WORKSPACE/.git" ]; then
    cd "$WORKSPACE"
    GIT_STATUS=$(git status --short 2>/dev/null || echo "Git status unavailable")
    if [ -n "$GIT_STATUS" ] && [ "$GIT_STATUS" != "Git status unavailable" ]; then
        echo "⚠️ **Uncommitted changes detected:**" >> "$REPORT_FILE"
        echo '```' >> "$REPORT_FILE"
        echo "$GIT_STATUS" >> "$REPORT_FILE"
        echo '```' >> "$REPORT_FILE"
    else
        echo "✅ No uncommitted git changes" >> "$REPORT_FILE"
    fi
    echo "" >> "$REPORT_FILE"
else
    echo "⚠️ Git not available or not a git repository" >> "$REPORT_FILE"
    echo "" >> "$REPORT_FILE"
fi

# Check for key file modifications in the last 7 days
echo "## Recent File Modifications (Last 7 Days)" >> "$REPORT_FILE"
echo "" >> "$REPORT_FILE"

RECENT_FILES=$(find "$WORKSPACE/departments" -name "*.md" -mtime -7 -type f 2>/dev/null | head -20 || echo "None found")
if [ -n "$RECENT_FILES" ]; then
    echo '```' >> "$REPORT_FILE"
    echo "$RECENT_FILES" >> "$REPORT_FILE"
    echo '```' >> "$REPORT_FILE"
else
    echo "No recent markdown file modifications detected." >> "$REPORT_FILE"
fi
echo "" >> "$REPORT_FILE"

# Night session analysis
NIGHT_LOG="$LOG_DIR/night-infra.log"
if [ -f "$NIGHT_LOG" ]; then
    NIGHT_ENTRIES=$(wc -l < "$NIGHT_LOG" 2>/dev/null || echo "0")
    NIGHT_SIZE=$(du -h "$NIGHT_LOG" 2>/dev/null | cut -f1 || echo "unknown")
    
    cat >> "$REPORT_FILE" <<EOF
## Night Session Activity

**Night Infra Log:**
- Entries: ${NIGHT_ENTRIES}
- Log size: ${NIGHT_SIZE}

EOF
fi

# Recommendations section
cat >> "$REPORT_FILE" <<EOF
---

## Recommendations

EOF

# Generate recommendations based on findings
RECOMMENDATIONS=0

if [ "${INFRA_ALERTS:-0}" -gt 0 ]; then
    echo "- 🔴 **Address ${INFRA_ALERTS} infrastructure alerts** - Review persistent security warnings" >> "$REPORT_FILE"
    RECOMMENDATIONS=$((RECOMMENDATIONS + 1))
fi

if [ "${INFRA_WARNS:-0}" -gt 0 ]; then
    echo "- ⚠️ **Review ${INFRA_WARNS} infrastructure warnings** - Check firewall and port configurations" >> "$REPORT_FILE"
    RECOMMENDATIONS=$((RECOMMENDATIONS + 1))
fi

# Check for specific known issues
if grep -q "mDNS" "$INFRA_LOG" 2>/dev/null; then
    echo "- 🔒 **mDNS exposure** - Consider disabling MulticastDNS/LLMNR on public hosts" >> "$REPORT_FILE"
    RECOMMENDATIONS=$((RECOMMENDATIONS + 1))
fi

if grep -q "ufw unavailable" "$INFRA_LOG" 2>/dev/null; then
    echo "- 🛡️ **Host firewall** - No host firewall tool detected, consider enabling ufw/nftables" >> "$REPORT_FILE"
    RECOMMENDATIONS=$((RECOMMENDATIONS + 1))
fi

if [ $RECOMMENDATIONS -eq 0 ]; then
    echo "✅ No critical recommendations at this time." >> "$REPORT_FILE"
fi

echo "" >> "$REPORT_FILE"
echo "---" >> "$REPORT_FILE"
echo "" >> "$REPORT_FILE"
echo "_Report generated by weekly-drift-report.sh_" >> "$REPORT_FILE"

echo "✅ Weekly drift report completed at $(date '+%H:%M:%S %Z')"
echo "📄 Report: ${REPORT_FILE}"

# Output key findings for cron response
echo ""
echo "=== KEY FINDINGS ==="
echo "Period: ${WEEK_AGO} to ${DATE}"
echo "- Infra alerts: ${INFRA_ALERTS:-0}"
echo "- Infra warnings: ${INFRA_WARNS:-0}"
echo "- Infra errors: ${INFRA_ERRORS:-0}"
echo "- Coding entries: ${CODING_ENTRIES:-0}"
echo "- Finance entries: ${FINANCE_ENTRIES:-0}"
echo "- Recommendations: ${RECOMMENDATIONS}"
echo "==================="

exit 0
