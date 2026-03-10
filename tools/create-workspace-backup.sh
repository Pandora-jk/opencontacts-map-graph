#!/bin/bash
# Create workspace backup archive
set -euo pipefail

WORKSPACE="/home/ubuntu/.openclaw/workspace"
BACKUP_DIR="/tmp/pandora-backup"
TIMESTAMP=$(date +%Y%m%dT%H%M%SZ)
ARCHIVE="${BACKUP_DIR}/workspace-${TIMESTAMP}.tar.gz"

mkdir -p "$BACKUP_DIR"

echo "Creating workspace backup: $ARCHIVE"

# Exclude certain paths from backup
tar -czf "$ARCHIVE" \
    --exclude="$WORKSPACE/memory/heartbeat-state.json" \
    --exclude="$WORKSPACE/memory/2026-03-10.md" \
    --exclude="$WORKSPACE/memory/2026-03-09.md" \
    --exclude="$WORKSPACE/memory/2026-03-08.md" \
    --exclude="$WORKSPACE/memory/2026-03-07.md" \
    --exclude="$WORKSPACE/memory/2026-03-06.md" \
    --exclude="$WORKSPACE/memory/2026-03-05.md" \
    --exclude="$WORKSPACE/memory/2026-03-04.md" \
    --exclude="$WORKSPACE/memory/2026-03-03.md" \
    --exclude="$WORKSPACE/memory/2026-03-02.md" \
    --exclude="$WORKSPACE/memory/2026-03-01.md" \
    --exclude="$WORKSPACE/memory/2026-02-28.md" \
    --exclude="$WORKSPACE/memory/2026-02-27.md" \
    --exclude="$WORKSPACE/memory/2026-02-26.md" \
    --exclude="$WORKSPACE/logs" \
    --exclude="$WORKSPACE/departments" \
    --exclude="$WORKSPACE/tools/__pycache__" \
    --exclude="$WORKSPACE/tools/.pyc" \
    --exclude="$WORKSPACE/scripts/__pycache__" \
    --exclude="$WORKSPACE/scripts/.pyc" \
    --exclude="$WORKSPACE/.git" \
    --exclude="$WORKSPACE/.openclaw" \
    --exclude="$WORKSPACE/*.pyc" \
    -C "$WORKSPACE" .

# Create symlink for compatibility with verify-backup-integrity.sh
ln -sf "$ARCHIVE" "/tmp/latest-workspace-backup.tar.gz"

echo "Backup created: $ARCHIVE"
ls -lh "$ARCHIVE"
